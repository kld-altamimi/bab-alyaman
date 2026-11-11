# dhamar_sprites.py - the sprites Dhamar (Mission 5, the Wadi) adds, on a sheet of its own (art/out/dhamar.png,
# gen/dhamar_sprites.json), for the test build of zones 1-3 (Khaled, 11 Nov 03:25: "let's go with your plan"; the
# Committee's look as placeholders until the fight's check-in). Built the way the cast is (mock/ms3.py), from what the
# mock page showed him:
#   the Committee (game/tools/committee_sprites.py, redrawn from his photo 11 Nov): standing, speaking, the vote, the
#     laugh's three frames, two walking frames; his table with its microphones, the gavel and the sign-in sheet;
#   the gathering at the vote (mock_dhamar_scenes.py's men: mismatched clothes, no armbands): each standing, hands up,
#     filing off; the one who asks;
#   the teacher from Ibb (ibb_sprites.py's, look A) drafted as his own pupils' sergeant: a cap too big, a whistle;
#   the children and Yazeed with his gun lowered (Ibb's, the same drawings: ibb_sprites.py), for the recruiting office;
#   men the gas torch caught: their atlas frames, hands up and running, blackened, the whites of their eyes left;
#   the Leader's silent screen (mock_dhamar_scenes.py's, at the game's size), and the poster of the Committee's laughing
#     face over the stamp window (no text);
#   the convoy's lorry (wooden slat sides, painted; its wheels are the atlas's), the goats, the horse that refuses and the
#     barber's chair for its load.
# Every frame is (image, ax, ay): the anchor is the point between the feet on the ground unless it says otherwise.
#   python3 dhamar_sprites.py --sheet | --look
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock'
sys.path.insert(0, MOCK)
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw
import ms3
from ms3 import pal, compose, at, INK, INK2
import committee_sprites as C
import ibb_sprites as IB
import mock_dhamar_scenes as MS
import mock_dhamar_road as MR

GAME = os.path.join(HERE, '..')
OUT = os.path.join(GAME, 'art', 'out')
GEN = os.path.join(GAME, 'gen')
_A = {}


def atlas(name):
    if not _A:
        _A['img'] = Image.open(os.path.join(OUT, 'atlas.png')).convert('RGBA')
        _A['fr'] = json.load(open(os.path.join(GEN, 'atlas.json')))['frames']
    fx, fy, w, h, ax, ay = _A['fr'][name]
    return _A['img'].crop((fx, fy, fx + w, fy + h)), ax, ay


# ---------------------------------------------------------------- the Committee
def walk_of(frame, k):
    """A walking frame from a standing one: under the thobe only the shoes show a stride; k = 0 or 1."""
    im, ax, ay = frame
    a = np.array(im)
    h = a.shape[0]
    out = a.copy()
    shoes = a[h - 2:h].copy()
    out[h - 2:h] = 0
    front, back = (2, -1) if k == 0 else (-1, 2)
    for y in range(2):
        row = shoes[y]
        for x in range(a.shape[1]):
            if row[x, 3] == 0:
                continue
            nx = x + (front if x >= ax else back)
            if 0 <= nx < a.shape[1]:
                out[h - 2 + y, nx] = row[x]
    return Image.fromarray(out), ax, ay


def committee_frames():
    st = C.committee('closed')
    out = [('cm_stand',) + st, ('cm_speak',) + C.committee('half'), ('cm_vote',) + C.committee_vote(),
           ('cm_laugh1',) + C.committee_laugh(1), ('cm_laugh2',) + C.committee_laugh(2), ('cm_laugh3',) + C.committee_laugh(3),
           ('cm_walk1',) + walk_of(st, 0), ('cm_walk2',) + walk_of(st, 1), ('cm_table',) + C.table()]
    return out


# ---------------------------------------------------------------- the gathering at the vote
def gathering_frames(n=7, asker=2):
    out = []
    for i in range(n):
        for pose in ('stand', 'hands', 'file'):
            out.append(('g%d_%s' % (i, pose),) + MS.man(i, pose))
    out.append(('g%d_ask' % asker,) + MS.man(asker, 'ask'))
    return out


