"""Dünya yuvaları (K20): zikirle gelen nimetlerin ilk kattaki sabit yerleri.

Oyun boş başlar; ağaç, çiçek, yapı ve obje zikirle gelir (K16, K20). Her asset'in dünyada
sabit yuvaları vardır. Olgun örnekler asset'in ilk yuvalarına, büyüyen örnek bir sonrakine
konur (game/core/dunya_durumu.gd). Yuvalar game/data/dunya_cennet.json "yuvalar" alanına yazılır:

  {"arsa": [yuva, ...], "cevre": [yuva, ...], "ayak": {asset_id: taban yarıçapı (ölçeksiz, m)}}
  yuva: [x, y, z, dönüş (derece, y ekseni), ölçek, asset_id, sıra]

Bölgeler:
  arsa   oyuncunun arsası (Tûbâ orijinde). Ağaçlar dış halkada (r 8-11 m), çiçek tarhları iç
         halkada, küçük objeler Tûbâ'nın dibinde ve sınırda, bahçe kapısı doğu kenarında.
  cevre  arsanın dışı, 13-120 m: türlere göre kümeler; ırmak koridorlarının (a + banka + 22 m),
         vitrin yapılarının (cennet.py yerlesim() "yapilar") ve çevre korularının (yerlesim()
         "koru"; "on misli yankı" ile yuvalardaki ağaçlarla aynı anda görünür) dışında, kesme
         düzleminin gerisinde.

Sıra kalıcıdır. Bir asset'in yuvaları sıraya göre dolar; oyuncunun üçüncü olgun hurması hep
aynı yuvada durur. Sıra numarası koy() çağrılarının sırasıyla verilir: önce _arsa(), sonra
_cevre(). KURAL: liste yalnız sona eklenir. Var olan bir grubun adedi ve sırası değiştirilmez;
yeni yuvalar yalnız yuvalar() fonksiyonunun sonuna, _cevre()'den sonra, yeni bir grup olarak
eklenir. _arsa() ya da _cevre() içine eklenen bir yuva sonraki bütün sıraları kaydırır; aynı
asset'in yuvaları yer değiştirir ve oyuncunun olgun ağaçları başka yere taşınır.

Konumlar sıra kadar kalıcı değildir. koy() ile konan tek yuva, yeri dolarsa en yakın boş yere
(itme payı kadar) kayar. _kume() tohumlu, reddetmeli örnekleme yapar: ırmaklar, yapılar ya da
korular değişirse kümedeki bütün konumlar ve kümenin yakından uzağa dizilişi değişebilir (adet
ve sıra numaraları değişmez).

Uzun öğeler (ağaçlar, kapı, yapılar) arsa ve ufuk kameralarının dikey (720x1280) kadrajında,
kamera ile Tûbâ arasında durmaz.
"""
from __future__ import annotations

import math

import numpy as np

from .cennet import ARSA_R, KESME_Z

# Kameralar (cennet.py yerlesim() "kameralar"): konum (x, z), hedef (x, z), kadrajın kapanmaması
# gereken uzaklık. Arsa kamerası: kamera ile Tûbâ arası. Ufuk kamerası 17 m yukarıdadır; ağaçlar
# ufku ancak yakındayken kapatır.
ARSA_KAMERA = ((9.0, 21.0), (-2.0, -40.0), math.hypot(9.0, 21.0) + 1.0)
UFUK_KAMERA = ((12.0, 38.0), (-10.0, -700.0), 25.0)
# Dikey ekranda (720x1280, düşey görüş 55°) yatay yarım görüş açısı ve pay (derece)
KADRAJ_YARI_ACI = math.degrees(math.atan(math.tan(math.radians(27.5)) * 720 / 1280)) + 2.0
KAMERA_PAYI = 6.0            # uzun öğeler kameraya bundan yakın durmaz

