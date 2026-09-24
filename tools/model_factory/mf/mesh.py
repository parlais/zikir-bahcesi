"""Düz gölgeli (flat shaded) low-poly mesh ve primitifler.

Bir Mesh üçgen yüzlerden oluşur; her yüzün kendi rengi vardır. Dışa aktarımda
her yüz kendi köşelerini alır (normal paylaşılmaz), bu da stilize low-poly
görünümü verir. Bütün ölçüler metredir, Y yukarıdır.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from .palette import renk


def _rgb(c) -> np.ndarray:
    return np.asarray(renk(c) if isinstance(c, str) else c, dtype=np.float32)


@dataclass
class Mesh:
    V: np.ndarray                      # (n, 3) köşeler
    F: np.ndarray                      # (m, 3) üçgenler
    C: np.ndarray                      # (m, 3) yüz renkleri (doğrusal değil, sRGB 0-1)
    material: str = "mat"              # malzeme adı; Godot bu ada göre shader atar
    W: np.ndarray | None = None        # (n,) köşe ağırlığı -> COLOR_0.a (rüzgâr salınımı, 0 dip 1 uç)
    S: np.ndarray | None = None        # (m,) yüz başına yumuşatma açısı (derece; 0 = düz gölge)
    NV: np.ndarray | None = None       # (n, 3) elle verilmiş köşe normalleri (sıfır = hesapla)
    CV: np.ndarray | None = None       # (n, 3) köşe renkleri: verilirse köşeler paylaşılır (indeksli, yumuşak
                                       # renk geçişi; büyük arazilerde dosyayı küçültür). NV de verilmelidir.

    def __post_init__(self):
        if self.W is None:
            self.W = np.ones(len(self.V), dtype=np.float32)
        if self.S is None:
            self.S = np.zeros(len(self.F), dtype=np.float32)
        if self.NV is None:
            self.NV = np.zeros((len(self.V), 3), dtype=np.float32)

    # --- dönüşümler (hepsi yeni Mesh döndürür) ---------------------------
    def copy(self) -> "Mesh":
        return Mesh(self.V.copy(), self.F.copy(), self.C.copy(), self.material, self.W.copy(), self.S.copy(),
                    self.NV.copy(), None if self.CV is None else self.CV.copy())

    def kure_normal(self, merkez, olcek=(1.0, 1.0, 1.0)) -> "Mesh":
        """Yaprak kümeleri için normalleri tacın merkezinden dışa yönlendirir:
        yüzlerce küçük yaprak tek bir yumuşak, kabarık kütle gibi ışık alır."""
        m = self.copy()
        d = (m.V - np.asarray(merkez, np.float32)) / np.asarray(olcek, np.float32)
        m.NV = d / (np.linalg.norm(d, axis=1, keepdims=True) + 1e-9)
        return m

    def eksen_normal(self, x=0.0, z=0.0, dikey=0.25) -> "Mesh":
        """Selvi gibi dik kütleler: normaller dikey eksenden dışa (biraz yukarı)."""
        m = self.copy()
        d = m.V - np.array([x, 0.0, z], np.float32)
        d[:, 1] = dikey * np.linalg.norm(d[:, [0, 2]], axis=1)
        m.NV = d / (np.linalg.norm(d, axis=1, keepdims=True) + 1e-9)
        return m

    def smooth(self, aci: float = 50.0) -> "Mesh":
        """Yumuşak gölge: aralarındaki açı `aci` dereceden küçük komşu yüzlerin
        normalleri ortalanır. Keskin kenarlar (kutu köşeleri) keskin kalır."""
        m = self.copy()
        m.S = np.full(len(m.F), aci, dtype=np.float32)
        return m

    def weight(self, fn) -> "Mesh":
        """Köşe ağırlığını konumdan hesaplar: fn(V) -> (n,) 0..1."""
        m = self.copy()
        m.W = np.clip(np.asarray(fn(m.V), dtype=np.float32), 0, 1)
        return m

    def translate(self, x=0.0, y=0.0, z=0.0) -> "Mesh":
        m = self.copy()
        m.V = m.V + np.array([x, y, z], dtype=np.float32)
        return m

    def scale(self, sx, sy=None, sz=None) -> "Mesh":
        sy = sx if sy is None else sy
        sz = sx if sz is None else sz
        m = self.copy()
        m.V = m.V * np.array([sx, sy, sz], dtype=np.float32)
        if sx * sy * sz < 0:
            m.F = m.F[:, ::-1].copy()
        return m

    def rotate(self, axis: str, deg: float) -> "Mesh":
        m = self.copy()
        R = rot(axis, deg)
        m.V = m.V @ R.T
        m.NV = m.NV @ R.T
        return m

    def transform(self, M: np.ndarray) -> "Mesh":
        m = self.copy()
        m.V = m.V @ M.T
        return m

    def recolor(self, c) -> "Mesh":
        m = self.copy()
        m.C = np.tile(_rgb(c), (len(m.F), 1))
        return m

    def with_material(self, name: str) -> "Mesh":
        m = self.copy()
        m.material = name
        return m

    def flipped(self) -> "Mesh":
        """Yüzleri ters çevirir (çanağın içi gibi içeriden görülen yüzeyler için)."""
        m = self.copy()
        m.F = m.F[:, ::-1].copy()
        return m

    def double_sided(self) -> "Mesh":
        """İnce yüzeyler (yaprak, taç yaprak) arkadan da görünsün (normaller elle verilmişse
        arka yüz de aynı normali kullanır; kabarık taç görünümü böyle korunur)."""
        m = self.copy()
        m.F = np.vstack([m.F, m.F[:, ::-1]])
        m.C = np.vstack([m.C, m.C])
        m.S = np.concatenate([m.S, m.S])
        return m

    def jitter(self, amount: float, seed: int = 0, keep_y_below: float | None = None) -> "Mesh":
        """Köşeleri hafifçe oynatır (kaya, yaprak kümesi için doğal görünüm).
        Aynı konumdaki köşeler aynı miktarda kayar, böylece yüzeyde yırtık oluşmaz."""
        m = self.copy()
        rng = np.random.default_rng(seed)
        keys = np.round(m.V, 4)
        uniq, inv = np.unique(keys, axis=0, return_inverse=True)
        off = rng.uniform(-amount, amount, size=uniq.shape).astype(np.float32)
        if keep_y_below is not None:
            off[uniq[:, 1] <= keep_y_below, 1] = 0
        m.V = m.V + off[inv.reshape(-1)]
        return m

    def shade_vary(self, amount: float = 0.05, seed: int = 0) -> "Mesh":
        """Yüz renklerine küçük parlaklık farkı: tek düze plastik görünümü kırar."""
        m = self.copy()
        rng = np.random.default_rng(seed)
        k = 1.0 + rng.uniform(-amount, amount, size=(len(m.F), 1)).astype(np.float32)
        m.C = np.clip(m.C * k, 0, 1)
        return m

    @property
    def tri_count(self) -> int:
        return len(self.F)

    def bounds(self):
        return self.V.min(axis=0), self.V.max(axis=0)


def merge(*meshes: Mesh) -> Mesh:
    ms = [m for m in meshes if m is not None]
    mats = {m.material for m in ms}
    assert len(mats) == 1, f"Farklı malzemeler birleştirilemez: {mats}"
    V, F, C, W, S, NV, off = [], [], [], [], [], [], 0
    for m in ms:
        V.append(m.V)
        F.append(m.F + off)
        C.append(m.C)
        W.append(m.W)
        S.append(m.S)
        NV.append(m.NV)
        off += len(m.V)
    CV = None
    if all(m.CV is not None for m in ms):
        CV = np.vstack([m.CV for m in ms]).astype(np.float32)
    return Mesh(np.vstack(V).astype(np.float32), np.vstack(F).astype(np.int64),
                np.vstack(C).astype(np.float32), ms[0].material,
                np.concatenate(W).astype(np.float32), np.concatenate(S).astype(np.float32),
                np.vstack(NV).astype(np.float32), CV)


def rot(axis: str, deg: float) -> np.ndarray:
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    if axis == "x":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=np.float32)
    if axis == "y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=np.float32)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float32)


def _mk(V, F, color, material="mat") -> Mesh:
    F = np.asarray(F, dtype=np.int64).reshape(-1, 3)
    return Mesh(np.asarray(V, dtype=np.float32), F, np.tile(_rgb(color), (len(F), 1)), material)


# --------------------------------------------------------------------------
# Primitifler
# --------------------------------------------------------------------------

def box(w, h, d, color="tas", y0=0.0) -> Mesh:
    """Tabanı y0'da olan kutu (x, z merkezli)."""
    x, z = w / 2, d / 2
    V = [[-x, y0, -z], [x, y0, -z], [x, y0, z], [-x, y0, z],
         [-x, y0 + h, -z], [x, y0 + h, -z], [x, y0 + h, z], [-x, y0 + h, z]]
    F = [[0, 1, 2], [0, 2, 3],  # alt
         [4, 6, 5], [4, 7, 6],  # üst
         [0, 4, 5], [0, 5, 1], [1, 5, 6], [1, 6, 2],
         [2, 6, 7], [2, 7, 3], [3, 7, 4], [3, 4, 0]]
    return _mk(V, F, color)


