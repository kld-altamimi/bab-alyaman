# music_taiz.py - Taiz by Apache: the stage theme (the night flight) and the bosses' (the Castle Gun and their gunship).
# The band's five strings again (D F G A Bb), read a fourth way: from G (G A Bb D F), a minor that sits lower than the
# Strait's and has its semitone (A to B-flat) one string above the root, where it can nag. Same band as the other
# missions, highland end of it: the qanbus carries the piece.
#
# The stage theme, 32 bars at 144:
#   the night (4 bars)   the qanbus alone in sixteenths, grouped 3-3-2 like a rotor going round, the big kettledrum once a
#                        bar, the tray ticking, a held bass note; a flute calling over the town (the searchlight's song).
#   the tune (8 bars)    the whole band: kick and kettledrum on the 3-3-2, the backbeat, the bass galloping on the rotor's
#                        accents, the lyre off the beat; the mizmar takes a long-note tune over the busy strings.
#   again (8 bars)       a second pipe under it, the small kettledrums, the band answering at the ends of lines.
#   the dark (4 bars)    half time, the lyre picked out, the flute alone.
#   the climb (4 bars)   B-flat, F, D minor, F, the snare filling in, the mizmar climbing to the top string.
#   all in (4 bars)      the tune's answer with everything, the guitar under the qanbus, then the band stops and the night
#                        (the loop's first bar) comes back.
# The bosses' theme, 16 bars at 160: the bass grinding G against the A and B-flat above it, the qanbus still turning in
# sixteenths, a short hard tune on the mizmar; a break for the siren (B-flat and A on the brass, slow, the alarm) and
# the drums; then the tune with the flute an octave above it and the guitar in.
import numpy as np
from core import *
import inst as I
from music import Song, J, H, lyre_strums, lyre_arp, melody, stabs, STRAIT_SENDS

# ---------------------------------------------------------------- the strings from G
TAIZ_LYRE = {'Gm': ('G4', 'Bb4', 'D5'), 'Bb': ('D4', 'F4', 'Bb4'), 'F': ('F4', 'A4', 'F5'), 'Dm': ('D4', 'F4', 'A4')}
# the rotor: sixteen qanbus strokes to the bar, accented 3-3-2 twice (r root, o its octave, f and t the strings above,
# n a neighbour). A stroke's loudness is one of a few, so each stroke is rendered once.
ROTOR = (('r', 1.0), ('r', 0.45), ('o', 0.6), ('r', 0.9), ('r', 0.45), ('f', 0.6), ('r', 0.9), ('t', 0.6),
         ('r', 1.0), ('r', 0.45), ('n', 0.6), ('r', 0.9), ('r', 0.45), ('f', 0.6), ('r', 0.9), ('t', 0.6))
ROTOR_NOTES = {'Gm': dict(r='G2', o='G3', f='D3', t='F3', n='Bb2'),
               'Bb': dict(r='Bb2', o='Bb3', f='F3', t='A3', n='D3'),
               'F': dict(r='F2', o='F3', f='A2', t='D3', n='G2'),
               'Dm': dict(r='D3', o='D4', f='A3', t='F3', n='F3')}
# the bass on the rotor's accents (steps 0 3 6 8 11 14)
GALLOP_AT = (0, 3, 6, 8, 11, 14)
GALLOP = {'Gm': ('G1', 'G1', 'G2', 'G1', 'Bb1', 'D2'),
          'Bb': ('Bb1', 'Bb1', 'Bb2', 'Bb1', 'D2', 'F2'),
          'F': ('F1', 'F1', 'F2', 'F1', 'A1', 'D2'),
          'Dm': ('D2', 'D2', 'D3', 'D2', 'F2', 'A2')}
ROOT = {'Gm': 'G1', 'Bb': 'Bb1', 'F': 'F1', 'Dm': 'D2'}


