# music_ibb.py - Ibb, the Green Valleys: the stage theme (Khaled, 24 Oct 22:08: "Can you create the music").
# The band's five strings (D F G A Bb) read from B-flat (Bb D F G A): the brightest they go, the A under the B-flat
# leading home. The highlands in the rainy season, the morning after: a dance in threes (each beat split in three, like
# the highland drum dances: the big kettledrum on one and three with a push before three, the small kettledrum rolling
# every third, the tray riding them), the qanbus galloping the chord under it, the lyre off the beat, the mizmar on a
# tune that climbs the strings like the terraces and comes home to B-flat. And the joke of the mission: halfway round,
# the band stops for an important statement (a pompous fanfare, the news chime, a held chord), then picks up again as
# if nothing had happened.
#
# The stage theme, 30 bars at 120 (60 s):
#   the morning (2)     the qanbus galloping alone on B-flat and F, the kettledrum once a bar, the tray; the flute
#                       calling across the valley.
#   the tune (8)        the whole band in threes; the mizmar's tune (B-flat F G-minor F, then B-flat F G-minor B-flat).
#   again (8)           a second pipe under it, the small kettledrum rolling, claps, the brass answering at line ends.
#   the statement (2)   everything stops: a kettledrum roll, the fanfare (three short, one long), the held chord, the
#                       news chime (high, low); a snare pickup.
#   the terraces (4)    half time, the lyre picked out, the flute climbing (G-minor D-minor B-flat F).
#   the climb (2)       the drums on every beat, the guitar in, the mizmar up to the top string.
#   all in (4)          the tune's second half with everything, home on B-flat, and round to the morning.
import numpy as np
from core import *
import inst as I
from music import Song, J, H, melody, stabs, STRAIT_SENDS, TRIP, T3

IBB_LYRE = {'Bb': ('D4', 'F4', 'Bb4'), 'F': ('F4', 'A4', 'F5'), 'Gm': ('G4', 'Bb4', 'D5'), 'Dm': ('D4', 'F4', 'A4')}
# the gallop: three qanbus strokes to the beat (r the root, o its octave, f and t strings above it)
GAL_NOTES = {'Bb': dict(r='Bb2', o='Bb3', f='F3', t='D3'),
             'F': dict(r='F2', o='F3', f='A2', t='D3'),
             'Gm': dict(r='G2', o='G3', f='D3', t='Bb2'),
             'Dm': dict(r='D3', o='D4', f='A3', t='F3')}
GALLOP = ((('r', 1.0), ('r', 0.45), ('f', 0.6)), (('o', 0.8), ('r', 0.45), ('f', 0.6)),
          (('r', 0.95), ('r', 0.45), ('t', 0.6)), (('o', 0.8), ('f', 0.5), ('t', 0.55)))
# the bass under the kettledrum: one, the push before three, three, and a pickup into the next bar
LOW = {'Bb': ('Bb1', 'F2', 'Bb2'), 'F': ('F1', 'A1', 'F2'), 'Gm': ('G1', 'D2', 'G2'), 'Dm': ('D2', 'A1', 'D3')}


def gallop(s, bar, chord, vol=1.0, beats=range(4)):
    nt = GAL_NOTES[chord]
    for b in beats:
        for k, (w, v) in enumerate(GALLOP[b]):
            s.hit('qanbus', J.qanbus(H(nt[w]), dur=0.16, vel=v, seed=bar * 12 + b * 3 + k), bar, b * 4 + k * TRIP, vol, -0.2, human=0.002)


def low(s, bar, chord, vol=1.0, chug=False):
    r, f, o = (H(x) for x in LOW[chord])
    for st, fr, d, v in ((0, r, 0.42, 1.0), (4 + 2 * TRIP, r, 0.18, 0.75), (8, r, 0.36, 0.9), (12 + TRIP, f, 0.16, 0.7), (12 + 2 * TRIP, o, 0.16, 0.8)):
        s.hit('bass', J.bass(fr, dur=d, vel=v, seed=int(bar * 5 + st)), bar, st, vol)
        if chug:
            s.hit('guitar', J.chug(fr * 2, dur=min(0.3, d), vel=v, seed=int(bar * 5 + st)), bar, st, vol, 0.6)
            s.hit('guitar', J.chug(fr * 2, dur=min(0.3, d), vel=v, seed=int(bar * 5 + st) + 400), bar, st, vol * 0.9, -0.6, human=0.008)


