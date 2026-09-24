extends TestCase

var c := Content.load_default()


func test_gul_bali_gulleri_harcamaz() -> void:
	var s := GardenState.new()
	var r := RecipeSystem.new(c, s)
	s.envanter["kirmizi_gul"] = 100
	dogru(not r.yapilabilir("gul_bali_kavanozu"), "kovan olmadan yapılamaz")
	esit(r.eksikler("gul_bali_kavanozu")[0]["asset"], "ari_kovani", "eksik kovan")
	s.envanter["ari_kovani"] = 1
	var o := r.yap("gul_bali_kavanozu")
	dogru(olay_var(o, "tarif", {"asset": "gul_bali_kavanozu"}), "gül balı yapıldı")
	esit(s.adet("kirmizi_gul"), 100, "güller bahçede kalır")
	esit(s.adet("ari_kovani"), 1, "kovan yerinde kalır")


func test_malzeme_tuketilir() -> void:
	var s := GardenState.new()
	var r := RecipeSystem.new(c, s)
	s.envanter["un_cuvali"] = 4
	r.yap("tas_firin_ve_ekmek")
	esit(s.adet("un_cuvali"), 1, "3 un çuvalı harcandı")
	esit(s.adet("tas_firin_ve_ekmek"), 1, "fırın ve ekmek")


func test_etki_tarifi() -> void:
	var s := GardenState.new()
	var r := RecipeSystem.new(c, s)
	s.envanter["zeytinyagi_testisi"] = 1
	s.envanter["kandil"] = 1
	r.yap("kandil_tam_parlaklik")
	esit(s.adet("etki:kandil_tam_parlaklik"), 1, "kandil tam parlak")
	esit(s.adet("kandil"), 1, "kandil kalır")


func test_kayit_gidis_donus() -> void:
	var e := ZikirEngine.new(c, GardenState.new())
	e.say("subhanallahil_azim", 42)
	e.say("esma:nur", 256)
	e.state.ebced_modu = false
	StreakSystem.kaydet(e.state.seri, 500)
	var yol := "user://test_kayit.json"
	esit(SaveSystem.kaydet(e.state, yol), OK, "kaydedildi")
	var s := SaveSystem.yukle(yol)
	esit(s.sayac("subhanallahil_azim"), 42, "sayaç")
	esit(s.adet("kandil"), 1, "envanter")
	esit(s.ebced_modu, false, "mod")
	esit(s.seri["son_gun"], 500, "seri")
	esit(typeof(s.sayaclar["esma:nur"]), TYPE_INT, "sayaçlar tam sayı döner")
	var e2 := ZikirEngine.new(c, s)
	esit(e2.ilerleme("hurma_agaci")["sayi"], 42, "yüklenen durumla ilerleme aynı")
	DirAccess.remove_absolute(yol)
