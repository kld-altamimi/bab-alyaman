// rt_ibb.js - Ibb's range in real time (not stepped by hand): which of the Spokesman's lines are said, and when, walking
// along it with the keyboard (Yazeed kept from harm). Logs, and a picture at each screen. Usage: node rt_ibb.js <url> <out dir>
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const OUT = process.argv[3]; fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, locale: 'en-US' });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.route(/posthog|fonts\.(googleapis|gstatic)/, (r) => r.abort());
  await page.goto(process.argv[2]);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 30000 });
  await page.mouse.click(422, 200);
  await page.evaluate(() => window.__m1.begin('ibb', 0));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  await page.evaluate(() => {
    window.__log = []; let last = null;
    setInterval(() => {
      const l = window.__m1.line(), s = window.__m1.sim();
      if (!s) return;
      s.p.plates = Math.max(s.p.plates, 2); s.p.lives = 5;
      const id = l ? l.id + ' (' + l.who + ': ' + l.text + ')' : null;
      if (id !== last) { window.__log.push(s.time.toFixed(1) + 's x' + Math.round(s.p.x) + ' ' + (id || '-')); last = id; }
    }, 50);
  });
  const down = (gs) => page.evaluate((gs) => { const s = window.__m1.sim(); s.enemies.forEach(e => { if (e.alive && e.hostile && gs.indexOf(e.g) >= 0) Sim._.killEnemy(s, e, 1, 'shot'); }); gs.forEach(g => s.groups[g].pending.length = 0); }, gs);
  const walkTo = async (x) => { await page.keyboard.down('ArrowRight'); await page.waitForFunction((x) => window.__m1.sim().p.x >= x, x, { timeout: 30000, polling: 16 }); await page.keyboard.up('ArrowRight'); };
  await page.waitForTimeout(9000);
  await page.screenshot({ path: OUT + '/r1_billboard.png' });
  // shooting at the billboard: the shots go through it, and it keeps talking
  await page.keyboard.down('KeyJ'); await page.waitForTimeout(1200); await page.keyboard.up('KeyJ');
  await down(['A', 'B']); await walkTo(965);
  await page.waitForTimeout(3000);
  await page.screenshot({ path: OUT + '/r2_set.png' });
  await page.keyboard.down('KeyJ'); await page.waitForTimeout(900); await page.keyboard.up('KeyJ');      // (at the men by the set: it takes nothing)
  await page.waitForTimeout(3000);
  await page.screenshot({ path: OUT + '/r3_set_after_fire.png' });
  const log = await page.evaluate(() => window.__log);
  console.log(log.join('\n'));
  console.log(errors.length ? 'page errors: ' + errors.join(' | ') : 'no page errors');
  await browser.close();
})();
