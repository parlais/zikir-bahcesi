// Katın göğü: kat_gogu (opak) ve kat_gogu_saydam (yakınlaşmada eriyen ilk kat perdesi) ortak kodu.
// ALPHA yalnız saydam türde yazılır: yazılan her malzeme saydam geçişe düşer, derinlik yazmaz;
// tavan opak olmazsa arkasındaki üst katın ağaç siluetleri tavanın üstünde görünüyordu.
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
	// Sanal göz: perdenin bant_yukseklik önünde; h ileri (−z) uzaklık. Bakış yüksekliği
	// perdenin üst kenarındakini (~61°) aşmaz: tavan perdenin üst renginin sakin devamıdır.
	// (Başucu, içeriden hiç görülmeyen koyu gök mavisidir; Ori'de lacivert bir bant oluyordu.)
	float h = zb_kesit_olcu.x - zb_pencere(kh.x) + bant_yukseklik - dunya.z;
	h = max(h, yuk * bant_yukseklik / zb_kesit_olcu.w);
	float az = dunya.x / 5000.0;
	vec3 d_bant = normalize(vec3(sin(az) * h, yuk, -cos(az) * h));
	vec3 d_gercek = normalize(dunya - CAMERA_POSITION_WORLD);
	vec3 c = gok_renk(normalize(mix(d_gercek, d_bant, bant)));
	c = mix(c, zb_pus_nur, 0.75 * zb_kat_isik(kh.x) + 0.25 * step(6.5, kh.x));
	ALBEDO = c;
#ifdef SAYDAM
	ALPHA = opaklik;
#endif
}
