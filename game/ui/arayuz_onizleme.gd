class_name ArayuzOnizleme
extends CanvasLayer
## Yeni arayüz tasarımının stil önizlemesi (stil karşılaştırma sahnesi için).
## Büyük opak panel yerine sahnenin üstünde süzülen öğeler: altta yumuşak bir
## perde, hat yazısıyla Arapça söz, 33 taneli tesbih halkası, simgeli kaynak
## göstergeleri. Renkler ve yazı tipleri stil profilinin "arayuz" alanından gelir.

var profil: Dictionary
var _a: Dictionary

const ORNEK_SAYI := 23
const ORNEK_HEDEF := 33


func _ready() -> void:
	_a = profil["arayuz"]
	var kok := Control.new()
	kok.set_anchors_preset(Control.PRESET_FULL_RECT)
	kok.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(kok)
	_perde(kok)
	_ust(kok)
	_alt(kok)


func _latin(kalinlik := 600) -> Font:
	var ad: String = _a["latin"]
	var nunito: FontFile = load("res://assets/fonts/Nunito.ttf")
	var amiri: FontFile = load("res://assets/fonts/Amiri-Bold.ttf")
	if ad == "Nunito":
		var f := FontVariation.new()
		f.base_font = nunito
		f.variation_opentype = {TextServerManager.get_primary_interface().name_to_tag("wght"): kalinlik}
		f.fallbacks = [amiri]
		return f
	var ff: FontFile = load("res://assets/fonts/%s.ttf" % ad).duplicate()
	ff.fallbacks = [nunito, amiri]
	return ff


func _arapca_yazi() -> Font:
	var f: FontFile = load("res://assets/fonts/Amiri-Bold.ttf")
	return f


func _etiket(metin: String, font: Font, boy: int, renk: Color, golge := true) -> Label:
	var l := Label.new()
	l.text = metin
	l.add_theme_font_override("font", font)
	l.add_theme_font_size_override("font_size", boy)
	l.add_theme_color_override("font_color", renk)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	if golge and _a["golge"].a > 0.0:
		l.add_theme_color_override("font_shadow_color", _a["golge"])
		l.add_theme_constant_override("shadow_offset_x", 0)
		l.add_theme_constant_override("shadow_offset_y", 2)
		l.add_theme_constant_override("shadow_outline_size", 6 if boy > 30 else 3)
	return l


func _cam_kutu(yaricap := 40, kenar := 2) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = _a["cam"]
	s.set_corner_radius_all(yaricap)
	s.set_border_width_all(kenar)
	s.border_color = _a["cerceve"]
	s.content_margin_left = 22
	s.content_margin_right = 22
	s.content_margin_top = 10
	s.content_margin_bottom = 10
	s.shadow_color = Color(0, 0, 0, 0.18)
	s.shadow_size = 12
	s.anti_aliasing = true
	return s


func _perde(kok: Control) -> void:
	var g := Gradient.new()
	var p: Color = _a["perde"]
	g.set_color(0, Color(p, 0.0))
	g.add_point(0.45, Color(p, 0.35))
	g.set_color(g.get_point_count() - 1, Color(p, 0.9))
	var t := GradientTexture2D.new()
	t.gradient = g
	t.fill_from = Vector2(0, 0)
	t.fill_to = Vector2(0, 1)
	var r := TextureRect.new()
	r.texture = t
	r.stretch_mode = TextureRect.STRETCH_SCALE
	r.anchor_left = 0
	r.anchor_right = 1
	r.anchor_top = 0.46
	r.anchor_bottom = 1
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	kok.add_child(r)
	var ust := TextureRect.new()
	var g2 := Gradient.new()
	g2.set_color(0, Color(p, 0.45))
	g2.set_color(1, Color(p, 0.0))
	var t2 := GradientTexture2D.new()
	t2.gradient = g2
	t2.fill_from = Vector2(0, 0)
	t2.fill_to = Vector2(0, 1)
	ust.texture = t2
	ust.stretch_mode = TextureRect.STRETCH_SCALE
	ust.anchor_right = 1
	ust.anchor_bottom = 0.12
	kok.add_child(ust)


func _ust(kok: Control) -> void:
	var m := MarginContainer.new()
	m.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	for k in ["left", "right"]:
		m.add_theme_constant_override("margin_" + k, 30)
	m.add_theme_constant_override("margin_top", 38)
	kok.add_child(m)
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", 14)
	m.add_child(h)
	var seri := PanelContainer.new()
	seri.add_theme_stylebox_override("panel", _cam_kutu(30))
	var sh := HBoxContainer.new()
	sh.add_theme_constant_override("separation", 8)
	var ikon := Simge.new()
	ikon.tur = "yaprak"
	ikon.renk = _a["vurgu"]
	ikon.custom_minimum_size = Vector2(30, 30)
	sh.add_child(ikon)
	sh.add_child(_etiket("7 gün", _latin(800), 26, _a["metin"]))
	seri.add_child(sh)
	h.add_child(seri)
	var bos := Control.new()
	bos.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	h.add_child(bos)
	for g in [["hava", 0.8], ["su", 0.62], ["isik", 0.45], ["rizik", 0.7]]:
		var gs := Gosterge.new()
		gs.tur = g[0]
		gs.deger = g[1]
		gs.a = _a
		gs.custom_minimum_size = Vector2(62, 62)
		h.add_child(gs)
	var ayar := Gosterge.new()
	ayar.tur = "ayar"
	ayar.a = _a
	ayar.custom_minimum_size = Vector2(62, 62)
	h.add_child(ayar)


