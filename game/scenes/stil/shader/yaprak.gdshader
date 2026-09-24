shader_type spatial;
// Yapraklar: rüzgârla salınım (köşe ağırlığı COLOR.a), örnek başına renk
// farkı (INSTANCE_CUSTOM.r), arkadan gelen ışığın yapraktan geçişi.
render_mode blend_mix, depth_draw_opaque, cull_disabled;
#include "res://scenes/stil/shader/ortak.gdshaderinc"

uniform float ruzgar = 0.08;
uniform float ruzgar_hiz = 1.3;
uniform vec3 ton_a : source_color = vec3(1.0);
uniform vec3 ton_b : source_color = vec3(1.0);

varying float cesit;
varying vec3 dunya;

void vertex() {
	vec3 w = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float t = TIME * ruzgar_hiz;
	float s = sin(t + w.x * 0.35 + w.z * 0.22) + 0.4 * sin(t * 2.3 + w.x * 1.7 + w.y);
	VERTEX.x += s * ruzgar * COLOR.a;
	VERTEX.z += cos(t * 0.8 + w.z * 0.3) * ruzgar * 0.6 * COLOR.a;
	cesit = INSTANCE_CUSTOM.r;
	dunya = w;
}

void fragment() {
	vec3 c = COLOR.rgb * mix(ton_a, ton_b, cesit);
	c *= 0.9 + 0.2 * zb_gurultu(dunya * 3.0);
	ALBEDO = zb_renk(c);
	ROUGHNESS = 0.92;
	SPECULAR = 0.12;
	if (!FRONT_FACING) {
		NORMAL = -NORMAL;
	}
	EMISSION = kenar * pow(1.0 - clamp(abs(dot(NORMAL, VIEW)), 0.0, 1.0), 4.0) * kenar_renk * ALBEDO * 0.6;
}
