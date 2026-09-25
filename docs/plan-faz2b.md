# Faz 2b — Plan (2026-09-25'te onaylandı)

Faz 2a'da mekân ve ışık yönü netleşti:
- **Mekân (K10):** uçsuz bucaksız 8 yatay tabaka.
- **Işık (K12):** Nur ile Ori arasında değişen ışık.

Bu belge sıradaki işleri toplar.

**Onay (K13):**
- Sıra: önce ışık geçişi (1), sonra kalite (2), sonra mekanikler (3).
- Işık geçişi zikre ve olaylara bağlıdır.
- Canlılar model fabrikasında üretilir.

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
- **Kesit (dış görünüm):**
  - Şema gibi duruyor. Derinlik, ışık ve her katın farklı karakteri güçlenmeli (Rahmân 46-76: üst katlarda çeşitlilik artar).
  - Katlar arası merdivenler seçilir olmalı.
- **Modeller:**
  - Ağaçlar lolipop gibi; taç ve dal ayrıntısı ister.
  - Köşk ve çadırda yakın plan ayrıntısı eksik.
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
