"""Birden çok modelde kullanılan parçalar."""
from __future__ import annotations

import math

import numpy as np

from mf.mesh import Mesh, blob, cylinder, lathe, merge


def toprak_tumsek(r=0.35, h=0.08, seed=0) -> Mesh:
    """Tohum aşamasındaki bitkilerin altındaki küçük toprak tümseği."""
    m = lathe([(r, 0.0), (r * 0.8, h * 0.6), (r * 0.35, h), (0.0, h * 1.05)], seg=9, color="toprak")
    return m.jitter(r * 0.06, seed, keep_y_below=0.001).shade_vary(0.08, seed)


def yayla(p0, p1, n, sag=0.0):
    """p0'dan p1'e n noktalı, ortası `sag` kadar aşağı sarkan yol (yaprak omurgası)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    out = []
    for i in range(n):
        t = i / (n - 1)
        p = p0 + (p1 - p0) * t
        p[1] -= sag * 4 * t * (1 - t) + sag * t * t * 0.6
        out.append(p)
    return out


def taban_levha(r, h=0.04, seg=8, color="tas_koyu") -> Mesh:
    return cylinder(r, r * 0.96, h, seg, color)


def cevre_noktalari(n, r, y=0.0, start_deg=0.0):
    return [(r * math.cos(math.radians(start_deg + 360 * i / n)), y,
             r * math.sin(math.radians(start_deg + 360 * i / n))) for i in range(n)]