IRMAK_PAYI = 22.0            # ırmak koridoru: yatak (a) + banka + 22 m
CEVRE_R = (13.0, 120.0)      # çevre yuvalarının uzaklığı (arsanın ortasından)
SINIR_PAYI = 1.0             # çevre yuvaları çakıl sınırının en az bu kadar dışında
KESIT_PAYI = 8.0             # çevre yuvaları kesme düzleminin (KESME_Z) gerisinde kalır
KAPI_ACISI = 155.0           # bahçe kapısının arsa ortasına göre yönü (+z'den doğuya, derece); arsa
                             # kamerasının ~4° sağında, arsanın kuzeyinde; ovaya açılır (108°'de kadraj dışında kalıyordu)
ITME_ADIMI = 0.5             # yuva dolu bir yere düşerse bu adımlarla en yakın boş yer aranır
# Çevre korusu (ZB_bitki_koru_agac): taç yarıçapı (ölçeksiz, m). Modelin tacı gövdeden 4-6 m
# uzanır (kutusu x -4,0..5,9, z -6,1..4,2). Hiçbir yuva bir koru tacının içinde durmaz.
KORU_TAC = 5.0

# Taban yarıçapı (ölçeksiz, m): yuvalar arasında çakışma denetimi (oyundaki test de kullanır).
# Üretilmemiş modeller (gül, bahar dalı, kitabe, temel taşı, parsel kapısı, sur) tahminidir.
AYAK = {
    "tuba": 2.3,
    "hurma_agaci": 0.6, "cinar": 1.0, "servi": 0.5, "uzum_asmasi_ve_cardak": 2.4,
    "kirmizi_gul": 0.35, "beyaz_gul": 0.35, "lale": 0.18, "bahar_dali": 0.6,
    "bahce_kapisi": 1.5, "masaallah_kitabesi": 0.7, "temel_tasi": 0.5,
    "kosk": 2.4, "sadirvan": 2.1, "ab_i_hayat_pinari": 2.0, "parsel_kapisi_ve_anahtar": 1.8,
    "sur_parcalari": 1.9,
    "kandil": 0.5, "fener_ve_kutup_yildizi": 0.16, "rahle_ve_kitap": 0.25, "tesbih": 0.2,
    "define_sandigi": 0.38, "inci": 0.15, "mercan": 0.19, "sedef": 0.2, "hediye_bohcasi": 0.19,
    "ipek_kozasi": 0.2, "ari_kovani": 0.4,
}
# Uzun öğelerin taç yarıçapı (ölçeksiz, m): çevrede ağaçlar birbirinin tacına girmesin
TAC = {"hurma_agaci": 3.2, "cinar": 5.2, "servi": 1.4, "uzum_asmasi_ve_cardak": 3.2, "bahar_dali": 1.2,
       "kosk": 2.4, "sadirvan": 2.1, "parsel_kapisi_ve_anahtar": 1.8, "sur_parcalari": 1.9,
       "bahce_kapisi": 1.5}
UZUN = set(TAC) | {"tuba"}


def sinir_r(th: float) -> float:
    """Çakıl sınırının arsa ortasına uzaklığı (cennet.py yerlesim() "inci_cakil" halkası)."""
    kenar = 1.1 * math.sin(th * 5 + 0.7) + 0.6 * math.sin(th * 11 + 2.0)
    return ARSA_R - 0.4 - kenar


def _kutup(aci_derece: float, r: float):
    """Arsa ortasına göre konum: açı +z'den (arsa kamerası yönü) +x'e (doğu) doğru."""
    a = math.radians(aci_derece)
    return r * math.sin(a), r * math.cos(a)


def _yuze_don(x: float, z: float, hx: float = 0.0, hz: float = 0.0) -> float:
    """Modelin önü (+z) (hx, hz) noktasına baksın: y dönüşü (derece)."""
    return math.degrees(math.atan2(hx - x, hz - z))


