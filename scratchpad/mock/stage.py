# stage.py - Bab al-Mandab, built the way the arcade builds a stage: a slow painted
# panorama (sky, far coast, shipping), the sea, the ground the squad walks on, set pieces
# standing on it, and a fast foreground. Scenery carries no outlines; only sprites do.
import numpy as np
from scipy import ndimage as ndi
from paint import *
import props as P

SW, SH = 468, 216            # one screen
STAGE_W = 1872               # four screens of ground
HORIZON = 104                # sea meets sky
WALK = 180                   # where feet land on flat sand

# ------------------------------------------------------------------ ramps
SKY = ramp(['#00547c', '#0c6a90', '#2c84a0', '#56a0ac', '#84bcb8', '#aed4c0', '#d2e6c8', '#f0f2d8'], 20)
HAZE = ramp(['#4a8ea0', '#6aa6ac', '#8cbcb8', '#aed0c0', '#cce0c8'], 10)
SEA = ramp(['#021428', '#042c4c', '#064a66', '#0c6c7c', '#1e8c8c', '#48aa98', '#84c8a8', '#c0e2bc', '#eef4dc'], 20)
HAZE2 = ramp(['#1e5a74', '#33708a', '#4c869a', '#6a9ca8', '#88b2b4', '#a8c8c0', '#c8dcc8', '#e2ecd4'], 16)
SAND = ramp(['#241208', '#4c2a14', '#7a4c24', '#a47438', '#c69a54', '#deb870', '#f0d08c', '#fae4ac', '#fff2cc'], 20)
WET = ramp(['#1c1410', '#3c2c20', '#5e4a34', '#806a4c', '#a08c68', '#c0b08c', '#dcd0b0'], 12)
ROCK = ramp(['#0c0a0e', '#221c20', '#3c3232', '#5a4c46', '#7c6a5c', '#a08e78', '#c4b498'], 14)
WOOD = ramp(['#1a0e08', '#3c2212', '#644024', '#8c6238', '#b08a58', '#d0b080', '#ecd8ac'], 14)
RUST = ramp(['#1c0a06', '#3e160c', '#682a12', '#94441c', '#ba6a2c', '#d8944c', '#ecc080'], 14)


def puffs(h, w, clouds, seed):
    """Height field of heaped spheres: each cloud is a mound of small puffs on a flat floor."""
    r = rng(seed)
    Z = np.zeros((h, w))
    yy, xx = np.mgrid[0:h, 0:w]
    for cx, base, width, height, n, rmin, rmax in clouds:
        for i in range(n):
            u = r.uniform(-1, 1)
            u = np.sign(u) * abs(u) ** 1.3
            x = cx + u * width / 2
            top = base - height * (1 - abs(u) ** 1.7) * r.uniform(0.55, 1.0)
            y = base - (base - top) * r.uniform(0.0, 1.0) ** 0.6
            rad = r.uniform(rmin, rmax) * (1 - 0.45 * abs(u))
            x0, x1 = int(max(0, x - rad - 1)), int(min(w, x + rad + 2))
            y0, y1 = int(max(0, y - rad - 1)), int(min(h, y + rad + 2))
            if x1 <= x0 or y1 <= y0:
                continue
            d2 = (xx[y0:y1, x0:x1] - x) ** 2 + ((yy[y0:y1, x0:x1] - y) * 1.25) ** 2
            z = np.sqrt(np.clip(rad * rad - d2, 0, None))
            # flat floor: nothing hangs below the base
            z = np.where(yy[y0:y1, x0:x1] > base + 1, 0, z)
            Z[y0:y1, x0:x1] = np.maximum(Z[y0:y1, x0:x1], z)
    return Z


