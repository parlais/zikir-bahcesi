class_name IsikKaristirici
extends RefCounted
## K12, K13: Nur (altın) ile Sky/Ori (beyaz-turkuaz, nurani) ışık profillerini bir
## t değeriyle karıştırır: 0 Nur, 1 Ori. Mekân aynıdır; yalnızca ışığın tonu ve
## havası değişir (K5: gece yok, güneş diski yok).
##
##   var p := IsikKaristirici.profil(0.5)          # ilk katın içi
##   var p := IsikKaristirici.profil(0.5, true)    # dıştan kesit
##
## Sayılar lerp, renkler Color.lerp, yönler (Vector3) slerp ile karışır; diziler
## ve sözlükler eleman eleman karışır. Metin ve bool gibi kesikli değerler yarıda
## el değiştirir; bu yüzden iki uçta aynı tutulmalıdır (test eder).
##
## Işığın yönü karışmaz, çapraz geçer (K13): Nur'un ışığı ("gunes") ve gökteki
## parıltısı (nur_yon) yerinde söner, Ori'ninkiler ("gunes_b", nur_yon_b) kendi
## yerinde belirir. Gölgeler dönmez, ışık gökte gezinmez; geçiş güneşin hareketi ya
## da gün dönümü gibi okunmaz. İki uç da profillerin kendisidir: Ori'nin ırmaktaki
## parıltısı ve pusu, Nur'un altın arka ışığı olduğu gibi kalır.
##
## SABIT listesindekiler her t'de Nur'dan alınır:
##   - bulut deseninin ölçeği: bulutlar gökte büyüyüp kaymaz
##   - hacim sisinin uzunluğu: sis hacmi geçiş boyunca yeniden kurulmaz

const UC_NUR := "nur"
const UC_ORI := "sky"
const SABIT := ["gok/bulut_olcek", "ortam/hacim_sis/3"]
## Karıştırılmayan üst düzey alanlar (Nur'dan alınır). "kesit" üst yazımı
## AnimasyonStilleri.al() tarafından zaten uygulanmıştır.
const ATLA := ["ad", "alt", "kesit"]


static func profil(t: float, kesit := false) -> Dictionary:
	return karistir(AnimasyonStilleri.al(UC_NUR, kesit), AnimasyonStilleri.al(UC_ORI, kesit), t)


## İki profili karıştırır. Girdiler değişmez.
static func karistir(a: Dictionary, b: Dictionary, t: float) -> Dictionary:
	t = clampf(t, 0.0, 1.0)
	var p := {}
	for k in a:
		p[k] = a[k] if k in ATLA or not b.has(k) else _karistir(a[k], b[k], t)
	for k in b:
		if not p.has(k):
			p[k] = b[k]
	p = p.duplicate(true)
	for yol in SABIT:
		yaz(p, yol, oku(a, yol))
	# Çapraz geçiş: iki ışık, iki parıltı
	p["gunes"] = (a["gunes"] as Dictionary).duplicate(true)
	p["gunes"]["enerji"] = float(a["gunes"]["enerji"]) * (1.0 - t)
	p["gunes_b"] = (b["gunes"] as Dictionary).duplicate(true)
	p["gunes_b"]["enerji"] = float(b["gunes"]["enerji"]) * t
	p["gok"]["nur_yon"] = a["gok"]["nur_yon"]
	p["gok"]["nur_yon_b"] = b["gok"]["nur_yon"]
	p["gok"]["nur_karisim"] = t
	# Kesitte katların göğü (içerideki gök): aynı çapraz geçiş
	if a.has("kat_gok") and b.has("kat_gok"):
		p["kat_gok"]["nur_yon"] = a["kat_gok"]["nur_yon"]
		p["kat_gok"]["nur_yon_b"] = b["kat_gok"]["nur_yon"]
		p["kat_gok"]["nur_karisim"] = t
	return p


