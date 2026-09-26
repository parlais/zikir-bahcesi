#!/usr/bin/env python3
"""Çekimlerden karşılaştırma panosu ve geçiş animasyonu.

Pano: görüntüler satır satır dizilir, sütunların üstüne başlık yazılır.
    python3 tools/render/pano.py pano cikti.jpg --sutun 3 --baslik "Nur|Ara|Ori" a.png b.png c.png ...

Animasyon: kare dizisinden GIF; --gidis-donus ile sona varınca geri oynar.
    python3 tools/render/pano.py gif cikti.gif --sure 120 --bekle 1200 --gidis-donus dizi_*.png

Şerit: dizinin birkaç karesi yan yana, üstlerinde t değeri (tek satırlık pano).
    python3 tools/render/pano.py serit cikti.jpg --adet 5 dizi_*.png

Fark: iki çekimin piksel farkı (ortalama, en büyük, %99'luk) ve ısı haritası. Bir
değişikliğin onaylı görünüşü bozmadığını denetlemek için; aynı çekimin iki kez
alınmasıyla bulunan lavapipe gürültüsüyle karşılaştırılır.
    python3 tools/render/pano.py fark eski.png yeni.png fark.png
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ZEMIN = (245, 240, 230)
YAZI = (58, 42, 30)
ARA = 10
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _font(boy):
    try:
        return ImageFont.truetype(FONT, boy)
    except OSError:
        return ImageFont.load_default()


def pano(cikti, dosyalar, sutun, basliklar, genislik=None):
    resimler = [Image.open(d).convert("RGB") for d in dosyalar]
    w, h = resimler[0].size
    if genislik:
        h = round(h * genislik / w)
        w = genislik
        resimler = [r.resize((w, h), Image.LANCZOS) for r in resimler]
    satir = (len(resimler) + sutun - 1) // sutun
    ust = 50 if basliklar else ARA
    pano_r = Image.new("RGB", (sutun * w + (sutun + 1) * ARA, ust + satir * h + satir * ARA), ZEMIN)
    ciz = ImageDraw.Draw(pano_r)
    f = _font(26)
    for i, b in enumerate(basliklar or []):
        x = ARA + i * (w + ARA) + w // 2
        ciz.text((x, ust // 2 + 2), b, font=f, fill=YAZI, anchor="mm")
    for i, r in enumerate(resimler):
        pano_r.paste(r, (ARA + (i % sutun) * (w + ARA), ust + (i // sutun) * (h + ARA)))
    pano_r.save(cikti, quality=90)
    print(cikti, pano_r.size)


def gif(cikti, dosyalar, sure, bekle, gidis_donus, genislik=None):
    kareler = [Image.open(d).convert("RGB") for d in dosyalar]
    if genislik:
        w, h = kareler[0].size
        kareler = [k.resize((genislik, round(h * genislik / w)), Image.LANCZOS) for k in kareler]
    sureler = [sure] * len(kareler)
    sureler[0] = sureler[-1] = bekle
    if gidis_donus and len(kareler) > 2:
        kareler += kareler[-2:0:-1]
        sureler += [sure] * (len(kareler) - len(sureler))
    # Ortak palet: gök geçişlerinde kare kare titreme olmasın. Baştan sona dört kare
    # örneklenir (yakınlaşma filminde son karelerin yeşili paletin dışında kalıyordu).
    n = len(kareler)
    secilen = [kareler[round(i * (n - 1) / 3)] for i in range(4)]
    ornek = Image.new("RGB", (kareler[0].width, kareler[0].height * len(secilen)))
    for i, k in enumerate(secilen):
        ornek.paste(k, (0, i * kareler[0].height))
    palet = ornek.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    p_kareler = [k.quantize(palette=palet, dither=Image.Dither.FLOYDSTEINBERG) for k in kareler]
    p_kareler[0].save(cikti, save_all=True, append_images=p_kareler[1:], duration=sureler, loop=0, optimize=True)
    print(cikti, len(p_kareler), "kare", round(Path(cikti).stat().st_size / 1e6, 2), "MB")


def serit(cikti, dosyalar, adet, genislik=None):
    n = len(dosyalar)
    secilen = [dosyalar[round(i * (n - 1) / (adet - 1))] for i in range(adet)]
    basliklar = []
    for d in secilen:
        i = dosyalar.index(d)
        faz = i / (n - 1)
        t = faz * faz * (3 - 2 * faz)
        basliklar.append("Nur" if t == 0 else ("Ori" if t == 1 else "t = %.2f" % t).replace(".", ","))
    pano(cikti, secilen, adet, basliklar, genislik)


def fark(eski, yeni, cikti=None):
    import numpy as np
    a = np.asarray(Image.open(eski).convert("RGB"), dtype=np.float32)
    b = np.asarray(Image.open(yeni).convert("RGB"), dtype=np.float32)
    d = np.abs(a - b).max(axis=2)
    print("fark: ortalama %.3f, %%99 %.1f, en büyük %.0f (/255); 8'den büyük piksel %%%.2f"
          % (d.mean(), np.percentile(d, 99), d.max(), (d > 8).mean() * 100))
    if cikti:
        # Isı haritası: farkın 8 katı, kırmızı; altında soluk eski görüntü
        soluk = a.mean(axis=2, keepdims=True) * 0.35
        isi = np.clip(d * 8, 0, 255)[..., None]
        r = np.concatenate([np.maximum(soluk, isi), soluk, soluk], axis=2)
        Image.fromarray(r.astype(np.uint8)).save(cikti)
        print(cikti)


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    alt = a.add_subparsers(dest="is_", required=True)
    p = alt.add_parser("pano")
    p.add_argument("cikti")
    p.add_argument("dosyalar", nargs="+")
    p.add_argument("--sutun", type=int, default=3)
    p.add_argument("--baslik", default="", help="sütun başlıkları, | ile ayrılmış")
    p.add_argument("--genislik", type=int)
    g = alt.add_parser("gif")
    g.add_argument("cikti")
    g.add_argument("dosyalar", nargs="+")
    g.add_argument("--sure", type=int, default=120, help="kare süresi (ms)")
    g.add_argument("--bekle", type=int, default=1200, help="uçlarda bekleme (ms)")
    g.add_argument("--gidis-donus", action="store_true")
    g.add_argument("--genislik", type=int)
    s = alt.add_parser("serit")
    s.add_argument("cikti")
    s.add_argument("dosyalar", nargs="+")
    s.add_argument("--adet", type=int, default=5)
    s.add_argument("--genislik", type=int)
    f = alt.add_parser("fark")
    f.add_argument("eski")
    f.add_argument("yeni")
    f.add_argument("cikti", nargs="?")
    x = a.parse_args()
    if x.is_ == "pano":
        pano(x.cikti, x.dosyalar, x.sutun, [b for b in x.baslik.split("|") if b], x.genislik)
    elif x.is_ == "gif":
        gif(x.cikti, sorted(x.dosyalar), x.sure, x.bekle, x.gidis_donus, x.genislik)
    elif x.is_ == "fark":
        fark(x.eski, x.yeni, x.cikti)
    else:
        serit(x.cikti, sorted(x.dosyalar), x.adet, x.genislik)


if __name__ == "__main__":
    main()
