# mock_pass.py - the storyboard of the Spokesman's fight on Sumara pass (zone 4) and the reveal after it, drawn on the
# painted lookout with the game's own sprites before any of it is built (as the school's children and the rally were:
# Khaled sees the scene first). Nine pictures and a tenth of close-ups, a caption under each:
#   1  the lookout: he is at a podium, all five screens on him, giving statement E; each statement calls men in
#   2  his microphone shot: cut off mid-word, "WHAT? SPEAK UP!", stunned, hittable; every screen freezes on him
#   3  he leaps away over Yazeed (contact hurts); the cut podium's screen goes to snow: the lookout shrinks
#   4  phase 2: shouting, an ear ringing; the feedback runs along the ground: jump it
#   5  phase 3: the lights go out; he reads by torchlight at the last podium, cornered
#   6  caught: tied up in his own microphone cable
#   7  the screens come back on: still speaking; the ear too big, two Yemens (a close-up of the screen)
#   8  their van, the back room: three of the Uncle's men, hands up: "We only do the videos!"
#   9  the rack smashed: every screen in Ibb dark; the Uncle on the radio; the cloud clears; Mission Complete
#  10  close-ups: the screen as it was, and as it is in picture 7; the three technicians (stand-ins)
#   python3 mock_pass.py   -> ibb/s10/ibb_pass_mock.png
import sys, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/tools')
from paint import Layer, from_image
import stage_ibb as I
import stage_ibb_z2 as Z2
import stage_ibb_z4 as Z4
import look_ibb as LK
import ibb_sprites as S
import spokesman_s6 as S6

OUT = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/ibb/s10/'
ART = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/art/out/'
GEN = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/gen/'
A = json.load(open(GEN + 'stage_ibb.json'))['info']['z4']
PODS = A['arena']['podiums']
VAN = A['van']
FLOOR = A['arena']['y']
CAM_FIGHT = (PODS[0] + PODS[-1]) // 2 - I.SW // 2          # the screen held for the fight, at the widest
CAM_VAN = Z4.END4 - I.SW
PS_LIFT = 46


def put(im, f, x, y, flip=False):
    fr, ax, ay = f
    if flip:
        fr = fr.transpose(Image.FLIP_LEFT_RIGHT)
        ax = fr.width - 1 - ax
    im.alpha_composite(fr, (int(x - ax), int(y - ay)))


# ---------------------------------------------------------------- what the screens show
def fake_s6(s=3, mouth=1, blink=False, big_ear=False, yemens=False):
    """The approved portrait, as the screens show it at the end: the ear on the viewer's left too big, two Yemens on the
    backdrop (the generator's own code, with the left ear drawn larger and the maps added)."""
    src = open(S6.__file__).read()
    if big_ear:
        src = src.replace("""        ex2 = cx + sx * (6 * s)
        d.ellipse([ex2 - s - s // 2, top + 7 * s, ex2 + s + s // 2, top + 10 * s + s // 2], fill=skin, outline=OL)
        d.ellipse([ex2 - s // 2 - (s > 2), top + 8 * s, ex2 + s // 2, top + 9 * s + s // 2], fill=skin_d)""",
                          """        ex2 = cx + sx * (6 * s)
        if sx < 0:
            d.ellipse([ex2 - 3 * s, top + 5 * s, ex2 + s + s // 2, top + 13 * s], fill=skin, outline=OL)
            d.ellipse([ex2 - 2 * s, top + 6 * s + s // 2, ex2, top + 11 * s + s // 2], fill=skin_d)
            continue
        d.ellipse([ex2 - s - s // 2, top + 7 * s, ex2 + s + s // 2, top + 10 * s + s // 2], fill=skin, outline=OL)
        d.ellipse([ex2 - s // 2 - (s > 2), top + 8 * s, ex2 + s // 2, top + 9 * s + s // 2], fill=skin_d)""")
        assert 'if sx < 0' in src
    if yemens:
        # two maps of Yemen on the backdrop, behind him (drawn after the flag, before the podium and the man)
        hook = "d.rectangle([6 * s, 2 * s, 6 * s + max(1, s // 2), 28 * s], fill=(50, 40, 32))"
        assert src.count(hook) == 1
        src = src.replace(hook, hook + '''
    for mx, my in ((6.6, 8.0), (31.0, 8.0)):
        pts = [(mx * s + u * 8 * s, my * s + v * 5.5 * s) for u, v in YEMEN]
        d.polygon(pts, fill=(58, 128, 72), outline=(150, 210, 160))''')
    ns = {'YEMEN': [(0.03, 0.39), (0.04, 0.61), (0.07, 0.83), (0.085, 0.93), (0.24, 0.90), (0.62, 0.65), (0.82, 0.55),
                    (1.00, 0.35), (0.90, 0.00), (0.47, 0.22), (0.19, 0.25), (0.066, 0.38)]}
    exec(compile(src, 'fake_s6', 'exec'), ns)
    im = ns['s6'](s, mouth=mouth, blink=blink)
    return im


