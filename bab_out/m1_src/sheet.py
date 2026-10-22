# sheet.py - lay frames of one scene side by side, cropped around the action, enlarged
import sys, glob, os
from PIL import Image, ImageDraw
D = '/home/claude/bab_out/m1_src/shots/frames/'
def sheet(name, box=None, zoom=3, cols=4):
    fs = sorted(glob.glob(D + name + '_*.png'))
    ims = [Image.open(f).convert('RGB') for f in fs]
    if box: ims = [im.crop(box) for im in ims]
    w, h = ims[0].size
    rows = (len(ims) + cols - 1) // cols
    S = Image.new('RGB', (cols * (w * zoom + 4), rows * (h * zoom + 4)), (20, 20, 30))
    for i, im in enumerate(ims):
        im = im.resize((w * zoom, h * zoom), Image.NEAREST)
        d = ImageDraw.Draw(im); d.text((3, 2), os.path.basename(fs[i])[len(name) + 1:-4], fill=(255, 255, 0))
        S.paste(im, ((i % cols) * (w * zoom + 4), (i // cols) * (h * zoom + 4)))
    S.save(D + 'sheet_' + name + '.png')
    return S.size
if __name__ == '__main__':
    args = sys.argv[1:]
    name = args[0]
    box = tuple(int(v) for v in args[1].split(',')) if len(args) > 1 and args[1] != '-' else None
    zoom = int(args[2]) if len(args) > 2 else 3
    cols = int(args[3]) if len(args) > 3 else 4
    print(name, sheet(name, box, zoom, cols))
