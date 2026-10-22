# uncle.py - a voice for the Uncle across the water, for Khaled to hear before it goes in the game (17 Oct).
# He chose reading A ("A is great"): it now lives in voice.py as CAST['uncle'] with the four LINES; this file keeps both readings.
# He asked for a heavy Iranian accent. The synthesiser babbles, so the accent is carried by what Persian has and Arabic
# does not: the back, rounded â (the "aw" of qahve, ârmân); p, v, the ch of chek; qâf said soft and voiced (Ghahve,
# not qahwa); the stress on the last syllable of a word (and on the na- of a verb told not to); pure vowels, an
# even, syllable-by-syllable pace, the pitch up on each stressed syllable and down at the end of the sentence.
# The words: a few everyday Persian ones that say what the subtitle says (khob, chek, post, kodum, qahve), the rest
# nonsense in the same sounds. No religious phrases, no slogans, nothing political (see AVOID_FA).
# He calls over the radio, so every line goes through voice.radio. Two readings to choose from:
#   A  the patron: deep, slow, every word weighed, a tired rattle at the end of each sentence
#   B  the accountant: higher, through the nose, clipped and quick, a little pleased with himself
#
#   python3 uncle.py      writes out/uncle/*.wav and *.mp3, and a reel of the four lines for each reading
import os, sys
import numpy as np
from core import *
import voice as V

# ---- the sounds Persian adds
V.VOW['A'] = (640, 960, 2450)                    # â: back and rounded (between "father" and "law")
V.CON['p'] = ('stop', (200, 900, 2200), (900, 1100, 0.6))
V.CON['v'] = ('vfric', (300, 1050, 2300), (4800, 6000, 0.16))
V.CON['G'] = ('vstop', (480, 1000, 2400), (1150, 900, 0.45))     # qâf/ghein: the uvular stop, voiced
V.BACKING.add('G')

CAST = {
    'A': V.Voice(f0=92, rng_st=3.4, decl=2.4, final=-5.5, rate=0.76, vt=0.96, tilt=1.22, breath=0.045, jitter=0.009,
                 creak=0.35, stacc=1.08, name='The Uncle (the patron)'),
    'B': V.Voice(f0=126, rng_st=5.2, decl=1.4, final=-3.5, rate=0.98, vt=1.0, tilt=1.05, jitter=0.012, nasal=0.55,
                 stacc=0.88, name='The Uncle (the accountant)'),
}

# id: (subtitle, what he says, how it reads, options)
LINES = {
    'uncle_drones': ('The flying boat is a loan. Do not scratch it.',
                     'xob . GA-*ye-Ge pa-ran-*de , *Gar-ze . xat *na-zan !',
                     'khob. qâyeq-e parande, qarz-e. khat nazan!', dict(final=-6)),
    'uncle_guns': ('Use the new guns. Do not ask where from.',
                   'to-fang-*hA-ye ja-*did ! . az ko-*jA ? . *na-por-sid',
                   'tofang-hâ-ye jadid! az kojâ? naporsid.', {}),
    'uncle_coffee': ('I want the coffee. All of it. For the cause.',
                     'Gah-*ve mi-*xAm . ha-ma-*co ! . ba-rA-ye Ar-*mAn',
                     'qahve mikhâm. hamash-o! barâye ârmân.', {}),
    'uncle_cheque': ('The cheque is in the post. Which post? A post.',
                     'tcek tu *pos-te . ko-*dum *post ? . ye *post',
                     'chek tu post-e. kodum post? ye post.', dict(final=-6)),
}

# beside voice.AVOID (Arabic): what must not turn up in the Persian, by accident or otherwise
AVOID_FA = ('xoda', 'xodA', 'emAm', 'imAm', 'imam', 'rahbar', 'marg', 'sepAh', 'basij', 'mollA', 'Axund', 'cAh', 'enGe',
            'enqe', 'moGA', 'moqA', 'cahid', 'cohada', 'kir', 'kos', 'kun', 'jende', 'guz', 'xar', 'kesA', 'jAkec',
            'pedar', 'mAdar', 'irAn', 'iran', 'esrA', 'yahud', 'zan-e')


def check(text):
    flat = ''.join(ch for ch in text if ch.isalnum() or ch in "'")
    return [w for w in V.AVOID + AVOID_FA if w in flat]


def render(who, key):
    sub, text, reads, opt = LINES[key]
    y = CAST[who].say(text, seed=sum(map(ord, key)) % 997, **opt)
    return V.level(V.radio(y, seed=5))


if __name__ == '__main__':
    bad = {k: check(t) for k, (s, t, r, o) in LINES.items() if check(t)}
    if bad:
        sys.exit('words to avoid: %r' % bad)
    out = 'out/uncle/'
    os.makedirs(out, exist_ok=True)
    for who in CAST:
        reel = []
        for key in LINES:
            y = render(who, key)
            name = '%s_%s' % (key, who)
            write_wav(out + name + '.wav', y)
            to_mp3(out + name + '.wav', out + name + '.mp3', 128)
            reel += [y, np.zeros(n_of(0.9))]
            print('%-14s %s  %.2f s   %s' % (name, who, len(y) / SR, LINES[key][2]))
        r = np.concatenate([np.zeros(n_of(0.3))] + reel)
        write_wav(out + 'uncle_%s_all.wav' % who, r)
        to_mp3(out + 'uncle_%s_all.wav' % who, out + 'uncle_%s_all.mp3' % who, 128)
