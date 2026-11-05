"""The Black Jinn statement picture: the game's logo and Taiz line above a frame from the live game, the call to play and
the handle below. Everything is the game's own art and lettering, scaled by whole numbers. Usage: compose.py <frame.png> <out.png>"""
import sys
from PIL import Image
D = '/tmp/claude-0/-home-claude/df6305fd-b1bf-5dfd-a75a-44d8bb54fcc7/scratchpad/'
BG = (3, 4, 9)                       # the logo's own box colour, so it sits in the page without an edge
W, H = 1080, 1350
def strip(n, s):
    im = Image.open(D + 'taiz/text/%s.png' % n).convert('RGBA')
    return im.resize((im.width * s, im.height * s), Image.NEAREST)
def row(parts, gap):
    w = sum(p.width for p in parts) + gap * (len(parts) - 1); h = max(p.height for p in parts)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); x = 0
    for p in parts: im.alpha_composite(p, (x, (h - p.height) // 2)); x += p.width + gap
    return im
fr = Image.open(sys.argv[1]).convert('RGBA')
fr = fr.crop((18, 0, 18 + 540, 324)).resize((1080, 648), Image.NEAREST)
logo = Image.open(D + 'reel/logo.png').convert('RGBA')
head = row([strip('h_now', 4), strip('h_mission', 4)], 40)
cta = strip('h_play_b', 4)
hd = Image.open(D + 'reel/H_0.png').convert('RGBA'); hd = hd.resize((hd.width * 3, hd.height * 3), Image.NEAREST)
im = Image.new('RGBA', (W, H), BG + (255,))
y = 84;   im.alpha_composite(logo, ((W - logo.width) // 2, y)); y += logo.height + 30
im.alpha_composite(head, ((W - head.width) // 2, y)); y += head.height + 36
im.alpha_composite(fr, (0, y)); y += fr.height + 40
im.alpha_composite(cta, ((W - cta.width) // 2, y)); y += cta.height + 28
im.alpha_composite(hd, ((W - hd.width) // 2, y)); y += hd.height
print('content ends at', y, 'of', H)
im.convert('RGB').save(sys.argv[2], optimize=True)
