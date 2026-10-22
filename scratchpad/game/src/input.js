// input.js - thumbs and keys into the five things the simulation asks each tick: left/right, up/down, fire, jump, grenade.
// The stick floats: it appears where the left thumb lands and follows if the thumb drags past its rim.
// In the Apache (mode 'fly', Taiz) the right thumb has a stick of its own in FIRE's place, floating the same way: pushed
// any way, it points the chin gun that way and fires it (gun, gx, gy). FLARES and ROCKETS stay buttons beside it.
var Input = (function () {
  'use strict';
  var pad = null, el = {}, G = null, map = null;           // G: where everything is, in the pad's own pixels (set by layout)
  var ptr = {}, keys = {}, stick = { on: false, ox: 0, oy: 0, dx: 0, dy: 0, id: null };
  var aim = { on: false, ox: 0, oy: 0, dx: 0, dy: 0, id: null }, mode = 'foot';
  var held = { fire: false, jump: false, bomb: false }, lock = false, scheme = 'hold', enabled = false;
  var cb = {}, heldT = 0, locks = 0;
  var latch = { fire: false, jump: false, bomb: false };      // a press shorter than one tick still counts for one

  function init(padEl, els, callbacks) {
    pad = padEl; el = els; cb = callbacks || {};
    pad.addEventListener('pointerdown', down, { passive: false });
    pad.addEventListener('pointermove', move, { passive: false });
    pad.addEventListener('pointerup', up, { passive: false });
    pad.addEventListener('pointercancel', up, { passive: false });
    pad.addEventListener('lostpointercapture', lost);
    pad.addEventListener('contextmenu', function (e) { e.preventDefault(); });
    ['touchstart', 'touchmove', 'touchend'].forEach(function (n) { pad.addEventListener(n, function (e) { if (e.cancelable) e.preventDefault(); }, { passive: false }); });
    window.addEventListener('keydown', function (e) { key(e, true); });
    window.addEventListener('keyup', function (e) { key(e, false); });
    window.addEventListener('blur', releaseAll);
  }
  // g: the geometry; mapFn turns a pointer's place on the screen into the pad's own pixels (the pad may be turned sideways)
  function setLayout(g, mapFn) { G = g; map = mapFn || null; drawStick(); drawAim(); }
  function setMode(m) { if (m === mode) return; mode = m; aim.on = false; aim.id = null; aim.dx = aim.dy = 0; drawAim(); }
  // the aim stick's size and its place at rest: where FIRE is, a little bigger than FIRE
  function aimHome() { return { x: G.fire.x, y: G.fire.y, r: G.fire.r * 1.08 }; }
  function setEnabled(b) { enabled = b; if (!b) releaseAll(); }
  function setScheme(s) { scheme = s; lock = false; mark(); }
  function releaseAll() {
    ptr = {}; keys = {}; stick.on = false; stick.id = null; stick.dx = stick.dy = 0; held.fire = held.jump = held.bomb = false;
    aim.on = false; aim.id = null; aim.dx = aim.dy = 0;
    latch.fire = latch.jump = latch.bomb = false;
    drawStick(); drawAim(); mark();
  }
  function at(e) { return map ? map(e.clientX, e.clientY) : [e.clientX, e.clientY]; }

  function hit(b, x, y, slack) { var dx = x - b.x, dy = y - b.y, r = b.r * (slack || 1.25); return dx * dx + dy * dy <= r * r; }
  function down(e) {
    e.preventDefault();
    if (cb.any) cb.any();
    if (!G) return;
    var q = at(e), x = q[0], y = q[1], mouse = e.pointerType === 'mouse';
    if (!mouse && cb.touch) cb.touch();
    // a menu is up (the home screen, the map): the shell decides what a tap or a drag means
    if (!enabled && cb.menu && cb.menu('down', x, y, e.pointerId)) {
      try { pad.setPointerCapture(e.pointerId); } catch (err) {}
      ptr[e.pointerId] = { role: 'menu', sx: x, sy: y };
      return;
    }
    // the pause mark in the corner of the picture
    if (x >= G.pause.x0 && x <= G.pause.x1 && y >= G.pause.y0 && y <= G.pause.y1) { if (cb.pause) cb.pause(); return; }
    if (!enabled || (mouse && !G.shown)) return;
    try { pad.setPointerCapture(e.pointerId); } catch (err) {}
    var role = null;
    if (mode === 'fly') {
      // the Apache: FLARES and ROCKETS where they are; anywhere else on the right, the aim stick
      if (hit(G.jump, x, y, 1.15)) role = 'jump';
      else if (hit(G.bomb, x, y, 1.15)) role = 'bomb';
      else if (x < G.split && y >= G.top && stick.id === null) role = 'stick';
      else if (x >= G.split && y >= G.top && aim.id === null) role = 'aim';
    }
    else if (hit(G.fire, x, y)) role = 'fire';
    else if (hit(G.jump, x, y)) role = 'jump';
    else if (hit(G.bomb, x, y)) role = 'bomb';
    else if (x < G.split && y >= G.top && stick.id === null) role = 'stick';
    else if (x >= G.split && y >= G.top) {
      // a thumb that lands between buttons means the nearest one
      var best = null, bd = 1e9;
      ['fire', 'jump', 'bomb'].forEach(function (k) { var d = Math.hypot(x - G[k].x, y - G[k].y) - G[k].r; if (d < bd) { bd = d; best = k; } });
      if (bd < G.fire.r * 0.8) role = best;
    }
    if (!role) return;
    ptr[e.pointerId] = { role: role, sx: x, sy: y };
    if (role === 'stick') { stick.on = true; stick.id = e.pointerId; stick.ox = x; stick.oy = y; stick.dx = 0; stick.dy = 0; drawStick(); }
    else if (role === 'aim') { aim.on = true; aim.id = e.pointerId; aim.ox = x; aim.oy = y; aim.dx = 0; aim.dy = 0; drawAim(); buzz(); }
    else if (role === 'fire') {
      if (lock) { lock = false; ptr[e.pointerId].dead = true; }        // a tap on a locked trigger lets it go
      else { held.fire = true; latch.fire = true; }
      buzz();
    }
    else if (role === 'jump') { held.jump = true; latch.jump = true; buzz(); }
    else if (role === 'bomb') { held.bomb = true; latch.bomb = true; buzz(); }
    mark();
  }
  function move(e) {
    var p = ptr[e.pointerId];
    if (!p) return;
    e.preventDefault();
    var q = at(e), x = q[0], y = q[1];
    if (p.role === 'menu') { if (cb.menu) cb.menu('move', x, y, e.pointerId); return; }
    if (p.role === 'stick') {
      var dx = x - stick.ox, dy = y - stick.oy, d = Math.hypot(dx, dy), R = G.stick.r;
      if (d > R) { stick.ox += dx * (1 - R / d); stick.oy += dy * (1 - R / d); dx = x - stick.ox; dy = y - stick.oy; }
      stick.dx = dx; stick.dy = dy;
      drawStick();
    } else if (p.role === 'aim') {
      var ax = x - aim.ox, ay = y - aim.oy, ad = Math.hypot(ax, ay), AR = aimHome().r;
      if (ad > AR) { aim.ox += ax * (1 - AR / ad); aim.oy += ay * (1 - AR / ad); ax = x - aim.ox; ay = y - aim.oy; }
      aim.dx = ax; aim.dy = ay;
      drawAim();
    } else if (p.role === 'fire' && !p.dead && scheme === 'hold' && !lock) {
      // slide up off the trigger and it stays down
      if (p.sy - y > G.fire.r * 0.9) { lock = true; locks++; buzz(); mark(); }
    }
  }
  function up(e) {
    if (cb.any) cb.any();
    var p = ptr[e.pointerId];
    if (p && p.role === 'menu') {
      delete ptr[e.pointerId];
      if (cb.menu && G) { var q = at(e); cb.menu('up', q[0], q[1], e.pointerId); }
      return;
    }
    release(e.pointerId);
  }
  function lost(e) { release(e.pointerId); }
  function release(id) {
    var p = ptr[id];
    if (!p) return;
    delete ptr[id];
    if (p.role === 'menu') { if (cb.menu) cb.menu('cancel', 0, 0, id); return; }
    if (p.role === 'stick') { stick.on = false; stick.id = null; stick.dx = stick.dy = 0; drawStick(); }
    else if (p.role === 'aim') { aim.on = false; aim.id = null; aim.dx = aim.dy = 0; drawAim(); }
    else if (p.role === 'fire') held.fire = false;
    else if (p.role === 'jump') held.jump = false;
    else if (p.role === 'bomb') held.bomb = false;
    mark();
  }
  function buzz() { try { if (navigator.vibrate) navigator.vibrate(6); } catch (e) {} }

  var KEYMAP = { ArrowLeft: 'l', ArrowRight: 'r', ArrowUp: 'u', ArrowDown: 'd', a: 'l', d: 'r', w: 'u', s: 'd', A: 'l', D: 'r', W: 'u', S: 'd',
                 z: 'fire', Z: 'fire', j: 'fire', J: 'fire', x: 'jump', X: 'jump', k: 'jump', K: 'jump', ' ': 'jump', c: 'bomb', C: 'bomb', l: 'bomb', L: 'bomb' };
  function key(e, isDown) {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    var tag = e.target && e.target.tagName;
    // a menu is up: arrows, Enter, Escape and the fire and jump keys move about it (a focused button keeps Enter and Space)
    if (!enabled && isDown && cb.menuKey) {
      var onButton = tag === 'BUTTON' || tag === 'A' || tag === 'SUMMARY' || tag === 'INPUT';
      if (tag === 'SELECT' && e.key !== 'Escape') return;          // (a focused list keeps its own keys: arrows choose in it)
      if (!(onButton && (e.key === 'Enter' || e.key === ' ')) && cb.menuKey(e.key, !!e.repeat)) { e.preventDefault(); return; }
    }
    if (!enabled && (tag === 'BUTTON' || tag === 'A' || tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SUMMARY' || tag === 'SELECT')) {
      // a menu is up: its buttons keep Space and Enter, but Escape and P still work
      if (!(isDown && (e.key === 'Escape' || e.key === 'p' || e.key === 'P'))) return;
    }
    if (e.repeat) { if (KEYMAP[e.key] && enabled) e.preventDefault(); return; }
    if (isDown && cb.any) cb.any();
    if (isDown && (e.key === 'p' || e.key === 'P' || e.key === 'Escape')) { if (cb.pause) cb.pause(); e.preventDefault(); return; }
    if (isDown && (e.key === 'f' || e.key === 'F') && scheme === 'hold' && enabled) { lock = !lock; if (lock) locks++; mark(); return; }
    var k = KEYMAP[e.key];
    if (!k) return;
    if (!enabled) { if (!isDown) keys[k] = false; return; }
    e.preventDefault();
    keys[k] = isDown;
    if (isDown && latch[k] === false) latch[k] = true;
  }

  function drawStick() {
    if (!el.stick || !G) return;
    var cxp = stick.on ? stick.ox : G.stick.x, cyp = stick.on ? stick.oy : G.stick.y, R = G.stick.r;
    el.stick.style.transform = 'translate(' + (cxp - R).toFixed(1) + 'px,' + (cyp - R).toFixed(1) + 'px)';
    el.stick.classList.toggle('on', stick.on);
    el.knob.style.transform = 'translate(' + stick.dx.toFixed(1) + 'px,' + stick.dy.toFixed(1) + 'px)';
  }
  function drawAim() {
    if (!el.aim || !G) return;
    var h = aimHome(), cxp = aim.on ? aim.ox : h.x, cyp = aim.on ? aim.oy : h.y, R = h.r;
    el.aim.style.width = el.aim.style.height = (R * 2).toFixed(1) + 'px';
    el.aim.style.transform = 'translate(' + (cxp - R).toFixed(1) + 'px,' + (cyp - R).toFixed(1) + 'px)';
    el.aim.classList.toggle('on', aim.on);
    el.aim.classList.toggle('firing', aim.on);
    el.aimKnob.style.transform = 'translate(' + aim.dx.toFixed(1) + 'px,' + aim.dy.toFixed(1) + 'px)';
  }
  var AIM_DEAD = 0.25;                 // (how far the aim stick must be pushed before the gun points and fires)
  function mark() {
    if (!el.fire) return;
    el.fire.classList.toggle('on', held.fire || !!keys.fire || lock);
    el.fire.classList.toggle('locked', lock);
    el.fire.classList.toggle('auto', scheme === 'auto');
    el.jump.classList.toggle('on', held.jump || !!keys.jump);
    el.bomb.classList.toggle('on', held.bomb || !!keys.bomb);
  }

  // what the simulation is told this tick
  function sample() {
    var mx = 0, my = 0;
    if (stick.on && G) {
      var dx = stick.dx, dy = stick.dy, dead = G.stick.r * 0.26, ax = Math.abs(dx), ay = Math.abs(dy);
      // eight ways. Running is the common case, so sideways keeps a wide share of the circle; the upward diagonal
      // (aiming at 45 degrees on the run) starts a third of the way up, the downward one (a crouching walk) later, so a
      // thumb that sags while running does not slow him down.
      if (ax > dead && ax > ay * 0.45) mx = dx > 0 ? 1 : -1;
      if (ay > dead * 1.4 && ay > ax * (dy < 0 ? 0.62 : 0.84)) my = dy > 0 ? 1 : -1;
    }
    // (the stick as it lies, for what flies (Taiz): how far it is pushed, any way, past a small dead middle; full a little
    // short of the rim. On foot only the eight ways above count)
    var ax = 0, ay = 0;
    if (stick.on && G) {
      var d2 = Math.hypot(stick.dx, stick.dy), R2 = G.stick.r, dz = R2 * 0.16;
      if (d2 > dz) { var mag = Math.min(1, (d2 - dz) / (R2 * 0.78 - dz)); ax = stick.dx / d2 * mag; ay = stick.dy / d2 * mag; }
    }
    if (keys.l) mx = -1; if (keys.r) mx = 1;
    if (keys.u) my = -1; if (keys.d) my = 1;
    if (keys.l || keys.r) ax = mx; if (keys.u || keys.d) ay = my;
    var byHand = held.fire || !!keys.fire || latch.fire;
    if (byHand && !lock) heldT++;
    var o = { mx: mx, my: my, ax: ax, ay: ay, fire: byHand || lock, jump: held.jump || !!keys.jump || latch.jump, grenade: held.bomb || !!keys.bomb || latch.bomb, auto: scheme === 'auto' };
    // the aim stick: which way the gun is pointed, once it is pushed past its dead middle; held without a way, straight
    // ahead (Khaled, 21 Oct: "if I press the shoot button without a direction it shoots forward"). Either way it fires.
    if (mode === 'fly' && aim.on && G) {
      var gd = Math.hypot(aim.dx, aim.dy);
      o.gun = true;
      if (gd > aimHome().r * AIM_DEAD) { o.gx = aim.dx / gd; o.gy = aim.dy / gd; } else { o.gx = 1; o.gy = 0; }
    }
    latch.fire = latch.jump = latch.bomb = false;
    return o;
  }
  return { init: init, setLayout: setLayout, setEnabled: setEnabled, setScheme: setScheme, setMode: setMode, sample: sample, releaseAll: releaseAll,
           isLocked: function () { return lock; }, scheme: function () { return scheme; }, touches: function () { return Object.keys(ptr).length; },
           heldTicks: function () { return heldT; }, lockCount: function () { return locks; } };
})();
