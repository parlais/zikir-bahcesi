"""Cennet mekânının yapıları (Faz 2a).

  Su köşkü (Zümer 20: "kat kat birbiri üstüne inşa edilmiş ve altlarından
    ırmaklar akan yüksek köşkler"): ırmağın üstüne kemerli ayaklarla oturan iki
    katlı köşk. Duvarlar altın ve gümüş tuğla, misk harç (et-Tâc 5/402);
    inci kubbe, yakut süsler.
  İnci çadır (Buhârî-Müslim: içi boş inciden çadır).
  Sedir köşesi (Hicr 47, Gâşiye 13-16, Rahmân 76, İnsan 15): karşılıklı sedirler,
    yeşil yastıklar, serilmiş halı, gümüş kaplar ve billur kupalar.
  Selsebil çeşmesi (İnsan 18): suyun yavaşça aktığı dalgalı mermer levha.
  Âb-ı hayat pınarı (Rahmân 66: fışkıran pınarlar).

Yerel eksenler: ırmak köşkün altından +z yönünde akar; köşk x boyunca uzanır.
"""
from __future__ import annotations

import math

import numpy as np

from mf.mesh import (Mesh, blade, blob, box, cone, cylinder, icosphere, lathe, merge, pointed_arch,
                     star_polygon, tube)
from mf.palette import renk
from mf.scene import Node

from . import model
from .yapilar import alem, almasik_kemer, dolu_kemer, kemer_aynasi, kubbe

TUGLA = ("altin_tugla", "gumus_tugla")


def _gruplu(root: Node, parcalar: dict):
    """{malzeme: [mesh, ...]} -> köke malzeme başına tek mesh."""
    for mat, ms in parcalar.items():
        if ms:
            root.add(merge(*[m.with_material(mat) for m in ms]).shade_vary(0.025, len(mat)))


def _revak(x0, x1, y0, yay_y, ust_y, n, derinlik, kolon_r, P):
    """XY düzleminde (z=0) n gözlü revak cephesi: sütunlar, almaşık kemerler,
    kemer aynaları. P: malzeme sözlüğü (yerinde doldurulur)."""
    xs = np.linspace(x0, x1, n + 1)
    for x in xs:
        P["tas"] += [cylinder(kolon_r * 1.35, kolon_r * 1.35, 0.14, 8, "tas_koyu", y0=y0).translate(x, 0, 0),
                     cylinder(kolon_r, kolon_r * 0.88, yay_y - y0 - 0.34, 10, "mermer", y0=y0 + 0.14).translate(x, 0, 0)]
        P["metal"].append(cylinder(kolon_r * 0.9, kolon_r * 1.55, 0.24, 8, "altin", y0=yay_y - 0.22).translate(x, 0, 0))
    for i in range(n):
        a, b = xs[i], xs[i + 1]
        span = b - a - 2.4 * kolon_r
        cx = (a + b) / 2
        yay = pointed_arch(span, span * 0.56, 8)
        ic = [(cx + x, y + yay_y) for x, y in yay]
        dis = [(cx + x * 1.15, y * 1.13 + yay_y) for x, y in yay]
        P["tas"] += almasik_kemer(ic, dis, derinlik, renkler=TUGLA)
        P["tas"].append(kemer_aynasi(dis, a, b, yay_y, ust_y, derinlik * 0.9, "fildisi"))


def _dikdortgen_revak(gx, gz, y0, yay_y, ust_y, nx, nz, kolon_r, P, derinlik=0.34):
    """Dikdörtgen çevresinde revak (gx, gz yarı boyutlar)."""
    for s in (-1, 1):
        Q = {k: [] for k in P}
        _revak(-gx, gx, y0, yay_y, ust_y, nx, derinlik, kolon_r, Q)
        for k in Q:
            P[k] += [m.translate(0, 0, s * gz) for m in Q[k]]
        Q = {k: [] for k in P}
        _revak(-gz, gz, y0, yay_y, ust_y, nz, derinlik, kolon_r, Q)
        for k in Q:
            # Köşe sütunları x cephesinde zaten var: z cephesinin uç sütunlarını at
            P[k] += [m.rotate("y", 90).translate(s * gx, 0, 0) for m in Q[k]
                     if not (k in ("tas", "metal") and _kose_sutunu(m, gz))]


