"""Dallanan ağaç üreteci (K15: biçim gerçekçi, ışık rüya gibi).

Ağaç, türün parametrelerinden özyinelemeli olarak kurulur:
  gövde (kök genişlemesi ve kök lobları ile) -> ana dallar -> ikincil dallar -> ...
Her dal, paralel taşınan çerçevelerle kıvrılan bir borudur. Borularda kabuk
dokusu için UV vardır; normaller yumuşaktır (köşeler paylaşılır).

Yapraklar, son seviyelerdeki dallar boyunca dizilen yaprak kümesi kartlarıdır
(mf/doku.py atlası). Kartların normalleri tacın dış yüzeyine doğru bükülür: taç
binlerce kart yerine tek bir kabarık kütle gibi ışık alır. Tacın içi ve altı
köşe renginde koyulaşır (ortam gölgesi).

Rüzgâr ağırlığı (COLOR.a) yalnızca konuma bağlıdır; dal ve kart aynı yerde
aynı miktarda salınır, kartlar dallardan kopmaz.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from .doku import atlas_uv
from .mesh import Mesh, icosphere
from .palette import renk

YUKARI = np.array([0.0, 1.0, 0.0])


# --------------------------------------------------------------------------
# Parametreler
# --------------------------------------------------------------------------

@dataclass
class Seviye:
    """Bir dal seviyesi: ebeveyn dal boyunca çıkan çocuk dallar."""
    sayi: int                       # ebeveyn başına çocuk dal
    bas: float = 0.3                # ebeveyn boyunca ilk çıkış yeri (0 dip, 1 uç)
    son: float = 1.0
    aci: float = 50.0               # ebeveyn eksenine göre açı (derece)
    aci_sapma: float = 10.0
    uzunluk: float = 0.5            # ebeveyn uzunluğuna oran
    sekil: str = "konik"            # çıkış yerine göre uzunluk çarpanı (_sekil)
    egim: float = 0.0               # + yukarı kıvrılır, - sarkar (dal boyunca toplam, radyan)
    kivrim: float = 0.2             # rastgele kıvrım (dal boyunca toplam, radyan)
    yaricap: float = 0.6            # ebeveynin o noktadaki yarıçapına oran
    uc: float = 0.3                 # uç yarıçapı / dip yarıçapı
    segment: int = 6                # halka köşe sayısı
    adim: float = 0.5               # halka aralığı (metre, en az 3 halka)
    donus: float = 137.5            # ardışık çocukların eksen etrafındaki açı farkı
    yukari: float = 0.0             # çıkış yönünü dünya yukarısına çekme (0-1)


@dataclass
class YaprakAyar:
    malzeme: str                    # glTF malzemesi, ör. "yaprak_koru"
    seviyeler: tuple = (2,)         # kartların dizildiği dal seviyeleri
    siklik: float = 2.0             # dal metresi başına kart
    bas: float = 0.3                # dal boyunca kartların başladığı yer
    boy: tuple = (0.8, 1.1)         # kart boyu (metre)
    en: float = 0.9                 # kart eni / boyu
    disa: float = 0.8               # kartın dala göre dışa açılması
    yukari: float = 0.35            # kart yönünün yukarı eğilimi
    bukum: float = 0.12             # kartın ortadan bükülmesi (boya oranla)
    uc_karti: bool = True           # her dalın ucuna bir kart
    uc_kumesi: tuple = (0, 1)       # bu seviyelerin (gövde, ana dallar) ucuna birkaç kartlık küme
    renk: tuple = (255, 255, 255)   # kartların köşe rengi (doku ile çarpılır)
    renk_oynama: float = 0.08
    golge: float = 0.55             # tacın içindeki koyulaşma
    alt_golge: float = 0.25         # tacın altındaki koyulaşma
    dis_normal: float = 0.8         # normalin taç yüzeyine bükülme oranı
    oz: float = 0.0                 # > 0 ise tacın içine bu oranda koyu bir öz hacim (uzaktan dolu görünür)
    oz_renk: tuple = (40, 90, 52)


@dataclass
class AgacTuru:
    boy: float                      # gövde uzunluğu (taç içinde biter)
    govde_r: float                  # gövde dip yarıçapı
    seviyeler: list = field(default_factory=list)
    yaprak: YaprakAyar | None = None
    govde_uc: float = 0.25          # gövde ucu yarıçap oranı
    govde_segment: int = 12
    govde_adim: float = 0.45
    govde_egim: float = 3.0         # gövdenin dikten sapması (derece)
    govde_kivrim: float = 0.15
    kok: float = 0.7                # kök genişlemesi (yarıçapa oran)
    kok_boy: float = 3.0            # genişlemenin yüksekliği (gövde yarıçapı cinsinden)
    kok_lob: int = 5                # kök lobları (payanda kökler)
    kabuk_renk: tuple = (118, 98, 80)
    kabuk_renk_uc: tuple = (112, 104, 70)   # ince dalların rengi (yeşile çalan)
    kabuk_doku: float = 0.7         # kabuk dokusunun bir tekrarının boyu (metre)
    tohum: int = 0


def _sekil(ad: str, t: float) -> float:
    if ad == "konik":
        return 0.25 + 0.75 * (1 - t)
    if ad == "kure":
        return 0.25 + 0.75 * math.sin(math.pi * t)
    if ad == "yarim_kure":
        return 0.25 + 0.75 * math.cos(math.pi * 0.5 * t)
    if ad == "alev":
        return 0.25 + 0.75 * (t / 0.7 if t < 0.7 else (1 - t) / 0.3)
    if ad == "ters_konik":
        return 0.25 + 0.75 * t
    if ad == "silindir":
        return 1.0
    if ad == "mizrak":                                      # selvi: dipte dolgun, uca doğru incelir
        return 0.55 + 0.45 * t / 0.22 if t < 0.22 else 1.0 - 0.9 * ((t - 0.22) / 0.78) ** 1.2
    raise ValueError(ad)


# --------------------------------------------------------------------------
# İskelet
# --------------------------------------------------------------------------

@dataclass
class Dal:
    P: np.ndarray                   # (n, 3) eksen noktaları
    R: np.ndarray                   # (n,) yarıçaplar
    seviye: int
    segment: int
    s: np.ndarray                   # (n,) dip noktasından yay uzunluğu

    @property
    def uzunluk(self) -> float:
        return float(self.s[-1])

    def nokta(self, t: float):
        """t (0-1) yerindeki nokta, teğet ve yarıçap."""
        u = t * self.uzunluk
        i = int(np.clip(np.searchsorted(self.s, u) - 1, 0, len(self.s) - 2))
        f = (u - self.s[i]) / max(self.s[i + 1] - self.s[i], 1e-9)
        p = self.P[i] * (1 - f) + self.P[i + 1] * f
        tn = self.P[i + 1] - self.P[i]
        tn = tn / (np.linalg.norm(tn) + 1e-12)
        return p, tn, float(self.R[i] * (1 - f) + self.R[i + 1] * f)


def _dik(v):
    ref = np.array([1.0, 0, 0]) if abs(v[0]) < 0.9 else np.array([0, 0, 1.0])
    u = np.cross(v, ref)
    return u / np.linalg.norm(u)


def _dondur(v, eksen, aci):
    """v'yi eksen etrafında aci (radyan) döndürür (Rodrigues)."""
    k = eksen / (np.linalg.norm(eksen) + 1e-12)
    return v * math.cos(aci) + np.cross(k, v) * math.sin(aci) + k * np.dot(k, v) * (1 - math.cos(aci))


