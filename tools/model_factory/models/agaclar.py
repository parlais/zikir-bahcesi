"""Dallanan ağaçlar (K15): türlerin iskelet ve yaprak parametreleri.

Üreteç mf/agac.py'de, yaprak atlasları mf/doku.py'dedir. Her tür için:
  - yaprak kümesi dokusu (YaprakTuru): yaprak biçimi ve renkleri
  - ağaç (AgacTuru): gövde, dal seviyeleri, yaprak kartlarının dizilişi
"""
from __future__ import annotations

import math

import numpy as np

from mf.agac import AgacTuru, Dal, Seviye, YaprakAyar, _boru, agac, meyve_yerleri
from mf.doku import TUYSU_TURLERI, YaprakTuru, serit_uv, yaprak_turu
from mf.mesh import Mesh, cone, icosphere, lathe, merge, tube
from mf.scene import Node

# --------------------------------------------------------------------------
# Yaprak dokuları
# --------------------------------------------------------------------------

# Rahmân 64 (müdhâmmetân): koyu yeşil, dolgun; parlak, yumurta biçimli yapraklar
yaprak_turu(YaprakTuru("koru", [(42, 102, 56), (52, 114, 62), (62, 126, 66), (38, 96, 62)], boy=(0.15, 0.21),
                       en=0.46, uc=1.2, dip=0.75, sayi=34, yan_dal=3, renk_oynama=0.07, sarimsi_uc=0.04, tohum=1))

# Sidr (Ali Ünal: "dal bastı kirazlar"): kiraz yaprağı gibi sivri uçlu, dişli, parlak yeşil
yaprak_turu(YaprakTuru("sidr", [(92, 156, 70), (108, 170, 76), (80, 142, 62), (120, 176, 80)], boy=(0.16, 0.22),
                       en=0.44, uc=1.35, dip=0.6, testere=0.07, dis_sayi=22, sayi=30, yan_dal=2, tohum=2))
# Nar (Rahmân 68): dar, parlak, kümeler hâlinde yapraklar
yaprak_turu(YaprakTuru("nar", [(78, 146, 58), (96, 160, 60), (112, 170, 64), (70, 132, 54)], boy=(0.11, 0.16),
                       en=0.26, uc=0.9, dip=0.9, sayi=46, yan_dal=3, aci=(25.0, 60.0), kivrim=0.15, parlak=0.14,
                       tohum=3))
