extends Node3D
## Stil karşılaştırma sahnesi: büyük çarbağ bahçesi, seçilen stil profiliyle.
##
##   godot --path game res://scenes/stil/stil_sahnesi.tscn -- --zb-stil=nur --zb-kamera=portre
##   (ekran görüntüsü için ayrıca --zb-ekran=/yol.png --zb-kare=80; Game autoload yakalar)
##
## Sahne game/assets/models altındaki ZB_sahne_* ve ZB_bitki_* modellerinden,
## yerleşim game/data/sahne_carbag.json dosyasından kurulur (model fabrikası üretir).

const YERLESIM := "res://data/sahne_carbag.json"

var stil := "nur"
var kamera_modu := "portre"
var profil: Dictionary
var yer: Dictionary
var k: SahneKurucu
var _gunes: DirectionalLight3D


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--zb-stil="):
			stil = a.get_slice("=", 1)
		elif a.begins_with("--zb-kamera="):
			kamera_modu = a.get_slice("=", 1)
	profil = StilProfilleri.al(stil)
	yer = JSON.parse_string(FileAccess.get_file_as_string(YERLESIM))
	k = SahneKurucu.new(self, profil)
	k.goruntu_kalitesi()
	_gunes = k.ortam_kur()
	_sahne_kur()
	_bitkiler_kur()
	_parcaciklar_kur()
	_kamera_kur()
	if kamera_modu == "portre":
		var ui := ArayuzOnizleme.new()
		ui.profil = profil
		add_child(ui)


# --------------------------------------------------------------------------
# Sahne: arazi, yapılar, kandiller
# --------------------------------------------------------------------------

func _sahne_kur() -> void:
	k.ornek("ZB_sahne_carbag", [0, 0, 0, 0, 1])
	k.ornek("ZB_sahne_daglar", [0, 0, 0, 0, 1])
	var y: Dictionary = yer["yapilar"]
	var sadirvan := k.ornek("ZB_yapi_sadirvan", y["sadirvan"])
	k.ornek("ZB_yapi_kosk", y["kosk"])
	k.ornek("ZB_yapi_bahce_kapisi", y["bahce_kapisi"])
	for isaret in sadirvan.find_children("water_*", "", true, false):
		var m := MeshInstance3D.new()
		var c := CylinderMesh.new()
		c.top_radius = 0.9
		c.bottom_radius = 0.9
		c.height = 0.02
		c.radial_segments = 24
		m.mesh = c
		m.material_override = k.malzeme("su")
		isaret.add_child(m)
	var kd: Dictionary = profil["kandil"]
	for t in yer["kandil"]:
		var n := k.ornek("ZB_obje_kandil", t)
		if kd["enerji"] > 0.0:
			for isaret in n.find_children("isik_*", "", true, false):
				var l := OmniLight3D.new()
				l.light_color = kd["renk"]
				l.light_energy = kd["enerji"]
				l.omni_range = 7.0
				l.omni_attenuation = 1.4
				l.shadow_enabled = false
				l.light_volumetric_fog_energy = 2.0
				isaret.add_child(l)


# --------------------------------------------------------------------------
# Bitkiler: MultiMesh ile çoğaltma
# --------------------------------------------------------------------------

func _bitkiler_kur() -> void:
	k.coklu("ZB_bitki_selvi", yer["selvi"])
	k.coklu("ZB_bitki_nar", yer["nar"])
	k.coklu("ZB_bitki_simsir", yer["simsir"])
	k.coklu("ZB_bitki_gul_cali", yer["gul"])
	k.coklu("ZB_bitki_lale_tarhi", yer["lale"], false)
	var dis_selvi: Array = []
	var dis_nar: Array = []
	for t in yer["dis_agac"]:
		(dis_selvi if t[0] == "selvi" else dis_nar).append(t.slice(1))
	k.coklu("ZB_bitki_selvi", dis_selvi)
	k.coklu("ZB_bitki_nar", dis_nar)
	k.coklu("ZB_bitki_cimen", _cimen_konumlari(4.5), false)


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

func _parcaciklar_kur() -> void:
	var pc: Dictionary = profil["parcacik"]
	if pc["nur"] > 0:
		k.parcacik(pc["nur"], Vector3(0, 3.0, -4), Vector3(26, 3.0, 30), 0.07, pc["nur_renk"], 2.5,
			Vector3(0, 0.03, 0), 0.08, 14.0)
	if pc["yaprak"] > 0:
		var y := k.parcacik(pc["yaprak"], Vector3(0, 4.0, 8), Vector3(10, 3.5, 14), 0.07, pc["yaprak_renk"], 0.0,
			Vector3(0.15, -0.25, 0), 0.3, 12.0, BaseMaterial3D.BILLBOARD_PARTICLES)
		(y.draw_pass_1 as QuadMesh).size = Vector2(0.07, 0.045)
	# Şadırvan fıskiyesi
	var f := k.parcacik(260, Vector3(0, 2.75, 0), Vector3(0.05, 0.05, 0.05), 0.05, Color(0.85, 0.95, 1.0), 0.3,
		Vector3(0, -7.5, 0), 3.2, 0.95)
	var fm := f.process_material as ParticleProcessMaterial
	fm.direction = Vector3.UP
	fm.spread = 14.0
	fm.turbulence_enabled = false


# --------------------------------------------------------------------------
# Kamera
# --------------------------------------------------------------------------

func _kamera_kur() -> void:
	var kam := Camera3D.new()
	add_child(kam)
	var ayar := CameraAttributesPractical.new()
	if kamera_modu == "sinematik":
		kam.fov = 46.0
		kam.position = Vector3(-33, 14.5, 34)
		kam.look_at(Vector3(2.0, 2.0, -12))
	else:
		kam.fov = 60.0
		kam.position = Vector3(2.5, 2.0, 25.5)
		kam.look_at(Vector3(-0.8, 5.2, -36))
		ayar.dof_blur_far_enabled = true
		ayar.dof_blur_far_distance = 90.0
		ayar.dof_blur_far_transition = 60.0
		ayar.dof_blur_amount = 0.06
	kam.attributes = ayar
	kam.far = 1200.0
	kam.current = true
