# mock_stage.py - the storyboard of the Spokesman's first appearance, on the terraces' stage (zone 3), drawn on the painted
# zone with the game's own sprites, before any of it is built (as the school's children were: Khaled sees the scene
# first). Four pictures, a caption under each:
#   1  the station's fight; on the stage he goes on with his speech (statement D), his audience in the chairs clapping
#   2  the station cleared, Yazeed walks up: "Nice beret." He stops mid-word.
#   3  the jump: the podium was hiding the rest, no trousers; the audience applauds anyway
#   4  he runs for the pass, the audience still clapping; GO
# The audience are new: Zanabeel in the chairs, unarmed, clapping (two frames), drawn in the cast's style (ms3).
#   python3 mock_stage.py   -> ibb/s7/ibb_stage_mock.png (and the audience at x6: ibb/s7/audience_x6.png)
import sys, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/tools')
from paint import Layer, from_image
import ms3
from ms3 import PARTS, at, compose
import stage_ibb as I
import stage_ibb_z3 as Z3
import look_ibb as LK
import ibb_sprites as S

OUT = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/ibb/s7/'
ART = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/art/out/'
B = ms3.LEAN

# ---------------------------------------------------------------- the audience: seated, facing the stage, clapping
FUTA_SIT = [               # the futa over thighs held level, the knees to the right
    '.fgghhiiiihhg...',
    'fgghhfhiiiihhgg.',
    'fgghhfgghhiiihgg',
    'ffgghfgghhhiihhg',
    '.ffggffgghhhhhg.',
]
SHINS_SIT = [              # from the knee to the floor, the foot on it
    'pqrr..',
    'pqrr..',
    'pqrq..',
    'pqrq..',
    'pqArrq',
    'AAAAAA',
]
CLAP_UP = [                # both hands brought together in front of the chest
    '......qrs.',
    '...bccrrrs',
    '.abccbbqr.',
    'abbccb....',
    'aabbb.....',
]


def seated(look='worried', skin='skin2', clap=0):
    """One of the audience in his chair: (image, ax, ay), the anchor where he sits on the seat, facing right."""
    p = ms3.militia_pal(skin)
    dy = 7                                             # (sat down: the hips 7 px lower than standing)
    L = [at(FUTA_SIT, (4, 21 + dy), p), at(SHINS_SIT, (15, 26 + dy), p),
         at('jacket_l', B.torso, p, 0, dy), at('belt_l', B.belt, p, 0, dy), at('jambiya_s', B.jamb, p, 0, dy)]
    if clap:
        L += [at('sleeve_l', B.sleeve, p, 0, dy), at(CLAP_UP, (8, 10 + dy - 2), p)]
    else:
        L += [at('forearm_l', B.forearm, p, 0, dy), at('sleeve_l', B.sleeve, p, 0, dy)]
    from sprites import lean_head
    lean_head(L, {'qat': 'qat_l'}.get(look, look), p, 0, dy)
    im, fx, fy = compose(L, foot=(6, 26 + dy))
    return im, fx, fy


def put(im, f, x, y, flip=False):
    fr, ax, ay = f
    if flip:
        fr = fr.transpose(Image.FLIP_LEFT_RIGHT)
        ax = fr.width - 1 - ax
    im.alpha_composite(fr, (int(x - ax), int(y - ay)))


def clap_marks(im, x, y):
    """Two little strokes either side of the hands: the clap."""
    d = ImageDraw.Draw(im)
    for dx, dy in ((-4, -2), (4, -2), (-3, 2), (3, 2)):
        d.point((x + dx, y + dy), fill=(255, 250, 220, 255))


