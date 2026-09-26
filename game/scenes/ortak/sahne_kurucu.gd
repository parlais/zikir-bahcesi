class_name SahneKurucu
extends RefCounted
## Stil ve dünya sahnelerinin ortak kurucusu: glTF malzeme adına göre stil
## shader'ı, model örnekleme, MultiMesh ile çoğaltma, parçacıklar, ortam
## (gökyüzü, sis, küresel aydınlatma) ve ana ışık.
##
##   var k := SahneKurucu.new(self, profil)
##   k.goruntu_kalitesi()
##   k.ortam_kur()
##   k.ornek("ZB_yapi_kosk", [x, y, z, donus_derece, olcek])
##
## Profil şeması StilProfilleri ile aynıdır (gunes, gok, ortam, ortak, malzeme...).
##
## Işık geçişi (K12): guncelle(profil) ortamı, gökyüzünü, ana ışığı, malzemeleri
## ve bağları (bagla) yeni profile göre yeniden ayarlar. Yapı (SDFGI, SSR, sisin
## açık olup olmadığı, parıltı kipi) kurulduğu gibi kalır.

const MODELLER := "res://assets/models/"
const SHADER := "res://scenes/stil/shader/"
const DOKULAR := "res://assets/dokular/"
## Kesitte uzak ağaçların en çok büyütmesi (K20): gerçek boyda dikey ekranda 2-4 piksel kalıyorlardı
const AGAC_BUYUT := 1.8

## glTF malzeme adı -> [shader, sabit parametreler, profil malzeme anahtarı]
const MALZEME_TABLOSU := {
	"mat": ["yuzey", {"puruz": 0.75, "detay": 0.05}, ""],
	"tas": ["yuzey", {"puruz": 0.5, "detay": 0.12, "detay_olcek": 0.9}, "tas"],
	"govde": ["yuzey", {"puruz": 0.95, "detay": 0.25, "detay_olcek": 5.0}, ""],
	"metal": ["yuzey", {"puruz": 0.32, "metal": 0.85, "detay": 0.0}, "altin"],
	"altin": ["yuzey", {"puruz": 0.3, "metal": 0.9, "detay": 0.0}, "altin"],
	"kursun": ["yuzey", {"puruz": 0.45, "metal": 0.6, "detay": 0.05}, ""],
	"inci": ["yuzey", {"puruz": 0.25, "detay": 0.0}, "inci"],
	"uzak": ["yuzey", {"puruz": 1.0, "detay": 0.1, "detay_olcek": 0.02}, "uzak"],
	"zemin": ["zemin", {"spek": 0.03}, "zemin"],
	"yaprak": ["yaprak", {"spek": 0.03}, "yaprak"],
	"cimen_ot": ["cimen", {"spek": 0.03}, "cimen"],
	"cicek": ["cicek", {}, "cicek"],
	"meyve": ["cicek", {"ruzgar": 0.08}, "cicek"],
	"cini": ["cini", {}, "cini"],
	"su": ["su", {}, "su"],
	"nur": ["yuzey", {"puruz": 0.4, "detay": 0.0, "isima": Color(1.0, 0.8, 0.45)}, "nur"],
	# Cennet mekânı (Faz 2a)
	"sut": ["su", {"derin": Color("d8d4cc"), "sig": Color("fbf8f0"), "puruz": 0.12}, "sut"],
	"bal": ["su", {"derin": Color("8a4a08"), "sig": Color("eaa030")}, "bal"],
	"serbet": ["su", {"derin": Color("5a0618"), "sig": Color("d8305a")}, "serbet"],
	"selale": ["selale", {}, "selale"],
	"selale_pus": ["selale", {"pus": 1.0}, "selale"],
	"tugla": ["tugla", {}, "tugla"],
	"kumas": ["yuzey", {"puruz": 0.95, "detay": 0.05, "detay_olcek": 14.0, "spek": 0.08}, "kumas"],
	"tavan": ["tavan", {}, "tavan"],
	# Dallanan ağaçlar (K15): kabuk dokusu; "yaprak_*" adları _satir() ile yaprak_kart'a gider.
	"kabuk": ["kabuk", {"doku": DOKULAR + "kabuk.png", "doku_n": DOKULAR + "kabuk_n.png", "golge_alma": 0.75,
		"spek": 0.1}, ""],
	# Tûbâ (K17): gümüş-fildişi kabuk hafifçe kendi ışığıyla parlar; yaprak kenarlarındaki
	# altın-beyaz ışıltı da öyle
	"kabuk_tuba": ["kabuk", {"doku": DOKULAR + "kabuk_tuba.png", "doku_n": DOKULAR + "kabuk_tuba_n.png",
		"golge_alma": 0.6, "spek": 0.15, "isima_guc": 0.22, "isima_renk": Color(1.0, 0.93, 0.78)}, ""],
	"yaprak_tuba": ["yaprak_kart", {"doku": DOKULAR + "yaprak_tuba.png", "golge_alma": 0.5, "spek": 0.05,
		"isima_guc": 0.9, "isima_renk": Color(1.0, 0.88, 0.6)}, "yaprak"],
	# Kesit (K10, K18): öteki katların zemini (çimen katın tonuyla çarpılır), kesit yüzü
	# (za'ferân toprak), katın göğü, merdiven şeridi, uzak siluetler
	"zemin_kesit": ["zemin", {"spek": 0.03, "kose_ton": 1.0}, "zemin"],
	"kesit_yuzu": ["kesit_yuzu", {"doku": DOKULAR + "kesit_toprak.png", "doku_n": DOKULAR + "kesit_toprak_n.png"},
		"kesit_yuzu"],
	"kat_gogu": ["kat_gogu", {}, "kat_gogu"],
	# İlk katın perdesi (yakınlaşmada erir) ve katların tavanı (gerçek bakış yönüyle göğün aynısı)
	"kat_gogu_ilk": ["kat_gogu_saydam", {}, "kat_gogu"],
	"kat_tavani": ["kat_gogu", {}, "kat_gogu"],
	"kesit_serit": ["kesit_serit", {}, "kesit_serit"],
	"kesit_agac": ["kesit_agac", {"atlas": DOKULAR + "kesit_siluet.png", "golge_alma": 0.5, "spek": 0.05}, "yaprak"],
}

