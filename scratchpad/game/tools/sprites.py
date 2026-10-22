# sprites.py - the frames the prototype needs, built from the same parts as the cast sheet.
# Every frame is (image, ax, ay): the anchor is the point between the feet, on the ground.
import sys, json, os
MOCK = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock'
sys.path.insert(0, MOCK)
from PIL import Image
import ms3
from ms3 import at, weapon, compose, pal, PARTS, WEAPONS, WRAPS, FACES, STD, LEAN, SLIM, INK2, HAND

LEGS = PARTS['legs']
LEG_FAR = [r[0:8] for r in LEGS]            # the leg away from us
LEG_NEAR = [r[12:20] for r in LEGS]
LEGS_L = PARTS['legs_l']
LEG_FAR_L = [r[0:7] for r in LEGS_L]
LEG_NEAR_L = [r[11:18] for r in LEGS_L]


def rot_ccw(rows):
    """Turn a grid a quarter turn anticlockwise: what pointed right now points up."""
    w = max(len(r) for r in rows)
    rows = [r.ljust(w, '.') for r in rows]
    return [''.join(rows[y][x] for y in range(len(rows))) for x in range(w - 1, -1, -1)]


def rot_cw(rows):
    w = max(len(r) for r in rows)
    rows = [r.ljust(w, '.') for r in rows]
    return [''.join(rows[y][x] for y in range(len(rows) - 1, -1, -1)) for x in range(w)]


# new small parts
EXTRA = {
    # deeper crouch: the futa bunched over folded legs, toes showing
    'futa_squat': [
        '..fghhiiiiihhhg...',
        '.fgghSiiiiihghSgg.',
        'ffghhShh#iiihghSgg',
        'fgghhShgh#iihhgSgg',
        'SSKSSKSSKSSKSSKSSK',
    ],
    'toes_squat': [
        'pqAqA.........qAqArs',
        'AAAAA.........AAAAAA',
    ],
}


def yazeed_pal():
    p = pal('blue', 'cream', 'blue', 'skin2')
    p['9'] = '#e4dec2'
    return p


# ---------------------------------------------------------------- guns held at 45 degrees
def _grid(w, h):
    return [['.'] * w for _ in range(h)]


def _stroke(g, x0, y0, n, letters, dx=1, dy=-1):
    """n steps along a diagonal; at each step a horizontal run of letters."""
    for i in range(n):
        for k, ch in enumerate(letters):
            x, y = x0 + i * dx + k, y0 + i * dy
            if 0 <= y < len(g) and 0 <= x < len(g[0]) and ch != '.':
                g[y][x] = ch


def _rows(g):
    return [''.join(r) for r in g]


def mg_diag():
    """The machine gun pointing up and right: butt at lower left, belt hanging straight down."""
    g = _grid(30, 29)
    _stroke(g, 0, 26, 1, 'WXX')            # butt plate
    _stroke(g, 0, 25, 4, 'WXXYY')          # stock
    _stroke(g, 4, 21, 8, 'xyzyyyx')        # receiver
    _stroke(g, 5, 21, 1, 'yyyyyx')
    _stroke(g, 12, 13, 6, 'yzzyyx')        # handguard
    _stroke(g, 18, 7, 4, 'zyyx')           # barrel
    _stroke(g, 22, 3, 2, 'zyx')
    g[1][25] = 'y'; g[1][26] = 'y'; g[2][24] = 'z'        # muzzle
    g[5][19] = 'x'; g[4][20] = 'x'                        # front sight
    g[14][8] = 'Z'; g[13][9] = 'Z'; g[15][7] = 'z'        # feed cover catching the light
    g[17][8] = '#'; g[16][9] = '#'                        # ejection port
    for (x, y, ch) in ((11, 21, 'y'), (12, 22, 'y'), (12, 21, 'x'), (13, 22, 'x'), (11, 22, 'x'), (12, 23, 'x'), (13, 23, 'x')):
        g[y][x] = ch                                      # pistol grip
    belt = ['DEFE', 'EFED', 'FEDE', 'DEEF', 'EFDE', '.EDF', '.FE.', '..D.']
    for j, row in enumerate(belt):
        for i, ch in enumerate(row):
            if ch != '.':
                g[17 + j][14 + i] = ch
    return _rows(g)


