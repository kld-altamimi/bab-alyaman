"""The onboarding reel: «فيديو تعريفي للمنضمّين الجدد», a Zanabeel recruit's whole career in four real lines from the Strait
(live build 0.15.77, filmed by m1rig2.py: run A with the director in dir_a.json (shoot5), run B with a longer hold after the
alarm, dir_c.json (shootB), for the first stage). Four career stages, each a real moment: the alarm, the doorman's «إلا الوجه!»,
«أنا توّني بديت يوم الاثنين!», «أستسلم! مرتين!» (two surrender lines laid on the surrender that fits each stage best; both are the
game's own lines for a surrendering rifleman); then an end card.
Third cut (Khaled, 29 Oct: still too fast): each stage opens on its title for about a second before anyone speaks, plays the line,
then freezes and punches in on the speaker for about 1.3 seconds with the subtitle still up (the game's whoosh and thunk), so
each stage runs 2.7 to 3.7 seconds; the calmer music of the campaign map (112 BPM) instead of the Strait's (150 BPM).
One piece of music (cuts on its beat), the game's effects cross-faded and levelled, the voices clean from the game's voice file,
subtitles in the game's own lettering and order (name to the right).
Usage: python3 edit_onb.py [--x] [--preview]   (--x: the 4:5 cut for X)"""
import json, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

D = '/tmp/claude-0/-home-claude/df6305fd-b1bf-5dfd-a75a-44d8bb54fcc7/scratchpad/'
G = D + 'gc/'
RUNS = {'A': G + 'shoot5/', 'B': G + 'shootB/'}
TX = G + 'text_onb/'
AUD = G + 'build77/audio/'
X = '--x' in sys.argv
PREVIEW = '--preview' in sys.argv
OUT = G + ('out_onb_x/' if X else 'out_onb/')
import os; os.makedirs(OUT, exist_ok=True)
SR, FPS, SPF = 48000, 60, 800
W, H = (1080, 1350) if X else (1080, 1920)
BG = (3, 4, 9)
MASTER, MUSIC, MUSIC_UNDER, SFX, SFX_UNDER, VOICE = 0.85, 0.62, 0.27, 0.62, 0.30, 1.2
BED_START = 0.48                       # music_map's first downbeat; 112 BPM, a beat is 32.175 frames
BEAT = 0.53625 * 60
MUSIC_FILE = 'music_map.mp3'
XF = int(0.06 * SR)

LOGS = {r: json.load(open(d + 'log.json')) for r, d in RUNS.items()}
src = open(G + 'build77/index.html', encoding='utf8').read()
i = src.find('var AUDIO = '); j = src.find(';\n', i); MAN = json.loads(src[i + 12:j])

# ---- the four stages: source frames [a, a + n), the stage's line and where it is laid (source frame), the who and line strips
# framing: z 3 shows 360x216 of the 384x216 world from x0; z 4 shows 270x162 from (x0, 54); pan: x0 keyed on source frames
# each stage: live from source frame a up to fz (exclusive), then the picture holds on frame fz, punched in (x6) on the
# speaker at pc (world pixels), until the stage's end, which falls on the music's beat (beats: the stage's length)
SHOTS = [
    dict(name='hire',   run='B', st='st1', a=110,  fz=224,  beats=6, z=4, x0=104, vid='grunt_alarm',  at=168,  who='who_rifle', line='l_alarm',  pc=(297, 138)),
    dict(name='face',   run='A', st='st2', a=280,  fz=358,  beats=5, z=4, x0=114, vid='grunt_face',   at=335,  who='who_door',  line='l_face',   pc=(312, 136)),
    dict(name='monday', run='A', st='st3', a=1694, fz=1836, beats=7, z=4, x0=114, vid='grunt_monday', at=1762, who='who_rifle', line='l_monday', pc=(240, 138),
         pan=([1694, 1760, 1800, 1846], [114, 112, 90, 74])),
    dict(name='twice',  run='A', st='st4', a=696,  fz=834,  beats=7, z=4, x0=84,  vid='grunt_twice',  at=745,  who='who_rifle', line='l_twice',  pc=(300, 136)),
]
CARD_BEATS = 6
t, nb = 0, 0
for s in SHOTS:
    nb += s['beats']; end = int(round(nb * BEAT))
    s['r'] = t; s['n'] = end - t; s['live'] = s['fz'] - s['a']; s['F'] = s['n'] - s['live']
    assert s['F'] > 40, (s['name'], s['F'])
    t = end
