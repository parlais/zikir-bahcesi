"""Ağaçların büyüme aşamaları (K16, K17): her şey zikirle oluşur, oyuncu her ağacın tohumdan
olguna büyümesini izler. Bu yüzden bütün aşamalar aynı dilde ve aynı kalitededir.

  a1 tohum: yeni işlenmiş dikim yeri (dokulu toprak tümseği) ve türün tohumu
  a2 filiz: sap ve türün gerçek yaprakları (tek yaprak atlası); talh, hurma ve servi kendi
            biçimleriyle (küçük muz, şerit yapraklar, pul yapraklı sürgünler)
  a3 fidan: türün küçük ölçekli, iki dal seviyeli hâli; dikim yerinde
  a4 olgun: türün kendisi (models/agaclar.py)
  Tûbâ beş aşamadır: tohum (nur çekirdeği), filiz, fidan, olgun, ulu (arsayı gölgeler).

Burada kaydolanlar: nar, servi, çınar, Tûbâ. Hurma, sidr, talh ve üzüm kendi dosyalarında
kaydolur ve buradaki yardımcıları kullanır.
"""
from __future__ import annotations

import math

import numpy as np

from mf.agac import _dik, _kart, agac, meyve_yerleri
from mf.doku import YaprakTuru, atlas_uv, tek_yaprak, tek_yaprak_uv
from mf.mesh import Mesh, cone, cylinder, icosphere, merge, tube
from mf.scene import Node

from . import asamali
from .agaclar import CINAR, NAR, TUBA, _muz_bitkisi, _serit_mesh, nar_modeli, selvi_modeli

# --------------------------------------------------------------------------
# Filizlerin tek yaprakları (atlas hücreleri kayıt sırasıyla)
# --------------------------------------------------------------------------

tek_yaprak(YaprakTuru("sidr", [(100, 166, 76)], en=0.44, uc=1.35, dip=0.6, testere=0.07, dis_sayi=22, tohum=2))
tek_yaprak(YaprakTuru("nar", [(104, 164, 62)], en=0.28, uc=0.9, dip=0.9, parlak=0.14, tohum=3))
tek_yaprak(YaprakTuru("uzum", [(106, 166, 68)], parlak=0.12, bicim="el", tohum=5))
tek_yaprak(YaprakTuru("cinar", [(86, 146, 66)], parlak=0.12, bicim="el", lop_us=0.6, lop_derinlik=0.5,
                      dis_gucu=0.03, tohum=8))
tek_yaprak(YaprakTuru("tuba", [(104, 168, 86)], en=0.44, uc=1.15, dip=0.7, parlak=0.18, kenar_isik=(255, 236, 170),
                      kenar_isik_gucu=0.85, tohum=9))
tek_yaprak(YaprakTuru("hurma", [(96, 156, 82)], en=0.13, uc=0.8, dip=0.3, parlak=0.1, tohum=7))


def _r(*c):
    """0-255 sRGB -> primitiflerin beklediği 0-1 demet."""
    return tuple(x / 255 for x in c)


# --------------------------------------------------------------------------
# Dikim yeri ve tohumlar
# --------------------------------------------------------------------------

