# taiz_sprites.py - Taiz by Apache: the black gunship Salem flies (the teaser's, redrawn at play size), its rotors and its
# gun, the Zanabeel's anti-aircraft gun, the missile man's launcher, the rockets and the missile. Written out as a sheet
# of its own (art/out/taiz.png, gen/taiz_sprites.json) so the main atlas, and everything in it, stays where it is.
#   python3 taiz_sprites.py            (the sheet)      python3 taiz_sprites.py --look    (an enlarged proof, art/out/taiz_look.png)
# No markings of any kind on the Apache: no flag, no roundel, no number.
import sys, os, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock')
import numpy as np
from PIL import Image
from px import new, sprite, outline, silhouette, rgba

OUT = os.path.join(HERE, '..', 'art', 'out')
GEN = os.path.join(HERE, '..', 'gen')

# the teaser's colours: near-black, the moonlit edges, the canopy
PAL = {
    'K': (10, 11, 14), '0': (20, 22, 27), '1': (31, 34, 41), '2': (52, 57, 68), '3': (82, 90, 106),
    'g': (24, 44, 62), 'h': (110, 160, 205), 'G': (40, 70, 96),
    'e': (30, 30, 32), 'E': (52, 44, 44), 'R': (120, 52, 36),     # the engines' exhausts (and the heat inside one)
    'w': (14, 14, 16), 's': (46, 50, 58),                         # wheels, struts
    'p': (40, 44, 40), 'P': (66, 70, 64),                         # the rocket pods
    'm': (38, 42, 50),
}
OUTL = (6, 7, 9)


class Grid:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.c = [['.'] * w for _ in range(h)]

    def span(self, y, x0, x1, ch):
        if 0 <= y < self.h:
            for x in range(max(0, x0), min(self.w - 1, x1) + 1):
                self.c[y][x] = ch

    def dot(self, x, y, ch):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.c[y][x] = ch

    def rows(self):
        return [''.join(r) for r in self.c]


# ---------------------------------------------------------------- the Apache, side on, nose to the right
# The teaser's own (Khaled 21 Oct 05:23: "make the apatche fully black similar to the teaser"): traced from the teaser's
# frames at its own pixels, 120 x 42, its blades and its gun's barrel taken off (pieces of their own: the rotor spins, the
# barrel turns to aim). The body's middle, where the game keeps it (h.x, h.y), is column AX, row AY: under the mast.
# (Second cut, 0.9.52; the first cut's 94 x 28 drawing is in taiz_sprites_0951.py.)
AW, AH, AX, AY = 120, 42, 60, 22
APACHE = [
    '.......................................................KKKKKKKKKK.......................................................',
    '.......................................................K22222222K.......................................................',
    '.......................................................K00000000K.......................................................',
    '.......................................................KKKKKKKKKK.......................................................',
    '....KK0000.2..............................................K00K..........................................................',
    '.....K000002..............................................K00K..........................................................',
    '.....K000002K.............................................K00K..........................................................',
    '.....K0000002.................................03333.......K00K..........................................................',
    '....KK0000002...............................KK000003333333KKKK33333333K.................................................',
    '.....K0000002............................KKKKK000000000000011111111111K.................................................',
    '.....K0000002K...........................KKKKK000000000000111111111111K...KKK2..........................................',
    '.....K0000002K...........................KK0KK000000011111111111111111K...K111KKKKKK....................................',
    '......K0000002..........................KKKKKK0000011111111111111111112.222gggghhhhgK...................................',
    '......K0000002.........................K0KKKKK000011111111111111111111KKKKKggggggggggK..................................',
    '......K0000002K......................KK0000K01100111111111111111111111K00KKKK1ggggggg1K.................................',
    '......K0000002K......................2220000KKKKKK11111111111111111111K000000KKKKKKKKKKKK...............................',
    '......K0000000.22.22........22222222.0000000000000KKKKKKKKKKKKKKKKKKKKK0000000000000000KKKKKKKKKK.......................',
    '.....K000000222..2..00002222K000000020000000000000000000000000000000000000000000000000000KghhhhggK0.....................',
    '.....K00222202K00000000000000000002000000000000000000000000000000000000000000000000000000Kgggggggg1K0...................',
    'KKKKKK000000KKK0000000000000000000200000000000000000000000000000000000000000000000000000K1ggggggggg1KK..................',
    'K1111KKKKKKKKK00000000000000000000200000000000000000000000000000000000000000000000000000KKKKKKKKKKKKKKK0................',
    'KKKKK111111111KKKKK000000000000000K0000000000000000K0000000000000000000000000000000000000000000000000000.33.............',
    '.....KKKKKKKKK1111KKKKK000000000000K000000000000000K0000000000000000000000000K0000000000000000000K00000000233332........',
    '..............KKKKKK...K00000000000K000000000000000K0K22222222222222222222222K0000000000000000000K000000000000233.......',
    '...................K...0KKKKKKKKKK00K00000000000000K0K11111111111111111111111K2K00000000000000000K000000000000000KKKKKKK',
    '..................K...............KKK00000000000000K0KKKKKKKKKKKKKKKKKKKKKKKKK1K00000000000000000K0000000000000000K1111K',
    '.................KKK..................KK00000000000K00KKKKKKKKKK00KKKKKKKKKKKKKK00000000000000000K0000000000000000K111hK',
    '................0000K...................KKKK0000000K00K0000000K1K0KKKKKKKKKKKK0000000000000000000K0000000000000000K1111K',
    '................K000K.......................KKKKK00K00K000000K111KK0KK0KK0KK0K0000000000000000000K0000000000000000K1111K',
    '................K000K............................K0000K000000K111KK0KK0KK0KK0K0000000000000000000K000000000000000KK1111K',
    '.................KKK..............................K0KKK000000K111KKKKKKKKKKKKK000000000000000000000000000KK000KKK.KKKKKK',
    '......................................................K0000000K1K.KKKKKKKKKKKK000000000000KKKKKKKKKKKKKKK11KKK..........',
    '......................................................KKKKKKKKKK.............KKKKKKKKKKKKKKK...........K111KK...........',
    '..........................................................................................3KK...........111K............',
    '...........................................................................................KK...........K11K............',
    '.............................................................................................KKK.........KK.............',
    '...........................................................................................K0000K.......................',
    '..........................................................................................K000000K......................',
    '..........................................................................................K000200K......................',
    '..........................................................................................K000000K......................',
    '...........................................................................................K00000.......................',
    '...........................................................................................KKKKK........................',
]


