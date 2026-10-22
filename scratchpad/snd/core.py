# core.py - a small synthesis toolkit: oscillators, plucked strings, filters, reverb, mixing, export.
import os
import subprocess
import wave
import numpy as np
from scipy import signal

SR = 44100
TAU = 2 * np.pi


def n_of(dur):
    return int(round(dur * SR))


def tt(dur):
    return np.arange(n_of(dur)) / SR


def rng(seed):
    return np.random.default_rng(seed)


def white(n, seed=0):
    return rng(seed).uniform(-1.0, 1.0, n)


def decay(n, t60):
    """Exponential decay reaching -60 dB at t60 seconds."""
    return np.exp(-6.908 * np.arange(n) / (t60 * SR))


def fade(x, a=0.002, r=0.004):
    """Short linear fades so nothing starts or stops with a click."""
    x = np.array(x, dtype=np.float64)
    na, nr = min(len(x) // 2, n_of(a)), min(len(x) // 2, n_of(r))
    if na:
        x[:na] *= np.linspace(0, 1, na)
    if nr:
        x[-nr:] *= np.linspace(1, 0, nr)
    return x


def adsr(n, a, d, s, r):
    """Attack, decay to sustain level s, release at the end. Times in seconds."""
    e = np.full(n, s, dtype=np.float64)
    na, nd, nr = n_of(a), n_of(d), n_of(r)
    na = min(na, n)
    e[:na] = np.linspace(0, 1, na, endpoint=False)
    nd = min(nd, n - na)
    if nd > 0:
        e[na:na + nd] = 1 + (s - 1) * (1 - np.exp(-4 * np.arange(nd) / nd)) / (1 - np.exp(-4))
    nr = min(nr, n)
    if nr > 0:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


# ---------------------------------------------------------------- filters (RBJ biquads)
def _norm(b, a):
    return np.array([[b[0] / a[0], b[1] / a[0], b[2] / a[0], 1.0, a[1] / a[0], a[2] / a[0]]])


def lp(f, q=0.707):
    w = TAU * f / SR
    al = np.sin(w) / (2 * q)
    c = np.cos(w)
    return _norm([(1 - c) / 2, 1 - c, (1 - c) / 2], [1 + al, -2 * c, 1 - al])


def hp(f, q=0.707):
    w = TAU * f / SR
    al = np.sin(w) / (2 * q)
    c = np.cos(w)
    return _norm([(1 + c) / 2, -(1 + c), (1 + c) / 2], [1 + al, -2 * c, 1 - al])


def bp(f, q=1.0):
    w = TAU * f / SR
    al = np.sin(w) / (2 * q)
    c = np.cos(w)
    return _norm([al, 0, -al], [1 + al, -2 * c, 1 - al])


def peak(f, q, gain_db):
    A = 10 ** (gain_db / 40)
    w = TAU * f / SR
    al = np.sin(w) / (2 * q)
    c = np.cos(w)
    return _norm([1 + al * A, -2 * c, 1 - al * A], [1 + al / A, -2 * c, 1 - al / A])


def shelf_hi(f, gain_db, s=0.8):
    A = 10 ** (gain_db / 40)
    w = TAU * f / SR
    c, sn = np.cos(w), np.sin(w)
    al = sn / 2 * np.sqrt((A + 1 / A) * (1 / s - 1) + 2)
    k = 2 * np.sqrt(A) * al
    return _norm([A * ((A + 1) + (A - 1) * c + k), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - k)],
                 [(A + 1) - (A - 1) * c + k, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - k])


def shelf_lo(f, gain_db, s=0.8):
    A = 10 ** (gain_db / 40)
    w = TAU * f / SR
    c, sn = np.cos(w), np.sin(w)
    al = sn / 2 * np.sqrt((A + 1 / A) * (1 / s - 1) + 2)
    k = 2 * np.sqrt(A) * al
    return _norm([A * ((A + 1) - (A - 1) * c + k), 2 * A * ((A - 1) - (A + 1) * c), A * ((A + 1) - (A - 1) * c - k)],
                 [(A + 1) + (A - 1) * c + k, -2 * ((A - 1) + (A + 1) * c), (A + 1) + (A - 1) * c - k])


