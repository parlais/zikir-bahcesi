extends Node3D
## Cennet mekânı (Faz 2a, K10): ilk katın içi ya da 8 tabakanın dıştan kesiti,
## seçilen stille.
##
##   godot --path game res://scenes/dunya/cennet_sahnesi.tscn -- --zb-anim=nur_ori --zb-kamera=ufuk
##   --zb-anim:   nur_ori (varsayılan: Nur ↔ Ori ışık geçişi, K12-K13) | nur | sky | pixar | yagli_boya
##   --zb-kamera: ufuk | arsa | kesit | model
##   model: tek bir modeli arsanın ortasında inceleme (K15). --zb-model=ZB_bitki_koru_agac
##     --zb-model-aci=30 (bakış yönü, derece) --zb-model-yukseklik=6 (kamera yükseltisi, derece)
##     --zb-model-doluluk=0.85 (modelin kadrajı doldurma oranı)
##   (ekran görüntüsü için ayrıca --zb-ekran=/yol.png --zb-kare=30; Game autoload yakalar)
##
## nur_ori kipinde ışık zemin olarak Nur'dur; zikir tamamlanınca ya da bir olayda
## Ori'ye geçer ve döner (IsikGecisi, IsikKaristirici). Geliştirici için:
##   --zb-isik=0.5                 ışığı sabitler (0 Nur, 1 Ori)
##   --zb-dizi=/yol/onek           Nur'dan Ori'ye geçişi kare kare çeker (onek_00.png ...) ve çıkar
##       --zb-dizi-adim=13 --zb-dizi-bekle=3 --zb-isinma=16
##   --zb-ayar="ortam/parlama/0=0.2;ortam/parlama_kip=screen"   profil değerlerini dener
##   --zb-film=/yol/onek --zb-film-kare=48   kare kare film (tools/render/film.sh, --fixed-fps ile)
##   N tuşu: zikir tamamlanmış gibi geçişi başlatır
##
## Modeller ve yerleşim (game/data/dunya_cennet.json) model fabrikasında üretilir:
##   python3 tools/model_factory/build_all.py dunya
##
## Profilde "filtre" varsa 3B sahne bir SubViewport'a çizilir ve resim_filtresi
## shader'ıyla ekrana boyanır (yağlı boya).

const YERLESIM := "res://data/dunya_cennet.json"
const GOK := "res://scenes/stil/shader/gok_cennet.gdshader"
const FILTRE := "res://scenes/stil/shader/resim_filtresi.gdshader"

const BULUT_RENK := [Color("ffffff"), Color("c8d4f0")]
## Işık, t en az bu kadar değişince yeniden hesaplanır: %0,4'lük renk adımları
## gözle seçilmez, telefonda her karede bütün malzemeleri güncellemek gerekmez.
const ISIK_ADIM := 0.004
## Bu uzaklıktan (arsadan, metre) ötedeki korular hafif ufuk ağacıyla çizilir (K15, üçgen bütçesi).
const UFUK_AGACI_MESAFE := 700.0

var anim := "nur_ori"
var kamera_modu := "ufuk"
var profil: Dictionary
var yer: Dictionary
var k: SahneKurucu
var _vp: Viewport
var _kesit := false
## Işık geçişi (yalnız nur_ori kipinde; diğer stillerde null).
var gecis: IsikGecisi
var _son_t := -1.0
## nur_ori kipinde karışımın iki ucu: [Nur, Ori] (bir kez hesaplanır)
var _uclar: Array = []
## --zb-ayar ile denenen profil değerleri: [yol, değer]
var _ayarlar: Array = []
var _arg := {}
## --zb-kamera=model: incelenen model
var _inceleme_modeli: Node3D


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--zb-") and a.contains("="):
			_arg[a.get_slice("=", 0).trim_prefix("--zb-")] = a.substr(a.find("=") + 1)
	anim = _arg.get("anim", anim)
	kamera_modu = _arg.get("kamera", kamera_modu)
	if kamera_modu == "derece":
		kamera_modu = "kesit"
	_kesit = kamera_modu == "kesit"
	_ayar_coz(_arg.get("ayar", ""))
	if anim == "nur_ori":
		_uclar = [AnimasyonStilleri.al(IsikKaristirici.UC_NUR, _kesit), AnimasyonStilleri.al(IsikKaristirici.UC_ORI, _kesit)]
		gecis = IsikGecisi.new()
		if _arg.has("isik"):
			gecis.zorla(float(_arg["isik"]))
		Game.olay.connect(gecis.olay)
	profil = _profil_hesapla(gecis.t if gecis else 0.0)
	_son_t = gecis.t if gecis else 0.0
	yer = JSON.parse_string(FileAccess.get_file_as_string(YERLESIM))
	k = SahneKurucu.new(self, profil)
	_vp = _filtre_kur() if profil.has("filtre") else get_viewport()
	k.goruntu_kalitesi(_vp)
	k.ortam_kur(GOK)
	if _kesit:
		_kesit_kur()
	else:
		_kat_kur()
	_kamera_kur()
	if gecis and _arg.has("dizi"):
		_dizi_cek.call_deferred(_arg["dizi"])
	elif _arg.has("film"):
		_film_cek.call_deferred(_arg["film"])


