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
  ZB_dunya_kesit      8 tabakanın dıştan kesit görünümü
Yerleşim game/data/dunya_cennet.json dosyasına yazılır.
"""
from __future__ import annotations

import json
import math
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
    def __init__(self, tanim):
        self.ad = tanim["ad"]
        self.gen = tanim["gen"]
        self.P = _egri(tanim["noktalar"], 1.0)
        seg = np.linalg.norm(np.diff(self.P, axis=0), axis=1)
        self.s = np.concatenate([[0.0], np.cumsum(seg)])
        a = tanim["gen"] / 2
        self.a = a * (1.0 + 3.0 * np.exp(-self.s / 90.0))                 # çağlayan dibinde gölcük
        self.N = _dik(self.P)
        self.wl = np.minimum.accumulate(ova_y(self.P[:, 0], self.P[:, 1]) - 0.8)
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


def arazi_y(x, z, irmaklar, W_don=False):
    """Irmak yatakları oyulmuş ova yüksekliği (ve istenirse çimen ağırlığı)."""
    X = np.stack([np.asarray(x, float).ravel(), np.asarray(z, float).ravel()], axis=1)
    h = ova_y(X[:, 0], X[:, 1])
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
    arsa = 1 - _ss(ARSA_R - 2.5, ARSA_R + 1.2, dx + kenar)
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
        out.append(m)
    return out


@model("ZB_dunya_cennet")
def dunya_cennet() -> Node:
    irmaklar = _irmaklar()
    root = Node("ZB_dunya_cennet")
    root.add(Node("arazi", [_ova(irmaklar)]), Node("irmaklar", _su_seritleri(irmaklar)))
    return root


# --------------------------------------------------------------------------
# ZB_dunya_selaleler: gökten, bulutların içinden inen dört çağlayan
# --------------------------------------------------------------------------

def _lin2srgb(x):
    """gltf_export.srgb_to_linear'ın tersi: shader köşe verisini yazıldığı gibi okusun."""
    x = np.clip(np.asarray(x, float), 0.0, 1.0)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def _gok_selalesi(x, z, y_alt, y_ust, gen, bakis, seed):
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
    nv, nu = 64, 16

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
# ZB_dunya_kesit: 8 tabakanın dıştan görünümü (Dünya'nın katman resimleri gibi)
# --------------------------------------------------------------------------

KAT = 8
KAT_H = 300.0                # bir tabakanın toplam yüksekliği (zemin dilimi + gök)
KAT_T = 60.0                 # zemin diliminin kalınlığı
KESIT_X = 6000.0             # kesitin yarı genişliği (kadrajın dışına taşar: uzanıp gider)
KESIT_Z = 1300.0             # tabakaların derinliği (arka gök perdesine kadar)
KESIT_SELALE_X = [-1900.0, -650.0, 650.0, 1900.0]
KESIT_IRMAK = ["su", "sut", "bal", "serbet"]


def kesit_zemin_y(k, x, z):
    x = np.asarray(x, float)
    z = np.asarray(z, float)
    return k * KAT_H + KAT_T + 9.0 * _noise2(x * 0.8 + k * 97, z * 0.8, 200 + k) + 3.0 * _noise2(x * 4, z * 4, 210 + k)


def kesit_selale(k, j):
    """k. tabakanın göğünden inen j. çağlayanın ayağı (x, z)."""
    x = KESIT_SELALE_X[j] + 260.0 * math.sin(k * 1.7 + j)
    z = -380.0 - 260.0 * ((k + j) % 3)
    return x, z


def _kesit_zemin(k):
    """Tabakanın zemini: çayır, üst tabakalarda çiçek tarlaları artar (Rahmân 46-61)."""
    xs = np.linspace(-KESIT_X, KESIT_X, 181)
    zs = np.linspace(-KESIT_Z, 0.0, 27)
    X, Z = np.meshgrid(xs, zs)
    Y = kesit_zemin_y(k, X, Z)
    V = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
    cicek = _ss(0.3, 0.65, _noise2(X.ravel() * 3, Z.ravel() * 3, 220 + k) * 0.5 + 0.5) * min(1.0, 0.15 + 0.12 * k)
    tarla = np.array([renk(c) for c in ("gul", "lale_sari", "inci", "lale", "kaya_pembe")])
    secim = (np.floor((X.ravel() + 5000) / 260) + np.floor((Z.ravel() + 5000) / 190) + k).astype(int) % len(tarla)
    CV = tarla[secim]
    m = _izgara(V, len(xs) - 1, len(zs) - 1, CV, "zemin", W=1 - cicek)
    return _yuz_yonu(m, (0, 1, 0))


