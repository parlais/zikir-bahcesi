"""Prosedürel dokular: yaprak kümesi atlasları ve kabuk dokusu (K15).

Yaprak atlası 2×2 hücredir. Her hücrede bir ince dal ve üstünde yapraklar
vardır; dalın dibi hücrenin alt ortasındadır. Ağaç üreteci (mf/agac.py) kartın
dibini dal üstündeki bağlantı noktasına koyar.

Kabuk dokusu yatayda ve dikeyde döşenebilir. Renk kabaca griye yakındır; türün
rengi köşe renginden gelir (shader ikisini çarpar). Yanında normal haritası da
yazılır.

Bütün dokular deterministiktir: aynı kod aynı PNG'yi üretir.
"""
from __future__ import annotations

import colorsys
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

from .palette import renk

HUCRE = 512          # atlas hücresi (piksel)
SS = 3               # süper örnekleme: çizim HUCRE*SS'de yapılır, sonra küçültülür


# --------------------------------------------------------------------------
# Yaprak kümesi
# --------------------------------------------------------------------------

@dataclass
class YaprakTuru:
    ad: str
    renkler: list                  # yaprak renkleri (palet adı ya da sRGB 0-255)
    boy: tuple = (0.15, 0.22)      # yaprak boyu, hücre yüksekliğine oranla
    en: float = 0.42               # en / boy
    uc: float = 1.1                # uca doğru sivrilme (büyük: sivri uç)
    dip: float = 0.7               # dibe doğru daralma (büyük: ince dip)
    testere: float = 0.0           # kenar dişi genliği (en'e oranla)
    dis_sayi: int = 18             # kenar dişi sayısı
    sayi: int = 26                 # hücre başına yaprak
    yan_dal: int = 2               # ana dala çıkan yan dal sayısı
    yan_aci: tuple = (40.0, 65.0)  # yan dalın ana dala göre açısı
    yan_boy: tuple = (0.36, 0.5)   # yan dal boyu, hücreye oranla
    aci: tuple = (35.0, 70.0)      # yaprağın dala göre açısı
    sap: float = 0.08              # yaprak sapı, boya oranla
    dal_renk: tuple = (96, 78, 52)
    parlak: float = 0.10           # orta damar ve damarların aydınlığı
    kivrim: float = 0.12           # orta damarın eğriliği
    renk_oynama: float = 0.06      # yapraktan yaprağa ton ve parlaklık farkı
    sarimsi_uc: float = 0.05       # uç tarafın sarıya kayması
    tohum: int = 0
    bicim: str = "yumurta"         # "yumurta" (orta damarlı) ya da "el" (beş loplu: üzüm, çınar)
    lop_us: float = 1.3            # el biçimli yaprakta lop uçlarının sivriliği (küçük: sivri)
    lop_derinlik: float = 0.24     # el biçimli yaprakta girintilerin derinliği
    dis_gucu: float = 0.06         # el biçimli yaprakta kenar dişleri
    kenar_isik: tuple | None = None  # kenar ve uçta ışıltı rengi (Tûbâ: altın-beyaz)
    kenar_isik_gucu: float = 0.0


def _rgb01(c):
    if isinstance(c, str):
        c = renk(c)
    c = np.asarray(c, np.float32)
    return c / 255.0 if c.max() > 1.0 else c


def _oynat(c, rng, miktar):
    h, l, s = colorsys.rgb_to_hls(*c)
    h = (h + rng.uniform(-miktar, miktar) * 0.25) % 1.0
    l = float(np.clip(l * (1 + rng.uniform(-miktar, miktar) * 2.0), 0, 1))
    s = float(np.clip(s * (1 + rng.uniform(-miktar, miktar)), 0, 1))
    return np.array(colorsys.hls_to_rgb(h, l, s), np.float32)


def _ustune(tuval, x0, y0, rgb, a):
    """rgb (h,w,3), a (h,w) katmanını tuvalin (x0, y0) köşesine düz alfa ile bindirir."""
    h, w = a.shape
    H, W = tuval.shape[:2]
    x1, y1 = min(W, x0 + w), min(H, y0 + h)
    xs, ys = max(0, x0), max(0, y0)
    if x1 <= xs or y1 <= ys:
        return
    a = a[ys - y0:y1 - y0, xs - x0:x1 - x0, None]
    rgb = rgb[ys - y0:y1 - y0, xs - x0:x1 - x0]
    t = tuval[ys:y1, xs:x1]
    t[..., :3] = rgb * a + t[..., :3] * (1 - a)
    t[..., 3:] = a + t[..., 3:] * (1 - a)


def _dal_ciz(tuval, noktalar, yaricaplar, renk_):
    """Kalınlığı değişen dal: noktalar arası parçalar, silindir gibi ortası aydınlık."""
    renk_ = _rgb01(renk_)
    P = np.asarray(noktalar, np.float64)
    R = np.asarray(yaricaplar, np.float64)
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]
        r = max(R[i], R[i + 1])
        x0, y0 = np.floor(np.minimum(a, b) - r - 2).astype(int)
        x1, y1 = np.ceil(np.maximum(a, b) + r + 2).astype(int)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        p = np.stack([xx, yy], -1).astype(np.float64)
        ab = b - a
        t = np.clip(((p - a) @ ab) / max(ab @ ab, 1e-9), 0, 1)
        d = np.linalg.norm(p - (a + t[..., None] * ab), axis=-1)
        rr = R[i] + (R[i + 1] - R[i]) * t
        q = np.clip(d / np.maximum(rr, 1e-6), 0, 1)
        alfa = np.clip((rr - d) + 0.5, 0, 1)
        golge = 1.0 - 0.45 * q ** 2
        _ustune(tuval, x0, y0, renk_ * golge[..., None], alfa)


