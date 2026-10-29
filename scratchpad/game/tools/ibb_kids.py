# ibb_kids.py - the school's children (Ibb, zone 2: Jibla), drawn the way the cast is drawn (mock/ms3.py): fill-only
# parts in the cast's tone letters, each outlined by part() (black line, brown at skin and hair), lit from the right,
# facing right (the game flips them). Khaled, 29 Oct, on the storyboard's children: "too different from characters
# and blend too much with the background": so the cast's line and shading, a big head as children have, and colours
# that stand off the pale school wall and the cobbles (dark trousers and dresses, white scarves, bright bags).
#   boys: a light blue or white shirt, navy or grey trousers, black shoes; girls: a white scarf, a navy or dark green
#   dress over white trousers. Frames per child: run_a, run_b (the two halves of a stride), stand, wave.
#   python3 ibb_kids.py            writes art/preview_kids.png (the four children, every frame, x6)
import sys, os
MOCK = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock'
sys.path.insert(0, MOCK)
from PIL import Image
import ms3
from ms3 import pal, compose, RAMPS

RAMPS.setdefault('bottle', ('#0c2416', '#1a4428', '#2e6a40', '#5a9a62'))      # a dark green school dress
RAMPS.setdefault('slate', ('#1c1e26', '#353a48', '#575e70', '#8a92a4'))       # grey school trousers

# ---------------------------------------------------------------- heads (10-11 wide; eye at column 6-7)
BOY_HEAD = [          # cropped hair, a child's small nose (one pixel of highlight, no point), a short mouth
    '...uuuu...',
    '.uuvvvvu..',
    'uuvvvwwvu.',
    'uvvrrrrrr.',
    'uvqrrr#rr.',
    'uvq%rrrrs.',
    '.uqrrrrrr.',
    '..qrrr#r..',
    '...qqrr...',
]
GIRL_HEAD = [          # the white school scarf over the head and round the face, tucked under the chin
    '...HIIJ...',
    '.HIIJJJJ..',
    'HIIJJJJJJ.',
    'HIIJJrrrrr',
    'HIIJqrr#rr',
    'HIIJqrrrrs',
    'HIIJqrrrrr',
    'HIIJJqr#r.',
    '.HIIJJJJ..',
    '..HIJJ....',
]
# ---------------------------------------------------------------- bodies
SHIRT = [
    '.abccc..',
    'abbcccd.',
    'abbccdc.',
    'abbcccd.',
    'aabbccc.',
]
TROUSERS = [
    'fgghhhi',
    'fgghhhi',
    'fgg.ghh',
]
DRESS = [
    '.abccc...',
    'abbcccd..',
    'abbccdc..',
    'abbcccd..',
    'abbcccdc.',
    'abbccccdc',
    'abbbcccdc',
    'aabbcccdd',
]
# legs, per pose: boys' trouser legs (f g h) or the girls' white trousers (H I J), and black shoes (U V G)
LEGS = {
    'stand': ['fg..gh.', 'fg..gh.', 'UV..UVG'],
    'run_a': ['.fgg...ghh.', 'fgg.....ghh', 'UV.......UVG'],
    'run_b': ['..fggh..', '..fghh..', '..UVVG..'],
}
LEGS_GIRL = {
    'stand': ['.HI..IJ.', '.UV..UVG'],
    'run_a': ['HI.....IJ', 'UV.....UVG'],
    'run_b': ['..HIJ...', '..UVVG..'],
}
# the near arm: a short sleeve in the shirt's tones and a hand
ARMS = {
    'stand': (['bc', 'bc', 'qr'], (6, 10)),
    'run_a': (['bcc.', '.bqr'], (6, 10)),            # swung forward
    'run_b': (['cb.', 'qr.'], (3, 11)),              # swung back
    'wave': ([], (6, 10)),                          # (the near arm is raised: see kid())
}
BAG = ['.KLL', 'KLLM', 'KLLM', 'KLLM', 'KLLL', '.KK.']
BAGS = {'red': {}, 'yellow': {'K': '#7a5208', 'L': '#d49c1c', 'M': '#ffe264'}, 'blue': {'K': '#16264a', 'L': '#30588c', 'M': '#6c9cc8'}}

KIDS = {
    # name: (girl, top ramp, lower ramp, skin, bag)
    'boy1': (False, 'blue', 'navy', 'skin2', 'red'),
    'boy2': (False, 'white', 'slate', 'skin3', 'yellow'),
    'girl1': (True, 'navy', 'white', 'skin1', 'blue'),
    'girl2': (True, 'bottle', 'white', 'skin2', 'red'),
}
POSES = ('run_a', 'run_b', 'stand', 'wave')


def kid(name, pose):
    """One frame: (image, ax, ay), the anchor between the feet on the ground, facing right."""
    girl, top, lower, skin, bag = KIDS[name]
    p = pal(top, lower, 'white', skin)
    p.update(BAGS[bag])
    legs = pose if pose in LEGS else 'stand'
    bob = -1 if pose == 'run_b' else 0                    # (the body rides up on the passing step)
    L = [(BAG, -2 if girl else -1, 10 + bob, p)]
    if girl:
        lg = LEGS_GIRL[legs]
        L.append((lg, 1 if legs == 'run_a' else 2, 18, p))
        L.append((DRESS, 1, 10 + bob, p))
    else:
        lg = LEGS[legs]
        L.append((lg, 1 if legs == 'run_a' else 2, 17, p))
        L.append((TROUSERS, 2, 14 + bob, p))
        L.append((SHIRT, 1, 9 + bob, p))
    arm, (ax, ay) = ARMS[pose if pose in ARMS else 'stand']
    if arm:
        L.append((arm, ax, ay + bob + (1 if girl else 0), p))
    L.append((GIRL_HEAD if girl else BOY_HEAD, 0, (0 if girl else 0) + bob, p, ms3.INK2))
    if pose == 'wave':
        # the near arm up in front of him from the shoulder, the hand open above his head: a wave
        L.append((['..rs', '.qrr', '..qr', '..qr', '..qr', '..qr', '.bc.', '.bc.', 'bc..'], 8 if girl else 7, -1 + (1 if girl else 0), p))
    foot_y = 20 if girl else 19
    im, fx, fy = compose(L, foot=(5, foot_y))
    return im, fx, fy


def frames():
    out = {}
    for n in KIDS:
        for pose in POSES:
            out['kid_%s_%s' % (n, pose)] = kid(n, pose)
    return out


def preview(path, zoom=6):
    fr = frames()
    cell = (20, 30)
    cols = len(POSES)
    rows = len(KIDS)
    im = Image.new('RGBA', (cols * cell[0], rows * cell[1]), (200, 210, 190, 255))
    for i, n in enumerate(KIDS):
        for j, pose in enumerate(POSES):
            f, ax, ay = fr['kid_%s_%s' % (n, pose)]
            im.alpha_composite(f, (j * cell[0] + 10 - ax, i * cell[1] + 27 - ay))
    im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
    im.save(path)
    return im.size


if __name__ == '__main__':
    print(preview(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'art', 'preview_kids.png')))
    for k, (f, ax, ay) in sorted(frames().items()):
        print(k, f.size, (ax, ay))
