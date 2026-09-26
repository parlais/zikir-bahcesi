shader_type spatial;
// Kesitteki uzak ağaç ve yapı siluetleri (K18): gerçek modellerden önden çizilmiş
// kartlar (mf/siluet.py). Y ekseninde kameraya döner. Türü, rengi ve yeri gerçek
// ağaçla aynıdır; örnek başına renk farkı yaprak kartlarıyla aynı profilden gelir.
// INSTANCE_CUSTOM: r çeşit (ton_a..ton_b), g atlas hücresi / 16, b nur (Firdevs: ışıktan siluet).
render_mode blend_mix, depth_draw_opaque, cull_disabled;
#include "res://scenes/stil/shader/ortak.gdshaderinc"
#include "res://scenes/stil/shader/kesit.gdshaderinc"

uniform sampler2D atlas : source_color, filter_linear_mipmap, repeat_disable;
uniform vec2 atlas_hucre = vec2(3.0, 3.0);   // sütun, satır
uniform vec3 ton_a : source_color = vec3(1.0);
uniform vec3 ton_b : source_color = vec3(1.0);
uniform float alfa_esik = 0.4;
uniform float alfa_uzak = 0.35;
uniform vec3 nur_renk : source_color = vec3(1.0, 0.93, 0.76);
uniform float nur_isima = 1.6;

varying float cesit;
varying float nur;
varying float hucre;
varying vec3 dunya;

void vertex() {
	MODELVIEW_MATRIX = VIEW_MATRIX * mat4(
		vec4(normalize(cross(vec3(0.0, 1.0, 0.0), INV_VIEW_MATRIX[2].xyz)), 0.0),
		vec4(0.0, 1.0, 0.0, 0.0),
		vec4(normalize(cross(INV_VIEW_MATRIX[0].xyz, vec3(0.0, 1.0, 0.0))), 0.0),
		MODEL_MATRIX[3]);
	MODELVIEW_MATRIX = MODELVIEW_MATRIX * mat4(vec4(length(MODEL_MATRIX[0].xyz), 0.0, 0.0, 0.0),
		vec4(0.0, length(MODEL_MATRIX[1].xyz), 0.0, 0.0), vec4(0.0, 0.0, length(MODEL_MATRIX[2].xyz), 0.0),
		vec4(0.0, 0.0, 0.0, 1.0));
	MODELVIEW_NORMAL_MATRIX = mat3(MODELVIEW_MATRIX);
	// Ağaçlar uzakta hafifçe büyür, yaklaştıkça gerçek boya döner (K20). Yapılar (atlas hücresi
	// 7 ve sonrası: su köşkü, inci çadır) gerçek boyda kalır: köşkün ırmakla oranı bozulmaz.
	if (INSTANCE_CUSTOM.g * 16.0 < 6.5) {
		VERTEX *= zb_agac_olcek(MODEL_MATRIX[3].xyz, CAMERA_POSITION_WORLD);
	}
	dunya = (INV_VIEW_MATRIX * MODELVIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	cesit = INSTANCE_CUSTOM.r;
	hucre = floor(INSTANCE_CUSTOM.g * 16.0 + 0.5);
	nur = INSTANCE_CUSTOM.b;
}

void fragment() {
	vec2 h = vec2(mod(hucre, atlas_hucre.x), floor(hucre / atlas_hucre.x));
	vec2 uv = (h + clamp(UV, vec2(0.004), vec2(0.996))) / atlas_hucre;
	// Mipmap: hücreler birbirine karışmasın diye en fazla 4. seviye; alfa uzakta artar
	vec2 boyut = vec2(textureSize(atlas, 0));
	vec2 dx = dFdx(uv * boyut);
	vec2 dy = dFdy(uv * boyut);
	float lod = clamp(0.5 * log2(max(dot(dx, dx), dot(dy, dy))), 0.0, 4.0);
	vec4 t = textureLod(atlas, uv, lod);
	ALPHA = t.a * (1.0 + lod * alfa_uzak);
	ALPHA_SCISSOR_THRESHOLD = alfa_esik;
	vec3 c = t.rgb * mix(ton_a, ton_b, cesit);
	ALBEDO = zb_renk(c);
	// Taç tek bir kabarık kütle gibi ışık alsın: karta küre normali
	vec2 q = (UV - vec2(0.5, 0.45)) * vec2(1.6, -1.4);
	NORMAL = normalize(vec3(q.x, q.y + 0.2, 1.0));
	ROUGHNESS = 0.85;
	SPECULAR = 0.15;
	// Firdevs: ışıktan siluetler (albedo nura soluklaşır, kendi ışığıyla parlar)
	float l = dot(t.rgb, vec3(0.299, 0.587, 0.114));
	ALBEDO = mix(ALBEDO, nur_renk * 0.5, nur * 0.8);
	EMISSION = nur_renk * nur * nur_isima * (0.45 + 0.8 * l);
	ZB_KESIT_PUS(dunya);
}
