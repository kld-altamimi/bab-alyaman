# mock_dhamar_road.py - Dhamar (Mission 5, the Wadi), stage 1 (10 Nov): two of the plan's five mocks, drawn by the
# development run before any Dhamar code, with the game's own sprites (the atlas) and the Committee's mock sheet
# (game/tools/committee_sprites.py), at the game's logical screen (468 x 216), so Khaled can judge the look at the size
# it will play. Neither picture is game art: the plain, the lorries' loads, the checkpoint and the pass are painted by
# hand here; the real zones get their painters (mock/stage_dhamar*.py) once he says yes.
#   (A) the checkpoint on wheels: Qa' Jahran at dawn, Salem's 4x4 with Yazeed in the roof ring, the barrier, the stamp
#       window, the loudhailer pole, the queue being counted, the convoy's lorry going the other way (the barber's chair,
#       the horse that refuses), the goats under the lifted end, one banknote across the road.
#   (B) the money fight on the lorries: Naqil Yislah, three lorries across the road, the Committee in the vote on the
#       middle bed behind his table, the resolution barrier below him, notes falling, a drafted man walking off with one,
#       a real Zanabeel stepping over one toward Yazeed, the pile at a wheel.
#   python3 mock_dhamar_road.py   -> dhamar/s1/mock_checkpoint.png, dhamar/s1/mock_fight.png (3x)
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'game', 'tools'))
from PIL import Image, ImageDraw
import px
import ms3
import committee_sprites as C

GAME = os.path.join(HERE, '..', 'game')
OUT = os.path.join(HERE, '..', 'dhamar', 's1')
W, H = px.W, px.H
_A = {}


def atlas():
    if not _A:
        _A['img'] = Image.open(os.path.join(GAME, 'art', 'out', 'atlas.png')).convert('RGBA')
        _A['fr'] = json.load(open(os.path.join(GAME, 'gen', 'atlas.json')))['frames']
    return _A


def spr(im, name, x, y, flip=False):
    """An atlas frame with its anchor at (x, y), as the game's spr() draws it."""
    A = atlas()
    fx, fy, w, h, ax, ay = A['fr'][name]
    f = A['img'].crop((fx, fy, fx + w, fy + h))
    if flip:
        f = f.transpose(Image.FLIP_LEFT_RIGHT)
        ax = w - 1 - ax
    im.alpha_composite(f, (int(x - ax), int(y - ay)))


def put(im, frame, x, y, flip=False):
    """A composed cast frame (image, fx, fy) with its anchor at (x, y)."""
    f, fx, fy = frame
    if flip:
        f = f.transpose(Image.FLIP_LEFT_RIGHT)
        fx = f.width - 1 - fx
    im.alpha_composite(f, (int(x - fx), int(y - fy)))


