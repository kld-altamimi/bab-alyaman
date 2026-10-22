# props.py - set pieces painted for the stage: no outlines, close tones, upper-left light.
import numpy as np
from scipy import ndimage as ndi
from paint import *

WOOD = ramp(['#1a0e08', '#3c2212', '#644024', '#8c6238', '#b08a58', '#d0b080', '#ecd8ac'], 16)
GREY = ramp(['#16120e', '#34302a', '#58524a', '#7e786a', '#a49c88', '#c8c0a8', '#e6e0c8'], 14)
RUST = ramp(['#1c0a06', '#3e160c', '#682a12', '#94441c', '#ba6a2c', '#d8944c', '#ecc080'], 14)
TARP = ramp(['#10202e', '#1c3c52', '#2e5c78', '#4c809a', '#78a4b4', '#a8c8cc', '#d4e4dc'], 12)
NET = ramp(['#141008', '#2c2414', '#4a3e22', '#6a5a34'], 4)
FLOAT = ramp(['#5a1c08', '#a03c10', '#e0701c', '#f8b050'], 4)


def interp(x, pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return np.interp(x, xs, ys)


def smooth(x, pts, s=6):
    return ndi.gaussian_filter1d(interp(x, pts), s, mode='nearest')


def ramp_index(rgb, rmp):
    """Index of each pixel's colour in a ramp (-1 where it is not from that ramp)."""
    h, w, _ = rgb.shape
    key = rgb[..., 0].astype(np.int32) * 65536 + rgb[..., 1].astype(np.int32) * 256 + rgb[..., 2]
    out = np.full((h, w), -1, dtype=int)
    for i, c in enumerate(rmp):
        k = int(c[0]) * 65536 + int(c[1]) * 256 + int(c[2])
        out[key == k] = i
    return out


def shade(layer, mask, rmp, steps):
    """Darken (steps<0) or lighten the pixels of a ramp inside mask, staying on the ramp."""
    idx = ramp_index(layer.rgb, rmp)
    if np.isscalar(steps):
        steps = np.full(mask.shape, steps)
    ok = mask & (idx >= 0) & layer.a
    new = np.clip(idx + np.round(steps).astype(int), 0, len(rmp) - 1)
    layer.rgb[ok] = rmp[new[ok]]


DRIFT = ramp(['#120a06', '#2a1a10', '#4a3020', '#6e4c32', '#93704e', '#b8987a', '#d8c4a4', '#f0e6cc'], 16)


def dhow_wreck(seed=5):
    """A sambuk driven ashore and left: heeled toward us so the deck shows, bow to the right.
    Returns the picture, the row that sits on the sand, and the deck line to stand on."""
    W, Hh = 216, 100
    r = rng(seed)
    x = np.arange(W)
    yy, xx = np.mgrid[0:Hh, 0:W]
    base = 92                                             # sand line inside the picture
    x0, x1 = 14, 200                                      # stern .. stemhead
    hull = (x >= x0) & (x <= x1)
    # far rail, near rail and the turn of the bilge; all three meet at the stem
    far = smooth(x, [(x0, 54), (40, 58), (100, 61), (150, 57), (180, 46), (x1, 30)], 5)
    near = far + smooth(x, [(x0, 14), (60, 16), (120, 16), (165, 12), (190, 5), (x1, 0)], 4)
    bot = smooth(x, [(x0, base - 8), (36, base), (150, base), (176, base - 10), (192, base - 34), (x1, 34)], 3)
    bot = np.maximum(bot, near + 1)
    T = Tone(W, Hh)

    # ---- hull side: strakes that taper to the ends
    side = (yy >= near[None, :]) & (yy <= bot[None, :]) & hull[None, :]
    n_str = 7
    s = np.clip((yy - near[None, :]) / np.maximum(bot - near, 1)[None, :], 0, 1)
    k = s * n_str
    strake = np.floor(k)
    seam = (k - strake) < (0.9 / np.maximum((bot - near) / n_str, 1.0))[None, :]
    grain = fbm((Hh, W), seed + 1, 14, 0.7, octaves=3)
    blotch = fbm((Hh, W), seed + 7, 20, 5, octaves=2)
    plank_var = np.array([r.uniform(-0.05, 0.05) for _ in range(n_str + 1)])[strake.astype(int).clip(0, n_str)]
    t = 0.60 - 0.44 * s ** 1.1 + plank_var + 0.14 * (grain - 0.5) + 0.10 * (blotch - 0.5)
    t = np.where(strake <= 0, t + 0.14, t)                 # the sheer strake catches the sun
    t = np.where(s > 0.5, t - 0.08, t)                     # below the old waterline: tarred, weed-dark
    t = np.where(seam, t - 0.20, t)
    t -= 0.10 * np.clip((xx - 150) / 50.0, 0, 1)           # the bow turns away from the light
    for st in range(n_str):
        for bx in r.integers(x0 + 8, x1 - 30, 5):
            m = (strake == st) & (xx == bx) & side
            t = np.where(m, t - 0.2, t)
    T.mask(side, 0)
    T.t = np.where(side, t, T.t)
    # sprung planks: dark gaps with the ribs showing
    for (st, a_, b_) in ((2, 62, 98), (3, 58, 86), (4, 116, 150), (1, 128, 144), (5, 80, 104)):
        gap = side & (strake == st) & (xx >= a_) & (xx <= b_) & ~seam
        T.t = np.where(gap, 0.04 + 0.05 * (grain - 0.5), T.t)
        T.t = np.where(gap & (((xx - a_) % 7) < 2), 0.30, T.t)
        T.t = np.where(gap & (((xx - a_) % 7) == 0), 0.46, T.t)

    # ---- far bulwark: a low wall of planking beyond the deck
    bul = (yy >= far[None, :] - 6) & (yy <= far[None, :]) & hull[None, :] & (xx < x1 - 4)
    tb = 0.36 + 0.10 * (grain - 0.5) - 0.08 * (((yy - far[None, :]) % 3) == 0)
    T.mask(bul, 0)
    T.t = np.where(bul, tb, T.t)
    T.t = np.where(bul & (yy <= far[None, :] - 5.2), 0.84, T.t)      # lit cap
    for sx_ in range(x0 + 12, x1 - 20, 13):                        # frames standing proud
        T.t = np.where(bul & (xx == sx_), 0.22, T.t)

    # ---- deck, tilted toward us: planks run fore and aft
    deck = (yy > far[None, :]) & (yy < near[None, :]) & hull[None, :]
    sd = np.clip((yy - far[None, :]) / np.maximum(near - far, 1)[None, :], 0, 1)
    kd = sd * 5
    dseam = (kd - np.floor(kd)) < 0.2
    td = 0.74 - 0.08 * sd + 0.12 * (fbm((Hh, W), seed + 2, 18, 0.7, octaves=2) - 0.5) - 0.20 * np.clip(0.25 - sd, 0, 1) * 2
    td = np.where(dseam, td - 0.16, td)
    T.mask(deck, 0)
    T.t = np.where(deck, td, T.t)
    # hatch: half the boards gone
    hx0, hx1 = 90, 116
    hatch = deck & (xx >= hx0) & (xx <= hx1) & (sd > 0.25) & (sd < 0.8)
    T.t = np.where(hatch, 0.05, T.t)
    T.t = np.where(hatch & (xx > hx0 + 13) & (((xx - hx0) % 4) != 0), 0.60, T.t)
    coam = deck & (xx >= hx0 - 1) & (xx <= hx1 + 1) & (sd > 0.17) & (sd < 0.88) & ~hatch
    T.t = np.where(coam, 0.90, T.t)
    # near rail: a stout timber with a lit top
    nearrail = (yy >= near[None, :] - 1.6) & (yy <= near[None, :] + 0.6) & hull[None, :]
    T.mask(nearrail, 0.50)
    T.t = np.where(nearrail & (yy <= near[None, :] - 0.8), 0.92, T.t)

    # ---- the stemhead where it all meets
    T.rect(x1 - 2, 22, x1 + 2, 36, 0.40)
    T.rect(x1 - 2, 22, x1 - 1, 34, 0.84)
    T.rect(x1 - 3, 20, x1 + 3, 22, 0.56)
    T.rect(x1 - 3, 20, x1 + 1, 20, 0.90)

    # ---- the poop: a low deckhouse aft, doorway and port
    hp = [(x0 + 2, far[x0 + 2] - 20), (x0 + 40, far[x0 + 40] - 19), (x0 + 40, near[x0 + 40] - 3),
          (x0 + 2, near[x0 + 2] - 2)]
    ph = poly_mask(W, Hh, hp)
    th = 0.50 + 0.10 * (grain - 0.5) - 0.14 * ((yy % 4) == 0) - 0.12 * np.clip((yy - 60) / 14.0, 0, 1)
    T.mask(ph, 0)
    T.t = np.where(ph, th, T.t)
    T.poly([(x0 + 1, far[x0 + 2] - 20), (x0 + 41, far[x0 + 40] - 19), (x0 + 45, far[x0 + 43] - 24),
            (x0 + 5, far[x0 + 5] - 25)], 0.88)             # roof, sunlit
    T.rect(x0 + 1, int(far[x0 + 2]) - 20, x0 + 41, int(far[x0 + 2]) - 20, 0.28)       # eave shadow
    T.rect(x0 + 15, int(far[x0 + 16]) - 12, x0 + 22, int(near[x0 + 16]) - 3, 0.05)    # doorway
    T.rect(x0 + 23, int(far[x0 + 16]) - 12, x0 + 23, int(near[x0 + 16]) - 3, 0.80)
    T.rect(x0 + 29, int(far[x0 + 29]) - 12, x0 + 35, int(far[x0 + 29]) - 7, 0.08)     # port
    T.rect(x0 + 29, int(far[x0 + 29]) - 13, x0 + 35, int(far[x0 + 29]) - 13, 0.88)
    L = T.layer(DRIFT, dither=0.45, grain=0.07, seed=seed + 3)

    # ---- mast stump, snapped, with what is left of the rigging
    M = Tone(W, Hh)
    mx0, my0 = 130, int(near[130]) - 7
    for i in range(38):
        cx = mx0 + i * 0.28
        cy = my0 - i
        M.rect(cx - 2, cy, cx + 2, cy, 0.40)
        M.px(cx - 2, cy, 0.90)
        M.px(cx - 1, cy, 0.66)
        M.px(cx + 2, cy, 0.16)
        if i % 9 == 4:
            M.rect(cx - 2, cy, cx + 2, cy, 0.20)           # iron bands
    tx, ty = int(mx0 + 10), my0 - 38
    for dx, dy in ((-2, -3), (0, -6), (2, -2), (1, -1), (-1, -1)):
        M.px(tx + dx, ty + dy, 0.82)
        M.px(tx + dx, ty + dy + 1, 0.44)
    L.paste(M.layer(DRIFT, dither=0.3))
    R = Tone(W, Hh)
    R.line([(tx, ty), (x1 - 1, 23)], 0.50)                 # forestay, still made fast
    R.line([(tx - 1, ty + 2), (x0 + 36, far[x0 + 36] - 22)], 0.46)
    R.line([(tx, ty + 8), (158, near[158] - 2)], 0.40)
    for rx, ry, ln in ((160, 30, 5), (176, 27, 4), (100, 41, 6), (74, 45, 4)):
        R.rect(rx, ry, rx, ry + ln, 0.34)                  # rags of weed on the stays
    L.paste(R.layer(DRIFT, dither=0.0))

    # ---- awning: faded blue tarp sagging between poles over the poop
    A = Tone(W, Hh)
    A.rect(x0 + 6, int(far[x0 + 6]) - 36, x0 + 6, int(far[x0 + 6]) - 24, 0.24)
    A.rect(x0 + 42, int(far[x0 + 42]) - 35, x0 + 42, int(far[x0 + 42]) - 23, 0.24)
    L.paste(A.layer(DRIFT, dither=0.0))
    A = Tone(W, Hh)
    ax = np.arange(x0 + 2, x0 + 48)
    for i, sx_ in enumerate(ax):
        u = i / float(len(ax) - 1)
        sag = 4.5 * np.sin(np.pi * u)
        y0 = int(far[x0 + 6] - 37 + sag)
        ln = 5 + int(3 * np.sin(u * 7.0) + 2 * (i % 5 == 0))
        for j in range(ln):
            A.px(sx_, y0 + j, 0.90 - 0.13 * j + 0.10 * np.sin(u * 9.0))
        if (i // 3) % 2 == 0:
            A.px(sx_, y0 + 2, 0.30)
    L.paste(A.layer(TARP, dither=0.4))

    # ---- a net over the near rail, floats still on it
    N = Tone(W, Hh)
    for sx_ in range(40, 86):
        top = int(near[sx_]) - 1
        ln = int(9 + 5 * np.sin((sx_ - 40) / 46.0 * np.pi) + 2 * np.sin(sx_ * 0.9))
        for j in range(ln):
            if (sx_ + j) % 2 == 0 or j == 0:
                N.px(sx_, top + j, 0.2 + 0.6 * ((sx_ + 2 * j) % 3 == 0))
    L.paste(N.layer(NET, dither=0.0))
    Fl = Tone(W, Hh)
    for fx in (44, 53, 62, 72, 81):
        fy = int(near[fx]) + 2 + (fx % 3)
        Fl.rect(fx, fy, fx + 2, fy + 2, 0.55)
        Fl.px(fx, fy, 0.95)
        Fl.px(fx + 2, fy + 2, 0.1)
    L.paste(Fl.layer(FLOAT, dither=0.0))

    # iron sickness: rust weeping from the fastenings
    for i in range(30):
        rx = int(r.integers(x0 + 6, x1 - 34))
        ry = int(near[rx] + r.integers(3, 12))
        for j in range(int(r.integers(2, 5))):
            if ry + j < Hh and L.a[ry + j, rx]:
                L.rgb[ry + j, rx] = RUST[4 - min(j, 2)]
    deck_line = near - 5
    return L, base, (x0 + 46, x1 - 40, deck_line)


# ---------------------------------------------------------------- shipping containers
PAINTS = {
    'oxide': ramp(['#200a08', '#40160e', '#662616', '#883a22', '#a45438', '#bc7858', '#d4a080'], 12),
    'blue': ramp(['#0a141e', '#142838', '#224256', '#365e74', '#50808e', '#7ca0a4', '#a8c0bc'], 12),
    'green': ramp(['#0e160a', '#1e2a14', '#344422', '#4e6034', '#6c7e4c', '#909c6c', '#b8bc94'], 12),
    'white': ramp(['#2a2620', '#544e42', '#807868', '#a8a08c', '#c8c2ac', '#e2dcc8', '#f6f2e2'], 12),
    'ochre': ramp(['#221606', '#46300e', '#70501a', '#987428', '#b89844', '#d0b86c', '#e4d49c'], 12),
}
STENCIL = np.array([[248, 232, 200], [200, 184, 150]], dtype=np.uint8)
TAG = np.array([[232, 176, 36], [156, 108, 16]], dtype=np.uint8)

SCORPION = [             # the militia's mark, sprayed through a stencil
    '.##.....##.',
    '#..#...#..#',
    '#...###...#',
    '.#.#####.#.',
    '..#######..',
    '.#.#####.#.',
    '#...###...#',
    '....##.....',
    '...##......',
    '..##...##..',
    '..#...#..#.',
    '..##..#....',
    '...####....',
]


def container(paint='oxide', length=118, height=52, seed=1, tag=False, doors=False, marks=True):
    """A steel box seen from the side, a little from above and from the left: long face,
    a strip of roof, the right end in shade. Returns picture and the row of its floor."""
    r = rng(seed)
    top_h, end_w = 5, 7
    W, Hh = length + end_w + 2, height + top_h + 2
    yy, xx = np.mgrid[0:Hh, 0:W]
    T = Tone(W, Hh)
    fx0, fy0 = 0, top_h                                  # long face
    fx1, fy1 = length - 1, top_h + height - 1
    face = (xx >= fx0) & (xx <= fx1) & (yy >= fy0) & (yy <= fy1)
    # corrugation: ribs four pixels apart, each with a lit and a shaded flank
    ph = (xx - fx0) % 4
    rib = np.choose(ph, [0.66, 0.74, 0.58, 0.48])
    dent = fbm((Hh, W), seed, 16, 20, octaves=2)
    t = rib + 0.10 * (dent - 0.5) - 0.10 * np.clip((yy - fy0) / float(height), 0, 1) ** 2
    if doors:
        t = 0.62 + 0.08 * (dent - 0.5) + 0 * xx
    T.mask(face, 0)
    T.t = np.where(face, t, T.t)
    # rails and posts
    T.rect(fx0, fy0, fx1, fy0 + 2, 0.50)
    T.rect(fx0, fy0, fx1, fy0, 0.86)
    T.rect(fx0, fy1 - 3, fx1, fy1, 0.40)
    T.rect(fx0, fy1 - 3, fx1, fy1 - 3, 0.62)
    for px_ in (fx0, fx1 - 2):
        T.rect(px_, fy0, px_ + 2, fy1, 0.52)
        T.rect(px_, fy0, px_, fy1, 0.80)
    for px_ in (fx0, fx1 - 3):                           # corner castings
        for py_ in (fy0, fy1 - 3):
            T.rect(px_, py_, px_ + 3, py_ + 3, 0.34)
            T.rect(px_ + 1, py_ + 1, px_ + 2, py_ + 2, 0.10)
    for px_ in (fx0 + length // 3 - 6, fx0 + 2 * length // 3 - 6):   # fork pockets
        T.rect(px_, fy1 - 2, px_ + 11, fy1 - 1, 0.08)
    if doors:
        mid = (fx0 + fx1) // 2
        T.rect(mid, fy0 + 3, mid, fy1 - 4, 0.20)
        for bx in (fx0 + 8, mid - 8, mid + 8, fx1 - 9):  # locking bars and their handles
            T.rect(bx, fy0 + 3, bx, fy1 - 4, 0.84)
            T.rect(bx + 1, fy0 + 3, bx + 1, fy1 - 4, 0.36)
            T.rect(bx - 2, fy0 + height // 2, bx + 3, fy0 + height // 2 + 1, 0.30)
        for hy in (fy0 + 8, fy0 + height // 2 + 6, fy1 - 10):
            for hx in (fx0 + 3, fx1 - 5):
                T.rect(hx, hy, hx + 2, hy + 3, 0.28)
    # roof strip and shaded end
    roof = poly_mask(W, Hh, [(fx0, fy0), (fx1 + 1, fy0), (fx1 + 1 + end_w, fy0 - top_h), (fx0 + end_w, fy0 - top_h)])
    T.mask(roof, 0.90)
    T.t = np.where(roof & (((xx - yy) % 4) == 0), 0.74, T.t)
    end = poly_mask(W, Hh, [(fx1 + 1, fy0), (fx1 + 1 + end_w, fy0 - top_h), (fx1 + 1 + end_w, fy1 - top_h), (fx1 + 1, fy1 + 1)])
    T.mask(end, 0.26)
    T.t = np.where(end & (((yy + xx) % 5) == 0), 0.18, T.t)
    L = T.layer(PAINTS[paint], dither=0.4, grain=0.05, seed=seed + 1)

    # rust: weeping from the top rail, eating the bottom, blooming round dents
    rn = fbm((Hh, W), seed + 2, 7, 9, octaves=3)
    streak = fbm((Hh, W), seed + 3, 1.6, 14, octaves=2)
    low = np.clip((yy - (fy1 - 12)) / 12.0, 0, 1)
    high = np.clip(1 - (yy - fy0) / 16.0, 0, 1)
    rustm = face & ((rn + 0.35 * low > 0.78) | ((streak > 0.72) & (high > 0.2) & (rn > 0.5)))
    rt = 0.16 + 0.42 * rn + 0.2 * (rib - 0.6)
    RL = Layer(W, Hh)
    RL.put(toned(np.clip(rt, 0, 1), RUST, dither=0.5), rustm)
    L.paste(RL)

    if marks and not doors:
        # owner's block and number: pale paint, half gone
        bx, by = fx0 + 10 + int(r.integers(0, 10)), fy0 + 8
        for j in range(9):
            for i in range(26):
                if (j in (0, 1, 7, 8) or i < 3 or (3 < i < 26 and j in (3, 4, 5) and (i // 2) % 3 != 2)) and r.random() > 0.18:
                    if L.a[by + j, bx + i] and not rustm[by + j, bx + i]:
                        L.rgb[by + j, bx + i] = STENCIL[int((bx + i) % 4 >= 2)]
        nx, ny = fx1 - 34, fy0 + 7
        for row in range(2):
            for i in range(0, 26, 3):
                for j in range(4):
                    if r.random() > 0.3 and not rustm[ny + row * 6 + j, nx + i]:
                        L.rgb[ny + row * 6 + j, nx + i] = STENCIL[int((nx + i) % 4 >= 2)]
                        if r.random() > 0.5:
                            L.rgb[ny + row * 6 + j, nx + i + 1] = STENCIL[int((nx + i + 1) % 4 >= 2)]
    if tag:
        tx, ty = fx0 + length // 2 - 6, fy0 + height // 2 - 8
        for j, row in enumerate(SCORPION):
            for i, ch in enumerate(row):
                if ch == '#':
                    for sx_ in (0, 1):
                        for sy_ in (0, 1):
                            y_, x_ = ty + j * 2 + sy_, tx + i * 2 + sx_
                            if 0 <= y_ < Hh and 0 <= x_ < W and L.a[y_, x_]:
                                L.rgb[y_, x_] = TAG[int((x_ % 4) >= 2)]
    # bullet holes: a dark pip with a bright lip
    for _ in range(int(r.integers(3, 8))):
        hx, hy = int(r.integers(fx0 + 6, fx1 - 6)), int(r.integers(fy0 + 6, fy1 - 8))
        L.rgb[hy, hx] = (16, 8, 6)
        L.rgb[hy - 1, hx - 1] = PAINTS[paint][10]
    return L, fy1 + 1


def tilt(layer, deg, fill=None):
    """Rotate a painted piece without softening its pixels."""
    im = layer.image().rotate(deg, resample=Image.NEAREST, expand=True)
    return from_image(im)


# ---------------------------------------------------------------- rock, palm, hut, boats
ROCK = ramp(['#0c0a0e', '#201a1e', '#383030', '#544844', '#74645a', '#988674', '#bcaa90', '#dccca8'], 16)
PALM = ramp(['#0a1408', '#1a2c12', '#30481c', '#4e682c', '#748a42', '#a0ac62', '#c8cc8c'], 12)
THATCH = ramp(['#1e1206', '#42300e', '#6c5218', '#987828', '#c0a044', '#dcc46c', '#f0e09c'], 14)
BURLAP = ramp(['#1e160c', '#3e3018', '#62502a', '#887242', '#aa9660', '#c8b884', '#e2d6ac'], 14)
CAMO = ramp(['#0c1408', '#1e2a12', '#36421e', '#566030', '#7a8048', '#a09c68', '#c4bc90'], 12)
STEEL = ramp(['#0e1012', '#22262a', '#3c4246', '#5c6468', '#828a8c', '#aab0ae', '#d2d6ce'], 12)
BOATBLUE = ramp(['#081826', '#10304a', '#1c5074', '#30749c', '#58a0bc', '#94c8d4', '#d0e8e4'], 12)
BOATWHITE = ramp(['#322c24', '#5e564a', '#8c8474', '#b4ac98', '#d4ceb8', '#ece8d4', '#fbf8ec'], 12)
FLAGY = ramp(['#4a3004', '#8a5c08', '#c8900c', '#e8b824', '#f8dc64'], 8)


def rock(w=40, h=24, seed=1, sharp=0.6):
    """A lump of black lava: broken planes, lit from the upper left, pitted."""
    r = rng(seed)
    yy, xx = np.mgrid[0:h, 0:w]
    # an angular outline: a few corners at uneven radii, flat-footed
    n = int(r.integers(6, 9))
    angs = np.sort(r.uniform(np.pi, 2 * np.pi, n))
    angs[0], angs[-1] = np.pi, 2 * np.pi
    pts = []
    for a_ in angs:
        rad = r.uniform(0.62, 1.0)
        pts.append((w / 2.0 + np.cos(a_) * rad * (w / 2.0 - 1), (h - 1) + np.sin(a_) * rad * (h - 2)))
    pts = [(1, h - 1)] + pts + [(w - 2, h - 1)]
    m = poly_mask(w, h, pts)
    # facets: nearest of a few seeds, each a plane with its own tilt
    k = max(4, (w * h) // 150)
    px_ = r.uniform(0, w, k)
    py_ = r.uniform(0, h, k)
    slope = r.uniform(-1, 1, (k, 2))
    slope[:, 0] += (px_ - w / 2.0) / (w / 2.0) * 0.9           # planes fall away from the middle
    slope[:, 1] += (py_ - h * 0.4) / h * 1.2
    d = (xx[..., None] - px_) ** 2 + ((yy[..., None] - py_) * 1.5) ** 2
    cell = np.argmin(d, axis=-1)
    lit = -(slope[cell, 0] * 0.75 + slope[cell, 1] * 0.65)
    pit = fbm((h, w), seed + 3, 1.4, 1.4, octaves=2)
    grad = fbm((h, w), seed + 4, 6, 3, octaves=2)
    t = 0.36 + (0.20 + 0.14 * sharp) * np.clip(lit, -1.2, 1.2) + 0.10 * (pit - 0.5) + 0.10 * (grad - 0.5)
    t -= 0.20 * np.clip((yy - h * 0.55) / (h * 0.45), 0, 1)
    seam = ndi.morphological_gradient(cell, size=2) > 0
    t = np.where(seam, t - 0.08, t)
    top_edge = m & ~np.roll(m, 1, axis=0)
    t = np.where(top_edge & (xx < w * 0.7), t + 0.26, t)
    L = Layer(w, h)
    L.put(toned(np.clip(t, 0.02, 0.95), ROCK, dither=0.45), m)
    return L, h - 1


def palm(height=84, lean=10, seed=1, dead=0.3):
    """A wind-bent palm: ringed trunk, a ragged crown, a skirt of dead fronds."""
    r = rng(seed)
    W, Hh = 96, height + 30
    T = Tone(W, Hh)
    G = Tone(W, Hh)
    bx, by = W // 2 - lean, Hh - 1
    pts = []
    for i in range(height):
        u = i / float(height)
        cx = bx + lean * 2 * u ** 1.6
        cy = by - i
        wd = 3.2 - 1.4 * u
        pts.append((cx, cy))
        ring = (i % 4) < 2
        T.rect(cx - wd, cy, cx + wd, cy, 0.42 if ring else 0.30)
        T.px(cx - wd, cy, 0.86 if ring else 0.66)
        T.px(cx - wd + 1, cy, 0.66 if ring else 0.50)
        T.px(cx + wd, cy, 0.12)
    tx, ty = pts[-1]
    # fronds: arcs out of the crown, leaflets hanging off each
    n = 13
    for k in range(n):
        a0 = -np.pi * (0.04 + 0.92 * k / (n - 1.0)) + r.uniform(-0.08, 0.08)
        ln = r.uniform(26, 38)
        droop = r.uniform(0.022, 0.040)
        isdead = r.random() < dead and (k < 2 or k > n - 3)
        C = T if isdead else G
        px0, py0 = tx, ty
        for i in range(int(ln)):
            u = i / ln
            x_ = tx + np.cos(a0) * i
            y_ = ty + np.sin(a0) * i + droop * i * i
            C.px(x_, y_, 0.30 if isdead else 0.34)
            C.px(x_, y_ - 1, 0.62 if isdead else 0.78 - 0.2 * u)
            if i % 2 == 0 and i > 3:
                ll = int((1 - abs(u - 0.45) * 1.4) * 9)
                side = 1 if np.cos(a0) >= 0 else -1
                for j in range(1, max(ll, 1)):
                    C.px(x_ - side * j * 0.45, y_ + j, (0.20 + 0.05 * j) if isdead else (0.50 - 0.045 * j + 0.2 * (j < 2)))
                    if not isdead and j < 3:
                        C.px(x_ + side * j * 0.3, y_ - j, 0.70 - 0.1 * j)
    for dx, dy in ((-3, 1), (2, 2), (-1, 3), (4, 0)):       # fruit bunch
        T.rect(tx + dx, ty + dy, tx + dx + 1, ty + dy + 1, 0.50)
    L = T.layer(DRIFT, dither=0.3)
    L.paste(G.layer(PALM, dither=0.3))
    return L, Hh - 1, bx


def hut(seed=1):
    """A fisherman's shelter: driftwood frame, palm-mat walls, thatch, nets drying on the eave."""
    W, Hh = 84, 60
    r = rng(seed)
    yy, xx = np.mgrid[0:Hh, 0:W]
    T = Tone(W, Hh)
    wall = (xx >= 8) & (xx <= 74) & (yy >= 22) & (yy <= 56)
    weave = ((xx + yy) % 4 < 2) ^ ((xx - yy) % 6 < 3)
    t = 0.50 + 0.12 * weave + 0.10 * (fbm((Hh, W), seed, 6, 3) - 0.5) - 0.16 * np.clip((yy - 40) / 16.0, 0, 1)
    t -= 0.14 * np.clip((xx - 50) / 24.0, 0, 1)
    T.mask(wall, 0)
    T.t = np.where(wall, t, T.t)
    T.rect(30, 30, 46, 56, 0.05)                         # the doorway, a rag across it
    for i in range(30, 47):
        ln = 6 + int(3 * np.sin(i * 0.9))
        T.rect(i, 30, i, 30 + ln, 0.76 - 0.05 * ((i // 2) % 2))
    for px_ in (8, 28, 48, 74):                          # posts
        T.rect(px_, 20, px_ + 1, 57, 0.30)
        T.rect(px_, 20, px_, 57, 0.62)
    # thatch: a shaggy slope of palm, lit on top, ragged at the eave
    for i in range(0, W):
        u = i / float(W - 1)
        top = 8 + 6 * abs(u - 0.45) ** 1.3 * 4
        eave = 23 + 2 * np.sin(i * 0.8) + (i % 3 == 0) * 2
        for y_ in range(int(top), int(eave) + 1):
            v = (y_ - top) / max(eave - top, 1)
            T.px(i, y_, 0.90 - 0.55 * v + 0.10 * ((i + y_ * 2) % 3 == 0) - 0.10 * ((i * 7 + y_) % 5 == 0))
    L = T.layer(THATCH, dither=0.4, grain=0.06, seed=seed)
    # a net hung along the eave, floats on it
    N = Tone(W, Hh)
    for i in range(50, 80):
        ln = int(10 + 6 * np.sin((i - 50) / 30.0 * np.pi))
        for j in range(ln):
            if (i + j) % 2 == 0:
                N.px(i, 24 + j, 0.2 + 0.6 * ((i + 2 * j) % 3 == 0))
    L.paste(N.layer(NET, dither=0))
    F = Tone(W, Hh)
    for fx in (54, 63, 72):
        F.rect(fx, 27 + fx % 4, fx + 2, 29 + fx % 4, 0.6)
        F.px(fx, 27 + fx % 4, 0.95)
    L.paste(F.layer(FLOAT, dither=0))
    return L, 57


def fish_rack(n=9):
    """Poles and a line; the catch split and hung to dry."""
    W, Hh = 12 + n * 6, 30
    T = Tone(W, Hh)
    for px_ in (2, W - 4):
        T.rect(px_, 2, px_ + 1, Hh - 1, 0.30)
        T.rect(px_, 2, px_, Hh - 1, 0.66)
        T.line([(px_ - 2, Hh - 1), (px_ + 1, 10)], 0.36)
    for i in range(3, W - 3):
        T.px(i, 5 + int(1.5 * np.sin((i - 3) / float(W - 6) * np.pi)), 0.50)
    L = T.layer(DRIFT, dither=0)
    S = Tone(W, Hh)
    for k in range(n):
        fx = 7 + k * 6
        fy = 6 + int(1.5 * np.sin((fx - 3) / float(W - 6) * np.pi))
        for j in range(9):
            wd = 1 if j in (0, 8) else 2 if j in (1, 7) else 3
            for i in range(wd):
                S.px(fx + i - wd // 2, fy + j, 0.84 - 0.10 * i - 0.04 * j)
        S.px(fx, fy + 9, 0.5)
        S.px(fx - 1, fy + 10, 0.5)
        S.px(fx + 1, fy + 10, 0.5)
    L.paste(S.layer(GREY, dither=0.2))
    return L, Hh - 1


def skiff(length=74, paint=BOATBLUE, stripe=BOATWHITE, seed=1, motor=True, cargo=False):
    """A huri: the narrow fishing boat of this coast, hauled up on the sand, bow to the right."""
    W, Hh = length + 18, 34
    x = np.arange(W)
    yy, xx = np.mgrid[0:Hh, 0:W]
    x0, x1 = 12, 12 + length
    sheer = smooth(x, [(x0, 16), (x0 + length * 0.4, 18), (x0 + length * 0.8, 14), (x1, 6)], 3)
    keel = smooth(x, [(x0, 24), (x0 + 6, 28), (x0 + length * 0.7, 28), (x1 - 8, 22), (x1, 8)], 2)
    hull = (yy >= sheer[None, :]) & (yy <= keel[None, :]) & (xx >= x0) & (xx <= x1)
    s = np.clip((yy - sheer[None, :]) / np.maximum(keel - sheer, 1)[None, :], 0, 1)
    T = Tone(W, Hh)
    t = 0.72 - 0.42 * s + 0.08 * (fbm((Hh, W), seed, 10, 0.8) - 0.5) - 0.12 * np.clip((xx - x1 + 20) / 20.0, 0, 1)
    T.mask(hull, 0)
    T.t = np.where(hull, t, T.t)
    L = T.layer(paint, dither=0.4, grain=0.05, seed=seed)
    S = Tone(W, Hh)                                       # painted band under the rail, and the rail itself
    band = hull & (s > 0.12) & (s < 0.34)
    S.mask(band, 0.86)
    S.t = np.where(band & (((xx - x0) // 5) % 2 == 0) & (s > 0.2), 0.60, S.t)
    L.paste(S.layer(stripe, dither=0.2))
    R = Tone(W, Hh)
    rail = (np.abs(yy - sheer[None, :]) < 1.0) & (xx >= x0) & (xx <= x1)
    R.mask(rail, 0.50)
    R.t = np.where(rail & (yy < sheer[None, :]), 0.90, R.t)
    for tx_ in range(x0 + 14, x1 - 12, 16):               # thwarts seen over the rail
        R.rect(tx_, int(sheer[tx_]) - 1, tx_ + 4, int(sheer[tx_]) - 1, 0.70)
    R.rect(x1 - 1, 3, x1 + 1, 10, 0.44)                   # stem post
    R.rect(x1 - 1, 3, x1 - 1, 9, 0.86)
    L.paste(R.layer(DRIFT, dither=0.2))
    if motor:
        M = Tone(W, Hh)
        M.rect(4, 8, 11, 15, 0.42)                        # cowl
        M.rect(4, 8, 11, 9, 0.84)
        M.rect(4, 10, 5, 15, 0.66)
        M.rect(6, 16, 8, 26, 0.36)                        # leg
        M.rect(6, 16, 6, 26, 0.62)
        M.rect(3, 26, 10, 27, 0.30)                       # plate and screw
        M.rect(2, 28, 5, 30, 0.50)
        M.rect(12, 12, 16, 13, 0.30)                      # tiller
        L.paste(M.layer(STEEL, dither=0.2))
    if cargo:
        C = Tone(W, Hh)
        cx = x0 + int(length * 0.35)
        C.rect(cx, int(sheer[cx]) - 9, cx + 16, int(sheer[cx]) - 1, 0.56)
        C.rect(cx, int(sheer[cx]) - 9, cx + 16, int(sheer[cx]) - 9, 0.90)
        C.rect(cx + 8, int(sheer[cx]) - 9, cx + 8, int(sheer[cx]) - 1, 0.30)
        C.rect(cx + 20, int(sheer[cx + 20]) - 6, cx + 30, int(sheer[cx + 20]) - 1, 0.44)
        C.rect(cx + 20, int(sheer[cx + 20]) - 6, cx + 30, int(sheer[cx + 20]) - 6, 0.80)
        L.paste(C.layer(DRIFT, dither=0.3))
    return L, 29


# ---------------------------------------------------------------- the battery and loose kit
INK = np.array([18, 14, 10], dtype=np.uint8)
MISSILE = ramp(['#1a1c1a', '#3a3e38', '#5e6458', '#868c7c', '#aeb4a0', '#d2d6c4', '#f0f2e4'], 12)
REDP = ramp(['#2a0604', '#5a0e08', '#8e1c0e', '#be3418', '#e05c2c', '#f49458'], 8)
OLIVE = ramp(['#0e1408', '#1e2a10', '#34441c', '#4e622c', '#6e8440', '#94a85c', '#bccc88'], 12)
TYRE = ramp(['#08080a', '#16161a', '#2a2a2e', '#444448', '#626266'], 6)


def outlined(layer, color=INK):
    """Sprites that can be shot or stood behind carry the black line; scenery does not."""
    out = Layer(layer.w + 2, layer.h + 2)
    a = np.zeros((layer.h + 2, layer.w + 2), bool)
    a[1:-1, 1:-1] = layer.a
    grow = ndi.binary_dilation(a, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool))
    out.rgb[grow] = color
    out.a = grow.copy()
    sub = Layer(layer.w, layer.h)
    sub.rgb, sub.a = layer.rgb, layer.a
    out.paste(sub, 1, 1)
    return out


def sandbags(cols=5, rows=3, seed=1, taper=True):
    """A wall of filled sacks, laid like bricks and slumped."""
    bw, bh = 13, 6
    r = rng(seed)
    W, Hh = cols * bw + 8, rows * (bh - 1) + 3
    T = Tone(W, Hh)
    yy, xx = np.mgrid[0:Hh, 0:W]
    for row in range(rows):
        n = cols - (rows - 1 - row if taper else 0) if taper else cols
        n = cols - ((rows - 1 - row) if taper else 0)
        off = ((rows - 1 - row) * bw) // 2 if taper else (bw // 2 if row % 2 else 0)
        y0 = row * (bh - 1)
        for c in range(n):
            x0 = 3 + off + c * bw + int(r.integers(-1, 2))
            for j in range(bh):
                inset = 2 if j in (0, bh - 1) else 1 if j in (1, bh - 2) else 0
                for i in range(inset, bw - inset):
                    u, v = i / float(bw - 1), j / float(bh - 1)
                    t = 0.84 - 0.50 * v - 0.24 * u + 0.14 * (v < 0.3) * (u < 0.6)
                    if j == bh - 1 or i in (inset, bw - inset - 1):
                        t -= 0.22
                    t += 0.06 * ((i * 3 + j * 5 + c) % 4 == 0)
                    T.px(x0 + i, y0 + j, t)
            T.px(x0 + bw - 3, y0 + 2, 0.30)               # the tied ear
            T.px(x0 + bw - 2, y0 + 1, 0.60)
            for i in range(3, bw - 3, 3):
                T.px(x0 + i, y0 + bh - 2, 0.30)           # seam stitches
    L = T.layer(BURLAP, dither=0.4, grain=0.05, seed=seed)
    return L, Hh - 1


def drum(paint='oxide', seed=1, dented=False):
    """A 200-litre drum: rolled ribs, a filler cap, a faded band."""
    W, Hh = 13, 19
    T = Tone(W, Hh)
    for y in range(Hh):
        for x in range(W):
            if (y in (0, Hh - 1)) and x in (0, W - 1):
                continue
            u = x / float(W - 1)
            t = 0.30 + 0.62 * np.exp(-((u - 0.30) / 0.22) ** 2) - 0.14 * np.clip((u - 0.6) / 0.4, 0, 1)
            if y in (5, 6, 12, 13):
                t += 0.12 if y in (5, 12) else -0.14
            if y == 0:
                t = 0.90
            if y == Hh - 1:
                t = 0.14
            T.px(x, y, t)
    L = T.layer(PAINTS[paint], dither=0.3, grain=0.04, seed=seed)
    B = Tone(W, Hh)
    for x in range(W):
        u = x / float(W - 1)
        for y in (8, 9, 10):
            B.px(x, y, 0.40 + 0.5 * np.exp(-((u - 0.30) / 0.22) ** 2))
    L.paste(B.layer(PAINTS['white'], dither=0.3))
    L.rgb[1, 3] = (20, 16, 12)
    L.rgb[1, 4] = (20, 16, 12)
    return outlined(L), Hh + 1


def crate(seed=1, mark=True):
    """An ammunition box: battens, rope handles, a stencil."""
    W, Hh = 24, 15
    T = Tone(W, Hh)
    yy, xx = np.mgrid[0:Hh, 0:W]
    g = fbm((Hh, W), seed, 8, 0.7, octaves=2)
    t = 0.62 + 0.14 * (g - 0.5) - 0.16 * (yy / float(Hh)) - 0.10 * (xx / float(W))
    t = np.where((yy % 5) == 4, t - 0.2, t)
    T.mask(np.ones((Hh, W), bool), 0)
    T.t = t
    for bx in (2, W - 5):
        T.rect(bx, 0, bx + 2, Hh - 1, 0.52)
        T.rect(bx, 0, bx, Hh - 1, 0.84)
        T.rect(bx + 2, 0, bx + 2, Hh - 1, 0.30)
    T.rect(0, 0, W - 1, 0, 0.90)
    T.rect(0, Hh - 1, W - 1, Hh - 1, 0.18)
    L = T.layer(DRIFT, dither=0.35)
    if mark:
        for (i, j) in ((8, 5), (9, 5), (10, 5), (12, 5), (13, 5), (15, 5), (8, 7), (10, 7), (11, 7), (13, 7), (14, 7),
                       (15, 7), (8, 9), (9, 9), (11, 9), (12, 9), (14, 9)):
            L.rgb[j, i] = (30, 22, 14)
    return outlined(L), Hh + 1


def missile_launcher(seed=1):
    """The coast battery's piece: a sea-skimmer on its rail, on a two-wheel trailer, nose art and all."""
    W, Hh = 96, 62
    T = Tone(W, Hh)
    ang = np.radians(20)
    ca, sa = np.cos(ang), np.sin(ang)

    def along(d, off):
        """Point d pixels along the rail from its heel, off pixels above it."""
        return 12 + d * ca + off * sa, 46 - d * sa + off * ca * -1 + 0 * d

    # trailer: bed, drawbar, jack, wheel
    O = Tone(W, Hh)
    O.rect(8, 46, 62, 49, 0.50)
    O.rect(8, 46, 62, 46, 0.86)
    O.rect(8, 49, 62, 49, 0.22)
    O.line([(62, 47), (84, 51)], 0.44, 2)                 # drawbar
    O.rect(82, 50, 84, 59, 0.36)                          # jack
    O.rect(80, 59, 86, 60, 0.30)
    # the cradle: A-frame lifting the rail
    O.line([(24, 46), (30, 30)], 0.40, 2)
    O.line([(50, 46), (44, 25)], 0.40, 2)
    O.line([(30, 30), (50, 46)], 0.30)
    # rail
    for d in range(0, 66):
        x_, y_ = 10 + d * ca, 44 - d * sa
        O.rect(x_, y_, x_, y_ + 2, 0.46)
        O.px(x_, y_, 0.84)
        if d % 6 == 0:
            O.px(x_, y_ + 3, 0.30)
    L = O.layer(OLIVE, dither=0.3, grain=0.05, seed=seed)
    # wheel
    Wh = Tone(W, Hh)
    yy, xx = np.mgrid[0:Hh, 0:W]
    rr = np.sqrt((xx - 34) ** 2 + (yy - 53) ** 2)
    Wh.mask(rr <= 8.2, 0.30)
    Wh.t = np.where((rr <= 8.2) & (rr > 6.5), 0.22 + 0.25 * ((np.arctan2(yy - 53, xx - 34) * 4 % 1.0) > 0.5), Wh.t)
    Wh.t = np.where((rr <= 8.2) & (yy < 50) & (rr > 6.0), Wh.t + 0.30, Wh.t)
    L.paste(Wh.layer(TYRE, dither=0.2))
    Hb = Tone(W, Hh)
    Hb.mask(rr <= 3.6, 0.50)
    Hb.t = np.where((rr <= 3.6) & (yy < 53) & (xx < 35), 0.86, Hb.t)
    Hb.mask(rr <= 1.2, 0.20)
    L.paste(Hb.layer(OLIVE, dither=0.2))
    # the missile: a fat tube, lit along its back, wings and a tail, a red nose with teeth
    Mi = Tone(W, Hh)
    Rn = Tone(W, Hh)
    length, rad = 62, 4.6
    for d in range(-2, length):
        cx, cy = 14 + d * ca, 39 - d * sa
        rloc = rad
        if d > length - 12:
            rloc = rad * np.sqrt(max(0.0, 1 - ((d - (length - 12)) / 12.0) ** 2)) + 0.4
        if d < 4:
            rloc = rad * (0.7 + 0.075 * d)
        for o in np.arange(-rloc, rloc + 0.5, 0.5):
            x_, y_ = cx + o * sa, cy + o * ca
            v = (o + rloc) / (2 * rloc + 1e-6)             # 0 top, 1 belly
            t = 0.92 - 0.62 * v + 0.10 * (v < 0.25)
            C = Rn if d > length - 11 else Mi
            C.px(x_, y_, t)
        if d in (18, 19, 40, 41):
            for o in np.arange(-rad, rad + 0.5, 0.5):
                Mi.px(cx + o * sa, cy + o * ca, 0.30)       # body bands
    # wings and fins
    for d in range(22, 38):
        cx, cy = 14 + d * ca, 39 - d * sa
        span = (d - 22) * 0.55
        for o in np.arange(rad, rad + span, 0.5):
            Mi.px(cx + o * sa, cy + o * ca, 0.40)
        for o in np.arange(-rad - span * 0.8, -rad, 0.5):
            Mi.px(cx + o * sa, cy + o * ca, 0.84)
    for d in range(0, 9):
        cx, cy = 14 + d * ca, 39 - d * sa
        for o in np.arange(-rad - (9 - d) * 0.9, -rad + 1, 0.5):
            Mi.px(cx + o * sa, cy + o * ca, 0.78)
        for o in np.arange(rad - 1, rad + (9 - d) * 0.7, 0.5):
            Mi.px(cx + o * sa, cy + o * ca, 0.36)
    L.paste(Mi.layer(MISSILE, dither=0.3, grain=0.04, seed=seed + 2))
    L.paste(Rn.layer(REDP, dither=0.3))
    # nose art: an eye and a row of teeth
    ex, ey = int(14 + (length - 15) * ca - 1.5 * sa), int(39 - (length - 15) * sa - 1.5 * ca)
    L.rgb[ey, ex] = (250, 246, 230)
    L.rgb[ey, ex + 1] = (16, 12, 10)
    for k in range(5):
        tx_, ty_ = int(14 + (length - 13 + k * 2) * ca + 2.5 * sa), int(39 - (length - 13 + k * 2) * sa + 2.5 * ca)
        if 0 <= ty_ < Hh and 0 <= tx_ < W and L.a[ty_, tx_]:
            L.rgb[ty_, tx_] = (250, 246, 230)
    return outlined(L), 62


def flag(seed=1, h=58):
    """The Scorpion's colour: yellow field, black device, on a crooked pole."""
    W, Hh = 44, h
    T = Tone(W, Hh)
    for y in range(Hh):
        T.rect(3, y, 4, y, 0.36)
        T.px(3, y, 0.72)
    L = T.layer(DRIFT, dither=0)
    F = Tone(W, Hh)
    fw, fh = 34, 20
    cols = {}
    for i in range(fw):
        wave = 2.2 * np.sin(i / 5.0 + 0.6) * (i / float(fw))
        for j in range(fh):
            y_ = int(3 + j + wave)
            t = 0.70 + 0.22 * np.cos(i / 5.0 + 0.6) - 0.10 * (j / float(fh))
            F.px(6 + i, y_, t)
            cols[(i, j)] = (6 + i, y_)
    L.paste(F.layer(FLAGY, dither=0.3))
    for j, row in enumerate(SCORPION):
        for i, ch in enumerate(row):
            if ch == '#' and (i + 10, j + 3) in cols:
                x_, y_ = cols[(i + 10, j + 3)]
                L.rgb[y_, x_] = (22, 16, 10)
    return L, Hh - 1


def camo_net(w=120, h=40, seed=1):
    """Netting strung on poles over the battery: scalloped, mottled, full of holes."""
    r = rng(seed)
    W, Hh = w, h + 22
    T = Tone(W, Hh)
    P = Tone(W, Hh)
    posts = [4, w // 3, 2 * w // 3, w - 5]
    for px_ in posts:
        P.rect(px_, 4, px_ + 1, Hh - 1, 0.30)
        P.rect(px_, 4, px_, Hh - 1, 0.66)
    L = P.layer(DRIFT, dither=0)
    yy, xx = np.mgrid[0:Hh, 0:W]
    top = np.zeros(W)
    for a_, b_ in zip(posts[:-1], posts[1:]):
        xs = np.arange(a_, b_ + 1)
        u = (xs - a_) / float(b_ - a_)
        top[a_:b_ + 1] = 5 + 7 * np.sin(np.pi * u)
    top[:posts[0]] = 5
    top[posts[-1]:] = 5
    bottom = top + h * 0.55 + 6 * noise((1, W), seed, 8, 0.5)[0] + 3 * np.sin(np.arange(W) / 4.0)
    m = (yy >= top[None, :]) & (yy <= bottom[None, :]) & (xx >= posts[0] - 2) & (xx <= posts[-1] + 3)
    blot = fbm((Hh, W), seed + 1, 6, 4, octaves=3)
    holes = fbm((Hh, W), seed + 2, 2.2, 2.2, octaves=2) > 0.70
    t = 0.30 + 0.55 * blot - 0.22 * np.clip((yy - top[None, :]) / (h * 0.6), 0, 1)
    t = np.where(np.abs(yy - top[None, :]) < 1, 0.86, t)
    m2 = m & ~(holes & (yy > top[None, :] + 1))
    T.mask(m2, 0)
    T.t = np.where(m2, t, T.t)
    L.paste(T.layer(CAMO, dither=0.5))
    return L, Hh - 1


def watchtower(seed=1):
    """Four poles, a platform, a square of thatch: the battery's lookout."""
    W, Hh = 46, 96
    T = Tone(W, Hh)
    for px_, lean in ((6, 0.05), (38, -0.05), (14, 0.02), (30, -0.02)):
        for y in range(18, Hh):
            x_ = px_ + lean * (Hh - y)
            T.rect(x_, y, x_ + 1, y, 0.30 if px_ in (14, 30) else 0.38)
            T.px(x_, y, 0.56 if px_ in (14, 30) else 0.80)
    T.line([(8, 90), (38, 62)], 0.36)                     # braces
    T.line([(38, 90), (8, 62)], 0.30)
    T.rect(2, 46, 43, 48, 0.50)                           # platform
    T.rect(2, 46, 43, 46, 0.90)
    T.rect(2, 49, 43, 49, 0.18)
    T.rect(3, 36, 42, 36, 0.60)                           # rail
    for px_ in range(4, 43, 6):
        T.rect(px_, 36, px_, 46, 0.42)
    for y in range(50, Hh, 5):                            # ladder
        T.rect(19, y, 26, y, 0.52)
    T.rect(19, 49, 19, Hh - 1, 0.44)
    T.rect(26, 49, 26, Hh - 1, 0.30)
    L = T.layer(DRIFT, dither=0.2)
    R = Tone(W, Hh)
    for i in range(W):
        u = i / float(W - 1)
        top = 6 + 5 * abs(u - 0.5) * 2
        eave = 18 + 2 * np.sin(i * 0.9) + 2 * (i % 3 == 0)
        for y_ in range(int(top), int(eave) + 1):
            v = (y_ - top) / max(eave - top, 1)
            R.px(i, y_, 0.90 - 0.55 * v + 0.10 * ((i + y_ * 2) % 3 == 0))
    L.paste(R.layer(THATCH, dither=0.4))
    return L, Hh - 1, 46


def dish(seed=1):
    """A television dish pressed into service, on a scaffold pole."""
    W, Hh = 30, 44
    T = Tone(W, Hh)
    T.rect(14, 18, 15, Hh - 1, 0.34)
    T.rect(14, 18, 14, Hh - 1, 0.70)
    T.line([(8, Hh - 1), (14, 30)], 0.36)
    yy, xx = np.mgrid[0:Hh, 0:W]
    e = ((xx - 14) / 13.0) ** 2 + ((yy - 12) / 10.0) ** 2
    m = e <= 1
    t = 0.86 - 0.5 * np.clip(((xx - 8) / 20.0) ** 2 + ((yy - 7) / 16.0) ** 2, 0, 1)
    T.mask(m, 0)
    T.t = np.where(m, t, T.t)
    T.t = np.where(m & (e > 0.82), 0.40, T.t)
    T.line([(14, 12), (26, 3)], 0.30)
    T.rect(25, 2, 27, 4, 0.50)
    L = T.layer(STEEL, dither=0.3)
    return L, Hh - 1


def sink(layer, rows, seed=1, wave=2.0):
    """Bury the foot of a piece: sand has drifted up an uneven line."""
    out = Layer(layer.w, layer.h)
    out.rgb, out.a = layer.rgb.copy(), layer.a.copy()
    n = noise((1, layer.w), seed, 9, 0.5)[0]
    line = layer.h - rows + (n - 0.5) * 2 * wave
    yy = np.arange(layer.h)[:, None]
    out.a &= yy < line[None, :]
    return out


def cast_shadow(layer, base_row, reach=0.55, drop=0.16):
    """Where a piece's shadow falls on flat ground, light coming from the upper left.
    Returns a mask in the piece's own frame, widened to the right."""
    h, w = layer.a.shape
    ext = int(h * reach) + 2
    m = np.zeros((h + int(h * drop) + 3, w + ext), bool)
    ys, xs = np.nonzero(layer.a)
    hgt = np.clip(base_row - ys, 0, None)
    sx = (xs + hgt * reach).astype(int)
    sy = (base_row + hgt * drop).astype(int)
    ok = (sy >= 0) & (sy < m.shape[0]) & (sx >= 0) & (sx < m.shape[1])
    m[sy[ok], sx[ok]] = True
    m = ndi.binary_closing(m, iterations=1)
    return m


def flipflops(n=60, w=120, h=26, seed=1):
    """A burst container's cargo: beach sandals, one colour each, strewn downwind."""
    r = rng(seed)
    L = Layer(w, h)
    cols = [(232, 84, 110), (64, 150, 210), (244, 200, 60), (88, 184, 110), (240, 130, 50), (250, 246, 230)]
    for _ in range(n):
        x = int(np.clip(r.normal(w * 0.3, w * 0.25), 1, w - 4))
        y = int(np.clip(r.normal(h * 0.55, h * 0.22), 1, h - 3))
        c = cols[int(r.integers(0, len(cols)))]
        d = (max(c[0] - 90, 0), max(c[1] - 90, 0), max(c[2] - 90, 0))
        if r.random() < 0.5:
            pts = [(0, 0, c), (1, 0, c), (2, 0, c), (0, 1, d), (1, 1, d), (2, 1, d)]
        else:
            pts = [(0, 0, c), (1, 0, c), (0, 1, c), (1, 1, d), (0, 2, d)]
        for dx, dy, cc in pts:
            if 0 <= y + dy < h and 0 <= x + dx < w:
                L.rgb[y + dy, x + dx] = cc
                L.a[y + dy, x + dx] = True
    return L


def campfire(seed=1):
    """Three stones, a blackened pot, a thread of smoke."""
    W, Hh = 26, 40
    T = Tone(W, Hh)
    for (x0, y0, wd) in ((3, 34, 6), (16, 34, 7), (9, 36, 6)):
        T.rect(x0, y0, x0 + wd, y0 + 3, 0.36)
        T.rect(x0, y0, x0 + wd - 2, y0, 0.70)
    L = T.layer(ROCK, dither=0.2)
    P = Tone(W, Hh)
    for y in range(24, 35):
        half = 6 if 26 <= y <= 32 else 5
        for x in range(13 - half, 13 + half + 1):
            u = (x - (13 - half)) / float(2 * half)
            P.px(x, y, 0.20 + 0.5 * np.exp(-((u - 0.3) / 0.2) ** 2))
    P.rect(6, 23, 20, 23, 0.74)
    P.rect(4, 25, 5, 26, 0.5)
    P.rect(21, 25, 22, 26, 0.3)
    L.paste(P.layer(STEEL, dither=0.3))
    S = Layer(W, Hh)
    r = rng(seed)
    for i in range(22):
        x = 13 + int(3 * np.sin(i / 3.0) + i * 0.25)
        y = 21 - i
        for dx in range(-1 - i // 9, 2 + i // 9):
            if r.random() < 0.7 - i * 0.02 and 0 <= x + dx < W and y >= 0:
                S.rgb[y, x + dx] = (214, 206, 186) if (dx + i) % 2 else (168, 160, 144)
                S.a[y, x + dx] = True
    L.paste(S)
    F = Layer(W, Hh)
    for (x, y, c) in ((10, 35, (248, 200, 60)), (12, 34, (244, 130, 40)), (14, 35, (248, 220, 120)), (16, 35, (220, 80, 30))):
        F.rgb[y, x] = c
        F.a[y, x] = True
    L.paste(F)
    return L, 38


FIRE = ramp(['#1a0c08', '#4a1408', '#8c2408', '#cc4a0c', '#f08418', '#fcbc3c', '#fff08c', '#fffbe6'], 16)
SMOKE = ramp(['#2a221c', '#463c32', '#64584a', '#847866', '#a49a86', '#c4bca8'], 10)


def explosion(r=22, seed=1, smoke=True):
    """A drum going up: a white-hot core, tongues of orange, black smoke rolling off the top."""
    rg = rng(seed)
    W = Hh = r * 4
    yy, xx = np.mgrid[0:Hh, 0:W]
    cx, cy = W / 2.0, Hh * 0.60
    L = Layer(W, Hh)
    if smoke:
        Z = np.zeros((Hh, W))
        for i in range(9):
            a_ = rg.uniform(-np.pi * 0.85, -np.pi * 0.15)
            d_ = rg.uniform(0.6, 1.2) * r
            px_, py_ = cx + np.cos(a_) * d_ * 0.9, cy + np.sin(a_) * d_ - r * 0.35
            rad = rg.uniform(0.28, 0.5) * r
            z = np.sqrt(np.clip(rad * rad - ((xx - px_) ** 2 + (yy - py_) ** 2), 0, None))
            Z = np.maximum(Z, z)
        lit = light(ndi.gaussian_filter(Z, 0.8), -0.6, -0.8, 0.35)
        t = 0.34 + 0.40 * np.clip(lit, -1, 1) + 0.10 * (fbm((Hh, W), seed, 3, 3) - 0.5)
        L.put(toned(np.clip(t, 0, 1), SMOKE, dither=0.5), Z > 0.5)
    ang = np.arctan2(yy - cy, xx - cx)
    dist = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.08) ** 2)
    n1 = fbm((Hh, W), seed + 1, 5, 5, octaves=3)
    spikes = 0.82 + 0.26 * np.sin(ang * 7 + n1 * 5) * np.sin(ang * 3 + 1.3) + 0.30 * (n1 - 0.5)
    rad = r * spikes
    heat = np.clip(1 - dist / np.maximum(rad, 1), 0, 1)
    m = heat > 0.02
    t = 0.30 + 0.86 * heat ** 0.55 + 0.12 * (fbm((Hh, W), seed + 2, 2.5, 2.5, octaves=2) - 0.5)
    FL = Layer(W, Hh)
    FL.put(toned(np.clip(t, 0, 1), FIRE, dither=0.5), m)
    L.paste(FL)
    # sparks and flung grit
    for i in range(26):
        a_ = rg.uniform(-np.pi * 1.1, 0.1 * np.pi)
        d_ = rg.uniform(1.05, 1.7) * r
        x_, y_ = int(cx + np.cos(a_) * d_), int(cy + np.sin(a_) * d_)
        if 1 <= x_ < W - 1 and 1 <= y_ < Hh - 1:
            L.rgb[y_, x_] = FIRE[int(rg.integers(10, 15))]
            L.a[y_, x_] = True
            if i % 3 == 0:
                L.rgb[y_, x_ + 1] = FIRE[9]
                L.a[y_, x_ + 1] = True
    return L, int(cy + r * 0.8)


def sea_mine(seed=1):
    """A contact mine washed up and half buried: a rusted ball, lead horns, a link of chain."""
    W, Hh = 34, 30
    yy, xx = np.mgrid[0:Hh, 0:W]
    cx, cy, r = 16.0, 15.0, 11.0
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    m = d <= r
    z = np.sqrt(np.clip(r * r - (xx - cx) ** 2 - (yy - cy) ** 2, 0, None))
    lit = light(z, -0.7, -0.7, 0.16)
    pit = fbm((Hh, W), seed, 2.0, 2.0, octaves=2)
    t = 0.34 + 0.40 * np.clip(lit, -1, 1) + 0.16 * (pit - 0.5)
    T = Tone(W, Hh)
    T.mask(m, 0)
    T.t = np.where(m, t, T.t)
    seam = m & (np.abs(yy - cy - 1) < 0.7)
    T.t = np.where(seam, T.t - 0.16, T.t)
    L = T.layer(RUST, dither=0.5, grain=0.06, seed=seed)
    Hn = Tone(W, Hh)
    for a_ in (-2.6, -2.0, -1.4, -0.9, -0.3):
        for k in range(0, 5):
            x_, y_ = cx + np.cos(a_) * (r - 1 + k), cy + np.sin(a_) * (r - 1 + k)
            Hn.rect(x_, y_, x_ + 1, y_ + 1, 0.60 if k < 4 else 0.90)
    for (hx, hy) in ((11, 11), (19, 9), (22, 15)):          # horns facing us
        Hn.rect(hx, hy, hx + 1, hy + 1, 0.40)
        Hn.px(hx, hy, 0.92)
    L.paste(Hn.layer(STEEL, dither=0.2))
    C = Tone(W, Hh)
    for i, (x_, y_) in enumerate(((27, 24), (29, 25), (31, 26), (33, 27))):
        C.rect(x_, y_, x_ + 1, y_ + 1, 0.3 + 0.3 * (i % 2))
    L.paste(C.layer(STEEL, dither=0))
    return L, 25


def jetty(n=7, seed=1):
    """What is left of a landing stage: leaning piles, a few planks still spiked down."""
    W, Hh = n * 16 + 10, 30
    r = rng(seed)
    T = Tone(W, Hh)
    for i in range(n):
        x0 = 4 + i * 16 + int(r.integers(-1, 2))
        top = 6 + int(r.integers(0, 5)) + (i * 2)
        lean = r.uniform(-0.08, 0.08)
        for y in range(top, Hh):
            x_ = x0 + lean * (y - top)
            T.rect(x_, y, x_ + 2, y, 0.36)
            T.px(x_, y, 0.78)
            T.px(x_ + 2, y, 0.16)
        T.rect(x0 - 1, top, x0 + 3, top, 0.86)
        if i < n - 1 and r.random() < 0.75:
            T.rect(x0 + 2, top + 3 + i % 2, x0 + 17, top + 4 + i % 2, 0.56)
            T.rect(x0 + 2, top + 3 + i % 2, x0 + 17, top + 3 + i % 2, 0.84)
    L = T.layer(DRIFT, dither=0.3)
    return L, Hh - 1


if __name__ == '__main__':
    bg = Layer(470, 200)
    bg.rgb[:] = (222, 184, 112); bg.a[:] = True
    s, f = sandbags(5, 3, seed=2)
    bg.paste(s, 4, 60 - s.h)
    s2, f = sandbags(3, 2, seed=3, taper=False)
    bg.paste(s2, 84, 60 - s2.h)
    for i, pnt in enumerate(['oxide', 'blue', 'green']):
        d_, f = drum(pnt, seed=i)
        bg.paste(d_, 140 + i * 16, 60 - d_.h)
    c_, f = crate(seed=2)
    bg.paste(c_, 196, 60 - c_.h)
    ml, f = missile_launcher()
    bg.paste(ml, 230, 2)
    fl, f = flag()
    bg.paste(fl, 336, 2)
    wt, f, plat = watchtower()
    bg.paste(wt, 390, 2)
    cn, f = camo_net()
    bg.paste(cn, 4, 100)
    ds, f = dish()
    bg.paste(ds, 140, 110)
    im = bg.image()
    im = im.resize((im.width * 4, im.height * 4), Image.NEAREST)
    im.save('t3_prop.png')
    print(im.size)