def sky_layer(w=760, h=HORIZON + 6, seed=3, big=None):
    """Deep teal overhead falling to a pale, hot haze; cirrus streaks; cumulus heaped low."""
    yy = np.arange(h)[:, None] / float(HORIZON)
    xx = np.arange(w)[None, :]
    tone = 0.04 + 0.50 * np.clip(yy, 0, 1) ** 1.25 + 0 * xx
    cir = fbm((h, w), seed, 46, 1.3, octaves=3)
    band = np.exp(-((yy - 0.40) / 0.26) ** 2)
    tone += np.clip(cir - 0.56, 0, 1) * 0.9 * band
    cir2 = fbm((h, w), seed + 5, 90, 2.2, octaves=2)
    tone += np.clip(cir2 - 0.6, 0, 1) * 0.5 * np.exp(-((yy - 0.7) / 0.2) ** 2)

    # far bank on the horizon: a low, hazy line of cloud, soft and pale
    far = [(x, HORIZON - 2 + (i % 3), 90 + 30 * (i % 2), 8 + 5 * (i % 3), 46, 2.5, 5.5)
           for i, x in enumerate(range(10, w + 60, 58))]
    Zf = ndi.gaussian_filter(puffs(h, w, far, seed + 40), 1.1)
    covf = np.clip(Zf * 0.55, 0, 1)
    litf = light(Zf, -0.6, -0.8, 0.5)
    tf = 0.66 + 0.16 * np.clip(litf, -1, 1)
    tone = tone + covf * 0.8 * (np.clip(tf, 0.52, 0.84) - tone)

    # the towers: big heaps, hard light on top, blue floors melting into the haze
    big = big or [(96, 88, 150, 64, 170, 4.0, 11.0), (300, 93, 110, 34, 90, 3.5, 8.0),
                  (470, 90, 180, 54, 170, 4.0, 10.0), (668, 93, 120, 30, 90, 3.5, 8.0)]
    Z = puffs(h, w, big, seed + 41)
    Zs = ndi.gaussian_filter(Z, 0.7)
    cov = np.clip(Z * 0.8, 0, 1)
    lit = light(Zs, -0.55, -0.85, 0.5)
    floor = np.zeros((h, w))
    for cx, base, width, height, n, r0, r1 in big:
        f = np.clip(1 - (base - np.arange(h)[:, None]) / (height * 0.6), 0, 1) * (np.abs(xx - cx) < width * 0.62)
        floor = np.maximum(floor, f)
    shade = noise((h, w), seed + 50, 22, 12)
    ct = 0.74 + 0.46 * np.clip(lit, -1, 1) - 0.30 * floor ** 1.5 - 0.14 * (shade - 0.5)
    cov = cov * (1 - 0.55 * floor ** 3)
    tone = tone + cov * (np.clip(ct, 0.30, 1.0) - tone)
    L = Layer(w, h)
    L.put(toned(tone, SKY, dither=0.7), np.ones((h, w), bool))
    return L


# ------------------------------------------------------------------ far coast and shipping
FAR_H = 64
FAR_WATER = 60                # row of the waterline inside the far strip
FAR_TOP = HORIZON - FAR_WATER


def _ridge(w, seed, base, amp, sx):
    n = noise((1, w), seed, sx, 0.5)[0]
    n2 = noise((1, w), seed + 1, sx / 4, 0.5)[0]
    return base - amp * (0.75 * n + 0.25 * n2)