# --------------------------------------------------------------------------
# Işık geçişi (K12, K13)
# --------------------------------------------------------------------------

func _profil_hesapla(t: float) -> Dictionary:
	var p := IsikKaristirici.karistir(_uclar[0], _uclar[1], t) if anim == "nur_ori" else AnimasyonStilleri.al(anim, _kesit)
	for a in _ayarlar:
		IsikKaristirici.yaz(p, a[0], a[1])
	return p


func _process(dt: float) -> void:
	if gecis == null:
		return
	gecis.ilerle(dt)
	if absf(gecis.t - _son_t) >= ISIK_ADIM or (gecis.t != _son_t and (gecis.t == 0.0 or gecis.t == 1.0)):
		_isik_uygula(gecis.t)


func _isik_uygula(t: float) -> void:
	_son_t = t
	profil = _profil_hesapla(t)
	k.guncelle(profil)


func _unhandled_input(e: InputEvent) -> void:
	if gecis and e is InputEventKey and e.pressed and not e.echo and (e as InputEventKey).keycode == KEY_N:
		gecis.tetikle("tamamlandi")


## "yol=değer;yol=değer": sayı, #renk, true/false, Color(...) gibi metinler ya da düz metin.
func _ayar_coz(metin: String) -> void:
	for parca in metin.split(";", false):
		var i := parca.find("=")
		if i < 0:
			continue
		var d := parca.substr(i + 1).strip_edges()
		var deger: Variant = d
		if d.is_valid_float():
			deger = float(d)
		elif d.begins_with("#"):
			deger = Color(d)
		elif d == "true" or d == "false":
			deger = d == "true"
		elif d.contains("("):
			deger = str_to_var(d)
		_ayarlar.append([parca.substr(0, i).strip_edges(), deger])


## Geliştirici: Nur'dan Ori'ye geçişi eşit zaman aralıklarıyla kare kare çeker.
## Kareler arasında birkaç kare beklenir ki gökyüzü ışığı ve GI yetişsin.
func _dizi_cek(onek: String) -> void:
	var adim := int(_arg.get("dizi-adim", "13"))
	var bekle := int(_arg.get("dizi-bekle", "3"))
	gecis.zorla(0.0)
	_isik_uygula(0.0)
	for i in int(_arg.get("isinma", "16")):
		await get_tree().process_frame
	for i in adim:
		var faz := float(i) / float(maxi(adim - 1, 1))
		var t := faz * faz * (3.0 - 2.0 * faz)
		gecis.zorla(t)
		_isik_uygula(t)
		for j in bekle:
			await get_tree().process_frame
		var yol := "%s_%02d.png" % [onek, i]
		var err := _vp.get_texture().get_image().save_png(yol)
		print("Dizi karesi: %s t=%.3f (%s)" % [yol, t, error_string(err)])
	get_tree().quit()


## Geliştirici: ısınmadan sonra her kareyi kaydeder. Motor --fixed-fps ile çalıştırılırsa
## kareler eşit zaman adımıyla ilerler (su, parçacık, rüzgâr doğru hızda akar).
func _film_cek(onek: String) -> void:
	for i in int(_arg.get("isinma", "16")):
		await get_tree().process_frame
	for i in int(_arg.get("film-kare", "48")):
		await get_tree().process_frame
		var yol := "%s_%03d.png" % [onek, i]
		var err := _vp.get_texture().get_image().save_png(yol)
		print("Film karesi: %s (%s)" % [yol, error_string(err)])
	get_tree().quit()