def apache_body():
    return sprite(APACHE, PAL)                      # (its outline is in the drawing already)


# ---------------------------------------------------------------- turning a pixel picture without it breaking up:
# enlarged eight times, turned, and brought back down by taking each block's middle
def rot_sprite(im, ang, cx, cy, k=8):
    big = im.resize((im.width * k, im.height * k), Image.NEAREST)
    pad = int(max(im.width, im.height) * k * 0.6)
    canvas = Image.new('RGBA', (big.width + 2 * pad, big.height + 2 * pad), (0, 0, 0, 0))
    canvas.paste(big, (pad, pad))
    pcx, pcy = pad + cx * k + k // 2, pad + cy * k + k // 2
    rot = canvas.rotate(-math.degrees(ang), resample=Image.NEAREST, center=(pcx, pcy))
    # back down: the block whose middle lands on each pixel, the pivot staying on a pixel
    ox, oy = pcx - k // 2 - (pcx // k) * k, pcy - k // 2 - (pcy // k) * k
    W_, H_ = rot.width // k, rot.height // k
    a = np.asarray(rot)
    out = np.zeros((H_, W_, 4), np.uint8)
    for y in range(H_):
        for x in range(W_):
            sx, sy = x * k + k // 2 + ox, y * k + k // 2 + oy
            if 0 <= sx < a.shape[1] and 0 <= sy < a.shape[0]:
                out[y, x] = a[sy, sx]
    small = Image.fromarray(out, 'RGBA')
    bb = small.getbbox()
    piv = ((pcx - ox) // k, (pcy - oy) // k)
    return small.crop(bb), piv[0] - bb[0], piv[1] - bb[1]


TILTS = [-0.24, -0.16, -0.08, 0.0, 0.08, 0.16, 0.24]        # the nose up to the nose down: frames apache_t0 .. apache_t6


def rotor_frames():
    """The main rotor, spinning: four frames of its long dark blades seen edge on (as the teaser has them), 128 across."""
    out = []
    dark, blur = (12, 13, 16), (70, 76, 92)
    for k in range(4):
        im = new(130, 4)
        L = [126, 84, 112, 40][k]
        x0 = 65 - L // 2
        for x in range(L):
            d = abs(x - L / 2) / (L / 2)
            im.putpixel((x0 + x, 2), dark + (int(250 - 90 * d),))
            if (x + k * 5) % 11 < 3:
                im.putpixel((x0 + x, 1), blur + (int(70 * (1 - d)),))
        for dx in (-3, -2, -1, 0, 1, 2, 3):
            im.putpixel((65 + dx, 2), (20, 22, 27, 255))
        out.append(('apache_rotor%d' % k, im, 65, 2))
    return out


def tail_rotor_frames():
    out = []
    c = (44, 48, 58)
    R = 7
    for k in range(4):
        im = new(2 * R + 1, 2 * R + 1)
        for blade in range(2):
            a = (k * 45 + blade * 90) * math.pi / 180
            for r in range(-R, R + 1):
                if r == 0: continue
                x, y = int(round(R + math.cos(a) * r)), int(round(R + math.sin(a) * r))
                im.putpixel((x, y), (c[0], c[1], c[2], 235 - abs(r) * 22))
        im.putpixel((R, R), (20, 22, 27, 255))
        out.append(('apache_tail%d' % k, im, R, R))
    return out


def gun_barrel():
    im = new(15, 3)
    for x in range(15):
        im.putpixel((x, 1), rgba(PAL['K'] if x < 12 else PAL['1']))
        if x < 5:
            im.putpixel((x, 0), rgba(PAL['0'])); im.putpixel((x, 2), rgba(PAL['0']))
    im.putpixel((14, 1), rgba(PAL['2']))
    return im


# ---------------------------------------------------------------- the Zanabeel's anti-aircraft gun: a ring of sandbags, the
# mount, and the twin barrels (a piece of their own, turned to follow the Apache)
SAND = {'x': (40, 30, 20), 'o': (150, 124, 84), 'O': (188, 160, 110), 'd': (112, 90, 60), 'g': (60, 64, 52), 'G': (88, 94, 78),
        'k': (30, 32, 30), 'm': (70, 74, 66), 'K': (12, 13, 12)}
AA_BASE = [
    '................kkkkkkkk................',
    '...............kmmmmmmmmk...............',
    '...............kGgggggggk...............',
    '..............kgGgggggggGk..............',
    '..............kggggggggggk..............',
    '....OOoOOO....kgkkkkkkkkgk....OOoOOO....',
    '...OOoooooOO..kk........kk..OOoooooOO...',
    '..OoooooooooOOOOoOOOOOoOOOOOooooooooooO.',
    '.OooooooooooOooooooooooooooOooooooooooOO',
    'Oooodoooddooooooddoooooodooooodoooooddoo',
    'oodddoodddddddooddoddoodddoddoodddooddod',
    'dddddddddddddddddddddddddddddddddddddddd',
]
# the man on it: sitting behind the gun, hands on its handles (a head wrap, the Zanabeel's olive)
GUNNER = [
    '....tttt....',
    '...tTTTTt...',
    '...tTttTt...',
    '...sssss....',
    '...sesse....',
    '....ssss....',
    '..gggggggs..',
    '.ggGgggggss.',
    '.ggggggggg..',
    '.gggg.ggg...',
    '.gggg.......',
    '.gggg.......',
]
GPAL = {'t': (176, 146, 98), 'T': (212, 188, 142), 's': (176, 120, 80), 'e': (40, 26, 20), 'g': (84, 92, 58), 'G': (110, 120, 78)}
AA_BAR = [
    '...........................kk.',
    'kkkkkkkkkkkkkkkkkkkkkkkkkkkmkk',
    'kmmmmkk.......................',
    'kmGGmkkkkkkkkkkkkkkkkkkkkkkmkk',
    'kmmmmk.....................kk.',
    'kkkkkk........................',
]


def aa_parts():
    base = outline(sprite(AA_BASE, SAND), (24, 18, 12))
    gunner = outline(sprite(GUNNER, GPAL), (24, 18, 12))
    bar = sprite(AA_BAR, SAND)
    return base, bar, gunner


def burnt(im, seed=3):
    a = np.asarray(im.convert('RGBA')).astype(float)
    r = np.random.RandomState(seed)
    lum = a[..., :3].mean(axis=2, keepdims=True)
    soot = 0.30 + 0.16 * (r.rand(a.shape[0], a.shape[1], 1) > 0.5)
    rgb = (a[..., :3] * 0.35 + lum * 0.65) * soot + np.array([10.0, 6.0, 4.0])
    hot = (r.rand(a.shape[0], a.shape[1]) > 0.94) & (a[..., 3] > 0)
    rgb[hot] = (226, 110, 36)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a[..., 3:4]]).astype(np.uint8), 'RGBA')