def _tanker(T, x, wl, length=170):
    """A laden crude carrier seen broadside, bow to the left."""
    hull_top = wl - 7
    T.poly([(x + 6, hull_top), (x + length - 2, hull_top), (x + length, hull_top + 2), (x + length - 3, wl),
            (x + 3, wl), (x, hull_top + 3)], 0.40)
    T.rect(x + 4, wl - 1, x + length - 4, wl, 0.30)                    # boot topping, dark with weed
    T.rect(x + 6, hull_top, x + length - 3, hull_top, 0.62)            # sheer line catching light
    T.poly([(x, hull_top + 3), (x + 6, hull_top - 2), (x + 16, hull_top - 2), (x + 16, hull_top)], 0.46)   # raised bow
    # deck: pipe runs, the midships manifold, derrick posts
    T.rect(x + 18, hull_top - 1, x + length - 44, hull_top - 1, 0.52)
    for i, px_ in enumerate(range(x + 24, x + length - 46, 11)):
        T.rect(px_, hull_top - 3, px_, hull_top - 1, 0.44)
        T.rect(px_ - 1, hull_top - 3, px_ + 1, hull_top - 3, 0.58)
    mx = x + length // 2 - 14
    T.rect(mx, hull_top - 5, mx + 12, hull_top - 2, 0.50)
    T.rect(mx, hull_top - 5, mx + 12, hull_top - 5, 0.66)
    for px_ in (mx + 2, mx + 10):
        T.rect(px_, hull_top - 13, px_, hull_top - 5, 0.48)
    T.line([(mx + 2, hull_top - 13), (mx - 8, hull_top - 4)], 0.56)
    T.line([(mx + 10, hull_top - 13), (mx + 20, hull_top - 4)], 0.56)
    # the house aft: four decks, bridge wings, funnel, mast
    hx = x + length - 40
    T.rect(hx, hull_top - 15, hx + 22, hull_top - 1, 0.74)
    T.rect(hx, hull_top - 15, hx + 3, hull_top - 1, 0.84)             # lit face
    T.rect(hx - 3, hull_top - 17, hx + 25, hull_top - 15, 0.70)       # bridge wings
    T.rect(hx - 3, hull_top - 17, hx + 25, hull_top - 17, 0.86)
    for dy in (-13, -9, -5):
        for px_ in range(hx + 5, hx + 21, 3):
            T.px(px_, hull_top + dy, 0.36)
    T.rect(hx + 26, hull_top - 19, hx + 32, hull_top - 1, 0.50)       # funnel
    T.rect(hx + 26, hull_top - 16, hx + 32, hull_top - 14, 0.30)
    T.rect(hx + 26, hull_top - 19, hx + 27, hull_top - 1, 0.66)
    T.rect(hx + 9, hull_top - 27, hx + 9, hull_top - 17, 0.52)        # mast
    T.rect(hx + 6, hull_top - 23, hx + 12, hull_top - 23, 0.52)
    T.rect(x + 9, hull_top - 9, x + 9, hull_top - 2, 0.50)            # foremast


def _boxship(T, x, wl, length=132):
    hull_top = wl - 8
    T.poly([(x + 8, hull_top), (x + length, hull_top), (x + length - 2, wl), (x + 4, wl), (x, hull_top + 2),
            (x + 3, hull_top - 3), (x + 10, hull_top - 3)], 0.36)
    T.rect(x + 5, wl - 1, x + length - 3, wl, 0.28)
    T.rect(x + 8, hull_top, x + length - 1, hull_top, 0.58)
    r = rng(91)
    # boxes in tiers, stepped down toward the bow
    for col, bx in enumerate(range(x + 12, x + length - 30, 9)):
        tiers = 2 + (col % 3 != 0) + (col > 2) + (col % 4 == 1)
        for tier in range(tiers):
            y1 = hull_top - 1 - tier * 4
            T.rect(bx, y1 - 3, bx + 7, y1, float(r.choice([0.46, 0.54, 0.62, 0.70, 0.50])))
            T.rect(bx, y1 - 3, bx + 7, y1 - 3, 0.78)
            T.rect(bx + 7, y1 - 3, bx + 7, y1, 0.40)
    hx = x + length - 26
    T.rect(hx, hull_top - 22, hx + 12, hull_top - 1, 0.74)
    T.rect(hx, hull_top - 22, hx + 2, hull_top - 1, 0.84)
    T.rect(hx - 2, hull_top - 24, hx + 14, hull_top - 22, 0.86)
    for dy in (-20, -16, -12, -8):
        for px_ in range(hx + 4, hx + 12, 3):
            T.px(px_, hull_top + dy, 0.36)
    T.rect(hx + 15, hull_top - 17, hx + 20, hull_top - 1, 0.48)
    T.rect(hx + 15, hull_top - 14, hx + 20, hull_top - 13, 0.30)
    T.rect(hx + 6, hull_top - 32, hx + 6, hull_top - 24, 0.52)


def _dhow(T, x, wl):
    """A sambuk under one lateen sail, running before the wind."""
    T.poly([(x, wl - 5), (x + 6, wl - 4), (x + 36, wl - 4), (x + 44, wl - 9), (x + 46, wl - 9), (x + 41, wl),
            (x + 5, wl)], 0.22)
    T.rect(x + 5, wl - 5, x + 40, wl - 5, 0.46)
    T.rect(x + 34, wl - 9, x + 44, wl - 6, 0.26)                      # high poop
    T.line([(x + 18, wl - 5), (x + 20, wl - 34)], 0.30)               # raked mast
    T.poly([(x + 3, wl - 12), (x + 38, wl - 40), (x + 30, wl - 8), (x + 6, wl - 9)], 0.92)   # the sail
    T.poly([(x + 3, wl - 12), (x + 20, wl - 25), (x + 16, wl - 9), (x + 6, wl - 9)], 0.80)
    T.line([(x + 2, wl - 11), (x + 39, wl - 41)], 0.40)               # the yard
    T.line([(x + 38, wl - 40), (x + 44, wl - 9)], 0.50)


