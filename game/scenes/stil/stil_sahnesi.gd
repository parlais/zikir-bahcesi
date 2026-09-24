extends Node3D
## Stil karşılaştırma sahnesi: büyük çarbağ bahçesi, seçilen stil profiliyle.
##
##   godot --path game res://scenes/stil/stil_sahnesi.tscn -- --zb-stil=nur --zb-kamera=portre
##   (ekran görüntüsü için ayrıca --zb-ekran=/yol.png --zb-kare=80; Game autoload yakalar)
##
## Sahne game/assets/models altındaki ZB_sahne_* ve ZB_bitki_* modellerinden,
## yerleşim game/data/sahne_carbag.json dosyasından kurulur (model fabrikası üretir).

const MODELLER := "res://assets/models/"
const YERLESIM := "res://data/sahne_carbag.json"
const SHADER := "res://scenes/stil/shader/"

## glTF malzeme adı -> [shader, sabit parametreler, profil malzeme anahtarı]
const MALZEME_TABLOSU := {
	"mat": ["yuzey", {"puruz": 0.75, "detay": 0.05}, ""],
	"tas": ["yuzey", {"puruz": 0.5, "detay": 0.12, "detay_olcek": 0.9}, "tas"],
	"govde": ["yuzey", {"puruz": 0.95, "detay": 0.25, "detay_olcek": 5.0}, ""],
	"metal": ["yuzey", {"puruz": 0.32, "metal": 0.85, "detay": 0.0}, "altin"],
	"altin": ["yuzey", {"puruz": 0.3, "metal": 0.9, "detay": 0.0}, "altin"],
	"kursun": ["yuzey", {"puruz": 0.45, "metal": 0.6, "detay": 0.05}, ""],
	"inci": ["yuzey", {"puruz": 0.25, "detay": 0.0}, ""],
	"uzak": ["yuzey", {"puruz": 1.0, "detay": 0.1, "detay_olcek": 0.02}, "uzak"],
	"zemin": ["zemin", {"spek": 0.03}, "zemin"],
	"yaprak": ["yaprak", {"spek": 0.03}, "yaprak"],
	"cimen_ot": ["cimen", {"spek": 0.03}, "cimen"],
	"cicek": ["cicek", {}, "cicek"],
	"cini": ["cini", {}, "cini"],
	"su": ["su", {}, "su"],
	"nur": ["yuzey", {"puruz": 0.4, "detay": 0.0, "isima": Color(1.0, 0.8, 0.45)}, "nur"],
}

var stil := "nur"
var kamera_modu := "portre"
var profil: Dictionary
var yer: Dictionary
var _malzemeler: Dictionary = {}
var _gunes: DirectionalLight3D


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--zb-stil="):
			stil = a.get_slice("=", 1)
		elif a.begins_with("--zb-kamera="):
			kamera_modu = a.get_slice("=", 1)
	profil = StilProfilleri.al(stil)
	yer = JSON.parse_string(FileAccess.get_file_as_string(YERLESIM))
	_goruntu_kalitesi()
	_ortam_kur()
	_sahne_kur()
	_bitkiler_kur()
	_parcaciklar_kur()
	_kamera_kur()
	if kamera_modu == "portre":
		var ui := ArayuzOnizleme.new()
		ui.profil = profil
		add_child(ui)


# --------------------------------------------------------------------------
# Görüntü ve ortam
# --------------------------------------------------------------------------

func _goruntu_kalitesi() -> void:
	var vp := get_viewport()
	vp.msaa_3d = Viewport.MSAA_4X
	vp.screen_space_aa = Viewport.SCREEN_SPACE_AA_FXAA
	vp.positional_shadow_atlas_size = 4096
	RenderingServer.directional_shadow_atlas_set_size(8192, true)
	RenderingServer.directional_soft_shadow_filter_set_quality(RenderingServer.SHADOW_QUALITY_SOFT_HIGH)


