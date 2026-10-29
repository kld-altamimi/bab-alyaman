# stage_ibb_z3x.py - the hamlet on the top of the terraces (Khaled, 29 Oct 21:36: "the zones in this mission are a bit
# short"): past the farmhouse, on the last terrace before the relay station, a hamlet of stone houses: a tower house of
# two storeys with its door on the path and a water tank on its roof, a stepped alley up to the flat roof of the house
# beside it, the hamlet's cistern (a birka: a stone tank cut into the terrace, steps down into its green water, its rim
# along the path), a last house with two windows, a sidr tree. Local x, as stage_ibb_z3.py's (world = local + its X0).
import numpy as np
from paint import *
import stage_mocha as SM
import stage_taiz as STZ
import stage_ibb as I
import stage_ibb_z1 as Z1
import stage_ibb_z3 as Z3

SH = I.SH
put_tone, plat, wx, gy = SM.put_tone, I.plat, Z3.wx, Z3.gy
IBBSTONE, BLUEP, TEAK, SOOT, LIME = Z1.IBBSTONE, Z1.BLUEP, SM.TEAK, SM.SOOT, SM.LIME
GREENW = ramp(['#06120e', '#0c2018', '#143024', '#1e4232', '#2a5642', '#3a6c54', '#508468', '#6c9e80'], 14)     # the cistern's water


def hash_(a, b):
    return float(I.hash01(int(a), int(b)))