def dikim_yeri(r=0.42, h=0.045, tohum=0) -> Mesh:
    """Yeni işlenmiş toprak: düzensiz kenarlı, ortası kabarık tümsek. Kenarı çimenin altına
    girer. Dokulu (yuzey_toprak), rüzgârda salınmaz."""
    rng = np.random.default_rng(tohum)
    halka, seg = 7, 28
    faz = rng.uniform(0, 2 * math.pi, 3)
    V, CV = [np.array([0.0, h, 0.0])], [np.array([0.34, 0.235, 0.16])]
    for i in range(1, halka + 2):
        for k in range(seg):
            a = 2 * math.pi * k / seg
            kenar = r * (1 + 0.08 * math.sin(3 * a + faz[0]) + 0.05 * math.sin(5 * a + faz[1]))
            rho = kenar * min(i, halka) / halka * (1.3 if i > halka else 1.0)
            t = rho / kenar
            # Yumuşak kubbe; kenar halkası çimenin altına iner (sert bir basamak kalmaz)
            y = h * max(0.0, 1 - t * t) ** 2.0 * (1 + 0.25 * math.sin(4 * a + faz[2]) * t) - 0.012 * t \
                if i <= halka else -0.035
            y += rng.uniform(-0.004, 0.004) * (i <= halka)
            V.append(np.array([rho * math.cos(a), y, rho * math.sin(a)]))
            # Ortası nemli ve koyu, kenarı açık
            CV.append(np.array([0.34, 0.235, 0.16]) * (1 - min(t, 1.0)) + np.array([0.44, 0.33, 0.23]) * min(t, 1.0))
    V = np.array(V)
    F = []
    for k in range(seg):
        F.append([0, 1 + (k + 1) % seg, 1 + k])
    for i in range(halka):
        for k in range(seg):
            a0 = 1 + i * seg + k
            b0 = 1 + i * seg + (k + 1) % seg
            c0 = 1 + (i + 1) * seg + (k + 1) % seg
            d0 = 1 + (i + 1) * seg + k
            F += [[a0, b0, c0], [a0, c0, d0]]
    F = np.array(F)
    tri = V[F]
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    fn *= np.sign(fn[:, 1:2] + 1e-12)
    F = np.where((np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])[:, 1] < 0)[:, None], F[:, ::-1], F)
    N = np.zeros_like(V)
    for k in range(3):
        np.add.at(N, F[:, k], fn)
    N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
    UV = V[:, [0, 2]] / 0.45
    CV = np.array(CV)
    return Mesh(V.astype(np.float32), F.astype(np.int64), np.tile(CV.mean(0), (len(F), 1)).astype(np.float32),
                "yuzey_toprak", W=np.zeros(len(V), np.float32), NV=N.astype(np.float32),
                CV=CV.astype(np.float32), UV=UV.astype(np.float32))


TOHUM_OLCEK = 1.6     # tohumlar gerçek boyundan biraz iri: dikim yerinde seçilsin


def _tohum_mesh(parcalar) -> Mesh:
    m = merge(*parcalar).with_material("meyve").paylasimli()
    # Dikim yerinin tepesine oturacak biçimde, tabanı sabit kalarak büyüt
    taban = m.V[:, 1].min()
    m.V = ((m.V - np.array([0, taban, 0])) * TOHUM_OLCEK + np.array([0, taban - 0.012, 0])).astype(np.float32)
    m.W = np.zeros(len(m.V), np.float32)
    return m


def tohum_hurma(y):
    """Hurma çekirdeği: uzun, bir yanı oluklu."""
    govde = icosphere(0.022, 2, _r(150, 112, 74)).scale(0.62, 0.55, 1.0).smooth(80)
    oluk = tube([[0, 0.0122, -0.018], [0, 0.0128, 0.0], [0, 0.0122, 0.018]], [0.0016, 0.0018, 0.0016], 4,
                _r(98, 70, 44), cap=False)
    return _tohum_mesh([m.rotate("y", 30).translate(0.02, y + 0.008, 0.0) for m in (govde, oluk)])


def tohum_sidr(y):
    """Sidr: kiraz gibi küçük, parlak kırmızı-kahve meyve ve kuru sapı."""
    meyve = icosphere(0.018, 2, _r(150, 40, 44)).scale(1.0, 0.9, 1.0).smooth(80).translate(0.015, y + 0.012, 0)
    sap = tube([[0.015, y + 0.028, 0], [0.02, y + 0.045, 0.004], [0.03, y + 0.05, 0.01]], [0.0018, 0.0015, 0.0012], 3,
               _r(110, 86, 56), cap=False)
    return _tohum_mesh([meyve, sap])


def tohum_uzum(y):
    """Üzüm çekirdeği: armut biçimli, kahverengi; yanında buruşuk bir tane."""
    c1 = icosphere(0.011, 2, _r(122, 84, 48)).scale(0.8, 0.7, 1.25).rotate("y", 25).smooth(80).translate(0.012, y + 0.006, 0)
    tane = icosphere(0.02, 2, _r(96, 50, 96)).scale(1.0, 0.8, 1.0).jitter(0.002, 3).smooth(70).translate(-0.02, y + 0.012, 0.01)
    return _tohum_mesh([c1, tane])