def mg_down():
    """Pointing down and right. Only the part forward of the grip shows: the stock is behind him."""
    g = _grid(27, 27)
    _stroke(g, 0, 0, 8, 'xyzyyyx', 1, 1)          # receiver
    _stroke(g, 8, 8, 6, 'yzzyyx', 1, 1)           # handguard
    _stroke(g, 15, 14, 4, 'zyyx', 1, 1)           # barrel
    _stroke(g, 19, 18, 3, 'zyx', 1, 1)
    g[21][23] = 'y'; g[22][24] = 'y'; g[22][23] = 'y'
    g[17][20] = 'x'; g[18][21] = 'x'              # front sight
    g[3][6] = 'Z'; g[4][7] = 'Z'
    belt = ['DEFE', 'EFED', 'FEDE', 'DEEF', '.FDE', '..D.']
    for j, row in enumerate(belt):
        for i, ch in enumerate(row):
            if ch != '.' and g[6 + j][1 + i] == '.':
                g[6 + j][1 + i] = ch
    return _rows(g)


PISTOL_D = [
    '......zy',
    '.....zyy',
    '....zzyx',
    '...zzyx.',
    '..zzyx..',
    '.yzyyx..',
    'xyyyyx..',
    '.xxyYx..',
    '..xXYW..',
    '...WXW..',
]

FOREARM_D = [          # elbow lower left, hand upper right
    '.......qrs',
    '......brrr',
    '....bccqr.',
    '..bcccb...',
    '.bbccb....',
    'abbbb.....',
    'aaa.......',
]


BLADE_UP = [           # the jambiya drawn back over the shoulder, point up
    '..Z..',
    '.zZ..',
    '.zZ..',
    'zzZ..',
    'zZ...',
    'EF...',
    'DE...',
]
BLADE_OUT = [          # and at the end of the cut: arm out, the curve of the blade leading
    '.......zZ',
    '.....zzZ.',
    '...zzzZ..',
    'DEzzZZ...',
    'EF.......',
]


def yazeed_knife(legs='stand', stage=1):
    """The jambiya: 1 drawn back, 2 cut home. The gun hangs out of sight for the moment it takes."""
    L, foot, _ = yazeed(legs, 'side', 'fwd', bare=True)
    p = yazeed_pal()
    B = STD
    dx = 1 if legs in ('run', 'fall') else 0
    dy = -1 if legs == 'pass' else (12 if legs == 'crouch' else 0)
    if stage == 1:
        L = [(BLADE_UP, 0 + dx, -9 + dy, p), at('arm_raise_l', (2, -1), p, dx, dy)] + L
        L += [at('sleeve', B.sleeve, p, dx, dy)]
        tip = (2 + dx, -9 + dy)
    else:
        L += [(BLADE_OUT, 22 + dx, 9 + dy, p), at('forearm', (11, 12), p, dx, dy), at('sleeve', B.sleeve, p, dx, dy)]
        tip = (31 + dx, 9 + dy)
    return L, foot, tip


