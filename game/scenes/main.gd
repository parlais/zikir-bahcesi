extends Node3D
## Ana sahne: gökyüzü ve ışık, ada üzerindeki bahçe, yörünge kamera ve arayüz.
## Bahçenin canlılığı (hava kaynağı) ortamın renk doygunluğuna yansır:
## tevhid azaldığında bahçe solar ama asla ölmez.

@onready var _env: WorldEnvironment = $Ortam
@onready var _kamera: Camera3D = $KameraPivot/Kamera
@onready var _pivot: Node3D = $KameraPivot

var _yaw := 0.0
var _pitch := -32.0
var _mesafe := 13.5
var _dokunuslar: Dictionary = {}


func _ready() -> void:
	_ortam_kur()
	_kamera_uygula()
	Game.durum_degisti.connect(_canlilik_uygula)
	_canlilik_uygula()


func _ortam_kur() -> void:
	var sky_mat := ProceduralSkyMaterial.new()
	sky_mat.sky_top_color = Color("7fb6d8")
	sky_mat.sky_horizon_color = Color("f3e3c4")
	sky_mat.ground_bottom_color = Color("c9d8d8")
	sky_mat.ground_horizon_color = Color("f3e3c4")
	sky_mat.sun_angle_max = 20.0
	var sky := Sky.new()
	sky.sky_material = sky_mat
	var e := Environment.new()
	e.background_mode = Environment.BG_SKY
	e.sky = sky
	e.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	e.ambient_light_energy = 0.75
	e.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	e.adjustment_enabled = true
	e.fog_enabled = true
	e.fog_light_color = Color("f3e3c4")
	e.fog_density = 0.004
	e.fog_sky_affect = 0.0
	_env.environment = e


func _canlilik_uygula() -> void:
	var c := Game.engine.canlilik("hava")
	_env.environment.adjustment_saturation = lerpf(0.55, 1.0, c)
	_env.environment.adjustment_brightness = lerpf(0.94, 1.0, c)


func _kamera_uygula() -> void:
	_pivot.rotation_degrees = Vector3(_pitch, _yaw, 0)
	_kamera.position = Vector3(0, 0, _mesafe)


## Tek parmakla sürükleyince döner, iki parmakla sıkıştırınca yakınlaşır.
## Arayüzün yakaladığı dokunuşlar buraya gelmez (_unhandled_input).
func _unhandled_input(ev: InputEvent) -> void:
	if ev is InputEventScreenTouch:
		if ev.pressed:
			_dokunuslar[ev.index] = ev.position
		else:
			_dokunuslar.erase(ev.index)
	elif ev is InputEventScreenDrag:
		if _dokunuslar.size() >= 2:
			var eski: Vector2 = _dokunuslar[ev.index]
			var diger: Vector2 = _dokunuslar.values()[0] if _dokunuslar.keys()[0] != ev.index else _dokunuslar.values()[1]
			var fark: float = eski.distance_to(diger) - ev.position.distance_to(diger)
			_mesafe = clampf(_mesafe + fark * 0.03, 8.0, 22.0)
		else:
			_yaw -= ev.relative.x * 0.3
			_pitch = clampf(_pitch - ev.relative.y * 0.2, -70.0, -12.0)
		_dokunuslar[ev.index] = ev.position
		_kamera_uygula()
	elif ev is InputEventMouseButton and ev.pressed:
		if ev.button_index == MOUSE_BUTTON_WHEEL_UP:
			_mesafe = clampf(_mesafe - 0.8, 8.0, 22.0)
		elif ev.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			_mesafe = clampf(_mesafe + 0.8, 8.0, 22.0)
		_kamera_uygula()
