# export_ibb.py - Ibb's stage, written out for the game as its zones are painted (Khaled, 24 Oct: he plays them one by
# one): the sky, the far mountains and the nearer terraced hills (which wrap; the hills are a fourth layer, `mid`, drawn
# after the far one), each painted zone's long picture as a strip of its own, the mountainside behind Jibla and the
# terraces (`back`, at 0.7), the foreground, and gen/stage_ibb.json saying where each goes, where the floor is (flat
# until the terraces climb), and where the tops of things are as painted (unit_ibb.js checks the level against them).
#   python3 export_ibb.py
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock'
sys.path.insert(0, MOCK)
import stage_ibb as I              # noqa: E402
import stage_ibb_z1 as Z1          # noqa: E402
import stage_ibb_z2 as Z2          # noqa: E402
import stage_ibb_z3 as Z3          # noqa: E402

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
z2 = Z2.play_z2()                  # (adds zone 2's platforms, and I.INFO['z2'])
f2 = Z2.fore_z2()
b2 = Z2.back_town()
z3 = Z3.play_z3()                  # (zone 3's platforms, and I.INFO['z3'])
f3 = Z3.fore_z3()
b3 = Z3.back_falls()
zones = [('i_z1', 0, Z1.W1, z1), ('i_z2', Z2.X0, Z2.END2, z2), ('i_z3', Z3.X0, Z3.END3, z3)]
play = []
for name, a, b, L in zones:
    w, h = save(name, L)
    play.append(dict(img=name, x=a, w=w, y=0, h=h))
save('i_sky', B['sky'])
save('i_far', B['far'])
save('i_mid', B['mid'])
ft = max(0, first_row(f1) - 1)
fw, fh = save('if_z1', f1, ft)
ft2 = max(0, first_row(f2) - 1)
fw2, fh2 = save('if_z2', f2, ft2)
ft3 = max(0, first_row(f3) - 1)
fw3, fh3 = save('if_z3', f3, ft3)
fore = [dict(img='if_z1', x=0, w=fw, y=ft, h=fh), dict(img='if_z2', x=int(Z2.X0 * 1.25), w=fw2, y=ft2, h=fh2),
        dict(img='if_z3', x=int(Z3.X0 * 1.25), w=fw3, y=ft3, h=fh3)]
bw, bh = save('i_back2', b2)
bw3, bh3 = save('i_back3', b3)
back = [dict(img='i_back2', x=Z2.BACK_X, w=bw, y=0, h=bh), dict(img='i_back3', x=Z3.BACK_X, w=bw3, y=0, h=bh3)]
layers = {
    'sky': dict(img='i_sky', w=pics['i_sky'][0], h=pics['i_sky'][1], y=0, par=0.15, wrap=True),
    'far': dict(img='i_far', w=pics['i_far'][0], h=pics['i_far'][1], y=B['far_y'], par=0.3, wrap=True),
    'mid': dict(img='i_mid', w=pics['i_mid'][0], h=pics['i_mid'][1], y=B['mid_y'], par=0.55, wrap=True),
    'back': dict(par=0.7, strips=back),
    'play': dict(par=1.0, strips=play),
    'fore': dict(par=1.25, strips=fore),
}
END = zones[-1][2]
world = dict(Z1=0, Z2=Z2.X0, Z3=Z3.X0, END=END, ROAD_Y=I.WALK, VERGE=Z1.VERGE, ROAD_TOP=Z1.ROAD_TOP)
# the ground: flat at the road's walk line through zones 1 and 2, then the terraces a step at a time (each step a wall
# to hop up: the level has walls: true); every 4 px, the steps on the samples
ground = dict(step=4, y=[Z3.ground_world(x) for x in range(0, END + 1, 4)])
out = dict(layers=layers, world=world, fixed={}, ground=ground, plats=I.PLATS, info=I.INFO,
           pictures=[z[0] for z in zones] + ['i_sky', 'i_far', 'i_mid', 'i_back2', 'i_back3', 'if_z1', 'if_z2', 'if_z3'])
json.dump(out, open(os.path.join(GEN, 'stage_ibb.json'), 'w'), separators=(',', ':'), default=int)
tot = 0
for n in out['pictures']:
    kb = os.path.getsize(os.path.join(OUT, n + '.png')) / 1024.0
    tot += kb
    print('  %-8s %5d x %3d  %6.1f KB' % (n, pics[n][0], pics[n][1], kb))
print('Ibb stage: %d pictures, %.0f KB; zones painted: %d (to x %d); platforms %s' % (len(out['pictures']), tot, len(zones), END, ', '.join(sorted(I.PLATS))))
