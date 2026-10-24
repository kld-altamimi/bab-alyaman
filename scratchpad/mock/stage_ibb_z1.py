# stage_ibb_z1.py - Ibb's zone 1, Wadi al-Sahul: the valley road up from Taiz, the morning after rain (stage 3 of Ibb's
# plan, 24 Oct). The play strip, painted from the back of the field behind the road to the road's near edge, and what
# passes close to the lens. Back to front: the crops and trees in the fields, the dry-stone wall along them, the gravel
# verge, the buildings standing on it (the Zanabeel's checkpoint, a stone farmhouse, a roadside shop), the poles with
# their wires and loudspeakers (painted: scenery only), the wet road with its puddles, and what stands on the road (the
# checkpoint's sandbags and drums, a minibus that has given up). Where anyone can stand is recorded as it is painted
# (I.PLATS), with what else the level needs (I.INFO: doors, where the screens stand).
import numpy as np
from scipy import ndimage as ndi
from paint import *
import stage_mocha as SM
import stage_taiz as STZ
import stage_zabid as SZ
import stage_ibb as I
import json
from PIL import Image

GAME = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/'
_SHEET = {}

SH, WALK = I.SH, I.WALK
ROAD_TOP = 172              # the asphalt from here down
VERGE = 160                 # the gravel verge behind the road, from here to the asphalt
W1 = 1280                   # zone 1's length
put_tone = SM.put_tone
plat = I.plat

# ------------------------------------------------------------------ colour ramps (dark to pale)
IBBSTONE = ramp(['#1a1816', '#2e2a28', '#44403c', '#5a5550', '#726c66', '#8a837c', '#a39b92', '#bbb3a8', '#d2cbc0', '#e6e0d6'], 20)   # Ibb's grey building stone
CONCRETE = ramp(['#262624', '#3e3d3a', '#5a5853', '#77746d', '#94918a', '#b0aca4', '#cac6bc', '#e0dcd2'], 16)
EUCA = ramp(['#121c16', '#1e2c24', '#2c3c32', '#3c4e42', '#4e6252', '#627664', '#7a8c78', '#94a490', '#b0bcaa'], 18)          # eucalyptus leaves
BARK = ramp(['#2a221c', '#463c34', '#665a4e', '#867a6c', '#a69a8a', '#c4baa8', '#ddd4c4'], 14)                                  # its pale bark
SHUTG = ramp(['#0a1a12', '#12281c', '#1c3a2a', '#284e38', '#36644a', '#487c5e', '#5e9474', '#7aae8e'], 16)                      # green shutters
SIGNY = ramp(['#3a2a04', '#6c4e0a', '#a07612', '#cc9e20', '#eac440', '#f8e27a', '#fff4c0'], 14)
PLASTIC = ramp(['#20242c', '#3a4250', '#5a6474', '#808a98', '#a8b0bc', '#ccd2da', '#eef0f4'], 12)
TYRE = ramp(['#060606', '#101010', '#1a1a1a', '#262626', '#343434', '#464644'], 8)
GRASS = ramp(['#141e08', '#24320e', '#364814', '#4a5e1c', '#607626', '#7a8e32', '#96a644', '#b2bc5e', '#ccd27e'], 18)           # verge grass, yellower
ROADW = ramp(['#121416', '#1e2226', '#2a3034', '#383e44', '#464e54', '#565e64', '#687076', '#7c848a', '#929aa0', '#aab2b6'], 18)   # wet asphalt under a pale sky
TOMATO = ramp(['#2a0604', '#540c06', '#82180a', '#ac2a10', '#d0461c', '#ea6e34'], 10)
BLUEP = ramp(['#0a1424', '#122440', '#1c3860', '#2a5080', '#3e6ca0', '#5a8cbc', '#80aed4'], 12)                                  # blue paint
DRYST, LEAF, TERR, ROAD, GRAVEL, MUDI, TIN, RUSTI, BUSW, BUSB, REDP, GOLD, WATER, SKYI = (I.DRYST, I.LEAF, I.TERR, I.ROAD, I.GRAVEL,
    I.MUDI, I.TIN, I.RUSTI, I.BUSW, I.BUSB, I.REDP, I.GOLD, I.WATER, I.SKYI)
LIME, TEAK, SOOT, GREENSACK = SM.LIME, SM.TEAK, SM.SOOT, SM.GREENSACK


def piece_put(L, t, m, rmp, x0, y0, dither=0.45):
    """Map a tone patch (t, its mask m) through a ramp and lay it on L at (x0, y0), the checker kept in step with L's."""
    h, w = t.shape
    P = Layer(w, h)
    P.put(toned(np.clip(t, 0, 1), rmp, dither=dither, x0=x0, y0=y0), m)
    L.paste(P, x0, y0)


# ------------------------------------------------------------------ fields, walls, trees
def crops(L, x0, x1, base, seed=1, hmin=16, hmax=28, gap=2.2, heads=0.55):
    """Sorghum standing in a field: a dark mass of leaves low down, stalks rising out of it, long blades arching off them
    left and right, the heads at the top; lit from the left."""
    r = rng(seed)
    T = Tone(L.w, L.h)
    # the mass of leaves at the foot, uneven along its top
    top = base - 8 - 3 * noise((1, x1 - x0 + 1), seed, 6, 0.5)[0]
    for i, x in enumerate(range(x0, x1)):
        for y in range(int(top[i]), base):
            T.px(x, y, 0.22 + 0.10 * ((x * 3 + y) % 4 == 0) - 0.08 * (y > base - 3))
    x = x0 + r.uniform(0, gap)
    H = []
    while x < x1:
        hgt = r.uniform(hmin, hmax)
        lean = r.uniform(-0.10, 0.10)
        tp = int(base - hgt)
        for y in range(tp, base - 2):
            T.px(int(round(x + lean * (base - y))), y, 0.40 + 0.20 * (1 - (y - tp) / hgt))
        nl = int(r.integers(3, 6))
        for k in range(nl):
            ly = tp + (k + 1) * hgt / (nl + 1.3)
            side = -1 if (k + int(x)) % 2 == 0 else 1
            ln = int(r.integers(4, 8))
            for i in range(1, ln):
                px_ = int(round(x + lean * (base - ly) + side * i))
                py_ = int(round(ly - 1.1 * i + 0.20 * i * i))
                T.px(px_, py_, 0.64 + 0.10 * (side < 0) - 0.025 * i)
        if r.random() < heads:
            H.append((int(round(x + lean * hgt)), tp))
        x += r.uniform(gap * 0.6, gap * 1.4)
    put_tone(L, T, TERR, dither=0.4)
    Hd = Tone(L.w, L.h)
    for hx, ty in H:
        for j in range(4):
            Hd.px(hx, ty - j, 0.70 - 0.08 * j)
            if j in (1, 2):
                Hd.px(hx - 1, ty - j, 0.56)
    put_tone(L, Hd, GRASS, dither=0.3)


