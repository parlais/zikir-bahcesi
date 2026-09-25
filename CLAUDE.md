# Zikir Bahçesi — Claude için proje hafızası

Bu dosya her yeni oturumda otomatik okunur. Önce burayı, sonra "Okunacak belgeler" listesini oku.

## Proje
- Sesli zikirle fidan dikilen, Kur'an'daki cennet tasvirlerinden ilham alan 3D bir mobil oyun.
- Hedef kitle 7-12 yaş ve aileleri. Çocuk varsayılanları herkese uygulanır: reklam yok, ses cihazdan çıkmaz, üçüncü parti SDK yok.
- Motor Godot 4.7.2. Bütün 3D modeller depodaki Python model fabrikasında prosedürel üretilir; Tripo kullanılmıyor.
- Kullanıcıyla her zaman **Türkçe** konuş. Kod ve belgelerdeki adlar da Türkçedir.
- Kullanıcı görsel olarak çok titiz; "ultra kaliteli", etkileyici bir sonuç istiyor. Dini hassasiyetler önemli: dayanak, temsil dili ve danışma kurulu teyidi.

## Okunacak belgeler (sırayla)
1. `docs/kararlar.md`: bütün kararlar (K1-K13). Özellikle K10 (mekân), K11 (stil), K12 (ışık) ve K13 (ışık geçişinin tetikleyicisi, sıra, canlılar).
2. `docs/plan-faz2b.md`: **sıradaki işlerin planı.** Kullanıcı 2026-09-25'te onayladı (K13).
3. `docs/mekan-kurgusu.md`: cennet mekânının dayanakları (ayet, hadis, Risale-i Nur, Ali Ünal), 28. Söz'deki koni misalinin metni, danışma kurulu soruları.
4. `docs/plan-faz2a.md`: geçmiş kaydı. En üstteki "Revizyon 2" bölümü, Faz 2a'nın son hâlini anlatır.
5. `docs/asset-listesi.md`: içeriğin tek kaynağı (157 asset, 99+2 esma, tarifler). `docs/rapor.md`: fizibilite raporu. `docs/stil-karsilastirmasi.md`: ilk (çarbağ) stil karşılaştırması.

## Dallar
- Deponun varsayılan dalı `claude/busy-allen-p76wgo`, 2026-09-25'te kullanıcının onayıyla `claude/sleepy-bell-nc2a9a` ile aynı noktaya ilerletildi. İkisi de Faz 2a'nın son hâlini içerir.
- Yeni oturum kendi dalında çalışır ve commit'lerini oraya gönderir.
- Emin olmak için `git log --oneline -3` ile son commit'in "Oturum devri" ya da daha yeni olduğuna bak.

## Şu anki durum (2026-09-25)
**Onaylanmış yön:**
- **Mekân (K10):** Cennet uçsuz bucaksız 8 yatay tabakadır.
  - En üstte Firdevs vardır, ortasında dört ırmağın kaynağı bulunur. Üstte ışık vardır; Arş tasvir edilmez.
  - İçeriden: ufuk açıktır; göğe bakınca üst tabaka görünmez, atmosfer gibi.
  - Irmaklar uzakta bulutların içinden inen çağlayanlarla başlar.
  - Katlar arası çiçekli taş merdivenler bulutlara yükselir. Kullanıcının referansı: çiçek ve sarmaşıkla kaplı, göğe kıvrılan taş merdiven.
  - Dışarıdan (açılış, geçiş): tabakaların kesiti, Dünya'nın katman resimleri gibi.
- **Arsa:** Kadife çimenli boş çayır, inci ve yakut çakıl sınırı, ortada ışıklı Tûbâ çekirdeği. Dev Tûbâ yok.
- **Stil ve ışık (K11, K12):**
  - Filtresiz 3D.
  - Işık ara sıra Nur (altın) ile Sky/Ori (beyaz-turkuaz, nurani parıltılar) arasında değişir. Su, çiçek ve nur kendi ışığıyla parlar.
  - Geçiş zikre ve olaylara bağlıdır (K13). Zemin Nur'dur. Zikir, dua, sure ya da esma tamamlanınca ışık Ori'ye geçer, bir süre kalır, Nur'a döner. Tûbâ aşaması, kat değiştirme, ziyaret ve açılış da geçişi başlatır. Gerçek saate bağlanmaz.
  - Gece yok, güneş diski yok (K5).
  - Pixar ve yağlı boya beğenilmedi; kodu duruyor, kullanılmıyor.