def _kesit_dilim(k):
    """Zemin diliminin kesit yüzü (z=0) ve altı (alttaki tabakanın göğü gibi boyanır)."""
    y0 = k * KAT_H
    xs = np.linspace(-KESIT_X, KESIT_X, 241)
    ust = kesit_zemin_y(k, xs, np.zeros_like(xs))
    # Kesit yüzü: toprak katmanları (çimen, koyu toprak, altın damar, inci damar, taban)
    seritler = [(1.0, "cimen"), (0.92, "katman_toprak"), (0.66, "katman_toprak"), (0.6, "katman_altin"),
                (0.5, "katman_toprak"), (0.3, "katman_koyu"), (0.22, "katman_inci"), (0.12, "katman_koyu"),
                (0.0, "katman_koyu")]
    V, CV = [], []
    for t, ad in seritler:
        dalga = 1.5 * np.sin(xs * 0.01 + k * 3 + t * 9)
        y = y0 + 4 + (ust - y0 - 4) * t + (dalga if 0 < t < 1 else 0)
        V += list(np.stack([xs, y, np.zeros_like(xs)], 1))
        CV += [renk(ad)] * len(xs)
    yuz = _izgara(V, len(xs) - 1, len(seritler) - 1, CV, "tas")
    yuz = _yuz_yonu(yuz, (0, 0, 1))
    # Alt yüz: alttaki tabakanın gözünden gök (bulut tavanı); tavan malzemesi ışıklıdır
    zs = np.linspace(-KESIT_Z, 0.0, 8)
    X, Z = np.meshgrid(xs[::4], zs)
    Vt = np.stack([X.ravel(), np.full(X.size, y0 + 4.0), Z.ravel()], 1)
    n = _noise2(X.ravel() * 2, Z.ravel() * 2, 230 + k) * 0.5 + 0.5
    CVt = np.array(renk("gok_tavan")) * (1 - 0.35 * n[:, None]) + np.array(renk("bulut_beyaz")) * 0.35 * n[:, None]
    tavan = _izgara(Vt, X.shape[1] - 1, len(zs) - 1, CVt, "tavan")
    tavan = _yuz_yonu(tavan, (0, -1, 0))
    return yuz, tavan


def _kesit_arka(k):
    """Tabakanın arka gök perdesi: ufukta sıcak, yukarıda mavi (her tabakanın kendi göğü)."""
    y0 = k * KAT_H + KAT_T - 30
    y1 = (k + 1) * KAT_H + 4
    xs = np.linspace(-KESIT_X - 200, KESIT_X + 200, 40)
    V, CV = [], []
    ufuk, orta, tepe = (np.array(renk(c)) for c in ("gok_ufuk", "gok_orta", "gok_tavan"))
    for t in np.linspace(0, 1, 9):
        c = ufuk + (orta - ufuk) * _ss(0.0, 0.45, t) + (tepe - orta) * _ss(0.45, 1.0, t)
        V += list(np.stack([xs, np.full_like(xs, y0 + (y1 - y0) * t), np.full_like(xs, -KESIT_Z)], 1))
        CV += [c] * len(xs)
    m = _izgara(V, len(xs) - 1, 8, CV, "tavan")
    return _yuz_yonu(m, (0, 0, 1))


