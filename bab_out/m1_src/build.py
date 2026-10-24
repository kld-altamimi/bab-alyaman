# build.py - put code, data and pictures into one page, and write a wrapped copy for testing here.
import base64, json, os, struct, sys, time

GAME = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/'
HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
SITE = '/home/claude/bab_out/m1/'
# the version: 0.R.B. R = published release, +1 on every push to main; B = internal build, +1 on every preview build
# (--bump), never reset. Both live in version.json beside this file; --release bumps R. (--build X still forces a stamp.)
VER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'version.json')
_ver = json.load(open(VER_FILE))
if '--bump' in sys.argv:
    _ver['build'] += 1
if '--release' in sys.argv:
    _ver['release'] += 1
if '--bump' in sys.argv or '--release' in sys.argv:
    json.dump(_ver, open(VER_FILE, 'w'))
VERSION = '0.%d.%d' % (_ver['release'], _ver['build'])
BUILD = sys.argv[sys.argv.index('--build') + 1] if '--build' in sys.argv else VERSION


def js(obj):
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=False).replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')


def read(p):
    return open(p, encoding='utf-8').read()


atlas = json.load(open(GAME + 'gen/atlas.json'))
fonts = json.load(open(GAME + 'gen/fonts.json'))
audio = json.load(open(GAME + 'gen/audio.json'))
ground = json.load(open(GAME + 'gen/ground.json'))
# every mission's stage: its pictures, where they go, and its ground (the Strait's from export_art.py, the others from
# their own export scripts: gen/stage_<art>.json)
atlas['stages'] = {'strait': dict(layers=atlas['layers'], world=atlas['world'], fixed=atlas['fixed'])}
grounds = {'m1': ground}
# --no-souq (21 Oct; Khaled chose to release "All but the Souq"): the same game without the Souq. Its level, its boss's
# code, its stage pictures and its two music files are left out, and its card on the map is the live game's (coming soon,
# with the old teaser), so a player sees no change there. The atlas and the effects and voices strips keep the Souq's frames
# and clips, unused (laying them out again would move everything else in them).
NO_SOUQ = '--no-souq' in sys.argv
SOUQ_CODE = ('level_zabid', 'tailor', 'render_tailor')
# --ibb (24 Oct): a test build with Ibb in it (Mission 4, while it is being built: its plan's stages one at a time). Its
# level, its screens' code and its sheet go in, its lines (audio/speech_ibb.mp3) are listed, and on the map it is out,
# with the road from Taiz to it (the Souq off the road, as at Ibb's release). Without it, none of Ibb is in the page.
# Its painted zones come as a stage of their own (gen/stage_ibb.json, tools/export_ibb.py; 24 Oct: zone by zone).
IBB = '--ibb' in sys.argv
IBB_CODE = ('level_ibb', 'render_ibb')
pics = ['atlas', 'font', 'sky', 'far', 'sea', 'play_a', 'road', 'r2b', 'sand', 'b2r', 'play_b', 'fore', 'fore_road', 'fore_sand', 'fore_b', 'map']
for art, mission in (('mocha', 'mocha'), ('zabid', 'zabid'), ('ibb', 'ibb')):
    f = GAME + 'gen/stage_%s.json' % art
    if not os.path.exists(f) or (NO_SOUQ and art == 'zabid') or (not IBB and art == 'ibb'):
        continue
    st = json.load(open(f))
    atlas['stages'][art] = dict(layers=st['layers'], world=st['world'], fixed=st['fixed'])
    grounds[mission] = st['ground']
    pics += st['pictures']

# Taiz (21 Oct): the Apache, its rotors and the Zanabeel's guns are a sheet of their own (tools/taiz_sprites.py), kept out of
# the main atlas so nothing already in it moves
TAIZ_SHEET = GAME + 'gen/taiz_sprites.json'
if os.path.exists(TAIZ_SHEET) and os.path.exists(GAME + 'art/out/taiz.png'):
    atlas['taiz'] = json.load(open(TAIZ_SHEET))
    pics.append('taiz')
IBB_SHEET = GAME + 'gen/ibb_sprites.json'
if IBB:
    atlas['ibb'] = json.load(open(IBB_SHEET))
    pics.append('ibb')