def bands(im, y0, y1, cols):
    """Horizontal colour bands from y0 to y1, a checker dither between neighbours."""
    d = ImageDraw.Draw(im)
    n = len(cols)
    span = max(1, y1 - y0)
    for y in range(y0, y1):
        t = (y - y0) / span * (n - 1)
        i = int(t)
        fr = t - i
        for x in range(0, im.width, 2):
            c = cols[min(n - 1, i + 1)] if (fr > 0.5 and (x // 2 + y) % 2 == 0) or (fr > 0.75) else cols[i]
            d.line([(x, y), (x + 1, y)], fill=c)


def hills(im, y, amp, seed, cols, step=1):
    """A line of far hills: a soft noise skyline filled down to the bottom in two tones."""
    import random
    r = random.Random(seed)
    d = ImageDraw.Draw(im)
    pts = []
    k = r.uniform(0, 6.28)
    import math
    for x in range(0, im.width + 1, step):
        h = amp * (0.55 * math.sin(x / 61.0 + k) + 0.3 * math.sin(x / 23.0 + 2 * k) + 0.15 * math.sin(x / 9.0 + 3 * k))
        pts.append((x, int(y + h)))
    for x, yy in pts:
        d.line([(x, yy), (x, im.height)], fill=cols[0])
        d.point((x, yy), fill=cols[1])
        d.line([(x, yy + 1), (x, yy + 3)], fill=cols[1] if x % 3 else cols[0])


def village(im, x, y, w, cols):
    """Far stone houses: a few stacked boxes with a tower."""
    d = ImageDraw.Draw(im)
    import random
    r = random.Random(x)
    cx = x
    while cx < x + w:
        bw, bh = r.randint(5, 9), r.randint(4, 9)
        d.rectangle([cx, y - bh, cx + bw, y], fill=cols[0])
        d.rectangle([cx, y - bh, cx + 1, y], fill=cols[1])
        if r.random() < 0.3:
            d.rectangle([cx + bw - 2, y - bh - 5, cx + bw, y - bh], fill=cols[0])
        cx += bw + r.randint(1, 3)


# ---------------------------------------------------------------- hand-drawn props (the cast's letters, px.sprite)
P = ms3.pal('dark', 'white', 'redchk', 'skin2')
P.update(C.NOTE)
P['9'] = '#f0e4c8'

HORSE = [            # a bay horse on the lorry's bed, head turned back over its shoulder (it refuses)
    '......XY....',
    '.....XYW....',
    '....XYY.....',
    '....XY......',
    'XYYYYYYYX...',
    'YYYYYYYYYX..',
    'XYYYYYYYYY..',
    '.X.X...X.X..',
    '.X.X...X.X..',
    '.A.A...A.A..',
]
GOAT = [
    '......u.',
    '.wwwwwuu',
    'wwwwwwwu',
    '.w.w.w.w',
    '.u.u.u.u',
]
CHAIR = [            # the barber's chair, carried: a red seat on a chrome post
    'LLLLL',
    'LMMML',
    '.zZz.',
    '..z..',
    '.zzz.',
]
POT = [              # the cook's pot helmet seen on a lorry: he is the atlas cook, so this is spare
    'xyyyx',
]
BARRIER = [          # the checkpoint's striped pole
    'JJJJLLLLJJJJLLLLJJJJLLLLJJJJLLLLJJJJLLLLJJJJ',
    'IIIIKKKKIIIIKKKKIIIIKKKKIIIIKKKKIIIIKKKKIIII',
]
LOUDHAILER = [       # the loudhailer on its pole, turned down the road
    '.....IJ',
    '...LLMJ',
    'xKLLLMJ',
    'x.KLLMJ',
    'x...KLI',
    'x......',
    'x......',
    'x......',
    'x......',
    'x......',
    'x......',
    'x......',
    'x......',
    'x......',
    'x......',
    'x......',
    'x......',
    'x......',
    'x......',
    'x......',
]
STAMP_HUT = [        # the stamp window: a small concrete box with a hatch, the counter, a stamp pad on it
    'yyyyyyyyyyyyyyyyyyyyyy',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZxxxxxxxxxxZZZZZZz',
    'zZZZZxUUUUUUUUxZZZZZZz',
    'zZZZZxUUUUUUUUxZZZZZZz',
    'zZZZZxUUUUUUUUxZZZZZZz',
    'zZZZZxUUUUUUUUxZZZZZZz',
    'zZZZZxxxxxxxxxxZZZZZZz',
    'zZZZZXYYYYYYYYYXZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zZZZZZZZZZZZZZZZZZZZZz',
    'zzzzzzzzzzzzzzzzzzzzzz',
]
# the resolution barrier: a low wall of stamped paper (pale sheets on a frame), one big round red stamp mark on it
RESOLUTION = [
    'XJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJX',
    'XJIIJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJIIJJJX',
    'XJJJJJJJJJJJJJJJLLLLLLLJJJJJJJJJJJJJJJJJJJX',
    'XJJJJJJJJJJJJJLLJJJJJJJLLJJJJJJJJJJJJJJJJJX',
    'XJIJJJJJJJJJJLJJJJJJJJJJJLJJJJJJJJJJJJJJIJX',
    'XJJJJJJJJJJJLJJJJLLLLLJJJJLJJJJJJJJJJJJJJJX',
    'XJJJJJJJJJJJLJJJLJJJJJLJJJLJJJJJJJJJJJJJJJX',
    'XJJJJJJJJJJJLJJJLJJJJJLJJJLJJJJJJJJJJJJJJJX',
    'XJIJJJJJJJJJLJJJJLLLLLJJJJLJJJJJJJJJJJJJIJX',
    'XJJJJJJJJJJJJLJJJJJJJJJJJLJJJJJJJJJJJJJJJJX',
    'XJJJJJJJJJJJJJLLJJJJJJJLLJJJJJJJJJJJJJJJJJX',
    'XJJJJJJJJJJJJJJJLLLLLLLJJJJJJJJJJJJJJJJJJJX',
    'XJIIJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJIIJJJX',
    'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
]


def rows_img(rows):
    return px.sprite([r.ljust(max(len(x) for x in rows), '.') for r in rows], P)


def lorry(im, x, y, flip=False, paint='sand'):
    """A convoy lorry: the atlas truck with its wheels, as render.js drawTruck draws it."""
    spr(im, 'truck_' + paint, x, y, flip)
    spr(im, 'wheel0', x - 29, y - 9)
    spr(im, 'wheel0', x + 29, y - 9)


def car(im, x, y, yazeed=True):
    """Salem's 4x4 (the armoured truck since build 17), Yazeed up in the roof ring, as drawCar."""
    if yazeed:
        spr(im, 'yazeed_stand_hmg_fwd', x - 6, y - 10 - 23)
    spr(im, 'shass', x, y)
    spr(im, 'bwheel0', x - 29, y - 11)
    spr(im, 'bwheel0', x + 29, y - 11)


# ---------------------------------------------------------------- (A) the checkpoint on wheels
def checkpoint():
    im = px.new(W, H)
    # dawn over the high plain: a cold sky warming to the horizon, the mountain line, the fields, the highway
    bands(im, 0, 118, [(92, 110, 148), (132, 148, 176), (190, 186, 182), (232, 200, 150), (246, 214, 158)])
    hills(im, 96, 9, 3, [(118, 112, 124), (142, 134, 140)])
    hills(im, 108, 5, 7, [(150, 138, 118), (170, 158, 132)])
    bands(im, 118, 150, [(196, 176, 112), (182, 160, 96), (170, 150, 90)])
    village(im, 60, 119, 40, [(176, 160, 128), (206, 192, 156)])
    village(im, 300, 119, 34, [(176, 160, 128), (206, 192, 156)])
    d = ImageDraw.Draw(im)
    for y in range(122, 150, 4):                              # the wheat's rows
        for x in range(0, W, 7):
            d.point((x + (y % 8), y), fill=(214, 196, 130))
    d.rectangle([0, 150, W, 158], fill=(150, 128, 84))        # the verge
    for x in range(0, W, 5):
        d.point((x, 152 + (x % 3)), fill=(120, 100, 64))
    d.rectangle([0, 158, W, 216], fill=(78, 76, 80))          # the asphalt
    d.rectangle([0, 158, W, 160], fill=(100, 98, 102))
    for x in range(0, W, 24):
        d.rectangle([x, 186, x + 12, 187], fill=(214, 204, 150))   # the centre line
    for x in range(0, W, 3):
        d.point((x, 200 + (x * 7) % 13), fill=(68, 66, 70))
    ROAD = 196                                                # the near lane's ground line
    FAR = 170                                                 # the far lane's
    # the convoy's lorry going the other way (far lane), loaded: drafted men, the barber with his chair, the horse
    lorry(im, 250, FAR, flip=True, paint='olive')
    horse = rows_img(HORSE).resize((24, 20), Image.NEAREST)
    px.blit(im, horse, 250 - 2, FAR - 52)
    for name, dx in [('rifle_worried_up_stand', -36), ('cook_up_stand', -20)]:
        spr(im, name, 250 + dx, FAR - 30, flip=True)
    spr(im, 'rifle_youth_up_stand', 250 + 30, FAR - 30, flip=True)
    px.blit(im, rows_img(CHAIR).resize((10, 10), Image.NEAREST), 250 + 18, FAR - 46)
    # the checkpoint: the stamp window behind the queue, the loudhailer on its pole, sandbags, the barrier across the lane
    px.blit(im, rows_img(STAMP_HUT), 340, 158 - 37 + 2)
    d.rectangle([410, 104, 411, ROAD - 14], fill=(40, 40, 46))
    hail = ms3.part(ms3.MARSHAL['megaphone'], P)
    px.blit(im, hail, 404, 96)
    spr(im, 'rbags', 426, 160)
    spr(im, 'rbags', 464, ROAD + 2)
    # the queue of men being counted, mismatched: a rifleman, the cook in his pot helmet, a youth, a doorman, a bomber
    for name, x, flip in [('rifle_worried_stand', 318, False), ('cook_stand', 338, False), ('rifle_youth_stand', 356, False),
                          ('door_bare_stand', 374, False), ('bomber_stand', 392, False)]:
        spr(im, name, x, ROAD - 14, flip)
    # the striped pole across the road on its post, lifted at the far end; the goats pass under it
    d.rectangle([446, 152, 449, ROAD], fill=(60, 60, 66))
    pole = rows_img(BARRIER).rotate(16, resample=Image.NEAREST, expand=True)
    px.blit(im, pole, 448 - pole.width, ROAD - 34)
    goat = rows_img(GOAT)
    for gx in (404, 416, 428):
        px.blit(im, goat, gx, ROAD - 6)
    # Salem's 4x4 coming up the near lane, Yazeed in the roof ring
    car(im, 110, ROAD)
    # one banknote blowing across the road from the convoy ahead
    n = C.note()[0].rotate(20, resample=Image.NEAREST, expand=True)
    px.blit(im, n, 206, ROAD - 22)
    px.blit(im, C.note()[0], 232, ROAD - 8)
    return im


# ---------------------------------------------------------------- (B) the money fight on the lorries
def fight():
    im = px.new(W, H)
    # the pass: a cold bright sky, the plateau's edge dropping away at the right into haze
    bands(im, 0, 120, [(150, 178, 212), (184, 200, 222), (212, 214, 216), (226, 216, 196)])
    hills(im, 104, 8, 11, [(128, 118, 110), (150, 140, 128)])
    d = ImageDraw.Draw(im)
    d.polygon([(0, 112), (W, 112), (W, 140), (0, 140)], fill=(154, 136, 104))     # the plain behind the road
    hills(im, 124, 3, 5, [(154, 136, 104), (176, 160, 124)])
    d.rectangle([0, 140, W, 216], fill=(80, 78, 82))                                  # the road
    d.rectangle([0, 140, W, 142], fill=(104, 102, 106))
    # the drop beyond the road's edge at the right
    d.polygon([(420, 142), (W, 142), (W, 216), (440, 216)], fill=(112, 100, 84))
    d.polygon([(424, 142), (W, 142), (W, 172), (446, 180)], fill=(190, 196, 206))   # the haze below the edge
    for x in range(424, W, 4):
        d.point((x, 142 + (x % 5)), fill=(140, 128, 108))
    ROAD = 192
    # the three lorries parked across the road, their beds the platforms (the camera holds all three)
    for lx, paint in ((70, 'sand'), (234, 'olive'), (398, 'sand')):
        lorry(im, lx, ROAD - 12, paint=paint)
    BED = ROAD - 12 - 27                                       # the bed's floor, where a man stands on a lorry
    # the Committee in the vote on the middle bed, his table beside him, both hands up: the only second he can be hit
    put(im, C.table(), 196, BED + 1)
    put(im, C.committee_vote(), 228, BED)
    # the resolution barrier on the road below him, stopping low shots
    px.blit(im, rows_img(RESOLUTION), 212, ROAD - 14)
    # the notes falling from him onto the lorries and the road
    nimg = C.note()[0]
    import random
    r = random.Random(5)
    for k, (nx, ny) in enumerate([(236, BED - 46), (252, BED - 36), (222, BED - 26), (270, BED - 14), (244, BED - 6),
                                  (290, ROAD - 30), (210, ROAD - 44), (300, ROAD - 10)]):
        px.blit(im, nimg.rotate(r.choice((-25, 0, 20, 35)), resample=Image.NEAREST, expand=True), nx, ny)
    # the pile at the middle lorry's wheel
    for wx, wy in ((252, ROAD - 2), (256, ROAD - 3), (249, ROAD - 4), (254, ROAD - 6)):
        px.blit(im, C.wad()[0], wx, wy - 4)
    # a drafted man who reached a note walks off right with it, toward the lorries and home (immune from here)
    put(im, ms3.cook(), 340, ROAD, flip=False)
    px.blit(im, nimg, 356, ROAD - 22)
    # a real Zanabeel steps over a note toward Yazeed, rifle up: the difficulty stays
    spr(im, 'rifle_angry_run', 160, ROAD, flip=True)
    px.blit(im, nimg, 150, ROAD - 3)
    # drafted men still coming off the lorries behind him
    spr(im, 'rifle_worried_pass', 52, BED, flip=True)
    spr(im, 'door_bare_stand', 372, BED, flip=True)
    # Yazeed at the left, firing up at the vote
    spr(im, 'yazeed_stand_side_diag', 48, ROAD)
    spr(im, 'fx_muzzle', 62, ROAD - 37)
    for tx in range(80, 200, 14):
        spr(im, 'fx_tracer', tx, ROAD - 40 - (tx - 80) // 3)
    return im


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for name, f in (('mock_checkpoint', checkpoint), ('mock_fight', fight)):
        im = f()
        im.resize((im.width * 3, im.height * 3), Image.NEAREST).save(os.path.join(OUT, name + '.png'))
        print('wrote', name)
