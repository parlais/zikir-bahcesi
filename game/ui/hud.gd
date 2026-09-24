class_name Hud
extends CanvasLayer
## Oyun arayüzü: zikir seçici, dokunmatik tesbih, ilerleme, "Neden bu?"
## kartları, açılış notu ve ayarlar. Bütün arayüz koddan kurulur.

const TESBIHAT_ADIMLARI := [["subhanallah", 33], ["elhamdulillah", 33], ["allahu_ekber", 33]]
const DAYANAK := {"N": "Ayet veya hadis", "G": "Gelenek", "A": "İsmin anlamı"}
const TEMSIL_NOTU := "Bu bahçe bir temsildir; gerçek cennet tasavvurun ötesindedir."

var secili := "subhanallahil_azim"
var _tesbihat_adim := 0
var _tesbihat_sayi := 0

var _arapca: Label
var _ad: Label
var _hedef: Label
var _cubuk: ProgressBar
var _tesbih_dugmesi: Button
var _seri: Label
var _kaynak_cubuklari: Dictionary = {}
var _cipler: Dictionary = {}
var _bildirim: Label
var _kart_katmani: Control
var _kart_kuyrugu: Array = []
var _ayarlar: Control
var _ebced: CheckButton


func _ready() -> void:
	var kok := Control.new()
	kok.set_anchors_preset(Control.PRESET_FULL_RECT)
	kok.mouse_filter = Control.MOUSE_FILTER_IGNORE
	kok.theme = Tema.al()
	add_child(kok)
	_ust_cubuk(kok)
	_alt_panel(kok)
	_bildirim_kur(kok)
	_kart_katmani_kur(kok)
	_ayarlar_kur(kok)
	Game.durum_degisti.connect(_tazele)
	Game.olay.connect(_on_olay)
	_sec(secili)
	_tazele()
	_acilis_karti()


# --------------------------------------------------------------------------
# Kurulum
# --------------------------------------------------------------------------

func _ust_cubuk(kok: Control) -> void:
	var m := MarginContainer.new()
	m.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	for k in ["left", "right"]:
		m.add_theme_constant_override("margin_" + k, 20)
	m.add_theme_constant_override("margin_top", 24)
	m.mouse_filter = Control.MOUSE_FILTER_IGNORE
	kok.add_child(m)
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", 12)
	m.add_child(h)

	var seri_kutu := PanelContainer.new()
	_seri = _etiket("", 22, 800)
	seri_kutu.add_child(_seri)
	h.add_child(seri_kutu)

	var kaynaklar := PanelContainer.new()
	kaynaklar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var g := GridContainer.new()
	g.columns = 4
	g.add_theme_constant_override("h_separation", 10)
	for k in [["hava", "Hava"], ["su", "Su"], ["isik", "Işık"], ["rizik", "Rızık"]]:
		var v := VBoxContainer.new()
		v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		v.add_theme_constant_override("separation", 2)
		v.add_child(_etiket(k[1], 16, 700))
		var p := ProgressBar.new()
		p.show_percentage = false
		p.custom_minimum_size = Vector2(0, 10)
		p.min_value = 0
		p.max_value = 100
		v.add_child(p)
		_kaynak_cubuklari[k[0]] = p
		g.add_child(v)
	kaynaklar.add_child(g)
	h.add_child(kaynaklar)

	var ayar := Button.new()
	ayar.text = "Ayarlar"
	ayar.add_theme_font_size_override("font_size", 20)
	ayar.pressed.connect(func(): _ayarlar.visible = true)
	h.add_child(ayar)


