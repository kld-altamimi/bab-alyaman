# stage_taiz.py - Taiz (the mission by Apache), painted as the Strait, the Coffee Port and the Souq are: tone fields mapped
# through colour ramps, checker dither between neighbours, light from the upper left, no outlines on scenery.
# Unlike the missions on foot, Taiz is not one long strip: the camera climbs as well as going along, so the stage is a set
# of pieces (each tower house, the city gate, the souq's stalls, the bridge, the castle's walls and towers...), each painted
# at its own size and placed in the world by export_taiz.py, which also writes down where everything is (roofs to stand
# on, doors men come out of, windows that light up at night) as it is painted.
# Everything is painted in daylight colours: the game darkens it for the night and lights what gives light of its own
# (windows, lamps, the castle's floodlights) over the top, as the teaser does.
import numpy as np
from scipy import ndimage as ndi
from paint import *
import props as P
import stage_mocha as SM
import stage_zabid as SZ

# ------------------------------------------------------------------ colour ramps (dark to pale)
LIME = SM.LIME                                                                                                  # lime plaster, gypsum
BASALT = ramp(['#0e0c0e', '#1e1a1c', '#2e2a2a', '#423c3a', '#58504c', '#706662', '#8a807a', '#a49a92'], 16)      # Taiz's dark volcanic stone
TSTONE = ramp(['#1c140e', '#36281c', '#52402e', '#6e5840', '#8a7254', '#a68c6a', '#c0a684', '#d8c2a2'], 18)      # the town's brown stone
OCHRE = ramp(['#24160a', '#463014', '#6a4a20', '#8c6630', '#ac8444', '#c8a260', '#dcc084', '#eedcae'], 18)       # ochre-washed walls
CASTLE = ramp(['#20160c', '#403020', '#644c34', '#86684a', '#a68660', '#c2a47a', '#dac096', '#ecd8b4'], 18)      # the castle's dressed stone
EARTHT = ramp(['#160e08', '#2c1e12', '#46321e', '#62482c', '#7e603e', '#987a54', '#b2966e'], 14)                # the hillside's earth
ROCKT = ramp(['#121012', '#262022', '#3a3230', '#504640', '#685c52', '#827466', '#9c8e7e', '#b4a898'], 16)        # the castle rock
ASPHALT = ramp(['#0e0e10', '#1c1c1e', '#2a2a2c', '#3a3a3a', '#4c4a48', '#5e5c58'], 10)
TEAK = SM.TEAK
IRON = SM.IRON
SOOT = SM.SOOT
TANK = SZ.TANK
BLUEWOOD = SZ.BLUEWOOD
GREENWOOD = ramp(['#06140c', '#0c2616', '#163e22', '#225832', '#367446', '#58945e', '#8ab888'], 12)
REDWOOD = ramp(['#1a0806', '#38100a', '#5c1c10', '#80301a', '#a44a28', '#c46c40', '#dc9464'], 12)
GLASSQ = ramp(['#0c0c14', '#181a2a', '#262a40', '#363c56', '#4a5068'], 6)                                          # a fanlight's glass by day: dark
CLOTH_R, CLOTH_B, CLOTH_Y, CLOTH_G = SZ.CLOTH_R, SZ.CLOTH_B, SZ.CLOTH_Y, SZ.CLOTH_G
SHRUB = ramp(['#0a1008', '#162212', '#24361c', '#344c26', '#4a6434', '#647e46'], 10)
SAND_ = ramp(['#2a1e14', '#4c3a26', '#6e5638', '#8e744e', '#ae9268', '#c8ae86'], 12)

put_tone = SM.put_tone


def piece(w, h):
    return Layer(int(w), int(h))


# ------------------------------------------------------------------ walls: courses of stone, plaster, the white bands
def ashlar(L, x0, y0, x1, y1, rmp, seed=1, course=6, block=(10, 22), base=0.52, light=0.0, rough=0.10):
    """Dressed stone laid in courses: each block a slightly different tone, its top edge lit, its joints dark; the right
    third of the wall a little in shadow (light from the upper left), grime gathering low down."""
    w, h = x1 - x0, y1 - y0
    if w <= 0 or h <= 0:
        return
    r = rng(seed)
    T = Tone(L.w, L.h)
    yy, xx = np.mgrid[0:h, 0:w]
    tone = np.zeros((h, w))
    joint = np.zeros((h, w), bool)
    lit = np.zeros((h, w), bool)
    row = 0
    y = 0
    while y < h:
        ch = course + int(r.integers(-1, 2))
        off = int(r.integers(0, block[1]))
        x = -off
        while x < w:
            bw = int(r.integers(block[0], block[1] + 1))
            m = (xx >= x) & (xx < x + bw) & (yy >= y) & (yy < y + ch)
            tone[m] = r.uniform(-0.07, 0.07)
            joint |= (xx == x) & (yy >= y) & (yy < y + ch)
            lit |= (xx == x + 1) & (yy >= y + 1) & (yy < y + ch - 1)
            x += bw
        joint |= (yy == y + ch - 1)
        lit |= (yy == y)
        y += ch
        row += 1
    grit = fbm((h, w), seed + 3, 1.5, 1.0, octaves=2) - 0.5
    stain = np.clip(fbm((h, w), seed + 5, 8, 18, octaves=3) - 0.55, 0, 1) * 1.6
    side = np.clip((xx - w * 0.62) / max(1.0, w * 0.38), 0, 1)
    low = np.clip((yy - h * 0.70) / max(1.0, h * 0.30), 0, 1)
    t = base + light + tone + rough * grit - 0.16 * side - 0.10 * low - 0.18 * stain
    t = np.where(lit, t + 0.10, t)
    t = np.where(joint, t - 0.24, t)
    T.t[y0:y1, x0:x1] = t
    T.m[y0:y1, x0:x1] = True
    put_tone(L, T, rmp, dither=0.45)


