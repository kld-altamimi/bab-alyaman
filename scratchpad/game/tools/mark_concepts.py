# mark_concepts.py - the maker's mark on the side of the armoured truck, in the spirit of the badge Khaled sent: heavy
# slanted capitals in dark slate, one letter's upright replaced by a green blade rising past the top of the word. Our
# own word and our own blade (a jambiya's point, as in the game's logo), never the real company's mark.
# Three words: SHASS (the car's name), SAIF (four letters; the make's name, the hero being Yazeed), SALEM (the driver).
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock')
import numpy as np
from PIL import Image, ImageDraw
import props as P
import vehicles as V
import armour_concepts as AC

SLATE = (46, 74, 86)
SLATE_D = (30, 50, 60)
GREEN = (120, 180, 92)
GREEN_D = (84, 136, 64)
# the small mark, for the side of the truck: 5 wide x 7 tall upright capitals with two-pixel strokes; the A has no
# left leg: a green blade stands there, leaning forward, its point three rows over the top
GLY = {
    'S': ['.####', '##...', '##...', '.###.', '...##', '...##', '####.'],
    'H': ['##.##', '##.##', '##.##', '#####', '##.##', '##.##', '##.##'],
    'A': ['..##.', '..###', '..###', '..###', '..###', '..###', '..###'],
    'I': ['##', '##', '##', '##', '##', '##', '##'],
    'F': ['#####', '##...', '##...', '####.', '##...', '##...', '##...'],
    'L': ['##...', '##...', '##...', '##...', '##...', '##...', '#####'],
    'E': ['#####', '##...', '##...', '####.', '##...', '##...', '#####'],
    'M': ['##.##', '#####', '#####', '##.##', '##.##', '##.##', '##.##'],
}
# the A, with its crossbar and right leg; the blade is drawn over its left two columns
GLY['A'] = ['..##.', '.#.##', '.#.##', '#####', '##.##', '##.##', '##.##']
BLADE = [(2, -3), (2, -2), (1, -1), (2, -1), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2), (1, 2), (0, 3), (1, 3), (0, 4), (1, 4), (0, 5), (1, 5), (0, 6), (1, 6)]
RISE = 3


def mark(word):
    """The word as an RGBA image at 1x. Returns (image, baseline row)."""
    widths = [len(GLY[ch][0]) for ch in word]
    Wd = sum(widths) + len(word) - 1
    out = Image.new('RGBA', (Wd + 2, 7 + RISE + 1), (0, 0, 0, 0))
    px = out.load()
    x = 1
    for ch, wch in zip(word, widths):
        for j, row in enumerate(GLY[ch]):
            for i, c in enumerate(row):
                if c == '#':
                    px[x + i, RISE + j] = SLATE
        if ch == 'A':
            for (i, j) in BLADE:
                px[x + i, RISE + j] = GREEN_D if (i == 0 or j < -1) else GREEN
        x += wch + 1
    return out, RISE + 6


# the big mark, for a card: the same letters built from slanted strokes, the blade a long wedge
def big_mark(word, u=22, shear=0.22):
    import math
    STROKES = {       # rectangles in a 5 x 7 grid, (x0, y0, x1, y1), the way the pixel letters are built
        'S': [(0, 0, 5, 1.8), (0, 0, 1.9, 4.2), (0, 2.8, 5, 4.4), (3.1, 2.8, 5, 7), (0, 5.6, 5, 7)],
        'H': [(0, 0, 2, 7), (3, 0, 5, 7), (0, 3, 5, 5)],
        'A': [(3, 0, 5, 7), (1, 0, 5, 2), (1, 3, 5, 5)],
        'I': [(0, 0, 2, 7)],
        'F': [(0, 0, 2, 7), (0, 0, 5, 2), (0, 3, 4, 5)],
        'L': [(0, 0, 2, 7), (0, 5, 5, 7)],
        'E': [(0, 0, 2, 7), (0, 0, 5, 2), (0, 3, 4, 5), (0, 5, 5, 7)],
        'M': [(0, 0, 2, 7), (3, 0, 5, 7), (0, 0, 5, 2), (1.5, 1, 3.5, 4)],
    }
    widths = [2 if ch == 'I' else 5 for ch in word]
    Wd = (sum(widths) + len(word) - 1) * u + 6 * u
    Hh = 13 * u
    im = Image.new('RGBA', (Wd, Hh), (248, 248, 246, 255))
    d = ImageDraw.Draw(im)
    oy = 4 * u
    def sh(x, y):   # shear: the top leans right
        return (x + shear * (7 * u - y) + 2 * u, y + oy)
    x = 0
    for ch, w in zip(word, widths):
        for (x0, y0, x1, y1) in STROKES[ch]:
            X0, Y0, X1, Y1 = (x + x0) * u, y0 * u, (x + x1) * u, y1 * u
            d.polygon([sh(X0, Y0), sh(X1, Y0), sh(X1, Y1), sh(X0, Y1)], fill=SLATE)
        if ch == 'A':
            # the blade: from the foot of the left leg, up past the cap line to a point
            X0, X1 = x * u, (x + 2) * u
            tip = sh((x + 2.6) * u, -3.6 * u)
            d.polygon([sh(X0, 7 * u), sh(X1, 7 * u), tip], fill=GREEN)
            d.polygon([sh(X0, 7 * u), sh(X0 + 0.7 * u, 7 * u), (tip[0] - 0.2 * u, tip[1] + 0.5 * u)], fill=GREEN_D)
        x += w + 1
    return im