def strums(s, bar, chord, vol=1.0):
    """The lyre off the beat: on the last third of every beat, a lighter one on the middle third of two and four."""
    fr = [H(c) for c in IBB_LYRE[chord]]
    for b in range(4):
        s.hit('lyre', J.strum(fr, dur=0.34, vel=0.85, up=b % 2 == 1, seed=bar * 16 + b), bar, b * 4 + 2 * TRIP, vol, -0.5)
    for b in (1, 3):
        s.hit('lyre', J.strum(fr[1:], dur=0.2, vel=0.5, up=True, seed=bar * 16 + b + 8), bar, b * 4 + TRIP, 0.7 * vol, -0.5)


def groove(s, bar, kind='A', vol=1.0, fill=None, claps=False):
    """One bar of the dance. kind: 'morning', 'A', 'full' (the small kettledrum rolling), 'half', 'build'."""
    sd = int(bar * 157)
    if kind == 'morning':
        s.hit('marfa', J.marfa(seed=sd, vel=0.85), bar, 0, 0.85 * vol)
        s.hit('drums', J.kick(seed=sd), bar, 0, 0.55 * vol)
        for b in range(4):
            for k in range(3):
                s.hit('sahn', J.sahn(seed=sd + b * 3 + k, vel=0.7 if k == 0 else 0.35), bar, b * 4 + k * TRIP, 0.8 * vol, 0.6, human=0.003)
        s.hit('tabl', J.tabl(kind='tak', seed=sd + 5), bar, 12 + 2 * TRIP, 0.55 * vol, -0.25)
    elif kind in ('A', 'full'):
        for st, v in ((0, 1.0), (8, 0.85)):
            s.hit('drums', J.kick(seed=sd + st), bar, st, v * vol)
            s.hit('marfa', J.marfa(seed=sd + st, vel=v), bar, st, v * vol)
            s.hit('tabl', J.tabl(kind='dum', seed=sd + st), bar, st, 0.9 * vol, -0.3)
        s.hit('marfa', J.marfa(seed=sd + 7, vel=0.7), bar, 4 + 2 * TRIP, 0.7 * vol)                 # the push into three
        s.hit('drums', J.kick(seed=sd + 9), bar, (4 + 2 * TRIP) if bar % 2 == 0 else (12 + TRIP), 0.6 * vol)
        for b in (1, 3):
            s.hit('drums', J.snare(seed=sd + 20 + b), bar, b * 4, 0.9 * vol)
            s.hit('sahn', J.jingle(seed=sd + b), bar, b * 4, 0.9 * vol, -0.6)
            if claps:
                s.hit('sahn', J.clap(seed=sd + b), bar, b * 4, 1.4 * vol, 0.15)
                s.hit('sahn', J.clap(seed=sd + b + 500), bar, b * 4, 1.1 * vol, -0.3, human=0.01)
        s.hit('drums', J.snare(seed=sd + 30, ghost=True), bar, 12 + 2 * TRIP, 0.55 * vol)
        for b in range(4):
            s.hit('tabl', J.tabl(kind='tak', seed=sd + b * 5), bar, b * 4 + 2 * TRIP, 0.6 * vol, -0.25)
            for k in range(3):
                s.hit('sahn', J.sahn(seed=sd + b * 3 + k, vel=(0.95, 0.45, 0.6)[k]), bar, b * 4 + k * TRIP, 0.9 * vol, 0.6, human=0.003)
        if kind == 'full':
            # the small kettledrum rolling every third, as in the highland dances
            for b in range(4):
                for k in range(3):
                    s.hit('tunk', J.tunk(seed=sd + 60 + b * 3 + k, pitch=(440.0, 392.0, 349.0)[k], vel=(0.8, 0.45, 0.55)[k]),
                          bar, b * 4 + k * TRIP, 0.75 * vol, 0.45)
    elif kind == 'half':
        s.hit('marfa', J.marfa(seed=sd, vel=0.9), bar, 0, 0.9 * vol)
        s.hit('drums', J.kick(seed=sd), bar, 0, 0.75 * vol)
        s.hit('drums', J.snare(seed=sd + 3), bar, 8, 0.7 * vol)
        s.hit('tabl', J.tabl(kind='dum', seed=sd + 1), bar, 0, 0.8 * vol, -0.25)
        for b in range(4):
            s.hit('sahn', J.sahn(seed=sd + b, vel=0.7), bar, b * 4, vol, 0.6, human=0.003)
            s.hit('tabl', J.tabl(kind='tak', seed=sd + b + 9), bar, b * 4 + 2 * TRIP, 0.45 * vol, -0.25)
    elif kind == 'build':
        for b in range(4):
            s.hit('drums', J.kick(seed=sd + b), bar, b * 4, vol)
            s.hit('marfa', J.marfa(seed=sd + b, vel=0.9), bar, b * 4, 0.85 * vol)
            for k in range(3):
                s.hit('drums', J.snare(seed=sd + 40 + b * 3 + k, ghost=True), bar, b * 4 + k * TRIP, (0.45 + 0.55 * (b * 3 + k) / 11) * vol)
                s.hit('sahn', J.sahn(seed=sd + b * 3 + k, vel=0.8 if k == 0 else 0.5), bar, b * 4 + k * TRIP, vol, 0.6, human=0.003)
    if fill == 'call':
        for i, st in enumerate((12, 12 + TRIP, 12 + 2 * TRIP)):
            s.hit('tunk', J.tunk(seed=sd + 80 + i, pitch=(330.0, 392.0, 440.0)[i]), bar, st, 1.0 * vol, 0.35)
    elif fill == 'roll':
        for i in range(6):
            s.hit('drums', J.snare(seed=sd + 40 + i, ghost=i < 2), bar, 8 + i * TRIP, (0.6 + 0.5 * i / 5) * vol)
        for i, st in enumerate((12, 12 + TRIP, 12 + 2 * TRIP)):
            s.hit('tunk', J.tunk(seed=sd + 90 + i, pitch=(440.0, 392.0, 330.0)[i]), bar, st, 1.0 * vol, 0.35)