def plaster(L, x0, y0, x1, y1, rmp=LIME, seed=1, base=0.80, stain=1.0):
    """Lime plaster over the stone: smooth, pale, streaked where the rain runs down, a little patchy."""
    w, h = x1 - x0, y1 - y0
    if w <= 0 or h <= 0:
        return
    T = Tone(L.w, L.h)
    yy, xx = np.mgrid[0:h, 0:w]
    patch = fbm((h, w), seed, 14, 10, octaves=3)
    streak = np.clip(fbm((h, w), seed + 1, 2.5, 26, octaves=3) - 0.58, 0, 1) * 1.8 * stain
    side = np.clip((xx - w * 0.62) / max(1.0, w * 0.38), 0, 1)
    t = base + 0.08 * (patch - 0.5) - 0.20 * streak - 0.12 * side
    T.t[y0:y1, x0:x1] = t
    T.m[y0:y1, x0:x1] = True
    put_tone(L, T, rmp, dither=0.4)


def white_band(L, x0, x1, y, h=4, kind=0, seed=1):
    """The white gypsum band between floors, carved: a row of lozenges, a zigzag, or plain mouldings (Taiz's houses wear
    them as the Sana'a ones do)."""
    SZ.stucco_band(L, x0, x1, y, h=h, seed=seed, kind=kind)