def _uzum_yapragi_ciz(tuval, taban, yon, boy, tur: YaprakTuru, rng):
    """Beş loplu, dişli üzüm yaprağı: sapın bağlandığı yerde derin bir girinti, merkezden
    loplara uzanan beş ana damar."""
    a = np.asarray(yon, np.float64)
    a /= np.linalg.norm(a)
    p = np.array([-a[1], a[0]])
    R = boy * 0.5
    merkez = np.asarray(taban, np.float64) + a * R * 0.95
    k0 = np.floor(merkez - R * 1.1 - 3).astype(int)
    k1 = np.ceil(merkez + R * 1.1 + 3).astype(int)
    yy, xx = np.mgrid[k0[1]:k1[1], k0[0]:k1[0]]
    d = np.stack([xx, yy], -1).astype(np.float64) - merkez
    u, v = d @ a, d @ p
    r = np.hypot(u, v)
    th = np.arctan2(v, u)                                   # 0 yaprağın ucu
    lop = 1 - np.abs(np.sin(2.5 * th)) ** tur.lop_us        # lop uçları, yuvarlak girintiler
    dis = 1 - tur.dis_gucu * np.abs(np.sin(th * 24)) ** 2   # kenar dişleri
    sinir = R * (1 - tur.lop_derinlik + tur.lop_derinlik * lop) * (0.8 + 0.2 * np.cos(th)) * dis
    sinir = sinir * (1 - 0.45 * np.exp(-((np.abs(th) - np.pi) / 0.32) ** 2))   # sapın girdiği derin girinti
    alfa = np.clip(sinir - r + 0.5, 0, 1)
    if not alfa.any():
        return
    c = _oynat(_rgb01(tur.renkler[rng.integers(len(tur.renkler))]), rng, tur.renk_oynama)
    damar = 0.0
    for aci in (0.0, 1.2566, -1.2566, 2.513, -2.513):
        fark = np.abs(np.angle(np.exp(1j * (th - aci))))
        damar = np.maximum(damar, np.clip(1 - fark * r / (R * 0.035), 0, 1) * (r < sinir * 0.9))
    isik = 0.88 + 0.12 * np.clip(r / R, 0, 1) - 0.1 * np.clip(r / np.maximum(sinir, 1e-6) - 0.85, 0, 1) / 0.15
    rgb = np.clip(c[None, None] * (isik * (1 + tur.parlak * 1.5 * damar))[..., None], 0, 1)
    _ustune(tuval, k0[0], k0[1], rgb, alfa)


def _yaprak_ciz(tuval, taban, yon, boy, tur: YaprakTuru, rng):
    """Tek yaprak: orta damar boyunca eni değişen, hafif eğri, katlanmış görünüşlü."""
    if tur.bicim in ("el", "uzum"):
        return _uzum_yapragi_ciz(tuval, taban, yon, boy, tur, rng)
    a = np.asarray(yon, np.float64)
    a /= np.linalg.norm(a)
    p = np.array([-a[1], a[0]])
    taban = np.asarray(taban, np.float64)
    en = boy * tur.en * rng.uniform(0.85, 1.12)
    bukum = tur.kivrim * rng.uniform(-1, 1)
    # Sınır kutusu
    s = np.linspace(0, 1, 24)
    merkez = taban[None] + np.outer(s * boy, a) + np.outer(bukum * boy * s ** 2, p)
    k0 = np.floor(merkez.min(0) - en - 3).astype(int)
    k1 = np.ceil(merkez.max(0) + en + 3).astype(int)
    yy, xx = np.mgrid[k0[1]:k1[1], k0[0]:k1[0]]
    d = np.stack([xx, yy], -1).astype(np.float64) - taban
    s = (d @ a) / boy
    sc = np.clip(s, 0, 1)
    yan = d @ p - bukum * boy * sc ** 2
    # Yarı en: dipte ve uçta daralır, en geniş yer ortanın biraz altında
    g = np.clip(sc, 1e-4, 1 - 1e-4)
    w = g ** tur.dip * (1 - g) ** tur.uc
    w /= (tur.dip / (tur.dip + tur.uc)) ** tur.dip * (tur.uc / (tur.dip + tur.uc)) ** tur.uc
    w = w * en * 0.5
    if tur.testere > 0:
        w = w * (1 + tur.testere * (np.abs(np.sin(sc * tur.dis_sayi * math.pi)) - 0.5))
    q = yan / np.maximum(w, 1e-6)
    ic = (np.abs(yan) - w)
    alfa = np.clip(0.5 - ic, 0, 1) * ((s >= 0) & (s <= 1))
    if not alfa.any():
        return
    # Renk
    c = _oynat(_rgb01(tur.renkler[rng.integers(len(tur.renkler))]), rng, tur.renk_oynama)
    sari = np.array([0.86, 0.84, 0.32], np.float32)
    uc_ton = np.clip((sc - 0.55) / 0.45, 0, 1)[..., None] * tur.sarimsi_uc
    rgb = c * (1 - uc_ton) + sari * uc_ton
    isik = 0.84 + 0.2 * np.sin(np.clip(sc, 0, 1) * math.pi) ** 0.6            # dipte koyu
    kat = np.where(q > 0, 1.05, 0.9) - 0.06 * np.abs(q)                         # orta damardan katlanma
    kenar = 1.0 - 0.22 * np.clip((np.abs(q) - 0.7) / 0.3, 0, 1)
    damar_orta = np.clip(1 - np.abs(yan) / (0.9 + boy * 0.012), 0, 1) * (sc < 0.97)
    faz = sc * 7.0 - np.abs(q) * 0.9
    damar_yan = np.clip(1 - np.abs(faz - np.round(faz)) / 0.07, 0, 1) * (np.abs(q) < 0.85) * (sc > 0.08)
    parlak = 1 + tur.parlak * (1.6 * damar_orta + 0.6 * damar_yan)
    if tur.kenar_isik is not None:
        kenar = np.ones_like(kenar)                             # ışıltılı kenar koyulaşmaz
    rgb = np.clip(rgb * (isik * kat * kenar * parlak)[..., None], 0, 1)
    if tur.kenar_isik is not None:
        # Kenara ve uca doğru altın-beyaz ışıltı (Tûbâ: nurlu nitelik); damarlar da hafif ışır
        e = np.clip((np.abs(q) - 0.74) / 0.26, 0, 1) ** 1.8 + 0.7 * np.clip((sc - 0.84) / 0.16, 0, 1) ** 2
        e = np.clip(e * tur.kenar_isik_gucu + 0.25 * tur.kenar_isik_gucu * damar_orta, 0, 1)[..., None]
        rgb = rgb * (1 - e) + _rgb01(tur.kenar_isik) * e
    _ustune(tuval, k0[0], k0[1], rgb, alfa)