## Yağlı boya gibi resim filtreleri: sahne SubViewport'a çizilir, ekrana
## filtreli bir TextureRect olarak basılır. Kök görünüm 3B çizmez.
func _filtre_kur() -> Viewport:
	var sv := SubViewport.new()
	sv.size = get_window().size
	sv.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(sv)
	get_viewport().disable_3d = true
	var mat := ShaderMaterial.new()
	mat.shader = load(FILTRE)
	var f: Dictionary = profil["filtre"]
	for a in f:
		mat.set_shader_parameter(a, f[a])
	var katman := CanvasLayer.new()
	add_child(katman)
	var tr := TextureRect.new()
	tr.texture = sv.get_texture()
	tr.material = mat
	tr.stretch_mode = TextureRect.STRETCH_SCALE
	tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	katman.add_child(tr)
	tr.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return sv


# --------------------------------------------------------------------------
# İlk katın içi: ufka uzanan ova, gökten inen ırmaklar, göğe yükselen merdiven
# --------------------------------------------------------------------------

func _kat_kur() -> void:
	k.ornek("ZB_dunya_cennet", [0, 0, 0, 0, 1])
	k.ornek("ZB_dunya_selaleler", [0, 0, 0, 0, 1])
	for t in yer["su_kosku"]:
		k.ornek("ZB_yapi_su_kosku", t)
	for t in yer["inci_cadir"]:
		k.ornek("ZB_yapi_inci_cadir", t)
	for t in yer["sedir_kosesi"]:
		k.ornek("ZB_yapi_sedir_kosesi", t)
	for t in yer["selsebil"]:
		k.ornek("ZB_yapi_selsebil_cesmesi", t)
	for t in yer["pinar"]:
		var p := k.ornek("ZB_yapi_ab_i_hayat_pinari", t)
		for isaret in p.find_children("fiskiye_*", "", true, false):
			_fiskiye((isaret as Node3D).global_position)
	for t in yer["merdiven"]:
		k.ornek("ZB_yapi_kat_merdiveni", t)
	if kamera_modu == "model":
		_inceleme_modeli = k.ornek(_arg.get("model", "ZB_bitki_koru_agac"), [0, 0, 0, 0, 1])
	else:
		_arsa_kur()
	_bitkiler_kur()
	_gok_kur()
	_parcaciklar_kur()


## Oyuncunun arsası: ışıklı Tûbâ çekirdeği, tek fidan, ilk çiçekler, nur tohumları.
func _arsa_kur() -> void:
	var a: Dictionary = yer["arsa"]
	var nur_renk := k.yol("parcacik/nur_renk")
	var tuba := k.ornek("ZB_agac_tuba_a1", a["tuba"])
	for isaret in tuba.find_children("isik_*", "", true, false):
		var l := OmniLight3D.new()
		k.bagla(l, "light_color", nur_renk)
		l.light_energy = 2.2
		l.omni_range = 5.0
		l.omni_attenuation = 1.6
		l.shadow_enabled = false
		isaret.add_child(l)
		var pos := (isaret as Node3D).global_position
		k.parcacik(40, pos + Vector3(0, 0.25, 0), Vector3(0.35, 0.3, 0.35), 0.05, nur_renk, 3.0,
			Vector3(0, 0.12, 0), 0.08, 4.0)
		_hale(pos, 1.6, nur_renk, 1.2)
	k.coklu("ZB_obje_inci_cakil", yer["inci_cakil"], false)
	for f in a["fidan"]:
		k.ornek(f[5], f.slice(0, 5))
	for c in a["cicek"]:
		k.ornek("ZB_cicek_lale_a3", c)
	for p in a["nur_tohumu"]:
		k.parcacik(10, Vector3(p[0], p[1], p[2]), Vector3(0.2, 0.08, 0.2), 0.04, nur_renk, 3.0,
			Vector3(0, 0.1, 0), 0.05, 3.0)


