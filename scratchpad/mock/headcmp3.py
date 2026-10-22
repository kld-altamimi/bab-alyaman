# Private preview: heads of my new sprites enlarged with a grid, optionally beside reference crops.
import sys
sys.path.insert(0, '.')
import ms3
from PIL import Image, ImageDraw
out, z = sys.argv[1], int(sys.argv[2])
items = sys.argv[3:]
crops = []
for it in items:
    flip = it.endswith('!')
    if flip:
        it = it[:-1]
    if it.endswith('.png'):
        r = Image.open(it).convert('RGBA')
        r = r.crop(r.getbbox())
        if flip:
            r = r.transpose(Image.FLIP_LEFT_RIGHT)
        c = r.crop((0, 0, r.width, 17))
    else:
        im = dict(ms3.CAST)[it]()[0]
        c = im.crop((0, 0, im.width, 17))
    # keep the columns around the head: find the column range of the top 8 rows
    top = c.crop((0, 0, c.width, 8))
    bb = top.getbbox()
    x0 = max(0, bb[0] - 2); x1 = min(c.width, bb[2] + 3)
    crops.append(c.crop((x0, 0, x1, 17)))
W = sum(c.width + 2 for c in crops) + 2
sheet = Image.new('RGBA', (W * z, 19 * z), (138, 132, 120, 255))
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