# ---------------------------------------------------------------- the teacher, drafted as his pupils' sergeant
# Ibb's teacher (look A: the green jacket, the grey trousers, his red reader, now the ledger of his pupils' names he
# refuses to fill in), with the cap they gave him, too big, down over his ears, and a whistle on a cord.
CAP = [
    '...6666666...',
    '..677777776..',
    '.67777777776.',
    '5555555555555555',
]
WHISTLE = [
    'z',
    'z',
    'ZI',
]


def sergeant(pose='walk1', flip=False):
    p = pal('sage', 'dark', 'black', 'skin2')
    B = ms3.LEAN
    dy = -1 if pose == 'walk2' else 0
    L = []
    if pose == 'tied':
        L.append(at('post', (3, -10), p))
    if pose == 'wave':
        L.append(at('arm_raise_l', (3, 0), p))
    L += [at(IB.TROUSERS_L, (2, 20), p), at('jacket_l', B.torso, p, 0, dy), at('belt_l', B.belt, p, 0, dy)]
    if pose == 'tied':
        L.append(at('rope_s', (5, 11), p))
    elif pose != 'wave':
        L += [at('forearm_l', B.forearm, p, 0, dy), at('sleeve_l', B.sleeve, p, 0, dy)]
    L.append(at(IB.FACES['elder'], B.face, p, 0, dy))
    L.append(at(IB.HAIR, B.wrap, p, 0, 1 + dy, ink=INK2))
    L.append(at(CAP, (B.wrap[0] - 2, B.wrap[1] - 1), p, 0, dy))          # (too big: it sits on his ears)
    L.append(at(WHISTLE, (B.torso[0] + 7, B.torso[1] + 2), p, 0, dy))
    if pose != 'tied':
        L.append(at(IB.BOOK, (16, 12 + dy), p))
    if pose == 'wave':
        L.append(at('arm_raise_fl', (17, 2), p))
    return compose(L, flip=flip, foot=B.foot)


def sergeant_frames():
    return [('sgt_%s' % k,) + sergeant(k) for k in ('tied', 'wave', 'walk1', 'walk2')]


# ---------------------------------------------------------------- caught by the gas torch
SOOT = [(14, 12, 12), (30, 26, 24), (48, 42, 38), (70, 62, 56), (98, 88, 80)]


def skin_mask(a):
    r, g, b, al = [a[..., k].astype(int) for k in range(4)]
    return (al > 0) & (r > 110) & (r > g + 12) & (g > b + 4) & (r - b > 40)


def scorched(name):
    """His atlas frame, blackened: the brightness kept as five tones of soot, the outline as it was, the white of his eye
    kept (found where his face's top row of skin has its dark eye pixel); his hair is smoking (render_dhamar.js)."""
    im, ax, ay = atlas(name)
    a = np.array(im.convert('RGBA'))
    sk = skin_mask(a)
    lum = (0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2])
    out = a.copy()
    vis = a[..., 3] > 0
    q = np.clip((lum / 255.0 * len(SOOT) * 1.15).astype(int), 0, len(SOOT) - 1)
    for k, c in enumerate(SOOT):
        m = vis & (q == k) & (lum > 40)
        out[m, 0], out[m, 1], out[m, 2] = c
    # the eye: the first dark pixel, from the top, with skin either side of it (the hands up above the head have none)
    H_, W_ = a.shape[0], a.shape[1]
    done = False
    for y in range(H_):
        for x in range(1, W_ - 1):
            if vis[y, x] and not sk[y, x] and lum[y, x] < 90 and sk[y, x - 1] and sk[y, x + 1]:
                out[y, x, :3] = (250, 248, 236)
                out[y, x + 1, :3] = (250, 248, 236)
                done = True
                break
        if done:
            break
    return Image.fromarray(out), ax, ay


def scorched_frames():
    out = []
    for base in ('rifle_worried', 'rifle_youth', 'rifle_angry', 'rifle_qat', 'bomber', 'door'):
        out.append(('sc_%s_run' % base,) + scorched(base + '_up_run'))
        out.append(('sc_%s_pass' % base,) + scorched(base + '_up_pass'))
    out.append(('sc_cook_run',) + scorched('cook_up_stand'))
    out.append(('sc_cook_pass',) + scorched('cook_up_pass'))
    return out


