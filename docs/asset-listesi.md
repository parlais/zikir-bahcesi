# Zikir Bahçesi — Ana Asset Listesi

2026-09-21 · @Someone

## Okuma kılavuzu

Bu liste 148 asset ve 13 tarif ürünü içerir. Her biri mikrofona söylenebilen bir zikir, esma, dua veya sureyle tetiklenir. Namaz, oruç ve ahlaki amellere dayanan karşılıklar ölçülemediği için listede yoktur.

- **Adet kuralı:** Esma item'larında eşik, ismin ebced değeridir. Ebcedi 500 ve üzeri olan isimler aile veya grup hedefidir.
- **Aşama kuralı:** Ağaçlar 4 aşamalıdır: 1 tohum, 10 filiz, 33 fidan, 100 olgun. Çiçekler 3 aşamalıdır: tohum, gonca, açmış.
- **Tekrar kuralı:** "×100" gibi bir sayı her 100'de yeniden verilir (her 100 istiğfarda bir nisan yağmuru). "Toplamı 100 (bir kez)" ömür boyu toplam sayıdır: sayaç eşiğe ulaşınca asset bir kez verilir, bir daha verilmez (dört ırmak). Tûbâ da ömür boyu toplamla büyür ve bir kez olgunlaşır.
- **Dayanak kodu:** N = nass (ayet veya hadis), G = gelenek, A = ismin anlamı. Bu sütun item kartındaki "Neden bu?" metninin kaynağıdır.
- **Öncelik:** MVP ilk sürüm, v2 ilk büyük güncelleme, v3 sonrası.
- **Sınırlar:** İnsan, melek ve peygamber tasviri yoktur. Allah lafzı ve esmalar yere konan veya üzerine basılan objelerde yer almaz.

| Tip kodu | Anlamı | Üretim yöntemi |
| --- | --- | --- |
| 3D | Statik model | Model fabrikası (`tools/model_factory`) |
| 3D-A | Aşamalı model (büyüme) | Model fabrikası, aşama başına bir `.glb` |
| Rig | Parçalı ve animasyonlu canlı | Model fabrikası (parçalı hiyerarşi) + Godot AnimationPlayer |
| VFX | Parçacık veya shader efekti | Godot içinde |
| Sky | Gökyüzü veya arka plan katmanı | Godot içinde |
| UI | Kart, ikon veya arayüz öğesi | Godot içinde |

## A. Atmosfer, VFX ve gökyüzü

Bu 19 öğe model fabrikası gerektirmez; motor içinde shader, parçacık ve gökyüzü katmanı olarak üretilir.

| Asset | Tetikleyici | Dayanak | Tip | Öncelik |
| --- | --- | --- | --- | --- |
| Sabâ yeli, açılan gökyüzü, dağılan sis | La ilahe illallah (sürekli) | A: tevhid nefes gibi temel ihtiyaç | VFX | MVP |
| Nisan yağmuru | Estağfirullah ×100 | N: Nuh 10-12 | VFX | MVP |
| Kandil ışığı, nur hüzmesi | Ya Nûr (256) | N: Nur 35 | VFX | MVP |
| Gül kokusu parçacıkları | Salavat, 10 üst üste | G: gül ve Hz. Peygamber | VFX | MVP |
| Su yüzeyi (ırmak, havuz, dere) | Su yapılarıyla birlikte gelir | N: altlarından ırmaklar akan bahçeler | VFX | MVP |
| Gökkuşağı | Seyyidü'l-istiğfar | A: yağmurdan sonra müjde | VFX | v2 |
| Rahmet bulutu | Ya Rahmân (298) | N: A'râf 57, rahmetin önünde müjdeci rüzgârlar | VFX | v2 |
| Bahar patlaması: tüm bahçe çiçek açar | Ya Bâis (573, grup) | N: Hac 5-6, ölü toprağın dirilişi | VFX | v2 |
| Gece koruma kubbesi | Âyetü'l-Kürsî | N: Buhârî, yatarken okuyan korunur | VFX | v2 |
| Şafak gökyüzü | Felak suresi | N: Felak 1, sabahın Rabbi | Sky | v2 |
| Yıldızlı gece göğü | Ya Kayyûm (156) | G: Risale-i Nur, 30. Lem'a | Sky | v2 |
| Deniz ufku (arka plan) | Ya Vâsi' (137) | A: genişlik | Sky | v2 |
| Çiy taneli sabah | Ya Gafûr (1286, grup) | A: her sabah tazelenme | VFX | v3 |
| Kar örtüsü (kış) | Ya Gaffâr (1281, grup) | A: gafr, örtmek demektir | VFX | v3 |
| Sonbahar yaprak dökümü | Ya Kâbıd (903, grup) | A: daraltan | VFX | v3 |
| Parlak güneşli gün | Ya Zâhir (1106, grup) | A: apaçık olan | Sky | v3 |
| Karlı dağ silüeti (arka plan) | Ya Mütekebbir (662, grup) | A: azamet; Nebe 7 | Sky | v3 |
| Şimşek ve gök gürültüsü | Ya Muktedir (744, grup) | N: Ra'd 13, gök gürültüsü hamd ile tesbih eder | VFX | v3 |
| Gökyüzü sureleri: kuşluk ışığı, ay, yıldız | Duhâ, Kamer, Necm sureleri | N | Sky | v3 |

