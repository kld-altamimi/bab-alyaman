# stage_ibb_z1x.py - the rest of Ibb's zone 1 (Khaled, 29 Oct 21:36: "the zones in this mission are a bit short"): past
# the minibus the valley road crosses the wadi on a concrete bridge (the land falling away behind its parapet into the
# wadi: its banks, boulders, oleanders, the stream coming down from the hills under the bridge), then a petrol station at
# the town's edge (a forecourt, a canopy on two posts, two pumps, a kiosk, a tall pole with a blank sign), then the
# town's edge itself, painted across the join into Jibla (stage_ibb_world.py: a half-built house of concrete blocks, a
# wall, the last poles). World coordinates (zone 1's picture starts at 0). Platforms as painted (I.PLATS).
import numpy as np
from paint import *
import stage_mocha as SM
import stage_taiz as STZ
import stage_zabid as SZ
import stage_ibb as I
import stage_ibb_z1 as Z1

SH, WALK, VERGE, ROAD_TOP = I.SH, I.WALK, Z1.VERGE, Z1.ROAD_TOP
put_tone, plat = SM.put_tone, I.plat
IBBSTONE, CONCRETE, SIGNY, PLASTIC, BLUEP, REDP, GOLD, GRASS = (Z1.IBBSTONE, Z1.CONCRETE, Z1.SIGNY, Z1.PLASTIC, Z1.BLUEP,
                                                               Z1.REDP, Z1.GOLD, Z1.GRASS)
DRYST, LEAF, TERR, GRAVEL, WATER, SOOT, LIME, TEAK, TIN, RUSTI, BUSW = (I.DRYST, I.LEAF, I.TERR, I.GRAVEL, I.WATER, SM.SOOT,
                                                                      SM.LIME, SM.TEAK, I.TIN, I.RUSTI, I.BUSW)
ROCK = ramp(['#1a1816', '#2c2926', '#403b36', '#56504a', '#6e675f', '#888077', '#a29a90', '#bcb4a8'], 14)      # the wadi's boulders
OLEAN = ramp(['#4a0c24', '#7a1838', '#a8284e', '#cc4468', '#e46e8a', '#f4a0b4'], 10)                         # oleander flowers
REED = ramp(['#1e2410', '#34401a', '#4c5a24', '#667430', '#828e40', '#a0aa58', '#bcc478'], 12)

BRIDGE = (1300, 1600)            # where the road is on the bridge (its parapets between these)
STREAM_X = 1452                  # where the stream passes under the bridge


def hash_(a, b):
    return float(I.hash01(int(a), int(b)))


