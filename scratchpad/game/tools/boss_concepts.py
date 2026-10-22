# boss_concepts.py - proposals for a new look for the Coffee Port's boss (Khaled, 15 Oct: "The boss in Mocha looks
# like a train car, the mechanic of the boss are ok, but can you give proposals of different designs?").
# Same moves as the Big Roaster (bean spray high or low, roast bombs, steam up close, a pour of burning beans along the
# ground, a lunge, two parts shot off, the Quartermaster at the end); three new machines drawn in the game's own way:
# tone fields mapped through colour ramps with the checker dither, light from the upper left, a black line round the
# whole. Coordinates are from the ground under the machine's middle, x negative to the front (it faces left), y up
# negative.
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock'
sys.path.insert(0, MOCK)
sys.path.insert(0, HERE)
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
from paint import Layer, Tone, ramp, poly_mask, light
import props as P
import stage_mocha as SM

CW, CH = 240, 180              # every concept is painted on one canvas this size
AX, AY = 120, 170              # where the ground under its middle falls
YS, XS = np.mgrid[0:CH, 0:CW] + 0.5
LV = np.array([-0.55, -0.62, 0.56])
LV = LV / np.linalg.norm(LV)

KHAKI = ramp(['#140e08', '#2e2214', '#4c3a22', '#6e5634', '#90744a', '#b09062', '#ccae80', '#e2cca4', '#f4e8cc'], 18)
BRASS = ramp(['#160e04', '#342206', '#5a3e0c', '#845e14', '#ae8020', '#d0a232', '#e8c452', '#f6e08a', '#fff6cc'], 18)
OLIVE = P.OLIVE
IRON = SM.IRON
COPPER = SM.COPPER
FIRE = P.FIRE
WOOD = P.WOOD
TYRE = P.TYRE
STEEL = P.STEEL
RED = SM.CLOTH_R
BLUE = SM.CLOTH_B
YEL = SM.CRANE
SACK = SM.SACK
BEAN = SM.BEAN
CREAM = ramp(['#3a3226', '#6a5e4a', '#9a8e74', '#c4baa0', '#e4dcc4', '#f8f4e6'], 10)
TEAL = ramp(['#06181a', '#0c3032', '#14504e', '#1e706a', '#34908a', '#5cb0a6', '#94d0c4'], 12)


def X(x):
    return AX + x


def Y(y):
    return AY + y


# ------------------------------------------------------------------ the brushes
class Machine:
    """Parts painted one over another; each a tone field with its ramp. edge=True rings the part with a dark line where
    it lies over what was painted before (the way Metal Slug draws one plate over another)."""

    def __init__(self):
        self.parts = []

    def part(self, rmp, dither=0.3, edge=True):
        T = Tone(CW, CH)
        self.parts.append([T, rmp, dither, edge])
        return T

    def image(self, im, x, y):
        """A sprite already drawn (a person), put in the stack at (x, y) from the anchor, its own outline kept."""
        self.parts.append([('img', im, X(x), Y(y)), None, 0, False])

    def render(self, outline=True):
        L = Layer(CW, CH)
        below = np.zeros((CH, CW), bool)
        for T, rmp, dth, edge in self.parts:
            if isinstance(T, tuple):
                _, im, ix, iy = T
                arr = np.array(im.convert('RGBA'))
                Li = Layer(arr.shape[1], arr.shape[0])
                Li.rgb = arr[..., :3].copy(); Li.a = arr[..., 3] > 127
                L.paste(Li, int(ix), int(iy))
                sub = np.zeros((CH, CW), bool)
                y0, x0 = max(0, int(iy)), max(0, int(ix))
                y1, x1 = min(CH, int(iy) + Li.h), min(CW, int(ix) + Li.w)
                sub[y0:y1, x0:x1] = Li.a[y0 - int(iy):y1 - int(iy), x0 - int(ix):x1 - int(ix)]
                below |= sub
                continue
            if edge and below.any():
                rim = T.m & ~ndi.binary_erosion(T.m) & below
                T.t = np.where(rim, 0.0, T.t)
            L.paste(T.layer(rmp, dither=dth))
            below |= T.m
        if outline:
            L = P.outlined(L)
        im = L.image()
        return im


def _put(T, m, t):
    T.t = np.where(m, np.clip(t, 0, 1), T.t)
    T.m |= m


def _shade(nx, ny, amb, kd, ks, sh=12):
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    d = np.clip(nx * LV[0] + ny * LV[1] + nz * LV[2], 0, 1)
    return amb + kd * d + ks * d ** sh


def sphere(T, cx, cy, rx, ry, amb=0.16, kd=0.72, ks=0.2, clip=None):
    nx, ny = (XS - X(cx)) / rx, (YS - Y(cy)) / ry
    m = nx * nx + ny * ny <= 1
    if clip is not None:
        m &= clip
    _put(T, m, _shade(nx, ny, amb, kd, ks))
    return m


def tube(T, pts, r, amb=0.16, kd=0.72, ks=0.18, rings=0, ring_t=0.06):
    """A shaded tube along a polyline; r a radius or one per point. rings: a dark band every so many pixels along it."""
    pts = [(X(x), Y(y)) for x, y in pts]
    rs = r if isinstance(r, (list, tuple)) else [r] * len(pts)
    best = np.full((CH, CW), np.inf)
    bnx = np.zeros((CH, CW)); bny = np.zeros((CH, CW)); along = np.zeros((CH, CW))
    run = 0.0
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy or 1e-9
        u = np.clip(((XS - x0) * dx + (YS - y0) * dy) / L2, 0, 1)
        rr = rs[i] + (rs[i + 1] - rs[i]) * u
        ex, ey = XS - (x0 + u * dx), YS - (y0 + u * dy)
        d = np.sqrt(ex * ex + ey * ey) / rr
        b = d < best
        best = np.where(b, d, best)
        bnx = np.where(b, ex / rr, bnx)
        bny = np.where(b, ey / rr, bny)
        along = np.where(b, run + u * np.sqrt(L2), along)
        run += np.sqrt(L2)
    m = best <= 1
    t = _shade(bnx, bny, amb, kd, ks)
    if rings:
        t = np.where((along.astype(int) % rings) == 0, t * 0.45 + ring_t, t)
    _put(T, m, t)
    return m


def plate(T, m, base=0.5, bevel=2.5, k=0.55, vgrad=0.18, y0=None, y1=None, noise_=0.0):
    """A flat plate with rounded edges: lit on its upper left edges, dark on the lower right, a little lighter at the top."""
    d = ndi.distance_transform_edt(m)
    h = np.clip(d / bevel, 0, 1)
    sh = light(h, -0.7, -0.75, k)
    ys = np.where(m)[0]
    if y0 is None and len(ys):
        y0, y1 = ys.min(), ys.max()
    v = (YS - y0) / max(1, (y1 - y0))
    t = base + sh - vgrad * (v - 0.5)
    _put(T, m, t)
    return m