var kok: Node3D
var profil: Dictionary
var ortam: Environment
var gok_malzeme: ShaderMaterial
var gunes: DirectionalLight3D
## Işık geçişinde ikinci ışık (profilde "gunes_b" varsa): çapraz geçiş, K13.
var gunes_b: DirectionalLight3D
var _malzemeler: Dictionary = {}
## [nesne, özellik, Callable(profil) -> değer]
var _baglar: Array = []


func _init(k: Node3D, p: Dictionary) -> void:
	kok = k
	profil = p


# --------------------------------------------------------------------------
# Görüntü ve ortam
# --------------------------------------------------------------------------

func goruntu_kalitesi(vp: Viewport = null) -> void:
	if vp == null:
		vp = kok.get_viewport()
	vp.msaa_3d = Viewport.MSAA_4X
	vp.screen_space_aa = Viewport.SCREEN_SPACE_AA_FXAA
	vp.positional_shadow_atlas_size = 4096
	RenderingServer.directional_shadow_atlas_set_size(8192, true)
	RenderingServer.directional_soft_shadow_filter_set_quality(RenderingServer.SHADOW_QUALITY_SOFT_HIGH)


## Gökyüzü, Environment ve ana ışık. Döndürdüğü ışık profilin "gunes" alanından
## kurulur (cennet sahnelerinde güneş diski görünmez; yalnızca yön ve gölge verir).
func ortam_kur(gok_shader := SHADER + "gok.gdshader") -> DirectionalLight3D:
	var o: Dictionary = profil["ortam"]
	gok_malzeme = ShaderMaterial.new()
	gok_malzeme.shader = load(gok_shader)
	var sky := Sky.new()
	sky.sky_material = gok_malzeme
	sky.radiance_size = Sky.RADIANCE_SIZE_256
	sky.process_mode = Sky.PROCESS_MODE_INCREMENTAL

	var e := Environment.new()
	ortam = e
	e.background_mode = Environment.BG_SKY
	e.sky = sky
	e.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	e.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	match o["ton"]:
		"aces":
			e.tonemap_mode = Environment.TONE_MAPPER_ACES
		"agx":
			e.tonemap_mode = Environment.TONE_MAPPER_AGX
		_:
			e.tonemap_mode = Environment.TONE_MAPPER_FILMIC

	e.glow_enabled = true
	match o.get("parlama_kip", ""):
		"screen":
			e.glow_blend_mode = Environment.GLOW_BLEND_MODE_SCREEN
		"softlight":
			e.glow_blend_mode = Environment.GLOW_BLEND_MODE_SOFTLIGHT
		"additive":
			e.glow_blend_mode = Environment.GLOW_BLEND_MODE_ADDITIVE
		_:
			e.glow_blend_mode = Environment.GLOW_BLEND_MODE_SOFTLIGHT if o["parlama"][0] < 0.5 else Environment.GLOW_BLEND_MODE_SCREEN
	var seviye: Array = o.get("parlama_seviye", [0.0, 0.3, 0.6, 0.9, 1.0, 0.8, 0.5])
	for i in 7:
		e.set_glow_level(i, seviye[i])

	e.fog_enabled = true
	if o.has("sis_yukseklik"):  # [yükseklik, yoğunluk]: alçak yerlerde pus
		e.fog_height = o["sis_yukseklik"][0]
		e.fog_height_density = o["sis_yukseklik"][1]
	var h: Array = o["hacim_sis"]  # yoğunluk, renk, anizotropi, uzunluk
	if h[0] > 0.0:
		e.volumetric_fog_enabled = true
		e.volumetric_fog_length = h[3]
		e.volumetric_fog_detail_spread = 1.5
		e.volumetric_fog_sky_affect = 0.0

	e.sdfgi_enabled = o["sdfgi"]
	e.sdfgi_use_occlusion = true
	e.sdfgi_cascades = o.get("sdfgi_kademe", 4)
	e.sdfgi_min_cell_size = o.get("sdfgi_hucre", 0.25)
	e.ssao_enabled = o["ssao"] > 0.0
	e.ssao_radius = 1.2
	e.ssil_enabled = true
	e.ssr_enabled = o["ssr"]
	e.ssr_max_steps = 96
	e.ssr_fade_in = 0.05
	e.ssr_fade_out = 1.5
	e.adjustment_enabled = true
	var we := WorldEnvironment.new()
	we.environment = e
	kok.add_child(we)

	gunes = _isik_kur()
	if profil.has("gunes_b"):
		gunes_b = _isik_kur()

	_gok_ayarla()
	_ortam_ayarla()
	_gunes_ayarla()
	kesit_globalleri()
	return gunes


