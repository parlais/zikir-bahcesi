# Faz 2b — Plan (2026-09-25'te onaylandı)

Faz 2a'da mekân ve ışık yönü netleşti:
- **Mekân (K10):** uçsuz bucaksız 8 yatay tabaka.
- **Işık (K12):** Nur ile Ori arasında değişen ışık.

Bu belge sıradaki işleri toplar.

**Onay (K13):**
- Sıra: önce ışık geçişi (1), sonra kalite (2), sonra mekanikler (3).
- Işık geçişi zikre ve olaylara bağlıdır.
- Canlılar model fabrikasında üretilir.

**Geri bildirim (K14, 2026-09-25):**
- Işık geçişi ve süreleri onaylandı; çağlayanlar kabul edildi.
- Genel istek: "her şey daha detaylı ve gerçekçi". Kalan kalite işleri (kesit, ağaç ve köşk modelleri, kuşlar ve kelebekler) bu ölçütle yapılır.
- İki soru soruldu ve cevaplandı (K15):
  - Biçim ve malzeme gerçekçi, ışık rüya gibi.
  - Modeller fabrikada üretilir; yüzey dokuları CC0 kütüphanelerinden gelebilir.
  - İlk iş ağaçlar.

## 1. Işık geçişi: Nur ↔ Ori (K12)
- `animasyon_stilleri.gd` içindeki `nur` ve `sky` profilleri iki uç durumdur. Bir karıştırıcı bunları zamanla yumuşakça birbirine geçirir.
  - Karıştırılacaklar: gök uniform'ları, Environment (sis, parıltı, ambient, pozlama, doygunluk), ana ışığın yönü, rengi ve enerjisi, malzeme uniform'ları, bulut ve parçacık renkleri.
  - Sayılar lerp, renkler Color.lerp, yönler slerp ile karışır.
- Öneri: `game/scenes/dunya/isik_karistirici.gd`.
  - Profil sözlüklerini bir `t` (0 Nur, 1 Ori) ile karıştırır ve SahneKurucu'nun kurduğu nesneleri günceller.
  - Karıştırma fonksiyonu Godot'a bağlı olmamalı ve test edilmeli.
- **Tetikleyici (K13):** zikir ve olay.
  - Zemin Nur'dur. Zikir, dua, sure ya da esma tamamlanınca ışık Ori'ye geçer, bir süre kalır, Nur'a döner.
  - Olaylar da aynı geçişi başlatır: Tûbâ aşaması, kat değiştirme, ziyaret, açılış.
  - Süreler ilk tahmindir; çekimlere bakarak ayarlanır.
- Işık çapraz geçer: Nur'un ışığı ve gökteki parıltısı yerinde söner, Ori'ninkiler kendi yerinde belirir. Gölgeler dönmez, gün dönümü gibi okunmaz.
- Doğrulama: `t` = 0, 0.5 ve 1'de üç çekim; ayrıca kısa bir geçiş dizisi (kare dizisi).

**Durum (2026-09-25): yapıldı.**
- `game/scenes/dunya/isik_karistirici.gd` (IsikKaristirici): iki profili karıştırır.
  - Işık yönü karışmaz, çapraz geçer. Nur'un güneşi `gunes` olarak (1 − t) ile söner, Ori'ninki `gunes_b` olarak t ile belirir.
  - Gökte de iki parıltı var: `nur_yon`, `nur_yon_b` ve `nur_karisim` (`gok_cennet.gdshader`).
  - İlk denemede güneşin yönü Nur'da sabitlenmişti. Ori'nin ırmaktaki beyaz parıltısı ve soldaki pusu kayboldu, bu yüzden çapraz geçişe geçildi.
  - `SABIT` listesindekiler Nur'dan alınır: bulut deseninin ölçeği (bulutlar kaymasın diye) ve sis hacminin uzunluğu.
