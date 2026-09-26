shader_type spatial;
// Çiçek ve meyve: canlı renk, hafif ışıma, rüzgâr.
render_mode blend_mix, depth_draw_opaque, cull_disabled;
#include "res://scenes/stil/shader/ortak.gdshaderinc"
#include "res://scenes/stil/shader/kesit.gdshaderinc"

uniform float ruzgar = 0.06;
uniform float ruzgar_hiz = 1.3;
uniform float isima_guc = 0.0;

// Rüzgâr yaprak ve kabuk shader'larıyla aynı: dallardaki meyveler dallarıyla birlikte salınır.
varying vec3 zb_dunya;

void vertex() {
	zb_dunya = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec3 w = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float t = TIME * ruzgar_hiz;
	float s = sin(t + w.x * 0.35 + w.z * 0.22) + 0.4 * sin(t * 2.3 + w.x * 1.7 + w.y);
	VERTEX.x += s * ruzgar * COLOR.a;
	VERTEX.z += cos(t * 0.8 + w.z * 0.3) * ruzgar * 0.6 * COLOR.a;
}

void fragment() {
	vec3 c = zb_renk(COLOR.rgb);
	ALBEDO = c;
	ROUGHNESS = 0.6;
	if (!FRONT_FACING) {
		NORMAL = -NORMAL;
	}
	EMISSION = c * isima_guc;
	// Kesit (K18): dıştan bakınca katın pusu; içeride etkisiz (zb_kesit = 0)
	ZB_KESIT_PUS(zb_dunya);
}
