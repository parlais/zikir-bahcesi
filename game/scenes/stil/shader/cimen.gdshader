shader_type spatial;
// Çimen tutamları: dipten uca renk geçişi, dalga dalga rüzgâr.
render_mode blend_mix, depth_draw_opaque, cull_disabled;
#include "res://scenes/stil/shader/ortak.gdshaderinc"
#include "res://scenes/stil/shader/kesit.gdshaderinc"

uniform vec3 dip : source_color = vec3(0.16, 0.34, 0.14);
uniform vec3 uc : source_color = vec3(0.62, 0.8, 0.36);
uniform float ruzgar = 0.12;
uniform float ruzgar_hiz = 1.6;

varying float boy;
varying float cesit;

varying vec3 zb_dunya;

void vertex() {
	zb_dunya = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec3 w = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float dalga = sin(TIME * ruzgar_hiz + w.x * 0.25 + w.z * 0.18) * 0.7 + sin(TIME * 3.1 + w.x * 1.3) * 0.3;
	VERTEX.x += dalga * ruzgar * COLOR.a * COLOR.a;
	VERTEX.z += dalga * ruzgar * 0.5 * COLOR.a * COLOR.a;
	NORMAL = normalize(mix(NORMAL, vec3(0.0, 1.0, 0.0), 0.75));
	boy = COLOR.a;
	cesit = INSTANCE_CUSTOM.r;
}

void fragment() {
	vec3 c = mix(dip, uc, boy) * (0.85 + 0.3 * cesit);
	ALBEDO = zb_renk(c);
	ROUGHNESS = 0.9;
	SPECULAR = 0.1;
	// Kesit (K18): dıştan bakınca katın pusu; içeride etkisiz (zb_kesit = 0)
	ZB_KESIT_PUS(zb_dunya);
}
