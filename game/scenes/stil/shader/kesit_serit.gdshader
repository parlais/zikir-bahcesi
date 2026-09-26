shader_type spatial;
// Kesitte merdivenin ışıklı şeridi (K18): ilk kattaki gerçek merdivenle aynı kıvrım
// (_merdiven_yolu). Gerçek ölçekte merdiven 5,6 m'dir, kesitte piksel altında kalır:
// şerit ekranda en az en_px piksel genişliğe açılır, yakında gerçek genişliğe iner.
// Köşe verisi: UV.x kenar (-1, +1), UV.y yol boyunca oran, NORMAL yolun yönü,
// COLOR.r = 1 gerçek merdivenin olduğu kısım (yakınlaşınca ona yerini bırakır).
render_mode unshaded, cull_disabled, blend_mix, depth_draw_opaque;
#include "res://scenes/stil/shader/ortak.gdshaderinc"
#include "res://scenes/stil/shader/kesit.gdshaderinc"

uniform float en = 5.6;
uniform float en_px = 4.0;
uniform vec3 tas_renk : source_color = vec3(0.98, 0.94, 0.86);
uniform vec3 cicek_renk : source_color = vec3(1.0, 0.62, 0.7);
uniform vec3 yaprak_renk : source_color = vec3(0.24, 0.42, 0.18);
uniform float isima = 0.35;

varying vec3 dunya;
varying float gercek;
varying float boy;

void vertex() {
	vec3 merkez = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec3 yon = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
	vec3 bak = CAMERA_POSITION_WORLD - merkez;
	float uz = length(bak);
	vec3 yan = normalize(cross(yon, bak / uz));
	float piksel = 2.0 * uz / (PROJECTION_MATRIX[1][1] * VIEWPORT_SIZE.y);
	float w = max(en, en_px * piksel);
	gercek = COLOR.r * smoothstep(3.0, 6.0, en / piksel);
	vec3 p = merkez + yan * UV.x * w * 0.5;
	dunya = p;
	boy = UV.y;
	POSITION = PROJECTION_MATRIX * VIEW_MATRIX * vec4(p, 1.0);
}

void fragment() {
	// Mermer basamaklar, iki yanda yaprak ve çiçek benekleri
	// Ortada mermer basamaklar, iki yanda koyu yeşil sarmaşık ve çiçek (K10: çiçek ve
	// sarmaşıkla kaplı taş merdiven); açık gökte de seçilsin diye kenarlar koyu
	float yanlik = abs(UV.x);
	vec3 c = mix(tas_renk, yaprak_renk, smoothstep(0.35, 0.6, yanlik));
	float benek = step(0.72, fract(sin(floor(boy * 900.0) * 12.9898 + sign(UV.x) * 7.1) * 43758.5453));
	c = mix(c, cicek_renk, benek * smoothstep(0.6, 0.85, yanlik));
	c = zb_renk(c) * (1.0 + isima * (1.0 - smoothstep(0.35, 0.6, yanlik)));
	float p = zb_pus_miktar(dunya);
	ALBEDO = mix(c, zb_pus_renk(dunya), p);
	ALPHA = (1.0 - gercek) * zb_kesit;
	ALPHA_SCISSOR_THRESHOLD = 0.5;
}
