# spokesman_lines.py - Ibb's Spokesman (Mission 4; game-direction-R4, stage 1, 24 Oct): his voice and his five
# statements. The voice is the one Khaled approved on 24 Oct (game-direction's measurements from two real clips: a base
# near 175 Hz with the stresses thrown up near 290, each phrase opening high and falling, 4-4.5 syllables a second, the
# last syllable of every sentence held long and rising, half a second between phrases and none inside, nasal, strained,
# screaming), driven into a television speaker. Gibberish only, as every voice in the game: the Arabic is the subtitle
# (Khaled's approved text, claude/topics/game-direction-brief-ibb.md), the English is this chat's, for his OK.
# A few nonsense words come back on purpose, as the real thing repeats itself: *daa-ma-run *kuu-tiim (an important
# statement), um-*qa-fad da-*maar (end of statement), faq-*rii7 (correction), *saa-miid (Taiz), *quum (the Uncle),
# ka-ba-*rii-ya (the operation), *lam-ba-ra (the roaster), *maa-sir (the boat), bi-la-*muu7 (successfully).
#   python3 spokesman_lines.py [out dir]      -> one wav per statement and per line, and lines.json (timings, subtitles)
import json, os, sys
import numpy as np
from scipy import signal
from core import *
import voice as V

SPOKESMAN = V.Voice(f0=196, rng_st=11.0, decl=3.0, final=-7.0, rate=1.25, vt=0.93, tilt=0.8, breath=0.05,
                    jitter=0.02, nasal=0.3, growl=0.45, stacc=0.85, top=6.0, name='The Spokesman')
V.CAST['spokesman'] = SPOKESMAN
BREAK = 0.5                     # between phrases (none inside one)


def tv(x, seed=0):
    """A small television speaker: band-limited, a little compressed (game-direction's treatment on the approved clip)."""
    b, a = signal.butter(2, [220 / (SR / 2), 4200 / (SR / 2)], btype='band')
    y = signal.lfilter(b, a, x)
    return np.tanh(y * 1.8) / 1.8


IMPORTANT = ('بيان مهم.', 'An important statement.', '*daa-ma-run , *kuu-tiiiiim ! .')
END = ('انتهى البيان.', 'End of statement.', 'um-*qa-fad da-*maaaaaar . .')