def _yol(bas, yon, uzunluk, adim, egim, kivrim, rng):
    """Kıvrılan dal ekseni. egim: dal boyunca yukarıya (+) ya da aşağıya (-) toplam
    dönüş; kivrim: rastgele sapma."""
    n = max(3, int(math.ceil(uzunluk / adim)) + 1)
    ds = uzunluk / (n - 1)
    d = np.asarray(yon, float) / np.linalg.norm(yon)
    P = [np.asarray(bas, float)]
    faz = rng.uniform(0, 2 * math.pi, 2)
    for i in range(1, n):
        # yukarı/aşağı kıvrılma: yatay bileşeni olan dallarda etkili
        yatay = YUKARI - d * np.dot(d, YUKARI)
        if np.linalg.norm(yatay) > 1e-6:
            d = d + yatay / np.linalg.norm(yatay) * math.tan(egim / (n - 1))
        # rastgele kıvrım: yumuşak (sinüs) + gürültü
        e = _dik(d)
        e2 = np.cross(d, e)
        t = i / (n - 1)
        d = d + (e * math.sin(faz[0] + t * 5.0) + e2 * math.cos(faz[1] + t * 4.0)) * kivrim / (n - 1) * 1.4
        d = d + rng.normal(0, kivrim * 0.35 / math.sqrt(n), 3)
        d /= np.linalg.norm(d)
        P.append(P[-1] + d * ds)
    return np.array(P)


