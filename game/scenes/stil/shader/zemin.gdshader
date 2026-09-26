shader_type spatial;
// Çimenlik zemin ve dış arazi: büyük ölçekli lekeler, sarımsı çayır izleri.
render_mode blend_mix, depth_draw_opaque, cull_back;
#include "res://scenes/stil/shader/ortak.gdshaderinc"
#include "res://scenes/stil/shader/kesit.gdshaderinc"
#include "res://scenes/stil/shader/cayir.gdshaderinc"

uniform vec3 cimen_acik : source_color = vec3(0.55, 0.72, 0.32);
uniform vec3 cimen_koyu : source_color = vec3(0.22, 0.42, 0.2);
uniform vec3 kuru : source_color = vec3(0.72, 0.68, 0.38);
uniform float kuru_miktar = 0.25;
uniform float cicek_yogun = 0.35;      // kır çiçeği benekleri
uniform vec3 cicek_a : source_color = vec3(1.0, 0.95, 0.85);
uniform vec3 cicek_b : source_color = vec3(1.0, 0.72, 0.8);
uniform vec3 cicek_c : source_color = vec3(1.0, 0.85, 0.35);
uniform vec3 filiz_renk : source_color = vec3(0.45, 0.72, 0.25);
uniform float filiz_miktar = 0.0;
// Kesitteki öteki katlar (K18): çimen, köşe rengindeki katın tonuyla çarpılır (0,5 nötr).
// İçerideki arazide 0'dır; görünüş değişmez.
uniform float kose_ton = 0.0;
// Boş başlangıç (K20): ilk katın arazisinde UV ırmak yatağı verisidir (x oyma m, y ırmak +
// bölge * 0,99; cennet.py irmak_oyma). Irmak kapalıyken yatak ova hizasına kalkar ve bölge
// çimen olur (kuru hendek kalmaz). Yalnız bu arazinin örneğinde 1'dir.
instance uniform float irmak_yatagi = 0.0;
// Çayırın kadife görünüşü (K20; boş ovada zemin tek başına görünür):
//   leke_kontrast  büyük çimen lekelerinin karşıtlığı (1: eski, iri koyu lekeler)
//   normal_yumusak çimenli yerde ışığın tümseklere duyarlılığı azalır (0: eski)
//   ruzgar_dalga   ovada yavaşça kayan açık rüzgâr bantları
//   kadife         yatık bakışta yumuşak parıltı
uniform float leke_kontrast = 1.0;
uniform float normal_yumusak = 0.0;
uniform float ruzgar_dalga = 0.0;
uniform float kadife = 0.0;

varying vec3 dunya;
varying float zb_yatak;

