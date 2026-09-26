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
#include "res://scenes/stil/shader/kat_gogu.gdshaderinc"