def iskelet(tur: AgacTuru, olcek: float = 1.0, seviye_sayisi: int | None = None):
    """Ağacın dallarını üretir. olcek genç aşamalar için bütün boyları küçültür;
    seviye_sayisi verilirse daha ince seviyeler üretilmez."""
    rng = np.random.default_rng(tur.tohum)
    sev = tur.seviyeler[:seviye_sayisi] if seviye_sayisi is not None else tur.seviyeler
    # Gövde
    egim_yon = rng.uniform(0, 2 * math.pi)
    yon = np.array([math.sin(math.radians(tur.govde_egim)) * math.cos(egim_yon), math.cos(math.radians(tur.govde_egim)),
                    math.sin(math.radians(tur.govde_egim)) * math.sin(egim_yon)])
    L = tur.boy * olcek
    P = _yol(np.array([0.0, -0.15 * olcek, 0.0]), yon, L, tur.govde_adim * olcek, 0.0, tur.govde_kivrim, rng)
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    r0 = tur.govde_r * olcek
    R = r0 * (1 - (1 - tur.govde_uc) * (s / s[-1]) ** 0.9)
    dallar = [Dal(P, R, 0, tur.govde_segment, s)]
    ebeveynler = [dallar[0]]
    for li, sv in enumerate(sev):
        yeni = []
        for eb in ebeveynler:
            n = sv.sayi
            if eb.seviye > 0:
                n = max(1, int(round(n * min(1.0, eb.uzunluk / (L * 0.35)) ** 0.5)))
            faz0 = rng.uniform(0, 360)
            for i in range(n):
                t = sv.bas + (sv.son - sv.bas) * (i + rng.uniform(0.2, 0.8)) / n
                p, tn, r_eb = eb.nokta(t)
                ek = _dik(tn)
                ek2 = np.cross(tn, ek)
                fi = math.radians(faz0 + i * sv.donus + rng.uniform(-15, 15))
                radyal = ek * math.cos(fi) + ek2 * math.sin(fi)
                a = math.radians(sv.aci + rng.uniform(-sv.aci_sapma, sv.aci_sapma))
                d = tn * math.cos(a) + radyal * math.sin(a)
                if sv.yukari > 0:
                    d = d * (1 - sv.yukari) + YUKARI * sv.yukari
                tt = (t - sv.bas) / max(sv.son - sv.bas, 1e-6)
                uz = eb.uzunluk * sv.uzunluk * _sekil(sv.sekil, tt) * rng.uniform(0.85, 1.15)
                if eb.seviye == 0:
                    uz = L * sv.uzunluk * _sekil(sv.sekil, tt) * rng.uniform(0.85, 1.15)
                r = min(r_eb * sv.yaricap, r_eb * 0.9)
                if uz < 0.08 * olcek or r < 0.003:
                    continue
                Pc = _yol(p, d, uz, sv.adim * max(olcek, 0.4), sv.egim, sv.kivrim, rng)
                sc = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(Pc, axis=0), axis=1))])
                Rc = r * (1 - (1 - sv.uc) * sc / sc[-1])
                yeni.append(Dal(Pc, Rc, li + 1, sv.segment, sc))
        dallar += yeni
        ebeveynler = yeni
    return dallar


# --------------------------------------------------------------------------
# Örgü
# --------------------------------------------------------------------------