def tohum_nar(y):
    """Nar taneleri: yakut gibi parlak üç dört tane."""
    rng = np.random.default_rng(4)
    parca = []
    for i in range(4):
        a = i * 1.7
        parca.append(icosphere(0.011, 2, _r(186, 26, 52) if i % 2 else _r(206, 44, 70)).scale(0.85, 1.0, 1.2)
                     .rotate("y", math.degrees(a)).smooth(80)
                     .translate(0.018 * math.cos(a) + rng.uniform(-0.003, 0.003), y + 0.009, 0.018 * math.sin(a)))
    return _tohum_mesh(parca)


def tohum_servi(y):
    """Servi kozalağı: yuvarlak, pullu, gri kahve."""
    koz = icosphere(0.02, 1, _r(126, 110, 90)).jitter(0.003, 11).smooth(30).translate(0.012, y + 0.016, 0)
    return _tohum_mesh([koz])


def tohum_cinar(y):
    """Çınar tohum topu: tüylü, sarı kahve top ve kısa sapı."""
    top = icosphere(0.02, 2, _r(170, 140, 84)).jitter(0.0025, 13).smooth(40).translate(0.012, y + 0.018, 0)
    sap = tube([[0.012, y + 0.036, 0], [0.02, y + 0.06, 0.01], [0.04, y + 0.07, 0.02]], [0.0018, 0.0015, 0.0012], 3,
               _r(116, 96, 66), cap=False)
    return _tohum_mesh([top, sap])


def tohum_muz(y):
    """Talh (muz) tohumla değil kökten sürgünle çoğalır: toprağın içinden yeşil bir sürgün ucu."""
    sogan = icosphere(0.035, 2, _r(150, 150, 96)).scale(1.0, 0.6, 1.0).smooth(80).translate(0, y - 0.004, 0)
    uc = cone(0.016, 0.07, 7, _r(122, 170, 84)).smooth(60).translate(0, y + 0.012, 0)
    return _tohum_mesh([sogan, uc])


# --------------------------------------------------------------------------
# Filiz
# --------------------------------------------------------------------------

def _yaprak_dortgen(taban, yon, boy, tek, bukum=0.12, sarkma=0.18):
    """Tek yaprak dörtgeni (2×3 köşe): dibi taban, ucu yon boyunca; ortası kabarık, ucu sarkık."""
    yon = np.asarray(yon, float) / np.linalg.norm(yon)
    en_yon = np.cross(yon, [0.0, 1.0, 0.0])
    if np.linalg.norm(en_yon) < 1e-3:
        en_yon = _dik(yon)
    en_yon /= np.linalg.norm(en_yon)
    nrm = np.cross(en_yon, yon)
    nrm = nrm if nrm[1] >= 0 else -nrm
    taban = np.asarray(taban, float)
    orta = taban + yon * boy * 0.5 + nrm * bukum * boy
    ust = taban + yon * boy + np.array([0, -sarkma * boy, 0])
    V = np.array([taban - en_yon * boy * 0.5, taban + en_yon * boy * 0.5, orta - en_yon * boy * 0.5,
                  orta + en_yon * boy * 0.5, ust - en_yon * boy * 0.5, ust + en_yon * boy * 0.5])
    u0, v0, u1, v1 = tek_yaprak_uv(tek)
    UV = np.array([[u0, v1], [u1, v1], [u0, (v0 + v1) / 2], [u1, (v0 + v1) / 2], [u0, v0], [u1, v0]])
    F = np.array([[0, 1, 3], [0, 3, 2], [2, 3, 5], [2, 5, 4]])
    return V, F, UV, nrm