func _alt_panel(kok: Control) -> void:
	var p := PanelContainer.new()
	p.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	p.grow_vertical = Control.GROW_DIRECTION_BEGIN
	p.add_theme_stylebox_override("panel", Tema.kutu(Color(Tema.KREM, 0.94), 34, 0, Color.TRANSPARENT, 20))
	kok.add_child(p)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 10)
	p.add_child(v)

	var kaydir := ScrollContainer.new()
	kaydir.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	kaydir.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_SHOW_NEVER
	kaydir.custom_minimum_size = Vector2(0, 64)
	var cipler := HBoxContainer.new()
	cipler.add_theme_constant_override("separation", 8)
	for key in ZikirSecenekleri.ILK_DILIM:
		var b := Button.new()
		b.text = _cip_adi(key)
		b.toggle_mode = true
		b.add_theme_font_size_override("font_size", 20)
		b.pressed.connect(_sec.bind(key))
		cipler.add_child(b)
		_cipler[key] = b
	kaydir.add_child(cipler)
	v.add_child(kaydir)

	_arapca = _etiket("", 40, 500)
	_arapca.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(_arapca)
	_ad = _etiket("", 28, 800)
	_ad.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_ad.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(_ad)
	_hedef = _etiket("", 20, 600)
	_hedef.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hedef.modulate = Color(1, 1, 1, 0.8)
	v.add_child(_hedef)
	_cubuk = ProgressBar.new()
	_cubuk.show_percentage = false
	_cubuk.custom_minimum_size = Vector2(0, 14)
	v.add_child(_cubuk)

	var orta := CenterContainer.new()
	_tesbih_dugmesi = Button.new()
	_tesbih_dugmesi.custom_minimum_size = Vector2(210, 210)
	_tesbih_dugmesi.add_theme_font_size_override("font_size", 46)
	for durum in ["normal", "hover"]:
		_tesbih_dugmesi.add_theme_stylebox_override(durum, Tema.kutu(Tema.FIRUZE, 105, 8, Tema.FIRUZE_KOYU))
	_tesbih_dugmesi.add_theme_stylebox_override("pressed", Tema.kutu(Tema.FIRUZE_KOYU, 105, 8, Tema.ALTIN))
	for renk in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color"]:
		_tesbih_dugmesi.add_theme_color_override(renk, Color.WHITE)
	_tesbih_dugmesi.button_down.connect(_dokun)
	orta.add_child(_tesbih_dugmesi)
	v.add_child(orta)


func _bildirim_kur(kok: Control) -> void:
	_bildirim = _etiket("", 24, 800)
	_bildirim.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_bildirim.position.y = 150
	_bildirim.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_bildirim.add_theme_stylebox_override("normal", Tema.kutu(Color(Tema.MUREKKEP, 0.82), 20, 0, Color.TRANSPARENT, 18))
	_bildirim.add_theme_color_override("font_color", Color.WHITE)
	_bildirim.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_bildirim.modulate.a = 0.0
	_bildirim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	kok.add_child(_bildirim)


func _kart_katmani_kur(kok: Control) -> void:
	_kart_katmani = ColorRect.new()
	_kart_katmani.color = Color(0.1, 0.08, 0.05, 0.45)
	_kart_katmani.set_anchors_preset(Control.PRESET_FULL_RECT)
	_kart_katmani.visible = false
	kok.add_child(_kart_katmani)


func _ayarlar_kur(kok: Control) -> void:
	_ayarlar = ColorRect.new()
	(_ayarlar as ColorRect).color = Color(0.1, 0.08, 0.05, 0.45)
	_ayarlar.set_anchors_preset(Control.PRESET_FULL_RECT)
	_ayarlar.visible = false
	kok.add_child(_ayarlar)
	var c := CenterContainer.new()
	c.set_anchors_preset(Control.PRESET_FULL_RECT)
	_ayarlar.add_child(c)
	var p := PanelContainer.new()
	p.custom_minimum_size = Vector2(600, 0)
	c.add_child(p)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 16)
	p.add_child(v)
	v.add_child(_etiket("Ayarlar", 34, 800))
	_ebced = CheckButton.new()
	_ebced.text = "Ebced modu"
	_ebced.toggled.connect(Game.ebced_modu_ayarla)
	v.add_child(_ebced)
	var aciklama := _etiket("Açıkken esmalar ebced değeri kadar sayılır (Nûr 256). Kapalıyken her esma 33'te tamamlanır. Ebced adetleri gelenek kaynaklıdır, farz değildir.", 20, 500)
	aciklama.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(aciklama)
	var sifirla := Button.new()
	sifirla.text = "Bahçeyi sıfırla (deneme)"
	sifirla.add_theme_font_size_override("font_size", 20)
	sifirla.pressed.connect(func():
		Game.sifirla()
		_bildir("Bahçe sıfırlandı"))
	v.add_child(sifirla)
	var kapat := Button.new()
	kapat.text = "Tamam"
	kapat.pressed.connect(func(): _ayarlar.visible = false)
	v.add_child(kapat)


