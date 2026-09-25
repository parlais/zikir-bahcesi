extends TestCase
## K12, K13: Nur ↔ Ori ışık karıştırıcısı ve geçiş zamanlayıcısı.


func _yakin(a: Variant, b: Variant, mesaj: String) -> void:
	var ok := false
	if a is Color and b is Color:
		ok = (a as Color).is_equal_approx(b)
	elif a is Vector3 and b is Vector3:
		ok = (a as Vector3).is_equal_approx(b)
	elif (a is float or a is int) and (b is float or b is int):
		ok = is_equal_approx(float(a), float(b))
	else:
		ok = a == b
	dogru(ok, "%s: beklenen %s, gelen %s" % [mesaj, b, a])


func test_nur_ve_ori_profilleri_karismaya_uygun() -> void:
	for kesit in [false, true]:
		var a := AnimasyonStilleri.al(IsikKaristirici.UC_NUR, kesit)
		var b := AnimasyonStilleri.al(IsikKaristirici.UC_ORI, kesit)
		for h in IsikKaristirici.uyumsuzluklar(a, b):
			dogru(false, "%s: %s" % ["kesit" if kesit else "kat", h])


func test_uclar_profillerin_kendisi() -> void:
	var nur := AnimasyonStilleri.al("nur")
	var ori := AnimasyonStilleri.al("sky")
	var p0 := IsikKaristirici.profil(0.0)
	var p1 := IsikKaristirici.profil(1.0)
	for yol in ["gok/tepe", "ortam/pozlama", "ortam/sis/0", "ortam/sis/1",
			"ortak/kenar", "malzeme/su/isima_guc", "malzeme/cicek/isima_guc", "bulut_renk/0", "parcacik/nur_renk"]:
		_yakin(IsikKaristirici.oku(p0, yol), IsikKaristirici.oku(nur, yol), "t=0 " + yol)
		_yakin(IsikKaristirici.oku(p1, yol), IsikKaristirici.oku(ori, yol), "t=1 " + yol)
	esit(p1["parcacik"]["nur"], ori["parcacik"]["nur"], "t=1 nur zerresi sayısı")
	# Uçlarda yalnız o ucun ışığı yanar, olduğu gibi
	for alan in ["yon", "yukseklik", "renk", "enerji", "yumusak", "golge_bulanik", "golge_mesafe"]:
		_yakin(p0["gunes"][alan], nur["gunes"][alan], "t=0 Nur ışığı " + alan)
		_yakin(p1["gunes_b"][alan], ori["gunes"][alan], "t=1 Ori ışığı " + alan)
	_yakin(p0["gunes_b"]["enerji"], 0.0, "t=0 Ori ışığı sönük")
	_yakin(p1["gunes"]["enerji"], 0.0, "t=1 Nur ışığı sönük")


func test_ortada_yari_yarim() -> void:
	var nur := AnimasyonStilleri.al("nur")
	var ori := AnimasyonStilleri.al("sky")
	var p := IsikKaristirici.profil(0.5)
	_yakin(p["gunes"]["enerji"], nur["gunes"]["enerji"] * 0.5, "Nur ışığı yarı yarıya")
	_yakin(p["gunes_b"]["enerji"], ori["gunes"]["enerji"] * 0.5, "Ori ışığı yarı yarıya")
	_yakin(p["gok"]["ufuk"], (nur["gok"]["ufuk"] as Color).lerp(ori["gok"]["ufuk"], 0.5), "ufuk rengi")
	_yakin(p["ortam"]["hacim_sis"][0], (nur["ortam"]["hacim_sis"][0] + ori["ortam"]["hacim_sis"][0]) * 0.5, "hacim sisi")
	esit(typeof(p["parcacik"]["nur"]), TYPE_INT, "zerre sayısı tam sayı kalır")


func test_isik_capraz_gecer_gezinmez() -> void:
	# Işıklar ve gökteki parıltılar yerinde kalır, yalnız güçleri değişir (K13).
	var nur := AnimasyonStilleri.al("nur")
	var ori := AnimasyonStilleri.al("sky")
	for t in [0.0, 0.3, 0.7, 1.0]:
		var p := IsikKaristirici.profil(t)
		for alan in ["yon", "yukseklik"]:
			_yakin(p["gunes"][alan], nur["gunes"][alan], "t=%s Nur ışığının %s" % [t, alan])
			_yakin(p["gunes_b"][alan], ori["gunes"][alan], "t=%s Ori ışığının %s" % [t, alan])
		_yakin(p["gok"]["nur_yon"], nur["gok"]["nur_yon"], "t=%s Nur parıltısının yeri" % t)
		_yakin(p["gok"]["nur_yon_b"], ori["gok"]["nur_yon"], "t=%s Ori parıltısının yeri" % t)
		_yakin(p["gok"]["nur_karisim"], t, "t=%s parıltı karışımı" % t)
		_yakin(p["gunes"]["enerji"], nur["gunes"]["enerji"] * (1.0 - t), "t=%s Nur ışığı söner" % t)
		_yakin(p["gunes_b"]["enerji"], ori["gunes"]["enerji"] * t, "t=%s Ori ışığı belirir" % t)
		for yol in IsikKaristirici.SABIT:
			_yakin(IsikKaristirici.oku(p, yol), IsikKaristirici.oku(nur, yol), "t=%s %s" % [t, yol])


