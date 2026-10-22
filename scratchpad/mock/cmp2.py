# Private comparison: a reference frame beside my sprites at the same scale, feet on one line.
# Never a deliverable. Run with python3 -I from the mock directory (reads one reference file by path).
import sys
sys.path.insert(0, '.')
import ms2
from PIL import Image, ImageDraw
ref, out, z = sys.argv[1], sys.argv[2], int(sys.argv[3])
names = sys.argv[4:]
r = Image.open(ref).convert('RGBA')
r = r.crop(r.getbbox())
fn = dict(ms2.CAST)
ims = [r] + [fn[n]()[0] for n in names]
H = max(i.height for i in ims) + 4
W = sum(i.width + 4 for i in ims) + 4
sheet = Image.new('RGBA', (W * z, H * z), (138, 132, 120, 255))
x = 4
for im in ims:
    sheet.alpha_composite(im.resize((im.width * z, im.height * z), Image.NEAREST), (x * z, (H - 2 - im.height) * z))
    x += im.width + 4
if z >= 8:
    d = ImageDraw.Draw(sheet)
    for gx in range(0, sheet.width, z):
        d.line([(gx, 0), (gx, sheet.height)], fill=(120, 114, 104, 255))
    for gy in range(0, sheet.height, z):
        d.line([(0, gy), (sheet.width, gy)], fill=(120, 114, 104, 255))
sheet.save(out)
print(sheet.size)
