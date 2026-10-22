# export_art.py - everything the prototype draws, written out as one sprite sheet, five stage layers and the lettering.
import sys, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock'
sys.path.insert(0, MOCK)
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image
import stage
import props as P
from paint import Layer, from_image

OUT = os.path.join(HERE, '..', 'art', 'out')
GEN = os.path.join(HERE, '..', 'gen')
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- the stage, with the mine lifted out to be a thing of its own
CAP = {}
_put = stage.put


def put(play, piece, x, base_y, floor, shadow=True, bury=0, seed=1, reach=0.5):
    if int(x) == 430 and base_y == 172:
        pc = P.sink(piece, piece.h - floor + bury, seed=seed) if bury else piece
        CAP['mine'] = (pc.image(), int(x), int(base_y - floor))
        m = P.cast_shadow(pc, min(floor - bury, pc.h - 1), reach=reach)
        stage._shadow_on(play, m, int(x), int(base_y - floor), -3)
        return
    return _put(play, piece, x, base_y, floor, shadow=shadow, bury=bury, seed=seed, reach=reach)


stage.put = put
S = stage.build_layers()
import scene_strait as SS          # noqa: E402  (it builds on the layers above)
import sprites as SP               # noqa: E402
import ms3                         # noqa: E402
import hud2                        # noqa: E402
import fx as FXM                   # noqa: E402
import px                          # noqa: E402
from px import new, blit, sprite, outline, silhouette, rgba   # noqa: E402

walk = S['info']['walk']
frames = {}          # name -> dict(im, ax, ay[, mx, my])
points = {}


def add(name, f):
    frames[name] = f
    if 'mx' in f:
        points[name] = [f['mx'] - f['ax'], f['ay'] - f['my']]      # forward of the feet, above the feet


