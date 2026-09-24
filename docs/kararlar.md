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
