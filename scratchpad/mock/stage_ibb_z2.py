# stage_ibb_z2.py - Ibb's zone 2, Jibla (Khaled, 24 Oct 23:29: "Continue": the next zone). Queen Arwa's old town, built on
# the side of a mountain over a terraced valley: stone tower houses with white bands and qamariya windows, alleys so steep
# and narrow no car goes up them (worldheritagesite.org, tentative list), and the Queen Arwa mosque among the houses with
# its two minarets (one on a high square stone base, its shaft ribbed) and two domes (Wikipedia, Queen Arwa Mosque).
# The street runs along the foot of the town; the town climbs behind it (a layer of its own, `back`, between the hills
# and the street, so it moves at its own pace); the mosque stands up there, in the background and out of bounds.
# Along the street, left to right: the edge of town (the road turning to cobbles, a shop with a set in front), houses with
# a stepped alley up to a roof, the school (its yard open to the street: a flagpole, sets on crates, the building at the
# back with barred classrooms and a walkway along its upper floor, stairs up to it), more houses and a second alley, the
# gap where the mosque shows over a low wall, a last house with a shop, and the path out of town toward the terraces.
# Platforms and what else the level needs are recorded in world coordinates (I.PLATS, I.INFO['z2']).
import numpy as np
from scipy import ndimage as ndi
from paint import *
import stage_mocha as SM
import stage_taiz as STZ
import stage_zabid as SZ
import stage_ibb as I
import stage_ibb_z1 as Z1

SH, WALK = I.SH, I.WALK
X0 = Z1.W1                      # zone 2 starts where zone 1's picture ends
W2 = 1360
END2 = X0 + W2                  # 2640
BASE = 170                      # where the houses' fronts stand, behind the street
ROAD_TOP = Z1.ROAD_TOP          # the street's back edge
put_tone, plat = SM.put_tone, I.plat
IBBSTONE, CONCRETE, SHUTG, SIGNY, PLASTIC, BLUEP, REDP, GOLD = (Z1.IBBSTONE, Z1.CONCRETE, Z1.SHUTG, Z1.SIGNY, Z1.PLASTIC,
                                                              Z1.BLUEP, Z1.REDP, Z1.GOLD)
LIME, TEAK, SOOT, DRYST, LEAF, TERR = SM.LIME, SM.TEAK, SM.SOOT, I.DRYST, I.LEAF, I.TERR
COBBLE = ramp(['#141210', '#24201c', '#36302a', '#4a433b', '#5e564c', '#746a5e', '#8a8072', '#a29888', '#bab0a0'], 18)   # wet setts
SCHOOL = ramp(['#22261c', '#3c4232', '#5a6250', '#7a846e', '#9aa48c', '#b8c2a8', '#d2dac2', '#e8eedc'], 16)         # the school's pale green wash
IRONG = ramp(['#081410', '#10221a', '#1a3428', '#264838', '#345e4a', '#467660'], 10)                               # its green iron


def wx(lx):
    return int(lx + X0)


def lx_(x):
    return int(x - X0)


# ------------------------------------------------------------------ houses
def house(L, x, w, h, seed, floors=1, door=True, roof=(), stone=True):
    """A tower house of Jibla, its foot at BASE: Ibb's grey stone, a darker ground floor, white bands between the floors
    and round the parapet, qamariya windows, a toothed white parapet (Taiz's house, in Ibb's stone). x is local.
    -> (the roof's height, the street door's middle (local x) or None)."""
    old = STZ.TSTONE
    STZ.TSTONE = IBBSTONE
    try:
        P, info = STZ.taiz_house(w, h, seed=seed, style='stone' if stone else 'lime', roof=list(roof), door='street' if door else None, floors=floors)
    finally:
        STZ.TSTONE = old
    y0 = BASE - P.h
    L.paste(P, x, y0)
    d = info['doors'][0]['x'] + x if info['doors'] else None
    return y0 + info['top'], d