def _kose_sutunu(m: Mesh, gz) -> bool:
    lo, hi = m.bounds()
    c = (lo + hi) / 2
    genis = hi[1] - lo[1] > 0.1 and (hi[0] - lo[0]) < 0.6 and (hi[2] - lo[2]) < 0.6
    return genis and abs(abs(c[0]) - gz) < 1e-3 and abs(c[2]) < 1e-3


def _korkuluk(gx, gz, y0, aralik, P, yuk=0.55):
    """Dam kenarında alçak korkuluk; direk başlarında inciler."""
    for s in (-1, 1):
        P["tas"].append(box(2 * gx, yuk, 0.22, "fildisi", y0=y0).translate(0, 0, s * gz))
        P["tas"].append(box(0.22, yuk, 2 * gz, "fildisi", y0=y0).translate(s * gx, 0, 0))
        P["tas"].append(box(2 * gx + 0.1, 0.08, 0.3, "altin_tugla", y0=y0 + yuk).translate(0, 0, s * gz))
        P["tas"].append(box(0.3, 0.08, 2 * gz + 0.1, "altin_tugla", y0=y0 + yuk).translate(s * gx, 0, 0))
    for x in np.arange(-gx, gx + 1e-6, aralik):
        for s in (-1, 1):
            P["tas"].append(box(0.3, yuk + 0.25, 0.3, "fildisi", y0=y0).translate(x, 0, s * gz))
            P["inci"].append(icosphere(0.17, 0, "inci").smooth(70).translate(x, y0 + yuk + 0.4, s * gz))
    for z in np.arange(-gz, gz + 1e-6, aralik):
        for s in (-1, 1):
            P["tas"].append(box(0.3, yuk + 0.25, 0.3, "fildisi", y0=y0).translate(s * gx, 0, z))
            P["inci"].append(icosphere(0.17, 0, "inci").smooth(70).translate(s * gx, y0 + yuk + 0.4, z))


def _pencereler(gx, gz, y0, boy, n_x, n_z, P):
    """Salon duvarlarına çini dolgulu, altın çerçeveli sivri kemerli pencereler."""
    for eksen, g, n, diger in (("x", gx, n_x, gz), ("z", gz, n_z, gx)):
        for i in range(n):
            u = -g + 2 * g * (i + 0.5) / n
            w = min(1.5, 2 * g / n * 0.55)
            yay = pointed_arch(w, w * 0.6, 6)
            ic = [(x, y + y0 + boy * 0.62) for x, y in yay]
            panel = merge(box(w, boy * 0.62, 0.06, "cini_lacivert", y0=y0),
                          dolu_kemer(ic, y0 + boy * 0.62, 0.06, "cini_lacivert"))
            dis = [(x * 1.18, y * 1.14 + y0 + boy * 0.62) for x, y in yay]
            cerceve = merge(band_ic(ic, dis), box(0.12, boy * 0.62, 0.1, "altin", y0=y0).translate(-w / 2 - 0.06, 0, 0),
                            box(0.12, boy * 0.62, 0.1, "altin", y0=y0).translate(w / 2 + 0.06, 0, 0))
            for s in (-1, 1):
                if eksen == "x":
                    P["cini"].append(panel.translate(u, 0, s * (diger + 0.02)))
                    P["metal"].append(cerceve.translate(u, 0, s * (diger + 0.05)))
                else:
                    P["cini"].append(panel.rotate("y", 90).translate(s * (diger + 0.02), 0, u))
                    P["metal"].append(cerceve.rotate("y", 90).translate(s * (diger + 0.05), 0, u))


