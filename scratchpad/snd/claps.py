# claps.py - the Spokesman's audience at his rally (Ibb, zone 3; Khaled, 29 Oct 21:36: "The story board looks great"):
# five pairs of hands. A polite round after each of his lines (clap_s: they join in one after another, keep it up for a
# second or so and stop one after another) and the applause for his jump (clap_l: three seconds, quicker, louder, one
# of them whistling through his fingers). Each clap is a crack of noise through a band of its own (each man's hands
# sound their own), gone in a hundredth of a second, with a little of the hillside's air on it.
#   python3 claps.py   -> out/tmp/clap_s.wav, out/tmp/clap_l.wav (add_speech.py puts them in Ibb's speech file)
import numpy as np
from core import *


def clap(r, f, q):
    """One clap: a sharp attack, a quick fall; the body a band around f, a little crack above."""
    n = n_of(0.07)
    t = np.arange(n) / SR
    env = np.minimum(1.0, t / 0.0006) * np.exp(-t / r.uniform(0.0065, 0.011))
    x = white(n, int(r.integers(0, 1 << 30))) * env
    return filt(x, bp(f, q)) * 2.2 + filt(x, hp(2600)) * 0.35


def whistle(r, t0, out):
    """Two blasts through the fingers: a short one rising, a long one up and over."""
    for (start, dur, f0, f1, f2) in ((t0, 0.22, 2500, 3200, 3150), (t0 + 0.34, 0.62, 2700, 3450, 2900)):
        n = n_of(dur)
        u = np.arange(n) / n
        f = np.where(u < 0.35, f0 + (f1 - f0) * np.clip(u / 0.35, 0, 1) ** 0.6, f1 + (f2 - f1) * np.clip((u - 0.35) / 0.65, 0, 1) ** 1.4)
        f = f * (1 + 0.006 * np.sin(TAU * 6.2 * np.arange(n) / SR))
        ph = TAU * np.cumsum(f) / SR
        env = np.minimum(1, u / 0.08) * np.minimum(1, (1 - u) / 0.18) ** 1.5
        y = (np.sin(ph) + 0.08 * np.sin(2 * ph)) * env
        y += filt(white(n, int(r.integers(0, 1 << 30))), bp(3000, 2.5)) * env * 0.12      # (the breath in it)
        i = n_of(start)
        m = min(n, len(out) - i)
        out[i:i + m] += y[:m] * 0.2


def round_of(dur, people=5, rate=4.2, seed=1, whistler=False, tail=0.3):
    """-> mono: `people` pairs of hands clapping at about `rate` a second for about `dur` seconds."""
    r = rng(seed)
    out = np.zeros(n_of(dur + 0.5))
    for k in range(people):
        f, q, g = r.uniform(1000, 2300), r.uniform(1.0, 1.8), r.uniform(0.6, 1.0)
        per = 1.0 / (rate * r.uniform(0.88, 1.12))
        t = 0.02 + k * r.uniform(0.03, 0.08)               # (one after another)
        stop = dur * r.uniform(0.72, 1.0)
        while t < stop:
            c = clap(r, f * r.uniform(0.95, 1.05), q)
            i = n_of(t)
            amp = g * r.uniform(0.75, 1.0) * min(1.0, (stop - t) / tail + 0.15)
            m = min(len(c), len(out) - i)
            out[i:i + m] += c[:m] * amp
            t += per * r.uniform(0.9, 1.1)
    if whistler:
        whistle(r, dur * 0.18, out)
    ir = reverb_ir(rt60=0.45, predelay=0.012, damp=6000.0, seed=seed + 7, early=True)
    wet = convolve(out, ir).mean(axis=1)[:len(out)]
    y = out + 0.22 * wet
    end = np.nonzero(np.abs(y) > 1e-4 * np.max(np.abs(y)))[0][-1] + 1
    return fade(y[:end], 0.001, 0.05)


def clips():
    """-> {'clap_s': mono, 'clap_l': mono}, each brought to its loudness (the game plays them under the voices)."""
    s = round_of(1.15, rate=4.0, seed=11)
    l = round_of(3.0, rate=5.6, seed=23, whistler=True, tail=0.6)
    return {'clap_s': to_level(s, -19.0)[0], 'clap_l': to_level(l, -16.5)[0]}


if __name__ == '__main__':
    for k, y in clips().items():
        write_wav('out/tmp/%s.wav' % k, y)
        print(k, '%.2f s' % (len(y) / SR), 'peak %.2f' % np.max(np.abs(y)), 'lufs %.1f' % lufs(y))
