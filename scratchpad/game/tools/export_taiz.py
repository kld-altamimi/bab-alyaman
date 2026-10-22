# export_taiz.py - Taiz's stage, laid out and written out for the game (Khaled, 21 Oct 05:38: "design the full level"):
# where every house, the gate, the souq, the terraces, the road and its bridge, the castle rock and the castle are, each
# piece painted at its size (mock/stage_taiz.py), packed onto a sheet (art/out/taiz_stage.png), and gen/stage_taiz.json
# saying where each goes and what the level needs: the ground's height along the way, the stone that stops the Apache and
# the shots, the roofs and walls men stand on, the doors they come out of, the windows that light up, the lamps, the road
# the pickups drive.
#   python3 export_taiz.py              (the sheet and the json)
#   python3 export_taiz.py --look X Y    (a picture of the world about X, Y as the game shows it at night: plan/look_X_Y.png)
import sys, os, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock'
sys.path.insert(0, MOCK)
import numpy as np
from PIL import Image
import stage_taiz as TZ

OUT = os.path.join(HERE, '..', 'art', 'out')
GEN = os.path.join(HERE, '..', 'gen')

# ------------------------------------------------------------------ the shape of the place (world pixels; y down)
WX, WY = 7950, 1300
STREET = 1200                    # the lower town's street, the old city's square
INTRO_END = 1160                 # the opening is played on foot along the street up to here
GATE_X = 2900                    # the old city's wall and its gate (260 wide)
SOUQ = (3160, 3700)              # the souq's square, between two tall houses
TERR = [(3700, 3850, 1130), (3850, 4000, 1060), (4000, 4150, 990), (4150, 4300, 920)]     # the terraces: x0, x1, ground
ROAD = [(4300, 920), (5300, 740)]                                    # the hillside road, climbing
BRIDGE_X, DECK, WADI = 5300, 740, 960                                # the bridge (320 wide), its deck, the wadi's bed
ROAD2 = [(5620, 740), (6200, 700)]                                   # the road on to the foot of the castle rock
ROCK_X0, ROCK_X1, TOP = 6200, 6320, 420                              # the castle rock's face, the top of it
CASTLE_X = 6320


def gy(x):
    """the ground's height at x (the heightfield: the street, the terraces' steps, the road, the wadi, the rock, the top)"""
    if x < TERR[0][0]:
        return STREET
    for x0, x1, g in TERR:
        if x0 <= x < x1:
            return g
    if x < ROAD[1][0]:
        f = (x - ROAD[0][0]) / float(ROAD[1][0] - ROAD[0][0])
        return ROAD[0][1] + (ROAD[1][1] - ROAD[0][1]) * f
    if x < BRIDGE_X + 60:
        return DECK + (x - BRIDGE_X) / 60.0 * 30 if x > BRIDGE_X + 20 else DECK
    if x < BRIDGE_X + 260:
        return WADI
    if x < ROAD2[0][0]:
        return DECK
    if x < ROAD2[1][0]:
        f = (x - ROAD2[0][0]) / float(ROAD2[1][0] - ROAD2[0][0])
        return ROAD2[0][1] + (ROAD2[1][1] - ROAD2[0][1]) * f
    if x < ROCK_X1:
        return ROAD2[1][1]
    return TOP


# ------------------------------------------------------------------ what stands where
# a house: [x0, width, height (street to parapet top), style, roof props, seed]; its foot on the ground under it
LOWER = [
    [1170, 74, 214, 'stone', ['tank'], 101], [1268, 90, 254, 'lime', ['stair', 'line'], 103], [1384, 66, 196, 'ochre', ['dish'], 107],
    [1478, 84, 286, 'mixed', ['stair', 'tank'], 109], [1588, 100, 236, 'lime', ['line', 'dish'], 113], [1716, 70, 300, 'stone', ['stair'], 127],
    [1814, 92, 226, 'ochre', ['tank', 'dish'], 131], [1932, 78, 262, 'lime', ['stair', 'tank'], 137], [2038, 104, 214, 'stone', ['line'], 139],
    [2170, 72, 322, 'mixed', ['stair'], 149], [2268, 96, 248, 'lime', ['tank', 'line'], 151], [2392, 80, 286, 'ochre', ['stair', 'dish'], 157],
    [2500, 92, 232, 'stone', ['tank'], 163], [2620, 76, 270, 'lime', ['stair', 'line'], 167], [2722, 92, 220, 'mixed', ['dish', 'tank'], 173],
]
SOUQ_HOUSES = [[3160, 100, 330, 'stone', ['stair', 'tank'], 181], [3600, 100, 320, 'lime', ['stair', 'dish'], 191]]
TERR_HOUSES = [[3742, 78, 118, 'lime', ['stair'], 201], [3892, 74, 124, 'ochre', ['tank'], 211], [4036, 80, 118, 'stone', ['stair', 'dish'], 223],
               [4186, 76, 120, 'lime', ['line'], 227]]
