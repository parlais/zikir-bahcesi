shader_type spatial;
// Katın göğü (K10, K18): kesitte her katın perdesi ve (yakınlaşmada görünen) tavanı.
// İçeriden görülen gökyüzünün aynısını çizer (gok_ortak: aynı renkler, aynı nur, aynı
// bulut deseni; profilin "kat_gok" alanı, Nur <-> Ori ile karışır).
//   bant = 1: gök, katın havasına konmuş sanal bir gözden görülür. Göz, perdenin
//             bant_yukseklik kadar önünde, zemin hizasındadır: perdede 0-440 m, 0-45°'lik
//             bakışa eşlenir (her bantta ufuk ışığı, gök ve bulutlar; dışarıdan kesit).
//             Tavan aynı gözden görülür, perdenin üst kenarından devam eder (dikişsiz).
//   bant = 0: gerçek bakış yönü: içeriden bakana göğün kendisi. Yakınlaşmada ilk katın
//             perdesi ve tavanı bu kipe döner; tavan gizlendiği an gök sıçramaz.
// Üst katlarda gök nura karışır; Firdevs'in havası tamamen nurdur (mavi yok).
render_mode unshaded, cull_back, fog_disabled;
#include "res://scenes/stil/shader/gok_ortak.gdshaderinc"
#include "res://scenes/stil/shader/kesit.gdshaderinc"

uniform float bant = 1.0;
uniform float bant_yukseklik = 440.0;   // 45°'ye eşlenen yükseklik (m): perdenin kesitte görünen kısmı
uniform float opaklik = 1.0;            // yakınlaşmada ilk katın perdesi erir

varying vec3 dunya;

void vertex() {
	dunya = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	// Tavan (katın üstü, G + hava) ve perdenin üst kenarı bir sonraki katın sınırına değer
	vec2 kh = zb_kat(dunya - vec3(0.0, 10.0, 0.0));
	float yuk = max(dunya.y - kh.x * zb_kesit_olcu.y, 0.0);
	// Sanal göz: perdenin bant_yukseklik önünde; h ileri (−z) uzaklık, tavanda arkaya döner
	float h = zb_kesit_olcu.x - zb_pencere(kh.x) + bant_yukseklik - dunya.z;
	float az = dunya.x / 5000.0;
	vec3 d_bant = normalize(vec3(sin(az) * h, yuk, -cos(az) * h));
	vec3 d_gercek = normalize(dunya - CAMERA_POSITION_WORLD);
	vec3 c = gok_renk(normalize(mix(d_gercek, d_bant, bant)));
	c = mix(c, zb_pus_nur, 0.75 * zb_kat_isik(kh.x) + 0.25 * step(6.5, kh.x));
	ALBEDO = c;
	ALPHA = opaklik;
}
