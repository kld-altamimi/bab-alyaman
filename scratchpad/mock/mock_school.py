# mock_school.py - a storyboard of the school's classrooms (Ibb zone 2), for Khaled to say yes or no to before any of it
# is built (flow note, 24 Oct: a mechanic is shown as a mock before its code). Four pictures at the game's scale, on the
# painted yard, with the game's own Yazeed and teacher and the screens; the children drawn here for the mock.
#   1  the yard is clear: the classroom doors are padlocked, a glint on each lock
#   2  Yazeed at a door: it swings open, the class pours out
#   3  they run for home across the yard; his gun is pointed at the ground while they are in sight (no shot can be fired);
#      one stops in front of him: "Go home. Tell your mother."
#   4  the teacher, freed at his flagpole, waves and goes after his pupils
import json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from paint import Layer, from_image
import stage_ibb as I
import stage_ibb_z2 as Z2
import look_ibb as LK
import sys as _sys
_sys.path.insert(0, '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/tools')
import ibb_kids as K

OUT = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/ibb/s3/'
LAY = OUT + 'layers/'

SKIN = [(122, 78, 52), (150, 100, 68), (178, 126, 90)]
BOY_SHIRT = [(52, 88, 146), (78, 120, 182), (112, 152, 206)]          # the school's blue
GIRL_DRESS = [(26, 76, 52), (40, 104, 72), (62, 134, 96)]             # the girls' green
SCARF = [(200, 200, 196), (232, 232, 228), (250, 250, 248)]
TROUS = [(60, 62, 70), (84, 86, 96)]
HAIR = (30, 22, 18)
SHOE = (24, 20, 18)
BAGS = [[(150, 30, 26), (196, 52, 40)], [(196, 150, 40), (230, 190, 70)], [(40, 110, 160), (70, 150, 200)]]