func _ortam_kur() -> void:
	var o: Dictionary = profil["ortam"]
	var g: Dictionary = profil["gok"]
	var sky_mat := ShaderMaterial.new()
	sky_mat.shader = load(SHADER + "gok.gdshader")
	for k in g:
		sky_mat.set_shader_parameter(k, g[k])
	var sky := Sky.new()
	sky.sky_material = sky_mat
	sky.radiance_size = Sky.RADIANCE_SIZE_256
	sky.process_mode = Sky.PROCESS_MODE_INCREMENTAL

	var e := Environment.new()
	e.background_mode = Environment.BG_SKY
	e.sky = sky
	e.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	e.ambient_light_energy = o["ambient"]
	e.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	e.tonemap_mode = Environment.TONE_MAPPER_ACES if o["ton"] == "aces" else Environment.TONE_MAPPER_FILMIC
	e.tonemap_exposure = o["pozlama"]
	e.tonemap_white = o["beyaz"]

	var p: Array = o["parlama"]  # yoğunluk, güç, bloom, hdr eşiği
	e.glow_enabled = true
	e.glow_intensity = p[0]
	e.glow_strength = p[1]
	e.glow_bloom = p[2]
	e.glow_hdr_threshold = p[3]
	e.glow_blend_mode = Environment.GLOW_BLEND_MODE_SOFTLIGHT if p[0] < 0.5 else Environment.GLOW_BLEND_MODE_SCREEN
	for i in 7:
		e.set_glow_level(i, [0.0, 0.3, 0.6, 0.9, 1.0, 0.8, 0.5][i])

	var s: Array = o["sis"]  # yoğunluk, renk, güneş saçılımı, gökyüzü etkisi
	e.fog_enabled = true
	e.fog_density = s[0]
	e.fog_light_color = s[1]
	e.fog_sun_scatter = s[2]
	e.fog_sky_affect = s[3]
	e.fog_aerial_perspective = o.get("hava_perspektif", 0.2)

	var h: Array = o["hacim_sis"]  # yoğunluk, renk, anizotropi, uzunluk
	if h[0] > 0.0:
		e.volumetric_fog_enabled = true
		e.volumetric_fog_density = h[0]
		e.volumetric_fog_albedo = h[1]
		e.volumetric_fog_anisotropy = h[2]
		e.volumetric_fog_length = h[3]
		e.volumetric_fog_detail_spread = 1.5
		e.volumetric_fog_sky_affect = 0.0

	e.sdfgi_enabled = o["sdfgi"]
	e.sdfgi_use_occlusion = true
	e.sdfgi_cascades = 4
	e.sdfgi_min_cell_size = 0.25
	e.ssao_enabled = o["ssao"] > 0.0
	e.ssao_intensity = o["ssao"] * 2.0
	e.ssao_radius = 1.2
	e.ssil_enabled = true
	e.ssr_enabled = o["ssr"]
	e.ssr_max_steps = 96
	e.ssr_fade_in = 0.05
	e.ssr_fade_out = 1.5
	e.adjustment_enabled = true
	e.adjustment_saturation = o["doygunluk"]
	e.adjustment_contrast = o["kontrast"]
	e.adjustment_brightness = o["parlaklik"]
	var we := WorldEnvironment.new()
	we.environment = e
	add_child(we)

	var gp: Dictionary = profil["gunes"]
	_gunes = DirectionalLight3D.new()
	var el := deg_to_rad(gp["yukseklik"])
	var az := deg_to_rad(gp["yon"])
	var yon := Vector3(cos(el) * sin(az), sin(el), cos(el) * cos(az))
	add_child(_gunes)
	_gunes.position = yon * 100.0
	_gunes.look_at(Vector3.ZERO, Vector3.UP if absf(yon.y) < 0.99 else Vector3.FORWARD)
	_gunes.light_color = gp["renk"]
	_gunes.light_energy = gp["enerji"]
	_gunes.light_angular_distance = gp["yumusak"]
	_gunes.light_volumetric_fog_energy = 1.6
	_gunes.shadow_enabled = true
	_gunes.shadow_blur = 1.5
	_gunes.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS
	_gunes.directional_shadow_max_distance = 120.0


