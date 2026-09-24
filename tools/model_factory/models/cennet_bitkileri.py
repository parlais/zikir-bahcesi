"""Cennet mekânının bitkileri (Faz 2a).

  Sidr (Vâkıa 28; Ali Ünal: "dikensiz, dal bastı kirazlar"): şemsiye taçlı,
    dal uçları meyve yüküyle sarkık ağaç.
  Talh (Vâkıa 29, "dolgun salkımlı muzlar"): üç gövdeli muz kümesi, kat kat salkım.
  Üzüm asması ve çardak (Nebe 32; İnsan 14: salkımlar ele kadar sarkar).
  Koru ağacı (Rahmân 64: koyu yeşil): korulukların yüksek, dolgun ağacı.
  Uzak ağaç: yüzlerce metre ötedeki korular için birkaç düzine üçgenlik taç.
  Tûbâ çekirdeği (Küllî Kaideler 1: iman kalpte bir Tûbâ çekirdeği taşır).
  Dev Tûbâ: ufukta, üst derecelerin üstünde yükselen merkez simge.

Aşamalar bitkiler.py ile aynı: a1 tohum, a2 filiz, a3 fidan, a4 olgun.
"""
from __future__ import annotations

import math

import numpy as np

from mf.mesh import blade, blob, box, cylinder, icosphere, lathe, merge, tube
from mf.scene import Node

from . import asamali, model
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
    olgun = asama == 4
    k = 1.0 if olgun else 0.36
    rng = np.random.default_rng(13 + asama)
    gov_ust = np.array([0.1, 1.85, 0.05]) * k
    dallar = [tube([[0, 0, 0], [0.12 * k, 0.9 * k, 0.0], gov_ust], [0.22 * k, 0.18 * k, 0.15 * k], 8, "govde").smooth(60)]
    kumeler = [(np.array([0.0, 3.85, 0.0]) * k, 1.1 * k)]
    uclar = []
    n_dal = 6 if olgun else 3
    for i in range(n_dal):
        a = math.radians(i * 360 / n_dal + 15 + rng.uniform(-12, 12))
        yon = np.array([math.cos(a), 0.0, math.sin(a)])
        uz = rng.uniform(0.9, 1.1)
        mid = gov_ust + (yon * 0.9 * uz + np.array([0, 1.0, 0])) * k
        uc = gov_ust + (yon * 2.1 * uz + np.array([0, 1.55, 0])) * k
        sark = gov_ust + (yon * 2.6 * uz + np.array([0, 1.2, 0])) * k
        dallar.append(tube([gov_ust, mid, uc, sark], [0.1 * k, 0.07 * k, 0.045 * k, 0.03 * k], 6, "govde").smooth(60))
        uclar.append(uc)
        kumeler.append((uc + np.array([0, 0.05, 0]) * k, 0.9 * k))
    if olgun:
        for a in (0.6, 2.7, 4.7):
            kumeler.append((np.array([1.05 * math.cos(a), 4.15, 1.05 * math.sin(a)]), 0.85))
    tac_merkez = np.array([0.0, 3.5, 0.0]) * k
    renkler = ["yaprak_cennet", "yaprak", "yaprak_acik", "yaprak_cennet"]
    tac = _tac(kumeler, tac_merkez, renkler, 22 if olgun else 16, 0.26 * max(k, 0.6), 130 + asama,
               kutle_renk="yaprak", squash=0.75)
    yaprak = merge(*tac).with_material("yaprak").weight(lambda V: np.clip((V[:, 1] - 2.0 * k) / (2.2 * k), 0, 1))
    root.add(merge(*dallar).with_material("govde"), yaprak)
    if olgun:
        # Kirazlar: dal uçlarındaki kümelerin altından çift çift sarkar
        meyve = []
        for c, r in kumeler[1:n_dal + 1]:
            for j in range(6):
                v = rng.normal(0, 1, 3)
                v[1] = -abs(v[1]) - 0.9
                v /= np.linalg.norm(v)
                p = c + v * r * 0.8
                q = p + np.array([0, -0.16, 0])
                meyve.append(tube([p, q], [0.008, 0.006], 3, "govde_acik", cap=False))
                for s in (-1, 1):
                    meyve.append(icosphere(0.058, 0, "kiraz" if j % 3 else "kiraz_koyu")
                                 .translate(q[0] + s * 0.035, q[1] - 0.04, q[2]).smooth(70))
        root.add(merge(*meyve).with_material("cicek").weight(lambda V: np.ones(len(V)) * 0.8))
    else:
        root.add(toprak_tumsek(0.4, 0.06, seed=14))
    return root


