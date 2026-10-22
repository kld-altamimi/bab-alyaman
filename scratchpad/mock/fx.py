# fx.py - gunfire and dust, and the arcade-style HUD lettering.
from px import *

FXPAL = {'W': '#fffbe6', 'Y': '#ffe45a', 'O': '#ffa820', 'R': '#e45a14', 'D': '#8a2c0c', 'K': '#141008',
         's': '#f8e4a8', 't': '#dcc080', 'u': '#b89454', 'g': '#8a8a82', 'G': '#c8c8bc', 'k': '#3a3630',
         'L': '#b8301c', 'M': '#f0703c', 'J': '#fffbef', 'v': '#40322a'}

FX = {
    'muzzle': [
        '....O.......',
        '.O..YO....O.',
        '..OYYYO.OO..',
        '.OYWWWYYYYOO',
        'YWWWWWWWYYYO',
        '.OYWWWYYYYOO',
        '..OYYYO.OO..',
        '.O..YO....O.',
        '....O.......',
    ],
    'muzzle_s': [
        '..O....',
        '.OYO.O.',
        'OYWWYYO',
        '.OYO.O.',
        '..O....',
    ],
    'tracer': [
        'DROOYYWW',
        'DROOYYWW',
    ],
    'tracer_e': [
        'WWYYOORD',
        'WWYYOORD',
    ],
    'spark': [
        '..Y..',
        'Y.W.Y',
        '.WWW.',
        'Y.W.Y',
        '..Y..',
    ],
    'spark2': [
        'Y...O',
        '.Y.O.',
        '..W..',
        '.O.Y.',
        'O...Y',
    ],
    'puff': [
        '...ss.....',
        '.sstss.ss.',
        'sttuttstts',
        '.tuutuuut.',
        '..u..uu...',
    ],
    'casing': [
        'OY',
        'DO',
    ],
    'stick': [           # a lit stick of dynamite, end over end
        '.....Y.',
        '....Y.W',
        '...v...',
        '.LMJ...',
        'LMJM...',
        'MJML...',
        '.ML....',
    ],
    'smoke': [
        '..GG..',
        '.GggG.',
        'GggkgG',
        '.GgkG.',
        '..gg..',
    ],
}


def fx(name, flip=False):
    im = sprite(FX[name], FXPAL)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im


# ---------------------------------------------------------------- HUD lettering
LAV = ['#ffffff', '#f4f4ff', '#dcdcf8', '#bcbcec', '#9c9cdc', '#8080c8']
ORG = ['#fff8c8', '#ffe66a', '#ffc22e', '#f8941c', '#e06410', '#b83c08']
RED = ['#fff0c0', '#ffc850', '#f88c28', '#e85018', '#c42810', '#8c1408']
BLU = ['#ffffff', '#d8f0ff', '#a0d0f8', '#60a0e8', '#3070d0', '#1c48a8']
EDGE = '#10101c'


def gtext(dst, x, y, s, font=FONT_M, grad=LAV, edge=EDGE, scale_=1, align='l', sp=1, shadow=True):
    """Lettering with a top-to-bottom gradient and a dark edge, the arcade's way."""
    im = text_img(s, font, '#ffffff', sp, scale_)
    w = text_w(s, font, sp, scale_)
    hgt = font_h(font) * scale_
    px_ = im.load()
    for yy in range(im.height):
        c = rgba(grad[min(len(grad) - 1, yy * len(grad) // max(hgt, 1))])
        for xx in range(im.width):
            if px_[xx, yy][3]:
                px_[xx, yy] = c
    if align == 'c':
        x -= w // 2
    elif align == 'r':
        x -= w
    o = outline(im, edge, diag=True)
    if shadow:
        blit(dst, silhouette(o, (10, 8, 20, 120)), x, y)
    blit(dst, o, x - 1, y - 1)
    return w


TALL = {                 # the timer's tall thin numerals
    '0': ['.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    '1': ['..#..', '.##..', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..', '.###.'],
    '2': ['.###.', '#...#', '....#', '....#', '...#.', '..#..', '.#...', '#....', '#....', '#....', '#####'],
    '3': ['.###.', '#...#', '....#', '....#', '....#', '..##.', '....#', '....#', '....#', '#...#', '.###.'],
    '4': ['...#.', '..##.', '..##.', '.#.#.', '.#.#.', '#..#.', '#..#.', '#####', '...#.', '...#.', '...#.'],
    '5': ['#####', '#....', '#....', '#....', '####.', '....#', '....#', '....#', '....#', '#...#', '.###.'],
    '6': ['.###.', '#...#', '#....', '#....', '####.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    '7': ['#####', '....#', '....#', '...#.', '...#.', '..#..', '..#..', '..#..', '.#...', '.#...', '.#...'],
    '8': ['.###.', '#...#', '#...#', '#...#', '#...#', '.###.', '#...#', '#...#', '#...#', '#...#', '.###.'],
    '9': ['.###.', '#...#', '#...#', '#...#', '#...#', '.####', '....#', '....#', '....#', '#...#', '.###.'],
    ':': ['.', '.', '.', '#', '#', '.', '.', '#', '#', '.', '.'],
}


def tall(dst, cx, y, s, grad=LAV, edge=EDGE):
    w = sum(len(TALL[ch][0]) + 2 for ch in s) - 2
    im = new(w * 2, 22)
    x = 0
    for ch in s:
        g = TALL[ch]
        for j, row in enumerate(g):
            c = rgba(grad[min(len(grad) - 1, j * len(grad) // 11)])
            for i, bit in enumerate(row):
                if bit == '#':
                    rect(im, (x + i) * 2, j * 2, (x + i) * 2 + 1, j * 2 + 1, c)
        x += len(g[0]) + 2
    o = outline(im, edge, diag=True)
    blit(dst, silhouette(o, (10, 8, 20, 120)), cx - w + 1, y + 1)
    blit(dst, o, cx - w, y)
    return w * 2


if __name__ == '__main__':
    s = new(200, 70, hexc('#3a6a8a'))
    x = 4
    for n in FX:
        im = fx(n)
        blit(s, im, x, 4)
        x += im.width + 4
    gtext(s, 4, 22, 'YAZEED 0012400', FONT_M, LAV)
    gtext(s, 4, 34, '187', FONT_B, ORG)
    gtext(s, 40, 34, 'ARMS', FONT_S, LAV)
    gtext(s, 70, 34, 'MISSION START', FONT_B, RED)
    tall(s, 160, 4, '1:42')
    save(s, 't3_fx.png', 5)
