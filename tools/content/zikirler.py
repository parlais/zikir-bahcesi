"""Zikir, dua ve sure kataloğu.

Asset listesindeki tetikleyicilerin işaret ettiği sözlerin tek kaynağı burasıdır.
Arapça metinler harekesiz yazıldı; üretime geçmeden önce danışma kurulunca
teyit edilecektir (asset listesi, I bölümü).

Alanlar:
  ad        Ekranda görünen Türkçe okunuş
  arapca    Harekesiz Arapça metin (sure ve uzun dualarda None)
  anlam     Çocuk diliyle kısa anlam
  tur       zikir | dua | sure | gunluk (günlük dildeki söz)
  onek_of   Bu sözle BAŞLAYAN daha uzun sözler. Ses tanımada, bu söz
            duyulduğunda ödül, uzun sözün bitip bitmediği anlaşılana kadar
            bekletilir (asset listesi, H bölümü: iç içe geçen ifadeler).
  sonek_of  Bu sözle BİTEN daha uzun sözler (aynı amaçla).
"""

ZIKIRLER = {
    "bismillah": dict(
        ad="Bismillâhirrahmânirrahîm", arapca="بسم الله الرحمن الرحيم",
        anlam="Rahmân ve Rahîm olan Allah'ın adıyla.", tur="zikir"),
    "tevhid": dict(
        ad="Lâ ilâhe illallâh", arapca="لا إله إلا الله",
        anlam="Allah'tan başka ilah yoktur.", tur="zikir",
        onek_of=["tehlil_kebir"]),
    "tehlil_kebir": dict(
        ad="Lâ ilâhe illallâhu vahdehû lâ şerîke leh, lehü'l-mülkü ve lehü'l-hamdü ve hüve alâ külli şey'in kadîr",
        arapca="لا إله إلا الله وحده لا شريك له له الملك وله الحمد وهو على كل شيء قدير",
        anlam="Allah'tan başka ilah yoktur; O tektir, ortağı yoktur. Mülk ve hamd O'nundur, O her şeye gücü yetendir.",
        tur="zikir"),
    "subhanallah": dict(
        ad="Sübhânallâh", arapca="سبحان الله",
        anlam="Allah her türlü eksiklikten uzaktır.", tur="zikir",
        onek_of=["subhanallahi_ve_bihamdihi", "subhanallahil_azim"]),
    "subhanallahi_ve_bihamdihi": dict(
        ad="Sübhânallâhi ve bihamdihî", arapca="سبحان الله وبحمده",
        anlam="Allah'ı hamd ile tesbih ederim.", tur="zikir"),
    "subhanallahil_azim": dict(
        ad="Sübhânallâhi'l-azîm ve bihamdihî", arapca="سبحان الله العظيم وبحمده",
        anlam="Yüce Allah'ı hamd ile tesbih ederim.", tur="zikir"),
    "elhamdulillah": dict(
        ad="Elhamdülillâh", arapca="الحمد لله",
        anlam="Hamd Allah'adır.", tur="zikir"),
    "allahu_ekber": dict(
        ad="Allâhu ekber", arapca="الله أكبر",
        anlam="Allah en büyüktür.", tur="zikir"),
    "lahavle": dict(
        ad="Lâ havle ve lâ kuvvete illâ billâh", arapca="لا حول ولا قوة إلا بالله",
        anlam="Güç ve kuvvet yalnız Allah'tandır.", tur="zikir"),
    "masaallah": dict(
        ad="Mâşâallah, lâ kuvvete illâ billâh", arapca="ما شاء الله لا قوة إلا بالله",
        anlam="Allah dilemiş; kuvvet yalnız Allah'tandır.", tur="zikir"),
    "istigfar": dict(
        ad="Estağfirullâh", arapca="أستغفر الله",
        anlam="Allah'tan bağışlanma dilerim.", tur="zikir"),
    "seyyidul_istigfar": dict(
        ad="Seyyidü'l-istiğfâr",
        arapca=("اللهم أنت ربي لا إله إلا أنت خلقتني وأنا عبدك وأنا على عهدك ووعدك ما استطعت "
                "أعوذ بك من شر ما صنعت أبوء لك بنعمتك علي وأبوء بذنبي فاغفر لي فإنه لا يغفر الذنوب إلا أنت"),
        anlam="İstiğfarların efendisi olan bağışlanma duası.", tur="dua"),
    "salavat": dict(
        ad="Allâhümme salli alâ Muhammed", arapca="اللهم صل على محمد",
        anlam="Allah'ım, Hz. Muhammed'e salât eyle.", tur="zikir"),
    "salat_tefriciye": dict(
        ad="Salât-ı Tefriciye", arapca=None,
        anlam="Toplu okunan bir salavat.", tur="dua"),
    "hasbunallah": dict(
        ad="Hasbünallâhu ve ni'mel vekîl", arapca="حسبنا الله ونعم الوكيل",
        anlam="Allah bize yeter, O ne güzel vekildir.", tur="zikir"),
    "yunus_duasi": dict(
        ad="Lâ ilâhe illâ ente sübhâneke innî küntü mine'z-zâlimîn",
        arapca="لا إله إلا أنت سبحانك إني كنت من الظالمين",
        anlam="Senden başka ilah yoktur; sen eksiklikten uzaksın, ben kendime yazık edenlerden oldum.",
        tur="dua"),
    "rabbi_zidni_ilma": dict(
        ad="Rabbi zidnî ilmâ", arapca="رب زدني علما",
        anlam="Rabbim, ilmimi artır.", tur="dua"),
    "rabbena_atina": dict(
        ad="Rabbenâ âtinâ", arapca="ربنا آتنا في الدنيا حسنة وفي الآخرة حسنة وقنا عذاب النار",
        anlam="Rabbimiz, bize dünyada da ahirette de güzellik ver.", tur="dua"),
    "insallah": dict(
        ad="İnşâallah", arapca="إن شاء الله",
        anlam="Allah dilerse.", tur="gunluk"),
    "selam": dict(
        ad="Selâmün aleyküm", arapca="السلام عليكم",
        anlam="Selam üzerinize olsun.", tur="gunluk"),
    "cezakallah": dict(
        ad="Cezâkallâhu hayran", arapca="جزاك الله خيرا",
        anlam="Allah seni hayırla mükâfatlandırsın.", tur="gunluk"),
    "tesbihat": dict(
        ad="33'lük tesbihat", arapca=None,
        anlam="33 Sübhânallâh, 33 Elhamdülillâh, 33 Allâhu ekber.", tur="zikir",
        bilesik=[["subhanallah", 33], ["elhamdulillah", 33], ["allahu_ekber", 33]]),
    # Sureler: metin mushaftan gelir, burada yalnızca sure numarası tutulur.
    "fatiha": dict(ad="Fâtiha suresi", arapca=None, anlam="Kur'an'ın açılış suresi.", tur="sure", sure_no=1),
    "ayetel_kursi": dict(ad="Âyetü'l-Kürsî", arapca=None, anlam="Bakara suresi 255. ayet.", tur="sure", sure_no=2, ayet=255),
    "ihlas": dict(ad="İhlâs suresi", arapca=None, anlam="Allah'ın birliğini anlatan sure.", tur="sure", sure_no=112),
    "felak": dict(ad="Felak suresi", arapca=None, anlam="Sabahın Rabbine sığınma.", tur="sure", sure_no=113),
    "tin": dict(ad="Tîn suresi", arapca=None, anlam="İncire ve zeytine yemin ile başlar.", tur="sure", sure_no=95),
    "kevser": dict(ad="Kevser suresi", arapca=None, anlam="Kur'an'ın en kısa suresi.", tur="sure", sure_no=108),
    "rahman_suresi": dict(ad="Rahmân suresi", arapca=None, anlam="Nimetleri sayan sure.", tur="sure", sure_no=55),
    "vakia": dict(ad="Vâkıa suresi", arapca=None, anlam="Kıyameti ve bahçeleri anlatan sure.", tur="sure", sure_no=56),
    "duha": dict(ad="Duhâ suresi", arapca=None, anlam="Kuşluk vaktine yemin.", tur="sure", sure_no=93),
    "kamer": dict(ad="Kamer suresi", arapca=None, anlam="Ay suresi.", tur="sure", sure_no=54),
    "necm": dict(ad="Necm suresi", arapca=None, anlam="Yıldız suresi.", tur="sure", sure_no=53),
    "kuran_okuma": dict(ad="Kur'an okuma", arapca=None, anlam="Her ayet bir basamak.", tur="sure"),
}

