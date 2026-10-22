# Private comparison: our sprite beside one reference frame at the same zoom. Not a deliverable.
import sys
from PIL import Image
sys.path.insert(0, '.')
import importlib
import ms2
from px import *
names = sys.argv[1:] or ['yazeed']
ims = [getattr(ms2, n)() for n in names]
m = Image.open('../ref2/nathancy_Metal-Slug/Metal_Slug/PlayerIdle/0.png').convert('RGBA')
w = 44 + sum(im.width + 6 for im, _, _ in ims)
sheet = new(w, 56, hexc('#8a8478'))
sheet.alpha_composite(m, (4, 50 - m.height + 1))
x = 44
for im, fx, fy in ims:
    blit(sheet, im, x, 50 - fy)
    x += im.width + 6
Z = 10 if w <= 150 else 8 if w <= 230 else 6
save(sheet, 't2_cmp.png', Z)
print(sheet.size, [im.size for im, _, _ in ims])
