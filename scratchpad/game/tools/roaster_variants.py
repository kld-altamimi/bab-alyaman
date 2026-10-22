# roaster_variants.py - the Big Roaster kept, the train taken out of it (Khaled, 16 Oct: "Let's get back to the same
# design in the current build, can you give me options of the design that make it less confusing for a train?").
# What reads as a locomotive in build 14: the copper drum lying lengthwise like a boiler, the tall chimney, the cab at
# the back with the driver in it, the plough at the front like a cowcatcher, and a flat row of wheels like a bogie.
# Three variants, smallest change first; the moves stay where the game has them: the high spray and the low one leave
# the front at 31 and 7 dots over the ground (R.HIGH, R.LOW at R.SPOUT's x), the steam at the grille, the pour at the
# chute. Drawn with boss_concepts' brushes, in the build's palette.
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image
import boss_concepts as B
from boss_concepts import (Machine, sphere, tube, plate, poly, ell, superell, px, line, rivets, stencil, rounded, crop,
                           _put, XS, YS, X, Y, MS_qm, camo, OLIVE, IRON, COPPER, BRASS, FIRE, STEEL, TYRE, YEL, CREAM, BEAN)
import stage_mocha as SM
import props as P

HAZ = SM.CRANE


# ------------------------------------------------------------------ the chassis every variant stands on
def tracks(M, k=0):
    """A tank's running gear, not a bogie: five big road wheels, the idler raised at the front, a toothed sprocket at
    the back, return rollers along the top run, the track a trapezoid round them."""
    T = M.part(IRON, 0.25)
    loop = [(-46, -1), (44, -1), (54, -8), (56, -13), (52, -18), (-50, -21), (-58, -15), (-56, -9), (-46, -1)]
    tube(T, loop, 2.6, amb=0.1, kd=0.55, ks=0.1)
    # the links: a dark tooth every few dots along the bottom run and the top run
    L_ = M.part(IRON, 0, edge=False)
    for x in range(-44, 46, 4):
        px(L_, x + (k % 2) * 2, -1, 0.05)
    for x in range(-48, 52, 4):
        yy = -21 + (x + 48) * (3.0 / 100)
        px(L_, x + (k % 2) * 2, int(round(yy)), 0.08)
    W = M.part(IRON, 0.25)
    for wx in (-36, -18, 0, 18, 36):
        sphere(W, wx, -8, 6.6, 6.6, amb=0.14, kd=0.6, ks=0.2)
    sphere(W, -51, -14, 5.2, 5.2, amb=0.14, kd=0.6, ks=0.2)                      # the idler, up at the front
    sphere(W, 50, -12, 6.0, 6.0, amb=0.14, kd=0.6, ks=0.2)                       # the sprocket
    H = M.part(STEEL, 0.2, edge=False)
    for wx in (-36, -18, 0, 18, 36):
        sphere(H, wx, -8, 2.4, 2.4, amb=0.4, kd=0.5, ks=0.4)
    sphere(H, -51, -14, 2.0, 2.0, amb=0.4, kd=0.5, ks=0.4)
    for a in range(0, 360, 45):
        ang = np.radians(a + k * 15)
        px(H, int(round(50 + 5.6 * np.cos(ang))), int(round(-12 + 5.6 * np.sin(ang))), 0.9)
    sphere(H, 50, -12, 2.2, 2.2, amb=0.4, kd=0.5, ks=0.4)
    R_ = M.part(IRON, 0.2)
    for rx in (-26, 8, 32):
        sphere(R_, rx, -20, 2.6, 2.6, amb=0.2, kd=0.6, ks=0.2)