def _dal_yolu(bas, yon, uzunluk, bukum, n, rng):
    """Hafif kıvrılan dal yolu (piksel)."""
    P = [np.asarray(bas, np.float64)]
    d = np.asarray(yon, np.float64) / np.linalg.norm(yon)
    for i in range(n):
        aci = bukum / n + rng.normal(0, 0.05)
        c, s_ = math.cos(aci), math.sin(aci)
        d = np.array([c * d[0] - s_ * d[1], s_ * d[0] + c * d[1]])
        P.append(P[-1] + d * uzunluk / n)
    return np.array(P)


def _hucre(tur: YaprakTuru, tohum: int):
    """Bir yaprak kümesi (RGBA, 0-1, süper örneklenmiş) ve dalın dibinin pikseli.
    Tuval hücreden geniştir; atlas kümeyi hücreye sığacak kadar küçültür."""
    rng = np.random.default_rng(tohum)
    N = HUCRE * SS
    H, W = int(N * 1.3), int(N * 1.7)
    tuval = np.zeros((H, W, 4), np.float32)
    dip = np.array([W * 0.5, H - 2.0])
    # Ana dal: alttan yukarı (görüntüde y aşağı)
    ana = _dal_yolu(dip, (rng.uniform(-0.15, 0.15), -1.0),
                    N * rng.uniform(0.62, 0.72), rng.uniform(-0.5, 0.5), 10, rng)
    dallar = [(ana, N * 0.012, N * 0.004)]
    for j in range(tur.yan_dal):
        i = int(len(ana) * rng.uniform(0.2, 0.62))
        t = ana[min(i + 1, len(ana) - 1)] - ana[i]
        taraf = 1 if j % 2 == 0 else -1
        aci = math.radians(rng.uniform(*tur.yan_aci)) * taraf
        yon = np.array([t[0] * math.cos(aci) - t[1] * math.sin(aci), t[0] * math.sin(aci) + t[1] * math.cos(aci)])
        yol = _dal_yolu(ana[i], yon, N * rng.uniform(*tur.yan_boy), -taraf * rng.uniform(0.1, 0.5), 7, rng)
        dallar.append((yol, N * 0.007, N * 0.003))
    for yol, r0, r1 in dallar:
        _dal_ciz(tuval, yol, np.linspace(r0, r1, len(yol)), tur.dal_renk)
    # Yapraklar dal boyunca, dala yakın olanlar önce çizilir ki uçtakiler üste gelsin
    yapraklar = []
    agirlik = np.array([1.0] + [0.45] * tur.yan_dal)
    for k in range(tur.sayi):
        di = rng.choice(len(dallar), p=agirlik / agirlik.sum())
        yol = dallar[di][0]
        t = rng.uniform(0.18, 1.0) ** 0.8
        i = min(int(t * (len(yol) - 1)), len(yol) - 2)
        f = t * (len(yol) - 1) - i
        nokta = yol[i] * (1 - f) + yol[i + 1] * f
        tan = yol[i + 1] - yol[i]
        tan /= np.linalg.norm(tan)
        taraf = 1 if k % 2 == 0 else -1
        aci = math.radians(rng.uniform(*tur.aci)) * taraf
        yon = np.array([tan[0] * math.cos(aci) - tan[1] * math.sin(aci), tan[0] * math.sin(aci) + tan[1] * math.cos(aci)])
        boy = N * rng.uniform(*tur.boy) * (1.0 - 0.3 * t)
        yapraklar.append((t, nokta, yon, boy))
    # Uç yaprakları
    for yol, _, _ in dallar:
        tan = yol[-1] - yol[-2]
        yapraklar.append((1.1, yol[-1], tan / np.linalg.norm(tan), N * tur.boy[1] * 0.8))
    yapraklar.sort(key=lambda y: y[0] + rng.uniform(0, 0.3))
    for t, nokta, yon, boy in yapraklar:
        sap = yon * boy * tur.sap
        _dal_ciz(tuval, [nokta, nokta + sap], [N * 0.0025, N * 0.002], tur.dal_renk)
        _yaprak_ciz(tuval, nokta + sap, yon, boy, tur, rng)
    return tuval, dip


