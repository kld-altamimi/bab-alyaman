# build_ibb_music.py - render Ibb's stage theme to out/*.npy and out/*.wav, report their levels, and
# add them to out/music.json beside the others (export_ibb_music.py makes the MP3).
import json, sys, time
import numpy as np
from core import *
import music_ibb as T, meter


def main(which=('music_ibb',)):
    rev = reverb_ir(1.1, seed=3)
    info = json.load(open('out/music.json'))
    bad = T.check_tunes()
    print('long notes a semitone off the strings under them:', bad or 'none')
    jobs = [('music_ibb', T.ibb_theme, T.IBB_LEVELS, T.IBB_SENDS, -16.0)]
    print(' ' * 77 + ' '.join('%4d' % b for b in meter.BANDS))
    for name, fn, levels, sends, target in jobs:
        if name not in which:
            continue
        t0 = time.time()
        s = fn()
        out, rep = s.render(levels, sends, rev, master_lufs=target, loop=True)
        meter.report(name, out, loop=True)
        np.save('out/%s.npy' % name, out.astype(np.float32))
        write_wav('out/%s.wav' % name, out)
        info[name] = dict(seconds=round(len(out) / SR, 4), bpm=s.bpm, bars=s.bars, loop=True,
                          lufs=round(lufs(out), 1), limiter_db=rep['_master']['limiter_db'],
                          stems={k: v[0] for k, v in rep.items() if k != '_master'})
        print('   limiter %.1f dB, %.1fs to render; stems (own LUFS, gain): %s' % (rep['_master']['limiter_db'], time.time() - t0,
              {k: v for k, v in rep.items() if k != '_master'}))
    json.dump(info, open('out/music.json', 'w'), indent=1, default=float)


if __name__ == '__main__':
    main(tuple(sys.argv[1:]) or ('music_ibb',))