# --------------------------------------------------------------------------
# Malzemeler
# --------------------------------------------------------------------------

## glTF malzeme adına göre stil shader'ı (önbellekli).
func _malzeme(ad: String) -> Material:
	if _malzemeler.has(ad):
		return _malzemeler[ad]
	if not MALZEME_TABLOSU.has(ad):
		_malzemeler[ad] = null
		return null
	var satir: Array = MALZEME_TABLOSU[ad]
	var m := ShaderMaterial.new()
	m.shader = load(SHADER + satir[0] + ".gdshader")
	var ortak: Dictionary = profil["ortak"]
	for k in ortak:
		m.set_shader_parameter(k, ortak[k])
	for k in satir[1]:
		m.set_shader_parameter(k, satir[1][k])
	var ozel: Dictionary = profil["malzeme"].get(satir[2], {})
	for k in ozel:
		m.set_shader_parameter(k, ozel[k])
	if ad == "uzak":
		m.set_shader_parameter("doygunluk", float(ortak.get("doygunluk", 1.0)) * 0.7)
	_malzemeler[ad] = m
	return m


func _boya(n: Node) -> void:
	for mi in n.find_children("*", "MeshInstance3D", true, false):
		var mesh: Mesh = mi.mesh
		for i in mesh.get_surface_count():
			var eski := mesh.surface_get_material(i)
			var yeni := _malzeme(eski.resource_name) if eski else null
			if yeni:
				mi.set_surface_override_material(i, yeni)
			elif eski is BaseMaterial3D:
				(eski as BaseMaterial3D).vertex_color_use_as_albedo = true


func _ornek(model: String, t: Array, ek_olcek := 1.0) -> Node3D:
	var s: PackedScene = load(MODELLER + model + ".glb")
	var n: Node3D = s.instantiate()
	n.position = Vector3(t[0], t[1], t[2])
	n.rotation_degrees.y = t[3]
	n.scale = Vector3.ONE * float(t[4]) * ek_olcek
	add_child(n)
	_boya(n)
	return n


# --------------------------------------------------------------------------
# Sahne: arazi, yapılar, kandiller
# --------------------------------------------------------------------------

func _sahne_kur() -> void:
	_ornek("ZB_sahne_carbag", [0, 0, 0, 0, 1])
	_ornek("ZB_sahne_daglar", [0, 0, 0, 0, 1])
	var y: Dictionary = yer["yapilar"]
	var sadirvan := _ornek("ZB_yapi_sadirvan", y["sadirvan"])
	_ornek("ZB_yapi_kosk", y["kosk"])
	_ornek("ZB_yapi_bahce_kapisi", y["bahce_kapisi"])
	for isaret in sadirvan.find_children("water_*", "", true, false):
		var m := MeshInstance3D.new()
		var c := CylinderMesh.new()
		c.top_radius = 0.9
		c.bottom_radius = 0.9
		c.height = 0.02
		c.radial_segments = 24
		m.mesh = c
		m.material_override = _malzeme("su")
		isaret.add_child(m)
	var k: Dictionary = profil["kandil"]
	for t in yer["kandil"]:
		var n := _ornek("ZB_obje_kandil", t)
		if k["enerji"] > 0.0:
			for isaret in n.find_children("isik_*", "", true, false):
				var l := OmniLight3D.new()
				l.light_color = k["renk"]
				l.light_energy = k["enerji"]
				l.omni_range = 7.0
				l.omni_attenuation = 1.4
				l.shadow_enabled = false
				l.light_volumetric_fog_energy = 2.0
				isaret.add_child(l)


