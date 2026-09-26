class_name KesitKurucu
extends RefCounted
## Kesit (K10, K18): sekiz tabakanın dıştan görünümü.
##
## İlk kat, içerideki dünyanın kendisidir (CennetSahnesi._kat_kur); kesme düzleminin
## önündeki parçası gizlenir. Bu sınıf yalnız dışarıdan görülenleri ekler:
##   - ilk katın kesit yüzü ve merdiveninin bulutlara uzanan devamı (ZB_kesit_kat1)
##   - 2-8. katlar (ZB_kesit_kat2..7, ZB_kesit_firdevs): zemin, kesit yüzü, ırmaklar,
##     çağlayanlar, merdiven şeridi, tavan ve arka perde
##   - uzak ağaç ve yapı siluetleri (gerçek modellerden çizilmiş kartlar, tek MultiMesh)
##   - bulut kümeleri (çağlayanların indiği bulutlar, gökte süzülenler, tavanın altındaki kuşak)
##   - Firdevs'in nuru (hale ve zerreler; ışık sütunu yok) ve en alttaki bulut denizi
## Ölçüler ve yerleşim model fabrikasında üretilir (tools/model_factory/models/kesit.py).

const VERI := "res://data/dunya_kesit.json"
const AGACLAR := "res://data/dunya_kesit_agac.bin"
const SHADER := "res://scenes/stil/shader/"

var sahne: Node3D
var k: SahneKurucu
var veri: Dictionary
## Kesit katmanı: yakınlaşmada kamera içeri girince gizlenir.
var kok: Node3D
var _arsa_mat: StandardMaterial3D


func _init(s: Node3D, kurucu: SahneKurucu) -> void:
	sahne = s
	k = kurucu


