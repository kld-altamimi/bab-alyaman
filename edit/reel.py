"""A reel from filmed runs (rig/film.py), laid out like the game's posts: the logo and a title row above the picture,
the game's own subtitles under it (its lettering, the speaker's name on the right), an end card, one piece of the game's
music from the first frame to the last. Generalised from the Ibb tour (reference/edit_tour.py).
Usage: reel.py <spec.json> [--x] [--preview] [--audio-only]
  --x: the 4:5 cut for X (1080x1350); default the upright cut (1080x1920). --preview: a sheet of frames, no video.
Spec (JSON):
{
 "name": "bab-alyemen-ibb-tour",                      output file name (no extension)
 "out": "work/out/ibb-tour",                          folder for the outputs (relative to MK_WORK, or absolute)
 "runs": {"T": "work/runs/ibbT"},                     film.py output folders
 "shots": [{"run": "T", "a": 1, "n": 310, "x0": 0, "y0": 36, "sc": 4},  source frame a, n frames, crop at x0,y0;
           {"run": "T", "a": 2980, "n": 170, "x0": 10, "y0": 40, "xi": 0.005}, …]
     sc: 4 = a 270x162 crop (close), 3 = 360x216 (wide: use it when a fight spreads, so the men he shoots at stay in);
     xi: fade-in seconds for a shot that comes in on a word (default 0.05, a short cross-fade)
 "music": {"file": "music_ibb.mp3", "from": 0.82},     from the build's audio/; start on a beat (Ibb 60 BPM from 0.82 s)
 "head": [["المهمة 4: إب", "b_org"], ["متاحة الآن", "b_red"]],     the title row, in reading order (right to left)
 "card": [["المهمة 4: إب", "b_org", 6], ["الوديان الخضراء", "b_org", 5], ["متاحة الآن", "b_red", 6],
          ["العبها الآن من المتصفح", "b_org", 4]],     the end card's lines under the logo, with their scale; handle last
 "card_frames": 240,
 "subs": "auto",          the game's subtitles from each run's log; or a list [[from, to, who, line], …] in reel frames
 "sub_min": 15,           a subtitle shown for fewer frames than this (a line's tail as a shot starts) is left out
 "drop": ["يلّا."],       lines never shown
 "lines": [{"id": "yazeed_roaster", "at": 250}, …]   a real game line laid at reel frame `at`: its voice from the build's
          audio at the game's own level, its subtitle in the game's Arabic, the music and effects under it as the game
          does. For shots filmed with MUTEVOICES=1, so each line plays while what it's about is on screen (a real line in
          another scene is allowed). With "lines", the logs' own subtitles and voices are left out (they were silent).
          Optional per line: "hold" frames the subtitle stays after the voice (default 24), "min" its shortest (90)
}
A shot whose picture doesn't move for more than 0.4 s is refused (it reads as a hang; Khaled, 6 Nov: "The video is
buggy"): take frames where it moves. --allow-still overrides it, only for a still that is the point.
Rules this follows (Khaled's): pace 3–4 s a beat with text; no clipped word at a cut (check the log: a new line cuts the
one playing); one piece of music; the card names the mission, says it's out and how to play."""
import json, os, sys, subprocess, hashlib
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lettering'))
import mk

SPEC = json.load(open(sys.argv[1]))
X = '--x' in sys.argv
PREVIEW = '--preview' in sys.argv
def wpath(p): return p if os.path.isabs(p) else os.path.join(mk.WORK, p[5:] if p.startswith('work/') else p)
OUT = wpath(SPEC['out']) + ('_x' if X else '') + '/'
os.makedirs(OUT, exist_ok=True)
SR, FPS, SPF = 48000, 60, 800
W, H = (1080, 1350) if X else (1080, 1920)
BG = mk.BG
MASTER, MUSIC, MUSIC_UNDER = 0.85, 0.62, 0.38      # the game's own: music 0.62, 0.38 under a line, master 0.85