# ---------------------------------------------------------------- the office wall: the Leader's screen, the poster
def outline_pic(im, col=(14, 12, 10, 255)):
    a = np.array(im)
    m = a[..., 3] > 0
    g = np.zeros((a.shape[0] + 2, a.shape[1] + 2), bool)
    g[1:-1, 1:-1] = m
    ring = (g[:-2, 1:-1] | g[2:, 1:-1] | g[1:-1, :-2] | g[1:-1, 2:]) & ~m
    out = a.copy()
    out[ring] = col
    return Image.fromarray(out)


def leader():
    """The Leader's silent screen on the recruiting office's wall: the mock's picture at the game's size in a dark set with
    a red standby light; no face, no voice, no text. Anchored at its top left."""
    pic = MS.leader_screen(s=1)
    w, h = pic.width + 6, pic.height + 7
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], fill=(22, 20, 24, 255))
    d.rectangle([1, 1, w - 2, h - 2], fill=(44, 42, 48, 255))
    im.alpha_composite(pic, (3, 3))
    d.rectangle([3, 3, 3 + pic.width - 1, 3], fill=(120, 132, 126, 90))            # a lighter line along the glass
    d.point((w - 5, h - 3), fill=(220, 40, 30, 255))                                 # the standby light
    for y in range(3, 3 + pic.height, 3):                                            # the scan lines
        for x in range(3, 3 + pic.width):
            r, g, b, al = im.getpixel((x, y))
            im.putpixel((x, y), (int(r * 0.82), int(g * 0.82), int(b * 0.82), al))
    return im, 0, 0


def poster():
    """His laughing face over the stamp window: the laugh frame's head on a paper sheet; no text.
    Anchored at its top left. (Freed, the teacher stamps it: a red mark across the face, render_dhamar.js.)"""
    im, ax, ay = C.committee_laugh(2)
    a = np.array(im)
    head = im.crop((0, 0, im.width, 18))
    bb = head.getbbox()
    head = head.crop(bb)
    w, h = head.width + 6, head.height + 8
    pic = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(pic)
    d.rectangle([0, 0, w - 1, h - 1], fill=(206, 194, 166, 255))
    d.rectangle([1, 1, w - 2, h - 2], fill=(232, 222, 196, 255))
    d.rectangle([2, 2, w - 3, h - 3], fill=(196, 176, 140, 255))                   # the printed ground behind him
    pic.alpha_composite(head, (3, 3))
    d.rectangle([2, h - 4, w - 3, h - 3], fill=(150, 40, 30, 255))                 # a red band along the foot (no words)
    d.point((1, 1), fill=(120, 110, 96, 255)); d.point((w - 2, 1), fill=(120, 110, 96, 255))     # its two pins
    return pic, 0, 0


# ---------------------------------------------------------------- the convoy's lorry, and its load
SLAT = [(150, 48, 32), (196, 160, 52), (60, 120, 84), (40, 82, 140)]


