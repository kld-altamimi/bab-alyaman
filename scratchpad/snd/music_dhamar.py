# music_dhamar.py - Dhamar, the Wadi (Mission 5): the stage theme, for the test build of zones 1-3 (Khaled, 11 Nov 03:25:
# "let's go with your plan"). The same band as Ibb's and the same five strings (D F G A Bb), read from D, its minor; but
# where Ibb danced in threes, Dhamar marches in twos: the Draft. The high plain at dawn, cold and bright; then the convoy
# on the march, the kettledrum on one, the snare on two and four, the qanbus trotting straight eighths, the lyre on the
# off-beats, the mizmar on a strutting tune that never quite gets anywhere; and every fourth bar the stamp comes down
# (the big kettledrum and a slap on the last beat). The joke of the mission, halfway round: someone asks about the wages
# and the band stops for the laugh (the brass, ha-ha-ha down the strings, three times, then out of breath), a coin rings,
# and the march picks up again as if nothing had happened.
#
# 32 bars at 116 (66 s), a loop:
#   dawn on the plain (2)   the qanbus alone on D and A, the flute calling across the fields, the kettledrum once a bar.
#   the march (8)           the band; the tune (D minor, G minor, B-flat), the stamp every fourth bar.
#   again (8)               a second pipe under it, claps, the brass answering the stamps.
#   the laugh (2)           everything stops: ha-ha-ha down the strings on the brass, three runs, a breath, the coin.
#   the plain (4)           half time, the lyre picked out, the flute.
#   the climb (2)           the drums on every beat, the guitar in.
#   all in (6)              the march's second half with everything, home on D.
import numpy as np
from core import *
from music import Song, J, H, melody, stabs, STRAIT_SENDS
from music_ibb import IBB_LYRE, LOW, fanfare, IBB_LEVELS, IBB_SENDS

DH_LYRE = dict(IBB_LYRE, A=('A3', 'D4', 'A4'))           # (no C sharp on these strings: an open A with the D)


def trot(s, bar, chord, vol=1.0, beats=range(4)):
    """The qanbus trotting straight eighths: the root on the beat, the fifth or the octave between."""
    lo = LOW[chord] if chord in LOW else ('A1', 'E2', 'A2')
    r, f, o = H(lo[0]) * 2, H(lo[1]) * 2, H(lo[2]) * 2
    for b in beats:
        s.hit('qanbus', J.qanbus(r, dur=0.18, vel=1.0 if b % 2 == 0 else 0.8, seed=bar * 8 + b), bar, b * 4, vol, -0.2, human=0.002)
        s.hit('qanbus', J.qanbus(o if b % 2 else f, dur=0.14, vel=0.55, seed=bar * 8 + b + 4), bar, b * 4 + 2, vol, -0.2, human=0.002)


def bassline(s, bar, chord, vol=1.0, chug=False):
    lo = LOW[chord] if chord in LOW else ('A1', 'E2', 'A2')
    r, f, o = (H(x) for x in lo)
    for st, fr, d, v in ((0, r, 0.4, 1.0), (6, r, 0.16, 0.6), (8, f, 0.4, 0.9), (14, o, 0.16, 0.7)):
        s.hit('bass', J.bass(fr, dur=d, vel=v, seed=int(bar * 5 + st)), bar, st, vol)
        if chug:
            s.hit('guitar', J.chug(fr * 2, dur=min(0.3, d), vel=v, seed=int(bar * 5 + st)), bar, st, vol, 0.6)
            s.hit('guitar', J.chug(fr * 2, dur=min(0.3, d), vel=v, seed=int(bar * 5 + st) + 400), bar, st, vol * 0.9, -0.6, human=0.008)


def offbeats(s, bar, chord, vol=1.0):
    fr = [H(c) for c in DH_LYRE[chord]]
    for b in range(4):
        s.hit('lyre', J.strum(fr, dur=0.22, vel=0.8, up=b % 2 == 1, seed=bar * 16 + b), bar, b * 4 + 2, vol, -0.5)


