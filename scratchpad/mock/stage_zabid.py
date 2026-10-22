# stage_zabid.py - The Souq (Zabid), painted as the Strait and the Coffee Port are: tone fields mapped through colour
# ramps, checker dither between neighbours, light from the upper left, no outlines on scenery.
# One long picture of everything the squad walks past: the road in across the Tihama plain to the old town's gate (a
# Dhanab checkpoint, a spice seller's cart, a tea stall, the white wall and its gatehouse); the spice market inside it
# (stalls under awnings, heaps of spice, tower houses with their carved plaster, balconies, the market's own gate);
# the rooftops (the roofs are the ground here: gaps between the houses, water tanks, washing lines, stair-heads); and
# the covered market, a long vaulted hall, where the souq's Great Scale stands. Cut into strips for the game; a foreground
# that passes close to the lens; a hazy afternoon sky, Zabid's skyline far off, and the plain, all of which wrap.
# Where the ground and the tops of things are is recorded as it is painted (GROUND, PLATS, INFO), so the level can be
# checked against the picture (unit8.js).
import numpy as np
from scipy import ndimage as ndi
from paint import *
import props as P
import stage as ST
import stage_long as SL
import stage_mocha as SM

SW, SH = 468, 216
WORLD = 4864
TG, SS, RT, CM = 0, 1280, 2560, 3880        # the town gate, the spice stalls, the rooftops, the covered market
WALK = 184                                   # where feet land, but on the rooftops
HORIZON = ST.HORIZON
WALLB = 160                                  # inside, where the back walls meet the street

# ------------------------------------------------------------------ colour ramps (dark to pale)
LIME = SM.LIME                                                                                                   # lime plaster
BRICK = ramp(['#1e0c06', '#3e1a0c', '#622c14', '#86401e', '#a8582c', '#c4743e', '#dc9458', '#eeb47c'], 16)       # Zabid's fired brick
DUST = ramp(['#2a1c10', '#4e3820', '#76583a', '#9c7c56', '#bc9c74', '#d6ba92', '#ead4b0', '#f8ecd4'], 18)        # the road
EARTH = SM.EARTH
TEAK = SM.TEAK
IRON = SM.IRON
SOOT = SM.SOOT
SACK = SM.SACK
CORAL = SM.CORAL
CLOTH_R, CLOTH_B = SM.CLOTH_R, SM.CLOTH_B
CLOTH_Y = ramp(['#2e1c04', '#5c3a06', '#8c5c0c', '#bc8418', '#dcaa30', '#f0cc5c', '#fae498'], 12)            # saffron awning
CLOTH_G = ramp(['#06180e', '#0e301a', '#1a4c2a', '#2c6a3c', '#4a8a54', '#78ac74', '#acd0a0'], 12)            # green awning
BLUEWOOD = ramp(['#06121e', '#0c2236', '#163a54', '#245674', '#3c7896', '#6a9eb4', '#a4c8d4'], 12)           # painted doors and shutters
CHILLI = ramp(['#200402', '#480a04', '#760e06', '#a41c0c', '#cc3016', '#ea5228', '#f8864c', '#fcb880'], 14)
TURMERIC = ramp(['#2e1a02', '#5e3804', '#8e5a08', '#c08410', '#e4aa20', '#f8cc44', '#fde684'], 12)
PAPRIKA = ramp(['#2a0c02', '#561a04', '#86300a', '#b44c12', '#d8701e', '#f09838', '#f8c070'], 12)
CUMIN = ramp(['#1a1206', '#36280e', '#584218', '#7a5e26', '#9a7c3a', '#bca05a', '#d8c284'], 12)
TANK = ramp(['#060608', '#101014', '#1c1c22', '#2c2c34', '#42424c', '#5e5e6a', '#828290'], 10)               # black plastic water tanks
TIN = ramp(['#141414', '#2a2a2a', '#444444', '#606060', '#7e7e7c', '#a09e98', '#c4c0b6'], 12)                # corrugated iron
PALMW = ramp(['#1a1408', '#3a2e14', '#5e4c24', '#84703a', '#a89456', '#c8b47a', '#e2d2a2'], 14)               # palm-frond matting
GLASS_T = ramp(['#1a2a26', '#2e4a40', '#4a7262', '#76a08a', '#a8c8b0', '#dcecd8'], 8)                        # tea glasses
SKYZ = ramp(['#3a6898', '#4a78a6', '#5e88b2', '#7698ba', '#90a8c0', '#aab6c2', '#c2c4c4', '#d6d0c4', '#e6dcc8', '#f2e8d4', '#faf4e6'], 22)
HAZEZ = ramp(['#6e6c7c', '#868494', '#9e9ca8', '#b4b0b6', '#c8c2c2', '#d8d0ca', '#e6ded2', '#f2ecde', '#fcf8ee'], 16)
PLAIN = ramp(['#4c4a3a', '#66624a', '#82785a', '#9c8e6a', '#b4a47e', '#c8b892', '#dacaa6', '#eadcbc'], 16)
SCRUB = ramp(['#141c0c', '#24321a', '#3a4c26', '#546a36', '#72884a', '#94a866', '#b8c48c'], 10)
FIRE = P.FIRE

PLATS = {}            # id -> [[x, y], ...] as painted
INFO = {}             # anything else the level needs to know (doors, pits, barricades, stalls)


def plat(pid, pts):
    PLATS[pid] = [[int(x), int(y)] for x, y in pts]


put_tone = SM.put_tone
soft_shadow = SM.soft_shadow
shade_box = SM.shade_box
crate_tone = SM.crate_tone
sack_tone = SM.sack_tone
glow = SM.glow
lantern_glass = SM.lantern_glass


# ------------------------------------------------------------------ the ground: flat but for the rooftops
# heights from x on (piecewise constant; the game samples every 4 px and joins the samples with straight lines, so a
# jump between two samples is a wall). On the rooftops a step of more than 7 px is a wall to walk into, a drop off one
# is a fall; the gaps between the houses drop to a lower shed roof, deep enough to need a jump to get out.
GROUND_SET = [
    (0, WALK),
    # the stair up beside the last house of the market: six steps
    (2492, 178), (2504, 172), (2516, 166), (2528, 160), (2540, 155), (2552, 150),
    (2764, 194),                     # gap 1
    (2800, 144),                     # roof B
    (2988, 196),                     # gap 2
    (3016, 140),                     # roof C
    (3228, 152),                     # roof D (a drop of twelve)
    (3296, 194),                     # gap 3
    (3336, 146),                     # roof E
    (3548, 150),                     # roof F
    # the stair down into the covered market's yard
    (3628, 156), (3640, 162), (3652, 168), (3664, 174), (3676, 179), (3688, WALK),
]
PITS = [[2762, 2798], [2986, 3014], [3294, 3334]]
ROOFS = [(2552, 2764, 150), (2800, 2988, 144), (3016, 3228, 140), (3228, 3296, 152), (3336, 3548, 146), (3548, 3628, 150)]


