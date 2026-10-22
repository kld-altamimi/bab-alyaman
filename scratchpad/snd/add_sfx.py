# add_sfx.py - put effects made since the last full export onto the end of the game's sfx.mp3 without moving the rest:
# the strip is laid out again from the same recipes in the same order as export_game.py (every old clip comes out at
# the same place, which is checked against gen/audio.json), the new ones go on the end, and audio.json gains entries
# for them.
#   python3 add_sfx.py            (18 Oct: the Souq's sack, barricade knock, cannon, wheels, pigeon; 19 Oct: the Great
#                                  Scale's bonk, chain and weights, the cannon's shot renamed the blunderbuss; later on
#                                  19 Oct: the Tailor's in, the Great Scale's out)
import json
import numpy as np
from core import *
import sfx

GEN = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/gen/'
AUD = '/home/claude/bab_out/m1/audio/'
MARK, GAP = 0.05, 0.1                                        # the same layout as export_game.py (copied: it runs on import)


def marker():
    n = n_of(0.0012)
    t = np.arange(n) / SR
    return np.sin(TAU * 4000 * t) * np.hanning(n) * 0.6


def sprite(clips):
    parts = [np.zeros(n_of(MARK)), marker(), np.zeros(n_of(0.15))]
    at = {}
    pos = sum(len(p) for p in parts)
    for name, y in clips:
        y = fade(np.asarray(y, dtype=float).copy(), 0.0001, 0.004)
        at[name] = [round(pos / SR, 4), round(len(y) / SR, 4)]
        parts += [y, np.zeros(n_of(GAP))]
        pos += len(y) + n_of(GAP)
    return np.concatenate(parts), at


def pk(y, peak_db):
    return to_peak(np.asarray(y, dtype=float), peak_db)


E = sfx.EFFECTS
def eff(name, seed=0):
    label, group, fn, peak = E[name]
    return pk(fn(seed), peak)


def loopable(y, pad=0.05):
    k = n_of(pad)
    return np.concatenate([y[-k:], y, y[:k]])


def old_clips():
    """export_game.py's list, as it stood at build 27."""
    one_hmg = pk(sfx.heavy_mg(seed=0, shots=1)[:n_of(0.42)], -4.0)
    one_hmg2 = pk(sfx.heavy_mg(seed=5, shots=1)[:n_of(0.42)], -4.0)
    return [
        ('shot_side', eff('pistol')), ('shot_hmg', one_hmg), ('shot_hmg2', one_hmg2), ('eshot', eff('enemy_rifle')), ('eshot2', eff('enemy_rifle', 3)),
        ('clang', eff('door_clang')), ('ricochet', eff('ricochet')), ('hit_body', eff('hit_body')), ('hit_sand', eff('hit_sand')),
        ('door_break', eff('door_break')), ('bash', eff('bash')),
        ('throw', eff('grenade_throw')), ('bounce', eff('grenade_bounce')), ('boom_s', eff('explosion_small')), ('boom_s2', eff('explosion_small', 4)),
        ('boom_m', eff('explosion_drum')), ('fuse', eff('fuse')),
        ('step', pk(sfx.step_sand(0), -18)), ('step2', pk(sfx.step_sand(1), -19)), ('jump', eff('jump')), ('land', eff('land')),
        ('pick_weapon', eff('pickup_weapon')), ('pick_gren', eff('pickup_grenades')), ('coin', eff('coin')), ('medal', eff('medal')), ('checkpoint', eff('checkpoint')),
        ('rope', eff('rope_cut')), ('freed', eff('freed')), ('surrender', eff('surrender')),
        ('go', eff('go_prompt')), ('plate', eff('plate_lost')), ('low', eff('low_armour')), ('life', eff('life_lost')),
        ('ui_move', eff('ui_move')), ('ui_select', eff('ui_select')), ('ui_back', eff('ui_back')), ('tick', eff('tick')), ('radio', eff('radio_full')),
        ('sea', eff('sea')), ('gull', eff('gull')),
        ('knife', eff('knife')), ('knife2', eff('knife', 5)),
        ('engine', loopable(eff('engine_loop'))), ('rotor', loopable(eff('rotor_loop'))),
        ('hop', eff('hop')), ('car_land', eff('car_land')), ('crash', eff('crash')), ('ram', eff('ram')), ('ram2', eff('ram', 4)),
        ('horn_shass', eff('horn_shass')), ('horn_truck', eff('horn_truck')), ('boat_horn', eff('boat_horn')),
        ('brake', eff('brake')), ('door_slam', eff('door_slam')),
        ('heavy_shot', eff('heavy_shot')), ('heavy_shot2', eff('heavy_shot', 3)), ('spinup', eff('spinup')),
        ('lock', eff('lock')), ('dive', eff('dive')), ('whistle', eff('whistle')), ('bay', eff('bay')), ('launch', eff('launch')),
        ('smash_crate', eff('smash_crate')), ('smash_bags', eff('smash_bags')),
        ('part_off', eff('part_off')), ('boss_fall', eff('boss_fall')), ('boom_big', eff('explosion_big')), ('strike', eff('strike_bells')),
        ('stamp', eff('stamp')), ('paper', eff('paper')), ('route', eff('route')),
        ('door_creak', eff('door_creak')), ('hiss', eff('hiss')), ('steam', eff('steam')), ('bean_spray', eff('bean_spray')),
        ('pop', eff('pop')), ('pour', eff('pour')), ('rev', eff('rev')),
    ]


