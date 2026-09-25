# Zikir Bahçesi — Kararlar

Raporun "Birlikte karar vermemiz gereken açık sorular" bölümüne verilen cevaplar ve sonradan yapılan revizyonlar burada tutulur. Her karar tarihlidir; değişirse eskisinin üstü çizilmez, altına yenisi yazılır.

## K1 — Oyun motoru: Godot 4 (2026-09-24)
- Sürüm: Godot 4.7.2-stable.
- Gerekçe: Sahneler ve scriptler metin tabanlıdır, bu da yapay zekâ destekli tek kişilik geliştirmeye uygundur. Açık kaynaktır ve ücretsizdir. Aynı projeden mobil ve web sürümü çıkar.
- Açık soru #2 kapandı.

## K2 — 3D modeller: kendi model fabrikamız (2026-09-24)
- Tripo ve diğer AI 3D servisleri kullanılmaz. Modeller depodaki prosedürel Python kodunda üretilir (`tools/model_factory/`) ve `.glb` olarak dışa aktarılır.
- Asset listesinin H bölümündeki kredi ve plan hesabı kaldırıldı.
- Kazanç:
  - Lisans riski yok, bütün modeller projenin malıdır.
  - Her model yeniden üretilebilir; stil tek paletten yönetilir.
  - Aşamalar (tohum → olgun) aynı fonksiyondan gelir.
- Bedel: Stil bilinçli olarak sade low-poly'dir. En zor kalem canlılardır, onlar en sona bırakıldı. Gerekirse hero modeller ileride elle iyileştirilebilir.

## K3 — Hedef kitle: 7-12 yaş + aile (2026-09-24)
- Birincil kitle 7-12 yaş. Tasarım tonu, dil düzeyi ve güvenlik varsayılanları bu yaşa göre kurulur.
- Ebeveyn de kendi bahçesiyle katılır. Ebcedi 500 ve üzeri isimler aile hedefi olarak ortak yürür.
- Çocuk varsayılanları herkese uygulanır:
  - reklam yok
  - ses cihazdan çıkmaz
  - üçüncü parti analitik ve reklam SDK'sı yok
  - bireysel sıralama yok
- 7 yaş her metni okuyamaz; her kart ikon ve sesli anlatımla desteklenecek. Sesli anlatım sonraki fazda gelecek.
- Açık soru #1 kapandı.

