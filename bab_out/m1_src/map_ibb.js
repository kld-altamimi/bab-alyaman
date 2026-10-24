// map_ibb.js - the test build's campaign map: Ibb out, the road from Taiz to it, its card with Skip ahead.
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true, locale: process.argv[4] || 'en-US' });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.route(/posthog|fonts\.(googleapis|gstatic)/, (r) => r.abort());
  await page.goto(process.argv[2]);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 30000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate(() => window.__m1.toMap('ibb'));
  await page.waitForTimeout(2500);
  const card = await page.evaluate(() => { const c = document.querySelector('#card') || document.querySelector('.card'); return c ? c.innerText : document.body.innerText.slice(0, 600); });
  await page.screenshot({ path: process.argv[3] });
  console.log(card.replace(/\n+/g, ' | '));
  console.log(errors.length ? 'page errors: ' + errors.join(' | ') : 'no page errors');
  await browser.close();
})();