# --------------------------------------------------------------------------
# Talh (muz)
# --------------------------------------------------------------------------

def _muz_yapragi(tepe, aci_deg, uzunluk, kalkis, sarkma, en, renk, seed):
    a = math.radians(aci_deg)
    yon = np.array([math.cos(a), 0.0, math.sin(a)])
    n = 8
    yol, enler = [], []
    for i in range(n):
        t = i / (n - 1)
        p = np.asarray(tepe, float) + yon * uzunluk * t
        p[1] += uzunluk * (kalkis * t - sarkma * t * t)
        yol.append(p)
        if t < 0.14:
            w = en * 0.08                                        # yaprak sapı
        else:
            w = en * (0.35 + 0.65 * math.sin(math.pi * min(1.0, (t - 0.1) / 0.92)))
        if i == n - 1:
            w = en * 0.1
        enler.append(w * (1.0 if i % 2 else 0.86))           # rüzgârla yırtılmış kenar izi
    return blade(yol, enler, renk, fold=0.14).shade_vary(0.06, seed)


def _muz_salkimi(tepe, aci_deg, olcek, seed):
    a = math.radians(aci_deg)
    d = np.array([math.cos(a), 0.0, math.sin(a)])
    t0 = np.asarray(tepe, float)
    sap = [t0, t0 + d * 0.35 * olcek + np.array([0, 0.08, 0]) * olcek,
           t0 + d * 0.6 * olcek + np.array([0, -0.35, 0]) * olcek,
           t0 + d * 0.66 * olcek + np.array([0, -1.15, 0]) * olcek]
    parca = [tube(sap, [0.045 * olcek, 0.04 * olcek, 0.035 * olcek, 0.03 * olcek], 5, "muz_govde")]
    muz = []
    P = np.asarray(sap)
    for k in range(6):                                           # kat kat eller (mandûd)
        t = 0.35 + 0.1 * k
        seg = min(int(t * 3), 2)
        u = t * 3 - seg
        q = P[seg] + (P[seg + 1] - P[seg]) * u
        n = 7 if k < 4 else 5
        for j in range(n):
            b = 2 * math.pi * j / n + k * 0.4
            r = np.array([math.cos(b), 0.0, math.sin(b)])
            s = olcek * (1.0 - 0.07 * k)
            yol = [q + r * 0.05 * s, q + r * 0.13 * s + np.array([0, 0.03, 0]) * s,
                   q + r * 0.17 * s + np.array([0, 0.12, 0]) * s]
            muz.append(tube(yol, [0.022 * s, 0.026 * s, 0.012 * s], 5, "muz"))
    uc = P[-1]
    tomurcuk = lathe([(0.0, 0.0), (0.06, 0.05), (0.085, 0.14), (0.06, 0.24), (0.0, 0.3)], 7, "muz_cicek")
    tomurcuk = tomurcuk.scale(olcek).rotate("x", 180).translate(uc[0], uc[1] + 0.04 * olcek, uc[2])
    return merge(*parca).with_material("govde"), merge(*muz, tomurcuk).smooth(60).with_material("cicek")


