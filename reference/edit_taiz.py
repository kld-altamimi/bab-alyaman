"""The Taiz launch reel, second cut: one continuous soundtrack. The Taiz theme runs from its quiet intro to a fade on the
end card (no boss theme, no fanfare); the game's effects (filmed with the voices muted) cross-fade at every cut; the voices
are laid in clean from the game's own voice file, exactly where the game played them; the music dips under each line as
the game does. Shots are found from the shoot's own event log, so the cut follows whichever build was filmed.
Usage: python3 edit2.py <shoot dir> [--preview]"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image

D = os.path.dirname(os.path.abspath(__file__)) + '/'
SH = os.path.abspath(os.path.join(D, sys.argv[1])) + '/'
TX = D + '../text/'
BUILD = os.path.abspath(os.path.join(D, '..', os.environ.get('TAIZ_BUILD', 'build70'))) + '/'
AUD = BUILD + 'audio/'
OUT = D + 'out2/'
os.makedirs(OUT, exist_ok=True)
PREVIEW = '--preview' in sys.argv
WINDOWS = '--windows' in sys.argv
SR, FPS, SPF = 48000, 60, 800
W, H = 1080, 1920
BG = (3, 4, 9)
WIN_Y = 520
MASTER, MUSIC, MUSIC_UNDER, SFX, SFX_UNDER, VOICE = 0.85, 0.62, 0.38, 0.62, 0.44, 1.2
BED_START = 0.495                     # music_taiz's first downbeat; 144 BPM, so a beat is exactly 25 frames
XF = int(0.06 * SR)                   # each side of a cut's cross-fade in the effects

LOG = json.load(open(SH + 'log.json'))
src = open(BUILD + 'index.html', encoding='utf8').read()
i = src.find('var AUDIO = '); j = src.find(';\n', i); MAN = json.loads(src[i + 12:j])

def ev(name, k=None, nth=0):
    hits = [f for kk, f, d in LOG['log'] if kk == 'ev' and d[0] == name and (k is None or d[1] == k)]
    return hits[nth]
def voice_at(vid, after=0):
    return min(f for kk, f, d in LOG['log'] if kk == 'voice' and d[0] == vid and f >= after)

# ---- the shots, anchored on the shoot's own events (offsets measured on the first cut), in beats of 25 frames
opening_qanya = min(f for kk, f, d in LOG['log'] if kk == 'ev' and d[0] == 'qanya')
SHOTS = [
    ('hook',       opening_qanya - 43,                     6, (24, 0, 3)),
    ('lift',       ev('liftoff') + 13,                     7, None),
    ('roofs',      ev('oops') - 33,                        3, (180, 57, 3)),
    ('chase',      ev('chase') + 117,                      4, ('pan', 178, 78, 150, 84, 3)),
    ('chase_boom', ev('chase') + 314,                      3, None),
    ('cgun',       ev('boss_intro', 'cgun') + 25,          4, (150, 42, 3)),
    ('launcher',   voice_at('cmdr_behold', ev('boss_intro', 'launcher')) - 4, 9, (80, 62, 3)),
    ('farce',      ev('lost_count') - 10,                 16, (50, 82, 3)),
    ('boom',       ev('boss_dying', 'launcher') - 23,      5, None),
    ('complete',   [f for kk, f, d in LOG['log'] if kk == 'jingle'][0], 8, None),
]
CARD_BEATS = 7
cuts, at = [], 0
for name, fin, nb, crop in SHOTS:
    cuts.append(dict(name=name, fin=fin, ln=nb * 25, at=at, crop=crop)); at += nb * 25
card_at = at
TOTAL = card_at + CARD_BEATS * 25
print('cuts:', [(c['name'], c['fin'], c['ln'], c['at']) for c in cuts], '| total', TOTAL, '=', TOTAL / FPS, 's')
if WINDOWS:
    win = [{'a': c['fin'] - 40, 'b': c['fin'] + c['ln'] + 40, 'name': c['name']} for c in cuts]
    json.dump(win, open(D + '../rig/windows70.json', 'w'), indent=1); print('windows written'); sys.exit(0)

# ---- voices as the game played them: (frame, id, opts)
voices = [(f, d[0], d[1] if len(d) > 1 and isinstance(d[1], dict) else {}) for k, f, d in LOG['log'] if k == 'voice']
spoken = []
for f, vid, o in voices:
    v = MAN['voices'].get(vid)
    if not v or not v.get('text') or o.get('over'): continue
    spoken.append((f, f + int(round(v['at'][1] * FPS / (o.get('rate') or 1))), vid))
subs, duck = [], []
for c in cuts:
    for f, e, vid in spoken:
        a, b = max(f, c['fin']), min(e + 18, c['fin'] + c['ln'])
        if b > a and f >= c['fin'] - 2 and vid != 'yazeed_yalla':
            subs.append((c['at'] + a - c['fin'], c['at'] + b - c['fin'], vid))
        a2, b2 = max(f, c['fin']), min(e, c['fin'] + c['ln'])
        if b2 > a2: duck.append((c['at'] + a2 - c['fin'], c['at'] + b2 - c['fin'], vid))
lift = next(c for c in cuts if c['name'] == 'lift')
ANN_AT = lift['at'] + 6
ann_len = int(round(MAN['voices']['ann_taiz']['at'][1] * FPS))
subs.append((ANN_AT, ANN_AT + ann_len + 18, 'ann_taiz')); duck.append((ANN_AT, ANN_AT + ann_len, 'ann_taiz'))
subs.sort()
print('subtitles:', subs)

# ---- picture (as in the first cut)
WHO = {'RIFLEMAN': 'who_rifle', 'ANNOUNCER': 'who_ann', 'COMMANDER': 'who_cmdr', 'SALEM': 'who_salem', 'THE UNCLE': 'who_uncle', 'YAZEED': 'who_yazeed'}
LINE = {'grunt_qanya': 'l_qanya', 'ann_taiz': 'l_taiz', 'cmdr_behold': 'l_behold', 'grunt_count': 'l_count', 'cmdr_again': 'l_again',
        'ann_complete': 'l_complete', 'grunt_face': 'l_face', 'grunt_alarm': 'l_alarm', 'yazeed_tea': 'l_tea'}
assert all(v in LINE for a, b, v in subs), [v for a, b, v in subs if v not in LINE]
TM = json.load(open(TX + 'meta.json'))
def strip(n, s):
    im = Image.open(TX + n + '.png').convert('RGBA'); return im.resize((im.width * s, im.height * s), Image.NEAREST)
def pair(who, line, s=4, gap=6):
    a, b = Image.open(TX + line + '.png').convert('RGBA'), Image.open(TX + who + '.png').convert('RGBA')
    top = min(TM[line]['y0'], TM[who]['y0']); bot = max(TM[line]['y0'] + TM[line]['h'], TM[who]['y0'] + TM[who]['h'])
    im = Image.new('RGBA', (a.width + gap + b.width, bot - top), (0, 0, 0, 0))
    im.alpha_composite(a, (0, TM[line]['y0'] - top)); im.alpha_composite(b, (a.width + gap, TM[who]['y0'] - top))
    return im.resize((im.width * s, im.height * s), Image.NEAREST)
SUB_IMG = {vid: pair(WHO[MAN['voices'][vid]['who']], LINE[vid]) for a, b, vid in subs}
LOGO = Image.open(D + '../../reel/logo.png').convert('RGBA')
def row(*parts, gap=36):
    w = sum(p.width for p in parts) + gap * (len(parts) - 1); h = max(p.height for p in parts)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); x = 0
    for p in parts: im.alpha_composite(p, (x, (h - p.height) // 2)); x += p.width + gap
    return im
HEAD2 = row(strip('h_now', 4), strip('h_mission', 4)); CTA = strip('h_play', 3)
BASE = Image.new('RGBA', (W, H), BG + (255,))
BASE.alpha_composite(LOGO, ((W - LOGO.width) // 2, 230)); BASE.alpha_composite(HEAD2, ((W - HEAD2.width) // 2, 432)); BASE.alpha_composite(CTA, ((W - CTA.width) // 2, 1352))
card = Image.new('RGBA', (W, H), BG + (255,)); card.alpha_composite(LOGO, ((W - LOGO.width) // 2, 520))
for n, s, y in [('h_mission', 6, 780), ('h_now', 6, 912), ('h_play_b', 4, 1100)]:
    im = strip(n, s); card.alpha_composite(im, ((W - im.width) // 2, y))
hd = Image.open(D + '../../reel/H_0.png').convert('RGBA'); hd = hd.resize((hd.width * 3, hd.height * 3), Image.NEAREST)
card.alpha_composite(hd, ((W - hd.width) // 2, 1226)); CARD = card.convert('RGB')
FADE_END = 8

def window(k, crop, u=0.0):
    im = Image.open(SH + 'f/%06d.png' % k).convert('RGB')
    if im.width == 384: x0, y0, s = 24, 0, 3
    elif crop is None: x0, y0, s = 18, 0, 2
    elif crop[0] == 'pan': _, xa, ya, xb, yb, s = crop; x0 = round(xa + (xb - xa) * u); y0 = round(ya + (yb - ya) * u)
    else: x0, y0, s = crop
    w, h = W // s, 648 // s
    x0 = max(0, min(im.width - w, x0)); y0 = max(0, min(im.height - h, y0))
    return im.crop((x0, y0, x0 + w, y0 + h)).resize((W, 648), Image.NEAREST)
def frame(t):
    if t >= card_at:
        k = t - card_at
        if k < FADE_END: return Image.blend(frame(card_at - 1), CARD, (k + 1) / (FADE_END + 1))
        return CARD
    c = next(c for c in cuts if c['at'] <= t < c['at'] + c['ln'])
    im = BASE.copy()
    im.paste(window(c['fin'] + t - c['at'], c['crop'], (t - c['at']) / max(1, c['ln'] - 1)), (0, WIN_Y))
    for a, b, vid in subs:
        if a <= t < b: s = SUB_IMG[vid]; im.alpha_composite(s, ((W - s.width) // 2, 1212))
    return im.convert('RGB')

if PREVIEW:
    ks = sorted(set([c['at'] + c['ln'] // 2 for c in cuts] + [card_at + 60] + [a + 3 for a, b, v in subs]))
    ims = [frame(k).resize((270, 480)) for k in ks]
    cols = 8; S = Image.new('RGB', (cols * 270, ((len(ims) + cols - 1) // cols) * 480))
    for n, im in enumerate(ims): S.paste(im, ((n % cols) * 270, (n // cols) * 480))
    S.save(OUT + 'preview.png'); print('preview', len(ims)); sys.exit(0)

if '--audio-only' not in sys.argv:
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', str(FPS), OUT + 'picture.mp4'], stdin=subprocess.PIPE)
    for t in range(TOTAL): enc.stdin.write(frame(t).tobytes())
    enc.stdin.close(); enc.wait(); print('picture done')

# ---- sound
def decode(path, start=0.0, dur=None, ch=2):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(start), '-i', path]
    if dur: cmd += ['-t', str(dur)]
    cmd += ['-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, ch).copy()
N = TOTAL * SPF
t = np.arange(N) / SR
GAME = np.fromfile(SH + 'game.pcm', dtype='<i2').reshape(-1, 2).astype(np.float32) / 32768.0
# effects: each shot with a little of what comes before and after it, cross-faded (equal power) over 120 ms at each cut
fx = np.zeros((N, 2), np.float32)
for n, c in enumerate(cuts):
    a, b = c['fin'] * SPF - XF, (c['fin'] + c['ln']) * SPF + XF
    seg = GAME[max(0, a):b].copy()
    if a < 0: seg = np.vstack([np.zeros((-a, 2), np.float32), seg])
    L = len(seg); ramp = np.sin(np.linspace(0, np.pi / 2, 2 * XF))[:, None]
    seg[:2 * XF] *= ramp; seg[-2 * XF:] *= ramp[::-1]
    if n == len(cuts) - 1:                       # into the end card: the effects go over 0.4 s
        fo = int(0.4 * SR); seg[-fo:] *= np.linspace(1, 0, fo)[:, None]
    p = c['at'] * SPF - XF
    lo, hi = max(0, p), min(N, p + L)
    fx[lo:hi] += seg[lo - p:hi - p]
# a slow leveller on the effects: loud action comes down (up to 8 dB), quiet shots come up a little (up to 3 dB), so
# the soundtrack doesn't swing from shot to shot; the music, continuous underneath, does the rest
FX_TARGET, FX_CUT, FX_LIFT = -21.0, -8.0, 3.0
win = int(0.2 * SR); pw = np.convolve((fx ** 2).mean(axis=1), np.ones(win) / win, 'same')
want = np.clip(FX_TARGET - 10 * np.log10(pw + 1e-10), FX_CUT, FX_LIFT)
gl, cur = np.empty(N, np.float32), 0.0
att, rel = 1 - np.exp(-1 / (0.05 * SR)), 1 - np.exp(-1 / (0.4 * SR))
for k in range(N):
    tg = want[k]; cur += (tg - cur) * (att if tg < cur else rel); gl[k] = cur
fx *= (10 ** (gl / 20))[:, None]
# the lift-off's effects dip under the announcer's line, as the game dips them under any line
g = np.ones(N, np.float32); a0, a1 = ANN_AT / FPS, (ANN_AT + ann_len) / FPS
g[(t >= a0) & (t < a1)] = SFX_UNDER / SFX
cur = 1.0; gs = np.ones(N, np.float32)
for k in range(int(lift['at'] * SPF), min(N, int((lift['at'] + lift['ln']) * SPF) + SR)):
    tg = g[k]; cur += (tg - cur) * (1 - np.exp(-1 / ((0.04 if tg < cur else 0.15) * SR))); gs[k] = cur
fx *= gs[:, None]

# voices, from the game's own voice file, where and how the game played them (gain, speed, pan)
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
    if pan != pan: pan = 0
    pan = max(-1, min(1, pan)); th = (pan + 1) * np.pi / 4
    return np.stack([s * gain * np.cos(th), s * gain * np.sin(th)], axis=1)
vo = np.zeros((N, 2), np.float32)
placed = []                                     # (start sample, end sample, over) for the game's one-line-at-a-time rule
for c in cuts:
    for f, vid, o in voices:
        if not (c['fin'] <= f < c['fin'] + c['ln']): continue
        if vid not in MAN['voices']: continue
        x = line_audio(vid, o)
        p = (c['at'] + f - c['fin']) * SPF
        end_cut = (c['at'] + c['ln']) * SPF + int(0.25 * SR)       # a yelp may ring a moment past its cut, then fades
        x = x[:max(0, min(len(x), end_cut - p))]
        if len(x) > int(0.25 * SR) and p + len(x) > (c['at'] + c['ln']) * SPF:
            fo = min(len(x), int(0.2 * SR)); x[-fo:] *= np.linspace(1, 0, fo)[:, None]
        if not o.get('over'):
            # a new line stops the one still speaking (60 ms), as the game does
            for q in placed:
                if not q[2] and q[0] < p < q[1]:
                    k0, k1 = p, min(q[1], p + int(0.06 * SR)); vo[k0:k1] *= np.linspace(1, 0, k1 - k0)[:, None]; vo[k1:q[1]] = 0
        vo[p:p + len(x)] += x[:N - p]
        placed.append((p, p + len(x), bool(o.get('over'))))
ann = line_audio('ann_taiz', {}); k0 = ANN_AT * SPF; vo[k0:k0 + len(ann)] += ann[:N - k0]

# music: the Taiz theme, one piece from its first downbeat to the end, under every line as the game does, fading at the end
bed = decode(AUD + 'music_taiz.mp3', BED_START, TOTAL / FPS + 0.3)[:N]
music = np.zeros((N, 2), np.float32); music[:len(bed)] = bed
target = np.ones(N, np.float32)
for a, b, v in duck: target[(t >= a / FPS) & (t < b / FPS)] = MUSIC_UNDER / MUSIC
mg, cur = np.empty(N, np.float32), 1.0
da, ua = 1 - np.exp(-1 / (0.05 * SR)), 1 - np.exp(-1 / (0.18 * SR))
for k in range(N):
    tg = target[k]; cur += (tg - cur) * (da if tg < cur else ua); mg[k] = cur
music *= (mg * MUSIC * MASTER)[:, None]
fo = int(2.0 * SR); music[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5

mix = fx + vo + music
mix.astype('<f4').tofile(OUT + 'mix.f32')
for name, arr in (('fx', fx), ('vo', vo), ('music', music)): arr.astype('<f4').tofile(OUT + name + '.f32')
print('mix peak', round(float(np.abs(mix).max()), 3))
p1 = subprocess.run(['ffmpeg', '-v', 'info', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', OUT + 'mix.f32', '-af', 'loudnorm=I=-14:TP=-1:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
js = json.loads(p1[p1.rfind('{'):p1.rfind('}') + 1])
af = (f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:"
      f"measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', OUT + 'mix.f32', '-af', af, '-ar', str(SR), OUT + 'sound.wav'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', OUT + 'picture.mp4', '-i', OUT + 'sound.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                '-shortest', '-movflags', '+faststart', OUT + 'bab-alyemen-taiz-launch.mp4'], check=True)
json.dump({'cuts': cuts, 'subs': subs, 'duck': duck, 'total': TOTAL, 'loudness_in': js}, open(OUT + 'edit.json', 'w'), ensure_ascii=False, indent=1)
print('done', OUT + 'bab-alyemen-taiz-launch.mp4')
