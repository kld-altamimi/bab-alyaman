# build_standalone.py - the same build as a folder any web host can serve: index.html plus the audio folder, zipped.
import os, shutil, zipfile
SITE = '/home/claude/bab_out/m1/'
OUT = '/home/claude/bab_out/m1_standalone/'
ZIP = '/home/claude/bab_out/strait-feel-prototype-latest.zip'
page = open(SITE + 'page.html', encoding='utf-8').read()
cut = page.index('<div id="app">')
head_part, body_part = page[:cut], page[cut:]
assert '<title>' in head_part and '</style>' in head_part and '<script>' in body_part
doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
       '<meta name="theme-color" content="#090b16">\n'
       '<meta name="mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-capable" content="yes">\n'
       '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
       '<style>:root{color-scheme:dark;padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>\n'
       + head_part + '</head>\n<body>\n' + body_part + '</body>\n</html>\n')
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT + 'audio')
open(OUT + 'index.html', 'w', encoding='utf-8').write(doc)
for f in sorted(os.listdir(SITE + 'audio')):
    shutil.copy(SITE + 'audio/' + f, OUT + 'audio/' + f)
with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write(OUT + 'index.html', 'index.html')
    for f in sorted(os.listdir(OUT + 'audio')):
        z.write(OUT + 'audio/' + f, 'audio/' + f, compress_type=zipfile.ZIP_STORED)
names = zipfile.ZipFile(ZIP).namelist()
print('zip %.2f MB:' % (os.path.getsize(ZIP) / 1048576), names)
