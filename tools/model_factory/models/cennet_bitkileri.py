"""Cennet mekânının bitkileri (Faz 2a).

  Sidr (Vâkıa 28; Ali Ünal: "dikensiz, dal bastı kirazlar"): şemsiye taçlı,
    dal uçları meyve yüküyle sarkık ağaç.
  Talh (Vâkıa 29, "dolgun salkımlı muzlar"): üç gövdeli muz kümesi, kat kat salkım.
  Üzüm asması ve çardak (Nebe 32; İnsan 14: salkımlar ele kadar sarkar).
  Koru ağacı (Rahmân 64: koyu yeşil): korulukların yüksek, dolgun ağacı.
  Uzak ağaç: yüzlerce metre ötedeki korular için birkaç düzine üçgenlik taç.
  Tûbâ çekirdeği (Küllî Kaideler 1: iman kalpte bir Tûbâ çekirdeği taşır).

Aşamalar bitkiler.py ile aynı: a1 tohum, a2 filiz, a3 fidan, a4 olgun.
"""
from __future__ import annotations

import math

import numpy as np

from mf.mesh import blade, blob, box, cylinder, icosphere, lathe, merge, tube
from mf.scene import Node

from . import asamali, model
from mf.agac import meyve_yerleri

from .agaclar import KORU, UZAK, agac_modeli, muz_modeli, sidr_modeli
from .agaclar import asma as asma_kur
from .ortak import toprak_tumsek
from .sahne import _yaprak_bulutu


def _tac(kumeler, tac_merkez, renkler, yaprak_sayi, boy, seed, kutle_renk="yaprak_koyu",
         squash=0.85, subdiv=2):
    """Yaprak kümeleri: her küme bir kabarık kütle ve üstünde dışa bakan yapraklar.
    Normaller bütün tacın merkezine doğru karıştırılır: yumuşak, bütünlüklü taç."""
    tm = np.asarray(tac_merkez, float)
    out = []
    for i, (c, r) in enumerate(kumeler):
        c = np.asarray(c, float)
        nm = tm * 0.6 + c * 0.4
        out.append(blob(r * 0.88, kutle_renk, seed=seed + i, subdiv=subdiv, squash=squash, jitter=0.12)
                   .translate(*c).kure_normal(nm))
        out += [y.kure_normal(nm) for y in _yaprak_bulutu(c, r, yaprak_sayi, seed + 50 + i, renkler, boy=boy)]
    return out


def _tohum_asamasi(ad, tohum_renk, seed, boyut=0.045):
    root = Node(ad)
    tohum = icosphere(boyut, 1, tohum_renk).scale(1.0, 0.8, 1.25).rotate("y", 30).translate(0.02, 0.085, 0)
    root.add(toprak_tumsek(0.3, 0.08, seed=seed), tohum.smooth(60))
    return root


def _filiz(yapraklar, sap_boy, sap_renk="govde_acik", yaprak_renk="yaprak_acik", seed=0):
    """Toprak tümseğinden çıkan ince sap ve birkaç küçük yaprak."""
    sap = tube([[0, 0.05, 0], [0.01, 0.05 + sap_boy * 0.5, 0], [0.0, 0.05 + sap_boy, 0.01]],
               [0.012, 0.009, 0.006], 5, sap_renk)
    parca = [sap]
    for i, (aci, y, boy) in enumerate(yapraklar):
        a = math.radians(aci)
        d = np.array([math.cos(a), 0.35, math.sin(a)])
        p0 = np.array([0.0, 0.05 + y, 0.0])
        parca.append(blade([p0, p0 + d * boy * 0.5, p0 + d * boy], [0.004, boy * 0.3, 0.003], yaprak_renk,
                           fold=0.4))
    return merge(*parca).shade_vary(0.05, seed)


# --------------------------------------------------------------------------
# Sidr
# --------------------------------------------------------------------------

