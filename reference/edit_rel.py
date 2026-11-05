"""Ibb's release reel, "Off air": Brigadier Breaking («العميد عاجل») never stops talking until Yazeed shoots his microphone.
Filmed from the live game, 0.17.95 (ibbrig.py): run R from the terraces with Yazeed kept back from the rally's chairs so
statement D plays through (shootR); run F from Sumara pass, Yazeed untouchable from the Spokesman's entrance and holding
his fire for two seconds at the last podium so the question «ما زلنا على الهواء؟» is heard whole (shootF).
Four shots on the beat of his theme (144 BPM, a beat is 25 frames): the rally («وقد بدأت العملية.» «وانتهت.»), the first
microphone shot («تعز ما زالت بأيدينا.» → «ماذا؟ ارفع صوتك!»), the last podium in the dark («ما زلنا على الهواء؟»), the
catch: the last shot («ماذا؟ ارفع صوتك!»), his music stops as the game's does, the cable winds him up, he goes over, and
«انقطع البث!» as the game's banner. Then the end card with Ibb's own theme.
The game's sound as filmed (effects, voices and his speech, its own ducking), his theme laid under it and ducked under his
lines; subtitles in the game's lettering and order (name on the right). Usage: python3 edit_rel.py [--x] [--preview]"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image

D = '/tmp/claude-0/-home-claude/df6305fd-b1bf-5dfd-a75a-44d8bb54fcc7/scratchpad/'
G = D + 'ibbr/'
RUNS = {'R': G + 'shootR/', 'F': G + 'shootF/'}
TX = G + 'text/'
AUD = D + 'ibb95/audio/'
X = '--x' in sys.argv
PREVIEW = '--preview' in sys.argv
OUT = G + ('out_x/' if X else 'out/')
os.makedirs(OUT, exist_ok=True)
SR, FPS, SPF = 48000, 60, 800
W, H = (1080, 1350) if X else (1080, 1920)
BG = (3, 4, 9)
MASTER, MUSIC, MUSIC_UNDER = 0.85, 0.50, 0.24
BEAT = 25                                  # music_spokesman: 144 BPM from 0.08 s

LOGS = {r: json.load(open(d + 'log.json')) for r, d in RUNS.items()}
src = open(D + 'ibb95/index.html', encoding='utf8').read()
i = src.find('var AUDIO = '); j = src.find(';\n', i); MAN = json.loads(src[i + 12:j])
SPEECH = MAN['speech']['ibb']['lines']

# ---- the shots: run, first source frame, length in beats, the crop (x0, y0 of 270x162 at x4)
SHOTS = [
    dict(name='rally', run='R', a=2596, beats=11, x0=100, y0=0),     # «وقد بدأت العملية.» … «وانتهت.»
    dict(name='cut1',  run='F', a=2104, beats=8,  x0=20,  y0=0),     # «تعز ما زالت بأيدينا.» → the shot → «ماذا؟ ارفع صوتك!»
    dict(name='last',  run='F', a=2870, beats=8,  x0=114, y0=0),     # the lights go out; «ما زلنا على الهواء؟» by torchlight
    dict(name='fall',  run='F', a=3380, beats=14, x0=114, y0=0),     # the last shot, his music stops, the cable, «انقطع البث!»
]
CARD_N = 210
t = 0
for s in SHOTS:
    s['n'] = s['beats'] * BEAT; s['r'] = t; t += s['n']
CARD_AT = t
TOTAL = CARD_AT + CARD_N
def reel(s, f): return s['r'] + f - s['a']
def ev_at(run, typ, **kw):
    for k, f, d in LOGS[run]['log']:
        if k == 'evx' and d.get('t') == typ and all(d.get(a) == b for a, b in kw.items()): return f
    return None
FALL = SHOTS[3]
OFFAIR = ev_at('F', 'boss_dead')                       # the game's banner: «انقطع البث!» for 170 frames
DYING = ev_at('F', 'boss_dying')                       # his music stops (0.6 s fade, as the game's)
print('shots', [(s['name'], s['run'], s['a'], s['n'], s['r']) for s in SHOTS], 'card', CARD_AT, 'total', TOTAL, TOTAL / FPS, 's; off air at src', OFFAIR, 'dying', DYING)

# ---- subtitles: what the game showed (its own log), inside each shot
LINE = {'وقد بدأت العملية.': 'l_d5', 'وانتهت.': 'l_d6', 'تعز ما زالت بأيدينا.': 'l_a7', 'ماذا؟ ارفع صوتك!': 'l_what',
        'ما زلنا على الهواء؟': 'l_a11', 'انتهى البيان.': 'l_end', 'يلّا.': 'l_yalla'}
WHO = {'العميد عاجل': 'who_brig', 'يزيد': 'who_yazeed'}
SUBS = []
for s in SHOTS:
    subs = LOGS[s['run']]['subs']
    for n, (f, txt) in enumerate(subs):
        end = subs[n + 1][0] if n + 1 < len(subs) else 10 ** 9
        a, b = max(f, s['a']), min(end, s['a'] + s['n'])
        if b - a < 12 or not txt: continue                   # (the tail of a line cut off as a shot starts: not shown)
        who, line = txt.split('|', 1)
        assert line in LINE, (s['name'], f, txt)
        SUBS.append((reel(s, a), reel(s, b), who, line))
print('subtitles', [(a, b, l) for a, b, w, l in SUBS])

# ---------------------------------------------------------------- picture
TM = json.load(open(TX + 'meta.json'))
GAP = TM['_gap'] or 7
def strip(n, sc):
    im = Image.open(TX + n + '.png').convert('RGBA'); return im.resize((im.width * sc, im.height * sc), Image.NEAREST)
def pair(who, line, sc):
    a, b = Image.open(TX + line + '.png').convert('RGBA'), Image.open(TX + who + '.png').convert('RGBA')
    top = min(TM[line]['y0'], TM[who]['y0']); bot = max(TM[line]['y0'] + TM[line]['h'], TM[who]['y0'] + TM[who]['h'])
    im = Image.new('RGBA', (a.width + GAP + b.width, bot - top), (0, 0, 0, 0))
    im.alpha_composite(a, (0, TM[line]['y0'] - top)); im.alpha_composite(b, (a.width + GAP, TM[who]['y0'] - top))
    return im.resize((im.width * sc, im.height * sc), Image.NEAREST)
def scaled_logo(f):
    im = Image.open(D + 'reel/logo.png').convert('RGBA'); return im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
def row(parts, gap):
    w = sum(p.width for p in parts) + gap * (len(parts) - 1); h = max(p.height for p in parts)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); x = 0
    for p in parts: im.alpha_composite(p, (x, (h - p.height) // 2)); x += p.width + gap
    return im
HANDLE = Image.open(D + 'reel/H_0.png').convert('RGBA'); HANDLE = HANDLE.resize((HANDLE.width * 3, HANDLE.height * 3), Image.NEAREST)
SUBIMG = {(w, l): pair(WHO[w], LINE[l], 4 if X else 5) for a, b, w, l in SUBS}
if X:
    L = dict(logo=0.62, logo_y=40, head_y=196, win_y=330, sub_y=1020, card_logo=0.85, card_y=220)
else:
    L = dict(logo=0.82, logo_y=230, head_y=452, win_y=600, sub_y=1300, card_logo=1.0, card_y=430)
LOGO = scaled_logo(L['logo'])
HEAD = row([strip('h_now', 4), strip('h_m4', 4)], 40)            # read right to left: «المهمة 4: إب» then «متاحة الآن»
BASE = Image.new('RGBA', (W, H), BG + (255,))
BASE.alpha_composite(LOGO, ((W - LOGO.width) // 2, L['logo_y']))
BASE.alpha_composite(HEAD, ((W - HEAD.width) // 2, L['head_y']))

CARD = Image.new('RGBA', (W, H), BG + (255,))
cl = scaled_logo(L['card_logo']); y = L['card_y']
CARD.alpha_composite(cl, ((W - cl.width) // 2, y)); y += cl.height + (56 if not X else 40)
for n, sc, gap in [('h_m4', 6, 18), ('h_valleys', 5, 30), ('h_now', 6, 60), ('e_play', 4, 34)]:
    im = strip(n, sc); CARD.alpha_composite(im, ((W - im.width) // 2, y)); y += im.height + gap
CARD.alpha_composite(HANDLE, ((W - HANDLE.width) // 2, y))
CARD_RGB = CARD.convert('RGB')

# the game's banner, drawn where the game draws it: centred at x = W/2 of the world (192), the text's draw y = 84
BOFF = Image.open(TX + 'b_off.png').convert('RGBA')
def banner_on(k):
    """the game's rule: steady until 24 frames before its end, then blinking every 4 frames"""
    t = k - OFFAIR
    if OFFAIR is None or t < 0 or t > 170: return False
    return t < 170 - 24 or (t >> 2) % 2 == 1

