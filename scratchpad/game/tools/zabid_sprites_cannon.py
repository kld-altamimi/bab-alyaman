# zabid_sprites.py - the sprites The Souq adds: sacks of spice and the clouds they burst into, the shopkeepers tied
# behind their counters, the Dhanabs' barricades (whole, knocked about, nearly gone, and the bits that fly off), a wall
# of sandbags, and the Spice Cannon in parts: its wheels, its cart, its brass barrel (turned by the game), its basket of
# chillies, the chillies and the big chilli rounds it fires, and the two Dhanabs who push it, with scarves over their
# noses (one long and thin, one short and round), pushing, panting, and with their hands up at the end.
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


# ------------------------------------------------------------------ the Spice Cannon
# Coordinates from the point on the ground under its axle (the anchor). It faces left: its muzzle to the left, the
# handles and the two men pushing to the right.
CW, CH = 150, 90
CX, CY = 70, 86
WHEEL_R = 14
AXLE = (0, -WHEEL_R)
PIVOT = (-12, -38)                         # the barrel's trunnions, where the game turns it
WOOD = P.WOOD


def _cv():
    return Tone(CW, CH)


def _cpart(layers, outline_=True):
    im, ox, oy = _stack(layers, CW, CH, outline_)
    return im, CX - ox, CY - oy


def wheel(k=0, far=False):
    """A big spoked cart wheel, iron tyred: k (0..2) turns its spokes; the far one is darker and a little smaller."""
    T = _cv()
    K = _cv()
    ax, ay = CX + AXLE[0], CY + AXLE[1]
    R = WHEEL_R - (1 if far else 0)
    for a in range(0, 360, 3):
        for rr in (R - 2, R - 1):
            T.px(ax + rr * np.cos(np.radians(a)), ay + rr * np.sin(np.radians(a)), (0.70 if rr == R - 2 else 0.54) - 0.20 * (np.sin(np.radians(a)) > 0.3))
        K.px(ax + R * np.cos(np.radians(a)), ay + R * np.sin(np.radians(a)), 0.40 + 0.20 * (np.sin(np.radians(a)) < -0.5))
    for i in range(8):
        a = np.radians(i * 45 + k * 15)
        T.line([(ax + 2 * np.cos(a), ay + 2 * np.sin(a)), (ax + (R - 2) * np.cos(a), ay + (R - 2) * np.sin(a))], 0.58)
    T.rect(ax - 2, ay - 2, ax + 2, ay + 2, 0.46)
    K.rect(ax - 1, ay - 1, ax + 1, ay + 1, 0.70)
    if far:
        T.t = T.t * 0.62
        K.t = K.t * 0.70
    return _cpart([(T, WOOD, 0.2), (K, SM.IRON, 0)])


def cart(broken=False):
    """The cart: a plank bed on its frame over the axle, the handles running back and up to where the men push, a box
    for the shot under the bed. broken: the bed split and charred."""
    T = _cv()
    K = _cv()
    y0, y1 = CY - 26, CY - 19                    # the bed
    for x in range(CX - 40, CX + 34):
        for y in range(y0, y1):
            t = 0.70 - 0.24 * ((y - y0) / 6.0) + 0.08 * ((x % 7) == 0) - 0.10 * (y == y1 - 1)
            if y == y0:
                t = 0.90
            if broken and (abs(x - CX + 6) < 2 or ((x * 7 + y) % 11 == 0)):
                continue
            T.px(x, y, t)
    for x in range(CX - 36, CX + 30):            # the frame under it
        T.px(x, y1, 0.40)
        T.px(x, y1 + 1, 0.28)
    # the handles, back and up to the men's hands
    for k in range(40):
        hx, hy = CX + 30 + k, y0 + 2 - k * 0.32
        T.px(hx, hy, 0.74)
        T.px(hx, hy + 1, 0.46)
    T.rect(CX + 68, y0 - 12, CX + 71, y0 - 10, 0.60)
    # the shot box under the bed
    for x in range(CX - 34, CX - 14):
        for y in range(y1 + 2, y1 + 9):
            T.px(x, y, 0.56 - 0.20 * ((y - y1 - 2) / 6.0) + 0.10 * (x == CX - 34))
    # iron straps
    for sx in (CX - 30, CX - 2, CX + 24):
        K.rect(sx, y0, sx + 1, y1, 0.46)
    if broken:
        T.t = T.t * 0.55
    return _cpart([(T, WOOD, 0.3), (K, SM.IRON, 0)])


