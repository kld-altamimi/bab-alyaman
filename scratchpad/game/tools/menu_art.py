# menu_art.py - the pictures for the home screen and the campaign map: the logo, the map itself, and the small things
# drawn over it (mission badges, landmarks, the CLEAR stamp, clouds, the compass).
#
#   python3 menu_art.py            writes previews to ../art/preview/ (export_art.py takes the real ones)
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock'
sys.path.insert(0, MOCK)
from px import sprite, outline, silhouette, rgba          # noqa: E402

EDGE = (16, 16, 28, 255)


def hexc(h, a=255):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def mask_to_img(m, color):
    a = np.zeros(m.shape + (4,), np.uint8)
    a[m] = color
    return Image.fromarray(a, 'RGBA')


def ring_of(m, diag=True):
    """The pixels just outside a mask."""
    st = np.ones((3, 3), bool) if diag else ndimage.generate_binary_structure(2, 1)
    return ndimage.binary_dilation(m, st) & ~m


# ================================================================ the logo
# Heavy block capitals cut in gold with a dark extrusion, a line of shine across them and a few bullet holes. The hyphen is
# a jambiya.
SS = 4          # drawn this many times larger, then brought down


def _glyph(ch, H, S):
    """A glyph's mask at SS times size: H cap height, S stroke, both in final pixels."""
    W = {'B': 22, 'A': 22, 'L': 17, 'Y': 22, 'E': 18, 'M': 27, 'N': 22}[ch]
    w, h, s, g = W * SS, H * SS, S * SS, 0           # g: the width of a stencil cut (none: at this size the cuts read as extra letters)
    im = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(im)

    def rect(x0, y0, x1, y1, v=255):
        d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=v)

    def rrect(x0, y0, x1, y1, r, v=255, corners=None):
        # (by hand: PIL's own rounded rectangle refuses some small boxes)
        tl, tr, br, bl = corners if corners else (True, True, True, True)
        r = int(max(0, min(r, (x1 - x0) // 2, (y1 - y0) // 2)))
        d.rectangle([x0, y0, x1 - 1, y1 - 1], fill=v)
        if r <= 0:
            return
        for on, (cx0, cy0), (kx, ky) in ((tl, (x0, y0), (x0, y0)), (tr, (x1 - 2 * r, y0), (x1 - r, y0)),
                                          (br, (x1 - 2 * r, y1 - 2 * r), (x1 - r, y1 - r)), (bl, (x0, y1 - 2 * r), (x0, y1 - r))):
            if not on:
                continue
            d.rectangle([kx, ky, kx + r - 1, ky + r - 1], fill=0 if v else 255)
            d.ellipse([cx0, cy0, cx0 + 2 * r - 1, cy0 + 2 * r - 1], fill=v)
            # the ellipse also paints the other quarters of its square; put back what was there
        return

    if ch == 'B':
        rect(0, 0, s, h)
        mid = int(h * 0.47)
        bx = s + g
        rrect(bx, 0, w - SS * 2, mid + s // 2, r=int(mid * 0.55), corners=(False, True, True, False))
        rrect(bx + s, s, w - SS * 2 - s, mid - s // 2, r=int(mid * 0.3), v=0, corners=(False, True, True, False))
        rrect(bx, mid - s // 2, w, h, r=int((h - mid) * 0.55), corners=(False, True, True, False))
        rrect(bx + s, mid + s // 2, w - s, h - s, r=int((h - mid) * 0.3), v=0, corners=(False, True, True, False))
        rect(bx, mid - s // 2 + SS, bx + s, mid + s // 2 - SS, 255)
    elif ch == 'A':
        r = int(w * 0.42)
        rrect(0, 0, w, h, r=r, corners=(True, True, False, False))
        rrect(s, s, w - s, h + r, r=max(1, r - s), v=0, corners=(True, True, False, False))
        cb = int(h * 0.56)
        rect(0, cb, w, cb + int(s * 0.85))
    elif ch == 'L':
        rect(0, 0, s, h)
        rect(s + g, h - s, w, h)
    elif ch == 'Y':
        cy = int(h * 0.52)
        d.polygon([(0, 0), (s * 1.15, 0), (w / 2 + s * 0.2, cy - s * 0.2), (w / 2 + s * 0.2, cy + s * 0.55), (w / 2 - s * 0.55, cy + s * 0.55), (0, s * 0.9)], fill=255)
        d.polygon([(w, 0), (w - s * 1.15, 0), (w / 2 - s * 0.2 + g, cy - s * 0.2), (w / 2 - s * 0.2 + g, cy + s * 0.55), (w / 2 + s * 0.55, cy + s * 0.55), (w, s * 0.9)], fill=255)
        rect(w // 2 - s // 2, cy + int(s * 0.3), w // 2 + s // 2 + (s % 2), h)
    elif ch == 'E':
        rect(0, 0, s, h)
        x = s + g
        rect(x, 0, w, s)
        rect(x, int(h * 0.5 - s * 0.5), w - SS * 3, int(h * 0.5 + s * 0.5))
        rect(x, h - s, w, h)
    elif ch == 'M':
        rect(0, 0, s, h)
        rect(w - s, 0, w, h)
        vy = int(h * 0.64)
        d.polygon([(s + g, 0), (s + g + s * 0.95, 0), (w / 2, vy - s * 1.25), (w / 2, vy), (s + g, s * 1.7)], fill=255)
        d.polygon([(w - s - g, 0), (w - s - g - s * 0.95, 0), (w / 2, vy - s * 1.25), (w / 2, vy), (w - s - g, s * 1.7)], fill=255)
    elif ch == 'N':
        rect(0, 0, s, h)
        rect(w - s, 0, w, h)
        d.polygon([(s + g, 0), (s + g + s * 1.05, 0), (w - s - g, h - s * 1.6), (w - s - g, h), (w - s - g - s * 1.05, h), (s + g, s * 1.6)], fill=255)
    a = np.asarray(im.resize((W, H), Image.BOX)) >= 128
    return a


JAMBIYA = [
    '........................xx.',
    '......................xxWWx',
    '....................xxWWSSx',
    '..................xxWWSSSx.',
    '.xxxx..........xxxWWSSSSx..',
    'xGYYGxxxxxxxxxxWWSSSSSxx...',
    'xGRRGxBbBbBbBSSSSSSSxx.....',
    'xGYYGxxxxxxxxxxxxxxx.......',
    '.xxxx......................',
]
JAMBIYA_PAL = {'x': '#10101c', 'G': '#d8a030', 'Y': '#fff0a0', 'R': '#c02818', 'B': '#7a4420', 'b': '#a86030',
               'S': '#b8c4d0', 'W': '#ffffff'}

FACE = ['#fffbe0', '#fff0a0', '#ffd84a', '#ffc22e', '#f8a020', '#ec7c14', '#d45a0c', '#b03c08']


def logo(H=26, S=5):
    word = 'BAB AL-YEMEN'
    sp, gap = 2, 10
    parts, x = [], 0
    for ch in word:
        if ch == ' ':
            x += gap - sp
            continue
        if ch == '-':
            j = sprite(JAMBIYA, JAMBIYA_PAL)
            parts.append(('img', j, x + 1, H // 2 - 4))
            x += j.width + sp + 1
            continue
        m = _glyph(ch, H, S)
        parts.append(('mask', m, x, 0))
        x += m.shape[1] + sp
    Wt = x - sp
    EX = 3                                            # how deep the extrusion goes
    PAD = 3
    Wc, Hc = Wt + EX + PAD * 2, H + EX + PAD * 2
    M = np.zeros((Hc, Wc), bool)
    for kind, m, gx, gy in parts:
        if kind == 'mask':
            M[PAD + gy:PAD + gy + m.shape[0], PAD + gx:PAD + gx + m.shape[1]] |= m
    # the extrusion, down and to the right
    X = np.zeros_like(M)
    for k in range(1, EX + 1):
        X[k:, k:] |= M[:-k, :-k]
    X &= ~M
    out = np.zeros((Hc, Wc, 4), np.uint8)
    yy = np.arange(Hc)[:, None].repeat(Wc, 1)
    # the extrusion: darker the further back
    depth = np.zeros((Hc, Wc), int)
    for k in range(EX, 0, -1):
        sh = np.zeros_like(M)
        sh[k:, k:] = M[:-k, :-k]
        depth[sh & X] = k
    ex_cols = {1: hexc('#7a3a08'), 2: hexc('#5a2806'), 3: hexc('#3c1a04')}
    for k, c in ex_cols.items():
        out[(depth == k) & X] = c
    # the face: bands of gold from pale at the top to deep orange at the foot, and a bright line of shine across it
    t = (yy - PAD) / float(H - 1)
    band = np.clip((t * (len(FACE) - 1.0) + 0.35).astype(int), 0, len(FACE) - 1)
    for i, c in enumerate(FACE):
        out[M & (band == i)] = hexc(c)
    shine = PAD + int(H * 0.40)
    out[M & (yy == shine)] = hexc('#fffbe0')
    out[M & (yy == shine + 1)] = hexc('#ffe26a')
    # edges: lit along the top and the left, darker along the bottom
    up = np.zeros_like(M); up[1:, :] = M[:-1, :]
    left = np.zeros_like(M); left[:, 1:] = M[:, :-1]
    down = np.zeros_like(M); down[:-1, :] = M[1:, :]
    out[M & ~up] = hexc('#ffffff')
    lft = M & ~left & up
    out[lft] = np.minimum(255, out[lft].astype(int) + np.array([30, 30, 40, 0])).astype(np.uint8)
    out[M & ~down & up] = hexc('#a03406')
    # a few bullet holes, for the look of a sign that has been in a fight
    for hx, hy in ((PAD + 33, PAD + 7), (PAD + 128, PAD + 17), (PAD + 201, PAD + 5)):
        if M[hy, hx] and M[hy + 1, hx + 1]:
            out[hy, hx] = hexc('#2a1004'); out[hy + 1, hx] = hexc('#2a1004'); out[hy, hx + 1] = hexc('#2a1004'); out[hy + 1, hx + 1] = hexc('#5a2806')
            if M[hy - 1, hx]:
                out[hy - 1, hx] = hexc('#ffffff')
    im = Image.fromarray(out, 'RGBA')
    for kind, j, gx, gy in parts:
        if kind == 'img':
            # the jambiya casts the same shadow as the letters
            sh = silhouette(j, '#3c1a04')
            im.alpha_composite(sh, (PAD + gx + 2, PAD + gy + 2))
            im.alpha_composite(j, (PAD + gx, PAD + gy))
    im = outline(im, '#10101c')
    # and a soft dark edge outside that, so it reads over sky and sea alike
    a = np.array(im)
    solid = a[..., 3] > 0
    r2 = ring_of(solid)
    a[r2] = hexc('#10142c', 150)
    return Image.fromarray(a, 'RGBA')


# ================================================================ the logo in Arabic
# «باب اليمن» in the same gold (Khaled chose it, 17 Oct, with BAB AL-YEMEN kept small under it): the letters are
# Noto Kufi Arabic Black (github google/fonts ofl/notokufiarabic, installed in ~/.fonts), drawn large and brought down
# to pixels; then the Latin logo's paint. The jambiya sits between the two words, turned to point the way Arabic reads.
AR_FONT = os.path.expanduser('~/.fonts/NotoKufiArabic[wght].ttf')


def _ar_word(text, size, wt, H, base):
    """A word's mask, H rows tall with its baseline on row `base`, cropped left and right to its ink."""
    from PIL import ImageFont
    if not os.path.exists(AR_FONT):
        raise SystemExit('the Arabic logo needs ' + AR_FONT + ' (google/fonts: ofl/notokufiarabic)')
    f = ImageFont.truetype(AR_FONT, size * SS, layout_engine=ImageFont.Layout.RAQM)
    f.set_variation_by_axes([wt])
    w = int(size * SS * 0.9 * (len(text) + 1))
    im = Image.new('L', (w, H * SS), 0)
    ImageDraw.Draw(im).text((w - size * SS // 2, base * SS), text, font=f, fill=255, anchor='rs', direction='rtl')
    small = np.asarray(im.resize((w // SS, H), Image.BOX)) >= 118
    cols = np.where(small.any(0))[0]
    return small[:, cols[0]:cols[-1] + 1]


def logo_ar(size=40, wt=900, gap=4):
    H = int(size * 1.08)                                # from the top of the alef to the dots under ب
    base = int(size * 0.80)
    right, left = _ar_word('باب', size, wt, H, base), _ar_word('اليمن', size, wt, H, base)
    j = sprite(JAMBIYA, JAMBIYA_PAL).transpose(Image.FLIP_LEFT_RIGHT)
    Wt = left.shape[1] + gap + j.width + gap + right.shape[1]
    EX, PAD = 3, 3
    Wc, Hc = Wt + EX + PAD * 2, H + EX + PAD * 2
    M = np.zeros((Hc, Wc), bool)
    M[PAD:PAD + H, PAD:PAD + left.shape[1]] |= left
    xr = PAD + left.shape[1] + gap + j.width + gap
    M[PAD:PAD + H, xr:xr + right.shape[1]] |= right
    rows = np.where(M.any(1))[0]
    top, bot = rows[0], rows[-1]
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
    jx, jy = PAD + left.shape[1] + gap, PAD + base - int(size * 0.22) - j.height // 2
    im.alpha_composite(silhouette(j, '#3c1a04'), (jx + 2, jy + 2))
    im.alpha_composite(j, (jx, jy))
    im = outline(im, '#10101c')
    a = np.array(im)
    a[ring_of(a[..., 3] > 0)] = hexc('#10142c', 150)
    return Image.fromarray(a, 'RGBA')


# ================================================================ noise
def value_noise(w, h, cell, seed):
    rs = np.random.RandomState(seed)
    gw, gh = w // cell + 3, h // cell + 3
    g = rs.rand(gh, gw)
    ys, xs = np.mgrid[0:h, 0:w].astype(float)
    fx, fy = xs / cell, ys / cell
    x0, y0 = np.floor(fx).astype(int), np.floor(fy).astype(int)
    tx, ty = fx - x0, fy - y0
    tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    a, b = g[y0, x0], g[y0, x0 + 1]
    c, d = g[y0 + 1, x0], g[y0 + 1, x0 + 1]
    return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty


def fbm(w, h, cell, seed, octaves=4):
    out, amp, tot = np.zeros((h, w)), 1.0, 0.0
    for o in range(octaves):
        out += amp * value_noise(w, h, max(2, cell >> o), seed + o * 17)
        tot += amp
        amp *= 0.5
    return out / tot


BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 + 1 / 32.0


def dither(t, h, w):
    """Ordered dither threshold for a field of fractions."""
    return t > np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]


# ================================================================ the campaign map
# Western Yemen with north up, from the Strait of Bab al-Mandab to beyond Marib: 120 pixels to a degree, the top-left
# corner at 42.3 E, 16.3 N. Coasts and places are where they are on a real map, near enough; the relief is made up to
# look right (the plain along the Red Sea, the wall of the western mountains, the high plateau, the sands to the east).
MW, MH = 720, 480          # bigger than any screen: the map slides to keep the chosen mission in view
PXD, LON0, LAT0 = 120.0, 42.30, 16.30


def P(lon, lat):
    return ((lon - LON0) * PXD, (LAT0 - lat) * PXD)


GEO = {'m1': (43.40, 12.94), 'mocha': (43.25, 13.32), 'zabid': (43.32, 14.20), 'hodeidah': (42.95, 14.80), 'haraz': (43.74, 15.07),
       'kawkaban': (43.90, 15.50), 'taiz': (44.02, 13.58), 'ibb': (44.18, 13.97), 'dhamar': (44.40, 14.55), 'sanaa': (44.20, 15.35),
       'marib': (45.33, 15.46)}
NODES = {k: tuple(int(round(v)) for v in P(*ll)) for k, ll in GEO.items()}
# the coast of Yemen, from the tip at the strait up the Red Sea to the top of the map, then (after the map's own edges)
# along the Gulf of Aden back to the strait
RED_SEA_COAST = [(43.48, 12.68), (43.44, 12.75), (43.42, 12.86), (43.39, 12.95), (43.35, 13.05), (43.28, 13.20), (43.25, 13.32), (43.24, 13.46),
                 (43.25, 13.62), (43.24, 13.80), (43.18, 13.92), (43.10, 14.08), (43.03, 14.25), (42.98, 14.45), (42.96, 14.62), (42.95, 14.78),
                 (42.92, 14.88), (42.88, 14.95), (42.93, 15.02), (42.85, 15.14), (42.75, 15.22), (42.68, 15.30), (42.72, 15.40), (42.70, 15.55),
                 (42.68, 15.70), (42.73, 15.90), (42.78, 16.10), (42.80, 16.30)]
GULF_COAST = [(48.30, 14.08), (48.00, 13.98), (47.60, 13.85), (47.20, 13.70), (46.80, 13.56), (46.40, 13.48), (46.00, 13.42), (45.68, 13.35),
              (45.38, 13.12), (45.20, 12.95), (45.05, 12.84), (45.03, 12.77), (44.97, 12.75), (44.94, 12.79), (44.88, 12.80), (44.80, 12.74),
              (44.60, 12.70), (44.30, 12.64), (44.00, 12.62), (43.80, 12.65), (43.60, 12.68), (43.50, 12.67)]
AFRICA_COAST = [(42.30, 13.52), (42.45, 13.36), (42.60, 13.20), (42.74, 13.01), (42.90, 12.90), (43.10, 12.72), (43.20, 12.62), (43.28, 12.54),
                (43.32, 12.48), (43.38, 12.42), (43.42, 12.36), (43.45, 12.30)]
ISLANDS_LL = [(42.60, 15.35, 0.09, 0.15), (42.72, 13.72, 0.06, 0.09), (42.76, 14.02, 0.05, 0.07), (43.42, 12.66, 0.04, 0.025), (42.80, 13.62, 0.025, 0.03)]
WADIS_LL = [[(44.05, 14.02), (43.80, 14.10), (43.55, 14.16), (43.32, 14.21), (43.08, 14.24)],          # Wadi Zabid
            [(43.92, 13.58), (43.70, 13.50), (43.50, 13.43), (43.30, 13.38)],                          # down from Taiz towards Mocha
            [(43.75, 15.42), (43.50, 15.36), (43.25, 15.30), (42.98, 15.24)],                          # Wadi Surdud
            [(45.05, 15.42), (45.20, 15.44), (45.40, 15.47), (45.70, 15.50)]]                          # Wadi Adhanah, past Marib
TOWNS_LL = [(44.98, 12.79, 3), (43.29, 15.06, 1), (43.25, 13.80, 1), (43.47, 13.93, 1), (44.88, 13.06, 1), (44.38, 14.30, 1), (43.94, 15.66, 1),
            (43.60, 15.69, 1), (43.55, 15.47, 1), (45.57, 13.99, 1), (46.83, 14.54, 1), (44.30, 13.20, 1), (47.0, 15.0, 1)]
LABELS_LL = {'aden': (44.98, 12.79)}


def wiggle(poly, seed, amp=1.6, step=3):
    """Walk a coastline in short steps, pushed in and out a little, so it looks surveyed rather than drawn with a ruler."""
    rs = np.random.RandomState(seed)
    out = []
    ph = rs.rand() * 10
    for (x0, y0), (x1, y1) in zip(poly[:-1], poly[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(L / step))
        nx, ny = (-(y1 - y0) / L, (x1 - x0) / L) if L else (0, 0)
        on_edge = (x0 in (0, MW) and x1 in (0, MW)) or (y0 in (0, MH) and y1 in (0, MH))
        for k in range(n):
            u = k / n
            x, y = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
            if not on_edge:
                ph += 0.35 + rs.rand() * 0.5
                o = amp * (math.sin(ph) * 0.7 + (rs.rand() - 0.5) * 0.9)
                x, y = x + nx * o, y + ny * o
            out.append((x, y))
    out.append(poly[-1])
    return out


def poly_mask(poly, seed):
    im = Image.new('L', (MW * 2, MH * 2), 0)
    ImageDraw.Draw(im).polygon([(x * 2, y * 2) for x, y in wiggle(poly, seed)], fill=255)
    return np.asarray(im.resize((MW, MH), Image.BOX)) >= 128


def land_polys():
    yemen = [P(*ll) for ll in RED_SEA_COAST] + [(MW, 0), (MW, P(*GULF_COAST[0])[1])] + [P(*ll) for ll in GULF_COAST]
    yemen = [(min(MW, max(0, x)), min(MH, max(0, y))) for x, y in yemen]
    yemen = [yemen[0]] + yemen[1:]
    first = P(*RED_SEA_COAST[-1])
    yemen.insert(len(RED_SEA_COAST), (first[0], 0))
    africa = [P(*ll) for ll in AFRICA_COAST] + [(P(*AFRICA_COAST[-1])[0], MH), (0, MH)]
    africa = [(min(MW, max(0, x)), min(MH, max(0, y))) for x, y in africa]
    return yemen, africa


def land_masks():
    yp, ap = land_polys()
    arabia = poly_mask(yp, 3)
    africa = poly_mask(ap, 5)
    for lon, lat, rw, rh in ISLANDS_LL:
        cx_, cy_ = P(lon, lat)
        im = Image.new('L', (MW, MH), 0)
        ImageDraw.Draw(im).ellipse([cx_ - rw * PXD / 2, cy_ - rh * PXD / 2, cx_ + rw * PXD / 2, cy_ + rh * PXD / 2], fill=255)
        arabia |= np.asarray(im) > 0
    return arabia, africa


def ridged(w, h, cells, seed):
    out, tot = np.zeros((h, w)), 0.0
    for i, (c, wt) in enumerate(cells):
        n = value_noise(w, h, c, seed + i * 13)
        out += wt * (1 - np.abs(2 * n - 1)) ** 2
        tot += wt
    return out / tot


def smoothstep(a, b, x):
    t = np.clip((x - a) / (np.asarray(b, float) - a), 0, 1)
    return t * t * (3 - 2 * t)


def campaign_map():
    h, w = MH, MW
    ys, xs = np.mgrid[0:h, 0:w].astype(float)
    lon, lat = LON0 + xs / PXD, LAT0 - ys / PXD
    arabia, africa = land_masks()
    land = arabia | africa
    sea = ~land
    d_sea = ndimage.distance_transform_edt(land)
    d_land = ndimage.distance_transform_edt(sea)
    n_lo = fbm(w, h, 48, 11, 3)
    n_md = fbm(w, h, 18, 23, 3)
    wet = fbm(w, h, 30, 77, 3)

    # ---- height. The western mountains rise as a wall a little way in from the Red Sea; behind them the high plateau
    #      runs north to Sana'a and beyond, falling away east into the sands, and south into the hills behind Aden.
    esc = 43.52 + 0.06 * np.sin(lat * 3.1) + 0.10 * (n_lo - 0.5)
    high = smoothstep(esc - 0.05, esc + 0.32, lon)
    n_edge = fbm(w, h, 26, 57, 3) - 0.5
    high *= smoothstep(12.95, 13.45, lat + 0.35 * n_edge) * 0.85 + 0.15 * smoothstep(12.75, 13.0, lat)
    high *= 1 - 0.75 * smoothstep(44.75, 45.4, lon + 0.6 * n_edge + 0.12 * np.sin(lat * 4.0))
    plateau_e = smoothstep(46.0, 46.8, lon) * smoothstep(15.2, 14.4, lat) * 0.45       # the Hadramawt plateau, far east
    R = ridged(w, h, ((48, 1.0), (22, 0.6), (11, 0.32)), 41)
    peaks = np.zeros((h, w))
    for (plon, plat, r, ht) in ((44.00, 15.28, 0.16, 0.45), (44.03, 13.53, 0.10, 0.40), (43.73, 15.08, 0.14, 0.32), (43.62, 14.62, 0.16, 0.30),
                                (43.45, 14.85, 0.10, 0.22), (43.90, 15.50, 0.08, 0.22), (44.25, 14.02, 0.12, 0.28), (44.55, 13.75, 0.12, 0.18)):
        peaks += ht * np.exp(-(((lon - plon) / r) ** 2 + ((lat - plat) / r) ** 2))
    tihama = smoothstep(0, 46, d_sea) * 0.16
    e = tihama + high * (0.42 + 0.48 * R) + peaks * high + plateau_e * (0.6 + 0.5 * R)
    e *= smoothstep(1, 14, d_sea)
    sands = (smoothstep(45.25, 45.65, lon + 0.7 * (n_lo - 0.5) + 0.3 * n_edge) * smoothstep(14.5, 14.95, lat + 0.5 * n_edge)
             * (1 - smoothstep(46.2, 46.9, lon + 0.4 * n_edge) * smoothstep(15.2, 14.6, lat)))
    e = e * (1 - 0.65 * sands)
    e[~arabia] = (smoothstep(0, 40, d_sea) * (0.14 + 0.22 * n_md))[~arabia]
    es = ndimage.gaussian_filter(e, 0.9)
    gy, gx = np.gradient(es)
    hs = np.clip((-gx * 0.72 - gy * 0.70) * 34.0, -1.5, 1.5)

    img = np.zeros((h, w, 4), np.uint8)
    img[..., 3] = 255

    def paint(where, color):
        img[where] = hexc(color)

    def tones(where, cols, cuts, field):
        paint(where, cols[0])
        for i, cut in enumerate(cuts):
            soft = dither(np.clip((field - cut) / 0.18 + 0.5, 0, 1), h, w)
            paint(where & soft, cols[i + 1])

    # ---- the sea
    deep = d_land
    paint(sea, '#1a5290')
    paint(sea & (deep < 30) & dither(np.clip((30 - deep) / 8.0, 0, 1), h, w), '#1f5e9c')
    paint(sea & (deep < 18) & dither(np.clip((18 - deep) / 6.0, 0, 1), h, w), '#246cab')
    paint(sea & (deep < 9), '#2a7cb8')
    paint(sea & (deep < 5) & dither(np.clip((5 - deep) / 2.5, 0, 1), h, w), '#3895c6')
    paint(sea & (deep < 3), '#4cb0d0')
    paint(sea & (deep < 1.5), '#8fdce0')
    paint(sea & (deep < 1.5) & (((xs + ys) % 2) == 0), '#e8fbff')
    rs = np.random.RandomState(7)
    for _ in range(170):
        x0, y0 = rs.randint(0, w), rs.randint(0, h)
        L = rs.randint(3, 9)
        seg = (ys == y0) & (xs >= x0) & (xs < x0 + L)
        paint(seg & sea & (deep > 7), '#3a86c0' if rs.rand() < 0.55 else '#2b72ae')

    # ---- Yemen
    A = arabia
    plain = A & (e < 0.15)
    tones(plain, ['#cfac6c', '#dcbc80', '#e8cc92'], [-0.1, 0.45], hs + (n_md - 0.5) * 1.2)
    foot = A & (e >= 0.15) & (e < 0.31)
    tones(foot, ['#a88452', '#c29e68', '#d4b27c'], [-0.15, 0.35], hs)
    mnt = A & (e >= 0.31) & (e < 0.72)
    tones(mnt, ['#5c4230', '#7c5a3e', '#a07850', '#c49c6c', '#dcb886'], [-0.7, -0.15, 0.3, 0.85], hs)
    top = A & (e >= 0.72)
    tones(top, ['#5a4636', '#82664e', '#ac927a', '#d8c4a8'], [-0.5, 0.05, 0.6], hs)
    # the plateau round Sana'a and Dhamar: flatter, browner, with fields
    flat = A & (high > 0.6) & (np.abs(hs) < 0.35) & (lon > 44.1) & (lon < 44.9) & (lat > 14.3) & (lat < 15.9) & (R < 0.55)
    tones(flat, ['#a8784c', '#bf8e5c', '#cfa070'], [-0.2, 0.3], hs + (n_md - 0.5))
    # green: the rainy south of the highlands (Ibb, Taiz) and the Haraz terraces, on the slopes that face the weather
    rainy = (smoothstep(14.75, 14.35, lat) * smoothstep(13.25, 13.55, lat) * smoothstep(43.65, 43.85, lon) * (1 - smoothstep(44.45, 44.7, lon))
             + np.exp(-(((lon - 43.72) / 0.16) ** 2 + ((lat - 15.08) / 0.14) ** 2)) * 1.1)
    terr = A & (e > 0.24) & (e < 0.86) & (wet * (0.5 + rainy) > 0.48) & (rainy > 0.25)
    tb = (np.floor(e * 52) % 2) == 0
    paint(terr & tb, '#8aa64a')
    paint(terr & ~tb, '#647e34')
    paint(terr & tb & (hs > 0.45), '#a6c05c')
    paint(terr & ~tb & (hs < -0.4), '#4c6228')
    # fields round Sana'a: small plots, some green, some fallow
    rs3 = np.random.RandomState(29)
    sx_, sy_ = NODES['sanaa']
    for _ in range(190):
        r_, a_ = 12 + 34 * math.sqrt(rs3.rand()), rs3.rand() * 2 * math.pi
        fx_, fy_ = int(sx_ + r_ * math.cos(a_)), int(sy_ + r_ * math.sin(a_) * 0.85)
        fw_, fh_ = rs3.randint(2, 5), rs3.randint(2, 4)
        if 0 <= fy_ < h - fh_ and 0 <= fx_ < w - fw_ and A[fy_:fy_ + fh_, fx_:fx_ + fw_].all() and e[fy_, fx_] > 0.3:
            col_ = ['#98a650', '#86963e', '#b4b064', '#c8a464'][rs3.randint(0, 4)]
            img[fy_:fy_ + fh_, fx_:fx_ + fw_] = hexc(col_)
    # the sands east of Marib, and the dunes going on out of the map
    dz = A & (sands > 0.3) & (e < 0.34)
    rip = np.sin((xs * 0.8 + ys * 0.55) / 3.4 + n_lo * 10.0)
    paint(dz, '#e2aa5e')
    paint(dz & (rip > 0.5), '#f0c27a')
    paint(dz & (rip > 0.92), '#f8d896')
    paint(dz & (rip < -0.55), '#c88c46')
    # wadis: dry riverbeds with their scrub, down out of the mountains
    for k_, wll in enumerate(WADIS_LL):
        wm = Image.new('L', (w * 2, h * 2), 0)
        wpts = wiggle([P(*q) for q in wll], 9 + k_, amp=1.3, step=4)
        dr = ImageDraw.Draw(wm)
        for i in range(len(wpts) - 1):
            u = i / float(len(wpts) - 1)
            wd_ = int(3 + 13 * u * u) if k_ < 3 else int(3 + 4 * u)
            dr.line([(wpts[i][0] * 2, wpts[i][1] * 2), (wpts[i + 1][0] * 2, wpts[i + 1][1] * 2)], fill=255, width=wd_)
            if k_ < 3:
                dr.ellipse([wpts[i][0] * 2 - wd_ / 2, wpts[i][1] * 2 - wd_ / 2, wpts[i][0] * 2 + wd_ / 2, wpts[i][1] * 2 + wd_ / 2], fill=255)
        wad = (np.asarray(wm.resize((w, h), Image.BOX)) >= 100) & A
        if k_ < 3:
            # the wadis of the Tihama are farmed: a valley floor of fields, opening out as it reaches the plain
            paint(ring_of(wad) & A & (((xs + ys) % 2) == 0), '#9c9a52')
            fld = ((xs // 3 + ys // 2) % 2) == 0
            paint(wad & fld, '#88a040')
            paint(wad & ~fld, '#a4b452')
            paint(wad & (((xs * 3 + ys) % 9) == 0), '#5f7a2c')
            scrub = ring_of(wad | ring_of(wad)) & A & (n_md > 0.35) & (((xs * 7 + ys * 3) % 4) == 0)
            paint(scrub, '#6a8434')
        else:
            # out in the desert the wadi is dry: a pale bed of gravel and nothing growing in it
            paint(ring_of(wad) & A, '#9a7a4e')
            paint(wad, '#d8c8a0')
            paint(wad & (((xs * 5 + ys * 3) % 6) == 0), '#b8a888')
    # towns that are not missions: a pale block with a dark one beside it; Aden bigger
    for lon_, lat_, sz in TOWNS_LL:
        tx_, ty_ = (int(v) for v in P(lon_, lat_))
        for dx_ in range(-sz, sz + 1):
            for dy_ in range(-(sz // 2), sz // 2 + 1):
                if 0 <= ty_ + dy_ < h and 0 <= tx_ + dx_ < w and A[ty_ + dy_, tx_ + dx_] and (dx_ + dy_) % 2 == 0:
                    img[ty_ + dy_, tx_ + dx_] = hexc('#f4ecdc')
                    if tx_ + dx_ + 1 < w:
                        img[ty_ + dy_, tx_ + dx_ + 1] = hexc('#8a5a3a')
    # villages scattered through the mountains
    rs2 = np.random.RandomState(19)
    for _ in range(110):
        vx, vy = rs2.randint(130, 400), rs2.randint(8, 420)
        if A[vy, vx] and 0.25 < e[vy, vx] < 0.8 and not dz[vy, vx]:
            img[vy, vx] = hexc('#f4ecdc'); img[vy, vx + 1] = hexc('#8a5a3a')
    paint(A & (d_sea < 1.5), '#f2e2b0')

    # ---- Africa, across the water: the same ground, quieter, as it is not where the war is
    F = africa
    tones(F, ['#9c8668', '#ae9878', '#bea888'], [-0.2, 0.35], hs + (n_md - 0.5) * 1.5)
    paint(F & (d_sea < 1.5), '#d4c49c')

    # ---- a grid every degree, a shade darker, as a real map would have it
    grid = ((((xs - (43 - LON0) * PXD) % PXD) < 1) | (((ys - (LAT0 - 16.0) * PXD) % PXD) < 1)) & (((xs + ys) % 2) == 0)
    img[grid, :3] = (img[grid, :3] * 0.84).astype(np.uint8)
    return Image.fromarray(img, 'RGBA'), dict(nodes=NODES)


# ================================================================ things drawn over the map
BADGE_PAL = {
    'open': ('#10101c', '#ffc22e', '#fff4b0', '#b86a10', '#10101c'),       # edge, face, light, shade, number
    'clear': ('#10101c', '#7ccf62', '#d4f8b8', '#3c8a34', '#10101c'),
    'lock': ('#10101c', '#3c4278', '#6a72b0', '#262a52', '#aab1d8'),
}
DIGITS = {
    '1': ['.x.', 'xx.', '.x.', '.x.', 'xxx'], '2': ['xx.', '..x', '.x.', 'x..', 'xxx'], '3': ['xx.', '..x', '.x.', '..x', 'xx.'],
    '4': ['x.x', 'x.x', 'xxx', '..x', '..x'], '5': ['xxx', 'x..', 'xx.', '..x', 'xx.'],
    '6': ['.xx', 'x..', 'xxx', 'x.x', 'xxx'], '?': ['xx.', '..x', '.x.', '...', '.x.'],
}


def badge(n, state):
    edge, face, light, shade, num = BADGE_PAL[state]
    S = 15
    a = np.zeros((S, S, 4), np.uint8)
    yy, xx = np.mgrid[0:S, 0:S]
    r = np.hypot(xx - 7, yy - 7)
    disc = r <= 6.6
    a[disc] = hexc(face)
    a[disc & (r > 5.2) & ((xx + yy) > 15)] = hexc(shade)
    a[disc & (r > 5.2) & ((xx + yy) < 13)] = hexc(light)
    a[ring_of(disc, diag=False) & (r <= 7.6)] = hexc(edge)
    im = Image.fromarray(a, 'RGBA')
    dg = sprite(DIGITS[str(n)], {'x': num})
    im.alpha_composite(dg, (6, 5))
    return im


PADLOCK = ['.xxx.', 'x...x', 'x...x', 'xxxxx', 'xYYYx', 'xYxYx', 'xYYYx', 'xxxxx']
TICK = ['......x', '.....xG', 'x...xG.', 'Gx.xG..', '.GxG...', '..G....']


def stamp_clear():
    """A rubber stamp in red ink, a little crooked and a little worn."""
    import px
    t = px.text_img('CLEAR', px.FONT_B, '#d8261c')
    w, h = t.width + 10, t.height + 8
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    red = hexc('#d8261c')
    d.rectangle([0, 0, w - 1, h - 1], outline=red)
    d.rectangle([1, 1, w - 2, h - 2], outline=red)
    im.alpha_composite(t, (5, 4))
    a = np.array(im)
    rs = np.random.RandomState(4)
    worn = (rs.rand(h, w) < 0.10) & (a[..., 3] > 0)
    a[worn, 3] = 0
    return Image.fromarray(a, 'RGBA').rotate(8, resample=Image.NEAREST, expand=True)


def landmark(k):
    """A small picture of the place each mission happens, drawn as if pinned to the map."""
    im = Image.new('RGBA', (30, 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    C = lambda hx: hexc(hx)
    k = {'m1': 1, 'mocha': 2, 'haraz': 4, 'sanaa': 5, 'zabid': 'souq', 'marib': 'dam'}.get(k, k)
    if k == 1:
        # the battery: a dish on its mast and the launcher with its missile
        d.rectangle([4, 17, 26, 19], fill=C('#5c6440'))
        d.line([(9, 17), (9, 9)], fill=C('#8a8f96'), width=1)
        d.ellipse([3, 3, 15, 11], fill=C('#d8dde4'))
        d.ellipse([5, 5, 13, 9], fill=C('#aab2bc'))
        d.point((9, 7), fill=C('#5a6068'))
        d.polygon([(16, 15), (27, 9), (28, 10), (17, 16)], fill=C('#e8ecf0'))
        d.polygon([(26, 9), (29, 8), (28, 11)], fill=C('#d83a1c'))
        d.rectangle([15, 15, 24, 17], fill=C('#6c7448'))
        d.point((17, 18), fill=C('#22262c')); d.point((22, 18), fill=C('#22262c'))
    elif k == 2:
        # the coffee port: a dhow at the quay and a merchant's warehouse, whitewashed and flat-roofed, its sacks at the door
        d.rectangle([14, 6, 28, 18], fill=C('#ece2c8'))
        d.rectangle([14, 5, 28, 6], fill=C('#d4c6a2'))
        for px_ in range(14, 29, 3):
            d.rectangle([px_, 3, px_ + 1, 4], fill=C('#ece2c8'))
        d.line([(14, 8), (28, 8)], fill=C('#c4ad84'))
        d.rectangle([19, 12, 23, 18], fill=C('#5a3a22'))
        d.point((19, 12), fill=C('#ece2c8')); d.point((23, 12), fill=C('#ece2c8'))
        d.rectangle([15, 10, 16, 12], fill=C('#3a3040')); d.rectangle([25, 10, 26, 12], fill=C('#3a3040'))
        d.polygon([(1, 16), (13, 16), (11, 20), (3, 20)], fill=C('#8a5630'))
        d.line([(1, 16), (13, 16)], fill=C('#c08850'))
        d.line([(7, 16), (7, 4)], fill=C('#5a3a22'))
        d.polygon([(7, 4), (12, 13), (7, 13)], fill=C('#f4ecd8'))
        for sx in (15, 19, 23):
            d.ellipse([sx, 18, sx + 4, 21], fill=C('#a07a4a'))
    elif k == 3:
        # the wadi: canyon walls and the road through them
        d.polygon([(0, 22), (3, 6), (8, 4), (11, 22)], fill=C('#b07a4a'))
        d.polygon([(19, 22), (22, 5), (27, 7), (30, 22)], fill=C('#9a6a40'))
        d.line([(4, 7), (8, 5)], fill=C('#d8a46c')); d.line([(22, 6), (26, 8)], fill=C('#d8a46c'))
        d.polygon([(11, 22), (13, 12), (17, 12), (19, 22)], fill=C('#ead9a8'))
        d.rectangle([12, 15, 17, 18], fill=C('#e8e4dc')); d.rectangle([13, 13, 15, 15], fill=C('#e8e4dc'))
        d.point((13, 19), fill=C('#22262c')); d.point((16, 19), fill=C('#22262c'))
        d.point((5, 20), fill=C('#5d7a32')); d.point((24, 19), fill=C('#5d7a32')); d.point((25, 20), fill=C('#5d7a32'))
    elif k == 4:
        # the terraces, step on green step, and a village of tower houses at the top
        for i, y in enumerate((19, 15, 11, 7)):
            d.rectangle([i * 2, y, 22 - i * 2, y + 3], fill=C('#86a246' if i % 2 == 0 else '#5f7c32'))
            d.line([(i * 2, y + 3), (22 - i * 2, y + 3)], fill=C('#6a5236'))
        for hx_, hh_ in ((20, 9), (25, 12)):
            d.rectangle([hx_, 18 - hh_, hx_ + 4, 22], fill=C('#c89a6c'))
            d.line([(hx_, 18 - hh_ + 3), (hx_ + 4, 18 - hh_ + 3)], fill=C('#f4f0e8'))
            d.point((hx_ + 2, 18 - hh_ + 5), fill=C('#3a3040'))
    elif k == 'islands':
        # the islands: a low island with a palm and a lighthouse, and a boat off its shore
        d.ellipse([2, 14, 22, 22], fill=C('#e2c68a'))
        d.ellipse([5, 15, 19, 20], fill=C('#c8a868'))
        d.rectangle([14, 4, 16, 16], fill=C('#f4f0e8')); d.rectangle([14, 8, 16, 9], fill=C('#d8261c')); d.rectangle([14, 12, 16, 13], fill=C('#d8261c'))
        d.rectangle([13, 2, 17, 4], fill=C('#3a3040')); d.point((15, 3), fill=C('#ffe066'))
        d.line([(7, 16), (8, 8)], fill=C('#8a6236'))
        d.line([(3, 8), (8, 7), (12, 9)], fill=C('#5d7a32')); d.line([(4, 6), (8, 7), (11, 5)], fill=C('#86a246'))
        d.polygon([(21, 19), (29, 19), (27, 22), (23, 22)], fill=C('#3c78c8')); d.line([(25, 19), (25, 13)], fill=C('#5a3a22'))
        d.polygon([(25, 13), (28, 18), (25, 18)], fill=C('#f4ecd8'))
    elif k == 'dam':
        # the old dam: a wall across the valley, its sluice shut, and not much behind it
        d.polygon([(2, 22), (5, 8), (25, 8), (28, 22)], fill=C('#b8b0a0'))
        d.polygon([(5, 8), (25, 8), (24, 11), (6, 11)], fill=C('#d8d0c0'))
        for xx_ in (9, 15, 21):
            d.line([(xx_, 12), (xx_ - 1, 21)], fill=C('#8a8478'))
        d.rectangle([13, 15, 17, 21], fill=C('#4a4640')); d.rectangle([14, 16, 16, 17], fill=C('#d8261c'))
        d.line([(5, 8), (25, 8)], fill=C('#f0ece4'))
        d.point((15, 22), fill=C('#3f8fc0')); d.point((14, 23), fill=C('#3f8fc0'))
    elif k == 'bridge':
        # the stone bridge: one arch across the gorge between two cliffs
        d.polygon([(0, 22), (0, 8), (8, 6), (10, 22)], fill=C('#9c7a56'))
        d.polygon([(20, 22), (22, 7), (30, 9), (30, 22)], fill=C('#8c6a4a'))
        d.rectangle([7, 7, 23, 10], fill=C('#c8b08a'))
        d.arc([9, 8, 21, 22], 180, 360, fill=C('#6a5236'))
        d.line([(7, 7), (23, 7)], fill=C('#e8d8b4'))
        for xx_ in (9, 13, 17, 21):
            d.point((xx_, 8), fill=C('#8a7050'))
        d.rectangle([24, 1, 28, 7], fill=C('#d8c8a8')); d.rectangle([25, 3, 26, 4], fill=C('#3a3040'))
    elif k == 'souq':
        # the souq: stalls under striped awnings, a pile of spice, and a tower house behind
        d.rectangle([19, 2, 26, 22], fill=C('#c08a62'))
        for yy_ in (6, 11, 16):
            d.line([(19, yy_), (26, yy_)], fill=C('#f4f0e8'))
        d.point((22, 8), fill=C('#3a3040')); d.point((22, 13), fill=C('#3a3040'))
        for sx_, col_ in ((1, '#d8261c'), (10, '#3c78c8')):
            d.rectangle([sx_, 12, sx_ + 9, 21], fill=C('#8a5a36'))
            for k2 in range(5):
                d.rectangle([sx_ + k2 * 2, 9, sx_ + k2 * 2 + 1, 12], fill=C(col_ if k2 % 2 == 0 else '#f4ecd8'))
        d.polygon([(3, 21), (5, 17), (7, 21)], fill=C('#e8a030')); d.polygon([(12, 21), (14, 18), (16, 21)], fill=C('#c84a20'))
    elif k == 'hodeidah':
        # the port: two gantry cranes over a quay of containers, and a ship alongside
        d.rectangle([0, 18, 29, 21], fill=C('#8a8478'))
        d.polygon([(1, 22), (27, 22), (25, 24), (3, 24)], fill=C('#3c4a5a'))
        for cx_ in (5, 17):
            d.line([(cx_, 18), (cx_, 4)], fill=C('#e8b030')); d.line([(cx_ + 5, 18), (cx_ + 5, 4)], fill=C('#e8b030'))
            d.line([(cx_ - 3, 4), (cx_ + 9, 4)], fill=C('#e8b030')); d.line([(cx_, 9), (cx_ + 5, 9)], fill=C('#c08a20'))
            d.line([(cx_ + 2, 5), (cx_ + 2, 11)], fill=C('#3a3040'))
        for bx_, col_ in ((1, '#c8402a'), (6, '#3c78c8'), (11, '#2f8a5a'), (16, '#e8b030'), (21, '#c8402a')):
            d.rectangle([bx_, 15, bx_ + 4, 17], fill=C(col_))
        d.rectangle([7, 12, 11, 14], fill=C('#3c78c8'))
    elif k == 'kawkaban':
        # the sky fortress: a sheer cliff with the walled town along its top
        d.polygon([(2, 23), (5, 9), (25, 8), (28, 23)], fill=C('#9a7452'))
        d.line([(6, 10), (8, 22)], fill=C('#7a5a3e')); d.line([(19, 10), (21, 22)], fill=C('#7a5a3e'))
        d.line([(5, 9), (25, 8)], fill=C('#c8a070'))
        for hx_, hh_ in ((7, 5), (12, 7), (17, 6), (21, 4)):
            d.rectangle([hx_, 8 - hh_, hx_ + 3, 8], fill=C('#d8b890'))
            d.line([(hx_, 8 - hh_ + 2), (hx_ + 3, 8 - hh_ + 2)], fill=C('#f4f0e8'))
        d.line([(14, 23), (13, 18), (16, 14)], fill=C('#e2c68a'))
    elif k == 'taiz':
        # the mountain city: houses up the slope, the castle on the crag above them
        d.polygon([(0, 23), (12, 6), (17, 4), (30, 23)], fill=C('#8c6a4a'))
        d.polygon([(12, 6), (17, 4), (21, 10), (14, 11)], fill=C('#b08a62'))
        d.rectangle([13, 1, 21, 6], fill=C('#d8c8a8'))
        for tx_ in (13, 16, 19):
            d.rectangle([tx_, 0, tx_ + 1, 1], fill=C('#d8c8a8'))
        d.point((17, 3), fill=C('#3a3040'))
        for hx_, hy_ in ((4, 18), (8, 15), (12, 17), (17, 15), (21, 18), (25, 20), (7, 20), (15, 20)):
            d.rectangle([hx_, hy_, hx_ + 3, hy_ + 3], fill=C('#efe6d4')); d.point((hx_ + 1, hy_ + 1), fill=C('#5a4a40'))
    elif k == 'ibb':
        # the green valleys: terraced slopes either side and a waterfall coming down between them
        d.polygon([(0, 23), (0, 6), (11, 10), (13, 23)], fill=C('#6f8a3c'))
        d.polygon([(30, 23), (30, 5), (18, 9), (16, 23)], fill=C('#5f7c32'))
        for yy_ in (9, 13, 17, 21):
            d.line([(0, yy_), (11, yy_ + 1)], fill=C('#8aa64a')); d.line([(18, yy_), (30, yy_ - 1)], fill=C('#86a246'))
        d.rectangle([13, 4, 16, 23], fill=C('#8fdce0'))
        d.line([(14, 4), (14, 23)], fill=C('#e8fbff'))
        d.ellipse([10, 20, 20, 24], fill=C('#4cb0d0'))
        d.line([(12, 21), (18, 21)], fill=C('#e8fbff'))
    elif k == 'dhamar':
        # the high plain: a straight road to the horizon, a black volcano cone, and the convoy's bus
        d.polygon([(0, 23), (0, 15), (30, 13), (30, 23)], fill=C('#c49a62'))
        d.polygon([(11, 23), (14, 14), (16, 14), (19, 23)], fill=C('#5a5048'))
        d.line([(15, 15), (15, 22)], fill=C('#e8e0c8'))
        d.polygon([(19, 13), (24, 5), (27, 5), (30, 13)], fill=C('#3a3236'))
        d.line([(24, 5), (27, 5)], fill=C('#6a5a5a'))
        d.rectangle([2, 14, 10, 19], fill=C('#e8b030')); d.rectangle([3, 15, 9, 16], fill=C('#3a3040'))
        d.point((4, 20), fill=C('#22262c')); d.point((8, 20), fill=C('#22262c'))
        d.rectangle([3, 12, 9, 13], fill=C('#8a5a36'))
    elif k == 'sands':
        # the sands: something half-buried that should not be there, and a crate with a question on it
        d.polygon([(0, 22), (8, 17), (18, 18), (30, 22)], fill=C('#e4ad62'))
        d.pieslice([5, 6, 25, 30], 180, 360, fill=C('#7c8478'))
        d.arc([5, 6, 25, 30], 180, 360, fill=C('#a8b0a4'))
        d.rectangle([12, 12, 18, 18], fill=C('#2a2c30'))
        d.line([(22, 8), (22, 2)], fill=C('#8a8f96')); d.point((22, 1), fill=C('#ff5a3c'))
        d.polygon([(0, 22), (8, 18), (18, 19), (30, 22)], fill=C('#e4ad62'))
    elif k == 5:
        # Bab al-Yemen: the gate, its towers and the tall houses behind with their white trim
        d.rectangle([2, 6, 8, 22], fill=C('#b07c58')); d.rectangle([22, 6, 28, 22], fill=C('#b07c58'))
        d.rectangle([8, 9, 22, 22], fill=C('#c08a62'))
        d.rectangle([12, 13, 18, 22], fill=C('#2a1c18'))
        d.ellipse([12, 10, 18, 16], fill=C('#2a1c18'))
        for tx in (2, 22):
            for k2 in range(3):
                d.rectangle([tx + k2 * 2, 4, tx + k2 * 2, 5], fill=C('#b07c58'))
            d.line([(tx, 11), (tx + 6, 11)], fill=C('#f4f0e8'))
            d.line([(tx, 16), (tx + 6, 16)], fill=C('#f4f0e8'))
        d.line([(8, 9), (22, 9)], fill=C('#f4f0e8'))
        d.point((5, 13), fill=C('#3a3040')); d.point((25, 13), fill=C('#3a3040'))
    return outline(im, '#10101c')


def dimmed(im):
    """A place whose road is not open yet: there, but greyed and blue in the shade."""
    a = np.array(im).astype(float)
    solid = a[..., 3] > 0
    lum = (a[..., 0] * 0.3 + a[..., 1] * 0.55 + a[..., 2] * 0.15)[..., None]
    rgb = lum * 0.72 + np.array([60.0, 66.0, 112.0]) * 0.28
    out = np.zeros_like(a)
    out[..., :3] = rgb
    out[..., 3] = np.where(solid, 255, 0)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')


def signpost():
    """A fork in the road: a post with two boards pointing different ways."""
    im = Image.new('RGBA', (17, 19), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([7, 2, 8, 18], fill=hexc('#7a4a22'))
    d.polygon([(0, 4), (3, 1), (12, 1), (12, 7), (3, 7)], fill=hexc('#d8a058'))
    d.line([(3, 7), (12, 7)], fill=hexc('#a8743a'))
    d.polygon([(4, 9), (13, 9), (16, 12), (13, 15), (4, 15)], fill=hexc('#d8a058'))
    d.line([(4, 15), (13, 15)], fill=hexc('#a8743a'))
    for y_ in (4, 12):
        d.line([(5 if y_ == 4 else 6, y_), (10 if y_ == 4 else 11, y_)], fill=hexc('#8a5a2a'))
    d.rectangle([5, 17, 10, 18], fill=hexc('#5a3a1a'))
    return outline(im, '#10101c')


def shadowed(im):
    """Locked: a dark blue-grey cut-out with a dim edge, so you can see there is something there and not what."""
    a = np.array(im)
    solid = a[..., 3] > 0
    inner = solid & ~ring_of(~solid, diag=False)
    out = np.zeros_like(a)
    out[solid] = hexc('#4a5288')
    out[inner] = hexc('#2a3060')
    return Image.fromarray(out, 'RGBA')


SCORPION = [          # the Scorpion's mark, seen from above: claws open, tail curled round
    'x.x.....x.x',
    'xYx.....xYx',
    '.xYx...xYx.',
    '..xYxxxYx..',
    '...xYYYx...',
    '.xxYYYYYxx.',
    'x.xYYYYYx.x',
    '.xxYYYYYxx.',
    'x..xYYYx..x',
    '....xYx....',
    '....xYx....',
    '...xYx.....',
    '..xYYx.....',
    '..xxx......',
]


def compass():
    import px
    im = Image.new('RGBA', (21, 25), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, cy = 10, 14
    d.ellipse([c - 7, cy - 7, c + 7, cy + 7], outline=hexc('#e8ecff'))
    d.polygon([(c, cy - 9), (c + 2, cy), (c - 2, cy)], fill=hexc('#ff5a3c'))
    d.polygon([(c, cy + 9), (c + 2, cy), (c - 2, cy)], fill=hexc('#e8ecff'))
    d.polygon([(c - 9, cy), (c, cy - 2), (c, cy + 2)], fill=hexc('#aab1d8'))
    d.polygon([(c + 9, cy), (c, cy - 2), (c, cy + 2)], fill=hexc('#aab1d8'))
    n = px.text_img('N', px.FONT_S, '#e8ecff')
    im.alpha_composite(n, (c - n.width // 2, 0))
    return outline(im, '#10142c')


def cloud(w, h, seed):
    rs = np.random.RandomState(seed)
    yy, xx = np.mgrid[0:h, 0:w]
    m = np.zeros((h, w), bool)
    for _ in range(7):
        cx_, cy_ = rs.uniform(w * 0.2, w * 0.8), rs.uniform(h * 0.45, h * 0.75)
        rx, ry = rs.uniform(w * 0.14, w * 0.26), rs.uniform(h * 0.25, h * 0.42)
        m |= ((xx - cx_) / rx) ** 2 + ((yy - cy_) / ry) ** 2 <= 1
    a = np.zeros((h, w, 4), np.uint8)
    a[m] = hexc('#ffffff', 235)
    under = m & ~np.roll(m, -2, axis=0)
    a[under] = hexc('#cfd8ec', 235)
    a[ring_of(m, diag=False)] = hexc('#aab4d0', 140)
    return Image.fromarray(a, 'RGBA'), Image.fromarray(np.where(m[..., None], np.array(hexc('#10142c', 60), np.uint8), np.zeros(4, np.uint8)).astype(np.uint8), 'RGBA')


COFFEE_RING = None


def coffee_ring():
    yy, xx = np.mgrid[0:13, 0:15]
    r = np.hypot((xx - 7) / 7.0, (yy - 6) / 6.0)
    a = np.zeros((13, 15, 4), np.uint8)
    ringm = (r > 0.78) & (r <= 1.0)
    a[ringm] = hexc('#6a3c1c', 120)
    a[ringm & (xx < 6) & (yy > 6)] = hexc('#6a3c1c', 170)
    a[(r <= 0.78) & (((xx + yy) % 5) == 0)] = hexc('#6a3c1c', 40)
    return Image.fromarray(a, 'RGBA')


MARKER = ['x...x', 'xYYYx', '.xYx.', '..x..']
YAZEED_PIECE = [          # Yazeed as a piece on the map: shemagh, beard, blue shirt, jambiya, white futa
    '....xxx....',
    '...xTTTx...',
    '..xTtTTTx..',
    '..xtTTTtx..',
    '..xSSSSSx..',
    '..xSkSkSx..',
    '..xSSSSSx..',
    '...xbbbx...',
    '..xBBBBBx..',
    '.xSBBGBBSx.',
    '.xSBBBBBSx.',
    '..xWWWWWx..',
    '..xWwxwWx..',
    '..xFx.xFx..',
    '...x...x...',
]
YAZEED_PAL = {'x': '#10101c', 'T': '#e8f0fa', 't': '#8ab4e0', 'S': '#d09060', 'k': '#10101c', 'b': '#3a2a20', 'B': '#3c78c8', 'G': '#ffc22e',
            'W': '#f0ece0', 'w': '#c8c0b0', 'F': '#5a3a22'}
DHOW = ['....x....', '....xW...', '....xWW..', '....xWWW.', '....xWWWW', 'x...x....', 'xBBBBBBBx', '.xBBBBBx.', '..xxxxx..']


def sea_points(n=64, seed=5):
    """Places out at sea where the sun can catch a wave: the map's open water, away from the coast."""
    arabia, africa = land_masks()
    d = ndimage.distance_transform_edt(~(arabia | africa))
    ys, xs = np.nonzero(d > 4)
    rs = np.random.RandomState(seed)
    k = rs.choice(len(xs), n, replace=False)
    return [[int(xs[i]), int(ys[i])] for i in k]


def sprites():
    """Everything for the menus that goes into the sprite sheet: name -> (image, ax, ay)."""
    out = {}
    lg = logo()
    out['menu_logo'] = (lg, lg.width // 2, 0)
    la = logo_ar()
    out['menu_logo_ar'] = (la, la.width // 2, 0)
    for n in '123456?':
        for st in ('open', 'clear', 'lock'):
            out['menu_badge%s_%s' % ('q' if n == '?' else n, st)] = (badge(n, st), 7, 7)
    out['menu_padlock'] = (sprite(PADLOCK, {'x': '#10101c', 'Y': '#ffc22e'}), 2, 7)
    out['menu_tick'] = (outline(sprite(TICK, {'x': '#10101c', 'G': '#d4f8b8'}), '#10101c'), 4, 7)
    sc = stamp_clear()
    out['menu_stamp'] = (sc, sc.width // 2, sc.height // 2)
    for k in NODES:
        lm = landmark(k)
        out['menu_land_%s' % k] = (lm, lm.width // 2, lm.height - 1)
        out['menu_land_%s_x' % k] = (dimmed(lm), lm.width // 2, lm.height - 1)
    sg = signpost()
    out['menu_sign'] = (sg, sg.width // 2, sg.height - 1)
    sp = outline(sprite(SCORPION, {'x': '#10101c', 'Y': '#ffd23a'}), '#10101c')
    out['menu_scorpion'] = (sp, sp.width // 2, sp.height // 2)
    cp = compass()
    out['menu_compass'] = (cp, cp.width // 2, cp.height // 2)
    for i, (cw, ch, sd) in enumerate(((40, 16, 3), (28, 12, 5), (52, 18, 8))):
        c, s = cloud(cw, ch, sd)
        out['menu_cloud%d' % i] = (c, cw // 2, ch // 2)
        out['menu_cshadow%d' % i] = (s, cw // 2, ch // 2)
    out['menu_coffee'] = (coffee_ring(), 7, 6)
    out['menu_marker'] = (sprite(MARKER, {'x': '#10101c', 'Y': '#ffc22e'}), 2, 3)
    out['menu_yazeed'] = (sprite(YAZEED_PIECE, YAZEED_PAL), 5, 14)
    out['menu_dhow'] = (sprite(DHOW, {'x': '#3a2414', 'W': '#f4ecd8', 'B': '#8a5630'}), 4, 8)
    return out


if __name__ == '__main__':
    pv = os.path.join(HERE, '..', 'art', 'preview')
    os.makedirs(pv, exist_ok=True)
    lg = logo()
    bg = Image.new('RGBA', (lg.width + 20, lg.height + 20), hexc('#5aa8d8'))
    bg.alpha_composite(lg, (10, 10))
    bg.resize((bg.width * 3, bg.height * 3), Image.NEAREST).save(os.path.join(pv, 'logo.png'))
    m, info = campaign_map()
    m.save(os.path.join(pv, 'map.png'))
    m.resize((MW * 2, MH * 2), Image.NEAREST).save(os.path.join(pv, 'map2x.png'))
    sp = sprites()
    W_ = sum(im.width + 4 for im, _, _ in sp.values() if im.width < 100)
    sheet = Image.new('RGBA', (W_, 40), hexc('#d9b97a'))
    x = 0
    for n, (im, ax, ay) in sp.items():
        if im.width >= 100:
            continue
        sheet.alpha_composite(im, (x, 2))
        x += im.width + 4
    sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(os.path.join(pv, 'menu_sprites.png'))
    print('logo', lg.size, 'map', m.size, 'sprites', len(sp))
