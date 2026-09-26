class_name ZikirEngine
extends RefCounted
## Oyun kuralları: bir söz sayıldığında hangi bitkinin büyüyeceğine, hangi
## item'ın açılacağına ve kaynakların nasıl değişeceğine karar verir.
##
## Olaylar sözlük olarak döner; arayüz bunlara göre efekt ve kart gösterir:
##   {tur="asama", asset, asama}          büyüyen örnek yeni aşamaya geçti (yalnız aşamalı asset'ler)
##   {tur="tamamlandi", asset, adet}      item açıldı / bitki olgunlaştı. Aynı sayıda birden
##                                        çok asset gelirse sıra Content.by_key sırasıdır:
##                                        100. istiğfarda önce nisan yağmuru, sonra su ırmağı.
##   {tur="ardisik", asset}               N kez art arda söylendi (örn. gül kokusu)
##   {tur="esma_tamam", esma, kez}        esmanın hedef sayısı tamamlandı
##   {tur="kart", esma}                   öğretici kart açıldı
##   {tur="kaynak", kaynak, deger}        kaynak değişti

const KAYNAK_KAZANCI := {
	"tevhid": {"hava": 1.0},
	"elhamdulillah": {"su": 1.0},
	"istigfar": {"su": 1.0},
	"esma:nur": {"isik": 1.0},
	"esma:rezzak": {"rizik": 1.0},
}
## Saatte solma miktarı; taban değerin altına inmez.
const SOLMA_SAATLIK := 1.0

var content: Content
var state: GardenState


func _init(c: Content, s: GardenState) -> void:
	content = c
	state = s


## Bir sözü n kez sayar. baglam koşullu anahtarları açar:
##   {"cuma": true} -> "salavat@cuma" de sayılır
##   {"oturum_acilisi": true} -> "bismillah@oturum_acilisi" de sayılır
func say(anahtar: String, n: int = 1, baglam: Dictionary = {}) -> Array:
	var olaylar: Array = []
	var anahtarlar: Array[String] = [anahtar]
	for kosul in baglam:
		if baglam[kosul]:
			anahtarlar.append(anahtar + "@" + str(kosul))
	for i in n:
		for key in anahtarlar:
			_say_bir(key, olaylar)
		_ardisik(anahtar, olaylar)
	return olaylar


func _say_bir(key: String, olaylar: Array) -> void:
	var etkilenen: Array = content.by_key.get(key, [])
	var once := {}
	for id in etkilenen:
		once[id] = ilerleme(id)
	state.sayaclar[key] = state.sayac(key) + 1
	var c := state.sayac(key)

	for id in etkilenen:
		var sonra := ilerleme(id)
		# Tek aşamalı asset'in (ırmak) aşama adı yoktur; yalnız "tamamlandi" olayı gelir.
		var asamali: bool = int(content.assets[id]["asama_sayisi"]) > 1
		if asamali and sonra["asama"] > once[id]["asama"]:
			olaylar.append({"tur": "asama", "asset": id, "asama": sonra["asama"]})
		_ver(id, sonra["tamam"], olaylar)

	for id in content.her_n_by_key.get(key, []).slice(0, 1):
		var n: int = content.assets[id]["tetikleyici"]["adet"]
		if c % n == 0:
			var secenekler: Array = content.her_n_by_key[key]
			_kazan(secenekler[_rastgele(secenekler.size())], olaylar)

	# Sürekli kaynaklar (tevhid -> sabâ yeli) envantere girmez; kaynak olarak görünür.
	if KAYNAK_KAZANCI.has(key):
		for k in KAYNAK_KAZANCI[key]:
			var v: float = minf(GardenState.KAYNAK_TAVAN, state.kaynaklar[k] + KAYNAK_KAZANCI[key][k])
			if v != state.kaynaklar[k]:
				state.kaynaklar[k] = v
				olaylar.append({"tur": "kaynak", "kaynak": k, "deger": v})

	if key.begins_with("esma:") and not key.contains("@"):
		var esma_id := key.trim_prefix("esma:")
		var hedef := content.esma_hedefi(esma_id, state.ebced_modu)
		if c % hedef == 0:
			olaylar.append({"tur": "esma_tamam", "esma": esma_id, "kez": c / hedef})
			if content.kart_by_key.has(key) and not state.kartlar.has(esma_id):
				state.kartlar.append(esma_id)
				olaylar.append({"tur": "kart", "esma": esma_id})