func _alt(kok: Control) -> void:
	var v := VBoxContainer.new()
	v.anchor_left = 0
	v.anchor_right = 1
	v.anchor_top = 1
	v.anchor_bottom = 1
	v.offset_left = 28
	v.offset_right = -28
	v.offset_bottom = -44
	v.grow_vertical = Control.GROW_DIRECTION_BEGIN
	v.alignment = BoxContainer.ALIGNMENT_END
	v.add_theme_constant_override("separation", 6)
	kok.add_child(v)

	var cipler := HBoxContainer.new()
	cipler.alignment = BoxContainer.ALIGNMENT_CENTER
	cipler.add_theme_constant_override("separation", 10)
	for c in [["Allah", false], ["Yâ Nûr", false], ["Sübhânallâhi'l-azîm", true], ["Lâ havle", false]]:
		var p := PanelContainer.new()
		var st := _cam_kutu(28, 2 if c[1] else 1)
		if c[1]:
			st.bg_color = Color(_a["vurgu"], 0.9)
			st.border_color = _a["vurgu"]
		p.add_theme_stylebox_override("panel", st)
		var renk: Color = _a["dugme_ic"] if c[1] and _a["dugme_ic"].get_luminance() < 0.5 else _a["metin"]
		if c[1]:
			renk = Color("1b1408") if _a["vurgu"].get_luminance() > 0.5 else Color.WHITE
		p.add_child(_etiket(c[0], _latin(700), 22, renk, false))
		cipler.add_child(p)
	v.add_child(cipler)

	if _a["susleme"]:
		var s := Susleme.new()
		s.renk = _a["cerceve"]
		s.custom_minimum_size = Vector2(0, 34)
		v.add_child(s)
	else:
		var bos := Control.new()
		bos.custom_minimum_size = Vector2(0, 14)
		v.add_child(bos)

	var z: Dictionary = Game.content.zikirler["subhanallahil_azim"]
	v.add_child(_etiket(z["arapca"], _arapca_yazi(), 66, _a["metin"]))
	v.add_child(_etiket(z["ad"], _latin(800), 34, _a["metin"]))
	var anlam := _etiket(z["anlam"], _latin(500), 22, Color(_a["metin"], 0.85))
	v.add_child(anlam)

	var orta := CenterContainer.new()
	var halka := TesbihHalkasi.new()
	halka.a = _a
	halka.sayi = ORNEK_SAYI
	halka.hedef = ORNEK_HEDEF
	halka.font = _latin(800)
	halka.custom_minimum_size = Vector2(300, 300)
	orta.add_child(halka)
	v.add_child(orta)
	v.add_child(_etiket("Hurma ağacı · fidan olmasına %d zikir kaldı" % (ORNEK_HEDEF - ORNEK_SAYI), _latin(600), 22,
		Color(_a["metin"], 0.9)))


# --------------------------------------------------------------------------
# Çizilen öğeler
# --------------------------------------------------------------------------

class TesbihHalkasi:
	extends Control
	## 33 taneli tesbih halkası: çekilen her zikirde bir tane yanar, altın yay ilerler.
	var a: Dictionary
	var sayi := 0
	var hedef := 33
	var font: Font

	func _draw() -> void:
		var c := size / 2
		var R := minf(size.x, size.y) / 2 - 8
		var vurgu: Color = a["vurgu"]
		for i in 6:
			draw_circle(c, R + 6 - i * 2, Color(vurgu, 0.035))
		draw_circle(c, R - 30, a["dugme_dis"])
		draw_circle(c, R - 38, a["dugme_ic"])
		draw_arc(c, R - 52, deg_to_rad(200), deg_to_rad(340), 48, Color(1, 1, 1, 0.22), 10, true)
		draw_arc(c, R, 0, TAU, 128, Color(a["cerceve"], 0.35), 4, true)
		var oran := float(sayi) / hedef
		draw_arc(c, R, -PI / 2, -PI / 2 + TAU * oran, 128, vurgu, 7, true)
		for i in hedef:
			var aci := -PI / 2 + TAU * (i + 0.5) / hedef
			var p := c + Vector2(cos(aci), sin(aci)) * (R - 17)
			if i < sayi:
				draw_circle(p, 10, Color(vurgu, 0.25))
				draw_circle(p, 7, vurgu)
				draw_circle(p + Vector2(-2, -2), 2.4, Color(1, 1, 1, 0.7))
			else:
				draw_circle(p, 6, Color(a["cerceve"], 0.3))
		var yazi := str(sayi)
		var metin_renk: Color = Color.WHITE if Color(a["dugme_ic"]).get_luminance() < 0.5 else Color("2a2014")
		var boy := 84
		var s := font.get_string_size(yazi, HORIZONTAL_ALIGNMENT_CENTER, -1, boy)
		draw_string(font, c + Vector2(-s.x / 2, s.y * 0.28), yazi, HORIZONTAL_ALIGNMENT_LEFT, -1, boy, metin_renk)
		var alt := "/ %d" % hedef
		var s2 := font.get_string_size(alt, HORIZONTAL_ALIGNMENT_CENTER, -1, 26)
		draw_string(font, c + Vector2(-s2.x / 2, 62), alt, HORIZONTAL_ALIGNMENT_LEFT, -1, 26, Color(metin_renk, 0.7))


