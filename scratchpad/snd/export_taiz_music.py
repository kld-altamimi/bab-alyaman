# export_taiz_music.py - Taiz's two loops as the page plays them, made exactly as export_music.py makes the others (a whole
# number of MP3 frames, put on the 16-bit grid once, half a second of run-in and run-out, LAME's variable rate), their
# entries in the game's audio.json, and the same seam check on the decoded file. (export_music.py would re-encode every
# loop; this touches only Taiz's.)
import json, subprocess, wave
import numpy as np
from core import *

AUD = '/home/claude/bab_out/m1/audio/'
GEN = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/gen/'
ROLL, LOOP_AT, LEAD = 0.5, 0.6, 0.5
LOOPS = [('taiz', 'music_taiz'), ('taizboss', 'music_taizboss')]


def loop_file(x):
    r = n_of(ROLL)
    pre = x[-r:] * (np.linspace(0, 1, r)[:, None] ** 2)
    post = x[:r].copy()
    k = n_of(0.1)
    post[-k:] *= np.linspace(1, 0, k)[:, None]
    return np.concatenate([pre, x, post])


def on_grid(x, seed):
    r = np.random.default_rng(seed)
    d = r.uniform(-0.5, 0.5, x.shape) + r.uniform(-0.5, 0.5, x.shape)
    return np.round(np.clip(x, -1.0, 1.0) * 32767.0 + d).clip(-32768, 32767) / 32767.0


def write_exact(path, x):
    pcm = np.round(np.clip(x, -1.0, 1.0) * 32767.0).clip(-32768, 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(x.shape[1])
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def decode(path):
    wav = 'out/tmp/dec_check.wav'
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', path, wav], check=True)
    with wave.open(wav) as w:
        n, ch, sr = w.getnframes(), w.getnchannels(), w.getframerate()
        y = np.frombuffer(w.readframes(n), dtype='<i2').astype(np.float64) / 32768.0
    return y.reshape(-1, ch), sr


man = json.load(open(GEN + 'audio.json'))
assert abs(man['loopAt'] - LOOP_AT) < 1e-9 and abs(man['lead'] - LEAD) < 1e-9
ok = True
for key, name in LOOPS:
    x0 = np.load('out/%s.npy' % name).astype(np.float64)
    x, cents = frame_aligned(x0)
    x = on_grid(x, sum(map(ord, name)))
    L = len(x) / SR
    write_exact('out/tmp/%s.wav' % name, loop_file(x))
    size = to_mp3_vbr('out/tmp/%s.wav' % name, AUD + name + '.mp3', VBR['music'])
    man['music'][key] = dict(file=name, seconds=round(L, 6))
    y, sr = decode(AUD + name + '.mp3')
    line = '%-14s %4.0f KB, loop %.6f s (%d frames; was %.4f s, pitch %+.2f cents), %.3f s decoded (%.3f expected), peak %.1f dB' % (
        name, size / 1024, L, len(x) // MP3_FRAME, len(x0) / SR, cents, len(y) / sr, L + 2 * ROLL, db(np.abs(y).max()))
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
