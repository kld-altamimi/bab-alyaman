# HISTORICAL: do not run. The strips are kept by add_sfx.py and add_voices.py (this would rebuild them from the build-28
# lists), the music by export_music.py, the rates by core.VBR (0.8.47).
# export_game.py - the sounds the prototype plays, cut the way a game needs them: one shot at a time.
import json, os, shutil, sys
import numpy as np
from core import *
import sfx
import voice as V

SITE = '/home/claude/bab_out/m1/'
AUD = SITE + 'audio/'
GEN = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/gen/'
os.makedirs(AUD, exist_ok=True)
MARK, GAP = 0.05, 0.1


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
    # wrap a little of each end round the other, so the page can loop from pad to the end less pad without a seam
    k = n_of(pad)
    return np.concatenate([y[-k:], y, y[:k]])


one_hmg = pk(sfx.heavy_mg(seed=0, shots=1)[:n_of(0.42)], -4.0)
one_hmg2 = pk(sfx.heavy_mg(seed=5, shots=1)[:n_of(0.42)], -4.0)
clips = [
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
    # build 3: the knife, the coast road, the battery
    ('knife', eff('knife')), ('knife2', eff('knife', 5)),
    ('engine', loopable(eff('engine_loop'))), ('rotor', loopable(eff('rotor_loop'))),
    ('hop', eff('hop')), ('car_land', eff('car_land')), ('crash', eff('crash')), ('ram', eff('ram')), ('ram2', eff('ram', 4)),
    ('horn_shass', eff('horn_shass')), ('horn_truck', eff('horn_truck')), ('boat_horn', eff('boat_horn')),
    ('brake', eff('brake')), ('door_slam', eff('door_slam')),
    ('heavy_shot', eff('heavy_shot')), ('heavy_shot2', eff('heavy_shot', 3)), ('spinup', eff('spinup')),
    ('lock', eff('lock')), ('dive', eff('dive')), ('whistle', eff('whistle')), ('bay', eff('bay')), ('launch', eff('launch')),
    ('smash_crate', eff('smash_crate')), ('smash_bags', eff('smash_bags')),
    ('part_off', eff('part_off')), ('boss_fall', eff('boss_fall')), ('boom_big', eff('explosion_big')), ('strike', eff('strike_bells')),
    # build 5: the campaign map
    ('stamp', eff('stamp')), ('paper', eff('paper')), ('route', eff('route')),
    # build 12: The Coffee Port
    ('door_creak', eff('door_creak')), ('hiss', eff('hiss')), ('steam', eff('steam')), ('bean_spray', eff('bean_spray')),
    ('pop', eff('pop')), ('pour', eff('pour')), ('rev', eff('rev')),
    # build 28: the Souq (add_sfx.py put these on the end of the strip without moving the rest)
    ('sack_burst', eff('sack_burst')), ('thunk', eff('thunk')), ('cannon', eff('cannon')), ('creak', loopable(eff('creak_loop'))),
    ('pigeon', eff('pigeon')),
]
strip, at = sprite(clips)
write_wav('out/tmp/game_sfx.wav', strip)
size = to_mp3('out/tmp/game_sfx.wav', AUD + 'sfx.mp3', 160)
print('sfx.mp3: %d clips, %.1f s, %.0f KB' % (len(clips), len(strip) / SR, size / 1024))

# voices: the same clips as the sound test
VO = dict(np.load('out/voice.npz'))
order = list(V.LINES) + list(V.VOCALS)
# lines written since the sound test: say them now, and keep them
new_lines = [k for k in order if k not in VO]
for k in new_lines:
    if k in V.LINES:
        sp, fx, sub, text, opt = V.LINES[k]
        VO[k] = V.level(fx(V.CAST[sp].say(text, seed=sum(map(ord, k)) % 997, **opt), seed=5))
    else:
        sp, fx, sub, fn = V.VOCALS[k]
        VO[k] = V.level(fx(fn(V.CAST[sp], 7), seed=5), -17.0 if sp != 'guard' else -15.0)
if new_lines:
    np.savez('out/voice.npz', **VO)
    print('new lines:', new_lines)
vstrip, vat = sprite([(k, VO[k]) for k in order])
write_wav('out/tmp/game_voices.wav', vstrip)
vsize = to_mp3('out/tmp/game_voices.wav', AUD + 'voices.mp3', 80)
SPEAKER = {'yazeed': 'YAZEED', 'announcer': 'ANNOUNCER', 'dispatcher': 'DISPATCH', 'grunt': 'RIFLEMAN', 'cook': 'COOK', 'elder': 'ELDER',
           'guard': 'THE GUARD', 'commander': 'COMMANDER', 'salem': 'SALEM', 'bilqis': 'BILQIS', 'arwa': 'ARWA', 'quartermaster': 'QUARTERMASTER',
           'uncle': 'THE UNCLE'}
lines = {}
for k in order:
    inf = V.LINES.get(k) or V.VOCALS.get(k)
    lines[k] = dict(at=vat[k], who=SPEAKER[inf[0]], text=inf[2] if k in V.LINES else '')
print('voices.mp3: %d clips, %.1f s, %.0f KB' % (len(order), len(vstrip) / SR, vsize / 1024))

# music: straight from the sound test
for f in ('music_strait.mp3', 'music_battery.mp3', 'jingle_start.mp3', 'jingle_complete.mp3'):
    shutil.copy('/home/claude/bab_out/sound/audio/' + f, AUD + f)
music = json.load(open('out/music.json'))
man = dict(mark=MARK, loopAt=0.6, lead=0.5, sfx=at, voices=lines,
           music=dict(strait=dict(file='music_strait', seconds=music['music_strait']['seconds']),
                      battery=dict(file='music_battery', seconds=music['music_battery']['seconds']),
                      start=dict(file='jingle_start', seconds=music['jingle_start']['seconds'], landing=2 * 4 * 60.0 / 150),
                      complete=dict(file='jingle_complete', seconds=music['jingle_complete']['seconds'])))
json.dump(man, open(GEN + 'audio.json', 'w'), separators=(',', ':'))
print('wrote audio.json;', {k: v for k, v in list(at.items())[:5]})
print(sorted(os.listdir(AUD)), '%.2f MB' % (sum(os.path.getsize(AUD + f) for f in os.listdir(AUD)) / 1e6))

# the home screen's theme and the map's march (build 9): encoded from out/music_title.npy and out/music_map.npy
# (made by build_menu_music.py) and added to audio.json
import runpy
runpy.run_path('export_menu_music.py', run_name='__main__')
# The Coffee Port's stage theme and the Big Roaster's (build 12): from out/music_mocha.npy and out/music_roaster.npy
runpy.run_path('export_mocha_music.py', run_name='__main__')
# The Souq's stage theme and the Spice Cannon's (build 28): from out/music_souq.npy and out/music_cannon.npy
runpy.run_path('export_souq_music.py', run_name='__main__')
