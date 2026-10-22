# armour_concepts.py - three ways Salem's pickup on the coast road could be an armoured vehicle, drawn at the pickup's
# own scale (106 x 66, wheelbase 58, wheels r 9) and anchor, so Yazeed stands where he stands, Salem's head shows where
# it shows, the gun fires over the cab and the ram bar is where the bull bar is. Proposals only; nothing in the game
# changes.
#   A  Plated Shass: the same white pickup with steel welded over it
#   B  Tin Can: a homemade armoured box on the pickup's chassis
#   C  Grandfather: an old scout car, captured and painted up
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock')
import numpy as np
from PIL import Image, ImageDraw
from paint import *
import props as P
import vehicles as V
from vehicles import WB, WR, WHITE, STEEL, RUST, GLASS, SANDP, OLIVE, _px, driver

W, H = 106, 66
g = H - 1
cx = 52
rx, fx = cx - WB // 2, cx + WB // 2
belt, roof, sill = g - 26, g - 41, g - 11
PLATE = ramp(['#0c0e10', '#1e2226', '#323a3e', '#4a5256', '#626a6c', '#7e8684', '#9aa09a'], 12)      # welded plate, duller than chrome
SAND = SANDP
BOLT = (214, 218, 210)


def stripes(L, x0, x1, y0, skip=()):
    for i, c in enumerate(((232, 132, 60), (206, 60, 44), (244, 198, 60))):
        for x in range(x0, x1):
            y = y0 + i
            if 0 <= y < H and L.a[y, x] and x not in skip:
                L.rgb[y, x] = c


def bolts(L, pts):
    for (x, y) in pts:
        if L.a[y, x]:
            L.rgb[y, x] = BOLT


def arches(L, paint):
    yy, xx = np.mgrid[0:H, 0:W]
    for wx in (rx, fx):
        rr = np.sqrt((xx - wx) ** 2 + (yy - (g - WR)) ** 2)
        cut = (rr < 12.2) & (yy > g - 23)
        L.a &= ~cut
        flare = (rr >= 12.2) & (rr < 13.6) & (yy > g - 23) & (yy <= sill + 1) & L.a
        P.shade(L, flare, paint, -3)


# ------------------------------------------------------------------ A. the plated Shass
def plated(seed=3):
    """Salem's own pickup with steel plates welded over the doors, the bonnet and the bed sides, a slit visor over the
    windscreen, sandbags along the rail and a heavier ram bar: the stripes and the tassels still show between the plates."""
    L, _, _ = V.pickup(WHITE, 'shass', seed=seed)
    Pl = Tone(W, H)
    # bed sides: a plate hung outside the bed, bolted at the corners, the rail and the tassels showing above it
    Pl.poly([(6, belt + 6), (45, belt + 6), (45, sill - 1), (6, sill - 1)], 0.58)
    Pl.rect(6, belt + 6, 45, belt + 6, 0.80)
    # the doors: a plate with a cut-out for the glass, down to the sill
    Pl.poly([(47, belt + 1), (74, belt + 1), (74, sill - 1), (47, sill - 1)], 0.62)
    Pl.rect(47, belt + 1, 74, belt + 1, 0.82)
    # the bonnet plate, sloped
    Pl.poly([(76, belt - 1), (92, belt), (95, belt + 3), (95, belt + 8), (76, belt + 8)], 0.60)
    Pl.rect(76, belt - 1, 92, belt - 1, 0.86)
    # a visor over the windscreen: a plate with a slit
    Pl.poly([(64, roof + 2), (67, roof + 2), (75, belt - 1), (72, belt - 1)], 0.66)
    for (x0, x1, y) in ((6, 45, sill - 1), (47, 74, sill - 1), (76, 95, belt + 8)):
        Pl.rect(x0, y, x1, y, 0.22)
    L.paste(Pl.layer(PLATE, dither=0.3, grain=0.05, seed=seed))
    # the slit, and the glass behind it
    for y in range(roof + 7, roof + 9):
        for x in range(66, 72):
            _px(L, x + (y - roof - 7), y, (20, 40, 56))
    bolts(L, [(8, belt + 8), (43, belt + 8), (8, sill - 3), (43, sill - 3), (49, belt + 3), (72, belt + 3), (49, sill - 3), (72, sill - 3), (78, belt + 1), (90, belt + 1), (78, belt + 7), (90, belt + 7)])
    stripes(L, 8, 44, belt + 10)
    stripes(L, 49, 73, belt + 10)
    # rust bleeding from the welds
    Rr = Tone(W, H)
    for (x0, x1, y) in ((6, 45, sill - 1), (47, 74, sill - 1)):
        for x in range(x0, x1, 3):
            Rr.px(x, y, 0.45)
            Rr.px(x, y - 1, 0.35)
    L.paste(Rr.layer(RUST, dither=0.4))
    # sandbags along the bed rail, in front of where Yazeed stands
    Sb = Tone(W, H)
    for i, x in enumerate(range(8, 44, 7)):
        Sb.poly([(x, belt - 3), (x + 6, belt - 3), (x + 7, belt), (x - 1, belt)], 0.62 - 0.08 * (i % 2))
        Sb.rect(x + 1, belt - 3, x + 5, belt - 3, 0.84)
    L.paste(Sb.layer(SAND, dither=0.4, seed=seed))
    # the ram bar: a heavier welded frame on the front, where the bull bar was
    Rb = Tone(W, H)
    Rb.rect(98, belt - 3, 102, sill - 1, 0.50)
    Rb.rect(98, belt - 3, 98, sill - 1, 0.84)
    for y in (belt - 3, belt + 4, belt + 11):
        Rb.rect(95, y, 102, y + 1, 0.66)
    L.paste(Rb.layer(PLATE, dither=0.2))
    driver(L, cx, g, 'salem')
    return L


