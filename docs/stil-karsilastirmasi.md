# Stil karşılaştırması (2026-09-24)

İlk dilimdeki küçük ada ve soluk arayüz yerine büyük bir çarbağ bahçesi kuruldu. Aynı sahne dört farklı görsel yönde çekildi. Amaç stil seçmek; bu görüntüler son kalite değildir.

| Stil | His | Işık | Arayüz |
| --- | --- | --- | --- |
| **Nur** | Ruhani, sakin | Altın saat, karşıdan gelen güneş, nur zerreleri | Fildişi cam, altın halka, Marcellus yazı |
| **Boyalı** | Ghibli, sıcak, neşeli | Öğle, parlak gök, çizgi film gölge geçişi | Krem kâğıt, yeşil ve mercan |
| **Mücevher** | Osmanlı gecesi, büyülü | Ay ışığı, yanan kandiller, parlayan su ve çini | Lacivert ve altın, tezhip süsü |
| **Fantastik-gerçekçi** | Genshin ve Zelda arası | Berrak öğleden sonra, derin gölgeler | Koyu cam, beyaz yazı, altın vurgu |

Görüntüler `docs/goruntuler/stil/` altında: her stil için `*_portre.png` (telefon ekranı, arayüzle) ve `*_manzara.png` (bahçenin geniş görünümü).

## Sahnede neler var

- **Bahçe:** 60×60 m çarbağ. Dört su kanalı ortadaki sekizgen havuzda buluşur (Muhammed 15).
- **Yapılar:** kuzeyde yükseltilmiş terasta köşk, ortada şadırvan ve fıskiye, güneyde kapı. Güney, doğu ve batıda çini kuşaklı surlar var.
- **Bitkiler:**
  - 46 selvi, 16 nar ağacı, 40 gül çalısı, 96 şimşir çit parçası, 864 lale
  - on binlerce çimen tutamı, bahçe dışında 170 ağaçlık koruluk
- **Çevre:** tepelik arazi ve karlı dağ halkası.
- **Işık ve atmosfer:** hacimli sis, gerçek zamanlı küresel aydınlatma (SDFGI), su yansıması (SSR), ortam gölgesi (SSAO), parlama (bloom).
- **Shader'lar:**
  - rüzgârla salınan yapraklar, arkadan ışık alan yaprak geçirgenliği
  - sekiz köşeli yıldız çini deseni, kır çiçekli çimen
  - bulutlu gökyüzü ve gece için yıldızlarla hilal

## Yeniden çekmek

```sh
python3 tools/model_factory/build_all.py      # sahne modelleri ve game/data/sahne_carbag.json
godot --headless --path game --import
# Forward+ (Vulkan) gerekir. GPU'suz ortamda Mesa lavapipe ile de çalışır (yavaş).
godot --path game --rendering-method forward_plus --resolution 900x1600 \
  res://scenes/stil/stil_sahnesi.tscn -- --zb-stil=nur --zb-kamera=portre \
  --zb-ekran=/tmp/nur.png --zb-kare=30
```

`--zb-stil` değerleri: `nur`, `ghibli`, `mucevher`, `gercekci`. `--zb-kamera` değerleri: `portre`, `sinematik`.

Profiller `game/scenes/stil/stil_profilleri.gd` dosyasındadır. Işık, gökyüzü, sis, malzeme ve arayüz renkleri tek bir sözlükte durur, bu yüzden stiller karıştırılabilir. Örneğin Nur'un ışığı Mücevher'in arayüzüyle birleştirilebilir.

## Dürüst notlar

- Modeller hâlâ geometrik (doku yok). Seçilen stil netleşince modeller o stile göre yeniden işlenecek: daha fazla ayrıntı, dokular, yumuşak formlar ve el yapımı hissi veren kusurlar.
- Görüntüler GPU'suz bir bulut ortamında, yazılım renderer'ıyla çekildi. Kalite gerçek cihazla aynıdır ama telefonda akıcılık ayrıca ölçülmeli. Bu ayarlar orta-üst seviye telefon hedefler.
