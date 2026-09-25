shader_type spatial;
// Gökten, bulutun içinden inen çağlayan (at kuyruğu biçimi; cennet.py _gok_selalesi).
// Köşe verisi: COLOR.r perdenin eni boyunca konum (0-1), COLOR.g tepe genişliği / 200 m,
// COLOR.b çağlayana özgü rastgele sayı, COLOR.a tepeden dibe 1 -> 0.
//
// Perde: uzaktan da seçilen iri akış çizgileri, yaklaştıkça orta ve ince çizgiler; her
// biri kendi hızıyla aşağı iner. Gövde koyu turkuaz (ışık arkadan gelir; parlak gökte
// suyun biçimi böyle okunur), ince beyaz köpük çizgileri ve aşağı düşen beyaz öbekler.
// İnce kenarlar ve köpük ışıyarak parlar. Kenarlar aşağı doğru saçılır; tepe buluttan
// çıkar, dip serpintiye dağılır.
// pus = 1: perdenin arkasındaki geniş, yumuşak, parlayan serpinti zarfı.
render_mode blend_mix, depth_draw_opaque, cull_disabled;
#include "res://scenes/stil/shader/ortak.gdshaderinc"

uniform vec3 su_renk : source_color = vec3(0.62, 0.86, 0.9);
uniform vec3 derin_renk : source_color = vec3(0.25, 0.55, 0.62);
uniform vec3 kopuk : source_color = vec3(1.0);
uniform float hiz = 1.0;              // akış hızı çarpanı
uniform float cizgi_olcek = 1.0;      // akış çizgilerinin genişlik çarpanı
uniform float isima_guc = 0.25;
uniform float saydamlik = 1.0;
uniform float pus = 0.0;

varying vec3 dunya;
varying float enine;     // 0 sol kenar, 1 sağ kenar
varying float dus;       // 0 tepe, 1 dip
varying float genislik;  // tepe genişliği (m)
varying float tohum;

void vertex() {
	dunya = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	enine = COLOR.r;
	genislik = max(COLOR.g * 200.0, 1.0);
	tohum = COLOR.b * 97.0;
	dus = 1.0 - COLOR.a;
}

// Ekranda seçilemeyecek kadar ince desen titremesin: seçilirken 1, pikselden
// incelince 0 (koordinat desenin bir periyodu = 1 birim).
float secilir(float koordinat) {
	return 1.0 - smoothstep(0.3, 0.75, fwidth(koordinat));
}

void fragment() {
	float t = TIME * hiz;
	// Enine metre, tepe ölçüsünde: perde aşağıda açıldıkça çizgiler de yelpaze gibi açılır.
	float x = (enine - 0.5) * genislik;
	float y = dunya.y;
	float yan = abs(enine * 2.0 - 1.0);  // 0 perdenin ortası, 1 kenarı
	vec3 c;
	float a;
	if (pus > 0.5) {
		// Serpinti zarfı: iri, yumuşak, yavaş inen pus; aşağıda yoğun
		float n = zb_fbm(vec3(x / 26.0, (y + t * 7.0) / 60.0, tohum + 5.0));
		float yay = 1.0 - smoothstep(0.2, 1.0, yan + (n - 0.5) * 0.6);
		a = smoothstep(0.08, 0.6, dus) * yay * (0.25 + 0.75 * n) * 0.3 * saydamlik;
		c = mix(su_renk, kopuk, 0.85);
		ROUGHNESS = 1.0;
		SPECULAR = 0.0;
		EMISSION = c * isima_guc * 0.9;
	} else {
		float o = cizgi_olcek;
		float g1 = 7.0 * o;
		float g2 = 2.8 * o;
		float g3 = 1.1 * o;
		// Düşeyde uzun desenler: su, kesintisiz paralel çizgilerle okunur
		float n1 = zb_gurultu(vec3(x / g1, (y + t * 16.0) / (g1 * 18.0), tohum));
		float n2 = zb_gurultu(vec3((x + 3.1) / g2, (y + t * 24.0) / (g2 * 24.0), tohum + 11.0));
		float n3 = zb_gurultu(vec3((x + 7.7) / g3, (y + t * 34.0) / (g3 * 30.0), tohum + 23.0));
		float s1 = secilir(x / g1);
		float s2 = secilir(x / g2);
		float s3 = secilir(x / g3);
		float akis = 0.5 + (n1 - 0.5) * 1.3 * s1 + (n2 - 0.5) * 0.8 * s2 + (n3 - 0.5) * 0.5 * s3;
		// Aşağı düşen beyaz öbekler (arkalarında uzun iz bırakır)
		float kume = smoothstep(0.6, 0.8, zb_gurultu(vec3(x / 8.0, (y + t * 20.0) / 55.0, tohum + 31.0)));
		// Havalanma: tepede cam gibi su, aşağı indikçe köpük artar. Köpük çizgileri keskin kenarlı.
		float hava = smoothstep(0.0, 0.85, dus);
		float esik_k = 0.64 - hava * 0.2;
		float kop = smoothstep(esik_k, esik_k + 0.07, akis) + kume * 0.35 * (0.2 + 0.8 * hava);
		// Uzakta çizgiler seçilmez: köpüğün ortalamasına geç (yoksa gövde rengi kalır,
		// pusla griye döner ve perde duman sütunu gibi okunur)
		kop = mix(mix(0.3, 0.55, hava), kop, s1 * 0.5 + s2 * 0.5);
		kop = clamp(kop + smoothstep(0.84, 1.0, dus) * 0.5, 0.0, 1.0);
		// İnce su taneciği: köpüğe doku
		float tane = zb_gurultu(vec3(x / 0.7, (y + t * 40.0) / 5.0, tohum + 60.0));
		kop *= mix(1.0, 0.75 + 0.5 * tane, s3);
		// Gövde ırmaklarla aynı doygun turkuaz; çizgi aralarında derinleşir
		vec3 govde = mix(derin_renk, su_renk, clamp(akis * 1.4 - 0.25, 0.0, 1.0));
		c = mix(govde, kopuk, kop);
		// Kenarlar aşağı doğru saçılır: akış yönünde uzamış, yumuşak saçaklar
		float dag = zb_gurultu(vec3(x / 4.0, (y + t * 18.0) / 50.0, tohum + 47.0));
		float esik = mix(0.8, 0.55, dus);
		float yay = 1.0 - smoothstep(esik, 1.0, yan + (dag - 0.5) * mix(0.1, 0.35, dus));
		// Tepe buluttan çıkar; dip serpintiye dağılır
		float tepe = smoothstep(0.0, 0.1, dus);
		float dagilma = 1.0 - smoothstep(0.8, 1.0, dus) * (0.3 + 0.4 * (1.0 - n1));
		// İnce kenarlar ışığı geçirir: daha saydam ve ışıyan
		float ince = smoothstep(0.35, 0.95, yan);
		a = saydamlik * mix(0.95, 0.6, ince) * yay * tepe * dagilma;
		ROUGHNESS = 0.3;
		SPECULAR = 0.5;
		EMISSION = (kopuk * kop * 0.8 + govde * 0.4 + mix(su_renk, kopuk, 0.5) * ince * 0.5) * isima_guc;
	}
	ALBEDO = zb_renk(c);
	ALPHA = clamp(a, 0.0, 1.0);
	if (!FRONT_FACING) {
		NORMAL = -NORMAL;
	}
}
