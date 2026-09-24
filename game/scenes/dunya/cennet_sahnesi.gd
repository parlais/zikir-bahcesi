extends Node3D
## Cennet mekânı (Faz 2a): ilk katın içi ya da katlı koni-dağın dış görünümü,
## seçilen animasyon stiliyle.
##
##   godot --path game res://scenes/dunya/cennet_sahnesi.tscn -- --zb-anim=pixar --zb-kamera=ufuk
##   --zb-anim:   pixar | ghibli | arcane | sky
##   --zb-kamera: ufuk | arsa | derece
##   (ekran görüntüsü için ayrıca --zb-ekran=/yol.png --zb-kare=30; Game autoload yakalar)
##
## Modeller ve yerleşim (game/data/dunya_cennet.json) model fabrikasında üretilir:
##   python3 tools/model_factory/build_all.py dunya

const YERLESIM := "res://data/dunya_cennet.json"
const GOK := "res://scenes/stil/shader/gok_cennet.gdshader"
const BULUT := "res://scenes/stil/shader/bulut_denizi.gdshader"

var anim := "pixar"
var kamera_modu := "ufuk"
var profil: Dictionary
var yer: Dictionary
var k: SahneKurucu


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--zb-anim="):
			anim = a.get_slice("=", 1)
		elif a.begins_with("--zb-kamera="):
			kamera_modu = a.get_slice("=", 1)
	var derece := kamera_modu == "derece"
	profil = AnimasyonStilleri.al(anim, derece)
	yer = JSON.parse_string(FileAccess.get_file_as_string(YERLESIM))
	k = SahneKurucu.new(self, profil)
	k.goruntu_kalitesi()
	k.ortam_kur(GOK)
	if derece:
		_derece_kur()
	else:
		_kat_kur()
	_kamera_kur()


# --------------------------------------------------------------------------
# İlk katın içi
# --------------------------------------------------------------------------

func _kat_kur() -> void:
	k.ornek("ZB_dunya_cennet", [0, 0, 0, 0, 1])
	k.ornek("ZB_dunya_dereceler", [0, 0, 0, 0, 1])
	k.ornek("ZB_dunya_tuba_dev", yer["tuba_dev"])
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
	_arsa_kur()
	_bitkiler_kur()
	_parcaciklar_kur()


