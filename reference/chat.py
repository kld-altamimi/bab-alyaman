"""The Zanabeel group chat (official statements #2): two slides of a dark group chat drawn at the game's pixel size
(256x260, shown x4), its words in the game's own lettering, avatars cut from the game's sprites, and two photos from
the game (the flying boat rising at the Strait, live 0.15.77; the boat wreck people saw on 21 Oct). The game around it:
the logo above, the call to play and the handle below (Khaled, 23 Oct)."""
import json, sys
import numpy as np
from PIL import Image, ImageDraw
D = '/tmp/claude-0/-home-claude/df6305fd-b1bf-5dfd-a75a-44d8bb54fcc7/scratchpad/'
G = D + 'gc/'
S = 4                                   # the chat's pixel size
CW, CH = 256, 272                       # the chat at 1x
W, H = 1080, 1350
BG = (3, 4, 9)
PANEL, TOPBAR, BUBBLE, CHIP = (13, 19, 29), (27, 36, 52), (33, 46, 60), (24, 33, 46)
def txt(n):
    return Image.open(G + 'text/%s.png' % n).convert('RGBA')
def dim(im, k=0.62):
    a = np.array(im).astype(np.float32); a[..., :3] *= k; return Image.fromarray(a.astype(np.uint8))

ATL = Image.open(G + 'atlas77.png').convert('RGBA'); FR = json.load(open(G + 'atlas_frames.json'))
def spr(n): x, y, w, h = FR[n][:4]; return ATL.crop((x, y, x + w, y + h))
def circle(im, d):
    m = Image.new('L', (d, d), 0); ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255)
    out = Image.new('RGBA', (d, d), (0, 0, 0, 0)); out.paste(im.resize((d, d), Image.NEAREST) if im.size != (d, d) else im, (0, 0), m)
    return out
def face(n, box, bg):
    s = spr(n); x0, y0, x1, y1 = box
    c = Image.new('RGBA', (x1 - x0, y1 - y0), bg + (255,)); c.alpha_composite(s.crop(box))
    return c
sign = spr('sc_sign_battery')
AV = {
    'uncle': circle(face('sc_sign_battery', (1, 1, 17, 17), (232, 182, 40)), 16),
    'cmdr': circle(face('cmdr_stand', (6, 1, 22, 17), (70, 92, 70)), 16),
    'cook': circle(face('cook_stand', (6, 0, 22, 16), (92, 70, 56)), 16),
}
GROUP_AV = circle(face('sc_sign_battery', (0, 0, 20, 20), (232, 182, 40)), 20)
NAME = {'uncle': txt('n_uncle'), 'cmdr': txt('n_cmdr'), 'cook': txt('n_cook')}

# the photos, at the game's own pixels (150x84 cut from the 384-wide world)
boat = Image.open(G + 'boat/000291.png').convert('RGBA')
P_BOAT = boat.crop((120, 8, 270, 84))
wr = Image.open('/home/claude/bab-alyemen-boat-wreck-clean.png').convert('RGB')
sx = 1824 / 384.0; top = 232
wr1 = Image.new('RGB', (384, int((1095 - top) / sx)))
a = np.array(wr); b = np.zeros((wr1.height, 384, 3), np.uint8)
for j in range(wr1.height):
    for i in range(384):
        b[j, i] = a[int(top + (j + 0.5) * sx), int((i + 0.5) * sx)]
wr1 = Image.fromarray(b).convert('RGBA')
P_WRECK = wr1.crop((158, 98, 308, 174))

def chip(im, d, label, y):
    w = label.width + 10; x = (CW - w) // 2
    d.rounded_rectangle((x, y, x + w - 1, y + label.height + 3), radius=4, fill=CHIP)
    im.alpha_composite(label, (x + 5, y + 2))
    return y + label.height + 3

