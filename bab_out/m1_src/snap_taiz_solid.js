// snap_taiz_solid.js - Taiz's picture at given places with what the Apache can fly into outlined (the level's rock
// polygons, in red) and the route (in yellow), for telling solid from scenery. Pictures to shots/solid/.
// Usage: node snap_taiz_solid.js [url] x,y x,y ...   (the camera centred on each x,y)
const { chromium } = require('playwright');
const fs = require('fs');
const URL = process.argv[2] && process.argv[2].startsWith('http') ? process.argv[2] : 'http://127.0.0.1:8766/index.html?internal=1';
const SPOTS = process.argv.slice(2).filter(a => /^\d+,\d+$/.test(a)).map(a => a.split(',').map(Number));
const OUT = __dirname + '/shots/solid/', PLAIN = process.argv.includes('--plain');
(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  for (const f of fs.readdirSync(OUT)) if (f.startsWith(PLAIN ? 'plain_' : 'solid_')) fs.unlinkSync(OUT + f);
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 20000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate(() => window.__m1.begin('taiz', 1));
  await page.waitForFunction(() => window.__m1.state() === 'play' && window.__m1.sim().heli && window.__m1.sim().heli.st === 'fly', null, { timeout: 20000 });
  for (const [x, y] of SPOTS) {
    const info = await page.evaluate(([x, y]) => {
      window.__m1.frozen = true;
      const s = window.__m1.sim(), VW = s.viewW || Render.width(), VH = Render.height();
      s.cam = x - VW / 2; s.camY = y - VH / 2; s.heli.x = x - 60; s.heli.y = y - 40;
      Render.draw(s, { paused: false, fps: null, lock: false, auto: false, sub: null, overlay: false, caps: true, noHud: true, dim: 0 });
      return { cam: s.cam, camY: s.camY, VW, VH };
    }, [x, y]);
    // (the page puts the picture on the screen in its own loop: let it run two frames with the game held still)
    await page.evaluate(() => new Promise(res => {
      const real = Sim.step; Sim.step = function () {};
      window.__m1.frozen = false;
      requestAnimationFrame(() => requestAnimationFrame(() => { window.__m1.frozen = true; Sim.step = real; res(); }));
    }));
    // the outlines over the picture, in the page
    await page.evaluate(({ info, PLAIN, rock, route }) => {
      const cv = [...document.querySelectorAll('canvas')].sort((a, b) => b.getBoundingClientRect().width - a.getBoundingClientRect().width)[0];
      const r = cv.getBoundingClientRect(), k = r.width / info.VW;
      let svg = document.getElementById('solidSvg');
      if (!svg) { svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); svg.id = 'solidSvg'; document.body.appendChild(svg); }
      svg.setAttribute('style', `position:fixed;left:${r.left}px;top:${r.top}px;width:${r.width}px;height:${r.height}px;pointer-events:none;z-index:99`);
      svg.setAttribute('viewBox', `0 0 ${r.width} ${r.height}`);
      const P = pts => pts.map(p => ((p[0] - info.cam) * k).toFixed(1) + ',' + ((p[1] - info.camY) * k).toFixed(1)).join(' ');
      if (PLAIN) { svg.innerHTML = ''; return; }
      svg.innerHTML = rock.map(p => `<polygon points="${P(p)}" fill="rgba(255,0,0,0.12)" stroke="#ff3030" stroke-width="2"/>`).join('') +
        `<polyline points="${P(route)}" fill="none" stroke="#ffe040" stroke-width="2" stroke-dasharray="6 4"/>`;
    }, { info, PLAIN, rock: await page.evaluate(() => window.__m1.sim().L.fly.rock), route: await page.evaluate(() => window.__m1.sim().L.fly.route) });
    await page.screenshot({ path: OUT + (PLAIN ? 'plain_' : 'solid_') + x + '_' + y + '.png' });
    console.log('solid_' + x + '_' + y + '.png', JSON.stringify(info));
  }
  console.log(errors.length ? 'ERRORS: ' + errors.join(' | ') : 'no errors on the page');
  await browser.close();
})();
