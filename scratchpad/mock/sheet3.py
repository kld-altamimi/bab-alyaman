# Working contact sheet of the rebuilt cast (no reference material in it).
import sys
sys.path.insert(0, '.')
import ms3
from px import *
args = sys.argv[1:]
out = args[0]; Z = int(args[1]); names = args[2:] or [n for n, _ in ms3.CAST]
fn = dict(ms3.CAST)
ims = [fn[n]() for n in names]
w = sum(im.width + 8 for im, _, _ in ims) + 8
sheet = new(w, 66, hexc('#8a8478'))
rect(sheet, 0, 60, w - 1, 60, '#5a544a')
x = 8
for im, fx, fy in ims:
    blit(sheet, im, x, 59 - fy)
    x += im.width + 8
save(sheet, out, Z)
print(sheet.size)