def drystone(L, x0, x1, top, base, seed=1, grass=True):
    """A field wall of stones laid dry: rows of rough stones, each lit along its top and left and dark in the gaps, the
    top course uneven, grass growing out of it. -> the wall's top, column by column (for a platform or a poster)."""
    r = rng(seed)
    T = Tone(L.w, L.h)
    tops = np.full(x1 - x0, base, dtype=int)
    y = base
    while y > top:
        rh = int(r.integers(3, 6))
        y0 = max(top, y - rh)
        x = x0 - int(r.integers(0, 6))
        last = y0 <= top
        while x < x1:
            sw = int(r.integers(4, 11))
            sx0, sx1 = max(x0, x), min(x1, x + sw)
            sy0 = y0 + (int(r.integers(-2, 2)) if last else 0)
            t0 = r.uniform(0.40, 0.68)
            for yy in range(sy0, y):
                for xx in range(sx0, sx1 - 1):
                    corner = (xx == sx0 or xx == sx1 - 2) and (yy == sy0 or yy == y - 1)
                    if corner and r.random() < 0.7:
                        T.px(xx, yy, 0.12)
                        continue
                    t = t0 + (0.14 if yy == sy0 else (0.07 if xx == sx0 else 0)) - (0.12 if yy == y - 1 else 0) - (0.07 if xx == sx1 - 2 else 0)
                    T.px(xx, yy, t + 0.04 * (r.random() - 0.5))
                T.px(sx1 - 1, yy, 0.12)
            if last:
                tops[max(0, sx0 - x0):max(0, sx1 - x0)] = np.minimum(tops[max(0, sx0 - x0):max(0, sx1 - x0)], sy0)
            x += sw
        y = y0
    put_tone(L, T, DRYST, dither=0.35)
    if grass:
        G = Tone(L.w, L.h)
        for i in range(0, x1 - x0):
            if hash_(i + x0, seed) < 0.35:
                ty = tops[i]
                n = int(1 + 4 * hash_(i + x0, seed + 1))
                for j in range(n):
                    G.px(x0 + i, ty - 1 - j, 0.50 + 0.25 * (j == n - 1) - 0.05 * j)
        put_tone(L, G, GRASS, dither=0.3)
    return tops


def hash_(a, b):
    return float(I.hash01(int(a), int(b)))


def crown(L, cx, cy, rx, ry, seed, rmp=None, blobs=36, rmin=5.0, rmax=11.0, dark=0.0, lean=0.0, hang=0):
    """A tree's crown: clumps of leaves heaped in an oval, each clump lit on its upper left, shade deep between them.
    hang > 0: the leaves hang in strands (a eucalyptus), ragged below by that many pixels."""
    rmp = rmp if rmp is not None else LEAF
    r = rng(seed)
    pad = int(rmax + 3)
    x0, y0 = int(cx - rx - pad), int(cy - ry - pad)
    w, h = int(2 * (rx + pad)), int(2 * (ry + pad))
    yy, xx = np.mgrid[0:h, 0:w]
    Hh = np.zeros((h, w))
    for i in range(blobs):
        a = r.uniform(0, 2 * np.pi)
        d = np.sqrt(r.uniform(0, 1))
        bx = (cx - x0) + np.cos(a) * d * rx + lean * (np.sin(a) * d * ry)
        by = (cy - y0) + np.sin(a) * d * ry
        br = r.uniform(rmin, rmax) * (1 - 0.3 * d)
        z = np.sqrt(np.clip(br * br - (xx - bx) ** 2 - ((yy - by) * 1.1) ** 2, 0, None))
        Hh = np.maximum(Hh, np.where(z > 0, z + (1 - d) * 5, 0))
    m = Hh > 0.6
    lit = light(ndi.gaussian_filter(Hh, 0.7), -0.6, -0.8, 0.30)
    leaf = noise((h, w), seed + 1, 0.7, 0.7) if not hang else noise((h, w), seed + 1, 0.45, 2.2)
    t = 0.46 + 0.32 * np.clip(lit, -1, 1) + 0.16 * (leaf - 0.5) - dark - 0.10 * (yy > (cy - y0) + ry * 0.5)
    if hang:
        strands = noise((h, w), seed + 2, 0.4, 1.5) > 0.55
        below = np.zeros_like(m)
        for k in range(1, hang + 1):
            sh_ = np.roll(m, k, axis=0)
            sh_[:k] = False
            below |= sh_ & strands & (noise((h, w), seed + 3 + k, 0.5, 0.5) > 0.25 + 0.6 * k / hang)
        t = np.where(below & ~m, 0.30, t)
        m = m | below
        m &= ~((noise((h, w), seed + 9, 0.8, 0.8) > 0.80) & (Hh < 3))
    piece_put(L, t, m, rmp, x0, y0, dither=0.5)
    return m, x0, y0


def trunk(L, x, base, top, w=4, seed=1, rmp=None, lean=0.0, forks=2):
    """A trunk rising from the ground and dividing into a few limbs under the crown."""
    rmp = rmp if rmp is not None else SM.TEAK
    r = rng(seed)
    T = Tone(L.w, L.h)
    for y in range(top, base):
        u = (base - y) / float(base - top)
        cx = x + lean * (base - y)
        ww = max(1.5, w * (1 - 0.35 * u))
        for i in range(int(np.floor(-ww / 2)), int(np.ceil(ww / 2))):
            T.px(int(round(cx + i)), y, 0.50 - 0.20 * (i >= 0) + 0.12 * (i == int(np.floor(-ww / 2))) + 0.05 * ((y * 3 + i) % 5 == 0))
    for k in range(forks):
        side = -1 if k % 2 == 0 else 1
        x0, y0 = x + lean * (base - top), top
        ln = int(r.integers(8, 16))
        for i in range(ln):
            T.px(int(round(x0 + side * i * 0.9)), int(round(y0 - i * 0.8)), 0.36)
            T.px(int(round(x0 + side * i * 0.9)) + 1, int(round(y0 - i * 0.8)), 0.26)
    put_tone(L, T, rmp, dither=0.3)


def sidr(L, cx, base, seed=1):
    """A sidr tree: a short thick trunk forking low into boughs that spread up and out, and over them a wide, dense,
    round-topped crown, dark green, its underside in shade."""
    trunk(L, cx, base, base - 18, w=6, seed=seed, forks=0)
    for dx, dy, w in ((-24, 20, 3), (-9, 28, 3), (9, 27, 3), (25, 19, 3)):
        limb(L, cx, base - 18, cx + dx, base - 18 - dy, w=w, rmp=TEAK)
    crown(L, cx + 2, base - 54, 46, 19, seed, LEAF, blobs=84, rmin=5, rmax=10, dark=0.04)


def limb(L, x0, y0, x1, y1, w=2, rmp=None):
    """A bough from (x0, y0) to (x1, y1), lit on its upper side."""
    rmp = rmp if rmp is not None else BARK
    T = Tone(L.w, L.h)
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for i in range(n):
        u = i / float(max(1, n - 1))
        x, y = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
        ww = max(1, int(round(w * (1 - 0.5 * u))))
        for k in range(ww):
            T.px(int(round(x)) + k, int(round(y)), 0.62 - 0.22 * k)
    put_tone(L, T, rmp, dither=0)


def eucalyptus(L, x, base, hgt=128, seed=1):
    """A eucalyptus by the road: a tall pale trunk, a few boughs going up and out near the top, and on each an open mass
    of grey-green leaves hanging in strands, the sky showing through."""
    r = rng(seed)
    lean = r.uniform(-0.05, 0.05)
    trunk(L, x, base, base - int(hgt * 0.88), w=4, seed=seed, rmp=BARK, lean=lean, forks=0)
    tips = []
    for k, side in enumerate((-1, 1, -1 if r.random() < 0.5 else 1)):
        u0 = r.uniform(0.52, 0.78)
        sx, sy = x + lean * hgt * u0, base - hgt * u0
        ex, ey = sx + side * r.uniform(9, 17), sy - r.uniform(14, 26)
        limb(L, sx, sy, ex, ey, w=2)
        tips.append((ex, ey))
    tips.append((x + lean * hgt * 0.92, base - hgt * 0.94))
    for k, (ex, ey) in enumerate(tips):
        crown(L, ex, ey, r.uniform(9, 14), r.uniform(6, 9), seed * 11 + k, EUCA, blobs=34, rmin=2.0, rmax=4.2, hang=7)