def rotor(s, bar, chord, vol=1.0, steps=range(16)):
    nt = ROTOR_NOTES[chord]
    for st in steps:
        k, v = ROTOR[st]
        s.hit('qanbus', J.qanbus(H(nt[k]), dur=0.12, vel=v, seed=bar * 16 + st), bar, st, vol, -0.2, human=0.002)


def gallop(s, bar, chord, vol=1.0, chug=False):
    for i, st in enumerate(GALLOP_AT):
        f = H(GALLOP[chord][i])
        v = 1.0 if st in (0, 8) else 0.85
        s.hit('bass', J.bass(f, dur=0.16, vel=v, seed=bar * 6 + i), bar, st, vol)
        if chug:
            s.hit('guitar', J.chug(f * 2, dur=0.14, vel=v, seed=bar * 6 + i), bar, st, vol, 0.6)
            s.hit('guitar', J.chug(f * 2, dur=0.14, vel=v, seed=bar * 6 + i + 400), bar, st, vol * 0.9, -0.6, human=0.008)


def night_groove(s, bar, kind='A', vol=1.0, fill=None):
    """One bar of the drums. kind: 'night' (the kettledrum and the tray), 'A', 'full' (the small kettledrums too),
    'half', 'build'."""
    sd = int(bar * 163)
    if kind == 'night':
        s.hit('marfa', J.marfa(seed=sd, vel=0.85), bar, 0, 0.85 * vol)
        s.hit('drums', J.kick(seed=sd), bar, 0, 0.6 * vol)
        if bar % 2 == 1:
            s.hit('marfa', J.marfa(seed=sd + 1, vel=0.55), bar, 10, 0.55 * vol)
        for st in range(0, 16, 2):
            s.hit('sahn', J.sahn(seed=sd + st, vel=0.8 if st % 4 == 2 else 0.4), bar, st, 0.85 * vol, 0.6, human=0.003)
        if bar % 4 == 3:
            for st in (14, 15):
                s.hit('tabl', J.tabl(kind='tak', seed=sd + st), bar, st, 0.6 * vol, -0.25)
    elif kind in ('A', 'full'):
        # kick and the big kettledrum on the rotor's 3-3-2, the backbeat over it
        for st in ((0, 6, 8, 11) if bar % 2 == 0 else (0, 3, 6, 8, 14)):
            s.hit('drums', J.kick(seed=sd + st), bar, st, (1.0 if st in (0, 8) else 0.8) * vol)
        for st in (4, 12):
            s.hit('drums', J.snare(seed=sd + 20 + st), bar, st, vol)
        for st in ((7, 15) if bar % 2 == 0 else (7, 10, 15)):
            s.hit('drums', J.snare(seed=sd + 40 + st, ghost=True), bar, st, 0.65 * vol)
        s.hit('marfa', J.marfa(seed=sd, vel=1.0), bar, 0, vol)
        s.hit('marfa', J.marfa(seed=sd + 1, vel=0.75), bar, 6, 0.8 * vol)
        if bar % 2 == 1:
            s.hit('marfa', J.marfa(seed=sd + 2, vel=0.6), bar, 11, 0.65 * vol)
        for st in (0, 8):
            s.hit('tabl', J.tabl(kind='dum', seed=sd + st), bar, st, 0.95 * vol, -0.3)
        for st in (3, 6, 11, 14):
            s.hit('tabl', J.tabl(kind='tak', seed=sd + st), bar, st, 0.75 * vol, -0.25)
        for st in range(16):
            s.hit('sahn', J.sahn(seed=sd + st, vel=1.0 if st % 4 == 2 else 0.45), bar, st, 0.9 * vol, 0.6, human=0.003)
        if kind == 'full':
            for st, pc in ((9, 392.0), (10, 349.0), (13, 294.0)):
                s.hit('tunk', J.tunk(seed=sd + 60 + st, pitch=pc, vel=0.75), bar, st, 0.75 * vol, 0.5)
    elif kind == 'half':
        s.hit('marfa', J.marfa(seed=sd, vel=0.9), bar, 0, 0.9 * vol)
        s.hit('marfa', J.marfa(seed=sd + 1, vel=0.55), bar, 10, 0.6 * vol)
        s.hit('drums', J.kick(seed=sd), bar, 0, 0.8 * vol)
        s.hit('drums', J.snare(seed=sd + 3), bar, 8, 0.75 * vol)
        s.hit('tabl', J.tabl(kind='dum', seed=sd + 1), bar, 0, 0.8 * vol, -0.25)
        for st in (6, 11, 14):
            s.hit('tabl', J.tabl(kind='tak', seed=sd + st), bar, st, 0.55 * vol, -0.25)
        for st in range(0, 16, 2):
            s.hit('sahn', J.sahn(seed=sd + st, vel=0.85 if st % 4 == 2 else 0.45), bar, st, vol, 0.6, human=0.003)
    elif kind == 'build':
        for st in (0, 6, 8, 14):
            s.hit('drums', J.kick(seed=sd + st), bar, st, vol)
            s.hit('marfa', J.marfa(seed=sd + st, vel=0.9), bar, st, 0.85 * vol)
        for st in range(16):
            s.hit('drums', J.snare(seed=sd + st, ghost=True), bar, st, (0.45 + 0.6 * st / 16) * vol)
        for st in range(0, 16, 2):
            s.hit('sahn', J.sahn(seed=sd + st, vel=0.8), bar, st, vol, 0.6, human=0.003)
    if fill == 'roll':
        for i, st in enumerate(range(8, 16)):
            s.hit('drums', J.snare(seed=sd + 50 + st, ghost=i < 4), bar, st, (0.7 + 0.5 * i / 7) * vol)
        for i, st in enumerate((10, 11, 13, 14, 15)):
            s.hit('tunk', J.tunk(seed=sd + 80 + st, pitch=(440.0, 392.0, 349.0, 294.0, 220.0)[i]), bar, st, vol, 0.35)
    elif fill == 'call':
        for i, st in enumerate((12, 13, 14, 15)):
            s.hit('tunk', J.tunk(seed=sd + 90 + st, pitch=(294.0, 349.0, 392.0, 440.0)[i]), bar, st, vol, 0.35)


