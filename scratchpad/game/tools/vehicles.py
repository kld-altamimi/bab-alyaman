# vehicles.py - the things with engines: Salem's Shass, the Scorpion's gun trucks, the little drones and the flying boat.
# Painted the way the stage's set pieces are (tone through a ramp, lit from the upper left), then given the black line
# that everything in play carries. Own drawings throughout.
import sys, os, math
MOCK = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock'
sys.path.insert(0, MOCK)
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
from paint import *
import props as P
import ms3
from ms3 import at, compose, pal, FACES, WRAPS, INK2

GLASS = ramp(['#0a1824', '#143044', '#245068', '#3e748c', '#6a9cae', '#a2c6cc', '#d8eae8'], 10)
RUBBER = ramp(['#060608', '#101014', '#1c1c22', '#2e2e34', '#46464c', '#646468'], 8)
SANDP = ramp(['#2a2010', '#4e3c1e', '#7a6030', '#a48848', '#c6ac66', '#e0cc8c', '#f2e6b4'], 12)
OLIVE = P.OLIVE
WHITE = P.BOATWHITE
STEEL = P.STEEL
RUST = P.RUST
WOOD = P.WOOD
BRASS = ramp(['#3a2404', '#6e4a08', '#a87a14', '#d4a82c', '#f0d060', '#fff0a8'], 8)
WB = 58                       # wheelbase
WR = 9                        # wheel radius


def _px(L, x, y, rgb):
    if 0 <= x < L.w and 0 <= y < L.h:
        L.rgb[int(y), int(x)] = rgb
        L.a[int(y), int(x)] = True


def head_image(face, wrap, palette, end=None, wrap_dy=0):
    """One of the cast's heads on its own: (image, x of the nape, y of the chin)."""
    L = []
    if end:
        L.append((WRAPS[end], 0 - 1, 0 + 6, palette, INK2))
    L.append((FACES[face], 0, 5, palette))
    L.append((WRAPS[wrap], 0, wrap_dy, palette, INK2))
    im, fx, fy = compose(L, foot=(0, 13))
    return im, fx, fy