# ------------------------------------------------------------------ the wadi behind the bridge
def wadi(L, x0, x1, seed=141):
    """Behind the bridge the fields give way to the wadi, lower than the road: the far fields along the top, the far bank
    falling steeply from them (earth, rock, scrub, in shade), the wadi's floor of pale stones and gravel with the stream
    winding across it toward the bridge, shining, boulders, oleanders in flower and reeds along the water, two trees
    growing up out of the floor; at either end the field's edge falls away to the floor. -> (the floor's top, the
    stream's line)."""
    r = rng(seed)
    w = x1 - x0
    xs = np.arange(x0, x1)
    top = np.round(117 + 9 * (noise((1, w), seed, 16, 0.5)[0] - 0.5) + 2 * np.sin(xs / 37.0)).astype(int)
    fl = np.round(136 + 4 * (noise((1, w), seed + 1, 24, 0.5)[0] - 0.5)).astype(int)
    g = noise((SH, w), seed + 2, 1.0, 0.8)
    fb = fbm((SH, w), seed + 3, 10, 4, octaves=3)
    # the stream's centre line across the floor: from the far bank's foot at the left toward the bridge
    def stream_at(y):
        v = (y - 136) / float(ROAD_TOP + 1 - 136)
        return x0 + 70 + (STREAM_X - x0 - 70) * v ** 0.8 + 10 * np.sin(v * 5.0) * (1 - v), 3.0 + 13 * v ** 1.1
    F = Tone(L.w, L.h)                     # the far fields
    Bk = Tone(L.w, L.h)                    # the far bank: earth
    Rk = Tone(L.w, L.h)                    # its rock
    Fl = Tone(L.w, L.h)                    # the floor: gravel and stones
    Wt = Tone(L.w, L.h)                    # the water
    for i, x in enumerate(xs):
        for y in range(int(top[i]), int(top[i]) + 7):
            F.px(x, y, 0.56 + 0.08 * (g[y, i] - 0.5) - 0.14 * ((y - top[i]) % 3 == 2) + 0.06 * (y == top[i]))
        for y in range(int(top[i]) + 7, int(fl[i])):
            v = (y - top[i] - 7) / float(max(1, fl[i] - top[i] - 7))
            t = 0.46 - 0.18 * v + 0.12 * (fb[y, i] - 0.5)
            if g[y, i] > 0.70 or fb[y, i] > 0.72:
                Rk.px(x, y, t + 0.14 + 0.10 * (g[y, i] > 0.85))
            elif fb[y, i] < 0.40:
                F.px(x, y, 0.40 - 0.10 * v + 0.10 * (g[y, i] - 0.5))           # (scrub growing on it)
            else:
                Bk.px(x, y, t)
        for y in range(int(fl[i]), ROAD_TOP + 2):
            cx, half = stream_at(y)
            d = abs(x - cx)
            v = (y - fl[i]) / float(ROAD_TOP + 2 - fl[i])
            if d < half:
                Wt.px(x, y, 0.30 + 0.22 * v + 0.40 * (g[y, i] > 0.74) + 0.22 * ((x + 2 * y) % 9 == 0) - 0.16 * (d > half - 1.2))
            else:
                wet = d < half + 3
                Fl.px(x, y, 0.62 - 0.10 * v + 0.12 * (g[y, i] - 0.5) + 0.12 * (g[y, i] > 0.80) - 0.18 * wet - 0.10 * (y == fl[i]))
    put_tone(L, F, TERR, dither=0.4)
    put_tone(L, Bk, I.MUDI, dither=0.4)
    put_tone(L, Rk, ROCK, dither=0.35)
    put_tone(L, Fl, GRAVEL, dither=0.4)
    put_tone(L, Wt, WATER, dither=0.4)
    # scrub and grass on the far bank, the odd far tree along the top
    G = Tone(L.w, L.h)
    for i, x in enumerate(xs):
        if hash_(x, seed + 4) < 0.25:
            y = int(top[i]) + 7 + int(hash_(x, seed + 5) * (fl[i] - top[i] - 8))
            for j in range(int(1 + 3 * hash_(x, seed + 6))):
                G.px(x, y - j, 0.40 + 0.10 * j)
    put_tone(L, G, GRASS, dither=0.3)
    Tt = Tone(L.w, L.h)
    for k in range(int(w / 50)):
        tx = int(r.integers(x0 + 10, x1 - 10))
        I.tree_tone(Tt, tx, int(top[tx - x0]) + 2, r.uniform(2.5, 4.0), int(r.integers(0, 1000)))
    put_tone(L, Tt, LEAF, dither=0.4)
    # either end: the field's edge falling away to the floor
    E = Tone(L.w, L.h)
    for side, ex in ((-1, x0), (1, x1)):
        for j in range(0, 32):
            y = 140 + j
            reach = int(4 + j * 0.9)
            for q in range(reach):
                xx = ex - q if side > 0 else ex + q
                E.px(xx, y, 0.50 - 0.010 * j + 0.10 * (q < 2) + 0.06 * (hash_(xx, y) < 0.2))
    put_tone(L, E, I.MUDI, dither=0.4)
    # boulders on the floor
    B = Tone(L.w, L.h)
    for k in range(int(w / 30)):
        bx = int(r.integers(x0 + 20, x1 - 20))
        by = int(r.integers(140, ROAD_TOP + 1))
        cx, half = stream_at(by)
        if abs(bx - cx) < half + 4:
            continue
        rx, ry = r.uniform(3, 8), r.uniform(2.5, 5)
        for jj in range(-int(ry) - 1, 1):
            for ii in range(-int(rx) - 1, int(rx) + 2):
                e = (ii / rx) ** 2 + (jj / ry) ** 2
                if e <= 1.0:
                    B.px(bx + ii, by + jj, 0.70 - 0.30 * (ii / rx) - 0.20 * (jj > -2) + 0.12 * (jj < -ry * 0.5))
    put_tone(L, B, ROCK, dither=0.35)
    # two trees growing up out of the floor (their crowns over the parapet), reeds and oleanders along the water
    for k, (tx, hh) in enumerate(((x0 + 44, 50), (x1 - 40, 58))):
        Z1.trunk(L, tx, 160, 160 - hh + 14, w=4, seed=seed + 20 + k, forks=1)
        Z1.crown(L, tx + 2, 160 - hh, 22, 12, seed + 30 + k, LEAF, blobs=50, rmin=4, rmax=8, dark=0.02)
    Rd = Tone(L.w, L.h)
    Ol = Tone(L.w, L.h)
    Fw = Tone(L.w, L.h)
    for k in range(16):
        y = int(r.integers(140, ROAD_TOP))
        cx, half = stream_at(y)
        side = -1 if k % 2 else 1
        px_ = cx + side * (half + r.uniform(2, 6))
        sc = 0.5 + (y - 136) / 50.0
        if r.random() < 0.5:
            for st in range(int(r.integers(4, 8))):
                sx = px_ + r.uniform(-4, 4)
                hh = r.uniform(6, 12) * sc
                for j in range(int(hh)):
                    Rd.px(int(round(sx + 0.15 * j * side)), y - j, 0.40 + 0.40 * j / hh)
        else:
            rad = r.uniform(3.5, 6) * sc
            for jj in range(-int(rad * 1.2), 1):
                for ii in range(-int(rad * 1.4), int(rad * 1.4) + 1):
                    e = (ii / (rad * 1.4)) ** 2 + (jj / (rad * 1.2)) ** 2
                    if e <= 1.0 and hash_(ii * 7 + int(px_), jj * 13 + y) < 0.92:
                        Ol.px(int(px_) + ii, y + jj, 0.36 + 0.24 * (jj < -rad * 0.5) - 0.12 * (ii > 0))
                        if hash_(ii * 3 + int(px_), jj * 5 + y + 1) < 0.18:
                            Fw.px(int(px_) + ii, y + jj, 0.50 + 0.4 * hash_(ii, jj))
    put_tone(L, Rd, REED, dither=0.3)
    put_tone(L, Ol, LEAF, dither=0.35)
    put_tone(L, Fw, OLEAN, dither=0.2)
    return fl