def _yaprak_mesh(parcalar, malzeme, yukseklik) -> Mesh:
    V, F, UV, N, off = [], [], [], [], 0
    for v, f, uv, nrm in parcalar:
        V.append(v)
        F.append(f + off)
        UV.append(uv)
        N.append(np.tile(nrm * 0.6 + np.array([0, 0.4, 0]), (len(v), 1)))
        off += len(v)
    V, F, N = np.vstack(V), np.vstack(F), np.vstack(N)
    N /= np.linalg.norm(N, axis=1, keepdims=True)
    W = np.clip(V[:, 1] / max(yukseklik, 1e-3), 0, 1) * 0.12      # sap salınmaz; yapraklar yalnız kıpırdar
    return Mesh(V.astype(np.float32), F, np.ones((len(F), 3), np.float32), malzeme, W=W.astype(np.float32),
                NV=N.astype(np.float32), CV=np.full((len(V), 3), 0.96, np.float32), UV=np.vstack(UV).astype(np.float32))


def filiz(tek, sap_boy, yapraklar, y0=0.05, sap_r=0.006, sap_renk=(0.44, 0.56, 0.26), tohum=0):
    """İnce, hafif kıvrık sap ve dizili gerçek yapraklar. yapraklar: [(t sap boyunca, yön açısı
    (derece), yaprak boyu (m), kalkış açısı (derece))]. (sap Mesh, yaprak Mesh)"""
    rng = np.random.default_rng(tohum)
    faz = rng.uniform(0, 2 * math.pi)
    yol = [np.array([0.012 * math.sin(faz + 3 * t) * t, y0 - 0.01 + sap_boy * t, 0.012 * math.cos(faz + 2 * t) * t])
           for t in np.linspace(0, 1, 7)]
    sap = tube(yol, list(np.linspace(sap_r, sap_r * 0.45, 7)), 6, sap_renk).smooth(70)
    parcalar, saplar = [], [sap]
    for t, aci, boy, kalkis in yapraklar:
        i = min(int(t * 6), 5)
        p = yol[i] + (yol[i + 1] - yol[i]) * (t * 6 - i)
        a, k = math.radians(aci), math.radians(kalkis)
        d = np.array([math.cos(a) * math.cos(k), math.sin(k), math.sin(a) * math.cos(k)])
        q = p + d * boy * 0.18
        saplar.append(tube([p, (p + q) / 2 + np.array([0, 0.004, 0]), q], [sap_r * 0.35, sap_r * 0.3, sap_r * 0.25], 3,
                           sap_renk, cap=False))
        parcalar.append(_yaprak_dortgen(q, d + np.array([0, -0.15, 0]), boy, tek))
    sap_m = merge(*saplar).with_material("govde")
    return sap_m, _yaprak_mesh(parcalar, "yaprak_tek", y0 + sap_boy)


def serit_filiz(tek, yapraklar, y0=0.04):
    """Hurma fidesi gibi sapsız, topraktan çıkan şerit yapraklar: [(yön açısı, boy, kalkış)]."""
    parcalar = []
    for aci, boy, kalkis in yapraklar:
        a, k = math.radians(aci), math.radians(kalkis)
        d = np.array([math.cos(a) * math.cos(k), math.sin(k), math.sin(a) * math.cos(k)])
        parcalar.append(_yaprak_dortgen(np.array([0.0, y0, 0.0]), d, boy, tek, bukum=0.05, sarkma=0.3))
    return _yaprak_mesh(parcalar, "yaprak_tek", y0 + 0.3)


