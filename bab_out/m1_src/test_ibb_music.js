// test_ibb_music.js - Ibb plays its own theme: on the map its card asks for it (and not the Coffee Port's), the mission
// starts it after the start jingle, and it is the loop sounding once play is under way. Usage: node test_ibb_music.js <url>
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const page = await (await browser.newContext({ viewport: { width: 844, height: 390 }, locale: 'en-US' })).newPage();
  const errors = [], files = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('request', r => { const m = r.url().match(/audio\/([a-z_]+)\.mp3/); if (m) files.push(m[1]); });
  await page.route(/posthog|fonts\.(googleapis|gstatic)/, (r) => r.abort());
  await page.goto(process.argv[2]);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 30000 });
  await page.mouse.click(422, 200);
  await page.evaluate(() => window.__m1.begin('ibb', 0));
  await page.waitForFunction(() => window.__m1.state() === 'play', null, { timeout: 15000 });
  let seen = null;
  for (let i = 0; i < 40 && !seen; i++) {
    await page.waitForTimeout(500);
    seen = await page.evaluate(() => Sound.playing());
  }
  const info = await page.evaluate(() => Sound.info());
  console.log('loop sounding:', seen, '| files fetched:', [...new Set(files)].join(' '), '| sound', JSON.stringify(info));
  const ok = seen === 'ibb' && files.includes('music_ibb') && !files.includes('music_mocha') && !errors.length;
  console.log(errors.length ? 'page errors: ' + errors.join(' | ') : 'no page errors');
  console.log(ok ? 'IBB MUSIC OK' : 'IBB MUSIC PROBLEM');
  await browser.close();
  process.exit(ok ? 0 : 1);
})();