class _Yerlestirici:
    def __init__(self, irmaklar, yapilar, yerde, korular=()):
        self.irmaklar = irmaklar
        self.yapilar = list(yapilar)
        # (x, z, taç yarıçapı): cennet.py yerlesim() "koru" örnekleri [x, y, z, dönüş, ölçek, ...]
        self.korular = [(float(k[0]), float(k[2]), KORU_TAC * float(k[4])) for k in korular]
        self.yerde = yerde
        self.konan = []            # (bölge, x, z, dönüş, ölçek, asset, sıra, dy)
        self.sira = 0

    # --- Denetimler (None: uygun; değilse nedeni)
    def neden(self, bolge, asset, x, z, olcek):
        ayak = AYAK[asset] * olcek
        r = math.hypot(x, z)
        th = math.atan2(x, z)
        if bolge == "arsa":
            sinir = sinir_r(th)
            if asset == "bahce_kapisi":
                if abs(r - sinir) > 0.3:
                    return "kapı çakıl sınırında değil"
            elif r + ayak > min(sinir, ARSA_R) - 0.3:
                return "arsanın dışına taşıyor"
        else:
            if r - ayak < max(CEVRE_R[0], sinir_r(th) + SINIR_PAYI) or r > CEVRE_R[1]:
                return "çevre halkasının dışında"
            if z > KESME_Z - KESIT_PAYI:
                return "kesme düzlemine yakın"
            X = np.array([[x, z]])
            for ir in self.irmaklar:
                d, i = ir.uzaklik(X)
                if d[0] < ir.a[i[0]] + ir.banka()[i[0]] + IRMAK_PAYI + ayak:
                    return "ırmak koridorunda: " + ir.ad
            for (yx, yz, yr) in self.yapilar:
                if math.hypot(x - yx, z - yz) < yr + ayak:
                    return "vitrin yapısının yerinde"
        # Koru ağaçları: yuva tacın altına girmez; uzun öğelerin tacı koru tacıyla iç içe geçmez
        # (ağaçlar arasındaki kuralla aynı pay)
        for (kx, kz, kr) in self.korular:
            d = math.hypot(x - kx, z - kz)
            if d < kr + ayak:
                return "koru tacının altında"
            if asset in TAC and d < 0.8 * (kr + TAC[asset] * olcek):
                return "tacı bir koru tacının içinde"
        if asset in UZUN and asset != "tuba":
            for (kx, kz), (hx, hz), menzil in (ARSA_KAMERA, UFUK_KAMERA):
                vx, vz = x - kx, z - kz
                d = math.hypot(vx, vz)
                if d < KAMERA_PAYI + TAC[asset] * olcek:
                    return "kameraya çok yakın"
                bx, bz = hx - kx, hz - kz
                cos = (vx * bx + vz * bz) / (d * math.hypot(bx, bz))
                aci = math.degrees(math.acos(max(-1.0, min(1.0, cos))))
                yari = math.degrees(math.atan2(TAC[asset] * olcek, d))
                if aci - yari < KADRAJ_YARI_ACI and d - TAC[asset] * olcek < menzil:
                    return "kadrajı kapatıyor"
        for (b2, x2, z2, _r2, o2, a2, _s2, _dy2) in self.konan:
            d = math.hypot(x - x2, z - z2)
            if d < ayak + AYAK[a2] * o2:
                return "başka yuvayla çakışıyor: " + a2
            if bolge == "cevre" and asset in TAC and a2 in TAC and d < 0.8 * (TAC[asset] * olcek + TAC[a2] * o2):
                return "tacı başka bir tacın içinde: " + a2
        return None

    def koy(self, bolge, asset, x, z, olcek=1.0, rot=None, dy=0.0, itme=2.0, yuz=None):
        """Yuvayı koyar; yer doluysa en yakın boş yere (itme metreye kadar) iter. Sıra kalıcıdır:
        her çağrı bir sonraki sıra numarasını alır. rot: dönüş (derece); yuz: (hx, hz) bakılacak
        nokta (itildikten sonra hesaplanır)."""
        aday = [(x, z)]
        k = 1
        while k * ITME_ADIMI <= itme:
            n = 8 * k
            for j in range(n):
                a = 2 * math.pi * j / n
                aday.append((x + k * ITME_ADIMI * math.cos(a), z + k * ITME_ADIMI * math.sin(a)))
            k += 1
        ilk = None
        for (cx, cz) in aday:
            n = self.neden(bolge, asset, cx, cz, olcek)
            if n is None:
                if yuz is not None:
                    rot = _yuze_don(cx, cz, *yuz)
                self.konan.append((bolge, cx, cz, 0.0 if rot is None else rot, olcek, asset, self.sira, dy))
                self.sira += 1
                return cx, cz
            ilk = ilk or n
        raise ValueError(f"Yuva konamadı: {asset} ({x:.1f}, {z:.1f}) {bolge}: {ilk}")

    def sonuc(self) -> dict:
        out = {"arsa": [], "cevre": []}
        for (bolge, x, z, rot, olcek, asset, sira, dy) in self.konan:
            out[bolge].append([round(float(x), 2), round(float(self.yerde(x, z)) + dy, 2), round(float(z), 2),
                               round(float(rot) % 360.0, 1), round(float(olcek), 2), asset, sira])
        out["ayak"] = dict(AYAK)
        return out


