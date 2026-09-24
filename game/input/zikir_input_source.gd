class_name ZikirInputSource
extends Node
## Zikir girişi kaynağı. Dokunmatik tesbih ve (sonraki fazda) mikrofon aynı
## sinyali yayar; Game hangisinden geldiğine bakmadan sayar.

## key: tetikleyici anahtarı ("tevhid", "esma:nur"...).
## bas/son: sözün başladığı ve bittiği an, saniye (Time.get_ticks_msec tabanlı).
signal soz_algilandi(key: String, bas: float, son: float)

## true ise algılama kesindir ve PhraseResolver beklemesine girmez.
## Dokunmatik girişte kullanıcı sözü açıkça seçtiği için kesindir; ses
## tanımada önek sözler (Sübhanallah -> Sübhanallahi ve bihamdihi) beklenir.
var kesin := false


static func simdi() -> float:
	return Time.get_ticks_msec() / 1000.0
