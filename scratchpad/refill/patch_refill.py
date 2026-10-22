#!/usr/bin/env python3
"""Checkpoint refill (Khaled, 22 Oct 04:33): at every checkpoint, lives back up to the starting three (extra lives stay)
and the armour plates (also the 4x4's and the Apache's armour) back to full. Applies the same edits to the game's sources
(sim.js, fly.js, main.js, render.js) or to a built index.html. Every anchor must occur exactly once where it applies.
Usage: patch_refill.py src <dir>   |   patch_refill.py html <index.html>"""
import sys

CP_FOOT = ("    while (z2 + 1 < L.zones.length && p.x >= L.zones[z2 + 1].x) z2++;\n"
           "    if (z2 !== s.zone) { s.zone = z2; s.zoneScore = s.score; ev(s, { t: 'checkpoint', zone: z2, name: L.zones[z2].name }); }")
CP_FLY = ("    while (z2 + 1 < L.zones.length && s.u >= L.zones[z2 + 1].u) z2++;\n"
          "    if (z2 !== s.zone) { s.zone = z2; s.zoneScore = s.score; ev(s, { t: 'checkpoint', zone: z2, name: L.zones[z2].name }); }")
REFILL_FN = """  // a checkpoint fills Yazeed back up: lives to the starting three (extra lives stay) and the armour plates, which are the
  // 4x4's and the Apache's armour too, to full (Khaled, 22 Oct: more players through the Strait's coast road)
  function refill(s) {
    var p = s.p;
    if (!p || p.dead) return;
    var lives = Math.max(0, T.LIVES - p.lives), plates = Math.max(0, T.PLATES - p.plates);
    if (!lives && !plates) return;
    p.lives += lives; p.plates += plates;
    ev(s, { t: 'refill', x: p.x, y: p.y, lives: lives, plates: plates });
  }
"""
SIM = [
    (CP_FOOT, CP_FOOT[:-2] + " refill(s); }"),
    ("  function hurtPlayer(", REFILL_FN + "  function hurtPlayer("),
    ("_: { ev: ev, explode: explode,", "_: { ev: ev, refill: refill, explode: explode,"),
]
FLY = [(CP_FLY, CP_FLY[:-2] + " I.refill(s); }")]
MAIN = [
    ("        case 'plate_lost': Sound.sfx('plate'); buzz(35); break;\n",
     "        case 'plate_lost': Sound.sfx('plate'); buzz(35); break;\n"
     "        case 'refill': after(10, function () { Sound.sfx('pick_gren', { gain: 0.7 }); }); break;      // (a checkpoint refill)\n"),
]
RENDER = [
    ("var parts = [], decals = [], posts = [], popups = [], shake = 0, flashT = 0, tick = 0;",
     "var parts = [], decals = [], posts = [], popups = [], shake = 0, flashT = 0, tick = 0, refillT = 0;"),
    ("spin = {}; gunAng = 2.2; duckT = 0; flashT = 0; achoo.t = -999;",
     "spin = {}; gunAng = 2.2; duckT = 0; flashT = 0; achoo.t = -999; refillT = 0;"),
    ("  function onEvents(s, events) {\n",
     "  function onEvents(s, events) {\n"
     "    for (var ri = 0; ri < events.length; ri++) if (events[ri].t === 'refill') refillT = 60;      // (a checkpoint refill: the HUD glints)\n"),
    ("    for (i = 0; i < 3; i++) spr(i < p.plates ? 'hud_plate_on' : 'hud_plate_off', 30 + i * 9, 17);\n",
     "    for (i = 0; i < 3; i++) spr(i < p.plates ? 'hud_plate_on' : 'hud_plate_off', 30 + i * 9, 17);\n"
     "    var glint = refillT > 0 && ((refillT >> 2) & 1);        // a checkpoint refill: the plates and the heads glint gold for a second\n"
     "    if (refillT > 0 && !paused) refillT--;\n"
     "    if (glint) { cx.fillStyle = 'rgba(255,194,46,0.45)'; cx.fillRect(29, 16, 27, 9); }\n"),
    ("        } else { cx.drawImage(hd, hx, hy); text('m_org', '=' + lv, hx + hd.width + 3, hy + 2); }\n",
     "        } else { cx.drawImage(hd, hx, hy); text('m_org', '=' + lv, hx + hd.width + 3, hy + 2); }\n"
     "        if (glint && lv) { cx.fillStyle = 'rgba(255,194,46,0.45)'; cx.fillRect(hx - 1, hy - 1, Math.min(lv, 4) * (hd.width + 2) + 1, hd.height + 2); }\n"),
]


def apply(text, edits, where):
    for old, new in edits:
        n = text.count(old)
        if n != 1:
            sys.exit('%s: anchor found %d times: %r' % (where, n, old[:80]))
        text = text.replace(old, new)
    return text


def main():
    mode, path = sys.argv[1], sys.argv[2]
    if mode == 'src':
        for name, edits in (('sim.js', SIM), ('fly.js', FLY), ('main.js', MAIN), ('render.js', RENDER)):
            p = path.rstrip('/') + '/' + name
            t = open(p, encoding='utf-8').read()
            if 'refill' in t and name != 'main.js' or "case 'refill'" in t:
                sys.exit(p + ': already has the refill')
            open(p, 'w', encoding='utf-8').write(apply(t, edits, p))
            print('patched', p)
    else:
        t = open(path, encoding='utf-8').read()
        if "t: 'refill'" in t:
            sys.exit(path + ': already has the refill')
        t = apply(t, SIM + MAIN + RENDER, path)          # (no Taiz on main: fly.js isn't in this page)
        open(path, 'w', encoding='utf-8').write(t)
        print('patched', path)


main()