def _kesit_irmaklari(k):
    """Her tabakada dört ırmak: gökten inen çağlayanın dibinden kesit yüzüne kıvrılarak akar.
    En üstte (Firdevs) dört ırmak ortadaki kaynaktan dört yöne çıkar."""
    out = {ad: [] for ad in KESIT_IRMAK}
    for j, ad in enumerate(KESIT_IRMAK):
        if k == KAT - 1:
            x0, z0 = 0.0, -650.0
            yon = [(-1, 0.25), (-0.3, 1), (0.3, 1), (1, 0.25)][j]
            pts = [(x0 + yon[0] * t * 2200 + 90 * math.sin(t * 9 + j), z0 + yon[1] * t * 650) for t in
                   np.linspace(0.02, 1, 30)]
        else:
            x0, z0 = kesit_selale(k, j)
            pts = [(x0 + 140 * math.sin(t * 6.5 + j + k), z0 + (0 - z0) * t) for t in np.linspace(0, 1, 30)]
        P = _egri(pts, 30.0)
        N = _dik(P)
        gen = 34.0
        V = []
        for p, nrm in zip(P, N):
            y = float(kesit_zemin_y(k, p[0], p[1])) + 4.0
            V += [[p[0] + nrm[0] * gen / 2, y, p[1] + nrm[1] * gen / 2], [p[0] - nrm[0] * gen / 2, y, p[1] - nrm[1] * gen / 2]]
        F = []
        for i in range(len(P) - 1):
            a = 2 * i
            F += [[a, a + 1, a + 3], [a, a + 3, a + 2]]
        m = Mesh(np.array(V, np.float32), np.array(F, np.int64), np.tile(np.array(renk(ad), np.float32), (len(F), 1)), ad)
        m = _yuz_yonu(m, (0, 1, 0))
        m.NV = np.tile(np.array([0, 1, 0], np.float32), (len(m.V), 1))
        out[ad].append(m)
    return out


def _kesit_selaleleri():
    ana, pus = [], []
    for k in range(KAT - 1):
        for j in range(4):
            x, z = kesit_selale(k, j)
            y_alt = float(kesit_zemin_y(k, x, z)) + 2.0
            y_ust = (k + 1) * KAT_H + 2.0
            a, p = _gok_selalesi(x, z, y_alt, y_ust, 75.0, (0.25, 1.0), 40 + k * 4 + j)
            ana.append(a)
            pus.append(p)
    return [merge(*pus), merge(*ana)]


def _kesit_merdivenleri():
    """Kesitte her tabakadan bir üsttekine çıkan, uzaktan seçilebilecek genişlikte
    çiçekli merdiven (içerideki ZB_yapi_kat_merdiveni'nin kesit ölçeğindeki karşılığı)."""
    rng = np.random.default_rng(270)
    tas, yesil, cicek = [], [], []
    for k in range(KAT - 1):
        x0 = [-2300.0, 1900.0, -900.0, 1300.0, -1900.0, 600.0, 2400.0][k]
        z0 = -350.0
        y0 = float(kesit_zemin_y(k, x0, z0)) - 2.0
        y1 = (k + 1) * KAT_H + 6.0
        n = 26
        for i in range(n):
            t = i / (n - 1)
            x = x0 + 170.0 * math.sin(2 * math.pi * 0.85 * t + k)
            z = z0 - 260.0 * t
            y = y0 + (y1 - y0) * t
            tas.append(box(46.0, 5.0, 22.0, "mermer" if i % 2 else "fildisi", y0=-5.0).translate(x, y, z))
            for sgn in (-1, 1):
                c = np.array([x + sgn * 25.0, y + 2.0, z])
                yesil.append(icosphere(rng.uniform(7.0, 10.0), 1, ["yaprak_cennet", "yaprak", "yaprak_zumrut"][i % 3])
                             .jitter(2.0, i + k * 50).translate(*c))
                for _ in range(2):
                    v = rng.normal(0, 1, 3)
                    v[1] = abs(v[1])
                    v /= np.linalg.norm(v)
                    cicek.append(icosphere(rng.uniform(2.5, 3.8), 0,
                                           ["gul", "lale", "lale_sari", "cicek_mor", "inci"][rng.integers(5)])
                                 .translate(*(c + v * 8.0)))
    return (merge(*tas).with_material("tas"), merge(*yesil).with_material("yaprak").paylasimli(),
            merge(*cicek).with_material("cicek").paylasimli())


