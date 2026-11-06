"""Quality gate for a finished reel: fails on what has read as "buggy". Usage: qc.py <video.mp4> [win_y win_h]
  frozen picture  > 1.5 s (outside the end card, the last 4 s)
  white strobe    more than 3 frames in a second with a big block of pure white (a boss's full-white hit flash)"""
import subprocess, sys
import numpy as np
v = sys.argv[1]; y = int(sys.argv[2]) if len(sys.argv) > 2 else 600; h = int(sys.argv[3]) if len(sys.argv) > 3 else 648
w = 270; hh = h // 4 + (h // 4) % 2
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', v, '-vf', f'crop=1080:{h}:0:{y},scale={w}:{hh},format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
a = np.frombuffer(raw, np.uint8); n = len(a) // (w * hh); a = a[:n * w * hh].reshape(n, hh, w).astype(np.int16)
body = n - 240; d = np.abs(a[1:body] - a[:body - 1]).mean((1, 2))
longest = cur = 0
for x in d:
    cur = cur + 1 if x < 0.02 else 0; longest = max(longest, cur)
c = (a[:body] > 245).sum((1, 2)); white = np.r_[False, (c[1:] - c[:-1]) > 40]   # a big block of pure white appearing at once
strobe = max(int(white[i:i + 60].sum()) for i in range(max(1, body - 60)))
print('frames', n, 'longest freeze', round(longest / 60, 2), 's; white strobe', strobe, 'frames in a second')
i = 0
while i < len(d):
    if d[i] < 0.02:
        j = i
        while j < len(d) and d[j] < 0.02: j += 1
        if j - i > 30: print(' freeze', round(i / 60, 2), 's to', round(j / 60, 2))
        i = j
    else: i += 1
sys.exit(1 if longest > 90 or strobe > 3 else 0)