# where each of Yazeed's guns sits for each way of pointing it: (grip x, grip y) in the standing figure
def yazeed(legs='stand', gun='side', aim='fwd', throw=False, bare=False):
    p = yazeed_pal()
    B = STD
    L = []
    dx = dy = 0
    if legs == 'stand':
        L += [at(LEG_FAR, B.legs, p), at(LEG_NEAR, B.legs, p, 12), at('futa', B.futa, p)]
    elif legs == 'run':
        dx = 1
        L += [at('legs_run', (0, 29), p), at('futa_run', (3, 22), p)]
    elif legs == 'pass':
        dy = -1
        L += [at(LEG_FAR, B.legs, p, 3), at(LEG_NEAR, B.legs, p, 8), at('futa', B.futa, p, 0, -1)]
    elif legs == 'jump':
        L += [at('legs_crouch', (2, 25), p), at('futa_crouch', (3, 22), p)]
    elif legs == 'fall':
        dx = 1
        L += [at('legs_run', (0, 28), p), at('futa_run', (3, 22), p)]
    elif legs == 'crouch':
        dy = 12
        L += [at(EXTRA['toes_squat'], (2, 35), p), at(EXTRA['futa_squat'], (3, 32), p)]
    body = [at('pack', B.pack, p, dx, dy)]
    if throw:
        body.append(at('arm_raise_l', (2, -1), p, dx, dy))
    body += [at('blazer', B.torso, p, dx, dy), at('belt', B.belt, p, dx, dy), at('jambiya', B.jamb, p, dx, dy)]
    L = body[:1 + (1 if throw else 0)] + L + body[1 + (1 if throw else 0):]
    muzzle = None
    over = []                 # what passes in front of the face when the gun is raised at 45 degrees
    if bare:
        pass
    elif gun == 'side':
        if aim == 'fwd':
            g = (21 + dx, 16 + dy)
            weapon(L, 'pistol', p, g)
            L += [at('forearm', (11, 12), p, dx, dy), at('sleeve', B.sleeve, p, dx, dy)]
            muzzle = (g[0] + 8, g[1] - 3)
        elif aim == 'up':
            w = rot_ccw(WEAPONS['pistol']['rows'])
            L += [(w, 18 + dx, -6 + dy, p)]
            L += [at('sleeve', B.sleeve, p, dx, dy), at('arm_raise_fl', (18, 2), p, dx, dy)]
            muzzle = (19 + dx, -7 + dy)
        elif aim == 'diag':
            L += [at('sleeve', B.sleeve, p, dx, dy)]
            over += [(PISTOL_D, 18 + dx, -1 + dy, p), (FOREARM_D, 14 + dx, 6 + dy, p)]
            muzzle = (25 + dx, -1 + dy)
        elif aim == 'ddiag':
            L += [(PISTOL_D[::-1], 17 + dx, 15 + dy, p), at('sleeve', B.sleeve, p, dx, dy), (FOREARM_D[::-1], 13 + dx, 14 + dy, p)]
            muzzle = (24 + dx, 24 + dy)
        else:
            w = rot_cw(WEAPONS['pistol']['rows'])
            L += [(w, 17 + dx, 21 + dy, p)]
            L += [at('sleeve', B.sleeve, p, dx, dy), at(rot_cw(PARTS['forearm']), (12, 13), p, dx, dy)]
            muzzle = (19 + dx, 31 + dy)
    else:
        if aim == 'fwd':
            g = (B.grip[0] + dx, B.grip[1] + dy)
            weapon(L, 'mg', p, g)
            L += [at('forearm', B.forearm, p, dx, dy), at('sleeve', B.sleeve, p, dx, dy)]
            muzzle = (g[0] + 26, g[1] - 2)
        elif aim == 'up':
            w = rot_ccw(WEAPONS['mg']['rows'])
            L += [(w, 19 + dx, -12 + dy, p)]
            L += [at('sleeve', B.sleeve, p, dx, dy), at('forearm_up', (11, 13), p, dx, dy)]
            muzzle = (22 + dx, -13 + dy)
        elif aim == 'diag':
            over += [(mg_diag(), 6 + dx, -3 + dy, p), (HAND, 22 + dx, 8 + dy, p), at('forearm', B.forearm, p, dx, dy - 1), at('sleeve', B.sleeve, p, dx, dy)]
            muzzle = (33 + dx, -3 + dy)
        elif aim == 'ddiag':
            L += [(mg_down(), 9 + dx, 9 + dy, p), (HAND, 22 + dx, 20 + dy, p), at('forearm', B.forearm, p, dx, dy - 2), at('sleeve', B.sleeve, p, dx, dy)]
            muzzle = (33 + dx, 32 + dy)
        else:
            w = rot_cw(WEAPONS['mg']['rows'])
            L += [(w, 15 + dx, 13 + dy, p)]
            L += [at('sleeve', B.sleeve, p, dx, dy), at('forearm', B.forearm, p, dx, dy - 2)]
            muzzle = (19 + dx, 47 + dy)
    ms3.head(L, B, p, 'yazeed', 'check', 'check_end', dx, dy)
    L.append(at(WRAPS['basil'], B.wrap, p, dx, dy + 1, ink=INK2))
    L += over
    return L, B.foot, muzzle