def pickup(paint=WHITE, livery='shass', seed=1):
    """A Land Cruiser pickup from the side, nose to the right, without its wheels.
    Returns (layer, x of the middle of the wheelbase, ground row)."""
    W, H = 106, 66
    g = H - 1
    cx = 52
    rx, fx = cx - WB // 2, cx + WB // 2            # wheel centres
    T = Tone(W, H)
    yy, xx = np.mgrid[0:H, 0:W]
    belt, roof, sill = g - 26, g - 41, g - 11
    # ---- far side of the bed, seen over the near side
    T.rect(7, belt - 3, 45, belt - 1, 0.50)
    T.rect(7, belt - 3, 45, belt - 3, 0.66)
    # ---- bed
    T.poly([(4, belt + 1), (46, belt + 1), (46, sill), (6, sill), (4, sill - 3)], 0.72)
    T.rect(4, belt + 1, 46, belt + 2, 0.94)                       # rail
    T.rect(4, belt + 3, 46, belt + 3, 0.60)
    for x in (12, 20, 28, 36):                                    # pressed ribs
        T.rect(x, belt + 6, x, sill - 4, 0.60)
        T.rect(x + 1, belt + 6, x + 1, sill - 4, 0.80)
    T.rect(4, belt + 1, 5, sill - 2, 0.56)                        # tailgate edge
    # ---- cab
    T.poly([(46, belt + 1), (47, roof + 2), (49, roof), (64, roof), (66, roof + 1), (75, belt), (75, sill), (46, sill)], 0.76)
    T.rect(49, roof, 64, roof, 0.98)                              # roof edge in the sun
    T.rect(48, roof + 1, 65, roof + 1, 0.86)
    # ---- bonnet and nose
    T.poly([(75, belt), (92, belt + 1), (96, belt + 4), (96, sill), (75, sill)], 0.78)
    T.rect(75, belt, 92, belt, 0.97)
    T.rect(76, belt + 1, 93, belt + 1, 0.88)
    for x in (80, 84, 88):
        T.rect(x, belt + 3, x + 2, belt + 3, 0.58)                # vents
    # shade the lower body, light the upper
    body = T.m.copy()
    grad = np.clip((yy - (belt + 4)) / float(sill - belt - 4), 0, 1)
    T.t = np.where(body & (yy > belt + 3), T.t - 0.16 * grad, T.t)
    # seams
    for x in (46, 57, 74):
        T.rect(x, belt + 3, x, sill - 1, 0.46)
    T.rect(60, belt + 6, 63, belt + 6, 0.36)                      # door handle
    T.rect(60, belt + 5, 63, belt + 5, 0.90)
    # the sill and what is under it
    T.rect(6, sill, 96, sill + 1, 0.30)
    L = T.layer(paint, dither=0.35, grain=0.04, seed=seed)

    # ---- glass
    G = Tone(W, H)
    G.poly([(50, roof + 3), (56, roof + 3), (56, belt - 1), (50, belt - 1)], 0.40)                 # quarter light
    G.poly([(58, roof + 3), (64, roof + 3), (71, belt - 1), (58, belt - 1)], 0.44)                 # door glass
    G.poly([(66, roof + 3), (67, roof + 3), (74, belt - 1), (73, belt - 1)], 0.62)                 # windscreen, edge on
    gl = G.m.copy()
    G.t = np.where(gl, G.t + 0.34 * np.clip(1 - ((xx - 58) + (yy - roof - 3) * 1.4) / 9.0, 0, 1) * (xx >= 58), G.t)   # a glare across the door glass
    L.paste(G.layer(GLASS, dither=0.3))

    # ---- arches
    for wx in (rx, fx):
        rr = np.sqrt((xx - wx) ** 2 + (yy - (g - WR)) ** 2)
        cut = (rr < 12.2) & (yy > g - 23)
        L.a &= ~cut
        flare = (rr >= 12.2) & (rr < 13.6) & (yy > g - 23) & (yy <= sill + 1) & L.a
        P.shade(L, flare, paint, -3)

    # ---- chrome and rubber: bumpers, bull bar, mirror, lamps
    C = Tone(W, H)
    C.rect(93, sill - 4, 101, sill - 1, 0.60)                     # front bumper
    C.rect(93, sill - 4, 101, sill - 4, 0.94)
    C.rect(2, sill - 3, 6, sill - 1, 0.50)                        # rear bumper
    C.rect(2, sill - 3, 6, sill - 3, 0.86)
    if livery == 'shass':
        C.rect(99, belt - 1, 100, sill - 1, 0.56)                 # bull bar
        C.rect(99, belt - 1, 99, sill - 1, 0.90)
        C.rect(96, belt - 1, 100, belt, 0.70)
        C.rect(96, belt + 6, 100, belt + 6, 0.66)
    C.rect(71, belt - 4, 73, belt - 1, 0.34)                      # mirror
    C.rect(94, belt + 6, 96, belt + 11, 0.22)                     # grille
    C.rect(94, belt + 7, 96, belt + 7, 0.50)
    C.rect(94, belt + 9, 96, belt + 9, 0.50)
    L.paste(C.layer(STEEL, dither=0.2))
    for (x, y, c) in ((93, belt + 3, (255, 236, 150)), (94, belt + 3, (255, 252, 230)), (93, belt + 4, (240, 200, 90)), (94, belt + 4, (255, 236, 150)),
                      (4, belt + 6, (226, 60, 40)), (5, belt + 6, (240, 96, 60)), (4, belt + 7, (170, 36, 24)), (5, belt + 7, (226, 60, 40))):
        _px(L, x, y, c)

    if livery == 'shass':
        # the three stripes every Shass on the coast road wears
        for i, c in enumerate(((232, 132, 60), (206, 60, 44), (244, 198, 60))):
            for x in range(6, 93):
                y = belt + 9 + i
                if L.a[y, x] and x not in (46, 57, 74):
                    L.rgb[y, x] = c
        # a low rack on the roof, and the lamps where they do not get in the gun's way: on the bar at the front
        R = Tone(W, H)
        R.rect(49, roof - 2, 65, roof - 2, 0.36)
        for x in (50, 57, 64):
            R.rect(x, roof - 2, x, roof - 1, 0.30)
        L.paste(R.layer(STEEL, dither=0.1))
        for y in (belt - 5, belt + 2):
            for dx in range(3):
                for dy in range(3):
                    _px(L, 98 + dx, y + dy, (255, 232, 120) if (dx + dy) % 2 == 0 or dy == 0 else (228, 180, 60))
            _px(L, 99, y + 1, (255, 252, 236))
        # tassels along the rail and under the rack
        for i, x in enumerate(range(7, 46, 3)):
            c = ((214, 72, 60), (76, 176, 96), (244, 198, 60))[i % 3]
            _px(L, x, belt + 4, c)
            if i % 2 == 0:
                _px(L, x, belt + 5, c)
        # aerial and pennant
        A = Tone(W, H)
        A.line([(90, belt), (86, belt - 22)], 0.30)
        L.paste(A.layer(STEEL, dither=0))
        for (dx, dy, c) in ((1, 0, (64, 144, 216)), (2, 0, (64, 144, 216)), (3, 1, (64, 144, 216)), (4, 1, (244, 198, 60)),
                            (1, 1, (64, 144, 216)), (2, 1, (244, 198, 60)), (1, 2, (64, 144, 216)), (2, 2, (64, 144, 216))):
            _px(L, 86 + dx, belt - 22 + dy, c)
        # a jerrycan and a rolled rug riding in the back, and the box Yazeed stands on
        J = Tone(W, H)
        J.rect(39, belt - 7, 44, belt, 0.50)
        J.rect(39, belt - 7, 44, belt - 7, 0.84)
        J.rect(40, belt - 9, 42, belt - 8, 0.40)
        J.rect(42, belt - 5, 42, belt - 2, 0.30)
        L.paste(J.layer(OLIVE, dither=0.2))
        for x in range(6, 10):
            for y in range(belt - 4, belt + 1):
                _px(L, x, y, (184, 60, 68) if (x + y) % 3 else (244, 198, 60))
    else:
        # rust at the arches and along the sill, and the Scorpion's mark on the door
        r = rng(seed + 5)
        rust = (fbm((H, W), seed + 7, 5, 3, octaves=3) > 0.60) & L.a & (yy > belt + 8) & (P.ramp_index(L.rgb, paint) >= 0)
        Rr = Tone(W, H)
        Rr.mask(rust, 0.5)
        Rr.t = np.where(rust, 0.36 + 0.3 * fbm((H, W), seed + 9, 2, 2), Rr.t)
        L.paste(Rr.layer(RUST, dither=0.5))
        for j, row in enumerate(P.SCORPION[:11]):
            for i, ch in enumerate(row):
                if ch == '#' and i < 11:
                    x, y = 59 + i, belt + 5 + j
                    if y < sill - 1 and L.a[y, x]:
                        L.rgb[y, x] = (230, 180, 40) if paint is not SANDP else (30, 22, 14)
    return L, cx, g


