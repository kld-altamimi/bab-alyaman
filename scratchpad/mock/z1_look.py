# z1_look.py - zone 1 (Wadi al-Sahul) painted, saved, and looked at with its screens and some people in it.
#   python3 z1_look.py [--cached]
import sys, os, time
import numpy as np
from PIL import Image
from paint import Layer, from_image
import stage_ibb as I
import stage_ibb_z1 as Z
import look_ibb as LK

OUT = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/ibb/s3/'
LAY = OUT + 'layers/'
os.makedirs(LAY, exist_ok=True)

t0 = time.time()
if '--cached' in sys.argv and os.path.exists(LAY + 'i_play1.png'):
    S = {k: from_image(Image.open(LAY + 'i_%s.png' % k)) for k in ('sky', 'far', 'mid', 'play1', 'fore1')}
    S['far_y'], S['mid_y'] = 10, 96
else:
    B = I.backgrounds()
    S = dict(sky=B['sky'], far=B['far'], mid=B['mid'], far_y=B['far_y'], mid_y=B['mid_y'], play1=Z.play_z1(), fore1=Z.fore_z1())
    for k in ('sky', 'far', 'mid', 'play1', 'fore1'):
        S[k].image().save(LAY + 'i_%s.png' % k)
    import json
    json.dump(dict(plats=I.PLATS, info=I.INFO), open(LAY + 'z1.json', 'w'), indent=1, default=int)
S['play'], S['fore'] = S['play1'], S['fore1']
print('layers in %.1f s' % (time.time() - t0))

V = Z.VERGE
shots = [
    (0, [('board', 120, V + 4), ('yazeed_stand_side_fwd', 168, 184)]),
    (300, [('tv', 548, V + 10), ('rifle_angry_stand', 474, 162, True), ('rifle_youth_stand', 512, 184, True),
           ('yazeed_run_side_fwd', 388, 184)]),
    (560, [('rifle_qat_stand', 652, 84, True), ('rifle_worried_stand', 732, 125, True), ('cmdr_stand', 790, 184, True),
           ('yazeed_stand_side_fwd', 604, 184)]),
    (812, [('tv', 866, V + 10), ('rifle_angry_stand', 930, 139, True), ('rifle_youth_stand', 1000, 184, True),
           ('yazeed_run_side_fwd', 850, 184)]),
    (1000, [('rifle_qat_stand', 1150, 125, True), ('yazeed_stand_side_fwd', 1060, 184)]),
    (196, [('yazeed_stand_side_fwd', 260, 184), ('rifle_youth_stand', 430, 184, True)]),
]
print(LK.sheet_of(S, shots, OUT + 'z1_look.png'))
