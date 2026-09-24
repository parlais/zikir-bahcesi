#!/usr/bin/env python3
"""Bütün modelleri üretir: game/assets/models/*.glb

    python3 tools/model_factory/build_all.py            # hepsi
    python3 tools/model_factory/build_all.py kandil     # adında "kandil" geçenler

Her model deterministiktir (tohumlar kodda sabit); aynı kod aynı dosyayı üretir.
Ayrıca asset listesinden (game/data/assets.json) beklenen dosyalarla
karşılaştırıp hangi modellerin henüz yazılmadığını raporlar.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from mf.gltf_export import write_glb  # noqa: E402
from models import load_all  # noqa: E402

OUT = ROOT / "game" / "assets" / "models"
# Asset listesinde olmayan ama sahne için gereken modeller.
EK_MODELLER = {"ZB_zemin_ada", "ZB_sahne_carbag", "ZB_sahne_daglar", "ZB_bitki_selvi", "ZB_bitki_nar",
               "ZB_bitki_gul_cali", "ZB_bitki_simsir", "ZB_bitki_cimen", "ZB_bitki_lale_tarhi"}
# Sahne modelleri tek parça büyük arazidir; üçgen sınırı onlara uygulanmaz.
SINIRSIZ = {"ZB_sahne_carbag", "ZB_sahne_daglar"}
# Ana ağaçlar sahnede az sayıda bulunur; daha dolgun taç için sınır yüksek.
OZEL_SINIR = {"ZB_bitki_nar": 11000}
# Bir modelin üst sınırı: mobilde bahçede onlarca model aynı anda görünür.
UCGEN_SINIRI = 6000


def main(argv):
    filtre = argv[1] if len(argv) > 1 else ""
    reg = load_all()
    toplam = 0
    hatali = []
    for name in sorted(reg):
        if filtre and filtre not in name:
            continue
        node = reg[name]()
        assert node.name == name or name.startswith(node.name), f"Kök düğüm adı dosya adıyla aynı olmalı: {name}"
        node.name = name
        tris = node.tri_count()
        size = write_glb(node, OUT / f"{name}.glb")
        toplam += 1
        sinir = OZEL_SINIR.get(name, UCGEN_SINIRI)
        uyari = "  ÜÇGEN SINIRI AŞILDI" if tris > sinir and name not in SINIRSIZ else ""
        if uyari:
            hatali.append(name)
        print(f"{name:34s} {tris:6d} üçgen {size / 1024:7.1f} KB{uyari}")
    print(f"{toplam} model yazıldı -> {OUT.relative_to(ROOT)}")
    from models.sahne import yerlesim_yaz
    print("Sahne yerleşimi:", yerlesim_yaz(ROOT).relative_to(ROOT))

    beklenen = set(EK_MODELLER)
    for a in json.loads((ROOT / "game/data/assets.json").read_text(encoding="utf-8"))["assets"]:
        beklenen.update(a["modeller"])
    eksik = sorted(beklenen - set(reg))
    fazla = sorted(set(reg) - beklenen)
    print(f"Asset listesi: {len(beklenen)} model, {len(beklenen) - len(eksik)} hazır, {len(eksik)} bekliyor.")
    if fazla:
        print("Listede olmayan modeller:", ", ".join(fazla))
        hatali += fazla
    return 1 if hatali else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
