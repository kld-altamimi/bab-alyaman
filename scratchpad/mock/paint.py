# paint.py - a small painter for stage art in the arcade manner: no outlines, many close
# tones per material, checker dither between neighbours, light from the upper left.
# Every picture is a scalar "tone" field mapped through a colour ramp.
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw


def hexrgb(h):
    h = h.lstrip('#')
    return np.array([int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)], dtype=np.float64)


def ramp(keys, n=16, snap=True):
    """Interpolate key colours into n steps. snap keeps the 5-bit-per-channel look."""
    keys = [hexrgb(k) for k in keys]
    xs = np.linspace(0, len(keys) - 1, n)
    out = np.zeros((n, 3))
    for i, x in enumerate(xs):
        a = int(np.floor(x))
        b = min(a + 1, len(keys) - 1)
        t = x - a
        out[i] = keys[a] * (1 - t) + keys[b] * t
    if snap:
        out = np.round(out / 8) * 8
    return np.clip(out, 0, 255).astype(np.uint8)


def rng(seed):
    return np.random.default_rng(seed)


def noise(shape, seed, sx, sy):
    """Smooth noise in 0..1, stretched sx by sy pixels."""
    h, w = shape
    r = rng(seed).random((h, w))
    f = ndi.gaussian_filter(r, (sy, sx), mode='wrap')
    lo, hi = f.min(), f.max()
    return (f - lo) / (hi - lo + 1e-9)


def fbm(shape, seed, sx, sy, octaves=4, gain=0.5):
    out = np.zeros(shape)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        out += amp * noise(shape, seed * 31 + o * 7 + 1, max(0.4, sx / 2 ** o), max(0.4, sy / 2 ** o))
        tot += amp
        amp *= gain
    out /= tot
    lo, hi = out.min(), out.max()
    return (out - lo) / (hi - lo + 1e-9)


BAYER2 = np.array([[0.125, 0.625], [0.875, 0.375]])
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 + 1 / 32.0


def toned(tone, rmp, dither=0.5, matrix=BAYER2, x0=0, y0=0):
    """Map a tone field (0..1) through a ramp. dither is the share of each step that is
    blended with its neighbour by the checker; 0 gives hard bands."""
    h, w = tone.shape
    n = len(rmp)
    f = np.clip(tone, 0, 1) * (n - 1)
    i0 = np.floor(f)
    frac = f - i0
    if dither > 0:
        fr = np.clip((frac - 0.5) / dither + 0.5, 0, 1)
    else:
        fr = (frac > 0.5).astype(float)
    my, mx = matrix.shape
    yy = (np.arange(h)[:, None] + y0) % my
    xx = (np.arange(w)[None, :] + x0) % mx
    thr = matrix[yy, xx]
    idx = np.clip(i0 + (fr > thr), 0, n - 1).astype(int)
    return rmp[idx]


class Layer:
    """RGB picture with a coverage mask."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.rgb = np.zeros((h, w, 3), dtype=np.uint8)
        self.a = np.zeros((h, w), dtype=bool)

    def put(self, rgb, mask):
        self.rgb[mask] = rgb[mask]
        self.a |= mask

    def paste(self, other, x=0, y=0):
        """Draw another layer on top at (x, y)."""
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + other.w), min(self.h, y + other.h)
        if x1 <= x0 or y1 <= y0:
            return
        sub_a = other.a[y0 - y:y1 - y, x0 - x:x1 - x]
        sub_rgb = other.rgb[y0 - y:y1 - y, x0 - x:x1 - x]
        self.rgb[y0:y1, x0:x1][sub_a] = sub_rgb[sub_a]
        self.a[y0:y1, x0:x1] |= sub_a

    def image(self):
        im = np.zeros((self.h, self.w, 4), dtype=np.uint8)
        im[..., :3] = self.rgb
        im[..., 3] = np.where(self.a, 255, 0)
        return Image.fromarray(im, 'RGBA')

    def crop(self, x0, y0, x1, y1):
        out = Layer(x1 - x0, y1 - y0)
        out.rgb = self.rgb[y0:y1, x0:x1].copy()
        out.a = self.a[y0:y1, x0:x1].copy()
        return out


def from_image(im):
    arr = np.array(im.convert('RGBA'))
    L = Layer(arr.shape[1], arr.shape[0])
    L.rgb = arr[..., :3].copy()
    L.a = arr[..., 3] > 127
    return L


def poly_mask(w, h, pts):
    im = Image.new('1', (w, h), 0)
    ImageDraw.Draw(im).polygon([(float(x), float(y)) for x, y in pts], fill=1)
    return np.array(im, dtype=bool)


def line_mask(w, h, pts, width=1):
    im = Image.new('1', (w, h), 0)
    ImageDraw.Draw(im).line([(float(x), float(y)) for x, y in pts], fill=1, width=width)
    return np.array(im, dtype=bool)


def ellipse_mask(w, h, x0, y0, x1, y1):
    im = Image.new('1', (w, h), 0)
    ImageDraw.Draw(im).ellipse((x0, y0, x1, y1), fill=1)
    return np.array(im, dtype=bool)


def light(height, lx=-0.7, ly=-0.7, scale=1.0):
    """Shade a height field lit from (lx, ly): the upper left by default."""
    gy, gx = np.gradient(height)
    return -(gx * lx + gy * ly) * scale


def edge_in(mask, n=1):
    """Pixels of the mask within n of its edge."""
    er = ndi.binary_erosion(mask, iterations=n)
    return mask & ~er


def shadow_under(mask, dy=1, dx=0):
    """Mask shifted, for cast shadows."""
    out = np.zeros_like(mask)
    h, w = mask.shape
    ys, xs = np.nonzero(mask)
    ys2, xs2 = ys + dy, xs + dx
    ok = (ys2 >= 0) & (ys2 < h) & (xs2 >= 0) & (xs2 < w)
    out[ys2[ok], xs2[ok]] = True
    return out


class Tone:
    """A tone canvas: draw in 0..1 (dark..pale), then map through a ramp once."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.t = np.zeros((h, w))
        self.m = np.zeros((h, w), bool)

    def rect(self, x0, y0, x1, y1, t):
        x0, x1 = max(0, int(x0)), min(self.w - 1, int(x1))
        y0, y1 = max(0, int(y0)), min(self.h - 1, int(y1))
        if x1 < x0 or y1 < y0:
            return
        self.t[y0:y1 + 1, x0:x1 + 1] = t
        self.m[y0:y1 + 1, x0:x1 + 1] = True

    def px(self, x, y, t):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.t[int(y), int(x)] = t
            self.m[int(y), int(x)] = True

    def mask(self, m, t):
        self.t = np.where(m, t, self.t)
        self.m |= m

    def poly(self, pts, t):
        self.mask(poly_mask(self.w, self.h, pts), t)

    def line(self, pts, t, width=1):
        self.mask(line_mask(self.w, self.h, pts, width), t)

    def layer(self, rmp, dither=0.5, grain=0.0, seed=1):
        t = self.t
        if grain:
            t = t + grain * (noise((self.h, self.w), seed, 2.5, 1.2) - 0.5)
        L = Layer(self.w, self.h)
        L.put(toned(np.clip(t, 0, 1), rmp, dither=dither), self.m)
        return L
