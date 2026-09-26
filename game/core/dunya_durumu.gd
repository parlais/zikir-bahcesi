class_name DunyaDurumu
extends RefCounted
## Dünyanın hâli (K20): oyuncunun kaydından dünyada neyin açık olduğunu hesaplar.
##
## Oyun boş başlar; ağaç, ırmak, çiçek, canlı ve nimet oynadıkça açılır. Dünya ikiye ayrılır:
##   çerçeve  hep vardır: ışık, gök, bulut, nur zerreleri, ova ve tepeler, arsanın kadife
##            çimeni, süzülen Tûbâ çekirdeği. Hâlde yer almaz; sahne her zaman kurar.
##   nimet    zikirle gelir; bu sınıfın hesapladığı her şey.
##
## Hâl (Dictionary):
##   vitrin    bool   true: vitrin kipi; sahne mevcut yerleşim listelerini kurar
##   tuba      int    0-5 (0: süzülen çekirdek, 1: ilk tevhid ... 5: ulu, 10000 tevhid)
##   kapi      bool   bahçe kapısı (ilk Bismillah; oturum açılışı)
##   cakil     bool   inci ve yakut çakıl sınırı (kapıyla birlikte gelir)
##   yuva      {asset_id: [model adı, ...]}  dolu yuvalar, yuva sırasıyla (DunyaYuvalari).
##             Olgun kopyalar = min(adet, yuva sayısı) son aşama modeli; ardından büyüyen
##             örnek o anki aşamasının modeliyle. Boş asset yer almaz.
##   yansima   {cevre, ova, ufuk, cicek, cimen}: 0-1
##             cevre, ova  "on misli yankı" (En'âm 160): olgunlaşan her ağaç ovada 10 ağaç
##                         açar. n = 10 x olgun ağaç (Tûbâ hariç); önce çevre koruları
##                         (286), sonra ova (1496 uzak ağaç). Sahne listenin bu oranını açar.
##             ufuk        Tûbâ olgunlaşınca (aşama 4, 1000 tevhid): uzak korular ve ufuk
##             cicek       kır çiçekleri: 0 yok; 1/3 arsa çevresi (3 olgun çiçek); 12 olgun
##                         çiçeğe doğru 2/3'e (ova) büyür; 1 bütün ova (Bahar patlaması, Bâis)
##             cimen       0 seyrek, 1 gür (Çimen halısı, Bâsıt 72)
##   irmak     [su, sut, bal, serbet]: 0/1. Irmak asset'i (IRMAKLAR) tamamlandıysa ya da
##             envanterdeyse açıktır (bir kez verilir).
##   selale    ırmakla aynı (gökten inen çağlayan ırmağıyla gelir)
##   merdiven  bool   kat merdiveni; kat değiştirme mekaniğiyle gelecek (şimdilik false)
##   canli     {asset_id: adet}  Rig asset'leri
##   etki      [String]  envanterdeki "etki:" anahtarları (tarif etkileri), sıralı
##
## Hesap yalnız hiç azalmayan değerlerden yapılır: sayaçlar, tamamlanan ve kazanilan.
## Tarifte harcanan malzeme dünyadan düşmez (cezasızlık, rapor §6d). Ebced modu
## değişince büyüyen bir örneğin aşaması düşebilir; hesapla() sonucu oyuncunun gördüğü
## son hâlle (GardenState.dunya_gorulen) birleştirir, hiçbir değer geri gitmez.
## Kullanım: hal = hesapla(...); sahne fark(state.dunya_gorulen, hal) ile yeni gelenleri
## canlandırır, sonra goruldu(state, hal).

