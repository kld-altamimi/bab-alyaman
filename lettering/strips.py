"""Lettering in the game's own hand: each string drawn by the game's text renderer (its pixel Kufi for Arabic) at the
game's pixel size, saved as a transparent strip; edits and layouts scale strips up by whole pixels.
Usage: strips.py <strings.json> [outdir]      (outdir default: mk.TEXT)
  strings.json: {"name": ["font", "text"], …}. Fonts the posts use: m_org (a speaker's name, orange), m_lav (a subtitle
  line), b_org / b_red (big titles: «المهمة 4: إب», «متاحة الآن»), s_lav (small). Other fonts: see Render.text in the game.
Also importable: strips.render({name: [font, text]}, outdir) returns the merged meta.
Writes <name>.png and merges {name: {x0, y0, w, h, cut}} into meta.json ("_gap": the width of the game's gap between a
line and its speaker's name). A strip marked cut ran off the game's canvas: split the string."""
import json, os, sys, base64
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'rig'))
import common, mk
from playwright.sync_api import sync_playwright
PORT = int(os.environ.get('PORT', '8797'))

def render(strings, out=None, port=PORT, quiet=False):
    out = os.path.abspath(out or mk.TEXT); os.makedirs(out, exist_ok=True)
    srv = common.serve(port)
    meta = json.load(open(f'{out}/meta.json')) if os.path.exists(f'{out}/meta.json') else {}
    with sync_playwright() as p:
        bw = p.chromium.launch()
        ctx = bw.new_context(locale='ar-SA', viewport={'width': 2160, 'height': 1000})
        css = "@font-face{font-family:'Noto Kufi Arabic';src:url(http://127.0.0.1:%d/__kufi.ttf) format('truetype');font-weight:100 900;}" % port
        ctx.route('**/*posthog*', lambda r: r.abort())
        ctx.route('**/fonts.googleapis.com/**', lambda r: r.fulfill(status=200, content_type='text/css', body=css))
        ctx.route('**/__kufi.ttf', lambda r: r.fulfill(status=200, content_type='font/ttf', body=common.KUFI))
        pg = ctx.new_page()
        pg.goto(f'http://127.0.0.1:{port}/index.html?internal=1')
        pg.wait_for_function("window.__m1 && window.__m1.state && window.__m1.state()==='home'", timeout=60000)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(1500)
        for name, (font, s) in strings.items():
            r = pg.evaluate("""([font, s]) => {
              // the world's canvas is opaque: draw the string over black and over white, and take its alpha from the difference
              const c = Render.ctx(), W = Render.width(), H = Render.height();
              const shot = (bg) => { c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1; c.globalCompositeOperation = 'source-over'; c.fillStyle = bg; c.fillRect(0, 0, W, H); Render.text(font, s, 4, 40); const d = c.getImageData(0, 0, W, H).data; c.restore(); return d; };
              const B = shot('#000'), Wt = shot('#fff');
              const o = document.createElement('canvas'); o.width = W; o.height = H;
              const oc = o.getContext('2d'), im = oc.createImageData(W, H), q = im.data;
              let x0 = W, y0 = H, x1 = -1, y1 = -1;
              for (let i = 0; i < W * H; i++) {
                const k = i * 4, a = 255 - (Wt[k] - B[k]);
                if (a <= 0) continue;
                q[k] = Math.min(255, Math.round(B[k] * 255 / a)); q[k + 1] = Math.min(255, Math.round(B[k + 1] * 255 / a)); q[k + 2] = Math.min(255, Math.round(B[k + 2] * 255 / a)); q[k + 3] = a;
                const x = i % W, y = (i / W) | 0;
                if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y;
              }
              oc.putImageData(im, 0, 0);
              const o2 = document.createElement('canvas'); o2.width = x1 - x0 + 1; o2.height = y1 - y0 + 1;
              o2.getContext('2d').drawImage(o, x0, y0, o2.width, o2.height, 0, 0, o2.width, o2.height);
              return { url: o2.toDataURL('image/png'), x0, y0, w: o2.width, h: o2.height, cut: x1 >= W - 2 };
            }""", [font, s])
            open(f'{out}/{name}.png', 'wb').write(base64.b64decode(r['url'].split(',', 1)[1]))
            meta[name] = {k: r[k] for k in ('x0', 'y0', 'w', 'h', 'cut')}
            meta[name]['font'] = font; meta[name]['text'] = s
            if not quiet: print(name, font, r['w'], 'x', r['h'], 'CUT!' if r['cut'] else '')
        meta['_gap'] = pg.evaluate("(function(){ try { return Render.textW('m_org', '  '); } catch (e) { return 7; } })()") or 7
        json.dump(meta, open(f'{out}/meta.json', 'w'), ensure_ascii=False, indent=1)
        bw.close()
    srv.shutdown(); srv.server_close()
    return meta

if __name__ == '__main__':
    render(json.load(open(sys.argv[1])), sys.argv[2] if len(sys.argv) > 2 else None)