CARD_AT = t
CARD_N = int(round((nb + CARD_BEATS) * BEAT)) - CARD_AT
TOTAL = CARD_AT + CARD_N
print('shots', [(s['name'], s['a'], s['n'], s['r'], 'live', s['live'], 'freeze', s['F']) for s in SHOTS], 'card', CARD_AT, 'total', TOTAL, '=', TOTAL / FPS, 's')

# the lines as laid in the reel: (reel frame, id, opts, shot)
LINES = []
for s in SHOTS:
    LINES.append((s['r'] + s['at'] - s['a'], s['vid'], {}, s))
# the barks the game played over them inside each shot, where and how it played them
for s in SHOTS:
    for k, f, d in LOGS[s['run']]['log']:
        if k != 'voice' or not (isinstance(d[1], dict) and d[1].get('over')): continue
        if s['a'] <= f < s['fz'] - 6: LINES.append((s['r'] + f - s['a'], d[0], d[1], s))
LINES.sort(key=lambda x: x[0])
print('voices', [(f, v) for f, v, o, s in LINES])

# ---------------------------------------------------------------- picture
def strip(n, sc):
    im = Image.open(TX + n + '.png').convert('RGBA'); return im.resize((im.width * sc, im.height * sc), Image.NEAREST)
TM = json.load(open(TX + 'meta.json'))
GAP = TM['_gap'] or 7
def pair(who, line, sc):
    """the game's subtitle in Arabic: the line, a gap, then the speaker's name on its right (read first)"""
    a, b = Image.open(TX + line + '.png').convert('RGBA'), Image.open(TX + who + '.png').convert('RGBA')
    top = min(TM[line]['y0'], TM[who]['y0']); bot = max(TM[line]['y0'] + TM[line]['h'], TM[who]['y0'] + TM[who]['h'])
    im = Image.new('RGBA', (a.width + GAP + b.width, bot - top), (0, 0, 0, 0))
    im.alpha_composite(a, (0, TM[line]['y0'] - top)); im.alpha_composite(b, (a.width + GAP, TM[who]['y0'] - top))
    return im.resize((im.width * sc, im.height * sc), Image.NEAREST)
def scaled_logo(f):
    im = Image.open(D + 'reel/logo.png').convert('RGBA'); return im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
HANDLE = Image.open(D + 'reel/H_0.png').convert('RGBA'); HANDLE = HANDLE.resize((HANDLE.width * 3, HANDLE.height * 3), Image.NEAREST)

if X:
    L = dict(logo=0.62, logo_y=36, hd1_y=176, hd2_y=262, st_y=318, st_h=104, pip_y=432, win_y=474, sub_y=1158,
             card_logo=0.85, card_y=250)
else:
    L = dict(logo=0.78, logo_y=196, hd1_y=388, hd2_y=480, st_y=560, st_h=116, pip_y=690, win_y=748, sub_y=1438,
             card_logo=1.0, card_y=470)
LOGO = scaled_logo(L['logo'])
HD1, HD2 = strip('hd1', 4), strip('hd2', 3)
ST = {s['st']: strip(s['st'], 6) for s in SHOTS}
ST_POP = {s['st']: strip(s['st'], 7) for s in SHOTS}
SUB = {s['name']: pair(s['who'], s['line'], 4 if X else 5) for s in SHOTS}

