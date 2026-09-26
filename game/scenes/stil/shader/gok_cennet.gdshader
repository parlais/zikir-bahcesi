shader_type sky;
// Cennet göğü (K5): güneş diski yok; ışık yumuşak ve kaynağı belirsiz. Üst
// derecelerin ardından gelen geniş bir nur parıltısı, kabarık kümülüs bulutları.
// kozmik = 1: katlı koni-dağın dıştan görünümü için ışıklı, pastel bir boşluk
// (Küllî Kaideler 2: galaksiler ve güneşler bu bahçenin çiçekleri gibidir).
// Gökyüzünün kodu gok_ortak.gdshaderinc içindedir (kesitteki katların göğüyle ortak).

#include "res://scenes/stil/shader/gok_ortak.gdshaderinc"

void sky() {
	COLOR = gok_renk(EYEDIR);
}
