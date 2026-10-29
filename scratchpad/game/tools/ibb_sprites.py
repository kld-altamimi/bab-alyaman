# ibb_sprites.py - the sprites Ibb (Mission 4, the Green Valleys) adds. Stage 1 (24 Oct): the Zanabeel's Spokesman,
# on screens and in person. Built the way the cast is (mock/ms3.py: fill-only rows, outlined by part()), from the look
# Khaled approved on 24 Oct (game-direction's S6 portrait: red beret pulled over, gold badge, long face, heavy stubble
# and no beard, desert camo with red shoulder boards, a wooden podium with a red plaque). Every frame is (image, ax, ay):
# the anchor is the point between the feet on the ground, unless it says otherwise.
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock'
sys.path.insert(0, MOCK)
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw
import ms3
from ms3 import pal, compose, INK, INK2, PARTS, WRAPS, FACES

# ---------------------------------------------------------------- his colours
# the cast's tone letters (ms3.py), with his own: desert camo for the jacket (a b c d) and the trousers (f g h i), its
# blotches (5 6), the red of the beret and the shoulder boards (K L M), gold (D E F), the podium's wood (W X Y)
DESERT = ('#5e4c32', '#9a8460', '#c8b48a', '#e4d6b0')
BLOTCH = ('#7c6440', '#a6895a')


def spk_pal(skin='skin1'):
    p = pal('khaki', 'khaki', 'blue', skin)
    for ch, c in zip('abcd', DESERT):
        p[ch] = c
    for ch, c in zip('fghi', DESERT):
        p[ch] = c
    p['5'], p['6'] = BLOTCH
    p['K'], p['L'], p['M'] = '#6a0c10', '#b21e22', '#e0443c'
    return p


# ---------------------------------------------------------------- his parts (fill rows, facing right)
SPK = {
    # long face, heavy stubble over the lower half (a checker of the hair's light tone over the skin's shadow, darker
    # along the jaw), no beard; the moustache stubble-dark; three mouths
    'face': [
        '.u.rrrr#rr.',
        '.u.qrrrrrst',
        '..q%rrrrrq.',
        '..qqrrrrrr.',
        '..qwrrwuuu.',
        '..qqwrw##r.',
        '...qwqwqwr.',
        '...vqvqvqv.',
        '....vvvvv..',
    ],
    'mouth0': [          # closed: a line under the moustache
        '..qqwrw##r.',
        '...qwqwqwr.',
    ],
    'mouth1': [          # half open
        '..qqwr#KKr.',
        '...qwq###r.',
    ],
    'mouth2': [          # open wide, the teeth showing: the screaming register
        '..qqwr#JJJ.',
        '...qwq#KK#.',
    ],
    'blink': [
        '.u.rrrrwwr.',
    ],
    # the beret: flat and wide, pulled down over the back of the head, the gold badge at the front, the band under it
    'beret': [
        '.....KLLLK....',
        '...KLMMMMLLK..',
        '.KLMMMMMMMMLK.',
        'KLLLLLMMLLEFLK',
        '.KKLLLLLLLDEK.',
        '..KKKKKKKKKK..',
    ],
    # the uniform jacket: desert camo, a red shoulder board with its gold pip, the collar, a row of medals
    'jacket': [
        '....bcLLb...',
        '..abcLFLcb..',
        '.ab5cdccdcb.',
        '.abc6cdc#c..',
        'aab5ccLSOc#c',
        'abbccEEEccdc',
        'abb5ccccc#dc',
        'abbc6ccbcccc',
        'abb5cbcc5ccb',
        'aabbcc6cc#cb',
        '.abb5ccccbb.',
        '.aabbcc6cbb.',
        '.aabbbcccb..',
        '..aabbbbb...',
    ],
    'sleeve': [
        '..bcLLc.',
        '.bc5dddc',
        'abccd6dc',
        'abb5cddc',
        'aabbcc6b',
        '.aabbcb.',
        '..aabb..',
    ],
    # the near arm reaching forward to the podium's edge, the hand flat on it
    'forearm_podium': [
        'abcb.........',
        'ab5ccb.......',
        '.abbc6cb.....',
        '..aabbcccqrr.',
        '....aabbqrrrs',
        '.........qqqq',
    ],
    # camo trousers bloused into the boots: he stands up straight to read
    'trousers': [
        '..fghhhhhgg.....',
        '.fgh5hhhh5hg....',
        '.fghhhhhh6hg....',
        '.fgh5hhgfhhh5g..',
        '.fghhhg.fghh5g..',
        '.fgh6hg.fgh6hg..',
        '.fghhhg.fghhhg..',
        '.fg5hhg.fg5hhg..',
        '.fghhhg.fghhhg..',
    ],
    'boots': [
        '.UVVVG..UVVVG...',
        '.UVVGG..UVVGG...',
        'UVVVGGG.UVVVGGG.',
        'UUUUUUU.UUUUUUUU',
    ],
}