def band_bar(s, bar, chord, kind='A', vol=1.0, fill=None, chug=False, lyre=True):
    night_groove(s, bar, kind, vol, fill)
    rotor(s, bar, chord, vol)
    gallop(s, bar, chord, vol, chug)
    if lyre:
        lyre_strums(s, bar, TAIZ_LYRE[chord], vol=0.85 * vol)


# ---------------------------------------------------------------- the tune (beat from the phrase's start, beats, note, grace)
TAIZ_HOOK_1 = [(0, 2.0, 'D5', 'F5'), (2, 0.5, 'F5', None), (2.5, 0.5, 'D5', None), (3, 1.0, 'Bb4', None),
               (4, 1.5, 'A4', 'Bb4'), (5.5, 0.5, 'Bb4', None), (6, 0.5, 'A4', None), (6.5, 0.5, 'F4', None), (7, 1.0, 'G4', None),
               (8, 1.5, 'Bb4', 'D5'), (9.5, 0.5, 'D5', None), (10, 1.0, 'F5', None), (11, 1.0, 'G5', 'A5'),
               (12, 0.5, 'F5', None), (12.5, 0.5, 'D5', None), (13, 0.5, 'Bb4', None), (13.5, 0.5, 'D5', None), (14, 2.0, 'A4', 'Bb4')]
TAIZ_HOOK_2 = TAIZ_HOOK_1[:9] + [(8, 1.5, 'Bb4', 'D5'), (9.5, 0.5, 'D5', None), (10, 1.0, 'F5', None), (11, 0.5, 'A5', 'Bb5'),
                                 (11.5, 0.5, 'G5', None), (12, 0.5, 'F5', None), (12.5, 0.5, 'D5', None), (13, 1.0, 'Bb4', None),
                                 (14, 2.0, 'G4', 'A4')]
