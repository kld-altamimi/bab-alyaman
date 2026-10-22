# sfx.py - the Strait's sound effects, all synthesised. Each function returns a mono array.
# House rules: the player's guns are fuller and brighter than the enemy's, so a shot tells you whose
# it was; hits are cartoon hits; anything the interface says, it says on the band's own instruments.
import numpy as np
from core import *
import inst as I

H = I.hz


def _place(n, parts):
    """Lay (start seconds, sound, gain) parts on one buffer n seconds long."""
    out = np.zeros(n_of(n))
    for t, s, g in parts:
        a = n_of(t)
        if a >= len(out):
            continue
        b = min(len(out), a + len(s))
        out[a:b] += s[:b - a] * g
    return out


def _metal(freqs, t60, seed=0, dur=None, spread=0.004):
    """Struck metal: a handful of partials that are not in tune with each other."""
    dur = dur or t60 * 1.2
    n = n_of(dur)
    t = np.arange(n) / SR
    r = rng(seed)
    y = np.zeros(n)
    for i, f in enumerate(freqs):
        f = f * (1 + spread * r.normal())
        y += (1.0 / (1 + 0.35 * i)) * np.sin(TAU * f * t + r.uniform(0, TAU)) * decay(n, t60 / (1 + 0.25 * i))
    return y / len(freqs) ** 0.5


def _gun(seed=0, lo=600, hi=5200, crack=0.05, body=130.0, body_t=0.07, tail=0.3, tail_g=0.14, drive=1.6, weight=0.45):
    """A shot: a snap, a band of noise that dies fast, a short low body, and the report rolling away."""
    n = n_of(tail + 0.06)
    t = np.arange(n) / SR
    cr = filt(white(n, seed), hp(lo), lp(hi)) * decay(n, crack)
    snap = filt(white(n, seed + 2), hp(2500)) * decay(n, 0.008)
    bd = np.sin(TAU * np.cumsum(body * (1 + 1.6 * np.exp(-t / 0.011))) / SR) * decay(n, body_t)
    tl = filt(white(n, seed + 1), lp(1700), hp(180)) * decay(n, tail) * tail_g
    y = cr * 1.25 + snap * 0.9 + bd * weight + tl
    return fade(soft(y * drive, 1.4), 0.0002, 0.02)


# ---------------------------------------------------------------- the player's weapons
def pistol(seed=0):
    return _gun(seed, 800, 7000, 0.042, 175.0, 0.05, 0.22, 0.10, weight=0.35)


def rifle_shot(seed=0):
    return _gun(seed, 500, 6500, 0.06, 132.0, 0.07, 0.3, 0.14, weight=0.45)


def rifle_burst(seed=0):
    return _place(0.62, [(i * 0.085, rifle_shot(seed + i), 1.0 - 0.06 * i) for i in range(3)])