# ------------------------------------------------------------------ the ground: the verge and the road
def verge(L, x0, x1, seed=3):
    """The gravel verge between the wall and the road: grey stones in mud, puddles, tufts of grass."""
    w, h = x1 - x0, ROAD_TOP - VERGE + 2
    yy, xx = np.mgrid[0:h, 0:w]
    g = noise((h, w), seed, 0.6, 0.6)
    mud = fbm((h, w), seed + 1, 14, 3, octaves=3)
    t = 0.46 + 0.22 * (g - 0.5) + 0.10 * (yy / h) - 0.10 * (yy < 2)
    stones = g > 0.72
    t = np.where(stones, t + 0.18, t)
    piece_put(L, t, mud < 0.62, GRAVEL, x0, VERGE, dither=0.4)
    tm = 0.44 + 0.20 * (g - 0.5)
    piece_put(L, tm, mud >= 0.62, MUDI, x0, VERGE, dither=0.4)
    G = Tone(L.w, L.h)
    r = rng(seed + 2)
    for i in range(int(w / 5)):
        gx = x0 + int(r.integers(0, w))
        gy = VERGE + int(r.integers(2, h - 1))
        for j in range(int(r.integers(2, 6))):
            G.px(gx + (j % 2) * (1 if r.random() < 0.5 else -1), gy - j, 0.42 + 0.10 * j)
    put_tone(L, G, GRASS, dither=0.3)


def road(L, x0, x1, seed=5):
    """The wet road: dark asphalt shining where it takes the sky, patched, cracked, a broken edge at the back, the centre
    dashes worn half away."""
    w, h = x1 - x0, SH - ROAD_TOP
    yy, xx = np.mgrid[0:h, 0:w]
    v = yy / float(h)
    sheen = noise((h, w), seed, 46, 0.7)
    grain = noise((h, w), seed + 1, 0.6, 0.6)
    t = 0.52 - 0.10 * v + 0.22 * np.clip(sheen - 0.45, 0, 1) + 0.07 * (grain - 0.5)
    # patches of newer and older asphalt
    r = rng(seed + 2)
    for i in range(int(w / 90)):
        px0 = int(r.integers(0, w)); pw = int(r.integers(14, 50)); py0 = int(r.integers(2, h - 6)); ph = int(r.integers(4, 12))
        d = r.choice([-0.07, 0.06])
        m = (xx >= px0) & (xx < px0 + pw) & (yy >= py0) & (yy < py0 + ph)
        t = np.where(m, t + d, t)
        edge = m & ((xx == px0) | (yy == py0) | (xx == px0 + pw - 1) | (yy == py0 + ph - 1))
        t = np.where(edge, t - 0.06, t)
    # cracks
    for i in range(int(w / 70)):
        cx, cy = r.uniform(0, w), r.uniform(4, h - 2)
        for k in range(int(r.integers(6, 20))):
            cx += r.choice([1, 1, 1, 0]); cy += r.choice([-1, 0, 0, 1]) * 0.6
            ix, iy = int(cx), int(np.clip(cy, 0, h - 1))
            if 0 <= ix < w:
                t[iy, ix] -= 0.14
    # the centre line, worn
    cy = WALK + 12 - ROAD_TOP
    dash = ((xx + 6) % 34) < 16
    worn = noise((h, w), seed + 3, 3, 0.6) > 0.35
    t = np.where((yy >= cy) & (yy < cy + 2) & dash & worn, 0.84 - 0.10 * (yy == cy + 1), t)
    # the broken edge at the back
    edge = ROAD_TOP - VERGE
    t = np.where(yy < 2, t - 0.10, t)
    piece_put(L, t, np.ones((h, w), bool), ROADW, x0, ROAD_TOP, dither=0.45)
    G = Tone(L.w, L.h)
    for x in range(x0, x1):
        k = int(2.5 * noise((1, w), seed + 4, 2, 0.5)[0][x - x0])
        for j in range(k):
            G.px(x, ROAD_TOP + j, 0.50 + 0.15 * ((x + j) % 3 == 0))
    put_tone(L, G, GRAVEL, dither=0.3)


def puddle(L, cx, cy, w, h, seed=1):
    """Rain on the road: a flat pool taking the pale sky, darker at its far rim, a bright line at its near one."""
    yy, xx = np.mgrid[0:h, 0:w]
    e = ((xx - w / 2.0) / (w / 2.0)) ** 2 + ((yy - h / 2.0) / (h / 2.0)) ** 2
    rr = noise((h, w), seed, 3, 1)
    m = e + 0.35 * (rr - 0.5) < 1.0
    t = 0.62 + 0.20 * (yy / float(h)) + 0.10 * (noise((h, w), seed + 1, 8, 0.5) - 0.5)
    t = np.where(yy == 0, 0.30, t)
    piece_put(L, t, m, WATER, int(cx - w / 2), int(cy - h / 2), dither=0.4)


