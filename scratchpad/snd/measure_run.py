# measure_run.py - what the game's loudspeaker output measured like over one recorded run
import sys
import numpy as np
from scipy.io import wavfile
from core import lufs, db, SR
path = sys.argv[1]
sr, x = wavfile.read(path)
x = x.astype(float) / 32768.0
if x.ndim == 1:
    x = np.stack([x, x], axis=1)
n = len(x)
pk = np.abs(x).max()
print('%s: %.1f s, peak %.1f dBFS, loudness %.1f LUFS' % (path.split('/')[-1], n / sr, db(pk), lufs(x)))
near = (np.abs(x) > 0.985).sum()
print('samples within 0.13 dB of full scale: %d' % near)
# second by second
win = sr
rows = []
for i in range(0, n - win + 1, win):
    seg = x[i:i + win]
    rows.append((i // win, db(np.sqrt((seg ** 2).mean()) + 1e-9), db(np.abs(seg).max() + 1e-9)))
print('per second, RMS dB (peak dB):')
print('  ' + '  '.join('%2d:%5.1f(%5.1f)' % r for r in rows[:len(rows) // 2]))
print('  ' + '  '.join('%2d:%5.1f(%5.1f)' % r for r in rows[len(rows) // 2:]))
r = np.array([q[1] for q in rows])
print('quietest second %.1f dB, loudest %.1f dB, median %.1f dB' % (r.min(), r.max(), np.median(r)))
# balance by octave
m = x.mean(axis=1)
spec = np.abs(np.fft.rfft(m * np.hanning(len(m)))) ** 2
f = np.fft.rfftfreq(len(m), 1 / sr)
tot = spec.sum()
print('energy by band: ' + ', '.join('%s %.0f%%' % (lab, 100 * spec[(f >= a) & (f < b)].sum() / tot) for lab, a, b in (('below 120 Hz', 0, 120), ('120-500', 120, 500), ('500-2k', 500, 2000), ('2k-6k', 2000, 6000), ('above 6k', 6000, 30000))))
# left/right
print('left %.1f dB, right %.1f dB' % (db(np.sqrt((x[:, 0] ** 2).mean())), db(np.sqrt((x[:, 1] ** 2).mean()))))
