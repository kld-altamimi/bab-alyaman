# stage_ibb.py - Ibb, the Green Valleys (Mission 4), painted as the other missions are: tone fields mapped through colour
# ramps, checker dither between neighbours, light from the upper left, no outlines on scenery.
# Stage 3 of Ibb's plan (24 Oct): the four zones, one at a time, each shown to Khaled before it goes in. Zone 1 first:
# Wadi al-Sahul, the valley road up from Taiz in the rainy season: the greenest place in Yemen, terraced to the tops of its
# mountains, cloud sitting on them, a road along the valley floor with a farmhouse, a roadside shop, a minibus that has
# given up, the Zanabeel's posters on every wall and loudspeakers on the poles (scenery only: nothing to take over).
# Layers, back to front: the sky (wraps), the far mountains (wrap), the nearer terraced hills (wrap), the zone's long
# picture (the road and everything on it), and a foreground passing close to the lens. Where the floor and the tops of
# things are is recorded as it is painted (PLATS), so the level can be checked against the picture.
import numpy as np
from scipy import ndimage as ndi
from paint import *
import stage as ST
import stage_long as SL
import stage_mocha as SM
import stage_taiz as STZ

SW, SH = 468, 216
WALK = 184                                 # where feet land on the road
ROADB = 170                                # the road's back edge: the bank behind it starts here
Z1 = 1280                                  # zone 1's length
put_tone = SM.put_tone

# ------------------------------------------------------------------ colour ramps (dark to pale)
SKYI = ramp(['#2e4c6c', '#3c5c7a', '#4e6e8a', '#648298', '#7c96a6', '#96aab4', '#b0c0c4', '#c8d4d2', '#dce4e0', '#eef2ec', '#fafcf6'], 22)
MOUNT = ramp(['#16281c', '#203624', '#2c462c', '#3a5836', '#4a6a40', '#5c7c4c', '#709060', '#88a274', '#a2b48a', '#bac4a2',
              '#d0d6bc', '#e2e6d4', '#f0f2e8'], 26)                                                              # the mountains, near to far in the haze
TERR = ramp(['#10200e', '#1a3216', '#24461c', '#305a24', '#3e6e2c', '#4e8234', '#62963e', '#7aaa4c', '#96bc62', '#b4cc80'], 20)   # crops on the terraces
DRYST = ramp(['#1e1a14', '#36302a', '#4e4840', '#686056', '#827a6e', '#9c9486', '#b6ae9e', '#cec8b8'], 14)          # dry-stone walls, grey
BASALT = STZ.BASALT
TSTONE = STZ.TSTONE
LIME = SM.LIME
ROAD = ramp(['#0e0e10', '#1a1a1c', '#28282a', '#36363a', '#46464a', '#58585a', '#6c6c6c', '#828280'], 14)        # wet asphalt
GRAVEL = ramp(['#1c1814', '#3a332a', '#5a5044', '#7a6e5e', '#9a8e7a', '#b8ac96'], 12)
MUDI = ramp(['#160e08', '#2c1c10', '#46301a', '#604428', '#7c5a38', '#98744c'], 12)                               # wet earth
LEAF = ramp(['#081408', '#10220e', '#1a3414', '#26481c', '#345e24', '#46742e', '#5c8a3a', '#78a24a', '#98ba62'], 18)   # trees, bushes
BANANA = ramp(['#0e1e0a', '#1c3412', '#2c4c1a', '#3e6624', '#548230', '#6e9c3c', '#8cb44c', '#acca6a'], 16)
WATER = ramp(['#16242a', '#24383e', '#344e52', '#486668', '#628080', '#82a0a0', '#a8c0bc', '#d0e0d8'], 14)
TIN = ramp(['#141416', '#262628', '#3a3a3a', '#504e4c', '#686460', '#827c76', '#9e968c', '#bab2a4'], 14)       # corrugated iron
RUSTI = ramp(['#1c0c06', '#3a180a', '#5c2a12', '#7e401c', '#9e5828', '#ba7436', '#d29650'], 12)
BUSW = ramp(['#2a2a2c', '#4c4c4e', '#727270', '#989690', '#bcb8ae', '#d8d4c8', '#eeeae0'], 12)                  # a white minibus, grimy
BUSB = ramp(['#081626', '#0e2640', '#183c5e', '#265680', '#3c74a0', '#5c94bc'], 10)                             # its stripe
REDP = ramp(['#240604', '#4a0c08', '#741410', '#9c2218', '#c03624', '#d85a3c', '#ec8a64'], 12)                  # the Zanabeel's red
GOLD = ramp(['#3a2404', '#6a440a', '#9a6a14', '#c49020', '#e2b43c', '#f4d470', '#fcecac'], 12)
WOOD = SM.TEAK
SOOT = SM.SOOT

