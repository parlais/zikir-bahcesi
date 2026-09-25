"""Büyük çarbağ sahnesi (stil karşılaştırması ve ileride ana bahçe).

Çarbağ düzeni: dört kol halinde akan su kanalları ortadaki sekizgen havuzda
buluşur (Muhammed 15: su, süt, bal ve şarap ırmakları). Kuzeyde yükseltilmiş
terasta köşk, güneyde bahçe kapısı; güney, doğu ve batı surlarla çevrili.
Dışarıda hafif tepeli arazi, çok uzakta dağ halkası.

Ölçüler metredir. Bahçe x, z ∈ [-30, 30]; kamera güney kapıdan kuzeye bakar (-z).
Bitki ve fener yerleşimi game/data/sahne_carbag.json dosyasına yazılır;
Godot bunları MultiMesh ile çoğaltır.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from mf.mesh import Mesh, blade, blob, box, cone, cylinder, icosphere, lathe, merge, tube
from mf.palette import renk
from mf.scene import Node

from .agaclar import nar_modeli, selvi_modeli
from . import model

B = 30.0          # bahçe yarı genişliği
KANAL = 0.9       # kanal yarı genişliği
BORDUR = 0.35     # mermer bordür eni
YOL = 2.6         # kanal yanı yol eni
HAVUZ = 5.0       # merkez havuz yarıçapı
SU_Y = -0.14      # su yüzeyi yüksekliği
TERAS_Z0, TERAS_Z1, TERAS_H = -31.0, -46.0, 2.6
SUR_H = 2.6
EKSEN = KANAL + BORDUR + YOL          # eksen bandının yarı genişliği (~3.85)


# --------------------------------------------------------------------------
# Yardımcılar
# --------------------------------------------------------------------------

def _grid(x0, x1, z0, z1, nx, nz, color, yfn=None, material="zemin") -> Mesh:
    """Düz ya da yükseklik fonksiyonlu ızgara (yukarı bakan)."""
    xs = np.linspace(x0, x1, nx + 1)
    zs = np.linspace(z0, z1, nz + 1)
    X, Z = np.meshgrid(xs, zs)
    Y = np.zeros_like(X) if yfn is None else yfn(X, Z)
    V = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
    F = []
    for j in range(nz):
        for i in range(nx):
            a = j * (nx + 1) + i
            b, c, d = a + 1, a + nx + 2, a + nx + 1
            F += [[a, c, b], [a, d, c]]
    F = np.array(F, dtype=np.int64)
    return Mesh(V.astype(np.float32), F, np.tile(np.array(renk(color), np.float32), (len(F), 1)), material)


def _noise2(x, z, seed=0, oct=4):
    rng = np.random.default_rng(seed)
    out = np.zeros_like(x, dtype=np.float64)
    amp, fr = 1.0, 1.0 / 60.0
    for _ in range(oct):
        px, pz, ph = rng.uniform(0, 100, 3)
        out += amp * (np.sin(x * fr + px) * np.cos(z * fr * 1.3 + pz) + 0.5 * np.sin((x + z) * fr * 0.7 + ph))
        amp *= 0.5
        fr *= 2.1
    return out


def _mermer_kutu(w, h, d, y0=0.0, color="mermer"):
    return box(w, h, d, color, y0=y0).with_material("tas")


# --------------------------------------------------------------------------
# Arazi
# --------------------------------------------------------------------------

def arazi_y(x, z):
    """Dış arazi yüksekliği: bahçeden uzaklaştıkça yükselen hafif tepeler."""
    x = np.asarray(x, dtype=np.float64)
    z = np.asarray(z, dtype=np.float64)
    dx = np.maximum(np.abs(x) - B, 0)
    dz = np.maximum(np.abs(z + 8) - (B + 8), 0)
    d = np.sqrt(dx ** 2 + dz ** 2)
    h = _noise2(x, z, 3) * 2.2 + 1.5
    return np.clip(d / 18.0, 0, 1) ** 1.6 * (h + d * 0.06) - 0.02


def _dis_arazi() -> Mesh:
    """Bahçenin dışındaki tepelik arazi; bahçe ve teras bölgesi boş bırakılır."""
    R = 170.0
    n = 136
    xs = np.linspace(-R, R, n + 1)
    X, Z = np.meshgrid(xs, xs)

    Y = arazi_y(X, Z)
    V = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
    F = []
    for j in range(n):
        for i in range(n):
            cx, cz = (xs[i] + xs[i + 1]) / 2, (xs[j] + xs[j + 1]) / 2
            if abs(cx) < B + 0.3 and TERAS_Z1 - 0.3 < cz < B + 0.3:
                continue
            a = j * (n + 1) + i
            b, c, d = a + 1, a + n + 2, a + n + 1
            F += [[a, c, b], [a, d, c]]
    F = np.array(F, dtype=np.int64)
    m = Mesh(V.astype(np.float32), F, np.tile(np.array(renk("cimen"), np.float32), (len(F), 1)), "zemin")
    return m.smooth(60)


def _daglar() -> Mesh:
    """Ufuktaki dağ halkası (sisle maviye çalan uzak katman)."""
    seg, rings = 240, 8
    rng = np.random.default_rng(12)
    ph = rng.uniform(0, 2 * np.pi, 6)
    V, F = [], []
    for r_i in range(rings + 1):
        t = r_i / rings
        for k in range(seg):
            a = 2 * np.pi * k / seg
            prof = (np.sin(a * 3 + ph[0]) * 0.5 + np.sin(a * 7 + ph[1]) * 0.3 + np.sin(a * 13 + ph[2]) * 0.2
                    + np.sin(a * 29 + ph[3]) * 0.08)
            h = (70 + 45 * prof) * math.sin(math.pi * t) ** 0.8 if 0 < t < 1 else -5.0
            # Kuzey (−z) yönünde daha yüksek sıradağ: köşkün ardındaki manzara
            h *= 1.0 + 0.6 * max(0.0, -math.sin(a)) ** 2
            # Sırtlar: yüksek frekanslı keskin tepeler
            h += (abs(math.sin(a * 41 + ph[4])) * 9 + abs(math.sin(a * 83 + ph[5] + t * 3)) * 5) * math.sin(math.pi * t)
            r = 260 + 160 * t
            V.append([r * math.cos(a), h, r * math.sin(a)])
    for r_i in range(rings):
        for k in range(seg):
            a = r_i * seg + k
            b = r_i * seg + (k + 1) % seg
            c, d = b + seg, a + seg
            F += [[a, b, c], [a, c, d]]
    F = np.array(F, dtype=np.int64)
    V = np.array(V, np.float32)
    cy = V[F][:, :, 1].mean(axis=1)
    orman, kaya, kar = (np.array(renk(k), np.float32) for k in ("uzak_orman", "uzak_dag", "kar"))
    t1 = np.clip((cy - 25) / 35, 0, 1)[:, None]
    t2 = np.clip((cy - 88) / 18, 0, 1)[:, None]
    C = orman * (1 - t1) + kaya * t1
    C = C * (1 - t2) + kar * t2
    return Mesh(V, F, C.astype(np.float32), "uzak").smooth(70)


# --------------------------------------------------------------------------
# Bahçe zemini: kanallar, havuz, yollar, çimenlik parterler
# --------------------------------------------------------------------------

def _kanal_parcalari():
    su, dip, kenar = [], [], []
    L = B
    for eksen in ("x", "z"):
        for isaret in (-1, 1):
            # Havuz kenarından bahçe kenarına kadar
            a0, a1 = HAVUZ - 0.3, L - 1.2 if not (eksen == "z" and isaret < 0) else L + 0.2
            uz = a1 - a0
            orta = isaret * (a0 + uz / 2)
            if eksen == "z":
                su.append(box(2 * KANAL, 0.02, uz, "su", y0=SU_Y - 0.02).translate(0, 0, orta))
                dip.append(box(2 * KANAL, 0.1, uz, "cini_firuze", y0=-0.62).translate(0, 0, orta))
                for s in (-1, 1):
                    kenar.append(_mermer_kutu(BORDUR, 0.74, uz, y0=-0.62).translate(s * (KANAL + BORDUR / 2), 0, orta))
            else:
                su.append(box(uz, 0.02, 2 * KANAL, "su", y0=SU_Y - 0.02).translate(orta, 0, 0))
                dip.append(box(uz, 0.1, 2 * KANAL, "cini_firuze", y0=-0.62).translate(orta, 0, 0))
                for s in (-1, 1):
                    kenar.append(_mermer_kutu(uz, 0.74, BORDUR, y0=-0.62).translate(orta, 0, s * (KANAL + BORDUR / 2)))
    return su, dip, kenar


def _havuz():
    seg = 8
    su = lathe([(HAVUZ - 0.02, SU_Y - 0.02), (HAVUZ - 0.02, SU_Y), (0.0, SU_Y)], seg, "su", start_deg=22.5)
    dip = lathe([(HAVUZ, -0.72), (0.0, -0.72)], seg, "cini_firuze", start_deg=22.5).flipped()
    dip = merge(dip, cylinder(HAVUZ, HAVUZ, 0.1, seg, "cini_firuze", y0=-0.72).rotate("y", 22.5))
    kenar = lathe([(HAVUZ, -0.7), (HAVUZ, 0.16), (HAVUZ + 0.55, 0.16), (HAVUZ + 0.55, -0.02),
                   (HAVUZ + 0.7, -0.02), (HAVUZ + 0.7, -0.1)], seg, "mermer", start_deg=22.5, cap=False)
    return su.with_material("su"), dip.with_material("cini"), kenar.flipped().with_material("tas")


def _yollar_ve_parterler():
    """Eksen bantlarında taş yollar; dört çeyrekte çimenlik parter ve iç yollar."""
    yollar, cimen = [], []
    # Ana eksen yolları (kanal kenarında)
    for s in (-1, 1):
        x = s * (KANAL + BORDUR + YOL / 2)
        for z0, z1 in ((HAVUZ + 0.7, B), (-B, -(HAVUZ + 0.7))):
            yollar.append(box(YOL, 0.1, z1 - z0, "tas_yol", y0=-0.1).translate(x, 0, (z0 + z1) / 2))
            yollar.append(box(z1 - z0, 0.1, YOL, "tas_yol", y0=-0.1).translate((z0 + z1) / 2, 0, x))
    # Havuz çevresi meydan
    yollar.append(lathe([(HAVUZ + EKSEN + 1.2, -0.1), (HAVUZ + EKSEN + 1.2, 0.0), (0.0, 0.0)],
                        8, "tas_yol", start_deg=22.5))
    # Çeyreklerde çevre yolu ve parter çimeni
    ic0 = EKSEN
    kenar_yol = 1.8
    for sx in (-1, 1):
        for sz in (-1, 1):
            x0, x1 = ic0, B
            z0, z1 = ic0, B
            cx, cz = sx * (x0 + x1) / 2, sz * (z0 + z1) / 2
            w = x1 - x0
            # Dış çevre yolu (sura bitişik)
            yollar.append(box(w, 0.1, kenar_yol, "tas_yol", y0=-0.1).translate(cx, 0, sz * (B - kenar_yol / 2)))
            yollar.append(box(kenar_yol, 0.1, w, "tas_yol", y0=-0.1).translate(sx * (B - kenar_yol / 2), 0, cz))
            # Çeyreğin ortasından geçen ince çapraz yollar (küçük çarbağ)
            yollar.append(box(w - kenar_yol, 0.1, 1.2, "tas_yol", y0=-0.09).translate(cx - sx * kenar_yol / 2, 0, cz))
            yollar.append(box(1.2, 0.1, w - kenar_yol, "tas_yol", y0=-0.09).translate(cx, 0, cz - sz * kenar_yol / 2))
            # Çimen parter (yolların hemen üstünde değil; hafif kabarık)
            gx0, gx1 = sorted((sx * x0, sx * (B - kenar_yol)))
            gz0, gz1 = sorted((sz * z0, sz * (B - kenar_yol)))
            cimen.append(_grid(gx0, gx1, gz0, gz1, 14, 14, "cimen", yfn=lambda X, Z: 0.02 + 0 * X))
    return merge(*yollar).with_material("tas"), merge(*cimen)


def _teras():
    """Kuzeyde yükseltilmiş teras, ortada geniş merdiven, korkuluk."""
    w = 2 * B
    d = TERAS_Z0 - TERAS_Z1
    zc = (TERAS_Z0 + TERAS_Z1) / 2
    tas = [
        box(w, TERAS_H, d, "tas", y0=-0.1).translate(0, 0, zc),
        box(w + 0.4, 0.25, 0.5, "tas_koyu", y0=TERAS_H - 0.1).translate(0, 0, TERAS_Z0 + 0.1),
    ]
    # Merdiven: 10 basamak
    n = 10
    for i in range(n):
        h = TERAS_H * (i + 1) / n
        tas.append(box(9.0, h, 0.42, "mermer", y0=-0.1).translate(0, 0, TERAS_Z0 + 0.42 * (n - i) - 0.2))
    # Korkuluk (merdiven boşluğu hariç)
    for s in (-1, 1):
        x0, x1 = 4.8, B
        tas.append(box(x1 - x0, 0.9, 0.3, "mermer", y0=TERAS_H - 0.1).translate(s * (x0 + x1) / 2, 0, TERAS_Z0 + 0.2))
        for k in range(12):
            x = x0 + (x1 - x0) * (k + 0.5) / 12
            tas.append(box(0.36, 1.1, 0.36, "mermer", y0=TERAS_H - 0.1).translate(s * x, 0, TERAS_Z0 + 0.2))
    ust = _grid(-B, B, TERAS_Z1, TERAS_Z0, 20, 6, "cimen", yfn=lambda X, Z: TERAS_H - 0.08 + 0 * X)
    yol = box(10.0, 0.1, d - 0.6, "tas_yol", y0=TERAS_H - 0.09).translate(0, 0, zc - 0.3)
    cini = box(w - 0.2, 0.35, 0.05, "cini_lacivert", y0=TERAS_H - 0.7).translate(0, 0, TERAS_Z0 + 0.02)
    return merge(*tas, yol).with_material("tas"), ust, cini.with_material("cini")


def _surlar():
    """Güney, doğu ve batı surları; güneyde kapı boşluğu. Üstte kiremit bandı ve çini kuşak."""
    t = 0.7
    parca, cini = [], []
    kapı_yari = 2.9
    kenarlar = [
        ((-B - t / 2, kapı_yari - 0.0), B + t / 2, "x"),   # güney sol
    ]
    segs = []
    # Güney (z = +B): iki parça
    segs.append((-B - t, -kapı_yari, B + t / 2, "x"))
    segs.append((kapı_yari, B + t, B + t / 2, "x"))
    # Doğu ve batı (x = ±B): terasın sonuna kadar
    for s in (-1, 1):
        segs.append((TERAS_Z1, B + t, s * (B + t / 2), "z"))
    for a0, a1, sabit, eksen in segs:
        L = a1 - a0
        c = (a0 + a1) / 2
        govde = box(L, SUR_H, t, "tas", y0=-0.1)
        ust = box(L, 0.22, t + 0.25, "tas_koyu", y0=SUR_H - 0.1)
        bant = box(L, 0.3, t + 0.04, "cini_firuze", y0=SUR_H - 0.55)
        if eksen == "x":
            parca += [govde.translate(c, 0, sabit), ust.translate(c, 0, sabit)]
            cini.append(bant.translate(c, 0, sabit))
        else:
            parca += [govde.rotate("y", 90).translate(sabit, 0, c), ust.rotate("y", 90).translate(sabit, 0, c)]
            cini.append(bant.rotate("y", 90).translate(sabit, 0, c))
        # Ayak kuleleri (her 10 m)
        k = int(L // 10)
        for i in range(k + 1):
            u = a0 + L * i / max(k, 1)
            p = (u, sabit) if eksen == "x" else (sabit, u)
            parca.append(box(t + 0.5, SUR_H + 0.5, t + 0.5, "tas", y0=-0.1).translate(p[0], 0, p[1]))
            parca.append(cone(0.55, 0.7, 8, "kursun_renk", y0=SUR_H + 0.4).translate(p[0], 0, p[1]))
    return merge(*parca).with_material("tas"), merge(*cini).with_material("cini")


@model("ZB_sahne_carbag")
def carbag() -> Node:
    root = Node("ZB_sahne_carbag")
    su, dip, kenar = _kanal_parcalari()
    hsu, hdip, hkenar = _havuz()
    yollar, cimen = _yollar_ve_parterler()
    teras_tas, teras_ust, teras_cini = _teras()
    sur, sur_cini = _surlar()
    root.add(
        Node("zemin_dis", [_dis_arazi()]),
        Node("zemin_bahce", [cimen, teras_ust]),
        Node("tas", [yollar, merge(*kenar).with_material("tas"), hkenar, teras_tas, sur]),
        Node("cini", [merge(*dip).with_material("cini"), hdip, teras_cini, sur_cini]),
        Node("su", [merge(*su).with_material("su"), hsu]),
    )
    return root


@model("ZB_sahne_daglar")
def daglar() -> Node:
    return Node("ZB_sahne_daglar", [_daglar()])


# --------------------------------------------------------------------------
# Bitkiler (MultiMesh için tek düğüm, tek mesh)
# --------------------------------------------------------------------------

def _yaprak_bulutu(merkez, r, n, seed, renkler, boy=0.16):
    """Bir küre yüzeyine dışa bakan küçük yapraklar: dolgun, tüylü taç."""
    rng = np.random.default_rng(seed)
    parcalar = []
    for i in range(n):
        v = rng.normal(0, 1, 3)
        v /= np.linalg.norm(v)
        if v[1] < -0.55:
            v[1] = -v[1] * 0.4
            v /= np.linalg.norm(v)
        p = np.asarray(merkez) + v * r * rng.uniform(0.82, 1.05)
        yan = np.cross(v, [0, 1, 0])
        if np.linalg.norm(yan) < 1e-3:
            yan = np.array([1.0, 0, 0])
        yan /= np.linalg.norm(yan)
        yon = v * 0.6 + np.array([0, 0.5, 0]) + rng.normal(0, 0.25, 3)
        yon /= np.linalg.norm(yon)
        L = boy * rng.uniform(0.8, 1.25)
        yol = [p - yon * L * 0.1, p + yon * L * 0.5, p + yon * L]
        parcalar.append(blade(yol, [0.01, L * 0.32, 0.004], renkler[i % len(renkler)], fold=0.25, side=yan))
    return parcalar


@model("ZB_bitki_selvi")
def selvi() -> Node:
    """Servi/selvi: alev biçimli, dimdik (vahdet sembolü). Kanal boylarında sıra halinde."""
    return selvi_modeli("ZB_bitki_selvi")


@model("ZB_bitki_nar")
def nar_agaci() -> Node:
    """Nar ağacı (Rahmân 68): dipten çatallanan gövdeler, sık yuvarlak taç, sarkan narlar."""
    return nar_modeli("ZB_bitki_nar")


@model("ZB_bitki_gul_cali")
def gul_cali() -> Node:
    """Gül çalısı: dolgun yeşil küme, üzerinde açmış güller (salavat)."""
    rng = np.random.default_rng(31)
    kutle = [blob(0.42, "yaprak_koyu", seed=5, subdiv=2, squash=0.8, jitter=0.1).translate(0, 0.42, 0),
             blob(0.3, "yaprak_koyu", seed=6, subdiv=2, squash=0.8, jitter=0.1).translate(0.3, 0.35, 0.15),
             blob(0.3, "yaprak_koyu", seed=7, subdiv=2, squash=0.8, jitter=0.1).translate(-0.28, 0.33, -0.1)]
    yapraklar = []
    for i, c in enumerate([(0, 0.42, 0), (0.3, 0.35, 0.15), (-0.28, 0.33, -0.1)]):
        yapraklar += _yaprak_bulutu(c, 0.38 if i == 0 else 0.28, 45, 90 + i, ["yaprak_koyu", "yaprak"], boy=0.11)
    guller = []
    for i in range(9):
        v = rng.normal(0, 1, 3)
        v[1] = abs(v[1]) + 0.5
        v /= np.linalg.norm(v)
        p = np.array([0, 0.4, 0]) + v * np.array([0.5, 0.42, 0.45])
        g = merge(
            lathe([(0.0, 0.0), (0.05, 0.02), (0.075, 0.06), (0.07, 0.085)], 7, "gul", cap=False).flipped(),
            lathe([(0.0, 0.0), (0.05, 0.02), (0.075, 0.06), (0.07, 0.085)], 7, "gul_koyu", cap=False),
            icosphere(0.045, 1, "gul_koyu").scale(1, 0.8, 1).translate(0, 0.05, 0),
        ).smooth(60)
        guller.append(g.rotate("x", rng.uniform(-25, 25)).rotate("y", rng.uniform(0, 360)).translate(*p))
    yaprak = merge(*kutle, *yapraklar).with_material("yaprak").weight(lambda V: np.clip(V[:, 1] / 0.8, 0, 1))
    yaprak = yaprak.kure_normal((0.0, 0.25, 0.0), (1.0, 0.8, 1.0))
    return Node("ZB_bitki_gul_cali", [yaprak, merge(*guller).with_material("cicek")])


@model("ZB_bitki_simsir")
def simsir() -> Node:
    """Şimşir çit parçası (2 m): parterleri çevreleyen alçak, budanmış yeşil bordür."""
    parcalar = []
    for k in range(5):
        parcalar.append(blob(0.34, "yaprak_koyu", seed=200 + k, subdiv=2, squash=0.9, jitter=0.08)
                        .scale(1.2, 1.0, 1.0).translate(-0.8 + 0.4 * k, 0.33, 0))
    yapraklar = []
    for k in range(5):
        yapraklar += _yaprak_bulutu((-0.8 + 0.4 * k, 0.33, 0), 0.34, 26, 300 + k, ["yaprak_koyu", "yaprak"], boy=0.09)
    m = merge(*parcalar, *yapraklar).with_material("yaprak").weight(lambda V: np.clip(V[:, 1] / 0.7, 0, 1) * 0.3)
    return Node("ZB_bitki_simsir", [m.kure_normal((0.0, 0.1, 0.0), (3.0, 1.0, 1.0))])


@model("ZB_bitki_cimen")
def cimen_tutami() -> Node:
    """Çimen tutamı: 7 ince yaprak. Godot'da on binlerce kopya, rüzgârla dalgalanır."""
    rng = np.random.default_rng(41)
    yapraklar = []
    for i in range(7):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(0.0, 0.08)
        base = np.array([r * math.cos(a), 0.0, r * math.sin(a)])
        h = rng.uniform(0.22, 0.4)
        egim = np.array([math.cos(a), 0, math.sin(a)]) * rng.uniform(0.05, 0.14)
        yol = [base, base + egim * 0.3 + [0, h * 0.5, 0], base + egim + [0, h, 0]]
        yapraklar.append(blade(yol, [0.016, 0.011, 0.001], "cimen", fold=0.2,
                               side=[-math.sin(a), 0, math.cos(a)]))
    m = merge(*yapraklar).with_material("cimen_ot").weight(lambda V: np.clip(V[:, 1] / 0.4, 0, 1))
    return Node("ZB_bitki_cimen", [m])


