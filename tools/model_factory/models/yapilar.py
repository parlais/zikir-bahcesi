"""D bölümü: yapılar ve mimari (MVP ilk dilim: bahçe kapısı, şadırvan, köşk).

Osmanlı bahçe mimarisinden sade formlar: sivri kemer, almaşık (kırmızı-beyaz)
kemer taşları, kurşun kubbe ve alem. Hareketli parçalar ayrı düğümdür.
"""
from __future__ import annotations

import math

import numpy as np

from mf.mesh import (band, blob, box, cone, cylinder, icosphere, lathe, merge, pointed_arch, tube)
from mf.scene import Node

from . import model
from .ortak import cevre_noktalari


def kubbe(r, color="kursun", seg=10, y0=0.0) -> "Mesh":
    """Yarım küreye yakın, tepesi hafif sivri Osmanlı kubbesi."""
    prof = [(r, 0.0), (r * 0.97, r * 0.25), (r * 0.87, r * 0.5), (r * 0.68, r * 0.74),
            (r * 0.4, r * 0.93), (r * 0.12, r * 1.02), (0.0, r * 1.05)]
    return lathe([(a, b + y0) for a, b in prof], seg, color)


def alem(y0, boy=0.35) -> "Mesh":
    """Kubbe tepesindeki alem: üst üste topuzlar (hilal yok; sade)."""
    return merge(
        cylinder(0.025, 0.02, boy * 0.4, 6, "altin", y0=y0),
        icosphere(boy * 0.14, 1, "altin").translate(0, y0 + boy * 0.45, 0),
        icosphere(boy * 0.1, 1, "altin").translate(0, y0 + boy * 0.72, 0),
        cone(boy * 0.05, boy * 0.25, 6, "altin", y0=y0 + boy * 0.8),
    ).with_material("metal")


def almasik_kemer(ic, dis, derinlik, renkler=("mercan_kirmizi", "fildisi")) -> list:
    """Kemer taşları sırayla iki renk: Osmanlı almaşık (ablak) kemeri."""
    return [band(ic[i:i + 2], dis[i:i + 2], derinlik, renkler[i % 2]) for i in range(len(ic) - 1)]


def kemer_aynasi(dis, sol, sag, alt, ust, derinlik, color="tas"):
    """Kemerin dışı ile dikdörtgen çerçeve arasındaki köşelikler (spandrel)."""
    cx, cy = (sol + sag) / 2, alt
    cerceve = []
    for x, y in dis:
        dx, dy = x - cx, y - cy
        t = min((sag - cx) / abs(dx) if abs(dx) > 1e-9 else 1e9, (ust - cy) / dy if dy > 1e-9 else 1e9)
        cerceve.append((cx + dx * t, cy + dy * t))
    return band(dis, cerceve, derinlik, color)


def dolu_kemer(ic, taban_y, derinlik, color):
    """Kemerin içini dolduran ayna (kapı üstü alınlık)."""
    return band([(x, taban_y) for x, _ in ic], ic, derinlik, color)


