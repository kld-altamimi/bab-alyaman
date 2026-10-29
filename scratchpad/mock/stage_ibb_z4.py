# stage_ibb_z4.py - Ibb's zone 4, Sumara pass / نقيل سمارة (Khaled, 29 Oct 23:11: "Great, continue to next"): the highest
# point of the road north, in cloud (the brief). Past the Spokesman's stage the terraces' path meets the highway climbing
# to the pass: the road cut into the mountainside, a retaining wall of dressed stone under the cut, kerbstones painted
# black and white, a crash barrier on the drop's side, the road's next hairpin below seen through the cloud, the terraces
# falling away under it. Along it: the Zanabeel's post in a shipping container (sandbags across the road), a tea shack of
# stone with a tin awning and plastic chairs, the summit's marker and their flag; then the lookout at the top, a gravel
# shelf behind a low wall, where they have set out five podiums with a screen each (sprites: render_ibb.js), and the
# cloud. Everything is painted into the one picture (stage_ibb_world.py): the terraces' fields, path and drop come from
# zone 3's painter, carried on across the join, and this paints the pass over them. Local x (world = local + X0).
import numpy as np
from paint import *
import stage_mocha as SM
import stage_taiz as STZ
import stage_ibb as I
import stage_ibb_z1 as Z1
import stage_ibb_z3 as Z3

SH = I.SH
X0 = Z3.END3                    # zone 4 starts where the terraces end (6200)
W4 = 2000
END4 = X0 + W4                  # 8200
WALKY = 120                     # the road's walk line (the terraces' top level, carried on)
BACK = WALKY - 8                # the road's back edge
FRONT = WALKY + 6               # its front edge, where the barrier stands
ARENA = (1350, 1960)            # the lookout at the top, where the podiums stand
HAIR0 = 150                     # the hairpin below comes out of the cloud here
PODIUMS = [1480, 1560, 1640, 1720, 1800]   # where the five podiums stand on the lookout (sprites: render_ibb.js)
VAN = 1872                      # their broadcast van, at the lookout's far end
put_tone, plat = SM.put_tone, I.plat
IBBSTONE, CONCRETE, REDP, BLUEP, GOLD, SIGNY, GRASS, PLASTIC = (Z1.IBBSTONE, Z1.CONCRETE, Z1.REDP, Z1.BLUEP, Z1.GOLD, Z1.SIGNY,
                                                                Z1.GRASS, Z1.PLASTIC)
DRYST, LEAF, TERR, TIN, RUSTI, SOOT, TEAK, LIME = I.DRYST, I.LEAF, I.TERR, I.TIN, I.RUSTI, SM.SOOT, SM.TEAK, SM.LIME
STEEL, EARTH = Z3.STEEL, Z3.EARTH
BUSW, WATER = I.BUSW, I.WATER
ROADW = Z1.ROADW
ROCKP = ramp(['#141210', '#24211d', '#36322c', '#4a443c', '#5e574d', '#746b60', '#8b8174', '#a29788', '#b8ae9e'], 18)   # the pass's rock
FOG = ramp(['#a8b2b2', '#b8c0c0', '#c6cdcc', '#d2d8d6', '#dde2e0', '#e8ecea'], 10)                                    # cloud
CONTR = ramp(['#1c0806', '#3a120c', '#5a1e14', '#7a2c1c', '#984028', '#b25a3a', '#c87a56'], 12)                       # a container's red paint
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 + 1 / 32.0


def wx(lx):
    return int(lx + X0)


def hash_(a, b):
    return float(I.hash01(int(a), int(b)))


# ------------------------------------------------------------------ cloud
FOGC = np.array([214, 220, 218], dtype=float)


def fog(L, dens, x0=0, seed=1):
    """(kept for the back layer's joins) A haze: what is painted is drawn toward the cloud's colour by `dens` (0..1, an
    array the picture's height by its width from x0); nothing is added where nothing is painted."""
    h, w = dens.shape
    sub = L.rgb[:, x0:x0 + w].astype(float)
    a = L.a[:, x0:x0 + w]
    d = np.clip(dens, 0, 1)[..., None]
    out = np.round((sub * (1 - d) + FOGC * d) / 8) * 8         # (kept on the ramps' 5-bit steps)
    L.rgb[:, x0:x0 + w] = np.where(a[..., None], out, sub).astype(np.uint8)


def bank(L, x0, x1, yc, thick, seed=1, n=None, rmin=7, rmax=20, behind=True, lit=0.0):
    """A bank of cloud: puffs heaped along a line, each rounded on top, lit from above, grey-blue underneath, as the
    sky's clouds are drawn. behind: only where nothing is painted yet (the cloud is beyond what stands there)."""
    r = rng(seed)
    T = Tone(L.w, L.h)
    n = n or max(3, int((x1 - x0) / 9))
    best = np.full((L.h, L.w), -1.0)
    for k in range(n):
        cx = r.uniform(x0, x1)
        cy = yc + r.uniform(-0.5, 0.5) * thick
        rad = r.uniform(rmin, rmax)
        ys = range(max(0, int(cy - rad)), min(L.h, int(cy + rad) + 1))
        for y in ys:
            dy = (y - cy) / rad
            half = rad * np.sqrt(max(0.0, 1 - dy * dy))
            for x in range(max(0, int(cx - half)), min(L.w, int(cx + half) + 1)):
                if behind and L.a[y, x]:
                    continue
                v = (y - (cy - rad)) / (2 * rad)
                t = 0.92 - 0.42 * v + lit - 0.10 * (((x + y) % 7) == 0) * (v > 0.6)
                if t > best[y, x]:
                    best[y, x] = t
                    T.px(x, y, t)
    put_tone(L, T, FOG, dither=0.35)


