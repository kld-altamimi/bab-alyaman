# committee_voice.py - the Committee's voice for Dhamar (Mission 5), stage 1: the mocks Khaled hears before any Dhamar code
# (the stage plan approved 10 Nov; game-direction-brief-dhamar.md: "a chairman's drone for the minutes, the loudhailer
# squeal for the motions, and the laugh, long, rising, running out of breath and starting again, through the loudhailer").
# Drawn 10 Nov by the development run. Gibberish only (the babble notation of voice.py); no real quote. His Voice is
# defined here, not in voice.py's CAST, until Khaled says yes to it; then it moves there and his lines go in a
# speech_dhamar.mp3 of their own (add_speech.py's way).
#   python3 committee_voice.py [out folder]   -> committee_minutes.mp3 (the drone, dry), committee_motion.mp3 (through the
#   loudhailer, then the stamp), committee_laugh.mp3 (the laugh through the loudhailer), committee_laugh_dry.mp3 (the same,
#   close), laugh_shape.json (a mouth frame every 1/15 s: 0 shut, 1 half, 2 wide, for the laugh frames) and clips.json
#   (durations). Default out folder: scratchpad/dhamar/s1/.
import json, os, sys
import numpy as np
from core import *
import voice as V
import laugh as L

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dhamar', 's1')
OUT = os.path.abspath(OUT) + '/'
os.makedirs(OUT, exist_ok=True)
TMP = OUT + 'tmp/'
os.makedirs(TMP, exist_ok=True)

# the chairman: low-mid, a narrow range, a slow fall through the sentence, a little through the nose, a slight creak
COMMITTEE = V.Voice(f0=118, rng_st=1.6, decl=1.2, final=-2.0, rate=0.9, vt=1.0, tilt=1.2, breath=0.035, jitter=0.009,
                    creak=0.3, nasal=0.3, stacc=1.05, name='The Committee')

# the babble (voice.py's sounds): «صوّتت اللجنة. بالإجماع.» and «كل من يوافق؟» as sounds, not words
MINUTES = '*saw-wa-tat al-*laj-nah . bil-ij-*maa3'
MOTION = '*kull man yu-*waa-fiq ?'


def check_words():
    bad = []
    for text in (MINUTES, MOTION):
        flat = ''.join(ch for ch in text if ch.isalnum() or ch in "'")
        for w in V.AVOID:
            if w in flat:
                bad.append((text, w))
    return bad


def stamp(seed=3):
    """The stamp coming down on the table: a knock of filtered noise and a low thud that rings out."""
    n = n_of(0.22)
    t = np.arange(n) / SR
    knock = filt(white(n, seed), bp(900, 0.8), lp(2500)) * np.exp(-t / 0.012)
    thud = np.sin(TAU * np.cumsum(np.full(n, 62.0) * (1 + 0.6 * np.exp(-t / 0.01))) / SR) * np.exp(-t / 0.06)
    y = knock * 0.9 + thud * 0.8
    return fade(y / (np.max(np.abs(y)) + 1e-9), 0.001, 0.03)


def squeal(dur=0.18, f=2500.0, up=500.0, amp=0.16):
    """The loudhailer feeding back."""
    n = n_of(dur)
    t = np.arange(n) / SR
    return np.sin(TAU * np.cumsum(f + up * (t / t[-1]) ** 1.5) / SR) * np.hanning(n) ** 0.5 * amp


