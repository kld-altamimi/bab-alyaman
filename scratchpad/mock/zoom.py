import sys
sys.path.insert(0, '.')
import ms2
from px import *
names = sys.argv[2:]
out = sys.argv[1]
fn = dict(ms2.CAST)
ims = [fn[n]() for n in names]
w = sum(im.width + 8 for im, _, _ in ims) + 8
sheet = new(w, 70, hexc('#8a8478'))
x = 8
rect(sheet, 0, 65, w - 1, 65, '#5a544a')
for im, fx, fy in ims:
    blit(sheet, im, x, 64 - fy)
    x += im.width + 8
save(sheet, out, 8)
print(sheet.size)
