# export_ibb.py - Ibb's stage, written out for the game as its zones are painted (Khaled, 24 Oct: he plays them one by
# one): the sky, the far mountains and the nearer terraced hills (which wrap; the hills are a fourth layer, `mid`, drawn
# after the far one), each painted zone's long picture as a strip of its own, the foreground, and gen/stage_ibb.json
# saying where each goes, where the floor is and where the tops of things are as painted (unit_ibb.js checks the level
# against them).
#   python3 export_ibb.py
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock'
sys.path.insert(0, MOCK)
import stage_ibb as I              # noqa: E402
import stage_ibb_z1 as Z1          # noqa: E402

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
    """The first row with anything painted on it (the foreground is mostly clear above its grass and stones)."""
    rows = L.a.any(axis=1)
    return int(rows.argmax()) if rows.any() else 0


B = I.backgrounds()
z1 = Z1.play_z1()                  # (fills I.PLATS and I.INFO)
f1 = Z1.fore_z1()
zones = [('i_z1', 0, Z1.W1, z1)]
play = []
for name, a, b, L in zones:
    w, h = save(name, L)
    play.append(dict(img=name, x=a, w=w, y=0, h=h))
save('i_sky', B['sky'])
save('i_far', B['far'])
save('i_mid', B['mid'])
ft = max(0, first_row(f1) - 1)
fw, fh = save('if_z1', f1, ft)
fore = [dict(img='if_z1', x=0, w=fw, y=ft, h=fh)]
layers = {
    'sky': dict(img='i_sky', w=pics['i_sky'][0], h=pics['i_sky'][1], y=0, par=0.15, wrap=True),
    'far': dict(img='i_far', w=pics['i_far'][0], h=pics['i_far'][1], y=B['far_y'], par=0.3, wrap=True),
    'mid': dict(img='i_mid', w=pics['i_mid'][0], h=pics['i_mid'][1], y=B['mid_y'], par=0.55, wrap=True),
    'play': dict(par=1.0, strips=play),
    'fore': dict(par=1.25, strips=fore),
}
END = zones[-1][2]
world = dict(Z1=0, END=END, ROAD_Y=I.WALK, VERGE=Z1.VERGE, ROAD_TOP=Z1.ROAD_TOP)
out = dict(layers=layers, world=world, fixed={}, ground=dict(step=4, y=[I.WALK]), plats=I.PLATS, info=I.INFO,
           pictures=[z[0] for z in zones] + ['i_sky', 'i_far', 'i_mid', 'if_z1'])
json.dump(out, open(os.path.join(GEN, 'stage_ibb.json'), 'w'), separators=(',', ':'), default=int)
tot = 0
for n in out['pictures']:
    kb = os.path.getsize(os.path.join(OUT, n + '.png')) / 1024.0
    tot += kb
    print('  %-8s %5d x %3d  %6.1f KB' % (n, pics[n][0], pics[n][1], kb))
print('Ibb stage: %d pictures, %.0f KB; zones painted: %d (to x %d); platforms %s' % (len(out['pictures']), tot, len(zones), END, ', '.join(sorted(I.PLATS))))
