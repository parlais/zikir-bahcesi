extends TestCase

var c := Content.load_default()


func test_sayilar_asset_listesiyle_uyusur() -> void:
	esit(c.assets.size(), 161, "asset sayısı (148 + 13 tarif ürünü)")
	var doksan_dokuz := c.esma.values().filter(func(e): return e["doksan_dokuz"])
	esit(doksan_dokuz.size(), 99, "99 esma")
	esit(c.esma.size(), 101, "99 + Cemîl + Şâfî")
	esit(c.tarifler.size(), 15, "13 model tarifi + 2 etki tarifi")
	esit(c.meta["ozet"]["MVP"]["asset"], 44, "MVP asset (40 + dört ırmak)")
	esit(c.meta["ozet"]["MVP"]["model"], 59, "MVP model (ırmaklar dünya modelinin parçası)")
	esit(c.meta["ozet"]["toplam"]["model"], 203, "toplam model")


## JSON sayıları float döner; dizi karşılaştırması için tam sayıya çevirir.
func _tamsayilar(dizi: Array) -> Array:
	return dizi.map(func(x): return int(x))


## Sözleşme (K20): sahne ırmakları bu kimliklerle açar; her biri istiğfarın
## ömür boyu toplamıyla bir kez gelir.
func test_dort_irmak_sozlesmesi() -> void:
	var esik := {"irmak_su": 100, "irmak_sut": 300, "irmak_bal": 700, "irmak_serbet": 1000}
	for id in esik:
		dogru(c.assets.has(id), "ırmak asset'i yok: " + id)
		if not c.assets.has(id):
			continue
		var a: Dictionary = c.assets[id]
		esit(a["tetikleyici"]["kaynak"], "istigfar", id + " istiğfarla gelir")
		esit(a["tetikleyici"]["kural"], "toplam", id + " toplam kuralı")
		dogru(c.tekrarsiz(id), id + " tekrarsız")
		esit(_tamsayilar(a["esikler"]), [esik[id]], id + " eşiği")
		esit(_tamsayilar(a["esikler_serbest"]), [esik[id]], id + " eşiği ebced kapalıyken de aynı")
		esit(a["asama_sayisi"], 1, id + " tek aşamalı")
		esit(a["tip"], "3D", id + " tipi")
		esit(a["oncelik"], "MVP", id + " önceliği")
		esit(a["modeller"], [], id + " ayrı model dosyası yok")
		esit(a.get("dunya_parcasi"), "ZB_dunya_cennet", id + " dünya modelinin parçası")
	dogru(not c.tekrarsiz("nisan_yagmuru"), "nisan yağmuru her 100'de tekrarlanır")
	esit(c.by_key["istigfar"], ["nisan_yagmuru", "irmak_su", "irmak_sut", "irmak_bal", "irmak_serbet"],
		"istiğfar sırası: önce yağmur, sonra ırmaklar")


func test_model_dosya_adlari_kurala_uyar() -> void:
	var re := RegEx.create_from_string("^ZB_(agac|cicek|bitki|canli|yapi|obje|tarif)_[a-z0-9_]+?(_a[1-5])?$")
	for id in c.assets:
		for m in c.assets[id]["modeller"]:
			dogru(re.search(m) != null, "dosya adı kurala uymuyor: " + m)


func test_tetikleyici_dizini() -> void:
	dogru(c.by_key["subhanallahil_azim"].has("hurma_agaci"), "hurma Sübhanallahi'l-azîm ile büyür")
	dogru(c.by_key["esma:nur"].has("kandil"), "kandil Nûr ile açılır")
	esit(c.by_key["esma:nur"][-1], "fanus", "fanus Nûr'un ikinci item'ı, sırada sonda")
	dogru(c.her_n_by_key["subhanallah"].has("guvercin"), "her 33 Sübhanallah'ta kuş")
	dogru(c.ardisik_by_key["salavat"].has("gul_kokusu_parcaciklari"), "10 üst üste salavat")
	dogru(c.by_key["salavat@cuma"].has("beyaz_gul"), "beyaz gül yalnız cuma salavatıyla")
	dogru(c.turev_by_key["item:define_sandigi"].has("inci"), "inci define sandığından çıkar")
	esit(c.kart_by_key.size(), 7, "7 celâlî isim kartı")


func test_esma_ebced_ve_mod() -> void:
	esit(c.esma_hedefi("nur", true), 256, "Nûr ebcedi")
	esit(c.esma_hedefi("nur", false), 33, "serbest mod")
	esit(c.esma["hafiz"]["grup"], true, "998 aile hedefi")
	esit(c.key_label("esma:nur"), "Yâ Nûr", "etiket")
	esit(c.key_label("esma:allah"), "Allah", "Allah lafzına Yâ eklenmez")