def band_ic(ic, dis):
    from mf.mesh import band
    return band(ic, dis, 0.1, "altin")


@model("ZB_yapi_su_kosku")
def su_kosku() -> Node:
    root = Node("ZB_yapi_su_kosku")
    P = {"tas": [], "tugla": [], "cini": [], "metal": [], "inci": []}
    W, D = 26.0, 12.0
    # --- Suyun içindeki ayaklar ve alt kemerler (ırmak bunların altından akar)
    xs = np.linspace(-W / 2 + 0.75, W / 2 - 0.75, 5)
    ayak_w = 1.5
    for x in xs:
        P["tas"].append(box(ayak_w, 6.4, D, "fildisi", y0=-2.0).translate(x, 0, 0))
        P["tas"].append(box(ayak_w + 0.2, 0.3, D + 0.2, "kaya_krem", y0=-0.25).translate(x, 0, 0))
        for s in (-1, 1):                                        # sel yaran
            P["tas"].append(box(1.06, 4.4, 1.06, "fildisi", y0=-2.0).rotate("y", 45).translate(x, 0, s * D / 2))
            P["tas"].append(cone(0.76, 1.0, 4, "altin_tugla", y0=2.4).translate(x, 0, s * D / 2))
    yay_y = 1.1
    for i in range(4):
        a, b = xs[i] + ayak_w / 2, xs[i + 1] - ayak_w / 2
        span = b - a
        cx = (a + b) / 2
        yay = pointed_arch(span, span * 0.62, 10)
        ic = [(cx + x, y + yay_y) for x, y in yay]
        dis = [(cx + x * 1.12, y * 1.1 + yay_y) for x, y in yay]
        for s in (-1, 1):
            P["tas"] += [m.translate(0, 0, s * (D / 2 - 0.3)) for m in almasik_kemer(ic, dis, 0.62, TUGLA)]
            P["tas"].append(kemer_aynasi(dis, a, b, yay_y, 4.4, 0.6, "fildisi").translate(0, 0, s * (D / 2 - 0.3)))
        # Kemerin altındaki tonoz (sudan yansıyan çini)
        V, F = [], []
        for j, (x, y) in enumerate(ic):
            V += [[x, y, -D / 2 + 0.6], [x, y, D / 2 - 0.6]]
        for j in range(len(ic) - 1):
            k = 2 * j
            F += [[k, k + 1, k + 3], [k, k + 3, k + 2]]
        m = Mesh(np.array(V, np.float32), np.array(F), np.tile(np.array(renk("cini_firuze"), np.float32), (len(F), 1)))
        P["cini"].append(m.flipped())
    # --- Döşeme ve saçak bandı
    P["tas"].append(box(W + 1.4, 0.6, D + 1.4, "fildisi", y0=4.4))
    P["cini"].append(box(W + 1.6, 0.26, D + 1.6, "cini_firuze", y0=4.55))
    for x in np.arange(-W / 2, W / 2 + 0.01, W / 8):             # yakut süsler
        for s in (-1, 1):
            P["inci"].append(star_polygon(8, 0.2, 0.1, 0.06, "yakut").translate(x, 4.68, s * (D / 2 + 0.83)))
    # --- 1. kat: tuğla salon ve çevresinde revak
    y1 = 5.0
    P["tugla"].append(box(15.0, 5.4, 6.4, "fildisi", y0=y1))
    _pencereler(7.5, 3.2, y1 + 0.6, 3.6, 5, 2, P)
    gx, gz = 11.0, 5.2
    _dikdortgen_revak(gx, gz, y1, 8.3, 10.0, 8, 4, 0.2, P)
    for s in (-1, 1):
        P["tas"].append(box(2 * gx + 0.6, 0.4, 0.6, "fildisi", y0=10.0).translate(0, 0, s * gz))
        P["tas"].append(box(0.6, 0.4, 2 * gz + 0.6, "fildisi", y0=10.0).translate(s * gx, 0, 0))
        P["cini"].append(box(2 * gx + 0.64, 0.16, 0.64, "cini_firuze", y0=10.1).translate(0, 0, s * gz))
        P["cini"].append(box(0.64, 0.16, 2 * gz + 0.64, "cini_firuze", y0=10.1).translate(s * gx, 0, 0))
    P["tas"].append(box(2 * gx + 1.0, 0.36, 2 * gz + 1.0, "fildisi", y0=10.4))
    _korkuluk(gx + 0.3, gz + 0.3, 10.76, 2.75, P)
    # Köşe köşkçükleri (çardak kubbeler)
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx, cz = sx * (gx - 1.0), sz * (gz - 0.9)
            for kx in (-1, 1):
                for kz in (-1, 1):
                    P["tas"].append(cylinder(0.1, 0.09, 2.1, 8, "mermer", y0=10.76).translate(cx + kx * 0.62, 0, cz + kz * 0.62))
            P["tas"].append(box(1.7, 0.18, 1.7, "fildisi", y0=12.86).translate(cx, 0, cz))
            P["metal"].append(kubbe(0.82, "altin", 12, y0=13.04).translate(cx, 0, cz))
            P["metal"].append(alem(13.9, 0.5).translate(cx, 0, cz))
    # --- 2. kat
    y2 = 10.76
    P["tugla"].append(box(10.0, 4.0, 5.0, "fildisi", y0=y2))
    _pencereler(5.0, 2.5, y2 + 0.5, 2.8, 4, 2, P)
    gx2, gz2 = 6.6, 3.8
    _dikdortgen_revak(gx2, gz2, y2, 13.0, 14.4, 5, 3, 0.17, P, derinlik=0.3)
    for s in (-1, 1):
        P["tas"].append(box(2 * gx2 + 0.5, 0.36, 0.5, "fildisi", y0=14.4).translate(0, 0, s * gz2))
        P["tas"].append(box(0.5, 0.36, 2 * gz2 + 0.5, "fildisi", y0=14.4).translate(s * gx2, 0, 0))
    P["tas"].append(box(2 * gx2 + 0.9, 0.32, 2 * gz2 + 0.9, "fildisi", y0=14.76))
    _korkuluk(gx2 + 0.25, gz2 + 0.25, 15.08, 2.64, P, yuk=0.45)
    # --- Kasnak ve inci kubbe
    P["tugla"].append(cylinder(3.1, 3.1, 1.7, 16, "fildisi", y0=15.08).rotate("y", 11.25))
    P["cini"].append(cylinder(3.16, 3.16, 0.28, 16, "cini_firuze", y0=16.45).rotate("y", 11.25))
    P["inci"].append(kubbe(3.25, "inci", 24, y0=16.78).smooth(50))
    for i in range(12):
        a = 2 * math.pi * i / 12
        prof = [(3.3 * f, 16.78 + 3.25 * g) for f, g in ((1.0, 0.0), (0.97, 0.25), (0.87, 0.5), (0.68, 0.74),
                                                          (0.4, 0.93), (0.12, 1.02))]
        P["metal"].append(tube([[r * math.cos(a), y, r * math.sin(a)] for r, y in prof],
                               [0.07] * 6, 4, "altin", cap=False))
    P["metal"].append(alem(16.78 + 3.35, 1.5))
    _gruplu(root, P)
    return root


