"""Uzak siluetler (kesit, K18): gerçek modellerden önden (+z'den -z'ye bakış) çizilen
dikey kartlar. Kesitte ağaçlar ekranda birkaç piksel eder; binlercesi tek bir çoğaltılmış
dörtgenle çizilir. Siluetin türü, rengi ve yeri gerçek ağaçla aynıdır: yakınlaşınca
yerini gerçek modele bırakır, başka bir şey belirmez.

Çizim numpy ile yapılır (GPU yok): üçgenler ortografik izdüşümle, z tamponuyla rasterlenir.
Yaprak kartları ve kabuk, Godot'daki gibi dokularından örneklenir (yaprak: doku × köşe rengi,
alfa kesme; kabuk: doku × köşe rengi × 2). Işık yoktur (albedo); ışığı shader verir.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from .scene import Node

_DOKU_ONBELLEK: dict[str, np.ndarray] = {}


def _srgb2lin(c):
    c = np.clip(np.asarray(c, np.float64), 0.0, None)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _lin2srgb(c):
    c = np.clip(np.asarray(c, np.float64), 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def _doku(klasor: Path, ad: str):
    if ad not in _DOKU_ONBELLEK:
        p = klasor / f"{ad}.png"
        _DOKU_ONBELLEK[ad] = np.asarray(Image.open(p).convert("RGBA"), np.float64) / 255.0 if p.exists() else None
    return _DOKU_ONBELLEK[ad]


def _ucgenler(node: Node):
    """Modelin bütün üçgenleri (dönüşümsüz; ağaç ve yapı modelleri kök koordinatındadır)."""
    for n in node.walk():
        for m in n.meshes:
            s = np.asarray(n.scale, np.float64)
            t = np.asarray(n.translation, np.float64)
            V = m.V.astype(np.float64) * s + t
            yield m, V


def siluet_ciz(node: Node, dokular: Path, boy: int = 256):
    """Modelin önden görünüşü: (rgba boy×boy, dünya ölçüsü S, dip y0).
    Hücre x ∈ [-S/2, S/2], y ∈ [y0, y0 + S] aralığını kaplar."""
    parcalar = list(_ucgenler(node))
    Vt = np.vstack([V for _, V in parcalar])
    y0 = float(Vt[:, 1].min())
    S = float(max(2 * np.abs(Vt[:, 0]).max(), Vt[:, 1].max() - y0) * 1.04)
    renk = np.zeros((boy, boy, 3))
    alfa = np.zeros((boy, boy))
    derin = np.full((boy, boy), -1e9)
    for m, V in parcalar:
        px = (V[:, 0] / S + 0.5) * boy
        py = (1.0 - (V[:, 1] - y0) / S) * boy
        pz = V[:, 2]
        malz = m.material
        doku = None
        carpan = 1.0
        if malz.startswith("yaprak_") or malz.startswith("kabuk"):
            doku = _doku(dokular, malz)
            if malz.startswith("kabuk"):
                carpan = 2.0
        kose = m.CV if m.CV is not None else None
        for fi, f in enumerate(m.F):
            x = px[f]
            y = py[f]
            x0, x1 = int(max(np.floor(x.min()), 0)), int(min(np.ceil(x.max()), boy - 1))
            y0p, y1p = int(max(np.floor(y.min()), 0)), int(min(np.ceil(y.max()), boy - 1))
            if x1 < x0 or y1p < y0p:
                continue
            gy, gx = np.mgrid[y0p:y1p + 1, x0:x1 + 1] + 0.5
            d = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
            if abs(d) < 1e-12:
                continue
            l0 = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / d
            l1 = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / d
            l2 = 1 - l0 - l1
            ic = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
            if not ic.any():
                continue
            z = l0 * pz[f[0]] + l1 * pz[f[1]] + l2 * pz[f[2]]
            if kose is not None:
                c = (l0[..., None] * kose[f[0]] + l1[..., None] * kose[f[1]] + l2[..., None] * kose[f[2]])
            else:
                c = np.broadcast_to(m.C[fi], l0.shape + (3,))
            c = _srgb2lin(c)
            a = np.ones(l0.shape)
            if doku is not None and m.UV is not None:
                uv = l0[..., None] * m.UV[f[0]] + l1[..., None] * m.UV[f[1]] + l2[..., None] * m.UV[f[2]]
                h, w = doku.shape[:2]
                tu = np.clip((uv[..., 0] % 1.0) * w, 0, w - 1).astype(int)
                tv = np.clip((uv[..., 1] % 1.0) * h, 0, h - 1).astype(int)
                t = doku[tv, tu]
                c = c * _srgb2lin(t[..., :3]) * carpan
                a = t[..., 3]
            ic &= a > 0.45
            yy, xx = np.nonzero(ic)
            yy_g, xx_g = yy + y0p, xx + x0
            onde = z[yy, xx] > derin[yy_g, xx_g]
            yy, xx, yy_g, xx_g = yy[onde], xx[onde], yy_g[onde], xx_g[onde]
            derin[yy_g, xx_g] = z[yy, xx]
            renk[yy_g, xx_g] = c[yy, xx]
            alfa[yy_g, xx_g] = 1.0
    return renk, alfa, S, y0


def _genislet(renk, alfa, adim=4):
    """Saydam piksellere komşu renk taşınır: mipmap'te koyu kenar oluşmasın."""
    r = renk.copy()
    a = alfa > 0
    for _ in range(adim):
        top = np.zeros_like(r)
        say = np.zeros(a.shape)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ka = np.roll(a, (dy, dx), (0, 1))
            top += np.roll(r, (dy, dx), (0, 1)) * ka[..., None]
            say += ka
        yeni = (~a) & (say > 0)
        r[yeni] = top[yeni] / say[yeni][:, None]
        a = a | yeni
    return r


def siluet_atlasi(modeller: list, dokular: Path, hucre: int = 128, sutun: int = 4):
    """modeller: [(ad, Node)]. Döner: (RGBA atlas Image, meta {ad: [hücre, S, y0]})."""
    satir = (len(modeller) + sutun - 1) // sutun
    atlas = np.zeros((satir * hucre, sutun * hucre, 4))
    meta = {}
    for i, (ad, node) in enumerate(modeller):
        renk, alfa, S, y0 = siluet_ciz(node, dokular, hucre * 2)
        renk = _genislet(renk, alfa)
        # 2× çizim, alfa ağırlıklı küçültme
        r = renk.reshape(hucre, 2, hucre, 2, 3).mean((1, 3))
        a = alfa.reshape(hucre, 2, hucre, 2).mean((1, 3))
        oy, ox = (i // sutun) * hucre, (i % sutun) * hucre
        atlas[oy:oy + hucre, ox:ox + hucre, :3] = _lin2srgb(r)
        atlas[oy:oy + hucre, ox:ox + hucre, 3] = a
        meta[ad] = [i, round(S, 3), round(y0, 3)]
    img = Image.fromarray(np.round(atlas * 255).astype(np.uint8), "RGBA")
    return img, meta