# where his parts sit (fill coordinates; the house build's head on a lean body)
SB = ms3.Build(trousers=(4, 22), boots=(4, 31), torso=(6, 8), belt=(6, 20), sleeve=(7, 11), forearm=(8, 15),
               face=(8, 5), wrap=(6, -1), foot=(11, 34))


# the rest of him, for once the trousers have gone (the jump in zone 3) and for the fight on the pass
SPK.update({
    # white boxer shorts with red hearts: what the podium was hiding
    'boxers': [
        '..HIIJJJIIH.....',
        '.HIJLJJJLJIH....',
        '.HIJJJJLJJIH....',
        '.HIJLIHHIJLIH...',
        '.HIJIH..HIJJH...',
    ],
    # bare shins, thin and pale, into the boots
    'shins': [
        '..pqrq..pqrq....',
        '..pqrq..pqrq....',
        '..pqrr..pqrr....',
        '..pqrq..pqrq....',
        '..pqrq..pqrq....',
    ],
    # the jump: legs flung apart, boots and all
    'legs_jump': [
        '...HIIJJJIIH.......',
        '..HIJLJJJLJIH......',
        '..HIJJJJLJJIHH.....',
        '.HIJJLIH..HIJJH....',
        'pqrqIH.....HJJIH...',
        'pqrq........pqrq...',
        'pqrr.........pqrq..',
        'UVVG..........pqrr.',
        'UVVGG.........UVVGG',
        'UUUUU.........UUUUU',
    ],
    # running, two strides (the shins are the cast's own run, in boots)
    'run0': [
        '...HIIJJJIIH.........',
        '..HIJLJJJLJIH........',
        '..HIJJJLJJJIHH.......',
        '..HIJJIHHIJJLIH......',
        '..pqrr...HIJJIH......',
        '.pqqr.......pqrr.....',
        'pqqr.........pqrr....',
        'UVVGG.........pqrq...',
        'UUUUU........UVVGG...',
        '.............UUUUUU..',
    ],
    'run1': [
        '...HIIJJJIIH.........',
        '..HIJLJJJLJIH........',
        '..HIJJJLJJJIH........',
        '...HIJJIIJJLH........',
        '....pqrrpqrr.........',
        '....pqrq.pqrr........',
        '...pqrq...pqrr.......',
        '..pqrq....UVVGG......',
        '.UVVGG....UUUUU......',
        '.UUUUU...............',
    ],
    # the near arm cupped to his ear: WHAT? SPEAK UP!
    'arm_ear': [
        '.......qrs',
        '......qrrr',
        '.....bcqr.',
        '....bc5c..',
        '...bc6c...',
        '..bccb....',
        '.bc5b.....',
        'bccb......',
        'abb.......',
    ],
    # a torch in the far hand, a sheet of paper in the near one: phase 3, reading in the dark
    'torch': [
        'xyyzZJ',
        'xyyzZJ',
        '.qrr..',
    ],
    'paper': [
        '..HIIJJ',
        '.HIJJJJ',
        '.HIJJJJ',
        'qrIJJJJ',
        'qrHIIJJ',
    ],
    'arm_read': [        # the near arm holding the paper up to the light
        'abcb......',
        'ab5ccb....',
        '.abbc6cb..',
        '..aabbccqr',
        '....aabqrr',
    ],
    # caught: his own microphone cable wound round him, arms and all
    'cable': [
        'UVUVUVUVUVU.',
        '.UGUGUGUGUGU',
        '............',
        'UVUVUVUVUVU.',
        '.UGUGUGUGUGU',
        '............',
        '..UVUVUVUVU.',
        '...UGUGUGU..',
    ],
    # the ear, ringing (phase 2): the face's ear turned hot red
    'ear_hot': [
        '..LMrrrrrq.',
    ],
    # his ear ringing: two arcs beside it (phase 2; the renderer flashes them)
    'ring': [
        '..FF.',
        '.F..F',
        'F.EE.',
        'F.E..',
        'F.EE.',
        '.F..F',
        '..FF.',
    ],
})