def img(name, im, ax=None, ay=None):
    frames[name] = dict(im=im, ax=im.width // 2 if ax is None else ax, ay=im.height - 1 if ay is None else ay)


# ---------------------------------------------------------------- Yazeed
for legs in ('stand', 'pass', 'run', 'jump', 'fall', 'crouch'):
    for gun in ('side', 'hmg'):
        add('yazeed_%s_%s_fwd' % (legs, gun), SP.build(*SP.yazeed(legs, gun, 'fwd')))
        add('yazeed_%s_%s_throw' % (legs, gun), SP.build(*SP.yazeed(legs, gun, 'fwd', throw=True)))
        if legs != 'crouch':
            add('yazeed_%s_%s_up' % (legs, gun), SP.build(*SP.yazeed(legs, gun, 'up')))
            add('yazeed_%s_%s_diag' % (legs, gun), SP.build(*SP.yazeed(legs, gun, 'diag')))
        if legs in ('jump', 'fall'):
            add('yazeed_%s_%s_down' % (legs, gun), SP.build(*SP.yazeed(legs, gun, 'down')))
            add('yazeed_%s_%s_ddiag' % (legs, gun), SP.build(*SP.yazeed(legs, gun, 'ddiag')))
    for st_ in (1, 2):
        add('yazeed_%s_knife%d' % (legs, st_), SP.build(*SP.yazeed_knife(legs, st_)))

# ---------------------------------------------------------------- the Scorpion's men
LOOKS = {'worried': 'skin2', 'youth': 'skin1', 'angry': 'skin3', 'qat': 'skin2'}
for look, skin in LOOKS.items():
    for pose in ('stand', 'pass', 'run'):
        add('rifle_%s_%s' % (look, pose), SP.build(*SP.rifleman(pose, look, skin)))
        add('rifle_%s_up_%s' % (look, pose), SP.build(*SP.rifleman(pose, look, skin, act='up')))
    add('rifle_%s_aim' % look, SP.build(*SP.rifleman('stand', look, skin, act='aim')))
    add('rifle_%s_flung' % look, SP.build(*SP.rifleman('run', look, skin, act='flung')))
for pose in ('stand', 'pass', 'run'):
    add('bomber_%s' % pose, SP.build(*SP.bomber(pose)))
    add('bomber_up_%s' % pose, SP.build(*SP.bomber(pose, 'up')))
    add('door_%s' % pose, SP.build(*SP.doorman(pose)))
    add('door_bare_%s' % pose, SP.build(*SP.doorman(pose, 'bare')))
    add('door_up_%s' % pose, SP.build(*SP.doorman(pose, 'hands')))
add('bomber_wind', SP.build(*SP.bomber('stand', 'wind')))
add('bomber_throw', SP.build(*SP.bomber('stand', 'throw')))
add('bomber_flung', SP.build(*SP.bomber('run', 'flung')))
add('door_lean', SP.build(*SP.doorman('stand', 'lean')))
add('door_back', SP.build(*SP.doorman('stand', 'back')))
add('door_shove', SP.build(*SP.doorman('stand', 'shove')))
add('door_aim', SP.build(*SP.doorman('stand', 'aim')))
add('door_flung', SP.build(*SP.doorman('run', 'flung')))
add('piece_door', SP.build(*SP.door_piece()))
add('piece_door_top', SP.build(*SP.door_piece('top')))
add('piece_door_bot', SP.build(*SP.door_piece('bot')))
add('det_tied', SP.build(*SP.detainee('tied')))
add('det_freed', SP.build(*SP.detainee('freed')))
add('det_walk1', SP.build(*SP.detainee('walk')))
add('det_walk2', SP.build(*SP.detainee('walk', 'pass')))
add('post', SP.build(*SP.post_piece()))
add('cmdr_stand', SP.build(*SP.commander('stand')))
add('cmdr_up_stand', SP.build(*SP.commander('hands')))
add('cmdr_up_pass', SP.build(*SP.commander('hands', 1)))

# ---------------------------------------------------------------- things that stand in the level
mine_im, mine_x, mine_y = CAP['mine']
img('mine', mine_im, 0, 0)
fixed = {'mine': [mine_x, mine_y]}                         # drawn exactly where the painting had it
for name, paint, seed in (('drum_oxide', 'oxide', 3), ('drum_blue', 'blue', 2)):
    dr, f = P.drum(paint, seed=seed)
    img(name, dr.image(), dr.w // 2, f - 2)
cr, f = P.crate(seed=7, mark=False)
crim = cr.image()
# the letter on the weapon crate
g = px.text_img('H', px.FONT_M, '#fff6d8')
blit(crim, silhouette(g, (40, 26, 12, 255)), crim.width // 2 - 2, 5)
blit(crim, g, crim.width // 2 - 3, 4)
img('crate_h', crim, crim.width // 2, f - 1)
crg = cr.image()
gG = px.text_img('G', px.FONT_M, '#fff6d8')
blit(crg, silhouette(gG, (40, 26, 12, 255)), crg.width // 2 - 2, 5)
blit(crg, gG, crg.width // 2 - 3, 4)
img('crate_g', crg, crg.width // 2, f - 1)
HMG_BOX = [
    '...xxxxxxx...',
    '..xYyYYyYYx..',
    '.xYYxYxYxYYx.',
    'xOOxYYYYYxOOx',
    'xOoOxYxYxOOox',
    'xOoOOoOOoOoox',
    'xooOooOooOoox',
    '.xxxxxxxxxxx.',
]
img('pick_hmg', sprite(HMG_BOX, {'x': '#141008', 'Y': '#ffd84a', 'y': '#c89018', 'O': '#8a6a3c', 'o': '#5a4020'}))
GREN_BOX = [
    '...xxxxxxx...',
    '..xGGgGGgGx..',
    '.xGgxxGxxgGx.',
    'xOOxYYxYYxOOx',
    'xOoOOoOOoOOox',
    'xOoOOoOOoOoox',
    'xooOooOooOoox',
    '.xxxxxxxxxxx.',
]
img('pick_gren', sprite(GREN_BOX, {'x': '#141008', 'G': '#8c9a5a', 'g': '#5c6a34', 'O': '#6e7c3c', 'o': '#3e4a1e', 'Y': '#ffd84a'}))

# ---------------------------------------------------------------- things with engines, and what stands beside the road
import vehicles as V          # noqa: E402
rig = {}
for name, paint, liv, who, seed_ in (('truck_olive', V.OLIVE, 'militia', 'grunt', 5), ('truck_sand', V.SANDP, 'militia', 'grunt', 6)):
    Lv, cx_, g_ = V.pickup(paint, liv, seed=seed_)
    V.driver(Lv, cx_, g_, who)
    img(name, P.outlined(Lv).image(), cx_ + 1, g_ + 1)
# Salem's car: the armoured truck (build 17; the white pickup it replaced is V.pickup(V.WHITE, 'shass'))
img('shass', P.outlined(V.mrap(seed=6)).image(), 53, 66)
rig['car'] = dict(wheel=V.WB // 2, r=V.WR, big=V.WRB)
for n_, L_ in V.wheel_frames() + V.big_wheel_frames():
    im_ = L_.image()
    img(n_, im_, im_.width // 2, im_.height // 2)
tg_, ax_, ay_ = V.truck_gun()
img('truck_gun', tg_.image(), ax_ + 1, ay_ + 1)
for k_ in range(2):
    im_ = V.kdrone(k_)
    img('kdrone%d' % k_, im_, im_.width // 2, 5)
    im_ = V.rmine(k_)
    img('rmine%d' % k_, im_, im_.width // 2, im_.height - 2)
im_ = V.mine_flag()
img('rmine_flag', im_, 1, im_.height - 1)
im_ = V.bbomb()
img('bbomb', im_, im_.width // 2, im_.height // 2)
bt_, binfo_ = V.boat()
img('boat', bt_.image(), binfo_['mid'][0] + 1, binfo_['mid'][1] + 1)
rig['boat'] = dict(rotors=[[x_ - binfo_['mid'][0], y_ - binfo_['mid'][1]] for x_, y_ in binfo_['rotors']], gun=[binfo_['gun'][0] - binfo_['mid'][0], binfo_['gun'][1] - binfo_['mid'][1]])
for n_, im_ in V.rotor_frames():
    img(n_, im_, im_.width // 2, 0)
bg_, ax_, ay_ = V.boss_gun()
img('boss_gun', bg_.image(), ax_ + 1, ay_ + 1)
cm_, ax_, ay_ = V.camel()
img('sc_camel', cm_.image(), ax_, ay_)
for k_ in ('camel', 'stop', 'end', 'battery'):
    sg_, ax_, ay_ = V.sign(k_)
    img('sc_sign_' + k_, sg_.image(), ax_, ay_)
st_, ax_, ay_ = V.stone()
img('sc_stone', st_.image(), ax_, ay_)
sk_, f_ = P.skiff(length=62, paint=P.BOATBLUE, stripe=P.BOATWHITE, seed=11, motor=False)
img('sc_boat', sk_.image(), sk_.w // 2, f_)
sk_, f_ = P.skiff(length=54, paint=P.BOATWHITE, stripe=P.REDP, seed=12, motor=False)
img('sc_boat2', sk_.image(), sk_.w // 2, f_)


def net_poles(w=46, h=30, seed=5):
    # a fishing net hung out to dry between two poles, sagging, with its floats
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px_ = im.load()
    wood = [(58, 38, 22, 255), (96, 66, 40, 255), (140, 104, 66, 255)]
    for x0 in (1, w - 3):
        for y in range(2, h):
            px_[x0, y] = wood[0]; px_[x0 + 1, y] = wood[2] if y % 5 else wood[1]
    rs = np.random.RandomState(seed)
    for x in range(3, w - 3):
        u = (x - 3) / float(w - 7)
        sag = 4 + 7 * (1 - (2 * u - 1) ** 2)
        top = int(4 + sag * 0.35)
        for y in range(top, int(top + 10 + sag * 0.6)):
            if (x + y) % 3 == 0 or (x - y) % 3 == 0:
                if rs.rand() < 0.85:
                    px_[x, y] = (46, 62, 52, 255) if (x + y) % 2 else (70, 90, 74, 255)
        if x % 7 == 3:
            px_[x, top] = (230, 120, 40, 255); px_[x, top - 1] = (250, 170, 80, 255)
    return im


img('sc_net', net_poles(), 23, 29)
for n_, (h_, lean_, seed_) in (('sc_palm_a', (78, 8, 21)), ('sc_palm_b', (64, -9, 23))):
    pm_, f_, bx_ = P.palm(height=h_, lean=lean_, seed=seed_)
    img(n_, pm_.image(), bx_, f_)
for n_, (w_, h_, seed_) in (('sc_rock_a', (44, 24, 41)), ('sc_rock_b', (30, 16, 43))):
    rk_, f_ = P.rock(w_, h_, seed=seed_)
    img(n_, rk_.image(), w_ // 2, f_)
ht_, f_ = P.hut(seed=4)
img('sc_hut', ht_.image(), ht_.w // 2, f_)
ml_, f_ = P.missile_launcher()
img('launcher', ml_.image(), 0, f_)
lw_, f_ = V.launcher_wreck()
img('launcher_wreck', lw_.image(), 6, f_)
sb_, f_ = P.sandbags(4, 3, seed=8)
ob_ = P.outlined(sb_).image()
img('rbags', ob_, ob_.width // 2, f_ + 1)

# ---------------------------------------------------------------- gunfire, dust, things in the air
for name in FXM.FX:
    im = FXM.fx(name)
    img('fx_' + name, im, im.width // 2, im.height // 2)
frames['fx_muzzle']['ax'] = 0
frames['fx_muzzle_s']['ax'] = 0
# the stick, end over end: four quarter turns
stick = FXM.fx('stick')
for i in range(4):
    r = stick.rotate(-90 * i, expand=True)
    img('fx_stick%d' % i, r, r.width // 2, r.height // 2)
GREN = ['.xxx.', 'xGgox', 'xgOox', 'xooox', '.xxx.']
gp = {'x': '#141008', 'G': '#b8c47c', 'g': '#8c9a5a', 'O': '#6e7c3c', 'o': '#3e4a1e'}
gi = sprite(GREN, gp)
for i in range(4):
    r = gi.rotate(-90 * i)
    img('fx_gren%d' % i, r, 2, 2)
# a longer, hotter tracer for the heavy gun
HT = ['.DROOOYYYWWW', 'DROOOYYYYWWW']
img('fx_tracer_h', sprite(HT, FXM.FXPAL), 11, 1)
HV = ['..DRROOYYW.', '.DRROOOYYWW', '.DRROOOYYWW', '..DRROOYYW.']
img('fx_heavy', sprite(HV, FXM.FXPAL), 9, 2)
# sand kicked up behind the pickup's wheels on the beach: fresh and dense, then wider and thinning out
SANDPAL = dict(FXM.FXPAL, d='#8c6a3a')
SANDPUFF = [            # lighter than the beach on top, so it reads against it, and shaded underneath
    ['...ss.....', '..sstss...', '.sttttts..', 'sttutuutt.', '.tuuduuut.', '..uu.ddu..'],
    ['.....ss..ss.....', '...sssts.stss...', '..sttttsstttts..', '.sttuttttttutts.', 'sttuutuuttuuutt.', '.tuuduuuduuuut..',
     '..uu.ddu.dduu...', '....d....d......'],
    ['.......s..s.s.........', '....s.s.ss.s.st.s.....', '...s.tst.tst.s.t.s....', '..t.st.t.t.tt.t.tt.s..', '.t.tutt.tu.tut.tu.t.t.',
     't.u.tu.u.tu.u.tu.u.t..', '.u.u.u.d.u.u.d.u.u.u..', '..u...u...d...u...u...', '....d.......u.....d...'],
]
for k_, rows_ in enumerate(SANDPUFF):
    img('fx_sand%d' % k_, sprite(rows_, SANDPAL), len(rows_[0]) // 2, len(rows_) - 1)
# smoke off a machine that is burning: three sizes of the same dark puff
for k_, r_ in enumerate((3.2, 4.6, 6.0)):
    S_ = 15
    yy_, xx_ = np.mgrid[0:S_, 0:S_]
    rs_ = np.random.RandomState(40 + k_)
    lobes_ = [(7 + rs_.uniform(-1.5, 1.5) * (k_ + 1) * 0.5, 7 + rs_.uniform(-1.2, 1.2) * (k_ + 1) * 0.5, r_ * rs_.uniform(0.62, 0.9)) for _ in range(4)] + [(7, 7, r_ * 0.8)]
    m_ = np.zeros((S_, S_), bool)
    lit_ = np.zeros((S_, S_), bool)
    for (cx_, cy_, rr_) in lobes_:
        d_ = np.sqrt((xx_ - cx_) ** 2 + (yy_ - cy_) ** 2)
        m_ |= d_ <= rr_
        lit_ |= np.sqrt((xx_ - cx_ + 1.2) ** 2 + (yy_ - cy_ + 1.4) ** 2) <= rr_ * 0.55
    im_ = np.zeros((S_, S_, 4), np.uint8)
    im_[m_] = (58, 52, 50, 255)
    im_[m_ & ((xx_ + yy_) % 2 == 0) & (yy_ > 8)] = (40, 36, 36, 255)
    im_[m_ & lit_] = (98, 90, 84, 255)
    im_[m_ & lit_ & ((xx_ + yy_) % 2 == 0) & (yy_ < 6)] = (132, 122, 112, 255)
    pim_ = Image.fromarray(im_, 'RGBA')
    bb_ = pim_.getbbox()
    img('fx_bsmoke%d' % k_, pim_.crop(bb_), 7 - bb_[0], 7 - bb_[1])
# the jambiya's cut: a crescent of light, two frames
for k_, (r0_, r1_) in enumerate(((13.0, 17.5), (15.0, 17.0))):
    S_ = 40
    yy_, xx_ = np.mgrid[0:S_, 0:S_]
    rr_ = np.sqrt((xx_ - 8.0) ** 2 + (yy_ - 20.0) ** 2)
    an_ = np.arctan2(yy_ - 20.0, xx_ - 8.0)
    arc_ = (rr_ >= r0_ + 3.0 * np.abs(an_) ** 1.5) & (rr_ <= r1_) & (np.abs(an_) < 1.15)
    im_ = np.zeros((S_, S_, 4), np.uint8)
    edge_ = arc_ & (rr_ > r1_ - 1.2)
    im_[arc_] = (255, 244, 200, 255)
    im_[edge_] = (255, 255, 255, 255)
    im_[arc_ & (rr_ < r0_ + 3.0 * np.abs(an_) ** 1.5 + 1.0)] = (255, 214, 120, 255)
    pim_ = Image.fromarray(im_, 'RGBA')
    bb_ = pim_.getbbox()
    img('fx_slash%d' % k_, pim_.crop(bb_), 8 - bb_[0], 20 - bb_[1])
frames['fx_tracer']['ax'] = 7
frames['fx_tracer_e']['ax'] = 0
import boom as BOOM          # noqa: E402
booms = {}
for bname, (R_, n_, seed_, ground_, dust_) in BOOM.SETS.items():
    fr_ = BOOM.trimmed(BOOM.frames(R_, n_, seed_, ground_, dust_))
    booms[bname] = len(fr_)
    for i, (im_, ax_, ay_) in enumerate(fr_):
        img('%s%02d' % (bname, i), im_, ax_, ay_)
for lv in (1, 2):
    img('door_marks%d' % lv, SP.door_marks(lv), 0, 0)
SCORCH = [
    '....kkKkkk.kk.....',
    '.kkKKKKKKKKKKkkk..',
    'kKKKKKKKKKKKKKKKkk',
    '.kkKKKKKKKKKKKkk..',
    '....kkkKKkkk......',
]
img('scorch', sprite(SCORCH, {'K': (30, 20, 14, 150), 'k': (46, 32, 22, 90)}), 9, 2)

# ---------------------------------------------------------------- the HUD's pieces
box = new(22, 22)
hud2.portrait(box, 1, 1, 'yazeed')
img('hud_portrait', box, 0, 0)
img('hud_plate_on', sprite(hud2.PLATE, hud2.PLATE_PAL), 0, 0)
img('hud_plate_off', sprite(hud2.PLATE, hud2.PLATE_OFF), 0, 0)
img('hud_pow_on', outline(sprite(hud2.POW, hud2.POW_PAL), FXM.EDGE), 0, 0)
img('hud_pow_off', outline(sprite(hud2.POW, {k: '#2a303c' for k in hud2.POW_PAL}), FXM.EDGE), 0, 0)
img('hud_radio', outline(sprite(hud2.RADIO, {'x': '#2a303c', 'Z': '#a8e8b0', 'z': '#e8ecff', 'y': '#5c6878'}), FXM.EDGE), 0, 0)
go = new(60, 20)
hud2.go_sign(go, 2, 4)
bb = go.getbbox()
img('hud_go', go.crop(bb), 0, 0)
ALERT = [
    '...xx...',
    '..xYYx..',
    '..xYYx..',
    '.xYxxYx.',
    '.xYxxYx.',
    'xYYxxYYx',
    'xYYYYYYx',
    'xYYxxYYx',
    'xYYYYYYx',
    '.xxxxxx.',
]
img('hud_alert', sprite(ALERT, {'x': '#141008', 'Y': '#ffd23a'}), 4, 12)
BEHIND = [
    '....xx',
    '...xRx',
    '..xRRx',
    '.xRRRx',
    'xRRRRx',
    '.xRRRx',
    '..xRRx',
    '...xRx',
    '....xx',
]
img('hud_behind', sprite(BEHIND, {'x': '#141008', 'R': '#ff5a3a'}), 0, 4)
LOCK = [
    '..xxxx..',
    '.xZxxZx.',
    '.xZ..Zx.',
    'xxxxxxxx',
    'xYYYYYYx',
    'xYYxxYYx',
    'xYYxxYYx',
    'xxxxxxxx',
]
img('hud_lock', sprite(LOCK, {'x': '#141008', 'Z': '#e8ecff', 'Y': '#ffc22e'}), 0, 0)

# the sandbags by the bow stand in front of the man who hides behind them, so they are a sprite of their own
DRESS = SS.dressing()
for im_, sx_, fy0_, fx0_, fyf_ in DRESS:
    if int(sx_) == 880:
        img('bags', im_, 0, 0)
        fixed['bags'] = [int(sx_ - fx0_), int(fy0_ - fyf_)]

# ---------------------------------------------------------------- The Coffee Port (mocha_sprites.py): the cook, the quartermaster, the Big Roaster
import mocha_sprites as MS          # noqa: E402
for n_, f_ in MS.frames().items():
    add(n_, f_)
RST = MS.roaster_parts()
for n_, (im_, ax_, ay_) in RST.items():
    img(n_, im_, ax_, ay_)
for n_, (im_, ax_, ay_) in MS.mocha_fx().items():
    img(n_, im_, ax_, ay_)
# what is left of it: the parts in their last state, together, burnt
_wr = Image.new('RGBA', (MS.RW + 40, MS.RH_ + 40), (0, 0, 0, 0))
for n_ in ('rst_track0', 'rst_body3', 'rst_drumc0', 'rst_stub'):
    im_, ax_, ay_ = RST[n_]
    _wr.alpha_composite(im_, (MS.OX + 20 - ax_, MS.OY + 20 - ay_))
_bb = _wr.getbbox()
WRECK = (_wr.crop(_bb), MS.OX + 20 - _bb[0], MS.OY + 20 - _bb[1])

# ---------------------------------------------------------------- The Souq (zabid_sprites.py): sacks of spice and their clouds, the
# shopkeepers and their counters, the barricades, the sandbags, the Tailor and his dummies, their stands and sheets
import zabid_sprites as ZS          # noqa: E402
for n_, f_ in ZS.frames().items():
    add(n_, f_)
for n_, (im_, ax_, ay_) in ZS.zabid_fx().items():
    img(n_, im_, ax_, ay_)

# ---------------------------------------------------------------- frames drawn by hand, taken in by import_art.py
# A name the game already has is replaced; a new name is added. 'roles' says which animation plays which part.
INC = os.path.join(HERE, '..', 'art', 'incoming')
roles, hips, incoming = {}, {}, set()
if os.path.exists(os.path.join(INC, 'manifest.json')):
    man_ = json.load(open(os.path.join(INC, 'manifest.json')))
    for n_, e_ in man_['frames'].items():
        frames[n_] = dict(im=Image.open(os.path.join(INC, 'frames', n_ + '.png')).convert('RGBA'), ax=e_['ax'], ay=e_['ay'])
        incoming.add(n_)
        if 'muzzle' in e_:
            points[n_] = e_['muzzle']
        if 'hip' in e_:
            hips[n_] = e_['hip']
    roles = man_.get('roles', {})
    print('hand-drawn frames taken in: %d; roles: %s' % (len(incoming), ', '.join(sorted(roles)) or 'none'))

# ---------------------------------------------------------------- burnt copies: what is left of a machine that has gone up
def burnt(im, seed=3):
    a = np.asarray(im.convert('RGBA')).astype(float)
    r = np.random.RandomState(seed)
    lum = a[..., :3].mean(axis=2, keepdims=True)
    soot = 0.30 + 0.16 * (r.rand(a.shape[0], a.shape[1], 1) > 0.5)
    rgb = (a[..., :3] * 0.35 + lum * 0.65) * soot + np.array([10.0, 6.0, 4.0])
    hot = (r.rand(a.shape[0], a.shape[1]) > 0.965) & (a[..., 3] > 0) & (lum[..., 0] > 60)
    rgb[hot] = (226, 110, 36)
    out = np.dstack([np.clip(rgb, 0, 255), a[..., 3:4]]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


frames['rst_wreck'] = dict(im=burnt(WRECK[0], seed=9), ax=WRECK[1], ay=WRECK[2])
for name in ('boat', 'shass', 'truck_olive', 'truck_sand'):
    f = frames[name]
    bn_ = name.split('_')[0] + '_burnt' if name.startswith('truck') else name + '_burnt'
    if bn_ not in incoming:
        frames[bn_] = dict(im=burnt(f['im']), ax=f['ax'], ay=f['ay'])

# ---------------------------------------------------------------- white copies, for the frame a hit lands
for name in list(frames):
    souq = name in ('barr0', 'barr1', 'barr2') or (name.startswith('tl_') and name not in ('tl_stand', 'tl_cover', 'tl_scissors', 'tl_pin'))
    if (name.split('_')[0] in ('rifle', 'bomber', 'door', 'drum', 'truck', 'cmdr', 'cook', 'qm', 'rst') and not name.startswith('door_marks') and name not in ('truck_gun', 'rst_wreck')) or name in ('mine', 'boat', 'shass', 'kdrone0', 'kdrone1') or souq:
        f = frames[name]
        frames[name + '!'] = dict(im=silhouette(f['im'], '#ffffff'), ax=f['ax'], ay=f['ay'])

# ---------------------------------------------------------------- the home screen and the campaign map (menu_art.py)
import menu_art as MA          # noqa: E402
for n_, (im_, ax_, ay_) in MA.sprites().items():
    img(n_, im_, ax_, ay_)
map_im_, map_info_ = MA.campaign_map()
map_im_.save(os.path.join(OUT, 'map.png'), optimize=True)
menu_meta = dict(map=dict(w=MA.MW, h=MA.MH, nodes={k: list(v) for k, v in MA.NODES.items()}, sea=MA.sea_points()))

# ---------------------------------------------------------------- pack them
order = sorted(frames, key=lambda n: (-frames[n]['im'].height, n))
AW = 512 if sum(f['im'].width * f['im'].height for f in frames.values()) < 512 * 1700 else 1024      # wider once the hand-drawn frames come in
x = y = rowh = 0
place = {}
for n in order:
    im = frames[n]['im']
    if x + im.width + 1 > AW:
        x = 0
        y += rowh + 1
        rowh = 0
    place[n] = (x, y)
    x += im.width + 1
    rowh = max(rowh, im.height)
AH = y + rowh + 1
atlas = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
meta = {}
for n in order:
    f = frames[n]
    atlas.alpha_composite(f['im'], place[n])
    meta[n] = [place[n][0], place[n][1], f['im'].width, f['im'].height, f['ax'], f['ay']]
atlas.save(os.path.join(OUT, 'atlas.png'), optimize=True)

# ---------------------------------------------------------------- the stage: three pictures of ground and five strips that slide past
import stage_long as SL          # noqa: E402
LS = SL.build()
play_a = Layer(SL.XA, stage.SH)
play_a.paste(LS['play_a'], 0, 0)
for im, sx, fy_, fx_, fy in sorted(DRESS, key=lambda s_: s_[2]):
    if int(sx) == 836:                                       # the crate by the bow is only something to look at
        play_a.paste(from_image(im), int(sx - fx_), int(fy_ - fy))
play_b = Layer(SL.WB, stage.SH)
play_b.paste(LS['play_b'], 0, 0)
BI = LS['binfo']
for k_, (bx_, pnt_) in enumerate(((452, 'oxide'), (466, 'green'))):
    dr_, f_ = P.drum(pnt_, seed=k_)
    play_b.paste(dr_, bx_ - dr_.w // 2, SL.ARENA_Y - 8 - f_)
for bx_, seed_ in ((420, 5), (700, 6)):
    sb_, f_ = P.sandbags(4, 3, seed=seed_)
    ob_ = P.outlined(sb_)
    play_b.paste(ob_, bx_, SL.ARENA_Y - 6 - f_)
br_, bh_ = SL.barrier()
play_b.paste(br_, BI['barrier'][0], BI['barrier'][1] - bh_ + 2)
pics = {}
for name, L in (('sky', LS['sky']), ('far', LS['far']), ('sea', LS['sea']), ('play_a', play_a), ('road', LS['tile']), ('play_b', play_b),
                ('r2b', LS['r2b']), ('sand', LS['sand']), ('b2r', LS['b2r']),
                ('fore', LS['fore'].crop(0, 150, LS['fore'].w, stage.SH)), ('fore_road', LS['fore_road'].crop(0, 84, LS['fore_road'].w, stage.SH)),
                ('fore_sand', LS['fore_sand'].crop(0, 84, LS['fore_sand'].w, stage.SH)),
                ('fore_b', LS['fore_b'].crop(0, 150, LS['fore_b'].w, stage.SH))):
    im = L.image()
    im.save(os.path.join(OUT, name + '.png'), optimize=True)
    pics[name] = im.size
FR0, FR1 = 2400, int(SL.XB * 1.25)
layers = {
    'sky': dict(img='sky', w=pics['sky'][0], h=pics['sky'][1], y=0, par=0.2, wrap=True),
    'far': dict(img='far', w=pics['far'][0], h=pics['far'][1], y=stage.FAR_TOP, par=0.35, wrap=True),
    'sea': dict(img='sea', w=pics['sea'][0], h=pics['sea'][1], y=stage.HORIZON, par=0.6, wrap=True),
    # (laid out by stage_long.strips(): road, the tarmac giving out, the sand run, the tarmac coming back, road, battery)
    'play': dict(par=1.0, strips=[dict(dict(img=n_, x=x_, w=w_, y=y_, h=pics[n_][1]), **({'until': u_} if u_ is not None else {}))
                                  for (n_, x_, w_, y_, u_) in SL.strips()[0]]),
    'fore': dict(par=1.25, strips=[dict(dict(img=n_, x=x_, w=w_, y=y_, h=pics[n_][1]), **({'until': u_} if u_ is not None else {}))
                                   for (n_, x_, w_, y_, u_) in SL.strips()[1]]),
}
old_ground = json.load(open(os.path.join(GEN, 'ground_beach.json')))
json.dump(dict(step=4, y=SL.ground_profile(old_ground['y'])), open(os.path.join(GEN, 'ground.json'), 'w'), separators=(',', ':'))
world = dict(XA=SL.XA, TILE=SL.TILE, NT=SL.NT, XB=SL.XB, WB=SL.WB, WORLD=SL.WORLD, ROAD_Y=SL.ROAD_Y, ARENA_Y=SL.ARENA_Y, XR1=SL.XR1, XS0=SL.XS0, XS1=SL.XS1, XR2=SL.XR2,
             tower=[SL.XB + BI['tower'][0], BI['tower'][1]], tower_w=BI['tower_w'], launcher=[SL.XB + BI['launcher'][0], BI['launcher'][1]],
             barrier=[SL.XB + BI['barrier'][0], BI['barrier'][1]])
json.dump(world, open(os.path.join(GEN, 'world.json'), 'w'), separators=(',', ':'))

# ---------------------------------------------------------------- lettering: every glyph with its edge and shadow already on it
FONTS = {
    'm_lav': (px.FONT_M, FXM.LAV), 'm_org': (px.FONT_M, FXM.ORG), 'm_red': (px.FONT_M, FXM.RED), 'm_blu': (px.FONT_M, FXM.BLU),
    's_lav': (px.FONT_S, FXM.LAV), 's_org': (px.FONT_S, FXM.ORG),
    'b_lav': (px.FONT_B, FXM.LAV), 'b_org': (px.FONT_B, FXM.ORG), 'b_red': (px.FONT_B, FXM.RED), 'b_blu': (px.FONT_B, FXM.BLU),
}
strips = []
fmeta = {}
for fname, (font, grad) in FONTS.items():
    cap = px.font_h(font)
    chars = sorted(k for k in font if len(k) == 1)
    cellh = cap + 6
    w = sum(len(font[c][0]) + 4 for c in chars)
    strip = new(w, cellh)
    gl = {}
    xx = 0
    for c in chars:
        gw = len(font[c][0])
        cell = new(gw + 4, cellh)
        FXM.gtext(cell, 1, 1, c, font, grad)
        strip.alpha_composite(cell, (xx, 0))
        gl[c] = [xx, gw]
        xx += gw + 4
    strips.append((fname, strip))
    fmeta[fname] = dict(cap=cap, cell=cellh, glyphs=gl, upper=(font is not px.FONT_M))
# the timer's tall numerals
chars = sorted(FXM.TALL)
tw = sum(len(FXM.TALL[c][0]) * 2 + 6 for c in chars)
strip = new(tw, 26)
gl = {}
xx = 0
for c in chars:
    n = len(FXM.TALL[c][0])
    gw = n * 2
    cell = new(gw + 8, 26)
    FXM.tall(cell, n + 1, 1, c)              # the outlined numeral lands at x=1, its shadow one further on
    strip.alpha_composite(cell.crop((0, 0, gw + 5, 26)), (xx, 0))
    gl[c] = [xx, gw]
    xx += gw + 6
strips.append(('tall', strip))
fmeta['tall'] = dict(cap=22, cell=26, glyphs=gl, upper=True, adv=4)
FW = max(s.width for _, s in strips)
FH = sum(s.height + 1 for _, s in strips)
fim = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
yy = 0
for fname, strip in strips:
    fim.alpha_composite(strip, (0, yy))
    fmeta[fname]['y'] = yy
    yy += strip.height + 1
fim.save(os.path.join(OUT, 'font.png'), optimize=True)

json.dump(dict(frames=meta, points=points, fixed=fixed, layers=layers, booms=booms, world=world, rig=rig, stage=dict(w=SL.WORLD, h=stage.SH),
               anims=roles, hips=hips, menu=menu_meta), open(os.path.join(GEN, 'atlas.json'), 'w'), separators=(',', ':'))
json.dump(fmeta, open(os.path.join(GEN, 'fonts.json'), 'w'), separators=(',', ':'))
print('atlas %dx%d, %d frames (%d with a white copy)' % (AW, AH, len(meta), sum(1 for n in meta if n.endswith('!'))))
print('pictures', pics)
print('font sheet %dx%d, %d faces' % (FW, FH, len(fmeta)))
for n in ['atlas', 'font', 'map'] + list(pics):
    print('  %-6s %6.1f KB' % (n + '.png', os.path.getsize(os.path.join(OUT, n + '.png')) / 1024))
print('muzzles:', {k: v for k, v in points.items() if k.startswith('yazeed_stand') or k.startswith('yazeed_crouch') or k.startswith('yazeed_jump')})
print('enemy points:', {k: v for k, v in points.items() if not k.startswith('yazeed') and ('worried' in k or 'door' in k or 'bomber' in k)})
print('mine at', fixed['mine'], 'size', mine_im.size)
print('bags at', fixed['bags'], 'size', frames['bags']['im'].size)
