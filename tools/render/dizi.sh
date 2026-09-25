#!/bin/bash
# Nur -> Ori ışık geçişini kare kare çeker (cennet sahnesi, nur_ori kipi; lavapipe).
# Kullanım: tools/render/dizi.sh <kamera> <genişlikxyükseklik> <önek> [ek argümanlar]
#   Kareler <önek>_00.png ... olarak yazılır. Ek argümanlar: --zb-dizi-adim=13 (kare sayısı),
#   --zb-dizi-bekle=3 (kareler arası), --zb-isinma=16 (ilk kareden önce), --zb-ayar=...
# Örnek:  tools/render/dizi.sh ufuk 640x360 /tmp/dizi/ufuk
#         python3 tools/render/pano.py gif /tmp/gecis.gif --gidis-donus /tmp/dizi/ufuk_*.png
# Süre: 640x360, 13 kare ~5 dk.
KOK="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$KOK" || exit 1
mkdir -p "$(dirname "$3")"
VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.json xvfb-run -a -s "-screen 0 1920x1080x24" \
  godot --audio-driver Dummy --path game --rendering-method forward_plus --rendering-driver vulkan \
  --resolution "$2" res://scenes/dunya/cennet_sahnesi.tscn -- --zb-anim=nur_ori --zb-kamera="$1" \
  --zb-dizi="$3" "${@:4}" > "$3.log" 2>&1
grep -iE "SCRIPT ERROR|SHADER ERROR|Parse Error" "$3.log" | head -5
grep "Dizi karesi" "$3.log" | tail -3