@asamali("ZB_agac_sidr", 4)
def sidr(asama: int) -> Node:
    ad = f"ZB_agac_sidr_a{asama}"
    if asama == 1:
        return _tohum_asamasi(ad, "kiraz_koyu", 11)
    root = Node(ad)
    if asama == 2:
        root.add(toprak_tumsek(0.3, 0.07, seed=12),
                 _filiz([(20, 0.18, 0.09), (140, 0.24, 0.08), (260, 0.28, 0.07), (330, 0.3, 0.06)], 0.3, seed=12))
        return root
    if asama == 4:
        return sidr_modeli(ad, True)
    # Fidan: aynı türün küçük, iki dal seviyeli hâli; arsada yeni dikilmiş (toprak tümseği)
    return sidr_modeli(ad, False).add(toprak_tumsek(0.4, 0.06, seed=14))


# --------------------------------------------------------------------------
# Talh (muz)
# --------------------------------------------------------------------------

@asamali("ZB_agac_talh", 4)
def talh(asama: int) -> Node:
    ad = f"ZB_agac_talh_a{asama}"
    if asama == 1:
        return _tohum_asamasi(ad, "muz_govde", 21, 0.06)
    root = Node(ad)
    if asama == 2:
        root.add(toprak_tumsek(0.3, 0.07, seed=22),
                 _filiz([(40, 0.2, 0.16), (220, 0.26, 0.13)], 0.3, "muz_govde", "muz_yaprak", seed=22))
        return root
    if asama == 3:
        return muz_modeli(ad, False).add(toprak_tumsek(0.45, 0.06, seed=23))
    return muz_modeli(ad, True)


# --------------------------------------------------------------------------
# Üzüm asması ve çardak
# --------------------------------------------------------------------------

def _uzum_yapragi(p, yon, boy, renk):
    """Beş loplu üzüm yaprağının sade karşılığı: geniş, kısa, ucu sivri şerit."""
    yan = np.cross(yon, [0, 1, 0])
    if np.linalg.norm(yan) < 1e-3:
        yan = np.array([1.0, 0, 0])
    yol = [p, p + yon * boy * 0.35, p + yon * boy * 0.75, p + yon * boy]
    return blade(yol, [0.01, boy * 0.55, boy * 0.45, 0.005], renk, fold=0.2, side=yan)


def _salkim(p, n_kat, olcek, renk, seed):
    rng = np.random.default_rng(seed)
    out = [tube([p + np.array([0, 0.08, 0]), p], [0.008, 0.006], 3, "govde_acik", cap=False)]
    sayilar = [4, 4, 3, 3, 2, 1][:n_kat]
    for k, n in enumerate(sayilar):
        r = (0.07 - 0.012 * k) * olcek
        for j in range(n):
            a = 2 * math.pi * j / n + k * 0.7
            q = p + np.array([r * math.cos(a), -0.055 * k * olcek - 0.03, r * math.sin(a)])
            q += rng.normal(0, 0.006, 3)
            out.append(icosphere(0.032 * olcek, 0, renk if (j + k) % 3 else renk + "_koyu"
                                 if renk == "uzum" else renk).translate(*q).smooth(70))
    return out


def _cardak(olcek=1.0, yari=1.5, yuk=2.5):
    s = olcek
    parca = []
    for x in (-yari, yari):
        for z in (-yari, yari):
            parca += [cylinder(0.1 * s, 0.09 * s, 0.12 * s, 8, "tas_koyu").translate(x * s, 0, z * s),
                      cylinder(0.075 * s, 0.07 * s, yuk * s, 8, "ahsap", y0=0.1 * s).translate(x * s, 0, z * s),
                      cylinder(0.09 * s, 0.09 * s, 0.08 * s, 8, "altin", y0=(yuk + 0.02) * s).translate(x * s, 0, z * s)]
    for z in (-yari, yari):
        parca.append(box((2 * yari + 0.5) * s, 0.14 * s, 0.14 * s, "ahsap", y0=(yuk + 0.08) * s).translate(0, 0, z * s))
    for i in range(6):
        x = -yari + 2 * yari * i / 5
        parca.append(box(0.08 * s, 0.09 * s, (2 * yari + 0.5) * s, "ahsap_koyu", y0=(yuk + 0.22) * s).translate(x * s, 0, 0))
    return merge(*parca)