# --------------------------------------------------------------------------
@model("ZB_yapi_inci_cadir")
def inci_cadir() -> Node:
    """İçi boş inciden çadır: ön yüzünde (+z) perdeleri toplanmış bir kapı."""
    root = Node("ZB_yapi_inci_cadir")
    P = {"inci": [], "kumas": [], "metal": [], "tas": []}
    R = 6.5
    alt = [(R, 0.25), (R * 1.03, 1.4), (R * 1.04, 2.8), (R * 1.0, 4.2)]
    ust = [(R * 1.0, 4.2), (R * 0.93, 5.6), (R * 0.78, 7.1), (R * 0.56, 8.5), (R * 0.3, 9.5), (R * 0.1, 9.95),
           (0.0, 10.05)]
    kapi = 44.0
    bas, sup = 90 + kapi / 2, 360 - kapi
    P["inci"].append(lathe(alt, 36, "inci", start_deg=bas, sweep=sup, cap=False).smooth(60))
    P["inci"].append(lathe(ust, 40, "inci", cap=False).smooth(60))
    ic_renk = "inci_ic"
    P["kumas"].append(lathe([(r * 0.97, y) for r, y in alt], 36, ic_renk, start_deg=bas, sweep=sup, cap=False).flipped().smooth(60))
    P["kumas"].append(lathe([(r * 0.97, y - 0.05) for r, y in ust], 40, ic_renk, cap=False).flipped().smooth(60))
    # Kaburgalar
    for i in range(16):
        a = 2 * math.pi * i / 16 + math.pi / 16
        derece = math.degrees(a) % 360
        prof = ust if 90 - kapi / 2 - 4 < derece < 90 + kapi / 2 + 4 else alt[:-1] + ust
        P["metal"].append(tube([[r * 1.012 * math.cos(a), y, r * 1.012 * math.sin(a)] for r, y in prof],
                               [0.06] * len(prof), 4, "altin", cap=False))
    # Etek bandı ve inci dizisi
    P["metal"].append(lathe([(R * 1.02, 4.05), (R * 1.03, 4.4)], 40, "altin", cap=False))
    for i in range(36):
        a = 2 * math.pi * i / 36
        P["inci"].append(icosphere(0.1, 0, "inci").smooth(70).translate(R * 1.05 * math.cos(a), 4.0, R * 1.05 * math.sin(a)))
    # Kapı: altın direkler ve toplanmış perdeler
    for s in (-1, 1):
        a = math.radians(90 + s * kapi / 2)
        x, z = R * math.cos(a), R * math.sin(a)
        P["metal"].append(cylinder(0.12, 0.1, 4.2, 8, "altin", y0=0.25).translate(x, 0, z))
        P["metal"].append(icosphere(0.18, 1, "altin").translate(x, 4.5, z))
        yol = [[x - s * 0.1, 4.1, z + 0.15], [x - s * 0.55, 2.8, z + 0.3], [x - s * 0.25, 1.6, z + 0.3],
               [x - s * 0.45, 0.3, z + 0.35]]
        P["kumas"].append(blade(yol, [0.5, 0.35, 0.22, 0.4], "ipek", fold=0.6,
                                side=[math.cos(a + math.pi / 2), 0, math.sin(a + math.pi / 2)]).smooth(60))
    # Taban, halı, yastıklar
    P["tas"].append(lathe([(R + 0.9, 0.0), (R + 0.9, 0.2), (R + 0.7, 0.26), (0.0, 0.26)], 36, "mermer"))
    P["kumas"].append(lathe([(R * 0.88, 0.27), (0.0, 0.27)], 32, "hali_kirmizi"))
    P["kumas"].append(lathe([(R * 0.6, 0.275), (0.0, 0.275)], 32, "hali_lacivert"))
    P["kumas"].append(lathe([(R * 0.25, 0.28), (0.0, 0.28)], 16, "hali_altin"))
    for i in range(9):
        a = math.radians(140 + i * 28)
        P["kumas"].append(blob(0.5, "yastik_yesil", seed=700 + i, subdiv=2, squash=0.7, jitter=0.05)
                          .scale(1.0, 1.0, 0.55).rotate("y", -(math.degrees(a) + 90))
                          .translate(R * 0.8 * math.cos(a), 0.62, R * 0.8 * math.sin(a)).smooth(60))
    P["metal"].append(alem(10.0, 1.1))
    _gruplu(root, P)
    return root


