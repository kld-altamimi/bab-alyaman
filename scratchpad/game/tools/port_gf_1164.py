#!/usr/bin/env python3
"""Port game-features' 0.11.64 (main 50bb6cc) into this chat's sources (game-features-R2, 22 Oct): the results' like /
dislike + "Tell us on X" row, the continue screen's one big Continue, the `menu_step` calls, and their 6 Arabic lines.
Reads their hunks from the diff of index.html (9005608 -> 50bb6cc) and applies each one where its old text occurs exactly
once: main.js (the shell) or page.tpl.html (styles and markup). BUILD and LANG_AR hunks are skipped: the build stamps
BUILD, and the Arabic goes into lang_ar.json by key.
Usage: port_0864.py <diff> <src dir> <page.tpl.html> [--dry]"""
import json
import re
import sys

diff_path, src_dir, tpl_path = sys.argv[1], sys.argv[2].rstrip('/') + '/', sys.argv[3]
dry = '--dry' in sys.argv

hunks, cur = [], None
for line in open(diff_path, encoding='utf-8').read().split('\n'):
    if line.startswith('@@'):
        cur = {'head': line, 'old': [], 'new': []}
        hunks.append(cur)
    elif cur is not None and line[:1] in (' ', '-', '+') and not line.startswith(('---', '+++')):
        tag, body = line[0], line[1:]
        if tag in (' ', '-'):
            cur['old'].append(body)
        if tag in (' ', '+'):
            cur['new'].append(body)

targets = {'main.js': src_dir + 'main.js', 'page.tpl.html': tpl_path}
texts = {k: open(p, encoding='utf-8').read() for k, p in targets.items()}
done = 0
for h in hunks:
    old, new = '\n'.join(h['old']), '\n'.join(h['new'])
    if 'var BUILD = ' in old or 'var LANG_AR = ' in old:
        print('skip (build stamp / Arabic):', h['head'][:60])
        continue
    hits = [k for k in texts if texts[k].count(old) == 1]
    many = [k for k in texts if texts[k].count(old) > 1]
    if len(hits) != 1 or many:
        sys.exit('no single home for hunk %s: once in %s, more than once in %s\n%s' % (h['head'], hits, many, old[:300]))
    texts[hits[0]] = texts[hits[0]].replace(old, new)
    done += 1
    print('ok', hits[0], h['head'][:60])

# the Arabic: the 6 keys 0.11.64 added
added = {'Like this mission?': 'أعجبتك المهمة؟', 'Thanks!': 'شكرًا!', 'Tell us on X': 'شاركنا رأيك على X',
         'I liked it': 'أعجبتني', "I didn't like it": 'لم تعجبني', 'Feedback on {0}: ': 'ملاحظاتي على {0}: '}
ar_path = src_dir + 'lang_ar.json'
ar = json.load(open(ar_path, encoding='utf-8'))
clash = {k: ar[k] for k in added if k in ar and ar[k] != added[k]}
if clash:
    sys.exit('lang_ar.json already has different Arabic for: %r' % clash)
ar.update(added)
print('hunks applied:', done, '| lang_ar.json lines:', len(ar))
if dry:
    print('(dry run: nothing written)')
    sys.exit(0)
for k, p in targets.items():
    open(p, 'w', encoding='utf-8').write(texts[k])
json.dump(ar, open(ar_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('written')