@asamali("ZB_agac_uzum", 4)
def uzum(asama: int) -> Node:
    ad = f"ZB_agac_uzum_a{asama}"
    if asama == 1:
        return _tohum_asamasi(ad, "uzum", 31, 0.04)
    root = Node(ad)
    rng = np.random.default_rng(30 + asama)
    if asama == 2:
        kazik = cylinder(0.015, 0.012, 0.7, 5, "ahsap").translate(0.08, 0, 0)
        root.add(toprak_tumsek(0.3, 0.07, seed=32), kazik.with_material("govde"),
                 _filiz([(60, 0.16, 0.1), (200, 0.24, 0.09), (300, 0.3, 0.07)], 0.32, seed=32))
        return root
    if asama == 3:
        kazik = merge(cylinder(0.03, 0.025, 1.6, 6, "ahsap"), cylinder(0.04, 0.04, 0.04, 6, "altin", y0=1.6))
        yol = [[0.05 * math.cos(t * 5), t * 1.5, 0.05 * math.sin(t * 5)] for t in np.linspace(0, 1, 9)]
        asma = tube(yol, list(np.linspace(0.025, 0.01, 9)), 5, "govde")
        yap = []
        for i in range(10):
            t = 0.35 + 0.065 * i
            a = i * 2.3
            p = np.array([0.06 * math.cos(a), t * 1.5, 0.06 * math.sin(a)])
            yon = np.array([math.cos(a), -0.3, math.sin(a)])
            yap.append(_uzum_yapragi(p, yon / np.linalg.norm(yon), 0.16, "yaprak" if i % 2 else "yaprak_cennet"))
        root.add(toprak_tumsek(0.35, 0.06, seed=33), merge(kazik, asma).with_material("govde"),
                 merge(*yap).with_material("yaprak").weight(lambda V: np.clip(V[:, 1] / 1.6, 0, 1)))
        return root

    yuk = 2.5
    cerceve = _cardak(1.0, 1.5, yuk)
    # İki kütük, köşe direklerine sarılarak çıkar; kirişler boyunca kollar, çatının üstüne sürgünler
    govdeler, surgunler = [], []
    kollar = []
    for sx, sz in ((1, 1), (-1, -1)):
        pts = []
        for t in np.linspace(0, 1, 12):
            a = t * 7.0 + (0 if sx > 0 else 2)
            pts.append([sx * 1.5 + 0.13 * math.cos(a), -0.05 + t * (yuk + 0.35), sz * 1.5 + 0.13 * math.sin(a)])
        kol = [pts[-1], [sx * 0.6, yuk + 0.38, sz * 1.25], [-sx * 0.5, yuk + 0.42, sz * 0.8],
               [-sx * 1.3, yuk + 0.4, sz * 0.2]]
        govdeler.append((np.array(pts + kol[1:]), np.concatenate([np.linspace(0.085, 0.05, 12),
                                                                    np.linspace(0.045, 0.025, 3)])))
        kollar.append(np.array(kol))
    for k in range(16):
        kol = kollar[k % 2]
        t = rng.uniform(0.15, 0.95)
        i = min(int(t * (len(kol) - 1)), len(kol) - 2)
        p0 = kol[i] + (kol[i + 1] - kol[i]) * (t * (len(kol) - 1) - i)
        fi = rng.uniform(0, 2 * math.pi)
        yon = np.array([math.cos(fi), 0.0, math.sin(fi)])
        L = rng.uniform(1.0, 1.7)
        yol = [p0 + yon * L * u + np.array([0, 0.18 * math.sin(math.pi * u) - (0.5 * max(0.0, np.abs(p0 + yon * L * u)[[0, 2]].max() - 1.6)), 0])
               for u in np.linspace(0, 1, 6)]
        surgunler.append((np.array(yol), np.linspace(0.022, 0.008, 6)))
    kabuk, yapraklar, surgun, ruzgar = asma_kur(govdeler, surgunler, (0.0, yuk + 0.35, 0.0), (2.1, 0.55, 2.1))
    salkimlar = []
    for i, (p, tn, r) in enumerate(meyve_yerleri(surgun, (1,), 10, 341, bas=0.2)):
        salkimlar += _salkim(p - np.array([0, 0.02, 0]), 6, 1.2, "uzum" if i % 3 else "uzum_acik", 340 + i)
    meyve = merge(*salkimlar).with_material("meyve").paylasimli()
    meyve.W = ruzgar(meyve.V).astype(np.float32)
    root.add(cerceve.with_material("govde"), kabuk, *yapraklar, meyve)
    return root