RUNS = {k: wpath(v) + '/' for k, v in SPEC['runs'].items()}
LOGS = {k: json.load(open(v + 'log.json')) for k, v in RUNS.items()}
src = open(os.path.join(mk.BUILD, 'index.html'), encoding='utf8').read()
i = src.find('var AUDIO = '); j = src.find(';\n', i); MAN = json.loads(src[i + 12:j])
SPEECH = {}
for v in (MAN.get('speech') or {}).values(): SPEECH.update(v.get('lines', {}))

SHOTS = SPEC['shots']
t = 0
for s in SHOTS:
    s.setdefault('run', next(iter(RUNS))); s['r'] = t; t += s['n']
CARD_N = SPEC.get('card_frames', 240)
CARD_AT = t; TOTAL = CARD_AT + CARD_N
def reel(s, f): return s['r'] + f - s['a']
for s in SHOTS:
    for f in range(s['a'], s['a'] + s['n']):
        assert os.path.exists(RUNS[s['run']] + 'f/%06d.png' % f), ('missing frame', s, f)
print('shots', [(s['run'], s['a'], s['n'], s['r']) for s in SHOTS], 'card', CARD_AT, 'total', TOTAL, round(TOTAL / FPS, 2), 's')

# ---- stills: a game picture that doesn't move for more than 0.4 s reads as a hang (a bot waiting for a boss's
# entrance, a scripted pause): refused before anything is made
def still_runs(s, most=24):
    x0, y0, sc = s['x0'], s['y0'], s.get('sc', 4); box = (x0, y0, x0 + 1080 // sc, y0 + 648 // sc)
    prev, start, out = None, None, []
    for f in range(s['a'], s['a'] + s['n'] + 1):
        b = Image.open(RUNS[s['run']] + 'f/%06d.png' % f).convert('RGB').crop(box).tobytes() if f < s['a'] + s['n'] else None
        if b is not None and b == prev:
            if start is None: start = f - 1
        else:
            if start is not None and f - start > most: out.append((start, f))
            start = None
        prev = b
    return out
STILLS = [(k, r) for k, s in enumerate(SHOTS) for r in still_runs(s)]
for k, (a_, b_) in STILLS:
    print("STILL: shot %d, source frames %d-%d (%.2f s): the picture doesn't move; take frames where it does" % (k, a_, b_, (b_ - a_) / FPS))
if STILLS and not PREVIEW and '--allow-still' not in sys.argv: sys.exit(1)

# ---- subtitles
SUBS = []
LAID = bool(SPEC.get('lines'))
if SPEC.get('subs', 'auto') == 'auto' and LAID: pass          # the shots were filmed silent: their subtitles don't apply
elif SPEC.get('subs', 'auto') == 'auto':
    for s in SHOTS:
        subs = LOGS[s['run']]['subs']
        for n, (f, txt) in enumerate(subs):
            end = subs[n + 1][0] if n + 1 < len(subs) else 10 ** 9
            a, b = max(f, s['a']), min(end, s['a'] + s['n'])
            if b - a < SPEC.get('sub_min', 15) or not txt: continue
            who, line = txt.split('|', 1)
            if line in SPEC.get('drop', []): continue
            SUBS.append((reel(s, a), reel(s, b), who, line))
else:
    SUBS = [tuple(x) for x in SPEC['subs']]
# the laid lines: a real game line each, placed where what it's about is on screen
import re
LANG = src[src.find('var LANG_AR'):src.find('var AUDIO = ')]
def ar(en):
    m = re.search('"' + re.escape(en) + r'"\s*:\s*"((?:[^"\\]|\\.)*)"', LANG)
    return json.loads('"' + m.group(1) + '"') if m else en
def voice_of(vid):
    if vid in MAN['voices']: return 'voices', MAN['voices'][vid]
    for sp in (MAN.get('speech') or {}).values():
        if vid in sp.get('lines', {}): return sp['file'], sp['lines'][vid]
    sys.exit('no such line in the build: ' + vid)
LINES = []
for o in SPEC.get('lines', []):
    f_, v_ = voice_of(o['id']); n_ = int(round(v_['at'][1] * FPS))
    LINES.append(dict(o, file=f_, v=v_, n=n_))
    SUBS.append((o['at'], min(o['at'] + max(n_ + o.get('hold', 24), o.get('min', 90)), CARD_AT), ar(v_['who']), ar(v_['text'])))
    print('line', o['id'], 'at reel frame', o['at'], '(%.2f s), voice %.2f s:' % (o['at'] / FPS, v_['at'][1]), ar(v_['text']))
print('subtitles', SUBS)

# ---- lettering: every string the reel needs, drawn by the game (missing ones rendered now)
SC = 4 if X else 5
def key(font, text): return 's_' + hashlib.md5((font + '|' + text).encode()).hexdigest()[:10]
META = json.load(open(os.path.join(mk.TEXT, 'meta.json'))) if os.path.exists(os.path.join(mk.TEXT, 'meta.json')) else {}
need = {}
def want(font, text): k = key(font, text); need[k] = [font, text]; return k
def words_split(text):
    ws = text.split(' '); best = None
    for c in range(1, len(ws)):
        a, b = ' '.join(ws[:c]), ' '.join(ws[c:]); d = abs(len(a) - len(b))
        if best is None or d < best[0]: best = (d, a, b)
    return [best[1], best[2]] if best else [text]
for a, b, w, l in SUBS: want('m_org', w); want('m_lav', l)
for txt, font in SPEC.get('head', []): want(font, txt)
for txt, font, sc in SPEC.get('card', []): want(font, txt)
def render_missing():
    miss = {k: v for k, v in need.items() if k not in META}
    if miss:
        import strips
        META.update(strips.render(miss, mk.TEXT, quiet=True))
render_missing()
GAP = META.get('_gap') or 7
# a line too wide for the frame goes on two rows (split at the word nearest its middle), the name on the first
SPLIT = {}
for a, b, w, l in SUBS:
    kw, kl = key('m_org', w), key('m_lav', l)
    if (META[kl]['w'] + GAP + META[kw]['w']) * SC > W - 80:
        SPLIT[l] = [want('m_lav', part) for part in words_split(l)]
render_missing()

def strip(k, sc):
    im = Image.open(os.path.join(mk.TEXT, k + '.png')).convert('RGBA'); return im.resize((im.width * sc, im.height * sc), Image.NEAREST)
def pair(who, line, sc):
    kw = key('m_org', who); lines = SPLIT.get(line) or [key('m_lav', line)]
    rows = []
    for n, kl in enumerate(lines):
        a = Image.open(os.path.join(mk.TEXT, kl + '.png')).convert('RGBA')
        if n == 0:
            b = Image.open(os.path.join(mk.TEXT, kw + '.png')).convert('RGBA')
            top = min(META[kl]['y0'], META[kw]['y0']); bot = max(META[kl]['y0'] + META[kl]['h'], META[kw]['y0'] + META[kw]['h'])
            im = Image.new('RGBA', (a.width + GAP + b.width, bot - top), (0, 0, 0, 0))
            im.alpha_composite(a, (0, META[kl]['y0'] - top)); im.alpha_composite(b, (a.width + GAP, META[kw]['y0'] - top))
        else:
            im = a
        rows.append(im.resize((im.width * sc, im.height * sc), Image.NEAREST))
    if len(rows) == 1: return rows[0]
    lead = 5 * sc; w = max(r.width for r in rows); h = sum(r.height for r in rows) + lead * (len(rows) - 1)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); y = 0
    for r in rows: im.alpha_composite(r, ((w - r.width) // 2, y)); y += r.height + lead
    return im
def scaled_logo(f):
    im = Image.open(mk.LOGO).convert('RGBA'); return im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
def row(parts, gap):
    w = sum(p.width for p in parts) + gap * (len(parts) - 1); h = max(p.height for p in parts)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); x = 0
    for p in parts: im.alpha_composite(p, (x, (h - p.height) // 2)); x += p.width + gap
    return im
HANDLE = Image.open(mk.HANDLE).convert('RGBA'); HANDLE = HANDLE.resize((HANDLE.width * 3, HANDLE.height * 3), Image.NEAREST)
SUBIMG = {(w, l): pair(w, l, SC) for a, b, w, l in SUBS}
L = (dict(logo=0.62, logo_y=40, head_y=196, win_y=330, sub_y=1020, card_logo=0.85, card_y=220) if X else
     dict(logo=0.82, logo_y=230, head_y=452, win_y=600, sub_y=1300, card_logo=1.0, card_y=430))
BASE = Image.new('RGBA', (W, H), BG + (255,))
LOGO = scaled_logo(L['logo']); BASE.alpha_composite(LOGO, ((W - LOGO.width) // 2, L['logo_y']))
if SPEC.get('head'):
    HEAD = row([strip(key(f, t_), 4) for t_, f in reversed(SPEC['head'])], 40)     # right to left: the first is rightmost
    BASE.alpha_composite(HEAD, ((W - HEAD.width) // 2, L['head_y']))
CARD = Image.new('RGBA', (W, H), BG + (255,))
cl = scaled_logo(L['card_logo']); y = L['card_y']
CARD.alpha_composite(cl, ((W - cl.width) // 2, y)); y += cl.height + (40 if X else 56)
for n, (t_, f, sc) in enumerate(SPEC.get('card', [])):
    im = strip(key(f, t_), sc); CARD.alpha_composite(im, ((W - im.width) // 2, y)); y += im.height + (60 if f == 'b_red' else 24)
CARD.alpha_composite(HANDLE, ((W - HANDLE.width) // 2, y + 10))
CARD_RGB = CARD.convert('RGB')

def window(s, k):
    im = Image.open(RUNS[s['run']] + 'f/%06d.png' % k).convert('RGB')
    x0, y0, sc = s['x0'], s['y0'], s.get('sc', 4)
    return im.crop((x0, y0, x0 + 1080 // sc, y0 + 648 // sc)).resize((1080, 648), Image.NEAREST)
def frame(t):
    if t >= CARD_AT:
        k = t - CARD_AT
        if k < 8: return Image.blend(frame(CARD_AT - 1), CARD_RGB, (k + 1) / 9)
        return CARD_RGB
    s = next(s for s in SHOTS if s['r'] <= t < s['r'] + s['n'])
    im = BASE.copy(); im.paste(window(s, s['a'] + t - s['r']), (0, L['win_y']))
    for a, b, w, l in SUBS:
        if a <= t < b: sb = SUBIMG[(w, l)]; im.alpha_composite(sb, ((W - sb.width) // 2, L['sub_y']))
    return im.convert('RGB')

if PREVIEW:
    ks = []
    for s in SHOTS: ks += [s['r'] + 2, s['r'] + s['n'] // 3, s['r'] + 2 * s['n'] // 3, s['r'] + s['n'] - 2]
    ks = sorted(set(ks + [a + 12 for a, b, w, l in SUBS] + [CARD_AT + 60]))
    ims = [frame(k).resize((W // 4, H // 4)) for k in ks]
    cols = 8; S = Image.new('RGB', (cols * (W // 4), ((len(ims) + cols - 1) // cols) * (H // 4)))
    for n, im in enumerate(ims): S.paste(im, ((n % cols) * (W // 4), (n // cols) * (H // 4)))
    S.save(OUT + 'preview.png'); print('preview', OUT + 'preview.png', ks); sys.exit(0)

# ---------------------------------------------------------------- sound
def decode(path, start=0.0, dur=None, ch=2):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(start), '-i', path] + (['-t', str(dur)] if dur else []) + ['-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, ch).copy()
N = TOTAL * SPF; tt = np.arange(N) / SR; XF = int(0.05 * SR)
PCM = {k: np.fromfile(v + 'game.pcm', dtype='<i2').reshape(-1, 2).astype(np.float32) / 32768.0 for k, v in RUNS.items()}
game = np.zeros((N, 2), np.float32)
for n, s in enumerate(SHOTS):
    xi = int(s.get('xi', 0.05) * SR); full = xi == XF
    a, b = s['a'] * SPF - (XF if full else 0), (s['a'] + s['n']) * SPF + XF
    pre = max(0, -a); a = max(0, a)
    seg = np.concatenate([np.zeros((pre, 2), np.float32), PCM[s['run']][a:b].copy()])
    hi_ = 2 * XF if full else xi
    seg[:hi_] *= np.sin(np.linspace(0, np.pi / 2, hi_))[:, None]
    seg[-2 * XF:] *= np.sin(np.linspace(0, np.pi / 2, 2 * XF))[::-1][:, None]
    if n == len(SHOTS) - 1: fo = int(0.5 * SR); seg[-fo:] *= np.linspace(1, 0, fo)[:, None]
    p = s['r'] * SPF - (XF if full else 0); lo, hi = max(0, p), min(N, p + len(seg))
    game[lo:hi] += seg[lo - p:hi - p]
# the laid lines: each voice at the game's own level (VOICE 1.2 x MASTER 0.85), the effects under it as the game does
VOICE, SFX, SFX_UNDER = 1.2, 0.62, 0.44
VOX = {}
def vox(fname):
    if fname not in VOX:
        pcm = decode(os.path.join(mk.BUILD, 'audio', fname + '.mp3'))
        k = np.nonzero(np.abs(pcm).max(axis=1) > 0.15)[0]
        VOX[fname] = (pcm, (k[0] / SR - MAN['mark']) if len(k) else 0.0)      # the game's own alignment (Sound's shift)
    return VOX[fname]
if LINES:
    sfxg = np.ones(N, np.float32)
    for L_ in LINES:
        p = L_['at'] * SPF; sfxg[p:p + int(L_['v']['at'][1] * SR)] = SFX_UNDER / SFX
    sg, cur = np.empty(N, np.float32), 1.0
    da_, ua_ = 1 - np.exp(-1 / (0.04 * SR)), 1 - np.exp(-1 / (0.15 * SR))
    for k in range(N): tg = sfxg[k]; cur += (tg - cur) * (da_ if tg < cur else ua_); sg[k] = cur
    game *= sg[:, None]
    for L_ in LINES:
        pcm, sh = vox(L_['file']); s0 = int(round((L_['v']['at'][0] + sh) * SR))
        seg = pcm[s0:s0 + int(round(L_['v']['at'][1] * SR))] * (VOICE * MASTER)
        p = L_['at'] * SPF; m_ = min(len(seg), N - p)
        if m_ > 0: game[p:p + m_] += seg[:m_]
TARGET, CUT, LIFT = -19.0, -6.0, 2.0          # a gentle leveller on the game's own mix
win = int(0.25 * SR); pw = np.convolve((game ** 2).mean(axis=1), np.ones(win) / win, 'same')
want_db = np.clip(TARGET - 10 * np.log10(pw + 1e-10), CUT, LIFT)
gl, cur = np.empty(N, np.float32), 0.0
att, rel = 1 - np.exp(-1 / (0.08 * SR)), 1 - np.exp(-1 / (0.5 * SR))
for k in range(N): tg = want_db[k]; cur += (tg - cur) * (att if tg < cur else rel); gl[k] = cur
game *= (10 ** (gl / 20))[:, None]
duck = [(L_['at'], L_['at'] + L_['n']) for L_ in LINES]
for s in ([] if LAID else SHOTS):
    for k, f, d in LOGS[s['run']]['log']:
        if k != 'voice' or (isinstance(d[1], dict) and d[1].get('over')): continue
        v = SPEECH.get(d[0]) or MAN['voices'].get(d[0])
        if not v: continue
        a, b = f, f + int(round(v['at'][1] * FPS)); a2, b2 = max(a, s['a']), min(b, s['a'] + s['n'])
        if b2 > a2: duck.append((reel(s, a2), reel(s, b2)))
mus = SPEC.get('music') or {}
music = np.zeros((N, 2), np.float32)
if mus:
    bed = decode(os.path.join(mk.BUILD, 'audio', mus['file']), mus.get('from', 0), TOTAL / FPS + 0.5)
    m = min(len(bed), N); music[:m] = bed[:m]
target = np.ones(N, np.float32)
for a, b in duck: target[(tt >= a / FPS) & (tt < b / FPS)] = MUSIC_UNDER / MUSIC
target[CARD_AT * SPF:] = 1.5
mg, cur = np.empty(N, np.float32), 1.0
da, ua = 1 - np.exp(-1 / (0.05 * SR)), 1 - np.exp(-1 / (0.2 * SR))
for k in range(N): tg = target[k]; cur += (tg - cur) * (da if tg < cur else ua); mg[k] = cur
music *= (mg * MUSIC * MASTER)[:, None]
fo2 = int(1.4 * SR); music[-fo2:] *= (np.linspace(1, 0, fo2) ** 1.5)[:, None]
mix = game + music
fi0 = int(0.02 * SR); mix[:fi0] *= np.linspace(0, 1, fi0)[:, None]
from scipy.ndimage import minimum_filter1d
LIM = 0.35
pk = np.abs(mix).max(axis=1)
g2 = minimum_filter1d(np.minimum(1.0, LIM / np.maximum(pk, 1e-9)), size=2 * int(0.005 * SR) + 1)
g2 = np.concatenate([g2[int(0.005 * SR):], np.ones(int(0.005 * SR), np.float32)])
sm, cur, rl = np.empty(N, np.float32), 1.0, 1 - np.exp(-1 / (0.08 * SR))
for k in range(N): cur = g2[k] if g2[k] < cur else cur + (g2[k] - cur) * rl; sm[k] = cur
mix *= sm[:, None]
mix.astype('<f4').tofile(OUT + 'mix.f32')
p1 = subprocess.run(['ffmpeg', '-v', 'info', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', OUT + 'mix.f32', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
js = json.loads(p1[p1.rfind('{'):p1.rfind('}') + 1])
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:"
      f"measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', OUT + 'mix.f32', '-af', af + ',alimiter=limit=0.79:attack=2:release=60:level=disabled', '-ar', str(SR), OUT + 'sound.wav'], check=True)
print('sound: limiter %.1f dB, loudness in %s' % (20 * np.log10(sm.min()), js['input_i']))
if '--audio-only' in sys.argv: sys.exit(0)
NAME = SPEC['name'] + ('-x' if X else '') + '.mp4'
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-i', OUT + 'sound.wav', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
                        # (AAC overshoots on bright tones: a low-pass and a limiter before it keep the true peak under -1 dB)
                        '-af', 'volume=-1.5dB,lowpass=f=16000,alimiter=limit=0.70:attack=1:release=50:level=disabled',
                        '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', OUT + NAME], stdin=subprocess.PIPE)
for t in range(TOTAL): enc.stdin.write(frame(t).tobytes())
enc.stdin.close(); enc.wait()
json.dump({'shots': SHOTS, 'subs': SUBS, 'card': CARD_AT, 'total': TOTAL}, open(OUT + 'edit.json', 'w'), ensure_ascii=False, indent=1)
print('done', OUT + NAME)
# the quality gate: a frozen picture or a white strobe reads as "buggy" (Khaled, 30 Oct and 6 Nov); fix before showing it
qc = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qc.py'), OUT + NAME, str(L['win_y']), '648'], capture_output=True, text=True)
print(qc.stdout.strip()); print('QC', 'passed' if qc.returncode == 0 else 'FAILED: fix it before showing the reel')
