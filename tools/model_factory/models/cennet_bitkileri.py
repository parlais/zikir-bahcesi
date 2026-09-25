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
from .agac_asamalari import dikim_yeri, filiz, muz_filizi, tohum_muz, tohum_sidr, tohum_uzum
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
        return Node(ad).add(dikim_yeri(tohum=11), tohum_sidr(0.06))
    if asama == 2:
        sap, yap = filiz("sidr", 0.4, [(0.28, 20, 0.14, 22), (0.46, 150, 0.15, 25), (0.62, 280, 0.15, 28),
                                       (0.79, 50, 0.13, 36), (0.95, 190, 0.11, 55)], sap_r=0.008, tohum=12)
        return Node(ad).add(dikim_yeri(tohum=12), sap, yap)
    if asama == 4:
        return sidr_modeli(ad, True)
    # Fidan: aynı türün küçük, iki dal seviyeli hâli; arsada yeni dikilmiş
    return sidr_modeli(ad, False).add(dikim_yeri(0.45, tohum=14))


# --------------------------------------------------------------------------
# Talh (muz)
# --------------------------------------------------------------------------

@asamali("ZB_agac_talh", 4)
def talh(asama: int) -> Node:
    ad = f"ZB_agac_talh_a{asama}"
    if asama == 1:
        return Node(ad).add(dikim_yeri(tohum=21), tohum_muz(0.06))
    if asama == 2:
        return Node(ad).add(dikim_yeri(tohum=22), *muz_filizi())
    if asama == 3:
        return muz_modeli(ad, False).add(dikim_yeri(0.5, tohum=23))
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
        return Node(ad).add(dikim_yeri(tohum=31), tohum_uzum(0.06))
    root = Node(ad)
    rng = np.random.default_rng(30 + asama)
    if asama == 2:
        kazik = cylinder(0.012, 0.01, 0.62, 6, "ahsap").translate(0.07, 0, 0).with_material("govde")
        sap, yap = filiz("uzum", 0.34, [(0.45, 200, 0.15, 20), (0.72, 20, 0.16, 25), (0.95, 110, 0.13, 45)],
                         sap_r=0.008, sap_renk=(0.5, 0.42, 0.28), tohum=32)
        # Kazığa uzanan asma bıyığı
        biyik = tube([[0.0, 0.3, 0.0], [0.03, 0.34, 0.01], [0.06, 0.36, 0.0], [0.07, 0.4, -0.01], [0.065, 0.43, 0.0]],
                     [0.0025, 0.002, 0.0018, 0.0015, 0.0012], 3, (0.46, 0.56, 0.26), cap=False).with_material("govde")
        root.add(dikim_yeri(tohum=32), kazik, sap, biyik, yap)
        return root
    if asama == 3:
        # Kazığa sarılan genç asma: kütük kazık boyunca kıvrılarak çıkar, tepede birkaç sürgün
        kazik = merge(cylinder(0.03, 0.025, 1.6, 6, "ahsap"), cylinder(0.04, 0.04, 0.04, 6, "altin", y0=1.6))
        yol = [[0.05 * math.cos(t * 5), -0.02 + t * 1.5, 0.05 * math.sin(t * 5)] for t in np.linspace(0, 1, 10)]
        surgunler = []
        for k in range(4):
            fi = k * 1.7 + 0.4
            yon = np.array([math.cos(fi), 0.0, math.sin(fi)])
            b = np.array(yol[6 + k % 4 if 6 + k % 4 < 10 else 9])
            surgunler.append((np.array([b + yon * 0.45 * u + np.array([0, 0.12 * math.sin(math.pi * u) - 0.25 * u * u, 0])
                                        for u in np.linspace(0, 1, 5)]), np.linspace(0.012, 0.005, 5)))
        kabuk, yapraklar, _, _ = asma_kur([(np.array(yol), np.linspace(0.03, 0.012, 10))], surgunler,
                                          (0.0, 1.3, 0.0), (0.6, 0.6, 0.6), olcek=0.45, tohum=34)
        root.add(dikim_yeri(0.45, tohum=33), kazik.with_material("govde"), kabuk, *yapraklar)
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