def poly(pts):
    return poly_mask(CW, CH, [(X(x), Y(y)) for x, y in pts])


def ell(cx, cy, rx, ry):
    return ((XS - X(cx)) / rx) ** 2 + ((YS - Y(cy)) / ry) ** 2 <= 1


def superell(cx, cy, a, b, p=3.0):
    return np.abs((XS - X(cx)) / a) ** p + np.abs((YS - Y(cy)) / b) ** p <= 1


def px(T, x, y, t):
    T.px(X(x), Y(y), t)


def line(T, pts, t, w=1):
    T.line([(X(x), Y(y)) for x, y in pts], t, w)


def rivets(T, pts, t=0.9, under=0.15):
    for x, y in pts:
        px(T, x, y, t)
        px(T, x + 1, y + 1, under)


def rot(pts, ang, ox=0.0, oy=0.0):
    c, s = np.cos(ang), np.sin(ang)
    return [(ox + x * c - y * s, oy + x * s + y * c) for x, y in pts]


def bezier(p0, p1, p2, p3, n=10):
    out = []
    for i in range(n + 1):
        u = i / float(n)
        a, b, c, d = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def crop(im, pad=1):
    bb = im.getbbox()
    return im.crop(bb), AX + 1 - bb[0], AY + 1 - bb[1]          # (the outline moved everything one right and down)


# ------------------------------------------------------------------ the people and the props, from the game's own sheet
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


def stencil(T, x0, y0, t):
    for j, row in enumerate(P.SCORPION):
        for i, ch in enumerate(row):
            if ch == '#':
                px(T, x0 + i, y0 + j, t)


def rounded(m, r=2):
    st = ndi.generate_binary_structure(2, 1)
    return ndi.binary_closing(ndi.binary_opening(m, st, iterations=r), st, iterations=1)


CAMO_O = ramp(['#0e1208', '#1e2610', '#33401c', '#4b5a2a', '#66743c', '#82904e'], 10)
CAMO_B = ramp(['#140a06', '#2a160c', '#442614', '#5e381e', '#7a4c2a', '#966238'], 10)


def camo(M, m, seed=1, density=0.42):
    """Desert camouflage: soft blobs of olive and brown over a plate, shaded with it."""
    from paint import noise
    n1 = noise((CH, CW), seed, 7, 4)
    n2 = noise((CH, CW), seed + 9, 6, 5)
    sh = np.clip(1 - (YS - YS[m].min()) / max(1, (YS[m].max() - YS[m].min())), 0, 1) if m.any() else 0
    for nn, rmp, lo in ((n1, np.array(CAMO_O), 0.60), (n2, np.array(CAMO_B), 0.66)):
        mm = m & (nn > lo) & ndi.binary_erosion(m, iterations=2)
        T = M.part(rmp, 0.4, edge=False)
        _put(T, mm, 0.3 + 0.5 * sh)


# ------------------------------------------------------------------ A. the caravan camel
CAMEL_NECK = {
    # where the neck runs from the chest to the poll, and the angle the head is held at (radians, + is nose down)
    'idle': ([(-36, -74), (-50, -77), (-60, -87), (-66, -99), (-68, -105)], -0.12),
    'high': ([(-36, -74), (-52, -72), (-63, -60), (-70, -44), (-74, -32)], 0.0),
    'low': ([(-36, -72), (-50, -64), (-59, -46), (-64, -26), (-67, -10)], -0.06),
    'lunge': ([(-36, -72), (-52, -70), (-64, -62), (-74, -56), (-82, -52)], 0.22),
}


def camel_head(M, ox, oy, ang, phase=1, open_=False, ramp_=None):
    """The head, its local origin at the poll: long muzzle, heavy lidded lamp of an eye, drooping lip, buck teeth,
    a halter with tassels."""
    H = M.part(ramp_ or KHAKI, 0.3)
    hp = [(4, -5), (-2, -8), (-10, -8.5), (-18, -6.5), (-26, -3.5), (-29.5, -0.5), (-31, 3), (-28, 7 if open_ else 6),
          (-22, 6.5), (-12, 5.5), (-2, 6.5), (5, 3)]
    m = poly(rot(hp, ang, ox, oy))
    plate(H, m, base=0.52, bevel=2.2, k=0.6, vgrad=0.22)
    # a plate seam across the face, rivets on the cheek
    line(H, rot([(-15, -6), (-13, 5)], ang, ox, oy), 0.22)
    rivets(H, rot([(-6, 2), (-3, -3), (-19, 1)], ang, ox, oy), 0.86)
    # the mouth, the lip, the teeth
    line(H, rot([(-30, 3), (-20, 4), (-14, 3.5)], ang, ox, oy), 0.05)
    if open_:
        mm = poly(rot([(-31, 3), (-20, 4), (-20, 6), (-29, 7)], ang, ox, oy))
        _put(H, mm, 0.02)
    T = M.part(CREAM, 0, edge=False)
    for q in rot([(-27, 4), (-25, 4)], ang, ox, oy):
        T.rect(X(q[0]), Y(q[1]), X(q[0]) + 1, Y(q[1]) + 1, 0.95)
    # the nostril, with its little vent ring
    N = M.part(BRASS, 0.2, edge=False)
    q = rot([(-24.5, -3)], ang, ox, oy)[0]
    sphere(N, q[0], q[1], 2.0, 1.6, amb=0.3, kd=0.6, ks=0.3)
    px(N, int(round(q[0])), int(round(q[1])), 0.0)
    # the ear
    E = M.part(ramp_ or KHAKI, 0.3)
    q = rot([(-1, -10.5)], ang, ox, oy)[0]
    sphere(E, q[0], q[1], 1.8, 3.0, amb=0.2, kd=0.6)
    # the eye: a lamp, half under a heavy riveted lid
    L_ = M.part(YEL, 0.2, edge=False)
    q = rot([(-9.5, -4)], ang, ox, oy)[0]
    sphere(L_, q[0], q[1], 2.6, 2.6, amb=0.45, kd=0.5, ks=0.5)
    lid = M.part(ramp_ or KHAKI, 0.3, edge=False)
    lm = poly(rot([(-13, -7.5), (-6, -7.5), (-6.5, -4.2), (-12.5, -4.2)], ang, ox, oy))
    plate(lid, lm, base=0.36, bevel=1.2, k=0.4, vgrad=0.1)
    line(lid, rot([(-12.8, -4.2), (-6.2, -4.2)], ang, ox, oy), 0.05)
    # the halter: a red strap round the muzzle and up behind the ear, tassels hanging from the cheek
    R = M.part(RED, 0.2, edge=False)
    line(R, rot([(-21, -5.5), (-20, 5.5)], ang, ox, oy), 0.62, 2)
    line(R, rot([(-20, 0), (-9, 1), (1, -7)], ang, ox, oy), 0.5)
    for i, (rm, tt) in enumerate(((RED, 0.7), (YEL, 0.7), (TEAL, 0.7), (RED, 0.5))):
        Q = M.part(rm, 0, edge=False)
        a = rot([(-16 + i * 2, 4.5), (-16 + i * 2, 9.5 + (i % 2))], ang, ox, oy)
        line(Q, a, tt)
    return m