def heavy_mg(seed=0, shots=12, gap=0.095):
    r = rng(seed)
    parts = []
    for i in range(shots):
        s = _gun(seed + i, 350, 5000, 0.07, 100.0 * (1 + 0.03 * r.normal()), 0.09, 0.26, 0.16, drive=1.9, weight=0.6)
        parts.append((i * gap + r.uniform(0, 0.004), s, 0.92 + 0.08 * r.uniform()))
    for i in range(shots // 2):
        f = r.uniform(3200, 5200)
        parts.append((0.12 + i * gap * 2 + r.uniform(0, 0.05), _metal([f, f * 1.48, f * 2.1], 0.09, seed + 40 + i) * 0.5, 0.25))
    return _place(shots * gap + 0.5, parts)


def shotgun(seed=0):
    n = n_of(0.75)
    t = np.arange(n) / SR
    boom = filt(white(n, seed), lp(3200), hp(110)) * decay(n, 0.26)
    sub = np.sin(TAU * np.cumsum(78 * (1 + 1.2 * np.exp(-t / 0.02))) / SR) * decay(n, 0.2)
    tail = filt(white(n, seed + 1), lp(1200), hp(150)) * decay(n, 0.7) * 0.2
    y = soft((boom * 1.1 + sub * 1.0 + tail) * 1.8, 1.5)

    def click(f, s):
        m = n_of(0.05)
        return filt(white(m, s) * decay(m, 0.022), bp(f, 2.0)) * 0.6
    return _place(1.05, [(0.0, y, 1.0), (0.46, click(1700, seed + 2), 1.0), (0.6, click(2500, seed + 3), 1.0)])


def marksman(seed=0):
    n = n_of(1.3)
    crack = filt(white(n, seed), hp(1100), lp(9000)) * decay(n, 0.045)
    t = np.arange(n) / SR
    body = np.sin(TAU * np.cumsum(112 * (1 + 2.0 * np.exp(-t / 0.01))) / SR) * decay(n, 0.09)
    y = soft((crack * 1.6 + body * 0.5) * 1.8, 1.5)
    echo = filt(y, lp(1500))
    out = _place(1.5, [(0.0, y, 1.0), (0.19, echo, 0.32), (0.41, filt(echo, lp(900)), 0.18), (0.72, filt(echo, lp(600)), 0.09)])
    m = n_of(0.05)
    bolt = filt(white(m, seed + 5) * decay(m, 0.02), bp(2200, 2.0)) * 0.5
    return out + _place(1.5, [(0.95, bolt, 1.0), (1.08, bolt, 0.8)])


def grenade_throw(seed=0):
    n = n_of(0.22)
    y = sweep_filter(white(n, seed), 500, 2000, 'bp', q=1.6, steps=10) * np.hanning(n) ** 0.7
    return fade(y * 0.9)


def grenade_bounce(seed=0):
    a = _metal([1750, 2890, 4310], 0.05, seed)
    return _place(0.35, [(0.0, a, 1.0), (0.17, _metal([1820, 2950, 4400], 0.04, seed + 1), 0.55)])


def explosion(size=1.0, seed=0, crackle=True):
    """size 0.6 a grenade, 1.0 a fuel drum, 1.6 the battery going up."""
    dur = 0.75 + 0.75 * size
    n = n_of(dur)
    t = np.arange(n) / SR
    r = rng(seed)
    body = sweep_filter(white(n, seed), 5200, 170, 'lp', q=0.7, steps=28, curve=0.45) * decay(n, dur * 0.8)
    body[:n_of(0.004)] *= np.linspace(0, 1, n_of(0.004))
    sub = np.sin(TAU * np.cumsum(34 + 55 * np.exp(-t / (0.09 * size))) / SR) * decay(n, dur * 0.6)
    thud = filt(white(n, seed + 3) * decay(n, 0.05), lp(900)) * 1.2
    y = body * 1.2 + sub * (0.9 + 0.25 * size) + thud
    if crackle:
        k = np.zeros(n)
        for _ in range(int(40 * size)):
            i = int(r.uniform(0.08, dur * 0.9) * SR)
            k[i] += r.uniform(0.2, 1.0) * (1 - i / n)
        y += filt(k, bp(2200, 0.8), hp(900), lp(5000)) * 1.8
    return fade(soft(y * 1.5, 1.6), 0.0003, 0.08)


def explosion_small(seed=0):
    return explosion(0.6, seed)


def explosion_drum(seed=0):
    clang = _metal([210, 388, 615, 1040, 1730], 0.22, seed + 9) * 1.1
    whoosh = sweep_filter(white(n_of(1.1), seed + 4), 900, 250, 'lp', steps=12) * decay(n_of(1.1), 0.9) * 0.45
    return _place(1.7, [(0.0, explosion(1.0, seed), 1.0), (0.0, clang, 0.7), (0.25, whoosh, 1.0)])


def explosion_big(seed=0):
    return _place(3.0, [(0.0, explosion(1.3, seed), 1.0), (0.22, explosion(0.8, seed + 1), 0.75), (0.5, explosion(1.6, seed + 2), 1.0),
                        (0.95, explosion(0.7, seed + 3), 0.55), (0.0, _metal([140, 315, 470, 825, 1260], 0.5, seed + 4), 0.8)])


def rocket(seed=0):
    n = n_of(0.9)
    t = np.arange(n) / SR
    hiss = sweep_filter(white(n, seed), 500, 2600, 'bp', q=1.2, steps=20) * (np.minimum(1, t / 0.03) * decay(n, 0.8))
    rumble = filt(white(n, seed + 1), lp(160)) * (1 + 0.5 * np.sin(TAU * 31 * t)) * decay(n, 0.6) * 2.2
    pop = filt(white(n_of(0.05), seed + 2) * decay(n_of(0.05), 0.02), lp(2500)) * 1.2
    y = hiss * 0.9 + rumble
    y[:len(pop)] += pop
    return fade(soft(y * 1.4, 1.3), 0.0005, 0.06)


# ---------------------------------------------------------------- support
def mortar(seed=0):
    n = n_of(0.95)
    t = np.arange(n) / SR
    f = 2500 * (900 / 2500) ** ((t / t[-1]) ** 1.6)
    wh = np.sin(TAU * np.cumsum(f) / SR) * (0.15 + 0.85 * (t / t[-1]) ** 1.5)
    wh += filt(white(n, seed), bp(1800, 1.5)) * 0.12 * (t / t[-1])
    return _place(2.4, [(0.0, fade(wh * 0.5, 0.02, 0.01), 1.0), (0.94, explosion(0.9, seed + 1), 1.0)])


def sniper_overwatch(seed=0):
    n = n_of(0.05)
    t = np.arange(n) / SR
    zipp = np.sin(TAU * np.cumsum(6500 * (2000 / 6500) ** (t / t[-1])) / SR) * np.hanning(n) * 0.5
    far = filt(_gun(seed, 500, 2400, 0.06, 105.0, 0.09, 0.9, 0.3), lp(1700))
    thud = filt(white(n_of(0.08), seed + 2) * decay(n_of(0.08), 0.03), lp(700)) * 1.0
    return _place(1.4, [(0.0, zipp, 1.0), (0.03, thud, 1.0), (0.24, far, 0.8), (0.52, filt(far, lp(800)), 0.3)])


def radio_full(seed=0):
    sq = filt(white(n_of(0.09), seed), bp(2100, 1.2)) * np.hanning(n_of(0.09)) * 0.5
    def beep(f):
        m = n_of(0.07)
        return fade(np.sin(TAU * f * np.arange(m) / SR) * 0.4, 0.004, 0.006)
    y = _place(0.34, [(0.0, sq, 1.0), (0.1, beep(1250), 1.0), (0.19, beep(1660), 1.0)])
    return filt(y, hp(500), lp(3400))


def radio_call(seed=0):
    m = n_of(0.02)
    click = filt(white(m, seed) * decay(m, 0.006), bp(2500, 1.5))
    st = filt(white(n_of(0.26), seed + 1), bp(1900, 0.7)) * fade(np.ones(n_of(0.26)), 0.01, 0.03) * 0.33
    k = n_of(0.13)
    roger = fade(np.sin(TAU * 1040 * np.arange(k) / SR) * 0.38, 0.005, 0.01)
    return filt(_place(0.5, [(0.0, click, 1.0), (0.02, st, 1.0), (0.3, roger, 1.0)]), hp(500), lp(3400))


# ---------------------------------------------------------------- what bullets hit
def ricochet(seed=0):
    n = n_of(0.42)
    t = np.arange(n) / SR
    f = 3300 * (850 / 3300) ** (t / t[-1]) * (1 + 0.035 * np.sin(TAU * 31 * t))
    whine = np.sin(TAU * np.cumsum(f) / SR) * decay(n, 0.34) * (0.75 + 0.25 * np.sin(TAU * 27 * t))
    return _place(0.45, [(0.0, _metal([2300, 3650, 5200], 0.035, seed), 1.0), (0.008, fade(whine * 0.55, 0.004, 0.02), 1.0)])


def door_clang(seed=0):
    m = n_of(0.01)
    tick = filt(white(m, seed) * decay(m, 0.004), hp(1500)) * 0.7
    y = _metal([232, 418, 644, 1012, 1685, 2460], 0.17, seed) + _metal([1012, 1685, 2460, 3320], 0.07, seed + 1, dur=0.17 * 1.2) * 1.2
    y[:m] += tick
    return fade(y * 1.3, 0.0002, 0.02)


def door_break(seed=0):
    """A pickup door shot off its hinges: a flat bang, the panel ringing as it goes, the window, and the thing landing."""
    nb = n_of(0.09)
    bang = filt(white(nb, seed) * decay(nb, 0.035), lp(2600), hp(140)) * 1.4
    ring = _metal([148, 262, 395, 612, 940, 1480], 0.42, seed + 1)
    r = rng(seed + 2)
    n = n_of(0.5)
    k = np.zeros(n)
    for _ in range(24):
        i = int(r.uniform(0.03, 0.42) * SR)
        k[i] += r.uniform(0.3, 1.0) * (1 - i / n)
    glass = filt(k, bp(5200, 2.0), hp(3000)) * 2.4
    drop = _metal([190, 344, 520, 815], 0.14, seed + 3)
    return fade(_place(0.8, [(0.0, bang, 1.0), (0.0, ring, 0.8), (0.02, glass, 0.6), (0.40, drop, 0.55)]), 0.0003, 0.03)


def bash(seed=0):
    """A door swung like a bat: the air it moves, then the flat of it arriving."""
    n = n_of(0.3)
    sw = sweep_filter(white(n, seed), 420, 2200, 'bp', q=1.3, steps=12) * np.hanning(n) ** 0.8 * 0.55
    m = n_of(0.16)
    t = np.arange(m) / SR
    thump = np.sin(TAU * 74 * t) * decay(m, 0.09) + filt(white(m, seed + 1) * decay(m, 0.03), lp(1400)) * 0.8
    clang = _metal([232, 418, 644], 0.12, seed + 2) * 0.5
    return fade(_place(0.5, [(0.0, sw, 1.0), (0.29, thump, 1.0), (0.29, clang, 0.8)]), 0.0003, 0.03)


def hit_sand(seed=0):
    n = n_of(0.09)
    y = filt(white(n, seed), lp(1500), hp(250)) * decay(n, 0.05) + filt(white(n, seed + 1), hp(4000)) * decay(n, 0.03) * 0.25
    return fade(y * 0.8)


def hit_body(seed=0):
    n = n_of(0.11)
    t = np.arange(n) / SR
    bonk = np.sin(TAU * np.cumsum(520 * (360 / 520) ** (t / t[-1])) / SR) * decay(n, 0.07)
    thud = filt(white(n, seed) * decay(n, 0.03), lp(900))
    return fade(bonk * 0.6 + thud * 0.8)


def launcher_hit(seed=0):
    thud = filt(white(n_of(0.1), seed) * decay(n_of(0.1), 0.04), lp(700)) * 1.4
    y = _metal([141, 312, 468, 822, 1255, 1900], 0.45, seed + 1) * 1.5
    y[:len(thud)] += thud
    return fade(soft(y, 1.2), 0.0002, 0.03)


# ---------------------------------------------------------------- moving
def step_sand(seed=0):
    n = n_of(0.07)
    y = filt(white(n, seed), bp(1300 + 250 * (seed % 2), 0.8)) * np.hanning(n) ** 1.5
    y += filt(white(n, seed + 7) * decay(n, 0.02), lp(260)) * 0.9
    return fade(y * 0.5)


def steps(seed=0):
    return _place(0.75, [(i * 0.17, step_sand(seed + i), 1.0 - 0.1 * (i % 2)) for i in range(4)])


def jump(seed=0):
    n = n_of(0.12)
    t = np.arange(n) / SR
    y = np.sin(TAU * np.cumsum(270 * (540 / 270) ** (t / t[-1])) / SR) * np.hanning(n) * 0.35
    y += filt(white(n, seed), bp(900, 1.0)) * np.hanning(n) * 0.2
    return fade(y)


def land(seed=0):
    n = n_of(0.12)
    t = np.arange(n) / SR
    y = np.sin(TAU * 92 * t) * decay(n, 0.06) * 0.6 + filt(white(n, seed), bp(700, 0.6)) * decay(n, 0.05) * 1.2
    return fade(y * 0.8)


# ---------------------------------------------------------------- pickups and the interface: the band's instruments
def _notes(seq, gap, fn, tail=0.6, **kw):
    return _place(len(seq) * gap + tail, [(i * gap, fn(H(nm), **kw), 1.0) for i, nm in enumerate(seq)])


def pickup_weapon(seed=0):
    y = _notes(['D5', 'A5', 'D6'], 0.055, I.lyre, dur=0.7, seed=seed)
    return y + _place(len(y) / SR, [(0.11, I.bell(H('D6'), 0.5), 0.8)])


def pickup_ammo(seed=0):
    return _notes(['A5', 'D6'], 0.05, I.lyre, tail=0.3, dur=0.3, seed=seed)


def pickup_grenades(seed=0):
    m = n_of(0.03)
    tick = filt(white(m, seed) * decay(m, 0.01), bp(1500, 2.0))
    return _place(0.6, [(0.0, tick, 0.8), (0.06, tick, 0.8), (0.12, tick, 0.8), (0.17, I.lyre(H('G5'), 0.4, seed=seed), 0.9)])


def coin(seed=0):
    return _place(0.5, [(0.0, I.bell(H('A5'), 0.12), 1.0), (0.07, I.bell(H('D6'), 0.4), 1.0)])


def medal(seed=0):
    seq = ['Bb5', 'D6', 'F6', 'Bb6']
    y = _place(1.6, [(i * 0.09, I.bell(H(nm), 1.1), 0.9) for i, nm in enumerate(seq)])
    return y + _place(1.6, [(0.27, I.sahn(accent=True, seed=seed), 2.0), (0.0, I.strum([H('Bb4'), H('D5'), H('F5')], dur=1.2, seed=seed), 0.5)])


def checkpoint(seed=0):
    return _place(1.1, [(0.0, I.strum([H('D4'), H('A4'), H('D5'), H('F5')], dur=0.9, up=True, seed=seed), 0.8), (0.12, I.bell(H('A5'), 0.6), 0.8)])


def ui_move(seed=0):
    return I.lyre(H('A4'), 0.12, vel=0.7, seed=seed) * 0.8


def ui_select(seed=0):
    return _place(0.4, [(0.0, I.lyre(H('D5'), 0.3, seed=seed), 0.8), (0.045, I.lyre(H('A5'), 0.3, seed=seed + 1), 0.9)])


def ui_back(seed=0):
    return _place(0.3, [(0.0, I.lyre(H('A4'), 0.12, vel=0.7, seed=seed), 0.8), (0.05, I.lyre(H('F4'), 0.16, vel=0.6, seed=seed + 1), 0.8)])


def go_prompt(seed=0):
    return _place(0.9, [(0.0, I.strum([H('D5'), H('A5')], dur=0.25, seed=seed), 0.8), (0.14, I.strum([H('D5'), H('A5'), H('D6')], dur=0.6, up=True, seed=seed + 1), 0.9),
                        (0.16, I.bell(H('D6'), 0.5), 0.7)])


def plate_lost(seed=0):
    n = n_of(0.14)
    t = np.arange(n) / SR
    blip = np.sin(TAU * np.cumsum(620 * (290 / 620) ** (t / t[-1])) / SR) * np.hanning(n) * 0.4
    return _place(0.36, [(0.0, _metal([640, 1130, 1790, 2700], 0.09, seed), 1.1), (0.06, blip, 1.0)])


def life_lost(seed=0):
    y = _notes(['A4', 'F4', 'D4'], 0.13, I.lyre, tail=0.9, dur=0.9, seed=seed)
    return y + _place(len(y) / SR, [(0.26, I.marfa(seed=seed), 0.8), (0.26, I.bass(H('D2'), 0.6, seed=seed), 0.6)])


def low_armour(seed=0):
    m = n_of(0.075)
    b = fade(soft(np.sin(TAU * 880 * np.arange(m) / SR) * 2.0, 1.0) * 0.3, 0.004, 0.008)
    return _place(0.3, [(0.0, b, 1.0), (0.14, b, 1.0)])


def tick(seed=0):
    m = n_of(0.045)
    t = np.arange(m) / SR
    return fade((np.sin(TAU * 930 * t) * 0.6 + filt(white(m, seed), bp(1900, 2.0)) * 0.5) * decay(m, 0.025))


# ---------------------------------------------------------------- rescue and capture (played straight)
def rope_cut(seed=0):
    m = n_of(0.02)
    snip = filt(white(m, seed) * decay(m, 0.007), hp(3000))
    tw = pluck(120.0, 0.25, t60=0.25, damp=0.3, bright=0.6, seed=seed)
    idx = np.arange(len(tw)) * (1 + 0.6 * np.linspace(0, 1, len(tw)))
    tw = np.interp(idx, np.arange(len(tw)), tw, right=0.0)
    return _place(0.4, [(0.0, snip, 0.8), (0.05, snip, 0.7), (0.07, filt(tw, hp(80)), 0.7)])


def freed(seed=0):
    y = _notes(['D4', 'F4', 'A4', 'D5'], 0.075, I.lyre, tail=1.0, dur=1.0, seed=seed)
    fl = I.flute([(0.0, 0.14, H('A5'), None), (0.14, 0.55, H('D6'), H('F6'))], 0.8, seed=seed)
    return y + _place(len(y) / SR, [(0.3, fl, 0.9), (0.44, I.bell(H('D6'), 0.7), 0.5)])


def surrender(seed=0):
    r = rng(seed)
    parts = [(0.0 + i * 0.07 + r.uniform(0, 0.02), _metal([r.uniform(900, 1500), r.uniform(1900, 2900), r.uniform(3300, 4800)], 0.05, seed + i), 0.7 - 0.12 * i)
             for i in range(3)]
    parts += [(0.3, I.lyre(H('F4'), 0.5, vel=0.7, seed=seed), 0.8), (0.42, I.lyre(H('A4'), 0.7, vel=0.8, seed=seed + 1), 0.9)]
    return _place(1.2, parts)


# ---------------------------------------------------------------- the Scorpion's side
def enemy_rifle(seed=0):
    return _gun(seed, 900, 3000, 0.04, 215.0, 0.035, 0.16, 0.08, drive=1.3, weight=0.3)


def guard_mg(seed=0):
    return heavy_mg(seed + 50, shots=8, gap=0.14) * 0.95


def fuse(seed=0):
    n = n_of(0.7)
    r = rng(seed)
    amp = filt(np.abs(r.normal(0, 1, n)), lp(60)) * 2.0
    y = filt(white(n, seed + 1), hp(3200), lp(9000)) * amp
    return fade(y * 0.35, 0.02, 0.03)


def ladle_pot(seed=0):
    y = _metal([538, 1312, 2084, 3160, 4420], 0.4, seed)
    t = np.arange(len(y)) / SR
    return fade(y * (1 + 0.15 * np.sin(TAU * 7 * t)) * 1.2, 0.0002, 0.04)


def klaxon(seed=0):
    out = []
    for nm in ('A4', 'Bb4', 'A4', 'Bb4'):
        n = n_of(0.34)
        ff = np.full(n, H(nm) / 2)
        y = additive(ff, lambda k, f: (1.0 / k ** 0.6) * np.exp(-f / 2600.0), maxf=6000.0)
        out.append(fade(soft(y * 1.4, 1.5) * 0.3, 0.012, 0.02))
    return filt(np.concatenate(out), hp(180), peak(900, 1.5, 4.0))


def missile_launch(seed=0):
    n = n_of(2.3)
    t = np.arange(n) / SR
    env = np.minimum(1, t / 0.12) * decay(n, 2.6)
    roar = sweep_filter(white(n, seed), 400, 3400, 'lp', q=0.9, steps=24, curve=0.5) * env
    away = sweep_filter(roar, 4000, 500, 'lp', steps=18, curve=1.6)
    rumble = filt(white(n, seed + 1), lp(120)) * (1 + 0.6 * np.sin(TAU * 23 * t)) * env * 3.0
    pop = filt(white(n_of(0.08), seed + 2) * decay(n_of(0.08), 0.03), lp(3000)) * 1.3
    y = away * 1.1 + rumble
    y[:len(pop)] += pop
    return fade(soft(y * 1.3, 1.4), 0.0005, 0.25)


# ---------------------------------------------------------------- the place
def sea(seed=0, dur=8.0):
    """Two waves coming in, eight seconds, cut so that it loops."""
    n = n_of(dur)
    t = np.arange(n) / SR
    r = rng(seed)
    swell = (0.5 - 0.5 * np.cos(TAU * t / (dur / 2))) ** 1.6
    wash = filt(r.uniform(-1, 1, n), lp(700), hp(90)) * (0.25 + 0.75 * swell)
    foam = filt(r.uniform(-1, 1, n), hp(2400), lp(8000)) * (0.5 - 0.5 * np.cos(TAU * (t - 0.55) / (dur / 2))) ** 3 * 0.35
    far = filt(r.uniform(-1, 1, n), lp(260)) * 0.5
    y = wash + foam + far
    # crossfade the ends so the loop has no seam
    k = n_of(0.4)
    y[:k] = y[:k] * np.linspace(0, 1, k) + y[-k:] * np.linspace(1, 0, k)
    return y[:-k] * 0.5


def gull(seed=0):
    parts = []
    r = rng(seed)
    for i in range(3):
        n = n_of(0.2)
        t = np.arange(n) / SR
        f = (2500 - 250 * i) * (1 - 0.3 * (t / t[-1]) ** 2) * (1 + 0.02 * np.sin(TAU * 38 * t))
        ph = np.cumsum(f) / SR
        y = (np.sin(TAU * ph) + 0.4 * np.sin(TAU * 2 * ph) + 0.2 * np.sin(TAU * 3 * ph)) * np.hanning(n) ** 0.6
        parts.append((i * 0.27 + r.uniform(0, 0.03), y * 0.3, 1.0 - 0.15 * i))
    return filt(_place(0.95, parts), hp(900), lp(7000))


def skiff(seed=0):
    """The outboard, throttling down as the boat grounds."""
    n = n_of(2.0)
    t = np.arange(n) / SR
    rate = 24 * (11 / 24) ** ((t / t[-1]) ** 1.3)
    ph = np.cumsum(rate) / SR
    pulses = (np.mod(ph, 1.0) < 0.12).astype(float)
    y = filt(pulses + 0.15 * white(n, seed), bp(190, 2.5)) * 2.0 + filt(pulses, bp(430, 3.0)) * 1.0
    y *= np.minimum(1, t / 0.05) * (1 - (t / t[-1]) ** 3)
    scrape = filt(white(n_of(0.5), seed + 1), bp(900, 0.6)) * np.hanning(n_of(0.5)) * 0.35
    return fade(soft(y, 1.2) * 0.7, 0.01, 0.05) + _place(2.0, [(1.5, scrape, 1.0)])


# ---------------------------------------------------------------- the coast road
def _periodic(x_fn, P, reps=3):
    """Make a sound that repeats every P seconds: drive it with an input that repeats, and keep the middle repeat."""
    n = n_of(P)
    y = x_fn(n * reps, n)
    return y[n:2 * n]


def _tiled(n_total, n, seed):
    w = white(n, seed)
    return np.tile(w, n_total // n + 1)[:n_total]


def engine_loop(seed=0, P=1.0):
    """A diesel pickup at cruise, one second that repeats without a seam. The game changes its speed with the car's."""
    def make(N, n):
        t = np.arange(N) / SR
        fire = 36.0                                   # firing pulses a second: a whole number per loop
        ph = np.mod(t * fire, 1.0)
        pulses = np.exp(-ph / 0.06) * (1 + 0.25 * np.sin(TAU * 2 * t))       # uneven, as an old engine is
        rough = _tiled(N, n, seed)
        y = filt(pulses + 0.12 * rough, bp(110, 1.8)) * 2.2 + filt(pulses, bp(310, 3.0)) * 0.9 + filt(pulses * rough, bp(1400, 1.0)) * 0.5
        y += filt(rough, lp(220)) * 0.35
        return soft(y * 1.3, 1.3)
    return _periodic(make, P) * 0.7


def rotor_loop(seed=0, P=1.0):
    """Four rotors on a fishing boat: a chop, a motor buzz and the air they move. Repeats every second."""
    def make(N, n):
        t = np.arange(N) / SR
        chop = 0.5 + 0.5 * np.cos(TAU * 23 * t)
        chop2 = 0.5 + 0.5 * np.cos(TAU * 19 * t + 1.0)
        air = filt(_tiled(N, n, seed), bp(700, 0.7)) * (0.25 + 0.75 * chop ** 3) + filt(_tiled(N, n, seed + 1), bp(1300, 0.9)) * 0.5 * chop2 ** 3
        buzz = filt(np.sign(np.sin(TAU * 140 * t)) * 0.3 + np.sin(TAU * 280 * t) * 0.2, lp(1800))
        whump = filt(chop ** 6, lp(90)) * 2.0
        return air * 1.2 + buzz * 0.5 + whump
    return _periodic(make, P) * 0.8


def heli_loop(seed=0, P=1.0):
    """Taiz: the Apache. A heavy blade slap twelve times a second, the air it beats, the turbines' whine over it and the
    tail rotor's buzz under it. Repeats every second; the game quickens it a little when it is flown hard."""
    def make(N, n):
        t = np.arange(N) / SR
        ph = np.mod(t * 12.0, 1.0)                    # blade passes a second: a whole number in a loop
        slap = np.exp(-ph / 0.035)
        thump = filt(slap, lp(120)) * 3.0
        air = filt(_tiled(N, n, seed), bp(500, 0.8)) * (0.15 + 0.85 * slap) * 1.4
        crack = filt(_tiled(N, n, seed + 2), bp(2200, 1.2)) * slap ** 2 * 0.5
        whine = np.sin(TAU * 1640 * t) * 0.12 + np.sin(TAU * 3280 * t) * 0.05
        whine = filt(whine * (1 + 0.1 * np.sin(TAU * 2 * t)) + filt(_tiled(N, n, seed + 3), bp(1640, 6.0)) * 0.3, bp(1640, 2.0))
        tail = filt(np.sign(np.sin(TAU * 72 * t)) * 0.2, lp(600)) * (0.6 + 0.4 * np.cos(TAU * 6 * t))
        return thump + air + crack + whine * 0.8 + tail * 0.35
    return _periodic(make, P) * 0.8


def chin_gun(seed=0):
    """Taiz: the Apache's chin gun, a heavy cannon fired fast: a hard snap, a deep short thud, the barrel's ring, and a short
    roll after it (short: it fires fifteen times a second and must not turn to mud)."""
    r = rng(seed)
    n = n_of(0.24)
    t = np.arange(n) / SR
    snap = filt(white(n, seed + 7), hp(1800), lp(7000)) * decay(n, 0.012) * 1.3
    thud = np.sin(TAU * np.cumsum(62 * (1 + 2.4 * np.exp(-t / 0.008))) / SR) * decay(n, 0.05) * 1.1
    crack = filt(white(n, seed + 1), hp(400), lp(3800)) * decay(n, 0.03)
    ring = _metal([1240 * (1 + 0.02 * r.normal()), 1870, 2930], 0.05, seed + 3, dur=0.24) * 0.25
    roll = filt(white(n, seed + 2), lp(900), hp(90)) * decay(n, 0.11) * 0.3
    y = snap + thud + crack + ring + roll
    return fade(soft(y * 1.8, 1.5), 0.0002, 0.03)


def gun30(seed=0):
    """Taiz: the Apache's 30 mm chain gun, as Khaled asked for it ("closer to apache"): a deep thump that drops away, the
    muzzle's crack, the chain feed's clunk just after it, and a short low roll. Short enough for twenty a second."""
    r = rng(seed)
    n = n_of(0.26)
    t = np.arange(n) / SR
    thump = np.sin(TAU * np.cumsum(48 + 92 * np.exp(-t / 0.012)) / SR) * decay(n, 0.085) * 1.25
    body = filt(white(n, seed + 1), hp(180), lp(900)) * decay(n, 0.05) * 0.95
    crack = filt(white(n, seed + 2), hp(1500), lp(6500)) * decay(n, 0.011) * 0.75
    clunk = _place(0.26, [(0.018, _metal([620 * (1 + 0.02 * r.normal()), 1180, 1730], 0.035, seed + 5, dur=0.12), 0.32)])
    roll = filt(white(n, seed + 3), lp(480), hp(40)) * decay(n, 0.13) * 0.38
    y = thump + body + crack + clunk + roll
    return fade(soft(y * 2.0, 1.6), 0.0002, 0.03)


def hedp(seed=0):
    """Taiz: a chin gun round bursting where it lands: a little crack and thump, and a crackle (small: twenty a second)."""
    n = n_of(0.28)
    t = np.arange(n) / SR
    crack = filt(white(n, seed), hp(800), lp(7000)) * decay(n, 0.009)
    thump = np.sin(TAU * np.cumsum(50 + 60 * np.exp(-t / 0.015)) / SR) * decay(n, 0.06) * 0.9
    crackle = filt(white(n, seed + 4), bp(2400, 1.0)) * decay(n, 0.08) * 0.28 * (rng(seed + 9).random(n) > 0.6)
    return fade(soft((crack + thump + crackle) * 1.6, 1.3), 0.0002, 0.03)


def rlock_beep(seed=0):
    """Taiz: the rocket pod finding its target: one short clean blip (three of them, closer and higher, as it closes in)."""
    n = n_of(0.05)
    t = np.arange(n) / SR
    return (np.sin(TAU * 2400 * t) * 0.8 + np.sin(TAU * 4800 * t) * 0.15) * np.hanning(n) ** 0.4 * 0.7


def rlock_tone(seed=0):
    """Taiz: the rocket pod has it: two quick notes, up."""
    def note(f, d):
        k = n_of(d); tt = np.arange(k) / SR
        return (np.sin(TAU * f * tt) * 0.8 + np.sin(TAU * 2 * f * tt) * 0.12) * np.hanning(k) ** 0.3
    return _place(0.2, [(0.0, note(2600, 0.06), 0.7), (0.075, note(3400, 0.11), 0.8)])


def lock_beep(seed=0):
    """Taiz: one beat of a missile man's lock-on: a short hard beep (the game plays them closer and higher as he gets it)."""
    n = n_of(0.055)
    t = np.arange(n) / SR
    sq = np.sign(np.sin(TAU * 1850 * t)) * 0.35 + np.sin(TAU * 1850 * t) * 0.4 + np.sin(TAU * 3700 * t) * 0.12
    return filt(sq, lp(6000)) * np.hanning(n) ** 0.25 * 0.8


def lock_tone(seed=0):
    """Taiz: he has it: one long tone, a little higher than the beats and wavering, until the missile goes."""
    n = n_of(0.36)
    t = np.arange(n) / SR
    f = 2050 * (1 + 0.012 * np.sin(TAU * 22 * t))
    ph = np.cumsum(f) / SR
    y = np.sign(np.sin(TAU * ph)) * 0.3 + np.sin(TAU * ph) * 0.45 + np.sin(TAU * 2 * ph) * 0.1
    return fade(filt(y, lp(6500)) * 0.8, 0.003, 0.02)


def hop(seed=0):
    """The engine revs, the springs let go."""
    n = n_of(0.5)
    t = np.arange(n) / SR
    rate = 36 + 60 * np.minimum(1, t / 0.12) * np.exp(-np.maximum(0, t - 0.12) / 0.2)
    ph = np.mod(np.cumsum(rate) / SR, 1.0)
    rev = filt(np.exp(-ph / 0.05), bp(140, 1.6)) * 1.6 * decay(n, 0.45)
    f = 150 * (1 - 0.35 * (t / t[-1])) * (1 + 0.06 * np.sin(TAU * 17 * t))
    boing = np.sin(TAU * np.cumsum(f) / SR) * decay(n, 0.35) * 0.7
    return fade(soft(rev + boing, 1.2), 0.002, 0.05)


def car_land(seed=0):
    """A pickup coming down on its springs: a thump, the body knocking, a rattle."""
    n = n_of(0.6)
    t = np.arange(n) / SR
    thump = filt(white(n, seed) * decay(n, 0.09), lp(500)) * 2.2
    sub = np.sin(TAU * np.cumsum(70 * (1 + 0.8 * np.exp(-t / 0.03))) / SR) * decay(n, 0.25) * 1.2
    rattle = _metal([980, 1530, 2260, 3100], 0.12, seed + 3, dur=0.5) * 0.6
    f = 120 * (1 + 0.08 * np.sin(TAU * 14 * t))
    spring = np.sin(TAU * np.cumsum(f) / SR) * decay(n, 0.22) * 0.35
    y = thump + sub + _place(0.6, [(0.03, rattle, 1.0)]) + spring
    return fade(soft(y * 1.2, 1.4), 0.0005, 0.06)


def crash(seed=0):
    """A pickup rammed over: sheet metal folding, glass going, the thump of it landing on its roof."""
    n = n_of(1.1)
    t = np.arange(n) / SR
    r = rng(seed)
    crunch = sweep_filter(white(n, seed), 3200, 500, 'bp', q=0.9, steps=16) * decay(n, 0.35) * 1.4
    body = _metal([168, 251, 397, 655, 1080], 0.5, seed + 1, dur=1.1) * 1.1
    glass = np.zeros(n)
    for i in range(14):
        a = int(r.uniform(0.02, 0.5) * SR)
        g = _metal([r.uniform(3800, 5200), r.uniform(5600, 7400)], 0.05, seed + 10 + i)
        b = min(n, a + len(g))
        glass[a:b] += g[:b - a] * r.uniform(0.2, 0.5)
    thump = filt(white(n_of(0.2), seed + 2) * decay(n_of(0.2), 0.06), lp(400)) * 2.0
    y = crunch + body + glass * 0.8 + _place(1.1, [(0.42, thump, 1.0)])
    return fade(soft(y * 1.3, 1.5), 0.0003, 0.08)


def ram(seed=0):
    """Somebody meets the bull bar: a thwack, and the bar ringing."""
    n = n_of(0.35)
    t = np.arange(n) / SR
    thwack = filt(white(n, seed) * decay(n, 0.03), bp(900, 0.8)) * 1.4
    thud = np.sin(TAU * np.cumsum(110 * (1 + 1.2 * np.exp(-t / 0.01))) / SR) * decay(n, 0.08)
    ring = _metal([520, 845, 1310], 0.18, seed + 1, dur=0.35) * 0.45
    return fade(soft(thwack + thud + ring, 1.3), 0.0003, 0.03)


def _horn(notes, durs, buzz=1.0, seed=0, detune=0.0):
    parts, at = [], 0.0
    for nm, d in zip(notes, durs):
        n = n_of(d)
        t = np.arange(n) / SR
        fs = [H(x) for x in (nm if isinstance(nm, (list, tuple)) else [nm])]
        y = np.zeros(n)
        for j, f in enumerate(fs):
            ff = np.full(n, f * (1 + detune * (j - 0.5)))
            y += additive(ff, lambda k, fq: (1.0 / k ** (0.55 / buzz)) * np.exp(-fq / 3800.0) * np.where(np.asarray(k) % 2 == 1, 1.0, 0.6), maxf=7000.0)
        y = soft(y / len(fs) * 1.6, 1.5) * 0.35
        parts.append((at, fade(y, 0.01, 0.02), 1.0))
        at += d + 0.02
    out = _place(at + 0.05, parts)
    return filt(out, hp(220), peak(1800, 1.2, 5.0), lp(6000))


def horn_shass(seed=0):
    """Salem's horn: two notes, cheerful, more than once."""
    return _horn(['C#5', 'A4', 'C#5', 'A4', 'E5'], [0.1, 0.1, 0.1, 0.1, 0.3], 1.1, seed)


def horn_truck(seed=0):
    """Their pickup coming the wrong way: one long sour blare."""
    return _horn([['Eb3', 'G3']], [0.75], 1.3, seed, detune=0.01)


def boat_horn(seed=0):
    """The flying boat's truck horns, all three, not quite together."""
    return _horn([['D4', 'F4', 'B4'], ['D4', 'F4', 'B4']], [0.35, 0.65], 1.3, seed, detune=0.012)


def brake(seed=0):
    """Salem stopping at the barrier: tyres on hot tarmac."""
    n = n_of(0.85)
    t = np.arange(n) / SR
    sq = filt(white(n, seed), bp(1150, 9.0)) * 3.0 + filt(white(n, seed + 1), bp(2300, 7.0)) * 1.2
    sq *= (np.minimum(1, t / 0.04) * (1 - (t / t[-1]) ** 2)) * (1 + 0.3 * np.sin(TAU * 9 * t))
    return fade(soft(sq, 1.3) * 0.8, 0.003, 0.06)


def door_slam(seed=0):
    """Yazeed climbing in over the tailgate: a thunk and the latch."""
    n = n_of(0.3)
    t = np.arange(n) / SR
    thunk = filt(white(n, seed) * decay(n, 0.04), lp(700)) * 1.6 + np.sin(TAU * 140 * t) * decay(n, 0.07)
    latch = _metal([2400, 3700], 0.03, seed + 1, dur=0.08) * 0.5
    return fade(thunk + _place(0.3, [(0.05, latch, 1.0)]), 0.0003, 0.03)


def heavy_shot(seed=0):
    """One round from their heavy guns: deeper and slower than Yazeed's."""
    return _gun(seed + 70, 400, 2600, 0.07, 92.0, 0.1, 0.36, 0.17, drive=1.7, weight=0.62)


def spinup(seed=0):
    """A heavy gun being readied: a crank and a rising whine. It is the warning."""
    n = n_of(0.5)
    t = np.arange(n) / SR
    f = 260 * (1400 / 260) ** (t / t[-1])
    whine = np.sin(TAU * np.cumsum(f) / SR) * (0.3 + 0.7 * t / t[-1]) * 0.35
    clicks = np.zeros(n)
    tt_, k = 0.0, 0
    while tt_ < 0.45:
        i = int(tt_ * SR)
        clicks[i:i + 30] += np.hanning(30)
        tt_ += max(0.016, 0.06 * (0.8 ** k)); k += 1
    clicks = filt(clicks, bp(2600, 1.5)) * 1.2
    return fade(whine + clicks, 0.003, 0.03)


def lock(seed=0):
    """A drone has picked its spot: two short beeps."""
    n = n_of(0.06)
    t = np.arange(n) / SR
    b = np.sin(TAU * 2250 * t) * np.hanning(n) ** 0.3 * 0.5
    return _place(0.22, [(0.0, b, 1.0), (0.12, b, 1.0)])


def dive(seed=0):
    """A little drone coming down: a whine that falls and grows."""
    n = n_of(0.7)
    t = np.arange(n) / SR
    f = 1900 * (650 / 1900) ** (t / t[-1])
    y = (np.sin(TAU * np.cumsum(f) / SR) + 0.3 * np.sin(TAU * np.cumsum(2 * f) / SR)) * (0.25 + 0.75 * (t / t[-1]) ** 1.2)
    y += filt(white(n, seed), bp(1500, 1.2)) * 0.25 * (t / t[-1])
    return fade(y * 0.5, 0.01, 0.02)


def whistle(seed=0):
    """A bomb falling from the boat."""
    n = n_of(0.75)
    t = np.arange(n) / SR
    f = 2300 * (750 / 2300) ** ((t / t[-1]) ** 1.4)
    y = np.sin(TAU * np.cumsum(f) / SR) * (0.2 + 0.8 * (t / t[-1]) ** 1.5) + filt(white(n, seed), bp(1600, 1.6)) * 0.1
    return fade(y * 0.55, 0.02, 0.01)


def bay(seed=0):
    """The bomb bay opening: a hydraulic whine and a clunk."""
    n = n_of(0.45)
    t = np.arange(n) / SR
    hyd = filt(white(n, seed), bp(900, 2.0)) * (t / t[-1]) * 0.8 + np.sin(TAU * np.cumsum(180 + 120 * t / t[-1]) / SR) * 0.25
    clunk = _metal([300, 470, 860], 0.12, seed + 1, dur=0.2)
    knock = filt(white(n_of(0.1), seed + 2) * decay(n_of(0.1), 0.03), lp(600)) * 1.2
    return fade(_place(0.65, [(0.0, hyd, 1.0), (0.4, clunk, 1.0), (0.4, knock, 1.0)]), 0.003, 0.03)


def launch(seed=0):
    """A little drone let go: a pop and a whoosh."""
    n = n_of(0.4)
    pop = filt(white(n_of(0.05), seed) * decay(n_of(0.05), 0.015), lp(2200)) * 1.3
    wh = sweep_filter(white(n, seed + 1), 600, 2600, 'bp', q=1.3, steps=10) * np.hanning(n) * 0.6
    return fade(_place(0.45, [(0.0, pop, 1.0), (0.03, wh, 1.0)]), 0.0003, 0.03)


def knife(seed=0):
    """The jambiya: a swish and a small bright ring."""
    n = n_of(0.16)
    sw = sweep_filter(white(n, seed), 1200, 5200, 'bp', q=1.4, steps=10) * np.hanning(n) ** 0.8 * 0.9
    shing = _metal([3550, 5230, 7080], 0.12, seed + 1, dur=0.22) * 0.35
    return fade(_place(0.3, [(0.0, sw, 1.0), (0.06, shing, 1.0)]), 0.0005, 0.03)


def smash_crate(seed=0):
    """A grenade crate under the bull bar: planks cracking."""
    r = rng(seed)
    parts = []
    for i in range(6):
        n = n_of(0.08)
        k = filt(white(n, seed + i) * decay(n, 0.02), bp(r.uniform(500, 1300), 1.2)) * r.uniform(0.6, 1.2)
        parts.append((i * 0.035 + r.uniform(0, 0.02), k, 1.0))
    crack = filt(white(n_of(0.12), seed + 9) * decay(n_of(0.12), 0.03), hp(1800)) * 0.6
    parts.append((0.0, crack, 1.0))
    return fade(soft(_place(0.45, parts) * 1.3, 1.3), 0.0003, 0.03)


def smash_bags(seed=0):
    """Sandbags through the windscreen's view: a heavy, soft whump."""
    n = n_of(0.4)
    t = np.arange(n) / SR
    y = filt(white(n, seed) * decay(n, 0.12), lp(350)) * 2.0 + np.sin(TAU * np.cumsum(60 * (1 + np.exp(-t / 0.02))) / SR) * decay(n, 0.15)
    y += filt(white(n, seed + 1), hp(2500)) * decay(n, 0.2) * 0.15
    return fade(soft(y, 1.2), 0.0005, 0.04)


def part_off(seed=0):
    """A rotor torn off the boat: a bang, metal tearing, the blades clattering away."""
    n = n_of(1.3)
    t = np.arange(n) / SR
    tear = sweep_filter(white(n, seed), 2600, 700, 'bp', q=2.5, steps=14) * decay(n, 0.5) * 1.2
    clatter = np.zeros(n)
    tt_ = 0.15
    while tt_ < 1.1:
        i = int(tt_ * SR)
        g = _metal([1300, 2100], 0.03, seed + int(tt_ * 100), dur=0.06)
        b = min(n, i + len(g))
        clatter[i:b] += g[:b - i] * (1 - tt_)
        tt_ += 0.05 + 0.1 * tt_
    return fade(soft(_place(1.3, [(0.0, explosion(0.9, seed + 3), 1.0)]) + tear + clatter * 0.8, 1.4), 0.0003, 0.08)


def boss_fall(seed=0):
    """The pride of the coast losing interest in the sky: the rotors running down, the engine coughing."""
    n = n_of(1.7)
    t = np.arange(n) / SR
    rate = 23 * (5 / 23) ** (t / t[-1])
    ph = np.cumsum(rate) / SR
    chop = (0.5 + 0.5 * np.cos(TAU * ph)) ** 3
    air = filt(white(n, seed), bp(700, 0.7)) * (0.2 + 0.8 * chop)
    f = 140 * (55 / 140) ** (t / t[-1])
    buzz = filt(np.sign(np.sin(TAU * np.cumsum(f) / SR)) * 0.3, lp(1500))
    cough = np.zeros(n)
    for c in (0.35, 0.62, 0.8, 1.15):
        i = int(c * SR)
        k = filt(white(n_of(0.09), seed + int(c * 10)) * decay(n_of(0.09), 0.03), bp(260, 1.0)) * 1.4
        cough[i:i + len(k)] += k[:max(0, min(len(k), n - i))]
    y = (air * 1.1 + buzz * 0.5) * (1 - 0.4 * t / t[-1]) + cough
    return fade(soft(y * 1.2, 1.3), 0.01, 0.15)


def strike_bells(seed=0):
    """A whole file of men in one go: the band plays a flourish."""
    return _notes(['D5', 'F5', 'A5', 'D6'], 0.06, I.bell, tail=0.7, dur=0.5)



# ---------------------------------------------------------------- build 5: the campaign map
def stamp(seed=0):
    """CLEAR stamped on the map: the stamp's wooden block on the desk, the rubber smacking the paper, a rattle of the inkpad."""
    n = n_of(0.45)
    t = np.arange(n) / SR
    thump = np.sin(TAU * 92 * t * (1 - 0.25 * t)) * decay(n, 0.09) * 1.1 + filt(white(n, seed) * decay(n, 0.05), lp(420)) * 1.4
    smack = filt(white(n, seed + 1) * decay(n, 0.018), bp(1700, 0.8)) * 0.9
    block = _metal([620, 1130, 1810], 0.05, seed + 2, dur=0.12) * 0.22
    rattle = filt(white(n_of(0.08), seed + 3) * decay(n_of(0.08), 0.03), bp(3200, 1.2)) * 0.18
    return fade(_place(0.45, [(0.0, thump + smack, 1.0), (0.004, block, 1.0), (0.11, rattle, 1.0)]), 0.0002, 0.05)


def paper(seed=0):
    """The map coming out: a sheet of paper unfolded and smoothed flat."""
    n = n_of(0.55)
    r = rng(seed)
    out = np.zeros(n)
    tt_ = 0.0
    while tt_ < 0.46:
        m = n_of(r.uniform(0.012, 0.04))
        g = r.uniform(0.25, 1.0) * (1.0 - 0.6 * tt_ / 0.46)
        cr = filt(white(m, int(r.integers(1 << 20))) * decay(m, m / SR * 0.5), bp(r.uniform(1400, 4200), 0.9)) * g
        a = n_of(tt_)
        k = max(0, min(m, n - a))
        out[a:a + k] += cr[:k]
        tt_ += r.uniform(0.012, 0.05)
    hiss = filt(white(n, seed + 7), bp(2600, 0.5)) * adsr(n, 0.04, 0.2, 0.25, 0.2) * 0.12
    return fade(out + hiss, 0.003, 0.06)


def route(seed=0):
    """A pencil marking the way from one mission to the next: a run of short dots on paper."""
    n = n_of(1.0)
    r = rng(seed)
    parts = []
    for k in range(13):
        m = n_of(0.03)
        dot = filt(white(m, seed + k) * decay(m, 0.012), bp(r.uniform(3200, 4600), 1.4))
        parts.append((0.03 + k * 0.072 + r.uniform(-0.006, 0.006), dot, r.uniform(0.6, 1.0)))
    scratch = filt(white(n, seed + 99), bp(5200, 0.7)) * adsr(n, 0.05, 0.3, 0.3, 0.3) * 0.08
    return fade(_place(1.0, parts) + scratch, 0.002, 0.05)

# name: (label, group, function, peak level in dB)
# ---------------------------------------------------------------- The Coffee Port (build 12)
def door_creak(seed=0):
    """A heavy warehouse door swung open from inside: the hinge groaning in short catches, and the knock as it stops."""
    n = n_of(0.55)
    t = np.arange(n) / SR
    rate = 38 + 26 * (t / t[-1])                                       # the catches come faster as it swings
    ph = np.cumsum(rate) / SR
    pulses = (np.mod(ph, 1.0) < 0.12).astype(float) * (0.6 + 0.4 * np.sin(TAU * 3 * t))
    groan = filt(pulses * filt(white(n, seed), bp(900, 2.0)), peak(720, 4.0, 9.0), peak(1450, 5.0, 6.0), lp(3200)) * 2.2
    groan *= np.minimum(1, t / 0.05) * np.clip(1 - (t - 0.42) / 0.08, 0, 1)
    knock = filt(white(n_of(0.12), seed + 1) * decay(n_of(0.12), 0.03), lp(500)) * 1.4
    return fade(_place(0.62, [(0.0, groan, 1.0), (0.46, knock, 1.0)]), 0.003, 0.04)


def hiss(seed=0):
    """Steam building up under a grating: a hiss that swells and flutters."""
    n = n_of(0.75)
    t = np.arange(n) / SR
    y = filt(white(n, seed), hp(2600), lp(9500)) * (0.15 + 0.85 * (t / t[-1]) ** 1.6)
    y *= 1 + 0.3 * np.sin(TAU * (14 + 10 * t / t[-1]) * t)
    return fade(y * 0.7, 0.02, 0.05)


def steam(seed=0):
    """A blast of steam: a roar of air with a low rumble in it, falling away."""
    n = n_of(1.0)
    t = np.arange(n) / SR
    env = np.minimum(1, t / 0.02) * np.exp(-t / 0.45)
    roar = filt(white(n, seed), hp(500), lp(7000), peak(2200, 0.8, 4.0)) * env
    rum = filt(white(n, seed + 1), lp(180)) * env * 2.5
    return fade(soft((roar + rum) * 1.4, 1.3) * 0.8, 0.002, 0.08)


def bean_spray(seed=0):
    """The Roaster's spout: a puff, and a fistful of hot beans rattling out of it."""
    r = rng(seed)
    parts = [(0.0, filt(white(n_of(0.08), seed) * decay(n_of(0.08), 0.03), lp(1200)) * 1.4, 1.0)]
    for i in range(14):
        m = n_of(0.03)
        k = filt(white(m, seed + 10 + i) * decay(m, 0.006), bp(r.uniform(2500, 5200), 2.5)) * r.uniform(0.5, 1.0)
        parts.append((0.01 + i * 0.012 + r.uniform(0, 0.01), k, 1.0))
    return fade(_place(0.32, parts) * 1.3, 0.0005, 0.03)


def pop(seed=0):
    """A roast bomb out of the hopper: a hollow pop, like a very big cork."""
    n = n_of(0.3)
    t = np.arange(n) / SR
    f = 420 * np.exp(-t / 0.04) + 160
    body = np.sin(TAU * np.cumsum(f) / SR) * decay(n, 0.09)
    click = filt(white(n, seed) * decay(n, 0.006), hp(1200)) * 0.7
    return fade((body + click) * 0.9, 0.0003, 0.04)


def pour(seed=0):
    """The drum tipping its burning beans out: a long rattle and the sizzle of them going."""
    r = rng(seed)
    parts = []
    for i in range(40):
        m = n_of(0.03)
        k = filt(white(m, seed + 20 + i) * decay(m, 0.008), bp(r.uniform(1500, 4200), 2.0)) * r.uniform(0.3, 0.9)
        parts.append((i * 0.022 + r.uniform(0, 0.015), k, 1.0))
    y = _place(1.1, parts)
    n = len(y)
    t = np.arange(n) / SR
    y += filt(white(n, seed + 3), hp(3500)) * 0.25 * np.minimum(1, t / 0.2) * np.clip(1 - (t - 0.8) / 0.3, 0, 1)
    return fade(y, 0.003, 0.06)


def rev(seed=0):
    """The Roaster's engine wound up for its lunge: a coughing old diesel climbing."""
    n = n_of(0.85)
    t = np.arange(n) / SR
    f = 34 * (2.6 ** (t / t[-1]))
    ph = np.cumsum(f) / SR
    saw = 2 * (ph - np.floor(ph + 0.5))
    y = filt(soft(saw * 2.2, 1.6), lp(900), peak(240, 1.0, 6.0)) * (0.5 + 0.5 * t / t[-1])
    y += filt(white(n, seed), bp(700, 1.0)) * 0.25 * (0.3 + 0.7 * (np.mod(ph, 1.0) < 0.2))
    return fade(y * 0.9, 0.01, 0.06)


# ---------------------------------------------------------------- the Souq
def sack_burst(seed=0):
    """A sack of ground spice split open: the cloth giving, a soft heavy whump, the powder going up in a hiss that
    hangs a moment, and grains pattering down."""
    n = n_of(0.9)
    t = np.arange(n) / SR
    r = rng(seed)
    rip = filt(white(n_of(0.07), seed) * decay(n_of(0.07), 0.016), bp(1500, 1.1)) * 0.9
    whump = filt(white(n, seed + 1) * decay(n, 0.07), lp(420)) * 1.5
    whump += np.sin(TAU * np.cumsum(88 * (1 + 0.8 * np.exp(-t / 0.015))) / SR) * decay(n, 0.08) * 0.8
    env = np.minimum(1, t / 0.035) * np.exp(-t / 0.33)
    puff = filt(white(n, seed + 2), bp(2300, 0.6), hp(800)) * env * 0.5
    parts = [(0.0, rip, 1.0), (0.008, whump, 1.0), (0.0, puff, 1.0)]
    for i in range(18):
        m = n_of(0.02)
        k = filt(white(m, seed + 30 + i) * decay(m, 0.004), bp(r.uniform(2800, 6000), 2.0)) * r.uniform(0.15, 0.45)
        parts.append((0.12 + r.uniform(0, 0.6), k, 1.0))
    return fade(soft(_place(0.95, parts) * 1.2, 1.2), 0.0003, 0.06)


def thunk(seed=0):
    """A round into the barricade: a short knock of wood with a dull thud under it."""
    n = n_of(0.16)
    t = np.arange(n) / SR
    knock = _metal([540, 1210, 1960], 0.028, seed, dur=0.16, spread=0.02) * 0.7
    thud = filt(white(n, seed + 1) * decay(n, 0.018), lp(700)) * 1.2
    body = np.sin(TAU * np.cumsum(170 * (1 + 0.5 * np.exp(-t / 0.008))) / SR) * decay(n, 0.04) * 0.7
    return fade(soft(knock + thud + body, 1.2), 0.0002, 0.02)


def creak_loop(seed=0, P=1.1):
    """Something old and heavy turning on a dry pin (made for the Spice Cannon's wheels, then the Great Scale's beam; now the
    Tailor's stands rolling about, played faster):
    a squeak twice a turn, wood groaning, a knock. Repeats every P seconds; the game changes its speed."""
    def make(N, n):
        t = np.arange(N) / SR
        ph = np.mod(t / P * 2, 1.0)
        sq_env = np.exp(-((ph - 0.32) / 0.07) ** 2)
        f = 1280 + 260 * np.sin(TAU * ph * 1.5)
        squeak = np.sin(TAU * np.cumsum(f) / SR) * sq_env * (0.7 + 0.3 * np.sin(TAU * 96 * t))
        squeak = filt(squeak, peak(1400, 2.0, 6.0))
        groan = filt(_tiled(N, n, seed), bp(380, 3.0)) * (0.35 + 0.65 * np.exp(-((ph - 0.62) / 0.18) ** 2)) * 0.9
        turn = np.mod(t / P, 1.0)
        knock = filt(_tiled(N, n, seed + 1) * np.exp(-turn / 0.012), lp(600)) * 1.4
        return squeak * 0.45 + groan + knock
    return _periodic(make, P) * 0.7


def pigeon(seed=0):
    """A pigeon on a roof: three soft coos, the middle one rolling up and down in its throat."""
    parts, at = [], 0.0
    for i, (f0, f1, ln) in enumerate(((380, 330, 0.22), (340, 425, 0.38), (360, 300, 0.26))):
        n = n_of(ln)
        t = np.arange(n) / SR
        u = t / t[-1]
        f = f0 + (f1 - f0) * (np.sin(np.pi * u) if i == 1 else u)
        ph = np.cumsum(f) / SR
        y = (np.sin(TAU * ph) + 0.5 * np.sin(TAU * 2 * ph) + 0.15 * np.sin(TAU * 3 * ph)) * (0.65 + 0.35 * np.sin(TAU * 27 * t))
        parts.append((at, y * np.hanning(n) ** 0.8 * 0.6, 1.0 - 0.1 * i))
        at += ln + (0.06 if i == 0 else 0.1)
    return filt(_place(at + 0.05, parts), hp(220), lp(3200))



# ---------------------------------------------------------------- the Tailor (build 30)
def snip(seed=0):
    """His shears: two quick snips, steel on steel, a dry click of the pivot in each."""
    parts = []
    for i, at in enumerate((0.0, 0.085)):
        m = n_of(0.06)
        hiss = filt(white(m, seed + i) * decay(m, 0.012), hp(3200), lp(9000)) * 0.9
        ring = _metal([3150 + 140 * i, 5080, 7400], 0.035, seed + 4 + i, dur=0.12, spread=0.01) * 0.55
        k = n_of(0.004)
        click = filt(white(k, seed + 9 + i), hp(1500)) * 0.8
        parts += [(at, hiss, 1.0), (at + 0.012, ring, 1.0), (at + 0.018, click, 1.0)]
    return fade(_place(0.24, parts), 0.0002, 0.03)


def pin_rattle(seed=0):
    """A pinch of pins out of the tin and thrown: a little rattle of fine steel, then a hiss as they go."""
    r = rng(seed)
    parts = []
    for i in range(14):
        m = n_of(0.03)
        f = r.uniform(4200, 7800)
        parts.append((r.uniform(0, 0.16), _metal([f, f * 1.47, f * 2.11], 0.012, seed + 20 + i, dur=0.03, spread=0.02), r.uniform(0.25, 0.6)))
    n = n_of(0.18)
    t = np.arange(n) / SR
    hiss = filt(white(n, seed + 1), bp(5200, 0.8)) * np.minimum(1, t / 0.03) * decay(n, 0.06) * 0.35
    parts.append((0.15, hiss, 1.0))
    return fade(_place(0.36, parts), 0.0002, 0.03)


def rip(seed=0):
    """Cloth tearing: a quick ragged rip, threads giving one after another, and the flap of it coming away."""
    n = n_of(0.34)
    t = np.arange(n) / SR
    r = rng(seed)
    env = np.minimum(1, t / 0.02) * np.exp(-t / 0.13)
    rough = np.abs(np.sin(TAU * np.cumsum(70 + 160 * t / t[-1] + 40 * r.normal(size=n) * 0.02) / SR)) ** 3
    tear = filt(white(n, seed), bp(2300, 0.7), hp(700)) * env * (0.45 + 0.55 * rough)
    parts = [(0.0, tear, 1.0)]
    for i in range(9):
        m = n_of(0.008)
        parts.append((r.uniform(0.0, 0.22), filt(white(m, seed + 30 + i) * decay(m, 0.002), bp(r.uniform(1800, 4200), 2.5)), r.uniform(0.3, 0.7)))
    m = n_of(0.12)
    flap = filt(white(m, seed + 2) * decay(m, 0.03), lp(900)) * 0.6
    parts.append((0.2, flap, 1.0))
    return fade(soft(_place(0.4, parts) * 1.3, 1.1), 0.0002, 0.04)


def tape_zip(seed=0):
    """A tape measure run out of its case: the ratchet buzzing faster and higher as it goes, the steel whirring."""
    n = n_of(0.42)
    t = np.arange(n) / SR
    rate = 55 + 70 * t / t[-1]
    ph = np.mod(np.cumsum(rate) / SR, 1.0)
    clicks = filt(white(n, seed) * np.exp(-ph / 0.06), bp(3400, 1.2)) * 0.9
    whir = np.sin(TAU * np.cumsum(900 + 700 * t / t[-1]) / SR) * 0.12 * np.minimum(1, t / 0.05)
    env = np.minimum(1, t / 0.01) * np.exp(-np.maximum(0, t - 0.3) / 0.04)
    return fade((clicks + whir) * env, 0.0002, 0.02)


def clatter(seed=0):
    """A dummy going over: its pole and the wooden stand knocking on the stone, a hollow bump and a short rattle."""
    n = n_of(0.5)
    t = np.arange(n) / SR
    r = rng(seed)
    parts = []
    for i, (at, f, g) in enumerate(((0.0, 210, 1.0), (0.11, 260, 0.6), (0.19, 300, 0.35))):
        m = n_of(0.16)
        tt = np.arange(m) / SR
        tone = np.sin(TAU * np.cumsum(f * (1 + 0.3 * np.exp(-tt / 0.01))) / SR) * decay(m, 0.05)
        knock = _metal([f * 2.6, f * 4.1, f * 6.3], 0.03, seed + i, dur=0.16, spread=0.03)
        thud = filt(white(m, seed + 10 + i) * decay(m, 0.012), lp(900))
        parts.append((at, (tone * 0.8 + knock * 0.5 + thud * 0.9) * g, 1.0))
    for i in range(6):
        m = n_of(0.03)
        parts.append((0.24 + r.uniform(0, 0.18), filt(white(m, seed + 30 + i) * decay(m, 0.006), bp(r.uniform(900, 2400), 2.0)), r.uniform(0.15, 0.35)))
    return fade(soft(_place(0.55, parts) * 1.1, 1.2), 0.0002, 0.05)


def whoosh(seed=0):
    """A sheet thrown out over something: a soft rush of cloth through the air, up and down again."""
    n = n_of(0.42)
    t = np.arange(n) / SR
    u = t / t[-1]
    x = white(n, seed)
    lo = sweep_filter(x, 500, 2200, kind='lp', q=0.9, steps=24, curve=1.0)
    env = np.sin(np.pi * np.clip(u * 1.1, 0, 1)) ** 1.5
    flut = 0.75 + 0.25 * np.sin(TAU * 23 * t)
    return fade(filt(lo, hp(180)) * env * flut, 0.002, 0.04)

EFFECTS = {
    'pistol': ('Sidearm', 'Your weapons', pistol, -4),
    'rifle_burst': ('Rifle, three rounds', 'Your weapons', rifle_burst, -3),
    'heavy_mg': ('Heavy MG', 'Your weapons', heavy_mg, -3),
    'shotgun': ('Shotgun', 'Your weapons', shotgun, -2),
    'marksman': ('Marksman rifle', 'Your weapons', marksman, -3),
    'rocket': ('Rocket', 'Your weapons', rocket, -4),
    'grenade_throw': ('Grenade, thrown', 'Your weapons', grenade_throw, -12),
    'grenade_bounce': ('Grenade, bouncing', 'Your weapons', grenade_bounce, -12),
    'explosion_small': ('Grenade blast', 'Blasts', explosion_small, -3),
    'explosion_drum': ('Fuel drum', 'Blasts', explosion_drum, -2),
    'explosion_big': ('The battery goes up', 'Blasts', explosion_big, -1.5),
    'mortar': ('Mortar: whistle and landing', 'Support', mortar, -2.5),
    'sniper_overwatch': ('Sniper overwatch', 'Support', sniper_overwatch, -4),
    'radio_full': ('Radio bar full', 'Support', radio_full, -10),
    'radio_call': ('Calling it in', 'Support', radio_call, -10),
    'ricochet': ('Ricochet', 'Hits', ricochet, -8),
    'door_clang': ('Round on the pickup door', 'Hits', door_clang, -7),
    'door_break': ('The door comes off', 'Hits', door_break, -5),
    'bash': ('The door, swung', "The Scorpion's side", bash, -8),
    'hit_sand': ('Round in the sand', 'Hits', hit_sand, -14),
    'hit_body': ('A hit that lands', 'Hits', hit_body, -9),
    'launcher_hit': ('Round on the launcher', 'Hits', launcher_hit, -5),
    'steps': ('Steps on sand', 'Moving', steps, -18),
    'jump': ('Jump', 'Moving', jump, -14),
    'land': ('Landing', 'Moving', land, -12),
    'pickup_weapon': ('Weapon crate', 'Pickups and score', pickup_weapon, -8),
    'pickup_ammo': ('Ammunition', 'Pickups and score', pickup_ammo, -10),
    'pickup_grenades': ('Grenades', 'Pickups and score', pickup_grenades, -10),
    'coin': ('Score', 'Pickups and score', coin, -10),
    'medal': ('Medal', 'Pickups and score', medal, -7),
    'checkpoint': ('Checkpoint', 'Pickups and score', checkpoint, -8),
    'rope_cut': ('Rope cut', 'Rescue and capture', rope_cut, -11),
    'freed': ('Detainee freed', 'Rescue and capture', freed, -7),
    'surrender': ('Weapon dropped, capture', 'Rescue and capture', surrender, -9),
    'enemy_rifle': ('Their rifle', "The Scorpion's side", enemy_rifle, -7),
    'guard_mg': ("The Guard's belt-fed gun", "The Scorpion's side", guard_mg, -4),
    'fuse': ('Dynamite fuse', "The Scorpion's side", fuse, -14),
    'ladle_pot': ('Ladle on the pot', "The Scorpion's side", ladle_pot, -7),
    'klaxon': ('Battery alarm', "The Scorpion's side", klaxon, -8),
    'missile_launch': ('Missile away', "The Scorpion's side", missile_launch, -3),
    'ui_move': ('Move', 'Interface', ui_move, -14),
    'ui_select': ('Select', 'Interface', ui_select, -12),
    'ui_back': ('Back', 'Interface', ui_back, -14),
    'go_prompt': ('GO!', 'Interface', go_prompt, -9),
    'plate_lost': ('Armour plate lost', 'Interface', plate_lost, -8),
    'low_armour': ('Last plate warning', 'Interface', low_armour, -12),
    'life_lost': ('Life lost', 'Interface', life_lost, -7),
    'tick': ('Continue countdown', 'Interface', tick, -12),
    'sea': ('The sea (loops)', 'The place', sea, -14),
    'gull': ('Gull', 'The place', gull, -14),
    'skiff': ('The skiff grounding', 'The place', skiff, -9),
    'engine_loop': ('Pickup engine (loops)', 'The coast road', engine_loop, -12),
    'rotor_loop': ('Flying boat rotors (loops)', 'The battery', rotor_loop, -11),
    'heli_loop': ('The Apache (loops)', 'Taiz', heli_loop, -11),
    'chin_gun': ("The Apache's chin gun", 'Taiz', chin_gun, -5),
    'lock_beep': ("A missile man's lock-on, one beat", 'Taiz', lock_beep, -10),
    'gun30': ("The Apache's chain gun", 'Taiz', gun30, -4),
    'hedp': ('Its round bursting', 'Taiz', hedp, -9),
    'rlock_beep': ('The rocket pod finding its target', 'Taiz', rlock_beep, -14),
    'rlock_tone': ('The rocket pod locked', 'Taiz', rlock_tone, -12),
    'lock_tone': ('He has it: the long tone', 'Taiz', lock_tone, -10),
    'hop': ('Pickup hop', 'The coast road', hop, -8),
    'car_land': ('Pickup landing', 'The coast road', car_land, -5),
    'crash': ('Their pickup flipped', 'The coast road', crash, -3),
    'ram': ('Run over', 'The coast road', ram, -7),
    'horn_shass': ("Salem's horn", 'The coast road', horn_shass, -8),
    'horn_truck': ('Their horn', 'The coast road', horn_truck, -8),
    'boat_horn': ("The boat's horns", 'The battery', boat_horn, -7),
    'brake': ('Brakes at the barrier', 'The coast road', brake, -10),
    'door_slam': ('Getting in', 'The coast road', door_slam, -9),
    'heavy_shot': ('Their heavy gun', 'The coast road', heavy_shot, -5),
    'spinup': ('Heavy gun readied', 'The coast road', spinup, -9),
    'lock': ('Drone has its spot', 'The coast road', lock, -12),
    'dive': ('Drone diving', 'The coast road', dive, -9),
    'whistle': ('Bomb falling', 'The battery', whistle, -10),
    'bay': ('Bomb bay opening', 'The battery', bay, -9),
    'launch': ('Drone launched', 'The battery', launch, -9),
    'knife': ('Jambiya', 'Your weapons', knife, -8),
    'smash_crate': ('Crate smashed', 'The coast road', smash_crate, -7),
    'smash_bags': ('Sandbags hit', 'The coast road', smash_bags, -6),
    'part_off': ('A rotor torn off', 'The battery', part_off, -2.5),
    'boss_fall': ('The boat going down', 'The battery', boss_fall, -5),
    'strike_bells': ('Strike flourish', 'Pickups and score', strike_bells, -8),
    'stamp': ('CLEAR stamped on the map', 'Interface', stamp, -6),
    'paper': ('The map unfolded', 'Interface', paper, -16),
    'route': ('The way marked on the map', 'Interface', route, -15),
    'door_creak': ('A door at the back opening', 'The Coffee Port', door_creak, -10),
    'hiss': ('A vent about to blow', 'The Coffee Port', hiss, -11),
    'steam': ('Steam blowing', 'The Coffee Port', steam, -5),
    'bean_spray': ("The Roaster's spray of beans", 'The Coffee Port', bean_spray, -6),
    'pop': ('A roast bomb out of the hopper', 'The Coffee Port', pop, -7),
    'pour': ('Burning beans poured out', 'The Coffee Port', pour, -8),
    'rev': ('The Roaster winding up its engine', 'The Coffee Port', rev, -6),
    'sack_burst': ('A sack of spice shot open', 'The Souq', sack_burst, -5),
    'thunk': ('A round into the barricade', 'The Souq', thunk, -9),
    'creak_loop': ("The Tailor's stands rolling (loops)", 'The Souq', creak_loop, -10),
    'pigeon': ('A pigeon on the roof', 'The Souq', pigeon, -9),
    'snip': ("The Tailor's shears", 'The Souq', snip, -9),
    'pin_rattle': ('A pinch of pins thrown', 'The Souq', pin_rattle, -11),
    'rip': ("A dummy's clothes shot off", 'The Souq', rip, -7),
    'tape_zip': ('The tape measure run out', 'The Souq', tape_zip, -9),
    'clatter': ('A dummy knocked over', 'The Souq', clatter, -7),
    'whoosh': ('A sheet thrown over the stands', 'The Souq', whoosh, -11),
}


def render_all():
    out = {}
    for name, (label, group, fn, pk) in EFFECTS.items():
        y = np.asarray(fn(seed=3), dtype=np.float64)
        y = y - np.mean(y)
        y = to_peak(y, pk)
        out[name] = y
    return out