def chat(msgs, first_chip):
    im = Image.new('RGBA', (CW, CH), PANEL + (255,)); d = ImageDraw.Draw(im)
    # the top bar: back arrow, the group's avatar, its name and members
    d.rectangle((0, 0, CW - 1, 27), fill=TOPBAR)
    ax = CW - 9
    d.line((ax - 6, 13, ax, 13), fill=(200, 205, 220)); d.line((ax - 3, 10, ax, 13), fill=(200, 205, 220)); d.line((ax - 3, 16, ax, 13), fill=(200, 205, 220))
    im.alpha_composite(GROUP_AV, (CW - 36, 4))
    nm, mb = txt('g_name'), dim(txt('g_members'), 0.8)
    im.alpha_composite(nm, (CW - 40 - nm.width, 1)); im.alpha_composite(mb, (CW - 40 - mb.width, 14))
    for k in range(3): d.rectangle((8, 9 + k * 4, 9, 10 + k * 4), fill=(200, 205, 220))
    y = 31
    y = chip(im, d, dim(txt(first_chip), 0.9), y) + 4
    prev = None
    for m in msgs:
        if m[0] == 'sys':
            y = chip(im, d, dim(txt(m[1]), 0.9), y + 2) + 4; prev = None; continue
        who, kind, body, t = m
        first = who != prev
        tm = dim(txt(t), 0.75)
        nmh = NAME[who].height - 2 if first else 0
        if kind == 'text':
            body_im = txt(body)
            bw = max(body_im.width + tm.width + 12, (NAME[who].width + 8) if first else 0); bh = nmh + body_im.height + 4
        else:
            body_im = body; bw = body_im.width + 6; bh = nmh + body_im.height + 6
        x1 = CW - 24; x0 = x1 - bw
        d.rounded_rectangle((x0, y, x1, y + bh), radius=4, fill=BUBBLE)
        if first:
            d.polygon([(x1 - 1, y), (x1 + 4, y), (x1 - 1, y + 5)], fill=BUBBLE)
            im.alpha_composite(AV[who], (CW - 19, y))
            im.alpha_composite(NAME[who], (x1 - 3 - NAME[who].width, y - 1))
        if kind == 'text':
            im.alpha_composite(body_im, (x1 - 4 - body_im.width, y + nmh + 1))
            im.alpha_composite(tm, (x0 + 4, y + bh - tm.height))
        else:
            im.alpha_composite(body_im, (x0 + 3, y + nmh + 3))
            sh = Image.new('RGBA', (tm.width + 4, tm.height), (0, 0, 0, 120)); im.alpha_composite(sh, (x0 + 5, y + bh - tm.height - 4))
            im.alpha_composite(tm, (x0 + 7, y + bh - tm.height - 4))
        y += bh + 4; prev = who
    if y > CH: print('WARNING: chat overflows', y)
    return im.resize((CW * S, CH * S), Image.NEAREST)

LOGO = Image.open(D + 'reel/logo.png').convert('RGBA'); LOGO = LOGO.resize((int(LOGO.width * 0.5), int(LOGO.height * 0.5)), Image.LANCZOS)
def tstrip(n, s):
    im = Image.open(D + 'taiz/text/%s.png' % n).convert('RGBA'); return im.resize((im.width * s, im.height * s), Image.NEAREST)
CTA = tstrip('h_play', 3)
HD = Image.open(D + 'reel/H_0.png').convert('RGBA'); HD = HD.resize((HD.width * 2, HD.height * 2), Image.NEAREST)
def slide(c):
    im = Image.new('RGBA', (W, H), BG + (255,))
    im.alpha_composite(LOGO, ((W - LOGO.width) // 2, 18))
    y = 18 + LOGO.height + 12
    d = ImageDraw.Draw(im); d.rectangle(((W - c.width) // 2 - 4, y - 4, (W + c.width) // 2 + 3, y + c.height + 3), fill=(40, 48, 66))
    im.alpha_composite(c, ((W - c.width) // 2, y)); y += c.height + 22
    foot = Image.new('RGBA', (HD.width + 34 + CTA.width, max(HD.height, CTA.height)), (0, 0, 0, 0))
    foot.alpha_composite(HD, (0, (foot.height - HD.height) // 2)); foot.alpha_composite(CTA, (HD.width + 34, (foot.height - CTA.height) // 2))
    im.alpha_composite(foot, ((W - foot.width) // 2, y)); y += foot.height
    if y > H: print('WARNING: slide overflows', y)
    return im.convert('RGB')

one = [('uncle', 'text', 'c_u1', 't_941'), ('cmdr', 'text', 'c_c1', 't_942'), ('cmdr', 'photo', P_BOAT, 't_942'),
       ('cmdr', 'text', 'c_c2', 't_942'), ('cook', 'text', 'c_k1', 't_943')]
two = [('cmdr', 'photo', P_WRECK, 't_1043'), ('cmdr', 'text', 'c_c3', 't_1043'), ('uncle', 'text', 'c_u2', 't_1044'),
       ('cmdr', 'text', 'c_c4', 't_1044'), ('sys', 'sys')]
s1, s2 = slide(chat(one, 'today')), slide(chat(two, 'chip'))
s1.save(G + 'groupchat-1.png', optimize=True); s2.save(G + 'groupchat-2.png', optimize=True)
P_WRECK.resize((600, 336), Image.NEAREST).save(G + 'wreck_check.png')
both = Image.new('RGB', (W * 2 + 20, H), (60, 60, 60)); both.paste(s1, (0, 0)); both.paste(s2, (W + 20, 0)); both.resize((1090, 675)).save(G + 'both.png')
print('ok')