def camel(pose='idle', phase=1):
    M = Machine()
    neck, ang = CAMEL_NECK[pose]
    dark = dict(amb=0.06, kd=0.46, ks=0.05)
    # ---- the far legs, behind the body
    far = M.part(IRON, 0.25)
    tube(far, [(-24, -56), (-25, -44), (-23, -25), (-26, -6)], [5, 4.4, 3.4, 3.0], **dark)
    tube(far, [(24, -60), (29, -44), (32, -25), (29, -6)], [5.5, 5, 3.6, 3.0], **dark)
    farf = M.part(TYRE, 0.2)
    for fx in (-28, 27):
        sphere(farf, fx, -2.5, 7.5, 3.2, amb=0.1, kd=0.4)
    farj = M.part(BRASS, 0.25)
    for jx, jy in ((-23, -25), (32, -25)):
        sphere(farj, jx, jy, 3.6, 3.6, amb=0.05, kd=0.4, ks=0.1)
    # ---- the tail
    tl = M.part(KHAKI, 0.3)
    tube(tl, [(44, -72), (50, -64), (51, -56)], [2.6, 2.2, 2.0], rings=3)
    tq = M.part(RED, 0.2)
    tube(tq, [(51, -56), (52, -49)], [2.4, 1.6])
    # ---- the body: riveted plate, a deep chest, a tucked belly
    B = M.part(KHAKI, 0.3)
    body = poly([(-34, -85), (-8, -87), (22, -85), (38, -79), (46, -68), (44, -56), (34, -48), (6, -44), (-22, -41), (-40, -47),
                 (-47, -61), (-43, -77)])
    body = rounded(body, 2)
    plate(B, body, base=0.56, bevel=4.5, k=0.62, vgrad=0.42)
    camo(M, body, seed=3)
    B = M.part(KHAKI, 0.3, edge=False)
    for sx in (-22, -6, 10, 26):
        line(B, [(sx, -84), (sx + 1, -45)], 0.24)
    line(B, [(-44, -54), (40, -54)], 0.30)
    rivets(B, [(sx + 2, y) for sx in (-22, -6, 10, 26) for y in (-80, -70, -60)], 0.88)
    rivets(B, [(x, -51) for x in range(-38, 38, 5)], 0.80)
    # the scorpion on the hindquarters
    st = M.part(SM.LIME, 0, edge=False)
    stencil(st, 14, -76, 0.86 if phase == 1 else 0.7)
    # the saddlebag: a coffee sack hanging on the flank, its chute at the foot
    S = M.part(SACK, 0.3)
    sm = rounded(poly([(-33, -79), (-13, -79), (-12, -58), (-17, -53), (-29, -53), (-34, -58)]), 1)
    plate(S, sm, base=0.55, bevel=3, k=0.5, vgrad=0.35)
    for y in (-74, -68, -62):
        line(S, [(-32, y), (-14, y + 1)], 0.36)
    ch = M.part(IRON, 0.2)
    _put(ch, poly([(-27, -53), (-19, -53), (-21, -48), (-25, -48)]), 0.45)
    line(ch, [(-27, -53), (-19, -53)], 0.8)
    # ---- the near legs, over the body
    lg = M.part(IRON, 0.25)
    tube(lg, [(-30, -58), (-32, -44), (-30, -25), (-33, -6)], [5.6, 4.8, 3.6, 3.2])
    tube(lg, [(30, -62), (36, -44), (40, -25), (37, -6)], [6.2, 5.4, 3.8, 3.2])
    pis = M.part(STEEL, 0.2, edge=False)
    line(pis, [(-36, -52), (-35, -32)], 0.85)
    line(pis, [(42, -50), (45, -32)], 0.85)
    ft = M.part(TYRE, 0.2)
    for fx in (-36, 35):
        sphere(ft, fx, -2.6, 8.5, 3.3, amb=0.15, kd=0.55)
    sole = M.part(IRON, 0.2, edge=False)
    for fx in (-36, 35):
        line(sole, [(fx - 7, -5), (fx + 7, -5)], 0.6)
    kn = M.part(BRASS, 0.25)
    for jx, jy in ((-30, -25), (40, -25), (-32, -44), (36, -44)):
        sphere(kn, jx, jy, 4.2, 4.2, amb=0.15, kd=0.66, ks=0.4)
    # ---- the hump: the roaster itself, a copper dome on an iron ring, banded, a mortar cap on top
    ring_ = M.part(IRON, 0.25)
    _put(ring_, superell(5, -84, 25, 3.5, 4), 0.5)
    hump = M.part(COPPER, 0.3)
    hm = ell(5, -84, 23, 26) & (YS < Y(-84))
    sphere(hump, 5, -84, 23, 26, amb=0.12, kd=0.7, ks=0.5, clip=hm)
    bands = M.part(IRON, 0.2, edge=False)
    for bx in (-6, 16):
        bm = hm & (np.abs(XS - X(bx + (5 - bx) * 0.25 * (np.abs(YS - Y(-84)) / 26.0) ** 2)) < 1.1)
        _put(bands, bm, 0.4 + 0.25 * (bx < 0))
    rivets(bands, [(-6, -95), (-6, -88), (16, -95), (16, -88), (5, -106)], 0.9)
    cap = M.part(IRON, 0.25)
    tube(cap, [(5, -108), (5, -114)], 3.4)
    _put(cap, superell(5, -115, 5, 1.6, 4), 0.62)
    if phase >= 3:
        F = M.part(FIRE, 0.2, edge=False)
        for sx, sy, ln, d in ((-8, -100, 12, 1), (10, -104, 14, -1), (0, -92, 10, 1)):
            for i in range(ln):
                xx, yy = sx + i * 0.7 * d, sy + i * 0.9 + 1.5 * np.sin(i * 1.4)
                if hm[int(Y(yy)), int(X(xx))]:
                    px(F, int(xx), int(yy), 0.85)
                    px(F, int(xx) + 1, int(yy), 0.55)
    if phase >= 2:
        sootp = M.part(SM.SOOT, 0.3, edge=False)
        for cx, cy, r in ((-18, -62, 5), (22, -70, 4)) if phase == 3 else ((-18, -62, 4),):
            m_ = ell(cx, cy, r + 2, r) & body
            _put(sootp, m_ & ((XS.astype(int) + YS.astype(int)) % 3 != 0), 0.25)
    # ---- the saddle: the cantle behind him, the quartermaster, then the rug and the pommel in front of him
    wd0 = M.part(WOOD, 0.25)
    tube(wd0, [(-9, -86), (-8, -101)], 2.2)
    sphere(wd0, -8, -102, 2.6, 2.6, amb=0.3, kd=0.6, ks=0.3)
    q, qx, qy = MS_qm(pose in ('low', 'high', 'lunge'))
    M.image(q, -21 - qx, -110)
    rug = M.part(RED, 0.25)
    rm = poly([(-38, -88), (-30, -92), (-14, -92), (-6, -89), (-4, -75), (-8, -71), (-36, -70), (-40, -74)])
    plate(rug, rm, base=0.55, bevel=2, k=0.4, vgrad=0.3)
    for i, x in enumerate(range(-36, -6, 3)):
        line(rug, [(x, -72), (x, -69)], 0.85 if i % 2 else 0.3)
    yl = M.part(YEL, 0, edge=False)
    line(yl, [(-37, -78), (-5, -80)], 0.7)
    line(yl, [(-37, -82), (-5, -84)], 0.5)
    wd = M.part(WOOD, 0.25)
    tube(wd, [(-33, -84), (-34, -98)], 2.2)
    sphere(wd, -34, -99, 2.8, 2.8, amb=0.3, kd=0.6, ks=0.3)
    # ---- the parasol over the saddle (shot away in phase 2: a bent pole and rags)
    if phase == 1:
        pole = M.part(WOOD, 0.2)
        line(pole, [(-20, -88), (-20, -128)], 0.55, 1)
        can = M.part(RED, 0.25)
        cm = ell(-20, -126, 21, 9) & (YS < Y(-125))
        sphere(can, -20, -126, 21, 9, amb=0.3, kd=0.6, ks=0.1, clip=cm)
        cr = M.part(CREAM, 0.2, edge=False)
        for k in range(-3, 4, 2):
            sm_ = cm & (np.abs((XS - X(-20)) - k * 5.6 * (1 - 0.5 * np.clip((Y(-126) - YS) / 9.0, 0, 1))) < 1.6)
            _put(cr, sm_, 0.75)
        fr = M.part(YEL, 0, edge=False)
        for x in range(-40, 1, 3):
            line(fr, [(x, -125), (x + 1, -122)], 0.7)
    else:
        pole = M.part(WOOD, 0.2)
        line(pole, [(-20, -88), (-20, -106), (-15, -112)], 0.5, 1)
        rag = M.part(RED, 0.2)
        line(rag, [(-15, -112), (-12, -106)], 0.5, 1)
        line(rag, [(-15, -112), (-19, -107)], 0.4, 1)
    # ---- the neck: an armoured hose of rings, then the head
    nk = M.part(KHAKI, 0.3)
    tube(nk, neck, [8.5, 7.4, 6.4, 5.8, 5.2], amb=0.18, kd=0.7, ks=0.12, rings=3, ring_t=0.02)
    hx, hy = neck[-1]
    camel_head(M, hx + 1, hy, ang, phase, open_=pose in ('low', 'high'))
    return M