PLATS = {}            # id -> [[x, y], ...] as painted
INFO = {}             # what else the level needs to know (where the screens' crates stand, the shop's door)


def plat(pid, pts):
    PLATS[pid] = [[int(x), int(y)] for x, y in pts]


def wrapfbm(shape, seed, sx, sy, octaves=3):
    return fbm(shape, seed, sx, sy, octaves=octaves)          # (paint.noise filters with mode='wrap': it tiles)


# ------------------------------------------------------------------ the sky: the morning after rain
def sky_i(w=1404, seed=5):
    """A washed blue overhead going pale and misty low down; big soft clouds, lit white on top, grey under, and a thin veil
    of stratus across the middle."""
    h = 124
    yy = np.arange(h)[:, None] / float(h)
    xx = np.arange(w)[None, :]
    tone = 0.18 + 0.78 * np.clip(yy, 0, 1) ** 1.5 + 0 * xx
    veil = wrapfbm((h, w), seed, 70, 2.0)
    tone += np.clip(veil - 0.55, 0, 1) * 0.55 * np.exp(-((yy - 0.42) / 0.14) ** 2)
    big = [(120, 70, 190, 50, 170, 4.0, 11.0), (420, 60, 150, 36, 120, 3.5, 9.0), (700, 74, 220, 56, 190, 4.0, 12.0),
           (980, 58, 130, 30, 100, 3.5, 8.0), (1220, 70, 200, 48, 170, 4.0, 11.0)]
    Z = SL.puffs_wrap(h, w, big, seed + 41)
    Zs = ndi.gaussian_filter(Z, 0.8, mode='wrap')
    cov = np.clip(Z * 0.8, 0, 1)
    lit = light(Zs, -0.55, -0.85, 0.5)
    floor = np.zeros((h, w))
    for cx, base, width, height, n, r0, r1 in big:
        dx = (xx - cx + w / 2.0) % w - w / 2.0
        f = np.clip(1 - (base - np.arange(h)[:, None]) / (height * 0.6), 0, 1) * (np.abs(dx) < width * 0.62)
        floor = np.maximum(floor, f)
    shade = noise((h, w), seed + 50, 22, 12)
    ct = 0.84 + 0.36 * np.clip(lit, -1, 1) - 0.36 * floor ** 1.4 - 0.10 * (shade - 0.5)
    cov = cov * (1 - 0.4 * floor ** 3)
    tone = tone + cov * (np.clip(ct, 0.40, 1.0) - tone)
    L = Layer(w, h)
    L.put(toned(np.clip(tone, 0, 1), SKYI, dither=0.7), np.ones((h, w), bool))
    return L


# ------------------------------------------------------------------ the mountains, terraced to their tops
HAZEB = ramp(['#30506c', '#3e5e7a', '#4e6e88', '#628096', '#7892a4', '#90a6b4', '#a8bac4', '#c0ced4', '#d8e2e4', '#eef2f0'], 20)   # the farthest range, blue in the haze
HAZEG = ramp(['#1e3226', '#284030', '#344e3a', '#405e46', '#4e6e52', '#5e7e60', '#70906e', '#86a280', '#9eb494', '#b8c8ac',
              '#d2dcc8', '#e8eee2'], 24)                                                                       # the nearer range: green, hazed
HOUSEF = ramp(['#3c4440', '#56605a', '#727a72', '#90968c', '#b0b2a6', '#ccccbe', '#e4e2d4', '#f6f4e8'], 14)  # stone houses, far off


