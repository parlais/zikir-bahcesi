shader_type spatial;
// Ağaç kabuğu (K15): döşenen kabuk dokusu ve normal haritası. Tür rengi ve taç
// içindeki gölge köşe renginden gelir. Rüzgâr salınımı yaprak kartlarıyla aynıdır
// (ağırlık COLOR.a): dal ve üstündeki kartlar birlikte salınır.
render_mode blend_mix, depth_draw_opaque, cull_back;
#include "res://scenes/stil/shader/ortak.gdshaderinc"

uniform sampler2D doku : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D doku_n : hint_normal, filter_linear_mipmap_anisotropic, repeat_enable;
uniform float normal_guc = 1.0;
uniform float puruz = 0.9;
uniform float ruzgar = 0.08;
uniform float ruzgar_hiz = 1.3;

void vertex() {
	vec3 w = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float t = TIME * ruzgar_hiz;
	float s = sin(t + w.x * 0.35 + w.z * 0.22) + 0.4 * sin(t * 2.3 + w.x * 1.7 + w.y);
	VERTEX.x += s * ruzgar * COLOR.a;
	VERTEX.z += cos(t * 0.8 + w.z * 0.3) * ruzgar * 0.6 * COLOR.a;
}

void fragment() {
	vec3 t = texture(doku, UV).rgb;
	ALBEDO = zb_renk(COLOR.rgb * t * 2.0);
	NORMAL_MAP = texture(doku_n, UV).rgb;
	NORMAL_MAP_DEPTH = normal_guc;
	ROUGHNESS = puruz;
	SPECULAR = 0.3;
	EMISSION = kenar * pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), 3.0) * kenar_renk * 0.3;
}