def camel_img(pose='idle', phase=1):
    return crop(camel(pose, phase).render())


def MS_qm(shout=False):
    import mocha_sprites as MSP
    return MSP.roaster_qm(shout)


# ------------------------------------------------------------------ helpers for machines that lean
def to_layer(im):
    arr = np.array(im.convert('RGBA'))
    L = Layer(arr.shape[1], arr.shape[0])
    L.rgb = arr[..., :3].copy()
    L.a = arr[..., 3] > 127
    return L


def outline_img(im):
    return P.outlined(to_layer(im)).image()


def turned(im, deg, pivot):
    """The upper body leant over about a point (anchor coordinates); + is nose down, as it faces left."""
    return im.rotate(deg, resample=Image.NEAREST, center=(X(pivot[0]), Y(pivot[1])))


def stack(*ims):
    out = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    for im in ims:
        out.alpha_composite(im)
    return out


CRAB = ramp(['#160604', '#360c06', '#5c160a', '#862810', '#ae4018', '#cc5e24', '#e48638', '#f4b25c', '#fcdc98'], 18)


# ------------------------------------------------------------------ B. the roasting-pan crab
def crab_pan(phase=1):
    """The roasting pan it carries for a shell, heaped with beans, roasting through: everything that tips."""
    M = Machine()
    # the long handle, behind: up and back, a wooden grip at its end (he steers by it)
    hd = M.part(IRON, 0.25)
    tube(hd, [(42, -62), (58, -72), (68, -86)], [3.0, 2.7, 2.4])
    gr = M.part(WOOD, 0.25)
    tube(gr, [(68, -86), (73, -96)], 3.2, rings=3, ring_t=0.1)
    pan = M.part(IRON, 0.3)
    top = ell(-4, -62, 50, 8)
    bowl = (poly([(-54, -62), (46, -62), (38, -50), (-46, -50)]) | ell(-4, -50, 42, 4.5)) & ~(top & (YS < Y(-62)))
    bowl |= top & (YS >= Y(-62))
    plate(pan, bowl, base=0.36, bevel=3, k=0.5, vgrad=0.5)
    rim = M.part(IRON, 0.2, edge=False)
    _put(rim, ell(-4, -62, 51, 8.5) & ~ell(-4, -62, 48, 6.5), 0.5 + 0.42 * ((YS < Y(-62)) & (XS < X(0))))
    bn = M.part(BEAN, 0.4, edge=False)
    heap = ell(-6, -62, 46, 6) | (ell(-8, -64, 34, 11) & (YS < Y(-60)))
    _put(bn, heap, 0.3 + 0.55 * np.clip(1 - np.abs(XS - X(-18)) / 46.0, 0, 1) * ((XS.astype(int) * 7 + YS.astype(int) * 3) % 5 > 1))
    gl = M.part(FIRE, 0.2, edge=False)
    rr = np.random.default_rng(4)
    for i in range(18 if phase < 3 else 40):
        x = rr.integers(-46, 34); y = rr.integers(-74, -58)
        if heap[int(Y(y)), int(X(x))]:
            px(gl, x, y, 0.55 + 0.35 * rr.random())
    if phase >= 3:
        F = M.part(FIRE, 0.2, edge=False)
        for sx, sy, ln in ((-34, -60, 9), (8, -59, 11)):
            for i in range(ln):
                px(F, int(sx + i * 0.8), int(sy + i * 0.7 + np.sin(i)), 0.9)
    return M


def crab_legs(M, far=False, tip=0):
    """Four chunky legs a side: out of the shell, up to a knee, down to a pointed foot."""
    sh = dict(amb=0.05, kd=0.42, ks=0.05) if far else dict(amb=0.18, kd=0.7, ks=0.3)
    off = 6 if far else 0
    T = M.part(CRAB, 0.3)
    Ft = M.part(CRAB, 0.3)
    legs = [((-26, -34), (-46, -46), (-62, -2)), ((-12, -30), (-28, -44), (-36, -2)),
            ((12, -30), (30, -44), (36, -2)), ((26, -34), (48, -46), (62, -2))]
    for (b, k, f) in legs:
        b, k, f = (b[0] + off, b[1]), (k[0] + off, k[1] + (tip * 4 if b[0] < 0 else 0)), (f[0] + off, f[1])
        tube(T, [b, k], [5.0, 4.4], **sh)
        sphere(T, k[0], k[1], 4.6, 4.6, **sh)
        mid = (k[0] + (f[0] - k[0]) * 0.55, k[1] + (f[1] - k[1]) * 0.55)
        tube(T, [k, mid], [4.2, 3.6], **sh)
        sphere(T, mid[0], mid[1], 3.6, 3.6, **sh)
        tube(Ft, [mid, f], [3.4, 1.0], **sh)
        if not far:
            px(Ft, int(mid[0] + (f[0] - mid[0]) * 0.4) - 1, int(mid[1] + (f[1] - mid[1]) * 0.4), 0.95)