def small(im):
    return S._majority(im, 4)


def snow(seed):
    r = np.random.default_rng(seed)
    a = (r.random((32, 48)) * 200 + 30).astype(np.uint8)
    a[::3] = (a[::3] * 0.75).astype(np.uint8)
    rgb = np.stack([a, a, a], -1)
    return Image.fromarray(rgb).convert('RGBA')


def dark():
    return Image.new('RGBA', (48, 32), (8, 10, 12, 255))


def frozen():
    im = S.screen('podium', 1, False).copy()
    d = ImageDraw.Draw(im)
    d.rectangle([3, 3, 4, 8], fill=(250, 250, 250, 255))
    d.rectangle([7, 3, 8, 8], fill=(250, 250, 250, 255))
    return im


def podium_nomic():
    p = S.spk_pal()
    return S.compose([(S.PODIUM, 0, 0, p)], foot=(11, 14))


# ---------------------------------------------------------------- the lookout's things, as render_ibb.js draws them
def arena(im, cam, screens, mics, lights=1.0):
    """Each podium: its pole, its screen (a picture or None for the live face), its bezel, the podium (with or without its
    microphone)."""
    d = ImageDraw.Draw(im)
    pod = S.podium()
    nom = podium_nomic()
    for i, x in enumerate(PODS):
        sx = x - cam
        top = FLOOR - PS_LIFT - 40
        d.rectangle([sx - 1, top + 40, sx + 1, FLOOR - 1], fill=(22, 24, 28, 255))
        d.rectangle([sx - 1, top + 40, sx - 1, FLOOR - 2], fill=(74, 78, 86, 255))
        d.rectangle([sx - 6, FLOOR - 1, sx + 6, FLOOR - 1], fill=(22, 24, 28, 255))
        d.rectangle([sx - 4, FLOOR - 2, sx + 4, FLOOR - 2], fill=(22, 24, 28, 255))
        pic = screens[i]
        im.alpha_composite(pic, (sx - 24, top + 2))
        LK.spr(im, 'ps_box', sx - 26, top, ibb=True)
        put(im, pod if mics[i] else nom, sx, FLOOR, flip=True)


def him_at(im, cam, i, pose):
    """Him close behind podium i (the podium drawn over him), turned to Yazeed (left)."""
    x = PODS[i] - cam
    put(im, pose, x + 3, FLOOR, flip=True)


def shot(S_, cam):
    return LK.shot(S_, cam, [])


def bullets(im, x0, y0, x1, y1, n=3):
    d = ImageDraw.Draw(im)
    for k in range(n):
        u = (k + 1) / float(n + 1)
        bx, by = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
        d.rectangle([bx - 3, by, bx + 2, by], fill=(255, 236, 140, 255))
        d.point((bx + 3, by), fill=(255, 255, 230, 255))


def spark(im, x, y, r=4):
    d = ImageDraw.Draw(im)
    for dx, dy in ((0, -r), (0, r), (-r, 0), (r, 0), (-r + 1, -r + 1), (r - 1, r - 1), (r - 1, -r + 1), (-r + 1, r - 1)):
        d.line([(x, y), (x + dx, y + dy)], fill=(255, 246, 190, 255))
    d.point((x, y), fill=(255, 255, 255, 255))