static func _karistir(x: Variant, y: Variant, t: float) -> Variant:
	var tx := typeof(x)
	var ty := typeof(y)
	if tx != ty:
		if (tx == TYPE_INT or tx == TYPE_FLOAT) and (ty == TYPE_INT or ty == TYPE_FLOAT):
			return lerpf(float(x), float(y), t)
		return x if t < 0.5 else y
	match tx:
		TYPE_FLOAT:
			return lerpf(x, y, t)
		TYPE_INT:
			return roundi(lerpf(float(x), float(y), t))
		TYPE_COLOR:
			return (x as Color).lerp(y, t)
		TYPE_VECTOR2:
			return (x as Vector2).lerp(y, t)
		TYPE_VECTOR3:
			return (x as Vector3).slerp(y, t)
		TYPE_ARRAY:
			var xa: Array = x
			var ya: Array = y
			if xa.size() != ya.size():
				return x if t < 0.5 else y
			var out: Array = []
			for i in xa.size():
				out.append(_karistir(xa[i], ya[i], t))
			return out
		TYPE_DICTIONARY:
			var xd: Dictionary = x
			var yd: Dictionary = y
			var out := {}
			for k in xd:
				out[k] = _karistir(xd[k], yd[k], t) if yd.has(k) else xd[k]
			for k in yd:
				if not out.has(k):
					out[k] = yd[k]
			return out
	return x if t < 0.5 else y


## İki profilin karışmaya uymayan yerleri: yalnız bir uçta olan anahtarlar ve
## iki uçta farklı olan kesikli değerler (metin, bool, farklı uzunlukta dizi).
## Boş dönmelidir; yoksa geçişte sıçrama ya da uçlarda istenmeyen değer olur.
static func uyumsuzluklar(a: Dictionary, b: Dictionary) -> Array[String]:
	var out: Array[String] = []
	for k in a:
		if not k in ATLA:
			_uyumsuz(a[k], b.get(k), str(k), out, b.has(k))
	for k in b:
		if not k in ATLA and not a.has(k):
			out.append("%s: yalnız Ori'de" % k)
	return out


static func _uyumsuz(x: Variant, y: Variant, yol: String, out: Array[String], var_mi := true) -> void:
	if not var_mi:
		out.append("%s: yalnız Nur'da" % yol)
		return
	var sayi := [TYPE_INT, TYPE_FLOAT]
	if typeof(x) != typeof(y) and not (typeof(x) in sayi and typeof(y) in sayi):
		out.append("%s: tür farklı" % yol)
		return
	match typeof(x):
		TYPE_DICTIONARY:
			for k in x:
				_uyumsuz(x[k], y.get(k), "%s/%s" % [yol, k], out, (y as Dictionary).has(k))
			for k in y:
				if not (x as Dictionary).has(k):
					out.append("%s/%s: yalnız Ori'de" % [yol, k])
		TYPE_ARRAY:
			if (x as Array).size() != (y as Array).size():
				out.append("%s: dizi uzunluğu farklı" % yol)
			else:
				for i in (x as Array).size():
					_uyumsuz(x[i], y[i], "%s/%d" % [yol, i], out)
		TYPE_STRING, TYPE_STRING_NAME, TYPE_BOOL:
			if x != y:
				out.append("%s: kesikli değer farklı (%s / %s)" % [yol, x, y])


## "gunes/yon" gibi bir yolu okur (dizi indisleri sayı olarak yazılır: "ortam/sis/0").
static func oku(p: Dictionary, yol: String) -> Variant:
	var d: Variant = p
	for s in yol.split("/"):
		d = d[int(s)] if d is Array else d[s]
	return d


static func yaz(p: Dictionary, yol: String, deger: Variant) -> void:
	var parca := yol.split("/")
	var d: Variant = p
	for i in parca.size() - 1:
		d = d[int(parca[i])] if d is Array else d[parca[i]]
	var son := parca[parca.size() - 1]
	if d is Array:
		d[int(son)] = deger
	else:
		d[son] = deger