def far_layer(w=960, seed=7, k=1.0):
    """What stands on the horizon: the far shore in haze, the island and its light, ships in the lane."""
    h, wl = FAR_H, FAR_WATER
    yy, xx = np.mgrid[0:h, 0:w]
    L = Layer(w, h)
    # the far shore: two pale ridges, almost sky
    for i, (seed_i, amp, sx, t0) in enumerate([(seed, 20, 110, 0.90), (seed + 9, 12, 70, 0.80)]):
        top = _ridge(w, seed_i, wl - 2, amp, sx)
        fade = np.clip(np.sin(np.linspace(0, np.pi * 1.6, w) + i * 1.3) * 0.5 + 0.7, 0.15, 1)
        top = wl - (wl - top) * fade
        m = (yy >= top[None, :]) & (yy < wl)
        tone = t0 + 0.07 * np.clip((yy - top[None, :]) / 12.0, 0, 1) + 0.03 * (noise((h, w), seed_i + 3, 6, 2) - 0.5)
        L.put(toned(np.clip(tone, 0, 1), HAZE2, dither=0.6), m)

    T = Tone(w, h)
    # the island: low lava cliffs, nearer and darker
    ix0, ix1 = int(540 * k), int(540 * k) + 300
    xs = np.arange(ix0, ix1)
    u = (xs - ix0) / float(ix1 - ix0)
    hill = 30 * np.sin(np.pi * u) ** 0.7 * (0.55 + 0.45 * np.sin(u * 7.0 + 0.6) ** 2)
    hill += 3 * noise((1, len(xs)), seed + 20, 4, 0.5)[0]
    prof = np.full(w, float(wl))
    prof[ix0:ix1] = wl - hill
    m = (yy >= prof[None, :]) & (yy < wl)
    strata = noise((h, w), seed + 21, 10, 1.2)
    facets = noise((h, w), seed + 22, 3, 5)
    lit = light(ndi.gaussian_filter(facets, 1.0), -0.8, -0.5, 6.0)
    depth = np.clip((yy - prof[None, :]) / 22.0, 0, 1)
    tone = 0.46 + 0.16 * np.clip(lit, -1, 1) + 0.10 * (strata - 0.5) + 0.16 * depth
    tone = np.where((yy - prof[None, :]) < 1.5, tone + 0.22, tone)      # sunlit crest
    T.mask(m, 0)
    T.t = np.where(m, tone, T.t)
    # the lighthouse on the high point, banded, with its lantern and the keeper's block
    lx = ix0 + 160
    ly = int(prof[lx]) + 1
    for i in range(26):
        yb = ly - i
        half = 3 if i < 5 else 2
        band = (i // 5) % 2
        T.rect(lx - half, yb, lx + half, yb, 0.88 if band else 0.40)
        T.px(lx - half, yb, 0.96 if band else 0.52)
        T.px(lx + half, yb, 0.70 if band else 0.30)
    T.rect(lx - 4, ly - 27, lx + 4, ly - 26, 0.34)                      # gallery
    T.rect(lx - 2, ly - 31, lx + 2, ly - 28, 0.94)                      # lantern
    T.rect(lx - 2, ly - 30, lx + 2, ly - 30, 0.50)
    T.rect(lx - 3, ly - 32, lx + 3, ly - 32, 0.36)
    T.rect(lx - 1, ly - 34, lx + 1, ly - 33, 0.36)
    T.rect(lx, ly - 37, lx, ly - 35, 0.40)
    T.rect(lx + 7, ly - 6, lx + 22, ly, 0.84)                           # keeper's block
    T.rect(lx + 7, ly - 7, lx + 22, ly - 7, 0.94)
    for px_ in (lx + 10, lx + 14, lx + 18):
        T.rect(px_, ly - 4, px_, ly - 3, 0.38)
    T.rect(lx - 30, ly + 2, lx - 18, ly + 6, 0.80)                      # the old garrison, roofless
    T.rect(lx - 30, ly + 1, lx - 18, ly + 1, 0.92)
    T.rect(lx - 27, ly + 3, lx - 26, ly + 6, 0.36)
    T.rect(lx - 22, ly + 3, lx - 21, ly + 6, 0.36)

    _tanker(T, int(96 * k), wl)
    _boxship(T, int(372 * k), wl)
    _dhow(T, int(880 * k), wl)
    L.paste(T.layer(HAZE2, dither=0.5, grain=0.05, seed=seed + 30))
    return L


def sea_layer(w=1320, seed=11):
    """Water from the horizon to the beach: pale at the haze line, deep in the lane, bright in the shallows."""
    h = 52
    yy, xx = np.mgrid[0:h, 0:w]
    v = yy / float(h - 1)
    base = 0.62 - 0.9 * v * np.exp(-v * 3.2) * 1.9 + 0.50 * v ** 2.2
    # streaks that lengthen toward the viewer
    tone = np.zeros((h, w))
    src = fbm((h, w * 2), seed, 10, 0.6, octaves=3)
    for y in range(h):
        s = 0.35 + 1.9 * (y / (h - 1.0))
        xs = (np.arange(w) / s + 37 * y) % (w * 2 - 1)
        tone[y] = np.interp(xs, np.arange(w * 2), src[y])
    blot = fbm((h, w), seed + 3, 60, 5, octaves=2)
    t = base + 0.22 * (tone - 0.5) - 0.16 * np.clip(blot - 0.5, 0, 1) * (1 - v)
    t[0] = 0.86
    t[1] = np.maximum(t[1], 0.72)
    # glitter: a few bright dashes
    glint = (fbm((h, w), seed + 5, 3, 0.5, octaves=2) > 0.80) & (v > 0.15)
    t = np.where(glint, t + 0.22, t)
    L = Layer(w, h)
    L.put(toned(np.clip(t, 0.05, 0.98), SEA, dither=0.6), np.ones((h, w), bool))
    return L


# ------------------------------------------------------------------ the ground
G_TOP = 118                   # the ground layer covers screen rows G_TOP..SH-1
G_H = SH - G_TOP


def shore_line(w=STAGE_W, seed=21):
    """Screen row of the waterline along the stage. The sea comes in close at the landing."""
    x = np.arange(w)
    y = 137 + 5 * (noise((1, w), seed, 140, 0.5)[0] - 0.5) * 2 + 2 * (noise((1, w), seed + 1, 30, 0.5)[0] - 0.5) * 2
    y += 16 * np.exp(-(x / 150.0) ** 2)                       # the cove where the boat is beached
    y -= 6 * np.exp(-((x - 1650) / 220.0) ** 2)               # the rise toward the battery
    return y


def walk_line(w=STAGE_W, seed=23):
    """Screen row the feet land on."""
    x = np.arange(w)
    y = WALK + 2.5 * (noise((1, w), seed, 90, 0.5)[0] - 0.5) * 2
    y -= 7 * np.exp(-((x - 1700) / 170.0) ** 2)               # the lava rise under the battery
    return y


def sand_tone(h, w, d, seed):
    """Tone of the beach surface. d = rows below the waterline (screen space)."""
    yy, xx = np.mgrid[0:h, 0:w]
    depth = np.clip(d / (SH - 137.0), 0, 1)                   # 0 at the water, 1 at the bottom of the screen
    # dunes: long low swells plus a few distinct mounds; lit from the upper left
    H = 1.0 * fbm((h, w), seed + 2, 70, 9, octaves=2) + 0.45 * fbm((h, w), seed + 3, 22, 4, octaves=2)
    r = rng(seed + 40)
    for i in range(int(w / 55)):
        cx, cy = r.uniform(0, w), r.uniform(h * 0.25, h * 1.05)
        rx, ry = r.uniform(26, 70), r.uniform(4, 9)
        H += r.uniform(0.25, 0.6) * np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2))
    Hs = ndi.gaussian_filter(H, (0.8, 2.0))
    lit = light(Hs, -0.6, -0.8, 1.0)
    lit = lit / (np.percentile(np.abs(lit), 97) + 1e-6)
    # hollows scoured by the wind: soft pools of shade on the lee (lower right) of the swells
    hol = fbm((h, w), seed + 4, 30, 5, octaves=2)
    hollow = np.clip(hol - 0.62, 0, 1) * 2.6
    # ripples: combed strokes rising to the right, coarser toward the viewer, in patches
    warp = fbm((h, w), seed + 6, 60, 10, octaves=3)
    period = 2.4 + 2.0 * depth
    u = (yy + 0.22 * xx + 26.0 * warp) / period
    rip = np.sin(2 * np.pi * u)
    patch = np.clip((fbm((h, w), seed + 8, 30, 6, octaves=3) - 0.42) * 3.5, 0, 1)
    fine = fbm((h, w), seed + 9, 3.0, 0.6, octaves=2) - 0.5
    t = 0.74 - 0.06 * depth + 0.26 * np.clip(lit, -1.3, 1.3) - 0.34 * hollow
    t += (0.03 + 0.045 * depth) * rip * patch + 0.05 * fine
    # the far strip flattens and pales in the glare
    far = np.clip(1 - d / 14.0, 0, 1)
    t = t * (1 - 0.55 * far) + 0.84 * 0.55 * far
    return t, depth