def crab_shell(M, phase=1):
    """Its own shell under the pan: a red carapace, the brazier's vents glowing along its side, the grille it blows
    hot smoke out of at the front, the quartermaster's seat at the back."""
    S = M.part(CRAB, 0.3)
    shell = ell(-4, -40, 47, 17)
    sphere(S, -4, -46, 48, 24, amb=0.14, kd=0.7, ks=0.35, clip=shell)
    for sx in (-30, -12, 8, 26):
        line(S, [(sx, -55), (sx + 3, -26)], 0.18)
    rivets(S, [(x, -52) for x in range(-40, 36, 6)], 0.92)
    rivets(S, [(x, -27) for x in range(-36, 32, 7)], 0.6)
    V = M.part(FIRE, 0.25, edge=False)
    for vx in (-22, -4, 14):
        _put(V, poly([(vx, -42), (vx + 10, -42), (vx + 9, -36), (vx + 1, -36)]), 0.62 + (0.25 if phase >= 3 else 0))
    Vb = M.part(IRON, 0, edge=False)
    for vx in (-22, -4, 14):
        for y in (-41, -39, -37):
            line(Vb, [(vx + 1, y), (vx + 9, y)], 0.22)
    # the face: mouthparts as a grille, the hot smoke comes out between its bars
    G = M.part(IRON, 0.25)
    gm = poly([(-52, -46), (-42, -48), (-40, -30), (-50, -30)])
    plate(G, gm, base=0.4, bevel=1.5, k=0.5, vgrad=0.2)
    for y in range(-45, -31, 3):
        line(G, [(-51, y), (-41, y - 1)], 0.08)
    sc = M.part(SM.LIME, 0, edge=False)
    stencil(sc, 22, -50, 0.85 if phase == 1 else 0.7)
    if phase >= 2:
        sm_ = M.part(SM.SOOT, 0.3, edge=False)
        for cx, cy, r in ((-26, -48, 5), (12, -34, 4)) if phase == 3 else ((-26, -48, 4),):
            _put(sm_, ell(cx, cy, r + 2, r) & shell & ((XS.astype(int) + YS.astype(int)) % 3 != 0), 0.22)


def crab_claw(M, phase=1, pose='idle'):
    if phase >= 2:                                   # shot off: a sparking stump
        T = M.part(CRAB, 0.3)
        tube(T, [(-40, -38), (-54, -42)], [5.0, 4.4])
        S = M.part(FIRE, 0, edge=False)
        for dx, dy in ((-58, -44), (-59, -40), (-57, -38), (-60, -42), (-61, -45)):
            px(S, dx, dy, 0.9)
        return
    T = M.part(CRAB, 0.3)
    low = pose == 'low'
    cx, cy = (-82, -40) if not low else (-80, -16)
    tube(T, [(-40, -38), (-58, -46), (cx + 10, cy)], [5.4, 5.0, 5.0])
    sphere(T, -58, -46, 5.4, 5.4, amb=0.2, kd=0.7, ks=0.35)
    C = M.part(CRAB, 0.3)
    sphere(C, cx + 9, cy, 13, 10, amb=0.18, kd=0.72, ks=0.4)                 # the palm of the claw
    upper = poly([(cx + 2, cy - 9), (cx - 18, cy - 9), (cx - 24, cy - 4), (cx - 14, cy - 2), (cx + 2, cy - 1)])
    lower = poly([(cx + 2, cy + 2), (cx - 15, cy + 3), (cx - 20, cy + 8), (cx - 10, cy + 9), (cx + 2, cy + 8)])
    plate(C, upper | lower, base=0.62, bevel=2.2, k=0.6, vgrad=0.4)
    teeth = M.part(CREAM, 0, edge=False)
    for i in range(5):
        px(teeth, cx - 3 - i * 3, cy - 1, 0.9)
        px(teeth, cx - 2 - i * 3, cy + 3, 0.85)
    rivets(C, [(cx + 6, cy - 4), (cx + 12, cy + 2)], 0.95)


def crab(pose='idle', phase=1):
    tip = 1 if pose == 'tip' else 0
    back = Machine()
    crab_legs(back, far=True)
    # the far claw holds the stirring paddle: up over the pan, or swung down and forward to flick
    pa = back.part(WOOD, 0.25)
    if pose == 'high':
        tube(pa, [(-30, -50), (-52, -40), (-72, -34)], [2.4, 2.2, 2.0])
        _put(pa, rounded(poly([(-72, -40), (-88, -41), (-89, -29), (-72, -28)]), 1), 0.6)
    else:
        tube(pa, [(-30, -52), (-40, -76), (-46, -96)], [2.4, 2.2, 2.0])
        _put(pa, rounded(poly([(-53, -112), (-40, -114), (-40, -97), (-53, -96)]), 1), 0.6)
    fc = back.part(CRAB, 0.3)
    tube(fc, [(-30, -46), (-32, -54)], 4.0, amb=0.05, kd=0.42)
    up = back.render(outline=False)
    body = Machine()
    crab_shell(body, phase)
    # the seat at the back: he sits on it and steers by the pan's handle
    q, qx, qy = MS_qm(pose in ('high', 'low', 'tip'))
    body.image(q, 34 - qx, -92)
    seat = body.part(WOOD, 0.25)
    _put(seat, rounded(poly([(24, -70), (46, -70), (46, -64), (24, -64)]), 1), 0.55)
    tube(seat, [(46, -64), (48, -84)], 2.2)
    shell = body.render(outline=False)
    pan = crab_pan(phase).render(outline=False)
    if tip:
        pan = turned(pan, 16, (-52, -52))
    front = Machine()
    crab_legs(front, far=False, tip=tip)
    # the eyes on their stalks, goggling over the claw
    st = front.part(CRAB, 0.3)
    tube(st, [(-40, -50), (-44, -62), (-46, -72)], [2.2, 2.0, 1.8])
    tube(st, [(-32, -54), (-33, -66), (-35, -76)], [2.2, 2.0, 1.8])
    ey = front.part(YEL, 0.2)
    sphere(ey, -46, -75, 4.0, 4.0, amb=0.4, kd=0.5, ks=0.6)
    sphere(ey, -35, -79, 4.0, 4.0, amb=0.4, kd=0.5, ks=0.6)
    pu = front.part(IRON, 0, edge=False)
    px(pu, -48, -75, 0.02); px(pu, -37, -79, 0.02)
    crab_claw(front, phase, pose)
    fr = front.render(outline=False)
    return outline_img(stack(up, pan, shell, fr))


