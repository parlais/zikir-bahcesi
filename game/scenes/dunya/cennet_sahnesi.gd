extends Node3D
## Cennet mekânı (Faz 2a, K10): ilk katın içi ya da 8 tabakanın dıştan kesiti,
## seçilen stille.
##
##   godot --path game res://scenes/dunya/cennet_sahnesi.tscn -- --zb-anim=nur_ori --zb-kamera=ufuk
##   --zb-anim:   nur_ori (varsayılan: Nur ↔ Ori ışık geçişi, K12-K13) | nur | sky | pixar | yagli_boya
##   --zb-kamera: ufuk | arsa | kesit | yakinlasma | model
##   --zb-durum=vitrin | bos | ilk (K20): vitrin dolu bahçe (varsayılan; çekimler), bos yeni oyuncunun
##     gördüğü: yalnız çerçeve (ışık, gök, bulutlar, nur zerreleri, ova, arsanın çimeni,
##     süzülen Tûbâ çekirdeği). --zb-irmak=1,0,0,0 ırmakları (su, süt, bal, şerbet) tek tek açar.
##   --zb-dalga=4: her 4 sn'de bir sabâ halkası (oyunda her sayımda; film için)
##   yakinlasma (K18): kesitten arsaya kesintisiz iniş (aynı mekân). --zb-yakin=0.4 tek bir an;
##     --zb-yakin-sure=8 (sn, oynatma); filmde --zb-yakin-bas=0 --zb-yakin-son=1 (film.sh ile)
##   model: tek bir modeli arsanın ortasında inceleme (K15). --zb-model=ZB_bitki_koru_agac
##     --zb-model-aci=30 (bakış yönü, derece) --zb-model-yukseklik=6 (kamera yükseltisi, derece)
##     --zb-model-doluluk=0.85 (modelin kadrajı doldurma oranı)
##   --zb-tuba=1..5: arsadaki Tûbâ'nın aşaması (tohum, filiz, fidan, olgun, ulu; K17)
##   --zb-kam="x,y,z;hx,hy,hz;fov": kamerayı yerleşim dosyasına dokunmadan dener (konum; hedef; görüş açısı)
##   (ekran görüntüsü için ayrıca --zb-ekran=/yol.png --zb-kare=30; Game autoload yakalar)
##
## nur_ori kipinde ışık zemin olarak Nur'dur; zikir tamamlanınca ya da bir olayda
## Ori'ye geçer ve döner (IsikGecisi, IsikKaristirici). Geliştirici için:
##   --zb-isik=0.5                 ışığı sabitler (0 Nur, 1 Ori)
##   --zb-dizi=/yol/onek           Nur'dan Ori'ye geçişi kare kare çeker (onek_00.png ...) ve çıkar
##       --zb-dizi-adim=13 --zb-dizi-bekle=3 --zb-isinma=16
##   --zb-ayar="ortam/parlama/0=0.2;ortam/parlama_kip=screen"   profil değerlerini dener
##   --zb-film=/yol/onek --zb-film-kare=48   kare kare film (tools/render/film.sh, --fixed-fps ile)
##   N tuşu: zikir tamamlanmış gibi geçişi başlatır
##
## Modeller ve yerleşim (game/data/dunya_cennet.json) model fabrikasında üretilir:
##   python3 tools/model_factory/build_all.py dunya
##
## Profilde "filtre" varsa 3B sahne bir SubViewport'a çizilir ve resim_filtresi
## shader'ıyla ekrana boyanır (yağlı boya).

const YERLESIM := "res://data/dunya_cennet.json"
const GOK := "res://scenes/stil/shader/gok_cennet.gdshader"
const FILTRE := "res://scenes/stil/shader/resim_filtresi.gdshader"

const BULUT_RENK := [Color("ffffff"), Color("c8d4f0")]
## Işık, t en az bu kadar değişince yeniden hesaplanır: %0,4'lük renk adımları
## gözle seçilmez, telefonda her karede bütün malzemeleri güncellemek gerekmez.
const ISIK_ADIM := 0.004
## Bu uzaklıktan (arsadan, metre) ötedeki korular hafif ufuk ağacıyla çizilir (K15, üçgen bütçesi).
const UFUK_AGACI_MESAFE := 700.0

