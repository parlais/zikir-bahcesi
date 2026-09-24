class_name AnimasyonStilleri
extends RefCounted
## Cennet mekânının animasyon stilleri (K6): Pixar, Ghibli, Arcane, Sky/Ori.
## Şema StilProfilleri ile aynıdır (gunes, gok, ortam, ortak, malzeme, parcacik);
## ek alanlar:
##   filtre   tam ekran resim filtresi (Kuwahara, kontur, kâğıt; ileride)
##   derece   katlı koni-dağın dış görünümünde üzerine yazılan alanlar
##
## Işık K5'e uyar: güneş diski görünmez, ışık yumuşak ve kaynağı belirsizdir.
## "gunes" yalnızca yumuşak gölgenin yönünü verir; gökteki parıltı (nur_yon)
## üst derecelerin ardındadır.

const SIRA := ["pixar", "ghibli", "arcane", "sky"]

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
		"parcacik": {"nur": 260, "nur_renk": Color(1.0, 0.93, 0.7), "sis_renk": Color(1.0, 1.0, 1.0, 0.45)},
		"derece": {
			"gunes": {"yukseklik": 34.0, "yon": 82.0, "enerji": 1.8, "golge_mesafe": 6000.0},
			"gok": {"kozmik": 1.0, "tepe": Color("6f8fe8"), "ufuk": Color("fff0d4"), "nur_yon": Vector3(-0.64, 0.26, -0.72),
				"nur_guc": 0.8, "nur_cekirdek": 1.2, "bulutsu_a": Color("f0a8c8"), "bulutsu_b": Color("8ea4ec"),
				"parilti": 1.4},
			"ortam": {"sis": [0.00006, Color("ffe8e0"), 0.2, 0.05], "hava_perspektif": 0.2, "sdfgi": false,
				"ssr": false, "ambient": 0.4, "pozlama": 0.85, "kontrast": 1.14, "doygunluk": 1.2},
		},
	},
}


## Profili döndürür; derece (dış görünüm) istenirse "derece" alanı üzerine yazılır.
## Henüz tanımlanmamış stiller Pixar'a düşer.
static func al(ad: String, derece := false) -> Dictionary:
	var p: Dictionary = PROFILLER.get(ad, PROFILLER["pixar"]).duplicate(true)
	if derece and p.has("derece"):
		for alan in p["derece"]:
			for anahtar in p["derece"][alan]:
				p[alan][anahtar] = p["derece"][alan][anahtar]
	return p
