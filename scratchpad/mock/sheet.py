# Working contact sheet of the cast (no reference material in it).
import sys
sys.path.insert(0, '.')
import ms2
from px import *
names = sys.argv[1:] or [n for n, _ in ms2.CAST]
fn = dict(ms2.CAST)
ims = [fn[n]() for n in names]
per = 6
rows = [ims[i:i + per] for i in range(0, len(ims), per)]
roww = max(sum(im.width + 8 for im, _, _ in r) for r in rows) + 8
sheet = new(roww, 62 * len(rows) + 4, hexc('#8a8478'))
for ri, r in enumerate(rows):
    x = 8
    base = 62 * ri + 56
    rect(sheet, 0, base + 1, roww - 1, base + 1, '#5a544a')
    for im, fx, fy in r:
        blit(sheet, im, x, base - fy)
        x += im.width + 8
Z = 6 if roww <= 320 else 5
save(sheet, 't2_sheet.png', Z)
print(sheet.size, Z, [(n, im.size) for n, (im, _, _) in zip(names, ims)])