def driver(L, cx, g, who='salem'):
    """Put the man at the wheel: his head in the door glass. Salem's hat is too tall for the cab, so it has a hole in the roof."""
    belt, roof = g - 26, g - 41
    if who == 'salem':
        p = pal('white', 'cream', 'cream', 'skin3', **ms3.KUFIYA)
        im, fx, fy = head_image('salem', 'kufiya', p, wrap_dy=-1)
        hx, hy = 57, belt - 2 - im.height + 2
    else:
        p = ms3.militia_pal('skin2')
        im, fx, fy = head_image('angry', 'check', p, end='check_end')
        hx, hy = 57, belt - im.height + 3
    hl = from_image(im)
    # only what shows above the door: the body is behind it
    keep = np.zeros_like(hl.a)
    rows = np.arange(hl.h)[:, None] + hy
    keep[:] = rows < belt
    hl.a &= keep
    L.paste(hl, hx, hy)
    return L


def wheel_frames():
    """The wheel turning slowly (four frames) and at speed (two, smeared)."""
    out = []
    S = WR * 2 + 1
    yy, xx = np.mgrid[0:S, 0:S]
    c = WR
    rr = np.sqrt((xx - c) ** 2 + (yy - c) ** 2)
    ang = np.arctan2(yy - c, xx - c)
    disc = rr <= WR + 0.3
    for k in range(4):
        a0 = k * (math.pi / 3) / 4
        T = Tone(S, S)
        lug = (np.floor((ang + a0) / (math.pi / 3) * 2) % 2 == 0)
        t = np.where(rr > WR - 2.4, 0.26 + 0.34 * lug, 0.36)
        t = np.where((rr > WR - 2.4) & (yy < c - 3), t + 0.2, t)
        T.mask(disc, 0)
        T.t = np.where(disc, t, T.t)
        L = T.layer(RUBBER, dither=0.2)
        Hh = Tone(S, S)
        hub = rr <= WR - 3.6
        spoke = (np.floor((ang + a0 * 1.0) / (math.pi / 2.5) * 2) % 2 == 0)
        ht = 0.62 + 0.2 * spoke - 0.25 * np.clip((xx - c + yy - c) / 8.0, -0.4, 1)
        ht = np.where(rr <= 1.6, 0.30, ht)
        Hh.mask(hub, 0)
        Hh.t = np.where(hub, ht, Hh.t)
        L.paste(Hh.layer(STEEL, dither=0.3))
        out.append(('wheel%d' % k, P.outlined(L)))
    for k in range(2):
        T = Tone(S, S)
        t = np.where(rr > WR - 2.4, 0.40 + 0.08 * ((xx + yy + k) % 2), 0.36)
        t = np.where((rr > WR - 2.4) & (yy < c - 3), t + 0.18, t)
        T.mask(disc, 0)
        T.t = np.where(disc, t, T.t)
        L = T.layer(RUBBER, dither=0.3)
        Hh = Tone(S, S)
        hub = rr <= WR - 3.6
        ht = 0.66 - 0.22 * np.clip((xx - c + yy - c) / 8.0, -0.4, 1) + 0.06 * (((rr * 2).astype(int) + k) % 2)
        Hh.mask(hub, 0)
        Hh.t = np.where(hub, ht, Hh.t)
        L.paste(Hh.layer(STEEL, dither=0.4))
        out.append(('wheelf%d' % k, P.outlined(L)))
    return out


# ------------------------------------------------------------------ D. the MRAP
PLATE = ramp(['#0c0e10', '#1e2226', '#323a3e', '#4a5256', '#626a6c', '#7e8684', '#9aa09a'], 12)      # welded plate
SAND = SANDP
BOLT = (214, 218, 210)


def bolts(L, pts):
    for (x, y) in pts:
        if L.a[y, x]:
            L.rgb[y, x] = BOLT


# the maker's mark on the armoured truck's door: SAIF in heavy capitals, the A's left leg a green blade standing past
# the top of the word (after the badge Khaled sent, with our own word and a jambiya's point; the hero is Yazeed)
MARK_GLY = {
    'S': ['.####', '##...', '##...', '.###.', '...##', '...##', '####.'],
    'A': ['..##.', '.#.##', '.#.##', '#####', '##.##', '##.##', '##.##'],
    'I': ['##', '##', '##', '##', '##', '##', '##'],
    'F': ['#####', '##...', '##...', '####.', '##...', '##...', '##...'],
}
MARK_BLADE = [(2, -3), (2, -2), (1, -1), (2, -1), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2), (1, 2), (0, 3), (1, 3), (0, 4), (1, 4), (0, 5), (1, 5), (0, 6), (1, 6)]
MARK_SLATE, MARK_GREEN, MARK_GREEN_D = (46, 74, 86), (120, 180, 92), (84, 136, 64)


def badge(L, word, x0, y0):
    """The mark pressed onto L with its letters' top row at y0 (the blade rises three rows over it)."""
    x = x0
    for ch in word:
        g_ = MARK_GLY[ch]
        for j, row in enumerate(g_):
            for i, c in enumerate(row):
                if c == '#' and L.a[y0 + j, x + i]:
                    L.rgb[y0 + j, x + i] = MARK_SLATE
        if ch == 'A':
            for (i, j) in MARK_BLADE:
                if L.a[y0 + j, x + i]:
                    L.rgb[y0 + j, x + i] = MARK_GREEN_D if (i == 0 or j < -1) else MARK_GREEN
        x += len(g_[0]) + 1