BOFF4 = BOFF.resize((BOFF.width * 4, BOFF.height * 4), Image.NEAREST)
def window(s, k):
    im = Image.open(RUNS[s['run']] + 'f/%06d.png' % k).convert('RGB')
    x0, y0 = s['x0'], s['y0']
    w = im.crop((x0, y0, x0 + 270, y0 + 162)).resize((1080, 648), Image.NEAREST)
    if s['name'] == 'fall' and banner_on(k):
        # the game's banner at the game's own size (x4 here), across the top of the picture as on a screen, clear of the men
        w = w.convert('RGBA'); w.alpha_composite(BOFF4, ((1080 - BOFF4.width) // 2, 26)); w = w.convert('RGB')
    return w

def frame(t):
    if t >= CARD_AT:
        k = t - CARD_AT
        if k < 8: return Image.blend(frame(CARD_AT - 1), CARD_RGB, (k + 1) / 9)
        return CARD_RGB
    s = next(s for s in SHOTS if s['r'] <= t < s['r'] + s['n'])
    k = s['a'] + t - s['r']
    im = BASE.copy()
    im.paste(window(s, k), (0, L['win_y']))
    for a, b, w, l in SUBS:
        if a <= t < b:
            sb = SUBIMG[(w, l)]; im.alpha_composite(sb, ((W - sb.width) // 2, L['sub_y']))
    return im.convert('RGB')

if PREVIEW:
    ks = []
    for s in SHOTS: ks += [s['r'] + 2, s['r'] + s['n'] // 3, s['r'] + 2 * s['n'] // 3, s['r'] + s['n'] - 2]
    ks += [a + 12 for a, b, w, l in SUBS] + [reel(FALL, OFFAIR) + 20, CARD_AT + 60]
    ks = sorted(set(ks))
    ims = [frame(k).resize((W // 4, H // 4)) for k in ks]
    cols = 8; S = Image.new('RGB', (cols * (W // 4), ((len(ims) + cols - 1) // cols) * (H // 4)))
    for n, im in enumerate(ims): S.paste(im, ((n % cols) * (W // 4), (n // cols) * (H // 4)))
    S.save(OUT + 'preview.png'); frame(reel(FALL, OFFAIR) + 30).save(OUT + 'f_offair.png'); CARD_RGB.save(OUT + 'f_card.png')
    print('preview at', ks); sys.exit(0)

# ---------------------------------------------------------------- sound
def decode(path, start=0.0, dur=None, ch=2):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(start), '-i', path]
    if dur: cmd += ['-t', str(dur)]
    cmd += ['-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, ch).copy()
N = TOTAL * SPF
tt = np.arange(N) / SR
XF = int(0.05 * SR)
GAMES = {r: np.fromfile(d + 'game.pcm', dtype='<i2').reshape(-1, 2).astype(np.float32) / 32768.0 for r, d in RUNS.items()}
game = np.zeros((N, 2), np.float32)
for n, s in enumerate(SHOTS):
    a, b = s['a'] * SPF - XF, (s['a'] + s['n']) * SPF + XF
    seg = GAMES[s['run']][a:b].copy()
    ramp = np.sin(np.linspace(0, np.pi / 2, 2 * XF))[:, None]
    seg[:2 * XF] *= ramp; seg[-2 * XF:] *= ramp[::-1]
    if n == len(SHOTS) - 1:
        fo = int(0.5 * SR); seg[-fo:] *= np.linspace(1, 0, fo)[:, None]
    p = s['r'] * SPF - XF
    lo, hi = max(0, p), min(N, p + len(seg))
    game[lo:hi] += seg[lo - p:hi - p]
# a gentle leveller on the game's own mix (it already ducks its effects under every line): loud stretches down (up to 6 dB),
# quiet ones up a little (up to 2 dB)
TARGET, CUT, LIFT = -19.0, -6.0, 2.0
win = int(0.25 * SR); pw = np.convolve((game ** 2).mean(axis=1), np.ones(win) / win, 'same')
want = np.clip(TARGET - 10 * np.log10(pw + 1e-10), CUT, LIFT)
gl, cur = np.empty(N, np.float32), 0.0
att, rel = 1 - np.exp(-1 / (0.08 * SR)), 1 - np.exp(-1 / (0.5 * SR))
for k in range(N):
    tg = want[k]; cur += (tg - cur) * (att if tg < cur else rel); gl[k] = cur
game *= (10 ** (gl / 20))[:, None]

# his lines (the game's own log): the music steps down under each, as the game's does
duck = []
for s in SHOTS:
    for k, f, d in LOGS[s['run']]['log']:
        if k != 'voice' or (isinstance(d[1], dict) and d[1].get('over')): continue
        v = SPEECH.get(d[0]) or MAN['voices'].get(d[0])
        if not v: continue
        a, b = f, f + int(round(v['at'][1] * FPS))
        a2, b2 = max(a, s['a']), min(b, s['a'] + s['n'])
        if b2 > a2: duck.append((reel(s, a2), reel(s, b2)))
# his theme, from its first beat, under the four shots; it stops on the last shot (0.6 s), as the game's does
stop_at = reel(FALL, DYING)
bed = decode(AUD + 'music_spokesman.mp3', 0.08, stop_at / FPS + 1.0)
music = np.zeros((N, 2), np.float32); m = min(len(bed), N); music[:m] = bed[:m]
target = np.ones(N, np.float32)
for a, b in duck: target[(tt >= a / FPS) & (tt < b / FPS)] = MUSIC_UNDER / MUSIC
mg, cur = np.empty(N, np.float32), 1.0
da, ua = 1 - np.exp(-1 / (0.05 * SR)), 1 - np.exp(-1 / (0.2 * SR))
for k in range(N):
    tg = target[k]; cur += (tg - cur) * (da if tg < cur else ua); mg[k] = cur
music *= (mg * MUSIC * MASTER)[:, None]
s0 = stop_at * SPF; fo = int(0.6 * SR)
music[s0:s0 + fo] *= np.linspace(1, 0, fo)[:, None]; music[s0 + fo:] = 0
# the end card: Ibb's own theme comes in
card = decode(AUD + 'music_ibb.mp3', 4.82, CARD_N / FPS + 0.2)            # (from a beat in its fuller part)
c0 = CARD_AT * SPF - int(0.15 * SR); cn = min(len(card), N - c0)
cm = card[:cn] * MUSIC * MASTER * 1.6
fi = int(0.25 * SR); cm[:fi] *= np.linspace(0, 1, fi)[:, None]
fo2 = int(1.2 * SR); cm[-fo2:] *= (np.linspace(1, 0, fo2) ** 1.5)[:, None]
music[c0:c0 + cn] += cm

mix = game + music
fi0 = int(0.02 * SR); mix[:fi0] *= np.linspace(0, 1, fi0)[:, None]          # no click on the first beat
from scipy.ndimage import minimum_filter1d
LIM = 0.35
pk = np.abs(mix).max(axis=1)
g2 = minimum_filter1d(np.minimum(1.0, LIM / np.maximum(pk, 1e-9)), size=2 * int(0.005 * SR) + 1)
g2 = np.concatenate([g2[int(0.005 * SR):], np.ones(int(0.005 * SR), np.float32)])
sm, cur, rl = np.empty(N, np.float32), 1.0, 1 - np.exp(-1 / (0.08 * SR))
for k in range(N):
    cur = g2[k] if g2[k] < cur else cur + (g2[k] - cur) * rl; sm[k] = cur
mix *= sm[:, None]
print('limiter: deepest cut %.1f dB' % (20 * np.log10(sm.min())))
mix.astype('<f4').tofile(OUT + 'mix.f32')
for nm, arr in (('game', game), ('music', music)): arr.astype('<f4').tofile(OUT + nm + '.f32')
p1 = subprocess.run(['ffmpeg', '-v', 'info', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', OUT + 'mix.f32', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
js = json.loads(p1[p1.rfind('{'):p1.rfind('}') + 1])
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:"
      f"measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', OUT + 'mix.f32', '-af', af + ',alimiter=limit=0.79:attack=2:release=60:level=disabled', '-ar', str(SR), OUT + 'sound.wav'], check=True)
print('sound done', js['input_i'])
if '--audio-only' in sys.argv: sys.exit(0)

NAME = 'bab-alyemen-ibb-release' + ('-x' if X else '') + '.mp4'
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-i', OUT + 'sound.wav', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
                        # (the feedback's 880 Hz tone makes the AAC encoder overshoot: a 16 kHz low-pass, a limiter, 256k)
                        '-af', 'volume=-1.5dB,lowpass=f=16000,alimiter=limit=0.70:attack=1:release=50:level=disabled',
                        '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', OUT + NAME], stdin=subprocess.PIPE)
for t in range(TOTAL): enc.stdin.write(frame(t).tobytes())
enc.stdin.close(); enc.wait()
json.dump({'shots': SHOTS, 'subs': SUBS, 'duck': duck, 'card': CARD_AT, 'total': TOTAL, 'offair': OFFAIR, 'dying': DYING, 'loudness_in': js},
          open(OUT + 'edit.json', 'w'), ensure_ascii=False, indent=1)
print('done', OUT + NAME)