def crest_profile(w, seed, base, n, hmin, hmax, wmin, wmax, sharp=1.5, rough=2.5):
    """A range's skyline, wrapping: n peaks, each a concave cone (steep near the top), the highest wins where they meet;
    a little roughness on top. -> (the skyline's y in each column, [(x, top y)] of the peaks)."""
    r = rng(seed)
    x = np.arange(w, dtype=float)
    y = np.full(w, float(base))
    tops = []
    for i in range(n):
        cx = (i + r.uniform(0.15, 0.85)) * w / float(n)
        hh = r.uniform(hmin, hmax)
        hwl = r.uniform(wmin, wmax)
        hwr = hwl * r.uniform(0.6, 1.6)
        dx = (x - cx + w / 2.0) % w - w / 2.0
        hw = np.where(dx < 0, hwl, hwr)
        f = np.clip(1 - np.abs(dx) / hw, 0, 1) ** sharp
        y = np.minimum(y, base - hh * f)
        tops.append((cx, base - hh))
    y = y - rough * (noise((1, w), seed + 3, 4, 0.5)[0] - 0.5) - rough * 0.5 * (noise((1, w), seed + 4, 1.2, 0.5)[0] - 0.5)
    return y, tops


def slope_field(crest, h, fall=60.0, lam_top=1.0, lam_bot=0.35, smooth=3.0):
    """For a range whose skyline is `crest`: each pixel's depth under the skyline; the 'height' terrace lines follow (seen
    from the valley floor they arch over each peak and spur, following the skyline near the top and flattening lower
    down); and the light on the slope (the left flanks of peaks and spurs lit, from the upper left)."""
    yy = np.arange(h)[:, None].astype(float)
    d = yy - crest[None, :]
    cs = ndi.gaussian_filter1d(crest, smooth, mode='wrap')
    dev = cs - cs.mean()
    lam = lam_bot + (lam_top - lam_bot) * np.exp(-np.clip(d, 0, None) / fall)
    E = yy - lam * dev[None, :]
    slope = np.gradient(ndi.gaussian_filter1d(crest, smooth * 2, mode='wrap'))
    lit = -slope[None, :] * np.exp(-np.clip(d, 0, None) / (fall * 1.5))
    return d, E, lit


def hash01(*a):
    """A repeatable 0..1 from integers (arrays welcome)."""
    v = np.int64(1469598103)
    for i, x in enumerate(a):
        v = (v ^ (np.asarray(x, dtype=np.int64) * np.int64([73856093, 19349663, 83492791, 2654435761][i % 4]))) % np.int64(2147483647)
        v = (v * np.int64(48271)) % np.int64(2147483647)
    return (v % 10007) / 10007.0


def house_far(T, x, base, hgt, wid, seed, white=0.97):
    """A stone tower house far off: a lit face and a shaded side, a white band at the top, a row of dark windows a floor."""
    r = rng(seed)
    top = base - hgt
    for y in range(top, base):
        for i in range(wid):
            T.px(x + i, y, 0.80 if i < wid - 1 or wid < 3 else 0.52)
    for i in range(wid):
        T.px(x + i, top, white)
    for fy in range(top + 2, base - 1, 3):
        for i in range(0, wid - 1, 2):
            if r.random() < 0.8:
                T.px(x + i, fy, 0.18)


