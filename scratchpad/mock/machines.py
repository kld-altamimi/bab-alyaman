# machines.py - vehicles and bosses, built from simple shapes and then outlined.
import math
from px import *
from palette import P
from world import INK, C
import cast


def wheel(lay, cx, cy, r=8, hub='#c8ccd4'):
    disc(lay, cx, cy, r, '#2a2630')
    ring(lay, cx, cy, r, '#16121c', 1)
    disc(lay, cx, cy, r - 3, '#4a4654')
    disc(lay, cx, cy, r - 5, hub)
    put(lay, cx, cy, '#5a5664')
    for a in range(0, 360, 45):                       # tread blocks
        x = int(round(cx + math.cos(math.radians(a)) * (r - 1)))
        y = int(round(cy + math.sin(math.radians(a)) * (r - 1)))
        put(lay, x, y, '#5a5664')
    # sand kicked onto the lower tread
    for dx in (-3, 0, 3):
        put(lay, cx + dx, cy + r - 1, '#c8a668')


def shass(driver_head='straw', driver_pal=None, flip=False, firing=True):
    """The hero vehicle: an armed Land Cruiser-style pickup, squat and loud.
    Returns (image, ground_x, ground_y) with ground_x at the rear wheel."""
    Wd, Hd = 112, 70
    lay = new(Wd, Hd)
    g = 62                      # ground line inside the layer
    body, body_s, body_l, body_d = '#f2efe6', '#c9c4b6', '#ffffff', '#8f8a80'
    # --- bed
    poly(lay, [(8, g - 26), (44, g - 26), (44, g - 10), (10, g - 10), (8, g - 14)], body)
    rect(lay, 8, g - 26, 44, g - 25, body_l)
    rect(lay, 9, g - 12, 44, g - 10, body_s)
    for xx in (16, 24, 32, 40):                        # panel ribs
        vline(lay, xx, g - 23, g - 13, body_s)
    rect(lay, 6, g - 27, 9, g - 12, body_s)            # tailgate edge
    rect(lay, 4, g - 14, 8, g - 11, '#3a3640')         # rear bumper
    rect(lay, 6, g - 20, 7, g - 17, '#e8483c')         # tail light
    # --- cab
    poly(lay, [(42, g - 26), (44, g - 40), (64, g - 40), (72, g - 27), (72, g - 10), (42, g - 10)], body)
    rect(lay, 45, g - 40, 63, g - 39, body_l)
    poly(lay, [(47, g - 37), (62, g - 37), (68, g - 28), (47, g - 28)], '#3c5c7c')       # glass
    poly(lay, [(47, g - 37), (53, g - 37), (49, g - 28), (47, g - 28)], '#6c94b4')       # glare
    vline(lay, 56, g - 37, g - 28, body)                                                 # pillar
    rect(lay, 47, g - 27, 71, g - 27, body_s)
    vline(lay, 57, g - 26, g - 11, body_s)                                               # door seam
    rect(lay, 60, g - 22, 63, g - 21, '#5a5664')                                         # handle
    rect(lay, 69, g - 31, 71, g - 28, '#3a3640')                                         # mirror
    # --- hood and nose
    poly(lay, [(72, g - 27), (92, g - 25), (95, g - 22), (95, g - 10), (72, g - 10)], body)
    rect(lay, 73, g - 27, 91, g - 26, body_l)
    for xx in (78, 83, 88):
        hline(lay, xx, xx + 2, g - 23, body_s)                                           # vents
    rect(lay, 93, g - 21, 95, g - 15, '#3a3640')                                         # grille
    rect(lay, 92, g - 24, 94, g - 22, '#ffe066')                                         # headlight
    put(lay, 93, g - 23, '#ffffff')
    rect(lay, 90, g - 13, 99, g - 10, '#3a3640')                                         # bumper
    rect(lay, 96, g - 25, 97, g - 10, '#5a5664')                                         # bull bar
    rect(lay, 94, g - 25, 99, g - 24, '#5a5664')
    rect(lay, 94, g - 18, 99, g - 17, '#5a5664')
    # --- the famous stripes
    for i, c in enumerate(('#e8843c', '#d8483c', '#f4c63c')):
        hline(lay, 10, 70, g - 19 + i, c)
        hline(lay, 72, 90, g - 19 + i, c)
    # --- sills and arches
    rect(lay, 8, g - 10, 95, g - 9, body_d)
    for cx in (22, 80):
        disc(lay, cx, g - 9, 11, '#1e1a24')
    rect(lay, 0, g - 8, Wd - 1, Hd - 1, (0, 0, 0, 0))
    # redraw the lower body the arches cut through
    for cx in (22, 80):
        for yy in range(g - 8, Hd):
            for xx in range(cx - 12, cx + 13):
                lay.putpixel((xx, yy), (0, 0, 0, 0))
    wheel(lay, 22, g - 8, 8)
    wheel(lay, 80, g - 8, 8)
    rect(lay, 31, g - 9, 70, g - 7, '#3a3640')         # chassis rail
    # --- roof rack, lamps, horn, tassels
    rect(lay, 44, g - 43, 64, g - 42, '#3a3640')
    for xx in (46, 51, 56, 61):
        rect(lay, xx, g - 46, xx + 2, g - 44, '#ffe066')
        put(lay, xx + 1, g - 45, '#ffffff')
    for i, xx in enumerate(range(45, 65, 3)):          # tassels under the rack
        put(lay, xx, g - 41, ('#d8483c', '#4cb060', '#f4c63c')[i % 3])
    for i, xx in enumerate(range(10, 44, 3)):          # tassels along the bed rail
        put(lay, xx, g - 24, ('#d8483c', '#4cb060', '#f4c63c')[i % 3])
        if i % 2 == 0:
            put(lay, xx, g - 23, ('#d8483c', '#4cb060', '#f4c63c')[i % 3])
    # antenna with a pennant
    vline(lay, 66, g - 58, g - 40, '#3a3640')
    poly(lay, [(67, g - 58), (74, g - 56), (67, g - 54)], '#3f8fd8')
    hline(lay, 67, 70, g - 56, '#f4c63c')
    # --- cargo: jerrycan, rolled rug, spare wheel
    rect(lay, 10, g - 33, 15, g - 26, '#8a9a4e')
    rect(lay, 10, g - 33, 15, g - 32, '#aebb6a')
    rect(lay, 12, g - 35, 13, g - 34, '#62743a')
    rect(lay, 36, g - 31, 42, g - 26, '#b83c44')
    for xx in (37, 39, 41):
        vline(lay, xx, g - 31, g - 26, '#f4c63c' if xx == 39 else '#862a38')
    # --- the gun on its pintle
    rect(lay, 24, g - 36, 26, g - 26, '#4a4e5c')
    poly(lay, [(20, g - 26), (30, g - 26), (27, g - 30), (23, g - 30)], '#33353f')
    gun = sprite([
        '...........mmm......................',
        '....QQQQQQQQQQQQQQQ.................',
        'MMMMMMMMMMMMMMMMMMMMmQmQmQmQmQmQmMM.',
        'MMmmMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMQ',
        'MMMMMMMMMMMMMMMMMMMMmmmmmmmmmmmmmm..',
        '....mYYYYYYm........................',
        '....mYyyyyYm........................',
        '....mmmmmmmm........................',
    ], cast.WPAL)
    blit(lay, gun, 16, g - 43)
    rect(lay, 21, g - 47, 30, g - 34, (0, 0, 0, 0)) if False else None
    # gun shield
    poly(lay, [(30, g - 49), (34, g - 49), (34, g - 33), (30, g - 35)], '#667284')
    vline(lay, 30, g - 48, g - 36, '#98a4b4')
    # --- the driver: hat through the roof
    if driver_head:
        hd = sprite(cast.HEADS[driver_head], driver_pal or cast.PAL['salem'])
        blit(lay, hd, 45, g - 54)
        # glass back over the lower face so he sits inside the cab
        poly(lay, [(47, g - 37), (62, g - 37), (68, g - 28), (47, g - 28)], (60, 92, 124, 150))
        rect(lay, 44, g - 40, 47, g - 39, body_l)
        rect(lay, 60, g - 40, 64, g - 39, body_l)
    lay2 = lay.crop((0, 0, Wd, g + 1))
    bb = lay2.getbbox()
    out = outline(lay2.crop(bb), INK)
    gx, gy = 22 - bb[0] + 1, g - bb[1] + 1
    if flip:
        out = out.transpose(Image.FLIP_LEFT_RIGHT)
        gx = out.width - 1 - gx
    return out, gx, gy