def servi_filizi(boy=0.32):
    """Küçük servi: ince sap ve yukarı bakan pul yapraklı sürgünler (servi atlası)."""
    rng = np.random.default_rng(66)
    sap = tube([[0, 0.03, 0], [0.004, 0.03 + boy * 0.5, 0], [0, 0.03 + boy, 0.003]], [0.007, 0.005, 0.003], 5,
               _r(120, 100, 80)).smooth(60)
    V, F, UV, FN = [], [], [], []
    for i in range(9):
        t = 0.2 + 0.8 * i / 8
        a = i * 2.4
        p = np.array([0.0, 0.03 + boy * t, 0.0])
        yon = np.array([math.cos(a) * 0.45, 1.0, math.sin(a) * 0.45])
        yon /= np.linalg.norm(yon)
        en_yon = _dik(yon)
        b = boy * (0.55 - 0.3 * t) * rng.uniform(0.9, 1.1)
        v, f, nrm = _kart(p, yon, en_yon, b, b * 0.8, 0.05)
        u0, v0, u1, v1 = atlas_uv(int(rng.integers(4)))
        F.append(f + len(V) * 6)
        V.append(v)
        UV.append(np.array([[u0, v1], [u1, v1], [u0, (v0 + v1) / 2], [u1, (v0 + v1) / 2], [u0, v0], [u1, v0]]))
        FN.append(np.repeat(nrm[None], 6, 0))
    V, F = np.vstack(V), np.vstack(F)
    d = V - np.array([0, 0.03 + boy * 0.5, 0])
    N = d / (np.linalg.norm(d, axis=1, keepdims=True) + 1e-9)
    yap = Mesh(V.astype(np.float32), F, np.ones((len(F), 3), np.float32), "yaprak_selvi",
               W=(np.clip(V[:, 1] / (boy + 0.03), 0, 1) * 0.12).astype(np.float32), NV=N.astype(np.float32),
               CV=np.full((len(V), 3), 0.92, np.float32), UV=np.vstack(UV).astype(np.float32))
    return sap.with_material("govde"), yap


def muz_filizi():
    """Talh filizi: kökten çıkan, üç yapraklı küçük muz sürgünü."""
    rng = np.random.default_rng(22)
    govde, parcalar, ust = _muz_bitkisi((0.0, 0.0), 0.26, 6, 3, 0.3, rng)
    return govde, _serit_mesh(parcalar, ust - np.array([0, 0.1, 0]), "yaprak_muz", golge_dip=0.85, dis=0.3)


# --------------------------------------------------------------------------
# Tûbâ: nur çekirdeği ve nurlu kökler (her aşamada dipte kalır)
# --------------------------------------------------------------------------

def nur_kokleri(r_ic, r_dis, n, kalinlik, tohum=92, y=0.012):
    """Tûbâ'nın dibinden toprağa yayılan ince nur kökleri (nur malzemesi, kendi ışığıyla)."""
    rng = np.random.default_rng(tohum)
    kokler = []
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.3, 0.3)
        L = rng.uniform(0.6, 1.0) * (r_dis - r_ic)
        pts = []
        for t in np.linspace(0, 1, 7):
            r = r_ic + L * t
            b = a + 0.35 * math.sin(t * 3 + i)
            pts.append([r * math.cos(b), y + 0.02 * (1 - t) * (r_ic > 0.2), r * math.sin(b)])
        kokler.append(tube(pts, list(np.linspace(kalinlik, kalinlik * 0.25, 7)), 4, "nur", cap=False))
    m = merge(*kokler).with_material("nur")
    m.W = np.zeros(len(m.V), np.float32)
    return m


def tuba_cekirdegi(ad: str) -> Node:
    """Oyuncunun arsasının ortasındaki ışıklı Tûbâ çekirdeği (Küllî Kaideler 1). Toprağa ince
    nur kökleri salmış; Godot "isik_cekirdek" noktasına ışık ve parıltı koyar."""
    root = Node(ad)
    tohum = icosphere(0.085, 2, "nur_beyaz").scale(0.85, 1.15, 0.85).translate(0, 0.13, 0).smooth(80)
    root.add(dikim_yeri(0.6, 0.11, tohum=91), tohum.with_material("nur"), nur_kokleri(0.08, 0.62, 7, 0.012))
    root.add(Node("isik_cekirdek", translation=(0.0, 0.25, 0.0)))
    return root


def tuba_filizi(ad: str) -> Node:
    """Tûbâ filizi (33 tevhid): altın-fildişi sap, nurlu kenarlı ilk yapraklar; dipte çekirdeğin nuru."""
    root = Node(ad)
    sap, yap = filiz("tuba", 0.5, [(0.35, 20, 0.15, 25), (0.5, 160, 0.16, 22), (0.66, 280, 0.16, 28),
                                   (0.82, 60, 0.14, 35), (0.95, 200, 0.12, 55)],
                     y0=0.1, sap_r=0.01, sap_renk=_r(214, 204, 160), tohum=93)
    root.add(dikim_yeri(0.6, 0.11, tohum=91), sap, yap, nur_kokleri(0.05, 0.6, 7, 0.01))
    root.add(Node("isik_cekirdek", translation=(0.0, 0.16, 0.0)))
    return root