var anim := "nur_ori"
var kamera_modu := "ufuk"
var profil: Dictionary
var yer: Dictionary
var k: SahneKurucu
var _vp: Viewport
var _kesit := false
## Kesit katmanı (K18): dışarıdan görülenler (kesit yüzleri, öteki katlar, siluetler)
var kesit: KesitKurucu
## Işık geçişi (yalnız nur_ori kipinde; diğer stillerde null).
var gecis: IsikGecisi
var _son_t := -1.0
## nur_ori kipinde karışımın iki ucu: [Nur, Ori] (bir kez hesaplanır)
var _uclar: Array = []
## --zb-ayar ile denenen profil değerleri: [yol, değer]
var _ayarlar: Array = []
var _arg := {}
## --zb-kamera=model: incelenen model
var _inceleme_modeli: Node3D
## Yakınlaşma (K18): iç profilin uçları [Nur, Ori], yoldaki konum (0 kesit, 1 arsa) ve
## dışarılık d (1 kesit, 0 içeride; kameranın arsaya uzaklığından)
var _uclar_ic: Array = []
var _yakin := false
var _u := 0.0
var _dis := 1.0
var _kam: Camera3D
var _on_dugumleri: Array[Node] = []
## Boş başlangıç (K20): dünyanın hâli. Anahtarlar DunyaDurumu ile aynıdır (vitrin, tuba,
## kapi, cakil, irmak [su, süt, bal, şerbet], merdiven, yansima {cevre, ova, ufuk, cicek, cimen}).
var durum: Dictionary = {}
const IRMAK_ADLARI := ["su", "sut", "bal", "serbet"]
const ARSA_R := 13.0
## Kapalı ırmak ve çağlayan düğümleri gizli bir tutucuya taşınır (kesitin ve yakınlaşmanın
## görünürlük ayarları onlara dokunmaz)
var _kapali: Node3D
## Sabâ halkası (K20): her zikirde çekirdekten ovaya yayılan halkanın yaşı (sn; < 0 yok)
var _saba_yas := -1.0
const SABA_HIZ := 15.0
const SABA_SURE := 6.0


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--zb-") and a.contains("="):
			_arg[a.get_slice("=", 0).trim_prefix("--zb-")] = a.substr(a.find("=") + 1)
	anim = _arg.get("anim", anim)
	kamera_modu = _arg.get("kamera", kamera_modu)
	if kamera_modu == "derece":
		kamera_modu = "kesit"
	_yakin = kamera_modu == "yakinlasma"
	_kesit = kamera_modu == "kesit" or _yakin
	_ayar_coz(_arg.get("ayar", ""))
	if _yakin:
		_u = clampf(float(_arg.get("yakin", _arg.get("yakin-bas", "0"))), 0.0, 1.0)
	if anim == "nur_ori":
		_uclar = [AnimasyonStilleri.al(IsikKaristirici.UC_NUR, _kesit), AnimasyonStilleri.al(IsikKaristirici.UC_ORI, _kesit)]
		if _yakin:
			_uclar_ic = [AnimasyonStilleri.al(IsikKaristirici.UC_NUR), AnimasyonStilleri.al(IsikKaristirici.UC_ORI)]
		gecis = IsikGecisi.new()
		if _arg.has("isik"):
			gecis.zorla(float(_arg["isik"]))
		Game.olay.connect(gecis.olay)
	# Her sayımda sabâ halkası (boş dünya da her zikre görünür bir karşılık verir)
	Game.durum_degisti.connect(_saba)
	yer = JSON.parse_string(FileAccess.get_file_as_string(YERLESIM))
	durum = _durum_kur(_arg.get("durum", "vitrin"))
	if _yakin:
		# Ortamın yapısı (SDFGI, SSR, hacim sisi) içeridekidir; kesit ucu yalnız sürekli değerleri verir
		_dis = 0.0
		profil = _profil_hesapla(gecis.t if gecis else 0.0)
		_dis = _dis_hesapla(_yakin_kamera(_u)[0])
	else:
		profil = _profil_hesapla(gecis.t if gecis else 0.0)
	_son_t = gecis.t if gecis else 0.0
	k = SahneKurucu.new(self, profil)
	_vp = _filtre_kur() if profil.has("filtre") else get_viewport()
	k.goruntu_kalitesi(_vp)
	k.ortam_kur(GOK)
	_durum_globalleri()
	if _kesit:
		k.agac_payi = 25.0
		_kesit_kur()
	else:
		_kat_kur()
	_kamera_kur()
	if _yakin:
		_yakin_uygula(_u, true)
	if gecis and _arg.has("dizi"):
		_dizi_cek.call_deferred(_arg["dizi"])
	elif _arg.has("film"):
		_film_cek.call_deferred(_arg["film"])


# --------------------------------------------------------------------------
# Işık geçişi (K12, K13)
# --------------------------------------------------------------------------

func _profil_hesapla(t: float) -> Dictionary:
	var p := IsikKaristirici.karistir(_uclar[0], _uclar[1], t) if anim == "nur_ori" else AnimasyonStilleri.al(anim, _kesit)
	if _yakin:
		var ic := IsikKaristirici.karistir(_uclar_ic[0], _uclar_ic[1], t) if anim == "nur_ori" else AnimasyonStilleri.al(anim)
		p = IsikKaristirici.dis_karistir(ic, p, _dis)
	for a in _ayarlar:
		IsikKaristirici.yaz(p, a[0], a[1])
	return p


func _process(dt: float) -> void:
	_saba_ilerle(dt)
	if _yakin and not _arg.has("yakin") and not _arg.has("film"):
		_yakin_uygula(minf(_u + dt / float(_arg.get("yakin-sure", "8")), 1.0))
	if gecis == null:
		return
	gecis.ilerle(dt)
	if absf(gecis.t - _son_t) >= ISIK_ADIM or (gecis.t != _son_t and (gecis.t == 0.0 or gecis.t == 1.0)):
		_isik_uygula(gecis.t)


func _isik_uygula(t: float) -> void:
	_son_t = t
	profil = _profil_hesapla(t)
	k.guncelle(profil)


func _unhandled_input(e: InputEvent) -> void:
	if gecis and e is InputEventKey and e.pressed and not e.echo and (e as InputEventKey).keycode == KEY_N:
		gecis.tetikle("tamamlandi")


## "yol=değer;yol=değer": sayı, #renk, true/false, Color(...) gibi metinler ya da düz metin.
func _ayar_coz(metin: String) -> void:
	for parca in metin.split(";", false):
		var i := parca.find("=")
		if i < 0:
			continue
		var d := parca.substr(i + 1).strip_edges()
		var deger: Variant = d
		if d.is_valid_float():
			deger = float(d)
		elif d.begins_with("#"):
			deger = Color(d)
		elif d == "true" or d == "false":
			deger = d == "true"
		elif d.contains("("):
			deger = str_to_var(d)
		_ayarlar.append([parca.substr(0, i).strip_edges(), deger])


## Geliştirici: Nur'dan Ori'ye geçişi eşit zaman aralıklarıyla kare kare çeker.
## Kareler arasında birkaç kare beklenir ki gökyüzü ışığı ve GI yetişsin.
func _dizi_cek(onek: String) -> void:
	var adim := int(_arg.get("dizi-adim", "13"))
	var bekle := int(_arg.get("dizi-bekle", "3"))
	gecis.zorla(0.0)
	_isik_uygula(0.0)
	for i in int(_arg.get("isinma", "16")):
		await get_tree().process_frame
	for i in adim:
		var faz := float(i) / float(maxi(adim - 1, 1))
		var t := faz * faz * (3.0 - 2.0 * faz)
		gecis.zorla(t)
		_isik_uygula(t)
		for j in bekle:
			await get_tree().process_frame
		var yol := "%s_%02d.png" % [onek, i]
		var err := _vp.get_texture().get_image().save_png(yol)
		print("Dizi karesi: %s t=%.3f (%s)" % [yol, t, error_string(err)])
	get_tree().quit()


## Geliştirici: ısınmadan sonra her kareyi kaydeder. Motor --fixed-fps ile çalıştırılırsa
## kareler eşit zaman adımıyla ilerler (su, parçacık, rüzgâr doğru hızda akar).
func _film_cek(onek: String) -> void:
	var n := int(_arg.get("film-kare", "48"))
	var bas := float(_arg.get("yakin-bas", "0"))
	var son := float(_arg.get("yakin-son", "1"))
	for i in int(_arg.get("isinma", "16")):
		await get_tree().process_frame
	for i in n:
		if _yakin:
			_yakin_uygula(lerpf(bas, son, float(i) / float(maxi(n - 1, 1))))
		await get_tree().process_frame
		var yol := "%s_%03d.png" % [onek, i]
		var err := _vp.get_texture().get_image().save_png(yol)
		print("Film karesi: %s (%s)" % [yol, error_string(err)])
	get_tree().quit()


