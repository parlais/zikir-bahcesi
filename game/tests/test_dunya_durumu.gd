extends TestCase
## Dünyanın hâli (K20): boş başlangıç, nimetlerin gelişi, hiçbir değerin düşmemesi.

var c := Content.load_default()


## Tek olan asset'ler (dünya verisinde de tek yuvaları vardır).
const TEKLER := ["tuba", "bahce_kapisi"]


## İçeriğe göre sentetik yuvalar: her MVP 3D ve 3D-A asset'ine üç yuva (dosyadan bağımsız).
func _yuvalar(adet := 3) -> DunyaYuvalari:
	var liste: Array = []
	var sira := 0
	var ids := c.assets.keys()
	ids.sort()
	for id in ids:
		var a: Dictionary = c.assets[id]
		if a["oncelik"] != "MVP" or not a["tip"] in ["3D", "3D-A"]:
			continue
		for i in (1 if id in TEKLER else adet):
			liste.append([float(sira), 0.0, 0.0, 0.0, 1.0, id, sira])
			sira += 1
	return DunyaYuvalari.sozlukten({"arsa": liste})


func _yeni() -> ZikirEngine:
	return ZikirEngine.new(c, GardenState.new())


func _hal(e: ZikirEngine, y: DunyaYuvalari = null) -> Dictionary:
	return DunyaDurumu.hesapla(c, e.state, e, y if y != null else _yuvalar())


## eski'den yeni'ye hiçbir değer düşmedi mi? Düşenlerin listesi (boşsa düşmedi).
func _dusenler(eski: Dictionary, yeni: Dictionary) -> Array:
	var out: Array = []
	if yeni["tuba"] < eski["tuba"]:
		out.append("tuba %d -> %d" % [eski["tuba"], yeni["tuba"]])
	for k in ["kapi", "cakil", "merdiven"]:
		if eski[k] and not yeni[k]:
			out.append(k)
	for k in ["irmak", "selale"]:
		for i in 4:
			if yeni[k][i] < eski[k][i]:
				out.append("%s[%d]" % [k, i])
	for k in eski["yansima"]:
		if yeni["yansima"][k] < eski["yansima"][k] - 1e-9:
			out.append("yansima.%s %f -> %f" % [k, eski["yansima"][k], yeni["yansima"][k]])
	for id in eski["canli"]:
		if int(yeni["canli"].get(id, 0)) < eski["canli"][id]:
			out.append("canli." + id)
	for key in eski["etki"]:
		if not yeni["etki"].has(key):
			out.append("etki." + key)
	for id in eski["yuva"]:
		var a: Dictionary = c.assets[id]
		var y1: Array = eski["yuva"][id]
		var y2: Array = yeni["yuva"].get(id, [])
		for i in y1.size():
			var m2: String = y2[i] if i < y2.size() else ""
			if DunyaDurumu.asama_no(a, m2) < DunyaDurumu.asama_no(a, y1[i]):
				out.append("yuva.%s[%d] %s -> %s" % [id, i, y1[i], m2])
	return out


func test_bos_dunyada_nimet_yok() -> void:
	var b := DunyaDurumu.bos()
	esit(b["tuba"], 0, "Tûbâ süzülen çekirdek")
	esit(b["vitrin"], false, "vitrin değil")
	for k in ["kapi", "cakil", "merdiven"]:
		esit(b[k], false, k)
	esit(b["yuva"].size(), 0, "yuva boş")
	for k in DunyaDurumu.YANSIMALAR:
		esit(b["yansima"][k], 0.0, "yansıma " + k)
	esit(b["irmak"], [0, 0, 0, 0], "ırmak yok")
	esit(b["selale"], [0, 0, 0, 0], "çağlayan yok")
	esit(b["canli"].size(), 0, "canlı yok")
	esit(b["etki"].size(), 0, "etki yok")
	var e := _yeni()
	var h := _hal(e)
	esit(DunyaDurumu.fark(b, h).size(), 0, "hiç zikir söylenmemiş durum boş dünyadır")
	esit(DunyaDurumu.bos(), DunyaDurumu.bos(), "boş hâl her seferinde aynı")
	b["irmak"][0] = 1
	esit(DunyaDurumu.bos()["irmak"], [0, 0, 0, 0], "boş hâlin kopyası paylaşılmaz")


