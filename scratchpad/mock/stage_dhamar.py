# stage_dhamar.py - Dhamar, the Wadi (Mission 5), painted as the other missions are: tone fields through colour ramps,
# checker dither, light from the upper left, no outlines on scenery. Built 11 Nov in the development chat (Khaled, 03:25:
# zones 1-3 straight through as one test build). The high plain at 2,400 m: a cold, bright, clear sky; the volcanic
# cones the plateau is known for, dark and flat-topped, along the horizon; the Jahran plain's fields at harvest between
# dry-stone walls; Dhamar's stone tower houses with their white bands; the hot springs of Hammam Ali in their valley.
# Layers, back to front: the sky (wraps), the far ranges and cones (wrap), the plain (wraps), the play picture (one
# painting along the whole mission, cut into strips at export), and a foreground passing close to the lens. Where anyone
# can stand is recorded as it is painted (PLATS), with what else the level needs (INFO).
#   zone 1, Qa' Jahran (0 - 6200): the highway north across the plain, on wheels: dry asphalt, its verge, the fields and
#     walls behind it, poles and wires; three of the Committee's checkpoints (a stamp hut, sandbags, a pole with speakers;
#     the barrier and the queue are sprites: render_dhamar.js); two stone hamlets, a tea shack, eucalyptus; then the
#     outskirts: block houses and shops, and Dhamar's old gate, where Salem stops.
#   zone 2, Dhamar (6200 - 8600): through the gate into the old town: the souq's stalls, tower houses, an alley up to a
#     roof; the recruiting office (the school: three classrooms padlocked along its yard, a walkway and its stair, the
#     office at the end with the stamp window and his poster over it); the university's gate; the street out west.
#   zone 3, Hammam Ali (8600 - 10600): the road down into the springs' valley: a farm wall, the village's houses, the hot
#     pools in their stone basins (the steam is the game's), the old bathhouse with its domes, the car park where the
#     convoy waits, and the ground beside it where he holds his vote.
import numpy as np
from paint import *
import stage_mocha as SM
import stage_taiz as STZ
import stage_ibb as I
import stage_ibb_z1 as Z1
import stage_ibb_z2 as Z2
import stage_ibb_z4 as Z4

SH, WALK = I.SH, I.WALK                  # 216; where feet land (184)
ROAD_TOP = Z1.ROAD_TOP                   # the asphalt from here down (172)
VERGE = Z1.VERGE                         # the verge behind the road (160)
BASE = 170                               # in town: where the houses' fronts stand, behind the street
Z2X, Z3X, END = 6200, 8600, 10600        # where the city and the springs start; where the test's picture ends
GATE_X = 6290                            # the old gate (260 wide)
put_tone = SM.put_tone
PLATS = {}
INFO = {}


def plat(pid, pts):
    PLATS[pid] = [[int(x), int(y)] for x, y in pts]


# ------------------------------------------------------------------ colour ramps (dark to pale)
SKYD = ramp(['#1c3a66', '#24467a', '#2e548c', '#3a649c', '#4a74aa', '#5c86b6', '#7298c2', '#8aaccc', '#a4c0d6', '#bed2e0',
             '#d6e2e8', '#eaf0f0'], 22)                                                         # high, cold, clear
HAZEF = ramp(['#3a4e66', '#465a72', '#54687e', '#64768a', '#768696', '#8a98a4', '#a0acb4', '#b8c2c6', '#d0d6d6'], 18)   # far ranges
CONES = ramp(['#141214', '#201c1e', '#2e2828', '#3e3634', '#504642', '#645852', '#7a6c64', '#928478'], 14)           # basalt cones
GOLDF = Z4.GOLDF                                                                                      # barley at harvest
FALLOW = I.FALLOW
GREENF = ramp(['#16200c', '#243212', '#34461a', '#465a22', '#5a6e2c', '#728438', '#8c9a48', '#a6b05c'], 14)          # lucerne, qat-free
WALLD = ramp(['#1a1714', '#2c2824', '#403a34', '#564e46', '#6c6358', '#82786c', '#9a8f82', '#b2a898'], 14)         # dry-stone walls, dark
DRYROAD = ramp(['#1a1918', '#2a2826', '#3a3734', '#4c4844', '#5e5954', '#726c66', '#88817a', '#9e968e', '#b4ad a4'.replace(' ', ''),
                '#c8c2b8'], 18)                                                                   # dry asphalt, dusty
DUST = ramp(['#2a2218', '#40362a', '#584c3c', '#706250', '#887a66', '#a0927c', '#b8aa92', '#ccc0a8'], 14)           # the verge's dust
BASALT = STZ.BASALT
TSTONE = STZ.TSTONE
LIME = SM.LIME
CONCRETE = Z1.CONCRETE
WATERD = ramp(['#14262a', '#1e363a', '#2a4a4c', '#3a6060', '#4e7876', '#68928e', '#88aca6', '#acc8c0', '#d0e2da'], 16)   # the pools, mineral green
SINTER = ramp(['#2a2416', '#463c26', '#625638', '#7e704c', '#9a8a62', '#b4a47c', '#ccbe98', '#e2d6b6'], 14)           # the springs' stone, crusted
DOME = ramp(['#3a3630', '#545048', '#6e6a60', '#888478', '#a29e92', '#bab6aa', '#d0ccc0', '#e4e0d6'], 14)            # the bathhouse's plaster
OCHREW = ramp(['#2a1e10', '#46341c', '#62482a', '#7e5e3a', '#98764c', '#b08e62', '#c6a67c', '#dabe98'], 14)            # the office's ochre wash
IRONG = Z2.IRONG
REDP = I.REDP