def mrap(seed=6, mark=True):
    W, H = 106, 66
    g = H - 1
    cx = 52
    rx, fx = cx - WB // 2, cx + WB // 2
    belt, roof, sill = g - 26, g - 41, g - 11
    """A modern mine-protected 4x4 in desert tan, the shape of the one in Khaled's photo: a tall slab cab with small
    armoured windows in thick frames, a long faceted bonnet with the heavy grille and bumper, high ground clearance on
    big wheels, two whip aerials, and a gun ring on the roof behind the cab where Yazeed stands. No maker's badge."""
    T = Tone(W, H)
    yy, xx = np.mgrid[0:H, 0:W]
    top = roof - 4                 # taller than the pickup
    floor = sill - 2               # and higher off the road
    bon = belt - 5                 # the bonnet line
    # the hull: the crew box from the back to the cab, the bonnet ahead of it, the belly tucked in
    T.poly([(4, top + 2), (6, top), (70, top), (73, top + 3), (76, bon), (90, bon), (97, bon + 4), (99, bon + 10), (99, floor), (8, floor), (4, floor - 3)], 0.72)
    T.rect(6, top, 70, top, 0.98)
    T.rect(76, bon, 90, bon, 0.96)
    T.line([(70, top), (73, top + 3), (76, bon)], 0.92)
    # the bonnet's facets: a raised centre, the slope down to the grille
    T.rect(77, bon + 1, 95, bon + 1, 0.84)
    T.rect(77, bon + 4, 96, bon + 4, 0.52)
    # lower body darker, the upper lit
    grad = np.clip((yy - (belt + 1)) / float(floor - belt - 1), 0, 1)
    T.t = np.where(T.m & (yy > belt), T.t - 0.22 * grad, T.t)
    # the knuckle where the sides angle in
    T.rect(4, belt + 2, 99, belt + 2, 0.50)
    # the doors: a rear door and the cab door, with their seams
    for x in (28, 48, 74):
        T.rect(x, top + 2, x, floor - 1, 0.44)
    T.rect(30, belt + 6, 33, belt + 6, 0.36)                      # door handles
    T.rect(50, belt + 6, 53, belt + 6, 0.36)
    # the steps under the doors
    T.rect(30, floor + 1, 46, floor + 2, 0.40)
    T.rect(50, floor + 1, 66, floor + 2, 0.40)
    # the gun ring on the roof behind the cab: a low drum with a shield in front of it (Yazeed stands in it)
    T.poly([(20, top - 3), (44, top - 3), (44, top), (20, top)], 0.66)
    T.rect(20, top - 3, 44, top - 3, 0.9)
    L = T.layer(SAND, dither=0.35, grain=0.04, seed=seed)
    # the windows: small, square, in thick frames: the windscreen at the front of the cab, the door glass, a rear port
    G = Tone(W, H)
    G.poly([(63, top + 3), (70, top + 3), (74, bon - 1), (63, bon - 1)], 0.5)       # windscreen, edge on
    G.rect(50, top + 3, 61, top + 12, 0.44)                                        # door glass
    G.rect(36, top + 5, 42, top + 10, 0.4)                                         # the rear port
    gl = G.m.copy()
    G.t = np.where(gl, G.t + 0.3 * np.clip(1 - ((xx - 52) + (yy - top - 4) * 1.2) / 8.0, 0, 1) * (xx >= 52) * (xx <= 61), G.t)
    L.paste(G.layer(GLASS, dither=0.3))
    # thick frames round the glass
    Fr = Tone(W, H)
    for (x0, y0, x1, y1) in ((49, top + 2, 62, top + 13), (35, top + 4, 43, top + 11)):
        Fr.rect(x0, y0, x1, y0, 0.3); Fr.rect(x0, y1, x1, y1, 0.3); Fr.rect(x0, y0, x0, y1, 0.3); Fr.rect(x1, y0, x1, y1, 0.3)
    Fr.line([(63, top + 3), (73, bon - 1)], 0.3)
    L.paste(Fr.layer(PLATE, dither=0.1))
    bolts(L, [(x, top + 2) for x in range(8, 70, 6)] + [(x, floor - 2) for x in range(8, 98, 6)] + [(x, bon + 2) for x in range(78, 96, 6)])
    # the big arches, then the wheels' cut (the game's wheels, a size up would suit it)
    Mg = Tone(W, H)
    for wx in (rx, fx):
        Mg.poly([(wx - 18, floor), (wx - 16, floor - 11), (wx + 16, floor - 11), (wx + 18, floor)], 0.5)
        Mg.rect(wx - 16, floor - 11, wx + 16, floor - 11, 0.78)
    L.paste(Mg.layer(SAND, dither=0.4, seed=seed + 1))
    yy2, xx2 = np.mgrid[0:H, 0:W]
    for wx in (rx, fx):
        rr = np.sqrt((xx2 - wx) ** 2 + (yy2 - (g - WRB)) ** 2)
        cut = (rr < WRB + 2.6) & (yy2 > g - 26)
        L.a &= ~cut
    # the grille, the bumper with its lamps, the tow hooks; the rear bumper and lamps
    C = Tone(W, H)
    for y in range(bon + 6, belt + 2, 2):
        C.rect(93, y, 98, y, 0.22)
    C.rect(93, bon + 5, 98, bon + 5, 0.6)
    C.rect(92, belt + 4, 102, belt + 7, 0.46)                     # the bumper
    C.rect(92, belt + 4, 102, belt + 4, 0.86)
    C.rect(100, belt + 8, 101, belt + 10, 0.4)                    # tow hook
    C.rect(2, belt + 4, 5, belt + 7, 0.46)
    L.paste(C.layer(PLATE, dither=0.2))
    for (x, y, c) in ((93, bon + 3, (255, 236, 150)), (94, bon + 3, (255, 252, 230)), (96, belt + 1, (255, 236, 150)), (97, belt + 1, (255, 252, 230)),
                      (3, belt + 1, (226, 60, 40)), (4, belt + 1, (240, 96, 60))):
        _px(L, x, y, c)
    if mark:
        badge(L, 'SAIF', 11, top + 13)
    # the gun shield on the ring, a plate with a notch for the gun
    Gs = Tone(W, H)
    Gs.poly([(40, top - 13), (46, top - 13), (46, top - 3), (40, top - 3)], 0.56)
    Gs.rect(40, top - 13, 46, top - 13, 0.86)
    Gs.rect(44, top - 11, 46, top - 9, 0.2)
    L.paste(Gs.layer(PLATE, dither=0.25))
    # two whip aerials, the pennant on the front one
    A = Tone(W, H)
    A.line([(9, top), (7, top - 26)], 0.30)
    A.line([(84, bon), (81, bon - 24)], 0.30)
    L.paste(A.layer(STEEL, dither=0))
    for (dx, dy, c) in ((1, 0, (64, 144, 216)), (2, 0, (64, 144, 216)), (3, 1, (64, 144, 216)), (4, 1, (244, 198, 60)), (1, 1, (64, 144, 216)), (2, 1, (244, 198, 60)), (1, 2, (64, 144, 216)), (2, 2, (64, 144, 216))):
        _px(L, 81 + dx, bon - 24 + dy, c)
    # Salem at the wheel: his head in the door glass
    p = pal('white', 'cream', 'cream', 'skin3', **ms3.KUFIYA)
    im, fx_, fy_ = head_image('salem', 'kufiya', p, wrap_dy=-1)
    hl = from_image(im)
    hx, hy = 52, top + 12 - im.height + 1
    keep = np.zeros_like(hl.a)
    rows = np.arange(hl.h)[:, None] + hy
    cols = np.arange(hl.w)[None, :] + hx
    keep[:] = (rows >= top + 3) & (rows <= top + 12) & (cols >= 50) & (cols <= 61)
    hl.a &= keep
    L.paste(hl, hx, hy)
    return L