def filt(x, *sections):
    y = np.asarray(x, dtype=np.float64)
    for s in sections:
        y = signal.sosfilt(s, y, axis=0)
    return y


def sweep_filter(x, f_start, f_end, kind='lp', q=0.8, steps=24, curve=1.0):
    """A filter whose corner moves over the sound: cut the sound into overlapping blocks,
    filter each with its own corner, and crossfade."""
    n = len(x)
    out = np.zeros(n)
    wsum = np.zeros(n)
    hop = max(64, n // steps)
    win = np.hanning(2 * hop)
    mk = {'lp': lp, 'hp': hp, 'bp': bp}[kind]
    pos = -hop
    while pos < n:
        a, b = max(0, pos), min(n, pos + 2 * hop)
        if b <= a:
            pos += hop
            continue
        mid = (a + b) / 2 / max(1, n)
        f = f_start * (f_end / f_start) ** (mid ** curve)
        # filter with some lead-in so the block starts settled
        lead = max(0, a - 2048)
        seg = filt(x[lead:b], mk(min(f, SR * 0.45), q))[a - lead:]
        w = win[a - pos:b - pos]
        out[a:b] += seg * w
        wsum[a:b] += w
        pos += hop
    return out / np.maximum(wsum, 1e-6)


# ---------------------------------------------------------------- plucked string (Karplus-Strong)
def pluck(f, dur, t60=1.6, damp=0.25, bright=0.6, pick=0.18, seed=0):
    """A plucked string. damp 0..0.5: how fast the top end dies (0.5 dull, 0.05 wiry).
    bright 0..1: how sharp the plectrum is. pick: where along the string it is plucked."""
    damp = float(np.clip(damp, 0.01, 0.5))
    N = int(SR / f - damp)
    N = max(N, 4)
    n = n_of(dur)
    exc = white(N, seed)
    # plectrum hardness: a one-pole lowpass over the burst
    c = 0.05 + 0.95 * bright
    for i in range(1, N):
        exc[i] = c * exc[i] + (1 - c) * exc[i - 1]
    # pluck position: comb the burst
    d = max(1, int(pick * N))
    exc = exc - np.roll(exc, d) * 0.9
    exc -= exc.mean()
    exc /= np.max(np.abs(exc)) + 1e-9
    x = np.zeros(n + 64)
    x[:N] = exc
    rho = np.exp(-6.908 / (f * t60))
    a = np.zeros(N + 2)
    a[0] = 1.0
    a[N] = -rho * (1 - damp)
    a[N + 1] = -rho * damp
    y = signal.lfilter([1.0], a, x)
    # the loop is N + damp samples long; pull it to the exact pitch
    fa = SR / (N + damp)
    r = f / fa
    idx = np.arange(n) * r
    y = np.interp(idx, np.arange(len(y)), y, right=0.0)
    return y


# ---------------------------------------------------------------- additive voices
def additive(f0, weights, maxf=9000.0, chunk=4096):
    """Sum of harmonics of a moving pitch. weights(k, f) -> amplitude for harmonic numbers k (K,1)
    at frequencies f (K,chunk)."""
    f0 = np.asarray(f0, dtype=np.float64)
    n = len(f0)
    ph = TAU * np.cumsum(f0) / SR
    K = int(maxf / max(20.0, f0.min()))
    k = np.arange(1, K + 1)[:, None]
    out = np.zeros(n)
    for a in range(0, n, chunk):
        b = min(n, a + chunk)
        f = k * f0[None, a:b]
        w = weights(k, f)
        w = np.where(f < maxf, w, 0.0)
        out[a:b] = np.sum(w * np.sin(k * ph[None, a:b]), axis=0)
    return out


def glide(freqs, times, n, slide=0.012):
    """A pitch line through note changes with a short slide between them."""
    f = np.zeros(n)
    idx = [n_of(t) for t in times] + [n]
    for i, fr in enumerate(freqs):
        f[idx[i]:idx[i + 1]] = fr
    k = max(1, n_of(slide))
    ker = np.hanning(2 * k + 1)
    ker /= ker.sum()
    pad = np.concatenate([np.full(k, f[0]), f, np.full(k, f[-1])])
    return np.exp(np.convolve(np.log(np.maximum(pad, 1.0)), ker, mode='valid'))


# ---------------------------------------------------------------- space
def reverb_ir(rt60=1.1, predelay=0.012, damp=5000.0, seed=1, early=True):
    n = n_of(rt60 * 1.2)
    out = []
    for ch in (0, 1):
        r = rng(seed + ch * 17)
        ir = r.normal(0, 1, n) * decay(n, rt60)
        ir = filt(ir, lp(damp), hp(180))
        # the top end dies sooner
        ir2 = filt(ir, lp(damp * 0.35))
        mix = np.linspace(0, 1, n) ** 0.6
        ir = ir * (1 - mix) + ir2 * mix * 1.6
        if early:
            for d, g in ((0.007, 0.5), (0.013, -0.35), (0.021, 0.3), (0.034, -0.22)):
                i = n_of(d * (1 + 0.13 * ch))
                ir[i] += g * 6
        pd = np.zeros(n_of(predelay))
        ir = np.concatenate([pd, ir])
        ir /= np.sqrt(np.sum(ir ** 2))
        out.append(ir)
    return np.stack(out, axis=1)


def convolve(x, ir):
    """Mono or stereo in, stereo out."""
    x = np.asarray(x)
    if x.ndim == 1:
        return np.stack([signal.fftconvolve(x, ir[:, 0]), signal.fftconvolve(x, ir[:, 1])], axis=1)
    return np.stack([signal.fftconvolve(x[:, 0], ir[:, 0]), signal.fftconvolve(x[:, 1], ir[:, 1])], axis=1)


def pan(x, p=0.0):
    """Constant-power pan, p from -1 (left) to 1 (right)."""
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], axis=1)


