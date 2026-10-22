# music.py - the Strait's music. One lyre tuning, D F G A Bb, read three ways:
#   from D   the stage theme (a tough minor)
#   from A   the Shore Battery (dark; the A-Bb semitone doubles as its alarm)
#   from Bb  mission complete (the same strings come out bright)
# The band is the coast's: a big kettledrum leading, a two-headed drum holding the pattern, small
# kettledrums answering, a copper tray ticking, a strummed five-string lyre, a qanbus on the bass riff,
# a double-reed mizmar on the tune, a flute in the bridge. From the arcade: a march snare, unison
# band hits, an overdriven chug under the last chorus.
import numpy as np
from core import *
import inst as I

H = I.hz


class Cached:
    """The same drum or string stroke is used many times: render each variant once."""

    def __init__(self, mod, variants=3):
        self.mod, self.cache, self.v = mod, {}, variants

    def __getattr__(self, name):
        fn = getattr(self.mod, name)

        def call(*a, **k):
            if 'seed' in k:
                k['seed'] = int(k['seed']) % self.v
            key = (name,
                   tuple(tuple(round(float(z), 3) for z in x) if isinstance(x, (list, tuple)) else
                         (round(x, 3) if isinstance(x, float) else x) for x in a),
                   tuple(sorted((kk, round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in k.items())))
            if key not in self.cache:
                self.cache[key] = fn(*a, **k)
            return self.cache[key]
        return call


J = Cached(I)
STRINGS = ('D', 'F', 'G', 'A', 'Bb')


class Song:
    def __init__(self, bpm, bars, tail=2.5, seed=1):
        self.bpm = bpm
        self.beat = 60.0 / bpm
        self.bars = bars
        self.length = bars * 4 * self.beat
        self.total = self.length + tail
        self.stems = {}
        self.sends = {}
        self.r = rng(seed)
        self.cache = {}

    def bus(self, name):
        if name not in self.stems:
            self.stems[name] = Bus(self.total)
        return self.stems[name]

    def t(self, bar, step=0.0):
        """Seconds at a bar (from 0) and a sixteenth-note step within it."""
        return (bar * 4 + step / 4.0) * self.beat

    def hit(self, stem, snd, bar, step, gain=1.0, p=0.0, human=0.004):
        dt = self.r.uniform(-human, human) if human else 0.0
        g = gain * (1 + self.r.uniform(-0.06, 0.06))
        self.bus(stem).put(snd, max(0.0, self.t(bar, step) + dt), g, p)

    def one(self, key, fn):
        if key not in self.cache:
            self.cache[key] = fn()
        return self.cache[key]

    def render(self, levels, sends, rev, master_lufs=-15.0, loop=True):
        """Balance the stems to their loudness targets, add the room, fold the tail for looping, master."""
        mix = np.zeros((n_of(self.total), 2))
        wet = np.zeros((n_of(self.total), 2))
        report = {}
        for name, b in self.stems.items():
            x = b.x
            if not np.any(x):
                continue
            if name in ('drums', 'marfa', 'tabl', 'tunk'):
                # drums go through a soft clip of their own: the peaks round off, the weight stays
                pk = np.max(np.abs(x))
                x = soft(x / pk * 2.2, 1.0) * pk / 2.2 * 1.6
            l = lufs(x)
            g = 10 ** ((levels[name] - l) / 20)
            mix += x * g
            if sends.get(name, 0) > 0:
                wet += x * g * sends[name]
            report[name] = (round(l, 1), round(db(g), 1))
        w = convolve(wet, rev)[:len(mix)]
        mix = mix + w * 0.5
        n = n_of(self.length)
        if loop:
            tail = mix[n:]
            body = mix[:n].copy()
            m = min(len(tail), n)
            body[:m] += tail[:m]
            mix = body
        mix = filt(mix, hp(32), shelf_hi(9500, -2.0), lp(15000))
        # bring to level, round off the tallest drum peaks, then limit what is left
        g = 10 ** ((master_lufs + 1.0 - lufs(mix)) / 20)
        mix = soft(mix * g * 0.9, 1.0) / 0.9
        out, l0, red = to_level(mix, master_lufs, -1.0)
        report['_master'] = dict(pre_lufs=round(l0, 1), limiter_db=round(red, 1), out_lufs=round(lufs(out), 1),
                                 peak_db=round(db(np.abs(out).max()), 2), seconds=round(len(out) / SR, 3))
        return out, report


# ---------------------------------------------------------------- shared patterns
def drums_groove(s, bar, kind='A', fill=None, vol=1.0):
    """One bar of the band's groove. kind: 'A' full, 'half' the bridge, 'build' the climb, 'boss'."""
    K, SN, GH = I.kick, I.snare, lambda **k: J.snare(ghost=True, **k)
    sd = int(bar * 131)
    if kind in ('A', 'boss'):
        kicks = [0, 6, 8, 11] if bar % 2 == 0 else [0, 3, 8, 10]
        if kind == 'boss':
            kicks = [0, 2, 4, 8, 10, 12] if bar % 2 == 0 else [0, 2, 4, 7, 8, 10, 12, 14]
        for st in kicks:
            s.hit('drums', K(seed=sd + st), bar, st, 1.0 * vol)
        for st in (4, 12):
            s.hit('drums', SN(seed=sd + st), bar, st, 1.0 * vol)
        for st in ((7, 15) if bar % 2 == 0 else (7, 9, 15)):
            s.hit('drums', GH(seed=sd + st), bar, st, 0.7 * vol)
        # the big kettledrum leads: the downbeat and one push
        s.hit('marfa', J.marfa(seed=sd), bar, 0, 1.0 * vol)
        s.hit('marfa', J.marfa(seed=sd + 1, vel=0.75), bar, 10 if bar % 2 == 0 else 14, 0.8 * vol)
        # the two-headed drum keeps the pattern
        for st in (0, 8):
            s.hit('tabl', J.tabl(kind='dum', seed=sd + st), bar, st, 1.0 * vol, -0.3)
        for st in ((2, 6, 12) if bar % 2 == 0 else (2, 6, 12, 14, 15)):
            s.hit('tabl', J.tabl(kind='tak', seed=sd + st), bar, st, 0.85 * vol, -0.25)
        # the small kettledrums run three against the band's four
        for st in range(16):
            if (bar * 16 + st) % 3 == 0:
                hi = ((bar * 16 + st) // 3) % 4 == 0
                s.hit('tunk', J.tunk(seed=sd + st, pitch=330.0 if hi else 262.0, vel=0.9 if hi else 0.65), bar, st,
                      (1.0 if kind == 'boss' else 0.8) * vol, 0.5)
        for st in range(16):
            acc = st % 4 == 2
            s.hit('sahn', J.sahn(seed=sd + st, vel=1.0 if acc else 0.55), bar, st, vol, 0.6, human=0.003)
        for st in (4, 12, 14):
            s.hit('sahn', J.jingle(seed=sd + st), bar, st, 0.9 * vol, -0.6)
    elif kind == 'half':
        s.hit('marfa', J.marfa(seed=sd), bar, 0, 0.9 * vol)
        s.hit('marfa', J.marfa(seed=sd + 1, vel=0.6), bar, 11, 0.7 * vol)
        s.hit('tabl', J.tabl(kind='dum', seed=sd), bar, 0, 0.8 * vol, -0.25)
        for st in (6, 8, 14):
            s.hit('tabl', J.tabl(kind='tak', seed=sd + st), bar, st, 0.6 * vol, -0.25)
        s.hit('drums', J.snare(seed=sd), bar, 8, 0.75 * vol)
        for st in range(0, 16, 2):
            s.hit('sahn', J.sahn(seed=sd + st, vel=0.9 if st % 4 == 2 else 0.5), bar, st, vol, 0.6, human=0.003)
    elif kind == 'build':
        for st in (0, 6, 12):
            s.hit('drums', K(seed=sd + st), bar, st, 1.0 * vol)
            s.hit('marfa', J.marfa(seed=sd + st), bar, st, 0.9 * vol)
        for st in range(16):
            s.hit('drums', GH(seed=sd + st), bar, st, (0.5 + 0.6 * st / 16) * vol)
        for st in range(0, 16, 2):
            s.hit('sahn', J.sahn(seed=sd + st, vel=0.8), bar, st, vol, 0.6, human=0.003)
    if fill == 'roll':
        # a march roll into the next bar: snare sixteenths swelling, small kettledrums stepping down
        for i, st in enumerate(range(8, 16)):
            s.hit('drums', J.snare(seed=sd + 50 + st, ghost=i < 4), bar, st, (0.7 + 0.5 * i / 7) * vol)
        for i, st in enumerate((10, 11, 13, 14, 15)):
            s.hit('tunk', J.tunk(seed=sd + 70 + st, pitch=(392, 349, 330, 294, 262)[i]), bar, st, 1.0 * vol, 0.35)
    elif fill == 'call':
        for i, st in enumerate((12, 13, 14, 15)):
            s.hit('tunk', J.tunk(seed=sd + 90 + st, pitch=(294, 330, 349, 392)[i]), bar, st, 1.0 * vol, 0.35)
        s.hit('drums', J.snare(seed=sd + 91), bar, 14, 0.9 * vol)
        s.hit('drums', J.snare(seed=sd + 92), bar, 15, 1.0 * vol)


def bass_line(s, bar, notes, stem='bass', chug=False, vol=1.0):
    """Eight eighth-notes to the bar; None is a rest."""
    for i, nm in enumerate(notes):
        if nm is None:
            continue
        acc = 1.0 if i % 2 == 0 else 0.82
        f = H(nm)
        s.hit(stem, J.bass(f, dur=0.17, vel=acc, seed=bar * 8 + i), bar, i * 2, vol)
        if chug:
            s.hit('guitar', J.chug(f * 2, dur=0.15, vel=acc, seed=bar * 8 + i), bar, i * 2, vol, 0.65)
            s.hit('guitar', J.chug(f * 2, dur=0.15, vel=acc, seed=bar * 8 + i + 400), bar, i * 2, vol * 0.9, -0.65, human=0.008)


def lyre_strums(s, bar, chord, steps=(2, 6, 10, 14), light=(5, 13), vol=1.0):
    fr = [H(c) for c in chord]
    for i, st in enumerate(steps):
        s.hit('lyre', J.strum(fr, dur=0.5, vel=0.9, up=i % 2 == 1, seed=bar * 16 + st), bar, st, vol, -0.5)
    for st in light:
        s.hit('lyre', J.strum(fr[1:], dur=0.3, vel=0.55, up=True, seed=bar * 16 + st), bar, st, 0.7 * vol, -0.5)


def lyre_arp(s, bar, chord, vol=1.0):
    fr = [H(c) for c in chord]
    order = [0, 1, 2, 1, 0, 1, 2, 1]
    for i, k in enumerate(order):
        s.hit('lyre', J.lyre(fr[k], dur=0.9, vel=0.8 if i % 4 == 0 else 0.6, seed=bar * 8 + i), bar, i * 2, vol, -0.5)


def melody(s, stem, bar0, notes, voice='mizmar', vol=1.0, p=0.0, seed=0):
    """notes: (beat from bar0, beats long, note name, grace note name or None)."""
    if not notes:
        return
    b = s.beat
    start = notes[0][0] * b
    end = max(n[0] + n[1] for n in notes) * b + 0.12
    ev = [((n[0] * b - start), n[1] * b * 0.96, H(n[2]), H(n[3]) if n[3] else None) for n in notes]
    fn = I.mizmar if voice == 'mizmar' else I.flute
    y = fn(ev, end - start, seed=seed)
    s.bus(stem).put(y, s.t(bar0) + start, vol, p)


def stabs(s, bar, hits, chord=('D4', 'A4', 'D5'), vol=1.0, dur=0.16):
    """Unison band hits: (step, accent)."""
    for st, acc in hits:
        for i, nm in enumerate(chord):
            s.hit('brass', J.brass(H(nm), dur=dur, vel=acc, seed=bar * 16 + st + i), bar, st, vol, (-0.3, 0.0, 0.3)[i % 3])


# ---------------------------------------------------------------- the stage theme
HOOK_1 = [(0, 1.5, 'D5', 'F5'), (1.5, 0.5, 'A4', None), (2, 0.5, 'Bb4', None), (2.5, 0.5, 'A4', None), (3, 1.0, 'G4', None),
          (4, 1.0, 'F4', None), (5, 0.5, 'G4', None), (5.5, 2.0, 'A4', 'Bb4'), (7.5, 0.5, 'D5', None),
          (8, 0.5, 'D5', None), (8.5, 0.5, 'F5', None), (9, 0.5, 'D5', None), (9.5, 1.0, 'Bb4', None), (10.5, 0.5, 'A4', None),
          (11, 0.5, 'G4', None), (11.5, 0.5, 'F4', None), (12, 2.0, 'A4', 'Bb4')]
HOOK_2 = [(0, 1.5, 'D5', 'F5'), (1.5, 0.5, 'A4', None), (2, 0.5, 'Bb4', None), (2.5, 0.5, 'A4', None), (3, 1.0, 'G4', None),
          (4, 1.0, 'F4', None), (5, 0.5, 'G4', None), (5.5, 2.0, 'A4', 'Bb4'), (7.5, 0.5, 'D5', None),
          (8, 0.5, 'D5', None), (8.5, 0.5, 'F5', None), (9, 1.0, 'G5', 'A5'), (10, 0.5, 'F5', None), (10.5, 0.5, 'D5', None),
          (11, 0.5, 'Bb4', None), (11.5, 0.5, 'A4', None), (12, 2.5, 'D5', 'F5')]
# a second pipe two strings below the tune
BELOW = {'D5': 'A4', 'A4': 'F4', 'Bb4': 'G4', 'G4': 'D4', 'F4': 'D4', 'F5': 'Bb4', 'G5': 'D5', 'A5': 'F5', 'D4': 'A3'}
PROG = ('D', 'D', 'Bb', 'A')
BASS = {
    'D0': ['D2', 'D2', 'D3', 'D2', 'F2', 'G2', 'A2', 'A2'],
    'D1': ['D2', 'D2', 'D3', 'D2', 'A2', 'G2', 'F2', 'D2'],
    'Bb': ['Bb1', 'Bb1', 'Bb2', 'Bb1', 'Bb1', 'D2', 'F2', 'G2'],
    'A': ['A1', 'A1', 'A2', 'A1', 'A1', 'A2', 'G2', 'F2'],
    'Aend': ['A1', 'A1', 'A2', 'A1', 'A2', 'A1', 'A2', 'A2'],
    'G': ['G1', 'G1', 'G2', 'G1', 'Bb1', 'D2', 'G2', 'D2'],
}
LYRE = {'D': ('D4', 'A4', 'D5'), 'Bb': ('D4', 'F4', 'Bb4'), 'A': ('G4', 'A4', 'D5'), 'G': ('G4', 'Bb4', 'D5'),
        'Dm': ('D4', 'F4', 'A4')}


def a_section(s, bar0, hook, second=False, chug=False, claps=False, last_fill='roll', vol=1.0):
    for i in range(8):
        bar = bar0 + i
        ch = PROG[i % 4]
        fill = None
        if i == 3:
            fill = 'call'
        if i == 7:
            fill = last_fill
        drums_groove(s, bar, 'A', fill, vol)
        key = {'D': 'D0' if i % 4 == 0 else 'D1', 'Bb': 'Bb', 'A': 'Aend' if i == 7 else 'A'}[ch]
        bass_line(s, bar, BASS[key], chug=chug, vol=vol)
        lyre_strums(s, bar, LYRE[ch], vol=vol)
        if claps:
            s.hit('sahn', J.clap(seed=bar), bar, 12, 1.6 * vol, 0.1)
            s.hit('sahn', J.clap(seed=bar + 500), bar, 12, 1.3 * vol, -0.3, human=0.01)
    melody(s, 'lead', bar0, HOOK_1, seed=bar0 + 1, vol=vol)
    melody(s, 'lead', bar0 + 4, hook, seed=bar0 + 2, vol=vol)
    if second:
        for off, hk in ((0, HOOK_1), (4, hook)):
            low = [(b, d, BELOW.get(nm, nm), None) for (b, d, nm, g) in hk]
            melody(s, 'lead2', bar0 + off, low, seed=bar0 + off + 9, vol=vol, p=0.4)
        # the band answers in the gaps
        stabs(s, bar0 + 3, [(8, 0.9), (10, 0.8), (12, 1.0)], ('A3', 'D4', 'A4'), vol)
        stabs(s, bar0 + 7, [(10, 0.9), (12, 0.9), (14, 1.0)], ('D4', 'A4', 'D5'), vol)


def strait_theme():
    s = Song(150, 32, seed=11)
    a_section(s, 0, HOOK_2)
    a_section(s, 8, HOOK_2, second=True, last_fill='roll')
    # the bridge: half time, the flute over broken chords, then the climb back
    prog = ('G', 'Dm', 'G', 'A')
    for i in range(4):
        bar = 16 + i
        drums_groove(s, bar, 'half')
        lyre_arp(s, bar, LYRE[prog[i]])
        root = {'G': 'G1', 'Dm': 'D2', 'A': 'A1'}[prog[i]]
        s.hit('bass', J.bass(H(root), dur=1.1, vel=0.9, seed=bar), bar, 0)
        s.hit('bass', J.bass(H(root) * 2, dur=0.35, vel=0.7, seed=bar + 3), bar, 10)
    melody(s, 'flute', 16, [(0, 2, 'Bb4', None), (2, 1, 'A4', None), (3, 1, 'G4', None),
                            (4, 3, 'F4', 'G4'), (7, 1, 'D4', None),
                            (8, 1, 'G4', None), (9, 1, 'A4', None), (10, 1, 'Bb4', None), (11, 1, 'D5', 'F5'),
                            (12, 3.5, 'A4', 'Bb4')], voice='flute', seed=5, p=0.15)
    for i in range(4):
        bar = 20 + i
        ch = ('G', 'G', 'A', 'A')[i]
        drums_groove(s, bar, 'build', fill='roll' if i == 3 else None)
        root = 'G' if ch == 'G' else 'A'
        low = root + ('1' if root != 'D' else '2')
        for st in (0, 6, 12):
            s.hit('bass', J.bass(H(low), dur=0.3, vel=1.0, seed=bar + st), bar, st)
            s.hit('guitar', J.chug(H(low) * 2, dur=0.3, vel=1.0, seed=bar + st, open_=True), bar, st, 1.0, 0.3)
            s.hit('guitar', J.chug(H(low) * 2, dur=0.3, vel=1.0, seed=bar + st + 400, open_=True), bar, st, 0.8, -0.5)
        stabs(s, bar, [(0, 1.0), (6, 0.9), (12, 1.0)], LYRE[ch], dur=0.22)
        lyre_strums(s, bar, LYRE[ch], steps=(0, 6, 12), light=())
    melody(s, 'lead', 20, [(0, 1, 'G4', None), (1, 1, 'A4', None), (2, 1, 'Bb4', None), (3, 1, 'D5', None),
                           (4, 3.5, 'G5', 'A5'),
                           (8, 1, 'A4', None), (9, 1, 'Bb4', None), (10, 1, 'D5', None), (11, 1, 'F5', None),
                           (12, 2.5, 'A5', 'Bb5')], seed=31)
    a_section(s, 24, HOOK_2, second=True, chug=True, claps=True, last_fill='roll')
    return s


STRAIT_LEVELS = dict(drums=-19.5, marfa=-23.0, tabl=-24.5, tunk=-27.5, sahn=-30.5, bass=-19.5, lyre=-22.5,
                     lead=-18.0, lead2=-24.5, flute=-19.5, guitar=-23.0, brass=-22.0)
STRAIT_SENDS = dict(drums=0.06, marfa=0.10, tabl=0.10, tunk=0.14, sahn=0.10, lyre=0.12, lead=0.20, lead2=0.22,
                    flute=0.34, brass=0.22, guitar=0.05)


# ---------------------------------------------------------------- the Shore Battery
def battery_theme():
    s = Song(160, 16, seed=23)
    riff0 = ['A1', 'A1', 'A2', 'A1', 'Bb1', 'A1', 'G2', 'A1']
    riff1 = ['A1', 'A1', 'A2', 'A1', 'Bb1', 'A1', 'D2', 'F2']
    riff2 = ['Bb1', 'Bb1', 'Bb2', 'Bb1', 'A1', 'A1', 'G2', 'A1']
    motif = [(0, 1.5, 'A4', None), (1.5, 0.5, 'Bb4', None), (2, 1.0, 'A4', None), (3, 0.5, 'G4', None), (3.5, 0.5, 'F4', None),
             (4, 2.0, 'D4', 'F4'), (6, 0.5, 'F4', None), (6.5, 0.5, 'G4', None), (7, 1.0, 'A4', 'Bb4'),
             (8, 1.5, 'A4', None), (9.5, 0.5, 'Bb4', None), (10, 1.0, 'D5', None), (11, 0.5, 'Bb4', None), (11.5, 0.5, 'A4', None),
             (12, 3.0, 'G4', 'A4')]
    high = [(b, d, {'A4': 'A5', 'Bb4': 'Bb5', 'G4': 'G5', 'F4': 'F5', 'D4': 'D5', 'D5': 'D5'}.get(nm, nm), None) for (b, d, nm, g) in motif]
    for i in range(16):
        sect = i // 4
        if sect == 2:
            # the break: drums and the alarm
            drums_groove(s, i, 'boss', fill='roll' if i == 11 else None)
            for st, nm in ((0, 'A4'), (8, 'Bb4')):
                for k, n2 in enumerate((nm, nm[:-1] + '3')):
                    s.hit('brass', J.brass(H(n2), dur=0.62, vel=1.0, seed=i * 16 + st + k), i, st, 1.0, (-0.3, 0.3)[k])
            s.hit('bass', J.bass(H('A1'), dur=0.5, vel=1.0, seed=i), i, 0)
            s.hit('bass', J.bass(H('Bb1'), dur=0.5, vel=1.0, seed=i + 7), i, 8)
            continue
        drums_groove(s, i, 'boss', fill='roll' if i % 4 == 3 else None)
        riff = (riff0, riff1, riff2, riff1)[i % 4]
        bass_line(s, i, riff, chug=True)
        if i % 2 == 1:
            s.hit('lyre', J.strum([H('A4'), H('D5')], dur=0.4, vel=0.9, seed=i), i, 12, 1.0, -0.35)
            s.hit('lyre', J.strum([H('Bb4'), H('D5')], dur=0.4, vel=0.9, up=True, seed=i + 3), i, 14, 1.0, -0.35)
    melody(s, 'lead', 0, motif, seed=41)
    melody(s, 'lead', 4, motif, seed=42)
    melody(s, 'lead', 12, high, seed=43)
    melody(s, 'lead2', 12, motif, seed=44, p=0.3)
    return s


BATTERY_LEVELS = dict(drums=-18.5, marfa=-21.0, tabl=-25.0, tunk=-25.5, sahn=-31.0, bass=-19.0, lyre=-25.0,
                      lead=-18.5, lead2=-24.0, guitar=-21.5, brass=-21.0)


# ---------------------------------------------------------------- jingles
def mission_start():
    """Two bars: the drums bring the boat in, the band answers with a rising call."""
    s = Song(150, 2, tail=2.2, seed=31)
    for st, v in ((0, 1.0), (6, 0.8), (12, 0.9), (16, 1.0), (20, 0.9), (24, 1.0), (26, 0.9), (28, 1.0), (30, 1.0)):
        s.hit('marfa', J.marfa(seed=st, vel=v), 0, st, 1.0)
    for i, st in enumerate(range(16, 32)):
        s.hit('drums', J.snare(seed=st, ghost=i < 8), 0, st, 0.45 + 0.75 * i / 15)
    for i, st in enumerate(range(8, 32, 2)):
        s.hit('tabl', J.tabl(kind='tak' if i % 2 else 'dum', seed=st), 0, st, 0.6 + 0.4 * i / 11, -0.25)
    for st in range(0, 32, 2):
        s.hit('sahn', J.sahn(seed=st, vel=0.8), 0, st, 1.0, 0.45)
    stabs(s, 0, [(16, 0.9)], ('D4', 'A4', 'D5'), dur=0.3)
    stabs(s, 0, [(22, 0.9)], ('F4', 'A4', 'D5'), dur=0.3)
    stabs(s, 0, [(28, 1.0), (30, 1.0)], ('A4', 'D5', 'F5'), dur=0.14)
    melody(s, 'lead', 0, [(4, 1.5, 'D5', 'F5'), (5.5, 0.5, 'A4', None), (6, 0.5, 'Bb4', None), (6.5, 0.5, 'D5', None), (7, 1.0, 'F5', 'G5')], seed=3)
    # the landing: everyone on the downbeat of the bar after
    s.hit('marfa', J.marfa(seed=99), 2, 0, 1.2)
    s.hit('drums', J.kick(seed=98), 2, 0, 1.0)
    s.hit('drums', J.snare(seed=97), 2, 0, 0.9)
    stabs(s, 2, [(0, 1.0)], ('D4', 'A4', 'D5'), dur=0.5)
    s.hit('lyre', J.strum([H('D4'), H('A4'), H('D5'), H('F5')], dur=1.6, seed=5), 2, 0, 1.0, -0.2)
    s.hit('bass', J.bass(H('D2'), dur=0.9, seed=6), 2, 0)
    s.hit('sahn', J.sahn(seed=7, accent=True), 2, 0, 1.6, 0.45)
    melody(s, 'lead', 2, [(0, 1.2, 'D5', None)], seed=8)
    return s


def mission_complete():
    """The same five strings from B flat: bright. Three bars and a last hit."""
    s = Song(150, 3, tail=2.6, seed=37)
    tune = [(0, 0.5, 'Bb4', None), (0.5, 0.5, 'D5', None), (1, 1.0, 'F5', 'G5'), (2, 0.5, 'D5', None), (2.5, 0.5, 'F5', None), (3, 1.0, 'G5', None),
            (4, 0.5, 'A5', None), (4.5, 0.5, 'G5', None), (5, 1.0, 'F5', None), (6, 0.5, 'D5', None), (6.5, 0.5, 'F5', None), (7, 0.5, 'G5', None), (7.5, 0.5, 'A5', None),
            (8, 2.5, 'Bb5', 'D6')]
    melody(s, 'lead', 0, tune, seed=4)
    low = [(b, d, {'Bb4': 'F4', 'D5': 'Bb4', 'F5': 'D5', 'G5': 'D5', 'A5': 'F5', 'Bb5': 'F5'}.get(nm, nm), None) for (b, d, nm, g) in tune]
    melody(s, 'lead2', 0, low, seed=6, p=0.3)
    chords = [('D4', 'F4', 'Bb4'), ('G4', 'Bb4', 'D5'), ('D4', 'F4', 'Bb4')]
    roots = ['Bb1', 'G1', 'Bb1']
    for bar in range(3):
        for st in (0, 4, 8, 12):
            s.hit('drums', J.kick(seed=bar * 16 + st), bar, st)
            s.hit('marfa', J.marfa(seed=bar * 16 + st, vel=0.9), bar, st, 0.9)
        for st in (4, 12):
            s.hit('drums', J.snare(seed=bar * 16 + st + 1), bar, st)
        for st in range(16):
            s.hit('drums', J.snare(seed=bar * 16 + st + 30, ghost=True), bar, st, 0.5)
            s.hit('sahn', J.sahn(seed=bar * 16 + st, vel=0.9 if st % 4 == 2 else 0.5), bar, st, 1.0, 0.45)
        lyre_strums(s, bar, chords[bar], steps=(0, 4, 8, 12), light=(2, 6, 10, 14))
        bass_line(s, bar, [roots[bar], None, roots[bar], roots[bar], None, roots[bar], roots[bar][:-1] + '2', roots[bar]])
        for st in (4, 12):
            s.hit('sahn', J.clap(seed=bar * 16 + st), bar, st, 1.6, 0.1)
    stabs(s, 0, [(0, 1.0)], ('Bb3', 'F4', 'Bb4'), dur=0.3)
    stabs(s, 1, [(0, 0.9), (8, 0.9)], ('G3', 'D4', 'G4'), dur=0.25)
    stabs(s, 2, [(0, 1.0)], ('Bb3', 'F4', 'Bb4'), dur=0.9)
    # the last word: two hits and a ringing chord
    for st, v in ((10, 0.9), (12, 1.0)):
        stabs(s, 2, [(st, v)], ('Bb3', 'F4', 'Bb4', 'D5'), dur=0.12)
        s.hit('drums', J.kick(seed=st), 2, st)
        s.hit('drums', J.snare(seed=st + 1), 2, st)
        s.hit('marfa', J.marfa(seed=st), 2, st, 1.1)
    s.hit('lyre', J.strum([H('Bb3'), H('D4'), H('F4'), H('Bb4'), H('D5')], dur=2.0, vel=1.0, seed=8), 2, 12, 1.2, -0.2)
    s.hit('sahn', J.sahn(seed=9, accent=True), 2, 12, 1.8, 0.45)
    s.hit('bass', J.bass(H('Bb1'), dur=1.2, seed=10), 2, 12)
    return s


JINGLE_LEVELS = dict(drums=-19.0, marfa=-20.5, tabl=-24.0, sahn=-29.0, bass=-19.5, lyre=-22.5, lead=-18.0, lead2=-24.5,
                     brass=-20.5, tunk=-27.0)
SENDS = STRAIT_SENDS


# ---------------------------------------------------------------- the home screen and the map
# The main theme, "Bab al-Yemen": the same five strings from D, but a tune that climbs where the stage theme's falls,
# to the A at the top and the semitone above it. Two arrangements of one tune, so the menus sound like one game:
#   the home screen: the whole band on a 3-3-2 pulse (the big kettledrum on the first, the fourth and the seventh
#     eighth-note: a dotted lilt, my own pattern, as the stage theme's are; I could not source a named one), the mizmar
#     on the tune, brass and an overdriven guitar the second time round, then the flute's verse and a climb back.
#   the map: the same tune as a march (Metal Slug had a march for its briefing screen), lighter, to read by:
#     a snare cadence, the kettledrum on one and three, the qanbus on the beat and the lyre off it, the flute on the
#     tune, the qanbus taking the verse, the mizmar joining the last time through.
THEME = [(0, 1.0, 'D5', None), (1, 0.5, 'A4', None), (1.5, 0.5, 'D5', None), (2, 1.5, 'F5', 'G5'), (3.5, 0.5, 'G5', None),
         (4, 2.5, 'A5', 'Bb5'), (6.5, 0.5, 'G5', None), (7, 1.0, 'F5', None),
         (8, 1.0, 'G5', None), (9, 0.5, 'F5', None), (9.5, 0.5, 'D5', None), (10, 1.0, 'F5', None), (11, 0.5, 'G5', None),
         (11.5, 0.5, 'F5', None),
         (12, 3.0, 'D5', 'F5'),
         (16, 1.0, 'D5', None), (17, 0.5, 'A4', None), (17.5, 0.5, 'D5', None), (18, 1.5, 'F5', 'G5'), (19.5, 0.5, 'G5', None),
         (20, 1.5, 'A5', 'Bb5'), (21.5, 0.5, 'Bb5', None), (22, 0.5, 'A5', None), (22.5, 0.5, 'G5', None), (23, 1.0, 'F5', None),
         (24, 0.5, 'G5', None), (24.5, 0.5, 'A5', None), (25, 0.5, 'G5', None), (25.5, 0.5, 'F5', None), (26, 1.0, 'D5', None),
         (27, 0.5, 'Bb4', None), (27.5, 0.5, 'A4', None),
         (28, 3.5, 'D5', 'F5')]
THEME_PROG = ('D', 'Dm', 'Bb', 'D', 'D', 'G', 'A', 'D')
# the verse: from B flat, the bright end of the strings, and back down to the A that leads home
VERSE = [(0, 1.5, 'F5', None), (1.5, 0.5, 'D5', None), (2, 0.5, 'F5', None), (2.5, 0.5, 'G5', None), (3, 1.0, 'A5', None),
         (4, 2.0, 'Bb5', 'D6'), (6, 0.5, 'A5', None), (6.5, 0.5, 'G5', None), (7, 1.0, 'A5', None),
         (8, 1.5, 'F5', None), (9.5, 0.5, 'G5', None), (10, 1.0, 'A5', None), (11, 0.5, 'F5', None), (11.5, 0.5, 'D5', None),
         (12, 0.5, 'G5', None), (12.5, 0.5, 'F5', None), (13, 0.5, 'D5', None), (13.5, 0.5, 'Bb4', None), (14, 2.0, 'A4', 'Bb4'),
         (16, 1.0, 'D5', None), (17, 0.5, 'F5', None), (17.5, 0.5, 'G5', None), (18, 1.5, 'A5', None), (19.5, 0.5, 'Bb5', None),
         (20, 2.0, 'D6', 'F6'), (22, 0.5, 'Bb5', None), (22.5, 0.5, 'A5', None), (23, 1.0, 'G5', None),
         (24, 1.0, 'A5', None), (25, 0.5, 'G5', None), (25.5, 0.5, 'F5', None), (26, 1.0, 'G5', None), (27, 1.0, 'A5', None),
         (28, 1.0, 'Bb5', None), (29, 1.5, 'A5', 'Bb5')]
VERSE_PROG = ('Bb', 'G', 'Dm', 'A', 'Bb', 'G', 'A', 'A')
BELOW.update({'Bb5': 'G5', 'D6': 'A5', 'F6': 'D6'})
# the second pipe under the main theme: a third or a fourth below, never the B flat against the lyre's A
THEME_BELOW = dict(BELOW, F5='D5')

# the home screen's bass: on the 3-3-2, with a pickup into the next bar. (step, note, length in seconds, strength)
TITLE_BASS = {
    'D': [(0, 'D2', 0.42, 1.0), (6, 'D2', 0.32, 0.85), (10, 'A1', 0.2, 0.7), (12, 'D2', 0.3, 0.9), (14, 'F2', 0.2, 0.75)],
    'Dm': [(0, 'D2', 0.42, 1.0), (6, 'D2', 0.32, 0.85), (10, 'F2', 0.2, 0.7), (12, 'G2', 0.3, 0.9), (14, 'A2', 0.2, 0.75)],
    'Bb': [(0, 'Bb1', 0.42, 1.0), (6, 'Bb1', 0.32, 0.85), (10, 'F2', 0.2, 0.7), (12, 'Bb1', 0.3, 0.9), (14, 'D2', 0.2, 0.75)],
    'G': [(0, 'G1', 0.42, 1.0), (6, 'G1', 0.32, 0.85), (10, 'D2', 0.2, 0.7), (12, 'G2', 0.3, 0.9), (14, 'F2', 0.2, 0.75)],
    'A': [(0, 'A1', 0.42, 1.0), (6, 'A1', 0.32, 0.85), (10, 'A2', 0.2, 0.7), (12, 'G2', 0.3, 0.9), (14, 'F2', 0.2, 0.75)],
}


def title_groove(s, bar, vol=1.0, fill=None, claps=False):
    """One bar on the 3-3-2: kettledrum and kick on the first, fourth and seventh eighth, a backbeat over it."""
    sd = int(bar * 137)
    for st, v in ((0, 1.0), (6, 0.8), (12, 0.72)):
        s.hit('marfa', J.marfa(seed=sd + st, vel=v), bar, st, vol)
        s.hit('drums', J.kick(seed=sd + st), bar, st, (0.95 if st == 0 else 0.75) * vol)
    for st in (4, 12):
        s.hit('drums', J.snare(seed=sd + st), bar, st, 0.95 * vol)
    for st in (7, 10, 15):
        s.hit('drums', J.snare(seed=sd + st, ghost=True), bar, st, 0.6 * vol)
    # the two-headed drum: the dotted pattern in its low stroke, the high one filling the gaps
    for st in (0, 6):
        s.hit('tabl', J.tabl(kind='dum', seed=sd + st), bar, st, 0.95 * vol, -0.3)
    for st in ((3, 9, 12, 14) if bar % 2 == 0 else (3, 9, 11, 12, 14)):
        s.hit('tabl', J.tabl(kind='tak', seed=sd + st), bar, st, (0.85 if st == 12 else 0.6) * vol, -0.25)
    for st in range(0, 16, 2):
        s.hit('sahn', J.sahn(seed=sd + st, vel=1.0 if st % 4 == 2 else 0.5), bar, st, vol, 0.6, human=0.003)
    for st in (4, 12):
        s.hit('sahn', J.jingle(seed=sd + st), bar, st, 0.8 * vol, -0.6)
    if claps:
        for st in (4, 12):
            s.hit('sahn', J.clap(seed=sd + st), bar, st, 1.5 * vol, 0.1)
            s.hit('sahn', J.clap(seed=sd + st + 500), bar, st, 1.2 * vol, -0.3, human=0.01)
    if fill == 'call':
        # the small kettledrums answer at the end of a line
        for i, st in enumerate((10, 11, 13, 14, 15)):
            s.hit('tunk', J.tunk(seed=sd + 70 + st, pitch=(392, 349, 330, 294, 262)[i]), bar, st, 0.95 * vol, 0.35)
    elif fill == 'roll':
        for i, st in enumerate(range(8, 16)):
            s.hit('drums', J.snare(seed=sd + 50 + st, ghost=i < 3), bar, st, (0.6 + 0.55 * i / 7) * vol)
        for i, st in enumerate((12, 13, 14, 15)):
            s.hit('tunk', J.tunk(seed=sd + 90 + st, pitch=(262, 294, 330, 392)[i]), bar, st, 1.0 * vol, 0.35)


def title_bass(s, bar, chord, chug=False, vol=1.0):
    for st, nm, ln, v in TITLE_BASS[chord]:
        f = H(nm)
        s.hit('bass', J.bass(f, dur=ln, vel=v, seed=bar * 16 + st), bar, st, vol)
        if chug:
            s.hit('guitar', J.chug(f * 2, dur=ln * 0.8, vel=v, seed=bar * 16 + st), bar, st, vol, 0.6)
            s.hit('guitar', J.chug(f * 2, dur=ln * 0.8, vel=v, seed=bar * 16 + st + 400), bar, st, vol * 0.9, -0.6, human=0.008)


def title_theme():
    """The home screen: 24 bars at 126, the tune twice and the verse."""
    s = Song(126, 24, seed=71)
    # the tune, the band behind it
    for i in range(8):
        ch = THEME_PROG[i]
        title_groove(s, i, fill='call' if i == 3 else ('roll' if i == 7 else None))
        title_bass(s, i, ch)
        lyre_strums(s, i, LYRE[ch], steps=(2, 6, 10, 14), light=(9,), vol=0.9)
    melody(s, 'lead', 0, THEME, seed=101)
    # again, bigger: a second pipe below it, the brass answering, the guitar under the bass, hands clapping
    for i in range(8):
        bar = 8 + i
        ch = THEME_PROG[i]
        title_groove(s, bar, fill='call' if i == 3 else ('roll' if i == 7 else None), claps=True)
        title_bass(s, bar, ch, chug=True)
        lyre_strums(s, bar, LYRE[ch], steps=(2, 6, 10, 14), light=(9,), vol=0.9)
    melody(s, 'lead', 8, THEME, seed=102)
    melody(s, 'lead2', 8, [(b, d, THEME_BELOW.get(nm, nm), None) for (b, d, nm, g) in THEME], seed=103, p=0.4)
    stabs(s, 11, [(0, 0.8), (6, 0.8), (12, 1.0)], ('A3', 'D4', 'A4'), dur=0.2)
    stabs(s, 15, [(6, 0.9), (12, 1.0)], ('D4', 'A4', 'D5'), dur=0.2)
    stabs(s, 15, [(14, 1.0)], ('F4', 'A4', 'D5'), dur=0.14)
    # the verse: the flute from B flat over the strings, the drums at half the weight; then the climb back
    for i in range(8):
        bar = 16 + i
        ch = VERSE_PROG[i]
        if i < 6:
            s.hit('marfa', J.marfa(seed=bar * 7, vel=0.9), bar, 0, 0.9)
            s.hit('marfa', J.marfa(seed=bar * 7 + 1, vel=0.6), bar, 6, 0.6)
            s.hit('drums', J.snare(seed=bar * 7 + 2), bar, 8, 0.7)
            for st in (0, 6):
                s.hit('tabl', J.tabl(kind='dum', seed=bar * 7 + st), bar, st, 0.7, -0.3)
            for st in (3, 9, 12):
                s.hit('tabl', J.tabl(kind='tak', seed=bar * 7 + st), bar, st, 0.5, -0.25)
            for st in range(0, 16, 2):
                s.hit('sahn', J.sahn(seed=bar * 7 + st, vel=0.8 if st % 4 == 2 else 0.4), bar, st, 0.9, 0.6, human=0.003)
            lyre_arp(s, bar, LYRE[ch], vol=0.9)
            root = {'Bb': 'Bb1', 'G': 'G1', 'Dm': 'D2', 'A': 'A1'}[ch]
            s.hit('bass', J.bass(H(root), dur=0.9, vel=0.9, seed=bar), bar, 0)
            s.hit('bass', J.bass(H(root), dur=0.35, vel=0.75, seed=bar + 3), bar, 6)
            s.hit('bass', J.bass(H(root) * 2, dur=0.3, vel=0.7, seed=bar + 5), bar, 12)
        else:
            # the climb: the 3-3-2 in everything, the brass on it, a roll into the top
            title_groove(s, bar, fill='roll' if i == 7 else None)
            for st in (0, 6, 12):
                s.hit('bass', J.bass(H('A1'), dur=0.3, vel=1.0, seed=bar + st), bar, st)
                s.hit('guitar', J.chug(H('A2'), dur=0.3, vel=1.0, seed=bar + st, open_=True), bar, st, 0.9, 0.3)
                s.hit('guitar', J.chug(H('A2'), dur=0.3, vel=1.0, seed=bar + st + 400, open_=True), bar, st, 0.75, -0.5)
            stabs(s, bar, [(0, 1.0), (6, 0.9), (12, 1.0)], ('G4', 'A4', 'D5'), dur=0.22)
            lyre_strums(s, bar, LYRE['A'], steps=(0, 6, 12), light=())
    melody(s, 'flute', 16, VERSE, voice='flute', seed=105, p=0.15)
    melody(s, 'lead2', 22, [(b - 24, d, nm, g) for (b, d, nm, g) in VERSE if b >= 24], seed=106, p=-0.3, vol=0.8)
    return s


TITLE_LEVELS = dict(drums=-20.0, marfa=-22.0, tabl=-25.0, tunk=-27.5, sahn=-31.0, bass=-19.0, lyre=-22.5,
                    lead=-17.5, lead2=-24.0, flute=-18.5, guitar=-25.0, brass=-22.0)


# the map's march: the qanbus on the beat (root and fifth), the lyre off it
MARCH_BASS = {'D': ('D2', 'A1'), 'Dm': ('D2', 'A1'), 'Bb': ('Bb1', 'F2'), 'G': ('G1', 'D2'), 'A': ('A1', 'D2')}
WALK = {'D': ('F2', 'G2'), 'Dm': ('F2', 'G2'), 'Bb': ('A1', 'Bb1'), 'G': ('A1', 'Bb1'), 'A': ('G2', 'F2')}


def march_drums(s, bar, vol=1.0, roll=False, light=False):
    sd = int(bar * 149)
    s.hit('marfa', J.marfa(seed=sd, vel=1.0), bar, 0, vol)
    s.hit('marfa', J.marfa(seed=sd + 1, vel=0.65), bar, 8, 0.75 * vol)
    # the snare cadence: accents on the beat, the wires filling in between
    if roll:
        pat = [(0, 0.9), (4, 0.55), (8, 0.6), (9, 0.4), (10, 0.5), (11, 0.55), (12, 0.65), (13, 0.75), (14, 0.85), (15, 1.0)]
    elif light:
        pat = [(0, 0.6), (4, 0.4), (8, 0.55), (12, 0.4), (14, 0.3)]
    elif bar % 2 == 0:
        pat = [(0, 0.9), (2, 0.3), (4, 0.55), (6, 0.3), (7, 0.4), (8, 0.8), (10, 0.3), (12, 0.55), (14, 0.3), (15, 0.45)]
    else:
        pat = [(0, 0.9), (3, 0.45), (4, 0.55), (6, 0.35), (8, 0.8), (11, 0.45), (12, 0.55), (14, 0.4), (15, 0.4)]
    for st, v in pat:
        s.hit('drums', J.snare(seed=sd + st, ghost=v < 0.5), bar, st, (v if v >= 0.5 else v * 1.6) * vol)
    for st in (4, 12):
        s.hit('tabl', J.tabl(kind='tak', seed=sd + st), bar, st, 0.5 * vol, -0.25)
    for st in range(0, 16, 2):
        s.hit('sahn', J.sahn(seed=sd + st, vel=0.8 if st % 8 == 4 else 0.4), bar, st, 0.85 * vol, 0.6, human=0.003)


def march_band(s, bar, chord, walk=False, vol=1.0):
    root, fifth = MARCH_BASS[chord]
    s.hit('bass', J.bass(H(root), dur=0.38, vel=1.0, seed=bar * 4), bar, 0, vol)
    s.hit('bass', J.bass(H(fifth), dur=0.38, vel=0.85, seed=bar * 4 + 1), bar, 8, vol)
    if walk:
        w1, w2 = WALK[chord]
        s.hit('bass', J.bass(H(w1), dur=0.2, vel=0.7, seed=bar * 4 + 2), bar, 12, vol)
        s.hit('bass', J.bass(H(w2), dur=0.2, vel=0.75, seed=bar * 4 + 3), bar, 14, vol)
    fr = [H(c) for c in LYRE[chord]]
    for st in (4, 12):
        s.hit('lyre', J.strum(fr, dur=0.28, vel=0.75, up=st == 12, seed=bar * 16 + st), bar, st, 0.85 * vol, -0.45)


def map_march():
    """The map: 24 bars at 112, the tune on the flute, the verse on the qanbus, the tune again with the mizmar."""
    s = Song(112, 24, seed=83)
    for i in range(8):
        ch = THEME_PROG[i]
        march_drums(s, i, roll=(i == 7), light=(i < 2))
        march_band(s, i, ch, walk=(i in (3, 7)))
        if i == 3:
            for k, st in enumerate((12, 13, 14, 15)):
                s.hit('tunk', J.tunk(seed=200 + st, pitch=(294, 330, 349, 392)[k]), i, st, 0.8, 0.35)
    melody(s, 'flute', 0, THEME, voice='flute', seed=111, p=0.1)
    # the verse: the qanbus plays it, the snare eases off, the lyre rolls its chords
    for i in range(8):
        bar = 8 + i
        ch = VERSE_PROG[i]
        march_drums(s, bar, light=True, roll=(i == 7))
        march_band(s, bar, ch, walk=(i in (3, 7)), vol=0.9)
        lyre_arp(s, bar, LYRE[ch], vol=0.45)
    for (b, d, nm, g) in VERSE:
        bar, beat = 8 + int(b // 4), b % 4
        st = beat * 4
        f = H(nm) / 2                       # the lute plays it an octave below the flute
        s.hit('qanbus', J.qanbus(f, dur=min(1.2, d * s.beat * 0.95), vel=0.95 if d >= 1 else 0.8, seed=int(b * 2)), bar, st, 1.0, 0.2)
        if d >= 1.5:
            # a long note on the lute is a tremolo: pick it again and again
            n = int(d * 4) - 1
            for k in range(1, n):
                s.hit('qanbus', J.qanbus(f, dur=0.16, vel=0.55, seed=int(b * 2) + k), bar, st + k, 0.8, 0.2, human=0.002)
    # the tune again: the mizmar, the flute a pipe below it, the brass at the ends of the lines
    for i in range(8):
        bar = 16 + i
        ch = THEME_PROG[i]
        march_drums(s, bar, roll=(i == 7))
        march_band(s, bar, ch, walk=(i in (3, 7)))
    melody(s, 'lead', 16, THEME, seed=113, vol=0.85)
    melody(s, 'flute', 16, [(b, d, THEME_BELOW.get(nm, nm), None) for (b, d, nm, g) in THEME], voice='flute', seed=114, p=-0.25, vol=0.8)
    stabs(s, 19, [(8, 0.7), (12, 0.8)], ('A3', 'D4', 'A4'), dur=0.18, vol=0.8)
    stabs(s, 23, [(8, 0.75), (12, 0.85), (14, 0.9)], ('D4', 'A4', 'D5'), dur=0.16, vol=0.8)
    return s


MAP_LEVELS = dict(drums=-22.5, marfa=-23.0, tabl=-28.0, tunk=-28.5, sahn=-33.0, bass=-19.0, lyre=-24.0, qanbus=-21.5,
                  lead=-19.0, flute=-19.0, brass=-23.5)
MENU_SENDS = dict(STRAIT_SENDS, qanbus=0.18)


# ---------------------------------------------------------------- The Coffee Port (build 12)
# The same five strings, read from F this time: F G A Bb D, with the A for its bright third. A port at work and the
# whole country waiting for its coffee: a swung dance (each beat split in three), claps on two and four, the copper
# tray riding the shuffle, a qanbus walking the bass, the mizmar on a tune that bounces up the strings and back; the
# flute's bridge over a half-time groove, a break where the tray and the claps carry it alone, and the band all in at
# the end. The Big Roaster's theme is from G (G A Bb D F): the dark minor with the A-Bb semitone as its alarm, a
# chugging riff, the drums doubled, the small kettledrums clanking three against four like the drum going round, and
# a steam whistle in the break.
TRIP = 4.0 / 3.0           # one swung eighth, in sixteenth-note steps
MOCHA_LYRE = {'F': ('F4', 'A4', 'F5'), 'Bb': ('D4', 'F4', 'Bb4'), 'Gm': ('G4', 'Bb4', 'D5'), 'Dm': ('D4', 'F4', 'A4')}
MOCHA_ROOT = {'F': ('F1', 'C2'), 'Bb': ('Bb1', 'F2'), 'Gm': ('G1', 'D2'), 'Dm': ('D2', 'A1')}
MOCHA_WALK = {'F': ('F1', 'A1', 'Bb1', 'A1'), 'Bb': ('Bb1', 'D2', 'F2', 'D2'), 'Gm': ('G1', 'Bb1', 'D2', 'Bb1'), 'Dm': ('D2', 'F2', 'A1', 'F2')}


def swing_groove(s, bar, kind='A', vol=1.0, fill=None, claps=True):
    """One bar of the port's dance: kick and kettledrum on one and three with a push before three, claps on two and
    four, the tray riding the shuffle (the first and the last third of each beat), the two-headed drum between."""
    sd = int(bar * 149)
    if kind in ('A', 'full'):
        for beat, v in ((0, 1.0), (2, 0.85)):
            s.hit('drums', J.kick(seed=sd + beat), bar, beat * 4, v * vol)
            s.hit('marfa', J.marfa(seed=sd + beat, vel=v), bar, beat * 4, v * vol)
        s.hit('marfa', J.marfa(seed=sd + 7, vel=0.7), bar, 4 + 2 * TRIP, 0.7 * vol)            # the push into three
        if bar % 2 == 1:
            s.hit('drums', J.kick(seed=sd + 9), bar, 12 + 2 * TRIP, 0.6 * vol)
        for beat in (1, 3):
            s.hit('drums', J.snare(seed=sd + 20 + beat), bar, beat * 4, 0.85 * vol)
            if claps:
                s.hit('sahn', J.clap(seed=sd + beat), bar, beat * 4, 1.5 * vol, 0.15)
                s.hit('sahn', J.clap(seed=sd + beat + 500), bar, beat * 4, 1.2 * vol, -0.3, human=0.01)
        for beat in range(4):
            s.hit('sahn', J.sahn(seed=sd + beat * 3, vel=1.0 if beat % 2 == 0 else 0.8), bar, beat * 4, vol, 0.6, human=0.003)
            s.hit('sahn', J.sahn(seed=sd + beat * 3 + 1, vel=0.55), bar, beat * 4 + 2 * TRIP, vol, 0.6, human=0.003)
            s.hit('tabl', J.tabl(kind='tak', seed=sd + beat * 5), bar, beat * 4 + 2 * TRIP, 0.6 * vol, -0.25)
        for beat in (0, 2):
            s.hit('tabl', J.tabl(kind='dum', seed=sd + beat), bar, beat * 4, 0.9 * vol, -0.3)
        if kind == 'full':
            for beat in range(4):
                s.hit('tunk', J.tunk(seed=sd + 60 + beat, pitch=330.0 if beat % 2 == 0 else 262.0, vel=0.7), bar, beat * 4 + TRIP, 0.7 * vol, 0.5)
    elif kind == 'half':
        s.hit('marfa', J.marfa(seed=sd, vel=0.9), bar, 0, 0.9 * vol)
        s.hit('drums', J.kick(seed=sd), bar, 0, 0.8 * vol)
        s.hit('drums', J.snare(seed=sd + 3), bar, 8, 0.7 * vol)
        s.hit('tabl', J.tabl(kind='dum', seed=sd + 1), bar, 0, 0.8 * vol, -0.25)
        for beat in range(4):
            s.hit('sahn', J.sahn(seed=sd + beat, vel=0.7), bar, beat * 4, vol, 0.6, human=0.003)
            s.hit('tabl', J.tabl(kind='tak', seed=sd + beat + 9), bar, beat * 4 + 2 * TRIP, 0.45 * vol, -0.25)
    elif kind == 'break':
        # only the tray and the hands: the grinder going round
        for beat in range(4):
            for k in range(3):
                s.hit('sahn', J.sahn(seed=sd + beat * 3 + k, vel=1.0 if k == 0 else 0.6), bar, beat * 4 + k * TRIP, vol, 0.6, human=0.003)
        for beat in (1, 3):
            s.hit('sahn', J.clap(seed=sd + beat), bar, beat * 4, 1.6 * vol, 0.15)
            s.hit('sahn', J.clap(seed=sd + beat + 500), bar, beat * 4, 1.3 * vol, -0.3, human=0.01)
        s.hit('tabl', J.tabl(kind='dum', seed=sd), bar, 0, 0.9 * vol, -0.3)
    if fill == 'call':
        for i, st in enumerate((12, 12 + TRIP, 12 + 2 * TRIP, 15)):
            s.hit('tunk', J.tunk(seed=sd + 80 + i, pitch=(294, 330, 349, 392)[i]), bar, st, 1.0 * vol, 0.35)
    elif fill == 'roll':
        for i in range(6):
            s.hit('drums', J.snare(seed=sd + 40 + i, ghost=i < 2), bar, 8 + i * TRIP, (0.6 + 0.5 * i / 5) * vol)
        for i, st in enumerate((12, 12 + TRIP, 12 + 2 * TRIP)):
            s.hit('tunk', J.tunk(seed=sd + 90 + i, pitch=(392, 349, 330)[i]), bar, st, 1.0 * vol, 0.35)


def walk_bass(s, bar, chord, vol=1.0, chug=False):
    """The qanbus walking the bass on the beat, with a swung pickup into each beat after the first."""
    w = MOCHA_WALK[chord]
    for beat in range(4):
        f = H(w[beat])
        s.hit('qanbus', J.qanbus(f, dur=0.36, vel=1.0 if beat % 2 == 0 else 0.8, seed=bar * 8 + beat), bar, beat * 4, vol, -0.15)
        s.hit('bass', J.bass(f, dur=0.28, vel=0.9 if beat % 2 == 0 else 0.75, seed=bar * 8 + beat), bar, beat * 4, vol)
        if beat in (1, 3):
            s.hit('qanbus', J.qanbus(f * 2, dur=0.16, vel=0.55, seed=bar * 8 + beat + 40), bar, beat * 4 + 2 * TRIP, vol, -0.15)
        if chug:
            s.hit('guitar', J.chug(f * 2, dur=0.22, vel=0.9, seed=bar * 8 + beat), bar, beat * 4, vol, 0.6)
            s.hit('guitar', J.chug(f * 2, dur=0.22, vel=0.9, seed=bar * 8 + beat + 400), bar, beat * 4, vol * 0.9, -0.6, human=0.008)


def swing_strums(s, bar, chord, vol=1.0):
    """The lyre off the beat: on the last third of each beat, a lighter one on the middle third of two and four."""
    fr = [H(c) for c in MOCHA_LYRE[chord]]
    for beat in range(4):
        s.hit('lyre', J.strum(fr, dur=0.36, vel=0.85, up=beat % 2 == 1, seed=bar * 16 + beat), bar, beat * 4 + 2 * TRIP, vol, -0.5)
    for beat in (1, 3):
        s.hit('lyre', J.strum(fr[1:], dur=0.22, vel=0.5, up=True, seed=bar * 16 + beat + 8), bar, beat * 4 + TRIP, 0.7 * vol, -0.5)


T3 = 1.0 / 3.0
# the tune: up the strings and back, in swung pairs. (beat from the start of the phrase, beats long, note, grace)
MOCHA_A = [(0, 1, 'A4', None), (1, 2 * T3, 'F4', None), (1 + 2 * T3, T3, 'G4', None), (2, 2 * T3, 'A4', None), (2 + 2 * T3, T3, 'Bb4', None),
           (3, 1, 'D5', 'F5'),
           (4, 2 * T3, 'Bb4', None), (4 + 2 * T3, T3, 'A4', None), (5, 1, 'G4', None), (6, 1.5, 'F4', 'G4'),
           (8, 2 * T3, 'A4', None), (8 + 2 * T3, T3, 'Bb4', None), (9, 2 * T3, 'D5', None), (9 + 2 * T3, T3, 'F5', None), (10, 1, 'G5', 'A5'),
           (11, 2 * T3, 'F5', None), (11 + 2 * T3, T3, 'D5', None),
           (12, 2.5, 'F5', 'G5')]
MOCHA_B = [(0, 1, 'A4', None), (1, 2 * T3, 'F4', None), (1 + 2 * T3, T3, 'G4', None), (2, 2 * T3, 'A4', None), (2 + 2 * T3, T3, 'Bb4', None),
           (3, 1, 'D5', None),
           (4, 2 * T3, 'F5', None), (4 + 2 * T3, T3, 'G5', None), (5, 1, 'A5', 'Bb5'), (6, 2 * T3, 'G5', None), (6 + 2 * T3, T3, 'F5', None),
           (7, 1, 'D5', None),
           (8, 2 * T3, 'Bb4', None), (8 + 2 * T3, T3, 'D5', None), (9, 1, 'G4', None), (10, 2 * T3, 'A4', None), (10 + 2 * T3, T3, 'G4', None),
           (11, 1, 'F4', None),
           (12, 2.5, 'F4', 'G4')]
MOCHA_PROG_A = ('F', 'Bb', 'Gm', 'F')
MOCHA_PROG_B = ('F', 'Dm', 'Gm', 'F')
# the second pipe a string or two below
MOCHA_BELOW = {'A4': 'F4', 'F4': 'D4', 'G4': 'D4', 'Bb4': 'G4', 'D5': 'Bb4', 'F5': 'D5', 'G5': 'D5', 'A5': 'F5', 'Bb5': 'G5'}


def mocha_tune(s, bar0, second=False, vol=1.0):
    melody(s, 'lead', bar0, MOCHA_A, seed=bar0 + 1, vol=vol)
    melody(s, 'lead', bar0 + 4, MOCHA_B, seed=bar0 + 2, vol=vol)
    if second:
        for off, ph in ((0, MOCHA_A), (4, MOCHA_B)):
            low = [(b, d, MOCHA_BELOW.get(nm, nm), None) for (b, d, nm, g) in ph]
            melody(s, 'lead2', bar0 + off, low, seed=bar0 + off + 9, vol=vol, p=0.4)


def mocha_theme():
    """The Coffee Port: 32 bars at 132, swung."""
    s = Song(132, 32, seed=83)
    # the tune with the band behind it
    for i in range(8):
        bar = i
        ch = (MOCHA_PROG_A + MOCHA_PROG_B)[i]
        swing_groove(s, bar, 'A', fill='call' if i == 3 else ('roll' if i == 7 else None))
        walk_bass(s, bar, ch)
        swing_strums(s, bar, ch)
    mocha_tune(s, 0)
    # again, a second pipe under it and the brass answering at the ends of lines
    for i in range(8):
        bar = 8 + i
        ch = (MOCHA_PROG_A + MOCHA_PROG_B)[i]
        swing_groove(s, bar, 'full', fill='call' if i == 3 else ('roll' if i == 7 else None))
        walk_bass(s, bar, ch)
        swing_strums(s, bar, ch)
    mocha_tune(s, 8, second=True)
    stabs(s, 11, [(12, 0.9), (12 + TRIP, 0.8), (12 + 2 * TRIP, 1.0)], ('F4', 'A4', 'F5'))
    stabs(s, 15, [(8, 0.9), (12, 1.0)], ('F4', 'A4', 'F5'), dur=0.3)
    # the bridge: half time, the flute over the lyre picked out, then the tray and the hands on their own
    prog = ('Bb', 'F', 'Gm', 'Dm', 'Bb', 'F')
    for i in range(6):
        bar = 16 + i
        swing_groove(s, bar, 'half')
        ch = prog[i]
        fr = [H(c) for c in MOCHA_LYRE[ch]]
        for k, idx in enumerate((0, 1, 2, 1)):
            s.hit('lyre', J.lyre(fr[idx], dur=0.9, vel=0.75 if k == 0 else 0.55, seed=bar * 8 + k), bar, k * 4, 1.0, -0.5)
        root = MOCHA_ROOT[ch]
        s.hit('qanbus', J.qanbus(H(root[0]), dur=0.9, vel=0.9, seed=bar), bar, 0, 1.0, -0.15)
        s.hit('bass', J.bass(H(root[0]), dur=1.0, vel=0.85, seed=bar), bar, 0)
        s.hit('qanbus', J.qanbus(H(root[1]), dur=0.4, vel=0.6, seed=bar + 3), bar, 8 + 2 * TRIP, 1.0, -0.15)
    melody(s, 'flute', 16, [(0, 1.5, 'D5', 'F5'), (1.5, 0.5, 'Bb4', None), (2, 1, 'A4', None), (3, 1, 'F4', None),
                            (4, 2, 'A4', 'Bb4'), (6, 1, 'G4', None), (7, 1, 'A4', None),
                            (8, 1.5, 'Bb4', None), (9.5, 0.5, 'D5', None), (10, 1, 'G5', None), (11, 1, 'F5', None),
                            (12, 2, 'D5', 'F5'), (14, 1, 'A4', None), (15, 1, 'Bb4', None),
                            (16, 1.5, 'D5', None), (17.5, 0.5, 'F5', None), (18, 1, 'G5', 'A5'), (19, 1, 'F5', None),
                            (20, 3.5, 'F5', 'G5')], voice='flute', seed=7, p=0.15)
    for i in range(2):
        bar = 22 + i
        swing_groove(s, bar, 'break', fill='roll' if i == 1 else None)
    # all in: the tune again with claps, brass and the overdriven guitar under the walk
    for i in range(8):
        bar = 24 + i
        ch = (MOCHA_PROG_A + MOCHA_PROG_B)[i]
        swing_groove(s, bar, 'full', fill='call' if i == 3 else ('roll' if i == 7 else None))
        walk_bass(s, bar, ch, chug=True)
        swing_strums(s, bar, ch)
    mocha_tune(s, 24, second=True)
    stabs(s, 27, [(12, 0.9), (12 + TRIP, 0.8), (12 + 2 * TRIP, 1.0)], ('F4', 'A4', 'F5'))
    stabs(s, 31, [(4, 0.9), (8, 0.9), (12, 1.0)], ('F4', 'A4', 'F5'), dur=0.3)
    return s


MOCHA_LEVELS = dict(drums=-21.0, marfa=-23.0, tabl=-25.0, tunk=-28.0, sahn=-28.5, bass=-21.5, qanbus=-21.0, lyre=-22.5,
                    lead=-18.0, lead2=-24.5, flute=-19.5, guitar=-24.0, brass=-22.0)
MOCHA_SENDS = dict(STRAIT_SENDS, qanbus=0.14)


def roaster_theme():
    """The Big Roaster: 16 bars at 168, from G, heavy."""
    s = Song(168, 16, seed=97)
    riff0 = ['G1', 'G1', 'G2', 'G1', 'Bb1', 'G1', 'A1', 'Bb1']
    riff1 = ['G1', 'G1', 'G2', 'G1', 'F1', 'F1', 'G1', 'D2']
    riff2 = ['Bb1', 'Bb1', 'Bb2', 'Bb1', 'A1', 'A1', 'G1', 'A1']
    motif = [(0, 1.5, 'G4', None), (1.5, 0.5, 'Bb4', None), (2, 1.0, 'A4', None), (3, 0.5, 'G4', None), (3.5, 0.5, 'F4', None),
             (4, 2.0, 'G4', 'A4'), (6, 0.5, 'D4', None), (6.5, 0.5, 'F4', None), (7, 1.0, 'G4', None),
             (8, 1.5, 'Bb4', None), (9.5, 0.5, 'A4', None), (10, 1.0, 'D5', 'F5'), (11, 0.5, 'Bb4', None), (11.5, 0.5, 'A4', None),
             (12, 3.0, 'G4', 'A4')]
    high = [(b, d, {'G4': 'G5', 'Bb4': 'Bb5', 'A4': 'A5', 'F4': 'F5', 'D4': 'D5', 'D5': 'D6'}.get(nm, nm), None) for (b, d, nm, g) in motif]
    for i in range(16):
        sect = i // 4
        if sect == 2:
            # the break: the alarm on the semitone, and the steam whistle
            drums_groove(s, i, 'boss', fill='roll' if i == 11 else None)
            for st, nm in ((0, 'A4'), (8, 'Bb4')):
                for k, n2 in enumerate((nm, nm[:-1] + '3')):
                    s.hit('brass', J.brass(H(n2), dur=0.62, vel=1.0, seed=i * 16 + st + k), i, st, 1.0, (-0.3, 0.3)[k])
            s.hit('bass', J.bass(H('A1'), dur=0.5, vel=1.0, seed=i), i, 0)
            s.hit('bass', J.bass(H('Bb1'), dur=0.5, vel=1.0, seed=i + 7), i, 8)
            continue
        drums_groove(s, i, 'boss', fill='roll' if i % 4 == 3 else None)
        riff = (riff0, riff1, riff2, riff1)[i % 4]
        bass_line(s, i, riff, chug=True)
        # the drum going round: the tray clanking on every third sixteenth
        for st in range(16):
            if (i * 16 + st) % 3 == 0:
                s.hit('sahn', J.sahn(seed=i * 16 + st, vel=0.9), i, st, 1.0, 0.5, human=0.002)
        if i % 2 == 1:
            s.hit('lyre', J.strum([H('G4'), H('D5')], dur=0.4, vel=0.9, seed=i), i, 12, 1.0, -0.35)
            s.hit('lyre', J.strum([H('A4'), H('D5')], dur=0.4, vel=0.9, up=True, seed=i + 3), i, 14, 1.0, -0.35)
    melody(s, 'lead', 0, motif, seed=51)
    melody(s, 'lead', 4, motif, seed=52)
    # the steam whistle over the alarm
    melody(s, 'flute', 8, [(0, 1.5, 'A5', None), (2, 1.5, 'Bb5', None), (4, 1.5, 'A5', None), (6, 1.5, 'Bb5', 'D6'),
                           (8, 1.0, 'A5', None), (9, 1.0, 'Bb5', None), (10, 1.0, 'A5', None), (11, 1.0, 'Bb5', None),
                           (12, 3.0, 'D6', None)], voice='flute', seed=9, p=0.2)
    melody(s, 'lead', 12, high, seed=53)
    melody(s, 'lead2', 12, motif, seed=54, p=0.3)
    return s


ROASTER_LEVELS = dict(drums=-18.5, marfa=-21.0, tabl=-25.0, tunk=-25.5, sahn=-28.5, bass=-19.0, lyre=-25.0,
                      lead=-18.5, lead2=-24.0, flute=-20.0, guitar=-21.5, brass=-21.0)


# ---------------------------------------------------------------- the Souq
# The same five strings read from B-flat this time (Bb D F G A): the brightest the strings go, with the A under the
# B-flat to lead home. A market at full tilt: the big kettledrum walking every beat like the crowd, the two-headed drum
# running sixteenths, the tray on the off-beats, claps; the qanbus turning a figure over and over. The tune is a
# haggle: the flute (the Tihama's own) asks for two bars and the mizmar answers for two, the second time round with a
# pipe under each. The bridge drops to half time for the flute, a break for the tray and the hands (one calls, the other
# answers), and then the market's sneeze: three rising band hits with a held breath after them, and the whole band in
# on the next downbeat. The Spice Cannon's theme is from A (A Bb D F G): a heavy plod at 104, the cart's every step a
# boom, the bass grinding A against B-flat, the small kettledrums creaking three against four like a dry axle, the
# mizmar heaving a phrase up the strings that rolls back down; a break where everything stops for breath but the
# panting flute, and the tune again an octave up with the band behind it.
SOUQ_LYRE = {'Bb': ('D4', 'F4', 'Bb4'), 'F': ('F4', 'A4', 'F5'), 'Gm': ('G4', 'Bb4', 'D5'), 'Dm': ('D4', 'F4', 'A4')}
SOUQ_FIG = {'Bb': ('Bb1', 'Bb2', 'F2', 'Bb2'), 'F': ('F1', 'F2', 'A1', 'F2'), 'Gm': ('G1', 'G2', 'D2', 'G2'),
            'Dm': ('D2', 'D3', 'A2', 'D3')}
SOUQ_PROG = ('Bb', 'F', 'Gm', 'F', 'Bb', 'F', 'Gm', 'Bb')


def souq_groove(s, bar, kind='A', vol=1.0, fill=None):
    """One bar of the market: the big kettledrum on every beat (the first and third heavier), kick and backbeat, the
    two-headed drum running sixteenths, the tray on the off-beats, claps on two and four and a pair to end every other
    bar. kind: 'A', 'full' (the small kettledrums too), 'half', 'haggle' (the tray and the hands alone), 'build'."""
    sd = int(bar * 157)
    if kind in ('A', 'full'):
        for beat in range(4):
            v = 1.0 if beat % 2 == 0 else 0.72
            s.hit('marfa', J.marfa(seed=sd + beat, vel=v), bar, beat * 4, v * vol)
        for st in ((0, 8, 10) if bar % 2 == 0 else (0, 7, 8)):
            s.hit('drums', J.kick(seed=sd + st), bar, st, vol)
        for st in (4, 12):
            s.hit('drums', J.snare(seed=sd + 20 + st), bar, st, 0.9 * vol)
        for st in ((3, 11) if bar % 2 == 0 else (3, 11, 14)):
            s.hit('drums', J.snare(seed=sd + 40 + st, ghost=True), bar, st, 0.6 * vol)
        for st in range(16):
            if st % 4 == 0:
                s.hit('tabl', J.tabl(kind='dum', seed=sd + st), bar, st, 0.9 * vol, -0.3)
            else:
                s.hit('tabl', J.tabl(kind='tak', seed=sd + st), bar, st, (0.62 if st % 2 == 0 else 0.42) * vol, -0.25, human=0.003)
        for beat in range(4):
            s.hit('sahn', J.sahn(seed=sd + beat * 2, vel=1.0), bar, beat * 4 + 2, vol, 0.6, human=0.003)
            s.hit('sahn', J.sahn(seed=sd + beat * 2 + 1, vel=0.45), bar, beat * 4, vol, 0.6, human=0.003)
        for st in ((4, 12) if bar % 2 == 0 else (4, 12, 14, 15)):
            s.hit('sahn', J.clap(seed=sd + st), bar, st, 1.5 * vol, 0.15)
            s.hit('sahn', J.clap(seed=sd + st + 500), bar, st, 1.2 * vol, -0.3, human=0.01)
        if kind == 'full':
            for st, pc in ((6, 392.0), (7, 330.0), (14, 349.0)):
                s.hit('tunk', J.tunk(seed=sd + 60 + st, pitch=pc, vel=0.75), bar, st, 0.75 * vol, 0.5)
    elif kind == 'half':
        s.hit('marfa', J.marfa(seed=sd, vel=0.9), bar, 0, 0.9 * vol)
        s.hit('marfa', J.marfa(seed=sd + 1, vel=0.55), bar, 10, 0.6 * vol)
        s.hit('drums', J.kick(seed=sd), bar, 0, 0.8 * vol)
        s.hit('drums', J.snare(seed=sd + 3), bar, 8, 0.7 * vol)
        s.hit('tabl', J.tabl(kind='dum', seed=sd + 1), bar, 0, 0.8 * vol, -0.25)
        for st in (6, 10, 14):
            s.hit('tabl', J.tabl(kind='tak', seed=sd + st), bar, st, 0.5 * vol, -0.25)
        for st in range(0, 16, 2):
            s.hit('sahn', J.sahn(seed=sd + st, vel=0.85 if st % 4 == 2 else 0.45), bar, st, vol, 0.6, human=0.003)
    elif kind == 'haggle':
        # one side calls on the small kettledrums, the hands answer; the tray keeps the time between them
        for st in range(0, 16, 2):
            s.hit('sahn', J.sahn(seed=sd + st, vel=0.9 if st % 4 == 2 else 0.5), bar, st, vol, 0.6, human=0.003)
        s.hit('marfa', J.marfa(seed=sd, vel=0.8), bar, 0, 0.8 * vol)
        for st, pc in ((0, 349.0), (2, 392.0), (3, 349.0)) if bar % 2 == 0 else ((0, 392.0), (1, 349.0), (3, 294.0)):
            s.hit('tunk', J.tunk(seed=sd + 70 + st, pitch=pc, vel=0.9), bar, st, 1.0 * vol, 0.35)
        for st in ((8, 10, 11) if bar % 2 == 0 else (8, 9, 11, 12)):
            s.hit('sahn', J.clap(seed=sd + st), bar, st, 1.6 * vol, 0.15)
            s.hit('sahn', J.clap(seed=sd + st + 500), bar, st, 1.3 * vol, -0.3, human=0.01)
    elif kind == 'build':
        for st in (0, 6, 12):
            s.hit('drums', J.kick(seed=sd + st), bar, st, vol)
            s.hit('marfa', J.marfa(seed=sd + st), bar, st, 0.9 * vol)
        for st in range(16):
            s.hit('drums', J.snare(seed=sd + st, ghost=True), bar, st, (0.45 + 0.6 * st / 16) * vol)
        for st in range(0, 16, 2):
            s.hit('sahn', J.sahn(seed=sd + st, vel=0.8), bar, st, vol, 0.6, human=0.003)
    if fill == 'roll':
        for i, st in enumerate(range(8, 16)):
            s.hit('drums', J.snare(seed=sd + 50 + st, ghost=i < 4), bar, st, (0.7 + 0.5 * i / 7) * vol)
        for i, st in enumerate((10, 11, 13, 14, 15)):
            s.hit('tunk', J.tunk(seed=sd + 80 + st, pitch=(392, 349, 330, 294, 262)[i]), bar, st, 1.0 * vol, 0.35)
    elif fill == 'call':
        for i, st in enumerate((12, 13, 14, 15)):
            s.hit('tunk', J.tunk(seed=sd + 90 + st, pitch=(294, 349, 392, 440)[i]), bar, st, 1.0 * vol, 0.35)


def souq_band(s, bar, chord, vol=1.0, chug=False):
    """The qanbus turning its figure in eighths (root, octave, the next string, octave), the bass on the beat under it,
    the lyre's strums off the beat."""
    fig = [H(n) for n in SOUQ_FIG[chord]]
    for i in range(8):
        f = fig[i % 4]
        s.hit('qanbus', J.qanbus(f * (2 if i % 2 else 1), dur=0.22, vel=1.0 if i % 2 == 0 else 0.7, seed=bar * 8 + i), bar, i * 2, vol, -0.15)
        if i % 2 == 0:
            s.hit('bass', J.bass(fig[0], dur=0.2, vel=0.95 if i % 4 == 0 else 0.8, seed=bar * 8 + i), bar, i * 2, vol)
            if chug:
                s.hit('guitar', J.chug(fig[0] * 2, dur=0.15, vel=0.9, seed=bar * 8 + i), bar, i * 2, vol, 0.6)
                s.hit('guitar', J.chug(fig[0] * 2, dur=0.15, vel=0.9, seed=bar * 8 + i + 400), bar, i * 2, vol * 0.9, -0.6, human=0.008)
    lyre_strums(s, bar, SOUQ_LYRE[chord], vol=vol)


# the haggle: the flute asks, the mizmar answers (beat from the start of the phrase, beats long, note, grace)
SOUQ_CALL = [(0, 0.5, 'F4', None), (0.5, 0.5, 'Bb4', None), (1, 0.5, 'D5', None), (1.5, 0.5, 'F5', None), (2, 1.0, 'D5', 'F5'),
             (3, 1.0, 'Bb4', None),
             (4, 0.5, 'A4', None), (4.5, 0.5, 'F4', None), (5, 0.5, 'A4', None), (5.5, 0.5, 'D5', None), (6, 1.5, 'F5', 'G5'),
             (7.5, 0.5, 'G5', None)]
SOUQ_CALL2 = SOUQ_CALL[:10] + [(6, 1.0, 'A5', 'Bb5'), (7, 0.5, 'G5', None), (7.5, 0.5, 'F5', None)]
SOUQ_ANS = [(0, 1.0, 'G5', None), (1, 0.5, 'F5', None), (1.5, 0.5, 'D5', None), (2, 0.5, 'Bb4', None), (2.5, 0.5, 'D5', None),
            (3, 1.0, 'G4', None),
            (4, 0.5, 'A4', None), (4.5, 0.5, 'Bb4', None), (5, 1.0, 'A4', None), (6, 2.0, 'F4', 'G4')]
SOUQ_ANS2 = [(0, 0.5, 'G4', None), (0.5, 0.5, 'Bb4', None), (1, 0.5, 'D5', None), (1.5, 0.5, 'G5', None), (2, 1.0, 'F5', None),
             (3, 1.0, 'D5', None),
             (4, 0.5, 'A4', None), (4.5, 0.5, 'Bb4', None), (5, 0.5, 'D5', None), (5.5, 0.5, 'A4', None), (6, 2.0, 'Bb4', 'D5')]
# a pipe a string or two under each line, the second time round
SOUQ_BELOW = {'F4': 'D4', 'Bb4': 'F4', 'D5': 'Bb4', 'F5': 'D5', 'G5': 'D5', 'A5': 'F5', 'A4': 'F4', 'G4': 'D4'}


def souq_lines(s, bar0, second=False, vol=1.0):
    for off, ph, voice, stem in ((0, SOUQ_CALL, 'flute', 'flute'), (2, SOUQ_ANS, 'mizmar', 'lead'),
                                 (4, SOUQ_CALL2, 'flute', 'flute'), (6, SOUQ_ANS2, 'mizmar', 'lead')):
        melody(s, stem, bar0 + off, ph, voice=voice, seed=bar0 + off + 1, vol=vol, p=0.12 if voice == 'flute' else 0.0)
        if second:
            low = [(b, d, SOUQ_BELOW.get(nm, nm), None) for (b, d, nm, g) in ph]
            melody(s, 'lead2', bar0 + off, low, seed=bar0 + off + 9, vol=vol, p=-0.35 if voice == 'flute' else 0.4)


def souq_theme():
    """The Souq: 32 bars at 138."""
    s = Song(138, 32, seed=101)
    for i in range(8):
        souq_groove(s, i, 'A', fill='call' if i == 3 else ('roll' if i == 7 else None))
        souq_band(s, i, SOUQ_PROG[i])
    souq_lines(s, 0)
    # again, a pipe under each line, the small kettledrums in, the band answering at the ends of lines
    for i in range(8):
        souq_groove(s, 8 + i, 'full', fill='call' if i == 3 else ('roll' if i == 7 else None))
        souq_band(s, 8 + i, SOUQ_PROG[i])
    souq_lines(s, 8, second=True)
    stabs(s, 11, [(8, 0.9), (10, 0.8), (12, 1.0)], ('F4', 'A4', 'F5'))
    stabs(s, 15, [(10, 0.9), (12, 0.9), (14, 1.0)], ('D4', 'F4', 'Bb4'))
    # the bridge: half time, the lyre picked out, the flute alone over it
    prog = ('Gm', 'Bb', 'Gm', 'F')
    for i in range(4):
        bar = 16 + i
        souq_groove(s, bar, 'half')
        lyre_arp(s, bar, SOUQ_LYRE[prog[i]])
        root = SOUQ_FIG[prog[i]][0]
        s.hit('qanbus', J.qanbus(H(root), dur=0.9, vel=0.9, seed=bar), bar, 0, 1.0, -0.15)
        s.hit('bass', J.bass(H(root), dur=1.1, vel=0.85, seed=bar), bar, 0)
        s.hit('qanbus', J.qanbus(H(root) * 2, dur=0.4, vel=0.6, seed=bar + 3), bar, 10, 1.0, -0.15)
    melody(s, 'flute', 16, [(0, 2, 'D5', None), (2, 1, 'F5', None), (3, 1, 'D5', None), (4, 3, 'Bb4', 'D5'), (7, 1, 'A4', None),
                            (8, 1.5, 'G4', None), (9.5, 0.5, 'Bb4', None), (10, 1, 'D5', None), (11, 1, 'G5', None),
                            (12, 3.5, 'F5', 'G5')], voice='flute', seed=17, p=0.15)
    # the haggle in the hands
    for i in range(2):
        souq_groove(s, 20 + i, 'haggle')
        s.hit('bass', J.bass(H('F1'), dur=0.4, vel=0.8, seed=20 + i), 20 + i, 0)
    # the sneeze: ah... ah... ah... and the band in on the next downbeat
    souq_groove(s, 22, 'build')
    for st in (0, 6, 12):
        s.hit('bass', J.bass(H('F1'), dur=0.3, vel=1.0, seed=22 + st), 22, st)
    for st, ch, v in ((0, ('F4', 'A4', 'F5'), 0.75), (4, ('G4', 'Bb4', 'G5'), 0.88), (8, ('A4', 'D5', 'A5'), 1.0)):
        stabs(s, 23, [(st, v)], ch, dur=0.3)
        s.hit('marfa', J.marfa(seed=230 + st, vel=v), 23, st, v)
        s.hit('drums', J.kick(seed=230 + st), 23, st, v)
    s.hit('tunk', J.tunk(seed=239, pitch=440.0, vel=0.5), 23, 14, 0.5, 0.35)
    # all in: the haggle once more, the pipes doubled, claps, the band, the guitar under the qanbus
    for i in range(8):
        souq_groove(s, 24 + i, 'full', fill='call' if i == 3 else ('roll' if i == 7 else None))
        souq_band(s, 24 + i, SOUQ_PROG[i], chug=True)
    stabs(s, 24, [(0, 1.0)], ('D4', 'F4', 'Bb4'), dur=0.45)
    s.hit('marfa', J.marfa(seed=241, vel=1.0), 24, 0, 1.2)
    souq_lines(s, 24, second=True)
    stabs(s, 27, [(8, 0.9), (10, 0.8), (12, 1.0)], ('F4', 'A4', 'F5'))
    stabs(s, 31, [(4, 0.9), (8, 0.9), (12, 1.0)], ('D4', 'F4', 'Bb4'), dur=0.3)
    return s


SOUQ_LEVELS = dict(drums=-21.0, marfa=-22.5, tabl=-25.0, tunk=-28.0, sahn=-28.5, bass=-21.0, qanbus=-23.5, lyre=-24.0,
                   lead=-18.5, lead2=-24.5, flute=-18.0, guitar=-25.0, brass=-22.0)
SOUQ_SENDS = dict(STRAIT_SENDS, qanbus=0.14, flute=0.30)


CANNON_LYRE = {'A': ('A3', 'D4', 'A4'), 'G': ('G3', 'D4', 'G4'), 'F': ('F3', 'A3', 'F4'), 'Bb': ('D4', 'F4', 'Bb4'),
               'Dm': ('D4', 'F4', 'A4')}


def cannon_theme():
    """The Spice Cannon: 16 bars at 104, from A, heavy and slow."""
    s = Song(104, 16, seed=113)
    plod = (['A1', 'A1', 'Bb1', 'A1'], ['G1', 'G1', 'F1', 'G1'], ['A1', 'A1', 'Bb1', 'D2'], ['F1', 'G1', 'A1', 'A1'])
    chords = ('A', 'G', 'A', 'F')
    heave = [(0, 1.5, 'A4', None), (1.5, 0.5, 'Bb4', None), (2, 2.0, 'A4', None),
             (4, 1.5, 'D5', None), (5.5, 0.5, 'F5', None), (6, 2.0, 'D5', None),
             (8, 1.0, 'F5', None), (9, 1.0, 'G5', None), (10, 0.5, 'F5', None), (10.5, 0.5, 'D5', None), (11, 1.0, 'Bb4', None),
             (12, 0.5, 'A4', None), (12.5, 0.5, 'G4', None), (13, 0.5, 'F4', None), (13.5, 0.5, 'D4', None), (14, 2.0, 'A4', 'Bb4')]
    heave2 = heave[:10] + [(11, 1.0, 'A5', 'Bb5'), (12, 0.5, 'G5', None), (12.5, 0.5, 'F5', None), (13, 0.5, 'D5', None),
                           (13.5, 0.5, 'Bb4', None), (14, 2.0, 'A4', 'Bb4')]
    for i in range(16):
        sd = i * 61
        sect = i // 4
        if sect == 2:
            # everything stops for breath: the kettledrum once, the two-headed drum puffing, the bass holding on
            s.hit('marfa', J.marfa(seed=sd, vel=0.9), i, 0, 0.9)
            s.hit('drums', J.kick(seed=sd), i, 0, 0.8)
            for st in (6, 7, 14, 15):
                s.hit('tabl', J.tabl(kind='tak', seed=sd + st), i, st, 0.7 if st % 2 == 0 else 0.5, -0.25)
            s.hit('tabl', J.tabl(kind='dum', seed=sd + 1), i, 8, 0.6, -0.25)
            root = ('A1', 'G1', 'F1', 'A1')[i % 4]
            s.hit('bass', J.bass(H(root), dur=2.2, vel=0.9, seed=sd), i, 0)
            s.hit('lyre', J.strum([H(n) for n in CANNON_LYRE[chords[i % 4]]], dur=1.4, vel=0.6, seed=sd), i, 0, 0.8, -0.4)
            if i == 11:
                for k, st in enumerate(range(8, 16)):
                    s.hit('drums', J.snare(seed=sd + 50 + st, ghost=k < 4), i, st, 0.7 + 0.5 * k / 7)
            continue
        # the cart's every step: kick and kettledrum on one and three, the backbeat with the brass's low answer
        for st in (0, 8):
            s.hit('drums', J.kick(seed=sd + st), i, st, 1.0)
            s.hit('marfa', J.marfa(seed=sd + st, vel=1.0), i, st, 1.0)
            s.hit('tabl', J.tabl(kind='dum', seed=sd + st), i, st, 0.9, -0.3)
        for st in (4, 12):
            s.hit('drums', J.snare(seed=sd + 20 + st), i, st, 1.0)
            s.hit('marfa', J.marfa(seed=sd + st + 3, vel=0.5), i, st, 0.5)
        for st in (6, 14):
            s.hit('drums', J.kick(seed=sd + st + 9), i, st, 0.55)
        for st in (2, 10):
            s.hit('tabl', J.tabl(kind='tak', seed=sd + st), i, st, 0.6, -0.25)
        # the axle: the small kettledrums creaking three against four
        for st in range(16):
            if (i * 16 + st) % 3 == 0:
                s.hit('tunk', J.tunk(seed=sd + st, pitch=440.0 if ((i * 16 + st) // 3) % 2 else 392.0, vel=0.55), i, st, 0.55, 0.5)
        for st in range(0, 16, 2):
            s.hit('sahn', J.sahn(seed=sd + st, vel=0.8 if st % 4 == 2 else 0.4), i, st, 1.0, 0.6, human=0.003)
        notes = plod[i % 4]
        for k, nm in enumerate(notes):
            f = H(nm)
            s.hit('bass', J.bass(f, dur=0.42, vel=1.0 if k % 2 == 0 else 0.85, seed=sd + k), i, k * 4)
            s.hit('qanbus', J.qanbus(f * 2, dur=0.3, vel=0.8, seed=sd + k), i, k * 4, 1.0, -0.15)
            if k % 2 == 1:
                s.hit('brass', J.brass(f * 2, dur=0.22, vel=0.8, seed=sd + k), i, k * 4, 0.9, -0.2)
                s.hit('brass', J.brass(f * 4, dur=0.22, vel=0.7, seed=sd + k + 5), i, k * 4, 0.6, 0.2)
            if sect == 3:
                s.hit('guitar', J.chug(f * 2, dur=0.3, vel=1.0, seed=sd + k), i, k * 4, 1.0, 0.6)
                s.hit('guitar', J.chug(f * 2, dur=0.3, vel=1.0, seed=sd + k + 400), i, k * 4, 0.9, -0.6, human=0.008)
        lyre_strums(s, i, CANNON_LYRE[chords[i % 4]], steps=(2, 10), light=(6, 14), vol=0.85)
        if i % 4 == 3:
            for k, st in enumerate((12, 13, 14, 15)):
                s.hit('tunk', J.tunk(seed=sd + 80 + st, pitch=(294, 349, 392, 440)[k]), i, st, 0.9, 0.35)
    melody(s, 'lead', 0, heave, seed=61)
    melody(s, 'lead', 4, heave2, seed=62)
    # the pushers getting their breath back, on the flute
    melody(s, 'flute', 8, [(0, 0.5, 'A5', None), (0.75, 0.5, 'G5', None), (2, 0.5, 'A5', None), (2.75, 0.5, 'G5', None),
                           (4, 0.5, 'A5', None), (4.75, 0.5, 'F5', None), (6, 0.5, 'A5', None), (6.75, 0.5, 'F5', None),
                           (8, 0.5, 'Bb5', None), (8.75, 0.5, 'A5', None), (10, 0.5, 'Bb5', None), (10.75, 0.5, 'A5', None),
                           (12, 3.0, 'A5', 'Bb5')], voice='flute', seed=63, p=0.2)
    high = [(b, d, {'A4': 'A5', 'Bb4': 'Bb5', 'D5': 'D6', 'F5': 'F6', 'G5': 'G6', 'G4': 'G5', 'F4': 'F5', 'D4': 'D5', 'A5': 'A6'}.get(nm, nm),
             None) for (b, d, nm, g) in heave]
    melody(s, 'flute', 12, high, voice='flute', seed=64, p=0.15)
    melody(s, 'lead', 12, heave, seed=65)
    stabs(s, 15, [(8, 0.9), (12, 1.0)], ('A3', 'D4', 'A4'), dur=0.3)
    return s


SCALE_LEVELS = CANNON_LEVELS = dict(drums=-18.5, marfa=-20.5, tabl=-25.0, tunk=-28.0, sahn=-30.0, bass=-19.0, qanbus=-23.0, lyre=-24.5,
                     lead=-18.5, flute=-19.5, guitar=-22.0, brass=-21.0)


# build 29: the Great Scale took the Spice Cannon's place in the Souq's covered market, and its music with it
scale_theme = cannon_theme