func test_bismillah_kapi_ve_cakil() -> void:
	var e := _yeni()
	e.say("bismillah")
	var h := _hal(e)
	dogru(not h["kapi"], "oturum açılışı olmayan Bismillah kapıyı getirmez")
	e.say("bismillah", 1, {"oturum_acilisi": true})
	h = _hal(e)
	dogru(h["kapi"] and h["cakil"], "ilk Bismillah kapı ve çakıl sınırını getirir")
	esit(h["yuva"].get("bahce_kapisi"), ["ZB_yapi_bahce_kapisi"], "kapı yuvasında")
	e.say("bismillah", 1, {"oturum_acilisi": true})
	esit(_hal(e)["yuva"]["bahce_kapisi"].size(), 1, "tek kapı")


func test_tuba_asamalari() -> void:
	var e := _yeni()
	esit(_hal(e)["tuba"], 0, "0 tevhid: süzülen çekirdek")
	dogru(not _hal(e)["yuva"].has("tuba"), "çekirdek yuvada değil (çerçeve)")
	e.say("tevhid")
	var h := _hal(e)
	esit(h["tuba"], 1, "ilk tevhid: a1")
	esit(h["yuva"]["tuba"], ["ZB_agac_tuba_a1"], "Tûbâ yuvası a1")
	e.say("tevhid", 32)
	esit(_hal(e)["tuba"], 2, "33 tevhid")
	e.say("tevhid", 967)
	h = _hal(e)
	esit(h["tuba"], 4, "1000 tevhid: olgun")
	esit(h["yansima"]["ufuk"], 1.0, "Tûbâ olgunlaşınca ufuk açılır")
	e.say("tevhid", 9000)
	h = _hal(e)
	esit(h["tuba"], 5, "10000 tevhid: ulu")
	esit(h["yuva"]["tuba"], ["ZB_agac_tuba_a5"], "ulu Tûbâ")
	esit(h["yansima"]["cevre"], 0.0, "Tûbâ on misli sayısına girmez")


func test_ufuk_tuba_olgunlasmadan_kapali() -> void:
	var e := _yeni()
	e.say("tevhid", 999)
	esit(_hal(e)["yansima"]["ufuk"], 0.0, "999 tevhidde ufuk kapalı")


func test_on_misli_yanki() -> void:
	var e := _yeni()
	e.say("subhanallahil_azim", 300)
	var h := _hal(e)
	esit(e.state.adet("hurma_agaci"), 3, "üç olgun hurma")
	dogru(is_equal_approx(h["yansima"]["cevre"], 30.0 / 286.0), "3 ağaç: çevre 30/286, gelen %f" % h["yansima"]["cevre"])
	esit(h["yansima"]["ova"], 0.0, "ova henüz kapalı")
	# 27 servi daha: 30 ağaç -> 300 ağaç; çevre dolar, ova 14/1496
	e.say("esma:vahid", 19 * 27)
	h = _hal(e)
	esit(h["yansima"]["cevre"], 1.0, "çevre dolu")
	dogru(is_equal_approx(h["yansima"]["ova"], 14.0 / 1496.0), "ova 14/1496, gelen %f" % h["yansima"]["ova"])
	esit(DunyaDurumu.ON_MISLI, 10, "on misli")
	esit(DunyaDurumu.KORU_SAYISI, 286, "koru sayısı")
	esit(DunyaDurumu.UZAK_AGAC_SAYISI, 1496, "uzak ağaç sayısı")


func test_olgun_ve_buyuyen_yuvalar() -> void:
	var e := _yeni()
	e.say("subhanallahil_azim", 133)
	var h := _hal(e)
	esit(h["yuva"]["hurma_agaci"], ["ZB_agac_hurma_a4", "ZB_agac_hurma_a3"], "bir olgun, biri fidan")
	e.say("subhanallahil_azim", 300)
	esit(_hal(e)["yuva"]["hurma_agaci"], ["ZB_agac_hurma_a4", "ZB_agac_hurma_a4", "ZB_agac_hurma_a4"],
		"yuvalar dolunca büyüyen örnek görünmez")


func test_irmaklar_sozlesmedeki_kimliklerle() -> void:
	esit(DunyaDurumu.IRMAKLAR, ["irmak_su", "irmak_sut", "irmak_bal", "irmak_serbet"], "sözleşme")
	var e := _yeni()
	e.state.tamamlanan["irmak_sut"] = 1
	var h := _hal(e)
	esit(h["irmak"], [0, 1, 0, 0], "tamamlanan süt ırmağı")
	e.state.envanter["irmak_bal"] = 1
	h = _hal(e)
	esit(h["irmak"], [0, 1, 1, 0], "envanterdeki bal ırmağı")
	esit(h["selale"], h["irmak"], "çağlayan ırmağıyla gelir")
	e.state.envanter["irmak_bal"] = 0
	esit(_hal(e)["irmak"], [0, 1, 0, 0], "ham hesap sözleşmeye uyar")


