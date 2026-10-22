# mocha_sprites.py - the sprites The Coffee Port adds: the cook (a heavy man of the Scorpion's with a pot for a helmet
# and a ladle), the quartermaster who drives the Big Roaster, the Big Roaster itself in parts, the steam vents, the
# sacks that men hide behind, and the beans that fly about. Built the same way as sprites.py: the cast's parts, outlined.
# Every frame is (image, ax, ay): the anchor is the point between the feet, on the ground, unless it says otherwise.
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock'
sys.path.insert(0, MOCK)
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image
import ms3
from ms3 import at, weapon, compose, pal, PARTS, WEAPONS, WRAPS, FACES, HEAVY, INK2
import sprites as SP
import px
from px import new, blit, sprite, outline, silhouette
import props as P
from paint import Layer, Tone, ramp, toned, rng, noise, fbm
import stage_mocha as SM

LEGH = PARTS['legs_h']
LEGH_FAR = [r[0:9] for r in LEGH]
LEGH_NEAR = [r[13:22] for r in LEGH]
LADLE = WEAPONS['ladle']


def _ladle(turn):
    """The ladle's rows and where the hand holds it, turned: 0 as drawn (bowl up and forward), 1 a quarter turn back
    (bowl up over the shoulder), -1 a quarter turn forward (bowl out and down)."""
    rows, g = LADLE['rows'], LADLE['grip']
    w, h = max(len(r) for r in rows), len(rows)
    if turn == 1:
        return SP.rot_ccw(rows), (g[1], w - 1 - g[0])
    if turn == -1:
        return SP.rot_cw(rows), (h - 1 - g[1], g[0])
    return rows, g


def cook(pose='stand', act='hold', skin='skin2'):
    """The cook. act: hold (ladle up at the ready), scoop (drawn back over the shoulder, full of hot beans), fling (out
    in front, empty), raise (high over his head), swing (brought down in front of him), up (hands up), flung (hit)."""
    p = dict(ms3.militia_pal(skin))
    p['L'] = '#6c3818'                                # (the stains on his apron are coffee)
    B = HEAVY
    dx = dy = 0
    if pose == 'pass':
        dy = -1
        legs = [at(LEGH_FAR, B.legs, p, 3), at(LEGH_NEAR, B.legs, p, 9), at('futa_h', B.futa, p, 0, -1)]
    else:
        legs = [at('legs_h', B.legs, p), at('futa_h', B.futa, p)]
    L = []
    if act in ('up', 'flung', 'scoop', 'raise'):
        L.append(at('arm_raise_l', (4, -1), p, dx, dy))
    if act in ('scoop', 'raise'):
        rows, g = _ladle(1)
        hand = (6 + dx, -2 + dy) if act == 'scoop' else (9 + dx, -6 + dy)
        L.append((rows, hand[0] - g[0], hand[1] - g[1], p))
    L += legs + [at('jacket_h', B.torso, p, dx, dy), at('apron_h', (10, 12), p, dx, dy)]
    if act == 'hold':
        weapon(L, 'ladle', p, (B.grip[0] + dx, B.grip[1] + dy))
        L += [at('forearm_h', B.forearm, p, dx, dy)]
    elif act in ('fling', 'swing'):
        rows, g = _ladle(-1) if act == 'swing' else _ladle(0)
        hand = (23 + dx, 15 + dy) if act == 'fling' else (22 + dx, 19 + dy)
        L.append((rows, hand[0] - g[0], hand[1] - g[1], p))
        L += [at('forearm_h', B.forearm, p, dx + 1, dy - 1 if act == 'fling' else dy + 1)]
    L += [at('sleeve_h', B.sleeve, p, dx, dy), at(FACES['cook'], B.face, p, dx, dy), at(WRAPS['pot'], B.wrap, p, dx - 1, dy, ink=INK2)]
    if act in ('up', 'flung'):
        L.append(at('arm_raise_fl', (19, 2), p, dx, dy))
    return L, B.foot, None


