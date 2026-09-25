#!/bin/bash
# Cennet sahnesinden ekran görüntüsü (Forward+, GPU'suz ortamda Mesa lavapipe ile).
# Kullanım: tools/render/cek.sh <stil> <kamera> <genişlikxyükseklik> <kare> <çıktı.png> [ek argümanlar]
#   stil: nur_ori | nur | sky | pixar | yagli_boya      kamera: ufuk | arsa | kesit
#   ek argümanlar sahneye geçer, ör. --zb-isik=0.5 ya da --zb-ayar="ortam/parlama/0=0.2"
# Örnek:  tools/render/cek.sh nur ufuk 800x450 16 /tmp/nur_ufuk.png
#         tools/render/cek.sh nur_ori ufuk 800x450 16 /tmp/gecis_05.png --zb-isik=0.5
# Süre: 640x360 8 kare ~1,5 dk; 800x450 16 kare ~5 dk (üç çekim paralel çalışabilir).
KOK="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$KOK" || exit 1
VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.json xvfb-run -a -s "-screen 0 1920x1080x24" \
  godot --audio-driver Dummy --path game --rendering-method forward_plus --rendering-driver vulkan \
  --resolution "$3" res://scenes/dunya/cennet_sahnesi.tscn -- --zb-anim="$1" --zb-kamera="$2" \
  --zb-ekran="$5" --zb-kare="$4" "${@:6}" > "${5%.png}.log" 2>&1
grep -iE "SCRIPT ERROR|SHADER ERROR|Parse Error" "${5%.png}.log" | head -5
ls -la "$5"