def _cerceveler(P):
    """Paralel taşınan çerçeveler: (T, U, V), her biri (n, 3)."""
    n = len(P)
    T = np.zeros((n, 3))
    for i in range(n):
        t = P[min(i + 1, n - 1)] - P[max(i - 1, 0)]
        T[i] = t / (np.linalg.norm(t) + 1e-12)
    U = np.zeros((n, 3))
    U[0] = _dik(T[0])
    for i in range(1, n):
        u = U[i - 1] - np.dot(U[i - 1], T[i]) * T[i]
        U[i] = u / (np.linalg.norm(u) + 1e-12)
    V = np.cross(T, U)
    return T, U, V


def _boru(dal: Dal, tur: AgacTuru, govde: bool):
    """Dalın borusu: köşeler, yüzler, normaller, UV (halkada dikiş köşesi çifttir)."""
    P, R, seg = dal.P, dal.R.copy(), dal.segment
    T, U, V = _cerceveler(P)
    n = len(P)
    a = np.linspace(0, 2 * math.pi, seg + 1)
    ca, sa = np.cos(a), np.sin(a)
    carpan = np.ones((n, seg + 1))
    if govde and tur.kok > 0:
        yuk = np.clip(P[:, 1] / (tur.kok_boy * dal.R[0]), 0, 1)
        g = (1 - yuk) ** 2.5
        faz = 0.7
        lob = np.clip(np.sin(a * tur.kok_lob + faz), 0, 1) ** 1.5
        carpan = 1 + g[:, None] * tur.kok * (0.45 + 0.55 * lob[None])
    radyal = ca[None, :, None] * U[:, None] + sa[None, :, None] * V[:, None]      # (n, seg+1, 3)
    Vx = P[:, None] + radyal * (R[:, None] * carpan)[..., None]
    # Normal: radyal, daralmaya göre hafif eksene eğik
    dr = np.gradient(R * carpan.mean(1), dal.s) if n > 1 else np.zeros(n)
    N = radyal - T[:, None] * dr[:, None, None]
    N /= np.linalg.norm(N, axis=-1, keepdims=True)
    tekrar = max(1, int(round(2 * math.pi * R[0] / tur.kabuk_doku)))
    u = np.linspace(0, tekrar, seg + 1)
    v = dal.s / tur.kabuk_doku
    UV = np.stack([np.broadcast_to(u[None], (n, seg + 1)), np.broadcast_to(-v[:, None], (n, seg + 1))], -1)
    F = []
    w = seg + 1
    for i in range(n - 1):
        for k in range(seg):
            a0, b0 = i * w + k, i * w + k + 1
            c0, d0 = (i + 1) * w + k + 1, (i + 1) * w + k
            F += [[a0, b0, c0], [a0, c0, d0]]
    return Vx.reshape(-1, 3), np.array(F, np.int64), N.reshape(-1, 3), UV.reshape(-1, 2)


def _kart(taban, yon, en_yon, boy, en, bukum):
    """Kıvrık yaprak kartı: 2×3 köşe, 4 üçgen. taban kartın alt ortası."""
    nrm = np.cross(en_yon, yon)
    orta = taban + yon * boy * 0.5 + nrm * bukum * boy
    ust = taban + yon * boy
    V = np.array([taban - en_yon * en * 0.5, taban + en_yon * en * 0.5,
                  orta - en_yon * en * 0.5, orta + en_yon * en * 0.5,
                  ust - en_yon * en * 0.5, ust + en_yon * en * 0.5])
    F = np.array([[0, 1, 3], [0, 3, 2], [2, 3, 5], [2, 5, 4]])
    return V, F, nrm


