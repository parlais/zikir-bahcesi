class_name Tema
extends RefCounted
## Arayüz teması: çocuk dostu büyük yazı, yuvarlak köşeler, bahçe paleti.
## Yazı tipi Nunito; Arapça harfler için Noto Naskh Arabic yedek yazı tipidir.

const KREM := Color("f6efe0")
const KREM_KOYU := Color("e8dcc2")
const MUREKKEP := Color("3a2e22")
const FIRUZE := Color("2ca4a0")
const FIRUZE_KOYU := Color("1f7d7a")
const ALTIN := Color("d9a441")
const MERCAN := Color("c8443a")
const YESIL := Color("5f9e48")

static var _tema: Theme


static func yazi(kalinlik := 600) -> Font:
	var ana: FontFile = load("res://assets/fonts/Nunito.ttf")
	var arapca: FontFile = load("res://assets/fonts/NotoNaskhArabic.ttf")
	var f := FontVariation.new()
	f.base_font = ana
	f.variation_opentype = {TextServerManager.get_primary_interface().name_to_tag("wght"): kalinlik}
	f.fallbacks = [arapca]
	return f


static func kutu(renk: Color, yaricap := 22, kenar := 0, kenar_renk := Color.TRANSPARENT, ic := 14) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = renk
	s.set_corner_radius_all(yaricap)
	s.set_border_width_all(kenar)
	s.border_color = kenar_renk
	s.content_margin_left = ic
	s.content_margin_right = ic
	s.content_margin_top = ic * 0.6
	s.content_margin_bottom = ic * 0.6
	s.anti_aliasing = true
	return s


static func al() -> Theme:
	if _tema:
		return _tema
	var t := Theme.new()
	t.default_font = yazi(600)
	t.default_font_size = 26
	t.set_color("font_color", "Label", MUREKKEP)
	t.set_stylebox("normal", "Button", kutu(KREM, 26, 3, KREM_KOYU))
	t.set_stylebox("hover", "Button", kutu(KREM_KOYU, 26, 3, KREM_KOYU))
	t.set_stylebox("pressed", "Button", kutu(FIRUZE, 26, 3, FIRUZE_KOYU))
	t.set_stylebox("focus", "Button", StyleBoxEmpty.new())
	t.set_stylebox("disabled", "Button", kutu(KREM_KOYU, 26))
	t.set_color("font_color", "Button", MUREKKEP)
	t.set_color("font_hover_color", "Button", MUREKKEP)
	t.set_color("font_pressed_color", "Button", Color.WHITE)
	t.set_color("font_focus_color", "Button", MUREKKEP)
	t.set_stylebox("panel", "PanelContainer", kutu(Color(KREM, 0.96), 28, 0, Color.TRANSPARENT, 24))
	t.set_stylebox("background", "ProgressBar", kutu(KREM_KOYU, 10, 0, Color.TRANSPARENT, 0))
	t.set_stylebox("fill", "ProgressBar", kutu(FIRUZE, 10, 0, Color.TRANSPARENT, 0))
	t.set_color("font_color", "CheckButton", MUREKKEP)
	_tema = t
	return t
