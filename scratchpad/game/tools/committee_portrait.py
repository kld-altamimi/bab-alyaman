# committee_portrait.py - Dhamar stage 1: the Committee's portrait, drawn at a parametric scale as the Spokesman's S6 was
# (spokesman_s6.py: 48 x 32 units, scale 2 for a screen's real size, scale 4 to present), so the look can be judged
# before any sprite is final. First drawn 10 Nov by the development run; redrawn 11 Nov from the photo and the wages clip
# Khaled sent ("the character design needs to be closer to how he looks"): a caricature by his traits, as the
# Spokesman's was. The head is a pixel grid at half a unit (so the glasses, the brows and the grey in the beard have
# room): thick black curly hair standing up and swept back, heavy brows, rimless glasses with a gold bar along the top
# and gold arms, heavy lids, a broad nose, a short beard going grey. A dark navy jacket over the white thobe buttoned to
# its band collar, the pockets bulging with notes, the jambiya with its horn hilt and pale sheath on a black-and-gold
# belt; no shemagh (he wears none). The game's own: the loudhailer up in one hand, the stamp on its chain under the
# other, the gavel he never uses and the sign-in sheet with one name. Two frames: speaking (the drone) and the laugh as
# in the clip (eyes squeezed shut behind the glasses, the cheeks up, the mouth wide, the head back and tilted, the
# shoulders up, notes in the air). No emblem, no flag, no text anywhere. Own drawing.
#   python3 committee_portrait.py   -> dhamar/s1/committee_portrait.png (both frames at scale 4, side by side)
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'dhamar', 's1')

WALL, WALL_D, WALL_L = (214, 200, 170), (178, 162, 130), (236, 226, 200)
WOOD, WOOD_D, WOOD_L = (116, 70, 36), (80, 46, 22), (152, 100, 54)
COAT, COAT_D, COAT_L = (34, 44, 66), (14, 18, 28), (62, 78, 106)
THOBE, THOBE_D = (250, 246, 232), (200, 192, 170)
RED, RED_D, WHITE_CHK = (164, 48, 28), (90, 18, 8), (240, 228, 200)
HORN, HORN_L, SHEATH, SHEATH_D = (58, 36, 24), (96, 64, 42), (226, 200, 160), (176, 146, 106)
BELT, BELT_L = (22, 20, 22), (52, 48, 50)
GOLD, GOLD_D = (228, 186, 74), (170, 126, 40)
NOTE, NOTE_D, NOTE_L = (122, 156, 124), (62, 90, 68), (196, 216, 184)
OL = (40, 28, 24)
SKIN, SKIN_D, SKIN_L = (214, 160, 126), (168, 114, 88), (238, 196, 162)
HAIR, HAIR_L = (36, 26, 20), (76, 58, 46)
IRIS, PUPIL, EYE_W = (70, 44, 28), (18, 12, 10), (246, 242, 236)
GREEN, GREEN_D = (44, 124, 60), (16, 60, 28)
RUBBER = (28, 28, 30)


# ---------------------------------------------------------------- his head, at half a unit (24 x 28)
HEAD_PAL = {'u': (22, 18, 15), 'v': (44, 38, 34), 'w': (90, 82, 76), 'p': (106, 64, 48), 'q': SKIN_D, 'r': SKIN,
            's': SKIN_L, 'x': (28, 26, 24), 'y': (62, 58, 55), 'z': (122, 116, 108), 'Z': (172, 166, 156),
            'E': (212, 156, 28), 'D': (138, 100, 16), 'J': (244, 248, 255), 'Q': (246, 242, 234), '#': (26, 14, 10),
            'K': (90, 20, 16), 'M': (154, 74, 60), 'L': (184, 48, 28)}