def _muz_bitkisi(taban, boy, egim_deg, yaprak_n, uzunluk, seed, salkim=False):
    rng = np.random.default_rng(seed)
    e = math.radians(egim_deg)
    x0, z0 = taban
    ust = np.array([x0 + math.sin(e) * boy * 0.25, boy, z0 + math.cos(e) * boy * 0.1])
    govde = tube([[x0, 0, z0], [x0 + math.sin(e) * boy * 0.05, boy * 0.4, z0], ust],
                 [0.17 * boy / 3.2 + 0.03, 0.14 * boy / 3.2 + 0.02, 0.1 * boy / 3.2 + 0.02], 8, "muz_govde").smooth(60)
    yapraklar = []
    for i in range(yaprak_n):
        aci = 360.0 * i / yaprak_n + rng.uniform(-14, 14)
        yas = i % 3                                              # yaşlı yapraklar daha sarkık
        yapraklar.append(_muz_yapragi(ust + np.array([0, 0.04 * yas, 0]), aci, uzunluk * rng.uniform(0.85, 1.05),
                                      kalkis=1.25 - 0.3 * yas, sarkma=1.25 + 0.25 * yas, en=0.34 * uzunluk / 2.2,
                                      renk="muz_yaprak" if yas else "muz_yaprak_koyu", seed=seed + i))
    # Tepedeki dik, kıvrık genç yaprak
    yapraklar.append(_muz_yapragi(ust, rng.uniform(0, 360), uzunluk * 0.6, kalkis=2.4, sarkma=1.2,
                                  en=0.16 * uzunluk / 2.2, renk="yaprak_acik", seed=seed + 40))
    out = [govde.with_material("govde"), merge(*yapraklar).with_material("yaprak")]
    if salkim:
        out += list(_muz_salkimi(ust - np.array([0, 0.1, 0]), rng.uniform(0, 360), boy / 3.2, seed))
    return out


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
        parca = _muz_bitkisi((0.0, 0.0), 1.2, 10, 5, 0.9, 23)
        root.add(toprak_tumsek(0.45, 0.06, seed=23), *parca)
    else:
        parca = (_muz_bitkisi((0.0, 0.0), 3.3, 8, 8, 2.3, 24, salkim=True)
                 + _muz_bitkisi((0.6, 0.3), 2.6, 60, 7, 2.0, 25, salkim=True)
                 + _muz_bitkisi((-0.4, 0.5), 1.8, -40, 6, 1.5, 26))
        gruplar: dict[str, list] = {}
        for m in parca:
            gruplar.setdefault(m.material, []).append(m)
        for mat, ms in gruplar.items():
            m = merge(*ms)
            if mat == "yaprak":
                m = m.weight(lambda V: np.clip((V[:, 1] - 1.0) / 2.5, 0, 1))
            elif mat == "cicek":
                m = m.weight(lambda V: np.ones(len(V)) * 0.3)
            root.add(m)
    return root


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
    asmalar = []
    for sx, sz in ((1, 1), (-1, -1)):
        pts = []
        for t in np.linspace(0, 1, 10):
            a = t * 7.0 + (0 if sx > 0 else 2)
            pts.append([sx * 1.5 + 0.13 * math.cos(a), t * (yuk + 0.3), sz * 1.5 + 0.13 * math.sin(a)])
        asmalar.append(tube(pts, list(np.linspace(0.075, 0.04, 10)), 6, "govde").smooth(60))
        # Kirişler boyunca uzanan kollar
        asmalar.append(tube([pts[-1], [sx * 0.6, yuk + 0.35, sz * 1.2], [-sx * 0.8, yuk + 0.38, sz * 0.9]],
                            [0.04, 0.03, 0.018], 5, "govde").smooth(60))
    kutle, yapraklar = [], []
    merkez = np.array([0.0, yuk + 0.2, 0.0])
    for i, x in enumerate((-1.1, 0.0, 1.1)):
        for j, z in enumerate((-1.1, 0.0, 1.1)):
            c = np.array([x + rng.uniform(-0.15, 0.15), yuk + 0.45, z + rng.uniform(-0.15, 0.15)])
            kutle.append(blob(0.72, "yaprak", seed=300 + i * 3 + j, subdiv=2, squash=0.42, jitter=0.14)
                         .translate(*c).kure_normal(merkez, (2.0, 0.6, 2.0)))
            for k in range(20):
                v = rng.normal(0, 1, 3)
                v[1] = abs(v[1]) * 0.5 - 0.15
                v /= np.linalg.norm(v)
                p = c + v * np.array([0.72, 0.3, 0.72]) * rng.uniform(0.8, 1.05)
                yon = v * 0.7 + np.array([0, -0.35, 0])
                yon /= np.linalg.norm(yon)
                yapraklar.append(_uzum_yapragi(p, yon, rng.uniform(0.18, 0.25),
                                               ["yaprak", "yaprak_cennet", "yaprak_koyu"][k % 3])
                                 .kure_normal(merkez, (2.0, 0.6, 2.0)))
    salkimlar = []
    for i in range(8):
        a = 2 * math.pi * i / 8 + 0.3
        r = rng.uniform(0.5, 1.3)
        p = np.array([r * math.cos(a), yuk + 0.12, r * math.sin(a)])
        salkimlar += _salkim(p, 6, 1.1, "uzum" if i % 3 else "uzum_acik", 340 + i)
    yaprak = merge(*kutle, *yapraklar).with_material("yaprak").weight(lambda V: np.clip((V[:, 1] - 2.0) / 1.0, 0, 1) * 0.5)
    root.add(cerceve.with_material("govde"), merge(*asmalar).with_material("govde"), yaprak,
             merge(*salkimlar).with_material("cicek").weight(lambda V: np.ones(len(V)) * 0.3))
    return root