## Yağlı boya gibi resim filtreleri: sahne SubViewport'a çizilir, ekrana
## filtreli bir TextureRect olarak basılır. Kök görünüm 3B çizmez.
func _filtre_kur() -> Viewport:
	var sv := SubViewport.new()
	sv.size = get_window().size
	sv.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(sv)
	get_viewport().disable_3d = true
	var mat := ShaderMaterial.new()
	mat.shader = load(FILTRE)
	var f: Dictionary = profil["filtre"]
	for a in f:
		mat.set_shader_parameter(a, f[a])
	var katman := CanvasLayer.new()
	add_child(katman)
	var tr := TextureRect.new()
	tr.texture = sv.get_texture()
	tr.material = mat
	tr.stretch_mode = TextureRect.STRETCH_SCALE
	tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	katman.add_child(tr)
	tr.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return sv


# --------------------------------------------------------------------------
# İlk katın içi: ufka uzanan ova, gökten inen ırmaklar, göğe yükselen merdiven
# --------------------------------------------------------------------------

func _kat_kur() -> void:
	_kapali = Node3D.new()
	_kapali.name = "kapali"
	_kapali.visible = false
	add_child(_kapali)
	var dunya := k.ornek("ZB_dunya_cennet", [0, 0, 0, 0, 1])
	# Arazi ırmak yatağı verisini taşır: kapalı ırmağın yatağı düz çayırdır (zemin shader'ı)
	for ad in ["arazi", "arazi_on"]:
		for g in _dugumler(dunya, ad):
			(g as GeometryInstance3D).set_instance_shader_parameter("irmak_yatagi", 1.0)
			# Ova kendi üstüne gölge düşürmez: alçak güneşte küçük tümsekler geniş koyu lekeler
			# bırakıyor, gölge mesafesinin bittiği yerde sert bir sınır çiziyordu (boş ovada
			# belirgin). Ağaçlar ve yapılar zemine gölge düşürmeye devam eder.
			(g as GeometryInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var selaleler := k.ornek("ZB_dunya_selaleler", [0, 0, 0, 0, 1])
	for i in IRMAK_ADLARI.size():
		if _irmak_acik(i):
			continue
		var ad: String = IRMAK_ADLARI[i]
		for n in [dunya.find_child("irmak_" + ad, true, false), dunya.find_child("irmak_%s_on" % ad, true, false),
				selaleler.find_child("selale_" + ad, true, false)]:
			if n:
				(n as Node).reparent(_kapali)
	# Yapılar (su köşkü, inci çadır, sedir köşesi, selsebil, pınar) nimettir: yalnız vitrinde
	if durum["vitrin"]:
		for t in yer["su_kosku"]:
			k.ornek("ZB_yapi_su_kosku", t)
		for t in yer["inci_cadir"]:
			k.ornek("ZB_yapi_inci_cadir", t)
		for t in yer["sedir_kosesi"]:
			k.ornek("ZB_yapi_sedir_kosesi", t)
		for t in yer["selsebil"]:
			k.ornek("ZB_yapi_selsebil_cesmesi", t)
		for t in yer["pinar"]:
			var p := k.ornek("ZB_yapi_ab_i_hayat_pinari", t)
			for isaret in p.find_children("fiskiye_*", "", true, false):
				_fiskiye((isaret as Node3D).global_position)
	# Merdiven kat değiştirme mekaniğiyle gelir; ucundaki bulut çerçevedir
	if durum["merdiven"]:
		for t in yer["merdiven"]:
			k.ornek("ZB_yapi_kat_merdiveni", t)
	if kamera_modu == "model":
		_inceleme_modeli = k.ornek(_arg.get("model", "ZB_bitki_koru_agac"), [0, 0, 0, 0, 1])
		_nur_isaretleri(_inceleme_modeli)
	else:
		_arsa_kur()
	_bitkiler_kur()
	_gok_kur()
	_bulut_katmani()
	_parcaciklar_kur()


## Oyuncunun arsası: ışıklı Tûbâ çekirdeği, tek fidan, ilk çiçekler, nur tohumları.
func _arsa_kur() -> void:
	var a: Dictionary = yer["arsa"]
	var nur_renk := k.yol("parcacik/nur_renk")
	if int(durum["tuba"]) == 0:
		_suzulen_cekirdek(Vector3(a["tuba"][0], a["tuba"][1], a["tuba"][2]))
	else:
		var tuba := k.ornek("ZB_agac_tuba_a%d" % clampi(int(durum["tuba"]), 1, 5), a["tuba"])
		k.agac_isaretle(tuba)
		_nur_isaretleri(tuba)
	# İnci ve yakut çakıllı sınır ilk Bismillah'la gelir (bahçe kapısıyla)
	if durum["cakil"]:
		k.coklu("ZB_obje_inci_cakil", yer["inci_cakil"], false)
	if not durum["vitrin"]:
		# Bahçe kapısı (Bismillah) arsanın doğu kenarında; yolu arsaya dik (yuva tablosu gelince oradan)
		if durum["kapi"]:
			k.ornek("ZB_yapi_bahce_kapisi", [ARSA_R, 0.0, 0.0, 90.0, 1.0])
		return
	for f in a["fidan"]:
		k.agac_isaretle(k.ornek(f[5], f.slice(0, 5)))
	for c in a["cicek"]:
		k.ornek("ZB_cicek_lale_a3", c)
	for p in a["nur_tohumu"]:
		k.parcacik(10, Vector3(p[0], p[1], p[2]), Vector3(0.2, 0.08, 0.2), 0.04, nur_renk, 3.0,
			Vector3(0, 0.1, 0), 0.05, 3.0)


func _bitkiler_kur() -> void:
	if not durum["vitrin"]:
		# Boş başlangıç: ağaç, koru ve çiçek yok; arsanın çevresinde seyrek, kısa çimen tutamları
		k.coklu("ZB_bitki_cimen", _cimen_konumlari(0.35, 0.55, 0.75), false)
		return
	k.coklu("ZB_agac_sidr_a4", yer["sidr"], true, 0.0, true)
	k.coklu("ZB_agac_uzum_a4", yer["uzum"], true, 0.0, true)
	k.coklu("ZB_agac_hurma_a4", yer["hurma"], true, 0.0, true)
	k.coklu("ZB_agac_talh_a4", yer["talh"], true, 0.0, true)
	k.coklu("ZB_agac_nar_a4", yer["nar"], true, 0.0, true)
	k.coklu("ZB_agac_servi_a4", yer["selvi"], true, 0.0, true)
	k.coklu("ZB_bitki_gul_cali", yer["gul"])
	k.coklu("ZB_bitki_lale_tarhi", yer["lale"], false)
	k.coklu("ZB_bitki_koru_agac", yer["koru"], true, 60.0, true)
	# Uzak korular: 700 m'ye kadar dallı hafif ağaç, ötesinde (dikey ekranda birkaç piksel) ufuk ağacı
	var yakin_uzak := []
	var ufuk := []
	for t in yer["uzak_agac"]:
		(yakin_uzak if Vector2(t[0], t[2]).length() < UFUK_AGACI_MESAFE else ufuk).append(t)
	k.coklu("ZB_bitki_uzak_agac", yakin_uzak, false, 250.0, true)
	k.coklu("ZB_bitki_ufuk_agaci", ufuk, false, 1000.0, true)
	# 1. katın uzak koruları (K20): kesit penceresinde 700-2200 m, kuzey kamasında 2,2-4 km
	k.coklu("ZB_bitki_ufuk_agaci", yer.get("uzak_koru", []), false, 0.0, true)
	k.coklu("ZB_bitki_cimen", _cimen_konumlari(), false)


## Modeldeki nur işaretleri (Tûbâ, K17):
##   isik_*  : çekirdeğin nuru; sıcak ışık, yükselen zerreler ve yerde bir hale (her aşamada dipte)
##   nur_tac : tacın içinde süzülen nur zerreleri; konum tacın merkezi, ölçek tacın yarı boyutları
func _nur_isaretleri(model: Node3D) -> void:
	var nur_renk := k.yol("parcacik/nur_renk")
	for isaret in model.find_children("isik_*", "", true, false):
		# İşaretin ölçeği ışığın boyudur (fidanda küçük, ulu Tûbâ'nın kök aralarında orta)
		var o: float = (isaret as Node3D).global_basis.get_scale().x
		# Ölçekli işaretlerde (Tûbâ'nın kök araları) ışık yok: yalnız hale ve zerreler. Oradaki
		# ışıklar tacı ve gövdeyi keskin yatay çizgilerle bölüyordu; telefonda da pahalıdır.
		if o >= 1.0:
			var l := OmniLight3D.new()
			k.bagla(l, "light_color", nur_renk)
			l.light_energy = 2.2
			l.omni_range = 5.0
			l.omni_attenuation = 1.6
			l.shadow_enabled = false
			isaret.add_child(l)
		var pos := (isaret as Node3D).global_position
		k.parcacik(int(40 * o), pos + Vector3(0, 0.25, 0) * o, Vector3(0.35, 0.3, 0.35) * o, 0.05, nur_renk, 3.0,
			Vector3(0, 0.12, 0), 0.08, 4.0)
		# Ölçekli işaretlerde (Tûbâ'nın kök araları) yumuşak bir sızıntı; çekirdekte parlak hale
		_hale(pos, 1.6 * o, nur_renk, 1.2 if o >= 1.0 else 0.8, o < 1.0)
	for isaret in model.find_children("nur_tac*", "", true, false):
		var n3 := isaret as Node3D
		var yari := n3.global_basis.get_scale()
		var hacim := yari.x * yari.y * yari.z
		k.parcacik(clampi(int(hacim * 6.0), 30, 600), n3.global_position, yari * 0.85, 0.06 + yari.y * 0.004,
			nur_renk, 3.0, Vector3(0, -0.03, 0), 0.12, 7.0)


## Gökteki bulut kümeleri: çağlayanların indiği bulutlar, merdivenin ucunu saran
## bulut ve ışık, ufuk üstünde süzülen birkaç küme. Üst tabaka görünmez (K10).
func _gok_kur() -> void:
	var nur_renk := k.yol("parcacik/nur_renk")
	var i := 0
	for s in yer["gok_selale"]:
		var g: float = s[3]
		# Perdenin başı bulutun içinden çıksın: bulutun altı perdenin tepesini örter
		_bulut_kumesi(Vector3(s[0], s[1] + 15.0, s[2]), g * 6.0, 46, 50 + i, 2.2)
		# Bulut çerçevedir; ışığı çağlayanla (ırmakla) birlikte gelir
		if _irmak_acik(i):
			_hale(Vector3(s[0], s[1] - 10.0, s[2]), g * 5.0, nur_renk, 0.5)
		i += 1
	var u: Array = yer["merdiven_ust"]
	var ust := Vector3(u[0], u[1], u[2])
	_bulut_kumesi(ust + Vector3(0, 18, 0), 220.0, 40, 90)
	if durum["merdiven"]:
		_hale(ust + Vector3(0, 25, 0), 260.0, nur_renk, 1.0)
	var rng := RandomNumberGenerator.new()
	rng.seed = 7
	for j in 9:
		var a := rng.randf_range(-1.2, 1.2)
		var r := rng.randf_range(900.0, 2600.0)
		_bulut_kumesi(Vector3(sin(a) * r, rng.randf_range(260.0, 520.0), -cos(a) * r), rng.randf_range(160.0, 320.0),
			18, 120 + j)


## Çimen tutamları: model fabrikasının yazdığı 1 m'lik ızgaradan (yükseklik ve
## çimen ağırlığı). Yoğunluk arsa çevresinde yüksek, uzaklaştıkça azalır.
func _cimen_konumlari(oran := 1.0, olcek_min := 0.55, olcek_max := 1.0) -> Array:
	var iz: Dictionary = yer["izgara"]
	var nx: int = iz["nx"]
	var nz: int = iz["nz"]
	var x0: float = iz["x0"]
	var z0: float = iz["z0"]
	var ys: Array = iz["y_cm"]
	var ws: Array = iz["cimen"]
	var out: Array = []
	var rng := RandomNumberGenerator.new()
	rng.seed = 11
	for j in nz - 1:
		for i in nx - 1:
			var w: float = ws[j * nx + i] / 9.0
			if w < 0.5:
				continue
			var cx := x0 + i + 0.5
			var cz := z0 + j + 0.5
			var d := Vector2(cx, cz - 6.0).length()
			var yog := lerpf(7.0, 1.2, clampf((d - 18.0) / 30.0, 0.0, 1.0))
			if d > 55.0:
				yog = 0.3
			var n := int(yog * w * oran + rng.randf())
			for s in n:
				var fx := rng.randf()
				var fz := rng.randf()
				var y00: float = ys[j * nx + i]
				var y10: float = ys[j * nx + i + 1]
				var y01: float = ys[(j + 1) * nx + i]
				var y11: float = ys[(j + 1) * nx + i + 1]
				var y := lerpf(lerpf(y00, y10, fx), lerpf(y01, y11, fx), fz) / 100.0
				out.append([x0 + i + fx, y - 0.03, z0 + j + fz, rng.randf_range(0, 360), rng.randf_range(olcek_min, olcek_max)])
	return out


func _fiskiye(pos: Vector3) -> void:
	var f := k.parcacik(220, pos, Vector3(0.03, 0.03, 0.03), 0.045, Color(0.88, 0.97, 1.0), 0.3,
		Vector3(0, -6.0, 0), 2.6, 0.85)
	var fm := f.process_material as ParticleProcessMaterial
	fm.direction = Vector3.UP
	fm.spread = 12.0
	fm.turbulence_enabled = false


func _parcaciklar_kur() -> void:
	# Havada süzülen nur zerreleri (Müslim, Cennet 14-22: ışık her şeyden hafifçe yayılır).
	# Geçişte sayı amount_ratio ile değişir: en çok zerre baştan kurulur.
	var en_cok := _en_cok_zerre()
	if en_cok > 0:
		var z := k.parcacik(en_cok, Vector3(-8, 3.5, -40), Vector3(36, 3.0, 36), 0.05, k.yol("parcacik/nur_renk"), 2.5,
			Vector3(0, 0.03, 0), 0.08, 14.0)
		k.bagla(z, "amount_ratio", func(p: Dictionary) -> float: return float(p["parcacik"]["nur"]) / en_cok)
	# Gökten inen çağlayanların dibi: ağaçların üstüne taşan, ışıkta parlayan kabarık su
	# sisi (bulut dokulu). Perdenin çevresindeki serpintiyi selale_pus zarfı verir.
	var sis_renk := func(p: Dictionary) -> Color:
		return p["parcacik"].get("selale_sis", p["parcacik"]["sis_renk"])
	for i in yer["selale_dip"].size():
		if not _irmak_acik(i):
			continue
		var s: Array = yer["selale_dip"][i]
		var g: float = s[3]
		k.parcacik(45, Vector3(s[0], s[1] + g * 0.8, s[2]), Vector3(g * 1.2, g * 0.6, g * 0.8), g * 1.6, sis_renk,
			0.0, Vector3(0, 0.7, 0), 1.2, 16.0, BaseMaterial3D.BILLBOARD_ENABLED, _bulut_doku())
	# Selsebil levhasının dibinde ince serpinti
	for t in (yer["selsebil"] if durum["vitrin"] else []):
		var y := Vector3(t[0], t[1] + 0.6, t[2])
		k.parcacik(30, y + Basis(Vector3.UP, deg_to_rad(t[3])) * Vector3(0, 0, 1.2), Vector3(0.5, 0.05, 0.2), 0.03,
			Color(0.9, 0.97, 1.0), 0.4, Vector3(0, -1.0, 0), 0.3, 1.2)


func _en_cok_zerre() -> int:
	if anim != "nur_ori":
		return int(profil["parcacik"]["nur"])
	return maxi(int(_uclar[0]["parcacik"]["nur"]), int(_uclar[1]["parcacik"]["nur"]))


# --------------------------------------------------------------------------
# Boş başlangıç (K20): dünyanın hâli
# --------------------------------------------------------------------------

## vitrin: dolu bahçe (çekimler, tanıtım). bos: hiç zikir söylenmemiş; yalnız çerçeve.
## (Oyun kipi DunyaDurumu.hesapla ile gelecek; anahtarlar aynıdır.)
func _durum_kur(ad: String) -> Dictionary:
	var d := {"vitrin": true, "tuba": clampi(int(_arg.get("tuba", "1")), 1, 5), "kapi": true, "cakil": true,
		"irmak": [1.0, 1.0, 1.0, 1.0], "merdiven": true,
		"yansima": {"cevre": 1.0, "ova": 1.0, "ufuk": 1.0, "cicek": 1.0, "cimen": 1.0}}
	if ad == "bos" or ad == "ilk":
		d = {"vitrin": false, "tuba": 0, "kapi": false, "cakil": false, "irmak": [0.0, 0.0, 0.0, 0.0],
			"merdiven": false, "yansima": {"cevre": 0.0, "ova": 0.0, "ufuk": 0.0, "cicek": 0.0, "cimen": 0.0}}
	# ilk: açılıştaki ilk Bismillah'tan sonra (nur izi arsayı dolaşır, çakıl sınırı ve kapı gelir)
	if ad == "ilk":
		d["kapi"] = true
		d["cakil"] = true
	if _arg.has("irmak"):
		var v := str(_arg["irmak"]).split_floats(",")
		for i in mini(v.size(), 4):
			d["irmak"][i] = clampf(v[i], 0.0, 1.0)
	return d


## Sabâ halkası başlar (art arda sayımda halka yeniden doğar; çok sık değil)
func _saba() -> void:
	if _saba_yas < 0.0 or _saba_yas > 0.8:
		_saba_yas = 0.0


func _saba_ilerle(dt: float) -> void:
	# Geliştirme: --zb-dalga=4 her 4 sn'de bir halka (film için)
	if _arg.has("dalga"):
		var p := float(_arg["dalga"])
		if _saba_yas < 0.0 or _saba_yas >= p:
			_saba_yas = 0.0
	if _saba_yas < 0.0:
		return
	_saba_yas += dt
	var guc := smoothstep(0.0, 0.3, _saba_yas) * (1.0 - smoothstep(SABA_SURE * 0.5, SABA_SURE, _saba_yas))
	RenderingServer.global_shader_parameter_set("zb_dalga", Vector4(0.0, 0.0, _saba_yas * SABA_HIZ, guc))
	if _saba_yas >= SABA_SURE:
		_saba_yas = -1.0
		RenderingServer.global_shader_parameter_set("zb_dalga", Vector4.ZERO)


func _irmak_acik(i: int) -> bool:
	return float(durum["irmak"][i]) > 0.0


## Durumun shader'a giden değerleri: açık ırmaklar ve kır çiçeklerinin yayıldığı yarıçap
func _durum_globalleri() -> void:
	var ir: Array = durum["irmak"]
	RenderingServer.global_shader_parameter_set("zb_irmak_dolu", Vector4(ir[0], ir[1], ir[2], ir[3]))
	var c: float = durum["yansima"]["cicek"]
	RenderingServer.global_shader_parameter_set("zb_ova_cicek", Vector2(c, 1e5) if c >= 1.0 else Vector2(c, 16.0 + c * 400.0))


## Model içindeki bir düğüm (ve alt düğümleri): GeometryInstance3D listesi
func _dugumler(kok: Node, ad: String) -> Array:
	var n := kok.find_child(ad, true, false)
	if n == null:
		return []
	var out: Array = [n] if n is GeometryInstance3D else []
	out.append_array(n.find_children("*", "GeometryInstance3D", true, false))
	return out


## Tûbâ çekirdeği, zikirden önce (K20): arsanın ortasında diz boyunda süzülen bir nur. Toprak
## ve model yok; küçük bir ışık, hale ve zerreler, nefes alır gibi yavaşça parlar. İlk
## tevhidde toprağa iner ve a1 olur (Küllî Kaideler 1: iman çekirdeği).
func _suzulen_cekirdek(taban: Vector3) -> void:
	var nur_renk := k.yol("parcacik/nur_renk")
	var pos := taban + Vector3(0, 0.55, 0)
	var l := OmniLight3D.new()
	k.bagla(l, "light_color", nur_renk)
	l.light_energy = 1.6
	l.omni_range = 4.0
	l.omni_attenuation = 1.6
	l.shadow_enabled = false
	l.position = pos
	add_child(l)
	var ic := _hale(pos, 0.5, nur_renk, 1.6)
	var dis := _hale(pos, 2.4, nur_renk, 0.7, true)
	k.parcacik(36, pos, Vector3(0.35, 0.3, 0.35), 0.04, nur_renk, 3.0, Vector3(0, 0.1, 0), 0.08, 4.0)
	# Nefes: 4 sn'lik yavaş parıltı
	var tw := create_tween().set_loops()
	tw.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tw.tween_property(dis, "scale", Vector3.ONE * 1.12, 2.0)
	tw.parallel().tween_property(ic, "scale", Vector3.ONE * 1.15, 2.0)
	tw.parallel().tween_property(l, "light_energy", 2.1, 2.0)
	tw.tween_property(dis, "scale", Vector3.ONE * 0.9, 2.0)
	tw.parallel().tween_property(ic, "scale", Vector3.ONE * 0.9, 2.0)
	tw.parallel().tween_property(l, "light_energy", 1.3, 2.0)


# --------------------------------------------------------------------------
# Dıştan kesit: uzanıp giden 8 tabaka (K10)
# --------------------------------------------------------------------------

func _kesit_kur() -> void:
	# İlk kat, içerideki dünyanın kendisidir: aynı arazi, ırmaklar, çağlayanlar, köşkler,
	# merdiven, korular, arsa ve Tûbâ. Kesme düzleminin önündekiler gizlenir.
	var olcu: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(KesitKurucu.VERI))["olcu"]
	var on := Node3D.new()
	on.name = "kesme_onu"
	on.visible = false
	add_child(on)
	k.on_ebeveyn = on
	k.kesme_z = float(olcu["kesme_z"])
	_kat_kur()
	for n in find_children("*_on", "Node3D", true, false):
		(n as Node3D).visible = false
	k.kesit_dislik = 1.0
	k.kesit_globalleri()
	kesit = KesitKurucu.new(self, k)
	kesit.kur()


