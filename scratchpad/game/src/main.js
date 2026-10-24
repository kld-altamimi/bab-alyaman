// main.js - the shell around the game: loading, the home screen and the campaign map, the loop, the menus, what is kept
// between visits, and telling picture and sound what happened.
(function () {
  'use strict';
  function el(id) { return document.getElementById(id); }
  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }
  var STEP_MS = 1000 / 60, H = 216;
  var app = el('app'), rotEl = el('rot'), hi = el('hi'), lo = el('lo'), padEl = el('pad'), uiEl = el('ui');
  var bFire = el('bFire'), bJump = el('bJump'), bBomb = el('bBomb'), stickEl = el('stick'), knobEl = el('knob');
  var panels = { home: el('pHome'), map: el('pMap'), opts: el('pOpts'), brief: el('pBrief'), pause: el('pPause'), over: el('pOver'), results: el('pDone') };
  var hx = null, imgs = {}, W = 468, sim = null, backdrop = null, state = 'load';
  // the zoom the picture is drawn at: 1, or a mission's own while it is on the screen (Taiz, by Apache, is seen from further
  // back). The world is then drawn larger than W x H, and the HUD on a canvas of its own at W x H (render.js)
  var Z = 1;
  function zoomOf(L) { return (L && L.zoom) || 1; }
  function viewOf(L) { var z = zoomOf(L); return [Math.round(W * z), Math.round(H * z)]; }
  var geo = { rot: false, land: true, scale: 1, n: 1, fast: false, forceFast: false, fellBack: false, dpr: 1, vw: 0, vh: 0, lanes: [0.07, 0.09] };
  var LANES_THUMBS = [0.18, 0.25], LANES_CLEAR = [0.07, 0.09];      // how much of each edge is kept for walking in: more where thumbs lie over the picture
  var appRect = { left: 0, top: 0, width: 0, height: 0 };
  var prefs = { scheme: 'hold', muted: false, vol: null, lang: null, dev: false, best: null, prog: null, last: null, fpsTip: false };   // vol: the three meters, 0..1 each; lang: null = the browser's; fpsTip: the 30-frames tip has been shown on this device
  var coarse = false, fsOK = false, wake = null, calm = false, booted = false;
  // the missions that are built, by their id on the map (campaign.js); cur is the one being played
  var LEVELS = {}, cur = 'm1';
  [typeof LEVEL !== 'undefined' ? LEVEL : null, typeof LEVEL_MOCHA !== 'undefined' ? LEVEL_MOCHA : null,
   typeof LEVEL_ZABID !== 'undefined' ? LEVEL_ZABID : null, typeof LEVEL_TAIZ !== 'undefined' ? LEVEL_TAIZ : null,
   typeof LEVEL_IBB !== 'undefined' ? LEVEL_IBB : null].forEach(function (L) { if (L) LEVELS[L.id] = L; });
  // the run being played: the checkpoint it started at, and whether one was skipped on the way (either makes it a
  // practice run: a clear still counts, but no best and no medals are kept). fromSel: the start chosen on each card.
  var run = { from: 0, skipped: false }, fromSel = {};

  // ------------------------------------------------------------------ small things kept between visits
  var KEY = 'strait-m1';
  function loadPrefs(extra) {
    try {
      var raw = window.localStorage.getItem(KEY);
      if (raw) { var o = JSON.parse(raw); for (var k in prefs) if (o && o[k] != null) prefs[k] = o[k]; }
    } catch (e) {}
    if (extra) for (var k2 in prefs) if (extra[k2] != null) prefs[k2] = extra[k2];
    if (prefs.scheme !== 'auto') prefs.scheme = 'hold';
    prefs.dev = prefs.dev === true;
    tidyProgress();
  }
  // how far through the campaign: for each mission, the furthest checkpoint reached, whether it is cleared, the best
  // result, the medals ever won, how many goes, and whether its CLEAR has been stamped on the map yet
  function tidyProgress() {
    var p = prefs.prog && typeof prefs.prog === 'object' ? prefs.prog : {};
    CAMPAIGN.forEach(function (m) {
      var q = p[m.id] && typeof p[m.id] === 'object' ? p[m.id] : {};
      var best = q.best && typeof q.best.total === 'number' ? { total: q.best.total, time: q.best.time | 0 } : null;
      p[m.id] = { reached: Math.max(0, q.reached | 0), cleared: !!q.cleared, best: best, ace: !!q.ace, lib: !!q.lib, runs: q.runs | 0, stamped: !!q.stamped };
    });
    // (builds before the map kept one best score for the Strait: a best means it was cleared)
    if (prefs.best && typeof prefs.best.total === 'number' && !p.m1.best) { p.m1.best = prefs.best; p.m1.cleared = true; p.m1.reached = LEVEL.zones.length - 1; }
    prefs.prog = p;
  }
  function savePrefs() { try { window.localStorage.setItem(KEY, JSON.stringify(prefs)); } catch (e) {} }
  // an iPhone or iPad (an iPad says it is a Mac, but a Mac has no touch screen)
  function isIOS() { return /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1); }

  // ------------------------------------------------------------------ where everything sits
  function mapPoint(cx, cy) {
    var x = cx - appRect.left, y = cy - appRect.top;
    return geo.rot ? [y, appRect.width - x] : [x, y];
  }
  function place(node, b) {
    node.style.width = node.style.height = (b.r * 2).toFixed(1) + 'px';
    node.style.transform = 'translate(' + (b.x - b.r).toFixed(1) + 'px,' + (b.y - b.r).toFixed(1) + 'px)';
    node.style.fontSize = Math.max(10, b.r * 0.4).toFixed(1) + 'px';
  }
  // where the X credit lies on the screen: the picture's bottom-right corner, made at least a thumb tall
  var socialHot = false;
  function placeSocial(x0, y0, scale) {
    var a = el('aX'); if (!a) return;
    var w = 110, h = 26;
    try { w = Render.textW('m_org', 'x.com/babalyemengame') + 8; } catch (e) {}
    var pw = w * scale, ph = Math.max(44, h * scale);
    a.style.width = pw + 'px'; a.style.height = ph + 'px';
    a.style.left = (x0 + (W - 2) * scale - pw) + 'px';
    a.style.top = (y0 + (H - 8) * scale - ph) + 'px';
  }
  function layout() {
    if (!booted) return;
    var r = app.getBoundingClientRect();
    if (r.width < 20 || r.height < 20) return;
    appRect = { left: r.left, top: r.top, width: r.width, height: r.height };
    var cs = window.getComputedStyle(app);
    var safeL = parseFloat(cs.paddingLeft) || 0, safeR = parseFloat(cs.paddingRight) || 0;
    var dpr = window.devicePixelRatio || 1;
    // The game is only ever laid out on its side. A phone held upright gets it turned a quarter, so it plays the moment
    // the phone is turned (whether or not the browser turns with it); a tall window on a desk, which cannot be turned,
    // gets it on its side across the window's width.
    var tall = r.height >= r.width;
    var rot = tall && coarse;
    var vw = rot ? r.height : r.width, vh = rot ? r.width : r.height;
    var gl = rot ? 16 : Math.max(16, safeL), gr = rot ? 16 : Math.max(16, safeR);
    var land = true, availW = vw - gl - gr, scale, w, cw, ch, x0, y0;
    scale = vh / H; w = Math.floor(availW / scale);
    if (w > 468) w = 468;
    if (w < 384) { w = 384; scale = availW / 384; }
    cw = w * scale; ch = H * scale;
    x0 = gl + (availW - cw) / 2;
    y0 = coarse ? 0 : (vh - ch) / 2;
    // the picture is drawn small, enlarged by a whole number, and the last fraction is left to the browser
    var sd = scale * dpr, n = clamp(Math.round(sd), 1, 6);
    while (n > 1 && w * n * H * n > 4.2e6) n--;
    var ratio = sd / n, exact = Math.abs(ratio - 1) < 0.004;
    if (exact && w * n / dpr <= availW + 0.01 && H * n / dpr <= vh + 0.01) { cw = w * n / dpr; ch = H * n / dpr; x0 = gl + (availW - cw) / 2; } else exact = false;
    var snap = function (v) { return Math.round(v * dpr) / dpr; };
    x0 = snap(x0); y0 = snap(y0); cw = snap(cw); ch = snap(ch);
    var fast = geo.forceFast;
    var flipped = geo.land !== land || geo.rot !== rot;       // the thumbs have moved: stop and let the player settle
    geo.cx0 = x0; geo.cy0 = y0; geo.cw = cw; geo.ch = ch;
    geo.rot = rot; geo.land = land; geo.scale = scale; geo.n = n; geo.fast = fast; geo.dpr = dpr; geo.vw = vw; geo.vh = vh;

    if (rot) {
      rotEl.style.width = vw + 'px'; rotEl.style.height = vh + 'px'; rotEl.style.left = '50%'; rotEl.style.top = '50%';
      rotEl.style.transform = 'translate(-50%,-50%) rotate(90deg)';
    } else {
      rotEl.style.width = '100%'; rotEl.style.height = '100%'; rotEl.style.left = '0'; rotEl.style.top = '0'; rotEl.style.transform = 'none';
    }
    app.classList.add('is-land');
    app.classList.toggle('is-rot', rot);

    geo.exact = exact;
    if (w !== W || lo.width !== Math.round(w * Z)) { W = w; Render.resize(W, Z); if (backdrop) backdrop.viewW = W; }
    [hi, lo].forEach(function (c) { c.style.left = x0 + 'px'; c.style.top = y0 + 'px'; c.style.width = cw + 'px'; c.style.height = ch + 'px'; });
    sizeHi();
    hi.hidden = fast; lo.hidden = !fast;

    // thumbs
    // tight in the corner, as on the look-and-feel sheet: the fight is staged clear of the right quarter of the picture
    var R = vw - gr, B = vh - Math.max(8, vh * 0.03), rF = clamp(vh * 0.111, 28, 48);
    var fire = { x: R - 1.75 * rF, y: B - 1.9 * rF, r: rF };
    var jump = { x: fire.x - 1.75 * rF, y: fire.y + 0.95 * rF, r: Math.max(26, rF * 0.72) };
    var bomb = { x: fire.x + 0.1 * rF, y: fire.y - 2.0 * rF, r: Math.max(24, rF * 0.67) };
    // (the Apache: an aim stick where FIRE was, so FLARES and ROCKETS stand a little further out from it)
    if (app.classList.contains('is-fly')) {
      jump = { x: fire.x - 2.2 * rF, y: fire.y + 1.0 * rF, r: Math.max(28, rF * 0.78) };
      bomb = { x: fire.x + 0.3 * rF, y: fire.y - 2.3 * rF, r: Math.max(24, rF * 0.67) };
    }
    var Rs = clamp(vh * 0.135, 36, 58);
    var home = { x: gl + Rs + 26, y: B - Rs - 22, r: Rs };
    var top = y0 + ch * 0.2;
    var pcx = x0 + (W - 12) * scale, pcy = y0 + 13 * scale, half = Math.max(22, 11 * scale);
    var G = { fire: fire, jump: jump, bomb: bomb, stick: home, split: vw / 2, top: top, shown: app.classList.contains('has-touch'),
              pause: { x0: pcx - half, x1: pcx + half, y0: pcy - half, y1: pcy + half } };
    geo.lanes = G.shown ? LANES_THUMBS : LANES_CLEAR;
    if (backdrop) { backdrop.laneL = geo.lanes[0]; backdrop.laneR = geo.lanes[1]; }
    place(bFire, fire); place(bJump, jump); place(bBomb, bomb);
    stickEl.style.width = stickEl.style.height = (Rs * 2).toFixed(1) + 'px';
    Input.setLayout(G, mapPoint);
    geo.G = G;

    // the menus lie over the picture and keep within it (on a very wide screen it does not reach the edges; in a tall
    // window on a desk they keep to the picture's band across the middle)
    var band = tall && !coarse;
    uiEl.style.top = band ? y0 + 'px' : '0'; uiEl.style.bottom = band ? Math.max(0, vh - y0 - ch) + 'px' : '';
    uiEl.style.paddingLeft = Math.max(gl, x0) + 'px'; uiEl.style.paddingRight = Math.max(gr, vw - (x0 + cw)) + 'px';
    if (flipped && state === 'play') pause();
    if (onMap()) aim(mv.sel, !mv.moved);
    turnHint();
    if (state !== 'load') draw(true);
  }

  // the enlarged picture: the small one times a whole number, the last fraction left to the browser. Zoomed out, the world is
  // enlarged by an even number (nz), so that the HUD, at its own size, is enlarged by a whole number too (Z x nz)
  function sizeHi() {
    var sd = geo.scale * geo.dpr, n = geo.n, k = n;
    if (Z !== 1) {
      // (the even number nearest the screen's own enlargement, by ratio: a little under is softened, a little over is not)
      var t = sd / Z, n0 = Math.max(2, 2 * Math.floor(t / 2)), n1 = n0 + 2;
      n = Math.abs(Math.log(t / n0)) <= Math.abs(Math.log(t / n1)) ? n0 : n1;
      while (n > 2 && W * Z * n * H * Z * n > 4.2e6) n -= 2;
      k = Z * n;
    }
    geo.nz = n;
    var hw = Math.round(W * k), hh = Math.round(H * k);
    if (hi.width !== hw || hi.height !== hh) { hi.width = hw; hi.height = hh; }
    hx = hi.getContext('2d', { alpha: false });
    hx.imageSmoothingEnabled = false;
    var ratio = sd / k;
    hi.style.imageRendering = ((geo.exact && Z === 1) || (ratio > 0.8 && ratio < 1.25) || (Z !== 1 && ratio <= 0.8)) ? 'auto' : 'pixelated';
  }
  function setZoom(z) {
    if (z === Z) return;
    Z = z;
    Render.resize(W, Z);
    sizeHi();
  }
  // what is on the screen decides the zoom: a zoomed mission's own while it is being played (and paused, lost or won over
  // it), 1 for everything else
  function zoomNow() {
    var screen = state === 'opts' || state === 'brief' ? optsFrom : state;
    // (Taiz's opening is played on foot at the usual size: the picture draws back to the Apache's once it lifts off)
    return (screen === 'home' || screen === 'map' || screen === 'load' || !sim) ? 1 : (sim.zoom != null && sim.zoom < 1.0001 ? 1 : zoomOf(sim.L));
  }

  // ------------------------------------------------------------------ how smoothly it is running
  var M = { ring: [], hz: 60, snap: STEP_MS, fps: 60, wF: 0, wMs: 0 }, P = null;
  function resetPlayMeter() { P = { frames: 0, ms: 0, long: 0, worst: 0, minFps: 999, sF: 0, sMs: 0, slips: 0, slow: 0 }; }
  resetPlayMeter();
  function meter(d) {
    M.ring.push(d); if (M.ring.length > 90) M.ring.shift();
    M.wF++; M.wMs += d;
    if (M.wMs >= 500) {
      M.fps = Math.round(M.wF * 1000 / M.wMs); M.wF = 0; M.wMs = 0;
      if (M.ring.length >= 30) {
        var a = M.ring.slice().sort(function (x, y) { return x - y; }), med = a[a.length >> 1], ks = [0.25, 1 / 3, 0.5, 1, 2], s = med;
        for (var i = 0; i < ks.length; i++) if (Math.abs(med - STEP_MS * ks[i]) < STEP_MS * ks[i] * 0.015) s = STEP_MS * ks[i];
        M.hz = Math.round(1000 / med); M.snap = s;
      }
    }
    if (state === 'play' && d < 1000) {
      P.frames++; P.ms += d;
      if (d > P.worst) P.worst = d;
      if (d > M.snap * 1.6 + 1) P.long++;
      P.sF++; P.sMs += d;
      if (P.sMs >= 1000) { var f = P.sF * 1000 / P.sMs; if (f < P.minFps) P.minFps = f; P.sF = 0; P.sMs = 0; }
      // how long the frames have come at exactly 30 a second, without a break (what a phone's power saving does: the 30-frames tip)
      P.slow = Math.abs(M.snap - 2 * STEP_MS) < 0.5 ? P.slow + d : 0;
      // the sharper way of enlarging the picture costs a little; give it up if this phone cannot spare it
      if (!geo.fast && !geo.fellBack && P.frames === 360 && P.long / P.frames > 0.12) { geo.forceFast = true; geo.fellBack = true; layout(); }
    }
  }
  function report() {
    var a = Sound.info(), avg = P.ms > 0 ? (P.frames * 1000 / P.ms).toFixed(1) : '-', mn = P.minFps < 900 ? P.minFps.toFixed(0) : '-';
    var lines = [
      'Bab al-Yemen v' + BUILD,
      'Screen ' + Math.round(appRect.width) + ' x ' + Math.round(appRect.height) + ' at ' + (+geo.dpr.toFixed(2)) + 'x, ' + (geo.rot ? 'held upright, game turned sideways' : 'on its side') + (coarse ? ', touch' : ', mouse or keys'),
      'Picture ' + W + ' x ' + H + ', one dot = ' + (geo.scale * geo.dpr).toFixed(2) + ' screen dots, ' + (geo.fast ? 'plain enlarging' + (geo.fellBack ? ' (switched after slow frames)' : '') : 'sharp enlarging x' + geo.n),
      'Display about ' + M.hz + ' Hz. In play: ' + avg + ' frames a second on average, worst second ' + mn + ', slowest frame ' + Math.round(P.worst) + ' ms, ' + P.long + ' long frames in ' + P.frames + (P.slips ? ', ' + P.slips + ' steps dropped' : ''),
      'Sound ' + a.state + (a.rate ? ' at ' + a.rate + ' Hz' : '') + ', files ' + a.decoded + ' decoded ' + a.how + (a.failed ? ', SOME FAILED TO LOAD' : '') + (a.session ? ', playback session set' : '') + (a.latency != null ? ', latency ' + a.latency + ' ms' : ''),
      'Fire: ' + (prefs.scheme === 'auto' ? 'auto' : 'hold') + ', lock used ' + Input.lockCount() + ' times. Full screen ' + (fsOK ? 'offered' : 'not offered') + '. Touch points ' + (navigator.maxTouchPoints || 0) + '.',
      navigator.userAgent
    ];
    if (M.hz >= 28 && M.hz <= 32) lines.splice(4, 0, 'A steady 30 usually means a power-saving mode is holding the browser back.');
    if (sim && LEVELS[cur] && Menu.mission(cur)) lines.splice(1, 0, 'Mission: ' + Menu.mission(cur).name + (run.from ? ', started at ' + zoneWords(LEVELS[cur], run.from) : '') + (run.skipped ? ', checkpoints skipped' : '') + ', now at ' + zoneWords(sim.L, sim.zone));
    return lines.join('\n');
  }

  // ------------------------------------------------------------------ who says what, and when
  var gt = 0, timers = [], line = null, queue = [], flags = {}, hintLine = null, used = { hold: 0, auto: 0 };
  function after(ticks, fn) { timers.push({ at: gt + ticks, fn: fn }); }
  // the Uncle: the Scorpion across the water, never seen, never heard either. His calls come over the Zanabeel's radio as
  // text alone, with the set's crackle, and they take their turn like spoken lines
  // (the Uncle's four calls over the radio are voiced since 17 Oct, reading A: they are ordinary lines now, in
  // gen/audio.json, with the radio's crackle in the recording itself)
  function speak(id, o) {
    o = o || {};
    var v = Sound.lineOf(id);
    if (!v) return;
    var pri = o.pri || 1;
    if (line && gt < line.until - 20) {
      if (o.wait) { if (queue.length < 2 || o.keep) queue.push({ id: id, o: o, at: gt }); return; }      // worth hearing: it takes its turn (a story line always gets one)
      if (pri <= line.pri) return;                 // a bark never talks over its equal
    }
    var dur = Sound.voice(id, { gain: o.gain });
    line = { id: id, who: T(o.who || v.who), text: T(v.text), until: gt + Math.round(dur * 60) + 26, pri: pri };
  }
  function yelp(e) {
    if (gt - (flags.yelpAt || -99) < 9) return;
    flags.yelpAt = gt;
    Sound.voice(e.how === 'blast' || Math.random() < 0.3 ? 'grunt_scream' : 'grunt_yelp', { over: true, gain: 0.55, rate: 0.9 + Math.random() * 0.25, pan: panOf(e.x) });
  }
  function hint(text) { Render.setHint(text, 320); hintLine = { text: text, until: gt + 320 }; }
  function panOf(x) { var vw = sim.viewW || W; return clamp((x - (sim.cam + vw / 2)) / (vw / 2) * 0.7, -0.7, 0.7); }
  function buzz(p) { try { if (navigator.vibrate) navigator.vibrate(p); } catch (e) {} }
  var WHO = { rifle: 'RIFLEMAN', bomber: 'BOMBER', door: 'DOORMAN', cmdr: 'COMMANDER', cook: 'COOK' };
  var HINTS = {
    up: 'Push up to aim up, or up and along to aim between', door: 'Keep shooting and the door breaks. A grenade is quicker', cover: 'He is safe behind the bags until he comes up',
    drive: 'Push forward to go faster, back to slow down. JUMP hops', ram: 'Run them down: the bull bar does the work', truck: 'Ram their pickups to flip them, or land on one',
    drone: 'Shoot the little drones before they dive', mine: 'A red flag marks a mine: hop over it', mount: 'Walk up to the 4x4 to get in',
    vent: 'A vent hisses before it blows: wait, then cross',
    spice: 'Crouch and shoot a spice sack: the Zanabeel cannot fight while they sneeze', sneeze: 'Keep out of the chilli: you cannot shoot while you sneeze',
    bar: 'Grenades break a barricade fastest. So does a drum', gap: 'Jump the gaps between the roofs'
  };

  function react(ev) {
    for (var i = 0; i < ev.length; i++) {
      var e = ev[i], j;
      if (window.HM) HM.sim(e, sim, cur);                       // (analytics.js, in the repo: its own file, never edited here)
      switch (e.t) {
        case 'shot':
          if (e.w === 'chin') { Sound.sfx('gun30', { gain: 0.95 }); break; }      // (the Apache's chain gun)
          Sound.sfx(e.w === 'hmg' ? 'shot_hmg' : 'shot_side', { gain: e.w === 'hmg' ? 0.8 : 0.9 }); break;
        case 'eshot':
          if (e.k === 'heavy' || e.k === 'boss' || e.k === 'aa') Sound.sfx('heavy_shot', { gain: e.k === 'aa' ? 0.7 : 0.85, pan: panOf(e.x), rate: e.k === 'aa' ? 1.15 : 1 });
          else if (e.k === 'sniper') Sound.sfx('heavy_shot', { gain: 0.8, rate: 1.35, pan: panOf(e.x) });
          else if (e.k === 'truck') Sound.sfx('eshot', { gain: 0.7, rate: 0.85, pan: panOf(e.x) });
          else Sound.sfx('eshot', { gain: 0.85, pan: panOf(e.x) });
          break;
        case 'slash':
          Sound.sfx('knife', { gain: 0.9 });
          if (e.hit === 'door') Sound.sfx('clang', { gain: 0.7, pan: panOf(e.x) }); else Sound.sfx('hit_body', { gain: 0.8, pan: panOf(e.x) });
          break;
        case 'hit':
          if (e.kind === 'body') Sound.sfx('hit_body', { pan: panOf(e.x) });
          else if (e.kind === 'guard') Sound.sfx('ricochet', { gain: 0.5, pan: panOf(e.x) });        // a shot glancing off one still coming in
          else if (e.kind === 'door' || e.kind === 'metal') { Sound.sfx('clang', { gain: 0.9, pan: panOf(e.x) }); if (Math.random() < 0.22) Sound.sfx('ricochet', { gain: 0.5, pan: panOf(e.x) }); }
          else if (e.kind === 'stone' && sim.mode === 'fly') break;        // (Taiz: the chain gun's rounds burst, and say so themselves)
          else Sound.sfx('hit_sand', { gain: 0.8, pan: panOf(e.x) });
          break;
        case 'die':
          if (e.how === 'ram') { Sound.sfx('ram', { pan: panOf(e.x) }); buzz(15); }
          if (e.how === 'knife' && !flags.knifed) { flags.knifed = 1; }
          if (e.k !== 'aa' && e.k !== 'drone') yelp(e);                   // (a gun and a drone go up without a word)
          break;
        case 'drum_lit': Sound.sfx('fuse', { gain: 0.9, pan: panOf(e.x) }); break;
        case 'explode':
          if (e.kind === 'chilli') { Sound.sfx('pop', { gain: 0.55, rate: 1.1 + Math.random() * 0.2, pan: panOf(e.x) }); break; }
          if (e.kind === 'drum' || e.kind === 'mine' || e.kind === 'truck' || e.kind === 'heli' || e.kind === 'aa') { Sound.sfx('boom_m', { pan: panOf(e.x) }); buzz(30); }
          else Sound.sfx('boom_s', { pan: panOf(e.x), gain: e.kind === 'kdrone' ? 0.75 : 1 });
          break;
        case 'jump': Sound.sfx('jump', { gain: 0.7 }); break;
        case 'drop': Sound.sfx('jump', { gain: 0.4, rate: 0.8 }); break;
        case 'land': if (e.v > 150) Sound.sfx('land', { gain: 0.8 }); break;
        case 'thud': Sound.sfx('land', { gain: 0.6, rate: 0.85, pan: panOf(e.x) }); break;
        case 'step': Sound.sfx('step', { gain: 0.55 }); break;
        case 'throw':
          Sound.sfx('throw');
          if (!flags.face) {
            for (j = 0; j < sim.enemies.length; j++) {
              var d = sim.enemies[j];
              if (d.alive && d.hostile && d.k === 'door' && Sim.doorUp(d) && Sim.onScreen(sim, d.x, 0) && (d.x - sim.p.x) * sim.p.face > 24 && Math.abs(d.x - sim.p.x) < 180) {
                flags.face = 1;
                after(12, function () { speak('grunt_face', { pri: 3, who: 'DOORMAN' }); });
                break;
              }
            }
          }
          break;
        case 'lob': Sound.sfx('throw', { gain: 0.6, rate: 0.85, pan: panOf(e.x) }); break;
        case 'bounce': Sound.sfx('bounce', { gain: 0.8, pan: panOf(e.x) }); break;
        case 'dyn_land': Sound.sfx('bounce', { gain: 0.5, rate: 0.8, pan: panOf(e.x) }); break;
        case 'tell':
          if (e.k === 'bomber') Sound.sfx('fuse', { gain: 0.8, pan: panOf(e.x) });
          else if (e.k === 'bash') Sound.sfx('bash', { gain: 0.9, pan: panOf(e.x) });
          else if (e.k === 'heavy' || e.k === 'bgun' || e.k === 'aa') Sound.sfx('spinup', { gain: 0.9, pan: panOf(e.x), rate: e.k === 'bgun' ? 0.85 : (e.k === 'aa' ? 1.1 : 1) });
          else if (e.k === 'drone') Sound.sfx('lock', { gain: 0.8, pan: panOf(e.x) });
          else if (e.k === 'rpg') Sound.sfx('fuse', { gain: 0.5, rate: 1.3, pan: panOf(e.x) });
          else if (e.k === 'truck') Sound.sfx('spinup', { gain: 0.5, rate: 1.3, pan: panOf(e.x) });
          else if (e.k === 'bomb') Sound.sfx('bay', { pan: panOf(e.x) });
          else if (e.k === 'swoop') Sound.sfx('boat_horn', { pan: panOf(e.x) });
          else if (e.k === 'spray_hi' || e.k === 'spray_lo') Sound.sfx('spinup', { gain: 0.9, rate: e.k === 'spray_hi' ? 1.1 : 0.8, pan: panOf(e.x) });
          else if (e.k === 'steam' || e.k === 'pour') Sound.sfx('hiss', { pan: panOf(e.x) });
          else if (e.k === 'cgun') Sound.sfx('spinup', { gain: 1, rate: 0.6, pan: panOf(e.x) });          // (the Castle Gun's sweep coming)
          else if (e.k === 'lunge') Sound.sfx('horn_truck', { rate: 0.8, pan: panOf(e.x) });
          else if (e.k === 'lob') Sound.sfx('bay', { rate: 1.2, pan: panOf(e.x) });
          else if (e.k === 'tl_scissors') Sound.sfx('snip', { gain: 0.75, rate: 0.9, pan: panOf(e.x) });       // (the Tailor's shears out)
          else if (e.k === 'tl_pins') Sound.sfx('pins', { gain: 0.6, rate: 0.8, pan: panOf(e.x) });          // (a pinch of pins out of the tin)
          else if (e.k === 'tl_tape') Sound.sfx('tape', { gain: 0.5, rate: 0.6, pan: panOf(e.x) });          // (the tape's case unlatched)
          else if (e.k === 'swing') Sound.sfx('bash', { gain: 0.8, rate: 0.9, pan: panOf(e.x) });
          else if (e.k === 'scoop') {
            Sound.sfx('tick', { gain: 0.8, rate: 0.8, pan: panOf(e.x) });
            if (!flags.cookLine) { flags.cookLine = 1; speak('cook_hungry', { pri: 3, who: 'COOK' }); }      // the first cook to wind up
          }
          else Sound.sfx('tick', { gain: 0.8, pan: panOf(e.x) });
          break;
        case 'door_break':
          Sound.sfx('door_break', { pan: panOf(e.x) });
          if (!flags.door) { flags.door = 1; after(16, function () { speak('grunt_door', { pri: 3, wait: true, who: 'DOORMAN' }); }); }
          break;
        case 'bash': if (e.hit) buzz(45); break;
        case 'pickup':
          if (e.k === 'bean' || e.k === 'chilli') { Sound.sfx('coin', { gain: 0.6, rate: 1.2 }); break; }
          if (e.k === 'hmg') { Sound.sfx('pick_weapon'); speak('ann_hmg', { pri: 6 }); }
          else Sound.sfx('pick_gren');
          break;
        case 'weapon_empty': speak('ann_pistol', { pri: 6 }); break;
        case 'plate_lost': Sound.sfx('plate'); buzz(35); break;
        case 'refill': after(10, function () { Sound.sfx('pick_gren', { gain: 0.7 }); }); break;      // (a checkpoint refill)
        case 'low_armour': after(14, function () { Sound.sfx('low'); }); break;
        case 'life_lost': Sound.sfx('life'); buzz([40, 30, 90]); break;
        case 'alarm': speak('grunt_alarm', { pri: 5, wait: true, who: WHO[whoIs(e)] }); break;
        case 'behind': Sound.sfx('ui_back', { gain: 0.8, pan: -0.5 }); break;
        // a mine coming into view: the drone's two beeps, lower and slower, so the two are not mistaken for each other
        case 'spot': if (e.k === 'rmine') Sound.sfx('lock', { gain: 0.95, rate: 0.6, pan: panOf(e.x) }); else Sound.sfx('ui_move'); break;
        case 'radio': if (RADIO_ON) Sound.sfx('radio', { gain: 0.8 }); break;
        case 'go':
          Sound.sfx('go');
          if (!e.quiet && !gateQuiet(e.gate)) after(46, function () { speak('yazeed_yalla', { pri: 1 }); });
          break;
        case 'checkpoint': Sound.sfx('checkpoint', { gain: 0.8 }); break;
        case 'freed':
          Sound.sfx('rope');
          after(12, function () { Sound.sfx('freed', { gain: 0.8 }); });
          if (e.look) { var sl = e.look; after(40, function () { speak(sl === 'shop_tea' ? 'shop_tea' : (sl === 'shop_cloth' ? 'shop_cloth' : 'shop_thanks'), { pri: 4, wait: true }); }); }
          else after(40, function () { speak('elder_thanks', { pri: 4, wait: true }); });
          break;
        case 'surrender':
          Sound.sfx('surrender', { gain: 0.7 });
          if (e.k === 'quartermaster') { speak('qm_surrender', { pri: 7, who: 'QUARTERMASTER' }); after(200, function () { speak('uncle_cheque', { pri: 3, wait: true, keep: true }); }); break; }
          if (e.k === 'tailor') { speak('tl_surrender', { pri: 7, wait: true }); break; }
          if (whoIs(e) === 'cmdr') { speak('cmdr_surrender', { pri: 7, who: 'COMMANDER' }); break; }      // (the mission ends before the Uncle could call)
          flags.surr = (flags.surr || 0) + 1;
          speak(flags.surr % 2 ? 'grunt_twice' : 'grunt_monday', { pri: 3, who: WHO[whoIs(e)] });
          break;
        case 'capture': Sound.sfx('coin'); break;
        // ---- the Souq
        case 'spice_burst':
          Sound.sfx('sack_burst', { pan: panOf(e.x) });
          break;
        case 'sneeze':
          if (e.who === 'p') {
            Sound.voice('yazeed_sneeze', { over: true, gain: 0.9 });
            if (!flags.sneezed) { flags.sneezed = 1; after(70, function () { speak('yazeed_chilli', { pri: 3, wait: true }); }); }
          } else if (e.who === 'boss') {
            Sound.voice('grunt_sneeze', { over: true, gain: 0.75, rate: 1.08, pan: panOf(e.x) });      // (the Tailor: dummies don't sneeze)
          } else {
            Sound.voice('grunt_sneeze', { over: true, gain: 0.5, rate: 0.92 + Math.random() * 0.2, pan: panOf(e.x) });
            if (!flags.eyes) { flags.eyes = 1; after(46, function () { speak('grunt_eyes', { pri: 3, who: WHO[e.k] || 'RIFLEMAN' }); }); }
          }
          break;
        case 'achoo': if (Math.random() < 0.6) Sound.voice('grunt_sneeze', { over: true, gain: 0.42, rate: 0.9 + Math.random() * 0.25, pan: panOf(e.x) }); break;
        case 'fumble': Sound.sfx('bounce', { gain: 0.6, rate: 0.8, pan: panOf(e.x) }); break;
        case 'bar_hit':
          if (e.how === 'shot') Sound.sfx(Math.random() < 0.7 ? 'thunk' : 'clang', { gain: 0.6, pan: panOf(e.x) });
          else Sound.sfx('smash_crate', { gain: 0.7, pan: panOf(e.x) });
          break;
        case 'bar_break':
          Sound.sfx('smash_crate', { pan: panOf(e.x) }); Sound.sfx('crash', { gain: 0.8, pan: panOf(e.x) }); buzz(40);
          if (!flags.wall) { flags.wall = 1; after(30, function () { speak('grunt_wall', { pri: 3, wait: true }); }); }
          break;
        // the Tailor
        case 'snip': Sound.sfx('throw', { gain: 0.6, rate: 1.25, pan: panOf(e.x) }); Sound.sfx('snip', { gain: 0.6, rate: 1.15, pan: panOf(e.x) }); break;
        case 'pins': Sound.sfx('pins', { pan: panOf(e.x) }); break;
        case 'tape': Sound.sfx('tape', { pan: panOf(e.x) }); break;
        case 'yank': Sound.sfx('tape', { gain: 0.8, rate: 1.45, pan: panOf(e.x) }); buzz(30); break;
        case 'shred':
          // a dummy shot: its clothes go, and the pins in them come back at you
          Sound.sfx('rip', { pan: panOf(e.x) });
          after(3, function () { Sound.sfx('pins', { gain: 0.8, rate: 1.15, pan: panOf(e.x) }); });
          // (he wails about it the first time nobody else is talking: once a fight, never over a line)
          if (!flags.tlSilk) after(24, function () { speak('tl_silk', { pri: 5 }); if (line && line.id === 'tl_silk') flags.tlSilk = 1; });
          break;
        case 'topple': Sound.sfx('clatter', { pan: panOf(e.x), rate: 0.9 + Math.random() * 0.2 }); break;
        case 'redress': Sound.sfx('whoosh', { gain: 0.45, rate: 1.35, pan: panOf(e.x) }); break;
        case 'cover': Sound.sfx('whoosh', { gain: 0.9 }); break;
        case 'uncover': Sound.sfx('whoosh', { gain: 0.8, rate: 1.2 }); break;
        case 'caught':
          Sound.voice('tl_ow', { over: true, gain: 0.9, pan: panOf(e.x) });
          if (e.n === 1) after(30, function () { speak('tl_dummy', { pri: 6, keep: true }); });      // (found out, he tries being a dummy)
          buzz(20);
          break;
        case 'tape_wind':
          Sound.sfx('tape', { gain: 0.45, rate: 1.4 + Math.random() * 0.3, pan: panOf(e.x) });
          if (!flags.tlWound) { flags.tlWound = 1; Sound.voice('tl_whoa', { over: true, gain: 0.85, pan: panOf(e.x) }); }
          break;
        case 'wrap_hop': Sound.sfx('jump', { gain: 0.35, rate: 1.3, pan: panOf(e.x) }); break;
        case 'boat': after(34, function () { speak('yazeed_boat', { pri: 1 }); }); break;
        case 'hint': if (HINTS[e.k]) hint(T(HINTS[e.k])); break;

        // ---- the coast road
        case 'horn': Sound.sfx(e.k === 'truck' ? 'horn_truck' : 'horn_shass', { pan: panOf(e.x) }); break;
        case 'car_wait': after(10, function () { if (sim.car && sim.car.st === 'wait') speak('salem_getin', { pri: 4 }); }); break;
        case 'mount':
          Sound.sfx('door_slam');
          if (!flags.drive) { flags.drive = 1; after(24, function () { speak('salem_drive', { pri: 4, wait: true }); }); after(300, function () { speak('uncle_guns', { pri: 3, wait: true, keep: true }); }); }
          break;
        case 'dismount': Sound.sfx('jump', { gain: 0.7 }); break;
        case 'hop': Sound.sfx('hop', { gain: 0.9 }); break;
        case 'car_land': Sound.sfx('car_land', { gain: clamp(e.v / 420, 0.35, 1) }); if (e.v > 260) buzz(20); break;
        case 'road_end': Sound.sfx('brake'); after(56, function () { speak('salem_out', { pri: 4, wait: true }); }); break;
        case 'panic':
          if (!flags.carLine && Math.random() < 0.5) { flags.carLine = 1; speak('grunt_car', { pri: 2, who: WHO[e.k] || 'RIFLEMAN' }); }
          else yelp(e);
          break;
        case 'gunner_down': yelp(e); break;
        case 'flip':
          Sound.sfx('crash', { pan: panOf(e.x) }); buzz(40);
          flags.flips = (flags.flips || 0) + 1;
          if (flags.flips === 2) after(30, function () { speak('salem_again', { pri: 3 }); });
          break;
        case 'truck_dead': if (e.how === 'crush') Sound.sfx('crash', { gain: 0.8, pan: panOf(e.x) }); break;
        case 'strike': Sound.sfx('strike', { gain: 0.9 }); speak('ann_strike', { pri: 7 }); break;
        case 'dive': Sound.sfx('dive', { pan: panOf(e.x) }); break;
        case 'smash': Sound.sfx(e.k === 'crate' ? 'smash_crate' : 'smash_bags', { pan: panOf(e.x) }); break;

        // ---- the battery
        case 'boss_intro':
          Sound.startMusic(false, sim.L.bossMusic || 'battery', 0.8);
          bossSays(e.k, 'intro');
          if (e.k === 'cgun') { Sound.sfx('rip', { gain: 0.6, pan: panOf(e.x) }); Sound.sfx('spinup', { gain: 0.9, rate: 0.7, pan: panOf(e.x) }); after(300, function () { speak('uncle_guns', { pri: 3, wait: true, keep: true }); }); }
          else if (e.k === 'launcher') {
            // the keep's gate opening, and the launcher's engine; the hint once it is out
            Sound.sfx('door_creak', { gain: 0.9, rate: 0.6, pan: panOf(e.x) }); after(24, function () { Sound.sfx('door_creak', { gain: 0.7, rate: 0.52, pan: panOf(e.x) }); });
            if (!flags.lnTip) { flags.lnTip = 1; after(150, function () { hint(T('Their missile launcher! Get it before the missile is up')); }); }
          }
          else after(420, function () { speak(e.k === 'roaster' ? 'uncle_coffee' : (e.k === 'tailor' ? 'uncle_spice' : 'uncle_drones'), { pri: 3, wait: true, keep: true }); });
          break;
        case 'boss_phase':
          if (e.k === 'tailor') Sound.sfx(e.n === 3 ? 'whoosh' : 'clatter', { pan: panOf(e.x), rate: 0.8 });      // (a spare dummy wheeled in; the sheets out)
          else Sound.sfx('part_off', { pan: panOf(e.x) });
          buzz(60);
          bossSays(e.k, 'phase' + e.n);
          break;
        case 'boss_dying': Sound.sfx(BOSSLINES[e.k || 'boat'].fall || 'boss_fall', { pan: panOf(e.x) }); break;
        case 'boss_dead':
          if (e.k === 'tailor') {
            // the dummies all going over at once, and the chillies they were stuffed with bursting out of them
            Sound.sfx('clatter'); Sound.sfx('sack_burst', { gain: 0.9, rate: 0.9 });
            after(7, function () { Sound.sfx('clatter', { rate: 0.85 }); }); after(15, function () { Sound.sfx('clatter', { rate: 1.12 }); });
          } else Sound.sfx('boom_big');
          buzz([60, 40, 140]); Sound.stopMusic(1.6);
          break;
        case 'bomb_drop': Sound.sfx('whistle', { gain: 0.8, pan: panOf(e.x) }); break;
        case 'launch': Sound.sfx('launch', { pan: panOf(e.x) }); break;
        case 'clear':
          Sound.jingle('complete');
          Render.setBanner(T('MISSION COMPLETE!'), '', 280);
          say(sim.L.lines && sim.L.lines.clear);
          break;
        case 'failsafe': flags.failsafe = (flags.failsafe || 0) + 1; break;

        // ---- Mocha
        case 'emerge': Sound.sfx('door_creak', { pan: panOf(e.x) }); break;
        case 'fling': Sound.sfx('throw', { gain: 0.6, rate: 1.15, pan: panOf(e.x) }); break;
        case 'swing': Sound.sfx('knife', { gain: 0.7, rate: 0.7, pan: panOf(e.x) }); if (e.hit) { Sound.sfx('clang', { gain: 0.8, pan: panOf(e.x) }); buzz(40); } break;
        case 'vent_hiss': Sound.sfx('hiss', { gain: 0.6, pan: panOf(e.x) }); break;
        case 'vent_blast': Sound.sfx('steam', { gain: 0.8, pan: panOf(e.x) }); break;
        case 'rspray': Sound.sfx('bean_spray', { gain: 0.9, pan: panOf(e.x) }); break;
        case 'rlob': Sound.sfx('pop', { gain: 0.9, pan: panOf(e.x) }); break;
        case 'steam_jet': Sound.sfx('steam', { pan: panOf(e.x) }); break;
        case 'pour': Sound.sfx('pour', { pan: panOf(e.x) }); break;
        case 'lunge': Sound.sfx('rev', { pan: panOf(e.x) }); buzz(30); break;
        case 'brake': Sound.sfx('brake', { gain: 0.8, pan: panOf(e.x) }); break;

        // ---- Taiz, by Apache
        case 'heli_ready':
          if (!flags.flyTip) { flags.flyTip = 1; after(30, function () { hint(T(coarse ? 'Left stick flies it. Right stick aims and fires the gun' : 'The arrows fly it. Hold FIRE and the gun aims itself')); }); }
          after(50, function () { speak('salem_drive', { pri: 4, who: 'SALEM' }); });
          break;
        // the opening: the Apache sets down in the street, Yazeed climbs in
        case 'landed':
          speak('salem_getin', { pri: 5, who: 'SALEM' });
          after(70, function () { if (sim.intro && sim.intro.st === 'wait') hint(T(coarse ? 'Left stick: walk to the Apache' : 'Arrows: walk to the Apache')); });
          break;
        case 'board':
          Sound.sfx('hop', { gain: 0.6 }); after(14, function () { Sound.sfx('door_slam', { gain: 0.45 }); }); speak('yazeed_yalla', { pri: 5, who: 'YAZEED' });
          Render.setHint('', 0); hintLine = null;
          break;
        case 'qanya':
          // «قنية سودا!»: the black jinn. One says it, and another says it after him
          speak('grunt_qanya', { pri: 4, who: 'RIFLEMAN' });
          after(14, function () { Sound.voice('grunt_qanya', { over: true, gain: 0.45, rate: 1.12, pan: panOf(e.x) }); });
          break;
        case 'scatter': Sound.voice('grunt_yelp', { over: true, gain: 0.5, rate: 1.15 + Math.random() * 0.2, pan: panOf(e.x) }); break;
        case 'emerge': Sound.sfx('door_creak', { gain: 0.7, pan: panOf(e.x) }); break;
        // out of a door on a roof or in the street, up through a hatch; a crate of drones opening, and one going up
        case 'enter': if (e.how === 'door') Sound.sfx('door_creak', { gain: 0.6, pan: panOf(e.x) }); else if (e.how === 'hatch') Sound.sfx('clang', { gain: 0.3, rate: 1.4, pan: panOf(e.x) }); break;
        // the people tied up on the roofs (22 Oct): a word the first time one is in the picture; the rope going down to him
        case 'captive': if (!flags.captiveTip) { flags.captiveTip = 1; after(20, function () { hint(T('Somebody is tied up on that roof! Hover low over him to lift him out')); }); } break;
        case 'rope_down': if (gt - (flags.ropeT || -99) > 40) { flags.ropeT = gt; Sound.sfx('rope', { gain: 0.45, rate: 1.25, pan: panOf(e.x) }); } break;
        case 'crate_open':
          Sound.sfx('clang', { gain: 0.4, rate: 0.85, pan: panOf(e.x) });
          if (!flags.crateTip) { flags.crateTip = 1; after(16, function () { hint(T('A crate of drones! Hit it before it sends them all')); }); }
          break;
        case 'drone_up': Sound.sfx('spinup', { gain: 0.45, rate: 1.5, pan: panOf(e.x) }); break;
        // the bosses' moments, the dawn and the landing
        case 'flak': Sound.sfx('heavy_shot', { gain: 0.75, rate: 0.7, pan: panOf(e.x) }); break;
        // the launcher: out of the keep, its crew's smoke, its missile away, the next one loaded; its missile cooking off
        case 'roll': Sound.sfx('rev', { gain: 0.8, rate: 0.7, pan: panOf(e.x) }); after(20, function () { Sound.sfx('engine', { gain: 0.5, rate: 0.6, pan: panOf(e.x) }); }); break;
        case 'smoke':
          Sound.sfx('hiss', { gain: 0.6, rate: 0.8, pan: panOf(e.x) }); Sound.sfx('pop', { gain: 0.4, rate: 0.7, pan: panOf(e.x) });
          if (!flags.smokeTip) { flags.smokeTip = 1; after(10, function () { hint(T('Smoke! Your rockets lose it in there. Use the gun')); }); }
          break;
        case 'big_launch': Sound.sfx('launch', { gain: 1, rate: 0.62, pan: panOf(e.x) }); Sound.sfx('boom_m', { gain: 0.6, rate: 0.7, pan: panOf(e.x) }); buzz(80); break;
        // the Castle Gun's barrels too hot to fire, after its sweep
        case 'overheat':
          Sound.sfx('hiss', { gain: 0.8, rate: 0.9, pan: panOf(e.x) }); Sound.sfx('steam', { gain: 0.6, pan: panOf(e.x) });
          if (!flags.coolTip) { flags.coolTip = 1; after(10, function () { hint(T('Its barrels are too hot to fire. Now!')); }); }
          break;
        // the launcher's count (a timed boss, Khaled 22 Oct): under way; the crew losing count and starting again; the last
        // ten seconds; nought; the missile away; and one of their drones going the wrong way
        case 'countdown':
          Sound.sfx('rlocked', { gain: 0.8, rate: 0.6 });
          if (!flags.countTip) { flags.countTip = 1; after(40, function () { hint(T('Wreck it before the count runs out')); }); }
          break;
        case 'lost_count': speak('grunt_count', { pri: 6, who: 'RIFLEMAN', wait: true, keep: true }); break;
        case 'recount': speak('cmdr_again', { pri: 6, who: 'COMMANDER', wait: true, keep: true }); Sound.sfx('pick_gren', { gain: 0.6 }); break;
        case 'count_tick': Sound.sfx('beep', { gain: e.n <= 3 ? 0.9 : 0.6, rate: e.n <= 3 ? 1.25 : 1 }); break;
        case 'ignite': Sound.sfx('rip', { gain: 0.9, rate: 0.5, pan: panOf(e.x) }); Sound.sfx('spinup', { gain: 1, rate: 0.45, pan: panOf(e.x) }); buzz(60); break;
        case 'got_away': after(40, function () { Sound.sfx('boom_m', { gain: 0.3, rate: 0.5 }); }); break;
        case 'oops': speak('grunt_face', { pri: 3, who: 'RIFLEMAN' }); break;
        case 'load': Sound.sfx('clatter', { gain: 0.45, rate: 0.8, pan: panOf(e.x) }); break;
        case 'cookoff': Sound.sfx('launch', { gain: 0.8, rate: 1.4, pan: panOf(e.x) }); break;
        case 'firework': Sound.sfx('pop', { gain: 0.9, rate: 0.9 }); Sound.sfx('boom_s', { gain: 0.5, rate: 1.35 }); break;
        // a man who has had enough, over the edge of his roof (now and then one of them says so)
        case 'leap': if (gt - (flags.leapT || -99) > 50) { flags.leapT = gt; Sound.voice('grunt_scream', { over: true, gain: 0.45, rate: 1.1 + Math.random() * 0.25, pan: panOf(e.x) }); } break;
        case 'dawn':
          after(90, function () { hint(T(coarse ? 'Dawn. Bring it down in the courtyard' : 'Dawn. Bring it down in the courtyard')); });
          after(30, function () { Sound.startMusic(false, sim.L.music, 0.5); });
          break;
        case 'touchdown': Sound.sfx('car_land', { gain: 0.6, rate: 0.8 }); after(20, function () { speak('yazeed_tea', { pri: 6, who: 'YAZEED' }); }); break;
        // the chase up the hillside road; an RPG; a sniper's laser; a mortar; a searchlight that has the Apache
        case 'chase': if (!flags.chaseTip) { flags.chaseTip = 1; after(20, function () { hint(T('After them! Their gunners shoot back')); }); } break;
        case 'truck_go': Sound.sfx('rev', { gain: 0.5, pan: panOf(e.x) }); break;
        case 'rpg_fire': Sound.sfx('launch', { gain: 0.8, rate: 1.15, pan: panOf(e.x) }); Sound.sfx('whoosh', { gain: 0.5, pan: panOf(e.x) }); break;
        case 'snipe_aim':
          Sound.sfx('beep', { gain: 0.45, rate: 0.6, pan: panOf(e.x) });
          if (!flags.snipeTip) { flags.snipeTip = 1; hint(T('A sniper! Shoot him while he is at the window')); }
          break;
        case 'mortar_load': Sound.sfx('thunk', { gain: 0.7, pan: panOf(e.x) }); break;
        case 'mortar_fire':
          Sound.sfx('heavy_shot', { gain: 0.5, rate: 0.6, pan: panOf(e.x) }); after(34, function () { Sound.sfx('whistle', { gain: 0.5, rate: 0.85 }); });
          if (!flags.mortarTip) { flags.mortarTip = 1; after(20, function () { hint(T('Mortar! Get out of the circle before it lands')); }); }
          break;
        case 'spotted':
          Sound.sfx('lock', { gain: 0.6, rate: 0.8 });
          if (!flags.spotTip) { flags.spotTip = 1; hint(T('A searchlight has you: their guns are quicker. Shoot it out')); }
          break;
        case 'rocket': Sound.sfx('launch', { gain: 0.7, rate: 1.45, pan: panOf(e.x) }); break;
        case 'flare':
          Sound.sfx('pop', { gain: 0.8, rate: 0.7 }); after(4, function () { Sound.sfx('pop', { gain: 0.6, rate: 0.8 }); }); after(8, function () { Sound.sfx('pop', { gain: 0.5, rate: 0.9 }); });
          Sound.sfx('hiss', { gain: 0.35, rate: 1.4 });
          break;
        case 'lock_on':
          if (!flags.samTip) { flags.samTip = 1; hint(T('Missile lock! Drop FLARES before it fires')); }
          break;
        // the lock-on: a beat that quickens and climbs, then one long tone, then the launch
        case 'lock':
          if (e.solid) Sound.sfx('locktone', { gain: 0.75 });
          else Sound.sfx('beep', { gain: 0.6 + 0.04 * e.n, rate: 1 + e.n * 0.05 });
          break;
        case 'sam_launch': Sound.sfx('launch', { gain: 0.9, pan: panOf(e.x) }); Sound.sfx('whistle', { gain: 0.45, rate: 1.4, pan: panOf(e.x) }); break;
        case 'decoyed': Sound.sfx('ui_move', { gain: 0.5, rate: 0.8 }); break;
        // its rounds bursting where they land; the rocket pod finding its target, and locked
        case 'hedp': Sound.sfx('hedp', { gain: 0.3, rate: 0.9 + Math.random() * 0.2, pan: panOf(e.x) }); break;
        case 'rlock': Sound.sfx('rbeep', { gain: 0.42, rate: 1 + e.n * 0.12 }); break;
        case 'rlocked':
          Sound.sfx('rlocked', { gain: 0.5 });
          if (!flags.rlockTip && sim.p.grenades > 0) { flags.rlockTip = 1; after(10, function () { hint(T(coarse ? 'Locked on! Tap ROCKETS to send one' : 'Locked on! C sends a rocket')); }); }
          break;
        case 'scrape': Sound.sfx('clang', { gain: 0.7, rate: 0.7 }); buzz(20); break;
        case 'heli_down': Sound.sfx('boss_fall', { gain: 0.8, rate: 1.35 }); break;
      }
      if (e.t === 'tell' && e.k === 'aa' && !flags.aaTip) { flags.aaTip = 1; after(20, function () { hint(T('ROCKETS make short work of the big guns')); }); }
    }
  }
  // what each boss's moments sound like: lines as [ticks from now, line, priority, who]
  var BOSSLINES = {
    boat: { intro: [[34, 'yazeed_flying', 5], [150, 'cmdr_behold', 6, 'COMMANDER']], phase2: [[40, 'cmdr_minor', 6, 'COMMANDER']], phase3: [[40, 'cmdr_insured', 6, 'COMMANDER']] },
    roaster: { intro: [[40, 'yazeed_roaster', 5], [150, 'qm_behold', 6, 'QUARTERMASTER']], phase2: [[40, 'qm_chimney', 6, 'QUARTERMASTER']], phase3: [[40, 'qm_dark', 6, 'QUARTERMASTER']], fall: 'boss_fall' },
    // (the Tailor first, then Yazeed, then the Uncle on the radio at 420: one after another, none of them cut short)
    tailor: { intro: [[24, 'tl_welcome', 6], [260, 'yazeed_coat', 5]], phase2: [[40, 'tl_more', 6]], phase3: [[30, 'tl_cover', 6]], fall: 'tape' },
    // (Taiz's: the Castle Gun, heard rather than spoken; and the launcher, the Commander's new pride, with his old lines)
    cgun: { intro: [[30, 'grunt_alarm', 4, 'RIFLEMAN']] },
    launcher: { intro: [[70, 'cmdr_behold', 6, 'COMMANDER']], phase2: [[40, 'cmdr_minor', 6, 'COMMANDER']], phase3: [[40, 'cmdr_insured', 6, 'COMMANDER']] }
  };
  function bossSays(k, moment) {
    (BOSSLINES[k || 'boat'][moment] || []).forEach(function (q) { after(q[0], function () { speak(q[1], { pri: q[2], wait: true, keep: true, who: q[3] }); }); });
  }
  function whoIs(e) {
    if (e.id != null) for (var i = 0; i < sim.enemies.length; i++) if (sim.enemies[i].id === e.id) return sim.enemies[i].k;
    // the alarm does not say who raised it: take the nearest man to where it came from
    var best = 'rifle', bd = 1e9;
    for (var j = 0; j < sim.enemies.length; j++) { var m = sim.enemies[j], dd = Math.abs(m.x - e.x) + Math.abs(m.y - e.y); if (m.alive && dd < bd) { bd = dd; best = m.k; } }
    return best;
  }
  // a gate that opens on something else happening (Salem pulling up, say) gets no word from Yazeed
  function gateQuiet(id) { var g = sim.L.gates; for (var i = 0; i < g.length; i++) if (g[i].id === id) return !!g[i].quiet; return false; }
  function machines() {
    var s = sim, c = s.car, eng = 0, rate = 1, b = s.boss, rot = 0, rr = 1;
    if (c && (c.st === 'drive' || c.st === 'stop') && s.mode === 'drive' && !s.p.dead) { eng = 0.55; rate = 0.78 + 0.5 * clamp(c.vx / Sim.D.V_FAST, 0, 1) + (c.air ? 0.12 : 0); }
    else if (c && (c.st === 'arrive' || c.st === 'wait') && Sim.onScreen(s, c.x, 60)) { eng = 0.32; rate = c.st === 'arrive' ? 0.72 + 0.4 * clamp(c.vx / 250, 0, 1) : 0.7; }
    if (b && b.kind === 'roaster' && b.st !== 'dead') { eng = b.st === 'lunge' || b.st === 'lungetell' ? 0.6 : 0.36; rate = b.st === 'lunge' ? 0.9 : (b.st === 'lungetell' ? 0.8 : 0.5); }
    if (eng > 0) Sound.loop('engine', true, { gain: eng, rate: Math.round(rate * 50) / 50 }); else Sound.loop('engine', false);
    // the Tailor's stands squeak on their castors as they are wheeled about
    var tl = s.tailor, rolling = 0;
    if (tl && Sim.onScreen(s, s.L.tailor.slots[2], 160)) for (var fi = 0; fi < tl.figs.length; fi++) { var fg = tl.figs[fi]; if ((tl.shuffle && fg.x !== fg.x1) || fg.roll >= 0) rolling++; }
    if (rolling) Sound.loop('creak', true, { gain: 0.3 + 0.12 * Math.min(2, rolling), rate: 1.5 }); else Sound.loop('creak', false);
    if (b && b.kind === 'boat' && b.st !== 'dead') { rot = b.st === 'intro' ? 0.15 + 0.35 * Math.min(1, b.stT / 100) : 0.5; rr = b.st === 'dying' ? 0.76 : 1 + 0.04 * (b.phase - 1); }
    if (rot > 0) Sound.loop('rotor', true, { gain: rot, rate: rr }); else Sound.loop('rotor', false);
    // (Taiz: the Apache's rotor, a little quicker when it is flown hard, slowing as it comes down)
    var hl = s.heli, hg = 0, hrr = 1;
    if (hl && s.mode === 'fly' && hl.st !== 'wreck' && hl.st !== 'off') { hg = hl.st === 'down' ? 0.3 : 0.5; hrr = hl.st === 'down' ? 0.8 : 0.94 + 0.1 * Math.min(1, (Math.abs(hl.vx) + Math.abs(hl.vy)) / 170); hrr = Math.round(hrr * 50) / 50; }
    // (in the opening: heard coming before it is seen, and idling in the street)
    if (hl && hl.st === 'arrive') hg = 0.5 * clamp((hl.x + 260) / 380, 0.1, 1);
    if (hl && (hl.st === 'landed' || (s.intro && s.intro.st === 'board'))) { hg = 0.42; hrr = 0.84; }
    if (hl && hl.st === 'off' && s.intro && s.intro.t > 40) { hg = 0.5 * clamp((s.intro.t - 40) / 50, 0, 1) * 0.3; hrr = 0.94; }
    if (hg > 0) Sound.loop('heli', true, { gain: hg, rate: hrr }); else Sound.loop('heli', false);
  }
  // Taiz: the FLARES button pulses while a missile man has the Apache (or a missile is on its way) and the flares are ready
  var alertOn = false;
  function flareAlert() {
    var h = sim && sim.mode === 'fly' ? sim.heli : null, on = false;
    if (h && h.flareCd <= 0 && sim.status === 'play' && !sim.p.dead) {
      on = !!sim.locking;
      for (var i = 0; !on && i < sim.missiles.length; i++) if (!sim.missiles[i].gone && !sim.missiles[i].decoy) on = true;
    }
    if (on !== alertOn) { alertOn = on; bJump.classList.toggle('alert', on); }
  }
  function direct() {
    for (var i = timers.length - 1; i >= 0; i--) if (gt >= timers[i].at) { var f = timers[i].fn; timers.splice(i, 1); f(); }
    if (line && gt >= line.until) line = null;
    if (!line && queue.length) { var q = queue.shift(); if (gt - q.at < 200 || q.o.keep) speak(q.id, q.o); }      // (unless its moment has passed: a story line's never does)
    if (hintLine && gt >= hintLine.until) hintLine = null;
    // a mission's own talk (Ibb's screens): its next line, when nobody else is saying anything
    if (!line && !queue.length && sim.status === 'play' && !sim.p.dead) { var tk = Render.talk(sim); if (tk) speak(tk.id, tk.o); }
    // nobody has shown the lock yet: say so once, after a good while of holding the trigger down by hand
    if (!flags.lockTip && prefs.scheme === 'hold' && geo.G && geo.G.shown && Input.lockCount() === 0 && Input.heldTicks() > 420 && !hintLine && sim.status === 'play') {
      flags.lockTip = 1; hint(T('Slide your thumb up off FIRE to lock it on'));
    }
    // a phone holding the game to 30 frames a second (iOS does it to every page in Low Power Mode; Android's battery saver
    // can): say so once on this device, after six seconds of it, when no other tip is up (Khaled, 20 Oct)
    if (!prefs.fpsTip && coarse && P.slow > 6000 && !hintLine && sim.status === 'play') {
      prefs.fpsTip = true; savePrefs();
      hint(T(isIOS() ? 'Low Power Mode on? Turning it off makes the game smoother' : 'Battery saver on? Turning it off makes the game smoother'));
    }
    if (gt >= (flags.gullAt || 500)) { flags.gullAt = gt + 700 + Math.floor(Math.random() * 900); if (sim.status === 'play' && !sim.L.zones[sim.zone].indoor) Sound.sfx(sim.L.birds || 'gull', { gain: 0.22, pan: Math.random() * 1.4 - 0.7 }); }
  }
  // ------------------------------------------------------------------ the loop
  var lastT = 0, acc = 0, frameNo = 0;
  function tick() {
    gt++;
    var inp = Input.sample(), vv = viewOf(sim.L);
    inp.viewW = vv[0]; inp.viewH = vv[1];
    inp.lanes = geo.lanes;
    Sim.step(sim, inp);
    flareAlert();
    var ev = sim.events;
    if (ev.length) { Render.onEvents(sim, ev); react(ev); }
    machines();
    direct();
    used[prefs.scheme === 'auto' ? 'auto' : 'hold']++;
    if (sim.zone > prefs.prog[cur].reached) { prefs.prog[cur].reached = sim.zone; savePrefs(); }
    if (sim.status === 'over') gameOver();
    else if (sim.status === 'clear' && sim.clearT > 335) showResults();
  }
  function frame(t) {
    window.requestAnimationFrame(frame);
    if (window.__m1.frozen) { lastT = t; return; }          // (tests borrow the picture to draw frames of their own)
    var d = t - lastT; lastT = t;
    if (!(d > 0) || d > 2000) d = STEP_MS;
    meter(d);
    frameNo++;
    if (state === 'play') {
      if (d > 250) d = 250;
      var m = Math.round(d / M.snap);
      if (m >= 1 && Math.abs(d - m * M.snap) < M.snap * 0.3) d = m * M.snap;
      acc += d;
      var n = 0;
      while (acc >= STEP_MS * 0.6 && n < 4 && state === 'play') { tick(); acc -= STEP_MS; n++; }
      if (acc > STEP_MS) { P.slips += Math.floor(acc / STEP_MS); acc = 0; }
      if (fade.dir) fadeStep();
      draw(true);
    } else if (menuUp()) {
      macc += Math.min(d, 100);
      var k = 0;
      while (macc >= STEP_MS * 0.6 && k < 4) { menuTick(); macc -= STEP_MS; k++; }
      if (macc > STEP_MS) macc = 0;
      draw(true);
    } else if ((frameNo & 3) === 0 || fade.dir) { if (fade.dir) fadeStep(); draw(false); }
  }
  function draw() {
    var screen = state === 'opts' || state === 'brief' ? optsFrom : state;
    setZoom(zoomNow());
    if (screen === 'home' && backdrop) {
      Render.draw(backdrop, { paused: true, fps: null, lock: false, auto: false, sub: null, overlay: false, caps: true, noHud: true, dim: 0 });
      if (quick) Menu.gate({ t: homeT, coarse: coarse, calm: calm, wait: quickWait });
      else {
        placeSocial(geo.cx0, geo.cy0, geo.scale);
        Menu.home({ t: homeT, coarse: coarse, calm: calm, woke: woke, build: BUILD, social: true, hot: socialHot, cleared: clearedCount(), total: missionCount(), best: bestSum() ? num(bestSum()) : null });
      }
    } else if (screen === 'map') {
      Menu.map({ t: mapT, cam: mv.cam, camY: mv.camY, sel: mv.sel, prog: prefs.prog, last: prefs.last, reveal: mv.rv, calm: calm });
    } else {
      var s = sim || backdrop;
      if (!s) return;
      var over = state !== 'play';
      Render.draw(s, {
        paused: over, fps: prefs.dev ? M.fps : null, lock: Input.isLocked(), auto: prefs.scheme === 'auto',
        sub: state === 'play' && line && line.text ? line : null, overlay: false, caps: true,
        noHud: false, dim: over ? 0.6 : 0
      });
    }
    if (state === 'opts' || state === 'brief') Render.clear('rgba(8,10,24,0.55)');
    if (fade.a > 0) Render.clear('rgba(4,5,12,' + fade.a.toFixed(3) + ')');
    var hc = Z !== 1 ? Render.hudCanvas() : null;
    if (hc) bandA += ((underBand() ? BAND_DIM : 1) - bandA) * 0.25;
    if (!geo.fast && hx) {
      if (Z === 1) hx.drawImage(lo, 0, 0, W, H, 0, 0, hi.width, hi.height);
      else { hx.drawImage(lo, 0, 0, hi.width / geo.nz, hi.height / geo.nz, 0, 0, hi.width, hi.height); if (hc) layHud(hx, hc, hi.width / W, hi.height / H); }
    } else if (hc) layHud(Render.ctx(), hc, Z, Z);      // (the plain enlarging: the HUD laid on the world as it is)
  }
  // flying: the HUD has a canvas of its own, laid on the picture. While the Apache is up under its top band (the clock, the
  // score, the lives) that band is laid on faint, so the Apache can be seen through it; it comes back as the Apache leaves.
  var BAND = 38, BAND_DIM = 0.35, bandA = 1;
  function underBand() {
    var s = sim, h = s && s.heli;
    if (state !== 'play' || !h || h.st !== 'fly' || !s.L || !s.L.fly || !s.viewH) return false;
    return (h.y - 22 - s.camY) / s.viewH * H < BAND;          // (its rotor, in the HUD's own units)
  }
  function layHud(g, hc, kx, ky) {
    if (bandA > 0.99) { g.drawImage(hc, 0, 0, W, H, 0, 0, W * kx, H * ky); return; }
    g.globalAlpha = bandA; g.drawImage(hc, 0, 0, W, BAND, 0, 0, W * kx, BAND * ky);
    g.globalAlpha = 1; g.drawImage(hc, 0, BAND, W, H - BAND, 0, BAND * ky, W * kx, (H - BAND) * ky);
  }

  // ------------------------------------------------------------------ states
  function setState(st) {
    state = st;
    for (var k in panels) panels[k].hidden = k !== st;
    app.setAttribute('data-screen', st === 'opts' || st === 'brief' ? optsFrom : st);
    app.classList.toggle('has-panel', st !== 'play');
    app.setAttribute('data-state', st);
    var fly = !!(sim && sim.L && sim.L.fly), was = app.classList.contains('is-fly');
    app.classList.toggle('is-fly', fly);         // (Taiz: the buttons say FLARES and ROCKETS, and an aim stick takes FIRE's place)
    Input.setMode(fly ? 'fly' : 'foot');
    if (fly !== was && booted) layout();          // (and the thumbs are laid out for it)
    if (st !== 'play' && alertOn) { alertOn = false; bJump.classList.remove('alert'); }
    Input.setEnabled(st === 'play');
    var p = panels[st], first = p && p.querySelector('.go');
    if (first && !coarse) { try { first.focus({ preventScroll: true }); } catch (e) {} }
    else if (st === 'play' && document.activeElement && document.activeElement.blur) { try { document.activeElement.blur(); } catch (e) {} }
    menuMusic();
    turnHint();
  }
  // the menus' music: the theme on the home screen (and over its options), the march on the map (and over its
  // briefings and options). Before the first tap this only says which one to start when sound is allowed.
  function menuMusic() { if (menuUp()) Sound.menu(onMap() ? 'map' : 'title'); }
  // The home screen the way an arcade cabinet does it: until the first tap the picture only says TAP TO START, and
  // that tap wakes the sound (a browser allows none sooner) and brings the theme in; Start and Options appear then.
  var woke = false;
  // The steps before a mission, each counted once a visit as `menu_step` (game-performance-R4; Khaled: now, 22 Oct):
  // the title tapped (sound on, or the ?play screen's one tap), Start, the map, a mission card picked, the briefings.
  // Players see nothing of it. `link` says whether the visit came in on a ?play link.
  var stepsSeen = {}, cameOnPlay = /(?:^|[?&])play(?:[=&]|$)/.test(window.location.search || '');
  function menuStep(name, extra) {
    if (stepsSeen[name]) return;
    stepsSeen[name] = true;
    var p = { step: name, link: cameOnPlay ? 'play' : 'plain' };
    if (extra) for (var k in extra) p[k] = extra[k];
    if (window.HM) HM.track('menu_step', p);
  }
  function wakeUp() {
    if (woke) return;
    woke = true;
    menuStep('title');
    Sound.unlock(); menuMusic(); Sound.sfx('ui_select', { gain: 0.6 });
    panels.home.querySelector('.acts').hidden = false;
    if (state === 'home' && !coarse) { var b = el('bStart'); try { b.focus({ preventScroll: true }); } catch (e) {} }
  }
  // The ad's link (?play): someone new skips the title, the map and the briefing. They see the first mission's own
  // picture with TAP TO PLAY (and, holding the phone upright, a note the right way up to turn it), and that one tap,
  // which a browser needs before any sound, starts the mission. Someone who has played before goes to the map
  // instead. (Khaled, 21 Oct)
  var quick = /(?:^|[?&])play(?:[=&]|$)/.test(window.location.search || ''), quickWait = false, quickGoing = false, quickCam = 0;
  function firstTime() {
    return CAMPAIGN.every(function (m) { var p = prefs.prog[m.id]; return !p || (!p.runs && !p.cleared && !p.reached); });
  }
  function quickGo() {
    if (!quick || quickGoing) return;
    quickGoing = true;
    menuStep('title');
    Sound.unlock();
    Sound.want(musicFor('m1'));
    var ready = function () { return Sound.hasFailed() || (Sound.isReady() && Sound.hasTrack(musicFor('m1')[0])); };
    var go = function () {
      quickWait = false;
      transit(function () { quick = false; app.classList.remove('is-quick'); turnHint(); begin('m1', 0); });
    };
    if (ready()) { go(); return; }
    // the sound is still arriving: give it a moment rather than start in silence
    quickWait = true;
    var t0 = Date.now(), iv = window.setInterval(function () {
      if (ready() || Date.now() - t0 > 4000) { window.clearInterval(iv); go(); }
    }, 60);
  }
  // the note to turn the phone: only on the way in from the ad, only while the picture lies on its side. Upright, the
  // picture's left edge is the top of the screen. The note sits in a gap clear of the prompt in the middle and the
  // thumbs: below the prompt, above the buttons, where the picture is only beach; failing that above it, below the
  // stick (over Yazeed); on a screen too short for either, low down as before.
  function turnHint() {
    var h = el('turn'); if (!h) return;
    var on = quick && state === 'home' && geo.rot;
    if (on) { el('turnA').textContent = T('Turn your phone sideways'); el('turnB').textContent = T(coarse ? 'then tap to play' : 'then press any key'); }
    h.hidden = !on;
    if (!on || !geo.G || !geo.cw) return;
    var tw = 96;
    try { tw = Render.textW('b_org', T(coarse ? 'TAP TO PLAY' : 'PRESS ANY KEY TO PLAY')); } catch (e) {}
    var k = geo.cw / W, mid = geo.cx0 + Math.floor(W / 2) * k, half = tw / 2 * k, G = geo.G, need = h.offsetHeight + 16;
    var below = [mid + half, G.jump.x - G.jump.r], above = [G.stick.x + G.stick.r, mid - half];
    var gap = below[1] - below[0] >= need ? below : (above[1] - above[0] >= need ? above : null);
    h.classList.toggle('mid', !!gap);
    h.style.top = gap ? Math.round((gap[0] + gap[1]) / 2) + 'px' : '';
  }
  // straight to the map: the march waits for the first touch, as sound always must
  function soundOnFirstTouch() {
    var once = function () {
      document.removeEventListener('pointerup', once, true); document.removeEventListener('keydown', once, true);
      Sound.unlock(); menuMusic();
    };
    document.addEventListener('pointerup', once, true); document.addEventListener('keydown', once, true);
  }
  // a mission from the start, or from one of its checkpoints (id: which one; it stays the one being played until
  // another is started; zone: the checkpoint, 0 for the start)
  function begin(id, zone) {
    if (id && LEVELS[id]) cur = id;
    var L = LEVELS[cur];
    Sound.want(musicFor(cur));                // (its music, if it is not in hand already; the last mission's is let go)
    run = { from: Math.max(0, Math.min(L.zones.length - 1, zone | 0)), skipped: false };
    Sound.loopsOff();
    prefs.prog[cur].runs++; savePrefs();
    sim = Sim.create(L, { viewW: viewOf(L)[0], viewH: viewOf(L)[1], seed: 20261012, lanes: geo.lanes, zone: run.from });
    Render.reset();
    gt = 0; timers = []; queue = []; line = null; hintLine = null; flags = {}; used = { hold: 0, auto: 0 }; acc = 0;
    resetPlayMeter();
    setState('play');
    if (window.HM) HM.track('mission_start', { mission: cur, from_zone: run.from, from_checkpoint: run.from > 0, run_number: prefs.prog[cur].runs });
    Render.setBanner(T('MISSION START!'), run.from ? T(L.zones[run.from].name).toUpperCase() : T(L.banner), 170);
    Sound.startMusic(true, L.music);
    Sound.sea(!!L.sea);
    // (from a checkpoint, only the announcer: Yazeed's first words belong to the start)
    say(L.lines && L.lines.start && (run.from ? L.lines.start.slice(0, 1) : L.lines.start));
    keepAwake();
  }
  // the next checkpoint, straight away (from the pause menu): the score, the clock and the lives come along
  function skipAhead() {
    if (state !== 'pause' || !sim || sim.status !== 'play') return;
    var z = sim.zone + 1, L = sim.L;
    if (z >= L.zones.length) return;
    Sound.unlock(); Sound.pause(false); Sound.loopsOff();
    run.skipped = true;
    if (window.HM) HM.track('skip_ahead', HM.where(sim, cur));
    sim = Sim.create(L, { zone: z, score: sim.score, time: sim.time, stats: sim.stats, viewW: viewOf(L)[0], viewH: viewOf(L)[1], seed: (sim.tick * 7919 + 101) >>> 0, radio: sim.radio, lanes: geo.lanes, lives: sim.p.lives });
    Render.reset();
    timers = []; queue = []; line = null; hintLine = null; acc = 0; flags.yelpAt = -99;
    Sound.sfx('checkpoint', { gain: 0.8 });
    setState('play');
    Render.setBanner(T('SKIPPED AHEAD'), T(L.zones[z].name).toUpperCase(), 130);
    keepAwake();
  }
  // the music a mission plays: its stage theme and its boss's
  function musicFor(id) { var L = LEVELS[id]; return L ? [L.music || 'strait', L.bossMusic || 'battery'].concat(L.speech ? ['speech:' + id] : []) : []; }
  // a mission's card on the map: its music is fetched once the card has been looked at for a moment (not while the map
  // is being run through), so it is in hand by the time Start is pressed
  var wantT = 0;
  function wantSoon(id) {
    window.clearTimeout(wantT);
    if (!LEVELS[id]) return;
    wantT = window.setTimeout(function () { if (mv.sel === id && state === 'map') Sound.want(musicFor(id)); }, 500);
  }
  // its place in a sentence: "the battery", "Container beach"
  function zoneWords(L, z) { var n = L.zones[z].name; return Lang.rtl() ? T(n) : (/^The /.test(n) ? 'the ' + n.slice(4) : n); }
  // lines spoken at set moments: [[ticks from now, line, priority], ...]
  function say(list) { (list || []).forEach(function (q) { after(q[0], function () { speak(q[1], { pri: q[2] }); }); }); }
  function bestSum() { var t = 0; CAMPAIGN.forEach(function (m) { var b = prefs.prog[m.id].best; if (b) t += b.total; }); return t; }
  // a mission from the map: the picture goes dark, and the mission starts once the sound is ready (or has had its chance).
  // skip: from the card's button, which may also skip ahead to a mission whose road is not open yet (if it is built)
  function play(id, skip) {
    var m = Menu.mission(id);
    if (fade.dir > 0 || !m || !m.built || !(playable(id) || (skip && skippable(id)))) return;
    Sound.unlock();
    Sound.sfx('ui_select');
    Sound.stopMusic(0.5);                     // the march goes as the picture goes dark
    var from = prefs.dev ? (fromSel[id] || 0) : 0;
    var b = el('bPlay'), go = function () { transit(function () { begin(id, from); }); };
    Sound.want(musicFor(id));
    var ready = function () { return Sound.hasFailed() || (Sound.isReady() && Sound.hasTrack(musicFor(id)[0])); };
    if (ready()) { go(); return; }
    // the sound is still arriving: give it a moment rather than start in silence
    b.setAttribute('aria-busy', 'true'); b.textContent = T('Loading sound');
    var t0 = Date.now(), iv = window.setInterval(function () {
      if (ready() || Date.now() - t0 > 4000) {
        window.clearInterval(iv); b.removeAttribute('aria-busy'); card();
        if (state === 'map') go();
      }
    }, 60);
  }
  function pause() {
    if (state !== 'play') return;
    fillReport();
    var sk = el('bSkip'), z = sim ? sim.zone + 1 : 0;
    sk.hidden = !sim || sim.status !== 'play' || z >= sim.L.zones.length;
    if (!sk.hidden) sk.textContent = T('Skip to {0}', [zoneWords(sim.L, z)]);
    setState('pause');
    Sound.pause(true);
  }
  function resume() {
    if (state !== 'pause') return;
    Sound.unlock(); Sound.pause(false);
    acc = 0;
    setState('play');
    keepAwake();
  }
  function togglePause() { if (state === 'play') pause(); else if (state === 'pause') resume(); }
  function gameOver() {
    Sound.stopMusic(0.9); Sound.loopsOff();
    // (in Arabic the zone's own name can be either gender, so the sentence leads with منطقة, the zone)
    var zn = T(sim.L.zones[sim.zone].name);
    el('overZone').textContent = Lang.has('the zone {0}') ? T('the zone {0}', [zn]) : zn;
    if (window.HM) HM.track('game_over', HM.where(sim, cur));
    setState('over');
    countdown();
  }
  // the continue countdown: ten seconds to press Continue, a tick each second, and at nought the mission ends and the
  // map comes back. It waits while the page is out of sight. (Khaled, 19 Oct)
  var cd = { left: 0, wait: 0, shown: -1, beat: 0, coin: -1, raf: 0, last: 0, done: false };
  // the dial is drawn in pixels on a 64x64 canvas: a ring of ten blocks that drains, the number in the middle, and on
  // Continue a coin that drops into a slot
  var DIGITS = ['01110100011001110101110011000101110', '00100011000010000100001000010001110', '01110100010000100010001000100011111',
    '11111000100010000010000011000101110', '00010001100101010010111110001000010', '11111100001111000001000011000101110',
    '00110010001000011110100011000101110', '11111000010001000100010000100001000', '01110100011000101110100011000101110',
    '01110100011000101111000010001001100'];
  var DIAL = { gold: '#ffc22e', goldHi: '#ffe08a', goldLo: '#5a2c00', red: '#ff5a3c', redHi: '#ffa08a', redLo: '#5a1400', dim: '#3c4278', dimLo: '#232750', slot: '#04050c' };
  function countdown() {
    if (cd.raf) window.cancelAnimationFrame(cd.raf);
    cd.left = 10; cd.wait = 0.6; cd.shown = -1; cd.beat = 0; cd.coin = -1; cd.done = false; cd.last = 0;
    panels.over.classList.remove('urgent', 'ended', 'paid');
    el('hOver').textContent = T('Continue?');
    var k = el('overKept'), b = document.createElement('b');
    k.textContent = T('Score kept') + ' '; b.textContent = num(sim.zoneScore || 0); k.appendChild(b);
    el('bContinue').disabled = false; el('bQuit2').disabled = false;
    cd.raf = window.requestAnimationFrame(countFrame);
  }
  function countFrame(ts) {
    cd.raf = 0;
    if (state !== 'over') return;
    var dt = cd.last ? Math.min(0.1, (ts - cd.last) / 1000) : 0;
    cd.last = ts;
    if (cd.coin >= 0) {
      var c0 = cd.coin; cd.coin += dt;
      if (c0 < 0.5 && cd.coin >= 0.5) Sound.sfx('coin', { gain: 1 });
      if (cd.coin >= 1.05) { dialDraw(); carryOn(); return; }
    } else if (!cd.done) {
      if (cd.wait > 0) cd.wait -= dt;      // a breath after the fall before the clock starts
      else cd.left -= dt;
      if (cd.left <= 0) {
        cd.left = 0; cd.done = true;
        panels.over.classList.remove('urgent'); panels.over.classList.add('ended');
        el('hOver').textContent = T('GAME OVER');
        el('bContinue').disabled = true; el('bQuit2').disabled = true;
        Sound.sfx('life', { gain: 0.8 }); buzz([80, 60, 160]);
        window.setTimeout(function () { if (state === 'over' && cd.done) transit(function () { toMap(); }); }, 1800);
      } else {
        var n = Math.max(0, Math.ceil(cd.left) - 1);
        if (n !== cd.shown) {
          cd.shown = n; cd.beat = 0.14;
          panels.over.classList.toggle('urgent', n <= 3);
          Sound.sfx('tick', { gain: n <= 3 ? 1 : 0.6, rate: n <= 3 ? 1.25 : 1 });
          if (n <= 3) buzz([25]);
        }
      }
    }
    if (cd.beat > 0) cd.beat -= dt;
    dialDraw();
    cd.raf = window.requestAnimationFrame(countFrame);
  }
  // Continue: the clock stops, a coin drops into the slot, the ring fills back up, and the run carries on
  function coinIn() {
    if (state !== 'over' || cd.done || cd.coin >= 0) return;
    Sound.unlock(); Sound.sfx('ui_select');
    cd.coin = 0;
    panels.over.classList.remove('urgent'); panels.over.classList.add('paid');
    el('bContinue').disabled = true; el('bQuit2').disabled = true;
    if (!cd.raf) cd.raf = window.requestAnimationFrame(countFrame);
  }
  function dialDraw() {
    var cv = el('overDial'), g = cv.getContext('2d'), x, y;
    g.clearRect(0, 0, 64, 64);
    var red = !cd.done && cd.coin < 0 && cd.shown >= 0 && cd.shown <= 3, end = cd.done;
    var lit = red ? DIAL.red : DIAL.gold, litHi = red ? DIAL.redHi : DIAL.goldHi, lo = red ? DIAL.redLo : DIAL.goldLo;
    // how much of the ring is lit: the time left, or while the coin goes in, filling back up
    var frac = end ? 0 : cd.left / 10;
    if (cd.coin >= 0) frac = cd.coin < 0.6 ? cd.left / 10 : Math.min(1, cd.left / 10 + (cd.coin - 0.6) / 0.35);
    for (y = 0; y < 64; y++) for (x = 0; x < 64; x++) {
      var dx = x - 31.5, dy = y - 31.5, r = Math.sqrt(dx * dx + dy * dy);
      if (r < 24.5 || r > 30.5) continue;
      var a = Math.atan2(dx, -dy) / (Math.PI * 2); if (a < 0) a += 1;
      var f = a * 10 - Math.floor(a * 10);
      if (f < 0.07 || f > 0.93) continue;           // the gaps between the ten blocks
      var on = a < frac;
      g.fillStyle = on ? (r > 29.5 ? lo : (r < 26 ? litHi : lit)) : (r > 29.5 ? DIAL.dimLo : DIAL.dim);
      g.fillRect(x, y, 1, 1);
    }
    if (cd.coin >= 0) { coinDraw(g); return; }
    var d = cd.done ? 0 : Math.max(0, cd.shown);
    var sc = cd.beat > 0 ? 5 : 4, w = 5 * sc, h = 7 * sc, ox = Math.round(32 - w / 2), oy = Math.round(32 - h / 2);
    var ink = end || red ? DIAL.red : DIAL.gold, inkHi = end || red ? DIAL.redHi : DIAL.goldHi, sh = end || red ? DIAL.redLo : DIAL.goldLo;
    var bits = DIGITS[d];
    [[2, sh], [0, null]].forEach(function (pass) {
      for (var i = 0; i < 35; i++) if (bits.charAt(i) === '1') {
        var cx = i % 5, cy = Math.floor(i / 5);
        g.fillStyle = pass[1] || (cy < 3 ? inkHi : ink);
        g.fillRect(ox + cx * sc + pass[0], oy + cy * sc + pass[0], sc, sc);
      }
    });
  }
  function coinDraw(g) {
    var t = cd.coin, sy = 36;
    // the slot
    g.fillStyle = DIAL.gold; g.fillRect(19, sy - 2, 26, 6);
    g.fillStyle = DIAL.goldLo; g.fillRect(19, sy + 3, 26, 1);
    g.fillStyle = DIAL.slot; g.fillRect(21, sy, 22, 2);
    if (t > 0.55 && t < 0.8) { g.fillStyle = '#fff6d0'; g.fillRect(21, sy, 22, 2); }
    // the coin: falls, spinning, and sinks into the slot
    if (t >= 0.62) return;
    var p = Math.min(1, t / 0.45), cyTop = -14 + (sy - 6 + 14) * p * p;
    if (t > 0.45) cyTop = sy - 6 + (t - 0.45) / 0.17 * 12;
    var sx = Math.abs(Math.cos(t * Math.PI * 5)), cw = Math.max(2, Math.round(12 * sx)), cx0 = 32 - Math.round(cw / 2);
    for (var yy = 0; yy < 12; yy++) {
      var py = Math.round(cyTop) + yy;
      if (py >= sy) break;                           // what has gone into the slot is out of sight
      for (var xx = 0; xx < cw; xx++) {
        var u = (xx + 0.5) / cw * 12 - 6, v = yy + 0.5 - 6, rr = Math.sqrt(u * u + v * v);
        if (rr > 6) continue;
        var col = rr > 4.8 || cw <= 3 ? '#b86a00' : (u < -1 && v < -1 ? '#fff2b0' : (Math.abs(u) < 1.2 && Math.abs(v) < 2.5 ? '#d08a00' : DIAL.gold));
        g.fillStyle = col; g.fillRect(cx0 + xx, py, 1, 1);
      }
    }
  }
  function carryOn() {
    Sound.unlock(); Sound.loopsOff();
    sim = Sim.continueZone(sim, viewOf(sim.L)[0]);
    if (window.HM) HM.track('continue', HM.where(sim, cur));
    Render.reset();
    timers = []; queue = []; line = null; hintLine = null; acc = 0; flags.yelpAt = -99;
    setState('play');
    Render.setBanner(T('ONCE MORE!'), T(sim.L.zones[sim.zone].name).toUpperCase(), 130);
    Sound.startMusic(false, sim.boss && sim.boss.st !== 'dead' && sim.L.bossMusic ? sim.L.bossMusic : sim.L.music);
    keepAwake();
  }
  // ------------------------------------------------------------------ the home screen, the map, the briefings, the options
  var homeT = 0, mapT = 0, macc = 0, optsFrom = 'home', drag = null, eraseArm = 0;
  // the map's camera slides both ways: cam and camY are where it is, target and targetY where it is heading
  var mv = { cam: 0, camY: 0, target: 0, targetY: 0, sel: 'm1', rv: null, moved: false };
  var fade = { a: 0, dir: 0, then: null };
  function menuUp() { return state === 'home' || state === 'map' || state === 'opts' || state === 'brief'; }
  function onMap() { return state === 'map' || ((state === 'opts' || state === 'brief') && optsFrom === 'map'); }
  function clearedCount() { var c = 0; CAMPAIGN.forEach(function (m) { if (prefs.prog[m.id].cleared) c++; }); return c; }
  function missionCount() { return CAMPAIGN.filter(function (m) { return !m.secret; }).length; }
  // the picture goes dark, the next screen comes up, the picture comes back
  function transit(fn) {
    if (calm) { fn(); return; }
    if (fade.dir > 0) return;                 // (already on the way somewhere; a picture still coming back can go again)
    fade.dir = 1; fade.then = fn;
  }
  function fadeStep() {
    if (fade.dir > 0) { fade.a = Math.min(1, fade.a + 0.12); if (fade.a >= 1) { var f = fade.then; fade.then = null; fade.dir = -1; if (f) f(); } }
    else if (fade.dir < 0) { fade.a = Math.max(0, fade.a - 0.1); if (fade.a <= 0) fade.dir = 0; }
  }
  function stopGame() {
    if (window.HM && sim) { var lv = HM.where(sim, cur); lv.status = sim.status; HM.track('mission_leave', lv); }
    Sound.pause(false); Sound.loopsOff();
    Sound.stopMusic(0.3, true); Sound.sea(false);
    sim = null;
    Render.reset();
  }
  // Start: the map's march comes in as the picture goes dark (asked for before the sound is allowed, so that the first
  // tap starts the march and not the home screen's theme)
  function leaveHome() {
    menuStep('start');
    Sound.menu('map'); Sound.unlock(); Sound.sfx('ui_select');
    transit(function () { toMap(); });
  }
  function toHome() {
    stopGame();
    homeT = 0;
    setState('home');
  }
  // the map, with the chosen mission in view; a mission cleared and not yet stamped gets its minute first
  function toMap(sel) {
    stopGame();
    var st = Menu.statuses(prefs.prog), due = null;
    CAMPAIGN.forEach(function (m) { if (!due && m.built && prefs.prog[m.id].cleared && !prefs.prog[m.id].stamped) due = m.id; });
    mv.sel = due || (sel && Menu.released(sel) ? sel : Menu.here(st, prefs.last));
    mv.rv = due ? { id: due, t: 0 } : null;
    mapT = 0; mv.moved = false;
    setState('map');
    aim(mv.sel, true);
    card();
    Sound.sfx('paper', { gain: 0.8 });
    menuStep('map', { mission: mv.sel });
  }
  function openOpts() {
    if (state !== 'home' && state !== 'map') return;
    Sound.unlock();
    optsFrom = state; eraseArm = 0; eraseLabel();
    Sound.sfx('ui_select', { gain: 0.7 });
    setState('opts');
  }
  function closeOpts() {
    if (state !== 'opts' && state !== 'brief') return;
    Sound.sfx('ui_back', { gain: 0.7 });
    setState(optsFrom);
    if (optsFrom === 'map') card();
  }
  // how much of the picture's width the map can be seen in: all of it, unless the mission card lies over its right side
  function mapVis() {
    if (!geo.cw) return W;
    var card = panels.map, cw = card && !card.hidden ? card.offsetWidth : 0;
    return clamp(W - (cw + 12) * W / geo.cw, 160, W);
  }
  // point the camera at a mission (snap: be there now, rather than slide there)
  function aim(id, snap) {
    var c = Menu.camFor(id, mapVis());
    mv.target = c.x; mv.targetY = c.y;
    if (snap) { mv.cam = c.x; mv.camY = c.y; }
    else { mv.cam = clamp(mv.cam, 0, Menu.mapW() - W); mv.camY = clamp(mv.camY, 0, Menu.mapH() - H); }
  }
  function select(id, quiet) {
    if (!id || !Menu.released(id) || id === mv.sel) return;      // (a mission not out yet has no card)
    mv.sel = id; mv.moved = false;
    aim(id, false);
    if (!quiet) { Sound.sfx('ui_move', { gain: 0.8 }); menuStep('card', { mission: id }); }
    card();
  }
  function finishReveal() {
    if (!mv.rv) return;
    var id = mv.rv.id;
    mv.rv = null;
    prefs.prog[id].stamped = true; savePrefs();
    // another clear still waiting for its stamp (an old save): give it its own minute
    var due = null;
    CAMPAIGN.forEach(function (m) { if (!due && m.built && prefs.prog[m.id].cleared && !prefs.prog[m.id].stamped) due = m.id; });
    if (due) { mv.rv = { id: due, t: 0 }; select(due, true); }
    card();
  }
  function menuTick() {
    if (fade.dir) fadeStep();
    if (state === 'home' || ((state === 'opts' || state === 'brief') && optsFrom === 'home')) {
      homeT++;
      // the beach slides slowly past behind the lettering, there and back
      if (backdrop) backdrop.cam = quick ? quickCam : calm ? 220 : Math.round(560 - 540 * Math.cos(homeT / 1500));
    } else {
      mapT++;
      if (!drag || !drag.moved) { mv.cam += (mv.target - mv.cam) * 0.16; mv.camY += (mv.targetY - mv.camY) * 0.16; }
      if (mv.rv && state === 'map') {
        var r = ++mv.rv.t, nx = Menu.mission(mv.rv.id).next.filter(Menu.released);     // (a road opens only to a mission that is out)
        if (r === 32) { Sound.sfx('stamp'); buzz(30); }
        if (r === 52 && nx.length) Sound.sfx('route', { gain: 0.8 });
        if (r === 112 && nx.length) Sound.sfx('radio', { gain: 0.7 });
        if (r === 112) card();
        if (r === 150 && nx.length) select(nx[0], true);
        if (r > 200) finishReveal();
      }
    }
  }
  // what a tap or a drag on the picture means here
  function toPicture(x, y) { return [(x - geo.cx0) * W / geo.cw, (y - geo.cy0) * H / geo.ch]; }
  function menuPointer(type, x, y, id) {
    if (state !== 'home' && state !== 'map') return false;
    var q = toPicture(x, y);
    if (type === 'down') {
      if (q[0] < 0 || q[0] > W || q[1] < 0 || q[1] > H || fade.dir > 0) return false;
      drag = { id: id, x0: q[0], y0: q[1], cam0: mv.cam, camY0: mv.camY, moved: false };
      return true;
    }
    if (!drag || drag.id !== id) return false;
    if (type === 'move') {
      if (state === 'map' && Math.abs(q[0] - drag.x0) + Math.abs(q[1] - drag.y0) > 5) drag.moved = mv.moved = true;
      if (drag.moved) {
        mv.cam = clamp(drag.cam0 - (q[0] - drag.x0), 0, Menu.mapW() - W); mv.target = mv.cam;
        mv.camY = clamp(drag.camY0 - (q[1] - drag.y0), 0, Menu.mapH() - H); mv.targetY = mv.camY;
      }
      return true;
    }
    var d = drag; drag = null;
    if (type === 'up' && !d.moved) tapAt(q);
    return true;
  }
  function playable(id) { var s = Menu.statuses(prefs.prog)[id]; return s === 'open' || s === 'cleared'; }
  // built, but its road is not open yet: the card offers to skip ahead to it (a tap on the map still only reads it).
  // (Khaled, 23 Oct: Skip ahead stays for players for now; 0.13.72 had made it developers-only)
  function skippable(id) { var m = Menu.mission(id); return !!(m && m.built && LEVELS[id] && !playable(id)); }
  function tapAt(q) {
    if (state === 'home') { if (quick) { quickGo(); return; } if (!woke) wakeUp(); else leaveHome(); return; }
    if (mv.rv) { finishReveal(); return; }
    var id = Menu.nodeAt(q[0], q[1], mv.cam, mv.camY);
    if (!id) return;
    if (!Menu.released(id)) { Sound.sfx('ui_back', { gain: 0.7 }); return; }     // not out yet: only a dot, with no card
    if (id === mv.sel) { if (playable(id)) play(id); else Sound.sfx('ui_back', { gain: 0.7 }); }
    else select(id);
  }
  function menuKey(k) {
    if (state === 'opts' || state === 'brief') { if (k === 'Escape' || k === 'Backspace') { closeOpts(); return true; } return false; }
    if (state === 'home') {
      if (quick) { quickGo(); return true; }
      if (!woke) { wakeUp(); return true; }
      if (k === 'Enter' || k === ' ' || k === 'z' || k === 'Z' || k === 'j' || k === 'J') { leaveHome(); return true; }
      if (k === 'o' || k === 'O') { openOpts(); return true; }
      return false;
    }
    if (state === 'map') {
      if (mv.rv) { finishReveal(); return true; }
      // along the campaign a stage at a time; up and down cross over at a fork
      if (k === 'ArrowLeft' || k === 'a' || k === 'A') { select(Menu.stageStep(mv.sel, -1)); return true; }
      if (k === 'ArrowRight' || k === 'd' || k === 'D') { select(Menu.stageStep(mv.sel, 1)); return true; }
      if (k === 'ArrowUp' || k === 'w' || k === 'W') { select(Menu.laneStep(mv.sel, -1)); return true; }
      if (k === 'ArrowDown' || k === 's' || k === 'S') { select(Menu.laneStep(mv.sel, 1)); return true; }
      if (k === 'Enter' || k === ' ' || k === 'z' || k === 'Z' || k === 'j' || k === 'J') { play(mv.sel); return true; }
      if (k === 'Escape' || k === 'Backspace' || k === 'x' || k === 'X') { Sound.sfx('ui_back', { gain: 0.7 }); transit(function () { toHome(); }); return true; }
      if (k === 'o' || k === 'O') { openOpts(); return true; }
      if (k === 'b' || k === 'B') { openBriefs(); return true; }
    }
    return false;
  }
  // ---- what is said about each mission, on the card and in the briefings
  var STATE_WORD = { cleared: 'Cleared', open: 'Ready', soon: 'Coming soon', locked: 'Locked', secret: 'Locked' };
  function joinOr(a) { return a.length < 2 ? a.join('') : a.slice(0, -1).join(T(', ')) + T(' or ') + a[a.length - 1]; }
  // a mission as a sentence says it: "the Coffee Port" (the map beside the card shows where it is)
  function called(m) { return Lang.rtl() ? T(m.name) : (/^The /.test(m.name) ? 'the ' + m.name.slice(4) : m.name); }
  function eyebrow(m, s) { return m.stage ? T('Mission {0} · {1} · {2}', [m.stage, T(m.road), T(STATE_WORD[s])]) : T('Secret mission · {0}', [T(STATE_WORD[s])]); }
  // (only missions that are out are named as what comes next: the order of the rest is still open)
  function aheadText(m) {
    var all = m.next.map(Menu.mission), nx = all.filter(function (q) { return q.built && !q.secret; });
    if (!all.length) return T('The end of the road. As far as anyone knows.');
    if (!nx.length) return all.every(function (q) { return q.secret; }) ? T('This is the end of the road. Or is it?') : T('The road on from here is still being drawn.');
    if (nx.length === 1) return T('Next stop: {0}.', [called(nx[0])]);
    return T('A fork in the road: {0}.', [nx.map(function (q) { return T('the {0} to {1}', [Lang.rtl() ? T(q.road) : q.road.toLowerCase(), called(q)]); }).join(T(', or '))]);
  }
  function lockText(m, s) {
    if (s === 'soon') return T('The road here is open. The mission itself is still being built.');
    if (s !== 'locked' && s !== 'secret') return '';
    var ins = Menu.before(m.id).filter(Menu.released).map(function (id) { return called(Menu.mission(id)); });
    if (!ins.length) return '';
    return T('Clear {0} to open the road here{1}', [joinOr(ins), m.built && LEVELS[m.id] ? T(', or skip ahead and play it now.') : '.']);
  }
  function partsOf(m) { return (LEVELS[m.id] ? LEVELS[m.id].zones.map(function (z) { return z.name; }) : m.parts).map(function (n) { return T(n); }); }
  // the mission card: what the selected mission is, how far you have got with it, and what you can do
  function card() {
    var st = Menu.statuses(prefs.prog), id = mv.sel, m = Menu.mission(id), s = st[id], p = prefs.prog[id];
    wantSoon(id);
    // (while its minute is playing, a newly opened mission still shows as it was)
    if (mv.rv && mv.rv.t < 112 && Menu.mission(mv.rv.id).next.indexOf(id) >= 0) s = m.secret ? 'secret' : 'locked';
    el('mEye').textContent = eyebrow(m, s);
    el('mName').textContent = T(m.name);
    el('mTag').textContent = T(m.place);
    el('mBrief').textContent = T(m.brief);
    el('mAhead').textContent = [lockText(m, s), aheadText(m)].filter(Boolean).join(' ');
    el('mBoss').textContent = T(m.boss);
    var cps = el('mCps');
    cps.textContent = '';
    partsOf(m).forEach(function (name, k) {
      var li = document.createElement('li');
      li.textContent = name;
      if (m.built && (p.cleared || (k <= p.reached && (p.runs > 0 || p.reached > 0)))) li.className = 'done';
      cps.appendChild(li);
    });
    var best = el('mBest');
    if (m.built && p.best) {
      best.innerHTML = T('Best <b></b> in <b></b>') + ' <span class="cardbadges"></span>';
      var bs = best.querySelectorAll('b'), cb = best.querySelector('.cardbadges');
      bs[0].textContent = num(p.best.total); bs[1].textContent = clock(p.best.time);
      [['ace', p.ace, p.ace ? T('Ace. Won: no continues used') : T('Ace. Not yet: finish without a continue')],
       ['lib', p.lib, p.lib ? T('Liberator. Won: everyone freed') : T('Liberator. Not yet: free everyone')]].forEach(function (b) {
        var cv = Badges.into(document.createElement('canvas'), b[0], !!b[1]); cv.title = b[2]; cv.setAttribute('role', 'img'); cv.setAttribute('aria-label', b[2]); cb.appendChild(cv);
      });
    } else best.textContent = m.built ? (p.runs ? T('Not cleared yet. Furthest: {0}.', [partsOf(m)[Math.min(p.reached, partsOf(m).length - 1)]]) : T('Not played yet.')) : '';
    best.hidden = !m.built;
    var b = el('bPlay'), canPlay = s === 'open' || s === 'cleared', skip = !canPlay && m.built && !!LEVELS[id] && s !== 'soon';
    b.disabled = !canPlay && !skip;
    b.textContent = T(s === 'cleared' ? 'Play again' : (s === 'open' ? 'Start mission' : (skip ? 'Skip ahead' : (s === 'soon' ? 'Coming soon' : 'Locked'))));
    // where it starts: any of its checkpoints, in developer mode only (players always start at the start; Khaled, 19 Oct)
    var row = el('mFromRow'), sel = el('mFrom'), L = LEVELS[id];
    row.hidden = !prefs.dev || !(canPlay || skip) || !L;
    if (!row.hidden) {
      sel.textContent = '';
      L.zones.forEach(function (z, k) { var o = document.createElement('option'); o.value = String(k); o.textContent = T(z.name); sel.appendChild(o); });
      sel.value = String(Math.min(fromSel[id] || 0, L.zones.length - 1));
    }
    var mb = panels.map.querySelector('.mbody');
    mb.scrollTop = 0;
    window.requestAnimationFrame(moreBelow);
    el('mNav').textContent = T(coarse ? 'Tap a mission to read it. Tap it again to start.' : 'Arrows move along the roads and across a fork, Enter starts, B lists every briefing, Escape goes back.');
  }
  function moreBelow() { var mb = panels.map.querySelector('.mbody'); mb.classList.toggle('more', mb.scrollHeight - mb.scrollTop > mb.clientHeight + 2); }
  // ---- every briefing on one list, in the order the roads run: the missions that are out (the rest have no card yet)
  function openBriefs() {
    if (state !== 'map') return;
    menuStep('briefings');
    optsFrom = 'map';
    var st = Menu.statuses(prefs.prog), list = el('bList');
    list.textContent = '';
    CAMPAIGN.filter(function (m) { return m.built; }).sort(function (a, b) { return (a.stage || 8) - (b.stage || 8); }).forEach(function (m) {
      var s = st[m.id], li = document.createElement('li'), btn = document.createElement('button');
      btn.type = 'button'; btn.className = 'brief-item' + (m.id === mv.sel ? ' here' : '') + ' st-' + s;
      btn.setAttribute('data-id', m.id);
      var eye = document.createElement('span'); eye.className = 'eyebrow'; eye.textContent = eyebrow(m, s);
      var nm = document.createElement('span'); nm.className = 'bname'; nm.textContent = T(m.name);
      var tg = document.createElement('span'); tg.className = 'btag'; tg.textContent = T(m.place);
      var br = document.createElement('span'); br.className = 'btext'; br.textContent = T(m.brief);
      var pt = document.createElement('span'); pt.className = 'bparts'; pt.textContent = partsOf(m).join(' · ');
      var bo = document.createElement('span'); bo.className = 'bboss'; bo.textContent = T(m.boss);
      var ah = document.createElement('span'); ah.className = 'bahead'; ah.textContent = aheadText(m);
      [eye, nm, tg, br, pt, bo, ah].forEach(function (x) { btn.appendChild(x); });
      btn.addEventListener('click', function () { setState('map'); select(m.id); });
      li.appendChild(btn); list.appendChild(li);
    });
    Sound.sfx('paper', { gain: 0.7 });
    setState('brief');
    var here = list.querySelector('.here');
    if (here && here.scrollIntoView) { try { here.scrollIntoView({ block: 'nearest' }); } catch (e) {} }
  }
  // developer mode: the FPS counter, hit boxes, the phone report and the fire-usage note; off for players (Khaled, 17 Oct)
  function setDev(on, save) {
    prefs.dev = !!on;
    app.classList.toggle('is-dev', prefs.dev);
    if (!prefs.dev && Render.opts.boxes) { Render.opts.boxes = false; el('bBoxes').setAttribute('aria-pressed', 'false'); el('bBoxes').textContent = T('Hit boxes are off'); }
    devLabel();
    if (state === 'map' && mv.sel) card();   // the card's start picker comes and goes with it
    if (save) savePrefs();
  }
  function devLabel() { var b = el('bDev'); b.setAttribute('aria-pressed', prefs.dev ? 'true' : 'false'); b.textContent = T(prefs.dev ? 'Developer: on' : 'Developer: off'); }
  function eraseLabel() { el('bErase').textContent = T(eraseArm ? 'Tap again to erase' : 'Erase progress'); el('bErase').classList.toggle('warn', !!eraseArm); }
  function clock(t) { t = Math.max(0, Math.floor(t)); return Math.floor(t / 60) + ':' + ('0' + (t % 60)).slice(-2); }
  function num(n) { return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  // ---- passing the game on (Khaled, 21 Oct): the phone's own share sheet where there is one, the link copied where
  // there is not. The link is the ?play one, so a friend new to the game lands straight in the first mission, and it
  // says where it was shared from (utm_source=share; utm_medium home or results; utm_content the mission cleared).
  var shareLast = null;
  function shareLink(from) {
    var base = 'https://kld-altamimi.github.io/bab-alyaman/';
    try { var og = document.querySelector('meta[property="og:url"]'); if (og && og.content) base = og.content; } catch (e) {}
    return base + '?play&utm_source=share&utm_medium=' + from + (from === 'results' && shareLast ? '&utm_content=' + shareLast.id : '');
  }
  function shareGame(from, btn) {
    Sound.unlock(); Sound.sfx('ui_select');
    var r = from === 'results' ? shareLast : null, url = shareLink(from);
    var text = r ? T('I cleared {0} in Bab al-Yemen: {1} points in {2}. Can you beat that?', [T(Menu.mission(r.id).name), num(r.total), clock(r.time)])
                 : T('Bab al-Yemen: Yazeed and Salem against the Zanabeel, a run-and-gun on the road to Sana\'a. Play it free in your browser:');
    var sheet = typeof navigator.share === 'function';
    if (window.HM) HM.track('share_click', { from: from, mission: r ? r.id : undefined, how: sheet ? 'sheet' : 'copy' });
    if (sheet) {
      try {
        var p = navigator.share({ title: T('Bab al-Yemen'), text: text, url: url });
        if (p && p.catch) p.catch(function (e) { if (!e || e.name !== 'AbortError') copyLink(text, url, btn); });
        return;
      } catch (e) {}
    }
    copyLink(text, url, btn);
  }
  // the line and the link onto the clipboard, and the button says so for a moment; failing that, WhatsApp's own sharing
  function copyLink(text, url, btn) {
    var all = text + ' ' + url;
    var said = function () {
      var n = btn && btn.lastChild;
      if (!n || n.nodeType !== 3) return;
      n.nodeValue = T('Link copied');
      window.clearTimeout(btn.shareT);
      btn.shareT = window.setTimeout(function () { n.nodeValue = T('Share'); }, 2600);
    };
    var byHand = function () {
      var ta = document.createElement('textarea'), ok = false;
      ta.value = all; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.left = '-9999px'; ta.style.top = '0';
      document.body.appendChild(ta);
      try { ta.select(); ta.setSelectionRange(0, all.length); ok = document.execCommand('copy'); } catch (e) {}
      document.body.removeChild(ta);
      if (ok) said(); else { try { window.open('https://wa.me/?text=' + encodeURIComponent(all), '_blank', 'noopener'); } catch (e) {} }
    };
    try { navigator.clipboard.writeText(all).then(said, byHand); } catch (e) { byHand(); }
  }
  // ---- a word back from the player (Khaled, 22 Oct): on the results, whether they liked the mission (one vote a results
  // screen, counted as `feedback`), and a way to say more on X: a post already addressed to the game's account
  var fbVoted = false;
  function feedbackReset() {
    fbVoted = false;
    el('bLike').classList.remove('picked'); el('bDislike').classList.remove('picked');
    el('fbQ').hidden = false; el('fbThanks').hidden = true;
  }
  function vote(choice) {
    if (fbVoted) return;
    fbVoted = true;
    Sound.unlock(); Sound.sfx('ui_select');
    el(choice === 'like' ? 'bLike' : 'bDislike').classList.add('picked');
    el('fbQ').hidden = true; el('fbThanks').hidden = false;
    if (window.HM) HM.track('feedback', { mission: cur, choice: choice });
  }
  function feedbackOnX() {
    Sound.unlock(); Sound.sfx('ui_select');
    var m = Menu.mission(cur), text = '@BabAlYemenGame ' + T('Feedback on {0}: ', [m ? T(m.name) : '']);
    if (window.HM) HM.track('feedback', { mission: cur, choice: 'x' });
    try { window.open('https://x.com/intent/tweet?text=' + encodeURIComponent(text), '_blank', 'noopener'); } catch (e) {}
  }
  function showResults() {
    var r = Sim.results(sim), L = sim.L, pm = prefs.prog[cur], best = pm.best;
    shareLast = { id: cur, total: r.total, time: r.time };
    // a practice run (started at a checkpoint, or one skipped): the clear counts, the best and the medals do not
    var practice = run.from > 0 || run.skipped, isBest = !practice && (!best || r.total > best.total);
    if (window.HM) HM.track('mission_complete', { mission: cur, time: Math.round(r.time), par: Math.round(r.par), score: r.score, total: r.total, ace: !!r.ace, liberator: !!r.liberator, practice: practice, deaths: sim.stats.deaths });
    if (isBest) pm.best = { total: r.total, time: Math.floor(r.time) };
    pm.cleared = true; pm.reached = L.zones.length - 1; prefs.last = cur;
    if (r.ace && !practice) pm.ace = true;
    if (r.liberator && !practice) pm.lib = true;
    if (cur === 'm1' && pm.best) prefs.best = pm.best;            // (the one best score the builds before the map kept)
    savePrefs();
    el('rTime').textContent = clock(r.time);
    el('rPar').textContent = T('par {0}', [clock(r.par)]);
    el('rTotal').textContent = num(r.total);
    el('rBreak').textContent = T('Score {0}', [num(r.score)]) + '  ·  ' + T('Time +{0}', [num(r.timeBonus)]) + (r.cleanBonus ? '  ·  ' + T('No lives lost +{0}', [num(r.cleanBonus)]) : '');
    var yourBest = best ? T('Your best is {0} in {1}.', [num(best.total), clock(best.time)]) : '';
    el('rBest').textContent = practice
      ? T('{0}, so this run is not kept as a best.', [run.from > 0 ? T('Started at {0}', [zoneWords(L, run.from)]) : T('A checkpoint was skipped')]) + (best ? ' ' + yourBest : '')
      : (isBest ? (best ? T('A new best. The old one was {0}.', [num(best.total)]) : '') : yourBest);
    var facts = [[T('Put down'), r.kills]];
    if (r.ranOver) facts.push([T('Run over'), r.ranOver]);
    if (r.flips) facts.push([T('Trucks flipped'), r.flips]);
    if (r.knifed) facts.push([T('Knifed'), r.knifed]);
    facts.push([T('Captured'), r.captures], [T('Freed'), T('{0} of {1}', [r.freed, r.detainees])]);
    if (r.bossT) facts.push([T(L.bossFact || 'Boss beaten in'), clock(r.bossT)]);
    facts.push([T('Shots that hit'), Math.round(r.accuracy * 100) + '%'], [T('Plates lost'), r.plates], [T('Lives lost'), r.deaths], [T('Continues'), r.continues]);
    var ul = el('rFacts');
    ul.textContent = '';
    facts.forEach(function (f) { var li = document.createElement('li'), b = document.createElement('b'); b.textContent = f[1]; li.appendChild(document.createTextNode(f[0] + ' ')); li.appendChild(b); ul.appendChild(li); });
    var tot = used.hold + used.auto || 1;
    var aceWord = r.ace ? T('yes') : T('no, a continue was used');
    var libWord = r.liberator ? T('yes') : T('no, {0}', [T(L.freedNote || 'somebody is still tied up')]);
    var fireWord = used.auto === 0 ? T('hold') : (used.hold === 0 ? T('auto') : T('{0}% hold, {1}% auto', [Math.round(used.hold * 100 / tot), Math.round(used.auto * 100 / tot)]));
    el('rMedals').textContent = (practice ? T('Medals are won on a run from the start with nothing skipped') : T('Ace: {0}. Liberator: {1}', [aceWord, libWord])) + (prefs.dev ? T('. Fire: {0}.', [fireWord]) : '.');
    fillReport();
    feedbackReset();
    Sound.sea(false); Sound.loopsOff();
    setState('results');
    var cap = function (w) { return w.charAt(0).toUpperCase() + w.slice(1); };
    badgesIn(r, practice, pm, T('A continue was used'), cap(T(L.freedNote || 'somebody is still tied up')));
  }
  // the two badges: one won on this run is struck in front of you, one at a time; one won before shows as yours; one
  // not won is its outline, with what it would have taken
  var badgeT = [];
  function badgesIn(r, practice, pm, aceWord, libWord) {
    badgeT.forEach(function (t) { window.clearTimeout(t); }); badgeT = [];
    var list = [
      { kind: 'ace', now: !practice && r.ace, had: pm.ace, why: r.ace ? T('No continues used') : aceWord },
      { kind: 'lib', now: !practice && r.liberator, had: pm.lib, why: r.liberator ? T('Everyone freed') : libWord }
    ], k = 0;
    list.forEach(function (b) {
      var box = el('rBadges').querySelector('[data-kind="' + b.kind + '"]'), won = b.now || b.had;
      box.className = 'badge'; Badges.into(box.querySelector('canvas'), b.kind, won);
      var note = b.now ? b.why : (b.had ? T('Already yours') : (practice ? T('Practice run') : b.why));
      box.querySelector('.bnote').textContent = note;
      if (b.now) {
        box.classList.add('wait', 'won');
        var at = 450 + 650 * k++;
        badgeT.push(window.setTimeout(function () {
          if (state !== 'results') return;
          box.classList.remove('wait'); box.classList.add('earn');
          badgeT.push(window.setTimeout(function () { if (state === 'results') { Sound.sfx('medal', { gain: 0.85 }); buzz([30, 40, 60]); } }, 300));
        }, at));
      } else box.classList.add(won ? 'won' : 'dim');
    });
  }
  function fillReport() { var t = report(); el('report').textContent = t; el('report2').textContent = t; }
  function keepAwake() {
    try {
      if (navigator.wakeLock && navigator.wakeLock.request && document.visibilityState === 'visible') {
        navigator.wakeLock.request('screen').then(function (w) { wake = w; }, function () {});
      }
    } catch (e) {}
  }

  // ------------------------------------------------------------------ buttons
  function setScheme(s) {
    prefs.scheme = s === 'auto' ? 'auto' : 'hold';
    Input.setScheme(prefs.scheme);
    var all = document.querySelectorAll('[data-scheme]');
    for (var i = 0; i < all.length; i++) all[i].setAttribute('aria-checked', all[i].getAttribute('data-scheme') === prefs.scheme ? 'true' : 'false');
    var note = T(prefs.scheme === 'auto'
      ? 'The gun fires by itself when something is in front of it. FIRE still works by hand.'
      : (coarse ? 'Hold FIRE to shoot. Slide your thumb up off it and it stays on; tap it to let go.' : 'Hold Z to shoot. F locks the trigger on and lets it go.'));
    var notes = document.querySelectorAll('.scheme-note');
    for (var j = 0; j < notes.length; j++) notes[j].textContent = note;
    savePrefs();
  }
  // the meters: music, effects and voices, each in the options and in the pause menu, the two kept in step
  var METERS = { music: ['vMusic', 'vMusic2'], sfx: ['vSfx', 'vSfx2'], voice: ['vVoice', 'vVoice2'] };
  function volOf(kind) { var v = prefs.vol && typeof prefs.vol[kind] === 'number' ? prefs.vol[kind] : 1; return Math.max(0, Math.min(1, v)); }
  function setVolume(kind, v, save) {
    if (!prefs.vol || typeof prefs.vol !== 'object') prefs.vol = {};
    prefs.vol[kind] = Math.max(0, Math.min(1, +v || 0));
    Sound.setVolume(kind, prefs.vol[kind]);
    METERS[kind].forEach(function (id) {
      var m = el(id), pc = Math.round(prefs.vol[kind] * 100);
      if (String(m.value) !== String(pc)) m.value = pc;
      m.setAttribute('aria-valuetext', pc + ' per cent');
      var o = m.parentNode.querySelector('output'); if (o) o.textContent = pc + '%';
    });
    if (save) savePrefs();
  }
  function wireMeter(kind) {
    METERS[kind].forEach(function (id) {
      var m = el(id);
      m.addEventListener('input', function () { setVolume(kind, m.value / 100, false); });
      // let go: it is kept, and a sample of that kind says how loud it is now
      m.addEventListener('change', function () {
        setVolume(kind, m.value / 100, true);
        Sound.unlock();
        if (kind === 'sfx') Sound.sfx('ui_select');
        else if (kind === 'voice') Sound.voice('yazeed_yalla', { over: true });
      });
    });
  }
  function setMuted(b) {
    prefs.muted = !!b; Sound.setMuted(prefs.muted);
    ['bSound', 'bSound3'].forEach(function (id) { var t = el(id); t.setAttribute('aria-pressed', prefs.muted ? 'false' : 'true'); t.textContent = T(prefs.muted ? 'Sound is off' : 'Sound is on'); });
    savePrefs();
  }
  function on(id, fn) { el(id).addEventListener('click', function (e) { e.preventDefault(); fn(e); }); }
  function wire() {
    var segs = document.querySelectorAll('[data-scheme]');
    for (var i = 0; i < segs.length; i++) segs[i].addEventListener('click', function (e) { Sound.unlock(); Sound.sfx('ui_move'); setScheme(e.currentTarget.getAttribute('data-scheme')); });
    on('bStart', leaveHome);
    on('bOpts', openOpts); on('bOpts2', openOpts);
    on('bBack', closeOpts);
    on('bPlay', function () { play(mv.sel, true); });
    el('mFrom').addEventListener('change', function (e) {
      fromSel[mv.sel] = Math.max(0, parseInt(e.currentTarget.value, 10) || 0);
      Sound.unlock(); Sound.sfx('ui_move', { gain: 0.8 });
    });
    on('bBriefs', openBriefs);
    panels.map.querySelector('.mbody').addEventListener('scroll', moreBelow, { passive: true });
    on('bBriefBack', closeOpts);
    on('bHome', function () { Sound.sfx('ui_back', { gain: 0.7 }); transit(function () { toHome(); }); });
    on('bResume', resume);
    on('bRestart', function () { Sound.unlock(); Sound.pause(false); begin(cur, run.from); });
    on('bSkip', skipAhead);
    on('bQuit', function () { transit(function () { toMap(); }); }); on('bQuit2', function () { transit(function () { toMap(); }); });
    on('bToMap', function () { Sound.unlock(); Sound.sfx('ui_select'); badgeT.forEach(function (t) { window.clearTimeout(t); }); transit(function () { toMap(cur); }); });
    on('bContinue', coinIn);
    el('aX').addEventListener('click', function () { Sound.sfx('ui_select'); if (window.HM) HM.track('social_click', { to: 'x' }); });
    ['pointerenter', 'focus'].forEach(function (n) { el('aX').addEventListener(n, function () { socialHot = true; }); });
    ['pointerleave', 'blur'].forEach(function (n) { el('aX').addEventListener(n, function () { socialHot = false; }); });
    on('bAgain', function () { Sound.unlock(); Sound.sfx('ui_select'); begin(cur, run.from); });
    on('bShare', function (e) { shareGame('home', e.currentTarget); });
    on('bShare2', function (e) { shareGame('results', e.currentTarget); });
    on('bLike', function () { vote('like'); }); on('bDislike', function () { vote('dislike'); }); on('bFbX', feedbackOnX);
    on('bSound', function () { setMuted(!prefs.muted); });
    on('bSound3', function () { setMuted(!prefs.muted); });
    var langs = document.querySelectorAll('[data-lang]');
    for (var li = 0; li < langs.length; li++) langs[li].addEventListener('click', function (e) { Sound.unlock(); Sound.sfx('ui_move'); setLang(e.currentTarget.getAttribute('data-lang'), true); });
    ['music', 'sfx', 'voice'].forEach(wireMeter);
    on('bDev', function () { setDev(!prefs.dev, true); });
    on('bErase', function () {
      if (!eraseArm) { eraseArm = 1; eraseLabel(); window.setTimeout(function () { eraseArm = 0; if (state === 'opts') eraseLabel(); }, 3500); return; }
      eraseArm = 0; prefs.prog = null; prefs.best = null; fromSel = {}; tidyProgress(); savePrefs();
      el('bErase').textContent = T('Progress erased'); el('bErase').classList.remove('warn');
      Sound.sfx('ui_back');
    });
    on('bBoxes', function (e) {
      Render.opts.boxes = !Render.opts.boxes;
      e.currentTarget.setAttribute('aria-pressed', Render.opts.boxes ? 'true' : 'false');
      e.currentTarget.textContent = T(Render.opts.boxes ? 'Hit boxes are on' : 'Hit boxes are off');
    });
    ['bFull', 'bFull2'].forEach(function (id) { on(id, fullScreen); });
    ['bCopy', 'bCopy2'].forEach(function (id, k) {
      on(id, function (e) {
        var pre = el(k ? 'report2' : 'report'), btn = e.currentTarget;
        function picked() { try { var rg = document.createRange(); rg.selectNodeContents(pre); var sl = window.getSelection(); sl.removeAllRanges(); sl.addRange(rg); } catch (er) {} btn.textContent = T('Selected: copy it from here'); }
        try { navigator.clipboard.writeText(pre.textContent).then(function () { btn.textContent = T('Copied'); }, picked); } catch (er) { picked(); }
      });
    });
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) { pause(); if (menuUp()) Sound.pause(true); }       // the menus' music stops with the page out of sight
      else if (menuUp()) Sound.pause(false);
    });
    window.addEventListener('blur', function () { pause(); });
    window.addEventListener('resize', layout);
    window.addEventListener('orientationchange', function () { window.setTimeout(layout, 60); window.setTimeout(layout, 400); });
    if (window.visualViewport) window.visualViewport.addEventListener('resize', layout);
    if (window.ResizeObserver) { try { new ResizeObserver(function () { layout(); }).observe(app); } catch (e) {} }
    ['fullscreenchange', 'webkitfullscreenchange'].forEach(function (n) { document.addEventListener(n, function () { window.setTimeout(layout, 50); fsLabel(); }); });
  }
  function fsElement() { return document.fullscreenElement || document.webkitFullscreenElement || null; }
  function fsLabel() { var t = T(fsElement() ? 'Leave full screen' : 'Full screen'); el('bFull').textContent = t; el('bFull2').textContent = t; }
  function fullScreen() {
    try {
      if (fsElement()) { (document.exitFullscreen || document.webkitExitFullscreen).call(document); return; }
      var rq = app.requestFullscreen || app.webkitRequestFullscreen, pr = rq.call(app);
      var then = function () { try { if (screen.orientation && screen.orientation.lock) screen.orientation.lock('landscape').catch(function () {}); } catch (e) {} };
      if (pr && pr.then) pr.then(then, function () { el('bFull').hidden = true; el('bFull2').hidden = true; fsOK = false; });
    } catch (e) { el('bFull').hidden = true; el('bFull2').hidden = true; fsOK = false; }
  }

  // ------------------------------------------------------------------ starting up
  function howTo() {
    el('howTo').textContent = T(coarse
      ? 'Left thumb moves, crouches and aims: straight up, or up and along for 45 degrees. Right thumb fires, jumps and throws grenades. FIRE with a man at arm\'s length draws the knife. In the 4x4, the left thumb is the pedal.'
      : 'Arrows move, crouch and aim: up, or up with left or right for 45 degrees. Z fires (the knife, up close), X jumps, C throws a grenade, P pauses. In the 4x4, right and left are faster and slower.');
  }
  // ---- the language: every fixed word in the panels is remembered in English when the page is first read, and set
  // again in the chosen language; what the shell writes itself goes through T() as it is written
  var fixedText = [];
  function remember() {
    var walker = document.createTreeWalker(el('ui'), NodeFilter.SHOW_TEXT, null), n;
    while ((n = walker.nextNode())) {
      if (!/\S/.test(n.nodeValue) || !/[A-Za-z]/.test(n.nodeValue)) continue;
      var p = n.parentNode;
      if (p && p.closest && p.closest('[data-fixed]')) continue;
      fixedText.push({ node: n, en: n.nodeValue });
    }
    var withAria = el('ui').querySelectorAll('[aria-label]');
    for (var i = 0; i < withAria.length; i++) fixedText.push({ el: withAria[i], attr: 'aria-label', en: withAria[i].getAttribute('aria-label') });
    var hi = el('hi');
    fixedText.push({ el: hi, attr: 'aria-label', en: hi.getAttribute('aria-label') });
  }
  function relabel() {
    for (var i = 0; i < fixedText.length; i++) {
      var f = fixedText[i];
      if (f.node) f.node.nodeValue = T(f.en); else f.el.setAttribute(f.attr, T(f.en));
    }
  }
  var titleEn = null;
  function setLang(code, save) {
    if (save) { prefs.lang = code; savePrefs(); }
    Lang.set(Lang.resolve(code));
    var rtl = Lang.rtl();
    document.documentElement.lang = Lang.code();
    window.LANG = Lang.code();                                 // for analytics.js, should it want to say which language a run was in
    // for analytics.js: what the player is set up with, and where they are (read on every event; never written to)
    window.HMgame = { ctx: function () { return { lang: Lang.code(), touch: !!coarse, scheme: prefs.scheme === 'auto' ? 'auto' : 'hold', dev: !!prefs.dev, muted: !!prefs.muted }; },
                      now: function () { return { state: state, mission: cur, sim: sim }; } };
    if (titleEn == null) titleEn = document.title;            // (the tab's title follows the language; the page's own is in both)
    document.title = rtl ? T('Bab al-Yemen Prototype') : titleEn;
    el('ui').dir = rtl ? 'rtl' : 'ltr';
    app.classList.toggle('is-ar', rtl);
    var segs = document.querySelectorAll('[data-lang]');
    for (var i = 0; i < segs.length; i++) segs[i].setAttribute('aria-checked', segs[i].getAttribute('data-lang') === Lang.code() ? 'true' : 'false');
    try { if (rtl && document.fonts && document.fonts.load) document.fonts.load("500 12px 'Noto Kufi Arabic'", '\u0628\u0627\u0628'); } catch (e) {}
    if (!booted) return;
    relabel();
    setScheme(prefs.scheme); setMuted(prefs.muted); fsLabel(); eraseLabel(); devLabel(); howTo();
    el('bBoxes').textContent = T(Render.opts.boxes ? 'Hit boxes are on' : 'Hit boxes are off');
    if (state === 'map' || optsFrom === 'map') card();
  }
  function fail(msg) { var b = el('boot'); b.hidden = false; b.textContent = msg; }
  function boot(carried) {
    loadPrefs(carried && carried.prefs);
    try { coarse = window.matchMedia('(pointer: coarse)').matches; } catch (e) {}
    try { calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
    fsOK = !!((document.fullscreenEnabled || document.webkitFullscreenEnabled) && (app.requestFullscreen || app.webkitRequestFullscreen));
    el('bFull').hidden = !fsOK; el('bFull2').hidden = !fsOK;
    if (coarse) app.classList.add('has-touch');
    howTo();
    Input.init(padEl, { stick: stickEl, knob: knobEl, aim: el('aim'), aimKnob: el('aimKnob'), fire: bFire, jump: bJump, bomb: bBomb }, {
      pause: togglePause,
      menu: menuPointer,
      menuKey: menuKey,
      any: function () { if (state === 'play') Sound.resume(); },
      touch: function () { if (!app.classList.contains('has-touch')) { app.classList.add('has-touch'); coarse = true; layout(); } }
    });
    wire();
    remember();
    setLang(prefs.lang || 'auto', false);
    relabel();
    setScheme(prefs.scheme);
    setMuted(prefs.muted);
    setDev(prefs.dev, false);
    ['music', 'sfx', 'voice'].forEach(function (k) { setVolume(k, volOf(k), false); });
    try { Sound.prefetch(AUDIO); } catch (e) {}
    var names = Object.keys(IMAGES), left = names.length, bad = false;
    names.forEach(function (n) {
      var im = new Image();
      im.onload = function () { imgs[n] = im; if (--left === 0 && !bad) ready(); };
      // (the pictures are in the page as WebP since 0.8.47: one that will not open here means a browser too old for it, and
      // reloading will not help; every player seen so far is on a browser that opens them)
      im.onerror = function () { bad = true; fail(/^data:image\/webp/.test(IMAGES[n]) ? T('This browser is too old to show the game\'s pictures. Update it and try again.') : T('The picture did not load. Reload the page to try again.')); };
      im.src = IMAGES[n];
    });
  }
  function ready() {
    for (var id in LEVELS) LEVELS[id].ground = (typeof GROUNDS !== 'undefined' && GROUNDS[id]) || (id === 'm1' ? GROUND : LEVELS[id].ground || null);      // (Taiz's ground comes with its level)
    Render.init(lo, ATLAS, FONTS, imgs);
    Render.opts.calm = calm;
    Menu.init(Render, ATLAS);
    backdrop = Sim.create(LEVEL, { viewW: W, lanes: geo.lanes });
    el('boot').hidden = true;
    booted = true;
    if (window.HM && HM.boot) HM.boot();
    layout();
    panels.home.querySelector('.acts').hidden = !woke;
    quickCam = backdrop.cam || 0;
    if (quick && !firstTime()) { quick = false; toMap(); soundOnFirstTouch(); }
    else { if (quick) { app.classList.add('is-quick'); Sound.want(musicFor('m1')); } setState('home'); }
    turnHint();
    draw(true);
    lastT = window.performance.now();
    window.requestAnimationFrame(frame);
  }

  // a page that is replaced while open (a new build arriving) keeps the player's choices
  var hot = window.claude && window.claude.hot;
  try { if (hot && hot.snapshot) hot.snapshot(function () { return { prefs: prefs }; }); } catch (e) {}
  window.__m1 = {
    wake: wakeUp, woke: function () { return woke; }, line: function () { return line; }, setLang: function (c) { setLang(c, true); }, lang: function () { return Lang.code(); },
    state: function () { return state; }, sim: function () { return sim; }, geo: function () { return geo; }, meter: function () { return { M: M, P: P }; },
    report: report, begin: begin, cur: function () { return cur; }, levels: function () { return Object.keys(LEVELS); }, pause: pause, resume: resume, layout: layout, width: function () { return W; }, line: function () { return line; },
    run: function () { return { from: run.from, skipped: run.skipped }; }, skipAhead: skipAhead,
    prog: function () { return prefs.prog; }, menu: function () { return { sel: mv.sel, cam: mv.cam, camY: mv.camY, target: mv.target, targetY: mv.targetY, rv: mv.rv ? mv.rv.t : -1, rvId: mv.rv ? mv.rv.id : null, vis: mapVis(), fade: fade.a }; },
    toMap: function (i) { toMap(i); }, toHome: toHome, setDev: function (on) { setDev(on, true); }, dev: function () { return prefs.dev; },
    look: function (x, y) { mv.cam = mv.target = x; mv.camY = mv.targetY = y; mv.moved = true; }
  };
  if (hot && hot.ready) hot.ready(boot); else boot((hot && hot.data) || {});
})();
