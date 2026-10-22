# sanaa.py - Old Sanaa tower houses: burnt brick, white gypsum friezes, coloured fanlights.
from px import *
from world import INK, profile

GLASS = ['#ff6a4a', '#ffd24a', '#4ac8e8', '#6ce07a', '#f48cc0']
GLASS_DIM = ['#7a3a44', '#8a7040', '#3a6a80', '#3e7050', '#7a4a68']

DUSK = dict(
    brick='#a86c4c', brick_l='#cc8c5c', brick_s='#7e4a3c', brick_d='#583034',
    white='#fbe6c8', white_s='#cfa8a0', stone='#5c4a52', stone_s='#3e3040',
    dark='#241a2c', lamp='#ffcf5a', lamp_s='#f89838', wood='#6a4030',
)


def _window(lay, x, y, pal, lit, r, big=True):
    """Fanlight over a shuttered window. (x, y) is the top-left of the fanlight."""
    g = GLASS if lit else GLASS_DIM
    k = r.randint(0, 4)
    W_, w_ = rgba(pal['white']), rgba(pal['white_s'])
    px = lay.load()

    def P_(xx, yy, c):
        if 0 <= xx < lay.width and 0 <= yy < lay.height:
            px[xx, yy] = rgba(c)

    if big:
        rows = ['...WWWWW...', '..W12341W..', '.W2341234W.', '.W3412341W.', 'WWWWWWWWWWW']
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch == 'W':
                    P_(x + i, y + j, W_)
                elif ch in '1234':
                    P_(x + i, y + j, g[(int(ch) + k) % 5])
        inner = pal['lamp'] if lit else pal['dark']
        inner_s = pal['lamp_s'] if lit else '#1a1222'
        for j in range(7):
            for i in range(1, 10):
                c = W_ if i in (1, 5, 9) else (inner if (j + i) % 3 else inner_s)
                P_(x + i, y + 5 + j, c)
        for i in range(1, 10):
            P_(x + i, y + 12, W_)
        for i in range(2, 9):
            P_(x + i, y + 13, w_)
        if lit:                                  # a figure of shutter bars
            for j in (7, 9):
                for i in (2, 3, 4, 6, 7, 8):
                    P_(x + i, y + j, rgba(pal['lamp_s']))
    else:
        rows = ['.WWW.', 'W121W', 'WWWWW', 'WDDDW', 'WDDDW', 'WWWWW']
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch == 'W':
                    P_(x + i, y + j, W_)
                elif ch in '12':
                    P_(x + i, y + j, g[(int(ch) + k) % 5])
                elif ch == 'D':
                    P_(x + i, y + j, pal['lamp'] if lit else pal['dark'])


def _frieze(lay, x0, x1, y, pal, kind):
    W_ = rgba(pal['white'])
    px = lay.load()
    for x in range(x0, x1 + 1):
        if not (0 <= x < lay.width):
            continue
        i = x - x0
        if kind == 0:                            # zigzag
            if 0 <= y < lay.height and i % 4 in (0, 1):
                px[x, y] = W_
            if 0 <= y + 1 < lay.height and i % 4 in (2, 3):
                px[x, y + 1] = W_
        elif kind == 1:                          # line over dots
            if 0 <= y < lay.height:
                px[x, y] = W_
            if 0 <= y + 2 < lay.height and i % 3 == 1:
                px[x, y + 2] = W_
        else:                                    # diamonds
            if 0 <= y + 1 < lay.height and i % 4 == 1:
                px[x, y + 1] = W_
            if i % 4 in (0, 2):
                for yy in (y, y + 2):
                    if 0 <= yy < lay.height:
                        px[x, yy] = W_ if i % 4 == 0 else px[x, yy]
            if 0 <= y < lay.height and i % 4 == 1:
                px[x, y] = W_
            if 0 <= y + 2 < lay.height and i % 4 == 1:
                px[x, y + 2] = W_


