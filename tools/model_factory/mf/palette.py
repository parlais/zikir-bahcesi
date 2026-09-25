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
    "cimen": (108, 160, 78),
    "cimen_koyu": (84, 136, 66),
    "govde": (122, 84, 54),
    "govde_acik": (158, 116, 76),
    "hurma_govde": (150, 110, 72),
    "hurma_meyve": (196, 110, 40),
    "hurma_meyve_koyu": (150, 68, 30),
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
    # Büyük sahne
    "selvi": (46, 96, 58),
    "nar": (196, 40, 48),
    "nar_koyu": (140, 30, 36),
    "gul": (222, 70, 96),
    "gul_koyu": (170, 36, 64),
    "tas_yol": (222, 208, 184),
    "cini_firuze": (38, 150, 160),
    "cini_lacivert": (28, 64, 128),
    "kursun_renk": (112, 128, 142),
    "uzak_dag": (128, 132, 146),
    "uzak_orman": (70, 104, 84),
    "kar": (246, 248, 252),
    "bos": (30, 22, 18),                # kovan girişi gibi karanlık oyuklar
    # Cennet mekânı (Faz 2a)
    "yaprak_zumrut": (34, 98, 60),      # Rahmân 64: koyu yeşil (müdhâmmetân)
    "yaprak_cennet": (112, 178, 74),
    "kiraz": (206, 30, 52),             # sidr (Ali Ünal: dal bastı kirazlar)
    "kiraz_koyu": (140, 18, 40),
    "muz_yaprak": (104, 176, 76),       # talh (muz)
    "muz_yaprak_koyu": (70, 134, 60),
    "muz_govde": (128, 142, 72),
    "muz": (238, 206, 92),
    "muz_cicek": (128, 36, 72),
    "uzum": (98, 46, 112),
    "uzum_koyu": (62, 28, 80),
    "uzum_acik": (184, 204, 96),
    "altin_tugla": (234, 192, 112),     # et-Tâc: altın ve gümüş kerpiç, misk harç
    "gumus_tugla": (224, 228, 236),
    "misk": (74, 54, 40),
    "gumus": (206, 212, 222),
    "yakut": (196, 22, 64),
    "sut": (248, 244, 234),             # Muhammed 15: dört ırmak
    "bal": (220, 146, 34),
    "serbet": (196, 36, 72),
    "arsa_cimen": (118, 192, 82),       # Tirmizî 3462: düz ve boş arazi; kısa, kadife çimen
    "toprak_arsa": (82, 56, 38),        # dikim yerlerindeki yumuşak toprak
    "toprak_arsa_acik": (120, 86, 58),
    "kum": (228, 210, 174),
    "cakil": (200, 188, 168),
    "kaya_krem": (240, 222, 196),
    "kaya_pembe": (236, 190, 176),
    "kaya_altin": (238, 200, 140),
    "inci_ic": (242, 226, 206),
    "kadife_yesil": (36, 112, 76),      # Rahmân 76: yeşil yastıklar
    "yastik_yesil": (64, 150, 96),
    "hali_kirmizi": (164, 36, 50),
    "hali_lacivert": (30, 52, 112),
    "hali_krem": (238, 222, 184),
    "hali_altin": (214, 164, 72),
    "nur_beyaz": (255, 246, 222),
    # K10: tabakalar, gök perdeleri, merdiven çiçekleri
    "gok_tavan": (78, 146, 232),        # tabakanın göğü (yukarısı)
    "gok_orta": (150, 202, 246),
    "gok_ufuk": (255, 222, 158),        # tabakanın ufku (sıcak, ışıklı)
    "bulut_beyaz": (255, 252, 246),
    "cicek_mor": (130, 70, 196),
    "cicek_lila": (186, 140, 226),
    "katman_toprak": (122, 74, 42),     # kesit yüzünün katmanları (Dünya'nın katman resimleri gibi)
    "katman_altin": (232, 180, 82),
    "katman_inci": (246, 240, 228),
    "katman_koyu": (84, 52, 34),
}


def renk(ad: str):
    r, g, b = PALET[ad]
    return (r / 255.0, g / 255.0, b / 255.0)
