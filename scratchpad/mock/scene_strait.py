# scene_strait.py - the Bab al-Mandab stage: layer sheet, stage strip and one screen of play.
import sys
import numpy as np
import stage
import props as P
import ms3 as cast
import hud2
from paint import Layer, from_image, Image
from px import blit, new, save, hexc
from fx import fx, gtext, RED, LAV, ORG
from px import FONT_B, FONT_M, FONT_S

S = stage.build_layers()
info = S['info']
walk = info['walk']
dx0, dx1, deck = info['deck']


def deck_y(x):
    return float(deck[int(x - 668)])


def spr(fn, x, y=None, flip=False, **kw):
    im, fx_, fy_ = fn(flip=flip, **kw) if kw or flip else fn()
    return (im, x, (walk[int(x)] if y is None else y), fx_, fy_)


def prop(piece, x, y, floor):
    """A painted or outlined piece used as a sprite: stands with its floor row at y."""
    im = piece.image()
    return (im, x, y, 0, floor)


def play_screen(cam=590, out='t3_play.png'):
    sprites = []
    top = info['wreck_top']
    # the hero, mid-burst
    sprites.append(spr(cast.yazeed, cam + 104))
    # a man with a door, taking the fire
    sprites.append(spr(cast.doorman, cam + 204, flip=True))
    # on the wreck: an elder roped up on the deckhouse, a bomber winding up, a rifleman in the bow
    sprites.append(spr(cast.detainee, 668 + 34, top + 33))
    sprites.append(spr(cast.bomber, 668 + 82, deck_y(668 + 82), flip=True))
    sprites.append(spr(cast.grunt, 668 + 150, deck_y(668 + 150), flip=True, face='qat'))
    # the post beyond the bow: cover, a man who has had enough, and the drum that persuaded him
    sb, f = P.sandbags(5, 4, seed=2)
    sprites.append(prop(P.outlined(sb), cam + 290, walk[cam + 320] + 3, f + 2))
    sprites.append(spr(cast.surrender, cam + 328, walk[cam + 328] - 3, flip=True))
    cr, f = P.crate(seed=2)
    sprites.append(prop(cr, cam + 246, walk[cam + 250] + 6, f))
    sprites.sort(key=lambda s: s[2])
    scr = stage.compose(cam, S, sprites=sprites, fore=True).image()

    ex, f = P.explosion(19, seed=4)
    blit(scr, ex.image(), 378 - ex.w // 2, int(walk[cam + 378]) + 2 - f)
    # gunfire
    gy = int(walk[cam + 104]) - 20
    blit(scr, fx('muzzle'), 104 + 28, gy - 4)
    for i, tx in enumerate((148, 163)):
        blit(scr, fx('tracer'), tx, gy - 1 + (i % 2))
    blit(scr, fx('spark'), 177, gy - 4)
    blit(scr, fx('spark2'), 180, gy + 3)
    blit(scr, fx('casing'), 112, gy - 8)
    blit(scr, fx('casing'), 107, gy - 13)
    blit(scr, fx('puff'), 198, int(walk[cam + 204]) - 3)
    # fire from the bow
    by = int(deck_y(668 + 150)) - 20
    bx = 668 + 150 - cam
    blit(scr, fx('muzzle_s', flip=True), bx - 35, by - 2)
    blit(scr, fx('tracer_e'), bx - 54, by + 3)
    blit(scr, fx('tracer_e'), bx - 84, by + 11)
    blit(scr, fx('puff'), 126, int(walk[cam + 130]) - 2)
    # the stick already in the air
    blit(scr, fx('stick'), 150, 98)
    blit(scr, fx('smoke'), 160, 92)
    blit(scr, fx('smoke'), 168, 88)

    hud2.hud(scr)
    hud2.go_sign(scr, 420, 58)
    clean = scr.copy()
    for im_ in (scr, clean):
        hud2.subtitle(im_, 'YAZEED', "Mind the boat. Somebody's grandfather built it.", y=203)
    hud2.touch(scr)
    scr.resize((scr.width * 3, scr.height * 3), Image.NEAREST).save(out)
    clean.resize((clean.width * 3, clean.height * 3), Image.NEAREST).save(out.replace('.png', '_clean.png'))
    return scr


def dressing():
    """Sprites that belong to the stage itself: cover, drums, crates, the battery's piece."""
    out = []
    sb, f = P.sandbags(5, 4, seed=2)
    out.append(prop(P.outlined(sb), 880, walk[905] + 3, f + 2))
    sb2, f2 = P.sandbags(5, 4, seed=5)
    out.append(prop(P.outlined(sb2), 1556, walk[1580] + 3, f2 + 2))
    sb3, f3 = P.sandbags(4, 3, seed=6)
    out.append(prop(P.outlined(sb3), 1700, walk[1720] + 3, f3 + 2))
    ml, f = P.missile_launcher()
    out.append(prop(ml, 1606, walk[1650] + 1, f))
    for i, (x, pnt) in enumerate(((1532, 'oxide'), (1546, 'green'), (1340, 'blue'), (962, 'oxide'))):
        dr, f = P.drum(pnt, seed=i)
        out.append(prop(dr, x, walk[x] + 2, f))
    cr, f = P.crate(seed=2)
    out.append(prop(cr, 836, walk[840] + 6, f))
    return out


def cast_on_stage():
    """Who is where, for the strip: one hero at the landing, the opposition by section."""
    top = info['wreck_top']
    out = [spr(cast.yazeed, 196), spr(cast.detainee, 668 + 34, top + 33),
           spr(cast.bomber, 668 + 82, deck_y(668 + 82), flip=True),
           spr(cast.grunt, 668 + 150, deck_y(668 + 150), flip=True, face='qat'),
           spr(cast.doorman, 794, flip=True), spr(cast.surrender, 918, walk[918] - 3, flip=True),
           spr(cast.grunt, 1010, 134, flip=True, face='angry'),          # on the ochre box
           spr(cast.rocketeer, 1150, 108, flip=True),                    # on the green box
           spr(cast.cook, 1412, flip=True), spr(cast.detainee, 1300, walk[1300] - 2),
           spr(cast.grunt, 1594, walk[1594] - 3, flip=True), spr(cast.guard, 1690, flip=True),
           spr(cast.grunt, 1786, 122, flip=True, face='youth')]          # the lookout
    return out


def wide_layers():
    """The same stage flattened into one strip: far layers drawn at full width, no sliding."""
    big = [(96, 88, 150, 64, 170, 4.0, 11.0), (300, 93, 110, 34, 90, 3.5, 8.0), (470, 90, 180, 54, 170, 4.0, 10.0),
           (668, 93, 120, 30, 90, 3.5, 8.0), (900, 89, 170, 58, 170, 4.0, 11.0), (1110, 93, 120, 32, 90, 3.5, 8.0),
           (1330, 90, 190, 50, 170, 4.0, 10.0), (1560, 93, 120, 30, 90, 3.5, 8.0), (1770, 88, 160, 60, 170, 4.0, 11.0)]
    sky = stage.sky_layer(w=stage.STAGE_W, big=big)
    far = stage.far_layer(w=stage.STAGE_W, k=1.75)
    sea = stage.sea_layer(w=stage.STAGE_W)
    return sky, far, sea


def strip(out='out/strip.png', people=True, zoom=2):
    sky, far, sea = wide_layers()
    L = Layer(stage.STAGE_W, stage.SH)
    L.paste(sky, 0, 0)
    L.paste(sea, 0, stage.HORIZON)
    L.paste(far, 0, stage.FAR_TOP)
    L.paste(S['play'], 0, 0)
    sprites = dressing() + (cast_on_stage() if people else [])
    sprites.sort(key=lambda s_: s_[2])
    for im, sx, fy_, fx_, fy in sprites:
        L.paste(from_image(im), int(sx - fx_), int(fy_ - fy))
    fore = S['fore']
    L.paste(fore.crop(0, 0, stage.STAGE_W, stage.SH), 0, 0)
    im = L.image()
    im.resize((im.width * zoom, im.height * zoom), Image.NEAREST).save(out)
    return im


def layer_files(zoom=1):
    """Each layer on its own, as the engine holds them."""
    import os
    os.makedirs('out', exist_ok=True)
    sizes = {}
    for name in ('sky', 'far', 'sea', 'play', 'fore'):
        L = S[name]
        if name == 'fore':
            L = L.crop(0, 150, L.w, L.h)
        if name == 'play':
            # show the ground and its set pieces with the stage dressing in place
            L2 = Layer(L.w, L.h)
            L2.paste(L)
            for im, sx, fy_, fx_, fy in sorted(dressing(), key=lambda s_: s_[2]):
                L2.paste(from_image(im), int(sx - fx_), int(fy_ - fy))
            L = L2.crop(0, 30, L2.w, L2.h)
        im = L.image()
        if zoom != 1:
            im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
        im.save('out/layer_%s.png' % name)
        sizes[name] = im.size
    return sizes


if __name__ == '__main__':
    import os
    os.makedirs('out', exist_ok=True)
    play_screen(out='out/play.png')
    strip()
    print(layer_files())
    print('ok')