func test_kir_cicekleri_ve_cimen() -> void:
	esit(DunyaDurumu.kir_cicegi(2, false), 0.0, "2 çiçekte yok")
	dogru(is_equal_approx(DunyaDurumu.kir_cicegi(3, false), 1.0 / 3.0), "3 çiçekte arsa çevresi")
	dogru(is_equal_approx(DunyaDurumu.kir_cicegi(12, false), 2.0 / 3.0), "12 çiçekte ova")
	dogru(is_equal_approx(DunyaDurumu.kir_cicegi(50, false), 2.0 / 3.0), "Bahar patlamasına kadar ova")
	esit(DunyaDurumu.kir_cicegi(0, true), 1.0, "Bahar patlaması bütün ovayı açar")
	var e := _yeni()
	e.say("esma:allah", 66 * 3)
	var h := _hal(e)
	dogru(is_equal_approx(h["yansima"]["cicek"], 1.0 / 3.0), "üç lale: arsa çevresi")
	esit(h["yansima"]["cimen"], 0.0, "çimen önce seyrek")
	e.say("esma:basit", 72)
	esit(_hal(e)["yansima"]["cimen"], 1.0, "Çimen halısı açılınca gür")
	e.say("esma:bais", 573)
	esit(_hal(e)["yansima"]["cicek"], 1.0, "Bahar patlaması")


func test_tarifte_harcanan_malzeme_dunyada_kalir() -> void:
	var e := _yeni()
	var r := RecipeSystem.new(c, e.state)
	e.say("esma:vacid", 14)
	e.say("istigfar", 100)
	var once := _hal(e)
	esit(once["yuva"].get("sedef"), ["ZB_obje_sedef"], "sedef yuvasında")
	dogru(r.yapilabilir("inci_yagmuru"), "inci yağmuru yapılabilir")
	r.yap("inci_yagmuru")
	esit(e.state.adet("sedef"), 0, "sedef envanterden harcandı")
	var sonra := _hal(e)
	esit(sonra["yuva"].get("sedef"), ["ZB_obje_sedef"], "sedef dünyada kalır")
	esit(sonra["yuva"].get("inci"), ["ZB_obje_inci"], "inci geldi")
	esit(_dusenler(once, sonra), [], "hiçbir değer düşmedi")


func test_canli_ve_etki() -> void:
	var e := _yeni()
	e.say("esma:latif", 129)
	var h := _hal(e)
	esit(h["canli"].get("kelebek"), 1, "kozadan kelebek")
	e.state.envanter["zeytinyagi_testisi"] = 1
	e.state.envanter["kandil"] = 1
	RecipeSystem.new(c, e.state).yap("kandil_tam_parlaklik")
	esit(_hal(e)["etki"], ["etki:kandil_tam_parlaklik"], "tarif etkisi")


func test_model_varyantlari() -> void:
	var sur: Dictionary = c.assets["sur_parcalari"]
	esit(DunyaDurumu.model_adi(sur, 0, 1), "ZB_yapi_sur_parcalari_duz", "ilk yuva düz")
	esit(DunyaDurumu.model_adi(sur, 1, 1), "ZB_yapi_sur_parcalari_kose", "ikinci yuva köşe")
	var tuba: Dictionary = c.assets["tuba"]
	esit(DunyaDurumu.model_adi(tuba, 0, 3), "ZB_agac_tuba_a3", "Tûbâ a3")
	esit(DunyaDurumu.asama_no(tuba, "ZB_agac_tuba_a5"), 5, "aşama no")
	esit(DunyaDurumu.asama_no(tuba, ""), 0, "boş yuva")


