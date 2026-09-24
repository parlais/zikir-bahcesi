class_name StreakSystem
extends RefCounted
## Günlük vird serisi. Finch modeli: kaçırılan gün seri dondurmayla telafi
## edilir; dondurma yetmezse seri sessizce yeniden başlar, en uzun seri
## kaybolmaz ve hiçbir ceza verilmez (rapor §6d).

const DONDURMA_TAVAN := 3
## Her bu kadar günde bir dondurma hakkı kazanılır.
const DONDURMA_ARALIGI := 7


## Bugünün gün numarası (1970'ten beri gün, yerel tarih).
static func bugun() -> int:
	var d := Time.get_date_dict_from_system()
	return int(Time.get_unix_time_from_datetime_dict({"year": d["year"], "month": d["month"], "day": d["day"]})) / 86400


## Bugün zikir yapıldığını kaydeder. Olay sözlüğü döner:
##   {tur="yok"}                      bugün zaten sayılmış
##   {tur="devam", gun}               seri sürdü
##   {tur="dondurma", gun, kullanilan} kaçan gün(ler) dondurmayla kapandı
##   {tur="yeniden", gun}             seri yeniden başladı (cezasız)
static func kaydet(seri: Dictionary, gun: int) -> Dictionary:
	var son: int = seri["son_gun"]
	var olay: Dictionary
	if son == gun:
		return {"tur": "yok"}
	if son < 0 or gun == son + 1:
		seri["gun"] += 1
		olay = {"tur": "devam"}
	elif gun < son:
		return {"tur": "yok"}  # Saat geri alınmış; hiçbir şeyi bozma.
	else:
		var kacan := gun - son - 1
		if seri["dondurma"] >= kacan:
			seri["dondurma"] -= kacan
			seri["gun"] += 1
			olay = {"tur": "dondurma", "kullanilan": kacan}
		else:
			seri["gun"] = 1
			olay = {"tur": "yeniden"}
	seri["son_gun"] = gun
	seri["en_uzun"] = maxi(seri["en_uzun"], seri["gun"])
	if seri["gun"] % DONDURMA_ARALIGI == 0:
		seri["dondurma"] = mini(DONDURMA_TAVAN, seri["dondurma"] + 1)
	olay["gun"] = seri["gun"]
	return olay
