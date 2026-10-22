# logo_ar.py - a concept for the Arabic title: «باب اليمن» cut in the same gold as BAB AL-YEMEN (menu_art.logo):
# bands of gold from pale to deep orange, a line of shine, a dark extrusion down and to the right, lit top and left
# edges, the dark outline and the soft ring. The letters are Noto Kufi Arabic Black, drawn large and brought down to
# pixels; the jambiya sits between the two words, turned to point the way Arabic reads.
#
#   python3 logo_ar.py [size] [weight]   writes ../art/preview/logo_ar.png (and logo_ar_x3.png) for a look
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import menu_art as MA                                   # noqa: E402
from menu_art import hexc, ring_of, FACE, JAMBIYA, JAMBIYA_PAL, sprite, outline, silhouette   # noqa: E402

FONT = '/root/.fonts/NotoKufiArabic[wght].ttf'
SS = 4


def word_mask(text, size, wt, H, base):
    """A word's mask, H rows tall with its baseline on row `base`, cropped left and right to its ink."""
    f = ImageFont.truetype(FONT, size * SS, layout_engine=ImageFont.Layout.RAQM)
    try:
        f.set_variation_by_axes([wt])
    except Exception:
        pass
    w = int(size * SS * 0.9 * (len(text) + 1))
    im = Image.new('L', (w, H * SS), 0)
    ImageDraw.Draw(im).text((w - size * SS // 2, base * SS), text, font=f, fill=255, anchor='rs', direction='rtl')
    small = np.asarray(im.resize((w // SS, H), Image.BOX)) >= 118
    cols = np.where(small.any(0))[0]
    return small[:, cols[0]:cols[-1] + 1]


def ar_logo(size=44, wt=900, gap=4, jambiya=True):
    H = int(size * 1.08)                                # alef top to the dots under ب
    base = int(size * 0.80)
    right, left = word_mask('باب', size, wt, H, base), word_mask('اليمن', size, wt, H, base)
    j = sprite(JAMBIYA, JAMBIYA_PAL).transpose(Image.FLIP_LEFT_RIGHT) if jambiya else None
    jw = j.width if j else 6
    Wt = left.shape[1] + gap + jw + gap + right.shape[1]
    EX, PAD = 3, 3
    Wc, Hc = Wt + EX + PAD * 2, H + EX + PAD * 2
    M = np.zeros((Hc, Wc), bool)
    M[PAD:PAD + H, PAD:PAD + left.shape[1]] |= left
    xr = PAD + left.shape[1] + gap + jw + gap
    M[PAD:PAD + H, xr:xr + right.shape[1]] |= right
    rows = np.where(M.any(1))[0]
    top, bot = rows[0], rows[-1]
    # (what follows is menu_art.logo's paint, on these letters)
    X = np.zeros_like(M)
    for k in range(1, EX + 1):
        X[k:, k:] |= M[:-k, :-k]
    X &= ~M
    out = np.zeros((Hc, Wc, 4), np.uint8)
    yy = np.arange(Hc)[:, None].repeat(Wc, 1)
    depth = np.zeros((Hc, Wc), int)
    for k in range(EX, 0, -1):
        sh = np.zeros_like(M)
        sh[k:, k:] = M[:-k, :-k]
        depth[sh & X] = k
    for k, c in {1: hexc('#7a3a08'), 2: hexc('#5a2806'), 3: hexc('#3c1a04')}.items():
        out[(depth == k) & X] = c
    t = (yy - top) / float(max(1, bot - top))
    band = np.clip((t * (len(FACE) - 1.0) + 0.35).astype(int), 0, len(FACE) - 1)
    for i, c in enumerate(FACE):
        out[M & (band == i)] = hexc(c)
    shine = PAD + base - int(size * 0.30)              # across the bodies of the letters, as on the Latin one
    out[M & (yy == shine)] = hexc('#fffbe0')
    out[M & (yy == shine + 1)] = hexc('#ffe26a')
    up = np.zeros_like(M); up[1:, :] = M[:-1, :]
    lf = np.zeros_like(M); lf[:, 1:] = M[:, :-1]
    dn = np.zeros_like(M); dn[:-1, :] = M[1:, :]
    out[M & ~up] = hexc('#ffffff')
    lft = M & ~lf & up
    out[lft] = np.minimum(255, out[lft].astype(int) + np.array([30, 30, 40, 0])).astype(np.uint8)
    out[M & ~dn & up] = hexc('#a03406')
    im = Image.fromarray(out, 'RGBA')
    if j:
        jx, jy = PAD + left.shape[1] + gap, PAD + base - int(size * 0.22) - j.height // 2
        im.alpha_composite(silhouette(j, '#3c1a04'), (jx + 2, jy + 2))
        im.alpha_composite(j, (jx, jy))
    im = outline(im, '#10101c')
    a = np.array(im)
    a[ring_of(a[..., 3] > 0)] = hexc('#10142c', 150)
    return Image.fromarray(a, 'RGBA')


if __name__ == '__main__':
    size = int(sys.argv[1]) if len(sys.argv) > 1 else 44
    wt = int(sys.argv[2]) if len(sys.argv) > 2 else 900
    pv = os.path.join(HERE, '..', 'art', 'preview')
    os.makedirs(pv, exist_ok=True)
    lg = ar_logo(size, wt)
    lg.save(os.path.join(pv, 'logo_ar.png'))
    en = MA.logo()
    bg = Image.new('RGBA', (max(lg.width, en.width) + 20, lg.height + en.height + 30), hexc('#5aa8d8'))
    bg.alpha_composite(en, (10, 10))
    bg.alpha_composite(lg, (10, en.height + 20))
    bg.resize((bg.width * 3, bg.height * 3), Image.NEAREST).save(os.path.join(pv, 'logo_ar_x3.png'))
    print('arabic logo', lg.size, 'latin logo', en.size)
