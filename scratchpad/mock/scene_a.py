# scene_a.py - Prologue: The Strait. Daytime coast: core gameplay, HUD, touch controls.
from px import *
from palette import P
from world import *
import cast, hud

GROUND = 184        # y of the characters' feet


def backdrop():
    im = new()
    vbands(im, 0, 0, W - 1, 110, [C['sky5'], C['sky4'], C['sky4'], C['sky3'], C['sky3'], C['sky2'], C['sky1']], soft=3)
    cloud(im, 36, 62, 78, 11)
    cloud(im, 150, 46, 50, 12)
    cloud(im, 250, 80, 96, 13)
    cloud(im, 318, 100, 44, 15, light='#eef8f4', shade='#c4e2ec')
    far = profile(W, 21, 7, step=26)
    for x in range(W):
        h = int(far[x] + 2)
        vline(im, x, 110 - h, 110, '#a9cfe2')
        if h > 5:
            put(im, x, 110 - h, '#bfdcea')
    sea(im, 110, 174, seed=3)
    tk = sprite([
        '...............TT......',
        '...............Tt......',
        '.....o...o....TTTt.....',
        'rrrrrrrrrrrrrrrrrrrrrr.',
        '.rRRRRRRRRRRRRRRRRRRr..',
    ], {'T': '#e8eef0', 't': '#b8c8d4', 'r': '#7c5a66', 'R': '#9c6c70', 'o': '#7c8ca0'})
    blit(im, tint(tk, C['haze'], 0.35), 190, 105)
    return im


def lighthouse(im, x, ybase):
    hs = [2, 4, 6, 8, 10, 11, 12, 13, 13, 14, 14, 14, 14, 14, 13, 13, 12, 12, 11, 11, 10, 9, 9, 8, 7, 7, 6, 5, 5, 4, 3, 2, 1]
    lay = new(70, 90)
    rock(lay, 6, 6 + len(hs) - 1, 88, hs, seed=31, ledges=False)
    tw = sprite([
        '....oo....',
        '...oooo...',
        '..oooooo..',
        '...YwwY...',
        '...YwwY...',
        '..oooooo..',
        '...TTTt...',
        '...TTTt...',
        '...RRRr...',
        '...RRRr...',
        '...RRRr...',
        '...TTTt...',
        '...TTTt...',
        '..TTTTTt..',
        '..RRRRRr..',
        '..RRRRRr..',
        '..RRRRRr..',
        '..TTTTTt..',
        '..TTTTTt..',
        '..TTTTTt..',
        '.TTToTTTt.',
        '.TTToTTTt.',
    ], {'T': '#f4f0e4', 't': '#c4c8cc', 'R': '#d8483c', 'r': '#a02c30', 'o': '#3a3440',
        'Y': '#f4c63c', 'w': '#fff6c8'})
    blit(lay, tw, 16, 88 - 13 - 22 + 1)
    lay = tint(lay, C['haze'], 0.2)
    blit(im, lay, x - 22, ybase - 88)


def dhow(im, x, y):
    """Moored fishing dhow; (x, y) is the waterline at the stern."""
    lay = new(84, 72)
    wl = 62
    hull = [
        'W..........................................WWW',
        'WWW......................................WWWWWW',
        'xWWWW.................................WWWWWWWWx',
        '.xWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWx.',
        '.xTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTx.',
        '..xWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWx..',
        '..xBWBWBWBWBWBWBWBWBWBWBWBWBWBWBWBWBWBWBWBWBx...',
        '...xxWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWxx....',
        '.....xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx......',
    ]
    hp = {'W': P['wood'], 'x': P['woods'], 'T': '#e8e0cc', 'B': '#3c7cb8'}
    blit(lay, sprite(hull, hp), 8, wl - 7)
    vline(lay, 32, wl - 46, wl - 5, P['woods'])
    vline(lay, 33, wl - 46, wl - 5, P['woodd'])
    for k in range(3):
        line(lay, 12, wl - 18 - k, 54, wl - 50 - k, '#e8e0cc' if k < 2 else '#cfc4a8')
    line(lay, 12, wl - 17, 54, wl - 49, P['woods'])
    line(lay, 33, wl - 46, 56, wl - 7, P['ink2'])
    line(lay, 32, wl - 46, 10, wl - 6, P['ink2'])
    rect(lay, 33, wl - 51, 33, wl - 47, P['woodd'])
    poly(lay, [(34, wl - 51), (41, wl - 49), (34, wl - 47)], P['red'])
    o = outline(lay, '#3a2a34')
    blit(im, o, x - 9, y - wl - 1)
    for i, xx in enumerate(range(x + 2, x + 46, 5)):
        hline(im, xx, xx + 2, y + 2 + (i % 2), '#2f6f8c')


