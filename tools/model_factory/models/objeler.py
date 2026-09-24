"""E bölümü: küçük objeler (stil testi seti).

Ölçüler gerçek boyuta yakındır (metre); oyunda koleksiyon objeleri gerekirse
büyütülerek gösterilir. Hiçbir objede Allah lafzı veya esma yazısı yoktur
(asset listesi sınırları).
"""
from __future__ import annotations

import math

import numpy as np

from mf.mesh import (blade, blob, box, cone, cylinder, icosphere, lathe, merge, star_polygon, tube)
from mf.scene import Node

from . import model
from .ortak import cevre_noktalari, taban_levha, toprak_tumsek


# --------------------------------------------------------------------------
@model("ZB_obje_kandil")
def kandil() -> Node:
    """Direğe asılı Osmanlı cami kandili. Cam gövde, içinde nur."""
    root = Node("ZB_obje_kandil")
    direk = merge(
        taban_levha(0.14, 0.05),
        cylinder(0.05, 0.04, 0.08, 8, "demir", y0=0.05),
        cylinder(0.022, 0.018, 1.25, 6, "demir", y0=0.1),
        tube([[0, 1.3, 0], [0.12, 1.36, 0], [0.3, 1.36, 0], [0.36, 1.32, 0]], [0.018, 0.016, 0.015, 0.014], 5, "demir"),
        icosphere(0.03, 0, "altin").translate(0, 1.37, 0),
    ).with_material("metal")
    root.add(direk)

    lamba = Node("kandil", translation=(0.36, 0.78, 0.0))
    govde_profil = [(0.0, 0.0), (0.05, 0.012), (0.1, 0.05), (0.125, 0.1), (0.11, 0.16),
                    (0.085, 0.2), (0.1, 0.25), (0.13, 0.3)]
    cam = lathe(govde_profil, seg=10, color="cam").with_material("cam")
    halka = merge(
        cylinder(0.135, 0.135, 0.02, 10, "altin", y0=0.295),
        cylinder(0.02, 0.0, 0.04, 6, "altin", y0=-0.035),
        cylinder(0.105, 0.105, 0.012, 10, "altin", y0=0.1),
    ).with_material("metal")
    zincirler = merge(*[
        tube([[x, 0.31, z], [0.0, 0.5, 0.0]], [0.006, 0.006], 4, "altin", cap=False)
        for x, _, z in cevre_noktalari(3, 0.12, start_deg=90)
    ], tube([[0, 0.5, 0], [0, 0.54, 0]], [0.008, 0.008], 4, "altin")).with_material("metal")
    alev = merge(
        icosphere(0.045, 1, "nur").scale(1, 1.5, 1).translate(0, 0.13, 0),
        cylinder(0.03, 0.03, 0.04, 6, "altin", y0=0.05),
    )
    lamba.add(cam, halka, zincirler, alev.with_material("nur"))
    lamba.add(Node("isik_kandil", translation=(0.0, 0.14, 0.0)))
    root.add(lamba)
    return root


# --------------------------------------------------------------------------
@model("ZB_obje_fener")
def fener() -> Node:
    """Altıgen bahçe feneri ve üstünde süzülen kutup yıldızı (Nahl 16)."""
    root = Node("ZB_obje_fener")
    kasa = merge(
        cylinder(0.13, 0.12, 0.04, 6, "demir"),
        cylinder(0.1, 0.1, 0.02, 6, "demir", y0=0.04),
        *[cylinder(0.01, 0.01, 0.26, 4, "demir", y0=0.06).translate(x, 0, z)
          for x, _, z in cevre_noktalari(6, 0.095)],
        cylinder(0.115, 0.115, 0.025, 6, "demir", y0=0.32),
        cone(0.15, 0.13, 6, "demir", y0=0.345),
        tube([[0, 0.47, 0], [0, 0.53, 0.0]], [0.012, 0.012], 4, "demir"),
        tube([[0, 0.53, -0.04], [0, 0.57, 0], [0, 0.53, 0.04]], [0.008, 0.008, 0.008], 4, "demir", cap=False),
    ).with_material("metal")
    cam = cylinder(0.092, 0.092, 0.26, 6, "cam", y0=0.06).with_material("cam")
    alev = merge(
        cylinder(0.025, 0.02, 0.06, 6, "fildisi", y0=0.06),
        icosphere(0.03, 1, "nur").scale(1, 1.6, 1).translate(0, 0.16, 0),
    ).with_material("nur")
    root.add(kasa, cam, alev, Node("isik_fener", translation=(0.0, 0.18, 0.0)))
    yildiz = Node("yildiz", translation=(0.0, 0.78, 0.0))
    yildiz.add(star_polygon(8, 0.09, 0.05, 0.025, "nur").with_material("nur"))
    root.add(yildiz)
    return root