# 99 esma: asset listesi F bölümündeki sıra ve ebced değerleri korunur.
# Arapça yazımlar takısız ve harekesizdir.
ESMA_ARAPCA = {
    "allah": "الله", "rahman": "رحمن", "rahim": "رحيم", "melik": "ملك", "kuddus": "قدوس",
    "selam": "سلام", "mumin": "مؤمن", "muheymin": "مهيمن", "aziz": "عزيز", "cebbar": "جبار",
    "mutekebbir": "متكبر", "halik": "خالق", "bari": "بارئ", "musavvir": "مصور", "gaffar": "غفار",
    "kahhar": "قهار", "vehhab": "وهاب", "rezzak": "رزاق", "fettah": "فتاح", "alim": "عليم",
    "kabid": "قابض", "basit": "باسط", "hafid": "خافض", "rafi": "رافع", "muizz": "معز",
    "muzill": "مذل", "semi": "سميع", "basir": "بصير", "hakem": "حكم", "adl": "عدل",
    "latif": "لطيف", "habir": "خبير", "halim": "حليم", "azim": "عظيم", "gafur": "غفور",
    "sekur": "شكور", "aliyy": "علي", "kebir": "كبير", "hafiz": "حفيظ", "mukit": "مقيت",
    "hasib": "حسيب", "celil": "جليل", "kerim": "كريم", "rakib": "رقيب", "mucib": "مجيب",
    "vasi": "واسع", "hakim": "حكيم", "vedud": "ودود", "mecid": "مجيد", "bais": "باعث",
    "sehid": "شهيد", "hakk": "حق", "vekil": "وكيل", "kaviyy": "قوي", "metin": "متين",
    "veliyy": "ولي", "hamid": "حميد", "muhsi": "محصي", "mubdi": "مبدئ", "muid": "معيد",
    "muhyi": "محيي", "mumit": "مميت", "hayy": "حي", "kayyum": "قيوم", "vacid": "واجد",
    "macid": "ماجد", "vahid": "واحد", "samed": "صمد", "kadir": "قادر", "muktedir": "مقتدر",
    "mukaddim": "مقدم", "muahhir": "مؤخر", "evvel": "أول", "ahir": "آخر", "zahir": "ظاهر",
    "batin": "باطن", "vali": "والي", "muteali": "متعالي", "berr": "بر", "tevvab": "تواب",
    "muntekim": "منتقم", "afuvv": "عفو", "rauf": "رؤوف", "malikul_mulk": "مالك الملك",
    "zul_celali_vel_ikram": "ذو الجلال والإكرام", "muksit": "مقسط", "cami": "جامع",
    "gani": "غني", "mugni": "مغني", "mani": "مانع", "darr": "ضار", "nafi": "نافع",
    "nur": "نور", "hadi": "هادي", "bedi": "بديع", "baki": "باقي", "varis": "وارث",
    "resid": "رشيد", "sabur": "صبور",
    # 99 dışı iki isim (asset listesi F bölümü sonu)
    "cemil": "جميل", "safi": "شافي",
}

# 99 dışı isimler: F tablosunda yok, tetikleyicilerde geçiyor.
ESMA_99_DISI = {
    "cemil": dict(ad="Cemîl", ebced=83, karsiligi="Süs çiçekleri seti"),
    "safi": dict(ad="Şâfî", ebced=391, karsiligi="Reyhan ve lavanta saksıları"),
}

# Asset listesindeki "celâlî isimler öğretici kart" satırı: 7 kart.
CELALI_ISIMLER = ["kahhar", "kabid", "hafid", "muzill", "mumit", "muntekim", "darr"]
