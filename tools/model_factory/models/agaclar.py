"""Dallanan ağaçlar (K15): türlerin iskelet ve yaprak parametreleri.

Üreteç mf/agac.py'de, yaprak atlasları mf/doku.py'dedir. Her tür için:
  - yaprak kümesi dokusu (YaprakTuru): yaprak biçimi ve renkleri
  - ağaç (AgacTuru): gövde, dal seviyeleri, yaprak kartlarının dizilişi
"""
from __future__ import annotations

import math

import numpy as np

from mf.agac import AgacTuru, Seviye, YaprakAyar, agac, meyve_yerleri
from mf.doku import YaprakTuru, yaprak_turu
from mf.mesh import cone, icosphere, lathe, merge, tube
from mf.scene import Node

# --------------------------------------------------------------------------
# Yaprak dokuları
# --------------------------------------------------------------------------

# Rahmân 64 (müdhâmmetân): koyu yeşil, dolgun; parlak, yumurta biçimli yapraklar
yaprak_turu(YaprakTuru("koru", [(52, 118, 62), (62, 130, 68), (74, 142, 70), (46, 110, 72)], boy=(0.15, 0.21),
                       en=0.46, uc=1.2, dip=0.75, sayi=34, yan_dal=3, renk_oynama=0.07, sarimsi_uc=0.04, tohum=1))

# Sidr (Ali Ünal: "dal bastı kirazlar"): kiraz yaprağı gibi sivri uçlu, dişli, parlak yeşil
yaprak_turu(YaprakTuru("sidr", [(92, 156, 70), (108, 170, 76), (80, 142, 62), (120, 176, 80)], boy=(0.16, 0.22),
                       en=0.44, uc=1.35, dip=0.6, testere=0.07, dis_sayi=22, sayi=30, yan_dal=2, tohum=2))
# Nar (Rahmân 68): dar, parlak, kümeler hâlinde yapraklar
yaprak_turu(YaprakTuru("nar", [(78, 146, 58), (96, 160, 60), (112, 170, 64), (70, 132, 54)], boy=(0.11, 0.16),
                       en=0.26, uc=0.9, dip=0.9, sayi=46, yan_dal=3, aci=(25.0, 60.0), kivrim=0.15, parlak=0.14,
                       tohum=3))
# Selvi: pul yapraklı, tüy gibi yassı sürgünler
yaprak_turu(YaprakTuru("selvi", [(44, 92, 58), (52, 104, 62), (38, 82, 52)], boy=(0.065, 0.095), en=0.55, uc=0.8,
                       dip=0.5, sayi=300, yan_dal=8, yan_aci=(35.0, 75.0), yan_boy=(0.3, 0.46), aci=(20.0, 45.0),
                       sap=0.0, dal_renk=(70, 90, 56), parlak=0.05, kivrim=0.05, sarimsi_uc=0.02, tohum=4))


# --------------------------------------------------------------------------
# Türler
# --------------------------------------------------------------------------

KORU = AgacTuru(
    boy=8.0, govde_r=0.38, govde_uc=0.16, govde_egim=4.0, kok=0.8, kok_lob=5,
    kabuk_renk=(150, 134, 116), kabuk_renk_uc=(128, 118, 90), tohum=51,
    # Korular kameradan en az 70-80 m uzaktadır: en ince dal seviyesi yerine büyük yaprak
    # kümeleri ve öz hacim (sahnede yüzlerce örnek var).
    seviyeler=[
        Seviye(sayi=10, bas=0.38, son=0.97, aci=56, aci_sapma=12, uzunluk=0.62, sekil="kure", egim=0.3,
               kivrim=0.35, yaricap=0.6, uc=0.22, segment=7, adim=0.7),
        Seviye(sayi=9, bas=0.18, son=1.0, aci=50, aci_sapma=15, uzunluk=0.55, sekil="konik", egim=0.12,
               kivrim=0.45, yaricap=0.58, uc=0.3, segment=4, adim=0.8),
    ],
    yaprak=YaprakAyar("yaprak_koru", seviyeler=(2,), siklik=2.0, bas=0.25, boy=(1.5, 2.0), en=0.95,
                      disa=0.7, yukari=0.35, golge=0.42, alt_golge=0.25, oz=0.5, oz_renk=(44, 98, 56)),
)