VILLAGE = [[5700, 78, 150, 'stone', ['stair', 'tank'], 233], [5830, 70, 130, 'lime', ['dish'], 239], [5990, 86, 160, 'ochre', ['stair', 'line'], 241]]
# the castle on top: walls, towers, the bastion the Castle Gun stands on, the keep (x0, width, height above TOP, kind)
CASTLE = [[6320, 60, 150, 'tower'], [6380, 170, 100, 'wall'], [6550, 60, 140, 'tower'], [6610, 230, 96, 'wall'], [6840, 160, 110, 'bastion'],
          [7000, 200, 100, 'wall'], [7200, 50, 130, 'tower'], [7450, 220, 230, 'keep'], [7670, 60, 140, 'tower'], [7730, 220, 100, 'wall']]
COURTYARD = (7250, 7450)         # where the Apache lands at the end
LAMPS = [420, 760, 1000]         # street lamps along the opening's street
# the opening: where the Zanabeel stand, the doors they run for, where the Apache comes down
INTRO = dict(yazeed=60, men=[330, 352, 372, 395, 418], doors=[300, 470, 640, 812], land=980)

pieces = {}       # name -> Image
place = []        # dict(p=name, x, y, layer)  (layer: 'back' behind everything, 'mid' the stage, 'decor' in front of the stage)
rock = []         # polygons the Apache and shots cannot pass through
plats = {}        # id -> [[x, y], [x, y]]
doors = []        # dict(id, x, y, kind)
windows = []      # dict(x, y, w, h, fan)
lamps = []        # [x, y]
info = {}


def add_piece(name, L):
    pieces[name] = L.image() if hasattr(L, 'image') else L


def put(name, x, y, layer='mid', flip=False):
    place.append(dict(p=name, x=int(x), y=int(y), layer=layer, flip=bool(flip)))


def house(spec, ground=None, pid=None, layer='mid'):
    x0, w, h, style, roof, seed = spec
    L, hi = TZ.taiz_house(w, h, seed=seed, style=style, roof=roof)
    name = 'h%d' % seed
    add_piece(name, L)
    base = ground if ground is not None else gy(x0 + w / 2.0)
    y = int(base - hi['h'])
    put(name, x0, y, layer)
    roofy = y + hi['top']
    pid = pid or ('h%d' % seed)
    plats[pid] = [[x0 + 3, roofy], [x0 + w - 3, roofy]]
    rock.append([[x0, base + 2], [x0, roofy], [x0 + w, roofy], [x0 + w, base + 2]])
    for d in hi['doors']:
        doors.append(dict(id='%s_street' % pid, x=x0 + d['x'], y=y + d['y'], kind='street'))
    if hi['stair']:
        st = hi['stair']
        doors.append(dict(id='%s_roof' % pid, x=x0 + st['x'], y=y + st['y'], kind='roof', top=y + st['top'], x0=x0 + st['x0'], x1=x0 + st['x1']))
        rock.append([[x0 + st['x0'], roofy + 1], [x0 + st['x0'], y + st['top']], [x0 + st['x1'], y + st['top']], [x0 + st['x1'], roofy + 1]])
    for wn in hi['windows']:
        windows.append(dict(x=x0 + wn['x'], y=y + wn['y'], w=wn['w'], h=wn['h'], fan=[x0 + wn['fan'][0], y + wn['fan'][1], wn['fan'][2], wn['fan'][3]] if wn['fan'] else None, house=pid))
    return dict(x0=x0, x1=x0 + w, roof=roofy, base=base, id=pid)