def band(s, bar, chord, kind='A', vol=1.0, fill=None, claps=False, chug=False):
    groove(s, bar, kind, vol, fill, claps)
    gallop(s, bar, chord, vol)
    low(s, bar, chord, vol, chug)
    strums(s, bar, chord, 0.85 * vol)


# ---------------------------------------------------------------- the tunes (beat from the phrase's start, beats, note, grace)
L2, S1 = 2 * T3, T3          # the long and the short of a beat in threes
IBB_A1 = [(0, L2, 'D5', None), (L2, S1, 'F5', None), (1, 1, 'Bb5', None), (2, L2, 'A5', None), (2 + L2, S1, 'G5', None), (3, 1, 'F5', None),
          (4, L2, 'A5', None), (4 + L2, S1, 'G5', None), (5, L2, 'F5', None), (5 + L2, S1, 'D5', None), (6, 2, 'F5', 'G5'),
          (8, L2, 'G5', None), (8 + L2, S1, 'A5', None), (9, L2, 'Bb5', None), (9 + L2, S1, 'A5', None), (10, L2, 'G5', None),
          (10 + L2, S1, 'F5', None), (11, 1, 'D5', None),
          (12, L2, 'F5', None), (12 + L2, S1, 'G5', None), (13, 2, 'A5', 'Bb5')]
