# boom.py - explosions as short films: a flash, a ball of fire that rolls up and breaks into lumps, smoke that
# climbs away and thins. Each frame is drawn from the same few dozen moving puffs, so the frames follow on from
# one another the way hand-drawn ones do. Fire is banded hot to dark; smoke is lit from the upper left.
import sys, os, math
MOCK = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/mock'
sys.path.insert(0, MOCK)
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
from paint import ramp, rng, fbm, noise, light, BAYER4

FIRE = ramp(['#3a0c06', '#7c1a06', '#b8300a', '#e4580e', '#f88c1c', '#fcbc3c', '#ffe478', '#fff6c0', '#fffdf0'], 18)
SMOKE = ramp(['#1c1612', '#2e2620', '#443a30', '#5c5044', '#766a5a', '#928672', '#aea48e'], 12)
DUST = ramp(['#7a4c24', '#a47438', '#c69a54', '#deb870', '#f0d08c', '#fae4ac'], 10)


def ease(u):
    u = min(1.0, max(0.0, u))
    return 1 - (1 - u) ** 3


def field(yy, xx, pts):
    """Sum of smooth bumps: pts is a list of (x, y, r, weight)."""
    F = np.zeros(yy.shape)
    for x, y, r, w in pts:
        if r <= 0.3 or w <= 0:
            continue
        d2 = ((xx - x) ** 2 + (yy - y) ** 2) / (r * r)
        F += w * np.clip(1 - d2, 0, None) ** 2
    return F


def heap(yy, xx, pts):
    """Height of a heap of balls: for lighting the smoke."""
    Z = np.zeros(yy.shape)
    for x, y, r, w in pts:
        if r <= 0.6:
            continue
        z = np.sqrt(np.clip(r * r - ((xx - x) ** 2 + (yy - y) ** 2), 0, None))
        Z = np.maximum(Z, z)
    return Z


def banded(t, rmp, dither, x0=0, y0=0):
    h, w = t.shape
    n = len(rmp)
    f = np.clip(t, 0, 1) * (n - 1)
    i0 = np.floor(f)
    frac = f - i0
    fr = np.clip((frac - 0.5) / max(dither, 1e-6) + 0.5, 0, 1) if dither > 0 else (frac > 0.5).astype(float)
    thr = BAYER4[(np.arange(h)[:, None] + y0) % 4, (np.arange(w)[None, :] + x0) % 4]
    idx = np.clip(i0 + (fr > thr), 0, n - 1).astype(int)
    return rmp[idx]


