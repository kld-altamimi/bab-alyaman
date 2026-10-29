# stage_ibb_z3.py - Ibb's zone 3, the terraces (Khaled, 29 Oct 20:11: "Looks great": Jibla done, on to the terraces). The
# brief: "the climb beside the waterfall to the relay station on the mountain, where the Zanabeel have built a stage:
# podium, backdrop, a live Zanabeel audience." Ibb's mountainsides are terraced to their tops (dry-stone walls holding
# narrow fields of sorghum), and in the rains the streams come down them in falls.
# Left to right: the path out of Jibla turns to earth and starts up the terraces, a step of field wall at a time (each
# step a wall to hop up: the level's ground climbs, walls: true); a field hut; a stream off the falls crossed on a slab
# bridge; a boulder; the falls themselves up the mountainside behind (a layer of their own, `back`, at 0.7); a stone
# farmhouse on the last terrace; then, on the top, the Zanabeel's relay station (its fence and gate, an equipment cabin,
# a generator, the lattice mast with its dishes) and their stage: a deck, a frame hung with the blue curtain, their
# emblem over it and their flag beside it, lights on stands, a camera on its tripod, rows of plastic chairs.
# The podium stands on the deck as a sprite (render_ibb.js), so the scene can put the Spokesman behind it.
# Platforms, the ground's height along the zone and what else the level needs are recorded in world coordinates
# (I.PLATS, I.INFO['z3'], GROUND_STEPS).
import numpy as np
from scipy import ndimage as ndi
from paint import *
import stage_mocha as SM
import stage_taiz as STZ
import stage_ibb as I
import stage_ibb_z1 as Z1
import stage_ibb_z2 as Z2

SH = I.SH
X0 = Z2.END2                    # zone 3 starts where Jibla's picture ends (2640)
W3 = 2120                       # (1440 until 29 Oct: then the path running on 160 past the stage toward the pass, and
                                # the hamlet on the top terrace before the station, 520)
STATION = 520                   # how far the relay station and the stage moved on for the hamlet
END3 = X0 + W3                  # 6200
put_tone, plat = SM.put_tone, I.plat
IBBSTONE, CONCRETE, PLASTIC, BLUEP, REDP, GOLD, GRASS = Z1.IBBSTONE, Z1.CONCRETE, Z1.PLASTIC, Z1.BLUEP, Z1.REDP, Z1.GOLD, Z1.GRASS
DRYST, LEAF, TERR, FALLOW, MUDI, WATER = I.DRYST, I.LEAF, I.TERR, I.FALLOW, I.MUDI, I.WATER
LIME, TEAK, SOOT = SM.LIME, SM.TEAK, SM.SOOT
EARTH = ramp(['#1a120a', '#2e2216', '#443422', '#5a4630', '#705a40', '#886e52', '#a08668', '#b89e80'], 16)       # the path's wet earth
FOAM = ramp(['#3e5a62', '#5e7e86', '#82a2a8', '#a6c2c4', '#c8dcdc', '#e4f0ee', '#f8fcfa'], 12)                 # falling water
STEEL = ramp(['#16181c', '#2a2e34', '#40464e', '#5a626a', '#768088', '#949ea6', '#b4bcc2', '#d2d8dc'], 14)       # galvanised steel
PANEL = ramp(['#2c2a26', '#4a4740', '#6c6860', '#8e8a80', '#b0aca0', '#cecabe', '#e6e2d8', '#f6f4ec'], 14)       # the cabin's panels
CURTAIN = ramp(['#06102a', '#0c1c44', '#14295e', '#1e3a7c', '#2c4e98', '#3e64b0', '#5a80c6', '#7c9ed8'], 14)     # the stage's blue curtain
CLOTH = ramp(['#0a0a0c', '#141418', '#1e1e24', '#2a2a32', '#383842'], 8)                                        # black stage cloth
YELLOWG = ramp(['#2a2004', '#4e3c08', '#76600e', '#9e8418', '#c4a826', '#e0c840', '#f2e270'], 12)                # the generator's paint

# ------------------------------------------------------------------ the ground: the path climbs a terrace at a time
# (local x where each level starts, and its walk line). Each step up is 16 px: a wall to hop up (STEP_UP is 7).
STEPS = [(0, 184), (132, 168), (332, 152), (620, 136), (900, 120)]
LEVELS = [y for _, y in STEPS]


def wx(lx):
    return int(lx + X0)


def gy(lx):
    """The walk line at local x."""
    y = STEPS[0][1]
    for x0, yy in STEPS:
        if lx >= x0:
            y = yy
    return y


def ground_world(x):
    """The walk line at world x, for the level's ground (flat at 184 before zone 3)."""
    return gy(x - X0) if x >= X0 else I.WALK