def wrapn(shape, seed, sx, sy, octaves=3):
    return fbm(shape, seed, sx, sy, octaves=octaves)


# ------------------------------------------------------------------ the sky
def sky_d(w=1404, seed=7):
    """The plateau's sky at 2,400 m: a deep clear blue overhead going pale toward the plain, a few long streaks of high
    cloud, nothing else."""
    h = 124
    yy = np.arange(h)[:, None] / float(h) + np.zeros((1, w))
    tone = 0.12 + 0.86 * np.clip(yy, 0, 1) ** 1.7
    streak = wrapn((h, w), seed, 90, 1.6)
    band = np.exp(-((yy - 0.30) / 0.10) ** 2) + 0.6 * np.exp(-((yy - 0.52) / 0.07) ** 2)
    tone += np.clip(streak - 0.58, 0, 1) * 1.1 * band
    L = Layer(w, h)
    L.put(toned(np.clip(tone, 0, 1), SKYD, dither=0.7), np.ones((h, w), bool))
    return L


# ------------------------------------------------------------------ the far ranges and the volcanic cones
def far_d(w=2808, seed=17):
    """The plain's far edge: low blue ranges in the haze, and along the horizon the cones, dark, round-shouldered and
    flat on top (their craters), lit from the left. -> (picture, its y on the screen)."""
    h = 70
    L = Layer(w, h)
    yy = np.arange(h)[:, None] * np.ones((1, w))
    xs = np.arange(w)
    HZ = 58                                                       # the horizon in this picture
    ridge, _ = I.crest_profile(w, seed, HZ - 4, 9, 6, 20, 60, 160, sharp=1.2, rough=1.5)
    m = yy >= ridge[None, :]
    t = 0.50 + 0.06 * (noise((h, w), seed + 1, 10, 3) - 0.5) + 0.10 * ((yy - ridge[None, :]) < 1) + 0.10 * np.clip((yy - HZ + 10) / 10.0, 0, 1)
    L.put(toned(np.clip(t, 0, 1), HAZEF, dither=0.5), m)
    r = rng(seed + 2)
    T = Tone(w, h)
    n = 11
    for k in range(n):
        cx = (k + r.uniform(0.2, 0.8)) * w / float(n)
        hw, ch = r.uniform(26, 62), r.uniform(14, 30)
        topw = hw * r.uniform(0.22, 0.34)
        for x in range(int(cx - hw), int(cx + hw) + 1):
            xm = x % w
            d = abs(x - cx)
            u = 0 if d < topw else (d - topw) / (hw - topw)
            yt = HZ - ch * (0.5 + 0.5 * np.cos(np.pi * min(1.0, u)))
            for y in range(int(yt), HZ + 1):
                T.px(xm, y, 0.46 + 0.16 * (x < cx) * (1 - u) - 0.14 * (x > cx) + 0.14 * (y - yt < 1) - 0.08 * ((y - yt) / max(1.0, ch)))
            if d < topw - 1:
                T.px(xm, int(yt) + 1, 0.20)
    put_tone(L, T, CONES, dither=0.4)
    # the plain's far edge under them, a pale band
    t2 = 0.62 + 0.06 * (noise((h, w), seed + 3, 30, 2) - 0.5)
    L.put(toned(np.clip(t2, 0, 1), HAZEF, dither=0.4), yy >= HZ + 1)
    # haze over the farthest of it
    hz = np.clip((yy - 20) / 40.0, 0, 1) * 0.30
    sub = L.rgb.astype(float)
    L.rgb[:] = np.clip(sub * (1 - hz[..., None]) + np.array([200, 212, 220]) * hz[..., None], 0, 255).astype(np.uint8)
    return L, 62


