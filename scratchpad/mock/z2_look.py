# z2_look.py - zone 2 (Jibla) painted, saved, and looked at with its screens and some people in it, zone 1 beside it.
#   python3 z2_look.py [--cached]
import sys, os, time, json
import numpy as np
from PIL import Image
from paint import Layer, from_image
import stage_ibb as I
import stage_ibb_z1 as Z1
import stage_ibb_z2 as Z2
import look_ibb as LK

OUT = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/ibb/s3/'
LAY = OUT + 'layers/'
os.makedirs(LAY, exist_ok=True)
t0 = time.time()
S = {k: from_image(Image.open(LAY + 'i_%s.png' % k)) for k in ('sky', 'far', 'mid', 'play1', 'fore1')}
S['far_y'], S['mid_y'] = 10, 96
if '--cached' in sys.argv and os.path.exists(LAY + 'i_play2.png'):
    P2 = from_image(Image.open(LAY + 'i_play2.png'))
    B2 = from_image(Image.open(LAY + 'i_back2.png'))
    info = json.load(open(LAY + 'z2.json'))
else:
    I.PLATS.clear()
    P2 = Z2.play_z2()
    B2 = Z2.back_town()
    P2.image().save(LAY + 'i_play2.png')
    B2.image().save(LAY + 'i_back2.png')
    info = dict(plats=I.PLATS, info=I.INFO.get('z2'))
    json.dump(info, open(LAY + 'z2.json', 'w'), indent=1, default=int)
print('layers in %.1f s' % (time.time() - t0))
S['plays'] = [(0, S['play1']), (Z2.X0, P2)]
S['backs'] = [(Z2.BACK_X, B2)]
S['fore'] = S['fore1']
V = 160
sc = info['info']['school']
shots = [
    (1000, [('tv', 1376, V + 10), ('yazeed_run_side_fwd', 1080, 184)]),
    (1290, [('rifle_angry_stand', 1450, 144 - 1, True), ('rifle_youth_stand', 1530, 145, True), ('rifle_qat_stand', 1640, 184, True), ('yazeed_stand_side_fwd', 1330, 184)]),
    (1560, [('tv', 1800, V + 10), ('tv', 1912, V + 10), ('rifle_angry_stand', 1820, sc['walkway'], True), ('rifle_worried_stand', 1900, 184, True), ('yazeed_run_side_fwd', 1640, 184)]),
    (1820, [('rifle_youth_stand', 2080, 184, True), ('yazeed_stand_side_fwd', 1880, 184)]),
    (2060, [('rifle_qat_stand', 2150, 101, True), ('rifle_angry_stand', 2210, 184, True), ('yazeed_run_side_fwd', 2110, 184)]),
    (2172, [('tv', 2420, V + 10), ('rifle_worried_stand', 2560, 184, True), ('yazeed_stand_side_fwd', 2300, 184)]),
]
print(LK.sheet_of(S, shots, OUT + 'z2_look.png'))
print(sorted(info['plats'].items())[:40])