# ---------------------------------------------------------------- the Scorpion's men
FUTA_RUN_PLAIN = [r.replace('S', 'g').replace('K', 'f') for r in PARTS['futa_run'][:-1]] + ['fgffgfgffgfgffgfgff']


def lean_legs(p, pose, B=LEAN):
    if pose == 'run':
        return [at('legs_run', (-1, 28), p), at(FUTA_RUN_PLAIN, (2, 20), p)], 1, 0
    if pose == 'pass':
        return [at(LEG_FAR_L, B.legs, p, 3), at(LEG_NEAR_L, B.legs, p, 8), at('futa_l', B.futa, p, 0, -1)], 0, -1
    return [at('legs_l', B.legs, p), at('futa_l', B.futa, p)], 0, 0


def lean_head(L, face, p, dx=0, dy=0, B=LEAN):
    L.append(at(WRAPS['check_end'], B.wrap, p, dx - 1, dy + 6, ink=INK2))
    L.append(at(FACES[face], B.face, p, dx, dy))
    L.append(at(WRAPS['check_l'], B.wrap, p, dx, dy, ink=INK2))


def rifleman(pose='stand', look='worried', skin='skin2', act='hip'):
    """act: hip (carrying), aim (rifle at the shoulder), up (hands up), flung (hit)."""
    p = ms3.militia_pal(skin)
    B = LEAN
    look = {'qat': 'qat_l'}.get(look, look)
    legs, dx, dy = lean_legs(p, pose)
    L = []
    muzzle = None
    if act in ('up', 'flung'):
        L.append(at('arm_raise_l', (3, 0), p, dx, dy))
    L += legs + [at('jacket_l', B.torso, p, dx, dy), at('belt_l', B.belt, p, dx, dy), at('jambiya_s', B.jamb, p, dx, dy)]
    if act == 'hip':
        g = (B.grip[0] + dx, B.grip[1] + dy)
        weapon(L, 'rifle', p, g)
        L += [at('forearm_l', B.forearm, p, dx, dy), at('sleeve_l', B.sleeve, p, dx, dy), at('armband', B.sleeve, p, dx + 2, dy + 2)]
        muzzle = (g[0] + 22, g[1] - 3)
    elif act == 'aim':
        g = (18 + dx, 12 + dy)
        weapon(L, 'rifle', p, g, hand=False)
        L += [at('sleeve_l', B.sleeve, p, dx, dy), at('armband', B.sleeve, p, dx + 2, dy + 2), at('forearm_up_l', (9, 10), p, dx, dy)]
        muzzle = (g[0] + 22, g[1] - 3)
    else:
        L += [at('sleeve_l', B.sleeve, p, dx, dy), at('armband', B.sleeve, p, dx + 2, dy + 2)]
    lean_head(L, look, p, dx, dy)
    if act == 'aim':
        pass
    if act in ('up', 'flung'):
        L.append(at('arm_raise_fl', (17, 2), p, dx, dy))
    return L, B.foot, muzzle


def bomber(pose='stand', act='carry', skin='skin1'):
    """act: carry (stick held low), wind (arm back, lit), throw (arm forward, empty), up, flung."""
    p = ms3.militia_pal(skin)
    B = LEAN
    legs, dx, dy = lean_legs(p, pose)
    L = []
    hand = None
    if act == 'wind':
        L.append(at('arm_raise_l', (3, 0), p, dx, dy))
        weapon(L, 'dynamite', p, grip=(5 + dx, 0 + dy))
        hand = (6 + dx, -8 + dy)
    if act in ('up', 'flung'):
        L.append(at('arm_raise_l', (3, 0), p, dx, dy))
    L += legs + [at('jacket_l', B.torso, p, dx, dy), at('belt_l', B.belt, p, dx, dy), at('jambiya_s', B.jamb, p, dx, dy)]
    if act == 'carry':
        weapon(L, 'dynamite', p, grip=(20 + dx, 19 + dy))
        L += [at('forearm_l', B.forearm, p, dx, dy)]
    elif act == 'wind':
        L += [at('forearm_l', B.forearm, p, dx, dy)]
    elif act == 'throw':
        L += [at('forearm_up_l', (10, 9), p, dx, dy)]
    L += [at('sleeve_l', B.sleeve, p, dx, dy), at('armband', B.sleeve, p, dx + 2, dy + 2)]
    lean_head(L, 'angry', p, dx, dy)
    if act in ('up', 'flung'):
        L.append(at('arm_raise_fl', (17, 2), p, dx, dy))
    return L, B.foot, hand


