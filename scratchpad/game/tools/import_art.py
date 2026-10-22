# import_art.py - take hand-drawn frames (the art pack's format, see BRIEF.md) into the game.
#
#   python3 import_art.py PACK_DIR [ROLES.json] [--fix-alpha] [--clear]
#
# PACK_DIR holds a manifest.json ({"frames": {name: {w, h, ax, ay, muzzle?, hip?, file?}}, "animations": {...},
# "palettes": {...}}) and the PNGs, anywhere below it (found by "file", or by name). ROLES.json says which of the pack's
# animations plays which part in the game: {"yazeed.idle": "yazeed_idle", "rifle.death.shot": "rifle_death_shot", ...}
# (the roles render.js knows are listed at roleFrame there). --clear empties the incoming folder first.
#
# Writes game/art/incoming/frames/*.png and game/art/incoming/manifest.json, which export_art.py folds into the sprite
# sheet: a name the game already has is replaced, a new name is added. Nothing here touches the game's code.
import sys, os, json, shutil
from PIL import Image
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
INC = os.path.join(HERE, '..', 'art', 'incoming')
GEN = os.path.join(HERE, '..', 'gen')
LIMITS = {'character': 16, 'machine': 24, 'effect': 12}
MACHINES = ('shass', 'truck', 'boat', 'wheel', 'rotor', 'boss', 'kdrone', 'launcher')
EFFECTS = ('fx', 'ex', 'hud')


def kind_of(name):
    head = name.split('_')[0]
    if head.startswith(MACHINES):
        return 'machine'
    if head in EFFECTS:
        return 'effect'
    return 'character'


def find_png(root, name, given=None):
    if given:
        p = os.path.join(root, given)
        if os.path.exists(p):
            return p
    for dp, dn, fn in os.walk(root):
        for f in fn:
            if f == name + '.png':
                return os.path.join(dp, f)
    return None


def main(argv):
    args = [a for a in argv if not a.startswith('--')]
    if not args:
        print(__doc__ if __doc__ else 'usage: import_art.py PACK_DIR [ROLES.json]')
        return 2
    pack = args[0]
    roles_map = json.load(open(args[1])) if len(args) > 1 else {}
    fix = '--fix-alpha' in argv
    man = json.load(open(os.path.join(pack, 'manifest.json')))
    have = set(json.load(open(os.path.join(GEN, 'atlas.json')))['frames'])
    if '--clear' in argv and os.path.isdir(INC):
        shutil.rmtree(INC)
    os.makedirs(os.path.join(INC, 'frames'), exist_ok=True)
    old = {}
    if os.path.exists(os.path.join(INC, 'manifest.json')):
        old = json.load(open(os.path.join(INC, 'manifest.json')))
    out = {'frames': old.get('frames', {}), 'roles': old.get('roles', {}), 'palettes': old.get('palettes', {})}
    problems, replaced, added, groups = [], [], [], {}
    for name, e in sorted(man.get('frames', {}).items()):
        p = find_png(pack, name, e.get('file'))
        if not p:
            problems.append('%s: no PNG found' % name)
            continue
        im = Image.open(p).convert('RGBA')
        a = np.array(im)
        semi = int(((a[..., 3] > 0) & (a[..., 3] < 255)).sum())
        if semi:
            if fix:
                a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
                im = Image.fromarray(a, 'RGBA')
            else:
                problems.append('%s: %d half-transparent pixels (rerun with --fix-alpha to snap them)' % (name, semi))
        w, h = im.size
        if ('w' in e and e['w'] != w) or ('h' in e and e['h'] != h):
            problems.append('%s: manifest says %sx%s, the PNG is %dx%d' % (name, e.get('w'), e.get('h'), w, h))
        ax, ay = e.get('ax', w // 2), e.get('ay', h - 1)
        if not (-w <= ax <= 2 * w and -h <= ay <= 2 * h):
            problems.append('%s: anchor (%s, %s) is far outside a %dx%d frame' % (name, ax, ay, w, h))
        cols = set(map(tuple, a[a[..., 3] > 0][:, :3].tolist()))
        lim = LIMITS[kind_of(name)]
        if len(cols) > lim:
            problems.append('%s: %d colours (limit %d for a %s)' % (name, len(cols), lim, kind_of(name)))
        groups.setdefault(name.split('_')[0], set()).update(cols)
        im.save(os.path.join(INC, 'frames', name + '.png'))
        rec = {'ax': ax, 'ay': ay}
        for k in ('muzzle', 'hip'):
            if k in e:
                rec[k] = e[k]
        out['frames'][name] = rec
        (replaced if name in have else added).append(name)
    anims = man.get('animations', {})
    for role, aname in roles_map.items():
        an = anims.get(aname)
        if not an:
            problems.append('role %s: the pack has no animation called %s' % (role, aname))
            continue
        missing = [f for f in an['frames'] if f not in out['frames'] and f not in have]
        if missing:
            problems.append('role %s: frames not in the pack or the game: %s' % (role, ', '.join(missing[:6])))
            continue
        rec = {'frames': an['frames'], 'loop': bool(an.get('loop', False))}
        if an.get('px_per_frame'):
            rec['px'] = an['px_per_frame']
        else:
            t = an.get('ticks') or [6] * len(an['frames'])
            if len(t) == 1:
                t = t * len(an['frames'])
            if len(t) != len(an['frames']):
                problems.append('role %s: %d frames but %d timings' % (role, len(an['frames']), len(t)))
                continue
            rec['ticks'] = t
        out['roles'][role] = rec
    out['palettes'].update(man.get('palettes', {}))
    json.dump(out, open(os.path.join(INC, 'manifest.json'), 'w'), indent=1)
    print('%d frames taken in: %d replace frames the game has, %d are new' % (len(replaced) + len(added), len(replaced), len(added)))
    print('roles now set: %s' % (', '.join(sorted(out['roles'])) or 'none'))
    for g, cols in sorted(groups.items()):
        print('  %-10s %d colours across its frames' % (g, len(cols)))
    unmapped = sorted(set(anims) - set(roles_map.values()))
    if unmapped:
        print('animations in the pack that play no role yet: %s' % ', '.join(unmapped))
    if problems:
        print('PROBLEMS (%d):' % len(problems))
        for q in problems:
            print('  ' + q)
    print('next: python3 export_art.py, then build the page')
    return 1 if problems and not fix else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
