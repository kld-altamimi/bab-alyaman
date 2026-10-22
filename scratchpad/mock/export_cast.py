# export_cast.py - model sheets of the cast: fixed cells so labels can sit under each figure.
import os
import ms3 as cast
from px import *

os.makedirs('out', exist_ok=True)
fn = dict(cast.CAST)


def sheet(names, cell_w, cell_h, zoom, out, flip=(), base=None):
    base = base or cell_h - 3
    im = new(cell_w * len(names), cell_h)
    for i, n in enumerate(names):
        f = fn[n]
        spr, fx, fy = f(flip=True) if n in flip else f()
        x = i * cell_w + (cell_w - spr.width) // 2
        blit(im, spr, x, base - fy)
    im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
    im.save(out)
    return im.size


def silhouettes(names, cell_w, cell_h, zoom, out):
    im = new(cell_w * len(names), cell_h)
    for i, n in enumerate(names):
        spr, fx, fy = fn[n]()
        sil = silhouette(spr, (36, 30, 26, 255))
        blit(im, sil, i * cell_w + (cell_w - spr.width) // 2, cell_h - 3 - fy)
    im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
    im.save(out)
    return im.size


if __name__ == '__main__':
    print(sheet(['yazeed', 'salem', 'bilqis', 'arwa'], 57, 45, 8, 'out/cast_squad.png'))
    mil = ['grunt', 'rocketeer', 'doorman', 'bomber', 'cook', 'surrender', 'guard']
    print(sheet(mil, 52, 50, 5, 'out/cast_militia.png', flip=set(mil)))
    print(sheet(['marshal', 'detainee', 'detainee_freed', 'yazeed_run', 'yazeed_crouch'], 58, 58, 5, 'out/cast_more.png',
                flip={'marshal'}))
    print(silhouettes(['yazeed', 'salem', 'bilqis', 'arwa', 'grunt', 'cook', 'guard', 'marshal', 'detainee_freed'],
                      52, 58, 3, 'out/cast_builds.png'))
