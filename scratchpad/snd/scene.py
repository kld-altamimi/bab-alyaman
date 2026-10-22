# scene.py - a run-through of the Strait: what one pass through the stage sounds like, start to finish.
# Three layers are mixed over the stage's four sections and kept as three stems that add up to the mix,
# so the page can mute any of them. A cue sheet drives the subtitles and the camera.
import json
import numpy as np
from core import *
import sfx
import voice as V

OUT = 'out/'
SF = dict(np.load(OUT + 'sfx.npz'))
VO = dict(np.load(OUT + 'voice.npz'))
MU = {k: np.load(OUT + k + '.npy') for k in ('music_strait', 'music_battery', 'jingle_start', 'jingle_complete')}

TOTAL = 76.0
BAR, BBAR = 1.6, 1.5              # one bar of the stage theme (150 a minute) and of the boss theme (160)
T_J = 1.8                         # mission start
T_M = T_J + 2 * BAR               # the stage theme comes in on the jingle's landing
T_SW = T_M + 24 * BAR             # 43.4: the barrage lands on the bar line and the theme stops
T_B = 45.0                        # the boss theme
T_X = T_B + 10 * BBAR             # 60.0: the battery goes up on a bar line
T_C = 66.2                        # mission complete

music, amb, fxb, vox = Bus(TOTAL), Bus(TOTAL), Bus(TOTAL), Bus(TOTAL)
cues = []
talk = []

SPEAKER = {'yazeed': 'YAZEED', 'announcer': 'ANNOUNCER', 'dispatcher': 'DISPATCH', 'grunt': 'RIFLEMAN', 'cook': 'COOK',
           'elder': 'ELDER', 'guard': 'THE GUARD', 'commander': 'COMMANDER'}


def fx(t, name=None, gain=1.0, p=0.0, label=None, snd=None):
    y = SF[name] if snd is None else snd
    fxb.put(y, t, gain * 0.8, p)
    if label:
        cues.append(dict(t=round(t, 2), d=round(len(y) / SR, 2), layer='sfx', label=label))


def say(t, key, gain=1.0, who=None):
    y = VO[key]
    vox.put(y, t, gain, 0.0)
    sp, _, sub = V.LINES[key][:3]
    cues.append(dict(t=round(t, 2), d=round(len(y) / SR, 2), layer='voice', who=who or SPEAKER[sp], label=sub))
    talk.append((t, t + len(y) / SR, key))


def noise(t, key, gain=1.0):
    """A yell or a grunt: no subtitle, and the music does not move for it."""
    vox.put(VO[key], t, gain, 0.0)


def tune(t0, name, gain, label, t1=None):
    """Music from t0. With t1 it stops there, on the beat, and the room rings on."""
    x = MU[name]
    if t1 is not None:
        x = x[:n_of(t1 - t0)].copy()
        k = n_of(0.012)
        x[-k:] *= np.linspace(1, 0, k)[:, None]
        m = n_of(0.5)
        seg = x[-m:] * (np.linspace(0, 1, m)[:, None] ** 2)
        music.put(convolve(seg, reverb_ir(1.5, seed=5)) * 0.55 * gain, t1 - 0.5)
    music.put(x, t0, gain)
    cues.append(dict(t=round(t0, 2), d=round((t1 - t0) if t1 else len(x) / SR, 2), layer='music', label=label))


def thud(seed=0):
    n = n_of(0.45)
    t = np.arange(n) / SR
    y = np.sin(TAU * np.cumsum(95 * (42 / 95) ** (t / t[-1])) / SR) * decay(n, 0.3)
    y += filt(white(n, seed), lp(500), hp(80)) * decay(n, 0.12) * 0.8
    y += filt(white(n, seed + 1), bp(1400, 0.7)) * decay(n, 0.05) * 0.25
    return to_peak(fade(soft(y * 1.4, 1.3), 0.001, 0.05), -5.0)


# ------------------------------------------------------------------ the place
fx(0.15, 'skiff', 1.0, -0.5, 'The skiff grounds')
fx(0.75, 'gull', 0.8, 0.55)