def stairs_at(L, x0, base, steps, rise=11, run=14, seed=1, up=1):
    """A stepped alley of the hamlet: stone steps climbing from the path (up=1: to the right), each a platform; the flight
    on a wall of coursed stone down to `base`. -> each step's (local x0, x1, y)."""
    T = Tone(L.w, L.h)
    tops = []
    for k in range(steps):
        y = base - 10 - k * rise
        sx0, sx1 = (x0 + k * run, x0 + (k + 1) * run + 4) if up > 0 else (x0 - (k + 1) * run - 4, x0 - k * run)
        tops.append((sx0, sx1, y))
    xs0, xs1 = min(t[0] for t in tops), max(t[1] for t in tops)
    for xx in range(xs0, xs1):
        ys = [t[2] for t in tops if t[0] <= xx < t[1]]
        if not ys:
            continue
        ytop = min(ys)
        for yy in range(ytop, base + 2):
            course = ((yy - ytop) // 5) % 2
            joint = ((yy - ytop) % 5 == 4) or ((xx + 6 * course) % 12 == 0)
            T.px(xx, yy, 0.48 - 0.16 * joint + 0.04 * (((xx * 7 + yy * 3) % 13) == 0) - 0.08 * (yy > base - 6))
    for (sx0, sx1, y) in tops:
        for xx in range(sx0, sx1):
            T.px(xx, y, 0.90); T.px(xx, y + 1, 0.72)
        edge = sx1 - 1 if up > 0 else sx0
        for yy in range(y + 2, y + rise + 2):
            T.px(edge, yy, 0.24)
    put_tone(L, T, IBBSTONE, dither=0.3)
    return tops


def cistern(L, x0, x1, seed=1):
    """The hamlet's birka: a tank of dressed stone sunk in the terrace behind the path, seen over its front rim: the far
    wall's inner face, wet and dark near the water, the green water taking the sky, steps going down into it at the left
    end, the rim along the path (low enough to step up onto). -> the rim's top."""
    back = gy(x0) - 8
    rim = back - 3
    far = rim - 18
    T = Tone(L.w, L.h)
    Wt = Tone(L.w, L.h)
    st = noise((SH, L.w), seed, 1.1, 0.8)
    for xx in range(x0, x1):
        # the far rim, the far wall's inner face (darker and wetter toward the water)
        T.px(xx, far, 0.86); T.px(xx, far + 1, 0.70)
        for yy in range(far + 2, rim - 7):
            d = yy - far
            joint = (d % 5 == 4) or (((xx + 5 * (d // 5)) % 11) == 0)
            T.px(xx, yy, 0.46 - 0.14 * joint - 0.020 * d + 0.08 * (st[yy, xx] - 0.5))
        # the water
        for yy in range(rim - 7, rim):
            v = (yy - (rim - 7)) / 7.0
            Wt.px(xx, yy, 0.40 + 0.30 * v + 0.30 * (st[yy, xx] > 0.74) + 0.10 * ((xx + 3 * yy) % 13 == 0))
        # the front rim: dressed stone, its top lit
        T.px(xx, rim, 0.90); T.px(xx, rim + 1, 0.76)
        for yy in range(rim + 2, back + 2):
            T.px(xx, yy, 0.58 - 0.06 * (yy - rim) + 0.08 * ((xx // 9) % 2 == 0 and yy == rim + 2))
    # the ends of the tank
    for xx in (x0, x0 + 1, x1 - 2, x1 - 1):
        for yy in range(far, back + 2):
            T.px(xx, yy, 0.66 - 0.10 * (xx >= x1 - 2))
    put_tone(L, Wt, GREENW, dither=0.4)
    put_tone(L, T, IBBSTONE, dither=0.3)
    # steps down into it at the left end
    S = Tone(L.w, L.h)
    for k in range(5):
        sy = far + 3 + k * 3
        for xx in range(x0 + 2 + k * 3, x0 + 14 + k * 3):
            S.px(xx, sy, 0.84); S.px(xx, sy + 1, 0.56); S.px(xx, sy + 2, 0.36)
    put_tone(L, S, IBBSTONE, dither=0.2)
    # weed along the rim, a bucket on its rope
    G = Tone(L.w, L.h)
    for xx in range(x0, x1):
        if hash_(xx, seed) < 0.18:
            for j in range(int(1 + 3 * hash_(xx, seed + 1))):
                G.px(xx, rim - 1 - j, 0.46 + 0.10 * j)
    put_tone(L, G, Z1.GRASS, dither=0.3)
    return rim


def hamlet(L, x0, seed=601):
    """The hamlet: a tower house of two storeys (its door on the path; men come out of it), a stepped alley up to the
    flat roof of the one-storey house beside it, the cistern, a last house with two windows, a sidr, his poster. x0
    local. -> what the level needs."""
    info = {}
    base = gy(x0) - 8
    top1, d1 = Z3.house_at(L, x0, base, 62, 76, seed + 1, floors=2, door=True, roof=('tank',))
    info['door'] = dict(x=wx(d1), y=gy(d1)) if d1 is not None else None
    tops = stairs_at(L, x0 + 66, base, 3, rise=11, run=14, seed=seed + 2)
    for k, (s0, s1, sy) in enumerate(tops):
        plat('hamstep%d' % (k + 1), [(wx(s0), sy - 1), (wx(s1 - 1), sy - 1)])
    hx = x0 + 66 + 3 * 14 + 4
    hr, hd = Z3.hut(L, hx, w=66, h=34, seed=seed + 3, windows=2, door=BLUEP)
    plat('hamroof', [(wx(hx), hr), (wx(hx + 65), hr)])
    info['door2'] = dict(x=wx(hd), y=gy(hd)) if hd is not None else None
    cx0 = hx + 76
    rim = cistern(L, cx0, cx0 + 132, seed=seed + 4)
    plat('birkarim', [(wx(cx0 + 2), rim - 1), (wx(cx0 + 129), rim - 1)])
    lx = cx0 + 142
    lr, ld = Z3.hut(L, lx, w=60, h=32, seed=seed + 5, windows=2, door=TEAK)
    plat('lastroof', [(wx(lx), lr), (wx(lx + 59), lr)])
    Z1.sidr(L, lx + 92, base - 1, seed=seed + 6)
    info['posters'] = [Z1.poster(L, x0 + 34, base - 30, 'face', seed=seed + 7)]
    info['cistern'] = [wx(cx0), wx(cx0 + 132)]
    info['x0'], info['x1'] = wx(x0), wx(lx + 120)
    return info
