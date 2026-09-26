// Kesit (K10, K18): sekiz tabakanın dıştan görünümü için ortak pus ve kat ışığı.
// Global parametreler project.godot [shader_globals] içindedir; SahneKurucu yazar.
//   zb_kesit       0 içeride (etkisiz), 1 kesitte; yakınlaşmada konuma göre arada
//   zb_kesit_olcu  (kesme düzleminin z'si, kat yüksekliği, dilim kalınlığı, hava)
//   zb_pus_*       katın ufuk, gök ve nur rengi (profilden)
//   zb_pus_aralik  (pusun başladığı ve tamamlandığı derinlik, yanların ışığa karıştığı |x|)
// Her katın "göğü" dışarıdan bu pusla okunur: kesme düzleminden geriye derinlik arttıkça
// zemin önce katın ufuk rengine, yukarıda gök rengine karışır; üst katlarda nur ağır basar.
// Kamera dışarıdayken pus kesme düzleminden başlar, içeride motorun sisi devralır.

global uniform float zb_kesit;
global uniform vec4 zb_kesit_olcu;
global uniform vec3 zb_pus_ufuk : source_color;
global uniform vec3 zb_pus_gok : source_color;
global uniform vec3 zb_pus_nur : source_color;
global uniform vec4 zb_pus_aralik;
global uniform vec4 zb_kesit_kamera;   // kesit kamerasının (y, z), pencere_m: katın pencere derinliği için
global uniform float zb_agac_buyut;    // kesitte uzak ağaçların en çok büyütmesi (K20)
// Boş başlangıç (K20): ilk katta açılan ırmaklar (su, süt, bal, şerbet; 0 kapalı, 1 açık) ve
// kır çiçekleri (x miktar, y arsadan yarıçap, m). Vitrinde hepsi açıktır.
global uniform vec4 zb_irmak_dolu;
global uniform vec2 zb_ova_cicek;

float zb_irmak_acik(float zb_k) {
	vec4 zb_s = vec4(1.0) - min(abs(vec4(zb_k) - vec4(0.0, 1.0, 2.0, 3.0)), vec4(1.0));
	return dot(zb_irmak_dolu, zb_s);
}

// Uzak ağaç büyütmesi (K20): dışarıdan bakınca uzak ağaçlar hafifçe büyür (gerçek boyda
// dikey ekranda 2-4 piksel kalıyorlardı), yaklaştıkça gerçek boya döner. İçeride (zb_kesit
// = 0) ve 3 km'den yakında tam 1'dir. Ölçek örneğin kökenine (ağacın dibi) göre uygulanır.
float zb_agac_olcek(vec3 zb_koken, vec3 zb_kam) {
	float zb_u = smoothstep(3000.0, 20000.0, distance(zb_koken, zb_kam));
	return 1.0 + (zb_agac_buyut - 1.0) * zb_u * zb_kesit;
}

// Noktanın katı (0 ilk kat, 7 Firdevs) ve zeminden yüksekliğinin havaya oranı
vec2 zb_kat(vec3 zb_w) {
	float zb_k = clamp(floor((zb_w.y + zb_kesit_olcu.z) / zb_kesit_olcu.y), 0.0, 7.0);
	float zb_h = clamp((zb_w.y - zb_k * zb_kesit_olcu.y) / zb_kesit_olcu.w, 0.0, 1.0);
	return vec2(zb_k, zb_h);
}

// Katın penceresi: zeminin kesme düzleminden perdeye derinliği (models/kesit.py pencere())
float zb_pencere(float zb_k) {
	float zb_dy = max(zb_kesit_kamera.x - zb_k * zb_kesit_olcu.y, 1.0);
	float zb_dz = zb_kesit_kamera.y - zb_kesit_olcu.x;
	return min(zb_kesit_kamera.z * sqrt(zb_dy * zb_dy + zb_dz * zb_dz) / zb_dy, 9000.0);
}

// Katın ışığı: yukarı çıktıkça artar (1. kat 0, Firdevs 1)
float zb_kat_isik(float zb_k) {
	return pow(zb_k / 7.0, 1.4);
}

// Pus rengi: alçakta katın ufuk rengi (uzak zemin ufka karışır), yukarı doğru gök rengi
// (katın arka perdesi: her bandın üstü gök gibi okunur); katın ışığıyla nura doğru
vec3 zb_pus_renk(vec3 zb_w) {
	vec2 zb_kh = zb_kat(zb_w);
	float zb_dn = (zb_kesit_olcu.x - zb_w.z) / zb_pencere(zb_kh.x);
	float zb_t = max(smoothstep(0.02, 0.5, zb_kh.y), 0.25 * smoothstep(0.3, 1.0, zb_dn));
	vec3 zb_c = mix(zb_pus_ufuk, zb_pus_gok, zb_t);
	// Firdevs (8. kat): mavi gök yok, havası tamamen nurdur
	return mix(zb_c, zb_pus_nur, 0.65 * zb_kat_isik(zb_kh.x) + 0.35 * step(6.5, zb_kh.x));
}

// Pus miktarı: kesme düzleminden derinlikle; yanlarda ışığa karışır
// Pus miktarı: katın penceresi boyunca derinlikle (perdenin önünde ~%60: net ama yumuşak ufuk);
// Firdevs'in ardı nura erir; yanlarda ışığa karışır
float zb_pus_miktar(vec3 zb_w) {
	float zb_derin = zb_kesit_olcu.x - zb_w.z;
	float zb_k = zb_kat(zb_w).x;
	float zb_dn = zb_derin / zb_pencere(zb_k);
	float zb_m = 0.62 * smoothstep(zb_pus_aralik.x, zb_pus_aralik.y, zb_dn);
	float zb_i = zb_kat_isik(zb_k);
	zb_m = max(zb_m, step(6.5, zb_k) * smoothstep(0.08, 0.7, zb_dn));
	zb_m = zb_m + (1.0 - zb_m) * 0.08 * zb_i * step(0.0, zb_derin);
	zb_m = max(zb_m, smoothstep(zb_pus_aralik.z, zb_pus_aralik.w, abs(zb_w.x)));
	return clamp(zb_m, 0.0, 1.0) * zb_kesit;
}

// Işık alan malzemeler: fragment sonunda ALBEDO ve EMISSION'a uygulanır
#define ZB_KESIT_PUS(w) { float zb_p = zb_pus_miktar(w); ALBEDO *= 1.0 - zb_p; EMISSION = EMISSION * (1.0 - zb_p) + zb_pus_renk(w) * zb_p; }