class Gosterge:
	extends Control
	## Simgeli halka gösterge: hava, su, ışık, rızık (veya ayar düğmesi).
	var a: Dictionary
	var tur := "hava"
	var deger := 0.5

	func _draw() -> void:
		var c := size / 2
		var R := minf(size.x, size.y) / 2 - 2
		draw_circle(c, R, a["cam"])
		draw_arc(c, R - 1, 0, TAU, 64, Color(a["cerceve"], 0.6), 2, true)
		var v: Color = a["vurgu"]
		if tur != "ayar":
			draw_arc(c, R - 5, -PI / 2, -PI / 2 + TAU * deger, 64, v, 4, true)
		Simge.ciz(self, tur if tur != "ayar" else "yildiz", c, R * 0.46, a["metin"])


class Simge:
	extends Control
	var tur := "yaprak"
	var renk := Color.WHITE

	func _draw() -> void:
		Simge.ciz(self, tur, size / 2, minf(size.x, size.y) * 0.42, renk)

	static func ciz(ci: CanvasItem, tur: String, c: Vector2, r: float, renk: Color) -> void:
		match tur:
			"hava":
				for i in 3:
					var y := c.y - r * 0.5 + i * r * 0.5
					ci.draw_arc(Vector2(c.x - r * 0.2 + i * r * 0.15, y), r * 0.45, PI * 1.1, PI * 2.05, 16, renk, 2.2, true)
			"su":
				# Damla: altta yarım daireden fazlası, tepede sivri uç
				var pts := PackedVector2Array()
				var m := c + Vector2(0, r * 0.25)
				for i in 17:
					var aci := -PI * 0.2 + PI * 1.4 * i / 16.0
					pts.append(m + Vector2(cos(aci), sin(aci)) * r * 0.62)
				pts.append(c + Vector2(0, -r * 1.0))
				ci.draw_colored_polygon(pts, renk)
			"isik", "yildiz":
				var pts := PackedVector2Array()
				for i in 16:
					var aci := -PI / 2 + PI * i / 8.0
					var rr := r if i % 2 == 0 else r * 0.55
					pts.append(c + Vector2(cos(aci), sin(aci)) * rr)
				ci.draw_colored_polygon(pts, renk)
			"rizik":
				ci.draw_circle(c + Vector2(0, r * 0.15), r * 0.72, renk)
				var tac := PackedVector2Array([c + Vector2(-r * 0.35, -r * 0.45), c + Vector2(-r * 0.2, -r * 0.95),
					c + Vector2(0, -r * 0.6), c + Vector2(r * 0.2, -r * 0.95), c + Vector2(r * 0.35, -r * 0.45)])
				ci.draw_colored_polygon(tac, renk)
			"yaprak":
				var pts := PackedVector2Array()
				for i in 13:
					var t := float(i) / 12.0
					pts.append(c + Vector2(sin(t * PI) * r * 0.55, (t - 0.5) * r * 2.0).rotated(0.5))
				for i in 13:
					var t := 1.0 - float(i) / 12.0
					pts.append(c + Vector2(-sin(t * PI) * r * 0.55, (t - 0.5) * r * 2.0).rotated(0.5))
				ci.draw_colored_polygon(pts, renk)


class Susleme:
	extends Control
	## Tezhip çizgisi: iki ince altın hat, ortada sekiz köşeli yıldız, yanlarda noktalar.
	var renk := Color.GOLD

	func _draw() -> void:
		var c := size / 2
		var w := size.x * 0.36
		for dy in [-3.0, 3.0]:
			draw_line(c + Vector2(-w, dy), c + Vector2(-22, dy), Color(renk, 0.8), 1.5, true)
			draw_line(c + Vector2(22, dy), c + Vector2(w, dy), Color(renk, 0.8), 1.5, true)
		Simge.ciz(self, "yildiz", c, 15, renk)
		draw_circle(c, 4, Color(0.05, 0.08, 0.25))
		for s in [-1.0, 1.0]:
			for k in 3:
				draw_circle(c + Vector2(s * (w + 10 + k * 12), 0), 3.0 - k * 0.6, Color(renk, 0.9 - k * 0.25))
			Simge.ciz(self, "yildiz", c + Vector2(s * w * 0.55, 0), 7, Color(renk, 0.9))
