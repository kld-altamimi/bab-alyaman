# committee_sprites.py - Dhamar (Mission 5, the Wadi), stage 1: «ذِهنت بن راتب», Dhihint bin Ratib, the Committee,
# in person, built the way the cast is (mock/ms3.py: fill-only rows outlined by part()). First drawn 10 Nov by the
# development run from the brief's look; redrawn 11 Nov from the photo and the wages clip Khaled sent ("the character
# design needs to be closer to how he looks"): a caricature by his traits, as the Spokesman's was. Rimless glasses with a
# gold bar and gold arms, thick black curly hair swept up and back, a short beard going grey, heavy lids, a full face;
# a dark navy jacket over a white thobe buttoned to its band collar, every pocket bulging with notes, and the jambiya
# with a horn hilt and a pale sheath on a black-and-gold belt. No shemagh (he wears none). The loudhailer in the far
# hand and the stamp on a chain in the near one are the game's. The laugh is his from the clip: eyes squeezed shut
# behind the glasses, the cheeks up, the mouth wide in the beard, the head thrown back. The jacket has three states as
# the fight goes on (full, sagging, pockets turned out). A mock: nothing is in a build until Khaled says yes to the look.
# Every frame is (image, ax, ay): the anchor is the point between the feet on the ground.
#   python3 committee_sprites.py        -> dhamar/s1/committee_frames.png (the lineup at 4x, Yazeed for scale)
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock'
sys.path.insert(0, MOCK)
sys.path.insert(0, HERE)
from PIL import Image
import ms3
from ms3 import pal, compose, INK, INK2, PARTS, MARSHAL, Build

OUT = os.path.join(HERE, '..', '..', 'dhamar', 's1')

# ---------------------------------------------------------------- his colours
# the cast's tone letters: the jacket (a b c d) a dark navy (darker than the cast's navy, as in the photo), the thobe (f g h i) white; his own skin (p q r s t: lighter
# and pinker than the cast's skin2, from the photo), black hair (u v w, w the grey in the curls), the beard in the metal
# letters (x y z Z: charcoal, grey, light grey: salt and pepper); the notes use the canvas letters (6 7 8): the game's
# own paper, a grey-green with a pale centre and no script. The Uncle's paper is another colour (phase 3).
NOTE = {'6': '#3e5a44', '7': '#7a9c7c', '8': '#c4d8b8'}
UNCLE_NOTE = {'6': '#5a3e5a', '7': '#9a6c98', '8': '#e0c0dc'}
LOOK = {'a': '#0c1018', 'b': '#1a2232', 'c': '#2c3a52', 'd': '#46597a',
        'p': '#6a4030', 'q': '#a87258', 'r': '#d6a07e', 's': '#eec4a2', 't': '#fbe2cc',
        'u': '#16120f', 'v': '#2c2622', 'w': '#5a524c',
        'x': '#1c1a18', 'y': '#3e3a37', 'z': '#7a746c', 'Z': '#aca69c'}


def com_pal(uncle=False):
    p = pal('navy', 'white', 'black', 'skin2')
    p.update(LOOK)
    p.update(UNCLE_NOTE if uncle else NOTE)
    return p


def R(rows):
    """Pad rows to one width (so a part can be written without counting every row)."""
    w = max(len(r) for r in rows)
    return [r.ljust(w, '.') for r in rows]


