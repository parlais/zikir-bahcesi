class_name Content
extends RefCounted
## game/data/*.json dosyalarını yükler ve tetikleyici anahtarlarına göre dizinler.
##
## Tetikleyici anahtarı, sayaçların tutulduğu ortak dildir:
##   "tevhid", "salavat"        zikir, dua veya sure kimliği
##   "salavat@cuma"             koşullu söz (koşul sağlandığında ayrıca sayılır)
##   "esma:nur"                 esma
##   "item:define_sandigi"      bir item kazanıldığında türeyen item
## Veri, tools/content/build_content.py ile docs/asset-listesi.md'den üretilir.

const DATA_DIR := "res://data/"

var meta: Dictionary = {}
var assets: Dictionary = {}      ## id -> asset
var esma: Dictionary = {}        ## id -> esma
var zikirler: Dictionary = {}    ## id -> söz
var tarifler: Dictionary = {}    ## id -> tarif
## anahtar -> [asset id] (sayaçla ilerleyenler; kural "birikimli" veya "toplam").
##   birikimli  her eşikte yeniden verilir (her 100 istiğfarda nisan yağmuru)
##   toplam     ömür boyu toplamla bir kez verilir, tekrarlanmaz (Tûbâ; 100, 300,
##              700 ve 1000 istiğfarda dört ırmak)
## Aynı anahtarı paylaşanların sırası, aynı sayıda gelen olayların sırasıdır:
## önce birinci item'lar, sonra "ikinci item"; eşitlikte asset listesindeki sıra
## (nisan yağmuru A bölümünde, ırmaklar D bölümünde: önce yağmur, sonra ırmak).
var by_key: Dictionary = {}
## anahtar -> [asset id] (her N sözde bir kazanılanlar)
var her_n_by_key: Dictionary = {}
## anahtar -> [asset id] (N kez art arda söylenince tetiklenenler)
var ardisik_by_key: Dictionary = {}
## anahtar -> [asset id] (sürekli kaynak; örn. tevhid -> sabâ yeli)
var surekli_by_key: Dictionary = {}
## "item:<id>" -> [asset id] (bir item kazanılınca türeyenler)
var turev_by_key: Dictionary = {}
## esma anahtarı -> öğretici kart (celâlî isimler)
var kart_by_key: Dictionary = {}
## asset id -> asset listesindeki sıra (assets.json'daki yeri)
var liste_sirasi: Dictionary = {}


static func load_default() -> Content:
	var c := Content.new()
	c.load_from(DATA_DIR)
	return c


func load_from(dir: String) -> void:
	var a: Dictionary = _read(dir + "assets.json")
	meta = a["meta"]
	for x in a["assets"]:
		liste_sirasi[x["id"]] = assets.size()
		assets[x["id"]] = x
	for x in _read(dir + "esma.json")["esma"]:
		esma[x["id"]] = x
	for x in _read(dir + "zikirler.json")["zikirler"]:
		zikirler[x["id"]] = x
	for x in _read(dir + "tarifler.json")["tarifler"]:
		tarifler[x["id"]] = x
	_index()


func _read(path: String) -> Dictionary:
	var text := FileAccess.get_file_as_string(path)
	assert(text != "", "İçerik dosyası okunamadı: " + path)
	var parsed = JSON.parse_string(text)
	assert(parsed is Dictionary, "İçerik dosyası bozuk: " + path)
	return parsed


func _index() -> void:
	for id in assets:
		var a: Dictionary = assets[id]
		var t: Dictionary = a["tetikleyici"]
		for key in trigger_keys(t):
			match t["tur"]:
				"esma_kart":
					_add(kart_by_key, key, id)
				"item":
					_add(turev_by_key, key, id)
				"zikir", "sure", "esma":
					match t["kural"]:
						"her_n":
							_add(her_n_by_key, key, id)
						"ardisik":
							_add(ardisik_by_key, key, id)
						"surekli":
							_add(surekli_by_key, key, id)
						_:
							_add(by_key, key, id)
	# Aynı tetikleyiciyi paylaşanlar: önce birinci item'lar, sonra "ikinci item";
	# eşitlikte liste sırası. sort_custom kararlı değildir, sıra açıkça verilir.
	for key in by_key:
		by_key[key].sort_custom(_once_gelir)


func _add(d: Dictionary, key: String, id: String) -> void:
	if not d.has(key):
		d[key] = []
	d[key].append(id)


## Bir tetikleyicinin sayaç anahtarları (liste kaynaklı surelerde birden çok).
static func trigger_keys(t: Dictionary) -> Array[String]:
	var out: Array[String] = []
	var kaynaklar: Array = t["kaynak"] if t["kaynak"] is Array else [t["kaynak"]]
	for k in kaynaklar:
		if k == null:
			continue
		var key: String
		match t["tur"]:
			"esma", "esma_kart":
				key = "esma:" + str(k)
			"item":
				key = "item:" + str(k)
			"zikir", "sure":
				key = str(k)
			_:
				continue
		if t.get("kosul") != null:
			key += "@" + str(t["kosul"])
		out.append(key)
	return out


func _once_gelir(x: String, y: String) -> bool:
	if sira(x) != sira(y):
		return sira(x) < sira(y)
	return int(liste_sirasi[x]) < int(liste_sirasi[y])


## Ömür boyu toplamla bir kez verilen, tekrarlanmayan asset mi (Tûbâ, ırmaklar)?
func tekrarsiz(asset_id: String) -> bool:
	return assets[asset_id]["tetikleyici"]["kural"] == "toplam"


## 1: tetikleyicinin ilk item'ı, 2: "ikinci item" notlu olan.
func sira(asset_id: String) -> int:
	var n = assets[asset_id]["tetikleyici"].get("not")
	return 2 if n != null and str(n).contains("ikinci item") else 1


## Bu anahtarı paylaşan item'ların kaç ayrı sıra grubu olduğu (1 veya 2).
func sira_sayisi(key: String) -> int:
	var m := 1
	for id in by_key.get(key, []):
		m = maxi(m, sira(id))
	return m


func esikler(asset_id: String, ebced_modu: bool) -> Array:
	return assets[asset_id]["esikler" if ebced_modu else "esikler_serbest"]


func esma_hedefi(esma_id: String, ebced_modu: bool) -> int:
	if not ebced_modu:
		return int(meta["kurallar"]["serbest_esma_adedi"])
	return int(esma[esma_id]["ebced"])


## Ekranda gösterilecek ad: "esma:nur" -> "Yâ Nûr", "tevhid" -> "Lâ ilâhe illallâh".
func key_label(key: String) -> String:
	var base := key.get_slice("@", 0)
	if base.begins_with("esma:"):
		var e: Dictionary = esma[base.trim_prefix("esma:")]
		return e["ad"] if e["id"] == "allah" else "Yâ " + str(e["ad"])
	if zikirler.has(base):
		return zikirler[base]["ad"]
	return key
