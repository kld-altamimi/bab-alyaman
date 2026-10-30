# mock_pass4.py - Khaled's question (30 Oct 13:56): four podiums, two on the bottom and two on the top: would it work?
# A mock on the painted lookout with the game's own sprites, before anything is built: two scaffold towers with a deck
# 46 px up (a jump reaches 65), a podium on each deck and one at each tower's foot; the four screens hang between the
# towers from a truss, one per podium. Three pictures and the game as it is now (0.16.93) to compare.
#   python3 mock_pass4.py   -> ibb/s13/ibb_four_podiums.png
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock')
import mock_pass as M
from paint import from_image

S, LK, I = M.S, M.LK, M.I
OUT = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/ibb/s13/'
NOW = OUT + 'f2_speak.png'                     # (0.16.93 as the game draws it: the camera's picture, cropped)
FLOOR = M.FLOOR
DECK = FLOOR - 46                              # the towers' decks
TOP = 24                                       # the truss across their tops
TOWERS = (88, 380)                             # tower centres in the picture (the screen held for the fight)
TW = 22                                        # half a tower's width
SCREENS = (146, 206, 262, 322)                 # the four screens on the truss, left to right
# which podium each screen shows: lower-left, upper-left, upper-right, lower-right
POD = {'LL': (TOWERS[0], FLOOR), 'UL': (TOWERS[0], DECK), 'UR': (TOWERS[1], DECK), 'LR': (TOWERS[1], FLOOR)}
ORDER = ('LL', 'UL', 'UR', 'LR')
STEEL, STEEL_L, WOOD, WOOD_D = (40, 42, 48, 255), (92, 96, 104, 255), (138, 106, 58, 255), (88, 66, 36, 255)


def tower(im, cx):
    d = ImageDraw.Draw(im)
    x0, x1 = cx - TW, cx + TW
    for x in (x0, x1):
        d.rectangle([x - 1, TOP, x, FLOOR - 1], fill=STEEL)
        d.line([(x - 1, TOP), (x - 1, FLOOR - 1)], fill=STEEL_L)
        d.rectangle([x - 3, FLOOR - 1, x + 2, FLOOR - 1], fill=STEEL)            # base plates
    for y in (DECK - 26, FLOOR - 24):                                             # ledgers
        d.line([(x0, y), (x1, y)], fill=STEEL)
    d.line([(x0, DECK + 3), (x1, FLOOR - 24)], fill=STEEL)                        # bracing below the deck
    d.line([(x1, DECK + 3), (x0, FLOOR - 24)], fill=STEEL)
    d.rectangle([x0 - 3, DECK, x1 + 3, DECK + 1], fill=WOOD)                     # the deck
    d.rectangle([x0 - 3, DECK + 2, x1 + 3, DECK + 3], fill=WOOD_D)
    for k in range(x0 - 3, x1 + 4, 6):
        d.point((k, DECK + 1), fill=WOOD_D)


def truss(im):
    d = ImageDraw.Draw(im)
    a, b = TOWERS[0] - TW, TOWERS[1] + TW
    d.line([(a, TOP), (b, TOP)], fill=STEEL); d.line([(a, TOP + 5), (b, TOP + 5)], fill=STEEL)
    for x in range(a, b, 8):
        d.line([(x, TOP), (x + 4, TOP + 5)], fill=STEEL); d.line([(x + 4, TOP + 5), (x + 8, TOP)], fill=STEEL)


def screens(im, pics):
    d = ImageDraw.Draw(im)
    for x, pic in zip(SCREENS, pics):
        top = TOP + 9
        d.line([(x - 18, TOP + 5), (x - 18, top)], fill=STEEL); d.line([(x + 18, TOP + 5), (x + 18, top)], fill=STEEL)
        im.alpha_composite(pic, (x - 24, top + 2))
        LK.spr(im, 'ps_box', x - 26, top, ibb=True)


def podiums(im, mics, face):
    pod, nom = S.podium(), M.podium_nomic()
    for k in ORDER:
        x, y = POD[k]
        M.put(im, pod if mics[k] else nom, x, y, flip=face[k] < 0)


def him(im, k, pose, face):
    x, y = POD[k]
    M.put(im, pose, x - 3 * face, y, flip=face < 0)


def dash(im, x0, y0, x1, y1, n=3, col=(255, 236, 140, 255)):
    d = ImageDraw.Draw(im)
    for j in range(n):
        u = (j + 1) / float(n + 1)
        bx, by = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
        ux, uy = (x1 - x0), (y1 - y0)
        L = (ux * ux + uy * uy) ** 0.5
        ux, uy = ux / L, uy / L
        d.line([(bx - 3 * ux, by - 3 * uy), (bx + 2 * ux, by + 2 * uy)], fill=col)