# ---------------------------------------------------------------- his parts (fill rows, facing right)
COM = {
    # the head in one piece (hair, face, glasses, beard), from the photo: black curly hair standing up and swept back,
    # the forehead clear under it; thick straight brows over heavy lids; rimless glasses, read at this size as their gold
    # bar and gold arm back to the ear and the glint of the lens either side of the eye; a broad nose; a full face; a
    # short beard going grey (charcoal flecked with grey, lighter at the chin) over the jaw and the moustache.
    # Rows: hair (0-4), forehead, brows, glasses, eye, nose, cheek, moustache, mouth, beard, beard, chin.
    'head': R([
        '...uuuuuuuu...',
        '.uuvuuuvuuwuu.',
        'uuvuwuuuuvuuuu',
        'uuuuuuuuuuuuu.',
        'uuuuuuuurrrrr.',
        '.uuuuqrrrrrrrr',
        '.uuuqruuuurruu',
        '.uwq%EEEJJJEJr',
        '..qr%rrJ#qJrst',
        '..qq%rrqqqrsst',
        '...qqrrrrrrrq.',
        '...yzyrrryyyy.',
        '...yyyrry##yz.',
        '...yzyZyzyyZy.',
        '....yZyyZyzy..',
        '.....yyZyy....',
    ]),
    'mouth_half': R([       # the drone: the lips parted in the beard (row 12)
        '...yyyrr#K#yz.',
    ]),
    # the laugh, from the clip: the eyes squeezed shut behind the glasses, the cheeks pushed up under them, the mouth wide
    # open in the beard with the top teeth showing; 'head_laugh2' is the peak, the jaw dropped a row
    'head_laugh': R([
        '...uuuuuuuu...',
        '.uuvuuuvuuwuu.',
        'uuvuwuuuuvuuuu',
        'uuuuuuuuuuuuu.',
        'uuuuuuuurrrrr.',
        '.uuuuqrrrrrrrr',
        '.uuuqruuuuuruu',
        '.uwq%EEEJJJEJr',
        '..qr%rrJ%%Jstt',
        '..qq%rsssssrst',
        '...qqrrrrrrrrq',
        '...yzyr#####y.',
        '...yyy#JJJJJ#.',
        '...yzy#KKKKK#.',
        '....yZy#####..',
        '.....yyZyyy...',
    ]),
    'head_laugh2': R([
        '...uuuuuuuu...',
        '.uuvuuuvuuwuu.',
        'uuvuwuuuuvuuuu',
        'uuuuuuuuuuuuu.',
        'uuuuuuuurrrrr.',
        '.uuuuqrrrrrrrr',
        '.uuuqruuuuuruu',
        '.uwq%EEEJJJEJr',
        '..qr%rrJ%%Jstt',
        '..qq%rsssssrst',
        '...qqrrrrrrrrq',
        '...yzyr#####y.',
        '...yyy#JJJJJ#.',
        '...yzy#KKMKK#.',
        '...yzy#KKKKK#.',
        '....yZy#####..',
        '.....yyZyyy...',
    ]),
    # caught: the eyes shut, the mouth shut, and «Received», his own stamp's red mark, on his cheek
    'head_caught': R([
        '...uuuuuuuu...',
        '.uuvuuuvuuwuu.',
        'uuvuwuuuuvuuuu',
        'uuuuuuuuuuuuu.',
        'uuuuuuuurrrrr.',
        '.uuuuqrrrrrrrr',
        '.uuuqruuuurruu',
        '.uwq%EEEJJJEJr',
        '..qr%rrJ##Jrst',
        '..qq%LMqqqrsst',
        '...qqMLrrrrrq.',
        '...yzyrrryyyy.',
        '...yyyrry##yz.',
        '...yzyZyzyyZy.',
        '....yZyyZyzy..',
        '.....yyZyy....',
    ]),
    # the black-and-gold belt of the photo (wider than the cast's) and his jambiya: a horn hilt with two gold studs,
    # a pale leather sheath standing up the middle of him
    'belt': R([
        'VEVVEVVEVVEV',
        'UGEGUGEGUGEU',
        'VEVVEVVEVVEV',
    ]),
    'jambiya': R([
        '.yEy.',
        '.xyx.',
        '.yEy.',
        '.4334',
        '..434',
        '..343',
        '...43',
    ]),
    # the far arm up with the loudhailer: the jacket's sleeve, the thobe's white cuff
    'far_arm': R([
        '......qrs',
        '....IJrrr',
        '..bcIJrrq',
        'bbccIJq..',
        'bcccb....',
        'bccb.....',
    ]),
    # the jacket, dark worsted, buttoned, the white collar of the thobe in its V; a chest pocket and a hip pocket on the
    # near side, lighter flaps over them, both bulging with notes (the pale edges stick out over the flaps and the pocket
    # pushes past the jacket's front edge). Three states.
    'jacket_full': R([
        '....bccddcb...',
        '..abccdJJdccb.',
        '.abbcccJJcccb.',
        '.abbccccJcc8cb',
        'aabbccccc888cb',
        'aabbccccbbbbc8',
        'aabbcccccdddc8',
        'aabbcccccdddcb',
        'aabbccccccccdb',
        'aabbcccccc888b',
        'aabbcccc8888cb',
        'aabbcccbbbbbc8',
        'aabbcccddddcc8',
        '.aabbccddddcc8',
        '.aaabbbdddbbb.',
    ]),
    'jacket_sag': R([       # half the notes gone: the pockets hang open and sag, a note or two left in each
        '....bccddcb...',
        '..abccdJJdccb.',
        '.abbcccJJcccb.',
        '.abbccccJcccb.',
        'aabbcccccc8ccb',
        'aabbccccbbbbcb',
        'aabbccccbdddcb',
        'aabbcccccdddcb',
        'aabbccccccdccb',
        'aabbccccccccbb',
        'aabbccccccc8cb',
        'aabbcccbbbbbcb',
        'aabbcccbddddcb',
        '.aabbccbddddb.',
        '.aaabbbbdddbb.',
    ]),
    'jacket_out': R([       # the pockets turned out: the white linings hang at the chest and the hip, nothing in them
        '....bccddcb...',
        '..abccdJJdccb.',
        '.abbcccJJcccb.',
        '.abbccccJcccb.',
        'aabbcccccccccb',
        'aabbccccbbbbcb',
        'aabbccccIIIIcb',
        'aabbcccccHIIcb',
        'aabbccccccHIcb',
        'aabbccccccccbb',
        'aabbcccccccccb',
        'aabbcccbbbbbcb',
        'aabbcccIIIIIcb',
        '.aabbccHIIIIb.',
        '.aaabbbbHIIbb.',
    ]),
    # the thobe below the jacket, to the ankle, with its folds
    'thobe': R([
        '...fghhiiihhgf....',
        '...fghhiiiihhgf...',
        '..fghhhiiiihhgf...',
        '..fghhhiiiihhggf..',
        '..fghhhiiiiihhgf..',
        '.fgghhhiiiiihhgf..',
        '.fgghhhiiiiihhggf.',
        '.fgghhhhiiiiihhgf.',
        '.fgghhhhiiiiihhgf.',
        'fggghhhhiiiiihhggf',
        'fggghhhhiiiiiihhgf',
        'fggghhhhiiiiiihhgf',
        'ffgggghhhhhhhhggff',
    ]),
    'shoes': R([
        '...AABBC.....AABBC..',
        '..AABBBBC...AABBBBC.',
    ]),
    # the stamp on its chain: gold links, a turned wooden handle, the black rubber base
    'stamp': R([
        'E..',
        '.E.',
        '.E.',
        '.Y.',
        'XYX',
        'xxx',
    ]),
    # a banknote (the game's paper) and a wad
    'note': R([
        '7888',
        '6778',
    ]),
    'wad': R([
        '78888',
        '67778',
        '68888',
        '66778',
    ]),
    # the near arm down, the hand closed on the chain
    'arm_down': R([
        'abcb....',
        'abbccb..',
        '.abbccb.',
        '..abbccb',
        '..aabbqr',
        '....aqrs',
    ]),
    # the near arm reaching forward and down to the table's edge, the hand flat on it (the laugh, the catch)
    'arm_table': R([
        'abcb..........',
        'abbcccb.......',
        '.aabbcccbb....',
        '...aabbcccbqr.',
        '.....aabbbqrrs',
        '..........qqqq',
    ]),
    # the near hand patting the hip pocket (phase 3)
    'arm_pat': R([
        'abcb....',
        'abbccb..',
        '.abbccb.',
        '..abbcb.',
        '..aabcb.',
        '...abcqr',
        '...aqrrs',
    ]),
    # the near sleeve
    'sleeve': R([
        '..bcddc.',
        '.bccdddc',
        'abccdddc',
        'abbccddc',
        'aabbcccb',
        '.aabbcb.',
        '..aabb..',
    ]),
}

