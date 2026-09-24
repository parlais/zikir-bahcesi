class_name GardenState
extends RefCounted
## Oyuncunun kalıcı durumu. Yalnızca veri tutar; kuralları ZikirEngine uygular.
##
## Cezasızlık ilkesi (rapor §6d): hiçbir sayaç veya envanter azalmaz, bitki
## ölmez. Kaynaklar zamanla yalnızca bir tabana kadar solar ve zikirle geri döner.

const KAYNAK_TAVAN := 100.0
## Kaynakların inebileceği en düşük değer: bahçe solar ama asla ölmez.
const KAYNAK_TABAN := 20.0

var surum := 1
## Ebced modu açıkken esma eşikleri ebced değeridir; kapalıyken sabit 33.
var ebced_modu := true
## Tetikleyici anahtarı -> ömür boyu toplam sayı.
var sayaclar: Dictionary = {}
## Asset id -> verilmiş tamamlanma sayısı (olgun bitki, açılmış item).
var tamamlanan: Dictionary = {}
## Asset id -> envanterdeki adet (tarifler bunu tüketir).
var envanter: Dictionary = {}
## Kaynak -> değer (hava, su, isik, rizik).
var kaynaklar: Dictionary = {"hava": 60.0, "su": 60.0, "isik": 60.0, "rizik": 60.0}
## Kaynakların en son güncellendiği an (unix saniye).
var kaynak_zamani: float = 0.0
## Art arda sayım için son söylenen anahtar ve kaç kez üst üste söylendiği.
var son_anahtar := ""
var ardisik := 0
## Açılmış öğretici kartlar (esma id).
var kartlar: Array = []
## Rastgele tür seçimleri için tohum; aynı kayıt aynı sonucu verir.
var rng_durumu: int = 20260924
## Seri (streak) durumu; StreakSystem yönetir.
var seri: Dictionary = {"gun": 0, "son_gun": -1, "en_uzun": 0, "dondurma": 1}


func sayac(key: String) -> int:
	return int(sayaclar.get(key, 0))


func adet(asset_id: String) -> int:
	return int(envanter.get(asset_id, 0))


func ekle(asset_id: String, n: int = 1) -> void:
	envanter[asset_id] = adet(asset_id) + n


func to_dict() -> Dictionary:
	return {
		"surum": surum, "ebced_modu": ebced_modu, "sayaclar": sayaclar,
		"tamamlanan": tamamlanan, "envanter": envanter, "kaynaklar": kaynaklar,
		"kaynak_zamani": kaynak_zamani, "son_anahtar": son_anahtar, "ardisik": ardisik,
		"kartlar": kartlar, "rng_durumu": rng_durumu, "seri": seri,
	}


static func from_dict(d: Dictionary) -> GardenState:
	var s := GardenState.new()
	s.ebced_modu = bool(d.get("ebced_modu", true))
	s.sayaclar = _ints(d.get("sayaclar", {}))
	s.tamamlanan = _ints(d.get("tamamlanan", {}))
	s.envanter = _ints(d.get("envanter", {}))
	var k: Dictionary = d.get("kaynaklar", {})
	for name in s.kaynaklar:
		s.kaynaklar[name] = float(k.get(name, s.kaynaklar[name]))
	s.kaynak_zamani = float(d.get("kaynak_zamani", 0.0))
	s.son_anahtar = str(d.get("son_anahtar", ""))
	s.ardisik = int(d.get("ardisik", 0))
	s.kartlar = Array(d.get("kartlar", []))
	s.rng_durumu = int(d.get("rng_durumu", s.rng_durumu))
	var seri: Dictionary = d.get("seri", {})
	for name in s.seri:
		s.seri[name] = int(seri.get(name, s.seri[name]))
	return s


## JSON sayıları float olarak döner; sayaçları tam sayıya çevirir.
static func _ints(d: Dictionary) -> Dictionary:
	var out := {}
	for key in d:
		out[key] = int(d[key])
	return out
