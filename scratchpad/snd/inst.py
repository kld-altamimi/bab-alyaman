# inst.py - the band. Coast instruments first, then the arcade's.
import numpy as np
from core import *

# ---------------------------------------------------------------- pitch
A4 = 440.0
NOTE = {'C': -9, 'C#': -8, 'Db': -8, 'D': -7, 'Eb': -6, 'E': -5, 'F': -4, 'F#': -3, 'G': -2, 'Ab': -1,
        'A': 0, 'Bb': 1, 'B': 2}


def hz(name):
    """'D4' -> 293.66"""
    nm, octv = name[:-1], int(name[-1])
    return A4 * 2 ** ((NOTE[nm] + (octv - 4) * 12) / 12)


# ---------------------------------------------------------------- strings
def lyre(f, dur=1.2, vel=1.0, seed=0):
    """Five-string box lyre: wire strings, a horn plectrum, a skin-topped box. Bright and ringing."""
    y = pluck(f, dur, t60=1.9, damp=0.10, bright=0.55 + 0.4 * vel, pick=0.13, seed=seed)
    y2 = pluck(f * 1.0015, dur, t60=1.7, damp=0.12, bright=0.5 + 0.4 * vel, pick=0.21, seed=seed + 5)
    y = y + 0.5 * y2
    # the box: a thump under the attack and two resonances
    n = len(y)
    thump = np.sin(TAU * 190 * np.arange(n) / SR) * decay(n, 0.09) * 0.25
    y = filt(y + thump, hp(150), peak(420, 1.6, 4.0), peak(2400, 1.2, 5.0), lp(9000))
    return fade(y * vel, 0.0005, 0.03)


def strum(freqs, dur=0.9, vel=1.0, spread=0.012, up=False, seed=0):
    """The plectrum drawn across several strings."""
    order = list(freqs)[::-1] if up else list(freqs)
    n = n_of(dur + spread * len(order))
    out = np.zeros(n)
    for i, f in enumerate(order):
        s = lyre(f, dur, vel * (0.85 + 0.15 * (i % 2)), seed + i * 3)
        a = n_of(i * spread)
        out[a:a + len(s)] += s[:n - a]
    return out


def qanbus(f, dur=0.5, vel=1.0, seed=0):
    """The Yemeni lute: skin-faced, gut strings in pairs. A short, round, woody note."""
    y = pluck(f, dur, t60=0.9, damp=0.38, bright=0.45 + 0.35 * vel, pick=0.25, seed=seed)
    y += 0.8 * pluck(f * 1.003, dur, t60=0.8, damp=0.40, bright=0.4 + 0.35 * vel, pick=0.3, seed=seed + 9)
    n = len(y)
    knock = filt(white(n, seed + 2) * decay(n, 0.02), bp(900, 1.2)) * 0.5
    y = filt(y + knock, hp(45), peak(260, 1.4, 5.0), peak(700, 2.0, 2.5), lp(5200))
    return fade(y * vel, 0.0005, 0.02)


def bass(f, dur=0.3, vel=1.0, seed=0):
    """The qanbus an octave down, with the fundamental filled in underneath so it carries on small speakers."""
    n = n_of(dur + 0.08)
    y = pluck(f, dur + 0.08, t60=0.7, damp=0.42, bright=0.5 + 0.3 * vel, pick=0.31, seed=seed)
    t = np.arange(n) / SR
    sub = (np.sin(TAU * f * t) + 0.5 * np.sin(TAU * 2 * f * t) + 0.2 * np.sin(TAU * 3 * f * t)) * decay(n, 0.45)
    knock = filt(white(n, seed + 2) * decay(n, 0.015), bp(800, 1.0)) * 0.3
    y = filt(y * 0.8 + sub * 0.9 + knock, hp(38), peak(240, 1.2, 3.0), lp(3800))
    e = np.ones(n)
    e[n_of(dur):] = np.linspace(1, 0, n - n_of(dur))
    return fade(soft(y * e, 1.2) * vel * 0.7, 0.0005, 0.01)