HEAD_TOP = [
    '........uuuuuuuu........',
    '.....uuuuvuuuuuuuu......',
    '...uuuuuuuuwuuuvuuuu....',
    '..uuuvuuuuuuuuuuuuuuuu..',
    '..uuuuuuwuuuuuuuvuuuuuu.',
    '.uuuuuuuuuuuvuuuuuuuuuu.',
    '.uuvuuuuuuuuuuuuuuuuwuuu',
    '.uuuuuuuuuuuuuuuuuuuuuuu',
    '.uuuurrruuuuuuuuuurrruuu',
    '.uuurrrrrrruuuurrrrrrruu',
    '.uuqrrrrrrrrrrrrrrrrrruu',
    '.uqruuuuuuuqrrquuuuuuurq',
    'rDDEEEEEEEEDDDDEEEEEEEDD',     # the glasses: the gold bar over both lenses, the arms back to the ears
]
HEAD_EYES = [                       # heavy lids, dark eyes, the bags under them; the lens's corners catch the light
    'qrrsqq##qqsrrrsqq##qqsrq',
    'qrrsrQ##rrsrqrsrQ##rrsrq',
    'qrrJpppprrJrqrJrpppprJrq',
]
HEAD_EYES_LAUGH = [                 # squeezed shut, the cheeks pushed up into the lenses
    'qrrsrr####srrrsr####rsrq',
    'qrrs##ssss##rr##ssss##rq',
    'qrrJssssssJrqrJssssssJrq',
]
HEAD_NOSE = [
    'qqrrrrrrrrrsqrrrrrrrrrqq',
    '.qyrrrrrrrqssqrrrrrrryq.',
    '.yyrrrrrrqpssprrrrrrryy.',
    '.yyyrrrrqp#qq#pqrrrryyy.',
]
HEAD_LOW = [                        # the moustache, the lower lip, the beard: charcoal peppered grey, greyer at the chin
    '..yxyyyxyyyyyyyyyxyyyxy.',
    '..yzyyyyyqMMMMqyyyyyzy..',
    '..yyzyyzyyyyyyyyzyyzyy..',
    '...yzyyyzyZzyzyyyzyyy...',
    '...yyzyzyZZzZzyzyzyy....',
    '....yyzyzZZZZzyzyy......',
    '......yyzyzZzyzyy.......',
    '........yyyyyyy.........',
]
HEAD_LOW_LAUGH = [                  # the mouth wide open in the beard, the top teeth, the jaw dropped
    '..yxyyyxyyyyyyyyyxyyyxy.',
    '..yzy#JJJJJJJJJJJJ#yzy..',
    '..yy#KKKKKKKKKKKKKK#zy..',
    '..yz#KKKKKMMMMKKKKK#zy..',
    '..yyz#KKKKMMMMKKKK#yzy..',
    '...yzy##KKKKKKKK##yzy...',
    '...yyzyZ########ZyZyy...',
    '....yyzyzZZZZZzyzyy.....',
    '......yyzyzZzyzyy.......',
    '........yyyyyyy.........',
]
HEAD = HEAD_TOP + HEAD_EYES + HEAD_NOSE + HEAD_LOW
HEAD_LAUGH = HEAD_TOP + HEAD_EYES_LAUGH + HEAD_NOSE[:3] + HEAD_LOW_LAUGH


def grid(im, rows, x0, y0, hu, tilt=0.0):
    """Paint a letter grid at (x0, y0), each cell hu x hu pixels; tilt shears it (cells per row, about the middle row):
    the head thrown back to one side."""
    d = ImageDraw.Draw(im)
    mid = len(rows) / 2
    for j, row in enumerate(rows):
        sh = int(round((j - mid) * tilt))
        for i, ch in enumerate(row):
            if ch in HEAD_PAL:
                x = x0 + (i + sh) * hu
                y = y0 + j * hu
                d.rectangle([x, y, x + hu - 1, y + hu - 1], fill=HEAD_PAL[ch])