def main():
    S_ = {k: from_image(Image.open(M.ART + 'i_%s.png' % k)) for k in ('sky', 'far', 'mid')}
    S_['far_y'], S_['mid_y'] = 10, 96
    S_['plays'] = [(M.Z4.X0, from_image(Image.open(M.ART + 'i_z4.png')))]
    S_['backs'] = [(M.Z2.BACK_X + M.Z2.BACK_W + 1410, from_image(Image.open(M.ART + 'i_back4.png')))]
    cam = M.CAM_FIGHT
    live = [S.screen('podium', m, False) for m in range(3)]

    def lookout():
        im = M.shot(S_, cam)
        # (the five podiums' poles and the podiums of the painting's lookout are drawn by the game, not painted: the
        # picture is clean)
        for cx in TOWERS:
            tower(im, cx)
        truss(im)
        return im

    # A: him on the upper-left podium, speaking; Yazeed below, the gun pointed up and along at its microphone
    a = lookout()
    screens(a, [live[2]] * 4)
    face = {'LL': 1, 'UL': 1, 'UR': -1, 'LR': -1}
    podiums(a, {k: 1 for k in ORDER}, face)
    him(a, 'UL', S.speech(2, trousers=False), 1)
    podiums(a, {k: 1 for k in ORDER}, face)               # (the podiums over him)
    yx = 138
    LK.spr(a, 'yazeed_stand_side_diag', yx, FLOOR, flip=True)
    dash(a, yx - 14, FLOOR - 32, TOWERS[0] + 8, DECK - 22, 3)
    M.spark(a, TOWERS[0] + 7, DECK - 22, 3)
    LK.spr(a, 'rifle_angry_run', 446, FLOOR, flip=True)

    # B: Yazeed up on the right tower's deck: straight across at the upper-left one; the lower-right one already cut off
    b = lookout()
    screens(b, [live[1], live[1], live[1], M.snow(3)])
    face = {'LL': 1, 'UL': 1, 'UR': -1, 'LR': -1}
    mics = {'LL': 1, 'UL': 1, 'UR': 1, 'LR': 0}
    him(b, 'UL', S.speech(1, trousers=False), 1)
    podiums(b, mics, face)
    LK.spr(b, 'yazeed_stand_side_fwd', TOWERS[1] + 8, DECK, flip=True)
    M.bullets(b, TOWERS[1] - 14, DECK - 19, TOWERS[0] + 12, DECK - 19, 5)
    M.spark(b, TOWERS[0] + 8, DECK - 21, 3)
    M.word(b, TOWERS[0] + 6, DECK - 58, 'WHAT? SPEAK UP!')

    # C: two left: he leaps from the upper-left deck down across to the lower-right one, over Yazeed; the feedback
    c = lookout()
    screens(c, [M.snow(5), live[2], M.snow(7), live[2]])
    mics = {'LL': 0, 'UL': 1, 'UR': 0, 'LR': 1}
    face = {'LL': 1, 'UL': 1, 'UR': -1, 'LR': -1}
    podiums(c, mics, face)
    d3 = ImageDraw.Draw(c)
    for k in range(22):
        u = k / 21.0
        px = TOWERS[0] + (TOWERS[1] - TOWERS[0]) * u
        py = (DECK - 30) * (1 - u) + (FLOOR - 30) * u - 40 * 4 * u * (1 - u)
        if k % 2 == 0:
            d3.point((px, py), fill=(255, 255, 255, 210))
    M.put(c, S.spokesman_jump(flip=False), int(TOWERS[0] + (TOWERS[1] - TOWERS[0]) * 0.62), int(FLOOR - 52))
    LK.spr(c, 'yazeed_jump_side_fwd', 236, FLOOR - 20)
    for xx in range(150, 232):
        yy = FLOOR - 3 - round(3 * np.sin(xx / 2.3)) * (1 if (xx // 9) % 2 else 0.5)
        d3.point((xx, yy), fill=(214, 248, 255, 255)); d3.point((xx, yy + 1), fill=(120, 200, 230, 255))

    # the game now, for comparison
    now = Image.open(NOW).convert('RGBA')
    frames = [
        (now, 'Now (0.16.93): five podiums in a row on the floor, a screen on a pole behind each. Everything happens at one '
              'height: you shoot straight along the floor all fight.'),
        (a, 'Four: two on the floor, two up on scaffold towers (their decks 46 px up; a jump reaches 65). The four screens '
            'hang between the towers from a truss, one for each podium. Up top, his microphone is shot with the gun '
            'pointed up and along...'),
        (b, '...or from the other tower\'s deck, straight across. A cut-off podium\'s screen still goes to snow (here the '
            'lower right).'),
        (c, 'He leaps between them, up, down and across over Yazeed; with two left he shouts and the feedback runs along '
            'the floor (or the deck he is on). At the last one the lights go out as now.'),
    ]
    sc = 2
    W, H = I.SW * sc, I.SH * sc
    cap_h = 62
    sheet = Image.new('RGB', (W * 2 + 12, (H + cap_h + 12) * 2), (24, 20, 28))
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    dr = ImageDraw.Draw(sheet)

    def wrap(text, width):
        words, lines, cur = text.split(' '), [], ''
        for w_ in words:
            t = (cur + ' ' + w_).strip()
            if dr.textlength(t, font=font) > width and cur:
                lines.append(cur); cur = w_
            else:
                cur = t
        lines.append(cur)
        return '\n'.join(lines)

    for i, (im, text) in enumerate(frames):
        x0, y0 = (i % 2) * (W + 12), (i // 2) * (H + cap_h + 12)
        if im.size != (I.SW, I.SH):
            # (the game's picture: the canvas inside the phone's screen, without the side bars)
            g = im.convert('RGB')
            g = g.crop((34, 0, g.width - 34, g.height)).resize((W, H), Image.LANCZOS)
            sheet.paste(g, (x0, y0))
        else:
            sheet.paste(im.convert('RGB').resize((W, H), Image.NEAREST), (x0, y0))
        dr.multiline_text((x0 + 10, y0 + H + 8), wrap(text, W - 24), fill=(236, 230, 214), font=font, spacing=4)
    sheet.save(OUT + 'ibb_four_podiums.png')
    print(sheet.size, 'cam', cam)


if __name__ == '__main__':
    main()