def ground_samples():
    ys = []
    for i in range(WORLD // 4 + 1):
        x = i * 4
        y = WALK
        for x0, yy in GROUND_SET:
            if x0 <= x:
                y = yy
        ys.append(int(y))
    return ys


GS = ground_samples()


def gy(x):
    """The ground's height at x, as the game works it out."""
    i = x / 4.0
    n = len(GS) - 1
    if i <= 0:
        return GS[0]
    if i >= n:
        return GS[n]
    a = int(np.floor(i))
    f = i - a
    return GS[a] * (1 - f) + GS[a + 1] * f


# ------------------------------------------------------------------ small painters
def road(L, x0, x1, ytop=146, seed=3):
    """The road in: beaten dust, the ruts of carts and trucks along the walk line, stones and scraps, the verge at the
    back where the plain begins (a little scrub, pale in the glare)."""
    w = x1 - x0
    h = SH - ytop
    yy, xx = np.mgrid[0:h, 0:w]
    sy = yy + ytop
    X = xx + x0
    depth = np.clip((sy - ytop) / float(SH - ytop), 0, 1)
    H = fbm((h, w), seed, 40, 5, octaves=3)
    lit = light(ndi.gaussian_filter(H, 1.0), -0.6, -0.8, 5.0)
    grit = fbm((h, w), seed + 1, 1.3, 0.7, octaves=2) - 0.5
    tone = 0.66 - 0.20 * depth + 0.14 * np.clip(lit, -1, 1) + 0.08 * grit
    far = np.clip(1 - (sy - ytop) / 12.0, 0, 1)
    tone = tone * (1 - 0.45 * far) + 0.80 * 0.45 * far
    for ty, wd in ((178, 3), (192, 4)):                                   # ruts
        band = np.abs(sy - ty + 1.5 * np.sin(X / 140.0)) <= wd
        tread = ((X // 3) % 3 == 0)
        tone = np.where(band, tone - 0.07 - 0.04 * tread, tone)
        tone = np.where(np.abs(sy - ty - wd - 1 + 1.5 * np.sin(X / 140.0)) < 0.6, tone + 0.06, tone)
    G = Layer(w, h)
    G.put(toned(np.clip(tone, 0.05, 1), DUST, dither=0.5, x0=x0), np.ones((h, w), bool))
    L.paste(G, x0, ytop)
    r = rng(seed + 3)
    for k in range(int(w / 12)):
        x = int(r.uniform(x0, x1 - 2))
        y = int(r.uniform(ytop + 6, SH - 2))
        for (dx, dy, c) in ((0, 0, (138, 116, 92)), (1, 0, (176, 152, 120)), (0, 1, (84, 66, 50)), (1, 1, (110, 90, 70))):
            L.rgb[y + dy, x + dx] = c
    # the verge: tufts of scrub along the back edge
    S = Tone(L.w, L.h)
    for k in range(int(w / 9)):
        x = int(r.uniform(x0, x1 - 6))
        hh = int(r.integers(2, 6))
        for i in range(-3, 4):
            for j in range(hh - abs(i)):
                S.px(x + i, ytop + 1 - j, 0.30 + 0.30 * (i < 0) + 0.10 * (j == hh - abs(i) - 1))
    put_tone(L, S, SCRUB, dither=0.3)


def paving(L, x0, x1, ytop, seed=5, base=0.60):
    """Inside the walls: old stone paving, worn and dusty (the Coffee Port's quay paving, in limestone)."""
    SM.paving(L, x0, x1, ytop, seed=seed, base=base)


def merlons(T, x0, x1, top, t=0.90, kind='step'):
    """Zabid's crenellation along a parapet: little stepped teeth ('step') or pointed ones ('point')."""
    x = x0
    while x < x1 - 3:
        if kind == 'point':
            for j in range(4):
                T.rect(x + j // 2, top - j, x + 4 - j // 2, top - j, t - 0.04 * j)
            x += 7
        else:
            T.rect(x, top - 3, x + 3, top - 1, t)
            T.rect(x + 1, top - 5, x + 2, top - 4, t)
            x += 7


def stucco_band(L, x0, x1, y, h=5, seed=1, kind=0):
    """A band of carved plaster: the patterns Zabid's houses are known for, lozenges and zigzags in relief."""
    T = Tone(L.w, L.h)
    for x in range(x0, x1):
        for j in range(h):
            u = (x - x0)
            if kind == 0:
                d = abs(((u + j) % 8) - 4) + abs(j - h // 2)
                t = 0.92 if d < 2 else (0.62 if d < 3 else 0.80)
            elif kind == 1:
                z = (u // 2 + j) % 6
                t = 0.94 if z in (0, 1) else (0.58 if z == 3 else 0.78)
            else:
                t = 0.90 if (u % 6 in (0, 1)) or j in (0, h - 1) else 0.66
            T.px(x, y + j, t)
    put_tone(L, T, LIME, dither=0.2)


def brick_face(L, x0, x1, y0, y1, seed=1, lit=0.0):
    """Fired brick, laid in courses with lime joints (Zabid's houses show it where the plaster stops)."""
    T = Tone(L.w, L.h)
    for y in range(y0, y1):
        course = ((y - y0) // 3) % 2
        for x in range(x0, x1):
            joint = ((y - y0) % 3 == 0) or ((x + 4 * course) % 8 == 0)
            t = 0.58 + lit - 0.18 * joint - 0.10 * (x - x0) / max(1.0, x1 - x0) + 0.04 * (((x * 7 + y * 5) % 11) == 0)
            T.px(x, y, t)
    put_tone(L, T, BRICK, dither=0.3)


def shutters(L, x, y, w=12, h=16, open_=True, paint=BLUEWOOD, seed=1):
    """A window with painted wooden shutters, open or shut; a lime frame round it."""
    F = Tone(L.w, L.h)
    for j in range(-2, h + 2):
        for i in range(-2, w + 2):
            if i < 0 or j < 0 or i >= w or j >= h:
                F.px(x + i, y + j, 0.94 if (i < 0 or j < 0) else 0.62)
    put_tone(L, F, LIME, dither=0)
    D = Tone(L.w, L.h)
    D.rect(x, y, x + w - 1, y + h - 1, 0.10)
    put_tone(L, D, SOOT, dither=0.4)
    S = Tone(L.w, L.h)
    if open_:
        for j in range(h):
            S.px(x - 4, y + j, 0.56 - 0.1 * (j % 4 == 0))
            S.px(x - 3, y + j, 0.40)
            S.px(x + w + 2, y + j, 0.50 - 0.1 * (j % 4 == 0))
            S.px(x + w + 3, y + j, 0.34)
    else:
        for j in range(h):
            for i in range(w):
                S.px(x + i, y + j, 0.52 - 0.18 * (i == w // 2) + 0.10 * (j % 4 == 0) - 0.06 * (i > w // 2))
    put_tone(L, S, paint, dither=0.3)


def mashrabiya(L, x, y, w=20, h=22, seed=1):
    """A wooden window bay jutting out on brackets, its screen of turned lattice (a rawshan)."""
    T = Tone(L.w, L.h)
    for j in range(h):
        for i in range(w):
            edge = i in (0, w - 1) or j in (0, h - 1)
            lat = ((i + j) % 3 == 0) or ((i - j) % 3 == 0)
            t = 0.70 if edge else (0.46 if lat else 0.20)
            T.px(x + i, y + j, t - 0.10 * (i > w * 0.65))
    T.rect(x - 2, y - 2, x + w + 1, y - 1, 0.84)
    T.rect(x - 1, y + h, x + w, y + h + 1, 0.56)
    for k in range(4):                                          # the brackets under it
        T.rect(x + 2 + k, y + h + 2 + k, x + 3 + k, y + h + 2 + k, 0.40)
        T.rect(x + w - 4 - k, y + h + 2 + k, x + w - 3 - k, y + h + 2 + k, 0.36)
    put_tone(L, T, TEAK, dither=0.3)


def house_door(L, x, w=16, h=30, base=WALLB, paint=BLUEWOOD, seed=1, open_=False):
    """A house door: a carved plaster surround, a little arch over it, the leaves painted (or one swung open on the
    dark: men come out of these)."""
    T = Tone(L.w, L.h)
    y0 = base - h
    for j in range(-6, h):
        for i in range(-4, w + 4):
            inside = 0 <= i < w and j >= 0
            if inside:
                continue
            arch = j < 0 and abs(i - (w - 1) / 2.0) > (w / 2.0 + 4) - (6 + j) * 0.9
            if arch:
                continue
            T.px(x + i, y0 + j, 0.92 - 0.24 * (i >= w) + (0.06 if (i + j) % 4 == 0 else 0))
    put_tone(L, T, LIME, dither=0.3)
    D = Tone(L.w, L.h)
    if open_:
        D.rect(x, y0, x + w - 1, base - 1, 0.10)
        for j in range(h):
            D.px(x + w - 1, y0 + j, 0.20)
        put_tone(L, D, SOOT, dither=0.4)
        F = Tone(L.w, L.h)
        for j in range(h):
            for i in range(6):
                F.px(x - 6 + i, y0 + j + i // 3, 0.52 - 0.04 * i + 0.10 * ((j % 7) == 0))
        put_tone(L, F, paint, dither=0.3)
    else:
        for j in range(h):
            for i in range(w):
                D.px(x + i, y0 + j, 0.50 - 0.20 * (i == w // 2) + 0.10 * ((j % 7) == 0) - 0.08 * (i > w // 2) + 0.24 * ((i % 5 == 2) and (j % 7 == 3)))
        put_tone(L, D, paint, dither=0.3)
    INFO.setdefault('doors', []).append(x + w // 2)


def awning(L, x0, x1, top, depth=12, rmp=CLOTH_R, stripes=8, seed=1, sag=3):
    """A cloth awning over a stall, on two poles: striped, sagging between them, its scalloped edge in front."""
    A = Tone(L.w, L.h)
    W_ = Tone(L.w, L.h)
    for px_ in (x0 + 2, x1 - 3):
        for y in range(top, 182):
            W_.px(px_, y, 0.56)
            W_.px(px_ + 1, y, 0.32)
    for x in range(x0, x1):
        sg = sag * np.sin((x - x0) / float(max(1, x1 - x0 - 1)) * np.pi)
        for y in range(top, int(top + depth + sg)):
            st = ((x - x0) // stripes) % 2
            A.px(x, y, 0.72 - 0.34 * (y - top) / float(depth) + 0.14 * st)
        if (x - x0) % 6 < 4:
            A.px(x, int(top + depth + sg), 0.42)
    put_tone(L, A, rmp, dither=0.35)
    put_tone(L, W_, TEAK, dither=0.3)
    # the shade it throws on the wall behind
    shade_box(L, x0 + 6, top + depth + 4, x1 + 4, min(WALLB, top + depth + 30), 0.84)


def spice_heap(L, cx, base, w=14, rmp=CHILLI, seed=1):
    """A cone of ground spice heaped in a basket, the way the souq shows it off: a woven basket, the heap pointed and
    lit on its left."""
    Bk = Tone(L.w, L.h)
    for j in range(5):
        half = w // 2 + 1 - (j == 4)
        for i in range(-half, half + 1):
            Bk.px(cx + i, base - 5 + j, 0.62 - 0.08 * j + 0.12 * ((i + j) % 2) - 0.10 * (i > half - 2))
    put_tone(L, Bk, PALMW, dither=0.2)
    S = Tone(L.w, L.h)
    hh = w // 2 + 2
    for j in range(hh):
        half = int((w // 2) * (j + 1) / float(hh))
        for i in range(-half, half + 1):
            u = (i + half) / max(1.0, 2.0 * half)
            S.px(cx + i, base - 5 - hh + j, 0.80 - 0.40 * u - 0.10 * (j / float(hh)) + 0.06 * ((i * 3 + j) % 5 == 0))
    put_tone(L, S, rmp, dither=0.3)


def chilli_string(L, x, y, n=7, seed=1):
    """Dried chillies strung up to hang under an awning."""
    T = Tone(L.w, L.h)
    for k in range(n):
        yy = y + k * 3
        T.px(x + (k % 2), yy, 0.70)
        T.px(x + (k % 2), yy + 1, 0.50)
        T.px(x + (k % 2) + 1, yy + 1, 0.34)
    put_tone(L, T, CHILLI, dither=0)
    S = Tone(L.w, L.h)
    S.rect(x, y - 4, x, y - 1, 0.6)
    put_tone(L, S, PALMW, dither=0)


def stall_counter(L, x0, x1, top, seed=1, goods='spice'):
    """A market counter: planks on trestles, a cloth over the front, goods on top."""
    T = Tone(L.w, L.h)
    crate_tone(T, x0, top, x1 - x0, 182 - top, seed=seed)
    put_tone(L, T, TEAK, dither=0.35)
    C = Tone(L.w, L.h)
    for x in range(x0 + 2, x1 - 2):
        for y in range(top + 2, top + 9):
            C.px(x, y, 0.58 - 0.24 * (y - top - 2) / 7.0 + 0.12 * (((x - x0) // 5) % 2))
    put_tone(L, C, CLOTH_B if seed % 2 else CLOTH_G, dither=0.3)
    soft_shadow(L, x1, x1 + 8, 183, 3)


def spice_sacks_row(L, x0, x1, base, seed=1):
    """Open sacks of spice in a row along the foot of a stall, their mouths rolled down and the colour showing."""
    r = rng(seed)
    x = x0
    k = 0
    cols = (CHILLI, TURMERIC, PAPRIKA, CUMIN)
    while x < x1 - 12:
        w = int(r.integers(11, 15))
        T = Tone(L.w, L.h)
        h = int(r.integers(10, 13))
        for j in range(h):
            for i in range(w):
                u = i / float(w - 1)
                bulge = 1 if j > h // 2 else 0
                if (i == 0 or i == w - 1) and j < 2:
                    continue
                T.px(x + i - bulge * (i == 0), base - h + j, 0.70 - 0.30 * u - 0.10 * (j / float(h)) + 0.08 * (j == 1))
        put_tone(L, T, SACK, dither=0.3)
        S = Tone(L.w, L.h)
        for i in range(1, w - 1):
            hmp = int(2.5 * np.sin(np.pi * i / float(w - 1)))
            for j in range(hmp + 1):
                S.px(x + i, base - h + 1 - j, 0.78 - 0.30 * (i / float(w)) + 0.08 * (j == hmp))
        put_tone(L, S, cols[k % 4], dither=0.2)
        x += w + int(r.integers(1, 3))
        k += 1


def lamp(L, x, y, seed=1):
    """A brass lantern on a bracket."""
    K = Tone(L.w, L.h)
    K.rect(x - 4, y - 6, x, y - 6, 0.5)
    K.rect(x, y - 6, x, y - 4, 0.5)
    K.rect(x - 2, y - 4, x + 2, y - 3, 0.62)
    put_tone(L, K, IRON, dither=0)
    lantern_glass(L, x - 1, y - 2)


def palm_at(L, x, base, height=80, lean=8, seed=1):
    pm, f, bx = P.palm(height=height, lean=lean, seed=seed)
    L.paste(pm, x - bx, base - f)


# ------------------------------------------------------------------ 0: the road to the town gate
def spice_cart(L, x0=420, seed=7):
    """A spice seller's hand cart outside the gate, left where he left it: a box on two big wheels, shafts on the
    ground, open sacks of spice in it and a striped shade over it. Its bed is a step up."""
    T = Tone(L.w, L.h)
    crate_tone(T, x0, 158, 64, 16, seed=seed)
    for wx in (x0 + 14, x0 + 50):
        for a in range(0, 360, 8):
            T.px(wx + 9 * np.cos(np.radians(a)), 174 + 9 * np.sin(np.radians(a)), 0.30 + 0.20 * (a < 180))
            T.px(wx + 8 * np.cos(np.radians(a)), 174 + 8 * np.sin(np.radians(a)), 0.46)
        for a in range(0, 360, 45):
            T.line([(wx, 174), (wx + 8 * np.cos(np.radians(a)), 174 + 8 * np.sin(np.radians(a)))], 0.50)
        T.rect(wx - 1, 173, wx + 1, 175, 0.70)
    for k in range(30):                                       # the shafts, down on the ground
        T.px(x0 - k, 166 + k * 0.5, 0.56)
        T.px(x0 - k, 167 + k * 0.5, 0.36)
    put_tone(L, T, TEAK, dither=0.35)
    soft_shadow(L, x0 + 4, x0 + 70, 183, 3)
    spice_sacks_row(L, x0 + 3, x0 + 62, 158, seed=seed + 1)
    awning(L, x0 - 2, x0 + 66, 118, depth=9, rmp=CLOTH_Y, stripes=6, sag=2)
    plat('cart', [[x0 + 2, 158], [x0 + 62, 158]])


def checkpoint(L, x0=650, seed=11):
    """The Dhanabs' checkpoint on the road: a booth of corrugated iron and plywood with a flat roof (a platform), a
    barrier pole propped up open, sandbags, a stack of tyres, an oil drum for a stove, a plastic chair."""
    T = Tone(L.w, L.h)
    top, base = 128, 182
    for y in range(top, base):
        for x in range(x0, x0 + 52):
            corr = (x % 4 < 2)
            t = 0.56 + 0.12 * corr - 0.22 * (x - x0) / 52.0 - 0.06 * ((y - top) / 54.0)
            T.px(x, y, t)
    for x in range(x0 - 4, x0 + 57):
        T.px(x, top - 1, 0.84)
        T.px(x, top, 0.60)
        T.px(x, top + 1, 0.36)
    put_tone(L, T, TIN, dither=0.3, grain=0.04, seed=seed)
    W = Tone(L.w, L.h)
    W.rect(x0 + 8, top + 10, x0 + 30, top + 24, 0.12)            # its window
    W.rect(x0 + 6, top + 8, x0 + 32, top + 9, 0.80)
    W.rect(x0 + 6, top + 25, x0 + 32, top + 26, 0.54)
    W.rect(x0 + 36, top + 14, x0 + 48, base - 1, 0.40)           # its door, plywood
    W.rect(x0 + 36, top + 14, x0 + 48, top + 14, 0.74)
    put_tone(L, W, TEAK, dither=0.3)
    R = Tone(L.w, L.h)
    for y in range(top, base):
        for x in range(x0, x0 + 52):
            if ((x * 13 + y * 7) % 29 == 0) or (y > top + 30 and (x * 7 + y) % 37 == 0):
                R.px(x, y, 0.40)
    put_tone(L, R, P.RUST, dither=0)
    soft_shadow(L, x0 + 52, x0 + 62, 183, 3)
    plat('booth', [[x0 + 2, top - 1], [x0 + 52, top - 1]])
    # the barrier pole on its post, swung up open
    B = Tone(L.w, L.h)
    px_ = x0 + 70
    B.rect(px_, 150, px_ + 3, 182, 0.50)
    B.rect(px_ - 2, 148, px_ + 5, 151, 0.66)
    for k in range(64):
        a = np.radians(62)
        bx, by = px_ + 2 + k * np.cos(a) * -0.5, 149 - k * np.sin(a)
        stripe = (k // 6) % 2
        B.px(bx, by, 0.92 if stripe else 0.40)
        B.px(bx + 1, by, 0.80 if stripe else 0.30)
    put_tone(L, B, LIME, dither=0)
    Rd = Tone(L.w, L.h)
    for k in range(64):
        if (k // 6) % 2 == 0:
            a = np.radians(62)
            bx, by = px_ + 2 + k * np.cos(a) * -0.5, 149 - k * np.sin(a)
            Rd.px(bx, by, 0.60)
            Rd.px(bx + 1, by, 0.44)
    put_tone(L, Rd, CHILLI, dither=0)
    # sandbags and tyres beside it
    sb, sf = P.sandbags(cols=4, rows=2, seed=seed)
    L.paste(sb, x0 + 84, 183 - sf)
    Ty = Tone(L.w, L.h)
    for k in range(3):
        ty0 = 176 - k * 7 + (k == 2)
        xs = x0 - 28 + (k % 2) * 2
        for x in range(xs, xs + 22):
            u = (x - (xs + 11)) / 11.0
            if abs(u) > 0.98:
                continue
            Ty.px(x, ty0, 0.62 - 0.30 * (u > 0.4))                 # the tyre's shoulder, lit
            for j in range(1, 6):
                tread = ((x + j) % 3 == 0) and 1 <= j <= 4
                Ty.px(x, ty0 + j, 0.30 + 0.14 * (j == 1) - 0.10 * (abs(u) > 0.8) + 0.14 * tread - 0.08 * (u > 0.5))
    put_tone(L, Ty, P.TYRE, dither=0.2)


def tea_stall(L, x0=890, seed=13):
    """A tea seller's lean-to by the gate: palm-frond matting on poles, a brazier with a kettle, a bench, glasses on a
    tray. (The seller himself is in the game, tied behind his counter.)"""
    T = Tone(L.w, L.h)
    for x in range(x0, x0 + 70):
        sg = 2 * np.sin((x - x0) / 69.0 * np.pi)
        for y in range(118, int(126 + sg)):
            T.px(x, y, 0.70 - 0.30 * (y - 118) / 8.0 + 0.10 * ((x + y) % 3 == 0) - 0.08 * ((x // 4) % 2))
        if x % 3 == 0:
            T.px(x, int(126 + sg), 0.40)
            T.px(x, int(127 + sg), 0.30)
    put_tone(L, T, PALMW, dither=0.3)
    Pp = Tone(L.w, L.h)
    for px_ in (x0 + 3, x0 + 66):
        for y in range(120, 183):
            Pp.px(px_, y, 0.56)
            Pp.px(px_ + 1, y, 0.34)
    for x in range(x0 + 34, x0 + 64):                       # the bench
        Pp.px(x, 168, 0.80)
        Pp.px(x, 169, 0.46)
    for lx in (x0 + 36, x0 + 61):
        Pp.rect(lx, 170, lx + 1, 182, 0.40)
    put_tone(L, Pp, TEAK, dither=0.3)
    St = Tone(L.w, L.h)                                     # the brazier and the kettle
    for y in range(170, 182):
        half = 4 - (y > 178)
        for x in range(x0 + 46 - half, x0 + 47 + half):
            St.px(x, y, 0.40 + 0.10 * (y == 170))
    put_tone(L, St, IRON, dither=0.3)
    Fi = Tone(L.w, L.h)
    for x in range(x0 + 43, x0 + 51):
        Fi.px(x, 169, 0.70 + 0.2 * ((x * 3) % 2))
    put_tone(L, Fi, FIRE, dither=0)
    K = Tone(L.w, L.h)
    for j, half in enumerate([2, 3, 4, 4, 4, 3]):
        for i in range(-half, half + 1):
            K.px(x0 + 47 + i, 161 + j, 0.80 - 0.10 * (i + half) / max(1, half))
    for k in range(4):
        K.px(x0 + 42 - k, 163 - k, 0.70)
    put_tone(L, K, SM.COPPER, dither=0.2)
    for k, gx in enumerate((x0 + 52, x0 + 56, x0 + 60)):    # tea glasses on the bench
        L.rgb[165:168, gx:gx + 2] = (196, 228, 210)
        L.rgb[166:168, gx:gx + 2] = (150, 60, 30)
        L.a[165:168, gx:gx + 2] = True
    glow(L, x0 + 47, 170, 26, amt=0.30)


def town_wall(L, x0=930, x1=1196, seed=17):
    """The town's outer wall along the back of the road: lime plaster over mud brick, flaking at the foot, a drain
    spout, the stepped crenellation along the top; a round tower where it meets the gatehouse."""
    w = x1 - x0
    top, base = 66, 150
    h = base - top
    yy, xx = np.mgrid[0:h, 0:w]
    v = yy / float(h)
    X = xx + x0
    tone = 0.80 - 0.10 * v + 0.05 * (fbm((h, w), seed, 30, 20, octaves=3) - 0.5)
    tone -= 0.26 * np.clip((v - 0.70) / 0.30, 0, 1) ** 1.4
    tone -= 0.10 * np.clip(fbm((h, w), seed + 1, 3, 40, octaves=2) - 0.55, 0, 1) * 3
    tone += 0.04 * (fbm((h, w), seed + 2, 1.2, 0.8, octaves=2) - 0.5)
    G = Layer(w, h)
    G.put(toned(np.clip(tone, 0.04, 1), LIME, dither=0.5, x0=x0), np.ones((h, w), bool))
    pat = (fbm((h, w), seed + 3, 16, 9, octaves=3) > 0.80) & (v > 0.30)
    course = (yy // 3) % 2
    st = 0.52 - 0.18 * ((yy % 3) == 0) - 0.16 * (((X + 4 * course) % 8) == 0) - 0.12 * v
    S_ = Layer(w, h)
    S_.put(toned(np.clip(st, 0, 1), BRICK, dither=0.4, x0=x0), pat)
    G.paste(S_)
    L.paste(G, x0, top)
    T = Tone(L.w, L.h)
    merlons(T, x0, x1, top - 1, 0.92)
    for x in range(x0, x1):
        T.px(x, top, 0.96)
        T.px(x, top + 1, 0.70)
    for row in (top + 16, top + 40):                       # the holes the builders' poles went in, in rows
        for hx in range(x0 + 8, x1 - 4, 15):
            T.rect(hx, row, hx + 1, row + 1, 0.36)
    for bx in range(x0 + 44, x1 - 8, 88):                  # shallow buttresses, lit on their left
        for y in range(top + 8, base):
            T.px(bx, y, 0.96)
            T.px(bx + 7, y, 0.62)
    for x in range(x0, x1):                                # the plinth, darker, where the road's dust has climbed it
        for y in range(base - 9, base):
            T.px(x, y, 0.62 - 0.03 * (y - base + 9) + 0.04 * (((x * 5 + y * 3) % 7) == 0))
        T.px(x, base - 10, 0.84)
    for sx in (x0 + 60, x0 + 170):                         # drain spouts
        T.rect(sx, top + 6, sx + 5, top + 7, 0.40)
        T.rect(sx + 4, top + 8, sx + 5, top + 8, 0.30)
    put_tone(L, T, LIME, dither=0.2)
    # the dark streaks under the spouts
    for sx in (x0 + 60, x0 + 170):
        shade_box(L, sx + 3, top + 9, sx + 6, top + 40, 0.86)


def wall_walk(L, x0=1096, x1=1180, y=120, seed=19):
    """A wooden scaffold the Dhanabs have put up against the wall to shoot over it: a planked deck (a platform), posts,
    braces, and crates to climb up by."""
    T = Tone(L.w, L.h)
    for x in range(x0, x1 + 1):
        T.px(x, y, 0.92)
        T.px(x, y + 1, 0.70)
        T.px(x, y + 2, 0.46)
        T.px(x, y + 3, 0.30 if (x - x0) % 10 else 0.56)
        T.px(x, y - 12, 0.66)
        if (x - x0) % 14 == 0:
            T.rect(x, y - 12, x, y - 1, 0.54)
    for px_ in (x0 + 4, x0 + 40, x1 - 4):
        for yy in range(y + 4, 183):
            T.px(px_, yy, 0.62)
            T.px(px_ + 1, yy, 0.42)
            T.px(px_ + 2, yy, 0.26)
    T.line([(x0 + 6, y + 8), (x0 + 40, 176)], 0.40)
    T.line([(x0 + 42, y + 8), (x1 - 6, 176)], 0.34)
    put_tone(L, T, TEAK, dither=0.3, grain=0.03, seed=seed)
    CT = Tone(L.w, L.h)
    crate_tone(CT, x0 - 50, 166, 26, 17, seed=seed + 1)
    crate_tone(CT, x0 - 28, 146, 28, 20, seed=seed + 2)
    crate_tone(CT, x0 - 26, 166, 24, 17, seed=seed + 3)
    put_tone(L, CT, TEAK, dither=0.35)
    soft_shadow(L, x0 - 2, x0 + 8, 183, 3)
    plat('wc1', [[x0 - 50, 166], [x0 - 26, 166]])
    plat('wc2', [[x0 - 28, 146], [x0, 146]])
    plat('wallwalk', [[x0, y], [x1, y]])


def gatehouse(L, x0=1196, x1=1246, seed=23):
    """The town gate: the wall cut through, thick, lime over brick, an arched passage through it (where the Dhanabs
    have piled their barricade), the gate's great doors pinned back inside, and a round tower beside it standing up
    over everything with its crenellation."""
    T = Tone(L.w, L.h)
    D = Tone(L.w, L.h)
    w = x1 - x0
    cx_ = x0 + w / 2.0
    aw = 21.0                                            # the arch's half-width
    spring = 128                                         # where the arch springs
    for x in range(x0, x1):
        u = (x - x0) / float(w - 1)
        for y in range(30, SH):
            inside = abs(x - cx_) < aw and (y > spring or (x - cx_) ** 2 + (y - spring) ** 2 < aw ** 2)
            if inside:
                if y < WALK + 2:
                    D.px(x, y, 0.10 + 0.12 * (y - spring + aw) / 80.0 + 0.06 * (abs(x - cx_) > aw - 3))
                continue
            course = (y // 6) % 2
            stone = ((x + 7 * course) % 12 == 0) or (y % 6 == 0)
            t = 0.84 - 0.30 * u - 0.10 * (y > 172) - 0.06 * stone * (abs(u - 0.5) < 0.44)
            if x == x0:
                t += 0.06
            if x == x1 - 1:
                t -= 0.16
            T.px(x, y, t)
    merlons(T, x0 - 2, x1 + 2, 29, 0.92, kind='point')
    put_tone(L, T, LIME, dither=0.4, grain=0.03, seed=seed)
    put_tone(L, D, SOOT, dither=0.5)
    # the arch's voussoirs, picked out in brick
    B = Tone(L.w, L.h)
    for a in np.linspace(np.pi, 2 * np.pi, 40):
        for rr in (aw + 1, aw + 2):
            B.px(cx_ + rr * np.cos(a), spring + rr * np.sin(a), 0.62 if (int(a * 20) % 2) else 0.40)
    put_tone(L, B, BRICK, dither=0)
    stucco_band(L, x0 + 2, x1 - 2, 60, h=5, kind=0)
    # the round tower behind, to the left of the passage: it stands up over the wall
    R = Tone(L.w, L.h)
    tx0, tx1 = x0 - 64, x0 - 4
    for x in range(tx0, tx1):
        u = (x - tx0) / float(tx1 - tx0 - 1)
        s_ = np.sin(u * np.pi)
        for y in range(18, 66):
            t = 0.58 + 0.36 * (1 - u) ** 0.6 * s_ - 0.28 * u ** 2 + 0.03 * (((x * 5 + y * 3) % 7) == 0)
            R.px(x, y, t)
    merlons(R, tx0, tx1, 17, 0.90)
    for wy in (30, 46):                                   # arrow slits
        R.rect(tx0 + 22, wy, tx0 + 23, wy + 7, 0.14)
    put_tone(L, R, LIME, dither=0.4)
    # the doors, swung back against the passage walls (seen edge on beyond the barricade)
    F = Tone(L.w, L.h)
    for y in range(140, WALK):
        F.px(x1 - 3, y, 0.50)
        F.px(x1 - 2, y, 0.34)
        if y % 9 == 0:
            F.px(x1 - 3, y, 0.80)
    put_tone(L, F, BLUEWOOD, dither=0)
    INFO['gate'] = [x0, x1]


def town_gate(L):
    road(L, TG, 1196, 146, seed=3)
    paving(L, 1196, SS + 8, 150, seed=7)                 # (inside the gate the street begins)
    for x, (h_, lean, sd) in ((96, (78, 8, 41)), (300, (64, -6, 43)), (842, (84, 10, 45))):
        palm_at(L, x, 152, h_, lean, sd)
    town_wall(L)
    spice_cart(L)
    checkpoint(L)
    tea_stall(L)
    wall_walk(L)
    gatehouse(L)
    # the defenders' step behind the barricade
    STp = Tone(L.w, L.h)
    crate_tone(STp, 1236, 176, 56, 8, seed=29)
    put_tone(L, STp, TEAK, dither=0.3)
    plat('b1back', [[1236, 176], [1290, 176]])
    INFO.setdefault('bars', {})['b1'] = dict(x0=1196, top=150, x1=1290)


# ------------------------------------------------------------------ 1: the spice stalls
def house_front(L, x0, x1, top, seed=1, brick_top=0, floors=(), wins=(), mash=(), base=WALLB, shade=0.0):
    """A tower house seen from the street: lime plaster over brick, the top storey's brick left bare and banded with
    carved plaster (the Zabid way), rows of windows, a stepped parapet, darker toward the street."""
    w = x1 - x0
    h = base - top
    yy, xx = np.mgrid[0:h, 0:w]
    v = yy / float(h)
    X = xx + x0
    tone = 0.82 - 0.10 * v + 0.05 * (fbm((h, w), seed, 26, 18, octaves=3) - 0.5) - shade
    tone -= 0.24 * np.clip((v - 0.72) / 0.28, 0, 1) ** 1.4
    tone -= 0.08 * np.clip(fbm((h, w), seed + 1, 3, 34, octaves=2) - 0.55, 0, 1) * 3
    tone += 0.04 * (fbm((h, w), seed + 2, 1.2, 0.8, octaves=2) - 0.5)
    tone = np.where(xx == 0, tone + 0.06, tone)
    tone = np.where(xx >= w - 2, tone - 0.18, tone)
    G = Layer(w, h)
    G.put(toned(np.clip(tone, 0.04, 1), LIME, dither=0.5, x0=x0), np.ones((h, w), bool))
    pat = (fbm((h, w), seed + 3, 14, 8, octaves=3) > 0.86) & (v > 0.35)
    course = (yy // 3) % 2
    st = 0.52 - 0.18 * ((yy % 3) == 0) - 0.16 * (((X + 4 * course) % 8) == 0) - 0.12 * v
    S_ = Layer(w, h)
    S_.put(toned(np.clip(st, 0, 1), BRICK, dither=0.4, x0=x0), pat)
    G.paste(S_)
    L.paste(G, x0, top)
    if brick_top:
        brick_face(L, x0 + 1, x1 - 2, top + 3, top + brick_top, seed=seed)
        stucco_band(L, x0 + 1, x1 - 2, top + brick_top, h=4, kind=seed % 3)
    for fy in floors:
        stucco_band(L, x0 + 1, x1 - 2, fy, h=3, kind=(seed + fy) % 3)
    T = Tone(L.w, L.h)
    merlons(T, x0, x1, top - 1, 0.94, kind='step' if seed % 2 else 'point')
    for x in range(x0, x1):
        T.px(x, top, 0.96)
        T.px(x, top + 1, 0.74)
        T.px(x, top + 2, 0.52)
    put_tone(L, T, LIME, dither=0.2)
    for (wx, wy, ww, wh, op) in wins:
        shutters(L, wx, wy, ww, wh, open_=op, seed=seed + wx)
    for (mx, my, mw, mh) in mash:
        mashrabiya(L, mx, my, mw, mh, seed=seed + mx)


def balcony(L, x0, x1, y, seed=1):
    """A wooden balcony along a house front: planked floor (a platform), a turned rail, brackets under it."""
    T = Tone(L.w, L.h)
    for x in range(x0, x1 + 1):
        T.px(x, y, 0.92)
        T.px(x, y + 1, 0.70)
        T.px(x, y + 2, 0.46)
        T.px(x, y + 3, 0.26)
        T.px(x, y - 12, 0.70)
        T.px(x, y - 11, 0.46)
        if (x - x0) % 4 == 0:
            T.rect(x, y - 10, x, y - 1, 0.56 - 0.12 * ((x - x0) % 8 == 4))
        if (x - x0) % 22 == 6:
            for k in range(7):
                T.px(x + k // 2, y + 4 + k, 0.40)
                T.px(x + 1 + k // 2, y + 4 + k, 0.28)
    put_tone(L, T, TEAK, dither=0.3, grain=0.03, seed=seed)
    shade_box(L, x0, y + 4, x1 + 1, y + 10, 0.80)


def market_gate(L, x0=2388, x1=2440, seed=31):
    """The spice market's own gate across the street: a thick arch of brick and lime, a carved band over it, a wooden
    gallery on top, the street running on through it. (The Dhanabs have piled their barricade in it.)"""
    T = Tone(L.w, L.h)
    D = Tone(L.w, L.h)
    w = x1 - x0
    cx_ = x0 + w / 2.0
    aw, spring = 21.0, 132
    for x in range(x0, x1):
        u = (x - x0) / float(w - 1)
        for y in range(36, SH):
            inside = abs(x - cx_) < aw and (y > spring or (x - cx_) ** 2 + (y - spring) ** 2 < aw ** 2)
            if inside:
                if y < WALK + 2:
                    D.px(x, y, 0.12 + 0.10 * (y - spring + aw) / 80.0)
                continue
            course = (y // 6) % 2
            stone = ((x + 7 * course) % 12 == 0) or (y % 6 == 0)
            t = 0.84 - 0.30 * u - 0.10 * (y > 172) - 0.06 * stone * (abs(u - 0.5) < 0.44)
            if x == x1 - 1:
                t -= 0.16
            T.px(x, y, t)
    merlons(T, x0 - 2, x1 + 2, 35, 0.92, kind='step')
    put_tone(L, T, LIME, dither=0.4, grain=0.03, seed=seed)
    put_tone(L, D, SOOT, dither=0.5)
    B = Tone(L.w, L.h)
    for a in np.linspace(np.pi, 2 * np.pi, 40):
        for rr in (aw + 1, aw + 2):
            B.px(cx_ + rr * np.cos(a), spring + rr * np.sin(a), 0.62 if (int(a * 20) % 2) else 0.40)
    put_tone(L, B, BRICK, dither=0)
    brick_face(L, x0 + 2, x1 - 2, 44, 62, seed=seed)
    stucco_band(L, x0 + 2, x1 - 2, 62, h=5, kind=1)
    stucco_band(L, x0 + 2, x1 - 2, 40, h=3, kind=2)
    INFO['mgate'] = [x0, x1]


def stall(L, x0, x1, top=128, cloth=CLOTH_R, seed=1, heaps=3, counter=True, strings=2):
    """A spice stall against a house front: an awning, chillies strung under it, heaps of spice on the counter in
    baskets, open sacks along the foot."""
    awning(L, x0, x1, top, depth=11, rmp=cloth, stripes=7, sag=3)
    for k in range(strings):
        chilli_string(L, x0 + 10 + k * ((x1 - x0 - 20) // max(1, strings - 1) if strings > 1 else 0), top + 15, n=6)
    if counter:
        stall_counter(L, x0 + 6, x1 - 6, 164, seed=seed)
        cols = (CHILLI, TURMERIC, PAPRIKA, CUMIN, CHILLI)
        for k in range(heaps):
            cx_ = x0 + 14 + k * ((x1 - x0 - 28) // max(1, heaps - 1))
            spice_heap(L, cx_, 164, w=12, rmp=cols[(k + seed) % 5], seed=seed + k)
    else:
        spice_sacks_row(L, x0 + 6, x1 - 6, 182, seed=seed)


def spice_stalls(L):
    paving(L, SS + 8, 2500, WALLB, seed=9, base=0.58)
    # the houses along the back, left to right (and a little alley between two of them)
    H = [
        (1246, 1384, 38, 11, (88, 118), [(1262, 66, 10, 14, True), (1300, 66, 10, 14, False), (1262, 98, 10, 14, True), (1340, 98, 10, 14, True)], []),
        (1384, 1524, 18, 15, (70, 102), [(1400, 44, 10, 14, True), (1490, 44, 10, 14, True), (1400, 80, 10, 14, False)], [(1440, 76, 22, 22)]),
        (1524, 1664, 48, 9, (96,), [(1540, 66, 10, 14, True), (1610, 66, 10, 14, True), (1640, 100, 10, 14, False)], []),
        (1664, 1784, 30, 13, (80, 110), [(1680, 54, 10, 14, True), (1750, 54, 10, 14, True), (1750, 88, 10, 14, True)], [(1700, 82, 20, 20)]),
        (1784, 1904, 20, 17, (64, 96), [(1798, 40, 10, 14, True), (1870, 40, 10, 14, False), (1880, 72, 10, 14, True)], [(1820, 66, 22, 22)]),
        (1904, 2044, 44, 9, (92,), [(1920, 62, 10, 14, True), (2010, 62, 10, 14, True), (1920, 100, 10, 14, True)], []),
        (2044, 2184, 26, 13, (78, 108), [(2060, 52, 10, 14, False), (2150, 52, 10, 14, True), (2060, 86, 10, 14, True)], [(2100, 80, 20, 20)]),
        (2184, 2328, 34, 11, (84,), [(2200, 58, 10, 14, True), (2300, 58, 10, 14, True)], [(2240, 52, 22, 22)]),
        (2328, 2388, 50, 7, (100,), [(2344, 68, 10, 14, True)], []),
    ]
    for i, (a, b, top, bt, fl, wins, mash) in enumerate(H):
        house_front(L, a, b, top, seed=41 + i, brick_top=bt, floors=fl, wins=wins, mash=mash, shade=0.02 * (i % 2))
    # doors: closed ones, and the open ones men come out of
    for (dx, op, pnt) in ((1300, False, BLUEWOOD), (1470, True, BLUEWOOD), (1600, False, CLOTH_G), (1708, True, BLUEWOOD),
                          (1964, True, CLOTH_G), (2010, False, BLUEWOOD), (2290, True, BLUEWOOD)):
        house_door(L, dx - 8, open_=op, paint=pnt, seed=dx)
    # balconies: the first over the street door, the second over the middle of the market, the third by the gate
    balcony(L, 1420, 1500, 118, seed=51)
    plat('balc1', [[1420, 118], [1500, 118]])
    balcony(L, 1790, 1880, 112, seed=52)
    plat('balc2', [[1790, 112], [1880, 112]])
    balcony(L, 2236, 2304, 120, seed=53)
    plat('balc3', [[2236, 120], [2304, 120]])
    # the stalls, and what to climb by
    stall(L, 1256, 1330, 130, CLOTH_R, seed=61, heaps=3)
    stall(L, 1530, 1600, 128, CLOTH_G, seed=62, heaps=0, counter=False)            # (the shopkeeper's: his counter is in the game)
    stall(L, 1620, 1690, 132, CLOTH_Y, seed=63, heaps=3)
    stall(L, 1910, 1960, 130, CLOTH_B, seed=64, heaps=2)
    stall(L, 2060, 2150, 126, CLOTH_R, seed=65, heaps=0, counter=False)            # (the second shopkeeper's)
    stall(L, 2310, 2380, 134, CLOTH_Y, seed=66, heaps=3)
    CT = Tone(L.w, L.h)
    crate_tone(CT, 1380, 166, 28, 17, seed=71)            # up to the first balcony
    crate_tone(CT, 1398, 144, 26, 22, seed=72)
    crate_tone(CT, 1752, 164, 28, 19, seed=73)            # up to the second
    crate_tone(CT, 1768, 140, 26, 24, seed=74)
    crate_tone(CT, 2200, 166, 26, 17, seed=75)            # up to the third
    crate_tone(CT, 2214, 146, 24, 20, seed=76)
    put_tone(L, CT, TEAK, dither=0.35)
    for a in (1408, 1780, 2226):
        soft_shadow(L, a, a + 10, 183, 3)
    plat('cr1', [[1380, 166], [1408, 166]])
    plat('cr2', [[1398, 144], [1424, 144]])
    plat('cr3', [[1752, 164], [1780, 164]])
    plat('cr4', [[1768, 140], [1794, 140]])
    plat('cr5', [[2200, 166], [2226, 166]])
    plat('cr6', [[2214, 146], [2238, 146]])
    # lanterns on brackets along the fronts
    for lx in (1376, 1612, 1900, 2180):
        lamp(L, lx, 112)
    # spilled spice along the foot of the stalls
    r = rng(5)
    for k in range(260):
        x = int(r.uniform(SS, 2480))
        y = int(r.uniform(WALLB + 3, 200))
        col = [CHILLI[6], TURMERIC[5], PAPRIKA[5], CUMIN[4]][k % 4]
        L.rgb[y, x] = col
    market_gate(L)
    STp = Tone(L.w, L.h)
    crate_tone(STp, 2436, 176, 52, 8, seed=79)
    put_tone(L, STp, TEAK, dither=0.3)
    plat('b2back', [[2436, 176], [2488, 176]])
    INFO.setdefault('bars', {})['b2'] = dict(x0=2390, top=150, x1=2488)


# ------------------------------------------------------------------ 2: the rooftops
def roof_house(L, x0, x1, y, seed=1, back=8, wins=True, left_gap=False, right_gap=False):
    """A house seen from its own roof's level: the roof's edge (where feet go), the parapet along its far side, and
    its front falling away below to the bottom of the picture, windows and carved bands in it. A gap beside it shows
    its side wall in shadow."""
    w = x1 - x0
    # the front, from the roof edge down
    top = y + 3
    h = SH - top
    yy, xx = np.mgrid[0:h, 0:w]
    v = yy / float(h)
    X = xx + x0
    tone = 0.74 - 0.18 * v + 0.05 * (fbm((h, w), seed, 26, 18, octaves=3) - 0.5)
    tone -= 0.06 * np.clip(fbm((h, w), seed + 1, 3, 34, octaves=2) - 0.55, 0, 1) * 3
    tone += 0.04 * (fbm((h, w), seed + 2, 1.2, 0.8, octaves=2) - 0.5)
    G = Layer(w, h)
    G.put(toned(np.clip(tone, 0.04, 1), LIME, dither=0.5, x0=x0), np.ones((h, w), bool))
    L.paste(G, x0, top)
    brick_face(L, x0, x1, top, top + 7, seed=seed, lit=-0.04)
    stucco_band(L, x0, x1, top + 7, h=4, kind=seed % 3)
    if wins:
        r = rng(seed)
        for wx in range(x0 + 14 + int(r.integers(0, 10)), x1 - 20, int(r.integers(34, 48))):
            shutters(L, wx, top + 20, 10, 13, open_=bool(r.random() < 0.6), seed=wx)
            if top + 52 < SH - 6:
                shutters(L, wx, top + 52, 10, 13, open_=bool(r.random() < 0.5), seed=wx + 3)
        stucco_band(L, x0, x1, top + 42, h=3, kind=(seed + 1) % 3)
    # wooden drain spouts sticking out under the roof's edge, a dark streak under each
    r2 = rng(seed + 9)
    S = Tone(L.w, L.h)
    for sx in range(x0 + 20 + int(r2.integers(0, 20)), x1 - 10, int(r2.integers(60, 90))):
        S.rect(sx, y + 3, sx + 6, y + 4, 0.56)
        S.rect(sx + 5, y + 5, sx + 6, y + 5, 0.36)
        shade_box(L, sx + 4, y + 6, sx + 7, y + 30, 0.88)
    put_tone(L, S, TEAK, dither=0)
    # the roof's edge: a lit lip, the thickness of the roof under it
    T = Tone(L.w, L.h)
    for x in range(x0, x1):
        T.px(x, y - 1, 0.86)
        T.px(x, y, 0.98)
        T.px(x, y + 1, 0.76)
        T.px(x, y + 2, 0.50)
    # the parapet along the far side of the roof: a low wall with its crenellation
    for x in range(x0 + 2, x1 - 2):
        for j in range(back):
            T.px(x, y - 2 - j, 0.70 - 0.02 * j + 0.04 * ((x + j) % 5 == 0))
        T.px(x, y - 2 - back, 0.90)
    merlons(T, x0 + 2, x1 - 2, y - 2 - back, 0.90, kind='step' if seed % 2 else 'point')
    put_tone(L, T, LIME, dither=0.2)
    # (the parapet's foot is in shadow where the roof meets it)
    shade_box(L, x0 + 2, y - 3, x1 - 2, y - 1, 0.86)
    if left_gap:
        shade_box(L, x0, y - 2 - back, x0 + 3, SH, 0.62)
    if right_gap:
        shade_box(L, x1 - 3, y - 2 - back, x1, SH, 0.56)


def shed_roof(L, x0, x1, y, seed=1):
    """Down in a gap between two houses: the corrugated roof of a lean-to, rusty, with the dark of the alley under it."""
    T = Tone(L.w, L.h)
    for x in range(x0, x1):
        corr = (x % 4 < 2)
        T.px(x, y - 1, 0.84 + 0.10 * corr)
        T.px(x, y, 0.70 + 0.14 * corr)
        T.px(x, y + 1, 0.54 + 0.12 * corr)
        T.px(x, y + 2, 0.38)
        T.px(x, y + 3, 0.22)
    put_tone(L, T, TIN, dither=0.2)
    R = Tone(L.w, L.h)
    for x in range(x0, x1):
        if (x * 7) % 11 < 3:
            R.px(x, y, 0.42)
    put_tone(L, R, P.RUST, dither=0)
    D = Tone(L.w, L.h)
    D.rect(x0, y + 4, x1 - 1, SH - 1, 0.06)
    put_tone(L, D, SOOT, dither=0.4)


def gap_walls(L, x0, x1, ytop_l, ytop_r, floor, seed=1):
    """The side walls of the two houses either side of a gap, in shadow, down to the shed roof."""
    T = Tone(L.w, L.h)
    for x in range(x0, x1):
        for y in range(min(ytop_l, ytop_r) - 10, floor - 1):
            if x < (x0 + x1) // 2 and y < ytop_l + 2:
                continue
            if x >= (x0 + x1) // 2 and y < ytop_r + 2:
                continue
            u = (x - x0) / float(max(1, x1 - x0 - 1))
            t = 0.30 + 0.16 * (u > 0.5) - 0.10 * ((y - ytop_l) / 50.0) + 0.04 * (((x * 3 + y * 5) % 7) == 0)
            T.px(x, y, t)
    put_tone(L, T, LIME, dither=0.4)


def water_tank(L, cx, base, seed=1):
    """A black plastic water tank on an iron stand: the house's water, carried up and kept on the roof. Its lid is a
    platform."""
    K = Tone(L.w, L.h)
    for lx in (cx - 10, cx + 9):
        K.rect(lx, base - 8, lx + 1, base - 1, 0.50)
    K.rect(cx - 11, base - 9, cx + 11, base - 8, 0.62)
    K.line([(cx - 9, base - 1), (cx + 9, base - 7)], 0.40)
    put_tone(L, K, IRON, dither=0)
    T = Tone(L.w, L.h)
    top = base - 32
    for y in range(top, base - 9):
        for x in range(cx - 11, cx + 12):
            u = (x - (cx - 11)) / 22.0
            rib = ((y - top) % 6 == 0)
            t = 0.30 + 0.50 * np.exp(-((u - 0.30) / 0.22) ** 2) - 0.14 * rib
            T.px(x, y, t)
    for x in range(cx - 9, cx + 10):
        T.px(x, top - 1, 0.62)
        T.px(x, top - 2, 0.40)
    T.rect(cx - 3, top - 4, cx + 3, top - 3, 0.70)
    put_tone(L, T, TANK, dither=0.3)
    return top - 2


def stair_head(L, x0, x1, base, seed=1):
    """The little room on a roof that the stair comes up into: lime-washed, a flat top (a platform), its door open on
    the dark of the stairwell (men come up through it)."""
    T = Tone(L.w, L.h)
    top = base - 30
    for y in range(top, base):
        for x in range(x0, x1):
            u = (x - x0) / float(x1 - x0)
            t = 0.86 - 0.14 * u - 0.08 * (y > base - 4) + 0.03 * (((x * 5 + y * 3) % 9) == 0)
            if y < top + 3:
                t = 0.96 if y == top else 0.74
            T.px(x, y, t)
    merlons(T, x0, x1, top - 1, 0.92, kind='point')
    put_tone(L, T, LIME, dither=0.4)
    cx_ = (x0 + x1) // 2
    house_door(L, cx_ - 7, w=14, h=22, base=base, open_=True, seed=seed)
    return top


def washing_line(L, x0, x1, y, sag=6, seed=1):
    """A line strung between two poles on the roof, the day's washing pegged on it: shirts, a futa, a sheet."""
    K = Tone(L.w, L.h)
    for px_ in (x0, x1):
        for yy in range(y, y + 40):
            K.px(px_, yy, 0.52)
            K.px(px_ + 1, yy, 0.30)
    pts = []
    for x in range(x0, x1 + 1):
        u = (x - x0) / float(x1 - x0)
        ly = y + sag * 4 * u * (1 - u)
        K.px(x, ly, 0.66)
        pts.append((x, ly))
    put_tone(L, K, IRON, dither=0)
    r = rng(seed)
    x = x0 + 6
    cols = (CLOTH_B, CLOTH_R, CLOTH_Y, CLOTH_G, LIME)
    while x < x1 - 14:
        w = int(r.integers(8, 16))
        hh = int(r.integers(10, 20))
        rmp = cols[int(r.integers(0, len(cols)))]
        C = Tone(L.w, L.h)
        for i in range(w):
            u = (x + i - x0) / float(x1 - x0)
            ly = int(y + sag * 4 * u * (1 - u)) + 1
            for j in range(hh - (i % 5 == 0)):
                C.px(x + i, ly + j, 0.70 - 0.26 * (i / float(w)) - 0.10 * (j / float(hh)) + 0.08 * (j % 6 == 0))
        put_tone(L, C, rmp, dither=0.3)
        x += w + int(r.integers(3, 9))


def pigeon_coop(L, x0, base, seed=1):
    """A pigeon coop of old boards and wire on the roof, the birds' holes in a row (its top is a platform)."""
    T = Tone(L.w, L.h)
    top = base - 20
    for y in range(top, base):
        for x in range(x0, x0 + 40):
            t = 0.58 - 0.18 * (x - x0) / 40.0 + 0.10 * ((x - x0) % 7 == 0) - 0.08 * ((y - top) % 5 == 4)
            T.px(x, y, t)
    for x in range(x0 - 2, x0 + 42):
        T.px(x, top - 1, 0.86)
        T.px(x, top, 0.62)
    for hx in range(x0 + 5, x0 + 36, 8):
        T.rect(hx, top + 6, hx + 3, top + 9, 0.08)
    put_tone(L, T, TEAK, dither=0.3)
    return top - 1


def dish_at(L, x, base, seed=1):
    d, f = P.dish(seed=seed)
    L.paste(d, x - 14, base - f)


def roof_stair(L, steps, side_x0, side_x1, seed=1):
    """An outside stair of lime-washed masonry, its steps as the ground has them; a low wall along its open side."""
    T = Tone(L.w, L.h)
    for (a, b, y) in steps:
        for x in range(a, b):
            for yy in range(y, SH):
                t = 0.80 - 0.20 * ((yy - y) / 40.0) - 0.06 * (x - a) / max(1.0, b - a)
                if yy == y:
                    t = 0.96
                elif yy == y + 1:
                    t = 0.72
                T.px(x, yy, t)
    put_tone(L, T, LIME, dither=0.3)


HAZEL = ramp(['#8c8a96', '#a2a0aa', '#b6b2b8', '#c8c2c2', '#d8d0cc', '#e4dcd2', '#efe8dc', '#f8f4ea'], 14)


def roofscape(L, x0, x1, seed=91):
    """Behind the roofs we walk on: the rest of the town's roofs, paler for the distance and the haze, tower houses
    standing up out of them, a palm here and there."""
    T = Tone(L.w, L.h)
    r = rng(seed)
    x = x0
    while x < x1:
        w = int(r.integers(22, 60))
        top = int(r.integers(84, 128))
        for xx in range(x, min(x1, x + w)):
            u = (xx - x) / float(w)
            for y in range(top, 152):
                t = 0.82 - 0.22 * (u > 0.72) - 0.10 * ((y - top) / 60.0) + 0.03 * (((xx * 5 + y * 3) % 7) == 0)
                T.px(xx, y, t)
            if (xx - x) % 4 < 2:
                T.px(xx, top - 1, 0.88)
        for fy in range(top + 6, 146, 9):
            for wx in range(x + 3, x + w - 3, 6):
                if r.random() < 0.7:
                    T.px(wx, fy, 0.40)
                    T.px(wx, fy + 1, 0.46)
        if r.random() < 0.25:
            px_ = x + w + 2
            ph = int(r.integers(16, 30))
            for y in range(top + 20 - ph, top + 22):
                T.px(px_, y, 0.48)
            for a in range(7):
                ang = -np.pi * (0.1 + 0.8 * a / 6.0)
                for i in range(6):
                    T.px(px_ + np.cos(ang) * i, top + 20 - ph + np.sin(ang) * i + 0.15 * i * i, 0.44)
        x += w + int(r.integers(-6, 4))
    put_tone(L, T, HAZEL, dither=0.4)


def rooftops(L):
    roofscape(L, 2440, 3760)
    # the street runs on through the market gate to the foot of the stair
    paving(L, 2440, 2496, WALLB, seed=11, base=0.58)
    house_front(L, 2440, 2556, 150, seed=81, brick_top=0, floors=(), wins=[], mash=[], base=WALLB)
    # the stair up: the steps are the ground
    steps = [(2492, 2504, 178), (2504, 2516, 172), (2516, 2528, 166), (2528, 2540, 160), (2540, 2552, 155)]
    roof_stair(L, steps, 2492, 2552)
    # the houses, each at its roof's height, with the gaps between them
    roof_house(L, 2552, 2764, 150, seed=83, right_gap=True)
    roof_house(L, 2800, 2988, 144, seed=84, left_gap=True, right_gap=True)
    roof_house(L, 3016, 3228, 140, seed=85, left_gap=True)
    roof_house(L, 3228, 3296, 152, seed=86, right_gap=True, back=6)
    roof_house(L, 3336, 3548, 146, seed=87, left_gap=True)
    roof_house(L, 3548, 3628, 150, seed=88, back=6)
    for (a, b, yl, yr, fl) in ((2764, 2800, 150, 144, 194), (2988, 3016, 144, 140, 196), (3296, 3336, 152, 146, 194)):
        gap_walls(L, a, b, yl, yr, fl)
        shed_roof(L, a, b, fl)
    # roof A: a water tank, the washing, sacks of chilli drying
    t = water_tank(L, 2632, 150, seed=1)
    plat('tank1', [[2621, t], [2643, t]])
    washing_line(L, 2672, 2748, 110, sag=7, seed=3)
    # roof B: the stair-head (men come up it), a dish
    t = stair_head(L, 2858, 2902, 144, seed=2858)
    plat('shead1', [[2858, t], [2902, t]])
    dish_at(L, 2956, 144, seed=4)
    washing_line(L, 2810, 2846, 106, sag=5, seed=5)
    # roof C: a tank, the pigeon coop, the washing
    t = water_tank(L, 3074, 140, seed=6)
    plat('tank2', [[3063, t], [3085, t]])
    t = pigeon_coop(L, 3150, 140, seed=7)
    plat('coop', [[3150, t], [3190, t]])
    washing_line(L, 3200, 3290, 104, sag=8, seed=8)
    # roof E: another stair-head, a tank
    t = stair_head(L, 3398, 3442, 146, seed=3398)
    plat('shead2', [[3398, t], [3442, t]])
    t = water_tank(L, 3502, 146, seed=9)
    plat('tank3', [[3491, t], [3513, t]])
    washing_line(L, 3350, 3388, 108, sag=5, seed=10)
    dish_at(L, 3580, 150, seed=11)
    # the stair down into the covered market's yard
    steps = [(3628, 3640, 156), (3640, 3652, 162), (3652, 3664, 168), (3664, 3676, 174), (3676, 3688, 179)]
    paving(L, 3628, CM + 60, WALLB, seed=13, base=0.56)
    house_front(L, 3620, 3760, 96, seed=89, brick_top=8, floors=(130,), wins=[(3700, 110, 10, 14, False)], mash=[], base=WALLB)
    roof_stair(L, steps, 3628, 3688)
    INFO['pits'] = PITS
    INFO['roofs'] = [list(r) for r in ROOFS]


# ------------------------------------------------------------------ 3: the covered market
def market_front(L, x0=3756, x1=3810, seed=101):
    """The covered market's end wall, cut through where the street goes in: thick brick and lime, a pointed arch
    (barricaded), a carved band, the roof's edge above."""
    T = Tone(L.w, L.h)
    D = Tone(L.w, L.h)
    w = x1 - x0
    cx_ = x0 + w / 2.0
    aw, spring = 21.0, 130
    for x in range(x0, x1):
        u = (x - x0) / float(w - 1)
        for y in range(0, SH):
            dx = abs(x - cx_)
            pointed = y <= spring and dx < aw and (y - (spring - aw * 1.2)) > (dx / aw) * aw * 1.2 * 0.9 - 2
            inside = dx < aw and (y > spring or pointed)
            if inside:
                if y < WALK + 2:
                    D.px(x, y, 0.12 + 0.10 * (y - 100) / 80.0)
                continue
            course = (y // 4) % 2
            joint = (y % 4 == 0) or ((x + 5 * course) % 10 == 0)
            t = 0.60 - 0.22 * u - 0.16 * joint + (0.06 if x == x0 else 0) - (0.14 if x == x1 - 1 else 0)
            T.px(x, y, t)
    put_tone(L, T, BRICK, dither=0.4, grain=0.03, seed=seed)
    put_tone(L, D, SOOT, dither=0.5)
    stucco_band(L, x0 + 2, x1 - 2, 80, h=6, kind=0)
    stucco_band(L, x0 + 2, x1 - 2, 30, h=4, kind=1)
    INFO['mfront'] = [x0, x1]


def vault(L, x0, x1, bays, seed=103):
    """The hall's roof seen from inside: a brick barrel vault going up into the dark, a transverse arch at every pier,
    and in the middle of each bay a skylight, bright."""
    w = x1 - x0
    h = 46
    yy, xx = np.mgrid[0:h, 0:w]
    X = xx + x0
    course = (yy // 4) % 2
    joint = (yy % 4 == 0) | (((X + 5 * course) % 10) == 0)
    tone = 0.20 + 0.30 * (yy / float(h)) ** 1.2 - 0.08 * joint + 0.04 * (fbm((h, w), seed, 8, 3, octaves=2) - 0.5)
    G = Layer(w, h)
    G.put(toned(np.clip(tone, 0.02, 1), BRICK, dither=0.5, x0=x0), np.ones((h, w), bool))
    L.paste(G, x0, 0)
    T = Tone(L.w, L.h)
    for px_ in bays:
        for y in range(0, 48):
            for i in range(10):
                T.px(px_ - 5 + i, y, 0.62 - 0.30 * (i > 6) + 0.12 * (i < 2) - 0.003 * y)
    put_tone(L, T, LIME, dither=0.3)


def shop_front(L, x0, w=40, top=98, paint=BLUEWOOD, open_=False, seed=1):
    """A shop in the hall's wall: a pointed arch, its wooden shutters shut (or one open on a dark shop with sacks in
    it)."""
    T = Tone(L.w, L.h)
    cx_ = x0 + w / 2.0
    for y in range(top - 6, WALLB):
        for x in range(x0 - 3, x0 + w + 3):
            dx = abs(x - cx_)
            arch_y = top + (dx / (w / 2.0)) ** 1.6 * 12
            if y < arch_y - 3 or dx > w / 2.0 + 3:
                continue
            if y >= arch_y and dx <= w / 2.0:
                continue
            T.px(x, y, 0.86 - 0.20 * (x > cx_))
    put_tone(L, T, LIME, dither=0.3)
    S = Tone(L.w, L.h)
    for y in range(top, WALLB):
        for x in range(x0, x0 + w):
            dx = abs(x - cx_)
            if y < top + (dx / (w / 2.0)) ** 1.6 * 12:
                continue
            if open_:
                S.px(x, y, 0.10 + 0.06 * (y > 140))
            else:
                plank = (x - x0) % 5 == 0
                t = 0.52 - 0.16 * plank - 0.10 * (x > cx_) + 0.14 * (((y - top) % 16) == 8) * ((x - x0) % 10 == 3)
                S.px(x, y, t)
    put_tone(L, S, SOOT if open_ else paint, dither=0.3)
    if open_:
        N = Layer(L.w, L.h)
        SM.sack_pile(N, [(x0 + 4, x0 + w - 4, 138)], WALLB, seed=seed)
        L.paste(N)


def hall(L):
    x0, x1 = 3810, WORLD
    paving(L, 3760, x1, WALLB, seed=17, base=0.50)
    piers = list(range(3870, x1, 128))
    # the back wall: lime, the shops between the piers, small vents high up
    house_front(L, x0, x1, 40, seed=105, brick_top=0, floors=(84,), wins=[], mash=[], base=WALLB, shade=0.16)
    Nn = Tone(L.w, L.h)                                   # little arched vents high in the wall
    for nx in range(x0 + 30, x1 - 10, 32):
        for y in range(56, 72):
            for x in range(nx, nx + 8):
                if y < 59 and abs(x - nx - 3.5) > (y - 55) * 1.3:
                    continue
                Nn.px(x, y, 0.08 + 0.06 * (y > 66))
    put_tone(L, Nn, SOOT, dither=0.3)
    paints = (BLUEWOOD, CLOTH_G, TEAK, BLUEWOOD, CLOTH_R, TEAK, CLOTH_G, BLUEWOOD)
    k = 0
    for i, px_ in enumerate(piers + [x1 + 64]):
        a = (piers[i - 1] if i else x0) + 10
        b = px_ - 10
        if b - a < 50:
            continue
        n = 2 if b - a > 100 else 1
        sw = (b - a - 14 * (n - 1)) // n
        for j in range(n):
            sx = a + j * (sw + 14)
            shop_front(L, sx, w=min(44, sw), top=100, paint=paints[k % len(paints)], open_=(k % 5 == 3), seed=k)
            k += 1
    vault(L, x0, x1, piers)
    # the piers down the wall to the floor
    T = Tone(L.w, L.h)
    for px_ in piers:
        for y in range(40, WALLB + 4):
            for i in range(12):
                T.px(px_ - 6 + i, y, 0.80 - 0.32 * (i > 8) + 0.08 * (i < 2) - 0.10 * (y > WALLB - 6))
        T.rect(px_ - 8, 82, px_ + 7, 86, 0.92)
    put_tone(L, T, LIME, dither=0.3)
    for px_ in piers:
        soft_shadow(L, px_ + 6, px_ + 12, WALLB + 4, 3, 0.8)
    # lanterns hung from the transverse arches, and their light
    for px_ in piers[1::2]:
        K = Tone(L.w, L.h)
        for y in range(46, 64):
            K.px(px_, y, 0.40)
        K.rect(px_ - 2, 64, px_ + 2, 65, 0.50)
        put_tone(L, K, IRON, dither=0)
        lantern_glass(L, px_ - 1, 66)
        glow(L, px_, 72, 40, amt=0.28, col=(255, 210, 120))
    # skylights in the middle of each bay, and the sunlight falling from them across to the floor
    for i in range(len(piers) - 1):
        cx_ = (piers[i] + piers[i + 1]) // 2
        for y in range(2, 9):
            for x in range(cx_ - 6, cx_ + 7):
                L.rgb[y, x] = (255, 248, 222) if (x + y) % 3 else (250, 236, 196)
        SM.light_shaft(L, cx_ - 6, 9, WALLB + 28, w=12, slope=0.42, lift=1.12, floor_y=WALLB)
    # the far end: the Dhanabs' store of dried chillies, sacks piled to the vault, and a dark doorway (the scale itself is
    # drawn by the game: render_scale.js)
    N = Layer(L.w, L.h)
    SM.sack_pile(N, [(4720, 4800, 120), (4730, 4790, 104)], WALLB + 2, seed=107)
    L.paste(N)
    D = Tone(L.w, L.h)
    D.rect(4808, 70, x1 - 1, WALLB + 2, 0.06)
    put_tone(L, D, SOOT, dither=0.4)
    # a few dried chillies dropped at its foot (a pod is two dots of red and a dot of stalk)
    r = rng(108)
    for k2 in range(9):
        x = int(r.uniform(4712, 4800))
        y = WALLB + 1 + int(r.integers(0, 3))
        L.rgb[y, x] = CHILLI[6]
        L.rgb[y, x + 1] = CHILLI[5]
        L.rgb[y, x + 2] = (92, 74, 30)
    market_front(L)
    STp = Tone(L.w, L.h)
    crate_tone(STp, 3806, 176, 52, 8, seed=109)
    put_tone(L, STp, TEAK, dither=0.3)
    plat('b3back', [[3806, 176], [3858, 176]])
    INFO.setdefault('bars', {})['b3'] = dict(x0=3760, top=150, x1=3858)
    INFO['piers'] = piers


# ------------------------------------------------------------------ what passes close to the lens
# The foreground slides at 1.25 times the camera. Something meant to pass by world x when the camera is about there is
# at 1.25 x - 58 along the foreground (FX converts).
def FX(xw):
    return int(round(1.25 * xw - 58))


F1, F2, F3 = FX(1246), FX(2552), FX(3810)           # (where the market, the roofs and the hall begin)
F4 = FX(WORLD) + 520
FTILE = 640


def fore_road(w=F1):
    """On the road: the trunk of a palm close by, a cart wheel lying in the dust, tufts of scrub along the bottom."""
    L = Layer(w, SH)
    T = Tone(w, SH)
    for (bx, lean) in ((360, 10), (1160, -8)):
        for y in range(20, SH):
            u = (SH - y) / float(SH - 20)
            cx_ = bx + lean * u * u
            ring = (y % 9) < 4
            for i in range(-8, 9):
                T.px(cx_ + i, y, (0.26 if ring else 0.18) + 0.20 * np.exp(-((i + 4) / 3.5) ** 2))
    put_tone(L, T, P.DRIFT, dither=0.3)
    Wh = Tone(w, SH)
    for a in range(0, 360, 6):
        for rr in (17, 18):
            Wh.px(820 + rr * np.cos(np.radians(a)) * 1.0, 214 + rr * np.sin(np.radians(a)) * 0.45, 0.30)
    for a in range(0, 180, 30):
        Wh.line([(820, 214), (820 + 17 * np.cos(np.radians(a + 180)), 214 + 7 * np.sin(np.radians(a + 180)))], 0.24)
    put_tone(L, Wh, TEAK, dither=0.2)
    S = Tone(w, SH)
    r = rng(5)
    for k in range(int(w / 40)):
        x = int(r.uniform(0, w - 10))
        hh = int(r.integers(5, 10))
        for i in range(-8, 9):
            top = int(hh * np.sqrt(max(0.0, 1 - (i / 8.5) ** 2)))
            if i % 3 == 0 and abs(i) < 7:
                top += 2                                  # (a few blades standing up out of it)
            for j in range(top):
                S.px(x + i, SH - 1 - j, 0.16 + 0.12 * (i < -2) + 0.06 * (j > top - 3))
    put_tone(L, S, SCRUB, dither=0.3)
    return L


def fore_market(w=FTILE):
    """In the market: the fringes of awnings hanging into the top of the picture, and a lantern."""
    L = Layer(w, SH)
    A = Tone(w, SH)
    for (a, b, rmp) in ((40, 150, 0), (330, 430, 1)):
        for x in range(a, b):
            sg = 3 * np.sin((x - a) / float(b - a) * np.pi)
            for y in range(0, int(8 + sg)):
                A.px(x, y, 0.36 - 0.20 * (y / 10.0) + 0.10 * (((x - a) // 8) % 2))
            if (x - a) % 6 < 4:
                A.px(x, int(8 + sg), 0.18)
    put_tone(L, A, CLOTH_R, dither=0.3)
    K = Tone(w, SH)
    for y in range(0, 30):
        K.px(250 + (y % 2), y, 0.30)
    K.rect(245, 30, 256, 32, 0.30)
    K.rect(246, 42, 255, 43, 0.24)
    K.rect(245, 30, 245, 42, 0.22)
    K.rect(256, 30, 256, 42, 0.16)
    put_tone(L, K, IRON, dither=0)
    for y in range(33, 42):
        for x in range(247, 255):
            L.rgb[y, x] = (255, 226, 140) if (x + y) % 3 else (250, 190, 90)
            L.a[y, x] = True
    return L


def fore_roofs(w=F3 - F2):
    """On the roofs: the corner of a parapet at the bottom now and then. (Nothing hangs across the top: it would sit
    over the HUD.)"""
    L = Layer(w, SH)
    T = Tone(w, SH)
    for bx in (700, 1400):
        if bx + 60 > w:
            break
        for y in range(SH - 30, SH):
            for x in range(bx, bx + 56):
                T.px(x, y, 0.30 - 0.12 * ((x - bx) / 56.0) + (0.14 if y == SH - 30 else 0))
        merlons(T, bx, bx + 56, SH - 31, 0.40)
    put_tone(L, T, LIME, dither=0.3)
    return L


def fore_hall(w=FTILE):
    """In the covered market: the arcade's piers and arches close to the lens, dark against the hall, a lantern."""
    L = Layer(w, SH)
    T = Tone(w, SH)
    for x in range(w):
        for y in range(0, 10):
            T.px(x, y, 0.26 - 0.02 * y + 0.06 * (y == 0) + 0.04 * ((x // 23) % 2))
        T.px(x, 10, 0.08)
    for px_ in (110,):
        for y in range(10, SH):
            for i in range(18):
                T.px(px_ + i, y, 0.26 - 0.012 * i + 0.10 * (i == 0) + 0.03 * (((y // 6) % 2) and i in (6, 7)))
        for j in range(16):
            T.rect(px_ - 14 + j, 10 + j, px_ + 31 - j, 10 + j, 0.20 + 0.04 * (j == 0))
    put_tone(L, T, BRICK, dither=0.3)
    return L


# ------------------------------------------------------------------ sky, the town far off, the plain
def sky_z(w=1404, seed=7):
    """A hot afternoon over the Tihama: pale blue going to haze, a few thin high clouds, the glare low down."""
    h = HORIZON + 6
    yy = np.arange(h)[:, None] / float(HORIZON)
    xx = np.arange(w)[None, :]
    tone = 0.10 + 0.78 * np.clip(yy, 0, 1) ** 1.35 + 0 * xx
    cir = fbm((h, w), seed, 80, 1.2, octaves=3)
    tone += np.clip(cir - 0.56, 0, 1) * 0.9 * np.exp(-((yy - 0.30) / 0.20) ** 2)
    cir2 = fbm((h, w), seed + 3, 46, 0.9, octaves=2)
    tone += np.clip(cir2 - 0.62, 0, 1) * 0.6 * np.exp(-((yy - 0.52) / 0.12) ** 2)
    far = [(x, HORIZON - 3 + (i % 3), 90 + 30 * (i % 2), 5 + 3 * (i % 3), 34, 2.0, 4.0) for i, x in enumerate(range(30, w, 74))]
    Zf = ndi.gaussian_filter(SL.puffs_wrap(h, w, far, seed + 40), 1.2, mode='wrap')
    covf = np.clip(Zf * 0.5, 0, 1)
    tone = tone + covf * 0.7 * (0.93 - tone)
    L = Layer(w, h)
    L.put(toned(np.clip(tone, 0, 1), SKYZ, dither=0.7), np.ones((h, w), bool))
    return L


def _tower(T, x, base, hgt, wid, seed, brick=None):
    """A tower house far off: lit face, shaded side, rows of windows, a band of brick or carving at the top, the
    stepped parapet."""
    r = rng(seed)
    top = base - hgt
    for y in range(top, base):
        for i in range(wid):
            u = i / float(max(1, wid - 1))
            t = 0.92 - 0.30 * (u > 0.70) - 0.05 * ((y - top) / float(hgt))
            if brick is not None and y < top + 5:
                t -= 0.22
            T.px(x + i, y, t)
    for i in range(0, wid, 3):
        T.px(x + i, top - 1, 0.94)
    for fy in range(top + 6, base - 3, 6):
        for i in range(2, wid - 2, 4):
            if r.random() < 0.8:
                T.px(x + i, fy, 0.34)
                T.px(x + i, fy + 1, 0.40)


def far_z(w=2808, seed=9):
    """Zabid far off over the plain: whitewashed tower houses close together, the old citadel's square keep, palm
    groves round the town, and the mountains of the escarpment very faint in the haze to the east."""
    h, wl = ST.FAR_H, ST.FAR_WATER
    yy, xx = np.mgrid[0:h, 0:w]
    L = Layer(w, h)
    for i, (sd, amp, sx, t0) in enumerate([(seed, 30, 160, 0.86), (seed + 9, 16, 90, 0.78)]):
        top = ST._ridge(w, sd, wl - 4, amp, sx)
        fade = np.clip(np.sin(2 * np.pi * np.arange(w) / w * 2 + i * 1.3) * 0.5 + 0.75, 0.25, 1)
        top = wl - 4 - (wl - 4 - top) * fade
        m = (yy >= top[None, :]) & (yy < wl)
        tone = t0 + 0.04 * np.clip((yy - top[None, :]) / 12.0, 0, 1) + 0.03 * (noise((h, w), sd + 3, 6, 2) - 0.5)
        L.put(toned(np.clip(tone, 0, 1), HAZEZ, dither=0.6), m)
    T = Tone(w, h)
    r = rng(seed + 20)
    x = 6
    k = 0
    while x < w - 40:
        n = int(r.integers(4, 10))
        for c in range(n):
            wid = int(r.integers(8, 16))
            hgt = int(r.integers(10, 30))
            if x + wid >= w - 4:
                break
            _tower(T, x, wl, hgt, wid, seed + k, brick=True if r.random() < 0.4 else None)
            x += wid + int(r.integers(0, 2))
            k += 1
        # palm groves between the quarters
        for p in range(int(r.integers(2, 6))):
            px_ = x + 3 + p * 6
            if px_ >= w - 8:
                break
            ph = int(r.integers(10, 20))
            for y in range(wl - ph, wl):
                T.px(px_, y, 0.40)
            for a in range(7):
                ang = -np.pi * (0.1 + 0.8 * a / 6.0)
                for i in range(5):
                    T.px(px_ + np.cos(ang) * i, wl - ph + np.sin(ang) * i + 0.15 * i * i, 0.36)
        x += int(r.integers(14, 50))
    # the citadel: a long low wall and its square keep
    cx0 = 1300
    for x in range(cx0, cx0 + 150):
        for y in range(wl - 16, wl):
            T.px(x, y, 0.84 - 0.05 * ((x - cx0) // 30 % 2))
        if x % 5 < 2:
            T.px(x, wl - 17, 0.88)
    for y in range(wl - 40, wl - 16):
        for i in range(26):
            T.px(cx0 + 60 + i, y, 0.90 - 0.28 * (i > 18))
    for i in range(0, 26, 4):
        T.rect(cx0 + 60 + i, wl - 42, cx0 + 61 + i, wl - 41, 0.92)
    L.paste(T.layer(HAZEZ, dither=0.5, grain=0.04, seed=seed + 30))
    return L


def plain_z(w=1320, seed=13):
    """The plain between the town and the road (it takes the place the sea has elsewhere): dust and pale earth,
    scrub, acacias, palm groves, the haze lying on it."""
    h = 64
    yy, xx = np.mgrid[0:h, 0:w]
    v = yy / float(h - 1)
    base = 0.82 - 0.36 * v
    src = fbm((h, w * 2), seed, 18, 0.8, octaves=3)
    tone = np.zeros((h, w))
    for y in range(h):
        s_ = 0.4 + 1.8 * (y / (h - 1.0))
        xs = (np.arange(w) / s_ + 37 * y) % (w * 2 - 1)
        tone[y] = np.interp(xs, np.arange(w * 2), src[y])
    t = base + 0.12 * (tone - 0.5)
    t[0] = 0.92
    L = Layer(w, h)
    L.put(toned(np.clip(t, 0.05, 0.98), PLAIN, dither=0.6), np.ones((h, w), bool))
    T = Tone(w, h)
    r = rng(seed + 4)
    # palm groves along the far side and scrub nearer, wrapping round
    for k in range(70):
        x = int(r.uniform(0, w))
        y = int(4 + (r.random() ** 1.6) * (h - 12))
        s_ = 0.4 + 1.6 * (y / float(h))
        if r.random() < 0.35:
            ph = int(6 + 6 * s_)
            for yy_ in range(y - ph, y):
                T.px(x % w, yy_, 0.36)
            for a in range(7):
                ang = -np.pi * (0.1 + 0.8 * a / 6.0)
                for i in range(int(3 + 2 * s_)):
                    T.px((x + np.cos(ang) * i) % w, y - ph + np.sin(ang) * i + 0.15 * i * i, 0.30 + 0.06 * (a < 3))
        else:
            cw = int(3 + 4 * s_)
            for i in range(-cw, cw + 1):
                hh = int((cw - abs(i)) * 0.5) + 1
                for j in range(hh):
                    T.px((x + i) % w, y - j, 0.34 + 0.20 * (i < 0) + 0.10 * (j == hh - 1))
    L.paste(T.layer(SCRUB, dither=0.4))
    return SL._fold(L)


# ------------------------------------------------------------------ looking at it
def compose(cam, S, w=SW, fore=True):
    out = Layer(w, SH)

    def wrap(Lr, par, y):
        x = int(cam * par) % Lr.w
        out.paste(Lr, -x, y)
        out.paste(Lr, Lr.w - x, y)

    wrap(S['sky'], 0.2, 0)
    wrap(S['sea'], 0.6, HORIZON)
    wrap(S['far'], 0.35, ST.FAR_TOP)
    out.paste(S['play'], -int(cam), 0)
    if fore and 'fore' in S:
        out.paste(S['fore'], -int(cam * 1.25), 0)
    return out


def preview(S, cams, path, lines=False, w=SW):
    sheet = Layer(w * 2 + 6, (SH + 6) * ((len(cams) + 1) // 2))
    sheet.rgb[:] = (20, 16, 24)
    sheet.a[:] = True
    for i, c in enumerate(cams):
        sc = compose(c, S, w)
        if lines:
            for pid, pts in PLATS.items():
                for k in range(len(pts) - 1):
                    for x in range(pts[k][0], pts[k + 1][0] + 1):
                        xs = x - c
                        if 0 <= xs < w:
                            f = (x - pts[k][0]) / max(1, pts[k + 1][0] - pts[k][0])
                            y = int(round(pts[k][1] + (pts[k + 1][1] - pts[k][1]) * f))
                            sc.rgb[y, xs] = (255, 40, 200)
            for xs in range(0, w, 2):
                y = int(round(gy(c + xs)))
                if 0 <= y < SH:
                    sc.rgb[y, xs] = (40, 255, 120)
        sheet.paste(sc, (i % 2) * (w + 6), (i // 2) * (SH + 6))
    im = sheet.image()
    im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
    im.save(path)
    return im.size


# ------------------------------------------------------------------ the whole stage
_CACHE = {}


def build():
    if not _CACHE:
        PLATS.clear()
        INFO.clear()
        play = Layer(WORLD, SH)
        town_gate(play)
        spice_stalls(play)
        rooftops(play)
        hall(play)
        fr, fm, fo, fh = fore_road(), fore_market(), fore_roofs(), fore_hall()
        fore = Layer(F4, SH)
        fore.paste(fr, 0, 0)
        x = F1
        while x < F2:
            part = fm if x + FTILE <= F2 else fm.crop(0, 0, F2 - x, SH)
            fore.paste(part, x, 0)
            x += FTILE
        fore.paste(fo, F2, 0)
        x = F3
        while x < F4:
            part = fh if x + FTILE <= F4 else fh.crop(0, 0, F4 - x, SH)
            fore.paste(part, x, 0)
            x += FTILE
        _CACHE.update(play=play, sky=sky_z(), far=far_z(), sea=plain_z(), fore=fore, fore_road=fr, fore_market=fm, fore_roofs=fo, fore_hall=fh)
    return _CACHE


if __name__ == '__main__':
    import sys
    S = build()
    cams = [0, 640 - 234, 1186 - 234, 1300, 1760 - 234, 2380 - 234, 2560, 2920 - 234, 3470 - 234, 3750 - 234, 3990, 4306 - 234]
    print(preview(S, cams, sys.argv[1] if len(sys.argv) > 1 else 'zabid.png', lines='lines' in sys.argv))
    print('plats', PLATS)
    print('info', INFO)
