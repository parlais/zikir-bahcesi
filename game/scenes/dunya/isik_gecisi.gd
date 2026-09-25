class_name IsikGecisi
extends RefCounted
## K13: Işığın ne zaman Nur'dan Ori'ye geçeceğini tutar.
##
## Zemin Nur'dur (t = 0). Bir zikir, dua, sure ya da esma tamamlanınca ya da
## özel bir olayda ışık yavaşça Ori'ye çıkar (t = 1), bir süre kalır, sonra
## daha da yavaş Nur'a döner. Yeni bir tetik kalışı uzatır; zikir sürdükçe ışık
## Ori'de kalır. Gerçek saate ya da akan zamana bağlı değildir (K5).
##
##   var g := IsikGecisi.new()
##   Game.olay.connect(g.olay)       # ZikirEngine olayları
##   g.tetikle("kat_gecisi")         # sahne olayları
##   g.ilerle(delta)                 # her karede; g.t karıştırıcıya gider

## Nur -> Ori süresi (sn).
const GIRIS := 6.0
## Ori -> Nur süresi (sn): fark ettirmeden süzülür.
const DONUS := 40.0
## Tetik -> Ori'de kalma süresi (sn, çıkış dahil). Sonra dönüş başlar.
const KALIS := {
	"tamamlandi": 40.0,  # bir zikir, dua ya da sure tamamlandı (item açıldı, bitki olgunlaştı)
	"esma_tamam": 60.0,  # esmanın hedef sayısı tamamlandı
	"tuba_asama": 90.0,  # Tûbâ yeni aşamaya geçti
	"kat_gecisi": 30.0,  # merdivenle ya da açılışta kata iniş
	"ziyaret": 30.0,  # arkadaş bahçesine varış
	"acilis": 20.0,  # oyunun açılışı
}

## Karıştırıcıya giden değer: 0 Nur, 1 Ori (yumuşatılmış).
var t := 0.0
## Doğrusal ilerleme (0..1); t bunun yumuşatılmışıdır.
var faz := 0.0
var _kalis := 0.0
var _sabit := -1.0


## ZikirEngine olayı (bkz. zikir_engine.gd başı). Tarif, kaynak ve seri olayları
## ışığı değiştirmez.
func olay(o: Dictionary) -> void:
	match o.get("tur", ""):
		"tamamlandi", "esma_tamam":
			tetikle(o["tur"])
		"asama":
			if o.get("asset", "") == "tuba":
				tetikle("tuba_asama")


func tetikle(ad: String) -> void:
	_kalis = maxf(_kalis, float(KALIS.get(ad, KALIS["tamamlandi"])))


## Geliştirici: t'yi sabitler (çekimler için). Eksi değer serbest bırakır.
func zorla(deger: float) -> void:
	_sabit = deger
	if deger >= 0.0:
		faz = clampf(deger, 0.0, 1.0)
		t = faz


func ori_de_mi() -> bool:
	return _kalis > 0.0


func ilerle(dt: float) -> void:
	if _sabit >= 0.0:
		return
	if _kalis > 0.0:
		_kalis = maxf(0.0, _kalis - dt)
		faz = minf(1.0, faz + dt / GIRIS)
	else:
		faz = maxf(0.0, faz - dt / DONUS)
	t = faz * faz * (3.0 - 2.0 * faz)
