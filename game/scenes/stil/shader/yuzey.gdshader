shader_type spatial;
// Genel yüzey: taş, mermer, ahşap, kurşun, altın. Renk köşe renginden gelir.
render_mode blend_mix, depth_draw_opaque, cull_back;
#include "res://scenes/stil/shader/ortak.gdshaderinc"
#include "res://scenes/stil/shader/kesit.gdshaderinc"

uniform float puruz : hint_range(0.0, 1.0) = 0.8;
uniform float metal : hint_range(0.0, 1.0) = 0.0;
uniform float detay = 0.08;          // taş dokusu gibi hafif leke
uniform float detay_olcek = 1.6;
uniform vec3 isima : source_color = vec3(0.0);
uniform float isima_guc = 0.0;

uniform float agac_buyut = 0.0;   // 1: ağaç malzemesi, kesitte uzakta büyür
varying vec3 dunya;

void vertex() {
	// Kesitte uzak ağaç büyütmesi (K20); içeride etkisiz
	VERTEX *= mix(1.0, zb_agac_olcek(MODEL_MATRIX[3].xyz, CAMERA_POSITION_WORLD), agac_buyut);
	dunya = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	float n = zb_fbm(dunya * detay_olcek);
	vec3 c = zb_renk(COLOR.rgb) * (1.0 + (n - 0.5) * 2.0 * detay);
	ALBEDO = c;
	ROUGHNESS = puruz;
	METALLIC = metal;
	EMISSION = isima * isima_guc + kenar * pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), 3.0) * kenar_renk * 0.4;
	// Kesit (K18): dıştan bakınca katın pusu; içeride etkisiz (zb_kesit = 0)
	ZB_KESIT_PUS(dunya);
}