def tower(lay, x0, ytop, w, h, seed=1, pal=None, floor_h=19, lit=0.55, big=True, merlons=True,
          rim=True):
    """One tower house, its flat roof at ytop. Draws down h pixels."""
    pal = pal or DUSK
    r = rng(seed)
    x1 = x0 + w - 1
    rect(lay, x0, ytop, x1, ytop + h - 1, pal['brick'])
    # brick courses
    for yy in range(ytop + 2, ytop + h, 3):
        xx = x0 + (yy * 5 + seed) % 7
        while xx < x1:
            hsh = (xx * 31 + yy * 17 + seed * 7) % 13
            if hsh < 4:
                hline(lay, xx, min(x1, xx + 1 + hsh % 3), yy, pal['brick_s'])
            elif hsh == 5:
                hline(lay, xx, min(x1, xx + 2), yy - 1, pal['brick_l'])
            xx += 4 + hsh % 4
    # light from the left, shade to the right
    if rim:
        rect(lay, x0, ytop, x0 + 1, ytop + h - 1, pal['brick_l'])
    sw = max(3, w // 6)
    for yy in range(ytop, ytop + h):
        for xx in range(x1 - sw, x1 + 1):
            if xx > x1 - sw // 2 or BAYER4[yy % 4][xx % 4] < 8:
                put(lay, xx, yy, pal['brick_s'])
    rect(lay, x1, ytop, x1, ytop + h - 1, pal['brick_d'])
    # parapet
    rect(lay, x0, ytop, x1, ytop + 1, pal['white'])
    rect(lay, x0, ytop + 5, x1, ytop + 5, pal['white'])
    _frieze(lay, x0 + 1, x1 - 1, ytop + 2, pal, 0)
    if merlons:
        for mx in (x0, x1 - 3):
            rect(lay, mx, ytop - 3, mx + 3, ytop, pal['white'])
            rect(lay, mx + 1, ytop - 5, mx + 2, ytop - 3, pal['white'])
        step = 8 if big else 5
        for mx in range(x0 + step, x1 - step + 1, step):
            rect(lay, mx, ytop - 2, mx + 1, ytop, pal['white'])
    # floors
    y = ytop + 8
    f = 0
    ww = 11 if big else 5
    wh = 14 if big else 6
    while y + wh + 2 < ytop + h + wh:
        n = max(1, (w - 4) // (ww + (6 if big else 3)))
        gap = (w - n * ww) / (n + 1)
        for i in range(n):
            wx = int(x0 + gap + i * (ww + gap))
            _window(lay, wx, y, pal, r.random() < lit, r, big=big)
        yb = y + wh + (3 if big else 1)
        if yb + 3 < ytop + h:
            _frieze(lay, x0 + 1, x1 - 1, yb, pal, (f + seed) % 3)
        y += floor_h if big else (floor_h * 6) // 10
        f += 1
    return x0, ytop, x1


def minaret(lay, x, ybase, h, c, c2=None, lit=None):
    """Slim tower in silhouette with a balcony and small dome."""
    c2 = c2 or c
    rect(lay, x - 2, ybase - h, x + 2, ybase, c)
    rect(lay, x - 3, ybase - h + h // 3, x + 3, ybase - h + h // 3 + 1, c2)
    rect(lay, x - 3, ybase - h + 6, x + 3, ybase - h + 7, c2)
    rect(lay, x - 1, ybase - h - 5, x + 1, ybase - h, c)
    disc(lay, x, ybase - h - 6, 2, c)
    vline(lay, x, ybase - h - 11, ybase - h - 8, c)
    if lit:
        for yy in range(ybase - h + 10, ybase - 4, 9):
            put(lay, x, yy, lit)


def skyline(lay, y_base, seed, c, c_hi, lit_c, min_h=14, max_h=44, density=1.0):
    """A dense row of far tower-house silhouettes with a few lit windows."""
    r = rng(seed)
    x = -4
    while x < lay.width:
        w = r.randint(9, 18)
        h = r.randint(min_h, max_h)
        rect(lay, x, y_base - h, x + w - 1, y_base, c)
        rect(lay, x, y_base - h, x, y_base, c_hi)
        hline(lay, x, x + w - 1, y_base - h, c_hi)
        for mx in (x, x + w - 2):
            rect(lay, mx, y_base - h - 2, mx + 1, y_base - h, c_hi)
        for yy in range(y_base - h + 4, y_base - 2, 6):
            for xx in range(x + 2, x + w - 2, 4):
                if r.random() < 0.38 * density:
                    put(lay, xx, yy, lit_c)
                    put(lay, xx, yy + 1, lit_c)
                    if r.random() < 0.5:
                        put(lay, xx, yy - 1, r.choice(GLASS))
        x += w + r.randint(-2, 3)
