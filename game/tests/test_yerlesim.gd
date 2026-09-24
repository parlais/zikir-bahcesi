extends TestCase
## Bahçe yerleşimi içerikle ve üretilmiş modellerle uyumlu mu?

var c := Content.load_default()


func test_yerlesimdeki_assetler_var_ve_modelleri_uretilmis() -> void:
	for id in Yerlesim.YUVALAR:
		dogru(c.assets.has(id), "yerleşimde bilinmeyen asset: " + id)
		if not c.assets.has(id):
			continue
		for m in c.assets[id]["modeller"]:
			dogru(ResourceLoader.exists(Yerlesim.MODEL_DIR + m + ".glb"), "model üretilmemiş: " + m)


func test_yuvalar_ada_icinde() -> void:
	for id in Yerlesim.YUVALAR:
		for yuva in Yerlesim.YUVALAR[id]:
			var p: Vector3 = yuva[0]
			dogru(Vector2(p.x, p.z).length() < 5.4, "%s adanın kenarına çok yakın: %s" % [id, p])


func test_hud_seceneklerinin_hepsi_sayilabilir() -> void:
	for key in ZikirSecenekleri.ILK_DILIM:
		var base: String = key.trim_prefix("esma:")
		dogru(c.zikirler.has(key) or (key.begins_with("esma:") and c.esma.has(base)), "bilinmeyen söz: " + key)