IBB_A2 = [(0, L2, 'D5', None), (L2, S1, 'F5', None), (1, 1, 'Bb5', None), (2, L2, 'A5', None), (2 + L2, S1, 'G5', None),
          (3, L2, 'F5', None), (3 + L2, S1, 'G5', None),
          (4, 1, 'A5', None), (5, L2, 'F5', None), (5 + L2, S1, 'G5', None), (6, L2, 'A5', None), (6 + L2, S1, 'Bb5', None), (7, 1, 'A5', None),
          (8, L2, 'G5', None), (8 + L2, S1, 'F5', None), (9, 1, 'D5', None), (10, L2, 'G5', None), (10 + L2, S1, 'A5', None), (11, 1, 'Bb5', None),
          (12, L2, 'A5', None), (12 + L2, S1, 'G5', None), (13, L2, 'F5', None), (13 + L2, S1, 'D5', None), (14, 2, 'Bb4', 'D5')]
PROG_A1 = ('Bb', 'F', 'Gm', 'F')
PROG_A2 = ('Bb', 'F', 'Gm', 'Bb')
# the second pipe a string or two under the tune; over F and D minor (the lyre's A) it never goes to a B-flat
IBB_BELOW = {'Bb5': 'F5', 'A5': 'F5', 'G5': 'D5', 'F5': 'D5', 'D5': 'Bb4', 'Bb4': 'F4', 'A4': 'F4', 'G4': 'D4', 'F4': 'D4'}
IBB_BELOW_A = dict(IBB_BELOW, D5='A4')
MORNING = [(1, 1.5, 'F5', None), (2.5, 0.5, 'G5', None), (3, 1, 'Bb5', None), (4, 1.5, 'A5', None), (5.5, 0.5, 'G5', None), (6, 1.6, 'F5', None)]
TERRACES = [(0, 1, 'G4', None), (1, 1, 'Bb4', None), (2, 2, 'D5', 'F5'),
            (4, 1, 'F5', None), (5, 1, 'A5', None), (6, 2, 'D5', None),
            (8, 1, 'F5', None), (9, 1, 'D5', None), (10, 1, 'Bb4', None), (11, 1, 'D5', None),
            (12, 1.5, 'A4', None), (13.5, 0.5, 'G4', None), (14, 2, 'F4', 'G4')]
CLIMB = [(0, 1, 'Bb4', None), (1, 1, 'D5', None), (2, 1, 'F5', None), (3, 1, 'G5', None), (4, 3, 'A5', 'Bb5'), (7, L2, 'G5', None), (7 + L2, S1, 'A5', None)]


