"""Zikir Bahçesi paleti.

Renkler Osmanlı çini (İznik mavisi, mercan kırmızısı, firuze), bahçe
yeşilleri ve taş/ahşap tonlarından seçildi. Bütün modeller yalnızca bu
isimleri kullanır; stil değişikliği tek yerden yapılır.
Değerler sRGB'dir (0-255).
"""

PALET = {
    # Bitki
    "yaprak": (96, 158, 72),
    "yaprak_koyu": (58, 118, 62),
    "yaprak_acik": (150, 196, 92),
    "hurma_yaprak": (84, 146, 78),
    "cimen": (122, 178, 84),
    "cimen_koyu": (92, 150, 70),
    "govde": (122, 84, 54),
    "govde_acik": (158, 116, 76),
    "hurma_govde": (150, 110, 72),
    "hurma_meyve": (196, 110, 40),
    "lale": (204, 56, 52),
    "lale_koyu": (160, 36, 44),
    "lale_sari": (238, 190, 70),
    "tohum": (120, 82, 50),
    # Toprak ve taş
    "toprak": (138, 100, 66),
    "toprak_koyu": (104, 74, 50),
    "tas": (214, 204, 184),
    "tas_koyu": (164, 152, 132),
    "kaya": (148, 140, 128),
    "mermer": (236, 230, 218),
    # Mimari
    "fildisi": (242, 232, 212),
    "kursun": (112, 128, 142),          # Osmanlı kurşun kubbe
    "firuze": (44, 164, 160),
    "iznik": (30, 78, 140),
    "mercan_kirmizi": (200, 68, 58),
    "ahsap": (132, 88, 52),
    "ahsap_koyu": (92, 60, 38),
    "demir": (70, 72, 78),
    "altin": (217, 164, 65),
    # Obje
    "inci": (246, 242, 236),
    "sedef": (226, 214, 222),
    "sedef_dis": (150, 140, 128),
    "mercan": (232, 96, 80),
    "kumas_kirmizi": (178, 44, 52),
    "kumas_yesil": (40, 110, 90),
    "ipek": (246, 238, 210),
    "kehribar": (208, 138, 46),
    "saman": (214, 176, 96),
    "saman_koyu": (170, 132, 66),
    "kitap_sayfa": (246, 238, 214),
    "kitap_cilt": (130, 40, 42),
    "cam": (255, 226, 150),             # kandil camı (nur malzemesiyle parlar)
    "nur": (255, 214, 120),
    "su": (96, 176, 214),
    "bos": (30, 22, 18),                # kovan girişi gibi karanlık oyuklar
}


def renk(ad: str):
    r, g, b = PALET[ad]
    return (r / 255.0, g / 255.0, b / 255.0)