func test_karistirma_girdileri_degistirmez() -> void:
	var a := AnimasyonStilleri.al("nur")
	var b := AnimasyonStilleri.al("sky")
	var once: Color = a["gok"]["tepe"]
	var p := IsikKaristirici.karistir(a, b, 0.5)
	p["gok"]["tepe"] = Color.RED
	(p["ortam"]["sis"] as Array)[0] = 1.0
	esit(a["gok"]["tepe"], once, "Nur profili değişmemeli")
	dogru(a["ortam"]["sis"][0] < 0.01, "Nur sis dizisi değişmemeli")


func test_parlama_kipi_iki_ucta_ayni() -> void:
	# Kip kesiklidir: uçlarda farklıysa geçişin ortasında parıltı bir anda sıçrar.
	for kesit in [false, true]:
		var a := AnimasyonStilleri.al("nur", kesit)
		var b := AnimasyonStilleri.al("sky", kesit)
		dogru(a["ortam"].has("parlama_kip"), "Nur parlama kipini açıkça yazmalı")
		esit(a["ortam"].get("parlama_kip"), b["ortam"].get("parlama_kip"), "parlama kipi")


# --------------------------------------------------------------------------
# Geçiş zamanlayıcısı
# --------------------------------------------------------------------------

func _ilerlet(g: IsikGecisi, sure: float, adim := 0.1) -> void:
	var n := int(round(sure / adim))
	for i in n:
		g.ilerle(adim)


func test_gecis_zemini_nur() -> void:
	var g := IsikGecisi.new()
	_ilerlet(g, 30.0)
	esit(g.t, 0.0, "tetik yokken Nur")


func test_zikir_tamamlaninca_ori_sonra_nur() -> void:
	var g := IsikGecisi.new()
	g.olay({"tur": "tamamlandi", "asset": "gul", "adet": 1})
	_ilerlet(g, IsikGecisi.GIRIS * 0.5)
	dogru(g.t > 0.2 and g.t < 0.8, "çıkışın ortasında ara ışık: %s" % g.t)
	_ilerlet(g, IsikGecisi.GIRIS * 0.5 + 1.0)
	_yakin(g.t, 1.0, "çıkış bitince Ori")
	_ilerlet(g, IsikGecisi.KALIS["tamamlandi"] - IsikGecisi.GIRIS - 2.0)
	_yakin(g.t, 1.0, "kalış boyunca Ori")
	_ilerlet(g, 2.0 + IsikGecisi.DONUS + 1.0)
	_yakin(g.t, 0.0, "dönüş bitince Nur")


func test_yeni_zikir_kalisi_uzatir() -> void:
	var g := IsikGecisi.new()
	g.olay({"tur": "esma_tamam", "esma": "nur", "kez": 1})
	_ilerlet(g, IsikGecisi.KALIS["esma_tamam"] - 1.0)
	g.olay({"tur": "tamamlandi", "asset": "gul", "adet": 2})
	_ilerlet(g, 5.0)
	_yakin(g.t, 1.0, "zikir sürdükçe Ori'de kalır")


func test_donuste_tetik_sicramadan_geri_cikar() -> void:
	var g := IsikGecisi.new()
	g.tetikle("kat_gecisi")
	_ilerlet(g, IsikGecisi.KALIS["kat_gecisi"] + IsikGecisi.DONUS * 0.5)
	var once := g.t
	dogru(once > 0.05 and once < 0.95, "dönüşün ortasında: %s" % once)
	g.tetikle("ziyaret")
	g.ilerle(0.1)
	dogru(g.t >= once and g.t - once < 0.05, "tetik ışığı sıçratmaz: %s -> %s" % [once, g.t])


func test_isigi_degistirmeyen_olaylar() -> void:
	var g := IsikGecisi.new()
	for o in [{"tur": "kaynak", "kaynak": "hava", "deger": 30.0}, {"tur": "asama", "asset": "gul", "asama": 2},
			{"tur": "tarif", "tarif": "gul_bali", "asset": "gul_bali", "adet": 1}, {"tur": "seri_devam", "gun": 3},
			{"tur": "kart", "esma": "nur"}, {"tur": "ardisik", "asset": "gul_kokusu"}]:
		g.olay(o)
	_ilerlet(g, 5.0)
	esit(g.t, 0.0, "yalnız zikir tamamlanması ve olaylar ışığı değiştirir")


func test_tuba_asamasi_isigi_degistirir() -> void:
	var g := IsikGecisi.new()
	g.olay({"tur": "asama", "asset": "tuba", "asama": 2})
	_ilerlet(g, IsikGecisi.GIRIS + 1.0)
	_yakin(g.t, 1.0, "Tûbâ aşaması")


func test_zorla_sabitler() -> void:
	var g := IsikGecisi.new()
	g.zorla(0.5)
	g.tetikle("acilis")
	_ilerlet(g, 20.0)
	_yakin(g.t, 0.5, "zorlanan değer")