# --------------------------------------------------------------------------
# Bulut, hale, hüzme
# --------------------------------------------------------------------------

var _bulut_doku_onbellek: Texture2D


## Kabarık bulut dokusu: düzensiz kenarlı, tepesi aydınlık, altı hafif gölgeli (bir kez üretilir).
func _bulut_doku() -> Texture2D:
	if _bulut_doku_onbellek:
		return _bulut_doku_onbellek
	var n := FastNoiseLite.new()
	n.seed = 3
	n.frequency = 0.035
	n.fractal_octaves = 4
	var boy := 128
	var img := Image.create(boy, boy, false, Image.FORMAT_RGBA8)
	for y in boy:
		for x in boy:
			var u := (float(x) / boy - 0.5) * 2.0
			var v := (float(y) / boy - 0.5) * 2.0
			var r := sqrt(u * u + v * v * 1.3)
			var g := n.get_noise_2d(x, y) * 0.5 + 0.5
			var a := clampf((1.0 - r) * 1.8 + (g - 0.5) * 0.9 - 0.2, 0.0, 1.0)
			a = a * a * (3.0 - 2.0 * a)
			var isik := clampf(0.78 + 0.3 * (-v) + (g - 0.5) * 0.25, 0.6, 1.08)
			img.set_pixel(x, y, Color(isik, isik, isik * 0.99, a))
	_bulut_doku_onbellek = ImageTexture.create_from_image(img)
	return _bulut_doku_onbellek


