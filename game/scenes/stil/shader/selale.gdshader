shader_type spatial;
// Gökten, bulutun içinden inen çağlayan (at kuyruğu biçimi; cennet.py _gok_selalesi).
// Köşe verisi: COLOR.r perdenin eni boyunca konum (0-1), COLOR.g tepe genişliği / 200 m,
// COLOR.b çağlayana özgü rastgele sayı, COLOR.a tepeden dibe 1 -> 0.
//
// Perde: uzaktan da seçilen iri akış çizgileri, yaklaştıkça orta ve ince çizgiler; her
// biri kendi hızıyla aşağı iner. Tepede cam gibi su, aşağı indikçe köpük ve aşağı düşen
// beyaz öbekler. Kenarlar aşağı doğru saçılır; tepe buluttan çıkar, dip serpintiye dağılır.
// pus = 1: perdenin arkasındaki geniş, yumuşak serpinti zarfı.
// Arkadan gelen ışık ince sudan geçer (ortak light(): gecirgenlik, gecirgen_renk).
render_mode blend_mix, depth_draw_opaque, cull_disabled;
#include "res://scenes/stil/shader/ortak.gdshaderinc"

uniform vec3 su_renk : source_color = vec3(0.62, 0.86, 0.9);
uniform vec3 derin_renk : source_color = vec3(0.25, 0.55, 0.62);
uniform vec3 kopuk : source_color = vec3(1.0);
uniform float hiz = 1.0;              // akış hızı çarpanı
uniform float cizgi_olcek = 1.0;      // akış çizgilerinin genişlik çarpanı
uniform float isima_guc = 0.25;
uniform float saydamlik = 0.85;
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
		a = smoothstep(0.08, 0.6, dus) * yay * (0.3 + 0.7 * n) * 0.5;
		c = mix(su_renk, kopuk, 0.8);
		ROUGHNESS = 1.0;
		SPECULAR = 0.0;
		EMISSION = c * isima_guc * 0.5;
	} else {
		float o = cizgi_olcek;
		float g1 = 11.0 * o;
		float g2 = 4.0 * o;
		float g3 = 1.5 * o;
		float n1 = zb_gurultu(vec3(x / g1, (y + t * 16.0) / (g1 * 7.0), tohum));
		float n2 = zb_gurultu(vec3((x + 3.1) / g2, (y + t * 24.0) / (g2 * 9.0), tohum + 11.0));
		float n3 = zb_gurultu(vec3((x + 7.7) / g3, (y + t * 34.0) / (g3 * 12.0), tohum + 23.0));
		float akis = 0.5 + (n1 - 0.5) * 1.2 * secilir(x / g1) + (n2 - 0.5) * 0.7 * secilir(x / g2)
				+ (n3 - 0.5) * 0.4 * secilir(x / g3);
		// Aşağı düşen beyaz öbekler
		float kume = smoothstep(0.55, 0.85, zb_gurultu(vec3(x / 16.0, (y + t * 20.0) / 40.0, tohum + 31.0)));
		// Havalanma: tepede cam gibi su, aşağıda köpük; dipte her yer beyaz
		float hava = smoothstep(0.0, 0.8, dus);
		float kop = smoothstep(0.66 - hava * 0.36, 0.86 - hava * 0.2, akis) + kume * 0.55 * (0.3 + 0.7 * hava);
		kop = clamp(kop + smoothstep(0.8, 1.0, dus) * 0.6, 0.0, 1.0);
		vec3 govde = mix(derin_renk, su_renk, clamp(akis * 1.3 - 0.15, 0.0, 1.0));
		c = mix(govde, kopuk, kop);
		// Kenarlar aşağı doğru saçılır, dağınıklaşır
		float dag = zb_gurultu(vec3(x / 7.0, (y + t * 18.0) / 26.0, tohum + 47.0));
		float esik = mix(0.84, 0.4, dus);
		float yay = 1.0 - smoothstep(esik, 1.0, yan + (dag - 0.5) * mix(0.12, 0.7, dus));
		// Tepe buluttan çıkar; dip serpintiye dağılır
		float tepe = smoothstep(0.0, 0.1, dus);
		float dagilma = 1.0 - smoothstep(0.78, 1.0, dus) * (0.4 + 0.6 * (1.0 - n1));
		a = saydamlik * mix(0.6, 1.0, kop) * yay * tepe * dagilma;
		ROUGHNESS = 0.3;
		SPECULAR = 0.5;
		EMISSION = c * isima_guc * (0.6 + 0.8 * kop);
	}
	ALBEDO = zb_renk(c);
	ALPHA = clamp(a, 0.0, 1.0);
	if (!FRONT_FACING) {
		NORMAL = -NORMAL;
	}
}