**Yapılanlar:**
- **Faz 1:** İçerik veri katmanı, oyun çekirdeği (`game/core`, 34 test), model fabrikası, küçük adada oynanabilir ilk dilim (`game/scenes/main.tscn`).
- **İlk stil karşılaştırması:** Çarbağ sahnesi `game/scenes/stil/`, çekimler `docs/goruntuler/stil/`.
- **Faz 2a, model fabrikası (`tools/model_factory/models/`):**
  - `cennet.py`:
    - `ZB_dunya_cennet`: 9 km'lik ova ve dört ırmak
    - `ZB_dunya_selaleler`: gökten inen çağlayanlar
    - `ZB_dunya_kesit`: 8 tabakanın kesiti
    - yerleşim `game/data/dunya_cennet.json`
  - `cennet_bitkileri.py`: sidr, talh, üzüm (a1-a4), koru ve uzak ağaç, Tûbâ çekirdeği.
  - `cennet_yapilari.py`: su köşkü, inci çadır, sedir köşesi, selsebil, âb-ı hayat pınarı, inci çakıl, kat merdiveni.
- **Faz 2a, Godot:**
  - `scenes/ortak/sahne_kurucu.gd` (SahneKurucu: malzeme, çoğaltma, parçacık, ortam).
  - `scenes/dunya/cennet_sahnesi.tscn`: kameralar `ufuk`, `arsa`, `kesit` (ve inceleme için `selale`).
  - `scenes/dunya/animasyon_stilleri.gd`: profiller `nur`, `sky`, `pixar`, `yagli_boya`.
  - Shader'lar (`scenes/stil/shader/`): `gok_cennet`, `selale`, `tugla`, `tavan`, `bulut_denizi`, `resim_filtresi`.
- **Faz 2b (2026-09-25):**
  - **Işık geçişi:** Nur ↔ Ori (`isik_karistirici.gd`, `isik_gecisi.gd`, 13 test). Işıklar çapraz geçer. Cennet sahnesinin varsayılan kipi `nur_ori`.
  - **Çağlayanlar:** at kuyruğu perde, pus zarfı, dip sisi, su rengi gövde (`selale.gdshader`). Ayrıntılar `plan-faz2b.md` içinde.
  - **Nur kesiti:** kullanıcının gördüğü açık, pastel taslağa eşlendi (kontrast, parlaklık, doygunluk).
  - **Araçlar:** `tools/render/dizi.sh` (geçiş dizisi), `film.sh` (akış filmi), `pano.py` (pano, GIF, şerit).
- **Son çekimler (`docs/goruntuler/cennet/`):**
  - `gecis_nur_ori_pano.jpg`: ufuk, arsa ve kesit; t = 0, 0,5, 1
  - `gecis_nur_ori.gif` ve `gecis_nur_ori_serit.jpg`: Nur'dan Ori'ye geçiş
  - `selale_once_sonra.jpg`, `selale_akis_nur.gif` ve `selale_akis_ori.gif`: çağlayanlar
  - Eski taslaklar: `karsilastirma_nur_ori.jpg`, `taslak_*.png`
  - Kavram eskizleri: `eskiz_*.png`

**Sıradaki iş (`docs/plan-faz2b.md`, onaylı sıra):**
1. ~~Nur ↔ Ori ışık geçişi~~ (yapıldı).
2. Kalite: ~~gökten inen çağlayanlar~~ (yapıldı); sırada kesitin derinliği; ağaç ve köşk modelleri; kuşlar ve kelebekler (model fabrikasında, K13).
3. Plandaki mekanikler: nur tohumu ve bahar açılışı, açılış ve katlar arası geçiş (nur izi), merdivenle kat değiştirme, farklı katlardaki arkadaş bahçeleri, Firdevs ve nur katı çekimi.
4. Arayüz (K7) sonra.

**Açık sorular:**
- Danışma kurulu soruları: `mekan-kurgusu.md`.

