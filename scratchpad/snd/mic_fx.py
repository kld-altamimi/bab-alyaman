# mic_fx.py - the sounds of the Spokesman's microphone on the pass (Ibb, zone 4; Khaled, 30 Oct 00:39: "Go ahead and finish
# the whole level"): feedback, the howl of a microphone too near its loudspeaker (when his is shot off, and when the fight
# gets loud), and the shriek that runs along the ground from it with two podiums left (jump it): a howl that climbs, its
# overtones beating, driven into the loudspeakers until it breaks up, the hillside's air on it.
#   python3 mic_fx.py   -> out/tmp/feedback.wav, out/tmp/shriek.wav (add_speech.py puts them in Ibb's speech file)
import numpy as np
from core import *


def howl(dur, f0, f1, wob=5.5, drive=2.2, seed=1, rise=0.1, fall=0.25):
    """A howl from f0 to f1: a sine with its overtones, a quick wobble, swelling in and dying away."""
    n = n_of(dur)
    u = np.arange(n) / n
    f = f0 * (f1 / f0) ** (u ** 0.7)
    f = f * (1 + 0.012 * np.sin(TAU * wob * np.arange(n) / SR))
    ph = TAU * np.cumsum(f) / SR
    y = np.sin(ph) + 0.35 * np.sin(2 * ph + 0.4) + 0.18 * np.sin(3 * ph + 1.1)
    env = np.minimum(1, u / rise) * np.minimum(1, (1 - u) / fall) ** 1.3
    y = soft(y * env * drive, 1.0)
    y += filt(white(n, seed), bp(f0 * 1.5, 1.2)) * env * 0.05
    return y


def clips():
    fb = howl(0.95, 2350, 2900, seed=3) * 0.45
    sh = howl(1.0, 1500, 3400, wob=11.0, drive=3.4, seed=7, rise=0.04, fall=0.35) * 0.42
    ir = reverb_ir(0.6, damp=4200, seed=5)

    def air(x, wet):
        w = convolve(x, ir)
        if w.ndim == 2:
            w = w.mean(axis=1)
        d = np.zeros(len(w))
        d[:len(x)] = x
        return d * (1 - wet) + w * wet
    return {'feedback': to_peak(air(fb, 0.35), -3.0), 'shriek': to_peak(air(sh, 0.3), -2.0)}


if __name__ == '__main__':
    for k, y in clips().items():
        write_wav('out/tmp/%s.wav' % k, y)
        print(k, '%.2f s' % (len(y) / SR))