## Varsayılan kabul edilenler (değiştirilebilir)
- **Ebced modu:** Varsayılan açıktır, ayarlardan "serbest sayı" moduna geçilir (Açık soru #5). Serbest modda esma item'ları sabit 33'te açılır.
- **Rekabet:** Bireysel sıralama yoktur (Açık soru #4).
- **Müzik:** Yoktur, yalnızca doğa ambiyansı çalar (Rapor §7).

## Uygulamada verilen tasarım kararları (onayınızı bekler)
Asset listesinin açık bıraktığı yerler için seçilen değerler aşağıda. Hepsi `tools/content/build_content.py` başındaki sabitlerde durur ve tek satırla değiştirilebilir.

- **Çiçek eşikleri:** Çiçekler 1'de tohum, 33'te gonca, 100'de açmış olur. Kılavuz yalnızca ağaçlar için sayı veriyordu (1, 10, 33, 100).
- **Esma ile büyüyen bitkiler:** Eşikler ebcedin oranıdır; ebced tamamlanınca bitki olgunlaşır. Örneğin servi (Vâhid, 19) 1, 2, 7 ve 19'da büyür; lale (66) 1, 22 ve 66'da.
- **Tûbâ:** Ömür boyu toplam tevhid sayısıyla 5 aşamada büyür: 1, 33, 100, 1000, 10000.
- **Sure ağaçları (Tîn, Rahmân, Vâkıa):** Okuma sayısıyla 1, 3, 7 ve 11'de büyür.
- **Sayı belirtilmemiş tetikleyiciler:**
  - kısa zikirler 33'te tamamlanır
  - dualar, sureler ve günlük sözler 1 kez yeterlidir
  - olaya bağlı sözler de 1 kez söylenir: oturum açılışındaki Bismillah, arkadaşın bahçesinde verilen selam, hediye alınca söylenen "Cezâkallah"
- **Tekrar:** Bir bitki olgunlaşınca aynı zikirle yenisi dikilir; item'lar her tamamlamada envantere bir tane daha eklenir (gül balı için 100 gül gibi tarifler bunu gerektiriyor). "İkinci item" notlu olanlar sırayla gelir: 1. tamamlama kandil, 2. tamamlama fanus, 3. tamamlama yine kandil.
- **Tarifler:** Bahçede duran hiçbir şey harcanmaz (bitki, yapı, kovan, şadırvan). Yalnızca malzemeler tüketilir: inci, mercan, sedef, ipek kozası, un çuvalı, ekmek, zeytinyağı.
- **Kaynaklar:**
  - her tevhid havayı, her elhamdülillah ve istiğfar suyu artırır
  - Nûr ışığı, Rezzâk rızkı artırır
  - kaynaklar saatte 1 puan solar ama 20'nin altına inmez
  - bahçenin renk doygunluğu havaya bağlıdır
- **Seri:** Her 7 günde 1 dondurma hakkı kazanılır, en fazla 3 birikir. Kaçan gün dondurmayla kapanır. Dondurma yetmezse seri sessizce yeniden başlar; en uzun seri kaybolmaz.
- **Ses tanıma bekleme süresi:** Başka bir sözün başı olan söz 1,2 saniye bekletilir. Zamanda çakışan iki algılamadan uzun olan sayılır.

## K4 — Mekân: Kur'an tasvirlerinden ilhamlı, katlı cennet (2026-09-24)
- İlk dilimdeki küçük ada ve stil karşılaştırmasındaki 60×60 m çarbağ, istenen mekân değildi. Çarbağ "fena değil" bulundu ama his eksikti.
- Yeni mekân: Risale-i Nur'daki koni-dağ misaline göre iç içe katlar (dereceler).
  - Katlı yapı yalnızca dışarıdan görünür (açılış animasyonu, katlar arası geçiş).
  - Katın içinde tepede bir şey yoktur; ferah, güzel bir gökyüzü vardır.
  - En üst kat nurla doludur ve ayrıca özenle yapılacak.
- Oyuncu ilk katta verimli, boş bir arsada başlar; zikirle doldurur.
- Ayrıntılar ve dayanaklar: `docs/mekan-kurgusu.md`.

## K5 — Cennette gece-gündüz ve mevsim yok (2026-09-24)
- Işık sürekli, yumuşak ve kaynaksızdır; gölge süreklidir. Güneş diski görünmez.
- "Gerçek saatle gece-gündüz döngüsü" fikri ve Mücevher stilinin gece sahnesi **iptal edildi**.
- Işık tonunda hafif bir sabah-akşam farkı ve asset listesindeki mevsim ve gece öğeleri danışma kuruluna sorulacak.

## K6 — Görsel stil: animasyon stili olarak seçilecek (2026-09-24)
- Kullanıcı karar veremedi. Dört animasyon stilinin hepsini yeni mekânda görmek istiyor: Disney/Pixar 3D, Ghibli/boyalı, Arcane/fırça darbeli 3D, Sky/Journey/Ori.
- Çizim tarzı (yumuşak / toon / ara) da henüz seçilmedi.
- İlke: gerçekçi değil, rüya gibi ve dünyaya benzemeyen bir temsil. Biçimler tanıdık, nitelik ve ışık dünya dışı.

## K7 — Arayüz sonra, ayrı bir aşamada (2026-09-24)
- Şu an yalnızca 3D dünya konuşuluyor.
- Mevcut arayüz ve stil karşılaştırmasındaki arayüz önizlemesi kullanıcıyı tatmin etmiyor; ayrı bir aşamada baştan tasarlanacak.

## K8 — Kalite hedefi: "ultra" (2026-09-24)
- Kullanıcı oyuncuların görsel olarak çok etkilenmesini istiyor.
- Forward+ renderer (SDFGI, hacimli sis, SSR, SSAO, parlama) kullanılacak; hedef orta-üst seviye telefonlar.
- Canlılar ve bazı kilit modeller için AI 3D aracı ya da hazır paketlerle karma üretim önerildi; kullanıcı henüz cevap vermedi (açık soru).

## K9 — Beşinci stil: yağlı boya; mekân kurgusu değişecek (2026-09-24)
- Pixar taslakları (`docs/goruntuler/cennet/taslak_pixar_*.png`) istenen şey değildi.
- Kullanıcı bir video promptundaki "yaşayan yağlı boya" stilini beğendi. Bu stil beşinci stil olarak dört animasyon stiline eklenir.
- Promptten yalnızca yağlı boya estetiği alınır:
  - yüzeylerde ve gökte görünen fırça dokusu
  - ışıklı, zengin, klasik tablo renkleri
  - ince gren
- Gece, lamba ışığı ve karanlık chiaroscuro istenmiyor; K5 (gece yok) geçerli.
- Mekân kurgusu da değişecek (ova, ırmaklar, su köşkü, ufukta dereceler, Tûbâ). Kullanıcının tarifi bekleniyor.

## K10 — Cennet: uzanıp giden 8 yatay tabaka (2026-09-24)
- K4'teki koni-dağ görünümünün yerine geçer. 28. Söz'deki koni, güneşi görme ve birbirine geçme örneği için verilmiş bir dünya misalidir; cennet dağ gibi sınırlı bir yer değildir.
- **Tabakalar:**
  - Cennet 8 yatay tabakadır ve her tabaka uçsuz bucaksızdır.
  - En üstte Firdevs vardır, ortasında dört ırmağın kaynağı bulunur. Firdevs'in üstü her şeyi kuşatan ışıktır; Arş tasvir edilmez.
- **İçeriden:**
  - Her katta ufuk açıktır.
  - Göğe bakınca üst tabaka görünmez, atmosfer tabakaları gibi.
  - Aynı ışık her kata ulaşır (K5: güneş diski yok).
- **Dışarıdan:**
  - Açılışta ve katlar arası geçişte, Dünya'nın katman resimleri gibi bir kesit görünür.
  - Her tabakanın zemini ve göğü bant bant görünür, yanları ışığa karışır.
- **Merdivenler:** Katlar arasında çiçek ve sarmaşıkla kaplı taş merdivenler, kıvrılarak bulutların içinden ışığa yükselir. Alttan bakınca bulutta kaybolur. Kullanıcının referans görseli bu havadadır.
- **Firdevs'in yeri:** Hadisteki "evsat" hem "orta" hem "en seçkin" anlamına gelir. Firdevs en üst kat olarak konur, "ortası" da dört ırmağın kaynağıyla karşılanır. Danışma kuruluna sorulacak.
- Kavram eskizleri:
  - `docs/goruntuler/cennet/eskiz_katmanlar.png`
  - `docs/goruntuler/cennet/eskiz_kure_tabaka.png`
- Kullanıcının ek kararları (aynı gün):
  - İlk katın içinden bakınca dört ırmak gökten, bulutların içinden inen çağlayanlarla başlar; üst tabakanın kendisi görünmez.
  - Ufuktaki dev Tûbâ kaldırıldı. Oyuncunun Tûbâ'sı arsasında çekirdekten büyür.
  - İlk ara durak yağlı boya stilinde çekilir.

## K11 — Stil: yağlı boya filtresi ve Pixar tutmadı; Nur ve Sky/Ori deneniyor (2026-09-25)
- Kullanıcı yağlı boya taslaklarında "yağlı boya hissi hiç olmamış" dedi; Pixar'ı da sevmedi.
- İlk stil karşılaştırmasındaki Nur ile Sky/Journey/Ori'yi yeni mekânda görmek istedi.
- İkisi de yeni kurguya (K10) göre profil olarak eklendi: `animasyon_stilleri.gd` içinde `nur` ve `sky`. Resim filtresi yok.
- Nur'un eski hâlindeki güneş diski K5 gereği kaldırıldı; ışık arkadan ve alçaktan gelen altın bir parıltıdır.
- Çekimler:
  - `docs/goruntuler/cennet/taslak_{nur,ori}_{ufuk,arsa,kesit}.png`
  - `docs/goruntuler/cennet/karsilastirma_nur_ori.jpg`
- Eski mekân: Çarbağ sahnesi (`scenes/stil/`) depoda duruyor ve yeniden çekilebilir. Pixar taslağındaki koni-dağ, derece duvarları ve dev Tûbâ K10 ile koddan kaldırıldı; git geçmişinde duruyor.

## K12 — Işık: aynı mekânda Nur ile Ori arasında ara sıra değişen ışık (2026-09-25)
- Kullanıcı iki stili de sevdi. Altın ışık (Nur) güzel bir his veriyor; Ori'deki beyaz, nurani parıltılar da.
- Mekân aynı kalır; ışık ara sıra Nur'un altın ışığından Ori'nin beyaz-turkuaz nurani ışığına, sonra geri döner.
- Bu bir gece-gündüz döngüsü değildir (K5): karanlık yok, güneş diski yok, yalnızca ışığın tonu ve havası değişir.
- Suların, çiçeklerin ve nurun kendi ışığıyla parlaması (Ori'deki gibi) iki ışıkta da kalır.
- Açık konular:
  - Geçişin neye bağlı olacağı (zaman, zikir, olay, oyuncunun seçimi) kullanıcıyla belirlenecek.
  - Danışma kuruluna sorulan "ışık tonunda hafif sabah-akşam farkı" sorusu (Meryem 62) bu kararla doğrudan ilgili.
- Pixar ve yağlı boya profilleri ile `resim_filtresi.gdshader` kodda duruyor ama kullanılmıyor (K9, K11).

## K13 — Işık geçişi zikir ve olaylarla; sıradaki iş kalite; canlılar model fabrikasında (2026-09-25)
- Kullanıcı Faz 2b planını onayladı. Sıra:
  1. Nur ↔ Ori ışık geçişi
  2. kalite
  3. mekanikler
  4. arayüz (K7) sonra
- **Tetikleyici:** zikir ve olay (K12'deki açık konu kapandı).
  - Işığın zemini Nur'dur (altın). Bir zikir, dua ya da sure tamamlanınca ya da bir esma tamamlanınca ışık yavaşça Ori'nin beyaz-turkuaz nurani ışığına geçer. Bir süre öyle kalır, sonra yavaşça Nur'a döner. Zikir sürdükçe Ori'de kalır.
  - Olaylar da aynı geçişi başlatır: Tûbâ'nın aşama atlaması, kat değiştirme, arkadaş bahçesini ziyaret, açılış.
  - Işık gerçek saate ya da akan zamana bağlanmaz; değişim sabah-akşam gibi okunmasın (K5). Meryem 62 sorusu danışma kurulunda duruyor.
  - Işık çapraz geçer: Nur'un ışığı, gölgeleri ve gökteki parıltısı yerinde söner; Ori'ninkiler kendi yerinde belirir. Gölgeler dönmez, güneş hareket ediyormuş gibi görünmez. İki uç da onaylanan hâliyle kalır: Nur'un altın arka ışığı, Ori'nin ırmaktaki beyaz parıltısı.
  - Süreler ilk tahmindir ve tek yerden ayarlanır (`game/scenes/dunya/isik_gecisi.gd`).
- **Canlılar:** Kuş ve kelebek gibi canlılar model fabrikasında sade, parçalı modeller olarak üretilir; kanat çırpma Godot'da yapılır. K8'deki "AI 3D aracı ya da karma üretim" sorusu canlılar için kapandı; K2 geçerli.


## K14 — Geri bildirim: ışık geçişi ve çağlayanlar tamam; genel yön daha detaylı ve gerçekçi (2026-09-25)
- Kullanıcı Faz 2b'nin ilk sonuçlarına baktı: "Şu anki durum fena olmamış."
- **Işık geçişi:** Süreler "gayet iyi"; onaylandı.
  - Nur'dan Ori'ye 6 sn'de çıkış, Ori'den Nur'a 40 sn'de dönüş.
  - Ori'de kalış: tamamlanan zikir 40 sn, esma 60 sn, Tûbâ aşaması 90 sn, kat geçişi ve ziyaret 30 sn, açılış 20 sn.
- **Çağlayanlar:** "İyi gibi sanki." Kabul edildi; genel ayrıntı artışından onlar da payını alır.
- **Genel yön:** "Her şeyin daha detaylı ve gerçekçi olmasını istiyorum."
  - Sıradaki kalite işlerinin ölçütü budur: kesit, ağaç ve köşk modelleri, kuşlar ve kelebekler.
  - Açık konu (yeni oturumda kullanıcıya sorulacak): "Gerçekçi" ne kadar gerçekçi? K6'daki ilke "gerçekçi değil, rüya gibi; biçimler tanıdık, nitelik ve ışık dünya dışı" idi. Yüksek ayrıntı ve inandırıcılık mı isteniyor, yoksa fotogerçekçi dokular ve malzemeler mi?
  - Açık konu: Gerçekçilik için CC0 doku kütüphaneleri (Poly Haven, ambientCG; lisans riski yok) kullanılabilir mi, yoksa dokular da prosedürel mi üretilsin (K2)?

## K15 — Gerçekçilik ölçütü: biçim ve malzeme gerçekçi, ışık rüya gibi; dokular CC0; ilk iş ağaçlar (2026-09-25)
K14'teki iki açık soru ve iş sırası kullanıcıya soruldu.
- **Gerçekçilik ve K6 dengesi:** Biçim, ayrıntı ve malzeme inandırıcı olur.
  - Ağaçlar gerçekten dallanır ve binlerce yaprak taşır.
  - Taşta ve mermerde doku, yapılarda oyma ve çini bulunur.
  - Işık, renk ve parıltı Nur ile Ori'deki gibi dünya dışı kalır.
  - K6'daki ilke korunur: biçimler tanıdık, nitelik ve ışık dünya dışı. Fotogerçekçilik hedeflenmez.
- **Dokular (karma):**
  - Modeller model fabrikasında üretilmeye devam eder (K2 geçerli).
  - Yüzey dokuları CC0 kütüphanelerinden (Poly Haven, ambientCG) gelebilir: ağaç kabuğu, taş, mermer, toprak. Cennet paletine göre renklendirilir.
  - CC0 3D modeller kullanılmaz.
  - Bulut ortamının ağ politikası bu siteleri engelliyor; kullanıcının izin vermesi gerekir. İzin gelene kadar dokular prosedürel üretilir.
- **Sıra:** Önce ağaçlar gelir. Ekranda en çok görünen ve "lolipop" hissini en çok veren öğe ağaçlardır; iyileşmeleri ufuk, arsa ve kesit çekimlerini birlikte yükseltir. Sonra kesit, köşk ve çadır, kuşlar ve kelebekler gelir.
