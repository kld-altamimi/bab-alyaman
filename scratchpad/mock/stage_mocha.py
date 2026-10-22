# stage_mocha.py - The Coffee Port, painted as the Strait is: tone fields mapped through colour ramps, checker dither
# between neighbours, light from the upper left, no outlines on scenery.
# One long picture of everything the squad walks past (the quay; the coffee warehouses with their front wall cut away;
# the roasting house; the point with the old lighthouse), cut into strips for the game; a foreground that passes close
# to the lens; and a late-afternoon sky, the old town of Mocha across the harbour, and the harbour water, all of which
# wrap. Where the floor and the tops of things are is recorded as it is painted (PLATS), so the level can be checked
# against the picture.
import numpy as np
from scipy import ndimage as ndi
from paint import *
import props as P
import stage as ST
import stage_long as SL

SW, SH = 468, 216
WORLD = 4480
Q, WH, RH, PT = 0, 1232, 2464, 3584       # the quay, the warehouses, the roasting house, the point
WALK = 184                                 # where feet land, everywhere
QBACK = 148                                # the top of the quay's coping: the harbour shows above it
WALLB = 160                                # inside, where the back wall meets the floor
HORIZON = ST.HORIZON

# ------------------------------------------------------------------ colour ramps (dark to pale)
CORAL = ramp(['#1c1612', '#3a3029', '#5c4f43', '#82735f', '#a6967b', '#c4b797', '#ded3b8', '#f2ecd8'], 18)      # coral stone
LIME = ramp(['#2a2118', '#54473a', '#83755f', '#ab9f84', '#cbc2a6', '#e2dcc4', '#f4f0e0', '#fffcf2'], 20)       # lime-washed plaster
EARTH = ramp(['#1a120c', '#36261a', '#56402c', '#76583e', '#967454', '#b4926e', '#d0b08c'], 16)                 # beaten earth floors
MUD = ramp(['#160c08', '#30190e', '#4e2a16', '#6e3e20', '#8e542c', '#ac6e3e', '#c88c58', '#e0ac7c'], 18)        # mud brick
SOOT = ramp(['#0c0808', '#1c1412', '#2e221c', '#423228', '#584436', '#6e5646'], 10)
TEAK = ramp(['#140a06', '#2c160c', '#4a2814', '#6a3c1e', '#8c552c', '#ac7040', '#c88e5a', '#e0b080'], 16)
COPPER = ramp(['#1a0804', '#3c140a', '#682610', '#963c18', '#c05a22', '#de8034', '#f0a850', '#fcd08a', '#fff2cc'], 18)
IRON = ramp(['#0e0c0e', '#201c1e', '#363034', '#4e4648', '#6a6060', '#8a7e78', '#aa9e92'], 12)
CRANE = ramp(['#1e1004', '#4a2a06', '#7c4c0a', '#ac7410', '#d49c20', '#ecc040', '#f8e080', '#fffad0'], 16)      # dock-crane yellow
SACK = ramp(['#1c140a', '#3a2c18', '#5c4a2c', '#806a44', '#a28c60', '#bfab80', '#d8c8a0', '#ece2c4'], 16)
GREENSACK = ramp(['#161408', '#2e2c16', '#4a4626', '#686238', '#888050', '#a69e6c', '#c4bc90'], 14)
BEAN = ramp(['#0c0604', '#1e0e06', '#34180a', '#4e2610', '#6c3818', '#8a4c22'], 8)
CLOTH_R = ramp(['#2a0806', '#561008', '#84200e', '#ac3418', '#cc5228', '#e47c44', '#f4ac70'], 12)               # an awning
CLOTH_B = ramp(['#081422', '#10283e', '#1c4260', '#2e6084', '#4c84a4', '#7cacc4', '#b4d4e0'], 12)
GLASS = ramp(['#0a1014', '#14222a', '#203a44', '#34585e', '#5a8484', '#94b8b0', '#d4ecdc'], 10)
FIRE = P.FIRE
LIGHT = ramp(['#3a2810', '#7a5420', '#c08830', '#f0c050', '#fff0a0', '#fffbe0'], 10)
# the sky late in the afternoon: deep blue overhead, warm haze low down; the far shore and the water to match
SKYM = ramp(['#1c3c6c', '#2c4c7c', '#40608c', '#5c7498', '#7c88a0', '#a09aa0', '#c4aa9c', '#deb894', '#f0c890', '#f8dcac', '#fdf0d4'], 22)
HAZEM = ramp(['#5a5a78', '#76708a', '#94889a', '#b0a0a6', '#c8b4ac', '#dcc6b0', '#ecd8bc', '#f8ead0'], 16)
HARBOUR = ramp(['#0a1e2a', '#123446', '#1c4c5c', '#2a6670', '#448280', '#689e90', '#94b8a0', '#c4d4b0', '#ecead0'], 20)

PLATS = {}            # id -> [[x, y], ...] as painted
INFO = {}             # anything else the level needs to know (doors, vents, the lighthouse)


def plat(pid, pts):
    PLATS[pid] = [[int(x), int(y)] for x, y in pts]


# ------------------------------------------------------------------ small painters
def put_tone(L, T, rmp, dither=0.45, grain=0.0, seed=1):
    L.paste(T.layer(rmp, dither=dither, grain=grain, seed=seed))


def sack_tone(T, x, y, w=14, h=8, seed=0, lit=0.0, mark=None, green=False):
    """A sack lying on its side, the tied ear to the right: into a Tone canvas at (x, y) top-left."""
    r = rng(seed)
    for j in range(h):
        v = j / float(h - 1)
        inset = 2 if j in (0, h - 1) else (1 if j in (1, h - 2) else 0)
        for i in range(inset, w - inset):
            u = i / float(w - 1)
            t = 0.80 - 0.46 * v - 0.20 * u + 0.12 * (v < 0.34) * (u < 0.6) + lit
            if j == h - 1 or i in (inset, w - inset - 1):
                t -= 0.20
            t += 0.05 * ((i * 3 + j * 5 + seed) % 4 == 0) + 0.04 * (r.random() - 0.5)
            T.px(x + i, y + j, t)
    T.px(x + w - 2, y + 1, 0.30)            # the ear, tied off
    T.px(x + w - 1, y, 0.62)
    for i in range(3, w - 3, 3):
        T.px(x + i, y + h - 2, 0.30)         # the seam


def sack_marks(L, x, y, w=14, h=8, kind=0):
    """The stencil on a coffee sack: a red band and a dark mark (they say MOCHA, near enough)."""
    red = (150, 44, 26)
    dark = (44, 30, 18)
    if kind == 0:
        for i in range(3, w - 4):
            if 0 <= x + i < L.w and 0 <= y + 3 < L.h:
                L.rgb[y + 3, x + i] = red
        for i in (4, 6, 8):
            if 0 <= x + i < L.w and 0 <= y + 5 < L.h:
                L.rgb[y + 5, x + i] = dark
    elif kind == 1:
        for (i, j) in ((4, 2), (5, 3), (6, 2), (7, 3), (8, 2)):
            if 0 <= x + i < L.w and 0 <= y + j < L.h:
                L.rgb[y + j, x + i] = red