def merlons_point(L, x0, x1, top, seed=1):
    """The white teeth along a parapet's top: little pointed ones, close together."""
    T = Tone(L.w, L.h)
    x = x0
    while x < x1 - 4:
        for j in range(4):
            T.rect(x + j // 2, top - j, x + 4 - j // 2, top - j, 0.94 - 0.05 * j)
        T.px(x + 4, top, 0.70)
        x += 6
    put_tone(L, T, LIME, dither=0)


# ------------------------------------------------------------------ windows, doors
def qamariya_window(L, x, y, w=10, h=14, paint=BLUEWOOD, open_=False, seed=1, glass=True):
    """A Taiz window: a white frame, wooden shutters, and over it the qamariya, a half-moon of coloured glass in a white
    surround (dark by day; the game lights the glass and the window at night). Returns where the glass and the window are."""
    F = Tone(L.w, L.h)
    # the white surround: the frame, and the arch over the fanlight
    r_ = w / 2.0 + 1.5
    cxq, cyq = x + (w - 1) / 2.0, y - 1
    for j in range(-int(r_) - 3, h + 2):
        for i in range(-2, w + 2):
            inside_win = 0 <= i < w and 0 <= j < h
            if inside_win:
                continue
            px_, py_ = x + i, y + j
            if j < 0:
                d = np.hypot(px_ - cxq, (py_ - cyq) * 1.15)
                if d > r_ + 1.6:
                    continue
                if d < r_ - 1.0:
                    continue
            F.px(px_, py_, 0.96 if (i < w // 2 or j < 0) else 0.80)
    # a ledge under it
    F.rect(x - 2, y + h + 1, x + w + 1, y + h + 1, 0.88)
    F.rect(x - 1, y + h + 2, x + w, y + h + 2, 0.60)
    put_tone(L, F, LIME, dither=0)
    # the glass of the fanlight (dark by day)
    G = Tone(L.w, L.h)
    for j in range(-int(r_), 0):
        for i in range(0, w):
            px_, py_ = x + i, y + j
            if np.hypot(px_ - cxq, (py_ - cyq) * 1.15) < r_ - 1.0:
                G.px(px_, py_, 0.30 + 0.25 * (((i // 2) + j) % 2))
    put_tone(L, G, GLASSQ, dither=0)
    # the window: dark inside, shutters
    D = Tone(L.w, L.h)
    D.rect(x, y, x + w - 1, y + h - 1, 0.10)
    put_tone(L, D, SOOT, dither=0.3)
    S = Tone(L.w, L.h)
    if open_:
        for j in range(h):
            S.px(x, y + j, 0.56 - 0.1 * (j % 4 == 0)); S.px(x + 1, y + j, 0.38)
            S.px(x + w - 1, y + j, 0.46 - 0.1 * (j % 4 == 0)); S.px(x + w - 2, y + j, 0.30)
    else:
        for j in range(h):
            for i in range(w):
                S.px(x + i, y + j, 0.54 - 0.20 * (i == w // 2) + 0.10 * (j % 4 == 0) - 0.08 * (i > w // 2))
    put_tone(L, S, paint, dither=0.3)
    return dict(x=int(x), y=int(y), w=int(w), h=int(h), fan=[int(x), int(y - r_), int(w), int(r_)], open=bool(open_))


def small_window(L, x, y, w=6, h=7, paint=BLUEWOOD):
    """A small square window high up, with a white frame (a stair window, a storeroom's)."""
    F = Tone(L.w, L.h)
    F.rect(x - 1, y - 1, x + w, y + h, 0.92)
    put_tone(L, F, LIME, dither=0)
    D = Tone(L.w, L.h)
    D.rect(x, y, x + w - 1, y + h - 1, 0.10)
    put_tone(L, D, SOOT, dither=0)
    return dict(x=int(x), y=int(y), w=int(w), h=int(h), fan=None, open=True)


def arched_door(L, x, base, w=14, h=24, paint=TEAK, open_=False, seed=1):
    """A door under a pointed arch in a white surround: shut, or open on the dark (men come out of these)."""
    T = Tone(L.w, L.h)
    y0 = base - h
    for j in range(-7, h):
        for i in range(-3, w + 3):
            inside = 0 <= i < w and j >= 0
            if inside:
                continue
            u = abs(i - (w - 1) / 2.0)
            if j < 0 and u > (w / 2.0 + 3) - (7 + j) * 0.95:
                continue
            T.px(x + i, y0 + j, 0.92 - 0.22 * (i >= w) + (0.05 if (i + j) % 4 == 0 else 0))
    put_tone(L, T, LIME, dither=0.3)
    D = Tone(L.w, L.h)
    for j in range(-5, h):
        for i in range(w):
            u = abs(i - (w - 1) / 2.0)
            if j < 0 and u > (w / 2.0) - (5 + j) * 0.95:
                continue
            if open_:
                D.px(x + i, y0 + j, 0.06 + 0.10 * (i == w - 1))
            else:
                D.px(x + i, y0 + j, 0.50 - 0.20 * (i == w // 2) + 0.10 * ((j % 6) == 0) - 0.08 * (i > w // 2) + 0.20 * ((i % 4 == 1) and (j % 6 == 3)))
    put_tone(L, D, SOOT if open_ else paint, dither=0.3)
    if open_:
        E = Tone(L.w, L.h)                                  # the door leaf swung in, its edge catching the light
        for j in range(h):
            E.px(x + 1, y0 + j, 0.46); E.px(x + 2, y0 + j, 0.34)
        put_tone(L, E, paint, dither=0)
    return dict(x=int(x + w // 2), y=int(base), w=int(w), h=int(h))


# ------------------------------------------------------------------ a tower house
def taiz_house(w, h, seed=1, style=None, roof=None, door='street', floors=None):
    """A tower house of Taiz, w wide and h tall from the street to its parapet's top, with ROOM px above for what stands on
    the roof. style: 'stone' (brown stone all the way up), 'lime' (plastered above a basalt ground floor), 'ochre', 'mixed'
    (stone below, plaster above). roof: the props on its roof: a list of 'stair' (a stair-head with its door: men come up
    through it), 'tank', 'dish', 'line'. Returns the picture and what the level needs: where its roof is, its doors and
    its windows (relative to the picture's top left; the house's foot is at the bottom of the picture)."""
    r = rng(seed)
    ROOM = 44
    W, Hh = int(w), int(h) + ROOM
    L = piece(W, Hh)
    top = ROOM                                               # the parapet's top
    base = Hh                                                # the street
    style = style or ['stone', 'lime', 'ochre', 'mixed'][int(r.integers(0, 4))]
    gf = 34 + int(r.integers(0, 6))                          # the ground floor's height
    par = 7                                                  # the parapet's height
    nfl = floors or max(2, int(round((h - gf - par) / 40.0)))
    fh = (h - gf - par) / float(nfl)
    # the ground floor: the dark stone
    ashlar(L, 0, base - gf, W, base, BASALT, seed=seed + 1, course=6, block=(9, 18), base=0.46)
    # the floors above
    paint = [BLUEWOOD, GREENWOOD, TEAK, REDWOOD][int(r.integers(0, 4))]
    for f in range(nfl):
        y1 = int(round(base - gf - f * fh)); y0 = int(round(base - gf - (f + 1) * fh))
        mat = style
        if style == 'mixed':
            mat = 'stone' if f < nfl // 2 else 'lime'
        if mat == 'stone':
            ashlar(L, 0, y0, W, y1, TSTONE, seed=seed + 10 + f, course=6, block=(10, 22), base=0.56)
        elif mat == 'ochre':
            plaster(L, 0, y0, W, y1, OCHRE, seed=seed + 10 + f, base=0.66)
        else:
            plaster(L, 0, y0, W, y1, LIME, seed=seed + 10 + f, base=0.80)
    # the parapet, and its white teeth
    if style in ('stone', 'mixed') and nfl > 0:
        pass
    plaster(L, 0, top, W, top + par, LIME, seed=seed + 40, base=0.86, stain=0.3)
    merlons_point(L, 0, W, top - 1, seed=seed)
    # the white bands between the floors (and under the parapet)
    kinds = [0, 1, 2]
    for f in range(nfl):
        y = int(round(base - gf - f * fh)) - 2
        white_band(L, 0, W, y, h=4 if f else 5, kind=kinds[(f + seed) % 3], seed=seed + f)
    white_band(L, 0, W, top + par - 1, h=4, kind=(seed + 1) % 3, seed=seed + 50)
    # windows, a row to each floor (fewer and smaller in a narrow house), the fanlights over them
    wins = []
    nw = max(1, int((W - 8) // 24))
    span = W / float(nw)
    for f in range(nfl):
        y0 = int(round(base - gf - (f + 1) * fh))
        wy = y0 + int(fh * 0.38)
        for k in range(nw):
            if r.random() < 0.12 and nw > 1:
                continue
            ww = 10 if span >= 20 else 8
            wx = int(span * k + span / 2 - ww / 2)
            open_ = r.random() < 0.35
            wins.append(qamariya_window(L, wx, wy, w=ww, h=14, paint=paint, open_=open_, seed=seed + f * 7 + k))
    # the ground floor: the street door, a small window
    doors = []
    dx = int(W * (0.25 + 0.5 * r.random())) - 7
    if door == 'street':
        doors.append(dict(arched_door(L, dx, base, w=14, h=24, paint=paint, open_=False, seed=seed), kind='street'))
    if W > 50:
        sx = dx + 24 if dx + 30 < W else dx - 18
        if 0 < sx < W - 8:
            wins.append(small_window(L, sx, base - gf + 9, w=6, h=7))
    # the side in shadow, and the shadow under the parapet's lip
    for y in range(top, base):
        for x in range(W - 3, W):
            if L.a[y, x]:
                L.rgb[y, x] = (L.rgb[y, x].astype(float) * (0.80 - 0.05 * (x - (W - 3)))).astype(np.uint8)
    for x in range(W):
        y = top + par + 3
        if L.a[y, x]:
            L.rgb[y, x] = (L.rgb[y, x].astype(float) * 0.80).astype(np.uint8)
    # on the roof
    props = list(roof if roof is not None else [])
    stair = None
    if 'stair' in props:
        sw = 26
        sx0 = 3 if r.random() < 0.5 else W - sw - 3
        st_top = stair_head(L, sx0, sx0 + sw, top - 1, seed=seed)
        stair = dict(x=int(sx0 + sw // 2), y=int(top - 1), top=int(st_top), x0=int(sx0), x1=int(sx0 + sw))
    if 'tank' in props:
        cx_ = W - 16 if stair is None or stair['x'] < W / 2 else 16
        SZ.water_tank(L, cx_, top - 1, seed=seed)
    if 'dish' in props:
        SZ.dish_at(L, int(W * 0.5), top - 1, seed=seed)
    if 'line' in props and W > 60:
        SZ.washing_line(L, 6, W - 8, top - 30, sag=5, seed=seed)
    return L, dict(w=W, h=Hh, top=top, base=base, doors=doors, windows=wins, stair=stair, style=style)


def stair_head(L, x0, x1, base, seed=1):
    """The little room on the roof that the stair comes up into: plastered, its top flat, its door open on the dark of the
    stairwell (men come up through it)."""
    T = Tone(L.w, L.h)
    top = base - 28
    for y in range(top, base):
        for x in range(x0, x1):
            u = (x - x0) / float(x1 - x0)
            t = 0.84 - 0.16 * u - 0.08 * (y > base - 4) + 0.03 * (((x * 5 + y * 3) % 9) == 0)
            if y < top + 3:
                t = 0.94 if y == top else 0.72
            T.px(x, y, t)
    put_tone(L, T, LIME, dither=0.4)
    merlons_point(L, x0, x1, top - 1, seed=seed)
    cx_ = (x0 + x1) // 2
    arched_door(L, cx_ - 6, base, w=12, h=20, paint=TEAK, open_=True, seed=seed)
    return top


# ------------------------------------------------------------------ the low town along the street (the opening)
def shop_row(w, seed=1, doors_at=(), lamp_at=None):
    """The street's low side in the lower town, where the opening is played: one- and two-storey houses and shops, their
    shutters down for the night, doors (the Zanabeel run into these), so that the castle and the mountain show over them,
    as in the teaser. Returns the picture (its foot at the bottom) and the doors' places."""
    r = rng(seed)
    W, Hh = int(w), 130
    L = piece(W, Hh)
    base = Hh
    x = 0
    doors = []
    while x < W:
        bw = int(r.integers(70, 130))
        x1 = min(W, x + bw)
        hh = int(r.integers(58, 104))
        top = base - hh
        mat = r.random()
        if mat < 0.4:
            ashlar(L, x, top, x1, base, TSTONE, seed=seed + x, course=6, block=(10, 22), base=0.54)
        elif mat < 0.7:
            plaster(L, x, top, x1, base, LIME, seed=seed + x, base=0.78)
            ashlar(L, x, base - 20, x1, base, BASALT, seed=seed + x + 1, course=5, block=(8, 16), base=0.46)
        else:
            plaster(L, x, top, x1, base, OCHRE, seed=seed + x, base=0.64)
        plaster(L, x, top, x1, top + 4, LIME, seed=seed + x + 3, base=0.88, stain=0.2)
        merlons_point(L, x, x1, top - 1, seed=seed)
        white_band(L, x, x1, top + 3, h=3, kind=int(r.integers(0, 3)), seed=seed + x)
        # shop shutters (rolled down, corrugated) and doors along the street
        sx = x + 6
        while sx < x1 - 26:
            kind = r.random()
            if kind < 0.45:
                T = Tone(L.w, L.h)
                sw_ = int(r.integers(20, 30))
                for yy in range(base - 30, base):
                    for xx in range(sx, min(x1 - 4, sx + sw_)):
                        T.px(xx, yy, 0.46 + 0.16 * ((yy % 3) == 0) - 0.10 * (xx > sx + sw_ * 0.6))
                T.rect(sx - 1, base - 32, min(x1 - 4, sx + sw_), base - 31, 0.70)
                put_tone(L, T, SZ.TIN, dither=0.2)
                sx += sw_ + 8
            elif kind < 0.8:
                d = arched_door(L, sx, base, w=14, h=26, paint=[BLUEWOOD, GREENWOOD, TEAK][int(r.integers(0, 3))], open_=False, seed=seed + sx)
                doors.append(d)
                sx += 24
            else:
                qamariya_window(L, sx + 2, base - 46 if hh > 70 else base - 40, w=10, h=12, paint=BLUEWOOD, open_=r.random() < 0.5)
                sx += 22
        if hh > 80:
            qamariya_window(L, x + (x1 - x) // 2 - 5, top + 18, w=10, h=14, paint=GREENWOOD, open_=False)
        x = x1 + int(r.integers(0, 4))
    for (dxp) in doors_at:
        doors.append(arched_door(L, int(dxp) - 7, base, w=14, h=26, paint=TEAK, open_=True, seed=seed + int(dxp)))
    return L, dict(w=W, h=Hh, doors=doors)


def street_lamp(seed=1):
    """An iron street lamp on a post, its lantern (the game lights it)."""
    L = piece(14, 70)
    T = Tone(14, 70)
    T.rect(6, 12, 7, 69, 0.50)
    T.rect(5, 66, 8, 69, 0.40)
    T.rect(3, 10, 10, 11, 0.62)
    T.rect(4, 2, 9, 9, 0.30)
    T.rect(3, 1, 10, 1, 0.66)
    put_tone(L, T, IRON, dither=0)
    G = Tone(14, 70)
    G.rect(5, 3, 8, 8, 0.72)
    put_tone(L, G, SM.LIGHT, dither=0)
    return L, dict(w=14, h=70, light=[6, 5])


def paving_strip(w, h=40, seed=3):
    """The street's paving: big dark slabs (the lower town's basalt), worn, laid in courses."""
    L = piece(w, h)
    yy, xx = np.mgrid[0:h, 0:w]
    r = rng(seed)
    tone = np.full((h, w), 0.50)
    joint = np.zeros((h, w), bool)
    lit = np.zeros((h, w), bool)
    rows = [0, 4, 9, 15, 22, 30, h + 4]
    for k in range(len(rows) - 1):
        a, b = rows[k], rows[k + 1]
        band = (yy >= a) & (yy < b)
        x = -int(r.integers(0, 30))
        while x < w + 40:
            bw = int(r.integers(int(18 + (b - a) * 2), int(30 + (b - a) * 3)))
            lean = ((yy - a) * -0.3).astype(int)
            m = band & (xx - lean >= x) & (xx - lean < x + bw)
            tone[m] = 0.50 + r.uniform(-0.07, 0.07)
            joint |= band & (xx - lean == x)
            lit |= band & (xx - lean == x + 1)
            x += bw
        joint |= (yy == b - 1) & band
        lit |= (yy == a) & band
    grit = fbm((h, w), seed + 1, 1.4, 0.8, octaves=2) - 0.5
    depth = yy / float(h)
    t = tone + 0.10 * grit - 0.12 * depth
    t = np.where(lit, t + 0.10, t)
    t = np.where(joint, t - 0.26, t)
    far = np.clip(1 - yy / 6.0, 0, 1)
    t = t * (1 - 0.3 * far) + 0.62 * 0.3 * far
    L.put(toned(np.clip(t, 0.04, 1), BASALT, dither=0.5), np.ones((h, w), bool))
    return L


# ------------------------------------------------------------------ the old city: its wall and Bab al-Kabir
def city_gate(seed=7):
    """The old city's wall and its great gate: two square towers with their battlements, the gate's pointed arch between
    them over a passage (its doors open for the day: the Zanabeel's), the wall running away either side. 260 wide; the
    towers 330 tall, the wall 210."""
    W, Hh = 260, 344
    L = piece(W, Hh)
    base = Hh
    # the wall either side
    ashlar(L, 0, base - 210, W, base, TSTONE, seed=seed, course=7, block=(12, 26), base=0.50)
    # the towers
    for tx0, tx1 in ((10, 80), (180, 250)):
        ashlar(L, tx0, base - 330, tx1, base, TSTONE, seed=seed + tx0, course=7, block=(12, 24), base=0.58)
        T = Tone(L.w, L.h)
        for m in range(tx0, tx1 - 4, 9):
            T.rect(m, base - 341, m + 5, base - 331, 0.60)
            T.rect(m, base - 341, m + 5, base - 341, 0.78)
        put_tone(L, T, TSTONE, dither=0.3)
        white_band(L, tx0, tx1, base - 300, h=4, kind=1, seed=seed)
        for sy in range(base - 280, base - 120, 46):
            small_window(L, (tx0 + tx1) // 2 - 2, sy, w=4, h=9)
    # the battlements along the wall
    T = Tone(L.w, L.h)
    for m in range(80, 180, 9):
        T.rect(m, base - 220, m + 5, base - 211, 0.58)
    for m in range(0, 10, 9):
        T.rect(m, base - 220, m + 5, base - 211, 0.58)
    for m in range(250, W, 9):
        T.rect(m, base - 220, m + 5, base - 211, 0.58)
    put_tone(L, T, TSTONE, dither=0.3)
    # the gate: a pointed arch, its white surround, the passage dark, the doors open
    gx0, gx1, gtop = 98, 162, base - 130
    T = Tone(L.w, L.h)
    D = Tone(L.w, L.h)
    cxg = (gx0 + gx1) / 2.0
    for y in range(gtop - 24, base):
        for x in range(gx0 - 8, gx1 + 8):
            u = abs(x - cxg)
            half = (gx1 - gx0) / 2.0
            if y >= gtop:
                inner = u < half
            else:
                inner = u < half - (gtop - y) * 1.1
            outer = u < half + 7 - max(0, (gtop - y)) * 1.0 if y < gtop else u < half + 7
            if inner:
                D.px(x, y, 0.06 + 0.04 * (y > base - 30))
            elif outer:
                T.px(x, y, 0.90 - 0.2 * (x > cxg))
    put_tone(L, T, LIME, dither=0.3)
    put_tone(L, D, SOOT, dither=0.3)
    E = Tone(L.w, L.h)
    for y in range(gtop, base):
        for i in range(5):
            E.px(gx0 + 1 + i, y, 0.50 - 0.05 * i + 0.1 * ((y % 9) == 0))
            E.px(gx1 - 2 - i, y, 0.42 - 0.05 * i + 0.1 * ((y % 9) == 0))
    put_tone(L, E, TEAK, dither=0)
    return L, dict(w=W, h=Hh, towers=[[10, 80, base - 341], [180, 250, base - 341]], wall=base - 220, arch=[gx0, gx1, gtop])


# ------------------------------------------------------------------ the souq's square: stalls, awnings, the back houses
def souq_back(w, h=300, seed=11):
    """The houses behind the souq's square (seen across it, a little darker, nothing to touch): balconies, shuttered
    windows, washing; their windows light up at night."""
    L = piece(w, h)
    r = rng(seed)
    x = 0
    wins = []
    while x < w:
        bw = int(r.integers(60, 100))
        x1 = min(w, x + bw)
        hh = int(r.integers(200, h))
        top = h - hh
        if r.random() < 0.5:
            plaster(L, x, top, x1, h, LIME, seed=seed + x, base=0.68)
        else:
            ashlar(L, x, top, x1, h, TSTONE, seed=seed + x, base=0.46)
        merlons_point(L, x, x1, top - 1, seed=seed)
        for fy in range(top + 20, h - 60, 40):
            white_band(L, x, x1, fy + 26, h=3, kind=int(r.integers(0, 3)), seed=seed + fy)
            for wx in range(x + 8, x1 - 14, 22):
                wins.append(qamariya_window(L, wx, fy + 6, w=10, h=13, paint=BLUEWOOD, open_=r.random() < 0.4))
            if r.random() < 0.35:
                SZ.mashrabiya(L, x + bw // 2 - 10, fy, w=20, h=20, seed=seed + fy)
        x = x1 + int(r.integers(0, 3))
    # (a little darker: it is across the square)
    L.rgb[:] = (L.rgb.astype(float) * 0.82).astype(np.uint8)
    return L, dict(w=w, h=h, windows=wins)


def souq_stall(w=70, seed=1, cloth=None):
    """A stall in the square under its awning: a counter, heaps of spice and sacks, strings of chillies; the awning's top
    is somewhere to stand."""
    Hh = 70
    L = piece(w + 8, Hh)
    base = Hh
    cloth = cloth if cloth is not None else [CLOTH_R, CLOTH_Y, CLOTH_G, CLOTH_B][seed % 4]
    SZ.stall_counter(L, 6, w - 2, base - 22, seed=seed)
    # poles and the awning
    SZ.awning(L, 2, w + 4, base - 66, depth=12, rmp=cloth, stripes=8, seed=seed, sag=2)
    return L, dict(w=w + 8, h=Hh, top=base - 66)


# ------------------------------------------------------------------ the hillside: terraces, the road, the bridge
def terrace_wall(w, h, seed=21):
    """A terrace's retaining wall: rough stone laid dry, darker at its foot, a lip of earth and a few weeds on top."""
    L = piece(w, h + 4)
    ashlar(L, 0, 4, w, h + 4, TSTONE, seed=seed, course=5, block=(6, 14), base=0.48, rough=0.18)
    T = Tone(L.w, L.h)
    for x in range(w):
        T.px(x, 3, 0.40)
        T.px(x, 4, 0.30)
    put_tone(L, T, EARTHT, dither=0)
    r = rng(seed)
    S = Tone(L.w, L.h)
    for k in range(w // 12):
        x = int(r.integers(0, w))
        for j in range(int(r.integers(2, 5))):
            S.px(x + int(r.integers(-1, 2)), 3 - j, 0.4 + 0.1 * j)
    put_tone(L, S, SHRUB, dither=0)
    return L


def stone_bridge(seed=31):
    """The old bridge over the wadi: a single pointed arch of dressed stone between two heavy piers, a parapet along its
    deck (the road runs over it). 320 wide; the deck 20 below the top, the arch's opening 200 wide and 180 tall."""
    W, Hh = 320, 240
    L = piece(W, Hh)
    ashlar(L, 0, 6, W, Hh, TSTONE, seed=seed, course=7, block=(12, 26), base=0.54)
    # the opening: a pointed arch
    D = np.zeros((Hh, W), bool)
    cxb, half, spring = W / 2.0, 100.0, 80
    yy, xx = np.mgrid[0:Hh, 0:W]
    u = np.abs(xx - cxb)
    D |= (yy >= spring) & (u < half)
    # the arch's two curves meet at a point
    r_ = half * 1.25
    left_c, right_c = cxb + half - r_, cxb - half + r_
    D |= (yy < spring) & (yy > 20) & (np.hypot(xx - left_c, (yy - spring) * 1.0) < r_) & (np.hypot(xx - right_c, (yy - spring) * 1.0) < r_)
    L.a[D] = False
    # voussoirs round the arch
    ring = ndi.binary_dilation(D, iterations=6) & ~D
    T = Tone(L.w, L.h)
    T.mask(ring, 0.70)
    put_tone(L, T, TSTONE, dither=0.3)
    ring2 = ndi.binary_dilation(D, iterations=1) & ~D
    T2 = Tone(L.w, L.h)
    T2.mask(ring2, 0.30)
    put_tone(L, T2, TSTONE, dither=0)
    # the parapet
    T3 = Tone(L.w, L.h)
    T3.rect(0, 0, W - 1, 6, 0.66)
    T3.rect(0, 0, W - 1, 0, 0.84)
    for x in range(0, W, 20):
        T3.rect(x, 1, x, 6, 0.40)
    put_tone(L, T3, TSTONE, dither=0)
    return L, dict(w=W, h=Hh, deck=20, opening=[int(cxb - half), int(cxb + half), 20, Hh])


def water_tower(seed=41):
    """A water tank up on an iron tower on the hillside."""
    W, Hh = 46, 120
    L = piece(W, Hh)
    T = Tone(W, Hh)
    for lx in (8, 37):
        T.line([(lx, 119), (lx + (4 if lx < 20 else -4), 40)], 0.50, width=2)
    for y in (60, 84, 106):
        T.line([(9, y), (36, y)], 0.40)
        T.line([(9, y), (36, y - 22)], 0.34)
    put_tone(L, T, IRON, dither=0)
    K = Tone(W, Hh)
    for y in range(8, 42):
        for x in range(4, 42):
            u = (x - 4) / 38.0
            K.px(x, y, 0.30 + 0.5 * np.exp(-((u - 0.32) / 0.22) ** 2) - 0.12 * ((y - 8) % 6 == 0))
    K.rect(6, 6, 39, 7, 0.60)
    put_tone(L, K, TANK, dither=0.3)
    return L, dict(w=W, h=Hh)


# ------------------------------------------------------------------ Al-Qahira: the castle's walls, towers, bastion, keep
def battlements(L, x0, x1, top, rmp=CASTLE, seed=1, tooth=7, gap=5, hgt=9):
    T = Tone(L.w, L.h)
    x = x0
    while x < x1:
        T.rect(x, top, min(x1 - 1, x + tooth - 1), top + hgt, 0.62)
        T.rect(x, top, min(x1 - 1, x + tooth - 1), top, 0.82)
        T.rect(min(x1 - 1, x + tooth - 1), top + 1, min(x1 - 1, x + tooth - 1), top + hgt, 0.44)
        x += tooth + gap
    put_tone(L, T, rmp, dither=0.3)


def castle_wall(w, h, seed=51, slits=True):
    """A stretch of the castle's wall: big dressed stones, battlements along its top (the wall walk is behind them),
    arrow slits."""
    L = piece(w, h + 10)
    top = 10
    ashlar(L, 0, top + 8, w, h + 10, CASTLE, seed=seed, course=8, block=(14, 30), base=0.58)
    battlements(L, 0, w, 0, seed=seed)
    T = Tone(L.w, L.h)
    T.rect(0, top + 8, w - 1, top + 9, 0.40)
    put_tone(L, T, CASTLE, dither=0)
    if slits:
        for x in range(18, w - 10, 34):
            for y in range(top + 30, h - 10, 46):
                T2 = Tone(L.w, L.h)
                T2.rect(x, y, x + 1, y + 10, 0.06)
                T2.rect(x - 1, y + 4, x + 2, y + 5, 0.06)
                put_tone(L, T2, SOOT, dither=0)
    return L, dict(w=w, h=h + 10, walk=top + 9)


def castle_tower(w, h, seed=61, windows=2):
    """A square tower of the castle, taller than the walls, battlements on top, a few windows."""
    L = piece(w, h + 12)
    ashlar(L, 0, 12, w, h + 12, CASTLE, seed=seed, course=8, block=(14, 28), base=0.64)
    battlements(L, 0, w, 0, seed=seed, hgt=11)
    T = Tone(L.w, L.h)
    T.rect(0, 12, w - 1, 13, 0.40)
    put_tone(L, T, CASTLE, dither=0)
    wins = []
    for k in range(windows):
        y = 40 + k * 56
        if y < h - 30:
            wins.append(small_window(L, w // 2 - 3, y, w=6, h=11))
    return L, dict(w=w, h=h + 12, top=0, windows=wins)


def keep(w=220, h=240, seed=71):
    """The keep: the castle's great tower, its upper floor with arched windows (lit at night), corner turrets."""
    L = piece(w, h + 20)
    ashlar(L, 0, 20, w, h + 20, CASTLE, seed=seed, course=8, block=(14, 30), base=0.62)
    battlements(L, 0, w, 8, seed=seed, hgt=12)
    for tx in (0, w - 30):
        ashlar(L, tx, 0, tx + 30, 60, CASTLE, seed=seed + tx, course=8, block=(10, 18), base=0.70)
        battlements(L, tx, tx + 30, -2, seed=seed + tx, tooth=6, gap=4, hgt=9)
    white_band(L, 0, w, 70, h=4, kind=2, seed=seed)
    wins = []
    for x in range(36, w - 40, 36):
        wins.append(qamariya_window(L, x, 96, w=12, h=18, paint=TEAK, open_=False, seed=seed + x))
    for x in range(54, w - 50, 54):
        wins.append(small_window(L, x, 170, w=6, h=10))
    return L, dict(w=w, h=h + 20, top=8, windows=wins)


def bastion(w=150, h=150, seed=81):
    """The bastion the Castle Gun stands on: a broad round-fronted platform of stone, sloping out at its foot."""
    L = piece(w, h + 10)
    T = np.zeros((h + 10, w), bool)
    yy, xx = np.mgrid[0:h + 10, 0:w]
    slope = np.clip((yy - 40) / float(h), 0, 1) * 10
    T |= (yy >= 10) & (xx >= 10 - slope) & (xx < w - 10 + slope)
    ashlar(L, 0, 10, w, h + 10, CASTLE, seed=seed, course=8, block=(14, 28), base=0.60)
    L.a &= T
    battlements(L, 10, w - 10, 0, seed=seed)
    return L, dict(w=w, h=h + 10, top=10)


# ------------------------------------------------------------------ the far view: Jabal Sabir, the castle on its rock
def jabal_sabir(w=1200, h=260, seed=91):
    """Jabal Sabir, behind the city: a great dark mass of rock, terraced on its lower slopes (painted in daylight colours:
    the game darkens it; its villages' lights are the game's)."""
    L = piece(w, h)
    x = np.arange(w)
    ridge = (h - 30 - 190 * np.exp(-((x - w * 0.55) / (w * 0.32)) ** 2) - 16 * np.sin(x / 47.0) - 8 * np.sin(x / 13.0 + 1.3)
             - 4 * np.sin(x / 5.3) - 40 * np.exp(-((x - w * 0.15) / (w * 0.10)) ** 2))
    yy, xx = np.mgrid[0:h, 0:w]
    m = yy >= ridge[None, :]
    d = (yy - ridge[None, :]) / 120.0
    tex = fbm((h, w), seed, 18, 7, octaves=4)
    terr = (np.sin((yy + 6 * np.sin(xx / 31.0)) / 3.2) > 0.75) & (d > 0.35)
    t = 0.46 + 0.20 * (tex - 0.5) - 0.18 * np.clip(d, 0, 1) - 0.06 * terr
    t += 0.10 * np.clip(1 - d * 6, 0, 1)
    L.put(toned(np.clip(t, 0.04, 1), ROCKT, dither=0.5), m)
    return L, dict(w=w, h=h, ridge=[int(v) for v in ridge[::4]], step=4)


def far_qahira(seed=93):
    """Al-Qahira on its rock, far off: the castle's long walls and its towers, the rock under it (the game floodlights it at
    night, warm, as the teaser has it)."""
    W, Hh = 230, 150
    L = piece(W, Hh)
    x = np.arange(W)
    rock_top = 70 - 18 * np.exp(-((x - 115) / 70.0) ** 2) + 4 * np.sin(x / 9.0)
    yy, xx = np.mgrid[0:Hh, 0:W]
    rm = (yy >= rock_top[None, :]) & (np.abs(xx - 115) < 112 - (Hh - yy) * 0.0)
    tex = fbm((Hh, W), seed, 6, 4, octaves=3)
    L.put(toned(np.clip(0.42 + 0.2 * (tex - 0.5) - 0.2 * (yy - 60) / 90.0, 0.05, 1), ROCKT, dither=0.5), rm)
    # the walls along the top, towers at intervals
    C = Layer(W, Hh)
    ashlar(C, 22, 34, 208, 66, CASTLE, seed=seed, course=4, block=(6, 12), base=0.64)
    for tx0, tx1, tt in ((20, 44, 12), (96, 128, 4), (180, 206, 16)):
        ashlar(C, tx0, tt, tx1, 66, CASTLE, seed=seed + tx0, course=4, block=(5, 10), base=0.70)
        battlements(C, tx0, tx1, tt - 5, seed=seed, tooth=4, gap=3, hgt=5)
    battlements(C, 22, 208, 29, seed=seed, tooth=4, gap=3, hgt=5)
    L.paste(C)
    return L, dict(w=W, h=Hh)


def moon():
    L = piece(18, 18)
    yy, xx = np.mgrid[0:18, 0:18]
    a = np.hypot(xx - 8.5, yy - 8.5) < 7.5
    b = np.hypot(xx - 12.0, yy - 6.5) < 6.8
    m = a & ~b
    t = 0.85 + 0.1 * (xx < 6)
    L.put(toned(t, SM.LIGHT, dither=0), m)
    return L