## Kesit (K18): katların pusu ve ışığı için global shader parametreleri. kesit: 0 içeride
## (pus etkisiz), 1 dışarıdan kesitte; yakınlaşmada kameranın konumuna göre arada.
var kesit_dislik := 0.0


func kesit_globalleri() -> void:
	RenderingServer.global_shader_parameter_set("zb_kesit", kesit_dislik)
	# Kesitte uzak ağaçların en çok büyütmesi (K20); --zb-ayar="agac_buyut=2" ile denenir
	RenderingServer.global_shader_parameter_set("zb_agac_buyut", float(profil.get("agac_buyut", AGAC_BUYUT)))
	if profil.has("kesit_pus"):
		var kp: Dictionary = profil["kesit_pus"]
		# Uzak zemin, katın göğünün ufkuna karışır (perdenin altıyla zemin arasında dikiş kalmasın)
		var ufuk: Color = profil["kat_gok"]["ufuk"] if profil.has("kat_gok") else kp["ufuk"]
		RenderingServer.global_shader_parameter_set("zb_pus_ufuk", ufuk)
		RenderingServer.global_shader_parameter_set("zb_pus_gok", kp["gok"])
		RenderingServer.global_shader_parameter_set("zb_pus_nur", kp["nur"])


## Işık geçişi (K12): profil değişince sürekli değerleri yeniden ayarlar.
func guncelle(p: Dictionary) -> void:
	profil = p
	kesit_globalleri()
	if gok_malzeme:
		_gok_ayarla()
	if ortam:
		_ortam_ayarla()
	if gunes:
		_gunes_ayarla()
	for ad in _malzemeler:
		if _malzemeler[ad]:
			_malzeme_ayarla(ad, _malzemeler[ad])
	for b in _baglar:
		(b[0] as Object).set(b[1], (b[2] as Callable).call(p))