# --------------------------------------------------------------------------
@model("ZB_obje_rahle")
def rahle() -> Node:
    """Çapraz geçmeli rahle ve üzerinde açık kitap."""
    root = Node("ZB_obje_rahle")
    aci = 40.0
    L, W, T = 0.56, 0.3, 0.024
    parcalar = []
    for yon in (1, -1):
        tahta = box(W, L, T, "ahsap", y0=-L / 2)
        # Kitap yarısı: tahtanın üst yarısında, V'nin iç tarafında
        sayfa = box(W * 0.8, 0.2, 0.02, "kitap_sayfa", y0=0.04).translate(0, 0, -yon * (T / 2 + 0.01))
        cilt = box(W * 0.86, 0.22, 0.008, "kitap_cilt", y0=0.03).translate(0, 0, -yon * (T / 2 + 0.002))
        for m in (tahta, cilt, sayfa):
            parcalar.append(m.rotate("x", yon * aci).translate(0, L / 2 * math.cos(math.radians(aci)), 0))
    # Kitabın ortasındaki kurdele
    parcalar.append(box(0.015, 0.16, 0.004, "altin", y0=0.0).rotate("x", 90).translate(0, 0.28, 0.0))
    root.add(merge(*parcalar).shade_vary(0.03, 3))
    return root


# --------------------------------------------------------------------------
@model("ZB_obje_define_sandigi")
def define_sandigi() -> Node:
    """Altın kuşaklı define sandığı; kapak ayrı düğüm (arkadan menteşeli)."""
    root = Node("ZB_obje_define_sandigi")
    W, H, D = 0.6, 0.3, 0.4
    govde = merge(
        box(W, H, D, "ahsap"),
        box(W + 0.02, 0.03, D + 0.02, "ahsap_koyu"),
        *[box(0.04, H - 0.02, D + 0.016, "altin", y0=0.01).translate(x, 0, 0) for x in (-0.2, 0.2)],
        box(0.08, 0.1, 0.02, "altin", y0=0.17).translate(0, 0, D / 2 + 0.005),
        box(0.03, 0.04, 0.01, "bos", y0=0.19).translate(0, 0, D / 2 + 0.016),
    ).shade_vary(0.04, 1)
    root.add(govde)
    kapak = Node("kapak", translation=(0.0, H, -D / 2))
    kapak.add(merge(
        box(W + 0.02, 0.07, D + 0.02, "ahsap"),
        box(W - 0.04, 0.06, D * 0.7, "ahsap_koyu", y0=0.07),
        *[box(0.04, 0.1, D + 0.03, "altin", y0=0.0).translate(x, 0, 0) for x in (-0.2, 0.2)],
    ).translate(0, 0, D / 2).shade_vary(0.04, 2))
    root.add(kapak)
    return root


# --------------------------------------------------------------------------
@model("ZB_obje_inci")
def inci() -> Node:
    """Kadife minder üzerinde inci (Rahmân 22)."""
    root = Node("ZB_obje_inci")
    minder = merge(
        blob(0.13, "kumas_kirmizi", seed=4, subdiv=1, squash=0.32, jitter=0.08).translate(0, 0.04, 0),
        *[icosphere(0.015, 0, "altin").translate(x, 0.035, z) for x, _, z in cevre_noktalari(4, 0.115, start_deg=45)],
    )
    tane = icosphere(0.055, 2, "inci").translate(0, 0.125, 0).with_material("inci")
    root.add(minder, tane)
    return root


# --------------------------------------------------------------------------
def _mercan_dal(rng, p, d, uzunluk, r, derinlik, out):
    n = 4
    pts, rads = [p], [r]
    for i in range(1, n):
        d = d + rng.normal(0, 0.18, 3)
        d[1] = abs(d[1]) + 0.25
        d = d / np.linalg.norm(d)
        pts.append(pts[-1] + d * uzunluk / (n - 1))
        rads.append(r * (1 - 0.18 * i))
    out.append(tube(pts, rads, 5, "mercan"))
    out.append(icosphere(rads[-1] * 1.1, 0, "mercan").translate(*pts[-1]))
    if derinlik > 0:
        for _ in range(2 if derinlik > 1 else rng.integers(1, 3)):
            yon = d + rng.normal(0, 0.55, 3)
            _mercan_dal(rng, pts[-1], yon, uzunluk * 0.72, rads[-1] * 0.95, derinlik - 1, out)