def ironback(pal_boss=None):
    """Dug-in tank the crew has been living in. Faces left.
    Returns (image, anchor_x, anchor_y): anchor at the hull's left end on the ground."""
    Wd, Hd = 230, 120
    lay = new(Wd, Hd)
    g = 108
    A, B, Cc, D = '#9a62a4', '#743c80', '#52286a', '#381a4c'
    steel, steel_d = '#667284', '#3e4656'
    # --- hull, low and long
    poly(lay, [(92, g - 30), (212, g - 30), (222, g - 20), (222, g - 8), (84, g - 8), (84, g - 22)], B)
    rect(lay, 92, g - 30, 212, g - 29, A)
    rect(lay, 84, g - 12, 222, g - 8, Cc)
    for xx in range(98, 214, 16):
        vline(lay, xx, g - 28, g - 13, Cc)
        put(lay, xx + 2, g - 26, A)
    poly(lay, [(84, g - 22), (92, g - 30), (92, g - 8), (84, g - 8)], Cc)          # glacis
    # tracks and road wheels
    rect(lay, 88, g - 8, 220, g, '#2a2630')
    for cx in range(96, 218, 15):
        disc(lay, cx, g - 4, 5, '#3e3a48')
        disc(lay, cx, g - 4, 2, '#8c88a0')
    for xx in range(88, 221, 4):
        put(lay, xx, g, '#16121c')
        put(lay, xx, g - 9, '#16121c')
    # --- turret: a big dome
    for yy in range(0, 30):
        t = yy / 29
        half = int(34 * math.sqrt(max(0, 1 - (1 - t) ** 2)) + 6)
        c = A if yy < 5 else (B if yy < 20 else Cc)
        hline(lay, 150 - half, 150 + half, g - 60 + yy, c)
    for yy in range(3, 26):                                                       # dome shading
        t = yy / 29
        half = int(34 * math.sqrt(max(0, 1 - (1 - t) ** 2)) + 6)
        for xx in range(150 + half - 10, 150 + half + 1):
            if BAYER4[yy % 4][xx % 4] < 9:
                put(lay, xx, g - 60 + yy, Cc)
        hline(lay, 150 - half + 2, 150 - half + 6, g - 60 + yy, A) if yy % 5 == 0 else None
    rect(lay, 112, g - 32, 190, g - 30, D)                                        # turret ring
    for xx in range(120, 186, 9):                                                 # rivets
        put(lay, xx, g - 36, A)
        put(lay, xx, g - 35, D)
    # scorpion emblem on the turret
    emb = sprite(['Y.....Y', 'YY...YY', '.Y.Y.Y.', '..YYY..', '..YYY..', '...Y..Y', '...YYYY'], {'Y': '#f4c63c'})
    blit(lay, scale(emb, 2), 146, g - 54)
    # --- the gun: long, with hazard stripes
    rect(lay, 112, g - 50, 122, g - 42, Cc)                                       # mantlet
    rect(lay, 16, g - 49, 114, g - 44, steel)
    rect(lay, 16, g - 49, 114, g - 48, '#98a4b4')
    rect(lay, 16, g - 45, 114, g - 44, steel_d)
    rect(lay, 62, g - 51, 78, g - 42, steel)                                      # fume extractor
    rect(lay, 62, g - 51, 78, g - 50, '#98a4b4')
    rect(lay, 62, g - 43, 78, g - 42, steel_d)
    rect(lay, 10, g - 51, 18, g - 42, steel_d)                                    # muzzle brake
    rect(lay, 10, g - 51, 18, g - 50, steel)
    for xx in range(22, 58, 8):                                                   # hazard bands
        poly(lay, [(xx, g - 44), (xx + 4, g - 49), (xx + 8, g - 49), (xx + 4, g - 44)], '#f4c63c')
    # --- home comforts: washing line from the barrel to the antenna
    vline(lay, 186, g - 86, g - 56, '#2a2238')
    pts = []
    for i in range(0, 151):
        t = i / 150
        x = 36 + i
        y = int((g - 51) + (g - 84 - (g - 51)) * t + 9 * math.sin(math.pi * t))
        pts.append((x, y))
        put(lay, x, y, '#2a2238')
    items = [(12, '#fbf8ec', 4, 6), (22, '#d8483c', 3, 7), (31, '#fbf8ec', 4, 6), (42, '#3f8fd8', 7, 9),
             (56, '#f4c63c', 3, 6), (64, '#fbf8ec', 6, 8), (78, '#4cb060', 3, 7), (88, '#cc5492', 7, 10),
             (104, '#fbf8ec', 3, 6), (114, '#d8483c', 6, 8)]
    for i, c, w, h in items:
        x, y = pts[i]
        rect(lay, x, y + 1, x + w - 1, y + h, c)
        vline(lay, x + w - 1, y + 2, y + h, (0, 0, 0, 55))
        if w <= 4:                                            # socks get a toe
            rect(lay, x + w, y + h - 1, x + w + 1, y + h, c)
    # satellite dish and kettle on the turret roof
    d = sprite(['....wWWW....', '..wWWWWWWW..', '.wWWWWoWWWWm', '.wWWWWWoWWm.', '..wwWWWWom..', '....wwmm..o.', '.....bb.....', '.....bb.....'],
               {'W': '#e8e4e0', 'w': '#fbf8f4', 'm': '#a8a0b0', 'o': '#5a5268', 'b': '#4a4458'})
    blit(lay, d, 166, g - 68)
    k = sprite(['..MMM...', '.MQMMM.m', 'MMMMMMMm', 'MMMMMMm.', '.MMMMM..'], {'M': '#c8922a', 'Q': '#fce88c', 'm': '#8c6240'})
    blit(lay, k, 126, g - 65)
    put(lay, 128, g - 67, '#f4f4ee')
    put(lay, 129, g - 69, '#f4f4ee')
    # a rug over the engine deck and a potted basil
    for j in range(0, 9):
        for i in range(0, 20):
            c = '#b83c44'
            if j in (1, 7) or i in (1, 18):
                c = '#f4c63c'
            elif (i + j) % 5 == 0:
                c = '#2a66a8'
            put(lay, 196 + i, g - 30 + j, c)
    rect(lay, 214, g - 36, 219, g - 31, '#a85c38')
    for dx, dy in ((0, -3), (2, -5), (4, -3), (1, -1), (3, -2), (5, -4)):
        put(lay, 214 + dx, g - 36 + dy, '#4cb060')
    out_bb = lay.getbbox()
    out = outline(lay.crop(out_bb), INK)
    return out, 84 - out_bb[0] + 1, g - out_bb[1] + 1, (150 - out_bb[0] + 1, g - 60 - out_bb[1] + 1), (10 - out_bb[0] + 1, g - 47 - out_bb[1] + 1)