# --------------------------------------------------------------------------
def _hali(w, d, nx, nz, y=0.02) -> Mesh:
    """Desenli halı: kenar suyu, kırmızı zemin, lacivert madalyon."""
    V, F, C = [], [], []
    for j in range(nz + 1):
        for i in range(nx + 1):
            V.append([-w / 2 + w * i / nx, y, -d / 2 + d * j / nz])
    for j in range(nz):
        for i in range(nx):
            a = j * (nx + 1) + i
            u = (i + 0.5) / nx * 2 - 1
            v = (j + 0.5) / nz * 2 - 1
            kenar = min(1 - abs(u), 1 - abs(v)) * min(nx, nz) / 2
            if kenar < 1:
                c = "hali_lacivert"
            elif kenar < 2:
                c = "hali_altin" if (i + j) % 2 else "hali_krem"
            else:
                m = abs(u) / 0.55 + abs(v) / 0.6
                c = "hali_krem" if m < 0.35 else ("hali_lacivert" if m < 0.8 else "hali_kirmizi")
            for f in ([a, a + nx + 2, a + 1], [a, a + nx + 1, a + nx + 2]):
                F.append(f)
                C.append(renk(c))
    return Mesh(np.array(V, np.float32), np.array(F), np.array(C, np.float32))


def _sedir(P, z, yon):
    """Tek sedir: ahşap gövde, yeşil kadife döşek, sırtta yastık dizisi. yon: oturanın baktığı z yönü."""
    L = 2.8
    P["govde"] += [box(L, 0.36, 0.95, "ahsap_koyu", y0=0.02).translate(0, 0, z)]
    P["metal"] += [box(L + 0.04, 0.05, 0.99, "altin", y0=0.34).translate(0, 0, z)]
    for x in (-L / 2 + 0.1, L / 2 - 0.1):
        for dz in (-0.4, 0.4):
            P["metal"].append(icosphere(0.06, 1, "altin").translate(x, 0.04, z + dz))
    P["kumas"].append(box(L - 0.1, 0.17, 0.9, "kadife_yesil", y0=0.39).translate(0, 0, z))
    arka = z - yon * 0.34
    for i in range(4):
        x = -L / 2 + 0.4 + i * (L - 0.8) / 3
        P["kumas"].append(blob(0.34, "yastik_yesil", seed=800 + i + int(z * 10), subdiv=2, squash=0.8, jitter=0.04)
                          .scale(1.0, 1.0, 0.4).rotate("x", -yon * 12).translate(x, 0.8, arka).smooth(60))
    for x in (-L / 2 + 0.12, L / 2 - 0.12):
        P["kumas"].append(cylinder(0.14, 0.14, 0.8, 10, "hali_altin").rotate("x", 90)
                          .translate(x, 0.7, z - 0.4).smooth(40))