def carriage():
    """The block the barrel rides on, wedged at the back to lift the muzzle."""
    T = _cv()
    for y in range(CY - 38, CY - 25):
        v = (y - (CY - 38)) / 13.0
        for x in range(CX - 28 + int(4 * (1 - v)), CX + 6):
            T.px(x, y, 0.66 - 0.20 * v - 0.12 * ((x - CX + 28) / 34.0) + 0.06 * (((x + y) % 5) == 0))
    T.rect(CX - 16, CY - 40, CX - 8, CY - 37, 0.50)
    return _cpart([(T, WOOD, 0.3)])


def barrel(cracked=False):
    """The brass cannon: muzzle flared, rings, a ball at the back; anchored at its trunnions so the game can raise and
    lower it. cracked: split along the top and wired up."""
    W, H = 70, 24
    px_, py_ = 46, 12                           # the trunnions on this canvas; the muzzle points left
    T = Tone(W, H)
    for x in range(px_ - 40, px_ + 14):
        u = (px_ + 14 - x) / 54.0                # 0 at the breech, 1 at the muzzle
        half = 5.6 - 1.8 * u + (1.6 if u > 0.94 else 0) + (0.8 if abs(u - 0.38) < 0.03 or abs(u - 0.70) < 0.03 else 0)
        for y in range(int(py_ - half), int(py_ + half) + 1):
            v = (y - (py_ - half)) / (2 * half)
            t = 0.46 + 0.46 * np.exp(-((v - 0.30) / 0.22) ** 2) - 0.10 * (v > 0.8)
            if abs(u - 0.38) < 0.03 or abs(u - 0.70) < 0.03:
                t += 0.10
            T.px(x, y, t)
    for a in range(0, 360, 20):                 # the ball at the back
        for rr in (1, 2, 3):
            T.px(px_ + 16 + rr * np.cos(np.radians(a)), py_ + rr * np.sin(np.radians(a)), 0.80 - 0.12 * rr)
    T.rect(px_ - 41, py_ - 3, px_ - 40, py_ + 3, 0.20)            # the bore, dark
    L = T.layer(BRASS, dither=0.3)
    if cracked:
        for x in range(px_ - 30, px_ + 4):
            y = py_ - 4 + int(1.2 * np.sin(x * 0.7))
            L.rgb[y, x] = (40, 20, 6)
        for x in (px_ - 20, px_ - 8):
            L.rgb[py_ - 6:py_ + 6, x] = (90, 90, 96)
    im = P.outlined(L).image()
    bb = im.getbbox()
    im = im.crop(bb)
    return im, px_ + 1 - bb[0], py_ + 1 - bb[1]


def basket():
    """A big basket on the bed behind the cannon, heaped with dried chillies: what it fires."""
    T = _cv()
    S = _cv()
    bx0, bx1, top, bot = CX + 6, CX + 30, CY - 40, CY - 26
    for y in range(top, bot):
        v = (y - top) / float(bot - top)
        for x in range(bx0 + int(2 * v), bx1 - int(2 * v)):
            T.px(x, y, 0.62 + 0.12 * ((x + y) % 2) - 0.18 * v - 0.10 * (x > bx1 - 6))
    for x in range(bx0 + 1, bx1 - 1):
        u = (x - (bx0 + bx1) / 2.0) / ((bx1 - bx0) / 2.0)
        hh = int(6 * np.sqrt(max(0, 1 - u * u)))
        for y in range(top - hh, top + 1):
            S.px(x, y, 0.62 + 0.20 * ((x * 3 + y * 5) % 4 == 0) - 0.20 * (x > bx1 - 7))
    return _cpart([(T, SZ.PALMW, 0.2), (S, CHILLI, 0.2)])