@model("ZB_obje_mercan")
def mercan() -> Node:
    root = Node("ZB_obje_mercan")
    rng = np.random.default_rng(22)
    dallar = []
    for yon in ([0.2, 1, 0], [-0.5, 1, 0.3], [0.1, 1, -0.5]):
        _mercan_dal(rng, np.array([0.0, 0.05, 0.0]), np.array(yon, float), 0.16, 0.022, 2, dallar)
    kaya = blob(0.12, "kaya", seed=5, subdiv=1, squash=0.45, jitter=0.2).translate(0, 0.03, 0)
    root.add(kaya, merge(*dallar).shade_vary(0.05, 6))
    return root


# --------------------------------------------------------------------------
def _kabuk(seed):
    profil = [(0.0, 0.0), (0.06, 0.012), (0.11, 0.03), (0.145, 0.055), (0.155, 0.07)]
    dis = lathe(profil, seg=12, color="sedef_dis", cap=False).scale(1, 1, 0.78).jitter(0.005, seed).shade_vary(0.08, seed)
    ic = lathe(profil, seg=12, color="sedef", cap=False).scale(0.94, 1, 0.74).translate(0, 0.007, 0).flipped()
    return dis, ic


@model("ZB_obje_sedef")
def sedef() -> Node:
    """Aralık istiridye kabuğu; içi sedef rengi (Ya Vâcid: açınca bulursun)."""
    root = Node("ZB_obje_sedef")
    alt_dis, alt_ic = _kabuk(8)
    root.add(alt_dis, alt_ic.with_material("inci"))
    ust = Node("ust_kabuk", translation=(0.0, 0.07, -0.115), rotation_deg=(-150.0, 0.0, 0.0))
    ust_dis, ust_ic = _kabuk(9)
    ust.add(ust_dis.translate(0, 0, 0.11), ust_ic.translate(0, 0, 0.11).with_material("inci"))
    root.add(ust)
    return root


# --------------------------------------------------------------------------
@model("ZB_obje_hediye_bohcasi")
def hediye_bohcasi() -> Node:
    """Köşeleri tepede bağlanmış hediye bohçası (yalnız arkadaşa gönderilir)."""
    root = Node("ZB_obje_hediye_bohcasi")
    govde = blob(0.17, "kumas_kirmizi", seed=11, subdiv=1, squash=0.62, jitter=0.07).translate(0, 0.105, 0)
    kulaklar = []
    for i, (x, _, z) in enumerate(cevre_noktalari(4, 1.0, start_deg=45)):
        yol = [[0, 0.2, 0], [x * 0.05, 0.27, z * 0.05], [x * 0.1, 0.3, z * 0.1]]
        kulaklar.append(blade(yol, [0.05, 0.045, 0.005], "kumas_kirmizi", fold=0.4))
    dugum = icosphere(0.035, 1, "kumas_kirmizi").scale(1, 0.8, 1).translate(0, 0.21, 0)
    serit = tube([[math.cos(a) * 0.045, 0.205, math.sin(a) * 0.045]
                  for a in np.linspace(0, 2 * math.pi, 9)], [0.012] * 9, 4, "altin", cap=False)
    desen = [icosphere(0.012, 0, "altin").translate(x, 0.1, z) for x, _, z in cevre_noktalari(6, 0.17)]
    root.add(merge(govde, *kulaklar, dugum, serit, *desen).shade_vary(0.03, 12))
    return root