def crab_img(pose='idle', phase=1):
    return crop(crab(pose, phase))


# ------------------------------------------------------------------ C. the dallah walker
def dallah_legs(M, far=False, crouch=0.0):
    """Two bird legs: the hip up under the pot, the joint bent backward, three claws forward and a spur behind."""
    sh = dict(amb=0.05, kd=0.42, ks=0.05) if far else dict(amb=0.18, kd=0.7, ks=0.3)
    off = 9 if far else -5
    T = M.part(IRON, 0.25)
    J = M.part(BRASS, 0.25)
    Ft = M.part(STEEL, 0.25)
    hip = (off, -60 + 12 * crouch)
    knee = (off + 17, -38 + 9 * crouch)
    ank = (off + 3, -11)
    tube(T, [hip, knee], [7.0, 5.6], **sh)
    tube(T, [knee, ank], [4.6, 3.6], **sh)
    if not far:
        P_ = M.part(STEEL, 0.2, edge=False)
        line(P_, [(hip[0] + 4, hip[1] + 2), (knee[0] + 2, knee[1] - 4)], 0.85)
    sphere(J, knee[0], knee[1], 5.6, 5.6, **sh)
    sphere(J, ank[0], ank[1], 3.8, 3.8, **sh)
    for dx, dy, r0 in ((-14, -1, 2.6), (-9, 0, 2.4), (-4, 0, 2.2)):
        tube(Ft, [ank, (ank[0] + dx, ank[1] + 8 + dy)], [2.8, 1.0], **sh)
    tube(Ft, [ank, (ank[0] + 7, ank[1] + 8)], [2.2, 0.8], **sh)


DS, DY = 1.12, -5            # the pot a size bigger than first drawn, and up on longer legs (its finial clear of the HUD)


def D(x, y):
    return (x * DS, -50 + DY + (y + 50) * DS)


def Dp(pts):
    return [D(x, y) for x, y in pts]


def dallah_pot(phase=1, lid='peek', pose='idle'):
    """The coffee pot: a flared foot, a round brass belly with engraved bands, the waist, the stepped lid with its
    finial, the long beak of a spout, the handle at the back."""
    M = Machine()
    s = DS
    # the handle, behind the belly
    hd = M.part(BRASS, 0.25)
    tube(hd, Dp(bezier((8, -106), (34, -110), (40, -84), (24, -66), 10)), 3.0 * s, amb=0.12, kd=0.66, ks=0.4)
    # the foot ring
    ft = M.part(BRASS, 0.3)
    fm = poly(Dp([(-26, -50), (26, -50), (22, -57), (-22, -57)]))
    plate(ft, fm, base=0.5, bevel=2, k=0.6, vgrad=0.4)
    rivets(ft, [D(x, -53) for x in range(-20, 22, 5)], 0.95)
    # the spout: a long brass beak from low on the belly, curving up to its lipped mouth
    sp = M.part(BRASS, 0.3)
    path = Dp(bezier((-20, -66), (-44, -64), (-52, -84), (-60, -104), 12))
    tube(sp, path, list(np.linspace(6.0 * s, 3.0 * s, len(path))), amb=0.14, kd=0.7, ks=0.45)
    tip = path[-1]
    sphere(sp, tip[0] - 1, tip[1] - 1, 4.2 * s, 3.0 * s, amb=0.2, kd=0.7, ks=0.5)
    mo = M.part(SM.SOOT, 0, edge=False)
    _put(mo, ell(tip[0] - 2, tip[1] - 2, 2.4, 1.5), 0.1)
    # the belly
    B = M.part(BRASS, 0.3)
    bc = D(0, -76)
    bm = ell(bc[0], bc[1], 29 * s, 23 * s)
    sphere(B, bc[0], bc[1] - 2, 31 * s, 26 * s, amb=0.12, kd=0.68, ks=0.55, clip=bm)
    # engraved bands: rows of little marks round the belly, following its curve
    E = M.part(BRASS, 0, edge=False)
    for by in (-86, -68):
        for x in range(-26, 28, 3):
            u = x / 29.0
            q = D(x, by + 3.0 * (1 - u * u) * (1 if by > -76 else -1) * 0.6)
            if bm[int(Y(q[1])), int(X(q[0]))]:
                px(E, int(q[0]), int(q[1]), 0.18)
                px(E, int(q[0]) + 1, int(q[1]) + 1, 0.12)
        for x in range(-24, 26, 6):
            u = x / 29.0
            q = D(x, by - 2 + 3.0 * (1 - u * u) * (1 if by > -76 else -1) * 0.6)
            if bm[int(Y(q[1])), int(X(q[0]))]:
                px(E, int(q[0]), int(q[1]), 0.25)
    # the militia's scorpion, and a pressure gauge
    sc = M.part(SM.LIME, 0, edge=False)
    q = D(-10, -82)
    stencil(sc, int(q[0]), int(q[1]), 0.9 if phase == 1 else 0.72)
    G = M.part(CREAM, 0.1)
    q = D(14, -64)
    sphere(G, q[0], q[1], 4.4, 4.4, amb=0.5, kd=0.4, ks=0.3)
    Gn = M.part(IRON, 0, edge=False)
    line(Gn, [q, (q[0] + 2, q[1] - 2)], 0.05)
    # the waist, then the lid
    W_ = M.part(BRASS, 0.3)
    wm = poly(Dp([(-14, -100), (14, -100), (9, -108), (-9, -108)]))
    nx = np.clip((XS - X(0)) / (14.0 * s), -1, 1)
    _put(W_, wm, _shade(nx, np.zeros_like(nx), 0.14, 0.7, 0.4))
    rimL = M.part(BRASS, 0.25)
    rc = D(0, -109)
    _put(rimL, superell(rc[0], rc[1], 12 * s, 2.4, 4), 0.72)
    if phase >= 2:
        # the lid is gone: he stands in the open neck, the pot boiling round him
        q_, qx, qy = MS_qm(True)
        M.image(q_, -qx + 1, rc[1] - 20)
        fr = M.part(BRASS, 0.25)
        _put(fr, superell(rc[0], rc[1], 12 * s, 2.4, 4), 0.62)
        st = M.part(CREAM, 0.35, edge=False)
        for k_, (sx, sy) in enumerate(((-13, -6), (12, -8), (-9, -13), (15, -15))):
            for j in range(5):
                px(st, int(rc[0] + sx + np.sin(j * 1.3 + k_) * 1.6), int(rc[1] + sy - j * 2), 0.75 - 0.08 * j)
                px(st, int(rc[0] + sx + 1 + np.sin(j * 1.3 + k_) * 1.6), int(rc[1] + sy - j * 2), 0.6 - 0.08 * j)
    else:
        # the lid, lifted a crack on its hinge at the back: under it, his eyes
        lift = 5 if lid == 'peek' else 12
        q_, qx, qy = MS_qm(False)
        qc = q_.crop((0, 0, q_.width, 12))
        M.image(qc, -qx + 1, rc[1] - 9)
        L = M.part(BRASS, 0.3)
        lidm = poly([(x, y - lift) for x, y in Dp([(-13, -111), (13, -110), (11, -114), (-11, -115)])])
        plate(L, lidm, base=0.6, bevel=1.5, k=0.6, vgrad=0.4)
        dc = D(0, -115)
        dome = ell(dc[0], dc[1] - lift, 10 * s, 8 * s) & (YS < Y(dc[1] - lift))
        sphere(L, dc[0], dc[1] - lift, 10 * s, 8 * s, amb=0.15, kd=0.7, ks=0.55, clip=dome)
        fi = M.part(BRASS, 0.25)
        fc = D(0, -125)
        sphere(fi, fc[0], fc[1] - lift, 3.4, 3.4, amb=0.2, kd=0.7, ks=0.6)
        tube(fi, [(fc[0], fc[1] - lift - 3), (fc[0], fc[1] - lift - 7)], [1.8, 0.6])
        hinge = M.part(IRON, 0, edge=False)
        h0 = D(10, -111)
        line(hinge, [h0, (h0[0] + 2, h0[1] - lift)], 0.5)
    if phase >= 3:
        F = M.part(FIRE, 0.2, edge=False)
        for sx, sy, ln, d in ((-16, -88, 13, 1), (6, -92, 15, -1), (-2, -70, 10, 1)):
            for i in range(ln):
                q = D(sx + i * 0.7 * d, sy + i * 0.9 + 1.5 * np.sin(i * 1.3))
                if bm[int(Y(q[1])), int(X(q[0]))]:
                    px(F, int(q[0]), int(q[1]), 0.88)
                    px(F, int(q[0]) + 1, int(q[1]), 0.6)
        dn = M.part(SM.SOOT, 0.3, edge=False)
        q = D(18, -82)
        _put(dn, ell(q[0], q[1], 7, 5) & bm & ((XS.astype(int) + YS.astype(int)) % 3 != 0), 0.25)
    # exhausts at the back of the foot, puffing
    ex = M.part(IRON, 0.25)
    tube(ex, Dp([(20, -56), (30, -60)]), 2.4)
    tube(ex, Dp([(18, -54), (29, -54)]), 2.2)
    return M


