# mock_dhamar_scenes.py - Dhamar (Mission 5, the Wadi), stage 1 (10 Nov): three of the plan's five mocks, drawn by the
# development run before any Dhamar code (the 24 Oct rule: a mock before a new mechanic; the stage plan approved
# 10 Nov 03:18). Nothing here is game art yet.
#   (C) the vote in the steam: a storyboard of zone 3's rally at Hammam Ali in four panels, each the game's logical
#       screen (468 x 216), with the game's own sprites (mock/ms3.py's cast, game/tools/committee_sprites.py) over a
#       painted bathhouse: he convenes alone; the hand in the steam asks about the wages and he laughs until a coin
#       rings on the stone; Yazeed arrives and the vote is on whether he is there (shots pass: nobody here can be hit,
#       Ibb's rally rule); the gathering drafted in one motion and filed onto the lorries.
#   (D) the Leader's silent screen: the recruiting office's wall set, a pointing finger, no face, no voice, no text.
#   (E) the Negotiator's first video from his hotel: the bathrobe, the minibar, the watch.
#   python3 mock_dhamar_scenes.py   -> dhamar/s1/mock_steam.png, mock_leader_screen.png, mock_hotel_video.png
import os, sys, json, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'game', 'tools'))
import numpy as np
from PIL import Image, ImageDraw
import px
from px import new, blit, rect, text, FONT_M
import ms3
from ms3 import pal, at, done, PARTS, FACES, WRAPS, LEAN, INK2
import committee_sprites as C

GAME = os.path.join(HERE, '..', 'game')
OUT = os.path.join(HERE, '..', 'dhamar', 's1')
W, H = px.W, px.H
GROUND = 184                       # the play floor, as the Strait's ROAD_Y

_A = {}


def atlas(name, flip=False):
    if not _A:
        _A['img'] = Image.open(os.path.join(GAME, 'art', 'out', 'atlas.png')).convert('RGBA')
        _A['fr'] = json.load(open(os.path.join(GAME, 'gen', 'atlas.json')))['frames']
    fx, fy, w, h, ax, ay = _A['fr'][name]
    f = _A['img'].crop((fx, fy, fx + w, fy + h))
    if flip:
        f = f.transpose(Image.FLIP_LEFT_RIGHT)
        ax = w - 1 - ax
    return f, ax, ay


def put(im, frame, x, y):
    """Draw a (image, ax, ay) frame with its anchor at (x, y)."""
    f, ax, ay = frame
    im.alpha_composite(f, (int(x - ax), int(y - ay)))


# ---------------------------------------------------------------- the gathering: men in mismatched clothes, no armbands
LOOKS = [  # (top, lower, wrap, skin, face, headwear)
    ('khaki', 'cream', 'white', 'skin2', 'worried', 'check_l'),
    ('maroon', 'sand', 'turban', 'skin1', 'youth', 'cap'),
    ('blue', 'white', 'white', 'skin3', 'angry', 'kufiya'),
    ('dark', 'cream', 'turban', 'skin2', 'elder', 'check_l'),
    ('olive', 'sand', 'white', 'skin1', 'salem', 'cap'),
    ('sage', 'cream', 'white', 'skin2', 'cook', 'pot'),
    ('navy', 'white', 'turban', 'skin3', 'youth', 'check_l'),
    ('teal', 'cream', 'white', 'skin2', 'worried', 'kufiya'),
    ('ochre', 'sand', 'turban', 'skin1', 'qat_l', 'check_l'),
    ('rose', 'white', 'white', 'skin2', 'youth', 'cap'),
]