def march(s, bar, kind='A', vol=1.0, stamp=False, claps=False, fill=None):
    """One bar of the march. kind: 'dawn', 'A', 'half', 'build'. stamp: the stamp coming down on the last beat."""
    sd = int(bar * 131)
    if kind == 'dawn':
        s.hit('marfa', J.marfa(seed=sd, vel=0.8), bar, 0, 0.8 * vol)
        s.hit('drums', J.kick(seed=sd), bar, 0, 0.5 * vol)
        for b in range(4):
            s.hit('sahn', J.sahn(seed=sd + b, vel=0.55), bar, b * 4, 0.7 * vol, 0.6, human=0.003)
    elif kind == 'A':
        for st, v in ((0, 1.0), (8, 0.85)):
            s.hit('drums', J.kick(seed=sd + st), bar, st, v * vol)
            s.hit('tabl', J.tabl(kind='dum', seed=sd + st), bar, st, 0.85 * vol, -0.3)
        s.hit('marfa', J.marfa(seed=sd + 1, vel=0.95), bar, 0, 0.9 * vol)
        for b in (1, 3):
            s.hit('drums', J.snare(seed=sd + 20 + b), bar, b * 4, 0.9 * vol)
            s.hit('sahn', J.jingle(seed=sd + b), bar, b * 4, 0.8 * vol, -0.6)
            if claps:
                s.hit('sahn', J.clap(seed=sd + b), bar, b * 4, 1.3 * vol, 0.15)
                s.hit('sahn', J.clap(seed=sd + b + 500), bar, b * 4, 1.0 * vol, -0.3, human=0.01)
        for st in range(0, 16, 2):
            s.hit('sahn', J.sahn(seed=sd + st, vel=0.85 if st % 4 == 0 else 0.45), bar, st, 0.85 * vol, 0.6, human=0.003)
        for b in range(4):
            s.hit('tabl', J.tabl(kind='tak', seed=sd + b * 5), bar, b * 4 + 3, 0.45 * vol, -0.25)
        s.hit('drums', J.snare(seed=sd + 30, ghost=True), bar, 14, 0.45 * vol)
    elif kind == 'half':
        s.hit('marfa', J.marfa(seed=sd, vel=0.9), bar, 0, 0.9 * vol)
        s.hit('drums', J.kick(seed=sd), bar, 0, 0.75 * vol)
        s.hit('drums', J.snare(seed=sd + 3), bar, 8, 0.7 * vol)
        for b in range(4):
            s.hit('sahn', J.sahn(seed=sd + b, vel=0.7), bar, b * 4, vol, 0.6, human=0.003)
    elif kind == 'build':
        for b in range(4):
            s.hit('drums', J.kick(seed=sd + b), bar, b * 4, vol)
            s.hit('marfa', J.marfa(seed=sd + b, vel=0.9), bar, b * 4, 0.85 * vol)
            for k in range(2):
                s.hit('drums', J.snare(seed=sd + 40 + b * 2 + k, ghost=True), bar, b * 4 + k * 2, (0.45 + 0.55 * (b * 2 + k) / 7) * vol)
    if stamp:
        # the stamp: the big kettledrum and a slap together on the last beat, and a hush after it
        s.hit('marfa', J.marfa(seed=sd + 70, vel=1.0), bar, 12, 1.25 * vol)
        s.hit('drums', J.kick(seed=sd + 71), bar, 12, 1.0 * vol)
        s.hit('sahn', J.clap(seed=sd + 72), bar, 12, 1.5 * vol, 0.0)
        s.hit('tabl', J.tabl(kind='dum', seed=sd + 73), bar, 12, 1.0 * vol, -0.3)
    if fill == 'roll':
        for i in range(6):
            s.hit('drums', J.snare(seed=sd + 40 + i, ghost=i < 2), bar, 10 + i, (0.55 + 0.5 * i / 5) * vol)