# ------------------------------------------------------------------ the hillside behind the path
def hillside(L, seed=301):
    """Behind the path, the terraces climbing away from it: from the path's back edge up, the field of the path's own
    terrace (sorghum standing at its front), then the next terrace's dry-stone wall and its field; the bands step up with
    the path, the one behind a little ahead of it (the walls run up the hill at a slant). Where it ends, the mountainside
    and its falls (the back layer) show above. -> the crest, column by column."""
    w = L.w
    back = np.array([gy(x) for x in range(w)]) - 8                       # the path's back edge
    w1 = np.array([gy(min(w - 1, x + 44)) for x in range(w)]) - 8 - 34   # the next terrace's wall top
    WH = 10
    crest = w1 - 14
    F = Tone(w, SH)
    W = Tone(w, SH)
    fn = noise((SH, w), seed, 1.6, 0.8)
    st = noise((SH, w), seed + 1, 1.2, 0.9)
    for x in range(w):
        # the path's terrace: its field, from the next wall's foot down to the path
        y0, y1 = w1[x] + WH, back[x]
        for y in range(y0, y1):
            v = (y - y0) / max(1.0, y1 - y0)
            row = ((y - y0) % 4 == 3)
            F.px(x, y, 0.40 + 0.12 * (fn[y, x] - 0.5) - 0.10 * row + 0.08 * (v < 0.25) - 0.08 * (v > 0.8))
        # the next terrace's wall
        for y in range(w1[x], w1[x] + WH):
            d = y - w1[x]
            joint = (d % 4 == 3) or (((x + 5 * (d // 4)) % 9) == 0)
            W.px(x, y, 0.44 - 0.14 * joint + 0.10 * (st[y, x] - 0.5) + 0.10 * (d == 0))
        # its field, up to the crest: paler, hazier
        for y in range(crest[x], w1[x]):
            v = (y - crest[x]) / 14.0
            F.px(x, y, 0.52 + 0.10 * (fn[y, x] - 0.5) - 0.08 * ((y - crest[x]) % 4 == 3) + 0.06 * (v < 0.3))
    put_tone(L, F, TERR, dither=0.45)
    put_tone(L, W, DRYST, dither=0.35)
    # sorghum standing at the front of each field
    for seg0, seg1 in segments(back):
        Z1.crops(L, seg0, seg1, int(back[seg0]), seed=seed + 10 + seg0, hmin=12, hmax=20)
    for seg0, seg1 in segments(w1):
        Z1.crops(L, seg0, seg1, int(w1[seg0]), seed=seed + 30 + seg0, hmin=6, hmax=11, gap=2.6)
    return crest


def segments(lvl):
    """Runs of equal height in a profile: [(x0, x1)]."""
    out = []
    x0 = 0
    for x in range(1, len(lvl) + 1):
        if x == len(lvl) or lvl[x] != lvl[x0]:
            out.append((x0, x))
            x0 = x
    return out


# ------------------------------------------------------------------ the path and the drop in front of it
def path(L, x0, x1, seed=311):
    """The path along the terrace's front: wet earth worn into the grass, stones in it, its near edge the top of the
    terrace wall; where it climbs, the end of the wall above, faced with dressed stones."""
    w = x1 - x0
    T = Tone(L.w, SH)
    G = Tone(L.w, SH)
    g = noise((SH, L.w), seed, 0.7, 0.7)
    mud = fbm((SH, L.w), seed + 1, 10, 2.5, octaves=3)
    for x in range(x0, x1):
        y0 = gy(x) - 7
        for y in range(y0, gy(x) + 3):
            v = (y - y0) / 9.0
            t = 0.44 + 0.10 * (g[y, x] - 0.5) - 0.12 * (y == y0) + 0.06 * (v > 0.5) + 0.10 * (mud[y, x] > 0.62) - 0.10 * (y >= gy(x) + 2)
            if g[y, x] > 0.80:
                t += 0.16                                   # a stone in the path
            T.px(x, y, t)
        # grass along the back edge and the front edge
        if hash_(x, seed) < 0.45:
            n = int(1 + 3 * hash_(x, seed + 1))
            for j in range(n):
                G.px(x, gy(x) - 8 - j, 0.44 + 0.08 * j)
        if hash_(x, seed + 2) < 0.30:
            G.px(x, gy(x) + 2, 0.56)
    put_tone(L, T, EARTH, dither=0.4)
    put_tone(L, G, GRASS, dither=0.3)


def drop(L, seed=321):
    """In front of the path the hillside falls away toward us a terrace at a time: the wall under the path, a field below
    it seen from above (rows of sorghum, their heads), the next wall, the next field, to the bottom of the picture; the
    walls' tops wander a little along the hill, a tree's crown rises out of a field here and there. -> the bands, each
    (kind, top, bottom) with top and bottom column by column (the stream comes down through them)."""
    w = L.w
    bands = []
    top = np.array([gy(x) + 3 for x in range(w)], dtype=float)
    k = 0
    while top.min() < SH:
        n1 = noise((1, w), seed + 7 * k, 110, 0.5)[0] - 0.5
        n2 = noise((1, w), seed + 7 * k + 3, 80, 0.5)[0] - 0.5
        wh = (19 if k == 0 else 23 + 2 * k) + 8 * n1
        bot = top + wh
        bands.append(('wall', np.round(top).astype(int), np.round(bot).astype(int)))
        fh = 11 + 2 * k + 6 * n2
        bands.append(('field', np.round(bot).astype(int), np.round(bot + fh).astype(int)))
        top = bot + fh
        k += 1
    T = Tone(w, SH)
    F = Tone(w, SH)
    Hd = Tone(w, SH)
    Fw = Tone(w, SH)                                     # (the fallow ones: ploughed earth)
    for i, (kind, t0, t1) in enumerate(bands):
        if kind == 'wall':
            stonewall(T, 0, w, t0, t1, seed + 11 * i, t_=0.44 - 0.02 * i)
        else:
            # stretches of this terrace's field: mostly green, now and then left fallow
            x = 0
            rr = rng(seed + 13 * i)
            while x < w:
                ln = int(rr.integers(90, 260))
                tgt = Fw if rr.random() < 0.22 else F
                field_rows(tgt, Hd if tgt is F else Tone(w, SH), x, min(w, x + ln), t0, t1, seed + 11 * i)
                x += ln
    put_tone(L, T, DRYST, dither=0.35)
    put_tone(L, F, TERR, dither=0.45)
    put_tone(L, Fw, FALLOW, dither=0.45)
    put_tone(L, Hd, GRASS, dither=0.2)
    # grass along each wall's top, and a tree's crown rising out of a field here and there
    G = Tone(w, SH)
    for kind, t0, t1 in bands:
        if kind != 'wall':
            continue
        for x in range(w):
            if hash_(x, seed + int(t0[x])) < 0.30:
                n = int(1 + 3 * hash_(x, seed + 5))
                for j in range(n):
                    G.px(x, t0[x] - j, 0.46 + 0.08 * j)
    put_tone(L, G, GRASS, dither=0.3)
    r = rng(seed + 99)
    Tt = Tone(w, SH)
    for i in range(int(w / 120)):
        cx = int(r.integers(0, w))
        fb = [b for b in bands if b[0] == 'field' and b[1][cx] < SH - 6 and b[1][cx] > gy(cx) + 20]
        if not fb:
            continue
        b = fb[int(r.integers(0, len(fb)))]
        I.tree_tone(Tt, cx, int(b[1][cx]) - 2, r.uniform(6, 10), int(r.integers(0, 1000)), dark=0.06)
    put_tone(L, Tt, LEAF, dither=0.5)
    return bands


def stonewall(T, x0, x1, top, bot, seed, t_=0.46):
    """A dry-stone wall face between two lines (column by column): courses of rough stones following its top, each stone
    lit along its top and left edge, dark in the joints, each a little lighter or darker than the next."""
    r = rng(seed)
    nrows = int(max(bot[x0:x1] - top[x0:x1])) // 3 + 2
    rows = []
    for k in range(nrows):
        rh = int(r.integers(3, 6))
        stones = []
        x = x0 - int(r.integers(0, 9))
        while x < x1:
            sw = int(r.integers(5, 13))
            stones.append((x, x + sw, r.uniform(-0.12, 0.12)))
            x += sw
        rows.append((rh, stones))
    for x in range(x0, x1):
        y = int(top[x])
        for rh, stones in rows:
            if y >= bot[x]:
                break
            st = stones[0]
            for q in stones:
                if q[0] <= x < q[1]:
                    st = q
                    break
            for yy in range(y, min(int(bot[x]), y + rh)):
                e = yy - y
                joint = (e == rh - 1) or (x == st[1] - 1)
                lit = (e == 0) or (x == st[0])
                T.px(x, yy, t_ + st[2] + 0.12 * lit - 0.26 * joint - 0.06 * (yy > bot[x] - 3))
            y += rh


def field_rows(F, Hd, x0, x1, top, bot, seed):
    """A terrace's field seen from above, between two lines: rows of sorghum running along the terrace, lit along their
    tops, the heads catching the light here and there, darker toward its front edge where it drops."""
    for x in range(x0, x1):
        h = max(1, bot[x] - top[x])
        for y in range(int(top[x]), int(bot[x])):
            d = y - top[x]
            v = d / float(h)
            n = noise_at(x // 2, y, seed)
            row = (d + (x // 11) % 2) % 3
            t = 0.34 + 0.16 * (n - 0.5) + 0.10 * (row == 0) - 0.06 * (row == 2) + 0.06 * (v < 0.2) - 0.12 * (v > 0.82)
            F.px(x, y, t)
            if n > 0.93 and row == 0:
                Hd.px(x, y, 0.62)


def noise_at(x, y, seed):
    return float(I.hash01(int(x) * 3 + int(y) * 7, int(seed)))


def hash_(a, b):
    return float(I.hash01(int(a), int(b)))


def risers(L, seed=331):
    """Where the path steps up: the end of the upper terrace, faced with dressed stones, its corner lit, its shadow on the
    path below (the wall the player meets: the ground's 16 px rise sits over the last 4 px before the step)."""
    T = Tone(L.w, SH)
    S = Tone(L.w, SH)
    for k in range(1, len(STEPS)):
        x, ylo, yhi = STEPS[k][0], STEPS[k - 1][1], STEPS[k][1]
        for xx in range(x - 5, x):
            for y in range(yhi - 8, ylo + 3):
                d = y - (yhi - 8)
                course = d // 5
                joint = (d % 5 == 4) or (xx == x - 5 + (2 if course % 2 else 4) and d % 5 != 4 and False)
                lit = 0.20 if xx == x - 5 else (0.08 if xx == x - 4 else -0.05 * (xx - (x - 4)))
                T.px(xx, y, 0.56 + lit - 0.18 * joint + 0.10 * (y == yhi - 8))
        for xx in range(x - 9, x - 5):
            for y in range(ylo - 7, ylo + 2):
                S.px(xx, y, 0.18 + 0.04 * (xx - (x - 9)))
    put_tone(L, S, EARTH, dither=0.3)
    put_tone(L, T, IBBSTONE, dither=0.25)


# ------------------------------------------------------------------ the stream off the falls, and its bridge
def stream(L, x0, x1, bands, seed=341):
    """The stream out of the falls' pool: under the path through a culvert, a stone slab laid across it for the path, then
    white over each wall in front and along each field below in a stone-lined channel, to the bottom of the picture;
    foam where each fall lands."""
    W = Tone(L.w, SH)      # water lying in the channel
    Fo = Tone(L.w, SH)     # white water falling, and the foam where it lands
    K = Tone(L.w, SH)      # the channel's stones
    rip = noise((SH, L.w), seed, 4.0, 0.7)
    fall = noise((SH, L.w), seed + 1, 0.55, 5.0)
    jag = noise((SH, L.w), seed + 2, 0.9, 1.4)
    yb = gy(x0)
    cx = (x0 + x1) / 2.0
    hw0 = (x1 - x0) / 2.0
    foots = []
    for bi, (kind, t0, t1) in enumerate(bands):
        kind = 'fall' if kind == 'wall' else 'chan'
        half = hw0 + 0.6 * bi
        cx = (x0 + x1) / 2.0 + (2, -1, 3, 0, -2, 1, 2)[bi % 7]
        for x in range(int(cx - half - 4), int(cx + half + 4)):
            y0, y1 = int(t0[x]), min(SH, int(t1[x]))
            for y in range(y0, y1):
                h = half + 1.2 * (jag[y, x] - 0.5) * (2 if kind == 'fall' else 1)
                e = abs(x - cx + 0.5) / h
                if e > 1.0:
                    if kind == 'chan' and e < 1.0 + 3.0 / h:
                        K.px(x, y, 0.30 + 0.14 * (noise_at(x, y // 2, seed) - 0.5) + 0.10 * (y == y0))
                    continue
                if kind == 'fall':
                    Fo.px(x, y, 0.80 + 0.22 * (fall[y, x] - 0.5) - 0.18 * e ** 3 - 0.10 * (y - y0 < 2))
                else:
                    W.px(x, y, 0.34 + 0.26 * max(0, rip[y, x] - 0.45) + 0.06 * (1 - e) - 0.10 * (y - y0 < 1))
        if kind == 'fall':
            foots.append((int(t1[int(cx)]), half, cx))
    put_tone(L, K, DRYST, dither=0.3)
    put_tone(L, W, WATER, dither=0.4)
    r = rng(seed + 3)
    for fy, half, cx in foots:
        for i in range(int(40 * half / 8)):
            a = r.uniform(0, np.pi)
            d = r.uniform(0, 1) ** 0.6
            Fo.px(int(cx + np.cos(a) * d * (half + 6)), int(fy + 1 - np.sin(a) * d * 3), 0.84 + 0.12 * r.random())
    put_tone(L, Fo, FOAM, dither=0.35)
    # the slab over it, and the culvert's dark mouth under the slab's front edge
    S = Tone(L.w, SH)
    for x in range(x0 - 6, x1 + 6):
        for y in range(yb - 7, yb + 1):
            S.px(x, y, 0.58 + 0.16 * (y == yb - 7) - 0.12 * (y == yb) + 0.05 * ((x * 3 + y) % 7 == 0) - 0.08 * (x in (x0 - 6, x1 + 5)))
    put_tone(L, S, IBBSTONE, dither=0.25)
    D = Tone(L.w, SH)
    for x in range(x0 - 1, x1 + 1):
        for y in range(yb + 1, yb + 5):
            D.px(x, y, 0.04 + 0.03 * (y == yb + 4))
    put_tone(L, D, SOOT, dither=0)


# ------------------------------------------------------------------ things on the terraces
def falls(L, fx, seed=345):
    """The falls the path climbs beside: a buttress of dark rock rising out of the terraces behind the path and out of
    the top of the picture, ragged where the green slope meets it, faceted, wet and darker by the water, green on its
    ledges; down a cleft in it the water, coming over from above in a white ribbon, broken on a ledge, into a pool at the
    path's back edge, foam where it lands. -> the pool's extent."""
    back = gy(fx) - 8
    x0, x1 = fx - 130, fx + 120
    w = x1 - x0
    yy, xx = np.mgrid[0:SH, 0:w]
    ax = (xx + x0 - fx).astype(float)
    core = np.where(ax < 0, 66.0, 58.0) + 12 * (noise((SH, w), seed + 7, 30, 12) - 0.5)
    jag = noise((SH, w), seed, 3, 6) - 0.5
    top = -12 + 150 * np.clip((np.abs(ax) - core) / 52.0, 0, 1) ** 1.3 + 12 * jag
    rock = (yy >= top) & (yy < back + 1)
    # strata: ledges running across it, a little tilted, lit along their tops
    strata = ((yy + 0.12 * ax + 6 * (noise((SH, w), seed + 8, 20, 4) - 0.5)) % 23.0)
    Hh = fbm((SH, w), seed + 1, 6, 8, octaves=4) * 30 + 0.25 * yy
    lit = light(ndi.gaussian_filter(Hh, 0.8), -0.7, -0.5, 0.42)
    wet = np.clip(1 - np.abs(ax) / 22.0, 0, 1)
    t = 0.42 + 0.20 * np.clip(lit, -1, 1) + 0.06 * (noise((SH, w), seed + 2, 1.2, 1.2) - 0.5) - 0.16 * wet \
        + 0.10 * (yy < top + 2) - 0.10 * (yy > back - 6) + 0.12 * (strata < 1.5) - 0.08 * ((strata > 1.5) & (strata < 4))
    Z1.piece_put(L, t[:back + 1], rock[:back + 1], STZ.BASALT, x0, 0, dither=0.4)
    r = rng(seed + 3)
    Tt = Tone(L.w, SH)
    for i in range(90):                                          # green on its ledges
        gx = int(r.uniform(x0 + 6, x1 - 6))
        if abs(gx - fx) < 13:
            continue
        col = np.where(rock[:, gx - x0] & (strata[:, gx - x0] < 2.5))[0]
        if not len(col):
            continue
        gy_ = int(col[int(r.integers(0, len(col)))])
        if gy_ > back - 4:
            continue
        I.tree_tone(Tt, gx, gy_ - 1, r.uniform(1.4, 3.4), int(r.integers(0, 1000)), dark=0.10)
    put_tone(L, Tt, LEAF, dither=0.5)
    # the water: over from above, broken on a ledge, a little wider as it falls; streaked, its edges ragged
    F = Tone(L.w, SH)
    f = noise((SH, L.w), seed + 4, 0.5, 7.0)
    ej = noise((SH, L.w), seed + 5, 0.8, 1.6)
    ledge = int(back * 0.46)
    for y in range(0, back - 3):
        upper = y < ledge
        hw = 4.0 + y * 0.015 if upper else 6.0 + (y - ledge) * 0.06
        cxw = fx + (0 if upper else 2) + 1.2 * np.sin(y / 13.0)
        for x in range(int(cxw - hw - 2), int(cxw + hw) + 3):
            e = abs(x - cxw) / max(1.0, hw + 1.6 * (ej[y, x] - 0.5))
            if e > 1.0:
                continue
            F.px(x, y, 0.80 + 0.22 * (f[y, x] - 0.5) - 0.24 * max(0, e - 0.5) - 0.06 * (y % 9 == 0 and e > 0.6))
    for i in range(70):                                         # the ledge, the water breaking white on it
        a_ = r.uniform(0, np.pi)
        d = r.uniform(0, 1) ** 0.6
        F.px(int(fx + 1 + np.cos(a_) * d * 9), int(ledge + 1 - np.sin(a_) * d * 3), 0.80 + 0.16 * r.random())
    # the pool at its foot, at the back of the path
    P = Tone(L.w, SH)
    px0, px1 = fx - 22, fx + 24
    for x in range(px0, px1):
        e = abs(x - (px0 + px1) / 2.0) / ((px1 - px0) / 2.0)
        y0 = back - 8 + int(4 * e * e)
        for y in range(y0, back + 1):
            P.px(x, y, 0.36 + 0.24 * max(0, noise_at(x // 2, y, seed) - 0.55) + 0.16 * (y == y0))
    put_tone(L, P, WATER, dither=0.4)
    for i in range(110):                                        # foam where it lands
        a = r.uniform(0, np.pi)
        d = r.uniform(0, 1) ** 0.5
        F.px(int(fx + 2 + np.cos(a) * d * 14), int(back - 4 - np.sin(a) * d * 5), 0.80 + 0.16 * r.random())
    put_tone(L, F, FOAM, dither=0.35)
    return (px0, px1)


def hut(L, x, w=52, h=30, seed=351, windows=0, door=None):
    """A field hut of rough stone on the terrace, its foot at the path's back edge: a flat roof with a white lip, a low
    dark doorway, a slit window; with windows > 0 a farmhouse: that many windows framed in white (a white arch over each),
    its door painted. -> (the roof's top, the door's middle)."""
    base = gy(x + w // 2) - 8
    top = base - h
    T = Tone(L.w, SH)
    st = noise((SH, L.w), seed, 1.1, 0.8)
    for y in range(top, base):
        for xx in range(x, x + w):
            d = y - top
            joint = (d % 5 == 4) or (((xx + 4 * (d // 5)) % 9) == 0)
            T.px(xx, y, 0.42 - 0.12 * joint + 0.10 * (st[y, xx] - 0.5) - 0.12 * (xx > x + w - 9) - 0.06 * (y > base - 4))
    put_tone(L, T, IBBSTONE, dither=0.3)
    Wt = Tone(L.w, SH)
    for xx in range(x - 1, x + w + 1):
        Wt.px(xx, top - 1, 0.94); Wt.px(xx, top, 0.80); Wt.px(xx, top + 1, 0.60)
        if (xx - x) % 3 == 0:
            Wt.px(xx, top - 2, 0.92)
    D = Tone(L.w, SH)
    dx = x + 12
    for y in range(base - 22, base):
        for xx in range(dx, dx + 11):
            D.px(xx, y, 0.06 + 0.04 * (xx == dx))
    if windows:
        for k in range(windows):
            wx0 = x + 30 + k * 16
            if wx0 + 8 > x + w - 4:
                break
            for y in range(top + 9, top + 18):
                for xx in range(wx0, wx0 + 7):
                    D.px(xx, y, 0.08)
            for xx in range(wx0 - 1, wx0 + 8):
                Wt.px(xx, top + 18, 0.86)
            for i in range(7):
                Wt.px(wx0 + i, top + 7 - (1 if 1 <= i <= 5 else 0), 0.92)
        for xx in range(x, x + w):
            Wt.px(xx, top + 5, 0.82)
    else:
        for y in range(top + 8, top + 12):
            for xx in range(x + 34, x + 42):
                D.px(xx, y, 0.08)
    put_tone(L, Wt, LIME, dither=0)
    put_tone(L, D, SOOT, dither=0)
    if door is not None:
        P = Tone(L.w, SH)
        for y in range(base - 21, base):
            for xx in range(dx + 1, dx + 10):
                P.px(xx, y, 0.46 + 0.14 * (xx == dx + 1) - 0.14 * ((y - base) % 7 == 0) - 0.10 * (xx == dx + 5))
        put_tone(L, P, door, dither=0.2)
    return top - 1, dx + 5


def boulder(L, cx, base, rx=26, ry=24, seed=361):
    """A granite boulder left in a field: rounded, lit on its upper left, lichen on it. -> its top's profile."""
    h, w = ry + 2, 2 * rx + 2
    yy, xx = np.mgrid[0:h, 0:w]
    e = ((xx - rx) / float(rx)) ** 2 + ((yy - ry) / float(ry)) ** 2
    m = (e <= 1.0) & (yy < ry)
    Hh = np.sqrt(np.clip(1 - e, 0, 1))
    lit = light(ndi.gaussian_filter(Hh * 20, 1.0), -0.7, -0.8, 0.12)
    t = 0.44 + 0.30 * np.clip(lit, -1, 1) + 0.08 * (noise((h, w), seed, 1.2, 1.2) - 0.5)
    Z1.piece_put(L, t, m, IBBSTONE, cx - rx, base - ry, dither=0.4)
    tops = {}
    for i in range(w):
        col = np.where(m[:, i])[0]
        if len(col):
            tops[cx - rx + i] = base - ry + int(col.min())
    return tops


def house_at(L, x, base, w, h, seed, floors=1, door=True, roof=()):
    """A stone house of Ibb standing with its foot at `base` (Jibla's house, wherever it stands). -> (roof, door x)."""
    old = STZ.TSTONE
    STZ.TSTONE = IBBSTONE
    try:
        P, info = STZ.taiz_house(w, h, seed=seed, style='stone', roof=list(roof), door='street' if door else None, floors=floors)
    finally:
        STZ.TSTONE = old
    y0 = base - P.h
    L.paste(P, x, y0)
    d = info['doors'][0]['x'] + x if info['doors'] else None
    return y0 + info['top'], d


# ------------------------------------------------------------------ the relay station
def fence(L, x0, x1, base, h=22, gate=None, seed=371):
    """A chain-link fence on steel posts with barbed wire along the top; `gate`: (x0, x1) where it stands open, the leaf
    swung back against the fence."""
    T = Tone(L.w, SH)
    top = base - h
    for x in range(x0, x1):
        if gate and gate[0] <= x < gate[1]:
            continue
        for y in range(top, base):
            if ((x + y) % 4 == 0) or ((x - y) % 4 == 0):
                T.px(x, y, 0.50 + 0.10 * (y < top + 3))
    for x in range(x0, x1 + 1, 24):
        if gate and gate[0] < x < gate[1]:
            continue
        for y in range(top - 4, base + 1):
            T.px(x, y, 0.80); T.px(x + 1, y, 0.46)
    if gate:
        for gx in gate:
            for y in range(top - 4, base + 1):
                T.px(gx, y, 0.84); T.px(gx + 1, y, 0.50)
        # the leaf, swung back against the fence on the left
        for x in range(gate[0] - 14, gate[0]):
            for y in range(top + 2, base - 1):
                if ((x + y) % 3 == 0) or y in (top + 2, base - 2) or x in (gate[0] - 14, gate[0] - 1):
                    T.px(x, y, 0.66)
    for x in range(x0, x1):
        if gate and gate[0] <= x < gate[1]:
            continue
        T.px(x, top - 3 + ((x // 3) % 2), 0.62)
    put_tone(L, T, STEEL, dither=0)


def cabin(L, x, base, w=70, h=32, seed=381):
    """The equipment shelter: a prefab box of white panels on a plinth, a door at its right end, an air conditioner on its
    side, cables running out of it toward the mast. -> (the roof's top, the door's middle)."""
    top = base - h
    T = Tone(L.w, SH)
    for y in range(top, base):
        for xx in range(x, x + w):
            seam = ((xx - x) % 14 == 13)
            T.px(xx, y, 0.74 - 0.14 * seam - 0.16 * (xx > x + w - 6) + 0.06 * (y < top + 2) - 0.10 * (y > base - 3) - 0.04 * ((y - top) > h * 0.6))
    for xx in range(x - 1, x + w + 1):
        T.px(xx, top - 1, 0.88); T.px(xx, top - 2, 0.58)
    put_tone(L, T, PANEL, dither=0.25)
    D = Tone(L.w, SH)
    dx = x + w - 20
    for y in range(base - 24, base):
        for xx in range(dx, dx + 12):
            D.px(xx, y, 0.10 + 0.05 * (xx == dx))
    for y in range(top + 6, top + 12):
        for xx in range(x + 8, x + 20):
            D.px(xx, y, 0.14 + 0.06 * (y == top + 6))
    put_tone(L, D, SOOT, dither=0)
    A = Tone(L.w, SH)                                     # the air conditioner
    for y in range(top + 6, top + 18):
        for xx in range(x + 28, x + 42):
            A.px(xx, y, 0.62 + 0.10 * (y == top + 6) - 0.20 * ((xx - x) % 2 == 0 and y > top + 8))
    put_tone(L, A, STEEL, dither=0)
    return top - 2, dx + 6


def generator(L, x, base, seed=391):
    """A diesel generator on skids: a yellow box with louvres and a black exhaust stack."""
    T = Tone(L.w, SH)
    for y in range(base - 16, base - 2):
        for xx in range(x, x + 22):
            louv = (xx > x + 3 and xx < x + 12 and (y - base) % 3 == 0)
            T.px(xx, y, 0.60 - 0.18 * louv - 0.14 * (xx > x + 18) + 0.10 * (y == base - 16))
    put_tone(L, T, YELLOWG, dither=0.2)
    K = Tone(L.w, SH)
    for xx in range(x - 1, x + 23):
        K.px(xx, base - 2, 0.30); K.px(xx, base - 1, 0.20)
    for y in range(base - 24, base - 16):
        K.px(x + 17, y, 0.30); K.px(x + 18, y, 0.18)
    put_tone(L, K, STEEL, dither=0)


def mast(L, cx, base, top=-10, seed=401):
    """The lattice mast: three legs (two seen) tapering upward, braced in X's, a ladder up its middle, a platform with a
    rail, dishes and panel antennas bolted on, red and white bands at the top for the aircraft. -> the platform's y."""
    T = Tone(L.w, SH)
    R = Tone(L.w, SH)
    hb, ht = 18, 5                                          # half-width at the foot and at the top
    for y in range(top, base):
        u = (base - y) / float(base - top)
        hw = hb + (ht - hb) * u
        xl, xr = int(round(cx - hw)), int(round(cx + hw))
        band = top < y < top + 40 and ((y - top) // 8) % 2 == 0
        tgt = R if band else T
        tgt.px(xl, y, 0.80); tgt.px(xl + 1, y, 0.50)
        tgt.px(xr, y, 0.60); tgt.px(xr - 1, y, 0.40)
        if (y - top) % 3 == 0:
            T.px(cx, y, 0.66)                                # the ladder's rungs
    # the bracing: X's between the legs, every 14 px
    for yb in range(base - 14, top, -14):
        for i in range(15):
            y = yb + i
            if y >= base:
                break
            u = (base - y) / float(base - top)
            hw = hb + (ht - hb) * u
            f = i / 14.0
            T.px(int(round(cx - hw + 2 * hw * f)), y, 0.56)
            T.px(int(round(cx + hw - 2 * hw * f)), y, 0.44)
    put_tone(L, T, STEEL, dither=0)
    put_tone(L, R, REDP, dither=0)
    # the platform and its rail (low enough that a man on it stands clear of the timer at the top of the screen)
    py = base - 34
    P = Tone(L.w, SH)
    for xx in range(cx - 16, cx + 17):
        P.px(xx, py, 0.84); P.px(xx, py + 1, 0.46)
        if (xx - cx) % 4 == 0:
            for j in range(1, 8):
                P.px(xx, py - j, 0.60)
        P.px(xx, py - 8, 0.72)
    put_tone(L, P, STEEL, dither=0)
    # dishes and panels
    D = Tone(L.w, SH)
    for (dx, dy, rr) in ((-12, py - 26, 7), (11, py - 40, 6), (-8, py - 58, 5)):
        for j in range(-rr, rr + 1):
            for i in range(-rr // 2, rr // 2 + 1):
                if (i / (rr / 2.0 + 0.5)) ** 2 + (j / (rr + 0.5)) ** 2 <= 1:
                    D.px(cx + dx + i, dy + j, 0.86 - 0.20 * (i > 0) + 0.04 * (j < 0))
    for (dx, dy) in ((14, py - 18), (-15, py - 46), (9, py - 66)):
        for j in range(12):
            D.px(cx + dx, dy + j, 0.80); D.px(cx + dx + 1, dy + j, 0.62)
    put_tone(L, D, PANEL, dither=0)
    return py - 1


# ------------------------------------------------------------------ their stage
def chairs(L, x0, x1, base, rows=2, seed=411):
    """Rows of plastic chairs set out for the audience, facing the stage (to the right): white, a red one here and there;
    the back row a step further off (higher up the picture). -> where each chair's seat is: [(x, y, row)], the x a
    sitter's hips come to (3 in from the back), the y the top of the seat."""
    T = Tone(L.w, SH)
    R = Tone(L.w, SH)
    seats = []
    for row in range(rows):
        b = base - 5 * (rows - 1 - row)
        for i, cx in enumerate(range(x0 + 5 * row, x1 - 8, 12)):
            seats.append((cx + 3, b - 7, row))
            tgt = R if (i * 3 + row * 5) % 7 == 2 else T
            # the back, leaning back a little, its top rolled
            for j, y in enumerate(range(b - 16, b - 7)):
                lx = cx - (1 if j < 3 else 0)
                tgt.px(lx, y, 0.84); tgt.px(lx + 1, y, 0.62)
            tgt.px(cx - 2, b - 16, 0.92)
            # the seat
            for xx in range(cx, cx + 8):
                tgt.px(xx, b - 7, 0.94); tgt.px(xx, b - 6, 0.58)
            # the legs, splayed
            for j in range(5):
                tgt.px(cx + 1 - (j // 3), b - 5 + j, 0.70)
                tgt.px(cx + 7 + (j // 3), b - 5 + j, 0.56)
    put_tone(L, T, PANEL, dither=0)
    put_tone(L, R, REDP, dither=0)
    return seats


def camera(L, x, base, seed=421):
    """A TV camera on a tripod, facing the stage: the body, the lens hood, the viewfinder, the pan bar."""
    T = Tone(L.w, SH)
    for y in range(base - 22, base):
        u = (y - (base - 22)) / 22.0
        T.px(int(round(x - 6 * u)), y, 0.50); T.px(int(round(x + 6 * u)), y, 0.40); T.px(x, y, 0.46)
    for y in range(base - 32, base - 23):
        for xx in range(x - 6, x + 8):
            T.px(xx, y, 0.34 + 0.12 * (y == base - 32) - 0.08 * (xx > x + 4))
    for y in range(base - 31, base - 25):
        for xx in range(x + 8, x + 12):
            T.px(xx, y, 0.22)
    for xx in range(x - 12, x - 5):
        T.px(xx, base - 25 + (x - 5 - xx) // 3, 0.56)
    put_tone(L, T, CLOTH, dither=0)
    G = Tone(L.w, SH)
    G.px(x + 11, base - 29, 0.9); G.px(x - 4, base - 34, 0.7); G.px(x - 3, base - 34, 0.7)
    put_tone(L, G, PANEL, dither=0)


def light_stand(L, x, base, hgt=46, face=1, seed=431):
    """A stage light on a stand: a thin pole on three feet, the lamp housing tilted toward the stage."""
    T = Tone(L.w, SH)
    for y in range(base - hgt, base):
        T.px(x, y, 0.40)
    for i in range(6):
        T.px(x - i, base - 1 + 0 * i - (i // 3), 0.36); T.px(x + i, base - 1 - (i // 3), 0.30)
    hy = base - hgt
    for j in range(-4, 5):
        for i in range(0, 8):
            if abs(j) <= 2 + i // 3:
                T.px(x + face * i, hy + j, 0.30 + 0.12 * (j < 0))
    put_tone(L, T, CLOTH, dither=0)
    G = Tone(L.w, SH)
    for j in range(-3, 4):
        G.px(x + face * 8, hy + j, 0.96 - 0.06 * abs(j))
    put_tone(L, G, PANEL, dither=0)


def stage(L, x0, x1, base, seed=441):
    """The stage: a deck on trestles skirted in black cloth, two steps up at its left end; at its back a truss frame hung
    with the blue curtain in deep folds under a swagged valance, their emblem (the gold scorpion in its wreath) over the
    middle, their flag on a pole beside the frame; a light on a stand at either end, turned on the podium.
    -> the deck's top, and where the podium stands."""
    deck = base - 12
    T = Tone(L.w, SH)
    for xx in range(x0, x1):
        for y in range(deck + 2, base):
            fold = (xx - x0) % 7
            T.px(xx, y, 0.28 + 0.10 * (fold < 2) - 0.08 * (fold >= 5) - 0.08 * (y > base - 3))
    for k in range(2):                                        # the steps up at the left end
        sx = x0 - 8 + 4 * k
        for xx in range(sx, sx + 5):
            for y in range(deck + 6 - 6 * k, base):
                T.px(xx, y, 0.34 + 0.12 * (y == deck + 6 - 6 * k) - 0.06 * (xx > sx + 3))
    put_tone(L, T, CLOTH, dither=0.2)
    Wd = Tone(L.w, SH)
    for xx in range(x0 - 1, x1 + 1):
        Wd.px(xx, deck, 0.80); Wd.px(xx, deck + 1, 0.56)
    put_tone(L, Wd, TEAK, dither=0)
    # the truss frame: two towers and a beam, lattice
    fx0, fx1 = x0 + 12, x1 - 10
    ctop = deck - 54
    F = Tone(L.w, SH)
    for tx in (fx0 - 5, fx1 + 1):
        for y in range(ctop - 6, deck):
            F.px(tx, y, 0.86); F.px(tx + 3, y, 0.52)
            zz = (y - ctop) % 6
            F.px(tx + (1 if zz < 3 else 2), y, 0.66)
    for xx in range(fx0 - 5, fx1 + 5):
        F.px(xx, ctop - 6, 0.88); F.px(xx, ctop - 3, 0.50)
        zz = (xx - fx0) % 6
        F.px(xx, ctop - 5 + (zz // 3), 0.68)
    put_tone(L, F, STEEL, dither=0)
    # the curtain: deep folds, lit from the left, darker toward the floor; a swagged valance along the top
    C = Tone(L.w, SH)
    for xx in range(fx0 - 1, fx1 + 1):
        u = (xx - fx0) / 11.0
        for y in range(ctop, deck - 1):
            v = (y - ctop) / float(deck - ctop)
            ph = u * 2 * np.pi + 0.35 * np.sin(v * 3.0 + u)
            t = 0.40 + 0.24 * np.cos(ph) + 0.06 * np.cos(2 * ph) - 0.12 * v
            C.px(xx, y, t)
    for xx in range(fx0 - 1, fx1 + 1):                        # the valance: swags 14 wide
        k = (xx - fx0) % 14
        depth = int(round(6 - 0.12 * (k - 7) ** 2))
        for y in range(ctop, ctop + 2 + max(0, depth)):
            C.px(xx, y, 0.62 + 0.14 * (y == ctop) - 0.18 * (y == ctop + 1 + max(0, depth)))
    put_tone(L, C, CURTAIN, dither=0.35)
    # the emblem: a gold wreath, the scorpion in it, on a red disc
    ex, ey = (fx0 + fx1) // 2, ctop + 20
    E = Tone(L.w, SH)
    Rr = Tone(L.w, SH)
    for j in range(-10, 11):
        for i in range(-10, 11):
            d = np.sqrt(i * i + j * j)
            if d <= 7.5:
                Rr.px(ex + i, ey + j, 0.52 + 0.10 * (j < -3))
            elif d <= 10 and (i + j) % 2 == 0 and j > -8:
                E.px(ex + i, ey + j, 0.70 + 0.12 * (i < 0))
    for (i, j) in [(0, -4), (0, -3), (0, -2), (1, -2), (0, -1), (1, -1), (0, 0), (1, 0), (0, 1), (1, 1), (1, 2), (2, 3), (3, 3),
                   (4, 2), (-3, -3), (-4, -4), (3, -3), (4, -4), (-3, -1), (-4, 0), (3, -1), (4, 0), (-2, 1), (2, 4)]:
        E.px(ex + i, ey + j, 0.92)
    put_tone(L, Rr, REDP, dither=0)
    put_tone(L, E, GOLD, dither=0)
    # the flag on its pole, left of the frame
    px_ = fx0 - 12
    P = Tone(L.w, SH)
    for y in range(ctop - 22, deck):
        P.px(px_, y, 0.76); P.px(px_ + 1, y, 0.46)
    P.px(px_, ctop - 23, 0.90)
    put_tone(L, P, STEEL, dither=0)
    Fq = np.zeros((10, 16, 3))
    yy, xx = np.mgrid[0:10, 0:16]
    wave = np.round(np.sin(xx / 3.0)).astype(int)
    Fq[:] = (184, 34, 24)
    Fq[((yy - wave) >= 4) & ((yy - wave) < 7)] = (232, 192, 56)
    Q = Layer(16, 10)
    Q.put((np.round(Fq / 8) * 8).astype(np.uint8), (yy - wave >= 0) & (yy - wave < 10))
    L.paste(Q, px_ + 2, ctop - 22)
    light_stand(L, x0 - 12, deck + 10, hgt=50, face=1, seed=seed + 1)
    light_stand(L, x1 + 1, deck + 10, hgt=50, face=-1, seed=seed + 2)
    return deck, (fx0 + fx1) // 2 + 26


# ------------------------------------------------------------------ the mountainside behind, and its falls
FALLS_LX = 380                    # where the far fall comes off the top in the back layer's picture
FX = 470                          # where the near falls come down behind the path (local x), into their pool


def back_falls(w=1410, seed=461, L=None, crest=None, slope=True):
    """The mountainside above the terraces (the `back` layer, moving at 0.7 of the path's pace), taking over from Jibla's
    slope: terraced green climbing on up, trees on it, and to the right the slope coming down again toward the pass, a
    hamlet of tower houses on a spur. -> the picture (at BACK_X)."""
    h = SH
    L = L if L is not None else Layer(w, h)
    r = rng(seed)
    yy, xx = np.mgrid[0:h, 0:w]
    xs = np.arange(w)
    if crest is None:
        crest = back_crest(w, seed)
    if slope:
        m = yy >= crest[None, :]
        per = 6.0
        E = yy - 0.35 * (crest[None, :] - crest.mean())
        frac = (E / per) - np.floor(E / per)
        t = 0.52 + 0.08 * (noise((h, w), seed + 1, 18, 3) - 0.5) - 0.14 * (frac > 0.72) + 0.06 * (frac < 0.2)
        L.put(toned(np.clip(t, 0, 1), I.TERR, dither=0.5), m)
    Tt = Tone(w, h)
    for i in range(int(w / 9)):
        cx = int(r.integers(0, w))
        cy = int(crest[cx] + r.integers(6, 70))
        if cy < h - 8:
            I.tree_tone(Tt, cx, cy, r.uniform(2.0, 4.2), int(r.integers(0, 1000)))
    L.paste(Tt.layer(I.LEAF, dither=0.5))
    for k, (hx, hw_, hh) in enumerate(((760, 18, 30), (781, 14, 22), (797, 20, 36), (820, 15, 26))):
        base = int(crest[hx + hw_ // 2] + 26)
        Z2.small_house(L, hx, base, hw_, hh, seed + 50 + k, haze=0.22)
    if slope:                                          # (painted as part of one picture, the haze comes with that)
        sub = L.rgb.astype(float)
        L.rgb[:] = np.clip(sub * 0.90 + Z2.HAZE_T * 0.10, 0, 255).astype(np.uint8)
    return L


BACK_X = Z2.BACK_X + Z2.BACK_W    # (this picks up where Jibla's slope ends)


def back_crest(w, seed=461):
    """The mountainside's skyline over the terraces: from where Jibla's slope comes down (76), up to the heights, coming
    down again toward the pass, with a hamlet on a spur."""
    xs = np.arange(w)
    return 76 - 40 * np.clip(xs / 300.0, 0, 1) ** 0.7 + 16 * np.clip((xs - 640) / 300.0, 0, 1) + 5 * (noise((1, w), seed, 26, 0.5)[0] - 0.5)


# ------------------------------------------------------------------ zone 3, put together
def play_z3(L=None, seed=501, ground=True):
    """The terraces, world 4080 to 6200 (the picture's x is world - 4080). With ground=False, Jibla's street and its last
    field wall running into the zone are left to stage_ibb_world.py (painted across the join)."""
    import stage_ibb_z3x as X
    L = L if L is not None else Layer(W3, SH)
    info = {}
    S = STATION
    # (1) the hillside behind the path, its trees, the things standing at the back of the path
    crest = hillside(L, seed=seed)
    if ground:
        Z1.drystone(L, 0, 40, 140, 171, seed=seed + 3)       # (Jibla's last field wall, running on into the zone)
    for k, (tx, th) in enumerate(((96, 120), (286, 112), (700, 128), (1018, 118), (1534 + S, 124))):
        Z1.eucalyptus(L, tx, gy(tx) - 30, hgt=th, seed=seed + 5 + k)
    Z1.sidr(L, 60, gy(60) - 9, seed=seed + 9)
    pool = falls(L, FX, seed=seed + 8)
    info['falls'] = dict(x=wx(FX), pool=[wx(pool[0]), wx(pool[1])])
    hr, hd = hut(L, 236, seed=seed + 10)
    plat('hutroof', [(wx(236), hr), (wx(236 + 51), hr)])
    info['hutdoor'] = dict(x=wx(hd), y=gy(hd))
    bt = boulder(L, 560, gy(560) - 1, seed=seed + 11)
    # the boulder's top: flat enough to stand on along its crown
    xs_ = sorted(x for x in bt if bt[x] <= min(bt.values()) + 3)
    plat('boulder', [(wx(xs_[0]), min(bt.values()) - 1), (wx(xs_[-1]), min(bt.values()) - 1)])
    fr, fd = hut(L, 944, w=70, h=33, seed=seed + 12, windows=2, door=BLUEP)
    plat('farmroof', [(wx(944), fr), (wx(944 + 69), fr)])
    info['farmdoor'] = dict(x=wx(fd), y=gy(fd)) if fd is not None else None
    # (2) the hamlet on the top terrace (29 Oct)
    info['hamlet'] = X.hamlet(L, 1046, seed=seed + 100)
    # (3) the relay station: the fence along the back of the path, the cabin, the generator, the mast
    base = gy(1100) - 7
    mty = mast(L, 1180 + S, base, seed=seed + 20)
    plat('mastdeck', [(wx(1166 + S), mty), (wx(1194 + S), mty)])
    cr, cd = cabin(L, 1064 + S, base, seed=seed + 21)
    plat('cabinroof', [(wx(1064 + S), cr), (wx(1064 + S + 69), cr)])
    info['cabindoor'] = dict(x=wx(cd), y=gy(cd))
    generator(L, 1138 + S, base, seed=seed + 22)
    fence(L, 1044 + S, 1214 + S, base, gate=(1196 + S, 1214 + S), seed=seed + 23)
    # (4) the stage: chairs for the audience, the camera, the deck, the curtain, the emblem, the flag, the lights
    seats = chairs(L, 1222 + S, 1288 + S, base + 3, seed=seed + 30)
    camera(L, 1210 + S, base + 4, seed=seed + 31)
    deck, podium = stage(L, 1296 + S, 1432 + S, gy(1300 + S) + 2, seed=seed + 32)
    plat('stagedeck', [(wx(1297 + S), deck - 1), (wx(1431 + S), deck - 1)])
    info['stage'] = dict(x0=wx(1296 + S), x1=wx(1432 + S), deck=deck - 1, podium=wx(podium), chairs=[wx(1222 + S), wx(1288 + S)],
                         camera=wx(1210 + S), seats=[[wx(x), y, row] for x, y, row in seats])
    # posters on the hut and the cabin
    info['posters'] = [Z1.poster(L, 271, gy(271) - 34, 'face', seed=seed + 40), Z1.poster(L, 1080 + S, base - 26, 'badge', seed=seed + 41)]
    info['posters'] += info['hamlet']['posters']
    # (4) the path along the terraces, the drop in front, the risers, the stream down through it all
    path(L, 36, W3, seed=seed + 50)
    bands = drop(L, seed=seed + 51)
    for kind, t0, t1 in bands:                          # (Jibla's street runs on for a few steps first)
        t0[:36] = SH; t1[:36] = SH
    risers(L, seed=seed + 52)
    stream(L, FX - 9, FX + 9, bands, seed=seed + 53)
    if ground:
        Z2.cobbles(L, 0, 40, seed=seed + 54)
    info['stream'] = dict(x0=wx(FX - 9), x1=wx(FX + 9))
    # where the screens' crates stand: at the back of the path
    info['screens'] = [dict(x=wx(56), gy=gy(56) - 10), dict(x=wx(780), gy=gy(780) - 10), dict(x=wx(1512), gy=gy(1512) - 10)]
    info['steps'] = [dict(x=wx(x), y=y) for x, y in STEPS]
    I.INFO['z3'] = info
    return L


def fore_z3(w=2100, seed=531):
    """Close to the lens on the terraces: the same tufts and stones as along the road."""
    return Z1.fore_z1(w=w, seed=seed)


if __name__ == '__main__':
    import time
    t0 = time.time()
    I.PLATS.clear()
    L = play_z3()
    B = back_falls()
    print('painted in %.1f s' % (time.time() - t0))
    print(sorted((k, v) for k, v in I.PLATS.items()))
    print(I.INFO.get('z3'))
