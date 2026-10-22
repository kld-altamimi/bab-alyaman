# check_audio.py - decode every MP3 the page will play and measure it the way a browser will get it.
import json, subprocess, sys, wave, os
import numpy as np
from core import *

SITE = '/home/claude/bab_out/sound/'
man = json.load(open(SITE + 'manifest.json'))


def decode(name):
    wav = 'out/tmp/dec_' + name + '.wav'
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', SITE + 'audio/' + name + '.mp3', wav], check=True)
    with wave.open(wav) as w:
        n, ch, sr = w.getnframes(), w.getnchannels(), w.getframerate()
        x = np.frombuffer(w.readframes(n), dtype='<i2').astype(np.float64) / 32768.0
    return x.reshape(-1, ch), sr


ok = True
print('-- music')
for m in man['music']:
    x, sr = decode(m['id'])
    L = m['seconds']
    exp = L + (1.0 if m['loop'] else 0.0)
    line = '%-16s %d Hz %d ch  %.3f s (expected %.3f)  peak %.1f dB  %.1f LUFS' % (m['id'], sr, x.shape[1], len(x) / sr, exp, db(np.abs(x).max()), lufs(x))
    if m['loop']:
        a, b = int(round(man['loopAt'] * sr)), int(round((man['loopAt'] + L) * sr))
        for shift in (0, int(0.026 * sr), int(0.051 * sr)):      # whatever the decoder does with the encoder's padding
            k, kb = int(0.2 * sr), int(0.09 * sr)
            # what follows the loop start against what follows the loop end, and the same for what comes before:
            # if these match, the jump back cannot be heard
            after = db(rms(x[a + shift:a + shift + k] - x[b + shift:b + shift + k]) / rms(x[a + shift:a + shift + k]))
            before = db(rms(x[a + shift - kb:a + shift] - x[b + shift - kb:b + shift]) / rms(x[a + shift - kb:a + shift]))
            jump = np.abs(x[b + shift - 1] - x[a + shift]).max()
            typical = np.abs(np.diff(x[a + shift - kb:a + shift + k], axis=0)).max()
            line += '\n      decoder shift %2d ms: the two sides of the seam match to %.1f dB after and %.1f dB before; step at the splice %.4f (largest ordinary step nearby %.4f)' % (
                shift * 1000 // sr, after, before, jump, typical)
            ok &= after < -22 and before < -22 and jump <= typical
    ok &= abs(len(x) / sr - exp) < 0.06 and np.abs(x).max() < 1.0
    print(line)

print('-- run-through')
stems = {}
for name in ('run_music', 'run_sfx', 'run_voice'):
    x, sr = decode(name)
    stems[name] = x
    print('%-16s %d ch  %.3f s  peak %.1f dB  %.1f LUFS' % (name, x.shape[1], len(x) / sr, db(np.abs(x).max()), lufs(x)))
n = min(len(v) for v in stems.values())
mix = stems['run_music'][:n] + stems['run_sfx'][:n] + stems['run_voice'][:n]       # mono voice lands in both channels
orig = np.load('out/run_mix.npy')
print('summed in the browser: peak %.2f dB, %.1f LUFS (before encoding: peak %.2f dB, %.1f LUFS); samples over full scale: %d' % (
    db(np.abs(mix).max()), lufs(mix), db(np.abs(orig).max()), lufs(orig), int((np.abs(mix) >= 1.0).sum())))
ok &= np.abs(mix).max() < 1.0 and abs(n / 44100 - man['run']['seconds']) < 0.06

NOISY = {'hit_sand', 'fuse', 'sea', 'steps', 'rocket', 'grenade_throw', 'missile_launch', 'tick', 'hit_body', 'jump', 'land', 'rope_cut'}
print('-- sprites')
for name, clips in (('sfx', [i for g in man['sfx'] for i in g['items']]), ('voices', [l for c in man['voices'] for l in c['lines']])):
    x, sr = decode(name)
    x = x[:, 0]
    first = int(np.argmax(np.abs(x) > 0.15))
    shift = first / sr - man['mark']
    src = dict(np.load('out/' + ('sfx' if name == 'sfx' else 'voice') + '.npz'))
    worst = (2.0, '')
    silent = []
    notes = []
    for c in clips:
        a = int(round((c['at'][0] + shift) * sr))
        m = int(c['at'][1] * sr)
        y = src[c['id']]
        y = y.mean(axis=1) if y.ndim == 2 else y
        m = min(m, len(y))
        # line the decoded clip up with what went in, allowing a millisecond or two either way
        best = -1.0
        for lag in range(-60, 61):
            seg = x[a + lag:a + lag + m]
            if len(seg) < m:
                continue
            best = max(best, float(np.dot(seg, y[:m]) / (np.linalg.norm(seg) * np.linalg.norm(y[:m]) + 1e-12)))
        if best < worst[0]:
            worst = (best, c['id'])
        seg = x[a:a + m]
        if rms(seg) < 1e-4:
            silent.append(c['id'])
        # the gap before each clip must be quiet, so a slightly early start plays nothing
        pre = x[max(0, a - int(0.06 * sr)):a - int(0.008 * sr)]
        loud = db(rms(seg) / rms(y[:m]))
        quiet_gap = (np.abs(pre).max() if len(pre) else 0) < 0.02
        # noise has no waveform worth matching: for hiss and sand the test is that it is as loud and as long as it was
        if best < 0.9:
            notes.append('%s: waveform match %.2f, level %+.1f dB' % (c['id'], best, loud))
        good = quiet_gap and abs(loud) < 1.5 and (best > 0.9 or c['id'] in NOISY)
        if not good:
            notes.append('FAIL %s: gap quiet %s (%.3f), level %+.1f dB, match %.2f' % (c['id'], quiet_gap, np.abs(pre).max() if len(pre) else 0, loud, best))
        ok &= good
    for nt in notes:
        print('      ' + nt)
    print('%-8s %.2f s, %d clips, marker found at %.4f s (shift %.1f ms), worst match %.3f (%s), silent: %s' % (name, len(x) / sr, len(clips), first / sr, shift * 1000, worst[0], worst[1], silent or 'none'))
print('ALL GOOD' if ok else 'PROBLEMS')