# ------------------------------------------------------------------ 1 · landfall
tune(T_J, 'jingle_start', 0.72, 'Mission start')
say(2.3, 'ann_start')
tune(T_M, 'music_strait', 0.6, 'Stage theme: The Strait', t1=T_SW)
fx(5.25, 'jump', 1.2, -0.4)
fx(5.6, 'land', 1.5, -0.35)
fx(5.85, 'steps', 1.3, -0.3)
say(6.6, 'yazeed_sand')
fx(8.9, 'steps', 1.3, -0.25)
fx(9.7, 'pickup_weapon', 1.0, -0.2, 'Weapon crate')
say(10.0, 'ann_hmg')
fx(11.9, 'go_prompt', 0.9, 0.0, 'GO!')
fx(12.2, 'steps', 1.3, -0.2)
fx(12.95, 'steps', 1.3, -0.15)

# ------------------------------------------------------------------ 2 · the fishing camp
say(13.7, 'grunt_alarm')
fx(14.7, 'enemy_rifle', 1.0, 0.45, 'Their rifles')
fx(14.92, 'ricochet', 0.9, -0.3)
fx(15.1, 'enemy_rifle', 0.9, 0.55)
fx(15.17, 'hit_sand', 1.4, -0.2)
fx(15.45, 'heavy_mg', 0.95, -0.25, 'Heavy MG')
fx(15.75, 'hit_body', 1.0, 0.45)
noise(15.8, 'grunt_yelp')
fx(16.1, 'hit_body', 1.0, 0.5)
noise(16.15, 'grunt_scream')
fx(16.6, 'coin', 0.8)
# the doorman: the stream rings off his door and runs dry
fx(17.2, snd=to_peak(sfx.heavy_mg(seed=3, shots=5), -3.0), gain=0.9, p=-0.25)
for i, t in enumerate((17.28, 17.47, 17.66)):
    fx(t, 'door_clang', 1.1, 0.3, 'Rounds on the pickup door' if i == 0 else None)
fx(17.7, 'ricochet', 0.8, 0.6)
fx(17.88, 'tick', 1.6, -0.25)
fx(18.0, 'tick', 1.6, -0.25)
say(18.1, 'ann_pistol')
fx(19.3, 'grenade_throw', 1.6, -0.2, 'Grenade')
fx(19.75, 'grenade_bounce', 1.6, 0.2)
say(19.85, 'grunt_face', who='DOORMAN')
fx(20.55, 'explosion_small', 0.95, 0.3, 'Grenade blast')
fx(21.25, 'door_clang', 0.9, 0.55)
fx(21.3, 'coin', 0.8)
# the bomber, who should not have lit it yet
fx(21.6, 'fuse', 1.5, 0.35, 'Dynamite fuse')
fx(22.0, 'pistol', 1.0, -0.25, 'Sidearm')
fx(22.25, 'pistol', 1.0, -0.25)
fx(22.3, 'hit_body', 1.0, 0.4)
fx(22.45, 'explosion_small', 0.9, 0.4)
noise(22.5, 'grunt_scream', 0.9)
fx(23.2, 'coin', 0.8)
say(23.4, 'yazeed_boat')
# the detained elder on the deckhouse
fx(26.5, 'jump', 1.2, -0.1)
fx(26.85, 'land', 1.5, 0.0)
fx(27.1, 'rope_cut', 1.3, 0.1, 'Rope cut')
fx(27.4, 'freed', 1.0, 0.1, 'Detainee freed')
say(27.8, 'elder_thanks')
fx(30.9, 'pickup_grenades', 1.0, 0.0, 'Grenades')
# the last man behind the sandbags
fx(31.2, 'surrender', 1.0, 0.4, 'Weapon dropped: a capture')
say(31.4, 'grunt_twice')
fx(33.0, 'coin', 0.8)
fx(33.15, 'coin', 0.8)