void vertex() {
	float zb_k = floor(UV.y + 0.001);
	float zb_bolge = clamp((UV.y - zb_k) / 0.99, 0.0, 1.0);
	float zb_kapali = irmak_yatagi * (1.0 - zb_irmak_acik(zb_k));
	VERTEX.y += UV.x * zb_kapali;
	zb_yatak = zb_bolge * zb_kapali;
	NORMAL = normalize(mix(NORMAL, vec3(0.0, 1.0, 0.0), zb_yatak));
	dunya = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	// Çimen ağırlığı: kapalı ırmağın yatağı ve kıyısı çimendir
	float zb_w = mix(COLOR.a, 1.0, zb_yatak);
	float buyuk = zb_fbm(dunya * 0.045);
	float kucuk = zb_fbm(dunya * 0.6);
	float leke = buyuk * 0.8 + kucuk * 0.35;
	leke = 0.575 + (leke - 0.575) * leke_kontrast;
	vec3 c = mix(cimen_koyu, cimen_acik, smoothstep(0.25, 0.75, leke));
	c = mix(c, kuru, smoothstep(0.62, 0.8, zb_fbm(dunya * 0.02 + 7.0)) * kuru_miktar);
	c *= mix(vec3(1.0), COLOR.rgb * 2.0, kose_ton * step(0.99, zb_w));
	// Kır çiçekleri: hücre başına bir benek, çayır lekelerinde yoğunlaşır
	vec2 hc = floor(dunya.xz * 3.0);
	vec2 hf = fract(dunya.xz * 3.0) - 0.5;
	float r = zb_hash(vec3(hc, 3.1));
	vec2 o = vec2(zb_hash(vec3(hc, 7.3)), zb_hash(vec3(hc, 1.7))) - 0.5;
	float benek = 1.0 - smoothstep(0.06, 0.11, length(hf - o * 0.6));
	float bolge = smoothstep(0.35, 0.7, zb_fbm(dunya * 0.08 + 13.0));
	// Boş başlangıç (K20): ilk katta kır çiçekleri açıldıkça arsadan dışa yayılır
	float zb_ova = zb_ova_cicek.x * (1.0 - smoothstep(zb_ova_cicek.y, zb_ova_cicek.y + 25.0, length(dunya.xz)));
	float var_mi = step(1.0 - cicek_yogun * bolge * mix(zb_ova, 1.0, kose_ton), r);
	vec3 cr = r > 0.97 ? cicek_c : (r > 0.93 ? cicek_b : cicek_a);
	c = mix(c, cr, benek * var_mi * step(0.99, zb_w));
	// Çimen olmayan yerler (köşe ağırlığı COLOR.a < 1): köşe rengi (toprak, kum, çakıl, taş).
	// Eski arazilerde ağırlık her yerde 1'dir; görünüm değişmez.
	float topak = zb_fbm(dunya * 2.3);
	float tane = zb_gurultu(dunya * 11.0);
	vec3 kose = COLOR.rgb * (0.78 + 0.4 * topak) * (0.9 + 0.2 * kucuk) * (0.9 + 0.2 * tane);
	// Toprakta yer yer minik filiz benekleri (verimli ama boş arsa)
	vec2 fc = floor(dunya.xz * 4.0);
	float fr = zb_hash(vec3(fc, 9.1));
	float filiz = (1.0 - smoothstep(0.05, 0.12, length(fract(dunya.xz * 4.0) - 0.5))) * step(0.965, fr);
	kose = mix(kose, filiz_renk, filiz * (1.0 - zb_w) * filiz_miktar);
	float kenar_gurultu = (zb_fbm(dunya * 0.9 + 3.0) - 0.5) * 0.5;
	float cim = smoothstep(0.4, 0.6, zb_w + kenar_gurultu * (1.0 - step(0.999, zb_w)));
	c = mix(kose, c, cim);
	// Rüzgâr dalgası: rüzgâr yönünde yavaşça kayan, kenarları yumuşak açık bantlar (çimen
	// yatınca daha çok ışık yansır); uzakta desen söner, ortalama kalır
	float zb_uzak = smoothstep(0.6, 3.0, length(fwidth(dunya.xz)));
	float zb_bant = mix(zb_ruzgar_bandi(dunya, TIME), 0.18, zb_uzak) * cim;
	c = mix(c, c * 1.16 + vec3(0.025, 0.03, 0.0), zb_bant * ruzgar_dalga);
	// Sabâ halkası: her zikirde çekirdekten yayılan açık, sıcak bir halka (arsanın çimeninde de)
	float zb_h = zb_halka(dunya.xz) * mix(0.45, 1.0, cim);   // arsanın küçük çimeninde yarı güçte
	c = mix(c, c * 1.35 + vec3(0.08, 0.07, 0.03), zb_h);
	ALBEDO = zb_renk(c);
	// Kadife: yatık bakışta çimen uçlarının yumuşak parıltısı
	float zb_yatik = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), 3.0);
	EMISSION += ALBEDO * zb_yatik * kadife * cim;
	// Halka nurdan bir dalga gibi hafifçe ışır
	EMISSION += vec3(1.0, 0.92, 0.7) * zb_h * 0.18;
	// Tümseklerin ışığı yumuşar (çimenli yerde)
	NORMAL = normalize(mix(NORMAL, (VIEW_MATRIX * vec4(0.0, 1.0, 0.0, 0.0)).xyz, normal_yumusak * cim));
	ROUGHNESS = 0.95;
	// Kesit (K18): dıştan bakınca katın pusu; içeride etkisiz (zb_kesit = 0)
	ZB_KESIT_PUS(dunya);
}