# ------------------------------------------------------------------ the plain: fields, walls, hamlets
def mid_d(w=1800, seed=27):
    """The Jahran plain nearer to: a patchwork of fields at harvest (gold barley, brown fallow, green lucerne) between dark
    dry-stone walls, rows getting deeper toward the road; now and then a hamlet of stone houses with white bands, a few
    trees. Wraps. -> (picture, its y)."""
    h = 54
    L = Layer(w, h)
    r = rng(seed)
    F, G, Gr, Wl = Tone(w, h), Tone(w, h), Tone(w, h), Tone(w, h)
    y, row = 0, 0
    while y < h:
        rh = 2 + int(row * 1.4)
        x = 0
        while x < w:
            fw = int(r.integers(30, 90)) + row * 10
            fw = min(fw, w - x)
            kind = r.random()
            tgt = F if kind < 0.45 else (G if kind < 0.75 else Gr)
            base = r.uniform(0.42, 0.70)
            for xx in range(x, x + fw):
                for yv in range(y, min(h, y + rh)):
                    stripe = ((xx + yv * 2) % 4 == 0) * (tgt is F) * 0.05
                    tgt.px(xx, yv, base + stripe + 0.03 * (((xx // 3 + yv) % 5) == 0))
                Wl.px(xx, y, 0.40 + 0.18 * ((xx % 3) == 0))
            for yv in range(y, min(h, y + rh)):
                Wl.px(x, yv, 0.36)
            x += fw
        y += rh + 1
        row += 1
    put_tone(L, F, GOLDF, dither=0.4)
    put_tone(L, G, FALLOW, dither=0.4)
    put_tone(L, Gr, GREENF, dither=0.4)
    put_tone(L, Wl, WALLD, dither=0.3)
    # hamlets: stone houses, small, white bands, dark windows
    Hs, Hw = Tone(w, h), Tone(w, h)
    for k in range(5):
        hx = int((k + r.uniform(0.1, 0.7)) * w / 5.0)
        for j in range(int(r.integers(3, 7))):
            bw, bh = int(r.integers(6, 13)), int(r.integers(8, 18))
            bx = hx + int(r.integers(-20, 30))
            by = 8 + int(r.integers(0, 6))
            for xx in range(bx, bx + bw):
                for yv in range(by - bh, by + 1):
                    xm = xx % w
                    if 0 <= yv < h:
                        Hs.px(xm, yv, 0.42 + 0.14 * (xx < bx + 2) - 0.10 * (xx >= bx + bw - 2) + 0.03 * ((xx + yv) % 2))
                if (xx - bx) % 4 == 1 and bh > 10:
                    Hs.px(xx % w, by - bh + 4, 0.12)
            for xx in range(bx, bx + bw):
                if 0 <= by - bh + 2 < h:
                    Hw.px(xx % w, by - bh + 2, 0.86)
    put_tone(L, Hs, BASALT, dither=0.3)
    put_tone(L, Hw, LIME, dither=0)
    return L, 118


def backgrounds():
    far, fy = far_d()
    mid, my = mid_d()
    return dict(sky=sky_d(), far=far, far_y=fy, mid=mid, mid_y=my)


# ------------------------------------------------------------------ the ground along the whole road
class swap:
    """Paint with another module's ramps for a while (the Ibb painters with Dhamar's dry colours)."""

    def __init__(self, mod, **kw):
        self.mod, self.kw, self.old = mod, kw, {}

    def __enter__(self):
        for k, v in self.kw.items():
            self.old[k] = getattr(self.mod, k)
            setattr(self.mod, k, v)

    def __exit__(self, *a):
        for k, v in self.old.items():
            setattr(self.mod, k, v)


def fields_back(L, x0, x1, seed=1):
    """Behind the verge on the plain: barley standing gold behind a dry-stone wall, a lane of fallow, the wall's top
    uneven."""
    with swap(Z1, TERR=GOLDF, GRASS=GOLDF):
        Z1.crops(L, x0, x1, VERGE - 14, seed=seed, hmin=8, hmax=16, gap=2.6, heads=0.75)
    with swap(Z1, DRYST=WALLD, GRASS=GOLDF):
        Z1.drystone(L, x0, x1, VERGE - 10, VERGE + 1, seed=seed + 1, grass=True)


def ground(L, seed=901):
    """The highway's dry asphalt and its dusty verge to the gate; the old town's paving from the gate to the springs'
    valley; a dirt road with gravel down to the car park."""
    with swap(Z1, ROADW=DRYROAD, GRAVEL=DUST, MUDI=DUST):
        Z1.verge(L, 0, Z2X + 120, seed=seed)
        Z1.road(L, 0, Z2X + 140, seed=seed + 1)
    fields_back(L, 0, Z2X - 760, seed=seed + 2)
    # the town's paving: from just short of the gate to the springs' valley
    P = STZ.paving_strip(Z3X + 260 - (Z2X + 100), SH - BASE, seed=seed + 3)
    L.paste(P, Z2X + 100, BASE)
    # the dirt road into the valley, then the car park's gravel
    w, h = END - (Z3X + 260), SH - BASE
    yy, xx = np.mgrid[0:h, 0:w]
    t = 0.50 + 0.10 * (noise((h, w), seed + 4, 1.0, 1.0) - 0.5) + 0.08 * (noise((h, w), seed + 5, 40, 2) - 0.5) - 0.08 * (yy < 2)
    ruts = (np.abs(yy - 22) < 1) | (np.abs(yy - 34) < 1)
    t = np.where(ruts, t - 0.08, t)
    Z1.piece_put(L, t, np.ones((h, w), bool), DUST, Z3X + 260, BASE, dither=0.45)


# ------------------------------------------------------------------ zone 1: the checkpoints and the plain
def stamp_hut(L, x, seed=1):
    """The checkpoint's stamp window: a little box of rendered block on the verge, a hatch with a counter and a stamp pad
    on it, a plastic chair inside in the dark, the paint gone at the corners. -> its counter."""
    T = Tone(L.w, L.h)
    x0, x1, top = x, x + 34, VERGE - 32
    for yy in range(top, VERGE + 2):
        for xx in range(x0, x1):
            u = (xx - x0) / float(x1 - x0)
            T.px(xx, yy, 0.66 - 0.18 * (u > 0.72) + 0.04 * (((xx * 7 + yy * 3) % 11) == 0) - 0.08 * (yy > VERGE - 3))
    for xx in range(x0 - 2, x1 + 2):
        T.px(xx, top - 1, 0.82); T.px(xx, top - 2, 0.50)
    put_tone(L, T, CONCRETE, dither=0.3)
    H = Tone(L.w, L.h)
    for yy in range(top + 8, top + 20):
        for xx in range(x0 + 6, x0 + 24):
            H.px(xx, yy, 0.08 + 0.05 * (yy > top + 15))
    put_tone(L, H, STZ.SOOT, dither=0)
    C = Tone(L.w, L.h)
    for xx in range(x0 + 4, x0 + 26):
        C.px(xx, top + 20, 0.70); C.px(xx, top + 21, 0.42)
    C.rect(x0 + 16, top + 18, x0 + 19, top + 19, 0.30)                  # the stamp pad
    put_tone(L, C, STZ.TEAK, dither=0)
    return dict(x=x0 + 15, y=top + 20)


def sandbags(L, x0, x1, base, rows=2, seed=1):
    """A low wall of sandbags, each lit on its top, dark in the joins."""
    T = Tone(L.w, L.h)
    r = rng(seed)
    for k in range(rows):
        y1 = base - k * 6
        off = 5 * (k % 2)
        x = x0 - off
        while x < x1:
            bw = 10 + int(r.integers(0, 3))
            for xx in range(max(x0, x), min(x1, x + bw)):
                for yy in range(y1 - 6, y1):
                    u = (yy - (y1 - 6)) / 6.0
                    T.px(xx, yy, 0.62 - 0.30 * u ** 1.5 + 0.12 * (yy == y1 - 6) - 0.14 * (xx == x or xx == x + bw - 1))
            x += bw
    put_tone(L, T, DUST, dither=0.3)
    return base - rows * 6


def checkpoint(L, x, seed=11):
    """One of the Committee's checkpoints, the part on the verge: the stamp hut, sandbags in front of it, a pole with
    speakers on it turned down the road (his laugh comes out of these), drums, a tyre. The barrier across the road, the
    men and the queue are the game's (render_dhamar.js). -> what the level needs."""
    hut = stamp_hut(L, x + 30, seed=seed)
    top = sandbags(L, x + 2, x + 30, VERGE + 2, rows=2, seed=seed + 1)
    Z1.drum(L, x + 70, VERGE + 3, seed=seed + 2)
    Z1.drum(L, x + 82, VERGE + 4, seed=seed + 3, rmp=Z1.BLUEP)
    Z1.tyre(L, x + 100, VERGE + 4, seed=seed + 4)
    tie = Z1.pole(L, x + 120, VERGE + 2, hgt=104, seed=seed + 5, horns=2)
    return dict(x=x, hut=hut, bags=[x + 2, x + 30, top], pole=x + 120, tie=tie)


def hamlet(L, x, seed=21, n=3):
    """A hamlet on the plain behind the fields: stone houses, small and squat, with white bands and a lime-washed top."""
    r = rng(seed)
    for k in range(n):
        w, h = int(r.integers(44, 70)), int(r.integers(46, 72))
        style = ['stone', 'mixed', 'stone'][k % 3]
        pic, info = STZ.taiz_house(w, h, seed=seed + k, style=style)
        L.paste(pic, x + k * int(w * 0.8) - 6, VERGE - 12 - pic.h)


def tea_shack(L, x, seed=31):
    """A tea shack by the road: block walls, a tin roof, a counter under a tin awning, a kettle on a gas ring."""
    T = Tone(L.w, L.h)
    x0, x1, top = x, x + 60, VERGE - 34
    for yy in range(top, VERGE + 2):
        for xx in range(x0, x1):
            T.px(xx, yy, 0.56 + 0.10 * (((xx // 8) + (yy // 4)) % 2) * 0.3 - 0.12 * (xx > x1 - 14))
    put_tone(L, T, CONCRETE, dither=0.3)
    R = Tone(L.w, L.h)
    for xx in range(x0 - 4, x1 + 16):
        for k in range(4):
            R.px(xx, top - 4 + k + (xx - x0) // 30, 0.46 + 0.20 * ((xx % 4) == 0) - 0.08 * k)
    put_tone(L, R, I.TIN, dither=0.3)
    H = Tone(L.w, L.h)
    H.rect(x0 + 10, top + 10, x0 + 34, VERGE - 8, 0.08)
    put_tone(L, H, STZ.SOOT, dither=0)


def plain(L, seed=101):
    """Zone 1's dressing along the highway: the checkpoints, poles and wires all the way, hamlets behind the fields,
    a tea shack, eucalyptus, a lorry's tyre; then the outskirts (shops, block houses, a petrol pump) up to the gate."""
    r = rng(seed)
    cps = []
    for k, cx in enumerate((1380, 3080, 4780)):
        cps.append(checkpoint(L, cx, seed=seed + 10 * k))
    INFO['checkpoints'] = cps
    for k, hx in enumerate((620, 2280, 3880, 5260)):
        hamlet(L, hx, seed=seed + 40 + k, n=2 + (k % 2))
    tea_shack(L, 2640, seed=seed + 60)
    for k, ex in enumerate((940, 1960, 2530, 3560, 4320, 5020)):
        with swap(Z1, EUCA=Z1.EUCA):
            Z1.eucalyptus(L, ex, VERGE - 2, hgt=int(r.integers(86, 120)), seed=seed + 70 + k)
    # poles and wires the whole way (the checkpoints' own poles carry speakers)
    ties = []
    x = 200
    while x < Z2X - 300:
        near = [c for c in cps if abs(c['pole'] - x) < 150]
        if near:
            ties.append(near[0]['tie'])
            x = near[0]['pole'] + 300
            continue
        ties.append(Z1.pole(L, x, VERGE + 2, hgt=108, seed=seed + x, horns=0))
        x += 300
    ties.sort(key=lambda t: t[0][0] if isinstance(t[0], (list, tuple)) else t[0])
    for a, b in zip(ties[:-1], ties[1:]):
        try:
            Z1.wires(L, a, b, sag=9)
        except Exception:
            pass
    # the outskirts: shops and block houses, the plain giving way to the town
    with swap(Z1, GRAVEL=DUST):
        Z1.shop(L, 5460, seed=seed + 90)
    for k, (hx, w, h) in enumerate(((5620, 70, 60), (5700, 84, 88), (5800, 66, 54), (5880, 92, 110), (5990, 74, 70))):
        pic, info = STZ.taiz_house(w, h, seed=seed + 100 + k, style=['mixed', 'lime', 'stone', 'mixed', 'lime'][k])
        L.paste(pic, hx, VERGE + 2 - pic.h)


# ------------------------------------------------------------------ zone 2: Dhamar
def gate(L, seed=201):
    """Dhamar's old gate: two towers, the pointed arch over the passage, the wall running away either side."""
    pic, info = STZ.city_gate(seed=seed)
    L.paste(pic, GATE_X, BASE + 2 - pic.h)
    INFO['gate'] = dict(x0=GATE_X, x1=GATE_X + pic.w)


def low_stall(w=70, seed=1, cloth=None):
    """Dhamar's market stall: Taiz's, its awning lower (48 over the street, not 66), so that its top is a jump up (134, in
    reach: a jump takes Yazeed about 65 up from the street)."""
    Hh = 52
    pic = STZ.piece(w + 8, Hh)
    cloth = cloth if cloth is not None else [STZ.CLOTH_R, STZ.CLOTH_Y, STZ.CLOTH_G, STZ.CLOTH_B][seed % 4]
    STZ.SZ.stall_counter(pic, 6, w - 2, Hh - 22, seed=seed)
    STZ.SZ.awning(pic, 2, w + 4, Hh - 48, depth=10, rmp=cloth, stripes=8, seed=seed, sag=2)
    return pic, dict(w=w + 8, h=Hh, top=Hh - 48)


def stall(L, x, seed=1, cloth=None):
    """A souq stall under its awning, standing in the street; the awning's top is somewhere to stand."""
    pic, info = low_stall(70, seed=seed, cloth=cloth)
    y0 = WALK - 6 - pic.h + 4
    L.paste(pic, x, y0)
    top = y0 + info['top']
    plat('stall%d' % seed, [[x + 4, top], [x + info['w'] - 4, top]])
    return top


def tower(L, x, w, h, seed, style='mixed', pid=None):
    """A tower house of Dhamar: basalt below, plaster and white bands above. Its roof is too high to stand on unless a
    stair or a neighbour leads up (pid names the roof when one does)."""
    pic, info = STZ.taiz_house(w, h, seed=seed, style=style)
    y0 = BASE + 2 - pic.h
    L.paste(pic, x, y0)
    if pid:
        plat(pid, [[x + 3, y0 + info['top']], [x + w - 3, y0 + info['top']]])
    return dict(x0=x, x1=x + w, roof=y0 + info['top'], doors=[dict(x=x + d['x'] + d['w'] // 2, y=BASE) for d in info['doors']])


def low_house(L, x, w, seed, roof_y=122, pid=None, door=True):
    """A one-storey house of dark stone, its parapet lime-washed: a roof to jump up onto."""
    T = Tone(L.w, L.h)
    pic = Layer(w, BASE - roof_y + 4)
    STZ.ashlar(pic, 0, 4, w, pic.h, BASALT, seed=seed, course=6, block=(9, 20), base=0.50)
    STZ.plaster(pic, 0, 0, w, 5, rmp=LIME, seed=seed + 1, base=0.86, stain=0.3)
    if door:
        STZ.arched_door(pic, w // 2 - 7, pic.h, w=14, h=24, paint=STZ.BLUEWOOD, seed=seed + 2)
    L.paste(pic, x, roof_y - 2)
    if pid:
        plat(pid, [[x + 2, roof_y - 2], [x + w - 2, roof_y - 2]])
    return dict(x0=x, x1=x + w, door=x + w // 2, roof=roof_y - 2)


def stair_up(L, x0, steps, rise=14, run=13, seed=1, pid='alley'):
    """Stone steps up against a house's side, each a place to stand (left to right, climbing)."""
    T = Tone(L.w, L.h)
    tops = []
    for k in range(steps):
        sx0, sx1 = x0 + k * (run - 1), x0 + k * (run - 1) + run + 2
        top = WALK - 13 - k * rise
        for yy in range(top, BASE + 2):
            for xx in range(sx0, sx1):
                T.px(xx, yy, 0.60 + 0.20 * (yy == top) - 0.12 * (xx > sx1 - 3) + 0.03 * (((xx + yy) % 5) == 0))
        plat('%s%d' % (pid, k + 1), [[sx0 + 1, top], [sx0 + run + 1, top]])
        tops.append(top)
    put_tone(L, T, TSTONE, dither=0.3)
    return tops


SCHOOL_X = 7300                       # the recruiting office (the school): its yard's left end
DOOR_DX = (120, 220, 320)             # its three classrooms' doors, from SCHOOL_X
DOOR_TOP, DOOR_BASE = 140, 170        # the painted doors (render_dhamar.js draws them open)
OFFICE_DX = 400                       # the office, at the yard's right end (the stamp window, his poster)


def recruiting_office(L, seed=241):
    """The school, taken over as the Committee's recruiting office: a long two-storey block washed ochre, the ground
    floor's three classroom doors along the yard (padlocked: the game draws the bar and lock), the upper floor's
    walkway in front of its windows with an iron rail, a stair up at the left end, the roof above; at the right end the
    office, its stamp window under an awning and the square his painted face is pasted in (the game's), the cash drawer
    under the counter."""
    x0, x1 = SCHOOL_X + 40, SCHOOL_X + 520
    top, mid = 76, 124                           # the roof's parapet; the walkway's floor
    pic = Layer(x1 - x0, BASE + 2 - top)
    STZ.plaster(pic, 0, 0, pic.w, pic.h, rmp=OCHREW, seed=seed, base=0.62, stain=0.8)
    STZ.white_band(pic, 0, pic.w, mid - top - 6, h=4, kind=1, seed=seed + 1)
    STZ.white_band(pic, 0, pic.w, 2, h=4, kind=0, seed=seed + 2)
    # the upper windows behind the walkway
    for k in range(9):
        STZ.qamariya_window(pic, 18 + k * 52, 22, w=10, h=14, paint=STZ.GREENWOOD, seed=seed + 10 + k)
    # the doors along the yard (dark wood, shut: the game draws them open, and the bar and padlock on them)
    D = Tone(pic.w, pic.h)
    for k, dx in enumerate(DOOR_DX):
        cx = SCHOOL_X + dx - x0
        for yy in range(DOOR_TOP - top, DOOR_BASE - top):
            for xx in range(cx - 8, cx + 8):
                D.px(xx, yy, 0.34 + 0.08 * ((xx - cx) % 4 == 0) - 0.10 * (xx == cx + 7))
        for xx in range(cx - 10, cx + 10):
            D.px(xx, DOOR_TOP - top - 1, 0.62); D.px(xx, DOOR_TOP - top - 2, 0.70)
    put_tone(pic, D, IRONG, dither=0)
    # the office at the right end: the stamp window, its awning, the counter; the empty square for his face
    ox = OFFICE_DX + 40 - 40
    H = Tone(pic.w, pic.h)
    H.rect(ox + 6, 152 - top, ox + 34, 166 - top, 0.06)
    put_tone(pic, H, STZ.SOOT, dither=0)
    C = Tone(pic.w, pic.h)
    for xx in range(ox + 2, ox + 38):
        C.px(xx, 166 - top, 0.72); C.px(xx, 167 - top, 0.40)
    C.rect(ox + 14, 168 - top, ox + 26, 172 - top, 0.30)                 # the cash drawer, locked
    C.px(ox + 20, 170 - top, 0.85)
    put_tone(pic, C, STZ.TEAK, dither=0)
    L.paste(pic, x0, top)
    INFO['office'] = dict(window=SCHOOL_X + OFFICE_DX + 20, poster=[SCHOOL_X + OFFICE_DX + 4, 128], screen=[SCHOOL_X + OFFICE_DX - 40, 146])
    # the walkway: a floor of planks on brackets with an iron rail, along the whole front
    W_ = Tone(L.w, L.h)
    for xx in range(x0, x1):
        W_.px(xx, mid, 0.70); W_.px(xx, mid + 1, 0.48); W_.px(xx, mid + 2, 0.30)
        if (xx - x0) % 26 == 0:
            for yy in range(mid + 3, mid + 9):
                W_.px(xx, yy, 0.30 + 0.02 * (yy - mid))
    put_tone(L, W_, STZ.TEAK, dither=0)
    R = Tone(L.w, L.h)
    for xx in range(x0, x1):
        R.px(xx, mid - 10, 0.56)
        if (xx - x0) % 6 == 0:
            for yy in range(mid - 9, mid):
                R.px(xx, yy, 0.40)
    put_tone(L, R, IRONG, dither=0)
    plat('walkway', [[x0 + 2, mid], [x1 - 2, mid]])
    plat('officeroof', [[x0 + 4, top], [x1 - 4, top]])
    # the stair up to the walkway at the left end
    stair_up(L, SCHOOL_X - 4, 4, rise=15, run=12, seed=seed + 30, pid='schoolstep')
    INFO['school'] = dict(x0=x0, x1=x1, doors=[SCHOOL_X + d for d in DOOR_DX], top=DOOR_TOP, base=DOOR_BASE)


def university_gate(L, x, seed=261):
    """The university's gate as scenery: two square pillars of dressed stone, a lintel across, iron gates folded back."""
    T = Layer(150, BASE + 2 - 70)
    for px0 in (0, 120):
        STZ.ashlar(T, px0, 10, px0 + 30, T.h, TSTONE, seed=seed + px0, course=7, block=(10, 18), base=0.60)
    STZ.ashlar(T, 0, 0, 150, 14, TSTONE, seed=seed + 5, course=7, block=(14, 26), base=0.66)
    STZ.white_band(T, 0, 150, 14, h=3, kind=2, seed=seed + 6)
    L.paste(T, x, 70)
    G = Tone(L.w, L.h)
    for xx in range(x + 32, x + 44):
        for yy in range(100, BASE):
            if (xx - x) % 3 == 0 or yy % 10 == 0:
                G.px(xx, yy, 0.30)
    for xx in range(x + 106, x + 118):
        for yy in range(100, BASE):
            if (xx - x) % 3 == 0 or yy % 10 == 0:
                G.px(xx, yy, 0.30)
    put_tone(L, G, STZ.IRON, dither=0)
    plat('unilintel', [[x + 2, 70], [x + 148, 70]])


def city(L, seed=201):
    """Zone 2, the old town of Dhamar, from the gate to the street out west."""
    gate(L, seed)
    # the souq: tower houses behind, stalls standing out in the street, an alley up to a roof
    t1 = tower(L, 6570, 96, 132, seed + 1, 'mixed')
    stall(L, 6600, seed=31, cloth=None)
    t2 = tower(L, 6672, 84, 110, seed + 2, 'stone')
    h1 = low_house(L, 6760, 92, seed + 3, roof_y=124, pid='souqroof1')
    stall(L, 6866, seed=32)
    t3 = tower(L, 6948, 100, 140, seed + 4, 'lime')
    stall(L, 7060, seed=33)
    tops = stair_up(L, 7136, 4, rise=14, run=13, seed=seed + 5, pid='alley')
    h2 = low_house(L, 7186, 96, seed + 6, roof_y=88, pid='alleyroof', door=True)
    INFO['souq'] = dict(doors=[t1['doors'][0]['x'], t2['doors'][0]['x'], h1['door'], t3['doors'][0]['x']])
    recruiting_office(L, seed + 40)
    # past the office: houses, the university's gate, the street on out of town
    h3 = low_house(L, 7880, 84, seed + 60, roof_y=122, pid='lowroof3')
    t4 = tower(L, 7968, 92, 126, seed + 61, 'mixed')
    university_gate(L, 8090, seed + 62)
    h4 = low_house(L, 8270, 90, seed + 63, roof_y=124, pid='lowroof4')
    t5 = tower(L, 8364, 96, 120, seed + 64, 'stone')
    with swap(Z1, DRYST=WALLD, GRASS=GOLDF):
        Z1.drystone(L, 8470, Z3X + 160, 150, BASE + 1, seed=seed + 65)
    INFO['town'] = dict(doors=[h3['door'], t4['doors'][0]['x'], h4['door'], t5['doors'][0]['x']])


# ------------------------------------------------------------------ zone 3: Hammam Ali
def pool(L, x0, x1, seed=1):
    """A hot pool in its basin of crusted stone, sunk in front of the path (nearer the lens than where anyone walks): a
    lip of stone along the path's edge, the water mineral green, darker under the far rim, a pale line where it takes the
    sky; the game puts the steam on it."""
    T = Tone(L.w, L.h)
    W_ = Tone(L.w, L.h)
    lip = WALK + 2
    for xx in range(x0, x1):
        for yy in range(lip, lip + 3):
            T.px(xx, yy, 0.74 - 0.12 * (yy - lip) + 0.04 * ((xx % 7) == 0))
        T.px(xx, SH - 1, 0.40)
    for yy in range(lip, SH):
        for xx in (x0, x0 + 1, x1 - 2, x1 - 1):
            T.px(xx, yy, 0.50 - 0.12 * (xx > x0 + 1))
    for xx in range(x0 + 2, x1 - 2):
        for yy in range(lip + 3, SH - 1):
            u = (yy - lip - 3) / float(SH - lip - 4)
            W_.px(xx, yy, 0.36 + 0.26 * u + 0.18 * (yy == lip + 3) + 0.10 * (((xx + 3 * yy) % 23) == 0) + 0.05 * (noise_at(xx, yy, seed) - 0.5))
    put_tone(L, T, SINTER, dither=0.3)
    put_tone(L, W_, WATERD, dither=0.4)
    return dict(x0=x0, x1=x1, y=lip)


def noise_at(x, y, seed):
    t = (x * 374761393 + y * 668265263 + seed * 1442695041) & 0xffffffff
    t = ((t ^ (t >> 13)) * 1274126177) & 0xffffffff
    return ((t ^ (t >> 16)) & 0xffff) / 65535.0


def bathhouse(L, x, seed=301):
    """The old bathhouse: a long building of dressed stone with a row of arched windows and three low domes on its roof,
    lime-washed; the roof's flat between the domes is somewhere to stand."""
    w, h = 300, 78
    pic = Layer(w, h + 30)
    STZ.ashlar(pic, 0, 30, w, pic.h, SINTER, seed=seed, course=7, block=(12, 24), base=0.56)
    STZ.white_band(pic, 0, w, 30, h=4, kind=1, seed=seed + 1)
    D = Tone(w, pic.h)
    for k, dcx in enumerate((60, 150, 240)):
        r_ = 26 if k == 1 else 20
        for yy in range(30 - r_, 31):
            for xx in range(dcx - r_, dcx + r_ + 1):
                e = ((xx - dcx) / float(r_)) ** 2 + ((yy - 30) / float(r_ * 0.9)) ** 2
                if e <= 1.0:
                    D.px(xx, yy, 0.86 - 0.30 * max(0.0, (xx - dcx) / float(r_)) + 0.08 * (yy < 30 - r_ * 0.6))
    put_tone(pic, D, DOME, dither=0.4)
    A = Tone(w, pic.h)
    for k in range(7):
        ax = 18 + k * 40
        for yy in range(52, 84):
            for xx in range(ax, ax + 16):
                u = abs(xx - (ax + 7.5)) / 8.0
                if yy < 60 and (yy - 52) < 8 - 8 * np.sqrt(max(0.0, 1 - u * u)):
                    continue
                A.px(xx, yy, 0.10 + 0.04 * (yy > 78))
    put_tone(pic, A, STZ.SOOT, dither=0)
    y0 = BASE + 2 - pic.h
    L.paste(pic, x, y0)
    plat('bathroof1', [[x + 84, y0 + 30], [x + 120, y0 + 30]])
    plat('bathroof2', [[x + 180, y0 + 30], [x + 214, y0 + 30]])
    return dict(x0=x, x1=x + w, roof=y0 + 30)


def springs(L, seed=301):
    """Zone 3: the road down into Hammam Ali's valley, a farm's wall, the village's houses, the pools, the bathhouse, the
    car park (the convoy's lorries are the game's) and the open ground where he holds his vote."""
    h1 = low_house(L, 8700, 88, seed + 1, roof_y=124, pid='vroof1')
    t1 = tower(L, 8800, 90, 112, seed + 2, 'stone')
    h2 = low_house(L, 8900, 80, seed + 3, roof_y=120, pid='vroof2')
    pools = [pool(L, 9010, 9150, seed=1), pool(L, 9230, 9390, seed=2)]
    h3 = low_house(L, 9420, 90, seed + 4, roof_y=124, pid='vroof3')
    b = bathhouse(L, 9540, seed + 10)
    pools.append(pool(L, 9860, 9990, seed=3))
    pools.append(pool(L, 10120, 10250, seed=4))           # (the last, beside the vote's ground: its steam is the vote's)
    INFO['springs'] = dict(pools=pools, bath=b, doors=[h1['door'], t1['doors'][0]['x'], h2['door'], h3['door']])
    # the car park and the vote's ground: a long low wall at the back, a lamp post, nothing else (the game's lorries)
    with swap(Z1, DRYST=WALLD, GRASS=GOLDF):
        Z1.drystone(L, 10020, END, 148, BASE + 1, seed=seed + 20)
    INFO['carpark'] = dict(x0=10020, x1=END)


# ------------------------------------------------------------------ the whole play picture
def play(seed=0):
    """-> the play picture (0 to END), PLATS and INFO filled."""
    PLATS.clear(); INFO.clear()
    L = Layer(END, SH)
    ground(L)
    plain(L)
    city(L)
    springs(L)
    return L


def fore(seed=131):
    """-> the foreground's strip along the whole mission (at 1.25 of the street's pace): dry tufts and stones."""
    with swap(Z1, GRASS=GOLDF):
        return Z1.fore_z1(w=int(END * 1.25) + 600, seed=seed)
