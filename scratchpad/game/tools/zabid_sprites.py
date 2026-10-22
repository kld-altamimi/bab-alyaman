# zabid_sprites.py - the sprites The Souq adds: sacks of spice and the clouds they burst into, the shopkeepers tied
# behind their counters, the Dhanabs' barricades (whole, knocked about, nearly gone, and the bits that fly off), a wall
# of sandbags, and the Tailor's shop: the Tailor himself (and so every one of his dummies, which wear what he wears), a
# dummy with its clothes shot off, the wheeled stands they stand on, the sheets thrown over them, his shears and his pins,
# and him wound up in his own tape at the end.
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
    """Dried chillies out of the Tailor's dummies when they go over (he stuffed them with stolen chillies): worth
    picking up (points)."""
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


# ------------------------------------------------------------------ the Tailor, and his dummies
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


# His coat: a tailor's own jacket over a white thobe, the shirt showing at the neck and the edge of the lapel running down
# it. Every dummy in his shop wears the same, so every frame of his that stands still is a frame of theirs too.
COAT_S = ['...bccb...',
          '.abccdcb..',
          'abbccdIJb.',
          'abbccdIJcb',
          'abbccc#Icb',
          'abbccc#ccb',
          'abbcc#cccb',
          'abbcc#cccb',
          '.abbc#cccb',
          '.abbcc#ccb',
          '.abbcc#ccb',
          '.abbcccccb',
          '.abbcccccb',
          '.aabbcccbb',
          '..aabbbbb.']
TAPE_DOWN = ['F', 'E', 'F', 'D', 'F', 'E', 'F', 'D', 'F', 'E', 'Z']      # the tape measure round his neck, down his front
TAPE_BACK = ['F', 'E', 'D', 'F', 'E']                                       # (and its other end, over his shoulder)
ARM_HANG = ['.bcd.',                                                        # an arm hanging straight down, stiff as a dummy's
            'bccdb',
            'bccdb',
            'abccb',
            'abbcb',
            '.abcb',
            '.abcb',
            '.abb.',
            '.pqr.',
            '.pqr.',
            '..q..']
FACE_TAILOR = ['..rrrr#rr.',                                                # clean-shaven but for a thin moustache
               '..qrrrrrst',
               '..q%rssrq.',
               '..qrrruuu.',
               '...qrrr#r.',
               '....qrrr..']
SCISSORS_UP = ['J...J', '.Z.Z.', '.ZJZ.', '..#..', '.u.u.', 'u.u.u', '.u.u.']   # his shears, open, held up
PINS_HAND = ['Z.Z.', '.Z.Z', 'ZZ..']                                         # a pinch of pins
TAPE_CASE = ['.EF.', 'EFFE', 'EDFE', '.EE.']                                 # the tape's brass case
WAVE = {'wave0': (['.r.r.', 'qrrr.', '.qrr.', '.bcc.', '.bcc.', 'abc..', 'abc..', 'abc..'], (14, -2)),
        'wave1': (['..r.r', '.qrrr', '.qrr.', '.bcc.', '.bcc.', '.abc.', 'abc..', 'abc..'], (16, -2))}
TL_TOP = 'maroon'


def tailor(act='pose'):
    """The Dhanabs' tailor (and every dummy in his shop: they wear exactly what he wears): slim, a maroon jacket over a
    white thobe, a white cap, his tape measure round his neck. act: pose (stock still, arms at his sides: the dummies'
    one frame), wave0/wave1 (hello), raise (his shears up: about to throw), pins (a pinch of pins drawn back), lash (bent
    forward with the tape's case: about to send it along the floor), throw (arm out, gone), caught0/caught1 (found out:
    flapping), sneeze (doubled over)."""
    p = ms3.pal(TL_TOP, 'cream', 'redchk', 'skin2')
    B = SLIM
    L = []
    if act in ('caught0', 'caught1', 'pins'):
        k = 1 if act == 'caught1' else 0
        L.append(at('arm_raise_l', (2 + k, -2 + k), p))
        if act == 'pins':
            L.append((PINS_HAND, 2, -5, p))
    L += [at('bare_feet_s', B.legs, p), at('thobe_s', B.futa, p), at(COAT_S, B.torso, p)]
    L += [at(TAPE_BACK, (B.torso[0] + 3, B.torso[1] + 1), p)]
    if act in ('pose', 'pins', 'sneeze', 'wave0', 'wave1'):
        L += [at(ARM_HANG, (B.sleeve[0] + 1, B.sleeve[1] - 1), p)]
    elif act == 'throw':
        L += [at('sleeve_s', B.sleeve, p), at('forearm_s', (B.forearm[0] + 2, B.forearm[1] - 1), p)]
    elif act == 'lash':
        L += [at('sleeve_s', B.sleeve, p), at('forearm_s', (B.forearm[0] + 1, B.forearm[1] + 2), p), (TAPE_CASE, B.forearm[0] + 11, B.forearm[1] + 3, p)]
    L += [at(TAPE_DOWN, (B.torso[0] + 7, B.torso[1] + 1), p)]
    L += [at(FACE_TAILOR, B.face, p), at(WRAPS['cap'], B.wrap, p, 1 if act == 'caught1' else 0, 1, ink=INK2)]
    if act in WAVE:
        L.append(at(WAVE[act][0], WAVE[act][1], p))
    elif act in ('caught0', 'caught1', 'raise'):
        ox = {'caught0': (12, 1), 'caught1': (13, 0), 'raise': (12, 0)}[act]
        L.append(at('arm_raise_fl', ox, p))
        if act == 'raise':
            L.append(at(SCISSORS_UP, (ox[0] + 2, ox[1] - 7), p))
    f = SP.build(L, B.foot)
    if act == 'sneeze':
        f['im'], f['ax'], f['ay'] = _shear(f['im'], f['ax'], f['ay'], 0.3)
    elif act == 'lash':
        f['im'], f['ax'], f['ay'] = _shear(f['im'], f['ax'], f['ay'], 0.18)
    return f