def main():
    S_ = {k: from_image(Image.open(ART + 'i_%s.png' % k)) for k in ('sky', 'far', 'mid')}
    S_['far_y'], S_['mid_y'] = 10, 96
    S_['plays'] = [(Z3.X0, from_image(Image.open(ART + 'i_z3.png')))]
    S_['backs'] = [(Z3.BACK_X, from_image(Image.open(ART + 'i_back3.png')))]
    st = json.load(open('/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/gen/stage_ibb.json'))['info']['z3']['stage']
    deck = st['deck']
    pod_x = st['podium']
    cam = Z3.END3 - I.SW
    looks = [('worried', 'skin2'), ('qat', 'skin3'), ('youth', 'skin1'), ('angry', 'skin2'), ('worried', 'skin3'),
             ('youth', 'skin2'), ('angry', 'skin1'), ('qat', 'skin2'), ('worried', 'skin1')]
    base = Z3.gy(1100) - 7 + 3
    seats = []                                          # (every other chair: the back row, then the front row)
    for row in range(2):
        b = base - 5 * (1 - row)
        for i, cx in enumerate(range(1222 + 5 * row, 1288 - 8, 12)):
            if (i + row) % 2 == 0:
                seats.append((Z3.wx(cx) + 3, b - 7))
    spk = S.speech(mouth=2)
    spk_shut = S.speech(mouth=0)
    pod = S.podium()

    def audience(im, clap_on):
        for k, (sx, sy) in enumerate(seats):
            lk, sk = looks[k % len(looks)]
            c = clap_on and (k % 2 == (1 if clap_on == 2 else 0) or clap_on == 3)
            put(im, seated(lk, sk, 1 if c else 0), sx - cam, sy)
            if c:
                clap_marks(im, sx - cam + 9, sy - 15)

    def frame(things, clap_on, him=None):
        im = LK.shot(S_, cam, [])
        audience(im, clap_on)
        if him:
            him(im)
        for t in things:
            LK.spr(im, t[0], t[1] - cam, t[2], flip=t[3] if len(t) > 3 else False)
        return im

    # 1: the fight at the station, the speech going on
    a = frame([('yazeed_stand_side_fwd', 3700, 120), ('rifle_angry_aim', 3768, 79, True), ('rifle_worried_stand', 3826, 120, True)], 1,
              lambda im: put(im, spk, pod_x + 9 - cam, deck, flip=True))
    # 2: cleared; Yazeed at the chairs: "Nice beret." He stops mid-word
    b = frame([('yazeed_stand_side_fwd', 3928, 120)], 0, lambda im: put(im, spk_shut, pod_x + 9 - cam, deck, flip=True))
    # 3: the jump, no trousers; the applause
    def jump(im):
        put(im, pod, pod_x - cam, deck, flip=True)
        put(im, S.spokesman_jump(flip=True), pod_x + 6 - cam, deck - 26)
    c = frame([('yazeed_stand_side_fwd', 3928, 120)], 3, jump)
    # 4: off for the pass; still clapping; GO
    def run(im):
        put(im, pod, pod_x - cam, deck, flip=True)
        put(im, S.spokesman_run(1), Z3.END3 - 6 - cam, 120)
    d = frame([('yazeed_run_side_fwd', 3960, 120)], 2, run)
    dd = ImageDraw.Draw(d)
    frames = [
        (a, '1  The station\'s fight. On the stage he goes on with his speech (statement D: "We announce the launch of\n'
            '    Operation Steadfast Victorious Mighty Wind."), his audience clapping. Shots pass them, as they pass his screens.'),
        (b, '2  The station cleared, Yazeed walks up to the stage. YAZEED: "Nice beret." He stops mid-word.'),
        (c, '3  He jumps. The podium was hiding the rest: no trousers. The audience applauds anyway.'),
        (d, '4  He runs for the pass (zone 4), the audience still clapping, and Yazeed goes after him.'),
    ]
    sc = 2
    W, H = I.SW * sc, I.SH * sc
    cap_h = 52
    sheet = Image.new('RGB', (W * 2 + 12, (H + cap_h + 12) * 2), (24, 20, 28))
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    except Exception:
        font = ImageFont.load_default()
    dr = ImageDraw.Draw(sheet)
    for i, (im, text) in enumerate(frames):
        x0, y0 = (i % 2) * (W + 12), (i // 2) * (H + cap_h + 12)
        sheet.paste(im.convert('RGB').resize((W, H), Image.NEAREST), (x0, y0))
        dr.multiline_text((x0 + 10, y0 + H + 8), text, fill=(236, 230, 214), font=font, spacing=4)
    sheet.save(OUT + 'ibb_stage_mock.png')
    # the audience on their own, at x6
    row = Image.new('RGBA', (8 * 26, 40), (200, 210, 190, 255))
    for k, (lk, sk) in enumerate(looks[:4]):
        for c in (0, 1):
            put(row, seated(lk, sk, c), 8 + (k * 2 + c) * 26, 34)
    row.resize((row.width * 6, row.height * 6), Image.NEAREST).save(OUT + 'audience_x6.png')
    print(sheet.size)


if __name__ == '__main__':
    main()
