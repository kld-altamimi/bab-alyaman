# stage_ibb_z2x.py - the rest of Jibla (Khaled, 29 Oct 21:36: "the zones in this mission are a bit short"): past the last
# house of the upper street, the souq (a terrace of stone houses with shops in their ground floors under striped canvas
# awnings on poles, crates of fruit and sacks of grain set out under them), then the ruin of Dar al-Izz, Queen Arwa's
# palace (stone walls standing roofless, five storeys of arched windows at their highest, their tops broken, an arched
# gateway into the dark, fallen stones heaped at their foot), then the path out of town between field walls toward the
# terraces (painted across the join by stage_ibb_world.py). Local x, as stage_ibb_z2.py's (world = local + its X0).
import numpy as np
from paint import *
import stage_mocha as SM
import stage_taiz as STZ
import stage_zabid as SZ
import stage_ibb as I
import stage_ibb_z1 as Z1
import stage_ibb_z2 as Z2

SH, WALK, BASE = I.SH, I.WALK, Z2.BASE
put_tone, plat, wx = SM.put_tone, I.plat, Z2.wx
IBBSTONE, CONCRETE, REDP, BLUEP, GOLD, SIGNY = Z1.IBBSTONE, Z1.CONCRETE, Z1.REDP, Z1.BLUEP, Z1.GOLD, Z1.SIGNY
LIME, TEAK, SOOT, DRYST, LEAF, TERR = SM.LIME, SM.TEAK, SM.SOOT, I.DRYST, I.LEAF, I.TERR
CANVAS = ramp(['#3a362c', '#5e584a', '#847c6a', '#a8a08c', '#c8c0aa', '#e2dac6', '#f4eee0'], 12)            # sun-bleached canvas
CANRED = ramp(['#2c0a06', '#561410', '#80221a', '#a63426', '#c64c38', '#de7058'], 10)
CANGRN = ramp(['#0c1a10', '#16301c', '#22482a', '#30603a', '#44784c', '#5c9062'], 10)
FRUIT = ramp(['#4a1a02', '#7e3204', '#b44e08', '#d86e10', '#ee9424', '#f8bc50'], 10)                          # oranges
OLDSTONE = ramp(['#16140f', '#29251e', '#3e382e', '#544c40', '#6c6252', '#857a66', '#9e927c', '#b6aa92', '#ccc2aa'], 18)  # the palace's old stone


def hash_(a, b):
    return float(I.hash01(int(a), int(b)))


