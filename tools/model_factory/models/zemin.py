"""Başlangıç adası: bahçenin kurulduğu, gökte süzülen toprak ada.

Asset listesinde ayrı satırı yoktur (rapor §5e "Arazi/ada"). Üst yüzey
hafif kubbeli çimendir; yanlarda toprak katmanları, altta kaya sivrilir.
Üst yüzey y=0 civarındadır; bahçe yerleşimi bu düzlemde yapılır.
"""
from __future__ import annotations

import math

import numpy as np

from mf.mesh import blob, lathe, merge
from mf.palette import renk
from mf.scene import Node

from . import model

YARICAP = 6.0


def _ada_govdesi(seed=7):
    prof = [(0.0, -3.7), (0.9, -3.4), (2.1, -2.8), (3.3, -2.0), (4.4, -1.2), (5.3, -0.55),
            (5.8, -0.2), (6.0, -0.04), (5.7, 0.04), (4.2, 0.08), (2.2, 0.11), (0.0, 0.12)]
    m = lathe(prof, seg=28, color="cimen", cap=False)
    # Kenarı düzensizleştir: her köşe açısına göre yarıçap çarpanı (aynı açıdaki
    # köşeler aynı çarpanı alır, yüzey yırtılmaz).
    rng = np.random.default_rng(seed)
    harm = [(k, rng.uniform(0.02, 0.06) / k ** 0.5, rng.uniform(0, 2 * math.pi)) for k in (2, 3, 5, 7)]
    V = m.V.astype(np.float64)
    ang = np.arctan2(V[:, 2], V[:, 0])
    f = 1.0 + sum(a * np.cos(k * ang + p) for k, a, p in harm)
    V[:, 0] *= f
    V[:, 2] *= f
    m.V = V.astype(np.float32)
    # Yan yüzlerin köşelerini oynat (üst yüzeyi düz bırak)
    m = m.jitter(0.14, seed + 1, keep_y_below=None)
    top = m.V[:, 1] > -0.03
    m.V[top, 1] = np.clip(m.V[top, 1], 0.0, 0.14)
    # Katman renkleri: yüz merkezinin yüksekliğine göre
    cy = m.V[m.F][:, :, 1].mean(axis=1)
    renkler = np.empty((len(m.F), 3), dtype=np.float32)
    for i, y in enumerate(cy):
        if y > -0.02:
            ad = "cimen" if (i * 7919) % 5 else "cimen_koyu"
        elif y > -0.4:
            ad = "cimen_koyu"
        elif y > -1.4:
            ad = "toprak"
        elif y > -2.5:
            ad = "toprak_koyu"
        else:
            ad = "kaya"
        renkler[i] = renk(ad)
    m.C = renkler
    return m.shade_vary(0.05, seed + 2)


@model("ZB_zemin_ada")
def ada() -> Node:
    root = Node("ZB_zemin_ada")
    kayalar = []
    rng = np.random.default_rng(3)
    for i in range(7):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(4.6, 5.6)
        s = rng.uniform(0.25, 0.5)
        kayalar.append(blob(s, "kaya", seed=100 + i, subdiv=1, squash=0.6).translate(
            r * math.cos(a), s * 0.25, r * math.sin(a)))
    for i in range(4):  # altta sarkan kayalar
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(1.0, 2.6)
        s = rng.uniform(0.35, 0.7)
        kayalar.append(blob(s, "kaya", seed=200 + i, subdiv=1, squash=1.4).translate(
            r * math.cos(a), -2.9 + r * 0.35, r * math.sin(a)))
    root.add(_ada_govdesi(), merge(*kayalar))
    return root