def build():
    out_houses = []
    # ---- the opening's street: the low side, the lamps, the paving
    L, si = TZ.shop_row(INTRO_END, seed=5, doors_at=INTRO['doors'])
    add_piece('shops', L)
    put('shops', 0, STREET - si['h'])
    for d in si['doors']:
        doors.append(dict(id='street_%d' % d['x'], x=d['x'], y=STREET, kind='street'))
    L, li = TZ.street_lamp()
    add_piece('lamp', L)
    for x in LAMPS:
        put('lamp', x - 7, STREET - li['h'] + 1, 'decor')
        lamps.append([x - 1, STREET - li['h'] + 1 + li['light'][1]])
    add_piece('paving', TZ.paving_strip(256, 40))
    # ---- the lower town
    for spec in LOWER:
        out_houses.append(house(spec))
    # ---- the old city's wall and gate
    L, gi = TZ.city_gate()
    add_piece('gate', L)
    gyv = STREET - gi['h']
    put('gate', GATE_X, gyv)
    for tx0, tx1, tt in gi['towers']:
        rock.append([[GATE_X + tx0, STREET + 2], [GATE_X + tx0, gyv + tt], [GATE_X + tx1, gyv + tt], [GATE_X + tx1, STREET + 2]])
        plats['gate_%d' % tx0] = [[GATE_X + tx0 + 3, gyv + tt], [GATE_X + tx1 - 3, gyv + tt]]
    wall_top = gyv + gi['wall']
    rock.append([[GATE_X, STREET + 2], [GATE_X, wall_top], [GATE_X + 260, wall_top], [GATE_X + 260, STREET + 2]])
    plats['gate_wall'] = [[GATE_X + 82, wall_top], [GATE_X + 178, wall_top]]
    info['gate'] = dict(x=GATE_X, y=gyv, arch=gi['arch'])
    # ---- the souq's square: the tall houses either side, the houses across it, the stalls
    for spec in SOUQ_HOUSES:
        out_houses.append(house(spec))
    L, bi = TZ.souq_back(SOUQ[1] - SOUQ[0] - 2 * 100 + 40, h=290, seed=11)
    add_piece('souq_back', L)
    put('souq_back', SOUQ[0] + 80, STREET - 290, 'back')
    for wn in bi['windows']:
        windows.append(dict(x=SOUQ[0] + 80 + wn['x'], y=STREET - 290 + wn['y'], w=wn['w'], h=wn['h'], fan=[SOUQ[0] + 80 + wn['fan'][0], STREET - 290 + wn['fan'][1], wn['fan'][2], wn['fan'][3]], house='souq_back', back=True))
    stalls = []
    for k, x in enumerate(range(SOUQ[0] + 112, SOUQ[1] - 180, 82)):
        L, sti = TZ.souq_stall(70, seed=k + 1)
        add_piece('stall%d' % k, L)
        put('stall%d' % k, x, STREET - sti['h'], 'decor')
        plats['stall%d' % k] = [[x + 3, STREET - sti['h'] + sti['top']], [x + sti['w'] - 4, STREET - sti['h'] + sti['top']]]
        stalls.append(x)
    info['stalls'] = stalls
    # ---- the terraces: their walls, a house on each
    for i, (x0, x1, g) in enumerate(TERR):
        prev = STREET if i == 0 else TERR[i - 1][2]
        hgt = prev - g
        L = TZ.terrace_wall(x1 - x0 + (0 if i == len(TERR) - 1 else 0), hgt + 260, seed=21 + i)
        add_piece('terr%d' % i, L)
        put('terr%d' % i, x0, g - 4, 'mid')
        plats['terr%d' % i] = [[x0 + 4, g], [x1 - 4, g]]
    for spec, (x0, x1, g) in zip(TERR_HOUSES, TERR):
        out_houses.append(house(spec, ground=g))
    # ---- the hillside: the bridge, the village, the water tower
    L, bri = TZ.stone_bridge()
    add_piece('bridge', L)
    put('bridge', BRIDGE_X, DECK - bri['deck'])
    o = bri['opening']
    bx = BRIDGE_X
    # (the bridge's stone: the deck and its parapet, and the two piers)
    rock.append([[bx, DECK - bri['deck']], [bx + 320, DECK - bri['deck']], [bx + 320, DECK + 40], [bx, DECK + 40]])
    rock.append([[bx, DECK], [bx + o[0], DECK], [bx + o[0], WADI + 2], [bx, WADI + 2]])
    rock.append([[bx + o[1], DECK], [bx + 320, DECK], [bx + 320, WADI + 2], [bx + o[1], WADI + 2]])
    plats['bridge'] = [[bx + 4, DECK - bri['deck']], [bx + 316, DECK - bri['deck']]]
    info['bridge'] = dict(x=bx, deck=DECK - bri['deck'], opening=[bx + o[0], bx + o[1]], wadi=WADI)
    for spec in VILLAGE:
        out_houses.append(house(spec))
    L, wi = TZ.water_tower()
    add_piece('wtower', L)
    put('wtower', 6100, gy(6120) - wi['h'] + 2, 'mid')
    # ---- the castle on its rock
    pieces_c = []
    for x0, w, h, kind in CASTLE:
        name = 'c_%d' % x0
        if kind == 'tower':
            L, ci = TZ.castle_tower(w, h, seed=x0)
        elif kind == 'wall':
            L, ci = TZ.castle_wall(w, h, seed=x0)
        elif kind == 'bastion':
            L, ci = TZ.bastion(w, h, seed=x0)
        else:
            L, ci = TZ.keep(w, h, seed=x0)
        add_piece(name, L)
        y = TOP - ci['h'] + 2
        put(name, x0, y, 'mid')
        t = y + (12 if kind in ('tower',) else 10 if kind in ('wall', 'bastion') else 20)
        rock.append([[x0, TOP + 2], [x0, t], [x0 + w, t], [x0 + w, TOP + 2]])
        plats[name] = [[x0 + 3, t], [x0 + w - 3, t]]
        for wn in ci.get('windows', []):
            windows.append(dict(x=x0 + wn['x'], y=y + wn['y'], w=wn['w'], h=wn['h'], fan=[x0 + wn['fan'][0], y + wn['fan'][1], wn['fan'][2], wn['fan'][3]] if wn.get('fan') else None, house=name, castle=True))
        pieces_c.append(dict(x0=x0, x1=x0 + w, top=t, kind=kind, id=name))
    info['castle'] = pieces_c
    plats['courtyard'] = [[COURTYARD[0] + 4, TOP], [COURTYARD[1] - 4, TOP]]
    # ---- the far view
    add_piece('qahira_far', TZ.far_qahira()[0])
    add_piece('moon', TZ.moon())
    info['houses'] = out_houses
    return out_houses