## Oyuncunun arsası: ışıklı Tûbâ çekirdeği, tek fidan, ilk çiçekler, nur tohumları.
func _arsa_kur() -> void:
	var a: Dictionary = yer["arsa"]
	var pc: Dictionary = profil["parcacik"]
	var tuba := k.ornek("ZB_agac_tuba_a1", a["tuba"])
	for isaret in tuba.find_children("isik_*", "", true, false):
		var l := OmniLight3D.new()
		l.light_color = pc["nur_renk"]
		l.light_energy = 2.2
		l.omni_range = 5.0
		l.omni_attenuation = 1.6
		l.shadow_enabled = false
		isaret.add_child(l)
		var pos := (isaret as Node3D).global_position
		k.parcacik(40, pos + Vector3(0, 0.25, 0), Vector3(0.35, 0.3, 0.35), 0.05, pc["nur_renk"], 3.0,
			Vector3(0, 0.12, 0), 0.08, 4.0)
		_hale(pos, 1.6, pc["nur_renk"], 1.2)
	k.coklu("ZB_obje_inci_cakil", yer["inci_cakil"], false)
	for f in a["fidan"]:
		k.ornek(f[5], f.slice(0, 5))
	for c in a["cicek"]:
		k.ornek("ZB_cicek_lale_a3", c)
	for p in a["nur_tohumu"]:
		k.parcacik(10, Vector3(p[0], p[1], p[2]), Vector3(0.2, 0.08, 0.2), 0.04, pc["nur_renk"], 3.0,
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
	k.coklu("ZB_bitki_koru_agac", yer["koru"])
	k.coklu("ZB_bitki_uzak_agac", yer["uzak_agac"], false)
	k.coklu("ZB_bitki_cimen", _cimen_konumlari(), false)


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
	var pc: Dictionary = profil["parcacik"]
	# Havada süzülen nur zerreleri (Müslim, Cennet 14-22: ışık her şeyden hafifçe yayılır)
	if pc["nur"] > 0:
		k.parcacik(pc["nur"], Vector3(-8, 3.5, -40), Vector3(36, 3.0, 36), 0.05, pc["nur_renk"], 2.5,
			Vector3(0, 0.03, 0), 0.08, 14.0)
	# Çağlayan diplerinde yükselen su sisi
	for s in yer["selale_dip"]:
		var g: float = s[3]
		k.parcacik(36, Vector3(s[0], s[1] + g * 0.5, s[2]), Vector3(g * 0.7, g * 0.4, g * 0.5), g * 1.6,
			pc["sis_renk"], 0.0, Vector3(0, 0.5, 0), 1.2, 10.0)
	# Selsebil levhasının dibinde ince serpinti
	for t in yer["selsebil"]:
		var y := Vector3(t[0], t[1] + 0.6, t[2])
		k.parcacik(30, y + Basis(Vector3.UP, deg_to_rad(t[3])) * Vector3(0, 0, 1.2), Vector3(0.5, 0.05, 0.2), 0.03,
			Color(0.9, 0.97, 1.0), 0.4, Vector3(0, -1.0, 0), 0.3, 1.2)


# --------------------------------------------------------------------------
# Katlı koni-dağın dış görünümü
# --------------------------------------------------------------------------

func _derece_kur() -> void:
	var koni := k.ornek("ZB_dunya_derece_koni", [0, 0, 0, 0, 1])
	k.coklu("ZB_bitki_uzak_agac", yer["koni_agac"], true)
	# Bulut denizi
	var bm := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(16000, 16000)
	pm.subdivide_width = 220
	pm.subdivide_depth = 220
	bm.mesh = pm
	var mat := ShaderMaterial.new()
	mat.shader = load(BULUT)
	var bd: Dictionary = profil.get("bulut_denizi", {})
	for a in bd:
		mat.set_shader_parameter(a, bd[a])
	bm.material_override = mat
	bm.position.y = -175.0
	bm.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(bm)
	# Etekteki kabarık bulut kümeleri
	var pc: Dictionary = profil["parcacik"]
	var bulut := k.parcacik(90, Vector3(0, -120, 0), Vector3(1500, 60, 1500), 420.0, Color(1, 1, 1, 0.55), 0.0,
		Vector3.ZERO, 2.0, 60.0)
	(bulut.process_material as ParticleProcessMaterial).turbulence_enabled = false
	# Orta halkaları saran ince bulut kuşakları: basamakların düzenini bozar, üst dereceler pusta kalır
	for kusak in [[300.0, 820.0, 0.2], [560.0, 520.0, 0.16]]:
		var b := k.parcacik(70, Vector3(0, kusak[0], 0), Vector3(kusak[1], 25, kusak[1]), 260.0,
			Color(1, 0.97, 0.96, kusak[2]), 0.0, Vector3.ZERO, 1.0, 60.0)
		var bp := b.process_material as ParticleProcessMaterial
		bp.turbulence_enabled = false
		bp.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_RING
		bp.emission_ring_axis = Vector3.UP
		bp.emission_ring_height = 30.0
		bp.emission_ring_radius = kusak[1]
		bp.emission_ring_inner_radius = kusak[1] * 0.75
	# Zirvedeki nur: ışık, hale, göğe uzanan hüzme
	for isaret in koni.find_children("isik_*", "", true, false):
		var pos := (isaret as Node3D).global_position
		var l := OmniLight3D.new()
		l.light_color = pc["nur_renk"]
		l.light_energy = 8.0
		l.omni_range = 700.0
		l.omni_attenuation = 1.2
		isaret.add_child(l)
		_hale(pos, 380.0, pc["nur_renk"], 1.3)
		_huzme(pos + Vector3(0, 900, 0), Vector2(220, 1900), pc["nur_renk"], 1.0)
		k.parcacik(260, pos + Vector3(0, 120, 0), Vector3(90, 140, 90), 7.0, pc["nur_renk"], 3.0,
			Vector3(0, 6.0, 0), 4.0, 30.0)


## Işık halesi: her yöne bakan yumuşak, eklemeli parıltı.
func _hale(pos: Vector3, boy: float, renk: Color, guc: float) -> void:
	var q := QuadMesh.new()
	q.size = Vector2(boy, boy)
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.albedo_texture = k.yuvarlak_doku()
	m.albedo_color = renk * guc
	m.disable_fog = true
	q.material = m
	var mi := MeshInstance3D.new()
	mi.mesh = q
	mi.position = pos
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mi)


## Zirveden göğe uzanan dikey ışık hüzmesi (Arş tasvir edilmez; ışık yukarıda söner).
func _huzme(pos: Vector3, boyut: Vector2, renk: Color, guc: float) -> void:
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
	m.albedo_color = renk * guc
	m.disable_fog = true
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	q.material = m
	var mi := MeshInstance3D.new()
	mi.mesh = q
	mi.position = pos
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mi)


# --------------------------------------------------------------------------
# Kamera
# --------------------------------------------------------------------------

func _kamera_kur() -> void:
	var tanim: Dictionary = yer["kameralar"].get(kamera_modu, yer["kameralar"]["ufuk"])
	var kam := Camera3D.new()
	add_child(kam)
	var kn: Array = tanim["konum"]
	var hd: Array = tanim["hedef"]
	kam.position = Vector3(kn[0], kn[1], kn[2])
	kam.look_at(Vector3(hd[0], hd[1], hd[2]))
	kam.fov = tanim["fov"]
	kam.near = 0.15
	kam.far = 16000.0 if kamera_modu == "derece" else 7000.0
	var ayar := CameraAttributesPractical.new()
	if kamera_modu == "arsa":
		ayar.dof_blur_far_enabled = true
		ayar.dof_blur_far_distance = 140.0
		ayar.dof_blur_far_transition = 300.0
		ayar.dof_blur_amount = 0.025
	kam.attributes = ayar
	kam.current = true