# ------------------------------------------------------------------ poles, wires, loudspeakers
def pole(L, x, base, hgt=112, seed=1, horns=0):
    """A concrete pole: a crossarm at the top with its insulators, a cable down it, and (horns > 0) loudspeakers bolted on
    below the arm, trumpets pointing up and down the road. -> where its wires are tied."""
    T = Tone(L.w, L.h)
    top = base - hgt
    for y in range(top, base):
        u = (y - top) / float(hgt)
        T.px(x - 1, y, 0.78 - 0.10 * u)
        T.px(x, y, 0.60 - 0.10 * u)
        T.px(x + 1, y, 0.40 - 0.10 * u)
        if u > 0.5:
            T.px(x + 2, y, 0.32)
    put_tone(L, T, CONCRETE, dither=0.3)
    A = Tone(L.w, L.h)
    for i in range(-11, 13):
        A.px(x + i, top + 4, 0.62)
        A.px(x + i, top + 5, 0.30)
    for i in (-10, -4, 5, 11):
        A.px(x + i, top + 3, 0.95)
        A.px(x + i, top + 2, 0.80)
    for i in (-7, 8):
        for j in range(6):
            A.px(x + int(i * (1 - j / 6.0)), top + 5 + j, 0.30)
    for y in range(top + 6, base - 2):
        if (y // 3) % 2 == 0:
            A.px(x + 2, y, 0.10)
    put_tone(L, A, SOOT, dither=0)
    if horns:
        hy = top + 16
        Hn = Tone(L.w, L.h)
        for k, side in enumerate([-1, 1] if horns >= 2 else [1]):
            for i in range(10):
                spread = 1 + i // 3
                for j in range(-spread, spread + 1):
                    t = 0.82 - 0.05 * i - 0.20 * (j > 0) + 0.10 * (j == -spread)
                    Hn.px(x + side * (3 + i), hy + j - i // 4, t)
            for j in range(-5, 6):
                Hn.px(x + side * 13, hy + j - 2, 0.92 - 0.04 * abs(j))
            Hn.px(x + side * 2, hy, 0.40)
        for j in range(4):
            Hn.px(x + 2, hy + 2 + j, 0.30)
        put_tone(L, Hn, CONCRETE, dither=0.2)
    return [(x - 10, top + 3), (x + 11, top + 3)]


def wires(L, a, b, sag=10, t=0.32):
    """Wires slung from one pole to the next, sagging between."""
    T = Tone(L.w, L.h)
    for (ax, ay), (bx, by) in zip(a, b):
        n = int(abs(bx - ax)) + 1
        for i in range(n):
            u = i / float(n - 1)
            x = ax + (bx - ax) * u
            y = ay + (by - ay) * u + sag * 4 * u * (1 - u)
            T.px(int(round(x)), int(round(y)), t)
    put_tone(L, T, SOOT, dither=0)


# ------------------------------------------------------------------ posters (no words on them: faces and badges only)
def sheet_frame(name):
    """A frame of Ibb's sprite sheet (stage 1's pictures of the Spokesman), as RGBA pixels."""
    if not _SHEET:
        _SHEET['im'] = np.array(Image.open(GAME + 'art/out/ibb.png').convert('RGBA'))
        _SHEET['fr'] = json.load(open(GAME + 'gen/ibb_sprites.json'))['frames']
    x, y, w, h, ax, ay = _SHEET['fr'][name]
    return _SHEET['im'][y:y + h, x:x + w]


def poster(L, x, y, kind='face', seed=1):
    """A poster pasted on a wall. 'face': the Spokesman as the shop sets show him (his beret, his stubble, the flag at his
    side, the podium), on paper; 'badge': the Zanabeel's gold scorpion in its wreath on their red with the yellow band.
    No words on either. Weathered: faded toward the paper, a streak where the rain runs, a corner torn off.
    -> where it is."""
    r = rng(seed)
    paper = np.array([222, 214, 196], dtype=float)
    if kind == 'face':
        img = sheet_frame('tv0')[:, :, :3].astype(float)
        ih, iw = img.shape[:2]
        w, h = iw + 2, ih + 3
        P = np.zeros((h, w, 3)) + paper
        P[1:1 + ih, 1:1 + iw] = img
    else:
        w, h = 16, 22
        yy, xx = np.mgrid[0:h, 0:w]
        P = np.zeros((h, w, 3)) + (176, 30, 22)
        P[(yy >= 14) & (yy < 17)] = (236, 196, 56)
        ring = np.abs(np.sqrt((xx - 7.5) ** 2 + (yy - 7.0) ** 2) - 5.0) < 0.8
        P[ring & ((xx + yy) % 2 == 0)] = (226, 190, 64)
        for i, j in [(7, 5), (8, 5), (7, 6), (8, 6), (7, 7), (8, 7), (7, 8), (8, 8), (7, 9), (8, 10), (9, 10), (10, 9),
                     (5, 4), (4, 3), (10, 4), (11, 3), (5, 6), (4, 7), (10, 6), (11, 7), (9, 11), (10, 11)]:
            P[j, i] = (248, 220, 104)
        P[0, :] = paper; P[-1, :] = paper; P[:, 0] = paper; P[:, -1] = paper
    yy, xx = np.mgrid[0:h, 0:w]
    fade = 0.18 + 0.20 * noise((h, w), seed, 3, 3)
    P = P * (1 - fade[..., None]) + paper * fade[..., None]
    sx = int(r.integers(2, w - 2))
    streak = (np.abs(xx - sx) < 1) & (yy > h * 0.35)
    P[streak] = P[streak] * 0.82
    m = np.ones((h, w), bool)
    c = int(r.integers(0, 4))
    for j in range(4):
        for i in range(4 - j):
            m[j if c < 2 else h - 1 - j, i if c % 2 == 0 else w - 1 - i] = False
    P = np.clip(np.round(P / 8) * 8, 0, 255).astype(np.uint8)
    Q = Layer(w, h)
    Q.put(P, m)
    L.paste(Q, int(x), int(y))
    return dict(x=int(x + w // 2), y=int(y), w=int(w), h=int(h), kind=kind)


# ------------------------------------------------------------------ the checkpoint
def drum(L, x, base, seed=1, rmp=None, h=17, w=11):
    """An oil drum standing on end: painted, rusting, two hoops, its lid catching the light."""
    rmp = rmp if rmp is not None else REDP
    r = rng(seed)
    T = Tone(L.w, L.h)
    Rr = Tone(L.w, L.h)
    for j in range(h):
        for i in range(w):
            u = i / float(w - 1)
            t = 0.70 - 0.50 * abs(u - 0.32) ** 1.2 * 1.6 - 0.06 * (j > h - 3)
            if j in (int(h * 0.33), int(h * 0.66)):
                t += 0.14
            if r.random() < 0.10 + 0.25 * (j > h * 0.7):
                Rr.px(x + i, base - h + j, 0.40 + 0.3 * r.random())
            else:
                T.px(x + i, base - h + j, t)
    for i in range(1, w - 1):
        T.px(x + i, base - h - 1, 0.86 - 0.03 * i)
    put_tone(L, T, rmp, dither=0.3)
    put_tone(L, Rr, RUSTI, dither=0.3)


def tyre(L, x, base, seed=1, r_=8):
    """An old tyre lying on its side against the drums."""
    T = Tone(L.w, L.h)
    for j in range(-4, 1):
        for i in range(-r_, r_ + 1):
            e = (i / float(r_)) ** 2 + ((j + 2) / 2.6) ** 2
            if e <= 1.0:
                inner = (i / (r_ * 0.55)) ** 2 + ((j + 2.6) / 1.2) ** 2 < 1.0
                T.px(x + i, base + j, 0.08 if inner else 0.36 + 0.24 * (j == -4) - 0.10 * (i > 0))
    put_tone(L, T, TYRE, dither=0)


def checkpoint(L, x, seed=11):
    """The Zanabeel's checkpoint, the part on the verge: a booth of corrugated iron with its door open on the dark and a
    plastic chair in there, a window, kerbstones painted their red and white, their flag on its roof, a poster of the
    Spokesman on it; and the barrier pole beside it, up (they let you through, for now). -> what the level needs."""
    r = rng(seed)
    bx0, bx1 = x + 36, x + 82
    btop = VERGE - 42
    T = Tone(L.w, L.h)
    for yy in range(btop + 3, VERGE + 4):
        for xx in range(bx0, bx1):
            rib = (xx - bx0) % 4
            T.px(xx, yy, 0.58 + 0.10 * (rib == 0) - 0.08 * (rib == 2) - 0.12 * (xx > bx1 - 10) - 0.06 * ((yy - btop) > 32))
    put_tone(L, T, TIN, dither=0.3, grain=0.06, seed=seed)
    Rr = Tone(L.w, L.h)
    for k in range(34):
        rx, ry = int(r.integers(bx0 + 1, bx1 - 1)), int(r.integers(btop + 6, VERGE + 2))
        for j in range(int(r.integers(2, 7))):
            Rr.px(rx, ry + j, 0.40 + 0.25 * r.random())
    put_tone(L, Rr, RUSTI, dither=0.2)
    # the door, open on the dark, the chair in there; the window beside it
    D = Tone(L.w, L.h)
    for yy in range(btop + 9, VERGE + 3):
        for xx in range(bx0 + 4, bx0 + 19):
            D.px(xx, yy, 0.10 + 0.04 * ((xx + yy) % 5 == 0))
    for yy in range(btop + 10, btop + 21):
        for xx in range(bx0 + 25, bx1 - 6):
            D.px(xx, yy, 0.14 + 0.05 * ((xx * 2 + yy) % 7 == 0))
    put_tone(L, D, SOOT, dither=0)
    C = Tone(L.w, L.h)
    cxh, cb = bx0 + 8, VERGE + 2
    for j in range(9):
        C.px(cxh + 6, cb - 7 - j, 0.80)
    for i in range(7):
        C.px(cxh + i, cb - 7, 0.92)
        C.px(cxh + i, cb - 6, 0.64)
    for j in range(6):
        C.px(cxh, cb - 5 + j, 0.62)
        C.px(cxh + 6, cb - 5 + j, 0.50)
    put_tone(L, C, PLASTIC, dither=0)
    # kerbstones along its front, painted red and white
    K = np.zeros((SH, L.w), np.uint8)
    for xx in range(bx0 - 8, bx1 + 8):
        for yy in (VERGE + 4, VERGE + 5):
            K[yy, xx] = 1 if ((xx - bx0) // 6) % 2 == 0 else 2
    L.rgb[K == 1] = (192, 44, 30)
    L.rgb[K == 2] = (224, 220, 206)
    L.a |= K > 0
    # the roof: a sheet laid across, overhanging, its edge catching the light
    R = Tone(L.w, L.h)
    for i in range(bx0 - 6, bx1 + 6):
        u = (i - (bx0 - 6)) / float(bx1 - bx0 + 12)
        y0 = int(round(btop + 1 - 2 * u))
        R.px(i, y0, 0.86)
        R.px(i, y0 + 1, 0.62 + 0.10 * (i % 4 == 0))
        R.px(i, y0 + 2, 0.30)
    put_tone(L, R, TIN, dither=0.2)
    plat('booth', [(bx0 - 4, btop), (bx1 + 4, btop - 2)])
    poster(L, bx0 + 24, btop + 24, 'badge', seed=seed + 3)
    # their flag on a pole on the roof
    F = Tone(L.w, L.h)
    fx = bx1 - 4
    for j in range(30):
        F.px(fx, btop - 1 - j, 0.30)
    put_tone(L, F, SOOT, dither=0)
    yy, xx = np.mgrid[0:12, 0:18]
    wave = np.round(np.sin(xx / 3.0) * 1.2).astype(int)
    band = ((yy - wave) >= 5) & ((yy - wave) < 8)
    Fl = np.where(band[..., None], np.array([232, 192, 56]), np.array([184, 34, 24])).astype(float)
    Fl *= np.where(((xx // 3) % 2 == 1)[..., None], 0.86, 1.0)
    Q = Layer(18, 12)
    Q.put((np.round(Fl / 8) * 8).astype(np.uint8), (yy - wave >= 0) & (yy - wave < 11))
    L.paste(Q, fx + 1, btop - 31)
    # the barrier: a striped pole on a post, up
    B = Tone(L.w, L.h)
    px0, pb = x + 6, VERGE + 6
    for j in range(24):
        B.px(px0, pb - j, 0.50); B.px(px0 + 1, pb - j, 0.30)
    put_tone(L, B, CONCRETE, dither=0)
    S = np.zeros((SH, L.w), dtype=np.uint8)
    for i in range(48):
        bx_, by_ = px0 + 1 + int(i * 0.5), pb - 22 - int(i * 0.86)
        for k in range(2):
            if 0 <= by_ + k < SH and 0 <= bx_ + k < L.w:
                S[by_ + k, bx_ + k] = 1 if (i // 6) % 2 == 0 else 2
    L.rgb[S == 1] = (200, 40, 28)
    L.rgb[S == 2] = (232, 228, 216)
    L.a |= S > 0
    return dict(booth=[bx0, bx1], door=dict(x=int(bx0 + 11), y=int(WALK)), tv=int(bx1 + 14))


def checkpoint_road(L, x, seed=11):
    """The checkpoint's part on the road: a wall of sandbags (somewhere to stand, and to hide behind), two drums, a tyre."""
    SM.sack_pile(L, [(x + 10, x + 62, WALK - 16), (x + 17, x + 55, WALK - 23)], WALK + 2, seed=seed, green=True, marks=False)
    plat('sandbags', [(x + 12, WALK - 22), (x + 60, WALK - 22)])
    drum(L, x + 64, WALK + 2, seed=seed + 1, rmp=REDP)
    drum(L, x + 75, WALK + 3, seed=seed + 2, rmp=BLUEP)
    tyre(L, x + 92, WALK + 2, seed=seed)
    SM.soft_shadow(L, x + 8, x + 100, WALK + 3, h=3, amt=0.74)


# ------------------------------------------------------------------ the farmhouse
def farmhouse(L, x, seed=21):
    """A stone farmhouse of the valley, two storeys of Ibb's grey stone with white bands, qamariya windows, its parapet
    toothed white, a water tank and a dish on the roof; a one-storey store at its side with a flat roof, and a courtyard
    wall in front of that, so a man can climb: the wall, the store's roof, the house's roof. -> what the level needs."""
    r = rng(seed)
    hx0, hx1 = x + 40, x + 124
    base = VERGE + 6
    gf, fl, par = 36, 38, 7
    top = base - gf - fl - par
    STZ.ashlar(L, hx0, base - gf, hx1, base, IBBSTONE, seed=seed + 1, course=6, block=(9, 18), base=0.42)
    STZ.ashlar(L, hx0, top + par, hx1, base - gf, IBBSTONE, seed=seed + 2, course=6, block=(10, 22), base=0.56)
    STZ.plaster(L, hx0, top, hx1, top + par, LIME, seed=seed + 3, base=0.86, stain=0.3)
    STZ.merlons_point(L, hx0, hx1, top - 1, seed=seed)
    STZ.white_band(L, hx0, hx1, base - gf - 2, h=4, kind=1, seed=seed)
    STZ.white_band(L, hx0, hx1, top + par - 1, h=4, kind=0, seed=seed + 5)
    wins = []
    for k, wx in enumerate((hx0 + 12, hx0 + 38, hx0 + 64)):
        wins.append(STZ.qamariya_window(L, wx, base - gf - fl + 14, w=10, h=14, paint=STZ.BLUEWOOD, open_=(k == 1), seed=seed + k))
    door = STZ.arched_door(L, hx0 + 30, base, w=14, h=24, paint=STZ.BLUEWOOD, open_=True, seed=seed)
    STZ.small_window(L, hx0 + 60, base - gf + 10, w=6, h=7)
    for yy in range(top, base):
        for xx in range(hx1 - 4, hx1):
            if L.a[yy, xx]:
                L.rgb[yy, xx] = (L.rgb[yy, xx].astype(float) * (0.80 - 0.05 * (xx - (hx1 - 4)))).astype(np.uint8)
    SZ.water_tank(L, hx0 + 18, top - 1, seed=seed)
    SZ.dish_at(L, hx1 - 22, top - 1, seed=seed)
    plat('house', [(hx0 + 1, top - 1), (hx1 - 1, top - 1)])
    # the store at its right: one storey, a flat roof with a low lip, a wooden door shut
    sx0, sx1 = hx1, hx1 + 54
    stop = base - 40
    STZ.ashlar(L, sx0, stop + 4, sx1, base, IBBSTONE, seed=seed + 7, course=5, block=(8, 16), base=0.50)
    STZ.plaster(L, sx0, stop, sx1, stop + 4, LIME, seed=seed + 8, base=0.80, stain=0.3)
    STZ.arched_door(L, sx0 + 20, base, w=12, h=20, paint=TEAK, open_=False, seed=seed + 1)
    plat('store', [(sx0, stop - 1), (sx1 - 1, stop - 1)])
    # the courtyard wall in front of the store, a little lower: the first step up
    tops = drystone(L, sx0 + 10, sx1 + 30, base - 24, base + 2, seed=seed + 9)
    plat('yardwall', [(sx0 + 30, base - 25), (sx1 + 28, base - 25)])
    # a pile of firewood by the door
    return dict(door=door, x0=hx0, x1=sx1 + 30, top=top, windows=wins)


# ------------------------------------------------------------------ the roadside shop
def shop(L, x, seed=31):
    """A roadside shop: one storey of plastered block with columns standing up out of its roof for the floor nobody has
    built yet, two shutters (one up on the dark of the shop and its shelves, one down, green and dented), a blank yellow
    signboard over them, an awning of corrugated iron on poles in front, crates of tomatoes and a stack of gas bottles
    outside, posters on its side wall. -> what the level needs."""
    r = rng(seed)
    x0, x1 = x, x + 136
    base = ROAD_TOP - 2
    top = base - 50
    STZ.plaster(L, x0, top, x1, base, LIME, seed=seed, base=0.74, stain=1.2)
    T = Tone(L.w, L.h)
    for xx in range(x0, x1):
        T.px(xx, top, 0.90); T.px(xx, top + 1, 0.62)
    put_tone(L, T, CONCRETE, dither=0)
    # the columns and their rods, waiting for the next floor
    C = Tone(L.w, L.h)
    for cx in (x0 + 2, x0 + 66, x1 - 8):
        for yy in range(top - 14, top):
            for i in range(6):
                C.px(cx + i, yy, 0.62 - 0.10 * (i > 3) + 0.10 * (i == 0))
        for i in (1, 4):
            for yy in range(top - 22, top - 14):
                C.px(cx + i, yy, 0.30)
    put_tone(L, C, CONCRETE, dither=0.3)
    Rr = Tone(L.w, L.h)
    for cx in (x0 + 2, x0 + 66, x1 - 8):
        for i in (1, 4):
            for yy in range(top - 22, top - 14):
                Rr.px(cx + i, yy, 0.45 + 0.15 * (yy % 2))
    put_tone(L, Rr, RUSTI, dither=0)
    plat('shoproof', [(x0 + 1, top - 1), (x1 - 1, top - 1)])
    # the sign over the shutters: blank yellow, a red stripe, rust running from its bolts
    Sg = Tone(L.w, L.h)
    for yy in range(top + 4, top + 15):
        for xx in range(x0 + 10, x1 - 10):
            Sg.px(xx, yy, 0.62 + 0.10 * (yy == top + 4) - 0.12 * (yy == top + 14) + 0.04 * ((xx * 7 + yy) % 9 == 0))
    put_tone(L, Sg, SIGNY, dither=0.3)
    St = Tone(L.w, L.h)
    for xx in range(x0 + 10, x1 - 10):
        St.px(xx, top + 11, 0.62); St.px(xx, top + 12, 0.50)
    put_tone(L, St, REDP, dither=0)
    # the shutters: the left one down, the right one up on the shop
    sy0 = top + 18
    Sh = Tone(L.w, L.h)
    for yy in range(sy0, base):
        for xx in range(x0 + 10, x0 + 62):
            rib = (yy - sy0) % 3
            dent = 0.08 * (((xx - x0) * 13 + (yy - sy0) * 7) % 23 == 0)
            Sh.px(xx, yy, 0.56 + 0.12 * (rib == 0) - 0.10 * (rib == 2) - dent - 0.10 * ((xx - x0) > 52))
    put_tone(L, Sh, SHUTG, dither=0.3)
    D = Tone(L.w, L.h)
    for yy in range(sy0 + 4, base):
        for xx in range(x0 + 70, x1 - 10):
            D.px(xx, yy, 0.12 + 0.03 * ((xx + yy) % 4 == 0))
    put_tone(L, D, SOOT, dither=0)
    Sh2 = Tone(L.w, L.h)
    for yy in range(sy0, sy0 + 4):
        for xx in range(x0 + 70, x1 - 10):
            Sh2.px(xx, yy, 0.60 + 0.12 * ((yy - sy0) % 2 == 0))
    put_tone(L, Sh2, SHUTG, dither=0)
    # shelves inside, with tins and packets on them
    G = np.zeros((SH, L.w, 3), dtype=np.uint8)
    Gm = np.zeros((SH, L.w), bool)
    goods = [(200, 48, 32), (232, 196, 60), (60, 120, 180), (236, 232, 220), (80, 160, 80), (210, 120, 40)]
    for sy in (sy0 + 9, sy0 + 17, sy0 + 25):
        for xx in range(x0 + 72, x1 - 12):
            Gm[sy, xx] = True
            G[sy, xx] = (96, 72, 48)
            if (xx * 5 + sy) % 7 < 4:
                c = goods[(xx * 3 + sy) % len(goods)]
                for j in range(1, 4):
                    if (xx + j) % 3:
                        Gm[sy - j, xx] = True
                        G[sy - j, xx] = (np.array(c) * (0.70 - 0.12 * (j == 1))).astype(np.uint8)
    L.rgb[Gm] = G[Gm]
    L.a |= Gm
    # posters on the side wall by the door
    p1 = poster(L, x0 + 63, top + 22, 'face', seed=seed + 1)
    # the awning: a sheet of corrugated iron sloping out over the front toward the road, its top seen from just above,
    # its front edge a dark line, its shade on the shutters; two poles hold its front up
    ax0, ax1 = x0 - 6, x1 + 6
    ay_back, ay_front = top + 15, top + 22
    Aw = Tone(L.w, L.h)
    for xx in range(ax0, ax1):
        rib = (xx - ax0) % 4
        for yy in range(ay_back, ay_front):
            v = (yy - ay_back) / float(ay_front - ay_back)
            Aw.px(xx, yy, 0.70 - 0.16 * v + 0.12 * (rib == 0) - 0.10 * (rib == 2))
        Aw.px(xx, ay_front, 0.34 + 0.08 * (rib == 0))
        Aw.px(xx, ay_front + 1, 0.20)
    put_tone(L, Aw, TIN, dither=0.3, grain=0.05, seed=seed)
    Ar = Tone(L.w, L.h)
    for k in range(70):
        rx = int(r.integers(ax0, ax1))
        ry = int(r.integers(ay_back, ay_front))
        for j in range(int(r.integers(1, 4))):
            Ar.px(rx, ry + j, 0.42 + 0.25 * r.random())
    put_tone(L, Ar, RUSTI, dither=0)
    SM.shade_box(L, x0, ay_front + 2, x1, ay_front + 9, 0.80)
    Po = Tone(L.w, L.h)
    for px_ in (ax0 + 3, ax1 - 4):
        for yy in range(ay_front + 2, ROAD_TOP + 3):
            Po.px(px_, yy, 0.56); Po.px(px_ + 1, yy, 0.30)
    put_tone(L, Po, CONCRETE, dither=0)
    plat('awning', [(ax0, ay_back + 2), (ax1, ay_back + 2)])
    # outside: crates of tomatoes, gas bottles, a fridge by the open shutter
    Cr = Tone(L.w, L.h)
    tm = Tone(L.w, L.h)
    for k, (cx, cyb) in enumerate(((x0 + 74, base + 6), (x0 + 88, base + 6), (x0 + 81, base - 3))):
        SM.crate_tone(Cr, cx, cyb - 9, 14, 9, seed=seed + k)
        for i in range(1, 13, 2):
            tm.px(cx + i, cyb - 10, 0.70 - 0.2 * (i % 4 == 1))
            tm.px(cx + i + 1, cyb - 10, 0.52)
    put_tone(L, Cr, TEAK, dither=0.3)
    put_tone(L, tm, TOMATO, dither=0)
    Gb = Tone(L.w, L.h)
    for k in range(4):
        gx = x0 + 108 + k * 6
        for j in range(15):
            for i in range(5):
                t = 0.62 - 0.30 * abs(i - 1.5) / 2.5 - 0.10 * (j > 12)
                Gb.px(gx + i, base + 6 - j, t)
        Gb.px(gx + 2, base + 6 - 15, 0.30); Gb.px(gx + 2, base + 6 - 16, 0.30)
    put_tone(L, Gb, BLUEP, dither=0.3)
    SM.soft_shadow(L, x0 - 4, x1 + 4, base + 6, h=3, amt=0.76)
    return dict(x0=x0, x1=x1, top=top, door=dict(x=int(x0 + 100), y=int(base)), tv=int(x0 + 40), posters=[p1])


# ------------------------------------------------------------------ the minibus
def minibus(L, x, seed=41):
    """A white minibus with a blue stripe that has given up at the side of the road, nose to the left: its front tyre
    flat, its sliding door open on the dark, the luggage still roped on the rack, rust at the sills, a red triangle set
    out behind it. Its rack is somewhere to stand. -> what the level needs."""
    r = rng(seed)
    x0, x1 = x, x + 104
    base = WALK - 1
    roof = base - 42
    sill = base - 9
    B = Tone(L.w, L.h)
    for yy in range(roof, sill):
        for xx in range(x0, x1):
            dx = xx - x0
            if dx < 9 and (yy - roof) < 9 - dx:                 # the nose, rounded over the windscreen
                continue
            if dx > 101 and (yy - roof) < 2:
                continue
            v = (yy - roof) / float(sill - roof)
            t = 0.76 - 0.20 * v + 0.12 * (yy == roof) - 0.06 * (dx > 90)
            t += 0.10 * (dx < 3) - 0.04 * ((xx * 7 + yy * 3) % 17 == 0)
            B.px(xx, yy, t)
    put_tone(L, B, BUSW, dither=0.35)
    # the windows: windscreen and the side ones, dark with the sky in them
    Wn = Tone(L.w, L.h)
    for yy in range(roof + 4, roof + 15):
        for xx in range(x0 + 2, x1 - 4):
            dx = xx - x0
            if dx < 11 and (yy - roof) < 12 - dx:
                continue
            if dx in (14, 15, 36, 37, 58, 59, 80, 81):
                continue
            Wn.px(xx, yy, 0.30 + 0.32 * (((xx + (yy - roof) * 2) % 15) < 3) + 0.10 * (yy == roof + 4))
    put_tone(L, Wn, WATER, dither=0.3)
    # the stripe, the sills rusting, the wheel arches, the lamps, the bumper, the mirror
    Bs = Tone(L.w, L.h)
    for yy in range(roof + 19, roof + 23):
        for xx in range(x0 + 1, x1):
            Bs.px(xx, yy, 0.64 - 0.08 * (yy - roof - 19))
    put_tone(L, Bs, BUSB, dither=0)
    Ru = Tone(L.w, L.h)
    for xx in range(x0, x1):
        for yy in range(sill - 4, sill):
            if hash_(xx * 3 + yy, seed) < 0.22 + 0.10 * (yy - sill + 4):
                Ru.px(xx, yy, 0.40 + 0.3 * hash_(xx, yy))
    put_tone(L, Ru, RUSTI, dither=0)
    K = Tone(L.w, L.h)
    for wx in (x0 + 20, x0 + 82):
        for i in range(-11, 12):
            for j in range(0, 12):
                if i * i + (j - 11) ** 2 <= 121 and i * i + (j - 11) ** 2 >= 64:
                    K.px(wx + i, sill - 11 + j, 0.14)
    for xx in range(x0 - 2, x0 + 12):
        K.px(xx, sill, 0.40); K.px(xx, sill + 1, 0.26)               # the front bumper
    for xx in range(x1 - 10, x1 + 2):
        K.px(xx, sill, 0.40); K.px(xx, sill + 1, 0.26)
    for j in range(5):
        K.px(x0 - 1, roof + 9 + j, 0.20)                              # the mirror's arm and glass
    K.px(x0 - 2, roof + 9, 0.30); K.px(x0 - 3, roof + 10, 0.30); K.px(x0 - 3, roof + 11, 0.30)
    put_tone(L, K, SOOT, dither=0)
    Lm = np.zeros((SH, L.w), np.uint8)
    for j in range(3):
        for i in range(3):
            Lm[sill - 5 + j, x0 + 1 + i] = 1                         # a headlamp
            Lm[sill - 7 + j, x1 - 3 + i - 1] = 2                     # a tail lamp
    L.rgb[Lm == 1] = (240, 232, 196)
    L.rgb[Lm == 2] = (200, 40, 32)
    L.a |= Lm > 0
    # the sliding door, open on the dark, a seat inside
    Dd = Tone(L.w, L.h)
    for yy in range(roof + 4, sill):
        for xx in range(x0 + 40, x0 + 57):
            Dd.px(xx, yy, 0.08 + 0.05 * ((xx + yy) % 6 == 0) + 0.25 * ((yy - roof) in (22, 23)) * (xx < x0 + 52))
    put_tone(L, Dd, SOOT, dither=0)
    # the wheels: the back one round, the front one flat on the road
    Wh = Tone(L.w, L.h)
    for wx, flat in ((x0 + 20, True), (x0 + 82, False)):
        cy = base - 7 if not flat else base - 5
        for j in range(-8, 9):
            for i in range(-9, 10):
                if flat:
                    e = (i / 9.0) ** 2 + (j / 6.5) ** 2 if j < 0 else (i / 9.5) ** 2 + (j / 5.0) ** 4
                else:
                    e = (i / 8.0) ** 2 + (j / 8.0) ** 2
                if e <= 1.0:
                    hub = (i * i + j * j) < (10 if not flat else 8)
                    Wh.px(wx + i, cy + j, 0.60 if hub else 0.32 - 0.10 * (i > 0) + 0.08 * (j < -5))
    put_tone(L, Wh, TYRE, dither=0)
    # the rack, and the luggage roped on it: bags, a rolled mattress, a box
    Rk = Tone(L.w, L.h)
    for xx in range(x0 + 10, x1 - 4):
        Rk.px(xx, roof - 4, 0.44)
    for xx in range(x0 + 12, x1 - 4, 10):
        for j in range(4):
            Rk.px(xx, roof - 4 + j, 0.30)
    put_tone(L, Rk, SOOT, dither=0)
    Lg = Tone(L.w, L.h)
    for k, (bx, bw, bh) in enumerate([(x0 + 14, 22, 9), (x0 + 38, 26, 12), (x0 + 88, 12, 7)]):
        for j in range(bh):
            for i in range(bw):
                if (i in (0, bw - 1)) and j in (0, bh - 1):
                    continue
                Lg.px(bx + i, roof - 5 - j, 0.72 - 0.40 * j / float(bh - 1) * 0 - 0.36 * (1 - j / float(bh - 1)) * 0 + 0.30 * (j / float(bh - 1)) - 0.16 * (i / float(bw - 1)))
    put_tone(L, Lg, SM.SACK, dither=0.35)
    Mt = Tone(L.w, L.h)
    for j in range(8):
        for i in range(22):
            e = ((j - 3.5) / 4.0) ** 2
            if e <= 1:
                Mt.px(x0 + 64 + i, roof - 5 - j, 0.72 - 0.10 * abs(j - 3) + 0.14 * ((i // 3) % 2 == 0) - 0.12 * (j < 2))
    put_tone(L, Mt, BLUEP, dither=0.3)
    Rp = Tone(L.w, L.h)
    for xx in range(x0 + 12, x1 - 6):
        if (xx // 2) % 2 == 0:
            Rp.px(xx, roof - 9 - int(round(2.5 * np.sin((xx - x0) / 6.0))), 0.80)
    put_tone(L, Rp, SIGNY, dither=0)
    plat('busrack', [(x0 + 12, roof - 14), (x0 + 64, roof - 16), (x1 - 8, roof - 12)])
    # yellow jerrycans stacked by its back door: a step up to the rack
    Jc = Tone(L.w, L.h)
    for (jx, jb) in ((x1 + 6, WALK + 1), (x1 + 15, WALK + 1), (x1 + 10, WALK - 10)):
        for j in range(11):
            for i in range(8):
                t = 0.66 - 0.26 * (i / 7.0) + 0.12 * (j == 0) - 0.10 * (j == 10) + 0.06 * ((j % 4) == 2)
                Jc.px(jx + i, jb - 11 + j, t)
        Jc.px(jx + 5, jb - 12, 0.40); Jc.px(jx + 6, jb - 12, 0.40)
    put_tone(L, Jc, SIGNY, dither=0.2)
    plat('cans', [(x1 + 10, WALK - 22), (x1 + 17, WALK - 22)])
    # the warning triangle set out behind
    Tr = Tone(L.w, L.h)
    tx = x1 + 44
    for j in range(8):
        for i in range(-j // 2 - 1, j // 2 + 2):
            if abs(i) >= j // 2 or j == 7:
                Tr.px(tx + i, base - 6 + j, 0.62)
    put_tone(L, Tr, REDP, dither=0)
    SM.soft_shadow(L, x0 + 4, x1 + 2, base + 1, h=4, amt=0.70)
    return dict(x0=x0, x1=x1, roof=roof, door=dict(x=int(x0 + 49), y=int(WALK)))


# ------------------------------------------------------------------ zone 1, put together
def play_z1(seed=101):
    """The valley road, 0 to 1280: the opening under the billboard; a field and a sidr tree; the checkpoint; the
    farmhouse; the roadside shop; the minibus; the fields climbing at the end toward Jibla."""
    I.PLATS.clear()
    I.INFO.clear()
    W = W1
    L = Layer(W, SH)
    r = rng(seed)
    # (1) the field behind the wall: eucalyptus along it, sorghum standing in it, a sidr tree
    for k, (ex, eh) in enumerate(((236, 132), (262, 116), (1020, 128), (1048, 140), (1218, 124))):
        eucalyptus(L, ex, VERGE - 10, hgt=eh, seed=seed + k)
    for k, (cx0, cx1) in enumerate(((0, 560), (760, 1280))):
        crops(L, cx0, cx1, VERGE - 12, seed=seed + 20 + k)
    sidr(L, 404, VERGE - 12, seed=seed + 9)
    # (2) the wall along the field, the verge
    walls = [(0, 572, 146), (740, 806, 148), (976, 1280, 146)]
    for k, (wx0, wx1, wt) in enumerate(walls):
        drystone(L, wx0, wx1, wt, VERGE + 2, seed=seed + 30 + k)
    verge(L, 0, W, seed=seed + 40)
    # posters on the wall
    I.INFO['posters'] = [poster(L, 282, 140, 'face', seed=1), poster(L, 320, 141, 'badge', seed=2),
                         poster(L, 776, 138, 'face', seed=3), poster(L, 1004, 140, 'face', seed=4), poster(L, 1040, 142, 'badge', seed=5)]
    # (3) the buildings on the verge
    cp = checkpoint(L, 452, seed=seed + 50)
    fh = farmhouse(L, 572, seed=seed + 60)
    sh = shop(L, 816, seed=seed + 70)
    # (4) the poles and their wires: two with loudspeakers
    poles = [(214, 1), (520, 0), (800, 2), (1080, 0), (1276, 0)]
    ends = [pole(L, px_, VERGE + 4, hgt=112, seed=seed + 80 + k, horns=hn) for k, (px_, hn) in enumerate(poles)]
    for a, b in zip(ends[:-1], ends[1:]):
        wires(L, a, b, sag=9)
    wires(L, [(e[0] - 260, e[1] + 10) for e in ends[0]], ends[0], sag=9)
    # (5) the road
    road(L, 0, W, seed=seed + 90)
    for k, (px_, py_, pw, ph_) in enumerate(((150, 200, 44, 5), (330, 192, 26, 3), (700, 206, 60, 6), (930, 190, 30, 3), (1180, 204, 40, 5))):
        puddle(L, px_, py_, pw, ph_, seed=seed + 100 + k)
    # (6) on the road: the minibus
    checkpoint_road(L, 452, seed=seed + 50)
    mb = minibus(L, 1100, seed=seed + 110)
    I.INFO.update(checkpoint=cp, farmhouse=dict(door=fh['door'], x0=fh['x0'], x1=fh['x1']), shop=dict(door=sh['door'], tv=sh['tv']),
                  minibus=dict(door=mb['door']), billboard=120, poles=[p for p, h in poles], horns=[p for p, h in poles if h])
    return L


def fore_z1(w=1640, seed=131):
    """What passes close to the lens along the road: tufts of grass and stones on the near verge, a fence post now and then."""
    L = Layer(w, SH)
    r = rng(seed)
    T = Tone(w, SH)
    G = Tone(w, SH)
    x = 0
    while x < w:
        if r.random() < 0.5:
            # a clump of grass: blades fanning up from the bottom edge
            n = int(r.integers(5, 12))
            hgt = r.uniform(8, 18)
            for k in range(n):
                a = (k / float(n - 1) - 0.5) * 1.4
                ln = hgt * r.uniform(0.6, 1.0)
                for i in range(int(ln)):
                    G.px(int(round(x + np.sin(a) * i + 0.02 * i * i * np.sign(a))), SH - 1 - int(i * np.cos(a)), 0.30 + 0.5 * i / ln)
        else:
            rw, rh = int(r.integers(8, 20)), int(r.integers(4, 9))
            for j in range(rh):
                for i in range(rw):
                    e = ((i - rw / 2.0) / (rw / 2.0)) ** 2 + ((j - rh) / float(rh)) ** 2
                    if e <= 1:
                        T.px(x + i, SH - rh + j, 0.50 - 0.25 * (i / rw) + 0.20 * (j < 2) - 0.10 * (j > rh - 2))
        x += int(r.integers(60, 180))
    put_tone(L, T, DRYST, dither=0.3)
    put_tone(L, G, GRASS, dither=0.3)
    return L


if __name__ == '__main__':
    import sys, time
    t0 = time.time()
    S = I.backgrounds()
    S['play'] = play_z1()
    S['fore'] = fore_z1()
    print('painted in %.1f s' % (time.time() - t0))
    out = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/ibb/s3/'
    print(I.preview(S, [0, 300, 560, 820], out + 'z1_a.png', lines=False))
    print(I.preview(S, [0, 300, 560, 820], out + 'z1_a_lines.png', lines=True))
    print(I.preview(S, [880, 1100], out + 'z1_b.png', lines=False))
    print(sorted(I.PLATS.items()))