WRB = 11                      # the armoured car's wheels, a size up


def big_wheel_frames():
    """The armoured car's wheels: the same frames as wheel_frames, two pixels bigger, with deeper lugs."""
    global WR
    keep = WR
    WR = WRB
    try:
        out = [('b' + n, im) for n, im in wheel_frames()]
    finally:
        WR = keep
    return out


def truck_gun():
    """The heavy gun in the back of their pickups, on its post, behind its plate. It points left: at you."""
    W, H = 40, 30
    T = Tone(W, H)
    T.rect(22, 12, 23, H - 1, 0.36)                     # the post
    T.rect(22, 12, 22, H - 1, 0.66)
    T.poly([(18, H - 1), (27, H - 1), (25, H - 4), (20, H - 4)], 0.30)
    T.rect(4, 8, 30, 10, 0.44)                          # barrel and receiver
    T.rect(4, 8, 30, 8, 0.78)
    T.rect(0, 7, 5, 11, 0.34)                           # muzzle brake
    T.rect(0, 7, 5, 7, 0.60)
    T.rect(18, 6, 30, 12, 0.50)
    T.rect(18, 6, 30, 6, 0.84)
    T.rect(30, 9, 36, 10, 0.40)                         # spade grips
    T.rect(35, 7, 36, 12, 0.46)
    T.rect(20, 12, 26, 15, 0.42)                        # ammunition box
    T.rect(20, 12, 26, 12, 0.70)
    L = T.layer(STEEL, dither=0.25)
    S = Tone(W, H)
    S.poly([(13, 0), (17, 0), (17, 17), (13, 15)], 0.56)   # the plate
    S.rect(13, 0, 13, 15, 0.86)
    S.rect(14, 7, 16, 10, 0.20)                          # the slot the barrel goes through
    L.paste(S.layer(OLIVE, dither=0.3))
    T2 = Tone(W, H)
    T2.rect(4, 8, 16, 10, 0.44)
    T2.rect(4, 8, 16, 8, 0.78)
    L.paste(T2.layer(STEEL, dither=0.2))
    return P.outlined(L), 23, H


KD = {
    'x': '#16141a', 'D': '#2e2c36', 'd': '#4a4856', 'g': '#787684', 'G': '#a8a6b2', 'w': '#dcdce4',
    'O': '#56602c', 'o': '#7c8a44', 'Y': '#aab866', 'R': '#ff4030', 'r': '#a01c14', 'b': '#c8cce0', 'B': '#eef0ff',
}
KDRONE = [
    ['.bBBBBBBb......bBBBBBBb.',
     '....dd............dd....',
     '....dDdddddddddddDd....',
     '......dDDgGGgDDd.......',
     '......dDDDRDDDDd.......',
     '.......ddOoYodd........',
     '.........OoYo..........',
     '.........OoYo..........',
     '.........OOoo..........',
     '..........Oo...........',
     '.........o.O...........'],
    ['...bBBBb..........bBBBb.',
     '....dd............dd....',
     '....dDdddddddddddDd....',
     '......dDDgGGgDDd.......',
     '......dDDDrDDDDd.......',
     '.......ddOoYodd........',
     '.........OoYo..........',
     '.........OoYo..........',
     '.........OOoo..........',
     '..........Oo...........',
     '.........o.O...........'],
]


def kdrone(k):
    from px import sprite, outline
    im = sprite(KDRONE[k], KD)
    return outline(im, '#120e0a')


BBOMB = ['..x..', '.xOx.', '.OoY.', 'OOoYo', 'OOoYo', 'OOooo', '.Ooo.', '.xOx.', 'x.O.x']


def bbomb():
    from px import sprite, outline
    return outline(sprite(BBOMB, KD), '#120e0a')