def band(s, bar, chord, kind='A', vol=1.0, stamp=False, claps=False, chug=False, fill=None):
    march(s, bar, kind, vol, stamp, claps, fill)
    trot(s, bar, chord, vol * 0.9)
    bassline(s, bar, chord, vol, chug)
    offbeats(s, bar, chord, 0.8 * vol)


# ---------------------------------------------------------------- the tunes (beat from the phrase's start, beats, note, grace)
# the march: a strut (a dotted step and a short one), up the strings and back, never quite arriving
TUNE_1 = [(0, 0.75, 'D5', None), (0.75, 0.25, 'D5', None), (1, 0.5, 'F5', None), (1.5, 0.5, 'D5', None), (2, 1, 'A4', None), (3, 1, 'D5', None),
          (4, 0.75, 'G5', None), (4.75, 0.25, 'F5', None), (5, 0.5, 'G5', None), (5.5, 0.5, 'A5', None), (6, 2, 'G5', 'A5'),
          (8, 0.75, 'F5', None), (8.75, 0.25, 'F5', None), (9, 0.5, 'G5', None), (9.5, 0.5, 'F5', None), (10, 1, 'D5', None), (11, 1, 'F5', None),
          (12, 1, 'A5', None), (13, 0.5, 'G5', None), (13.5, 0.5, 'F5', None), (14, 2, 'D5', 'F5')]
TUNE_2 = [(0, 0.75, 'D5', None), (0.75, 0.25, 'D5', None), (1, 0.5, 'F5', None), (1.5, 0.5, 'D5', None), (2, 1, 'A4', None), (3, 1, 'D5', None),
          (4, 0.75, 'Bb5', None), (4.75, 0.25, 'A5', None), (5, 0.5, 'G5', None), (5.5, 0.5, 'Bb5', None), (6, 2, 'D5', 'F5'),
          (8, 0.75, 'F5', None), (8.75, 0.25, 'G5', None), (9, 0.5, 'A5', None), (9.5, 0.5, 'G5', None), (10, 1, 'F5', None), (11, 1, 'A5', None),
          (12, 1, 'G5', None), (13, 0.5, 'F5', None), (13.5, 0.5, 'A4', None), (14, 2, 'D5', 'F5')]
PROG_1 = ('Dm', 'Gm', 'F', 'Dm')
PROG_2 = ('Dm', 'Bb', 'F', 'Dm')
BELOW = {'Bb5': 'F5', 'A5': 'F5', 'G5': 'D5', 'F5': 'D5', 'D5': 'A4', 'A4': 'F4', 'Bb4': 'F4', 'G4': 'D4', 'F4': 'D4'}
DAWN = [(1, 1.5, 'A4', None), (2.5, 0.5, 'D5', None), (3, 1, 'F5', None), (4, 1.5, 'G5', None), (5.5, 0.5, 'F5', None), (6, 1.6, 'D5', None)]
PLAIN = [(0, 1, 'D5', None), (1, 1, 'F5', None), (2, 2, 'Bb5', 'A5'),
         (4, 1, 'G5', None), (5, 1, 'F5', None), (6, 2, 'D5', None),
         (8, 1, 'Bb4', None), (9, 1, 'D5', None), (10, 1, 'F5', None), (11, 1, 'G5', None),
         (12, 1.5, 'F5', None), (13.5, 0.5, 'D5', None), (14, 2, 'A4', 'Bb4')]
CLIMB = [(0, 1, 'D5', None), (1, 1, 'F5', None), (2, 1, 'G5', None), (3, 1, 'Bb5', None), (4, 3, 'F5', 'G5'), (7, 0.5, 'D5', None), (7.5, 0.5, 'F5', None)]


def pipe2(s, bar0, tune, seed, vol=1.0):
    melody(s, 'lead2', bar0, [(b, d, BELOW.get(nm, nm), None) for (b, d, nm, g) in tune], seed=seed, vol=vol, p=0.4)