STATEMENTS = {
    # A, the recap: Ibb's spine, a few lines on each screen across the zones
    'A': [
        IMPORTANT,
        ('نفّذت قوات الزنابيل عملية نوعية في تعز.', 'Zanabeel forces carried out a special operation in Taiz.',
         '*taq-ra-dam lu-*waa-fi sa-ma-*nii-ru ka-ba-*rii-ya daq-*muu-la , bi *saa-miiiiid ! .'),
        ('بمحمصة، ومدفع من القلعة، وقارب طائر.', 'With a roaster, a cannon from the castle, and a flying boat.',
         'bi-*lam-ba-ra , wa-*tur-qa-fin ma-sal *dah-ka , wa-*maa-sir *taa-yi-raaaaa ! .'),
        ('تصحيح: القارب الطائر لم يكن في تعز.', 'Correction: the flying boat was not in Taiz.',
         'faq-*rii7 , al-*maa-sir at-*taa-yir lam *ya-kun bi *saa-miiiiid ! .'),
        ('وقد حققت العملية أهدافها بنجاح.', 'The operation achieved its objectives successfully.',
         'wa-tim *sar-qa-ba-dil ka-ba-*rii-ya um-*daa-ki-haa , bi-la-*muuuuuu7 ! .'),
        ('تصحيح: معظم أهدافها.', 'Correction: most of its objectives.',
         'faq-*rii7 , *dur-ma-fa um-*daa-ki-haaaaaa ! .'),
        ('تعز ما زالت بأيدينا.', 'Taiz remains in our hands.',
         '*saa-mid laa *buu-kat ra-ha-*nii-daaaaaa ! .'),
        ('في معظمها.', 'Most of it.', 'bi *dur-ma-fi-haaaaaa ! .'),
        ('والعمليات مستمرة حتى يرضى العم.', 'Operations continue until the Uncle is satisfied.',
         'wa-la-ras-ka-*dum-mu ka-ba-rii-*maa-ku-naa , *fat-taa *rab-da-3al *quuuuum ! .'),
        END,
        ('ما زلنا على الهواء؟', 'Are we still on air?', 'laa *tir-daa ka-lal ma-*suuuuuu ? .'),
    ],
    # B, the numbers: at the school or on the terraces (Yazeed loses a sandal for a zone)
    'B': [
        IMPORTANT,
        ('استهدفنا العدو بعشرين صاروخاً.', 'We struck the enemy with twenty missiles.',
         'is-*tah-da-fan *nal-ma-raa bi-*3ish-ra-na sa-*raa-qi-faaaaa ! .'),
        ('انفجر منها ١٨ قبل أن تُطلق.', 'Eighteen of them blew up before launch.',
         '*daf-ja-ra *min-haa ta-ma-*nii-sar , *kab-la *tum-la-qaaaaa ! .'),
        ('و٢ وهما في الطريق.', 'And two on the way.', 'wa-*tin-naa-san , wa-*mu-haa bi *dar-raa-qiiiii ! .'),
        ('وقد تم الاستحواذ على فردة نعل من العدو.', 'One enemy sandal has been captured.',
         'wa-kad *tam-ma-lis tah-*waa-qu da-la *far-ra-ti *naa-lin ma-sal *ma-raaaaaa ! .'),
        ('وبهذا تم إنجاز أهدافنا بنجاح.', 'Our objectives have thus been achieved successfully.',
         'wa-bi-*haa-za *tam-mal in-*jaa-su um-*daa-ki-naa , bi-la-*muuuuuu7 ! .'),
        END,
    ],
    # C, the warning: the opening billboard, the first thing Yazeed sees
    'C': [
        IMPORTANT,
        ('ندعو المدعو يزيد إلى الهدنة وضبط النفس.', 'We call upon the so-called Yazeed to observe the truce and show restraint.',
         '*nad-3u-lal *mad-3u *yaa-ziid , i-lal *hud-na-ti wa-*dab-ta *nab-saaaaaa ! .'),
        ('وإن أي تقدّم إضافي إلى إب سيُقابَل بالرد.', 'Any further advance on Ibb will be met with a response.',
         'wa-*nay ta-*qad-da-ma id-*daa-fi la-*ab-bin , sa-ru-*qaa-ba-lu bil-*raaaaad ! .'),
        ('رداً قاسياً.', 'A harsh response.', '*raz-zan *kaa-si-yaaaaaa ! .'),
        ('وربما أقسى.', 'Possibly harsher.', 'wa-*rub-ba-na *aq-taaaaaa ! .'),
        ('لقد حُذّرتم.', 'You have been warned.', 'la-kad *suz-zir-tuuuuum ! .'),
        ('أنت، وسائقك، والسيارة.', 'You, your driver, and the car.',
         '*an-da , wa-*saa-ri-qak , wal-say-*yaa-raaaaaa ! .'),
        END,
    ],
    # D, the operation's name: the podium speech on the terraces, when Yazeed walks in
    'D': [
        IMPORTANT,
        ('نعلن انطلاق عملية «الريح العاتية الصامدة المظفّرة».', 'We announce the launch of Operation Steadfast Victorious Mighty Wind.',
         'nu3-*la-nu in-ta-*raa-qa ka-ba-*rii-ya , ar-*rii-hal *3aa-ta-ya as-*saa-ma-da al-mu-*zaf-fa-raaaaa ! .'),
        ('توازن الصمود ٤٧.', 'Balance of Steadfastness 47.', 'ta-*waa-sun as-sa-*muud , *sab-3a wa-ar-*ba-3iiiiin ! .'),
        ('الجزء الثاني، المرحلة الأولى.', 'Part Two, Phase One.', 'al-*guz-u at-*taa-nii , al-*mar-ra-la al-*uu-laaaaaa ! .'),
        ('وقد بدأت العملية.', 'The operation has begun.', 'wa-kad *ba-da-at ka-ba-*rii-yaaaaaa ! .'),
        ('وانتهت.', 'And ended.', 'wan-*ta-qaaaaat ! .'),
        ('وستُعلن نتائجها في بيان لاحق.', 'Its results will be announced in a later statement.',
         'wa-sa-tu3-*lan na-*taa-ri-ju-haa bi *daa-ma-rin *laa-hiiiiiq ! .'),
        IMPORTANT,
        ('الساعة الرابعة.', 'The time is four o\'clock.', 'as-*saa-3a ar-*raa-bi-3aaaaa ! .'),
        END,
    ],
    # E, the Uncle: the last thing the screens play before the back room dies
    'E': [
        IMPORTANT,
        ('تؤكّد قوات الزنابيل أن العم راضٍ.', 'Zanabeel forces confirm that the Uncle is satisfied.',
         'tu-*ak-kid lu-*waa-fi sa-ma-*nii-ru an-nal *quum *raa-diiiiin ! .'),
        ('راضٍ جداً.', 'Very satisfied.', '*raa-din *jid-daaaaaa ! .'),
        ('وأن المحمصة لم تكن من ضمن الاتفاق.', 'And that the roaster was not part of the deal.',
         'wa-an-nal *lam-ba-ra lam *ta-kun min *dim-nil it-ti-*faaaaaq ! .'),
        ('ولا القارب.', 'Nor the boat.', 'wa-*lal *maa-siiiir ! .'),
        ('ولا خدشه.', 'Nor scratching it.', 'wa-laa *xad-su-huuuuu ! .'),
        ('ونؤكّد أننا لم نخدشه.', 'We confirm we did not scratch it.', 'wa-nu-*ak-kid an-*na-naa lam *nax-dis-huuuuu ! .'),
        ('والعمليات مستمرة حتى يرضى العم.', 'Operations continue until the Uncle is satisfied.',
         'wa-la-ras-ka-*dum-mu ka-ba-rii-*maa-ku-naa , *fat-taa *rab-da-3al *quuuuum ! .'),
        ('أكثر.', 'More.', '*ak-taaaaar ! .'),
        END,
    ],
}

