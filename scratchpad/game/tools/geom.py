# geom.py - measure the stage as painted: where feet land, where the tops of things are.
import sys, json
sys.path.insert(0, '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock')
import numpy as np
import stage

rec = []
_put = stage.put


def put(play, piece, x, base_y, floor, shadow=True, bury=0, seed=1, reach=0.5):
    y = int(base_y - floor)
    a = np.asarray(piece.a)
    cols = np.where(a.any(axis=0))[0]
    top = np.full(a.shape[1], -1)
    for c in cols:
        top[c] = int(np.argmax(a[:, c]))
    rec.append(dict(x=int(x), y=y, w=int(piece.w), h=int(piece.h), base_y=base_y, floor=int(floor), bury=bury, top=top))
    return _put(play, piece, x, base_y, floor, shadow=shadow, bury=bury, seed=seed, reach=reach)


stage.put = put
S = stage.build_layers()
info = S['info']
walk = info['walk']
dx0, dx1, deck = info['deck']
print('stage %d x %d; walk min %.1f max %.1f mean %.1f' % (stage.STAGE_W, stage.SH, walk.min(), walk.max(), walk.mean()))
print('walk every 117 px:', ' '.join('%d:%.0f' % (x, walk[x]) for x in range(0, 1872, 117)))
print('wreck: deck x %d..%d, deck y from %.1f to %.1f; len %d; wreck_top %s' % (dx0, dx1, float(np.min(deck)), float(np.max(deck)), len(deck), info['wreck_top']))
print('deck y every 12 px:', ' '.join('%d:%.0f' % (668 + i, deck[i]) for i in range(0, len(deck), 12)))
for r in sorted(rec, key=lambda r: r['x']):
    t = r['top']
    cols = np.where(t >= 0)[0]
    prof = ' '.join('%d:%d' % (r['x'] + c, r['y'] + t[c]) for c in cols[::max(1, len(cols) // 8)])
    print('piece x=%4d y=%4d w=%3d h=%3d base=%s floor=%d bury=%s | top: %s' % (r['x'], r['y'], r['w'], r['h'], r['base_y'], r['floor'], r['bury'], prof))
np.save('/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/tools/walk.npy', walk)
