# stage_long.py - the Strait at full length: the beach, then a coast road far too long to paint as one picture,
# then the battery. The road is one strip that repeats; the beach's last stretch and the battery's first are mixed
# into it, so the three meet without a seam. Sky, far coast and sea are made to wrap, so they can slide for ever.
import numpy as np
from scipy import ndimage as ndi
from paint import *
import props as P
import stage as ST

SW, SH = ST.SW, ST.SH
G_TOP, G_H = ST.G_TOP, ST.G_H
XA = 1500                 # the road's repeating strip starts here
TILE = 936                # two screens of road
NT = 13                   # how many times it repeats
XB = XA + NT * TILE       # where the battery's picture starts
WB = 900
WORLD = XB + WB
ROAD_Y = 184              # the row wheels and feet stand on, on the tarmac
ARENA_Y = 176             # and on the battery's rise
MIX0 = 1340               # the beach starts turning into road here
# halfway along, the road gives out and Salem drives along the beach, then climbs back onto the tarmac
XR1 = XA + 4 * TILE       # the tarmac starts to break up
JW = TILE                 # over a whole length of strip (so the ground's grain runs on unbroken into the next)
XS0 = XR1 + JW            # the sand run starts
NBT = 3                   # its strip, repeated
XS1 = XS0 + NBT * TILE    # and ends
XR2 = XS1 + JW            # back on the road, which runs on to the battery
assert (XB - XR2) % TILE == 0

ASPHALT = ramp(['#17171c', '#2a2a30', '#403f44', '#575456', '#706a66', '#8a8278', '#a69c8c', '#c2b8a2'], 14)
PAINT = ramp(['#8a7a4a', '#b8a868', '#dcd094', '#f2ecc0'], 5)


# ------------------------------------------------------------------ ground that repeats
def _wrapnoise(shape, seed, sx, sy):
    return noise(shape, seed, sx, sy)            # (the painter's noise already wraps at the picture's edges)


def road_shore(w=TILE, seed=121):
    return 137 + 4 * (noise((1, w), seed, 120, 0.5)[0] - 0.5) * 2 + 2 * (noise((1, w), seed + 1, 30, 0.5)[0] - 0.5) * 2


def sand_tone_wrap(h, w, d, seed):
    """As stage.sand_tone, with its mounds wrapped round the strip's ends."""
    yy, xx = np.mgrid[0:h, 0:w]
    depth = np.clip(d / (SH - 137.0), 0, 1)
    H = 1.0 * fbm((h, w), seed + 2, 70, 9, octaves=2) + 0.45 * fbm((h, w), seed + 3, 22, 4, octaves=2)
    r = rng(seed + 40)
    for i in range(int(w / 55)):
        cx, cy = r.uniform(0, w), r.uniform(h * 0.25, h * 1.05)
        rx, ry = r.uniform(26, 70), r.uniform(4, 9)
        dx = (xx - cx + w / 2.0) % w - w / 2.0
        H += r.uniform(0.25, 0.6) * np.exp(-((dx / rx) ** 2 + ((yy - cy) / ry) ** 2))
    Hs = ndi.gaussian_filter(H, (0.8, 2.0), mode='wrap')
    lit = light(Hs, -0.6, -0.8, 1.0)
    lit = lit / (np.percentile(np.abs(lit), 97) + 1e-6)
    hol = fbm((h, w), seed + 4, 30, 5, octaves=2)
    hollow = np.clip(hol - 0.62, 0, 1) * 2.6
    warp = fbm((h, w), seed + 6, 60, 10, octaves=3)
    period = 2.4 + 2.0 * depth
    u = (yy + 0.22 * xx + 26.0 * warp) / period
    rip = np.sin(2 * np.pi * u)
    patch = np.clip((fbm((h, w), seed + 8, 30, 6, octaves=3) - 0.42) * 3.5, 0, 1)
    fine = fbm((h, w), seed + 9, 3.0, 0.6, octaves=2) - 0.5
    t = 0.74 - 0.06 * depth + 0.26 * np.clip(lit, -1.3, 1.3) - 0.34 * hollow
    t += (0.03 + 0.045 * depth) * rip * patch + 0.05 * fine
    far = np.clip(1 - d / 14.0, 0, 1)
    t = t * (1 - 0.55 * far) + 0.84 * 0.55 * far
    return t, depth