def faceted(w, h, crest, tops, seed, main=3, extra=0.012, slope=(0.5, 1.1), drift=1.0, prom=(10, 18), length=(50, 110),
            branches=3, blen=(14, 40)):
    """A range's faces: spurs run down from each peak (and from shoulders along its skyline), branching as they go, each
    broadening and sinking into the slope below; the crest of each spur divides a face in the light from a face in shade.
    -> H, the lie of the face across the range (0 is the plain slope): its slope along x is the light on it (rising to
    the right: lit from the left), and terrace lines arch over its spurs."""
    r = rng(seed)
    ys = np.arange(h, dtype=float)[:, None]
    xs = np.arange(w, dtype=float)[None, :]
    H = np.zeros((h, w))

    def spur(x0, y0, sl, dr, ln, pr, depth):
        amp, ph, per = r.uniform(0.5, 3), r.uniform(0, 6.28), r.uniform(6, 14)
        u = np.clip((ys - y0) / ln, 0, 1)
        xr = x0 + dr * (ys - y0) + amp * np.sin((ys - y0) / per + ph)
        dx = (xs - xr + w / 2.0) % w - w / 2.0
        P = pr * (1 - u ** 2)
        s = sl / (1 + 2 * u)
        Hr = np.where((ys >= y0) & (u < 1), np.maximum(0, P - np.abs(dx) * s), 0)
        np.maximum(H, Hr, out=H)
        if depth < 1:
            for b in range(branches):
                v = r.uniform(0.15, 0.7)
                yb = y0 + v * ln
                xb = x0 + dr * (yb - y0) + amp * np.sin((yb - y0) / per + ph)
                spur(xb, yb, sl * r.uniform(1.0, 1.5), dr + r.choice([-1, 1]) * r.uniform(0.4, 1.1), r.uniform(*blen),
                     pr * (1 - v ** 2) * r.uniform(0.5, 0.9), depth + 1)

    for cx, ty in tops:
        for j in range(main):
            spur(cx + (r.uniform(-8, 8) if j else 0), ty + (r.uniform(3, 22) if j else 0), r.uniform(*slope) * (1.3 if j == 0 else 1.0),
                 r.uniform(-drift, drift), r.uniform(*length), r.uniform(*prom), 0)
    for i in range(int(w * extra)):
        x = r.uniform(0, w)
        spur(x, crest[int(x) % w] + r.uniform(1, 8), r.uniform(*slope) * 0.8, r.uniform(-drift, drift), r.uniform(*length) * 0.6,
             r.uniform(*prom) * 0.7, 0)
    return H


def face_light(H):
    """-> (light along x, -1..1; the creases where a shaded face meets the next lit one)."""
    Lx = np.clip(np.gradient(H, axis=1), -1.2, 1.2) / 1.2
    crease = (np.roll(Lx, 1, axis=1) < -0.15) & (Lx > 0.15)
    crease = crease | np.roll(crease, 1, axis=1)
    return Lx, crease