def kid(girl=False, frame=0, bag=0, wave=False):
    """A child of about 7 at the game's scale (22 px), running to the right (frame 0, 1) or standing (wave)."""
    w, h = 14, 23
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    p = im.load()

    def px(x, y, c):
        if 0 <= x < w and 0 <= y < h:
            p[x, y] = c + (255,)
    # head
    for y in range(1, 8):
        for x in range(4, 10):
            if (x in (4, 9)) and y in (1, 7):
                continue
            px(x, y, SKIN[1] if x < 8 else SKIN[0])
    px(8, 4, (20, 14, 12)); px(8, 3, SKIN[2])                    # an eye, facing right
    if girl:
        for y in range(0, 10):
            for x in range(3, 11):
                inner = 4 < x < 10 and 1 < y < 8
                if not inner and not (x in (3, 10) and y in (0, 9)):
                    px(x, y, SCARF[2] if x < 7 else SCARF[1])
    else:
        for x in range(4, 10):
            px(x, 0, HAIR); px(x, 1, HAIR)
        px(4, 2, HAIR); px(4, 3, HAIR); px(5, 2, HAIR)
    # body
    body = GIRL_DRESS if girl else BOY_SHIRT
    for y in range(8, 16 if not girl else 19):
        for x in range(4, 10):
            px(x, y, body[2] if x < 6 else (body[1] if x < 9 else body[0]))
    # the school bag on the back (left, as they run right)
    bc = BAGS[bag % 3]
    for y in range(9, 15):
        for x in range(1, 4):
            px(x, y, bc[1] if y < 11 else bc[0])
    # arms
    if wave:
        for k in range(5):
            px(10 + k // 2, 9 - k, SKIN[1])                        # the near arm up, waving
        px(3, 12, SKIN[0]); px(3, 13, SKIN[0])
    else:
        sw = 1 if frame == 0 else -1
        for k in range(4):
            px(9 + (k if sw > 0 else 0), 10 + k, SKIN[1])
            px(4 - (k if sw < 0 else 0), 10 + k, SKIN[0])
    # legs
    top = 16 if not girl else 19
    if wave:
        for y in range(top, 22):
            px(5, y, TROUS[1] if not girl else (230, 230, 226)); px(8, y, TROUS[0] if not girl else (210, 210, 206))
        px(5, 22, SHOE); px(6, 22, SHOE); px(8, 22, SHOE); px(9, 22, SHOE)
    else:
        legs = ((3, 10), (6, 8)) if frame == 0 else ((5, 8), (7, 9))
        for (a, b) in (legs,):
            pass
        if frame == 0:
            for k, y in enumerate(range(top, 22)):
                px(6 - k // 2, y, TROUS[1] if not girl else (230, 230, 226))
                px(8 + k // 2, y, TROUS[0] if not girl else (210, 210, 206))
            px(2, 22, SHOE); px(3, 22, SHOE); px(11, 22, SHOE); px(12, 22, SHOE)
        else:
            for y in range(top, 22):
                px(6, y, TROUS[1] if not girl else (230, 230, 226)); px(8, y, TROUS[0] if not girl else (210, 210, 206))
            px(5, 22, SHOE); px(6, 22, SHOE); px(8, 22, SHOE); px(9, 22, SHOE)
    return im


def put_kid(im, x, feet, girl=False, frame=0, bag=0, wave=False, flip=True):
    """One of the school's children as the game draws them (tools/ibb_kids.py; 29 Oct, redrawn in the cast's style),
    running for home (to the left), or stopped and waving."""
    name = ('girl%d' if girl else 'boy%d') % (1 + bag % 2)
    f, ax, ay = K.kid(name, 'wave' if wave else ('run_a', 'run_b')[frame % 2])
    if flip:
        f = f.transpose(Image.FLIP_LEFT_RIGHT)
        ax = f.width - 1 - ax
    im.alpha_composite(f, (int(x - ax), int(feet - ay)))


def door_open(im, x, y_base):
    """A classroom door swung open: the dark of the room behind it."""
    d = ImageDraw.Draw(im)
    d.rectangle((x - 8, y_base - 30, x + 7, y_base - 1), fill=(18, 14, 12, 255))
    d.rectangle((x - 12, y_base - 30, x - 9, y_base - 1), fill=(40, 96, 72, 255))


def glint(im, x, y):
    d = ImageDraw.Draw(im)
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        d.point((x + dx, y + dy), fill=(255, 250, 200, 255))
    d.point((x + 2, y), fill=(255, 230, 120, 255)); d.point((x - 2, y), fill=(255, 230, 120, 255))


def caption(im, text, scale=2):
    """A line under the picture, in plain type: this is a mock, not the game's subtitle bar."""
    return text


def main():
    S = {k: from_image(Image.open(LAY + 'i_%s.png' % k)) for k in ('sky', 'far', 'mid', 'play1', 'fore1')}
    S['far_y'], S['mid_y'] = 10, 96
    P2 = from_image(Image.open(LAY + 'i_play2.png'))
    B2 = from_image(Image.open(LAY + 'i_back2.png'))
    info = json.load(open(LAY + 'z2.json'))['info']['school']
    S['plays'] = [(0, S['play1']), (Z2.X0, P2)]
    S['backs'] = [(Z2.BACK_X, B2)]
    S['fore'] = S['fore1']
    cam = 1640
    doors = info['doors']                                   # world x of the three classroom doors
    base = 170
    frames = []
    # 1: the yard clear; padlocks glinting
    a = LK.shot(S, cam, [('tv', 1800, 170), ('tv', 1912, 170), ('det_tied', 1856, 184), ('yazeed_stand_side_fwd', 1720, 184)])
    for dx in doors:
        glint(a, dx - cam, base - 16)
    frames.append((a, '1  The yard is clear: the classroom doors are padlocked, a glint on each lock.'))
    # 2: Yazeed at the first door; it opens; the class pours out
    b = LK.shot(S, cam, [('tv', 1800, 170), ('tv', 1912, 170), ('det_tied', 1856, 184), ('yazeed_stand_side_fwd', 1736, 184)])
    door_open(b, doors[0] - cam, base)
    for k, (x, g) in enumerate(((1752, False), (1766, True), (1780, False))):
        put_kid(b, x - cam, 184 - (k % 2), girl=g, frame=k % 2, bag=k)
    frames.append((b, '2  He walks up to a door: it swings open and the class pours out.'))
    # 3: they run for home; his gun pointed at the ground; one stops: "Go home. Tell your mother."
    c = LK.shot(S, cam, [('tv', 1800, 170), ('tv', 1912, 170), ('det_tied', 1856, 184)])
    LK.spr(c, 'yazeed_stand_side_fwd', 1736 - cam, 184)
    door_open(c, doors[0] - cam, base)
    for k, (x, g) in enumerate(((1660, False), (1676, True), (1694, False), (1710, True), (1790, False))):
        put_kid(c, x - cam, 184 - (k % 2), girl=g, frame=k % 2, bag=k)
    put_kid(c, 1758 - cam, 184, girl=True, wave=True, bag=1)
    frames.append((c, '3  They run for home. While they are in sight his gun points at the ground and cannot fire;\n'
                      '    nothing can touch them. One stops: YAZEED "Go home. Tell your mother."'))
    # 4: the teacher, freed, waves and goes after his pupils
    d = LK.shot(S, cam, [('tv', 1800, 170), ('tv', 1912, 170), ('yazeed_stand_side_fwd', 1820, 184)])
    door_open(d, doors[0] - cam, base)
    door_open(d, doors[1] - cam, base)
    door_open(d, doors[2] - cam, base)
    LK.spr(d, 'det_walk1', 1700 - cam, 184, flip=True)
    frames.append((d, '4  Every class out, the teacher freed at his flagpole goes after his pupils (the Liberator).'))
    # the sheet: each picture at x2 with its caption under it
    sc = 2
    W, H = I.SW * sc, I.SH * sc
    cap_h = 52
    sheet = Image.new('RGB', (W * 2 + 12, (H + cap_h + 12) * 2), (24, 20, 28))
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)
    except Exception:
        font = ImageFont.load_default()
    dr = ImageDraw.Draw(sheet)
    for i, (im, text) in enumerate(frames):
        x0, y0 = (i % 2) * (W + 12), (i // 2) * (H + cap_h + 12)
        sheet.paste(im.convert('RGB').resize((W, H), Image.NEAREST), (x0, y0))
        dr.multiline_text((x0 + 10, y0 + H + 8), text, fill=(236, 230, 214), font=font, spacing=4)
    sheet.save(OUT + 'ibb_school_mock.png')
    print(sheet.size)


if __name__ == '__main__':
    main()
