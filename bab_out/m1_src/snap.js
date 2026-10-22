const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  for (const [w, h, dpr, name] of JSON.parse(process.argv[2])) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: dpr, hasTouch: true, isMobile: true });
    const page = await ctx.newPage();
    await page.goto('http://127.0.0.1:8766/index.html');
    await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home');
    await page.waitForTimeout(300);
    await page.screenshot({ path: '/home/claude/bab_out/m1_src/shots/' + name + '.png' });
    await ctx.close();
  }
  await browser.close();
})();