def pipe2(s, bar0, tune, prog, seed, vol=1.0):
    low_ = []
    for (b, d, nm, g) in tune:
        ch = prog[min(len(prog) - 1, int(b // 4))]
        low_.append((b, d, (IBB_BELOW_A if ch in ('F', 'Dm') else IBB_BELOW).get(nm, nm), None))
    melody(s, 'lead2', bar0, low_, seed=seed, vol=vol, p=0.4)


def fanfare(s, bar, st, chord, dur, vel=1.0):
    """The statement's brass: its own stem, so the fanfare can stand above the band's answers."""
    for i, nm in enumerate(chord):
        s.hit('fanfare', J.brass(H(nm), dur=dur, vel=vel, seed=int(bar * 16 + st * 3 + i)), bar, st, 1.0, (-0.3, 0.0, 0.3, 0.15)[i % 4])


def statement(s, bar):
    """The band stops for an important statement: a kettledrum roll, the fanfare (three short and one long), the chord
    held over the bass, the news chime high and low, a snare pickup back into the dance."""
    sd = bar * 211
    for i in range(6):                                            # the roll under the first two beats, swelling
        s.hit('marfa', J.marfa(seed=sd + i, vel=0.5 + 0.1 * i), bar, i * TRIP, (0.55 + 0.09 * i))
    for st in (8, 8 + TRIP, 8 + 2 * TRIP):                        # ta-ta-ta
        fanfare(s, bar, st, ('D4', 'F4', 'Bb4'), 0.14, 0.9)
    fanfare(s, bar, 12, ('F4', 'A4', 'F5'), 0.5)                  # taaa
    s.hit('bass', J.bass(H('F1'), dur=0.5, vel=1.0, seed=sd), bar, 12)
    s.hit('drums', J.kick(seed=sd + 7), bar, 12, 0.9)
    s.hit('marfa', J.marfa(seed=sd + 8, vel=1.0), bar + 1, 0, 1.2)  # and the long one: B-flat, held
    s.hit('drums', J.kick(seed=sd + 9), bar + 1, 0, 1.0)
    s.hit('bass', J.bass(H('Bb1'), dur=1.6, vel=1.0, seed=sd + 1), bar + 1, 0)
    fanfare(s, bar + 1, 0, ('Bb3', 'D4', 'F4', 'Bb4'), 1.6)
    fanfare(s, bar + 1, 0, ('D5', 'F5'), 1.4, 0.85)
    for k in range(3):
        s.hit('sahn', J.jingle(seed=sd + k), bar + 1, k * TRIP, 1.0, (-0.6, 0.6, 0.0)[k])
    for st, nm in ((8, 'F5'), (8 + 2 * TRIP, 'Bb4')):            # the news chime
        s.hit('bell', J.bell(H(nm), dur=0.9, vel=1.0), bar + 1, st, 1.0, 0.1)
    for i in range(3):
        s.hit('drums', J.snare(seed=sd + 30 + i), bar + 1, 12 + i * TRIP, 0.7 + 0.15 * i)


def ibb_theme():
    """The Green Valleys: 30 bars at 120, in threes."""
    s = Song(120, 30, seed=171)
    # the morning: the qanbus alone, the kettledrum, the tray; the flute calling across the valley
    for i, ch in enumerate(('Bb', 'F')):
        groove(s, i, 'morning', fill='call' if i == 1 else None)
        gallop(s, i, ch, 0.8 + 0.1 * i)
        s.hit('bass', J.bass(H(LOW[ch][0]), dur=1.8, vel=0.8, seed=i), i, 0, 0.8)
    melody(s, 'flute', 0, MORNING, voice='flute', seed=171, p=0.2)
    # the tune with the whole band
    for i in range(8):
        ch = (PROG_A1 + PROG_A2)[i]
        band(s, 2 + i, ch, 'A', fill='call' if i == 3 else ('roll' if i == 7 else None))
    s.hit('marfa', J.marfa(seed=401, vel=1.0), 2, 0, 1.15)
    melody(s, 'lead', 2, IBB_A1, seed=172)
    melody(s, 'lead', 6, IBB_A2, seed=173)
    # again: a second pipe, the small kettledrum rolling, claps, the brass answering at the ends of lines
    for i in range(8):
        ch = (PROG_A1 + PROG_A2)[i]
        band(s, 10 + i, ch, 'full', fill='call' if i == 3 else None, claps=True)
    melody(s, 'lead', 10, IBB_A1, seed=174)
    melody(s, 'lead', 14, IBB_A2, seed=175)
    pipe2(s, 10, IBB_A1, PROG_A1, 176)
    pipe2(s, 14, IBB_A2, PROG_A2, 177)
    stabs(s, 13, [(8, 0.85), (8 + TRIP, 0.75), (8 + 2 * TRIP, 0.9), (12, 1.0)], ('F4', 'A4', 'F5'))
    stabs(s, 17, [(4, 0.9), (8, 1.0)], ('D4', 'F4', 'Bb4'), dur=0.3)
    # an important statement
    statement(s, 18)
    # the terraces: half time, the lyre picked out, the flute climbing
    for i, ch in enumerate(('Gm', 'Dm', 'Bb', 'F')):
        bar = 20 + i
        groove(s, bar, 'half', fill='call' if i == 3 else None)
        fr = [H(c) for c in IBB_LYRE[ch]]
        for k, idx in enumerate((0, 1, 2, 1)):
            s.hit('lyre', J.lyre(fr[idx], dur=0.9, vel=0.75 if k == 0 else 0.55, seed=bar * 8 + k), bar, k * 4 + (TRIP if k % 2 else 0), 1.0, -0.5)
        r = H(LOW[ch][0])
        s.hit('bass', J.bass(r, dur=1.0, vel=0.85, seed=bar), bar, 0)
        s.hit('qanbus', J.qanbus(r * 2, dur=0.9, vel=0.9, seed=bar), bar, 0, 1.0, -0.2)
        s.hit('qanbus', J.qanbus(r * 4, dur=0.4, vel=0.6, seed=bar + 3), bar, 8 + 2 * TRIP, 1.0, -0.2)
        gallop(s, bar, ch, 0.45, beats=(2, 3))
    melody(s, 'flute', 20, TERRACES, voice='flute', seed=178, p=0.15)
    # the climb: the drums on every beat, the guitar in, the mizmar to the top string
    for i, ch in enumerate(('Bb', 'F')):
        bar = 24 + i
        groove(s, bar, 'build', fill='roll' if i == 1 else None)
        gallop(s, bar, ch, 0.85 + 0.1 * i)
        for b in range(4):
            f = H(LOW[ch][0])
            s.hit('bass', J.bass(f, dur=0.3, vel=1.0, seed=bar + b), bar, b * 4)
            s.hit('guitar', J.chug(f * 2, dur=0.3, vel=1.0, seed=bar + b, open_=True), bar, b * 4, 0.9, 0.3)
            s.hit('guitar', J.chug(f * 2, dur=0.3, vel=1.0, seed=bar + b + 400, open_=True), bar, b * 4, 0.75, -0.5)
        stabs(s, bar, [(0, 1.0), (8, 0.9)], IBB_LYRE[ch], dur=0.2)
    melody(s, 'lead', 24, CLIMB, seed=179)
    # all in: the tune's second half with everything, home on B-flat
    for i, ch in enumerate(PROG_A2):
        band(s, 26 + i, ch, 'full', fill='call' if i == 1 else None, claps=True, chug=True)
    s.hit('marfa', J.marfa(seed=402, vel=1.0), 26, 0, 1.2)
    stabs(s, 26, [(0, 1.0)], ('D4', 'F4', 'Bb4'), dur=0.45)
    melody(s, 'lead', 26, IBB_A2, seed=180)
    pipe2(s, 26, IBB_A2, PROG_A2, 181)
    stabs(s, 29, [(8, 0.9), (12, 1.0)], ('Bb3', 'D4', 'F4'), dur=0.35)
    return s


IBB_LEVELS = dict(drums=-20.0, marfa=-22.0, tabl=-25.5, tunk=-28.0, sahn=-29.5, bass=-20.0, qanbus=-22.0, lyre=-23.5,
                  lead=-18.0, lead2=-24.5, flute=-18.5, guitar=-24.0, brass=-21.5, fanfare=-18.0, bell=-23.0)
IBB_SENDS = dict(STRAIT_SENDS, qanbus=0.12, flute=0.34, bell=0.30, fanfare=0.30)


# ---------------------------------------------------------------- a check: the long notes against the strings under them
def check_tunes():
    """Every note of a beat or longer in the tunes is a note of the chord's strings or a whole tone off one, never a
    semitone (as the other themes are checked): returns the notes that break it."""
    pc = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

    def cls(nm):
        k = pc[nm[0]] + (-1 if len(nm) > 2 and nm[1] == 'b' else 0)
        return k % 12
    bad = []
    for name, tune, prog in (('A1', IBB_A1, PROG_A1), ('A2', IBB_A2, PROG_A2), ('terraces', TERRACES, ('Gm', 'Dm', 'Bb', 'F')),
                             ('morning', MORNING, ('Bb', 'F')), ('climb', CLIMB, ('Bb', 'F'))):
        for (b, d, nm, g) in tune:
            if d < 0.99:
                continue
            ch = prog[min(len(prog) - 1, int(b // 4))]
            strings = [cls(x) for x in IBB_LYRE[ch]]
            dist = min(min((cls(nm) - c) % 12, (c - cls(nm)) % 12) for c in strings)
            if dist == 1:
                bad.append((name, b, nm, ch))
    return bad