def quartermaster(act='stand', bob=0):
    """The Scorpion's quartermaster, who keeps the stores and drives the Roaster: the Commander's build, a fat ledger
    of a man in an apron over his uniform, a stoker's cap. act: hands (both up) or stand."""
    p = ms3.pal('olive', 'black', 'white', 'skin3')
    p['9'] = '#b8301c'
    p['L'] = '#6c3818'
    M = ms3.MARSHAL
    d = -bob
    L = [(M['boots'], 4, 40, p), (M['skirt'], 3, 30 + d, p)]
    if act == 'stand':
        L += [(M['far_arm'], 24, 12 + d, p)]
    else:
        L += [at('arm_raise_l', (25, 0 + d), p)]
    L += [(M['torso'], 4, 13 + d, p), at('apron_h', (12, 15 + d), p), (M['belt'], 4, 28 + d, p)]
    if act == 'stand':
        L += [(M['forearm'], 10, 22 + d, p)]
    L += [(M['sleeve'], 4, 15 + d, p), (FACES['cook'], 14, 5 + d, p), (WRAPS['pot'], 13, 0 + d, p, INK2)]
    if act != 'stand':
        L += [at('arm_raise_fl', (4, 3 + d), p)]
    return L, (17, 48), None


# ------------------------------------------------------------------ the Big Roaster, in parts
# Coordinates are from the middle of the tracks at the ground (the tank's anchor), x to the left negative (it faces left).
# The renderer stacks: tracks, body (hull, cab and the chimney's foot), drum, hopper, chimney, the quartermaster.
RW, RH_ = 132, 104                       # the canvas each part is painted on
OX, OY = 66, 100                         # where the anchor falls on it
OLIVE = P.OLIVE
COP = SM.COPPER
IRONR = SM.IRON


def _canvas():
    return Tone(RW, RH_)


def _part(layers, outline=True):
    """layers: [(Tone, ramp, dither)] -> (PIL image, ax, ay), outlined as sprites are, cropped."""
    L = Layer(RW, RH_)
    for T, rmp, dth in layers:
        L.paste(T.layer(rmp, dither=dth))
    if outline:
        L = P.outlined(L)
        ox, oy = OX + 1, OY + 1
    else:
        ox, oy = OX, OY
    im = L.image()
    bb = im.getbbox()
    im = im.crop(bb)
    return im, ox - bb[0], oy - bb[1]