func _bitkiler_kur() -> void:
	k.coklu("ZB_agac_sidr_a4", yer["sidr"])
	k.coklu("ZB_agac_uzum_a4", yer["uzum"])
	k.coklu("ZB_agac_hurma_a4", yer["hurma"])
	k.coklu("ZB_agac_talh_a4", yer["talh"])
	k.coklu("ZB_bitki_nar", yer["nar"])
	k.coklu("ZB_bitki_selvi", yer["selvi"])
	k.coklu("ZB_bitki_gul_cali", yer["gul"])
	k.coklu("ZB_bitki_lale_tarhi", yer["lale"], false)
	k.coklu("ZB_bitki_koru_agac", yer["koru"], true, 60.0)
	# Uzak korular: 700 m'ye kadar dallı hafif ağaç, ötesinde (dikey ekranda birkaç piksel) ufuk ağacı
	var yakin_uzak := []
	var ufuk := []
	for t in yer["uzak_agac"]:
		(yakin_uzak if Vector2(t[0], t[2]).length() < UFUK_AGACI_MESAFE else ufuk).append(t)
	k.coklu("ZB_bitki_uzak_agac", yakin_uzak, false, 250.0)
	k.coklu("ZB_bitki_ufuk_agaci", ufuk, false, 500.0)
	k.coklu("ZB_bitki_cimen", _cimen_konumlari(), false)


## Gökteki bulut kümeleri: çağlayanların indiği bulutlar, merdivenin ucunu saran
## bulut ve ışık, ufuk üstünde süzülen birkaç küme. Üst tabaka görünmez (K10).
func _gok_kur() -> void:
	var nur_renk := k.yol("parcacik/nur_renk")
	var i := 0
	for s in yer["gok_selale"]:
		var g: float = s[3]
		# Perdenin başı bulutun içinden çıksın: bulutun altı perdenin tepesini örter
		_bulut_kumesi(Vector3(s[0], s[1] + 15.0, s[2]), g * 6.0, 46, 50 + i, 2.2)
		_hale(Vector3(s[0], s[1] - 10.0, s[2]), g * 5.0, nur_renk, 0.5)
		i += 1
	var u: Array = yer["merdiven_ust"]
	var ust := Vector3(u[0], u[1], u[2])
	_bulut_kumesi(ust + Vector3(0, 18, 0), 220.0, 40, 90)
	_hale(ust + Vector3(0, 25, 0), 260.0, nur_renk, 1.0)
	var rng := RandomNumberGenerator.new()
	rng.seed = 7
	for j in 9:
		var a := rng.randf_range(-1.2, 1.2)
		var r := rng.randf_range(900.0, 2600.0)
		_bulut_kumesi(Vector3(sin(a) * r, rng.randf_range(260.0, 520.0), -cos(a) * r), rng.randf_range(160.0, 320.0),
			18, 120 + j)


## Çimen tutamları: model fabrikasının yazdığı 1 m'lik ızgaradan (yükseklik ve
## çimen ağırlığı). Yoğunluk arsa çevresinde yüksek, uzaklaştıkça azalır.
func _cimen_konumlari() -> Array:
	var iz: Dictionary = yer["izgara"]
	var nx: int = iz["nx"]
	var nz: int = iz["nz"]
	var x0: float = iz["x0"]
	var z0: float = iz["z0"]
	var ys: Array = iz["y_cm"]
	var ws: Array = iz["cimen"]
	var out: Array = []
	var rng := RandomNumberGenerator.new()
	rng.seed = 11
	for j in nz - 1:
		for i in nx - 1:
			var w: float = ws[j * nx + i] / 9.0
			if w < 0.5:
				continue
			var cx := x0 + i + 0.5
			var cz := z0 + j + 0.5
			var d := Vector2(cx, cz - 6.0).length()
			var yog := lerpf(7.0, 1.2, clampf((d - 18.0) / 30.0, 0.0, 1.0))
			if d > 55.0:
				yog = 0.3
			var n := int(yog * w + rng.randf())
			for s in n:
				var fx := rng.randf()
				var fz := rng.randf()
				var y00: float = ys[j * nx + i]
				var y10: float = ys[j * nx + i + 1]
				var y01: float = ys[(j + 1) * nx + i]
				var y11: float = ys[(j + 1) * nx + i + 1]
				var y := lerpf(lerpf(y00, y10, fx), lerpf(y01, y11, fx), fz) / 100.0
				out.append([x0 + i + fx, y - 0.03, z0 + j + fz, rng.randf_range(0, 360), rng.randf_range(0.55, 1.0)])
	return out


func _fiskiye(pos: Vector3) -> void:
	var f := k.parcacik(220, pos, Vector3(0.03, 0.03, 0.03), 0.045, Color(0.88, 0.97, 1.0), 0.3,
		Vector3(0, -6.0, 0), 2.6, 0.85)
	var fm := f.process_material as ParticleProcessMaterial
	fm.direction = Vector3.UP
	fm.spread = 12.0
	fm.turbulence_enabled = false


