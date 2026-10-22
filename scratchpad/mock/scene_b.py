# scene_b.py - Old Sanaa at dusk: rooftops, a protected zone, a demolition team on a countdown.
from px import *
from palette import P
from world import *
from sanaa import *
import cast, hud

SKY = ['#272a5c', '#352f6c', '#4f3a80', '#7a4a8c', '#b05a88', '#e2767c', '#f8a468', '#fcd08c']


def backdrop():
    im = new()
    vbands(im, 0, 0, W - 1, 132, SKY, soft=3)
    r = rng(5)
    for _ in range(46):                                    # stars
        x, y = r.randint(0, W - 1), r.randint(26, 70)
        put(im, x, y, '#f4ecd0' if r.random() < 0.6 else '#b8a8d8')
    for x, y in ((64, 44), (150, 58), (300, 40), (372, 62)):
        put(im, x, y, '#ffffff')
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            put(im, x + dx, y + dy, '#d8d0f0')
    disc(im, 404, 50, 8, '#fbf0c8')                        # crescent moon
    disc(im, 408, 47, 7, rgba(SKY[1]))
    # long clouds catching the last light
    for (cx, cy, cw, s) in ((30, 92, 120, 3), (190, 78, 90, 4), (300, 104, 150, 6), (120, 116, 110, 8)):
        lay = new(cw + 20, 12)
        pr = profile(cw, s, 4, step=12)
        for i in range(cw):
            t = i / cw
            env = min(1, t * 6, (1 - t) * 6)
            hh = int((1 + pr[i]) * env)
            if hh > 0:
                vline(lay, i + 10, 8 - hh, 8, '#c8749c')
                put(lay, i + 10, 8, '#ffb07c')
                if hh > 2:
                    put(lay, i + 10, 8 - hh, '#9a5c98')
        blit(im, lay, cx, cy)
    rect(im, 0, 132, W - 1, H - 1, '#4a3660')                 # the city floor, in shadow
    # the mountain east of the city
    m = profile(W, 44, 22, step=60)
    for x in range(W):
        h = int(m[x] + 10 + 8 * (x / W))
        vline(im, x, 134 - h, 134, '#8a5c90')
        put(im, x, 134 - h, '#b47c98')
        if x % 3 == 0:
            put(im, x, 134 - h + 2, '#9a6898')
    return im


def laundry(im, x0, y0, x1, y1, seed=3):
    r = rng(seed)
    n = x1 - x0
    pts = []
    for i in range(n + 1):
        t = i / n
        y = y0 + (y1 - y0) * t + int(5 * math.sin(math.pi * t))
        pts.append((x0 + i, int(y)))
        put(im, x0 + i, int(y), '#2a2238')
    i = 3
    cols = ['#d8483c', '#3f8fd8', '#f4c63c', '#fbf8ec', '#4cb060', '#cc5492']
    while i < n - 6:
        x, y = pts[i]
        c = r.choice(cols)
        w = r.choice([5, 6, 7])
        h = r.choice([7, 9, 11])
        rect(im, x, y + 1, x + w - 1, y + h, c)
        rect(im, x + w - 1, y + 1, x + w - 1, y + h, rgba(c, 255))
        vline(im, x + w - 1, y + 2, y + h, (0, 0, 0, 60))
        if h > 8:
            hline(im, x, x + w - 1, y + h - 2, '#fbf8ec' if c != '#fbf8ec' else '#3f8fd8')
        put(im, x, y, '#fbf8ec')
        put(im, x + w - 1, y, '#fbf8ec')
        i += w + r.randint(1, 3)


def tank(im, x, ybase):
    t = sprite([
        '...QQQQQQQQQ...',
        '..MMMMMMMMMMM..',
        '.MMQQMMMMMMMmm.',
        '.MMQMMMMMMMMmm.',
        '.MMQMMMMMMMMmm.',
        '.MMMMMMMMMMMmm.',
        '.MMQMMMMMMMMmm.',
        '.MMQMMMMMMMMmm.',
        '.MMMMMMMMMMMmm.',
        '..mmmmmmmmmmm..',
        '..b....b....b..',
        '..b...b.b...b..',
        '..b..b...b..b..',
        '..bbbbbbbbbbb..',
    ], {'M': '#3c5c8c', 'm': '#263c64', 'Q': '#6c94c4', 'b': '#4a4458'})
    blit(im, outline(t, INK), x, ybase - 15)


def dish(im, x, ybase):
    d = sprite([
        '.....wWWW....',
        '...wWWWWWWW..',
        '..wWWWWWWWWW.',
        '.wWWWWoWWWWWm',
        '.wWWWWWoWWWm.',
        '..wWWWWWoWm..',
        '...wwWWWmmo..',
        '.....wwm...o.',
        '......bb.....',
        '......bb.....',
        '......bb.....',
        '.....bbbb....',
    ], {'W': '#e8e4e0', 'w': '#fbf8f4', 'm': '#a8a0b0', 'o': '#5a5268', 'b': '#4a4458'})
    blit(im, outline(d, INK), x, ybase - 13)