## B. Bitkiler

Bu 28 satır 31 model eder (süs çiçekleri seti 4 modeldir). Tûbâ 5, diğer ağaçlar 4, çiçekler 3 aşamalıdır.

| Asset | Tetikleyici | Dayanak | Tip | Öncelik |
| --- | --- | --- | --- | --- |
| Tûbâ (bahçenin merkez ağacı) | Toplam La ilahe illallah sayısıyla büyür | N: hadis, gölgesi yüz yıllık yol; sembolik temsil | 3D-A | MVP |
| Hurma ağacı | Sübhanallahi'l-azîm ve bihamdihi | N: Tirmizî 3464 | 3D-A | MVP |
| Çınar | Allahu Ekber | G: azamet, Osman Gazi'nin rüyası | 3D-A | MVP |
| Servi | Ya Vâhid (19) | G: elif gibi dimdik, vahdet sembolü | 3D-A | MVP |
| Üzüm asması ve çardak | Elhamdülillah | N: Nebe 32; hamd mizanı doldurur | 3D-A | MVP |
| Kırmızı gül | Salavat | G: gül ve Hz. Peygamber | 3D-A | MVP |
| Beyaz gül | Cuma günü salavat | G; Cuma salavatı teşviki Ebû Dâvûd'da | 3D-A | MVP |
| Lale | Allah (66) | G: lale ile Allah lafzının ebcedi aynı | 3D-A | MVP |
| Bahar dalı (solmuş bitkiyi diriltir) | Ya Muhyî (68) | N: Rum 50 | 3D-A | MVP |
| Çimen halısı (zemin shader'ı) | Ya Bâsıt (72) | A: yayıp genişleten | VFX | MVP |
| Zeytin ağacı | Tîn suresi | N: Tîn 1; Nur 35 | 3D-A | v2 |
| İncir ağacı | Tîn suresi | N: Tîn 1 | 3D-A | v2 |
| Sidr ağacı | Ya Selâm (131), ikinci item | N: Vâkıa 28 | 3D-A | v2 |
| Toros sediri | Ya Kebîr (232) | A: büyüklük | 3D-A | v2 |
| Defne | Ya Bâkî (113) | A: her dem yeşil | 3D-A | v2 |
| Tefriciye gülü (altın sarısı, nadir) | Salât-ı Tefriciye 4444 (grup) | G: toplu okuma geleneği | 3D-A | v2 |
| Kardelen | Ya Mukaddim (184) | A: öne alan; bahardan önce açar | 3D-A | v2 |
| Süs çiçekleri seti: karanfil, sümbül, nergis, zambak | Ya Cemîl (83, 99 dışı) | N: Müslim, Allah güzeldir güzeli sever | 3D-A | v2 |
| Şifalı otlar tarhı: nane, kekik, adaçayı | Ya Nâfi' (201) | A: fayda veren | 3D | v2 |
| Gülistan tarhı (ateş çukurundan gül bahçesine) | Hasbünallahu ve ni'mel vekîl | N: Enbiyâ 69; G: ateşin gülistana dönmesi | 3D-A | v2 |
| Yedi başaklı buğday | Ya Şekûr (526, grup) | N: Bakara 261, bir tohum yedi başak | 3D-A | v2 |
| Fidanlık kasası | Ya Mübdi' (57) | A: ilk kez yaratan | 3D | v2 |
| Hazır fidan çukuru (yarının hedefi) | İnşallah | N: Kehf 23-24 | 3D | v2 |
| Nar ağacı | Rahmân suresi | N: Rahmân 68 | 3D-A | v3 |
| Talh (muz) ağacı | Vâkıa suresi | N: Vâkıa 29 | 3D-A | v3 |
| Güz çiğdemi | Ya Muahhir (847, grup) | A: erteleyen; herkesten sonra açar | 3D-A | v3 |
| Reyhan ve lavanta saksıları | Ya Şâfî (391, 99 dışı) | N: Vâkıa 89, reyhan | 3D | v3 |
| Nadir tür tohumu kesesi | Ya Hâlık (731, grup) | A: yaratan; rastgele yeni tür verir | 3D | v3 |

## C. Canlılar

Bu 18 canlının 10'u kuş, 5'i dört ayaklı, 2'si böcek, 1'i balıktır; dört rig tipi hepsini karşılar. Kuşlar ortak iskeleti paylaşır, bu yüzden yeni tür eklemek ucuzdur.

| Asset | Tetikleyici | Dayanak | Tip | Öncelik |
| --- | --- | --- | --- | --- |
| Güvercin | Sübhanallah (her 33'te bir kuş gelir) | N: Nur 41, kanat çırpan kuşlar tesbih eder | Rig | MVP |
| Serçe | Sübhanallah (rastgele tür) | N: Nur 41 | Rig | MVP |
| Bülbül | Ya Hamîd (62) | A: hamd; G: gül ve bülbül | Rig | MVP |
| Kıtmir (bahçe muhafızı) | Ya Hafîz (998, aile hedefi) | N: Kehf 18 | Rig | MVP |
| Arı | Ya Rezzâk (308) | N: Nahl 68-69 | Rig | MVP |
| Kelebek | Latîf kozasından çıkar | A: gizli lütuf | Rig | MVP |
| Kumru çifti | Ya Vedûd (20) | G: sevgi ve bağlılık | Rig | v2 |
| Harem güvercini (güvercinin doku varyantı) | Ya Mü'min (137) | G: Harem'in dokunulmaz güvercinleri, emniyet | Rig | v2 |
| Kırlangıç | Ya Tevvâb (409) | A: her yıl aynı yuvaya döner | Rig | v2 |
| Leylek ve yuvası | Ya Muîd (124) | A: geri döndüren; her bahar döner | Rig | v2 |
| Hüdhüd | Ya Habîr (812, grup) | N: Neml 20-22, haber getiren kuş | Rig | v2 |
| Kedi | Ya Veliyy (46) | A: dost | Rig | v2 |
| Ceylan | Ya Halîm (88) | A: yumuşak huylu | Rig | v2 |
| Koyun ve kuzu | Ya Raûf (287) | A: şefkat | Rig | v2 |
| Balık | Yunus duası | N: Enbiyâ 87 | Rig | v2 |
| Turna | Ya Aliyy (110) | A: yüksekte süzülen | Rig | v3 |
| Şahin | Ya Müteâlî (551, grup) | A: en yüce | Rig | v3 |
| Deve | Ya Sabûr (298) | N: Gâşiye 17; G: sabır sembolü | Rig | v3 |

## D. Yapılar ve mimari

Bu 49 satır 48 model eder (sur 2, patika 3 parçadır). Su yapıları model fabrikasında kuru üretilir; su yüzeyi A bölümündeki shader'dan gelir. Dört ırmak (su, süt, bal, şerbet) dünya modelinin (`ZB_dunya_cennet`) parçasıdır; ayrı model dosyaları yoktur, sahne onları oyuncunun durumundan açar. Başta hiçbiri yoktur; istiğfarın ömür boyu toplamı 100, 300, 700 ve 1000'e ulaşınca her biri bir kez gelir (K20). Su ırmağı çağlayanıyla birlikte gelir. Kaynakları Firdevs'tedir (Buhârî, Cihâd 4).

| Asset | Tetikleyici | Dayanak | Tip | Öncelik |
| --- | --- | --- | --- | --- |
| Bahçe kapısı | Bismillah (her oturum açılışı) | G: her hayrın başı | 3D | MVP |
| Mâşâallah kitabesi (kapı üstü levha) | Mâşâallah, lâ kuvvete illâ billâh | N: Kehf 39, bahçene girdiğinde böyle deseydin | 3D | MVP |
| Temel taşı | Ya Evvel (37) | A: ilk olan | 3D | MVP |
| Köşk | İhlas ×10 | N: Müsned, zayıf rivayet | 3D | MVP |
| Şadırvan | Ya Kuddûs (170) | A: arınma | 3D | MVP |
| Âb-ı hayat pınarı | Ya Hayy (18) | A: hayat veren | 3D | MVP |
| Su ırmağı (çağlayanıyla) | Estağfirullah toplamı 100 (bir kez) | N: Nuh 10-12, istiğfar edene yağmur, bahçeler ve ırmaklar verilir (dünya bağlamında; burada temsil); Muhammed 15, bozulmayan sudan ırmaklar | 3D | MVP |
| Süt ırmağı | Estağfirullah toplamı 300 (bir kez) | N: Muhammed 15, tadı bozulmayan sütten ırmaklar; Nuh 10-12, istiğfar ve ırmaklar (temsil) | 3D | MVP |
| Bal ırmağı | Estağfirullah toplamı 700 (bir kez) | N: Muhammed 15, süzme baldan ırmaklar; Nuh 10-12, istiğfar ve ırmaklar (temsil) | 3D | MVP |
| Şerbet ırmağı | Estağfirullah toplamı 1000 (bir kez) | N: Muhammed 15, içenlere lezzet veren içecekten ırmaklar; adı ve yakut renkli temsili danışma kurulunda (I); Nuh 10-12, istiğfar ve ırmaklar (temsil) | 3D | MVP |
| Parsel kapısı ve anahtar | Ya Fettâh (489) | A: açan | 3D | MVP |
| Sur parçaları (düz, köşe) | Tehlil-i kebir ×100 | N: Buhârî-Müslim, o gün şeytandan korunur | 3D | MVP |
| Bahçe çiti | Ya Mâni' (161) | A: engelleyen | 3D | v2 |
| Sur burcu | Ya Metîn (500, grup) | A: sapasağlam | 3D | v2 |
| Patika seti (düz, dönemeç, kavşak) | Fatiha | N: Fatiha 6, dosdoğru yol | 3D | v2 |
| Kameriye | Ya Selâm (131) | A: esenlik; Dârüsselâm | 3D | v2 |
| Sebil | Ya Rahmân (298) | G: su hayratı | 3D | v2 |
| Hayrat çeşmesi | Ya Mâcid (48) | A: cömert | 3D | v2 |
| Selsebil çeşmesi | Ya Semî' (180) | N: İnsan 18; su sesi için yapılır | 3D | v2 |
| Çıkrıklı kuyu | Ya Mücîb (55) | A: kovayı salarsın, suyla cevap verir | 3D | v2 |
| Yansıma havuzu | Ya Basîr (302) | A: gören | 3D | v2 |
| Fıskiyeli büyük havuz | Ya Celîl (73) | A: görkem | 3D | v2 |
| Kevser havuzu | Kevser suresi | N: Kevser 1 | 3D | v2 |
| Gölet | Yunus duası | N: Enbiyâ 87 | 3D | v2 |
| Bahçe deresi | Sübhanallahi ve bihamdihi ×100 | N: Buhârî, günahlar deniz köpüğü kadar olsa da silinir | 3D | v2 |
| Çarbağ kanalları (dört kol) | Ya Muksit (209) | G: çarbağ düzeni; A: denge | 3D | v2 |
| Su dolabı (sen yokken bahçeyi sular) | Ya Vekîl (66) | A: işi O'na bırakmak | 3D | v2 |
| Su değirmeni | Ya Mukît (550, grup) | A: besleyen | 3D | v2 |
| Taş köprü | Ya Kaviyy (116) | A: güçlü | 3D | v2 |
| Teras seti (yükseltilmiş kat) | Ya Râfi' (351) | A: yükselten | 3D | v2 |
| Taş avlu (arkadaş buluşma meydanı) | Ya Câmi' (114) | A: toplayan | 3D | v2 |
| Kuş evi (kuş sarayı) | Ya Rahîm (258) | G: Osmanlı kuş evleri, merhamet | 3D | v2 |
| Cihannüma (seyir kulesi) | Ya Müheymin (145) | A: gözetip koruyan | 3D | v2 |
| Taç kapı | Ya Muizz (117) | A: izzet veren | 3D | v2 |
| Mermer sütun | Ya Azîz (94) | A: yıkılmaz izzet | 3D | v2 |
| Mağara | Ya Bâtın (62) | A: gizli; N: Kehf | 3D | v2 |
| Yekpare kaya | Ya Samed (134) | A: her şeyin dayandığı | 3D | v2 |
| Sedir köşesi | Ya Melik (90) | N: İnsan 13, sedirler | 3D | v2 |
| Sancak direği | Ya Mecîd (57) | A: şan | 3D | v2 |
| Kitabe taşı (kilometre taşlarını kaydeder) | Ya Şehîd (319) | A: şahit | 3D | v2 |
| Bekçi feneri direği | Ya Rakîb (312) | A: gözeten | 3D | v2 |
| Misafir sediri | Selâmün aleyküm (arkadaş bahçesine girerken) | N: Müslim, selamı yayın | 3D | v2 |
| Nişan taşı (yön gösteren) | Ya Reşîd (514, grup) | A: doğru yola ileten | 3D | v3 |
| Yel değirmeni | Ya Kâdir (305) | A: kudret | 3D | v3 |
| Şelale | Ya Azîm (1020, grup) | A: azamet | 3D | v3 |
| Kilit taşlı kemer | Ya Âhir (801, grup) | A: son olan; temel taşının eşi | 3D | v3 |
| İkram köşkü | Ya Zü'l-Celâli ve'l-İkrâm (1100, grup) | A: celal ve ikram | 3D | v3 |
| Teras basamağı | Kur'an okuma (ayet başına bir basamak) | N: Tirmizî, oku ve yüksel | 3D | v3 |
| Çifte havuz | Rabbenâ âtinâ | N: Bakara 201, dünyada ve ahirette güzellik | 3D | v3 |

## E. Objeler

Bu 34 satırın 32'si 3D model, 2'si arayüz öğesidir. Küçük objeler en ucuz üretimlerdir; stil testine buradan başlamak mantıklıdır.

| Asset | Tetikleyici | Dayanak | Tip | Öncelik |
| --- | --- | --- | --- | --- |
| Kandil | Ya Nûr (256) | N: Nur 35 | 3D | MVP |
| Fener ve kutup yıldızı | Ya Hâdî (20) | N: Nahl 16, yıldızlarla yol bulurlar | 3D | MVP |
| Rahle ve kitap | Rabbi zidnî ilmâ | N: Tâhâ 114 | 3D | MVP |
| Define sandığı | La havle ve la kuvvete illa billah | N: Buhârî-Müslim, cennet hazinelerinden bir hazine | 3D | MVP |
| İnci | Define sandığından veya nisan yağmuru tarifinden | N: Rahmân 22 | 3D | MVP |
| Mercan | Define sandığından çıkar | N: Rahmân 22 | 3D | MVP |
| Sedef (istiridye) | Ya Vâcid (14) | A: bulan; açınca bulursun | 3D | MVP |
| Hediye bohçası (yalnız arkadaşa gönderilir) | Ya Vehhâb (14) | A: karşılıksız veren | 3D | MVP |
| İpek kozası | Ya Latîf (129) | A: gizli ve ince lütuf | 3D | MVP |
| Arı kovanı | Ya Rezzâk (308) | N: Nahl 68 | 3D | MVP |
| Tesbih | 33'lük tesbihat tamamlanınca | N: Müslim, namaz sonrası tesbihat | 3D | MVP |
| Fanus | Ya Nûr (256), ikinci item | N: Nur 35, cam içindeki kandil | 3D | v2 |
| Kütüphane dolabı | Ya Alîm (150) | A: her şeyi bilen | 3D | v2 |
| Divit ve kamış kalem | Ya Hakîm (78) | N: Kalem 1 | 3D | v2 |
| Güneş saati | Ya Hakem (68) | G: Risale-i Nur, hikmetli nizam | 3D | v2 |
| Terazi | Ya Adl (104) | N: Rahmân 7-9, mizan | 3D | v2 |
| Kıblenüma | Ya Hakk (108) | A: gerçeği gösteren | 3D | v2 |
| Abaküs | Ya Hasîb (80) | A: hesap gören | 3D | v2 |
| Mimar takımı: pergel ve cetvel | Ya Bârî (214) | A: kusursuz ve uyumlu yaratan | 3D | v2 |
| Bahçe maketi masası (kuş bakışı düzenleme) | Ya Vâlî (47) | A: yöneten | 3D | v2 |
| Koleksiyon albümü | Ya Muhsî (148) | A: tek tek sayan | UI | v2 |
| Ebru teknesi (boyama aracı) | Ya Musavvir (336) | A: şekil ve renk veren | 3D | v2 |
| Çini pano (her oyuncuya eşsiz motif) | Ya Bedî' (86) | A: örneksiz yaratan | 3D | v2 |
| Aşı ve onarım sandığı | Ya Cebbâr (206) | A: cebr, kırığı sarmak | 3D | v2 |
| Bahçe tırmığı | Ya Afüvv (156) | A: izleri silen | 3D | v2 |
| Ferman tomarı (yeni ada tapusu) | Ya Mâlikü'l-Mülk (212) | A: mülkün sahibi | 3D | v2 |
| Sedef kakma saklama kutusu | Ya Hafîz (998), ikinci item | A: koruyan | 3D | v2 |
| Altın tepsi ve ikram | Ya Kerîm (270) | N: Zuhruf 71 | 3D | v2 |
| Meyve sepeti (komşuya ikram) | Ya Berr (202) | A: iyilik eden | 3D | v2 |
| Teşekkür buketi | Cezâkallahu hayran (hediye alınca) | N: Tirmizî | 3D | v2 |
| Celâlî isimler öğretici kart seti (7 kart) | İsmin ebcedi kadar çekilince kart açılır | Gazâlî: tenzih ve haşyet | UI | v2 |
| Mücevher kutusu: yakut ve zümrüt | Ya Ganî (1060, grup) | N: Rahmân 58 | 3D | v3 |
| Bereket kesesi (arkadaşa kaynak gönderir) | Ya Muğnî (1100, grup) | A: zengin eden | 3D | v3 |
| Yadigâr sandığı (aile bahçesine miras) | Ya Vâris (707, grup) | A: her şeyin vârisi | 3D | v3 |

## F. 99 Esma dizini

99 ismin 92'sinin somut bir karşılığı var; 7 celâlî isim öğretici kart olarak kalır. MVP 16 isimle açılır. Ebced değerleri takısız hesaptır ve "Yâ" nidası sayıya katılmaz.

| # | İsim | Ebced | Karşılığı | Öncelik |
| --- | --- | --- | --- | --- |
| 1 | Allah | 66 | Lale | MVP |
| 2 | Rahmân | 298 | Sebil; rahmet bulutu | v2 |
| 3 | Rahîm | 258 | Kuş evi | v2 |
| 4 | Melik | 90 | Sedir köşesi | v2 |
| 5 | Kuddûs | 170 | Şadırvan | MVP |
| 6 | Selâm | 131 | Kameriye; sidr ağacı | v2 |
| 7 | Mü'min | 137 | Harem güvercini | v2 |
| 8 | Müheymin | 145 | Cihannüma | v2 |
| 9 | Azîz | 94 | Mermer sütun | v2 |
| 10 | Cebbâr | 206 | Aşı ve onarım sandığı | v2 |
| 11 | Mütekebbir | 662 | Karlı dağ silüeti | v3 |
| 12 | Hâlık | 731 | Nadir tür tohumu kesesi | v3 |
| 13 | Bârî | 214 | Mimar takımı | v2 |
| 14 | Musavvir | 336 | Ebru teknesi | v2 |
| 15 | Gaffâr | 1281 | Kar örtüsü | v3 |
| 16 | Kahhâr | 306 | Öğretici kart; zararlı ot temizleme mekaniği | v2 |
| 17 | Vehhâb | 14 | Hediye bohçası | MVP |
| 18 | Rezzâk | 308 | Arı ve kovan | MVP |
| 19 | Fettâh | 489 | Parsel kapısı ve anahtar | MVP |
| 20 | Alîm | 150 | Kütüphane dolabı | v2 |
| 21 | Kâbıd | 903 | Öğretici kart; sonbahar yaprak dökümü | v3 |
| 22 | Bâsıt | 72 | Çimen halısı | MVP |
| 23 | Hâfıd | 1481 | Öğretici kart | v2 |
| 24 | Râfi' | 351 | Teras seti | v2 |
| 25 | Muizz | 117 | Taç kapı | v2 |
| 26 | Müzill | 770 | Öğretici kart | v2 |
| 27 | Semî' | 180 | Selsebil çeşmesi | v2 |
| 28 | Basîr | 302 | Yansıma havuzu | v2 |
| 29 | Hakem | 68 | Güneş saati | v2 |
| 30 | Adl | 104 | Terazi | v2 |
| 31 | Latîf | 129 | İpek kozası; kelebek | MVP |
| 32 | Habîr | 812 | Hüdhüd | v2 |
| 33 | Halîm | 88 | Ceylan | v2 |
| 34 | Azîm | 1020 | Şelale | v3 |
| 35 | Gafûr | 1286 | Çiy taneli sabah | v3 |
| 36 | Şekûr | 526 | Yedi başaklı buğday | v2 |
| 37 | Aliyy | 110 | Turna | v3 |
| 38 | Kebîr | 232 | Toros sediri | v2 |
| 39 | Hafîz | 998 | Kıtmir; sedef kakma saklama kutusu | MVP |
| 40 | Mukît | 550 | Su değirmeni | v2 |
| 41 | Hasîb | 80 | Abaküs | v2 |
| 42 | Celîl | 73 | Fıskiyeli büyük havuz | v2 |
| 43 | Kerîm | 270 | Altın tepsi ve ikram | v2 |
| 44 | Rakîb | 312 | Bekçi feneri direği | v2 |
| 45 | Mücîb | 55 | Çıkrıklı kuyu | v2 |
| 46 | Vâsi' | 137 | Deniz ufku | v2 |
| 47 | Hakîm | 78 | Divit ve kamış kalem | v2 |
| 48 | Vedûd | 20 | Kumru çifti | v2 |
| 49 | Mecîd | 57 | Sancak direği | v2 |
| 50 | Bâis | 573 | Bahar patlaması | v2 |
| 51 | Şehîd | 319 | Kitabe taşı | v2 |
| 52 | Hakk | 108 | Kıblenüma | v2 |
| 53 | Vekîl | 66 | Su dolabı | v2 |
| 54 | Kaviyy | 116 | Taş köprü | v2 |
| 55 | Metîn | 500 | Sur burcu | v2 |
| 56 | Veliyy | 46 | Kedi | v2 |
| 57 | Hamîd | 62 | Bülbül | MVP |
| 58 | Muhsî | 148 | Koleksiyon albümü | v2 |
| 59 | Mübdi' | 57 | Fidanlık kasası | v2 |
| 60 | Muîd | 124 | Leylek ve yuvası | v2 |
| 61 | Muhyî | 68 | Bahar dalı | MVP |
| 62 | Mümît | 490 | Öğretici kart | v2 |
| 63 | Hayy | 18 | Âb-ı hayat pınarı | MVP |
| 64 | Kayyûm | 156 | Yıldızlı gece göğü | v2 |
| 65 | Vâcid | 14 | Sedef | MVP |
| 66 | Mâcid | 48 | Hayrat çeşmesi | v2 |
| 67 | Vâhid | 19 | Servi | MVP |
| 68 | Samed | 134 | Yekpare kaya | v2 |
| 69 | Kâdir | 305 | Yel değirmeni | v3 |
| 70 | Muktedir | 744 | Şimşek ve gök gürültüsü | v3 |
| 71 | Mukaddim | 184 | Kardelen | v2 |
| 72 | Muahhir | 847 | Güz çiğdemi | v3 |
| 73 | Evvel | 37 | Temel taşı | MVP |
| 74 | Âhir | 801 | Kilit taşlı kemer | v3 |
| 75 | Zâhir | 1106 | Parlak güneşli gün | v3 |
| 76 | Bâtın | 62 | Mağara | v2 |
| 77 | Vâlî | 47 | Bahçe maketi masası | v2 |
| 78 | Müteâlî | 551 | Şahin | v3 |
| 79 | Berr | 202 | Meyve sepeti | v2 |
| 80 | Tevvâb | 409 | Kırlangıç | v2 |
| 81 | Müntekım | 630 | Öğretici kart | v2 |
| 82 | Afüvv | 156 | Bahçe tırmığı | v2 |
| 83 | Raûf | 287 | Koyun ve kuzu | v2 |
| 84 | Mâlikü'l-Mülk | 212 | Ferman tomarı | v2 |
| 85 | Zü'l-Celâli ve'l-İkrâm | 1100 | İkram köşkü | v3 |
| 86 | Muksit | 209 | Çarbağ kanalları | v2 |
| 87 | Câmi' | 114 | Taş avlu | v2 |
| 88 | Ganî | 1060 | Mücevher kutusu | v3 |
| 89 | Muğnî | 1100 | Bereket kesesi | v3 |
| 90 | Mâni' | 161 | Bahçe çiti | v2 |
| 91 | Dârr | 1001 | Öğretici kart | v2 |
| 92 | Nâfi' | 201 | Şifalı otlar tarhı | v2 |
| 93 | Nûr | 256 | Kandil; fanus; kandil ışığı | MVP |
| 94 | Hâdî | 20 | Fener ve kutup yıldızı | MVP |
| 95 | Bedî' | 86 | Çini pano | v2 |
| 96 | Bâkî | 113 | Defne | v2 |
| 97 | Vâris | 707 | Yadigâr sandığı | v3 |
| 98 | Reşîd | 514 | Nişan taşı | v3 |
| 99 | Sabûr | 298 | Deve | v3 |

99 dışı iki isim de listede: Cemîl (83) süs çiçekleri setini, Şâfî (391) reyhan ve lavanta saksılarını verir.

## G. Tarif zincirleri

Mevcut item'lar birleşerek 13 yeni model üretir; hiçbiri yeni zikir gerektirmez. İki tarif yeni model istemez: nisan yağmuru ile sedef inciyi verir, zeytinyağı testisi ile kandil tam parlaklığa ulaşır.

| Tarif | Ürün | Dayanak | Öncelik |
| --- | --- | --- | --- |
| Olgun zeytin ağacı, hasat | Zeytinyağı testisi | N: Nur 35 | v2 |
| İnci ×33 + köşk | İnci köşk | N: Buhârî-Müslim, inciden çadırlar | v2 |
| Kırmızı gül ×100 + arı kovanı | Gül balı kavanozu | N: Nahl 69 | v2 |
| Kırmızı gül ×100 + şadırvan | Gülabdan (gülsuyu) | G: gülsuyu ikramı | v2 |
| Yedi başaklı buğday + su değirmeni | Un çuvalı | A: rızkın emeği | v2 |
| Un çuvalı ×3 | Taş fırın ve ekmek | A: rızkın emeği | v2 |
| Çini pano + lale | Lale motifli çini niş | G: çinide lale, tevhid sembolü | v2 |
| Mağara + Kıtmir | Kehf köşesi (Kıtmir'in nöbet yeri) | N: Kehf 18 | v2 |
| Ekmek + altın tepsi + meyve sepeti | İkram sofrası | G: misafire ikram | v3 |
| Olgun asma + parlak güneşli gün | Pekmez küpü | G | v3 |
| İpek kozası ×10 + ebru teknesi | İpek kilim | N: Gâşiye 16, serilmiş halılar | v3 |
| Çarbağ kanalları + bahçe deresi | Dört ırmak merkez havuzu | N: Muhammed 15 | v3 |
| Temel taşı + kilit taşlı kemer | Revak (kemerli yol) | A: Evvel ve Âhir | v3 |

## H. Sayım özeti ve üretim notları

> **Revizyon (2026-09-24):** Modeller artık Tripo'da değil, depodaki prosedürel **ZB model fabrikasında** (`tools/model_factory/`) üretilir. Kredi ve plan hesabı kaldırıldı. Ayrıntı: `docs/kararlar.md`.

Toplam 161 asset, büyüme aşamalarıyla birlikte 203 model dosyası eder; MVP bunun 59'udur. Dört ırmak dünya modelinin parçası olduğu için model dosyası sayısını artırmaz. Sayılar `game/data/assets.json` içindeki `meta.ozet` alanından gelir ve `tools/content/build_content.py` her çalıştığında yeniden hesaplanır. Önceki Tripo tahmini v2 için 115 diyordu. Aradaki 2'lik fark, harem güvercininin ayrı model değil renk varyantı sayılmasından ve aşama sayılarının artık kuraldan hesaplanmasından gelir.

| Sürüm | Asset | Model dosyası |
| --- | --- | --- |
| MVP | 44 | 59 |
| v2 | 87 | 113 |
| v3 | 30 | 31 |
| Toplam | 161 | 203 |

- **Üretim yöntemi:** Her model bir Python fonksiyonudur (`tools/model_factory/models/`). Parametreler koddadır, yani model istenildiği an yeniden üretilebilir, renk veya oran değişikliği tek satırdır. `python3 tools/model_factory/build_all.py` bütün modelleri `game/assets/models/` altına `.glb` olarak yazar.
- **Stil:** Stilize low-poly, düz gölgeli (flat shading), tek palet. Palet `tools/model_factory/palette.py` içindedir; Osmanlı çini ve bahçe renklerinden seçilmiştir.
- **Üretim sırası:** Önce E bölümündeki küçük objelerle stil testi, sonra yapılar, sonra bitkiler, en son canlılar.
- **Bitkiler:** Gövde, dal ve yaprak kümeleri aynı fonksiyondan aşama parametresiyle üretilir (tohum, filiz, fidan, olgun). Aşamalar birbirinin büyümüş hâlidir, bu yüzden geçiş animasyonu tutarlıdır.
- **Su yapıları:** Kuru üretilir; su yüzeyi shader'dan gelir. Su yüzeyinin yeri modelde `water_*` adlı boş bir düğümle işaretlenir.
- **Canlılar:** İskelet (skin) yerine parçalı hiyerarşi kullanılır: gövde, kanat, kuyruk, baş ayrı düğümlerdir ve Godot'da AnimationPlayer ile oynatılır. 10 kuş ortak parça setini paylaşır. Harem güvercini yeni model değil, güvercinin renk varyantıdır.
- **Dosya adı:** `ZB_[kategori]_[isim]_a[aşama]`, örneğin `ZB_agac_hurma_a3`. Aşamasız modellerde `_a` eki yoktur.
- **Önizleme:** `tools/preview/` her modelin görüntüsünü alıp bir kontakt sayfası üretir; görsel kontrol buradan yapılır.
- **İç içe geçen ifadeler:** "Sübhanallah" üç ayrı zikrin, "La ilahe illallah" tehlil-i kebirin başlangıcıdır. "La havle" ile "Mâşâallah" aynı sözlerle biter. Sistem ifade bitmeden ödül vermemelidir.
- **Sure tanıma:** İhlas, Fatiha, Tîn, Kevser ve Felak kısa zikirlerden zor tanınır. İhlas MVP'de olduğu için ilk ses prototipinde test edilmelidir.

## I. Danışma kuruluyla teyit edilecekler

Listedeki ayet ve hadis atıflarının bir kısmı araştırma raporundan, bir kısmı hafızadan yazıldı; üretime geçmeden önce hepsi tek tek doğrulanmalıdır.

- [ ] Hafızadan eklenen dayanaklar: Kehf 39, Bakara 261, Neml 20-22, Enbiyâ 69 ve 87, Tâhâ 114, Hac 5-6, A'râf 57, tehlil-i kebir hadisi, deniz köpüğü hadisi, selam hadisi, "oku ve yüksel" hadisi.
- [ ] İhlas ×10 köşk rivayeti zayıftır. Kartta bu nasıl belirtilecek?
- [ ] Tûbâ ve Kevser gerçek cennet öğeleridir. Modellenmeleri uygun mu, yoksa "merkez ağaç" ve "büyük havuz" gibi nötr adlar mı kullanılsın?
- [ ] Esma eşleştirmelerinin çoğu A kodludur, yani tasarım kararıdır. Kartlarda "bu bir temsildir" dili yeterli mi?
- [ ] Yedi celâlî ismin öğretici kart olarak kalması ve Kahhâr'ın temizleme mekaniği onaylanıyor mu?
- [ ] Ebced adetleri ve Salât-ı Tefriciye gelenek kaynaklıdır. "Gelenek" etiketi ve kapatılabilir ebced modu yeterli mi?
- [ ] Günlük dildeki sözler (İnşallah, Mâşâallah, Selâmün aleyküm, Cezâkallah) ödüle bağlanabilir mi?
- [ ] Kıtmir'in köpek olarak bahçede yer alması tüm hedef pazarlarda kabul görür mü?
- [ ] Nuh 10-12 (istiğfar edene yağmur, mal, evlat, bahçeler ve ırmaklar) dünya hayatıyla ilgili bir vaattir. Oyunda istiğfarın nisan yağmurunu ve cennetin dört ırmağını (Muhammed 15) açması bir temsil olarak kullanılıyor (K20). Bu bağlantı ve kartta "bu bir temsildir" dili uygun mu?
- [ ] Şerbet ırmağı: Muhammed 15'teki şarap ırmağının çocuk diline uygun adı ve yakut renkli temsili (`docs/mekan-kurgusu.md`, "Danışma kuruluna sorulacaklar"). Kesinleşene kadar "şerbet" adı geçicidir.