def lathe(profile, seg=8, color="tas", start_deg=0.0, sweep=360.0, cap=True) -> Mesh:
    """Y ekseni etrafında döndürülmüş profil. profile: [(yarıçap, y), ...] aşağıdan yukarı.
    Yarıçapı 0 olan uç noktalar tek köşeye (kutup) iner; açık uçlar cap=True ise
    düz kapakla kapanır (çanak, kabuk gibi açık yüzeylerde cap=False)."""
    prof = [(float(r), float(y)) for r, y in profile]
    full = abs(sweep - 360.0) < 1e-6
    n_ang = seg if full else seg + 1
    angs = [math.radians(start_deg + sweep * i / seg) for i in range(n_ang)]
    V, F, ring_idx = [], [], []
    for r, y in prof:
        if r < 1e-9:
            ring_idx.append([len(V)] * n_ang)
            V.append([0.0, y, 0.0])
        else:
            idx = []
            for a in angs:
                idx.append(len(V))
                V.append([r * math.cos(a), y, r * math.sin(a)])
            ring_idx.append(idx)
    for k in range(len(prof) - 1):
        lo, hi = ring_idx[k], ring_idx[k + 1]
        for i in range(seg):
            j = (i + 1) % n_ang
            a, b, c, d = lo[i], lo[j], hi[j], hi[i]
            if a != b:
                F.append([a, c, b])
            if c != d:
                F.append([a, d, c])
    if full and cap:
        # Kapaklar
        r0, y0 = prof[0]
        if r0 > 1e-9:
            ci = len(V)
            V.append([0.0, y0, 0.0])
            ring = ring_idx[0]
            for i in range(seg):
                F.append([ci, ring[i], ring[(i + 1) % seg]])
        r1, y1 = prof[-1]
        if r1 > 1e-9:
            ci = len(V)
            V.append([0.0, y1, 0.0])
            ring = ring_idx[-1]
            for i in range(seg):
                F.append([ci, ring[(i + 1) % seg], ring[i]])
    return _mk(V, F, color)