def antenna(im, x, ybase, h=22):
    vline(im, x, ybase - h, ybase, '#2a2238')
    for k, w in ((0, 5), (4, 4), (8, 3)):
        hline(im, x - w, x + w, ybase - h + k, '#2a2238')


def hut(im, x, ybase, w=26, h=22):
    lay = new(w, h + 6)
    tower(lay, 0, 5, w, h + 1, seed=9, lit=0, big=False, merlons=False)
    rect(lay, 8, 13, 17, h + 5, DUSK['wood'])
    rect(lay, 8, 13, 17, 13, DUSK['white'])
    rect(lay, 7, 13, 7, h + 5, DUSK['white'])
    rect(lay, 18, 13, 18, h + 5, DUSK['white'])
    vline(lay, 12, 14, h + 5, '#4a2c24')
    put(lay, 15, 20, DUSK['lamp'])
    blit(im, outline(lay.crop(lay.getbbox()), INK), x - 1, ybase - h - 2)


def rug(im, x, ytop, w=24, h=16):
    for j in range(h):
        for i in range(w):
            c = '#b83c44'
            if j in (1, h - 2) or i in (1, w - 2):
                c = '#f4c63c'
            elif (i + j) % 6 == 0 or (i - j) % 6 == 0:
                c = '#2a66a8'
            elif (i // 3 + j // 3) % 2 == 0:
                c = '#862a38'
            put(im, x + i, ytop + j, c)
    for i in range(0, w, 2):
        put(im, x + i, ytop + h, '#fbe6c8')
    frame(im, x - 1, ytop - 1, x + w, ytop + h + 1, INK)


def cat(im, x, ybase):
    c = sprite(['o.o......', 'ooo......', 'oyo...o..', 'ooooo..o.', '.ooooo.o.', '.oooooo..', '.oo.oo...'],
               {'o': '#2a2238', 'y': '#f4c63c'})
    blit(im, c, x, ybase - 7)


def ladder(im, x0, y0, x1, y1):
    for off in (0, 6):
        line(im, x0 + off, y0, x1 + off, y1, P['woods'])
        line(im, x0 + off + 1, y0, x1 + off + 1, y1, P['wood'])
    n = abs(y1 - y0) // 5
    for i in range(1, n):
        t = i / n
        xx = int(x0 + (x1 - x0) * t)
        yy = int(y0 + (y1 - y0) * t)
        hline(im, xx + 1, xx + 6, yy, P['woodl'])


def pigeon(im, x, y, fly=False):
    if fly:
        hline(im, x - 3, x - 1, y - 1, '#c8c0d8')
        put(im, x, y, '#e8e0f0')
        hline(im, x + 1, x + 3, y - 1, '#c8c0d8')
    else:
        rect(im, x, y - 3, x + 3, y - 1, '#9a94b0')
        rect(im, x + 3, y - 5, x + 4, y - 3, '#b8b0c8')
        put(im, x + 5, y - 4, '#f4a45c')
        put(im, x - 1, y - 2, '#7a748c')
        put(im, x + 1, y, '#f4a45c')


def countdown(im, cx, y, secs='0:14'):
    w = 46
    pill(im, cx - w // 2, y, cx + w // 2, y + 21, (24, 18, 34, 225), r=3)
    frame(im, cx - w // 2, y, cx + w // 2, y + 21, '#e8483c')
    text(im, cx, y + 3, 'CHARGE SET', FONT_S, '#f4ecd0', align='c')
    text(im, cx, y + 10, secs, FONT_B, '#ff6a4a', align='c')
    poly(im, [(cx - 3, y + 22), (cx + 3, y + 22), (cx, y + 26)], '#e8483c')


def scene(with_hud=True, with_touch=True):
    im = backdrop()
    # far skyline with minarets
    far = new()
    skyline(far, 146, 31, '#5e4672', '#7c5c88', '#ffd880', 14, 40)
    for mx, mh in ((62, 54), (236, 62), (424, 50)):
        minaret(far, mx, 146, mh, '#5e4672', '#8a6894', lit='#ffd880')
    blit(im, far, 0, 0)
    # mid towers, hazed
    mid = new()
    specs = [(14, 96, 38), (60, 110, 30), (150, 84, 34), (196, 104, 28), (300, 92, 36), (346, 74, 32), (430, 100, 40)]
    for i, (x, yt, w) in enumerate(specs):
        tower(mid, x, yt, w, 170 - yt, seed=40 + i, big=False, floor_h=22, lit=0.6)
    mid = tint(mid, '#7a5088', 0.42)
    blit(im, mid, 0, 0)
    # the sniper's laser from a mid tower window
    sx0, sy0 = 318, 106
    lz = new()
    line(lz, sx0, sy0, 118, 151, (255, 60, 60, 210))
    blit(im, lz, 0, 0)
    disc(im, sx0, sy0, 2, '#ff6a4a')
    put(im, sx0, sy0, '#ffffff')

    # foreground roofs: left, middle, and the tall house on the right
    fg = new()
    tower(fg, -8, 172, 160, 60, seed=3, lit=0.7)
    tower(fg, 180, 160, 152, 70, seed=5, lit=0.75)
    tower(fg, 346, 124, 130, 110, seed=8, lit=0.85)
    blit(im, outline(fg, INK), -1, -1)
    # alleys between the houses: deep shadow, a lantern each
    for x0, x1, yt, ly in ((152, 179, 150, 196), (332, 345, 150, 186)):
        for yy in range(yt, H):
            t = (yy - yt) / (H - yt)
            c = '#3a2a50' if t < 0.5 else '#2e2040'
            hline(im, x0, x1, yy, c)
        cx = (x0 + x1) // 2
        disc(im, cx, ly, 5, (255, 190, 90, 60))
        disc(im, cx, ly, 3, (255, 200, 100, 110))
        rect(im, cx - 1, ly - 1, cx + 1, ly + 1, '#ffd880')
        vline(im, cx, yt + 20, ly - 2, '#1a1220')
    # rooftop dressing
    tank(im, 6, 172)
    dish(im, 44, 172)
    antenna(im, 30, 172, 26)
    vline(im, 144, 146, 172, P['woods'])
    vline(im, 186, 136, 160, P['woods'])
    laundry(im, 144, 147, 186, 137, seed=4)
    antenna(im, 204, 160, 24)
    rug(im, 222, 161, 26, 17)
    cat(im, 250, 160)
    hut(im, 300, 160)
    ladder(im, 334, 160, 342, 124)
    pigeon(im, 356, 124)
    pigeon(im, 366, 124)
    for px_, py_ in ((250, 96), (262, 90), (276, 99), (120, 74), (132, 80)):
        pigeon(im, px_, py_, fly=True)
    # the charge on the tall house's parapet
    ch = sprite(['.oo.oo.', 'RRRRRRR', 'RrRrRrR', 'RRRRRRR', 'oYoooRo'], {'R': '#d8483c', 'r': '#a02c30', 'o': INK, 'Y': '#f4c63c'})
    blit(im, outline(ch, INK), 376, 118)
    for i in range(376, 398, 3):
        put(im, i, 124 + (i % 2), '#f4c63c')

    def stand(spr, x, y, sh=0):
        img, fx, fy = spr
        blit(im, img, x - fx, y - fy)
        return x - fx, y - fy

    # demolition team on the tall house
    stand(cast.grunt('demo', 2, flip=True), 408, 124)
    stand(cast.grunt('rifle', 3, flip=True, face='wrap_tache'), 446, 124)
    countdown(im, 392, 62)
    # the Guard on the middle roof, taking a hit
    gx, gy = stand(cast.grunt('guard', 1, flip=True), 284, 160)
    # Bilqis on the left roof
    bx, by = stand(cast.hero('bilqis', 'run'), 104, 172)
    mx, my = bx + 57, by + 19
    muzzle(im, mx, my, s=1)
    hline(im, mx + 12, gx + 6, my, '#fff6c8')               # one long shot
    hline(im, mx + 12, gx + 6, my + 1, (255, 216, 74, 150))
    explosion(im, gx + 8, my, 5, seed=5, smoke=False)
    for dx, dy in ((-6, 5), (-11, 9)):
        rect(im, bx + 30 + dx, by + 12 + dy, bx + 31 + dx, by + 12 + dy, P['yel'])
    if with_hud:
        hud.gameplay_hud(im, hero='bilqis', plates=2, lives=3, arms='12', bombs='0', score=86250,
                         radio=0.6, freed=(1, 3), time='3:05', par='5:00', locked=True)
        pill(im, 150, 34, 318, 58, (24, 18, 34, 200), r=3)
        frame(im, 150, 34, 318, 58, '#84c4f2')
        banner(im, 234, 36, 'PROTECTED ZONE', scale_=1,
               grad=['#ffffff', '#e4f4ff', '#bfe4ff', '#84c4f2', '#58aaf0', '#3f8fd8'])
        text(im, 234, 50, 'EXPLOSIVES LOCKED  -  HOUSES INTACT 3/3', FONT_S, '#f4ecd0', align='c')
        hud.dialog_bar(im, 'veil', cast.PAL['bilqis'], '#862a38', 'BILQIS',
                       "Mind the windows. They're older than all of us.", y=188, x0=84, x1=362)
    if with_touch:
        hud.touch_controls(im, stick=(1, 0), locked=True)
    return im


if __name__ == '__main__':
    save(scene(), 'screen_sanaa_x3.png', 3)
    save(scene(with_touch=False), 'screen_sanaa_clean_x3.png', 3)
