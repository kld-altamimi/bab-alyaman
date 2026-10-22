# zabid_sprites.py - the sprites The Souq adds: sacks of spice and the clouds they burst into, the shopkeepers tied
# behind their counters, the Dhanabs' barricades (whole, knocked about, nearly gone, and the bits that fly off), a wall
# of sandbags, and the Great Scale in parts: its post, its brass beam (turned by the game; and the two halves it breaks
# into), its pans (the outside of one, and the far side of its rim), the Weighmaster with his brass blunderbuss and his
# iron weights, and his porters, scarves over their noses, with sacks of spice on their shoulders.
# Built the same way as sprites.py and mocha_sprites.py: the cast's parts, outlined; machine parts painted as tone
# fields and outlined. Every frame is (image, ax, ay): the anchor is the point between the feet, on the ground, unless
# it says otherwise.
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock'
sys.path.insert(0, MOCK)
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image
import ms3
from ms3 import at, weapon, pal, PARTS, WRAPS, FACES, LEAN, HEAVY, SLIM, INK2
import sprites as SP
from px import sprite, outline, silhouette
import props as P
from paint import Layer, Tone, ramp, rng, noise
import stage_mocha as SM
import stage_zabid as SZ
import mocha_sprites as MS

CHILLI, TURMERIC, PAPRIKA = SZ.CHILLI, SZ.TURMERIC, SZ.PAPRIKA
SPICE = {'red': CHILLI, 'yel': TURMERIC, 'org': PAPRIKA}
CLOUD = {'red': ramp(['#5a1408', '#8a2410', '#b83c1c', '#d8603a', '#ec8c60', '#f8b48c', '#fcd8c0'], 12),
         'yel': ramp(['#6a4a0c', '#987018', '#c09a30', '#dcbc54', '#ecd480', '#f8e8b0', '#fff6dc'], 12),
         'org': ramp(['#6a2a08', '#9a4410', '#c86420', '#e48a3c', '#f2ae68', '#f8cc98', '#fde4c8'], 12)}
BRASS = ramp(['#1e1204', '#42280a', '#6e4a12', '#9a6c1c', '#c4922c', '#e2b848', '#f6dc84', '#fff4c4'], 16)


def _img(T, rmp, dither=0.3, outline_=False):
    L = T.layer(rmp, dither=dither)
    if outline_:
        L = P.outlined(L)
    im = L.image()
    bb = im.getbbox()
    return im.crop(bb), bb


def _stack(layers, W, H, outline_=True):
    """[(Tone, ramp, dither)] painted on one W x H canvas, outlined as sprites are: (image, x offset, y offset) of
    the crop."""
    L = Layer(W, H)
    for T, rmp, dth in layers:
        L.paste(T.layer(rmp, dither=dth))
    if outline_:
        L = P.outlined(L)
    im = L.image()
    bb = im.getbbox()
    return im.crop(bb), bb[0] - (1 if outline_ else 0), bb[1] - (1 if outline_ else 0)


# ------------------------------------------------------------------ sacks of spice, and the clouds out of them
def spice_sack(col='red'):
    """A sack of spice standing open on the ground, its mouth rolled down and the heap of spice showing: one shot and
    it goes up in a cloud."""
    W, H = 18, 20
    T = Tone(W, H)
    S = Tone(W, H)
    for y in range(7, H):
        v = (y - 7) / float(H - 8)
        half = 5 + int(1.5 * np.sin(v * np.pi)) - (y == H - 1)
        for x in range(9 - half, 9 + half + 1):
            u = (x - (9 - half)) / float(2 * half)
            t = 0.74 - 0.36 * u - 0.12 * v + 0.06 * ((x * 3 + y * 5) % 4 == 0)
            if y in (7, 8):
                t = 0.86 - 0.20 * u                           # the rolled mouth
            T.px(x, y, t)
    for x in range(5, 14):                                     # the heap in the mouth
        u = (x - 9) / 4.5
        hh = int(4 * np.sqrt(max(0, 1 - u * u)))
        for y in range(7 - hh, 8):
            S.px(x, y, 0.80 - 0.34 * ((x - 5) / 8.0) + 0.06 * (y == 7 - hh))
    L = T.layer(SM.SACK, dither=0.3)
    L.paste(S.layer(SPICE[col], dither=0.3))
    im = P.outlined(L).image()
    bb = im.getbbox()
    im = im.crop(bb)
    return im, im.width // 2, im.height - 1