def _kucult(t: np.ndarray, k: int) -> np.ndarray:
    """Süper örneklenmiş tuvali k kat küçültür (alfa ağırlıklı ortalama)."""
    H, W = t.shape[:2]
    t = t.reshape(H // k, k, W // k, k, 4)
    a = t[..., 3].mean(axis=(1, 3))
    rgb = (t[..., :3] * t[..., 3:]).sum(axis=(1, 3)) / np.maximum(t[..., 3].sum(axis=(1, 3)), 1e-6)[..., None]
    return np.concatenate([rgb, a[..., None]], -1)


def _renk_tasir(t: np.ndarray, adim: int = 8) -> np.ndarray:
    """Saydam piksellere komşu yaprakların rengini yayar: mipmap'te kenarlar
    siyaha ya da beyaza kaçmaz (alfa değişmez)."""
    rgb, a = t[..., :3].copy(), t[..., 3]
    dolu = (a > 0.5).astype(np.float32)
    toplam, agirlik = rgb * dolu[..., None], dolu.copy()
    for i in range(adim):
        r = 2 ** i
        for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r)):
            toplam = toplam + np.roll(toplam, (dy, dx), (0, 1)) * 0.5
            agirlik = agirlik + np.roll(agirlik, (dy, dx), (0, 1)) * 0.5
    ort = toplam / np.maximum(agirlik, 1e-6)[..., None]
    rgb = np.where((a > 0.5)[..., None], rgb, ort)
    return np.concatenate([rgb, a[..., None]], -1)


def _sigdir(tuval, dip, pay=0.035):
    """Kümeyi hücreye sığdırır: dalın dibi hücrenin alt ortasına gelir, yapraklar
    kenarlarda kesilmez. Önceden çarpılmış alfa ile küçültülür."""
    a = tuval[..., 3]
    ys, xs = np.nonzero(a > 0.01)
    yari = max(dip[0] - xs.min(), xs.max() - dip[0]) + 2
    boy = dip[1] - ys.min() + 2
    s = min(HUCRE * (0.5 - pay) / yari, HUCRE * (1 - pay) / boy)
    H, W = a.shape
    yeni = (max(1, round(W * s)), max(1, round(H * s)))
    kanallar = []
    for k in range(4):
        v = tuval[..., k] * (a if k < 3 else 1.0)
        kanallar.append(np.asarray(Image.fromarray(v.astype(np.float32), "F").resize(yeni, Image.BOX)))
    rgb = np.stack(kanallar[:3], -1) / np.maximum(kanallar[3], 1e-6)[..., None]
    kucuk = np.concatenate([rgb, kanallar[3][..., None]], -1)
    hucre = np.zeros((HUCRE, HUCRE, 4), np.float32)
    x0 = int(round(HUCRE * 0.5 - dip[0] * s))
    y0 = int(round(HUCRE - 1 - dip[1] * s))
    hy, hx = kucuk.shape[:2]
    xa, ya = max(0, x0), max(0, y0)
    xb, yb = min(HUCRE, x0 + hx), min(HUCRE, y0 + hy)
    hucre[ya:yb, xa:xb] = kucuk[ya - y0:yb - y0, xa - x0:xb - x0]
    return np.clip(hucre, 0, 1)


def yaprak_atlasi(tur: YaprakTuru) -> Image.Image:
    """2×2 hücreli yaprak kümesi atlası (RGBA, 2*HUCRE kare)."""
    atlas = np.zeros((2 * HUCRE, 2 * HUCRE, 4), np.float32)
    for j in range(2):
        for i in range(2):
            h = _sigdir(*_hucre(tur, tur.tohum * 10 + j * 2 + i))
            atlas[j * HUCRE:(j + 1) * HUCRE, i * HUCRE:(i + 1) * HUCRE] = h
    atlas = _renk_tasir(atlas)
    return Image.fromarray(np.round(np.clip(atlas, 0, 1) * 255).astype(np.uint8), "RGBA")


def atlas_uv(hucre: int) -> tuple[float, float, float, float]:
    """Hücrenin UV dikdörtgeni (u0, v0, u1, v1); v0 hücrenin üstü, v1 altı (dalın dibi)."""
    i, j = hucre % 2, hucre // 2
    kenar = 1.0 / (2 * HUCRE)
    return i * 0.5 + kenar, j * 0.5 + kenar, (i + 1) * 0.5 - kenar, (j + 1) * 0.5 - kenar


# --------------------------------------------------------------------------
# Tek yaprak atlası: filizler (a2) için her türün tek bir yaprağı
# --------------------------------------------------------------------------

TEK_YAPRAK: dict[str, YaprakTuru] = {}      # ad -> tür (sıra atlas hücresini verir)
TEK_HUCRE = 256
TEK_SUTUN = 4


def tek_yaprak(t: YaprakTuru) -> YaprakTuru:
    TEK_YAPRAK[t.ad] = t
    return t


def tek_yaprak_uv(ad: str) -> tuple[float, float, float, float]:
    """(u0, v0, u1, v1): v0 yaprağın ucu (hücrenin üstü), v1 dibi."""
    i = list(TEK_YAPRAK).index(ad)
    x, y = i % TEK_SUTUN, i // TEK_SUTUN
    k = 1.0 / TEK_SUTUN
    kenar = 1.0 / (TEK_HUCRE * TEK_SUTUN)
    return x * k + kenar, y * k + kenar, (x + 1) * k - kenar, (y + 1) * k - kenar