## En'âm 160: olgunlaşan her ağaç ovada bu kadar ağaç açar.
const ON_MISLI := 10
## Çevre koruları (13-300 m) ve ova (300-700 m, uzak ağaç) örnek sayıları.
const KORU_SAYISI := 286
const UZAK_AGAC_SAYISI := 1496
## Tûbâ bu aşamaya gelince (1000 tevhid) uzak korular ve ufuk açılır.
const UFUK_TUBA_ASAMASI := 4
const TUBA_SON_ASAMA := 5
## Kır çiçekleri: bu kadar olgun çiçekte arsa çevresi, sonra ova.
const KIR_CICEGI_ARSA := 3
const KIR_CICEGI_OVA := 12
const CICEK_ARSA_ORANI := 1.0 / 3.0
const CICEK_OVA_ORANI := 2.0 / 3.0

const TUBA := "tuba"
const KAPI := "bahce_kapisi"
const CIMEN := "cimen_halisi"
const BAHAR := "bahar_patlamasi"
## Dört ırmak (Muhammed 15), hâldeki sırasıyla: su, süt, bal, şerbet.
const IRMAKLAR := ["irmak_su", "irmak_sut", "irmak_bal", "irmak_serbet"]
const YANSIMALAR := ["cevre", "ova", "ufuk", "cicek", "cimen"]
## Ağaç ve çiçek asset'leri model adlarından tanınır.
const AGAC_ONEKI := "ZB_agac_"
const CICEK_ONEKI := "ZB_cicek_"
const _TEKLER := ["vitrin", "tuba", "kapi", "cakil", "merdiven"]
const _DIZILER := ["irmak", "selale"]


## Hiç zikir söylenmemiş dünya: Tûbâ süzülen çekirdek, bütün nimetler kapalı.
static func bos() -> Dictionary:
	var yansima := {}
	for k in YANSIMALAR:
		yansima[k] = 0.0
	return {
		"vitrin": false, "tuba": 0, "kapi": false, "cakil": false, "yuva": {}, "yansima": yansima,
		"irmak": [0, 0, 0, 0], "selale": [0, 0, 0, 0], "merdiven": false, "canli": {}, "etki": [],
	}


## Vitrin: her şey açık. Sahne vitrin kipinde mevcut yerleşim listelerini kurar.
## content ve yuvalar verilirse bütün yuvalar olgun modelle, canlılar ve etkiler de dolar.
static func vitrin(content: Content = null, yuvalar: DunyaYuvalari = null) -> Dictionary:
	var h := bos()
	h["vitrin"] = true
	h["tuba"] = TUBA_SON_ASAMA
	h["kapi"] = true
	h["cakil"] = true
	h["merdiven"] = true
	for k in YANSIMALAR:
		h["yansima"][k] = 1.0
	h["irmak"] = [1, 1, 1, 1]
	h["selale"] = [1, 1, 1, 1]
	if content == null:
		return h
	for id in content.assets:
		var a: Dictionary = content.assets[id]
		if a["tip"] == "Rig" and not a["modeller"].is_empty():
			h["canli"][id] = 1
	for t in content.tarifler.values():
		if t["urun"].has("etki"):
			h["etki"].append("etki:" + str(t["urun"]["etki"]))
	h["etki"].sort()
	if yuvalar != null:
		for id in yuvalar.assetler():
			if not content.assets.has(id) or content.assets[id]["modeller"].is_empty():
				continue
			var a: Dictionary = content.assets[id]
			var liste: Array = []
			for i in yuvalar.sayi(id):
				liste.append(model_adi(a, i, int(a["asama_sayisi"])))
			h["yuva"][id] = liste
	return h


## Oyuncunun durumundan dünyanın hâli; gördüğü son hâlin (state.dunya_gorulen) altına inmez.
static func hesapla(content: Content, state: GardenState, engine: ZikirEngine, yuvalar: DunyaYuvalari = null) -> Dictionary:
	var h := ham(content, state, engine, yuvalar)
	var gorulen: Dictionary = state.dunya_gorulen
	if not gorulen.is_empty() and not bool(gorulen.get("vitrin", false)):
		h = en_yuksek(content, gorulen, h, yuvalar)
	return h


