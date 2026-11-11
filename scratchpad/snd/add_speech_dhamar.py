# add_speech_dhamar.py - Dhamar's own spoken lines (Mission 5, the Wadi; the test build of zones 1-3, Khaled 11 Nov 03:25),
# in a file of their own that the game fetches only with Dhamar (add_speech.py's way, its layout: a click, then the clips).
# Gibberish only (voice.py's babble); the lines are the brief's (game-direction-brief-dhamar.md, "Lines"), no real quote.
#   the Committee (committee_voice.py's voice and his rebuilt laugh, the placeholders Khaled took for this build): his
#     vote's lines through the microphones on his table; the laugh close through them; the laugh through a checkpoint's
#     speakers on its pole (cut shorter: the 4x4 does not stop for it); each with the shape of his mouth (1/15 s frames);
#   Salem, Yazeed, the teacher, the drafted, the announcer, in the cast's voices (voice.py), as add_voices.py makes them.
#   python3 add_speech_dhamar.py   -> audio/speech_dhamar.mp3, and gen/audio.json's 'speech' gains 'dhamar'
import json, os, subprocess, sys
import numpy as np
from core import *
import voice as V
import committee_voice as CV
from add_speech import sprite, mouth_track, GEN, AUD

# id -> (speaker, who, subtitle, babble, options)
CAST_LINES = {
    'salem_checkpoint': ('salem', 'SALEM', 'Checkpoint. Again. Hold on.', '*nug-tat taf-*tiic . *mar-ra *taa-nya . ta-*mas-sak !', {}),
    'salem_stamp': ('salem', 'SALEM', 'The stamp said left.', 'al-*xatm *gaal ya-*saar .', dict(final=-2)),
    'yazeed_committee': ('yazeed', 'YAZEED', 'One man. Whole committee.', '*rij-jaal *waa-7id . . *laj-na *kaa-mi-la', {}),
    'yazeed_bath': ('yazeed', 'YAZEED', 'Good. A hot bath.', 'ta-*maam . . *7am-maam *7aar', {}),
    'teacher_pupils': ('elder', 'THE TEACHER', 'My pupils. Not his.', '*tul-laa-bi . . *muu *7ag-geh', {}),
    'grunt_wages': ('grunt', 'THE DRAFTED', 'And the wages?!', 'war-ra-*waa-tib ?', dict(final=7)),
    'ann_flame': ('announcer', 'ANNOUNCER', 'FLAMETHROWER!', 'fuu-*waaaaaaaa-cuuuu !', dict(final=-9, f0=205, hold_vib=0.45)),
    'ann_wadi': ('announcer', 'ANNOUNCER', "AND WE'RE OFF! THE WADI!", 'ha-*yaa da-*raa-ni ! . al-*waa-diiiiii !', dict(final=-7, hold_vib=0.35)),
}
# Ibb's line to the first child out, said again in Dhamar's recruiting office: the same voice, the same take (Ibb's seed),
# under an id of its own (a line belongs to one mission's file)
CAST_LINES['yazeed_home_d'] = ('yazeed', 'YAZEED', 'Go home. Tell your mother.', '*ruu7 *al-bayt . . wa-*tam-min *um-mak', {})
SEED_OF = {'yazeed_home_d': 'yazeed_home'}
# the Committee's lines at his vote (the brief's): «المحضر! مين يكتب المحضر؟» «كل من يوافق؟» «صوّتت اللجنة. بالإجماع.»
# «مُسجّل.» «الاقتراح مرفوض.» «مجنّد. تحضر الثلاثاء.» as sounds
COMMITTEE_LINES = {
    'cm_minutes': ("Minutes! Who's taking the minutes?", '*al-mah-Dar ! . *miin yik-*tub al-*mah-Dar ?', dict(final=3)),
    'cm_favour': ('All in favour?', CV.MOTION, dict(final=4)),
    'cm_voted': ('The Committee has voted. Unanimously.', CV.MINUTES, {}),
    'cm_noted': ('Noted.', '*mu-saj-jal .', dict(final=-3)),
    'cm_denied': ('Motion denied.', 'al-ig-*ti-raa7 . *mar-fuuD .', dict(final=-3)),
    'cm_drafted': ('Drafted. Report Tuesday.', '*mu-jan-nad . . *tah-Dar at-tu-*laa-taa', {}),
}
WHO_CM = 'THE COMMITTEE'


