# export_music.py - all of the game's music as the page plays it (build 0.8.47; it replaces export_menu_music.py,
# export_mocha_music.py, export_souq_music.py and the sound test's copies of the Strait's and the battery's): each loop made a
# whole number of MP3 frames long (core.frame_aligned), with half a second of run-in and run-out round it, encoded at
# LAME's variable rate (core.VBR); the two jingles as they are. Their entries in the game's audio.json follow (a loop's
# length to the microsecond now: the page loops at loopAt + seconds, and four decimals left it up to two samples out).
# Then each file is decoded again and its loop seam measured the way a browser will get it (the bar the exporters always
# used: both sides of the seam alike to 22 dB, at a decoder shift of 0, 26 and 51 ms, and no step bigger than the music's
# own), and nothing may reach full scale.
import json, os, subprocess, wave
import numpy as np
from core import *

AUD = '/home/claude/bab_out/m1/audio/'
GEN = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/gen/'
ROLL, LOOP_AT, LEAD = 0.5, 0.6, 0.5
LOOPS = [('title', 'music_title'), ('map', 'music_map'), ('strait', 'music_strait'), ('battery', 'music_battery'),
         ('mocha', 'music_mocha'), ('roaster', 'music_roaster'), ('souq', 'music_souq'), ('tailor', 'music_tailor')]
JINGLES = [('start', 'jingle_start'), ('complete', 'jingle_complete')]


def loop_file(x):
    r = n_of(ROLL)
    pre = x[-r:] * (np.linspace(0, 1, r)[:, None] ** 2)
    post = x[:r].copy()
    k = n_of(0.1)
    post[-k:] *= np.linspace(1, 0, k)[:, None]
    return np.concatenate([pre, x, post])


def on_grid(x, seed):
    # dithered to 16 bits once, BEFORE the run-in and run-out are copied from it, so the file holds the same samples on both
    # sides of the seam (core.write_wav dithers as it writes: the two copies came out different by the dither, and the
    # encoder, meeting different input, made different choices there). The run-in's fade is off the grid, but the page
    # starts each loop at `lead`, after it, so it is never heard.
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
ok, total = True, 0
for key, name in LOOPS:
    x0 = np.load('out/%s.npy' % name).astype(np.float64)
    x, cents = frame_aligned(x0)
    x = on_grid(x, sum(map(ord, name)))
    L = len(x) / SR
    write_exact('out/tmp/%s.wav' % name, loop_file(x))
    size = to_mp3_vbr('out/tmp/%s.wav' % name, AUD + name + '.mp3', VBR['music'])
    total += size
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
for key, name in JINGLES:
    x = np.load('out/%s.npy' % name).astype(np.float64)
    write_wav('out/tmp/%s.wav' % name, x)
    size = to_mp3_vbr('out/tmp/%s.wav' % name, AUD + name + '.mp3', VBR['jingle'])
    total += size
    y, sr = decode(AUD + name + '.mp3')
    assert abs(man['music'][key]['seconds'] - len(x) / SR) < 1e-3, (key, man['music'][key], len(x) / SR)
    print('%-14s %4.0f KB, %.3f s (%.3f s in audio.json), peak %.1f dB' % (name, size / 1024, len(y) / sr, man['music'][key]['seconds'], db(np.abs(y).max())))
    ok &= np.abs(y).max() < 1.0
json.dump(man, open(GEN + 'audio.json', 'w'), separators=(',', ':'))
print('music in all: %.0f KB' % (total / 1024))
print('audio.json music:', {k: v for k, v in man['music'].items()})
print('ALL SEAMS GOOD' if ok else 'SEAM PROBLEM')
