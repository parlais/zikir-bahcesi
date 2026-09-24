extends SceneTree
## Bağımlılıksız test koşucusu:
##   godot --headless --path game -s res://tests/run_tests.gd
## tests/ altındaki test_*.gd dosyalarındaki test_* fonksiyonlarını çalıştırır.
## Her test dosyası TestCase'ten türer.

func _init() -> void:
	var dosyalar: Array[String] = []
	for f in DirAccess.get_files_at("res://tests"):
		if f.begins_with("test_") and f.ends_with(".gd"):
			dosyalar.append(f)
	dosyalar.sort()
	var gecen := 0
	var kalan: Array[String] = []
	for f in dosyalar:
		var script: GDScript = load("res://tests/" + f)
		for m in script.get_script_method_list():
			var ad: String = m["name"]
			if not ad.begins_with("test_"):
				continue
			var t: TestCase = script.new()
			t.call(ad)
			if t.hatalar.is_empty():
				gecen += 1
			else:
				for h in t.hatalar:
					kalan.append("%s::%s  %s" % [f, ad, h])
	for h in kalan:
		printerr("BAŞARISIZ  " + h)
	print("%d test geçti, %d hata." % [gecen, kalan.size()])
	quit(1 if not kalan.is_empty() else 0)