def puffs(L, rows, seed=1, behind=False, x0=0, x1=None, ybot=SH, body=0.70, lit=0.0, flat=0.35, keep=None):
    """Cloud lying in rows, the back row first: each row a line of puffs heaped along it, rounded on top and lit from
    the upper left, solid below down to ybot; a nearer row drawn over the ones behind shows only its tops, the creases
    between them in shadow. rows: [(line, rmin, rmax)], line an array (the row's top line, column by column; nan where the
    row doesn't run). behind: only where nothing is painted yet. keep: a mask of where cloud may go."""
    w = L.w
    x1 = w if x1 is None else x1
    r = rng(seed)
    T = Tone(w, SH)
    for k, (line, rmin, rmax) in enumerate(rows):
        R = np.full((SH, w), -1.0)
        x = float(x0) - rmax
        while x < x1 + rmax:
            rad = r.uniform(rmin, rmax)
            cx = x + rad * 0.8
            ly = line[int(np.clip(cx, 0, w - 1))]
            x += rad * r.uniform(0.9, 1.5)
            if not np.isfinite(ly):
                continue
            cy = ly + rad * flat + r.uniform(-0.25, 0.25) * rad
            xa, xb = max(0, int(np.floor(cx - rad))), min(w, int(np.ceil(cx + rad)) + 1)
            if xb <= xa:
                continue
            xs = np.arange(xa, xb)
            dx = (xs - cx) / rad
            half = np.sqrt(np.clip(1 - dx * dx, 0, 1)) * rad
            ok = half > 0.4
            ytop = cy - half
            ya = max(0, int(np.floor(ytop[ok].min()))) if ok.any() else ybot
            if ya >= ybot:
                continue
            ys = np.arange(ya, ybot)[:, None]
            inside = (ys >= ytop[None, :]) & ok[None, :]
            u = np.clip((ys - ytop[None, :]) / np.maximum(1.0, cy - ytop[None, :]), 0, 1)
            t = np.where(ys < cy, 0.98 - 0.26 * u - 0.07 * dx[None, :], body - 0.10 * np.clip((ys - cy) / 40.0, 0, 1)) + lit
            t = t - 0.08 * (inside & (ys < ytop[None, :] + 1) & (dx[None, :] > 0.55))      # (the rim going round, its right end)
            sub = R[ya:ybot, xa:xb]
            sub[inside] = np.maximum(sub[inside], t[inside])
        m = R >= 0
        if behind:
            m &= ~L.a
        if keep is not None:
            m &= keep
        T.t[m] = R[m]
        T.m |= m
    put_tone(L, T, FOG, dither=0.35)
    return T.m