@model("ZB_yapi_sedir_kosesi")
def sedir_kosesi() -> Node:
    root = Node("ZB_yapi_sedir_kosesi")
    P = {"govde": [], "kumas": [], "metal": [], "inci": [], "cicek": []}
    for s in (-1, 1):
        _sedir(P, s * 1.75, -s)
    P["kumas"].append(_hali(3.6, 2.4, 24, 16))
    # Alçak sehpa, gümüş tepsi, billur kupalar, meyve kâsesi
    P["govde"].append(lathe([(0.3, 0.02), (0.22, 0.1), (0.14, 0.3), (0.28, 0.36), (0.0, 0.37)], 8, "ahsap_koyu"))
    P["metal"].append(lathe([(0.0, 0.37), (0.48, 0.37), (0.52, 0.41), (0.5, 0.42), (0.0, 0.39)], 16, "gumus"))
    for i, a in enumerate((0.3, 2.4, 4.4)):
        x, z = 0.3 * math.cos(a), 0.3 * math.sin(a)
        P["inci"].append(lathe([(0.0, 0.0), (0.04, 0.005), (0.012, 0.02), (0.01, 0.07), (0.045, 0.1), (0.05, 0.16),
                                (0.044, 0.162)], 10, "cam", cap=False).translate(x, 0.39, z).smooth(60))
    P["metal"].append(lathe([(0.0, 0.0), (0.07, 0.01), (0.09, 0.08), (0.05, 0.16), (0.04, 0.22), (0.06, 0.25),
                             (0.0, 0.25)], 10, "gumus").translate(-0.12, 0.39, 0.05).smooth(60))
    P["metal"].append(lathe([(0.0, 0.0), (0.12, 0.01), (0.19, 0.07), (0.2, 0.09)], 14, "gumus", cap=False)
                      .translate(0.14, 0.39, -0.1).smooth(60))
    rng = np.random.default_rng(81)
    for i in range(9):
        r = 0.1 * math.sqrt(rng.uniform(0.1, 1))
        a = rng.uniform(0, 2 * math.pi)
        P["cicek"].append(icosphere(0.05, 1, ["nar", "uzum", "hurma_meyve"][i % 3])
                          .translate(0.14 + r * math.cos(a), 0.47 + 0.02 * (i % 2), -0.1 + r * math.sin(a)).smooth(60))
    _gruplu(root, P)
    return root