# --------------------------------------------------------------------------
# Etkileşim
# --------------------------------------------------------------------------

func _sec(key: String) -> void:
	secili = key
	_tesbihat_adim = 0
	_tesbihat_sayi = 0
	for k in _cipler:
		_cipler[k].button_pressed = k == key
	_tazele()


func _dokun() -> void:
	Input.vibrate_handheld(18)
	var tw := create_tween()
	_tesbih_dugmesi.pivot_offset = _tesbih_dugmesi.size / 2
	tw.tween_property(_tesbih_dugmesi, "scale", Vector2(0.94, 0.94), 0.05)
	tw.tween_property(_tesbih_dugmesi, "scale", Vector2.ONE, 0.12)
	if secili == "tesbihat":
		var adim: Array = TESBIHAT_ADIMLARI[_tesbihat_adim]
		Game.tesbih.dokun(adim[0])
		_tesbihat_sayi += 1
		if _tesbihat_sayi >= adim[1]:
			_tesbihat_sayi = 0
			_tesbihat_adim += 1
			if _tesbihat_adim >= TESBIHAT_ADIMLARI.size():
				_tesbihat_adim = 0
				Game.tesbih.dokun("tesbihat")
		_tazele()
	else:
		Game.tesbih.dokun(secili)


func _tazele() -> void:
	var st := Game.state
	var c := Game.content
	var gosterilen := secili
	if secili == "tesbihat":
		gosterilen = TESBIHAT_ADIMLARI[_tesbihat_adim][0]
	_ad.text = c.key_label(gosterilen)
	_arapca.text = _arapca_metni(gosterilen)
	_arapca.visible = _arapca.text != ""
	var h := _hedef_bilgisi(secili)
	_hedef.text = h["metin"]
	_cubuk.max_value = maxf(1.0, h["hedef"])
	_cubuk.value = h["sayi"]
	_tesbih_dugmesi.text = str(h["dugme"])
	var seri: Dictionary = st.seri
	_seri.text = "Seri %d gün" % seri["gun"] if seri["gun"] > 0 else "Bugün başla"
	for k in _kaynak_cubuklari:
		_kaynak_cubuklari[k].value = st.kaynaklar[k]
	if _ebced:
		_ebced.set_pressed_no_signal(st.ebced_modu)