# ------------------------------------------------------------------ the mountain above the road
def mountain(L, seed=701):
    """Above the road the mountainside, cut back where the road was blasted into it: the terraces' fields carried on
    from zone 3 at first, then the cut rising in front of them: dark rock as the falls' buttress is drawn (faceted, lit
    from the upper left, ledges running across it a little tilted, cracks down it, green on its ledges), its top broken
    into blocks against the cloud; under it, along the road's back, a retaining wall of dressed stone with weep holes,
    kerbstones painted black and white along its foot. At the top of the pass the cut comes down to the lookout's low
    wall. -> the cut's top, column by column."""
    w = L.w
    r = rng(seed)
    xs = np.arange(w)
    k = np.clip((xs - 90) / 220.0, 0, 1) ** 1.3
    ar = np.clip((xs - (ARENA[0] - 90)) / 90.0, 0, 1) ** 0.8
    sky = 52 + 14 * (noise((1, w), seed, 36, 0.5)[0] - 0.5) * 2 + 6 * np.sin(xs / 47.0)
    low = np.where(xs < 600, BACK - 1, BACK - 13)          # (from nothing at its start; down to the lookout's wall)
    top = low - (low - sky) * k * (1 - ar)
    # the top broken into blocks: steps of a few pixels, a run of 3 to 12 columns each
    jag = np.zeros(w)
    x = 0
    while x < w:
        ln = int(r.integers(3, 13))
        jag[x:x + ln] = r.integers(-5, 4)
        x += ln
    top = np.round(top + jag * np.clip(k * (1 - ar) * 3, 0, 1)).astype(int)
    top = np.minimum(top, BACK - 13)
    y1 = BACK - 1
    yy, xx = np.mgrid[0:SH, 0:w]
    rock = (yy >= top[None, :]) & (yy < y1) & (xx >= 88)
    Hh = fbm((SH, w), seed + 1, 6, 7, octaves=4) * 30 + 0.22 * yy
    lit = light(ndi.gaussian_filter(Hh, 0.8), -0.7, -0.5, 0.42)
    strata = (yy + 0.10 * xx + 6 * (noise((SH, w), seed + 8, 24, 4) - 0.5)) % 19.0
    crack = np.abs(noise((SH, w), seed + 9, 1.4, 14) - 0.5) < 0.022
    t = 0.46 + 0.20 * np.clip(lit, -1, 1) + 0.06 * (noise((SH, w), seed + 2, 1.2, 1.2) - 0.5) \
        + 0.14 * (yy < top[None, :] + 2) + 0.12 * (strata < 1.5) - 0.09 * ((strata > 1.5) & (strata < 4)) - 0.16 * crack \
        - 0.10 * (yy > y1 - 4)
    Z1.piece_put(L, t[:y1], rock[:y1], ROCKP, 0, 0, dither=0.4)
    # green on its ledges, scrub along its top
    Tt = Tone(w, SH)
    for i in range(int(w / 9)):
        gx = int(r.uniform(4, w - 4))
        if k[gx] * (1 - ar[gx]) < 0.3:
            continue
        col = np.where(rock[:, gx] & (strata[:, gx] < 2.5))[0]
        if not len(col):
            continue
        gy_ = int(col[int(r.integers(0, len(col)))])
        if gy_ > y1 - 5:
            continue
        I.tree_tone(Tt, gx, gy_ - 1, r.uniform(1.4, 3.2), int(r.integers(0, 1000)), dark=0.10)
    put_tone(L, Tt, LEAF, dither=0.5)
    G = Tone(w, SH)
    for x in range(w):
        if k[x] * (1 - ar[x]) < 0.2:
            continue
        if hash_(x, seed + 7) < 0.50:
            for j in range(int(1 + 4 * hash_(x, seed + 8))):
                G.px(x, int(top[x]) - 1 - j, 0.40 + 0.10 * j)
    put_tone(L, G, GRASS, dither=0.3)
    # the retaining wall under the cut (not at the join, nor at the lookout)
    rw0, rw1 = 220, ARENA[0] - 40
    Wl = Layer(w, SH)
    STZ.ashlar(Wl, rw0, BACK - 13, rw1, BACK - 1, IBBSTONE, seed=seed + 3, course=4, block=(8, 16), base=0.50, rough=0.12)
    for x in range(rw0, rw0 + 30):                             # (its end built up against the rock, course by course)
        Wl.a[:int(BACK - 1 - (x - rw0) * 12 / 30.0) // 4 * 4 + 3, x] = False
    L.paste(Wl)
    Wh = Tone(w, SH)
    for x in range(rw0 + 10, rw1 - 6, 34):
        for j in range(3):
            Wh.px(x, BACK - 6 + j, 0.10); Wh.px(x + 1, BACK - 6 + j, 0.10)
        for j in range(4):
            Wh.px(x, BACK - 3 + j, 0.30)                        # (the stain below each)
    put_tone(L, Wh, SOOT, dither=0)
    # kerbstones along the road's back, painted black and white
    K = np.zeros((SH, w), np.uint8)
    for x in range(100, ARENA[0] - 30):
        c = 1 if ((x - 100) // 8) % 2 == 0 else 2
        for yk in (BACK - 1, BACK):
            K[yk, x] = c
    L.rgb[K == 1] = (226, 222, 210)
    L.rgb[K == 2] = (34, 32, 30)
    L.a |= K > 0
    return top


# ------------------------------------------------------------------ the road and its barrier
def road4(L, x0, x1, seed=711):
    """The highway's surface from the path's end on: wet asphalt, its back edge's white line worn, patches, a crack or
    two; at its start the terraces' path running into it."""
    w = x1 - x0
    h = FRONT - BACK + 2
    sheen = noise((h, w), seed, 40, 0.8)
    grain = noise((h, w), seed + 1, 0.6, 0.6)
    yy, xx = np.mgrid[0:h, 0:w]
    t = 0.50 + 0.20 * np.clip(sheen - 0.45, 0, 1) + 0.07 * (grain - 0.5) - 0.06 * (yy / float(h))
    line = (yy == 2) & (noise((h, w), seed + 2, 4, 0.5) > 0.30)
    t = np.where(line, 0.86, t)
    # the start: the asphalt breaking up over the path, holes in it, fewer further on
    n = noise((h, w), seed + 3, 3.5, 1.8)
    u = np.clip(xx / 90.0, 0, 1)
    m = n > 0.92 - 0.95 * u ** 0.7
    m[:, 90:] = True
    P = Layer(w, h)
    P.put(toned(np.clip(t, 0, 1), ROADW, dither=0.45, x0=x0, y0=BACK), m)
    L.paste(P, x0, BACK)


def barrier(L, x0, x1, seed=721, gaps=()):
    """The crash barrier along the drop's side: galvanised posts every 22 px, the corrugated rail on them, a red
    reflector on every other post; dented here and there."""
    T = Tone(L.w, SH)
    Rf = Tone(L.w, SH)
    for x in range(x0, x1):
        if any(a <= x < b for a, b in gaps):
            continue
        dent = 1 if hash_(x // 9, seed) < 0.08 else 0
        y0 = FRONT - 5 + dent
        T.px(x, y0, 0.90); T.px(x, y0 + 1, 0.62); T.px(x, y0 + 2, 0.82); T.px(x, y0 + 3, 0.48); T.px(x, y0 + 4, 0.30)
    for px_ in range(x0 + 4, x1, 22):
        if any(a <= px_ < b for a, b in gaps):
            continue
        for y in range(FRONT - 7, FRONT + 6):
            T.px(px_, y, 0.70); T.px(px_ + 1, y, 0.42)
        if (px_ // 22) % 2 == 0:
            Rf.px(px_, FRONT - 7, 0.70); Rf.px(px_ + 1, FRONT - 7, 0.55)
    put_tone(L, T, STEEL, dither=0.2)
    put_tone(L, Rf, REDP, dither=0)


def hairpin(L, y=180, seed=731):
    """The road's last hairpin, below this stretch, seen across the terraces through the cloud: a band of asphalt with
    its own barrier, a lorry labouring up it."""
    w = L.w
    T = Tone(w, SH)
    for x in range(HAIR0, w):
        for yy in range(y, y + 9):
            T.px(x, yy, 0.42 + 0.10 * (yy == y) - 0.08 * (yy > y + 6) + 0.05 * (hash_(x // 5, yy) < 0.2))
    put_tone(L, T, ROADW, dither=0.4)
    B = Tone(w, SH)
    for x in range(HAIR0, w):
        B.px(x, y + 9, 0.80); B.px(x, y + 10, 0.50)
        if x % 16 == 0:
            for j in range(4):
                B.px(x, y + 9 + j, 0.62)
    put_tone(L, B, STEEL, dither=0)
    # the lorry: a cab and a high load under a tarpaulin, small with distance
    lx = 860
    Lc = Tone(w, SH)
    for yy in range(y - 12, y + 2):
        for xx in range(lx, lx + 30):
            Lc.px(xx, yy, 0.62 - 0.10 * (yy > y - 2) - 0.08 * (xx > lx + 26) + 0.10 * (yy == y - 12))
    put_tone(L, Lc, I.BUSB, dither=0.3)
    Cb = Tone(w, SH)
    for yy in range(y - 8, y + 2):
        for xx in range(lx + 30, lx + 40):
            Cb.px(xx, yy, 0.70 - 0.10 * (xx > lx + 37) + (0.14 if (yy < y - 4 and xx > lx + 33) else 0))
    put_tone(L, Cb, I.BUSW, dither=0.3)
    Wl = Tone(w, SH)
    for cx in (lx + 6, lx + 22, lx + 34):
        for i in range(-2, 3):
            for j in range(-2, 2):
                if i * i + j * j <= 4:
                    Wl.px(cx + i, y + 2 + j, 0.20)
    put_tone(L, Wl, Z1.TYRE, dither=0)


# ------------------------------------------------------------------ along the road
def container_post(L, x, seed=741):
    """Their post: a shipping container set on the road's back edge, red, ribbed, rusting, a door cut in its side and
    left open on the dark, their emblem painted on it, their flag on a pole lashed to its corner; a nest of sandbags
    across the road in front of it, two drums. -> what the level needs."""
    cx0, cx1 = x, x + 92
    base = BACK + 2
    top = base - 42
    T = Tone(L.w, SH)
    for yy in range(top, base):
        for xx in range(cx0, cx1):
            rib = (xx - cx0) % 5
            T.px(xx, yy, 0.56 + 0.12 * (rib == 0) - 0.10 * (rib == 3) - 0.10 * (xx > cx1 - 10) + 0.08 * (yy == top) - 0.06 * (yy > base - 4))
    put_tone(L, T, CONTR, dither=0.3, grain=0.05, seed=seed)
    Rr = Tone(L.w, SH)
    r = rng(seed)
    for k in range(60):
        rx, ry = int(r.integers(cx0, cx1)), int(r.integers(top + 2, base))
        for j in range(int(r.integers(2, 8))):
            Rr.px(rx, ry + j, 0.36 + 0.3 * r.random())
    put_tone(L, Rr, RUSTI, dither=0.2)
    D = Tone(L.w, SH)
    dx = cx0 + 12
    for yy in range(top + 8, base):
        for xx in range(dx, dx + 16):
            D.px(xx, yy, 0.08 + 0.04 * ((xx + yy) % 5 == 0))
    put_tone(L, D, SOOT, dither=0)
    Fr = Tone(L.w, SH)
    for yy in range(top + 8, base):
        Fr.px(dx - 1, yy, 0.30); Fr.px(dx + 16, yy, 0.30)
    for xx in range(dx - 1, dx + 17):
        Fr.px(xx, top + 7, 0.30)
    put_tone(L, Fr, CONTR, dither=0)
    # their emblem: the red disc, the gold wreath
    ex, ey = cx0 + 60, top + 20
    E = Tone(L.w, SH)
    Rd = Tone(L.w, SH)
    for j in range(-8, 9):
        for i in range(-8, 9):
            d = np.sqrt(i * i + j * j)
            if d <= 5.5:
                Rd.px(ex + i, ey + j, 0.56)
            elif d <= 8 and (i + j) % 2 == 0:
                E.px(ex + i, ey + j, 0.76)
    put_tone(L, Rd, REDP, dither=0)
    put_tone(L, E, GOLD, dither=0)
    # their flag
    P = Tone(L.w, SH)
    fx = cx1 - 3
    for j in range(36):
        P.px(fx, top - 1 - j, 0.30)
    put_tone(L, P, SOOT, dither=0)
    yy, xx = np.mgrid[0:11, 0:17]
    wave = np.round(np.sin(xx / 3.0) * 1.2).astype(int)
    band = ((yy - wave) >= 4) & ((yy - wave) < 7)
    Fl = np.where(band[..., None], np.array([232, 192, 56]), np.array([184, 34, 24])).astype(float)
    Q = Layer(17, 11)
    Q.put((np.round(Fl / 8) * 8).astype(np.uint8), (yy - wave >= 0) & (yy - wave < 10))
    L.paste(Q, fx + 1, top - 36)
    # the nest across the road, a drum
    nx = cx1 + 20
    SM.sack_pile(L, [(nx, nx + 40, WALKY - 16), (nx + 6, nx + 34, WALKY - 23)], WALKY + 2, seed=seed + 1, green=True, marks=False)
    plat('cpnest', [(wx(nx + 2), WALKY - 22), (wx(nx + 38), WALKY - 22)])
    Z1.drum(L, nx + 44, WALKY + 2, seed=seed + 2, rmp=REDP)
    SM.soft_shadow(L, nx - 2, nx + 58, WALKY + 3, h=3, amt=0.74)
    return dict(door=dict(x=wx(dx + 8), y=WALKY), nest=[wx(nx), wx(nx + 40)], x0=wx(cx0), x1=wx(cx1))


def tea_shack(L, x, seed=751):
    """A tea shack at a bend of the road: one room of rough stone with a flat roof, a tin awning on two poles over the
    road's back edge, plastic chairs and a table under it, a gas bottle, the kettle on its burner; its door open."""
    base = BACK + 1
    w, h = 64, 33
    top = base - h
    T = Tone(L.w, SH)
    st = noise((SH, L.w), seed, 1.1, 0.8)
    for y in range(top, base):
        for xx in range(x, x + w):
            d = y - top
            joint = (d % 5 == 4) or (((xx + 4 * (d // 5)) % 9) == 0)
            T.px(xx, y, 0.42 - 0.12 * joint + 0.10 * (st[y, xx] - 0.5) - 0.12 * (xx > x + w - 9))
    put_tone(L, T, IBBSTONE, dither=0.3)
    Wt = Tone(L.w, SH)
    for xx in range(x - 1, x + w + 1):
        Wt.px(xx, top - 1, 0.94); Wt.px(xx, top, 0.80); Wt.px(xx, top + 1, 0.60)
    put_tone(L, Wt, LIME, dither=0)
    plat('shackroof', [(wx(x), top - 1), (wx(x + w - 1), top - 1)])
    D = Tone(L.w, SH)
    dx = x + 8
    for y in range(base - 22, base):
        for xx in range(dx, dx + 12):
            D.px(xx, y, 0.06 + 0.04 * (xx == dx))
    put_tone(L, D, SOOT, dither=0)
    # the awning: tin, out over the road's edge from the wall, on two poles
    ab, af = top + 6, top + 12
    Aw = Tone(L.w, SH)
    for xx in range(x + 22, x + w + 30):
        rib = (xx - x) % 4
        for yy in range(ab, af):
            Aw.px(xx, yy, 0.70 - 0.14 * (yy - ab) / 6.0 + 0.12 * (rib == 0) - 0.10 * (rib == 2))
        Aw.px(xx, af, 0.30)
    put_tone(L, Aw, TIN, dither=0.3, grain=0.05, seed=seed)
    SM.shade_box(L, x + 24, af + 1, x + w + 28, af + 8, 0.82)
    Po = Tone(L.w, SH)
    for px_ in (x + w + 4, x + w + 27):
        for yy in range(af + 1, BACK + 2):
            Po.px(px_, yy, 0.56); Po.px(px_ + 1, yy, 0.30)
    put_tone(L, Po, CONCRETE, dither=0)
    plat('shackawn', [(wx(x + 23), ab + 1), (wx(x + w + 29), ab + 1)])
    # under it: plastic chairs, a table, a gas bottle and the burner with the kettle
    C = Tone(L.w, SH)
    for cx in (x + 30, x + 52, x + 74):
        for j in range(9):
            C.px(cx, base - 1 - j, 0.84)
        for i in range(7):
            C.px(cx + i, base - 6, 0.94); C.px(cx + i, base - 5, 0.62)
        for j in range(5):
            C.px(cx + 1, base - 4 + j, 0.62); C.px(cx + 6, base - 4 + j, 0.50)
    put_tone(L, C, PLASTIC, dither=0)
    Tb = Tone(L.w, SH)
    for xx in range(x + 40, x + 52):
        Tb.px(xx, base - 9, 0.90); Tb.px(xx, base - 8, 0.60)
    for j in range(7):
        Tb.px(x + 42, base - 7 + j, 0.50); Tb.px(x + 49, base - 7 + j, 0.42)
    put_tone(L, Tb, PLASTIC, dither=0)
    Gb = Tone(L.w, SH)
    for j in range(12):
        for i in range(5):
            Gb.px(x + 24 + i, base - j, 0.62 - 0.30 * abs(i - 1.5) / 2.5)
    put_tone(L, Gb, BLUEP, dither=0.3)
    K = Tone(L.w, SH)
    for i in range(6):
        K.px(x + 31 + i, base - 13, 0.70); K.px(x + 31 + i, base - 14, 0.84)
    put_tone(L, K, STEEL, dither=0)
    return dict(door=dict(x=wx(dx + 6), y=WALKY), x0=wx(x), x1=wx(x + w + 30), roof=top - 1)


def summit(L, x, seed=761):
    """The top of the pass: a concrete marker painted in bands, a rock shouldering out of the cut beside the road (flat
    enough on top to stand on), their flag on a tall pole, a road sign on its post, blank (no words anywhere)."""
    # the rock: a block of the pass's rock left standing by the road, flat on top, faceted as the cut is
    rx0, rx1 = x + 30, x + 96
    topy = WALKY - 30
    pts = [(rx0 - 2, BACK + 2), (rx0 + 2, topy + 13), (rx0 + 9, topy + 5), (rx0 + 16, topy), (rx0 + 44, topy), (rx0 + 50, topy + 3),
           (rx0 + 57, topy + 10), (rx1 - 2, topy + 15), (rx1 + 2, topy + 22), (rx1 + 3, BACK + 2)]
    m = poly_mask(L.w, SH, pts)
    ys, xs_ = np.nonzero(m)
    bx0, bx1, by0, by1 = xs_.min(), xs_.max() + 1, ys.min(), ys.max() + 1
    mm = m[by0:by1, bx0:bx1]
    hh, ww = mm.shape
    Hh = fbm((hh, ww), seed + 1, 5, 5, octaves=3) * 18 + ndi.distance_transform_edt(mm) * 1.6
    lit = light(ndi.gaussian_filter(Hh, 0.8), -0.7, -0.6, 0.40)
    yy_, xx_ = np.mgrid[0:hh, 0:ww]
    strata = (yy_ + 0.12 * xx_) % 11.0
    edge = mm & ~ndi.binary_erosion(mm)
    tt = 0.46 + 0.22 * np.clip(lit, -1, 1) + 0.10 * (strata < 1.2) - 0.07 * ((strata > 1.2) & (strata < 3)) \
        + 0.16 * (edge & (yy_ < (topy + 3 - by0))) - 0.10 * (xx_ > ww - 6) - 0.10 * (yy_ > hh - 4)
    Z1.piece_put(L, tt, mm, ROCKP, bx0, by0, dither=0.4)
    plat('summitrock', [(wx(rx0 + 17), topy - 1), (wx(rx0 + 43), topy - 1)])
    # the marker: a squat concrete post, banded
    M = Tone(L.w, SH)
    for y in range(BACK - 20, BACK + 1):
        for xx in range(x, x + 10):
            band = ((y - (BACK - 20)) // 5) % 2
            M.px(xx, y, (0.86 if band == 0 else 0.16) - 0.14 * (xx > x + 7))
    put_tone(L, M, CONCRETE, dither=0)
    # the sign: a post, a blank panel
    S = Tone(L.w, SH)
    sx = x + 112
    for y in range(58, BACK + 1):
        S.px(sx, y, 0.66); S.px(sx + 1, y, 0.40)
    put_tone(L, S, STEEL, dither=0)
    Pn = Tone(L.w, SH)
    for y in range(48, 64):
        for xx in range(sx - 14, sx + 16):
            Pn.px(xx, y, 0.56 + 0.10 * (y == 48) - 0.12 * (y == 63) + 0.04 * ((xx + y) % 9 == 0))
    put_tone(L, Pn, BLUEP, dither=0.2)
    Pb = Tone(L.w, SH)
    for xx in range(sx - 13, sx + 15):
        Pb.px(xx, 49, 0.92); Pb.px(xx, 62, 0.92)
    for y in range(49, 63):
        Pb.px(sx - 13, y, 0.92); Pb.px(sx + 14, y, 0.92)
    put_tone(L, Pb, Z1.BUSW if hasattr(Z1, 'BUSW') else I.BUSW, dither=0)
    # their flag on a tall pole
    P = Tone(L.w, SH)
    fx = x + 140
    for j in range(BACK - 40):
        P.px(fx, BACK - j, 0.30)
    put_tone(L, P, SOOT, dither=0)
    yy, xx = np.mgrid[0:13, 0:22]
    wave = np.round(np.sin(xx / 3.4) * 1.4).astype(int)
    band = ((yy - wave) >= 5) & ((yy - wave) < 8)
    Fl = np.where(band[..., None], np.array([232, 192, 56]), np.array([184, 34, 24])).astype(float)
    Q = Layer(22, 13)
    Q.put((np.round(Fl / 8) * 8).astype(np.uint8), (yy - wave >= 0) & (yy - wave < 12))
    L.paste(Q, fx + 1, 40)
    return dict(rock=[wx(rx0), wx(rx1)], marker=wx(x), sign=wx(sx), flag=wx(fx))


def lookout(L, x0, x1, seed=771):
    """The lookout at the top: a shelf of gravel off the road behind a low wall of the pass's stone, nothing behind the
    wall but cloud; cables run along the ground from their van to where the podiums stand; a light on a stand at either
    end. (Over the lookout the terraces' fields carried on from zone 3 are cleared: the cloud stands behind the wall.)"""
    T = Tone(L.w, SH)
    g = noise((SH, L.w), seed, 0.8, 0.8)
    for xx in range(x0, L.w):
        for y in range(BACK - 2, FRONT + 1):
            T.px(xx, y, 0.56 + 0.12 * (g[y, xx] - 0.5) + 0.10 * (g[y, xx] > 0.82) - 0.06 * (y > FRONT - 3))
    put_tone(L, T, I.GRAVEL, dither=0.4)
    Z1.drystone(L, x0 - 44, L.w, BACK - 12, BACK - 1, seed=seed + 1)
    C = Tone(L.w, SH)
    for xx in range(PODIUMS[0] - 4, VAN + 2):
        C.px(xx, WALKY + 2 + int(round(1.2 * np.sin(xx / 13.0))), 0.18)
        if (xx * 7) % 11 < 3:
            C.px(xx, WALKY + 3 + int(round(1.2 * np.sin(xx / 13.0))), 0.10)
    for px_ in PODIUMS:                                          # (a loop of it at each podium's foot)
        for i in range(-5, 6):
            C.px(px_ + i, WALKY + 1 - int(abs(i) < 3), 0.22)
    put_tone(L, C, SOOT, dither=0)
    Z3.light_stand(L, x0 + 16, WALKY - 2, hgt=56, face=1, seed=seed + 2)
    Z3.light_stand(L, VAN - 18, WALKY - 2, hgt=56, face=-1, seed=seed + 3)


def ob_van(L, x, seed=781):
    """Their broadcast van, parked at the lookout's far end with its back to the podiums: a white box van, nose to the
    right, the Zanabeel's red band with its yellow stripe along it, their emblem on the side, a sliding door shut, a dish
    on the roof turned up at the sky, an aerial folded along it; cables out of its back to the podiums. (The back room:
    what is behind the door is the reveal's, render_ibb.js.) -> its parts."""
    base = BACK + 3
    x0, x1 = x, x + 80
    roof = base - 40
    sill = base - 9
    cab = x0 + 58
    B = Tone(L.w, SH)
    for yy in range(roof, sill):
        for xx in range(x0, x1):
            if xx >= cab:
                dx = xx - cab                                      # the cab, lower, its windscreen raked
                if yy < roof + 10 + max(0, dx - 12):
                    continue
            v = (yy - roof) / float(sill - roof)
            t = 0.80 - 0.18 * v + 0.12 * (yy == roof) - 0.08 * (xx > x1 - 4) + 0.08 * (xx < x0 + 2)
            t -= 0.10 * (xx == cab) * (yy > roof + 10)
            B.px(xx, yy, t)
    put_tone(L, B, BUSW, dither=0.35)
    # the windscreen and the cab's side window, the sky in them
    Wn = Tone(L.w, SH)
    for yy in range(roof + 12, roof + 22):
        for xx in range(cab + 3, x1 - 1):
            dx = xx - cab
            if yy < roof + 11 + max(0, dx - 12) or (dx in (13, 14)):
                continue
            Wn.px(xx, yy, 0.34 + 0.30 * (((xx + (yy - roof) * 2) % 13) < 3) + 0.10 * (yy == roof + 12))
    put_tone(L, Wn, WATER, dither=0.3)
    # their band along it, the yellow stripe on it; the emblem
    Bd = Tone(L.w, SH)
    for yy in range(roof + 24, roof + 29):
        for xx in range(x0, x1):
            Bd.px(xx, yy, 0.58 - 0.06 * (yy - roof - 24))
    put_tone(L, Bd, REDP, dither=0)
    Ys = Tone(L.w, SH)
    for xx in range(x0, x1):
        Ys.px(xx, roof + 26, 0.70)
    put_tone(L, Ys, GOLD, dither=0)
    ex, ey = x0 + 11, roof + 12
    E = Tone(L.w, SH)
    Rd = Tone(L.w, SH)
    for j in range(-6, 7):
        for i in range(-6, 7):
            d = np.sqrt(i * i + j * j)
            if d <= 3.6:
                Rd.px(ex + i, ey + j, 0.56)
            elif d <= 6 and (i + j) % 2 == 0:
                E.px(ex + i, ey + j, 0.76)
    put_tone(L, Rd, REDP, dither=0)
    put_tone(L, E, GOLD, dither=0)
    # the sliding door, shut: its seams, its handle, the rail above it
    D = Tone(L.w, SH)
    dx0, dx1 = x0 + 24, x0 + 46
    for yy in range(roof + 3, sill):
        D.px(dx0, yy, 0.30); D.px(dx1, yy, 0.30)
    for xx in range(dx0, dx1 + 1):
        D.px(xx, roof + 3, 0.30)
    for xx in range(dx0 - 2, dx1 + 10):
        D.px(xx, roof + 2, 0.42)
    D.px(dx1 - 3, roof + 18, 0.16); D.px(dx1 - 2, roof + 18, 0.16); D.px(dx1 - 3, roof + 19, 0.26)
    # the back: a ladder up to the roof, the cable port low down
    for yy in range(roof, sill):
        if (yy - roof) % 4 == 0:
            D.px(x0 + 1, yy, 0.26); D.px(x0 + 2, yy, 0.26)
    for yy in range(roof - 1, sill):
        D.px(x0, yy, 0.40)
    put_tone(L, D, SOOT, dither=0)
    # the dish on the roof, turned up at the sky; its arm and the feed; the aerial folded along the roof
    Ds = Tone(L.w, SH)
    cxd, cyd = x0 + 30, roof - 10
    for j in range(-12, 13):
        for i in range(-12, 13):
            a, b = 11.0, 4.6
            ca, sa = np.cos(-0.55), np.sin(-0.55)
            u_ = (i * ca + j * sa) / a
            v_ = (-i * sa + j * ca) / b
            if u_ * u_ + v_ * v_ <= 1.0:
                Ds.px(cxd + i, cyd + j, 0.86 - 0.30 * max(0, v_) - 0.10 * max(0, u_) + 0.06 * (v_ < -0.6))
    for j in range(9):
        Ds.px(cxd + 1, roof - 1 - j // 2 - 1, 0.50)
    for k in range(7):
        Ds.px(cxd + 3 + k, cyd - 2 - k, 0.40)
    Ds.px(cxd + 10, cyd - 9, 0.70); Ds.px(cxd + 11, cyd - 9, 0.70); Ds.px(cxd + 10, cyd - 10, 0.70)
    for xx in range(x0 + 4, x0 + 52):
        Ds.px(xx, roof - 2, 0.62)
    for xx in (x0 + 6, x0 + 50):
        Ds.px(xx, roof - 1, 0.50)
    Ds.px(x0 + 4, roof - 3, 0.62)
    put_tone(L, Ds, PLASTIC, dither=0.25)
    # the wheels, the bumper, the lamps
    Wl = Tone(L.w, SH)
    for wc in (x0 + 14, x0 + 66):
        for j in range(-7, 8):
            for i in range(-7, 8):
                e = i * i + j * j
                if e <= 49:
                    hub = e < 9
                    Wl.px(wc + i, base - 7 + j, 0.60 if hub else 0.30 - 0.08 * (i > 0) + 0.08 * (j < -4))
    put_tone(L, Wl, Z1.TYRE, dither=0)
    K = Tone(L.w, SH)
    for xx in range(x1 - 6, x1 + 2):
        K.px(xx, sill, 0.40); K.px(xx, sill + 1, 0.26)
    for xx in range(x0 - 2, x0 + 6):
        K.px(xx, sill, 0.40); K.px(xx, sill + 1, 0.26)
    for xx in range(x0 + 4, x1 - 4):
        if not (x0 + 6 <= xx <= x0 + 22 or x0 + 58 <= xx <= x0 + 74):
            K.px(xx, sill, 0.22)
    put_tone(L, K, SOOT, dither=0)
    Lm = np.zeros((SH, L.w), np.uint8)
    for j in range(3):
        Lm[sill - 4 + j, x1 - 2] = 1; Lm[sill - 4 + j, x1 - 1] = 1
        Lm[sill - 6 + j, x0 + 1] = 2; Lm[sill - 6 + j, x0 + 2] = 2
    L.rgb[Lm == 1] = (240, 232, 196)
    L.rgb[Lm == 2] = (200, 40, 32)
    L.a |= Lm > 0
    # cables out of its back, down to the ground and away to the podiums
    C = Tone(L.w, SH)
    for j in range(sill - 4, WALKY + 3):
        C.px(x0 - 2 - (j > sill + 2), j, 0.18)
    put_tone(L, C, SOOT, dither=0)
    SM.soft_shadow(L, x0 + 2, x1 + 2, base + 1, h=3, amt=0.72)
    return dict(x0=wx(x0), x1=wx(x1), door=[wx(dx0), wx(dx1)], roof=roof, sill=sill, base=base)


# ------------------------------------------------------------------ zone 4, put together
def play_z4(L, seed=801):
    """Sumara pass, world 6200 to 8200, painted over the terraces' fields, path and drop that zone 3's painter carries
    on into it (stage_ibb_world.py). -> what the level needs (I.INFO['z4'])."""
    info = {}
    w = L.w
    top = mountain(L, seed=seed)
    for x in range(ARENA[0] - 200, w):
        L.a[:top[x], x] = False
    road4(L, 110, ARENA[0] + 10, seed=seed + 10)
    hairpin(L, y=182, seed=seed + 20)
    info['post'] = container_post(L, 470, seed=seed + 30)
    info['shack'] = tea_shack(L, 860, seed=seed + 40)
    info['summit'] = summit(L, 1150, seed=seed + 50)
    lookout(L, ARENA[0], ARENA[1], seed=seed + 60)
    info['van'] = ob_van(L, VAN, seed=seed + 65)
    barrier(L, 120, ARENA[0] - 10, seed=seed + 70)
    barrier(L, ARENA[0] + 10, w - 2, seed=seed + 71)
    info['posters'] = [Z1.poster(L, 300, BACK - 11, 'face', seed=seed + 80), Z1.poster(L, 1030, BACK - 11, 'badge', seed=seed + 81)]
    # the cloud: a haze over everything, coming on from the join, heavier high up and down in the drop and toward the
    # top of the pass, lighter along the road; cloud lying on the cut's top; a sea of it in the valley below, a billow
    # of it rising where the hairpin comes out, the sea rising round the lookout; cloud behind the lookout's wall
    xs = np.arange(w)
    yy = np.arange(SH)[:, None]
    come = np.clip(xs / 320.0, 0, 1)[None, :] ** 1.2
    up = np.clip((xs - 150) / 1100.0, 0, 1)[None, :]
    at = np.clip((xs - (ARENA[0] - 250)) / 300.0, 0, 1)[None, :]
    dens = 0.08 + 0.18 * up + 0.30 * np.clip((80 - yy) / 50.0, 0, 1) * (0.5 + 0.5 * up) + 0.42 * np.clip((yy - 150) / 60.0, 0, 1) * (0.4 + 0.6 * up)
    dens = dens + 0.12 * at * np.clip((yy - FRONT) / 30.0, 0, 1)
    road = ((yy >= BACK - 34) & (yy <= FRONT + 6)).astype(float)
    dens = dens * (1 - 0.45 * road) * come
    fog(L, np.clip(dens, 0, 0.80), 0, seed=seed + 91)
    # the sea below: three rows, the line rising toward the top of the pass; the billow at the hairpin's end
    base = np.interp(xs, [0, 120, 320, 900, 1200, ARENA[0], ARENA[0] + 200, w], [232, 214, 198, 194, 188, 176, 166, 164])
    bill = 170 + 0.0045 * (xs - (HAIR0 + 12)) ** 2
    base = np.minimum(base, bill)
    puffs(L, [(base, 7, 13), (base + 8, 8, 15), (base + 17, 9, 17), (np.maximum(base + 30, 200.0), 10, 18)], seed=seed + 200, behind=False, body=0.66)
    # lying on the cut's top (and only where nothing stands)
    k = np.clip((xs - 200) / 200.0, 0, 1)
    ln = np.where(k > 0, top - 4.0, np.nan)
    puffs(L, [(ln - 10, 6, 12), (ln, 5, 11)], seed=seed + 300, behind=True, body=0.74, lit=0.0)
    # behind the lookout's wall
    lw = np.where(xs >= ARENA[0] - 110, BACK - 26.0, np.nan)
    puffs(L, [(lw - 26, 9, 18), (lw - 12, 8, 15), (lw, 7, 13)], seed=seed + 400, behind=True, body=0.76)
    info['arena'] = dict(x0=wx(ARENA[0]), x1=wx(ARENA[1]), y=WALKY, podiums=[wx(x) for x in PODIUMS])
    I.INFO['z4'] = info
    return info


def back_pass(w=1400, seed=861):
    """The mountains about the pass behind (the `back` layer at 0.7), lost in the cloud: where the cloud rolls in over
    the terraces' mountainside, its front heaped up in billows from the bottom of the picture to the top, the lower ones
    in front; behind it a wall of cloud filling the sky, the ridges only just showing in it, paler higher up. -> the
    picture."""
    L = Layer(w, SH)
    xs = np.arange(w)
    yy = np.arange(SH)[:, None] * np.ones((1, w))
    FR = 60
    t = 0.80 - 0.22 * (yy / SH) + 0.05 * (noise((SH, w), seed + 1, 30, 10) - 0.5)
    for k, (base, amp, sc, dk) in enumerate(((84, 22, 150, 0.08), (112, 14, 80, 0.13))):
        crest = base + amp * (noise((1, w), seed + 2 + k, sc, 0.5)[0] - 0.5) * 2
        t = np.where(yy >= crest[None, :], t - dk, t)
    L.put(toned(np.clip(t, 0, 1), FOG, dither=0.4), xs[None, :] * np.ones((SH, 1)) >= FR + 14)
    # the front: billows from the top of the picture down, each lit on its upper left
    r = rng(seed + 5)
    T = Tone(w, SH)
    y = -16
    while y < SH + 20:
        for j in range(2):
            rad = r.uniform(13, 24)
            cx = FR + r.uniform(-6, 16) + 10 * np.sin(y / 37.0)
            cy = y + r.uniform(-4, 4)
            for jj in range(int(-rad), int(rad) + 1):
                hy = int(cy + jj)
                if hy < 0 or hy >= SH:
                    continue
                half = np.sqrt(max(0.0, rad * rad - jj * jj))
                for ii in range(int(-half), int(half) + 1):
                    hx = int(cx + ii)
                    if hx < 0 or hx >= w:
                        continue
                    d = np.sqrt(ii * ii + jj * jj) / rad
                    tt = 0.80 - 0.22 * (hy / float(SH)) + 0.14 * max(0.0, (-ii * 0.6 - jj * 0.8) / rad) - 0.06 * max(0.0, (ii * 0.5 + jj * 0.8) / rad)
                    tt += 0.08 * (d > 0.86) * ((-ii - jj) > 0)
                    T.px(hx, hy, tt)
        y += r.uniform(10, 16)
    L.paste(T.layer(FOG, dither=0.35))
    return L
