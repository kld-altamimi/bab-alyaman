"""S6 refined: the newsreader portrait, drawn at a parametric scale so it can be rendered at the billboard's real size
(scale 2 -> 44px head) and at a presentation size (scale 4). Returns RGBA 48s x 32s.
Copied verbatim from game-direction's handover (claude/topics/game-direction-spokesman-mock.md, 24 Oct), the look
Khaled approved; only OUT changed. Game art is drawn from it in spokesman_art.py."""
from PIL import Image, ImageDraw, ImageFont
import random
OUT = "/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/ibb/s1/"
CUR, CUR_D, CUR_L = (26, 90, 126), (18, 66, 96), (38, 110, 148)
RED, RED_D, RED_L = (178, 30, 34), (120, 16, 20), (216, 58, 62)
GOLD, GOLD_D = (228, 186, 74), (170, 126, 40)
CAMO = [(200, 180, 138), (168, 144, 104), (128, 108, 76), (214, 198, 160)]
WOOD, WOOD_D, WOOD_L = (116, 70, 36), (80, 46, 22), (152, 100, 54)
OL = (58, 38, 34)
IRIS, IRIS_L, PUPIL, WHITE, WHITE_D = (88, 54, 34), (128, 84, 50), (20, 14, 12), (246, 242, 236), (204, 194, 184)