func _parcaciklar_kur() -> void:
	# Havada süzülen nur zerreleri (Müslim, Cennet 14-22: ışık her şeyden hafifçe yayılır).
	# Geçişte sayı amount_ratio ile değişir: en çok zerre baştan kurulur.
	var en_cok := _en_cok_zerre()
	if en_cok > 0:
		var z := k.parcacik(en_cok, Vector3(-8, 3.5, -40), Vector3(36, 3.0, 36), 0.05, k.yol("parcacik/nur_renk"), 2.5,
			Vector3(0, 0.03, 0), 0.08, 14.0)
		k.bagla(z, "amount_ratio", func(p: Dictionary) -> float: return float(p["parcacik"]["nur"]) / en_cok)
	# Gökten inen çağlayanların dibi: ağaçların üstüne taşan, ışıkta parlayan kabarık su
	# sisi (bulut dokulu). Perdenin çevresindeki serpintiyi selale_pus zarfı verir.
	var sis_renk := func(p: Dictionary) -> Color:
		return p["parcacik"].get("selale_sis", p["parcacik"]["sis_renk"])
	for s in yer["selale_dip"]:
		var g: float = s[3]
		k.parcacik(45, Vector3(s[0], s[1] + g * 0.8, s[2]), Vector3(g * 1.2, g * 0.6, g * 0.8), g * 1.6, sis_renk,
			0.0, Vector3(0, 0.7, 0), 1.2, 16.0, BaseMaterial3D.BILLBOARD_ENABLED, _bulut_doku())
	# Selsebil levhasının dibinde ince serpinti
	for t in yer["selsebil"]:
		var y := Vector3(t[0], t[1] + 0.6, t[2])
		k.parcacik(30, y + Basis(Vector3.UP, deg_to_rad(t[3])) * Vector3(0, 0, 1.2), Vector3(0.5, 0.05, 0.2), 0.03,
			Color(0.9, 0.97, 1.0), 0.4, Vector3(0, -1.0, 0), 0.3, 1.2)


func _en_cok_zerre() -> int:
	if anim != "nur_ori":
		return int(profil["parcacik"]["nur"])
	return maxi(int(_uclar[0]["parcacik"]["nur"]), int(_uclar[1]["parcacik"]["nur"]))


# --------------------------------------------------------------------------
# Dıştan kesit: uzanıp giden 8 tabaka (K10)
# --------------------------------------------------------------------------