def roaster_tracks(k):
    """The tracks: a long loop of links over six road wheels and the sprockets; k (0..2) moves the links along."""
    T = _canvas()
    W_ = _canvas()
    x0, x1, top, bot = OX - 58, OX + 58, OY - 18, OY - 1
    for x in range(x0, x1 + 1):
        for y in range(top, bot + 1):
            # the loop: rounded at both ends
            if x < x0 + 8 and (x - (x0 + 8)) ** 2 + (y - (top + bot) / 2.0) ** 2 * 3.2 > 64:
                continue
            if x > x1 - 8 and (x - (x1 - 8)) ** 2 + (y - (top + bot) / 2.0) ** 2 * 3.2 > 64:
                continue
            edge = y in (top, bot) or y in (top + 1, bot - 1)
            link = ((x + k * 2) // 3) % 2
            t = 0.36 + (0.22 if y <= top + 1 else 0) - (0.14 if y >= bot - 1 else 0) + (0.10 * link if edge else 0)
            if not edge:
                t = 0.14
            T.px(x, y, t)
    for wx in range(x0 + 10, x1 - 8, 19):
        for a in range(0, 360, 6):
            for rr in (4.5, 5.5):
                W_.px(wx + rr * np.cos(np.radians(a)), OY - 9 + rr * np.sin(np.radians(a)), 0.56 if rr < 5 else 0.36)
        W_.rect(wx - 1, OY - 10, wx + 1, OY - 8, 0.80)
        for a in range(0, 360, 90):
            ang = np.radians(a + k * 30)
            W_.px(wx + 3 * np.cos(ang), OY - 9 + 3 * np.sin(ang), 0.24)
    return _part([(T, IRONR, 0.2), (W_, IRONR, 0.2)])


def roaster_body(phase):
    """The hull: olive plate with rust, mudguards over the tracks, a sloped front with the steam grille and the low
    chute, the scorpion stencilled on its side, and the cab at the back with its bulkhead. Phase 2 and 3: dents, scorch
    marks, a plate hanging off."""
    T = _canvas()            # olive plate
    K = _canvas()            # iron fittings
    R = _canvas()            # rust
    top, bot = OY - 42, OY - 14
    for x in range(OX - 56, OX + 55):
        u = (x - (OX - 56)) / 110.0
        t0 = top + max(0, 10 - (x - (OX - 56))) if x < OX - 46 else top     # the sloped glacis at the front
        for y in range(int(t0), bot + 1):
            v = (y - top) / float(bot - top)
            t = 0.62 - 0.22 * v - 0.12 * u + 0.04 * ((x + y) % 2)
            if y == int(t0):
                t = 0.92
            if (x - (OX - 56)) % 22 == 0:
                t -= 0.14                                            # plate seams
            T.px(x, y, t)
    # rivets along the seams and the top
    for x in range(OX - 52, OX + 54, 4):
        K.px(x, top + 2, 0.80)
        K.px(x, bot - 2, 0.56)
    # the mudguard over the tracks
    for x in range(OX - 58, OX + 58):
        T.px(x, bot - 1, 0.70)
        T.px(x, bot, 0.40)
    # the grille at the front: slats, steam behind them
    for y in range(OY - 26, OY - 13):
        for x in range(OX - 58, OX - 49):
            K.px(x, y, 0.20 if (y % 3 == 0) else 0.46)
    # the low chute under the grille
    K.rect(OX - 60, OY - 12, OX - 50, OY - 6, 0.30)
    K.rect(OX - 60, OY - 12, OX - 50, OY - 12, 0.66)
    # the cab's bulkhead at the back, open on top
    for x in range(OX + 26, OX + 56):
        for y in range(OY - 62, top + 1):
            u = (x - (OX + 26)) / 30.0
            t = 0.58 - 0.20 * u + 0.04 * ((x + y) % 2)
            if y == OY - 62:
                t = 0.90
            T.px(x, y, t)
    K.rect(OX + 28, OY - 58, OX + 50, OY - 56, 0.30)               # the slot he looks out of
    # rust streaks
    for x in range(OX - 54, OX + 54, 7):
        for y in range(top + 4, bot - 2):
            if (x * 3 + y) % 5 == 0:
                R.px(x + (y % 2), y, 0.48)
    # the plough at the front: iron bars raked forward, toothed at the foot
    for i in range(5):
        for j in range(18):
            K.px(OX - 60 - j * 0.35 - i * 2, OY - 20 + j, 0.56 - 0.06 * i + (0.24 if j == 0 else 0))
    for i in range(4):
        K.px(OX - 67 - i * 2, OY - 2, 0.70)
        K.px(OX - 66 - i * 2, OY - 3, 0.40)
    # a pressure gauge by the cab, and copper pipes along the hull to the grille
    G = _canvas()
    gx, gy = OX + 44, OY - 28
    G.rect(gx - 3, gy - 3, gx + 3, gy + 3, 0.94)
    for a_ in range(0, 360, 10):
        G.px(gx + 4 * np.cos(np.radians(a_)), gy + 4 * np.sin(np.radians(a_)), 0.40)
    G.px(gx, gy, 0.20)
    G.px(gx + 1, gy - 1, 0.20)
    G.px(gx + 2, gy - 2, 0.20)
    Pp = _canvas()
    for x in range(OX - 48, OX + 26):
        Pp.px(x, OY - 37, 0.80 if x % 9 else 0.50)
        Pp.px(x, OY - 36, 0.46)
    for y in range(OY - 37, OY - 24):
        Pp.px(OX - 49, y, 0.70)
    # the militia's scorpion, sprayed on through a stencil
    Sc = _canvas()
    for j, row in enumerate(P.SCORPION):
        for i, ch in enumerate(row):
            if ch == '#':
                Sc.px(OX - 22 + i, OY - 34 + j, 0.86 if phase == 1 else 0.70)
    # hazard stripes on the front of the mudguard
    Hz = _canvas()
    for x in range(OX - 58, OX - 40):
        Hz.px(x, OY - 15, 0.9 if (x // 3) % 2 else 0.1)
        Hz.px(x, OY - 14, 0.9 if ((x + 1) // 3) % 2 else 0.1)
    layers = [(T, OLIVE, 0.35), (R, P.RUST, 0.2), (K, IRONR, 0.2), (Pp, COP, 0.2), (G, SM.LIME, 0), (Sc, SM.LIME, 0), (Hz, SM.CRANE, 0)]
    if phase >= 2:
        S_ = _canvas()
        for (cx, cy, r) in ((OX - 20, OY - 30, 6), (OX + 12, OY - 24, 5), (OX + 40, OY - 50, 4)) if phase == 3 else ((OX - 18, OY - 30, 5),):
            for y in range(cy - r, cy + r + 1):
                for x in range(cx - r - 2, cx + r + 3):
                    if (x - cx) ** 2 * 0.6 + (y - cy) ** 2 <= r * r:
                        S_.px(x, y, 0.20 + 0.25 * ((x + y) % 3 == 0))
        layers.append((S_, SM.SOOT, 0.3))
    return _part(layers)


def roaster_drum(k, cracked=False):
    """The roaster's copper drum, lying on top of the hull: lit from the upper left, banded with iron and turning (k
    moves its rivets round), the spout at its front end. Cracked: split, and glowing through the splits."""
    C = _canvas()
    K = _canvas()
    cx, cy, r, x0, x1 = OX - 6, OY - 46, 15, OX - 42, OX + 30
    for x in range(x0, x1 + 1):
        for y in range(cy - r, cy + r + 1):
            v = (y - (cy - r)) / float(2 * r)
            u = (x - x0) / float(x1 - x0)
            t = 0.30 + 0.62 * np.exp(-((v - 0.28) / 0.20) ** 2) - 0.14 * u + 0.05 * ((x + y) % 2)
            if y in (cy - r, cy + r):
                t -= 0.24
            C.px(x, y, t)
    # the end caps: domed, darker
    for y in range(cy - r, cy + r + 1):
        for i in range(3):
            K.px(x0 - 1 - i, y, 0.50 - 0.10 * i + 0.20 * (y < cy - 6))
            K.px(x1 + 1 + i, y, 0.30 - 0.06 * i)
    # iron bands, with rivets that travel round as it turns
    for bx in (x0 + 8, cx, x1 - 8):
        for y in range(cy - r, cy + r + 1):
            K.px(bx, y, 0.46 + 0.22 * (y < cy - 5))
            K.px(bx + 1, y, 0.26)
            if (y + k * 3) % 6 == 0:
                K.px(bx, y, 0.86)
    # the spout at the front, a little below the middle (the high spray comes out of it)
    B_ = _canvas()
    for x in range(OX - 56, x0 - 1):
        fl = int(np.clip((OX - 48 - x) * 0.6, 0, 4))                 # flaring toward the mouth
        for y in range(OY - 35 - fl, OY - 28 + fl):
            v = (y - (OY - 35 - fl)) / float(7 + 2 * fl)
            B_.px(x, y, 0.40 + 0.50 * np.exp(-((v - 0.3) / 0.25) ** 2))
    for y in range(OY - 39, OY - 23):
        B_.px(OX - 57, y, 0.30)
        B_.px(OX - 56, y, 0.62)
    # the crank on its side
    for a in range(0, 360, 15):
        K.px(x1 - 18 + 6 * np.cos(np.radians(a + k * 20)), cy + 2 + 6 * np.sin(np.radians(a + k * 20)) * 0.9, 0.62)
    layers = [(C, COP, 0.3), (K, IRONR, 0.2), (B_, SM.CRANE, 0.3)]
    if cracked:
        F = _canvas()
        for (sx, sy, ln, d) in ((cx - 18, cy - 8, 14, 1), (cx + 6, cy - 10, 16, -1), (cx - 4, cy + 4, 12, 1)):
            for i in range(ln):
                xx = sx + i * 0.8 * d
                yy = sy + i * 0.9 + 2 * np.sin(i * 1.3)
                F.px(xx, yy, 0.85)
                F.px(xx + 1, yy, 0.60)
        layers.append((F, SM.FIRE, 0.2))
    return _part(layers)


def roaster_hopper():
    """The hopper the green beans go in at, on top of the drum."""
    T = _canvas()
    for j in range(13):
        half = 10 - j * 0.45
        for x in range(int(OX - 6 - half), int(OX - 6 + half) + 1):
            T.px(x, OY - 73 + j, 0.62 - 0.30 * (x - (OX - 6 - half)) / (2 * half) + (0.30 if j == 0 else 0))
    return _part([(T, IRONR, 0.3)])


def roaster_chimney(stub=False):
    """The chimney at the back, a cap on it; or, once it has been shot off, the stub."""
    T = _canvas()
    topy = OY - 66 if stub else OY - 98
    for y in range(topy, OY - 42):
        for x in range(OX + 34, OX + 43):
            u = (x - (OX + 34)) / 8.0
            T.px(x, y, 0.70 - 0.46 * u + 0.04 * ((y // 6) % 2) + (0.14 if (y - topy) % 14 == 6 else 0))
    if stub:
        for x in range(OX + 33, OX + 44):
            T.px(x, topy + (x % 3), 0.20)
    else:
        T.rect(OX + 31, topy - 3, OX + 46, topy, 0.56)
        T.rect(OX + 31, topy - 3, OX + 46, topy - 3, 0.86)
    return _part([(T, IRONR, 0.3)])


def roaster_qm(shout=False):
    """The quartermaster in his cab, head and shoulders over the bulkhead, a hand on the lever."""
    p = ms3.pal('olive', 'black', 'white', 'skin3')
    p['L'] = '#6c3818'
    L = [(ms3.MARSHAL['torso'], 4, 13, p), (FACES['cook'], 14, 5, p), (WRAPS['pot'], 13, 0, p, INK2)]
    if shout:
        L.append(at('arm_raise_fl', (4, 0), p))
    im, fx, fy = compose(L, foot=(17, 30))
    im = im.crop((0, 0, im.width, min(im.height, 26)))
    return im, fx, 0                                  # (anchored at the top of his head)


def roaster_parts():
    out = {}
    for k in range(3):
        out['rst_track%d' % k] = roaster_tracks(k)
        out['rst_drum%d' % k] = roaster_drum(k)
        out['rst_drumc%d' % k] = roaster_drum(k, cracked=True)
    for ph in (1, 2, 3):
        out['rst_body%d' % ph] = roaster_body(ph)
    out['rst_hopper'] = roaster_hopper()
    out['rst_chimney'] = roaster_chimney()
    out['rst_stub'] = roaster_chimney(stub=True)
    out['rst_qm0'] = roaster_qm(False)
    out['rst_qm1'] = roaster_qm(True)
    return out


# ------------------------------------------------------------------ the roasting house's vents, steam, beans, sacks
def _img(T, rmp, dither=0.3, outline=False):
    L = T.layer(rmp, dither=dither)
    if outline:
        L = P.outlined(L)
    im = L.image()
    bb = im.getbbox()
    return im.crop(bb), bb


def vent(hot=False):
    """A grating in the floor over the steam pipe: iron bars; red hot round the edge while it is about to blow."""
    T = Tone(26, 7)
    for x in range(26):
        for y in range(7):
            t = 0.20 if (x % 4 == 1 and 1 <= y <= 5) else 0.56 - 0.06 * y + (0.24 if y == 0 else 0)
            if x in (0, 25):
                t = 0.34
            T.px(x, y, t)
    L = T.layer(SM.IRON, dither=0.2)
    if hot:
        for x in range(1, 25):
            for y in range(1, 6):
                if x % 4 == 1:
                    L.rgb[y, x] = (255, 120 + 30 * (y % 2), 40)
    im = P.outlined(L).image()
    return im, im.width // 2, 3


STEAM = ramp(['#4c4e58', '#74768a', '#9ea2b0', '#c4c8d0', '#e2e4e8', '#f6f6f6', '#ffffff'], 12)


def _puff_field(W_, H_, blobs):
    """A height field of heaped balls (steam, smoke): each blob (x, y, r)."""
    yy, xx = np.mgrid[0:H_, 0:W_]
    Z = np.zeros((H_, W_))
    for (bx, by, br) in blobs:
        d2 = (xx - bx) ** 2 + (yy - by) ** 2
        Z = np.maximum(Z, np.sqrt(np.clip(br * br - d2, 0, None)))
    return Z


def _steam_from(Z, seed):
    """Light a puff field from the upper left; thin, broken edges, so it reads as steam and not as a wall."""
    H_, W_ = Z.shape
    yy, xx = np.mgrid[0:H_, 0:W_]
    from scipy import ndimage as ndi
    lit = -np.gradient(ndi.gaussian_filter(Z, 0.8))[1] * 0.7 - np.gradient(ndi.gaussian_filter(Z, 0.8))[0] * 0.7
    t = 0.62 + 0.30 * np.clip(lit, -1, 1) + 0.04 * (noise((H_, W_), seed, 3, 3) - 0.5)
    m = Z > 0.6
    rim = m & (Z < 2.2)
    m &= ~(rim & ((xx + yy) % 2 == 0))
    T = Tone(W_, H_)
    T.mask(m, 0)
    T.t = np.where(m, np.clip(t, 0, 1), T.t)
    return T.layer(STEAM, dither=0.4).image()


def steam_column(k):
    """A column of steam blown up out of a grating: narrow at the foot, billowing wider as it rises."""
    W_, H_ = 34, 76
    r = rng(70 + k)
    blobs = []
    for i in range(16):
        u = i / 15.0                                   # 0 at the foot, 1 at the top
        by = H_ - 4 - u * (H_ - 14)
        br = 3.5 + 9 * u ** 0.8 + r.uniform(-1.2, 1.2)
        bx = W_ / 2.0 + r.uniform(-1, 1) * (1 + 4 * u) + 2 * np.sin(u * 6 + k * 2)
        blobs.append((bx, by, br))
    im = _steam_from(_puff_field(W_, H_, blobs), 80 + k)
    return im, W_ // 2, H_ - 1


def steam_jet(k):
    """The Roaster's jet of steam from its grille along the ground, to the left; anchored at the grille."""
    W_, H_ = 88, 30
    r = rng(90 + k)
    blobs = []
    for i in range(18):
        u = i / 17.0                                   # 0 at the grille (right), 1 at the far end
        bx = W_ - 4 - u * (W_ - 12)
        br = 3 + 9 * u ** 0.75 + r.uniform(-1, 1)
        by = H_ - 9 - 5 * u + r.uniform(-1, 1) * (1 + 2 * u)
        blobs.append((bx, by, br))
    im = _steam_from(_puff_field(W_, H_, blobs), 95 + k)
    return im, W_ - 1, H_ - 9


def bean(hot=False):
    """A coffee bean on the fly: three pixels by two, a crease; red hot when the Roaster fires them."""
    if hot:
        im = sprite(['.oO.', 'oYyO', '.oO.'], {'o': '#4a1c08', 'O': '#8a3410', 'Y': '#ffd060', 'y': '#ff8a20'})
    else:
        im = sprite(['.oO.', 'oCcO', '.oO.'], {'o': '#2a1408', 'O': '#6c3818', 'C': '#a0602c', 'c': '#1a0c04'})
    return outline(im, (16, 10, 6, 255)), 2, 1


def roast_bomb():
    """What the Roaster lobs out of its hopper: a bean as big as a fist, roasting as it flies."""
    rows = ['..xxxx..', '.xOoOOx.', 'xOYoOOOx', 'xOoyoOOx', 'xOOoYoOx', '.xOOoOx.', '..xxxx..']
    im = sprite(rows, {'x': '#140804', 'O': '#7a3410', 'o': '#2a1006', 'Y': '#ffcc50', 'y': '#ff8020'})
    return im, 4, 3


def pour(k):
    """A pour of burning beans rolling along the ground: a low heap, flames licking up off it."""
    W_, H_ = 18, 14
    T = Tone(W_, H_)
    F = Tone(W_, H_)
    r = rng(100 + k)
    for x in range(W_):
        u = (x - W_ / 2.0) / (W_ / 2.0)
        hh = int(5 * np.sqrt(max(0, 1 - u * u)))
        for y in range(H_ - 1 - hh, H_):
            T.px(x, y, 0.3 + 0.4 * ((x * 3 + y * 5 + k) % 4 == 0))
        if r.random() < 0.6:
            fl = int(r.integers(2, 8))
            for y in range(H_ - 1 - hh - fl, H_ - 1 - hh):
                F.px(x, y, 0.5 + 0.5 * (y - (H_ - 1 - hh - fl)) / fl)
    L = T.layer(SM.BEAN, dither=0)
    L.paste(F.layer(SM.FIRE, dither=0.2))
    im = L.image()
    return im, W_ // 2, H_ - 1


def pick_bean():
    """Roast coffee, rained down out of the burst drum: worth picking up (points)."""
    rows = ['..xxx..', '.xOOox.', 'xOOcoOx', 'xOocOOx', '.xoOOx.', '..xxx..']
    im = sprite(rows, {'x': '#140804', 'O': '#8a4c22', 'o': '#4e2610', 'c': '#1a0c04'})
    return im, 3, 5


def sacks_cover():
    """A wall of coffee sacks a man can hide behind: three rows, outlined (it is something to shoot at)."""
    T = Tone(58, 24)
    k = 0
    for row, (y0, n, off) in enumerate(((16, 4, 0), (9, 4, 7), (2, 3, 13))):
        for c in range(n):
            k += 1
            SM.sack_tone(T, off + c * 13, y0, 14, 8, seed=k, lit=0.05 * (row == 2))
    L = T.layer(SM.SACK, dither=0.4)
    for (sx, sy) in ((13, 16), (20, 9)):
        SM.sack_marks(L, sx, sy, 14, 8, kind=0)
    im = P.outlined(L).image()
    bb = im.getbbox()
    im = im.crop(bb)
    return im, im.width // 2, im.height - 1


def mocha_fx():
    out = {}
    out['vent'] = vent(False)
    out['vent_hot'] = vent(True)
    for k in range(3):
        out['steam%d' % k] = steam_column(k)
    for k in range(2):
        out['sjet%d' % k] = steam_jet(k)
        out['fx_pour%d' % k] = pour(k)
    out['fx_bean'] = bean(False)
    out['fx_bean_hot'] = bean(True)
    out['roastbomb'] = roast_bomb()
    out['pick_bean'] = pick_bean()
    out['sacks_cover'] = sacks_cover()
    return out


def frames():
    """name -> dict(im, ax, ay[, mx, my])"""
    out = {}
    for pose in ('stand', 'pass'):
        out['cook_' + pose] = SP.build(*cook(pose, 'hold'))
        out['cook_up_' + pose] = SP.build(*cook(pose, 'up'))
    for act in ('scoop', 'fling', 'raise', 'swing'):
        out['cook_' + act] = SP.build(*cook('stand', act))
    out['cook_flung'] = SP.build(*cook('pass', 'flung'))
    out['qm_stand'] = SP.build(*quartermaster('stand'))
    out['qm_up_stand'] = SP.build(*quartermaster('hands'))
    out['qm_up_pass'] = SP.build(*quartermaster('hands', bob=1))
    return out


def roaster_preview(path):
    parts = roaster_parts()
    sheet = Image.new('RGBA', (3 * 150 + 10, 2 * 120 + 10), (86, 150, 170, 255))
    for i, (ph, k) in enumerate(((1, 0), (2, 1), (3, 2), (1, 1), (2, 2), (3, 0))):
        ax, ay = 10 + (i % 3) * 150 + 70, 10 + (i // 3) * 120 + 108
        order = ['rst_track%d' % k, 'rst_body%d' % ph, ('rst_drumc%d' if ph == 3 else 'rst_drum%d') % k]
        if ph < 3:
            order.append('rst_hopper')
        order.append('rst_chimney' if ph == 1 else 'rst_stub')
        for n in order:
            im, fx, fy = parts[n]
            sheet.alpha_composite(im, (ax - fx, ay - fy))
        im, fx, fy = parts['rst_qm%d' % (i % 2)]
        sheet.alpha_composite(im, (ax + 38 - fx, ay - 82 - fy))
    sheet = sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST)
    sheet.save(path)


def fx_preview(path):
    fx = mocha_fx()
    W = sum(v[0].width + 8 for v in fx.values()) + 8
    Hh = max(v[0].height for v in fx.values()) + 16
    sheet = Image.new('RGBA', (W, Hh), (60, 44, 34, 255))
    x = 8
    for n, (im, ax, ay) in fx.items():
        sheet.alpha_composite(im, (x, Hh - 8 - im.height))
        x += im.width + 8
    sheet.resize((W * 4, Hh * 4), Image.NEAREST).save(path)
    print(list(fx))


if __name__ == '__main__':
    if 'fx' in sys.argv:
        fx_preview(sys.argv[1])
        sys.exit(0)
    if 'roaster' in sys.argv:
        roaster_preview(sys.argv[1])
        sys.exit(0)
    fr = frames()
    ref = SP.build(*SP.rifleman('stand', 'worried', 'skin2'))
    names = ['ref'] + list(fr)
    cells = [ref] + [fr[n] for n in fr]
    W = sum(c['im'].width + 6 for c in cells) + 6
    Hh = max(c['im'].height for c in cells) + 12
    sheet = Image.new('RGBA', (W, Hh), (86, 150, 170, 255))
    x = 6
    for c in cells:
        im = c['im']
        sheet.alpha_composite(im, (x, Hh - 6 - im.height))
        x += im.width + 6
    sheet = sheet.resize((W * 5, Hh * 5), Image.NEAREST)
    sheet.save(sys.argv[1] if len(sys.argv) > 1 else 'mocha_sprites.png')
    print(names)
