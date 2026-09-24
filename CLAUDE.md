# Zikir Bahçesi — Claude için proje hafızası

Bu dosya her yeni oturumda otomatik okunur. Önce burayı, sonra "Okunacak belgeler" listesini oku.

## Proje
- Sesli zikirle fidan dikilen, Kur'an'daki cennet tasvirlerinden ilham alan 3D bir mobil oyun.
- Hedef kitle 7-12 yaş ve aileleri. Çocuk varsayılanları herkese uygulanır: reklam yok, ses cihazdan çıkmaz, üçüncü parti SDK yok.
- Motor Godot 4.7.2. Bütün 3D modeller depodaki Python model fabrikasında prosedürel üretilir; Tripo kullanılmıyor.
- Kullanıcıyla her zaman **Türkçe** konuş. Kod ve belgelerdeki adlar da Türkçedir.
- Kullanıcı görsel olarak çok titiz; "ultra kaliteli", etkileyici bir sonuç istiyor. Dini hassasiyetler önemli: dayanak, temsil dili ve danışma kurulu teyidi.

## Okunacak belgeler (sırayla)
1. `docs/kararlar.md`: bütün kararlar (K1-K8) ve onay bekleyen tasarım değerleri.
2. `docs/plan-faz2a.md`: **şu anki plan.** Kullanıcı onay vermedi; başlamadan önce kullanıcıya teyit ettir.
3. `docs/mekan-kurgusu.md`: cennet mekânının ayet, hadis, Risale-i Nur ve Ali Ünal dayanakları; danışma kurulu soruları; asset listesinde yeniden düşünülecekler.
4. `docs/stil-karsilastirmasi.md`: yapılmış 4 stillik karşılaştırma (Nur, Boyalı, Mücevher, Gerçekçi) ve nasıl yeniden çekileceği.
5. `docs/asset-listesi.md`: içeriğin tek kaynağı (157 asset, 99+2 esma, tarifler). `docs/rapor.md`: fizibilite raporu.

## Şu anki durum (2026-09-24)
Çalışma dalı: `claude/sleepy-bell-nc2a9a` (önceki işler `claude/busy-allen-p76wgo` dalındaydı; bu dal onun devamı).

Yapılanlar:
- **Faz 1:**
  - içerik veri katmanı
  - oyun çekirdeği (`game/core`; 34 test geçiyor)
  - model fabrikası ve 22 model
  - küçük adada dokunmatik tesbihle oynanabilir ilk dilim (`game/scenes/main.tscn`)
- **Stil karşılaştırması:**
  - büyük çarbağ sahnesi (`game/scenes/stil/`), stil shader'ları, 4 stil profili
  - arayüz önizlemesi (`game/ui/arayuz_onizleme.gd`)
  - çekimler `docs/goruntuler/stil/` altında

- **Faz 2a, ara durak:**
  - Kullanıcı planı onayladı. Mekân önce yalnız Pixar stilinde gösterilecek, onaydan sonra dört stile geçilecek.
  - Model fabrikası:
    - `models/cennet.py`: ova, dört ırmak, derece duvarları, çağlayanlar, koni-dağ; yerleşim `game/data/dunya_cennet.json`
    - `models/cennet_bitkileri.py`: sidr, talh, üzüm a1-a4; koru ve uzak ağaç; Tûbâ çekirdeği; dev Tûbâ
    - `models/cennet_yapilari.py`: su köşkü, inci çadır, sedir köşesi, selsebil, âb-ı hayat pınarı, inci çakıl
  - Godot:
    - `scenes/ortak/sahne_kurucu.gd` (SahneKurucu), `scenes/dunya/cennet_sahnesi.tscn`
    - `animasyon_stilleri.gd`: şimdilik yalnız Pixar profili
    - yeni shader'lar: `gok_cennet`, `selale`, `tugla`, `bulut_denizi`
  - Taslak çekimler (800×450): `docs/goruntuler/cennet/taslak_pixar_{ufuk,arsa,derece}.png`. Kullanıcıya gönderildi, geri bildirim bekleniyor.
  - Arsa çıplak toprak yerine kadife çimenli boş çayır ve inci/yakut çakıl sınırı olarak yorumlandı (gerekçe `mekan-kurgusu.md`). Kullanıcıya soruldu.

Kullanıcının son geri bildirimleri:
- Çarbağ "fena değil" ama istenen cennet hissi değil. Yeni mekân: katlı koni-dağ (bkz. K4 ve `mekan-kurgusu.md`).
- Gece-gündüz ve mevsim yok (K5).
- Stil animasyon stili olarak seçilecek; dördü birden gösterilecek (K6).
- Arayüz sonra baştan ele alınacak (K7).

