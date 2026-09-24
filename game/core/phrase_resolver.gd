class_name PhraseResolver
extends RefCounted
## Ses tanımadan gelen algılamaları kesinleştirir.
##
## Asset listesi H bölümü: "Sübhanallah" üç ayrı zikrin, "La ilahe illallah"
## tehlil-i kebirin başlangıcıdır; "La havle" ile "Mâşâallah" aynı sözlerle
## biter. Sistem ifade bitmeden ödül vermemelidir. Kurallar:
##   1. Başka bir sözün başı olan söz, bekleme süresi dolana kadar tutulur.
##   2. Zamanda çakışan iki algılamadan uzun süreni kazanır.
## Dokunmatik tesbih bu katmandan geçmez; kullanıcı sözü açıkça seçer.

## Önek sözün, devamı gelir mi diye bekletildiği süre (saniye).
var bekleme := 1.2
## zikir id -> bu sözle başlayan uzun sözler
var _onek_of: Dictionary = {}
## Bekleyen algılamalar: {key, bas, son}
var _bekleyen: Array = []


func _init(zikirler: Dictionary = {}) -> void:
	for id in zikirler:
		var liste: Array = zikirler[id].get("onek_of", [])
		if not liste.is_empty():
			_onek_of[id] = liste


## Bir algılama ekler. bas/son: sözün başladığı ve bittiği an (saniye).
func ekle(key: String, bas: float, son: float) -> void:
	var yeni := {"key": key, "bas": bas, "son": son}
	var kalan: Array = []
	for b in _bekleyen:
		if _cakisir(b, yeni):
			if _sure(b) >= _sure(yeni):
				return  # Mevcut uzun algılama kazanır; yeni kısa olan atılır.
			continue  # Yeni uzun algılama eskisini düşürür.
		kalan.append(b)
	kalan.append(yeni)
	_bekleyen = kalan


## Kesinleşen sözleri sırayla döndürür ve bekleyenlerden çıkarır.
func guncelle(simdi: float) -> Array[String]:
	var cikan: Array[String] = []
	var kalan: Array = []
	for b in _bekleyen:
		var tut := bekleme if _onek_of.has(b["key"]) else 0.0
		if simdi >= b["son"] + tut:
			cikan.append(b["key"])
		else:
			kalan.append(b)
	_bekleyen = kalan
	return cikan


func bekleyen_sayisi() -> int:
	return _bekleyen.size()


static func _cakisir(a: Dictionary, b: Dictionary) -> bool:
	return a["bas"] < b["son"] and b["bas"] < a["son"]


static func _sure(a: Dictionary) -> float:
	return a["son"] - a["bas"]