def pier(im, x0, x1, y):
    rect(im, x0, y, x1, y + 2, P['wood'])
    rect(im, x0, y, x1, y, P['woodl'])
    rect(im, x0, y + 3, x1, y + 3, P['woodd'])
    for xx in range(x0, x1, 5):
        put(im, xx, y + 1, P['woods'])
        put(im, xx, y + 2, P['woods'])
    for xx in range(x0 + 6, x1, 18):
        rect(im, xx, y + 4, xx + 2, y + 16, P['woods'])
        rect(im, xx, y + 4, xx, y + 16, P['wood'])
        rect(im, xx, y - 5, xx + 2, y - 1, P['woods'])
        put(im, xx + 1, y - 6, P['woodl'])
        hline(im, xx - 1, xx + 3, y + 16, '#c8f2e4')


def sign(im, x, ybase, lines, post=18, bite=True):
    w = max(text_w(l, FONT_S) for l in lines) + 8
    h = len(lines) * 7 + 5
    lay = new(w + 4, h + post + 2)
    rect(lay, w // 2 - 1, h, w // 2 + 1, h + post, P['woods'])
    rect(lay, w // 2 - 1, h, w // 2 - 1, h + post, P['wood'])
    rect(lay, 0, 0, w - 1, h - 1, '#efe2bc')
    rect(lay, 0, 0, w - 1, 0, '#fbf4d8')
    rect(lay, 0, h - 1, w - 1, h - 1, '#c2ae82')
    rect(lay, w - 1, 0, w - 1, h - 1, '#c2ae82')
    rect(lay, 1, 1, w - 2, 7, '#7a2430')
    text(lay, w // 2, 2, lines[0], FONT_S, '#fbf4d8', align='c')
    for i, l in enumerate(lines[1:]):
        text(lay, w // 2, 10 + i * 7, l, FONT_S, '#3a2a34', align='c')
    for xx in (2, w - 3):
        put(lay, xx, h - 3, P['st3'])
    if bite:                                   # the goat has started on a corner
        px_ = lay.load()
        for dx, dy in ((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (0, 2), (3, 0), (0, 3), (1, 2), (2, 1)):
            px_[w - 1 - dx, h - 1 - dy] = (0, 0, 0, 0)
    o = outline(lay, INK)
    blit(im, o, x - w // 2 - 1, ybase - o.height + 2)
    return w, h


def goat(im, x, ybase, flip=False):
    """(x, ybase) is where the mouth goes when flipped: the goat is eating something."""
    g = sprite([
        '........................hh......',
        '.......................h..h.....',
        '.......................hWWWW....',
        '......................WWWWWeW...',
        '......................WWWWWWWp..',
        '.....................WWWWW.bb...',
        '....................WWWWW..bb...',
        '...................WWWWW...b....',
        '..................WWWWW.........',
        '.................WWWWW..........',
        '..WWWWWWWWWWWWWWWWWWW...........',
        '.WWWWWWBBBBWWWWWWWWWW...........',
        'tWWWWWBBBBBBWWWWWWWWW...........',
        'tWWWWWBBBBBWWWWWWWWWw...........',
        't.WWWWWBBBWWWWWWWWWww...........',
        '..WWWWWWWWWWWWWWWWWw............',
        '..WWwwWWWWWWWWWwwWWw............',
        '..Ww..WWw.....Ww..WWw...........',
        '..Ww..Ww......Ww..Ww............',
        '..Ww..Ww......Ww..Ww............',
        '..Ww..Ww......Ww..Ww............',
        '..Ww..Ww......Ww..Ww............',
        '..oo..oo......oo..oo............',
    ], {'W': '#f6f0e0', 'w': '#c8c0ac', 'B': '#8c6240', 'h': '#5a4a40', 'e': INK,
        'p': '#e8a0a0', 'o': '#3a3038', 't': '#c8c0ac', 'b': '#dcd4c0'})
    o = outline(g, INK)
    if flip:
        o = o.transpose(Image.FLIP_LEFT_RIGHT)
        blit(im, o, x - 2, ybase - 5)
    else:
        blit(im, o, x - o.width + 3, ybase - 5)
    return o.height - 5


def cauldron(im, x, ybase):
    c = sprite([
        '...Q..........Q...',
        '..MMMMMMMMMMMMMM..',
        '.MGGgGGGGgGGGGgGM.',
        '.MMMMMMMMMMMMMMMM.',
        'mMMQQMMMMMMMMMMMMm',
        'mMMQMMMMMMMMMMMMMm',
        'mMMQMMMMMMMMMMMMMm',
        'mMMMMMMMMMMMMMMMMm',
        'mMMMMMMMMMMMMMMMMm',
        '.mMMMMMMMMMMMMMMm.',
        '..mmMMMMMMMMMMmm..',
        '....mmmmmmmmmm....',
    ], {'M': '#4a4652', 'm': '#2e2a38', 'Q': '#74707c', 'G': '#c8b04c', 'g': '#e8d470'})
    o = outline(c, INK)
    blit(im, o, x - 10, ybase - 19)
    for i, xx in enumerate(range(x - 8, x + 8, 2)):
        vline(im, xx, ybase - 6 - (i * 5 % 4), ybase - 1, C['fire3'])
        vline(im, xx, ybase - 3 - (i % 2), ybase - 1, C['fire2'])
    hline(im, x - 10, x + 9, ybase, P['woodd'])
    hline(im, x - 8, x + 6, ybase - 1, P['woods'])
    for dx, dy in ((-3, -24), (-1, -28), (3, -33), (1, -38), (4, -43)):
        rect(im, x + dx, ybase + dy, x + dx + 1, ybase + dy + 1, '#f4f4ee')
        put(im, x + dx + 2, ybase + dy - 1, '#dfe6e6')


def crab(im, x, y):
    c = sprite(['r.RRR.r', 'rRRRRRr', '.rRRRr.', 'r.r.r.r'], {'R': '#e85c44', 'r': '#b03830'})
    put(c, 2, 0, INK)
    put(c, 4, 0, INK)
    blit(im, outline(c, INK), x, y - 5)


def gull(im, x, y, s=0):
    c = '#f4f4f0'
    if s == 0:
        hline(im, x - 4, x - 1, y - 1, c)
        put(im, x, y, c)
        hline(im, x + 1, x + 4, y - 1, c)
        put(im, x - 5, y, '#c8d4dc')
        put(im, x + 5, y, '#c8d4dc')
    else:
        hline(im, x - 4, x - 2, y + 1, c)
        hline(im, x - 1, x + 1, y, c)
        hline(im, x + 2, x + 4, y + 1, c)


def net_rack(im, x, ybase, w=34, h=26):
    lay = new(w + 4, h + 2)
    for xx in (1, w):
        rect(lay, xx, 0, xx + 1, h, P['woods'])
        put(lay, xx, 0, P['woodl'])
    hline(lay, 0, w + 2, 3, P['wood'])
    for yy in range(5, h - 4):
        for xx in range(3, w):
            sag = int(3 * math.sin(math.pi * (xx - 3) / (w - 3)))
            if yy < 5 + 12 + sag and (xx + yy) % 4 == 0:
                put(lay, xx, yy, '#6c8a94')
            elif yy < 5 + 12 + sag and (xx - yy) % 4 == 0:
                put(lay, xx, yy, '#4c6a78')
    for xx in (9, 20, 28):
        sag = int(3 * math.sin(math.pi * (xx - 3) / (w - 3)))
        disc(lay, xx, 5 + 12 + sag, 1, '#e8843c')
    blit(im, lay, x, ybase - h)


def scene(with_hud=True, with_touch=True):
    im = backdrop()
    lighthouse(im, 80, 152)
    # hazy headland with the shore battery on top
    hs = []
    for i in range(150):
        t = i / 149
        base = 8 + 68 * min(1, t * 1.9) ** 0.8
        step = (int(base) // 7) * 7 + (3 if (i // 9) % 2 else 0)
        hs.append(step + (2 if (i // 5) % 3 == 0 else 0))
    hill = new()
    rock(hill, 322, 471, 174, hs, seed=17)
    blit(im, tint(hill, C['haze'], 0.22), 0, 0)
    bat = sprite([
        '.........m.......m........',
        '........mM......mM........',
        '.......mMM.....mMM........',
        '......mMM.....mMM.........',
        '.....mMM.....mMM..........',
        '....mMM.....mMM...........',
        '...MMMMMMMMMMMMMMMMMM.....',
        '..MMmmMMMMmmMMMMMMMMMM....',
        '.MMMMMMMMMMMMMMMMMMMMMMM..',
        'bbbbbbbbbbbbbbbbbbbbbbbbbb',
    ], {'M': '#5c5a70', 'm': '#44425a', 'b': '#c8b488'})
    blit(im, tint(bat, C['haze'], 0.3), 372, 174 - 78)
    dhow(im, 168, 152)
    pier(im, 0, 70, 160)
    # beach
    sand(im, 172, H - 1, seed=5)
    foam = profile(W, 9, 4, step=14)
    for x in range(W):
        f = int(foam[x])
        vline(im, x, 170 - f, 172, '#f6fbf2')
        put(im, x, 173 + (f % 2), '#e2cf98')
        if (x + f) % 7 == 0:
            put(im, x, 168 - f, '#c8f2e4')
    hline(im, 0, W - 1, 174, '#dcc488')
    for xx, yy in ((58, 199), (213, 203), (290, 208), (120, 210), (338, 201)):   # shells
        hline(im, xx, xx + 2, yy, '#f8f0d0')
        put(im, xx + 1, yy - 1, '#fbe0c8')
    for xx in range(60, 118, 10):                                             # footprints
        hline(im, xx, xx + 3, 191 + (xx // 10) % 2 * 4, C['sand4'])
    # seaweed and driftwood along the tide line, a starfish, pebbles
    for xx, ln in ((150, 9), (206, 6), (284, 11), (338, 7)):
        hline(im, xx, xx + ln, 176, '#5c8a54')
        hline(im, xx + 1, xx + ln - 2, 175, '#7cae64')
    rect(im, 250, 200, 268, 201, P['woods'])
    hline(im, 250, 268, 200, P['woodl'])
    put(im, 269, 200, P['woodd'])
    st = sprite(['..o..', 'ooooo', '.ooo.', 'o...o'], {'o': '#f08a4c'})
    blit(im, outline(st, INK), 300, 196)
    r = rng(23)
    for _ in range(26):
        xx, yy = r.randint(0, W - 1), r.randint(205, H - 2)
        rect(im, xx, yy, xx + r.choice([1, 2, 2, 3]), yy + 1, r.choice(['#9a7c54', '#c4a674', '#7c6044']))
        put(im, xx, yy, '#e0c890')
    # palms and the drying nets, behind the fight
    palm(im, 26, 180, 64, seed=3, lean=9, fronds=9, edge='#243828')
    palm(im, 284, 178, 40, seed=8, lean=-4, fronds=8, haze=(C['haze'], 0.12), size=0.8)

    # foreground rocks on the right: two ledges
    rk = new()
    hs1 = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 41, 43] + [44] * 30 + [45, 47, 50, 54, 58, 62, 66, 70, 72] + [73] * 40
    rock(rk, 380, 467, 188, hs1, seed=6, strata=9)
    for bx, by, br in ((384, 187, 3), (392, 188, 2), (377, 188, 2)):       # loose boulders
        disc(rk, bx, by, br, C['rock2'])
        disc(rk, bx - 1, by - 1, max(1, br - 1), C['rock1'])
    blit(im, outline(rk, INK), -1, -1)
    for gx in (398, 404, 431, 452, 461):                                    # dry grass on the ledges
        gy = 188 - hs1[gx - 380]
        for k in (-1, 0, 1):
            vline(im, gx + k, gy - 3 - (k == 0), gy - 1, '#b8a858')

    def stand(spr, x, y=GROUND, sh=18):
        img, fx, fy = spr
        if sh:
            shadow(im, x, y, sh)
        blit(im, img, x - fx, y - fy)
        return x - fx, y - fy

    # the freed detainee legs it; his post and ropes stay behind
    post = sprite(['.BB.', 'BBBb'] + ['.Bb.'] * 30, {'B': P['wood'], 'b': P['woods']})
    blit(im, outline(post, INK), 100, GROUND - 31)
    for dx, dy in ((0, 0), (3, 1), (6, 0), (8, 2), (-4, 1), (-7, 2)):
        put(im, 98 + dx, GROUND + 1 + dy % 2, '#8c6240')
        put(im, 99 + dx, GROUND + 1 + dy % 2, '#6a4a34')
    stand(cast.detainee(flip=True, freed=True), 76, GROUND)
    for i in range(3):                                   # speed lines
        hline(im, 92, 98 - i * 2, 160 + i * 7, '#fbf8ec')
    drum(im, 6, GROUND + 3, 'blue')
    crate(im, 21, GROUND + 4)

    # enemy rifleman behind sandbags
    ex, ey = stand(cast.grunt('rifle', 3, flip=True), 262, GROUND - 1, sh=0)
    sandbags(im, 234, GROUND + 2, 3, 3)
    # field kitchen and its cook
    cauldron(im, 292, GROUND + 1)
    cx, cy = stand(cast.grunt('cook', 2, flip=True), 314, GROUND + 1)
    # the rules sign, with a goat on it
    sw, sh_ = sign(im, 356, GROUND + 2, ['BEACH RULES', 'NO SWIMMING', 'NO SURRENDERING'], post=20)
    goat(im, 356 + sw // 2 - 2, GROUND + 2 - 20 - 2, flip=True)
    # RPG gunner on the ledge
    rx, ry = stand(cast.grunt('rpg', 1, flip=True), 414, 188 - 44, sh=0)
    crab(im, 222, 207)
    gull(im, 176, 66)
    gull(im, 192, 74, 1)
    gull(im, 330, 52)

    # Yazeed, running and gunning
    sx, sy = stand(cast.hero('yazeed', 'run', 'hmg'), 138, GROUND)
    mx, my = sx + 53, sy + 22
    muzzle(im, mx, my, s=2)
    tracer(im, mx + 30, my - 1, 12)
    tracer(im, mx + 52, my, 12)
    for dx, dy in ((-4, -7), (-9, -12), (-15, -14), (-21, -11), (-26, -5)):     # spent brass
        rect(im, sx + 22 + dx, sy + 14 + dy, sx + 23 + dx, sy + 14 + dy, P['yel'])
        put(im, sx + 23 + dx, sy + 15 + dy, P['yels'])
    for dx, r_ in ((-14, 4), (-23, 3), (-31, 2)):                             # dust
        puff(im, 138 + dx, GROUND, r_, '#f8ecc4', '#e4cf98', '#c8b078')
    # rounds chewing up the sandbags
    explosion(im, 237, 170, 6, seed=3, smoke=False)
    debris(im, 238, 164, 10, 17, [C['bag2'], C['bag3'], C['sand2'], C['bag1']], seed=4)
    # enemy round coming back, low
    disc(im, 196, 176, 2, C['fire4'])
    disc(im, 196, 176, 1, C['fire1'])
    hline(im, 199, 206, 176, C['fire4'])
    # rocket in flight, smoke trail back to the gunner
    rk2 = sprite(['...666......', '.6666666MMMf', '66666666MMMf', '.6666666MMMf', '...666......'],
                 {'6': '#8a9a4e', 'M': '#667284', 'f': C['fire2']})
    rxx, ryy = 322, 128
    for i, (dx, dy, rr) in enumerate([(16, 0, 3), (25, -1, 4), (35, 0, 4), (45, -2, 3), (54, -1, 3), (62, -3, 2)]):
        puff(im, rxx + dx, ryy + 2 + dy, rr)
    blit(im, outline(rk2, INK), rxx - 1, ryy - 1)
    rect(im, rxx + 12, ryy + 1, rxx + 14, ryy + 3, C['fire3'])

    bubble(im, 304, 122, "I'm just the cook!", tail_x=58)
    if with_hud:
        hud.gameplay_hud(im, hero='yazeed', plates=3, lives=3, arms='187', bombs='10', score=12400,
                         radio=1.4, freed=(2, 5), time='1:42', par='4:30')
        banner(im, 190, 42, 'HEAVY MG!', scale_=2)
    if with_touch:
        hud.touch_controls(im, stick=(1, 0))
    return im


if __name__ == '__main__':
    im = scene()
    save(im, 'screen_strait.png')
    save(im, 'screen_strait_x3.png', 3)
    save(scene(with_touch=False), 'screen_strait_clean_x3.png', 3)