def laugh(seed=11):
    """The laugh, rebuilt 11 Nov on laugh.py (a voice from glottal pulses, not a synthesiser saying "ha") and measured on
    the wages clip Khaled sent: his laugh starts under his breath, a run of breathy chuckles about five a second (the
    clip, 0:02.7-0:03.7), then breaks out voiced at the pitch he laughs at, 220-330 Hz (a man shouting at a rally, not
    the chairman's 118 Hz drone), the calls nearly flat in pitch (his are), and ends on a loud "HAA" that falls away into
    breath (the clip, 1:24.5). Between them the brief's shape: rising, running out of breath and starting again.
      chuckles  5 breathy pulses, irregular (0.19, 0.19, 0.22, 0.30 s apart), the last ones voicing
      bout 1    7 calls, 5 a second, 240 -> 290 Hz, the head going back
      in        a breath in with a squeak in it
      bout 2    9 calls, faster and higher (300 -> 330 Hz), breathier; the last two squeak an octave up (where the
                loudhailer squeals)
      in        a long wheeze
      bout 3    5 calls slowing and falling (290 -> 230 Hz), the last two only breath
      the end   the clip's "HAA": a strong flat call at 220 Hz that falls away into breath
    Returns (clip, the squeal marks in seconds: where the loudhailer catches)."""
    lg = L.Laugh(vt=0.96, seed=seed)
    r = rng(seed)
    t = 0.06
    # under his breath: the chuckles, as in the clip: short, the mouth shut in a grin, air and a creak through the nose
    for i, gap in enumerate((0.19, 0.19, 0.22, 0.30, 0.0)):
        lg.call(t, 105 + 8 * i, amp=0.34 + 0.07 * i, breath=0.75 - 0.08 * i, h=0.022, voiced=0.035 + 0.008 * i,
                vowel=L.NASAL, fall=3.0, peak=0.0, oq=0.4)
        lg.mix(t, L.snort(seed + i, 0.05) * (0.10 + 0.03 * i))      # the air out through the nose, its click
        t += gap + r.normal(0, 0.008)
    # bout 1: it breaks out
    for i in range(7):
        f0 = 240 + 50 * i / 6 + r.normal(0, 3)
        lg.call(t, f0, amp=0.86 + 0.02 * i, breath=0.22 + 0.02 * i, h=0.03 if i else 0.05, voiced=0.105 - 0.002 * i,
                vowel=L.OPEN, fall=1.5, peak=0.5, oq=0.45)
        t += 0.205 - 0.003 * i + r.normal(0, 0.008)
    t = lg.breath_in(t + 0.02, 0.30, amp=0.42, whoop=(470, 620), whoop_amp=0.3) + 0.03
    # bout 2: helpless, higher, faster, breathier; the last two squeak
    for i in range(9):
        squeak = i >= 7
        f0 = (300 + 30 * i / 6 if not squeak else 520 + 50 * (i - 7)) + r.normal(0, 3)
        lg.call(t, f0, amp=0.95 - 0.03 * i, breath=0.3 + 0.04 * i, h=0.025, voiced=0.09 if not squeak else 0.11,
                vowel=L.GRIN if i % 3 == 2 else L.OPEN, fall=2.5, peak=0.8, oq=0.58 if not squeak else 0.72,
                squeak=squeak, tilt=0.45 if squeak else 0.0)
        t += (0.165 if not squeak else 0.19) + r.normal(0, 0.007)
    t = lg.breath_in(t + 0.03, 0.45, amp=0.5, whoop=(560, 700), whoop_amp=0.22) + 0.05
    # bout 3: out of breath, slowing and falling; the last two only breath
    for i in range(5):
        f0 = 290 - 60 * i / 4 + r.normal(0, 3)
        lg.call(t, f0, amp=0.7 - 0.08 * i, breath=0.45 + 0.13 * i, h=0.04 + 0.01 * i, voiced=0.1 if i < 3 else 0.06,
                vowel=L.SCHWA if i > 2 else L.OPEN, fall=2.0, peak=0.5, oq=0.62 + 0.04 * i)
        t += 0.24 + 0.04 * i
    t += 0.12
    # the end, as in the clip: a strong flat "HAA" that falls away into breath
    t = lg.call(t, 222, amp=1.0, breath=0.15, h=0.04, voiced=0.17, vowel=L.OPEN, fall=0.4, peak=0.2, oq=0.42)
    lg.sigh(t - 0.02, 0.42, f0=(214, 150), amp=0.55, breath=0.7)
    y = lg.render(tail=0.2)
    y = filt(y, hp(90), lp(8000))
    return fade(y / (np.max(np.abs(y)) + 1e-9), 0.003, 0.06), lg.marks