## Profilden okunan bir değeri bir nesnenin özelliğine bağlar: hemen atar,
## guncelle()'de yeniden hesaplar. fn: Callable(profil) -> değer.
func bagla(nesne: Object, ozellik: StringName, fn: Callable) -> void:
	nesne.set(ozellik, fn.call(profil))
	_baglar.append([nesne, ozellik, fn])


## Profildeki bir yolu okuyan bağ fonksiyonu, ör. yol("parcacik/nur_renk", 2.0).
func yol(y: String, carpan := 1.0) -> Callable:
	var parca := y.split("/")
	return func(p: Dictionary) -> Variant:
		var d: Variant = p
		for s in parca:
			d = d[int(s)] if d is Array else d[s]
		return d * carpan


func _gok_ayarla() -> void:
	var g: Dictionary = profil["gok"]
	for k in g:
		gok_malzeme.set_shader_parameter(k, g[k])


func _ortam_ayarla() -> void:
	var o: Dictionary = profil["ortam"]
	var e := ortam
	e.ambient_light_energy = o["ambient"]
	e.tonemap_exposure = o["pozlama"]
	e.tonemap_white = o["beyaz"]
	var p: Array = o["parlama"]  # yoğunluk, güç, bloom, hdr eşiği
	e.glow_intensity = p[0]
	e.glow_strength = p[1]
	e.glow_bloom = p[2]
	e.glow_hdr_threshold = p[3]
	var s: Array = o["sis"]  # yoğunluk, renk, güneş saçılımı, gökyüzü etkisi
	e.fog_density = s[0]
	e.fog_light_color = s[1]
	e.fog_sun_scatter = s[2]
	e.fog_sky_affect = s[3]
	e.fog_aerial_perspective = o.get("hava_perspektif", 0.2)
	if e.volumetric_fog_enabled:
		var h: Array = o["hacim_sis"]
		e.volumetric_fog_density = h[0]
		e.volumetric_fog_albedo = h[1]
		e.volumetric_fog_anisotropy = h[2]
	e.ssao_intensity = o["ssao"] * 2.0
	e.adjustment_saturation = o["doygunluk"]
	e.adjustment_contrast = o["kontrast"]
	e.adjustment_brightness = o["parlaklik"]


func _isik_kur() -> DirectionalLight3D:
	var l := DirectionalLight3D.new()
	kok.add_child(l)
	l.light_volumetric_fog_energy = 1.6
	l.sky_mode = DirectionalLight3D.SKY_MODE_LIGHT_AND_SKY
	l.shadow_enabled = true
	l.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS
	return l


func _gunes_ayarla() -> void:
	_isik_ayarla(gunes, profil["gunes"])
	if gunes_b:
		_isik_ayarla(gunes_b, profil["gunes_b"])


func _isik_ayarla(l: DirectionalLight3D, gp: Dictionary) -> void:
	var el := deg_to_rad(gp["yukseklik"])
	var az := deg_to_rad(gp["yon"])
	var yon := Vector3(cos(el) * sin(az), sin(el), cos(el) * cos(az))
	l.position = yon * 100.0
	l.look_at(Vector3.ZERO, Vector3.UP if absf(yon.y) < 0.99 else Vector3.FORWARD)
	l.light_color = gp["renk"]
	l.light_energy = gp["enerji"]
	l.light_angular_distance = gp["yumusak"]
	l.shadow_blur = gp.get("golge_bulanik", 1.5)
	l.directional_shadow_max_distance = gp.get("golge_mesafe", 120.0)
	# Çapraz geçişte sönmüş ışık gizlenir; gölgesi boşuna çizilmez.
	l.visible = float(gp["enerji"]) > 0.0005


# --------------------------------------------------------------------------
# Malzemeler
# --------------------------------------------------------------------------