def _mouth(face_rows, m):
    rows = list(face_rows)
    rows[5:7] = SPK['mouth%d' % m]
    return rows


def _head(L, p, mouth=0, blink=False, hot_ear=False, dx=0, dy=0):
    B = SB
    face = _mouth(SPK['face'], mouth)
    if blink:
        face[0] = SPK['blink'][0]
    if hot_ear:
        face[2] = SPK['ear_hot'][0]
    L.append((face, B.face[0] + dx, B.face[1] + dy, p))
    L.append((SPK['beret'], B.wrap[0] + dx, B.wrap[1] + dy, p, INK2))


def _top(L, p, dx=0, dy=0):
    B = SB
    L.append((SPK['jacket'], B.torso[0] + dx, B.torso[1] + dy, p))
    L.append((PARTS['belt_plain'], B.belt[0] + dx, B.belt[1] + dy, p))


def spokesman(mouth=0, blink=False, flip=False, trousers=True, hot_ear=False):
    """At the podium, mid-sentence, the hands reaching for its edges. Trousers on in zone 3; on the pass, not."""
    p = spk_pal()
    B = SB
    if trousers:
        L = [(SPK['boots'], B.boots[0], B.boots[1], p), (SPK['trousers'], B.trousers[0], B.trousers[1], p)]
    else:
        L = [(SPK['boots'], B.boots[0], B.boots[1], p), (SPK['shins'], B.trousers[0], B.trousers[1] + 4, p),
             (SPK['boxers'], B.trousers[0], B.trousers[1], p)]
    _top(L, p)
    L += [(SPK['forearm_podium'], B.forearm[0], B.forearm[1], p), (SPK['sleeve'], B.sleeve[0], B.sleeve[1], p)]
    _head(L, p, mouth, blink, hot_ear)
    return compose(L, flip=flip, foot=B.foot)


def spokesman_jump(flip=False):
    """The jump when Yazeed walks in: arms thrown up, legs flung apart, and no trousers."""
    p = spk_pal()
    B = SB
    L = [(PARTS['arm_raise_l'], 4, -1, p), (SPK['legs_jump'], 2, 22, p)]
    _top(L, p)
    L += [(PARTS['arm_raise_fl'], 15, 0, p)]
    _head(L, p, 2)
    return compose(L, flip=flip, foot=(10, 31))


def spokesman_run(k, flip=False):
    """Dashing from podium to podium, no trousers, arms pumping."""
    p = spk_pal()
    B = SB
    L = [(SPK['run%d' % k], 1, 22, p)]
    _top(L, p, 1)
    L += [(PARTS['forearm_l'], 9, 15, p), (SPK['sleeve'], 8, 11, p)]
    _head(L, p, 1, dx=1)
    return compose(L, flip=flip, foot=(10, 31))


