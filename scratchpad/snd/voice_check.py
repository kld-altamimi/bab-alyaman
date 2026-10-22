# voice_check.py - each placeholder voice's tonal balance against average speech, and hiss against vowel.
import sys
import numpy as np
from scipy import signal
from core import *
import importlib, voice as V
C = (125, 250, 500, 1000, 2000, 4000, 8000)
TARGET = (4.3, 6.1, 8.1, 0, -5.4, -8.5, -10.2)
TEXTS = {'yazeed': 'ma-*raa-li ca-*ban-du . *haa-di-ku *daa-ri ba-*luu-ma . ja-*bii-du ka-*raa-ni *ban-na-hu',
         'salem': 'sa-*waa-gu ! *ti-ma-si *kuu-bi ! ha ha ha ! *kam-ma-ni !',
         'bilqis': '*doo-ca . *muu *ree-fi . *bas *doo-ca *dal-fa . *ruc-bi',
         'arwa': '*lii-ka ! *lii-ka ! ti-*fic-fic ! *hib-tu ma-*lii-fa . *kaa-ba-ran',
         'dispatcher': '*dam-bu-ra *tii-ni . *mu-ba *la-ku-ni ta-*maam . *laa-mi *bu-ka-ru-ha',
         'announcer': 'ha-*yaa da-*raa-ni ! ta-*maam ta-*maam ! ca-ka-*buum !',
         'grunt': 'la la la ! *bad-ti *jum-ba-di ! xa-*laas ! xa-*laas ! *tin-ta-ni !',
         'cook': 'la la la ! *ba-na *maa-lu-bi ! *daa-ri *ful-ba-ti !',
         'elder': '*cuk-ran , *cuk-ran . *hii-mi ba-*lan-tu *ruu-7i *sal-ma-na',
         'guard': '*gun . *duu-ri . *bam',
         'commander': '*un-ba-ru ! *faj-du ka-*raa-ti-li-*naa ! *a-ba-di ta-*luu-man . bi-fa-*xaa-ma-tin'}


def bands(x):
    f, P = signal.welch(x, SR, nperseg=4096)
    out = np.array([10 * np.log10(P[(f >= c / 2 ** 0.5) & (f < c * 2 ** 0.5)].sum() + 1e-20) for c in C])
    return out - out[3]


def report():
    print('%-24s' % 'octave band, Hz' + ''.join('%7d' % c for c in C) + '   s under a   sh under a')
    print('%-24s' % 'speech, long-term avg' + ''.join('%7.1f' % v for v in TARGET) + '     10-15        8-14')
    for sp, tx in TEXTS.items():
        v = V.CAST[sp]
        y = v.say(tx, seed=3)
        ya = v.say('*saaaa', seed=1)
        r = v.rate
        s_ = db(rms(ya[n_of(0.16 / r + 0.03):n_of(0.16 / r + 0.1)])) - db(rms(ya[n_of(0.045):n_of(0.03 + 0.07 / r)]))
        yc = v.say('*caaaa', seed=1)
        c_ = db(rms(yc[n_of(0.16 / r + 0.03):n_of(0.16 / r + 0.1)])) - db(rms(yc[n_of(0.045):n_of(0.03 + 0.07 / r)]))
        print('%-24s' % sp + ''.join('%7.1f' % b for b in bands(y)) + '   %7.1f     %7.1f' % (s_, c_))


if __name__ == '__main__':
    report()
