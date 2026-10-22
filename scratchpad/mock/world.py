# world.py - scenery, props, effects and UI primitives shared by the mock screens.
import math
from px import *
from palette import P

C = dict(
    sky1='#f0ead8', sky2='#dce6e0', sky3='#bcd4de', sky4='#9cc0d6', sky5='#7ca8c8', sky6='#648fb4',
    sea1='#dcece0', sea2='#a4ccc0', sea3='#6ca8ac', sea4='#48889c', sea5='#346c88', sea6='#27506c',
    sand1='#f0e2c0', sand2='#e0cca4', sand3='#cab48c', sand4='#ae9670', sand5='#8a7456', sand6='#6a5842',
    rock1='#ccb090', rock2='#a88c6e', rock3='#846a52', rock4='#5e4a3c', rock5='#3e302a',
    leaf1='#98b060', leaf2='#6c8844', leaf3='#4a6636', leaf4='#30462a',
    trunk1='#a88866', trunk2='#80644a', trunk3='#584434',
    haze='#c8d8dc', cloud='#f6f4ea', clouds='#c4d2d8', cloudm='#e0e6e2',
    fire1='#fff6c8', fire2='#ffd84a', fire3='#fb9a2a', fire4='#dc4c1c', fire5='#7c2420',
    smoke1='#c8c2bc', smoke2='#9a948e', smoke3='#6c6664', smoke4='#48423e',
    bag1='#d0c098', bag2='#b0a074', bag3='#867654', bag4='#5c503a',
)
INK = '#1c1418'