def ground_layer(w=STAGE_W, seed=31):
    """Sea's edge, wet sand, the beach: soft dunes lit from the upper left, combed with ripples."""
    h = G_H
    yy, xx = np.mgrid[0:h, 0:w]
    sy = yy + G_TOP                                           # screen row
    shore = shore_line(w)[None, :]
    d = sy - shore                                            # rows below the waterline
    L = Layer(w, h)

    # near water above the line: pale shallows, two lines of lace where waves spend themselves
    lap = noise((h, w), seed, 16, 0.7)
    wt = 0.78 + 0.10 * (lap - 0.5) + 0.12 * np.clip(1 + d / 9.0, 0, 1)
    n1 = noise((1, w), seed + 1, 18, 0.5)[0][None, :]
    n2 = noise((1, w), seed + 5, 11, 0.5)[0][None, :]
    lace1 = np.abs(d + 7.5 - 3.0 * (n1 - 0.5) * 2) < (0.5 + 0.9 * noise((h, w), seed + 7, 5, 0.5))
    lace2 = np.abs(d + 3.0 - 2.0 * (n2 - 0.5) * 2) < (0.4 + 0.8 * noise((h, w), seed + 8, 4, 0.5))
    wt = np.where(lace1 | lace2, 0.985, wt)
    water = (d < 0) & (d > -13)
    L.put(toned(np.clip(wt, 0, 1), SEA, dither=0.6), water)

    t, depth = sand_tone(h, w, d, seed)
    sand = d >= 0
    L.put(toned(np.clip(t, 0.08, 1), SAND, dither=0.5), sand)

    # wet sand where the water has just been: darker, cooler, a sheen along the line
    wet_w = 4.0 + 3.0 * noise((1, w), seed + 10, 40, 0.5)[0][None, :]
    k = np.clip(1 - d / (wet_w + 0.01), 0, 1)
    wet = (d >= 0) & (d < wet_w)
    wtone = 0.66 + 0.26 * k ** 1.5 + 0.14 * (noise((h, w), seed + 12, 12, 0.6) - 0.5)
    L.put(toned(np.clip(wtone, 0, 1), WET, dither=0.6), wet)
    swash = (d >= -0.5) & (d < 0.8 + 1.2 * noise((h, w), seed + 13, 6, 0.5))
    L.put(toned(np.full((h, w), 0.96), SEA, dither=0.0), swash)

    # shells: a few pale specks near the viewer
    r = rng(seed + 14)
    n = w // 3
    for x, y in zip(r.integers(0, w, n), r.integers(0, h, n)):
        if sand[y, x] and d[y, x] > 12 and r.random() < depth[y, x]:
            L.rgb[y, x] = SAND[19]
            if x + 1 < w:
                L.rgb[y, x + 1] = SAND[5]
    return L