# --------------------------------------------------------------------------
# Bitkiler: MultiMesh ile çoğaltma
# --------------------------------------------------------------------------

func _bitki_mesh(model: String) -> Mesh:
	var s: PackedScene = load(MODELLER + model + ".glb")
	var n := s.instantiate()
	var mi: MeshInstance3D = n.find_children("*", "MeshInstance3D", true, false)[0]
	var mesh: ArrayMesh = mi.mesh.duplicate()
	for i in mesh.get_surface_count():
		var eski := mesh.surface_get_material(i)
		var yeni := _malzeme(eski.resource_name) if eski else null
		if yeni:
			mesh.surface_set_material(i, yeni)
	n.free()
	return mesh


func _coklu(model: String, konumlar: Array, golge := true) -> void:
	if konumlar.is_empty():
		return
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_custom_data = true
	mm.mesh = _bitki_mesh(model)
	mm.instance_count = konumlar.size()
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(model)
	for i in konumlar.size():
		var t: Array = konumlar[i]
		var b := Basis(Vector3.UP, deg_to_rad(t[3])).scaled(Vector3.ONE * float(t[4]))
		mm.set_instance_transform(i, Transform3D(b, Vector3(t[0], t[1], t[2])))
		mm.set_instance_custom_data(i, Color(rng.randf(), rng.randf(), 0, 0))
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = mm
	mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if golge else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mmi)


func _bitkiler_kur() -> void:
	_coklu("ZB_bitki_selvi", yer["selvi"])
	_coklu("ZB_bitki_nar", yer["nar"])
	_coklu("ZB_bitki_simsir", yer["simsir"])
	_coklu("ZB_bitki_gul_cali", yer["gul"])
	_coklu("ZB_bitki_lale_tarhi", yer["lale"], false)
	var dis_selvi: Array = []
	var dis_nar: Array = []
	for t in yer["dis_agac"]:
		(dis_selvi if t[0] == "selvi" else dis_nar).append(t.slice(1))
	_coklu("ZB_bitki_selvi", dis_selvi)
	_coklu("ZB_bitki_nar", dis_nar)
	_coklu("ZB_bitki_cimen", _cimen_konumlari(4.5), false)


func _cimen_konumlari(yogunluk: float) -> Array:
	var out: Array = []
	var rng := RandomNumberGenerator.new()
	rng.seed = 5
	for a in yer["cimen_alanlari"]:
		var x0: float = a[0]
		var z0: float = a[1]
		var x1: float = a[2]
		var z1: float = a[3]
		var n := int((x1 - x0) * (z1 - z0) * yogunluk)
		for i in n:
			var x := rng.randf_range(x0, x1)
			var z := rng.randf_range(z0, z1)
			var bos := false
			for s in yer["cimensiz"]:
				if x > s[0] and x < s[2] and z > s[1] and z < s[3]:
					bos = true
					break
			if not bos:
				out.append([x, a[4], z, rng.randf_range(0, 360), rng.randf_range(0.8, 1.4)])
	return out


# --------------------------------------------------------------------------
# Parçacıklar: nur zerreleri, uçuşan gül yaprakları, fıskiye
# --------------------------------------------------------------------------

func _yuvarlak_doku() -> Texture2D:
	var g := Gradient.new()
	g.set_color(0, Color(1, 1, 1, 1))
	g.set_color(1, Color(1, 1, 1, 0))
	var t := GradientTexture2D.new()
	t.gradient = g
	t.fill = GradientTexture2D.FILL_RADIAL
	t.fill_from = Vector2(0.5, 0.5)
	t.fill_to = Vector2(0.5, 0.0)
	t.width = 64
	t.height = 64
	return t


