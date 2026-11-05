"""Ibb's release reel, the tour: four moments of Mission 4 in the order the mission plays them, no boss fight and nothing
from the ending. Filmed from the live game, 0.17.95 (ibbrig.py, run T: Yazeed played by the bot from the start of the
mission with no holds and no shield, firing only when something is on screen to fire at).
  1. the drop-off: Brigadier Breaking on the billboard («بيان مهم.» «ندعو المدعو يزيد…»), Salem «ما أسوق في هذا الضجيج.»
  2. Jibla's school: the classes open, Yazeed «روح البيت. وطمّن أمك.»
  3. the green valleys, by the waterfall: the screen says «تعز ما زالت بأيدينا.» … «في معظمها.»
  4. the rally on the terraces: Yazeed in the crowd «بيريه حلوة.», the Brigadier jumps out from behind the podium with no
     trousers and runs for the pass (the fight itself is left for the player).
Then the end card. Ibb's own theme (60 BPM, a beat on every second from 0.82 s) from the first frame to the last, ducked
under the lines; cuts on its beats and the card on a bar line. The game's own sound as filmed under it.
Subtitles: the game's own, from its log, in its lettering and order (name on the right).
Usage: python3 edit_tour.py [--x] [--preview] [--audio-only]"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image

D = '/tmp/claude-0/-home-claude/df6305fd-b1bf-5dfd-a75a-44d8bb54fcc7/scratchpad/'
G = D + 'ibbr/'
RUN = G + 'shootT/'
TX = G + 'text/'
AUD = D + 'ibb95/audio/'
X = '--x' in sys.argv
PREVIEW = '--preview' in sys.argv
OUT = G + ('tour_x/' if X else 'tour/')
os.makedirs(OUT, exist_ok=True)
SR, FPS, SPF = 48000, 60, 800
W, H = (1080, 1350) if X else (1080, 1920)
BG = (3, 4, 9)
MASTER, MUSIC, MUSIC_UNDER = 0.85, 0.62, 0.38     # (the game's own: music 0.62, 0.38 under a line, master 0.85)
M0 = 0.82                                   # music_ibb: its first beat; from here a beat is exactly 60 frames

LOG = json.load(open(RUN + 'log.json'))
src = open(D + 'ibb95/index.html', encoding='utf8').read()
i = src.find('var AUDIO = '); j = src.find(';\n', i); MAN = json.loads(src[i + 12:j])
SPEECH = MAN['speech']['ibb']['lines']

# ---- the shots: first source frame, length (frames), the crop (x0, y0 of 270x162 at x4, or 360x216 at x3)
SHOTS = [
    dict(name='open',   a=1,    n=310, x0=0,   y0=36),     # the billboard, the 4x4 pulls up, Salem won't drive in this noise
                                                           # (out before «وإن أي تقدّم…» begins)
    dict(name='school', a=2980, n=170, x0=10,  y0=40, xi=0.005),   # the classes open, «روح البيت. وطمّن أمك.» (in on his
                                                           # first word, so the screen's line he cuts off is not heard; out before the next)
    dict(name='valley', a=5207, n=240, x0=12,  y0=0, sc=3),  # the waterfall, the screen: «تعز ما زالت بأيدينا.» … «في معظمها.»
                                                             # (wide, x3: the men he shoots at, behind him and ahead, stay in)
    dict(name='rally',  a=6656, n=240, x0=104, y0=0),      # «بيريه حلوة.», the jump, the run for the pass
]
CARD_N = 240
t = 0
for s in SHOTS:
    s['r'] = t; t += s['n']
CARD_AT = t
TOTAL = CARD_AT + CARD_N
def reel(s, f): return s['r'] + f - s['a']
print('shots', [(s['name'], s['a'], s['n'], s['r']) for s in SHOTS], 'card', CARD_AT, 'total', TOTAL, TOTAL / FPS, 's')
for s in SHOTS:
    for f in range(s['a'], s['a'] + s['n']):
        assert os.path.exists(RUN + 'f/%06d.png' % f), (s['name'], f)

# ---- subtitles: what the game showed (its own log), inside each shot
LINE = {'بيان مهم.': ['l_important'], 'ندعو المدعو يزيد إلى الهدنة وضبط النفس.': ['l_c2a', 'l_c2b'],
        'ما أسوق في هذا الضجيج.': ['l_salem'], 'روح البيت. وطمّن أمك.': ['l_home'], 'تعز ما زالت بأيدينا.': ['l_a7'],
        'في معظمها.': ['l_a8'], 'بيريه حلوة.': ['l_beret'], 'يلّا.': ['l_yalla']}
WHO = {'العميد عاجل': 'who_brig', 'يزيد': 'who_yazeed', 'سالم': 'who_salem'}
SUBS = []
subs = LOG['subs']
for s in SHOTS:
    for n, (f, txt) in enumerate(subs):
        end = subs[n + 1][0] if n + 1 < len(subs) else 10 ** 9
        a, b = max(f, s['a']), min(end, s['a'] + s['n'])
        if b - a < 15 or not txt: continue                   # (a line's last moments as a shot starts: not shown)
        who, line = txt.split('|', 1)
        assert line in LINE, (s['name'], f, txt)
        SUBS.append((reel(s, a), reel(s, b), who, line))
print('subtitles', [(a, b, w, l) for a, b, w, l in SUBS])

# ---------------------------------------------------------------- picture
TM = json.load(open(TX + 'meta.json'))
GAP = TM['_gap'] or 7
def strip(n, sc):
    im = Image.open(TX + n + '.png').convert('RGBA'); return im.resize((im.width * sc, im.height * sc), Image.NEAREST)
def pair(who, line, sc):
    """the game's subtitle: the line, then the name at its right; a line too long for the frame goes on two rows, the
    name on the first"""
    rows = []
    for k, ln in enumerate(line):
        a = Image.open(TX + ln + '.png').convert('RGBA')
        if k == 0:
            b = Image.open(TX + who + '.png').convert('RGBA')
            top = min(TM[ln]['y0'], TM[who]['y0']); bot = max(TM[ln]['y0'] + TM[ln]['h'], TM[who]['y0'] + TM[who]['h'])
            im = Image.new('RGBA', (a.width + GAP + b.width, bot - top), (0, 0, 0, 0))
            im.alpha_composite(a, (0, TM[ln]['y0'] - top)); im.alpha_composite(b, (a.width + GAP, TM[who]['y0'] - top))
        else:
            im = a
        rows.append(im.resize((im.width * sc, im.height * sc), Image.NEAREST))
    if len(rows) == 1: return rows[0]
    lead = 5 * sc
    w = max(r.width for r in rows); h = sum(r.height for r in rows) + lead * (len(rows) - 1)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); y = 0
    for r in rows: im.alpha_composite(r, ((w - r.width) // 2, y)); y += r.height + lead
    return im
def scaled_logo(f):
    im = Image.open(D + 'reel/logo.png').convert('RGBA'); return im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
def row(parts, gap):
    w = sum(p.width for p in parts) + gap * (len(parts) - 1); h = max(p.height for p in parts)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); x = 0
    for p in parts: im.alpha_composite(p, (x, (h - p.height) // 2)); x += p.width + gap
    return im
HANDLE = Image.open(D + 'reel/H_0.png').convert('RGBA'); HANDLE = HANDLE.resize((HANDLE.width * 3, HANDLE.height * 3), Image.NEAREST)
SC = 4 if X else 5
SUBIMG = {(w, l): pair(WHO[w], LINE[l], SC) for a, b, w, l in SUBS}
for k, im in SUBIMG.items(): assert im.width <= W - 80, (k, im.width)
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

def window(s, k):
    im = Image.open(RUN + 'f/%06d.png' % k).convert('RGB')
    x0, y0, sc = s['x0'], s['y0'], s.get('sc', 4)
    return im.crop((x0, y0, x0 + 1080 // sc, y0 + 648 // sc)).resize((1080, 648), Image.NEAREST)

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
    ks += [a + 12 for a, b, w, l in SUBS] + [CARD_AT + 60]
    ks = sorted(set(ks))
    ims = [frame(k).resize((W // 4, H // 4)) for k in ks]
    cols = 8; S = Image.new('RGB', (cols * (W // 4), ((len(ims) + cols - 1) // cols) * (H // 4)))
    for n, im in enumerate(ims): S.paste(im, ((n % cols) * (W // 4), (n // cols) * (H // 4)))
    S.save(OUT + 'preview.png'); CARD_RGB.save(OUT + 'f_card.png')
    for a, b, w, l in SUBS: frame(a + 20).save(OUT + 'f_%d.png' % a)
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
GAME = np.fromfile(RUN + 'game.pcm', dtype='<i2').reshape(-1, 2).astype(np.float32) / 32768.0
game = np.zeros((N, 2), np.float32)
for n, s in enumerate(SHOTS):
    xi = int(s.get('xi', 0.05) * SR)                     # (a shot can come in on a word: a short fade in, from its first frame)
    a, b = s['a'] * SPF - (XF if xi == XF else 0), (s['a'] + s['n']) * SPF + XF
    pre = max(0, -a); a = max(0, a)
    seg = np.concatenate([np.zeros((pre, 2), np.float32), GAME[a:b].copy()])
    hi_ = 2 * XF if xi == XF else xi
    seg[:hi_] *= np.sin(np.linspace(0, np.pi / 2, hi_))[:, None]
    seg[-2 * XF:] *= np.sin(np.linspace(0, np.pi / 2, 2 * XF))[::-1][:, None]
    if n == len(SHOTS) - 1:
        fo = int(0.5 * SR); seg[-fo:] *= np.linspace(1, 0, fo)[:, None]
    p = s['r'] * SPF - (XF if xi == XF else 0)
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

# the lines (the game's own log): the music steps down under each, as the game's does
duck = []
for s in SHOTS:
    for k, f, d in LOG['log']:
        if k != 'voice' or (isinstance(d[1], dict) and d[1].get('over')): continue
        v = SPEECH.get(d[0]) or MAN['voices'].get(d[0])
        if not v: continue
        a, b = f, f + int(round(v['at'][1] * FPS))
        a2, b2 = max(a, s['a']), min(b, s['a'] + s['n'])
        if b2 > a2: duck.append((reel(s, a2), reel(s, b2)))
# Ibb's theme, from its first beat, under the whole reel; up a little on the card (nothing is said there), out at its end
bed = decode(AUD + 'music_ibb.mp3', M0, TOTAL / FPS + 0.5)
music = np.zeros((N, 2), np.float32); m = min(len(bed), N); music[:m] = bed[:m]
target = np.ones(N, np.float32)
for a, b in duck: target[(tt >= a / FPS) & (tt < b / FPS)] = MUSIC_UNDER / MUSIC
c0 = CARD_AT * SPF
target[c0:] = 1.5
mg, cur = np.empty(N, np.float32), 1.0
da, ua = 1 - np.exp(-1 / (0.05 * SR)), 1 - np.exp(-1 / (0.2 * SR))
for k in range(N):
    tg = target[k]; cur += (tg - cur) * (da if tg < cur else ua); mg[k] = cur
music *= (mg * MUSIC * MASTER)[:, None]
fo2 = int(1.4 * SR); music[-fo2:] *= (np.linspace(1, 0, fo2) ** 1.5)[:, None]

mix = game + music
fi0 = int(0.02 * SR); mix[:fi0] *= np.linspace(0, 1, fi0)[:, None]          # no click on the first frame
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

NAME = 'bab-alyemen-ibb-tour' + ('-x' if X else '') + '.mp4'
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-i', OUT + 'sound.wav', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
                        '-af', 'volume=-1.5dB,lowpass=f=16000,alimiter=limit=0.70:attack=1:release=50:level=disabled',
                        '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', OUT + NAME], stdin=subprocess.PIPE)
for t in range(TOTAL): enc.stdin.write(frame(t).tobytes())
enc.stdin.close(); enc.wait()
json.dump({'shots': SHOTS, 'subs': SUBS, 'duck': duck, 'card': CARD_AT, 'total': TOTAL, 'loudness_in': js},
          open(OUT + 'edit.json', 'w'), ensure_ascii=False, indent=1)
print('done', OUT + NAME)
