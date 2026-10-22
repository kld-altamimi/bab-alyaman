# Private comparison lineup on a sand ground: reference frames among my sprites. Never a deliverable.
import sys
sys.path.insert(0, '.')
import ms3
from PIL import Image
out, z = sys.argv[1], int(sys.argv[2])
items = sys.argv[3:]
ims = []
for it in items:
    flip = it.endswith('!')
    if flip:
        it = it[:-1]
    if it.endswith('.png'):
        r = Image.open(it).convert('RGBA')
        r = r.crop(r.getbbox())
        if flip:
            r = r.transpose(Image.FLIP_LEFT_RIGHT)
        ims.append((r, r.height - 1))
    else:
        im, fx, fy = dict(ms3.CAST)[it]()
        ims.append((im, fy))
W = sum(i.width + 6 for i, _ in ims) + 6
H = 64
sheet = Image.new('RGBA', (W, H), (214, 196, 140, 255))
for y in range(56, H):
    for x in range(W):
        sheet.putpixel((x, y), (190, 168, 112, 255))
x = 6
for im, fy in ims:
    sheet.alpha_composite(im, (x, 56 - fy))
    x += im.width + 6
sheet = sheet.resize((W * z, H * z), Image.NEAREST)
sheet.save(out)
print(sheet.size)