# --------------------------------------------------------------------------
# Koru ağacı ve uzak ağaç
# --------------------------------------------------------------------------

@model("ZB_bitki_koru_agac")
def koru_agac() -> Node:
    """Rahmân 64 (müdhâmmetân, koyu yeşil): korulukların 12 m'lik dolgun, dallanan ağacı."""
    return agac_modeli("ZB_bitki_koru_agac", KORU)


@model("ZB_bitki_uzak_agac")
def uzak_agac() -> Node:
    """Yüzlerce metre ötedeki korular: korunun birkaç yüz üçgenlik hafif hâli."""
    return agac_modeli("ZB_bitki_uzak_agac", UZAK)


@model("ZB_bitki_ufuk_agaci")
def ufuk_agaci() -> Node:
    """Ufuktaki (700 m ötesi) ve kesitteki ağaçlar: dikey ekranda birkaç piksel boyundadır.
    Birkaç düzine üçgenlik taç ve gövde; rengi korunun yaprak dokusunun ortalaması."""
    govde = cylinder(0.3, 0.18, 4.0, 5, (150 / 255 * 0.7, 134 / 255 * 0.7, 116 / 255 * 0.7)).with_material("govde")
    parca = []
    for i, (c, r) in enumerate((((0, 6.2, 0), 2.6), ((1.2, 5.3, 0.6), 1.9), ((-1.1, 5.5, -0.5), 2.0),
                                ((0.2, 7.8, -0.2), 1.8))):
        parca.append(icosphere(r, 0, (48 / 255, 108 / 255, 60 / 255)).jitter(r * 0.12, 60 + i).shade_vary(0.08, 60 + i)
                     .translate(*c))
    tac = merge(*parca).kure_normal((0.0, 5.8, 0.0), (1.0, 0.8, 1.0)).with_material("yaprak")
    return Node("ZB_bitki_ufuk_agaci", [govde, tac.weight(lambda V: np.zeros(len(V)))])


# --------------------------------------------------------------------------
# Tûbâ
# --------------------------------------------------------------------------

@model("ZB_agac_tuba_a1")
def tuba_cekirdek() -> Node:
    """Oyuncunun arsasının ortasındaki ışıklı Tûbâ çekirdeği. Toprağa ince nur
    kökleri salmış; Godot "isik_cekirdek" noktasına ışık ve parıltı koyar."""
    root = Node("ZB_agac_tuba_a1")
    tumsek = toprak_tumsek(0.6, 0.12, seed=91).recolor("toprak_arsa_acik").shade_vary(0.08, 91)
    tohum = icosphere(0.085, 2, "nur_beyaz").scale(0.85, 1.15, 0.85).translate(0, 0.14, 0).smooth(80)
    kokler = []
    rng = np.random.default_rng(92)
    for i in range(7):
        a = 2 * math.pi * i / 7 + rng.uniform(-0.3, 0.3)
        L = rng.uniform(0.35, 0.6)
        pts = []
        for t in np.linspace(0, 1, 6):
            r = 0.08 + L * t
            b = a + 0.35 * math.sin(t * 3 + i)
            y = 0.125 * (1 - (r / 0.6) ** 2) + 0.012 if r < 0.6 else 0.012
            pts.append([r * math.cos(b), y, r * math.sin(b)])
        kokler.append(tube(pts, list(np.linspace(0.012, 0.003, 6)), 4, "nur", cap=False))
    root.add(tumsek, merge(tohum, *kokler).with_material("nur"))
    root.add(Node("isik_cekirdek", translation=(0.0, 0.25, 0.0)))
    return root