# A road mine the player can see coming: a fat olive disc, a yellow-and-black band round its side, a red lamp on top
# that blinks, and a lighter ring of disturbed ground under it. Beside it stands a red flag (mine_flag).
RMINE_ROWS = [
    '.........RRR.........',
    '........xRWRx........',
    '.......xxdddxx.......',
    '....xxdoooooooodxx...',
    '..xdooYoooYoooYoodx..',
    '.xdooooooooooooooodx.',
    'xDYYxxYYxxYYxxYYxxYDx',
    'xDDDDDDDDDDDDDDDDDDDx',
    '.xxxxxxxxxxxxxxxxxxx.',
    'ss.sssssssssssssss.ss',
]
KDM = dict(KD, W='#fff4e0', s='#c8b48a')


def rmine(k):
    """k 0: the lamp lit, 1: the lamp dark."""
    from px import sprite, outline
    rows = [r.ljust(21, '.')[:21] for r in RMINE_ROWS]
    if k == 1:
        rows[0] = rows[0].replace('R', 'r')
        rows[1] = rows[1].replace('R', 'r').replace('W', 'r')
    im = sprite(rows, KDM)
    return outline(im, '#120e0a')


FLAG = [
    'xRRRRR...',
    'xRWWRRRR.',
    'xRRRRRRRR',
    'xrRRRRR..',
    'xrrr.....',
] + ['x........'] * 17


def mine_flag():
    """The militia mark their own mines, so as not to drive over them themselves: a red pennant on a stick."""
    from px import sprite, outline
    pal = dict(KD, W='#fff4e0', x='#5a3a1c')
    return outline(sprite(FLAG, pal), '#120e0a')


def boat():
    """The pride of the coast: a fishing huri on four rotor arms, a dish for a mast, a truck's horns on the bow, bombs slung
    along the keel. Returns (layer, x of its middle, y of its middle), and where things hang off it."""
    sk, f = P.skiff(length=78, paint=WHITE, stripe=P.BOATBLUE, seed=7, motor=False)
    W, H = 110, 58
    L = Layer(W, H)
    ox, oy = 4, 18
    L.paste(sk, ox, oy)
    yy, xx = np.mgrid[0:H, 0:W]
    T = Tone(W, H)
    # the arms the rotors stand on: two near, two far
    arms = [(26, 6, 0.50), (88, 4, 0.50), (40, 9, 0.34), (74, 8, 0.34)]
    for (ax, ay, t) in arms:
        base_y = oy + 15
        T.rect(ax, ay + 2, ax + 1, base_y, t)
        T.rect(ax, ay + 2, ax, base_y, t + 0.3)
        T.rect(ax - 2, ay, ax + 3, ay + 2, t - 0.1)       # motor
        T.rect(ax - 2, ay, ax + 3, ay, t + 0.34)
    # cross braces
    T.line([(27, 16), (40, 30)], 0.36)
    T.line([(88, 14), (75, 30)], 0.36)
    # the dish amidships, on a stub of mast
    T.rect(56, 12, 57, oy + 16, 0.36)
    T.rect(56, 12, 56, oy + 16, 0.70)
    e = ((xx - 57) / 9.0) ** 2 + ((yy - 9) / 6.5) ** 2
    m = e <= 1
    T.mask(m, 0)
    T.t = np.where(m, 0.88 - 0.5 * np.clip(((xx - 51) / 16.0) ** 2 + ((yy - 5) / 12.0) ** 2, 0, 1), T.t)
    T.t = np.where(m & (e > 0.78), 0.42, T.t)
    T.line([(57, 9), (66, 2)], 0.30)
    T.rect(65, 1, 67, 3, 0.50)
    # the gun mount under the bow
    T.rect(78, oy + 27, 82, oy + 30, 0.40)
    T.rect(78, oy + 27, 82, oy + 27, 0.70)
    L2 = T.layer(STEEL, dither=0.25)
    # the huri goes in front of its own far arms and mast, behind the near ones
    out = Layer(W, H)
    far = Layer(W, H)
    far.rgb, far.a = L2.rgb.copy(), L2.a & ((np.abs(xx - 40.5) < 4) | (np.abs(xx - 74.5) < 4) | ((np.abs(xx - 57) < 12) & (yy < oy + 14)))
    out.paste(far)
    out.paste(L)
    near = Layer(W, H)
    near.rgb, near.a = L2.rgb.copy(), L2.a & ~far.a
    out.paste(near)
    # horns on the bow
    Bz = Tone(W, H)
    for (hx, hy, ln) in ((84, oy + 6, 12), (84, oy + 10, 9)):
        for i in range(ln):
            half = 0.6 + i * 0.22
            for o in np.arange(-half, half + 0.5, 0.5):
                Bz.px(hx + i, hy + o - i * 0.25, 0.44 + 0.4 * (o < 0))
    out.paste(Bz.layer(BRASS, dither=0.2))
    # an eye on the bow, as the old boats have
    for (x, y, c) in ((78, oy + 14, (250, 246, 230)), (79, oy + 14, (250, 246, 230)), (80, oy + 14, (250, 246, 230)), (79, oy + 13, (250, 246, 230)), (79, oy + 15, (250, 246, 230)),
                      (79, oy + 14, (20, 16, 12))):
        _px(out, x, y, c)
    # tassels along the rail
    for i, x in enumerate(range(18, 84, 4)):
        c = ((214, 72, 60), (76, 176, 96), (244, 198, 60))[i % 3]
        y = oy + int(17 - 3 * math.sin((x - 16) / 70.0 * math.pi)) + 1
        if out.a[y, x]:
            _px(out, x, y + 0, c)
    # the Scorpion's pennant on the dish's feed
    for (x, y) in ((68, 0), (69, 0), (70, 1), (68, 1), (69, 1), (68, 2)):
        _px(out, x, y, (236, 190, 40))
    # bombs slung under the keel
    bb = from_image(bbomb())
    for bx in (30, 40, 50, 60):
        out.paste(bb, ox + bx, oy + 26)
    info = dict(rotors=[(26 + 1, 5), (88 + 1, 3), (40 + 1, 8), (74 + 1, 7)], gun=(80, oy + 30), mid=(55, oy + 20), bay=(50, oy + 30))
    return P.outlined(out), info