def profile(n, seed, amp, step=10, smooth=True):
    """A lumpy 1-D height profile of n samples in [0, amp]."""
    r = rng(seed)
    pts = [r.random() * amp for _ in range(n // step + 3)]
    out = []
    for i in range(n):
        a, f = divmod(i / step, 1)
        a = int(a)
        if smooth:
            f = f * f * (3 - 2 * f)
        out.append(pts[a] + (pts[a + 1] - pts[a]) * f)
    return out


def cloud(im, x, y, w, seed, light=None, shade=None, h=14):
    """A cumulus bank: lumpy top, long flat base, three tones with dithered seams."""
    light = rgba(light or C['cloud'])
    shade = rgba(shade or C['clouds'])
    mid = rgba(C['cloudm'])
    r = rng(seed)
    top = profile(w, seed, h, step=9)
    px = im.load()
    for i in range(w):
        t = i / max(1, w - 1)
        env = min(1.0, t * 5, (1 - t) * 5) ** 0.6
        hh = int((3 + top[i]) * env)
        for j in range(hh):
            xx, yy = x + i, y - j
            if not (0 <= xx < im.width and 0 <= yy < im.height):
                continue
            f = j / max(1, hh)
            if f > 0.55 or (f > 0.4 and BAYER4[yy % 4][xx % 4] < 8):
                c = light
            elif f > 0.2 or (f > 0.1 and BAYER4[yy % 4][xx % 4] < 8):
                c = mid
            else:
                c = shade
            px[xx, yy] = c
        # wisps under the base
        if hh > 3 and (i + seed) % 5 < 2:
            xx, yy = x + i, y + 1
            if 0 <= xx < im.width and 0 <= yy < im.height:
                px[xx, yy] = shade


def sea(im, y0, y1, seed=3, colors=None):
    colors = colors or [C['sea6'], C['sea5'], C['sea5'], C['sea4'], C['sea4'], C['sea3'], C['sea2']]
    vbands(im, 0, y0, im.width - 1, y1, colors, soft=3)
    r = rng(seed)
    for y in range(y0 + 2, y1):
        t = (y - y0) / (y1 - y0)
        n = int(2 + t * 6)
        for _ in range(n):
            x = r.randint(0, im.width)
            ln = r.randint(2, int(3 + t * 14))
            if r.random() < 0.5:
                c = C['sea3'] if t < 0.5 else C['sea1']
            else:
                c = C['sea5'] if t > 0.35 else C['sea6']
            if r.random() < 0.45 + t * 0.3:
                hline(im, x, x + ln, y, c)


def sand(im, y0, y1, seed=5):
    vbands(im, 0, y0, im.width - 1, y1,
           [C['sand1'], C['sand2'], C['sand2'], C['sand3'], C['sand3'], C['sand4'], C['sand4']], soft=3)
    r = rng(seed)
    px = im.load()
    # wind ripples: broken wavy lines, denser toward the viewer
    yy = y0 + 6
    k = 0
    while yy < y1:
        wob = profile(im.width, seed * 7 + k, 3, step=22)
        for x in range(im.width):
            y = yy + int(wob[x])
            if y0 < y < y1 and (x * 3 + k * 11) % 29 > 6:
                px[x, y] = rgba(C['sand4'] if (y - y0) < (y1 - y0) * 0.6 else C['sand5'])
                if y + 1 <= y1 and (x + k) % 3 == 0:
                    px[x, y + 1] = rgba(C['sand1'] if (y - y0) < (y1 - y0) * 0.5 else C['sand2'])
        yy += 6 + k
        k += 1
    for _ in range(420):
        x, y = r.randint(0, im.width - 1), r.randint(y0 + 1, y1)
        t = (y - y0) / (y1 - y0)
        c = r.choice([C['sand3'], C['sand4']]) if t < 0.5 else r.choice([C['sand4'], C['sand5'], C['sand3']])
        hline(im, x, x + r.choice([0, 0, 0, 1, 1, 2]), y, c)
    for _ in range(70):
        x, y = r.randint(0, im.width - 1), r.randint(y0 + 2, y1)
        put(im, x, y, C['sand1'])


def rock(im, x0, x1, ybase, heights, seed=7, pal=None, ledges=True, strata=0):
    """A stepped rock mass. heights[i] = height above ybase at column x0+i."""
    pal = pal or [C['rock1'], C['rock2'], C['rock3'], C['rock4'], C['rock5']]
    r = rng(seed)
    w = x1 - x0 + 1
    hs = [int(heights[min(i, len(heights) - 1)]) for i in range(w)]
    for i in range(w):
        h = hs[i]
        if h <= 0:
            continue
        top = ybase - h
        vline(im, x0 + i, top, ybase, pal[1])
        vline(im, x0 + i, top, top + 1, pal[0])
        shade_from = top + int(h * 0.5)
        for y in range(shade_from, ybase + 1):
            if BAYER4[y % 4][(x0 + i) % 4] < 5 + (y - shade_from) * 11 // max(1, ybase - shade_from):
                put(im, x0 + i, y, pal[2])
    for i in range(1, w):
        if hs[i] < hs[i - 1] - 1:
            for k in range(0, 3):
                if i + k < w:
                    vline(im, x0 + i + k, ybase - hs[i - 1] + 2, ybase - hs[i], pal[2] if k else pal[3])
        if hs[i] > hs[i - 1] + 1:
            vline(im, x0 + i, ybase - hs[i], ybase - hs[i - 1], pal[0])
    for _ in range(w // 5):
        i = r.randint(1, w - 2)
        if hs[i] < 8:
            continue
        ytop = ybase - hs[i] + r.randint(2, max(3, hs[i] // 2))
        ln = r.randint(3, max(4, hs[i] // 3))
        for k in range(ln):
            put(im, x0 + i + (1 if (k // 3) % 2 else 0), ytop + k, pal[3])
    if strata:
        px_ = im.load()
        y = ybase - strata + r.randint(-2, 2)
        k = 0
        while y > ybase - max(hs) + 4:
            wob = profile(w, seed * 13 + k, 3, step=16)
            for i in range(w):
                yy = y + int(wob[i])
                if ybase - hs[i] + 3 < yy < ybase - 1 and (i + k * 5) % 23 > 3:
                    xx = x0 + i
                    if 0 <= xx < im.width and 0 <= yy < im.height - 1:
                        px_[xx, yy] = rgba(pal[3])
                        if (i + k) % 3:
                            px_[xx, yy + 1] = rgba(pal[0])
            y -= strata + r.randint(-2, 3)
            k += 1
    if ledges:
        for _ in range(w // 7):
            i = r.randint(1, max(2, w - 10))
            if hs[i] < 10:
                continue
            y = ybase - r.randint(3, hs[i] - 4)
            ln = r.randint(4, 10)
            for k in range(ln):
                if i + k < w and ybase - hs[i + k] < y:
                    put(im, x0 + i + k, y, pal[0])
                    put(im, x0 + i + k, y + 1, pal[3])


def palm(im, x, ybase, h, seed=1, lean=4, fronds=9, edge=None, haze=None, size=1.0, dates=True):
    """Date palm. Drawn on its own layer so it can be outlined or hazed."""
    lay = new(im.width + 120, im.height + 60)
    X, Y = x + 60, ybase + 30
    r = rng(seed)
    tw = 2 if size < 0.9 else 3
    pts = []
    for i in range(h + 1):
        t = i / h
        pts.append((X + int(round(lean * t * t)), Y - i))
    for i, (tx, ty) in enumerate(pts):
        rect(lay, tx - tw + 1, ty, tx + tw - 1, ty, C['trunk2'])
        put(lay, tx - tw + 1, ty, C['trunk1'])
        put(lay, tx + tw - 1, ty, C['trunk3'])
        if i % 4 == 0:
            rect(lay, tx - tw + 1, ty, tx + tw - 1, ty, C['trunk3'])
        if i % 4 == 1:
            put(lay, tx - tw + 2, ty, C['trunk1'])
    cx, cy = pts[-1]
    angs = [(-178 + i * (176 / (fronds - 1))) for i in range(fronds)]
    order = sorted(range(fronds), key=lambda k: -abs(k - (fronds - 1) / 2))
    for k in order:
        a = angs[k] + r.uniform(-7, 7)
        L = int((20 + r.randint(0, 7)) * size)
        droop = r.uniform(0.55, 0.95)
        ar = math.radians(a)
        back = k % 2 == 1
        for i in range(L + 1):
            t = i / L
            fx = int(round(cx + math.cos(ar) * L * t * 1.15))
            fy = int(round(cy + math.sin(ar) * L * t * 0.7 + droop * (t * t) * L * 0.9))
            ll = max(1, int(4.6 * size * math.sin(math.pi * min(1, t * 1.05)) + 1))
            vline(lay, fx, fy + 1, fy + ll, C['leaf4'] if back else C['leaf3'])
            if i % 2 == 0 and ll > 2:
                put(lay, fx, fy + ll, C['leaf4'])
            put(lay, fx, fy, C['leaf3'] if back else C['leaf2'])
            put(lay, fx, fy - 1, C['leaf2'] if back else C['leaf1'])
    disc(lay, cx, cy, 2 if size < 0.9 else 3, C['trunk3'])
    if dates:
        for dx, dy in ((-3, 3), (2, 4), (0, 3), (-1, 5), (3, 2)):
            put(lay, cx + dx, cy + dy, '#e09440')
            put(lay, cx + dx, cy + dy + 1, '#b8682c')
    if edge:
        lay = outline(lay, edge)
        blit(im, lay, -61, -31)
    else:
        if haze:
            lay = tint(lay, haze[0], haze[1])
        blit(im, lay, -60, -30)


def soft_outline(im, strength=0.42, tint=(40, 26, 34)):
    """Outline in darkened local colour instead of flat black: closer to hand-drawn arcade art."""
    wd, hg = im.size
    out = new(wd + 2, hg + 2)
    out.alpha_composite(im, (1, 1))
    src = out.copy().load()
    o = out.load()
    for y in range(hg + 2):
        for x in range(wd + 2):
            if src[x, y][3] == 0:
                acc, n = [0, 0, 0], 0
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < wd + 2 and 0 <= yy < hg + 2 and src[xx, yy][3] > 0:
                        c = src[xx, yy]
                        acc[0] += c[0]; acc[1] += c[1]; acc[2] += c[2]
                        n += 1
                if n:
                    o[x, y] = (int(acc[0] / n * strength * 0.7 + tint[0] * 0.3),
                               int(acc[1] / n * strength * 0.7 + tint[1] * 0.3),
                               int(acc[2] / n * strength * 0.7 + tint[2] * 0.3), 255)
    return out


def volume(mask, ramp, cuts=(0.10, 0.5, 0.82), soft=0.07, by='y'):
    """Shade a flat silhouette as a solid: light on top, dark underneath, dithered seams.
    ramp = (light, base, shade, dark)."""
    cols = [rgba(c) for c in ramp]
    wd, hg = mask.size
    m = mask.load()
    out = new(wd, hg)
    o = out.load()
    if by == 'y':
        for x in range(wd):
            ys = [y for y in range(hg) if m[x, y][3]]
            if not ys:
                continue
            y0, y1 = ys[0], ys[-1]
            for y in ys:
                t = (y - y0) / max(1, y1 - y0)
                d = (BAYER4[y % 4][x % 4] / 16 - 0.5) * 2 * soft
                tt = t + d
                i = 0 if tt < cuts[0] else (1 if tt < cuts[1] else (2 if tt < cuts[2] else 3))
                o[x, y] = cols[i]
    else:
        for y in range(hg):
            xs = [x for x in range(wd) if m[x, y][3]]
            if not xs:
                continue
            x0, x1 = xs[0], xs[-1]
            for x in xs:
                t = (x - x0) / max(1, x1 - x0)
                d = (BAYER4[y % 4][x % 4] / 16 - 0.5) * 2 * soft
                tt = t + d
                i = 0 if tt < cuts[0] else (1 if tt < cuts[1] else (2 if tt < cuts[2] else 3))
                o[x, y] = cols[i]
    return out


def grit(im, seed, dark=0.82, light=1.12, amount=0.05):
    """Weathering: scattered flecks of slightly darker or lighter local colour."""
    r = rng(seed)
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            c = px[x, y]
            if c[3] and r.random() < amount:
                f = dark if r.random() < 0.65 else light
                px[x, y] = (min(255, int(c[0] * f)), min(255, int(c[1] * f)), min(255, int(c[2] * f)), c[3])
    return im


# ------------------------------------------------------------------ props
def _placed(im, lay, x, ybase, edge=INK, center=False):
    lay = lay.crop(lay.getbbox())
    o = soft_outline(lay) if edge else lay
    blit(im, o, x - (o.width // 2 if center else 1), ybase - o.height + 1)
    return o.size


def sandbags(im, x, ybase, cols, rows):
    """Stack of sandbags; x is the left edge, ybase the ground line."""
    bw, bh = 13, 6
    lay = new(cols * bw + 10, rows * bh + 2)
    for rr in range(rows):
        off = 0 if rr % 2 == 0 else bw // 2
        n = cols if rr % 2 == 0 else cols - 1
        for cc in range(n):
            bx = cc * bw + off
            by = lay.height - (rr + 1) * bh
            rrect(lay, bx, by, bx + bw - 1, by + bh - 1, C['bag2'], r=2)
            rect(lay, bx + 2, by, bx + bw - 3, by + 1, C['bag1'])
            rect(lay, bx + 1, by + bh - 1, bx + bw - 2, by + bh - 1, C['bag3'])
            rect(lay, bx + bw - 2, by + 2, bx + bw - 1, by + bh - 2, C['bag3'])
            put(lay, bx + 6, by + 2, C['bag3'])
            put(lay, bx + 5, by + 3, C['bag3'])
            put(lay, bx + 7, by + 3, C['bag4'])
            hline(lay, bx, bx + bw - 1, by + bh - 1, C['bag4']) if rr == 0 else None
    return _placed(im, lay, x, ybase)


def drum(im, x, ybase, color='red', w=13, h=18):
    base, sh, li, dk = {'red': ('#a04a3c', '#74322e', '#c47860', '#4c2020'),
                        'blue': ('#44688c', '#2e4a68', '#7098b8', '#1e3248'),
                        'olive': ('#747c50', '#525a3a', '#9aa070', '#383c28'),
                        'yel': ('#c8a03c', '#96742c', '#e4c870', '#64501c')}[color]
    lay = new(w, h)
    rect(lay, 0, 0, w - 1, h - 1, base)
    rect(lay, w - 4, 0, w - 1, h - 1, sh)
    rect(lay, 1, 0, 2, h - 1, li)
    for yy in (0, h // 3, 2 * h // 3, h - 1):
        rect(lay, 0, yy, w - 1, yy, sh)
        rect(lay, 0, yy, 2, yy, base)
    rect(lay, 0, 0, w - 1, 0, li)
    rect(lay, 0, h - 1, w - 1, h - 1, dk)
    return _placed(im, lay, x, ybase)


def crate(im, x, ybase, label=None, w=18, h=15):
    lay = new(w, h)
    rect(lay, 0, 0, w - 1, h - 1, P['wood'])
    rect(lay, 0, 0, w - 1, 1, P['woodl'])
    rect(lay, 0, h - 2, w - 1, h - 1, P['woods'])
    rect(lay, 0, 0, 1, h - 1, P['woodl'])
    rect(lay, w - 2, 0, w - 1, h - 1, P['woods'])
    rect(lay, 2, 4, w - 3, 4, P['woods'])
    rect(lay, 2, h - 5, w - 3, h - 5, P['woods'])
    line(lay, 2, 5, w - 3, h - 6, P['woods'])
    for xx in (1, w - 2):
        for yy in (1, h - 2):
            put(lay, xx, yy, P['st2'])
    if label:
        t = text_img(label, FONT_S, P['yel'])
        rect(lay, w // 2 - t.width // 2 - 1, 5, w // 2 + t.width // 2 + 1, h - 6, P['woodd'])
        blit(lay, t, w // 2 - t.width // 2, 6)
    return _placed(im, lay, x, ybase)


def shadow(im, cx, y, w, alpha=70):
    lay = new(w + 2, 5)
    rect(lay, 1, 1, w, 3, (20, 14, 30, alpha))
    rect(lay, 4, 0, w - 3, 0, (20, 14, 30, alpha))
    rect(lay, 4, 4, w - 3, 4, (20, 14, 30, alpha))
    blit(im, lay, cx - w // 2 - 1, y - 2)


# ------------------------------------------------------------------ effects
def muzzle(im, x, y, s=2):
    """Flash pointing right from (x, y)."""
    poly(im, [(x, y - 2 * s), (x + 4 * s, y - 5 * s), (x + 4 * s, y - 2 * s), (x + 11 * s, y),
              (x + 4 * s, y + 2 * s), (x + 4 * s, y + 5 * s), (x, y + 2 * s)], C['fire4'])
    poly(im, [(x, y - 2 * s), (x + 3 * s, y - 4 * s), (x + 3 * s, y - s), (x + 9 * s, y),
              (x + 3 * s, y + s), (x + 3 * s, y + 4 * s), (x, y + 2 * s)], C['fire3'])
    poly(im, [(x, y - s), (x + 2 * s, y - 2 * s), (x + 3 * s, y), (x + 6 * s, y),
              (x + 3 * s, y), (x + 2 * s, y + 2 * s), (x, y + s)], C['fire2'])
    rect(im, x, y - s + 1, x + 2 * s, y + s - 1, C['fire1'])


def tracer(im, x, y, ln=12):
    rect(im, x - 4, y, x + ln, y + 1, C['fire3'])
    rect(im, x, y, x + ln, y, C['fire2'])
    rect(im, x + ln - 5, y, x + ln, y + 1, C['fire1'])
    rect(im, x + ln + 1, y, x + ln + 1, y + 1, C['fire2'])
    hline(im, x - 9, x - 5, y + 1, C['fire4'])


def explosion(im, cx, cy, r, seed=1, smoke=True):
    """Arcade fireball: smoke lobes, then red, orange, yellow, white cores."""
    rr = rng(seed)
    lobes = []
    n = max(6, r // 2 + 5)
    for i in range(n):
        a = i / n * math.tau + rr.uniform(-0.3, 0.3)
        d = r * rr.uniform(0.35, 0.75)
        lobes.append((cx + math.cos(a) * d, cy + math.sin(a) * d * 0.85, r * rr.uniform(0.38, 0.62)))
    if smoke:
        for lx, ly, lr in lobes:
            disc(im, int(lx + (lx - cx) * 0.45), int(ly + (ly - cy) * 0.45 - r * 0.15), max(2, int(lr * 0.9)), C['smoke4'])
        for lx, ly, lr in lobes[::2]:
            disc(im, int(lx + (lx - cx) * 0.5) - 1, int(ly + (ly - cy) * 0.5 - r * 0.2) - 1, max(1, int(lr * 0.55)), C['smoke3'])
    for lx, ly, lr in lobes:
        disc(im, int(lx), int(ly), max(2, int(lr)), C['fire5'])
    for lx, ly, lr in lobes:
        disc(im, int(cx + (lx - cx) * 0.9), int(cy + (ly - cy) * 0.9), max(2, int(lr * 0.86)), C['fire4'])
    for lx, ly, lr in lobes:
        disc(im, int(cx + (lx - cx) * 0.75), int(cy + (ly - cy) * 0.75), max(1, int(lr * 0.7)), C['fire3'])
    for lx, ly, lr in lobes:
        disc(im, int(cx + (lx - cx) * 0.55), int(cy + (ly - cy) * 0.55), max(1, int(lr * 0.52)), C['fire2'])
    disc(im, cx, cy, max(1, int(r * 0.3)), C['fire1'])
    for lx, ly, lr in lobes[::3]:
        disc(im, int(cx + (lx - cx) * 0.35), int(cy + (ly - cy) * 0.35), max(1, int(lr * 0.3)), C['fire1'])
    for _ in range(max(6, r)):
        a = rr.uniform(0, math.tau)
        d = r * rr.uniform(1.05, 1.75)
        x, y = int(cx + math.cos(a) * d), int(cy + math.sin(a) * d * 0.9)
        c = rr.choice([C['fire2'], C['fire3'], C['fire1']])
        put(im, x, y, c)
        if rr.random() < 0.5:
            put(im, x + 1, y, C['fire3'])
            put(im, x, y + 1, C['fire4'])


def puff(im, cx, cy, r, c1=None, c2=None, c3=None):
    c1 = c1 or C['smoke1']
    c2 = c2 or C['smoke2']
    disc(im, cx, cy, r, c3 or c2)
    disc(im, cx, cy, max(0, r - 1), c2)
    disc(im, cx - 1, cy - 1, max(0, r - 2), c1)


def debris(im, cx, cy, n, spread, colors, seed=1):
    r = rng(seed)
    for _ in range(n):
        a = r.uniform(-math.pi, 0)
        d = r.uniform(0.3, 1.0) * spread
        x, y = int(cx + math.cos(a) * d), int(cy + math.sin(a) * d)
        c = r.choice(colors)
        w, h = r.choice([(1, 1), (2, 1), (2, 2), (3, 2)])
        rect(im, x, y, x + w - 1, y + h - 1, c)
        put(im, x + w - 1, y + h - 1, INK)


# ------------------------------------------------------------------ UI
UI = dict(panel=(24, 18, 34, 150), panel2=(24, 18, 34, 215), line='#f4ecd0', dim='#a89c88',
          amber='#f8b830', green='#58c858', red='#e8483c', blue='#58aaf0',
          cream='#f4ecd0', ink=INK)


def pill(im, x0, y0, x1, y1, c=None, r=2):
    lay = new(x1 - x0 + 1, y1 - y0 + 1)
    rrect(lay, 0, 0, x1 - x0, y1 - y0, c or UI['panel'], r=r)
    blit(im, lay, x0, y0)


def frame(im, x0, y0, x1, y1, c):
    rect(im, x0 + 1, y0, x1 - 1, y0, c)
    rect(im, x0 + 1, y1, x1 - 1, y1, c)
    rect(im, x0, y0 + 1, x0, y1 - 1, c)
    rect(im, x1, y0 + 1, x1, y1 - 1, c)


def bubble(im, x, y, lines, tail_x=None, font=FONT_M, fg=None, bg=None, tail_dir=1, pad=4):
    """Speech bubble whose tail tip points at (x, y)."""
    fg = fg or UI['ink']
    bg = bg or '#fbf8ec'
    if isinstance(lines, str):
        lines = [lines]
    lh = font_h(font) + 3
    w = max(text_w(l, font) for l in lines) + pad * 2 + 1
    h = len(lines) * lh + pad * 2 - 3
    lay = new(w + 8, h + 9)
    rrect(lay, 0, 0, w - 1, h - 1, bg, r=3)
    rect(lay, 2, h - 2, w - 3, h - 1, '#ddd6c2')
    tx = w // 2 if tail_x is None else tail_x
    poly(lay, [(tx - 3, h - 2), (tx + 3, h - 2), (tx + (4 * tail_dir), h + 5)], bg)
    for i, l in enumerate(lines):
        text(lay, pad + 1, pad + i * lh, l, font, fg)
    lay = lay.crop(lay.getbbox())
    o = outline(lay, UI['ink'])
    tipx = tx + 4 * tail_dir + 1
    blit(im, o, x - tipx, y - o.height + 1)
    return o.size


def banner(im, cx, y, s, scale_=2, grad=None, edge=None, font=None):
    """Arcade announcer text: bold caps, vertical gradient, double edge, drop shadow."""
    grad = grad or ['#fffbe0', '#fff0a0', '#ffd84a', '#ffb62c', '#f8902c', '#e8641c']
    b = text_img(s, font or FONT_B, '#ffffff', sp=1)
    b = b.crop((0, 0, b.width, font_h(font or FONT_B)))
    b = scale(b, scale_)
    px_ = b.load()
    hgt = b.height
    for yy in range(hgt):
        c = rgba(grad[min(len(grad) - 1, yy * len(grad) // hgt)])
        for xx in range(b.width):
            if px_[xx, yy][3]:
                px_[xx, yy] = c
    o = outline(b, '#8c2c1c', diag=True)
    o = outline(o, edge or UI['ink'], diag=True)
    sh = silhouette(o, (20, 14, 30, 150))
    x = cx - o.width // 2
    blit(im, sh, x + scale_, y + scale_ + 1)
    blit(im, o, x, y)
    return o.width