## Kabarık bulut billboard'larından küme: tepesi sıcak beyaz, altı gölgeli.
## yatay: kümenin yatayda ne kadar yayıldığı (1 yuvarlak, 3 uzun bulut şeridi).
## Kartlar _bulut_kartlari'na küme olarak eklenir; _bulut_katmani() MultiMesh'lerle kurar.
func _bulut_kumesi(merkez: Vector3, boyut: float, adet: int, tohum: int, yatay := 1.0) -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = tohum
	var kume: Array = []
	_bulut_kartlari.append(kume)
	for i in adet:
		var o := Vector3(rng.randf_range(-0.75, 0.75) * yatay, rng.randf_range(-0.22, 0.28), rng.randf_range(-0.5, 0.5)) * boyut
		var s := boyut * rng.randf_range(0.5, 0.9) * (1.0 - 0.4 * absf(o.x) / (boyut * yatay))
		var yuk := clampf(o.y / (boyut * 0.3) * 0.5 + 0.5, 0.0, 1.0)
		var f := yuk * 0.8 + rng.randf() * 0.2
		kume.append([Transform3D(Basis().scaled(Vector3(s, s * 0.8, 1.0)), merkez + o), f])


var _bulut_kartlari: Array = []


## Bulut kartlarını MultiMesh'lerle kurar (bulut_kart.gdshader): her kart kameraya döner;
## uzaktan yakına (kameralar kuzeye, -z'ye bakar) sıralı çizilir. Renk bulut_renk'ten.
## birlesik = false: küme başına bir MultiMesh (içeride; haleler ve çağlayan pusuyla saydam
## sıralama eskisi gibi küme küme kalır). true: hepsi tek çizim (kesitte uzak katlar).
## Eskiden her kart ayrı bir MeshInstance ve malzemeydi (yüzlerce çizim çağrısı).
func _bulut_katmani(ebeveyn: Node = null, birlesik := false) -> void:
	if _bulut_kartlari.is_empty():
		return
	var kumeler := _bulut_kartlari
	_bulut_kartlari = []
	var mesh := QuadMesh.new()
	mesh.size = Vector2(1, 1)
	var mat := ShaderMaterial.new()
	mat.shader = load("res://scenes/stil/shader/bulut_kart.gdshader")
	mat.set_shader_parameter("doku", _bulut_doku())
	k.bagla(mat, "shader_parameter/acik", func(p: Dictionary) -> Color: return (p.get("bulut_renk", BULUT_RENK)[0] as Color))
	k.bagla(mat, "shader_parameter/golge", func(p: Dictionary) -> Color: return (p.get("bulut_renk", BULUT_RENK)[1] as Color))
	mesh.material = mat
	if birlesik:
		var hepsi: Array = []
		for kume in kumeler:
			hepsi.append_array(kume)
		kumeler = [hepsi]
	# Kümede uzaktan yakına: içeride kameralar arsanın çevresindedir (eski kartlar kameraya
	# uzaklıkla sıralanıyordu); kesitte kamera güneyde, uzaktadır (z sırası)
	var goz := Vector3(10, 10, 30)
	if not birlesik:
		# Küme, merkezine göre uzak ve yakın yarıya bölünür: halelerle saydam sıralama eski
		# kart kart sıralamaya yakın kalır (hale iki yarının arasına düşer)
		var yarilar: Array = []
		for kume: Array in kumeler:
			var merkez := Vector3.ZERO
			for kart in kume:
				merkez += (kart[0] as Transform3D).origin
			var r := (merkez / kume.size()).distance_to(goz)
			var uzak: Array = []
			var yakin: Array = []
			for kart in kume:
				((uzak if (kart[0] as Transform3D).origin.distance_to(goz) > r else yakin) as Array).append(kart)
			for y in [uzak, yakin]:
				if not (y as Array).is_empty():
					yarilar.append(y)
		kumeler = yarilar
	for kume: Array in kumeler:
		if birlesik:
			kume.sort_custom(func(a: Array, b: Array) -> bool: return (a[0] as Transform3D).origin.z < (b[0] as Transform3D).origin.z)
		else:
			kume.sort_custom(func(a: Array, b: Array) -> bool:
				return (a[0] as Transform3D).origin.distance_squared_to(goz) > (b[0] as Transform3D).origin.distance_squared_to(goz))
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.use_custom_data = true
		mm.mesh = mesh
		mm.instance_count = kume.size()
		for i in kume.size():
			mm.set_instance_transform(i, kume[i][0])
			mm.set_instance_custom_data(i, Color(kume[i][1], 0, 0, 0))
		var mmi := MultiMeshInstance3D.new()
		mmi.multimesh = mm
		mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		(ebeveyn if ebeveyn else self).add_child(mmi)


