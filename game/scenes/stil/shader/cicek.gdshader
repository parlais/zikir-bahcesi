shader_type spatial;
// Çiçek ve meyve: canlı renk, hafif ışıma, rüzgâr.
render_mode blend_mix, depth_draw_opaque, cull_disabled;
#include "res://scenes/stil/shader/ortak.gdshaderinc"

uniform float ruzgar = 0.06;
uniform float isima_guc = 0.0;

void vertex() {
	vec3 w = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	VERTEX.x += sin(TIME * 1.4 + w.x * 0.5 + w.z * 0.3) * ruzgar * COLOR.a;
}

void fragment() {
	vec3 c = zb_renk(COLOR.rgb);
	ALBEDO = c;
	ROUGHNESS = 0.6;
	if (!FRONT_FACING) {
		NORMAL = -NORMAL;
	}
	EMISSION = c * isima_guc;
}