def wreck():
    """What is left: the cart on its side, the bed split, the barrel down on the floor, one wheel, burnt and red with
    chilli dust."""
    parts = [cart(True), wheel(1, far=True)]
    canvas = Image.new('RGBA', (CW + 40, CH + 40), (0, 0, 0, 0))
    for im, ax, ay in parts:
        canvas.alpha_composite(im, (CX + 20 - ax, CY + 20 - ay))
    b, bax, bay = barrel(True)
    b = b.rotate(-8, resample=Image.NEAREST, expand=True)
    canvas.alpha_composite(b, (CX + 20 - 44, CY + 20 - 14))
    bb = canvas.getbbox()
    return canvas.crop(bb), CX + 20 - bb[0], CY + 20 - bb[1]


def chilli(k=0):
    """One dried chilli, end over end in the air (four turns)."""
    rows = [['.xxx...', 'xRRrRx.', '.xxRRrG', '....xG.'], ['..xx.', '.xRRx', 'xRrRx', 'xRRx.', 'Gxx..'],
            ['...xxx.', '.xRrRRx', 'GRRxxx.', '.G.....'], ['.xx..', 'xRRx.', 'xRrRx', '.xRRx', '..xxG']][k % 4]
    im = sprite(rows, {'x': '#2a0604', 'R': '#c8301a', 'r': '#f87a4c', 'G': '#4a6a1c'})
    return im, im.width // 2, im.height // 2


def shell():
    """A chilli round: a fat bundle of dried chillies bound with string, the size of a fist."""
    rows = ['...xxxxx...', '.xxRrRRRxx.', 'xRRrRSRrRRx', 'xRRRSRRRrRG', 'xRrRRSRRRRx', '.xxRRRrRxx.', '...xxxxx...']
    im = sprite(rows, {'x': '#2a0604', 'R': '#b82a16', 'r': '#f2804e', 'S': '#e6d6a8', 'G': '#4a6a1c'})
    return im, 5, 3


def pick_chilli():
    """Dried chillies out of the burst cannon: worth picking up (points)."""
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


# ------------------------------------------------------------------ the two who push it
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


def pusher(who='a', act='push', pose='stand', bob=0):
    """One of the two pushing the cannon: 'a' long and thin, 'b' short and round. Their scarves are up over their
    noses (the chilli). act: push (leaning into the handles, arms out), pant (bent over, getting his breath), up
    (hands up), pass/stand for the walk."""
    p = ms3.militia_pal('skin1' if who == 'a' else 'skin3')
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
    dy += bob
    if act == 'up':
        L.append(at('arm_raise_l', (3, 0) if who == 'a' else (4, -1), p, dx, dy))
    if who == 'a':
        L += legs + [at('jacket_l', B.torso, p, dx, dy), at('belt_l', B.belt, p, dx, dy)]
    else:
        L += legs + [at('jacket_h', B.torso, p, dx, dy), at('belt', B.belt, p, dx, dy)]
    if act == 'push':
        fa = 'forearm_l' if who == 'a' else 'forearm_h'
        L += [at(fa, (B.forearm[0] + 2, B.forearm[1] - 2), p, dx, dy)]
    L += [at('sleeve_l' if who == 'a' else 'sleeve_h', B.sleeve, p, dx, dy)]
    face = 'worried' if who == 'a' else 'angry'
    if who == 'a':
        SP.lean_head(L, face, p, dx, dy)
        L.append(at(BAND, (B.face[0] + 3, B.face[1] + 2), p, dx, dy))
    else:
        L += [at(FACES[face], B.face, p, dx, dy), at(WRAPS['check'], B.wrap, p, dx - 1, dy, ink=INK2)]
        L.append(at(BAND, (B.face[0] + 3, B.face[1] + 2), p, dx, dy))
    if act == 'up':
        L.append(at('arm_raise_fl', (17, 2) if who == 'a' else (19, 2), p, dx, dy))
    f = SP.build(L, B.foot)
    im, ax, ay = f['im'], f['ax'], f['ay']
    if act == 'push':
        im, ax, ay = _shear(im, ax, ay, 0.38)
    elif act == 'pant':
        im, ax, ay = _shear(im, ax, ay, 0.22)
    return dict(im=im, ax=ax, ay=ay)


