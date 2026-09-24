class_name SaveSystem
extends RefCounted
## Kayıt cihazda, user:// altında tek bir JSON dosyasıdır. Hiçbir veri
## cihazdan çıkmaz (rapor §3c; çocuk varsayılanları herkese uygulanır).

const VARSAYILAN_YOL := "user://kayit.json"


static func kaydet(state: GardenState, yol: String = VARSAYILAN_YOL) -> Error:
	var gecici := yol + ".tmp"
	var f := FileAccess.open(gecici, FileAccess.WRITE)
	if f == null:
		return FileAccess.get_open_error()
	f.store_string(JSON.stringify(state.to_dict(), "\t"))
	f.close()
	# Önce geçici dosyaya yazıp sonra taşımak, yazma yarıda kesilirse eski kaydı korur.
	return DirAccess.rename_absolute(gecici, yol)


static func yukle(yol: String = VARSAYILAN_YOL) -> GardenState:
	if not FileAccess.file_exists(yol):
		return GardenState.new()
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(yol))
	if not parsed is Dictionary:
		push_warning("Kayıt okunamadı, yeni bahçe açılıyor: " + yol)
		return GardenState.new()
	return GardenState.from_dict(parsed)