func test_monotonluk_1000_adim() -> void:
	var e := _yeni()
	var r := RecipeSystem.new(c, e.state)
	var y := _yuvalar(4)
	var rng := RandomNumberGenerator.new()
	rng.seed = 20260926
	var sozler := ["tevhid", "subhanallahil_azim", "allahu_ekber", "esma:vahid", "elhamdulillah", "salavat",
		"esma:allah", "esma:muhyi", "bismillah", "esma:basit", "istigfar", "esma:latif", "lahavle", "esma:vacid",
		"subhanallah", "esma:nur", "esma:bais", "tin", "ihlas", "esma:hayy", "esma:rezzak", "esma:vehhab",
		"tehlil_kebir", "masaallah", "esma:evvel", "esma:kuddus", "tesbihat", "rabbi_zidni_ilma", "esma:hadi"]
	var tarifler := c.tarifler.keys()
	var eski := DunyaDurumu.ham(c, e.state, e, y)
	var ilk := eski
	var tarif_sayisi := 0
	for adim in 1000:
		if rng.randf() < 0.2:
			var t: String = tarifler[rng.randi_range(0, tarifler.size() - 1)]
			if not r.yap(t).is_empty():
				tarif_sayisi += 1
		else:
			var soz: String = sozler[rng.randi_range(0, sozler.size() - 1)]
			var baglam := {}
			if soz == "bismillah" and rng.randf() < 0.3:
				baglam["oturum_acilisi"] = true
			if soz == "salavat" and rng.randf() < 0.3:
				baglam["cuma"] = true
			e.say(soz, rng.randi_range(1, 120), baglam)
		var yeni := DunyaDurumu.ham(c, e.state, e, y)
		var dusen := _dusenler(eski, yeni)
		if not dusen.is_empty():
			dogru(false, "adım %d: düştü %s" % [adim, dusen])
			return
		eski = yeni
	dogru(tarif_sayisi > 0, "en az bir tarif yapıldı")
	dogru(DunyaDurumu.fark(ilk, eski).size() > 20, "dünya doldu")
	dogru(eski["tuba"] >= 3, "Tûbâ büyüdü")


func test_ebced_modu_degisince_dusmez() -> void:
	var e := _yeni()
	var y := _yuvalar()
	e.say("tevhid", 150)
	e.say("esma:vahid", 10)
	var h := DunyaDurumu.hesapla(c, e.state, e, y)
	esit(h["yuva"]["servi"], ["ZB_agac_servi_a3"], "ebced: 10 Vâhid servi fidanı")
	DunyaDurumu.goruldu(e.state, h)
	e.state.ebced_modu = false
	var ham := DunyaDurumu.ham(c, e.state, e, y)
	esit(ham["yuva"]["servi"], ["ZB_agac_servi_a2"], "serbest modda eşik yüksek (ham hesap düşer)")
	var sonra := DunyaDurumu.hesapla(c, e.state, e, y)
	esit(sonra["yuva"]["servi"], ["ZB_agac_servi_a3"], "görülen fidan küçülmez")
	esit(sonra["tuba"], 3, "Tûbâ düşmez")
	esit(_dusenler(h, sonra), [], "hiçbir değer düşmedi")
	# Görülenden daha büyük Tûbâ (ör. eski sürüm) korunur
	e.state.dunya_gorulen["tuba"] = 4
	esit(DunyaDurumu.hesapla(c, e.state, e, y)["tuba"], 4, "en yüksek görülen korunur")
	e.state.ebced_modu = true
	e.say("esma:vahid", 9)
	h = DunyaDurumu.hesapla(c, e.state, e, y)
	esit(h["yuva"]["servi"], ["ZB_agac_servi_a4"], "olgunlaşınca yerini olgun servi alır")


## Yuva verisi okunamazsa (DunyaYuvalari.yukle boş döner) hatırlanan yuvalar silinmez.
func test_bos_yuvalar_gorulen_yuvalari_silmez() -> void:
	var e := _yeni()
	var y := _yuvalar()
	e.say("tevhid", 150)
	e.say("esma:vahid", 10)
	var h := DunyaDurumu.hesapla(c, e.state, e, y)
	DunyaDurumu.goruldu(e.state, h)
	var bos := DunyaYuvalari.sozlukten({})
	dogru(bos.bos_mu(), "boş yuvalar")
	dogru(not y.bos_mu(), "dolu yuvalar")
	var sonra := DunyaDurumu.hesapla(c, e.state, e, bos)
	esit(sonra["yuva"], h["yuva"], "görülen yuvalar korunur")
	esit(_dusenler(h, sonra), [], "hiçbir değer düşmedi")
	DunyaDurumu.goruldu(e.state, sonra)
	esit(e.state.dunya_gorulen["yuva"], h["yuva"], "kayıttaki yuvalar boşalmaz")
	# Dolu yuvalarda artık olmayan yuvalar yine atılır
	var tek := DunyaYuvalari.sozlukten({"arsa": [[0.0, 0.0, 0.0, 0.0, 1.0, "tuba", 0]]})
	var kirpik := DunyaDurumu.en_yuksek(c, h, DunyaDurumu.bos(), tek)
	esit(kirpik["yuva"].keys(), ["tuba"], "yuvası kalmayan asset atılır")


