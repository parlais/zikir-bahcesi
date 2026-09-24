class_name StilProfilleri
extends RefCounted
## Stil karşılaştırmasının dört yönü. Aynı sahne ve aynı modeller; farkı ışık,
## gökyüzü, atmosfer, malzeme parametreleri ve arayüz renkleri yaratır.
##
## Alanlar:
##   gunes      yükseklik/yön (derece), renk, enerji, gölge yumuşaklığı
##   gok        gok.gdshader uniform'ları
##   ortam      Environment ayarları (sis, hacimli sis, parlama, GI, SSR...)
##   ortak      bütün stil shader'larına giden ortak uniform'lar (ortak.gdshaderinc)
##   malzeme    malzeme adına özel uniform'lar (yaprak, zemin, su, çini...)
##   kandil     fener/kandil ışıkları
##   parcacik   nur zerreleri ve uçuşan yapraklar
##   arayuz     arayüz renkleri ve yazı tipleri

const SIRA := ["nur", "ghibli", "mucevher", "gercekci"]

const PROFILLER := {
	# ------------------------------------------------------------------
	"nur": {
		"ad": "Nur", "alt": "Ruhani, altın saat: ışık hüzmeleri, sis, parlayan su",
		"gunes": {"yukseklik": 9.0, "yon": 172.0, "renk": Color("ffd08a"), "enerji": 2.2, "yumusak": 2.5},
		"gok": {"tepe": Color("5a86d0"), "ufuk": Color("ffd298"), "alt": Color("e8c7a0"), "ufuk_kalin": 0.4,
			"gunes_renk": Color("ffcf8a"), "gunes_boyut": 1.3, "gunes_hale": 0.7, "gunes_parlak": 10.0,
			"bulut": 0.42, "bulut_olcek": 0.8, "bulut_acik": Color("fff2dc"), "bulut_golge": Color("e0b8a4"),
			"yildiz": 0.0, "ay": 0.0, "parlaklik": 1.0},
		"ortam": {"ambient": 0.45, "ton": "aces", "pozlama": 1.1, "beyaz": 6.0,
			"parlama": [0.55, 1.0, 0.04, 1.2], "sis": [0.0006, Color("ffd9a6"), 0.45, 0.12],
			"hacim_sis": [0.002, Color("ffe6c4"), 0.6, 80.0], "sdfgi": true, "ssao": 0.9, "ssr": true,
			"doygunluk": 1.15, "kontrast": 1.14, "parlaklik": 0.97},
		"ortak": {"toon": 0.0, "doygunluk": 0.95, "renk_carpan": Color("fff4e4"), "sarma": 0.35,
			"kenar": 0.35, "kenar_renk": Color("ffd9a0"), "spek": 0.3},
		"malzeme": {
			"yaprak": {"gecirgenlik": 1.6, "gecirgen_renk": Color("ffd070"), "ton_a": Color("e4f0c8"), "ton_b": Color("fff0c0")},
			"zemin": {"cimen_acik": Color("b6c86a"), "cimen_koyu": Color("5b7f3c"), "kuru": Color("e4c77a"), "kuru_miktar": 0.45},
			"cimen": {"dip": Color("476b2c"), "uc": Color("e2dc84"), "gecirgenlik": 1.4, "gecirgen_renk": Color("ffd070")},
			"su": {"derin": Color("20464e"), "sig": Color("5fa8a0"), "isima_guc": 0.08, "isima": Color("ffd48a")},
			"cini": {"isima_guc": 0.05},
			"cicek": {"isima_guc": 0.05},
			"nur": {"isima_guc": 3.0},
		},
		"kandil": {"enerji": 0.6, "renk": Color("ffcf80")},
		"parcacik": {"nur": 900, "nur_renk": Color(1.0, 0.9, 0.6), "yaprak": 140, "yaprak_renk": Color("ffd6e0")},
		"arayuz": {"metin": Color("fffaf0"), "golge": Color(0.35, 0.2, 0.05, 0.55), "vurgu": Color("ffd27a"),
			"cam": Color(1.0, 0.97, 0.9, 0.18), "cerceve": Color("ffe2a8"), "perde": Color("3a2410"),
			"dugme_ic": Color("fff3d6"), "dugme_dis": Color("e2b35c"), "latin": "Marcellus-Regular", "susleme": false},
	},
	# ------------------------------------------------------------------
	"ghibli": {
		"ad": "Boyalı", "alt": "Ghibli havası: parlak gök, kabarık bulutlar, yumuşak çizgi film ışığı",
		"gunes": {"yukseklik": 48.0, "yon": 215.0, "renk": Color("fff6e0"), "enerji": 1.6, "yumusak": 1.2},
		"gok": {"tepe": Color("2f7fe0"), "ufuk": Color("bfe4ff"), "alt": Color("9cc3d8"), "ufuk_kalin": 0.3,
			"gunes_renk": Color("fff4d6"), "gunes_boyut": 1.2, "gunes_hale": 0.25, "gunes_parlak": 10.0,
			"bulut": 0.55, "bulut_olcek": 0.55, "bulut_acik": Color("ffffff"), "bulut_golge": Color("a9bde0"),
			"yildiz": 0.0, "ay": 0.0, "parlaklik": 1.0},
		"ortam": {"ambient": 0.6, "ton": "filmic", "pozlama": 1.05, "beyaz": 4.0,
			"parlama": [0.35, 0.8, 0.05, 1.1], "sis": [0.0007, Color("cfe6ff"), 0.1, 0.12],
			"hacim_sis": [0.0, Color.WHITE, 0.0, 0.0], "sdfgi": true, "ssao": 0.5, "ssr": true,
			"doygunluk": 1.04, "kontrast": 1.06, "parlaklik": 1.02},
		"ortak": {"toon": 0.9, "toon_esik": 0.5, "toon_yumusak": 0.04, "golge_renk": Color("6a78c8"),
			"doygunluk": 1.05, "renk_carpan": Color("ffffff"), "sarma": 0.2, "kenar": 0.25, "kenar_renk": Color("ffffff"), "spek": 0.15},
		"malzeme": {
			"yaprak": {"gecirgenlik": 0.4, "gecirgen_renk": Color("e8ff9a"), "ton_a": Color("d8f0a0"), "ton_b": Color("a8e0a0")},
			"zemin": {"cimen_acik": Color("9ccf62"), "cimen_koyu": Color("45914a"), "kuru": Color("d8d070"), "kuru_miktar": 0.25},
			"cimen": {"dip": Color("2f7a3c"), "uc": Color("b4e070")},
			"su": {"derin": Color("12508a"), "sig": Color("46b8d8"), "isima_guc": 0.0},
			"cini": {"isima_guc": 0.0},
			"nur": {"isima_guc": 1.5},
		},
		"kandil": {"enerji": 0.0, "renk": Color("ffcf80")},
		"parcacik": {"nur": 160, "nur_renk": Color(1.0, 1.0, 0.85), "yaprak": 220, "yaprak_renk": Color("ffc4d8")},
		"arayuz": {"metin": Color("24361c"), "golge": Color(1, 1, 1, 0.9), "vurgu": Color("ef7a5a"),
			"cam": Color(1.0, 0.99, 0.94, 0.9), "cerceve": Color("7cae4c"), "perde": Color("fff8e8"),
			"dugme_ic": Color("fff8e8"), "dugme_dis": Color("6fae4a"), "latin": "Nunito", "susleme": false},
	},
	# ------------------------------------------------------------------
	"mucevher": {
		"ad": "Mücevher", "alt": "Osmanlı gecesi: lacivert gök, hilal, yanan kandiller, altın ve zümrüt",
		"gunes": {"yukseklik": 25.0, "yon": 203.0, "renk": Color("a8b8ff"), "enerji": 0.7, "yumusak": 0.6},
		"gok": {"tepe": Color("040a2a"), "ufuk": Color("2a2260"), "alt": Color("0a0a20"), "ufuk_kalin": 0.3,
			"gunes_renk": Color("7f8fff"), "gunes_boyut": 0.0, "gunes_hale": 0.05, "gunes_parlak": 0.0,
			"bulut": 0.25, "bulut_olcek": 0.7, "bulut_acik": Color("4a3f8a"), "bulut_golge": Color("1a1848"),
			"yildiz": 1.4, "ay": 1.0, "ay_yon": Vector3(-0.35, 0.42, -0.84), "parlaklik": 0.75},
		"ortam": {"ambient": 0.22, "ton": "aces", "pozlama": 1.3, "beyaz": 5.0,
			"parlama": [0.75, 1.1, 0.06, 0.9], "sis": [0.0012, Color("1c1a52"), 0.0, 0.08],
			"hacim_sis": [0.004, Color("6a6ac0"), 0.3, 60.0], "sdfgi": true, "ssao": 0.9, "ssr": true,
			"doygunluk": 1.1, "kontrast": 1.08, "parlaklik": 1.0},
		"ortak": {"toon": 0.0, "doygunluk": 1.15, "renk_carpan": Color("c4ccff"), "sarma": 0.15,
			"kenar": 0.25, "kenar_renk": Color("7fa0ff"), "spek": 0.5},
		"malzeme": {
			"yaprak": {"gecirgenlik": 0.2, "gecirgen_renk": Color("9fffd0"), "ton_a": Color("7fcf9a"), "ton_b": Color("5fb4a0")},
			"zemin": {"cimen_acik": Color("3f8a5a"), "cimen_koyu": Color("173f34"), "kuru": Color("4a6a50"), "kuru_miktar": 0.1},
			"cimen": {"dip": Color("12362c"), "uc": Color("4fa070")},
			"su": {"derin": Color("031a2a"), "sig": Color("0f6a78"), "isima_guc": 0.9, "isima": Color("1fe0d0")},
			"cini": {"isima_guc": 0.9, "yildiz": Color("ffc85a")},
			"cicek": {"isima_guc": 0.25},
			"nur": {"isima_guc": 6.0},
			"altin": {"isima_guc": 0.6},
		},
		"kandil": {"enerji": 3.2, "renk": Color("ffb45a")},
		"parcacik": {"nur": 1200, "nur_renk": Color(1.0, 0.8, 0.45), "yaprak": 0, "yaprak_renk": Color.WHITE},
		"arayuz": {"metin": Color("fff1d0"), "golge": Color(0.02, 0.02, 0.1, 0.7), "vurgu": Color("f2c35c"),
			"cam": Color(0.05, 0.08, 0.25, 0.55), "cerceve": Color("e8b64a"), "perde": Color("050b2a"),
			"dugme_ic": Color("0f2a6e"), "dugme_dis": Color("f2c35c"), "latin": "Marcellus-Regular", "susleme": true},
	},
	# ------------------------------------------------------------------
	"gercekci": {
		"ad": "Fantastik-gerçekçi", "alt": "Genshin ve Zelda arası: berrak ışık, derinlik, canlı ama doğal renkler",
		"gunes": {"yukseklik": 32.0, "yon": 235.0, "renk": Color("fff0dc"), "enerji": 2.0, "yumusak": 0.8},
		"gok": {"tepe": Color("3b74c8"), "ufuk": Color("d6e6f4"), "alt": Color("a0b0bc"), "ufuk_kalin": 0.32,
			"gunes_renk": Color("fff0d8"), "gunes_boyut": 1.0, "gunes_hale": 0.3, "gunes_parlak": 16.0,
			"bulut": 0.48, "bulut_olcek": 0.7, "bulut_acik": Color("ffffff"), "bulut_golge": Color("9aa6bc"),
			"yildiz": 0.0, "ay": 0.0, "parlaklik": 1.0},
		"ortam": {"ambient": 0.5, "ton": "aces", "pozlama": 1.05, "beyaz": 6.0,
			"parlama": [0.45, 0.9, 0.06, 1.1], "sis": [0.0008, Color("c8d8e8"), 0.35, 0.15],
			"hacim_sis": [0.0015, Color("e8eef8"), 0.6, 110.0], "sdfgi": true, "ssao": 1.2, "ssr": true,
			"doygunluk": 1.06, "kontrast": 1.06, "parlaklik": 1.0},
		"ortak": {"toon": 0.0, "doygunluk": 1.05, "renk_carpan": Color("ffffff"), "sarma": 0.1,
			"kenar": 0.1, "kenar_renk": Color("ffffff"), "spek": 0.35},
		"malzeme": {
			"yaprak": {"gecirgenlik": 0.7, "gecirgen_renk": Color("d8ff8a"), "ton_a": Color("f0ffe0"), "ton_b": Color("d0e8c0")},
			"zemin": {"cimen_acik": Color("86b24e"), "cimen_koyu": Color("3d6a2e"), "kuru": Color("b8a860"), "kuru_miktar": 0.3},
			"cimen": {"dip": Color("2e5424"), "uc": Color("a8cc5a"), "gecirgenlik": 0.6, "gecirgen_renk": Color("d8ff8a")},
			"su": {"derin": Color("0c2e3a"), "sig": Color("2e8a8e"), "isima_guc": 0.0},
			"cini": {"isima_guc": 0.0},
			"nur": {"isima_guc": 2.0},
		},
		"kandil": {"enerji": 0.0, "renk": Color("ffcf80")},
		"parcacik": {"nur": 220, "nur_renk": Color(1.0, 0.97, 0.85), "yaprak": 90, "yaprak_renk": Color("ffd0dc")},
		"arayuz": {"metin": Color("ffffff"), "golge": Color(0, 0, 0, 0.45), "vurgu": Color("ffd060"),
			"cam": Color(0.08, 0.1, 0.14, 0.45), "cerceve": Color(1, 1, 1, 0.35), "perde": Color("0a1018"),
			"dugme_ic": Color("1c2a36"), "dugme_dis": Color("ffd060"), "latin": "Nunito", "susleme": false},
	},
}


static func al(ad: String) -> Dictionary:
	return PROFILLER.get(ad, PROFILLER["nur"])