def spokesman_stunned(flip=False):
    """Cut off mid-sentence: a hand cupped to his ear, mouth open. WHAT? SPEAK UP!"""
    p = spk_pal()
    B = SB
    L = [(SPK['boots'], B.boots[0], B.boots[1], p), (SPK['shins'], B.trousers[0], B.trousers[1] + 4, p),
         (SPK['boxers'], B.trousers[0], B.trousers[1], p)]
    _top(L, p)
    L += [(SPK['sleeve'], B.sleeve[0], B.sleeve[1], p)]
    _head(L, p, 2, hot_ear=True)
    L += [(SPK['arm_ear'], 4, 6, p)]
    return compose(L, flip=flip, foot=B.foot)


def spokesman_reading(mouth=1, flip=False):
    """Phase 3, cornered on the last podium in the dark: a torch in one hand, the statement in the other."""
    p = spk_pal()
    B = SB
    L = [(SPK['boots'], B.boots[0], B.boots[1], p), (SPK['shins'], B.trousers[0], B.trousers[1] + 4, p),
         (SPK['boxers'], B.trousers[0], B.trousers[1], p)]
    _top(L, p)
    L += [(SPK['arm_read'], 8, 15, p), (SPK['paper'], 16, 11, p), (SPK['sleeve'], B.sleeve[0], B.sleeve[1], p)]
    _head(L, p, mouth, hot_ear=True)
    L += [(SPK['torch'], 19, 8, p)]                    # (held up by his face, at the page)
    return compose(L, flip=flip, foot=B.foot)


def spokesman_caught(flip=False):
    """Caught: tied up in his own microphone cable."""
    p = spk_pal()
    B = SB
    L = [(SPK['boots'], B.boots[0], B.boots[1], p), (SPK['shins'], B.trousers[0], B.trousers[1] + 4, p),
         (SPK['boxers'], B.trousers[0], B.trousers[1], p)]
    _top(L, p)
    L += [(SPK['sleeve'], B.sleeve[0], B.sleeve[1], p), (SPK['cable'], 5, 11, p)]
    _head(L, p, 1)
    return compose(L, flip=flip, foot=B.foot)


# ---------------------------------------------------------------- him on screens
# The billboard is game-direction's approved S6 portrait at its real size (scale 3, 144 x 96, his head about 45 px) with
# a television's scanlines; the podium screens (48 x 32) and the shop TVs (32 x 21) are the same picture shrunk by
# majority (each pixel the commonest colour of its block), so every screen is the one silhouette: the beret, the
# stubble, the red band of the podium. Three mouths and a blink each.
import spokesman_s6 as S6
from collections import Counter


def _majority(im, k):
    a = np.asarray(im.convert('RGB'))
    H, W = a.shape[0] // k, a.shape[1] // k
    out = np.zeros((H, W, 3), np.uint8)
    for y in range(H):
        for x in range(W):
            blk = a[y * k:(y + 1) * k, x * k:(x + 1) * k].reshape(-1, 3)
            out[y, x] = Counter(map(tuple, blk)).most_common(1)[0][0]
    return Image.fromarray(out).convert('RGBA')


def _scanlines(im, every=3, dim=0.86):
    a = np.asarray(im.convert('RGBA')).astype(float)
    a[::every, :, :3] *= dim
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def screen(size, mouth=1, blink=False):
    """size 'board' (144 x 96), 'podium' (48 x 32) or 'tv' (32 x 21) -> RGBA picture (no frame: the prop draws it)."""
    if size == 'board':
        return _scanlines(S6.s6(3, mouth=mouth, blink=blink))
    if size == 'podium':
        return _majority(S6.s6(4, mouth=mouth, blink=blink), 4)
    return _majority(S6.s6(6, mouth=mouth, blink=blink), 9)


