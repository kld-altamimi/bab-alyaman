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
# The renderer stacks: tracks, body (hull, platform and the stack's foot), drum, hopper, chimney, the quartermaster.
# 24 Oct, Khaled's five small edits (approved 22 Oct; drawn first in tools/roaster_minor.py), so it reads as a roastery
# on tracks, not a locomotive: 1 a short stack with the chaff cyclone on it; 2 the plough off, a cooling tray out front
# with its stirring arm, and the spout bent down into a chute over it; 3 five big road wheels instead of six small ones;
# 4 the cab cut down to an open platform with a railing, green-bean sacks on the deck; 5 a sight glass and a trier on
# the drum, its front end cap a faceplate with the bean door. What it does is unchanged (roaster.js).
RW, RH_ = 180, 104                       # the canvas each part is painted on (wider since the tray stands out in front)
OX, OY = 90, 100                         # where the anchor falls on it
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
    """The tracks: a long loop of links over five big road wheels with dished hubs; k (0..2) moves the links along."""
    T = _canvas()
    W_ = _canvas()
    x0, x1, top, bot = OX - 58, OX + 58, OY - 20, OY - 1
    for x in range(x0, x1 + 1):
        for y in range(top, bot + 1):
            # the loop: rounded at both ends
            if x < x0 + 9 and (x - (x0 + 9)) ** 2 + (y - (top + bot) / 2.0) ** 2 * 2.6 > 81:
                continue
            if x > x1 - 9 and (x - (x1 - 9)) ** 2 + (y - (top + bot) / 2.0) ** 2 * 2.6 > 81:
                continue
            edge = y in (top, bot) or y in (top + 1, bot - 1)
            link = ((x + k * 2) // 3) % 2
            t = 0.36 + (0.22 if y <= top + 1 else 0) - (0.14 if y >= bot - 1 else 0) + (0.10 * link if edge else 0)
            if not edge:
                t = 0.14
            T.px(x, y, t)
    # five road wheels, big, with a dished hub and five spoke holes that turn
    for wx in range(x0 + 12, x1 - 8, 23):
        for a in range(0, 360, 4):
            for rr in (5.5, 6.5, 7.5):
                W_.px(wx + rr * np.cos(np.radians(a)), OY - 10 + rr * np.sin(np.radians(a)), 0.60 if rr < 6 else (0.42 if rr < 7 else 0.30))
        W_.rect(wx - 1, OY - 11, wx + 1, OY - 9, 0.84)
        for a in range(0, 360, 72):
            ang = np.radians(a + k * 24)
            W_.px(wx + 4 * np.cos(ang), OY - 10 + 4 * np.sin(ang), 0.22)
    return _part([(T, IRONR, 0.2), (W_, IRONR, 0.2)])


def roaster_body(phase):
    """The hull: olive plate with rust, mudguards over the tracks, a sloped front with the steam grille and the low
    chute, the scorpion stencilled on its side; the open platform at the back with its railing and the green-bean
    sacks; the cooling tray out front on its bracket, beans heaped in it and the stirring arm over them. Phase 2 and 3:
    scorch marks."""
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
    # the platform at the back: the bulkhead cut down to knee height, a railing above it (an open platform, not a cab)
    for x in range(OX + 26, OX + 56):
        for y in range(OY - 50, top + 1):
            u = (x - (OX + 26)) / 30.0
            t = 0.58 - 0.20 * u + 0.04 * ((x + y) % 2)
            if y == OY - 50:
                t = 0.90
            T.px(x, y, t)
    K.rect(OX + 26, OY - 60, OX + 56, OY - 59, 0.72)                  # the top rail
    for x in (OX + 27, OX + 41, OX + 55):
        K.rect(x, OY - 59, x, OY - 51, 0.50)                           # its posts
    K.rect(OX + 26, OY - 55, OX + 56, OY - 55, 0.40)                  # the middle rail
    # rust streaks
    for x in range(OX - 54, OX + 54, 7):
        for y in range(top + 4, bot - 2):
            if (x * 3 + y) % 5 == 0:
                R.px(x + (y % 2), y, 0.48)
    # a pressure gauge by the platform, and copper pipes along the hull to the grille
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
    # the cooling tray: a wide shallow pan out in front on an iron bracket, its rim bright, the beans showing over it,
    # a stirring arm sweeping over them from a post with the motor on top
    Tr = _canvas()
    Bk = _canvas()
    Bn = _canvas()
    tx0, tx1, ty = OX - 86, OX - 58, OY - 26
    for x in range(tx0, tx1 + 1):
        u = (x - tx0) / float(tx1 - tx0)
        for y in range(ty - 6, ty + 2):
            v = (y - (ty - 6)) / 7.0
            t = 0.58 - 0.26 * v - 0.12 * u + 0.04 * ((x + y) % 2)
            if y == ty - 6:
                t = 0.95                                             # the rim
            if y == ty - 5:
                t = 0.22                                             # the dark inside, just over the rim
            if x in (tx0, tx1):
                t += 0.2
            Tr.px(x, y, t)
    for i in range(13):                                              # the beans heaped in it
        Bn.px(tx0 + 2 + i * 2 + (i % 2), ty - 6 - (i % 3 == 1), 0.5 + 0.25 * (i % 2))
        Bn.px(tx0 + 3 + i * 2, ty - 5, 0.35)
    mx = (tx0 + tx1) // 2
    Bk.rect(tx0 + 3, ty - 8, tx1 - 3, ty - 8, 0.74)                 # the stirring arm, over the pan
    Bk.rect(tx0 + 3, ty - 7, tx1 - 3, ty - 7, 0.40)
    Bk.rect(mx, ty - 15, mx + 1, ty - 8, 0.56)                        # its post...
    Bk.rect(mx - 3, ty - 19, mx + 4, ty - 15, 0.70)                   # ...and the motor
    Bk.rect(mx - 3, ty - 19, mx + 4, ty - 19, 0.92)
    Bk.rect(OX - 62, ty - 1, OX - 56, ty + 1, 0.5)                    # the bracket from the hull
    for i in range(12):
        Bk.px(OX - 72 + i * 0.9, ty + 2 + i, 0.44)                    # and a strut down to the mudguard
    layers += [(Tr, COP, 0.3), (Bn, SM.BEAN, 0.2), (Bk, IRONR, 0.2)]
    # green-bean sacks on the deck behind him
    Sk = _canvas()
    for (sx, sy, w_, h_) in ((OX + 46, OY - 60, 11, 10), (OX + 49, OY - 69, 9, 9)):
        for x in range(sx, sx + w_):
            for y in range(sy, sy + h_):
                u = (x - sx) / float(w_)
                Sk.px(x, y, 0.62 - 0.3 * u + 0.05 * ((x + y) % 2) - (0.2 if y == sy + h_ - 1 else 0))
        Sk.rect(sx + 2, sy - 1, sx + w_ - 3, sy - 1, 0.34)              # the tied neck
    layers.append((Sk, SM.SACK, 0.3))
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
    moves its rivets round); at its front a square chute bent down over the cooling tray (the high spray comes out of
    it), a sight glass and a trier on its front band, and the end cap squared off into a faceplate with the round bean
    door. Cracked: split, and glowing through the splits."""
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
    # the discharge chute: a square duct from the drum's front, bent down toward the cooling tray
    B_ = _canvas()
    for i in range(14):
        xx = x0 - 2 - i
        yy = OY - 35 + i * 0.45
        for j in range(7):
            B_.px(xx, yy + j, 0.40 + 0.5 * np.exp(-((j - 2) / 2.0) ** 2))
        B_.px(xx, yy, 0.92)
    B_.rect(x0 - 18, OY - 30, x0 - 15, OY - 29, 0.8)                 # its lip, over the tray
    B_.rect(x0 - 18, OY - 28, x0 - 16, OY - 27, 0.3)
    # the crank on its side
    for a in range(0, 360, 15):
        K.px(x1 - 18 + 6 * np.cos(np.radians(a + k * 20)), cy + 2 + 6 * np.sin(np.radians(a + k * 20)) * 0.9, 0.62)
    layers = [(C, COP, 0.3), (K, IRONR, 0.2), (B_, SM.CRANE, 0.3)]
    # the sight glass by the front band, the trier (the sampling scoop's brass handle) under it, and the faceplate
    Gl = _canvas()
    for a in range(0, 360, 8):
        for rr in (2.0, 3.0):
            Gl.px(x0 + 14 + rr * np.cos(np.radians(a)), cy - 6 + rr * np.sin(np.radians(a)), 0.9 if rr < 2.5 else 0.5)
    Gl.px(x0 + 14, cy - 6, 0.7)
    Gl.px(x0 + 13, cy - 7, 0.98)
    Tt = _canvas()
    Tt.rect(x0 + 12, cy + 5, x0 + 17, cy + 6, 0.8)                    # the trier's handle
    Tt.rect(x0 + 10, cy + 5, x0 + 11, cy + 6, 0.98)                    # its brass knob
    Fp = _canvas()
    for y in range(cy - r - 1, cy + r + 2):
        for i in range(4):
            Fp.px(x0 - 1 - i, y, 0.44 - 0.08 * i + 0.2 * (y < cy - 6))
    for a in range(0, 360, 10):
        Fp.px(x0 - 3 + 2.0 * np.cos(np.radians(a)) * 0.5, cy + 5.5 * np.sin(np.radians(a)), 0.9)   # the door's ring
    Fp.rect(x0 - 4, cy - 1, x0 - 3, cy + 1, 0.98)                                                    # its handle
    layers += [(Fp, IRONR, 0.2), (Gl, SM.GLASS, 0.2), (Tt, SM.CRANE, 0.3)]
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
    """The stack at the back: short, with the chaff cyclone on it (a fat can, a cone under it into the stack, a thin
    pipe out of its top bent back and down: a roastery's exhaust, not a funnel); or, once it has been shot off, the
    stub where it stood. (Its smoke comes out of the pipe's end, x+69 y-88, or the stub's top, x+52 y-62:
    render_roaster.js.)"""
    T = _canvas()
    if stub:
        topy = OY - 60
        for y in range(topy, OY - 42):
            for x in range(OX + 48, OX + 57):
                u = (x - (OX + 48)) / 8.0
                T.px(x, y, 0.70 - 0.46 * u + 0.04 * ((y // 6) % 2))
        for x in range(OX + 47, OX + 58):
            T.px(x, topy + (x % 3), 0.20)
        return _part([(T, IRONR, 0.3)])
    topy = OY - 70
    for y in range(topy, OY - 42):
        for x in range(OX + 48, OX + 57):
            u = (x - (OX + 48)) / 8.0
            T.px(x, y, 0.70 - 0.46 * u + 0.04 * ((y // 6) % 2))
    cx0, cx1 = OX + 43, OX + 63
    for y in range(topy - 8, topy + 1):                      # the cone, narrowing to the stack
        v = (y - (topy - 8)) / 8.0
        half = 10.5 - 6 * v
        for x in range(int(OX + 52.5 - half), int(OX + 52.5 + half) + 1):
            u = (x - (OX + 52.5 - half)) / (2 * half + 0.01)
            T.px(x, y, 0.62 - 0.4 * u)
    for y in range(topy - 22, topy - 8):                     # the can
        for x in range(cx0, cx1 + 1):
            u = (x - cx0) / float(cx1 - cx0)
            T.px(x, y, 0.74 - 0.5 * u + (0.1 if y in (topy - 22, topy - 13) else 0))
    T.rect(cx0 - 1, topy - 23, cx1 + 1, topy - 23, 0.9)
    T.rect(cx0 - 1, topy - 22, cx0 - 1, topy - 8, 0.4)
    T.rect(cx1 + 1, topy - 22, cx1 + 1, topy - 8, 0.4)
    for y in range(topy - 29, topy - 23):                    # the thin pipe out of the top...
        T.px(OX + 53, y, 0.76)
        T.px(OX + 54, y, 0.5)
        T.px(OX + 55, y, 0.3)
    for x in range(OX + 53, OX + 70):                        # ...bent back and down
        T.px(x, topy - 30, 0.76)
        T.px(x, topy - 29, 0.5)
        T.px(x, topy - 28, 0.3)
    for y in range(topy - 30, topy - 19):
        T.px(OX + 68, y, 0.6)
        T.px(OX + 69, y, 0.42)
        T.px(OX + 70, y, 0.28)
    return _part([(T, IRONR, 0.3)])


def roaster_qm(shout=False):
    """The quartermaster on his open platform, his coat going down behind the railing, a hand on the lever."""
    p = ms3.pal('olive', 'black', 'white', 'skin3')
    p['L'] = '#6c3818'
    L = [(ms3.MARSHAL['torso'], 4, 13, p), (FACES['cook'], 14, 5, p), (WRAPS['pot'], 13, 0, p, INK2)]
    if shout:
        L.append(at('arm_raise_fl', (4, 0), p))
    im, fx, fy = compose(L, foot=(17, 30))
    im = im.crop((0, 0, im.width, min(im.height, 34)))
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
