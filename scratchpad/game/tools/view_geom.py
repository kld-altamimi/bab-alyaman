# view_geom.py - the play layer with a ruler on it, to place platforms by eye as well as by number
import sys
sys.path.insert(0, '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock')
import numpy as np
from PIL import Image, ImageDraw
import stage
import scene_strait as SS
from paint import Layer, from_image

S = stage.build_layers()
L = Layer(stage.STAGE_W, stage.SH)
sky, far, sea = SS.wide_layers()
L.paste(sky, 0, 0); L.paste(sea, 0, stage.HORIZON); L.paste(far, 0, stage.FAR_TOP)
L.paste(S['play'], 0, 0)
for im, sx, fy_, fx_, fy in sorted(SS.dressing(), key=lambda s_: s_[2]):
    L.paste(from_image(im), int(sx - fx_), int(fy_ - fy))
base = L.image().convert('RGB')


def crop(x0, x1, y0, y1, zoom, path, lines=()):
    im = base.crop((x0, y0, x1, y1)).resize(((x1 - x0) * zoom, (y1 - y0) * zoom), Image.NEAREST)
    d = ImageDraw.Draw(im)
    for y in range((y0 // 10) * 10, y1, 10):
        if y < y0:
            continue
        d.line([(0, (y - y0) * zoom), (im.width, (y - y0) * zoom)], fill=(255, 255, 255) if y % 50 == 0 else (255, 255, 255, 90), width=1)
        d.text((2, (y - y0) * zoom + 1), str(y), fill=(255, 255, 0))
    for x in range((x0 // 20) * 20, x1, 20):
        if x < x0:
            continue
        d.line([((x - x0) * zoom, 0), ((x - x0) * zoom, im.height)], fill=(255, 255, 255), width=1)
        d.text(((x - x0) * zoom + 2, 12), str(x), fill=(0, 255, 255))
    for (ax, ay, bx, by, col) in lines:
        d.line([((ax - x0) * zoom, (ay - y0) * zoom), ((bx - x0) * zoom, (by - y0) * zoom)], fill=col, width=2)
    im.save(path)
    print(path, im.size)


if __name__ == '__main__':
    out = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/tools/'
    crop(650, 950, 80, 200, 5, out + 'g_wreck.png')
    crop(930, 1250, 60, 200, 5, out + 'g_boxes.png')
    crop(1220, 1500, 100, 200, 5, out + 'g_white.png')