var _isik_doku_onbellek: Texture2D


## Kenarı belirsiz parıltı dokusu (üstel sönüm): hale düz bir disk gibi görünmesin.
func _isik_doku() -> Texture2D:
	if _isik_doku_onbellek:
		return _isik_doku_onbellek
	var boy := 128
	var img := Image.create(boy, boy, false, Image.FORMAT_RGBA8)
	for y in boy:
		for x in boy:
			var u := (float(x) / boy - 0.5) * 2.0
			var v := (float(y) / boy - 0.5) * 2.0
			var r2 := u * u + v * v
			var a := clampf(exp(-r2 * 5.0) * 0.8 + exp(-r2 * 30.0) * 0.4 - 0.0067, 0.0, 1.0)
			img.set_pixel(x, y, Color(1, 1, 1, a))
	_isik_doku_onbellek = ImageTexture.create_from_image(img)
	return _isik_doku_onbellek


## Işık halesi: her yöne bakan yumuşak, eklemeli parıltı. renk: Color ya da k.yol(...).
func _hale(pos: Vector3, boy: float, renk: Variant, guc: float, yumusak := false) -> MeshInstance3D:
	var q := QuadMesh.new()
	q.size = Vector2(boy, boy)
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.albedo_texture = _isik_doku() if yumusak else k.yuvarlak_doku()
	_renk_bagla(m, renk, guc)
	m.disable_fog = true
	q.material = m
	var mi := MeshInstance3D.new()
	mi.mesh = q
	mi.position = pos
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mi)
	return mi


