# roaster_minor.py - the Big Roaster with small edits to its own sprite, so it stops reading as a locomotive and
# starts reading as a roastery on tracks. Everything is drawn with mocha_sprites' own functions where a part does
# not change; edited parts are copies with the edit in them. Two steps: 'light' (three edits) and 'full' (five).
#   1 chimney: shorter, no cap, an elbow bending back over the deck (a stovepipe flue, not a smokestack)
#   2 plough off; a round cooling tray out front on a bracket, a stirring arm on it, the spout bent down into a
#     chute that pours into the tray
#   3 tracks: five big road wheels instead of six small ones
#   4 cab: the bulkhead cut down to a railing, the quartermaster on an open platform, green-bean sacks behind him
#   5 drum: a sight glass and a trier on the front band, the end cap a flat faceplate with a bean door
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image
import mocha_sprites as MS
MS.RW, MS.OX = 180, 90                    # (a wider canvas than the game's parts: the tray stands out past the hull)
from mocha_sprites import _canvas, _part, OX, OY, OLIVE, COP, IRONR
import props as P
import stage_mocha as SM
import boss_concepts as B

EDITS = {'light': (1, 2, 3), 'full': (1, 2, 3, 4, 5)}


def tracks(k, big):
    if not big:
        return MS.roaster_tracks(k)
    T = _canvas()
    W_ = _canvas()
    x0, x1, top, bot = OX - 58, OX + 58, OY - 20, OY - 1
    for x in range(x0, x1 + 1):
        for y in range(top, bot + 1):
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
    # five road wheels, big, with a dished hub and five spokes-holes
    for wx in range(x0 + 12, x1 - 8, 23):
        for a in range(0, 360, 4):
            for rr in (5.5, 6.5, 7.5):
                W_.px(wx + rr * np.cos(np.radians(a)), OY - 10 + rr * np.sin(np.radians(a)), 0.60 if rr < 6 else (0.42 if rr < 7 else 0.30))
        W_.rect(wx - 1, OY - 11, wx + 1, OY - 9, 0.84)
        for a in range(0, 360, 72):
            ang = np.radians(a + k * 24)
            W_.px(wx + 4 * np.cos(ang), OY - 10 + 4 * np.sin(ang), 0.22)
    return _part([(T, IRONR, 0.2), (W_, IRONR, 0.2)])