func _kesit_kur() -> void:
	var kesit := k.ornek("ZB_dunya_kesit", [0, 0, 0, 0, 1])
	# Bütün tabakalar aynı ışığı alır: üstteki tabaka alttakine gölge düşürmez
	for mi in kesit.find_children("*", "MeshInstance3D", true, false):
		(mi as GeometryInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var ks: Dictionary = yer["kesit"]
	k.coklu("ZB_bitki_ufuk_agaci", ks["agac"], false)
	var i := 0
	for b in ks["bulut"]:
		_bulut_kumesi(Vector3(b[0], b[1], b[2]), b[3], 14, 300 + i, 1.8)
		i += 1
	# Tavanların altında ince bulut kuşağı: içeriden bakınca üst tabaka görünmez
	var kat: int = ks["kat"]
	var kh: float = ks["kat_h"]
	var rng := RandomNumberGenerator.new()
	rng.seed = 5
	for kk in range(1, kat):
		for j in 9:
			_bulut_kumesi(Vector3(rng.randf_range(-4200, 4200), kk * kh - 22.0, rng.randf_range(-1150, -150)),
				rng.randf_range(260.0, 420.0), 10, 400 + kk * 20 + j, 2.2)
	# Firdevs'in üstü: her şeyi kuşatan ışık (Arş tasvir edilmez)
	var nur_renk := k.yol("parcacik/nur_renk")
	for isaret in kesit.find_children("isik_*", "", true, false):
		var pos := (isaret as Node3D).global_position
		var l := OmniLight3D.new()
		k.bagla(l, "light_color", nur_renk)
		l.light_energy = 6.0
		l.omni_range = 1400.0
		l.omni_attenuation = 1.3
		isaret.add_child(l)
		_hale(pos + Vector3(0, 60, 0), 5200.0, nur_renk, 0.75, true)
		_huzme(pos + Vector3(0, 900, 0), Vector2(900, 1900), nur_renk, 0.7)
		k.parcacik(300, pos + Vector3(0, 150, 0), Vector3(1600, 120, 900), 12.0, nur_renk, 3.0,
			Vector3(0, 8.0, 0), 5.0, 30.0)


# --------------------------------------------------------------------------
# Bulut, hale, hüzme
# --------------------------------------------------------------------------

var _bulut_doku_onbellek: Texture2D


## Kabarık bulut dokusu: düzensiz kenarlı, tepesi aydınlık, altı hafif gölgeli (bir kez üretilir).
func _bulut_doku() -> Texture2D:
	if _bulut_doku_onbellek:
		return _bulut_doku_onbellek
	var n := FastNoiseLite.new()
	n.seed = 3
	n.frequency = 0.035
	n.fractal_octaves = 4
	var boy := 128
	var img := Image.create(boy, boy, false, Image.FORMAT_RGBA8)
	for y in boy:
		for x in boy:
			var u := (float(x) / boy - 0.5) * 2.0
			var v := (float(y) / boy - 0.5) * 2.0
			var r := sqrt(u * u + v * v * 1.3)
			var g := n.get_noise_2d(x, y) * 0.5 + 0.5
			var a := clampf((1.0 - r) * 1.8 + (g - 0.5) * 0.9 - 0.2, 0.0, 1.0)
			a = a * a * (3.0 - 2.0 * a)
			var isik := clampf(0.78 + 0.3 * (-v) + (g - 0.5) * 0.25, 0.6, 1.08)
			img.set_pixel(x, y, Color(isik, isik, isik * 0.99, a))
	_bulut_doku_onbellek = ImageTexture.create_from_image(img)
	return _bulut_doku_onbellek


## Kabarık bulut billboard'larından küme: tepesi sıcak beyaz, altı gölgeli.
## yatay: kümenin yatayda ne kadar yayıldığı (1 yuvarlak, 3 uzun bulut şeridi).
func _bulut_kumesi(merkez: Vector3, boyut: float, adet: int, tohum: int, yatay := 1.0) -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = tohum
	var doku := _bulut_doku()
	for i in adet:
		var o := Vector3(rng.randf_range(-0.75, 0.75) * yatay, rng.randf_range(-0.22, 0.28), rng.randf_range(-0.5, 0.5)) * boyut
		var s := boyut * rng.randf_range(0.5, 0.9) * (1.0 - 0.4 * absf(o.x) / (boyut * yatay))
		var q := QuadMesh.new()
		q.size = Vector2(s, s * 0.8)
		var m := StandardMaterial3D.new()
		m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		m.albedo_texture = doku
		var yuk := clampf(o.y / (boyut * 0.3) * 0.5 + 0.5, 0.0, 1.0)
		var f := yuk * 0.8 + rng.randf() * 0.2
		var renk_fn := func(p: Dictionary) -> Color:
			var r: Array = p.get("bulut_renk", BULUT_RENK)
			var c: Color = (r[1] as Color).lerp(r[0], f)
			c.a = 0.72
			return c
		k.bagla(m, "albedo_color", renk_fn)
		q.material = m
		var mi := MeshInstance3D.new()
		mi.mesh = q
		mi.position = merkez + o
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(mi)


var _isik_doku_onbellek: Texture2D


## Kenarı belirsiz parıltı dokusu (üstel sönüm): hale düz bir disk gibi görünmesin.
func _isik_doku() -> Texture2D:
	if _isik_doku_onbellek:
		return _isik_doku_onbellek
	var boy := 128
	var img := Image.create(boy, boy, false, Image.FORMAT_RGBA8)
	for y in boy:
		for x in boy:
			var u := (float(x) / boy - 0.5) * 2.0
			var v := (float(y) / boy - 0.5) * 2.0
			var r2 := u * u + v * v
			var a := clampf(exp(-r2 * 5.0) * 0.8 + exp(-r2 * 30.0) * 0.4 - 0.0067, 0.0, 1.0)
			img.set_pixel(x, y, Color(1, 1, 1, a))
	_isik_doku_onbellek = ImageTexture.create_from_image(img)
	return _isik_doku_onbellek


## Işık halesi: her yöne bakan yumuşak, eklemeli parıltı. renk: Color ya da k.yol(...).
func _hale(pos: Vector3, boy: float, renk: Variant, guc: float, yumusak := false) -> void:
	var q := QuadMesh.new()
	q.size = Vector2(boy, boy)
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.albedo_texture = _isik_doku() if yumusak else k.yuvarlak_doku()
	_renk_bagla(m, renk, guc)
	m.disable_fog = true
	q.material = m
	var mi := MeshInstance3D.new()
	mi.mesh = q
	mi.position = pos
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mi)


