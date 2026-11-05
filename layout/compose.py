"""A picture post with the game around it (Khaled, 23 Oct: anything going on social media carries the logo, the mission
line, the call to play and the handle): 1080x1350 (4:5, X and the Instagram feed), everything in the game's own art and
lettering, scaled by whole numbers. From the Black Jinn picture (reference/compose_black_jinn.py).
Usage: compose.py <spec.json>
Spec:
{
 "frame": "work/runs/ibbT/f/005300.png",   a frame from rig/film.py (the world's canvas, 384x216)
 "crop": [x0, y0, sc],                       sc 3 = a 360x216 crop (an on-foot scene's whole height; the default,
                                             [12, 0, 3]), 4 = 270x162 (close); 2 = 540x324 only on wider canvases
                                             (Taiz seen from the Apache)
 "head": [["المهمة 4: إب", "b_org"], ["متاحة الآن", "b_red"]],   the row under the logo, in reading order (right first)
 "sub": ["العميد عاجل", "تعز ما زالت بأيدينا."],   optional: a real game line, as the game's subtitle under the picture
 "bubbles": [{"text": "…", "x": 600, "y": 200, "tail": [520, 330]}],  optional: comic speech bubbles drawn on the picture
                                             (Khaled, 22 Oct: new words are fine in bubbles drawn as a comic)
 "foot": [["العبها الآن من المتصفح", "b_org", 4]],
 "out": "work/out/post.png"
}"""
import json, os, sys, hashlib
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lettering'))
import mk
SPEC = json.load(open(sys.argv[1]))
def wpath(p): return p if os.path.isabs(p) else os.path.join(mk.WORK, p[5:] if p.startswith('work/') else p)
W, H = 1080, 1350
def key(font, text): return 's_' + hashlib.md5((font + '|' + text).encode()).hexdigest()[:10]
META = json.load(open(os.path.join(mk.TEXT, 'meta.json'))) if os.path.exists(os.path.join(mk.TEXT, 'meta.json')) else {}
need = {}
for t, f in SPEC.get('head', []): need[key(f, t)] = [f, t]
for t, f, sc in SPEC.get('foot', [["العبها الآن من المتصفح", "b_org", 4]]): need[key(f, t)] = [f, t]
if SPEC.get('sub'):
    need[key('m_org', SPEC['sub'][0])] = ['m_org', SPEC['sub'][0]]; need[key('m_lav', SPEC['sub'][1])] = ['m_lav', SPEC['sub'][1]]
miss = {k: v for k, v in need.items() if k not in META}
if miss:
    import strips
    META.update(strips.render(miss, mk.TEXT, quiet=True))
def strip(k, s):
    im = Image.open(os.path.join(mk.TEXT, k + '.png')).convert('RGBA'); return im.resize((im.width * s, im.height * s), Image.NEAREST)
def row(parts, gap):
    w = sum(p.width for p in parts) + gap * (len(parts) - 1); h = max(p.height for p in parts)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); x = 0
    for p in parts: im.alpha_composite(p, (x, (h - p.height) // 2)); x += p.width + gap
    return im
x0, y0, sc = SPEC.get('crop', [12, 0, 3])
fr = Image.open(wpath(SPEC['frame'])).convert('RGBA')
fr = fr.crop((x0, y0, x0 + 1080 // sc, y0 + 648 // sc)).resize((1080, 648), Image.NEAREST)
if SPEC.get('bubbles'):
    # a comic bubble: white, a dark outline, a tail to the speaker; the words in the game's Kufi (Noto Kufi Arabic)
    d = ImageDraw.Draw(fr); font = ImageFont.truetype(mk.FONT, 34); font.set_variation_by_axes([700])
    for b in SPEC['bubbles']:
        tw = d.textbbox((0, 0), b['text'], font=font, direction='rtl', language='ar')
        w_, h_ = tw[2] - tw[0] + 44, tw[3] - tw[1] + 30; bx, by = b['x'] - w_ // 2, b['y'] - h_ // 2
        if b.get('tail'):
            tx, ty = b['tail']; d.polygon([(b['x'] - 14, by + h_ - 4), (b['x'] + 14, by + h_ - 4), (tx, ty)], fill='white', outline=(20, 20, 28), width=4)
        d.rounded_rectangle([bx, by, bx + w_, by + h_], radius=22, fill='white', outline=(20, 20, 28), width=4)
        if b.get('tail'): d.polygon([(b['x'] - 11, by + h_ - 6), (b['x'] + 11, by + h_ - 6), (b['tail'][0], b['tail'][1] - 6)], fill='white')
        d.text((b['x'], b['y']), b['text'], font=font, fill=(20, 20, 28), anchor='mm', direction='rtl', language='ar')
logo = Image.open(mk.LOGO).convert('RGBA')
im = Image.new('RGBA', (W, H), mk.BG + (255,))
y = 84; im.alpha_composite(logo, ((W - logo.width) // 2, y)); y += logo.height + 30
if SPEC.get('head'):
    head = row([strip(key(f, t), 4) for t, f in reversed(SPEC['head'])], 40); im.alpha_composite(head, ((W - head.width) // 2, y)); y += head.height + 36
im.alpha_composite(fr, (0, y)); y += fr.height + 24
if SPEC.get('sub'):
    who, line = SPEC['sub']; a = strip(key('m_lav', line), 4); b = strip(key('m_org', who), 4)
    pr = row([a, b], (META.get('_gap') or 7) * 4); im.alpha_composite(pr, ((W - pr.width) // 2, y)); y += pr.height + 24
y += 12
for t, f, s in SPEC.get('foot', [["العبها الآن من المتصفح", "b_org", 4]]):
    c = strip(key(f, t), s); im.alpha_composite(c, ((W - c.width) // 2, y)); y += c.height + 28
hd = Image.open(mk.HANDLE).convert('RGBA'); hd = hd.resize((hd.width * 3, hd.height * 3), Image.NEAREST)
im.alpha_composite(hd, ((W - hd.width) // 2, y)); y += hd.height
assert y <= H, ('too tall', y)
out = wpath(SPEC['out']); os.makedirs(os.path.dirname(out), exist_ok=True)
im.convert('RGB').save(out, optimize=True)
print('saved', out, 'content ends at', y, 'of', H)