def hull(M, phase=1, glacis=True):
    """Olive plate: a sloped glacis at the front with the bow gun and the grille in it, side skirts over the top of
    the tracks with their bolts, the scorpion stencilled on them, desert camouflage."""
    T = M.part(OLIVE, 0.35)
    hm = poly([(-58, -20), (-46, -40), (48, -40), (56, -34), (56, -18), (-58, -18)])
    plate(T, hm, base=0.5, bevel=3, k=0.6, vgrad=0.4)
    line(T, [(-46, -40), (-58, -21)], 0.85)                                       # the glacis edge, lit
    camo(M, hm, seed=11)
    S = M.part(OLIVE, 0.3)
    sk = rounded(poly([(-50, -30), (54, -30), (54, -17), (-50, -17)]), 1)
    plate(S, sk, base=0.42, bevel=2, k=0.5, vgrad=0.3)
    for x in range(-48, 54, 13):
        line(S, [(x, -30), (x, -17)], 0.2)
    rivets(S, [(x + 3, y) for x in range(-48, 54, 13) for y in (-28, -20)], 0.85)
    sc = M.part(SM.LIME, 0, edge=False)
    stencil(sc, 10, -31, 0.86 if phase == 1 else 0.7)
    # the bow gun (the high spray: 31 over the ground) and the grille under it (the steam)
    G = M.part(IRON, 0.25)
    tube(G, [(-50, -31), (-60, -31)], 2.2, amb=0.2, kd=0.6, ks=0.3)
    sphere(G, -50, -31, 3.6, 3.6, amb=0.2, kd=0.6, ks=0.3)
    gm = poly([(-56, -24), (-50, -24), (-50, -14), (-56, -14)])
    _put(G, gm, 0.4)
    for y in range(-23, -14, 2):
        line(G, [(-56, y), (-51, y)], 0.12)
    # the chute at the foot of the glacis (the low spray and the pour: 7 over the ground)
    C = M.part(IRON, 0.25)
    _put(C, poly([(-62, -11), (-52, -11), (-52, -5), (-63, -5)]), 0.35)
    line(C, [(-63, -11), (-52, -11)], 0.75)
    if phase >= 2:
        sm_ = M.part(SM.SOOT, 0.3, edge=False)
        for cx, cy, r in ((-24, -34, 5), (24, -26, 4)) if phase == 3 else ((-24, -34, 4),):
            _put(sm_, ell(cx, cy, r + 2, r) & (hm | sk) & ((XS.astype(int) + YS.astype(int)) % 3 != 0), 0.22)