# ------------------------------------------------------------------ all of them
def frames():
    """name -> dict(im, ax, ay): the characters (they get white hit copies like the others)."""
    out = {}
    for look in SHOPS:
        out[look + '_tied'] = SP.build(*shopkeeper(look, 'tied'))
        out[look + '_freed'] = SP.build(*shopkeeper(look, 'freed'))
        out[look + '_walk1'] = SP.build(*shopkeeper(look, 'walk'))
        out[look + '_walk2'] = SP.build(*shopkeeper(look, 'walk', 'pass'))
    for who in ('a', 'b'):
        out['push%s_push0' % who] = pusher(who, 'push', 'stand')
        out['push%s_push1' % who] = pusher(who, 'push', 'pass')
        out['push%s_pant0' % who] = pusher(who, 'pant', 'stand')
        out['push%s_pant1' % who] = pusher(who, 'pant', 'stand', bob=1)
        out['push%s_up_stand' % who] = pusher(who, 'up', 'stand')
        out['push%s_up_pass' % who] = pusher(who, 'up', 'pass')
    return out


def zabid_fx():
    """name -> (image, ax, ay): props, effects and the cannon's parts."""
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
    for k in range(3):
        out['cn_wheel%d' % k] = wheel(k)
        out['cn_wheelf%d' % k] = wheel(k, far=True)
    out['cn_cart'] = cart()
    out['cn_carriage'] = carriage()
    out['cn_barrel'] = barrel()
    out['cn_barrelc'] = barrel(True)
    out['cn_basket'] = basket()
    out['cn_wreck'] = wreck()
    for k in range(4):
        out['cn_chilli%d' % k] = chilli(k)
    out['cn_shell'] = shell()
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


def cannon_preview(path):
    """The cannon put together as the game stacks it, in a few states, to look at."""
    fx = zabid_fx()
    fr = frames()
    sheet = Image.new('RGBA', (3 * 190 + 10, 2 * 130 + 10), (200, 190, 170, 255))
    for i, (ang, k, ph) in enumerate(((0, 0, 1), (30, 1, 1), (-10, 2, 2), (0, 0, 3), (35, 1, 3), (0, 2, 1))):
        ax0, ay0 = 10 + (i % 3) * 190 + 80, 10 + (i // 3) * 130 + 118

        def put(name, dx=0, dy=0, im=None, a=None):
            if im is None:
                im, a1, a2 = fx[name] if name in fx else (fr[name]['im'], fr[name]['ax'], fr[name]['ay'])
            else:
                a1, a2 = a
            sheet.alpha_composite(im, (ax0 + dx - a1, ay0 + dy - a2))
        put('pushb_push%d' % (k % 2), 64, 0)
        if ph < 3:
            put('cn_wheelf%d' % k, 3, 0)
        put('cn_cart')
        put('cn_carriage')
        b, bx, by = fx['cn_barrelc' if ph == 3 else 'cn_barrel']
        if ang:
            bi = b.rotate(-ang, resample=Image.NEAREST, expand=True, center=(bx, by))
            put(None, PIVOT[0], PIVOT[1], im=bi, a=(bx + (bi.width - b.width) // 2, by + (bi.height - b.height) // 2))
        else:
            put('cn_barrel' if ph < 3 else 'cn_barrelc', PIVOT[0], PIVOT[1])
        if ph == 1:
            put('cn_basket')
        put('cn_wheel%d' % k)
        put('pusha_push%d' % (k % 2), 52, 0)
    sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(path)


if __name__ == '__main__':
    if 'cannon' in sys.argv:
        cannon_preview(sys.argv[1])
    else:
        preview(sys.argv[1] if len(sys.argv) > 1 else 'zabid_sprites.png')