# Sidr (Vâkıa 28): 5-6 m, şemsiye gibi yayılan taç; ince dallar kiraz yüküyle sarkar
SIDR = AgacTuru(
    boy=3.2, govde_r=0.21, govde_uc=0.3, govde_egim=7.0, kok=0.55, kok_lob=4, kok_boy=2.5,
    kabuk_renk=(138, 112, 100), kabuk_renk_uc=(128, 104, 84), tohum=13,
    seviyeler=[
        Seviye(sayi=7, bas=0.5, son=1.0, aci=64, aci_sapma=10, uzunluk=1.12, sekil="yarim_kure", egim=0.5,
               kivrim=0.35, yaricap=0.72, uc=0.25, segment=7, adim=0.4),
        Seviye(sayi=7, bas=0.2, son=1.0, aci=50, aci_sapma=14, uzunluk=0.55, sekil="konik", egim=-0.55,
               kivrim=0.4, yaricap=0.6, uc=0.3, segment=5, adim=0.35),
        Seviye(sayi=4, bas=0.3, son=1.0, aci=45, aci_sapma=15, uzunluk=0.5, sekil="konik", egim=-0.7,
               kivrim=0.45, yaricap=0.55, uc=0.4, segment=3, adim=0.4),
    ],
    yaprak=YaprakAyar("yaprak_sidr", seviyeler=(2, 3), siklik=3.0, bas=0.3, boy=(0.65, 0.9), en=0.95,
                      disa=0.65, yukari=0.2, golge=0.4, alt_golge=0.25),
)

# Nar (Rahmân 68): 4-5 m, dipten çatallanan birkaç gövde, sık ve yuvarlak taç
NAR = AgacTuru(
    boy=0.9, govde_r=0.17, govde_uc=0.6, govde_egim=4.0, kok=0.35, kok_lob=4, kok_boy=2.0,
    kabuk_renk=(140, 120, 106), kabuk_renk_uc=(128, 112, 86), tohum=21,
    seviyeler=[
        Seviye(sayi=4, bas=0.4, son=0.95, aci=24, aci_sapma=8, uzunluk=3.6, sekil="silindir", egim=0.1,
               kivrim=0.4, yaricap=0.75, uc=0.3, segment=6, adim=0.35),
        Seviye(sayi=12, bas=0.38, son=1.0, aci=50, aci_sapma=14, uzunluk=0.36, sekil="kure", egim=0.15,
               kivrim=0.5, yaricap=0.55, uc=0.35, segment=4, adim=0.35),
        Seviye(sayi=5, bas=0.25, son=1.0, aci=45, aci_sapma=15, uzunluk=0.5, sekil="konik", egim=-0.1,
               kivrim=0.5, yaricap=0.55, uc=0.4, segment=3, adim=0.4),
    ],
    yaprak=YaprakAyar("yaprak_nar", seviyeler=(2, 3), siklik=5.0, bas=0.2, boy=(0.7, 1.0), en=0.95,
                      disa=0.6, yukari=0.3, golge=0.4, alt_golge=0.25),
)

# Selvi (vahdet sembolü): 9 m, alev gibi dimdik; gövde tepeye kadar çıkar, kısa dallar yukarı bakar
SELVI = AgacTuru(
    boy=8.8, govde_r=0.2, govde_uc=0.06, govde_egim=1.0, govde_kivrim=0.05, kok=0.4, kok_lob=4,
    kabuk_renk=(132, 108, 92), kabuk_renk_uc=(110, 100, 74), tohum=6,
    seviyeler=[
        Seviye(sayi=60, bas=0.05, son=1.0, aci=50, aci_sapma=8, uzunluk=0.15, sekil="mizrak", egim=0.45,
               kivrim=0.2, yaricap=0.5, uc=0.3, segment=4, adim=0.35, yukari=0.15),
        Seviye(sayi=4, bas=0.25, son=1.0, aci=30, aci_sapma=10, uzunluk=0.55, sekil="konik", egim=0.25,
               kivrim=0.3, yaricap=0.55, uc=0.4, segment=3, adim=0.4),
    ],
    yaprak=YaprakAyar("yaprak_selvi", seviyeler=(1, 2), siklik=5.5, bas=0.1, boy=(0.6, 0.9), en=0.85,
                      disa=0.6, yukari=0.45, bukum=0.08, golge=0.45, alt_golge=0.1, dis_normal=0.85),
)

# Uzak ağaç: yüzlerce metre ötedeki korular için korunun hafif hâli. Aynı yaprak atlası,
# iki dal seviyesi, büyük kartlar; uzaktan korularla aynı dokuyu ve silueti verir.
UZAK = AgacTuru(
    boy=6.0, govde_r=0.3, govde_uc=0.2, govde_egim=4.0, govde_segment=5, govde_adim=1.5, kok=0.0,
    kabuk_renk=(150, 134, 116), kabuk_renk_uc=(128, 118, 90), tohum=61,
    seviyeler=[
        Seviye(sayi=7, bas=0.42, son=0.97, aci=52, aci_sapma=12, uzunluk=0.62, sekil="kure", egim=0.3,
               kivrim=0.3, yaricap=0.6, uc=0.25, segment=3, adim=1.5),
        Seviye(sayi=3, bas=0.3, son=1.0, aci=50, aci_sapma=15, uzunluk=0.5, sekil="konik", egim=0.1,
               kivrim=0.4, yaricap=0.58, uc=0.3, segment=3, adim=2.0),
    ],
    yaprak=YaprakAyar("yaprak_koru", seviyeler=(2,), siklik=0.9, bas=0.3, boy=(2.6, 3.4), en=1.0,
                      disa=0.7, yukari=0.35, golge=0.42, alt_golge=0.25, uc_kumesi=(0,), oz=0.62,
                      oz_renk=(44, 98, 56)),
)


