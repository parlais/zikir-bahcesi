extends TestCase
## Dünya yuvaları (K20): dunya_cennet.json "yuvalar" alanı içerikle uyumlu mu?
## Alan yoksa: python3 tools/model_factory/build_all.py ZB_dunya_cennet

var c := Content.load_default()
var y := DunyaYuvalari.yukle()
## Kapı çakıl sınırının üstündedir; sınır arsa yarıçapının çevresinde en çok bu kadar dalgalanır.
const SINIR_DALGASI := 1.7


func _arsa_r() -> float:
	var d = JSON.parse_string(FileAccess.get_file_as_string(DunyaYuvalari.VARSAYILAN_YOL))
	return float(d.get("arsa_r", 13.0)) if d is Dictionary else 13.0


func _veri_var() -> bool:
	dogru(not y.hepsi().is_empty(), "dunya_cennet.json'da yuva yok (build_all.py ZB_dunya_cennet)")
	return not y.hepsi().is_empty()


func test_sozlukten_kurulur() -> void:
	var t := DunyaYuvalari.sozlukten({
		"arsa": [[1.0, 0.0, 2.0, 90.0, 1.5, "lale", 3.0], [0.0, 0.0, 0.0, 0.0, 1.0, "tuba", 0.0]],
		"cevre": [[20.0, 1.0, -30.0, 0.0, 1.0, "lale", 1.0]],
		"ayak": {"lale": 0.2},
	})
	esit(t.assetler(), ["lale", "tuba"], "asset'ler")
	esit(t.sayi("lale"), 2, "iki lale yuvası")
	esit(t.sayi("kosk"), 0, "yuvası olmayan")
	var ilk: Array = t.yuvalar("lale")[0]
	esit(DunyaYuvalari.sira(ilk), 1, "sıraya göre: önce çevredeki")
	esit(t.bolge(ilk), "cevre", "bölge")
	esit(DunyaYuvalari.konum(ilk), Vector3(20, 1, -30), "konum")
	esit(typeof(DunyaYuvalari.sira(ilk)), TYPE_INT, "sıra tam sayı")
	esit(t.ayak_r(t.yuvalar("lale")[1]), 0.2 * 1.5, "ölçekli taban yarıçapı")
	esit(t.hepsi().size(), 3, "hepsi")
	esit(DunyaYuvalari.asset(t.hepsi()[0]), "tuba", "hepsi sıraya göre")
	esit(DunyaYuvalari.sozlukten([[0.0, 0.0, 0.0, 0.0, 1.0, "tuba", 0]]).sayi("tuba"), 1, "düz dizi")


func test_her_mvp_3d_asset_yuvali() -> void:
	if not _veri_var():
		return
	for id in c.assets:
		var a: Dictionary = c.assets[id]
		# Irmaklar dünya modelinin parçasıdır (ırmak başına düğüm); yuvaları yoktur.
		if a["oncelik"] == "MVP" and a["tip"] in ["3D", "3D-A"] and not id in DunyaDurumu.IRMAKLAR:
			dogru(y.sayi(id) >= 1, "yuvası yok: " + id)
			if id != "tuba" and str(a["modeller"][0]).begins_with("ZB_agac_"):
				dogru(y.sayi(id) > 1, "ağacın birden çok yuvası olmalı: " + id)
	for id in y.assetler():
		dogru(c.assets.has(id), "yuvada bilinmeyen asset: " + id)
		dogru(y.ayak.has(id), "taban yarıçapı yok: " + id)


func test_arsa_yuvalari_arsanin_icinde() -> void:
	if not _veri_var():
		return
	var r := _arsa_r()
	dogru(y.bolgeler.get("arsa", []).size() > 10, "arsada yuva var")
	for yuva in y.bolgeler.get("arsa", []):
		var p := DunyaYuvalari.konum(yuva)
		var d := Vector2(p.x, p.z).length()
		if DunyaYuvalari.asset(yuva) == "bahce_kapisi":
			dogru(d <= r + SINIR_DALGASI and d >= r - SINIR_DALGASI, "kapı sınırda değil: %s" % p)
			dogru(p.x > 0.0, "kapı doğu kenarında")
		else:
			dogru(d + y.ayak_r(yuva) <= r, "%s arsanın dışına taşıyor: %s" % [DunyaYuvalari.asset(yuva), p])
	esit(DunyaYuvalari.konum(y.yuvalar("tuba")[0]), Vector3.ZERO, "Tûbâ ortada")
	for yuva in y.bolgeler.get("cevre", []):
		var p := DunyaYuvalari.konum(yuva)
		dogru(Vector2(p.x, p.z).length() > r, "çevre yuvası arsanın içinde: %s" % p)


func test_yuvalar_cakismiyor() -> void:
	if not _veri_var():
		return
	var hepsi := y.hepsi()
	for i in hepsi.size():
		var a: Array = hepsi[i]
		var pa := DunyaYuvalari.konum(a)
		for j in range(i + 1, hepsi.size()):
			var b: Array = hepsi[j]
			var pb := DunyaYuvalari.konum(b)
			var d := Vector2(pa.x - pb.x, pa.z - pb.z).length()
			if d < y.ayak_r(a) + y.ayak_r(b) - 0.02:  # konumlar 1 cm'ye yuvarlanır
				dogru(false, "%s (%d) ile %s (%d) çakışıyor" % [DunyaYuvalari.asset(a), DunyaYuvalari.sira(a),
					DunyaYuvalari.asset(b), DunyaYuvalari.sira(b)])


func test_yuva_sirasi_benzersiz() -> void:
	if not _veri_var():
		return
	var gorulen := {}
	for yuva in y.hepsi():
		var s := DunyaYuvalari.sira(yuva)
		dogru(not gorulen.has(s), "sıra tekrar ediyor: %d" % s)
		gorulen[s] = true
		dogru(s >= 0, "sıra negatif")


func test_gercek_yuvalarla_hesap() -> void:
	if not _veri_var():
		return
	var e := ZikirEngine.new(c, GardenState.new())
	e.say("subhanallahil_azim", 150)
	var h := DunyaDurumu.hesapla(c, e.state, e, y)
	esit(h["yuva"]["hurma_agaci"], ["ZB_agac_hurma_a4", "ZB_agac_hurma_a3"], "ilk iki hurma yuvası")
	var ilk: Array = y.yuvalar("hurma_agaci")[0]
	esit(y.bolge(ilk), "arsa", "ilk olgun hurma arsada")
	var v := DunyaDurumu.vitrin(c, y)
	esit(v["yuva"]["servi"].size(), y.sayi("servi"), "vitrinde bütün servi yuvaları dolu")