# --------------------------------------------------------------------------
@model("ZB_obje_ipek_kozasi")
def ipek_kozasi() -> Node:
    """Dut dalında asılı ipek kozası; kelebek bu kozadan çıkar."""
    root = Node("ZB_obje_ipek_kozasi")
    dal = merge(
        toprak_tumsek(0.12, 0.04, seed=2),
        tube([[0, 0, 0], [0.01, 0.2, 0], [-0.02, 0.4, 0.01]], [0.018, 0.014, 0.01], 5, "govde"),
        tube([[0.0, 0.3, 0.0], [0.1, 0.36, 0.02], [0.2, 0.37, 0.02]], [0.011, 0.008, 0.005], 5, "govde"),
    )
    yapraklar = merge(*[
        blade([[x, y, z], [x + dx * 0.5, y + 0.02, z + dz * 0.5], [x + dx, y - 0.01, z + dz]],
              [0.012, 0.04, 0.005], "yaprak", fold=0.3)
        for (x, y, z, dx, dz) in [(-0.02, 0.4, 0.01, -0.08, 0.05), (-0.02, 0.4, 0.01, 0.04, -0.08),
                                   (0.2, 0.37, 0.02, 0.09, 0.03)]
    ]).shade_vary(0.05, 3)
    koza = Node("koza", translation=(0.14, 0.36, 0.02))
    koza.add(merge(
        tube([[0, 0, 0], [0, -0.03, 0]], [0.003, 0.003], 3, "ipek"),
        icosphere(0.05, 1, "ipek").scale(0.85, 1.55, 0.85).jitter(0.004, 5).translate(0, -0.1, 0),
    ).shade_vary(0.05, 4))
    root.add(dal, yapraklar, koza)
    return root


# --------------------------------------------------------------------------
@model("ZB_obje_ari_kovani")
def ari_kovani() -> Node:
    """Geleneksel saman kovan, ahşap sehpa üzerinde (Nahl 68)."""
    root = Node("ZB_obje_ari_kovani")
    sehpa = merge(
        box(0.56, 0.04, 0.56, "ahsap", y0=0.22),
        *[box(0.05, 0.22, 0.05, "ahsap_koyu").translate(x, 0, z)
          for x in (-0.22, 0.22) for z in (-0.22, 0.22)],
    ).shade_vary(0.05, 7)
    halkalar = []
    R, H, n = 0.24, 0.42, 7
    for k in range(n):
        y0, y1 = H * k / n, H * (k + 1) / n
        r0 = R * math.sqrt(max(0.0, 1 - (y0 / H) ** 2))
        r1 = R * math.sqrt(max(0.0, 1 - (y1 / H) ** 2))
        rm = (r0 + r1) / 2 + 0.012
        prof = [(r0, y0), (rm, (y0 + y1) / 2), (max(r1, 0.0), y1)]
        halkalar.append(lathe(prof, 12, "saman" if k % 2 == 0 else "saman_koyu"))
    kovan = merge(*halkalar, cylinder(0.03, 0.0, 0.03, 6, "saman_koyu", y0=H - 0.005)).jitter(0.004, 3)
    kovan = kovan.translate(0, 0.26, 0).shade_vary(0.05, 8)
    giris = box(0.07, 0.035, 0.02, "bos", y0=0.265).translate(0, 0, 0.235)
    root.add(sehpa, kovan, giris)
    return root


# --------------------------------------------------------------------------
@model("ZB_obje_tesbih")
def tesbih() -> Node:
    """33'lük kehribar tesbih: iki nişane, imame ve püskül."""
    root = Node("ZB_obje_tesbih")
    r = 0.017
    tanelar = []
    n = 33
    for i in range(n):
        t = 2 * math.pi * (i + 0.5) / (n + 3)
        # Damla biçimi: imame tarafı (t=0) daralır
        x = 0.15 * math.sin(t)
        z = -0.12 * math.cos(t) - 0.03 * math.cos(2 * t)
        renk = "altin" if i in (10, 21) else "kehribar"   # 11. ve 22. tanelerden sonra nişane
        rr = r * (1.25 if renk == "altin" else 1.0)
        tanelar.append(icosphere(rr, 1, renk).translate(x, rr, z))
    imame = lathe([(0.0, 0.0), (0.016, 0.01), (0.02, 0.03), (0.012, 0.055), (0.004, 0.07), (0.0, 0.075)],
                  8, "kehribar").rotate("x", -90).translate(0, 0.02, -0.16)
    puskul = merge(
        tube([[0, 0.018, -0.23], [0, 0.012, -0.26]], [0.004, 0.004], 4, "kumas_yesil"),
        cone(0.028, 0.08, 8, "kumas_yesil").rotate("x", -100).translate(0, 0.014, -0.26),
    )
    root.add(merge(*tanelar, imame, puskul).shade_vary(0.04, 9))
    return root
