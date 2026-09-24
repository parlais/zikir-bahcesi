shader_type spatial;
// Çağlayan: dünya koordinatında aşağı akan uzun çizgiler ve köpük. Köşe ağırlığı
// (COLOR.a) şeridin tepesinde 1, dibinde 0'dır: dipte köpük ve sis yoğunlaşır.
render_mode blend_mix, depth_draw_opaque, cull_disabled;
#include "res://scenes/stil/shader/ortak.gdshaderinc"

uniform vec3 su_renk : source_color = vec3(0.62, 0.86, 0.9);
uniform vec3 derin_renk : source_color = vec3(0.25, 0.55, 0.62);
uniform vec3 kopuk : source_color = vec3(1.0);
uniform float hiz = 1.0;
uniform float cizgi_olcek = 1.0;
uniform float isima_guc = 0.25;
uniform float saydamlik = 0.85;

varying vec3 dunya;
varying float tepe;

void vertex() {
	dunya = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	tepe = COLOR.a;
}

void fragment() {
	float t = TIME * hiz;
	vec3 p = dunya * cizgi_olcek;
	float yatay = (p.x + p.z) * 0.9;
	// Uzaktan bakınca ince çizgiler titreşmesin: ayrıntıyı ekran türeviyle söndür
	float ayrinti = 1.0 - clamp(fwidth(yatay) * 1.5 - 0.3, 0.0, 1.0);
	float cizgi = zb_fbm(vec3(yatay * 1.4, p.y * 0.05 + t * 1.6, 0.0));
	float ince = zb_gurultu(vec3(yatay * 5.0, p.y * 0.12 + t * 3.2, 2.0));
	float akis = mix(0.55, cizgi * 0.7 + ince * 0.5, ayrinti);
	float kop = smoothstep(0.35, 0.0, tepe) * (0.6 + 0.4 * ince) + smoothstep(0.9, 1.0, tepe) * 0.5;
	vec3 c = mix(derin_renk, su_renk, akis);
	c = mix(c, kopuk, clamp(kop + smoothstep(0.62, 0.85, akis) * 0.6, 0.0, 1.0));
	ALBEDO = zb_renk(c);
	ROUGHNESS = 0.25;
	SPECULAR = 0.6;
	EMISSION = c * isima_guc;
	ALPHA = clamp(saydamlik + kop * 0.3 + akis * 0.15, 0.0, 1.0);
	if (!FRONT_FACING) {
		NORMAL = -NORMAL;
	}
}
