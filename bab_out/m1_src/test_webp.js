// test_webp.js - the pictures in the page are WebP now (0.8.47): in a real browser every one of them opens, and drawn on
// a canvas each comes out exactly as its PNG does (the PNGs are fed to the page from disk); and the page has no PNG left.
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = '/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad/game/art/out/';
let fails = 0;
const note = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) fails++; };
(async () => {
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  const page = await (await browser.newContext({ viewport: { width: 844, height: 390 } })).newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.route('**/png/*.png', route => {
    const n = decodeURIComponent(route.request().url().split('/').pop());
    route.fulfill({ status: 200, contentType: 'image/png', body: fs.readFileSync(OUT + n) });
  });
  await page.goto('http://127.0.0.1:8766/index.html');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
  const kinds = await page.evaluate(() => { const k = {}; for (const n in IMAGES) { const m = /^data:image\/(\w+);/.exec(IMAGES[n]); k[m[1]] = (k[m[1]] || 0) + 1; } return k; });
  note(!kinds.png && kinds.webp >= 26, 'every picture in the page is WebP: ' + JSON.stringify(kinds));        // (26 without the Souq's stage, 27 with Taiz's sheet, 31+ with the Souq)
  const res = await page.evaluate(async () => {
    const load = src => new Promise((ok, no) => { const im = new Image(); im.onload = () => ok(im); im.onerror = () => no(new Error('did not open: ' + src.slice(0, 40))); im.src = src; });
    const pix = im => { const c = document.createElement('canvas'); c.width = im.naturalWidth; c.height = im.naturalHeight; const x = c.getContext('2d'); x.drawImage(im, 0, 0); return x.getImageData(0, 0, c.width, c.height).data; };
    // Opaque and clear pixels must come out the same to the bit. A see-through pixel (a shadow, a glow) is kept by the canvas
    // multiplied by its alpha, and the browser's WebP and PNG decoders round that product differently (by one step of 255:
    // read back and divided out again it can look like more); so those are compared as the canvas holds them.
    const out = [];
    for (const n of Object.keys(IMAGES)) {
      const a = await load(IMAGES[n]), b = await load('png/' + n + '.png');
      const pa = pix(a), pb = pix(b);
      let hard = 0, soft = 0, worst = 0;
      if (pa.length !== pb.length) hard = -1;
      else for (let i = 0; i < pa.length; i += 4) {
        const al = pb[i + 3];
        if (pa[i + 3] !== al) { hard++; continue; }
        for (let k = 0; k < 3; k++) {
          if (pa[i + k] === pb[i + k]) continue;
          if (al === 255 || al === 0) { hard++; break; }
          // multiplied back by the alpha (as the canvas held them), the two may differ by one step and no more
          const d = Math.abs(Math.round(pa[i + k] * al / 255) - Math.round(pb[i + k] * al / 255));
          worst = Math.max(worst, d);
          if (d > 1) { hard++; break; }
          soft++; break;
        }
      }
      out.push([n, a.naturalWidth + 'x' + a.naturalHeight, hard, soft, +worst.toFixed(2)]);
    }
    // the HUD portrait is read back pixel by pixel (lifeHead in render.js finds its red card by exact colour)
    const f = ATLAS.frames.hud_portrait, crop = (im) => { const c = document.createElement('canvas'); c.width = f[2]; c.height = f[3]; const x = c.getContext('2d'); x.drawImage(im, f[0], f[1], f[2], f[3], 0, 0, f[2], f[3]); return x.getImageData(0, 0, f[2], f[3]).data; };
    const ha = crop(await load(IMAGES.atlas)), hb = crop(await load('png/atlas.png'));
    let hd = 0; for (let i = 0; i < ha.length; i++) if (ha[i] !== hb[i]) hd++;
    return { out, hd };
  });
  const bad = res.out.filter(r => r[2] !== 0), soft = res.out.filter(r => r[3]);
  note(res.out.length >= 26 && !bad.length, res.out.length + ' pictures drawn from WebP and from PNG: ' + (bad.length ? 'DIFFERENT: ' + JSON.stringify(bad) :
    'every opaque and clear pixel the same; see-through pixels within the canvas\'s rounding' + (soft.length ? ' (' + soft.map(r => r[0] + ': ' + r[3] + ' pixels, at most ' + r[4] + ' of 255').join('; ') + ')' : '')));
  note(res.hd === 0, 'the HUD portrait, which the game reads back by exact colour, is the same to the bit (' + res.hd + ' bytes differ)');
  note(errors.length === 0, 'no errors on the page' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await browser.close();
  console.log(fails ? '\n' + fails + ' PROBLEM(S)' : '\nALL GOOD');
  process.exit(fails ? 1 : 0);
})();