def stairs(L, x0, steps, rise=14, run=13, seed=1, up=1):
    """A stepped alley: stone steps climbing from the street (up=1: to the right, -1: to the left), each a platform; the
    flight sits on a wall of coursed stone. x0 is local, at the foot. -> each step's (local x0, x1, y)."""
    T = Tone(L.w, L.h)
    tops = []
    for k in range(steps):
        y = BASE - 12 - k * rise
        if up > 0:
            sx0, sx1 = x0 + k * run, x0 + (k + 1) * run + 4
        else:
            sx0, sx1 = x0 - (k + 1) * run - 4, x0 - k * run
        tops.append((sx0, sx1, y))
    xs0 = min(t[0] for t in tops)
    xs1 = max(t[1] for t in tops)
    for xx in range(xs0, xs1):
        # the height of the flight over this column: the highest step that covers it
        ys = [t[2] for t in tops if t[0] <= xx < t[1]]
        if not ys:
            continue
        ytop = min(ys)
        for yy in range(ytop, BASE + 2):
            course = ((yy - ytop) // 5) % 2
            joint = ((yy - ytop) % 5 == 4) or ((xx + 6 * course) % 12 == 0)
            T.px(xx, yy, 0.48 - 0.16 * joint + 0.04 * (((xx * 7 + yy * 3) % 13) == 0) - 0.08 * (yy > BASE - 6))
    for (sx0, sx1, y) in tops:
        for xx in range(sx0, sx1):
            T.px(xx, y, 0.90)
            T.px(xx, y + 1, 0.72)
        edge = sx1 - 1 if up > 0 else sx0
        for yy in range(y + 2, y + rise + 2):
            T.px(edge, yy, 0.24)
    put_tone(L, T, IBBSTONE, dither=0.3)
    return tops


def shopfront(L, x, w, seed=1, open_=True):
    """A shop in a house's ground floor: a blank sign, the shutter up on the shelves inside (or down)."""
    top = BASE - 34
    Sg = Tone(L.w, L.h)
    for yy in range(top, top + 7):
        for xx in range(x, x + w):
            Sg.px(xx, yy, 0.62 + 0.12 * (yy == top) - 0.12 * (yy == top + 6))
    put_tone(L, Sg, SIGNY, dither=0.2)
    D = Tone(L.w, L.h)
    sh = Tone(L.w, L.h)
    for yy in range(top + 8, BASE):
        for xx in range(x + 2, x + w - 2):
            if open_ and yy > top + 11:
                D.px(xx, yy, 0.12 + 0.03 * ((xx + yy) % 4 == 0))
            else:
                rib = (yy - top) % 3
                sh.px(xx, yy, 0.56 + 0.12 * (rib == 0) - 0.10 * (rib == 2))
    put_tone(L, D, SOOT, dither=0)
    put_tone(L, sh, SHUTG, dither=0.3)
    if open_:
        G = np.zeros((SH, L.w, 3), np.uint8)
        Gm = np.zeros((SH, L.w), bool)
        goods = [(200, 48, 32), (232, 196, 60), (60, 120, 180), (236, 232, 220), (80, 160, 80)]
        for sy in (top + 18, top + 26):
            for xx in range(x + 4, x + w - 4):
                Gm[sy, xx] = True
                G[sy, xx] = (96, 72, 48)
                if (xx * 5 + sy) % 7 < 4:
                    for j in range(1, 4):
                        Gm[sy - j, xx] = True
                        G[sy - j, xx] = (np.array(goods[(xx * 3 + sy) % len(goods)]) * 0.7).astype(np.uint8)
        L.rgb[Gm] = G[Gm]
        L.a |= Gm
    return dict(x=wx(x + w // 2), y=WALK)


# ------------------------------------------------------------------ the street
def cobbles(L, x0, x1, seed=7):
    """The old town's street: stone setts in rows, smaller toward the back, wet and shining where they take the sky; a
    stone kerb along the house fronts."""
    w, h = x1 - x0, SH - ROAD_TOP
    T = Tone(L.w, L.h)
    r = rng(seed)
    y = ROAD_TOP
    row = 0
    while y < SH:
        rh = 3 + row // 2
        off = int(r.integers(0, 8))
        x = x0 - off
        while x < x1:
            sw = int(rh * 1.6 + r.integers(0, 4))
            t0 = r.uniform(0.40, 0.62)
            for yy in range(y, min(SH, y + rh)):
                for xx in range(max(x0, x), min(x1, x + sw - 1)):
                    edge = yy == y + rh - 1
                    t = t0 + 0.12 * (yy == y) - 0.14 * edge - 0.05 * (xx == x + sw - 2)
                    T.px(xx, yy, t)
            x += sw
        y += rh
        row += 1
    sheen = noise((SH, L.w), seed + 1, 40, 0.8)
    T.t = np.where(T.m, T.t + 0.12 * np.clip(sheen - 0.5, 0, 1), T.t)
    put_tone(L, T, COBBLE, dither=0.4)
    K = Tone(L.w, L.h)
    for xx in range(x0, x1):
        K.px(xx, ROAD_TOP - 2, 0.74)
        K.px(xx, ROAD_TOP - 1, 0.52)
        K.px(xx, ROAD_TOP, 0.30)
        for yy in range(BASE, ROAD_TOP - 2):
            K.px(xx, yy, 0.50 + 0.06 * ((xx // 9) % 2))
    put_tone(L, K, IBBSTONE, dither=0.2)


# ------------------------------------------------------------------ the school
def school(L, x, seed=41):
    """The school, the Zanabeel's "course" now: its yard open to the street, the building at the back two storeys of
    plastered block washed pale green, three classroom doors in green iron (barred shut), barred windows, a walkway along
    the upper floor with a railing, stairs up to it at its left end, an office door at its right with their flag over it,
    a black tank on the roof; in the yard the flagpole. x is local. -> what the level needs (world coordinates)."""
    r = rng(seed)
    bx0, bx1 = x + 40, x + 360
    gf, up = 46, 40
    top = BASE - gf - up
    # the walls
    T = Tone(L.w, L.h)
    for yy in range(top, BASE):
        for xx in range(bx0, bx1):
            t = 0.70 - 0.08 * ((xx - bx0) > (bx1 - bx0) - 8) + 0.04 * (((xx * 5 + yy * 3) % 17) == 0) - 0.10 * (yy > BASE - 4)
            if yy in (BASE - gf, BASE - gf + 1):
                t = 0.86 if yy == BASE - gf else 0.48
            T.px(xx, yy, t)
    stain = fbm((SH, L.w), seed, 3, 16, octaves=3)
    T.t = np.where(T.m, T.t - 0.14 * np.clip(stain - 0.6, 0, 1) * 3, T.t)
    put_tone(L, T, SCHOOL, dither=0.4)
    STZ.plaster(L, bx0 - 2, top - 5, bx1 + 2, top, LIME, seed=seed + 1, base=0.86, stain=0.3)
    plat('schoolroof', [(wx(bx0 + 2), top - 6), (wx(bx1 - 2), top - 6)])
    SZ.water_tank(L, bx1 - 30, top - 5, seed=seed)
    # the ground floor: three classroom doors, barred windows between
    doors = []
    D = Tone(L.w, L.h)
    Wn = Tone(L.w, L.h)
    Bars = Tone(L.w, L.h)
    for k, dx in enumerate((bx0 + 40, bx0 + 140, bx0 + 240)):
        for yy in range(BASE - 30, BASE):
            for xx in range(dx, dx + 16):
                D.px(xx, yy, 0.50 + 0.12 * ((yy - BASE) % 8 == 0) - 0.14 * (xx == dx + 8) - 0.08 * (xx > dx + 8) + 0.14 * (xx == dx))
        for yy in range(BASE - 22, BASE - 12):                 # a bar across each, padlocked
            pass
        for xx in range(dx - 2, dx + 18):
            D.px(xx, BASE - 18, 0.86)
            D.px(xx, BASE - 17, 0.30)
        D.px(dx + 8, BASE - 16, 0.92); D.px(dx + 8, BASE - 15, 0.92); D.px(dx + 9, BASE - 16, 0.70)
        doors.append(wx(dx + 8))
        for wx0 in (dx + 28, dx + 56):
            for yy in range(BASE - 34, BASE - 16):
                for xx in range(wx0, wx0 + 18):
                    Wn.px(xx, yy, 0.16 + 0.04 * ((xx + yy) % 5 == 0))
            for xx in range(wx0, wx0 + 18, 3):
                for yy in range(BASE - 34, BASE - 16):
                    Bars.px(xx, yy, 0.62)
            for yy in (BASE - 34, BASE - 25, BASE - 17):
                for xx in range(wx0, wx0 + 18):
                    Bars.px(xx, yy, 0.50)
    put_tone(L, D, IRONG, dither=0.2)
    put_tone(L, Wn, SOOT, dither=0)
    put_tone(L, Bars, IRONG, dither=0)
    # the upper floor: barred windows behind the walkway
    Wn2 = Tone(L.w, L.h)
    Bars2 = Tone(L.w, L.h)
    for wx0 in range(bx0 + 20, bx1 - 30, 46):
        for yy in range(top + 8, top + 26):
            for xx in range(wx0, wx0 + 20):
                Wn2.px(xx, yy, 0.16 + 0.04 * ((xx + yy) % 5 == 0))
        for xx in range(wx0, wx0 + 20, 3):
            for yy in range(top + 8, top + 26):
                Bars2.px(xx, yy, 0.62)
    put_tone(L, Wn2, SOOT, dither=0)
    put_tone(L, Bars2, IRONG, dither=0)
    # the walkway along the upper floor: a concrete slab on brackets, an iron railing
    wy = BASE - gf - 1
    Wk = Tone(L.w, L.h)
    for xx in range(bx0 - 4, bx1 + 2):
        Wk.px(xx, wy, 0.84)
        Wk.px(xx, wy + 1, 0.62)
        Wk.px(xx, wy + 2, 0.36)
    for xx in range(bx0 + 10, bx1, 40):
        for j in range(3, 7):
            Wk.px(xx + (j - 3), wy + j, 0.40)
    put_tone(L, Wk, CONCRETE, dither=0)
    Rl = Tone(L.w, L.h)
    for xx in range(bx0 - 2, bx1):
        Rl.px(xx, wy - 12, 0.66)
        if (xx - bx0) % 6 == 0:
            for j in range(1, 12):
                Rl.px(xx, wy - 12 + j, 0.52)
    put_tone(L, Rl, IRONG, dither=0)
    plat('walkway', [(wx(bx0 - 2), wy - 1), (wx(bx1 - 2), wy - 1)])
    # stairs up to it at its left end, climbing to the right
    st = stairs(L, x + 2, 3, rise=12, run=12, seed=seed, up=1)
    for k, (s0, s1, sy) in enumerate(st):
        plat('schoolstep%d' % (k + 1), [(wx(s0), sy - 1), (wx(s1 - 1), sy - 1)])
    # the office door at the right, their flag over it
    ox = bx1 - 22
    O = Tone(L.w, L.h)
    for yy in range(BASE - 30, BASE):
        for xx in range(ox, ox + 14):
            O.px(xx, yy, 0.10 + 0.05 * (xx == ox + 13))
    put_tone(L, O, SOOT, dither=0)
    yy, xx = np.mgrid[0:9, 0:14]
    Fl = np.where((((yy >= 3) & (yy < 6)))[..., None], np.array([232, 192, 56]), np.array([184, 34, 24])).astype(np.uint8)
    Q = Layer(14, 9)
    Q.put((np.round(Fl / 8) * 8).astype(np.uint8), np.ones((9, 14), bool))
    L.paste(Q, ox, BASE - 42)
    # the banner along the walkway: the Spokesman, three times
    for k in range(3):
        Z1.poster(L, bx0 + 70 + k * 92, top + 6, 'face', seed=seed + 20 + k)
    # in the yard: the flagpole, a whitewashed foot; the yard's floor is the street's
    fp = x + 196
    Fp = Tone(L.w, L.h)
    for yy in range(BASE - 104, WALK + 2):
        Fp.px(fp, yy, 0.86); Fp.px(fp + 1, yy, 0.62)
    for yy in range(WALK - 6, WALK + 3):
        for xx in range(fp - 6, fp + 8):
            Fp.px(xx, yy, 0.80 - 0.18 * (xx > fp + 3) + 0.10 * (yy == WALK - 6))
    put_tone(L, Fp, LIME, dither=0)
    Fq = np.zeros((10, 16, 3))
    yy, xx = np.mgrid[0:10, 0:16]
    wave = np.round(np.sin(xx / 3.0)).astype(int)
    Fq[:] = (184, 34, 24)
    Fq[((yy - wave) >= 4) & ((yy - wave) < 7)] = (232, 192, 56)
    Q = Layer(16, 10)
    Q.put((np.round(Fq / 8) * 8).astype(np.uint8), (yy - wave >= 0) & (yy - wave < 10))
    L.paste(Q, fp + 2, BASE - 104)
    return dict(doors=doors, office=dict(x=wx(ox + 7), y=WALK), flagpole=wx(fp), x0=wx(x), x1=wx(bx1), walkway=wy - 1)


def gatepost(L, x, h=44, seed=1):
    """A stone gatepost of the school's yard, a white cap on it."""
    T = Tone(L.w, L.h)
    for yy in range(BASE - h, BASE):
        for xx in range(x, x + 10):
            T.px(xx, yy, 0.52 - 0.16 * (xx > x + 6) + 0.05 * (((xx + yy * 2) % 7) == 0) - 0.10 * (yy % 6 == 0))
    put_tone(L, T, IBBSTONE, dither=0.3)
    C = Tone(L.w, L.h)
    for xx in range(x - 1, x + 11):
        C.px(xx, BASE - h - 1, 0.94); C.px(xx, BASE - h, 0.80); C.px(xx, BASE - h + 1, 0.62)
    put_tone(L, C, LIME, dither=0)


# ------------------------------------------------------------------ the town up the mountainside, and the mosque
HAZE_T = np.array([196, 208, 214], dtype=float)


def back_town(w=1150, seed=61):
    """Jibla climbing the mountain behind the street (the `back` layer, moving at 0.7 of the street's pace): the green
    slope rising to the right, terraced, with the town's houses in rows along it (smaller and paler the higher they
    stand), trees between, and the Queen Arwa mosque among them with its two ribbed minarets and two white domes. Its
    left end is the town's edge, so it first shows as the street reaches the town. -> the picture (at BACK_X)."""
    h = SH
    L = Layer(w, h)
    r = rng(seed)
    yy, xx = np.mgrid[0:h, 0:w]
    xs = np.arange(w)
    crest = 168 - 112 * np.clip(xs / 520.0, 0, 1) ** 0.8 + 8 * (noise((1, w), seed, 40, 0.5)[0] - 0.5)
    crest = np.where(xs > 900, crest + (xs - 900) * 0.08, crest)
    m = yy >= crest[None, :]
    per = 6.0
    E = yy - 0.35 * (crest[None, :] - crest.mean())
    frac = (E / per) - np.floor(E / per)
    t = 0.52 + 0.08 * (noise((h, w), seed + 1, 18, 3) - 0.5) - 0.14 * (frac > 0.72) + 0.06 * (frac < 0.2)
    L.put(toned(np.clip(t, 0, 1), I.TERR, dither=0.5), m)
    # trees on the slope
    Tt = Tone(w, h)
    for i in range(int(w / 9)):
        cx = int(r.integers(0, w))
        cy = int(crest[cx] + r.integers(6, 60))
        if cy < h - 4:
            I.tree_tone(Tt, cx, cy, r.uniform(2.0, 4.0), int(r.integers(0, 1000)))
    L.paste(Tt.layer(I.LEAF, dither=0.5))
    # the houses, row by row along the slope: the highest first; clusters with gaps between
    rows = [(16, 0.6, 0.26), (52, 0.72, 0.14), (94, 0.86, 0.06)]
    for ri, (below, sc, haze) in enumerate(rows):
        x = int(r.integers(0, 20))
        while x < w:
            if r.random() < 0.34:                      # a gap: terraces and trees
                x += int(r.integers(24, 64))
                continue
            hw = int((26 + r.integers(0, 18)) * sc)
            hh = int((44 + r.integers(0, 36)) * sc)
            base = int(crest[min(w - 1, x + hw // 2)] + below)
            in_mosque = 680 < x + hw // 2 < 860 and ri >= 1
            if base < h - 20 and not in_mosque:
                small_house(L, x, base, hw, hh, seed + ri * 100 + x, haze=haze)
            x += hw + int(r.integers(1, 8))
    mosque(L, 720, 140)
    return L


def small_house(L, x, base, w, h, seed, haze=0.3):
    """A tower house up the slope, small with distance: dark stone, the right side in shade, a white band between the
    floors, rows of windows framed in white (some with a white arch over them), a toothed white parapet; hazed a little
    toward the sky the higher it stands."""
    r = rng(seed)
    T = Tone(L.w, L.h)
    top = base - h
    side = max(2, w // 4)
    for y in range(top, base):
        for i in range(w):
            T.px(x + i, y, (0.30 if i < w - side else 0.18) + 0.06 * (((i * 3 + y * 5) % 11) == 0) - 0.05 * (y > base - 6))
    put_tone(L, T, IBBSTONE, dither=0.3)
    W = Tone(L.w, L.h)
    for i in range(w):
        W.px(x + i, top, 0.96 if i < w - side else 0.78)
        W.px(x + i, top + 1, 0.84 if i < w - side else 0.66)
        if i % 3 == 0:
            W.px(x + i, top - 1, 0.94 if i < w - side else 0.76)
    fh = 9
    fl = max(1, (h - 6) // fh)
    D = Tone(L.w, L.h)
    for f in range(fl):
        yb = top + 5 + f * fh
        if f > 0:
            for i in range(w - side):
                W.px(x + i, yb - 3, 0.84)
        for i in range(2, w - side - 2, 5):
            W.px(x + i, yb - 1, 0.96); W.px(x + i + 1, yb - 1, 0.96)          # the white arch over it
            for j in range(3):
                D.px(x + i, yb + j, 0.06); D.px(x + i + 1, yb + j, 0.06)
            W.px(x + i - 1, yb + 3, 0.80); W.px(x + i, yb + 3, 0.90); W.px(x + i + 1, yb + 3, 0.90); W.px(x + i + 2, yb + 3, 0.80)
    put_tone(L, W, LIME, dither=0)
    put_tone(L, D, SOOT, dither=0)
    if haze > 0:
        box = (slice(max(0, top - 2), base), slice(max(0, x), min(L.w, x + w)))
        sub = L.rgb[box].astype(float)
        L.rgb[box] = np.clip(sub * (1 - haze) + HAZE_T * haze, 0, 255).astype(np.uint8)


def mosque(L, x, base):
    """The Queen Arwa mosque as it shows over the roofs: its prayer hall with a white dome over each end, an arcade along
    its front, and its two minarets, the eastern on a high square stone base with a ribbed shaft, a white gallery and a
    white cap on each."""
    T = Tone(L.w, L.h)
    hw, hh = 110, 26
    for y in range(base - hh, base):
        for i in range(hw):
            T.px(x + i, y, 0.62 - 0.14 * (i > hw - 14) + 0.04 * (((i * 3 + y * 7) % 13) == 0))
    for k in range(9):                                   # the arcade: pointed arches, dark within
        ax = x + 8 + k * 11
        for j in range(12):
            for i in range(6):
                if j < 3 and abs(i - 2.5) > j + 0.5:
                    continue
                T.px(ax + i, base - 14 + j, 0.14)
    put_tone(L, T, IBBSTONE, dither=0.3)
    W = Tone(L.w, L.h)
    for i in range(-2, hw + 2):
        W.px(x + i, base - hh - 1, 0.94)
        W.px(x + i, base - hh, 0.82)
    for cx in (x + 26, x + 84):                          # the domes: white, lit on the left
        for j in range(-14, 0):
            for i in range(-14, 15):
                if (i / 14.0) ** 2 + (j / 13.0) ** 2 <= 1:
                    W.px(cx + i, base - hh - 1 + j, 0.98 - 0.22 * (i > 3) + 0.04 * (j < -9))
        W.px(cx, base - hh - 15, 0.70); W.px(cx, base - hh - 16, 0.70); W.px(cx, base - hh - 17, 0.92)
    put_tone(L, W, LIME, dither=0.2)
    for k, (mx, h0) in enumerate(((x - 14, 22), (x + hw + 2, 16))):
        M = Tone(L.w, L.h)
        sb = 14 if k == 0 else 12
        for y in range(base - h0, base):                 # the square stone base
            for i in range(sb):
                M.px(mx + i, y, 0.60 - 0.16 * (i > sb - 4) + 0.05 * ((y % 5) == 0))
        sh_top = base - h0 - 52
        for y in range(sh_top, base - h0):              # the ribbed shaft
            for i in range(2, sb - 2):
                rib = (i % 2 == 0)
                M.px(mx + i, y, 0.70 + 0.10 * rib - 0.16 * (i > sb - 5))
        put_tone(L, M, IBBSTONE, dither=0.2)
        G = Tone(L.w, L.h)
        for i in range(0, sb):                           # the gallery and the cap
            G.px(mx + i, sh_top - 1, 0.96); G.px(mx + i, sh_top, 0.80)
        for j in range(8):
            for i in range(3, sb - 3):
                G.px(mx + i, sh_top - 2 - j, 0.94 - 0.20 * (i > sb // 2))
        for j in range(5):
            w_ = max(1, (sb - 6) // 2 - j // 2)
            for i in range(-w_, w_ + 1):
                G.px(mx + sb // 2 + i, sh_top - 10 - j, 0.96 - 0.2 * (i > 0))
        G.px(mx + sb // 2, sh_top - 16, 0.80); G.px(mx + sb // 2, sh_top - 17, 0.92)
        put_tone(L, G, LIME, dither=0)
    box = (slice(0, base + 1), slice(max(0, x - 20), min(L.w, x + hw + 20)))
    sub = L.rgb[box].astype(float)
    L.rgb[box] = np.clip(sub * 0.82 + HAZE_T * 0.18, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ zone 2, put together
BACK_X = 960                     # where the back layer's picture starts, in the layer (0.7 of the street's pace)


def play_z2(seed=201):
    """Jibla's street, world 1280 to 2640 (the picture's x is world - 1280)."""
    L = Layer(W2, SH)
    info = {}
    r = rng(seed)
    # (0) the road comes in: the last of the valley's wall and crops, the asphalt turning to cobbles
    Z1.crops(L, 0, 60, Z1.VERGE - 12, seed=seed)
    Z1.drystone(L, 0, 58, 146, Z1.VERGE + 2, seed=seed + 1)
    Z1.verge(L, 0, 60, seed=seed + 2)
    # (1) the street's houses, back to front: left to right
    houses = []
    tH1, dH1 = house(L, 56, 84, 84, seed + 10, floors=1, door=False)
    info['shop1'] = shopfront(L, 66, 50, seed=seed + 11)
    plat('h1roof', [(wx(57), tH1 - 1), (wx(56 + 83), tH1 - 1)])
    st = stairs(L, 142, 4, rise=14, run=12, seed=seed + 12, up=1)
    for k, (s0, s1, sy) in enumerate(st):
        plat('alleyA%d' % (k + 1), [(wx(s0), sy - 1), (wx(s1 - 1), sy - 1)])
    tH2, dH2 = house(L, 196, 92, 84, seed + 13, floors=1, door=False, roof=('tank',))
    plat('h2roof', [(wx(197), tH2 - 1), (wx(196 + 91), tH2 - 1)])
    tH3, dH3 = house(L, 288, 82, 124, seed + 14, floors=2, door=True, roof=('dish',))
    info['h3door'] = dict(x=wx(dH3), y=WALK) if dH3 is not None else None
    # (2) the school: its gateposts, its yard open to the street, the building behind
    gatepost(L, 372, seed=seed + 20)
    info['school'] = school(L, 386, seed=seed + 21)
    gatepost(L, 752, seed=seed + 22)
    # (3) the upper street: two houses with an alley between, the gap over a low wall where the mosque shows, a last
    #     house with a shop, the way out
    tH4, dH4 = house(L, 770, 90, 84, seed + 30, floors=1, door=True, roof=('tank',))
    plat('h4roof', [(wx(771), tH4 - 1), (wx(770 + 89), tH4 - 1)])
    info['h4door'] = dict(x=wx(dH4), y=WALK) if dH4 is not None else None
    st2 = stairs(L, 916, 4, rise=14, run=12, seed=seed + 31, up=-1)
    for k, (s0, s1, sy) in enumerate(st2):
        plat('alleyB%d' % (k + 1), [(wx(s0), sy - 1), (wx(s1 - 1), sy - 1)])
    tH5, dH5 = house(L, 916, 84, 124, seed + 32, floors=2, door=True)
    info['h5door'] = dict(x=wx(dH5), y=WALK) if dH5 is not None else None
    # the gap: a low wall with the town's roofs and the mosque over it (the back layer shows through above)
    Z1.drystone(L, 1000, 1110, 150, BASE + 1, seed=seed + 33)
    plat('lowwall', [(wx(1004), 149), (wx(1106), 149)])
    tH6, dH6 = house(L, 1110, 96, 84, seed + 34, floors=1, door=False, roof=('tank',))
    info['shop2'] = shopfront(L, 1120, 56, seed=seed + 35)
    plat('h6roof', [(wx(1111), tH6 - 1), (wx(1110 + 95), tH6 - 1)])
    # the way out: a stone path between terraces, up toward the waterfall (zone 3)
    Z1.drystone(L, 1206, W2, 140, BASE + 1, seed=seed + 36)
    Z1.crops(L, 1210, W2, 140, seed=seed + 37, hmin=10, hmax=18)
    # posters of him on the walls
    info['posters'] = [Z1.poster(L, 300, BASE - 46, 'face', seed=seed + 40), Z1.poster(L, 1012, 151, 'badge', seed=seed + 41),
                       Z1.poster(L, 790, BASE - 48, 'face', seed=seed + 42)]
    # (4) the street: the asphalt's last metres, then cobbles; the kerb along the house fronts
    Z1.road(L, 0, 64, seed=seed + 50)
    cobbles(L, 60, W2, seed=seed + 51)
    for k, (px_, py_, pw, ph_) in enumerate(((240, 202, 36, 4), (640, 194, 24, 3), (1000, 206, 44, 5))):
        Z1.puddle(L, px_, py_, pw, ph_, seed=seed + 60 + k)
    I.INFO['z2'] = info
    return L


def fore_z2(w=1720, seed=231):
    """Close to the lens in the town: the odd stone, a tuft of grass at a kerb."""
    return Z1.fore_z1(w=w, seed=seed)


if __name__ == '__main__':
    import time
    t0 = time.time()
    I.PLATS.clear()
    L = play_z2()
    B = back_town()
    print('painted in %.1f s' % (time.time() - t0))
    print(sorted((k, v) for k, v in I.PLATS.items()))
    print(I.INFO.get('z2'))