DALLAH_POSE = {'idle': (0, 0), 'high': (62, 0), 'low': (65, 2.0), 'pour': (60, 1.0)}     # (lean in degrees, crouch): spout at 31, 7, 23 over the ground


def dallah(pose='idle', phase=1):
    lean, crouch = DALLAH_POSE.get(pose, (0, 0))
    back = Machine()
    dallah_legs(back, far=True, crouch=crouch)
    bk = back.render(outline=False)
    pot = dallah_pot(phase, lid='open' if pose in ('high', 'low') else 'peek', pose=pose).render(outline=False)
    drop = int(round(10 * crouch))
    if drop:
        sh = Image.new('RGBA', pot.size, (0, 0, 0, 0)); sh.alpha_composite(pot, (0, drop)); pot = sh
    if lean:
        pot = turned(pot, lean, (-6, -58 + drop))
    front = Machine()
    dallah_legs(front, far=False, crouch=crouch)
    fr = front.render(outline=False)
    return outline_img(stack(bk, pot, fr))


def dallah_img(pose='idle', phase=1):
    return crop(dallah(pose, phase))


# ------------------------------------------------------------------ the lighthouse yard, as the game draws it at the fight
VW, VH, GROUND = 468, 216, 184
CAM = 3776                                         # (where the screen holds for the fight, 468 wide)


