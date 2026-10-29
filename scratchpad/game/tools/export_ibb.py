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
import stage_ibb_z4 as Z4          # noqa: E402

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
# (29 Oct: the zones are painted as one picture, stage_ibb_world.py, and cut at their starts: a join is a cut through one
# painting; the mountainside behind and the foreground likewise)
import stage_ibb_world as WD   # noqa: E402
P = WD.play()                      # (fills I.PLATS and I.INFO for all four zones)
BK = WD.back()
FG = WD.fore()
zones = [('i_z1', 0, Z1.W1), ('i_z2', Z2.X0, Z2.END2), ('i_z3', Z3.X0, Z3.END3), ('i_z4', Z4.X0, Z4.END4)]
play = []
for name, a, b in zones:
    w, h = save(name, P.crop(a, 0, b, I.SH))
    play.append(dict(img=name, x=a, w=w, y=0, h=h))
save('i_sky', B['sky'])
save('i_far', B['far'])
save('i_mid', B['mid'])
ft = max(0, first_row(FG) - 1)
fore = []
cuts = [0, int(Z2.X0 * 1.25), int(Z3.X0 * 1.25), int(Z4.X0 * 1.25), FG.w]
for k, (fa, fb) in enumerate(zip(cuts[:-1], cuts[1:])):
    fw, fh = save('if_z%d' % (k + 1), FG.crop(fa, 0, fb, I.SH), ft)
    fore.append(dict(img='if_z%d' % (k + 1), x=fa, w=fw, y=ft, h=fh))
bw, bh = save('i_back2', BK.crop(0, 0, Z2.BACK_W, I.SH))
W3B = 1410                         # (the terraces' mountainside in the back layer; then the pass's cloud)
bw3, bh3 = save('i_back3', BK.crop(Z2.BACK_W, 0, Z2.BACK_W + W3B, I.SH))
bw4, bh4 = save('i_back4', BK.crop(Z2.BACK_W + W3B, 0, BK.w, I.SH))
back = [dict(img='i_back2', x=Z2.BACK_X, w=bw, y=0, h=bh), dict(img='i_back3', x=Z2.BACK_X + Z2.BACK_W, w=bw3, y=0, h=bh3),
        dict(img='i_back4', x=Z2.BACK_X + Z2.BACK_W + W3B, w=bw4, y=0, h=bh4)]
layers = {
    'sky': dict(img='i_sky', w=pics['i_sky'][0], h=pics['i_sky'][1], y=0, par=0.15, wrap=True),
    'far': dict(img='i_far', w=pics['i_far'][0], h=pics['i_far'][1], y=B['far_y'], par=0.3, wrap=True),
    'mid': dict(img='i_mid', w=pics['i_mid'][0], h=pics['i_mid'][1], y=B['mid_y'], par=0.55, wrap=True),
    'back': dict(par=0.7, strips=back),
    'play': dict(par=1.0, strips=play),
    'fore': dict(par=1.25, strips=fore),
}
END = zones[-1][2]
world = dict(Z1=0, Z2=Z2.X0, Z3=Z3.X0, Z4=Z4.X0, END=END, ROAD_Y=I.WALK, VERGE=Z1.VERGE, ROAD_TOP=Z1.ROAD_TOP)
# the ground: flat at the road's walk line through zones 1 and 2, then the terraces a step at a time (each step a wall
# to hop up: the level has walls: true); every 4 px, the steps on the samples
ground = dict(step=4, y=[Z3.ground_world(x) for x in range(0, END + 1, 4)])
out = dict(layers=layers, world=world, fixed={}, ground=ground, plats=I.PLATS, info=I.INFO,
           pictures=[z[0] for z in zones] + ['i_sky', 'i_far', 'i_mid', 'i_back2', 'i_back3', 'i_back4'] + ['if_z%d' % (k + 1) for k in range(len(fore))])
json.dump(out, open(os.path.join(GEN, 'stage_ibb.json'), 'w'), separators=(',', ':'), default=int)
tot = 0
for n in out['pictures']:
    kb = os.path.getsize(os.path.join(OUT, n + '.png')) / 1024.0
    tot += kb
    print('  %-8s %5d x %3d  %6.1f KB' % (n, pics[n][0], pics[n][1], kb))
print('Ibb stage: %d pictures, %.0f KB; zones painted: %d (to x %d); platforms %s' % (len(out['pictures']), tot, len(zones), END, ', '.join(sorted(I.PLATS))))
