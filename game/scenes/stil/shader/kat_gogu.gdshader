shader_type spatial;
// Katın göğü (K10, K18): kesitte her katın perdesi ve (yakınlaşmada görünen) tavanı.
// İçeriden görülen gökyüzünün aynısını çizer (gok_ortak: aynı renkler, aynı nur, aynı
// bulut deseni; profilin "kat_gok" alanı, Nur <-> Ori ile karışır).
//   bant = 1: perdedeki yükseklik, bant içinde 0°-45°'lik bakış yüksekliğine eşlenir: her
//             bantta ufuk ışığı, gök mavisi ve bulutlar görünür (dışarıdan kesit).
//   bant = 0: gerçek bakış yönü: içeriden bakana göğün kendisi (yakınlaşmada tavan).
// Üst katlarda gök nura karışır; Firdevs'in havası tamamen nurdur (mavi yok).
render_mode unshaded, cull_back, fog_disabled;
#include "res://scenes/stil/shader/gok_ortak.gdshaderinc"
#include "res://scenes/stil/shader/kesit.gdshaderinc"

uniform float bant = 1.0;
uniform float bant_yukseklik = 440.0;   // 45°'ye eşlenen yükseklik (m): perdenin kesitte görünen kısmı

varying vec3 dunya;

void vertex() {
	dunya = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec2 kh = zb_kat(dunya);
	float yuk = dunya.y - kh.x * zb_kesit_olcu.y;
	float e = radians(45.0) * clamp(yuk / bant_yukseklik, 0.0, 1.8);
	float az = dunya.x / 5000.0;
	vec3 d_bant = vec3(sin(az) * cos(e), sin(e), -cos(az) * cos(e));
	vec3 d_gercek = normalize(dunya - CAMERA_POSITION_WORLD);
	vec3 c = gok_renk(normalize(mix(d_gercek, d_bant, bant)));
	c = mix(c, zb_pus_nur, 0.75 * zb_kat_isik(kh.x) + 0.25 * step(6.5, kh.x));
	ALBEDO = c;
}
