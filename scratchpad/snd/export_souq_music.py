# SUPERSEDED (0.8.47): export_music.py now makes every music file (frame-aligned loops, variable rate). Running this would put
# back the old constant-rate file and the old loop length in audio.json.
# export_souq_music.py - The Souq's stage theme and its boss's (the Tailor's: first the Spice Cannon's, then the Great Scale's) as the page plays them: MP3 with half a second of
# run-in and run-out round the loop (as export.py does for the stage music), and their entries in the game's audio.json.
# Then each file is decoded again and its loop seam measured, the way a browser will get it.
import json, os, subprocess, wave
import numpy as np
from core import *

AUD = '/home/claude/bab_out/m1/audio/'
GEN = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/gen/'
ROLL, LOOP_AT, LEAD = 0.5, 0.6, 0.5
TRACKS = [('souq', 'music_souq'), ('tailor', 'music_tailor')]
# (the Coffee Port's stage theme starts its loop on claps and the tray: at 160 kbps the two sides of its seam came out of the encoder
# only 20 dB alike; at 192 they meet the bar the others do)
KBPS = {'souq': 192, 'tailor': 192}


def loop_file(x):
    r = n_of(ROLL)
    pre = x[-r:] * (np.linspace(0, 1, r)[:, None] ** 2)
    post = x[:r].copy()
    k = n_of(0.1)
    post[-k:] *= np.linspace(1, 0, k)[:, None]
    return np.concatenate([pre, x, post])


def decode(path):
    wav = 'out/tmp/dec_check.wav'
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', path, wav], check=True)
    with wave.open(wav) as w:
        n, ch, sr = w.getnframes(), w.getnchannels(), w.getframerate()
        y = np.frombuffer(w.readframes(n), dtype='<i2').astype(np.float64) / 32768.0
    return y.reshape(-1, ch), sr


man = json.load(open(GEN + 'audio.json'))
man['music'].pop('cannon', None)                              # (the Spice Cannon's: the boss has its music now)
man['music'].pop('scale', None)                               # (the Great Scale's theme is the Tailor's now, renamed)
assert abs(man['loopAt'] - LOOP_AT) < 1e-9 and abs(man['lead'] - LEAD) < 1e-9
ok = True
for key, name in TRACKS:
    x = np.load('out/%s.npy' % name).astype(np.float64)
    L = len(x) / SR
    write_wav('out/tmp/%s.wav' % name, loop_file(x))
    size = to_mp3('out/tmp/%s.wav' % name, AUD + name + '.mp3', KBPS.get(key, 160))
    man['music'][key] = dict(file=name, seconds=round(L, 4))
    y, sr = decode(AUD + name + '.mp3')
    line = '%-12s %.0f KB, %.3f s decoded (%.3f expected), peak %.1f dB, %.1f LUFS' % (name, size / 1024, len(y) / sr, L + 2 * ROLL, db(np.abs(y).max()), lufs(y))
    a, b = int(round(LOOP_AT * sr)), int(round((LOOP_AT + L) * sr))
    for shift in (0, int(0.026 * sr), int(0.051 * sr)):
        k, kb = int(0.2 * sr), int(0.09 * sr)
        after = db(rms(y[a + shift:a + shift + k] - y[b + shift:b + shift + k]) / rms(y[a + shift:a + shift + k]))
        before = db(rms(y[a + shift - kb:a + shift] - y[b + shift - kb:b + shift]) / rms(y[a + shift - kb:a + shift]))
        jump = np.abs(y[b + shift - 1] - y[a + shift]).max()
        typical = np.abs(np.diff(y[a + shift - kb:a + shift + k], axis=0)).max()
        line += '\n    decoder shift %2d ms: the seam matches to %.1f dB after and %.1f dB before; step %.4f (ordinary steps up to %.4f)' % (
            shift * 1000 // sr, after, before, jump, typical)
        ok &= after < -22 and before < -22 and jump <= typical
    ok &= np.abs(y).max() < 1.0
    print(line)
json.dump(man, open(GEN + 'audio.json', 'w'), separators=(',', ':'))
print('audio.json music:', {k: v for k, v in man['music'].items()})
print('ALL SEAMS GOOD' if ok else 'SEAM PROBLEM')
