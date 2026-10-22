# meter.py - what the ears would check, measured: octave balance, crest, stereo, loop seam.
import numpy as np
from scipy import signal
from core import *

BANDS = (63, 125, 250, 500, 1000, 2000, 4000, 8000)


def octave_levels(x):
    x = np.asarray(x)
    m = x.mean(axis=1) if x.ndim == 2 else x
    f, p = signal.welch(m, SR, nperseg=8192)
    out = []
    for c in BANDS:
        sel = (f >= c / 2 ** 0.5) & (f < c * 2 ** 0.5)
        out.append(10 * np.log10(np.sum(p[sel]) * (f[1] - f[0]) + 1e-20))
    return out


def report(name, x, loop=False):
    x = np.asarray(x)
    lv = octave_levels(x)
    pk = db(np.abs(x).max())
    r = db(rms(x))
    line = '%-18s %6.2fs  LUFS %6.1f  peak %5.1f  crest %4.1f dB  bands ' % (name, len(x) / SR, lufs(x), pk, pk - r)
    line += ' '.join('%4.0f' % v for v in lv)
    if x.ndim == 2:
        l, rr = x[:, 0], x[:, 1]
        c = float(np.corrcoef(l, rr)[0, 1])
        line += '  L/R corr %.2f' % c
    if loop:
        # the jump across the loop point compared with ordinary sample-to-sample steps
        m = x.mean(axis=1) if x.ndim == 2 else x
        step = np.abs(np.diff(m))
        line += '  seam step %.4f (typical %.4f, max %.4f)' % (abs(m[0] - m[-1]), np.median(step), step.max())
    print(line)
    return lv
