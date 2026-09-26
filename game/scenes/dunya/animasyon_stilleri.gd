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

const SIRA := ["nur", "sky", "pixar", "yagli_boya", "ghibli", "arcane"]

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
	# ------------------------------------------------------------------
	# Nur: ilk stil karşılaştırmasındaki Nur'un cennet mekânına uyarlaması. Altın ışık,
	# ışık hüzmeleri, sıcak pus, parlayan su. Güneş diski yok (K5): ışık üst derecelerin
	# ardındaki nurdan gelir gibi arkadan ve alçaktan vurur.
	"nur": {
		"ad": "Nur", "alt": "Ruhani ve sakin: altın ışık, ışık hüzmeleri, sıcak pus, parlayan su",
		"gunes": {"yukseklik": 22.0, "yon": 160.0, "renk": Color("ffd490"), "enerji": 1.9, "yumusak": 3.0,
			"golge_mesafe": 220.0, "golge_bulanik": 2.0},
		"gok": {"tepe": Color("5a86d0"), "orta": Color("a4c2e8"), "ufuk": Color("ffd298"), "alt": Color("e8c7a0"),
			"ufuk_kalin": 0.35, "nur_yon": Vector3(0.32, 0.37, -0.87), "nur_renk": Color("ffcf8a"), "nur_guc": 1.0,
			"nur_cekirdek": 1.6, "bulut": 0.42, "bulut_olcek": 0.8, "bulut_yukseklik": 0.3,
			"bulut_acik": Color("fff2dc"), "bulut_golge": Color("e0b8a4"), "bulut_kenar": Color("ffd9a0"),
			"kozmik": 0.0, "parlaklik": 1.0},
		# Parıltı kipi Ori ile aynı (screen): kip kesikli olduğundan farklı olsaydı geçişin
		# ortasında parıltı bir anda sıçrardı. Eski softlight 0.45 ile aynı görüntüyü screen
		# 0.15 verir (gökte fark yok, zeminde ortalama 2/255 ton).
		"ortam": {"ambient": 0.45, "ton": "aces", "pozlama": 0.95, "beyaz": 6.0,
			"parlama": [0.15, 0.9, 0.04, 1.3], "parlama_kip": "screen", "sis": [0.00032, Color("ffd9a6"), 0.25, 0.12],
			"hava_perspektif": 0.35, "hacim_sis": [0.00035, Color("ffe6c4"), 0.5, 220.0],
			"sdfgi": true, "sdfgi_hucre": 0.4, "ssao": 0.9, "ssr": true,
			"doygunluk": 1.12, "kontrast": 1.12, "parlaklik": 0.98},
		# toon_esik, toon_yumusak, golge_renk, cicek_*, su/puruz, tugla/isima_guc: shader
		# varsayılanları. Ori ile karışabilmek için açıkça yazılır (IsikKaristirici).
		"ortak": {"toon": 0.0, "toon_esik": 0.45, "toon_yumusak": 0.08, "golge_renk": Color(0.62, 0.66, 0.88),
			"doygunluk": 0.97, "renk_carpan": Color("fff4e4"), "sarma": 0.35,
			"kenar": 0.45, "kenar_renk": Color("ffd9a0"), "spek": 0.3},
		"malzeme": {
			"yaprak": {"gecirgenlik": 1.6, "gecirgen_renk": Color("ffd070"), "ton_a": Color("e4f0c8"), "ton_b": Color("fff0c0")},
			"zemin": {"cimen_acik": Color("b6c86a"), "cimen_koyu": Color("5b7f3c"), "kuru": Color("e4c77a"),
				"kuru_miktar": 0.4, "cicek_yogun": 0.45, "filiz_miktar": 0.3,
				"cicek_a": Color(1.0, 0.95, 0.85), "cicek_b": Color(1.0, 0.72, 0.8), "cicek_c": Color(1.0, 0.85, 0.35)},
			"cimen": {"dip": Color("476b2c"), "uc": Color("e2dc84"), "gecirgenlik": 1.4, "gecirgen_renk": Color("ffd070")},
			"su": {"derin": Color("20464e"), "sig": Color("5fa8a0"), "isima_guc": 0.1, "isima": Color("ffd48a"),
				"akis": Vector2(0.0, 0.5), "puruz": 0.03},
			"sut": {"derin": Color("efe2cc"), "sig": Color("fff8ea"), "isima_guc": 0.2, "isima": Color("ffe8c0"),
				"akis": Vector2(0.0, 0.35)},
			"bal": {"isima_guc": 0.3, "isima": Color("ffb040"), "akis": Vector2(0.0, 0.25), "puruz": 0.06},
			"serbet": {"isima_guc": 0.2, "isima": Color("ff6070"), "akis": Vector2(0.0, 0.4)},
			# Çağlayan suyu doygun camgöbeği-mavidir: altın pusla karışınca açık mavi kalır, su
			# olarak okunur (sıcak renkli su ışık sütunu, gri-yeşil su duman sütunu gibi okunuyordu).
			"selale": {"su_renk": Color("9fe6f5"), "derin_renk": Color("3ba3d0"), "isima_guc": 0.5,
				"gecirgenlik": 0.35, "gecirgen_renk": Color("ffdca0")},
			"tugla": {"tugla_a": Color("f0c878"), "tugla_b": Color("ece8e2"), "isima_guc": 0.0},
			"cini": {"isima_guc": 0.05},
			"cicek": {"isima_guc": 0.08},
			"inci": {"isima": Color("fff0dc"), "isima_guc": 0.18},
			"nur": {"isima_guc": 4.0},
			"tavan": {"guc": 1.0, "bulut": 0.35},
			"kesit_yuzu": {"yuz_ton": Color("ffffff"), "yuz_isik": 1.0, "damar_renk": Color("ffeab0")},
			"kesit_serit": {"isima": 0.35, "tas_renk": Color("fbf0dc"), "cicek_renk": Color("ff9fb4")},
		},
		"bulut_renk": [Color(1.3, 1.16, 0.98), Color(0.98, 0.84, 0.8)],
		"parcacik": {"nur": 700, "nur_renk": Color(1.0, 0.9, 0.6), "sis_renk": Color(1.0, 0.95, 0.85, 0.45),
			"selale_sis": Color(1.3, 1.24, 1.12, 0.35)},
		# Kesit (K18): katların pusu (her katın dışarıdan görünen göğü), alttaki bulut denizi
		"kesit_pus": {"ufuk": Color("ffd9a2"), "gok": Color("9ec2ec"), "nur": Color("fff2d8")},
		"bulut_denizi": {"acik": Color("fff4ea"), "golge": Color("d8b0b4"), "isima": Color("ffd8b4"), "isima_guc": 0.25},
		"kesit": {
			# Işık içerideki gibi arkadan gelir (aynı mekân, aynı ışık; yakınlaşmada gölge dönmez).
			# Gök: her şeyi kuşatan nur, mavi yok (Firdevs'in üstü; Arş tasvir edilmez).
			"gok": {"kozmik": 1.0, "tepe": Color("fff3dc"), "ufuk": Color("ffe2b0"), "nur_yon": Vector3(0.0, 0.93, -0.36),
				"nur_guc": 1.3, "nur_cekirdek": 1.8, "bulutsu_a": Color("ffe8cc"), "bulutsu_b": Color("f4ecf8"),
				"parilti": 0.8},
			# Kontrast, parlaklık, doygunluk: kullanıcının beğendiği taslak (taslak_nur_kesit.png)
			# profilin son ayarından önce çekilmişti; bu değerler o açık, pastel görüntüyü verir.
			"ortam": {"sis": [0.000002, Color("ffe8d0"), 0.2, 0.0], "hava_perspektif": 0.0, "sdfgi": false,
				"ssr": false, "ssao": 0.0, "ambient": 0.55, "hacim_sis": [0.0, Color.WHITE, 0.0, 0.0],
				"pozlama": 0.9, "kontrast": 1.12, "parlaklik": 1.0, "doygunluk": 1.3},
		},
	},
	# ------------------------------------------------------------------
	# Sky / Journey / Ori: ışıklı, sade, rüya gibi. Derin gök mavisi ve turkuaz; güçlü
	# parıltı; mavi-yeşil pus uzakları katman katman silüete çevirir; su, çiçek ve
	# nur kendi ışığıyla parlar; gölgeler mavidir.
	"sky": {
		"ad": "Sky / Ori", "alt": "Işıklı ve rüya gibi: turkuaz pus, katman katman silüetler, kendi ışığıyla parlayan su ve çiçekler",
		"gunes": {"yukseklik": 30.0, "yon": 205.0, "renk": Color("fff2dc"), "enerji": 1.3, "yumusak": 4.0,
			"golge_mesafe": 200.0, "golge_bulanik": 3.0},
		"gok": {"tepe": Color("0e3a8c"), "orta": Color("2f86d0"), "ufuk": Color("c4f4ff"), "alt": Color("a8e0f0"),
			"ufuk_kalin": 0.3, "nur_yon": Vector3(-0.05, 0.3, -1.0), "nur_renk": Color("fff0c8"), "nur_guc": 0.9,
			"nur_cekirdek": 1.6, "bulut": 0.5, "bulut_olcek": 0.6, "bulut_yukseklik": 0.4,
			"bulut_acik": Color("ffffff"), "bulut_golge": Color("7fa6e0"), "bulut_kenar": Color("fff0c0"),
			"kozmik": 0.0, "parlaklik": 1.0},
		"ortam": {"ambient": 0.5, "ton": "aces", "pozlama": 0.92, "beyaz": 5.0,
			"parlama": [0.55, 1.0, 0.06, 1.15], "parlama_kip": "screen", "sis": [0.00036, Color("5cc0e0"), 0.15, 0.12],
			"hava_perspektif": 0.75, "hacim_sis": [0.0003, Color("b8ecff"), 0.4, 200.0],
			"sdfgi": true, "sdfgi_hucre": 0.4, "ssao": 0.6, "ssr": true,
			"doygunluk": 1.25, "kontrast": 1.05, "parlaklik": 1.0},
		"ortak": {"toon": 0.25, "toon_esik": 0.45, "toon_yumusak": 0.2, "golge_renk": Color("4a6ad8"),
			"doygunluk": 1.15, "renk_carpan": Color("f0fbff"), "sarma": 0.5, "kenar": 0.9, "kenar_renk": Color("c8fff4"),
			"spek": 0.25},
		"malzeme": {
			"yaprak": {"gecirgenlik": 1.4, "gecirgen_renk": Color("c8ffb0"), "ton_a": Color("d8ffe0"), "ton_b": Color("e8fff0")},
			"zemin": {"cimen_acik": Color("7fdc8a"), "cimen_koyu": Color("1f7a5a"), "kuru": Color("c8f0a0"),
				"kuru_miktar": 0.2, "cicek_yogun": 0.6, "filiz_miktar": 0.4,
				"cicek_a": Color("f4fffe"), "cicek_b": Color("ffb8e8"), "cicek_c": Color("fff0a0")},
			"cimen": {"dip": Color("1a6a50"), "uc": Color("a8f0b0"), "gecirgenlik": 1.2, "gecirgen_renk": Color("d0ffc0")},
			"su": {"derin": Color("0a4a8a"), "sig": Color("2fb8d8"), "isima_guc": 0.14, "isima": Color("7ffff0"),
				"akis": Vector2(0.0, 0.5), "puruz": 0.16},
			"sut": {"derin": Color("e0f4f8"), "sig": Color("ffffff"), "isima_guc": 0.35, "isima": Color("f0ffff"),
				"akis": Vector2(0.0, 0.35)},
			"bal": {"isima_guc": 0.5, "isima": Color("ffc050"), "akis": Vector2(0.0, 0.25), "puruz": 0.06},
			"serbet": {"isima_guc": 0.45, "isima": Color("ff6090"), "akis": Vector2(0.0, 0.4)},
			"selale": {"su_renk": Color("a8f0ff"), "derin_renk": Color("1c9ccf"), "isima_guc": 0.9,
				"gecirgenlik": 0.35, "gecirgen_renk": Color("d8fff8")},
			"tugla": {"tugla_a": Color("f4d890"), "tugla_b": Color("eaf6ff"), "isima_guc": 0.05},
			"cini": {"isima_guc": 0.25},
			"cicek": {"isima_guc": 0.6},
			"inci": {"isima": Color("e8ffff"), "isima_guc": 0.35},
			"nur": {"isima_guc": 6.0},
			"tavan": {"guc": 1.05, "bulut": 0.3},
			"kesit_yuzu": {"yuz_ton": Color("f4fbff"), "yuz_isik": 1.05, "damar_renk": Color("e8fff8")},
			"kesit_serit": {"isima": 0.5, "tas_renk": Color("f4fcff"), "cicek_renk": Color("ffb4e0")},
		},
		"bulut_renk": [Color(1.35, 1.42, 1.5), Color(0.7, 0.86, 1.25)],
		"parcacik": {"nur": 1200, "nur_renk": Color(0.85, 1.0, 0.95), "sis_renk": Color(0.85, 0.97, 1.0, 0.4),
			"selale_sis": Color(1.15, 1.32, 1.42, 0.35)},
		"kesit_pus": {"ufuk": Color("c8f2ff"), "gok": Color("a8d6f2"), "nur": Color("effffb")},
		"bulut_denizi": {"acik": Color("ffffff"), "golge": Color("b4cff0"), "isima": Color("c4fff0"), "isima_guc": 0.35},
		"kesit": {
			"gok": {"kozmik": 1.0, "tepe": Color("f2fffd"), "ufuk": Color("d4fff4"), "nur_yon": Vector3(0.0, 0.93, -0.36),
				"nur_guc": 1.4, "nur_cekirdek": 2.0, "bulutsu_a": Color("e6fff8"), "bulutsu_b": Color("dcecff"),
				"parilti": 1.4},
			"ortam": {"sis": [0.000002, Color("a0e8ff"), 0.2, 0.0], "hava_perspektif": 0.0, "sdfgi": false,
				"ssr": false, "ssao": 0.0, "ambient": 0.5, "hacim_sis": [0.0, Color.WHITE, 0.0, 0.0],
				"parlama": [0.5, 1.0, 0.06, 1.2], "pozlama": 0.88, "kontrast": 1.12, "doygunluk": 1.3},
		},
	},
}


## Profili döndürür; kesit (dış görünüm) istenirse "kesit" alanı üzerine yazılır.
## Henüz tanımlanmamış stiller Pixar'a düşer.
static func al(ad: String, kesit := false) -> Dictionary:
	var p: Dictionary = PROFILLER.get(ad, PROFILLER["pixar"]).duplicate(true)
	if kesit:
		# Kesitte katların göğü (kat_gogu) içeriden görülen göğün aynısıdır: kesitin
		# üzerine yazdığı ortam göğünden önce saklanır (K18).
		p["kat_gok"] = (p["gok"] as Dictionary).duplicate(true)
	if kesit and p.has("kesit"):
		for alan in p["kesit"]:
			for anahtar in p["kesit"][alan]:
				p[alan][anahtar] = p["kesit"][alan][anahtar]
	return p