## glTF malzeme adına göre stil shader'ı (önbellekli).
## Tablo satırı. "yaprak_<tür>" malzemeleri o türün yaprak atlasıyla yaprak kartı
## shader'ına gider; profilden "yaprak" ayarlarını (ton, geçirgenlik) alır.
func _satir(ad: String) -> Array:
	if MALZEME_TABLOSU.has(ad):
		return MALZEME_TABLOSU[ad]
	if ad.begins_with("yaprak_"):
		return ["yaprak_kart", {"doku": DOKULAR + ad + ".png", "golge_alma": 0.5, "spek": 0.05}, "yaprak"]
	if ad.begins_with("kabuk_") or ad.begins_with("yuzey_"):
		# Dokulu yüzeyler (kabuk, dikim yerinin toprağı): kabuk shader'ı, dokusu adından
		var satir: Array = MALZEME_TABLOSU["kabuk"].duplicate(true)
		satir[1]["doku"] = DOKULAR + ad + ".png"
		satir[1]["doku_n"] = DOKULAR + ad + "_n.png"
		return satir
	return []


func malzeme(ad: String) -> Material:
	if _malzemeler.has(ad):
		return _malzemeler[ad]
	var satir: Array = _satir(ad)
	if satir.is_empty():
		_malzemeler[ad] = null
		return null
	var m := ShaderMaterial.new()
	m.shader = load(SHADER + satir[0] + ".gdshader")
	_malzeme_ayarla(ad, m)
	_malzemeler[ad] = m
	return m


## Sıra önemli: ortak, sonra tablodaki sabitler, en son profilin malzemeye özel değerleri.
func _malzeme_ayarla(ad: String, m: ShaderMaterial) -> void:
	var satir: Array = _satir(ad)
	var ortak: Dictionary = profil["ortak"]
	for k in ortak:
		m.set_shader_parameter(k, ortak[k])
	for k in satir[1]:
		var deger: Variant = satir[1][k]
		if deger is String and (deger as String).begins_with("res://"):
			deger = load(deger)
		m.set_shader_parameter(k, deger)
	var ozel: Dictionary = profil["malzeme"].get(satir[2], {})
	for k in ozel:
		m.set_shader_parameter(k, ozel[k])
	if ad == "uzak":
		m.set_shader_parameter("doygunluk", float(ortak.get("doygunluk", 1.0)) * 0.7)


func boya(n: Node) -> void:
	for mi in n.find_children("*", "MeshInstance3D", true, false):
		var mesh: Mesh = mi.mesh
		for i in mesh.get_surface_count():
			var eski := mesh.surface_get_material(i)
			var yeni := malzeme(eski.resource_name) if eski else null
			if yeni:
				mi.set_surface_override_material(i, yeni)
			elif eski is BaseMaterial3D:
				(eski as BaseMaterial3D).vertex_color_use_as_albedo = true


## Modeli sahneye koyar. t: [x, y, z, y ekseninde dönüş (derece), ölçek]
func ornek(model: String, t: Array, ek_olcek := 1.0, ebeveyn: Node = null) -> Node3D:
	var s: PackedScene = load(MODELLER + model + ".glb")
	var n: Node3D = s.instantiate()
	n.position = Vector3(t[0], t[1], t[2])
	n.rotation_degrees.y = t[3]
	n.scale = Vector3.ONE * float(t[4]) * ek_olcek
	(ebeveyn if ebeveyn else kok).add_child(n)
	boya(n)
	return n


# --------------------------------------------------------------------------
# MultiMesh ile çoğaltma
# --------------------------------------------------------------------------

func bitki_mesh(model: String) -> Mesh:
	var s: PackedScene = load(MODELLER + model + ".glb")
	var n := s.instantiate()
	var mi: MeshInstance3D = n.find_children("*", "MeshInstance3D", true, false)[0]
	var mesh: ArrayMesh = mi.mesh.duplicate()
	for i in mesh.get_surface_count():
		var eski := mesh.surface_get_material(i)
		var yeni := malzeme(eski.resource_name) if eski else null
		if yeni:
			mesh.surface_set_material(i, yeni)
	n.free()
	return mesh


## konumlar: [[x, y, z, dönüş, ölçek], ...]
## parca > 0 ise örnekler parca metrelik ızgara hücrelerine bölünür: her hücre kendi
## MultiMesh'idir ve ayrıntı düzeyi (LOD) hücrenin kameraya uzaklığına göre seçilir.
## Tek MultiMesh bütün örneklere en yakın örneğin ayrıntısını verirdi (K15 ağaçları).
## Kesit (K18): on_ebeveyn verilirse kesme düzleminin önündeki (z > kesme_z) örnekler
## ayrı MultiMesh'lere, o düğümün altına kurulur (kesitte gizlenir). Örnek başına renk
## farkı bütün listeden aynı sırayla üretilir; bölme görünüşü değiştirmez.
var on_ebeveyn: Node3D
var kesme_z := INF