# build 28: the Souq; build 30: the Tailor's shears, pins, the rip of a dummy's clothes, his tape, a dummy going over, a
# sheet thrown out. (Build 28's blunderbuss and build 29's bonk, chain and iron weights went with the Great Scale: the
# clips after the first of them moved up, and audio.json with them.)
NEW = [('sack_burst', lambda: eff('sack_burst')), ('thunk', lambda: eff('thunk')),
       ('creak', lambda: loopable(eff('creak_loop'))), ('pigeon', lambda: eff('pigeon')),
       ('snip', lambda: eff('snip')), ('pins', lambda: eff('pin_rattle')), ('rip', lambda: eff('rip')), ('tape', lambda: eff('tape_zip')),
       ('clatter', lambda: eff('clatter')), ('whoosh', lambda: eff('whoosh')),
       ('heli', lambda: loopable(eff('heli_loop'))),          # (21 Oct: Taiz, the Apache)
       ('beep', lambda: eff('lock_beep')), ('locktone', lambda: eff('lock_tone')),      # (21 Oct, second cut: the lock-on's beat and tone)
       ('gun30', lambda: eff('gun30')), ('gun30b', lambda: eff('gun30', 4)), ('hedp', lambda: eff('hedp')), ('hedp2', lambda: eff('hedp', 6)),
       ('rbeep', lambda: eff('rlock_beep')), ('rlocked', lambda: eff('rlock_tone'))]     # (0.9.52: the chain gun as an Apache's, its rounds bursting, the pod's lock)
DROPPED = ('blunderbuss', 'bonk', 'chain_snap', 'iron_thud', 'chin', 'chin2')       # (0.9.52: the second cut's chin gun, replaced by gun30)

if __name__ == '__main__':
    au = json.load(open(GEN + 'audio.json'))
    old = old_clips()
    have = au['sfx']
    clips = old + [(k, fn()) for k, fn in NEW if k not in [c[0] for c in old]]
    strip, at = sprite(clips)
    for k, _ in old:
        assert k in have and abs(at[k][0] - have[k][0]) < 0.0002 and abs(at[k][1] - have[k][1]) < 0.0002, k
    # (and every clip made before keeps its place, up to the first one taken out; after it, each keeps its length)
    names = list(have)
    first = min([names.index(k) for k in DROPPED if k in have] + [len(names)])
    for k, _ in clips:
        if k in have:
            assert abs(at[k][1] - have[k][1]) < 0.0002, k
            if names.index(k) < first:
                assert abs(at[k][0] - have[k][0]) < 0.0002, k
    write_wav('out/tmp/game_sfx.wav', strip)
    size = to_mp3_vbr('out/tmp/game_sfx.wav', AUD + 'sfx.mp3', VBR['sfx'])          # (0.8.47: variable rate; was 160 kbps)
    added = [k for k in at if k not in have]
    au['sfx'] = at
    json.dump(au, open(GEN + 'audio.json', 'w'), separators=(',', ':'))
    print('sfx.mp3: %d clips (new: %s), %.1f s, %.0f KB' % (len(clips), ', '.join(added) or '-', len(strip) / SR, size / 1024))