def mics(x):
    """Through the microphones on his table and the springs' loudspeakers: a little bright, a little pushed, the stone
    walls of the car park coming back. Not the loudhailer (he has none since 11 Nov 03:19)."""
    y = soft(filt(x, hp(170), lp(6800), peak(2500, 1.0, 3.5)) * 1.6, 1.4)
    n = len(y) + n_of(0.45)
    out = np.zeros(n)
    out[:len(y)] += y
    for d, g, c in ((0.07, 0.20, 3600), (0.16, 0.10, 2600), (0.29, 0.05, 1800)):
        a = n_of(d)
        out[a:a + len(y)] += filt(y, lp(c)) * g
    return fade(out, 0.003, 0.02)


def check_words():
    bad = []
    texts = [b for _, _, _, b, _ in CAST_LINES.values()] + [b for _, b, _ in COMMITTEE_LINES.values()]
    for text in texts:
        flat = ''.join(ch for ch in text if ch.isalnum() or ch in "'")
        for w in V.AVOID:
            if w in flat:
                bad.append((text, w))
    return bad


if __name__ == '__main__':
    bad = check_words()
    if bad:
        raise SystemExit('avoid: %r' % bad)
    clips, meta = [], {}
    for lid in sorted(COMMITTEE_LINES):
        en, bab, opt = COMMITTEE_LINES[lid]
        dry = CV.COMMITTEE.say(bab, seed=sum(map(ord, lid)) % 997, **opt)
        y = V.level(mics(dry))
        clips.append((lid, y))
        meta[lid] = dict(who=WHO_CM, text=en, m=mouth_track(dry))
    # the laugh: close, through the microphones at his vote; and through a checkpoint's speakers, the first five seconds of
    # it (the chuckles, the first bout, a breath) fading
    dry_laugh, marks = CV.laugh()
    y = V.level(mics(dry_laugh))
    clips.append(('cm_laugh', y))
    meta['cm_laugh'] = dict(who=WHO_CM, text='Ha. Hahaha. Ha.', m=mouth_track(dry_laugh))
    cut = n_of(5.2)
    short = dry_laugh[:cut].copy()
    short[-n_of(0.9):] *= np.linspace(1, 0, n_of(0.9)) ** 1.5
    y = V.level(CV.loudhailer(short, [m for m in marks if m < 5.0], 5))
    clips.append(('cm_speakers', y))
    meta['cm_speakers'] = dict(who='THE SPEAKERS', text='Ha. Hahaha. Haaa.')
    for lid in sorted(CAST_LINES):
        sp, who, en, bab, opt = CAST_LINES[lid]
        seed = sum(map(ord, SEED_OF.get(lid, lid))) % 997
        tr = V.pa if sp == 'announcer' else V.dry
        y = V.level(tr(V.CAST[sp].say(bab, seed=seed, **opt), seed=5))
        clips.append((lid, y))
        meta[lid] = dict(who=who, text=en)
    strip, at = sprite(clips)
    os.makedirs('out/tmp', exist_ok=True)
    write_wav('out/tmp/speech_dhamar.wav', strip)
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', 'out/tmp/speech_dhamar.wav', '-ar', '22050', '-codec:a', 'libmp3lame',
                    '-compression_level', '0', '-q:a', str(VBR['voices']), '-write_xing', '1', AUD + 'speech_dhamar.mp3'], check=True)
    size = os.path.getsize(AUD + 'speech_dhamar.mp3')
    for lid in meta:
        meta[lid]['at'] = at[lid]
    au = json.load(open(GEN + 'audio.json'))
    au.setdefault('speech', {})['dhamar'] = dict(file='speech_dhamar', lines=meta)
    json.dump(au, open(GEN + 'audio.json', 'w'), separators=(',', ':'))
    print('speech_dhamar.mp3: %d lines, %.1f s, %.0f KB' % (len(clips), len(strip) / SR, size / 1024))
    for lid in meta:
        print('  %-18s %5.2f s  %s' % (lid, meta[lid]['at'][1], meta[lid]['text']))