def man(i, pose='stand', flip=False):
    """One of the gathering: the lean build without the rifle or the armband. pose: stand / hands (both up) / ask (one
    arm forward, leaning in) / file (walking, a bundle on the shoulder)."""
    top, lower, wrap, skin, face, hw = LOOKS[i % len(LOOKS)]
    p = pal(top, lower, wrap, skin)
    p['9'] = ('#b8301c', '#2c5a8c', '#3c6a3c', '#8c4a1c')[i % 4]
    B = LEAN
    L = []
    if pose == 'hands':
        L.append(at('arm_raise_l', (3, 0), p))
    L += [at('legs_l', B.legs, p), at('futa_l', B.futa, p), at('jacket_l', B.torso, p), at('belt_l', B.belt, p)]
    if pose in ('stand', 'file'):
        L += [at('forearm_l', B.forearm, p), at('sleeve_l', B.sleeve, p)]
    elif pose == 'ask':
        L += [at('forearm_up_l', (B.forearm[0] + 2, B.forearm[1] - 3), p), at('sleeve_l', B.sleeve, p)]
    dx = 1 if pose == 'ask' else 0
    if hw == 'check_l':
        L.append(at(WRAPS['check_end'], B.wrap, p, dx - 1, 6, ink=INK2))
    L.append(at(FACES[face], B.face, p, dx))
    L.append(at(WRAPS[hw], B.wrap, p, dx, 0, ink=INK2))
    if pose == 'hands':
        L.append(at('arm_raise_fl', (17, 2), p))
    return done(L, flip, B.foot)


# ---------------------------------------------------------------- Hammam Ali: the bathhouse, the pools, the car park
SKY = ('#9fc4dc', '#c9dce6', '#e8e6dc')
STONE, STONE_D, STONE_L = (150, 134, 104, 255), (108, 94, 70, 255), (190, 176, 146, 255)
WATER, WATER_L = (54, 102, 112, 255), (110, 160, 160, 255)
HILL, HILL_D = (120, 104, 86, 255), (92, 78, 62, 255)


