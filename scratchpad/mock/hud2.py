# hud2.py - the HUD in the arcade's manner: gradient lettering with a dark edge straight on the
# picture, small dark tabs for ARMS and BOMB, tall timer numerals, a square portrait.
from px import *
from fx import gtext, tall, LAV, ORG, RED, BLU, EDGE
import ms3 as cast

HERO = {
    'yazeed': dict(bg='#b8301c', face='yazeed', wrap='check', pal=('blue', 'cream', 'blue', 'skin2'), nine='#e4dec2'),
    'salem': dict(bg='#b8301c', face='salem', wrap='kufiya', pal=('white', 'cream', 'cream', 'skin3'), nine=None),
    'bilqis': dict(bg='#b8301c', face='veiled', wrap='scarf', pal=('navy', 'navy', 'crimson', 'skin2'), nine=None),
    'arwa': dict(bg='#b8301c', face='arwa', wrap='flowered', pal=('rose', 'cream', 'sage', 'skin1'), nine=None),
}


def head_image(name):
    h = HERO[name]
    p = cast.pal(*h['pal'])
    if h['nine']:
        p['9'] = h['nine']
    B = cast.Build(face=(0, 5), wrap=(0, 0))
    L = []
    if h['wrap'] == 'check':
        cast.head(L, B, p, h['face'], 'check', 'check_end')
        L.append(cast.at(cast.WRAPS['basil'], B.wrap, p, 0, 1, ink=cast.INK2))
    elif h['wrap'] == 'kufiya':
        p.update(cast.KUFIYA)
        L += [cast.at(cast.FACES[h['face']], B.face, p), cast.at(cast.WRAPS['kufiya'], B.wrap, p, 0, -1, ink=cast.INK2)]
    elif h['wrap'] == 'scarf':
        L.append(cast.at(cast.WRAPS['drape_long'][:6], B.wrap, p, -3, 5, ink=cast.INK2))
        cast.head(L, B, p, h['face'], 'scarf')
    else:
        L.append(cast.at(cast.WRAPS['drape'], B.wrap, p, -2, 5, ink=cast.INK2))
        cast.head(L, B, p, h['face'], 'flowered')
    im, fx_, fy_ = cast.compose(L)
    return im


