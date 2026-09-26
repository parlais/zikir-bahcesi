class_name DunyaYuvalari
extends RefCounted
## Nimetlerin dünyadaki sabit yerleri (yuvalar, K20). game/data/dunya_cennet.json
## dosyasının "yuvalar" alanından okunur; model fabrikası üretir
## (tools/model_factory/models/dunya_yuvalari.py).
##
## Alanın biçimi:
##   {"arsa": [yuva, ...], "cevre": [yuva, ...], "ayak": {asset_id: taban yarıçapı}}
##   yuva: [x, y, z, dönüş (derece, y ekseni), ölçek, asset_id, sıra]
## Sıra kalıcıdır: bir asset'in yuvaları sıraya göre dolar (olgun örnekler ilk
## yuvalara, büyüyen örnek bir sonrakine). Liste yalnız sona eklenir.
## Yuvanın ilk beş alanı sahnedeki yerleşim listeleriyle aynıdır (SahneKurucu).

const VARSAYILAN_YOL := "res://data/dunya_cennet.json"

## Bölge adı -> [yuva] (sıraya göre).
var bolgeler: Dictionary = {}
## Asset id -> modelin taban yarıçapı (ölçeksiz, m); çakışma denetimi için.
var ayak: Dictionary = {}
var _by_asset: Dictionary = {}   ## asset id -> [yuva] (sıraya göre)
var _bolge: Dictionary = {}      ## sıra -> bölge adı


## dunya_cennet.json dosyasından okur. Dosya ya da alan yoksa boş döner (uyarıyla).
static func yukle(yol: String = VARSAYILAN_YOL) -> DunyaYuvalari:
	var y := DunyaYuvalari.new()
	var text := FileAccess.get_file_as_string(yol)
	var parsed = JSON.parse_string(text) if text != "" else null
	if not parsed is Dictionary or not parsed.has("yuvalar"):
		push_warning("Dünya yuvaları okunamadı: " + yol)
		return y
	y.kur(parsed["yuvalar"])
	return y


## Sözlükten kurar (testler için). d, "yuvalar" alanının kendisidir; bölge
## listelerinin yanında düz bir yuva dizisi de verilebilir (bölgesi "arsa" sayılır).
static func sozlukten(d) -> DunyaYuvalari:
	var y := DunyaYuvalari.new()
	y.kur(d if d is Dictionary else {"arsa": d})
	return y


func kur(d: Dictionary) -> void:
	bolgeler.clear()
	ayak.clear()
	_by_asset.clear()
	_bolge.clear()
	for anahtar in d:
		if anahtar == "ayak":
			for id in d["ayak"]:
				ayak[str(id)] = float(d["ayak"][id])
			continue
		if not d[anahtar] is Array:
			continue
		var liste: Array = []
		for ham in d[anahtar]:
			var yuva := _duzelt(ham)
			liste.append(yuva)
			_bolge[sira(yuva)] = str(anahtar)
			var id := asset(yuva)
			if not _by_asset.has(id):
				_by_asset[id] = []
			_by_asset[id].append(yuva)
		liste.sort_custom(_sira_once)
		bolgeler[str(anahtar)] = liste
	for id in _by_asset:
		_by_asset[id].sort_custom(_sira_once)


## Yuvası olan asset'ler (alfabetik).
func assetler() -> Array:
	var out := _by_asset.keys()
	out.sort()
	return out


## Bir asset'in yuvaları, sıraya göre.
func yuvalar(asset_id: String) -> Array:
	return _by_asset.get(asset_id, [])


func sayi(asset_id: String) -> int:
	return yuvalar(asset_id).size()


## Bütün yuvalar, sıraya göre.
func hepsi() -> Array:
	var out: Array = []
	for b in bolgeler:
		out.append_array(bolgeler[b])
	out.sort_custom(_sira_once)
	return out


func bolge(yuva: Array) -> String:
	return _bolge.get(sira(yuva), "")


## Yuvanın taban yarıçapı (ölçekli, m). Tabloda yoksa 0.
func ayak_r(yuva: Array) -> float:
	return float(ayak.get(asset(yuva), 0.0)) * olcek(yuva)


static func konum(yuva: Array) -> Vector3:
	return Vector3(yuva[0], yuva[1], yuva[2])


static func donus(yuva: Array) -> float:
	return yuva[3]


static func olcek(yuva: Array) -> float:
	return yuva[4]


static func asset(yuva: Array) -> String:
	return yuva[5]


static func sira(yuva: Array) -> int:
	return yuva[6]


## JSON sayıları float döner: sırayı tam sayıya, asset'i metne çevirir.
static func _duzelt(ham: Array) -> Array:
	return [float(ham[0]), float(ham[1]), float(ham[2]), float(ham[3]), float(ham[4]), str(ham[5]), int(ham[6])]


static func _sira_once(a: Array, b: Array) -> bool:
	return int(a[6]) < int(b[6])