class Bus:
    """A stereo buffer that sounds are dropped onto at times in seconds."""

    def __init__(self, dur):
        self.x = np.zeros((n_of(dur), 2))

    def put(self, snd, t, gain=1.0, p=0.0):
        s = np.asarray(snd)
        if s.ndim == 1:
            s = pan(s, p)
        i = n_of(t)
        if i >= len(self.x):
            return
        if i < 0:
            s = s[-i:]
            i = 0
        j = min(len(self.x), i + len(s))
        self.x[i:j] += s[:j - i] * gain

    def add(self, other, gain=1.0):
        m = min(len(self.x), len(other.x))
        self.x[:m] += other.x[:m] * gain


# ---------------------------------------------------------------- levels
def db(x):
    return 20 * np.log10(max(1e-12, x))


def rms(x):
    return float(np.sqrt(np.mean(np.square(x))))


def lufs(x):
    """Integrated loudness, BS.1770 style (K-weighting, 400 ms blocks, absolute and relative gates)."""
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = x[:, None]
    # K-weighting at 44.1 kHz: high shelf (+4 dB above ~1.5 kHz) then a 38 Hz highpass
    y = filt(x, shelf_hi(1500, 4.0, s=1.0), hp(38, 0.5))
    blk, hop = n_of(0.4), n_of(0.1)
    if len(y) < blk:
        ms = np.mean(np.sum(y ** 2, axis=1))
        return -0.691 + 10 * np.log10(max(ms, 1e-12))
    z = []
    for a in range(0, len(y) - blk + 1, hop):
        z.append(np.sum(np.mean(y[a:a + blk] ** 2, axis=0)))
    z = np.array(z)
    l = -0.691 + 10 * np.log10(np.maximum(z, 1e-12))
    keep = z[l > -70]
    if not len(keep):
        return -70.0
    rel = -0.691 + 10 * np.log10(np.mean(keep)) - 10
    keep = z[l > max(rel, -70)]
    return float(-0.691 + 10 * np.log10(np.mean(keep)))


