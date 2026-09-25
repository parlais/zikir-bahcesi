#!/bin/bash
# Cennet sahnesinden kısa film: her kare sabit zaman adımıyla ilerler (--fixed-fps), yavaş
# yazılım render'ında da akış hızı doğru çıkar. Kareler <önek>_000.png ... olarak yazılır.
# Kullanım: tools/render/film.sh <stil> <kamera> <genişlikxyükseklik> <önek> [ek argümanlar]
#   ek argümanlar: --zb-film-kare=48 (kare sayısı), --zb-isinma=16, --zb-isik=0.5, --zb-ayar=...
#   Kare hızı FPS ortam değişkeniyle (varsayılan 24).
# Örnek:  tools/render/film.sh nur_ori selale 640x360 /tmp/film/selale --zb-isik=0
#         python3 tools/render/pano.py gif /tmp/selale.gif --sure 42 --bekle 42 /tmp/film/selale_*.png
# Süre: 640x360, 48 kare ~4 dk.
KOK="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$KOK" || exit 1
mkdir -p "$(dirname "$4")"
VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.json xvfb-run -a -s "-screen 0 1920x1080x24" \
  godot --audio-driver Dummy --path game --rendering-method forward_plus --rendering-driver vulkan \
  --fixed-fps "${FPS:-24}" --resolution "$3" res://scenes/dunya/cennet_sahnesi.tscn -- --zb-anim="$1" \
  --zb-kamera="$2" --zb-film="$4" "${@:5}" > "$4.log" 2>&1
grep -iE "SCRIPT ERROR|SHADER ERROR|Parse Error" "$4.log" | head -5
grep "Film karesi" "$4.log" | tail -2