@model("ZB_bitki_lale_tarhi")
def lale_tarhi() -> Node:
    """Tek lale (açmış), yumuşak gölgeli ve daha ayrıntılı; tarhlarda çoğaltılır."""
    boy = 0.55
    sap = tube([[0, 0.0, 0], [0.012, boy * 0.5, 0.0], [0.0, boy, 0.0]], [0.011, 0.009, 0.008], 6, "yaprak_koyu").smooth(60)
    yap = []
    for aci, b in ((20, 0.34), (200, 0.3), (110, 0.22)):
        a = math.radians(aci)
        d = np.array([math.cos(a), 0.0, math.sin(a)])
        yol = [d * 0.01 + [0, 0.02, 0], d * 0.06 + [0, b * 0.4, 0], d * 0.11 + [0, b * 0.75, 0], d * 0.17 + [0, b, 0]]
        yap.append(blade(yol, [0.035, 0.045, 0.03, 0.003], "yaprak", fold=0.5, side=np.cross(d, [0, 1, 0])))
    tac = []
    for i in range(6):
        a = math.radians(60 * i + (30 if i % 2 else 0))
        d = np.array([math.cos(a), 0.0, math.sin(a)])
        t = np.array([-math.sin(a), 0.0, math.cos(a)])
        acil = 0.85 if i % 2 == 0 else 0.5
        ty = boy - 0.01
        yol = [d * 0.015 + [0, ty, 0], d * (0.035 + 0.03 * acil) + [0, ty + 0.05, 0],
               d * (0.04 + 0.05 * acil) + [0, ty + 0.1, 0], d * (0.03 + 0.09 * acil) + [0, ty + 0.15, 0]]
        tac.append(blade(yol, [0.016, 0.042, 0.034, 0.002], "lale" if i % 2 == 0 else "lale_koyu", fold=0.4, side=t))
    tac.append(cylinder(0.013, 0.017, 0.035, 6, "lale_sari", y0=boy - 0.01))
    yesil = merge(sap, *yap).with_material("yaprak").weight(lambda V: np.clip(V[:, 1] / boy, 0, 1))
    cicek = merge(*tac).smooth(55).with_material("cicek").weight(lambda V: np.ones(len(V)))
    return Node("ZB_bitki_lale_tarhi", [yesil, cicek])


