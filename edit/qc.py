"""Quality gate for a finished reel: fails on what has read as "buggy". Usage: qc.py <video.mp4> [win_y win_h]
  still picture  > 0.4 s (outside the end card, the last 4 s): a game picture that doesn't move reads as a hang
                 (Khaled, 6 Nov, on a reel with 1.1 s and 1.4 s stills: "The video is buggy")
  strobe         3 or more blinks in a second: a blink is a part of the picture jumping bright and back within two
                 frames, as a boss's hit flash does when the heavy MG is on it (the flying boat's full white: 350-550,
                 the Roaster's half-white wash: about 1,100, summed over the 18-px tiles that jump by more than 25);
                 a muzzle flash (25-70), a screen shake or a scrolling picture stays under 200
(win_y win_h: where the picture sits; edit/reel.py passes them: 600 648 upright, 330 648 for the 4:5 cut)"""
import subprocess, sys
import numpy as np
STILL_MAX = 24                 # frames (0.4 s at 60 fps)
TILE, JUMP, BLINK, BLINK_MAX = 18, 25, 200, 2    # tile size, a tile's jump, a frame's blink total, blinks a second
v = sys.argv[1]; y = int(sys.argv[2]) if len(sys.argv) > 2 else 600; h = int(sys.argv[3]) if len(sys.argv) > 3 else 648
w = 270; hh = h // 4 + (h // 4) % 2
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', v, '-vf', f'crop=1080:{h}:0:{y},scale={w}:{hh},format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
a = np.frombuffer(raw, np.uint8); n = len(a) // (w * hh); a = a[:n * w * hh].reshape(n, hh, w).astype(np.int16)
body = n - 240; d = np.abs(a[1:body] - a[:body - 1]).mean((1, 2))
longest = cur = 0
for x in d:
    cur = cur + 1 if x < 0.02 else 0; longest = max(longest, cur)
tm = a[:body, :hh - hh % TILE, :w - w % TILE].reshape(body, hh // TILE, TILE, w // TILE, TILE).mean((2, 4))   # tile brightness
blink = np.zeros(body)
for k in range(1, body - 2):
    rise = tm[k] - tm[k - 1]; back = np.maximum(tm[k] - tm[k + 1], tm[k] - tm[k + 2])
    m = (rise > JUMP) & (back > JUMP); blink[k] = np.minimum(rise, back)[m].sum()
bl = blink >= BLINK
per_s = max(int(bl[i:i + 60].sum()) for i in range(max(1, body - 60)))
print('frames', n, 'longest still', round(longest / 60, 2), 's; blinks: at most', per_s, 'in a second')
i = 0
while i < len(d):
    if d[i] < 0.02:
        j = i
        while j < len(d) and d[j] < 0.02: j += 1
        if j - i > 12: print(' still', round(i / 60, 2), 's to', round(j / 60, 2), '(%.2f s)' % ((j - i) / 60))
        i = j
    else: i += 1
if bl.any(): print(' blinks at', [round(k / 60, 2) for k in np.nonzero(bl)[0]], 's')
sys.exit(1 if longest > STILL_MAX or per_s > BLINK_MAX else 0)