# ---------------------------------------------------------------- the missile man's launcher, the rockets, the missile
def tube():
    rows = ['..kk............',
            'kkmmkkkkkkkkkkk.',
            'kgGGggggggggggGk',
            'kggggggggggggggk',
            '.kkkk.kkkkkkkkk.']
    pal = dict(SAND, k=(22, 24, 20))
    return sprite(rows, pal)


def rocket():
    rows = ['.kkkkkk..', 'kggggggOk', '.kkkkkk..']
    return sprite(rows, dict(SAND, O=(220, 214, 196)))


def missile():
    rows = ['kk.......', '.kggggggk', 'kkGGGGGGO', '.kggggggk', 'kk.......']
    return sprite(rows, dict(SAND, O=(200, 60, 40)))


# ---------------------------------------------------------------- the sheet
def build():
    items = []                                     # (name, image, ax, ay)
    body = apache_body()
    for i, t in enumerate(TILTS):
        im, ax, ay = rot_sprite(body, t, AX, AY)
        items.append(('apache_t%d' % i, im, ax, ay))
        items.append(('apache_t%d!' % i, silhouette(im, '#ffffff'), ax, ay))
    items.append(('apache_burnt', burnt(body, 5), AX, AY))
    items += rotor_frames() + tail_rotor_frames()
    items.append(('apache_gun', gun_barrel(), 0, 1))
    base, bar, gunner = aa_parts()
    items.append(('aa_base', base, base.width // 2, base.height - 1))
    items.append(('aa_base!', silhouette(base, '#ffffff'), base.width // 2, base.height - 1))
    items.append(('aa_bar', bar, 3, 3))
    items.append(('aa_bar!', silhouette(bar, '#ffffff'), 3, 3))
    items.append(('aa_gunner', gunner, gunner.width // 2, gunner.height - 1))
    items.append(('aa_gunner!', silhouette(gunner, '#ffffff'), gunner.width // 2, gunner.height - 1))
    items.append(('aa_wreck', burnt(base, 7), base.width // 2, base.height - 1))
    items.append(('aa_bar_burnt', burnt(bar, 8), 3, 3))
    t = tube()
    items.append(('sam_tube', t, 4, 2))
    items.append(('rocket', rocket(), 4, 1))
    items.append(('missile', missile(), 4, 2))
    # pack in rows
    W = 512
    x = y = rowh = 0
    place = []
    for n, im, ax, ay in items:
        if x + im.width + 1 > W:
            x = 0; y += rowh + 1; rowh = 0
        place.append((n, im, x, y, ax, ay))
        x += im.width + 1; rowh = max(rowh, im.height)
    H = y + rowh
    sheet = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    meta = {}
    for n, im, x, y, ax, ay in place:
        sheet.alpha_composite(im, (x, y))
        meta[n] = [x, y, im.width, im.height, int(ax), int(ay)]
    # where things are on the body (from its middle), for the game: the gun's pivot, the rotor hub, the tail rotor,
    # the nav lights, the searchlight
    rig = dict(gun=[45, 11], hub=[-1, -21], tail=[-58, -14], red=[-55, -18], green=[-25, -4], beacon=[-8, -14], light=[57, 3], exhaust=[-20, -8], pod=[18, 4])
    return sheet, meta, rig


if __name__ == '__main__':
    sheet, meta, rig = build()
    os.makedirs(OUT, exist_ok=True)
    if '--look' in sys.argv:
        bg = Image.new('RGBA', sheet.size, (70, 80, 110, 255))
        bg.alpha_composite(sheet)
        bg.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(os.path.join(OUT, 'taiz_look.png'))
        print('proof', os.path.join(OUT, 'taiz_look.png'), sheet.size)
    else:
        sheet.save(os.path.join(OUT, 'taiz.png'), optimize=True)
        json.dump(dict(frames=meta, rig=rig), open(os.path.join(GEN, 'taiz_sprites.json'), 'w'), separators=(',', ':'))
        print('taiz sheet %dx%d, %d frames' % (sheet.width, sheet.height, len(meta)))
