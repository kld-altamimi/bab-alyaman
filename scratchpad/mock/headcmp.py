# Private preview: my heads, enlarged with a grid (no reference pixels in it).
import sys
sys.path.insert(0, '.')
import ms2
from px import *
from PIL import ImageDraw
out, z = sys.argv[1], int(sys.argv[2])
names = sys.argv[3:] or ['yazeed', 'grunt', 'salem', 'bilqis', 'arwa']
fn = dict(ms2.CAST)
BOX = {'yazeed': (8, 0, 26, 17), 'grunt': (7, 0, 25, 17), 'salem': (9, 0, 28, 18), 'bilqis': (3, 0, 22, 17),
       'arwa': (12, 0, 34, 17), 'cook': (8, 0, 27, 17), 'guard': (9, 0, 29, 18), 'detainee_freed': (0, 0, 18, 18),
       'marshal': (6, 0, 30, 22), 'rocketeer': (5, 0, 25, 17), 'bomber': (5, 0, 25, 17), 'doorman': (5, 0, 25, 17),
       'surrender': (0, 0, 22, 19)}
crops = []
for n in names:
    im, fx, fy = fn[n]()
    b = BOX.get(n, (0, 0, im.width, 18))
    crops.append(im.crop((b[0], b[1], min(b[2], im.width), b[3])))
W = sum(c.width + 2 for c in crops) + 2
H = max(c.height for c in crops)
sheet = Image.new('RGBA', (W * z, (H + 2) * z), (138, 132, 120, 255))
x = 2
for c in crops:
    sheet.alpha_composite(c.resize((c.width * z, c.height * z), Image.NEAREST), (x * z, z))
    x += c.width + 2
d = ImageDraw.Draw(sheet)
for gx in range(0, sheet.width, z):
    d.line([(gx, 0), (gx, sheet.height)], fill=(120, 114, 104, 255))
for gy in range(0, sheet.height, z):
    d.line([(0, gy), (sheet.width, gy)], fill=(120, 114, 104, 255))
sheet.save(out)
print(sheet.size)
