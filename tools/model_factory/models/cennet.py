"""Cennet mekânı (Faz 2a, K10): uzanıp giden 8 yatay tabaka.

Kurgu (docs/kararlar.md K10, docs/mekan-kurgusu.md):
  - Cennet 8 yatay tabakadır, her tabaka uçsuz bucaksızdır. En üstte Firdevs;
    ortasında dört ırmağın kaynağı; üstte her şeyi kuşatan ışık (Arş tasvir edilmez).
  - İçeriden: ufuk açık; göğe bakınca üst tabaka görünmez (atmosfer tabakası gibi).
    Dört ırmak (Muhammed 15) üst tabakadan gelir: uzakta bulutların içinden inen
    çağlayanlar olarak görünür, ovada kıvrılarak akar.
  - Katlar arası çiçekli taş merdivenler bulutların içinden ışığa yükselir.
  - Dışarıdan (açılış, katlar arası geçiş): Dünya'nın katman resimleri gibi bir kesit.
  - Oyuncu arsası düz ve boş bir çayırdır (Tirmizî 3462), sınırı inci ve yakut çakıl.

Koordinatlar: metre, Y yukarı. Oyuncu arsası (0, 0, 0); ırmaklar kuzeyden (-z) gelir.

Modeller:
  ZB_dunya_cennet     ilk katın ovası (ufka kadar) ve dört ırmak
  ZB_dunya_selaleler  gökten, bulutların içinden inen dört çağlayan
Kesit (8 tabakanın dıştan görünümü) models/kesit.py içindedir: ilk kat bu dünyanın
kendisidir; KESME_Z düzleminde ikiye bölünür (ilk_kat_kesimi).
Yerleşim game/data/dunya_cennet.json dosyasına yazılır.
"""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy.spatial import Delaunay, cKDTree

from mf.mesh import Mesh, box, icosphere, lathe, merge
from mf.palette import renk
from mf.scene import Node

from . import model
from .cennet_yapilari import MERDIVEN_UST
from .sahne import _noise2

ARSA_R = 13.0                # oyuncu arsasının yarıçapı
YAKIN = (-70.0, -100.0, 70.0, 45.0)   # çimen ızgarası (x0, z0, x1, z1), 1 m adım
OVA_R = 9000.0               # ovanın uzandığı yarıçap (ötesi pusta kaybolur)
SELALE_UST = 360.0           # gökten inen çağlayanların başladığı yükseklik (bulutun içi)
# Kesit (K10): ilk kat bu dikey düzlemde kesilir. İç kameraların (ufuk z=38, arsa z=21)
# arkasında kalır; içeride kesit hiç görünmez. Dört ırmak da bu düzlemi arsanın iki yanında keser.
KESME_Z = 60.0
# Kesit kamerası (K18): 8 kat dikey kadraja sığar; önden, tele (şimdiki kompozisyon), 6° yukarıdan
KESIT_KAMERA = {"konum": [0.0, 8809.0, 48194.0], "hedef": [0.0, 3750.0, 60.0], "fov": 10.5}

# Dört ırmak: kaynak (gökten inen çağlayanın dibi) ve kontrol noktaları (x, z)
IRMAKLAR = [
    dict(ad="su", gen=16.0, noktalar=[(-330, -1250), (-190, -1080), (-110, -900), (-160, -560), (-75, -450),
                                      (-120, -320), (-55, -215), (-62, -140), (-50, -85), (-36, -40), (-31, 0),
                                      (-38, 40), (-70, 130), (-55, 260), (-80, 420)]),
    dict(ad="sut", gen=12.0, noktalar=[(330, -1350), (210, -1150), (230, -900), (175, -560), (110, -440),
                                       (165, -320), (95, -200), (125, -110), (82, -30), (74, 40), (100, 140),
                                       (85, 300), (110, 420)]),
    dict(ad="bal", gen=11.0, noktalar=[(-760, -1150), (-660, -980), (-560, -800), (-450, -620), (-395, -470),
                                       (-300, -340), (-265, -190), (-205, -60), (-215, 60), (-260, 200),
                                       (-230, 420)]),
    dict(ad="serbet", gen=11.0, noktalar=[(720, -1250), (620, -1050), (520, -850), (430, -610), (390, -450),
                                          (300, -320), (255, -170), (225, -40), (250, 90), (285, 220), (270, 420)]),
]

# Katlar arası merdiven: ayağı ovada, ucu bulutun içinde (yerleşimde dönüş ve ölçekle)
MERDIVEN = (70.0, -150.0, 16.0, 1.0)     # x, z, y ekseninde dönüş (derece), ölçek


# --------------------------------------------------------------------------
# Yardımcılar
# --------------------------------------------------------------------------

def _ss(a, b, x):
    t = np.clip((np.asarray(x, float) - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def _egri(noktalar, adim):
    """Catmull-Rom eğrisi; yaklaşık `adim` aralıklı örnekler."""
    P = np.asarray(noktalar, float)
    P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        n = max(2, int(math.ceil(np.linalg.norm(p2 - p1) / adim)))
        for t in np.arange(n) / n:
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-2])
    return np.asarray(out)