## Göğe uzanan dikey ışık hüzmesi (Arş tasvir edilmez; ışık yukarıda söner).
func _huzme(pos: Vector3, boyut: Vector2, renk: Variant, guc: float) -> void:
	var img := Image.create(64, 256, false, Image.FORMAT_RGBA8)
	for y in 256:
		var v := float(y) / 255.0
		for x in 64:
			var u := (float(x) / 63.0 - 0.5) * 2.0
			var a := exp(-u * u * 4.0) * pow(v, 1.8) * (1.0 - pow(1.0 - v, 12.0))
			img.set_pixel(x, y, Color(1, 1, 1, a))
	var q := QuadMesh.new()
	q.size = boyut
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.billboard_mode = BaseMaterial3D.BILLBOARD_FIXED_Y
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.albedo_texture = ImageTexture.create_from_image(img)
	_renk_bagla(m, renk, guc)
	m.disable_fog = true
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	q.material = m
	var mi := MeshInstance3D.new()
	mi.mesh = q
	mi.position = pos
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mi)


func _renk_bagla(m: BaseMaterial3D, renk: Variant, guc: float) -> void:
	if renk is Callable:
		k.bagla(m, "albedo_color", func(p: Dictionary) -> Color: return (renk as Callable).call(p) * guc)
	else:
		m.albedo_color = renk * guc


# --------------------------------------------------------------------------
# Kamera
# --------------------------------------------------------------------------

func _kamera_kur() -> void:
	var tanim: Dictionary = yer["kameralar"].get(kamera_modu, yer["kameralar"]["ufuk"])
	var kam := Camera3D.new()
	if _vp is SubViewport:
		_vp.add_child(kam)
	else:
		add_child(kam)
	var kn: Array = tanim["konum"]
	var hd: Array = tanim["hedef"]
	kam.position = Vector3(kn[0], kn[1], kn[2])
	kam.look_at(Vector3(hd[0], hd[1], hd[2]))
	kam.fov = tanim["fov"]
	if _inceleme_modeli:
		_model_kamerasi(kam)
	kam.near = 0.15
	kam.far = 40000.0 if kamera_modu == "kesit" else 12000.0
	var ayar := CameraAttributesPractical.new()
	if kamera_modu == "arsa":
		ayar.dof_blur_far_enabled = true
		ayar.dof_blur_far_distance = 140.0
		ayar.dof_blur_far_transition = 300.0
		ayar.dof_blur_amount = 0.025
	kam.attributes = ayar
	kam.current = true


## İnceleme kamerası: modelin sınır kutusunu dikey ya da yatay kadraja sığdırır.
func _model_kamerasi(kam: Camera3D) -> void:
	var kutu := AABB()
	var ilk := true
	for mi in _inceleme_modeli.find_children("*", "MeshInstance3D", true, false):
		var b: AABB = (mi as MeshInstance3D).global_transform * (mi as MeshInstance3D).get_aabb()
		kutu = b if ilk else kutu.merge(b)
		ilk = false
	var aci := deg_to_rad(float(_arg.get("model-aci", "30")))
	var yuk := deg_to_rad(float(_arg.get("model-yukseklik", "6")))
	var dolu := float(_arg.get("model-doluluk", "0.85"))
	kam.fov = 40.0
	var boyut := Vector2(get_window().size)
	var oran := boyut.x / boyut.y
	var dik := tan(deg_to_rad(kam.fov) * 0.5)
	var yan := dik * oran
	var genis := maxf(kutu.size.x, kutu.size.z)
	var uzak := maxf(kutu.size.y * 0.5 / dik, genis * 0.5 / yan) / dolu + genis * 0.5
	var merkez := kutu.get_center()
	var yon := Vector3(sin(aci) * cos(yuk), sin(yuk), cos(aci) * cos(yuk))
	kam.position = merkez + yon * uzak
	kam.look_at(merkez)