def rotor_frames():
    """A rotor at speed: a smear of light, seen edge on. Three frames so that it shimmers."""
    out = []
    from px import sprite
    pals = {'a': (232, 236, 248, 255), 'b': (190, 196, 216, 255), 'c': (150, 156, 180, 235), 'x': (40, 40, 52, 255)}
    rows = [
        ['.cbbaaaaaaaaaaaaxxaaaaaaaaaaaaabbc.', '..ccbbbbbbbbbbbbxxbbbbbbbbbbbbcc...'],
        ['......cbaaaaaaaaxxaaaaaaaaabc......', '........ccbbbbbbxxbbbbbbcc.........'],
        ['...cbbaaaaaaaaaaxxaaaaaaaaaaabbc...', '.....ccbbbbbbbbbxxbbbbbbbbbcc......'],
    ]
    for k, r in enumerate(rows):
        out.append(('rotor%d' % k, sprite(r, pals)))
    return out


def boss_gun():
    """The gun in the flying boat's chin. Points right; the game turns it."""
    T = Tone(18, 6)
    T.rect(0, 1, 6, 4, 0.46)
    T.rect(0, 1, 6, 1, 0.80)
    T.rect(6, 2, 17, 3, 0.40)
    T.rect(6, 2, 17, 2, 0.72)
    T.rect(15, 1, 17, 4, 0.34)
    return P.outlined(T.layer(STEEL, dither=0.2)), 3, 3


def camel():
    """A camel by the road, not interested."""
    W, H = 52, 44
    C = ramp(['#2a180a', '#4a2e14', '#6e4a22', '#8e6634', '#aa8246', '#c29a5c', '#d8b478'], 12)
    T = Tone(W, H)
    yy, xx = np.mgrid[0:H, 0:W]
    body = (((xx - 22) / 15.0) ** 2 + ((yy - 22) / 7.5) ** 2 <= 1)
    hump = (((xx - 22) / 7.0) ** 2 + ((yy - 14) / 6.0) ** 2 <= 1)
    T.mask(body | hump, 0.6)
    # neck up and forward, head
    for i in range(18):
        u = i / 17.0
        x = 34 + 8 * u + 2 * math.sin(u * 3.0)
        y = 20 - 15 * u
        T.rect(x - 2.2 + u, y - 1, x + 2.2 - u * 0.6, y + 1, 0.6)
    T.poly([(40, 3), (49, 4), (51, 7), (49, 9), (42, 9), (40, 7)], 0.62)
    T.rect(41, 1, 42, 3, 0.5)                              # ear
    # legs
    for (lx, t) in ((11, 0.46), (16, 0.6), (29, 0.46), (33, 0.6)):
        T.rect(lx, 26, lx + 2, H - 3, t)
        T.rect(lx - 1, H - 3, lx + 3, H - 1, t - 0.16)
    T.line([(8, 20), (4, 30)], 0.5)                        # tail
    T.rect(3, 30, 5, 32, 0.36)
    m = T.m.copy()
    lit = np.clip(1 - (yy - 8) / 26.0, 0, 1)
    T.t = np.where(m & (yy < 30), T.t + 0.22 * lit - 0.14 * np.clip((xx - 26) / 30.0, 0, 1) + 0.06 * (fbm((H, W), 3, 3, 2) - 0.5), T.t)
    L = T.layer(C, dither=0.4)
    _px(L, 46, 5, (20, 14, 10))
    _px(L, 50, 8, (60, 36, 20))
    # a striped blanket over the hump
    for x in range(15, 30):
        for y in range(13, 22):
            if L.a[y, x] and (x - 15) % 5 in (0, 1):
                L.rgb[y, x] = (176, 52, 44) if (x - 15) % 5 == 0 else (236, 190, 60)
    return L, 22, H - 1


def sign(kind):
    """Things on posts beside the road."""
    W, H = 30, 50
    T = Tone(W, H)
    T.rect(14, 16, 15, H - 1, 0.40)
    T.rect(14, 16, 14, H - 1, 0.72)
    L = T.layer(STEEL, dither=0.1)
    yy, xx = np.mgrid[0:H, 0:W]
    if kind == 'camel':
        # a warning triangle with a camel on it, well shot at
        tri = (yy >= 2) & (yy <= 22) & (np.abs(xx - 14.5) <= (yy - 1) * 0.62 + 0.5)
        inner = (yy >= 6) & (yy <= 20) & (np.abs(xx - 14.5) <= (yy - 5) * 0.62 - 1.5)
        Rr = Tone(W, H)
        Rr.mask(tri, 0.66)
        L.paste(Rr.layer(P.REDP, dither=0.2))
        Wt = Tone(W, H)
        Wt.mask(inner, 0.86)
        L.paste(Wt.layer(WHITE, dither=0.2))
        cam = ['....#..', '...##..', '.#.#...', '####...', '####...', '#..#...']
        for j, row in enumerate(cam):
            for i, ch in enumerate(row):
                if ch == '#':
                    _px(L, 11 + i, 13 + j, (24, 18, 12))
        for (x, y) in ((12, 9), (17, 17), (15, 11)):
            _px(L, x, y, (40, 40, 48))
    elif kind == 'stop':
        Bd = Tone(W, H)
        Bd.rect(6, 2, 23, 17, 0.84)
        Bd.rect(6, 2, 23, 2, 0.98)
        Bd.rect(23, 2, 23, 17, 0.6)
        L.paste(Bd.layer(WHITE, dither=0.2))
        hand = ['..#.#.#...', '..#.#.#.#.', '..#.#.#.#.', '#.#####.#.', '#########.', '.########.', '..######..', '...####...']
        for j, row in enumerate(hand):
            for i, ch in enumerate(row):
                if ch == '#':
                    _px(L, 10 + i, 6 + j, (190, 52, 24))
    elif kind == 'end':
        # the tarmac starts here: a blue board with an arrow
        Bd = Tone(W, H)
        Bd.rect(4, 3, 25, 15, 0.56)
        Bd.rect(4, 3, 25, 3, 0.86)
        L.paste(Bd.layer(P.BOATBLUE, dither=0.2))
        for (x0, x1, y) in ((8, 19, 9), (17, 20, 8), (17, 20, 10), (18, 21, 9), (16, 18, 7), (16, 18, 11)):
            for x in range(x0, x1 + 1):
                _px(L, x, y, (244, 246, 236))
    else:
        # the battery's own notice: the mark, and nothing friendly
        Bd = Tone(W, H)
        Bd.rect(4, 1, 25, 19, 0.70)
        Bd.rect(4, 1, 25, 1, 0.92)
        L.paste(Bd.layer(P.FLAGY, dither=0.2))
        for j, row in enumerate(P.SCORPION):
            for i, ch in enumerate(row):
                if ch == '#':
                    _px(L, 9 + i, 4 + j, (22, 16, 10))
    return L, 14, H - 1


