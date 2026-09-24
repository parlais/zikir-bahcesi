class_name RecipeSystem
extends RefCounted
## Tarif zincirleri (asset listesi G bölümü).
##
## Cezasızlık gereği bahçede duran hiçbir şey (bitki, yapı, canlı, kovan,
## şadırvan...) tarifte harcanmaz. Yalnızca malzeme niteliğindeki item'lar
## tüketilir. Gül balı için 100 gül ve bir kovan gerekir; ikisi de yerinde kalır.

const MALZEMELER := [
	"inci", "mercan", "sedef", "ipek_kozasi", "un_cuvali", "tas_firin_ve_ekmek",
	"zeytinyagi_testisi",
]

var content: Content
var state: GardenState


func _init(c: Content, s: GardenState) -> void:
	content = c
	state = s


## Eksik girdiler: [{asset, gereken, mevcut}]. Boşsa tarif yapılabilir.
func eksikler(tarif_id: String) -> Array:
	var out: Array = []
	for g in content.tarifler[tarif_id]["girdiler"]:
		var mevcut := state.adet(g["asset"])
		if mevcut < int(g["adet"]):
			out.append({"asset": g["asset"], "gereken": int(g["adet"]), "mevcut": mevcut})
	return out


func yapilabilir(tarif_id: String) -> bool:
	return eksikler(tarif_id).is_empty()


## Yapılabilen tarifler (arayüzde "birleştir" önerisi için).
func yapilabilenler() -> Array[String]:
	var out: Array[String] = []
	for id in content.tarifler:
		if yapilabilir(id):
			out.append(id)
	return out


## Tarifi uygular; olay listesi döner (yapılamıyorsa boş).
func yap(tarif_id: String) -> Array:
	if not yapilabilir(tarif_id):
		return []
	var t: Dictionary = content.tarifler[tarif_id]
	for g in t["girdiler"]:
		if g["asset"] in MALZEMELER:
			state.envanter[g["asset"]] = state.adet(g["asset"]) - int(g["adet"])
	var urun: Dictionary = t["urun"]
	if urun.has("asset"):
		state.ekle(urun["asset"], int(urun.get("adet", 1)))
		return [{"tur": "tarif", "tarif": tarif_id, "asset": urun["asset"], "adet": state.adet(urun["asset"])}]
	var etki := "etki:" + str(urun["etki"])
	state.ekle(etki)
	return [{"tur": "tarif", "tarif": tarif_id, "etki": urun["etki"]}]
