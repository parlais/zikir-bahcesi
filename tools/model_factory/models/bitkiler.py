"""B bölümü: bitkiler ve büyüme aşamaları (ilk dilim: hurma ve lale).

Aşamalar aynı fonksiyondan gelir; aşama numarası boyu, yaprak sayısını ve
ayrıntıyı belirler. Böylece tohumdan olguna geçiş tutarlıdır.
  Ağaç: a1 tohum, a2 filiz, a3 fidan, a4 olgun
  Çiçek: a1 tohum, a2 gonca, a3 açmış
"""
from __future__ import annotations

import math

import numpy as np

from mf.mesh import blade, blob, cylinder, icosphere, lathe, merge, tube
from mf.scene import Node

from . import asamali
from .ortak import toprak_tumsek


# --------------------------------------------------------------------------
# Hurma (Tirmizî 3464: Sübhanallahi'l-azîm ve bihamdihi -> cennette hurma ağacı)
# --------------------------------------------------------------------------

def _hurma_yapragi(tepe, aci_deg, uzunluk, kalkis, sarkma, en, seed):
    """Tepe noktasından dışa uzanan, uca doğru sarkan hurma yaprağı.
    En değerleri dönüşümlü: yaprakçıkları (pinna) andıran tırtıklı kenar."""
    a = math.radians(aci_deg)
    yon = np.array([math.cos(a), 0.0, math.sin(a)])
    n = 9
    yol, enler = [], []
    for i in range(n):
        t = i / (n - 1)
        p = np.array(tepe, float) + yon * uzunluk * t
        p[1] += uzunluk * (kalkis * t - sarkma * t * t)
        yol.append(p)
        # Dipte dar, ortada geniş, uçta sivri (ama iğne gibi incelmeden)
        profil = 0.25 + 0.75 * math.sin(math.pi * min(1.0, 0.15 + t * 0.85))
        if i == n - 1:
            profil = 0.08
        enler.append(en * profil * (1.0 if i % 2 else 0.75))
    return blade(yol, enler, "hurma_yaprak", fold=0.55).shade_vary(0.07, seed)


def _hurma_govde(boy, taban_r, egim, halka_sayisi, seed):
    rng = np.random.default_rng(seed)
    parcalar = []
    pts = []
    for i in range(halka_sayisi + 1):
        t = i / halka_sayisi
        x = egim * boy * t * t
        pts.append([x, boy * t, 0.0])
    for i in range(halka_sayisi):
        t0, t1 = i / halka_sayisi, (i + 1) / halka_sayisi
        r0 = taban_r * (1.0 - 0.45 * t0) * (1.35 if i == 0 else 1.0)
        r1 = taban_r * (1.0 - 0.45 * t1)
        parcalar.append(tube([pts[i], pts[i + 1]], [r0, r1 * 1.08], 7,
                             "hurma_govde" if i % 2 == 0 else "govde_acik", cap=(i == 0)))
    return merge(*parcalar).jitter(taban_r * 0.05, seed), np.array(pts[-1])


@asamali("ZB_agac_hurma", 4)
def hurma(asama: int) -> Node:
    root = Node(f"ZB_agac_hurma_a{asama}")
    if asama == 1:
        tohum = icosphere(0.05, 1, "hurma_meyve").scale(0.7, 0.6, 1.25).rotate("y", 30).translate(0.02, 0.095, 0)
        root.add(toprak_tumsek(0.3, 0.08, seed=1), tohum)
        return root
    if asama == 2:
        yapraklar = []
        for i, (aci, boy) in enumerate(((0, 0.28), (125, 0.22), (240, 0.2))):
            a = math.radians(aci)
            yol = [[0, 0.06, 0], [0.02 * math.cos(a), 0.06 + boy * 0.5, 0.02 * math.sin(a)],
                   [0.07 * math.cos(a), 0.06 + boy, 0.07 * math.sin(a)]]
            yapraklar.append(blade(yol, [0.012, 0.028, 0.003], "hurma_yaprak", fold=0.6))
        root.add(toprak_tumsek(0.3, 0.07, seed=2), merge(*yapraklar).shade_vary(0.06, 2))
        return root

    olgun = asama == 4
    boy = 3.3 if olgun else 0.55
    govde, tepe = _hurma_govde(boy, 0.2 if olgun else 0.13, 0.12 if olgun else 0.0,
                               11 if olgun else 3, seed=asama)
    yaprak_sayisi = 13 if olgun else 7
    uzunluk = 1.9 if olgun else 0.8
    yapraklar = []
    rng = np.random.default_rng(10 + asama)
    for i in range(yaprak_sayisi):
        aci = 360.0 * i / yaprak_sayisi + rng.uniform(-10, 10)
        katman = i % 3
        yapraklar.append(_hurma_yapragi(
            tepe + np.array([0, 0.05 * katman, 0]), aci, uzunluk * rng.uniform(0.85, 1.05),
            kalkis=0.8 - 0.18 * katman, sarkma=1.0 + 0.12 * katman, en=0.2 if olgun else 0.11, seed=i))
    # Tepedeki genç, dik yapraklar
    for i in range(3):
        aci = 120.0 * i + 40
        yapraklar.append(_hurma_yapragi(tepe, aci, uzunluk * 0.55, kalkis=1.6, sarkma=0.9,
                                        en=0.1 if olgun else 0.06, seed=50 + i))
    root.add(govde, merge(*yapraklar))
    if olgun:
        salkimlar = []
        for k, aci in enumerate((30, 150, 265)):
            a = math.radians(aci)
            baslangic = tepe + np.array([0.18 * math.cos(a), -0.08, 0.18 * math.sin(a)])
            uc = baslangic + np.array([0.28 * math.cos(a), -0.35, 0.28 * math.sin(a)])
            salkimlar.append(tube([baslangic, uc], [0.02, 0.012], 4, "saman_koyu"))
            rng2 = np.random.default_rng(70 + k)
            for j in range(14):
                t = rng2.uniform(0.35, 1.0)
                p = baslangic + (uc - baslangic) * t + rng2.normal(0, 0.05, 3) * np.array([1, 0.6, 1])
                salkimlar.append(icosphere(0.035, 0, "hurma_meyve").scale(1, 1.35, 1).translate(*p))
        root.add(merge(*salkimlar).shade_vary(0.08, 5))
    else:
        root.add(toprak_tumsek(0.35, 0.06, seed=3))
    return root