def s6(s=4, mouth=1, blink=False, finger=False, hands=True, stubble=True):
    W, H = 48 * s, 32 * s
    im = Image.new("RGBA", (W, H), CUR); d = ImageDraw.Draw(im)
    # curtain folds
    for x in range(0, W, max(2, s + s // 2)):
        d.line([(x, 0), (x, H)], fill=CUR_D if (x // max(1, s)) % 2 else CUR_L)
    # emblem: gold scorpion in a wreath, high and centred
    ex, ey = W // 2 + 9 * s, 2 * s + s // 2
    d.ellipse([ex - 4 * s, ey - s - s // 2, ex + 4 * s, ey + s + s // 2], outline=GOLD, width=max(1, s // 2))
    d.rounded_rectangle([ex - 2 * s, ey - s // 2, ex + s, ey + s // 2], radius=s // 2, fill=GOLD)
    d.polygon([(ex + s, ey), (ex + 3 * s, ey - s - s // 2), (ex + 3 * s + s // 2, ey - s // 2)], fill=GOLD)
    d.rectangle([ex - 3 * s - s // 2, ey - s, ex - 2 * s, ey - s // 2], fill=GOLD)
    d.rectangle([ex - 3 * s - s // 2, ey + s // 2, ex - 2 * s, ey + s], fill=GOLD)
    # flag at the left: red with a yellow band, on a dark pole
    d.rectangle([2 * s, 3 * s, 6 * s, 26 * s], fill=RED); d.rectangle([2 * s, 9 * s, 6 * s, 10 * s + s // 2], fill=GOLD)
    d.rectangle([6 * s, 2 * s, 6 * s + max(1, s // 2), 28 * s], fill=(50, 40, 32))
    cx = 24 * s; top = 4 * s
    skin, skin_d, skin_dd, skin_l = (222, 186, 150), (190, 148, 110), (160, 118, 84), (236, 206, 176)
    # podium
    py = 28 * s
    d.rectangle([cx - 13 * s, py, cx + 13 * s, H], fill=WOOD)
    d.rectangle([cx - 14 * s, py - s, cx + 14 * s, py], fill=WOOD_L)
    d.rectangle([cx - 13 * s, py + s, cx + 13 * s, py + s + max(1, s // 2)], fill=WOOD_D)
    d.rectangle([cx - 10 * s, py + 2 * s, cx + 10 * s, H - s], fill=RED_D)
    d.rectangle([cx - 10 * s, py + 2 * s, cx + 10 * s, py + 2 * s + max(1, s // 2)], fill=GOLD)
    # torso: camo jacket, shoulders wide, arms down to the podium edges
    body = [(cx - 14 * s, py - s), (cx - 10 * s, top + 19 * s), (cx - 4 * s, top + 17 * s), (cx + 4 * s, top + 17 * s),
            (cx + 10 * s, top + 19 * s), (cx + 14 * s, py - s)]
    d.polygon(body, fill=CAMO[0], outline=OL)
    r = random.Random(9)
    for i in range(6 * s):
        px, py2 = r.randrange(cx - 13 * s, cx + 13 * s), r.randrange(top + 18 * s, py - s)
        t = (py2 - (top + 17 * s)) / max(1, (py - s) - (top + 17 * s)); half = 9 * s + t * 5 * s
        if abs(px - cx) < half - s:
            d.rounded_rectangle([px, py2, px + r.randrange(s, 3 * s), py2 + r.randrange(max(1, s // 2), s + 1)], radius=s // 2,
                                fill=CAMO[1 + i % 3])
    # collar, shoulder boards, badge
    d.polygon([(cx - 4 * s, top + 17 * s), (cx, top + 20 * s), (cx + 4 * s, top + 17 * s)], fill=CAMO[3], outline=OL)
    d.rectangle([cx - 11 * s, top + 18 * s + s // 2, cx - 6 * s, top + 19 * s + s // 2], fill=RED, outline=OL)
    d.rectangle([cx + 6 * s, top + 18 * s + s // 2, cx + 11 * s, top + 19 * s + s // 2], fill=RED, outline=OL)
    d.rectangle([cx - 10 * s, top + 18 * s + s // 2 + 1, cx - 9 * s, top + 19 * s + s // 2 - 1], fill=GOLD)
    d.rectangle([cx + 9 * s, top + 18 * s + s // 2 + 1, cx + 10 * s, top + 19 * s + s // 2 - 1], fill=GOLD)
    d.rectangle([cx - 8 * s, top + 21 * s, cx - 5 * s, top + 22 * s], fill=GOLD, outline=OL)
    # hands on the podium edges
    if hands:
        for sx in (-1, 1):
            if sx == -1 and finger:
                continue                      # the left hand is raised instead
            hx = cx + sx * 13 * s
            d.rounded_rectangle([hx - 2 * s, py - 3 * s, hx + 2 * s, py - s // 2], radius=s, fill=skin, outline=OL)
            for k in range(3):
                d.line([(hx - s + k * s, py - 2 * s), (hx - s + k * s, py - s)], fill=skin_d)
    if finger:
        # the left hand raised beside the shoulder: forearm in the sleeve, a fist, the index finger up
        fx = cx - 12 * s
        d.rounded_rectangle([fx - 2 * s, py - 8 * s, fx + 2 * s, py - s], radius=s, fill=CAMO[0], outline=OL)   # sleeve
        d.rounded_rectangle([fx - 2 * s - s // 2, py - 12 * s, fx + 2 * s + s // 2, py - 7 * s], radius=s, fill=skin, outline=OL)  # fist
        d.line([(fx - s, py - 9 * s), (fx + s, py - 9 * s)], fill=skin_d)
        d.rounded_rectangle([fx - s // 2 - (s > 2), py - 17 * s, fx + s // 2 + (s > 2), py - 11 * s], radius=s // 2, fill=skin, outline=OL)  # index
    # neck
    d.rectangle([cx - 3 * s, top + 15 * s, cx + 3 * s, top + 18 * s], fill=skin_d, outline=OL)
    # ears (normal)
    for sx in (-1, 1):
        ex2 = cx + sx * (6 * s)
        d.ellipse([ex2 - s - s // 2, top + 7 * s, ex2 + s + s // 2, top + 10 * s + s // 2], fill=skin, outline=OL)
        d.ellipse([ex2 - s // 2 - (s > 2), top + 8 * s, ex2 + s // 2, top + 9 * s + s // 2], fill=skin_d)
    # head: long face, slight taper to the chin
    d.rounded_rectangle([cx - 5 * s - s // 2, top + 2 * s, cx + 5 * s + s // 2, top + 17 * s], radius=3 * s, fill=skin, outline=OL)
    d.rectangle([cx - 5 * s - s // 2 + 1, top + 5 * s, cx - 4 * s - s // 2, top + 15 * s], fill=skin_d)               # shade left
    d.rectangle([cx + 4 * s + s // 2, top + 5 * s, cx + 5 * s + s // 2 - 1, top + 15 * s], fill=skin_l)               # light right
    d.rectangle([cx - 5 * s, top + 4 * s, cx + 5 * s, top + 5 * s], fill=skin_d)                     # brow shadow
    # heavy stubble (Khaled, 24 Oct): no beard shape, a dense checker over the lower face, darkest along the jaw
    if stubble:
        st = max(1, s // 2)
        for y in range(top + 9 * s + s // 2, top + 17 * s, st):
            depth = (y - (top + 9 * s)) / (8 * s)
            for x in range(cx - 5 * s - s // 2 + 1, cx + 5 * s + s // 2, st):
                if (x // st + y // st) % 2 == 0 or (depth > 0.7 and (x // st) % 3 == 0):
                    col = (84, 62, 54) if depth > 0.45 else (128, 100, 88)
                    d.rectangle([x, y, x + st - 1, y + st - 1], fill=col)
        d.rounded_rectangle([cx - 3 * s, top + 11 * s, cx + 3 * s, top + 12 * s], radius=s // 2, fill=(70, 50, 44))  # moustache, stubble-dark
    # mouth frames: 0 closed, 1 half, 2 open
    my = top + 13 * s
    if mouth == 0:
        d.rectangle([cx - 2 * s, my + s // 2, cx + 2 * s, my + s // 2 + max(1, s // 3)], fill=(110, 48, 50))
    elif mouth == 1:
        d.rounded_rectangle([cx - 2 * s, my, cx + 2 * s, my + s + s // 2], radius=s // 2, fill=(96, 32, 36))
    else:
        d.rounded_rectangle([cx - 2 * s - s // 2, my - s // 2, cx + 2 * s + s // 2, my + 2 * s], radius=s // 2, fill=(84, 26, 30))
        d.rectangle([cx - s - s // 2, my - s // 2 + 1, cx + s + s // 2, my + s // 2], fill=(238, 234, 228))
    # nose: bridge line and the tip's shadow
    d.line([(cx - s // 2, top + 7 * s), (cx - s // 2, top + 10 * s)], fill=skin_d, width=max(1, s // 2))
    d.rectangle([cx - s - s // 2, top + 10 * s, cx + s + s // 2, top + 10 * s + s // 2], fill=skin_d)
    d.point((cx + s, top + 9 * s + s // 2), fill=skin_l)
    # eyes: level, detailed
    for sx in (-1, 1):
        exx = cx + sx * 3 * s; ey2 = top + 7 * s
        if blink:
            d.line([(exx - 2 * s, ey2 + s), (exx + 2 * s, ey2 + s)], fill=OL, width=max(1, s // 2))
        else:
            d.rounded_rectangle([exx - 2 * s, ey2, exx + 2 * s, ey2 + s + s // 2], radius=s // 2, fill=WHITE)
            d.ellipse([exx - s, ey2 - s // 4, exx + s, ey2 + s + s // 2], fill=IRIS)
            d.ellipse([exx - s // 2 - (s > 2), ey2 + s // 3, exx + s // 2, ey2 + s + s // 3], fill=PUPIL)
            d.point((exx - s // 2, ey2 + s // 3), fill=(255, 255, 255))
            d.line([(exx - 2 * s, ey2), (exx + 2 * s, ey2)], fill=OL, width=max(1, s // 2))
            d.line([(exx - 2 * s + 1, ey2 + s + s // 2 + 1), (exx + 2 * s - 1, ey2 + s + s // 2 + 1)], fill=skin_dd)
        d.rectangle([exx - 2 * s - s // 2, ey2 - s - s // 2, exx + 2 * s + s // 2, ey2 - s + s // 4], fill=(48, 32, 28))  # brow
    # beret: red, pulled right, badge left, band
    d.ellipse([cx - 7 * s, top - 2 * s, cx + 9 * s, top + 3 * s], fill=RED, outline=OL)
    d.ellipse([cx - 6 * s, top - s - s // 2, cx + 7 * s, top + s], fill=RED_L)
    d.ellipse([cx - 8 * s, top, cx + 7 * s, top + 4 * s], fill=RED, outline=OL)
    d.rectangle([cx - 7 * s, top + 2 * s + s // 2, cx + 7 * s - s // 2, top + 3 * s + s // 2], fill=RED_D)
    d.rectangle([cx - 5 * s, top + s, cx - 3 * s, top + 3 * s], fill=GOLD, outline=GOLD_D)
    d.rectangle([cx - 4 * s - s // 2, top + s + s // 2, cx - 3 * s - s // 2, top + 2 * s + s // 2], fill=GOLD_D)
    # hair at the temples
    d.rectangle([cx - 5 * s - s // 2 + 1, top + 4 * s, cx - 4 * s, top + 6 * s], fill=(48, 32, 28))
    d.rectangle([cx + 4 * s, top + 4 * s, cx + 5 * s + s // 2 - 1, top + 6 * s], fill=(48, 32, 28))
    # microphone on the podium, right of centre
    d.rectangle([cx + 10 * s, py - 6 * s, cx + 10 * s + max(1, s // 2), py - s], fill=(36, 36, 40))
    d.ellipse([cx + 8 * s + s // 2, py - 9 * s, cx + 12 * s, py - 5 * s], fill=(30, 30, 34), outline=OL)
    # live dot
    d.ellipse([W - 5 * s, 2 * s, W - 3 * s, 4 * s], fill=(236, 40, 40))
    return im