def arena(cam=CAM):
    import json
    st = json.load(open(os.path.join(GAME, 'gen/stage_mocha.json')))
    ly = st['layers']
    out = Image.new('RGBA', (VW, VH), (0, 0, 0, 255))
    img = lambda n: Image.open(os.path.join(GAME, 'art/out', n + '.png')).convert('RGBA')

    def wrap(l):
        im = img(l['img']); x = int(np.floor(cam * l['par'])) % l['w']
        w1 = min(VW, l['w'] - x)
        out.alpha_composite(im.crop((x, 0, x + w1, l['h'])), (0, l['y']))
        if w1 < VW:
            out.alpha_composite(im.crop((0, 0, VW - w1, l['h'])), (w1, l['y']))

    def strips(l):
        x0 = int(round(cam * l['par']))
        for s in l['strips']:
            end = s.get('until', s['x'] + s['w'])
            if end <= x0 or s['x'] >= x0 + VW:
                continue
            im = img(s['img'])
            k = max(0, (x0 - s['x']) // s['w']) if 'until' in s else 0
            tx = s['x'] + k * s['w']
            while tx < end and tx < x0 + VW:
                a, b = max(0, x0 - tx), min(s['w'], end - tx, x0 + VW - tx)
                if b > a:
                    out.alpha_composite(im.crop((a, 0, b, s['h'])), (tx + a - x0, s['y']))
                tx += s['w']
    wrap(ly['sky']); wrap(ly['sea']); wrap(ly['far']); strips(ly['play'])
    return out, (lambda o: strips(ly['fore']) or o)


def put(scene, name_or_img, x, y, anchor=None):
    if isinstance(name_or_img, str):
        im, ax, ay = frame(name_or_img)
    else:
        im, (ax, ay) = name_or_img, anchor
    scene.alpha_composite(im, (int(x - ax), int(y - ay)))


def scene(boss, bx, extras=(), fore=True):
    """The yard with the machine standing at bx (screen x of its middle), Yazeed and whatever is flying added."""
    sc, _ = arena()
    im, ax, ay = boss
    for e in extras:
        if e[0] == 'under':
            put(sc, *e[1:])
    sc.alpha_composite(im, (int(bx - ax), int(GROUND - ay)))
    for e in extras:
        if e[0] != 'under':
            put(sc, *e)
    if fore:
        import json
        st = json.load(open(os.path.join(GAME, 'gen/stage_mocha.json')))
        l = st['layers']['fore']
        x0 = int(round(CAM * l['par']))
        for s in l['strips']:
            end = s.get('until', s['x'] + s['w'])
            if end <= x0 or s['x'] >= x0 + VW:
                continue
            fim = Image.open(os.path.join(GAME, 'art/out', s['img'] + '.png')).convert('RGBA')
            a, b = max(0, x0 - s['x']), min(s['w'], end - s['x'], x0 + VW - s['x'])
            sc.alpha_composite(fim.crop((a, 0, b, s['h'])), (s['x'] + a - x0, s['y']))
    return sc


def current_roaster():
    """The Big Roaster as it stands in build 14, stacked from its parts the way render_roaster.js does."""
    out = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    for n in ('rst_track0', 'rst_body1', 'rst_drum0', 'rst_hopper', 'rst_chimney'):
        im, ax, ay = frame(n)
        out.alpha_composite(im, (AX - ax, AY - ay))
    im, ax, ay = frame('rst_qm0')
    out.alpha_composite(im, (AX + 38 - ax, AY - 82 - ay))
    return crop(out)


def zoom(im, k=3):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


# ------------------------------------------------------------------ the boards: a hero shot, two moves, three phases
def dallah_tip(pose):
    lean, crouch = DALLAH_POSE.get(pose, (0, 0))
    drop = int(round(10 * crouch))
    path = Dp(bezier((-20, -66), (-44, -64), (-52, -84), (-60, -104), 12))
    tx, ty = path[-1][0] - 1, path[-1][1] - 1 + drop
    px_, py_ = -6, -58 + drop
    th = np.radians(lean)
    dx, dy = tx - px_, ty - py_
    return (px_ + dx * np.cos(th) + dy * np.sin(th), py_ - dx * np.sin(th) + dy * np.cos(th))


def beans_line(x0, y0, x1, n=6, hot=True, jitter=1.5, seed=1):
    r = np.random.default_rng(seed)
    out = []
    for i in range(n):
        u = (i + 0.5) / n
        out.append(('fx_bean_hot' if (hot and i % 2 == 0) else 'fx_bean', x0 + (x1 - x0) * u, y0 + r.uniform(-jitter, jitter)))
    return out


def board(concept, bx=330):
    """[(label, image)] for one concept: the hero shot, the high spray and how to dodge it, the low one (or the pour) and
    how to dodge it, and the three phases side by side."""
    G = GROUND
    shoot = [('yazeed_stand_side_fwd', 128, G), ('fx_muzzle', 128 + 18, G - 23), ('fx_tracer', 198, G - 23), ('fx_tracer', 238, G - 23)]
    duck = [('yazeed_crouch_side_fwd', 128, G)]
    hop = [('yazeed_jump_side_fwd', 128, G - 36)]
    out = []
    if concept == 'camel':
        img = camel_img
        out.append(('hero', scene(img('idle', 1), bx, shoot)))
        out.append(('high', scene(img('high', 1), bx, duck + beans_line(bx - 108, G - 29, 150, 6, seed=2))))
        out.append(('low', scene(img('low', 1), bx, hop + beans_line(bx - 101, G - 5, 110, 7, seed=3))))
    elif concept == 'crab':
        img = crab_img
        out.append(('hero', scene(img('idle', 1), bx, shoot)))
        out.append(('high', scene(img('high', 1), bx, duck + beans_line(bx - 92, G - 31, 152, 6, seed=4))))
        wave = [('under', 'fx_pour0', x, G) for x in range(bx - 150, bx - 60, 12)]
        fall = [('fx_bean_hot', bx - 66 + dx, G - 30 + dy) for dx, dy in ((0, 0), (-3, 8), (2, 14), (-2, 20))]
        out.append(('low', scene(img('tip', 1), bx, hop + wave + fall)))
    elif concept == 'dallah':
        img = dallah_img
        out.append(('hero', scene(img('idle', 1), bx, shoot)))
        tx, ty = dallah_tip('high')
        out.append(('high', scene(img('high', 1), bx, duck + beans_line(bx + tx - 6, G + ty, 150, 6, seed=5))))
        tx, ty = dallah_tip('pour')
        stream = [('fx_bean_hot' if i % 2 else 'fx_bean', bx + tx - 2 + (i % 2), G + ty + 3 + i * 4) for i in range(int((-ty - 4) / 4))]
        wave = [('under', 'fx_pour0' if i % 2 else 'fx_pour1', x, G) for i, x in enumerate(range(bx + int(tx) - 100, bx + int(tx) - 4, 12))]
        out.append(('low', scene(img('pour', 1), bx, hop + wave + stream)))
    elif concept == 'now':
        out.append(('hero', scene(current_roaster(), bx, shoot)))
    if concept != 'now':
        # the three phases, on a strip of the yard
        strip = Image.new('RGBA', (VW, VH), (0, 0, 0, 0))
        bg, _ = arena()
        strip.alpha_composite(bg)
        for i, ph in enumerate((1, 2, 3)):
            im, ax, ay = img('idle', ph)
            k = 0.62
            sm = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.NEAREST)
            strip.alpha_composite(sm, (int(78 + i * 156 - ax * k), int(G - ay * k)))
        out.append(('phases', strip))
    return out


SMOKE_AT = {'camel': (5, -116), 'crab': (-12, -78), 'dallah': (38, -68)}


def with_smoke(concept, boss, phase):
    """Phase 2 smokes a little, phase 3 a lot: a column of the game's black puffs from the hurt part."""
    im, ax, ay = boss
    if phase < 2:
        return boss
    pad = 40
    out = Image.new('RGBA', (im.width + pad * 2, im.height + pad), (0, 0, 0, 0))
    out.alpha_composite(im, (pad, pad))
    sx, sy = SMOKE_AT[concept]
    x0, y0 = ax + pad + sx, ay + pad + sy
    puffs = [('fx_bsmoke1', 0, 0), ('fx_bsmoke2', -2, -8), ('fx_bsmoke2', 2, -18)] if phase == 2 else \
            [('fx_bsmoke1', 0, 0), ('fx_bsmoke2', -3, -7), ('fx_bsmoke2', 3, -15), ('fx_bsmoke2', -1, -25), ('fx_bsmoke1', 4, -34), ('fx_bsmoke0', 1, -41)]
    for n, dx, dy in puffs:
        f, fx, fy = frame(n)
        out.alpha_composite(f, (int(x0 + dx - fx), int(y0 + dy - fy)))
    bb = out.getbbox()
    return out.crop(bb), ax + pad - bb[0], ay + pad - bb[1]


def phase_sheet(concept, w=640, h=196, bg=(16, 20, 44, 255)):
    img = {'camel': camel_img, 'crab': crab_img, 'dallah': dallah_img}[concept]
    figs = [with_smoke(concept, img('idle', ph), ph) for ph in (1, 2, 3)]
    out = Image.new('RGBA', (w, h), bg)
    g = h - 14
    band = Image.new('RGBA', (w, 14), (24, 30, 62, 255))
    out.alpha_composite(band, (0, g))
    slot = w // 3
    for i, (im, ax, ay) in enumerate(figs):
        cx = slot * i + slot // 2
        # (a soft shadow under it)
        sh = Image.new('RGBA', (110, 6), (0, 0, 0, 0))
        from PIL import ImageDraw
        ImageDraw.Draw(sh).ellipse((0, 0, 109, 5), fill=(8, 10, 24, 255))
        out.alpha_composite(sh, (cx - 55, g - 3))
        out.alpha_composite(im, (int(cx - ax + (im.width / 2 - ax) * 0 ), int(g - ay)))
    return out
