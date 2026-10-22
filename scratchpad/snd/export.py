# export.py - everything the sound test page plays, as MP3, plus one manifest that says what is where.
import json, os, shutil, subprocess, sys
import numpy as np
from core import *
import sfx
import voice as V

OUT = 'out/'
SITE = '/home/claude/bab_out/sound/'
AUD = SITE + 'audio/'
TMP = OUT + 'tmp/'
os.makedirs(AUD, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

ROLL = 0.5        # lead-in and run-out on a loop file, so the loop points sit clear of the encoder's padding
LOOP_AT = 0.6     # where the page loops from; the loop ends one loop length later
MARK = 0.05       # a click at this time in each sprite tells the page how much the decoder shifted things
GAP = 0.12


def mp3(name, x, kbps):
    wav = TMP + name + '.wav'
    write_wav(wav, x)
    size = to_mp3(wav, AUD + name + '.mp3', kbps)
    return size


def loop_file(x):
    r = n_of(ROLL)
    pre = x[-r:] * (np.linspace(0, 1, r)[:, None] ** 2)
    post = x[:r].copy()
    k = n_of(0.1)
    post[-k:] *= np.linspace(1, 0, k)[:, None]
    return np.concatenate([pre, x, post])


def marker():
    n = n_of(0.0012)
    t = np.arange(n) / SR
    return np.sin(TAU * 4000 * t) * np.hanning(n) * 0.6


def sprite(clips):
    """clips: list of (name, mono sound). Returns the strip and {name: [start, length]}."""
    parts = [np.zeros(n_of(MARK)), marker(), np.zeros(n_of(0.15))]
    at = {}
    pos = sum(len(p) for p in parts)
    for name, y in clips:
        y = np.asarray(y)
        if y.ndim == 2:
            y = y.mean(axis=1)
        y = fade(y.copy(), 0.0001, 0.004)      # the clips have their own edges; a gunshot's first millisecond is the crack
        at[name] = [round(pos / SR, 4), round(len(y) / SR, 4)]
        parts += [y, np.zeros(n_of(GAP))]
        pos += len(y) + n_of(GAP)
    return np.concatenate(parts), at


man = dict(loopAt=LOOP_AT, mark=MARK, files={})
sizes = {}

# ---- music
MUSIC = [
    ('music_strait', 'Stage theme: The Strait', True,
     "The band comes ashore. The mizmar's twin pipes carry the tune over kettledrums, with a march snare and a low riff from the arcade.",
     [[0, 'The tune'], [8, 'The band answers'], [16, 'Flute bridge'], [20, 'The climb'], [24, 'Everything']]),
    ('music_battery', 'Boss theme: Shore Battery', True,
     "The same five notes read from their dark end. The alarm's two notes, a semitone apart, are in the tune.",
     [[0, 'Riff and tune'], [4, 'Again'], [8, 'Drums and alarm'], [12, 'An octave up']]),
    ('jingle_start', 'Mission start', False, 'Drummers on this coast used to board dhows nearing harbour and drum them ashore. Two bars of drums do that for the skiff, and the band lands on the downbeat.', []),
    ('jingle_complete', 'Mission complete', False, 'The same notes read from their bright end. Three bars and out.', []),
]
info = json.load(open(OUT + 'music.json'))
man['music'] = []
for name, title, loop, note, sections in MUSIC:
    x = np.load(OUT + name + '.npy')
    L = len(x) / SR
    sizes[name] = mp3(name, loop_file(x) if loop else x, 160)
    bar = 60.0 / info[name]['bpm'] * 4
    man['music'].append(dict(id=name, title=title, loop=loop, seconds=round(L, 4), note=note, bpm=info[name]['bpm'], bars=info[name]['bars'],
                             sections=[[round(b * bar, 3), lab] for b, lab in sections], lufs=info[name]['lufs']))

# ---- the run-through
run = json.load(open(OUT + 'run.json'))
sizes['run_music'] = mp3('run_music', np.load(OUT + 'run_music.npy'), 128)
sizes['run_sfx'] = mp3('run_sfx', np.load(OUT + 'run_sfx.npy'), 192)      # gunshots want the bits
sizes['run_voice'] = mp3('run_voice', np.load(OUT + 'run_voice.npy'), 64)
man['run'] = run

# ---- effects
SF = dict(np.load(OUT + 'sfx.npz'))
strip, at = sprite([(k, SF[k]) for k in sfx.EFFECTS])
sizes['sfx'] = mp3('sfx', strip, 160)
groups = []
for k, (label, group, fn, pk) in sfx.EFFECTS.items():
    if not groups or groups[-1]['name'] != group:
        groups.append(dict(name=group, items=[]))
    # on the board the quiet ones come up a little, so a footstep can be heard on its own
    lift = float(np.clip(-9.0 - pk, 0.0, 8.0))
    groups[-1]['items'].append(dict(id=k, label=label, at=at[k], gain=round(10 ** (lift / 20), 3), loop=(k == 'sea')))
man['sfx'] = groups

# ---- voices
VO = dict(np.load(OUT + 'voice.npz'))
order = list(V.LINES) + list(V.VOCALS)
strip, at = sprite([(k, VO[k]) for k in order])
sizes['voices'] = mp3('voices', strip, 80)


def readable(text):
    """The nonsense as a reader would write it."""
    out = []
    for tok in text.replace('-', '').split():
        if tok in ('.', ',', '!', '?'):
            if out:
                out[-1] += tok
            continue
        tok = tok.replace('*', '')
        for a, b in (('c', 'sh'), ('x', 'kh'), ('7', 'h'), ('3', "'"), ('q', 'q')):
            tok = tok.replace(a, b)
        # long held vowels read better short
        for v in 'aiueo':
            while v * 4 in tok:
                tok = tok.replace(v * 4, v * 3)
        out.append(tok)
    s = ' '.join(out).replace('!.', '!').replace('?.', '?')
    res, cap = [], True
    for ch in s:
        res.append(ch.upper() if cap and ch.isalpha() else ch)
        if ch.isalpha():
            cap = False
        elif ch in '.!?':
            cap = True
    return ''.join(res)


STAGE = {'yazeed', 'announcer', 'dispatcher', 'grunt', 'cook', 'elder', 'guard', 'commander'}
cast = []
for sp in ('yazeed', 'announcer', 'dispatcher', 'grunt', 'cook', 'guard', 'commander', 'elder', 'salem', 'bilqis', 'arwa'):
    name, origin, delivery = V.WHO[sp]
    lines = []
    for k in order:
        inf = V.LINES.get(k) or V.VOCALS.get(k)
        if inf[0] != sp:
            continue
        said = readable(inf[3]) if k in V.LINES else ''
        lines.append(dict(id=k, text=inf[2], said=said, at=at[k]))
    cast.append(dict(id=sp, name=name, origin=origin, delivery=delivery, here=sp in STAGE, lines=lines))
man['voices'] = cast

json.dump(man, open(SITE + 'manifest.json', 'w'), indent=1)
shutil.copy('../mock/out/strip.png', SITE + 'strip.png')
tot = 0
for k, v in sizes.items():
    print('%-16s %7.1f KB' % (k + '.mp3', v / 1024))
    tot += v
print('audio total %.2f MB; strip %.0f KB; manifest %.1f KB' % (tot / 1e6, os.path.getsize(SITE + 'strip.png') / 1024, os.path.getsize(SITE + 'manifest.json') / 1024))
for c in cast:
    for l in c['lines']:
        if l['said']:
            print('  %-11s %-44s %s' % (c['id'], l['text'], l['said']))
