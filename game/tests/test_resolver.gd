extends TestCase

var c := Content.load_default()


func test_onek_bekletilir_sonra_kesinlesir() -> void:
	var r := PhraseResolver.new(c.zikirler)
	r.ekle("subhanallah", 0.0, 0.8)
	esit(r.guncelle(1.0).size(), 0, "önek söz hemen sayılmaz")
	esit(r.guncelle(2.1), ["subhanallah"] as Array[String], "bekleme bitince sayılır")


func test_uzun_soz_onegi_duser() -> void:
	var r := PhraseResolver.new(c.zikirler)
	r.ekle("subhanallah", 0.0, 0.8)
	r.ekle("subhanallahi_ve_bihamdihi", 0.0, 1.5)
	esit(r.guncelle(5.0), ["subhanallahi_ve_bihamdihi"] as Array[String], "yalnız uzun söz sayılır")


func test_cakisan_ortak_sonek_uzun_kazanir() -> void:
	var r := PhraseResolver.new(c.zikirler)
	r.ekle("masaallah", 0.0, 2.0)
	r.ekle("lahavle", 0.9, 2.0)
	esit(r.guncelle(5.0), ["masaallah"] as Array[String], "kısa çakışan algılama atılır")


func test_onek_olmayan_hemen_sayilir() -> void:
	var r := PhraseResolver.new(c.zikirler)
	r.ekle("elhamdulillah", 0.0, 0.7)
	esit(r.guncelle(0.7), ["elhamdulillah"] as Array[String], "bekleme yok")


func test_art_arda_iki_ayri_soz() -> void:
	var r := PhraseResolver.new(c.zikirler)
	r.ekle("elhamdulillah", 0.0, 0.7)
	r.ekle("elhamdulillah", 0.9, 1.6)
	esit(r.guncelle(2.0).size(), 2, "çakışmayan iki söz iki kez sayılır")