# ---------------------------------------------------------------- the podium (his five, and the studio's)
PODIUM = [
    '..XYYYYYYYYYYYYYYYYYX..',
    '.XYYYYYYYYYYYYYYYYYYYX.',
    'WWXXXXXXXXXXXXXXXXXXXWW',
    '.WXXDEEEEEEEEEEEEEDXXW.',
    '.WXXEKLLLLLLLLLLLKEXXW.',
    '.WXXEKLMMLLLLLLMLKEXXW.',
    '.WXXEKLLLLLLLLLLLKEXXW.',
    '.WXXEKKKKKKKKKKKKKEXXW.',
    '.WXXDEEEEEEEEEEEEEDXXW.',
    '.WXXXXXXXXXXXXXXXXXXXW.',
    '.WXXXXXXXXXXXXXXXXXXXW.',
    '.WXXXXXXXXXXXXXXXXXXXW.',
    '.WXXXXXXXXXXXXXXXXXXXW.',
    '.WWXXXXXXXXXXXXXXXXXWW.',
    'WWWWWWWWWWWWWWWWWWWWWWW',
]
MIC = [
    '.UVU',
    'UVGVU',
    '.UVU.',
    '..x..',
    '..x..',
    '..x..',
    '..x..',
]


def podium():
    p = spk_pal()
    im, fx, fy = compose([(MIC, 15, -7, p), (PODIUM, 0, 0, p)], foot=(11, 14))
    return im, fx, fy


def ring():
    p = spk_pal()
    return compose([(SPK['ring'], 0, 0, p)], foot=(0, 0))


def speech(mouth=1, trousers=True, hot_ear=False):
    """Him behind his podium, as the game will draw them (the podium in front)."""
    im, ax, ay = spokesman(mouth, trousers=trousers, hot_ear=hot_ear)
    pd, px_, py_ = podium()
    out = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
    out.alpha_composite(im, (24 - ax, 56 - ay))
    out.alpha_composite(pd, (24 + 9 - px_, 56 - py_))
    if hot_ear:
        rg = ring()[0]
        out.alpha_composite(rg, (24 - ax + 8 + 2 - rg.width, 56 - ay + 5))
    bb = out.getbbox()
    return out.crop(bb), 24 - bb[0], 56 - bb[1]


def preview(path, scale=6):
    frames = [spokesman(0), spokesman(1), spokesman(2), spokesman(1, blink=True), spokesman_jump(),
              spokesman_run(0), spokesman_run(1), spokesman_stunned(), spokesman(2, trousers=False, hot_ear=True),
              spokesman_reading(), spokesman_caught(), podium()]
    W = sum(f[0].width for f in frames) + 8 * (len(frames) + 1)
    H = max(f[0].height for f in frames) + 16
    out = Image.new('RGBA', (W, H), (16, 20, 44, 255))
    x = 8
    for im, ax, ay in frames:
        out.alpha_composite(im, (x, H - 8 - im.height))
        x += im.width + 8
    out = out.resize((out.width * scale, out.height * scale), Image.NEAREST)
    out.save(path)
    return out.size



# ================================================================ stage 2 (24 Oct): the screens
# The billboard (the approved picture at its real size, drawn as one picture and three small patches: the mouth half
# open, wide open, the blink) and the shop's set (the same silhouette at a quarter size, on a crate). They are scenery:
# nothing breaks them (Khaled, 24 Oct: people want to hear him; the speakers on poles were dropped the same day). On a
# sheet of their own, art/out/ibb.png (gen/ibb_sprites.json), as Taiz's is.
import json

OUT = os.path.join(HERE, '..', 'art', 'out')
GEN = os.path.join(HERE, '..', 'gen')


def prop_pal():
    return pal('khaki', 'khaki', 'blue', 'skin2')


BOARD_MOUTH = (64, 49, 81, 59)        # the box the mouths change in (x0, y0, x1, y1), and the blink's
BOARD_BLINK = (56, 32, 89, 40)


def board_parts():
    """The billboard's picture (mouth shut, eyes open) and its patches, each anchored so that drawn at the picture's
    own anchor (its top left) it lands where it belongs."""
    base = screen('board', 0, False)
    out = [('board', base, 0, 0)]
    for name, src, box in (('board_m1', screen('board', 1, False), BOARD_MOUTH), ('board_m2', screen('board', 2, False), BOARD_MOUTH),
                           ('board_bl', screen('board', 0, True), BOARD_BLINK)):
        out.append((name, src.crop(box), -box[0], -box[1]))
    return out