def tek_yaprak_atlasi() -> Image.Image:
    """Her türün tek yaprağı kendi hücresinde: dibi hücrenin alt ortasında, ucu yukarıda."""
    N = TEK_HUCRE * SS
    satir = (len(TEK_YAPRAK) + TEK_SUTUN - 1) // TEK_SUTUN
    atlas = np.zeros((TEK_SUTUN * TEK_HUCRE, TEK_SUTUN * TEK_HUCRE, 4), np.float32)
    for i, t in enumerate(TEK_YAPRAK.values()):
        rng = np.random.default_rng(t.tohum * 7 + 3)
        tuval = np.zeros((N, N, 4), np.float32)
        boy = N * 0.94
        if t.bicim in ("el", "uzum"):
            boy = N * 0.96
        tek = YaprakTuru(**{**t.__dict__, "kivrim": 0.0, "renk_oynama": 0.0})
        _yaprak_ciz(tuval, (N * 0.5, N - 2.0), (0.0, -1.0), boy, tek, rng)
        x, y = i % TEK_SUTUN, i // TEK_SUTUN
        atlas[y * TEK_HUCRE:(y + 1) * TEK_HUCRE, x * TEK_HUCRE:(x + 1) * TEK_HUCRE] = _kucult(tuval, SS)
    atlas = _renk_tasir(atlas)
    return Image.fromarray(np.round(np.clip(atlas, 0, 1) * 255).astype(np.uint8), "RGBA")


# --------------------------------------------------------------------------
# Tüysü (pinnat) yaprak: hurma
# --------------------------------------------------------------------------

def tuysu_yaprak_atlasi(tur: YaprakTuru, sayi=4, en=256, boy=1024) -> Image.Image:
    """Yan yana `sayi` tüysü yaprak (her biri en×boy): ortada orta damar (rachis),
    iki yanda uca doğru eğik dizilmiş uzun, dar yaprakçıklar. Uç görüntünün üstündedir."""
    atlas = np.zeros((boy, en * sayi, 4), np.float32)
    for k in range(sayi):
        rng = np.random.default_rng(tur.tohum * 10 + k)
        W, H = en * SS, boy * SS
        tuval = np.zeros((H, W, 4), np.float32)
        x0 = W * 0.5
        _dal_ciz(tuval, [(x0, H - 1), (x0, H * 0.35), (x0, H * 0.01)], [W * 0.028, W * 0.016, W * 0.006],
                 tur.dal_renk)
        n = 42
        yapraklar = []
        for i in range(n):
            t = 0.05 + 0.94 * i / (n - 1) + rng.uniform(-0.004, 0.004)
            y = H * (1 - t)
            uzun = W * 0.54 * math.sin(math.pi * min(1.0, 0.1 + 0.9 * t)) ** 0.6 * rng.uniform(0.85, 1.05)
            if t > 0.9:
                uzun *= 1 - (t - 0.9) / 0.1 * 0.6
            for taraf in (-1, 1):
                if rng.random() < 0.06:                     # arada eksik yaprakçık: doğal düzensizlik
                    continue
                aci = math.radians(rng.uniform(*tur.aci))
                yon = (taraf * math.sin(aci), -math.cos(aci))
                yapraklar.append((rng.random(), (x0 + taraf * W * 0.01, y), yon, uzun))
        yapraklar.sort(key=lambda v: v[0])
        for _, nokta, yon, uzun in yapraklar:
            _yaprak_ciz(tuval, nokta, yon, uzun, tur, rng)
        kucuk = _kucult(tuval, SS)
        atlas[:, k * en:(k + 1) * en] = kucuk
    atlas = _renk_tasir(atlas)
    return Image.fromarray(np.round(np.clip(atlas, 0, 1) * 255).astype(np.uint8), "RGBA")


def muz_yapragi_atlasi(sayi=4, en=256, boy=1024, tohum=9) -> Image.Image:
    """Yan yana `sayi` muz yaprağı: dipte sap, kalın orta damar, ona dik ve uca doğru
    hafif eğik paralel damarlar; kenardan damar boyunca içe uzanan birkaç yırtık."""
    atlas = np.zeros((boy, en * sayi, 4), np.float32)
    yesil = [np.array(c, np.float32) / 255 for c in ((88, 156, 64), (100, 168, 70), (80, 146, 60), (108, 170, 72))]
    for k in range(sayi):
        rng = np.random.default_rng(tohum * 10 + k)
        W, H = en * SS, boy * SS
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        t = 1 - y / H                                        # 0 dip, 1 uç
        dx = x - W * 0.5
        sap = 0.1
        g = np.clip((t - sap) / (1 - sap), 0, 1)
        yari = W * 0.47 * np.clip(np.sin(np.pi * np.clip(g * 0.97 + 0.03, 0, 1)), 0, 1) ** 0.3
        yari = yari * (1 - 0.35 * np.clip((g - 0.85) / 0.15, 0, 1) ** 2) * np.clip(g / 0.07, 0, 1) ** 0.6
        q = np.abs(dx) / np.maximum(yari, 1e-3)
        damar_en = W * (0.045 * (1 - 0.75 * t) + 0.008)
        orta = np.abs(dx) < damar_en
        ic = ((q <= 1) & (t > sap) & (t < 0.995)) | (orta & (t < 0.985))
        # Yan damarlar: orta damardan dışa, uca doğru hafif eğik
        faz = (t * H - np.abs(dx) * 0.35) / (H * 0.011)
        damar = np.clip(1 - np.abs(faz - np.round(faz)) / 0.12, 0, 1)
        # Yırtıklar: her yanda birkaç damar boyunca kenardan içe
        yirtik = np.zeros_like(t, bool)
        for taraf in (-1, 1):
            for _ in range(int(rng.integers(3, 6))):
                f0 = rng.uniform(0.18, 0.92) * H / (H * 0.011)
                derin = rng.uniform(0.25, 0.8)
                acik = rng.uniform(0.18, 0.4)
                bolge = (np.sign(dx) == taraf) & (q > 1 - derin)
                gen = acik * np.clip((q - (1 - derin)) / derin, 0, 1)
                yirtik |= bolge & (np.abs(faz - f0) < gen)
        alfa = (ic & ~yirtik).astype(np.float32)
        c = yesil[k % len(yesil)]
        l = 0.86 + 0.14 * np.clip(q, 0, 1) - 0.06 * np.clip(1 - q, 0, 1) ** 4
        l = l * (0.92 + 0.08 * np.sin(faz * np.pi))          # damarlar arası bantlar
        l = l + 0.08 * damar * (q < 0.97)
        rgb = c[None, None] * l[..., None]
        uc = np.clip((t - 0.7) / 0.3, 0, 1)[..., None] * 0.06
        rgb = rgb * (1 - uc) + np.array([0.8, 0.82, 0.35]) * uc
        rib = np.array([0.72, 0.78, 0.44], np.float32)
        rgb = np.where(orta[..., None], rib[None, None] * (0.9 + 0.1 * (1 - np.abs(dx) / np.maximum(damar_en, 1)))[..., None], rgb)
        tuval = np.concatenate([np.clip(rgb, 0, 1), alfa[..., None]], -1)
        atlas[:, k * en:(k + 1) * en] = _kucult(tuval, SS)
    atlas = _renk_tasir(atlas)
    return Image.fromarray(np.round(np.clip(atlas, 0, 1) * 255).astype(np.uint8), "RGBA")