# Taiz's painted stage (21 Oct, the full level: tools/export_taiz.py): its pieces on one sheet, and where everything is
TAIZ_STAGE = GAME + 'gen/stage_taiz.json'
stage_taiz = None
if os.path.exists(TAIZ_STAGE) and os.path.exists(GAME + 'art/out/taiz_stage.png'):
    stage_taiz = json.load(open(TAIZ_STAGE))
    pics.append('taiz_stage')

# The pictures go into the page as lossless WebP (0.8.47; Khaled, 20 Oct, the lighter first load): the same pixels in 43% of
# the bytes. Each is checked to decode to exactly its PNG's pixels (every visible pixel, and the alpha everywhere; the
# colour under a fully clear pixel is not kept, and nothing draws it) and kept in art/webp/ under its PNG's hash, because
# encoding at the best effort takes a while. --png builds the page with the PNGs as before.
import hashlib, io
import numpy as np
from PIL import Image
WEBP = GAME + 'art/webp/'
os.makedirs(WEBP, exist_ok=True)


def webp(n, raw):
    p = WEBP + '%s.%s.webp' % (n, hashlib.sha1(raw).hexdigest()[:12])
    if not os.path.exists(p):
        im = Image.open(io.BytesIO(raw)).convert('RGBA')
        buf = io.BytesIO()
        im.save(buf, 'WEBP', lossless=True, quality=100, method=6, exact=False)
        a, b = np.asarray(im), np.asarray(Image.open(io.BytesIO(buf.getvalue())).convert('RGBA'))
        seen = a[..., 3] > 0
        assert np.array_equal(a[..., 3], b[..., 3]) and np.array_equal(a[seen], b[seen]), 'WebP changed the pixels of ' + n
        open(p, 'wb').write(buf.getvalue())
    return open(p, 'rb').read()


images = {}
total_png = total_pic = 0
for n in pics:
    raw = open(GAME + 'art/out/%s.png' % n, 'rb').read()
    total_png += len(raw)
    if '--png' in sys.argv:
        pic, kind = raw, 'png'
    else:
        pic, kind = webp(n, raw), 'webp'
    total_pic += len(pic)
    images[n] = 'data:image/%s;base64,' % kind + base64.b64encode(pic).decode()
# the page only needs the lines the game can speak
audio_small = dict(audio)
if not IBB:
    audio_small.pop('speech', None)
    audio_small['music'] = {k: v for k, v in audio['music'].items() if k not in ('ibb', 'ibbboss')}      # (Ibb's music: test builds only)
if NO_SOUQ:
    audio_small['music'] = {k: v for k, v in audio_small['music'].items() if k not in ('souq', 'tailor')}

# a quarter-second of silence, for the iPhone ring-switch workaround
n, sr = 2000, 8000
wav = b'RIFF' + struct.pack('<I', 36 + n) + b'WAVEfmt ' + struct.pack('<IHHIIHH', 16, 1, 1, sr, sr, 1, 8) + b'data' + struct.pack('<I', n) + b'\x80' * n
silence = 'data:audio/wav;base64,' + base64.b64encode(wav).decode()

