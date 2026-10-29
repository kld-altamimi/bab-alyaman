# world_look.py - Ibb's stage painted as one (stage_ibb_world.py) and looked at, screen by screen, with Yazeed for scale.
#   python3 world_look.py <out.png> <cam> [<cam> ...]     (--cached: reuse the last painting, ibb/s9/world_*.png)
import sys, os, time, json
import numpy as np
from PIL import Image
from paint import Layer, from_image
import stage_ibb as I
import stage_ibb_world as WD
import stage_ibb_z2 as Z2
import stage_ibb_z3 as Z3
import look_ibb as LK

CACHE = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/ibb/s9/'
LAY = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/ibb/s3/layers/'
os.makedirs(CACHE, exist_ok=True)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    out = args[0]
    cams = [int(a) for a in args[1:]]
    if '--cached' in sys.argv:
        P = from_image(Image.open(CACHE + 'world_play.png'))
        B = from_image(Image.open(CACHE + 'world_back.png'))
    else:
        t0 = time.time()
        P = WD.play()
        B = WD.back()
        print('painted in %.1f s, %d wide' % (time.time() - t0, P.w))
        P.image().save(CACHE + 'world_play.png')
        B.image().save(CACHE + 'world_back.png')
        json.dump(dict(plats=I.PLATS, info=I.INFO), open(CACHE + 'world_info.json', 'w'), default=int)
    S = {k: from_image(Image.open(LAY + 'i_%s.png' % k)) for k in ('sky', 'far', 'mid')}
    S['far_y'], S['mid_y'] = 10, 96
    S['plays'] = [(0, P)]
    S['backs'] = [(Z2.BACK_X, B)]
    shots = [(c, [('yazeed_stand_side_fwd', c + 120, I.WALK if c + 120 < Z3.X0 + 132 else Z3.ground_world(c + 120))]) for c in cams]
    print(LK.sheet_of(S, shots, out))


if __name__ == '__main__':
    main()
