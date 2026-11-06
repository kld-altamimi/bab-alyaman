# variants.py - copies of the game's sources with one change each to the guard (the flashing that makes a man's shots
# glance off), for guard_audit.js to compare (Khaled, 25 Oct 03:37: "Most players are on phone, and now there is a big
# phone area with an invisible wall for shots, can you find other solutions, and remove the one with the lining up of the
# first attack").
#   base        as the game is (the guard at the edges, in doorways, and on a rifleman's or bomber's first attack)
#   nofirst     no guard on the first attack (Khaled's call)
#   open        nofirst, and nothing guarded at the edges either: shots, blasts, the knife and the aim help reach anyone on
#               the screen (the road's pickups and drones too). Nobody still starts an attack under the thumbs; doorways keep
#               their fade-in
#   enter       open, and a rifleman walking in from an edge fires one level round as he steps into the picture (no aiming
#               first: the slow bullet is the warning), then carries on as before
#   enter_b     enter, and a bomber walking in from an edge lights up as he steps in and throws from where he stands
#   narrow      nofirst, with the edge guard kept but the strips as narrow on a phone as on a computer (the audit is run
#               with lanes 0.07 / 0.09 for it)
# Usage: python3 variants.py [names...]
import os, shutil, sys
SP = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/'
SRC = SP + 'game/'
OUT = SP + 'guard/var/'


def make(name, edits):
    d = OUT + name + '/'
    if os.path.isdir(d):
        shutil.rmtree(d)
    for sub in ('src', 'tools', 'gen'):
        shutil.copytree(SRC + sub, d + sub, ignore=shutil.ignore_patterns('_pre_*', '*_build*', '*_0[0-9]*', '*_r[0-9]*', '*_before*'))
    for f, old, new in edits:
        p = d + 'src/' + f
        s = open(p).read()
        assert s.count(old) == 1, (name, f, old[:70], s.count(old))
        open(p, 'w').write(s.replace(old, new))
    print('made', name)


GUARD0 = "  function guarded(s, e) { return !!e && e.alive && e.hostile && ((!e.ext && (!inMiddle(s, e.x) || e.emerge > 0)) || (e.first && (e.st === 'aim' || e.st === 'wind'))); }"
NOFIRST = [('sim.js', GUARD0, "  function guarded(s, e) { return !!e && e.alive && e.hostile && !e.ext && (!inMiddle(s, e.x) || e.emerge > 0); }")]
OPEN = [('sim.js', GUARD0, "  function guarded(s, e) { return !!e && e.alive && e.hostile && !e.ext && e.emerge > 0; }"),
        ('sim.js', "  function inReach(s, x) { return inMiddle(s, x); }", "  function inReach(s, x) { return onScreen(s, x, 0); }"),
        ('drive.js', "      if (!staged(s, t.x) && (onGun || (b.x > t.x - D.TRUCK_HW && b.x < t.x + D.TRUCK_HW && b.y > t.y - D.TRUCK_H && b.y < t.y))) {\n        ev(s, { t: 'hit', kind: 'guard', x: b.x, y: b.y });\n        return true;\n      }\n", ""),
        ('drive.js', "        if (!staged(s, d.x)) { ev(s, { t: 'hit', kind: 'guard', x: b.x, y: b.y }); return true; }\n", ""),
        ('drive.js', "      if (t.st !== 'ok' || (own && !staged(s, t.x))) continue;", "      if (t.st !== 'ok') continue;"),
        ('drive.js', "if (t.st === 'ok' && t.gun > 0 && staged(s, t.x)) consider(", "if (t.st === 'ok' && t.gun > 0 && onScreen(s, t.x)) consider("),
        ('drive.js', "if (d.st !== 'gone' && staged(s, d.x)) consider(", "if (d.st !== 'gone' && onScreen(s, d.x)) consider(")]
HOOK = "    if (p.dead || s.status !== 'play') { if (e.st !== 'walk' && e.st !== 'wait') { e.st = e.post ? 'wait' : 'walk'; e.stT = 0; } return; }\n"
ENTER = [('sim.js', HOOK, HOOK +
          "    if (!e.entered) {\n"
          "      e.entered = true;\n"
          "      // he comes in shooting: one round as he steps into the picture, no aiming first (the slow bullet is the warning)\n"
          "      if (!e.post && e.k === 'rifle' && e.st === 'walk' && !staged(s, e)) { e.face = dx >= 0 ? 1 : -1; enemyFire(s, e, false, 26); e.enterShot = true; }\n"
          "    }\n")]
ENTER_B = [('sim.js', HOOK, HOOK +
            "    if (!e.entered) {\n"
            "      e.entered = true;\n"
            "      if (!e.post && e.k === 'rifle' && e.st === 'walk' && !staged(s, e)) { e.face = dx >= 0 ? 1 : -1; enemyFire(s, e, false, 26); e.enterShot = true; }\n"
            "      // a bomber comes in with his stick already lit, and throws from where he stands\n"
            "      if (!e.post && e.k === 'bomber' && e.st === 'walk' && !staged(s, e) && ad > 26) { e.face = dx >= 0 ? 1 : -1; e.st = 'wind'; e.stT = 22; e.lit = true; e.moving = 0; ev(s, { t: 'tell', k: 'bomber', x: e.x, y: e.y }); }\n"
            "    }\n")]
which = sys.argv[1:] or ['base', 'nofirst', 'open', 'enter', 'enter_b', 'narrow']
for n in which:
    make(n, {'base': [], 'nofirst': NOFIRST, 'open': OPEN, 'enter': OPEN + ENTER, 'enter_b': OPEN + ENTER_B, 'narrow': NOFIRST}[n])
