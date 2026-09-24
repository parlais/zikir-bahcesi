class_name Bahce
extends Node3D
## Adadaki bahçe: durumdaki envantere ve büyüme aşamalarına göre modelleri
## yerleştirir. Her asset'in sabit yuvaları (slot) vardır; olgun örnekler ilk
## yuvalara, büyüyen örnek bir sonrakine konur. Durum değiştikçe yalnız
## değişen yuvalar yeniden kurulur.

const SU_SHADER := preload("res://scenes/su.gdshader")

## Oturum Bismillah ile açılınca kapı kanatlarının açılma açısı.
const KAPI_ACISI := 78.0

var _yuvalar: Dictionary = {}     ## "asset#i" -> Node3D (kurulu model)
var _model_adi: Dictionary = {}   ## "asset#i" -> kurulu modelin dosya adı
var _sahneler: Dictionary = {}    ## dosya adı -> PackedScene (önbellek)
var _kapi_acik := false


func _ready() -> void:
	var ada := _yukle("ZB_zemin_ada")
	if ada:
		var n: Node3D = ada.instantiate()
		add_child(n)
		_susle(n)
	yenile(false)
	Game.durum_degisti.connect(yenile)
	Game.olay.connect(_on_olay)


## Durumdan bahçeyi kurar. animasyon=false ise açılışta sessizce yerleştirir.
func yenile(animasyon := true) -> void:
	var st := Game.state
	for id in Yerlesim.YUVALAR:
		var yuvalar: Array = Yerlesim.YUVALAR[id]
		var a: Dictionary = Game.content.assets[id]
		var modeller: Array = a["modeller"]
		if modeller.is_empty():
			continue
		var istenen: Array = []  # her yuva için model adı ("" = boş)
		if id == "bahce_kapisi":
			istenen = [modeller[0]]  # Kapı hep yerindedir; Bismillah onu açar.
		elif a["asama_sayisi"] > 1:
			var il := Game.engine.ilerleme(id)
			var olgun := mini(st.adet(id), yuvalar.size())
			for i in olgun:
				istenen.append(modeller[-1])
			if olgun < yuvalar.size() and il["asama"] > 0:
				istenen.append(modeller[il["asama"] - 1])
		else:
			for i in mini(st.adet(id), yuvalar.size()):
				istenen.append(modeller[0])
		for i in yuvalar.size():
			var model: String = istenen[i] if i < istenen.size() else ""
			_yuva_ayarla(id, i, model, animasyon)
	_kapiyi_ayarla(Game.oturum_acildi, animasyon)


func _yuva_ayarla(id: String, i: int, model: String, animasyon: bool) -> void:
	var anahtar := "%s#%d" % [id, i]
	if _model_adi.get(anahtar, "") == model:
		return
	if _yuvalar.has(anahtar):
		_yuvalar[anahtar].queue_free()
		_yuvalar.erase(anahtar)
	_model_adi[anahtar] = model
	if model == "":
		return
	var sahne := _yukle(model)
	if sahne == null:
		return
	var yuva: Array = Yerlesim.YUVALAR[id][i]
	var n: Node3D = sahne.instantiate()
	n.position = yuva[0]
	n.rotation_degrees.y = yuva[1]
	var s: float = yuva[2]
	n.scale = Vector3.ONE * s
	add_child(n)
	_yuvalar[anahtar] = n
	_susle(n)
	if animasyon:
		n.scale = Vector3.ONE * s * 0.4
		var tw := create_tween()
		tw.tween_property(n, "scale", Vector3.ONE * s, 0.6).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		efekt(n.global_position + Vector3(0, 0.5, 0))


