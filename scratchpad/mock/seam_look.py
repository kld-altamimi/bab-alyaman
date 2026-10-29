# seam_look.py - the zones' joins as the game draws them: the layers composed around each zone boundary, with Yazeed
import sys, json
from PIL import Image
from paint import from_image
import stage_ibb as I
import look_ibb as LK
ART = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/art/out/'
st = json.load(open('/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/gen/stage_ibb.json'))
S = {k: from_image(Image.open(ART + 'i_%s.png' % k)) for k in ('sky', 'far', 'mid')}
S['far_y'], S['mid_y'] = st['layers']['far']['y'], st['layers']['mid']['y']
S['plays'] = [(q['x'], from_image(Image.open(ART + q['img'] + '.png'))) for q in st['layers']['play']['strips']]
S['backs'] = [(q['x'], from_image(Image.open(ART + q['img'] + '.png'))) for q in st['layers']['back']['strips']]
out = sys.argv[1]
seams = [int(a) for a in sys.argv[2:]] or [1280, 2640]
shots = []
for x in seams:
    shots.append((x - 234, [('yazeed_stand_side_fwd', x - 40, I.WALK)]))
    shots.append((x - 120, []))
print(LK.sheet_of(S, shots, out))
