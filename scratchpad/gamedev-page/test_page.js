// Local check of the Game Development page with a stand-in db fed by seed.json: page errors, sideways overflow at
// 390 and 1200 px, answering (with a note), undo, adding an idea, and one phone screenshot.
const { chromium } = require('playwright');
const fs = require('fs');
const DIR = __dirname;
const seed = JSON.parse(fs.readFileSync(DIR + '/seed3.json', 'utf8'));

const page = fs.readFileSync(DIR + '/game-development.html', 'utf8');
fs.writeFileSync(DIR + '/test.html', '<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style></head><body>' + page + '</body></html>');

const stub = (SEED) => {
  const store = {}, listeners = {};
  for (const [c, docs] of Object.entries(SEED)) store[c] = Object.assign({}, docs);
  const snap = (c) => {
    const docs = Object.entries(store[c] || {}).map(([id, d]) => ({ id, exists: true, data: () => d, metadata: {} }));
    return { docs, size: docs.length, empty: !docs.length, docChanges: () => [], metadata: { fromCache: false, hasPendingWrites: false } };
  };
  const emit = (c) => (listeners[c] || []).forEach((f) => f(snap(c)));
  const db = {
    collection: (c) => ({ onSnapshot(next) { (listeners[c] = listeners[c] || []).push(next); setTimeout(() => next(snap(c)), 30); return () => {}; } }),
    doc: (p) => {
      const [c, id] = p.split('/');
      return {
        onSnapshot(next) { setTimeout(() => next({ id, exists: !!(store[c] || {})[id], data: () => (store[c] || {})[id], metadata: {} }), 30); return () => {}; },
        async set(d) { (store[c] = store[c] || {})[id] = d; setTimeout(() => emit(c), 20); },
        async delete() { if (store[c]) delete store[c][id]; setTimeout(() => emit(c), 20); }
      };
    }
  };
  window.claude = { use: async (n) => (n === 'db' ? db : null) };
};

(async () => {
  const browser = await chromium.launch();
  const errors = [];
  let fails = 0;
  const note = (ok, what) => { console.log((ok ? 'ok   ' : 'FAIL ') + what); if (!ok) fails++; };
  for (const width of [1200, 390]) {
    const ctx = await browser.newContext({ viewport: { width, height: 900 }, deviceScaleFactor: 2 });
    const p = await ctx.newPage();
    p.on('pageerror', (e) => errors.push(width + ': ' + e.message));
    p.on('console', (m) => { if (m.type() === 'error' && !/ERR_FAILED|fonts\.g/.test(m.text())) errors.push(width + ' console: ' + m.text()); });
    await p.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());
    await p.addInitScript(stub, seed);
    await p.goto('file://' + DIR + '/test.html');
    await p.waitForSelector('#needs .rowbtn');
    const counts = await p.evaluate(() => ({
      decide: document.querySelectorAll('#needs .rowbtn').length, pipe: document.querySelectorAll('#pipe .rowbtn').length,
      missions: document.querySelectorAll('#missions .rowbtn').length, req: document.querySelectorAll('#requests .rowbtn').length,
      done: document.querySelectorAll('#done .rowbtn').length, status: document.querySelector('#sync').textContent,
      stages: [...document.querySelectorAll('.tile b')].map((e) => e.textContent).join(',')
    }));
    note(counts.decide === 7 && counts.pipe === 7 && counts.missions === 11 && counts.req === 5 && counts.done === 0, width + ' rows: ' + JSON.stringify(counts));
    // open the Taiz sign-off, ask for changes with a note, send
    await p.click('[data-act="toggle"][data-id="taiz-signoff"]');
    await p.click('[data-act="pick"][data-id="taiz-signoff"][data-k="changes"]');
    await p.click('[data-act="save"][data-id="taiz-signoff"]');
    note(await p.isVisible('#needs .err'), width + ' an empty note is refused');
    await p.fill('#note-taiz-signoff', 'The launcher fight is too short');
    await p.click('[data-act="save"][data-id="taiz-signoff"]');
    await p.waitForSelector('#pending:not([hidden])');
    note((await p.textContent('#pending')).includes('1'), width + ' banner after an answer: ' + (await p.textContent('#pending')).trim().slice(0, 60));
    // ranks, levels and the stale chip
    const rk = await p.evaluate(() => ({ ranks: [...document.querySelectorAll('#needs .rank')].map((e) => e.textContent).join(','), lv: document.querySelectorAll('#needs .lv').length, stale: [...document.querySelectorAll('#needs .st')].filter((e) => e.textContent === 'Stale').length }));
    note(rk.ranks === '1,2,3,4,5,6,7' && rk.lv === 7 && rk.stale === 1, width + ' ranked 1 to 7 with levels; stale chips: ' + rk.stale);
    await p.click('#done-tog');
    note((await p.evaluate(() => document.querySelectorAll('#done .rowbtn').length)) > 0, width + ' Done opens');
    // an idea: approve
    await p.click('[data-act="toggle"][data-id="gun-continue"]');
    await p.click('[data-act="pick"][data-id="gun-continue"][data-k="approve"]');
    await p.waitForFunction(() => document.querySelector('#pending b') && document.querySelector('#pending b').textContent === '2');
    note(true, width + ' second answer counted');
    // undo the first
    await p.click('[data-act="undo"][data-id="taiz-signoff"]');
    await p.waitForFunction(() => document.querySelector('#pending b') && document.querySelector('#pending b').textContent === '1');
    note(await p.isVisible('[data-act="pick"][data-id="taiz-signoff"][data-k="push"]'), width + ' undo brings the buttons back');
    // add an idea
    await p.fill('#ideaText', 'A sandstorm level where the drones lose sight of you');
    await p.click('#addBtn');
    await p.waitForFunction(() => [...document.querySelectorAll('#pipe .ctx')].some((e) => e.textContent.startsWith('Your idea')));
    note(true, width + ' new idea shows under Ideas');
    // open a mission and a request row
    await p.click('[data-act="toggle"][data-id="mission-taiz"]');
    await p.click('[data-act="toggle"][data-id="req-game-development-R1"]');
    const over = await p.evaluate(() => ({ sw: document.documentElement.scrollWidth, iw: window.innerWidth }));
    note(over.sw <= over.iw, width + ' no sideways scroll (' + over.sw + ' <= ' + over.iw + ')');
    if (width === 390) {
      await p.evaluate(() => window.scrollTo(0, 0));
      await p.screenshot({ path: DIR + '/shot_390.png', fullPage: true });
    }
    await ctx.close();
  }
  note(errors.length === 0, 'no page errors' + (errors.length ? ': ' + errors.join(' | ') : ''));
  await browser.close();
  console.log(fails ? fails + ' PROBLEM(S)' : 'ALL GOOD');
  process.exit(fails ? 1 : 0);
})();