# --------------------------------------------------------------------------
@model("ZB_yapi_selsebil_cesmesi")
def selsebil_cesmesi() -> Node:
    """Selsebil: arkadaki niş, suyun istiridye kabuğu biçimli yuvalardan
    yavaşça süzüldüğü eğik mermer levha, önde küçük havuz. Ön yüz +z."""
    root = Node("ZB_yapi_selsebil_cesmesi")
    P = {"tas": [], "metal": [], "cini": [], "selale": [], "su": []}
    P["tas"].append(box(2.6, 3.9, 0.6, "mermer", y0=0.0))
    yay = pointed_arch(1.6, 1.0, 8)
    ic = [(x, y + 2.7) for x, y in yay]
    dis = [(x * 1.18, y * 1.14 + 2.7) for x, y in yay]
    P["tas"] += [m.translate(0, 0, 0.32) for m in almasik_kemer(ic, dis, 0.1, ("mermer", "kaya_pembe"))]
    P["cini"].append(merge(box(1.6, 2.7, 0.04, "cini_firuze", y0=0.0), dolu_kemer(ic, 2.7, 0.04, "cini_firuze"))
                     .translate(0, 0, 0.31))
    # Eğik dalgalı levha
    nx, nz = 8, 45
    w = 1.3
    V, V2 = [], []
    for j in range(nz + 1):
        t = j / nz
        for i in range(nx + 1):
            u = i / nx * 2 - 1
            z = 0.36 + 0.8 * t
            y = 2.45 - 1.75 * t
            kabuk = 0.07 * abs(math.sin(math.pi * t * 9)) * (1 - 0.5 * u * u)
            V.append([u * w / 2, y + kabuk, z])
            V2.append([u * w / 2 * 0.92, y + kabuk + 0.018, z])
    F = []
    for j in range(nz):
        for i in range(nx):
            a = j * (nx + 1) + i
            F += [[a, a + nx + 2, a + 1], [a, a + nx + 1, a + nx + 2]]
    F = np.array(F)
    lev = Mesh(np.array(V, np.float32), F, np.tile(np.array(renk("mermer"), np.float32), (len(F), 1)))
    P["tas"].append(lev.smooth(50))
    P["selale"].append(Mesh(np.array(V2, np.float32), F, np.tile(np.array(renk("su"), np.float32), (len(F), 1))))
    for s in (-1, 1):
        egim = np.array([[1, 0, 0], [0, 1, -2.1875], [0, 0, 1]], np.float32)   # levhanın eğimi
        P["tas"].append(box(0.1, 0.25, 0.8, "mermer", y0=0.0).translate(s * w / 2, 0, 0.76).transform(egim)
                        .translate(0, 3.24, 0))
    P["metal"].append(tube([[0, 2.75, 0.3], [0, 2.75, 0.45], [0, 2.6, 0.5]], [0.05, 0.05, 0.04], 6, "altin"))
    # Havuz
    P["tas"].append(box(2.2, 0.55, 1.15, "mermer", y0=0.0).translate(0, 0, 1.55))
    P["su"].append(box(1.9, 0.02, 0.85, "su", y0=0.47).translate(0, 0, 1.55))
    P["tas"].append(box(1.9, 0.02, 0.85, "cini_firuze", y0=0.12).translate(0, 0, 1.55))
    for s in (-1, 1):                                            # yan pilastırlar
        P["tas"].append(box(0.34, 4.3, 0.7, "kaya_krem", y0=0.0).translate(s * 1.3, 0, 0.05))
        P["metal"].append(kubbe(0.2, "altin", 8, y0=4.3).translate(s * 1.3, 0, 0.05))
    P["tas"].append(box(2.95, 0.3, 0.8, "kaya_krem", y0=3.9).translate(0, 0, 0.05))
    _gruplu(root, P)
    return root


