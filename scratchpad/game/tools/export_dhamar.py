# export_dhamar.py - Dhamar's stage, written out for the game (11 Nov, zones 1-3 as one test build): the sky, the far
# ranges and cones and the plain (which wrap), the play picture cut into strips (no strip wider than 2,200 px), the
# foreground, and gen/stage_dhamar.json saying where each goes, where the floor is (flat: the highway, the town's
# paving, the springs' road) and where the tops of things are as painted (unit_dhamar.js checks the level against them).
#   python3 export_dhamar.py [--look]   (--look: also a small overview picture, art/out/dhamar_look.png)
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock'
sys.path.insert(0, MOCK)
import stage_dhamar as D          # noqa: E402

OUT = os.path.join(HERE, '..', 'art', 'out')
GEN = os.path.join(HERE, '..', 'gen')
pics = {}


def save(name, L, crop_top=0):
    im = L.image()
    if crop_top:
        im = im.crop((0, crop_top, im.width, im.height))
    im.save(os.path.join(OUT, name + '.png'), optimize=True)
    pics[name] = im.size
    return im.size


def first_row(L):
    rows = L.a.any(axis=1)
    return int(rows.argmax()) if rows.any() else 0


B = D.backgrounds()
P = D.play()
FG = D.fore()
CUTS = [0, 2070, 4140, D.Z2X, 7400, D.Z3X, 9600, D.END]        # (the strips: the plain in three, the town in two, the springs in two)
play = []
names = []
for k, (a, b) in enumerate(zip(CUTS[:-1], CUTS[1:])):
    name = 'd_p%d' % (k + 1)
    w, h = save(name, P.crop(a, 0, b, D.SH))
    play.append(dict(img=name, x=a, w=w, y=0, h=h))
    names.append(name)
save('d_sky', B['sky'])
save('d_far', B['far'])
save('d_mid', B['mid'])
ft = max(0, first_row(FG) - 1)
fore = []
fcuts = list(range(0, FG.w, 2400)) + [FG.w]
for k, (fa, fb) in enumerate(zip(fcuts[:-1], fcuts[1:])):
    fw, fh = save('d_f%d' % (k + 1), FG.crop(fa, 0, fb, D.SH), ft)
    fore.append(dict(img='d_f%d' % (k + 1), x=fa, w=fw, y=ft, h=fh))
layers = {
    'sky': dict(img='d_sky', w=pics['d_sky'][0], h=pics['d_sky'][1], y=0, par=0.15, wrap=True),
    'far': dict(img='d_far', w=pics['d_far'][0], h=pics['d_far'][1], y=B['far_y'], par=0.3, wrap=True),
    'mid': dict(img='d_mid', w=pics['d_mid'][0], h=pics['d_mid'][1], y=B['mid_y'], par=0.55, wrap=True),
    'play': dict(par=1.0, strips=play),
    'fore': dict(par=1.25, strips=fore),
}
world = dict(Z1=0, Z2=D.Z2X, Z3=D.Z3X, END=D.END, ROAD_Y=D.WALK, VERGE=D.VERGE, ROAD_TOP=D.ROAD_TOP, BASE=D.BASE)
ground = dict(step=4, y=[D.WALK for x in range(0, D.END + 1, 4)])
out = dict(layers=layers, world=world, fixed={}, ground=ground, plats=D.PLATS, info=D.INFO,
           pictures=names + ['d_sky', 'd_far', 'd_mid'] + [f['img'] for f in fore])
json.dump(out, open(os.path.join(GEN, 'stage_dhamar.json'), 'w'), separators=(',', ':'), default=int)
print('wrote', len(out['pictures']), 'pictures;', len(D.PLATS), 'platforms')
if '--look' in sys.argv:
    # an overview: each strip at half size, stacked, with the sky and the far layers behind, for a look at the whole
    from PIL import Image
    rows = []
    sky, far, mid = B['sky'].image(), B['far'].image(), B['mid'].image()
    for a in range(0, D.END, 1400):
        b = min(D.END, a + 1400)
        bg = Image.new('RGBA', (b - a, D.SH), (0, 0, 0, 255))
        for x in range(0, b - a, sky.width):
            bg.alpha_composite(sky, (x, 0))
        for x in range(-((a * 3 // 10) % far.width), b - a, far.width):
            bg.alpha_composite(far, (x, B['far_y']))
        for x in range(-((a * 55 // 100) % mid.width), b - a, mid.width):
            bg.alpha_composite(mid, (x, B['mid_y']))
        bg.alpha_composite(P.crop(a, 0, b, D.SH).image(), (0, 0))
        rows.append(bg)
    W_ = 1400
    look = Image.new('RGBA', (W_, D.SH * len(rows)), (0, 0, 0, 255))
    for k, rw in enumerate(rows):
        look.paste(rw, (0, k * D.SH))
    look.save(os.path.join(OUT, 'dhamar_look.png'))
    print('look:', look.size)