# --------------------------------------------------------------------------
# Yerleşim (JSON): Godot bu listeleri MultiMesh ve sahne örnekleriyle kurar
# --------------------------------------------------------------------------

def yerlesim() -> dict:
    rng = np.random.default_rng(7)
    d: dict = {"bahce_yari": B, "su_y": SU_Y, "teras": [TERAS_Z0, TERAS_Z1, TERAS_H], "eksen": EKSEN}
    # Selviler: ana eksen boyunca iki sıra
    selvi = []
    for s in (-1, 1):
        for z in list(np.arange(HAVUZ + 5, B - 1, 3.6)) + list(-np.arange(HAVUZ + 5, B - 1, 3.6)):
            selvi.append([s * (EKSEN + 0.9), 0.0, float(z), float(rng.uniform(0, 360)), float(rng.uniform(0.9, 1.1))])
        for x in np.arange(-B + 3, B - 2, 5.0):  # teras üstünde arka sıra
            selvi.append([float(x) * 1.0, TERAS_H, TERAS_Z1 + 2.0, float(rng.uniform(0, 360)), float(rng.uniform(1.0, 1.25))])
    d["selvi"] = selvi
    # Nar ağaçları: çeyreklerde 2x2
    nar = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            for u in (0.28, 0.72):
                for v in (0.28, 0.72):
                    x = sx * (EKSEN + (B - 1.8 - EKSEN) * u)
                    z = sz * (EKSEN + (B - 1.8 - EKSEN) * v)
                    nar.append([float(x), 0.02, float(z), float(rng.uniform(0, 360)), float(rng.uniform(0.9, 1.15))])
    d["nar"] = nar
    # Şimşir çitler: parterlerin iç kenarları boyunca
    simsir = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            x0, x1 = EKSEN + 0.35, B - 1.8 - 0.35
            for u in np.arange(x0 + 1.0, x1, 2.0):
                simsir.append([float(sx * u), 0.02, float(sz * (EKSEN + 0.35)), 0.0, 1.0])
                simsir.append([float(sx * (EKSEN + 0.35)), 0.02, float(sz * u), 90.0, 1.0])
    d["simsir"] = simsir
    # Gül çalıları ve lale tarhları: havuz çevresi ve eksen boyu
    gul = []
    for k in range(16):
        a = 2 * math.pi * (k + 0.5) / 16
        r = HAVUZ + EKSEN + 2.2
        if min(abs(math.cos(a)), abs(math.sin(a))) < 0.22:
            continue
        gul.append([r * math.cos(a), 0.0, r * math.sin(a), float(rng.uniform(0, 360)), float(rng.uniform(0.9, 1.2))])
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx = sx * (EKSEN + (B - 1.8 - EKSEN) * 0.5)
            cz = sz * (EKSEN + (B - 1.8 - EKSEN) * 0.5)
            for k in range(8):
                a = 2 * math.pi * k / 8
                gul.append([cx + 1.9 * math.cos(a), 0.02, cz + 1.9 * math.sin(a), float(rng.uniform(0, 360)), 1.0])
    d["gul"] = gul
    lale = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            for z in np.arange(EKSEN + 1.2, B - 2.4, 0.42):
                for k in range(4):
                    x = EKSEN + 1.3 + k * 0.4
                    lale.append([float(sx * x + rng.normal(0, 0.05)), 0.02, float(sz * z + rng.normal(0, 0.05)),
                                 float(rng.uniform(0, 360)), float(rng.uniform(0.85, 1.15))])
    d["lale"] = lale
    # Kandiller: ana yol boyunca
    kandil = []
    for s in (-1, 1):
        for z in (9.0, 16.0, 23.0, -9.0, -16.0, -23.0):
            kandil.append([s * (EKSEN - 0.2), 0.0, z, 90.0 if s > 0 else -90.0, 1.6])
    d["kandil"] = kandil
    # Çimen alanları (dikdörtgenler): Godot bunları rastgele doldurur
    alanlar = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            gx0, gx1 = sorted((sx * EKSEN, sx * (B - 1.8)))
            gz0, gz1 = sorted((sz * EKSEN, sz * (B - 1.8)))
            alanlar.append([gx0, gz0, gx1, gz1, 0.02])
    alanlar.append([-B, TERAS_Z1, -5.0, TERAS_Z0 - 0.4, TERAS_H - 0.08])
    alanlar.append([5.0, TERAS_Z1, B, TERAS_Z0 - 0.4, TERAS_H - 0.08])
    d["cimen_alanlari"] = alanlar
    # İç yolların çimen tutamı konmayacak şeritleri (çeyrek ortası çapraz yollar)
    serit = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx = sx * (EKSEN + B) / 2 - sx * 0.9
            cz = sz * (EKSEN + B) / 2 - sz * 0.9
            serit.append([cx - 0.75, -B, cx + 0.75, B])
            serit.append([-B, cz - 0.75, B, cz + 0.75])
    d["cimensiz"] = serit
    # Bahçe dışı koruluk: surların ötesinde selvi ve nar kümeleri (köşkün ardındaki manzara açık)
    dis = []
    rng2 = np.random.default_rng(99)
    while len(dis) < 170:
        a = rng2.uniform(0, 2 * math.pi)
        r = rng2.uniform(38, 125)
        x, z = r * math.cos(a), r * math.sin(a) - 8
        if abs(x) < B + 5 and TERAS_Z1 - 5 < z < B + 5:
            continue
        if abs(x) < 16 and z < TERAS_Z1:          # köşkün arkasındaki görüş koridoru
            continue
        if abs(x) < 7 and z > B:                   # kapı önündeki yol
            continue
        tur = "selvi" if rng2.uniform() < 0.55 else "nar"
        dis.append([tur, float(x), float(arazi_y(x, z)) - 0.05, float(z), float(rng2.uniform(0, 360)),
                    float(rng2.uniform(0.9, 1.5))])
    d["dis_agac"] = dis
    d["yapilar"] = {
        "sadirvan": [0.0, 0.0, 0.0, 22.5, 2.2],
        "kosk": [0.0, TERAS_H - 0.1, -39.0, 0.0, 3.8],
        "bahce_kapisi": [0.0, -0.1, B + 0.35, 0.0, 2.1],
    }
    return d


def yerlesim_yaz(root: Path) -> Path:
    p = root / "game" / "data" / "sahne_carbag.json"
    p.write_text(json.dumps(yerlesim(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return p
