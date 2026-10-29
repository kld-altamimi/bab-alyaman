# z3_look.py - zone 3 (the terraces) painted, saved, and looked at with Yazeed and some of the Zanabeel in it, Jibla's
# end beside it.   python3 z3_look.py [out.png] [--lines]
import sys, os, time, json
import numpy as np
from PIL import Image
from paint import Layer, from_image
import stage_ibb as I
import stage_ibb_z1 as Z1
import stage_ibb_z2 as Z2
import stage_ibb_z3 as Z3
import look_ibb as LK

OUT = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/ibb/s7/'
LAY = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/ibb/s3/layers/'
os.makedirs(OUT, exist_ok=True)
t0 = time.time()
S = {k: from_image(Image.open(LAY + 'i_%s.png' % k)) for k in ('sky', 'far', 'mid', 'play2', 'back2', 'fore1')}
S['far_y'], S['mid_y'] = 10, 96
I.PLATS.clear()
P3 = Z3.play_z3()
B3 = Z3.back_falls()
F3 = Z3.fore_z3()
P3.image().save(LAY + 'i_play3.png')
B3.image().save(LAY + 'i_back3.png')
print('zone 3 painted in %.1f s' % (time.time() - t0))
S['plays'] = [(Z2.X0, S['play2']), (Z3.X0, P3)]
S['backs'] = [(Z2.BACK_X, S['back2']), (Z3.BACK_X, B3)]
S['fore'] = S['fore1']
g = Z3.ground_world
shots = [
    (2560, [('yazeed_run_side_fwd', 2620, 184), ('rifle_angry_stand', 2860, g(2860), True)]),
    (2706, [('yazeed_stand_side_fwd', 2760, 184), ('rifle_qat_stand', 2900, 129, True), ('rifle_youth_stand', 2850, g(2850), True), ('rifle_worried_stand', 3010, g(3010), True)]),
    (2900, [('yazeed_run_side_fwd', 2990, 152), ('tv', 3420, 126)]),
    (3046, [('yazeed_stand_side_fwd', 3100, 152), ('rifle_angry_stand', 3200, 126, True), ('rifle_qat_stand', 3330, g(3330), True)]),
    (3250, [('yazeed_run_side_fwd', 3300, 136), ('tv', 3420, 126)]),
    (3386, [('yazeed_stand_side_fwd', 3450, 136), ('rifle_youth_stand', 3600, 71, True), ('rifle_angry_stand', 3560, g(3560), True)]),
    (3540, [('yazeed_run_side_fwd', 3640, 120), ('rifle_qat_stand', 3740, 79, True)]),
    (3612, [('yazeed_stand_side_fwd', 3700, 120), ('rifle_worried_stand', 3820, 60, True), ('rifle_angry_stand', 3840, 120, True)]),
]
size = LK.sheet_of(S, shots, OUT + (sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'z3_look.png'))
print(size, sorted(I.PLATS.items()))