## Ortam kurulumu (her yeni bulut oturumunda gerekir)
Konteyner temiz başlar. Gerekenler:
```sh
# Godot 4.7.2 (GitHub releases erişilebilir)
mkdir -p /home/user/tools-cache && cd /home/user/tools-cache
curl -sSL -o godot.zip https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_linux.x86_64.zip
unzip -o -q godot.zip && ln -sf $PWD/Godot_v4.7.2-stable_linux.x86_64 /usr/local/bin/godot
# Python paketleri
pip install numpy pygltflib pillow scipy
# Forward+ (Vulkan) için yazılım sürücüsü (GPU yok)
apt-get update -qq && apt-get install -y -qq mesa-vulkan-drivers xvfb
# Model önizleme için
cd /home/user/zikir-bahcesi/tools/preview && npm install
```
- Render çekimi: `xvfb-run` ile, `VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.json`, `--rendering-method forward_plus --rendering-driver vulkan`. Örnek komutlar `docs/stil-karsilastirmasi.md` dosyasında.
- lavapipe yavaş: cennet sahnesi 640×360'ta 8 kare ~1,5 dk, 800×450'de 16 kare ~5 dk. Önce düşük çözünürlükte dene. Uzun çekimleri arka planda çalıştır (komut süre sınırı).
- Ağ: çoğu web sitesi (erisale, archive.org, sorularlaislamiyet vb.) ağ kurallarınca engelli. WebSearch çalışır. Google Fonts için raw.githubusercontent.com erişilebilir; npm ve pypi erişilebilir.

## Komutlar
```sh
python3 tools/content/build_content.py                 # asset listesi -> game/data/*.json
python3 tools/model_factory/build_all.py [filtre]      # modeller -> game/assets/models/*.glb (+ sahne_carbag.json, dunya_cennet.json)
node tools/preview/contact.mjs [filtre] [çıktı.png]    # model kontakt sayfası
godot --headless --path game --import                  # içe aktarım (yeni model/shader sonrası şart)
godot --headless --path game -s res://tests/run_tests.gd   # testler
# Geliştirici argümanları (Game autoload): --zb-senaryo=demo|kart --zb-kartsiz=1 --zb-ekran=yol.png --zb-kare=N
# Stil sahnesi: res://scenes/stil/stil_sahnesi.tscn -- --zb-stil=nur|ghibli|mucevher|gercekci --zb-kamera=portre|sinematik
# Cennet sahnesi: res://scenes/dunya/cennet_sahnesi.tscn -- --zb-anim=nur_ori|nur|sky|pixar|yagli_boya --zb-kamera=ufuk|arsa|kesit
#   nur_ori (varsayılan): Nur ↔ Ori geçişi. --zb-isik=0..1 ışığı sabitler; --zb-ayar="ortam/parlama/0=0.2;gok/bulut=0.5"
#   profil değerlerini dosyaya dokunmadan dener; N tuşu geçişi başlatır.
tools/render/cek.sh nur ufuk 800x450 16 /tmp/nur_ufuk.png   # cennet sahnesi çekimi (lavapipe; ~5 dk, üçü paralel olur)
tools/render/cek.sh nur_ori arsa 800x450 16 /tmp/a.png --zb-isik=0.5   # ek argümanlar sahneye geçer
tools/render/dizi.sh ufuk 640x360 /tmp/dizi/ufuk            # Nur -> Ori geçişi kare kare (~5 dk)
python3 tools/render/pano.py gif /tmp/gecis.gif --gidis-donus /tmp/dizi/ufuk_*.png   # ayrıca: pano, serit
```