def _kartlar(dallar, tur: AgacTuru, olcek, rng):
    ya = tur.yaprak
    V, F, UV, FN = [], [], [], []
    son_seviye = max(d.seviye for d in dallar)
    for dal in dallar:
        if dal.seviye in ya.seviyeler:
            n = int(ya.siklik * dal.uzunluk / max(olcek, 0.4) + rng.uniform(0, 1))
            ts = list(np.sort(rng.uniform(ya.bas, 1.0, n)))
            if ya.uc_karti:
                ts.append(1.0)
        elif dal.seviye in ya.uc_kumesi and dal.seviye < son_seviye:
            # Çıplak kalan uçlar (gövdenin tepesi, ana dal uçları) yapraksız çubuk gibi görünmesin
            ts = list(rng.uniform(0.9, 0.99, 3)) + [1.0]
        else:
            continue
        for t in ts:
            p, tn, r = dal.nokta(min(t, 1.0))
            e = _dik(tn)
            fi = rng.uniform(0, 2 * math.pi)
            radyal = e * math.cos(fi) + np.cross(tn, e) * math.sin(fi)
            if t >= 1.0:
                yon = tn + YUKARI * ya.yukari * 0.5
            else:
                yon = tn * (1 - ya.disa) + radyal * ya.disa + YUKARI * ya.yukari
            yon = yon + rng.normal(0, 0.15, 3)
            yon /= np.linalg.norm(yon)
            en_yon = np.cross(yon, YUKARI)
            if np.linalg.norm(en_yon) < 1e-3:
                en_yon = _dik(yon)
            en_yon /= np.linalg.norm(en_yon)
            en_yon = _dondur(en_yon, yon, rng.uniform(-0.9, 0.9))
            boy = rng.uniform(*ya.boy) * max(olcek, 0.45)
            v, f, nrm = _kart(p + radyal * r * 0.5, yon, en_yon, boy, boy * ya.en, ya.bukum * rng.uniform(-1, 1))
            u0, v0, u1, v1 = atlas_uv(int(rng.integers(4)))
            if rng.random() < 0.5:
                u0, u1 = u1, u0
            F.append(f + len(V) * 6)
            V.append(v)
            UV.append(np.array([[u0, v1], [u1, v1], [u0, (v0 + v1) / 2], [u1, (v0 + v1) / 2], [u0, v0], [u1, v0]]))
            FN.append(np.repeat(nrm[None], 6, 0))
    if not V:
        return None
    return np.vstack(V), np.vstack(F), np.vstack(UV), np.vstack(FN)


# --------------------------------------------------------------------------
# Ağaç
# --------------------------------------------------------------------------

def _rgb(c):
    return np.asarray(renk(c) if isinstance(c, str) else c, np.float32) / 255.0


def agac(tur: AgacTuru, olcek: float = 1.0, seviye_sayisi: int | None = None, yaprakli: bool = True):
    """(kabuk Mesh, yapraklar [Mesh], dallar, ruzgar). Kabuk malzemesi "kabuk"; yapraklar
    kartlar ve (tür istiyorsa) öz hacimdir. ruzgar(X) konumdan rüzgâr ağırlığı verir:
    dallara asılan meyveler de aynı ağırlığı alır."""
    rng = np.random.default_rng(tur.tohum + 1000)
    dallar = iskelet(tur, olcek, seviye_sayisi)
    kartlar = _kartlar(dallar, tur, olcek, rng) if (yaprakli and tur.yaprak) else None
    # Tacın zarfı (elips): kartlardan, kart yoksa dal uçlarından
    if kartlar is not None:
        noktalar = kartlar[0]
    else:
        noktalar = np.vstack([d.P[-1:] for d in dallar])
    merkez = noktalar.mean(0)
    yari = np.maximum(np.percentile(np.abs(noktalar - merkez), 92, axis=0), 0.3 * olcek)
    gov = dallar[0].P

    def ruzgar(X):
        yatay = np.linalg.norm(X[:, [0, 2]] - gov[0, [0, 2]], axis=1)
        yuk = np.clip((X[:, 1] - gov[0, 1]) / (gov[-1, 1] - gov[0, 1] + 1e-6), 0, 1.3)
        return np.clip((yatay / (yari[[0, 2]].max() + 1e-6)) ** 1.3 * 0.9 + yuk ** 2 * 0.25, 0, 1)

    def golge(X, guc, alt):
        e = np.linalg.norm((X - merkez) / yari, axis=1)
        g = 1 - guc * np.clip(1 - e, 0, 1) ** 0.8
        g *= 1 - alt * np.clip((merkez[1] - X[:, 1]) / yari[1], 0, 1)
        return g

    # Kabuk
    Vs, Fs, Ns, UVs, Cs = [], [], [], [], []
    k_dip, k_uc = _rgb(tur.kabuk_renk), _rgb(tur.kabuk_renk_uc)
    enkalin = dallar[0].R[0]
    off = 0
    for dal in dallar:
        v, f, nr, uv = _boru(dal, tur, dal.seviye == 0)
        ince = np.clip(1 - np.repeat(dal.R, dal.segment + 1) / (enkalin * 0.35), 0, 1)
        c = k_dip[None] * (1 - ince[:, None]) + k_uc[None] * ince[:, None]
        Vs.append(v)
        Fs.append(f + off)
        Ns.append(nr)
        UVs.append(uv)
        Cs.append(c)
        off += len(v)
    V = np.vstack(Vs).astype(np.float32)
    CV = np.vstack(Cs) * golge(V, 0.3, 0.12)[:, None]
    F = np.vstack(Fs)
    kabuk = Mesh(V, F, np.tile(k_dip, (len(F), 1)), "kabuk", W=ruzgar(V).astype(np.float32),
                 NV=np.vstack(Ns).astype(np.float32), CV=np.clip(CV, 0, 1).astype(np.float32),
                 UV=np.vstack(UVs).astype(np.float32))
    yapraklar = []
    if kartlar is not None:
        yapraklar = yaprak_orgusu(kartlar, tur.yaprak, merkez, yari, ruzgar, golge, rng, tur.tohum)
    return kabuk, yapraklar, dallar, ruzgar