def camel(flip=False):
    c = sprite([
        '..............................hh....',
        '.............................hCCC...',
        '............................CCCCeC..',
        '............................CCCCCCc.',
        '...........................CCCC.cc..',
        '..........................CCCC......',
        '.............CCCC.........CCC.......',
        '...........CCCCCCCC......CCCC.......',
        '..........CCCCCCCCCC....CCCC........',
        '.....CCCCCCCCCCCCCCCCCCCCCC.........',
        '...CCCCCCCCCCCCCCCCCCCCCCC..........',
        '..CCCCCCCCCCCCCCCCCCCCCCCc..........',
        '.tCCCCCCCCCCCCCCCCCCCCCCcc..........',
        '.tCCCCCCCCCCCCCCCCCCCCCCc...........',
        't.CCCcCCCCCCCCCCCCcCCCCc............',
        '..CCc.cCC......CCc.cCC..............',
        '..Cc...CC......Cc...CC..............',
        '..Cc...Cc......Cc...Cc..............',
        '..Cc...Cc......Cc...Cc..............',
        '..Cc...Cc......Cc...Cc..............',
        '..Cc...Cc......Cc...Cc..............',
        '..CC...CC......CC...CC..............',
        '..oo...oo......oo...oo..............',
    ], {'C': '#d8a868', 'c': '#b08048', 'h': '#8c6240', 'e': INK, 't': '#b08048', 'o': '#6a4a34'})
    o = outline(c, INK)
    if flip:
        o = o.transpose(Image.FLIP_LEFT_RIGHT)
    return o


if __name__ == '__main__':
    sheet = new(420, 150, hexc('#e8cf98'))
    im, gx, gy = shass()
    blit(sheet, im, 10, 130 - gy)
    tk = ironback()
    blit(sheet, tk[0], 150, 130 - tk[2])
    blit(sheet, camel(), 100, 60)
    rect(sheet, 0, 130, 419, 130, '#b48e58')
    save(sheet, 't_machines.png', 4)