DOOR = PARTS['door']
DOOR_TOP = DOOR[:8]                      # the window half
DOOR_BOT = DOOR[8:]                      # the panel with the stripe


def doorman(pose='stand', act='up', skin='skin2'):
    """act: up (behind the door), lean (door dropped, taking aim), back (door swung back to shove), shove (door thrust out),
    bare (the man without his door), aim (the same, pistol up), hands (arms up), flung."""
    p = ms3.militia_pal(skin)
    B = STD
    dx = dy = 0
    if pose == 'run':
        dx = 1
        legs = [at('legs_run', (0, 29), p), at(FUTA_RUN_PLAIN, (3, 22), p)]
    elif pose == 'pass':
        dy = -1
        legs = [at(LEG_FAR, B.legs, p, 3), at(LEG_NEAR, B.legs, p, 8), at('futa_plain', B.futa, p, 0, -1)]
    else:
        legs = [at('legs', B.legs, p), at('futa_plain', B.futa, p)]
    L = []
    if act in ('flung', 'hands'):
        L.append(at('arm_raise_l', (3, 1), p, dx, dy))
    L += legs + [at('jacket', B.torso, p, dx, dy), at('belt_plain', B.belt, p, dx, dy), at('jambiya_s', B.jamb, p, dx, dy + 1),
                 at('sleeve', B.sleeve, p, dx, dy), at('armband', B.sleeve, p, dx + 3, dy + 2)]
    ms3._militia_head(L, 'qat', p, B) if (dx == 0 and dy == 0) else head_std(L, 'qat', p, dx, dy)
    muzzle = None
    door = None
    if act == 'up':
        door = (19, 11)
        L += [at('door', door, p, dx, dy)]
        weapon(L, 'pistol', p, grip=(21 + dx, 9 + dy))
        L += [at('forearm_up', (9, 8), p, dx, dy)]
        muzzle = (29 + dx, 6 + dy)
    elif act == 'lean':
        door = (15, 17)
        L += [at('door', door, p, dx, dy)]
        weapon(L, 'pistol', p, grip=(22 + dx, 10 + dy))
        L += [at('forearm_up', (10, 9), p, dx, dy)]
        muzzle = (30 + dx, 7 + dy)
    elif act == 'back':
        door = (14, 5)
        L += [at('door', door, p, dx, dy), at('forearm_up', (8, 9), p, dx, dy)]
    elif act == 'shove':
        door = (25, 12)
        L += [at('door', door, p, dx, dy), at('forearm', (13, 14), p, dx, dy)]
    elif act == 'bare':
        weapon(L, 'pistol', p, grip=(21 + dx, 16 + dy))
        L += [at('forearm', (11, 12), p, dx, dy)]
        muzzle = (29 + dx, 13 + dy)
    elif act == 'aim':
        weapon(L, 'pistol', p, grip=(22 + dx, 10 + dy))
        L += [at('forearm_up', (10, 9), p, dx, dy)]
        muzzle = (30 + dx, 7 + dy)
    elif act in ('flung', 'hands'):
        L.append(at('arm_raise_fl', (18, 3), p, dx, dy))
    if door:
        muzzle = (door[0] + dx, door[1] + dy)          # for these frames the second point is the door's corner, so marks can be put on it
    return L, B.foot, muzzle