# Üzüm (Nebe 32; İnsan 14): beş loplu, el biçimli yapraklar, uzun saplı
yaprak_turu(YaprakTuru("uzum", [(96, 158, 64), (112, 170, 70), (84, 146, 58), (120, 172, 74)], boy=(0.32, 0.42),
                       sayi=10, yan_dal=2, yan_boy=(0.25, 0.35), aci=(40.0, 80.0), sap=0.18, parlak=0.12,
                       bicim="uzum", dal_renk=(110, 86, 56), tohum=5))
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
        Seviye(sayi=10, bas=0.18, son=1.0, aci=50, aci_sapma=15, uzunluk=0.55, sekil="konik", egim=0.12,
               kivrim=0.45, yaricap=0.58, uc=0.3, segment=4, adim=0.8),
    ],
    yaprak=YaprakAyar("yaprak_koru", seviyeler=(2,), siklik=2.9, bas=0.2, boy=(1.6, 2.2), en=0.95,
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


# --------------------------------------------------------------------------
# Hurma (Tirmizî 3464): tüysü yapraklar, yaprak dipli gövde, sarkan salkımlar
# --------------------------------------------------------------------------

TUYSU_TURLERI["hurma"] = YaprakTuru("hurma", [(84, 146, 78), (96, 156, 82), (74, 132, 70), (104, 160, 84)],
                                    en=0.085, uc=0.9, dip=0.45, aci=(34.0, 46.0), dal_renk=(150, 150, 90),
                                    kivrim=0.03, parlak=0.12, sarimsi_uc=0.06, tohum=7)

HURMA_GOVDE = AgacTuru(boy=1.0, govde_r=1.0, govde_segment=12, kabuk_doku=0.7, kok=0.5, kok_lob=6, kok_boy=2.0,
                       kabuk_renk=(176, 156, 130), kabuk_renk_uc=(176, 156, 130))


def _serit_yaprak(taban, yon, uzunluk, en, kalkis, sarkma, katlanma, k, rng, dip=0.55, burgu=0.25):
    """Kavisli, orta damardan katlanmış şerit yaprak (hurma, muz): atlasın k. şeridi.
    katlanma > 0 kenarlar yukarıda (V), < 0 kenarlar sarkık. dip: yaprağın dipteki en oranı.
    (köşeler, yüzler, UV, orta damar boyunca t)"""
    yon = np.asarray(yon, float)
    yatay = np.array([yon[0], 0.0, yon[2]])
    yatay /= np.linalg.norm(yatay) + 1e-9
    yan = np.cross(yatay, [0.0, 1.0, 0.0])
    n = 11
    u0, u1 = serit_uv(k)
    V, UV, T = [], [], []
    b = rng.uniform(-burgu, burgu)
    for i in range(n):
        t = i / (n - 1)
        p = np.asarray(taban, float) + yatay * uzunluk * t * (1 - 0.15 * t)
        p[1] += uzunluk * (kalkis * t - sarkma * t * t)
        e = en * (dip + (1 - dip) * min(1.0, t / 0.25))
        a = b * t
        yan_t = yan * math.cos(a) + np.array([0.0, 1.0, 0.0]) * math.sin(a)
        yuk = np.cross(yan_t, yatay)
        yuk = yuk if yuk[1] > 0 else -yuk
        kat = katlanma * e * (1 - 0.5 * t)
        V += [p - yan_t * e * 0.5 + yuk * kat, p, p + yan_t * e * 0.5 + yuk * kat]
        v = 1.0 - t
        UV += [[u0, v], [(u0 + u1) / 2, v], [u1, v]]
        T += [t, t, t]
    F = []
    for i in range(n - 1):
        a0, b0 = 3 * i, 3 * (i + 1)
        F += [[a0, b0, a0 + 1], [a0 + 1, b0, b0 + 1], [a0 + 1, b0 + 1, a0 + 2], [a0 + 2, b0 + 1, b0 + 2]]
    return np.array(V), np.array(F), np.array(UV), np.array(T)


def _serit_mesh(parcalar, merkez, malzeme, golge_dip=0.72, dis=0.45):
    """Şerit yapraklardan tek Mesh: normaller yukarı bakan yüz normali ile tacın
    merkezinden dışa yönün karışımı; yaprak dipleri gölgede; rüzgâr uca doğru artar."""
    Vs, Fs, UVs, Ts, off = [], [], [], [], 0
    for v, f, uv, t in parcalar:
        Vs.append(v)
        Fs.append(f + off)
        UVs.append(uv)
        Ts.append(t)
        off += len(v)
    V, F, T = np.vstack(Vs), np.vstack(Fs), np.concatenate(Ts)
    tri = V[F]
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    fn = fn * np.sign(fn[:, 1:2] + 1e-9)
    N = np.zeros_like(V)
    for k in range(3):
        np.add.at(N, F[:, k], fn)
    N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-9
    d = V - np.asarray(merkez, float)
    d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
    N = N * (1 - dis) + d * dis
    N /= np.linalg.norm(N, axis=1, keepdims=True)
    golge = golge_dip + (1 - golge_dip) * np.clip(T / 0.35, 0, 1)
    CV = np.ones((len(V), 3)) * golge[:, None]
    W = np.clip(T, 0, 1) ** 1.4
    return Mesh(V.astype(np.float32), F, np.ones((len(F), 3), np.float32), malzeme, W=W.astype(np.float32),
                NV=N.astype(np.float32), CV=CV.astype(np.float32), UV=np.vstack(UVs).astype(np.float32))


def hurma_modeli(ad: str, olcek: float = 1.0, meyveli: bool = True) -> Node:
    """Olgun hurma (olcek 1): 5,5 m gövde, 26 yaprak, dört salkım. Fidanda olcek küçüktür."""
    rng = np.random.default_rng(31 + int(olcek * 10))
    boy = 5.5 * olcek
    # Gövde: hafif eğik ve kıvrık; dipte kök genişlemesi, tepede yaprak diplerinin kalınlığı
    egim = rng.uniform(0, 2 * math.pi)
    P = []
    for i in range(14):
        t = i / 13
        P.append([0.35 * olcek * t * t * math.cos(egim), -0.1 * olcek + boy * t, 0.35 * olcek * t * t * math.sin(egim)])
    P = np.array(P)
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    R = (0.23 - 0.03 * s / s[-1] + 0.05 * np.clip((s / s[-1] - 0.9) / 0.1, 0, 1)) * max(olcek, 0.45)
    dal = Dal(P, R, 0, 12, s)
    Vg, Fg, Ng, UVg = _boru(dal, HURMA_GOVDE, True)
    renk = np.array([222, 204, 178], np.float32) / 255
    kabuk = Mesh(Vg.astype(np.float32), Fg, np.tile(renk, (len(Fg), 1)), "kabuk_hurma",
                 NV=Ng.astype(np.float32), CV=np.tile(renk, (len(Vg), 1)).astype(np.float32),
                 UV=UVg.astype(np.float32))
    tepe = P[-1] + np.array([0.0, 0.05 * olcek, 0.0])
    # Yapraklar: sarmal dizilim; içtekiler genç ve dik, dıştakiler yatay ve sarkık
    sayi = 26 if olcek > 0.5 else 11
    parcalar = []
    for i in range(sayi):
        yas = i / (sayi - 1)                               # 0 genç (içte), 1 yaşlı (dışta)
        fi = math.radians(i * 137.5 + rng.uniform(-8, 8))
        yon = np.array([math.cos(fi), 0.0, math.sin(fi)])
        L = (3.6 * olcek + 0.4) * (0.75 + 0.25 * math.sin(math.pi * min(1.0, 0.2 + yas))) * rng.uniform(0.9, 1.05)
        kalkis = 1.25 - 1.05 * yas + rng.uniform(-0.08, 0.08)
        sarkma = 0.55 + 0.75 * yas
        taban = tepe + yon * 0.12 * olcek + np.array([0.0, -0.25 * olcek * yas, 0.0])
        parcalar.append(_serit_yaprak(taban, yon, L, (1.25 * olcek + 0.2) * rng.uniform(0.9, 1.05), kalkis, sarkma,
                                      0.28, int(rng.integers(4)), rng))
    yaprak = _serit_mesh(parcalar, tepe - np.array([0, 0.6 * olcek, 0]), "yaprak_hurma")
    root = Node(ad).add(kabuk, yaprak)
    if meyveli:
        root.add(_hurma_salkimlari(tepe, rng))
    return root


def _hurma_salkimlari(tepe, rng):
    """Taç altından kavislenip sarkan dört salkım: sapları altın sarısı, hurmalar kehribar."""
    parca = []
    for k in range(4):
        fi = math.radians(k * 90 + 40 + rng.uniform(-15, 15))
        yon = np.array([math.cos(fi), 0.0, math.sin(fi)])
        b = tepe + yon * 0.15 + np.array([0, -0.35, 0])
        yol = [b, b + yon * 0.35 + np.array([0, 0.05, 0]), b + yon * 0.6 + np.array([0, -0.35, 0]),
               b + yon * 0.7 + np.array([0, -0.8, 0])]
        parca.append(tube(yol, [0.03, 0.025, 0.02, 0.015], 5, "saman_koyu", cap=False))
        uc = np.array(yol[-1])
        for j in range(9):                                   # sarkan dallar (spikelet)
            a = rng.uniform(0, 2 * math.pi)
            dy = rng.uniform(0.35, 0.55)
            p0 = np.array(yol[2]) + (uc - np.array(yol[2])) * rng.uniform(0.2, 1.0)
            p1 = p0 + np.array([0.12 * math.cos(a), -dy, 0.12 * math.sin(a)])
            parca.append(tube([p0, (p0 + p1) / 2 + np.array([0.02, 0, 0]), p1], [0.008, 0.007, 0.005], 3,
                              "saman", cap=False))
            for m in range(5):
                q = p0 + (p1 - p0) * rng.uniform(0.25, 1.0) + rng.normal(0, 0.025, 3)
                parca.append(icosphere(0.028, 0, "hurma_meyve" if rng.random() < 0.7 else "hurma_meyve_koyu")
                             .scale(0.8, 1.3, 0.8).translate(*q).smooth(70))
    m = merge(*parca).with_material("meyve").paylasimli()
    m.W = np.clip((tepe[1] - m.V[:, 1]) / 1.5, 0, 1).astype(np.float32) * 0.4
    return m


# --------------------------------------------------------------------------
# Talh (Vâkıa 29, "dolgun salkımlı muzlar"): yalancı gövde, geniş yapraklar
# --------------------------------------------------------------------------

MUZ_GOVDE = AgacTuru(boy=1.0, govde_r=1.0, govde_segment=10, kabuk_doku=0.6, kok=0.35, kok_lob=4, kok_boy=1.5)


def _muz_bitkisi(taban, boy, egim_deg, yaprak_n, uzunluk, rng, salkim=False):
    """Bir muz bitkisi: yalancı gövde, gövde ucundan yayılan yapraklar, isteğe bağlı salkım."""
    e = math.radians(egim_deg)
    x0, z0 = taban
    P = []
    for i in range(8):
        t = i / 7
        P.append([x0 + math.sin(e) * boy * 0.2 * t * t, -0.05 + boy * t, z0 + math.cos(e) * boy * 0.08 * t * t])
    P = np.array(P)
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    R = (0.17 * boy / 3.2 + 0.03) * (1 - 0.4 * s / s[-1])
    Vg, Fg, Ng, UVg = _boru(Dal(P, R, 0, 10, s), MUZ_GOVDE, True)
    beyaz = np.array([0.92, 0.95, 0.85], np.float32)
    govde = Mesh(Vg.astype(np.float32), Fg, np.tile(beyaz, (len(Fg), 1)), "kabuk_muz", NV=Ng.astype(np.float32),
                 CV=np.tile(beyaz, (len(Vg), 1)).astype(np.float32), UV=UVg.astype(np.float32))
    ust = P[-1]
    parcalar = []
    for i in range(yaprak_n):
        fi = math.radians(360.0 * i / yaprak_n + rng.uniform(-14, 14))
        yas = (i % 3) / 2
        yon = np.array([math.cos(fi), 0.0, math.sin(fi)])
        L = uzunluk * rng.uniform(0.85, 1.05)
        parcalar.append(_serit_yaprak(ust + np.array([0, 0.04 * (1 - yas), 0]), yon, L, L * 0.26,
                                      1.2 - 0.35 * yas, 1.15 + 0.35 * yas, -0.12, int(rng.integers(4)), rng,
                                      dip=0.2, burgu=0.35))
    # Tepedeki dik, henüz açılmamış genç yaprak
    fi = rng.uniform(0, 2 * math.pi)
    parcalar.append(_serit_yaprak(ust, [math.cos(fi), 0, math.sin(fi)], uzunluk * 0.55, uzunluk * 0.07, 2.6, 1.0,
                                  0.35, int(rng.integers(4)), rng, dip=0.3, burgu=0.1))
    out = [govde, parcalar, ust]
    if salkim:
        out.append(_muz_salkimi(ust - np.array([0, 0.1, 0]), rng.uniform(0, 360), boy / 3.2, rng))
    return out


def _muz_salkimi(tepe, aci_deg, olcek, rng):
    """Gövde ucundan kavislenip sarkan sap, kat kat muz elleri (mandûd), uçta mor tomurcuk."""
    a = math.radians(aci_deg)
    d = np.array([math.cos(a), 0.0, math.sin(a)])
    t0 = np.asarray(tepe, float)
    sap = [t0, t0 + d * 0.35 * olcek + np.array([0, 0.08, 0]) * olcek,
           t0 + d * 0.6 * olcek + np.array([0, -0.35, 0]) * olcek,
           t0 + d * 0.66 * olcek + np.array([0, -1.15, 0]) * olcek]
    parca = [tube(sap, [0.045 * olcek, 0.04 * olcek, 0.035 * olcek, 0.03 * olcek], 6, "muz_govde").smooth(60)]
    P = np.asarray(sap)
    for k in range(7):
        t = 0.33 + 0.09 * k
        seg = min(int(t * 3), 2)
        u = t * 3 - seg
        q = P[seg] + (P[seg + 1] - P[seg]) * u
        n = 9 if k < 4 else 7
        for j in range(n):
            b = 2 * math.pi * j / n + k * 0.4 + rng.uniform(-0.1, 0.1)
            r = np.array([math.cos(b), 0.0, math.sin(b)])
            s = olcek * (1.0 - 0.06 * k)
            yol = [q + r * 0.05 * s, q + r * 0.12 * s + np.array([0, 0.02, 0]) * s,
                   q + r * 0.17 * s + np.array([0, 0.1, 0]) * s, q + r * 0.18 * s + np.array([0, 0.17, 0]) * s]
            parca.append(tube(yol, [0.02 * s, 0.026 * s, 0.022 * s, 0.008 * s], 6, "muz").smooth(60))
    uc = P[-1]
    tomurcuk = lathe([(0.0, 0.0), (0.06, 0.05), (0.085, 0.14), (0.06, 0.24), (0.0, 0.3)], 8, "muz_cicek")
    parca.append(tomurcuk.scale(olcek).rotate("x", 180).translate(uc[0], uc[1] + 0.04 * olcek, uc[2]).smooth(60))
    m = merge(*parca).with_material("meyve").paylasimli()
    m.W = np.full(len(m.V), 0.25, np.float32)
    return m


def muz_modeli(ad: str, olgun: bool) -> Node:
    rng = np.random.default_rng(24 if olgun else 23)
    root = Node(ad)
    if olgun:
        bitkiler = [_muz_bitkisi((0.0, 0.0), 3.3, 8, 8, 2.4, rng, salkim=True),
                    _muz_bitkisi((0.7, 0.35), 2.6, 60, 7, 2.1, rng, salkim=True),
                    _muz_bitkisi((-0.45, 0.55), 1.8, -40, 6, 1.6, rng)]
    else:
        bitkiler = [_muz_bitkisi((0.0, 0.0), 1.2, 10, 5, 0.95, rng)]
    parcalar = [p for b in bitkiler for p in b[1]]
    merkez = np.mean([b[2] for b in bitkiler], axis=0) - np.array([0, 0.8, 0])
    root.add(*[b[0] for b in bitkiler], _serit_mesh(parcalar, merkez, "yaprak_muz", golge_dip=0.8, dis=0.35))
    root.add(*[b[3] for b in bitkiler if len(b) > 3])
    return root


# --------------------------------------------------------------------------
# Üzüm asması: çardağın üstüne yayılan sürgünler (model cennet_bitkileri.py'de)
# --------------------------------------------------------------------------

UZUM = AgacTuru(boy=1.0, govde_r=1.0, govde_segment=7, kabuk_doku=0.45, kok=0.0,
                kabuk_renk=(134, 106, 84), kabuk_renk_uc=(128, 110, 76), tohum=33,
                yaprak=YaprakAyar("yaprak_uzum", seviyeler=(1,), siklik=4.2, bas=0.05, boy=(0.7, 0.95), en=0.95,
                                  disa=0.85, yukari=0.05, bukum=0.1, golge=0.35, alt_golge=0.5, dis_normal=0.7))


def asma(govdeler, surgunler, merkez, yari, olcek=1.0, tohum=33):
    """Asma: govdeler ve surgunler [(noktalar, yarıçaplar)]. (kabuk, yapraklar, surgun dalları, ruzgar)"""
    from mf.agac import _kartlar, _rgb, yaprak_orgusu
    rng = np.random.default_rng(tohum)
    merkez = np.asarray(merkez, float)
    yari = np.asarray(yari, float)

    def ruzgar(X):
        return np.clip(np.linalg.norm((X - merkez)[:, [0, 2]], axis=1) / (yari[[0, 2]].max() * 1.2), 0, 1) * 0.5

    def golge(X, guc, alt):
        e = np.linalg.norm((X - merkez) / yari, axis=1)
        g = 1 - guc * np.clip(1 - e, 0, 1) ** 0.8
        return g * (1 - alt * np.clip((merkez[1] - X[:, 1]) / yari[1], 0, 1))

    dallar = []
    for seviye, liste in ((0, govdeler), (1, surgunler)):
        for P, R in liste:
            P = np.asarray(P, float)
            s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
            dallar.append(Dal(P, np.asarray(R, float), seviye, 7 if seviye == 0 else 4, s))
    Vs, Fs, Ns, UVs, Cs, off = [], [], [], [], [], 0
    k0, k1 = _rgb(UZUM.kabuk_renk), _rgb(UZUM.kabuk_renk_uc)
    for d in dallar:
        v, f, nr, uv = _boru(d, UZUM, False)
        c = np.tile(k0 if d.seviye == 0 else k1, (len(v), 1))
        Vs.append(v); Fs.append(f + off); Ns.append(nr); UVs.append(uv); Cs.append(c)
        off += len(v)
    V = np.vstack(Vs)
    govde_agirlik = ruzgar(V) * np.clip((V[:, 1] - merkez[1] + yari[1]) / yari[1], 0, 1)
    kabuk = Mesh(V.astype(np.float32), np.vstack(Fs), np.tile(k0, (off, 1))[:1].repeat(len(np.vstack(Fs)), 0),
                 "kabuk", W=govde_agirlik.astype(np.float32), NV=np.vstack(Ns).astype(np.float32),
                 CV=np.clip(np.vstack(Cs) * golge(V, 0.3, 0.2)[:, None], 0, 1).astype(np.float32),
                 UV=np.vstack(UVs).astype(np.float32))
    kartlar = _kartlar(dallar, UZUM, olcek, rng)
    yapraklar = yaprak_orgusu(kartlar, UZUM.yaprak, merkez, yari, ruzgar, golge, rng)
    return kabuk, yapraklar, [d for d in dallar if d.seviye == 1], ruzgar