def outline(im, colour=OL):
    """A one-pixel line round everything that is not transparent (for the head pasted onto the picture)."""
    a = im.getchannel('A')
    from PIL import ImageFilter
    grown = a.filter(ImageFilter.MaxFilter(3))
    edge = Image.new('RGBA', im.size, colour + (255,))
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    out.paste(edge, (0, 0), grown)
    out.alpha_composite(im)
    return out


def portrait(s=4, laugh=False):
    W, H = 48 * s, 32 * s
    hu = max(1, s // 2)
    im = Image.new('RGBA', (W, H), WALL)
    d = ImageDraw.Draw(im)
    # the wall: whitewash, a dado line, a wooden panel behind him (nothing on it)
    d.rectangle([0, 0, W, 2 * s], fill=WALL_L)
    d.rectangle([0, 19 * s, W, 19 * s + s // 2], fill=WALL_D)
    d.rectangle([14 * s, 3 * s, 34 * s, 19 * s], fill=(196, 176, 140), outline=WALL_D)
    for x in range(15 * s, 34 * s, 3 * s):
        d.line([(x, 3 * s), (x, 19 * s)], fill=(186, 166, 130))
    cx = 24 * s
    top = 4 * s
    lift = -s if laugh else 0                   # the shoulders going: the trunk a unit higher
    py = 26 * s
    # trunk: the jacket, wide at the shoulders, open in a V over the thobe
    sh = top + 15 * s + lift
    body = [(cx - 15 * s, py), (cx - 13 * s, sh + 3 * s), (cx - 6 * s, sh), (cx + 6 * s, sh), (cx + 13 * s, sh + 3 * s),
            (cx + 15 * s, py)]
    d.polygon(body, fill=COAT, outline=OL)
    for x in range(cx - 13 * s, cx + 14 * s, 2 * s):                                                # a faint pinstripe
        d.line([(x, sh + 3 * s), (x, py)], fill=(42, 54, 78))
    d.polygon([(cx - 5 * s, sh), (cx, sh + 8 * s), (cx + 5 * s, sh)], fill=THOBE, outline=OL)      # the V of the thobe
    d.line([(cx, sh + s), (cx, sh + 2 * s)], fill=THOBE_D)                                          # its placket
    for k in range(1):
        d.rectangle([cx - s // 4 - 1, sh + 2 * s + k * 2 * s, cx + s // 4, sh + 2 * s + k * 2 * s + s // 2], fill=(214, 206, 186))
    d.rounded_rectangle([cx - 4 * s, sh - s, cx + 4 * s, sh + s // 2], radius=s // 2, fill=THOBE, outline=THOBE_D)  # the band collar
    # lapels: the jacket's edges either side of the V
    d.line([(cx - 5 * s, sh), (cx - s, sh + 9 * s)], fill=COAT_L, width=max(1, s // 2))
    d.line([(cx + 5 * s, sh), (cx + s, sh + 9 * s)], fill=COAT_D, width=max(1, s // 2))
    # the pockets: four, every one bulging, notes' edges over the flaps
    def pocket(x0, y0, w, h, n):
        d.rounded_rectangle([x0 - s // 2, y0 - s // 2, x0 + w + s // 2, y0 + h], radius=s, fill=COAT_L, outline=OL)
        d.rectangle([x0 - s, y0 - s, x0 + w + s, y0 + s // 2], fill=COAT, outline=OL)              # the flap
        for k in range(n):
            nx = x0 + k * (w // max(1, n))
            d.rectangle([nx, y0 - 2 * s - (k % 2) * s, nx + s + s // 2, y0 - s], fill=NOTE_L, outline=NOTE_D)
    pocket(cx - 10 * s, sh + 4 * s, 4 * s, 3 * s, 2)
    pocket(cx + 6 * s, sh + 4 * s, 4 * s, 3 * s, 2)
    pocket(cx - 11 * s, py - 6 * s, 5 * s, 4 * s, 3)
    pocket(cx + 6 * s, py - 6 * s, 5 * s, 4 * s, 3)
    # the belt, black and gold, and the jambiya standing up the middle of him: the horn hilt with two gold studs, the
    # pale sheath going down behind the table
    by = sh + 6 * s
    d.rectangle([cx - 5 * s, by, cx + 5 * s, by + 2 * s], fill=BELT, outline=OL)
    for x in range(cx - 5 * s + s // 2, cx + 5 * s, s):
        d.rectangle([x, by + s // 2, x + s // 2, by + s + s // 4], fill=GOLD)
        d.point((x + s // 4, by + s + s // 2), fill=GOLD_D)
    d.rounded_rectangle([cx - s, sh + 2 * s, cx + s, by + s // 2], radius=s // 2, fill=HORN, outline=OL)     # the hilt
    d.line([(cx - s // 2, sh + 2 * s + s // 2), (cx - s // 2, by - s // 2)], fill=HORN_L)
    for yy in (sh + 3 * s, sh + 5 * s):
        d.ellipse([cx - s // 2, yy - s // 2, cx + s // 2, yy + s // 2], fill=GOLD, outline=GOLD_D)
    d.polygon([(cx - 2 * s, by + 2 * s), (cx + 2 * s, by + 2 * s), (cx + s, py), (cx - s, py)], fill=SHEATH, outline=OL)
    d.line([(cx - s, by + 3 * s), (cx - s // 2, py - s)], fill=SHEATH_D)
    # the far arm up with the loudhailer (viewer's right), the thobe's white cuff at the wrist
    ax = cx + 11 * s
    d.rounded_rectangle([ax - 2 * s, sh - 2 * s + lift, ax + 2 * s, sh + 6 * s], radius=s, fill=COAT, outline=OL)
    d.rectangle([ax - 2 * s, sh - 3 * s + lift, ax + 2 * s, sh - 2 * s + lift], fill=THOBE, outline=OL)
    d.rounded_rectangle([ax - 2 * s, sh - 6 * s + lift, ax + 2 * s, sh - 3 * s + lift], radius=s, fill=SKIN, outline=OL)
    my = sh - 8 * s + lift
    d.rectangle([ax - 3 * s, my, ax, my + 2 * s], fill=RED_D, outline=OL)                           # the loudhailer's grip
    d.polygon([(ax, my - 3 * s), (ax + 9 * s, my - 6 * s), (ax + 9 * s, my + 5 * s), (ax, my + 2 * s)], fill=RED, outline=OL)
    d.polygon([(ax + 9 * s, my - 6 * s), (ax + 10 * s, my - 6 * s), (ax + 10 * s, my + 5 * s), (ax + 9 * s, my + 5 * s)], fill=WHITE_CHK, outline=OL)
    d.line([(ax + 2 * s, my - 2 * s), (ax + 7 * s, my - 4 * s)], fill=(214, 90, 60))
    # the head: the grid at half a unit, with its own outline; in the laugh, back and tilted
    rows = HEAD_LAUGH if laugh else HEAD
    gw, gh = 24 * hu, len(rows) * hu
    tilt = -0.07 if laugh else 0.0
    pad = 4 * hu
    head = Image.new('RGBA', (gw + 2 * pad, gh + 2 * pad), (0, 0, 0, 0))
    grid(head, rows, pad, pad, hu, tilt)
    head = outline(head)
    hx = cx - gw // 2 - pad + (-s if laugh else 0)
    hy = top - s - pad + (-2 * s if laugh else 0)
    d.rectangle([cx - 3 * s + (-s if laugh else 0), top + 11 * s, cx + 3 * s + (-s if laugh else 0), sh], fill=SKIN_D, outline=OL)  # the neck
    d.rounded_rectangle([cx - 4 * s, sh - s, cx + 4 * s, sh + s // 2], radius=s // 2, fill=THOBE, outline=THOBE_D)  # the collar over it
    im.alpha_composite(head, (hx, hy))
    d = ImageDraw.Draw(im)
    # the table, in front of him; then the gavel (left) and the sign-in sheet with one name (right)
    d.rectangle([3 * s, py, W - 3 * s, py + s], fill=WOOD_L)
    d.rectangle([3 * s, py + s, W - 3 * s, H], fill=WOOD)
    d.rectangle([3 * s, py + s, W - 3 * s, py + s + max(1, s // 2)], fill=WOOD_D)
    # the near hand on the stamp, on the table (viewer's left), its chain to the belt
    hx = cx - 16 * s
    d.rectangle([hx - s - s // 2, py - 3 * s, hx + s + s // 2, py], fill=RUBBER)
    d.rectangle([hx - s // 2, py - 7 * s, hx + s // 2, py - 3 * s], fill=WOOD_L, outline=WOOD_D)
    for k in range(7):
        d.point((hx + 2 * s + k * s // 2, py - 5 * s - k * s // 2), fill=GOLD)
    d.line([(cx - 12 * s, sh + 4 * s), (hx, py - 8 * s)], fill=OL, width=4 * s)                   # the near arm's sleeve
    d.line([(cx - 12 * s, sh + 4 * s), (hx, py - 8 * s)], fill=COAT, width=3 * s)
    d.rectangle([hx - 2 * s, py - 10 * s, hx + 2 * s, py - 9 * s], fill=THOBE, outline=OL)          # the cuff
    d.rounded_rectangle([hx - 2 * s, py - 9 * s, hx + 2 * s, py - 6 * s], radius=s, fill=SKIN, outline=OL)
    d.line([(hx - s, py - 7 * s), (hx + s, py - 7 * s)], fill=SKIN_D)
    gx = W - 24 * s
    d.rectangle([gx, py - s, gx + 5 * s, py + s // 2], fill=WOOD_D)                     # the block
    d.rectangle([gx + 5 * s, py - 2 * s, gx + 11 * s, py - s], fill=WOOD_L)               # the handle, lying
    d.rectangle([gx + 10 * s, py - 4 * s, gx + 13 * s, py], fill=WOOD, outline=WOOD_D)    # the head
    sx0 = W - 14 * s
    d.polygon([(sx0, py - s), (sx0 + 9 * s, py - 2 * s), (sx0 + 10 * s, py + s), (sx0 + s, py + 2 * s)], fill=THOBE, outline=THOBE_D)
    d.line([(sx0 + s, py), (sx0 + 4 * s, py - s // 2)], fill=(60, 50, 90), width=max(1, s // 2))   # the one name
    for k in range(1, 4):
        d.line([(sx0 + s, py + k * s // 2 + s // 2), (sx0 + 8 * s, py + k * s // 2)], fill=THOBE_D)
    # the laugh: notes in the air, out of every pocket
    if laugh:
        for k, (nx, ny) in enumerate(((cx - 12 * s, sh - 2 * s), (cx + 9 * s, sh), (cx - 15 * s, py - 10 * s),
                                      (cx + 13 * s, py - 9 * s), (cx - 9 * s, sh - 6 * s), (cx + 6 * s, sh - 3 * s))):
            w, h = 3 * s, 2 * s
            if k % 2:
                w, h = h, w
            d.rectangle([nx, ny, nx + w, ny + h], fill=NOTE, outline=NOTE_D)
            d.rectangle([nx + s // 2, ny + s // 2, nx + w - s // 2, ny + h - s // 2], fill=NOTE_L)
    return im


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    a, b = portrait(4), portrait(4, laugh=True)
    both = Image.new('RGBA', (a.width * 2 + 8, a.height), (24, 22, 20, 255))
    both.alpha_composite(a, (0, 0))
    both.alpha_composite(b, (a.width + 8, 0))
    both.save(os.path.join(OUT, 'committee_portrait.png'))
    portrait(2).save(os.path.join(OUT, 'committee_portrait_s2.png'))
    print('wrote', OUT)