def limit(x, ceiling_db=-1.0, lookahead=0.004, release=0.12, curve=False):
    """A look-ahead peak limiter: turns down ahead of each peak and lets go slowly."""
    x = np.asarray(x, dtype=np.float64)
    mono = x.ndim == 1
    if mono:
        x = x[:, None]
    ceil = 10 ** (ceiling_db / 20)
    pk = np.max(np.abs(x), axis=1)
    need = np.minimum(1.0, ceil / np.maximum(pk, 1e-9))
    la = n_of(lookahead)
    # earliest minimum over the look-ahead window
    from scipy.ndimage import minimum_filter1d
    g = minimum_filter1d(need, size=2 * la + 1, mode='nearest')
    # smooth: fast attack is built into the look-ahead; slow release
    rel = np.exp(-1.0 / (release * SR))
    out = np.empty_like(g)
    cur = 1.0
    k = 1.0 - rel
    for i, gi in enumerate(g.tolist()):
        if gi < cur:
            cur = gi
        else:
            cur += (gi - cur) * k
        out[i] = cur
    win = np.hanning(2 * la + 1)
    win /= win.sum()
    padded = np.concatenate([np.full(la, out[0]), out, np.full(la, out[-1])])
    out = np.minimum(np.convolve(padded, win, mode='valid'), g)
    y = x * out[:, None]
    if curve:
        return (y[:, 0] if mono else y), float(db(out.min())), out
    return (y[:, 0] if mono else y), float(db(out.min()))


def to_level(x, target_lufs, ceiling_db=-1.0):
    """Bring a sound to a loudness, limiting what pokes over the ceiling."""
    l = lufs(x)
    g = 10 ** ((target_lufs - l) / 20)
    y, red = limit(np.asarray(x) * g, ceiling_db)
    return y, l, red


def to_peak(x, peak_db=-1.0):
    m = np.max(np.abs(x))
    return x * (10 ** (peak_db / 20) / m) if m > 0 else x


def soft(x, drive=1.0):
    return np.tanh(np.asarray(x) * drive) / np.tanh(drive)


# ---------------------------------------------------------------- files
def write_wav(path, x):
    x = np.asarray(x)
    if x.ndim == 1:
        x = x[:, None]
    x = np.clip(x, -1.0, 1.0)
    # triangular dither before rounding to 16 bits
    r = rng(abs(hash(os.path.basename(path))) % (2 ** 31))
    d = (r.uniform(-0.5, 0.5, x.shape) + r.uniform(-0.5, 0.5, x.shape)) / 32767.0
    pcm = np.round((x + d) * 32767.0).clip(-32768, 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(x.shape[1])
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def to_mp3(wav, mp3, kbps=128):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', wav, '-codec:a', 'libmp3lame',
                    '-b:a', '%dk' % kbps, '-write_xing', '1', mp3], check=True)
    return os.path.getsize(mp3)


# The game's sound at a lower rate (build 0.8.47; Khaled, 20 Oct: "Do the offer items", the lighter first load): LAME's
# variable bitrate at its best algorithm quality instead of a constant 80-192 kbps. A variable rate spends next to nothing
# on the strips' gaps (the voices at V7 keep the fidelity they had at 80 kbps in 57% of the bytes). Lower V = better.
VBR = dict(music=6, jingle=6, sfx=2, voices=7)


def to_mp3_vbr(wav, mp3, q):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', wav, '-codec:a', 'libmp3lame',
                    '-compression_level', '0', '-q:a', str(q), '-write_xing', '1', mp3], check=True)
    return os.path.getsize(mp3)


MP3_FRAME = 1152


def frame_aligned(x):
    """A music loop (one period of something that repeats) resampled to the nearest whole number of MP3 frames. Then the
    encoder meets the same frames at both ends of the loop, and the seam decodes the same on both sides, to the sample
    (measured: the loops that were already whole frames long came out that way, the others did not). Fourier resampling
    treats the loop as the periodic thing it is, so it stays seamless; the length (and the pitch) moves by a few
    hundredths of a percent, under a cent. Returns the loop and the pitch change in cents."""
    n = len(x)
    m = max(MP3_FRAME, int(round(n / MP3_FRAME)) * MP3_FRAME)
    if m == n:
        return x, 0.0
    return signal.resample(x, m, axis=0), 1200 * np.log2(n / m)
