# build_dhamar_music.py - render Dhamar's stage theme to out/music_dhamar.npy and .wav, report its levels, and add it to
# out/music.json beside the others (export_dhamar_music.py makes the MP3).
import json, sys, time
import numpy as np
from core import *
import music_dhamar as T, meter


def main():
    rev = reverb_ir(1.1, seed=3)
    info = json.load(open('out/music.json'))
    print('long notes a semitone off the strings under them:', T.check_tunes() or 'none')
    t0 = time.time()
    s = T.dhamar_theme()
    out, rep = s.render(T.DH_LEVELS, T.DH_SENDS, rev, master_lufs=-16.0, loop=True)
    meter.report('music_dhamar', out, loop=True)
    np.save('out/music_dhamar.npy', out.astype(np.float32))
    write_wav('out/music_dhamar.wav', out)
    info['music_dhamar'] = dict(seconds=round(len(out) / SR, 4), bpm=s.bpm, bars=s.bars, loop=True, lufs=round(lufs(out), 1),
                                limiter_db=rep['_master']['limiter_db'], stems={k: v[0] for k, v in rep.items() if k != '_master'})
    print('   limiter %.1f dB, %.1fs to render' % (rep['_master']['limiter_db'], time.time() - t0))
    json.dump(info, open('out/music.json', 'w'), indent=1, default=float)


if __name__ == '__main__':
    main()