def chug(f, dur=0.16, vel=1.0, seed=0, open_=False):
    """The arcade's overdriven guitar: root, fifth and octave through a hard clipper and a small cabinet."""
    n = n_of(dur + 0.25)
    y = np.zeros(n)
    for i, m in enumerate((1.0, 1.4983, 2.0)):
        s = pluck(f * m, dur + 0.25, t60=2.5, damp=0.3, bright=0.9, pick=0.12, seed=seed + i)
        y[:len(s)] += s * (1.0, 0.8, 0.6)[i]
    y = filt(y, hp(70), peak(900, 1.0, 6.0))
    y = np.tanh(y * 6.0)
    y = filt(y, hp(90), lp(4200, 0.9), peak(2600, 1.5, 3.0), peak(180, 1.0, 2.0))
    # palm mute: the note is choked unless left open
    e = np.ones(n) if open_ else decay(n, 0.22)
    e[n_of(dur):] *= decay(n - n_of(dur), 0.06)
    return fade(y * e * vel * 0.5, 0.001, 0.01)


# ---------------------------------------------------------------- winds
_GRID = np.arange(0, 12000, 10.0)
_NASAL = 1.0 + 2.2 * np.exp(-0.5 * ((_GRID - 1500.0) / 420.0) ** 2) + 1.2 * np.exp(-0.5 * ((_GRID - 3100.0) / 600.0) ** 2)


def _reed_weights(k, f):
    # a single-reed pipe: strong odd harmonics, a hard nasal peak, a slow roll-off
    w = (1.0 / k ** 0.75) * np.where(k % 2 == 0, 0.42, 1.0)
    return w * _NASAL[np.minimum((f * 0.1).astype(np.int32), len(_NASAL) - 1)]


def _smooth_log(f, k):
    """Round the corners of a pitch line (in log pitch) without bending its ends."""
    ker = np.hanning(2 * k + 1)
    ker /= ker.sum()
    lf = np.log(f)
    pad = np.concatenate([np.full(k, lf[0]), lf, np.full(k, lf[-1])])
    return np.exp(np.convolve(pad, ker, mode='valid'))