def lorry():
    """A convoy lorry, facing right: the cab white with a blue stripe, its slatted wooden sides painted in bands as Yemeni
    lorries are, a black chassis; the wheels are the atlas's (render_dhamar.js puts them at -44, -22 and +40). The anchor
    is on the ground under the middle; its bed's floor is 30 above it."""
    W_, H_ = 136, 52
    im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    g = H_ - 1
    # chassis and bumper
    d.rectangle([4, g - 14, 128, g - 10], fill=(28, 26, 26, 255))
    d.rectangle([124, g - 16, 133, g - 10], fill=(60, 60, 64, 255))
    # the bed: slatted sides, four painted bands, the posts
    bx0, bx1, by0, by1 = 2, 96, g - 40, g - 15
    for k, y in enumerate(range(by0, by1, 6)):
        c = SLAT[k % len(SLAT)]
        d.rectangle([bx0, y, bx1, y + 4], fill=c + (255,))
        d.line([(bx0, y), (bx1, y)], fill=tuple(min(255, v + 50) for v in c) + (255,))
        d.line([(bx0, y + 5), (bx1, y + 5)], fill=(30, 22, 16, 255))
    for x in range(bx0, bx1 + 1, 16):
        d.rectangle([x, by0 - 2, x + 2, by1], fill=(70, 46, 26, 255))
    d.rectangle([bx0, by1 - 1, bx1, by1 + 1], fill=(46, 30, 20, 255))
    # the cab
    cx0, cx1, cy0 = 98, 128, g - 44
    d.rectangle([cx0, cy0 + 4, cx1, g - 12], fill=(226, 226, 220, 255))
    d.polygon([(cx0, cy0 + 4), (cx0 + 4, cy0), (cx1 - 6, cy0), (cx1, cy0 + 8), (cx1, cy0 + 12), (cx0, cy0 + 12)], fill=(236, 236, 230, 255))
    d.polygon([(cx1 - 14, cy0 + 3), (cx1 - 6, cy0 + 3), (cx1 - 1, cy0 + 10), (cx1 - 14, cy0 + 10)], fill=(40, 70, 110, 255))      # the windscreen
    d.rectangle([cx0 + 3, cy0 + 4, cx0 + 12, cy0 + 10], fill=(54, 86, 126, 255))                                                 # the side window
    d.rectangle([cx0, cy0 + 16, cx1, cy0 + 19], fill=(40, 90, 170, 255))                                                         # the blue stripe
    d.rectangle([cx1 - 3, cy0 + 22, cx1, cy0 + 25], fill=(250, 236, 160, 255))                                                   # the lamp
    d.line([(cx0 + 14, cy0 + 12), (cx0 + 14, g - 13)], fill=(150, 150, 146, 255))                                                # the door's line
    d.rectangle([cx0 + 9, cy0 + 20, cx0 + 12, cy0 + 21], fill=(80, 80, 84, 255))                                                 # its handle
    # the wheel arches
    for wx in (26, 48, 116):
        d.ellipse([wx - 12, g - 23, wx + 12, g + 1], fill=(0, 0, 0, 0))
    im = outline_pic(im)
    return im, 68, H_ - 1


def rows_pic(rows, p):
    return ms3.part([r.ljust(max(len(x) for x in rows), '.') for r in rows], p)


def load_frames():
    p = MR.P
    goat = rows_pic(MR.GOAT, p)
    g2 = MR.GOAT[:3] + ['.w.w..w.w'[:8], '.u.u..u.u'[:8]]
    out = [('goat1', goat, 4, goat.height - 1), ('goat2', rows_pic(g2, p), 4, goat.height - 1)]
    horse = rows_pic(MR.HORSE, p)
    out.append(('horse', horse, 5, horse.height - 1))
    chair = rows_pic(MR.CHAIR, p)
    out.append(('chair', chair, 3, chair.height - 1))
    out.append(('lorry',) + lorry())
    return out


# ---------------------------------------------------------------- the sheet
def frames():
    items = []
    items += committee_frames()
    items += gathering_frames()
    items += sergeant_frames()
    items += IB.kid_frames() + IB.yazeed_low()
    items += scorched_frames()
    items.append(('leader',) + leader())
    items.append(('poster',) + poster())
    items += load_frames()
    return items


def sheet():
    items = frames()
    W = 512
    x = y = rowh = 0
    place = []
    for n, im, ax, ay in sorted(items, key=lambda q: (-q[1].height, q[0])):
        if x + im.width + 1 > W:
            x = 0; y += rowh + 1; rowh = 0
        place.append((n, im, x, y, ax, ay))
        x += im.width + 1; rowh = max(rowh, im.height)
    H = y + rowh
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    meta = {}
    for n, im, x, y, ax, ay in place:
        out.alpha_composite(im.convert('RGBA'), (x, y))
        meta[n] = [x, y, im.width, im.height, int(ax), int(ay)]
    return out, meta


if __name__ == '__main__':
    sh, meta = sheet()
    if '--look' in sys.argv:
        bg = Image.new('RGBA', sh.size, (120, 130, 150, 255))
        bg.alpha_composite(sh)
        p = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/dh/dhamar_look.png'
        bg.resize((sh.width * 3, sh.height * 3), Image.NEAREST).save(p)
        print('proof', p, sh.size)
    else:
        sh.save(os.path.join(OUT, 'dhamar.png'), optimize=True)
        json.dump(dict(frames=meta), open(os.path.join(GEN, 'dhamar_sprites.json'), 'w'), separators=(',', ':'))
        print('dhamar sheet %dx%d, %d frames, %d bytes' % (sh.width, sh.height, len(meta), os.path.getsize(os.path.join(OUT, 'dhamar.png'))))