def cylinder(r_bottom, r_top, h, seg=8, color="tas", y0=0.0) -> Mesh:
    return lathe([(r_bottom, y0), (r_top, y0 + h)], seg, color)


def cone(r, h, seg=8, color="tas", y0=0.0) -> Mesh:
    return lathe([(r, y0), (0.0, y0 + h)], seg, color)


def icosphere(r=1.0, subdiv=1, color="inci") -> Mesh:
    t = (1 + 5 ** 0.5) / 2
    V = [[-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0], [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t],
         [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1]]
    F = [[0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11], [1, 5, 9], [5, 11, 4], [11, 10, 2],
         [10, 7, 6], [7, 1, 8], [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9], [4, 9, 5],
         [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]]
    V = [list(np.array(v) / np.linalg.norm(v)) for v in V]
    for _ in range(subdiv):
        cache, nf = {}, []

        def mid(a, b):
            k = (min(a, b), max(a, b))
            if k not in cache:
                p = (np.array(V[a]) + np.array(V[b])) / 2
                V.append(list(p / np.linalg.norm(p)))
                cache[k] = len(V) - 1
            return cache[k]
        for a, b, c in F:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            nf += [[a, ab, ca], [b, bc, ab], [c, ca, bc], [ab, bc, ca]]
        F = nf
    return _mk(np.array(V) * r, F, color)