## Yalnız durumdan hesaplanan hâl (görülenle birleştirilmemiş).
static func ham(content: Content, state: GardenState, engine: ZikirEngine, yuvalar: DunyaYuvalari = null) -> Dictionary:
	var h := bos()
	if content.assets.has(TUBA):
		h["tuba"] = clampi(int(engine.ilerleme(TUBA)["asama"]), 0, TUBA_SON_ASAMA)
	var kapi := adet(state, KAPI) >= 1
	h["kapi"] = kapi
	h["cakil"] = kapi
	if yuvalar != null:
		h["yuva"] = _yuvalar(content, state, engine, yuvalar)
	h["yansima"] = _yansima(content, state, h["tuba"])
	for i in IRMAKLAR.size():
		h["irmak"][i] = 1 if adet(state, IRMAKLAR[i]) >= 1 else 0
	h["selale"] = h["irmak"].duplicate()
	h["merdiven"] = false
	for id in content.assets:
		if content.assets[id]["tip"] == "Rig":
			var n := adet(state, id)
			if n > 0:
				h["canli"][id] = n
	var etki: Array = []
	for key in state.kazanilan.keys() + state.envanter.keys():
		if str(key).begins_with("etki:") and adet(state, key) >= 1 and not etki.has(key):
			etki.append(key)
	etki.sort()
	h["etki"] = etki
	return h


## Bir asset'in hiç azalmayan adedi: tamamlanma, ömür boyu kazanılan ve envanter sayısının
## en büyüğü. Tarifte harcanan malzeme envanterden düşer; kazanılan düşmez.
static func adet(state: GardenState, id: String) -> int:
	return maxi(maxi(int(state.tamamlanan.get(id, 0)), int(state.kazanilan.get(id, 0))), state.adet(id))


## Bir yuvanın modeli: yuva_no'ncu yuva, verilen aşama (1..aşama sayısı). Aşama sayısından
## çok model varsa (sur parçaları: düz, köşe; süs çiçekleri) yuvalar varyantları sırayla alır.
static func model_adi(a: Dictionary, yuva_no: int, asama: int) -> String:
	var modeller: Array = a["modeller"]
	var asama_sayisi := maxi(1, int(a["asama_sayisi"]))
	var varyant := maxi(1, modeller.size() / asama_sayisi)
	var i := (yuva_no % varyant) * asama_sayisi + clampi(asama, 1, asama_sayisi) - 1
	return modeller[mini(i, modeller.size() - 1)]


## Modelin aşaması (1..); model bu asset'in değilse ya da boşsa 0.
static func asama_no(a: Dictionary, model: String) -> int:
	if model == "":
		return 0
	var i: int = a["modeller"].find(model)
	if i < 0:
		return 0
	return i % maxi(1, int(a["asama_sayisi"])) + 1


## Kır çiçeklerinin oranı (bkz. sınıf başı).
static func kir_cicegi(olgun_cicek: int, bahar: bool) -> float:
	if bahar:
		return 1.0
	if olgun_cicek < KIR_CICEGI_ARSA:
		return 0.0
	if olgun_cicek >= KIR_CICEGI_OVA:
		return CICEK_OVA_ORANI
	var t := float(olgun_cicek - KIR_CICEGI_ARSA) / float(KIR_CICEGI_OVA - KIR_CICEGI_ARSA)
	return lerpf(CICEK_ARSA_ORANI, CICEK_OVA_ORANI, t)