func kur() -> void:
	veri = JSON.parse_string(FileAccess.get_file_as_string(VERI))
	kok = Node3D.new()
	kok.name = "kesit"
	sahne.add_child(kok)
	var o: Dictionary = veri["olcu"]
	RenderingServer.global_shader_parameter_set("zb_kesit_olcu",
		Vector4(o["kesme_z"], o["kat_h"], o["kat_t"], o["hava"]))
	# Pus: katın penceresi boyunca (oran) başladığı ve tamamlandığı yer; yanların ışığa karıştığı |x|
	RenderingServer.global_shader_parameter_set("zb_pus_aralik", Vector4(0.25, 1.05, 2600.0, 3800.0))
	var kam: Array = o["kamera"]["konum"]
	RenderingServer.global_shader_parameter_set("zb_kesit_kamera", Vector4(kam[1], kam[2], o["pencere_m"], 0.0))
	var modeller := ["ZB_kesit_kat1"]
	for i in range(2, int(o["kat"])):
		modeller.append("ZB_kesit_kat%d" % i)
	modeller.append("ZB_kesit_firdevs")
	for m in modeller:
		var n := k.ornek(m, [0, 0, 0, 0, 1], 1.0, kok)
		# Bütün tabakalar aynı ışığı alır: üstteki alttakine gölge düşürmez
		for mi in n.find_children("*", "GeometryInstance3D", true, false):
			(mi as GeometryInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	# Katların göğü: içeriden görülen göğün aynısı (profilin kat_gok alanı, Nur <-> Ori)
	for ad in ["kat_gogu", "kat_gogu_ilk", "kat_tavani"]:
		var km := k.malzeme(ad) as ShaderMaterial
		if k.profil.has("kat_gok"):
			for a in k.profil["kat_gok"]:
				k.bagla(km, "shader_parameter/" + a, k.yol("kat_gok/" + a))
	_siluetler()
	_bulutlar()
	_firdevs()
	_bulut_denizi()
	_arsa_isareti()


## Uzak ağaç ve yapı siluetleri: kat başına bir MultiMesh. Kart, dibi örneğin yerinde
## duran ve kameraya dönen bir dörtgendir; boyu türün gerçek boyu × örneğin ölçeği.
func _siluetler() -> void:
	var b := FileAccess.get_file_as_bytes(AGACLAR).to_float32_array()
	var meta: Dictionary = veri["siluet"]
	var turler: Array = veri["turler"]
	var mesh := _kart()
	mesh.surface_set_material(0, k.malzeme("kesit_agac"))
	var rng := RandomNumberGenerator.new()
	rng.seed = 41
	for kat in veri["katlar"]:
		var bas: int = kat["agac"][0]
		var n: int = kat["agac"][1]
		if n == 0:
			continue
		var nur := 1.0 if kat.has("kaynak") else 0.0
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.use_custom_data = true
		mm.mesh = mesh
		mm.instance_count = n
		for i in n:
			var j := (bas + i) * 5
			var tur: String = turler[int(b[j + 4])]
			var m: Array = meta[tur]      # [hücre, S, y0]
			var s: float = float(m[1]) * b[j + 3]
			var t := Transform3D(Basis().scaled(Vector3.ONE * s), Vector3(b[j], b[j + 1] + float(m[2]) * b[j + 3], b[j + 2]))
			mm.set_instance_transform(i, t)
			mm.set_instance_custom_data(i, Color(rng.randf(), float(m[0]) / 16.0, nur, 0.0))
		var mmi := MultiMeshInstance3D.new()
		mmi.multimesh = mm
		mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		kok.add_child(mmi)


## Dibi orijinde, 1 m'lik dikey kart (x -0,5..0,5, y 0..1).
func _kart() -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var k4 := [Vector3(-0.5, 0, 0), Vector3(0.5, 0, 0), Vector3(0.5, 1, 0), Vector3(-0.5, 1, 0)]
	var uv := [Vector2(0, 1), Vector2(1, 1), Vector2(1, 0), Vector2(0, 0)]
	for i in [0, 1, 2, 0, 2, 3]:
		st.set_normal(Vector3(0, 0, 1))
		st.set_uv(uv[i])
		st.add_vertex(k4[i])
	return st.commit()


## Bulut kümeleri: içerideki _bulut_kumesi ile aynı kural ve renk, tek MultiMesh.
func _bulutlar() -> void:
	for kat in veri["katlar"]:
		for bl in kat["bulut"]:
			sahne._bulut_kumesi(Vector3(bl[0], bl[1], bl[2]), bl[3], 14 if bl[3] > 200.0 else 10, int(bl[5]), bl[4])
		sahne._bulut_katmani(kok, true)


## Firdevs (nurlu bahçe): kaynağın ışığı ve her şeyi kuşatan nur. Işık sütunu konmaz;
## ışık bir şeye yönelmiş gibi değil, her yeri kuşatır. Arş tasvir edilmez.
func _firdevs() -> void:
	var nur_renk := k.yol("parcacik/nur_renk")
	for kat in veri["katlar"]:
		if not kat.has("kaynak"):
			continue
		var p := Vector3(kat["kaynak"][0], kat["kaynak"][1], kat["kaynak"][2])
		# Kaynağın yer seviyesindeki yumuşak ışığı; gökte tek bir ışık noktası konmaz
		sahne._hale(p + Vector3(0, 30, 0), 700.0, nur_renk, 0.9, true)
		# Kaynağın üstünde yavaşça yükselen, ~400 m'de sönen zerreler
		k.parcacik(140, p + Vector3(0, 150, 0), Vector3(800, 140, 500), 12.0, nur_renk, 3.0,
			Vector3(0, 6.0, 0), 4.0, 30.0)


## En altta bulut denizi: ilk katın dilimi onun üstünde yüzer (eski boş pembe alanın yerine).
func _bulut_denizi() -> void:
	var o: Dictionary = veri["olcu"]
	var pm := PlaneMesh.new()
	pm.size = Vector2(44000, 44000)
	pm.subdivide_width = 160
	pm.subdivide_depth = 160
	var mat := ShaderMaterial.new()
	mat.shader = load(SHADER + "bulut_denizi.gdshader")
	mat.set_shader_parameter("kabarma", 300.0)
	mat.set_shader_parameter("olcek", 0.00035)
	mat.set_shader_parameter("oz_isik", 0.85)
	mat.set_shader_parameter("kabarcik", 1.0)
	for a in ["acik", "golge", "isima", "isima_guc"]:
		k.bagla(mat, "shader_parameter/" + a, k.yol("bulut_denizi/" + a))
	pm.material = mat
	var mi := MeshInstance3D.new()
	mi.mesh = pm
	mi.position = Vector3(0, -float(o["kat_t"]) - 420.0, -15000.0)
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	kok.add_child(mi)


## Arsanın nuru (Tûbâ çekirdeği): kesitte ekranda sabit boyutlu yumuşak bir hale; "buradasın".
## Açılıştaki yakınlaşmanın hedefidir. Gerçek Tûbâ piksel altında kalır.
func _arsa_isareti() -> void:
	var q := QuadMesh.new()
	q.size = Vector2(0.004, 0.004)
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	m.fixed_size = true
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.no_depth_test = false
	m.albedo_texture = sahne._isik_doku()
	k.bagla(m, "albedo_color", func(p: Dictionary) -> Color: return (p["parcacik"]["nur_renk"] as Color) * 2.2)
	_arsa_mat = m
	m.disable_fog = true
	q.material = m
	var mi := MeshInstance3D.new()
	mi.mesh = q
	mi.position = Vector3(0, 6, 0)
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	kok.add_child(mi)


## Yakınlaşma (K18): d dışarılık (1 kesit, 0 içeride), kam kameranın konumu.
## Kamera ilk katın havasına girince (kesme düzleminin arkasında, tavanın altında) kesit
## katmanı gizlenir: o an üst katlar tavanın ardındadır, tavan göğün aynısıdır, ilk katın
## perdesi erimiştir; içeriden üst tabaka görünmez (K10).
func uygula(d: float, kam: Vector3) -> void:
	var o: Dictionary = veri["olcu"]
	var ic := kam.z < float(o["kesme_z"]) - 1.0 and kam.y < float(o["hava"]) - 20.0
	kok.visible = not ic
	# İlk katın perdesi ve tavanlar: yaklaştıkça sanal gözün göğü gerçek bakış yönüne döner
	# (içeriden görülen gök), sonra perde erir; ardında içerideki gök ve ova vardır.
	var bant := smoothstep(0.3, 1.0, d)
	var pm := k.malzeme("kat_gogu_ilk") as ShaderMaterial
	pm.set_shader_parameter("bant", bant)
	pm.set_shader_parameter("opaklik", smoothstep(0.25, 0.7, d))
	(k.malzeme("kat_tavani") as ShaderMaterial).set_shader_parameter("bant", bant)
	if _arsa_mat:
		_arsa_mat.albedo_color.a = smoothstep(0.3, 0.8, d)