# --------------------------------------------------------------------------
# Arsa
# --------------------------------------------------------------------------

def _arsa(y: _Yerlestirici, rng) -> None:
    def kutup(asset, aci, r, olcek=1.0, rot=None, yuz=(0.0, 0.0), dy=0.0, itme=1.0):
        x, z = _kutup(aci, r)
        y.koy("arsa", asset, x, z, olcek, rot=rot, yuz=None if rot is not None else yuz, dy=dy, itme=itme)

    def rastgele():
        return float(rng.uniform(0, 360))

    # Tûbâ: ortada (aşama 0'da süzülen çekirdek sahnenin işidir; yuva a1'den itibaren dolar)
    y.koy("arsa", "tuba", 0.0, 0.0, 1.0, rot=0.0, itme=0.0)
    # Bahçe kapısı (ilk Bismillah): kuzeydoğu kenarında, çakıl sınırının üstünde; önü arsaya bakar.
    # Arsa kamerasından görünür: Tûbâ solda, kapı sağ arkada; kamerayı kapatmaz.
    aci = KAPI_ACISI
    x, z = _kutup(aci, sinir_r(math.radians(aci)))
    y.koy("arsa", "bahce_kapisi", x, z, 1.0, rot=aci + 180.0, itme=0.0)
    # Kapının iki yanında, içeride: Mâşâallah kitabesi (Kehf 39) ve temel taşı; girene bakar
    for asset, a in (("masaallah_kitabesi", aci - 11.0), ("temel_tasi", aci + 11.0)):
        kutup(asset, a, min(sinir_r(math.radians(a)), ARSA_R) - 1.0 - AYAK[asset], rot=a)

    # Ağaçlar: dış halka (r 8-11 m), Tûbâ'nın arkası ve yanları; ön taraf (kamera) açık kalır.
    # Her türün ilk yuvası arsa kamerasından görünen yerdedir.
    for asset, aci, r, olcek in (("servi", 158.0, 9.0, 1.0), ("hurma_agaci", 183.0, 10.0, 1.05),
                                 ("uzum_asmasi_ve_cardak", 132.0, 10.2, 0.95), ("cinar", 210.0, 10.4, 0.85),
                                 ("servi", 236.0, 9.2, 1.0), ("hurma_agaci", 262.0, 10.0, 0.95),
                                 ("servi", 292.0, 9.6, 1.05)):
        kutup(asset, aci, r, olcek, rot=rastgele())

    # Çiçek tarhları: iç halka (r 4-6.5 m). Lale önde (kameraya bakan yüz), güller yanlarda,
    # bahar dalları arkada.
    def tarh(asset, aci0, aci1, r0, r1, n, olcek):
        for k in range(n):
            t = (k + 0.5) / n
            a = aci0 + (aci1 - aci0) * t + float(rng.uniform(-2.5, 2.5))
            r = r0 + (r1 - r0) * ((k * 0.618) % 1.0) + float(rng.uniform(-0.15, 0.15))
            kutup(asset, a, r, olcek * float(rng.uniform(0.92, 1.08)), rot=rastgele(), itme=0.8)

    tarh("lale", -8.0, 52.0, 4.2, 6.2, 12, 1.5)
    tarh("kirmizi_gul", 292.0, 338.0, 4.4, 6.2, 6, 1.2)
    tarh("beyaz_gul", 62.0, 96.0, 4.4, 6.0, 4, 1.2)
    tarh("bahar_dali", 140.0, 172.0, 5.6, 6.4, 3, 1.0)

    # Tûbâ'nın dibi (r 2.6-3.6 m): rahle ve tesbih, define sandığı ve ondan çıkanlar, bohça, koza
    kutup("rahle_ve_kitap", 18.0, 3.1, 1.5)
    kutup("tesbih", 34.0, 2.9, 2.5, rot=rastgele())
    kutup("hediye_bohcasi", 330.0, 3.0, 1.8, rot=rastgele())
    kutup("define_sandigi", 200.0, 3.2, 1.6)
    kutup("inci", 188.0, 3.4, 2.2, rot=rastgele())
    kutup("mercan", 212.0, 3.6, 1.8, rot=rastgele())
    kutup("sedef", 222.0, 3.0, 2.0, rot=rastgele())
    kutup("ipek_kozasi", 262.0, 3.0, 2.0, rot=rastgele())
    # Kandiller Tûbâ'nın dört yanında; kolu dışa uzanır (modelin kolu +x yönünde)
    for aci in (70.0, 160.0, 250.0, 340.0):
        kutup("kandil", aci, 3.9, 1.3, rot=aci - 90.0)
    # Sınırda: kuzeyde iki fener (kutup yıldızı yönü), batıda gül tarhının yanında arı kovanı
    kutup("fener_ve_kutup_yildizi", 172.0, 11.2, 1.6)
    kutup("fener_ve_kutup_yildizi", 188.0, 11.2, 1.6)
    kutup("ari_kovani", 316.0, 10.6, 1.5)


