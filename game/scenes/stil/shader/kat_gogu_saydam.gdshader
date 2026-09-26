shader_type spatial;
// Yakınlaşmada eriyen ilk kat perdesi (K19): kat_gogu'nun saydam türü (opaklik).
render_mode unshaded, cull_back, fog_disabled;
#define SAYDAM
#include "res://scenes/stil/shader/kat_gogu.gdshaderinc"
