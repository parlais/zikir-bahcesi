"""Kesit (K10, K18; 2026-09-26): sekiz tabakanın dıştan görünümü.

İlke: kesit ayrı bir maket değil, içerideki dünyanın kendisidir. Kullanıcı:
"Uzaklaştırma, yakınlaştırma yapılınca aynı mekân olduğu belli olsun."
  - 1. kat, içeride gördüğümüz dünyadır (ZB_dunya_cennet, çağlayanlar, köşkler,
    merdiven, korular, arsa ve Tûbâ). Kesme düzleminde (cennet.KESME_Z) kesilir;
    kesit kipinde düzlemin önündeki parça gizlenir. Bu modül yalnız dışarıdan
    görülenleri ekler: kesit yüzü, merdivenin bulutlara uzanan devamı.
  - 2-8. katlar aynı üreteç diliyle (ova, dört ırmak, gökten inen çağlayanlar,
    merdiven, korular, köşkler) ve gerçek ölçekte kurulur. Aynı veri (kat_dunyasi)
    ileride o katın içini kurarken de kullanılacak: kesitte görülen kat, girilince
    bulunan katın kendisi olur.
  - Katlar Rahmân suresindeki gibidir (kullanıcı, 2026-09-26; eşleme bir yorumdur,
    danışma kuruluna sorulacak):
      1-4. katlar, Rahmân 62-76: koyu yeşil (müdhâmmetân), fışkıran pınarlar, hurma
        ve nar, otağlar (çadır obaları).
      5-7. katlar, Rahmân 46-61: çeşit çeşit dallı ağaçlar, akan pınarlar, çift çift
        meyveler, köşkler; yukarı çıktıkça çeşitlilik, incelik ve ışık artar.
      8. kat Firdevs: nurlu bahçe (kullanıcının seçimi). Zemin görünür ama her şey
        nurdandır; ağaçlar ışıktan siluetler, ortada dört ırmağın kaynağı; göğü mavi
        değil, her şeyi kuşatan ışıktır. Arş tasvir edilmez; ışık sütunu da konmaz
        (ışık bir şeye yönelmiş gibi görünmesin, her yeri kuşatsın).
  - Kesit yüzü, Dünya'nın katman resimleri gibidir: za'ferân toprak, misk damarları,
    inci ve yakut çakıllar ("toprağı za'ferân, çakılları inci ve yakut, harcı misk";
    et-Tâc 5/402, Tirmizî 2526; danışma kurulu teyit edecek), kökler.

Ölçüler (metre). Kat k (0 = 1. kat, 7 = Firdevs) zemini G(k) = k * KAT_H yükseltisindedir;
dilimi [G(k) - KAT_T, G(k)] arasıdır. Havası (zeminden üst dilimin altına) KAT_HAVA'dır:
içerideki en yüksek bulut kümeleri ~755 m'ye çıkar, tavan onların üstünde kalır.
Katlar arası mesafe temsilîdir (Buhârî, Cihâd 4: "gökle yer arası").

Modeller: ZB_kesit_kat1 ... ZB_kesit_kat7, ZB_kesit_firdevs
Yerleşim: game/data/dunya_kesit.json ve ağaçlar için game/data/dunya_kesit_agac.bin
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import numpy as np

from mf.mesh import Mesh, lathe, merge
from mf.palette import renk
from mf.scene import Node

from . import model
from .cennet import (KESIT_KAMERA, KESME_Z, SELALE_UST, Irmak, _gok_selalesi, _izgara, _kes, _kose_normalleri, _lin2srgb, _ss,
                     _su_seritleri, _yuz_yonu, arazi_y, ilk_kat_kesimi)
from .cennet_yapilari import MERDIVEN_H
from .sahne import _noise2

KAT = 8
KAT_H = 1000.0                # zeminden zemine
KAT_T = 200.0                 # zemin dilimi: kesit yüzünün boyu (dikey kadrajda ~28 px; katman resmi okunur)
KAT_HAVA = KAT_H - KAT_T      # zeminden tavana (üst dilimin altı)
KABUK_X = 4000.0              # 2-8. katların ve yüzlerin yarı genişliği (dikey kadraj ±2,5 km görür)
DERIN = 12000.0               # katların kesme düzleminden geriye derinliği
ARKA_Z = KESME_Z - DERIN
# Kesitte her katın göğü (perde) katın "penceresi"nin arkasında durur: bandın alt kısmı zemin,
# üstü gök okunur (K10: "her tabakanın zemini ve göğü bant bant görünür"). Pencerenin
# derinliği, kesit kamerasının o kata bakış açısından hesaplanır; her bantta zemin aynı
# oranı tutar: D = PENCERE_M / sin(θ). Yakınlaşmada kamera içeri girince perde erir.
PENCERE_M = 360.0


def pencere(k: int) -> float:
    """k. katın zemininin kesme düzleminden perdeye derinliği (m)."""
    kx, ky, kz = KESIT_KAMERA["konum"]
    dy = ky - G(k)
    dz = kz - KESME_Z
    return float(min(PENCERE_M * math.hypot(dy, dz) / dy, 9000.0))
# İlk katın merdiveni (cennet.MERDIVEN): ayak, dönüş; kesitte bulutlara uzanan devamı
MERDIVEN_ILK = (70.0, -150.0, 16.0)
MERDIVEN_T_UST = (KAT_HAVA / MERDIVEN_H) ** (1 / 1.08)     # _merdiven_yolu'nun tavana vardığı t

# Firdevs'in ortası (Buhârî, Cihâd 4: "cennetin ortası ve en yükseğidir"): dört ırmağın kaynağı
FIRDEVS_KAYNAK = (0.0, -1300.0)
FIRDEVS_TEPE = 250.0

# Uzak ağaç siluetlerinin türleri (atlas hücreleri): gerçek modellerden çizilir (mf/siluet.py)
SILUET_TURLERI = ["koru", "hurma", "nar", "sidr", "selvi", "cinar", "talh", "su_kosku", "inci_cadir"]
SILUET_MODELLERI = {"koru": "ZB_bitki_koru_agac", "hurma": "ZB_agac_hurma_a4", "nar": "ZB_bitki_nar",
                    "sidr": "ZB_agac_sidr_a4", "selvi": "ZB_bitki_selvi", "cinar": "ZB_agac_cinar_a4",
                    "talh": "ZB_agac_talh_a4", "su_kosku": "ZB_yapi_su_kosku", "inci_cadir": "ZB_yapi_inci_cadir"}


def G(k: int) -> float:
    return k * KAT_H


# --------------------------------------------------------------------------
# Katların karakteri (Rahmân 46-76)
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class KatKarakteri:
    kat: int                        # 0..7
    grup: str                       # "ilk", "alt", "ust", "firdevs"
    agac: dict = field(default_factory=dict)   # tür -> pay
    koru_esik: float = 0.1          # koru alanının bolluğu (küçük: daha çok koru)
    tek_siklik: float = 0.12        # koru dışında tek ağaç olasılığı
    ton: tuple = (1.0, 1.0, 1.0)    # çimenin köşe tonu (kose_ton ile çarpılır; 0,5 nötr ölçeğinde ×2)
    cicek: float = 0.0              # çiçek tarlası payı
    cicek_renk: tuple = ("gul", "inci", "lale_sari")
    cadir: int = 0                  # çadır obası sayısı
    kosk: int = 0                   # köşk sayısı (ırmak kıyısında)
    isik: float = 0.0               # kat ışığı (pus ve ışıma artışı)


KARAKTERLER = [
    KatKarakteri(0, "ilk"),
    KatKarakteri(1, "alt", {"koru": .45, "hurma": .25, "nar": .20, "talh": .10}, koru_esik=0.0,
                 ton=(0.93, 0.98, 0.9), cadir=6, kosk=1),
    KatKarakteri(2, "alt", {"koru": .40, "hurma": .25, "nar": .25, "talh": .10}, koru_esik=-0.05,
                 ton=(0.92, 0.98, 0.89), cadir=5, kosk=2),
    KatKarakteri(3, "alt", {"koru": .30, "hurma": .20, "nar": .20, "selvi": .15, "sidr": .15}, koru_esik=0.0,
                 ton=(0.96, 1.0, 0.92), cicek=0.08, cadir=4, kosk=3),
    KatKarakteri(4, "ust", {"cinar": .20, "selvi": .15, "sidr": .20, "nar": .15, "hurma": .15, "koru": .15},
                 koru_esik=0.08, tek_siklik=0.2, ton=(1.0, 1.02, 0.92), cicek=0.15, kosk=5),
    KatKarakteri(5, "ust", {"nar": .25, "hurma": .20, "sidr": .20, "cinar": .15, "selvi": .10, "talh": .10},
                 koru_esik=0.12, tek_siklik=0.24, ton=(1.05, 1.06, 0.94), cicek=0.2, kosk=6),
    KatKarakteri(6, "ust", {"cinar": .18, "sidr": .18, "nar": .18, "hurma": .16, "selvi": .15, "talh": .15},
                 koru_esik=0.16, tek_siklik=0.28, ton=(1.1, 1.1, 1.0), cicek=0.26,
                 cicek_renk=("inci", "inci", "gul", "lale_sari"), kosk=8),
    KatKarakteri(7, "firdevs", {"cinar": .4, "selvi": .3, "sidr": .3}, koru_esik=0.3, tek_siklik=0.1,
                 ton=(1.25, 1.2, 1.05), cicek=0.3, cicek_renk=("inci", "inci", "lale_sari")),
]
for _i, _k in enumerate(KARAKTERLER):
    object.__setattr__(_k, "isik", ((_i) / 7.0) ** 1.4)


# --------------------------------------------------------------------------
# Kat dünyası: ova, ırmaklar, çağlayanlar, merdiven, ağaçlar, yapılar, bulutlar
# --------------------------------------------------------------------------

def kat_ovasi(k: int):
    """Katın zemin yüksekliği (G(k)'ye göre). İlk kattaki ovayla aynı dil: kuzeye
    doğru hafifçe yükselir, uzakta alçak ve geniş tepeler. Firdevs'in ortası yükselir
    (Buhârî, Cihâd 4: "Firdevs cennetin ortası ve en yükseğidir")."""
    s = 300 + 17 * k

    def ova(x, z):
        x = np.asarray(x, float)
        z = np.asarray(z, float)
        d = KESME_Z - z
        h = 14.0 * _ss(0.0, 2200.0, d)
        h += _noise2(x, z, s) * 1.4 + _noise2(x * 3.0, z * 3.0, s + 1) * 0.4
        h += (8.0 + 6.0 * _noise2(x * 0.5, z * 0.5, s + 2)) * _ss(200.0, 1400.0, d)
        h += (26.0 + 22.0 * _noise2(x * 0.18, z * 0.18, s + 3)) * _ss(2500.0, 7000.0, d)
        if k == KAT - 1:
            # Ortası yumuşak bir tepe: kaynak tepede, ırmaklar yamaçlardan iner; sıyırarak bakan
            # kesit kamerasına nurlu bahçe görünür
            h += FIRDEVS_TEPE * np.exp(-((x / 1500.0) ** 2 + ((z - FIRDEVS_KAYNAK[1]) / 1200.0) ** 2))
        return h
    return ova


def _irmak_tanimlari(k: int):
    """Dört ırmak (su, süt, bal, şerbet): gökten inen çağlayanın dibinden (kuzey) kesme
    düzlemine kıvrılarak iner. Kesme düzlemindeki sıra her katta aynıdır (bal, su, süt,
    şerbet; ilk kattaki gibi): dört renk kattan kata aynı sırayla okunur.
    Firdevs'te ırmaklar ortadaki kaynaktan yelpaze gibi açılır."""
    rng = np.random.default_rng(700 + k)
    kay = 330.0 * math.sin(k * 1.9)                      # katlar arasında kayma
    if k == KAT - 1:
        kaynak = FIRDEVS_KAYNAK
        uclar = {"bal": -1000.0, "su": -350.0, "sut": 350.0, "serbet": 1000.0}
        out = []
        for ad, xc in uclar.items():
            pts = [kaynak]
            for t in (0.25, 0.5, 0.75):
                x = kaynak[0] + (xc - kaynak[0]) * t + 60 * math.sin(t * 7 + xc)
                z = kaynak[1] + (KESME_Z - kaynak[1]) * t
                pts.append((x, z))
            pts.append((xc, KESME_Z + 40.0))
            out.append(dict(ad=ad, gen={"su": 16.0, "sut": 12.0, "bal": 11.0, "serbet": 11.0}[ad], noktalar=pts))
        return out
    # Çağlayan ayakları (ilk kattakine benzer dağılım) ve kesme düzlemindeki geçiş
    ayak = {"su": (-330.0, -1250.0), "sut": (330.0, -1350.0), "bal": (-760.0, -1150.0), "serbet": (720.0, -1250.0)}
    gecis = {"bal": -215.0, "su": -46.0, "sut": 79.0, "serbet": 242.0}
    genis = {"su": 16.0, "sut": 12.0, "bal": 11.0, "serbet": 11.0}
    out = []
    for ad in ("su", "sut", "bal", "serbet"):
        ax, az = ayak[ad]
        ax = ax * rng.uniform(0.8, 1.5) + kay
        az = az + rng.uniform(-150, 150)
        xc = gecis[ad] * rng.uniform(1.5, 3.0) + kay * 0.6
        pts = [(ax, az)]
        n = 6
        for i in range(1, n):
            t = i / n
            x = ax + (xc - ax) * t + rng.uniform(-90, 90) * math.sin(t * math.pi)
            z = az + (KESME_Z - az) * t
            pts.append((x, z))
        pts.append((xc, KESME_Z + 40.0))
        out.append(dict(ad=ad, gen=genis[ad], noktalar=pts))
    return out


@dataclass
class KatDunyasi:
    k: int
    kar: KatKarakteri
    ova: object
    irmaklar: list
    selaleler: list          # [(x, z, y_alt, y_ust, gen, seed)] (dünya y'si)
    merdiven: tuple | None   # (x, z, dönüş derece)
    agaclar: dict            # tür -> (n, 5) [x, y, z, dönüş, ölçek]
    yapilar: dict            # tür -> (n, 5)
    bulutlar: list           # [(x, y, z, boyut, yatay, tohum)]
    kaynak: tuple | None     # Firdevs'in kaynağı (x, y, z)

    def zemin_y(self, x, z):
        return G(self.k) + arazi_y(x, z, self.irmaklar, ova=self.ova).reshape(np.shape(x))


def _yakin_irmak(irmaklar, X):
    """Her noktanın en yakın ırmağa uzaklığı."""
    d = np.full(len(X), 1e9)
    for ir in irmaklar:
        dd, _ = ir.uzaklik(X)
        d = np.minimum(d, dd - ir.a[0])
    return d


def _koru_alani(k, x, z):
    """Koru alanı alanı (0..1): 200-600 m'lik koruluklar, aralarında çayırlar."""
    n = _noise2(np.asarray(x) * 0.28, np.asarray(z) * 0.28, 520 + k, 3) / 1.6
    n += 0.35 * _noise2(np.asarray(x) * 0.9, np.asarray(z) * 0.9, 530 + k, 2) / 1.5
    return n


def _cicek_alani(k, x, z):
    return _noise2(np.asarray(x) * 0.7, np.asarray(z) * 0.7, 560 + k, 3) / 1.6


def _firdevs_agaclari(irmaklar, rng, bos, derin_max) -> dict:
    """Firdevs (nurlu bahçe): seyrek ve düzenli, ışıktan ağaçlar (~400). Dört ırmağın iki
    kıyısında kaynaktan açılan sıralar (çınar ve servi dönüşümlü), kaynağın çevresinde bir
    halka, arkada seyrek sidrler. Kesitte sıralar ırmakları kaynağa bağlayan ışık çizgileri
    gibi okunur; ortası ve kaynağı açık kalır."""
    kx, kz = FIRDEVS_KAYNAK
    agaclar = {"cinar": [], "selvi": [], "sidr": []}
    olcek = {"cinar": (1.2, 1.45), "selvi": (1.45, 1.65), "sidr": (1.25, 1.4)}

    def ekle(t, x, z):
        agaclar[t].append([x, 0.0, z, rng.uniform(0, 360), rng.uniform(*olcek[t])])

    # Irmak kıyısı sıraları: yay uzunluğunca 70 m'de bir, iki yanda
    for ir in irmaklar:
        i = 0
        sira = 0
        for s_hedef in np.arange(200.0, ir.s[-1] - 30.0, 70.0):
            i = int(np.searchsorted(ir.s, s_hedef))
            x, z = ir.P[i]
            t = "cinar" if sira % 2 == 0 else "selvi"
            for yan in (-1.0, 1.0):
                n = ir.N[i] * (ir.a[i] + ir.banka()[i] + 22.0) * yan
                if bos(x + n[0], z + n[1], 0.0):
                    ekle(t, x + n[0], z + n[1])
            sira += 1
    # Kaynağın çevresinde halka (ırmak ağızları açık kalır)
    for j in range(18):
        a = 2 * math.pi * (j + 0.5) / 18
        x, z = kx + 230.0 * math.sin(a), kz + 230.0 * math.cos(a)
        if bos(x, z, 30.0):
            ekle("selvi" if j % 2 else "cinar", x, z)
    # Arkada ve yanlarda seyrek sidrler (380 m'lik titreşimli ızgara)
    for x in np.arange(-2600.0, 2601.0, 380.0):
        for z in np.arange(KESME_Z - 150.0, KESME_Z - derin_max, -380.0):
            px, pz = x + rng.uniform(-120, 120), z + rng.uniform(-120, 120)
            if math.hypot(px - kx, pz - kz) < 420.0 or rng.uniform() < 0.35:
                continue
            if bos(px, pz, 40.0):
                ekle("sidr", px, pz)
    return agaclar


@lru_cache(maxsize=None)
def kat_dunyasi(k: int) -> KatDunyasi:
    """k. katın (1..7) verisi: kesit bunun hafif hâlini çizer; ileride katın içi de
    bundan kurulacak. (İlk kat, k = 0, içerideki dünyadır; burada kurulmaz.)"""
    assert 1 <= k < KAT
    kar = KARAKTERLER[k]
    ova = kat_ovasi(k)
    irmaklar = [Irmak(t, ova=ova) for t in _irmak_tanimlari(k)]
    rng = np.random.default_rng(800 + k)

    # Çağlayanlar: ilk kattaki gibi tepeleri SELALE_UST + 30j (bulut kuşağının içinde)
    selaleler = []
    if k < KAT - 1:
        for j, ir in enumerate(irmaklar):
            x, z = ir.P[0]
            selaleler.append((float(x), float(z), G(k) + float(ir.wl[0]) - 1.5, G(k) + SELALE_UST + 30 * j,
                              ir.gen * 4.0, 40 + 7 * k + j))

    # Merdiven: kattan kata zikzak bir yükseliş yolu (kesme düzleminin yakınında)
    merdiven = None
    if k < KAT - 1:
        mx = [0.0, -1400.0, 1100.0, -600.0, 1600.0, -1800.0, 400.0][k]
        merdiven = (mx, -150.0 - 120.0 * (k % 3), float(rng.uniform(-30, 30)))

    def bos(x, z, pay):
        X = np.stack([np.atleast_1d(x), np.atleast_1d(z)], 1)
        return _yakin_irmak(irmaklar, X) > pay

    # Ağaçlar: yalnız okunur bölgede (kesme düzleminden geriye); daha derindeki orman
    # zeminin köşe renginde koyu leke olarak durur. Aralık derinlikle büyür.
    turler = list(kar.agac)
    paylar = np.array([kar.agac[t] for t in turler])
    paylar = paylar / paylar.sum()
    derin_max = pencere(k) + 200.0
    agaclar = {t: [] for t in turler}
    z = KESME_Z - 12.0
    if kar.grup == "firdevs":
        agaclar = _firdevs_agaclari(irmaklar, rng, bos, derin_max)
        z = -1e9
    while KESME_Z - z < derin_max:
        derin = KESME_Z - z
        adim = 26.0 + derin * 0.012
        xs = np.arange(-2900.0, 2900.0, adim) + rng.uniform(-0.45, 0.45, int(math.ceil(5800 / adim))) * adim
        zs = z + rng.uniform(-0.45, 0.45, len(xs)) * adim
        koru = _koru_alani(k, xs, zs)
        p = np.where(koru > kar.koru_esik, 0.92, kar.tek_siklik)
        sec = rng.uniform(0, 1, len(xs)) < p
        sec &= bos(xs, zs, 22.0)
        for x, zz, kv in zip(xs[sec], zs[sec], koru[sec]):
            # Korularda baskın tür; dışarıda çeşit (üst katlarda çift çift meyve bahçeleri)
            if kv > kar.koru_esik and "koru" in agaclar and rng.uniform() < 0.65:
                t = "koru"
            else:
                t = turler[rng.choice(len(turler), p=paylar)]
            olcek = {"koru": (1.3, 2.1), "hurma": (1.9, 2.5), "nar": (1.15, 1.5), "sidr": (1.2, 1.4),
                     "selvi": (1.3, 1.7), "cinar": (1.1, 1.5), "talh": (1.2, 1.5)}[t]
            agaclar[t].append([x, 0.0, zz, rng.uniform(0, 360), rng.uniform(*olcek)])
        z -= adim
    # Hurma ırmak boylarında (Rahmân 68; Zümer 20: altlarından ırmaklar akar)
    if "hurma" in agaclar:
        for ir in irmaklar:
            for i in range(0, len(ir.P), 9):
                if rng.uniform() < 0.5:
                    continue
                x, zz = ir.P[i]
                if KESME_Z - zz > derin_max:
                    continue
                n = ir.N[i] * (ir.a[i] + ir.banka()[i] + rng.uniform(4, 16)) * rng.choice([-1, 1])
                agaclar["hurma"].append([x + n[0], 0.0, zz + n[1], rng.uniform(0, 360), rng.uniform(1.9, 2.5)])
    agaclar = {t: np.asarray(v, float).reshape(-1, 5) for t, v in agaclar.items()}
    kd = KatDunyasi(k, kar, ova, irmaklar, selaleler, merdiven, agaclar, {}, [], None)
    for t, a in agaclar.items():
        if len(a):
            a[:, 1] = kd.zemin_y(a[:, 0], a[:, 2]) - 0.3

    # Yapılar: köşkler ırmak kıyısında (Zümer 20), çadırlar çayırda obalar hâlinde (Rahmân 72)
    kosk, cadir = [], []
    for i in range(kar.kosk):
        ir = irmaklar[i % len(irmaklar)]
        j = int(rng.uniform(0.15, 0.85) * (len(ir.P) - 1))
        x, zz = ir.P[j]
        dx, dz = ir.P[min(j + 1, len(ir.P) - 1)] - ir.P[max(j - 1, 0)]
        kosk.append([x, float(G(k) + ir.wl[j]), zz, math.degrees(math.atan2(dx, dz)), rng.uniform(0.85, 1.1)])
    for i in range(kar.cadir):
        cx, cz = rng.uniform(-2200, 2200), rng.uniform(KESME_Z - 2600, KESME_Z - 200)
        for _ in range(int(rng.integers(5, 10))):
            x, zz = cx + rng.normal(0, 45), cz + rng.normal(0, 35)
            if bos(x, zz, 25.0):
                cadir.append([x, 0.0, zz, rng.uniform(0, 360), rng.uniform(0.9, 1.2)])
    yapilar = {"su_kosku": np.asarray(kosk, float).reshape(-1, 5), "inci_cadir": np.asarray(cadir, float).reshape(-1, 5)}
    if len(yapilar["inci_cadir"]):
        c = yapilar["inci_cadir"]
        c[:, 1] = kd.zemin_y(c[:, 0], c[:, 2]) - 0.2
    kd.yapilar = yapilar

    # Bulutlar: çağlayanların indiği bulutlar ve merdivenin ucu (ilk kattaki _gok_kur
    # kuralları), gökte süzülen kümeler ve tavanın altındaki kuşak.
    bulutlar = []
    for j, (x, zz, _, yu, g, _) in enumerate(selaleler):
        bulutlar.append((x, yu + 15.0, zz, g * 6.0, 2.2, 50 + 10 * k + j))
    for j in range(9):
        a = rng.uniform(-1.2, 1.2)
        r = rng.uniform(900.0, 2600.0)
        bulutlar.append((math.sin(a) * r, G(k) + rng.uniform(260.0, 520.0), KESME_Z - math.cos(a) * r,
                         rng.uniform(160.0, 320.0), 1.0, 120 + 10 * k + j))
    if k < KAT - 1:
        for j in range(11):
            bulutlar.append((rng.uniform(-3000, 3000), G(k) + rng.uniform(700.0, 770.0),
                             KESME_Z - rng.uniform(100.0, 1600.0), rng.uniform(200.0, 340.0), 2.6, 300 + 30 * k + j))
    kd.bulutlar = bulutlar
    if k == KAT - 1:
        kx, kz = FIRDEVS_KAYNAK
        kd.kaynak = (kx, float(kd.zemin_y(np.array([kx]), np.array([kz]))[0]), kz)
    return kd


# --------------------------------------------------------------------------
# Geometri
# --------------------------------------------------------------------------

def _x_sutunlari(irmaklar=()):
    """Kesme çizgisindeki ve zemin ızgarasındaki x örnekleri: merkezde sık, kenarda seyrek;
    ırmak geçişlerinde yatak kenarları ayrıca örneklenir (ince yataklar kaybolmasın)."""
    xs = [np.arange(-2600.0, 2600.0, 30.0), np.arange(2600.0, KABUK_X + 1, 100.0),
          -np.arange(2600.0 + 100.0, KABUK_X + 1, 100.0)]
    for ir in irmaklar:
        i = int(np.argmin(np.abs(ir.P[:, 1] - KESME_Z)))
        xc, a, b = ir.P[i, 0], ir.a[i], ir.banka()[i]
        xs.append(xc + np.array([-a - b, -a, -a * 0.5, 0.0, a * 0.5, a, a + b]))
    x = np.unique(np.round(np.concatenate(xs), 2))
    return x[(x >= -KABUK_X) & (x <= KABUK_X)]


def _z_satirlari(derin):
    son = KESME_Z - derin
    zs = [KESME_Z]
    adim = 8.0
    while zs[-1] > son:
        zs.append(max(zs[-1] - adim, son))
        adim = min(adim * 1.09, 400.0)
    return np.asarray(zs)


def _kat_zemini(kd: KatDunyasi) -> Mesh:
    """Katın zemini: kesme düzleminden (ön satır, kesit yüzünün üst kenarıyla aynı x'ler)
    geriye DERIN metre. Köşe renginde katın tonu (çimen onunla çarpılır), korulukların
    altı koyu, ırmak kıyıları kum ve çakıl, üst katlarda çiçek tarlaları."""
    k = kd.k
    xs = _x_sutunlari(kd.irmaklar)
    zs = _z_satirlari(pencere(k) + 400.0 if k < KAT - 1 else DERIN)
    X, Z = np.meshgrid(xs, zs)
    x, z = X.ravel(), Z.ravel()
    h, W, kiyi, _ = arazi_y(x, z, kd.irmaklar, W_don=True, ova=kd.ova, arsa=False)
    W = np.maximum(W, 0.0)
    V = np.stack([x, G(k) + h, z], 1)
    kar = kd.kar
    # Katın tonu (0,5 nötr): zemin shader'ı kose_ton ile çimeni bununla çarpar (×2)
    ton = np.tile(np.array(kar.ton) * 0.5, (len(x), 1))
    koru = _koru_alani(k, x, z)
    ton *= (1.0 - 0.2 * _ss(kar.koru_esik - 0.05, kar.koru_esik + 0.25, koru))[:, None]
    cv = ton
    # Irmak kıyısı: kum ve çakıl (W < 1 yerlerde köşe rengi görünür)
    kum = np.array(renk("kum"))
    cv = cv + (kum - cv) * _ss(0.2, 0.45, kiyi)[:, None]
    # Çiçek tarlaları (W < 1): üst katlarda artar
    if kar.cicek > 0:
        c = _cicek_alani(k, x, z)
        esik = 1.0 - 2.2 * kar.cicek
        tarla = _ss(esik, esik + 0.12, c) * (1 - _ss(0.2, 0.5, kiyi))
        renkler = np.array([renk(r) for r in kar.cicek_renk])
        sec = (np.floor((x + 9000) / 170) + np.floor((z + 9000) / 130)).astype(int) % len(renkler)
        cv = cv * (1 - tarla[:, None]) + renkler[sec] * tarla[:, None]
        W = np.minimum(W, 1 - 0.9 * tarla)
    m = _izgara(V, len(xs) - 1, len(zs) - 1, cv, "zemin_kesit", W=W)
    return _yuz_yonu(m, (0, 1, 0))


def _kesit_yuzu(cizgi: np.ndarray, taban_y: float, k: int) -> Mesh:
    """Kesit yüzü: kesme çizgisinden (üst kenar, zeminle aynı köşeler) dilimin altına.
    UV.x = x / 300 m, UV.y = yüzeyden derinlik oranı (0 üst, 1 alt): kesit_toprak
    dokusunun katmanları yüzeye paralel akar. COLOR.r = kat / 8 (desen katlar arasında
    kaysın), COLOR.a = 1."""
    oranlar = np.array([0.0, 0.004, 0.02, 0.06, 0.13, 0.25, 0.42, 0.62, 0.82, 1.0])
    x, yu = cizgi[:, 0], cizgi[:, 1]
    V, UV = [], []
    for o in oranlar:
        y = yu + (taban_y - yu) * o
        V.append(np.stack([x, y, np.full_like(x, KESME_Z)], 1))
        UV.append(np.stack([x / 300.0, np.full_like(x, o)], 1))
    V = np.vstack(V)
    UV = np.vstack(UV)
    cv = _lin2srgb(np.tile([k / 8.0, 0.5, 0.5], (len(V), 1)))
    m = _izgara(V, len(x) - 1, len(oranlar) - 1, cv, "kesit_yuzu")
    m.UV = UV.astype(np.float32)
    m = _yuz_yonu(m, (0, 0, 1))
    m.NV = np.tile(np.array([0, 0, 1], np.float32), (len(m.V), 1))
    return m


def _duz(y, z0, z1, x0, x1, malzeme, yon, n=8) -> Mesh:
    """Yatay dikdörtgen (tavan): n×n ızgara."""
    xs = np.linspace(x0, x1, n + 1)
    zs = np.linspace(z0, z1, n + 1)
    X, Z = np.meshgrid(xs, zs)
    V = np.stack([X.ravel(), np.full(X.size, y), Z.ravel()], 1)
    m = _izgara(V, n, n, np.ones((len(V), 3)), malzeme)
    m = _yuz_yonu(m, yon)
    m.NV = np.tile(np.array(yon, np.float32), (len(m.V), 1))
    return m


def _perde(k: int, malzeme: str = "kat_gogu") -> Mesh:
    """Katın göğü: kesme düzleminden pencere(k) geride dikey perde; kat_gogu shader'ı
    içerideki göğü çizer."""
    xs = np.linspace(-KABUK_X - 2000, KABUK_X + 2000, 9)
    ys = np.linspace(G(k) - 60.0, G(k) + KAT_HAVA + 5.0, 5)
    X, Y = np.meshgrid(xs, ys)
    V = np.stack([X.ravel(), Y.ravel(), np.full(X.size, KESME_Z - pencere(k))], 1)
    m = _izgara(V, len(xs) - 1, len(ys) - 1, np.ones((len(V), 3)), malzeme)
    m = _yuz_yonu(m, (0, 0, 1))
    m.NV = np.tile(np.array([0, 0, 1], np.float32), (len(m.V), 1))
    return m


def _merdiven_seridi(x0, z0, rot, y0, t0, t1) -> Mesh:
    """Merdivenin kesitteki ışıklı şeridi: _merdiven_yolu eğrisi (ilk kattaki gerçek
    merdivenle aynı kıvrım), t0..t1 aralığında. Şerit shader'ı genişliği ekranda en az
    birkaç piksele açar (uzakta seçilsin, yakında gerçek 5,6 m'ye iner).
    Köşe verisi: UV.x = kenar (-1 sol, +1 sağ), UV.y = yol boyunca oran; NV = yolun yönü."""
    t = np.linspace(t0, t1, int(40 * (t1 - t0)) + 2)
    x = 55.0 * np.sin(2 * math.pi * 1.25 * t) * (0.55 + 0.45 * t)
    z = -300.0 * t
    y = MERDIVEN_H * t ** 1.08
    a = math.radians(rot)
    wx = x * math.cos(a) + z * math.sin(a)
    wz = -x * math.sin(a) + z * math.cos(a)
    P = np.stack([x0 + wx, y0 + y, z0 + wz], 1)
    T = np.gradient(P, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    V = np.repeat(P, 2, axis=0)
    NV = np.repeat(T, 2, axis=0)
    UV = np.stack([np.tile([-1.0, 1.0], len(P)), np.repeat(np.linspace(0, 1, len(P)), 2)], 1)
    F = []
    for i in range(len(P) - 1):
        a0 = 2 * i
        F += [[a0, a0 + 1, a0 + 3], [a0, a0 + 3, a0 + 2]]
    F = np.asarray(F, np.int64)
    m = Mesh(V.astype(np.float32), F, np.ones((len(F), 3), np.float32), "kesit_serit")
    m.NV = NV.astype(np.float32)
    m.CV = np.ones((len(V), 3), np.float32)
    m.UV = UV.astype(np.float32)
    return m


def _kat_irmaklari(kd: KatDunyasi):
    """Su şeritleri (ilk kattaki _su_seritleri), kesme düzleminde kesilip yükseltilir."""
    out = []
    for m in _su_seritleri(kd.irmaklar):
        arka, _, _ = _kes(m, KESME_Z)
        arka = arka.translate(0, G(kd.k), 0)
        out.append(arka)
    return out


def _kat_selaleleri(kd: KatDunyasi):
    ana, pus = [], []
    for (x, z, ya, yu, g, seed) in kd.selaleler:
        a, p = _gok_selalesi(x, z, ya, yu, g, (-x, KESME_Z - z), seed, nv=28, nu=8)
        ana.append(a)
        pus.append(p)
    return [merge(*pus), merge(*ana)] if ana else []


def _firdevs_kaynagi(kd: KatDunyasi) -> Mesh:
    """Dört ırmağın kaynağı: nurdan, sığ bir havuz (yakından dört ağzı seçilir)."""
    x, y, z = kd.kaynak
    return lathe([(70, 0), (64, 5), (40, 8), (0, 9)], 32, "nur_beyaz").translate(x, y - 3.0, z).with_material("nur")


def _kat_modeli(k: int) -> Node:
    """2-8. katların kesit modeli. k = 1..7."""
    kd = kat_dunyasi(k)
    ad = "ZB_kesit_firdevs" if k == KAT - 1 else f"ZB_kesit_kat{k + 1}"
    root = Node(ad)
    zemin = _kat_zemini(kd)
    xs = _x_sutunlari(kd.irmaklar)
    cizgi = np.stack([xs, kd.zemin_y(xs, np.full_like(xs, KESME_Z))], 1)
    root.add(Node("zemin", [zemin]), Node("yuz", [_kesit_yuzu(cizgi, G(k) - KAT_T, k)]))
    # Alttaki katın tavanı: bu dilimin altı (içeriden gök gibi görünür; dışarıdan hiç)
    root.add(Node("taban", [_duz(G(k) - KAT_T, KESME_Z, ARKA_Z, -KABUK_X, KABUK_X, "kat_tavani", (0, -1, 0))]))
    if k < KAT - 1:
        root.add(Node("perde", [_perde(k)]))
    root.add(Node("irmaklar", _kat_irmaklari(kd)))
    if kd.selaleler:
        root.add(Node("selaleler", _kat_selaleleri(kd)))
    if kd.merdiven:
        mx, mz, mr = kd.merdiven
        y0 = float(kd.zemin_y(np.array([mx]), np.array([mz]))[0])
        root.add(Node("merdiven", [_merdiven_seridi(mx, mz, mr, y0 - 0.3, 0.0, MERDIVEN_T_UST)]))
    if kd.kaynak:
        root.add(Node("kaynak", [_firdevs_kaynagi(kd)]))
        root.add(Node("isik_kaynak", translation=(kd.kaynak[0], kd.kaynak[1] + 30.0, kd.kaynak[2])))
    return root


@model("ZB_kesit_kat1")
def kesit_kat1() -> Node:
    """İlk katın kesitte eklenenleri: kesit yüzü (içerideki arazinin kesme çizgisinden)
    ve merdivenin gerçek modelin ucundan (210 m) tavana uzanan devamı; ilk katın arka perdesi."""
    k = ilk_kat_kesimi()
    cizgi = k["cizgi"]
    root = Node("ZB_kesit_kat1")
    root.add(Node("yuz", [_kesit_yuzu(cizgi, -KAT_T, 0)]))
    mx, mz, mr = MERDIVEN_ILK
    root.add(Node("merdiven", [_merdiven_seridi(mx, mz, mr, -0.3, 0.0, MERDIVEN_T_UST)]))
    # İlk katın perdesi yakınlaşmada erir: ardındaki gerçek ova ve gök açılır
    root.add(Node("perde", [_perde(0, "kat_gogu_ilk")]))
    return root


for _k in range(1, KAT):
    model("ZB_kesit_firdevs" if _k == KAT - 1 else f"ZB_kesit_kat{_k + 1}")(lambda _k=_k: _kat_modeli(_k))


# --------------------------------------------------------------------------
# Yerleşim: ağaç siluetleri, yapı vekilleri, bulutlar, ölçüler
# --------------------------------------------------------------------------

def kesit_yerlesim_yaz(root: Path) -> Path:
    """game/data/dunya_kesit.json ve dunya_kesit_agac.bin.
    Ağaçlar ikili dosyada: kat başına float32 dizisi [x, y, z, ölçek, tür] × n
    (tür SILUET_TURLERI sırası). JSON'da her katın dizideki başlangıcı ve sayısı."""
    veri = {"olcu": {"kat": KAT, "kat_h": KAT_H, "kat_t": KAT_T, "hava": KAT_HAVA, "kesme_z": KESME_Z,
                     "pencere_m": PENCERE_M, "kamera": KESIT_KAMERA,
                     "kabuk_x": KABUK_X, "arka_z": ARKA_Z},
            "turler": SILUET_TURLERI, "katlar": []}
    parcalar = []
    bas = 0
    for k in range(1, KAT):
        kd = kat_dunyasi(k)
        satir = []
        for t, a in list(kd.agaclar.items()) + list(kd.yapilar.items()):
            if len(a) == 0:
                continue
            ti = SILUET_TURLERI.index(t)
            satir.append(np.column_stack([a[:, 0], a[:, 1], a[:, 2], a[:, 4], np.full(len(a), ti)]))
        s = np.vstack(satir).astype(np.float32) if satir else np.zeros((0, 5), np.float32)
        # Uzaktan yakına (kamera kuzeye bakar): saydam kenarlar doğru sıralansın
        s = s[np.argsort(s[:, 2])]
        parcalar.append(s.ravel())
        kat = {"k": k, "agac": [bas, len(s)], "isik": round(KARAKTERLER[k].isik, 4),
               "bulut": [[round(float(v), 1) for v in b] for b in kd.bulutlar],
               "selale_dip": [[round(x, 1), round(ya, 1), round(z, 1), round(g, 1)] for (x, z, ya, _, g, _) in kd.selaleler]}
        if kd.kaynak:
            kat["kaynak"] = [round(v, 1) for v in kd.kaynak]
        veri["katlar"].append(kat)
        bas += len(s)
    veri["ilk_kat"] = {"isik": 0.0}
    # Siluet atlası: gerçek modellerden önden çizilir (mf/siluet.py)
    from mf.doku import _import_ayari
    from mf.siluet import siluet_atlasi
    from . import load_all
    reg = load_all()
    dokular = root / "game" / "assets" / "dokular"
    atlas, meta = siluet_atlasi([(t, reg[SILUET_MODELLERI[t]]()) for t in SILUET_TURLERI], dokular, 128, 3)
    atlas.save(dokular / "kesit_siluet.png", optimize=True)
    _import_ayari(dokular / "kesit_siluet.png")
    veri["siluet"] = meta
    yol = root / "game" / "data" / "dunya_kesit.json"
    yol.write_text(json.dumps(veri, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (root / "game" / "data" / "dunya_kesit_agac.bin").write_bytes(np.concatenate(parcalar).astype("<f4").tobytes())
    return yol