# --------------------------------------------------------------------------
# Lale (Allah lafzı ile lale kelimesinin ebcedi aynı: 66)
# --------------------------------------------------------------------------

def _lale_yapragi(aci_deg, boy, seed):
    a = math.radians(aci_deg)
    d = np.array([math.cos(a), 0.0, math.sin(a)])
    yol = [np.array([0, 0.03, 0]) + d * 0.01,
           np.array([0, boy * 0.35, 0]) + d * 0.05,
           np.array([0, boy * 0.7, 0]) + d * 0.1,
           np.array([0, boy, 0]) + d * 0.17]
    return blade(yol, [0.03, 0.04, 0.028, 0.002], "yaprak", fold=0.5, side=np.cross(d, [0, 1, 0])).shade_vary(0.05, seed)


def _lale_tac_yapragi(aci_deg, taban_y, boy, acilma, renk, seed):
    """Osmanlı lalesi (lâle-i rûmî): badem biçimli, ucu sivri, hafif dışa kıvrık taç yaprak."""
    a = math.radians(aci_deg)
    d = np.array([math.cos(a), 0.0, math.sin(a)])
    teget = np.array([-math.sin(a), 0.0, math.cos(a)])
    yol = [d * 0.015 + np.array([0, taban_y, 0]),
           d * (0.03 + 0.03 * acilma) + np.array([0, taban_y + boy * 0.35, 0]),
           d * (0.035 + 0.05 * acilma) + np.array([0, taban_y + boy * 0.7, 0]),
           d * (0.03 + 0.085 * acilma) + np.array([0, taban_y + boy, 0])]
    return blade(yol, [0.014, 0.037, 0.03, 0.002], renk, fold=0.35, side=teget).shade_vary(0.05, seed)


@asamali("ZB_cicek_lale", 3)
def lale(asama: int) -> Node:
    root = Node(f"ZB_cicek_lale_a{asama}")
    if asama == 1:
        sogan = lathe([(0.0, 0.02), (0.03, 0.035), (0.034, 0.06), (0.018, 0.09), (0.0, 0.11)], 7, "tohum")
        filiz = blade([[0, 0.1, 0], [0.005, 0.13, 0], [0.01, 0.155, 0]], [0.008, 0.006, 0.001], "yaprak_acik", fold=0.6)
        root.add(toprak_tumsek(0.18, 0.06, seed=4), sogan, filiz)
        return root
    boy = 0.36 if asama == 2 else 0.46
    sap = tube([[0, 0.0, 0], [0.01, boy * 0.5, 0.0], [0.0, boy, 0.0]], [0.009, 0.008, 0.007], 5, "yaprak_koyu")
    yapraklar = [_lale_yapragi(20, boy * 0.62, 1), _lale_yapragi(200, boy * 0.55, 2)]
    root.add(toprak_tumsek(0.16, 0.035, seed=5), merge(sap, *yapraklar))
    if asama == 2:
        gonca = lathe([(0.0, 0.0), (0.022, 0.012), (0.03, 0.04), (0.027, 0.07), (0.014, 0.095), (0.0, 0.105)],
                      6, "lale").translate(0, boy - 0.01, 0).shade_vary(0.05, 6)
        root.add(gonca)
    else:
        tac = []
        for i in range(3):
            tac.append(_lale_tac_yapragi(60 + 120 * i, boy - 0.01, 0.13, 0.9, "lale", 10 + i))
            tac.append(_lale_tac_yapragi(120 * i, boy - 0.005, 0.115, 0.55, "lale_koyu", 20 + i))
        tac.append(cylinder(0.012, 0.016, 0.03, 6, "lale_sari", y0=boy - 0.01))
        root.add(merge(*tac))
    return root
