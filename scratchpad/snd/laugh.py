# laugh.py - a laugh that sounds like a person, not a synthesiser saying "ha" (Khaled, 11 Nov 02:26: "The laugh needs
# some work"). Built the way speech scientists build voices (a Klatt-style source and filter) and laid out the way
# people laugh (Bachorowski, Smoski & Owren 2001; Provine 2000):
# - the voice is a train of glottal pulses (a KLGLOTT88 flow: the pulse, then the closure that rings the throat) with
#   the small irregularities of a real larynx: jitter (the pitch wobbles from cycle to cycle) and shimmer (so does the
#   loudness); breath noise rides on every pulse and swamps it when he runs out of air;
# - five formants shape it; a laugh's vowel is central and open (head back), not the spoken "a" of "ha";
# - each call starts with its own "h" (the same vowel, whispered), the pitch peaks early and falls inside the call, about
#   five calls a second, getting breathier down the bout; a bout runs on one breath, and between bouts the breath is
#   dragged back in, often with a squeak in it.
# A laugh is a list of events (calls, breaths in, sighs, hums) rendered into one set of tracks, so the formants and the
# breath move continuously from one call to the next, as they do in a throat.
import numpy as np
from scipy import signal
from core import *
import voice as V

OS = 2   # the pulses are drawn at twice the rate, then filtered down (the closure is a corner: it would alias)

# vowel targets (F1..F5 in Hz) for a man's throat; vt scales them (a bigger man, a longer throat, lower)
OPEN = (720, 1260, 2520, 3400, 4300)       # head back, mouth open: the belly laugh
GRIN = (600, 1520, 2560, 3450, 4350)       # the mouth stretched in a grin: the giggle
SCHWA = (540, 1380, 2480, 3420, 4300)      # out of breath: the mouth half shut
INHALE = (420, 1900, 2750, 3600, 4500)     # air dragged in through a narrow throat
NASAL = (330, 1080, 2350, 3300, 4200)      # the mouth shut on a chuckle: air and a creak through the nose
BW_MODAL = (80, 100, 150, 220, 280)
BW_BREATHY = (150, 170, 240, 320, 400)
BW_NASAL = (120, 260, 380, 460, 520)


def _lp_noise(n, cutoff, r, sr=SR):
    b, a = signal.butter(2, min(0.99, cutoff / (sr / 2)))
    y = signal.lfilter(b, a, r.normal(0, 1, n))
    return y / (np.std(y) + 1e-12)