# ------------------------------------------------------------------ 3 · container beach
fx(33.1, 'enemy_rifle', 0.9, 0.4)
fx(33.25, 'rocket', 0.9, 0.5, 'Their rocket')
fx(34.0, 'explosion_small', 0.85, -0.25)
fx(34.1, 'plate_lost', 1.0, -0.2, 'Armour plate lost')
for t in (34.3, 34.52, 34.74):
    fx(t, 'pistol', 1.0, -0.25)
fx(34.56, 'hit_body', 1.0, 0.45)
fx(34.78, 'hit_body', 1.0, 0.45)
noise(34.8, 'grunt_scream', 0.9)
fx(35.0, 'ladle_pot', 1.0, 0.5, 'Ladle on the pot')
fx(35.3, 'ladle_pot', 0.9, 0.5)
say(35.45, 'cook_cook')
fx(37.0, 'surrender', 0.8, 0.5)
fx(37.15, 'radio_full', 1.1, 0.0, 'Radio bar full')
fx(37.5, 'radio_call', 1.1, 0.0, 'Calling it in')
say(37.8, 'yazeed_call')
say(40.4, 'disp_free')

# ------------------------------------------------------------------ 4 · the battery
for i, (t, p) in enumerate(((T_SW, 0.35), (T_SW + 0.45, 0.6), (T_SW + 1.0, 0.15))):
    fx(t - 0.94, snd=to_peak(sfx.mortar(seed=11 + i * 7), -2.5), gain=1.0 if i == 0 else 0.85, p=p,
       label='Mortar barrage' if i == 0 else None)
noise(T_SW + 0.25, 'grunt_scream', 0.8)
fx(44.75, 'klaxon', 1.0, 0.3, 'Battery alarm')
fx(46.11, 'klaxon', 0.55, 0.3)
tune(T_B, 'music_battery', 0.62, 'Boss theme: Shore Battery', t1=T_X)
say(45.9, 'cmdr_behold')
noise(50.1, 'guard_hmph')
say(50.65, 'guard_leave')
fx(52.6, 'guard_mg', 0.95, 0.35, "The Guard's belt-fed gun")
fx(52.9, 'ricochet', 0.9, -0.4)
fx(53.0, 'hit_sand', 1.4, -0.2)
fx(53.3, 'ricochet', 0.8, -0.1)
fx(53.45, 'hit_sand', 1.4, -0.3)
fx(53.6, 'plate_lost', 1.0, -0.2)
fx(54.2, 'pickup_weapon', 1.0, -0.2)
say(54.45, 'ann_shotgun')
for i, t in enumerate((55.3, 56.1, 56.9)):
    fx(t, 'shotgun', 0.9, -0.2, 'Shotgun' if i == 0 else None)
    fx(t + 0.05, 'hit_body', 1.1, 0.35)
noise(56.98, 'guard_hmph', 1.1)
fx(57.35, snd=thud(3), gain=1.0, p=0.35, label='The Guard goes down')
fx(57.6, 'missile_launch', 0.9, 0.2, 'Missile away')
for t in (58.3, 59.05):
    fx(t, 'shotgun', 0.9, -0.2)
    fx(t + 0.05, 'launcher_hit', 1.0, 0.25, 'Rounds on the launcher' if t < 58.5 else None)
fx(59.5, 'grenade_throw', 1.6, -0.2)
fx(T_X, 'explosion_big', 1.0, 0.2, 'The battery goes up')
fx(60.9, 'explosion_small', 0.55, 0.45)
fx(61.4, 'door_clang', 0.8, -0.3)
fx(61.6, 'explosion_small', 0.4, 0.0)
for t in (62.0, 62.15, 62.3):
    fx(t, 'coin', 0.8)
say(62.5, 'cmdr_surrender')
tune(T_C, 'jingle_complete', 0.75, 'Mission complete')
say(66.7, 'ann_complete')
fx(70.0, 'medal', 1.0, 0.0, 'Medal')
say(71.7, 'yazeed_tea')
fx(73.7, 'gull', 0.7, -0.4)