def frames(R=26, n=16, seed=1, ground=True, dust=True):
    """Returns a list of (RGBA image, anchor x, anchor y). The anchor is the point of the blast: on the ground for a
    ground burst, the middle for one in the air."""
    rg = rng(seed)
    W = int(R * 4.6) | 1
    up = int(R * 4.6)
    down = 4 if ground else int(R * 1.8)
    H = up + down
    cx, cy = W // 2, up
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    # ---- the cast: lobes of fire thrown out from the middle, each with its own direction, reach, size and staying power
    N = 22 if R >= 32 else 16
    puffs = []
    for i in range(N):
        if ground:
            a = -math.pi / 2 + rg.uniform(-1, 1) * math.pi * 0.52
        else:
            a = rg.uniform(-math.pi, math.pi)
        k = (i + 0.5) / N                          # 0: stays near the middle and burns longest; 1: thrown furthest, cools first
        reach = (0.18 + 0.86 * k) * R * rg.uniform(0.85, 1.12)
        puffs.append(dict(a=a, reach=reach, r=(0.52 - 0.20 * k) * R * rg.uniform(0.85, 1.2), h0=1.5 - 0.42 * k, rate=1.75 + 1.5 * k + rg.uniform(-0.2, 0.2),
                          lift=rg.uniform(0.75, 1.25) * (1.15 - 0.35 * k), late=0.05 * k * rg.uniform(0, 1), sway=rg.uniform(-1, 1), spin=rg.uniform(-1, 1)))
    sparks = [dict(a=(-math.pi / 2 + rg.uniform(-1, 1) * math.pi * 0.47) if ground else rg.uniform(-math.pi, math.pi), v=rg.uniform(1.7, 3.0) * R, g=rg.uniform(0.6, 1.6) * R)
              for _ in range(8 if R < 32 else 13)]
    jets = [dict(a=-math.pi / 2 + rg.uniform(-1, 1) * math.pi * 0.44, v=rg.uniform(1.3, 2.3) * R, w=rg.uniform(1.2, 2.2)) for _ in range(7)] if (ground and dust) else []
    nz = fbm((H * 2, W), seed + 7, 4.0, 4.0, octaves=3)
    nz2 = fbm((H, W), seed + 11, 2.2, 2.2, octaves=2)
    out = []
    for f in range(n):
        u = f / float(n - 1)
        rgb = np.zeros((H, W, 3), np.uint8)
        al = np.zeros((H, W), bool)
        spts, fl = [], []
        for p_ in puffs:
            uu = max(0.0, u - p_['late'])
            out_k = ease(uu * 3.0)
            x = cx + math.cos(p_['a']) * p_['reach'] * out_k + p_['sway'] * R * 0.30 * uu
            y = cy + math.sin(p_['a']) * p_['reach'] * out_k - R * 1.55 * p_['lift'] * uu ** 1.5
            grow = 0.35 + 0.65 * ease(uu * 5.0)
            heat = max(0.0, p_['h0'] - uu * p_['rate'])
            rr = p_['r'] * grow
            if ground:
                y = min(y, cy - rr * 0.45)             # it sits on the ground until it lifts
            if heat > 0.02:
                fl.append((x, y, rr * (0.72 + 0.28 * min(1.0, heat)), heat))
            # smoke takes a lobe's place as its fire dies, swells a little as it climbs, and shrinks to nothing at the end
            born = min(1.0, max(0.0, (0.75 - heat) / 0.5)) * min(1.0, uu * 9)
            gone = min(1.0, max(0.0, (1.0 - u) / 0.45)) ** 0.85
            sr = p_['r'] * (0.74 + 0.42 * uu) * born * gone
            if sr > 0.8:
                spts.append((x + p_['spin'] * 1.5 * uu, y - 1 - R * 0.22 * uu, sr, 1.0))
        # ---- smoke first: lit from the upper left, dark in its folds
        if spts:
            Z = heap(yy, xx, spts)
            m = Z > 1.0
            if m.any():
                lit = light(ndi.gaussian_filter(Z, 0.6), -0.62, -0.78, 0.5)
                rim = np.clip(Z / 2.6, 0, 1)
                t = 0.40 + 0.40 * np.clip(lit, -1, 1) - 0.26 * (1 - rim) + 0.14 * u + 0.10 * (nz2 - 0.5)
                rgb[m] = banded(np.clip(t, 0, 1), SMOKE, 0.30)[m]
                al |= m
        # ---- fire over it: every lobe is banded from its rim to its heart, so the ball reads as a heap of them
        if fl:
            Tm = np.zeros((H, W))
            Ts = np.zeros((H, W))
            for x, y, r, heat in fl:
                d2 = ((xx - x) ** 2 + (yy - y) ** 2) / (r * r)
                bmp = np.clip(1 - d2, 0, None) ** 0.75 * heat
                Tm = np.maximum(Tm, bmp)
                Ts += bmp
            T_ = Tm + 0.16 * (Ts - Tm)
            lick = nz[(np.arange(H)[:, None] + int(u * R * 2.2)) % (H * 2), np.arange(W)[None, :]]
            T_ = T_ * (0.80 + 0.40 * lick)
            cut = 0.13
            m = T_ > cut
            if ground:
                m &= yy <= cy + 1
            if m.any():
                t = np.clip((T_ - cut) / (1.22 - cut), 0, 1) ** 0.85
                rgb[m] = banded(t, FIRE, 0.18)[m]
                al |= m
        # ---- the flash that starts it
        if f <= 1:
            fy0 = cy - R * (0.25 if ground else 0.0)
            ang = np.arctan2(yy - fy0, xx - cx)
            dist = np.hypot(xx - cx, yy - fy0)
            rad = R * (0.66 if f == 0 else 1.02) * (1 + 0.24 * np.sin(ang * 8 + seed) * np.sin(ang * 3 + 1.0))
            m = dist < rad
            if ground:
                m &= yy <= cy + 1
            t = np.clip(1.10 - 0.42 * dist / np.maximum(rad, 1), 0, 1) if f == 0 else np.clip(1.04 - 0.62 * dist / np.maximum(rad, 1), 0, 1)
            rgb[m] = banded(t, FIRE, 0.18)[m]
            al |= m
        # ---- sand and grit
        for j in jets:
            if u > 0.6:
                break
            d0 = j['v'] * ease(u * 2.0) * 0.55
            d1 = j['v'] * ease(u * 2.0)
            for k in range(int(d0), int(d1) + 1, 1):
                kk = (k - d0) / max(1.0, d1 - d0)
                x = cx + math.cos(j['a']) * k
                y = cy + math.sin(j['a']) * k * 0.9 + 0.9 * R * (u * 1.5) ** 2 * (k / max(1.0, d1))
                wdt = j['w'] * (1 - kk) * (1 - u * 1.4)
                if wdt <= 0.25:
                    continue
                m = ((xx - x) ** 2 + (yy - y) ** 2) < max(0.6, wdt) ** 2
                if ground:
                    m &= yy <= cy
                m &= ~al
                tone = 0.35 + 0.5 * kk
                rgb[m] = DUST[int(np.clip(tone * (len(DUST) - 1), 0, len(DUST) - 1))]
                al |= m
        if ground and dust and u < 0.8:
            # a low skirt of dust running out along the ground
            reach = R * (0.5 + 1.35 * ease(u * 1.7))
            hgt = R * 0.30 * math.sin(min(1.0, u * 1.5) * math.pi) + 0.5
            prof = hgt * np.clip(1 - (np.abs(xx - cx) / reach) ** 2.2, 0, None) * (0.66 + 0.7 * nz[H // 2 + (yy * 0).astype(int), xx.astype(int)])
            m = (cy - yy < prof) & (yy <= cy) & ~al
            t = 0.30 + 0.5 * (cy - yy) / max(1.0, hgt)
            rgb[m] = banded(np.clip(t, 0, 1), DUST, 0.4)[m]
            al |= m
        for s_ in sparks:
            if u > 0.5:
                break
            for back in range(3):
                uu = max(0.0, u - back * 0.02)
                d = s_['v'] * (1 - (1 - min(1.0, uu * 2.0)) ** 2)
                x = int(round(cx + math.cos(s_['a']) * d))
                y = int(round(cy + math.sin(s_['a']) * d + s_['g'] * uu * uu * 2.2))
                if 0 <= x < W and 0 <= y < H and (not ground or y <= cy):
                    rgb[y, x] = FIRE[[17, 13, 9][back] if u < 0.3 else [13, 9, 5][back]]
                    al[y, x] = True
        im = np.zeros((H, W, 4), np.uint8)
        im[..., :3] = rgb
        im[..., 3] = np.where(al, 255, 0)
        out.append((Image.fromarray(im, 'RGBA'), cx, cy))
    return out


def trimmed(fr):
    """Crop each frame to what is drawn in it, carrying the anchor."""
    res = []
    for im, ax, ay in fr:
        bb = im.getbbox()
        if not bb:
            res.append((Image.new('RGBA', (1, 1), (0, 0, 0, 0)), 0, 0))
            continue
        res.append((im.crop(bb), ax - bb[0], ay - bb[1]))
    return res


SETS = {
    # name: (radius, frames, seed, on the ground, with dust)
    'ex_s': (24, 18, 5, True, True),        # a grenade, a stick of dynamite
    'ex_m': (36, 22, 9, True, True),        # a drum, a mine
    'ex_a': (22, 16, 3, False, False),      # something hit in the air
}


def sheet(path, zoom=3, bg=(86, 150, 170)):
    rows = []
    for name, (R, n, seed, ground, dust) in SETS.items():
        rows.append((name, frames(R, n, seed, ground, dust)))
    cw = max(fr[0][0].width for _, fr in rows) + 4
    chs = [fr[0][0].height + 4 for _, fr in rows]
    cols = max(len(fr) for _, fr in rows)
    half = (cols + 1) // 2
    Wd = cw * half
    Ht = sum(c * 2 for c in chs)
    im = Image.new('RGBA', (Wd, Ht), bg + (255,))
    y = 0
    for (name, fr), ch in zip(rows, chs):
        for i, (f, ax, ay) in enumerate(fr):
            px = (i % half) * cw + cw // 2 - ax
            py = y + (i // half) * ch + 2
            # the ground
            if SETS[name][3]:
                for xg in range((i % half) * cw, (i % half + 1) * cw):
                    im.putpixel((xg, min(Ht - 1, py + ay + 1)), (222, 184, 112, 255))
            im.alpha_composite(f, (px, py))
        y += ch * 2
    im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
    im.save(path)
    return im.size


if __name__ == '__main__':
    print(sheet(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work', 'boom.png'), zoom=2))
