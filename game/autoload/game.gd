extends Node
## Oyunun tek giriş noktası (autoload "Game").
##
## İçeriği ve kaydı yükler, giriş kaynaklarından gelen sözleri ZikirEngine'e
## iletir ve olayları arayüze sinyal olarak yayar. Kurallar core/ altındadır;
## burada yalnızca bağlama (cuma mı, oturum açılışı mı) ve kayıt işleri yapılır.

## Motorun ürettiği her olay (bkz. ZikirEngine başı).
signal olay(o: Dictionary)
## Sayaçlar, envanter veya ayarlar değişti; arayüz kendini tazelesin.
signal durum_degisti

const KAYIT_GECIKMESI := 2.0

var content: Content
var state: GardenState
var engine: ZikirEngine
var tarifler: RecipeSystem
var resolver: PhraseResolver
var tesbih: TapTesbihSource
## Bu oturumda Bismillah ile açılış yapıldı mı?
var oturum_acildi := false
## İlk açılış mı (temsil notu gösterilecek mi)?
var ilk_acilis := false

var _kayit_zamanlayici: Timer
var _kaynaklar: Array[ZikirInputSource] = []
## Geliştirici komutlarında (ekran görüntüsü, senaryo) kayıt diske yazılmaz.
var _kayit_kapali := false
## Geliştirici: kartları gösterme (--zb-kartsiz=1).
var kartsiz := false
## Geliştirici: çalıştırılan senaryo adı (varsa açılış kartı atlanır).
var senaryo := ""


func _ready() -> void:
	content = Content.load_default()
	var gelistirici := _gelistirici_argumanlari()
	_kayit_kapali = not gelistirici.is_empty()
	kartsiz = gelistirici.has("kartsiz")
	senaryo = gelistirici.get("senaryo", "")
	ilk_acilis = _kayit_kapali or not FileAccess.file_exists(SaveSystem.VARSAYILAN_YOL)
	_durum_kur(GardenState.new() if _kayit_kapali else SaveSystem.yukle())
	resolver = PhraseResolver.new(content.zikirler)

	tesbih = TapTesbihSource.new()
	tesbih.name = "TapTesbih"
	add_child(tesbih)
	kaynak_ekle(tesbih)

	_kayit_zamanlayici = Timer.new()
	_kayit_zamanlayici.one_shot = true
	_kayit_zamanlayici.wait_time = KAYIT_GECIKMESI
	_kayit_zamanlayici.timeout.connect(kaydet)
	add_child(_kayit_zamanlayici)
	if not gelistirici.is_empty():
		_gelistirici_calistir.call_deferred(gelistirici)


func _durum_kur(s: GardenState) -> void:
	state = s
	engine = ZikirEngine.new(content, state)
	tarifler = RecipeSystem.new(content, state)
	engine.zaman_gecir(Time.get_unix_time_from_system())


## Mikrofon kaynağı sonraki fazda buradan bağlanacak.
func kaynak_ekle(k: ZikirInputSource) -> void:
	_kaynaklar.append(k)
	k.soz_algilandi.connect(_on_soz.bind(k))


func _on_soz(key: String, bas: float, son: float, k: ZikirInputSource) -> void:
	if k.kesin:
		say(key)
	else:
		resolver.ekle(key, bas, son)


func _process(_delta: float) -> void:
	if resolver.bekleyen_sayisi() > 0:
		for key in resolver.guncelle(ZikirInputSource.simdi()):
			say(key)


## Bir sözü sayar ve olayları yayar. Bağlam (cuma, oturum açılışı) burada eklenir.
func say(key: String, n: int = 1) -> Array:
	var baglam := {}
	if key == "salavat" and Time.get_date_dict_from_system()["weekday"] == Time.WEEKDAY_FRIDAY:
		baglam["cuma"] = true
	if key == "bismillah" and not oturum_acildi:
		baglam["oturum_acilisi"] = true
		oturum_acildi = true
	engine.zaman_gecir(Time.get_unix_time_from_system())
	var olaylar := engine.say(key, n, baglam)
	var seri := StreakSystem.kaydet(state.seri, StreakSystem.bugun())
	if seri["tur"] != "yok":
		seri["tur"] = "seri_" + seri["tur"]
		olaylar.append(seri)
	for o in olaylar:
		olay.emit(o)
	durum_degisti.emit()
	_kayit_zamanlayici.start()
	return olaylar


func tarif_yap(tarif_id: String) -> void:
	for o in tarifler.yap(tarif_id):
		olay.emit(o)
	durum_degisti.emit()
	_kayit_zamanlayici.start()


func ebced_modu_ayarla(acik: bool) -> void:
	state.ebced_modu = acik
	durum_degisti.emit()
	kaydet()


func kaydet() -> void:
	if _kayit_kapali:
		return
	var err := SaveSystem.kaydet(state)
	if err != OK:
		push_warning("Kayıt yazılamadı: %s" % error_string(err))


## Yalnızca geliştirme için: bahçeyi sıfırlar.
func sifirla() -> void:
	_durum_kur(GardenState.new())
	oturum_acildi = false
	kaydet()
	durum_degisti.emit()


func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST or what == NOTIFICATION_APPLICATION_PAUSED:
		kaydet()


# --------------------------------------------------------------------------
# Geliştirici komutları (yalnız masaüstünde, komut satırından):
#   godot --path game -- --zb-senaryo=demo --zb-ekran=/yol/ekran.png
# Senaryo bahçeyi örnek sayılarla doldurur; ekran seçeneği birkaç kare sonra
# görüntüyü kaydedip çıkar. Kayıt diske yazılmaz.
# --------------------------------------------------------------------------

func _gelistirici_argumanlari() -> Dictionary:
	var d := {}
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--zb-") and a.contains("="):
			d[a.get_slice("=", 0).trim_prefix("--zb-")] = a.get_slice("=", 1)
	return d


func _gelistirici_calistir(d: Dictionary) -> void:
	var senaryo: String = d.get("senaryo", "")
	if senaryo == "demo":
		var sayilar := {
			"bismillah": 1, "subhanallahil_azim": 245, "esma:allah": 330, "esma:nur": 256,
			"lahavle": 33, "esma:kuddus": 170, "ihlas": 10, "esma:hadi": 40, "esma:vacid": 14,
			"esma:vehhab": 14, "esma:latif": 129, "esma:rezzak": 308, "rabbi_zidni_ilma": 1,
			"subhanallah": 33, "elhamdulillah": 33, "allahu_ekber": 33, "tesbihat": 1, "tevhid": 60,
		}
		for key in sayilar:
			engine.say(key, sayilar[key], {"oturum_acilisi": key == "bismillah"})
		oturum_acildi = true
		durum_degisti.emit()
	elif senaryo == "kart":
		say("bismillah")
		say("esma:allah", 66)
	if d.has("ekran"):
		var kare := int(d.get("kare", "90"))
		for i in kare:
			await get_tree().process_frame
		var img := get_viewport().get_texture().get_image()
		var err := img.save_png(d["ekran"])
		print("Ekran görüntüsü: %s (%s)" % [d["ekran"], error_string(err)])
		if d.has("olcum"):
			# --zb-olcum=1: son karenin çizim bütçesi (telefon bütçesiyle karşılaştırmak için)
			print("Ölçüm: %d üçgen, %d çizim çağrısı, %d nesne" % [
				RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME),
				RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME),
				RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_OBJECTS_IN_FRAME)])
		get_tree().quit()
