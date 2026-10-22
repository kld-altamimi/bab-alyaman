# voice.py - placeholder voices: a small formant synthesiser that babbles.
# What it can carry: who is speaking (pitch, size of the throat), how (pace, range, attitude), and
# the rhythm of a line. What it cannot carry: an accent. A Taizi or Tihami voice needs a person.
# The words are nonsense built from Arabic's sounds, plus a few everyday interjections
# (yalla, la la la, khalas, tamaam) and one place name. No religious phrases, no slogans.
import numpy as np
from scipy import signal
from core import *

# ---------------------------------------------------------------- sounds
# vowels: F1, F2, F3 for an adult man; scaled per speaker
# Arabic's a sits forward in the mouth (nearer "cat" than "father"); after q, kh and the throat sounds it falls back
VOW = {'a': (670, 1560, 2560), 'i': (300, 2240, 2950), 'u': (340, 880, 2300), 'e': (480, 1900, 2600), 'o': (500, 920, 2450)}
A_BACK = (730, 1180, 2500)
BACKING = set('qx37G')
# Persian's, for the Uncle across the water (17 Oct): the back, rounded â; p and v; qâf said soft and voiced
VOW['A'] = (640, 960, 2450)
# consonants: kind, formant target (where the mouth is), and for noisy ones the band of the hiss
CON = {
    'm': ('nasal', (250, 1050, 2250)), 'n': ('nasal', (250, 1650, 2600)),
    'l': ('son', (350, 1250, 2800)), 'r': ('tap', (430, 1350, 1900)),
    'w': ('son', (300, 700, 2300)), 'y': ('son', (270, 2200, 3000)),
    '3': ('ayn', (820, 1150, 2500)),
    'b': ('vstop', (200, 900, 2200), (700, 1200, 0.25)), 'd': ('vstop', (200, 1750, 2700), (4200, 2500, 0.35)),
    'g': ('vstop', (220, 2000, 2250), (1900, 1200, 0.4)), 'j': ('vstop', (230, 2050, 2700), (3200, 1800, 0.7)),
    't': ('stop', (200, 1750, 2700), (4500, 2600, 0.7)), 'k': ('stop', (220, 2000, 2250), (2000, 1300, 0.8)),
    'q': ('stop', (480, 1000, 2400), (1150, 900, 1.0)), "'": ('glottal', None),
    's': ('fric', (300, 1750, 2700), (6200, 3000, 0.55)), 'c': ('fric', (300, 2000, 2600), (3200, 1900, 0.62)),
    'f': ('fric', (300, 1000, 2300), (4500, 6000, 0.22)), 'x': ('fric', (450, 1300, 2400), (1750, 1300, 0.7)),
    '7': ('fric', (700, 1200, 2500), (1150, 1200, 0.5)), 'z': ('vfric', (280, 1750, 2700), (6000, 3000, 0.3)),
    'h': ('h', None),
    'p': ('stop', (200, 900, 2200), (900, 1100, 0.6)), 'v': ('vfric', (300, 1050, 2300), (4800, 6000, 0.16)),
    'G': ('vstop', (480, 1000, 2400), (1150, 900, 0.45)),
    'D': ('vfric', (300, 1500, 2600), (5200, 6000, 0.12)),          # dh (ذ), soft: the tongue between the teeth
}
BLOCK = 64


def parse(text):
    """'ma-*raa-li ca-*ban-du . *haa-di-ku' -> a list of (sound, length factor, stressed) and pauses."""
    out = []
    for tok in text.replace('-', ' ').split():
        if tok in ('.', ',', '!', '?'):
            out.append(('pause', tok, False))
            continue
        stress = tok.startswith('*')
        if stress:
            tok = tok[1:]
        i = 0
        while i < len(tok):
            ch = tok[i]
            j = i
            while j < len(tok) and tok[j] == ch:
                j += 1
            run = j - i
            if ch in VOW:
                out.append((ch, 1.0 if run == 1 else 1.75 + 0.45 * (run - 2), stress))
            elif ch in CON:
                out.append((ch, 1.0 if run == 1 else 1.7, stress))
            else:
                raise ValueError('unknown sound %r in %r' % (ch, tok))
            i = j
    return out


def _resonate(x, F, BW):
    """One formant: a two-pole resonator whose centre and width move in blocks."""
    n = len(x)
    F = np.broadcast_to(np.asarray(F, dtype=float), (n,))
    BW = np.broadcast_to(np.asarray(BW, dtype=float), (n,))
    y = np.empty(n)
    zi = np.zeros(2)
    T = 1.0 / SR
    for a in range(0, n, BLOCK):
        b = min(n, a + BLOCK)
        f, bw = F[a], BW[a]
        C = -np.exp(-TAU * bw * T)
        B = 2 * np.exp(-np.pi * bw * T) * np.cos(TAU * f * T)
        A = 1 - B - C
        y[a:b], zi = signal.lfilter([A], [1.0, -B, -C], x[a:b], zi=zi)
    return y


def _fixed(x, f, bw):
    """One resonance that does not move."""
    T = 1.0 / SR
    C = -np.exp(-TAU * bw * T)
    B = 2 * np.exp(-np.pi * bw * T) * np.cos(TAU * f * T)
    return signal.lfilter([1 - B - C], [1.0, -B, -C], x)


