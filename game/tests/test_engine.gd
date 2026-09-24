extends TestCase

var c := Content.load_default()


func _yeni() -> ZikirEngine:
	return ZikirEngine.new(c, GardenState.new())


func test_agac_asamalari_1_10_33_100() -> void:
	var e := _yeni()
	var o := e.say("subhanallahil_azim")
	dogru(olay_var(o, "asama", {"asset": "hurma_agaci", "asama": 1}), "1'de tohum")
	e.say("subhanallahil_azim", 8)
	o = e.say("subhanallahil_azim")
	dogru(olay_var(o, "asama", {"asset": "hurma_agaci", "asama": 2}), "10'da filiz")
	e.say("subhanallahil_azim", 22)
	o = e.say("subhanallahil_azim")
	dogru(olay_var(o, "asama", {"asset": "hurma_agaci", "asama": 3}), "33'te fidan")
	o = e.say("subhanallahil_azim", 66)
	dogru(not olay_var(o, "tamamlandi", {"asset": "hurma_agaci"}), "99'da henüz olgun değil")
	o = e.say("subhanallahil_azim")
	dogru(olay_var(o, "tamamlandi", {"asset": "hurma_agaci"}), "100'de olgun")
	esit(e.state.adet("hurma_agaci"), 1, "bir olgun hurma")
	esit(e.ilerleme("hurma_agaci")["asama"], 0, "yeni fidan henüz dikilmedi")
	o = e.say("subhanallahil_azim")
	dogru(olay_var(o, "asama", {"asset": "hurma_agaci", "asama": 1}), "101'de ikinci tohum")


func test_esma_ebced_modu() -> void:
	var e := _yeni()
	var o := e.say("esma:allah", 65)
	dogru(not olay_var(o, "tamamlandi", {"asset": "lale"}), "65'te lale yok")
	o = e.say("esma:allah")
	dogru(olay_var(o, "tamamlandi", {"asset": "lale"}), "66'da lale açar")
	dogru(olay_var(o, "esma_tamam", {"esma": "allah"}), "esma tamam olayı")


func test_serbest_mod_33() -> void:
	var e := _yeni()
	e.state.ebced_modu = false
	var o := e.say("esma:allah", 33)
	dogru(olay_var(o, "tamamlandi", {"asset": "lale"}), "serbest modda 33'te lale")


func test_ikinci_item_sirasi() -> void:
	var e := _yeni()
	var o := e.say("esma:nur", 256)
	dogru(olay_var(o, "tamamlandi", {"asset": "kandil"}), "ilk 256: kandil")
	dogru(olay_var(o, "tamamlandi", {"asset": "kandil_isigi"}), "ilk 256: kandil ışığı")
	dogru(not olay_var(o, "tamamlandi", {"asset": "fanus"}), "ilk 256'da fanus yok")
	o = e.say("esma:nur", 256)
	dogru(olay_var(o, "tamamlandi", {"asset": "fanus"}), "ikinci 256: fanus")
	dogru(not olay_var(o, "tamamlandi", {"asset": "kandil"}), "ikinci 256'da kandil yok")
	o = e.say("esma:nur", 256)
	dogru(olay_var(o, "tamamlandi", {"asset": "kandil"}), "üçüncü 256: yine kandil")


func test_her_33_subhanallahta_kus() -> void:
	var e := _yeni()
	e.say("subhanallah", 32)
	var o := e.say("subhanallah")
	var kus := olay_var(o, "tamamlandi", {"asset": "guvercin"}) or olay_var(o, "tamamlandi", {"asset": "serce"})
	dogru(kus, "33'te bir kuş gelir")
	esit(e.state.adet("guvercin") + e.state.adet("serce"), 1, "tek kuş")


func test_ardisik_salavat() -> void:
	var e := _yeni()
	e.say("salavat", 9)
	e.say("tevhid")
	var o := e.say("salavat", 9)
	dogru(not olay_var(o, "ardisik"), "araya başka söz girince sayaç sıfırlanır")
	o = e.say("salavat")
	dogru(olay_var(o, "ardisik", {"asset": "gul_kokusu_parcaciklari"}), "10 üst üste salavat")


func test_cuma_salavati() -> void:
	var e := _yeni()
	e.say("salavat", 5)
	esit(e.ilerleme("beyaz_gul")["asama"], 0, "cuma dışı salavat beyaz gülü büyütmez")
	e.say("salavat", 1, {"cuma": true})
	esit(e.ilerleme("beyaz_gul")["asama"], 1, "cuma salavatı beyaz gülü büyütür")
	esit(e.ilerleme("kirmizi_gul")["sayi"], 6, "kırmızı gül her salavatla büyür")


func test_tevhid_hava_ve_tuba() -> void:
	var e := _yeni()
	var once: float = e.state.kaynaklar["hava"]
	var o := e.say("tevhid", 33)
	dogru(e.state.kaynaklar["hava"] > once, "tevhid havayı artırır")
	dogru(olay_var(o, "asama", {"asset": "tuba", "asama": 2}), "Tûbâ 33'te ikinci aşama")
	e.say("tevhid", 1000)
	esit(e.state.kaynaklar["hava"], GardenState.KAYNAK_TAVAN, "hava tavanı aşmaz")


func test_define_sandigi_turev() -> void:
	var e := _yeni()
	var o := e.say("lahavle", 33)
	dogru(olay_var(o, "tamamlandi", {"asset": "define_sandigi"}), "33 la havle: define sandığı")
	esit(e.state.adet("inci") + e.state.adet("mercan"), 1, "sandıktan inci veya mercan çıkar")


func test_ipek_kozasi_kelebek() -> void:
	var e := _yeni()
	var o := e.say("esma:latif", 129)
	dogru(olay_var(o, "tamamlandi", {"asset": "ipek_kozasi"}), "koza")
	dogru(olay_var(o, "tamamlandi", {"asset": "kelebek"}), "kozadan kelebek")


func test_mod_degisimi_geri_almaz() -> void:
	var e := _yeni()
	e.state.ebced_modu = false
	e.say("esma:allah", 40)
	esit(e.state.adet("lale"), 1, "serbest modda bir lale")
	e.state.ebced_modu = true
	e.say("esma:allah")
	esit(e.state.adet("lale"), 1, "ebced moduna geçince lale geri alınmaz")


func test_celali_kart() -> void:
	var e := _yeni()
	var o := e.say("esma:kahhar", 306)
	dogru(olay_var(o, "kart", {"esma": "kahhar"}), "Kahhâr kartı açılır")
	o = e.say("esma:kahhar", 306)
	dogru(not olay_var(o, "kart"), "kart bir kez açılır")


func test_solma_tabanin_altina_inmez() -> void:
	var e := _yeni()
	e.zaman_gecir(1000.0)
	e.zaman_gecir(1000.0 + 3600.0 * 24 * 30)
	esit(e.state.kaynaklar["hava"], GardenState.KAYNAK_TABAN, "bir ay sonra bile taban")
	esit(e.canlilik(), 0.0, "solgun ama ölü değil")


func test_oturum_acilisi_bismillah() -> void:
	var e := _yeni()
	var o := e.say("bismillah", 1, {"oturum_acilisi": true})
	dogru(olay_var(o, "tamamlandi", {"asset": "bahce_kapisi"}), "Bismillah ile kapı açılır")