- Işıklar yalnız geçiş sırasında birlikte yanar; sönmüş ışık gizlenir, gölgesi çizilmez.
- `game/scenes/dunya/isik_gecisi.gd` (IsikGecisi): zamanlayıcı.
  - Nur'dan Ori'ye 6 sn'de çıkar, Ori'den Nur'a 40 sn'de döner.
  - Ori'de kalış olaya göre değişir: tamamlanan zikir 40 sn, esma 60 sn, Tûbâ aşaması 90 sn; kat geçişi ve ziyaret 30 sn, açılış 20 sn.
  - `Game.olay` sinyaline bağlıdır; sahne olayları için `tetikle()` kullanılır.
- `SahneKurucu.guncelle()` ve `bagla()`: ortam, gök, ana ışık, malzemeler ve profilden renk alan her şey çalışma anında güncellenir.
- Cennet sahnesinin varsayılan kipi `nur_ori`. Geliştirici argümanları: `--zb-isik`, `--zb-dizi`, `--zb-ayar`. N tuşu geçişi başlatır.
- Parıltı kipi kesikli olduğu için iki uçta aynı olmalı. Nur, "softlight 0.45"ten aynı görüntüyü veren "screen 0.15"e geçirildi.
- Testler: `game/tests/test_isik.gd` (13 test).

## 2. Kalite (taslaklarda zayıf kalanlar)
- **Gökten inen çağlayanlar:**
  - Uzaktan ışık sütunu gibi görünüyor, su gibi görünmeli.
  - Çare: perdede akış ve köpük, yanlardan dağılan serpinti, dipte büyük sis, tepede bulutun içinden çıkış.
  - **Durum (2026-09-25): yapıldı**, sekiz denemede.
    - Model (`cennet.py` `_gok_selalesi`):
      - Perde (`selale`) tepede dar, aşağı genişler, rüzgârda salınır.
      - Arkasında daha geniş bir serpinti zarfı (`selale_pus`) var.
      - Enine konum ve tepe genişliği köşe renginde taşınır.
    - Shader (`selale.gdshader`):
      - Uzaktan seçilen sık akış çizgileri, aşağı akan köpük öbekleri, keskin köpük kenarı, ince tanecik dokusu, saçılan kenarlar.
      - Gövde doygun su rengindedir: Nur'da camgöbeği-mavi, Ori'de turkuaz-mavi.
      - Çizgiler uzakta seçilmez olunca köpüğün ortalamasına geçilir.
    - Sahne: dipte parlak, kabarık su sisi (`selale_sis`); perdenin başı buluttan çıkar.
    - Öğrenilenler:
      - Sıcak ya da beyaz su altın gökte ışık sütunu, gri su puslu havada duman sütunu gibi okunuyor.
      - Suyu okutan şeyler: doygun su rengi, uzun paralel çizgiler ve akış (film).
      - Uzak görünüş oyunun dikey ekranında (720×1280) değerlendirilmeli. 800×450'lik deneme çekimi, dikey ekranın üçte biri kadar ayrıntı gösterir.
    - İnceleme için `selale` kamerası (360 m) ve akış filmi (`tools/render/film.sh`).
- **Sıra (K15):** önce ağaçlar, sonra kesit, köşk ve çadır, en son kuşlar ve kelebekler.
- **MVP ağaçları ve büyüme aşamaları (K16, K17), durum (2026-09-25): yapıldı.**
  - Her şey zikirle oluştuğu için oyuncu her ağacın büyümesini izler; bütün aşamalar aynı dilde.
  - **Ortak parçalar (`models/agac_asamalari.py`):**
    - `dikim_yeri`: yeni işlenmiş, dokulu toprak tümseği (`yuzey_toprak`, rüzgârda salınmaz).
    - Türe özgü tohumlar (1,6 kat iri):
      - hurma çekirdeği, sidr meyvesi, üzüm çekirdeği, yakut gibi nar taneleri
      - servi kozalağı, çınar tohum topu
      - muzun kökten çıkan sürgünü
    - `filiz`: kıvrık sap ve türün gerçek yaprakları. Tek yaprak atlası `yaprak_tek.png`: sidr, nar, üzüm, çınar, Tûbâ, hurma.
    - `serit_filiz` (hurma fidesi), `servi_filizi` (pul yapraklı sürgünler), `muz_filizi`.
  - **Yeni asset'ler:**
    - nar (a1-a4), servi (a1-a4)
    - çınar (a1-a4): alacalı kabuk dokusu `kabuk_cinar`, derin loplu yaprak atlası, sarkan tohum topları
    - Tûbâ (a1-a5)
  - **Yenilenen aşamalar:** hurma, sidr, talh ve üzüm a1-a2; üzümün a3'ü (kazığa sarılan asma).
  - **Tûbâ (K17):**
    - `yaprak_tuba`: ince altın-beyaz kenar, `yaprak_kart` ışıması.
    - Gümüş-fildişi kabuk; tacın dış yüzünde nur çiçekleri.
    - Dipte nur kökleri ve `isik_cekirdek`; tacın içinde `nur_tac` işareti (Godot nur zerreleri).
    - Arsadaki aşama `--zb-tuba=1..5` ile seçilir.
  - **Düzeltme:** Hurma ve muz gövdeleri rüzgârda dipleriyle birlikte salınıyordu; yaprak dipleri ise sabitti.
    - Gövde artık dipte sabit, uca doğru salınıyor.
    - Yapraklar gövde ucunun ağırlığıyla başlıyor (`GOVDE_UCU_RUZGAR`).