## İki hâlin birleşimi: her değerin büyüğü (yuvalarda aşaması büyük olan model).
## yuvalar verilirse artık olmayan yuvalar atılır.
static func en_yuksek(content: Content, eski: Dictionary, yeni: Dictionary, yuvalar: DunyaYuvalari = null) -> Dictionary:
	var e := duzelt(eski)
	var h := duzelt(yeni)
	h["tuba"] = maxi(h["tuba"], e["tuba"])
	for k in ["kapi", "cakil", "merdiven"]:
		h[k] = h[k] or e[k]
	for k in _DIZILER:
		for i in IRMAKLAR.size():
			h[k][i] = maxi(h[k][i], e[k][i])
	for k in e["yansima"]:
		h["yansima"][k] = maxf(float(h["yansima"].get(k, 0.0)), e["yansima"][k])
	for id in e["canli"]:
		h["canli"][id] = maxi(int(h["canli"].get(id, 0)), e["canli"][id])
	for key in e["etki"]:
		if not h["etki"].has(key):
			h["etki"].append(key)
	h["etki"].sort()
	for id in e["yuva"]:
		if not content.assets.has(id):
			continue
		var a: Dictionary = content.assets[id]
		var ey: Array = e["yuva"][id]
		var hy: Array = h["yuva"].get(id, [])
		var n := maxi(ey.size(), hy.size())
		if yuvalar != null:
			n = mini(n, yuvalar.sayi(id))
		var liste: Array = []
		for i in n:
			var m1: String = ey[i] if i < ey.size() else ""
			var m2: String = hy[i] if i < hy.size() else ""
			liste.append(m1 if asama_no(a, m1) > asama_no(a, m2) else m2)
		while not liste.is_empty() and liste[-1] == "":
			liste.pop_back()
		if liste.is_empty():
			h["yuva"].erase(id)
		else:
			h["yuva"][id] = liste
	return h


## Değişenler, sabit sırayla: [{tur, id, eski, yeni}]. tur: "vitrin", "tuba", "kapi",
## "cakil", "merdiven" (id alanın adı), "irmak", "selale" (id ırmak asset'i), "yansima"
## (id: cevre, ova...), "yuva" (id asset, ayrıca yuva_no; boş yuva ""), "canli", "etki"
## (eski, yeni: var mı).
static func fark(eski: Dictionary, yeni: Dictionary) -> Array:
	var e := duzelt(eski)
	var h := duzelt(yeni)
	var out: Array = []
	for k in _TEKLER:
		if e[k] != h[k]:
			out.append({"tur": k, "id": k, "eski": e[k], "yeni": h[k]})
	for k in _DIZILER:
		for i in IRMAKLAR.size():
			if e[k][i] != h[k][i]:
				out.append({"tur": k, "id": IRMAKLAR[i], "eski": e[k][i], "yeni": h[k][i]})
	for k in _anahtarlar(e["yansima"], h["yansima"]):
		var v1: float = e["yansima"].get(k, 0.0)
		var v2: float = h["yansima"].get(k, 0.0)
		if not is_equal_approx(v1, v2):
			out.append({"tur": "yansima", "id": k, "eski": v1, "yeni": v2})
	for id in _anahtarlar(e["yuva"], h["yuva"]):
		var a: Array = e["yuva"].get(id, [])
		var b: Array = h["yuva"].get(id, [])
		for i in maxi(a.size(), b.size()):
			var m1: String = a[i] if i < a.size() else ""
			var m2: String = b[i] if i < b.size() else ""
			if m1 != m2:
				out.append({"tur": "yuva", "id": id, "yuva_no": i, "eski": m1, "yeni": m2})
	for id in _anahtarlar(e["canli"], h["canli"]):
		var n1: int = e["canli"].get(id, 0)
		var n2: int = h["canli"].get(id, 0)
		if n1 != n2:
			out.append({"tur": "canli", "id": id, "eski": n1, "yeni": n2})
	var etkiler: Array = e["etki"].duplicate()
	for key in h["etki"]:
		if not etkiler.has(key):
			etkiler.append(key)
	etkiler.sort()
	for key in etkiler:
		var v1: bool = e["etki"].has(key)
		var v2: bool = h["etki"].has(key)
		if v1 != v2:
			out.append({"tur": "etki", "id": key, "eski": v1, "yeni": v2})
	return out


## Sahne hâli gösterince çağırır: oyuncunun gördüğü son hâl olarak kaydeder (vitrin hariç).
static func goruldu(state: GardenState, hal: Dictionary) -> void:
	if not bool(hal.get("vitrin", false)):
		state.dunya_gorulen = duzelt(hal)