**Sıradaki iş:** Kullanıcının Pixar taslakları hakkındaki mekân geri bildirimini al ve işle. Mekân onaylanınca:
1. Ghibli, Arcane ve Sky/Ori profillerini `animasyon_stilleri.gd` içine yaz. `resim_filtresi.gdshader` (Kuwahara, kontur, kâğıt) ve `ortak.gdshaderinc` içine `firca` parametresini ekle.
2. 4 stil × 3 kamera (`ufuk`, `arsa`, `derece`) çek: 1600×900, `docs/goruntuler/cennet/`, ardından karşılaştırma panoları.
3. Taslakta kalan kalite işleri: kuşlar ve kelebekler, köşk ve duvar ayrıntısı, koni-dağın daha doğal silüeti.

Açık sorular:
- Canlılar için AI 3D aracı ya da karma üretim kabul edilir mi?
- Çizim tarzı: yumuşak, toon ya da ara?
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
apt-get update -qq && apt-get install -y -qq mesa-vulkan-drivers
# Model önizleme için
cd /home/user/zikir-bahcesi/tools/preview && npm install
```
- Render çekimi: `xvfb-run` ile, `VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.json`, `--rendering-method forward_plus --rendering-driver vulkan`. Örnek komutlar `docs/stil-karsilastirmasi.md` dosyasında.
- lavapipe yavaş: 800×450'de 20 kare yaklaşık 1 dakika sürer. Önce yarım çözünürlükte dene, sonra tam çözünürlükte çek. 4 çekim aynı anda çalışırsa süre sınırı (1500 sn) aşılabilir.
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
# Cennet sahnesi: res://scenes/dunya/cennet_sahnesi.tscn -- --zb-anim=pixar --zb-kamera=ufuk|arsa|derece
#   (640x360, 8 kare ~1,5 dk; üç kamera paralel ~3 dk; 800x450, 16 kare paralel ~6 dk)
```

## Kodlama kuralları ve bilinen tuzaklar
- **Model dosya adları:** `ZB_[kategori]_[isim]_a[aşama]`. Model fonksiyonları `tools/model_factory/models/*.py` içinde `@model` veya `@asamali` ile kaydolur.
- **Malzeme adları:** glTF malzeme adları (`mat`, `tas`, `yaprak`, `cimen_ot`, `zemin`, `cini`, `su`, `cicek`, `altin`, `nur`, `uzak`...) Godot'da `scenes/ortak/sahne_kurucu.gd` içindeki `MALZEME_TABLOSU` ile stil shader'larına eşlenir.
- **Köşe renkleri:** Godot glTF importer'ı köşe rengini malzemeye bağlamıyor. `vertex_color_use_as_albedo` elle açılmalı (bkz. `bahce.gd` `_susle`) ya da shader override kullanılmalı.
- **Mesh özellikleri:** `smooth(aci)` yumuşak gölge verir; `kure_normal`/`eksen_normal` yaprak kütlesine yumuşak ışık verir; `weight(fn)` rüzgâr ağırlığını COLOR_0.a'ya yazar.
- **Büyük araziler:** `Mesh.CV` (köşe renkleri) verilirse dışa aktarım indeksli olur ve dosya yaklaşık 4 kat küçülür; bu durumda `NV` de verilmelidir. `zemin` shader'ı köşe ağırlığı (`COLOR.a`) 1'den küçük yerlerde köşe rengini gösterir (toprak, kum, arsa çimeni).
- **Ton eşleme:** AgX cennet sahnesinde soluk verdi; Pixar profili ACES kullanır.
- **Godot'a bağımlı olmayan veri:** Test edilecek sabitler Godot'a (Game autoload) bağlı olmayan sınıflarda durmalı (örnek: `scenes/yerlesim.gd`, `ui/zikir_secenekleri.gd`). Test koşucusu derlenemeyen test dosyasını hata sayar.
- **Commit:** Mesajlar Türkçe. Her adım ayrı commit, sonra `git push -u origin claude/sleepy-bell-nc2a9a`. PR açma (kullanıcı istemedi). Dünya modelleri büyüktür (toplam ~11 MB); ara denemelerde değil, anlamlı adımlarda commit et.
- **Kullanıcının yüklediği dosyalar:** Ali Ünal epub'ları ve Sorularla İslamiyet PDF'i depoya konmaz (telif). Bulgular `docs/mekan-kurgusu.md` dosyasına işlendi.