## Seçili sözün bir sonraki hedefi: metin, mevcut sayı, hedef sayı, düğme yazısı.
func _hedef_bilgisi(key: String) -> Dictionary:
	var c := Game.content
	var e := Game.engine
	if key == "tesbihat":
		var adim: Array = TESBIHAT_ADIMLARI[_tesbihat_adim]
		return {"metin": "33'lük tesbihat · adım %d / 3 · sonunda tesbih" % (_tesbihat_adim + 1),
				"sayi": _tesbihat_sayi, "hedef": adim[1], "dugme": _tesbihat_sayi}
	var toplam := Game.state.sayac(key)
	for id in c.by_key.get(key, []):
		var a: Dictionary = c.assets[id]
		var il := e.ilerleme(id)
		var ad := _kisa_ad(a["ad"])
		var adim_adi := ""
		if a["asama_sayisi"] > 1:
			adim_adi = " → " + str(a["asama_adlari"][mini(il["asama"], a["asama_sayisi"] - 1)])
		var grup := "  · aile hedefi" if a["grup"] else ""
		return {"metin": "%s%s · %d / %d%s" % [ad, adim_adi, il["sayi"], il["sonraki"], grup],
				"sayi": il["sayi"], "hedef": il["sonraki"], "dugme": toplam}
	for id in c.her_n_by_key.get(key, []):
		var n: int = c.assets[id]["tetikleyici"]["adet"]
		return {"metin": "Her %d'te bahçeye bir kuş gelir · %d / %d" % [n, toplam % n, n],
				"sayi": toplam % n, "hedef": n, "dugme": toplam}
	return {"metin": "Toplam %d" % toplam, "sayi": 0, "hedef": 1, "dugme": toplam}


func _on_olay(o: Dictionary) -> void:
	var c := Game.content
	match o["tur"]:
		"tamamlandi":
			var a: Dictionary = c.assets[o["asset"]]
			if int(o["adet"]) == 1:
				_kart_goster(_asset_karti(a))
			else:
				_bildir("%s (%d)" % [_kisa_ad(a["ad"]), o["adet"]])
		"asama":
			var a: Dictionary = c.assets[o["asset"]]
			_bildir("%s: %s" % [_kisa_ad(a["ad"]), a["asama_adlari"][int(o["asama"]) - 1]])
		"ardisik":
			_bildir(_kisa_ad(c.assets[o["asset"]]["ad"]))
		"kart":
			var es: Dictionary = c.esma[o["esma"]]
			_kart_goster({"baslik": "Yâ " + es["ad"], "arapca": es["arapca"],
				"govde": "Bu isim bahçede bir item değil, öğretici kart olarak kalır. Anlamını büyüklerinle birlikte oku.",
				"alt": "Ebced %d" % es["ebced"]})
		"seri_dondurma":
			_bildir("Seri dondurma kullanıldı; serin sürüyor")
		"seri_yeniden":
			_bildir("Yeni bir seri başladı. Hoş geldin!")


func _asset_karti(a: Dictionary) -> Dictionary:
	var d: Dictionary = a["dayanak"]
	var govde := _buyuk_harfle(str(d["metin"])) if str(d["metin"]) != "" else "-"
	var alt := "%s · Tetikleyici: %s" % [DAYANAK.get(d["kod"], d["kod"]), a["tetikleyici"]["ham"]]
	if a["grup"]:
		alt += "\nAile hedefi: birlikte tamamlanır."
	return {"baslik": _kisa_ad(a["ad"]), "arapca": "", "govde": "Neden bu? " + govde, "alt": alt}


# --------------------------------------------------------------------------
# Kartlar ve bildirim
# --------------------------------------------------------------------------

func _acilis_karti() -> void:
	if Game.senaryo != "":
		return
	var metin := "Zikir Bahçesi bir hatırlatıcıdır. Söylediğin her zikirle bahçene fidan dikilir.\nZikrini Allah için yap; bahçe sana yalnızca eşlik eder."
	if not Game.ilk_acilis:
		metin = "Bahçene hoş geldin."
	_kart_goster({"baslik": "Zikir Bahçesi", "arapca": Game.content.zikirler["bismillah"]["arapca"],
		"govde": metin, "alt": TEMSIL_NOTU, "dugme": "Bismillah ile başla",
		"eylem": func(): Game.tesbih.dokun("bismillah")})


func _kart_goster(k: Dictionary) -> void:
	if Game.kartsiz:
		return
	_kart_kuyrugu.append(k)
	if _kart_kuyrugu.size() == 1:
		_kart_ac(k)