# --------------------------------------------------------------------------
# Çevre: arsanın doğusunda ve kuzeyinde, iki ırmağın arasındaki çayır (ayrıca su ırmağının batısı)
# --------------------------------------------------------------------------

def _kume(y: _Yerlestirici, asset, merkez, yaricap, n, olcek, seed, bas=(0.0, 0.0), aralik=None, yuz=None):
    """Tür kümesi: merkez çevresinde n yuva (tohumlu). Yuvalar bas noktasına yakından uzağa
    sıralanır (ilk olgunlaşan en yakına)."""
    rng = np.random.default_rng(seed)
    secilen = []
    deneme = 0
    while len(secilen) < n:
        deneme += 1
        if deneme > 4000:
            raise ValueError(f"Küme doldurulamadı: {asset} {merkez} ({len(secilen)}/{n})")
        a = rng.uniform(0, 2 * math.pi)
        q = yaricap * math.sqrt(rng.uniform(0, 1))
        x, z = merkez[0] + q * math.cos(a), merkez[1] + q * math.sin(a)
        o = olcek * float(rng.uniform(0.9, 1.1))
        if aralik and any(math.hypot(x - sx, z - sz) < aralik for sx, sz, _ in secilen):
            continue
        if y.neden("cevre", asset, x, z, o) is not None:
            continue
        # Kümenin kendi içindeki aralığı da denetlensin diye geçici olarak konur
        y.konan.append(("cevre", x, z, 0.0, o, asset, -1, 0.0))
        secilen.append((x, z, o))
    del y.konan[-n:]
    secilen.sort(key=lambda p: math.hypot(p[0] - bas[0], p[1] - bas[1]))
    for x, z, o in secilen:
        y.koy("cevre", asset, x, z, o, rot=None if yuz else float(rng.uniform(0, 360)), yuz=yuz, itme=0.0)


