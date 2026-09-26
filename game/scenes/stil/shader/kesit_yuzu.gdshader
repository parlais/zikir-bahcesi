shader_type spatial;
// Kesit yüzü (K10, K18): Dünya'nın katman resimleri gibi, cennet toprağının kesiti.
// "Toprağı za'ferân, çakılları inci ve yakut, harcı misk" (et-Tâc 5/402, Tirmizî 2526;
// danışma kurulu teyit edecek). Doku (mf/doku.py kesit_toprak): çimen kökleri, za'ferân
// toprak, misk damarı, inci ve yakut çakıllar, altın damarlar.
// Yüz bir çizim gibi kendi ışığıyla aydınlanır (güneş arkadan vurur; aksi hâlde karanlık kalırdı).
// UV.x = x / 300 m, UV.y = yüzeyden derinlik oranı. COLOR.r = kat / 8.
render_mode unshaded, cull_back, depth_draw_opaque;
#include "res://scenes/stil/shader/ortak.gdshaderinc"
#include "res://scenes/stil/shader/kesit.gdshaderinc"

uniform sampler2D doku : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D doku_n : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform vec3 yuz_ton : source_color = vec3(1.0);
uniform float yuz_isik = 1.0;
uniform vec3 damar_renk : source_color = vec3(1.0, 0.92, 0.7);

varying vec3 dunya;

void vertex() {
	// Boş başlangıç (K20): ilk katta kapalı ırmağın çentiği düzleşir (COLOR.g = oyma / 16 *
	// (1 - derinlik oranı), COLOR.b = (ırmak + 1) / 8; 0 ırmak yok)
	float zb_irmak = floor(COLOR.b * 8.0 + 0.5) - 1.0;
	if (zb_irmak >= 0.0) {
		VERTEX.y += COLOR.g * 16.0 * (1.0 - zb_irmak_acik(zb_irmak));
	}
	dunya = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	float k = floor(COLOR.r * 8.0 + 0.5);
	// Döşeme tekrarı seçilmesin: katlar arasında kayar, geniş dalgalarla bükülür
	vec2 uv = UV;
	uv.x += k * 0.37 + 0.13 * sin(dunya.x / 900.0 + k * 2.1);
	uv.y = clamp(uv.y + 0.018 * sin(dunya.x / 640.0 + k * 1.7), 0.002, 0.998);
	vec3 c = texture(doku, uv).rgb * yuz_ton;
	// Kabartma: çakıllar, kökler ve damarlar sol üstten gelen yumuşak bir ışıkla (yüz kendi
	// ışığıyla aydınlanır; güneş arkada kalır)
	vec3 n = texture(doku_n, uv).xyz * 2.0 - 1.0;
	c *= 0.84 + 0.3 * clamp(dot(normalize(n), normalize(vec3(-0.35, 0.55, 0.75))), 0.0, 1.0);
	// Üst kenarın hemen altı (çimenin saçağı) hafif gölgeli
	c *= mix(0.8, 1.0, smoothstep(0.0, 0.05, UV.y));
	// Yukarı çıktıkça toprak açılır; ince nur damarları belirir
	float isik = zb_kat_isik(k);
	c = mix(c, c * 1.12 + vec3(0.06, 0.05, 0.03), isik * 0.6);
	float damar = smoothstep(0.93, 1.0, sin(uv.x * 6.283 * 3.0 + uv.y * 40.0 + sin(uv.x * 11.0) * 2.0)) * isik;
	c = mix(c, damar_renk * 1.3, damar * 0.5);
	vec3 son = zb_renk(c) * yuz_isik;
	float p = zb_pus_miktar(dunya);
	ALBEDO = mix(son, zb_pus_renk(dunya), p);
}
