// make_share.js - the link-preview picture (share.png, 1200x630): the title screen as it is now, in both languages:
// «باب اليمن» with BAB AL-YEMEN under it, the tagline in Arabic and then in English. No version number, no prompt.
const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.argv[2] || '/home/claude/bab_out/m1_src/shots/share_new.png';
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1, locale: 'ar' });
  const page = await ctx.newPage();
  await page.goto('http://127.0.0.1:8766/index.html');
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => {
    const oText = Render.text, tag = T('Yazeed and Salem against the Dhanabs');
    const prompts = ['TAP TO START', 'PRESS START', 'PRESS ANY KEY'].map(k => T(k));
    Render.text = function (font, str, x, y, align) {
      if (/^V\d/.test(str) || prompts.indexOf(str) >= 0) return x;                    // no build number, no prompt
      const r = oText.apply(this, arguments);
      if (str === tag) oText.call(this, 'm_lav', 'Yazeed and Salem against the Dhanabs', x, y + 16, 'c');
      return r;
    };
  });
  await sleep(2200);                                                                     // (the logo has dropped in and settled)
  await page.screenshot({ path: OUT, clip: { x: 0, y: 0, width: 1200, height: 630 } });
  await browser.close();
  console.log('wrote', OUT);
})();