# --------------------------------------------------------------------------
# Koru ağacı ve uzak ağaç
# --------------------------------------------------------------------------

@model("ZB_bitki_koru_agac")
def koru_agac() -> Node:
    """Rahmân 64 (müdhâmmetân, koyu yeşil): korulukların 11 m'lik dolgun ağacı."""
    rng = np.random.default_rng(51)
    gov_ust = np.array([0.15, 4.6, 0.0])
    dallar = [tube([[0, 0, 0], [0.1, 2.4, 0.05], gov_ust], [0.38, 0.3, 0.24], 8, "govde").smooth(60)]
    kumeler = [(np.array([0.0, 8.4, 0.0]), 2.3)]
    for i in range(4):
        a = i * math.pi / 2 + 0.5 + rng.uniform(-0.2, 0.2)
        uc = np.array([2.0 * math.cos(a), 7.5, 2.0 * math.sin(a)])
        dallar.append(tube([gov_ust, gov_ust + np.array([0.9 * math.cos(a), 1.6, 0.9 * math.sin(a)]), uc],
                           [0.2, 0.13, 0.08], 6, "govde").smooth(60))
        kumeler.append((uc + np.array([0, 0.2, 0]), 1.85))
    for i, a in enumerate((0.1, 2.2, 4.3)):
        kumeler.append((np.array([1.0 * math.cos(a), 9.9, 1.0 * math.sin(a)]), 1.55))
    for a in (1.3, 3.9):
        kumeler.append((np.array([1.7 * math.cos(a), 6.3, 1.7 * math.sin(a)]), 1.4))
    renkler = ["yaprak_zumrut", "yaprak_koyu", "selvi", "yaprak"]
    tac = _tac(kumeler, (0.0, 8.0, 0.0), renkler, 14, 0.42, 520, kutle_renk="yaprak_zumrut", squash=0.9)
    yaprak = merge(*tac).with_material("yaprak").weight(lambda V: np.clip((V[:, 1] - 5.0) / 5.0, 0, 1) * 0.6)
    return Node("ZB_bitki_koru_agac", [merge(*dallar).with_material("govde"), yaprak])


@model("ZB_bitki_uzak_agac")
def uzak_agac() -> Node:
    """Yüzlerce metre ötedeki korular: 9 m, birkaç düzine üçgen."""
    govde = cylinder(0.3, 0.18, 4.0, 5, "govde").with_material("govde")
    parca = []
    for i, (c, r) in enumerate((((0, 6.2, 0), 2.6), ((1.2, 5.3, 0.6), 1.9), ((-1.1, 5.5, -0.5), 2.0),
                                ((0.2, 7.8, -0.2), 1.8))):
        parca.append(icosphere(r, 0, "yaprak_zumrut").jitter(r * 0.12, 60 + i).shade_vary(0.08, 60 + i)
                     .translate(*c))
    tac = merge(*parca).kure_normal((0.0, 5.8, 0.0), (1.0, 0.8, 1.0)).with_material("yaprak")
    return Node("ZB_bitki_uzak_agac", [govde, tac.weight(lambda V: np.zeros(len(V)))])


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