def cloud_puff(col='red', k=0, r=11):
    """One billow of a cloud of spice: lit from the upper left, its edges thinned to a dither so the clouds read as
    dust in the air (the game heaps several of them into a cloud and fades it out)."""
    W_ = H_ = 2 * r + 6
    rr = rng(300 + k * 7 + r)
    blobs = []
    for i in range(6):
        a = i / 6.0 * 2 * np.pi + rr.uniform(-0.4, 0.4)
        d = r * rr.uniform(0.25, 0.55)
        blobs.append((W_ / 2.0 + d * np.cos(a), H_ / 2.0 + d * np.sin(a) * 0.8, r * rr.uniform(0.45, 0.65)))
    blobs.append((W_ / 2.0, H_ / 2.0, r * 0.7))
    Z = MS._puff_field(W_, H_, blobs)
    from scipy import ndimage as ndi
    g = np.gradient(ndi.gaussian_filter(Z, 0.8))
    lit = -g[1] * 0.7 - g[0] * 0.7
    yy, xx = np.mgrid[0:H_, 0:W_]
    t = 0.56 + 0.30 * np.clip(lit, -1, 1) + 0.05 * (noise((H_, W_), 400 + k, 3, 3) - 0.5)
    m = Z > 0.5
    rim = m & (Z < 2.6)
    m &= ~(rim & ((xx + yy) % 2 == 0))
    T = Tone(W_, H_)
    T.mask(m, 0)
    T.t = np.where(m, np.clip(t, 0, 1), T.t)
    im = T.layer(CLOUD[col], dither=0.4).image()
    return im, W_ // 2, H_ // 2


def sneeze_spray():
    """What comes out of a man who sneezes: a little burst of spray."""
    rows = ['....o.', '.o..oo', 'oOoO..', '.o..oo', '....o.']
    im = sprite(rows, {'o': '#d8e8f0', 'O': '#ffffff'})
    return im, 0, 2


# ------------------------------------------------------------------ the shopkeepers, and their counters
SHOPS = {
    # top, lower, wrap, skin, face, wrap part
    'shop_tea': ('sand', 'sand', 'redchk', 'skin2', 'elder', 'cap'),
    'shop_spice': ('ochre', 'cream', 'white', 'skin1', 'worried', 'check'),
    'shop_cloth': ('teal', 'navy', 'blue', 'skin3', 'youth', 'kufiya'),
}


def _tint(name, to):
    """A part with its white cloth (H I J) put into another of the palette's ramps (abc: the top, fgh: the lower)."""
    rows = PARTS[name] if isinstance(name, str) else name
    return [r.translate(str.maketrans('HIJ', to)) for r in rows]


def shopkeeper(look='shop_tea', act='tied', pose='stand'):
    """A stallholder the Dhanabs have tied to the post of his own stall (as the detained elder is tied): a thobe in his
    own colours, a cap; freed, he salutes and runs for it. Played straight."""
    top, lower, wrap, skin, face, wp = SHOPS[look]
    p = pal(top, lower, wrap, skin)
    p['9'] = '#b8301c'                                   # (the pattern on a shawl)
    B = SLIM
    L = []
    dy = -1 if pose == 'pass' else 0
    if act == 'tied':
        L.append(at('post', (2, -10), p))
    L += [at('bare_feet_s', B.legs, p, 1 if pose == 'pass' else 0, 0), at(_tint('thobe_s', 'fgh'), B.futa, p, 0, dy),
          at(_tint('thobe_top_s', 'abc'), B.torso, p, 0, dy)]
    if act == 'tied':
        L += [at('rope_s', (4, 10), p)]
    L += [at(FACES[face], B.face, p, 0, dy), at(WRAPS[wp], B.wrap, p, 0, (1 if wp == 'cap' else 0) + dy, ink=INK2)]
    if act == 'freed':
        L += [at(_tint('arm_salute_s', 'abc'), (12, 2), p)]
    return L, B.foot, None