def _kesit_koskleri():
    """Tabakalarda uzaktan parıldayan inci kubbeler (köşkler)."""
    rng = np.random.default_rng(260)
    out = []
    for k in range(KAT):
        for _ in range(14 + 2 * k):
            x = rng.uniform(-KESIT_X * 0.9, KESIT_X * 0.9)
            z = rng.uniform(-KESIT_Z * 0.9, -150)
            y = float(kesit_zemin_y(k, x, z))
            b = rng.uniform(9.0, 16.0)
            out.append(lathe([(b, 0), (b * 0.97, b * 0.4), (b * 0.75, b * 0.85), (b * 0.35, b * 1.15), (0, b * 1.25)],
                             10, "inci").translate(x, y - 0.5, z))
    return merge(*out).smooth(60)


@model("ZB_dunya_kesit")
def dunya_kesit() -> Node:
    root = Node("ZB_dunya_kesit")
    zemin, yuz, tavan, arka = [], [], [], []
    irmak = {ad: [] for ad in KESIT_IRMAK}
    for k in range(KAT):
        zemin.append(_kesit_zemin(k))
        y, t = _kesit_dilim(k)
        yuz.append(y)
        if k > 0:
            tavan.append(t)
        arka.append(_kesit_arka(k))
        for ad, ms in _kesit_irmaklari(k).items():
            irmak[ad] += ms
    # Firdevs'in ortasında dört ırmağın kaynağı
    kaynak = lathe([(60, 0), (52, 6), (20, 10), (0, 12)], 24, "nur_beyaz").translate(0, float(kesit_zemin_y(KAT - 1, 0, -650)) + 2, -650)
    root.add(Node("zeminler", [merge(*zemin)]), Node("kesit_yuzu", [merge(*yuz)]), Node("tavanlar", [merge(*tavan)]),
             Node("gokler", [merge(*arka)]), Node("irmaklar", [merge(*v) for v in irmak.values()]),
             Node("selaleler", _kesit_selaleleri()), Node("koskler", [_kesit_koskleri()]),
             Node("merdivenler", list(_kesit_merdivenleri())),
             Node("kaynak", [kaynak.with_material("nur")]))
    root.add(Node("isik_firdevs", translation=(0.0, KAT * KAT_H + 80.0, -650.0)))
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

    # --- Kesit: tabakalardaki ağaçlar, merdivenler, çağlayan bulutları
    kesit_agac, kesit_merdiven, kesit_bulut = [], [], []
    for k in range(KAT):
        adet = 520
        while adet > 0:
            x = rng.uniform(-4500.0, 4500.0)
            z = rng.uniform(-KESIT_Z * 0.97, -40)
            if _noise2(np.array([x * 1.2 + k * 50]), np.array([z * 1.2]), 240 + k)[0] < -0.05:
                continue
            y = float(kesit_zemin_y(k, x, z))
            kesit_agac.append([round(x, 1), round(y - 1, 1), round(z, 1), round(float(rng.uniform(0, 360)), 0),
                               round(float(rng.uniform(5.0, 8.0)), 2)])
            adet -= 1
        if k < KAT - 1:
            x = [-2300.0, 1900.0, -900.0, 1300.0, -1900.0, 600.0, 2400.0][k]
            xu = x + 170.0 * math.sin(2 * math.pi * 0.85 + k)
            kesit_bulut.append([round(xu, 1), (k + 1) * KAT_H - 20.0, -610.0, 150.0])
            for j in range(4):
                sx, sz = kesit_selale(k, j)
                kesit_bulut.append([round(sx, 1), (k + 1) * KAT_H - 30.0, round(sz, 1), 140.0])
    d["kesit"] = {"kat": KAT, "kat_h": KAT_H, "agac": kesit_agac, "merdiven": kesit_merdiven, "bulut": kesit_bulut}

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
        "kesit": {"konum": [0.0, 2600.0, 16500.0], "hedef": [0.0, 1230.0, -700.0], "fov": 10.5},
        # Geliştirme: gökten inen su çağlayanına 360 m'den yakın bakış (kalite incelemesi)
        "selale": {"konum": [-250.0, _yerde(-250, -900, irmaklar) + 60.0, -900.0], "hedef": [-330.0, 170.0, -1250.0],
                   "fov": 55.0},
    }
    return d


def yerlesim_yaz(root: Path) -> Path:
    p = root / "game" / "data" / "dunya_cennet.json"
    p.write_text(json.dumps(yerlesim(), ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return p
