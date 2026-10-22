# Private preview: every head in the cast, composed alone, enlarged.
import sys
sys.path.insert(0, '.')
import ms3 as c
from PIL import Image, ImageDraw
out, z = sys.argv[1], int(sys.argv[2])

def mk(face, wrap, palargs, end=None, nine=None, lean=False, extra=None, wrap_dy=0, wrap_dx=0, kw=None):
    p = c.pal(*palargs, **(kw or {}))
    if nine:
        p['9'] = nine
    B = c.Build(face=(0, 5), wrap=(0, 0))
    L = []
    if end:
        L.append(c.at(c.WRAPS[end], B.wrap, p, -1, 6, ink=c.INK2))
    L.append(c.at(c.FACES[face], B.face, p))
    L.append(c.at(c.WRAPS[wrap], B.wrap, p, wrap_dx, wrap_dy, ink=c.INK2 if wrap != 'pot' else None))
    if extra:
        L += extra(p, B)
    return c.compose(L)[0]

heads = [
    mk('yazeed', 'check', ('blue', 'cream', 'blue', 'skin2'), 'check_end', '#e4dec2',
       extra=lambda p, B: [c.at(c.WRAPS['basil'], B.wrap, p, 1, -1)]),
    mk('salem', 'kufiya', ('white', 'cream', 'cream', 'skin3'), wrap_dy=-1, kw=c.KUFIYA),
    mk('veiled', 'scarf', ('navy', 'navy', 'crimson', 'skin2')),
    mk('arwa', 'flowered', ('rose', 'cream', 'sage', 'skin1')),
    mk('worried', 'check_l', ('olive', 'dark', 'white', 'skin2'), 'check_end', '#b8301c'),
    mk('youth', 'check_l', ('olive', 'dark', 'white', 'skin3'), 'check_end', '#b8301c'),
    mk('angry', 'check_l', ('olive', 'dark', 'white', 'skin1'), 'check_end', '#b8301c'),
    mk('qat_l', 'check_l', ('olive', 'dark', 'white', 'skin2'), 'check_end', '#b8301c'),
    mk('qat', 'check', ('olive', 'dark', 'white', 'skin2'), 'check_end', '#b8301c'),
    mk('cook', 'pot', ('olive', 'dark', 'white', 'skin2'), wrap_dx=-1),
    mk('masked', 'hood', ('black', 'black', 'black', 'skin2'), 'hood_end'),
    mk('elder', 'cap', ('white', 'white', 'white', 'skin3'), wrap_dy=1),
]
W = sum(h.width + 2 for h in heads) + 2
H = max(h.height for h in heads) + 2
sheet = Image.new('RGBA', (W * z, H * z), (138, 132, 120, 255))
x = 2
for h in heads:
    sheet.alpha_composite(h.resize((h.width * z, h.height * z), Image.NEAREST), (x * z, (H - 1 - h.height) * z))
    x += h.width + 2
if z >= 10:
    d = ImageDraw.Draw(sheet)
    for gx in range(0, sheet.width, z):
        d.line([(gx, 0), (gx, sheet.height)], fill=(120, 114, 104, 255))
    for gy in range(0, sheet.height, z):
        d.line([(0, gy), (sheet.width, gy)], fill=(120, 114, 104, 255))
sheet.save(out)
print(sheet.size)
