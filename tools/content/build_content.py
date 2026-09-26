#!/usr/bin/env python3
"""docs/asset-listesi.md -> game/data/*.json

Asset listesi tek kaynak (source of truth) olarak kalır. Bu betik tabloları
okuyup oyunun kullandığı yapılandırılmış veriye çevirir. Listeyi değiştirdikten
sonra yeniden çalıştırın:

    python3 tools/content/build_content.py

Tabloda yorum gerektiren her şey (tetikleyici metni, aşama sayısı, tarif
girdileri) aşağıdaki açık kurallar ve tablolarla çözülür. Tanınmayan bir
tetikleyici metni hata verir; sessizce tahmin edilmez.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from zikirler import CELALI_ISIMLER, ESMA_99_DISI, ESMA_ARAPCA, ZIKIRLER  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "docs" / "asset-listesi.md"
OUT = ROOT / "game" / "data"

# --------------------------------------------------------------------------
# Kurallar (asset listesi "Okuma kılavuzu" + tasarım kararları)
# --------------------------------------------------------------------------

# Aşama eşikleri: zikir sayısıyla büyüyen bitkiler (kılavuz: 1, 10, 33, 100).
AGAC_ESIKLERI = [1, 10, 33, 100]
# Çiçekler 3 aşamalıdır (tohum, gonca, açmış). Sayılar kılavuzda yok; ağacın
# ilk ve son iki eşiğiyle uyumlu seçildi.
CICEK_ESIKLERI = [1, 33, 100]
# Tûbâ ömür boyu toplam tevhid ile büyür; 5 aşama.
TUBA_ESIKLERI = [1, 33, 100, 1000, 10000]
# Sure ile büyüyen ağaçlar (Tîn, Rahmân, Vâkıa): okuma sayısı.
SURE_AGAC_ESIKLERI = [1, 3, 7, 11]
# Esma ile büyüyen bitkilerde eşikler ebcedin oranıdır: ebced tamamlanınca olgun.
AGAC_ORANLARI = [0.01, 0.10, 0.33, 1.0]
CICEK_ORANLARI = [0.01, 0.33, 1.0]
# Ebced modu kapalıyken ("serbest sayı") her esma 33'te tamamlanır.
SERBEST_ESMA_ADEDI = 33
# Aile/grup hedefi eşiği (kılavuz: ebcedi 500 ve üzeri).
GRUP_ESIGI = 500
# Sayı belirtilmemiş tetikleyicilerin varsayılan adedi (söz türüne göre).
VARSAYILAN_ADET = {"zikir": 33, "dua": 1, "gunluk": 1, "sure": 1}

ASAMA_ADLARI = {
    3: ["tohum", "gonca", "açmış"],
    4: ["tohum", "filiz", "fidan", "olgun"],
    5: ["tohum", "filiz", "fidan", "olgun", "ulu"],
}

CICEKLER = {
    "kirmizi_gul", "beyaz_gul", "lale", "tefriciye_gulu", "kardelen",
    "sus_cicekleri_seti", "guz_cigdemi", "gulistan_tarhi", "yedi_basakli_bugday",
    "bahar_dali",
}

# Tek satırı birden çok model eden assetler (asset listesi B ve D açıklamaları).
COKLU_MODEL = {
    "sus_cicekleri_seti": ["karanfil", "sumbul", "nergis", "zambak"],
    "sur_parcalari": ["duz", "kose"],
    "patika_seti": ["duz", "donemec", "kavsak"],
}
# Yeni model istemeyen varyantlar.
VARYANT = {"harem_guvercini": ("guvercin", "harem")}

# Tablodaki addan türemeyen, sözleşmeyle sabitlenmiş kimlikler (tablodaki adın
# sluggu -> asset id). Sahne dört ırmağı bu kimliklerle açar (DunyaDurumu,
# hal.irmak = [su, sut, bal, serbet]).
KIMLIK = {
    "su_irmagi": "irmak_su", "sut_irmagi": "irmak_sut",
    "bal_irmagi": "irmak_bal", "serbet_irmagi": "irmak_serbet",
}
# Dünya modelinin parçası olan assetler: ayrı .glb dosyaları yoktur. Irmak
# yatağı ve suyu dünya modelindedir; sahne onları oyuncunun durumundan açar.
DUNYA_PARCASI = {
    "irmak_su": "ZB_dunya_cennet", "irmak_sut": "ZB_dunya_cennet",
    "irmak_bal": "ZB_dunya_cennet", "irmak_serbet": "ZB_dunya_cennet",
}

# Dosya adındaki kısa isim (ZB_[kategori]_[isim]). Verilmezse id'den türetilir.
KISA_AD = {
    "tuba": "tuba", "uzum_asmasi_ve_cardak": "uzum", "toros_sediri": "sedir",
    "kitmir": "kitmir", "kumru_cifti": "kumru", "leylek_ve_yuvasi": "leylek",
    "koyun_ve_kuzu": "koyun", "mashaallah_kitabesi": "masaallah_kitabesi",
    "fener_ve_kutup_yildizi": "fener", "rahle_ve_kitap": "rahle",
    "altin_tepsi_ve_ikram": "altin_tepsi", "reyhan_ve_lavanta_saksilari": "reyhan_saksi",
    "sifali_otlar_tarhi": "sifali_otlar", "hazir_fidan_cukuru": "fidan_cukuru",
    "nadir_tur_tohumu_kesesi": "tohum_kesesi", "sedef_kakma_saklama_kutusu": "sedef_kutu",
    "mimar_takimi": "mimar_takimi", "divit_ve_kamis_kalem": "divit",
    "bahce_maketi_masasi": "maket_masasi", "aski_ve_onarim_sandigi": "onarim_sandigi",
    "asi_ve_onarim_sandigi": "onarim_sandigi", "tas_firin_ve_ekmek": "tas_firin",
    "lale_motifli_cini_nis": "cini_nis", "kehf_kosesi": "kehf_kosesi",
    "dort_irmak_merkez_havuzu": "dort_irmak_havuzu", "revak": "revak",
}

# Tarif girdileri (asset listesi G bölümü). Metinden otomatik çıkarmak
# yerine açıkça yazıldı; her girdi bir asset id'sine bağlanır.
TARIF_GIRDILERI = {
    "zeytinyagi_testisi": [dict(asset="zeytin_agaci", asama=4, adet=1, eylem="hasat")],
    "inci_kosk": [dict(asset="inci", adet=33), dict(asset="kosk", adet=1)],
    "gul_bali_kavanozu": [dict(asset="kirmizi_gul", asama=3, adet=100), dict(asset="ari_kovani", adet=1)],
    "gulabdan": [dict(asset="kirmizi_gul", asama=3, adet=100), dict(asset="sadirvan", adet=1)],
    "un_cuvali": [dict(asset="yedi_basakli_bugday", asama=3, adet=1), dict(asset="su_degirmeni", adet=1)],
    "tas_firin_ve_ekmek": [dict(asset="un_cuvali", adet=3)],
    "lale_motifli_cini_nis": [dict(asset="cini_pano", adet=1), dict(asset="lale", asama=3, adet=1)],
    "kehf_kosesi": [dict(asset="magara", adet=1), dict(asset="kitmir", adet=1)],
    "ikram_sofrasi": [dict(asset="tas_firin_ve_ekmek", adet=1), dict(asset="altin_tepsi_ve_ikram", adet=1),
                      dict(asset="meyve_sepeti", adet=1)],
    "pekmez_kupu": [dict(asset="uzum_asmasi_ve_cardak", asama=4, adet=1), dict(asset="parlak_gunesli_gun", adet=1)],
    "ipek_kilim": [dict(asset="ipek_kozasi", adet=10), dict(asset="ebru_teknesi", adet=1)],
    "dort_irmak_merkez_havuzu": [dict(asset="carbag_kanallari", adet=1), dict(asset="bahce_deresi", adet=1)],
    "revak": [dict(asset="temel_tasi", adet=1), dict(asset="kilit_tasli_kemer", adet=1)],
}
# Yeni model istemeyen iki tarif (G bölümü açıklaması).
ETKI_TARIFLERI = [
    dict(id="inci_yagmuru", girdiler=[dict(asset="nisan_yagmuru", adet=1), dict(asset="sedef", adet=1)],
         urun=dict(asset="inci", adet=1), aciklama="Nisan yağmuru ile sedef inciyi verir."),
    dict(id="kandil_tam_parlaklik", girdiler=[dict(asset="zeytinyagi_testisi", adet=1), dict(asset="kandil", adet=1)],
         urun=dict(etki="kandil_tam_parlaklik"), aciklama="Zeytinyağı testisi ile kandil tam parlaklığa ulaşır."),
]

# Zikir/dua/sure tetikleyicileri: tablodaki metin -> yapı.
# Anahtar, parantez ve çarpan temizlendikten sonraki metnin sluggudur.
SOZ_ESLEME = {
    "la_ilahe_illallah": "tevhid", "toplam_la_ilahe_illallah_sayisiyla_buyur": "tevhid",
    "estagfirullah": "istigfar", "salavat": "salavat", "cuma_gunu_salavat": "salavat",
    "seyyidul_istigfar": "seyyidul_istigfar", "ayetul_kursi": "ayetel_kursi",
    "felak_suresi": "felak", "subhanallahil_azim_ve_bihamdihi": "subhanallahil_azim",
    "allahu_ekber": "allahu_ekber", "elhamdulillah": "elhamdulillah", "tin_suresi": "tin",
    "salat_i_tefriciye": "salat_tefriciye", "hasbunallahu_ve_nimel_vekil": "hasbunallah",
    "insallah": "insallah", "rahman_suresi": "rahman_suresi", "vakia_suresi": "vakia",
    "subhanallah": "subhanallah", "yunus_duasi": "yunus_duasi", "bismillah": "bismillah",
    "masaallah_la_kuvvete_illa_billah": "masaallah", "ihlas": "ihlas",
    "tehlil_i_kebir": "tehlil_kebir", "fatiha": "fatiha", "kevser_suresi": "kevser",
    "subhanallahi_ve_bihamdihi": "subhanallahi_ve_bihamdihi", "selamun_aleykum": "selam",
    "kuran_okuma": "kuran_okuma", "rabbena_atina": "rabbena_atina",
    "la_havle_ve_la_kuvvete_illa_billah": "lahavle", "rabbi_zidni_ilma": "rabbi_zidni_ilma",
    "33luk_tesbihat_tamamlaninca": "tesbihat", "cezakallahu_hayran": "cezakallah",
}

KOSUL_ESLEME = {
    "her oturum açılışı": "oturum_acilisi",
    "arkadaş bahçesine girerken": "arkadas_bahcesi",
    "hediye alınca": "hediye_alinca",
}


# --------------------------------------------------------------------------
# Yardımcılar
# --------------------------------------------------------------------------

_TR = str.maketrans({
    "ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u", "â": "a", "î": "i", "û": "u",
    "Ç": "c", "Ğ": "g", "I": "i", "İ": "i", "Ö": "o", "Ş": "s", "Ü": "u", "Â": "a", "Î": "i", "Û": "u",
})


def slug(text: str) -> str:
    s = text.translate(_TR).lower()
    s = s.replace("'", "").replace("’", "")
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def asset_id(name: str) -> str:
    base = slug(re.split(r"[(:,]", name, maxsplit=1)[0])
    return KIMLIK.get(base, base)


def parse_tables(md: str) -> dict[str, list[list[str]]]:
    """Bölüm harfi -> tablo satırları (başlık hariç)."""
    tables: dict[str, list[list[str]]] = {}
    section = None
    for line in md.splitlines():
        m = re.match(r"^## ([A-I])\. ", line)
        if m:
            section = m.group(1)
            continue
        if section and line.startswith("| ") and not line.startswith("| ---"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells[0] in ("Asset", "#", "Tarif", "Sürüm", "Tip kodu"):
                continue
            tables.setdefault(section, []).append(cells)
    return tables


# Kodsuz yazılmış dayanaklar: hangi koda girdiği açıkça belirtilir.
DAYANAK_KODSUZ = {"Gazâlî: tenzih ve haşyet": "G"}


def parse_dayanak(text: str) -> dict:
    if text in DAYANAK_KODSUZ:
        return {"kod": DAYANAK_KODSUZ[text], "metin": text, "ham": text}
    m = re.match(r"^([NGA])(?:[:;]\s*(.*))?$", text)
    if not m:
        raise ValueError(f"Dayanak kodu okunamadı: {text!r}")
    return {"kod": m.group(1), "metin": (m.group(2) or "").strip(), "ham": text}


def oransal_esikler(toplam: int, oranlar: list[float]) -> list[int]:
    out: list[int] = []
    for p in oranlar:
        v = max(1, math.ceil(toplam * p - 1e-9))
        if out and v <= out[-1]:
            v = out[-1] + 1
        out.append(v)
    out[-1] = max(out[-1], toplam)
    return out


# --------------------------------------------------------------------------
# Tetikleyici çözümleme
# --------------------------------------------------------------------------

def parse_trigger(text: str, esma_by_slug: dict) -> dict:
    """Tablodaki tetikleyici metnini yapıya çevirir. Kurallar (kural alanı):
      birikimli  sayaç her eşiğe ulaştığında yeniden verilir ("Estağfirullah ×100")
      toplam     ömür boyu toplam; bir kez verilir, tekrarlanmaz. Tûbâ aşamalarla
                 büyür ("Toplam La ilahe illallah sayısıyla büyür"); ırmaklar tek
                 eşiklidir ("Estağfirullah toplamı 100 (bir kez)")
      her_n      her N sözde bir item (rastgele tür olabilir)
      ardisik    N kez art arda söylenince
      surekli    sürekli kaynak (envantere girmez)
    """
    t = {"ham": text, "tur": None, "kaynak": None, "adet": None, "grup": False,
         "kural": "birikimli", "kosul": None, "not": None}

    # "Ya Nûr (256)", "Ya Hafîz (998, aile hedefi)", "Ya Selâm (131), ikinci item", "Allah (66)"
    m = re.match(r"^(?:Ya )?(.+?) \((\d+)(?:, ([^)]+))?\)(?:, (.+))?$", text)
    if m and (text.startswith("Ya ") or text.startswith("Allah (")):
        ad, sayi, ek, sonra = m.groups()
        key = slug(ad)
        if key not in esma_by_slug:
            raise ValueError(f"Esma bulunamadı: {ad!r} ({text!r})")
        t.update(tur="esma", kaynak=key, adet=int(sayi))
        if esma_by_slug[key]["ebced"] != int(sayi):
            raise ValueError(f"Ebced uyuşmuyor: {text!r} vs {esma_by_slug[key]['ebced']}")
        if ek and ek.strip() in ("grup", "aile hedefi"):
            t["grup"] = True
        elif ek:
            t["not"] = ek.strip()
        if sonra:
            t["not"] = sonra.strip()
        t["grup"] = t["grup"] or int(sayi) >= GRUP_ESIGI
        return t

    if text == "İsmin ebcedi kadar çekilince kart açılır":
        t.update(tur="esma_kart", kaynak=CELALI_ISIMLER)
        return t
    if text == "Su yapılarıyla birlikte gelir":
        t.update(tur="yapi_ile", kural=None)
        return t
    if text.startswith("Define sandığından"):
        t.update(tur="item", kaynak="define_sandigi", kural=None)
        if "tarif" in text:
            t["not"] = "ayrıca inci_yagmuru tarifi"
        return t
    if text == "Latîf kozasından çıkar":
        t.update(tur="item", kaynak="ipek_kozasi", kural=None)
        return t
    if text == "Duhâ, Kamer, Necm sureleri":
        t.update(tur="sure", kaynak=["duha", "kamer", "necm"])
        return t

    # Genel zikir/sure: "X ×100", "X (koşul)", "X, 10 üst üste"
    body = text
    m = re.search(r" ×(\d+)$", body)
    if m:
        t["adet"] = int(m.group(1))
        body = body[: m.start()]
    m = re.search(r" \(([^)]+)\)$", body)
    if m:
        ic = m.group(1)
        body = body[: m.start()]
        m2 = re.match(r"^(\d+)(?:, (grup))?$", ic)
        if m2:
            t["adet"] = int(m2.group(1))
            t["grup"] = bool(m2.group(2))
        elif ic == "grup":
            t["grup"] = True
        elif ic == "sürekli":
            t["kural"] = "surekli"
        elif ic.startswith("her 33"):
            t.update(kural="her_n", adet=33)
            t["not"] = ic
        elif ic == "rastgele tür":
            t.update(kural="her_n", adet=33)
            t["not"] = ic
        elif ic == "ayet başına bir basamak":
            t.update(kural="her_n", adet=1)
        elif ic == "bir kez":
            t["kural"] = "toplam"
        elif ic in KOSUL_ESLEME:
            t["kosul"] = KOSUL_ESLEME[ic]
        else:
            raise ValueError(f"Parantez içi okunamadı: {text!r}")
    m = re.search(r" (\d+)$", body)  # "Salât-ı Tefriciye 4444"
    if m:
        t["adet"] = int(m.group(1))
        body = body[: m.start()]
    m = re.search(r", (\d+) üst üste$", body)
    if m:
        t.update(adet=int(m.group(1)), kural="ardisik")
        body = body[: m.start()]
    key = slug(body)
    if key.startswith("toplam_"):
        t["kural"] = "toplam"
    # "Estağfirullah toplamı 100 (bir kez)": ömür boyu toplam, tekrarsız.
    toplamli = key.endswith("_toplami")
    if toplamli:
        key = key[: -len("_toplami")]
        t["kural"] = "toplam"
    if toplamli != text.endswith(" (bir kez)"):
        raise ValueError(f"'toplamı N' ile '(bir kez)' birlikte yazılmalı: {text!r}")
    if key == "cuma_gunu_salavat":
        t["kosul"] = "cuma"
    if key not in SOZ_ESLEME:
        raise ValueError(f"Tetikleyici tanınmadı: {text!r} (anahtar {key!r})")
    kaynak = SOZ_ESLEME[key]
    t["tur"] = "sure" if ZIKIRLER[kaynak]["tur"] == "sure" else "zikir"
    t["kaynak"] = kaynak
    return t


# --------------------------------------------------------------------------
# Derleme
# --------------------------------------------------------------------------

BOLUM = {
    "A": "atmosfer", "B": "bitki", "C": "canli", "D": "yapi", "E": "obje", "G": "tarif",
}


def asama_sayisi(aid: str, bolum: str, tip: str) -> int:
    if tip != "3D-A":
        return 1
    if aid == "tuba":
        return 5
    return 3 if aid in CICEKLER else 4


def model_kategori(aid: str, bolum: str, tip: str) -> str | None:
    if aid in DUNYA_PARCASI:
        return None
    if tip in ("VFX", "Sky"):
        return None
    if tip == "UI":
        return None
    if bolum == "B":
        if tip == "3D-A":
            return "cicek" if aid in CICEKLER else "agac"
        return "bitki"
    return {"C": "canli", "D": "yapi", "E": "obje", "G": "tarif"}[bolum]


def kisa_ad(aid: str, kategori: str | None) -> str:
    if aid in KISA_AD:
        return KISA_AD[aid]
    s = aid
    for suf in ("_agaci",):
        if s.endswith(suf):
            s = s[: -len(suf)]
    return s


def esikler_hesapla(asset: dict, serbest: bool) -> list[int]:
    t = asset["tetikleyici"]
    n = asset["asama_sayisi"]
    cicek = n == 3
    if t["tur"] == "esma" or (t["adet"] and t["adet"] > 1 and n > 1):
        hedef = t["adet"]
        if serbest and t["tur"] == "esma":
            hedef = SERBEST_ESMA_ADEDI
        if n == 1:
            return [hedef]
        return oransal_esikler(hedef, CICEK_ORANLARI if cicek else AGAC_ORANLARI)
    if n == 1:
        if t["adet"]:
            return [t["adet"]]
        # Olaya bağlı sözler (oturum açılışı, selam, teşekkür) bir kez söylenir;
        # bileşik zikir (33'lük tesbihat) bir kez tamamlanır.
        if t["kosul"] or (isinstance(t["kaynak"], str) and ZIKIRLER.get(t["kaynak"], {}).get("bilesik")):
            return [1]
        if t["tur"] in ("zikir", "sure") and t["kural"] == "birikimli":
            return [VARSAYILAN_ADET[ZIKIRLER[t["kaynak"] if isinstance(t["kaynak"], str) else t["kaynak"][0]]["tur"]]]
        return [1]
    if asset["id"] == "tuba":
        return list(TUBA_ESIKLERI)
    if t["tur"] == "sure":
        return list(SURE_AGAC_ESIKLERI)
    return list(CICEK_ESIKLERI if cicek else AGAC_ESIKLERI)


def main() -> None:
    md = SRC.read_text(encoding="utf-8")
    tables = parse_tables(md)

    # --- Esma -------------------------------------------------------------
    esma: list[dict] = []
    for no, ad, ebced, karsiligi, oncelik in tables["F"]:
        key = slug(ad)
        if key not in ESMA_ARAPCA:
            raise ValueError(f"Arapça yazım eksik: {ad} ({key})")
        esma.append(dict(id=key, no=int(no), ad=ad, arapca=ESMA_ARAPCA[key], ebced=int(ebced),
                         grup=int(ebced) >= GRUP_ESIGI, karsiligi=karsiligi, oncelik=oncelik,
                         celali=key in CELALI_ISIMLER, doksan_dokuz=True))
    for key, d in ESMA_99_DISI.items():
        esma.append(dict(id=key, no=None, ad=d["ad"], arapca=ESMA_ARAPCA[key], ebced=d["ebced"],
                         grup=d["ebced"] >= GRUP_ESIGI, karsiligi=d["karsiligi"], oncelik=None,
                         celali=False, doksan_dokuz=False))
    esma_by_slug = {e["id"]: e for e in esma}

    # --- Assetler ---------------------------------------------------------
    assets: list[dict] = []
    for bolum in "ABCDE":
        for ad, tetik, dayanak, tip, oncelik in tables[bolum]:
            aid = asset_id(ad)
            a = dict(id=aid, ad=ad, bolum=bolum, kategori=BOLUM[bolum], tip=tip, oncelik=oncelik,
                     dayanak=parse_dayanak(dayanak), tetikleyici=parse_trigger(tetik, esma_by_slug))
            assets.append(a)
    for tarif_ad, urun, dayanak, oncelik in tables["G"]:
        aid = asset_id(urun)
        if aid not in TARIF_GIRDILERI:
            raise ValueError(f"Tarif girdisi tanımsız: {urun} ({aid})")
        a = dict(id=aid, ad=urun, bolum="G", kategori="tarif", tip="3D", oncelik=oncelik,
                 dayanak=parse_dayanak(dayanak),
                 tetikleyici={"ham": tarif_ad, "tur": "tarif", "kaynak": aid, "adet": None,
                              "grup": False, "kural": None, "kosul": None, "not": None})
        assets.append(a)

    ids = [a["id"] for a in assets]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise ValueError(f"Çift asset id: {dup}")

    for a in assets:
        n = asama_sayisi(a["id"], a["bolum"], a["tip"])
        a["asama_sayisi"] = n
        a["asama_adlari"] = ASAMA_ADLARI.get(n, [])
        kat = model_kategori(a["id"], a["bolum"], a["tip"])
        files: list[str] = []
        if kat:
            if a["id"] in VARYANT:
                base, var = VARYANT[a["id"]]
                a["varyant_of"] = dict(model=f"ZB_{kat}_{base}", renk=var)
            else:
                parcalar = COKLU_MODEL.get(a["id"], [kisa_ad(a["id"], kat)])
                prefix = "" if a["id"] not in COKLU_MODEL else kisa_ad(a["id"], kat) + "_"
                if a["id"] == "sus_cicekleri_seti":
                    prefix = ""
                for p in parcalar:
                    stem = f"ZB_{kat}_{prefix}{p}"
                    if n > 1:
                        files += [f"{stem}_a{i}" for i in range(1, n + 1)]
                    else:
                        files.append(stem)
        a["modeller"] = files
        if a["id"] in DUNYA_PARCASI:
            a["dunya_parcasi"] = DUNYA_PARCASI[a["id"]]
        a["esikler"] = esikler_hesapla(a, serbest=False)
        a["esikler_serbest"] = esikler_hesapla(a, serbest=True)
        a["grup"] = bool(a["tetikleyici"]["grup"]) or (
            a["tetikleyici"]["tur"] == "esma" and esma_by_slug[a["tetikleyici"]["kaynak"]]["grup"])

    # --- Tarifler ---------------------------------------------------------
    by_id = {a["id"]: a for a in assets}
    tarifler = []
    for tarif_ad, urun, dayanak, oncelik in tables["G"]:
        aid = asset_id(urun)
        girdiler = TARIF_GIRDILERI[aid]
        for g in girdiler:
            if g["asset"] not in by_id:
                raise ValueError(f"Tarif girdisi asset değil: {g['asset']} ({urun})")
        tarifler.append(dict(id=aid, ad=tarif_ad, girdiler=girdiler, urun=dict(asset=aid, adet=1),
                             dayanak=parse_dayanak(dayanak), oncelik=oncelik, yeni_model=True))
    for t in ETKI_TARIFLERI:
        for g in t["girdiler"]:
            if g["asset"] not in by_id:
                raise ValueError(f"Etki tarifi girdisi asset değil: {g['asset']}")
        tarifler.append(dict(t, ad=t["aciklama"], dayanak=None, oncelik="v2", yeni_model=False))

    # --- Doğrulama --------------------------------------------------------
    for a in assets:
        t = a["tetikleyici"]
        if t["tur"] == "item" and t["kaynak"] not in by_id:
            raise ValueError(f"Item kaynağı yok: {t['kaynak']} ({a['id']})")
        e = a["esikler"]
        if len(e) != max(1, a["asama_sayisi"]) or e != sorted(set(e)):
            raise ValueError(f"Eşikler hatalı: {a['id']} {e}")
        if t["kural"] == "toplam" and a["asama_sayisi"] == 1 and not t["adet"]:
            raise ValueError(f"Tek eşikli 'toplam' kuralının adedi yok: {a['id']}")
    for aid in DUNYA_PARCASI:
        if aid not in by_id:
            raise ValueError(f"Dünya parçası listede yok: {aid}")

    ozet = {}
    for s in ("MVP", "v2", "v3"):
        sec = [a for a in assets if a["oncelik"] == s]
        ozet[s] = dict(asset=len(sec), model=sum(len(a["modeller"]) for a in sec))
    ozet["toplam"] = dict(asset=len(assets), model=sum(len(a["modeller"]) for a in assets))

    zikirler = [dict(id=k, varsayilan_adet=VARSAYILAN_ADET[v["tur"]], **{kk: vv for kk, vv in v.items()})
                for k, v in ZIKIRLER.items()]
    for z in zikirler:
        z.setdefault("onek_of", [])
        z.setdefault("sonek_of", [])
    # "La havle ve la kuvvete illa billah" ile "Mâşâallah, lâ kuvvete illâ billâh" aynı sözlerle biter.
    zmap = {z["id"]: z for z in zikirler}
    zmap["lahavle"]["sonek_ortak"] = ["masaallah"]
    zmap["masaallah"]["sonek_ortak"] = ["lahavle"]

    meta = dict(
        kaynak="docs/asset-listesi.md", uretici="tools/content/build_content.py",
        kurallar=dict(agac_esikleri=AGAC_ESIKLERI, cicek_esikleri=CICEK_ESIKLERI,
                      tuba_esikleri=TUBA_ESIKLERI, sure_agac_esikleri=SURE_AGAC_ESIKLERI,
                      agac_oranlari=AGAC_ORANLARI, cicek_oranlari=CICEK_ORANLARI,
                      serbest_esma_adedi=SERBEST_ESMA_ADEDI, grup_esigi=GRUP_ESIGI,
                      varsayilan_adet=VARSAYILAN_ADET),
        ozet=ozet,
    )

    OUT.mkdir(parents=True, exist_ok=True)
    def dump(name, obj):
        (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    dump("assets.json", dict(meta=meta, assets=assets))
    dump("esma.json", dict(esma=esma))
    dump("zikirler.json", dict(zikirler=zikirler))
    dump("tarifler.json", dict(tarifler=tarifler))

    print(f"{len(assets)} asset, {len(esma)} esma, {len(zikirler)} söz, {len(tarifler)} tarif yazıldı.")
    for k, v in ozet.items():
        print(f"  {k:6s} asset={v['asset']:3d} model={v['model']:3d}")


if __name__ == "__main__":
    main()
