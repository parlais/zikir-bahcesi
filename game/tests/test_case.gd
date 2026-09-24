class_name TestCase
extends RefCounted
## Test dosyalarının temel sınıfı: hata biriktiren basit karşılaştırmalar.

var hatalar: Array[String] = []


func esit(gercek, beklenen, mesaj := "") -> void:
	if typeof(gercek) != typeof(beklenen) and not (_sayi(gercek) and _sayi(beklenen)):
		hatalar.append("%s: beklenen %s (%s), gelen %s (%s)" % [mesaj, beklenen, type_string(typeof(beklenen)), gercek, type_string(typeof(gercek))])
	elif gercek != beklenen:
		hatalar.append("%s: beklenen %s, gelen %s" % [mesaj, beklenen, gercek])


func dogru(kosul: bool, mesaj := "") -> void:
	if not kosul:
		hatalar.append(mesaj if mesaj != "" else "koşul yanlış")


func _sayi(v) -> bool:
	return typeof(v) == TYPE_INT or typeof(v) == TYPE_FLOAT


## Olay listesinde belirli türde ve alanlarda olay var mı?
func olay_var(olaylar: Array, tur: String, alanlar := {}) -> bool:
	for o in olaylar:
		if o["tur"] != tur:
			continue
		var uyar := true
		for k in alanlar:
			if o.get(k) != alanlar[k]:
				uyar = false
		if uyar:
			return true
	return false
