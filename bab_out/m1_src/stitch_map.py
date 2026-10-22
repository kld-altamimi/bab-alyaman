# stitch_map.py - put the map shots from snap_mapfull.js back together: python3 stitch_map.py <dir> <fresh|all>
import json, sys
from PIL import Image
d, name = sys.argv[1], sys.argv[2]
meta = json.load(open(d + 'full_%s.json' % name))
out = Image.new('RGB', (720, 480), 'black')
for f, cx, cy in meta['shots']:
    im = Image.open(f).convert('RGB')
    pw = round(meta['geo']['w'] / 2)          # picture pixels across (2 screen pixels each)
    im = im.resize((pw, 216), Image.NEAREST)
    # leave out the heading plate in the top left corner, except where nothing else covers it
    for (x0, y0, x1, y1) in [(0, 20, pw, 216), (130, 0, pw, 20)]:
        out.paste(im.crop((x0, y0, x1, y1)), (cx + x0, cy + y0))
out.save(d + 'full_%s.png' % name)
out.resize((1440, 960), Image.NEAREST).save(d + 'full_%s_2x.png' % name)
print('ok', name, pw)