## Kodlama kuralları ve bilinen tuzaklar
- **Model dosya adları:** `ZB_[kategori]_[isim]_a[aşama]`. Model fonksiyonları `tools/model_factory/models/*.py` içinde `@model` veya `@asamali` ile kaydolur.
- **Malzeme adları:** glTF malzeme adları (`mat`, `tas`, `yaprak`, `cimen_ot`, `zemin`, `cini`, `su`, `cicek`, `altin`, `nur`, `uzak`...) Godot'da `scenes/ortak/sahne_kurucu.gd` içindeki `MALZEME_TABLOSU` ile stil shader'larına eşlenir.
- **Köşe renkleri:** Godot glTF importer'ı köşe rengini malzemeye bağlamıyor. `vertex_color_use_as_albedo` elle açılmalı (bkz. `bahce.gd` `_susle`) ya da shader override kullanılmalı.
- **Mesh özellikleri:** `smooth(aci)` yumuşak gölge verir; `kure_normal`/`eksen_normal` yaprak kütlesine yumuşak ışık verir; `weight(fn)` rüzgâr ağırlığını COLOR_0.a'ya yazar.
- **Büyük araziler:** `Mesh.CV` (köşe renkleri) verilirse dışa aktarım indeksli olur ve dosya yaklaşık 4 kat küçülür; bu durumda `NV` de verilmelidir. `zemin` shader'ı köşe ağırlığı (`COLOR.a`) 1'den küçük yerlerde köşe rengini gösterir (toprak, kum, arsa çimeni).
- **Ton eşleme:** AgX cennet sahnesinde soluk verdi; profiller ACES kullanır.
- **Sis ve parıltı:** Bu sahne kilometrelerce derin. Hacim sisi, `fog_sun_scatter` ve güçlü parıltı birlikte kullanılırsa görüntü beyaza boğulur (Nur ve Ori'nin ilk denemeleri). Hacim sisi yoğunluğu ~0,0003-0,0004 ve sis ~0,0003 civarında kalmalı.
- **Resim filtresi:** Profilde `filtre` varsa sahne SubViewport'a çizilir, `resim_filtresi.gdshader` ile TextureRect'te boyanır.
  - SubViewport boyutu `get_window().size` olmalı. Proje `canvas_items` ölçekleme kullandığı için görünür alan tuval biriminde büyüktür (ör. 2275×1280).
  - TextureRect için `set_anchors_and_offsets_preset(FULL_RECT)` kullanılmalı; boyutu elle verilmemeli.
- **Shader adları:** Godot shader dilinde `E` ve `PI` gibi adlar yerleşik sabittir; değişken adı olarak kullanılmaz.
- **Fırça dokusu:** Ekran yönüne göre döndürülen desen moiré (parmak izi halkaları) yapar. Fırça izi, Kuwahara'nın örneklediği renklere eklenen sabit gürültüyle elde edilir.
- **Godot'a bağımlı olmayan veri:** Test edilecek sabitler Godot'a (Game autoload) bağlı olmayan sınıflarda durmalı (örnek: `scenes/yerlesim.gd`, `ui/zikir_secenekleri.gd`). Test koşucusu derlenemeyen test dosyasını hata sayar.
- **Işık geçişi (K12, K13):** Nur ile Ori `IsikKaristirici` ile karışır.
  - Kesikli değerler (metin, bool, parıltı kipi) iki uçta aynı olmalı; yoksa geçişin ortasında sıçrama olur. `test_isik.gd` bunu denetler.
  - Yeni bir profil anahtarı iki uca birden yazılmalı; shader varsayılanı bile olsa açıkça yazılır.
  - Işığın yönü karıştırılmaz, iki ışıkla çapraz geçer. Güneşi döndürmek gölgeleri çevirir; yönü sabitlemek de Ori'nin ırmak parıltısını siliyordu.
- **Shader'da ad çakışması:** `ortak.gdshaderinc` uniform'larıyla (`kenar`, `spek`, `sarma`, `toon`, `parlaklik`, `doygunluk`...) aynı adlı yerel değişken "Redefinition" hatası verir ve malzeme hiç çizilmez. Çekim günlüğünde `SHADER ERROR` aranmalı.
- **Köşe renginde veri:** `gltf_export` köşe renklerini sRGB'den doğrusala çevirir. Renk kanalına veri (ör. enine konum) yazılacaksa `_lin2srgb` ile ters çevrilerek yazılır (bkz. `cennet.py` `_gok_selalesi`).
- **Uzak ayrıntı:** Desen `fwidth` ile söndürülürken ortalama görünüşe geçilmeli. Yalnızca söndürülürse zemin rengi kalır; çağlayan uzakta gri bir duman sütununa dönüyordu.
- **Denetim kipi:** `godot --check-only --script` autoload'ları yüklemez; "Identifier not found: Game" hatası yanıltıcıdır. Sahneyi başsız birkaç kare çalıştırmak daha güvenilirdir.
- **Çekimler ve kod:** `taslak_nur_kesit.png`, profilin son ayarından önce çekilmişti; kod 13 ton daha koyu çiziyordu. Taslak çekimi profil değişince yenilenmeli; karşılaştırma yaparken önce eski kodla (git worktree) doğrulanmalı.
- **Commit:** Mesajlar Türkçe. Her adım ayrı commit, sonra oturumun kendi dalına `git push -u origin <dal>`. PR açma (kullanıcı istemedi). Dünya modelleri büyüktür (toplam ~13 MB); ara denemelerde değil, anlamlı adımlarda commit et.
- **Kullanıcının yüklediği dosyalar:** Ali Ünal epub'ları ve Sorularla İslamiyet PDF'i depoya konmaz (telif). Bulgular `docs/mekan-kurgusu.md` dosyasına işlendi.