TAIZ_PROG = ('Gm', 'F', 'Bb', 'F', 'Gm', 'F', 'Bb', 'Gm')
TAIZ_END = ('Gm', 'F', 'Bb', 'Gm')                       # (the answer alone, at the end)
# the second pipe, a string or two under the tune; where the strings have an A in them (F, Dm) it goes down to the A or
# the F instead of the B-flat, so it never puts B-flat against the lyre's A
TAIZ_BELOW = {'D5': 'Bb4', 'F5': 'D5', 'G5': 'D5', 'A5': 'F5', 'Bb5': 'G5', 'Bb4': 'G4', 'A4': 'F4', 'G4': 'D4', 'F4': 'D4'}
TAIZ_BELOW_A = dict(TAIZ_BELOW, D5='A4', Bb4='F4')


def second_pipe(s, bar0, hook, seed, prog, vol=1.0):
    """prog: the chord of each bar the tune spans (four beats a bar)."""
    low = []
    for (b, d, nm, g) in hook:
        ch = prog[min(len(prog) - 1, int(b // 4))]
        low.append((b, d, (TAIZ_BELOW_A if ch in ('F', 'Dm') else TAIZ_BELOW).get(nm, nm), None))
    melody(s, 'lead2', bar0, low, seed=seed, vol=vol, p=0.4)


def taiz_theme():
    """Taiz by night: 32 bars at 144."""
    s = Song(144, 32, seed=131)
    # the night: the rotor alone, the kettledrum, a held bass, the flute calling
    for i in range(4):
        night_groove(s, i, 'night', fill='call' if i == 3 else None)
        rotor(s, i, 'Gm', 0.8 + 0.06 * i)
        if i % 2 == 0:
            s.hit('bass', J.bass(H('G1'), dur=3.2, vel=0.8, seed=i), i, 0, 0.8)
    # (the call starts on the first bar's third beat, so the night is never empty for long)
    melody(s, 'flute', 0, [(2, 2.5, 'D5', None), (4.5, 0.5, 'F5', None), (5, 1.0, 'D5', None),
                           (6, 3.0, 'A5', 'Bb5'), (9, 1.0, 'G5', None),
                           (10, 1.5, 'F5', None), (11.5, 0.5, 'D5', None), (12, 2.5, 'G5', 'A5')], voice='flute', seed=131, p=0.2)
    stabs(s, 3, [(12, 0.75), (14, 0.9)], ('G3', 'D4', 'G4'), dur=0.2)
    # the tune with the whole band
    for i in range(8):
        band_bar(s, 4 + i, TAIZ_PROG[i], 'A', fill='call' if i == 3 else ('roll' if i == 7 else None))
    s.hit('marfa', J.marfa(seed=401, vel=1.0), 4, 0, 1.15)
    melody(s, 'lead', 4, TAIZ_HOOK_1, seed=132)
    melody(s, 'lead', 8, TAIZ_HOOK_2, seed=133)
    # again: a second pipe, the small kettledrums, the band answering at the ends of lines
    for i in range(8):
        band_bar(s, 12 + i, TAIZ_PROG[i], 'full', fill='call' if i == 3 else ('roll' if i == 7 else None))
    melody(s, 'lead', 12, TAIZ_HOOK_1, seed=134)
    melody(s, 'lead', 16, TAIZ_HOOK_2, seed=135)
    second_pipe(s, 12, TAIZ_HOOK_1, 136, TAIZ_PROG[:4])
    second_pipe(s, 16, TAIZ_HOOK_2, 137, TAIZ_PROG[4:])
    stabs(s, 15, [(8, 0.85), (10, 0.8), (12, 1.0)], ('F4', 'A4', 'F5'))
    stabs(s, 19, [(10, 0.9), (12, 0.9), (14, 1.0)], ('G4', 'Bb4', 'D5'))
    # the dark: half time, the lyre picked out, the flute alone over it
    prog = ('Bb', 'F', 'Gm', 'Dm')
    for i in range(4):
        bar = 20 + i
        night_groove(s, bar, 'half')
        lyre_arp(s, bar, TAIZ_LYRE[prog[i]])
        root = ROOT[prog[i]]
        s.hit('bass', J.bass(H(root), dur=1.1, vel=0.85, seed=bar), bar, 0)
        s.hit('qanbus', J.qanbus(H(root) * 2, dur=0.9, vel=0.9, seed=bar), bar, 0, 1.0, -0.2)
        s.hit('qanbus', J.qanbus(H(root) * 4, dur=0.4, vel=0.6, seed=bar + 3), bar, 10, 1.0, -0.2)
        rotor(s, bar, prog[i], 0.45, steps=range(8, 16))
    melody(s, 'flute', 20, [(0, 2, 'F5', None), (2, 1, 'D5', None), (3, 1, 'Bb4', None),
                            (4, 3, 'A4', 'Bb4'), (7, 1, 'F4', None),
                            (8, 1.5, 'G4', None), (9.5, 0.5, 'Bb4', None), (10, 1, 'D5', None), (11, 1, 'G5', None),
                            (12, 3.5, 'A5', 'Bb5')], voice='flute', seed=138, p=0.15)
    # the climb: B-flat, F, D minor, F, the snare filling in, the mizmar to the top string
    for i, ch in enumerate(('Bb', 'F', 'Dm', 'F')):
        bar = 24 + i
        night_groove(s, bar, 'build', fill='roll' if i == 3 else None)
        rotor(s, bar, ch, 0.8 + 0.07 * i)
        for st in (0, 6, 8, 14):
            f = H(ROOT[ch])
            s.hit('bass', J.bass(f, dur=0.3, vel=1.0, seed=bar + st), bar, st)
            s.hit('guitar', J.chug(f * 2, dur=0.3, vel=1.0, seed=bar + st, open_=True), bar, st, 0.9, 0.3)
            s.hit('guitar', J.chug(f * 2, dur=0.3, vel=1.0, seed=bar + st + 400, open_=True), bar, st, 0.75, -0.5)
        stabs(s, bar, [(0, 1.0), (6, 0.85), (8, 0.9), (14, 0.95)], TAIZ_LYRE[ch], dur=0.2)
    melody(s, 'lead', 24, [(0, 1, 'Bb4', None), (1, 1, 'D5', None), (2, 1, 'F5', None), (3, 1, 'G5', None),
                           (4, 3.5, 'A5', 'Bb5'),
                           (8, 1, 'D5', None), (9, 1, 'F5', None), (10, 1, 'A5', None), (11, 1, 'G5', None),
                           (12, 3.0, 'A5', 'Bb5')], seed=139)
    # all in: the answer with everything, then the band stops and the night comes round again
    for i, ch in enumerate(TAIZ_END):
        band_bar(s, 28 + i, ch, 'full', fill='call' if i == 1 else None, chug=True)
        s.hit('sahn', J.clap(seed=28 + i), 28 + i, 4, 1.5, 0.1)
        s.hit('sahn', J.clap(seed=528 + i), 28 + i, 12, 1.5, -0.25, human=0.01)
    s.hit('marfa', J.marfa(seed=402, vel=1.0), 28, 0, 1.2)
    stabs(s, 28, [(0, 1.0)], ('G4', 'Bb4', 'D5'), dur=0.45)
    melody(s, 'lead', 28, TAIZ_HOOK_2, seed=140)
    second_pipe(s, 28, TAIZ_HOOK_2, 141, TAIZ_END)
    stabs(s, 31, [(8, 0.9), (12, 1.0)], ('G3', 'D4', 'G4'), dur=0.35)
    return s


TAIZ_LEVELS = dict(drums=-20.0, marfa=-22.0, tabl=-25.5, tunk=-28.0, sahn=-30.0, bass=-19.5, qanbus=-22.5, lyre=-25.5,
                   lead=-18.0, lead2=-24.5, flute=-18.5, guitar=-23.5, brass=-22.0)
TAIZ_SENDS = dict(STRAIT_SENDS, qanbus=0.12, flute=0.34)


# ---------------------------------------------------------------- the Castle Gun and their gunship
BOSS_RIFF = (('G1', 'G1', 'G2', 'G1', 'A1', 'Bb1', 'G1', 'D2'),
             ('G1', 'G1', 'G2', 'G1', 'F2', 'D2', 'Bb1', 'A1'),
             ('Bb1', 'Bb1', 'Bb2', 'Bb1', 'D2', 'Bb1', 'A1', 'Bb1'),
             ('D2', 'D2', 'D3', 'D2', 'F2', 'D2', 'A1', 'Bb1'))
BOSS_CHORDS = ('Gm', 'Gm', 'Bb', 'Dm')
BOSS_TUNE = [(0, 1.0, 'G4', None), (1, 0.5, 'Bb4', None), (1.5, 0.5, 'A4', None), (2, 1.0, 'G4', None), (3, 1.0, 'D5', 'F5'),
             (4, 1.5, 'Bb4', None), (5.5, 0.5, 'A4', None), (6, 2.0, 'G4', 'A4'),
             (8, 1.0, 'Bb4', None), (9, 0.5, 'D5', None), (9.5, 0.5, 'Bb4', None), (10, 1.0, 'F5', None), (11, 1.0, 'D5', None),
             (12, 1.0, 'A4', 'Bb4'), (13, 1.0, 'Bb4', None), (14, 2.0, 'A4', 'Bb4')]
BOSS_HIGH = {'G4': 'G5', 'Bb4': 'Bb5', 'A4': 'A5', 'D5': 'D6', 'F5': 'F6'}


def boss_drums(s, i, fill=None):
    sd = i * 71
    kicks = (0, 2, 4, 8, 10, 12) if i % 2 == 0 else (0, 2, 4, 7, 8, 10, 12, 14)
    for st in kicks:
        s.hit('drums', J.kick(seed=sd + st), i, st, 1.0 if st % 8 == 0 else 0.85)
    for st in (4, 12):
        s.hit('drums', J.snare(seed=sd + 20 + st), i, st, 1.0)
    for st in ((7, 15) if i % 2 == 0 else (7, 9, 15)):
        s.hit('drums', J.snare(seed=sd + 40 + st, ghost=True), i, st, 0.7)
    s.hit('marfa', J.marfa(seed=sd, vel=1.0), i, 0, 1.0)
    s.hit('marfa', J.marfa(seed=sd + 1, vel=0.8), i, 6, 0.85)
    s.hit('marfa', J.marfa(seed=sd + 2, vel=0.7), i, 10 if i % 2 == 0 else 14, 0.75)
    for st in (0, 8):
        s.hit('tabl', J.tabl(kind='dum', seed=sd + st), i, st, 1.0, -0.3)
    for st in (3, 6, 11, 14):
        s.hit('tabl', J.tabl(kind='tak', seed=sd + st), i, st, 0.8, -0.25)
    # the small kettledrums run three against four
    for st in range(16):
        if (i * 16 + st) % 3 == 0:
            hi = ((i * 16 + st) // 3) % 4 == 0
            s.hit('tunk', J.tunk(seed=sd + st, pitch=392.0 if hi else 294.0, vel=0.9 if hi else 0.65), i, st, 0.9, 0.5)
    for st in range(16):
        s.hit('sahn', J.sahn(seed=sd + st, vel=1.0 if st % 4 == 2 else 0.5), i, st, 1.0, 0.6, human=0.003)
    if fill == 'roll':
        for k, st in enumerate(range(8, 16)):
            s.hit('drums', J.snare(seed=sd + 50 + st, ghost=k < 4), i, st, 0.7 + 0.5 * k / 7)
        for k, st in enumerate((10, 11, 13, 14, 15)):
            s.hit('tunk', J.tunk(seed=sd + 80 + st, pitch=(440.0, 392.0, 349.0, 294.0, 220.0)[k]), i, st, 1.0, 0.35)


def taiz_boss_theme():
    """The Castle Gun and the gunship: 16 bars at 160."""
    s = Song(160, 16, seed=151)
    for i in range(16):
        sect = i // 4
        boss_drums(s, i, fill='roll' if i % 4 == 3 else None)
        ch = BOSS_CHORDS[i % 4]
        rotor(s, i, ch, 0.9)
        if sect == 2:
            # the break: the siren on the brass, B-flat then A, the bass under it
            for st, nm in ((0, 'Bb4'), (8, 'A4')):
                for k, n2 in enumerate((nm, nm[:-1] + '3')):
                    s.hit('brass', J.brass(H(n2), dur=0.62, vel=1.0, seed=i * 16 + st + k), i, st, 1.0, (-0.3, 0.3)[k])
            s.hit('bass', J.bass(H('G1'), dur=0.5, vel=1.0, seed=i), i, 0)
            s.hit('bass', J.bass(H('A1'), dur=0.5, vel=1.0, seed=i + 7), i, 8)
            continue
        for k, nm in enumerate(BOSS_RIFF[i % 4]):
            f = H(nm)
            acc = 1.0 if k % 2 == 0 else 0.82
            s.hit('bass', J.bass(f, dur=0.17, vel=acc, seed=i * 8 + k), i, k * 2)
            if sect >= 1:
                s.hit('guitar', J.chug(f * 2, dur=0.15, vel=acc, seed=i * 8 + k), i, k * 2, 1.0, 0.65)
                s.hit('guitar', J.chug(f * 2, dur=0.15, vel=acc, seed=i * 8 + k + 400), i, k * 2, 0.9, -0.65, human=0.008)
        if i % 2 == 1:
            s.hit('lyre', J.strum([H('G4'), H('D5')], dur=0.4, vel=0.9, seed=i), i, 12, 1.0, -0.35)
            s.hit('lyre', J.strum([H('A4'), H('D5')], dur=0.4, vel=0.9, up=True, seed=i + 3), i, 14, 1.0, -0.35)
    melody(s, 'lead', 4, BOSS_TUNE, seed=152)
    # the break's flute: the searchlight going over, back and forth
    melody(s, 'flute', 10, [(0, 0.5, 'A5', None), (0.5, 0.5, 'Bb5', None), (1, 0.5, 'A5', None), (1.5, 0.5, 'Bb5', None),
                            (2, 1.0, 'D6', None), (3, 1.0, 'Bb5', None),
                            (4, 0.5, 'A5', None), (4.5, 0.5, 'Bb5', None), (5, 0.5, 'A5', None), (5.5, 0.5, 'G5', None),
                            (6, 2.0, 'A5', 'Bb5')], voice='flute', seed=153, p=0.2)
    high = [(b, d, BOSS_HIGH.get(nm, nm), None) for (b, d, nm, g) in BOSS_TUNE]
    melody(s, 'flute', 12, high, voice='flute', seed=154, p=0.15)
    melody(s, 'lead', 12, BOSS_TUNE, seed=155)
    second_pipe(s, 12, BOSS_TUNE, 156, BOSS_CHORDS)
    stabs(s, 15, [(8, 0.9), (12, 1.0)], ('G3', 'D4', 'G4'), dur=0.3)
    return s


TAIZ_BOSS_LEVELS = dict(drums=-18.5, marfa=-21.0, tabl=-25.0, tunk=-26.5, sahn=-30.5, bass=-19.0, qanbus=-24.0, lyre=-25.0,
                        lead=-18.5, lead2=-24.5, flute=-19.5, guitar=-21.5, brass=-21.0)