class Voice:
    def __init__(self, f0=110.0, rng_st=3.0, decl=2.0, final=-4.0, rate=1.0, vt=1.0, tilt=1.1, breath=0.03,
                 jitter=0.008, tremor=0.0, creak=0.0, stacc=1.0, growl=0.0, nasal=0.0, top=3.0, hiss=1.0, name=''):
        self.__dict__.update(locals())
        del self.__dict__['self']

    def say(self, text, seed=0, final=None, f0=None, hold_vib=0.0):
        """Synthesise one line. final overrides the closing pitch move in semitones."""
        r = rng(seed)
        segs = parse(text)
        rate = self.rate
        # ---- lay the sounds out in time
        tl = []           # (kind, sound, start, dur, stress, lengthfactor)
        t = 0.03
        nv = sum(1 for s in segs if s[0] in VOW)
        vi = 0
        for k, (ph, lf, st) in enumerate(segs):
            if ph == 'pause':
                d = {'.': 0.26, ',': 0.14, '!': 0.2, '?': 0.2}[lf] / max(0.8, rate ** 0.5)
                tl.append(('pause', lf, t, d, False, 1.0))
                t += d
                continue
            if ph in VOW:
                vi += 1
                d = 0.085 * lf * (1.22 if st else 1.0) * self.stacc
                nxt = segs[k + 1] if k + 1 < len(segs) else ('pause', '.', False)
                if nxt[0] == 'pause' or k == len(segs) - 1:
                    d *= 1.3            # the last vowel before a break stretches
                kind = 'vowel'
            else:
                kind = CON[ph][0]
                d = {'nasal': 0.06, 'son': 0.052, 'tap': 0.03, 'ayn': 0.065, 'vstop': 0.06, 'stop': 0.085,
                     'glottal': 0.04, 'fric': 0.085, 'vfric': 0.07, 'h': 0.06}[kind] * lf
            d /= rate
            tl.append((kind, ph, t, d, st, lf))
            t += d
        total = t + 0.06
        n = n_of(total)
        tt_ = np.arange(n) / SR
        # ---- formant targets: one anchor per sound, two for long ones, straight lines between
        at, af = [0.0], []
        first = next((s for s in tl if s[0] != 'pause'), None)

        def target(kind, ph, nxt_v, before=None):
            if kind == 'vowel':
                return A_BACK if (ph == 'a' and before in BACKING) else VOW[ph]
            if kind in ('glottal', 'h'):
                return nxt_v
            return CON[ph][1]
        vowels_after = []
        last_v = VOW['a']
        for s in reversed(tl):
            if s[0] == 'vowel':
                last_v = VOW[s[1]]
            vowels_after.append(last_v)
        vowels_after = vowels_after[::-1]
        af.append(target(first[0], first[1], vowels_after[0]) if first else VOW['a'])
        prev = af[0]
        before = None
        for s, va in zip(tl, vowels_after):
            kind, ph, t0, d, st, lf = s
            if kind == 'pause':
                at += [t0 + d * 0.5]
                af += [prev]
                before = None
                continue
            tg = target(kind, ph, va, before)
            before = ph
            if kind == 'vowel' and d > 0.11:
                at += [t0 + d * 0.25, t0 + d * 0.8]
                af += [tg, tg]
            else:
                at += [t0 + d * 0.5]
                af += [tg]
            prev = tg
        at.append(total)
        af.append(prev)
        af = np.array(af, dtype=float) * self.vt
        F = [np.interp(tt_, at, af[:, i]) for i in range(3)]
        # ---- loudness of the voice and of the breath through the mouth
        av = np.zeros(n)
        ah = np.zeros(n)
        fr_events = []
        tight = np.zeros(n)        # 1 where the mouth is closed or nearly (nasals, stop closures): dulls the top
        for kind, ph, t0, d, st, lf in tl:
            a, b = n_of(t0), min(n, n_of(t0 + d))
            if kind == 'vowel':
                av[a:b] = 1.0 + (0.18 if st else 0.0)
            elif kind == 'son':
                av[a:b] = 0.62
            elif kind == 'nasal':
                av[a:b] = 0.5
                tight[a:b] = 1.0
            elif kind == 'tap':
                av[a:b] = 0.25
            elif kind == 'ayn':
                av[a:b] = 0.7
            elif kind == 'vstop':
                c = a + int((b - a) * 0.75)
                av[a:c] = 0.14
                tight[a:c] = 1.0
                av[c:b] = 0.5
                fr_events.append((t0 + d * 0.75, 0.014, CON[ph][2], 0.6))
            elif kind == 'stop':
                c = a + int((b - a) * 0.62)
                bl = CON[ph][2]
                fr_events.append((t0 + d * 0.62, 0.016, bl, 1.0))
                ah[c:b] = 0.5
            elif kind == 'fric':
                fr_events.append((t0, d, CON[ph][2], 1.0))
            elif kind == 'vfric':
                av[a:b] = 0.4
                fr_events.append((t0, d, CON[ph][2], 1.0))
            elif kind == 'h':
                ah[a:b] = 0.85
            # glottal stop and pauses stay silent
        k = n_of(0.009)
        ker = np.hanning(2 * k + 1)
        ker /= ker.sum()
        av = np.convolve(av, ker, mode='same')
        ah = np.convolve(ah, ker, mode='same')
        tight = np.convolve(tight, ker, mode='same')
        # ---- pitch: a slope down the phrase, a lift on each stressed vowel, a move at the end
        f0b = f0 or self.f0
        st_ = np.linspace(self.decl / 2, -self.decl / 2, n)
        for kind, ph, t0, d, s_, lf in tl:
            if kind == 'vowel' and s_:
                c = t0 + d * 0.4
                st_ += self.rng_st * np.exp(-0.5 * ((tt_ - c) / (0.055 + 0.3 * d)) ** 2)
        # each phrase (up to a pause) closes with its own small move; the last one gets the full move
        ends = [(s[2], s[1]) for s in tl if s[0] == 'pause']
        if tl and tl[-1][0] != 'pause':
            ends.append((total - 0.06, 'end'))
        fin = self.final if final is None else final
        for i, (te, mark) in enumerate(ends):
            mv = fin if i == len(ends) - 1 else (abs(fin) * 0.8 if mark == '?' else fin * 0.45)
            if mark == '!' and i != len(ends) - 1:
                mv = abs(fin) * 0.3
            w = np.clip((tt_ - (te - 0.2)) / 0.2, 0, 1) * (tt_ <= te + 0.02)
            st_ += mv * w ** 1.5
        drift = filt(r.normal(0, 1, n), lp(3.0)) * 12.0 * self.jitter
        flut = filt(r.normal(0, 1, n), lp(35.0)) * 3.5 * self.jitter
        st_ += drift + flut
        if self.tremor:
            st_ += self.tremor * np.sin(TAU * 5.6 * tt_ + r.uniform(0, 6))
        if hold_vib:
            # a long held vowel shakes once it has settled
            for kind, ph, t0, d, s_, lf in tl:
                if kind == 'vowel' and d > 0.3:
                    w = np.clip((tt_ - t0 - 0.12) / 0.15, 0, 1) * (tt_ < t0 + d)
                    st_ += hold_vib * w * np.sin(TAU * 6.2 * (tt_ - t0))
        fz = f0b * 2 ** (st_ / 12)
        if self.creak:
            # the voice drops into a rattle at the end of the line
            w = np.clip((tt_ - (total - 0.28)) / 0.2, 0, 1)
            fz = fz * (1 - 0.42 * self.creak * w)
        # ---- the buzz of the throat, then the mouth's resonances
        tilt = self.tilt
        src = additive(fz, lambda kk, f: 1.0 / kk ** tilt, maxf=5200.0)
        src *= av
        if self.growl:
            ph_ = np.cumsum(fz) / SR
            src *= 1 - self.growl * 0.5 * (1 + np.sign(np.sin(np.pi * ph_))) * 0.5
        noise = r.normal(0, 1, n)
        asp = filt(noise, hp(350)) * (ah * 0.22 + av * self.breath)
        x = src * 0.5 + asp
        widen = 1.0 + 1.6 * tight
        y = x
        for i, (bw0, wid) in enumerate(((75.0, 1.0), (100.0, widen), (160.0, widen))):
            y = _resonate(y, np.maximum(F[i], 150.0), bw0 * wid * (1 + 0.6 * self.breath * 10 * (i == 0)))
        # the throat has a resonance every thousand hertz or so, without end. Stopping at three leaves the top
        # 6 to 12 dB short, which is the muffled sound of a cheap synthesiser: so three more, fixed, and a shelf
        # standing in for the rest
        for f4, bw4 in ((3500.0, 280.0), (4500.0, 380.0), (5500.0, 520.0)):
            y = _fixed(y, f4 * self.vt, bw4)
        y = y * (1 - 0.55 * tight)
        if self.nasal:
            y = filt(y, peak(270 * self.vt, 2.0, 6.0 * self.nasal), peak(1000 * self.vt, 2.5, -7.0 * self.nasal))
        # ---- hisses and bursts, made beside the mouth filter and set against this voice's own vowels
        loud = av > 0.6
        ref = float(np.sqrt(np.mean(y[loud] ** 2))) if loud.any() else float(np.sqrt(np.mean(y ** 2)) + 1e-9)
        for (t0, d, (fc, bw, g0), g) in fr_events:
            m = n_of(d + 0.03)
            a = n_of(t0)
            if a >= n:
                continue
            e = np.ones(m)
            ka = min(m // 2, n_of(0.012 if d > 0.03 else 0.002))
            kr = min(m // 2, n_of(0.02 if d > 0.03 else 0.012))
            e[:ka] = np.linspace(0, 1, ka)
            e[-kr:] = np.linspace(1, 0, kr)
            fcs = min(fc * (0.85 + 0.15 * self.vt), SR * 0.42)
            hs = filt(r.normal(0, 1, m), bp(fcs, max(0.5, fcs / bw)), hp(min(700, fcs * 0.5)))
            hs /= np.sqrt(np.mean(hs ** 2)) + 1e-9
            b = min(n, a + m)
            y[a:b] += hs[:b - a] * e[:b - a] * g0 * g * self.hiss * ref * 0.5
        y = filt(y, hp(90), shelf_hi(3200, self.top), lp(7600))
        return fade(y / (np.max(np.abs(y)) + 1e-9), 0.003, 0.02)


# ---------------------------------------------------------------- treatments
def radio(x, seed=0):
    """Through a handset: narrow band, a little crushed, static under it, a squelch at each end."""
    n = len(x) + n_of(0.3)
    y = np.zeros(n)
    y[n_of(0.12):n_of(0.12) + len(x)] = x
    y = filt(y, hp(480), lp(2900), peak(1500, 1.0, 5.0))
    y = soft(y * 2.6, 1.6)
    st = filt(white(n, seed), bp(2300, 0.6)) * 0.035
    def sq(s):
        m = n_of(0.07)
        return filt(white(m, s), bp(2000, 0.9)) * np.hanning(m) * 0.5
    y += st
    y[:n_of(0.07)] += sq(seed + 1)
    y[-n_of(0.07):] += sq(seed + 2)
    return fade(filt(y, hp(450), lp(3200)), 0.004, 0.01)


def megaphone(x, seed=0, squeal=True):
    """A hand megaphone: honky, clipped, and slapping back off the containers."""
    y = filt(x, hp(650), lp(3300), peak(1900, 1.4, 8.0))
    y = np.clip(y * 3.0, -1, 1) * 0.8
    y = filt(y, hp(600), lp(3600))
    n = len(y) + n_of(0.55)
    out = np.zeros(n)
    out[:len(y)] += y
    for d, g, c in ((0.115, 0.36, 2400), (0.25, 0.17, 1600), (0.41, 0.08, 1100)):
        a = n_of(d)
        out[a:a + len(y)] += filt(y, lp(c)) * g
    if squeal:
        m = n_of(0.28)
        t = np.arange(m) / SR
        sq = np.sin(TAU * np.cumsum(2500 + 450 * (t / t[-1]) ** 2) / SR) * np.hanning(m) ** 0.5 * 0.2
        out = np.concatenate([np.zeros(n_of(0.2)), out])
        out[:m] += sq
    return fade(out, 0.004, 0.02)


def pa(x, seed=0):
    """A stadium announcer's desk: bright, pushed, with the hall coming back."""
    y = soft(filt(x, hp(180), peak(2600, 1.0, 4.0)) * 1.8, 1.4)
    n = len(y) + n_of(0.5)
    out = np.zeros(n)
    out[:len(y)] += y
    for d, g, c in ((0.09, 0.22, 3000), (0.19, 0.12, 2200), (0.33, 0.06, 1500)):
        a = n_of(d)
        out[a:a + len(y)] += filt(y, lp(c)) * g
    return fade(out, 0.003, 0.02)


def dry(x, seed=0):
    """Close and plain, with the grain of an arcade sample."""
    return fade(soft(filt(x, hp(110), lp(7200)) * 1.5, 1.2), 0.003, 0.02)


# ---------------------------------------------------------------- the cast
# delivery follows the plan's voice table
CAST = {
    'yazeed': Voice(f0=104, rng_st=2.4, decl=2.5, final=-4.5, rate=0.92, vt=1.0, tilt=1.15, creak=0.5, name='Yazeed'),
    'salem': Voice(f0=128, rng_st=5.5, decl=1.0, final=3.0, rate=1.42, vt=0.95, tilt=1.02, jitter=0.012, name='Salem'),
    'bilqis': Voice(f0=196, rng_st=1.2, decl=1.5, final=-2.5, rate=1.0, vt=1.17, tilt=1.22, breath=0.05, stacc=0.9, name='Bilqis'),
    'arwa': Voice(f0=262, rng_st=4.5, decl=0.5, final=4.0, rate=1.36, vt=1.24, tilt=0.95, stacc=0.82, name='Arwa'),
    'dispatcher': Voice(f0=96, rng_st=0.9, decl=3.0, final=-3.0, rate=0.8, vt=1.0, tilt=1.25, breath=0.06, creak=0.7, name='Dispatcher'),
    'announcer': Voice(f0=178, rng_st=6.5, decl=-1.0, final=2.0, rate=1.12, vt=1.0, tilt=0.92, jitter=0.012, name='Announcer'),
    'grunt': Voice(f0=285, rng_st=5.0, decl=-1.0, final=5.0, rate=1.55, vt=1.06, tilt=0.9, jitter=0.03, name="Scorpion's men"),
    'cook': Voice(f0=188, rng_st=6.0, decl=0.0, final=4.0, rate=1.25, vt=0.94, tilt=1.0, jitter=0.02, nasal=0.6, name='The cook'),
    'elder': Voice(f0=122, rng_st=2.2, decl=2.5, final=-3.0, rate=0.72, vt=1.03, tilt=1.35, breath=0.06, tremor=0.5, creak=0.4, top=0.0, name='The detained'),
    'guard': Voice(f0=71, rng_st=1.0, decl=2.0, final=-5.0, rate=0.7, vt=0.84, tilt=1.05, growl=0.6, name='The Guard'),
    'commander': Voice(f0=138, rng_st=5.0, decl=1.0, final=-6.0, rate=0.82, vt=0.98, tilt=1.0, name="The battery's commander"),
    'quartermaster': Voice(f0=112, rng_st=6.5, decl=1.5, final=-5.0, rate=0.86, vt=0.92, tilt=1.05, jitter=0.015, nasal=0.4, name='The quartermaster'),
    'uncle': Voice(f0=92, rng_st=3.4, decl=2.4, final=-5.5, rate=0.76, vt=0.96, tilt=1.22, breath=0.045, jitter=0.009, creak=0.35,
                   stacc=1.08, name='The Uncle'),
    # build 28: the Souq. Three shopkeepers (played straight), and the two who push the Spice Cannon
    'shop1': Voice(f0=116, rng_st=2.6, decl=2.0, final=-3.0, rate=0.86, vt=1.02, tilt=1.25, breath=0.05, tremor=0.25, name='The tea seller'),
    'shop2': Voice(f0=134, rng_st=3.5, decl=1.5, final=-2.5, rate=1.05, vt=0.98, tilt=1.12, jitter=0.01, name='The spice seller'),
    'shop3': Voice(f0=148, rng_st=4.0, decl=1.0, final=-1.5, rate=1.2, vt=0.97, tilt=1.05, jitter=0.012, name='The cloth seller'),
    # build 30: the Tailor (in place of the Great Scale's Weighmaster): quick, fussy, a salesman to the last
    'tailor': Voice(f0=146, rng_st=6.5, decl=0.5, final=2.0, rate=1.22, vt=1.0, tilt=1.02, jitter=0.012, nasal=0.35,
                    name='The Tailor'),
}

# id: (speaker, treatment, subtitle, sounds, options)
# (19 Oct: grunt_alarm, cmdr_behold and cmdr_surrender were re-voiced by the other chat when the Dhanabs became the
# Zanabeel; their clips are in out/voice.npz, cut from main 95cc2f3's voices.mp3. Their sounds here are the old ones: do
# not say those three again from here.)
LINES = {
    # ---- on the Strait
    'ann_start': ('announcer', pa, "AND WE'RE OFF! THE STRAIT!", 'ha-*yaa da-*raa-ni ! . baa-bal-man-*daaaaab !', dict(final=-7, hold_vib=0.35)),
    'yazeed_sand': ('yazeed', dry, 'Sand in my sandals. Already.', 'ma-*raa-li ca-*ban-du . *haa-di-ku', {}),
    # (17 Oct: "IT'S HIM! DHA-NAB! DHA-NAB!" sounded as if they were calling Yazeed the Dhanab: they call their mates)
    'grunt_alarm': ('grunt', dry, "ZANABEEL! IT'S HIM!", '*yaa aD-*naab ! *bii-hu !', dict(final=6)),
    'grunt_face': ('grunt', dry, 'Not the face!', 'la la *wij-bi !', dict(final=7)),
    'grunt_door': ('grunt', dry, 'That was my door!', '*baa-bi ! . *haa-da *baa-biiii !', dict(final=6, hold_vib=0.3)),
    'ann_hmg': ('announcer', pa, 'HEAVY MG!', 'ra-ta-ta-*taaaaaaaa !', dict(final=-9, f0=205, hold_vib=0.45)),
    'ann_pistol': ('announcer', pa, '...pistol.', 'bif .', dict(final=-6, f0=118)),
    'ann_shotgun': ('announcer', pa, 'SHOTGUN!', 'ca-ka-*buuuuuum !', dict(final=-8, f0=200, hold_vib=0.4)),
    'yazeed_boat': ('yazeed', dry, "Careful. Somebody's grandfather built that.", '*daa-ri ba-*luu-ma . ja-*bii-du ka-*raa-ni *ban-na-hu', {}),
    'elder_thanks': ('elder', dry, 'Thank you, my son. Take this.', '*cuk-ran , *cuk-ran . *hii-mi ba-*lan-tu', {}),
    'elder_go': ('elder', dry, 'Go safely.', '*ruu-7i *sal-ma-na', {}),
    'cook_cook': ('cook', dry, "I'm just the cook!", 'la la la ! *ba-na *maa-lu-biiii !', dict(final=5, hold_vib=0.3)),
    'cook_lunch': ('cook', dry, 'Mind the lunch!', '*daa-ri *ful-ba-tiii !', dict(final=6)),
    'grunt_monday': ('grunt', dry, 'I only started Monday!', 'la la la ! *bad-ti *jum-ba-di !', dict(final=6)),
    'grunt_twice': ('grunt', dry, 'I surrender! Twice!', 'xa-*laas ! xa-*laas ! *tin-ta-ni !', dict(final=4)),
    'yazeed_call': ('yazeed', dry, 'Dispatch. One barrage, please.', '*kaa-bi-ru . *lam-ba *duu-fa-ra , tik-*ram', {}),
    'disp_free': ('dispatcher', radio, "Mortars again. These aren't free.", '*dam-bu-ra *tii-ni . *mu-ba *la-ku-ni', {}),
    'disp_copy': ('dispatcher', radio, 'Copy. Try not to waste them.', 'ta-*maam . *laa-mi *bu-ka-ru-ha', {}),
    'cmdr_behold': ('commander', megaphone, 'Behold! The pride of the Zanabeel!', '*un-ba-ruuu ! . *faj-du ka-*raa-ti-li-*naaaa !', dict(final=-7, hold_vib=0.25)),
    'guard_leave': ('guard', dry, 'You. Small. Leave.', '*gun . *duu-ri . *bam', {}),
    'cmdr_surrender': ('commander', megaphone, "I'd like to surrender. For the Zanabeel.", '*a-ba-di ta-*luu-man . bi-fa-*xaa-ma-tin', dict(final=-3)),
    'ann_complete': ('announcer', pa, 'MISSION COMPLETE!', 'ta-*maam ta-*maam ! . ha-la-*buuuuuuuu !', dict(final=-8, f0=195, hold_vib=0.4)),
    'yazeed_tea': ('yazeed', dry, 'Good. I need tea.', 'ta-*maam . *ba-di *luu-fa', {}),
    'yazeed_yalla': ('yazeed', dry, 'Yalla.', '*yal-la', dict(final=-3)),
    # ---- build 3: the coast road and the battery
    'salem_getin': ('salem', dry, 'Get in! Get in!', '*ta-3aal ! *ta-3aal ! ba-*sur-3a !', dict(final=5)),
    'salem_out': ('salem', dry, 'Last stop. Out you get.', '*xa-las ! . *in-zil , *in-zil', dict(final=-2)),
    'grunt_car': ('grunt', dry, 'Car! CAR!', '*say-ya-ra ! *say-ya-raaa !', dict(final=7)),
    'ann_strike': ('announcer', pa, 'STRIKE!', 'ca-*laaa-*baaaam !', dict(final=-8, f0=205, hold_vib=0.45)),
    'yazeed_flying': ('yazeed', dry, 'Is that boat... flying?', '*ha-di-ka . . *ta-*yi-ra ?', {}),
    'cmdr_minor': ('commander', megaphone, 'A minor setback. Minor!', '*mac-ka-la *sa-gii-ra . *sa-*gii-raaa !', dict(final=-5, hold_vib=0.25)),
    'cmdr_insured': ('commander', megaphone, 'The Uncle will pay. Probably.', '*mu-ta-*mam-ma . . *yim-kin', dict(final=-3)),
    # ---- build 12: The Coffee Port
    'ann_mocha': ('announcer', pa, "AND WE'RE OFF! THE COFFEE PORT!", 'ha-*yaa da-*raa-ni ! . al-*mu-xaaaaaa !', dict(final=-7, hold_vib=0.35)),
    'yazeed_coffee': ('yazeed', dry, 'Smell that? Somebody is roasting.', '*cam-mi-ta ? . *bun-ni-ya *taa-ba', {}),
    'cook_hungry': ('cook', dry, "Who's hungry?!", '*miin *jaa-3aan ? ! *jaa-3aaaan !', dict(final=6, hold_vib=0.3)),
    'yazeed_roaster': ('yazeed', dry, 'Is that... a coffee pot?', '*ha-di-ka . . *dal-la ?', {}),
    'qm_behold': ('quartermaster', dry, 'Fresh from the oven!', '*taa-za ! . *taa-za *mi-nal *fur-niii !', dict(final=-6, hold_vib=0.25)),
    'qm_chimney': ('quartermaster', dry, 'That chimney was from the Uncle!', '*mid-xa-na ! . *mus-taw-*ra-daaa !', dict(final=-4)),
    'qm_dark': ('quartermaster', dry, "Now it's a DARK roast!", '*al-*aan ! *gaa-miq ! *gaa-miiiiq !', dict(final=-8, hold_vib=0.3)),
    'qm_surrender': ('quartermaster', dry, 'All right! The coffee is on me!', '*xa-las , *xa-las ! . *al-qah-wa *3a-lay-ya', dict(final=-2)),
    'yazeed_cup': ('yazeed', dry, 'Good. Now, about that coffee.', 'ta-*maam . *ha-la *fin-jaan', {}),
    # ---- the rest of the squad, who join later
    'salem_drive': ('salem', dry, 'I drive. You hold on.', 'sa-*waa-gu ! *ti-ma-si *kuu-bi !', {}),
    'salem_again': ('salem', dry, 'Hah! Again!', 'ha ha ha ! *kam-ma-ni !', dict(final=5)),
    'bilqis_loud': ('bilqis', dry, 'Loud. Not good. Just loud.', '*doo-ca . *muu *ree-fi . *bas *doo-ca', {}),
    'bilqis_round': ('bilqis', dry, 'One round. One problem.', '*dal-fa . *ruc-bi', {}),
    'arwa_still': ('arwa', dry, 'Hold still. This stings.', '*lii-ka ! *lii-ka ! ti-*fic-fic !', {}),
    'arwa_umbrella': ('arwa', dry, 'I brought an umbrella. Obviously.', '*hib-tu ma-*lii-fa . *kaa-ba-ran', dict(final=-2)),
    # ---- the Uncle across the water, on the radio (17 Oct): khob. qâyeq-e parande qarz-e. khat nazan! / tofang-hâ-ye
    # jadid! az kojâ? naporsid. / qahve mikhâm. hamash-o! barâye ârmân. / chek tu post-e. kodum post? ye post.
    'uncle_drones': ('uncle', radio, 'The flying boat is a loan. Do not scratch it.', 'xob . GA-*ye-Ge pa-ran-*de , *Gar-ze . xat *na-zan !', dict(final=-6)),
    'uncle_guns': ('uncle', radio, 'Use the new guns. Do not ask where from.', 'to-fang-*hA-ye ja-*did ! . az ko-*jA ? . *na-por-sid', {}),
    'uncle_coffee': ('uncle', radio, 'I want the coffee. All of it. For the cause.', 'Gah-*ve mi-*xAm . ha-ma-*co ! . ba-rA-ye Ar-*mAn', {}),
    'uncle_cheque': ('uncle', radio, 'The cheque is in the post. Which post? A post.', 'tcek tu *pos-te . ko-*dum *post ? . ye *post', dict(final=-6)),
    # ---- build 28: the Souq (a few real words in the nonsense: souq, bharat, basbaas the Yemeni chilli, cannon, cart,
    # tea; the Uncle's, in Persian: advie mâl-e man-e. tup hedye bud. nashkanid!)
    'ann_souq': ('announcer', pa, "AND WE'RE OFF! THE SOUQ!", 'ha-*yaa da-*raa-ni ! . as-*suuuuuuq !', dict(final=-7, hold_vib=0.35)),
    'yazeed_souq': ('yazeed', dry, 'Mind the spice. Especially the red.', '*daa-ri *bu-ha-rat . . *xaa-sa *al-*7am-ra', {}),
    'yazeed_chilli': ('yazeed', dry, 'Chilli. In the eyes. Lovely.', '*bas-baas . *fil-*3uy-uun . . ra-*hiib', {}),
    'yazeed_lunch': ('yazeed', dry, 'Good. Now, lunch. Not too spicy.', 'ta-*maam . *ha-la *ga-daa . . *mic *7aar *mar-ra', {}),
    'grunt_eyes': ('grunt', dry, 'My eyes! MY EYES!', '*3uu-ni ! . *3uu-niiiii !', dict(final=7, hold_vib=0.3)),
    'grunt_wall': ('grunt', dry, 'That took us all morning!', '*ta-3ab-na ! . *ta-3ab-na *kul-la *yoo-maaa !', dict(final=6)),
    'shop_tea': ('shop1', dry, 'Thank you, thank you. Come back for tea. Any time.', '*cuk-ran , *cuk-ran . . *ta-3aal *ic-rab *cay . *ay *waqt', {}),
    'shop_thanks': ('shop2', dry, 'Thank you, son. Take this. Go carefully.', '*cuk-ran ya *wa-la-di . *xud *ha-da . *ruu7 *bi-sa-*laa-ma', {}),
    'shop_cloth': ('shop3', dry, "My shop... Thank you. Take these, you'll need them.", '*ma-7al-li . . *cuk-ran . *xu-*duu-hum , *bat-*7a-taj-hum', {}),
    # build 30: the Tailor (a few real words: maqaas a size, dumya a dummy, 7ariir silk, gattu cover, jaket a jacket,
    # hadiyya a gift; the Uncle's, in Persian: advie mâl-e man-e. jâyi qâyem-esh konid ke hichkas negâh nemikone)
    'tl_welcome': ('tailor', dry, 'Welcome! Everything here is made to measure. Including you.', '*ah-*laan ! . *kul *ci *hi-na 3al-ma-*qaas . . *wa *ant *ka-*daa-lik !', dict(final=4)),
    'yazeed_coat': ('yazeed', dry, "They're all wearing the same coat.", '*kul-lu-hum *laa-bi-siin . . *nafs *al-*ja-*ket', {}),
    'tl_dummy': ('tailor', dry, "I'm a dummy! Dummies don't talk!", '*a-na *dum-ya ! . . *ad-*du-ma *maa *tit-*kal-*lam !', dict(final=6)),
    'tl_silk': ('tailor', dry, 'Not the silk!', '*laa ! . *mus *al-*7a-*riiir !', dict(final=8, hold_vib=0.3)),
    'tl_more': ('tailor', dry, 'More dummies! I have plenty.', '*du-ma *ak-*tar ! . . *3in-*di *kat-*tiir !', dict(final=5)),
    'tl_cover': ('tailor', dry, 'Cover them! Cover everything!', '*gat-*tuu-hum ! . *gat-*tu *kul *ciii !', dict(final=7)),
    'tl_surrender': ('tailor', dry, 'All right! The coat is on the house.', '*xa-*laas ! . . *al-*ja-*ket 3a-*lay-ya . . *ha-*dii-ya !', dict(final=2)),
    # ---- 21 Oct: Taiz, by Apache. The Zanabeel's name for the black helicopter: the black jinn, «قنية سودا!» (ج said as g,
    # the way they say it), screamed, and a second one after the first. The announcer's ta3iz is the city's name.
    'grunt_qanya': ('grunt', dry, 'THE BLACK JINN!', '*gun-ni-ya *suu-daaa !', dict(final=8, hold_vib=0.35)),
    'ann_taiz': ('announcer', pa, "AND WE'RE OFF! THE CASTLE!", 'ha-*yaa da-*raa-ni ! . ta-*3iiiiiiz !', dict(final=-7, hold_vib=0.35)),
    'uncle_spice': ('uncle', radio, 'The spice is mine. Hide it where nobody looks.', 'ad-vi-*ye mA-le *ma-ne . *jA-yi GA-ye-*mec ko-*nid . ke *hic-kas ne-*gAh ne-mi-*ko-ne', dict(final=-6)),
}

# things that must not turn up by accident inside the nonsense (checked on every line)
AVOID = ('allah', 'wallah', 'rabb', 'yarab', 'bism', 'nabi', 'islam', 'kafir', 'kuffar', 'quran', 'jihad', 'cahid', 'takbir',
         'xara', 'zib', 'zubb', 'kus', 'kis', 'kos', 'ayr', 'tiz', 'nik', 'niik', 'manyak', 'manyuk', 'carmut', 'qa7b', 'ga7b',
         'kalb', '7imar', 'xawal', 'luti', 'zamil', '3ars', 'xanzir', 'yahud', '7uthi', 'huthi', 'da3ic', 'qa3ida', 'rafid',
         'nasib', 'majus', 'ci3a', 'sunni', 'zaydi', 'hacim')


AVOID_FA = ('xoda', 'xodA', 'emAm', 'imAm', 'imam', 'rahbar', 'marg', 'sepAh', 'basij', 'mollA', 'Axund', 'cAh', 'enGe',
            'enqe', 'moGA', 'moqA', 'cahid', 'cohada', 'kir', 'kos', 'kun', 'jende', 'guz', 'xar', 'kesA', 'jAkec',
            'pedar', 'mAdar', 'irAn', 'iran', 'esrA', 'yahud')


def check_words():
    bad = []
    for k, (sp, fx, sub, text, opt) in LINES.items():
        flat = ''.join(ch for ch in text if ch.isalnum() or ch in "'")
        for w in AVOID + (AVOID_FA if sp == 'uncle' else ()):
            if w in flat:
                bad.append((k, w))
    return bad


# ---------------------------------------------------------------- noises a throat makes
def scream(v, dur=0.75, seed=0, rise=False):
    """A cartoon yell: one open vowel, sliding."""
    n = n_of(dur)
    t = np.arange(n) / SR
    r = rng(seed)
    st = (7 * (t / dur) if rise else 5 - 12 * (t / dur) ** 1.4) + filt(r.normal(0, 1, n), lp(25)) * 0.6
    fz = v.f0 * 1.9 * 2 ** (st / 12)
    src = additive(fz, lambda kk, f: 1.0 / kk ** 0.85, maxf=5200.0)
    env = np.minimum(1, t / 0.03) * np.minimum(1, (dur - t) / 0.12)
    wob = 1 + 0.25 * np.sin(TAU * 9 * t)
    y = src * env * wob + filt(r.normal(0, 1, n), hp(500)) * 0.06 * env
    for f, bw in ((820 * v.vt, 110), (1350 * v.vt, 130), (2700 * v.vt, 200), (3600 * v.vt, 300)):
        y = _resonate(y, np.full(n, f * (1 + 0.08 * (t / dur))), np.full(n, float(bw)))
    y = filt(y, hp(200), shelf_hi(2500, 4.0), lp(6500))
    return fade(y / np.max(np.abs(y)), 0.003, 0.03)


def yelp(v, seed=0):
    return scream(v, 0.22, seed, rise=True)


def hmph(v, seed=0, dur=0.5):
    """A closed-mouth grunt, pitch falling."""
    n = n_of(dur)
    t = np.arange(n) / SR
    fz = v.f0 * 1.25 * 2 ** ((3 - 8 * (t / t[-1]) ** 0.8) / 12)
    src = additive(fz, lambda kk, f: 1.0 / kk ** 1.15, maxf=4000.0)
    env = np.minimum(1, t / 0.035) * np.minimum(1, (dur - t) / 0.16) ** 1.3 * (1 - 0.35 * t / dur)
    ph_ = np.cumsum(fz) / SR
    src *= 1 - 0.35 * (1 + np.sign(np.sin(np.pi * ph_))) * 0.5
    y = src * env
    for f, bw in ((270 * v.vt, 110), (1050 * v.vt, 260), (2250 * v.vt, 380)):
        y = _resonate(y, np.full(n, f), np.full(n, float(bw)))
    y += filt(rng(seed).normal(0, 1, n), bp(1500, 0.8)) * 0.04 * decay(n, 0.12)
    y = filt(y, hp(60), peak(1200, 1.0, 5.0), lp(3800))
    return fade(y / np.max(np.abs(y)), 0.003, 0.03)


def _vowel(n, fz, F, tilt=1.0, maxf=5000.0):
    """A held vowel on a pitch track: the source through three formants."""
    y = additive(fz, lambda kk, f: 1.0 / kk ** tilt, maxf=maxf)
    for f, bw in F:
        y = _resonate(y, np.full(n, f), np.full(n, float(bw)))
    return y / (np.max(np.abs(y)) + 1e-9)


def sneeze(v, seed=0, short=False):
    """Ah... ah... CHOO: catches of breath climbing (one, for a short one), a held one, and the burst."""
    r = rng(seed)
    catches = ((0.22, 4),) if short else ((0.16, 0), (0.2, 3), (0.3, 6))
    parts, t0 = [], 0.0
    for i, (dur, st) in enumerate(catches):
        n = n_of(dur)
        t = np.arange(n) / SR
        fz = v.f0 * 1.6 * 2 ** ((st + 2 * (t / dur)) / 12)
        y = _vowel(n, fz, ((700 * v.vt, 160), (1250 * v.vt, 200), (2600 * v.vt, 300)))
        br = filt(r.normal(0, 1, n), bp(1400, 0.7))
        y = y * 0.65 + br / (np.max(np.abs(br)) + 1e-9) * 0.35
        env = np.minimum(1, t / 0.04) * np.minimum(1, (dur - t) / 0.05)
        parts.append((t0, y * env * (0.35 + 0.12 * (i + (2 if short else 0)))))
        t0 += dur + (0.1 if i < len(catches) - 1 else 0.16)
    n = n_of(0.34)
    t = np.arange(n) / SR
    ch = filt(r.normal(0, 1, n), bp(3200, 1.0), hp(1500)) * np.exp(-t / 0.05)
    fz = v.f0 * 2.1 * 2 ** (-10 * (t / 0.34) / 12)
    vow = _vowel(n, fz, ((360 * v.vt, 120), (900 * v.vt, 180), (2300 * v.vt, 300)), tilt=0.9)
    vow *= np.clip((t - 0.03) / 0.02, 0, 1) * np.exp(-np.maximum(0, t - 0.05) / 0.09)
    parts.append((t0, ch / (np.max(np.abs(ch)) + 1e-9) * 0.9 + vow * 0.9))
    out = np.zeros(n_of(t0 + 0.4))
    for st, y in parts:
        a = n_of(st)
        out[a:a + len(y)] += y[:len(out) - a]
    out = filt(out, hp(120), lp(7000))
    return fade(out / np.max(np.abs(out)), 0.003, 0.03)


def pant(v, seed=0, breaths=6):
    """Out of breath: short hard breaths out and in, a little voice in the outs."""
    r = rng(seed)
    parts, t0 = [], 0.0
    for i in range(breaths):
        out_ = i % 2 == 0
        dur = 0.15 if out_ else 0.12
        n = n_of(dur)
        t = np.arange(n) / SR
        y = r.normal(0, 1, n)
        for f, bw in ((750 * v.vt, 250), (1300 * v.vt, 300), (2500 * v.vt, 400)):
            y = _resonate(y, np.full(n, f), np.full(n, float(bw)))
        y = y / (np.max(np.abs(y)) + 1e-9)
        if out_:
            fz = v.f0 * 1.3 * 2 ** (-3 * (t / dur) / 12)
            y = y * 0.8 + _vowel(n, fz, ((750 * v.vt, 200), (1300 * v.vt, 240), (2500 * v.vt, 360)), tilt=1.2, maxf=3000.0) * 0.3
        env = np.sin(np.pi * t / dur) ** (0.7 if out_ else 1.2)
        parts.append((t0, y * env * (1.0 if out_ else 0.5)))
        t0 += dur + 0.05
    out = np.zeros(n_of(t0 + 0.05))
    for st, y in parts:
        a = n_of(st)
        out[a:a + len(y)] += y[:len(out) - a]
    out = filt(out, hp(200), lp(6000))
    return fade(out / np.max(np.abs(out)), 0.003, 0.03)


VOCALS = {
    'grunt_scream': ('grunt', dry, '(a long way down)', lambda v, s: scream(v, 0.8, s)),
    'grunt_yelp': ('grunt', dry, '(hit)', lambda v, s: yelp(v, s)),
    'cook_wail': ('cook', dry, '(the pot!)', lambda v, s: scream(v, 0.6, s, rise=True)),
    'guard_hmph': ('guard', dry, 'Hmph.', lambda v, s: hmph(v, s)),
    # build 28: the Souq
    'yazeed_sneeze': ('yazeed', dry, '(sneeze)', lambda v, s: sneeze(v, s)),
    'grunt_sneeze': ('grunt', dry, '(sneeze)', lambda v, s: sneeze(v, s, short=True)),
    # build 30: the Tailor caught out, and spun round in his own tape
    'tl_ow': ('tailor', dry, '(caught)', lambda v, s: yelp(v, s)),
    'tl_whoa': ('tailor', dry, '(wound up)', lambda v, s: v.say('*waa-*waa-*waaa !', seed=s, final=9)),
}


def level(y, target=-15.0, knee=0.5, top=0.84):
    """Bring a clip to a loudness; anything over the knee is rounded off instead of cut."""
    y = y - np.mean(y)
    y = y * 10 ** ((target - lufs(np.stack([y, y], 1))) / 20)
    a = np.abs(y)
    over = a > knee
    out = y.copy()
    out[over] = np.sign(y[over]) * (knee + (top - knee) * np.tanh((a[over] - knee) / (top - knee)))
    return out


# who is who on the page: name, where the voice is from, how it is delivered
WHO = {
    'yazeed': ('Yazeed', 'Taiz', 'Low and unhurried'),
    'salem': ('Salem', 'Tihama coast', 'Fast and bouncy'),
    'bilqis': ('Bilqis', 'Marib', 'Flat and dry'),
    'arwa': ('Arwa', 'Ibb', 'Bright and clipped'),
    'dispatcher': ('The dispatcher', 'Gulf', 'Bored, through radio crackle'),
    'announcer': ('The announcer', 'Broadcast Arabic', 'Football-commentator ecstasy'),
    'commander': ("The battery's commander", 'Podium Arabic', 'Pompous, in love with his own echo'),
    'grunt': ("The Scorpion's men", 'Mixed, from everywhere', 'Squeaky panic'),
    'cook': ('The cook', 'Mixed, from everywhere', 'Aggrieved, through the nose'),
    'guard': ('The Guard', 'Mixed, from everywhere', 'A growl from the floor'),
    'elder': ('The detained', 'The coast', 'Old and slow, played straight'),
    'quartermaster': ('The quartermaster', 'Podium Arabic', 'Pompous, put out, fond of his machine'),
    'uncle': ('The Uncle', 'Across the water: Persian', 'A patron on the radio: deep, slow, every word weighed'),
    'shop1': ('The tea seller', 'Zabid', 'Old and warm, played straight'),
    'shop2': ('The spice seller', 'Zabid', 'Kind and quick, played straight'),
    'shop3': ('The cloth seller', 'Zabid', 'Shaken, grateful, played straight'),
    'tailor': ('The Tailor', 'Mixed, from everywhere', 'Smooth and fussy, a salesman to the last'),
}


def render_all():
    out = {}
    for k, (sp, fx, sub, text, opt) in LINES.items():
        v = CAST[sp]
        y = fx(v.say(text, seed=sum(map(ord, k)) % 997, **opt), seed=5)
        out[k] = level(y)
    for k, (sp, fx, sub, fn) in VOCALS.items():
        y = fx(fn(CAST[sp], 7), seed=5)
        out[k] = level(y, -17.0 if sp != 'guard' else -15.0)
    return out