# where his parts sit (fill coordinates): the house build, a little broader in the jacket; the head (16 rows) puts its
# eye on the row the cast's eyes are on and its beard over the collar
CB = Build(thobe=(3, 21), shoes=(3, 34), torso=(5, 8), belt=(6, 20), jamb=(13, 19), sleeve=(6, 11), forearm=(8, 15),
           head=(9, -3), far_arm=(14, 2), megaphone=(20, -4), foot=(12, 36))

JACKETS = {'full': 'jacket_full', 'sag': 'jacket_sag', 'out': 'jacket_out'}
HEADS = {'closed': 'head', 'laugh': 'head_laugh', 'laugh2': 'head_laugh2', 'caught': 'head_caught'}


def _head(L, p, kind='closed', dx=0, dy=0):
    """kind: closed, half (speaking), laugh, laugh2 (the peak), caught."""
    B = CB
    rows = list(COM[HEADS.get(kind, 'head')])
    if kind == 'half':
        rows[12] = COM['mouth_half'][0]
    L.append((rows, B.head[0] + dx, B.head[1] + dy, p))


def _base(p, jacket='full', dy=0):
    """Shoes, thobe, jacket, belt, jambiya: the standing man without arms or head. dy lifts the trunk (shoulders going)."""
    B = CB
    return [(COM['shoes'], B.shoes[0], B.shoes[1], p), (COM['thobe'], B.thobe[0], B.thobe[1], p),
            (COM[JACKETS[jacket]], B.torso[0], B.torso[1] + dy, p), (COM['belt'], B.belt[0], B.belt[1], p),
            (COM['jambiya'], B.jamb[0], B.jamb[1], p)]


