# look_ibb.py - Ibb's painted zones seen as the game will show them: the layers composed at a camera position, with the
# screens (stage 1's sprites: the billboard, the shop sets on their crates) and people (Yazeed, a few of the Zanabeel)
# drawn over them at their places, for judging scale and readability before anything goes into the game.
import json
import numpy as np
from PIL import Image
from paint import Layer
import stage_ibb as I

GAME = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/'
_A = {}


def sheets():
    if not _A:
        _A['atlas'] = Image.open(GAME + 'art/out/atlas.png').convert('RGBA')
        _A['af'] = json.load(open(GAME + 'gen/atlas.json'))['frames']
        _A['ibb'] = Image.open(GAME + 'art/out/ibb.png').convert('RGBA')
        _A['if'] = json.load(open(GAME + 'gen/ibb_sprites.json'))['frames']
    return _A


def spr(im, name, x, y, flip=False, ibb=False):
    """Draw a frame with its anchor at (x, y), as the game's spr() does."""
    A = sheets()
    sheet, fr = (A['ibb'], A['if']) if ibb else (A['atlas'], A['af'])
    fx, fy, w, h, ax, ay = fr[name]
    f = sheet.crop((fx, fy, fx + w, fy + h))
    if flip:
        f = f.transpose(Image.FLIP_LEFT_RIGHT)
        ax = w - 1 - ax
    im.alpha_composite(f, (int(x - ax), int(y - ay)))


def board(im, x, gy):
    """The billboard as render_ibb draws it: the panel on two legs, the frame over it."""
    from PIL import ImageDraw
    x0, y1 = int(x) - 72, int(gy) - 16
    y0 = y1 - 96
    d = ImageDraw.Draw(im)
    for lx in (x0 + 22, x0 + 116):
        d.rectangle((lx, y1 + 3, lx + 5, gy - 1), fill=(18, 14, 10, 255))
        d.rectangle((lx + 1, y1 + 3, lx + 4, gy - 1), fill=(58, 62, 68, 255))
        d.rectangle((lx + 1, y1 + 3, lx + 1, gy - 1), fill=(90, 96, 104, 255))
    spr(im, 'board', x0, y0, ibb=True)
    spr(im, 'board_frame', x0, y0, ibb=True)


def tv(im, x, gy):
    base = int(gy) - 14
    spr(im, 'crate', x, gy, ibb=True)
    spr(im, 'tv1', x - 20, base - 26, ibb=True)
    spr(im, 'tv_box', x, base, ibb=True)


def shot(S, cam, things, w=I.SW):
    """One picture: the layers at camera `cam`, then each thing: ('board', x, gy) | ('tv', x, gy) | (frame, x, y, flip)."""
    L = I.compose(cam, S, w, fore=False)
    im = L.image()
    for t in things:
        if t[0] == 'board':
            board(im, t[1] - cam, t[2])
        elif t[0] == 'tv':
            tv(im, t[1] - cam, t[2])
        else:
            spr(im, t[0], t[1] - cam, t[2], flip=t[3] if len(t) > 3 else False)
    if 'fore' in S:
        F = Layer(w, I.SH)
        F.paste(S['fore'], -int(cam * 1.25), 0)
        im.alpha_composite(F.image())
    return im


def sheet_of(S, shots, path, scale=2, w=I.SW):
    cols = 2
    rows = (len(shots) + 1) // 2
    out = Image.new('RGBA', ((w + 6) * cols - 6, (I.SH + 6) * rows - 6), (20, 16, 24, 255))
    for i, (cam, things) in enumerate(shots):
        out.alpha_composite(shot(S, cam, things, w), ((i % cols) * (w + 6), (i // cols) * (I.SH + 6)))
    out = out.resize((out.width * scale, out.height * scale), Image.NEAREST)
    out.save(path)
    return out.size
