shader_type spatial;
// Yaprak kümesi kartları (K15): atlas dokusu ve alfa kesme. Rüzgâr, örnek başına
// renk farkı ve arkadan ışık geçişi yaprak.gdshader ile aynıdır. Normaller modelde
// tacın dış yüzeyine bükülmüştür; arka yüzde de aynı normal kullanılır, böylece
// taç binlerce kart yerine tek bir kabarık kütle gibi ışık alır.
render_mode blend_mix, depth_draw_opaque, cull_disabled;
#include "res://scenes/stil/shader/ortak.gdshaderinc"
#include "res://scenes/stil/shader/kesit.gdshaderinc"

uniform sampler2D doku : source_color, filter_linear_mipmap_anisotropic, repeat_disable;
uniform float ruzgar = 0.08;
uniform float ruzgar_hiz = 1.3;
uniform float kipirti = 0.025;        // yaprakların titremesi (metre)
uniform vec3 ton_a : source_color = vec3(1.0);
uniform vec3 ton_b : source_color = vec3(1.0);
uniform float alfa_esik = 0.45;
// Işıma (Tûbâ): dokunun açık kısımları (altın-beyaz kenarlar) kendi ışığıyla parlar
uniform float isima_guc = 0.0;
uniform vec3 isima_renk : source_color = vec3(1.0);
uniform float alfa_uzak = 0.22;       // mipmap seviyesi başına alfa artışı (uzakta taç seyrelmesin)

varying float cesit;
varying vec3 dunya;

void vertex() {
	vec3 w = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float t = TIME * ruzgar_hiz;
	float s = sin(t + w.x * 0.35 + w.z * 0.22) + 0.4 * sin(t * 2.3 + w.x * 1.7 + w.y);
	VERTEX.x += s * ruzgar * COLOR.a;
	VERTEX.z += cos(t * 0.8 + w.z * 0.3) * ruzgar * 0.6 * COLOR.a;
	// Titreme: rüzgâr ağırlığı büyük (dıştaki) yapraklar daha çok kıpırdar
	VERTEX.y += sin(TIME * 5.0 + w.x * 3.1 + w.z * 2.3) * kipirti * COLOR.a * COLOR.a;
	cesit = INSTANCE_CUSTOM.r;
	dunya = w;
}

void fragment() {
	vec4 t = texture(doku, UV);
	vec2 boyut = vec2(textureSize(doku, 0));
	vec2 dx = dFdx(UV * boyut);
	vec2 dy = dFdy(UV * boyut);
	float lod = max(0.5 * log2(max(dot(dx, dx), dot(dy, dy))), 0.0);
	ALPHA = t.a * (1.0 + lod * alfa_uzak);
	ALPHA_SCISSOR_THRESHOLD = alfa_esik;
	vec3 c = t.rgb * COLOR.rgb * mix(ton_a, ton_b, cesit);
	c *= 0.94 + 0.12 * zb_gurultu(dunya * 1.5);
	ALBEDO = zb_renk(c);
	ROUGHNESS = 0.8;
	SPECULAR = 0.2;
	if (!FRONT_FACING) {
		NORMAL = -NORMAL;
	}
	EMISSION = kenar * pow(1.0 - clamp(abs(dot(NORMAL, VIEW)), 0.0, 1.0), 4.0) * kenar_renk * ALBEDO * 0.6;
	if (isima_guc > 0.0) {
		float isik = dot(t.rgb, vec3(0.299, 0.587, 0.114));
		EMISSION += t.rgb * isima_renk * isima_guc * smoothstep(0.5, 0.85, isik);
	}
	// Kesit (K18): dıştan bakınca katın pusu; içeride etkisiz (zb_kesit = 0)
	ZB_KESIT_PUS(dunya);
}