func _kart_ac(k: Dictionary) -> void:
	for ch in _kart_katmani.get_children():
		ch.queue_free()
	_kart_katmani.visible = true
	var c := CenterContainer.new()
	c.set_anchors_preset(Control.PRESET_FULL_RECT)
	_kart_katmani.add_child(c)
	var p := PanelContainer.new()
	p.custom_minimum_size = Vector2(620, 0)
	c.add_child(p)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 14)
	p.add_child(v)
	var bas := _etiket(k["baslik"], 36, 800)
	bas.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(bas)
	if k.get("arapca", "") != "":
		var ar := _etiket(k["arapca"], 38, 500)
		ar.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		v.add_child(ar)
	var g := _etiket(k["govde"], 24, 600)
	g.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	g.custom_minimum_size = Vector2(560, 0)
	v.add_child(g)
	var alt := _etiket(str(k.get("alt", TEMSIL_NOTU)), 19, 500)
	alt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	alt.modulate = Color(1, 1, 1, 0.75)
	v.add_child(alt)
	if not k.has("alt") or k["alt"] != TEMSIL_NOTU:
		var tn := _etiket(TEMSIL_NOTU, 17, 500)
		tn.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		tn.modulate = Color(1, 1, 1, 0.6)
		v.add_child(tn)
	var b := Button.new()
	b.text = k.get("dugme", "Tamam")
	b.custom_minimum_size = Vector2(0, 70)
	b.add_theme_stylebox_override("normal", Tema.kutu(Tema.FIRUZE, 26))
	b.add_theme_color_override("font_color", Color.WHITE)
	b.pressed.connect(_kart_kapat.bind(k))
	v.add_child(b)
	p.scale = Vector2(0.9, 0.9)
	p.pivot_offset = Vector2(310, 200)
	create_tween().tween_property(p, "scale", Vector2.ONE, 0.25).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


func _kart_kapat(k: Dictionary) -> void:
	_kart_kuyrugu.pop_front()
	_kart_katmani.visible = false
	if k.has("eylem"):
		k["eylem"].call()
	if not _kart_kuyrugu.is_empty():
		_kart_ac(_kart_kuyrugu[0])


func _bildir(metin: String) -> void:
	_bildirim.text = metin
	_bildirim.reset_size()
	_bildirim.position.x = (get_viewport().get_visible_rect().size.x - _bildirim.size.x) / 2
	var tw := create_tween()
	_bildirim.modulate.a = 1.0
	tw.tween_interval(1.8)
	tw.tween_property(_bildirim, "modulate:a", 0.0, 0.6)


# --------------------------------------------------------------------------
# Yardımcılar
# --------------------------------------------------------------------------

func _etiket(metin: String, boy: int, kalinlik: int) -> Label:
	var l := Label.new()
	l.text = metin
	l.add_theme_font_size_override("font_size", boy)
	l.add_theme_font_override("font", Tema.yazi(kalinlik))
	return l


func _cip_adi(key: String) -> String:
	if key == "tesbihat":
		return "Tesbihat"
	var ad := Game.content.key_label(key)
	return ad if ad.length() <= 22 else ad.substr(0, 20) + "…"


func _arapca_metni(key: String) -> String:
	var c := Game.content
	if key.begins_with("esma:"):
		var e: Dictionary = c.esma[key.trim_prefix("esma:")]
		return e["arapca"] if e["id"] == "allah" else "يا " + str(e["arapca"])
	var z = c.zikirler.get(key)
	if z and z["arapca"] != null and str(z["arapca"]).length() < 40:
		return z["arapca"]
	return ""


## Türkçe büyük harf: "i" -> "İ" (String.to_upper Türkçe kuralını bilmez).
static func _buyuk_harfle(s: String) -> String:
	if s.is_empty():
		return s
	var ilk := s[0]
	ilk = "İ" if ilk == "i" else ("I" if ilk == "ı" else ilk.to_upper())
	return ilk + s.substr(1)


static func _kisa_ad(ad: String) -> String:
	return ad.get_slice(" (", 0)
