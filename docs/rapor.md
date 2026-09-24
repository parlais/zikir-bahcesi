# ZİKİR BAHÇESİ — Sesli Zikir ile "Cennet İnşa" Oyunu: Fizibilite ve Strateji Raporu

## YÖNETİCİ ÖZETİ
Fikir hem dini açıdan güçlü bir metafora (zikirle cennette ağaç dikilmesi hadisleri) hem de kanıtlanmış bir oyun mekaniğine (Forest/Finch tarzı "alışkanlık→bahçe") dayanıyor ve bu ikisini birleştiren, sesli tanıma temelli bir İslami oyun pazarda **yok**. Sesli zikir sayıcıları var ama oyunlaştırılmış "cennet bahçesi" yok; İslami çocuk oyunları var ama sesli/gerçek zamanlı zikir mekaniği yok. Bu net bir boşluk (gap) ve fikrin özgün, savunulabilir çekirdeğidir.

En kritik üç karar: (1) Gerçek zamanlı ses tanımayı **cihaz-üstü (on-device) keyword spotting** ile çözmek — hem gizlilik/çocuk mevzuatı hem gecikme açısından şart. (2) **Riya/ihlas hassasiyetini** tasarımın merkezine koymak (klasik liderlik tablosu yerine ortak/aile hedefleri, cezasız ekonomi). (3) MVP'yi **8-12 zikir + tek bahçe + özel/hazır KWS** ile dar tutup, önce Arapça zikir tanıma doğruluğunu prototiple test etmek.

En büyük iki risk: Arapça zikir ifadelerinin cihaz-üstü tanınma doğruluğu (özellikle çocuk sesi ve aksan çeşitliliğiyle) ve ibadetin oyunlaştırılmasına dair teolojik hassasiyet. Her ikisinin de somut karşı önlemleri var ve rapor boyunca işlendi.

---

## 1. RAKİP VE BENZER ÜRÜN ANALİZİ

### 1a. Sesli zikir sayıcıları (mekanik örtüşme var, oyun yok)
- **Tasbih Speech Recognition (MWM)**: "Pazardaki ilk" iddiasıyla sesle zikir tanıyıp sayan uygulama. Sesle tanıma + dokunma yedeği. Oyun/ödül/dünya katmanı yok.
- **Dhikr – Dua, Athkar & Tasbih**: "AI Mic" ile sesle sayım, iQibla Zikr Ring Bluetooth entegrasyonu, streak + streak-freeze, başarımlar, günlük dhikr skoru, widget'lar, Siri kısayolu. En olgun rakip; hafif oyunlaştırma var ama bahçe/dünya inşası yok.
- **ZikirVox, Tazbi, Voice Dhikr Counter, Tasbih Voice**: Sesli sayım + offline + özelleştirilebilir zikir, haptik/sesli geri bildirim. Hepsi basit sayaç; görsel dünya yok.
- **Çıkarım**: Sesli tanıma teknik olarak kanıtlanmış ve rakiplerce yaygın kullanılıyor; farklılaşma sayaçta değil **oyun/dünya-inşa katmanında**.

### 1b. Kur'an sesli tanıma (teknoloji öncüsü, altın referans)
- **Tarteel AI**: App Store açıklamasına göre "Join 15+ million Muslims" — kelime düzeyinde gerçek zamanlı Kur'an tanıma, hata tespiti, "Shazam for Quran" sesli arama. NVIDIA vaka çalışmasına göre Riva/NeMo ile "state-of-the-art results with a 4 percent WER" elde etti ve dünyanın ilk Kur'an Arapçası ASR'sini kurdu. Mikrofon + internet gerektiriyor. Freemium + aile planı (5 kişi) + okullar için LMS entegrasyonu. Açık kaynak veri seti (everyayah, Hugging Face) yayınladı. **Teknoloji, veri, iş modeli ve âlim danışmanlığı için birebir referans.**

### 1c. İslami çocuk oyunları (tematik örtüşme var, mekanik yok)
- **Masjid Builder**: Sürükle-bırak cami inşası (kubbe, minare), 5-10 yaş. Sığ; sesli/zikir yok.
- **Muslim Kids TV, Noor Kids, Omar & Hana, Ali Huda**: İçerik/çizgi film/quiz ağırlıklı; dünya-inşa veya sesli zikir yok.
- **Salaam Gateway ("Top 10 Islamic-themed children gaming apps") analizi**: Tür hâlâ "lightweight quiz and learning games rather than high-production 3D titles" hâkimiyetinde; yüksek prodüksiyonlu 3D başlık az, ama kitle "large and loyal" — bu doğrudan bir fırsat.
- Bazı derleme kaynaklarda "doğru okunan kelimelerle köy inşa eden" ve "3D cami özelleştiren" uygulamalardan söz ediliyor; ancak **sesli/gerçek zamanlı zikir + cennet bahçesi** kombinasyonu hiçbirinde yok.

### 1d. İslami olmayan mekanik komşular (tasarım referansı)
- **Forest**: Odaklanınca ağaç büyür; tek seferlik satın alma; telefon bağımlılığına odaklı.
- **Finch (Self-Care Pet)**: Alışkanlık→kuş büyür; **cezasız, şefkat temelli**; bağımsız bir gamification uzmanı (Gamification+) tarafından 2026 için en iyi oyunlaştırılmış alışkanlık uygulaması seçildi. Streak korkusunu kaldıran nazik tasarımı çocuk/gençte model alınmalı.
- **Habitica**: Tam RPG; 15M+ indirme; HP kaybı/ceza mekaniği — **ibadet için sakıncalı model** (asla cezalandırıcı olmamalı).
- **Habit garden uygulamaları (Habitanics vb.)**: "Her alışkanlık bir ekin"; büyüme metaforu, görünmez tutarlılığı görünür kılar. Fikrin çekirdek psikolojisiyle birebir örtüşür ("nurture beats guilt").
- **Cozy/garden builder**: Animal Crossing, Viridi, Terra Nil, Tiny Glade, Townscaper — sanat yönü ve düşük-stres tasarım referansları.

