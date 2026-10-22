# hud.py - arcade-style HUD, touch controls and dialogue bars.
from px import *
from palette import P
from world import UI, pill, frame, INK
import cast

ICON = {
    'plate': ['MMMMMMM', 'MQQMMMm', 'MQMMMMm', 'MMMMMMm', 'MMMMMMm', '.MMMMm.', '..MMm..', '...m...'],
    'heart': ['.R.R.', 'RRRRR', 'RRRRR', '.RRR.', '..R..'],
    'grenade': ['..QQ...', '.QMY...', '.GGGGG.', 'GgGGGGG', 'GGGGGGG', 'GgGGGGG', 'GGGGGGG', '.GGGGG.'],
    'radio': ['......Q', '.....Q.', '....Q..', 'MMMMMM.', 'MQQQQM.', 'MMMMMM.', 'MoMoMM.', 'MMMMMM.', 'MMMMMM.'],
    'freed': ['.TTT.', '.TTT.', 'T.T.T', '.TTT.', '..T..', '.T.T.', '.T.T.'],
    'lock': ['.MMM.', 'M...M', 'M...M', 'YYYYY', 'YYoYY', 'YYoYY', 'YYYYY'],
    'crate': ['WWWWWWW', 'WxxxxxW', 'WWWWWWW', 'WxWWWxW', 'WWWWWWW', 'WxxxxxW', 'WWWWWWW'],
    'medal': ['.R.R.', '.R.R.', '..R..', '.YYY.', 'YYyYY', 'YyYyY', 'YYyYY', '.YYY.'],
    'medal_off': ['.m.m.', '.m.m.', '..m..', '.mmm.', 'mm.mm', 'm...m', 'mm.mm', '.mmm.'],
    'fuel': ['...R...', '..RRR..', '..RRR..', '.RRRRR.', '.RRrRR.', 'RRRrRRR', 'RRRRRRR', '.RRRRR.'],
    'missile': ['...Q...', '..QMQ..', '..MMM..', '..MRM..', '..MMM..', '.MMMMM.', '.M.F.M.', '...F...'],
    'drone': ['Q.....Q', 'MM...MM', '.MMMMM.', '..MRM..', '.MMMMM.', 'MM...MM', 'Q.....Q'],
    'signal': ['Y..Q..Y', '.Y.Q.Y.', '...Q...', '..QMQ..', '..MMM..', '.M.M.M.', '.M...M.', 'MM...MM'],
    'command': ['...Y...', '..YYY..', 'YYYYYYY', '.YYYYY.', '.YY.YY.', 'YY...YY'],
    'check': ['......T', '.....TT', 'T...TT.', 'TT.TT..', '.TTT...', '..T....'],
    'cross': ['R...R', '.R.R.', '..R..', '.R.R.', 'R...R'],
    'pause': ['TT.TT', 'TT.TT', 'TT.TT', 'TT.TT', 'TT.TT', 'TT.TT', 'TT.TT'],
    'up': ['...T...', '..TTT..', '.TTTTT.', 'TTTTTTT', '..TTT..', '..TTT..', '..TTT..'],
    'gate': ['.TTTTT.', 'TTtttTT', 'TTt.tTT', 'TT...TT', 'TT...TT', 'TT...TT'],
    'scorpion': ['Y.....Y', 'YY...YY', '.Y.Y.Y.', '..YYY..', '..YYY..', '...Y..Y', '...YYYY'],
    'inf': ['.TT..TT.', 'T..TT..T', 'T..TT..T', '.TT..TT.'],
}
IPAL = {'M': '#98a4b4', 'm': '#3e4656', 'Q': '#d4dce4', 'R': '#e8483c', 'r': '#f8b830', 'Y': '#f8b830',
        'y': '#c8922a', 'G': '#8a9a4e', 'g': '#aebb6a', 'T': '#f4ecd0', 't': '#a89c88',
        'o': INK, 'W': '#a8703c', 'x': '#7c4c2c', 'F': '#fb9a2a'}


def icon(name, pal=None, edge=None):
    im = sprite(ICON[name], pal or IPAL)
    if edge:
        im = outline(im, edge)
    return im


