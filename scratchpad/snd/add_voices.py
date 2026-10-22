# add_voices.py - put lines written since the last full export into the game's voices.mp3 without touching the rest:
# the strip is laid out again from the cached clips in the order the game already has (so every old clip keeps its
# place to the sample), the new ones go on the end, and gen/audio.json keeps its subtitles and speakers for the old
# ones (they were edited by hand after the export: the Dhanabs, the Uncle) and gains entries for the new.
#   python3 add_voices.py            (17 Oct: the Uncle's four calls, reading A; 18 Oct: the Souq's lines and noises)
#   python3 add_voices.py uncle_spice --drop=pusher_push,...      (19 Oct: the Great Scale's in, the Spice Cannon's out)
#   python3 add_voices.py uncle_spice --drop=wm_behold,...        (19 Oct, later: the Tailor's in, the Great Scale's out)
# Noises (voice.VOCALS: sneezes, panting) are added the same way, with no subtitle. A line named after it is said again
# (in its old place); --drop= takes clips out (everything after the first one dropped moves up, and audio.json with it).
import json, sys
import numpy as np
from core import *
import voice as V

MARK, GAP = 0.05, 0.1                                        # the same layout as export_game.py (copied: it runs on import)


def marker():
    n = n_of(0.0012)
    t = np.arange(n) / SR
    return np.sin(TAU * 4000 * t) * np.hanning(n) * 0.6


def sprite(clips):
    parts = [np.zeros(n_of(MARK)), marker(), np.zeros(n_of(0.15))]
    at = {}
    pos = sum(len(p) for p in parts)
    for name, y in clips:
        y = fade(np.asarray(y, dtype=float).copy(), 0.0001, 0.004)
        at[name] = [round(pos / SR, 4), round(len(y) / SR, 4)]
        parts += [y, np.zeros(n_of(GAP))]
        pos += len(y) + n_of(GAP)
    return np.concatenate(parts), at

GEN = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/gen/'
AUD = '/home/claude/bab_out/m1/audio/'
SPEAKER = {'uncle': 'THE UNCLE', 'announcer': 'ANNOUNCER', 'yazeed': 'YAZEED', 'grunt': 'RIFLEMAN', 'commander': 'COMMANDER', 'shop1': 'SHOPKEEPER',
           'shop2': 'SHOPKEEPER', 'shop3': 'SHOPKEEPER', 'tailor': 'TAILOR'}

au = json.load(open(GEN + 'audio.json'))
vo = au['voices']
VO = dict(np.load('out/voice.npz'))
# (build 18 renamed saif_* to yazeed_* in the game; the cache still had the old names)
for k in list(VO):
    if k.startswith('saif_'):
        VO['yazeed_' + k[5:]] = VO.pop(k)
order = list(vo)
drop = [k for a in sys.argv[1:] if a.startswith('--drop=') for k in a[7:].split(',') if k]
for k in drop:
    assert k in vo and k not in V.LINES and k not in V.VOCALS, k
first_drop = min([order.index(k) for k in drop] or [len(order)])
for k in drop:
    order.remove(k)
    del vo[k]
    VO.pop(k, None)
new = [k for k in list(V.LINES) + list(V.VOCALS) if k not in vo]
redo = [k for k in sys.argv[1:] if k in V.LINES or k in V.VOCALS]     # lines re-voiced: said again, in their old place
for k in new + redo:
    if k in V.LINES:
        sp, fx, sub, text, opt = V.LINES[k]
        VO[k] = V.level(fx(V.CAST[sp].say(text, seed=sum(map(ord, k)) % 997, **opt), seed=5))
    else:                                                    # (a noise: as export_game.py makes them)
        sp, fx, sub, fn = V.VOCALS[k]
        VO[k] = V.level(fx(fn(V.CAST[sp], 7), seed=5), -17.0 if sp != 'guard' else -15.0)
np.savez('out/voice.npz', **VO)
order += new
strip, at = sprite([(k, VO[k]) for k in order])
first = min([order.index(k) for k in redo] + [first_drop, len(order)])
for k in order[:first]:                                      # every old clip before the first one said again stays where it was
    if k in vo:
        assert abs(at[k][0] - vo[k]['at'][0]) < 0.0002 and abs(at[k][1] - vo[k]['at'][1]) < 0.0002, k
write_wav('out/tmp/game_voices.wav', strip)
size = to_mp3_vbr('out/tmp/game_voices.wav', AUD + 'voices.mp3', VBR['voices'])   # (0.8.47: variable rate; was 80 kbps)
for k in order:
    if k in vo:
        vo[k]['at'] = at[k]
        if k in redo and k in V.LINES:
            vo[k]['text'] = V.LINES[k][2]
    elif k in V.LINES:
        sp, fx, sub, text, opt = V.LINES[k]
        vo[k] = dict(at=at[k], who=SPEAKER[sp], text=sub)
    else:
        vo[k] = dict(at=at[k], who=SPEAKER[V.VOCALS[k][0]], text='')
json.dump(au, open(GEN + 'audio.json', 'w'), separators=(',', ':'))
print('voices.mp3: %d clips (new: %s; said again: %s; dropped: %s), %.1f s, %.0f KB' % (len(order), ', '.join(new) or '-', ', '.join(redo) or '-',
      ', '.join(drop) or '-', len(strip) / SR, size / 1024))