# the career so far: four squares, the stages done, the one now, the ones to come
ORG, ORG_D, SLATE, INK = (255, 194, 46), (184, 60, 8), (44, 46, 66), (16, 16, 28)
def pips(k):
    P, GP = 8, 6                                       # in game pixels, drawn x4
    im = Image.new('RGBA', (4 * P + 3 * GP, P), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    for n in range(4):
        x = (3 - n) * (P + GP)                         # read right to left: the first stage on the right
        col = ORG if n == k else (ORG_D if n < k else SLATE)
        dr.rectangle((x, 0, x + P - 1, P - 1), fill=INK); dr.rectangle((x + 1, 1, x + P - 2, P - 2), fill=col)
        if n == k: dr.rectangle((x + 2, 1, x + P - 3, 2), fill=(255, 230, 106))
    return im.resize((im.width * 4, im.height * 4), Image.NEAREST)
PIPS = [pips(k) for k in range(4)]

BASE = Image.new('RGBA', (W, H), BG + (255,))
BASE.alpha_composite(LOGO, ((W - LOGO.width) // 2, L['logo_y']))
BASE.alpha_composite(HD1, ((W - HD1.width) // 2, L['hd1_y']))
BASE.alpha_composite(HD2, ((W - HD2.width) // 2, L['hd2_y']))

CARD = Image.new('RGBA', (W, H), BG + (255,))
cl = scaled_logo(L['card_logo']); y = L['card_y']
CARD.alpha_composite(cl, ((W - cl.width) // 2, y)); y += cl.height + (64 if not X else 48)
for n, sc, gap in [('e_play', 5, 30), ('e_new', 4, 46)]:
    im = strip(n, sc); CARD.alpha_composite(im, ((W - im.width) // 2, y)); y += im.height + gap
CARD.alpha_composite(HANDLE, ((W - HANDLE.width) // 2, y))
CARD_RGB = CARD.convert('RGB')

def window(s, k):
    im = Image.open(RUNS[s['run']] + 'f/%06d.png' % k).convert('RGB')
    x0 = int(round(np.interp(k, *s['pan']))) if 'pan' in s else s['x0']
    if s['z'] == 4: return im.crop((x0, 54, x0 + 270, 216)).resize((1080, 648), Image.NEAREST)
    return im.crop((x0, 0, x0 + 360, 216)).resize((1080, 648), Image.NEAREST)
def punch(s):
    """the held frame, x6 on the speaker"""
    im = Image.open(RUNS[s['run']] + 'f/%06d.png' % s['fz']).convert('RGB')
    cx, cy = s['pc']; x0 = max(0, min(384 - 180, cx - 90)); y0 = max(0, min(216 - 108, cy - 54))
    return im.crop((x0, y0, x0 + 180, y0 + 108)).resize((1080, 648), Image.NEAREST)
PUNCH = {}

def frame(t):
    if t >= CARD_AT:
        k = t - CARD_AT
        if k < 6: return Image.blend(frame(CARD_AT - 1), CARD_RGB, (k + 1) / 7)
        return CARD_RGB
    s = next(s for s in SHOTS if s['r'] <= t < s['r'] + s['n'])
    k = s['a'] + t - s['r']
    im = BASE.copy()
    st = (ST_POP if t - s['r'] < 3 else ST)[s['st']]                 # the stage's title lands with a little pop
    im.alpha_composite(st, ((W - st.width) // 2, L['st_y'] + (L['st_h'] - st.height) // 2))
    p = PIPS[SHOTS.index(s)]; im.alpha_composite(p, ((W - p.width) // 2, L['pip_y']))
    if k < s['fz']: im.paste(window(s, k), (0, L['win_y']))
    else:
        if s['name'] not in PUNCH: PUNCH[s['name']] = punch(s)
        im.paste(PUNCH[s['name']], (0, L['win_y']))
    a = s['r'] + s['at'] - s['a']
    if a <= t:                                                       # up from the line to the end of the stage
        sb = SUB[s['name']]; im.alpha_composite(sb, ((W - sb.width) // 2, L['sub_y']))
    return im.convert('RGB')

if PREVIEW:
    ks = []
    for s in SHOTS:
        a = s['r'] + s['at'] - s['a']
        ks += [s['r'] + 1, s['r'] + 30, a + 10, s['r'] + s['live'] - 1, s['r'] + s['live'] + 20]
    ks += [CARD_AT + 3, CARD_AT + 60]
    ims = [frame(k).resize((W // 4, H // 4)) for k in ks]
    cols = 5; S = Image.new('RGB', (cols * (W // 4), ((len(ims) + cols - 1) // cols) * (H // 4)))
    for n, im in enumerate(ims): S.paste(im, ((n % cols) * (W // 4), (n // cols) * (H // 4)))
    S.save(OUT + 'preview.png')
    frame(SHOTS[2]['r'] + SHOTS[2]['at'] - SHOTS[2]['a'] + 20).save(OUT + 'f_monday.png'); CARD_RGB.save(OUT + 'f_card.png')
    print('preview at', ks); sys.exit(0)

# ---------------------------------------------------------------- sound
def decode(path, start=0.0, dur=None, ch=2):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(start), '-i', path]
    if dur: cmd += ['-t', str(dur)]
    cmd += ['-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, ch).copy()
N = TOTAL * SPF
tt = np.arange(N) / SR
GAMES = {r: np.fromfile(d + 'game.pcm', dtype='<i2').reshape(-1, 2).astype(np.float32) / 32768.0 for r, d in RUNS.items()}
# effects: each shot with a little either side, cross-faded (equal power) at every cut; into the card over 0.4 s
fx = np.zeros((N, 2), np.float32)
for n, s in enumerate(SHOTS):
    a, b = s['a'] * SPF - XF, s['fz'] * SPF + int(0.04 * SR)
    seg = GAMES[s['run']][a:b].copy(); Lg = len(seg)
    ramp = np.sin(np.linspace(0, np.pi / 2, 2 * XF))[:, None]
    seg[:2 * XF] *= ramp
    fo = int(0.08 * SR); seg[-fo:] *= np.linspace(1, 0, fo)[:, None]       # the game holds its breath with the picture
    p = s['r'] * SPF - XF
    lo, hi = max(0, p), min(N, p + Lg)
    fx[lo:hi] += seg[lo - p:hi - p]
# a slow leveller: loud gunfire down (up to 8 dB), quiet moments up a little (up to 3 dB)
FX_TARGET, FX_CUT, FX_LIFT = -22.0, -9.0, 3.0
win = int(0.2 * SR); pw = np.convolve((fx ** 2).mean(axis=1), np.ones(win) / win, 'same')
want = np.clip(FX_TARGET - 10 * np.log10(pw + 1e-10), FX_CUT, FX_LIFT)
gl, cur = np.empty(N, np.float32), 0.0
att, rel = 1 - np.exp(-1 / (0.05 * SR)), 1 - np.exp(-1 / (0.4 * SR))
for k in range(N):
    tg = want[k]; cur += (tg - cur) * (att if tg < cur else rel); gl[k] = cur
fx *= (10 ** (gl / 20))[:, None]

# voices, from the game's own voice file
vox = decode(AUD + 'voices.mp3', ch=1)[:, 0]
shift = int(np.argmax(np.abs(vox[:int(0.3 * SR)]) > 0.15)) / SR - MAN['mark']
def line_audio(vid, o):
    at0, dur = MAN['voices'][vid]['at']
    s = vox[int((at0 + shift) * SR):int((at0 + shift + dur + 0.01) * SR)].copy()
    rate = o.get('rate') or 1
    if rate != 1:
        n2 = int(len(s) / rate); s = np.interp(np.arange(n2) * rate, np.arange(len(s)), s).astype(np.float32)
    gain = (1 if o.get('gain') is None else o['gain']) * VOICE * MASTER
    pan = o.get('pan') or 0
    pan = max(-1, min(1, pan)); th = (pan + 1) * np.pi / 4
    return np.stack([s * gain * np.cos(th), s * gain * np.sin(th)], axis=1)
vo = np.zeros((N, 2), np.float32)
duck = []
for f, vid, o, s in LINES:
    x = line_audio(vid, o)
    p = f * SPF
    end_cut = ((s['r'] + s['n']) if not o.get('over') else (s['r'] + s['live'])) * SPF + int(0.15 * SR)   # barks stop with the picture
    x = x[:max(0, min(len(x), end_cut - p))]
    if p + len(x) >= end_cut - int(0.15 * SR):
        fo = min(len(x), int(0.12 * SR)); x[-fo:] *= np.linspace(1, 0, fo)[:, None]
    vo[p:p + len(x)] += x[:N - p]
    if not o.get('over'): duck.append((f, f + int(round(MAN['voices'][vid]['at'][1] * FPS))))
# the effects step back under each line, as the game's mix does
g = np.ones(N, np.float32)
for a, b in duck: g[(tt >= a / FPS) & (tt < b / FPS)] = SFX_UNDER / SFX
gs, cur = np.empty(N, np.float32), 1.0
for k in range(N):
    tg = g[k]; cur += (tg - cur) * (1 - np.exp(-1 / ((0.04 if tg < cur else 0.15) * SR))); gs[k] = cur
fx *= gs[:, None]

# the punch-in on each held frame: the game's own whoosh and thunk
SFXF = decode(AUD + 'sfx.mp3')
def put_sfx(name, at_frame, db):
    a0, d0 = MAN['sfx'][name]; x = SFXF[int(a0 * SR):int((a0 + d0) * SR)].copy() * (10 ** (db / 20)) * MASTER
    p = int(at_frame * SPF); e = min(N, p + len(x)); fx[p:e] += x[:e - p]
for s in SHOTS:
    put_sfx('whoosh', s['r'] + s['live'] - 9, -16); put_sfx('thunk', s['r'] + s['live'], -9)

# music: the campaign map's theme, one piece from its first downbeat to the end, down under every line, out at the end
bed = decode(AUD + MUSIC_FILE, BED_START, TOTAL / FPS + 0.3)[:N]
music = np.zeros((N, 2), np.float32); music[:len(bed)] = bed
target = np.ones(N, np.float32)
for a, b in duck: target[(tt >= a / FPS) & (tt < b / FPS)] = MUSIC_UNDER / MUSIC
target[tt >= CARD_AT / FPS] = 1.15                                   # up a little on the card
mg, cur = np.empty(N, np.float32), 1.0
da, ua = 1 - np.exp(-1 / (0.05 * SR)), 1 - np.exp(-1 / (0.18 * SR))
for k in range(N):
    tg = target[k]; cur += (tg - cur) * (da if tg < cur else ua); mg[k] = cur
music *= (mg * MUSIC * MASTER)[:, None]
fo = int(1.1 * SR); music[-fo:] *= (np.linspace(1, 0, fo) ** 1.6)[:, None]

mix = fx + vo + music
# a look-ahead peak limiter (5 ms ahead, 80 ms release), so a close explosion can't push the normalised sound over the top
from scipy.ndimage import minimum_filter1d
LIM = 0.33
pk = np.abs(mix).max(axis=1)
gl = minimum_filter1d(np.minimum(1.0, LIM / np.maximum(pk, 1e-9)), size=2 * int(0.005 * SR) + 1)
gl = np.concatenate([gl[int(0.005 * SR):], np.ones(int(0.005 * SR), np.float32)])        # lead the peak by 5 ms
sm, cur, rl = np.empty(N, np.float32), 1.0, 1 - np.exp(-1 / (0.08 * SR))
for k in range(N):
    cur = gl[k] if gl[k] < cur else cur + (gl[k] - cur) * rl; sm[k] = cur
mix *= sm[:, None]
print('limiter: deepest cut %.1f dB' % (20 * np.log10(sm.min())))
mix.astype('<f4').tofile(OUT + 'mix.f32')
for nm, arr in (('fx', fx), ('vo', vo), ('music', music)): arr.astype('<f4').tofile(OUT + nm + '.f32')
print('mix peak', round(float(np.abs(mix).max()), 3))
p1 = subprocess.run(['ffmpeg', '-v', 'info', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', OUT + 'mix.f32', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
js = json.loads(p1[p1.rfind('{'):p1.rfind('}') + 1])
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:"
      f"measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', OUT + 'mix.f32', '-af', af, '-ar', str(SR), OUT + 'sound.wav'], check=True)
print('sound done', js['input_i'])
if '--audio-only' in sys.argv: sys.exit(0)

NAME = 'bab-alyemen-onboarding' + ('-x' if X else '') + '.mp4'
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-i', OUT + 'sound.wav', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
                        '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', OUT + NAME], stdin=subprocess.PIPE)
for t in range(TOTAL): enc.stdin.write(frame(t).tobytes())
enc.stdin.close(); enc.wait()
json.dump({'shots': [{k: v for k, v in s.items()} for s in SHOTS], 'lines': [(f, v) for f, v, o, s in LINES], 'card': CARD_AT, 'total': TOTAL, 'loudness_in': js},
          open(OUT + 'edit.json', 'w'), ensure_ascii=False, indent=1)
print('done', OUT + NAME)
