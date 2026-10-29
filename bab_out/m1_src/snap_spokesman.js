// snap_spokesman.js - pictures of Ibb's opening and of Brigadier Breaking's fight and the reveal after it, as the game
// draws them (30 Oct: "Go ahead and finish the whole level"). The opening plays by itself; the fight is moved along by hand
// (the microphone shot through the game's own shot hook, the stuns' damage through its hurt hook), Yazeed kept from harm.
// Usage: node snap_spokesman.js <url> <out dir> [--ar] [--only opening|fight]
const { chromium } = require('playwright');
const fs = require('fs');
const args = process.argv.slice(2).filter(a => !a.startsWith('--'));
const URL = args[0], OUT = args[1];
const LANG = process.argv.includes('--ar') ? 'ar' : 'en';
const ONLY = (process.argv.find(a => a.startsWith('--only=')) || '').slice(7);
fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true, locale: LANG === 'ar' ? 'ar' : 'en-US' });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.route(/posthog|fonts\.(googleapis|gstatic)/, (r) => r.abort());
  await page.goto(URL);
  await page.waitForFunction(() => window.__m1 && window.__m1.state() === 'home', null, { timeout: 30000 });
  await page.touchscreen.tap(422, 150);
  await page.evaluate((l) => window.__m1.setLang(l), LANG);
  const pre = LANG === 'ar' ? 'ar_' : '';
  async function snap(name) {
    await page.evaluate(() => { const s = window.__m1.sim(); s.p.inv = 0; s.bullets = s.bullets.filter(b => b.own); s.bombs = s.bombs.filter(b => b.own); });
    await page.waitForTimeout(40);
    await page.screenshot({ path: OUT + '/' + pre + name + '.png' });
    await page.evaluate(() => { const s = window.__m1.sim(); s.p.inv = 99999; });
    const info = await page.evaluate(() => { const s = window.__m1.sim(), b = s.boss; return { t: s.tick, x: Math.round(s.p.x), cam: Math.round(s.cam), boss: b ? b.st + ' hp ' + b.hp + ' ph ' + b.phase + ' pod ' + b.pod : '-', rv: s.spk && s.spk.rv ? s.spk.rv.st : '-', open: s.open ? s.open.st : '-' }; });
    console.log(name, JSON.stringify(info));
  }
  const until = (fn, arg, ms) => page.waitForFunction(fn, arg, { timeout: ms || 30000, polling: 16 });

  if (ONLY !== 'fight') {
    // ---- the opening
    await page.evaluate(() => window.__m1.begin('ibb', 0));
    await until(() => window.__m1.state() === 'play');
    await until(() => { const s = window.__m1.sim(); return s.open && s.open.st === 'drive' && s.open.x > 40; });
    await snap('op1_drive');
    await until(() => { const s = window.__m1.sim(); return s.open && s.open.st === 'stop'; });
    await page.waitForTimeout(150);
    await snap('op2_stop');
    await until(() => { const s = window.__m1.sim(); return s.open && s.open.st === 'hop' && s.p.vy > -60; });
    await snap('op3_hop');
    await until(() => { const s = window.__m1.sim(); return s.open && s.open.st === 'down' && s.open.t > 60; });
    await snap('op4_salem');
    await until(() => { const s = window.__m1.sim(); return s.open && s.open.st === 'back' && s.open.t > 20; });
    await snap('op5_back');
    await until(() => { const s = window.__m1.sim(); return !s.script; });
    await page.waitForTimeout(900);
    await snap('op6_go');
    await until(() => { const l = window.__m1.line(); return l && l.id === 'yazeed_quiet'; }, null, 20000).catch(() => {});
    await page.waitForTimeout(300);
    await snap('op7_quiet');
  }
  if (ONLY !== 'opening') {
    // ---- the fight: the pass's earlier fights put down, Yazeed at the lookout's near end
    await page.evaluate(() => window.__m1.begin('ibb', 3));
    await until(() => window.__m1.state() === 'play');
    await page.waitForTimeout(300);
    await page.evaluate(() => {
      const s = window.__m1.sim(), L = s.L, W = Render.width();
      window.__m1.frozen = true;
      for (const g of s.gates) {
        if (g.id === 'arena' || g.id === 'van') continue;
        g.done = true;
        for (const k of g.groups) { const G = s.groups[k]; G.done = true; G.pending.length = 0; G.awake = true; }
      }
      s.enemies.forEach(e => { if (e.alive) { e.alive = false; e.st = 'gone'; e.deadT = 999; } });
      const x = L.groups.BOSS.trig + 4;
      s.p.x = x; s.p.y = Sim.groundY(L, x); s.p.vx = 0; s.p.inv = 99999; s.p.plat = -1; s.p.air = false; s.p.face = 1;
      s.cam = Math.min(x - W * 0.35, 7840 - W * 0.5);
      window.__m1.frozen = false;
    });
    await until(() => { const s = window.__m1.sim(); return s.boss && s.boss.st === 'arrive' && s.boss.x < s.cam + Render.width() - 30; });
    await snap('f1_arrive');
    await until(() => { const s = window.__m1.sim(); return s.boss && s.boss.st === 'speak' && s.boss.stT > 40; });
    await snap('f2_speak');
    // cut him off: three shots on the live microphone (the game's own shot hook), then hurt him for a stun's worth
    // (shots put into the game as Yazeed's own, a few pixels short of what they are for, so that the game plays them out
    // and says what it says: the microphone, him while stunned, the rack)
    const fire = (pts) => page.evaluate((pts) => { const s = window.__m1.sim(); for (const [x, y] of pts) s.bullets.push({ x: x, y: y, vx: 450, vy: 0, life: 30, own: true, age: 0 }); }, pts);
    const cutHim = async () => {
      await until(() => { const s = window.__m1.sim(); return s.boss && s.boss.st === 'speak' && s.boss.stT > 10; }, null, 40000);
      const at = await page.evaluate(() => { const s = window.__m1.sim(); return [Sim.ext.spokesman.micX(s, s.boss), s.L.arena.y - 22]; });
      await fire([0, 1, 2].map(i => [at[0] - 6 - 9 * i, at[1]]));
      await until(() => { const s = window.__m1.sim(); return s.boss && s.boss.st === 'stun'; }, null, 5000);
      await page.waitForTimeout(250);
    };
    const hurtHim = async (n) => {
      // (one at a time, from just short of him: shots that start off the picture are dropped)
      for (let i = 0; i < n; i++) {
        const at = await page.evaluate(() => { const b = window.__m1.sim().boss; return b && b.st === 'stun' ? [b.x, b.y - 24] : null; });
        if (!at) break;
        await fire([[at[0] - 10, at[1]]]);
        await page.waitForTimeout(40);
      }
      await page.waitForTimeout(300);
    };
    await cutHim();
    await snap('f3_stun');
    await hurtHim(14);
    await until(() => { const s = window.__m1.sim(); return s.boss && s.boss.st === 'leap' && s.boss.stT > 18; });
    await snap('f4_leap');
    await cutHim(); await hurtHim(14);
    await cutHim(); await hurtHim(14);
    // two podiums left: shouting, the feedback, the dash
    await until(() => { const s = window.__m1.sim(); return s.boss && s.boss.st === 'speak' && s.boss.phase === 2 && s.boss.stT > 40; }, null, 40000);
    await snap('f5_phase2');
    await until(() => { const s = window.__m1.sim(); return s.spk.waves.length > 0 && s.spk.waves[0].t > 20; }, null, 40000);
    await snap('f6_wave');
    await cutHim(); await hurtHim(14);
    await until(() => { const s = window.__m1.sim(); return s.boss && s.boss.st === 'dash' && s.boss.stT > 12; }, null, 40000);
    await snap('f7_dash');
    // the last podium, in the dark
    await until(() => { const s = window.__m1.sim(); return s.boss && s.boss.st === 'speak' && s.boss.phase === 3 && s.spk.dark >= 1 && s.boss.stT > 30; }, null, 40000);
    await snap('f8_dark');
    await cutHim();
    await until(() => { const s = window.__m1.sim(); return s.boss && s.boss.st === 'stun' && s.boss.stT > 30; });
    await snap('f9_dark_stun');
    await hurtHim(20);
    await until(() => { const s = window.__m1.sim(); return s.boss && s.boss.st === 'dying' && s.boss.stT > 50; });
    await snap('r1_caught');
    await until(() => { const s = window.__m1.sim(); return s.spk.rv && s.spk.rv.st === 'rerender' && s.spk.rv.t > 70; });
    await snap('r2_closeup');
    await until(() => { const s = window.__m1.sim(); return s.spk.rv && s.spk.rv.st === 'cables' && s.spk.rv.t > 30; }, null, 30000);
    await snap('r3_cables');
    // Yazeed walks up to the van
    await page.evaluate(() => { const s = window.__m1.sim(); s.enemies.forEach(e => { if (e.alive && e.tech == null) { e.alive = false; e.st = 'gone'; e.deadT = 999; } }); });
    await until(() => { const s = window.__m1.sim(); return s.gates.find(g => g.id === 'arena').done; }, null, 20000);
    await page.evaluate(() => { const s = window.__m1.sim(), W = Render.width(); s.cam = Math.min(8100 - W * 0.5, s.L.endRight - W); s.p.x = s.L.arena.van.door[0] - 60; s.p.y = s.L.arena.y; s.p.face = 1; });
    await until(() => { const l = window.__m1.line(); return l && l.id === 'tech_videos' && window.__m1.sim().tick - l.t0 > 20; }, null, 20000);
    await snap('r4a_videos');
    await until(() => { const s = window.__m1.sim(); return s.spk.techs >= 3 && s.enemies.filter(e => e.tech != null && e.st === 'surr').length >= 2; }, null, 30000);
    await snap('r4_van');
    const rack = await page.evaluate(() => { const V = window.__m1.sim().L.arena.van; return [V.door[0], (V.roof + V.sill) / 2]; });
    await fire([0, 1, 2, 3, 4, 5].map(i => [rack[0] - 4 - 9 * i, rack[1]]));
    await page.waitForTimeout(400);
    await snap('r5_smash');
    for (const [id, nm] of [['uncle_again', 'r5a_uncle'], ['tech_cannot', 'r5b_tech'], ['uncle_me', 'r5c_uncle']]) {
      await until((id) => { const l = window.__m1.line(); return l && l.id === id && window.__m1.sim().tick - l.t0 > 20; }, id, 20000);
      await snap(nm);
    }
    await until(() => { const s = window.__m1.sim(); return s.spk.rv && s.spk.rv.st === 'clearing' && s.spk.rv.t > 120; }, null, 30000);
    await snap('r6_clearing');
    await until(() => { const s = window.__m1.sim(); return s.spk.rv && s.spk.rv.st === 'done'; }, null, 30000);
    await page.waitForTimeout(1500);
    await snap('r7_plateau');
    // and off the pass: walk right (the keyboard's arrow) to the way out, and the results
    await page.keyboard.down('ArrowRight');
    await until(() => window.__m1.state() !== 'play' || window.__m1.sim().status === 'clear', null, 30000).catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: OUT + '/' + pre + 'r8_walk.png' });
    await page.keyboard.up('ArrowRight');
    await until(() => window.__m1.state() === 'results' || window.__m1.state() === 'clear', null, 20000).catch(() => {});
    await page.waitForTimeout(2500);
    await page.screenshot({ path: OUT + '/' + pre + 'r9_results.png' });
    console.log('end', await page.evaluate(() => window.__m1.state() + ' ' + window.__m1.sim().status));
  }
  console.log(errors.length ? 'page errors: ' + errors.join(' | ') : 'no page errors');
  await browser.close();
})();