## Örnekler parça hücrelerine bölünür; bütün hücreler (MultiMeshInstance3D) döner.
## agac: kesitte uzakta büyüyen ağaç (K20); büyüyen tepe sınır kutusundan taşmasın diye kırpma payı.
func coklu(model: String, konumlar: Array, golge := true, parca := 0.0, agac := false) -> Array[MultiMeshInstance3D]:
	var hucreler: Array[MultiMeshInstance3D] = []
	if konumlar.is_empty():
		return hucreler
	var mesh := bitki_mesh(model)
	var gruplar := {}
	for i in konumlar.size():
		var t: Array = konumlar[i]
		var anahtar := Vector3i.ZERO
		if parca > 0.0:
			anahtar = Vector3i(floori(float(t[0]) / parca), floori(float(t[2]) / parca), 0)
		if on_ebeveyn and float(t[2]) > kesme_z:
			anahtar.z = 1
		if not gruplar.has(anahtar):
			gruplar[anahtar] = []
		gruplar[anahtar].append(i)
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(model)
	var ozel := PackedColorArray()
	for i in konumlar.size():
		ozel.append(Color(rng.randf(), rng.randf(), 0, 0))
	for anahtar in gruplar:
		var sira: Array = gruplar[anahtar]
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.use_custom_data = true
		mm.mesh = mesh
		mm.instance_count = sira.size()
		for j in sira.size():
			var t: Array = konumlar[sira[j]]
			var b := Basis(Vector3.UP, deg_to_rad(t[3])).scaled(Vector3.ONE * float(t[4]))
			mm.set_instance_transform(j, Transform3D(b, Vector3(t[0], t[1], t[2])))
			mm.set_instance_custom_data(j, ozel[sira[j]])
		var mmi := MultiMeshInstance3D.new()
		mmi.multimesh = mm
		mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if golge else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		if agac:
			agac_isaretle(mmi)
		(on_ebeveyn if anahtar.z == 1 else kok).add_child(mmi)
		hucreler.append(mmi)
	return hucreler


## Ağaç örneği: kesitte uzakta hafifçe büyür (K20). Yalnız ağaçlara verilir; merdivenin
## sarmaşığı, köşkün ahşabı gibi aynı malzemeyi kullanan yapılar gerçek boyda kalır.
func agac_isaretle(n: Node) -> void:
	var liste: Array = [n] if n is GeometryInstance3D else []
	liste.append_array(n.find_children("*", "GeometryInstance3D", true, false))
	for g in liste:
		(g as GeometryInstance3D).set_instance_shader_parameter("agac_buyut", 1.0)
		(g as GeometryInstance3D).extra_cull_margin = 25.0


# --------------------------------------------------------------------------
# Parçacıklar
# --------------------------------------------------------------------------

func yuvarlak_doku() -> Texture2D:
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


## renk bir Color ya da Callable(profil) -> Color olabilir (yol() ile); Callable ise
## ışık geçişinde profile göre güncellenir. doku verilmezse yumuşak yuvarlak leke.
func parcacik(adet: int, merkez: Vector3, alan: Vector3, boy: float, renk: Variant, isik: float,
		yercekimi: Vector3, hiz: float, omur: float, billboard := BaseMaterial3D.BILLBOARD_ENABLED,
		doku: Texture2D = null) -> GPUParticles3D:
	var p := GPUParticles3D.new()
	p.amount = adet
	p.lifetime = omur
	p.preprocess = omur
	p.visibility_aabb = AABB(-alan * 1.5 - Vector3.ONE * boy, alan * 3.0 + Vector3.ONE * boy * 2.0)
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
	if renk is Callable:
		bagla(mat, "albedo_color", func(p: Dictionary) -> Color: return (renk as Callable).call(p) * (1.0 + isik))
	else:
		mat.albedo_color = renk * (1.0 + isik)
	mat.albedo_texture = doku if doku else yuvarlak_doku()
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	q.material = mat
	p.draw_pass_1 = q
	p.position = merkez
	kok.add_child(p)
	return p