func _ardisik(anahtar: String, olaylar: Array) -> void:
	if state.son_anahtar == anahtar:
		state.ardisik += 1
	else:
		state.son_anahtar = anahtar
		state.ardisik = 1
	for id in content.ardisik_by_key.get(anahtar, []):
		var n: int = content.assets[id]["tetikleyici"]["adet"]
		if state.ardisik % n == 0:
			state.ekle(id)
			olaylar.append({"tur": "ardisik", "asset": id})


## Hesaplanan tamamlanma sayısı verilenden fazlaysa farkı verir.
## Hiçbir zaman geri almaz (ebced modu değişse bile).
func _ver(id: String, tamam: int, olaylar: Array) -> void:
	var verilen := int(state.tamamlanan.get(id, 0))
	if tamam <= verilen:
		return
	state.tamamlanan[id] = tamam
	for i in tamam - verilen:
		_kazan(id, olaylar)


## Envantere bir item ekler ve ondan türeyenleri (define sandığı -> inci
## veya mercan, ipek kozası -> kelebek) verir.
func _kazan(id: String, olaylar: Array) -> void:
	state.ekle(id)
	olaylar.append({"tur": "tamamlandi", "asset": id, "adet": state.adet(id)})
	var turevler: Array = content.turev_by_key.get("item:" + id, [])
	if turevler.is_empty():
		return
	# Tek türev her seferinde gelir; birden çok türev varsa biri rastgele seçilir.
	var secilen: String = turevler[0] if turevler.size() == 1 else turevler[_rastgele(turevler.size())]
	_kazan(secilen, olaylar)


## Bir asset'in durumu:
##   tamam     kaç kez tamamlandığı (olgun bitki / açılan item sayısı)
##   asama     şu an büyüyen örneğin aşaması (0: henüz tohum yok)
##   sayi      büyüyen örneğin mevcut sayısı
##   sonraki   bir sonraki aşamanın eşiği (yoksa son eşik)
func ilerleme(id: String) -> Dictionary:
	var a: Dictionary = content.assets[id]
	var t: Dictionary = a["tetikleyici"]
	var esikler: Array = content.esikler(id, state.ebced_modu)
	var son: int = esikler[-1]
	var c := 0
	var keys := Content.trigger_keys(t)
	for key in keys:
		c += state.sayac(key)

	var tamam := 0
	var p := 0
	if t["kural"] == "toplam":
		# Ömür boyu toplamla ilerler; son eşikte bir kez verilir, tekrar etmez.
		# Tûbâ beş aşamayla büyür; dört ırmak tek eşiklidir (100, 300, 700, 1000 istiğfar).
		tamam = 1 if c >= son else 0
		p = c
	else:
		var sira_sayisi := content.sira_sayisi(keys[0]) if not keys.is_empty() else 1
		var offset := (content.sira(id) - 1) * son
		var dongu := son * sira_sayisi
		if c >= offset:
			var d := c - offset
			tamam = 0 if d < son else (d - son) / dongu + 1
			p = d % dongu
			if p >= son:
				p = 0  # Bu tur, aynı tetikleyiciyi paylaşan diğer item'ın sırası.

	var asama := 0
	for e in esikler:
		if p >= int(e):
			asama += 1
	if t["kural"] == "toplam":
		asama = mini(asama, esikler.size())
	var sonraki: int = son
	for e in esikler:
		if p < int(e):
			sonraki = int(e)
			break
	return {"tamam": tamam, "asama": asama, "sayi": p, "sonraki": sonraki}


## Zaman geçtikçe kaynakları tabana doğru soldurur. Ölüm yok, yalnız solma.
func zaman_gecir(simdi: float) -> void:
	if state.kaynak_zamani <= 0.0:
		state.kaynak_zamani = simdi
		return
	var saat := maxf(0.0, simdi - state.kaynak_zamani) / 3600.0
	state.kaynak_zamani = simdi
	for k in state.kaynaklar:
		var v: float = state.kaynaklar[k]
		if v > GardenState.KAYNAK_TABAN:
			state.kaynaklar[k] = maxf(GardenState.KAYNAK_TABAN, v - SOLMA_SAATLIK * saat)


## 0 (solgun) ile 1 (canlı) arası; görsel doygunluk için.
func canlilik(kaynak: String = "hava") -> float:
	var v: float = state.kaynaklar[kaynak]
	return clampf((v - GardenState.KAYNAK_TABAN) / (GardenState.KAYNAK_TAVAN - GardenState.KAYNAK_TABAN), 0.0, 1.0)


## Kayda yazılabilen basit doğrusal eşlik üreteci (31 bit).
func _rastgele(n: int) -> int:
	state.rng_durumu = (state.rng_durumu * 1103515245 + 12345) % 2147483648
	return (state.rng_durumu >> 16) % n
