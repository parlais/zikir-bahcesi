"""Cennet mekânı (Faz 2a): ilk katın içi ve katlı koni-dağın dış görünümü.

Kurgu (docs/mekan-kurgusu.md):
  - Cennet, iç içe halkalardan oluşan, zirvesi nura açılan koni biçimli bir dağdır
    (Risale-i Nur, 28. Söz). Oyuncu en dış halkada, ilk kattadır.
  - Katın içinde tepede hiçbir şey yoktur. İçeriden bakınca üst dereceler ufukta,
    ışıklı pusa karışan kat kat yamaçlar olarak görünür (Buhârî, Cihad 4).
  - Dört ırmak (Muhammed 15) üst derecelerden çağlayan olarak iner, ovada kıvrılır.
  - Oyuncu arsası verimli ama boş bir topraktır (Tirmizî 3462).

Koordinatlar: metre, Y yukarı. Oyuncu arsası (0, 0, 0); koni-dağın merkezi
MERKEZ (xz), arsanın kuzeyinde (-z). Kutupsal açı phi, merkezden arsaya bakan
yönde (+z) sıfırdır.

Modeller:
  ZB_dunya_cennet       ilk katın ovası ve dört ırmak
  ZB_dunya_dereceler    ufuktaki derece duvarları, sekiler ve çağlayanlar
  ZB_dunya_derece_koni  katlı koni-dağın dıştan görünümü (açılış çekimi)
Yerleşim game/data/dunya_cennet.json dosyasına yazılır.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.spatial import Delaunay, cKDTree

from mf.mesh import Mesh, icosphere, lathe, merge
from mf.palette import renk
from mf.scene import Node

from . import model
from .sahne import _noise2

MERKEZ = np.array([0.0, -2600.0])
# Derece duvarları: (taban yarıçapı, üst kenar yüksekliği). İlki oyuncunun katını sınırlar.
DUVARLAR = [(1900.0, 120.0), (1450.0, 280.0), (1080.0, 420.0), (760.0, 560.0)]
DUVAR_ACI = 100.0            # duvarların uzandığı açı (±derece)
ARSA_R = 13.0                # oyuncu arsasının yarıçapı
YAKIN = (-70.0, -100.0, 70.0, 45.0)   # çimen ızgarası (x0, z0, x1, z1), 1 m adım

# Dört ırmak: çağlayanın indiği açı (derece), genişlik, kontrol noktaları (x, z)
IRMAKLAR = [
    dict(ad="su", phi=-6.0, gen=16.0, noktalar=[(-160, -560), (-75, -450), (-120, -320), (-55, -215), (-62, -140),
                                                   (-50, -85), (-36, -40), (-31, 0), (-38, 40), (-70, 130), (-55, 260),
                                                   (-80, 420)]),
    dict(ad="sut", phi=4.0, gen=12.0, noktalar=[(175, -560), (110, -440), (165, -320), (95, -200), (125, -110),
                                                   (82, -30), (74, 40), (100, 140), (85, 300), (110, 420)]),
    dict(ad="bal", phi=-16.0, gen=11.0, noktalar=[(-450, -620), (-395, -470), (-300, -340), (-265, -190),
                                                     (-205, -60), (-215, 60), (-260, 200), (-230, 420)]),
    dict(ad="serbet", phi=15.0, gen=11.0, noktalar=[(430, -610), (390, -450), (300, -320), (255, -170),
                                                       (225, -40), (250, 90), (285, 220), (270, 420)]),
]


# --------------------------------------------------------------------------
# Yardımcılar
# --------------------------------------------------------------------------

def _ss(a, b, x):
    t = np.clip((np.asarray(x, float) - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def kutup(x, z):
    dx, dz = np.asarray(x, float) - MERKEZ[0], np.asarray(z, float) - MERKEZ[1]
    return np.hypot(dx, dz), np.arctan2(dx, dz)


def kartezyen(rho, phi):
    return MERKEZ[0] + rho * np.sin(phi), MERKEZ[1] + rho * np.cos(phi)


def duvar_r(k, phi):
    """k. derece duvarının yarıçapı: öne çıkan burunlar ve içeri giren koylar."""
    R = DUVARLAR[k][0]
    phi = np.asarray(phi, float)
    return (R + (60 - 8 * k) * np.sin(4.7 * phi + 0.5 + k) + (22 + 8 * k) * np.sin(3.1 * phi + k)
            + (11 + 4 * k) * np.sin(7.3 * phi + 2.0 * k) + 5 * np.sin(17.0 * phi + 0.7 * k))


def duvar_ust(k, phi):
    """k. duvarın üst kenarının yüksekliği: dalgalı sırt; yanlara doğru alçalır,
    ufuk açılır (ortada yükselen geniş bir dağ gibi)."""
    phi = np.asarray(phi, float)
    alt = duvar_ust(k - 1, phi) if k > 0 else np.zeros_like(phi)
    fark = DUVARLAR[k][1] - (DUVARLAR[k - 1][1] if k > 0 else 0.0)
    n = 0.16 * np.sin(4.3 * phi + 1.3 * k) + 0.08 * np.sin(11.7 * phi + k) + 0.04 * np.sin(23.0 * phi + 2 * k)
    yan = 1.0 - 0.6 * _ss(0.3, 1.25, np.abs(phi))
    return alt + fark * (1.0 + n) * yan


def duvar_etek(v):
    """Duvar kesiti: ormanlı geniş etek, dik ve kaburgalı yüz, yuvarlak yeşil sırt."""
    return 90.0 * (1 - v) ** 2.2


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


def _izgara_mesh(V, nu, nv, renkler, material, W=None) -> Mesh:
    """(nv+1) x (nu+1) köşeli ızgara; renkler (nv, nu) yüz çifti başına."""
    F, C = [], []
    for j in range(nv):
        for i in range(nu):
            a = j * (nu + 1) + i
            b, c, d = a + 1, a + nu + 2, a + nu + 1
            F += [[a, c, b], [a, d, c]]
            C += [renkler[j][i], renkler[j][i]]
    F = np.asarray(F, np.int64)
    V = np.asarray(V, np.float32)
    C = np.asarray(C, np.float32)
    m = Mesh(V, F, C, material, W=None if W is None else np.asarray(W, np.float32))
    m.NV = _kose_normalleri(V, F)
    m.CV = _kose_renkleri(V, F, C)
    return m


def _kose_renkleri(V, F, C):
    """Yüz renklerinin köşelerde ortalaması (indeksli, yumuşak geçişli dışa aktarım için)."""
    CV = np.zeros((len(V), 3))
    n = np.zeros(len(V))
    for k in range(3):
        np.add.at(CV, F[:, k], C)
        np.add.at(n, F[:, k], 1.0)
    return (CV / np.maximum(n, 1)[:, None]).astype(np.float32)


def _yon_duzelt(m: Mesh, yukari=True) -> Mesh:
    """Izgaranın yüzleri istenen tarafa (yukarı ya da merkezden dışa) baksın."""
    tri = m.V[m.F]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    if (n[:, 1].sum() < 0) == yukari:
        m = m.flipped()
        m.NV = -m.NV
    return m


# --------------------------------------------------------------------------
# Ova yüksekliği ve ırmaklar
# --------------------------------------------------------------------------

def ova_y(x, z):
    x = np.asarray(x, float)
    z = np.asarray(z, float)
    rho, phi = kutup(x, z)
    d = np.hypot(x, z)
    h = 12.0 * np.clip((2600.0 - rho) / 700.0, 0, 1) ** 1.5              # dereceye doğru hafif yükselen ova
    h += _noise2(x, z, 41) * 1.4 + _noise2(x * 3.0, z * 3.0, 42) * 0.4 + _noise2(x * 11, z * 11, 43) * 0.12
    yan = _ss(380.0, 1500.0, np.abs(x)) * (1 - _ss(-900, -1500, z))
    arka = _ss(450.0, 1100.0, z)
    h += (38.0 + 22.0 * _noise2(x * 0.6, z * 0.6, 44)) * np.maximum(yan, arka)
    h += 14.0 * _ss(duvar_r(0, phi) + 260.0, duvar_r(0, phi) + 90.0, rho)   # duvar eteğinde yamaç
    duz = _ss(16.0, 48.0, d)                                               # arsa düzlüğü
    return h * duz


class Irmak:
    def __init__(self, tanim):
        self.ad = tanim["ad"]
        phi = math.radians(tanim["phi"])
        r0 = float(duvar_r(0, phi))
        bas = kartezyen(r0 + 110.0, phi)
        self.selale_phi = phi
        self.P = _egri([bas] + tanim["noktalar"], 1.0)
        seg = np.linalg.norm(np.diff(self.P, axis=0), axis=1)
        self.s = np.concatenate([[0.0], np.cumsum(seg)])
        a = tanim["gen"] / 2
        self.a = a * (1.0 + 1.3 * np.exp(-self.s / 45.0))                 # çağlayan dibinde gölcük
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
    yakin = np.stack([gx.ravel(), gz.ravel()], 1) + rng.uniform(-0.35, 0.35, (gx.size, 2)) * s
    pts.append(yakin)
    # Uzaklaştıkça seyrelen halkalar
    r = 70.0
    while r < 3700:
        n = int(2 * math.pi / 0.024)
        a = np.arange(n) * 2 * math.pi / n + rng.uniform(0, 1) * 0.02
        P = np.stack([r * np.sin(a), r * np.cos(a)], 1)
        ic = (P[:, 0] > x0 - 2) & (P[:, 0] < x1 + 2) & (P[:, 1] > z0 - 2) & (P[:, 1] < z1 + 2)
        pts.append(P[~ic])
        r *= 1.024
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
    # Duvar dibi
    phi = np.radians(np.arange(-DUVAR_ACI - 5, DUVAR_ACI + 5, 0.25))
    for dr in (0.0, 12.0, 35.0, 80.0):
        x, z = kartezyen(duvar_r(0, phi) + dr, phi)
        pts.append(np.stack([x, z], 1))
    P = np.vstack(pts)
    rho, phi = kutup(P[:, 0], P[:, 1])
    P = P[rho >= duvar_r(0, phi) - 0.5]
    # Çok yakın noktaları ayıkla (ince üçgen olmasın)
    _, tek = np.unique(np.round(P / 0.4), axis=0, return_index=True)
    return P[np.sort(tek)]


def _ova(irmaklar) -> Mesh:
    P = _ova_noktalari(irmaklar)
    tri = Delaunay(P).simplices
    c = P[tri].mean(axis=1)
    rho, phi = kutup(c[:, 0], c[:, 1])
    uzun = np.max(np.linalg.norm(P[tri] - P[np.roll(tri, 1, axis=1)], axis=2), axis=1)
    tri = tri[(rho > duvar_r(0, phi) - 1.0) & (uzun < 400)]
    h, W, kiyi, arsa = arazi_y(P[:, 0], P[:, 1], irmaklar, W_don=True)
    V = np.stack([P[:, 0], h, P[:, 1]], 1).astype(np.float32)
    F = tri[:, [0, 2, 1]].astype(np.int64)
    n = np.cross(V[F][:, 1] - V[F][:, 0], V[F][:, 2] - V[F][:, 0])
    F[n[:, 1] < 0] = F[n[:, 1] < 0][:, ::-1]
    # Yüz renkleri: toprak, kıyı kumu/çakılı, dik yamaçta taş; çimen bölgesinde çimen
    Wf = W[F].mean(1)
    kf = kiyi[F].mean(1)
    af = arsa[F].mean(1)
    n = np.cross(V[F][:, 1] - V[F][:, 0], V[F][:, 2] - V[F][:, 0])
    dik = 1 - np.abs(n[:, 1]) / (np.linalg.norm(n, axis=1) + 1e-12)
    rng = np.random.default_rng(5)
    t = rng.uniform(0, 1, len(F))
    C = np.tile(np.array(renk("cimen"), np.float32), (len(F), 1))
    kum = np.where(t[:, None] < 0.5, renk("kum"), renk("cakil"))
    C = np.where((kf > 0.3)[:, None], kum, C)
    C = np.where((kf > 0.85)[:, None], np.array(renk("toprak_koyu")) * 0.8, C)
    C = np.where((dik > 0.45)[:, None], renk("kaya_krem"), C)
    C = np.where((af > 0.3)[:, None], np.where(t[:, None] < 0.5, renk("toprak_arsa"), renk("toprak_arsa_acik")), C)
    m = Mesh(V, F, C.astype(np.float32), "zemin", W=W.astype(np.float32))
    # Dik yamaçlarda çimen olmasın
    dik_v = np.zeros(len(V))
    np.maximum.at(dik_v, F.ravel(), np.repeat(dik, 3))
    m.W = np.minimum(m.W, 1 - _ss(0.4, 0.55, dik_v)).astype(np.float32)
    m.NV = _kose_normalleri(V, F)
    # Köşe renkleri: çimen dışı yerlerde (W küçük) görünen toprak, kum, çakıl, taş
    t = _noise2(P[:, 0] * 9, P[:, 1] * 9, 7) * 0.5 + 0.5
    cv = np.tile(np.array(renk("cimen")), (len(V), 1))
    kum = np.where((t > 0.5)[:, None], renk("kum"), renk("cakil"))
    cv = cv + (kum - cv) * _ss(0.2, 0.45, kiyi)[:, None]
    cv = cv + (np.array(renk("toprak_koyu")) * 0.8 - cv) * _ss(0.8, 0.95, kiyi)[:, None]
    cv = cv + (np.array(renk("kaya_krem")) - cv) * _ss(0.4, 0.55, dik_v)[:, None]
    cv = cv + (np.array(renk("arsa_cimen")) - cv) * _ss(0.2, 0.5, arsa)[:, None]
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
        m = _yon_duzelt(m, True)
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
# ZB_dunya_dereceler: ufuktaki duvarlar, sekiler, çağlayanlar
# --------------------------------------------------------------------------

def _kaburga(phi, k):
    """Duvar yüzündeki dikey payandalar (içe doğru girinti, metre)."""
    s = 0.0
    for f, a, p in ((41, 1.0, 0.3), (97, 0.6, 1.1), (211, 0.35, 2.3)):
        s = s + a * np.abs(np.sin(f * phi + p + k))
    return 7.0 * s


def _duvar(k):
    R, ust = DUVARLAR[k]
    alt = (DUVARLAR[k - 1][1] if k > 0 else 0.0) - 6.0
    dphi = 0.35 if k == 0 else 0.6
    phis = np.radians(np.arange(-DUVAR_ACI, DUVAR_ACI + 1e-6, dphi))
    nv = 16
    vs = np.linspace(0, 1, nv + 1)
    V, W = [], []
    ust_y = duvar_ust(k, phis)
    for v in vs:
        r = (duvar_r(k, phis) + duvar_etek(v) - _kaburga(phis, k) * _ss(0.2, 0.5, v) * (0.4 + 0.6 * v)
             + 4.0 * _ss(0.88, 1.0, v))
        taban = (ova_y(*kartezyen(duvar_r(0, phis) + 95, phis)) - 6) if k == 0 else duvar_ust(k - 1, phis) - 6
        y = taban + (ust_y - taban) * v
        x, z = kartezyen(r, phis)
        V += list(np.stack([x, y, z], 1))
    rng = np.random.default_rng(70 + k)
    renkler = []
    for j in range(nv):
        v = (j + 0.5) / nv
        serit = _noise2(np.full(len(phis) - 1, v * 900.0), phis[:-1] * 300.0, 80 + k)
        tas = np.where(serit[:, None] > 0.4, renk("kaya_pembe"),
                       np.where(serit[:, None] < -0.5, renk("kaya_altin"), renk("kaya_krem")))
        sarkan = (_noise2(phis[:-1] * 2500.0, np.zeros(len(phis) - 1), 90 + k) * 0.5 + 0.5) > (1.2 - v * 0.8)
        orman = v < 0.3 + 0.12 * _noise2(phis[:-1] * 900.0, np.zeros(len(phis) - 1), 95 + k)
        yesil = np.where(rng.uniform(0, 1, len(phis) - 1)[:, None] < 0.5, renk("yaprak_zumrut"), renk("yaprak_koyu"))
        row = np.where((sarkan | orman)[:, None] | (v > 0.9), yesil, tas)
        renkler.append(list(row))
    m = _izgara_mesh(V, len(phis) - 1, nv, renkler, "tas")
    # Yüzler merkezden dışa (oyuncuya) baksın
    tri = m.V[m.F]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    c = tri.mean(1)
    dis = np.stack([c[:, 0] - MERKEZ[0], np.zeros(len(c)), c[:, 2] - MERKEZ[1]], 1)
    if (n * dis).sum() < 0:
        m = m.flipped()
        m.NV = -m.NV
    return m


def _seki(k):
    """k. duvarın üstündeki seki: bir sonraki duvarın dibine kadar uzanan çayır."""
    R_ic = DUVARLAR[k + 1][0] if k + 1 < len(DUVARLAR) else DUVARLAR[k][0] - 420.0
    y0 = DUVARLAR[k][1]
    dphi = 0.7
    phis = np.radians(np.arange(-DUVAR_ACI, DUVAR_ACI + 1e-6, dphi))
    nr = 10
    V = []
    for i in range(nr + 1):
        t = i / nr
        r = duvar_r(k, phis) + 3.0 + (duvar_r(k + 1, phis) + 60.0 - duvar_r(k, phis) - 3.0) * t \
            if k + 1 < len(DUVARLAR) else duvar_r(k, phis) + 3.0 - 420.0 * t
        x, z = kartezyen(r, phis)
        y = duvar_ust(k, phis) + _noise2(x * 2, z * 2, 60 + k) * 3.0
        V += list(np.stack([x, y, z], 1))
    renkler = [[renk("cimen")] * (len(phis) - 1) for _ in range(nr)]
    m = _izgara_mesh(V, len(phis) - 1, nr, renkler, "zemin")
    return _yon_duzelt(m, True)


def _selale_seridi(k, phi, gen):
    """k. duvardan dökülen çağlayan: duvar yüzünü izleyen, aşağıda açılan şerit."""
    ust = float(duvar_ust(k, phi))
    alt = (ova_y(*kartezyen(duvar_r(0, phi) + 95, phi)) - 2.0) if k == 0 else float(duvar_ust(k - 1, phi)) - 2.0
    nv = 18
    V = []
    for j in range(nv + 1):
        v = 1 - j / nv
        r = float(duvar_r(k, phi)) + duvar_etek(v) + 5.0 + 9.0 * (1 - v) ** 0.6
        y = alt + (ust + 0.6 - alt) * v
        g = gen * (0.65 + 0.55 * (1 - v))
        da = g / 2 / r
        for s in (-1, 1):
            x, z = kartezyen(r, phi + s * da)
            V.append([float(x), float(y), float(z)])
    F = []
    for j in range(nv):
        a = 2 * j
        F += [[a, a + 1, a + 3], [a, a + 3, a + 2]]
    m = Mesh(np.array(V, np.float32), np.array(F, np.int64),
             np.tile(np.array(renk("su"), np.float32), (len(F), 1)), "selale")
    tri = m.V[m.F]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    c = tri.mean(1)
    dis = np.stack([c[:, 0] - MERKEZ[0], np.zeros(len(c)), c[:, 2] - MERKEZ[1]], 1)
    if (n * dis).sum() < 0:
        m = m.flipped()
    m.W = np.repeat(np.linspace(1, 0, nv + 1), 2).astype(np.float32)   # COLOR.a: 1 tepe, 0 dip
    return m, (float(kartezyen(r, phi)[0]), float(alt), float(kartezyen(r, phi)[1]), gen)


def selaleler():
    """Bütün çağlayanlar ve dip noktaları (sis parçacıkları için)."""
    seritler, dipler = [], []
    for ir in IRMAKLAR:
        phi = math.radians(ir["phi"])
        for k in range(len(DUVARLAR) - 1):
            gen = ir["gen"] * (1.6 if k == 0 else 2.4)
            m, dip = _selale_seridi(k, phi + 0.012 * k, gen)
            seritler.append(m)
            if k == 0:
                dipler.append(dip)
    rng = np.random.default_rng(77)
    for k, adet in ((0, 9), (1, 7), (2, 5)):
        for _ in range(adet):
            phi = math.radians(rng.uniform(-45, 45))
            if min(abs(phi - math.radians(ir["phi"])) for ir in IRMAKLAR) < math.radians(3):
                continue
            m, dip = _selale_seridi(k, phi, rng.uniform(3.0, 7.0) * (1 + k))
            seritler.append(m)
            if k == 0:
                dipler.append(dip)
    return seritler, dipler


@model("ZB_dunya_dereceler")
def dunya_dereceler() -> Node:
    root = Node("ZB_dunya_dereceler")
    root.add(Node("duvarlar", [merge(*[_duvar(k) for k in range(len(DUVARLAR))])]))
    root.add(Node("sekiler", [merge(*[_seki(k) for k in range(len(DUVARLAR))])]))
    root.add(Node("selaleler", [merge(*selaleler()[0])]))
    return root


# --------------------------------------------------------------------------
# ZB_dunya_derece_koni: dışarıdan görünen katlı koni-dağ
# --------------------------------------------------------------------------

KONI_R = [1000.0, 830.0, 675.0, 540.0, 420.0, 315.0, 225.0, 150.0, 92.0]
KONI_Y = [0.0, 120.0, 235.0, 345.0, 450.0, 550.0, 645.0, 735.0, 815.0]
KONI_TABAN = -320.0
KONI_IRMAK_ACI = [25.0, 115.0, 205.0, 295.0]
KONI_IRMAK = ["su", "sut", "bal", "serbet"]


def koni_r(i, phi):
    phi = np.asarray(phi, float)
    R = KONI_R[i]
    return R * (1 + 0.07 * np.sin(3 * phi + i) + 0.04 * np.sin(7 * phi + 2 * i) + 0.015 * np.sin(19 * phi + i))


def koni_y(i, phi):
    """i. sekinin yüksekliği: halkalar düz değil, hafifçe dalgalanır."""
    phi = np.asarray(phi, float)
    if i >= len(KONI_Y) - 1:
        return np.full_like(phi, KONI_Y[i])
    return KONI_Y[i] + (10.0 + 1.5 * i) * np.sin(2 * phi + 0.7 * i) + 5.0 * np.sin(5 * phi + i)


def _koni_duvar(i, nphi=240):
    """i. halkanın dış duvarı (i=0 dağın bulutlara inen eteği)."""
    phis = np.linspace(-math.pi, math.pi, nphi + 1)
    alt = KONI_TABAN if i == 0 else koni_y(i - 1, phis) - 4
    ust = koni_y(i, phis)
    nv = 14 if i == 0 else 8
    V = []
    for j in range(nv + 1):
        v = j / nv
        acil = (0.22 * (1 - v) ** 1.5) if i == 0 else 0.07 * (1 - v) ** 2.2
        r = (koni_r(i, phis) * (1 + acil)
             - 0.012 * KONI_R[i] * _kaburga(phis * 1.5, i) / 7.0 * _ss(0.2, 0.45, v) * (0.4 + 0.6 * v))
        y = alt + (ust - alt) * v
        V += list(np.stack([r * np.sin(phis), np.full_like(phis, y), r * np.cos(phis)], 1))
    renkler = []
    for j in range(nv):
        v = (j + 0.5) / nv
        serit = _noise2(np.full(nphi, v * 700.0 + i * 50), phis[:-1] * 200.0, 120 + i)
        tas = np.where(serit[:, None] > 0.4, renk("kaya_pembe"),
                       np.where(serit[:, None] < -0.5, renk("kaya_altin"), renk("kaya_krem")))
        yesil = (_noise2(phis[:-1] * 1800.0, np.zeros(nphi), 130 + i) * 0.5 + 0.5) > (1.2 - v * 0.8)
        if i > 0:
            yesil |= v < 0.3 + 0.12 * _noise2(phis[:-1] * 900.0, np.zeros(nphi), 135 + i)
        renkler.append(list(np.where(yesil[:, None] | (v > 0.88), renk("yaprak_zumrut"), tas)))
    m = _izgara_mesh(V, nphi, nv, renkler, "tas")
    tri = m.V[m.F]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    c = tri.mean(1)
    if (n[:, [0, 2]] * c[:, [0, 2]]).sum() < 0:
        m = m.flipped()
        m.NV = -m.NV
    return m


def _koni_seki(i, nphi=240):
    """i. halkanın üstü: çayır; üst halkalarda çiçek tarlaları daha çok (Rahmân 46-61)."""
    phis = np.linspace(-math.pi, math.pi, nphi + 1)
    nr = 8
    V, W = [], []
    rng = np.random.default_rng(140 + i)
    for j in range(nr + 1):
        t = j / nr
        r = koni_r(i, phis) * (1 - t) + (koni_r(i + 1, phis) * 1.02) * t
        y = koni_y(i, phis) + 6 * np.sin(phis * 5 + i) * t * (1 - t) + 10 * t ** 3
        V += list(np.stack([r * np.sin(phis), y, r * np.cos(phis)], 1))
        x, z = r * np.sin(phis), r * np.cos(phis)
        cicek = _ss(0.25, 0.6, _noise2(x * 8, z * 8, 150 + i) * 0.5 + 0.5) * min(1.0, 0.25 + i * 0.12)
        W += list(1 - cicek)
    tarla = ["gul", "lale_sari", "inci", "lale", "kaya_pembe"]
    renkler = []
    for j in range(nr):
        renkler.append([renk(tarla[(k // 7 + j + i) % len(tarla)]) for k in range(nphi)])
    m = _izgara_mesh(V, nphi, nr, renkler, "zemin", W=W)
    return _yon_duzelt(m, True)


def _koni_irmaklari():
    """Dört ırmak zirveden iner: her sekide çaprazlama akar, her duvardan çağlayanla dökülür."""
    seritler, selale = {k: [] for k in KONI_IRMAK}, []
    for j, (aci, ad) in enumerate(zip(KONI_IRMAK_ACI, KONI_IRMAK)):
        for i in range(len(KONI_R) - 1):
            p0 = math.radians(aci + 9 * (i + 1))
            p1 = math.radians(aci + 9 * i)
            gen = 26.0 - i * 2.0
            # Seki üstünde akış: iç duvarın dibinden dış kenara
            n = 14
            V = []
            for k in range(n + 1):
                t = k / n
                phi = p0 + (p1 - p0) * t
                r = float(koni_r(i + 1, phi)) * 1.03 * (1 - t) + float(koni_r(i, phi)) * 0.995 * t
                y = float(koni_y(i, phi)) + 1.2 + 6 * math.sin(phi * 5 + i) * t * (1 - t) + 10 * (1 - t) ** 3
                da = gen / 2 / r
                for s in (-1, 1):
                    V.append([r * math.sin(phi + s * da), y, r * math.cos(phi + s * da)])
            F = []
            for k in range(n):
                a = 2 * k
                F += [[a, a + 1, a + 3], [a, a + 3, a + 2]]
            m = Mesh(np.array(V, np.float32), np.array(F, np.int64),
                     np.tile(np.array(renk(ad), np.float32), (len(F), 1)), ad)
            seritler[ad].append(_yon_duzelt(m, True))
            # Dış kenardan aşağı çağlayan (i=0: bulut denizine)
            alt = KONI_TABAN + 150 if i == 0 else float(koni_y(i - 1, p1)) + 1
            nv = 12
            V = []
            for k in range(nv + 1):
                v = 1 - k / nv
                acil = (0.22 * (1 - v) ** 1.5) if i == 0 else 0.07 * (1 - v) ** 2.2
                r = float(koni_r(i, p1)) * (1 + acil) + 4 + 6 * (1 - v) ** 0.6
                y = alt + (float(koni_y(i, p1)) + 1.2 - alt) * v
                da = gen * (0.7 + 0.6 * (1 - v)) / 2 / r
                for s in (-1, 1):
                    V.append([r * math.sin(p1 + s * da), y, r * math.cos(p1 + s * da)])
            F = []
            for k in range(nv):
                a = 2 * k
                F += [[a, a + 1, a + 3], [a, a + 3, a + 2]]
            m = Mesh(np.array(V, np.float32), np.array(F, np.int64),
                     np.tile(np.array(renk("su"), np.float32), (len(F), 1)), "selale")
            tri = m.V[m.F]
            nn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
            c = tri.mean(1)
            if (nn[:, [0, 2]] * c[:, [0, 2]]).sum() < 0:
                m = m.flipped()
            m.W = np.repeat(np.linspace(1, 0, nv + 1), 2).astype(np.float32)
            selale.append(m)
    return seritler, selale


def _koni_koskleri():
    """Sekilerde küçük inci kubbeler: uzaktan parıldayan köşkler."""
    rng = np.random.default_rng(160)
    out = []
    for i in range(len(KONI_R) - 1):
        for _ in range(10 + 2 * i):
            phi = rng.uniform(-math.pi, math.pi)
            t = rng.uniform(0.25, 0.75)
            r = float(koni_r(i, phi)) * (1 - t) + float(koni_r(i + 1, phi)) * t
            y = float(koni_y(i, phi)) + 6 * math.sin(phi * 5 + i) * t * (1 - t) + 10 * t ** 3
            b = rng.uniform(5.0, 9.0)
            out.append(lathe([(b, 0), (b * 0.97, b * 0.4), (b * 0.75, b * 0.85), (b * 0.35, b * 1.15), (0, b * 1.25)],
                             10, "inci").translate(r * math.sin(phi), y - 0.5, r * math.cos(phi)))
    return merge(*out).smooth(60)


@model("ZB_dunya_derece_koni")
def dunya_derece_koni() -> Node:
    root = Node("ZB_dunya_derece_koni")
    n = len(KONI_R) - 1
    duvarlar = [_koni_duvar(i) for i in range(n + 1)]
    sekiler = [_koni_seki(i) for i in range(n)]
    seritler, selale = _koni_irmaklari()
    zirve = lathe([(KONI_R[-1] * 1.05, KONI_Y[-1]), (KONI_R[-1] * 0.8, KONI_Y[-1] + 6), (0.0, KONI_Y[-1] + 9)],
                  48, "nur_beyaz").with_material("nur")
    root.add(Node("duvarlar", [merge(*duvarlar)]), Node("sekiler", [merge(*sekiler)]),
             Node("irmaklar", [merge(*v) for v in seritler.values()]), Node("selaleler", [merge(*selale)]),
             Node("koskler", [_koni_koskleri()]), Node("zirve", [zirve]))
    root.add(Node("isik_zirve", translation=(0.0, KONI_Y[-1] + 40.0, 0.0)))
    return root


# --------------------------------------------------------------------------
# Yerleşim: bitkiler, yapılar, parçacık noktaları, kameralar, çimen ızgarası
# --------------------------------------------------------------------------

def _yerde(x, z, irmaklar):
    return float(arazi_y(np.array([x]), np.array([z]), irmaklar)[0])


def _irmak_yonu(ir, z):
    i = int(np.argmin(np.abs(ir.P[:, 1] - z) + 1e3 * (np.hypot(*(ir.P - ir.P[0]).T) < 50)))
    j = min(i + 3, len(ir.P) - 1)
    d = ir.P[j] - ir.P[max(i - 3, 0)]
    return ir.P[i], float(ir.wl[i]), math.degrees(math.atan2(d[0], d[1]))


def yerlesim() -> dict:
    irmaklar = _irmaklar()
    su = irmaklar[0]
    rng = np.random.default_rng(2026)
    d: dict = {"merkez": MERKEZ.tolist(), "arsa_r": ARSA_R, "duvarlar": DUVARLAR}

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
    d["su_kosku"] = [[round(float(kosk_p[0]), 2), round(kosk_y, 2), round(float(kosk_p[1]), 2), round(kosk_rot, 1), 1.0],
                     [round(float(kosk2_p[0]), 2), round(kosk2_y, 2), round(float(kosk2_p[1]), 2), round(kosk2_rot, 1), 0.9],
                     [round(float(sut_p[0]), 2), round(sut_y, 2), round(float(sut_p[1]), 2), round(sut_rot, 1), 0.85],
                     [round(float(bal_p[0]), 2), round(bal_y, 2), round(float(bal_p[1]), 2), round(bal_rot, 1), 1.0]]
    cadir = (40.0, -62.0)
    d["inci_cadir"] = [yer(*cadir, rot=math.degrees(math.atan2(-cadir[0], -cadir[1])), dy=-0.2)]
    sedir = (-15.0, -24.0)
    d["sedir_kosesi"] = [yer(*sedir, rot=25.0, dy=0.02)]
    d["selsebil"] = [yer(-10.5, -30.5, rot=-20.0, dy=-0.05)]
    d["pinar"] = [yer(-21.5, -17.5, dy=-0.1)]
    yapilar = [(kosk_p[0], kosk_p[1], 18), (kosk2_p[0], kosk2_p[1], 18), (sut_p[0], sut_p[1], 16),
               (bal_p[0], bal_p[1], 18), (cadir[0], cadir[1], 10), (sedir[0], sedir[1], 4), (-10.5, -30.5, 3),
               (-21.5, -17.5, 3)]

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
    d["gul"] = gul
    lale = []
    for cx, cz, n in ((16.0, 18.0, 70), (-10.0, 22.0, 60), (20.0, -18.0, 50), (-6.0, -34.0, 45), (8.0, 30.0, 60)):
        for _ in range(n):
            r = 3.2 * math.sqrt(rng.uniform(0, 1))
            a = rng.uniform(0, 2 * math.pi)
            x, z = cx + r * math.cos(a), cz + r * math.sin(a) * 0.7
            if bos_mu(x, z, 0.0, yapilar):
                lale.append(yer(x, z, olcek=rng.uniform(0.85, 1.2), dy=-0.02))
    d["lale"] = lale

    # --- Korular (koyu yeşil, Rahmân 64) ve uzak ağaçlar
    koru, uzak = [], []
    kumeler = [(-110, -60, 40, 26), (-140, -150, 50, 32), (-95, -230, 45, 26), (120, -80, 45, 24), (150, -170, 55, 30),
               (70, -260, 45, 22), (-20, -300, 60, 28), (40, -150, 30, 14), (-60, 40, 30, 10), (95, 60, 35, 14),
               (-150, 20, 40, 18), (160, -20, 40, 18), (-190, -90, 45, 22), (200, -110, 45, 22), (10, -210, 35, 14)]
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
    while len(uzak) < 2600:
        a = rng.uniform(-math.pi, math.pi)
        r = 260 * math.exp(rng.uniform(0, math.log(9.0)))
        x, z = r * math.sin(a), -r * math.cos(a)
        rho, phi = kutup(x, z)
        if rho < duvar_r(0, phi) + 25 or z > 600:
            continue
        # Koru kümeleri halinde: gürültü eşiği
        if _noise2(np.array([x * 6.0]), np.array([z * 6.0]), 170)[0] < 0.1:
            continue
        if bos_mu(x, z, 6.0, yapilar):
            uzak.append(yer(x, z, olcek=rng.uniform(1.9, 3.0), dy=-0.3))
    # Derece kenarlarında ağaç saçağı
    for k in range(len(DUVARLAR)):
        R, ust = DUVARLAR[k]
        adim = 11.0 + 5 * k
        for phi in np.arange(-math.radians(65.0), math.radians(65.0), adim / R):
            for sira in range(2):
                p = phi + rng.uniform(-0.3, 0.3) * adim / R
                r = float(duvar_r(k, p)) - 10.0 - sira * 22.0 - rng.uniform(0, 12)
                x, z = kartezyen(r, p)
                y = float(duvar_ust(k, p)) + _noise2(np.array([x * 2]), np.array([z * 2]), 60 + k)[0] * 3.0
                uzak.append([round(float(x), 1), round(float(y) - 0.5, 1), round(float(z), 1),
                             round(float(rng.uniform(0, 360)), 0), round(float(rng.uniform(1.8, 3.0) * (1 + 0.3 * k)), 2)])
    d["uzak_agac"] = uzak

    # --- Dev Tûbâ (üçüncü sekide, sağda)
    tphi = math.radians(27.0)
    tx, tz = kartezyen(1230.0, tphi)
    d["tuba_dev"] = [round(float(tx), 1), round(float(duvar_ust(1, tphi)) - 4.0, 1), round(float(tz), 1), 20.0, 1.0]

    # --- Çağlayan dipleri, fıskiyeler, ırmak ışıltısı
    _, dipler = selaleler()
    d["selale_dip"] = [[round(a, 1), round(b, 1), round(c, 1), round(g, 1)] for a, b, c, g in dipler]

    # --- Koni-dağın sekilerindeki ağaçlar (dış görünüm); ırmak yollarından uzak
    koni = []
    for i in range(len(KONI_R) - 1):
        adet = int(2000 * (KONI_R[i] ** 2 - KONI_R[i + 1] ** 2) / (KONI_R[0] ** 2 - KONI_R[1] ** 2))
        adet = max(adet, 60)
        while adet > 0:
            phi = rng.uniform(-math.pi, math.pi)
            t = rng.uniform(0.08, 0.85)
            yakin = min(abs((math.degrees(phi) - (aci + 9 * (i + 1 - t)) + 180) % 360 - 180) for aci in KONI_IRMAK_ACI)
            if yakin < 3.0:
                continue
            r = float(koni_r(i, phi)) * (1 - t) + float(koni_r(i + 1, phi)) * 1.02 * t
            y = float(koni_y(i, phi)) + 6 * math.sin(phi * 5 + i) * t * (1 - t) + 10 * t ** 3
            koni.append([round(r * math.sin(phi), 1), round(y - 0.5, 1), round(r * math.cos(phi), 1),
                         round(float(rng.uniform(0, 360)), 0), round(float(rng.uniform(4.0, 6.0)), 2)])
            adet -= 1
    d["koni_agac"] = koni

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
        "ufuk": {"konum": [12.0, _yerde(12, 38, irmaklar) + 17.0, 38.0], "hedef": [-30.0, 22.0, -700.0], "fov": 55.0},
        "arsa": {"konum": [9.0, 5.8, 21.0], "hedef": [-12.0, 0.5, -40.0], "fov": 50.0},
        "derece": {"konum": [1750.0, 170.0, 1950.0], "hedef": [0.0, 470.0, 0.0], "fov": 42.0},
    }
    return d


def yerlesim_yaz(root: Path) -> Path:
    p = root / "game" / "data" / "dunya_cennet.json"
    p.write_text(json.dumps(yerlesim(), ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return p
