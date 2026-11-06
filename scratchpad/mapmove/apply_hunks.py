# apply_hunks.py - applies the map build's index.html hunks (0.13.70 -> 0.13.72, game-features) to the game's source
# files: each hunk's old text (context and removed lines) must be found exactly once across the live sources, and is
# replaced by its new text. Hunks for BUILD and LANG_AR are skipped (the build stamps BUILD; the Arabic line is added
# to lang_ar.json separately). Usage: python3 apply_hunks.py <diff> <src dir> [--dry]
import sys, os, re
diff, src = sys.argv[1], sys.argv[2]
dry = '--dry' in sys.argv
FILES = ['menu.js', 'main.js', 'campaign.js', 'input.js', 'render.js', 'lang.js', 'badges.js', 'audio.js', 'level.js', 'sim.js']
texts = {f: open(os.path.join(src, f), encoding='utf-8').read() for f in FILES if os.path.exists(os.path.join(src, f))}
hunks, cur = [], None
for line in open(diff, encoding='utf-8').read().split('\n'):
    if line.startswith('@@'):
        cur = {'head': line, 'old': [], 'new': []}; hunks.append(cur); continue
    if cur is None or line.startswith('\\'): continue
    if line.startswith('-'): cur['old'].append(line[1:])
    elif line.startswith('+'): cur['new'].append(line[1:])
    elif line.startswith(' '): cur['old'].append(line[1:]); cur['new'].append(line[1:])
    elif line == '': pass
ok = True
for h in hunks:
    old, new = '\n'.join(h['old']), '\n'.join(h['new'])
    if 'var BUILD = ' in old or 'var LANG_AR = ' in old:
        print('skip  ', h['head'][:60]); continue
    hits = [(f, t.count(old)) for f, t in texts.items() if old in t]
    if len(hits) != 1 or hits[0][1] != 1:
        # try trimming context lines one at a time from both ends (the sources may differ around the hunk)
        print('MISS  ', h['head'][:80], hits); ok = False; continue
    f = hits[0][0]
    texts[f] = texts[f].replace(old, new)
    print('apply ', h['head'][:60], '->', f)
if not dry and ok:
    for f, t in texts.items(): open(os.path.join(src, f), 'w', encoding='utf-8').write(t)
    print('written')
elif not ok: print('not written: fix the misses first')