func _parcacik(adet: int, merkez: Vector3, alan: Vector3, boy: float, renk: Color, isik: float,
		yercekimi: Vector3, hiz: float, omur: float, billboard := BaseMaterial3D.BILLBOARD_ENABLED) -> GPUParticles3D:
	var p := GPUParticles3D.new()
	p.amount = adet
	p.lifetime = omur
	p.preprocess = omur
	p.visibility_aabb = AABB(-alan * 1.5, alan * 3.0)
	var pm := ParticleProcessMaterial.new()
	pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	pm.emission_box_extents = alan
	pm.gravity = yercekimi
	pm.initial_velocity_min = hiz * 0.3
	pm.initial_velocity_max = hiz
	pm.spread = 180.0
	pm.turbulence_enabled = true
	pm.turbulence_noise_strength = 0.6
	pm.turbulence_noise_scale = 6.0
	pm.scale_min = 0.5
	pm.scale_max = 1.3
	pm.angle_min = 0.0
	pm.angle_max = 360.0
	var sonuk := Gradient.new()
	sonuk.set_color(0, Color(1, 1, 1, 0))
	sonuk.add_point(0.2, Color(1, 1, 1, 1))
	sonuk.add_point(0.8, Color(1, 1, 1, 1))
	sonuk.set_color(sonuk.get_point_count() - 1, Color(1, 1, 1, 0))
	var gt := GradientTexture1D.new()
	gt.gradient = sonuk
	pm.color_ramp = gt
	p.process_material = pm
	var q := QuadMesh.new()
	q.size = Vector2(boy, boy)
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.billboard_mode = billboard
	mat.billboard_keep_scale = true
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD if isik > 0.0 else BaseMaterial3D.BLEND_MODE_MIX
	mat.vertex_color_use_as_albedo = true
	mat.albedo_color = renk * (1.0 + isik)
	mat.albedo_texture = _yuvarlak_doku()
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	q.material = mat
	p.draw_pass_1 = q
	p.position = merkez
	add_child(p)
	return p


func _parcaciklar_kur() -> void:
	var pc: Dictionary = profil["parcacik"]
	if pc["nur"] > 0:
		_parcacik(pc["nur"], Vector3(0, 3.0, -4), Vector3(26, 3.0, 30), 0.07, pc["nur_renk"], 2.5,
			Vector3(0, 0.03, 0), 0.08, 14.0)
	if pc["yaprak"] > 0:
		var y := _parcacik(pc["yaprak"], Vector3(0, 4.0, 8), Vector3(10, 3.5, 14), 0.07, pc["yaprak_renk"], 0.0,
			Vector3(0.15, -0.25, 0), 0.3, 12.0, BaseMaterial3D.BILLBOARD_PARTICLES)
		(y.draw_pass_1 as QuadMesh).size = Vector2(0.07, 0.045)
	# Şadırvan fıskiyesi
	var f := _parcacik(260, Vector3(0, 2.75, 0), Vector3(0.05, 0.05, 0.05), 0.05, Color(0.85, 0.95, 1.0), 0.3,
		Vector3(0, -7.5, 0), 3.2, 0.95)
	var fm := f.process_material as ParticleProcessMaterial
	fm.direction = Vector3.UP
	fm.spread = 14.0
	fm.turbulence_enabled = false


# --------------------------------------------------------------------------
# Kamera
# --------------------------------------------------------------------------

func _kamera_kur() -> void:
	var k := Camera3D.new()
	add_child(k)
	var ayar := CameraAttributesPractical.new()
	if kamera_modu == "sinematik":
		k.fov = 46.0
		k.position = Vector3(-33, 14.5, 34)
		k.look_at(Vector3(2.0, 2.0, -12))
	else:
		k.fov = 60.0
		k.position = Vector3(2.5, 2.0, 25.5)
		k.look_at(Vector3(-0.8, 5.2, -36))
		ayar.dof_blur_far_enabled = true
		ayar.dof_blur_far_distance = 90.0
		ayar.dof_blur_far_transition = 60.0
		ayar.dof_blur_amount = 0.06
	k.attributes = ayar
	k.far = 1200.0
	k.current = true