def road_tile(w=TILE, seed=131):
    """One length of coast road: shallows, a strip of beach, the tarmac with sand creeping over it, the near verge."""
    h = G_H
    yy, xx = np.mgrid[0:h, 0:w]
    sy = yy + G_TOP
    shore = road_shore(w)[None, :]
    d = sy - shore
    L = Layer(w, h)
    lap = noise((h, w), seed, 16, 0.7)
    wt = 0.78 + 0.10 * (lap - 0.5) + 0.12 * np.clip(1 + d / 9.0, 0, 1)
    n1 = noise((1, w), seed + 1, 18, 0.5)[0][None, :]
    n2 = noise((1, w), seed + 5, 11, 0.5)[0][None, :]
    lace1 = np.abs(d + 7.5 - 3.0 * (n1 - 0.5) * 2) < (0.5 + 0.9 * noise((h, w), seed + 7, 5, 0.5))
    lace2 = np.abs(d + 3.0 - 2.0 * (n2 - 0.5) * 2) < (0.4 + 0.8 * noise((h, w), seed + 8, 4, 0.5))
    wt = np.where(lace1 | lace2, 0.985, wt)
    water = (d < 0) & (d > -13)
    L.put(toned(np.clip(wt, 0, 1), ST.SEA, dither=0.6), water)
    t, depth = sand_tone_wrap(h, w, d, seed)
    sand = d >= 0
    L.put(toned(np.clip(t, 0.08, 1), ST.SAND, dither=0.5), sand)
    wet_w = 4.0 + 3.0 * noise((1, w), seed + 10, 40, 0.5)[0][None, :]
    k = np.clip(1 - d / (wet_w + 0.01), 0, 1)
    wet = (d >= 0) & (d < wet_w)
    wtone = 0.66 + 0.26 * k ** 1.5 + 0.14 * (noise((h, w), seed + 12, 12, 0.6) - 0.5)
    L.put(toned(np.clip(wtone, 0, 1), ST.WET, dither=0.6), wet)
    swash = (d >= -0.5) & (d < 0.8 + 1.2 * noise((h, w), seed + 13, 6, 0.5))
    L.put(toned(np.full((h, w), 0.96), ST.SEA, dither=0.0), swash)

    # ---- the tarmac: a band across the picture, its edges eaten by sand
    top = 169.5 + 1.2 * (noise((1, w), seed + 20, 60, 0.5)[0] - 0.5) * 2
    bot = 198.0 + 1.6 * (noise((1, w), seed + 21, 44, 0.5)[0] - 0.5) * 2
    drift = fbm((h, w), seed + 22, 14, 3.0, octaves=3)
    edge_t = np.clip((sy - top[None, :]) / 5.0, 0, 1)             # 0 on the far edge, 1 five rows in
    edge_b = np.clip((bot[None, :] - sy) / 7.0, 0, 1)
    inside = (sy >= top[None, :]) & (sy <= bot[None, :])
    keep = inside & (drift < 0.30 + 0.62 * np.minimum(edge_t, edge_b))      # sand lies over the edges in tongues
    v = np.clip((sy - top[None, :]) / np.maximum(bot[None, :] - top[None, :], 1), 0, 1)
    grain = fbm((h, w), seed + 23, 1.2, 0.7, octaves=2) - 0.5
    streak = noise((h, w), seed + 24, 40, 0.8) - 0.5
    tone = 0.50 + 0.10 * v + 0.16 * grain + 0.12 * streak
    # two wheel tracks worn dark and smooth
    for cy_, wd in ((178.0, 2.4), (190.5, 3.0)):
        tone -= 0.09 * np.exp(-((sy - cy_) / wd) ** 2)
    # patches where it has been mended, and the cracks nobody mended
    rg = rng(seed + 25)
    for i in range(9):
        px_, py_ = rg.integers(0, w), rg.integers(172, 192)
        pw, ph = rg.integers(14, 40), rg.integers(4, 8)
        dx = (xx - px_ + w // 2) % w - w // 2
        m = (np.abs(dx) < pw // 2) & (np.abs(sy - py_) < ph // 2 + 1)
        tone = np.where(m, tone - 0.13 + 0.04 * grain, tone)
    crack = np.abs(fbm((h, w), seed + 26, 9, 5, octaves=3) - 0.5) < 0.012
    tone = np.where(crack, tone - 0.22, tone)
    tone = np.where(np.abs(sy - top[None, :]) < 1.0, tone - 0.20, tone)      # the far edge in its own shadow
    tone = np.where(np.abs(sy - bot[None, :]) < 1.2, tone + 0.10, tone)      # the near edge catching the light
    RL = Layer(w, h)
    RL.put(toned(np.clip(tone, 0.04, 1), ASPHALT, dither=0.55), keep)
    L.paste(RL)
    # the middle line: short dashes, mostly worn away
    worn = fbm((h, w), seed + 27, 5, 1.5, octaves=2)
    dash = ((xx % 36) < 15) & (np.abs(sy - 184.0) <= 0.6) & keep & (worn > 0.34)
    L.put(toned(0.55 + 0.4 * worn, PAINT, dither=0.4), dash)
    # sand blown along the near verge in thin tails across the tarmac
    tails = (fbm((h, w), seed + 28, 26, 0.7, octaves=2) > 0.74) & keep & (sy > 186)
    L.put(toned(np.clip(t + 0.02, 0, 1), ST.SAND, dither=0.5), tails)
    return L


def beach_shore(w=TILE, seed=141):
    """On the sand run the sea comes right up to where the wheels go."""
    return 158 + 3 * (noise((1, w), seed, 110, 0.5)[0] - 0.5) * 2 + 1.5 * (noise((1, w), seed + 1, 26, 0.5)[0] - 0.5) * 2


def coast_tile(w, shore, tar, seed=151):
    """Coast ground with the sea's edge at `shore` (one value a column) and, where `tar` (0..1 a column) is high, the
    tarmac; where it is low, packed wet sand with two tyre ruts, seaweed along the swash line and shells in the dry."""
    h = G_H
    yy, xx = np.mgrid[0:h, 0:w]
    sy = yy + G_TOP
    shore = np.asarray(shore, dtype=float)[None, :]
    tv = np.clip(np.asarray(tar, dtype=float), 0, 1)[None, :]
    sand_run = 1 - tv
    d = sy - shore
    L = Layer(w, h)
    lap = noise((h, w), seed, 16, 0.7)
    wt = 0.78 + 0.10 * (lap - 0.5) + 0.12 * np.clip(1 + d / 9.0, 0, 1)
    n1 = noise((1, w), seed + 1, 18, 0.5)[0][None, :]
    n2 = noise((1, w), seed + 5, 11, 0.5)[0][None, :]
    lace1 = np.abs(d + 7.5 - 3.0 * (n1 - 0.5) * 2) < (0.5 + 0.9 * noise((h, w), seed + 7, 5, 0.5))
    lace2 = np.abs(d + 3.0 - 2.0 * (n2 - 0.5) * 2) < (0.4 + 0.8 * noise((h, w), seed + 8, 4, 0.5))
    lace3 = np.abs(d + 12.0 - 2.5 * (n1 - 0.5) * 2) < (0.4 + 0.7 * noise((h, w), seed + 9, 5, 0.5)) * sand_run
    wt = np.where(lace1 | lace2 | lace3, 0.985, wt)
    water = (d < 0) & (d > -13 - 9 * sand_run)
    L.put(toned(np.clip(wt, 0, 1), ST.SEA, dither=0.6), water)
    t, depth = sand_tone_wrap(h, w, d, seed)
    sand = d >= 0
    L.put(toned(np.clip(t, 0.08, 1), ST.SAND, dither=0.5), sand)
    wet_w = (4.0 + 3.0 * noise((1, w), seed + 10, 40, 0.5)[0][None, :]) * (1 + 1.6 * sand_run)
    k = np.clip(1 - d / (wet_w + 0.01), 0, 1)
    wet = (d >= 0) & (d < wet_w)
    wtone = 0.66 + 0.26 * k ** 1.5 + 0.14 * (noise((h, w), seed + 12, 12, 0.6) - 0.5)
    L.put(toned(np.clip(wtone, 0, 1), ST.WET, dither=0.6), wet)
    swash = (d >= -0.5) & (d < 0.8 + 1.2 * noise((h, w), seed + 13, 6, 0.5))
    L.put(toned(np.full((h, w), 0.96), ST.SEA, dither=0.0), swash)

    # ---- the sand run: damp packed sand where the wheels go, two ruts, the marks of the tread
    top_s = 170.5 + 1.5 * (noise((1, w), seed + 30, 50, 0.5)[0] - 0.5) * 2
    bot_s = 199.0 + 2.0 * (noise((1, w), seed + 31, 40, 0.5)[0] - 0.5) * 2
    band = (sy >= top_s[None, :]) & (sy <= bot_s[None, :])
    soft_edge = (fbm((h, w), seed + 32, 10, 3.0, octaves=2) < 0.35 + 0.65 * np.minimum(np.clip((sy - top_s[None, :]) / 4.0, 0, 1), np.clip((bot_s[None, :] - sy) / 5.0, 0, 1)))
    broken = fbm((h, w), seed + 36, 24, 6, octaves=3)
    damp = band & soft_edge & (broken >= tv * 1.15 - 0.05)                         # it shows where the tarmac has gone
    wander = 1.4 * np.sin(xx / 47.0 * 2 * np.pi * 0 + xx * (2 * np.pi / w) * 7) + 0.8 * (noise((1, w), seed + 37, 30, 0.5)[0][None, :] - 0.5) * 2
    dt = t - 0.14 + 0.05 * (fbm((h, w), seed + 34, 30, 4, octaves=2) - 0.5)
    for cy_, wd in ((178.0, 2.0), (190.5, 2.6)):
        rut = np.exp(-((sy - cy_ - wander) / wd) ** 2)
        tread = ((xx // 2) % 3 == 0) & (rut > 0.6)
        dt = dt - 0.18 * rut - 0.06 * tread
    L.put(toned(np.clip(dt, 0.05, 1), ST.SAND, dither=0.5), damp)

    # ---- the tarmac, where there still is any: as on the road, its edges eaten by sand, and broken up as tar falls
    top = 169.5 + 1.2 * (noise((1, w), seed + 20, 60, 0.5)[0] - 0.5) * 2
    bot = 198.0 + 1.6 * (noise((1, w), seed + 21, 44, 0.5)[0] - 0.5) * 2
    drift = fbm((h, w), seed + 22, 14, 3.0, octaves=3)
    edge_t = np.clip((sy - top[None, :]) / 5.0, 0, 1)
    edge_b = np.clip((bot[None, :] - sy) / 7.0, 0, 1)
    inside = (sy >= top[None, :]) & (sy <= bot[None, :])
    keep = inside & (drift < 0.30 + 0.62 * np.minimum(edge_t, edge_b)) & (broken < tv * 1.15 - 0.05)
    v = np.clip((sy - top[None, :]) / np.maximum(bot[None, :] - top[None, :], 1), 0, 1)
    grain = fbm((h, w), seed + 23, 1.2, 0.7, octaves=2) - 0.5
    streak = noise((h, w), seed + 24, 40, 0.8) - 0.5
    tone = 0.50 + 0.10 * v + 0.16 * grain + 0.12 * streak
    for cy_, wd in ((178.0, 2.4), (190.5, 3.0)):
        tone -= 0.09 * np.exp(-((sy - cy_) / wd) ** 2)
    rg = rng(seed + 25)
    for i in range(9):
        px_, py_ = rg.integers(0, w), rg.integers(172, 192)
        pw, ph = rg.integers(14, 40), rg.integers(4, 8)
        dx = (xx - px_ + w // 2) % w - w // 2
        m = (np.abs(dx) < pw // 2) & (np.abs(sy - py_) < ph // 2 + 1)
        tone = np.where(m, tone - 0.13 + 0.04 * grain, tone)
    crack = np.abs(fbm((h, w), seed + 26, 9, 5, octaves=3) - 0.5) < 0.012 + 0.02 * sand_run
    tone = np.where(crack, tone - 0.22, tone)
    tone = np.where(np.abs(sy - top[None, :]) < 1.0, tone - 0.20, tone)
    tone = np.where(np.abs(sy - bot[None, :]) < 1.2, tone + 0.10, tone)
    RL = Layer(w, h)
    RL.put(toned(np.clip(tone, 0.04, 1), ASPHALT, dither=0.55), keep)
    L.paste(RL)
    worn = fbm((h, w), seed + 27, 5, 1.5, octaves=2)
    dash = ((xx % 36) < 15) & (np.abs(sy - 184.0) <= 0.6) & keep & (worn > 0.34)
    L.put(toned(0.55 + 0.4 * worn, PAINT, dither=0.4), dash)
    tails = (fbm((h, w), seed + 28, 26, 0.7, octaves=2) > 0.74) & keep & (sy > 186)
    L.put(toned(np.clip(t + 0.02, 0, 1), ST.SAND, dither=0.5), tails)

    # ---- what the sea leaves: seaweed along the swash line, shells and the odd stone in the dry sand
    r = rng(seed + 40)
    C = Layer(w, h)
    for i in range(int(w / 9)):
        cx = int(r.uniform(0, w))
        if r.random() > sand_run[0, cx]:
            continue
        kind = r.random()
        if kind < 0.45:                                              # a clump of weed where the last wave reached
            cy = int(shore[0, cx] - G_TOP + wet_w[0, cx] * r.uniform(0.6, 1.1))
            for j in range(int(r.integers(3, 8))):
                x_, y_ = (cx + int(r.integers(-3, 4))) % w, cy + int(r.integers(-1, 2))
                if 0 <= y_ < h:
                    C.rgb[y_, x_] = (52, 64, 30) if r.random() < 0.6 else (88, 98, 46)
                    C.a[y_, x_] = True
        elif kind < 0.85:                                            # a shell, below the drive line
            y_ = int(r.uniform(bot_s[cx] - G_TOP + 2, h - 2))
            if 0 <= y_ < h:
                C.rgb[y_, cx] = (250, 238, 222) if r.random() < 0.7 else (236, 180, 170)
                C.a[y_, cx] = True
                if r.random() < 0.5 and y_ + 1 < h:
                    C.rgb[y_ + 1, cx] = (150, 120, 96)
                    C.a[y_ + 1, cx] = True
        else:                                                        # a pebble
            y_ = int(r.uniform(bot_s[cx] - G_TOP + 3, h - 3))
            for (ddx, ddy, c) in ((0, 0, (120, 108, 96)), (1, 0, (150, 136, 120)), (0, 1, (70, 60, 54)), (1, 1, (96, 84, 74))):
                x_, yv = (cx + ddx) % w, y_ + ddy
                if 0 <= yv < h:
                    C.rgb[yv, x_] = c
                    C.a[yv, x_] = True
    L.paste(C)
    return L


def sand_run_tile():
    return coast_tile(TILE, beach_shore(TILE), np.zeros(TILE), seed=131)


def _handover(base, new, x_from, x_to, seed, rise=True):
    """base everywhere, new mixed in a dot at a time between x_from and x_to (and wholly beyond, or before if not rise)."""
    m = _mixmask(base.h, base.w, x_from, x_to, seed, rise=rise, fine=True)
    out = Layer(base.w, base.h)
    out.rgb = base.rgb.copy()
    out.a = base.a.copy()
    take = m & new.a
    out.rgb[take] = new.rgb[take]
    out.a = np.where(m, new.a, base.a)
    return out


def sand_joins(road, sand):
    """The strip where the tarmac gives out onto the sand (r2b) and the one where it comes back (b2r). Each is a whole
    length of strip painted from the same grain as the road and the sand run, so either end follows on from its
    neighbour with no seam: only the sea's edge and how much tarmac is left change, smoothly, across it."""
    u = np.arange(TILE) / float(TILE - 1)
    sm = u * u * (3 - 2 * u)
    rs, bs = road_shore(), beach_shore()
    r2b = coast_tile(TILE, rs * (1 - sm) + bs * sm, np.clip(1.0 - 1.3 * sm, 0, 1), seed=131)
    b2r = coast_tile(TILE, bs * (1 - sm) + rs * sm, np.clip(1.3 * sm - 0.3, 0, 1), seed=131)
    return r2b, b2r


def strips():
    """How the ground and the foreground are laid along the stage: (picture, x, width, y, until) as the game reads them."""
    FR0, FR1 = 2400, int(XB * 1.25)
    FB0, FB1 = FR0 + 4 * 1170, FR0 + 8 * 1170
    play = [('play_a', 0, XA, 0, None), ('road', XA, TILE, G_TOP, XR1), ('r2b', XR1, JW, G_TOP, None), ('sand', XS0, TILE, G_TOP, XS1),
            ('b2r', XS1, JW, G_TOP, None), ('road', XR2, TILE, G_TOP, XB), ('play_b', XB, WB, 0, None)]
    fore = [('fore', 0, 2340, 150, None), ('fore_road', FR0, 1170, 84, FB0), ('fore_sand', FB0, 1170, 84, FB1),
            ('fore_road', FB1, 1170, 84, FR1), ('fore_b', FR1, 1125, 150, None)]
    return play, fore


def _mixmask(h, w, x_from, x_to, seed, rise=True, fine=False):
    """A hand-over between two pictures: 0 before x_from, 1 after x_to. Ragged tongues in between, or (fine) a
    scatter of single dots, which is how two stretches of the same sand are joined without the join showing."""
    yy, xx = np.mgrid[0:h, 0:w]
    ramp_ = np.clip((xx - x_from) / float(max(1, x_to - x_from)), 0, 1)
    if not rise:
        ramp_ = 1 - ramp_
    if fine:
        n = rng(seed).random((h, w))
        m = ramp_ > 0.08 + 0.84 * n
    else:
        n = fbm((h, w), seed, 22, 3.0, octaves=3)
        m = (ramp_ + 0.55 * (n - 0.5)) > 0.5
    m |= ramp_ >= 1
    m &= ramp_ > 0
    return m


def _join(h, w, x_from, x_to, shore_a, shore_b, seed, rise=True):
    """Where to take picture B instead of picture A across a join. Down on the sand the two are mixed a dot at a time;
    along the water's edge, where a scatter of dots would show, the change is made at the one column where the two
    shorelines agree."""
    yy, xx = np.mgrid[0:h, 0:w]
    sy = yy + G_TOP
    xs = np.arange(x_from, x_to)
    diff = np.abs(shore_a[xs] - shore_b[xs])
    xc = int(xs[int(np.argmin(diff))])
    fine = _mixmask(h, w, x_from, x_to, seed, rise=rise, fine=True)
    hard = (xx >= xc) if rise else (xx < xc)
    top = np.maximum(shore_a, shore_b)[None, :] + 9
    return np.where(sy < top, hard, fine), xc, float(diff.min())


def ramp_index_any(rgb, rmp):
    return P.ramp_index(rgb, rmp) >= 0


def road_strip(tile, x0, x1):
    """The repeating strip laid out between two stage positions (x0 may fall anywhere along it)."""
    w = x1 - x0
    out = Layer(w, tile.h)
    cols = (np.arange(x0, x1) - XA) % tile.w
    out.rgb = tile.rgb[:, cols].copy()
    out.a = tile.a[:, cols].copy()
    return out


# ------------------------------------------------------------------ the beach, handing over to the road
def beach(tile):
    play, info = ST.play_layer(battery=False)
    A = play.crop(0, 0, XA, SH)
    road = road_strip(tile, 0, XA)
    # sand into sand a dot at a time over a long stretch; the tarmac comes out from under it in tongues, later
    cols = (np.arange(0, XA) - XA) % tile.w
    m, xc, gap = _join(G_H, XA, MIX0 - 60, XA - 30, ST.shore_line()[:XA], road_shore()[cols], 301)
    info_join = (xc, gap)
    tar = (ramp_index_any(road.rgb, ASPHALT) | ramp_index_any(road.rgb, PAINT)) & road.a
    m &= ~tar | _mixmask(G_H, XA, MIX0 + 40, XA - 24, 305)
    sub = A.crop(0, G_TOP, XA, SH)
    # nothing that stands on the beach is painted over: only its ground
    ground = ST.ground_layer()
    g = ground.crop(0, 0, XA, G_H)
    is_ground = (sub.rgb == g.rgb).all(axis=2) | ~sub.a
    take = m & road.a & is_ground
    A.rgb[G_TOP:, :][take] = road.rgb[take]
    A.a[G_TOP:, :] |= take
    info = dict(info, join=info_join)
    return A, info


# ------------------------------------------------------------------ the battery at the road's end
def barrier(seed=1):
    """A pole across the road on two drums, striped, with a hand painted on a board: the battery's front gate."""
    W, Hh = 66, 40
    L = Layer(W, Hh)
    for i, (x, pnt) in enumerate(((4, 'oxide'), (48, 'blue'))):
        dr, f = P.drum(pnt, seed=seed + i)
        L.paste(dr, x, Hh - 1 - f)
    T = Tone(W, Hh)
    R = Tone(W, Hh)
    for x in range(0, W):
        C = R if (x // 6) % 2 == 0 else T
        C.rect(x, 12, x, 14, 0.78)
        C.px(x, 12, 0.96)
        C.px(x, 15, 0.34)
    L.paste(T.layer(P.BOATWHITE, dither=0.2))
    L.paste(R.layer(P.REDP, dither=0.2))
    B = Tone(W, Hh)
    B.rect(26, 0, 39, 11, 0.86)
    B.rect(26, 0, 39, 0, 0.98)
    B.rect(39, 0, 39, 11, 0.60)
    L.paste(B.layer(P.BOATWHITE, dither=0.2))
    hand = ['..#.#.#...', '..#.#.#.#.', '..#.#.#.#.', '#.#####.#.', '#########.', '.########.', '..######..', '...####...']
    for j, row in enumerate(hand):
        for i, ch in enumerate(row):
            if ch == '#':
                L.rgb[2 + j, 28 + i] = (190, 52, 24)
    return P.outlined(L), Hh


def battery(tile):
    """The lava rise: the road runs out at a barrier, and beyond it the launcher under its net, the dish, the tower."""
    w = WB
    old_shore, old_walk = ST.shore_line, ST.walk_line

    def shore_b(w_=w, seed=21):
        x = np.arange(w_)
        base = 137 + 5 * (noise((1, w_), 77, 140, 0.5)[0] - 0.5) * 2 + 2 * (noise((1, w_), 78, 30, 0.5)[0] - 0.5) * 2
        return base - 7 * np.exp(-((x - 520) / 240.0) ** 2)

    ST.shore_line = shore_b
    shore_here = shore_b()
    try:
        g = ST.ground_layer(w=w, seed=331)
    finally:
        ST.shore_line, ST.walk_line = old_shore, old_walk
    play = Layer(w, SH)
    play.paste(g, 0, G_TOP)
    # the road comes in from the left and gives out
    road = road_strip(tile, XB, XB + w)
    xx_ = np.mgrid[0:G_H, 0:w][1]
    cols = (np.arange(XB, XB + w) - XA) % tile.w
    m, xc, gap = _join(G_H, w, 150, 330, road_shore()[cols], shore_here, 303, rise=False)
    m = m | (xx_ < 150)
    tar = (ramp_index_any(road.rgb, ASPHALT) | ramp_index_any(road.rgb, PAINT)) & road.a
    m &= ~tar | _mixmask(G_H, w, 150, 250, 307, rise=False) | (xx_ < 150)
    take = m & road.a
    play.rgb[G_TOP:, :][take] = road.rgb[take]
    play.a[G_TOP:, :] |= take
    items = []

    def add(piece, x, base_y, floor, **kw):
        items.append((base_y, piece, x, floor, kw))

    for i, (x, by, w_, h_) in enumerate([(262, 164, 60, 34), (318, 170, 36, 18), (372, 160, 46, 28), (806, 168, 54, 30), (852, 180, 30, 16), (446, 162, 30, 15)]):
        rk, f = P.rock(w_, h_, seed=30 + i)
        add(rk, x, by, f, bury=2, seed=i)
    ds, f = P.dish()
    add(ds, 400, 160, f)
    wt, f, plat = P.watchtower()
    tower_x, tower_base = 640, 170
    add(wt, tower_x, tower_base, f)
    cn, f = P.camo_net(w=132, h=40, seed=3)
    add(cn, 490, 170, f, shadow=False)
    fl, f = P.flag()
    add(fl, 700, 170, f)
    pm5, f, bx = P.palm(height=70, lean=6, seed=13)
    add(pm5, 744, 150, f)
    pm6, f, bx = P.palm(height=84, lean=-8, seed=17)
    add(pm6, 196, 152, f)
    old_sh = ST._shadow_on
    for base_y, piece, x, floor, kw in sorted(items, key=lambda t_: t_[0]):
        ST.put(play, piece, x, base_y, floor, **kw)
    info = dict(tower=(tower_x, tower_base - (wt.h - 1 - plat)), tower_w=wt.w, launcher=(522, ARENA_Y - 4), barrier=(196, ROAD_Y - 2), net=(490, 170), join=(xc, gap))
    return play, info


# ------------------------------------------------------------------ the ground's height along the whole stage
def ground_profile(old):
    """old: the beach's measured walk line (one value every 4 px). Returns the same for the whole stage."""
    n = WORLD // 4 + 1
    y = np.zeros(n)
    for i in range(n):
        x = i * 4
        if x < MIX0:
            y[i] = old[min(i, len(old) - 1)]
        elif x < XA:
            u = (x - MIX0) / float(XA - MIX0)
            u = u * u * (3 - 2 * u)
            y[i] = old[min(i, len(old) - 1)] * (1 - u) + ROAD_Y * u
        elif x < XB + 190:
            y[i] = ROAD_Y
        elif x < XB + 300:
            u = (x - XB - 190) / 110.0
            u = u * u * (3 - 2 * u)
            y[i] = ROAD_Y * (1 - u) + ARENA_Y * u
        else:
            y[i] = ARENA_Y
    return [round(float(v), 1) for v in y]


# ------------------------------------------------------------------ sky, far coast and sea that wrap
def puffs_wrap(h, w, clouds, seed):
    r = rng(seed)
    Z = np.zeros((h, w))
    yy, xx = np.mgrid[0:h, 0:w]
    for cx, base, width, height, n, rmin, rmax in clouds:
        for i in range(n):
            u = r.uniform(-1, 1)
            u = np.sign(u) * abs(u) ** 1.3
            x = (cx + u * width / 2) % w
            top = base - height * (1 - abs(u) ** 1.7) * r.uniform(0.55, 1.0)
            y = base - (base - top) * r.uniform(0.0, 1.0) ** 0.6
            rad = r.uniform(rmin, rmax) * (1 - 0.45 * abs(u))
            dx = (xx - x + w / 2.0) % w - w / 2.0
            near = np.abs(dx) <= rad + 1
            if not near.any():
                continue
            d2 = dx ** 2 + ((yy - y) * 1.25) ** 2
            z = np.sqrt(np.clip(rad * rad - d2, 0, None))
            z = np.where(yy > base + 1, 0, z)
            Z = np.maximum(Z, z)
    return Z


def sky_wrap(w=1404, seed=3):
    h = ST.HORIZON + 6
    yy = np.arange(h)[:, None] / float(ST.HORIZON)
    xx = np.arange(w)[None, :]
    tone = 0.04 + 0.50 * np.clip(yy, 0, 1) ** 1.25 + 0 * xx
    cir = fbm((h, w), seed, 46, 1.3, octaves=3)
    band = np.exp(-((yy - 0.40) / 0.26) ** 2)
    tone += np.clip(cir - 0.56, 0, 1) * 0.9 * band
    cir2 = fbm((h, w), seed + 5, 90, 2.2, octaves=2)
    tone += np.clip(cir2 - 0.6, 0, 1) * 0.5 * np.exp(-((yy - 0.7) / 0.2) ** 2)
    far = [(x, ST.HORIZON - 2 + (i % 3), 90 + 30 * (i % 2), 8 + 5 * (i % 3), 46, 2.5, 5.5) for i, x in enumerate(range(10, w, 58))]
    Zf = ndi.gaussian_filter(puffs_wrap(h, w, far, seed + 40), 1.1, mode='wrap')
    covf = np.clip(Zf * 0.55, 0, 1)
    litf = light(Zf, -0.6, -0.8, 0.5)
    tf = 0.66 + 0.16 * np.clip(litf, -1, 1)
    tone = tone + covf * 0.8 * (np.clip(tf, 0.52, 0.84) - tone)
    big = [(96, 88, 150, 64, 170, 4.0, 11.0), (300, 93, 110, 34, 90, 3.5, 8.0), (470, 90, 180, 54, 170, 4.0, 10.0), (668, 93, 120, 30, 90, 3.5, 8.0),
           (880, 89, 170, 58, 170, 4.0, 11.0), (1080, 93, 120, 32, 90, 3.5, 8.0), (1262, 90, 170, 48, 160, 4.0, 10.0)]
    Z = puffs_wrap(h, w, big, seed + 41)
    Zs = ndi.gaussian_filter(Z, 0.7, mode='wrap')
    cov = np.clip(Z * 0.8, 0, 1)
    lit = light(Zs, -0.55, -0.85, 0.5)
    floor = np.zeros((h, w))
    for cx, base, width, height, n, r0, r1 in big:
        dx = (xx - cx + w / 2.0) % w - w / 2.0
        f = np.clip(1 - (base - np.arange(h)[:, None]) / (height * 0.6), 0, 1) * (np.abs(dx) < width * 0.62)
        floor = np.maximum(floor, f)
    shade = noise((h, w), seed + 50, 22, 12)
    ct = 0.74 + 0.46 * np.clip(lit, -1, 1) - 0.30 * floor ** 1.5 - 0.14 * (shade - 0.5)
    cov = cov * (1 - 0.55 * floor ** 3)
    tone = tone + cov * (np.clip(ct, 0.30, 1.0) - tone)
    L = Layer(w, h)
    L.put(toned(tone, ST.SKY, dither=0.7), np.ones((h, w), bool))
    return L


def _frigate(T, x, wl, length=120):
    """A grey warship standing off the coast, bow to the right: somebody on our side is watching."""
    top = wl - 6
    T.poly([(x, top), (x + length - 14, top), (x + length, top - 3), (x + length - 6, wl), (x + 4, wl)], 0.50)
    T.rect(x + 4, wl - 1, x + length - 7, wl, 0.34)
    T.rect(x + 2, top, x + length - 12, top, 0.70)
    T.rect(x + 30, top - 8, x + 74, top - 1, 0.62)                    # the house
    T.rect(x + 30, top - 8, x + 74, top - 8, 0.80)
    T.rect(x + 40, top - 13, x + 62, top - 8, 0.66)
    T.rect(x + 40, top - 13, x + 62, top - 13, 0.84)
    for px_ in range(x + 34, x + 72, 4):
        T.px(px_, top - 4, 0.36)
    T.rect(x + 50, top - 25, x + 50, top - 13, 0.50)                  # mast
    T.rect(x + 46, top - 21, x + 54, top - 21, 0.50)
    T.rect(x + 48, top - 17, x + 52, top - 16, 0.56)
    T.rect(x + 66, top - 16, x + 71, top - 8, 0.52)                   # funnel
    T.rect(x + 66, top - 16, x + 71, top - 15, 0.34)
    T.rect(x + 86, top - 4, x + 92, top - 1, 0.60)                    # the gun
    T.rect(x + 92, top - 3, x + 101, top - 3, 0.48)
    T.rect(x + 12, top - 3, x + 22, top - 1, 0.58)                    # the pad aft
    T.rect(x + 8, top - 9, x + 8, top - 1, 0.50)                      # ensign staff


def far_wrap(w=2808, seed=7):
    h, wl = ST.FAR_H, ST.FAR_WATER
    yy, xx = np.mgrid[0:h, 0:w]
    L = Layer(w, h)
    for i, (seed_i, amp, sx, t0) in enumerate([(seed, 20, 110, 0.90), (seed + 9, 12, 70, 0.80)]):
        top = ST._ridge(w, seed_i, wl - 2, amp, sx)
        fade = np.clip(np.sin(2 * np.pi * np.arange(w) / w * 3 + i * 1.3) * 0.5 + 0.7, 0.15, 1)
        top = wl - (wl - top) * fade
        m = (yy >= top[None, :]) & (yy < wl)
        tone = t0 + 0.07 * np.clip((yy - top[None, :]) / 12.0, 0, 1) + 0.03 * (noise((h, w), seed_i + 3, 6, 2) - 0.5)
        L.put(toned(np.clip(tone, 0, 1), ST.HAZE2, dither=0.6), m)
    T = Tone(w, h)
    prof = np.full(w, float(wl))

    def island(ix0, width, height, sd):
        xs = np.arange(ix0, ix0 + width)
        u = (xs - ix0) / float(width)
        hill = height * np.sin(np.pi * u) ** 0.7 * (0.55 + 0.45 * np.sin(u * 7.0 + 0.6) ** 2)
        hill += 3 * noise((1, len(xs)), sd, 4, 0.5)[0]
        prof[ix0:ix0 + width] = np.minimum(prof[ix0:ix0 + width], wl - hill)

    island(540, 300, 30, seed + 20)              # Perim, with its light
    island(1690, 380, 22, seed + 60)             # the headland before the battery
    m = (yy >= prof[None, :]) & (yy < wl)
    strata = noise((h, w), seed + 21, 10, 1.2)
    facets = noise((h, w), seed + 22, 3, 5)
    lit = light(ndi.gaussian_filter(facets, 1.0), -0.8, -0.5, 6.0)
    depth = np.clip((yy - prof[None, :]) / 22.0, 0, 1)
    tone = 0.46 + 0.16 * np.clip(lit, -1, 1) + 0.10 * (strata - 0.5) + 0.16 * depth
    tone = np.where((yy - prof[None, :]) < 1.5, tone + 0.22, tone)
    T.mask(m, 0)
    T.t = np.where(m, tone, T.t)
    lx = 540 + 160
    ly = int(prof[lx]) + 1
    for i in range(26):
        yb = ly - i
        half = 3 if i < 5 else 2
        band = (i // 5) % 2
        T.rect(lx - half, yb, lx + half, yb, 0.88 if band else 0.40)
        T.px(lx - half, yb, 0.96 if band else 0.52)
        T.px(lx + half, yb, 0.70 if band else 0.30)
    T.rect(lx - 4, ly - 27, lx + 4, ly - 26, 0.34)
    T.rect(lx - 2, ly - 31, lx + 2, ly - 28, 0.94)
    T.rect(lx - 2, ly - 30, lx + 2, ly - 30, 0.50)
    T.rect(lx - 3, ly - 32, lx + 3, ly - 32, 0.36)
    T.rect(lx - 1, ly - 34, lx + 1, ly - 33, 0.36)
    T.rect(lx, ly - 37, lx, ly - 35, 0.40)
    T.rect(lx + 7, ly - 6, lx + 22, ly, 0.84)
    T.rect(lx + 7, ly - 7, lx + 22, ly - 7, 0.94)
    for px_ in (lx + 10, lx + 14, lx + 18):
        T.rect(px_, ly - 4, px_, ly - 3, 0.38)
    T.rect(lx - 30, ly + 2, lx - 18, ly + 6, 0.80)
    T.rect(lx - 30, ly + 1, lx - 18, ly + 1, 0.92)
    T.rect(lx - 27, ly + 3, lx - 26, ly + 6, 0.36)
    T.rect(lx - 22, ly + 3, lx - 21, ly + 6, 0.36)
    ST._tanker(T, 96, wl)
    ST._boxship(T, 372, wl)
    ST._dhow(T, 880, wl)
    _frigate(T, 1120, wl)
    ST._dhow(T, 1420, wl)
    ST._dhow(T, 1500, wl - 0)
    ST._boxship(T, 2130, wl, length=150)
    ST._dhow(T, 2380, wl)
    ST._tanker(T, 2540, wl, length=190)
    L.paste(T.layer(ST.HAZE2, dither=0.5, grain=0.05, seed=seed + 30))
    return L


def _fold(layer, lap=64, seed=5):
    """Make a strip wrap: its last `lap` columns are mixed into its first, and the strip is cut that much shorter."""
    w = layer.w - lap
    out = Layer(w, layer.h)
    out.rgb = layer.rgb[:, :w].copy()
    out.a = layer.a[:, :w].copy()
    n = fbm((layer.h, lap), seed, 6, 2, octaves=2)
    ramp_ = np.arange(lap)[None, :] / float(lap)
    tail = (ramp_ + 0.5 * (n - 0.5)) < 0.5                     # near x = 0 the picture is the old tail, so it follows on from the end
    out.rgb[:, :lap][tail] = layer.rgb[:, w:][tail]
    return out


def sea_wrap():
    return _fold(ST.sea_layer())


# ------------------------------------------------------------------ what passes close to the lens
def fore_road(w=1170, seed=61):
    """Along the road: stones and scrub on the near verge, and now and then a pole, close enough to blur by."""
    L = Layer(w, SH)
    for i, (x, w_, h_) in enumerate([(40, 34, 16), (300, 22, 11), (512, 50, 22), (560, 20, 10), (860, 30, 14), (1040, 44, 20)]):
        rk, f = P.rock(w_, h_, seed=90 + i, sharp=0.9)
        P.shade(rk, rk.a, P.ROCK, -2)
        L.paste(rk, x, SH - h_ + 5)
    T = Tone(w, SH)
    for px_, top in ((214, 92), (800, 104)):
        T.rect(px_, top, px_ + 3, SH - 1, 0.30)
        T.rect(px_, top, px_, SH - 1, 0.62)
        T.rect(px_ - 9, top + 6, px_ + 12, top + 7, 0.36)
        T.rect(px_ - 9, top + 6, px_ + 12, top + 6, 0.58)
        for dx in (-8, 11):
            T.rect(px_ + dx, top + 3, px_ + dx, top + 5, 0.70)
    L.paste(T.layer(P.DRIFT, dither=0.3))
    # dry scrub: a few tufts
    S = Tone(w, SH)
    r = rng(seed)
    for cx in (130, 430, 700, 960, 1120):
        for k in range(14):
            a = r.uniform(-2.6, -0.5)
            ln = r.uniform(6, 15)
            S.line([(cx + r.uniform(-5, 5), SH - 1), (cx + np.cos(a) * ln, SH - 1 + np.sin(a) * ln)], r.uniform(0.25, 0.6))
    L.paste(S.layer(P.PALM, dither=0.3))
    return L


def fore_sand(w=1170, seed=71):
    """Along the sand run: driftwood, a tangle of net, weed and dune grass close to the lens; no poles out here."""
    L = Layer(w, SH)
    T = Tone(w, SH)
    for (x, ln, th) in ((90, 46, 4), (610, 30, 3), (980, 58, 5)):          # driftwood logs
        T.rect(x, SH - th - 2, x + ln, SH - 3, 0.40)
        T.rect(x, SH - th - 2, x + ln, SH - th - 2, 0.70)
        T.rect(x + ln // 3, SH - th - 5, x + ln // 3 + 1, SH - th - 2, 0.50)
    L.paste(T.layer(P.DRIFT, dither=0.3))
    for i, (x, w_, h_) in enumerate([(380, 26, 12), (820, 18, 9)]):
        rk, f = P.rock(w_, h_, seed=130 + i, sharp=0.9)
        P.shade(rk, rk.a, P.ROCK, -2)
        L.paste(rk, x, SH - h_ + 4)
    S = Tone(w, SH)
    r = rng(seed)
    for cx in (40, 300, 520, 760, 1100):
        for k in range(12):
            a = r.uniform(-2.4, -0.7)
            ln = r.uniform(5, 13)
            S.line([(cx + r.uniform(-5, 5), SH - 1), (cx + np.cos(a) * ln, SH - 1 + np.sin(a) * ln)], r.uniform(0.3, 0.65))
    L.paste(S.layer(P.PALM, dither=0.3))
    return L


def fore_battery(w=1125):
    L = Layer(w, SH)
    for i, (x, w_, h_) in enumerate([(120, 60, 28), (470, 30, 15), (900, 64, 30), (1060, 40, 18)]):
        rk, f = P.rock(w_, h_, seed=110 + i, sharp=0.9)
        P.shade(rk, rk.a, P.ROCK, -2)
        L.paste(rk, x, SH - h_ + 6)
    return L


_CACHE = {}


def build():
    if not _CACHE:
        tile = road_tile()
        A, info = beach(tile)
        B, binfo = battery(tile)
        sand = sand_run_tile()
        r2b, b2r = sand_joins(tile, sand)
        _CACHE.update(tile=tile, play_a=A, info=info, play_b=B, binfo=binfo, sky=sky_wrap(), far=far_wrap(), sea=sea_wrap(),
                      fore=ST.foreground_layer(), fore_road=fore_road(), fore_b=fore_battery(),
                      sand=sand, r2b=r2b, b2r=b2r, fore_sand=fore_sand())
    return _CACHE


def compose(cam, S=None, w=SW):
    """One screen of the long stage at camera x, for looking at."""
    S = S or build()
    out = Layer(w, SH)

    def wrap(L, par, y):
        x = int(cam * par) % L.w
        out.paste(L, -x, y)
        out.paste(L, L.w - x, y)

    wrap(S['sky'], 0.2, 0)
    wrap(S['sea'], 0.6, ST.HORIZON)
    wrap(S['far'], 0.35, ST.FAR_TOP)
    play, fore = strips()
    pics = dict(play_a=S['play_a'], road=S['tile'], r2b=S['r2b'], sand=S['sand'], b2r=S['b2r'], play_b=S['play_b'],
                fore=S['fore'], fore_road=S['fore_road'], fore_sand=S['fore_sand'], fore_b=S['fore_b'])
    for lay, x0 in ((play, int(cam)), (fore, int(cam * 1.25))):
        for name, x, tw, y, until in lay:
            pic = pics[name]
            end = until if until is not None else x + tw
            if end <= x0 or x >= x0 + w:
                continue
            k = max(0, (x0 - x) // tw) if until is not None else 0
            tx = x + k * tw
            while tx < end and tx < x0 + w:
                part = pic if tx + tw <= end else pic.crop(0, 0, end - tx, pic.h)
                out.paste(part, tx - x0, y if name not in ('play_a', 'play_b') else 0)
                tx += tw
    return out


if __name__ == '__main__':
    import sys, os
    S = build()
    cams = [XR1 - 300, XR1 + 60, XR1 + 300, XS0 + 200, XS1 - 200, XS1 + 100, XS1 + 360, XR2 + 100]
    sheet = Layer(SW * 2 + 6, (SH + 6) * 4)
    sheet.rgb[:] = (20, 16, 24)
    sheet.a[:] = True
    for i, c in enumerate(cams):
        sheet.paste(compose(c, S), (i % 2) * (SW + 6), (i // 2) * (SH + 6))
    im = sheet.image()
    im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
    out = sys.argv[1] if len(sys.argv) > 1 else 't8_long.png'
    im.save(out)
    print(im.size, 'world', WORLD, 'battery at', XB, S['binfo'])