def _loudhailer(L, p, dy=0):
    B = CB
    L += [(COM['far_arm'], B.far_arm[0], B.far_arm[1] + dy, p), (MARSHAL['megaphone'], B.megaphone[0], B.megaphone[1] + dy, p)]


def _notes(L, p, k):
    """Notes lifting out of the pockets as the laugh goes on: k = 1, 2, 3 (the frame)."""
    B = CB
    x, y = B.torso
    spots = [(x + 12, y + 2), (x + 15, y - 2), (x + 11, y + 8), (x + 18, y - 6), (x + 16, y + 5)][:k + 1]
    for nx, ny in spots:
        L.append((COM['note'], nx, ny, p))


def committee(mouth='half', jacket='full', flip=False):
    """Standing, the loudhailer up in the far hand, the stamp on its chain in the near one: the chairman reading the minutes."""
    p = com_pal()
    B = CB
    L = _base(p, jacket)
    _loudhailer(L, p)
    L += [(COM['arm_down'], B.forearm[0], B.forearm[1], p), (COM['stamp'], B.forearm[0] + 7, B.forearm[1] + 6, p),
          (COM['sleeve'], B.sleeve[0], B.sleeve[1], p)]
    _head(L, p, mouth)
    return compose(L, flip=flip, foot=B.foot)


def committee_vote(jacket='full', flip=False):
    """The vote: both hands up ("All in favour?"), the loudhailer on the table: the only second he can be hit."""
    p = com_pal()
    B = CB
    L = [(PARTS['arm_raise_l'], 4, -1, p)] + _base(p, jacket)
    L += [(PARTS['arm_raise_fl'], 15, 0, p)]
    _head(L, p, 'half')
    return compose(L, flip=flip, foot=B.foot)


def committee_laugh(k=1, jacket='full', flip=False):
    """The laugh, three frames: the head goes back, the shoulders go, the near hand holds the table, the loudhailer
    stays up, and notes lift out of the pockets (more each frame)."""
    p = com_pal()
    B = CB
    sh = (0, -1, 0)[k - 1]                          # the shoulders going: the trunk up a row on frame 2
    L = _base(p, jacket, dy=sh)
    _loudhailer(L, p, dy=sh - (k - 1))
    L += [(COM['arm_table'], B.forearm[0], B.forearm[1] + sh, p), (COM['sleeve'], B.sleeve[0], B.sleeve[1] + sh, p)]
    _head(L, p, 'laugh2' if k == 2 else 'laugh', dx=-min(k, 2), dy=-k + sh)
    _notes(L, p, k)
    return compose(L, flip=flip, foot=B.foot)