def muz_govdesi(n=512, tohum=14):
    """Muzun yalancı gövdesi: dikey lifler, üst üste binen kın kenarları ve koyu lekeler."""
    rng = np.random.default_rng(tohum)
    lif = _fbm(n, 64, 2, rng, 4)
    kin = _fbm(n, 3, 1, rng, 3)
    kenar = np.abs(((np.arange(n)[None] / n * 3 + kin * 1.2) % 1.0) - 0.5) * 2
    leke = np.clip((_fbm(n, 8, 12, rng, 4) - 0.66) / 0.1, 0, 1)
    l = 0.55 + 0.14 * (lif - 0.5) - 0.12 * np.clip(1 - kenar / 0.08, 0, 1)
    rgb = np.stack([l * 0.95, l * 1.02, l * 0.78], -1)
    rgb = rgb * (1 - 0.45 * leke[..., None]) + np.array([0.32, 0.2, 0.16]) * 0.45 * leke[..., None]
    h = lif * 0.3 + np.clip(kenar / 0.1, 0, 1) * 0.5
    guc = 4.0
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * guc
    dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * guc
    nrm = np.stack([-dx, dy, np.ones_like(h)], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    return (Image.fromarray(np.round(np.clip(rgb, 0, 1) * 255).astype(np.uint8), "RGB"),
            Image.fromarray(np.round((nrm * 0.5 + 0.5) * 255).astype(np.uint8), "RGB"))


def serit_uv(k: int, sayi: int = 4) -> tuple[float, float]:
    """Tüysü yaprak atlasında k. yaprağın u aralığı."""
    kenar = 0.5 / (256 * sayi)
    return k / sayi + kenar, (k + 1) / sayi - kenar


# --------------------------------------------------------------------------
# Kabuk
# --------------------------------------------------------------------------

def _periyodik_gurultu(n, fx, fy, rng):
    """[0,1) üzerinde fx×fy ızgaralı, iki yönde döşenebilir değer gürültüsü (n×n)."""
    G = rng.random((fy, fx))
    y = np.arange(n) / n * fy
    x = np.arange(n) / n * fx
    y0 = np.floor(y).astype(int)
    x0 = np.floor(x).astype(int)
    ty = y - y0
    tx = x - x0
    ty = ty * ty * (3 - 2 * ty)
    tx = tx * tx * (3 - 2 * tx)
    a = G[y0 % fy][:, x0 % fx]
    b = G[y0 % fy][:, (x0 + 1) % fx]
    c = G[(y0 + 1) % fy][:, x0 % fx]
    d = G[(y0 + 1) % fy][:, (x0 + 1) % fx]
    ust = a + (b - a) * tx[None]
    alt = c + (d - c) * tx[None]
    return ust + (alt - ust) * ty[:, None]


def _fbm(n, fx, fy, rng, oktav=5):
    s, a, t = np.zeros((n, n)), 0.5, 0.0
    for o in range(oktav):
        s += a * _periyodik_gurultu(n, fx * 2 ** o, fy * 2 ** o, rng)
        t += a
        a *= 0.5
    return s / t


def _hucresel(n, sayi_x, sayi_y, rng, bukum=None):
    """Worley F2-F1 (döşenebilir): levhalar ve aralarındaki yarıklar. bukum (n×n×2)
    verilirse örnekleme noktası kaydırılır: yarıklar dalgalanır."""
    px = (np.arange(sayi_x)[None] + rng.random((sayi_y, sayi_x))) / sayi_x
    py = (np.arange(sayi_y)[:, None] + rng.random((sayi_y, sayi_x))) / sayi_y
    pts = np.stack([px.ravel(), py.ravel()], 1)
    y, x = np.mgrid[0:n, 0:n] / n
    if bukum is not None:
        x = x + bukum[..., 0]
        y = y + bukum[..., 1]
    f1 = np.full((n, n), 9.0)
    f2 = np.full((n, n), 9.0)
    for ox in (-1, 0, 1):
        for oy in (-1, 0, 1):
            for p in pts + np.array([ox, oy]):
                dx = (x - p[0]) * sayi_x
                dy = (y - p[1]) * sayi_y
                d = np.sqrt(dx * dx + dy * dy)
                f2 = np.where(d < f1, f1, np.minimum(f2, d))
                f1 = np.minimum(f1, d)
    return f2 - f1


def kabuk_dokusu(n=512, tohum=8, yarik_sayi=5):
    """Döşenebilir kabuk: dikeyde uzanan, birbirine karışan yarıklar ve aralarında
    lifli sırtlar. Yarıklar yatayda periyodik bir alanın eş yükselti çizgileridir.
    Albedo (RGB, griye yakın) ve normal haritası (OpenGL, +Y yukarı)."""
    rng = np.random.default_rng(tohum)
    x = np.arange(n) / n
    f = _fbm(n, 5, 1, rng, 5)
    w = (_fbm(n, 2, 6, rng, 4) - 0.5) * 0.8
    faz = x[None] * yarik_sayi + f * 1.8 + w
    yar = 1 - np.abs((faz % 1.0) - 0.5) * 2            # 0 yarıkta, 1 sırt ortasında
    kirik = np.clip(_hucresel(n, 9, 3, rng) / 0.1, 0, 1)
    lif = _fbm(n, 48, 3, rng, 4)
    orta = _fbm(n, 12, 2, rng, 4)
    iri = _fbm(n, 3, 1, rng, 3)
    sirt = np.clip(yar / 0.6, 0, 1) ** 0.5 * (0.88 + 0.12 * kirik)
    h = sirt * 0.8 + (lif - 0.5) * 0.3 + (orta - 0.5) * 0.3
    l = (0.52 + 0.16 * (lif - 0.5) + 0.12 * (orta - 0.5) + 0.08 * (iri - 0.5)) * (0.28 + 0.72 * sirt)
    l = np.clip(l, 0.04, 1)
    sicak = 0.05 * (iri - 0.5) + 0.03 * (orta - 0.5)
    rgb = np.stack([l * (1.03 + sicak), l, l * (0.95 - sicak)], -1)
    guc = 6.0
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * guc
    dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * guc
    nrm = np.stack([-dx, dy, np.ones_like(h)], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    albedo = Image.fromarray(np.round(np.clip(rgb, 0, 1) * 255).astype(np.uint8), "RGB")
    normal = Image.fromarray(np.round((nrm * 0.5 + 0.5) * 255).astype(np.uint8), "RGB")
    return albedo, normal


def hurma_kabugu(n=512, tohum=12, sutun=4, sira=5):
    """Hurma gövdesi: sıra sıra, yarım kaydırılmış yaprak dibi kalıntıları. Her kalıntı
    yukarı doğru genişler ve üstte kesik bir kenarla biter; aralarında koyu lifli
    boşluklar vardır. Döşenebilir; albedo ve normal haritası."""
    rng = np.random.default_rng(tohum)
    y, x = np.mgrid[0:n, 0:n] / n
    bukum = (_fbm(n, 4, 4, rng, 3) - 0.5)
    yy = y + bukum * 0.02
    r = np.floor(yy * sira)
    fy = yy * sira - r                                   # 0 kalıntının dibi, 1 üstü (görüntüde aşağı)
    fy = 1 - fy                                          # görüntüde y aşağı: üst kenar yukarıda olsun
    kx = x * sutun + (r % 2) * 0.5 + bukum * 0.08
    hucre = np.floor(kx) + r * 17
    lx = (kx % 1.0) - 0.5
    rast = (np.sin(hucre * 12.9898) * 43758.5453) % 1.0  # hücreye özgü sabit rastgele
    genis = 0.62 + 0.38 * fy + (rast - 0.5) * 0.12
    q = np.abs(lx) / (genis * 0.5)
    ic = np.clip(1 - q ** 2, 0, 1) ** 0.5
    kenar_ust = 1 - np.clip((fy - (0.86 + 0.06 * rast)) / 0.05, 0, 1)
    dip = np.clip(fy / 0.18, 0, 1)
    tepe = ic * kenar_ust * dip
    lif = _fbm(n, 48, 8, rng, 4)
    iri = _fbm(n, 3, 2, rng, 3)
    h = tepe ** 0.5 * 0.85 + (lif - 0.5) * 0.25
    l = (0.5 + 0.2 * (lif - 0.5) + 0.1 * (iri - 0.5) + 0.12 * (rast - 0.5)) * (0.22 + 0.78 * tepe ** 0.35)
    l = np.clip(l, 0.04, 1)
    rgb = np.stack([l * 1.07, l * 0.98, l * 0.84], -1)
    guc = 6.0
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * guc
    dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * guc
    nrm = np.stack([-dx, dy, np.ones_like(h)], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    return (Image.fromarray(np.round(np.clip(rgb, 0, 1) * 255).astype(np.uint8), "RGB"),
            Image.fromarray(np.round((nrm * 0.5 + 0.5) * 255).astype(np.uint8), "RGB"))


def _normal(h, guc):
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * guc
    dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * guc
    nrm = np.stack([-dx, dy, np.ones_like(h)], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    return Image.fromarray(np.round((nrm * 0.5 + 0.5) * 255).astype(np.uint8), "RGB")


def toprak_dokusu(n=512, tohum=21):
    """Dikim yerinin yeni işlenmiş toprağı: irili ufaklı topaklar ve ufalanmış taneler,
    seyrek küçük çakıllar. Griye yakın (renk köşe renginden gelir). Döşenebilir."""
    rng = np.random.default_rng(tohum)
    kum = _fbm(n, 96, 96, rng, 2)
    orta = _fbm(n, 24, 24, rng, 3)
    iri = _fbm(n, 6, 6, rng, 4)
    topak = np.clip((orta - 0.45) / 0.25, 0, 1) ** 0.7              # kabarık topaklar
    tane = np.clip((kum - 0.62) / 0.12, 0, 1)                      # ufak taneler
    h = topak * 0.6 + tane * 0.25 + iri * 0.25
    l = 0.38 + 0.2 * topak + 0.08 * tane + 0.08 * (iri - 0.5) + 0.05 * (kum - 0.5)
    rgb = np.stack([l, l * 0.97, l * 0.93], -1)
    y, x = np.mgrid[0:n, 0:n]
    for _ in range(26):
        cx, cy, r = rng.uniform(0, n), rng.uniform(0, n), rng.uniform(2.0, 4.5)
        for ox in (-n, 0, n):
            for oy in (-n, 0, n):
                d = np.hypot(x - cx - ox, (y - cy - oy) * 1.3) / r
                m = np.clip(1 - d, 0, 1)
                if m.any():
                    k = np.clip(m * 3, 0, 1)[..., None]
                    rgb = rgb * (1 - k) + np.array([0.64, 0.61, 0.56]) * (0.75 + 0.25 * np.sqrt(m))[..., None] * k
                    h = np.maximum(h, np.sqrt(m) * 0.8)
    albedo = Image.fromarray(np.round(np.clip(rgb, 0, 1) * 255).astype(np.uint8), "RGB")
    return albedo, _normal(h, 5.0)


def cinar_kabugu(n=512, tohum=17):
    """Çınar kabuğu: pul pul dökülen, alacalı levhalar (krem, zeytin grisi, açık kahve).
    Renkler dokudadır; köşe rengi griye yakın verilir. Döşenebilir; albedo ve normal."""
    rng = np.random.default_rng(tohum)
    renkler = [np.array(c) / 255 for c in ((214, 204, 172), (154, 150, 126), (176, 148, 116), (140, 140, 116),
                                            (196, 186, 154))]
    rgb = np.tile(renkler[0], (n, n, 1)).astype(np.float64)
    h = np.zeros((n, n))
    for k, (sx, sy, esik) in enumerate(((5, 7, 0.52), (7, 9, 0.55), (9, 12, 0.58), (12, 16, 0.6))):
        bukum = np.stack([(_fbm(n, 3, 3, rng, 3) - 0.5) * 0.08, (_fbm(n, 3, 3, rng, 3) - 0.5) * 0.08], -1)
        alan = _fbm(n, sx, sy, rng, 4)
        leke = np.clip((alan - esik) / 0.03, 0, 1)                 # keskin kenarlı levha
        kenar = np.clip(1 - np.abs(alan - esik) / 0.012, 0, 1)      # soyulmuş levhanın ince kenarı
        c = renkler[(k + 1) % len(renkler)]
        rgb = rgb * (1 - leke[..., None]) + c * leke[..., None]
        rgb = rgb * (1 - 0.35 * kenar[..., None])
        h = h + leke * 0.25 - kenar * 0.15
    ince = _fbm(n, 32, 32, rng, 3)
    rgb = rgb * (0.9 + 0.2 * ince[..., None])
    albedo = Image.fromarray(np.round(np.clip(rgb, 0, 1) * 255).astype(np.uint8), "RGB")
    return albedo, _normal(h + ince * 0.1, 4.0)


# --------------------------------------------------------------------------
# Kayıt
# --------------------------------------------------------------------------

YAPRAK_TURLERI: dict[str, YaprakTuru] = {}
# Tüysü yapraklar (hurma): ad -> yaprakçık türü
TUYSU_TURLERI: dict[str, YaprakTuru] = {}


def yaprak_turu(t: YaprakTuru) -> YaprakTuru:
    YAPRAK_TURLERI[t.ad] = t
    return t


def _import_ayari(png: Path, normal: bool = False):
    """Godot içe aktarım ayarı: 3B'de kullanılan dokular mipmap'li olmalı (yoksa uzakta
    yapraklar kırpışır). Dosya yoksa en kısa hâli yazılır, Godot gerisini doldurur."""
    imp = png.with_name(png.name + ".import")
    istek = {"mipmaps/generate": "true", "compress/normal_map": "1" if normal else "0",
             "detect_3d/compress_to": "0"}
    if not imp.exists():
        imp.write_text('[remap]\n\nimporter="texture"\ntype="CompressedTexture2D"\n\n[params]\n\n'
                       + "".join(f"{k}={v}\n" for k, v in istek.items()))
        return
    satirlar = imp.read_text().splitlines()
    for i, satir in enumerate(satirlar):
        k = satir.split("=", 1)[0]
        if k in istek:
            satirlar[i] = f"{k}={istek[k]}"
    imp.write_text("\n".join(satirlar) + "\n")


def dokulari_yaz(klasor: Path) -> list[Path]:
    klasor.mkdir(parents=True, exist_ok=True)
    yazilan = []
    for ad, t in sorted(YAPRAK_TURLERI.items()):
        p = klasor / f"yaprak_{ad}.png"
        yaprak_atlasi(t).save(p, optimize=True)
        yazilan.append(p)
    for ad, t in sorted(TUYSU_TURLERI.items()):
        p = klasor / f"yaprak_{ad}.png"
        tuysu_yaprak_atlasi(t).save(p, optimize=True)
        yazilan.append(p)
    muz_yapragi_atlasi().save(klasor / "yaprak_muz.png", optimize=True)
    yazilan.append(klasor / "yaprak_muz.png")
    if TEK_YAPRAK:
        tek_yaprak_atlasi().save(klasor / "yaprak_tek.png", optimize=True)
        yazilan.append(klasor / "yaprak_tek.png")
    for ad, (albedo, normal) in (("kabuk", kabuk_dokusu()), ("kabuk_hurma", hurma_kabugu()),
                                 ("kabuk_muz", muz_govdesi()), ("kabuk_cinar", cinar_kabugu()),
                                 ("yuzey_toprak", toprak_dokusu())):
        for img, dosya in ((albedo, f"{ad}.png"), (normal, f"{ad}_n.png")):
            img.save(klasor / dosya, optimize=True)
            yazilan.append(klasor / dosya)
    for p in yazilan:
        _import_ayari(p, normal=p.stem.endswith("_n"))
    return yazilan