def bathhouse():
    im = new(W, H, px.hexc(SKY[0]))
    d = ImageDraw.Draw(im)
    for y in range(0, 120):                                   # the cold bright sky, paler toward the plain
        t = y / 120
        c = tuple(int(a * (1 - t) + b * t) for a, b in zip(px.hexc(SKY[0])[:3], px.hexc(SKY[2])[:3])) + (255,)
        d.line([(0, y), (W, y)], fill=c)
    r = random.Random(5)
    pts = [(0, 96)]                                           # the plateau's hills, low and dry
    for x in range(0, W + 40, 40):
        pts.append((x, 84 + r.randrange(0, 18)))
    d.polygon(pts + [(W, 120), (0, 120)], fill=HILL)
    d.polygon([(p[0], p[1] + 8) for p in pts] + [(W, 120), (0, 120)], fill=HILL_D)
    # the car park at the back, left: a flat sandy lot and the convoy's lorries
    d.rectangle([0, 112, W, 134], fill=(176, 160, 124, 255))
    for x, nm in ((40, 'truck_olive'), (128, 'truck_sand'), (216, 'truck_olive')):
        put(im, atlas(nm, flip=True), x, 134)
    # the bathhouse: a long stone wall with arches and a dome, behind the pools
    d.rectangle([250, 60, W, 136], fill=STONE)
    d.rectangle([250, 60, W, 63], fill=STONE_L)
    d.ellipse([330, 24, 420, 70], fill=STONE_L, outline=STONE_D)
    d.rectangle([330, 48, 420, 62], fill=STONE_L)
    for ax in (270, 318, 366, 414):
        d.rounded_rectangle([ax, 86, ax + 30, 136], radius=15, fill=(40, 36, 32, 255))
        d.arc([ax - 1, 85, ax + 31, 117], 180, 360, fill=STONE_D, width=2)
    for y in range(68, 136, 8):                               # courses of stone
        for x in range(250 + (y // 8 % 2) * 10, W, 20):
            d.point((x, y), fill=STONE_D)
    # the stone floor and the pools
    d.rectangle([0, 136, W, H], fill=STONE)
    for y in range(140, H, 6):
        d.line([(0, y), (W, y)], fill=STONE_D)
        for x in range((y // 6 % 2) * 12, W, 24):
            d.line([(x, y), (x, y + 5)], fill=STONE_D)
    d.rectangle([0, GROUND, W, GROUND + 1], fill=STONE_L)
    # the pools: one in the foreground below the floor's edge, one behind the floor against the bathhouse's wall
    d.rectangle([250, 136, W, 142], fill=WATER); d.rectangle([250, 142, W, 144], fill=STONE_L)
    d.rectangle([14, GROUND + 6, 454, H], fill=WATER)
    d.rectangle([10, GROUND + 2, 458, GROUND + 6], fill=STONE_L)
    d.rectangle([10, GROUND + 6, 13, H], fill=STONE_D); d.rectangle([455, GROUND + 6, 458, H], fill=STONE_D)
    for k in range(20, 450, 14):
        d.line([(k, GROUND + 12 + (k // 7) % 3 * 6), (k + 7, GROUND + 12 + (k // 7) % 3 * 6)], fill=WATER_L)
    return im


def steam_layer(seed=2, heavy=1.0):
    """A pale translucent sheet with holes, dithered, lying over the pools and the people: the springs' steam."""
    r = np.random.RandomState(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    base = np.zeros((H, W))
    for cx, cy, sx, sy in ((110, 200, 120, 22), (340, 200, 120, 22), (234, 176, 220, 14), (380, 140, 70, 8)):
        base += np.exp(-(((xx - cx) / sx) ** 2 + ((yy - cy) / sy) ** 2))
    n = r.rand(H // 8 + 1, W // 8 + 1)
    n = np.kron(n, np.ones((8, 8)))[:H, :W]
    n2 = np.kron(r.rand(H // 3 + 1, W // 3 + 1), np.ones((3, 3)))[:H, :W]
    a = (base * heavy * (0.55 + 0.45 * n) * (0.7 + 0.3 * n2)).clip(0, 1)
    bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
    bm = np.tile(bayer, (H // 4 + 1, W // 4 + 1))[:H, :W]
    lvl = np.where(a > bm, np.where(a > 0.75, 170, np.where(a > 0.45, 120, 70)), 0).astype(np.uint8)
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = 236, 240, 240
    rgba[..., 3] = lvl
    return Image.fromarray(rgba)


def wisps(im, seed=3):
    r = random.Random(seed)
    for k in range(3):
        f = atlas('steam%d' % (k % 3))
        im.alpha_composite(f[0], (r.randrange(10, W - 40), GROUND + 8 - f[2] + r.randrange(-4, 10)))


# ---------------------------------------------------------------- the four panels
def panel(k):
    im = bathhouse()
    wisps(im, 3 + k)
    ground = GROUND
    tbl = C.table()
    gathering_x = [230, 262, 288, 318, 342, 372, 398, 428]
    if k == 0:
        # convening alone: him at the table with the stamp, the sheet with its one name; the gathering in the steam, facing him
        put(im, C.committee('half'), 150, ground)
        put(im, tbl, 184, ground)
        for i, x in enumerate(gathering_x):
            put(im, man(i, 'stand', flip=True), x, ground + (i % 2) * 2)
        im.alpha_composite(steam_layer(2, 0.9))
    elif k == 1:
        # the hand in the steam asks about the wages: he laughs, holding the table; a coin rings on the stone
        put(im, C.committee_laugh(2), 150, ground)
        put(im, tbl, 184, ground)
        for i, x in enumerate(gathering_x):
            pose = 'ask' if i == 1 else 'hands'
            put(im, man(i, pose, flip=True), x, ground + (i % 2) * 2)
        im.alpha_composite(steam_layer(5, 0.9))
        d = ImageDraw.Draw(im)
        cx, cy = 176, ground - 1
        d.rectangle([cx, cy - 1, cx + 1, cy], fill=(255, 226, 100, 255))        # the coin, landing
        d.rectangle([cx, cy - 10, cx + 1, cy - 9], fill=(212, 156, 28, 255))    # where it fell from
        for rr in (4, 8, 12):                                                    # the ring on the stone
            d.ellipse([cx - rr, cy - rr // 3, cx + rr + 1, cy + rr // 3], outline=(255, 240, 180, 200))
    elif k == 2:
        # Yazeed arrives from the left, rifle up; the vote on whether he is there; his shots pass through everyone
        put(im, ms3.yazeed(), 56, ground)
        put(im, C.committee_vote(), 150, ground)
        put(im, tbl, 184, ground)
        for i, x in enumerate(gathering_x):
            put(im, man(i, 'hands', flip=True), x, ground + (i % 2) * 2)
        for bx in (120, 200, 290, 380):
            put(im, atlas('fx_tracer'), bx, ground - 22)
        im.alpha_composite(steam_layer(7, 0.8))
    else:
        # drafted in one motion: the men file right to the lorries, stamped one by one; the table left with its sheet
        put(im, tbl, 96, ground)
        for i, x in enumerate((150, 184, 216, 250, 286, 318, 350, 384)):
            put(im, man(i, 'file'), x, ground + (i % 2) * 2)
        put(im, C.committee('closed', flip=True), 436, ground)
        im.alpha_composite(steam_layer(9, 0.7))
    return im


CAPTIONS = ('1. He convenes, moves, seconds, carries. Alone.', '2. "And the wages?" The laugh. A coin rings.',
            '3. Yazeed arrives. Motion denied. Nothing here is hit.', '4. Drafted in one motion. To the lorries.')


def storyboard():
    gap, strip = 6, 14
    out = new(W * 2 + gap * 3, (H + strip) * 2 + gap * 3, (28, 26, 30, 255))
    for k in range(4):
        x = gap + (k % 2) * (W + gap)
        y = gap + (k // 2) * (H + strip + gap)
        out.alpha_composite(panel(k), (x, y))
        text(out, x + 4, y + H + 4, CAPTIONS[k], FONT_M, '#e8e2d0')
    return px.scale(out, 2)


# ---------------------------------------------------------------- screens: a 144 x 96 picture in a dark set, scanlines
def _scanlines(im, every=3, dim=0.86):
    a = np.asarray(im.convert('RGBA')).astype(float)
    a[::every, :, :3] *= dim
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def framed(pic, live=True, playbar=False):
    """The picture in a television's dark frame, as Ibb's screens hang: a 6 px bezel, a lit edge, the live dot."""
    b = 6
    out = new(pic.width + 2 * b, pic.height + 2 * b + (8 if playbar else 0), (22, 22, 26, 255))
    d = ImageDraw.Draw(out)
    d.rectangle([1, 1, out.width - 2, out.height - 2], outline=(58, 58, 66, 255))
    out.alpha_composite(_scanlines(pic), (b, b))
    if live:
        d.ellipse([out.width - b - 6, b + 2, out.width - b - 2, b + 6], fill=(236, 40, 40, 255))
    if playbar:
        y = b + pic.height + 2
        d.rectangle([b, y, out.width - b - 1, y + 3], fill=(60, 60, 68, 255))
        d.rectangle([b, y, b + pic.width // 4, y + 3], fill=(220, 60, 50, 255))
        d.polygon([(b, out.height - 3), (b, out.height - 1), (b + 2, out.height - 2)], fill=(200, 200, 200, 255))
    return out


def leader_screen(s=3):
    """The Leader: a dim figure from the shoulders up, a shadowed brow and no face, one hand raised with the finger
    pointing out of the screen and filling a third of the picture; a plain curtain; silent."""
    Wd, Hd = 48 * s, 32 * s
    im = Image.new('RGBA', (Wd, Hd), (26, 34, 30, 255))
    d = ImageDraw.Draw(im)
    for x in range(0, Wd, s + s // 2):                                    # the curtain's folds, dark green
        d.line([(x, 0), (x, Hd)], fill=(18, 26, 22, 255) if (x // s) % 2 else (34, 44, 38, 255))
    cx = 18 * s
    OL = (8, 8, 10, 255)
    cloak = (24, 20, 24, 255); cloak_l = (40, 34, 40, 255)
    skin_sh = (70, 48, 40, 255); skin = (150, 108, 84, 255); skin_l = (196, 150, 120, 255)
    # the shoulders and the cloak, the head a dark shape, the brow the one lit edge
    d.polygon([(cx - 17 * s, Hd), (cx - 12 * s, 17 * s), (cx - 5 * s, 14 * s), (cx + 5 * s, 14 * s), (cx + 12 * s, 17 * s), (cx + 17 * s, Hd)],
              fill=cloak, outline=OL)
    d.line([(cx - 12 * s, 17 * s), (cx - 15 * s, Hd)], fill=cloak_l, width=max(1, s // 2))
    d.rounded_rectangle([cx - 5 * s, 3 * s, cx + 5 * s, 15 * s], radius=3 * s, fill=(36, 28, 28, 255), outline=OL)
    d.ellipse([cx - 6 * s, 0, cx + 6 * s, 9 * s], fill=(96, 92, 86, 255), outline=OL)                  # the wrap, wound round the head
    d.ellipse([cx - 5 * s, 1 * s, cx + 5 * s, 5 * s], fill=(120, 116, 108, 255))
    d.rectangle([cx - 6 * s, 5 * s, cx + 6 * s, 6 * s], fill=(72, 68, 64, 255))
    d.polygon([(cx + 5 * s, 6 * s), (cx + 9 * s, 7 * s), (cx + 8 * s, 14 * s), (cx + 5 * s, 12 * s)], fill=(96, 92, 86, 255), outline=OL)  # its end, hanging
    d.rectangle([cx - 4 * s, 6 * s, cx + 4 * s, 7 * s], fill=skin_sh)                  # the brow, the one lit line
    d.rectangle([cx - 3 * s, 8 * s, cx + 3 * s, 9 * s - s // 2], fill=(20, 14, 14, 255))  # the eyes' shadow
    d.polygon([(cx - 4 * s, 11 * s), (cx + 4 * s, 11 * s), (cx + 3 * s, 15 * s), (cx - 3 * s, 15 * s)], fill=(24, 18, 18, 255))  # the beard
    # the arm comes from the shoulder toward the camera, Uncle-Sam style: the cuff behind, the fist behind that with the
    # thumb along its top edge, a short finger body, and the big round fingertip nearest the viewer, pointing at us
    fx, fy = cx + 13 * s, 19 * s
    d.polygon([(cx + 7 * s, 17 * s), (cx + 14 * s, 16 * s), (fx + 6 * s, fy + 2 * s), (fx - 6 * s, fy + 6 * s)], fill=cloak, outline=OL)  # the sleeve
    d.rounded_rectangle([fx - 7 * s, fy - 4 * s, fx + 7 * s, fy + 7 * s], radius=2 * s, fill=cloak_l, outline=OL)               # the cuff
    d.rounded_rectangle([fx - 7 * s, fy - 5 * s, fx + 7 * s, fy + 6 * s], radius=3 * s, fill=skin, outline=OL)                 # the fist
    for k in range(3):                                                                                                       # the curled fingers
        d.line([(fx - 4 * s + k * 3 * s, fy + 3 * s), (fx - 2 * s + k * 3 * s, fy + 3 * s)], fill=skin_sh, width=max(1, s // 2))
    d.rounded_rectangle([fx - 7 * s, fy - 8 * s, fx + 4 * s, fy - 4 * s], radius=s, fill=skin_l, outline=OL)                  # the thumb, along the top
    d.rounded_rectangle([fx - 5 * s, fy - 6 * s, fx + 1 * s, fy + 1 * s], radius=2 * s, fill=skin, outline=OL)                # the finger's body, short
    d.ellipse([fx - 7 * s, fy - 8 * s, fx + 1 * s, fy], fill=skin_l, outline=OL)                                              # the fingertip, nearest
    d.ellipse([fx - 5 * s, fy - 6 * s, fx - 1 * s, fy - 2 * s], fill=(222, 178, 148, 255))                                    # the pad
    d.arc([fx - 5 * s, fy - 6 * s, fx - 1 * s, fy - 2 * s], 200, 340, fill=skin_sh, width=max(1, s // 2))                     # the nail's edge
    return im


def hotel_video(s=3):
    """The Negotiator's first video: a hotel room abroad at night, the bathrobe, the minibar, the watch held up."""
    Wd, Hd = 48 * s, 32 * s
    im = Image.new('RGBA', (Wd, Hd), (214, 196, 160, 255))
    d = ImageDraw.Draw(im)
    OL = (58, 38, 34, 255)
    # the wall, a window on the left with a city at night, a lamp on the right
    d.rectangle([2 * s, 2 * s, 16 * s, 20 * s], fill=(18, 22, 44, 255), outline=(120, 100, 70, 255), width=max(1, s // 2))
    r = random.Random(11)
    for k in range(60):
        x, y = r.randrange(3 * s, 15 * s), r.randrange(8 * s, 19 * s)
        d.point((x, y), fill=(255, 226, 150, 255) if r.random() < 0.6 else (160, 200, 240, 255))
    for bx, by in ((4, 9), (8, 6), (12, 11)):                                        # the towers' outlines
        d.rectangle([bx * s, by * s, bx * s + 3 * s, 20 * s], outline=(40, 46, 70, 255))
    d.rectangle([1 * s, 20 * s, 17 * s, 21 * s], fill=(140, 110, 70, 255))            # the sill, the curtains
    d.rectangle([0, 1 * s, 2 * s, 22 * s], fill=(150, 60, 60, 255)); d.rectangle([16 * s, 1 * s, 18 * s, 22 * s], fill=(150, 60, 60, 255))
    d.polygon([(39 * s, 4 * s), (47 * s, 4 * s), (48 * s, 10 * s), (38 * s, 10 * s)], fill=(248, 230, 170, 255), outline=OL)  # the lamp
    d.rectangle([42 * s + s // 2, 10 * s, 43 * s + s // 2, 20 * s], fill=(120, 90, 50, 255))
    d.ellipse([36 * s, 8 * s, 50 * s, 16 * s], fill=(234, 220, 180, 60))
    # the bed's edge he sits on, the nightstand with the hotel phone
    d.rectangle([0, 23 * s, Wd, Hd], fill=(120, 40, 44, 255))                         # the bedspread
    d.rectangle([0, 23 * s, Wd, 24 * s], fill=(170, 70, 74, 255))
    d.rectangle([38 * s, 20 * s, 48 * s, 23 * s], fill=(96, 64, 32, 255), outline=OL)  # nightstand
    d.rounded_rectangle([40 * s, 17 * s, 46 * s, 20 * s], radius=s, fill=(236, 232, 220, 255), outline=OL)  # the phone
    d.rounded_rectangle([40 * s, 16 * s, 46 * s, 17 * s + s // 2], radius=s // 2, fill=(210, 206, 196, 255), outline=OL)
    # the minibar, open, with its little bottles, low on the right
    d.rectangle([34 * s, 24 * s, 46 * s, Hd], fill=(60, 58, 60, 255), outline=OL)
    d.rectangle([35 * s, 25 * s, 45 * s, Hd], fill=(20, 24, 30, 255))
    for k, col in enumerate(((220, 170, 60), (90, 160, 90), (200, 80, 70), (120, 160, 220), (240, 220, 160))):
        bx = 36 * s + k * 2 * s
        d.rectangle([bx, 27 * s, bx + s, 30 * s], fill=col + (255,))
        d.rectangle([bx, 26 * s, bx + s // 2, 27 * s], fill=col + (255,))
    d.rectangle([46 * s, 24 * s, 48 * s, 26 * s], fill=(236, 232, 220, 255))           # the door swung open
    # the man: the bathrobe, the shawl collar, the belt; round, pleased, moustache, hair neat
    cx = 24 * s
    skin, skin_d = (222, 186, 150, 255), (190, 148, 110, 255)
    d.polygon([(cx - 12 * s, Hd), (cx - 10 * s, 16 * s), (cx - 4 * s, 14 * s), (cx + 4 * s, 14 * s), (cx + 10 * s, 16 * s), (cx + 12 * s, Hd)],
              fill=(246, 244, 238, 255), outline=OL)                                     # the robe
    d.polygon([(cx - 4 * s, 14 * s), (cx, 22 * s), (cx + 4 * s, 14 * s), (cx + 2 * s, 14 * s), (cx, 19 * s), (cx - 2 * s, 14 * s)],
              fill=(220, 214, 200, 255), outline=OL)                                     # the shawl collar's V
    d.polygon([(cx - 3 * s, 15 * s), (cx + 3 * s, 15 * s), (cx, 21 * s)], fill=skin_d)   # the chest in the V
    d.rectangle([cx - 10 * s, 27 * s, cx + 10 * s, 28 * s + s // 2], fill=(220, 214, 200, 255), outline=OL)  # the belt
    d.rectangle([cx - 3 * s, 12 * s, cx + 3 * s, 15 * s], fill=skin_d, outline=OL)       # neck
    d.ellipse([cx - 6 * s, 2 * s, cx + 6 * s, 14 * s], fill=skin, outline=OL)             # a round, well-fed face
    d.ellipse([cx - 7 * s, 5 * s, cx - 5 * s, 8 * s], fill=skin, outline=OL); d.ellipse([cx + 5 * s, 5 * s, cx + 7 * s, 8 * s], fill=skin, outline=OL)
    d.chord([cx - 6 * s, 1 * s, cx + 6 * s, 7 * s], 180, 360, fill=(40, 30, 28, 255), outline=OL)   # neat hair
    d.rectangle([cx - 6 * s, 4 * s, cx - 5 * s, 6 * s], fill=(40, 30, 28, 255)); d.rectangle([cx + 5 * s, 4 * s, cx + 6 * s, 6 * s], fill=(40, 30, 28, 255))
    for sx in (-1, 1):                                                                     # the eyes, creased with pleasure
        ex = cx + sx * 2 * s + (s // 2 if sx < 0 else -s // 2)
        d.arc([ex - s - s // 2, 6 * s, ex + s + s // 2, 8 * s + s // 2], 200, 340, fill=OL, width=max(1, s // 2))
    d.rectangle([cx - 2 * s - s // 2, 9 * s, cx + 2 * s + s // 2, 9 * s + s], fill=(60, 44, 40, 255))       # the moustache
    d.arc([cx - 3 * s, 8 * s, cx + 3 * s, 12 * s], 10, 170, fill=(120, 48, 50, 255), width=max(1, s // 2))  # the smile
    d.point((cx + s, 8 * s), fill=(236, 206, 176, 255))
    # the near arm held up to the camera: the sleeve, the wrist, and the watch, gold and large
    d.polygon([(cx + 8 * s, 18 * s), (cx + 12 * s, 17 * s), (cx + 15 * s, 8 * s), (cx + 11 * s, 7 * s)], fill=(246, 244, 238, 255), outline=OL)
    d.rounded_rectangle([cx + 11 * s, 2 * s, cx + 16 * s, 9 * s], radius=2 * s, fill=skin, outline=OL)           # the hand, fingers curled
    for k in range(3):
        d.line([(cx + 12 * s + k * s + s // 2, 3 * s), (cx + 12 * s + k * s + s // 2, 5 * s)], fill=skin_d)
    d.rectangle([cx + 10 * s, 8 * s, cx + 17 * s, 11 * s], fill=(212, 170, 40, 255), outline=OL)                  # the band
    d.ellipse([cx + 10 * s, 6 * s, cx + 17 * s, 13 * s], fill=(228, 186, 74, 255), outline=OL)                    # the case
    d.ellipse([cx + 11 * s + s // 2, 7 * s + s // 2, cx + 15 * s + s // 2, 11 * s + s // 2], fill=(246, 246, 240, 255), outline=(170, 126, 40, 255))
    d.line([(cx + 13 * s + s // 2, 9 * s + s // 2), (cx + 13 * s + s // 2, 8 * s)], fill=OL); d.line([(cx + 13 * s + s // 2, 9 * s + s // 2), (cx + 15 * s, 9 * s + s // 2)], fill=OL)
    d.point((cx + 11 * s, 7 * s), fill=(255, 255, 255, 255)); d.point((cx + 16 * s, 12 * s), fill=(255, 255, 255, 255))  # the glint
    return im


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    storyboard().save(os.path.join(OUT, 'mock_steam.png'))
    px.scale(framed(leader_screen()), 4).save(os.path.join(OUT, 'mock_leader_screen.png'))
    px.scale(framed(hotel_video(), live=False, playbar=True), 4).save(os.path.join(OUT, 'mock_hotel_video.png'))
    print('wrote', OUT)
