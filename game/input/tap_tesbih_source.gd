class_name TapTesbihSource
extends ZikirInputSource
## Dokunmatik tesbih: her zaman açık yedek giriş (rapor §3d).


func _init() -> void:
	kesin = true


func dokun(key: String) -> void:
	var t := ZikirInputSource.simdi()
	soz_algilandi.emit(key, t, t)