def board_frame():
    """The bezel round the billboard's picture (152 x 104, the picture showing through the middle)."""
    W, H = 144 + 8, 96 + 8
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], fill=(18, 14, 10, 255))
    d.rectangle([1, 1, W - 2, H - 2], fill=(52, 56, 62, 255))
    d.line([(1, 1), (W - 2, 1)], fill=(96, 104, 110, 255))
    d.rectangle([3, 3, W - 4, H - 4], fill=(22, 24, 28, 255))
    d.rectangle([4, 4, W - 5, H - 5], fill=(0, 0, 0, 0))
    return im, 4, 4


def tv_box():
    """The set (screen hole 32 x 21 at 3, 3), a little stand under it; anchored at the bottom middle of the stand."""
    W, H = 32 + 6 + 8, 21 + 6
    im = Image.new('RGBA', (W, H + 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], fill=(18, 14, 10, 255))
    d.rectangle([1, 1, W - 2, H - 2], fill=(44, 40, 50, 255))
    d.line([(1, 1), (W - 2, 1)], fill=(78, 74, 88, 255))
    d.rectangle([2, 2, 32 + 3, 21 + 3], fill=(14, 12, 16, 255))
    d.rectangle([3, 3, 32 + 2, 21 + 2], fill=(0, 0, 0, 0))
    for ky in (6, 12):          # the knobs
        d.rectangle([W - 6, ky, W - 4, ky + 2], fill=(150, 142, 120, 255))
        d.point((W - 6, ky), fill=(220, 214, 190, 255))
    d.rectangle([W - 7, 19, W - 3, 21], fill=(20, 20, 24, 255))      # the speaker grille
    d.rectangle([6, H, 9, H + 2], fill=(18, 14, 10, 255))            # feet
    d.rectangle([W - 10, H, W - 7, H + 2], fill=(18, 14, 10, 255))
    # the rabbit ears
    for x0, x1 in ((W // 2 - 2, W // 2 - 9), (W // 2 + 1, W // 2 + 8)):
        d.line([(x0, 0), (x1, -1)], fill=(18, 14, 10, 255))
    ears = Image.new('RGBA', (W, H + 3 + 9), (0, 0, 0, 0))
    de = ImageDraw.Draw(ears)
    de.line([(W // 2 - 1, 9), (W // 2 - 9, 0)], fill=(30, 28, 30, 255))
    de.line([(W // 2 + 1, 9), (W // 2 + 9, 0)], fill=(30, 28, 30, 255))
    de.rectangle([W // 2 - 2, 8, W // 2 + 2, 9], fill=(30, 28, 30, 255))
    ears.alpha_composite(im, (0, 9))
    return ears, W // 2, H + 3 + 9 - 1


CRATE = [                       # what a set stands on in the street: a crate
    'XYYYYYYYYYYYYYYYYYYYYYYYYX',
    'XXXXXXXXXXXXXXXXXXXXXXXXXX',
    'XWXXXXXXXXXXXXXXXXXXXXXXWX',
    'XWXXXXXXXXXXXXXXXXXXXXXXWX',
    'XWYYYYYYYYYYYYYYYYYYYYYYWX',
    'XWXXXXXXXXXXXXXXXXXXXXXXWX',
    'XWXXXXXXXXXXXXXXXXXXXXXXWX',
    'XWXXXXXXXXXXXXXXXXXXXXXXWX',
    'XWYYYYYYYYYYYYYYYYYYYYYYWX',
    'XWXXXXXXXXXXXXXXXXXXXXXXWX',
    'XWXXXXXXXXXXXXXXXXXXXXXXWX',
    'XWXXXXXXXXXXXXXXXXXXXXXXWX',
    'XWWWWWWWWWWWWWWWWWWWWWWWWX',
]


def crate():
    p = prop_pal()
    return compose([(CRATE, 0, 0, p)], foot=(13, len(CRATE)))


def kid_frames():
    """The school's children (tools/ibb_kids.py; 29 Oct): each of the four, running (two halves of a stride), standing,
    waving. They face right; the game flips them to run left, for home."""
    import ibb_kids
    return [(n, im, ax, ay) for n, (im, ax, ay) in sorted(ibb_kids.frames().items())]


def yazeed_low():
    """Yazeed with his gun pointed at the ground, for while the school's children are out (render_ibb.js): standing and
    the two walking frames, with each gun. The same drawing as his frames in the atlas (sprites.py), aimed down and along."""
    import sprites as SP
    out = []
    for legs in ('stand', 'pass', 'run'):
        for gun in ('side', 'hmg'):
            b = SP.build(*SP.yazeed(legs, gun, 'ddiag'))
            out.append(('ylow_%s_%s' % (legs, gun), b['im'], b['ax'], b['ay']))
    return out


def stage_frames():
    """The terraces' stage (render_ibb.js, stage.js; Khaled, 29 Oct 21:36: "The story board looks great"): him at his
    podium, three mouths and a blink (no trousers already: he stands so close behind it that it hides everything below
    his belt, render_ibb.js); his jump (now they see) and the two halves of his run for the pass; the five of his
    audience in their chairs, still and clapping (tools/ibb_audience.py). All face right; the game turns him to face his
    audience."""
    out = []
    for m in range(3):
        out.append(('spk_m%d' % m,) + spokesman(m, trousers=False))
    out.append(('spk_bl',) + spokesman(0, blink=True, trousers=False))
    out.append(('spk_jump',) + spokesman_jump())
    for k in (0, 1):
        out.append(('spk_run%d' % k,) + spokesman_run(k))
    import ibb_audience as A
    for i, (look, skin) in enumerate(A.LOOKS):
        for c in (0, 1):
            out.append(('aud%d_%d' % (i, c),) + A.seated(look, skin, c))
    return out


def frames():
    """-> [(name, image, ax, ay)] for the sheet."""
    items = []
    for nm, im, ax, ay in board_parts():
        items.append((nm, im, ax, ay))
    items.append(('board_frame',) + board_frame())
    for m in range(3):
        items.append(('tv%d' % m, screen('tv', m, False), 0, 0))
    items.append(('tvb', screen('tv', 0, True), 0, 0))
    items.append(('tv_box',) + tv_box())
    items.append(('crate',) + crate())
    items += kid_frames() + yazeed_low()
    items.append(('podium',) + podium())          # (the terraces' stage: his podium on its deck, render_ibb.js)
    items += stage_frames()
    return items


def sheet():
    items = frames()
    W = 512
    x = y = rowh = 0
    place = []
    for n, im, ax, ay in sorted(items, key=lambda q: -q[1].height):
        if x + im.width + 1 > W:
            x = 0; y += rowh + 1; rowh = 0
        place.append((n, im, x, y, ax, ay))
        x += im.width + 1; rowh = max(rowh, im.height)
    H = y + rowh
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    meta = {}
    for n, im, x, y, ax, ay in place:
        out.alpha_composite(im, (x, y))
        meta[n] = [x, y, im.width, im.height, int(ax), int(ay)]
    return out, meta, dict(board=[144, 96], tv=[32, 21])


if __name__ == '__main__':
    if '--sheet' in sys.argv or '--look' in sys.argv:
        sh, meta, rig = sheet()
        if '--look' in sys.argv:
            bg = Image.new('RGBA', sh.size, (70, 80, 110, 255))
            bg.alpha_composite(sh)
            bg.resize((sh.width * 3, sh.height * 3), Image.NEAREST).save(os.path.join(OUT, 'ibb_look.png'))
            print('proof', os.path.join(OUT, 'ibb_look.png'), sh.size)
        else:
            sh.save(os.path.join(OUT, 'ibb.png'), optimize=True)
            json.dump(dict(frames=meta, rig=rig), open(os.path.join(GEN, 'ibb_sprites.json'), 'w'), separators=(',', ':'))
            print('ibb sheet %dx%d, %d frames, %d bytes' % (sh.width, sh.height, len(meta), os.path.getsize(os.path.join(OUT, 'ibb.png'))))
    else:
        print(preview(sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/ibb/s1/spk_poses.png'))
