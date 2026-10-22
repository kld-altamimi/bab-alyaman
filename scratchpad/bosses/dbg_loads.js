const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  const page = await (await browser.newContext({ viewport: { width: 844, height: 390 } })).newPage();
  await page.route(/posthog|fonts\.(googleapis|gstatic)/, (r) => r.abort());
  await page.goto('http://127.0.0.1:8792/index.html?internal=1');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 30000 });
  await page.mouse.click(422, 150);
  await page.evaluate(() => window.__m1.begin('taiz', 2));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  const r = await page.evaluate(() => window.__m1.sim().enemies.filter(e => e.k === 'truck').map(e => ({ id: e.id, x: Math.round(e.x), load: e.load, paint: e.paint, st: e.st })));
  console.log(JSON.stringify(r));
  await browser.close();
})();
