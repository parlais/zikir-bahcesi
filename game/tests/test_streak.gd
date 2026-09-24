extends TestCase


func _seri() -> Dictionary:
	return GardenState.new().seri


func test_art_arda_gunler() -> void:
	var s := _seri()
	StreakSystem.kaydet(s, 100)
	StreakSystem.kaydet(s, 101)
	esit(StreakSystem.kaydet(s, 101)["tur"], "yok", "aynı gün iki kez sayılmaz")
	esit(s["gun"], 2, "iki gün")


func test_dondurma_kacan_gunu_kapatir() -> void:
	var s := _seri()
	StreakSystem.kaydet(s, 100)
	var o := StreakSystem.kaydet(s, 102)
	esit(o["tur"], "dondurma", "bir gün kaçtı, dondurma kullanıldı")
	esit(s["gun"], 2, "seri sürdü")
	esit(s["dondurma"], 0, "dondurma harcandı")


func test_yeniden_baslama_cezasiz() -> void:
	var s := _seri()
	for g in range(100, 105):
		StreakSystem.kaydet(s, g)
	var o := StreakSystem.kaydet(s, 120)
	esit(o["tur"], "yeniden", "uzun ara")
	esit(s["gun"], 1, "yeni seri")
	esit(s["en_uzun"], 5, "en uzun seri korunur")


func test_haftada_bir_dondurma_kazanilir() -> void:
	var s := _seri()
	s["dondurma"] = 0
	for g in range(1, 8):
		StreakSystem.kaydet(s, g)
	esit(s["dondurma"], 1, "7. günde dondurma")