## Şemaya uyan bağımsız bir kopya: eksik alanlar boş hâlden, türler düzeltilir
## (JSON'dan okunan kayıtta sayılar float döner).
static func duzelt(d: Dictionary) -> Dictionary:
	var h := bos()
	h["vitrin"] = bool(d.get("vitrin", false))
	h["tuba"] = int(d.get("tuba", 0))
	for k in ["kapi", "cakil", "merdiven"]:
		h[k] = bool(d.get(k, false))
	var yuva = d.get("yuva", {})
	if yuva is Dictionary:
		for id in yuva:
			if yuva[id] is Array and not yuva[id].is_empty():
				var liste: Array = []
				for m in yuva[id]:
					liste.append(str(m))
				h["yuva"][str(id)] = liste
	var yansima = d.get("yansima", {})
	if yansima is Dictionary:
		for k in yansima:
			h["yansima"][str(k)] = float(yansima[k])
	for k in _DIZILER:
		var v = d.get(k, [])
		if v is Array:
			for i in mini(v.size(), IRMAKLAR.size()):
				h[k][i] = int(v[i])
	var canli = d.get("canli", {})
	if canli is Dictionary:
		for id in canli:
			h["canli"][str(id)] = int(canli[id])
	var etki = d.get("etki", [])
	if etki is Array:
		for key in etki:
			if not h["etki"].has(str(key)):
				h["etki"].append(str(key))
		h["etki"].sort()
	return h


static func _yuvalar(content: Content, state: GardenState, engine: ZikirEngine, yuvalar: DunyaYuvalari) -> Dictionary:
	var out := {}
	for id in yuvalar.assetler():
		if not content.assets.has(id):
			continue
		var a: Dictionary = content.assets[id]
		if a["modeller"].is_empty():
			continue
		var n := yuvalar.sayi(id)
		var asama_sayisi := maxi(1, int(a["asama_sayisi"]))
		var olgun := mini(adet(state, id), n)
		var liste: Array = []
		for i in olgun:
			liste.append(model_adi(a, i, asama_sayisi))
		var kural = a["tetikleyici"]["kural"]
		# "toplam" kuralı (Tûbâ) bir kez olgunlaşır; ardından yeni örnek büyümez.
		var buyuyen: bool = kural == "birikimli" or (kural == "toplam" and olgun == 0)
		if olgun < n and asama_sayisi > 1 and buyuyen:
			var asama := int(engine.ilerleme(id)["asama"])
			if asama > 0:
				liste.append(model_adi(a, olgun, asama))
		if not liste.is_empty():
			out[id] = liste
	return out


static func _yansima(content: Content, state: GardenState, tuba: int) -> Dictionary:
	var agac := 0
	var cicek := 0
	for id in content.assets:
		var a: Dictionary = content.assets[id]
		if a["kategori"] != "bitki" or a["modeller"].is_empty() or id == TUBA:
			continue
		var m: String = a["modeller"][0]
		if m.begins_with(AGAC_ONEKI):
			agac += adet(state, id)
		elif m.begins_with(CICEK_ONEKI):
			cicek += adet(state, id)
	var n := ON_MISLI * agac
	return {
		"cevre": minf(float(n) / KORU_SAYISI, 1.0),
		"ova": clampf(float(n - KORU_SAYISI) / UZAK_AGAC_SAYISI, 0.0, 1.0),
		"ufuk": 1.0 if tuba >= UFUK_TUBA_ASAMASI else 0.0,
		"cicek": kir_cicegi(cicek, adet(state, BAHAR) >= 1),
		"cimen": 1.0 if adet(state, CIMEN) >= 1 else 0.0,
	}


static func _anahtarlar(a: Dictionary, b: Dictionary) -> Array:
	var out: Array = a.keys()
	for k in b:
		if not out.has(k):
			out.append(k)
	out.sort()
	return out