def commander(act='stand', bob=0):
    """The battery's Commander. act: stand (megaphone up), hands (both up, which is how the day ends for him)."""
    p = ms3.pal('olive', 'black', 'white', 'skin1')
    p['9'] = '#b8301c'
    M = ms3.MARSHAL
    d = -bob
    L = [(M['boots'], 4, 40, p), (M['skirt'], 3, 30 + d, p)]
    if act == 'stand':
        L += [(M['far_arm'], 24, 12 + d, p)]
    else:
        L += [at('arm_raise_l', (25, 0 + d), p)]
    L += [(M['torso'], 4, 13 + d, p), (M['sash'], 10, 14 + d, p), (M['medals'], 18, 17 + d, p), (M['belt'], 4, 28 + d, p), (M['jambiya'], 18, 24 + d, p)]
    if act == 'stand':
        L += [(M['megaphone'], 30, 6 + d, p), (M['forearm'], 10, 22 + d, p)]
    L += [(M['sleeve'], 4, 15 + d, p), (M['epaulette'], 4, 13 + d, p), (M['face'], 14, 5 + d, p), (M['wrap'], 11, -4 + d, p, INK2)]
    if act != 'stand':
        L += [at('arm_raise_fl', (4, 3 + d), p)]
    return L, (17, 48), None


def head_std(L, face, p, dx, dy, B=STD):
    L.append(at(WRAPS['check_end'], B.wrap, p, dx - 1, dy + 6, ink=INK2))
    L.append(at(FACES[face], B.face, p, dx, dy))
    L.append(at(WRAPS['check'], B.wrap, p, dx, dy, ink=INK2))


