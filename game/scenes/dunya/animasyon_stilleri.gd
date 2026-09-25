class_name AnimasyonStilleri
extends RefCounted
## Cennet mekânının animasyon stilleri (K6): Pixar, Ghibli, Arcane, Sky/Ori.
## Şema StilProfilleri ile aynıdır (gunes, gok, ortam, ortak, malzeme, parcacik);
## ek alanlar:
##   filtre   tam ekran resim filtresi (resim_filtresi.gdshader uniform'ları); yoksa filtre yok
##   kesit    tabakaların dıştan kesit görünümünde üzerine yazılan alanlar (K10)
##
## Işık K5'e uyar: güneş diski görünmez, ışık yumuşak ve kaynağı belirsizdir.
## "gunes" yalnızca yumuşak gölgenin yönünü verir; gökteki parıltı (nur_yon)
## ufuktaki ışıktadır.

const SIRA := ["pixar", "ghibli", "arcane", "sky", "yagli_boya"]

const PROFILLER := {
	# ------------------------------------------------------------------
	"pixar": {
		"ad": "Pixar", "alt": "Yumuşak ve yuvarlak ışık, zengin dolaylı aydınlatma, temiz ve doygun renkler",
		"gunes": {"yukseklik": 42.0, "yon": 262.0, "renk": Color("fff0d8"), "enerji": 1.7, "yumusak": 3.5,
			"golge_mesafe": 160.0, "golge_bulanik": 2.0},
		"gok": {"tepe": Color("2a6fd6"), "orta": Color("72b2f0"), "ufuk": Color("ffe8c8"), "alt": Color("f0e0cc"),
			"ufuk_kalin": 0.22, "nur_yon": Vector3(-0.08, 0.2, -1.0), "nur_renk": Color("fff0cc"), "nur_guc": 0.9,
			"nur_cekirdek": 1.2, "bulut": 0.56, "bulut_olcek": 0.8, "bulut_yukseklik": 0.3,
			"bulut_acik": Color("ffffff"), "bulut_golge": Color("a8bce8"), "bulut_kenar": Color("ffe8c8"),
			"kozmik": 0.0, "parlaklik": 1.0},
		"ortam": {"ambient": 0.5, "ton": "aces", "pozlama": 1.0, "beyaz": 6.0,
			"parlama": [0.35, 0.9, 0.03, 1.3], "sis": [0.00032, Color("fff0dc"), 0.25, 0.12],
			"hava_perspektif": 0.4, "hacim_sis": [0.0, Color.WHITE, 0.0, 0.0],
			"sdfgi": true, "sdfgi_hucre": 0.4, "ssao": 0.8, "ssr": true,
			"doygunluk": 1.12, "kontrast": 1.08, "parlaklik": 1.0},
		"ortak": {"toon": 0.0, "doygunluk": 1.06, "renk_carpan": Color("fff9f0"), "sarma": 0.38,
			"kenar": 0.3, "kenar_renk": Color("ffe8c0"), "spek": 0.3},
		"malzeme": {
			"yaprak": {"gecirgenlik": 1.1, "gecirgen_renk": Color("dcff86"), "ton_a": Color("eef8d4"), "ton_b": Color("fff6d0")},
			"zemin": {"cimen_acik": Color("a4d85c"), "cimen_koyu": Color("4a9440"), "kuru": Color("e8dc7c"),
				"kuru_miktar": 0.15, "cicek_yogun": 0.45, "filiz_miktar": 0.35},
			"cimen": {"dip": Color("3a7c30"), "uc": Color("c4e878"), "gecirgenlik": 1.0, "gecirgen_renk": Color("e0ff90")},
			"su": {"derin": Color("137a8c"), "sig": Color("48d0cc"), "isima_guc": 0.06, "isima": Color("80fff0"),
				"akis": Vector2(0.0, 0.5)},
			"sut": {"derin": Color("efe8dc"), "sig": Color("fffcf6"), "isima_guc": 0.18, "isima": Color("fff8ea"),
				"akis": Vector2(0.0, 0.35)},
			"bal": {"isima_guc": 0.2, "isima": Color("ffb040"), "akis": Vector2(0.0, 0.25), "puruz": 0.06},
			"serbet": {"isima_guc": 0.15, "isima": Color("ff5070"), "akis": Vector2(0.0, 0.4)},
			"selale": {"su_renk": Color("b8f0f4"), "derin_renk": Color("5ab8c4"), "isima_guc": 0.35},
			"tugla": {"tugla_a": Color("f0c878"), "tugla_b": Color("e8ecf2")},
			"cini": {"isima_guc": 0.0},
			"cicek": {"isima_guc": 0.06},
			"inci": {"isima": Color("fff6ee"), "isima_guc": 0.12},
			"nur": {"isima_guc": 5.0},
		},
		"bulut_denizi": {"acik": Color("fff6ee"), "golge": Color("a8acdc"), "isima": Color("ffd8c0"), "isima_guc": 0.18},
		"bulut_renk": [Color("ffffff"), Color("c4d0f0")],
		"parcacik": {"nur": 260, "nur_renk": Color(1.0, 0.93, 0.7), "sis_renk": Color(1.0, 1.0, 1.0, 0.45)},
		"kesit": {
			"gunes": {"yukseklik": 40.0, "yon": 335.0, "enerji": 1.5, "golge_mesafe": 6000.0},
			"gok": {"kozmik": 1.0, "tepe": Color("6f8fe8"), "ufuk": Color("fff0d4"), "nur_yon": Vector3(-0.64, 0.26, -0.72),
				"nur_guc": 0.8, "nur_cekirdek": 1.2, "bulutsu_a": Color("f0a8c8"), "bulutsu_b": Color("8ea4ec"),
				"parilti": 1.4},
			"ortam": {"sis": [0.00006, Color("ffe8e0"), 0.2, 0.05], "hava_perspektif": 0.2, "sdfgi": false,
				"ssr": false, "ambient": 0.4, "pozlama": 0.85, "kontrast": 1.14, "doygunluk": 1.2},
		},
	},
	# ------------------------------------------------------------------
	"yagli_boya": {
		"ad": "Yağlı boya", "alt": "Yaşayan bir yağlı boya tablosu: ışıklı bulutlar, fırça izleri, zengin ve sıcak renkler",
		"gunes": {"yukseklik": 36.0, "yon": 250.0, "renk": Color("fff0cc"), "enerji": 1.6, "yumusak": 4.0,
			"golge_mesafe": 180.0, "golge_bulanik": 2.5},
		"gok": {"tepe": Color("0f4fb8"), "orta": Color("3a8ee0"), "ufuk": Color("ffe9b8"), "alt": Color("f4e4c8"),
			"ufuk_kalin": 0.2, "nur_yon": Vector3(-0.03, 0.34, -1.0), "nur_renk": Color("ffe8a0"), "nur_guc": 0.9,
			"nur_cekirdek": 1.4, "bulut": 0.46, "bulut_olcek": 0.7, "bulut_yukseklik": 0.36,
			"bulut_acik": Color("fffbe8"), "bulut_golge": Color("8ea4e0"), "bulut_kenar": Color("ffe7a0"),
			"kozmik": 0.0, "parlaklik": 1.0},
		"ortam": {"ambient": 0.55, "ton": "aces", "pozlama": 0.95, "beyaz": 6.0,
			"parlama": [0.4, 0.9, 0.05, 1.2], "sis": [0.00024, Color("fff0d4"), 0.3, 0.05],
			"hava_perspektif": 0.45, "hacim_sis": [0.0, Color.WHITE, 0.0, 0.0],
			"sdfgi": true, "sdfgi_hucre": 0.4, "ssao": 0.9, "ssr": true,
			"doygunluk": 1.2, "kontrast": 1.08, "parlaklik": 1.0},
		"ortak": {"toon": 0.0, "doygunluk": 1.1, "renk_carpan": Color("fff7e8"), "sarma": 0.45,
			"kenar": 0.35, "kenar_renk": Color("ffe2a0"), "spek": 0.2},
		"malzeme": {
			"yaprak": {"gecirgenlik": 1.3, "gecirgen_renk": Color("e8ff80"), "ton_a": Color("f0fad0"), "ton_b": Color("fff2c0")},
			"zemin": {"cimen_acik": Color("9cd456"), "cimen_koyu": Color("3c8a3a"), "kuru": Color("ecd876"),
				"kuru_miktar": 0.18, "cicek_yogun": 0.55, "filiz_miktar": 0.35},
			"cimen": {"dip": Color("2f7430"), "uc": Color("c8ea70"), "gecirgenlik": 1.2, "gecirgen_renk": Color("e8ff90")},
			"su": {"derin": Color("0b4f9c"), "sig": Color("2ab0d8"), "isima_guc": 0.08, "isima": Color("70e8ff"),
				"akis": Vector2(0.0, 0.5)},
			"sut": {"derin": Color("efe8dc"), "sig": Color("fffcf6"), "isima_guc": 0.2, "isima": Color("fff8ea"),
				"akis": Vector2(0.0, 0.35)},
			"bal": {"isima_guc": 0.25, "isima": Color("ffb040"), "akis": Vector2(0.0, 0.25), "puruz": 0.06},
			"serbet": {"isima_guc": 0.18, "isima": Color("ff5070"), "akis": Vector2(0.0, 0.4)},
			"selale": {"su_renk": Color("c8f4ff"), "derin_renk": Color("5aa8d8"), "isima_guc": 0.45},
			"tugla": {"tugla_a": Color("f4c870"), "tugla_b": Color("eceff4")},
			"cini": {"isima_guc": 0.05},
			"cicek": {"isima_guc": 0.12},
			"inci": {"isima": Color("fff6ee"), "isima_guc": 0.15},
			"nur": {"isima_guc": 5.0},
			"tavan": {"guc": 1.0, "bulut": 0.35},
		},
		"filtre": {"yaricap": 5.0, "anizotropi": 1.0, "keskinlik": 8.0, "firca": 0.09, "firca_olcek": 1.0,
			"impasto": 0.7, "tuval": 0.035, "gren": 0.01, "doygunluk": 1.14, "kontrast": 1.08,
			"sicak": Color("fff3dc"), "golge_ton": Color("dfe0ff"), "vinyet": 0.2},
		"bulut_renk": [Color(1.35, 1.32, 1.22), Color(0.98, 1.02, 1.2)],
		"parcacik": {"nur": 220, "nur_renk": Color(1.0, 0.93, 0.66), "sis_renk": Color(1.0, 1.0, 1.0, 0.45)},
		"kesit": {
			"gunes": {"yukseklik": 40.0, "yon": 335.0, "enerji": 1.5, "golge_mesafe": 6000.0},
			"gok": {"kozmik": 1.0, "tepe": Color("12306e"), "ufuk": Color("ffe39a"), "nur_yon": Vector3(0.0, 0.93, -0.36),
				"nur_guc": 1.2, "nur_cekirdek": 1.6, "bulutsu_a": Color("5a8ee0"), "bulutsu_b": Color("1b3f9a"),
				"parilti": 1.0},
			"ortam": {"sis": [0.000002, Color("fff0e0"), 0.2, 0.0], "hava_perspektif": 0.0, "sdfgi": false,
				"ssr": false, "ssao": 0.0, "ambient": 0.55, "pozlama": 0.95, "kontrast": 1.1, "doygunluk": 1.2},
		},
	},
}


## Profili döndürür; kesit (dış görünüm) istenirse "kesit" alanı üzerine yazılır.
## Henüz tanımlanmamış stiller Pixar'a düşer.
static func al(ad: String, kesit := false) -> Dictionary:
	var p: Dictionary = PROFILLER.get(ad, PROFILLER["pixar"]).duplicate(true)
	if kesit and p.has("kesit"):
		for alan in p["kesit"]:
			for anahtar in p["kesit"][alan]:
				p[alan][anahtar] = p["kesit"][alan][anahtar]
	return p