def blob(r, color, seed=0, subdiv=1, squash=1.0, jitter=0.18) -> Mesh:
    """Yaprak kümesi / kaya gibi düzensiz küre."""
    return icosphere(r, subdiv, color).scale(1, squash, 1).jitter(r * jitter, seed).shade_vary(0.06, seed)


def tube(path, radii, seg=6, color="govde", cap=True) -> Mesh:
    """Bir yol boyunca uzanan boru (eğri gövde, sap, dal). radii her noktada yarıçap."""
    P = np.asarray(path, dtype=np.float64)
    n = len(P)
    V, F = [], []
    prev_u = None
    for i in range(n):
        tng = P[min(i + 1, n - 1)] - P[max(i - 1, 0)]
        tng /= np.linalg.norm(tng) + 1e-12
        if prev_u is None:
            ref = np.array([1.0, 0, 0]) if abs(tng[0]) < 0.9 else np.array([0, 0, 1.0])
            u = np.cross(tng, ref)
        else:
            u = prev_u - np.dot(prev_u, tng) * tng
        u /= np.linalg.norm(u) + 1e-12
        v = np.cross(tng, u)
        prev_u = u
        for k in range(seg):
            a = 2 * math.pi * k / seg
            V.append(P[i] + radii[i] * (math.cos(a) * u + math.sin(a) * v))
    for i in range(n - 1):
        for k in range(seg):
            a, b = i * seg + k, i * seg + (k + 1) % seg
            c, d = (i + 1) * seg + (k + 1) % seg, (i + 1) * seg + k
            F += [[a, b, c], [a, c, d]]
    if cap:
        for i, flip in ((0, True), (n - 1, False)):
            if radii[i] < 1e-6:
                continue
            ci = len(V)
            V.append(P[i])
            for k in range(seg):
                a, b = i * seg + k, i * seg + (k + 1) % seg
                F.append([ci, b, a] if flip else [ci, a, b])
    return _mk(V, F, color)


def blade(path, widths, color="yaprak", fold=0.25, side=None) -> Mesh:
    """Yaprak/taç yaprak şeridi: yol boyunca eni değişen, ortadan hafif katlanmış yüzey.
    side: şeridin açıldığı yön (verilmezse yola dik yatay yön)."""
    P = np.asarray(path, dtype=np.float64)
    n = len(P)
    V, F = [], []
    for i in range(n):
        tng = P[min(i + 1, n - 1)] - P[max(i - 1, 0)]
        tng /= np.linalg.norm(tng) + 1e-12
        s = np.asarray(side, dtype=np.float64) if side is not None else np.cross(tng, [0, 1, 0])
        if np.linalg.norm(s) < 1e-6:
            s = np.array([1.0, 0, 0])
        s = s - np.dot(s, tng) * tng
        s /= np.linalg.norm(s) + 1e-12
        up = np.cross(s, tng)
        w = widths[i]
        V.append(P[i] - s * w - up * w * fold)
        V.append(P[i] + up * w * fold * 0.3)
        V.append(P[i] + s * w - up * w * fold)
    for i in range(n - 1):
        a = 3 * i
        b = 3 * (i + 1)
        F += [[a, b, a + 1], [a + 1, b, b + 1], [a + 1, b + 1, a + 2], [a + 2, b + 1, b + 2]]
    return _mk(V, F, color).double_sided()


