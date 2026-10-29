# kids_look.py - the school's children (tools/ibb_kids.py) in the school yard at the game's scale, beside Yazeed and the
# teacher, for judging them against the cast and the background before they go in.
import sys, json
from PIL import Image
from paint import from_image
import stage_ibb as I
import stage_ibb_z2 as Z2
import look_ibb as LK
sys.path.insert(0, '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/tools')
import ibb_kids as K

OUT = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/ibb/s3/'
LAY = OUT + 'layers/'


def stage():
    S = {k: from_image(Image.open(LAY + 'i_%s.png' % k)) for k in ('sky', 'far', 'mid', 'play1', 'fore1')}
    S['far_y'], S['mid_y'] = 10, 96
    S['plays'] = [(0, S['play1']), (Z2.X0, from_image(Image.open(LAY + 'i_play2.png')))]
    S['backs'] = [(Z2.BACK_X, from_image(Image.open(LAY + 'i_back2.png')))]
    S['fore'] = S['fore1']
    return S


def put(im, name, x, feet, flip=False):
    f, ax, ay = K.kid(*name.split(':'))
    if flip:
        f = f.transpose(Image.FLIP_LEFT_RIGHT)
        ax = f.width - 1 - ax
    im.alpha_composite(f, (int(x - ax), int(feet - ay)))


if __name__ == '__main__':
    S = stage()
    cam = 1640
    a = LK.shot(S, cam, [('tv', 1800, 170), ('tv', 1912, 170), ('det_tied', 1856, 184), ('yazeed_stand_side_fwd', 1736, 184)])
    xs = [(1662, 'boy1:run_a'), (1680, 'girl1:run_b'), (1698, 'boy2:run_b'), (1716, 'girl2:run_a'), (1790, 'boy1:run_b'), (1806, 'girl2:run_a')]
    for x, n in xs:
        put(a, n, x - cam, 184, flip=True)
    put(a, 'girl1:wave', 1758 - cam, 184, flip=True)
    crop = a.crop((0, 90, 300, 216)).resize((900, 378), Image.NEAREST)
    crop.save(OUT + 'kids_look.png')
    print(crop.size)