# --------------------------------------------------------------------------
@model("ZB_yapi_bahce_kapisi")
def bahce_kapisi() -> Node:
    """Bismillah ile açılan bahçe kapısı. Kanatlar ayrı düğüm, menteşeden döner.
    Kapı üstünde Mâşâallah kitabesi için boş yer (kitabe_yeri) bırakıldı."""
    root = Node("ZB_yapi_bahce_kapisi")
    acik = 1.6            # kemer açıklığı
    ayak = 0.5            # ayak genişliği
    yay_y = 2.0           # kemerin başladığı yükseklik
    D = 0.45
    parcalar = [box(acik + 2 * ayak + 0.3, 0.12, D + 0.5, "tas_koyu")]
    for s in (-1, 1):
        x = s * (acik / 2 + ayak / 2)
        parcalar += [
            box(ayak + 0.12, 0.35, D + 0.12, "tas_koyu", y0=0.12).translate(x, 0, 0),
            box(ayak, 3.3, D, "tas", y0=0.12).translate(x, 0, 0),
            box(ayak + 0.14, 0.12, D + 0.14, "tas_koyu", y0=3.42).translate(x, 0, 0),
            cylinder(0.2, 0.2, 0.12, 8, "tas", y0=3.54).translate(x, 0, 0),
            kubbe(0.2, "kursun", 8, y0=3.66).translate(x, 0, 0),
        ]
    ic = [(x, y + yay_y) for x, y in pointed_arch(acik, 1.05, 10)]
    dis = [(x * 1.22, y * 1.18 + yay_y) for x, y in pointed_arch(acik, 1.05, 10)]
    parcalar += almasik_kemer(ic, dis, D * 0.9)
    parcalar.append(kemer_aynasi(dis, -acik / 2, acik / 2, yay_y, 3.42, D * 0.85, "tas"))
    parcalar.append(dolu_kemer(ic, yay_y, 0.08, "firuze").translate(0, 0, -0.1))
    parcalar.append(box(acik + 2 * ayak + 0.2, 0.2, D + 0.2, "tas_koyu", y0=3.42))
    parcalar.append(box(acik + 2 * ayak, 0.06, D + 0.1, "mercan_kirmizi", y0=3.36))
    root.add(merge(*parcalar).shade_vary(0.03, 21))
    root.add(alem(3.92).translate(-(acik / 2 + ayak / 2), 0, 0), alem(3.92).translate(acik / 2 + ayak / 2, 0, 0))

    for s, ad in ((-1, "kanat_sol"), (1, "kanat_sag")):
        kanat = Node(ad, translation=(s * acik / 2, 0.12, -0.1))
        w = acik / 2
        civiler = [icosphere(0.022, 0, "altin").translate(-s * (w * fx), 1.9 * fy + 0.05, 0.05)
                   for fx in (0.2, 0.5, 0.8) for fy in (0.15, 0.4, 0.65, 0.9)]
        kanat.add(merge(
            box(w, 1.88, 0.07, "ahsap").translate(-s * w / 2, 0, 0),
            box(w - 0.12, 0.05, 0.08, "ahsap_koyu", y0=0.6).translate(-s * w / 2, 0, 0.01),
            box(w - 0.12, 0.05, 0.08, "ahsap_koyu", y0=1.3).translate(-s * w / 2, 0, 0.01),
        ).shade_vary(0.04, 22 + s))
        kanat.add(merge(*civiler,
                        tube([[-s * (w - 0.1), 1.0, 0.06], [-s * (w - 0.1), 0.92, 0.1], [-s * (w - 0.1), 0.84, 0.06]],
                             [0.012] * 3, 5, "altin", cap=False)).with_material("metal"))
        root.add(kanat)
    root.add(Node("kitabe_yeri", translation=(0.0, 3.2, D / 2 + 0.02)))
    return root


# --------------------------------------------------------------------------
@model("ZB_yapi_sadirvan")
def sadirvan() -> Node:
    """Sekizgen şadırvan: havuz, musluklar, sütunlar ve kurşun saçak."""
    root = Node("ZB_yapi_sadirvan")
    zemin = merge(
        cylinder(1.62, 1.6, 0.14, 8, "tas_koyu", y0=0.0),
        cylinder(1.48, 1.46, 0.12, 8, "tas", y0=0.14),
    )
    havuz = merge(
        lathe([(1.1, 0.26), (1.12, 0.78), (1.16, 0.8), (1.16, 0.86), (0.98, 0.86), (0.96, 0.4)],
              8, "mermer", cap=False),
        cylinder(0.97, 0.97, 0.01, 8, "su", y0=0.38),
    )
    musluklar = merge(*[
        merge(tube([[0, 0.62, 0], [0.12, 0.62, 0], [0.16, 0.56, 0]], [0.02, 0.018, 0.015], 5, "altin"),
              icosphere(0.035, 0, "altin").translate(0.02, 0.62, 0))
        .rotate("y", -i * 45 - 22.5).translate(*[1.12 * math.cos(math.radians(i * 45 + 22.5)), 0,
                                                1.12 * math.sin(math.radians(i * 45 + 22.5))])
        for i in range(8)
    ]).with_material("metal")
    orta = merge(
        cylinder(0.26, 0.2, 0.9, 8, "mermer", y0=0.38),
        lathe([(0.12, 1.28), (0.34, 1.36), (0.4, 1.44), (0.38, 1.47)], 8, "mermer"),
        cylinder(0.08, 0.05, 0.25, 6, "mermer", y0=1.47),
        icosphere(0.08, 1, "altin").translate(0, 1.74, 0),
    )
    sutunlar = []
    for x, _, z in cevre_noktalari(8, 1.3, start_deg=22.5):
        sutunlar += [
            cylinder(0.1, 0.1, 0.12, 8, "tas_koyu", y0=0.26).translate(x, 0, z),
            cylinder(0.075, 0.065, 2.2, 8, "mermer", y0=0.38).translate(x, 0, z),
            cylinder(0.08, 0.12, 0.14, 8, "altin", y0=2.58).translate(x, 0, z),
        ]
    cati = merge(
        cylinder(1.45, 1.45, 0.16, 8, "fildisi", y0=2.72),
        cylinder(1.47, 1.47, 0.05, 8, "firuze", y0=2.76),
        lathe([(2.05, 2.86), (1.9, 2.98), (1.1, 3.35), (0.55, 3.55), (0.0, 3.58)], 8, "kursun"),
        cylinder(0.55, 0.5, 0.25, 8, "fildisi", y0=3.45),
        kubbe(0.52, "kursun", 8, y0=3.7),
    )
    root.add(merge(zemin, havuz, orta, *sutunlar, cati).shade_vary(0.03, 31), musluklar, alem(4.24))
    root.add(Node("water_havuz", translation=(0.0, 0.72, 0.0), scale=(0.96, 1.0, 0.96)))
    return root


