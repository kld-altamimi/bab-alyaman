# export_zabid.py - The Souq's stage, written out for the game: the long picture cut into four strips (the town gate,
# the spice stalls, the rooftops, the covered market), the sky, Zabid far off and the plain (which wrap; the plain
# goes where the sea goes elsewhere), the foreground, and gen/stage_zabid.json saying where each goes, the ground as
# painted (the rooftops' heights and gaps), and where the tops of things are (unit8.js checks the level against it).
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock'
sys.path.insert(0, MOCK)
import stage_zabid as Z          # noqa: E402
import stage as ST               # noqa: E402

OUT = os.path.join(HERE, '..', 'art', 'out')
GEN = os.path.join(HERE, '..', 'gen')
S = Z.build()
pics = {}


def save(name, L, crop_top=0):
    im = L.image()
    if crop_top:
        im = im.crop((0, crop_top, im.width, im.height))
    im.save(os.path.join(OUT, name + '.png'), optimize=True)
    pics[name] = im.size
    return im.size


cuts = [('z_gate', Z.TG, Z.SS), ('z_stalls', Z.SS, Z.RT), ('z_roofs', Z.RT, Z.CM), ('z_hall', Z.CM, Z.WORLD)]
play = []
for name, a, b in cuts:
    w, h = save(name, S['play'].crop(a, 0, b, Z.SH))
    play.append(dict(img=name, x=a, w=w, y=0, h=h))
save('z_sky', S['sky'])
save('z_far', S['far'])
save('z_plain', S['sea'])
# the foreground: the road's, one length of the market's repeated, the roofs', one length of the hall's repeated
w1, h1 = save('zf_road', S['fore_road'])
w2, h2 = save('zf_mkt', S['fore_market'])
w3, h3 = save('zf_roofs', S['fore_roofs'])
w4, h4 = save('zf_hall', S['fore_hall'])
fore = [dict(img='zf_road', x=0, w=w1, y=0, h=h1), dict(img='zf_mkt', x=Z.F1, w=w2, y=0, h=h2, until=Z.F2),
        dict(img='zf_roofs', x=Z.F2, w=w3, y=0, h=h3), dict(img='zf_hall', x=Z.F3, w=w4, y=0, h=h4, until=Z.F4)]
layers = {
    'sky': dict(img='z_sky', w=pics['z_sky'][0], h=pics['z_sky'][1], y=0, par=0.2, wrap=True),
    'far': dict(img='z_far', w=pics['z_far'][0], h=pics['z_far'][1], y=ST.FAR_TOP, par=0.35, wrap=True),
    'sea': dict(img='z_plain', w=pics['z_plain'][0], h=pics['z_plain'][1], y=ST.HORIZON, par=0.6, wrap=True),
    'play': dict(par=1.0, strips=play),
    'fore': dict(par=1.25, strips=fore),
}
world = dict(TG=Z.TG, SS=Z.SS, RT=Z.RT, CM=Z.CM, WORLD=Z.WORLD, ROAD_Y=Z.WALK, doors=Z.INFO.get('doors', []), pits=Z.PITS,
             roofs=[list(r) for r in Z.ROOFS], bars=Z.INFO.get('bars', {}), piers=Z.INFO.get('piers', []))
out = dict(layers=layers, world=world, fixed={}, ground=dict(step=4, y=Z.GS), plats=Z.PLATS, info=Z.INFO,
           pictures=[n for n, _, _ in cuts] + ['z_sky', 'z_far', 'z_plain', 'zf_road', 'zf_mkt', 'zf_roofs', 'zf_hall'])
json.dump(out, open(os.path.join(GEN, 'stage_zabid.json'), 'w'), separators=(',', ':'))
tot = 0
for n in out['pictures']:
    kb = os.path.getsize(os.path.join(OUT, n + '.png')) / 1024.0
    tot += kb
    print('  %-9s %5d x %3d  %6.1f KB' % (n, pics[n][0], pics[n][1], kb))
print('Zabid stage: %d pictures, %.0f KB; platforms %s' % (len(out['pictures']), tot, ', '.join(sorted(Z.PLATS))))
