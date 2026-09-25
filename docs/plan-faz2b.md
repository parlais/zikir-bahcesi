# Faz 2b — Taslak plan (kullanıcı onayı bekliyor)

Faz 2a'da mekân ve ışık yönü netleşti:
- **Mekân (K10):** uçsuz bucaksız 8 yatay tabaka.
- **Işık (K12):** Nur ile Ori arasında değişen ışık.

Bu belge sıradaki işleri toplar. Yeni oturum önce bunu kullanıcıya kısaca özetler, öncelik ve kapsam için onay alır.

## 1. Işık geçişi: Nur ↔ Ori (K12)
- `animasyon_stilleri.gd` içindeki `nur` ve `sky` profilleri iki uç durumdur. Bir karıştırıcı bunları zamanla yumuşakça birbirine geçirir.
  - Karıştırılacaklar: gök uniform'ları, Environment (sis, parıltı, ambient, pozlama, doygunluk), ana ışığın yönü, rengi ve enerjisi, malzeme uniform'ları, bulut ve parçacık renkleri.
  - Sayılar lerp, renkler Color.lerp, yönler slerp ile karışır.
- Öneri: `game/scenes/dunya/isik_karistirici.gd`.
  - Profil sözlüklerini bir `t` (0 Nur, 1 Ori) ile karıştırır ve SahneKurucu'nun kurduğu nesneleri günceller.
  - Karıştırma fonksiyonu Godot'a bağlı olmamalı ve test edilmeli.
- Kullanıcıya sorulacak: Geçiş neye bağlı olsun (zaman, zikir, olay, seçim)? Ne sıklıkla olsun, ne kadar sürsün?
- Doğrulama: `t` = 0, 0.5 ve 1'de üç çekim; ayrıca kısa bir geçiş dizisi (kare dizisi).

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
- **Canlılık:** Kuşlar ve kelebekler (sade kanat çırpan billboard'lar ya da basit modeller).

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
