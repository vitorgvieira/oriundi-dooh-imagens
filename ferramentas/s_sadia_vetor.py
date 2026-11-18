# Vetoriza o S original da Sadia (arquivo de 320 px enviado pelo Vitor) com potrace e devolve a
# mascara do S em qualquer altura, com o "Sadia" do miolo tirado da logo oficial de 1280 px.
# Uso: from s_sadia_vetor import s_original; m = s_original(altura_px)  -> Image L (S + wordmark)
import numpy as np
import potrace
from PIL import Image, ImageDraw
from scipy import ndimage

ORIG = 'brf/sadia/elementos/s_sadia_original_320.png'
LOGO = 'brf/sadia/logo/sadia_vermelha.png'


def _curvas():
    a = np.asarray(Image.open(ORIG).convert('RGBA'))[..., 3].astype(float) / 255
    lab, n = ndimage.label(a > 0.5)
    sz = ndimage.sum(a > 0.5, lab, range(1, n + 1))
    s = (lab == int(np.argmax(sz)) + 1)
    s = ndimage.binary_dilation(s, iterations=1) & (a > 0.08)   # inclui a borda antialias
    up = np.asarray(Image.fromarray((a * s * 255).astype(np.uint8)).resize((320 * 8, 320 * 8), Image.BICUBIC)) > 127
    plist = potrace.Bitmap(up).trace(turdsize=50, alphamax=1.0, opticurve=True, opttolerance=0.2)
    bbox = np.argwhere(up); (y0, x0), (y1, x1) = bbox.min(0), bbox.max(0)
    return plist, (x0, y0, x1, y1)


def _xy(p):
    return (p.x, p.y) if hasattr(p, 'x') else (p[0], p[1])


def _pts(curve, sc, ox, oy):
    pts = []; p0 = _xy(curve.start_point)
    for seg in curve.segments:
        if seg.is_corner:
            pts += [p0, _xy(seg.c), _xy(seg.end_point)]
        else:
            t = np.linspace(0, 1, 24)[:, None]
            P0, P1, P2, P3 = (np.array(_xy(v), float) for v in (p0, seg.c1, seg.c2, seg.end_point))
            pts += list((1 - t) ** 3 * P0 + 3 * (1 - t) ** 2 * t * P1 + 3 * (1 - t) * t * t * P2 + t ** 3 * P3)
        p0 = _xy(seg.end_point)
    return [((x - ox) * sc, (y - oy) * sc) for x, y in pts]


def s_original(altura, com_wordmark=True):
    plist, (x0, y0, x1, y1) = _curvas()
    sc = altura / (y1 - y0); w = round((x1 - x0) * sc)
    SS = 2
    m = Image.new('L', (w * SS, altura * SS), 0); d = ImageDraw.Draw(m)
    for c in plist:   # potrace devolve tambem a moldura do bitmap: pular; o S nao tem furo
        pts = np.array(_pts(c, 1, 0, 0))
        if pts.min() <= 1 and pts.max() >= 320 * 8 - 1:
            continue
        d.polygon([(x * SS, y * SS) for x, y in _pts(c, sc, x0, y0)], fill=255)
    m = m.resize((w, altura), Image.LANCZOS)
    if com_wordmark:
        # "Sadia" do miolo: no original de 320 px ocupa x 128-198, y 213-248 (S em x 68-252, y 16-304)
        k = altura / (304 - 16)
        lg = Image.open(LOGO).convert('RGBA').getchannel('A')
        lw = round((198 - 128) * k); lh = round(lg.height * lw / lg.width)
        lg = lg.resize((lw, lh), Image.LANCZOS)
        m.paste(255, (round((128 - 68) * k), round((213 - 16) * k)), lg)
    return m
