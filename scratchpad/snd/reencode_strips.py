# reencode_strips.py - the effects and voices strips encoded again at the lower rate (build 0.8.47), from the strips
# add_sfx.py and add_voices.py last wrote (out/tmp/game_sfx.wav, game_voices.wav: checked to be what the shipped files were
# made from), so nothing in them moves. Then checked the way the page will use them: the click the page finds the decoder's
# shift by is still found (first sample over 0.15 in the first 0.3 s) where it was, and every clip in audio.json, read at
# its place plus that shift, is still the clip (correlation with the source).
import json, os, subprocess, wave
import numpy as np
from core import *

AUD = '/home/claude/bab_out/m1/audio/'
GEN = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/gen/'
OLD = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/work/audio_0846/'


def read(path):
    with wave.open(path) as w:
        n, ch = w.getnframes(), w.getnchannels()
        y = np.frombuffer(w.readframes(n), dtype='<i2').astype(np.float64) / 32768.0
    return y.reshape(-1, ch)[:, 0]


def decode(path):
    wav = 'out/tmp/dec_check.wav'
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', path, wav], check=True)
    return read(wav)


def mark_shift(d, mark):
    m = min(len(d), int(SR * 0.3))
    for i in range(m):
        if abs(d[i]) > 0.15:
            return i / SR - mark
    return None


man = json.load(open(GEN + 'audio.json'))
ok = True
for name, q, places in (('sfx', VBR['sfx'], {k: v for k, v in man['sfx'].items()}),
                        ('voices', VBR['voices'], {k: v['at'] for k, v in man['voices'].items()})):
    src = read('out/tmp/game_%s.wav' % name)
    old_size = os.path.getsize(OLD + name + '.mp3')
    size = to_mp3_vbr('out/tmp/game_%s.wav' % name, AUD + name + '.mp3', q)
    y, yo = decode(AUD + name + '.mp3'), decode(OLD + name + '.mp3')
    s_src, s_new, s_old = mark_shift(src, man['mark']), mark_shift(y, man['mark']), mark_shift(yo, man['mark'])
    def match(d, s, at, n):
        a0, a1 = int(round((at + s_src) * SR)), int(round((at + s_src + n) * SR))
        b0 = int(round((at + s) * SR))
        u, v = src[a0:a1], d[b0:b0 + (a1 - a0)]
        return float(np.dot(u, v) / np.sqrt(np.dot(u, u) * np.dot(v, v) + 1e-18))
    worst, bad, low = (1.0, ''), [], []
    for k, (at, n) in places.items():
        c, co = match(y, s_new, at, n), match(yo, s_old, at, n)
        if c < worst[0]:
            worst = (c, k)
        # a clip out of place would not match at all; a hiss or a crowd never matches a waveform closely at any rate,
        # so the bar is the old file's own match, less a little
        if c < min(0.95, co - 0.05):
            bad.append('%s %.3f (old %.3f)' % (k, c, co))
        elif c < 0.95:
            low.append('%s %.2f/%.2f' % (k, c, co))
    print('%-6s V%d: %4.0f KB (was %4.0f KB, %.0f%% of it); click found at %+.2f ms (source %+.2f, old file %+.2f); %d clips, worst match %.4f (%s)%s%s' % (
        name, q, size / 1024, old_size / 1024, 100.0 * size / old_size, s_new * 1000, s_src * 1000, s_old * 1000, len(places), worst[0], worst[1],
        ('\n    noise-like, as close as before (new/old): ' + ', '.join(low)) if low else '', ('\n    WORSE THAN BEFORE: ' + ', '.join(bad)) if bad else ''))
    ok &= s_new is not None and abs(s_new - s_old) < 0.0005 and not bad
print('STRIPS GOOD' if ok else 'STRIP PROBLEM')