def agac_modeli(ad: str, tur: AgacTuru, **kw) -> Node:
    kabuk, yapraklar, _, _ = agac(tur, **kw)
    return Node(ad).add(kabuk, *yapraklar)


def selvi_modeli(ad: str) -> Node:
    """Selvi: kartların içinde koyu bir öz hacim; sütun sık ve koyu görünür, aralardan gök
    görünmez. Öz, kartların yükseklik dilimlerindeki yarıçapının %60'ıdır."""
    kabuk, yapraklar, _, ruzgar = agac(SELVI)
    V = yapraklar[0].V
    y0, y1 = 1.0, float(V[:, 1].max()) - 1.1
    prof = []
    for y in np.linspace(y0, y1, 16):
        dilim = V[np.abs(V[:, 1] - y) < 0.4]
        r = float(np.percentile(np.linalg.norm(dilim[:, [0, 2]], axis=1), 70)) if len(dilim) > 8 else 0.1
        prof.append((max(r * 0.62, 0.05), y))
    prof = [(0.0, y0 - 0.2)] + prof + [(0.0, y1 + 0.2)]
    oz = lathe(prof, 10, "selvi").jitter(0.04, 61).smooth(70).eksen_normal(dikey=0.3).with_material("yaprak")
    oz.W = ruzgar(oz.V).astype(np.float32) * 0.5
    return Node(ad).add(kabuk, *yapraklar, oz)


def _kirazlar(yerler, ruzgar, tohum):
    """Sapları dala bağlı, çift çift sarkan kirazlar."""
    rng = np.random.default_rng(tohum)
    parca = []
    for p, tn, r in yerler:
        yan = np.cross(tn, [0.0, 1.0, 0.0])
        yan = yan / (np.linalg.norm(yan) + 1e-9)
        q = p + np.array([rng.uniform(-0.03, 0.03), -rng.uniform(0.12, 0.17), rng.uniform(-0.03, 0.03)])
        for k, s_ in enumerate((-1, 1)):
            uc = q + yan * s_ * 0.035 + np.array([0, rng.uniform(-0.02, 0.01), 0])
            parca.append(tube([p, (p + uc) / 2 + yan * s_ * 0.01 + np.array([0, 0.02, 0]), uc],
                              [0.006, 0.005, 0.004], 3, "govde_acik", cap=False))
            parca.append(icosphere(rng.uniform(0.045, 0.055), 0, "kiraz" if (k + len(parca)) % 3 else "kiraz_koyu")
                         .scale(1.0, 0.92, 1.0).translate(*(uc + np.array([0, -0.04, 0]))).smooth(70))
    m = merge(*parca).with_material("meyve").paylasimli()
    m.W = ruzgar(m.V).astype(np.float32)
    return m


def _narlar(yerler, ruzgar, tohum):
    """Saplı, taçlı narlar: tacı (kaliks) aşağı bakar."""
    rng = np.random.default_rng(tohum)
    parca = []
    for p, tn, r in yerler:
        b = rng.uniform(0.07, 0.095)
        m = p + np.array([rng.uniform(-0.04, 0.04), -b * 1.3, rng.uniform(-0.04, 0.04)])
        parca.append(tube([p, m + np.array([0, b * 0.9, 0])], [0.01, 0.008], 3, "govde", cap=False))
        parca.append(icosphere(b, 1, "nar" if rng.random() < 0.7 else "nar_koyu").scale(1.0, 0.9, 1.0)
                     .translate(*m).smooth(70))
        parca.append(cone(b * 0.35, b * 0.45, 6, "nar_koyu").rotate("x", 180).translate(m[0], m[1] - b * 0.8, m[2]))
    m = merge(*parca).with_material("meyve").paylasimli()
    m.W = ruzgar(m.V).astype(np.float32)
    return m


def sidr_modeli(ad: str, olgun: bool) -> Node:
    if olgun:
        kabuk, yapraklar, dallar, ruzgar = agac(SIDR)
        meyve = _kirazlar(meyve_yerleri(dallar, (3,), 70, 131), ruzgar, 132)
        return Node(ad).add(kabuk, *yapraklar, meyve)
    kabuk, yapraklar, _, _ = agac(SIDR, olcek=0.4, seviye_sayisi=2)
    return Node(ad).add(kabuk, *yapraklar)


def nar_modeli(ad: str) -> Node:
    kabuk, yapraklar, dallar, ruzgar = agac(NAR)
    return Node(ad).add(kabuk, *yapraklar, _narlar(meyve_yerleri(dallar, (2, 3), 16, 211), ruzgar, 212))
