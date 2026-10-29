# add_speech.py - a mission's own spoken lines, in a file of their own that the game fetches only with that mission (as
# it does a mission's music), so nobody pays for them who never goes there. Ibb (stage 2, 24 Oct): the Spokesman's five
# statements, line by line (the screens play them; the nearest one carries the voice and the subtitle). Each line
# also gets the shape of his mouth, a frame every 1/15 s
# (0 shut, 1 half, 2 wide), measured off its own loudness, for the screen that is saying it.
# The file is laid out as voices.mp3 is (a click, then the clips), so the game lines it up the same way.
# Ibb's own lines from the cast go on the end, after the statements (29 Oct: Yazeed's to the child who stops to wave, at
# the school), in their own voices, as add_voices.py makes them; then the claps of his audience at the rally (29 Oct
# 21:36, the storyboard "looks great": claps.py), played over everything else, under no subtitle.
#   python3 add_speech.py              -> audio/speech_ibb.mp3, and gen/audio.json's 'speech' gains 'ibb'
import json, os, subprocess, sys
import numpy as np
from core import *
import voice as V
import spokesman_lines as S

# the same layout as voices.mp3 (copied from add_voices.py, which runs when imported)
MARK, GAP = 0.05, 0.1
GEN = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/gen/'
AUD = '/home/claude/bab_out/m1/audio/'


def marker():
    n = n_of(0.0012)
    t = np.arange(n) / SR
    return np.sin(TAU * 4000 * t) * np.hanning(n) * 0.6


def sprite(clips):
    parts = [np.zeros(n_of(MARK)), marker(), np.zeros(n_of(0.15))]
    at = {}
    pos = sum(len(p) for p in parts)
    for name, y in clips:
        y = fade(np.asarray(y, dtype=float).copy(), 0.0001, 0.004)
        at[name] = [round(pos / SR, 4), round(len(y) / SR, 4)]
        parts += [y, np.zeros(n_of(GAP))]
        pos += len(y) + n_of(GAP)
    return np.concatenate(parts), at

WHO = 'BRIGADIER BREAKING'                       # «العميد عاجل» (Khaled, 24 Oct)
# the cast's lines in Ibb: id -> (speaker, who, subtitle, babble, options); «روح البيت. وطمّن أمك.» (Khaled, 29 Oct: "All good")
CAST_LINES = {
    'yazeed_home': ('yazeed', 'YAZEED', 'Go home. Tell your mother.', '*ruu7 *al-bayt . . wa-*tam-min *um-mak', {}),
    'yazeed_beret': ('yazeed', 'YAZEED', 'Nice beret.', '*bay-reh *7il-wa', {}),          # (the rally: he stops mid-word)
}
FPS = 15


def mouth_track(y):
    a = np.abs(np.asarray(y, dtype=float))
    a /= a.max() + 1e-9
    n = int(np.ceil(len(a) / SR * FPS))
    out = ''
    for i in range(n):
        seg = a[int(i * SR / FPS):int((i + 1) * SR / FPS)]
        r = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
        out += '0' if r < 0.06 else ('1' if r < 0.2 else '2')
    return out


def lines():
    """-> [(id, text, babble, seed)]: every line of the five statements once (the lines they share, once)."""
    seen, out = {}, []
    for key in sorted(S.STATEMENTS):
        for i, (ar, en, bab) in enumerate(S.STATEMENTS[key]):
            if en in seen:
                continue
            lid = {'An important statement.': 'sp_important', 'End of statement.': 'sp_end',
                   'Operations continue until the Uncle is satisfied.': 'sp_ops'}.get(en, 'sp_%s%d' % (key, i + 1))
            seen[en] = lid
            out.append((lid, en, bab, 100 * (ord(key) - 64) + i))
    return out, seen


def order(seen):
    """Each statement as the list of its line ids, in order."""
    return {key: [seen[en] for _, en, _ in S.STATEMENTS[key]] for key in sorted(S.STATEMENTS)}


if __name__ == '__main__':
    todo, seen = lines()
    clips, meta = [], {}
    for lid, en, bab, seed in todo:
        y = S.line(bab, seed)
        clips.append((lid, y))
        meta[lid] = dict(who=WHO, text=en, m=mouth_track(y))
    for lid in sorted(CAST_LINES):
        sp, who, en, bab, opt = CAST_LINES[lid]
        y = V.level(V.dry(V.CAST[sp].say(bab, seed=sum(map(ord, lid)) % 997, **opt), seed=5))
        clips.append((lid, y))
        meta[lid] = dict(who=who, text=en)
    import claps
    for lid, y in sorted(claps.clips().items()):
        clips.append((lid, y))
        meta[lid] = dict(who='', text='')
    strip, at = sprite(clips)
    write_wav('out/tmp/speech_ibb.wav', strip)
    # (at half the rate the voices use: his lines come through a television and stop at 4.2 kHz anyway; a fifth smaller)
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', 'out/tmp/speech_ibb.wav', '-ar', '22050', '-codec:a', 'libmp3lame',
                    '-compression_level', '0', '-q:a', str(VBR['voices']), '-write_xing', '1', AUD + 'speech_ibb.mp3'], check=True)
    size = os.path.getsize(AUD + 'speech_ibb.mp3')
    for lid in meta:
        meta[lid]['at'] = at[lid]
    au = json.load(open(GEN + 'audio.json'))
    au.setdefault('speech', {})['ibb'] = dict(file='speech_ibb', lines=meta, statements=order(seen))
    json.dump(au, open(GEN + 'audio.json', 'w'), separators=(',', ':'))
    print('speech_ibb.mp3: %d lines, %.1f s, %.0f KB' % (len(clips), len(strip) / SR, size / 1024))
