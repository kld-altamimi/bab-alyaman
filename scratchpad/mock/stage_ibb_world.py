# stage_ibb_world.py - Ibb's stage as one painting (Khaled, 29 Oct 21:36: "The transition between the zones is not
# seemless especially 1 to 2", and "the zones in this mission are a bit short"). Every zone paints into one long play
# picture through a window onto it (its own x from 0, as before), after the ground along the whole road has been painted
# in one piece: the valley's verge and asphalt, the asphalt's last stretch breaking up over the town's setts, the setts
# running on through Jibla to the foot of the terraces. What crosses a join is painted across it (the town's edge, the
# poles carrying the wires into the town, Jibla's last field wall running on into the terraces). The export cuts the
# picture at the zones' starts, so a join is a cut through one painting. The mountainside behind (the `back` layer, at
# 0.7) is one painting too, its slope and terraces in one piece from Jibla's town to the falls; the foreground's tufts
# one strip along the whole mission.
import numpy as np
from paint import *
import stage_mocha as SM
import stage_ibb as I
import stage_ibb_z1 as Z1
import stage_ibb_z1x as Z1X
import stage_ibb_z2 as Z2
import stage_ibb_z3 as Z3

SH = I.SH
ASPHALT_END = 1990               # the valley's asphalt whole to here, then breaking up over the setts
SETTS_FROM = 1960                # the town's setts from here (under the asphalt's last stretch)
SETTS_FULL = 2260                # the last of the asphalt
VERGE_END = 2140                 # the gravel verge as far as the town's first house


def view(L, ox, w):
    """A window onto L from x = ox, w wide: a Layer whose pixels are L's (painting into it paints L)."""
    V = Layer.__new__(Layer)
    V.w, V.h = w, L.h
    V.rgb = L.rgb[:, ox:ox + w]
    V.a = L.a[:, ox:ox + w]
    return V


def ground(L, seed=901):
    """The ground along the whole road, in one piece: the verge and the valley's asphalt, the setts from the town's edge
    to the foot of the terraces, and between the two the asphalt's last stretch breaking up, holes opening in it over the
    setts, more and wider toward the town, each with a dark broken rim."""
    Z1.verge(L, 0, VERGE_END, seed=seed)
    Z2.cobbles(L, SETTS_FROM, Z3.X0 + 40, seed=seed + 1)
    R = Layer(L.w, L.h)
    Z1.road(R, 0, SETTS_FULL, seed=seed + 2)
    x0, x1 = ASPHALT_END, SETTS_FULL
    n = noise((SH, x1 - x0), seed + 3, 4.5, 2.2)
    xs = np.arange(x0, x1)
    u = np.clip((xs - x0) / float(x1 - x0), 0, 1) ** 0.8
    road_rows = slice(Z1.ROAD_TOP, SH)
    sample = np.sort(n[road_rows].ravel())
    thr = sample[np.clip((u * (len(sample) - 1)).astype(int), 0, len(sample) - 1)]
    keep = n > thr[None, :]
    keep[:, :4] = True
    R.a[:, x0:x1] &= keep
    R.a[:, x1:] = False
    # the broken rim: asphalt next to a hole is darker
    a = R.a[:, x0:x1]
    edge = a & ~(np.roll(a, 1, 0) & np.roll(a, -1, 0) & np.roll(a, 1, 1) & np.roll(a, -1, 1))
    edge[:Z1.ROAD_TOP + 1] = False
    sub = R.rgb[:, x0:x1]
    sub[edge] = (sub[edge].astype(float) * 0.62).astype(np.uint8)
    L.paste(R)


def joins(L, seed=951):
    """What crosses the joins between the zones, painted across them: the town's edge (a half-built house of blocks, a
    low wall, the last poles carrying the wires into Jibla); the way out of Jibla, its field wall and sorghum running on
    into the terraces, where the street ends at the path."""
    e = Z1X.town_edge(L, 1960, seed=seed)
    # the poles: zone 1's last one carries the wires on to one at the town's edge and one at the first house
    ends = I.INFO.get('pole_ends')
    poles = [(2068, 0), (2160, 1)]
    nxt = [Z1.pole(L, px_, Z1.VERGE + 4, hgt=112, seed=seed + 5 + k, horns=hn) for k, (px_, hn) in enumerate(poles)]
    if ends:
        Z1.wires(L, ends, nxt[0], sag=int(round(9 * (2068 - 1946) / 280.0)))
    Z1.wires(L, nxt[0], nxt[1], sag=4)
    # Jibla's last field wall, from the ruin to the terraces' first steps
    wx0, wx1 = Z2.X0 + 1840, Z3.X0 + 40
    Z1.drystone(L, wx0, wx1, 140, Z2.BASE + 1, seed=seed + 10)
    Z1.crops(L, wx0 + 4, wx1 - 4, 140, seed=seed + 11, hmin=10, hmax=18)
    return e


# ------------------------------------------------------------------ the whole play picture
def play(seed=0):
    """-> the play picture (0 to the end of the last zone) with I.PLATS and I.INFO filled."""
    W = Z3.END3
    L = Layer(W, SH)
    ground(L)
    Z1.play_z1(view(L, 0, Z1.W1), ground=False)
    Z2.play_z2(view(L, Z2.X0, Z2.W2), ground=False)
    Z3.play_z3(view(L, Z3.X0, Z3.W3), ground=False)
    e = joins(L)
    I.INFO['edge'] = e
    return L


# ------------------------------------------------------------------ the mountainside behind, in one piece
def back(seed=0):
    """-> the `back` layer's picture (from Z2.BACK_X): Jibla climbing its slope, then the terraces' mountainside with
    its falls and its hamlet on a spur, on one slope: one skyline and one sweep of terraces across the two."""
    w2, w3 = Z2.BACK_W, 1410
    W = w2 + w3
    L = Layer(W, SH)
    c2 = Z2.back_crest(w2, 61)
    c3 = Z3.back_crest(w3, 461)
    crest = np.concatenate([c2, c3])
    # (the two skylines meet at 76; ease the meeting over a few columns)
    k = 24
    crest[w2 - k:w2 + k] = np.linspace(crest[w2 - k], crest[w2 + k - 1], 2 * k)
    yy, xx = np.mgrid[0:SH, 0:W]
    m = yy >= crest[None, :]
    per = 6.0
    E = yy - 0.35 * (crest[None, :] - crest.mean())
    frac = (E / per) - np.floor(E / per)
    t = 0.52 + 0.08 * (noise((SH, W), 62, 18, 3) - 0.5) - 0.14 * (frac > 0.72) + 0.06 * (frac < 0.2)
    L.put(toned(np.clip(t, 0, 1), I.TERR, dither=0.5), m)
    Z2.back_town(w2, 61, L=view(L, 0, w2), crest=crest[:w2], slope=False)
    Z3.back_falls(w3, 461, L=view(L, w2, w3), crest=crest[w2:], slope=False)
    # the mountainside further off than the town: a haze coming on across the join
    hz = np.clip((np.arange(W) - (w2 - 200)) / 400.0, 0, 1) * 0.10
    sub = L.rgb.astype(float)
    L.rgb[:] = np.clip(sub * (1 - hz[None, :, None]) + Z2.HAZE_T * hz[None, :, None], 0, 255).astype(np.uint8)
    return L


def fore(seed=131):
    """-> the foreground's strip along the whole mission (at 1.25 of the street's pace): tufts and stones."""
    return Z1.fore_z1(w=int(Z3.END3 * 1.25) + 600, seed=seed)