def stone():
    """A kilometre stone, white with a yellow cap."""
    W, H = 10, 13
    T = Tone(W, H)
    T.rect(1, 3, 8, H - 1, 0.80)
    T.rect(1, 3, 2, H - 1, 0.94)
    T.rect(8, 3, 8, H - 1, 0.56)
    L = T.layer(WHITE, dither=0.2)
    Y = Tone(W, H)
    Y.rect(1, 0, 8, 3, 0.7)
    Y.rect(2, 0, 7, 0, 0.94)
    L.paste(Y.layer(P.FLAGY, dither=0.2))
    for (x, y) in ((3, 6), (4, 6), (5, 6), (5, 7), (4, 8), (3, 8), (3, 9), (4, 10), (5, 10), (3, 10)):
        _px(L, x, y, (30, 26, 22))
    return L, 5, H - 1


def launcher_wreck():
    """What is left of the launcher once the flying boat has landed on it."""
    ml, f = P.missile_launcher()
    W, H = ml.w + 20, ml.h
    L = Layer(W, H)
    L.paste(ml, 6, 0)
    yy, xx = np.mgrid[0:H, 0:W]
    # the rail and its missile are gone above a ragged line; what is left is burnt black
    n = noise((1, W), 5, 5, 0.5)[0]
    line = 30 + 10 * (n - 0.5) * 2 + 0.16 * (xx[0] - 30)
    L.a &= yy >= line[None, :]
    for rmp in (P.OLIVE, P.MISSILE, P.REDP, P.TYRE):
        P.shade(L, L.a, rmp, -4)
    # the boat's bow, stove in, standing in the wreckage
    sk, sf = P.skiff(length=44, paint=WHITE, stripe=P.BOATBLUE, seed=9, motor=False)
    sk2 = P.tilt(sk, -38)
    for rmp in (WHITE, P.BOATBLUE, P.DRIFT):
        P.shade(sk2, sk2.a, rmp, -3)
    L2 = Layer(W, H)
    L2.paste(sk2, 30, H - sk2.h + 10)
    L2.a &= yy < H - 1
    L.paste(L2)
    return P.outlined(L), f


def sheet(path, zoom=4):
    items = []
    for name, paint, liv, who in (('shass', WHITE, 'shass', 'salem'), ('truck_olive', OLIVE, 'militia', 'grunt'), ('truck_sand', SANDP, 'militia', 'grunt')):
        L, cx, g = pickup(paint, liv, seed=3 if liv == 'shass' else 5)
        driver(L, cx, g, who)
        items.append((name, P.outlined(L).image()))
    for n, im in wheel_frames():
        items.append((n, im.image()))
    tg, ax, ay = truck_gun()
    items.append(('truck_gun', tg.image()))
    for k in range(2):
        items.append(('kdrone%d' % k, kdrone(k)))
        items.append(('rmine%d' % k, rmine(k)))
    items.append(('bbomb', bbomb()))
    b, info = boat()
    items.append(('boat', b.image()))
    for n, im in rotor_frames():
        items.append((n, im))
    bg, _, _ = boss_gun()
    items.append(('boss_gun', bg.image()))
    c, _, _ = camel()
    items.append(('camel', c.image()))
    for k in ('camel', 'stop', 'end', 'battery'):
        s_, _, _ = sign(k)
        items.append(('sign_' + k, s_.image()))
    st, _, _ = stone()
    items.append(('stone', st.image()))
    lw, _ = launcher_wreck()
    items.append(('launcher_wreck', lw.image()))
    ml, _ = P.missile_launcher()
    items.append(('launcher', ml.image()))
    Wd = 560
    x = y = rowh = 4
    place = []
    for n, im in items:
        if x + im.width + 6 > Wd:
            x = 4
            y += rowh + 8
            rowh = 0
        place.append((n, im, x, y))
        x += im.width + 8
        rowh = max(rowh, im.height)
    Ht = y + rowh + 6
    sh = Image.new('RGBA', (Wd, Ht), (222, 190, 120, 255))
    for n, im, x, y in place:
        sh.alpha_composite(im, (x, y))
    sh = sh.resize((Wd * zoom, Ht * zoom), Image.NEAREST)
    sh.save(path)
    return sh.size, info


if __name__ == '__main__':
    print(sheet(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work', 'vehicles.png'), zoom=3))