# his lines in person (no television: the studio's microphone, then nothing)
IN_PERSON = {
    'stunned': ('ماذا؟ ارفع صوتك!', 'WHAT? SPEAK UP!', '*maa-daa ? *ar-fa3 *saw-taaaak ! .'),
}


def line(babble, seed, screen=True):
    y = SPOKESMAN.say(babble, seed=seed, final=5)
    if screen:
        y = tv(y, seed)
    return V.level(y, -17.0)


def statement(key, seed0=0):
    """-> (audio, [(t0, t1, ar, en), ...]): the phrases one after another, half a second apart."""
    parts, subs, t = [], [], 0.0
    for i, (ar, en, bab) in enumerate(STATEMENTS[key]):
        y = line(bab, seed0 + i)
        parts += [y, np.zeros(n_of(BREAK))]
        subs.append((round(t, 3), round(t + len(y) / SR, 3), ar, en))
        t += len(y) / SR + BREAK
    return np.concatenate(parts), subs


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/ibb/s1/audio'
    os.makedirs(out, exist_ok=True)
    meta = {}
    for k in STATEMENTS:
        y, subs = statement(k, seed0=100 * (ord(k) - 64))
        write_wav(os.path.join(out, 'statement_%s.wav' % k), y)
        meta[k] = dict(seconds=round(len(y) / SR, 2), lines=subs)
        print(k, '%.1f s, %d lines, %.1f syllables a second' % (len(y) / SR, len(subs), sum(len([c for c in b.replace('-', ' ').split() if c not in '.,!?']) for _, _, b in STATEMENTS[k]) / (len(y) / SR)))
    y = line(IN_PERSON['stunned'][2], 7, screen=False)
    write_wav(os.path.join(out, 'stunned.wav'), y)
    json.dump(meta, open(os.path.join(out, 'lines.json'), 'w'), ensure_ascii=False, indent=1)