def tailor_wrapped(k=0):
    """Him at the end, wound round and round in his own tape, arms to his sides; k=1 squashed for a hop."""
    f = tailor('pose')
    a = np.asarray(f['im']).copy()
    H_, W_ = a.shape[:2]
    for y in range(H_):
        for x in range(W_):
            if a[y, x, 3] == 0 or not (5 <= f['ay'] - y <= 34):
                continue
            ph = (y + x // 2) % 6
            if ph in (0, 1):
                a[y, x, :3] = (255, 226, 100) if ph == 0 else (212, 156, 28)
            elif ph == 2 and x % 3 == 0:
                a[y, x, :3] = (122, 82, 8)
    im = Image.fromarray(a, 'RGBA')
    if k == 1:
        return dict(im=im.resize((im.width + 2, im.height - 2), Image.NEAREST), ax=f['ax'] + 1, ay=f['ay'] - 2)
    return dict(im=im, ax=f['ax'], ay=f['ay'])


LINEN = ramp(['#4a3c26', '#7a6644', '#a8946a', '#cbb88c', '#e6d6ae', '#f6ecd0'], 12)
SHEET = ramp(['#5a5448', '#8c8676', '#b8b2a0', '#dcd6c4', '#f2eee0', '#fffdf4'], 12)


def tl_bare():
    """A dummy with its clothes shot off: what was under them, a padded linen dress form on a turned wooden pole, a
    wooden knob for a head, a pin or two still in it and a scrap of the coat on its shoulder. Anchored where its pole
    stands (as a figure's anchor is between its feet)."""
    W, H = 24, 44
    cx, base = 11, 41
    T = Tone(W, H)                   # the linen
    K = Tone(W, H)                   # the wood
    for y in range(base - 16, base + 1):
        for x in (cx, cx + 1):
            K.px(x, y, 0.70 - 0.30 * (x == cx + 1) + 0.08 * (y % 5 == 0))
    for x in range(cx - 2, cx + 4):
        K.px(x, base - 16, 0.62 - 0.08 * (x > cx + 1))
    for x in range(cx - 3, cx + 5):
        K.px(x, base, 0.50 - 0.10 * (x > cx + 2))
    top = base - 36
    prof = [(0, -3, 3), (1, -5, 4), (2, -6, 5), (3, -6, 6), (4, -6, 6), (5, -6, 7), (6, -6, 7), (7, -6, 6), (8, -5, 6),
            (9, -5, 5), (10, -4, 5), (11, -4, 4), (12, -4, 4), (13, -4, 4), (14, -5, 5), (15, -5, 5), (16, -6, 5), (17, -6, 5),
            (18, -6, 5), (19, -5, 4), (20, -4, 3)]
    for dy, l, r in prof:                                   # shoulders, chest (out to the front, to the right), waist, hips
        y = top + 3 + dy
        for x in range(cx + l, cx + r + 1):
            u = (x - (cx + l)) / float(r - l + 0.01)
            T.px(x, y, 0.80 - 0.40 * u + 0.12 * (u < 0.25) - 0.10 * (dy in (11, 12, 13)) + 0.05 * (((x * 5 + y * 3) % 7) == 0))
    for y in range(top + 3, top + 24):                      # a seam down the front
        if y % 2 == 0:
            T.px(cx + 1, y, 0.42)
    for y in range(top, top + 3):                           # the neck, and the knob on it
        K.px(cx, y, 0.66)
        K.px(cx + 1, y, 0.46)
    for ang in range(0, 360, 20):
        for r in (1, 2):
            K.px(cx + 0.5 + r * np.cos(np.radians(ang)), top - 2 + r * np.sin(np.radians(ang)), 0.80 - 0.18 * r - 0.22 * (np.cos(np.radians(ang)) > 0.3))
    im, ox, oy = _stack([(K, SM.TEAK, 0.2), (T, LINEN, 0.3)], W, H)
    a = np.asarray(im).copy()

    def put(x, y, col):
        x -= ox
        y -= oy
        if 0 <= x < a.shape[1] and 0 <= y < a.shape[0]:
            a[y, x] = tuple(int(col[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
    for (x, y) in ((cx + 5, top + 7), (cx + 4, top + 14), (cx - 4, top + 9)):
        put(x, y, '#c8301a')
        put(x + 1, y, '#c4be98')
    for (x, y, c) in ((cx - 5, top + 4, '#74202a'), (cx - 5, top + 5, '#b04a44'), (cx - 4, top + 4, '#b04a44'), (cx - 6, top + 6, '#74202a'), (cx - 6, top + 7, '#3c0c12')):
        put(x, y, c)
    return dict(im=Image.fromarray(a, 'RGBA'), ax=cx - ox, ay=base - oy)


def tl_stand():
    """The wheeled stand a figure stands on: a block of wood on two little iron castors. Anchored on the floor in its
    middle; its top is 7 above the floor (tailor.js: STAND_H)."""
    W, H = 22, 9
    cx = 11
    T = Tone(W, H)
    K = Tone(W, H)
    for y in range(1, 5):
        for x in range(cx - 9, cx + 9):
            T.px(x, y, 0.70 - 0.28 * (y >= 3) + 0.16 * (y == 1) - 0.08 * ((x - cx + 9) > 14) + 0.04 * ((x * 3) % 7 == 0))
    for wx in (cx - 6, cx + 5):
        for ang in range(0, 360, 30):
            for r in (0.5, 1.4):
                K.px(wx + r * np.cos(np.radians(ang)), 6.5 + r * np.sin(np.radians(ang)), 0.70 - 0.3 * (np.sin(np.radians(ang)) > 0.2))
        K.px(wx, 5, 0.45)
    im, ox, oy = _stack([(K, SM.IRON, 0), (T, SM.TEAK, 0.25)], W, H)
    return im, cx - ox, 8 - oy


def tl_cover():
    """The sheet thrown over a figure on its stand: a length of plain cloth, a bump for the head and the shoulders,
    hanging in folds to the floor. Anchored on the floor in its middle."""
    W, H = 30, 52
    cx, fl = 15, 50
    T = Tone(W, H)
    top = fl - 46
    for y in range(top, fl - 1):
        v = (y - top) / float(fl - top)
        hw = 4 + 22 * v if v < 0.12 else (6.6 + 5 * (v - 0.12) / 0.12 if v < 0.24 else 11.6 + 2.4 * (v - 0.24) / 0.76)
        for x in range(int(round(cx - hw)), int(round(cx + hw)) + 1):
            u = (x - (cx - hw)) / (2 * hw + 0.01)
            T.px(x, y, 0.82 - 0.34 * u + 0.10 * np.sin((x - cx) * 0.9 + y * 0.05) * min(1, v * 2.2) + 0.08 * (u < 0.15))
    rr = rng(17)                                            # the hem, uneven along the floor
    for x in range(cx - 14, cx + 15):
        if rr.uniform() < 0.6:
            T.px(x, fl - 1, 0.50 - 0.2 * (x > cx + 6))
    im, ox, oy = _stack([(T, SHEET, 0.3)], W, H)
    return im, cx - ox, fl - oy


def tl_scissors():
    """His shears, open, as they fly: blades to the right. Anchored in the middle (the game turns them)."""
    rows = ['.......J', '.....JZ.', '.uu.ZZ..', 'u..u#...', '.uu.ZZ..', '.....JZ.', '.......J']
    im = ms3.part(rows, ms3.pal(TL_TOP, 'cream', 'redchk', 'skin2'))
    return im, im.width // 2, im.height // 2


def tl_pin():
    """A pin in flight, point first, its red head behind: outlined so it shows against the floor. Anchored in the
    middle (the game turns it along its way)."""
    im = ms3.part(['MLZZZJ', 'LL....'], {'L': '#c8301a', 'M': '#f87a4c', 'Z': '#c4be98', 'J': '#fffbef'})
    return im, im.width // 2, im.height // 2


# ------------------------------------------------------------------ all of them
def frames():
    """name -> dict(im, ax, ay): the characters (they get white hit copies like the others)."""
    out = {}
    for look in SHOPS:
        out[look + '_tied'] = SP.build(*shopkeeper(look, 'tied'))
        out[look + '_freed'] = SP.build(*shopkeeper(look, 'freed'))
        out[look + '_walk1'] = SP.build(*shopkeeper(look, 'walk'))
        out[look + '_walk2'] = SP.build(*shopkeeper(look, 'walk', 'pass'))
    for act in ('pose', 'wave0', 'wave1', 'raise', 'pins', 'lash', 'throw', 'caught0', 'caught1', 'sneeze'):
        out['tl_' + act] = tailor(act)
    out['tl_wrapped0'] = tailor_wrapped(0)
    out['tl_wrapped1'] = tailor_wrapped(1)
    out['tl_bare'] = tl_bare()
    return out


def zabid_fx():
    """name -> (image, ax, ay): props, effects and the Tailor's shop."""
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
    out['tl_stand'] = tl_stand()
    out['tl_cover'] = tl_cover()
    out['tl_scissors'] = tl_scissors()
    out['tl_pin'] = tl_pin()
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
