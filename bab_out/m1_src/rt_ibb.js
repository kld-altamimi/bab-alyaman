// rt_ibb.js - Ibb's range in real time (not stepped by hand): which lines are said, and when, walking along it with
// the keyboard; the hint; a speaker taken over (its announcer and the rifleman's answer). Logs, no pictures.
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 600 }, locale: 'en-US' });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.route(/posthog|fonts\.(googleapis|gstatic)/, (r) => r.abort());
  await page.goto(process.argv[2]);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 30000 });
  await page.mouse.click(640, 300);
  await page.evaluate(() => window.__m1.begin('ibb', 0));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.evaluate(() => {
    window.__log = [];
    let last = null, lastHint = null;
    setInterval(() => {
      const l = window.__m1.line(), s = window.__m1.sim();
      if (!s) return;
      s.p.inv = Math.max(s.p.inv, 5); s.p.lives = 5;
      const id = l ? l.id + ' (' + l.who + ': ' + l.text + ')' : null;
      if (id !== last) { window.__log.push((s.time).toFixed(1) + 's x' + Math.round(s.p.x) + ' ' + (id || '-')); last = id; }
    }, 50);
  });
  const hold = async (key, ms) => { await page.keyboard.down(key); await page.waitForTimeout(ms); await page.keyboard.up(key); };
  await page.waitForTimeout(9000);                    // the billboard
  await hold('ArrowRight', 2500);                     // up to the first speaker
  await page.waitForTimeout(3000);
  const hint = await page.evaluate(() => { const h = document.querySelector('#hint'); return window.__m1.sim().ibb.hinted; });
  await hold('ArrowRight', 1600);                     // into the pole
  await page.waitForTimeout(7000);
  const st = await page.evaluate(() => { const s = window.__m1.sim(); return { spk: s.ibb.spk.map(o => o.st), men: s.enemies.filter(e => e.g === 'A').map(e => e.st), counts: Sound.counts ? Object.keys(Sound.counts()).filter(k => /^sp_|grunt_already|ann_complete/.test(k)) : null, info: Sound.info() }; });
  const log = await page.evaluate(() => window.__log);
  console.log(log.join('\n'));
  console.log('hinted', hint, JSON.stringify(st));
  console.log(errors.length ? 'page errors: ' + errors.join(' | ') : 'no page errors');
  await browser.close();
})();