def yaprak_orgusu(kartlar, ya: YaprakAyar, merkez, yari, ruzgar, golge, rng, tohum=0):
    """Kartlardan yaprak Mesh'i (ve istenirse öz hacim): normaller taç zarfına (elips) bükülür,
    köşe rengi taç içinde koyulaşır. golge(X, guc, alt) koyulaşmayı verir."""
    V, F, UV, FN = kartlar
    dis = (V - merkez) / yari ** 2
    dis /= np.linalg.norm(dis, axis=1, keepdims=True) + 1e-9
    # Kart yüzünün normalini dışa bakan tarafa çevir, sonra taç yüzeyine bük
    yuz = FN * np.sign(np.sum(FN * dis, axis=1, keepdims=True) + 1e-6)
    N = yuz * (1 - ya.dis_normal) + dis * ya.dis_normal
    N /= np.linalg.norm(N, axis=1, keepdims=True)
    c = _rgb(ya.renk)
    kart_say = len(V) // 6
    oyn = 1 + rng.uniform(-ya.renk_oynama, ya.renk_oynama, (kart_say, 1)) * np.array([[1.0, 0.8, 1.3]])
    CV = np.repeat(c[None] * oyn, 6, 0) * golge(V, ya.golge, ya.alt_golge)[:, None]
    out = [Mesh(V.astype(np.float32), F, np.tile(c, (len(F), 1)), ya.malzeme, W=ruzgar(V).astype(np.float32),
                NV=N.astype(np.float32), CV=np.clip(CV, 0, 1).astype(np.float32), UV=UV.astype(np.float32))]
    if ya.oz > 0:
        oz = icosphere(1.0, 1, tuple(_rgb(ya.oz_renk))).scale(*(yari * ya.oz)).jitter(0.06 * float(yari.min()), tohum)
        oz = oz.translate(*merkez).kure_normal(merkez, tuple(yari)).with_material("yaprak")
        oz.W = ruzgar(oz.V).astype(np.float32) * 0.7
        out.append(oz)
    return out


def meyve_yerleri(dallar, seviyeler, sayi, tohum, bas=0.45):
    """Meyvelerin asılacağı dal noktaları: [(nokta, teğet, yarıçap)], ince dallardan."""
    rng = np.random.default_rng(tohum)
    adaylar = [d for d in dallar if d.seviye in seviyeler]
    if not adaylar:
        return []
    agirlik = np.array([d.uzunluk for d in adaylar])
    out = []
    for i in rng.choice(len(adaylar), size=sayi, p=agirlik / agirlik.sum()):
        out.append(adaylar[i].nokta(rng.uniform(bas, 1.0)))
    return out
