# export_mocha.py - The Coffee Port's stage, written out for the game: the long picture cut into four strips, the sky,
# the town across the harbour and the water (which wrap), the foreground, and gen/stage_mocha.json saying where each
# goes, where the floor is and where the tops of things are as painted (unit6.js checks the level against them).
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock'
sys.path.insert(0, MOCK)
import stage_mocha as M          # noqa: E402
import stage as ST               # noqa: E402

OUT = os.path.join(HERE, '..', 'art', 'out')
GEN = os.path.join(HERE, '..', 'gen')
S = M.build()
pics = {}


def save(name, L, crop_top=0):
    im = L.image()
    if crop_top:
        im = im.crop((0, crop_top, im.width, im.height))
    im.save(os.path.join(OUT, name + '.png'), optimize=True)
    pics[name] = im.size
    return im.size


# the ground and everything on it, in four strips
cuts = [('m_quay', M.Q, M.WH), ('m_ware', M.WH, M.RH), ('m_roast', M.RH, M.PT), ('m_point', M.PT, M.WORLD)]
play = []
for name, a, b in cuts:
    w, h = save(name, S['play'].crop(a, 0, b, M.SH))
    play.append(dict(img=name, x=a, w=w, y=0, h=h))
# what wraps
save('m_sky', S['sky'])
save('m_far', S['far'])
save('m_sea', S['sea'])
# the foreground: the quay's (only its foot), one length of the inside repeated, the point's (its lower part)
fq_top, fp_top = 150, 112
w1, h1 = save('mf_quay', S['fore_quay'], fq_top)
w2, h2 = save('mf_in', S['fore_inside'])
w3, h3 = save('mf_pt', S['fore_point'], fp_top)
fore = [dict(img='mf_quay', x=0, w=w1, y=fq_top, h=h1), dict(img='mf_in', x=M.FI0, w=w2, y=0, h=h2, until=M.FI1),
        dict(img='mf_pt', x=M.FI1, w=w3, y=fp_top, h=h3)]
layers = {
    'sky': dict(img='m_sky', w=pics['m_sky'][0], h=pics['m_sky'][1], y=0, par=0.2, wrap=True),
    'far': dict(img='m_far', w=pics['m_far'][0], h=pics['m_far'][1], y=ST.FAR_TOP, par=0.35, wrap=True),
    'sea': dict(img='m_sea', w=pics['m_sea'][0], h=pics['m_sea'][1], y=ST.HORIZON, par=0.6, wrap=True),
    'play': dict(par=1.0, strips=play),
    'fore': dict(par=1.25, strips=fore),
}
world = dict(Q=M.Q, WH=M.WH, RH=M.RH, PT=M.PT, WORLD=M.WORLD, ROAD_Y=M.WALK, doors=M.INFO.get('doors', []), lighthouse=M.INFO.get('lighthouse'))
out = dict(layers=layers, world=world, fixed={}, ground=dict(step=4, y=[M.WALK]), plats=M.PLATS, info=M.INFO,
           pictures=[n for n, _, _ in cuts] + ['m_sky', 'm_far', 'm_sea', 'mf_quay', 'mf_in', 'mf_pt'])
json.dump(out, open(os.path.join(GEN, 'stage_mocha.json'), 'w'), separators=(',', ':'))
tot = 0
for n in out['pictures']:
    kb = os.path.getsize(os.path.join(OUT, n + '.png')) / 1024.0
    tot += kb
    print('  %-8s %5d x %3d  %6.1f KB' % (n, pics[n][0], pics[n][1], kb))
print('Mocha stage: %d pictures, %.0f KB; platforms %s' % (len(out['pictures']), tot, ', '.join(sorted(M.PLATS))))
