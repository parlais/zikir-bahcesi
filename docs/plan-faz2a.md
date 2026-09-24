# Faz 2a — Kur'an tasvirlerinden ilham alan cennet mekânı, 4 animasyon stilinde

## Bağlam
Stil karşılaştırmasındaki çarbağ kullanıcıya iyi geldi ama tam istediği mekân değil. Kullanıcı Kur'an'daki cennet tasvirlerinden ilham alan bir his ve mekân istiyor.

Onaylanan mekân fikri şu:
- Uzaktan sonsuz görünen, ışığa doğru yükselen teraslar (dereceler).
- Irmaklar köşklerin altından akıyor, teraslardan çağlayan olarak dökülüyor.
- Oyuncu verimli ama boş bir ovada başlıyor ve bahçesini zikirle dikiyor. Dayanak Tirmizî 3462: toprak verimli ama boş, fidanları zikirdir.

Görsel stil "animasyon stili" olarak ele alınacak. Kullanıcı dördünü de görmek istedi: Disney/Pixar 3D, Ghibli/boyalı, Arcane/fırça darbeli 3D, Sky/Journey/Ori.

Kapsam yalnızca 3D dünya. Arayüz bu fazda yok; sonra baştan ele alınacak.

**Gece ve gündüz revizyonu:** Kullanıcının paylaştığı kaynağa göre cennette gece-gündüz, kış-yaz gibi doğa olayları yoktur (Sorularla İslamiyet; Nisâ 57). Gece-gündüz döngüsü (ve Mücevher'in gece sahnesi) kaldırılır.

Bu, asset listesindeki bazı VFX ve gökyüzü öğeleriyle çelişiyor:
- kar örtüsü
- sonbahar yaprak dökümü
- yıldızlı gece göğü
- şafak gökyüzü
- şimşek
- çiy taneli sabah

Bu fazda bunlara dokunulmaz. `docs/mekan-kurgusu.md` içinde "yeniden düşünülecek" listesine yazılır; kullanıcı ve danışma kuruluyla sonra karar verilir.
- Işık sürekli, yumuşak ve kaynağı belirsizdir (İnsan 13).
- "Sabah akşam rızıkları" (Meryem 62) klasik tefsirde dünya zamanının ölçüsüyle anlatılır. Bu yüzden oyunda zaman karanlıkla değil, yalnızca ışığın tonundaki çok hafif bir değişimle hissettirilebilir. Bu da danışma kuruluna sorulacak.
- Çekimler bu sürekli ışıkta yapılır.
- Kandiller ve fenerler dekor olarak kalır; gece için değil, nur ve güzellik için yanar.

## Mekân kurgusu (ayet → mekân öğesi)
Teyit edilecek dayanaklar `docs/mekan-kurgusu.md` dosyasına tablo olarak yazılır.

| Dayanak | Mekân öğesi |
| --- | --- |
| Âl-i İmrân 133 (genişliği göklerle yer kadar) | Ufuk sonsuz: teraslar ışıklı pusa, aşağısı bulut denizine karışır |
| Tirmizî 3462 | Ön planda oyuncunun verimli, boş arsası: yumuşak toprak, tek bir genç fidan, ilk çiçekler |
| Bakara 25 ve diğerleri (altlarından ırmaklar akan) | Ana ırmak tepeden iner, ovada kıvrılarak akar |
| Zümer 20 (üst üste bina edilmiş köşkler, altlarından ırmaklar) | Suyun üstünde, ayaklar üzerine kurulu, iki üç katlı köşkler; teraslar dereceler halinde yükselir |
| Muhammed 15 (dört ırmak) | Su (turkuaz), süt (inci beyazı), bal (kehribar) ve Ali Ünal'ın açıklamasına göre sarhoşluk vermeyen tertemiz içecek, yani yakut renkli bir şerbet ırmağı (adı ve temsili danışma kuruluyla kesinleşir) |
| Vâkıa 28-30 | Dikensiz sidr, dizi dizi talh (muz), uzayıp giden gölge |
| Rahmân 62-68 | Koyu yeşil iki bahçe, fışkıran iki pınar, hurma ve nar |
| İnsan 13-14 | Yakıcı güneş de dondurucu soğuk da yok: güneş diski görünmez, ışık yumuşak ve kaynağı belirsiz, gece de yok. Gölgeler üzerlerine sarkmış, meyveler eğdirilmiş |
| İnsan 18 | Selsebil pınarı |
| Hicr 47, Gâşiye 13-16 | Karşılıklı sedirler, serilmiş halılar |
| Buhârî-Müslim | İnciden çadırlar: parlak inci kubbe |
| Nisâ 57 | "Ne sıcak ne soğuk, tam kararında gölgelik": her yer yumuşak gölge altında |
| Hicr 45, Mürselât 41 | Bahçeler, gölgeler ve pınar başları: oturma yerleri hep pınarın yanında |
| Rahmân 48 | Çeşit çeşit dallı, sık ağaçlar; sarmaş dolaş koyu yeşillik |
| Rahmân 50, 66; Gâşiye 12; İnsan 6, 18; Mutaffifîn 28 | Akan ve fışkıran pınarlar (Selsebil, Kâfur, Tesnîm) |
| Rahmân 12, 68; Vâkıa 28-29 | Hurma, nar, reyhan, muz; meyveleri kolay toplanan ağaçlar |
| Buhârî, Bed'ü'l-halk 8 | Gölgesinde yüz yıl koşulan ağaç (Tûbâ): ufku kaplayan dev bir ağaç, sahnenin merkez simgesi |
| et-Tâc 5/402 | Gümüş ve altın kerpiç, misk harç, inci ve yakut taşlar: yapılarda almaşık altın ve gümüş tuğla, inci ve yakut süsler |
| Buhârî, Cihad 4 | Yüz derece, her biri gökle yer arası kadar: teraslar arası dikey mesafe çok büyük, üst dereceler ışıklı pusta kaybolur |
| Müslim, Cennet 14-22 | Cennet ehli dolunay ve yıldız gibi ışık saçar: ışık her şeyden hafifçe yayılır, kaynağı belirsizdir |
| İbn Abbas: "isimlerden başka dünyayı andıran hiçbir şey yok"; Secde 17 | Gerçekçi değil, rüya gibi ve bu dünyaya benzemeyen bir temsil. Stil seçiminde bir ölçüt olarak kullanılır |
| Risale-i Nur, 28. Söz: sekiz tabaka, hepsinin damı Arş; koni biçimli dağ misali | **Katlı yapı yalnızca dışarıdan görünür.** Açılış animasyonunda ve katlar arası geçişte kamera uzaktan bakar: iç içe halkalardan oluşan, ışıklı koni biçimli dağ. Oyuncu kendi katına doğru yaklaşıp o kata iner. **Katın içinde ise tepede hiçbir şey yoktur:** her katta ferah, açık ve bütün güzelliğiyle bir gökyüzü görünür. Zirve (en üst kat) tamamen nur ve ışıkla doludur; Arş tasvir edilmez |
| Risale-i Nur, 10. Söz: bahar haşrin ve cennetin numunesi; ağaçlar ipek giydirilmiş, çiçek ve meyveyle süslenmiş | Mevsim yok ama her an bahar dolgunluğu. Zikirle büyüme anı bir "bahar açılışı": tomurcuk, çiçek ve meyve birlikte açar |
| Risale-i Nur, 28. Söz: cennet ehli bir anda yüz bin yerde; dünya kadar yer, yüz bin köşk; güneşin çok aynada görünmesi misali | Oyuncunun arsası küçük bir parsel değil, ufka uzanan bir alan. Su ve cilalı yüzeyler ışığı çoğaltan aynalar gibi. İleride arkadaş bahçesi ziyaretine dayanak |
| Bakara 25 ve 28. Söz: "Bu daha önce rızıklandığımız şeydir" | Meyveler tanıdık biçimde (nar, hurma, üzüm) ama ışıklı ve kusursuz |

### Ali Ünal'ın eserlerinden (kullanıcının yüklediği epub'lar)
*Kur'ân-ı Kerîm ve Açıklamalı Meali*, *Risale-i Nur'da Küllî Kaideler 1-3* ve *Hizmet Rehberi* tarandı. Mekân için öne çıkanlar:

| Kaynak | Mekân / mekanik öğesi |
| --- | --- |
| Rahmân 46-61 ve 62-76, notlar 17-19 | **Katlar birbirinden farklı görünür.** Üstteki iki cennet mukarrebîn içindir: sık yapraklı, çeşit çeşit ağaçlar; akıp giden iki pınar; çift çift meyveler; işlemeli ipek döşekler; kolayca erişilen meyveler. Alttaki iki cennet ashab-ı yemîn içindir: baştanbaşa (koyu) yemyeşil; fışkıran iki pınar; hurma ve nar; otağlar; yeşil yastıklar. İlk kat (oyuncunun başladığı kat) alttaki cennetlerin özelliklerini taşır, yukarı çıktıkça çeşitlilik ve incelik artar |
| Vâkıa 28-31 (Ali Ünal meali) | "Dikensiz, dal bastı kirazlar, dolgun salkımlı muzlar, uzayıp giden gölgeler, çağlayarak akan suların başları." Sidr, kiraz olarak modellenir |
| İnsan 13-21 | Ağaçlar gölge yapar, salkım salkım meyveler ele kadar sarkar; gümüş kaplar ve billur kupalar; yavaş ve sürekli akan Selsebil. 20. ayet "Ne tarafa baksan hayale gelmez nimetler, ihtişam ve büyük bir saltanat görürsün": görsel etki hedefinin kendisi |
| Ra'd 35 | "Yiyecekleri gibi gölgeleri de bitevîdir": gölge hiç kaybolmaz; sürekli ışık ile sürekli gölge birlikte |
| Zümer 20 | "Kat kat birbiri üstüne inşa edilmiş ve altlarından ırmaklar akan yüksek köşkler" |
| Muhammed 15, not 5 | Şarap ırmağı "sarhoşluk ve baş ağrısı vermeyen tertemiz içecek" (başka bir yerde "değişik meyve suları") olarak açıklanır. **Oyunda yakut/nar renkli bir şerbet ırmağı** olarak temsil edilebilir; adı çocuk diline uygun seçilir. Danışma kurulu teyidine kadar sahnede renkli ama adı konmamış bir ırmak olarak durur |
| Muhammed 15, not 6; Vâkıa, not 5 | Nimetler renk, şekil ve isim bakımından dünyadakilere benzer ki insan yabancılık çekmesin; tat ve koku ise âhirete hastır. **Görsel ilke:** tanıdık biçimler, dünyada görülmemiş bir nitelik ve ışık |
| Hadîd 12 | Mü'minlerin nurları önlerinde ve sağlarında parlar: açılış animasyonunda ve katlar arası geçişte oyuncunun önünde ilerleyen bir nur izi |
| Vâkıa 25-26 | "Boş söz işitmezler; işittikleri ancak selâm": ses tasarımı sakin; su, kuş, rüzgâr |
| Küllî Kaideler 1 | "İman kalbde bir tûbâ-i Cennet çekirdeği taşır; âhirette mü'minin cennetini gölgelendirecek bir tûbâ ağacı olarak ortaya çıkar." **Tevhidle büyüyen Tûbâ mekaniğinin doğrudan dayanağı.** Oyuncunun Tûbâ'sı arsasında ışıklı bir çekirdekle başlar |
| Küllî Kaideler 2 | Her amel misal âleminde kök, gövde, dal, çiçek ve meyveleriyle bir ağaç olur. Kur'ân'ın her harfi on sevap, on cennet meyvesidir ve Kur'ân nurânî bir Tûbâ olur. **Sure okumanın meyve vermesine dayanak** |
| Küllî Kaideler 1 | Bahçe sahibinin her ürünün numunesini bahçesine dikmesi gibi, cennet mü'minin makbul amellerini içerir. **Zikir → item eşleşmesinin, yani oyunun temel fikrinin dayanağı** |
| Küllî Kaideler 1 ve 3 | Cennet nurâniyetiyle her tarafa yayılmıştır, güneşin ışığıyla yeri kuşatması gibi; yıldız kandillerine nur veren daimî merkez cennettir. **Işık kaynaksız ve her yerden gelir; en üst kat nurun kaynağı olarak parlar** |
| Küllî Kaideler 2 | Yeryüzü genişletilip "başka bir arz" olacak ve cennet orada kurulacak (Zümer 74, İbrahim 48). **Mekân tanıdık bir yeryüzü dili konuşur (ova, ırmak, dağ) ama genişletilmiş ve yüceltilmiştir** |
| Küllî Kaideler 2 | Kâinat bir cennet bahçesi gibidir; galaksiler ve güneşler bu bahçenin ağaçları ve çiçekleridir. **Açılış animasyonu:** koni-dağ, ışıklı ve kozmik bir bahçe boşluğunda durur |
| Hizmet Rehberi | "Sizler Cennet benzeri bir baharda geleceksiniz; şimdi ekilen nur tohumları çiçek açacaktır." **Tohumlar ışıklı:** her dikim bir "nur tohumu" parıltısıyla başlar |

## Uygulama

### 1. Modeller — `tools/model_factory/models/cennet.py` (yeni)
Mevcut `mf/` kütüphanesi kullanılır: `lathe`, `tube`, `blade`, `band`, `kure_normal`, `smooth`, `weight`.

- **`ZB_dunya_cennet`:** Ana arazi.
  - Bir katın içi (ilk kat): geniş ova ve oyuncu arsası, ırmaklar, köşkler, pınarlar, koruluklar. Ufuk açık; üstte hiçbir yapı yok, yalnızca geniş ve güzel gökyüzü var. Uzakta, aynı kattaki tepeler ve ırmak yatakları görünür.
- **`ZB_dunya_derece_koni`:** Katlı yapının dış görünümü; yalnızca açılış ve geçiş çekimleri için. Zirvesi ışığa açılan koni biçimli dağ ve iç içe 7-8 halka kat. Her halkada küçük ölçekte bahçe, ırmak ve çağlayan izleri var. Bu çekimlerde katın içindeki gökyüzü görünmez; dağ, bulut denizinin ve ışıklı bir boşluğun içinde durur.
- **En üst kat (nur katı):** Bu fazda yalnızca dış görünümden, parlayan zirve olarak gösterilir. Nur katının içi ayrı bir kalite işi: hacimli ışık hüzmeleri, ışıktan yapılmış ağaç ve çiçek siluetleri, parçacık akışları, çok katmanlı bloom. Sonraki fazda ayrı ve özenli bir çekim olarak planlanır.
  - Irmak yatakları.
  - Malzemeler: `zemin`, `tas`, `toprak_arsa`.
- **`ZB_dunya_irmaklar`:** Su yüzeyleri. Malzeme adları `su`, `sut`, `bal` ve `serbet` (yakut) olur; aynı su shader'ı farklı renklerle kullanılır.
- **Oyuncu arsası:** Toprağın ortasında ışıklı bir Tûbâ çekirdeği (Küllî Kaideler 1). İlk fidanlar "nur tohumu" parıltısıyla yükselir.
- **İlk katın karakteri** (Rahmân 62-76): koyu, baştanbaşa yeşil; fışkıran pınarlar; hurma ve nar; otağlar ve yeşil yastıklı sedirler. Uzakta görünen üst katların silüetinde daha çeşitli ağaçlar ve akan pınarlar sezilir.
- **`ZB_dunya_selaleler`:** Teraslar arası çağlayan şeritleri, malzeme `selale`.
- **`ZB_yapi_su_kosku`:** Ayaklar üzerinde, katlı köşk. Mevcut `yapilar.py` içindeki `kubbe`, `almasik_kemer`, `kemer_aynasi` kullanılır; kubbeler yumuşak gölgeli ve daha çok segmentli yapılır.
- **`ZB_yapi_inci_cadir`:** İnci beyazı, yumuşak gölgeli kubbe çadır.
- **`ZB_bitki_tuba_dev`:** Ufukta, üst derecelerin ardında yükselen dev ağaç. Gövdesi bulutlara girer, tacı gökyüzünün bir bölümünü kaplar.
- **Köşk malzemesi:** Almaşık altın ve gümüş tuğla deseni. Yüzey shader'ına `tugla` parametresi eklenir; inci ve yakut süsler eklenir.
- **`ZB_obje_sedir_hali`:** Karşılıklı sedirler ve serilmiş halı.
- **Yeni bitkiler:** `ZB_bitki_sidr`, `ZB_bitki_talh` (muz), `ZB_bitki_asma` (üzüm çardağı). Mevcut selvi, nar ve hurma da yeniden kullanılır; hurmaya küre normalleri eklenir.
- **Yerleşim dosyası:** `game/data/dunya_cennet.json`. İçinde bitkiler, köşkler, pınarlar, sedirler ve kamera noktaları olur. `sahne.py` içindeki `yerlesim_yaz` deseni izlenir; `build_all.py` bunu da yazar.

### 2. Ortak sahne kurucusu (yeniden kullanım)
- `game/scenes/stil/stil_sahnesi.gd` içindeki malzeme eşleme (`_malzeme`, `_boya`), MultiMesh (`_bitki_mesh`, `_coklu`), parçacık (`_parcacik`) ve ortam (`_ortam_kur`) kodu `game/scenes/ortak/sahne_kurucu.gd` içine taşınır (`class_name SahneKurucu`).
- `stil_sahnesi.gd` bunu kullanacak şekilde incelir; eski çarbağ karşılaştırması aynen yeniden çekilebilir kalır.

### 3. Cennet sahnesi — `game/scenes/dunya/cennet_sahnesi.gd` ve `.tscn` (yeni)
- Yerleşim JSON'undan kurulur.
- Parçacıklar: çağlayan köpüğü, pınar fışkırmaları, nur zerreleri, uçuşan kuşlar ve kelebekler (sade kanat çırpan billboard'lar).
- Gökyüzü: `gok.gdshader` kullanılır. Güneş diski kapalı; ışık terasların ardından gelen yumuşak bir parlama olarak verilir.
- Kamera noktaları:
  - `ufuk`: kattan ferah bakış; ırmak, köşkler ve açık gökyüzü
  - `arsa`: oyuncu arsasına yakın plan; arkada ırmak ve köşk
  - `derece`: katlı koni-dağın dıştan görünümü (açılış animasyonu karesi)

### 4. Animasyon stilleri — `game/scenes/dunya/animasyon_stilleri.gd` (yeni)
Profil şeması `StilProfilleri` ile aynıdır. Ek olarak her stilin bir `filtre` bölümü olur.

- **Pixar:** Yumuşak ve yuvarlak ışık, zengin küresel aydınlatma (SDFGI), yapraklardan geçen ışık, doygun ama temiz renkler, yumuşak gölgeler. Filtre yok.
- **Ghibli:** Toon geçişi, suluboya kâğıdı dokusu, elle boyanmış renk lekeleri, kabarık kümülüs bulutları. Hafif Kuwahara filtresi (boya fırçası etkisi).
- **Arcane:** Nesnelere yapışık fırça darbesi dokusu, gölgelerde renk kayması (mor/turkuaz), güçlü kenar ışığı, derinlikten ince kontur. Güçlü Kuwahara.
- **Sky/Ori:** Işıklı, sade, rüya gibi. Güçlü bloom ve hacimli sis, katmanlı silüetler, parlayan su ve çiçekler, kısık doygunlukta renk geçişi.

Yeni shader'lar:
- `shader/resim_filtresi.gdshader`: Kameraya bağlı tam ekran quad. Ekran ve derinlik dokusundan Kuwahara, kontur (derinlik ve normal farkı), kâğıt grenini ve renk düzeltmeyi yapar; her biri parametreyle açılıp kapanır.
- `shader/selale.gdshader`: Dünya koordinatında aşağı akan gürültü ve köpük.
- `ortak.gdshaderinc` içine `firca` parametresi: üç eksenli (triplanar) fırça dokusu gürültüsü.

Çalıştırma: `--zb-anim=pixar|ghibli|arcane|sky` ve `--zb-kamera=ufuk|arsa`.

### 5. Çıktılar
- `docs/goruntuler/cennet/`: 4 stil × 3 kamera (`ufuk`, `arsa`, `derece`; 1600×900) ve karşılaştırma panoları. Kullanıcıya gönderilir.
- `docs/mekan-kurgusu.md` (yeni): ayet tablosu, mekân açıklaması ve danışma kuruluna sorulacaklar (şarap ırmağı; köşk, çadır ve Kevser gibi gerçek cennet öğelerinin temsili).
- `docs/kararlar.md` dosyasına eklenecek kararlar:
  - K4: Mekân Kur'an tasvirlerinden ilhamlı, yükselen teraslar
  - K5: Cennette gece-gündüz ve mevsim yok: sürekli yumuşak ışık; önceki "gerçek saatle gece-gündüz" kararı iptal. Işık tonunda hafif sabah-akşam farkı ve asset listesindeki mevsim ve gece öğeleri danışma kuruluna sorulacak
  - K6: Arayüz ayrı bir aşamada baştan tasarlanacak

## Doğrulama
- Testler geçmeli: `godot --headless --path game -s res://tests/run_tests.gd` (şu an 34 test).
- `python3 tools/model_factory/build_all.py` üçgen sınırı hatası vermeden bitmeli.
- Eski karşılaştırma (`stil_sahnesi.tscn --zb-stil=nur`) yeniden düzenlemeden sonra hatasız render etmeli.
- Her çekim lavapipe ile Forward+ renderer'da alınır ve görsel olarak kendim incelerim. Önce yarım çözünürlükte hızlı denemelerle iterasyon yapılır, sonra tam çözünürlükte son çekimler alınır. Kontrol edeceklerim:
  - ufuk sonsuz görünüyor mu
  - ırmak köşkün altından akıyor mu
  - çağlayanlar okunuyor mu
  - arsa boş ama verimli görünüyor mu
  - dört stil birbirinden net ayrışıyor mu
- Her adım ayrı commit olarak `claude/busy-allen-p76wgo` dalına gönderilir.