def committee_pat(flip=False):
    """Phase 3, the emergency session: the pockets turned out, patting them, the loudhailer stuck on."""
    p = com_pal()
    B = CB
    L = _base(p, 'out')
    _loudhailer(L, p)
    L += [(COM['arm_pat'], B.forearm[0], B.forearm[1], p), (COM['sleeve'], B.sleeve[0], B.sleeve[1], p)]
    _head(L, p, 'half')
    return compose(L, flip=flip, foot=B.foot)


def committee_caught(flip=False):
    """Caught at the table: hands on it, head down, his own stamp's mark on his cheek ("Received"), the loudhailer gone."""
    p = com_pal()
    B = CB
    L = _base(p, 'out')
    L += [(COM['arm_table'], B.forearm[0], B.forearm[1] + 1, p), (COM['sleeve'], B.sleeve[0], B.sleeve[1], p)]
    _head(L, p, 'caught', dx=1, dy=2)
    return compose(L, flip=flip, foot=B.foot)


def note(uncle=False):
    return compose([(COM['note'], 0, 0, com_pal(uncle))], foot=(0, 2))


def wad(uncle=False):
    return compose([(COM['wad'], 0, 0, com_pal(uncle))], foot=(0, 4))


# ---------------------------------------------------------------- the table, the gavel, the sign-in sheet
TABLE = R([
    'YYYYYYYYYYYYYYYYYYYYYYYYYYYY',
    'XXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    'WXW......................WXW',
    'WXW......................WXW',
    'WXW......................WXW',
    'WXW......................WXW',
    'WXW......................WXW',
    'WXW......................WXW',
    'WXW......................WXW',
    'WXW......................WXW',
])
GAVEL = R([
    'XWWX..',
    'XWWXY.',
    'XWWX.Y',
])
SHEET = R([              # the sign-in sheet: one name on it (a line), the rest blank
    'JJJJJJJ',
    'J#I#JJJ',
    'JJJJJJJ',
    'JJJJJJJ',
])


def table():
    p = com_pal()
    return compose([(TABLE, 0, 3, p), (GAVEL, 3, 0, p), (SHEET, 18, -1, p)], foot=(14, 13))


FRAMES = [('stand', lambda: committee('half')), ('vote', committee_vote), ('laugh1', lambda: committee_laugh(1)),
          ('laugh2', lambda: committee_laugh(2)), ('laugh3', lambda: committee_laugh(3)),
          ('sag', lambda: committee('half', 'sag')), ('laugh_sag', lambda: committee_laugh(2, 'sag')),
          ('pat', committee_pat), ('caught', committee_caught)]


def lineup(scale=4, with_yazeed=True):
    """Every frame on one strip, the feet on one line, Yazeed at the left for scale, the table at the right."""
    frames = [f() for _, f in FRAMES]
    if with_yazeed:
        frames = [ms3.yazeed()] + frames
    frames.append(table())
    gap = 6
    w = sum(im.width for im, _, _ in frames) + gap * (len(frames) + 1)
    top = max(fy for _, _, fy in frames)
    bot = max(im.height - fy for im, _, fy in frames)
    bg = Image.new('RGBA', (w, top + bot + 8), (214, 196, 160, 255))
    x = gap
    ground = top + 4
    for im, fx, fy in frames:
        bg.alpha_composite(im, (x, ground - fy))
        x += im.width + gap
    return bg.resize((bg.width * scale, bg.height * scale), Image.NEAREST)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    lineup().save(os.path.join(OUT, 'committee_frames.png'))
    for name, f in FRAMES:
        im, fx, fy = f()
        im.resize((im.width * 4, im.height * 4), Image.NEAREST).save(os.path.join(OUT, 'c_%s.png' % name))
    print('wrote', OUT)