def blade(M):
    """A dozer blade instead of the plough: curved, hazard-striped, on two push arms."""
    A = M.part(IRON, 0.25)
    tube(A, [(-50, -14), (-62, -10)], 2.0)
    T = M.part(IRON, 0.25)
    bm = poly([(-74, -1), (-70, -20), (-64, -24), (-62, -21), (-66, -12), (-66, -1)])
    plate(T, bm, base=0.5, bevel=2, k=0.6, vgrad=0.3)
    Hz = M.part(HAZ, 0, edge=False)
    for y in range(-19, -2):
        x0 = -70 + (y + 20) * 0.2
        px(Hz, int(x0), y, 0.9 if (y // 3) % 2 else 0.12)
        px(Hz, int(x0) + 1, y, 0.9 if (y // 3) % 2 else 0.12)


def cupola(M, x, y, shout=False, lid=True):
    """A commander's hatch with him in it, head and shoulders out, its lid standing open behind him."""
    if lid:
        Ld = M.part(OLIVE, 0.3)
        sphere(Ld, x + 9, y - 9, 3.0, 8.0, amb=0.15, kd=0.6, ks=0.2)
    q, qx, qy = MS_qm(shout)
    M.image(q, x - qx, y - 20)
    R_ = M.part(IRON, 0.25)
    _put(R_, superell(x, y, 10, 2.6, 4), 0.55)
    rivets(R_, [(x - 7, y), (x, y + 1), (x + 7, y)], 0.9)


def exhausts(M, phase=1):
    E = M.part(IRON, 0.25)
    if phase == 1:
        tube(E, [(42, -40), (50, -50)], 2.4, amb=0.15, kd=0.6, ks=0.25)
        tube(E, [(47, -40), (55, -48)], 2.2, amb=0.1, kd=0.5, ks=0.2)
        _put(E, ell(50, -51, 3, 1.5), 0.15)
    else:
        tube(E, [(42, -40), (44, -43)], 2.4)
        tube(E, [(47, -40), (48, -42)], 2.2)


# ------------------------------------------------------------------ 1. fix the cues: the drum stays long, as a gun
def v1(phase=1, k=0):
    """The copper drum stays long, but it is laid in a gun cradle and raised like a howitzer barrel, tapering to a
    muzzle (the roast bombs come out of it); no chimney, no cab, no plough."""
    M = Machine()
    tracks(M, k)
    hull(M, phase)
    blade(M)
    # the cradle: an iron trunnion block on the deck the drum pivots in
    Cr = M.part(IRON, 0.25)
    _put(Cr, poly([(-12, -40), (20, -40), (16, -50), (-8, -50)]), 0.45)
    rivets(Cr, [(-6, -44), (4, -44), (14, -44)], 0.9)
    # the drum, raised 12 degrees: copper, banded, tapering to a brass muzzle with a brake
    ang = np.radians(-12)
    def rp(u, v):                                   # along the barrel u (negative forward), across it v
        return (2 + u * np.cos(ang) - v * np.sin(ang), -52 + u * np.sin(ang) + v * np.cos(ang))
    Bl = M.part(IRON, 0.25)
    tube(Bl, [rp(-10, 0), rp(-46, 0)], [4.4, 3.8], amb=0.15, kd=0.6, ks=0.35)    # the barrel out of its front
    D = M.part(COPPER, 0.3)
    tube(D, [rp(24, 0), rp(-8, 0)], 12.5, amb=0.08, kd=0.62, ks=0.5)
    Bd = M.part(IRON, 0.2, edge=False)
    for u in (17, 8, -1):
        line(Bd, [rp(u, -12), rp(u, 12)], 0.3, 1)
    rivets(Bd, [rp(17, -8), rp(8, -9), rp(-1, -7)], 0.9)
    Ec = M.part(IRON, 0.25)
    for u_, rx in ((25, 3.4), (-9, 3.4)):
        e0 = rp(u_, 0)
        sphere(Ec, e0[0], e0[1], rx, 12.4, amb=0.1, kd=0.5, ks=0.2)                # the end caps
    Mz = M.part(BRASS, 0.3)
    tube(Mz, [rp(-46, 0), rp(-53, 0)], [6.4, 6.4], amb=0.15, kd=0.7, ks=0.5)      # the muzzle brake
    hole = M.part(IRON, 0, edge=False)
    mo = rp(-54, 0)
    _put(hole, ell(mo[0], mo[1], 1.6, 3.6), 0.02)
    # the hopper the green beans go in at, on top of the drum
    Hp = M.part(IRON, 0.3)
    hb = rp(6, -13)
    for j in range(10):
        half = 7 - j * 0.35
        for x in range(int(hb[0] - half), int(hb[0] + half) + 1):
            px(Hp, x, int(hb[1] - j), 0.62 - 0.3 * (x - (hb[0] - half)) / (2 * half) + (0.3 if j == 9 else 0))
    if phase >= 3:
        F = M.part(FIRE, 0.2, edge=False)
        for u0, v0, ln, d in ((20, -8, 10, 1), (8, -6, 12, -1), (0, 2, 7, 1)):
            for i in range(ln):
                q = rp(u0 - i * 0.9, v0 + i * 0.8 * d * 0.5 + 1.2 * np.sin(i * 1.4))
                px(F, int(round(q[0])), int(round(q[1])), 0.88)
    cupola(M, 34, -40)
    exhausts(M, phase)
    return M


# ------------------------------------------------------------------ 2. the drum crosswise, in a turret
def v2(phase=1, k=0):
    """The drum turns crosswise and sits in a cast turret: you see its round copper face, the bean door and the sight
    glass; a short gun lobs the roast bombs; the hopper on top is what is shot away first."""
    M = Machine()
    tracks(M, k)
    hull(M, phase)
    blade(M)
    # the turret: low cast armour on a ring
    Tr = M.part(OLIVE, 0.35)
    tm = superell(2, -40, 34, 14, 2.6) & (YS < Y(-39))
    plate(Tr, tm, base=0.56, bevel=4, k=0.7, vgrad=0.5)
    camo(M, tm, seed=21)
    Rg = M.part(IRON, 0.2, edge=False)
    line(Rg, [(-30, -40), (34, -40)], 0.2)
    # its gun: short and fat, cocked up, a brass muzzle (the roast bombs)
    Gn = M.part(IRON, 0.25)
    tube(Gn, [(-26, -46), (-56, -54)], [3.6, 3.0], amb=0.15, kd=0.6, ks=0.3)
    Mz = M.part(BRASS, 0.3)
    tube(Mz, [(-56, -54), (-62, -55.5)], 4.4, amb=0.2, kd=0.7, ks=0.5)
    # the drum's face: a copper disc in an iron rim, raised on the turret
    Rm = M.part(IRON, 0.25)
    sphere(Rm, -2, -68, 20, 20, amb=0.12, kd=0.55, ks=0.25)
    F_ = M.part(COPPER, 0.3)
    fm = ell(-2, -68, 17, 17)
    nx, ny = (XS - X(-2)) / 30.0, (YS - Y(-68)) / 30.0
    _put(F_, fm, B._shade(nx, ny, 0.2, 0.62, 0.55))
    Rv = M.part(IRON, 0.2, edge=False)
    for a in range(0, 360, 30):
        ang = np.radians(a)
        px(Rv, int(round(-2 + 18.6 * np.cos(ang))), int(round(-68 + 18.6 * np.sin(ang))), 0.9)
    # the bean door (a half moon at the foot of the face), its handle, the sight glass, the hub and its spokes
    Dr = M.part(COPPER, 0.25)
    dm = fm & (YS > Y(-63)) & ell(-2, -64, 13, 12)
    _put(Dr, dm, 0.3)
    line(Dr, [(-13, -63), (9, -63)], 0.08)
    Hd = M.part(BRASS, 0.2)
    tube(Hd, [(-6, -57), (2, -57)], 1.4, amb=0.3, kd=0.6, ks=0.5)
    Sg = M.part(YEL, 0.2)
    sphere(Sg, -9, -74, 3.6, 3.6, amb=0.5, kd=0.4, ks=0.7)
    Sgr = M.part(BRASS, 0, edge=False)
    for a in range(0, 360, 20):
        ang = np.radians(a)
        px(Sgr, int(round(-9 + 4.6 * np.cos(ang))), int(round(-74 + 4.6 * np.sin(ang))), 0.7)
    Hb = M.part(IRON, 0.25)
    sphere(Hb, 3, -70, 3.2, 3.2, amb=0.25, kd=0.6, ks=0.4)
    for a in (20, 140, 260):
        ang = np.radians(a)
        line(Hb, [(3, -70), (3 + 9 * np.cos(ang), -70 + 9 * np.sin(ang))], 0.45)
    # the hopper on top: shot away in phase 2, a stump left
    Hp = M.part(IRON, 0.3)
    if phase == 1:
        for j in range(12):
            half = 9 - j * 0.45
            for x in range(int(-2 - half), int(-2 + half) + 1):
                px(Hp, x, -88 - j, 0.62 - 0.3 * (x - (-2 - half)) / (2 * half) + (0.3 if j == 11 else 0))
        _put(Hp, poly([(-5, -88), (1, -88), (1, -85), (-5, -85)]), 0.5)
    else:
        _put(Hp, poly([(-5, -89), (1, -89), (1, -85), (-5, -85)]), 0.4)
        for x in range(-6, 2):
            px(Hp, x, -90 + (x % 2), 0.15)
    if phase >= 3:
        Fr = M.part(FIRE, 0.2, edge=False)
        for sx, sy, ln, d in ((-14, -78, 13, 1), (6, -80, 12, -1), (-4, -66, 8, 1)):
            for i in range(ln):
                xx, yy = sx + i * 0.6 * d, sy + i * 0.9 + 1.4 * np.sin(i * 1.3)
                if fm[int(Y(yy)), int(X(xx))]:
                    px(Fr, int(xx), int(yy), 0.88)
                    px(Fr, int(xx) + 1, int(yy), 0.6)
    cupola(M, 28, -48)
    exhausts(M, phase)
    return M


# ------------------------------------------------------------------ 3. the shop roaster, on tracks
def v3(phase=1, k=0):
    """A coffee-shop roaster bolted to the tank: the enamel cabinet with its round faceplate at the front (bean door,
    sight glass, trier), the hopper on top, the round cooling tray out in front with its stirring arm, and the chaff
    cyclone at the back where the chimney was."""
    M = Machine()
    tracks(M, k)
    hull(M, phase)
    # the chaff cyclone at the back: a drum on an upturned cone, its bin at the foot (shot away in phase 2)
    Cy = M.part(STEEL, 0.25)
    if phase == 1:
        nx = np.clip((XS - X(38)) / 10.0, -1, 1)
        cyl = poly([(28, -92), (48, -92), (48, -78), (28, -78)])
        _put(Cy, cyl, B._shade(nx, np.zeros_like(nx), 0.2, 0.62, 0.35))
        cone = poly([(28, -78), (48, -78), (40, -58), (36, -58)])
        _put(Cy, cone, B._shade(nx, np.zeros_like(nx), 0.16, 0.56, 0.25))
        _put(Cy, poly([(27, -94), (49, -94), (49, -92), (27, -92)]), 0.8)
        line(Cy, [(28, -78), (48, -78)], 0.35)
        rivets(Cy, [(31, -88), (38, -89), (45, -88), (31, -81), (45, -81)], 0.95)
        tube(Cy, [(38, -99), (38, -94)], 2.6, amb=0.2, kd=0.6, ks=0.3)
    Bn = M.part(IRON, 0.25)
    _put(Bn, rounded(poly([(31, -58), (45, -58), (45, -42), (31, -42)]), 1), 0.42)
    rivets(Bn, [(34, -55), (42, -55)], 0.9)
    # the duct from the cabinet to the cyclone
    Du = M.part(STEEL, 0.25)
    if phase == 1:
        tube(Du, [(14, -74), (18, -82), (28, -85)], 3.0, amb=0.2, kd=0.62, ks=0.35, rings=4, ring_t=0.05)
    else:
        tube(Du, [(14, -74), (19, -80)], 3.0, amb=0.2, kd=0.62, ks=0.35, rings=4, ring_t=0.05)
    # the cabinet: militia-olive enamel, a copper band where the drum turns inside
    Cb = M.part(OLIVE, 0.35)
    cm = rounded(poly([(-30, -76), (20, -76), (22, -40), (-32, -40)]), 2)
    plate(Cb, cm, base=0.6, bevel=3, k=0.6, vgrad=0.45)
    camo(M, cm, seed=31)
    Bd = M.part(COPPER, 0.3)
    bm = poly([(-30, -64), (20, -64), (21, -56), (-31, -56)])
    plate(Bd, bm, base=0.62, bevel=1.5, k=0.6, vgrad=0.6)
    rivets(Bd, [(x, -60) for x in range(-26, 20, 6)], 0.92)
    # the gauge and the burner's peep hole on its side
    Gg = M.part(CREAM, 0.1)
    sphere(Gg, 10, -70, 3.4, 3.4, amb=0.5, kd=0.4, ks=0.3)
    Gn_ = M.part(IRON, 0, edge=False)
    line(Gn_, [(10, -70), (12, -72)], 0.05)
    Ph = M.part(FIRE, 0.2)
    sphere(Ph, -6, -47, 2.6, 2.0, amb=0.6, kd=0.3, ks=0.2)
    # the hopper with its slide gate
    Hp = M.part(IRON, 0.3)
    for j in range(12):
        half = 8 - j * 0.42
        for x in range(int(-12 - half), int(-12 + half) + 1):
            px(Hp, x, -77 - j, 0.62 - 0.3 * (x - (-12 - half)) / (2 * half) + (0.3 if j == 11 else 0))
    Sl = M.part(BRASS, 0.2)
    _put(Sl, poly([(-16, -79), (-6, -79), (-6, -77), (-16, -77)]), 0.7)
    # the faceplate at the front of the cabinet, seen a little from the side: copper in an iron ring
    Fr = M.part(IRON, 0.25)
    sphere(Fr, -33, -58, 7.5, 17.5, amb=0.12, kd=0.55, ks=0.3)
    Fp = M.part(COPPER, 0.3)
    fpm = ell(-34, -58, 5.6, 15.4)
    sphere(Fp, -34, -60, 7, 18, amb=0.2, kd=0.65, ks=0.55, clip=fpm)
    Dd = M.part(COPPER, 0.25)
    _put(Dd, fpm & (YS > Y(-54)), 0.25)
    line(Dd, [(-39, -54), (-29, -54)], 0.06)
    Sg = M.part(YEL, 0.2)
    sphere(Sg, -35, -65, 2.0, 2.6, amb=0.5, kd=0.4, ks=0.7)
    Ti = M.part(BRASS, 0.25)
    tube(Ti, [(-36, -59), (-42, -59)], 1.4, amb=0.3, kd=0.6, ks=0.5)
    sphere(Ti, -43, -59, 1.8, 1.8, amb=0.3, kd=0.6, ks=0.5)
    # the cooling tray out in front, on its arm: shallow, round, stirred; the high spray is flicked off it (31 up)
    Ar = M.part(IRON, 0.25)
    tube(Ar, [(-40, -32), (-50, -28)], 2.0)
    tube(Ar, [(-58, -27), (-58, -18)], 2.2)
    _put(Ar, poly([(-61, -18), (-55, -18), (-55, -14), (-61, -14)]), 0.4)        # the stirrer's motor under it
    Ct = M.part(STEEL, 0.3)
    side = poly([(-75, -31), (-41, -31), (-42, -26), (-74, -26)])
    plate(Ct, side, base=0.5, bevel=1.5, k=0.6, vgrad=0.5)
    rim = ell(-58, -31, 17, 3.2)
    _put(Ct, rim & ~ell(-58, -31, 15.6, 2.2), 0.85)
    Bn2 = M.part(BEAN, 0.4, edge=False)
    _put(Bn2, ell(-58, -31.5, 15, 2.0), 0.55)
    St = M.part(BRASS, 0.2, edge=False)
    line(St, [(-58, -32), (-58, -37), (-50, -36)], 0.75)
    if phase >= 3:
        Fx = M.part(FIRE, 0.2, edge=False)
        for sx, sy, ln in ((-34, -70, 10), (-33, -52, 7)):
            for i in range(ln):
                px(Fx, int(sx + np.sin(i * 1.5) * 1.5), sy + i, 0.88)
        for sx, sy, ln in ((-20, -74, 10), (4, -72, 12)):
            for i in range(ln):
                px(Fx, int(sx + i * 0.8), int(sy + i * 0.9), 0.8)
    cupola(M, 6, -76, lid=False)
    return M


VARIANTS = {'v1': v1, 'v2': v2, 'v3': v3}


def variant_img(name, phase=1, k=0):
    return crop(VARIANTS[name](phase, k).render())


# ------------------------------------------------------------------ staging: the yard, the phases
SMOKE = {'v1': (22, -66), 'v2': (-2, -92), 'v3': (38, -60)}


def with_smoke(name, boss, phase):
    B.SMOKE_AT['_v'] = SMOKE[name]
    return B.with_smoke('_v', boss, phase)


def phase_sheet(name, w=624, h=180, bg=(16, 20, 44, 255)):
    from PIL import ImageDraw
    figs = [with_smoke(name, variant_img(name, ph), ph) for ph in (1, 2, 3)]
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


def hero(name, bx=330):
    G = B.GROUND
    shoot = [('yazeed_stand_side_fwd', 128, G), ('fx_muzzle', 128 + 18, G - 23), ('fx_tracer', 198, G - 23), ('fx_tracer', 238, G - 23)]
    return B.scene(variant_img(name, 1), bx, shoot)