## Göğe uzanan dikey ışık hüzmesi (Arş tasvir edilmez; ışık yukarıda söner).
func _huzme(pos: Vector3, boyut: Vector2, renk: Variant, guc: float) -> void:
	var img := Image.create(64, 256, false, Image.FORMAT_RGBA8)
	for y in 256:
		var v := float(y) / 255.0
		for x in 64:
			var u := (float(x) / 63.0 - 0.5) * 2.0
			var a := exp(-u * u * 4.0) * pow(v, 1.8) * (1.0 - pow(1.0 - v, 12.0))
			img.set_pixel(x, y, Color(1, 1, 1, a))
	var q := QuadMesh.new()
	q.size = boyut
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.billboard_mode = BaseMaterial3D.BILLBOARD_FIXED_Y
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.albedo_texture = ImageTexture.create_from_image(img)
	_renk_bagla(m, renk, guc)
	m.disable_fog = true
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	q.material = m
	var mi := MeshInstance3D.new()
	mi.mesh = q
	mi.position = pos
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mi)


func _renk_bagla(m: BaseMaterial3D, renk: Variant, guc: float) -> void:
	if renk is Callable:
		k.bagla(m, "albedo_color", func(p: Dictionary) -> Color: return (renk as Callable).call(p) * guc)
	else:
		m.albedo_color = renk * guc


# --------------------------------------------------------------------------
# Kamera
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Yakınlaşma (K18): kesitten arsaya kesintisiz; aynı mekân
# --------------------------------------------------------------------------

## Yakınlaşmanın hedefi (arsa) ve dışarılığın ölçüldüğü nokta
const YAKIN_MERKEZ := Vector3(0, 5, 0)