def _cevre(y: _Yerlestirici, rng) -> None:
    arsa = (0.0, 0.0)
    # Âb-ı hayat pınarı (Hayy 18, ilk gelen yapılardan): arsanın doğusunda, hurmalığın ortasında
    pinar = (24.0, 4.0)
    y.koy("cevre", "ab_i_hayat_pinari", *pinar, 1.0, yuz=arsa, itme=6.0)
    # Köşk (İhlâs 10): arsanın kuzeyinde, arsa kamerasının kadrajında; servi yolunun sonunda
    kosk = (9.5, -63.0)
    y.koy("cevre", "kosk", *kosk, 1.0, yuz=arsa, itme=8.0)
    # Şadırvan: servi yolunun başında, arsanın kuzeydoğusunda
    y.koy("cevre", "sadirvan", 22.0, -22.0, 0.9, yuz=arsa, itme=6.0)
    # Parsel kapısı ve anahtar (Fettâh): çayırın kuzey ucunda, sonraki parsele açılır
    y.koy("cevre", "parsel_kapisi_ve_anahtar", 16.0, -108.0, 1.0, yuz=arsa, itme=10.0)
    # Sur parçaları: sut ırmağı koridorunun kıyısında, çayırın doğu duvarı (düz, köşe, düz, köşe...)
    for k in range(6):
        z = -6.0 - 5.2 * k
        y.koy("cevre", "sur_parcalari", 33.5 - 0.35 * k, z, 1.0, rot=90.0, itme=4.0)

    # Servi yolu: şadırvandan köşke uzanan iki sıra (yakından uzağa çiftler)
    a, b = np.array([20.0, -29.0]), np.array([13.0, -52.0])
    yon = (b - a) / np.linalg.norm(b - a)
    dik = np.array([-yon[1], yon[0]])
    for k in range(6):
        p = a + (b - a) * (k / 5)
        for s in (1, -1):
            q = p + dik * 3.3 * s
            y.koy("cevre", "servi", float(q[0]), float(q[1]), float(rng.uniform(0.95, 1.1)),
                  rot=float(rng.uniform(0, 360)), itme=2.0)

    # Hurmalık: pınarın çevresinde
    _kume(y, "hurma_agaci", pinar, 13.0, 9, 1.05, 101, bas=arsa)
    # Ulu çınarlar: çayırın kuzeydoğusunda, geniş aralıklı
    _kume(y, "cinar", (42.0, -94.0), 20.0, 6, 1.0, 102, bas=arsa)
    # Üzüm bağı: köşkün kuzeyinde, çardak sıraları
    for k in range(8):
        sira, j = divmod(k, 4)
        y.koy("cevre", "uzum_asmasi_ve_cardak", 8.0 + 7.5 * j, -80.0 - 8.0 * sira, 1.0, rot=0.0, itme=3.0)

    # Çiçekler: köşkün önünde lale tarhı, şadırvanın çevresinde güller, servi yolunun yanında bahar dalları
    _kume(y, "lale", (11.0, -57.8), 2.8, 14, 1.5, 103, bas=arsa, aralik=0.7)
    _kume(y, "kirmizi_gul", (26.5, -30.0), 4.0, 8, 1.2, 104, bas=arsa, aralik=1.0)
    _kume(y, "beyaz_gul", (22.0, -60.0), 4.5, 6, 1.2, 105, bas=arsa, aralik=1.0)
    _kume(y, "bahar_dali", (26.0, -46.0), 5.0, 5, 1.0, 106, bas=arsa, aralik=2.0)

    # Su ırmağının batısındaki çayır: ağaçlar için ikinci kümeler. Çayırın kuzeyi ve batısı
    # koru (yansima.cevre); kümeler korunun güney kıyısıyla ırmak koridoru arasındaki açıklıkta.
    _kume(y, "servi", (-102.0, -8.0), 7.0, 10, 1.05, 107, bas=arsa)
    _kume(y, "hurma_agaci", (-92.0, 10.0), 11.0, 8, 1.05, 108, bas=arsa)
    _kume(y, "cinar", (-86.0, -10.0), 6.0, 3, 1.0, 109, bas=arsa)
    _kume(y, "uzum_asmasi_ve_cardak", (-96.0, 34.0), 10.0, 5, 1.0, 110, bas=arsa)


def yuvalar(irmaklar, yapilar, yerde, korular=()) -> dict:
    """Dünya yuvaları (bkz. modül başı). irmaklar: cennet.Irmak listesi; yapilar: vitrin
    yapılarının (x, z, yarıçap) listesi; yerde(x, z): arazinin yüksekliği; korular: çevre
    koruları (yerlesim() "koru", [x, y, z, dönüş, ölçek, ...]), yuvalar onların tacına girmez."""
    y = _Yerlestirici(irmaklar, yapilar, yerde, korular)
    rng = np.random.default_rng(20260926)
    _arsa(y, rng)
    _cevre(y, rng)
    return y.sonuc()