# ------------------------------------------------------------------ the sea, under all of it
n = n_of(TOTAL)
sea = SF['sea']
reps = int(np.ceil(n / len(sea))) + 1
tile = np.tile(sea, reps)
sea_st = np.stack([tile[:n], tile[n_of(3.1):n_of(3.1) + n]], axis=1)
tt_ = np.arange(n) / SR
sea_env = np.interp(tt_, [0, 0.6, 1.8, 3.0, 6.5, 43.0, 44.5, 59.8, 61.5, 66.0, 67.5, 71.5, 73.6, 76.0], [0, 1.9, 1.9, 1.0, 0.7, 0.7, 0.5, 0.5, 1.3, 1.3, 0.8, 1.0, 1.7, 0.0])
amb.x += sea_st * sea_env[:, None]

# ------------------------------------------------------------------ the music gives way to speech
act = np.zeros(n)
for a, b, k in talk:
    act[n_of(a - 0.05):n_of(b + 0.05)] = 1.0
k = n_of(0.16)
ker = np.hanning(2 * k + 1)
ker /= ker.sum()
act = np.convolve(np.concatenate([np.zeros(k), act, np.zeros(k)]), ker, mode='valid')
duck = 10 ** (-4.0 * act / 20)
music.x *= duck[:, None]


def build(target=-15.0, ceiling=-1.5):
    stems = dict(music=music.x, voice=vox.x, sfx=fxb.x + amb.x)
    stems = {k: filt(v, hp(28)) for k, v in stems.items()}
    mix = sum(stems.values())
    g0 = 10 ** ((target - lufs(mix)) / 20)
    lim, red, curve = limit(mix * g0, ceiling, curve=True)
    # one more pass so the limiter's work does not leave it short of the target
    g1 = 10 ** ((target - lufs(lim)) / 20)
    lim, red, curve = limit(mix * g0 * g1, ceiling, curve=True)
    k = g0 * g1 * curve[:, None]
    stems = {name: v * k for name, v in stems.items()}
    end = np.linspace(1, 0, n_of(0.4))
    for v in stems.values():
        v[-len(end):] *= end[:, None]
    return stems, lim, red


if __name__ == '__main__':
    stems, lim, red = build()
    mix = sum(stems.values())
    print('mix: %.1f LUFS, peak %.1f dB, limiter worked up to %.1f dB' % (lufs(mix), db(np.abs(mix).max()), red))
    for k, v in stems.items():
        print('  %-6s %.1f LUFS, peak %.1f dB' % (k, lufs(v), db(np.abs(v).max())))
    # the voice stem is mono
    assert np.allclose(stems['voice'][:, 0], stems['voice'][:, 1])
    talk.sort()
    for (a, b, k), (a2, b2, k2) in zip(talk, talk[1:]):
        if a2 < b - 0.02:
            print('  voices overlap: %s ends %.2f, %s starts %.2f' % (k, b, k2, a2))
    cues.sort(key=lambda c: c['t'])
    np.save(OUT + 'run_music.npy', stems['music'])
    np.save(OUT + 'run_sfx.npy', stems['sfx'])
    np.save(OUT + 'run_voice.npy', stems['voice'][:, 0])
    np.save(OUT + 'run_mix.npy', mix)
    pan_keys = [[0, 0], [5.2, 0], [12.0, 380], [13.6, 936], [26.0, 1000], [31.0, 1100], [33.0, 1872], [35.0, 2060], [42.0, 2250], [44.2, 2808], [TOTAL, 2808]]
    sections = [[0, 'Landfall'], [13.6, 'The fishing camp'], [33.0, 'Container beach'], [43.4, 'The battery']]
    json.dump(dict(seconds=TOTAL, cues=cues, pan=pan_keys, sections=sections, lufs=round(lufs(mix), 1)), open(OUT + 'run.json', 'w'), indent=1)
    print('%d cues: %d spoken, %d effects, %d music' % (len(cues), sum(c['layer'] == 'voice' for c in cues), sum(c['layer'] == 'sfx' for c in cues), sum(c['layer'] == 'music' for c in cues)))
    for c in cues:
        print('  %6.2f %5.2f %-5s %s%s' % (c['t'], c['d'], c['layer'], (c.get('who', '') + ': ') if c.get('who') else '', c['label']))