def door_piece(which='whole'):
    p = ms3.militia_pal('skin2')
    rows = {'whole': DOOR, 'top': DOOR_TOP, 'bot': DOOR_BOT}[which]
    return [at(rows, (0, 0), p)], (8, len(rows) // 2), None


DOOR_MARKS = {
    # what a door looks like after some shooting: holes punched through, the window starred
    1: ['.............', '......x......', '.....#x#.....', '......#......', '.............', '.............', '.............', '.........xx..', '.........x#..', '.............'],
    2: ['....#........', '...#x#..#....', '....#..#x#...', '..x.....#....', '.x#x.........', '..x......x...', '........x#x..', '...xx....x...', '...x#x.......', '....x........'],
}


def door_marks(level):
    p = ms3.militia_pal('skin2')
    p = dict(p)
    p['x'] = '#16120e'
    p['#'] = '#4a4438'
    from px import sprite
    return sprite(DOOR_MARKS[level], p)


def detainee(act='tied', pose='stand'):
    p = pal('white', 'white', 'white', 'skin3')
    B = SLIM
    L = []
    dy = -1 if pose == 'pass' else 0
    if act == 'tied':
        L.append(at('post', (2, -10), p))
    L += [at('bare_feet_s', B.legs, p, 1 if pose == 'pass' else 0, 0), at('thobe_s', B.futa, p, 0, dy), at('thobe_top_s', B.torso, p, 0, dy)]
    if act == 'tied':
        L += [at('rope_s', (4, 10), p)]
    L += [at(FACES['elder'], B.face, p, 0, dy), at(WRAPS['cap'], B.wrap, p, 0, 1 + dy, ink=INK2)]
    if act == 'freed':
        L += [at('arm_salute_s', (12, 2), p)]
    return L, B.foot, None


def post_piece():
    p = pal('white', 'white', 'white', 'skin3')
    return [at('post', (2, -10), p)], SLIM.foot, None


def build(layers, foot, muzzle=None, flip=False):
    """Compose and carry a second point (the muzzle) through the same crop."""
    im, fx, fy = compose(layers, flip=False, foot=foot)
    # compose() crops; recover the offset it used so other points can follow
    minx = min(l[1] for l in layers) - 1
    miny = min(l[2] for l in layers) - 1
    full, _, _ = compose_nocrop(layers)
    bb = full.getbbox()
    ox, oy = minx + bb[0], miny + bb[1]
    out = dict(im=im, ax=fx, ay=fy)
    if muzzle:
        out['mx'] = muzzle[0] - ox
        out['my'] = muzzle[1] - oy
    return out


def compose_nocrop(layers):
    from px import new, blit
    minx = min(l[1] for l in layers) - 1
    miny = min(l[2] for l in layers) - 1
    maxx = max(l[1] + max(len(r) for r in l[0]) for l in layers) + 1
    maxy = max(l[2] + len(l[0]) for l in layers) + 1
    im = new(maxx - minx, maxy - miny)
    for l in layers:
        rows, x, y, p = l[:4]
        blit(im, ms3.part(rows, p, l[4] if len(l) > 4 else None), x - 1 - minx, y - 1 - miny)
    return im, minx, miny


def sheet(frames, path, zoom=6, cols=8, cell=(56, 62), bg=(86, 150, 170)):
    """Lay frames out on a grid with their anchors on a common line, to look at."""
    from PIL import ImageDraw
    rows = (len(frames) + cols - 1) // cols
    W, H = cols * cell[0], rows * cell[1]
    im = Image.new('RGBA', (W, H), bg + (255,))
    d = ImageDraw.Draw(im)
    for i, (name, f) in enumerate(frames):
        cx, cy = (i % cols) * cell[0] + cell[0] // 2, (i // cols) * cell[1] + cell[1] - 8
        d.line([(cx - 20, cy), (cx + 20, cy)], fill=(240, 220, 150, 255))
        im.alpha_composite(f['im'], (cx - f['ax'], cy - f['ay']))
        if 'mx' in f:
            mxp, myp = cx - f['ax'] + f['mx'], cy - f['ay'] + f['my']
            if 0 <= mxp < W and 0 <= myp < H:
                im.putpixel((mxp, myp), (255, 0, 255, 255))
    im = im.resize((W * zoom, H * zoom), Image.NEAREST)
    d = ImageDraw.Draw(im)
    for i, (name, f) in enumerate(frames):
        d.text(((i % cols) * cell[0] * zoom + 4, (i // cols) * cell[1] * zoom + 4), name, fill=(255, 255, 255, 255))
    im.save(path)
    return im.size


if __name__ == '__main__':
    fr = []
    for legs in ('stand', 'pass', 'run', 'jump', 'fall', 'crouch'):
        for gun in ('side', 'hmg'):
            L, foot, mz = yazeed(legs, gun, 'fwd')
            fr.append(('%s %s' % (legs, gun), build(L, foot, mz)))
    for gun in ('side', 'hmg'):
        for aim in ('up', 'down'):
            L, foot, mz = yazeed('stand' if aim == 'up' else 'jump', gun, aim)
            fr.append(('%s %s' % (gun, aim), build(L, foot, mz)))
    L, foot, mz = yazeed('stand', 'side', 'fwd', throw=True)
    fr.append(('throw', build(L, foot, mz)))
    for n, f in fr:
        if 'mx' in f:
            print(n, 'muzzle rel feet', (f['mx'] - f['ax'], f['ay'] - f['my']))
    print(sheet(fr, 'art/preview_yazeed.png', zoom=5, cols=6, cell=(62, 74)))
    en = []
    for pose in ('stand', 'pass', 'run'):
        en.append(('rifle ' + pose, build(*rifleman(pose, 'worried'))))
    en.append(('rifle aim', build(*rifleman('stand', 'youth', act='aim'))))
    en.append(('rifle up', build(*rifleman('stand', 'angry', act='up'))))
    en.append(('rifle flung', build(*rifleman('run', 'qat', act='flung'))))
    for pose in ('stand', 'run'):
        en.append(('bomber ' + pose, build(*bomber(pose))))
    en.append(('bomber wind', build(*bomber('stand', 'wind'))))
    en.append(('bomber throw', build(*bomber('stand', 'throw'))))
    for pose in ('stand', 'pass', 'run'):
        en.append(('door ' + pose, build(*doorman(pose))))
    en.append(('door lean', build(*doorman('stand', 'lean'))))
    en.append(('door bare', build(*doorman('stand', 'bare'))))
    en.append(('door flung', build(*doorman('run', 'flung'))))
    en.append(('door piece', build(*door_piece())))
    en.append(('det tied', build(*detainee('tied'))))
    en.append(('det freed', build(*detainee('freed'))))
    en.append(('det walk', build(*detainee('walk', 'pass'))))
    en.append(('post', build(*post_piece())))
    for n, f in en:
        if 'mx' in f:
            print(n, 'point rel feet', (f['mx'] - f['ax'], f['ay'] - f['my']))
    print(sheet(en, 'art/preview_men.png', zoom=5, cols=7, cell=(56, 66)))