def _nur_cicekleri(kartlar_V, merkez, yari, sayi, boy, tohum):
    """Tacın dış kabuğunda seyrek, kendi ışığıyla parlayan küçük nur çiçekleri."""
    rng = np.random.default_rng(tohum)
    e = np.linalg.norm((kartlar_V - merkez) / yari, axis=1)
    dis = kartlar_V[e > 0.75]
    if len(dis) == 0:
        return None
    sec = dis[rng.choice(len(dis), size=min(sayi, len(dis)), replace=False)]
    parca = [icosphere(boy * rng.uniform(0.7, 1.2), 0, "nur_beyaz").translate(*p) for p in sec]
    m = merge(*parca).with_material("nur").paylasimli()
    return m


def tuba_agaci(ad: str, olcek: float, seviye: int | None = None) -> Node:
    """Tûbâ'nın fidan, olgun ve ulu aşamaları: aynı türün ölçekli hâli. Dipte çekirdeğin nuru
    (ışık noktası ve nur kökleri), tacın dış yüzünde nur çiçekleri, tacın içinde nur zerreleri
    için bir işaret (nur_tac: konum tacın merkezi, ölçek tacın yarı boyutları)."""
    kabuk, yapraklar, dallar, ruzgar = agac(TUBA, olcek=olcek, seviye_sayisi=seviye)
    root = Node(ad).add(kabuk, *yapraklar)
    V = yapraklar[0].V
    merkez = V.mean(0)
    yari = np.maximum(np.percentile(np.abs(V - merkez), 92, axis=0), 0.3)
    cicek = _nur_cicekleri(V, merkez, yari, int(25 + 260 * min(olcek, 1.0) ** 2), 0.02 + 0.045 * olcek, 97)
    if cicek is not None:
        cicek.W = ruzgar(cicek.V).astype(np.float32)
        root.add(cicek)
    r_gov = TUBA.govde_r * olcek
    if olcek < 0.3:
        # Fidan: çekirdeğin nur kökleri hâlâ toprağın üstünde, dipte küçük bir nur
        root.add(nur_kokleri(r_gov * 1.4, r_gov * 1.4 + 0.9, 8, 0.012, y=0.02), dikim_yeri(0.6 + r_gov, 0.1, tohum=94))
        root.add(Node("isik_cekirdek", translation=(0.0, 0.25, 0.0), scale=(0.55, 0.55, 0.55)))
    else:
        # Olgun ve ulu: nur, gövdenin dibinde kök aralarından sızar (payanda köklerin arası)
        for i in range(TUBA.kok_lob):
            a = 2 * math.pi * (i + 0.5) / TUBA.kok_lob - 0.7 / TUBA.kok_lob
            rr = r_gov * (1.0 + 1.4 * TUBA.kok * 0.45)
            root.add(Node(f"isik_kok_{i}", translation=(rr * math.cos(a), 0.15 + 0.2 * olcek, rr * math.sin(a)),
                          scale=(0.6 * olcek + 0.3,) * 3))
    root.add(Node("nur_tac", translation=tuple(float(x) for x in merkez), scale=tuple(float(x) for x in yari)))
    return root


# --------------------------------------------------------------------------
# Kayıtlar: nar, servi, çınar, Tûbâ
# --------------------------------------------------------------------------

@asamali("ZB_agac_nar", 4)
def nar_asamalari(asama: int) -> Node:
    """Nar (Rahmân 68; Rahmân suresiyle büyür)."""
    ad = f"ZB_agac_nar_a{asama}"
    if asama == 1:
        return Node(ad).add(dikim_yeri(tohum=31), tohum_nar(0.06))
    if asama == 2:
        sap, yap = filiz("nar", 0.38, [(0.3, 0, 0.12, 30), (0.3, 180, 0.12, 30), (0.55, 90, 0.13, 35),
                                       (0.55, 270, 0.13, 35), (0.78, 45, 0.12, 45), (0.78, 225, 0.12, 45),
                                       (0.96, 130, 0.1, 65)], sap_r=0.008, tohum=32)
        return Node(ad).add(dikim_yeri(tohum=32), sap, yap)
    if asama == 3:
        kabuk, yapraklar, _, _ = agac(NAR, olcek=0.4, seviye_sayisi=2)
        return Node(ad).add(dikim_yeri(0.45, tohum=33), kabuk, *yapraklar)
    return nar_modeli(ad)


