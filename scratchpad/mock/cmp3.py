# Private comparison: reference frames beside my new sprites at the same scale, feet on one line.
# Never a deliverable. Run with python3 -I from the mock directory.
import sys
sys.path.insert(0, '.')
import ms3
from PIL import Image, ImageDraw
out, z = sys.argv[1], int(sys.argv[2])
items = sys.argv[3:]
ims = []
for it in items:
    if it.endswith('.png'):
        r = Image.open(it).convert('RGBA')
        ims.append(r.crop(r.getbbox()))
    elif it.endswith('.png!'):          # flipped reference
        r = Image.open(it[:-1]).convert('RGBA')
        ims.append(r.crop(r.getbbox()).transpose(Image.FLIP_LEFT_RIGHT))
    else:
        ims.append(dict(ms3.CAST)[it]()[0])
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
print(sheet.size, [i.size for i in ims])