def word(im, x, y, text, col=(255, 236, 120, 255)):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 9)
    w = d.textlength(text, font=f)
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1)):
        d.text((x - w / 2 + ox, y + oy), text, font=f, fill=(20, 14, 10, 255))
    d.text((x - w / 2, y), text, font=f, fill=col)


def darken(im, k=0.26, tint=(0.80, 0.86, 1.10)):
    a = np.asarray(im).astype(float)
    a[..., 0] *= k * tint[0]; a[..., 1] *= k * tint[1]; a[..., 2] *= k * tint[2]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


# ---------------------------------------------------------------- the Uncle's men (stand-ins: the cook's hands-up frame,
# re-dressed: a pale shirt, dark trousers, dark hair; headphones on)
def technician(k):
    A_ = LK.sheets()
    fx, fy, w, h, ax, ay = A_['af']['cook_up_stand']
    f = A_['atlas'].crop((fx, fy, fx + w, fy + h)).convert('RGBA')
    a = np.asarray(f).astype(int).copy()
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    shirts = [(120, 150, 190), (150, 150, 158), (176, 150, 112)]
    sr, sg, sb = shirts[k % 3]
    lum = (r + g + b) / 3.0
    sat = np.max(a[..., :3], -1) - np.min(a[..., :3], -1)
    green = (g > r + 8) & (g > b + 8) & (al > 0)
    apron = (lum > 170) & (sat < 40) & (al > 0)
    for c, base in ((0, sr), (1, sg), (2, sb)):
        a[..., c] = np.where(green, np.clip(base * (0.40 + lum / 160.0), 0, 255), a[..., c])
        a[..., c] = np.where(apron, np.clip(base * (0.80 + (lum - 170) / 300.0), 0, 255), a[..., c])
    greyish = (np.abs(r - g) < 12) & (np.abs(g - b) < 14) & (lum < 110) & (al > 0)
    ys = np.arange(h)[:, None] * np.ones((1, w))
    low = greyish & (ys > h * 0.55)
    a[..., 0] = np.where(low, 40 + lum * 0.3, a[..., 0]); a[..., 1] = np.where(low, 44 + lum * 0.3, a[..., 1]); a[..., 2] = np.where(low, 60 + lum * 0.35, a[..., 2])
    hair = greyish & (ys < h * 0.30)
    for c in range(3):
        a[..., c] = np.where(hair, 26 + lum * 0.25, a[..., c])
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(im)
    # the headphones: a band over the head and a cup on each ear
    cols = np.where(np.asarray(im)[..., 3][: int(h * 0.3)].any(axis=0))[0]
    rows = np.where(np.asarray(im)[..., 3].any(axis=1))[0]
    hx0, hx1 = int(cols.min()), int(cols.max())
    ht = int(rows.min())
    mid = (hx0 + hx1) // 2
    hl, hr = mid - 5, mid + 4
    d.arc([hl - 1, ht - 1, hr + 1, ht + 9], 180, 360, fill=(14, 14, 18, 255), width=2)
    d.rectangle([hl - 2, ht + 4, hl + 1, ht + 9], fill=(24, 24, 28, 255))
    d.rectangle([hr - 1, ht + 4, hr + 2, ht + 9], fill=(24, 24, 28, 255))
    d.point((hl, ht + 6), fill=(90, 90, 98, 255)); d.point((hr, ht + 6), fill=(90, 90, 98, 255))
    return im, ax, ay


