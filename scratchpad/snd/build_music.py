# build_music.py - render the four pieces of music to out/*.npy and out/*.wav and report their levels.
import sys, time, json
import numpy as np
from core import *
import music as M, meter


def main():
    rev = reverb_ir(1.1, seed=3)
    info = {}
    jobs = [('music_strait', M.strait_theme, M.STRAIT_LEVELS, True, -16.0),
            ('music_battery', M.battery_theme, M.BATTERY_LEVELS, True, -16.0),
            ('jingle_start', M.mission_start, M.JINGLE_LEVELS, False, -15.0),
            ('jingle_complete', M.mission_complete, M.JINGLE_LEVELS, False, -15.0)]
    print(' ' * 77 + ' '.join('%4d' % b for b in meter.BANDS))
    for name, fn, levels, loop, target in jobs:
        t0 = time.time()
        s = fn()
        out, rep = s.render(levels, M.SENDS, rev, master_lufs=target, loop=loop)
        if not loop:
            # trim the silence after the last ring and close with a short fade
            m = np.max(np.abs(out), axis=1)
            last = int(np.max(np.nonzero(m > 10 ** (-52 / 20))[0])) + n_of(0.15)
            out = out[:min(len(out), last)]
            out[-n_of(0.05):] *= np.linspace(1, 0, n_of(0.05))[:, None]
        meter.report(name, out, loop=loop)
        np.save('out/%s.npy' % name, out.astype(np.float32))
        write_wav('out/%s.wav' % name, out)
        info[name] = dict(seconds=round(len(out) / SR, 4), bpm=s.bpm, bars=s.bars, loop=loop,
                          lufs=round(lufs(out), 1), limiter_db=rep['_master']['limiter_db'],
                          stems={k: v[0] for k, v in rep.items() if k != '_master'})
        print('   limiter %.1f dB, %.1fs to render' % (rep['_master']['limiter_db'], time.time() - t0))
    json.dump(info, open('out/music.json', 'w'), indent=1, default=float)


if __name__ == '__main__':
    main()