def portrait(im, x, y, head, pal, bg, size=(22, 20), rim='#f8b830'):
    """Framed head shot; tall hats are clipped at the top of the frame."""
    w, h = size
    lay = new(w, h, rgba(bg))
    rect(lay, 0, h - 5, w - 1, h - 1, (0, 0, 0, 55))
    hd = outline(sprite(cast.HEADS[head], pal), INK)
    blit(lay, hd, (w - hd.width) // 2, h - hd.height - 1)
    blit(im, lay, x, y)
    frame(im, x - 1, y - 1, x + w, y + h, rim)
    frame(im, x - 2, y - 2, x + w + 1, y + h + 1, INK)


HERO_BG = {'yazeed': '#2a66a8', 'salem': '#c8922a', 'bilqis': '#862a38', 'arwa': '#2e8048'}
HERO_HEAD = {'yazeed': 'wrap', 'salem': 'straw', 'bilqis': 'veil', 'arwa': 'scarf'}


def digits(im, x, y, s, scale_=1, color=None, align='l'):
    return text(im, x, y, s, FONT_M, color or UI['cream'], edge=INK, scale_=scale_, align=align)


def gameplay_hud(im, hero='yazeed', plates=3, lives=3, arms='187', bombs='10', score=12400,
                 radio=1.4, freed=(2, 5), time='1:42', par='4:30', locked=False):
    # portrait, name, armour, lives
    portrait(im, 6, 6, HERO_HEAD[hero], cast.PAL[hero], HERO_BG[hero])
    text(im, 33, 5, hero.upper(), FONT_S, UI['amber'], edge=INK)
    for i in range(3):
        ic = icon('plate') if i < plates else icon('plate', {'M': '#262c3a', 'm': '#262c3a', 'Q': '#3e4656'})
        blit(im, outline(ic, INK), 32 + i * 10, 14)
    blit(im, icon('heart', edge=INK), 63, 15)
    text(im, 71, 16, 'x%d' % lives, FONT_S, UI['cream'], edge=INK)
    # ARMS / BOMB box
    x0 = 86
    pill(im, x0, 4, x0 + 67, 26, (24, 18, 34, 190), r=3)
    frame(im, x0, 4, x0 + 67, 26, '#f4ecd0')
    text(im, x0 + 17, 7, 'ARMS', FONT_S, UI['amber'], align='c')
    text(im, x0 + 51, 7, 'BOMB', FONT_S, UI['amber'], align='c')
    vline(im, x0 + 34, 7, 23, (244, 236, 208, 110))
    if arms == 'inf':
        blit(im, scale(icon('inf'), 1), x0 + 13, 17)
    else:
        text(im, x0 + 17, 15, arms, FONT_M, '#ffffff', align='c')
    if locked:
        blit(im, icon('lock', edge=INK), x0 + 47, 14)
    else:
        text(im, x0 + 51, 15, bombs, FONT_M, '#ffffff', align='c')
    # score
    text(im, 160, 5, 'SCORE', FONT_S, UI['amber'], edge=INK)
    digits(im, 160, 13, '%07d' % score)
    # time, top centre
    digits(im, W // 2, 4, time, scale_=2, color='#ffffff', align='c')
    text(im, W // 2, 22, 'PAR ' + par, FONT_S, UI['cream'], edge=INK, align='c')
    # freed detainees
    blit(im, icon('freed', edge=INK), 292, 5)
    text(im, 302, 6, 'FREED', FONT_S, UI['amber'], edge=INK)
    digits(im, 302, 13, '%d/%d' % freed)
    # radio meter (tap to call support)
    ready = radio >= 1
    x0 = 352
    pill(im, x0, 4, x0 + 92, 26, (24, 18, 34, 190), r=3)
    frame(im, x0, 4, x0 + 92, 26, UI['amber'] if ready else '#a89c88')
    blit(im, outline(icon('radio'), INK), x0 + 4, 9)
    text(im, x0 + 16, 7, 'RADIO', FONT_S, UI['amber'] if ready else UI['dim'])
    if ready:
        text(im, x0 + 88, 7, 'TAP!', FONT_S, '#ffffff', align='r')
    for i in range(3):
        bx = x0 + 16 + i * 25
        rect(im, bx, 15, bx + 22, 21, (0, 0, 0, 150))
        fill = max(0.0, min(1.0, radio - i))
        if fill > 0:
            c1, c2 = ('#f8b830', '#fde48a') if fill >= 1 else ('#b0862c', '#c89c44')
            rect(im, bx, 15, bx + int(22 * fill), 21, c1)
            rect(im, bx, 15, bx + int(22 * fill), 16, c2)
        frame(im, bx - 1, 14, bx + 23, 22, INK)
    # pause
    pill(im, 449, 4, 464, 26, (24, 18, 34, 190), r=3)
    blit(im, icon('pause'), 454, 12)


def _btn(layer, cx, cy, r, fill_a=70, ring_a=200):
    """Dark glass with a bright ring: readable over bright and dark scenes alike."""
    disc(layer, cx, cy, r, (22, 16, 32, fill_a))
    ring(layer, cx, cy, r, (255, 255, 255, ring_a), 1)
    ring(layer, cx, cy, r + 1, (22, 16, 32, 130), 1)
    ring(layer, cx, cy, r - 2, (255, 255, 255, 40), 1)


def touch_controls(im, stick=(1, 0), locked=False):
    lay = new()
    cx, cy = 46, 170
    disc(lay, cx, cy, 29, (22, 16, 32, 55))
    ring(lay, cx, cy, 29, (255, 255, 255, 170), 1)
    ring(lay, cx, cy, 30, (22, 16, 32, 120), 1)
    kx, ky = cx + stick[0] * 12, cy + stick[1] * 12
    disc(lay, kx, ky, 13, (255, 255, 255, 120))
    ring(lay, kx, ky, 13, (255, 255, 255, 235), 1)
    ring(lay, kx, ky, 14, (22, 16, 32, 120), 1)
    for dx, dy in ((-23, 0), (23, 0), (0, -23), (0, 23)):
        rect(lay, cx + dx - (1 if dy else 0), cy + dy - (1 if dx else 0),
             cx + dx + (1 if dy else 0), cy + dy + (1 if dx else 0), (255, 255, 255, 200))
    fx, fy = 424, 170
    _btn(lay, fx, fy, 24, 90, 230)
    jx, jy = 376, 190
    _btn(lay, jx, jy, 17)
    gx, gy = 444, 120
    _btn(lay, gx, gy, 16)
    blit(im, lay, 0, 0)
    wht = (255, 255, 255, 240)
    t = text_img('FIRE', FONT_S, wht)
    blit(im, t, fx - t.width // 2 + 1, fy + 8)
    rect(im, fx - 8, fy - 6, fx + 2, fy, wht)            # bullet glyph
    poly(im, [(fx + 3, fy - 6), (fx + 8, fy - 3), (fx + 3, fy)], wht)
    rect(im, fx - 8, fy - 6, fx - 6, fy, (255, 255, 255, 150))
    blit(im, icon('up', {'T': wht}), jx - 3, jy - 8)
    t = text_img('JUMP', FONT_S, wht)
    blit(im, t, jx - t.width // 2 + 1, jy + 3)
    g = icon('grenade', {k: wht for k in 'QMYG'} | {'g': (255, 255, 255, 150)})
    blit(im, g, gx - 3, gy - 8)
    t = text_img('BOMB', FONT_S, wht)
    blit(im, t, gx - t.width // 2 + 1, gy + 3)
    if locked:
        blit(im, outline(icon('lock'), INK), gx + 6, gy - 12)


def dialog_bar(im, head, pal, bg, name, line, y=186, x0=92, x1=356, name_c=None):
    """Subtitle bar: portrait, speaker and one English line. The bars after the
    name mark that the voice itself is gibberish."""
    pill(im, x0, y, x1, y + 25, UI['panel2'], r=3)
    frame(im, x0, y, x1, y + 25, '#f4ecd0')
    portrait(im, x0 + 5, y + 4, head, pal, bg, size=(20, 18))
    text(im, x0 + 31, y + 4, name, FONT_S, name_c or UI['amber'])
    nx = x0 + 31 + text_w(name, FONT_S) + 4
    for i, hgt in enumerate((1, 3, 2, 4, 2, 3, 1)):
        vline(im, nx + i * 2, y + 8 - hgt, y + 8, UI['dim'])
    text(im, x0 + 31, y + 13, line, FONT_M, UI['cream'])