def sack_pile(L, steps, base, seed=1, green=False, marks=True, w=14, h=8):
    """Sacks stacked like bricks. steps: [(x0, x1, top), ...] - each a block of sacks from top down to base."""
    T = Tone(L.w, L.h)
    placed = []
    k = 0
    for (x0, x1, top) in steps:
        rows = max(1, int(round((base - top) / float(h - 1))))
        for row in range(rows):
            y0 = base - (row + 1) * (h - 1) - 1
            if y0 < top - 2:
                break
            off = (w // 2) if row % 2 else 0
            n = int((x1 - x0 - off) // (w - 1))
            for c in range(n):
                sx = x0 + off + c * (w - 1)
                k += 1
                sack_tone(T, sx, y0, w, h, seed=seed * 31 + k, lit=0.05 * (row == rows - 1))
                placed.append((sx, y0, k))
    put_tone(L, T, GREENSACK if green else SACK, dither=0.4, grain=0.04, seed=seed)
    if marks:
        for sx, y0, k in placed:
            if k % 5 == 0:
                sack_marks(L, sx, y0, w, h, kind=k % 2)
    return placed


def crate_tone(T, x, y, w, h, seed=1, lid=True):
    """A wooden box: planks across, battens at the ends, lit from the upper left (scenery, so no outline)."""
    r = rng(seed)
    for j in range(h):
        for i in range(w):
            u, v = i / float(w - 1), j / float(h - 1)
            t = 0.62 - 0.16 * v - 0.12 * u + 0.05 * (r.random() - 0.5)
            if (j % 5) == 4:
                t -= 0.18
            if i < 3 or i >= w - 3:
                t = 0.54 - 0.12 * v + (0.22 if i == 0 else (-0.18 if i == w - 1 else 0))
            if j == 0:
                t = 0.86
            if j == h - 1:
                t = 0.20
            T.px(x + i, y + j, t)


def lamp_post(T, x, base, top=104):
    """An old harbour lamp: iron post, a scrolled arm, a glass lantern."""
    for y in range(top + 10, base):
        T.px(x, y, 0.62)
        T.px(x + 1, y, 0.34)
    T.rect(x - 2, base - 6, x + 3, base - 1, 0.44)
    T.rect(x - 2, base - 6, x + 3, base - 6, 0.70)
    for i in range(10):
        T.px(x + 1 + i, top + 10 - int(3 * np.sin(i / 9.0 * np.pi)), 0.56)
    T.rect(x + 8, top + 8, x + 13, top + 18, 0.30)


def lantern_glass(L, x, y):
    for j in range(8):
        for i in range(4):
            L.rgb[y + j, x + i] = (255, 236, 170) if (i + j) % 3 else (250, 200, 110)
            L.a[y + j, x + i] = True


# ------------------------------------------------------------------ the ground
def paving(L, x0, x1, ytop, seed=3, slant=-0.35, base=0.56):
    """Big worn slabs of coral stone, laid in courses that deepen toward the viewer; the joints lean a little, as a
    floor seen from above and in front does. Joints dark, top edges lit, cracks, stains and sand in the joints."""
    w = x1 - x0
    h = SH - ytop
    yy, xx = np.mgrid[0:h, 0:w]
    sy = yy + ytop
    X = xx + x0                                                    # (in stage coordinates, so pieces join up)
    rows = [ytop, ytop + 5, ytop + 11, ytop + 18, ytop + 26, ytop + 35, ytop + 45, ytop + 56, SH + 12]
    r = rng(seed)
    t = np.zeros((h, w))
    joint = np.zeros((h, w), bool)
    lit = np.zeros((h, w), bool)
    slab_id = np.zeros((h, w), int)
    for k in range(len(rows) - 1):
        a, b = rows[k], rows[k + 1]
        band = (sy >= a) & (sy < b)
        lean = (sy - a) * slant
        span = (b - a)
        x = x0 - int(r.integers(0, 60))
        edges = []
        while x < x1 + 60:
            edges.append(x)
            x += int(r.integers(int(22 + span * 1.6), int(34 + span * 2.6)))
        for i in range(len(edges) - 1):
            ea, eb = edges[i] + lean, edges[i + 1] + lean
            m = band & (X >= ea) & (X < eb)
            t = np.where(m, r.uniform(-0.07, 0.07), t)
            slab_id = np.where(m, k * 1000 + i, slab_id)
            joint |= band & (np.abs(X - ea) < 0.5)
            lit |= band & (np.abs(X - ea - 1) < 0.5)
        joint |= band & (sy == b - 1)
        lit |= band & (sy == a)
    depth = np.clip((sy - ytop) / float(SH - ytop), 0, 1)
    wear = fbm((h, w), seed + 1, 30, 6, octaves=3)
    grit = fbm((h, w), seed + 2, 1.4, 0.8, octaves=2) - 0.5
    stain = np.clip(fbm((h, w), seed + 3, 22, 5, octaves=3) - 0.62, 0, 1) * 2.4
    tone = base + t - 0.18 * depth + 0.10 * grit - 0.20 * stain + 0.04 * (wear - 0.5)
    crack = (np.abs(fbm((h, w), seed + 4, 10, 4, octaves=3) - 0.5) < 0.010) & ~joint
    tone = np.where(crack, tone - 0.20, tone)
    tone = np.where(lit, tone + 0.11, tone)
    tone = np.where(joint, tone - 0.30, tone)
    sand = joint & (fbm((h, w), seed + 6, 4, 1, octaves=2) > 0.62)
    tone = np.where(sand, base + 0.16, tone)
    # the back rows pale in the glare
    far = np.clip(1 - (sy - ytop) / 9.0, 0, 1)
    tone = tone * (1 - 0.40 * far) + 0.76 * 0.40 * far
    G = Layer(w, h)
    G.put(toned(np.clip(tone, 0.04, 1), CORAL, dither=0.5, x0=x0), np.ones((h, w), bool))
    L.paste(G, x0, ytop)


def earth_floor(L, x0, x1, ytop, seed=5, soot=0.0, warm=0.0):
    """A beaten earth floor, swept, with flags near the wall and dust where the sacks are dragged."""
    w = x1 - x0
    h = SH - ytop
    yy, xx = np.mgrid[0:h, 0:w]
    sy = yy + ytop
    depth = np.clip((sy - ytop) / float(SH - ytop), 0, 1)
    swirl = fbm((h, w), seed, 24, 3, octaves=3)
    grit = fbm((h, w), seed + 1, 1.2, 0.7, octaves=2) - 0.5
    drag = np.abs(np.sin((xx + x0) / 37.0 + swirl * 3)) < 0.06
    tone = 0.62 - 0.22 * depth + 0.12 * (swirl - 0.5) + 0.10 * grit - 0.08 * drag - soot * (0.3 + 0.3 * swirl)
    # a row of flags along the foot of the wall
    flag = (sy < ytop + 7)
    fx = ((xx + x0) // 26) % 2
    tone = np.where(flag, 0.70 + 0.06 * fx + 0.08 * grit - soot * 0.3, tone)
    tone = np.where(flag & ((xx + x0) % 26 == 0), tone - 0.26, tone)
    tone = np.where(sy == ytop + 7, tone - 0.20, tone)
    G = Layer(w, h)
    G.put(toned(np.clip(tone + warm, 0.04, 1), EARTH, dither=0.5, x0=x0), np.ones((h, w), bool))
    L.paste(G, x0, ytop)


def beans(L, x0, x1, y0, y1, n, seed=1):
    """Roasted beans spilled on the floor: a few dark specks with a glint."""
    r = rng(seed)
    for k in range(n):
        x = int(r.uniform(x0, x1))
        y = int(r.uniform(y0, y1))
        if 0 <= x < L.w - 1 and 0 <= y < L.h:
            L.rgb[y, x] = BEAN[2]
            L.rgb[y, x + 1] = BEAN[4] if r.random() < 0.5 else BEAN[1]
            L.a[y, x] = L.a[y, x + 1] = True


def shade_box(L, x0, y0, x1, y1, amt=0.75):
    """Darken what is already painted in a box (a shadow on the floor)."""
    x0, x1 = max(0, x0), min(L.w, x1)
    y0, y1 = max(0, y0), min(L.h, y1)
    if x1 <= x0 or y1 <= y0:
        return
    L.rgb[y0:y1, x0:x1] = (L.rgb[y0:y1, x0:x1].astype(float) * amt).astype(np.uint8)


def soft_shadow(L, x0, x1, y, h=5, amt=0.72):
    """A shadow pooled on the floor under something standing there: darkest at its foot."""
    for j in range(h):
        k = amt + (1 - amt) * j / float(h)
        shade_box(L, x0 + j, y + j - 1, x1 + j, y + j, k)


# ------------------------------------------------------------------ the quay
def coping(L, x0, x1, seed=7):
    """The edge of the quay at the back: big dressed blocks, a lit top, the drop to the water behind it."""
    T = Tone(L.w, L.h)
    r = rng(seed)
    x = x0
    while x < x1:
        bw = int(r.integers(18, 34))
        sh = r.uniform(-0.05, 0.05)
        for i in range(bw):
            if x + i >= x1:
                break
            T.px(x + i, QBACK - 3, 0.92 + sh)
            T.px(x + i, QBACK - 2, 0.80 + sh)
            T.px(x + i, QBACK - 1, 0.70 + sh)
            T.px(x + i, QBACK, 0.52 + sh)
            T.px(x + i, QBACK + 1, 0.36)
        T.rect(x, QBACK - 3, x, QBACK + 1, 0.30)
        x += bw
    put_tone(L, T, CORAL, dither=0.4)


def bollard(L, x, seed=1):
    """A cast-iron bollard on the coping, rusted, a rope round it."""
    T = Tone(L.w, L.h)
    y = QBACK - 2
    for j in range(11):
        half = 3 if j < 3 else (2 if j < 8 else 4)
        for i in range(-half, half + 1):
            T.px(x + i, y - 10 + j, 0.30 + 0.5 * np.exp(-((i + 1) / 2.0) ** 2) - 0.02 * j)
    put_tone(L, T, IRON, dither=0.3)
    R = Tone(L.w, L.h)
    for i in range(-4, 5):
        R.px(x + i, y - 5 + (abs(i) > 3), 0.66 + 0.2 * ((i + 9) % 3 == 0))
    put_tone(L, R, SACK, dither=0)


def dhow_trestles(L, x0=392, seed=11):
    """A sambuk hauled out on timber blocks for caulking: a raked stem, teak topsides with a carved band under the
    gunwale, the bottom limed white below a dark boot-top, a square stern with a window and the rudder hung off it, a
    mast raked forward and the lateen yard hoisted on it, its sail furled. Its deck and its poop are platforms."""
    T = Tone(L.w, L.h)            # teak
    Wt = Tone(L.w, L.h)           # the limed bottom
    S = Tone(L.w, L.h)            # the sail
    r = rng(seed)
    stern = 652

    def top(x):
        if x < 430:
            return 118 + (x - 392) * (138 - 118) / 38.0 if x >= 392 else 118
        if x < 600:
            return 138 - 2 * (x - 430) / 170.0
        return 124

    def bottom(x):
        if x < 440:
            return 118 + (x - 392) * (50 / 48.0)                     # the stem, raked
        if x < 636:
            return 168 + 2 * (x - 440) / 196.0                       # the keel
        return 170 - (x - 636) * 3.0                                 # the stern post, raked the other way

    WL = 153                                                         # the boot-top
    for x in range(392, stern + 1):
        tp, bt = int(round(top(x))), int(round(bottom(x)))
        if bt < tp:
            continue
        for y in range(tp, bt + 1):
            v = (y - tp) / max(1.0, bt - tp)
            if y < WL:
                hv = (y - tp) / max(1.0, WL - tp)
                t = 0.70 - 0.40 * hv ** 1.3 + 0.10 * (x < 470) * (1 - hv) - 0.10 * (x > 615)
                if (y - tp) % 3 == 0 and y > tp + 1:
                    t -= 0.08                                        # the strakes
                if y <= tp + 1:
                    t = 0.92                                         # the gunwale catching the sun
                elif y in (tp + 3, tp + 4):
                    t = 0.80 if (x // 3) % 2 else 0.58               # the carved band
                T.px(x, y, t + 0.03 * (r.random() - 0.5))
            elif y < WL + 2:
                T.px(x, y, 0.10)
            else:
                lv = (y - WL) / max(1.0, bt - WL)
                Wt.px(x, y, 0.86 - 0.42 * lv + 0.04 * ((x + y) % 3 == 0) - 0.14 * (abs(np.sin(x * 0.137 + y * 0.02)) < 0.05))
    # the stern: a carved transom, a window in it, the rudder hung off its post
    for y in range(118, 168):
        T.px(stern - (y - 118) * 0.32, y, 0.26)
    T.rect(632, 130, 642, 138, 0.14)
    T.rect(632, 129, 642, 129, 0.90)
    T.rect(631, 139, 643, 139, 0.86)
    for y in range(150, 175):
        for i in range(0, 6 + (y - 150) // 5):
            T.px(646 - (y - 150) * 0.2 + i, y, 0.30 - 0.05 * (i > 4))
    # the rails: a taffrail round the poop, a low rail forward
    for x in range(600, stern + 1):
        T.px(x, 117, 0.86)
        if x % 7 == 0:
            T.rect(x, 117, x, 123, 0.52)
    for x in range(394, 432):
        T.px(x, int(top(x)) - 4, 0.80)
        if x % 8 == 0:
            T.rect(x, int(top(x)) - 4, x, int(top(x)), 0.50)
    put_tone(L, T, TEAK, dither=0.4, grain=0.03, seed=seed)
    put_tone(L, Wt, LIME, dither=0.4)
    # timber blocks under the keel, as boats are laid up here
    F = Tone(L.w, L.h)
    for bx in (452, 534, 612):
        k = int(round(bottom(bx))) + 1
        y = k
        lay = 0
        while y < 182:
            bw = 14 if lay % 2 == 0 else 10
            F.rect(bx - bw // 2, y, bx + bw // 2, min(181, y + 4), 0.50 - 0.06 * lay)
            F.rect(bx - bw // 2, y, bx + bw // 2, y, 0.78)
            F.rect(bx + bw // 2, y, bx + bw // 2, min(181, y + 4), 0.28)
            y += 5
            lay += 1
    put_tone(L, F, TEAK, dither=0.3)
    soft_shadow(L, 440, 640, 183, 3, 0.80)
    # mast, raked forward; the yard hoisted on it, low at the bow and high over the stern, the sail furled along it
    M = Tone(L.w, L.h)
    for y in range(40, 137):
        mx = 522 - (137 - y) * 0.22
        M.px(mx, y, 0.66)
        M.px(mx + 1, y, 0.40)
    yx0, yy0, yx1, yy1 = 404, 98, 652, 6
    n = int(np.hypot(yx1 - yx0, yy1 - yy0))
    for i in range(n + 1):
        u = i / float(n)
        yx, yy_ = yx0 + (yx1 - yx0) * u, yy0 + (yy1 - yy0) * u
        M.px(yx, yy_, 0.56)
        th = 1 + int(3 * np.sin(np.pi * min(1, u * 1.15)) ** 0.7)          # the sail bunched thickest in the middle
        for j in range(1, th + 1):
            S.px(yx, yy_ + j, 0.92 - 0.12 * j - 0.10 * ((i // 7) % 2 == 0))
        if i % 11 == 0:
            S.px(yx, yy_ + th + 1, 0.50)                             # the gaskets tying it up
    for (ax, ay, bx, by) in ((501, 40, 396, 117), (501, 40, 650, 116), (404, 98, 404, 121)):
        M.line([(ax, ay), (bx, by)], 0.26)
    put_tone(L, M, TEAK, dither=0.2)
    put_tone(L, S, LIME, dither=0.3)
    # on deck: a water jar, a coil of rope, a bundle of sacks by the poop
    J = Tone(L.w, L.h)
    for j in range(9):
        half = [2, 3, 4, 4, 4, 4, 3, 3, 2][j]
        for i in range(-half, half + 1):
            J.px(470 + i, 128 + j, 0.80 - 0.10 * (i + half) / 2.0)
    put_tone(L, J, MUD, dither=0.3)
    R = Tone(L.w, L.h)
    for i in range(-5, 6):
        R.px(548 + i, 135 - (abs(i) < 4), 0.70 + 0.15 * (i % 2))
        R.px(548 + i, 134 - (abs(i) < 3), 0.56)
    put_tone(L, R, SACK, dither=0)
    plat('deck', [[404, 138], [520, 137], [600, 136]])
    plat('poop', [[600, 124], [648, 124]])
    INFO['dhow'] = [392, stern]


def crane(L, x0=712, seed=13):
    """A dockside crane on a portal: lattice legs, a walkway round the cab, the yellow cab with its windows and its
    counterweight, the jib reaching out over the dhow with a net of sacks on the hook. The walkway and the cab's roof
    are platforms."""
    C = Tone(L.w, L.h)            # crane yellow
    K = Tone(L.w, L.h)            # iron
    # the portal: two lattice legs, braced
    for lx in (x0, x0 + 86):
        for y in range(146, 181):
            K.px(lx, y, 0.66)
            K.px(lx + 1, y, 0.44)
            K.px(lx + 7, y, 0.40)
            K.px(lx + 8, y, 0.24)
            d = (y - 146) % 10
            K.px(lx + 1 + d * 6 // 10, y, 0.52)
            K.px(lx + 7 - d * 6 // 10, y, 0.34)
            if d == 0:
                K.rect(lx, y, lx + 8, y, 0.58)
        K.rect(lx - 3, 179, lx + 11, 181, 0.36)
        K.rect(lx - 3, 179, lx + 11, 179, 0.62)
    K.line([(x0 + 8, 148), (x0 + 86, 176)], 0.32)                     # one cross brace between the legs
    K.line([(x0 + 8, 176), (x0 + 86, 148)], 0.26)
    # the walkway at 142, its grating seen edge on, and a railing at the back
    for x in range(x0 + 4, x0 + 91):
        C.px(x, 142, 0.94)
        C.px(x, 143, 0.70)
        C.px(x, 144, 0.40 if x % 3 else 0.62)
        C.px(x, 145, 0.26)
        if x % 10 == 4:
            C.rect(x, 132, x, 141, 0.66)
        C.px(x, 132, 0.84)
        C.px(x, 136, 0.56)
    for x in range(x0 + 4, x0 + 91):                                 # hazard stripes along its edge
        if (x // 4) % 2 == 0:
            K.px(x, 145, 0.10)
    # the cab: a box with a low pitched roof, lit on its left
    for y in range(106, 142):
        for x in range(740, 795):
            u, v = (x - 740) / 54.0, (y - 106) / 35.0
            t = 0.80 - 0.22 * u - 0.12 * v + 0.03 * ((x + y) % 2)
            if (x - 740) % 18 == 0:
                t -= 0.12                                            # panel seams
            if y <= 107:
                t = 0.98 - 0.2 * u
            if x == 740:
                t = 0.94
            if x >= 793:
                t = 0.30
            C.px(x, y, t)
    for y in range(110, 140):                                        # rust streaks under the windows
        for x in (750, 768, 786):
            if y > 127 and (y + x) % 3:
                C.px(x, y, C.t[y, x] - 0.18)
    # the counterweight at the back
    for y in range(114, 141):
        for x in range(795, 814):
            K.px(x, y, 0.50 - 0.14 * (x - 795) / 19.0 + (0.18 if y == 114 else 0) - 0.06 * ((y - 114) % 6 == 0))
    # the jib: a lattice boom from the cab out over the dhow, two chords and the lacing between
    ax, ay, bx, by = 750, 108, 612, 22
    n = 46
    pts_t, pts_b = [], []
    for i in range(n + 1):
        u = i / float(n)
        x, y = ax + (bx - ax) * u, ay + (by - ay) * u
        w_ = 5 * (1 - 0.55 * u)
        pts_t.append((x, y))
        pts_b.append((x + w_ * 0.53, y + w_ * 0.85))
    C.line(pts_t, 0.92)
    C.line(pts_b, 0.52)
    for i in range(0, n, 2):
        C.line([pts_t[i], pts_b[i + 1]], 0.70)
        C.line([pts_b[i + 1], pts_t[min(n, i + 2)]], 0.60)
    C.rect(bx - 3, by - 2, bx + 3, by + 3, 0.74)
    C.line([(796, 106), (bx + 2, by)], 0.0)                         # the pendant from the counterweight's mast to the tip
    C.rect(796, 96, 798, 114, 0.62)
    put_tone(L, K, IRON, dither=0.3)
    put_tone(L, C, CRANE, dither=0.4, grain=0.04, seed=seed)
    Wn = Tone(L.w, L.h)                                              # the cab's windows, glass catching the low sun
    for wx in (745, 763, 781):
        Wn.rect(wx, 112, wx + 10, 124, 0.22)
        Wn.rect(wx, 112, wx + 10, 112, 0.04)
        Wn.rect(wx + 10, 112, wx + 10, 124, 0.40)
        for k in range(4):
            Wn.px(wx + 2 + k, 114 + k, 0.86)
        Wn.px(wx + 7, 121, 0.62)
    Wn.rect(741, 128, 793, 129, 0.30)
    put_tone(L, Wn, GLASS, dither=0.2)
    H = Tone(L.w, L.h)
    for i in range(0, 120):
        u = i / 119.0
        H.px(797 + (bx + 2 - 797) * u, 96 + (by - 96) * u, 0.40)
    for y in range(by + 3, 78):
        H.px(bx, y, 0.50)
    H.rect(bx - 2, 78, bx + 2, 80, 0.62)
    put_tone(L, H, IRON, dither=0)
    N = Layer(L.w, L.h)
    sack_pile(N, [(bx - 20, bx + 20, 82), (bx - 13, bx + 13, 82)], 101, seed=21, marks=True)
    L.paste(N)
    NT = Tone(L.w, L.h)
    for i in range(-21, 22):
        for j in range(0, 23):
            if (i + j) % 4 == 0 and abs(i) <= 20 - max(0, 4 - j) * 2:
                NT.px(bx + i, 80 + j, 0.40)
    put_tone(L, NT, P.NET, dither=0)
    plat('crane', [[716, 142], [802, 142]])
    plat('cab', [[740, 108], [794, 108]])


def coffee_stall(L, x0=980, seed=17):
    """A coffee seller's pitch on the quay: a red awning on poles, a bench, a charcoal stove with a pot on it, cups."""
    A = Tone(L.w, L.h)
    W_ = Tone(L.w, L.h)
    for px_ in (x0 + 4, x0 + 96):
        for y in range(116, 178):
            W_.px(px_, y, 0.56)
            W_.px(px_ + 1, y, 0.30)
    for x in range(x0, x0 + 104):
        sag = 3 * np.sin((x - x0) / 103.0 * np.pi)
        for y in range(116, int(126 + sag)):
            stripe = ((x - x0) // 8) % 2
            A.px(x, y, 0.70 - 0.30 * (y - 116) / 12.0 + 0.12 * stripe)
        # the scalloped edge
        if (x - x0) % 8 < 5:
            A.px(x, int(126 + sag), 0.40)
    put_tone(L, A, CLOTH_R, dither=0.35)
    # the bench, a carpet on it
    for x in range(x0 + 14, x0 + 70):
        W_.px(x, 166, 0.80)
        W_.px(x, 167, 0.50)
        for y in (168, 169):
            W_.px(x, y, 0.36)
    for lx in (x0 + 16, x0 + 66):
        W_.rect(lx, 168, lx + 1, 176, 0.40)
    put_tone(L, W_, TEAK, dither=0.3)
    R = Tone(L.w, L.h)
    for x in range(x0 + 16, x0 + 68):
        R.px(x, 165, 0.74 - 0.2 * ((x // 3) % 2))
        R.px(x, 164, 0.84 if x % 6 < 3 else 0.62)
    put_tone(L, R, CLOTH_B, dither=0)
    # the stove and the pot: a dallah, spout to the left
    S = Tone(L.w, L.h)
    S.rect(x0 + 78, 166, x0 + 90, 176, 0.36)
    S.rect(x0 + 78, 166, x0 + 90, 166, 0.70)
    put_tone(L, S, IRON, dither=0.3)
    D = Tone(L.w, L.h)
    cx_ = x0 + 84
    shape = [1, 1, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5]
    for j, half in enumerate(shape):
        for i in range(-half, half + 1):
            D.px(cx_ + i, 153 + j, 0.86 - 0.10 * (i + half) / max(1, half) + 0.08 * (j < 2))
    D.px(cx_, 151, 0.9)
    D.px(cx_, 152, 0.7)
    for k in range(5):                                      # the beak of a spout
        D.px(cx_ - 5 - k, 158 - k, 0.80)
    put_tone(L, D, COPPER, dither=0.2)
    for k, cx2 in enumerate((x0 + 30, x0 + 38, x0 + 46)):     # little cups on the bench
        L.rgb[162:164, cx2:cx2 + 3] = (236, 228, 204)
        L.rgb[161, cx2:cx2 + 3] = (120, 70, 30)
        L.a[161:164, cx2:cx2 + 3] = True


def quay(L):
    paving(L, 0, WH - 8, QBACK, seed=3)
    coping(L, 0, WH - 20)
    for bx in (88, 330, 690, 880, 1100):
        bollard(L, bx)
    # the skiff that put Yazeed ashore: only its mast and the top of its bow show over the coping, and the ladder up
    T = Tone(L.w, L.h)
    for y in range(64, QBACK - 3):
        T.px(52 + (QBACK - y) * 0.06, y, 0.58)
    for x in range(24, 92):
        T.px(x, QBACK - 4 - int(3 * np.exp(-((x - 90) / 10.0) ** 2)), 0.70)
    for y in range(QBACK - 3, QBACK + 14):
        T.px(66, y, 0.50)
        T.px(74, y, 0.40)
        if y % 4 == 0:
            T.rect(66, y, 74, y, 0.62)
    put_tone(L, T, TEAK, dither=0.3)
    F = Tone(L.w, L.h)
    for y in range(66, 100):
        F.px(53 + (QBACK - y) * 0.06 + 1, y, 0.86 - 0.2 * ((y // 5) % 2))
    put_tone(L, F, LIME, dither=0)
    # the first pile of sacks, on a pallet: two steps up
    Pp = Tone(L.w, L.h)
    for x in range(178, 254):
        Pp.px(x, 180, 0.70)
        Pp.px(x, 181, 0.40 if x % 9 else 0.62)
        Pp.px(x, 182, 0.30)
        Pp.px(x, 183, 0.40 if x % 12 < 2 else 0.18)
    put_tone(L, Pp, TEAK, dither=0)
    sack_pile(L, [(180, 252, 164), (196, 236, 150)], 180, seed=31)
    soft_shadow(L, 254, 266, 183, 3)
    plat('pile1', [[182, 164], [248, 164]])
    plat('pile1top', [[198, 150], [232, 150]])
    # lamp posts
    LP = Tone(L.w, L.h)
    lamp_post(LP, 344, 182)
    lamp_post(LP, 1150, 182)
    put_tone(L, LP, IRON, dither=0.2)
    lantern_glass(L, 353, 116)
    lantern_glass(L, 1159, 116)
    # a crate to step up from, by the dhow's bow
    CT = Tone(L.w, L.h)
    crate_tone(CT, 370, 162, 27, 22, seed=5)
    crate_tone(CT, 688, 166, 27, 18, seed=6)
    crate_tone(CT, 1040, 170, 22, 14, seed=7)
    crate_tone(CT, 1062, 170, 22, 14, seed=8)
    crate_tone(CT, 1050, 156, 24, 14, seed=9)
    put_tone(L, CT, TEAK, dither=0.35)
    soft_shadow(L, 397, 405, 183, 3)
    plat('step1', [[370, 162], [396, 162]])
    plat('crate2', [[688, 166], [714, 166]])
    dhow_trestles(L)
    crane(L)
    coffee_stall(L)
    # fish crates and a hand cart of sacks by the warehouse
    sack_pile(L, [(1092, 1136, 166)], 176, seed=33)
    CW = Tone(L.w, L.h)
    for x in range(1088, 1140):
        CW.px(x, 176, 0.70)
        CW.px(x, 177, 0.40)
    for (wx, wy) in ((1096, 180), (1130, 180)):
        for a in range(0, 360, 20):
            CW.px(wx + 4 * np.cos(np.radians(a)), wy + 4 * np.sin(np.radians(a)), 0.30)
        CW.px(wx, wy, 0.6)
    for k in range(18):
        CW.px(1140 + k, 176 - k // 2, 0.52)
    put_tone(L, CW, TEAK, dither=0.2)
    beans(L, 150, 1160, 168, 214, 70, seed=4)


# ------------------------------------------------------------------ sky, the town across the harbour, the harbour
def sky_m(w=1404, seed=5):
    """Late afternoon: deep blue overhead, a warm haze low down, a few heaps of cloud lit gold on their left."""
    h = HORIZON + 6
    yy = np.arange(h)[:, None] / float(HORIZON)
    xx = np.arange(w)[None, :]
    tone = 0.05 + 0.80 * np.clip(yy, 0, 1) ** 1.6 + 0 * xx
    cir = fbm((h, w), seed, 60, 1.4, octaves=3)
    tone += np.clip(cir - 0.58, 0, 1) * 0.7 * np.exp(-((yy - 0.36) / 0.22) ** 2)
    far = [(x, HORIZON - 2 + (i % 3), 100 + 30 * (i % 2), 7 + 4 * (i % 3), 40, 2.5, 5.0) for i, x in enumerate(range(20, w, 66))]
    Zf = ndi.gaussian_filter(SL.puffs_wrap(h, w, far, seed + 40), 1.1, mode='wrap')
    covf = np.clip(Zf * 0.5, 0, 1)
    litf = light(Zf, -0.6, -0.8, 0.5)
    tf = 0.84 + 0.10 * np.clip(litf, -1, 1)
    tone = tone + covf * 0.8 * (np.clip(tf, 0.70, 0.96) - tone)
    big = [(150, 86, 160, 52, 150, 4.0, 10.0), (470, 92, 120, 30, 90, 3.5, 8.0), (760, 88, 190, 46, 160, 4.0, 10.0),
           (1060, 92, 110, 26, 80, 3.5, 7.5), (1280, 90, 150, 40, 130, 4.0, 9.0)]
    Z = SL.puffs_wrap(h, w, big, seed + 41)
    Zs = ndi.gaussian_filter(Z, 0.7, mode='wrap')
    cov = np.clip(Z * 0.8, 0, 1)
    lit = light(Zs, -0.55, -0.85, 0.5)
    floor = np.zeros((h, w))
    for cx, base, width, height, n, r0, r1 in big:
        dx = (xx - cx + w / 2.0) % w - w / 2.0
        f = np.clip(1 - (base - np.arange(h)[:, None]) / (height * 0.6), 0, 1) * (np.abs(dx) < width * 0.62)
        floor = np.maximum(floor, f)
    shade = noise((h, w), seed + 50, 22, 12)
    ct = 0.80 + 0.40 * np.clip(lit, -1, 1) - 0.34 * floor ** 1.5 - 0.10 * (shade - 0.5)
    cov = cov * (1 - 0.5 * floor ** 3)
    tone = tone + cov * (np.clip(ct, 0.36, 1.0) - tone)
    L = Layer(w, h)
    L.put(toned(np.clip(tone, 0, 1), SKYM, dither=0.7), np.ones((h, w), bool))
    return L


def _tower_house(T, x, wl, hgt, wid, seed, ruined=False):
    """A merchant's tower house, whitewashed, far off: a lit face, a shaded side, rows of windows, a parapet."""
    r = rng(seed)
    top = wl - hgt
    for y in range(top, wl):
        for i in range(wid):
            u = i / float(max(1, wid - 1))
            t = 0.90 - 0.30 * (u > 0.72) - 0.04 * ((y - top) / float(hgt))
            T.px(x + i, y, t)
    # parapet: little crenels; or broken off if it is a ruin
    for i in range(wid):
        if ruined:
            dy = int(abs(np.sin(i * 1.7 + seed)) * 4)
            for y in range(top, top + dy):
                T.m[y, x + i] = False
        elif i % 3 == 0:
            T.px(x + i, top - 1, 0.94)
            T.px(x + i, top - 2, 0.94)
    # windows: dark, in rows, a decorated band between floors
    for fy in range(top + 4, wl - 3, 6):
        for i in range(2, wid - 2, 4):
            if r.random() < 0.85:
                T.px(x + i, fy, 0.30)
                T.px(x + i, fy + 1, 0.36)
        for i in range(wid):
            if i % 2 == 0:
                T.px(x + i, fy - 2, 0.80)


def far_m(w=2808, seed=9):
    """Mocha across the harbour: the old town along the shore, its tower houses whitewashed and some of them roofless,
    palms between them, the walls of the old fort, the mountains far inland in the haze, dhows at anchor."""
    h, wl = ST.FAR_H, ST.FAR_WATER
    yy, xx = np.mgrid[0:h, 0:w]
    L = Layer(w, h)
    # the mountains inland, faint
    for i, (sd, amp, sx, t0) in enumerate([(seed, 26, 140, 0.84), (seed + 9, 14, 80, 0.76)]):
        top = ST._ridge(w, sd, wl - 6, amp, sx)
        fade = np.clip(np.sin(2 * np.pi * np.arange(w) / w * 2 + i * 1.7) * 0.5 + 0.7, 0.2, 1)
        top = wl - 6 - (wl - 6 - top) * fade
        m = (yy >= top[None, :]) & (yy < wl)
        tone = t0 + 0.05 * np.clip((yy - top[None, :]) / 12.0, 0, 1) + 0.03 * (noise((h, w), sd + 3, 6, 2) - 0.5)
        L.put(toned(np.clip(tone, 0, 1), HAZEM, dither=0.6), m)
    T = Tone(w, h)
    r = rng(seed + 20)
    # a strip of shore under the town
    for x in range(w):
        T.px(x, wl - 1, 0.62)
        T.px(x, wl - 2, 0.70)
    # the town: clusters of tower houses with gaps for palms, wrapping round
    x = 10
    k = 0
    while x < w - 40:
        cluster = int(r.integers(3, 8))
        for c in range(cluster):
            wid = int(r.integers(9, 18))
            hgt = int(r.integers(10, 34))
            if x + wid >= w - 4:
                break
            _tower_house(T, x, wl - 2, hgt, wid, seed + k, ruined=r.random() < 0.18)
            x += wid + int(r.integers(0, 3))
            k += 1
        # palms in the gap
        for p in range(int(r.integers(1, 4))):
            px_ = x + 4 + p * 7
            if px_ >= w - 8:
                break
            ph = int(r.integers(10, 22))
            for y in range(wl - 2 - ph, wl - 2):
                T.px(px_, y, 0.42)
            for a in range(7):
                ang = -np.pi * (0.1 + 0.8 * a / 6.0)
                for i in range(5):
                    T.px(px_ + np.cos(ang) * i, wl - 2 - ph + np.sin(ang) * i + 0.15 * i * i, 0.40)
        x += int(r.integers(20, 70))
    # the old fort: a low wall with round towers
    fx0 = 1500
    for x in range(fx0, fx0 + 120):
        for y in range(wl - 14, wl - 2):
            T.px(x, y, 0.82 - 0.06 * ((x - fx0) // 30 % 2))
        if x % 4 < 2:
            T.px(x, wl - 15, 0.86)
    for tx in (fx0, fx0 + 60, fx0 + 118):
        for y in range(wl - 22, wl - 2):
            for i in range(-4, 5):
                T.px(tx + i, y, 0.88 - 0.25 * (i > 1))
        for i in range(-4, 5, 2):
            T.px(tx + i, wl - 23, 0.9)
    # dhows at anchor
    for dx in (300, 980, 1880, 2460):
        ST._dhow(T, dx, wl + 1)
    L.paste(T.layer(HAZEM, dither=0.5, grain=0.04, seed=seed + 30))
    return L


def sea_m(w=1320, seed=13):
    """The harbour: calm, green near the quay, the low sun glinting on it."""
    h = 52
    yy, xx = np.mgrid[0:h, 0:w]
    v = yy / float(h - 1)
    base = 0.70 - 0.40 * v + 0.06 * np.sin(v * 9)
    tone = np.zeros((h, w))
    src = fbm((h, w * 2), seed, 12, 0.6, octaves=3)
    for y in range(h):
        s_ = 0.35 + 1.6 * (y / (h - 1.0))
        xs = (np.arange(w) / s_ + 41 * y) % (w * 2 - 1)
        tone[y] = np.interp(xs, np.arange(w * 2), src[y])
    t = base + 0.18 * (tone - 0.5)
    t[0] = 0.88
    t[1] = np.maximum(t[1], 0.78)
    glint = (fbm((h, w), seed + 5, 3, 0.5, octaves=2) > 0.80) & (v < 0.7)
    t = np.where(glint, t + 0.24, t)
    L = Layer(w, h)
    L.put(toned(np.clip(t, 0.05, 0.98), HARBOUR, dither=0.6), np.ones((h, w), bool))
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
                sc.rgb[WALK, xs] = (40, 255, 120)
        sheet.paste(sc, (i % 2) * (w + 6), (i // 2) * (SH + 6))
    im = sheet.image()
    im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
    im.save(path)
    return im.size


# ------------------------------------------------------------------ inside: the warehouses and the roasting house
def ceiling(L, x0, x1, seed=21, soot=0.0):
    """The underside of a flat roof: mangrove poles laid close across heavy beams, the cut edge of the roof above."""
    T = Tone(L.w, L.h)
    r = rng(seed)
    for x in range(x0, x1):
        T.px(x, 0, 0.86 - soot)
        T.px(x, 1, 0.74 - soot)
        T.px(x, 2, 0.60 - soot)
        T.px(x, 3, 0.34 - soot * 0.5)
        # the poles: slanted strokes, one every 3 px
        for y in range(4, 19):
            u = (x + (y - 4) * 0.35) % 3
            t = 0.52 - 0.02 * (y - 4) + (0.16 if u < 1 else (-0.10 if u >= 2 else 0)) - soot
            T.px(x, y, t)
        # the beam along the back wall
        T.px(x, 19, 0.70 - soot)
        for y in range(20, 25):
            T.px(x, y, 0.40 - 0.04 * (y - 20) - soot * 0.6)
        T.px(x, 25, 0.16)
    # big beams across, every so often, with a bracket under each
    bx = x0 + int(r.integers(60, 140))
    while bx < x1 - 10:
        for y in range(3, 26):
            for i in range(9):
                xx_ = bx + i - int((y - 3) * 0.35)
                if x0 <= xx_ < x1:
                    T.px(xx_, y, (0.62 if i < 2 else (0.20 if i > 6 else 0.38)) - soot * 0.6)
        for k in range(6):
            T.px(bx - 1 + k, 26 + k, 0.30)
            T.px(bx + k, 26 + k, 0.46)
        bx += int(r.integers(170, 240))
    put_tone(L, T, TEAK, dither=0.4, grain=0.03, seed=seed)


def lime_wall(L, x0, x1, ytop=26, ybot=WALLB, seed=23, grime=1.0, warm=0.0):
    """A back wall of coral stone under lime wash: grimy toward the floor, streaked under the windows, the plaster
    fallen away here and there to show the stone."""
    w = x1 - x0
    h = ybot - ytop
    yy, xx = np.mgrid[0:h, 0:w]
    sy = yy + ytop
    X = xx + x0
    v = yy / float(h)
    tone = 0.64 - 0.10 * v + 0.05 * (fbm((h, w), seed, 30, 20, octaves=3) - 0.5) + warm
    tone -= grime * 0.30 * np.clip((v - 0.62) / 0.38, 0, 1) ** 1.5
    tone -= grime * 0.10 * np.clip(fbm((h, w), seed + 1, 3, 40, octaves=2) - 0.55, 0, 1) * 3       # streaks
    tone += 0.04 * (fbm((h, w), seed + 2, 1.2, 0.8, octaves=2) - 0.5)
    G = Layer(w, h)
    G.put(toned(np.clip(tone, 0.04, 1), LIME, dither=0.5, x0=x0), np.ones((h, w), bool))
    # the stone where the plaster has gone
    pat = (fbm((h, w), seed + 3, 16, 9, octaves=3) > 0.79) & (v > 0.08) & (v < 0.92)
    blocks = ((sy // 6) % 2 == 0) & ((X // 13) % 2 == 0) | ((sy // 6) % 2 == 1) & (((X + 6) // 13) % 2 == 0)
    st = 0.50 + 0.10 * blocks - 0.16 * ((sy % 6) == 0) - 0.14 * (((X + 6 * ((sy // 6) % 2)) % 13) == 0) - 0.12 * v
    S_ = Layer(w, h)
    S_.put(toned(np.clip(st, 0, 1), MUD, dither=0.4, x0=x0), pat)
    G.paste(S_)
    # the plinth along the foot
    for y in range(h - 6, h):
        k = y - (h - 6)
        tt = 0.40 - 0.04 * k + (0.18 if k == 0 else 0)
        G.rgb[y, :] = LIME[int(np.clip(tt, 0, 1) * (len(LIME) - 1))]
    L.paste(G, x0, ytop)


def window(L, x, y=40, w=12, h=20, seed=1):
    """A small arched window high in the wall, its shutters open: the sky shows through it."""
    T = Tone(L.w, L.h)
    for j in range(-2, h + 2):
        for i in range(-2, w + 2):
            inside = 0 <= i < w and 0 <= j < h
            arch = j < w // 2 and (i - (w - 1) / 2.0) ** 2 + (j - w // 2) ** 2 > (w / 2.0) ** 2
            if inside and not arch:
                L.a[y + j, x + i] = False                            # a hole: the sky shows through
            elif (i in (-2, -1, w, w + 1) or j in (-2, -1, h, h + 1)) and not (arch and inside):
                T.px(x + i, y + j, 0.86 if (i < 0 or j < 0) else 0.52)
    put_tone(L, T, LIME, dither=0)
    S_ = Tone(L.w, L.h)
    for j in range(h):
        S_.px(x - 4, y + j + 1, 0.56)
        S_.px(x - 3, y + j + 1, 0.40)
        S_.px(x + w + 2, y + j + 1, 0.50)
        S_.px(x + w + 3, y + j + 1, 0.34)
    put_tone(L, S_, TEAK, dither=0)


def light_shaft(L, x, y0, y1, w=12, slope=0.55, lift=1.10, floor_y=WALLB):
    """Sunlight from a high window falling across the room: the wall and the floor it lands on are lifted a little,
    with motes of dust in the air."""
    for y in range(y0, y1):
        xs = int(x + (y - y0) * slope)
        a, b = max(0, xs), min(L.w, xs + w + (y - y0) // 8)
        seg = L.rgb[y, a:b].astype(float)
        k = lift if y < floor_y else lift + 0.06
        L.rgb[y, a:b] = np.clip(seg * k + 6, 0, 255).astype(np.uint8)
    r = rng(int(x))
    for k in range(18):
        yy = int(r.uniform(y0 + 4, y1 - 4))
        xx = int(x + (yy - y0) * slope + r.uniform(0, w))
        if 0 <= xx < L.w and 0 <= yy < L.h and L.a[yy, xx]:
            L.rgb[yy, xx] = (255, 244, 210)


def back_door(L, x, w=26, h=44, seed=1, open_left=True):
    """A doorway in the back wall: a stone arch, dark inside, one heavy leaf swung open (they come out of these)."""
    T = Tone(L.w, L.h)
    D = Tone(L.w, L.h)
    y1 = WALLB
    y0 = y1 - h
    for j in range(h):
        for i in range(w):
            arch = j < w // 2 and (i - (w - 1) / 2.0) ** 2 + (j - w // 2) ** 2 > (w / 2.0) ** 2
            if not arch:
                D.px(x + i, y0 + j, 0.10 + 0.08 * (j / float(h)) + 0.05 * (i > w * 0.6))
    for j in range(-3, h):
        for i in range(-3, w + 3):
            arch_out = j < w // 2 + 3 and (i - (w - 1) / 2.0) ** 2 + (j - w // 2) ** 2 > ((w + 6) / 2.0) ** 2
            arch_in = j < w // 2 and (i - (w - 1) / 2.0) ** 2 + (j - w // 2) ** 2 > (w / 2.0) ** 2
            inside = 0 <= i < w and 0 <= j and not arch_in
            if not arch_out and not inside:
                T.px(x + i, y0 + j, 0.80 - 0.30 * (i > w // 2) + (0.10 if j < 0 else 0))
    put_tone(L, T, CORAL, dither=0.3)
    put_tone(L, D, SOOT, dither=0.5)
    # the open leaf: teak, iron studs
    F = Tone(L.w, L.h)
    lx = x - 9 if open_left else x + w
    for j in range(8, h):
        for i in range(9):
            sk = (i * 0.6) if open_left else ((8 - i) * 0.6)
            yy = y0 + j - int(sk)
            t = 0.50 - 0.04 * i + 0.08 * ((j % 6) == 0)
            if (i + j) % 7 == 0 and j % 6 == 3:
                t = 0.86
            F.px(lx + i, yy, t)
    put_tone(L, F, TEAK, dither=0.3)
    INFO.setdefault('doors', []).append(x + w // 2)


def gallery(L, x0, x1, y, posts, seed=27):
    """A wooden gallery along the back wall: planked deck (a platform), joists, posts down to the floor, a rail."""
    T = Tone(L.w, L.h)
    for x in range(x0, x1 + 1):
        if (x - x0) % 16 == 0:
            T.rect(x, y - 15, x + 1, y - 1, 0.56)
            T.px(x, y - 15, 0.80)
        T.px(x, y - 15, 0.74)
        T.px(x, y - 8, 0.62)
        T.px(x, y, 0.94)
        T.px(x, y + 1, 0.72)
        T.px(x, y + 2, 0.50)
        T.px(x, y + 3, 0.34 if (x - x0) % 12 else 0.56)
        T.px(x, y + 4, 0.22)
        T.px(x, y + 5, 0.16 if (x - x0) % 30 < 4 else 0.0)
    for px_ in posts:
        for yy in range(y + 5, WALLB + 6):
            T.px(px_, yy, 0.64)
            T.px(px_ + 1, yy, 0.46)
            T.px(px_ + 2, yy, 0.30)
        T.line([(px_ - 8, y + 5), (px_, y + 13)], 0.40)
        T.line([(px_ + 10, y + 5), (px_ + 2, y + 13)], 0.32)
    T.m &= ~((T.t == 0.0) & T.m)
    put_tone(L, T, TEAK, dither=0.3, grain=0.03, seed=seed)
    for px_ in posts:
        soft_shadow(L, px_ + 3, px_ + 8, WALLB + 6, 3, 0.8)


def scales(L, x, seed=31):
    """The big beam scale the sacks are weighed on: a timber gallows, an iron beam, a platform on chains."""
    T = Tone(L.w, L.h)
    K = Tone(L.w, L.h)
    for px_ in (x - 22, x + 22):
        for y in range(92, 172):
            T.px(px_, y, 0.62)
            T.px(px_ + 1, y, 0.42)
            T.px(px_ + 2, y, 0.26)
    T.rect(x - 26, 90, x + 27, 93, 0.56)
    T.rect(x - 26, 90, x + 27, 90, 0.86)
    put_tone(L, T, TEAK, dither=0.3)
    K.rect(x - 1, 94, x + 1, 100, 0.50)
    for i in range(-20, 21):
        K.px(x + i, 101 + int(i * 0.08), 0.66)
        K.px(x + i, 102 + int(i * 0.08), 0.40)
    K.rect(x + 18, 103, x + 21, 110, 0.30)                          # the weight
    for j in range(104, 140):
        K.px(x - 18 + (j - 104) * 0.08, j, 0.46)
        K.px(x - 2 - (j - 104) * 0.08, j, 0.46)
    K.rect(x - 22, 140, x + 2, 142, 0.56)
    K.rect(x - 22, 140, x + 2, 140, 0.80)
    put_tone(L, K, IRON, dither=0.2)
    N = Layer(L.w, L.h)
    sack_pile(N, [(x - 20, x + 1, 128)], 140, seed=37)
    L.paste(N)


def hoist(L, x, seed=33):
    """A tackle from the beam and a net of sacks on its hook, halfway up."""
    K = Tone(L.w, L.h)
    K.rect(x - 3, 26, x + 3, 32, 0.50)
    for y in range(32, 70):
        K.px(x - 1, y, 0.62)
        K.px(x + 1, y, 0.44)
    K.rect(x - 2, 70, x + 2, 73, 0.66)
    put_tone(L, K, IRON, dither=0.2)
    N = Layer(L.w, L.h)
    sack_pile(N, [(x - 20, x + 20, 76), (x - 14, x + 14, 76)], 96, seed=39)
    L.paste(N)
    NT = Tone(L.w, L.h)
    for i in range(-21, 22):
        for j in range(0, 22):
            if (i + j) % 4 == 0 and abs(i) <= 20 - max(0, 4 - j) * 2:
                NT.px(x + i, 74 + j, 0.40)
    put_tone(L, NT, P.NET, dither=0)


def wall_slice(L, x0, x1, door=(118, 176), seed=41, soot_right=False, roof=True, inside=EARTH):
    """The end of a building, cut through: a thick wall of whitewashed stone from the roof to the floor, the stone
    showing where it is cut, and an arched passage through it that the squad walks along: dark, with the floor
    running through."""
    T = Tone(L.w, L.h)
    D = Tone(L.w, L.h)
    w = x1 - x0
    cx_ = x0 + w / 2.0
    dw = (w - 8) / 2.0
    for x in range(x0, x1):
        u = (x - x0) / float(max(1, w - 1))
        for y in range(0 if roof else 26, SH):
            if door and y >= door[0]:
                inside_ = abs(x - cx_) < dw and (y > door[0] + dw or (x - cx_) ** 2 + (y - door[0] - dw) ** 2 < dw ** 2)
                if inside_:
                    if y < WALLB + 4:
                        D.px(x, y, 0.12 + 0.10 * (y - door[0]) / 60.0 + 0.06 * (abs(x - cx_) > dw - 2))
                    continue
            edge = x in (x0, x1 - 1)
            course = (y // 6) % 2
            stone = ((x + 7 * course) % 12 == 0) or (y % 6 == 0)
            t = 0.80 - 0.30 * u - 0.10 * (y > 170) + (0.06 if edge and x == x0 else 0) - (0.16 if edge and x != x0 else 0)
            t -= 0.08 * stone * (0.3 + 0.7 * (abs(u - 0.5) < 0.42))
            if soot_right and u > 0.5:
                t -= 0.24 * (u - 0.5) * 2 * (1 - y / 260.0)
            if y < 3:
                t = 0.96
            T.px(x, y, t)
    put_tone(L, T, LIME, dither=0.4, grain=0.03, seed=seed)
    put_tone(L, D, SOOT, dither=0.5)


def warehouses(L):
    ceiling(L, WH, RH - 20, seed=21)
    lime_wall(L, WH, RH - 20, seed=23)
    earth_floor(L, WH - 26, RH, WALLB, seed=5)
    # windows high in the back wall, and the light coming in through them
    wins = [1290, 1420, 1600, 1760, 1930, 2080, 2250, 2390]
    for wx in wins:
        window(L, wx, 40)
    # piles of sacks against the back wall: the Scorpion has taken every one
    for (a, b, top, sd) in ((1250, 1330, 112, 41), (1352, 1420, 128, 42), (1600, 1650, 140, 43), (1880, 1960, 132, 44),
                            (1990, 2060, 120, 45), (2160, 2240, 116, 46), (2300, 2420, 104, 47)):
        sack_pile(L, [(a, b, top), (a + 8, b - 8, top - 8)], WALLB + 2, seed=sd)
    for dx in (1566, 1846, 2124):
        back_door(L, dx - 13)
    gallery(L, 1500, 1966, 122, posts=[1512, 1620, 1730, 1840, 1952])
    plat('gallery', [[1500, 122], [1966, 122]])
    # on the gallery, against the wall: more sacks
    sack_pile(L, [(1560, 1600, 104), (1790, 1830, 108)], 120, seed=48)
    scales(L, 2020)
    hoist(L, 2350)
    # the steps up to the gallery, a pile under it, the pile by the scales
    sack_pile(L, [(1436, 1470, 166), (1462, 1500, 148)], 183, seed=51)
    plat('sk1', [[1436, 166], [1470, 166]])
    plat('sk2', [[1462, 148], [1500, 148]])
    sack_pile(L, [(1650, 1700, 158)], 183, seed=52)
    plat('pile3', [[1650, 158], [1700, 158]])
    sack_pile(L, [(2180, 2242, 162)], 183, seed=53)
    plat('pile2', [[2180, 162], [2242, 162]])
    for (a, b) in ((1436, 1500), (1650, 1700), (2180, 2242)):
        soft_shadow(L, b, b + 10, 183, 3)
    beans(L, WH, RH - 24, WALLB + 4, 214, 140, seed=7)
    for wx in wins:
        light_shaft(L, wx, 42, WALLB + 30, w=11, slope=0.62)
    # the end walls: the warehouse's, with the gateway in from the quay; the partition into the roasting house
    wall_slice(L, WH - 26, WH + 6, door=(112, 176), seed=41)
    wall_slice(L, RH - 20, RH + 12, door=(112, 176), seed=42, soot_right=True)


# ------------------------------------------------------------------ the roasting house
def brick_wall(L, x0, x1, ytop=26, ybot=WALLB, seed=61):
    """Mud brick, laid in courses, black with years of smoke toward the roof."""
    w = x1 - x0
    h = ybot - ytop
    yy, xx = np.mgrid[0:h, 0:w]
    sy = yy + ytop
    X = xx + x0
    v = yy / float(h)
    course = (sy // 5) % 2
    mortar = (sy % 5 == 0) | (((X + 6 * course) % 12) == 0)
    r = rng(seed)
    brick = noise((h, w), seed, 5, 2)
    tone = 0.56 + 0.10 * (brick - 0.5) - 0.20 * mortar + 0.04 * ((((X + 6 * course) % 12) == 1) & ~mortar)
    tone -= 0.52 * np.clip(1 - v * 1.35, 0, 1) ** 1.3                       # smoke, thickest under the roof
    tone -= 0.14 * np.clip((v - 0.8) / 0.2, 0, 1)
    tone += 0.05 * (fbm((h, w), seed + 1, 1.2, 0.8, octaves=2) - 0.5)
    G = Layer(w, h)
    G.put(toned(np.clip(tone, 0.02, 1), MUD, dither=0.5, x0=x0), np.ones((h, w), bool))
    L.paste(G, x0, ytop)


def glow(L, cx, cy, r, amt=0.55, col=(255, 150, 60)):
    """The light of a fire on whatever is near it."""
    x0, x1 = max(0, int(cx - r)), min(L.w, int(cx + r))
    y0, y1 = max(0, int(cy - r)), min(L.h, int(cy + r))
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.3) ** 2) / r
    k = np.clip(1 - d, 0, 1) ** 1.6 * amt
    # quantise the falloff into a few bands, dithered, so it stays pixel art
    k = np.floor(k * 6 + 0.5 * ((xx + yy) % 2)) / 6.0
    sub = L.rgb[y0:y1, x0:x1].astype(float)
    c = np.array(col, float)
    out = sub * (1 - k[..., None]) + (sub * 0.5 + c * 0.5) * k[..., None] * 1.25
    L.rgb[y0:y1, x0:x1] = np.clip(out, 0, 255).astype(np.uint8)


def roaster_drum(L, cx, seed=1, pipe_top=26):
    """A roaster: a brick firebox with its door glowing, a copper drum on it with a crank wheel at its end, a pipe up
    through the roof for the smoke, and a cooling tray in front of it with the beans being turned."""
    B = Tone(L.w, L.h)
    # the firebox
    x0, x1 = cx - 36, cx + 36
    for y in range(148, 170):
        for x in range(x0, x1):
            course = (y // 4) % 2
            mortar = (y % 4 == 0) or ((x + 5 * course) % 10 == 0)
            t = 0.58 - 0.18 * mortar - 0.20 * (x - x0) / 72.0 + (0.12 if y == 148 else 0)
            B.px(x, y, t)
    put_tone(L, B, MUD, dither=0.4)
    F = Tone(L.w, L.h)
    for y in range(154, 169):
        for x in range(cx - 9, cx + 9):
            arch = y < 159 and (x - cx + 0.5) ** 2 + (y - 159) ** 2 > 81
            if not arch:
                F.px(x, y, 0.62 + 0.36 * (1 - abs(x - cx) / 9.0) * ((y - 154) / 15.0) ** 0.5 + 0.08 * ((x * 3 + y) % 4 == 0))
    put_tone(L, F, FIRE, dither=0.3)
    # the drum: copper, lit from the upper left, banded with iron
    C = Tone(L.w, L.h)
    dx0, dx1, top, bot = cx - 30, cx + 30, 122, 148
    for y in range(top, bot):
        v = (y - top) / float(bot - top - 1)
        for x in range(dx0, dx1):
            u = (x - dx0) / float(dx1 - dx0 - 1)
            t = 0.36 + 0.56 * np.exp(-((v - 0.30) / 0.22) ** 2) - 0.16 * u + 0.06 * ((x + y) % 2)
            if y in (top, bot - 1):
                t -= 0.20
            C.px(x, y, t)
    put_tone(L, C, COPPER, dither=0.3)
    K = Tone(L.w, L.h)
    for bx in (dx0 + 4, cx, dx1 - 5):
        for y in range(top, bot):
            K.px(bx, y, 0.40 + 0.2 * (y < top + 8))
            K.px(bx + 1, y, 0.24)
    # the crank wheel at its left end
    for a in range(0, 360, 12):
        K.px(dx0 - 3 + 8 * np.cos(np.radians(a)) * 0.4, 135 + 8 * np.sin(np.radians(a)), 0.62)
    for a in range(0, 360, 60):
        K.line([(dx0 - 3, 135), (dx0 - 3 + 8 * np.cos(np.radians(a)) * 0.4, 135 + 8 * np.sin(np.radians(a)))], 0.48)
    K.rect(dx0 - 8, 134, dx0 - 4, 136, 0.70)
    # the hopper on top and the pipe up through the roof
    for j in range(8):
        K.rect(cx - 10 + j, 114 + j, cx + 10 - j, 114 + j, 0.46 + 0.04 * j)
    for y in range(pipe_top, 114):
        K.px(cx + 14, y, 0.56)
        K.px(cx + 15, y, 0.40)
        K.px(cx + 16, y, 0.30)
        K.px(cx + 17, y, 0.20)
        if y % 22 == 0:
            K.rect(cx + 13, y, cx + 18, y + 1, 0.62)
    K.rect(cx + 12, 114, cx + 19, 122, 0.40)
    put_tone(L, K, IRON, dither=0.3)
    # the cooling tray, beans turning in it
    T = Tone(L.w, L.h)
    for x in range(cx - 26, cx + 26):
        u = (x - cx) / 26.0
        h_ = int(3 * np.sqrt(max(0, 1 - u * u)))
        T.px(x, 172 - h_, 0.80)
        T.px(x, 173, 0.40)
        T.px(x, 174, 0.30)
    for lx in (cx - 22, cx + 22):
        T.rect(lx, 174, lx, 180, 0.40)
    put_tone(L, T, IRON, dither=0)
    Bn = Tone(L.w, L.h)
    for x in range(cx - 24, cx + 24):
        u = (x - cx) / 24.0
        h_ = int(3 * np.sqrt(max(0, 1 - u * u)))
        for y in range(172 - h_ + 1, 173):
            Bn.px(x, y, 0.4 + 0.3 * ((x * 5 + y * 3) % 4 == 0))
    put_tone(L, Bn, BEAN, dither=0)
    glow(L, cx, 162, 70, amt=0.42)


def catwalk(L, x0, x1, y, posts, seed=63):
    """An iron catwalk over the drums: grating on top (a platform), lattice under it, a rail at the back."""
    K = Tone(L.w, L.h)
    for x in range(x0, x1 + 1):
        K.px(x, y, 0.84)
        K.px(x, y + 1, 0.56 if x % 3 else 0.70)
        K.px(x, y + 2, 0.40)
        K.px(x, y + 6, 0.48)
        d = (x - x0) % 8
        K.px(x, y + 2 + (d if d < 4 else 8 - d), 0.36)
        K.px(x, y - 14, 0.66)
        K.px(x, y - 7, 0.50)
        if (x - x0) % 14 == 0:
            K.rect(x, y - 14, x, y - 1, 0.54)
    for px_ in posts:
        for yy in range(y + 7, WALLB + 8):
            K.px(px_, yy, 0.62)
            K.px(px_ + 1, yy, 0.42)
            K.px(px_ + 2, yy, 0.24)
        K.rect(px_ - 3, WALLB + 7, px_ + 5, WALLB + 8, 0.40)
    put_tone(L, K, IRON, dither=0.3)
    # lanterns hung from the rail
    for lx in range(x0 + 60, x1 - 20, 150):
        K2 = Tone(L.w, L.h)
        K2.rect(lx, y - 13, lx, y - 8, 0.4)
        K2.rect(lx - 2, y - 8, lx + 2, y - 7, 0.5)
        put_tone(L, K2, IRON, dither=0)
        lantern_glass(L, lx - 1, y - 6)
        glow(L, lx, y - 2, 34, amt=0.30, col=(255, 210, 120))


def cart(L, x0, x1, top, seed=1):
    """A wooden hand cart for beans: a box on two wheels, its top a place to stand."""
    T = Tone(L.w, L.h)
    crate_tone(T, x0, top, x1 - x0, 20, seed=seed)
    for wx in (x0 + 7, x1 - 8):
        for a in range(0, 360, 10):
            T.px(wx + 6 * np.cos(np.radians(a)), 177 + 6 * np.sin(np.radians(a)), 0.30)
        for a in range(0, 360, 45):
            T.line([(wx, 177), (wx + 6 * np.cos(np.radians(a)), 177 + 6 * np.sin(np.radians(a)))], 0.46)
    for k in range(14):
        T.px(x1 + k, top + 14 + k // 3, 0.52)
    put_tone(L, T, TEAK, dither=0.35)
    soft_shadow(L, x0 + 2, x1 + 6, 183, 3)
    # a heap of roast beans in it
    Bn = Tone(L.w, L.h)
    for x in range(x0 + 2, x1 - 2):
        u = (x - (x0 + x1) / 2.0) / ((x1 - x0) / 2.0)
        hh = int(3 * np.sqrt(max(0, 1 - u * u)))
        for y in range(top - hh, top):
            Bn.px(x, y, 0.4 + 0.3 * ((x * 5 + y * 3) % 4 == 0))
    put_tone(L, Bn, BEAN, dither=0)


def roasting_house(L):
    x0, x1 = RH + 12, PT - 20
    ceiling(L, x0, x1, seed=65, soot=0.16)
    brick_wall(L, x0, x1, seed=61)
    earth_floor(L, RH, PT + 12, WALLB, seed=67, soot=0.12)
    # sacks of green beans by the furnaces, sacks of roast ones going out
    for (a, b, top, sd, gr) in ((2490, 2560, 118, 71, True), (2620, 2676, 136, 72, True), (3280, 3360, 124, 73, False),
                                (3470, 3540, 110, 74, False)):
        sack_pile(L, [(a, b, top), (a + 8, b - 8, top - 8)], WALLB + 2, seed=sd, green=gr)
    for cx in (2580, 2900, 3110, 3420):
        roaster_drum(L, cx)
    back_door(L, 3300 - 13, open_left=False)                            # the stokers' door (they come out of it)
    catwalk(L, 2678, 3252, 118, posts=[2690, 2860, 3032, 3242])
    plat('catwalk', [[2678, 118], [3252, 118]])
    # crates up to the catwalk at its near end
    CT = Tone(L.w, L.h)
    crate_tone(CT, 2618, 166, 31, 18, seed=81)
    crate_tone(CT, 2650, 166, 29, 18, seed=82)
    crate_tone(CT, 2642, 146, 37, 20, seed=83)
    put_tone(L, CT, TEAK, dither=0.35)
    soft_shadow(L, 2679, 2690, 183, 3)
    plat('cr1', [[2618, 166], [2648, 166]])
    plat('cr2', [[2642, 146], [2678, 146]])
    cart(L, 2836, 2880, 152, seed=84)
    cart(L, 3196, 3236, 152, seed=85)
    plat('cart1', [[2836, 152], [2880, 152]])
    plat('cart2', [[3196, 152], [3236, 152]])
    beans(L, x0, x1, WALLB + 4, 214, 220, seed=9)
    wall_slice(L, PT - 20, PT + 12, door=(112, 176), seed=43)


# ------------------------------------------------------------------ the point and the old lighthouse
def yard(L, x0, x1, ytop=150, seed=91):
    """The point: packed sand with stones in it, the tracks of something very heavy coming down from the shed."""
    w = x1 - x0
    h = SH - ytop
    yy, xx = np.mgrid[0:h, 0:w]
    sy = yy + ytop
    X = xx + x0
    depth = np.clip((sy - ytop) / float(SH - ytop), 0, 1)
    H = fbm((h, w), seed, 50, 6, octaves=3)
    lit = light(ndi.gaussian_filter(H, 1.0), -0.6, -0.8, 6.0)
    grit = fbm((h, w), seed + 1, 1.3, 0.7, octaves=2) - 0.5
    tone = 0.60 - 0.18 * depth + 0.18 * np.clip(lit, -1, 1) + 0.08 * grit
    far = np.clip(1 - (sy - ytop) / 10.0, 0, 1)
    tone = tone * (1 - 0.4 * far) + 0.74 * 0.4 * far
    # the tracks: two broad bands of tread marks along the walk line, from the shed to the middle of the yard
    fade = np.clip((X - 3760) / 400.0, 0, 1)
    for ty, wd in ((179, 3), (190, 4)):
        band = (np.abs(sy - ty) <= wd) & (X > 3760)
        tread = ((X // 3) % 3 == 0)
        tone = np.where(band, tone - (0.05 + 0.06 * tread) * fade, tone)
    G = Layer(w, h)
    G.put(toned(np.clip(tone, 0.05, 1), ST.SAND, dither=0.5, x0=x0), np.ones((h, w), bool))
    L.paste(G, x0, ytop)
    r = rng(seed + 3)
    for k in range(int(w / 14)):
        x = int(r.uniform(x0, x1 - 2))
        y = int(r.uniform(ytop + 8, SH - 2))
        for (dx, dy, c) in ((0, 0, (120, 108, 96)), (1, 0, (156, 142, 124)), (0, 1, (70, 60, 54)), (1, 1, (96, 84, 74))):
            L.rgb[y + dy, x + dx] = c


def sea_wall(L, x0, x1, top=138, seed=93):
    """A low wall of coral stone along the back of the yard, the harbour over it."""
    T = Tone(L.w, L.h)
    r = rng(seed)
    for y in range(top, 152):
        course = (y - top) // 5
        for x in range(x0, x1):
            joint = ((y - top) % 5 == 0) or ((x + 9 * course) % 18 == 0)
            t = 0.62 - 0.06 * course - 0.24 * joint + (0.22 if y == top else 0) + 0.03 * (((x * 7 + y * 3) % 5) == 0)
            T.px(x, y, t)
    put_tone(L, T, CORAL, dither=0.4)


def lighthouse(L, cx=4204, base=168, top=26, seed=95):
    """The old lighthouse on the point: a tapering whitewashed tower, a dark band, small windows up it, an arched
    door, the gallery and the lantern room at the top with its lamp lit, a dome and a vane."""
    T = Tone(L.w, L.h)
    for y in range(top + 14, base):
        u = (y - top - 14) / float(base - top - 14)
        half = 11 + 9 * u
        for x in range(int(cx - half), int(cx + half) + 1):
            s_ = min(1.0, max(0.0, (x - (cx - half)) / (2 * half)))
            t = 0.90 - 0.42 * s_ ** 1.4 + 0.03 * (((x * 5 + y * 3) % 7) == 0)
            if 60 <= y <= 70:
                t -= 0.46                                             # the band
            if y > base - 5:
                t -= 0.14
            T.px(x, y, t)
    # windows up the tower, and the door
    for wy in (52, 88, 118):
        T.rect(cx - 1, wy, cx + 2, wy + 6, 0.16)
        T.rect(cx - 1, wy, cx + 2, wy, 0.06)
    for y in range(base - 22, base):
        for x in range(cx - 5, cx + 6):
            arch = y < base - 17 and (x - cx) ** 2 + (y - (base - 17)) ** 2 > 25
            if not arch:
                T.px(x, y, 0.10)
    put_tone(L, T, LIME, dither=0.4, grain=0.03, seed=seed)
    Dr = Tone(L.w, L.h)
    for y in range(base - 20, base):
        for x in range(cx - 4, cx + 5):
            if not (y < base - 16 and (x - cx) ** 2 + (y - (base - 17)) ** 2 > 16):
                Dr.px(x, y, 0.56 - 0.06 * (x - cx + 4) / 2 + 0.1 * (x == cx))
    put_tone(L, Dr, CLOTH_B, dither=0.3)
    # the gallery, the lantern room, the dome
    K = Tone(L.w, L.h)
    K.rect(cx - 15, top + 12, cx + 15, top + 14, 0.44)
    K.rect(cx - 15, top + 12, cx + 15, top + 12, 0.70)
    for x in range(cx - 15, cx + 16, 3):
        K.rect(x, top + 6, x, top + 11, 0.50)
    K.rect(cx - 15, top + 6, cx + 15, top + 6, 0.62)
    for x in (cx - 9, cx - 3, cx + 3, cx + 9):
        K.rect(x, top - 4, x, top + 11, 0.34)
    for j in range(8):
        half = 9 - j
        K.rect(cx - half, top - 5 - j, cx + half, top - 5 - j, 0.56 - 0.03 * j + (0.2 if j == 7 else 0))
    K.rect(cx, top - 18, cx, top - 13, 0.50)
    K.rect(cx - 3, top - 17, cx + 2, top - 17, 0.50)
    put_tone(L, K, IRON, dither=0.3)
    G = Tone(L.w, L.h)
    for y in range(top - 4, top + 6):
        for x in range(cx - 9, cx + 10):
            if x in (cx - 9, cx - 3, cx + 3, cx + 9):
                continue
            G.px(x, y, 0.62 + 0.30 * (x < cx - 3) + 0.08 * ((x + y) % 2))
    put_tone(L, G, GLASS, dither=0.3)
    for y in range(top - 2, top + 5):
        for x in range(cx - 2, cx + 3):
            L.rgb[y, x] = (255, 236, 160) if (x + y) % 2 else (255, 214, 120)
    INFO['lighthouse'] = [cx, top]


def keepers_house(L, x0=4228, x1=4320, base=170, seed=97):
    """The keeper's house at the foot of the tower: flat roofed, whitewashed, a blue door and shutters."""
    T = Tone(L.w, L.h)
    top = base - 38
    for y in range(top, base):
        for x in range(x0, x1):
            u = (x - x0) / float(x1 - x0)
            t = 0.84 - 0.12 * u - 0.10 * (y > base - 6) + 0.03 * (((x * 5 + y * 3) % 9) == 0)
            if y < top + 3:
                t = 0.94 if y == top else 0.72
            T.px(x, y, t)
    for i in range(x0 - 2, x1 + 2):                                   # the parapet
        if (i - x0) % 6 < 3:
            T.rect(i, top - 3, i, top - 1, 0.90)
    put_tone(L, T, LIME, dither=0.4)
    B = Tone(L.w, L.h)
    B.rect(x0 + 18, base - 26, x0 + 30, base - 1, 0.52)
    B.rect(x0 + 18, base - 26, x0 + 30, base - 26, 0.80)
    for wx in (x0 + 46, x0 + 70):
        B.rect(wx, base - 28, wx + 9, base - 17, 0.40)
        B.rect(wx - 4, base - 28, wx - 2, base - 17, 0.62)
        B.rect(wx + 11, base - 28, wx + 13, base - 17, 0.58)
    put_tone(L, B, CLOTH_B, dither=0.3)


def shed(L, x0=4330, x1=4480, base=172, seed=99):
    """The Scorpion's shed at the end of the point, corrugated iron, its doors open on the dark: something has come
    out of it."""
    T = Tone(L.w, L.h)
    top = base - 62
    for y in range(top, base):
        for x in range(x0, x1):
            corr = (x % 4 < 2)
            t = 0.56 + 0.12 * corr - 0.20 * (x - x0) / float(x1 - x0) - 0.06 * ((y - top) / 62.0)
            if y < top + 3:
                t = 0.76
            T.px(x, y, t)
    for x in range(x0 - 4, x1):                                       # the roof's edge, rusted
        T.px(x, top - 1, 0.80)
        T.px(x, top - 2, 0.56)
    put_tone(L, T, IRON, dither=0.3, grain=0.04, seed=seed)
    R = Tone(L.w, L.h)
    for y in range(top, base):
        for x in range(x0, x1):
            if ((x * 13 + y * 7) % 23 == 0) or (y > top + 20 and (x * 7 + y) % 31 == 0):
                R.px(x, y, 0.40)
    put_tone(L, R, P.RUST, dither=0)
    D = Tone(L.w, L.h)
    D.rect(x0 + 20, top + 10, x0 + 120, base - 1, 0.10)
    for y in range(top + 10, base):
        D.px(x0 + 20, y, 0.30)
    put_tone(L, D, SOOT, dither=0.3)
    # the door leaves, swung open
    F = Tone(L.w, L.h)
    for y in range(top + 12, base):
        for i in range(10):
            F.px(x0 + 10 + i, y + i // 3, 0.50 + 0.12 * (i % 4 < 2))
    put_tone(L, F, IRON, dither=0.2)


def point(L):
    sea_wall(L, PT - 20, WORLD)
    yard(L, PT - 20, WORLD)
    # rocks along the back, a boat turned over, nets, a palm or two
    items = []
    for i, (x, by, w_, h_) in enumerate([(3660, 150, 40, 20), (3940, 148, 30, 14), (4110, 150, 44, 22), (4440, 150, 36, 18)]):
        rk, f = P.rock(w_, h_, seed=200 + i)
        L.paste(rk, x, by - f)
    sk, f = P.skiff(length=70, paint=P.BOATBLUE, stripe=P.BOATWHITE, seed=31, motor=False)
    L.paste(P.sink(sk, 3, seed=2), 3690, 166 - f)
    for x, (h_, lean, sd) in ((3640, (80, 8, 41)), (4500, (70, -9, 43)), (3880, (64, 6, 45))):
        pm, f, bx = P.palm(height=h_, lean=lean, seed=sd)
        L.paste(pm, x - bx, 158 - f)
    lighthouse(L)
    keepers_house(L)
    shed(L)
    NT = Tone(L.w, L.h)
    for i in range(46):
        for j in range(8):
            if (i + j) % 3 == 0:
                NT.px(3790 + i, 160 + j - int(3 * np.sin(i / 45.0 * np.pi)), 0.3 + 0.4 * ((i + 2 * j) % 4 == 0))
    put_tone(L, NT, P.NET, dither=0)


# ------------------------------------------------------------------ what passes close to the lens
# The foreground slides at 1.25 times the camera. Something meant to pass by world x when the camera is about there is
# at 1.25 x - 58 along the foreground (FX converts).
def FX(xw):
    return int(round(1.25 * xw - 58))


FQ1, FI0, FI1, FP1 = FX(1206), FX(1206), FX(PT + 6), FX(WORLD) + 520     # quay | inside | point
FTILE = 640


def fore_quay(w=FQ1):
    """On the quay: a bollard and a hawser close to the lens, the corner of a crate, a coil of rope."""
    L = Layer(w, SH)
    T = Tone(w, SH)
    for bx in (300, 1040):
        for j in range(26):
            half = 9 if j < 6 else (7 if j < 18 else 11)
            for i in range(-half, half + 1):
                T.px(bx + i, 190 + j, 0.20 + 0.36 * np.exp(-((i + 3) / 4.0) ** 2) - 0.004 * j)
    put_tone(L, T, IRON, dither=0.3)
    R = Tone(w, SH)
    for x in range(306, 640):
        u = (x - 306) / 334.0
        y = 199 + 10 * np.sin(np.pi * u)
        for k in range(4):
            R.px(x, y + k, 0.62 - 0.12 * k + 0.12 * ((x + k * 2) % 6 < 2))
    for a in range(0, 720, 8):
        rr = 4 + a / 120.0
        R.px(1250 + rr * np.cos(np.radians(a)) * 1.6, 208 + rr * np.sin(np.radians(a)) * 0.6, 0.5 + 0.2 * (a % 24 == 0))
    put_tone(L, R, SACK, dither=0.2)
    C = Tone(w, SH)
    crate_tone(C, 880, 194, 44, 30, seed=91)
    C.t = C.t * 0.55
    put_tone(L, C, TEAK, dither=0.3)
    return L


def fore_inside(w=FTILE):
    """Inside: the front wall's lintel and one of its piers, a lantern on a chain, a sack near the lens. One length of
    it, repeated all the way through the warehouses and the roasting house."""
    L = Layer(w, SH)
    T = Tone(w, SH)
    for x in range(w):
        for y in range(0, 9):
            T.px(x, y, 0.30 - 0.03 * y + 0.06 * (y == 0) + 0.04 * ((x // 23) % 2))
        T.px(x, 9, 0.08)
    px_ = 330
    for y in range(9, SH):
        for i in range(14):
            T.px(px_ + i, y, 0.30 - 0.016 * i + 0.10 * (i == 0) + 0.03 * (((y // 9) % 2) and i in (5, 6)))
    for j in range(10):
        T.rect(px_ - 6 + j // 2, 9 + j, px_ + 19 - j // 2, 9 + j, 0.24 + 0.04 * (j == 0))
    for j in range(6):
        T.rect(px_ - 3, SH - 6 + j, px_ + 16, SH - 6 + j, 0.20)
    put_tone(L, T, TEAK, dither=0.3)
    K = Tone(w, SH)
    for y in range(10, 36):
        K.px(120 + (y % 2), y, 0.40)
    K.rect(115, 36, 126, 38, 0.36)
    K.rect(116, 48, 125, 49, 0.30)
    K.rect(115, 36, 115, 48, 0.26)
    K.rect(126, 36, 126, 48, 0.20)
    put_tone(L, K, IRON, dither=0)
    for y in range(39, 48):
        for x in range(117, 125):
            L.rgb[y, x] = (255, 226, 140) if (x + y) % 3 else (250, 190, 90)
            L.a[y, x] = True
    S_ = Tone(w, SH)
    sack_tone(S_, 500, 198, 40, 18, seed=5, lit=-0.25)
    put_tone(L, S_, SACK, dither=0.3)
    return L


def fore_point(w=FP1 - FI1):
    """On the point: dark rocks close to the lens and the foot of a palm."""
    L = Layer(w, SH)
    for i, (x, w_, h_) in enumerate([(60, 64, 30), (520, 40, 18), (880, 70, 32)]):
        rk, f = P.rock(w_, h_, seed=300 + i, sharp=0.9)
        P.shade(rk, rk.a, P.ROCK, -2)
        L.paste(rk, x, SH - h_ + 6)
    T = Tone(w, SH)
    for y in range(120, SH):
        cx_ = 170 + (SH - y) * 0.12
        for i in range(-5, 6):
            ring = (y % 5) < 2
            T.px(cx_ + i, y, (0.36 if ring else 0.26) + 0.18 * np.exp(-((i + 2) / 2.5) ** 2))
    put_tone(L, T, P.DRIFT, dither=0.3)
    return L


# ------------------------------------------------------------------ the whole stage
_CACHE = {}


def build():
    if not _CACHE:
        PLATS.clear()
        INFO.clear()
        play = Layer(WORLD, SH)
        quay(play)
        warehouses(play)
        roasting_house(play)
        point(play)
        fq, fi, fp = fore_quay(), fore_inside(), fore_point()
        fore = Layer(FP1, SH)
        fore.paste(fq, 0, 0)
        x = FI0
        while x < FI1:
            part = fi if x + FTILE <= FI1 else fi.crop(0, 0, FI1 - x, SH)
            fore.paste(part, x, 0)
            x += FTILE
        fore.paste(fp, FI1, 0)
        _CACHE.update(play=play, sky=sky_m(), far=far_m(), sea=sea_m(), fore=fore, fore_quay=fq, fore_inside=fi, fore_point=fp)
    return _CACHE


if __name__ == '__main__':
    import sys
    S = build()
    cams = [0, 560 - 234, 850 - 234, 1100, 1700 - 234, 2200 - 234, 2500, 2860 - 234, 3330 - 234, 3584 - 100, 4010 - 234, 4012]
    print(preview(S, cams, sys.argv[1] if len(sys.argv) > 1 else 'mocha.png', lines='lines' in sys.argv))
    print('plats', PLATS)
    print('info', INFO)