def loudhailer(y, marks=(), seed=0):
    """The laugh through his loudhailer: honky and pushed, but not crushed (the old megaphone() clipped a laugh into
    a buzz), slapping back off the lorries, squealing where the laugh peaks."""
    x = filt(y, hp(480), lp(3900), peak(1900, 1.3, 7.0), peak(900, 1.0, 2.5))
    x = soft(x / (np.max(np.abs(x)) + 1e-9) * 2.2, 1.6) * 0.8
    x = filt(x, hp(420), lp(4200))
    n = len(x) + n_of(0.6)
    out = np.zeros(n + n_of(0.2))
    o = n_of(0.2)                    # 0.2 s before the start: the loudhailer's own squeal as it keys on
    out[o:o + len(x)] += x
    for d, g, c in ((0.115, 0.3, 2400), (0.25, 0.14, 1600), (0.41, 0.07, 1100)):
        a = o + n_of(d)
        out[a:a + len(x)] += filt(x, lp(c)) * g
    m = n_of(0.28)
    tt_ = np.arange(m) / SR
    out[:m] += np.sin(TAU * np.cumsum(2500 + 450 * (tt_ / tt_[-1]) ** 2) / SR) * np.hanning(m) ** 0.5 * 0.18
    for mk in marks:
        sq = squeal(0.22, 2600.0, 600.0, 0.16)
        a = o + n_of(mk)
        out[a:a + len(sq)] += sq[:max(0, len(out) - a)]
    return fade(out, 0.004, 0.03)


def mouth_track(y, fps=15):
    a = np.abs(np.asarray(y, dtype=float))
    a /= a.max() + 1e-9
    n = int(np.ceil(len(a) / SR * fps))
    s = ''
    for i in range(n):
        seg = a[int(i * SR / fps):int((i + 1) * SR / fps)]
        rms = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
        s += '0' if rms < 0.06 else ('1' if rms < 0.2 else '2')
    return s


def save(name, y):
    y = V.level(y)
    write_wav(TMP + name + '.wav', y)
    size = to_mp3_vbr(TMP + name + '.wav', OUT + name + '.mp3', VBR['voices'])
    return dict(seconds=round(len(y) / SR, 2), kb=round(size / 1024, 1), peak=round(float(np.max(np.abs(y))), 3),
                rms=round(float(np.sqrt(np.mean(y ** 2))), 3))


if __name__ == '__main__':
    bad = check_words()
    if bad:
        raise SystemExit('avoid: %r' % bad)
    v = COMMITTEE
    info = {}
    info['committee_minutes'] = save('committee_minutes', V.dry(v.say(MINUTES, seed=1)))
    motion = np.concatenate([V.megaphone(v.say(MOTION, seed=2, final=4), 2, squeal=True), np.zeros(n_of(0.35)), stamp()])
    info['committee_motion'] = save('committee_motion', motion)
    dry_laugh, marks = laugh()
    room = convolve(dry_laugh, reverb_ir(0.35, 0.008, 6000.0, 4))          # close, in a room: not in a box
    close = dry_laugh + room[:len(dry_laugh), 0] * 0.14
    info['committee_laugh_dry'] = save('committee_laugh_dry', close)
    info['committee_laugh'] = save('committee_laugh', loudhailer(dry_laugh, marks, 5))
    shape = mouth_track(dry_laugh)
    json.dump(dict(fps=15, frames=shape, seconds=round(len(dry_laugh) / SR, 2), squeals_at=[round(m, 2) for m in marks],
                   note='0 shut, 1 half, 2 wide, every 1/15 s of committee_laugh_dry (the loudhailer file starts 0.2 s later)'),
              open(OUT + 'laugh_shape.json', 'w'), indent=1)
    json.dump(info, open(OUT + 'clips.json', 'w'), indent=1)
    for k, d in info.items():
        print('%-22s %5.2f s  %5.1f KB  peak %.3f  rms %.3f' % (k, d['seconds'], d['kb'], d['peak'], d['rms']))
    print('laugh shape:', shape)