def _dik(P):
    """Yol boyunca sola bakan yatay birim normaller."""
    T = np.gradient(P, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-12
    return np.stack([-T[:, 1], T[:, 0]], axis=1)


def _kose_normalleri(V, F):
    tri = V[F]
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    N = np.zeros_like(V)
    for k in range(3):
        np.add.at(N, F[:, k], fn)
    return (N / (np.linalg.norm(N, axis=1, keepdims=True) + 1e-12)).astype(np.float32)


def _izgara(V, nu, nv, CV, material, W=None) -> Mesh:
    """(nv+1) x (nu+1) köşeli ızgara; köşe renkleri CV (n, 3)."""
    F = []
    for j in range(nv):
        for i in range(nu):
            a = j * (nu + 1) + i
            b, c, d = a + 1, a + nu + 2, a + nu + 1
            F += [[a, c, b], [a, d, c]]
    F = np.asarray(F, np.int64)
    V = np.asarray(V, np.float32)
    CV = np.asarray(CV, np.float32)
    C = CV[F].mean(1)
    m = Mesh(V, F, C, material, W=None if W is None else np.asarray(W, np.float32))
    m.NV = _kose_normalleri(V, F)
    m.CV = CV
    return m


def _kes(m: Mesh, z0: float):
    """Mesh'i z = z0 dikey düzleminde ikiye böler: (arka: z <= z0, on: z > z0, cizgi).
    Düzlemi kesen üçgenler kenarları boyunca bölünür; yeni köşelerin konumu, köşe rengi,
    normali ve ağırlığı kenar boyunca doğrusal enterpole edilir. Yüzey birebir aynı
    kalır (iki parçanın birleşimi eski yüzeydir); iki parça kesme çizgisindeki köşeleri
    paylaşır, aralarında boşluk yoktur. cizgi: kesme çizgisinin x'e göre sıralı (x, y)
    noktaları (kesit yüzünün üst kenarı). İndeksli mesh ister (CV ve NV verilmiş)."""
    assert m.CV is not None, "_kes indeksli mesh ister (CV)"
    V = m.V.astype(np.float64)
    d = V[:, 2] - z0
    d = np.where(np.abs(d) < 1e-4, -1e-4, d)          # düzlemdeki köşe arka tarafa sayılır
    on_k = d > 0
    yeniV, yeniCV, yeniNV, yeniW = [], [], [], []
    kenar = {}

    def kes_nokta(a, b):
        anahtar = (min(a, b), max(a, b))
        if anahtar not in kenar:
            t = d[a] / (d[a] - d[b])
            kenar[anahtar] = len(V) + len(yeniV)
            yeniV.append(V[a] + (V[b] - V[a]) * t)
            yeniCV.append(m.CV[a] + (m.CV[b] - m.CV[a]) * t)
            yeniNV.append(m.NV[a] + (m.NV[b] - m.NV[a]) * t)
            yeniW.append(m.W[a] + (m.W[b] - m.W[a]) * t)
        return kenar[anahtar]

    arka_F, arka_C, on_F, on_C = [], [], [], []
    tf = on_k[m.F]
    for fi in np.nonzero(tf.any(1) & ~tf.all(1))[0]:
        f = m.F[fi]
        s = tf[fi]
        # Yalnız kalan köşe (tek başına bir tarafta olan) başa alınır, sıra (yön) korunur
        yalniz = int(np.nonzero(s != (s.sum() >= 2))[0][0])
        a, b, c = f[yalniz], f[(yalniz + 1) % 3], f[(yalniz + 2) % 3]
        pab, pac = kes_nokta(a, b), kes_nokta(a, c)
        uc = [[a, pab, pac]]
        dort = [[pab, b, c], [pab, c, pac]]
        if on_k[a]:
            on_F += uc; on_C += [m.C[fi]]
            arka_F += dort; arka_C += [m.C[fi]] * 2
        else:
            arka_F += uc; arka_C += [m.C[fi]]
            on_F += dort; on_C += [m.C[fi]] * 2
    tum_on = tf.all(1)
    tum_arka = ~tf.any(1)
    V2 = np.vstack([V, np.asarray(yeniV).reshape(-1, 3)]).astype(np.float32)
    CV2 = np.vstack([m.CV, np.asarray(yeniCV).reshape(-1, 3)]).astype(np.float32)
    NV2 = np.vstack([m.NV, np.asarray(yeniNV).reshape(-1, 3)]).astype(np.float32)
    W2 = np.concatenate([m.W, np.asarray(yeniW, np.float32)]).astype(np.float32)

    def parca(F_eski, C_eski, F_ek, C_ek):
        F = np.vstack([F_eski, np.asarray(F_ek, np.int64).reshape(-1, 3)])
        C = np.vstack([C_eski, np.asarray(C_ek, np.float32).reshape(-1, 3)])
        kullan = np.unique(F)
        yeni = np.full(len(V2), -1, np.int64)
        yeni[kullan] = np.arange(len(kullan))
        p = Mesh(V2[kullan], yeni[F], C.astype(np.float32), m.material, W=W2[kullan])
        p.NV = NV2[kullan]
        p.CV = CV2[kullan]
        return p

    arka = parca(m.F[tum_arka], m.C[tum_arka], arka_F, arka_C)
    on = parca(m.F[tum_on], m.C[tum_on], on_F, on_C)
    cizgi = np.asarray(yeniV).reshape(-1, 3)[:, :2] if yeniV else np.zeros((0, 2))
    cizgi = cizgi[np.argsort(cizgi[:, 0])]
    return arka, on, cizgi


def _yuz_yonu(m: Mesh, yon) -> Mesh:
    """Yüzlerin çoğunluğu verilen yöne baksın (gerekirse çevir)."""
    tri = m.V[m.F]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    if (n @ np.asarray(yon, np.float32)).sum() < 0:
        m = m.flipped()
        m.NV = -m.NV
    return m


# --------------------------------------------------------------------------
# Ova yüksekliği ve ırmaklar
# --------------------------------------------------------------------------

def ova_y(x, z):
    """Ova: kuzeye doğru çok hafif yükselir (ırmaklar güneye akar); uzakta alçak,
    geniş tepeler ufku yumuşatır; arsa çevresi düzdür."""
    x = np.asarray(x, float)
    z = np.asarray(z, float)
    d = np.hypot(x, z)
    h = 16.0 * _ss(0.0, 2200.0, -z)
    h += _noise2(x, z, 41) * 1.4 + _noise2(x * 3.0, z * 3.0, 42) * 0.4 + _noise2(x * 11, z * 11, 43) * 0.12
    h += (6.0 + 5.0 * _noise2(x * 0.5, z * 0.5, 44)) * _ss(300.0, 1400.0, d)
    h += (22.0 + 20.0 * _noise2(x * 0.18, z * 0.18, 45)) * _ss(2500.0, 6000.0, d)
    return h * _ss(16.0, 48.0, d)


class Irmak:
    def __init__(self, tanim, ova=None):
        ova = ova or ova_y
        self.ad = tanim["ad"]
        self.gen = tanim["gen"]
        self.P = _egri(tanim["noktalar"], 1.0)
        seg = np.linalg.norm(np.diff(self.P, axis=0), axis=1)
        self.s = np.concatenate([[0.0], np.cumsum(seg)])
        a = tanim["gen"] / 2
        self.a = a * (1.0 + 3.0 * np.exp(-self.s / 90.0))                 # çağlayan dibinde gölcük
        self.N = _dik(self.P)
        self.wl = np.minimum.accumulate(ova(self.P[:, 0], self.P[:, 1]) - 0.8)
        self.agac = cKDTree(self.P)

    def banka(self):
        return 1.3 * self.a + 5.0

    def uzaklik(self, X):
        """Noktaların yola uzaklığı ve en yakın örneğin indeksi (parça izdüşümüyle)."""
        d, i = self.agac.query(X)
        best = d.copy()
        for j0, j1 in ((i - 1, i), (i, i + 1)):
            j0 = np.clip(j0, 0, len(self.P) - 1)
            j1 = np.clip(j1, 0, len(self.P) - 1)
            A, B = self.P[j0], self.P[j1]
            AB = B - A
            L = (AB ** 2).sum(1) + 1e-12
            t = np.clip(((X - A) * AB).sum(1) / L, 0, 1)
            Q = A + AB * t[:, None]
            best = np.minimum(best, np.linalg.norm(X - Q, axis=1))
        return best, i


def _irmaklar():
    return [Irmak(t) for t in IRMAKLAR]


def arazi_y(x, z, irmaklar, W_don=False, ova=None, arsa=True):
    """Irmak yatakları oyulmuş ova yüksekliği (ve istenirse çimen ağırlığı).
    ova: yükseklik fonksiyonu (varsayılan ilk katın ovası; kesitteki öteki katlar kendininkini verir)."""
    X = np.stack([np.asarray(x, float).ravel(), np.asarray(z, float).ravel()], axis=1)
    h = (ova or ova_y)(X[:, 0], X[:, 1])
    W = np.ones(len(X))
    kiyi = np.zeros(len(X))
    for ir in irmaklar:
        d, i = ir.uzaklik(X)
        a = ir.a[i]
        B = ir.banka()[i]
        wl = ir.wl[i]
        yatak = wl - 1.6 * (1 - np.clip(d / a, 0, 1) ** 2)
        egim = wl + (h - wl) * _ss(0.0, 1.0, (d - a) / B)
        hedef = np.where(d < a, yatak, egim)
        h = np.where(d < a + B, np.minimum(h, hedef), h)
        W = np.minimum(W, _ss(a + 0.25 * B, a + 0.9 * B, d))
        kiyi = np.maximum(kiyi, 1 - _ss(a - 0.5, a + 0.5 * B, d))
    if not W_don:
        return h
    dx = np.hypot(X[:, 0], X[:, 1])
    th = np.arctan2(X[:, 0], X[:, 1])
    kenar = 1.1 * np.sin(th * 5 + 0.7) + 0.6 * np.sin(th * 11 + 2.0) + 0.5 * _noise2(X[:, 0] * 40, X[:, 1] * 40, 31)
    arsa = (1 - _ss(ARSA_R - 2.5, ARSA_R + 1.2, dx + kenar)) if arsa else np.zeros_like(W)
    W = np.minimum(W, 1 - arsa)
    return h, W, kiyi, arsa


# --------------------------------------------------------------------------
# ZB_dunya_cennet: ova ve ırmaklar
# --------------------------------------------------------------------------

def _ova_noktalari(irmaklar):
    rng = np.random.default_rng(3)
    pts = []
    # Arsa ve yakın çevre: sık, titreşimli ızgara
    x0, z0, x1, z1 = -95.0, -160.0, 95.0, 70.0
    s = 1.7
    gx, gz = np.meshgrid(np.arange(x0, x1, s), np.arange(z0, z1, s))
    pts.append(np.stack([gx.ravel(), gz.ravel()], 1) + rng.uniform(-0.35, 0.35, (gx.size, 2)) * s)
    # Uzaklaştıkça seyrelen halkalar (ufka kadar)
    r = 70.0
    while r < OVA_R:
        n = int(2 * math.pi / 0.024)
        a = np.arange(n) * 2 * math.pi / n + rng.uniform(0, 1) * 0.02
        P = np.stack([r * np.sin(a), r * np.cos(a)], 1)
        ic = (P[:, 0] > x0 - 2) & (P[:, 0] < x1 + 2) & (P[:, 1] > z0 - 2) & (P[:, 1] < z1 + 2)
        pts.append(P[~ic])
        r *= 1.03 if r > 2500 else 1.024
    # Irmak kıyı çizgileri
    for ir in irmaklar:
        d0 = np.hypot(ir.P[:, 0], ir.P[:, 1])
        adim = np.clip(0.01 * d0, 1.5, 20.0)
        j, idx = 0.0, []
        while j < len(ir.P) - 1:
            idx.append(int(j))
            j += adim[int(j)]
        idx = np.array(idx)
        a, B = ir.a[idx], ir.banka()[idx]
        for o in (-1.0, -0.5, 0.0, 0.5, 1.0):
            pts.append(ir.P[idx] + ir.N[idx] * (o * a)[:, None])
        for o in (0.5, 1.0):
            for sgn in (-1, 1):
                pts.append(ir.P[idx] + ir.N[idx] * (sgn * (a + o * B))[:, None])
    P = np.vstack(pts)
    _, tek = np.unique(np.round(P / 0.4), axis=0, return_index=True)
    return P[np.sort(tek)]


def _ova(irmaklar) -> Mesh:
    P = _ova_noktalari(irmaklar)
    tri = Delaunay(P).simplices
    uzun = np.max(np.linalg.norm(P[tri] - P[np.roll(tri, 1, axis=1)], axis=2), axis=1)
    tri = tri[uzun < 900]
    h, W, kiyi, arsa = arazi_y(P[:, 0], P[:, 1], irmaklar, W_don=True)
    V = np.stack([P[:, 0], h, P[:, 1]], 1).astype(np.float32)
    F = tri[:, [0, 2, 1]].astype(np.int64)
    n = np.cross(V[F][:, 1] - V[F][:, 0], V[F][:, 2] - V[F][:, 0])
    F[n[:, 1] < 0] = F[n[:, 1] < 0][:, ::-1]
    n = np.cross(V[F][:, 1] - V[F][:, 0], V[F][:, 2] - V[F][:, 0])
    dik = 1 - np.abs(n[:, 1]) / (np.linalg.norm(n, axis=1) + 1e-12)
    dik_v = np.zeros(len(V))
    np.maximum.at(dik_v, F.ravel(), np.repeat(dik, 3))
    W = np.minimum(W, 1 - _ss(0.4, 0.55, dik_v))
    # Köşe renkleri: çimen dışı yerlerde (W küçük) görünen kum, çakıl, taş, arsa çimeni
    t = _noise2(P[:, 0] * 9, P[:, 1] * 9, 7) * 0.5 + 0.5
    cv = np.tile(np.array(renk("cimen")), (len(V), 1))
    kum = np.where((t > 0.5)[:, None], renk("kum"), renk("cakil"))
    cv = cv + (kum - cv) * _ss(0.2, 0.45, kiyi)[:, None]
    cv = cv + (np.array(renk("toprak_koyu")) * 0.8 - cv) * _ss(0.8, 0.95, kiyi)[:, None]
    cv = cv + (np.array(renk("kaya_krem")) - cv) * _ss(0.4, 0.55, dik_v)[:, None]
    cv = cv + (np.array(renk("arsa_cimen")) - cv) * _ss(0.2, 0.5, arsa)[:, None]
    m = Mesh(V, F, cv[F].mean(1).astype(np.float32), "zemin", W=W.astype(np.float32))
    m.NV = _kose_normalleri(V, F)
    m.CV = cv.astype(np.float32)
    return m


def _su_seritleri(irmaklar):
    out = []
    for ir in irmaklar:
        d0 = np.hypot(ir.P[:, 0], ir.P[:, 1])
        adim = np.clip(0.008 * d0, 1.0, 12.0)
        j, idx = 0.0, []
        while j < len(ir.P) - 1:
            idx.append(int(j))
            j += adim[int(j)]
        idx.append(len(ir.P) - 1)
        idx = np.array(idx)
        L = ir.P[idx] + ir.N[idx] * (ir.a[idx] + 0.9)[:, None]
        R = ir.P[idx] - ir.N[idx] * (ir.a[idx] + 0.9)[:, None]
        y = ir.wl[idx]
        V = []
        for k in range(len(idx)):
            V += [[L[k, 0], y[k], L[k, 1]], [R[k, 0], y[k], R[k, 1]]]
        F = []
        for k in range(len(idx) - 1):
            a = 2 * k
            F += [[a, a + 1, a + 3], [a, a + 3, a + 2]]
        m = Mesh(np.array(V, np.float32), np.array(F, np.int64),
                 np.tile(np.array(renk(ir.ad), np.float32), (len(F), 1)), ir.ad)
        m = _yuz_yonu(m, (0, 1, 0))
        m.NV = np.tile(np.array([0, 1, 0], np.float32), (len(m.V), 1))
        # İndeksli (kesme düzleminde bölünebilsin); renk ve normal düz olduğu için görünüş aynı
        m.CV = np.tile(np.array(renk(ir.ad), np.float32), (len(m.V), 1))
        out.append(m)
    return out


@lru_cache(maxsize=1)
def ilk_kat_kesimi():
    """İlk katın arazisi ve ırmakları, kesme düzleminde (KESME_Z) ikiye bölünmüş hâlde:
    {"arazi": (arka, on), "irmaklar": [(arka, on), ...], "cizgi": arazinin kesme çizgisi}.
    İçeride iki parça birlikte görünür (yüzey aynı); kesitte öndekiler gizlenir."""
    irmaklar = _irmaklar()
    arka, on, cizgi = _kes(_ova(irmaklar), KESME_Z)
    ir = [_kes(m, KESME_Z)[:2] for m in _su_seritleri(irmaklar)]
    return {"arazi": (arka, on), "irmaklar": ir, "cizgi": cizgi}


@model("ZB_dunya_cennet")
def dunya_cennet() -> Node:
    k = ilk_kat_kesimi()
    root = Node("ZB_dunya_cennet")
    # "_on" düğümleri kesme düzleminin önündedir (z > KESME_Z): kesit ve yakınlaşmada gizlenir
    root.add(Node("arazi", [k["arazi"][0]]), Node("arazi_on", [k["arazi"][1]]),
             Node("irmaklar", [a for a, _ in k["irmaklar"]]),
             Node("irmaklar_on", [o for _, o in k["irmaklar"] if len(o.F)]))
    return root


# --------------------------------------------------------------------------
# ZB_dunya_selaleler: gökten, bulutların içinden inen dört çağlayan
# --------------------------------------------------------------------------

def _lin2srgb(x):
    """gltf_export.srgb_to_linear'ın tersi: shader köşe verisini yazıldığı gibi okusun."""
    x = np.clip(np.asarray(x, float), 0.0, 1.0)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def _gok_selalesi(x, z, y_alt, y_ust, gen, bakis, seed, nv=64, nu=16):
    """Gökten, bulutun içinden inen çağlayan (at kuyruğu biçimi). İki mesh döner:
      perde ("selale"): tepede dar, aşağı doğru genişleyen, hafif kıvrımlı su perdesi
      pus ("selale_pus"): perdenin arkasında daha geniş, ince serpinti zarfı
    bakis: perdenin yüzünün döndüğü yatay yön (oyuncuya).

    Köşe verisi shader içindir (selale.gdshader):
      COLOR.r  perdenin eni boyunca konum (0 sol kenar, 1 sağ kenar)
      COLOR.g  tepe genişliği / 200 m (akış çizgilerinin ölçeği)
      COLOR.b  çağlayana özgü rastgele sayı (desenler her çağlayanda farklı)
      COLOR.a  tepeden dibe 1 -> 0
    Dışa aktarım renkleri sRGB'den doğrusala çevirdiği için r, g, b ters çevrilerek yazılır."""
    rng = np.random.default_rng(seed)
    b = np.asarray(bakis, float)
    b /= np.linalg.norm(b)
    yan = np.array([-b[1], b[0]])
    faz = rng.uniform(0, 2 * math.pi)
    tohum = rng.uniform(0.05, 0.95)

    def perde(genislik, geri, malzeme):
        V, W, CV = [], [], []
        for j in range(nv + 1):
            v = j / nv                                          # 0 tepe, 1 dip
            y = y_ust + (y_alt - y_ust) * v
            g = genislik(v)
            kivrim = gen * 0.3 * math.sin(v * 3.0 + faz) * v    # rüzgârda salınan şerit gibi kıvrılır
            for i in range(nu + 1):
                u = i / nu * 2 - 1
                ic = (1 - u * u) * gen * 0.14 * (0.4 + v) - geri  # ortası öne kabarık, aşağıda daha çok
                px = x + yan[0] * (u * g / 2 + kivrim) + b[0] * ic
                pz = z + yan[1] * (u * g / 2 + kivrim) + b[1] * ic
                V.append([px, y, pz])
                W.append(1 - v)
                CV.append([i / nu, gen * 0.9 / 200.0, tohum])
        CV = _lin2srgb(np.asarray(CV))
        m = _izgara(V, nu, nv, CV, malzeme, W=W)
        return _yuz_yonu(m, (b[0], 0, b[1]))

    ana = perde(lambda v: gen * (0.9 + 0.7 * v ** 1.7), 0.0, "selale")
    pus = perde(lambda v: gen * (1.1 + 1.2 * v ** 1.5), gen * 0.18, "selale_pus")
    return ana, pus


@model("ZB_dunya_selaleler")
def dunya_selaleler() -> Node:
    irmaklar = _irmaklar()
    ana, pus = [], []
    for k, ir in enumerate(irmaklar):
        x, z = ir.P[0]
        a, p = _gok_selalesi(x, z, float(ir.wl[0]) - 1.5, SELALE_UST + 30 * k, ir.gen * 4.0, (-x, -z), 11 + k)
        ana.append(a)
        pus.append(p)
    root = Node("ZB_dunya_selaleler")
    root.add(merge(*pus), merge(*ana))
    return root


# --------------------------------------------------------------------------
# Yerleşim: bitkiler, yapılar, parçacık noktaları, kameralar, çimen ızgarası
# --------------------------------------------------------------------------

def _yerde(x, z, irmaklar):
    return float(arazi_y(np.array([x]), np.array([z]), irmaklar)[0])


def _irmak_yonu(ir, z):
    i = int(np.argmin(np.abs(ir.P[:, 1] - z) + 1e3 * (ir.s < 400)))
    j = min(i + 3, len(ir.P) - 1)
    d = ir.P[j] - ir.P[max(i - 3, 0)]
    return ir.P[i], float(ir.wl[i]), math.degrees(math.atan2(d[0], d[1]))


def merdiven_noktalari():
    """Merdivenin ayağı ve ucu (dünya koordinatı)."""
    x, z, rot, olcek = MERDIVEN
    a = math.radians(rot)
    ux, uy, uz = MERDIVEN_UST
    wx = x + (ux * math.cos(a) + uz * math.sin(a)) * olcek
    wz = z + (-ux * math.sin(a) + uz * math.cos(a)) * olcek
    return (x, z), (wx, uy * olcek, wz)


def yerlesim() -> dict:
    irmaklar = _irmaklar()
    su = irmaklar[0]
    rng = np.random.default_rng(2026)
    d: dict = {"arsa_r": ARSA_R}

    def yer(x, z, rot=None, olcek=1.0, dy=0.0):
        return [round(float(x), 2), round(_yerde(x, z, irmaklar) + dy, 2), round(float(z), 2),
                round(float(rng.uniform(0, 360)) if rot is None else float(rot), 1), round(float(olcek), 2)]

    def bos_mu(x, z, pay, yapilar=()):
        if math.hypot(x, z) < ARSA_R + pay:
            return False
        X = np.array([[x, z]])
        for ir in irmaklar:
            dd, i = ir.uzaklik(X)
            if dd[0] < ir.a[i[0]] + ir.banka()[i[0]] * 0.5 + pay:
                return False
        for (yx, yz, yr) in yapilar:
            if math.hypot(x - yx, z - yz) < yr + pay:
                return False
        return True

    # --- Yapılar
    kosk_p, kosk_y, kosk_rot = _irmak_yonu(su, -88.0)
    kosk2_p, kosk2_y, kosk2_rot = _irmak_yonu(su, -300.0)
    sut_p, sut_y, sut_rot = _irmak_yonu(irmaklar[1], -205.0)
    bal_p, bal_y, bal_rot = _irmak_yonu(irmaklar[2], -330.0)
    d["su_kosku"] = [[round(float(p[0]), 2), round(y, 2), round(float(p[1]), 2), round(r, 1), o]
                     for p, y, r, o in ((kosk_p, kosk_y, kosk_rot, 1.0), (kosk2_p, kosk2_y, kosk2_rot, 0.9),
                                        (sut_p, sut_y, sut_rot, 0.85), (bal_p, bal_y, bal_rot, 1.0))]
    cadir = (40.0, -62.0)
    d["inci_cadir"] = [yer(*cadir, rot=math.degrees(math.atan2(-cadir[0], -cadir[1])), dy=-0.2)]
    sedir = (-15.0, -24.0)
    d["sedir_kosesi"] = [yer(*sedir, rot=25.0, dy=0.02)]
    d["selsebil"] = [yer(-10.5, -30.5, rot=-20.0, dy=-0.05)]
    d["pinar"] = [yer(-21.5, -17.5, dy=-0.1)]
    (mx, mz), ust = merdiven_noktalari()
    d["merdiven"] = [yer(mx, mz, rot=MERDIVEN[2], olcek=MERDIVEN[3], dy=-0.3)]
    d["merdiven_ust"] = [round(v, 1) for v in ust]
    yapilar = [(kosk_p[0], kosk_p[1], 18), (kosk2_p[0], kosk2_p[1], 18), (sut_p[0], sut_p[1], 16),
               (bal_p[0], bal_p[1], 18), (cadir[0], cadir[1], 10), (sedir[0], sedir[1], 4), (-10.5, -30.5, 3),
               (-21.5, -17.5, 3), (mx, mz, 14)]

    # --- Arsa: Tûbâ çekirdeği, tek fidan, ilk çiçekler, nur tohumları
    d["arsa"] = {
        "tuba": [0.0, 0.0, 0.0, 0.0, 1.0],
        "fidan": [[-4.3, 0.0, -3.6, 40.0, 1.0, "ZB_agac_sidr_a3"], [5.6, 0.0, -4.2, 0.0, 1.3, "ZB_agac_hurma_a2"]],
        "cicek": [[3.2 + 0.5 * math.cos(a), 0.0, 2.6 + 0.5 * math.sin(a), float(a * 50), 1.0]
                  for a in (0.0, 1.3, 2.6, 3.9, 5.2)],
        "nur_tohumu": [[3.2, 0.15, 2.6], [5.6, 0.15, -4.2], [-4.3, 0.15, -3.6], [-2.4, 0.1, 6.2], [7.4, 0.1, 3.1],
                       [-7.8, 0.1, 2.4], [1.5, 0.1, -8.0]],
    }

    # --- Arsanın sınırı: inci ve yakut çakıllar (et-Tâc 5/402)
    cakil = []
    for a in np.arange(0, 2 * math.pi, 0.034):
        th = a + rng.uniform(-0.01, 0.01)
        kenar = 1.1 * math.sin(th * 5 + 0.7) + 0.6 * math.sin(th * 11 + 2.0)
        r = ARSA_R - 0.4 - kenar + rng.uniform(-0.12, 0.12)
        cakil.append(yer(r * math.sin(th), r * math.cos(th), olcek=rng.uniform(0.8, 1.2), dy=-0.02))
    d["inci_cakil"] = cakil

    # --- Yakın bitkiler
    d["sidr"] = [yer(-19.5, -29.0, olcek=1.35), yer(24.0, -30.0, olcek=1.2), yer(-8.0, -46.0, olcek=1.3)]
    d["uzum"] = [yer(13.5, -13.5, rot=18.0, olcek=1.0)]
    hurma = []
    for x, z in ((28, -48), (52, -52), (33, -78), (56, -80), (47, -40), (22, -66), (62, -66)):
        hurma.append(yer(x + rng.uniform(-2, 2), z + rng.uniform(-2, 2), olcek=rng.uniform(1.9, 2.5)))
    d["hurma"] = hurma
    talh = []
    for x, z in ((-20.5, 14), (-19.5, 3), (-22.5, -9), (-40, -58), (-66, -100), (-26, 52), (60, 5), (64, -18)):
        if bos_mu(x, z, -3.0, yapilar):
            talh.append(yer(x, z, olcek=rng.uniform(1.2, 1.5)))
    d["talh"] = talh
    nar = []
    for x, z in ((18, 8), (22, -6), (-2, -24), (8, -30), (-28, 24), (30, 22), (12, -44), (-30, -44), (40, -20),
                 (-44, 8), (28, 40), (-12, 30)):
        if bos_mu(x, z, 0.5, yapilar):
            nar.append(yer(x, z, olcek=rng.uniform(1.15, 1.45)))
    d["nar"] = nar
    selvi = []
    for x, z in ((-28, -96), (-74, -80), (-26, -70), (-76, -112), (-35, -128), (-80, -60), (-70, -140)):
        if bos_mu(x, z, 1.0, yapilar):
            selvi.append(yer(x, z, olcek=rng.uniform(1.3, 1.7)))
    d["selvi"] = selvi
    gul = []
    for k in range(9):
        a = 2 * math.pi * k / 9
        x, z = sedir[0] + 4.0 * math.cos(a), sedir[1] + 3.4 * math.sin(a)
        if abs(math.sin(a)) > 0.45 and bos_mu(x, z, -20.0):
            gul.append(yer(x, z, olcek=rng.uniform(1.0, 1.3)))
    for k in range(14):                              # arsanın kenarında, kameraya bakan yüz açık
        a = 2 * math.pi * k / 14
        x, z = (ARSA_R + 2.4) * math.sin(a), (ARSA_R + 2.4) * math.cos(a)
        if abs(a - math.pi) > 0.5 and z < 4.0 and bos_mu(x, z, -2.4):
            gul.append(yer(x, z, olcek=rng.uniform(0.9, 1.2)))
    # Merdivenin ayağında çiçekli çalılar
    for k in range(10):
        a = 2 * math.pi * k / 10
        x, z = mx + 9.0 * math.cos(a), mz + 7.0 * math.sin(a)
        if bos_mu(x, z, 0.0):
            gul.append(yer(x, z, olcek=rng.uniform(1.2, 1.6)))
    d["gul"] = gul
    lale = []
    for cx, cz, n in ((16.0, 18.0, 70), (-10.0, 22.0, 60), (20.0, -18.0, 50), (-6.0, -34.0, 45), (8.0, 30.0, 60),
                      (mx - 16, mz + 14, 60), (mx + 18, mz + 8, 50)):
        for _ in range(n):
            r = 3.2 * math.sqrt(rng.uniform(0, 1))
            a = rng.uniform(0, 2 * math.pi)
            x, z = cx + r * math.cos(a), cz + r * math.sin(a) * 0.7
            if bos_mu(x, z, 0.0, yapilar):
                lale.append(yer(x, z, olcek=rng.uniform(0.85, 1.2), dy=-0.02))
    d["lale"] = lale

    # --- Korular (koyu yeşil, Rahmân 64) ve uzak ağaçlar
    koru, uzak = [], []
    kumeler = [(-110, -60, 40, 26), (-140, -150, 50, 32), (-95, -230, 45, 26), (130, -70, 40, 22), (170, -190, 50, 26),
               (60, -290, 45, 22), (-20, -300, 60, 28), (-60, 40, 30, 10), (95, 60, 35, 14), (-150, 20, 40, 18),
               (160, -20, 40, 18), (-190, -90, 45, 22), (220, -110, 45, 22)]
    for cx, cz, r, n in kumeler:
        for _ in range(n * 3):
            if n <= 0:
                break
            a = rng.uniform(0, 2 * math.pi)
            q = r * math.sqrt(rng.uniform(0, 1))
            x, z = cx + q * math.cos(a), cz + q * math.sin(a)
            if bos_mu(x, z, 4.0, yapilar):
                koru.append(yer(x, z, olcek=rng.uniform(1.3, 2.1), dy=-0.1))
                n -= 1
    d["koru"] = koru
    while len(uzak) < 3400:
        a = rng.uniform(-math.pi, math.pi)
        r = 260 * math.exp(rng.uniform(0, math.log(14.0)))
        x, z = r * math.sin(a), -r * math.cos(a)
        if z > 700:
            continue
        if _noise2(np.array([x * 6.0]), np.array([z * 6.0]), 170)[0] < 0.1:
            continue
        if bos_mu(x, z, 6.0, yapilar):
            uzak.append(yer(x, z, olcek=rng.uniform(1.9, 3.2), dy=-0.3))
    d["uzak_agac"] = uzak

    # --- Gökten inen çağlayanlar: tepe bulutu ve dip sisi
    d["gok_selale"] = [[round(float(ir.P[0][0]), 1), SELALE_UST + 30 * k, round(float(ir.P[0][1]), 1), ir.gen * 4.0]
                       for k, ir in enumerate(irmaklar)]
    d["selale_dip"] = [[round(float(ir.P[0][0]), 1), round(float(ir.wl[0]), 1), round(float(ir.P[0][1]), 1),
                        ir.gen * 4.0] for ir in irmaklar]


    # --- Çimen ızgarası (Godot çimen tutamlarını buna göre dağıtır)
    x0, z0, x1, z1 = YAKIN
    xs = np.arange(x0, x1 + 0.5, 1.0)
    zs = np.arange(z0, z1 + 0.5, 1.0)
    X, Z = np.meshgrid(xs, zs)
    h, W, _, _ = arazi_y(X.ravel(), Z.ravel(), irmaklar, W_don=True)
    for (yx, yz, yr) in yapilar:
        W = np.where(np.hypot(X.ravel() - yx, Z.ravel() - yz) < yr * 0.8, 0.0, W)
    d["izgara"] = {"x0": x0, "z0": z0, "adim": 1.0, "nx": len(xs), "nz": len(zs),
                   "y_cm": [int(round(v * 100)) for v in h], "cimen": [int(round(v * 9)) for v in W]}

    # --- Kameralar: konum, hedef, dikey görüş açısı
    d["kameralar"] = {
        "ufuk": {"konum": [12.0, _yerde(12, 38, irmaklar) + 17.0, 38.0], "hedef": [-10.0, 60.0, -700.0], "fov": 55.0},
        "arsa": {"konum": [9.0, 5.8, 21.0], "hedef": [-2.0, 4.0, -40.0], "fov": 55.0},
        # Kesit (K18): 8 kat dikey kadraja sığar; önden, 4,6° yukarıdan, tele (şimdiki kompozisyon)
        "kesit": KESIT_KAMERA,
        # Geliştirme: gökten inen su çağlayanına 360 m'den yakın bakış (kalite incelemesi)
        "selale": {"konum": [-250.0, _yerde(-250, -900, irmaklar) + 60.0, -900.0], "hedef": [-330.0, 170.0, -1250.0],
                   "fov": 55.0},
    }
    return d


def yerlesim_yaz(root: Path) -> Path:
    p = root / "game" / "data" / "dunya_cennet.json"
    p.write_text(json.dumps(yerlesim(), ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return p