def far_i(w=2808, seed=9):
    """Two ranges round the valley. The farther, tall and blue in the haze, its faces lit and shaded about the ridges
    running down from its peaks, cloud sitting on its highest tops. The nearer, green under the haze, terraced to its tops
    (fine lines arching over each ridge), stone villages strung along its crests, and the valley's mist round its feet."""
    h, top0 = 158, 10                      # placed at y = 10: screen 10..168 (its foot is under the nearer hills)
    yy, xx = np.mgrid[0:h, 0:w]
    L = Layer(w, h)
    # the farther range
    c1, tops1 = crest_profile(w, seed, 100, 10, 34, 82, 70, 190, sharp=1.6, rough=2.0)
    m1 = yy >= c1[None, :]
    H1 = faceted(w, h, c1, tops1, seed + 1, main=3, extra=0.010, slope=(0.5, 1.0), drift=0.9, prom=(12, 22), length=(60, 120))
    Lx1, cr1 = face_light(ndi.gaussian_filter(H1, 0.8, mode='wrap'))
    d1 = yy - c1[None, :]
    t1 = 0.56 + 0.13 * Lx1 - 0.07 * cr1 + 0.07 * np.clip(d1 / 50.0, 0, 1) + 0.03 * (fbm((h, w), seed + 5, 10, 3, octaves=3) - 0.5)
    L.put(toned(np.clip(t1, 0, 1), HAZEB, dither=0.6), m1)
    # cloud on its highest tops: soft heaps over the summit, lit above, grey beneath, the peak showing past its edge
    hi = sorted(tops1, key=lambda t: t[1])[:4]
    caps = [(cx + 8, ty + 16, 100, 18, 70, 3.0, 8.0) for cx, ty in hi]
    Z = ndi.gaussian_filter(SL.puffs_wrap(h, w, caps, seed + 31), 0.9, mode='wrap')
    cov = np.clip(Z * 0.7, 0, 1)
    tc = 0.86 + 0.14 * np.clip(light(Z, -0.6, -0.8, 0.5), -1, 1)
    mc = cov > 0.35
    L.put(toned(np.clip(tc, 0.66, 1.0), HAZEB, dither=0.7), mc)
    # the nearer range
    c2, tops2 = crest_profile(w, seed + 17, 150, 19, 34, 78, 90, 210, sharp=1.3, rough=2.5)
    m2 = yy >= c2[None, :]
    H2 = faceted(w, h, c2, tops2, seed + 18, main=3, extra=0.016, slope=(0.5, 1.1), drift=1.0, prom=(10, 18), length=(40, 90))
    Lx2, cr2 = face_light(H2)
    d2 = yy - c2[None, :]
    E2 = yy - 0.45 * H2
    per = 3.0
    ph = E2 / per
    frac = ph - np.floor(ph)
    terr = np.where(frac < 0.34, -0.08, np.where(frac < 0.67, 0.035, 0.0))
    fields = fbm((h, w), seed + 21, 9, 3, octaves=3)
    t2 = 0.45 + 0.15 * Lx2 - 0.08 * cr2 + terr * np.clip(d2 / 3.0, 0, 1) + 0.07 * (fields - 0.5)
    trees = noise((h, w), seed + 22, 1.0, 1.0)
    t2 = np.where((trees > 0.82) & (d2 > 3), t2 - 0.12, t2)
    # the valley's mist: the range fades into it going down, deeper in some places than others
    mf = fbm((h, w), seed + 23, 70, 6, octaves=3)
    mist = np.clip((d2 - 34 - 18 * mf) / 30.0, 0, 1) ** 1.3
    t2 = t2 + mist * (0.86 - t2)
    L.put(toned(np.clip(t2, 0, 1), HAZEG, dither=0.6), m2)
    # villages along its crests: houses close together on the tops
    T = Tone(w, h)
    r = rng(seed + 40)
    for k, (cx, ty) in enumerate(sorted(tops2, key=lambda t: t[1])[:9]):
        n = int(r.integers(3, 8))
        x0 = int(cx) - n * 3
        for i in range(n):
            hx = (x0 + i * 5 + int(r.integers(-1, 2))) % w
            base = int(max(c2[hx % w], c2[(hx + 3) % w])) + 3
            house_far(T, hx, base, int(r.integers(4, 9)), int(r.integers(3, 5)), seed + 50 + k * 10 + i)
    L.put(toned(np.clip(T.t, 0, 1), HOUSEF, dither=0.3), T.m)
    return L, top0


TERR = ramp(['#0c1a0a', '#142812', '#1e3818', '#284a1e', '#345e24', '#40702a', '#4e8232', '#5e943a', '#72a646', '#88b656', '#a2c66c', '#c0d88a'], 24)   # crops on the terraces
FALLOW = ramp(['#1c140c', '#30241a', '#463626', '#5c4834', '#745c42', '#8c7252', '#a68a66', '#bea47e'], 16)       # ploughed and fallow


def tree_tone(T, cx, cy, rad, seed, dark=0.0):
    """A round crown lit from the upper left, with a few clumps of leaf showing in it."""
    r = rng(seed)
    R = int(np.ceil(rad)) + 1
    for j in range(-R, R + 1):
        for q in range(-R, R + 1):
            e = (q / rad) ** 2 + (j / (rad * 0.9)) ** 2
            if e <= 1.0 + 0.25 * (r.random() - 0.5):
                lt = 0.50 - 0.22 * (q + j) / (2 * rad) + 0.10 * ((q * 7 + j * 3 + seed) % 5 == 0) - 0.08 * e - dark
                T.px(int(cx + q), int(cy + j), lt)


