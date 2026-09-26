shader_type spatial;
// Almaşık altın ve gümüş tuğla, misk harç (et-Tâc 5/402): dünya koordinatlarında
// şaşırtmalı tuğla dizisi. Uzaklaştıkça desen ortalama renge yumuşakça döner.
render_mode blend_mix, depth_draw_opaque, cull_back;
#include "res://scenes/stil/shader/ortak.gdshaderinc"
#include "res://scenes/stil/shader/kesit.gdshaderinc"

uniform vec3 tugla_a : source_color = vec3(0.93, 0.76, 0.44);   // altın
uniform vec3 tugla_b : source_color = vec3(0.9, 0.91, 0.94);    // gümüş
uniform vec3 harc : source_color = vec3(0.3, 0.22, 0.16);       // misk
uniform vec2 boyut = vec2(0.72, 0.3);
uniform float harc_kalin = 0.03;
uniform float metal_a = 0.55;
uniform float metal_b = 0.5;
uniform float puruz = 0.32;
uniform float isima_guc = 0.0;

varying vec3 dunya;
varying vec3 dunya_n;

void vertex() {
	dunya = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	dunya_n = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

void fragment() {
	vec3 an = abs(dunya_n);
	vec2 uv = an.y > 0.7 ? dunya.xz : (an.x > an.z ? dunya.zy : dunya.xy);
	vec2 q = uv / boyut;
	float sira = floor(q.y);
	q.x += mod(sira, 2.0) * 0.5;
	vec2 hucre = floor(q);
	vec2 f = fract(q);
	float h = zb_hash(vec3(hucre, 1.3));
	float sec = mod(hucre.x + sira, 2.0);
	vec3 c = mix(tugla_a, tugla_b, sec) * (0.9 + 0.2 * h);
	float m = min(min(f.x, 1.0 - f.x) * boyut.x, min(f.y, 1.0 - f.y) * boyut.y);
	float w = fwidth(m) + 1e-4;
	float hat = 1.0 - smoothstep(harc_kalin * 0.5 - w, harc_kalin * 0.5 + w, m);
	float uzak = clamp(max(fwidth(q.x), fwidth(q.y)) * 2.5 - 0.4, 0.0, 1.0);
	vec3 ort = mix((tugla_a + tugla_b) * 0.5, harc, 0.12);
	c = mix(c, harc, hat);
	c = mix(c, ort, uzak);
	ALBEDO = zb_renk(c);
	METALLIC = mix(mix(metal_a, metal_b, sec) * (1.0 - hat), (metal_a + metal_b) * 0.45, uzak);
	ROUGHNESS = puruz + hat * 0.5;
	EMISSION = c * isima_guc + kenar * pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), 3.0) * kenar_renk * 0.3;
	// Kesit (K18): dıştan bakınca katın pusu; içeride etkisiz (zb_kesit = 0)
	ZB_KESIT_PUS(dunya);
}