def card(word):
    """The big mark, and the small one at 8x beside it."""
    big = big_mark(word)
    big = big.resize((big.width // 2, big.height // 2), Image.LANCZOS)
    im, base = mark(word)
    small = im.resize((im.width * 6, im.height * 6), Image.NEAREST)
    out = Image.new('RGBA', (max(720, big.width + small.width + 60), max(big.height, small.height) + 20), (248, 248, 246, 255))
    out.alpha_composite(big, (10, 10))
    out.alpha_composite(small, (big.width + 40, (out.height - small.height) // 2))
    return out


def on_truck(word, k=4):
    """The truck with the mark pressed on its side, over the rear body between the window and the knuckle."""
    L = V.mrap(mark=False)
    im, base = mark(word)
    # paint it on, as pressed lettering: dark letters, a light edge below-right
    W, H = 106, 66
    top = (H - 1) - 41 - 4
    x0, y0 = 8, top + 12 - (im.height - 7)
    src = im.load()
    for j in range(im.height):
        for i in range(im.width):
            r, g_, b, a = src[i, j]
            x, y = x0 + i, y0 + j
            if a and 0 <= x < W and 0 <= y < H and L.a[y, x]:
                L.rgb[y, x] = (r, g_, b)
    body = P.outlined(L).image()
    out = Image.new('RGBA', (180, 100), (16, 20, 44, 255))
    d = ImageDraw.Draw(out)
    gy = 86
    d.rectangle((0, gy, 180, 100), fill=(48, 44, 48, 255))
    d.rectangle((0, gy, 180, gy), fill=(70, 66, 70, 255))
    for x in range(4, 180, 24):
        d.rectangle((x, gy + 7, x + 12, gy + 7), fill=(226, 200, 120, 255))
    ox, oy = 90, gy - 10
    yazeed, sax, say = AC.frame('yazeed_stand_hmg_fwd')
    wheel = dict(V.big_wheel_frames())['bwheel0'].image()
    out.alpha_composite(yazeed, (ox - 22 - sax, oy + 10 - 31 - say))
    out.alpha_composite(body, (ox - 53, oy + 10 - 66))
    for wx in (-29, 29):
        out.alpha_composite(wheel, (ox + wx - wheel.width // 2, oy - 1 - wheel.height // 2))
    return out.resize((180 * k, 100 * k), Image.NEAREST)


if __name__ == '__main__':
    OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'boss_proposals')
    for w in ('SHASS', 'SAIF', 'SALEM'):
        card(w).save(os.path.join(OUT, 'mark_%s.png' % w))
        on_truck(w).save(os.path.join(OUT, 'mark_%s_truck.png' % w))
    sheet = Image.new('RGBA', (720, 3 * 580), (16, 20, 44, 255))
    for i, w in enumerate(('SHASS', 'SAIF', 'SALEM')):
        c = Image.open(os.path.join(OUT, 'mark_%s.png' % w))
        sheet.paste(c.crop((0, 0, 720, c.height)), (0, i * 580))
        sheet.paste(Image.open(os.path.join(OUT, 'mark_%s_truck.png' % w)), (0, i * 580 + 180))
    sheet.save(os.path.join(OUT, 'mark_sheet.png'))
    print('ok')