def house_mid(T, x, base, wid, hgt, seed, floors=None):
    """A stone house on the hillside: the lit face, the side in shade, a white band at the parapet and over each row of
    windows, dark windows with a white arch over them."""
    r = rng(seed)
    top = base - hgt
    side = max(2, wid // 4)
    for y in range(top, base):
        for i in range(wid):
            t = 0.60 if i < wid - side else 0.36
            t += 0.05 * (((i * 5 + y * 3 + seed) % 7) == 0) - 0.04 * (((i * 3 + y * 7) % 11) == 0)
            T.px(x + i, y, t)
    for i in range(wid + 1):
        T.px(x + i - 0, top, 0.92 if i < wid - side else 0.70)
        T.px(x + i - 0, top + 1, 0.86 if i < wid - side else 0.62)
    fl = floors or max(1, (hgt - 4) // 6)
    for f in range(fl):
        wy = top + 4 + f * 6
        if wy + 3 >= base:
            break
        for i in range(1, wid - side - 1, 4):
            T.px(x + i, wy - 1, 0.94)
            T.px(x + i + 1, wy - 1, 0.94)
            T.px(x + i, wy, 0.10); T.px(x + i + 1, wy, 0.10)
            T.px(x + i, wy + 1, 0.10); T.px(x + i + 1, wy + 1, 0.10)
    dx = x + int((wid - side) * r.uniform(0.3, 0.6))
    for y in range(base - 4, base):
        T.px(dx, y, 0.08); T.px(dx + 1, y, 0.08)


def mid_i(w=1872, seed=17):
    """The valley's far side, nearer: a hillside terraced from the valley floor to its top in broad steps, each a strip of
    crop on a grey dry-stone wall, the terraces arching over its spurs, the fields each their own shade (a few ploughed),
    trees thick in the gullies, stone houses on the spurs; at its foot the valley floor, fields running away to it."""
    h, top0 = 88, 96                       # placed at y = 96: screen 96..184
    yy, xx = np.mgrid[0:h, 0:w]
    crest, tops = crest_profile(w, seed, 52, 9, 14, 44, 90, 200, sharp=1.25, rough=1.6)
    FLOOR = 58                             # the valley floor from here down (screen 154)
    m = (yy >= crest[None, :]) & (yy < FLOOR + 2)
    H = faceted(w, h, crest, tops, seed + 1, main=2, extra=0.012, slope=(0.35, 0.8), drift=1.3, prom=(8, 16), length=(30, 70), blen=(10, 26))
    Lx, cr = face_light(H)
    E = yy - 0.55 * H
    per = 6.0
    ph = E / per
    k = np.floor(ph).astype(np.int64)
    frac = ph - k
    # each terrace is cut into fields along its length, each field its own crop
    off = (hash01(k, 1) * 60).astype(np.int64)
    seglen = 20 + (hash01(k, 2) * 46).astype(np.int64)
    seg = (xx + off) // seglen
    crop = hash01(k, seg, 3)
    fallow = hash01(k, seg, 4) < 0.10
    wall = frac >= 0.70
    lip = (frac >= 0.56) & (frac < 0.70)
    rows = ((xx + (k % 2)) % 2 == 0) & (frac < 0.5) & (crop > 0.5)
    t = 0.54 + 0.12 * (crop - 0.5) + 0.13 * Lx - 0.06 * cr + 0.08 * lip - 0.05 * rows
    t = t + 0.04 * (noise((h, w), seed + 5, 3, 1.5) - 0.5)
    L = Layer(w, h)
    L.put(toned(np.clip(t, 0, 1), TERR, dither=0.5), m & ~wall & ~fallow)
    tf = 0.52 + 0.12 * (crop - 0.5) + 0.12 * Lx + 0.08 * lip - 0.08 * (((xx + yy) % 3) == 0)
    L.put(toned(np.clip(tf, 0, 1), FALLOW, dither=0.5), m & ~wall & fallow)
    # the walls under each terrace: grey stone, lit along the top, darker to the foot, the stones showing
    wt = 0.60 - 0.28 * (frac - 0.70) / 0.30 + 0.10 * Lx + 0.05 * ((((xx // 3) + k) % 2) == 0)
    wt = wt + 0.06 * (noise((h, w), seed + 6, 1.5, 0.8) - 0.5)
    L.put(toned(np.clip(wt, 0, 1), DRYST, dither=0.4), m & wall)
    # trees: thick in the creases between spurs, a few along the terraces
    r = rng(seed + 9)
    Tt = Tone(w, h)
    cys, cxs = np.nonzero(cr & m & (yy < FLOOR - 2))
    for i in r.choice(len(cxs), size=min(len(cxs), int(w / 6)), replace=False):
        if r.random() < 0.7:
            tree_tone(Tt, cxs[i], cys[i], r.uniform(2.0, 4.0), int(r.integers(0, 1000)))
    for i in range(int(w / 30)):
        cx = int(r.integers(0, w))
        cy = int(r.integers(int(crest[cx]) + 4, FLOOR))
        tree_tone(Tt, cx, cy, r.uniform(1.6, 3.0), int(r.integers(0, 1000)))
    sh = shadow_under(Tt.m, 2, 1) & ~Tt.m & L.a
    L.rgb[sh] = (L.rgb[sh] * 0.62).astype(np.uint8)
    L.paste(Tt.layer(LEAF, dither=0.5))
    # stone houses on the spurs: on the tops and a little way down
    Th = Tone(w, h)
    for j, (cx, ty) in enumerate(sorted(tops, key=lambda t: t[1])[:6]):
        for q in range(int(r.integers(1, 4))):
            hx = int(cx + r.integers(-24, 24)) % w
            hy = int(crest[hx]) + int(r.integers(4, 16))
            house_mid(Th, hx, hy, int(r.integers(9, 15)), int(r.integers(11, 19)), seed + 70 + j * 5 + q)
    L.paste(Th.layer(DRYST, dither=0.3))
    # the valley floor: rows of fields running away from the road, deeper the nearer they are, trees along some edges
    edges = [FLOOR - 1, FLOOR + 1, FLOOR + 3, FLOOR + 6, FLOOR + 9, FLOOR + 13, FLOOR + 18, FLOOR + 24, FLOOR + 31]
    Tf = Tone(w, h)
    Tb = Tone(w, h)
    for i in range(len(edges) - 1):
        y0, y1 = edges[i], min(h, edges[i + 1])
        if y0 >= h:
            break
        x = int(r.integers(0, 30))
        while x < w + 40:
            fw = int(r.integers(30, 70) * (1 + i * 0.35))
            c = r.random()
            for y in range(y0, y1):
                for q in range(x, x + fw):
                    if c < 0.12:
                        Tb.px(q % w, y, 0.50 + 0.08 * ((q + y) % 3 == 0) - 0.06 * (y == y1 - 1))
                    else:
                        Tf.px(q % w, y, 0.46 + 0.20 * c + 0.05 * ((q % 2) == 0) * (i > 3) + 0.07 * (y == y0) - 0.07 * (y == y1 - 1))
            x += fw
    L.paste(Tf.layer(TERR, dither=0.5))
    L.paste(Tb.layer(FALLOW, dither=0.5))
    Tt2 = Tone(w, h)
    for i in (1, 3, 5, 6):
        y0 = edges[i]
        q = int(r.integers(0, 20))
        while q < w:
            if hash01(q // 11, i, 5) < 0.6:
                tree_tone(Tt2, q, y0 - 1, 1.6 + 0.5 * i * hash01(q, i, 6), q + i * 77)
                q += int(2 + 2 * i * hash01(q, i, 7))
            else:
                q += int(r.integers(12, 40))
    L.paste(Tt2.layer(LEAF, dither=0.5))
    return SL._fold(L, lap=72, seed=seed), top0


# ------------------------------------------------------------------ looking at it
def compose(cam, S, w=SW, fore=True):
    out = Layer(w, SH)

    def wrap(Lr, par, y):
        x = int(cam * par) % Lr.w
        out.paste(Lr, -x, y)
        out.paste(Lr, Lr.w - x, y)

    wrap(S['sky'], 0.15, 0)
    wrap(S['far'], 0.3, S['far_y'])
    wrap(S['mid'], 0.55, S['mid_y'])
    if 'play' in S:
        out.paste(S['play'], -int(cam), 0)
    if fore and 'fore' in S:
        out.paste(S['fore'], -int(cam * 1.25), 0)
    return out


def preview(S, cams, path, w=SW, scale=2, lines=False):
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
    im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(path)
    return im.size


_CACHE = {}


def backgrounds():
    if 'bg' not in _CACHE:
        far, fy = far_i()
        mid, my = mid_i()
        _CACHE['bg'] = dict(sky=sky_i(), far=far, far_y=fy, mid=mid, mid_y=my)
    return dict(_CACHE['bg'])


if __name__ == '__main__':
    import sys
    S = backgrounds()
    print(preview(S, [0, 300, 900, 1500], sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/ibb/s3/bg.png'))