def laugh_break(s, bar):
    """The band stops for the laugh: ha-ha-ha down the strings on the brass, three runs, each a little higher and more out
    of breath, a gasp, the coin ringing on the stone, a snare pickup back into the march."""
    sd = bar * 233
    runs = [(0, ('A5', 'G5', 'F5', 'D5')), (4, ('Bb5', 'A5', 'G5', 'F5')), (8, ('D5', 'D5', 'A4', 'A4'))]
    for b0, notes in runs:
        for i, nm in enumerate(notes):
            st = b0 + i
            s.hit('fanfare', J.brass(H(nm), dur=0.12, vel=0.95 - 0.1 * i, seed=int(sd + st)), bar, st, 1.0, (-0.2, 0.2)[i % 2])
            s.hit('fanfare', J.brass(H(nm) / 2, dur=0.12, vel=0.7 - 0.1 * i, seed=int(sd + st + 50)), bar, st, 0.8, 0.0)
        s.hit('marfa', J.marfa(seed=sd + b0, vel=0.7), bar, b0, 0.7)
    s.hit('bass', J.bass(H('D2'), dur=0.3, vel=0.8, seed=sd), bar, 0)
    # the gasp: a high held note, falling away
    fanfare(s, bar, 12, ('A4', 'D5'), 0.7, 0.8)
    # the coin
    s.hit('bell', J.bell(H('A6'), dur=0.6, vel=1.0), bar + 1, 2, 0.9, 0.3)
    s.hit('bell', J.bell(H('A6'), dur=0.4, vel=0.6), bar + 1, 3, 0.55, 0.35)
    s.hit('bell', J.bell(H('A6'), dur=0.3, vel=0.4), bar + 1, 3.5, 0.4, 0.4)
    # and back into the march, as if nothing had happened
    for i in range(4):
        s.hit('drums', J.snare(seed=sd + 30 + i), bar + 1, 12 + i, 0.6 + 0.12 * i)
    s.hit('drums', J.kick(seed=sd + 40), bar + 1, 8, 0.7)