@model("ZB_dunya_tuba_dev")
def tuba_dev() -> Node:
    """Ufuktaki dev Tûbâ (Buhârî, Bed'ü'l-halk 8: gölgesinde yüz yıl koşulan ağaç).
    Dünya ölçeğinde: 420 m. Geniş, kat kat şemsiye taç; dallardan inen kök
    sütunları; tacında ışıklı çiçekler (nur)."""
    H = 420.0
    rng = np.random.default_rng(401)
    gov = [[0, 0, 0], [0.02 * H, 0.16 * H, 0], [-0.015 * H, 0.32 * H, 0.01 * H], [0.0, 0.46 * H, 0]]
    dallar = [tube(gov, [0.1 * H, 0.075 * H, 0.06 * H, 0.045 * H], 14, "govde").smooth(60)]
    for i in range(9):                                                    # kök ayakları
        a = 2 * math.pi * i / 9 + rng.uniform(-0.2, 0.2)
        d = np.array([math.cos(a), 0, math.sin(a)])
        dallar.append(tube([d * 0.05 * H + [0, 0.1 * H, 0], d * 0.12 * H + [0, 0.025 * H, 0],
                            d * 0.19 * H - [0, 0.01 * H, 0]], [0.04 * H, 0.02 * H, 0.005 * H], 7, "govde").smooth(60))
    ust = np.array(gov[-1])
    uclar = []
    for i in range(10):
        a = 2 * math.pi * i / 10 + rng.uniform(-0.15, 0.15)
        d = np.array([math.cos(a), 0, math.sin(a)])
        orta = ust + d * 0.2 * H + np.array([0, 0.1 * H, 0])
        uc = d * rng.uniform(0.44, 0.52) * H + np.array([0, 0.6 * H + rng.uniform(-0.02, 0.02) * H, 0])
        dallar.append(tube([ust - [0, 0.06 * H, 0], orta, uc], [0.03 * H, 0.018 * H, 0.008 * H], 7, "govde").smooth(60))
        uclar.append(uc)
        # Daldan yere inen kök sütunu (banyan gibi): ağacın yaşını ve genişliğini gösterir
        if i % 2 == 0:
            k = orta * 0.4 + uc * 0.6
            dallar.append(tube([k, k * np.array([1.02, 0.5, 1.02]), k * np.array([1.04, 0.0, 1.04]) - [0, 0.01 * H, 0]],
                               [0.008 * H, 0.009 * H, 0.012 * H], 6, "govde").smooth(60))
    kumeler = []
    for i, u in enumerate(uclar):                                         # alt kat: geniş halka
        kumeler.append((u + np.array([0, 0.02 * H, 0]), 0.15 * H, 0.55))
    for i in range(7):                                                    # orta kat
        a = 2 * math.pi * i / 7 + 0.3
        kumeler.append((np.array([0.3 * H * math.cos(a), 0.69 * H, 0.3 * H * math.sin(a)]), 0.16 * H, 0.6))
    for i in range(4):                                                    # üst kat
        a = 2 * math.pi * i / 4 + 0.8
        kumeler.append((np.array([0.13 * H * math.cos(a), 0.78 * H, 0.13 * H * math.sin(a)]), 0.15 * H, 0.62))
    kumeler.append((np.array([0, 0.84 * H, 0]), 0.13 * H, 0.65))
    merkez = np.array([0, 0.66 * H, 0])
    tac = []
    for i, (c, r, sq) in enumerate(kumeler):
        tac.append(blob(r, ["yaprak_cennet", "yaprak", "yaprak_acik"][i % 3], seed=410 + i, subdiv=2, squash=sq,
                        jitter=0.16).translate(*c).kure_normal(merkez, (1.6, 0.6, 1.6)))
    cicek = []
    for i in range(140):
        c, r, sq = kumeler[rng.integers(len(kumeler))]
        v = rng.normal(0, 1, 3)
        v[1] = abs(v[1]) * 0.7 - 0.15
        v /= np.linalg.norm(v)
        cicek.append(icosphere(rng.uniform(0.005, 0.009) * H, 0, "nur_beyaz")
                     .translate(*(c + v * np.array([r, r * sq, r]) * 0.97)))
    root = Node("ZB_dunya_tuba_dev")
    root.add(merge(*dallar).with_material("govde"),
             merge(*tac).with_material("yaprak").weight(lambda V: np.zeros(len(V))),
             merge(*cicek).with_material("nur"))
    return root