- **Kesit (dış görünüm):**
  - Şema gibi duruyor. Derinlik, ışık ve her katın farklı karakteri güçlenmeli (Rahmân 46-76: üst katlarda çeşitlilik artar).
  - Katlar arası merdivenler seçilir olmalı.
- **Modeller:**
  - Ağaçlar lolipop gibi; taç ve dal ayrıntısı ister.
  - Köşk ve çadırda yakın plan ayrıntısı eksik.
- **Ağaçlar, durum (2026-09-25): yapıldı (K15'e göre ilk iş).**
  - **Üreteç (`tools/model_factory/mf/agac.py`):**
    - Tür parametreli dallanan iskelet: gövde, 2-3 dal seviyesi; paralel taşınan çerçevelerle kıvrılan borular.
    - Gövde dibinde kök genişlemesi ve payanda kök lobları.
    - Kabukta UV var (dokunun bir tekrarı `kabuk_doku` metre).
    - Yapraklar, son dal seviyelerine dizilen yaprak kümesi kartlarıdır: 2×3 köşe, ortadan bükük.
    - Kart normalleri taç zarfına (elips) bükülür: taç tek bir kabarık kütle gibi ışık alır. Taç içi ve altı köşe renginde koyulaşır.
    - Rüzgâr ağırlığı yalnız konuma bağlıdır; kabuk, kart ve meyve aynı yerde aynı salınır.
    - İsteğe bağlı öz hacim (`oz`): tacın içinde koyu bir elips. Uzaktan taç dolu görünür (koru, uzak ağaç, selvi).
    - Meyve yerleri (`meyve_yerleri`), şerit yapraklar (`models/agaclar.py`: hurma, muz).
  - **Dokular (`mf/doku.py`, prosedürel, `game/assets/dokular/`):**
    - Yaprak kümesi atlasları (2×2): koru, sidr, nar, selvi, üzüm (beş loplu yaprak).
    - Tüysü hurma yaprağı ve yırtıklı muz yaprağı şeritleri.
    - Kabuk, hurma gövdesi (yaprak dibi kalıntıları) ve muzun yalancı gövdesi; normal haritalarıyla.
    - Godot içe aktarımı mipmap'li (`_import_ayari`).
    - CC0 kütüphaneleri ağ politikasınca engelli (K15); erişim açılırsa kabuk ve taş dokuları değiştirilebilir.
  - **Türler:**
    - koru (Rahmân 64, koyu yeşil ve dolgun; 5,1 bin üçgen)
    - sidr a3/a4 (şemsiye taç, sarkan dallar, çift çift kirazlar)
    - nar (dipten çatallanan gövdeler, sarkan narlar)
    - selvi (sık, koyu sütun)
    - hurma a3/a4 (tüysü yapraklar, sarmal dizilim, salkımlar)
    - talh a3/a4 (muz kümesi, kat kat eller, mor tomurcuk)
    - üzüm a4 (çardağa yayılan asma, salkımlar)
    - uzak ağaç (korunun 600 üçgenlik hâli)
    - ufuk ağacı (700 m ötesi ve kesit için 100 üçgen)
    - a1 (tohum) ve a2 (filiz) aşamaları ile üzümün a3 aşaması (kazığa sarılan fidan) eski hâlinde kaldı.
  - **Godot:**
    - `yaprak_kart.gdshader` (alfa kesme, mipmap'te alfa artışı, titreme) ve `kabuk.gdshader` (doku ve normal haritası).
    - `ortak.gdshaderinc` içinde `golge_alma`: yapraklar gölgeyi yarı alır. Sık taçta kartlar birbirini gölgeleyince taç Nur'un arka ışığında kapkara bir silüete dönüyordu.
    - `meyve` malzemesi. Çiçek shader'ının rüzgârı yapraklarla aynı formüle getirildi.
    - `SahneKurucu.coklu(..., parca)`: örnekler ızgara parçalarına bölünür, LOD her parçada ayrı seçilir.
    - `yaprak_*` ve `kabuk_*` malzemeleri adından dokusunu bulur.
    - İnceleme kamerası: `--zb-kamera=model --zb-model=ZB_bitki_koru_agac [--zb-model-aci=30 --zb-model-yukseklik=6 --zb-model-doluluk=0.85]`.
  - **Üçgen bütçesi (sahnede):**

    | Öğe | Önce | Sonra |
    | --- | --- | --- |
    | Korular (286 örnek) | 1,61 milyon | 1,46 milyon |
    | Uzak ağaçlar | 0,34 milyon | 1,09 milyon (1496 dallı, 1904 ufuk ağacı) |
    | Kesit | 0,42 milyon | 0,42 milyon |

    Telefonda ölçülmedi; gerçek cihazda LOD ve görünürlük uzaklıkları ayarlanmalı.
  - **Çekimler (`docs/goruntuler/cennet/`):**
    - `agac_once_sonra.jpg` (koru, sidr, nar, selvi, hurma; üstte önce, altta sonra)
    - `agac_hurma_talh_uzum.jpg`
    - `agac_sahne_once_sonra.jpg` (dikey ufuk ve arsa)
    - `agac_sahne_ori.jpg`
  - **Öğrenilenler:**
    - three.js önizlemesi (`contact.mjs`) ince yaprakçıkları (hurma, üzüm) mipmap'te yok eder; kartlı modeller Godot'ta (`--zb-kamera=model`) değerlendirilmeli.
    - Yaprak kümesi hücreye sığdırılmalı (`_sigdir`). Kenarda kesilen yaprak kartta düz bir çizgi bırakır.
    - Kartlar tacın ortalama rengini düşürür; atlas renkleri eski düz renklerden bir ton açık seçilmeli.
    - Taç içi koyulaşma kabukta daha hafif tutulmalı; yoksa gövde siyah görünür.
- **Canlılık:** Kuşlar ve kelebekler: model fabrikasında sade, parçalı modeller; kanat çırpma Godot'da (K13).

## 3. Planda bekleyen mekân ve mekanik öğeleri
- **Nur tohumu ve bahar açılışı (10. Söz):** Zikirle dikim anında tomurcuk, çiçek ve meyve birlikte açar (animasyon).
- **Açılış ve katlar arası geçiş:** Dış kesitten oyuncunun katına iniş. Hadîd 12: oyuncunun önünde ilerleyen nur izi.
- **Merdivenle kat değiştirme:** Merdiven bulutun içinden bir üst kata çıkar.
- **Arkadaş ve aile bahçeleri (28. Söz):** Beraberlik misali. Farklı katlardaki bahçeler birbirini görür ve ziyaret eder.
- **Firdevs ve nur katı:** Ayrı ve özenli bir çekim. Hacimli ışık, ışıktan ağaç silüetleri, parçacık akışları; Arş tasvir edilmez.

## 4. Sonra
- Arayüz (K7) baştan tasarlanacak.
- Asset listesindeki gece ve mevsim öğelerinin dönüşümü (`mekan-kurgusu.md`, "yeniden düşünülecekler").
- Danışma kurulu soruları (`mekan-kurgusu.md`).
