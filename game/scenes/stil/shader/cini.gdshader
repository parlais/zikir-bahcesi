shader_type spatial;
// Çini: dünya koordinatlarında sekiz köşeli yıldız deseni (Osmanlı geometrik
// çinisinden). Zemin rengi köşe renginden; çizgiler beyaz/altın.
render_mode blend_mix, depth_draw_opaque, cull_back;
#include "res://scenes/stil/shader/ortak.gdshaderinc"

uniform float olcek = 1.6;
uniform vec3 cizgi : source_color = vec3(0.96, 0.93, 0.85);
uniform vec3 yildiz : source_color = vec3(0.95, 0.75, 0.3);
uniform float isima_guc = 0.0;
uniform float cizgi_kalin = 0.035;

varying vec3 dunya;
varying vec3 dunya_n;

void vertex() {
	dunya = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	dunya_n = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

float kare(vec2 p, float r) {
	vec2 d = abs(p) - vec2(r);
	return max(d.x, d.y);
}

void fragment() {
	vec3 an = abs(dunya_n);
	vec2 uv = an.y > 0.6 ? dunya.xz : (an.x > an.z ? dunya.zy : dunya.xy);
	vec2 h = fract(uv * olcek) - 0.5;
	vec2 r = vec2(h.x - h.y, h.x + h.y) * 0.70710678;
	float yil = min(kare(h, 0.22), kare(r, 0.22));           // sekiz köşeli yıldız
	float capraz = min(abs(h.x), abs(h.y));
	float hat = 1.0 - smoothstep(cizgi_kalin * 0.5, cizgi_kalin, abs(yil));
	float ic = step(yil, 0.0);
	vec3 zemin = zb_renk(COLOR.rgb);
	vec3 c = mix(zemin, mix(zemin * 1.25, yildiz, 0.35), ic * 0.6);
	c = mix(c, cizgi, hat);
	c = mix(c, zemin * 0.7, (1.0 - smoothstep(0.0, 0.02, capraz)) * (1.0 - ic) * 0.5);
	ALBEDO = c;
	ROUGHNESS = 0.18;
	SPECULAR = 0.7;
	EMISSION = (hat * yildiz + ic * zemin * 0.4) * isima_guc;
}