# --------------------------------------------------------------------------
@model("ZB_yapi_kosk")
def kosk() -> Node:
    """Sekizgen bahçe köşkü: yükseltilmiş taban, sütunlar, sivri kemerler,
    geniş kurşun saçak ve kubbe. Ön taraf (+z) merdivenli ve açıktır."""
    root = Node("ZB_yapi_kosk")
    R = 1.35               # sütun çemberi
    yay_y = 2.35
    parcalar = [
        cylinder(1.75, 1.72, 0.45, 8, "tas", y0=0.0),
        cylinder(1.78, 1.78, 0.06, 8, "tas_koyu", y0=0.45),
        cylinder(1.6, 1.6, 0.02, 8, "mermer", y0=0.51),
    ]
    for k in range(3):     # ön merdiven
        parcalar.append(box(1.0, 0.15, 0.3, "tas_koyu", y0=0.15 * k).translate(0, 0, 1.95 - 0.28 * k))
    kenar_aci = [22.5 + 45 * i for i in range(8)]
    kose = [(R * math.cos(math.radians(a)), R * math.sin(math.radians(a))) for a in kenar_aci]
    for x, z in kose:
        parcalar += [
            cylinder(0.11, 0.11, 0.1, 8, "tas_koyu", y0=0.52).translate(x, 0, z),
            cylinder(0.08, 0.07, yay_y - 0.62, 8, "mermer", y0=0.62).translate(x, 0, z),
            cylinder(0.08, 0.13, 0.15, 8, "altin", y0=yay_y - 0.15).translate(x, 0, z),
        ]
    for i in range(8):
        (x0, z0), (x1, z1) = kose[i], kose[(i + 1) % 8]
        mx, mz = (x0 + x1) / 2, (z0 + z1) / 2
        span = math.hypot(x1 - x0, z1 - z0) - 0.16
        yon = math.degrees(math.atan2(mz, mx))
        ic = [(x, y + yay_y) for x, y in pointed_arch(span, span * 0.55, 6)]
        dis = [(x * 1.14, y * 1.12 + yay_y) for x, y in pointed_arch(span, span * 0.55, 6)]
        kenar = almasik_kemer(ic, dis, 0.16)
        kenar.append(kemer_aynasi(dis, -span / 2, span / 2, yay_y, yay_y + 0.8, 0.14, "fildisi"))
        # Ön kenar (+z yönü) açık; diğerlerinde alçak ahşap korkuluk
        if not (60 < yon < 120):
            kenar.append(box(span, 0.5, 0.06, "ahsap", y0=0.52))
            kenar.append(box(span + 0.06, 0.05, 0.1, "ahsap_koyu", y0=1.02))
        for m in kenar:
            parcalar.append(m.rotate("y", 90 - yon).translate(mx * 1.0, 0, mz * 1.0))
    parcalar += [
        cylinder(1.55, 1.55, 0.14, 8, "firuze", y0=yay_y + 0.8),
        lathe([(2.35, yay_y + 0.94), (2.2, yay_y + 1.05), (1.2, yay_y + 1.45), (0.0, yay_y + 1.6)], 8, "kursun"),
        cylinder(0.85, 0.8, 0.35, 8, "fildisi", y0=yay_y + 1.3),
        cylinder(0.87, 0.87, 0.05, 8, "mercan_kirmizi", y0=yay_y + 1.6),
        kubbe(0.82, "kursun", 10, y0=yay_y + 1.65),
    ]
    root.add(merge(*parcalar).shade_vary(0.03, 41), alem(yay_y + 2.5))
    return root