def ground_samples(step=8):
    return [round(gy(x), 1) for x in range(0, WX + 1, step)]


def pack(names, W=1024):
    """shelf-pack the pieces, tallest first, onto one sheet W wide"""
    order = sorted(names, key=lambda n: -pieces[n].height)
    x = y = rowh = 0
    pos = {}
    for n in order:
        im = pieces[n]
        if x + im.width > W:
            x = 0; y += rowh + 1; rowh = 0
        pos[n] = [x, y, im.width, im.height]
        x += im.width + 1; rowh = max(rowh, im.height)
    H = y + rowh
    sheet = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for n in order:
        sheet.alpha_composite(pieces[n], (pos[n][0], pos[n][1]))
    return sheet, pos


def write():
    build()
    names = list(pieces)
    sheet, pos = pack(names)
    sheet.save(os.path.join(OUT, 'taiz_stage.png'), optimize=True)
    out = dict(world=dict(W=WX, H=WY, STREET=STREET, INTRO_END=INTRO_END, GATE_X=GATE_X, SOUQ=list(SOUQ), TOP=TOP, ROCK=[ROCK_X0, ROCK_X1],
                          BRIDGE=info['bridge'], COURTYARD=list(COURTYARD), DECK=DECK, WADI=WADI),
               ground=dict(step=8, y=ground_samples(8)), pieces=pos, place=place, rock=rock, plats=plats, doors=doors, windows=windows,
               lamps=lamps, intro=INTRO, info=info,
               road=[[4300, 920], [5300, 740], [5310, 720], [5610, 720], [5620, 740], [6200, 700]],
               terr=[list(t) for t in TERR])
    json.dump(out, open(os.path.join(GEN, 'stage_taiz.json'), 'w'), separators=(',', ':'))
    opaque = sum(int((np.asarray(pieces[n])[..., 3] > 0).sum()) for n in names)
    print('taiz stage: %d pieces on a %dx%d sheet (%d painted px); %d placed; %d rock, %d plats, %d doors, %d windows'
          % (len(names), sheet.width, sheet.height, opaque, len(place), len(rock), len(plats), len(doors), len(windows)))
    return out


if __name__ == '__main__':
    write()
