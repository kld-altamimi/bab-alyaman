// check_music.js - which sounds start when each mission begins (Khaled, 29 Oct: every mission opened with the Strait's
// start call, then its own theme). Every buffer started in the page is logged with its length and whether it loops; the
// start call is the one-shot of jingle_start's length.
// Usage: node check_music.js <url>
const { chromium } = require('playwright');
const URL = process.argv[2];
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.route(/posthog|fonts\.(googleapis|gstatic)/, (r) => r.abort());
  await page.addInitScript(() => {
    window.__starts = [];
    const st = AudioBufferSourceNode.prototype.start;
    AudioBufferSourceNode.prototype.start = function (when, off, dur) {
      try { window.__starts.push({ len: this.buffer ? +this.buffer.duration.toFixed(2) : 0, loop: this.loop, off: off == null ? 0 : +(+off).toFixed(2), t: performance.now() }); } catch (e) {}
      return st.apply(this, arguments);
    };
  });
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 30000 });
  await page.touchscreen.tap(422, 150);
  await page.waitForFunction(() => window.Sound && Sound.isReady && Sound.isReady(), null, { timeout: 30000 }).catch(() => {});
  await page.waitForTimeout(1500);
  const ids = await page.evaluate(() => [typeof LEVEL !== 'undefined' && LEVEL, typeof LEVEL_MOCHA !== 'undefined' && LEVEL_MOCHA, typeof LEVEL_TAIZ !== 'undefined' && LEVEL_TAIZ, typeof LEVEL_IBB !== 'undefined' && LEVEL_IBB].filter(Boolean).map(L => L.id));
  // the start call's own length: jingle_start.mp3, decoded here
  const jl = await page.evaluate(async () => {
    const r = await fetch('audio/jingle_start.mp3'); const b = await r.arrayBuffer();
    const c = new OfflineAudioContext(1, 44100, 44100); const d = await c.decodeAudioData(b); return +d.duration.toFixed(2);
  });
  console.log('missions', ids.join(','), '| start call length', jl, 's');
  for (const id of ids) {
    await page.evaluate(() => { window.__starts.length = 0; });
    await page.evaluate((id) => window.__m1.begin(id, 0), id);
    await page.waitForTimeout(4000);       // (time for a mission's music file to arrive, if it was not in hand)
    const r = await page.evaluate(() => ({ starts: window.__starts.filter(x => x.len > 3).map(x => x.len + (x.loop ? 'L' : '')), playing: Sound.playing(), track: Sound.track() }));
    const call = r.starts.some(s => Math.abs(parseFloat(s) - jl) < 0.05 && !/L$/.test(s));
    console.log(id.padEnd(8), 'loop playing:', String(r.playing).padEnd(9), 'start call:', call ? 'YES' : 'no ', ' long buffers started:', r.starts.join(' '));
    await page.evaluate(() => window.__m1.stop && window.__m1.stop());
  }
  console.log(errors.length ? 'page errors: ' + errors.join(' | ') : 'no page errors');
  await browser.close();
})();