def van_open(im, cam, smashed=False):
    """Their van's side door slid back along its side: the dark inside, the rack's lights, the big red button."""
    d = ImageDraw.Draw(im)
    x0, x1 = VAN['door'][0] - cam, VAN['door'][1] - cam
    top, sill = VAN['roof'] + 3, VAN['sill'] - 1
    # the door, slid back over the body behind it
    d.rectangle([x0 - 21, top, x0 - 1, sill], fill=(206, 202, 192, 255))
    d.line([(x0 - 21, top), (x0 - 21, sill)], fill=(120, 116, 110, 255))
    d.line([(x0 - 1, top), (x0 - 1, sill)], fill=(150, 146, 138, 255))
    d.rectangle([x0 - 21, top + 21, x0 - 1, top + 25], fill=(156, 40, 30, 255))
    # the inside
    d.rectangle([x0, top, x1, sill], fill=(14, 14, 18, 255))
    d.rectangle([x0 + 2, top + 2, x1 - 2, sill - 3], fill=(30, 32, 38, 255))
    for j in range(5):
        for i in range(4):
            on = not smashed and ((i * 7 + j * 3) % 5 != 0)
            col = (90, 230, 120, 255) if (i + j) % 3 else (240, 70, 50, 255)
            d.point((x0 + 4 + i * 4, top + 4 + j * 4), fill=col if on else (40, 40, 44, 255))
    d.rectangle([x0 + 6, sill - 9, x0 + 12, sill - 5], fill=(60, 60, 66, 255))
    d.rectangle([x0 + 7, sill - 8, x0 + 11, sill - 6], fill=(220, 40, 30, 255) if not smashed else (80, 30, 26, 255))
    if smashed:
        for (sx_, sy_) in ((x0 + 8, top + 8), (x0 + 15, top + 16), (x0 + 6, top + 20)):
            spark(im, sx_, sy_, 3)
        d.ellipse([x0 + 2, top - 10, x0 + 16, top + 2], fill=(70, 70, 74, 200))
        d.ellipse([x0 + 8, top - 18, x0 + 22, top - 6], fill=(96, 96, 100, 170))