def counter(goods='tea'):
    """The front of a stall's counter, drawn in front of the man tied behind it: planks, a cloth hung over the front,
    and what he sells on top."""
    W, H = 40, 30
    T = Tone(W, H)
    C = Tone(W, H)
    x0, x1, top = 4, 36, 14
    for y in range(top, H - 1):
        for x in range(x0, x1):
            t = 0.60 - 0.18 * ((x - x0) / float(x1 - x0)) - 0.08 * ((y - top) / 14.0)
            if y == top:
                t = 0.90
            if (y - top) % 5 == 4:
                t -= 0.14
            T.px(x, y, t)
    for x in range(x0 + 2, x1 - 2):
        for y in range(top + 2, top + 9):
            C.px(x, y, 0.62 - 0.26 * (y - top - 2) / 7.0 + 0.12 * (((x - x0) // 4) % 2))
    rmp = {'tea': SZ.CLOTH_R, 'spice': SZ.CLOTH_G, 'cloth': SZ.CLOTH_B}[goods]
    L = T.layer(SM.TEAK, dither=0.3)
    L.paste(C.layer(rmp, dither=0.3))
    G = Layer(W, H)
    if goods == 'tea':
        K = Tone(W, H)
        for j, half in enumerate([1, 2, 3, 3, 3, 2]):
            for i in range(-half, half + 1):
                K.px(26 + i, top - 7 + j, 0.80 - 0.10 * (i + half) / max(1, half))
        for k_ in range(3):
            K.px(22 - k_, top - 5 - k_, 0.70)
        G.paste(K.layer(SM.COPPER, dither=0.2))
        for gx in (8, 12, 16):
            for y in range(top - 3, top):
                G.rgb[y, gx:gx + 2] = (196, 228, 210) if y == top - 3 else (150, 60, 30)
                G.a[y, gx:gx + 2] = True
    elif goods == 'spice':
        for k_, (cx, rmp2) in enumerate(((10, CHILLI), (20, TURMERIC), (30, PAPRIKA))):
            S = Tone(W, H)
            for j in range(6):
                half = int(4 * (j + 1) / 6.0)
                for i in range(-half, half + 1):
                    S.px(cx + i, top - 6 + j, 0.80 - 0.34 * ((i + half) / (2.0 * half + 1)))
            G.paste(S.layer(rmp2, dither=0.3))
    else:
        for k_, (rmp2, y0) in enumerate(((SZ.CLOTH_R, top - 4), (SZ.CLOTH_Y, top - 8), (SZ.CLOTH_B, top - 4))):
            S = Tone(W, H)
            xa = 7 + (k_ % 2) * 10 + (k_ // 2) * 12
            for y in range(y0, y0 + 4):
                for x in range(xa, xa + 14):
                    S.px(x, y, 0.74 - 0.30 * ((y - y0) / 4.0) + 0.08 * ((x - xa) % 5 == 0))
            G.paste(S.layer(rmp2, dither=0.2))
    L.paste(G)
    im = P.outlined(L).image()
    bb = im.getbbox()
    im = im.crop(bb)
    return im, im.width // 2, im.height - 1


# ------------------------------------------------------------------ barricades
def barricade(state=0, seed=1):
    """The Dhanabs' barricade, piled up out of whatever the market had: an upturned hand cart, crates, sandbags, a
    blue door off its hinges, a sheet of corrugated iron, a tyre on top. state 1: knocked about, a hole through it;
    state 2: nearly gone. Anchored at the middle of its foot."""
    W, H = 60, 44
    gx = 8                                    # the pile's left foot on this canvas
    base = H - 2
    r = rng(seed)
    Bg = Tone(W, H)                           # sandbags
    Wd = Tone(W, H)                           # wood
    Tn = Tone(W, H)                           # tin
    Ty = Tone(W, H)                           # tyre
    Dr = Tone(W, H)                           # the blue door
    lose = {0: 0.0, 1: 0.18, 2: 0.55}[state]
    shrink = {0: 0, 1: 2, 2: 13}[state]

    def keep(x, y):
        if state == 0:
            return True
        hole = state >= 1 and (x - (gx + 22)) ** 2 + ((y - (base - 16)) * 1.4) ** 2 < 30
        return not hole and r.random() > lose * 0.35
    # sandbags along the foot, two rows
    for row in range(2):
        y0 = base - 6 - row * 5
        off = 0 if row == 0 else 6
        for c in range(4 - row):
            sx = gx + off + c * 12
            for j in range(6):
                inset = 2 if j in (0, 5) else (1 if j in (1, 4) else 0)
                for i in range(inset, 12 - inset):
                    if keep(sx + i, y0 + j):
                        Bg.px(sx + i, y0 + j, 0.80 - 0.44 * (j / 5.0) - 0.20 * (i / 11.0) + 0.10 * (j < 2))
    # an upturned hand cart, its wheel in the air, on the right
    cx_, cy_ = gx + 38, base - 18
    for x in range(gx + 26, gx + 50):
        for y in range(cy_, cy_ + 9):
            if keep(x, y):
                Wd.px(x, y, 0.66 - 0.18 * ((y - cy_) / 8.0) + 0.10 * ((x % 6) == 0) - 0.10 * (y == cy_ + 8))
    for a in range(0, 360, 10):
        for rr in (7, 8):
            Wd.px(cx_ + 4 + rr * np.cos(np.radians(a)), cy_ - 7 + rr * np.sin(np.radians(a)), 0.34 if rr == 8 else 0.52)
    for a in range(0, 360, 45):
        Wd.line([(cx_ + 4, cy_ - 7), (cx_ + 4 + 7 * np.cos(np.radians(a)), cy_ - 7 + 7 * np.sin(np.radians(a)))], 0.46)
    # crates in the middle
    for (bx, by, bw, bh) in ((gx + 4, base - 22, 16, 12), (gx + 14, base - 32 + shrink, 14, 11)):
        if state == 2 and by < base - 24:
            continue
        for x in range(bx, bx + bw):
            for y in range(by, by + bh):
                t = 0.60 - 0.14 * ((x - bx) / float(bw)) - 0.06 * ((y - by) / float(bh))
                if y == by:
                    t = 0.88
                if (y - by) % 4 == 3:
                    t -= 0.14
                if x in (bx, bx + bw - 1):
                    t -= 0.10
                if keep(x, y):
                    Wd.px(x, y, t)
    # the blue door, slanted across the front
    if state < 2:
        for k in range(30):
            for w_ in range(7):
                x = gx + 2 + k * 0.9 + w_ * 0.5
                y = base - 4 - k * 0.85 + w_ * 0.9
                if keep(int(x), int(y)):
                    Dr.px(x, y, 0.56 - 0.20 * (w_ > 4) + 0.12 * (k % 8 == 0))
    # a sheet of corrugated iron leaning against it, and a tyre on top
    for k in range(26 - shrink):
        for w_ in range(10):
            x = gx + 30 + w_ - k * 0.25
            y = base - 6 - k
            if keep(int(x), int(y)):
                Tn.px(x, y, 0.62 + 0.14 * ((w_ % 3) == 0) - 0.20 * (w_ > 7))
    if state == 0:
        for x in range(gx + 16, gx + 34):
            u = (x - (gx + 25)) / 9.0
            for j in range(6):
                Ty.px(x, base - 38 + j, 0.30 + 0.24 * (j == 0) - 0.10 * (abs(u) > 0.8) + 0.12 * ((x + j) % 3 == 0 and 0 < j < 5))
    L = Layer(W, H)
    for T, rmp in ((Bg, P.BURLAP), (Wd, SM.TEAK), (Dr, SZ.BLUEWOOD), (Tn, SZ.TIN), (Ty, P.TYRE)):
        L.paste(T.layer(rmp, dither=0.3))
    im = P.outlined(L).image()
    # anchor: the middle of the pile's foot (the game puts the prop's x there)
    return im, gx + 23 + 1, base + 1


def barricade_bits():
    """What flies off a barricade when it goes: a plank, a tyre, a sheet of tin, half a crate."""
    out = {}
    T = Tone(20, 6)
    T.rect(1, 1, 18, 3, 0.62)
    T.rect(1, 1, 18, 1, 0.86)
    im, _ = _img(T, SM.TEAK, outline_=True)
    out['barr_p0'] = (im, im.width // 2, im.height // 2)
    T = Tone(16, 10)
    for x in range(1, 15):
        for j in range(1, 8):
            T.px(x, j, 0.30 + 0.24 * (j == 1) + 0.12 * ((x + j) % 3 == 0))
    im, _ = _img(T, P.TYRE, outline_=True)
    out['barr_p1'] = (im, im.width // 2, im.height // 2)
    T = Tone(14, 16)
    for y in range(1, 15):
        for x in range(1, 12):
            T.px(x, y, 0.62 + 0.14 * ((x % 3) == 0))
    im, _ = _img(T, SZ.TIN, outline_=True)
    out['barr_p2'] = (im, im.width // 2, im.height // 2)
    T = Tone(12, 10)
    for x in range(1, 11):
        for y in range(1, 9):
            T.px(x, y, 0.60 - 0.04 * y + (0.26 if y == 1 else 0))
    im, _ = _img(T, SM.TEAK, outline_=True)
    out['barr_p3'] = (im, im.width // 2, im.height // 2)
    return out


def zbags():
    """A low wall of sandbags at the checkpoint: a man can hide behind it (it is drawn in front of him)."""
    sb, f = P.sandbags(cols=4, rows=3, seed=21)
    im = P.outlined(sb).image()
    bb = im.getbbox()
    im = im.crop(bb)
    return im, im.width // 2, im.height - 1


def pick_chilli():
    """Dried chillies out of the Weighmaster's burst sacks when his scale breaks: worth picking up (points)."""
    rows = ['..G..', '.xRx.', 'xRrRx', 'xRRRx', '.xRx.', '..x..']
    im = sprite(rows, {'x': '#2a0604', 'R': '#c8301a', 'r': '#f87a4c', 'G': '#4a6a1c'})
    return im, 2, 5


def red_puff(k=0):
    """The little puff where a chilli comes down."""
    T = Tone(12, 9)
    rr = rng(500 + k)
    for i in range(12):
        x, y = rr.uniform(2, 10), rr.uniform(2, 7)
        T.px(x, y, rr.uniform(0.5, 0.9))
        T.px(x + 1, y, rr.uniform(0.4, 0.7))
    im = T.layer(CLOUD['red'], dither=0.3).image()
    return im, 6, 8


# ------------------------------------------------------------------ the scarf over a nose, against the chilli
BAND = ['.kkkkkkk', 'kllllll.', 'kl9l9ll.', '.kl9ll..', '..kll...']


def _shear(im, ax, ay, k):
    """Lean a figure forward: each row shifted along by k for each pixel above the feet (the feet stay put)."""
    if not k:
        return im, ax, ay
    W, H = im.size
    extra = int(np.ceil(abs(k) * H)) + 1
    out = Image.new('RGBA', (W + extra, H), (0, 0, 0, 0))
    src = np.asarray(im)
    dst = np.zeros((H, W + extra, 4), dtype=np.uint8)
    for y in range(H):
        s = int(round((ay - y) * k))
        if s < 0:
            continue
        dst[y, s:s + W] = np.where(src[y][:, 3:4] > 0, src[y], dst[y, s:s + W])
    out = Image.fromarray(dst, 'RGBA')
    bb = out.getbbox()
    return out.crop(bb), ax - bb[0], ay - bb[1]


# ------------------------------------------------------------------ the scale itself
# Game coordinates: the beam turns about the top of the post (the pivot); its two ends are ARM either side of it; each
# pan hangs CHAIN below its end (to the pan's floor). A pan is PAN_HW either side of its middle, its rim RIM above its
# floor and its bottom BOTTOM below it (scale.js has the same numbers).
ARM, CHAIN, PAN_HW, RIM, BOTTOM = 64, 88, 24, 6, 8
PIVOT_Y, FLOOR_Y = 64, 184
CHAINC = ['#241e1a', '#4c4238', '#7a6c5a', '#a89880']          # the chains' iron, dark to light


def gs_post():
    """The scale's post: a squared post of old dark wood on a stone foot, bound with brass, and at its top the brass
    yoke the beam's pin turns in. Anchored on the floor under it."""
    top = PIVOT_Y - 9
    W, H = 28, FLOOR_Y - top + 1
    cx = 14
    T = Tone(W, H)                 # the wood
    K = Tone(W, H)                 # the brass
    S = Tone(W, H)                 # the stone foot
    fy = H - 1                     # the floor's row
    py = PIVOT_Y - top             # the pin's row
    for y in range(py + 6, fy - 9):
        for x in range(cx - 4, cx + 4):
            u = (x - (cx - 4)) / 7.0
            t = 0.62 + 0.18 * (u < 0.3) - 0.30 * (u > 0.72) + 0.05 * (((y * 7 + x * 3) % 11) == 0) - 0.06 * ((y // 9) % 2 == 0 and x == cx)
            T.px(x, y, t)
    for by in (py + 12, py + 44, py + 78, fy - 14):                # brass bands round it
        for y in (by, by + 1):
            for x in range(cx - 5, cx + 5):
                K.px(x, y, 0.86 - 0.40 * ((x - cx + 5) / 9.0) - 0.20 * (y == by + 1))
    # the yoke: two cheeks rising either side of the pin, a cross-piece under them
    for y in range(0, py + 7):
        for x in list(range(cx - 7, cx - 4)) + list(range(cx + 4, cx + 7)):
            K.px(x, y, 0.78 - 0.34 * (x > cx) + 0.10 * (y < 2))
    for y in range(py + 4, py + 7):
        for x in range(cx - 7, cx + 7):
            K.px(x, y, 0.70 - 0.30 * ((x - cx + 7) / 13.0) - 0.12 * (y == py + 6))
    # the stone foot, two steps
    for y in range(fy - 9, fy + 1):
        hw = 7 if y < fy - 4 else 10
        for x in range(cx - hw, cx + hw):
            S.px(x, y, 0.80 - 0.34 * ((x - cx + hw) / (2.0 * hw)) - 0.10 * (y in (fy - 9, fy - 4)) + 0.08 * (y in (fy - 8, fy - 3)))
    im, ox, oy = _stack([(S, SZ.LIME, 0.3), (T, SM.TEAK, 0.3), (K, BRASS, 0.2)], W, H)
    return im, cx - ox, fy - oy


def gs_beam(half=None):
    """The beam: brass, thickest over the pin and drawn out to a knob at each end, the pointer standing up from its
    middle, a ring under each end for the chains. Anchored on the pin (the game turns it there). half: 'l' or 'r', one
    of the two halves it breaks into, anchored where it broke."""
    W, H = 2 * ARM + 9, 26
    cx, cy = ARM + 4, 17
    T = Tone(W, H)
    K = Tone(W, H)                 # the pointer's iron
    for x in range(cx - ARM - 2, cx + ARM + 3):
        d = abs(x - cx) / float(ARM)
        th = 3.4 - 1.7 * min(1, d)
        for y in range(int(round(cy - th)), int(round(cy + th)) + 1):
            v = (y - (cy - th)) / (2 * th)
            t = 0.50 + 0.42 * np.exp(-((v - 0.28) / 0.22) ** 2) - 0.14 * (v > 0.8)
            T.px(x, y, t)
    for sx in (-1, 1):                                    # the knobs, and a ring under each end
        ex = cx + sx * (ARM + 1)
        for a in range(0, 360, 15):
            for r in (1, 2, 3):
                T.px(ex + sx + r * np.cos(np.radians(a)), cy + r * np.sin(np.radians(a)), 0.86 - 0.14 * r - 0.20 * (np.sin(np.radians(a)) > 0.4))
        rx = cx + sx * ARM
        for a in range(0, 360, 20):
            T.px(rx + 1.6 * np.cos(np.radians(a)), cy + 5 + 1.8 * np.sin(np.radians(a)), 0.62 - 0.22 * (np.cos(np.radians(a)) * -sx > 0.3))
    for a in range(0, 360, 6):                             # the boss over the pin
        for r in range(0, 6):
            T.px(cx + r * np.cos(np.radians(a)), cy + r * np.sin(np.radians(a)), 0.90 - 0.08 * r - 0.22 * (np.sin(np.radians(a)) * r > 2.2) - 0.16 * (np.cos(np.radians(a)) * r > 3))
    T.rect(cx - 1, cy - 1, cx, cy, 0.18)                    # the pin
    for y in range(1, cy - 5):                              # the pointer
        w = 1 if y < 6 else 2
        for x in range(cx - (w > 1), cx + 1):
            K.px(x, y, 0.70 - 0.30 * (x > cx - 1) + 0.12 * (y < 3))
    for a in range(0, 360, 30):
        T.px(cx + 1.2 * np.cos(np.radians(a)), 1 + 1.2 * np.sin(np.radians(a)), 0.95)
    if half:
        keep = (lambda x: x < cx - 1) if half == 'l' else (lambda x: x > cx + 1)
        for Tn in (T, K):
            for x in range(W):
                if not keep(x):
                    Tn.m[:, x] = False
            Tn.m[:cy - 5, :] = False                        # (the pointer goes with neither)
        rr = rng(41 if half == 'l' else 43)             # the broken end, jagged
        bx = cx - 2 if half == 'l' else cx + 2
        for y in range(cy - 4, cy + 5):
            if rr.uniform() < 0.5:
                T.m[y, bx] = False
    im, ox, oy = _stack([(T, BRASS, 0.25), (K, SM.IRON, 0)], W, H)
    if half == 'l':
        return im, cx - 2 - ox, cy - oy
    if half == 'r':
        return im, cx + 2 - ox, cy - oy
    return im, cx - ox, cy - oy


def gs_pan(part='front'):
    """A pan: a wide, shallow brass bowl. front: its outside, the rim lit along the top, a foot ring under it (drawn in
    front of whatever is in the pan). back: the far side of the rim, seen over the near side (drawn behind it).
    Anchored on the middle of the pan's floor."""
    W, H = 2 * PAN_HW + 4, RIM + BOTTOM + 6
    cx, fy = PAN_HW + 2, RIM + 3            # the floor's row; the rim is RIM above it
    T = Tone(W, H)
    ry = fy - RIM
    if part == 'front':
        for y in range(ry, fy + BOTTOM + 1):
            v = (y - ry) / float(RIM + BOTTOM)
            hw = PAN_HW - (v ** 2.4) * (PAN_HW - 15)
            for x in range(int(round(cx - hw)), int(round(cx + hw)) + 1):
                u = (x - (cx - hw)) / (2 * hw + 0.01)
                t = 0.78 - 0.36 * v + 0.16 * np.exp(-((v - 0.22) / 0.12) ** 2) - 0.26 * (u > 0.74) + 0.08 * (u < 0.18) - 0.10 * (u > 0.9)
                if y <= ry + 1:
                    t = 0.95 - 0.30 * (u > 0.8) - 0.10 * (y == ry + 1)
                T.px(x, y, t)
        for y in (fy + BOTTOM + 1,):                          # the foot ring
            for x in range(cx - 9, cx + 10):
                T.px(x, y, 0.56 - 0.24 * (x > cx + 3) - 0.10 * (y > fy + BOTTOM + 1))
        for sx in (-1, 1):                                    # the eyes the chains hook into
            ex = cx + sx * (PAN_HW - 2)
            T.px(ex, ry - 1, 0.70)
            T.px(ex, ry - 2, 0.50)
    else:
        for x in range(cx - PAN_HW + 1, cx + PAN_HW):
            u = (x - cx) / float(PAN_HW)
            y = ry - int(round(2.5 * np.sqrt(max(0, 1 - u * u))))
            T.px(x, y, 0.40 - 0.12 * (u > 0.5))
            T.px(x, y + 1, 0.22)
    im, ox, oy = _stack([(T, BRASS, 0.25)], W, H, outline_=(part == 'front'))
    return im, cx - ox, fy - oy


def gs_weight():
    """One of his iron weights: a squat round weight with a knob on top, the sort a souq scale is used with."""
    rows = ['...xx...',
            '..xZzx..',
            '...xx...',
            '.xxyyxx.',
            'xzZzzyyx',
            'xzzzyyyx',
            'xyzyyyyx',
            '.xxxxxx.']
    im = sprite(rows, {'x': '#16120e', 'y': '#3e3a36', 'z': '#6a645c', 'Z': '#a49c90'})
    return im, im.width // 2, im.height // 2


# ------------------------------------------------------------------ the Weighmaster
BLUNDER = dict(grip=(7, 4), rows=[
    '...................DE',
    '....DEEEEEEEEEEEEEDEF',
    'WXYYDEFFFFFFFFFFFFEEF',
    'WXKJDDEEEEEEEEEEEEEEF',
    'WXKJXxyyWXYYYXW...DEF',
    'WWXXX.xyyxWXXXW....DE',
    '.WWW..xyyx...........',
    '......xyx............',
])
WEIGHT_IN_HAND = ['.xx.', 'xyyx', 'yzyy', 'xyyx']


def _gun(L, p, g):
    w = BLUNDER
    L.append((w['rows'], g[0] - w['grip'][0], g[1] - w['grip'][1], p))


def weighmaster(act='stand', pose='stand', bob=0):
    """The Dhanabs' Weighmaster: stout, a maroon coat and a gold turban, his brass blunderbuss. act: stand (the gun
    held low), aim (levelled), up (hands up: clinging to the chains in his pan, thrown in the air, giving up at the
    end), heft (an iron weight up behind his head), throw (arm out, weight gone), sneeze (doubled over), pant (bent
    over getting his breath)."""
    p = ms3.pal('maroon', 'dark', 'turban', 'skin1')
    p['9'] = '#e4dec2'
    p.update({'x': '#16120e', 'y': '#3e3a36', 'z': '#6a645c'})
    B = HEAVY
    L = []
    dx, dy = 0, bob
    if pose == 'pass':
        dy -= 1
        legs = [at(MS.LEGH_FAR, B.legs, p, 3), at(MS.LEGH_NEAR, B.legs, p, 9), at('futa_h', B.futa, p, 0, -1)]
    else:
        legs = [at('legs_h', B.legs, p), at('futa_h', B.futa, p)]
    if act in ('up', 'heft'):
        L.append(at('arm_raise_l', (4, -1), p, dx, dy))
        if act == 'heft':
            L.append((WEIGHT_IN_HAND, 3 + dx, -5 + dy, p))
    L += legs + [at('jacket_h', B.torso, p, dx, dy), at('belt', B.belt, p, dx, dy)]
    if act in ('stand', 'sneeze', 'pant'):
        _gun(L, p, (B.grip[0] + dx, B.grip[1] + 4 + dy))
        L += [at('forearm_h', (B.forearm[0], B.forearm[1] + 3), p, dx, dy)]
    elif act == 'aim':
        _gun(L, p, (20 + dx, 12 + dy))
        L += [at('forearm_up', (10, 9), p, dx, dy)]
    elif act == 'throw':
        L += [at('forearm_up', (11, 7), p, dx, dy)]
    elif act == 'heft':
        L += [at('forearm_h', B.forearm, p, dx, dy)]
    L += [at('sleeve_h', B.sleeve, p, dx, dy)]
    L += [at(FACES['angry'], B.face, p, dx, dy), at(WRAPS['kufiya'], B.wrap, p, dx, dy - 1, ink=INK2)]
    if act == 'up':
        L.append(at('arm_raise_fl', (19, 2), p, dx, dy))
    f = SP.build(L, B.foot)
    if act == 'sneeze':
        f['im'], f['ax'], f['ay'] = _shear(f['im'], f['ax'], f['ay'], 0.30)
    elif act == 'pant':
        f['im'], f['ax'], f['ay'] = _shear(f['im'], f['ax'], f['ay'], 0.22)
    return f


# ------------------------------------------------------------------ his porters
SACK_ON = ['...ejjjjjjje..',
           '.ejjoooooojjj.',
           'ejoo++o+ooojje',
           'ejo+oooooojjee',
           'ejooooo+ooojje',
           '.ejjjoooojjje.',
           '..eeeejjjeee..']
BURLAP = {'e': '#4a361e', 'j': '#7c5e38', 'o': '#a8885a', '+': '#d0b484'}


def porter(who='a', act='carry', pose='stand'):
    """A Dhanab porter, his scarf over his nose: a sack of spice on his shoulder (carry), heaved up over his head into
    the pan (heave), or running off without it (run). 'a' is long and thin, 'b' short and round."""
    p = ms3.militia_pal('skin2' if who == 'a' else 'skin3')
    p.update(BURLAP)
    B = LEAN if who == 'a' else HEAVY
    L = []
    if who == 'a':
        legs, dx, dy = SP.lean_legs(p, pose)
    else:
        dx, dy = 0, 0
        if pose == 'pass':
            dy = -1
            legs = [at(MS.LEGH_FAR, B.legs, p, 3), at(MS.LEGH_NEAR, B.legs, p, 9), at('futa_h', B.futa, p, 0, -1)]
        else:
            legs = [at('legs_h', B.legs, p), at('futa_h', B.futa, p)]
    if act in ('carry', 'heave', 'up'):
        L.append(at('arm_raise_l', (3, 0) if who == 'a' else (4, -1), p, dx, dy))
    if act == 'carry':
        L.append((SACK_ON, (0 if who == 'a' else 1) + dx, -4 + dy, p))
    if who == 'a':
        L += legs + [at('jacket_l', B.torso, p, dx, dy), at('belt_l', B.belt, p, dx, dy), at('jambiya_s', B.jamb, p, dx, dy)]
    else:
        L += legs + [at('jacket_h', B.torso, p, dx, dy), at('belt', B.belt, p, dx, dy)]
    if act == 'run':
        L += [at('forearm_l' if who == 'a' else 'forearm_h', B.forearm, p, dx, dy)]
    L += [at('sleeve_l' if who == 'a' else 'sleeve_h', B.sleeve, p, dx, dy), at('armband', B.sleeve, p, dx + 2, dy + 2)]
    face = 'worried' if who == 'a' else 'qat'
    if who == 'a':
        SP.lean_head(L, face, p, dx, dy)
        L.append(at(BAND, (B.face[0] + 3, B.face[1] + 2), p, dx, dy))
    else:
        L += [at(FACES[face], B.face, p, dx, dy), at(WRAPS['check'], B.wrap, p, dx - 1, dy, ink=INK2)]
        L.append(at(BAND, (B.face[0] + 3, B.face[1] + 2), p, dx, dy))
    if act == 'heave':
        L.append((SACK_ON, (2 if who == 'a' else 4) + dx, -10 + dy, p))
    if act in ('heave', 'up'):
        L.append(at('arm_raise_fl', (17, 2) if who == 'a' else (19, 2), p, dx, dy))
    f = SP.build(L, B.foot)
    if act == 'carry':
        f['im'], f['ax'], f['ay'] = _shear(f['im'], f['ax'], f['ay'], 0.12)
    return f


# ------------------------------------------------------------------ all of them
def frames():
    """name -> dict(im, ax, ay): the characters (they get white hit copies like the others)."""
    out = {}
    for look in SHOPS:
        out[look + '_tied'] = SP.build(*shopkeeper(look, 'tied'))
        out[look + '_freed'] = SP.build(*shopkeeper(look, 'freed'))
        out[look + '_walk1'] = SP.build(*shopkeeper(look, 'walk'))
        out[look + '_walk2'] = SP.build(*shopkeeper(look, 'walk', 'pass'))
    for act in ('stand', 'aim', 'up', 'heft', 'throw', 'sneeze', 'pant'):
        out['wm_' + act] = weighmaster(act)
    out['wm_pant1'] = weighmaster('pant', bob=1)
    out['wm_up_pass'] = weighmaster('up', 'pass')
    out['wm_pass'] = weighmaster('stand', 'pass')
    for who in ('a', 'b'):
        out['porter_%s_carry0' % who] = porter(who, 'carry', 'stand')
        out['porter_%s_carry1' % who] = porter(who, 'carry', 'pass')
        out['porter_%s_heave' % who] = porter(who, 'heave', 'stand')
        out['porter_%s_run0' % who] = porter(who, 'run', 'stand')
        out['porter_%s_run1' % who] = porter(who, 'run', 'pass')
        out['porter_%s_flung' % who] = porter(who, 'up', 'stand')
    return out


def zabid_fx():
    """name -> (image, ax, ay): props, effects and the Great Scale's parts."""
    out = {}
    for col in ('red', 'yel', 'org'):
        out['spice_' + col] = spice_sack(col)
        for k in range(3):
            out['cpuff_%s%d' % (col, k)] = cloud_puff(col, k, r=10 + k * 2)
    out['fx_sneeze'] = sneeze_spray()
    for g in ('tea', 'spice', 'cloth'):
        out['counter_' + g] = counter(g)
    for s in range(3):
        out['barr%d' % s] = barricade(s)
    out.update(barricade_bits())
    out['zbags'] = zbags()
    out['gs_post'] = gs_post()
    out['gs_beam'] = gs_beam()
    out['gs_beam_l'] = gs_beam('l')
    out['gs_beam_r'] = gs_beam('r')
    out['gs_pan'] = gs_pan('front')
    out['gs_panb'] = gs_pan('back')
    out['gs_weight'] = gs_weight()
    out['pick_chilli'] = pick_chilli()
    for k in range(3):
        out['fx_redpuff%d' % k] = red_puff(k)
    return out


def preview(path):
    fr = frames()
    fx = zabid_fx()
    cells = [(n, f['im'], f['ax'], f['ay']) for n, f in fr.items()] + [(n, v[0], v[1], v[2]) for n, v in fx.items()]
    cols = 12
    cw, ch = 96, 100
    rows = (len(cells) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols * cw, rows * ch), (86, 150, 170, 255))
    for i, (n, im, ax, ay) in enumerate(cells):
        cx, cy = (i % cols) * cw + cw // 2, (i // cols) * ch + ch - 14
        sheet.alpha_composite(im, (max(0, cx - ax), max(0, cy - ay)))
        sheet.putpixel((cx, cy), (255, 0, 255, 255))
    sheet = sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST)
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheet)
    for i, (n, im, ax, ay) in enumerate(cells):
        d.text(((i % cols) * cw * 3 + 4, (i // cols) * ch * 3 + 4), n, fill=(255, 255, 255, 255))
    sheet.save(path)
    print(len(cells), 'sprites')


if __name__ == '__main__':
    preview(sys.argv[1] if len(sys.argv) > 1 else 'zabid_sprites.png')
