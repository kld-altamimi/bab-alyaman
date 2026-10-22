// snap_fps_tip.js - a picture of the 30-frames tip on a phone on its side, in English (iPhone wording) and in Arabic, on a
// narrow phone (667 x 375) as well as a wide one, to see that it fits on the screen.
const { chromium } = require('playwright');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const shots = '/home/claude/bab_out/m1_src/shots/';
const HALF = () => { const raf = window.requestAnimationFrame.bind(window); window.requestAnimationFrame = cb => raf(() => raf(cb)); };
const IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1';
(async () => {
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  for (const [w, h, lang] of [[844, 390, 'en'], [667, 375, 'en'], [667, 375, 'ar']]) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 2, hasTouch: true, isMobile: true, userAgent: IPHONE });
    await ctx.addInitScript(HALF);
    const page = await ctx.newPage();
    await page.goto('http://127.0.0.1:8766/index.html');
    await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
    await page.evaluate(() => { window.__hints = []; const f = Render.setHint; Render.setHint = function (s) { if (s) window.__hints.push(s); return f.apply(this, arguments); }; });
    if (lang === 'ar') await page.evaluate(() => window.__m1.setLang('ar'));
    await page.evaluate(() => window.__m1.begin('m1', 0));
    await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
    await page.waitForFunction(() => window.__hints.some(s => /Low Power|الطاقة/.test(s)), null, { timeout: 30000 });
    await sleep(700);
    const f = shots + 'fps_tip_' + w + '_' + lang + '.png';
    await page.screenshot({ path: f });
    console.log(f, '(width ' + (await page.evaluate(() => window.__m1.width())) + ' px of game)');
    await ctx.close();
  }
  await browser.close();
})();