def main():
    S_ = {k: from_image(Image.open(ART + 'i_%s.png' % k)) for k in ('sky', 'far', 'mid')}
    S_['far_y'], S_['mid_y'] = 10, 96
    S_['plays'] = [(Z4.X0, from_image(Image.open(ART + 'i_z4.png')))]
    S_['backs'] = [(Z2.BACK_X + Z2.BACK_W + 1410, from_image(Image.open(ART + 'i_back4.png')))]
    live = [S.screen('podium', m, False) for m in range(3)]
    F = frozen()
    cam = CAM_FIGHT
    Y = FLOOR

    # 1: the lookout; at the middle podium, all five screens on him, statement E; two of his men called in
    a = shot(S_, cam)
    arena(a, cam, [live[2]] * 5, [1] * 5)
    him_at(a, cam, 2, S.speech(2, trousers=False))
    LK.spr(a, 'yazeed_stand_side_fwd', PODS[0] - 40 - cam, Y)
    LK.spr(a, 'rifle_angry_run', PODS[4] + 50 - cam, Y, flip=True)
    LK.spr(a, 'rifle_youth_run', PODS[4] + 22 - cam, Y, flip=True)

    # 2: the microphone shot: cut off, stunned; every screen frozen on him; now he can be hit
    b = shot(S_, cam)
    arena(b, cam, [F] * 5, [1, 1, 0, 1, 1])
    put(b, S.spokesman_stunned(flip=True), PODS[2] + 3 - cam, Y - 2)
    put(b, podium_nomic(), PODS[2] - cam, Y, flip=True)
    yx = PODS[1] - 30
    LK.spr(b, 'yazeed_stand_side_fwd', yx - cam, Y)
    bullets(b, yx + 22 - cam, Y - 19, PODS[2] - 2 - cam, Y - 19)
    spark(b, PODS[2] - 2 - cam, Y - 19, 3)
    word(b, PODS[2] - cam, Y - 64, 'WHAT? SPEAK UP!')
    dd = ImageDraw.Draw(b)                                # (the microphone knocked off its stalk, flying)
    mx, my = PODS[2] + 12 - cam, Y - 34
    dd.ellipse([mx - 2, my - 2, mx + 2, my + 2], fill=(34, 34, 40, 255)); dd.point((mx - 1, my - 1), fill=(140, 140, 150, 255))
    dd.line([(mx + 2, my + 2), (mx + 5, my + 4)], fill=(30, 30, 30, 255))

    # 3: he leaps away over Yazeed to the first podium; the one he was cut off at shows snow
    c = shot(S_, cam)
    arena(c, cam, [live[1], live[1], snow(3), live[1], live[1]], [1, 1, 0, 1, 1])
    yx = PODS[1] + 4
    LK.spr(c, 'yazeed_stand_side_fwd', yx - cam, Y)
    d3 = ImageDraw.Draw(c)
    for k in range(18):                                   # (the arc of his leap, dotted)
        u = k / 17.0
        px_ = PODS[2] + (PODS[0] - PODS[2]) * u
        py_ = Y - 30 - 62 * 4 * u * (1 - u)
        if k % 2 == 0:
            d3.point((px_ - cam, py_), fill=(255, 255, 255, 200))
    put(c, S.spokesman_jump(flip=True), PODS[1] + 10 - cam, Y - 58)

    # 4: phase 2, two podiums left: shouting, one ear ringing; the feedback runs along the ground; Yazeed jumps it
    e = shot(S_, cam)
    arena(e, cam, [snow(5), live[2], snow(3), live[2], snow(7)], [0, 1, 0, 1, 0])
    him_at(e, cam, 3, S.speech(2, trousers=False, hot_ear=True))
    yx = PODS[1] + 6
    LK.spr(e, 'yazeed_jump_side_fwd', yx - cam, Y - 26)
    d4 = ImageDraw.Draw(e)
    for xx in range(int(PODS[1] - 30 - cam), int(PODS[3] - 14 - cam)):
        yy = Y - 3 - round(3 * np.sin(xx / 2.3)) * (1 if (xx // 9) % 2 else 0.5)
        d4.point((xx, yy), fill=(214, 248, 255, 255))
        d4.point((xx, yy + 1), fill=(120, 200, 230, 255))
    for k in range(3):
        d4.arc([PODS[3] - 26 - cam - 6 * k, Y - 14 - 3 * k, PODS[3] - 14 - cam - 6 * k, Y - 2 + 3 * k], 120, 240, fill=(214, 248, 255, 255))

    # 5: phase 3, the last podium: the lights out; he reads by torchlight, cornered; only his torch and his screen lit
    f = shot(S_, cam)
    f = darken(f)
    arena(f, cam, [dark(), live[1], dark(), dark(), dark()], [0, 1, 0, 0, 0])
    f2 = darken(f.copy(), 1.0)
    # (the podiums and poles in the dark too, but his screen lit)
    a5 = np.asarray(f).astype(float)
    mask = np.zeros(a5.shape[:2], bool)
    sx = PODS[1] - cam; top = Y - PS_LIFT - 40
    mask[top:top + 36, sx - 26:sx + 26] = True
    a5[~mask, :3] *= 0.55
    f = Image.fromarray(np.clip(a5, 0, 255).astype(np.uint8), 'RGBA')
    d5 = ImageDraw.Draw(f, 'RGBA')
    tx, ty = PODS[1] - 14 - cam, Y - 26                   # (his torch: the light on the page and his face)
    d5.polygon([(tx, ty), (tx - 26, ty - 22), (tx - 30, ty + 4)], fill=(255, 238, 170, 70))
    put(f, S.spokesman_reading(1, flip=True), PODS[1] + 3 - cam, Y)
    put(f, S.podium(), PODS[1] - cam, Y, flip=True)
    yz = Image.new('RGBA', f.size, (0, 0, 0, 0))
    LK.spr(yz, 'yazeed_stand_side_fwd', PODS[3] + 10 - cam, Y, flip=True)
    f.alpha_composite(darken(yz, 0.7, (1, 1, 1)))

    # 6: the last microphone shot, the last stun: caught, tied up in his own microphone cable; the lights back
    g = shot(S_, cam)
    arena(g, cam, [snow(5), snow(9), snow(3), snow(11), snow(7)], [0, 0, 0, 0, 0])
    put(g, S.spokesman_caught(flip=True), PODS[1] - 16 - cam, Y)
    LK.spr(g, 'yazeed_stand_side_fwd', PODS[1] - 50 - cam, Y)

    # 7: the screens come back on, all five: him, still speaking, though he stands there tied up; the ear too big, two
    #    Yemens on the backdrop. A close-up of the screen for a moment.
    fk = [small(fake_s6(4, m, big_ear=True, yemens=True)) for m in range(3)]
    h = shot(S_, cam)
    arena(h, cam, [fk[2], fk[1], fk[2], fk[1], fk[2]], [0, 0, 0, 0, 0])
    put(h, S.spokesman_caught(flip=True), PODS[1] - 16 - cam, Y)
    LK.spr(h, 'yazeed_stand_side_fwd', PODS[1] - 50 - cam, Y)
    big = fake_s6(2, 2, big_ear=True, yemens=True).resize((96 * 1, 64 * 1), Image.NEAREST)
    big = fake_s6(2, 2, big_ear=True, yemens=True)
    bx, by = I.SW // 2 - big.width // 2 + 70, 22
    dh = ImageDraw.Draw(h)
    dh.rectangle([bx - 3, by - 3, bx + big.width + 2, by + big.height + 2], fill=(20, 22, 26, 255))
    dh.rectangle([bx - 3, by - 3, bx + big.width + 2, by - 3], fill=(80, 84, 92, 255))
    h.alpha_composite(big, (bx, by))
    dh.ellipse([bx + 8, by + 26, bx + 26, by + 50], outline=(255, 220, 60, 255))

    # 8: their van, the back room: the door slides open; three of the Uncle's men come out, hands up
    cam2 = CAM_VAN
    k_ = shot(S_, cam2)
    arena(k_, cam2, [fk[1]] * 5, [0, 0, 0, 0, 0])
    van_open(k_, cam2)
    for n, tx in enumerate((VAN['door'][0] - 64, VAN['door'][0] - 46, VAN['door'][0] - 28)):
        put(k_, technician(n), tx - cam2, Y, flip=True)
    LK.spr(k_, 'yazeed_stand_side_fwd', VAN['door'][0] - 118 - cam2, Y)

    # 9: the rack smashed: every screen dark at once; the Uncle on the radio
    m_ = shot(S_, cam2)
    arena(m_, cam2, [dark()] * 5, [0, 0, 0, 0, 0])
    van_open(m_, cam2, smashed=True)
    for n, tx in enumerate((VAN['door'][0] - 64, VAN['door'][0] - 46, VAN['door'][0] - 28)):
        put(m_, technician(n), tx - cam2, Y, flip=True)
    yx = VAN['door'][0] - 100
    LK.spr(m_, 'yazeed_stand_side_fwd', yx - cam2, Y)
    bullets(m_, yx + 22 - cam2, Y - 19, VAN['door'][0] + 4 - cam2, Y - 24)

    # 10: close-ups: the screen as it was and as it is in picture 7 (at the billboard's size), the three technicians
    z = Image.new('RGBA', (I.SW, I.SH), (30, 28, 36, 255))
    dz = ImageDraw.Draw(z)
    n0 = S6.s6(2, mouth=1)
    n1 = fake_s6(2, 1, big_ear=True, yemens=True)
    z.alpha_composite(n0, (14, 16))
    z.alpha_composite(n1, (14 + 96 + 12, 16))
    dz.ellipse([14 + 96 + 12 + 8, 16 + 26, 14 + 96 + 12 + 26, 16 + 50], outline=(255, 220, 60, 255))
    f9 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)
    dz.text((14, 16 + 66), 'the approved picture', font=f9, fill=(220, 214, 200, 255))
    dz.text((14 + 108, 16 + 66), 'picture 7: the ear, two Yemens', font=f9, fill=(220, 214, 200, 255))
    tz = Image.new('RGBA', (90, 44), (0, 0, 0, 0))
    for n in range(3):
        put(tz, technician(n), 18 + n * 28, 40)
    tz = tz.resize((tz.width * 2, tz.height * 2), Image.NEAREST)
    z.alpha_composite(tz, (250, 12))
    dz.text((262, 104), 'the Uncle\'s men (stand-ins, x2)', font=f9, fill=(220, 214, 200, 255))
    # the podium screen and a cut one, at the game's size, and the frozen one
    for i, (pic, lab) in enumerate(((live[1], 'live'), (F, 'frozen'), (snow(3), 'cut off'), (fk[1], 'back on'), (dark(), 'dark'))):
        x_ = 14 + i * 90
        dz.rectangle([x_ - 2, 128 - 2, x_ + 49, 128 + 33], fill=(26, 28, 32, 255))
        z.alpha_composite(pic, (x_, 128))
        dz.text((x_, 166), lab, font=f9, fill=(220, 214, 200, 255))
    dz.text((14, 186), 'a podium\'s screen at the game\'s size (48 x 32)', font=f9, fill=(170, 164, 150, 255))

    frames = [
        (a, '1  The lookout at the top of the pass. The camera holds. He is at a podium, every screen on him, giving statement E\n'
            '    ("The Zanabeel confirm that the Uncle is satisfied."), calm, correcting it as he goes. Each statement calls men in.'),
        (b, '2  Shoot the microphone on the podium he is speaking from: it flies off and he is cut off mid-word, "WHAT? SPEAK UP!",\n'
            '    a hand to his ear, for a few seconds. Only now can he be hurt. Every screen freezes on his face.'),
        (c, '3  Then he leaps to another podium, over Yazeed (touching him hurts). The podium he was cut off at is done:\n'
            '    its screen shows snow and he can\'t use it again, so the lookout shrinks podium by podium.'),
        (e, '4  Two podiums left: he shouts, one ear ringing, and the feedback from his microphone runs along the ground\n'
            '    as a shriek. Jump it.'),
        (f, '5  The last podium: the cloud closes in and the lights go out. He reads the statement by torchlight, cornered;\n'
            '    the lookout lit only by his torch and his last screen.'),
        (g, '6  The last microphone shot, the last stun: caught, tied up in his own microphone cable.'),
        (h, '7  The screens come back on, all five: he is still speaking, though he stands there tied up, mouth shut. On the\n'
            '    screens the ear on the viewer\'s left is too big and there are two Yemens on the backdrop (a close-up comes up).'),
        (k_, '8  Their cables lead to their van. Its door slides open: the back room, a rack of machines, a button marked\n'
             '    RENDER. Three of the Uncle\'s men, headphones on; they don\'t fight, hands up: "We only do the videos!" (Persian under it).'),
        (m_, '9  Smash the rack: every screen in Ibb goes dark at once, for good. The Uncle, on the radio: "Render him again." /\n'
             '    "We cannot." / "Then render me." The cloud clears onto the Dhamar plateau. Mission Complete.'),
        (z, '10  Close-ups: the screen as approved and as it is in picture 7; the Uncle\'s men (stand-ins: their own sprites come\n'
             '     with the build); a podium\'s screen at the game\'s size: live, frozen (2), cut off (3), back on (7), dark (9).'),
    ]
    sc = 2
    W, H = I.SW * sc, I.SH * sc
    cap_h = 78
    rows = (len(frames) + 1) // 2
    sheet = Image.new('RGB', (W * 2 + 12, (H + cap_h + 12) * rows), (24, 20, 28))
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    dr = ImageDraw.Draw(sheet)

    def wrap(text, width):
        words = ' '.join(text.split()).split(' ')
        num, words = words[0], words[1:]
        lines, cur = [], num + ' '
        for w_ in words:
            t = cur + ('' if cur.endswith(' ') else ' ') + w_
            if dr.textlength(t, font=font) > width and cur.strip() != num:
                lines.append(cur.rstrip()); cur = '    ' + w_
            else:
                cur = t
        lines.append(cur)
        return '\n'.join(lines)

    for i, (im, text) in enumerate(frames):
        x0, y0 = (i % 2) * (W + 12), (i // 2) * (H + cap_h + 12)
        sheet.paste(im.convert('RGB').resize((W, H), Image.NEAREST), (x0, y0))
        dr.multiline_text((x0 + 10, y0 + H + 8), wrap(text, W - 24), fill=(236, 230, 214), font=font, spacing=4)
    sheet.save(OUT + 'ibb_pass_mock.png')
    print(sheet.size, 'cam', cam, 'van cam', cam2)


if __name__ == '__main__':
    main()