func test_vitrin_her_sey_acik() -> void:
	var v := DunyaDurumu.vitrin()
	esit(v["vitrin"], true, "vitrin alanı")
	esit(v["tuba"], 5, "ulu Tûbâ")
	for k in ["kapi", "cakil", "merdiven"]:
		esit(v[k], true, k)
	for k in DunyaDurumu.YANSIMALAR:
		esit(v["yansima"][k], 1.0, "yansıma " + k)
	esit(v["irmak"], [1, 1, 1, 1], "dört ırmak")
	esit(v["selale"], [1, 1, 1, 1], "dört çağlayan")
	var y := _yuvalar()
	var dolu := DunyaDurumu.vitrin(c, y)
	for id in y.assetler():
		esit(dolu["yuva"][id].size(), y.sayi(id), "vitrinde bütün yuvalar dolu: " + id)
	esit(dolu["yuva"]["tuba"][0], "ZB_agac_tuba_a5", "olgun modeller")
	dogru(dolu["canli"].has("guvercin"), "canlılar")
	dogru(dolu["etki"].has("etki:kandil_tam_parlaklik"), "etkiler")
	# Vitrin görülen hâl olarak kaydedilmez
	var s := GardenState.new()
	DunyaDurumu.goruldu(s, v)
	esit(s.dunya_gorulen.size(), 0, "vitrin kayda geçmez")


func test_fark() -> void:
	var e := _yeni()
	var once := _hal(e)
	e.say("bismillah", 1, {"oturum_acilisi": true})
	e.say("tevhid")
	var f := DunyaDurumu.fark(once, _hal(e))
	dogru(olay_var(f, "kapi", {"eski": false, "yeni": true}), "kapı açıldı")
	dogru(olay_var(f, "cakil"), "çakıl geldi")
	dogru(olay_var(f, "tuba", {"eski": 0, "yeni": 1}), "Tûbâ a1")
	dogru(olay_var(f, "yuva", {"id": "bahce_kapisi", "yuva_no": 0, "eski": "", "yeni": "ZB_yapi_bahce_kapisi"}), "kapı yuvası")
	dogru(olay_var(f, "yuva", {"id": "tuba", "yeni": "ZB_agac_tuba_a1"}), "Tûbâ yuvası")
	esit(f.size(), 5, "yalnız değişenler")
	esit(DunyaDurumu.fark(_hal(e), _hal(e)), [], "aynı hâlde fark yok")


func test_kayit_dunya_gorulen() -> void:
	var e := _yeni()
	e.say("tevhid", 40)
	e.say("subhanallahil_azim", 120)
	var h := _hal(e)
	DunyaDurumu.goruldu(e.state, h)
	var d = JSON.parse_string(JSON.stringify(e.state.to_dict()))
	var s := GardenState.from_dict(d)
	esit(s.surum, 2, "sürüm 2")
	esit(DunyaDurumu.fark(s.dunya_gorulen, h), [], "görülen hâl geri gelir")
	esit(s.dunya_gorulen["yuva"], h["yuva"], "yuvalar")
	esit(typeof(s.dunya_gorulen["tuba"]), TYPE_INT, "Tûbâ tam sayı")
	esit(typeof(s.dunya_gorulen["irmak"][0]), TYPE_INT, "ırmak tam sayı")
	esit(typeof(s.dunya_gorulen["yansima"]["cevre"]), TYPE_FLOAT, "yansıma ondalık")
	# Sürüm 1 kaydı: dunya_gorulen ve kazanilan yok
	var eski := {"surum": 1, "sayaclar": {"tevhid": 40.0}, "tamamlanan": {"lale": 2.0},
		"envanter": {"lale": 2.0, "inci": 1.0}}
	var s1 := GardenState.from_dict(eski)
	esit(s1.dunya_gorulen, {}, "eski kayıtta görülen hâl boş")
	esit(s1.kazanilan.get("inci"), 1, "kazanılan envanterden tahmin edilir")
	esit(s1.kazanilan.get("lale"), 2, "kazanılan tamamlanandan tahmin edilir")