class Laugh:
    """Collect events on a timeline, then render() them. Times in seconds; pitches in Hz; amplitudes 0..1."""

    def __init__(self, vt=1.0, seed=0):
        self.vt = vt
        self.seed = seed
        self.r = rng(seed)
        self.ev = []
        self.extra = []          # (time, clip): sounds made elsewhere (the hums), mixed in at the end
        self.marks = []          # times of the squeaks: where a loudhailer catches and squeals

    # ------------------------------------------------------------- events
    def call(self, t, f0, amp=1.0, breath=0.3, h=0.03, voiced=0.1, vowel=OPEN, fall=4.0, peak=1.0, oq=0.58,
             squeak=False, tilt=0.0):
        """One 'ha': a whispered onset of h seconds, then voiced seconds of voice whose pitch rises peak semitones over
        f0 in its first quarter and falls fall semitones below f0 by its end. breath: how much breath rides on the
        voice (0 clean, 1 as loud as the voice). tilt: extra darkening of the source (0..1)."""
        self.ev.append(('call', t, dict(f0=f0, amp=amp, breath=breath, h=h, voiced=voiced, vowel=vowel, fall=fall,
                                        peak=peak, oq=oq, squeak=squeak, tilt=tilt)))
        if squeak:
            self.marks.append(t + h)
        return t + h + voiced

    def breath_in(self, t, dur, amp=0.4, whoop=None, whoop_amp=0.35):
        """Air dragged back in: noise through a narrow throat, rising; whoop=(f0 start, f0 end) adds the squeak of a
        voice caught on the way in."""
        self.ev.append(('in', t, dict(dur=dur, amp=amp, whoop=whoop, whoop_amp=whoop_amp)))
        return t + dur

    def sigh(self, t, dur, f0=(210, 125), amp=0.5, breath=0.55, vowel=OPEN):
        """A long 'aaah' that falls and fades: the end of the laugh."""
        self.ev.append(('sigh', t, dict(dur=dur, f0=f0, amp=amp, breath=breath, vowel=vowel)))
        return t + dur

    def mix(self, t, clip):
        self.extra.append((t, clip))
        return t + len(clip) / SR

    # ------------------------------------------------------------- rendering
    def render(self, tail=0.25):
        end = 0.0
        for kind, t, p in self.ev:
            d = p.get('dur', p.get('h', 0) + p.get('voiced', 0) + 0.08)
            end = max(end, t + d)
        for t, c in self.extra:
            end = max(end, t + len(c) / SR)
        n = n_of(end + tail)
        tt_ = np.arange(n) / SR
        av = np.zeros(n)            # voice amplitude
        ah = np.zeros(n)            # breath amplitude
        dark = np.zeros(n)          # extra source darkening, 0..1
        kf_f0, kf_oq, kf_F, kf_B = [], [], [], []
        vt = self.vt

        def seg(a, b):
            return slice(max(0, n_of(a)), min(n, n_of(b)))

        def ramp(x, a, b):
            return np.clip((x - a) / max(1e-6, b - a), 0, 1)

        for kind, t, p in sorted(self.ev, key=lambda e: e[1]):
            if kind == 'call':
                h, v, A = p['h'], p['voiced'], p['amp']
                tv = t + h
                F = [f * vt for f in p['vowel']]
                B = BW_NASAL if p['vowel'] is NASAL else (BW_BREATHY if p['breath'] > 0.55 else BW_MODAL)
                kf_F.append((t, F)); kf_B.append((t, B))
                kf_F.append((tv + v, [f * (0.97 if i == 0 else 1.0) for i, f in enumerate(F)])); kf_B.append((tv + v, B))
                f0 = p['f0']
                kf_f0 += [(tv, f0 * 2 ** ((p['peak'] * 0.4) / 12)), (tv + 0.25 * v, f0 * 2 ** (p['peak'] / 12)),
                          (tv + v, f0 * 2 ** (-p['fall'] / 12))]
                kf_oq += [(t, p['oq']), (tv + v, min(0.85, p['oq'] + 0.1))]
                # the whispered onset: up in 8 ms, held, handing over to the voice
                s = seg(t, tv + 0.02)
                x = tt_[s]
                ah[s] += A * 0.42 * ramp(x, t, t + 0.006) * (1 - 0.7 * ramp(x, tv, tv + 0.015))
                # the voice: a fast attack, a short hold, a falling release
                s = seg(tv, tv + v + 0.06)
                x = (tt_[s] - tv) / v
                env = np.clip(x / 0.14, 0, 1) ** 1.5 * np.clip((1.0 - x) / 0.62, 0, 1) ** 1.35
                av[s] += A * (1 - p['breath'] * 0.6) * env
                # breath riding on the voice, and a little after it
                tailb = np.exp(-np.clip(x - 1.0, 0, None) * v / 0.03) * (x > 1.0)
                ah[s] += A * p['breath'] * 0.4 * (np.maximum(env, 0) + 0.8 * tailb)
                dark[s] = np.maximum(dark[s], p['tilt'])
            elif kind == 'in':
                d, A = p['dur'], p['amp']
                F = [f * vt for f in INHALE]
                kf_F += [(t, F), (t + d, [f * 1.08 for f in F])]
                kf_B += [(t, (200, 260, 340, 420, 500)), (t + d, (160, 220, 300, 380, 460))]
                kf_oq += [(t, 0.82), (t + d, 0.82)]
                s = seg(t, t + d)
                x = (tt_[s] - t) / d
                ah[s] += A * np.sin(np.pi * np.clip(x, 0, 1)) ** 0.7 * (0.6 + 0.4 * x)
                if p['whoop']:
                    a0, a1 = p['whoop']
                    kf_f0 += [(t + 0.25 * d, a0), (t + 0.9 * d, a1)]
                    w = np.clip((x - 0.25) / 0.2, 0, 1) * np.clip((0.95 - x) / 0.25, 0, 1)
                    av[s] += A * p['whoop_amp'] * w
                    dark[s] = np.maximum(dark[s], 0.55)
                    self.marks.append(t + 0.45 * d)
            elif kind == 'sigh':
                d, A = p['dur'], p['amp']
                F = [f * vt for f in p['vowel']]
                kf_F += [(t, F), (t + d, [f * vt for f in SCHWA])]
                kf_B += [(t, BW_MODAL), (t + d, BW_BREATHY)]
                kf_f0 += [(t, p['f0'][0]), (t + 0.15 * d, p['f0'][0] * 1.03), (t + d, p['f0'][1])]
                kf_oq += [(t, 0.6), (t + d, 0.8)]
                s = seg(t, t + d)
                x = (tt_[s] - t) / d
                env = np.clip(x / 0.08, 0, 1) * (1 - x) ** 1.6
                av[s] += A * (1 - p['breath'] * 0.5) * env * np.clip((0.85 - x) / 0.3, 0, 1)
                ah[s] += A * p['breath'] * env * (0.6 + 0.6 * x)
        # ---- tracks from keyframes (pitch in log, the rest straight lines)
        def track(kfs, default):
            if not kfs:
                return np.full(n, default, dtype=float)
            kfs = sorted(kfs, key=lambda k: k[0])
            xs = np.array([k[0] for k in kfs])
            ys = np.array([k[1] for k in kfs], dtype=float)
            return np.interp(tt_, xs, ys)

        f0 = np.exp(track([(t, np.log(f)) for t, f in kf_f0], np.log(180.0)))
        oq = np.clip(track(kf_oq, 0.6), 0.35, 0.9)
        Fs = [track([(t, F[i]) for t, F in kf_F], OPEN[i] * vt) for i in range(5)]
        Bs = [track([(t, B[i]) for t, B in kf_B], BW_MODAL[i]) for i in range(5)]
        # the larynx shakes when you laugh: a slow tremor under the cycle-to-cycle jitter
        r = self.r
        f0 = f0 * (1 + 0.012 * np.sin(TAU * 6.3 * tt_ + r.uniform(0, TAU)) + 0.006 * _lp_noise(n, 8.0, r))
        # ---- the source
        dg, g = self._glottal(f0, oq, r)
        dg = dg / (np.percentile(np.abs(dg), 99.5) + 1e-9)
        dg = filt(dg, shelf_hi(1800, 7.0))
        # darker source where asked (the squeaks are rounder, the voice caught on the way in): a moving one-pole
        dg = self._darken(dg, dark)
        noise = filt(r.normal(0, 1, n), hp(380), lp(9000))
        noise /= np.std(noise) + 1e-9
        gn = np.clip(g / (np.max(g) + 1e-9), 0, 1)
        # breath is louder while the folds are open; on its own (no voice) it is plain breath
        mod = np.where(av > 0.02, 0.4 + 0.9 * gn, 1.0)
        src = dg * av + noise * ah * mod * 0.32
        # ---- the throat: five formants in a cascade
        y = src
        for i in range(5):
            y = V._resonate(y, Fs[i], Bs[i])
        y = filt(y, hp(70), lp(9500))
        out = y / (np.max(np.abs(y)) + 1e-9) * 0.9
        for t, c in self.extra:
            a = n_of(t)
            out[a:a + len(c)] += c[:max(0, n - a)]
        return out

    def _glottal(self, f0, oq, r, jitter=0.010, shimmer=0.06):
        n = len(f0)
        m = n * OS
        sr = SR * OS
        xi = np.arange(m) / OS
        f = np.interp(xi, np.arange(n), f0)
        q = np.interp(xi, np.arange(n), oq)
        f = f * (1 + jitter * _lp_noise(m, 90.0, r, sr))
        ph = np.cumsum(f) / sr
        k = np.floor(ph).astype(np.int64)
        tau = ph - k
        amp = 1 + shimmer * r.normal(0, 1, k.max() - k.min() + 2)
        a = amp[k - k.min()]
        x = tau / q
        g = np.where(x < 1, 6.75 * x * x * (1 - x), 0.0) * a
        dg = np.diff(g, prepend=0.0) * sr / np.maximum(f, 1.0)
        dg = signal.resample_poly(dg, 1, OS)[:n]
        g = signal.resample_poly(g, 1, OS)[:n]
        return dg, g

    @staticmethod
    def _darken(x, dark, block=64):
        """A one-pole low-pass whose corner moves from open (dark 0) to about 900 Hz (dark 1)."""
        if not np.any(dark > 0):
            return x
        y = np.empty_like(x)
        z = np.zeros(1)
        for a in range(0, len(x), block):
            b = min(len(x), a + block)
            d = float(dark[a])
            fc = 9000.0 * (1 - d) + 900.0 * d
            c = np.exp(-TAU * fc / SR)
            seg, z = signal.lfilter([1 - c], [1, -c], x[a:b], zi=z)
            y[a:b] = seg * (1 + 1.5 * d)       # keep its loudness roughly where it was
        return y


def snort(seed=0, dur=0.07):
    """Air out through the nose: the chuckle before the laugh breaks."""
    n = n_of(dur)
    t = np.arange(n) / SR
    y = filt(rng(seed).normal(0, 1, n), bp(1100, 0.7), hp(400), lp(4000))
    return y / (np.max(np.abs(y)) + 1e-9) * np.exp(-t / 0.025) * np.clip(t / 0.004, 0, 1)