# ------------------------------------------------------------------ the playfield: ground plus set pieces
def _shadow_on(play, mask_local, x, y, steps=-3):
    """Darken the sand (and wet sand) under a mask given in a piece's frame at (x, y)."""
    h, w = mask_local.shape
    full = np.zeros((play.h, play.w), bool)
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(play.w, x + w), min(play.h, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    full[y0:y1, x0:x1] = mask_local[y0 - y:y1 - y, x0 - x:x1 - x]
    P.shade(play, full, SAND, steps)
    P.shade(play, full, WET, steps // 2)


def put(play, piece, x, base_y, floor, shadow=True, bury=0, seed=1, reach=0.5):
    """Stand a painted piece on the sand: its row `floor` goes to screen row base_y."""
    if bury:
        piece = P.sink(piece, piece.h - floor + bury, seed=seed)
        # sink() counts rows from the bottom of the picture
    y = int(base_y - floor)
    if shadow:
        m = P.cast_shadow(piece, min(floor - bury, piece.h - 1), reach=reach)
        _shadow_on(play, m, int(x), y, -3)
        core = ndi.binary_erosion(m, iterations=2)
        _shadow_on(play, core, int(x), y, -2)
    play.paste(piece, int(x), y)


def play_layer(seed=41, battery=True):
    """Ground and everything that stands on it, far pieces first. battery=False leaves the lava rise bare: the long stage
    puts the battery at the far end of the coast road instead."""
    g = ground_layer()
    play = Layer(STAGE_W, SH)
    play.paste(g, 0, G_TOP)
    shore = shore_line()
    walk = walk_line()
    items = []                                           # (base_y, callable)

    def add(piece, x, base_y, floor, **kw):
        items.append((base_y, piece, x, floor, kw))

    # ---- 1. landfall: the squad's boat, rocks, the first palm, a drying rack
    sk, f = P.skiff(length=96, paint=P.BOATWHITE, stripe=P.BOATBLUE, seed=3, cargo=True)
    add(sk, 8, 166, f, bury=2, seed=4)
    for i, (x, by, w_, h_) in enumerate([(150, 156, 34, 18), (196, 160, 20, 11), (330, 158, 26, 14)]):
        rk, f = P.rock(w_, h_, seed=10 + i)
        add(rk, x, by, f, bury=2, seed=i)
    pm, f, bx = P.palm(height=88, lean=9, seed=2)
    add(pm, 372, 152, f)
    fr, f = P.fish_rack(8)
    add(fr, 250, 157, f)
    jt, f = P.jetty(6, seed=2)
    add(jt, 96, 150, f, shadow=False)
    mn, f = P.sea_mine(seed=2)
    add(mn, 430, 172, f, bury=2, seed=3)
    for i, (x, by) in enumerate([(112, 172), (126, 176)]):
        cr, f = P.crate(seed=20 + i, mark=True)
        add(cr, x, by, f)

    # ---- 2. the fishing camp and the wreck
    ht, f = P.hut(seed=2)
    add(ht, 470, 156, f)
    pm2, f, bx = P.palm(height=76, lean=-7, seed=5)
    add(pm2, 520, 150, f)
    pm3, f, bx = P.palm(height=94, lean=12, seed=7, dead=0.5)
    add(pm3, 566, 153, f)
    sk2, f = P.skiff(seed=2)
    add(sk2, 556, 170, f, bury=2, seed=6)
    dh, base, deck = P.dhow_wreck()
    add(dh, 668, 181, base, bury=4, seed=9, reach=0.35)
    fr2, f = P.fish_rack(6)
    add(fr2, 612, 160, f)

    # ---- 3. container beach
    c5, f = P.container('ochre', seed=8)
    add(P.tilt(c5, 3), 1004, 166, f + 6, bury=10, seed=3, reach=0.3)
    c1, f = P.container('oxide', seed=3)
    add(P.tilt(c1, -6), 944, 196, f + 12, bury=22, seed=5, reach=0.3)
    c2, f = P.container('blue', seed=4, tag=True)
    add(c2, 1084, 186, f, bury=8, seed=7, reach=0.3)
    c3, f = P.container('green', length=60, seed=5, doors=True)
    add(c3, 1110, 135, f, shadow=False)                  # riding on the blue box
    c4, f = P.container('white', seed=6)
    add(P.tilt(c4, 9), 1236, 198, f + 18, bury=24, seed=8, reach=0.3)
    cf, f = P.campfire()
    add(cf, 1368, 172, f)
    pm4, f, bx = P.palm(height=80, lean=-10, seed=11)
    add(pm4, 1210, 150, f)

    # ---- 4. the battery on the lava rise
    if battery:
        for i, (x, by, w_, h_) in enumerate([(1424, 168, 60, 34), (1470, 176, 40, 20), (1520, 158, 46, 28),
                                             (1812, 170, 54, 30), (1852, 182, 30, 16)]):
            rk, f = P.rock(w_, h_, seed=30 + i)
            add(rk, x, by, f, bury=2, seed=i)
        ds, f = P.dish()
        add(ds, 1548, 160, f)
        wt, f, plat = P.watchtower()
        add(wt, 1762, 168, f)
        cn, f = P.camo_net(w=132, h=40, seed=3)
        add(cn, 1592, 172, f, shadow=False)
        fl, f = P.flag()
        add(fl, 1736, 170, f)
        pm5, f, bx = P.palm(height=70, lean=6, seed=13)
        add(pm5, 1690, 150, f)

    for base_y, piece, x, floor, kw in sorted(items, key=lambda t: t[0]):
        put(play, piece, x, base_y, floor, **kw)

    # cargo spilled from the white box
    ff = P.flipflops(n=90, w=150, h=30, seed=3)
    play.paste(ff, 1180, 176)
    return play, dict(walk=walk, shore=shore, deck=(668 + deck[0], 668 + deck[1], 181 - base + deck[2]), wreck_top=181 - base)


def foreground_layer(w=2340, seed=51):
    """What passes close to the lens: black rocks and drift along the bottom edge."""
    L = Layer(w, SH)
    r = rng(seed)
    spots = [(-14, 60, 30), (130, 30, 15), (540, 64, 30), (610, 28, 14), (1130, 50, 24), (1560, 70, 32),
             (1640, 30, 16), (2090, 60, 28), (2280, 60, 30)]
    for i, (x, w_, h_) in enumerate(spots):
        rk, f = P.rock(w_, h_, seed=70 + i, sharp=0.9)
        P.shade(rk, rk.a, P.ROCK, -2)
        L.paste(rk, x, SH - h_ + 6)
    # a mooring post near the lens
    T = Tone(w, SH)
    T.rect(1800, 186, 1805, 215, 0.34)
    T.rect(1800, 186, 1801, 215, 0.74)
    T.rect(1798, 192, 1807, 194, 0.56)
    L.paste(T.layer(P.DRIFT, dither=0.3))
    return L


def compose(cam=0, layers=None, sprites=(), fore=True):
    """One screen at camera x, each layer sliding at its own rate. sprites: (image, stage_x, foot_y, fx, fy)."""
    S = layers or build_layers()
    out = Layer(SW, SH)
    out.paste(S['sky'], -int(cam * 0.2), 0)
    out.paste(S['sea'], -int(cam * 0.6), HORIZON)
    out.paste(S['far'], -int(cam * 0.35), FAR_TOP)
    out.paste(S['play'], -int(cam), 0)
    for im, sx, fy_, fx, fy in sprites:
        out.paste(from_image(im), int(sx - cam - fx), int(fy_ - fy))
    if fore:
        out.paste(S['fore'], -int(cam * 1.25), 0)
    return out


_CACHE = {}


def build_layers():
    if not _CACHE:
        play, info = play_layer()
        _CACHE.update(sky=sky_layer(), far=far_layer(), sea=sea_layer(), play=play, info=info, fore=foreground_layer())
    return _CACHE


if __name__ == '__main__':
    import sys
    S = build_layers()
    cams = [0, 468, 936, 1404]
    sheet = Layer(SW * 2 + 6, SH * 2 + 6)
    sheet.rgb[:] = (20, 16, 24); sheet.a[:] = True
    for i, c in enumerate(cams):
        sheet.paste(compose(c, S), (i % 2) * (SW + 6), (i // 2) * (SH + 6))
    im = sheet.image()
    im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
    im.save('t3_stage.png')
    print(im.size)