def parapet(L, x0, x1, seed=143):
    """The bridge's parapet along the back of the road: concrete posts, a top rail and a middle one, the wadi showing
    between them; weathered, a stain under each post. -> the top rail's height."""
    T = Tone(L.w, L.h)
    top = VERGE - 7
    for xx in range(x0, x1):
        # the top rail: its top lit, its face, its shadow
        T.px(xx, top, 0.90); T.px(xx, top + 1, 0.74); T.px(xx, top + 2, 0.60); T.px(xx, top + 3, 0.34)
        # the middle rail
        T.px(xx, top + 9, 0.70); T.px(xx, top + 10, 0.52); T.px(xx, top + 11, 0.30)
        # the kerb at its foot
        for yy in range(ROAD_TOP - 3, ROAD_TOP + 1):
            T.px(xx, yy, 0.62 - 0.08 * (yy - (ROAD_TOP - 3)) + 0.06 * ((xx // 11) % 2))
    for px_ in range(x0, x1 + 1, 18):
        for yy in range(top, ROAD_TOP - 2):
            for i in range(4):
                T.px(px_ + i, yy, 0.78 - 0.14 * i + 0.06 * (yy == top))
    put_tone(L, T, CONCRETE, dither=0.25, grain=0.05, seed=seed)
    St = Tone(L.w, L.h)
    for px_ in range(x0, x1 + 1, 18):
        for j in range(6):
            St.px(px_ + 1, top + 4 + j, 0.30); St.px(px_ + 2, top + 4 + j, 0.36)
    put_tone(L, St, GRAVEL, dither=0)
    return top


def bridge_front(L, x0, x1, seed=145):
    """The near parapet, along the bottom of the picture: the top of its rail and the heads of its posts, under Yazeed's
    feet (the bridge from the road)."""
    T = Tone(L.w, L.h)
    y = SH - 7
    for xx in range(x0, x1):
        T.px(xx, y, 0.92); T.px(xx, y + 1, 0.76); T.px(xx, y + 2, 0.58)
        for yy in range(y + 3, SH):
            T.px(xx, yy, 0.40 - 0.04 * (yy - y))
    for px_ in range(x0 + 6, x1, 22):
        for yy in range(y - 2, SH):
            for i in range(5):
                T.px(px_ + i, yy, 0.84 - 0.12 * i + 0.08 * (yy == y - 2))
    put_tone(L, T, CONCRETE, dither=0.25)


def expansion_joint(L, x):
    """Where the road goes onto the bridge: a steel joint across it."""
    T = Tone(L.w, L.h)
    for yy in range(ROAD_TOP + 1, SH - 7):
        T.px(x, yy, 0.18); T.px(x + 1, yy, 0.62); T.px(x + 2, yy, 0.30)
    put_tone(L, T, I.TIN, dither=0)


def bridge(L, seed=147):
    """The bridge, the wadi behind it, the nest of sandbags they have on it. -> what the level needs."""
    b0, b1 = BRIDGE
    wadi(L, b0 - 14, b1 + 14, seed=seed)
    ptop = parapet(L, b0, b1, seed=seed + 1)
    plat('parapet', [(b0 + 2, ptop - 1), (b1 - 2, ptop - 1)])
    for x in (b0 - 3, b1 + 1):
        expansion_joint(L, x)
    bridge_front(L, b0, b1, seed=seed + 2)
    # their nest on the bridge: sandbags in two courses, a drum
    nx = 1424
    SM.sack_pile(L, [(nx, nx + 44, WALK - 16), (nx + 6, nx + 38, WALK - 23)], WALK + 2, seed=seed + 3, green=True, marks=False)
    plat('bridgebags', [(nx + 2, WALK - 22), (nx + 42, WALK - 22)])
    Z1.drum(L, nx + 47, WALK + 2, seed=seed + 4, rmp=BLUEP)
    SM.soft_shadow(L, nx - 2, nx + 60, WALK + 3, h=3, amt=0.74)
    return dict(x0=b0, x1=b1, parapet=ptop, nest=[nx, nx + 44])


# ------------------------------------------------------------------ the petrol station
def forecourt(L, x0, x1):
    """Concrete slabs where the verge was: grey, jointed, oil-stained."""
    T = Tone(L.w, L.h)
    for xx in range(x0, x1):
        for yy in range(VERGE + 1, ROAD_TOP + 1):
            joint = ((xx - x0) % 24 == 0) or ((yy - VERGE) % 6 == 0)
            stain = hash_(xx // 3, yy // 2) < 0.06
            T.px(xx, yy, 0.62 - 0.20 * joint - 0.22 * stain + 0.04 * ((xx * 5 + yy * 3) % 7 == 0))
    put_tone(L, T, CONCRETE, dither=0.3)


def pump(L, x, base, seed=1):
    """A fuel pump on its island: a white cabinet with a dark window and a red band, its nozzle hung on the side, the
    hose looping down."""
    T = Tone(L.w, L.h)
    h, w = 27, 12
    for j in range(h):
        for i in range(w):
            u = i / float(w - 1)
            T.px(x + i, base - h + j, 0.84 - 0.30 * u ** 1.5 + 0.08 * (j == 0) - 0.10 * (j > h - 3))
    put_tone(L, T, BUSW, dither=0.3)
    D = Tone(L.w, L.h)
    for j in range(5, 11):
        for i in range(2, 9):
            D.px(x + i, base - h + j, 0.14 + 0.10 * (j == 5))
    put_tone(L, D, SOOT, dither=0)
    Rb = Tone(L.w, L.h)
    for i in range(w):
        Rb.px(x + i, base - h + 14, 0.60); Rb.px(x + i, base - h + 15, 0.48)
    put_tone(L, Rb, REDP, dither=0)
    Hs = Tone(L.w, L.h)
    for k in range(14):
        a = k / 13.0
        Hs.px(x + w + int(3 * np.sin(a * np.pi)), base - h + 16 + int(a * 9), 0.20)
    for j in range(4):
        Hs.px(x + w, base - h + 12 + j, 0.30); Hs.px(x + w + 1, base - h + 12 + j, 0.26)
    put_tone(L, Hs, SOOT, dither=0)


def petrol(L, x, seed=151):
    """A petrol station at the town's edge: its forecourt, a canopy on two square posts with a red band along its edge
    and lights under it, two pumps on an island under it, a kiosk of plastered block (its door open on the dark, a window
    with a counter, a flat roof with a lip), posters of him on the kiosk, tyres and a drum, and a tall pole with a blank
    sign on top. -> what the level needs."""
    r = rng(seed)
    forecourt(L, x, x + 262)
    # the canopy: posts, then the slab with its band, its underside and lights
    cx0, cx1 = x + 14, x + 132
    ctop = 103
    P = Tone(L.w, L.h)
    for px_ in (x + 34, x + 108):
        for yy in range(ctop + 12, ROAD_TOP + 1):
            for i in range(5):
                P.px(px_ + i, yy, 0.80 - 0.13 * i - 0.06 * (yy > ROAD_TOP - 6))
    put_tone(L, P, CONCRETE, dither=0.2)
    C = Tone(L.w, L.h)
    for xx in range(cx0, cx1):
        C.px(xx, ctop, 0.92); C.px(xx, ctop + 1, 0.82)
        for yy in range(ctop + 2, ctop + 10):
            C.px(xx, yy, 0.86 - 0.02 * (yy - ctop))
        C.px(xx, ctop + 10, 0.40); C.px(xx, ctop + 11, 0.26)
    put_tone(L, C, BUSW, dither=0.25)
    Bd = Tone(L.w, L.h)
    for xx in range(cx0, cx1):
        for yy in (ctop + 4, ctop + 5, ctop + 6):
            Bd.px(xx, yy, 0.62 + 0.08 * (yy == ctop + 4))
    put_tone(L, Bd, REDP, dither=0)
    Lt = Tone(L.w, L.h)
    for lx in range(cx0 + 10, cx1 - 6, 18):
        for i in range(8):
            Lt.px(lx + i, ctop + 12, 0.95)
    put_tone(L, Lt, BUSW, dither=0)
    SM.shade_box(L, cx0 + 2, ctop + 13, cx1 - 2, ctop + 24, 0.86)
    plat('canopy', [(cx0 + 1, ctop - 1), (cx1 - 1, ctop - 1)])
    # the island and its pumps
    Is = Tone(L.w, L.h)
    for xx in range(x + 46, x + 100):
        for yy in range(ROAD_TOP - 6, ROAD_TOP + 1):
            Is.px(xx, yy, 0.74 - 0.08 * (yy - (ROAD_TOP - 6)) + 0.10 * (yy == ROAD_TOP - 6))
    put_tone(L, Is, CONCRETE, dither=0.2)
    for k, px_ in enumerate((x + 54, x + 80)):
        pump(L, px_, ROAD_TOP - 6, seed=seed + k)
    # the kiosk
    kx0, kx1 = x + 150, x + 222
    kb = ROAD_TOP - 1
    ktop = kb - 41
    STZ.plaster(L, kx0, ktop, kx1, kb, LIME, seed=seed + 3, base=0.78, stain=1.0)
    K = Tone(L.w, L.h)
    for xx in range(kx0 - 2, kx1 + 2):
        K.px(xx, ktop, 0.90); K.px(xx, ktop + 1, 0.70); K.px(xx, ktop + 2, 0.40)
    put_tone(L, K, CONCRETE, dither=0)
    plat('kiosk', [(kx0 - 1, ktop - 1), (kx1, ktop - 1)])
    D = Tone(L.w, L.h)
    door_x0 = kx0 + 8
    for yy in range(ktop + 13, kb):
        for xx in range(door_x0, door_x0 + 14):
            D.px(xx, yy, 0.10 + 0.04 * ((xx + yy) % 5 == 0))
    for yy in range(ktop + 12, ktop + 26):
        for xx in range(kx0 + 30, kx1 - 6):
            D.px(xx, yy, 0.16 + 0.05 * ((xx * 2 + yy) % 7 == 0))
    put_tone(L, D, SOOT, dither=0)
    Fr = Tone(L.w, L.h)
    for xx in range(door_x0 - 1, door_x0 + 15):
        Fr.px(xx, ktop + 12, 0.30)
    for yy in range(ktop + 12, kb):
        Fr.px(door_x0 - 1, yy, 0.30); Fr.px(door_x0 + 14, yy, 0.30)
    for xx in range(kx0 + 29, kx1 - 5):
        Fr.px(xx, ktop + 11, 0.36); Fr.px(xx, ktop + 26, 0.70); Fr.px(xx, ktop + 27, 0.44)
    put_tone(L, Fr, TEAK, dither=0)
    # goods in the window: bottles of water, oil, packets
    G = np.zeros((SH, L.w, 3), np.uint8)
    Gm = np.zeros((SH, L.w), bool)
    goods = [(200, 48, 32), (232, 196, 60), (60, 120, 180), (236, 232, 220), (80, 160, 80)]
    for sy in (ktop + 18, ktop + 25):
        for xx in range(kx0 + 32, kx1 - 8):
            if (xx * 5 + sy) % 6 < 4:
                c = goods[(xx * 3 + sy) % len(goods)]
                for j in range(1, 4):
                    Gm[sy - j, xx] = True
                    G[sy - j, xx] = (np.array(c) * (0.72 - 0.12 * (j == 1))).astype(np.uint8)
    L.rgb[Gm] = G[Gm]
    L.a |= Gm
    p1 = Z1.poster(L, x + 120, 141, 'face', seed=seed + 5)          # (on the wall behind the forecourt)
    # tyres stacked by the kiosk, a drum
    for k in range(3):
        Z1.tyre(L, kx1 + 14, ROAD_TOP + 1 - 4 * k, seed=seed + 6 + k, r_=8)
    Z1.drum(L, kx1 + 26, ROAD_TOP + 2, seed=seed + 9, rmp=REDP)
    # the tall sign: a pole, a blank panel with a red band
    sx = x + 252
    S = Tone(L.w, L.h)
    for yy in range(60, ROAD_TOP + 1):
        S.px(sx, yy, 0.70); S.px(sx + 1, yy, 0.50); S.px(sx + 2, yy, 0.30)
    put_tone(L, S, CONCRETE, dither=0)
    Pn = Tone(L.w, L.h)
    for yy in range(46, 66):
        for xx in range(sx - 12, sx + 15):
            Pn.px(xx, yy, 0.80 + 0.10 * (yy == 46) - 0.18 * (yy == 65) - 0.10 * (xx == sx + 14))
    put_tone(L, Pn, BUSW, dither=0.2)
    Pr = Tone(L.w, L.h)
    for yy in (52, 53, 54, 55):
        for xx in range(sx - 12, sx + 15):
            Pr.px(xx, yy, 0.60)
    put_tone(L, Pr, REDP, dither=0)
    SM.soft_shadow(L, x + 40, x + 104, ROAD_TOP + 1, h=3, amt=0.80)
    return dict(x0=x, x1=x + 262, canopy=[cx0, cx1], ctop=ctop, kiosk=[kx0, kx1], ktop=ktop,
                door=dict(x=int(door_x0 + 7), y=int(WALK)), posters=[p1], sign=sx)


# ------------------------------------------------------------------ the town's edge (painted across the join)
def block_house(L, x, w=64, h=38, seed=161):
    """A house of grey concrete blocks nobody has finished: one storey, the blocks showing, a doorway with no door, a
    window hole, rods standing up from its top for the next floor."""
    base = Z1.ROAD_TOP - 2
    top = base - h
    T = Tone(L.w, L.h)
    for yy in range(top, base):
        for xx in range(x, x + w):
            course = (yy - top) // 5
            joint = ((yy - top) % 5 == 4) or (((xx - x) + 8 * (course % 2)) % 16 == 0)
            T.px(xx, yy, 0.62 - 0.16 * joint - 0.08 * (xx > x + w - 6) + 0.04 * (hash_(xx, yy) < 0.1))
    put_tone(L, T, CONCRETE, dither=0.3)
    D = Tone(L.w, L.h)
    for yy in range(top + 12, base):
        for xx in range(x + 10, x + 22):
            D.px(xx, yy, 0.10)
    for yy in range(top + 10, top + 20):
        for xx in range(x + 34, x + 46):
            D.px(xx, yy, 0.12)
    put_tone(L, D, SOOT, dither=0)
    Rr = Tone(L.w, L.h)
    for cx in (x + 2, x + w // 2, x + w - 4):
        for i in (0, 2):
            for yy in range(top - 10, top):
                Rr.px(cx + i, yy, 0.42 + 0.16 * (yy % 2))
    put_tone(L, Rr, RUSTI, dither=0)
    return top


def town_edge(L, x0, seed=171):
    """Where the valley road reaches Jibla (world x0 on): the verge ending at a kerb, a half-built house of blocks, a low
    wall of the town's stone with his poster, the last poles carrying the wires into the town."""
    block_house(L, x0 + 12, seed=seed)
    Z1.drystone(L, x0 + 84, x0 + 150, VERGE - 4, VERGE + 2, seed=seed + 1)
    p = Z1.poster(L, x0 + 104, VERGE - 4, 'badge', seed=seed + 2)
    return dict(posters=[p])