## Yoldaki u (0 kesit, 1 arsa) için [konum, hedef, fov]. Anahtar kareler yerleşimdedir.
## Kamera, arsaya uzaklığının logaritmasıyla ilerler (ekranda sabit algılanan hız); yön ve
## uzaklık ayrı ayrı yumuşak eğrilerle karışır. Uçlar anahtar karelerin kendisidir.
func _yakin_kamera(u: float) -> Array:
	var kler: Array = yer["kameralar"]["yakinlasma"]
	var n := kler.size()
	var L: Array = []
	var Y: Array = []
	var H: Array = []
	var F: Array = []
	for kr in kler:
		var p := Vector3(kr["konum"][0], kr["konum"][1], kr["konum"][2]) - YAKIN_MERKEZ
		L.append(log(p.length()))
		Y.append(p.normalized())
		H.append(Vector3(kr["hedef"][0], kr["hedef"][1], kr["hedef"][2]))
		F.append(log(tan(deg_to_rad(float(kr["fov"])) * 0.5)))
	# u -> log uzaklık (uçlarda yumuşak giriş ve çıkış)
	var e := u * u * u * (u * (u * 6.0 - 15.0) + 10.0)
	var l := lerpf(L[0], L[n - 1], e)
	var i := 0
	while i < n - 2 and l < L[i + 1]:
		i += 1
	var t := clampf((L[i] - l) / (L[i] - L[i + 1]), 0.0, 1.0)
	var i0 := maxi(i - 1, 0)
	var i3 := mini(i + 2, n - 1)
	var yon: Vector3 = _cr(Y[i0], Y[i], Y[i + 1], Y[i3], t).normalized()
	var hedef: Vector3 = _cr(H[i0], H[i], H[i + 1], H[i3], t)
	var fov := rad_to_deg(2.0 * atan(exp(lerpf(F[i], F[i + 1], t * t * (3.0 - 2.0 * t)))))
	return [YAKIN_MERKEZ + yon * exp(l), hedef, fov]


static func _cr(p0: Vector3, p1: Vector3, p2: Vector3, p3: Vector3, t: float) -> Vector3:
	var t2 := t * t
	var t3 := t2 * t
	return 0.5 * ((2.0 * p1) + (-p0 + p2) * t + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t2 + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t3)


## Dışarılık: 1 uzakta (kesit), 0 arsaya ~80 m kala (içeride). Kameranın konumundan
## hesaplanır: ileride oyuncu elle yakınlaştırsa da aynı çalışır. İç sis ancak yere
## yaklaşınca tamamlanır; yüksekten bakınca ova süt beyazına boğulmaz.
func _dis_hesapla(konum: Vector3) -> float:
	var x := clampf((log(konum.distance_to(YAKIN_MERKEZ)) - log(80.0)) / (log(6000.0) - log(80.0)), 0.0, 1.0)
	return x * x * (3.0 - 2.0 * x)


func _yakin_uygula(u: float, ilk := false) -> void:
	_u = u
	var kr := _yakin_kamera(u)
	var konum: Vector3 = kr[0]
	_kam.position = konum
	_kam.look_at(kr[1])
	_kam.fov = kr[2]
	var uz := konum.distance_to(YAKIN_MERKEZ)
	_kam.near = clampf(uz * 0.0008, 0.15, 40.0)
	# Arsa kamerasının uzak bulanıklığı son anda gelir
	var ayar := _kam.attributes as CameraAttributesPractical
	ayar.dof_blur_far_enabled = true
	ayar.dof_blur_far_distance = 140.0
	ayar.dof_blur_far_transition = 300.0
	ayar.dof_blur_amount = 0.025 * smoothstep(0.93, 1.0, u)
	var d := _dis_hesapla(konum)
	# Kesme düzleminin önündekiler, kamera düzlemi geçince görünür (o an kameranın arkasındadır)
	var onde := konum.z > k.kesme_z
	if _on_dugumleri.is_empty():
		_on_dugumleri = find_children("*_on", "Node3D", true, false)
		_on_dugumleri.append(get_node("kesme_onu"))
	for n in _on_dugumleri:
		(n as Node3D).visible = not onde
	kesit.uygula(d, konum)
	if ilk or absf(d - _dis) >= ISIK_ADIM:
		_dis = d
		k.kesit_dislik = d
		_isik_uygula(gecis.t if gecis else 0.0)


func _kamera_kur() -> void:
	var tanim: Dictionary = yer["kameralar"]["kesit"] if _yakin else yer["kameralar"].get(kamera_modu, yer["kameralar"]["ufuk"])
	var kam := Camera3D.new()
	if _vp is SubViewport:
		_vp.add_child(kam)
	else:
		add_child(kam)
	_kam = kam
	var kn: Array = tanim["konum"]
	var hd: Array = tanim["hedef"]
	kam.position = Vector3(kn[0], kn[1], kn[2])
	kam.look_at(Vector3(hd[0], hd[1], hd[2]))
	kam.fov = tanim["fov"]
	if _arg.has("kam"):
		# Geliştirme: --zb-kam="x,y,z;hx,hy,hz;fov" kamerayı yerleşim dosyasına dokunmadan dener
		var p: PackedStringArray = str(_arg["kam"]).split(";")
		var a := p[0].split_floats(",")
		var b := p[1].split_floats(",")
		kam.position = Vector3(a[0], a[1], a[2])
		kam.look_at(Vector3(b[0], b[1], b[2]))
		kam.fov = float(p[2])
	if _inceleme_modeli:
		_model_kamerasi(kam)
	kam.near = 0.15
	kam.far = 90000.0 if _kesit else 12000.0
	if _arg.has("kam"):
		kam.far = 120000.0
	var ayar := CameraAttributesPractical.new()
	if kamera_modu == "arsa":
		ayar.dof_blur_far_enabled = true
		ayar.dof_blur_far_distance = 140.0
		ayar.dof_blur_far_transition = 300.0
		ayar.dof_blur_amount = 0.025
	kam.attributes = ayar
	kam.current = true


## İnceleme kamerası: modelin sınır kutusunu dikey ya da yatay kadraja sığdırır.
func _model_kamerasi(kam: Camera3D) -> void:
	var kutu := AABB()
	var ilk := true
	for mi in _inceleme_modeli.find_children("*", "MeshInstance3D", true, false):
		var b: AABB = (mi as MeshInstance3D).global_transform * (mi as MeshInstance3D).get_aabb()
		kutu = b if ilk else kutu.merge(b)
		ilk = false
	var aci := deg_to_rad(float(_arg.get("model-aci", "30")))
	var yuk := deg_to_rad(float(_arg.get("model-yukseklik", "6")))
	var dolu := float(_arg.get("model-doluluk", "0.85"))
	kam.fov = 40.0
	var boyut := Vector2(get_window().size)
	var oran := boyut.x / boyut.y
	var dik := tan(deg_to_rad(kam.fov) * 0.5)
	var yan := dik * oran
	var genis := maxf(kutu.size.x, kutu.size.z)
	var uzak := maxf(kutu.size.y * 0.5 / dik, genis * 0.5 / yan) / dolu + genis * 0.5
	var merkez := kutu.get_center()
	var yon := Vector3(sin(aci) * cos(yuk), sin(yuk), cos(aci) * cos(yuk))
	kam.position = merkez + yon * uzak
	kam.look_at(merkez)