@asamali("ZB_agac_servi", 4)
def servi_asamalari(asama: int) -> Node:
    """Servi (Ya Vâhid; elif gibi dimdik, vahdet sembolü)."""
    ad = f"ZB_agac_servi_a{asama}"
    if asama == 1:
        return Node(ad).add(dikim_yeri(tohum=41), tohum_servi(0.06))
    if asama == 2:
        return Node(ad).add(dikim_yeri(tohum=42), *servi_filizi())
    if asama == 3:
        return selvi_modeli(ad, olcek=0.3).add(dikim_yeri(0.45, tohum=43))
    return selvi_modeli(ad)


def _cinar_tohum_toplari(dallar, ruzgar, sayi, olcek=1.0):
    """Çınarın uzun saplarından sarkan tohum topları (ikişer üçer)."""
    rng = np.random.default_rng(72)
    parca = []
    for p, tn, r in meyve_yerleri(dallar, (3,), sayi, 73, bas=0.3):
        q = p + np.array([rng.uniform(-0.03, 0.03), -0.12 * olcek, rng.uniform(-0.03, 0.03)])
        parca.append(tube([p, (p + q) / 2 + np.array([0.01, 0, 0]), q], [0.004, 0.0035, 0.003], 3,
                          _r(120, 104, 70), cap=False))
        for j in range(int(rng.integers(1, 3))):
            parca.append(icosphere(0.024 * max(olcek, 0.6), 1, _r(158, 132, 78) if j % 2 else _r(140, 122, 70))
                         .jitter(0.003, j + len(parca)).smooth(50).translate(*(q + np.array([0, -0.035 * j, 0]))))
    m = merge(*parca).with_material("meyve").paylasimli()
    m.W = ruzgar(m.V).astype(np.float32)
    return m


@asamali("ZB_agac_cinar", 4)
def cinar_asamalari(asama: int) -> Node:
    """Çınar (Allahu Ekber; azamet): alacalı kabuklu, yayvan, ulu ağaç."""
    ad = f"ZB_agac_cinar_a{asama}"
    if asama == 1:
        return Node(ad).add(dikim_yeri(tohum=71), tohum_cinar(0.06))
    if asama == 2:
        sap, yap = filiz("cinar", 0.4, [(0.45, 30, 0.17, 22), (0.72, 200, 0.18, 28), (0.97, 100, 0.15, 55)],
                         sap_r=0.009, sap_renk=_r(128, 140, 80), tohum=72)
        return Node(ad).add(dikim_yeri(tohum=72), sap, yap)
    if asama == 3:
        kabuk, yapraklar, _, _ = agac(CINAR, olcek=0.28, seviye_sayisi=2)
        return Node(ad).add(dikim_yeri(0.5, tohum=73), kabuk, *yapraklar)
    kabuk, yapraklar, dallar, ruzgar = agac(CINAR)
    return Node(ad).add(kabuk, *yapraklar, _cinar_tohum_toplari(dallar, ruzgar, 40))


@asamali("ZB_agac_tuba", 5)
def tuba_asamalari(asama: int) -> Node:
    """Tûbâ (K17): toplam tevhidle büyür: tohum 1, filiz 33, fidan 100, olgun 1000, ulu 10000."""
    ad = f"ZB_agac_tuba_a{asama}"
    if asama == 1:
        return tuba_cekirdegi(ad)
    if asama == 2:
        return tuba_filizi(ad)
    if asama == 3:
        return tuba_agaci(ad, 0.2, seviye=2)
    if asama == 4:
        return tuba_agaci(ad, 0.5)
    return tuba_agaci(ad, 1.0)
