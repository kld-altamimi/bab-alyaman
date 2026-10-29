# ibb_audience.py - the Spokesman's audience on the terraces' stage (zone 3): five of the Zanabeel in the plastic chairs set
# out in front of the stage, unarmed, facing it (to the right), sitting still or clapping, in the cast's style (ms3), as
# the storyboard drew them (mock/mock_stage.py; Khaled, 29 Oct 21:36: "The story board looks great").
# ibb_sprites.py puts their frames on Ibb's sheet: aud<i>_<0|1> (still, clapping) for each of LOOKS.
import ms3
from ms3 import at, compose

B = ms3.LEAN
FUTA_SIT = [               # the futa over thighs held level, the knees to the right
    '.fgghhiiiihhg...',
    'fgghhfhiiiihhgg.',
    'fgghhfgghhiiihgg',
    'ffgghfgghhhiihhg',
    '.ffggffgghhhhhg.',
]
SHINS_SIT = [              # from the knee to the floor, the foot on it
    'pqrr..',
    'pqrr..',
    'pqrq..',
    'pqrq..',
    'pqArrq',
    'AAAAAA',
]
CLAP_UP = [                # both hands brought together in front of the chest
    '......qrs.',
    '...bccrrrs',
    '.abccbbqr.',
    'abbccb....',
    'aabbb.....',
]
# who sits where, left to right along the rows (the back row's three, then the front row's two: level_ibb.js's seats)
LOOKS = [('worried', 'skin2'), ('qat', 'skin3'), ('youth', 'skin1'), ('angry', 'skin2'), ('worried', 'skin3')]


def seated(look='worried', skin='skin2', clap=0):
    """One of the audience in his chair: (image, ax, ay), the anchor where he sits on the seat, facing right."""
    p = ms3.militia_pal(skin)
    dy = 7                                             # (sat down: the hips 7 px lower than standing)
    L = [at(FUTA_SIT, (4, 21 + dy), p), at(SHINS_SIT, (15, 26 + dy), p),
         at('jacket_l', B.torso, p, 0, dy), at('belt_l', B.belt, p, 0, dy), at('jambiya_s', B.jamb, p, 0, dy)]
    if clap:
        L += [at('sleeve_l', B.sleeve, p, 0, dy), at(CLAP_UP, (8, 10 + dy - 2), p)]
    else:
        L += [at('forearm_l', B.forearm, p, 0, dy), at('sleeve_l', B.sleeve, p, 0, dy)]
    from sprites import lean_head
    lean_head(L, {'qat': 'qat_l'}.get(look, look), p, 0, dy)
    im, fx, fy = compose(L, foot=(6, 26 + dy))
    return im, fx, fy


# where the hands meet when he claps, from his anchor (the clap's little marks go either side: render_ibb.js)
CLAP_AT = (9, -15)