# ------------------------------------------------------------------ the souq
def awning(L, x0, x1, rmp, seed=1):
    """A canvas awning over a shop: its top seen from just above, striped, its front edge scalloped and hanging, its
    shade under it, two poles holding the front up. -> its back's height (where a man can stand)."""
    ab, af = BASE - 36, BASE - 29
    T = Tone(L.w, L.h)
    S = Tone(L.w, L.h)
    for xx in range(x0, x1):
        stripe = ((xx - x0) // 5) % 2
        for yy in range(ab, af):
            v = (yy - ab) / float(af - ab)
            t = 0.74 - 0.20 * v + 0.04 * ((xx * 3 + yy) % 7 == 0)
            (S if stripe else T).px(xx, yy, t)
        # the hanging edge: scallops
        k = (xx - x0) % 8
        drop = 3 if 2 <= k <= 5 else 2
        for j in range(drop):
            (S if stripe else T).px(xx, af + j, 0.52 - 0.10 * j)
    put_tone(L, T, CANVAS, dither=0.3, grain=0.04, seed=seed)
    put_tone(L, S, rmp, dither=0.3)
    SM.shade_box(L, x0 + 2, af + 3, x1 - 2, af + 12, 0.82)
    Po = Tone(L.w, L.h)
    for px_ in (x0 + 2, x1 - 4):
        for yy in range(af + 2, Z1.ROAD_TOP + 2):
            Po.px(px_, yy, 0.56); Po.px(px_ + 1, yy, 0.34)
    put_tone(L, Po, TEAK, dither=0)
    return ab


def stall(L, x, seed=1, kind=0):
    """What is set out under an awning: crates of oranges or tomatoes, or sacks of grain with their tops rolled down."""
    if kind == 0:
        Cr = Tone(L.w, L.h)
        Fr = Tone(L.w, L.h)
        for k, (cx, cyb) in enumerate(((x, BASE + 3), (x + 15, BASE + 3), (x + 7, BASE - 6))):
            SM.crate_tone(Cr, cx, cyb - 9, 14, 9, seed=seed + k)
            for i in range(1, 13, 2):
                Fr.px(cx + i, cyb - 10, 0.72 - 0.2 * (i % 4 == 1))
                Fr.px(cx + i + 1, cyb - 10, 0.54)
                Fr.px(cx + i, cyb - 11, 0.86 * (i % 4 == 3) + 0.40 * (i % 4 != 3))
        put_tone(L, Cr, TEAK, dither=0.3)
        put_tone(L, Fr, FRUIT if seed % 2 else Z1.TOMATO, dither=0)
    else:
        Sk = Tone(L.w, L.h)
        for k in range(3):
            sx = x + k * 9
            for j in range(12):
                for i in range(9):
                    e = ((i - 4) / 4.5) ** 2
                    if e <= 1.0 - 0.3 * (j < 2):
                        Sk.px(sx + i, BASE + 2 - j, 0.70 - 0.30 * abs(i - 3) / 4.5 - 0.10 * (j < 2) + 0.12 * (j == 2))
        put_tone(L, Sk, CANVAS, dither=0.3)
        G = Tone(L.w, L.h)
        for k in range(3):
            for i in range(2, 8):
                G.px(x + k * 9 + i, BASE - 10, 0.60 + 0.2 * ((i + k) % 2))
        put_tone(L, G, GOLD, dither=0)


def souq(L, x0, seed=401):
    """The souq: a terrace of stone houses, shops in their ground floors under awnings of striped canvas, crates of
    fruit and sacks of grain under them, his poster on a wall. x0 local. -> what the level needs."""
    info = {}
    tA, _ = Z2.house(L, x0, 98, 84, seed + 1, floors=1, door=False, roof=('tank',))
    plat('souqroofA', [(wx(x0 + 1), tA - 1), (wx(x0 + 97), tA - 1)])
    tB, dB = Z2.house(L, x0 + 100, 112, 124, seed + 2, floors=2, door=True, roof=('dish',))
    info['door'] = dict(x=wx(dB), y=WALK) if dB is not None else None
    tC, _ = Z2.house(L, x0 + 214, 106, 84, seed + 3, floors=1, door=False)
    plat('souqroofC', [(wx(x0 + 215), tC - 1), (wx(x0 + 319), tC - 1)])
    shops = [(x0 + 6, 42, True), (x0 + 50, 42, False), (x0 + 220, 44, True), (x0 + 268, 44, True)]
    for k, (sx, sw, op) in enumerate(shops):
        Z2.shopfront(L, sx, sw, seed=seed + 10 + k, open_=op)
    aw = [(x0 + 2, x0 + 96, CANRED), (x0 + 216, x0 + 318, CANGRN)]
    for k, (a0, a1, rmp) in enumerate(aw):
        ab = awning(L, a0, a1, rmp, seed=seed + 20 + k)
        plat('souqawn%d' % (k + 1), [(wx(a0 + 1), ab + 1), (wx(a1 - 1), ab + 1)])
    for k, (sx, kind) in enumerate(((x0 + 10, 0), (x0 + 58, 1), (x0 + 226, 1), (x0 + 276, 0))):
        stall(L, sx, seed=seed + 30 + k, kind=kind)
    info['posters'] = [Z1.poster(L, x0 + 150, BASE - 48, 'face', seed=seed + 40)]
    info['x0'], info['x1'] = wx(x0), wx(x0 + 320)
    return info


# ------------------------------------------------------------------ Dar al-Izz
def arch(T, x, y_base, w, h, t=0.10):
    """An arched opening into T: straight sides, a round head."""
    r_ = w / 2.0
    for yy in range(y_base - h, y_base):
        for xx in range(x, x + w):
            dy = (y_base - h + r_) - yy
            if dy > 0:
                dx = xx + 0.5 - (x + r_)
                if dx * dx + dy * dy > r_ * r_:
                    continue
            T.px(xx, yy, t + 0.04 * ((xx + yy) % 5 == 0))


def jagged(x0, x1, y_lo, y_hi, seed, flat=None):
    """A broken wall top: -> its height column by column (between y_lo and y_hi), level along `flat` (x0, x1, y)."""
    w = x1 - x0
    n = noise((1, w), seed, 3, 0.5)[0]
    m = noise((1, w), seed + 1, 14, 0.5)[0]
    top = y_lo + (y_hi - y_lo) * np.clip(0.65 * m + 0.35 * n, 0, 1)
    top = np.round(top).astype(int)
    if flat:
        fx0, fx1, fy = flat
        top[max(0, fx0 - x0):max(0, fx1 - x0)] = fy
    return top


def wall_block(L, x0, x1, top, seed, base=BASE, rows=(), band_ys=(), sky=0.0):
    """A stretch of the palace's wall: old stone in courses from `base` up to its broken top (column by column), with
    rows of arched windows (dark inside, or open to the sky through the roofless rooms), white bands of carved plaster
    worn to the stone. rows: [(y_base, w, h, spacing, x_offset)]."""
    w = x1 - x0
    hmax = base - int(top.min())
    P = Layer(w, hmax + 2)
    STZ.ashlar(P, 0, 0, w, hmax + 2, OLDSTONE, seed=seed, course=7, block=(10, 24), base=0.54, rough=0.16)
    # cut it to the broken top
    for i in range(w):
        cut = int(top[i]) - (base - hmax)
        if cut > 0:
            P.a[:cut, i] = False
    # the broken edge itself: a lit rim
    for i in range(w):
        y = int(top[i]) - (base - hmax)
        if 0 <= y < P.h:
            P.rgb[y, i] = (np.minimum(255, P.rgb[y, i].astype(int) + 40)).astype(np.uint8)
    L.paste(P, x0, base - hmax)
    for yb in band_ys:
        Bd = Tone(L.w, L.h)
        for xx in range(x0, x1):
            if yb >= top[xx - x0] + 2 and hash_(xx, yb) > 0.18:
                for j in range(3):
                    Bd.px(xx, yb + j, 0.82 - 0.14 * j - 0.08 * ((xx // 3) % 2 == 0 and j == 1))
        put_tone(L, Bd, LIME, dither=0.3)
    D = Tone(L.w, L.h)
    for (yb, aw, ah, sp, off) in rows:
        for ax in range(x0 + off, x1 - aw, sp):
            if yb - ah > top[min(w - 1, ax - x0 + aw // 2)] + 3:
                arch(D, ax, yb, aw, ah)
    put_tone(L, D, SOOT, dither=0)
    if sky:
        # some of the upper windows look through the roofless rooms to the sky
        for (yb, aw, ah, sp, off) in rows[-1:]:
            for k, ax in enumerate(range(x0 + off, x1 - aw, sp)):
                if k % 2 == 0 and yb - ah > top[min(w - 1, ax - x0 + aw // 2)] + 3:
                    for yy in range(yb - ah + aw // 2, yb - 1):
                        for xx in range(ax + 1, ax + aw - 1):
                            L.a[yy, xx] = False


def rubble(L, x0, x1, top_y, seed=1):
    """Fallen stones heaped against the wall: blocks of all sizes at all angles, lit from the left. -> the heap's top,
    column by column."""
    r = rng(seed)
    w = x1 - x0
    xs = np.arange(w)
    prof = top_y + (BASE + 2 - top_y) * (np.abs(xs - w / 2.0) / (w / 2.0)) ** 1.6
    prof = np.round(prof).astype(int)
    T = Tone(L.w, L.h)
    for i in range(w):
        for y in range(int(prof[i]), BASE + 3):
            T.px(x0 + i, y, 0.40 + 0.10 * (hash_(x0 + i, y) - 0.5))
    for k in range(int(w * 1.2)):
        bx = x0 + int(r.integers(0, w))
        i = bx - x0
        by = int(r.integers(int(prof[i]), BASE + 3))
        bw, bh = int(r.integers(4, 11)), int(r.integers(3, 6))
        t0 = r.uniform(0.44, 0.66)
        for yy in range(by - bh, by):
            for xx in range(bx - bw // 2, bx + bw // 2):
                j = xx - x0
                if 0 <= j < w and yy >= prof[j]:
                    T.px(xx, yy, t0 + 0.14 * (yy == by - bh) + 0.08 * (xx == bx - bw // 2) - 0.14 * (yy == by - 1) - 0.08 * (xx == bx + bw // 2 - 1))
    put_tone(L, T, OLDSTONE, dither=0.35)
    return prof


def palace(L, x0, seed=431):
    """Dar al-Izz, Queen Arwa's palace, in ruins (its walls still stand in Jibla, roofless): a tall corner of five storeys
    of arched windows, its top broken; the long front, lower, its broken top level enough in one place to stand on, a
    great arched gateway into the dark at its foot; a low last stretch with fallen stones heaped against it. x0 local.
    -> what the level needs."""
    info = {}
    # the tall corner
    tw0, tw1 = x0, x0 + 58
    ttop = jagged(tw0, tw1, 58, 76, seed + 1)
    wall_block(L, tw0, tw1, ttop, seed + 2, rows=[(160, 10, 18, 22, 8), (128, 10, 16, 22, 8), (98, 10, 16, 22, 8), (72, 9, 12, 22, 9)],
               band_ys=(134, 104, 78), sky=1)
    # the long front: broken between 92 and 116, level at 100 for a stretch (a man can stand there)
    fw0, fw1 = x0 + 58, x0 + 196
    ftop = jagged(fw0, fw1, 92, 118, seed + 3, flat=(x0 + 92, x0 + 150, 100))
    wall_block(L, fw0, fw1, ftop, seed + 4, rows=[(132, 10, 16, 20, 6)], band_ys=(140, 112), sky=0)
    plat('ruinwall', [(wx(x0 + 93), 99), (wx(x0 + 149), 99)])
    # the gateway into the dark
    G = Tone(L.w, L.h)
    gx = x0 + 110
    arch(G, gx, BASE, 24, 40, t=0.06)
    put_tone(L, G, SOOT, dither=0)
    Gf = Tone(L.w, L.h)
    for yy in range(BASE - 40, BASE):
        Gf.px(gx - 1, yy, 0.86); Gf.px(gx + 24, yy, 0.40)
    for xx in range(gx - 2, gx + 26):
        Gf.px(xx, BASE - 41, 0.84)
    put_tone(L, Gf, OLDSTONE, dither=0)
    info['gate'] = dict(x=wx(gx + 12), y=WALK)
    # the low last stretch, and the stones fallen from it
    lw0, lw1 = x0 + 196, x0 + 286
    ltop = jagged(lw0, lw1, 126, 142, seed + 5, flat=(x0 + 204, x0 + 252, 130))
    wall_block(L, lw0, lw1, ltop, seed + 6, rows=[(160, 10, 16, 24, 10)], band_ys=(146,))
    plat('ruinlow', [(wx(x0 + 205), 129), (wx(x0 + 251), 129)])
    prof = rubble(L, x0 + 168, x0 + 244, 152, seed=seed + 7)
    flat = [i for i in range(len(prof)) if prof[i] <= prof.min() + 1]
    plat('rubble', [(wx(x0 + 168 + flat[0]), int(prof.min()) - 1), (wx(x0 + 168 + flat[-1]), int(prof.min()) - 1)])
    rubble(L, x0 - 8, x0 + 30, 160, seed=seed + 8)
    # grass and a fig growing out of the stones
    Gr = Tone(L.w, L.h)
    for xx in range(x0, x0 + 286):
        if hash_(xx, seed) < 0.22:
            for j in range(int(1 + 4 * hash_(xx, seed + 1))):
                Gr.px(xx, BASE - j, 0.44 + 0.08 * j)
    put_tone(L, Gr, Z1.GRASS, dither=0.3)
    Z1.crown(L, x0 + 40, 66, 12, 7, seed + 9, LEAF, blobs=26, rmin=3, rmax=6, dark=0.04)
    info['x0'], info['x1'] = wx(x0), wx(x0 + 286)
    return info