def dhamar_theme():
    """The Wadi: 32 bars at 116, marching in twos, D minor."""
    s = Song(116, 32, seed=191)
    # dawn on the plain: the qanbus alone, the flute across the fields
    for i, ch in enumerate(('Dm', 'Dm')):
        march(s, i, 'dawn')
        trot(s, i, ch, 0.75 + 0.1 * i, beats=(0, 2) if i == 0 else range(4))
        s.hit('bass', J.bass(H('D2'), dur=1.8, vel=0.8, seed=i), i, 0, 0.8)
    melody(s, 'flute', 0, DAWN, voice='flute', seed=191, p=0.2)
    # the march
    for i in range(8):
        ch = (PROG_1 + PROG_2)[i]
        band(s, 2 + i, ch, 'A', stamp=i % 4 == 3, fill='roll' if i == 7 else None)
    s.hit('marfa', J.marfa(seed=401, vel=1.0), 2, 0, 1.15)
    melody(s, 'lead', 2, TUNE_1, seed=192)
    melody(s, 'lead', 6, TUNE_2, seed=193)
    # again: the second pipe, claps, the brass answering each stamp
    for i in range(8):
        ch = (PROG_1 + PROG_2)[i]
        band(s, 10 + i, ch, 'A', stamp=i % 4 == 3, claps=True)
    melody(s, 'lead', 10, TUNE_1, seed=194)
    melody(s, 'lead', 14, TUNE_2, seed=195)
    pipe2(s, 10, TUNE_1, 196)
    pipe2(s, 14, TUNE_2, 197)
    stabs(s, 13, [(13, 0.8), (14, 0.9)], ('D4', 'F4', 'A4'), dur=0.2)
    stabs(s, 17, [(13, 0.8), (14, 1.0)], ('D4', 'F4', 'A4'), dur=0.2)
    # the laugh
    laugh_break(s, 18)
    # the plain: half time, the lyre, the flute
    for i, ch in enumerate(('Gm', 'Dm', 'Bb', 'Dm')):
        bar = 20 + i
        march(s, bar, 'half', stamp=i == 3)
        fr = [H(c) for c in DH_LYRE[ch]]
        for k, idx in enumerate((0, 1, 2, 1)):
            s.hit('lyre', J.lyre(fr[idx], dur=0.9, vel=0.75 if k == 0 else 0.55, seed=bar * 8 + k), bar, k * 4, 1.0, -0.5)
        r = H(LOW[ch][0])
        s.hit('bass', J.bass(r, dur=1.0, vel=0.85, seed=bar), bar, 0)
        s.hit('qanbus', J.qanbus(r * 2, dur=0.9, vel=0.9, seed=bar), bar, 0, 1.0, -0.2)
        trot(s, bar, ch, 0.4, beats=(2, 3))
    melody(s, 'flute', 20, PLAIN, voice='flute', seed=198, p=0.15)
    # the climb
    for i, ch in enumerate(('Gm', 'Bb')):
        bar = 24 + i
        march(s, bar, 'build', fill='roll' if i == 1 else None)
        trot(s, bar, ch, 0.9)
        for b in range(4):
            f = H(LOW[ch][0])
            s.hit('bass', J.bass(f, dur=0.3, vel=1.0, seed=bar + b), bar, b * 4)
            s.hit('guitar', J.chug(f * 2, dur=0.3, vel=1.0, seed=bar + b, open_=True), bar, b * 4, 0.9, 0.3)
            s.hit('guitar', J.chug(f * 2, dur=0.3, vel=1.0, seed=bar + b + 400, open_=True), bar, b * 4, 0.75, -0.5)
        stabs(s, bar, [(0, 1.0), (8, 0.9)], DH_LYRE[ch], dur=0.2)
    melody(s, 'lead', 24, CLIMB, seed=199)
    # all in: the march's second half twice over with everything, home on D
    for i in range(6):
        ch = (PROG_2 + PROG_1[:2])[i]
        band(s, 26 + i, ch, 'A', stamp=i in (3, 5), claps=True, chug=True)
    s.hit('marfa', J.marfa(seed=402, vel=1.0), 26, 0, 1.2)
    stabs(s, 26, [(0, 1.0)], ('D4', 'F4', 'A4'), dur=0.45)
    melody(s, 'lead', 26, TUNE_2, seed=200)
    pipe2(s, 26, TUNE_2, 201)
    melody(s, 'lead', 30, TUNE_1[:12], seed=202)
    stabs(s, 31, [(8, 0.9), (12, 1.0)], ('D4', 'F4', 'A4'), dur=0.35)
    return s


DH_LEVELS = dict(IBB_LEVELS)
DH_SENDS = dict(IBB_SENDS)


def check_tunes():
    """Every note a beat or longer is one of the chord's strings or a whole tone off one, never a semitone."""
    pc = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

    def cls(nm):
        return (pc[nm[0]] + (-1 if len(nm) > 2 and nm[1] == 'b' else 0)) % 12
    bad = []
    for name, tune, prog in (('1', TUNE_1, PROG_1), ('2', TUNE_2, PROG_2), ('dawn', DAWN, ('Dm', 'Dm')),
                             ('plain', PLAIN, ('Gm', 'Dm', 'Bb', 'Dm')), ('climb', CLIMB, ('Gm', 'Bb'))):
        for (b, d, nm, g) in tune:
            if d < 0.99:
                continue
            ch = prog[min(len(prog) - 1, int(b // 4))]
            strings = [cls(x) for x in DH_LYRE[ch]]
            dist = min(min((cls(nm) - c) % 12, (c - cls(nm)) % 12) for c in strings)
            if dist == 1:
                bad.append((name, b, nm, ch))
    return bad