# ------------------------------------------------------------------ B. the Tin Can
def tincan(seed=4):
    """A box of plate welded onto the pickup's chassis in somebody's yard: slab sides angled in at the top, a slit for the
    driver, a V-shaped ram plate on the nose, the open back with a gun shield for Yazeed. Olive, with the three stripes
    painted on by hand and the mirror kept."""
    T = Tone(W, H)
    yy, xx = np.mgrid[0:H, 0:W]
    top = roof + 4
    # the hull: one slab from the tailgate to the nose, the top edge angled in
    T.poly([(4, belt - 2), (6, belt - 6), (46, belt - 6), (49, top), (70, top), (80, belt - 4), (92, belt - 2), (97, belt + 3), (97, sill), (4, sill)], 0.70)
    T.rect(49, top, 70, top, 0.98)
    T.rect(6, belt - 6, 46, belt - 6, 0.92)
    # the angled plates read as facets: the upper band lighter
    band = (yy >= belt - 6) & (yy <= belt + 1)
    T.t = np.where(T.m & band, T.t + 0.18, T.t)
    cab = (yy < belt - 6) & (xx >= 48) & (xx <= 80)
    T.t = np.where(T.m & cab, T.t + 0.06, T.t)
    grad = np.clip((yy - (belt + 2)) / float(sill - belt - 2), 0, 1)
    T.t = np.where(T.m & (yy > belt + 1), T.t - 0.26 * grad, T.t)
    T.rect(48, top + 1, 48, belt - 6, 0.40)                       # the cab's front and back edges
    T.rect(71, top + 1, 71, belt - 6, 0.40)
    # the open back: a lower wall where Yazeed stands (his legs show over it)
    T.poly([(6, belt - 6), (46, belt - 6), (46, belt - 2), (6, belt - 2)], 0.76)
    # plate seams and the welds
    for x in (24, 46, 62, 80):
        T.rect(x, belt - 5, x, sill - 1, 0.44)
    T.rect(4, belt + 2, 97, belt + 2, 0.50)
    L = T.layer(OLIVE, dither=0.35, grain=0.04, seed=seed)
    bolts(L, [(x, belt - 3) for x in range(8, 46, 6)] + [(x, sill - 3) for x in range(8, 96, 6)] + [(x, belt + 4) for x in range(50, 96, 6)])
    # the driver's slit, with the glass behind it
    for x in range(52, 66):
        _px(L, x, top + 4, (18, 36, 52))
        _px(L, x, top + 5, (34, 66, 90) if x % 3 else (18, 36, 52))
    # the ram plate: a V on the nose, with teeth
    Rp = Tone(W, H)
    Rp.poly([(96, belt - 1), (103, belt + 6), (103, belt + 9), (96, sill - 1), (94, sill - 1), (94, belt - 1)], 0.56)
    Rp.line([(96, belt - 1), (103, belt + 6)], 0.9)
    for y in range(belt + 1, sill - 2, 4):
        Rp.rect(93, y, 94, y, 0.9)
    L.paste(Rp.layer(PLATE, dither=0.2))
    # the gun shield in the back: a plate with a notch, where the gun fires over the cab
    Gs = Tone(W, H)
    Gs.poly([(40, belt - 16), (47, belt - 16), (47, belt - 6), (40, belt - 6)], 0.58)
    Gs.rect(40, belt - 16, 47, belt - 16, 0.86)
    Gs.rect(44, belt - 13, 47, belt - 11, 0.2)
    L.paste(Gs.layer(PLATE, dither=0.25))
    # the stripes, painted on by hand (wobbly)
    for i, c in enumerate(((232, 132, 60), (206, 60, 44), (244, 198, 60))):
        for x in range(8, 92):
            y = belt + 9 + i + (1 if (x // 11) % 3 == 1 else 0)
            if L.a[y, x] and x not in (24, 46, 62, 80):
                L.rgb[y, x] = c
    arches(L, OLIVE)
    # bumpers, mirror, lamps in cages
    C = Tone(W, H)
    C.rect(2, sill - 3, 5, sill - 1, 0.5)
    C.rect(70, belt - 8, 72, belt - 5, 0.34)                      # the mirror, on a stalk
    C.rect(72, belt - 5, 72, belt - 3, 0.3)
    L.paste(C.layer(STEEL, dither=0.2))
    for (x, y) in ((91, belt + 4), (91, belt + 5)):
        _px(L, x, y, (255, 236, 150)); _px(L, x + 1, y, (255, 252, 230))
    for (x, y) in ((5, belt + 5), (5, belt + 6)):
        _px(L, x, y, (226, 60, 40))
    # aerial and pennant, as on the Shass
    A = Tone(W, H)
    A.line([(88, belt - 2), (84, belt - 24)], 0.30)
    L.paste(A.layer(STEEL, dither=0))
    for (dx, dy, c) in ((1, 0, (64, 144, 216)), (2, 0, (64, 144, 216)), (3, 1, (64, 144, 216)), (4, 1, (244, 198, 60)), (1, 1, (64, 144, 216)), (2, 1, (244, 198, 60)), (1, 2, (64, 144, 216)), (2, 2, (64, 144, 216))):
        _px(L, 84 + dx, belt - 24 + dy, c)
    # Salem's head out of a roof hatch (the hatch lid up behind him)
    Hl = Tone(W, H)
    Hl.poly([(50, top - 1), (60, top - 1), (60, top), (50, top)], 0.7)
    Hl.poly([(60, top - 12), (62, top - 12), (62, top), (60, top)], 0.6)            # the lid, open
    L.paste(Hl.layer(OLIVE, dither=0.3))
    driver_hatch(L, 56, top)
    return L


def driver_hatch(L, hx, top):
    """Salem's head and shoulders out of a hatch at (hx, top)."""
    p = V.pal('white', 'cream', 'cream', 'skin3', **V.ms3.KUFIYA)
    im, fx_, fy_ = V.head_image('salem', 'kufiya', p, wrap_dy=-1)
    hl = from_image(im)
    hy = top - im.height + 4
    keep = np.zeros_like(hl.a)
    rows = np.arange(hl.h)[:, None] + hy
    keep[:] = rows < top + 1
    hl.a &= keep
    L.paste(hl, hx, hy)


# ------------------------------------------------------------------ C. the Grandfather
def scoutcar(seed=5):
    """An old wheeled scout car out of some 1960s war, captured from the Scorpion and painted up: a boat-shaped hull
    with a sloped nose, big mudguards, the driver's hatch up front with Salem's head out of it, the open commander's
    hatch behind where Yazeed stands. Faded sand with rust, the three stripes painted on, the pennant on its aerial."""
    T = Tone(W, H)
    yy, xx = np.mgrid[0:H, 0:W]
    deck = belt - 5
    # the hull: a boat, the sides sloping in at the top and tucked in at the bottom
    T.poly([(3, deck + 4), (8, deck), (62, deck), (72, deck - 2), (90, deck), (101, belt + 4), (103, belt + 10), (100, sill), (6, sill), (3, sill - 4)], 0.70)
    T.rect(8, deck, 62, deck, 0.96)
    T.line([(62, deck), (72, deck - 2), (90, deck)], 0.96)
    # the upper slope lit, the lower tucked
    up = (yy >= deck) & (yy <= belt + 2)
    T.t = np.where(T.m & up, T.t + 0.1, T.t)
    grad = np.clip((yy - (belt + 3)) / float(sill - belt - 3), 0, 1)
    T.t = np.where(T.m & (yy > belt + 2), T.t - 0.2 * grad, T.t)
    # the knuckle line where the slope breaks
    T.rect(4, belt + 3, 101, belt + 3, 0.50)
    # the driver's cabin up front: a low turret with the hatch, the vision block
    T.poly([(64, deck - 7), (84, deck - 7), (88, deck), (62, deck)], 0.74)
    T.rect(64, deck - 7, 84, deck - 7, 0.96)
    # the commander's hatch ring behind, where Yazeed stands
    T.poly([(14, deck - 3), (44, deck - 3), (44, deck), (14, deck)], 0.66)
    T.rect(14, deck - 3, 44, deck - 3, 0.9)
    # the engine deck grilles at the back, the stowage bin
    for y in range(deck + 2, deck + 8, 2):
        T.rect(5, y, 12, y, 0.46)
    T.rect(22, belt + 5, 40, belt + 12, 0.6)
    T.rect(22, belt + 5, 40, belt + 5, 0.82)
    L = T.layer(SAND, dither=0.4, grain=0.05, seed=seed)
    # the vision block, dark glass
    for x in range(72, 84):
        _px(L, x, deck - 4, (18, 36, 52)); _px(L, x, deck - 3, (34, 66, 90) if x % 2 else (18, 36, 52))
    # rust where the paint has gone
    rust = (fbm((H, W), seed + 7, 5, 3, octaves=3) > 0.62) & L.a & (yy > belt + 4)
    Rr = Tone(W, H)
    Rr.mask(rust, 0.5)
    Rr.t = np.where(rust, 0.36 + 0.3 * fbm((H, W), seed + 9, 2, 2), Rr.t)
    L.paste(Rr.layer(RUST, dither=0.5))
    bolts(L, [(x, belt + 1) for x in range(6, 100, 8)] + [(x, sill - 3) for x in range(8, 100, 8)])
    # the stripes, painted on over the sand
    stripes(L, 6, 98, belt + 7)
    # big mudguards over the wheels, then the arches cut
    Mg = Tone(W, H)
    for wx in (rx, fx):
        Mg.poly([(wx - 16, sill), (wx - 14, sill - 6), (wx + 14, sill - 6), (wx + 16, sill)], 0.5)
        Mg.rect(wx - 14, sill - 6, wx + 14, sill - 6, 0.78)
    L.paste(Mg.layer(SAND, dither=0.4, seed=seed + 1))
    arches(L, SAND)
    # the sloped nose plate with a tow hook and the lamps in their cages; a spare wheel? no: a jerrycan on the back
    C = Tone(W, H)
    C.rect(100, belt + 6, 103, belt + 7, 0.6)                                     # tow hook
    C.rect(2, belt + 9, 4, sill - 1, 0.5)                                         # rear step
    C.rect(93, belt - 1, 95, belt + 1, 0.3)                                       # a lamp cage
    L.paste(C.layer(STEEL, dither=0.2))
    _px(L, 94, belt, (255, 236, 150))
    J = Tone(W, H)
    J.rect(6, deck - 6, 11, deck + 1, 0.5)
    J.rect(6, deck - 6, 11, deck - 6, 0.84)
    L.paste(J.layer(OLIVE, dither=0.2))
    # aerial and pennant
    A = Tone(W, H)
    A.line([(90, deck), (86, deck - 22)], 0.30)
    L.paste(A.layer(STEEL, dither=0))
    for (dx, dy, c) in ((1, 0, (64, 144, 216)), (2, 0, (64, 144, 216)), (3, 1, (64, 144, 216)), (4, 1, (244, 198, 60)), (1, 1, (64, 144, 216)), (2, 1, (244, 198, 60)), (1, 2, (64, 144, 216)), (2, 2, (64, 144, 216))):
        _px(L, 86 + dx, deck - 22 + dy, c)
    # Salem's head out of the driver's hatch, the lid up behind him
    Hl = Tone(W, H)
    Hl.poly([(80, deck - 18), (82, deck - 18), (82, deck - 7), (80, deck - 7)], 0.6)
    L.paste(Hl.layer(SAND, dither=0.3))
    driver_hatch(L, 70, deck - 7)
    return L


# ------------------------------------------------------------------ D. the MRAP
def mrap(seed=6):
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
    T.poly([(20, top - 5), (44, top - 5), (44, top), (20, top)], 0.66)
    T.rect(20, top - 5, 44, top - 5, 0.9)
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
        Mg.poly([(wx - 17, floor), (wx - 15, floor - 9), (wx + 15, floor - 9), (wx + 17, floor)], 0.5)
        Mg.rect(wx - 15, floor - 9, wx + 15, floor - 9, 0.78)
    L.paste(Mg.layer(SAND, dither=0.4, seed=seed + 1))
    yy2, xx2 = np.mgrid[0:H, 0:W]
    for wx in (rx, fx):
        rr = np.sqrt((xx2 - wx) ** 2 + (yy2 - (g - WR)) ** 2)
        cut = (rr < 13.2) & (yy2 > g - 24)
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
    # the gun shield on the ring, a plate with a notch for the gun
    Gs = Tone(W, H)
    Gs.poly([(40, top - 14), (46, top - 14), (46, top - 5), (40, top - 5)], 0.56)
    Gs.rect(40, top - 14, 46, top - 14, 0.86)
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
    p = V.pal('white', 'cream', 'cream', 'skin3', **V.ms3.KUFIYA)
    im, fx_, fy_ = V.head_image('salem', 'kufiya', p, wrap_dy=-1)
    hl = from_image(im)
    hx, hy = 52, top + 12 - im.height + 1
    keep = np.zeros_like(hl.a)
    rows = np.arange(hl.h)[:, None] + hy
    cols = np.arange(hl.w)[None, :] + hx
    keep[:] = (rows >= top + 3) & (rows <= top + 12) & (cols >= 50) & (cols <= 61)
    hl.a &= keep
    L.paste(hl, hx, hy)
    return L


CONCEPTS = {'A': plated, 'B': tincan, 'C': scoutcar, 'D': mrap}
NAMES = {'A': 'The plated Shass', 'B': 'The Tin Can', 'C': 'The Grandfather', 'D': 'The Desert Truck'}

# ------------------------------------------------------------------ staging: today's sprite and the concepts on the road
GAME = os.path.dirname(HERE)
_ATLAS = None


def frame(name):
    global _ATLAS
    if _ATLAS is None:
        import json
        _ATLAS = (Image.open(os.path.join(GAME, 'art/out/atlas.png')).convert('RGBA'), json.load(open(os.path.join(GAME, 'gen/atlas.json')))['frames'])
    sheet, frames = _ATLAS
    x, y, w, h, ax, ay = frames[name]
    return sheet.crop((x, y, x + w, y + h)), ax, ay


def body_image(key):
    if key is None:
        return frame('shass')
    L = CONCEPTS[key]()
    im = P.outlined(L).image()
    return im, cx + 1, g + 1


def on_road(key, w=180, h=100, k=4, bg=(16, 20, 44, 255)):
    """The car with Yazeed in the back and Salem at the wheel, on a strip of tarmac, the way drawCar stacks it."""
    out = Image.new('RGBA', (w, h), bg)
    d = ImageDraw.Draw(out)
    gy = h - 14
    d.rectangle((0, gy, w, h), fill=(48, 44, 48, 255))
    d.rectangle((0, gy, w, gy), fill=(70, 66, 70, 255))
    for x in range(4, w, 24):
        d.rectangle((x, gy + 7, x + 12, gy + 7), fill=(226, 200, 120, 255))
    ox, oy = w // 2, gy - 10                                # drawCar's origin: (c.x, c.y - 10)
    yazeed, sax, say = frame('yazeed_stand_hmg_fwd')
    body, bax, bay = body_image(key)
    wheel, wax, way = frame('wheel0')
    BED, STAND, WR_ = -22, (39 if key == 'D' else 23), 29     # (on the MRAP he stands up in the roof ring)
    out.alpha_composite(yazeed, (ox + BED - sax, oy + 10 - STAND - say))
    out.alpha_composite(body, (ox - bax, oy + 10 - bay))
    out.alpha_composite(wheel, (ox - WR_ - wax, oy + 1 - way))
    out.alpha_composite(wheel, (ox + WR_ - wax, oy + 1 - way))
    return out.resize((w * k, h * k), Image.NEAREST)


if __name__ == '__main__':
    OUT = os.path.join(os.path.dirname(GAME), 'boss_proposals')
    on_road(None).save(os.path.join(OUT, 'car_today.png'))
    for key in CONCEPTS:
        on_road(key).save(os.path.join(OUT, 'car_%s.png' % key))
    cmp_ = Image.new('RGBA', (720, 400 * 2), (16, 20, 44, 255))
    for i, key in enumerate([None, 'D']):
        cmp_.paste(Image.open(os.path.join(OUT, 'car_%s.png' % (key or 'today'))), (0, i * 400))
    cmp_.save(os.path.join(OUT, 'car_cmp.png'))
    print('ok')