def mizmar(notes, total, vel=1.0, seed=0):
    """A double clarinet: two pipes blown at once, never quite in tune with each other.
    notes: (start seconds, length seconds, frequency, grace) - grace is a flicked upper note before it."""
    n = n_of(total)
    r = rng(seed)
    f = np.full(n, notes[0][2] if notes else 440.0)
    amp = np.zeros(n)
    for (t0, ln, fr, grace) in notes:
        a, b = n_of(t0), min(n, n_of(t0 + ln))
        if b <= a:
            continue
        f[a:] = fr
        if grace:
            g = min(b, a + n_of(0.035))
            f[a:g] = grace
        e = np.ones(b - a)
        na, nr = min(len(e) // 2, n_of(0.012)), min(len(e) // 2, n_of(0.03))
        e[:na] = np.linspace(0.25, 1, na)
        e[-nr:] = np.linspace(1, 0.0, nr)
        amp[a:b] = np.maximum(amp[a:b], e)
    # smooth the pitch so notes join with a quick slide, and let it wander a little
    f = _smooth_log(f, n_of(0.006))
    drift = filt(r.normal(0, 1, n), lp(4.0)) * 0.0025
    out = np.zeros(n)
    for det, g in ((0.0, 1.0), (0.007, 0.8)):
        d2 = filt(r.normal(0, 1, n), lp(3.0)) * 0.002
        out += g * additive(f * (1 + det + drift + d2), _reed_weights, maxf=8000.0)
    buzz = 1.0 + 0.06 * filt(r.normal(0, 1, n), lp(60.0))
    out = filt(out * amp * buzz, hp(250), peak(1500, 2.0, 2.0), lp(8500))
    return out * vel * 0.16


def _brass_weights(bright):
    def w(k, f):
        return (1.0 / k) * np.exp(-f / (900.0 + 5200.0 * bright))
    return w


def brass(f, dur=0.3, vel=1.0, seed=0):
    """A unison band hit: the brass of a march, synthetic as the arcade's was."""
    n = n_of(dur + 0.12)
    r = rng(seed)
    out = np.zeros(n)
    e = adsr(n, 0.018, 0.09, 0.62, 0.11)
    for det in (-0.004, 0.0, 0.005):
        ff = np.full(n, f * (1 + det)) * (1 + 0.004 * np.exp(-np.arange(n) / (0.03 * SR)))
        # brightness opens fast and settles: do it in two layers and crossfade
        hi = additive(ff, _brass_weights(1.0), maxf=8000.0)
        lo = additive(ff, _brass_weights(0.25), maxf=8000.0)
        m = np.clip(e * 1.2, 0, 1) ** 2
        out += hi * m + lo * (1 - m)
    out = filt(out * e, hp(120), peak(1100, 1.2, 3.0))
    return fade(out * vel * 0.33, 0.001, 0.01)


def _flute_weights(k, f):
    return np.where(k == 1, 1.0, np.where(k == 2, 0.22, np.where(k == 3, 0.10, 0.03 / k)))


def flute(notes, total, vel=1.0, seed=0):
    """A reed flute (qassabah): a breathy tone with a slow shake on the long notes."""
    n = n_of(total)
    r = rng(seed)
    f = np.full(n, notes[0][2] if notes else 440.0)
    amp = np.zeros(n)
    vib = np.zeros(n)
    for (t0, ln, fr, grace) in notes:
        a, b = n_of(t0), min(n, n_of(t0 + ln))
        if b <= a:
            continue
        f[a:] = fr
        if grace:
            g = min(b, a + n_of(0.05))
            f[a:g] = grace
        m = b - a
        e = np.ones(m)
        na, nr = min(m // 2, n_of(0.04)), min(m // 2, n_of(0.09))
        e[:na] = np.linspace(0, 1, na) ** 0.7
        e[-nr:] = np.linspace(1, 0, nr)
        amp[a:b] = np.maximum(amp[a:b], e)
        # vibrato comes in after a moment on long notes
        v = np.clip((np.arange(m) / SR - 0.18) / 0.25, 0, 1)
        vib[a:b] = v
    f = _smooth_log(f, n_of(0.012))
    t = np.arange(n) / SR
    f = f * (1 + 0.006 * vib * np.sin(TAU * 5.2 * t))
    tone = additive(f, _flute_weights, maxf=7000.0)
    breath = filt(r.normal(0, 1, n), bp(1900, 0.9), hp(700), lp(4200)) * 0.13
    chiff = filt(r.normal(0, 1, n), bp(3500, 1.0)) * np.clip(np.gradient(amp) * SR * 0.02, 0, 1) * 0.6
    out = (tone * (1 + 0.1 * vib * np.sin(TAU * 5.2 * t + 1.0)) + breath + chiff) * amp
    return filt(out, hp(200), lp(7500)) * vel * 0.3


# ---------------------------------------------------------------- drums of the coast
def _membrane(f, t60, n, modes=((1.0, 1.0), (1.5, 0.5), (2.0, 0.3), (2.44, 0.2)), drop=0.35, drop_t=0.03):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for m, a in modes:
        ff = f * m * (1 + drop * np.exp(-t / drop_t))
        out += a * np.sin(TAU * np.cumsum(ff) / SR) * decay(n, t60 / (0.6 + 0.4 * m))
    return out


def marfa(vel=1.0, seed=0, pitch=73.42):
    """The large kettledrum that leads the ensemble: deep, round, long."""
    n = n_of(0.75)
    body = _membrane(pitch, 0.55, n, drop=0.5, drop_t=0.035)
    stick = filt(white(n, seed) * decay(n, 0.018), bp(1700, 0.9)) * 0.55
    y = filt(body + stick, hp(38), peak(90, 1.0, 3.0), lp(6000))
    return fade(soft(y * 0.9, 1.4) * vel, 0.0005, 0.02)


def tabl(vel=1.0, seed=0, kind='dum'):
    """The horizontal two-headed drum that keeps the pattern: an open low stroke and a dry high one."""
    if kind == 'dum':
        n = n_of(0.32)
        y = _membrane(128.0, 0.26, n, drop=0.3, drop_t=0.02)
        y += filt(white(n, seed) * decay(n, 0.012), bp(1200, 1.0)) * 0.35
        y = filt(y, hp(70), lp(5000))
    else:
        n = n_of(0.14)
        y = _membrane(410.0, 0.07, n, modes=((1.0, 1.0), (1.59, 0.6), (2.14, 0.4), (2.65, 0.3)), drop=0.15, drop_t=0.008)
        y += filt(white(n, seed) * decay(n, 0.03), bp(2600, 0.8)) * 0.8
        y = filt(y, hp(220), lp(7500))
    return fade(y * vel * 0.8, 0.0003, 0.01)


def tunk(vel=1.0, seed=0, pitch=300.0):
    """A small kettledrum, the one that answers and improvises: tight, bright, quick."""
    n = n_of(0.16)
    y = _membrane(pitch, 0.11, n, modes=((1.0, 1.0), (1.5, 0.45), (2.0, 0.25)), drop=0.25, drop_t=0.01)
    y += filt(white(n, seed) * decay(n, 0.02), bp(3200, 0.8)) * 0.55
    return fade(filt(y, hp(160), lp(8000)) * vel * 0.75, 0.0003, 0.01)


def sahn(vel=1.0, seed=0, accent=False):
    """The copper tray, tapped with the fingertips: a light metallic tick."""
    n = n_of(0.11 if not accent else 0.2)
    t = np.arange(n) / SR
    r = rng(seed)
    y = np.zeros(n)
    for f, a in ((2140, 1.0), (3370, 0.8), (5290, 0.6), (7410, 0.45), (9120, 0.3)):
        y += a * np.sin(TAU * f * (1 + 0.004 * r.normal()) * t) * decay(n, (0.05 if not accent else 0.12) * 2140 / f + 0.015)
    y += filt(white(n, seed) * decay(n, 0.008), hp(5000)) * 0.6
    return fade(filt(y, hp(1500)) * vel * 0.22, 0.0002, 0.005)


def jingle(vel=1.0, seed=0):
    """The frame drum's rattle on the backbeat."""
    n = n_of(0.13)
    y = filt(white(n, seed), hp(4300), peak(7200, 1.5, 5.0), lp(11000)) * decay(n, 0.09)
    y *= 1 + 0.5 * np.sin(TAU * 43 * np.arange(n) / SR)
    return fade(y * vel * 0.2, 0.0005, 0.01)


def clap(vel=1.0, seed=0):
    n = n_of(0.2)
    y = np.zeros(n)
    r = rng(seed)
    for i, d in enumerate((0.0, 0.011, 0.021, 0.034)):
        a = n_of(d + r.uniform(0, 0.002))
        m = n - a
        y[a:] += white(m, seed + i) * decay(m, 0.03 if i < 3 else 0.14) * (0.7 if i < 3 else 1.0)
    return fade(filt(y, bp(1400, 0.7), hp(500), lp(7000)) * vel * 0.55, 0.0003, 0.01)


# ---------------------------------------------------------------- the arcade's kit
def kick(vel=1.0, seed=0):
    n = n_of(0.3)
    t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t / 0.022)
    y = np.sin(TAU * np.cumsum(f) / SR) * decay(n, 0.24)
    y += filt(white(n, seed) * decay(n, 0.006), lp(3500)) * 0.4
    return fade(filt(soft(y, 1.6), hp(28)) * vel * 0.95, 0.0003, 0.01)


def snare(vel=1.0, seed=0, ghost=False):
    """The march snare: a short body and a rattle of wires."""
    n = n_of(0.22 if not ghost else 0.09)
    t = np.arange(n) / SR
    body = (np.sin(TAU * 190 * t) + 0.6 * np.sin(TAU * 286 * t)) * decay(n, 0.07)
    wires = filt(white(n, seed), bp(4200, 0.5), hp(1300)) * decay(n, 0.17 if not ghost else 0.06)
    y = body * 0.55 + wires * 0.9
    return fade(filt(y, hp(140), lp(9000)) * vel * (0.7 if not ghost else 0.3), 0.0003, 0.01)


def bell(f, dur=0.6, vel=1.0):
    """A small struck bell for pickups and medals (two-operator FM)."""
    n = n_of(dur)
    t = np.arange(n) / SR
    mod = np.sin(TAU * f * 3.5 * t) * (2.4 * decay(n, dur * 0.35))
    y = np.sin(TAU * f * t + mod) * decay(n, dur)
    y += 0.3 * np.sin(TAU * f * 2.0 * t) * decay(n, dur * 0.6)
    return fade(y * vel * 0.4, 0.0005, 0.01)