lang_ar = json.load(open(GAME + 'src/lang_ar.json'))
data = '\n'.join([
    'var BUILD = %s;' % js(BUILD),
    '// the Radio meter: hidden until spending it is built (it still fills underneath; Khaled, 19 Oct)',
    'var RADIO_ON = false;',
    read(GAME + 'src/badges.js'),            # (the Ace and Liberator badges, drawn in pixels: the other chat's, 0.7.42, kept where it put them)
    'var LANG_AR = %s;' % js(lang_ar),
    'var ATLAS = %s;' % js(atlas),
    'var FONTS = %s;' % js(fonts),
    'var AUDIO = %s;' % js(audio_small),
    'var GROUND = %s;' % js(ground),
    'var GROUNDS = %s;' % js(grounds),
    'var STAGE_TAIZ = %s;' % js(stage_taiz),
    'var IMAGES = %s;' % js(images),
])
code = []
for f in ('lang', 'level', 'level_mocha', 'level_zabid', 'level_taiz', 'level_ibb', 'campaign', 'sim', 'drive', 'boss', 'roaster', 'tailor', 'fly', 'render', 'render_roaster', 'render_tailor', 'render_fly', 'render_ibb', 'menu', 'audio', 'input', 'main'):
    if not os.path.exists(GAME + 'src/%s.js' % f) or (NO_SOUQ and f in SOUQ_CODE) or (not IBB and f in IBB_CODE):
        continue
    src = read(GAME + 'src/%s.js' % f)
    if IBB and f == 'campaign':
        # Ibb out, and the road from Taiz going to it
        for old, new in (("name: 'The Green Valleys', place: 'Ibb', road: 'Mountain road', built: false,", "name: 'The Green Valleys', place: 'Ibb', road: 'Mountain road', built: true,"),
                         ("name: 'The Castle', place: 'Taiz', road: 'Mountain road', built: true, next: ['zabid'],", "name: 'The Castle', place: 'Taiz', road: 'Mountain road', built: true, next: ['ibb'],")):
            assert src.count(old) == 1, old
            src = src.replace(old, new)
    if NO_SOUQ and f == 'campaign':
        # the Souq's card as the live game shows it (0.8.44): not built, and the teaser it has always had
        for old, new in (("name: 'The Souq', place: 'Zabid', road: 'Coast road', built: true,", "name: 'The Souq', place: 'Zabid', road: 'Coast road', built: false,"),
                         ("boss: 'The Tailor: the Zanabeel\\'s tailor, hiding among his own dummies, every one of them dressed exactly like him. Only one of them sneezes.' },",
                          "boss: 'The Spice Cannon. It fires chilli. Keep your mouth shut.' },")):
            assert src.count(old) == 1, old
            src = src.replace(old, new)
    if f == 'audio':
        assert src.count("'/*SILENCE*/'") == 1
        src = src.replace("'/*SILENCE*/'", js(silence))
    assert '</script' not in src.lower(), f
    code.append('// ---------------------------------------------------------------- %s.js\n' % f + src)
tpl = read(HERE + 'page.tpl.html')
assert tpl.count('/*__DATA__*/') == 1 and tpl.count('/*__CODE__*/') == 1
page = tpl.replace('/*__DATA__*/', data).replace('/*__CODE__*/', '\n'.join(code))
os.makedirs(SITE, exist_ok=True)
open(SITE + 'page.html', 'w', encoding='utf-8').write(page)

# what the viewer wraps around the page, near enough, so the copy tested here behaves like the published one
LOCAL = '''<style>
:root{--f-head:'DejaVu Sans',sans-serif !important;--f-body:'Inter','DejaVu Sans',sans-serif !important}
h1,h2,.eyebrow,.label,.btn,.seg button,.tb,#cap,.tally,.facts,.rep summary,.boot,.from select,.meter output{font-stretch:condensed !important;letter-spacing:0 !important}
html[lang="ar"]{--f-head:'Noto Kufi Arabic','DejaVu Sans',sans-serif !important;--f-body:'Noto Kufi Arabic','DejaVu Sans',sans-serif !important}
</style>'''
SKELETON = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>:root{color-scheme:light;padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
'''
wrapped = SKELETON + page + ('\n' + LOCAL if '--local-fonts' in sys.argv else '') + '\n</body>\n</html>\n'
open(SITE + 'index.html', 'w', encoding='utf-8').write(wrapped)
aud = sum(os.path.getsize(SITE + 'audio/' + f) for f in os.listdir(SITE + 'audio'))
print('build "%s"%s%s: page %.0f KB (pictures %.0f KB as %s, %.0f KB as PNG, before base64), sound files %.2f MB; title in first 8 KB: %s'
      % (BUILD, ' WITHOUT THE SOUQ' if NO_SOUQ else '', ' WITH IBB' if IBB else '', len(page.encode()) / 1024, total_pic / 1024, 'PNG' if '--png' in sys.argv else 'WebP', total_png / 1024, aud / 1048576, '<title>' in page[:8000]))
if NO_SOUQ:
    # the music the page can ask for (the folder keeps every file; copy only these to the repo)
    print('music files this page uses:', sorted(set(v['file'] for v in audio_small['music'].values())))