def band(inner, outer, depth, color="tas") -> Mesh:
    """İç ve dış eğri arasındaki bant, Z boyunca kalınlaştırılmış (kemer, çerçeve).
    inner/outer: aynı sayıda (x, y) nokta."""
    n = len(inner)
    z0, z1 = -depth / 2, depth / 2
    V = []
    for pts in (inner, outer):
        for z in (z0, z1):
            for x, y in pts:
                V.append([x, y, z])
    I0, I1, O0, O1 = 0, n, 2 * n, 3 * n
    F = []
    for i in range(n - 1):
        F += [[O0 + i, I0 + i, I0 + i + 1], [O0 + i, I0 + i + 1, O0 + i + 1]]      # arka yüz
        F += [[O1 + i, I1 + i + 1, I1 + i], [O1 + i, O1 + i + 1, I1 + i + 1]]      # ön yüz
        F += [[O0 + i, O0 + i + 1, O1 + i + 1], [O0 + i, O1 + i + 1, O1 + i]]      # dış kenar
        F += [[I0 + i, I1 + i + 1, I0 + i + 1], [I0 + i, I1 + i, I1 + i + 1]]      # iç kenar
    for e in (0, n - 1):
        F += [[I0 + e, O0 + e, O1 + e], [I0 + e, O1 + e, I1 + e]]
    F = [f[::-1] for f in F]  # yukarıdaki sıra içe bakıyordu; dışa çevir
    m = _mk(V, F, color)
    # Uç kapakları (son 4 üçgen) kemer ayağında aşağı bakmalı.
    tri = m.V[m.F[-4:]]
    nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    for i in range(4):
        if nrm[i, 1] > 0:
            m.F[len(m.F) - 4 + i] = m.F[len(m.F) - 4 + i][::-1]
    return m


def pointed_arch(span, rise, n=8):
    """Osmanlı sivri kemeri: iki daire yayı tepede buluşur. (x, y) noktaları soldan sağa."""
    half = span / 2
    # Sol yayın merkezi sağda (x=c), yarıçap R; tepede (0, rise) noktasından geçer.
    # (-half, 0) ve (0, rise) noktalarından geçen, merkezi y=0 üzerinde olan daire.
    c = (rise * rise - half * half) / (2 * half)
    R = half + c
    pts = []
    a0 = math.pi
    a1 = math.atan2(rise, -c)
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        pts.append((c + R * math.cos(a), R * math.sin(a)))
    right = [(-x, y) for x, y in reversed(pts[:-1])]
    return pts + right


def star_polygon(points=8, r_out=1.0, r_in=0.6, depth=0.1, color="altin") -> Mesh:
    """Düz yıldız (Osmanlı sekiz köşeli yıldız gibi), XY düzleminde, Z kalınlıklı."""
    V = [[0, 0, depth / 2], [0, 0, -depth / 2]]
    ring = []
    for i in range(points * 2):
        a = math.pi / 2 + math.pi * i / points
        r = r_out if i % 2 == 0 else r_in
        ring.append((r * math.cos(a), r * math.sin(a)))
    for x, y in ring:
        V.append([x, y, depth / 2])
        V.append([x, y, -depth / 2])
    F = []
    m = len(ring)
    for i in range(m):
        a, b = 2 + 2 * i, 2 + 2 * ((i + 1) % m)
        F += [[0, a, b], [1, b + 1, a + 1], [a, a + 1, b + 1], [a, b + 1, b]]
    return _mk(V, F, color)


def ring_of(mesh_fn, count, radius, y=0.0, start_deg=0.0):
    """Bir çember üzerine eşit aralıklı kopyalar (sütunlar, boncuklar)."""
    out = []
    for i in range(count):
        a = math.radians(start_deg + 360.0 * i / count)
        out.append(mesh_fn(i).translate(radius * math.cos(a), y, radius * math.sin(a)))
    return out