### 1e. Hadis temasını doğrudan kullanan ürün var mı?
Hayır — "zikir→cennette ağaç" hadisini oyunlaştıran bir ürün tespit edilmedi. Tema teolojik olarak sağlam: Tirmizî 3462 (İbrahim as'ın Miraç'ta tavsiyesi: "Cennet toprağı verimli ama boştur; fidanları SubhanAllah, Elhamdülillah, La ilahe illallah, Allahu Ekber'dir"), Tirmizî 3464 (SubhanAllahi'l-azîm ve bihamdihi → cennette hurma ağacı), "La havle ve la kuvvete illa billah = cennetin fidanı" (İbn Ömer). Bu, fikrin özgün ve nass-temelli dayanağıdır.

**GAP ÖZETİ**: Sesli/gerçek zamanlı zikir tanıma + cennet bahçesi/dünya inşası + çocuk-genç odağı + hadis temelli ödül mantığı = pazarda **bileşik olarak yok**. Farklılaşma net ve savunulabilir.

---

## 2. PAZAR ARAŞTIRMASI

- **Küresel Müslüman/helal ekonomi**: DinarStandard'ın *State of the Global Islamic Economy Report 2023/24* raporuna göre küresel İslami ekonomi sektörlerindeki tüketici harcaması 2022'de yıllık %9.5 büyümeyle 2.29 trilyon $'a ulaştı; İslami finans varlıklarının 2026'da 5.96 trilyon $'a çıkması bekleniyor. Müslüman nüfus ~1.9 milyar (2023).
- **Muslim Pro (Bitsmedia)**: 7 Aralık 2023 duyurusuna göre "over 150 million downloads globally"; Bintang Capital verisine göre "more than 25 million Monthly Active Users". 20M $ Seri A turuna CMIA, Gobi Partners ve Bintang Capital birlikte katıldı (tek lider Gobi değil). Gelir tarihsel olarak ~%85-90 reklam, %10-15 abonelik ($4.99). İlk 25M kullanıcı **organik** (sıfır pazarlama), Ramazan'da zirve — güçlü bir topluluk/mevsimsellik modeli.
- **Tarteel**: 15M+ kullanıcı; freemium + aile + okul lisansı.
- **Çocuk eğitim oyunları pazarı**: DataHorizzon Research'e göre "valued at USD 13.6 billion in 2024 and is expected to reach USD 31.1 billion by 2033, growing at a CAGR of 8.8% from 2025 to 2033"; Kuzey Amerika ~%36 pay, en yüksek CAGR Asya-Pasifik'te (genç Müslüman nüfusun yoğun olduğu bölge — stratejik örtüşme).
- **Cozy game pazarı**: Küresel ~973M $ (2024) → ~1.47 milyar $ (2032), %6.5 CAGR (IntelMarketResearch/GlobalInfoResearch tahminleri; kaynaklar arası fark var, ihtiyatla kullanılmalı). Türkiye MEA bölümünde ayrıca izleniyor.
- **Hedef pazarlar**: Endonezya & Malezya (Muslim Pro'nun en güçlü olduğu, mobil-öncelikli en büyük Müslüman pazarlar), Türkiye (yerel pazar + tasavvufi geleneğe açık), Körfez/MENA (Ramazan'da alışveriş uygulama oturumları yıllık %20 artıyor), Pakistan, Hindistan, Batı diasporası (ABD, UK, Almanya, Fransa).
- **Gelir modeli seçenekleri ve hassasiyetler**:
  - **Abonelik / aile planı** — Tarteel & Muslim Pro'da doğrulanmış; çocuk uygulamasında en temiz gelir.
  - **Kozmetik satış** (bahçe süsleri, mimari temalar, gökyüzü/atmosfer) — **pay-to-win DEĞİL**; ibadet karşılığı (zikir sayısı) satın alınmamalı, yalnızca estetik/kolaylık satılmalı.
  - **Reklam** — çocuk uygulamalarında COPPA/Families riski nedeniyle **kaçınılmalı** (aşağıda).
  - **Bağış/vakıf** (LaunchGood), **okul/Kur'an kursu kurum lisansı**, sadaka-jar modeli.
  - **Kritik etik kural**: İbadetin kendisi asla parayla satılmaz; para yalnızca estetik/kolaylık içindir.

---

## 3. TEKNİK FİZİBİLİTE — GERÇEK ZAMANLI SESLİ ZİKİR TANIMA (en kritik bölüm)

### 3a. Önerilen mimari: Cihaz-üstü Keyword Spotting (KWS)
Zikir tanıma bir **sınırlı sözcük dağarcığı** problemidir (10-30 sabit ifade), tam ASR değil. Doğru araç **keyword spotting**:
- **Picovoice Porcupine/Rhino**: Cihaz-üstü, düşük gecikme, MCU'da 20KB RAM'e kadar çalışır; özel wake-word konsoldan **saniyeler içinde, veri toplamadan** eğitilir; birden çok anahtar kelimeyi eşzamanlı, ihmal edilebilir ek maliyetle tanır. **KRİTİK UYARI**: Porcupine'ın resmi desteklediği diller İngilizce, İspanyolca, Fransızca, Almanca, İtalyanca, Japonca, Korece, Portekizce, Çince — **Arapça yok**. Arapça zikir ifadeleri için özel model/alternatif gerekebilir; bu, **prototipte ilk doğrulanması gereken risk**.
- **Açık kaynak alternatifler (özel zikir KWS için)**: openWakeWord, Sherpa-ONNX keyword spotting, Vosk, TensorFlow Lite/ONNX mikro modeller. Bunlarla kendi zikir sözlüğünüz için özel KWS eğitilebilir (ifadeler transliterasyondan bağımsız akustik kalıp olarak öğrenilir).
- **Genel ASR (yedek/doğrulama katmanı)**: whisper.cpp / faster-whisper / distil-whisper. Argmax WhisperKit (arXiv:2507.10860) cihaz-üstü gerçek zamanlı ASR'de "matches the lowest latency at 0.46s while achieving the highest accuracy 2.2% WER" sonucu verdi ve model ağırlıklarını outlier-decomposed palettization ile 1.6 GB'den 0.6 GB'ye sıkıştırdı (<%1 WER değişimiyle). Yine de tam Whisper mobilde ağırdır; **KWS + gerekirse ASR doğrulaması** en uygun mimari.

### 3b. Zorluklar ve çözümler
- **Hızlı seri tekrar (100x)**: KWS ardışık tetiklemeleri sayar; enerji/ritim tabanlı segmentasyon + minimum aralık eşiği.
- **Aksan çeşitliliği (Türk/Arap/Endonezya/Güney Asya) + çocuk sesleri**: Çok-aksanlı veri seti + çocuk sesi augmentasyonu şart. Literatür (KidWhisper; çocuk ASR çalışmaları) çocuk-yetişkin performans farkını ve adaptasyon ihtiyacını doğruluyor.
- **Fısıltı/sessiz zikir**: Eşik ayarı + "sessiz mod" (dokunmatik tesbih yedeği her zaman açık).
- **Hile önleme**: Kayıt çalma/başka kelime söyleme tespiti zor; canlılık için mikro-değişkenlik/ritim kontrolü. En güçlü çözüm **konumlandırma**: oyun "yarış değil ibadet/alışkanlık aracı" olduğundan hile "kendini kandırma" olur — tasarımsal olarak anlamsızlaştırılır.
- **Veri seti stratejisi**: Tarteel'in açık **everyayah** veri seti (~829 saat eğitim, 16kHz Arapça, reciter etiketli) fine-tune için başlangıç noktası. Özel zikir seti için: topluluk crowdsourcing + TTS ile sentetik augmentasyon. Kaç saat gerektiği KWS için ASR'den çok daha az (ifade başına yüzlerce-binlerce örnek yeterli olabilir).

### 3c. Çocuk verisi ve gizlilik (belirleyici — teknik değil, hukuki zorunluluk)
- **Geçerli mevzuat**: COPPA (ABD; FTC'nin bir on yıldaki en büyük güncellemesi 23 Haziran 2025 yürürlük, çoğu şirkete 22 Nisan 2026'ya kadar uyum süresi), GDPR-K (AB, <16, ülkeye göre 13'e inebilir), KVKK (TR), UK Age-Appropriate Design Code, Apple Kids Category, Google Play Families. Google Play Families politikası mikrofonu açıkça çocuklardan gelen "hassas bilgi" sayar.
- **Cihaz-üstü işleme = mevzuat avantajı**: Ses cihazdan çıkmazsa kişisel veri toplama minimize olur → doğrulanabilir ebeveyn onayı yükü ve ihlal riski büyük ölçüde düşer. Bu, on-device KWS'yi **hem teknik hem hukuki olarak zorunlu** kılar.
- Üçüncü parti SDK'lar (analitik/reklam) COPPA'nın en büyük risk kaynağı; **çocuk modunda kapatılmalı**.

### 3d. Yardımcı/alternatif giriş
Dokunmatik dijital tesbih (her zaman yedek), akıllı tesbih yüzüğü (iQibla Zikr Ring Bluetooth — Dhikr uygulamasında zaten entegre), akıllı saat.

---

## 4. OYUN MOTORU VE TEKNOLOJİ YIĞINI

| Kriter | Unity | Godot 4.x | Web (Three.js/Babylon/PlayCanvas) |
|---|---|---|---|
| Mobil 3D olgunluk | En yüksek (URP), en geniş ekosistem | Hızla olgunlaşıyor | Orta; hafif sahnelerde iyi |
| AI-destekli kodlama ("vibe coding") | C# + binary sahne/.meta → AI için zor | Metin tabanlı sahne + GDScript → **AI için en kolay** | JS → AI iyi |
| Asset Store | Devasa | Küçük (çoğu asset elle) | npm/çeşitli |
| Maliyet | Runtime Fee kaldırıldı (2026) | Tamamen ücretsiz/açık kaynak | Ücretsiz |
| Mikrofon/ML entegrasyonu | Olgun eklentiler (Picovoice SDK dahil) | ONNX var, daha az olgun | Web Audio + WASM |
| Öneri | Ticari/ölçekli mobil için **güvenli seçim** | Küçük/tek kişilik ekip + AI-destekli geliştirme için **ideal** | Hızlı prototip/hafif web sürümü |

**Öneri**: Mobil olgunluk + Picovoice/ML SDK desteği nedeniyle **Unity** en güvenli seçim. Ancak ekip tek kişi + yoğun AI-destekli geliştirme (Claude Code vb.) yapacaksa **Godot 4.x** ciddi değerlendirilmeli — metin tabanlı mimarisi AI ajanlarının sahneleri okuyup değiştirmesini Unity'ye göre çok kolaylaştırır. Karar Açık Soru #2'de.

**Backend**: Firebase (hızlı başlangıç, auth, bulut kayıt), Supabase (açık kaynak, Postgres), PlayFab (oyun servisleri), Nakama (açık kaynak, sosyal/gerçek zamanlı — arkadaş bahçesi ziyareti, aile/sınıf grupları için uygun). **MVP: Firebase veya Supabase; sosyal ölçek: Nakama.**

**Görsel stil**: Voxel/Minecraft yerine **low-poly stilize diorama/ada** önerilir — üretim maliyeti düşük, mobil performans yüksek, İslam bahçe estetiğine (çarbağ) uygun, AI 3D araçlarının en iyi çalıştığı format. Prosedürel bitki büyümesi için L-systems + elle hazırlanmış büyüme aşamaları; günlük/mevsimsel döngüler.

---

## 5. 3D ASSET ÜRETİMİ VE SANAT YÖNETİMİ

> **Revizyon (2026-09-24):** Bu bölüm araştırma dönemi notudur. Karar değişti: modeller AI 3D servislerinde (Tripo vb.) değil, depodaki prosedürel model fabrikasında üretilir. Bkz. `docs/kararlar.md`.

### 5a. AI 3D üretim araçları (2025-2026)
| Araç | Güç | Oyun-hazır? | Lisans notu |
|---|---|---|---|
| **Meshy 7** | En dengeli; text/image-to-3D, PBR, auto-rig, 600+ animasyon | Evet | Ücretsiz katman CC BY 4.0 (herkese açık); özel sahiplik Pro'da |
| **Tripo (P1 / v3)** | Oyun-hazır temiz topoloji (~20K poly), auto-rig, stilize (voxel/cartoon) | **En iyi oyun çıktısı** | Ücretsiz katman ticari **değil** |
| **Rodin Gen-2 / 2.5** | En yüksek gerçekçilik, 5 kalite katmanı | Hero assetler için | İndirme/ticaret ücretli planlarda |
| **Hunyuan3D 2.1** | Açık kaynak, self-host, yüksek kalite | Evet (post-process az) | Lisans AB/UK/G.Kore hariç |
| **TRELLIS 2** | Görsel kalite (Gaussian splatting), ~15-30s | Previz için | Model/kod MIT |

**İş akışı önerisi**: Ucuz iterasyon için Meshy veya Rodin (düşük katman, ~20 kredi) → oyun-hazır mesh için **Tripo P1** → hero/özel varlık için Rodin Ultra veya Hunyuan. **Lisansları yayından önce mutlaka kontrol edin** — bu sektörde koşullar habersiz değişiyor ("generate free, pay to own" kalıbı).

### 5b. Doku / skybox / ses
- Doku/materyal: AI PBR araçları (Meshy dahil). Gökyüzü/atmosfer: **Blockade Labs** (cennet gökyüzü, kandil/nur atmosferi).
- 2D görsel/UI/konsept: **Flux, Nano Banana (Gemini görsel modelleri), Seedream, Ideogram, Recraft, Krea, Higgsfield**. (Talebiniz gereği Midjourney/DALL-E önerilmedi.)
- Ses efekti/ambiyans: doğa/su/kuş sesleri kütüphaneleri + AI ses üretimi.

### 5c. Hazır asset kaynakları
- **Ücretsiz CC0**: Kenney, Quaternius (binlerce oyun-hazır, rigged model), Poly Pizza (Unity/Unreal/Godot hazır FBX/GLTF, giriş gerektirmez).
- **Ücretli/kaliteli**: Synty (stilize), Unity Asset Store, Fab, Sketchfab, Poly Haven (HDRI/doku).
- **İslami mimari**: CGTrader ve TurboSquid'de yüzlerce-binlerce cami/İslami mimari modeli mevcut (kubbe, minare, kemer). Çini/mukarnas/şadırvan/köşk gibi özgün öğeler için büyük olasılıkla özel üretim (AI 3D + elle rötuş) gerekir.

### 5d. Sanat yönü referansları
İslam bahçe geleneği (çarbağ/chahar bagh, Elhamra, Osmanlı has bahçeleri, lale/gül bahçeleri; Paradise garden geleneğinde zeytin/incir/hurma/nar sembolik ve yaygın), Kur'an-hadis cennet tasvirleri (altından ırmaklar akan bahçeler; su/süt/bal ırmakları; köşkler, inci çadırlar, Tûbâ ağacı, Sidre, Kevser, hurma/nar/üzüm), Osmanlı minyatürü/çini/tezhip/hat estetiği → modern stilize low-poly ile birleştirme. Bu, PARLADOR'un "Anadolu Rönesansı" felsefesiyle doğrudan örtüşür.

### 5e. İlk sürüm (MVP) 3D asset listesi taslağı (öncelik: Y=yüksek, O=orta, D=düşük)
| Kategori | Örnek öğeler | Adet (MVP) | Öncelik |
|---|---|---|---|
| Arazi/ada | Başlangıç adası + 2-4 genişleme parseli | 3-5 | Y |
| Su öğeleri | Irmak, havuz, şadırvan, çeşme | 4-6 | Y |
| Ağaçlar + büyüme aşamaları | Hurma, gül fidanı, genel ağaç (tohum→fidan→olgun, 3-4 aşama) | 5 tür × 4 aşama | Y |
| Çiçekler | Gül (salavat), lale, genel çiçek | 6-8 | Y |
| Mimari | Köşk, kemer, kubbe, kandil kulesi | 5-8 | O |
| Işık kaynakları | Kandil, fener, "nur" efekti (Ya Nûr) | 4-6 | O |
| Canlılar | Kuş, kelebek (peygamber/melek/insan tasviri **yok**) | 3-5 | O |
| Dekor | Halı, çini panel, çadır, taş yol | 6-10 | O |
| VFX | Tohum belirme, büyüme, ışık parçacıkları, ödül patlaması | 6-8 | Y |
| UI | Zikir sayacı, bahçe haritası, koleksiyon, öğretici kart, ebeveyn paneli | tam set | Y |
| Avatar | Opsiyonel; başta gereksiz (bahçe = ana özne) | 0-1 | D |

---

## 6. İÇERİK TASARIMI: ZİKİRLER, ESMALAR, ITEM EŞLEŞTİRMELERİ

### 6a. Temel zikirler ve oyun karşılıkları (sahih kaynaklı)
| Zikir | Kaynak/fazilet | Oyun karşılığı (öneri) |
|---|---|---|
| La ilahe illallah (Tevhid) | Zikrin en faziletlisi; cennet ağaçları hadisi | **Hava/oksijen** — en temel, her şeyin ön koşulu (kullanıcının fikri) |
| SubhanAllah | Tirmizî 3462-3464: cennette ağaç | Ağaç/genel bitki büyümesi |
| Elhamdülillah | Aynı hadis; "mizanı doldurur" (Müslim) | Su/bereket, sulama kaynağı |
| Allahu Ekber | Aynı hadis | Yükseklik/mimari yükseltme, kubbe |
| SubhanAllahi ve bihamdihi | Buhârî: 100x → günahlar deniz köpüğü kadar da olsa bağışlanır | Hızlı filiz/bonus |
| SubhanAllahi'l-azîm ve bihamdihi | Tirmizî 3464: cennette **hurma ağacı** | Hurma ağacı (özel) |
| La havle ve la kuvvete illa billah | İbn Ömer: "cennetin fidanı/hazinelerinden hazine" | Nadir fidan/hazine sandığı |
| Estağfirullah (istiğfar) | Nuh 10-12: yağmur, mal-evlat, bağ-bahçe | **Yağmur/rızık** — bahçeyi canlandırır |
| Salavat-ı şerife | Cuma ve genel faziletler | **Gül** (kullanıcının fikri) |
| Bismillah | Her hayrın başı | Günlük başlangıç bonusu |
| 33'lük tesbihat | Namaz sonrası sünnet | Günlük vird paketi |

### 6b. Esma-i Hüsna — Ebced değerleri + item önerileri (doğrulanmış tam tablo)
**Önemli not**: Aşağıdaki değerler tasavvufi/havas geleneğine (kökü Bûnî'nin *Şemsü'l-Maârif*'ine dayanır) ait, "zikir adedi" olarak yaygın kabul gören ebced değerleridir. **Kur'an veya sahih hadis kaynaklı bir farz adet değildir** (bkz. Bölüm 7). Değerler **takısız** hesaplanır ("el-/er-" eklenmez); "Yâ" nidâsı (=11) sayıya **katılmaz**. İki ana Türkçe kaynak (nukteler.com ve kunfeyekun.org/Arif Arslan listesi) karşılaştırıldı; 1-2 puanlık farklar "Not" ile işaretlendi.

| # | İsim | Ebced/Zikir | Not | Önerilen item/mekanik |
|---|---|---|---|---|
| 1 | Allah | 66 | | Merkez/çekirdek |
| 2 | Er-Rahmân | 298 | | Bereket yağmuru, geniş büyüme alanı |
| 3 | Er-Rahîm | 258 | | Şifa alanı, canlandırma |
| 4 | El-Melik | 90 | | Saray/köşk parçası, arazi tapusu |
| 5 | El-Kuddûs | 170 | bazı hesapta 605 | Su/arınma havuzu, temizlik efekti |
| 6 | Es-Selâm | 131 | | Huzur alanı (buff), sessiz köşe |
| 7 | El-Mü'min | 137 | 136/137 | Koruma kalkanı |
| 8 | El-Müheymin | 145 | | Gözetleme kulesi |
| 9 | El-Azîz | 94 | | Onur/rütbe nişanı |
| 10 | El-Cebbâr | 206 | | Onarım/tamir |
| 11 | El-Mütekebbir | 662 | | Anıtsal yapı (grup) |
| 12 | El-Hâlık | 731 | | Yeni tür yaratma (grup) |
| 13 | El-Bârî | 214 | 213/214 | İnşa aracı |
| 14 | El-Musavvir | 336 | | **Boyama/şekillendirme aracı** |
| 15 | El-Gaffâr | 1281 | | Toplu hata silme (grup) |
| 16 | El-Kahhâr | 306 | | Zararlı temizleme |
| 17 | El-Vehhâb | 14 | | Hediye/bağış |
| 18 | Er-Rezzâk | 308 | | **Meyve/rızık üretimi, verim artışı** |
| 19 | El-Fettâh | 489 | | **Kapı/anahtar → yeni bölge açma** |
| 20 | El-Alîm | 150 | | Kitap/kütüphane, ipucu |
| 21 | El-Kâbıd | 903 | | (ileri seviye) |
| 22 | El-Bâsıt | 72 | | Alan genişletme |
| 23 | El-Hâfid | 1481 | | (ileri seviye) |
| 24 | Er-Râfi' | 351 | | Yükseltme |
| 25 | El-Muizz | 117 | | Yüceltme/süs |
| 26 | El-Müzill | 770 | | (dikkatli konumlandır) |
| 27 | Es-Semî' | 180 | | Ses/çeşme öğesi |
| 28 | El-Basîr | 302 | alt 112 | Keşif/görüş |
| 29 | El-Hakem | 68 | | Denge/adalet öğesi |
| 30 | El-Adl | 104 | | Simetri/düzen |
| 31 | El-Latîf | 129 | | **Sürpriz hediye kutusu** (kullanıcının fikri) |
| 32 | El-Habîr | 812 | | **Hafıza kartı, keşif/harita** |
| 33 | El-Halîm | 88 | | Sakinlik buff'ı |
| 34 | El-Azîm | 1020 | | Anıtsal yapı (grup) |
| 35 | El-Gafûr | 1286 | | Hata silme/geri alma (grup) |
| 36 | Eş-Şekûr | 526 | | Şükür bonusu, çarpan |
| 37 | El-Aliyy | 110 | | Yükseklik |
| 38 | El-Kebîr | 232 | | Büyük yapı |
| 39 | El-Hafîz | 998 | | **Muhafız + hafıza kartı + koruma kalkanı** (kullanıcının fikri) |
| 40 | El-Mukît | 550 | | Besin/gıda |
| 41 | El-Hasîb | 80 | | Sayaç/istatistik |
| 42 | El-Celîl | 73 | | Görkemli süs |
| 43 | El-Kerîm | 270 | | Cömertlik/hediye |
| 44 | Er-Rakîb | 312 | | Bekçi |
| 45 | El-Mücîb | 55 | | Dilek/dua öğesi |
| 46 | El-Vâsi' | 137 | | Alan genişletme |
| 47 | El-Hakîm | 78 | | **Kalem, kütüphane, tasarım ipucu** |
| 48 | El-Vedûd | 20 | alt 400 | **Dostluk/hediye, arkadaş ziyareti** |
| 49 | El-Mecîd | 57 | | Şeref süsü |
| 50 | El-Bâis | 573 | | Diriltme (grup) |
| 51 | Eş-Şehîd | 319 | | Tanıklık/rozet |
| 52 | El-Hakk | 108 | | Gerçek/pusula |
| 53 | El-Vekîl | 66 | | Otomasyon/koruma |
| 54 | El-Kaviyy | 116 | 116/117 | Güç/dayanıklılık |
| 55 | El-Metîn | 500 | | Sağlamlaştırma |
| 56 | El-Veliyy | 46 | | Dostluk/koruma |
| 57 | El-Hamîd | 62 | | Övgü/çiçek |
| 58 | El-Muhsî | 148 | | Sayaç/koleksiyon |
| 59 | El-Mübdî | 57 | 56/57 | Yeni başlatma |
| 60 | El-Muîd | 124 | | Yenileme/geri getirme |
| 61 | El-Muhyî | 68 | | **Canlandırma — solmuş bitkiyi diriltir** |
| 62 | El-Mumît | 490 | | (dikkatli; hasat/döngü) |
| 63 | El-Hayy | 18 | | Canlılık/yeşillik |
| 64 | El-Kayyûm | 156 | | Kalıcılık/bakım |
| 65 | El-Vâcid | 14 | | Bulma/keşif |
| 66 | El-Mâcid | 48 | | Şeref süsü |
| 67 | El-Vâhid | 19 | | Birlik/merkez |
| 68 | Es-Samed | 134 | | Dayanıklı yapı |
| 69 | El-Kâdir | 305 | | Güç/inşa |
| 70 | El-Muktedir | 744 | | Büyük güç (grup) |
| 71 | El-Mukaddim | 184 | | Hızlandırma |
| 72 | El-Muahhir | 847 | 846/847 | Erteleme/zamanlama |
| 73 | El-Evvel | 37 | | Başlangıç bonusu |
| 74 | El-Âhir | 801 | | Tamamlama (grup) |
| 75 | Ez-Zâhir | 1106 | | Görünürlük (grup) |
| 76 | El-Bâtın | 62 | | Gizli hazine |
| 77 | El-Müteâlî | 551 | | Yücelik |
| 78 | El-Vâlî | 47 | | Yönetim/bakım |
| 79 | El-Berr | 202 | | İyilik/bereket |
| 80 | Et-Tevvâb | 409 | | Geri dönüş/tövbe öğesi |
| 81 | El-Müntekim | 630 | | (dikkatli konumlandır) |
| 82 | El-Afüvv | 156 | | Affetme/temizleme |
| 83 | Er-Raûf | 287 | 286/287 | Şefkat buff'ı |
| 84 | Mâlikü'l-Mülk | 212 | | Tapu/arazi |
| 85 | Zü'l-Celâli ve'l-İkrâm | 1100 | 1098/1100 | Görkem + ikram (grup) |
| 86 | El-Muksit | 209 | | Denge/adalet |
| 87 | El-Câmi' | 114 | | Toplama/koleksiyon |
| 88 | El-Ganî | 1060 | | Hazine, bolluk (grup) |
| 89 | El-Muğnî | 1100 | | Zenginlik (grup) |
| 90 | El-Mâni' | 161 | | Kalkan/engel |
| 91 | Ed-Dârr | 1001 | | (dikkatli konumlandır) |
| 92 | En-Nâfi' | 201 | | Fayda/verim |
| 93 | En-Nûr | 256 | | **Işık, kandil, elektrik** (kullanıcının fikri) |
| 94 | El-Hâdî | 20 | alt 400 | Rehber/harita işareti |
| 95 | El-Bedî' | 86 | | **Eşsiz/nadir tasarım öğeleri** |
| 96 | El-Bâkî | 113 | | Kalıcılık |
| 97 | El-Vâris | 707 | | Miras/koleksiyon |
| 98 | Er-Reşîd | 514 | | Rehberlik/ipucu |
| 99 | Es-Sabûr | 298 | | Sabır/uzun vadeli bonus |

**El-Cemîl ve Eş-Şâfî notu**: "Cemîl" (güzellik/süsleme) ve "Şâfî" (şifa bitkileri) tematik olarak ideal olsa da **standart 99'luk listede yer almazlar** (Şâfî, hadis/dua literatüründe ve Risale-i Nur'da geçer). "Genişletilebilir item havuzu"na eklenebilirler; ancak "esma zikri" olarak sunulurken bunun 99 dışı olduğu dikkatle konumlandırılmalı.

### 6c. MVP başlangıç seti (öneri: 10 zikir/esma)
Düşük ebcedli, anlamı görsele kolay çevrilen, çocuk dostu:
- **El-Vedûd (20)** → dostluk/hediye, **El-Muhyî (68)** → canlandırma, **El-Hakîm (78)** → kalem/kitap, **El-Melik (90)** → köşk, **El-Latîf (129)** → sürpriz kutusu, **Es-Selâm (131)** → huzur, **El-Alîm (150)** → kütüphane, **El-Kuddûs (170)** → su, **En-Nûr (256)** → ışık/kandil, **Er-Rezzâk (308)** → meyve.
- Yüksek ebcedli isimler (998, 1020, 1286...) çocuklar için **grup/aile hedefi** veya **parçalı ilerleme** (günde X, haftada tamamla) olarak sunulmalı — asla tek oturumda beklenmemeli.

### 6d. Oyun ekonomisi ve ilerleme
- **Hava/oksijen mekaniği cezalandırıcı olmamalı**: Tevhid zikri havayı artırır; yokluğu bahçeyi "öldürmemeli", yalnızca yavaşlatır/soldurur (geri dönülebilir). Finch'in şefkat modeli esas alınmalı.
- Kaynak türleri: Hava (tevhid), Su/bereket (hamd/istiğfar), Işık (Nûr), Rızık (Rezzâk). Alan açma (Fettâh), koleksiyon, nadir itemlar.
- Günlük vird + **seri (streak)** — ama **streak-freeze** ile suçluluk azaltılmalı (Finch ve Dhikr uygulamasının doğruladığı model).

### 6e. Rekabet ve sosyal (riya hassasiyetiyle)
- Klasik bireysel liderlik tablosu yerine: **aile/sınıf/cami grupları, ortak hedefler (kollektif hatim/zikir halkası), arkadaş bahçesi ziyareti ve hediye**. "Toplam ümmet bahçesi" gibi işbirlikçi hedefler.
- Bireysel sıralama olacaksa **opsiyonel/gizlenebilir** olmalı (varsayılan kapalı).

### 6f. Öğretici katman
Her zikir/esma için: anlam, fazilet, kaynak (hadis no), çocuk dostu kısa anlatım + sahih sesli telaffuz.

---

## 7. DİNİ/İTİKADİ HASSASİYETLER VE DANIŞMANLIK

- **İbadetin oyunlaştırılması & ihlas/riya**: En büyük teolojik risk. Riya klasik âlimlerce (Gazâlî) "gizli şirk" ve kalbin en tehlikeli hastalıklarından sayılır; ödül-odaklılık niyeti bozabilir. Dengeleyici gerçekler: (a) çocuk pedagojisinde ödül meşru bir **başlangıç** motivasyonudur; (b) hadislerin kendisi zikre cennet ağacı "ödülü" vaat eder — yani ödül anlatımı naslarla uyumludur. Âlimlerin ortak tavsiyesi: riya araya girse bile ameli terk etme, niyeti tazele. **Tasarım çözümü**: oyunu "ibadetin kendisi" değil "**hatırlatıcı/alışkanlık aracı**" olarak konumlandır; niyet hatırlatmaları ("Bunu Allah için söyle"), gizli/kişisel worship vurgusu, işbirlikçi (rekabetsiz) yapı.
- **Cennet tasviri**: "Hiçbir gözün görmediği" (Buhârî/Müslim) hadisi gereği oyun **"cennetin kendisi" değil sembolik/temsili bahçe** olarak adlandırılmalı. İsim/söylem önerisi: "Zikir Bahçesi", "Cennet Fidanları" — "Cennetini kur" yerine "**Cennetine fidan dik**" gibi metaforik dil. Açılışta "Bu bir temsildir; gerçek cennet tasavvurun ötesindedir" notu.
- **Tasvir yasakları**: Peygamber/melek/insan tasvirinden kaçın; canlı tasvirinde ihtiyatlı ol (stilize kuş/kelebek çoğu pazarda kabul görür, farklı pazarlarda ayarlanabilir). Allah lafzı ve esmalar saygılı kullanılmalı — **item olarak yere düşen/üzerine basılan öğede lafız bulunmamalı**.
- **Mikrofon açıkken müzik**: Hem teknik (gürültü → tanıma hatası) hem dini açıdan sorunlu. Ambiyans olarak **doğa/su sesi** tercih edilmeli; müzik opsiyonel/kapatılabilir olmalı.
- **Ebced/esma zikir adetleri ihtilafı**: Tasavvufi/havas gelenek kaynaklı (Bûnî, *Şemsü'l-Maârif*); selefi ve kimi kurumsal görüşler bunu eleştirir; Diyanet/TDV çizgisi zikirde **niyet, ihlâs ve süreklilik** vurgular, belirli ebced sayısını farz/şart saymaz (bir din görevlisi kaynağı bunu "bidat denilemez ama şart da değil, sayılar yuvarlanabilir" diye özetliyor). **Tasarım çözümü: ebced mekaniği opsiyonel/ayarlanabilir olsun** — Türkiye/tasavvufi pazarda "ebced modu" açık, Körfez/selefi pazarda "serbest sayı modu"na geçilebilsin.
- **Danışma kurulu**: Farklı ekollerden ilahiyatçı + pedagog + çocuk psikoloğu. Onay/mühür için: Diyanet ve yerel fetva kurumları; uluslararası için tanınmış âlim onayları (Tarteel'in âlim danışmanlığı modeli izlenebilir).

---

## 8. GEREKLİ / YARARLI HER ŞEY

- **Geliştirme hızlandırıcılar**: Picovoice SDK (KWS), WhisperKit/whisper.cpp (ASR yedek), Tarteel **everyayah** veri seti (fine-tune), Unity/Godot AI eklentileri, hazır asset kütüphaneleri (Kenney/Quaternius CC0, Synty), AI 3D (Meshy/Tripo/Rodin).
- **Ses tasarımı**: Mikrofon açıkken echo/geri besleme için **AEC (akustik yankı bastırma)** ve gürültü bastırma; zikre eşlik eden su/kuş/rüzgâr ambiyansı; her tanınan zikirde **haptik geri bildirim** (titreşim).
- **Erişilebilirlik & çoklu dil**: Türkçe, Arapça, İngilizce, Endonezce, Urduca, Fransızca, Almanca; **RTL desteği**; sesli/görsel/dokunsal çoklu geri bildirim (Esmaül Hüsna uygulamalarının çoklu dil desteği bir emsal).
- **Ebeveyn paneli**: Ekran süresi sınırı, **namaz vakitlerinde otomatik duraklatma**, ilerleme raporu, içerik/mod seçimi (ebced açık/kapalı).
- **Hukuki**: App Store/Play Kids/Families politikaları, COPPA/GDPR-K/KVKK/UK Children's Code, ABD LLC (PARLADOR) üzerinden yayın, marka tescili. İsimde dikkat: "Cennet/Jannah" kelimelerinin ticari kullanımında hassasiyet + küresel telaffuz kolaylığı.
- **Fonlama**: 
  - **LaunchGood** (2013 kuruluşu, dünyanın en büyük Müslüman kitle fonlama platformu; ödül-temelli girişim kampanyaları + AMCC bağlantısı).
  - **HASAN.VC** (Ethis Group, Umar Munshi): "five-week online programme ... up to US$60,000 (RM253,000) in pre-seed funding ... network of over 500 angel investors"; Cohort 001'de 42, Cohort 002'de 29 startup ağırladı, 20'si fon aldı, Güneydoğu Asya odaklı.
  - **Salam Fund, Ethis, Gobi Partners** (Muslim Pro'yu fonladı), **Goodforce Labs** (Dubai, İslami ekonomi hızlandırıcısı); vakıf/hayır destekleri; okul/kurum lisansı geliri.

### Riskler ve karşı önlemler
| Risk | Etki | Karşı önlem |
|---|---|---|
| Arapça KWS'nin Porcupine'da doğrudan desteklenmemesi | Yüksek | Özel KWS eğitimi (Sherpa-ONNX/openWakeWord); **prototipte ilk test** |
| Çocuk sesi + aksan tanıma düşük doğruluk | Yüksek | Çok-aksanlı + çocuk veri seti; dokunmatik yedek daima açık |
| Riya/oyunlaştırma teolojik eleştiri | Yüksek | Danışma kurulu; "hatırlatıcı" konumlandırma; rekabetsiz/işbirlikçi tasarım; niyet hatırlatıcıları |
| Ebced'in bazı pazarlarda reddi | Orta | Opsiyonel/ayarlanabilir mod (ebced ↔ serbest sayı) |
| Çocuk gizliliği ihlali (mikrofon) | Yüksek | On-device işleme; 3P SDK yasağı; ebeveyn onayı |
| Reklam modeli COPPA/Families riski | Orta-Yüksek | Reklamsız; abonelik + kozmetik gelir |
| Cennet tasviri hassasiyeti | Orta | Sembolik dil; tasvir yasaklarına uyum; lafız kullanımına özen |
| Yüksek asset üretim maliyeti | Orta | AI 3D (Meshy/Tripo) + CC0 kütüphaneler |
| Rakiplerin (Dhikr, Tarteel) benzer özellik eklemesi | Orta | Hız + özgün "cennet bahçesi" IP'si + PARLADOR sanat kimliği |

---

## SOMUT MVP ÖNERİSİ VE AŞAMALI YOL HARİTASI

**MVP kapsamı (dar, kanıtlanabilir çekirdek)**:
- Tek başlangıç adası/bahçe
- 10 zikir/esma (Bölüm 6c seti): La ilahe illallah = hava, salavat = gül, SubhanAllah = ağaç çekirdek + 7 düşük-ebcedli esma
- **On-device KWS** (önce 5-6 ifade), dokunmatik yedek daima açık
- Şefkat temelli, **cezasız** ekonomi; günlük vird + streak-freeze
- Öğretici kartlar (anlam/fazilet/kaynak/telaffuz)
- Ebeveyn paneli + namaz vakti duraklatma
- **Reklamsız**; başta ücretsiz + ileride kozmetik/abonelik
- Ebced modu opsiyonel

**Aşamalı yol haritası**:
1. **Prototip (0-3 ay)** — *Teknik risk kırma*: Arapça zikir KWS doğruluk testi (**en kritik iş**; Türk/Arap/çocuk sesleriyle). Tek zikir → tohum → ağaç döngüsü. Motor kararı (Unity vs Godot). Danışma kurulu çekirdeği kurulur.
2. **MVP (3-9 ay)**: 10 zikir, bahçe inşası, öğretici, ebeveyn paneli, çoklu dil temeli (TR/AR/EN), danışma kurulu onayı.
3. **Soft launch (9-12 ay)**: Türkiye + Endonezya/Malezya pilot; **Ramazan zamanlaması**; İslami influencer + Kur'an kursu/cami kanalları; LaunchGood kampanyası.
4. **Global (12-18 ay)**: Tam çoklu dil, sosyal/grup özellikleri (Nakama), aile/okul lisansı, ebced opsiyonel modu, item havuzu genişletme.

**Bütçe/ekip notu (aralık tahmini, kesinleştirilecek)**: Prototip tek geliştirici + AI-destekli araçlarla düşük maliyetle mümkün; MVP için ideal çekirdek 1 geliştirici + 1 part-time sanat/3D + danışma kurulu (dönemsel). Ana maliyet kalemleri: özel KWS veri toplama, sanat üretimi, hukuki/uyum. Rakamlar hedef pazar ve motor kararına bağlı; Açık Soru #2, #3, #7 netleşince modellenmeli.

---

## BİRLİKTE KARAR VERMEMİZ GEREKEN AÇIK SORULAR
1. **Hedef yaş**: Sadece çocuklar mı (7-12), yoksa gençler/yetişkinler de mi? Mikrofon/gizlilik yükünü ve tasarım tonunu belirler.
2. **Motor**: Unity (güvenli/ölçekli mobil) mi, Godot 4.x (AI-destekli tek kişi geliştirmeye çok uygun) mi?
3. **Sesli tanıma stratejisi**: Hazır (Picovoice — Arapça doğrulanmalı) mı, özel KWS eğitimi mi? İlk teknik prototip tam olarak neyi ölçsün (hangi ifadeler, hangi aksanlar, hedef doğruluk %)?
4. **Rekabet felsefesi**: Hiç bireysel sıralama olmasın mı, yoksa opsiyonel/varsayılan-kapalı mı?
5. **Ebced mekaniği**: Varsayılan açık mı, opsiyonel mi? Hangi pazarda hangi mod?
6. **Konumlandırma/isim**: "Cennet" kelimesi kullanılsın mı, yoksa tamamen metaforik ("Zikir Bahçesi") mi?
7. **Gelir modeli**: Baştan abonelik mi, önce ücretsiz büyüme + sonra kozmetik mi? Vakıf/bağış (LaunchGood) devrede mi?
8. **İlk pazar**: Türkiye öncelikli mi, yoksa Endonezya/Malezya (en büyük Müslüman mobil pazar) mı?
9. **Danışma kurulu**: Hangi ekol(ler)den âlim? Diyanet onayı hedefleniyor mu?
10. **Tasvir politikası**: Canlı (kuş/kelebek) tasvirinde sınır nerede; pazara göre değişken mi?

---
*Notlar: Ebced değerleri tasavvufi/havas geleneğine ait yaygın kabul gören sayılardır, farz adet değildir; kaynaklar arası 1-2 puan farklar tabloda işaretlenmiştir. Cozy game pazar rakamları kaynaklar arası farklılık gösterdiğinden ihtiyatla kullanılmalıdır. Porcupine'ın Arapça desteklemediği bilgisi prototipte doğrulanmalı; bu, projenin en kritik teknik varsayımıdır.*