## Model içindeki işaret düğümlerine ışık ve su ekler (bkz. model fabrikası).
## Ayrıca malzemelerin köşe rengini (modellerin bütün rengi buradadır) kullanmasını
## sağlar; glTF içe aktarıcısı bunu kendiliğinden açmıyor.
func _susle(n: Node3D) -> void:
	for mi in n.find_children("*", "MeshInstance3D", true, false):
		var mesh: Mesh = (mi as MeshInstance3D).mesh
		for i in mesh.get_surface_count():
			var mat := mesh.surface_get_material(i) as BaseMaterial3D
			if mat and not mat.vertex_color_use_as_albedo:
				mat.vertex_color_use_as_albedo = true
				mat.vertex_color_is_srgb = false
	for isaret in n.find_children("isik_*", "", true, false):
		var l := OmniLight3D.new()
		l.light_color = Color(1.0, 0.8, 0.5)
		l.light_energy = 1.6
		l.omni_range = 2.5
		isaret.add_child(l)
	for isaret in n.find_children("water_*", "", true, false):
		var m := MeshInstance3D.new()
		var c := CylinderMesh.new()
		c.top_radius = 0.93
		c.bottom_radius = 0.93
		c.height = 0.02
		c.radial_segments = 16
		c.rings = 1
		m.mesh = c
		var mat := ShaderMaterial.new()
		mat.shader = SU_SHADER
		m.material_override = mat
		isaret.add_child(m)


func _kapiyi_ayarla(acik: bool, animasyon: bool) -> void:
	var kapi: Node3D = _yuvalar.get("bahce_kapisi#0")
	if kapi == null:
		return
	var degisti := acik != _kapi_acik
	_kapi_acik = acik
	for ad in ["kanat_sol", "kanat_sag"]:
		var k: Node3D = kapi.find_child(ad, true, false)
		if k == null:
			continue
		var hedef := (KAPI_ACISI if ad == "kanat_sol" else -KAPI_ACISI) if acik else 0.0
		if animasyon and degisti:
			create_tween().tween_property(k, "rotation_degrees:y", hedef, 1.6) \
				.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		elif not animasyon:
			k.rotation_degrees.y = hedef


func _on_olay(o: Dictionary) -> void:
	if o["tur"] == "kaynak":
		return
	if o["tur"] == "tamamlandi" and o["asset"] == "bahce_kapisi":
		efekt(Vector3(0, 2.0, -4.5), 60)


## Nur parçacıkları: altın rengi, yukarı süzülen kısa bir patlama.
func efekt(konum: Vector3, adet := 36) -> void:
	var p := GPUParticles3D.new()
	p.one_shot = true
	p.amount = adet
	p.lifetime = 1.6
	p.explosiveness = 0.85
	var pm := ParticleProcessMaterial.new()
	pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	pm.emission_sphere_radius = 0.4
	pm.direction = Vector3.UP
	pm.spread = 60.0
	pm.initial_velocity_min = 0.6
	pm.initial_velocity_max = 1.6
	pm.gravity = Vector3(0, 0.3, 0)
	pm.scale_min = 0.6
	pm.scale_max = 1.2
	var grad := Gradient.new()
	grad.set_color(0, Color(1.0, 0.9, 0.55, 1.0))
	grad.set_color(1, Color(1.0, 0.8, 0.4, 0.0))
	var gt := GradientTexture1D.new()
	gt.gradient = grad
	pm.color_ramp = gt
	p.process_material = pm
	var q := QuadMesh.new()
	q.size = Vector2(0.12, 0.12)
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.vertex_color_use_as_albedo = true
	mat.albedo_color = Color(1, 1, 1)
	q.material = mat
	p.draw_pass_1 = q
	p.position = konum
	add_child(p)
	p.emitting = true
	p.finished.connect(p.queue_free)


func _yukle(model: String) -> PackedScene:
	if _sahneler.has(model):
		return _sahneler[model]
	var yol := Yerlesim.MODEL_DIR + model + ".glb"
	var s: PackedScene = null
	if ResourceLoader.exists(yol):
		s = load(yol)
	_sahneler[model] = s
	return s