def body(phase, edits):
    tray, platform = 2 in edits, 4 in edits
    T = _canvas()
    K = _canvas()
    R = _canvas()
    top, bot = OY - 42, OY - 14
    for x in range(OX - 56, OX + 55):
        u = (x - (OX - 56)) / 110.0
        t0 = top + max(0, 10 - (x - (OX - 56))) if x < OX - 46 else top
        for y in range(int(t0), bot + 1):
            v = (y - top) / float(bot - top)
            t = 0.62 - 0.22 * v - 0.12 * u + 0.04 * ((x + y) % 2)
            if y == int(t0):
                t = 0.92
            if (x - (OX - 56)) % 22 == 0:
                t -= 0.14
            T.px(x, y, t)
    for x in range(OX - 52, OX + 54, 4):
        K.px(x, top + 2, 0.80)
        K.px(x, bot - 2, 0.56)
    for x in range(OX - 58, OX + 58):
        T.px(x, bot - 1, 0.70)
        T.px(x, bot, 0.40)
    for y in range(OY - 26, OY - 13):
        for x in range(OX - 58, OX - 49):
            K.px(x, y, 0.20 if (y % 3 == 0) else 0.46)
    K.rect(OX - 60, OY - 12, OX - 50, OY - 6, 0.30)
    K.rect(OX - 60, OY - 12, OX - 50, OY - 12, 0.66)
    if platform:
        # the bulkhead cut down to knee height, a railing above it: an open platform, not a cab
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
    else:
        for x in range(OX + 26, OX + 56):
            for y in range(OY - 62, top + 1):
                u = (x - (OX + 26)) / 30.0
                t = 0.58 - 0.20 * u + 0.04 * ((x + y) % 2)
                if y == OY - 62:
                    t = 0.90
                T.px(x, y, t)
        K.rect(OX + 28, OY - 58, OX + 50, OY - 56, 0.30)
    for x in range(OX - 54, OX + 54, 7):
        for y in range(top + 4, bot - 2):
            if (x * 3 + y) % 5 == 0:
                R.px(x + (y % 2), y, 0.48)
    if not tray:
        for i in range(5):
            for j in range(18):
                K.px(OX - 60 - j * 0.35 - i * 2, OY - 20 + j, 0.56 - 0.06 * i + (0.24 if j == 0 else 0))
        for i in range(4):
            K.px(OX - 67 - i * 2, OY - 2, 0.70)
            K.px(OX - 66 - i * 2, OY - 3, 0.40)
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
    Sc = _canvas()
    for j, row in enumerate(P.SCORPION):
        for i, ch in enumerate(row):
            if ch == '#':
                Sc.px(OX - 22 + i, OY - 34 + j, 0.86 if phase == 1 else 0.70)
    Hz = _canvas()
    for x in range(OX - 58, OX - 40):
        Hz.px(x, OY - 15, 0.9 if (x // 3) % 2 else 0.1)
        Hz.px(x, OY - 14, 0.9 if ((x + 1) // 3) % 2 else 0.1)
    layers = [(T, OLIVE, 0.35), (R, P.RUST, 0.2), (K, IRONR, 0.2), (Pp, COP, 0.2), (G, SM.LIME, 0), (Sc, SM.LIME, 0), (Hz, SM.CRANE, 0)]
    if tray:
        # the cooling tray: a wide shallow pan out in front on an iron bracket, its rim bright, the beans showing
        # over it, a stirring arm sweeping round on a post with the motor on top
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
                    t = 0.95                                         # the rim
                if y == ty - 5:
                    t = 0.22                                         # the dark inside, just over the rim
                if x in (tx0, tx1):
                    t += 0.2
                Tr.px(x, y, t)
        for i in range(13):                                          # the beans heaped in it
            Bn.px(tx0 + 2 + i * 2 + (i % 2), ty - 6 - (i % 3 == 1), 0.5 + 0.25 * (i % 2))
            Bn.px(tx0 + 3 + i * 2, ty - 5, 0.35)
        mx = (tx0 + tx1) // 2
        Bk.rect(tx0 + 3, ty - 8, tx1 - 3, ty - 8, 0.74)             # the stirring arm, sweeping over the pan
        Bk.rect(tx0 + 3, ty - 7, tx1 - 3, ty - 7, 0.40)
        Bk.rect(mx, ty - 15, mx + 1, ty - 8, 0.56)                    # its post...
        Bk.rect(mx - 3, ty - 19, mx + 4, ty - 15, 0.70)               # ...and the motor
        Bk.rect(mx - 3, ty - 19, mx + 4, ty - 19, 0.92)
        Bk.rect(OX - 62, ty - 1, OX - 56, ty + 1, 0.5)                # the bracket from the hull
        for i in range(12):
            Bk.px(OX - 72 + i * 0.9, ty + 2 + i, 0.44)                # and a strut down to the mudguard
        layers += [(Tr, COP, 0.3), (Bn, SM.BEAN, 0.2), (Bk, IRONR, 0.2)]
    if platform:
        # green-bean sacks on the deck behind him
        Sk = _canvas()
        for (sx, sy, w_, h_) in ((OX + 46, OY - 60, 11, 10), (OX + 49, OY - 69, 9, 9)):
            for x in range(sx, sx + w_):
                for y in range(sy, sy + h_):
                    u = (x - sx) / float(w_)
                    Sk.px(x, y, 0.62 - 0.3 * u + 0.05 * ((x + y) % 2) - (0.2 if y == sy + h_ - 1 else 0))
            Sk.rect(sx + 2, sy - 1, sx + w_ - 3, sy - 1, 0.34)          # the tied neck
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


def drum(k, edits, cracked=False):
    chute, fittings = 2 in edits, 5 in edits
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
    for y in range(cy - r, cy + r + 1):
        for i in range(3):
            K.px(x0 - 1 - i, y, 0.50 - 0.10 * i + 0.20 * (y < cy - 6))
            K.px(x1 + 1 + i, y, 0.30 - 0.06 * i)
    for bx in (x0 + 8, cx, x1 - 8):
        for y in range(cy - r, cy + r + 1):
            K.px(bx, y, 0.46 + 0.22 * (y < cy - 5))
            K.px(bx + 1, y, 0.26)
            if (y + k * 3) % 6 == 0:
                K.px(bx, y, 0.86)
    B_ = _canvas()
    if chute:
        # the discharge chute: a square duct from the drum's front, bent down toward the cooling tray
        for i in range(14):
            xx = x0 - 2 - i
            yy = OY - 35 + i * 0.45
            for j in range(7):
                B_.px(xx, yy + j, 0.40 + 0.5 * np.exp(-((j - 2) / 2.0) ** 2))
            B_.px(xx, yy, 0.92)
        B_.rect(x0 - 18, OY - 30, x0 - 15, OY - 29, 0.8)             # its lip, over the tray
        B_.rect(x0 - 18, OY - 28, x0 - 16, OY - 27, 0.3)
    else:
        for x in range(OX - 56, x0 - 1):
            fl = int(np.clip((OX - 48 - x) * 0.6, 0, 4))
            for y in range(OY - 35 - fl, OY - 28 + fl):
                v = (y - (OY - 35 - fl)) / float(7 + 2 * fl)
                B_.px(x, y, 0.40 + 0.50 * np.exp(-((v - 0.3) / 0.25) ** 2))
        for y in range(OY - 39, OY - 23):
            B_.px(OX - 57, y, 0.30)
            B_.px(OX - 56, y, 0.62)
    for a in range(0, 360, 15):
        K.px(x1 - 18 + 6 * np.cos(np.radians(a + k * 20)), cy + 2 + 6 * np.sin(np.radians(a + k * 20)) * 0.9, 0.62)
    layers = [(C, COP, 0.3), (K, IRONR, 0.2), (B_, SM.CRANE, 0.3)]
    if fittings:
        # a sight glass by the front band, a trier (the sampling scoop's brass handle) under it, and the front end
        # cap squared off into a faceplate with the round bean door on it
        Gl = _canvas()
        for a in range(0, 360, 8):
            for rr in (2.0, 3.0):
                Gl.px(x0 + 14 + rr * np.cos(np.radians(a)), cy - 6 + rr * np.sin(np.radians(a)), 0.9 if rr < 2.5 else 0.5)
        Gl.px(x0 + 14, cy - 6, 0.7)
        Gl.px(x0 + 13, cy - 7, 0.98)
        Tr = _canvas()
        Tr.rect(x0 + 12, cy + 5, x0 + 17, cy + 6, 0.8)                    # the trier's handle
        Tr.rect(x0 + 10, cy + 5, x0 + 11, cy + 6, 0.98)                    # its brass knob
        Fp = _canvas()
        for y in range(cy - r - 1, cy + r + 2):
            for i in range(4):
                Fp.px(x0 - 1 - i, y, 0.44 - 0.08 * i + 0.2 * (y < cy - 6))
        for a in range(0, 360, 10):
            Fp.px(x0 - 3 + 2.0 * np.cos(np.radians(a)) * 0.5, cy + 5.5 * np.sin(np.radians(a)), 0.9)   # the door's ring
        Fp.rect(x0 - 4, cy - 1, x0 - 3, cy + 1, 0.98)                                                    # its handle
        layers += [(Fp, IRONR, 0.2), (Gl, SM.GLASS, 0.2), (Tr, SM.CRANE, 0.3)]
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


def chimney(edits, stub=False):
    if 1 not in edits:
        return MS.roaster_chimney(stub)
    T = _canvas()
    if stub:
        topy = OY - 60
        for y in range(topy, OY - 42):
            for x in range(OX + 34, OX + 43):
                u = (x - (OX + 34)) / 8.0
                T.px(x, y, 0.70 - 0.46 * u + 0.04 * ((y // 6) % 2))
        for x in range(OX + 33, OX + 44):
            T.px(x, topy + (x % 3), 0.20)
        return _part([(T, IRONR, 0.3)])
    # a short stack with the chaff cyclone on it: a fat can, a cone under it into the stack, a thin pipe out of
    # its top bent back (a roastery's exhaust, not a funnel)
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


def parts(step):
    e = EDITS[step]
    out = {}
    for k in range(3):
        out['rst_track%d' % k] = tracks(k, 3 in e)
        out['rst_drum%d' % k] = drum(k, e)
        out['rst_drumc%d' % k] = drum(k, e, cracked=True)
    for ph in (1, 2, 3):
        out['rst_body%d' % ph] = body(ph, e)
    out['rst_hopper'] = MS.roaster_hopper()
    out['rst_chimney'] = chimney(e)
    out['rst_stub'] = chimney(e, stub=True)
    for i, sh in enumerate((False, True)):
        im, fx, fy = MS.roaster_qm(sh)
        if 4 in e:                                            # on the open platform his coat goes down to the deck
            full_, fx2, fy2 = qm_long(sh)
            im = full_
        out['rst_qm%d' % i] = (im, fx, fy)
    return out


def qm_long(shout):
    from mocha_sprites import ms3, FACES, WRAPS, at, compose, INK2
    p = ms3.pal('olive', 'black', 'white', 'skin3')
    p['L'] = '#6c3818'
    L = [(ms3.MARSHAL['torso'], 4, 13, p), (FACES['cook'], 14, 5, p), (WRAPS['pot'], 13, 0, p, INK2)]
    if shout:
        L.append(at('arm_raise_fl', (4, 0), p))
    im, fx, fy = compose(L, foot=(17, 30))
    return im.crop((0, 0, im.width, min(im.height, 34))), fx, 0


def stack(ps, phase=1, k=0, shout=False):
    """The parts stacked the way render_roaster.js does, on the concepts' canvas -> (im, ax, ay)."""
    out = Image.new('RGBA', (B.CW, B.CH), (0, 0, 0, 0))
    order = ['rst_track%d' % k, 'rst_body%d' % phase, ('rst_drumc%d' if phase == 3 else 'rst_drum%d') % k]
    if phase < 3:
        order.append('rst_hopper')
    order.append('rst_chimney' if phase == 1 else 'rst_stub')
    for n in order:
        im, ax, ay = ps[n]
        out.alpha_composite(im, (B.AX - ax, B.AY - ay))
    im, ax, ay = ps['rst_qm%d' % (1 if shout else 0)]
    out.alpha_composite(im, (B.AX + 38 - ax, B.AY - 82 - ay))
    return B.crop(out)


def hero(step, bx=330):
    G = B.GROUND
    shoot = [('yazeed_stand_side_fwd', 128, G), ('fx_muzzle', 128 + 18, G - 23), ('fx_tracer', 198, G - 23), ('fx_tracer', 238, G - 23)]
    return B.scene(stack(parts(step)), bx, shoot)


def phase_sheet(step, w=624, h=180, bg=(16, 20, 44, 255)):
    from PIL import ImageDraw
    ps = parts(step)
    B.SMOKE_AT['_m'] = (53, -66)
    figs = [B.with_smoke('_m', stack(ps, ph), ph) for ph in (1, 2, 3)]
    out = Image.new('RGBA', (w, h), bg)
    g = h - 14
    out.alpha_composite(Image.new('RGBA', (w, 14), (24, 30, 62, 255)), (0, g))
    slot = w // 3
    for i, (im, ax, ay) in enumerate(figs):
        cx = slot * i + slot // 2
        sh = Image.new('RGBA', (110, 6), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse((0, 0, 109, 5), fill=(8, 10, 24, 255))
        out.alpha_composite(sh, (cx - 55, g - 3))
        out.alpha_composite(im, (int(cx - ax), int(g - ay)))
    return out


def plain(step, k=4):
    """The sprite alone at k times, on the canvas's navy, padded so today's and the edits line up on the anchor."""
    im, ax, ay = stack(parts(step)) if step else B.current_roaster()
    W, H = 176, 118
    out = Image.new('RGBA', (W, H), (16, 20, 44, 255))
    out.alpha_composite(im, (100 - ax, 110 - ay))
    return out.resize((W * k, H * k), Image.NEAREST)


if __name__ == '__main__':
    OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'boss_proposals')
    for step in ('light', 'full'):
        plain(step).save(os.path.join(OUT, 'minor_%s_plain.png' % step))
        hero(step).resize((B.VW * 2, B.VH * 2), Image.NEAREST).save(os.path.join(OUT, 'minor_%s_hero.png' % step))
        phase_sheet(step).resize((624 * 3 // 2, 270), Image.NEAREST).save(os.path.join(OUT, 'minor_%s_phases.png' % step))
    plain(None).save(os.path.join(OUT, 'minor_today_plain.png'))
    print('ok')
