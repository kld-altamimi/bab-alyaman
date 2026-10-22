// test_map.js - the Taiz map page with a stand-in store: no page errors, no sideways page scroll, the tiles load, drag
// and zoom move the map, a marker opens its details, a comment is added at a tapped spot and undone; pictures at 390 and
// 1200 px. Usage: node test_map.js   (serves this folder itself)
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const DIR = __dirname;
const page0 = fs.readFileSync(DIR + '/taiz-map.html', 'utf8');
fs.writeFileSync(DIR + '/test.html', '<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style></head><body>' + page0 + '</body></html>');
const srv = http.createServer((q, r) => {
  const p = path.join(DIR, decodeURIComponent(q.url.split('?')[0]));
  if (!p.startsWith(DIR) || !fs.existsSync(p)) { r.writeHead(404); r.end(); return; }
  r.writeHead(200, { 'content-type': p.endsWith('.webp') ? 'image/webp' : 'text/html' }); r.end(fs.readFileSync(p));
}).listen(8783, '127.0.0.1');
const stub = () => {
  const store = {}, ls = [];
  const snap = () => ({ docs: Object.entries(store).map(([id, d]) => ({ id, exists: true, data: () => d })) });
  const emit = () => ls.forEach((f) => f(snap()));
  const db = {
    collection: () => ({ onSnapshot(n) { ls.push(n); setTimeout(() => n(snap()), 20); return () => {}; } }),
    doc: (p) => { const id = p.split('/')[1]; return { async set(d) { store[id] = d; setTimeout(emit, 10); }, async delete() { delete store[id]; setTimeout(emit, 10); } }; }
  };
  window.claude = { use: async (n) => (n === 'db' ? db : null) };
};
let fails = 0;
const note = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) fails++; };
(async () => {
  const browser = await chromium.launch();
  const errors = [];
  for (const [w, h, touch] of [[1200, 900, false], [390, 844, true]]) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2, hasTouch: touch, isMobile: touch });
    const p = await ctx.newPage();
    p.on('pageerror', (e) => errors.push(w + ': ' + e.message));
    await p.route(/fonts\.(googleapis|gstatic)/, (r) => r.abort());
    await p.addInitScript(stub);
    await p.goto('http://127.0.0.1:8783/test.html');
    await p.waitForFunction(() => [...document.querySelectorAll('#world img')].every((i) => i.complete && i.naturalWidth > 0), null, { timeout: 15000 });
    await p.waitForTimeout(300);
    const t0 = await p.evaluate(() => document.getElementById('world').style.transform);
    await p.evaluate(() => document.getElementById('vp').scrollIntoView({ block: 'center' }));
    await p.waitForTimeout(150);
    const box = await p.locator('#vp').boundingBox();
    await p.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
    await p.mouse.down(); await p.mouse.move(box.x + box.width / 2 - 200, box.y + box.height / 2, { steps: 6 }); await p.mouse.up();
    await p.waitForTimeout(100);
    const t1 = await p.evaluate(() => document.getElementById('world').style.transform);
    note(t0 !== t1, w + ' drag moves the map');
    await p.click('#z-in'); await p.waitForTimeout(100);
    const t2 = await p.evaluate(() => document.getElementById('world').style.transform);
    note(t2 !== t1 && /scale\(/.test(t2), w + ' zoom in: ' + t2.slice(-14));
    // open the first visible fight marker
    await p.evaluate(() => document.getElementById('vp').scrollIntoView({ block: 'center' }));
    await p.waitForTimeout(150);
    const pt = await p.evaluate(() => {
      const v = document.getElementById('vp').getBoundingClientRect();
      for (const el of document.querySelectorAll('.mk.fight, .mk.en, .mk.zone')) {
        const r = el.firstChild.getBoundingClientRect(), cx = r.left + r.width / 2, cy = r.top + r.height / 2;
        if (el.style.visibility !== 'hidden' && !el.hidden && cx > v.left + 10 && cx < v.right - 10 && cy > v.top + 10 && cy < v.bottom - 10 && cy > 10 && cy < window.innerHeight - 10) return [cx, cy];
      }
      return null;
    });
    if (pt) { await p.mouse.click(pt[0], pt[1]); note(await p.isVisible('#pop'), w + ' a marker opens: ' + (await p.textContent('#pop')).slice(0, 60)); await p.click('[data-pop="close"]'); }
    else note(false, w + ' no marker inside the map view');
    // add a comment at the middle of the map
    await p.click('#addBtn');
    await p.evaluate(() => document.getElementById('vp').scrollIntoView({ block: 'center' }));
    await p.waitForTimeout(150);
    const box2 = await p.locator('#vp').boundingBox();
    await p.mouse.click(box2.x + box2.width / 2, box2.y + box2.height / 2);
    note(await p.isVisible('#editor'), w + ' tapping the map opens the comment box: ' + (await p.textContent('#edWhere')));
    await p.fill('#edText', 'Test comment: this tower should be background');
    await p.click('#edSave');
    await p.waitForSelector('.mk.pin:not(.draft)', { state: 'attached' });
    note((await p.textContent('#pending')).includes('1'), w + ' saved; banner: ' + (await p.textContent('#pending')).trim().slice(0, 50));
    if (w === 390) { await p.evaluate(() => window.scrollTo(0, 0)); await p.screenshot({ path: DIR + '/shot_390.png', fullPage: true }); }
    else await p.screenshot({ path: DIR + '/shot_1200.png' });
    await p.click('[data-nt="toggle"]'); await p.click('[data-nt="undo"]');
    await p.waitForFunction(() => !document.querySelector('.mk.pin'));
    note(true, w + ' undo removes it');
    const ov = await p.evaluate(() => ({ sw: document.documentElement.scrollWidth, iw: window.innerWidth }));
    note(ov.sw <= ov.iw, w + ' no sideways page scroll (' + ov.sw + ' <= ' + ov.iw + ')');
    await ctx.close();
  }
  note(errors.length === 0, 'no page errors' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await browser.close(); srv.close();
  console.log(fails ? fails + ' PROBLEM(S)' : 'ALL GOOD');
  process.exit(fails ? 1 : 0);
})();