@model("ZB_yapi_ab_i_hayat_pinari")
def ab_i_hayat_pinari() -> Node:
    """Fışkıran pınar: taş halkanın ortasında mermer kâseden su fışkırır
    (Godot "fiskiye_pinar" noktasına parçacık koyar)."""
    root = Node("ZB_yapi_ab_i_hayat_pinari")
    P = {"tas": [], "su": [], "metal": []}
    rng = np.random.default_rng(91)
    for i in range(16):
        a = 2 * math.pi * i / 16 + rng.uniform(-0.1, 0.1)
        r = rng.uniform(0.28, 0.45)
        P["tas"].append(blob(r, "kaya_krem" if i % 3 else "kaya_pembe", seed=900 + i, subdiv=1, squash=0.7, jitter=0.2)
                        .translate(1.55 * math.cos(a), 0.12, 1.55 * math.sin(a)).smooth(55))
    P["tas"].append(lathe([(1.6, -0.05), (1.5, -0.25), (0.0, -0.3)], 20, "cini_firuze").flipped())
    P["su"].append(lathe([(1.55, 0.12), (0.0, 0.12)], 24, "su"))
    P["tas"].append(blob(0.5, "kaya_krem", seed=950, subdiv=2, squash=0.8, jitter=0.15).translate(0, 0.2, 0).smooth(55))
    P["tas"].append(lathe([(0.1, 0.5), (0.12, 0.75), (0.2, 0.85), (0.42, 0.95), (0.46, 1.02), (0.4, 1.0),
                           (0.0, 0.92)], 14, "mermer").smooth(50))
    P["su"].append(lathe([(0.4, 0.99), (0.0, 0.99)], 14, "su"))
    P["metal"].append(cylinder(0.05, 0.04, 0.12, 8, "altin", y0=0.98))
    _gruplu(root, P)
    root.add(Node("fiskiye_pinar", translation=(0.0, 1.08, 0.0)))
    return root


@model("ZB_obje_inci_cakil")
def inci_cakil() -> Node:
    """Arsa sınırındaki çakıl kümesi: inci ve yakut taşlar (et-Tâc 5/402)."""
    rng = np.random.default_rng(97)
    parca = []
    for i in range(6):
        r = rng.uniform(0.05, 0.1)
        renk_ad = "yakut" if i == 2 else ("sedef" if i % 3 == 1 else "inci")
        parca.append(icosphere(r, 1, renk_ad).scale(1.0, 0.7, 0.85).rotate("y", rng.uniform(0, 180))
                     .translate(rng.uniform(-0.16, 0.16), r * 0.45, rng.uniform(-0.1, 0.1)).smooth(70))
    return Node("ZB_obje_inci_cakil", [merge(*parca).with_material("inci")])