def portrait(dst, x, y, name, size=20):
    box = new(size, size, rgba(HERO[name]['bg']))
    for j in range(size):
        if j > size * 0.55:
            rect(box, 0, j, size - 1, j, (90, 16, 10, 255))
    hd = head_image(name)
    blit(box, hd, (size - hd.width) // 2 + 1, max(1, size - hd.height - 2))
    # rounded corners, light rim, dark edge
    for cx, cy in ((0, 0), (size - 1, 0), (0, size - 1), (size - 1, size - 1)):
        box.putpixel((cx, cy), (0, 0, 0, 0))
    blit(dst, outline(box, EDGE), x - 1, y - 1)
    for i in range(1, size - 1):
        put(dst, x + i, y, (255, 220, 170, 255))
        put(dst, x, y + i, (255, 220, 170, 255))
        put(dst, x + i, y + size - 1, (70, 10, 8, 255))
        put(dst, x + size - 1, y + i, (70, 10, 8, 255))


def tab(dst, x, y, w, label):
    """The small dark label plate over a counter."""
    rect(dst, x, y, x + w - 1, y + 8, (16, 20, 44, 255))
    rect(dst, x, y, x + w - 1, y, (150, 160, 220, 255))
    rect(dst, x, y, x, y + 8, (150, 160, 220, 255))
    rect(dst, x + w - 1, y, x + w - 1, y + 8, (60, 66, 120, 255))
    rect(dst, x, y + 8, x + w - 1, y + 8, (60, 66, 120, 255))
    t = text_img(label, FONT_S, '#e8ecff')
    blit(dst, t, x + (w - t.width) // 2 + 1, y + 2)


PLATE = ['.xxxxx.', 'xZZzzyx', 'xZzzzyx', 'xzzzyyx', 'xzzyyyx', '.xyyyx.', '..xyx..', '...x...']
PLATE_PAL = {'x': EDGE, 'Z': '#f0f4f8', 'z': '#a8b4c4', 'y': '#5c6878'}
PLATE_OFF = {'x': EDGE, 'Z': '#3a4250', 'z': '#2a303c', 'y': '#1e222c'}
POW = ['..HH..', '.HJJH.', '.pqqp.', '.HJJH.', 'HHJJHH', '.HJJH.', '.H..H.']
POW_PAL = {'H': '#c4bea2', 'J': '#fffbef', 'p': '#90592a', 'q': '#bc864c'}
RADIO = ['......z', '.....z.', '....z..', 'xxxxxx.', 'xZZZZx.', 'xzyzyx.', 'xyyyyx.', 'xxxxxx.']


def hud(dst, hero='yazeed', score=12400, arms='187', bombs='10', plates=3, lives=2, time='1:42', par='4:30',
        freed=(2, 5), radio=1.4):
    # player one: portrait, name, lives, armour, score
    portrait(dst, 6, 6, hero)
    gtext(dst, 30, 6, hero.upper(), FONT_M, LAV)
    nx = 30 + text_w(hero.upper(), FONT_M) + 4
    gtext(dst, nx, 6, '=%d' % lives, FONT_M, ORG)
    for i in range(3):
        blit(dst, sprite(PLATE, PLATE_PAL if i < plates else PLATE_OFF), 30 + i * 9, 17)
    gtext(dst, 62, 17, '%07d' % score, FONT_M, LAV)
    # arms and bombs
    ax = 118
    tab(dst, ax, 6, 28, 'ARMS')
    tab(dst, ax + 30, 6, 28, 'BOMB')
    gtext(dst, ax + 14, 17, arms, FONT_M, ORG, align='c')
    gtext(dst, ax + 44, 17, bombs, FONT_M, ORG, align='c')
    # the clock
    tall(dst, W // 2, 5, time)
    gtext(dst, W // 2, 29, 'PAR ' + par, FONT_S, LAV, align='c')
    # detainees freed
    fx0 = 300
    tab(dst, fx0, 6, 30, 'FREED')
    for i in range(freed[1]):
        im = sprite(POW, POW_PAL if i < freed[0] else {k: '#2a303c' for k in POW_PAL})
        blit(dst, outline(im, EDGE), fx0 + i * 8 - 1, 16)
    # the radio: three charges, the first one ready
    rx = 356
    tab(dst, rx, 6, 34, 'RADIO')
    blit(dst, outline(sprite(RADIO, {'x': '#2a303c', 'Z': '#a8e8b0', 'z': '#e8ecff', 'y': '#5c6878'}), EDGE), rx + 37, 5)
    for i in range(3):
        bx = rx + i * 16
        rect(dst, bx, 17, bx + 13, 23, EDGE)
        fill = max(0.0, min(1.0, radio - i))
        rect(dst, bx + 1, 18, bx + 12, 22, (30, 34, 60, 255))
        if fill > 0:
            c1, c2 = ('#ffc22e', '#fff8c8') if fill >= 1 else ('#a06c14', '#c89430')
            rect(dst, bx + 1, 18, bx + 1 + int(11 * fill), 22, c1)
            rect(dst, bx + 1, 18, bx + 1 + int(11 * fill), 19, c2)
    if radio >= 1:
        gtext(dst, rx + 50, 17, 'TAP', FONT_S, ORG)
    # pause
    rect(dst, 449, 6, 462, 19, (16, 20, 44, 200))
    rect(dst, 453, 9, 455, 16, '#e8ecff')
    rect(dst, 457, 9, 459, 16, '#e8ecff')


def go_sign(dst, x, y):
    """The nudge to move on: blue-white GO with an orange arrow."""
    gtext(dst, x, y, 'GO', FONT_B, BLU, scale_=1)
    ax = x + 22
    for i in range(7):
        rect(dst, ax + i, y + 4 - min(i, 6 - i) // 2 * 0 - (3 - abs(3 - i)) // 3 * 0, ax + i, y + 4, EDGE)
    arrow = ['..x......', '..xx.....', 'xxxOx....', 'xYYOOx...', 'xYYYOOx..', 'xYYOOx...', 'xxxOx....', '..xx.....', '..x......']
    blit(dst, sprite(arrow, {'x': EDGE, 'Y': '#ffe66a', 'O': '#f8941c'}), ax, y)


def subtitle(dst, name, line, y=196):
    """One spoken line. The voice is gibberish in the speaker's accent; this is what it means."""
    w = text_w(name + '  ' + line, FONT_M)
    x = W // 2 - w // 2
    gtext(dst, x, y, name, FONT_M, ORG)
    gtext(dst, x + text_w(name + '  ', FONT_M), y, line, FONT_M, LAV)


def touch(dst, stick=(1, 0)):
    lay = new()

    def btn(cx, cy, r, fa=80, ra=220):
        disc(lay, cx, cy, r, (16, 14, 28, fa))
        ring(lay, cx, cy, r, (255, 255, 255, ra), 1)
        ring(lay, cx, cy, r + 1, (16, 14, 28, 140), 1)

    cx, cy = 46, 168
    btn(cx, cy, 29, 60, 180)
    kx, ky = cx + stick[0] * 12, cy + stick[1] * 12
    disc(lay, kx, ky, 13, (255, 255, 255, 110))
    ring(lay, kx, ky, 13, (255, 255, 255, 235), 1)
    ring(lay, kx, ky, 14, (16, 14, 28, 140), 1)
    btn(424, 168, 24, 100, 235)
    btn(376, 190, 17)
    btn(444, 118, 16)
    blit(dst, lay, 0, 0)
    wht = (255, 255, 255, 240)
    for (bx, by, lab) in ((424, 168, 'FIRE'), (376, 190, 'JUMP'), (444, 118, 'BOMB')):
        t = text_img(lab, FONT_S, wht)
        blit(dst, t, bx - t.width // 2 + 1, by - 2)
