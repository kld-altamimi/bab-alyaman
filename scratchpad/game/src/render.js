// render.js - draws one frame of the simulation at the game's own resolution. It keeps only what is purely for show:
// flashes, sparks, smoke, the shake of the screen. Nothing here feeds back into the game.
var Render = (function () {
  'use strict';
  var A = null, F = null, IMG = {}, cv = null, cx = null, W = 468, H = 216;
  // A level that zooms out (Taiz, by Apache) draws its world on a larger canvas (W x H, the zoom times the HUD's size) and
  // its HUD at the usual size on a canvas of its own (HW x HH), which the shell lays over the enlarged world: the HUD keeps
  // its size and its crisp lettering, and the world shows more around it.
  var HW = 468, HH = 216, zoom = 1, hudCv = null, hudCx = null;
  var parts = [], decals = [], posts = [], popups = [], shake = 0, flashT = 0, tick = 0, refillT = 0;
  var achoo = { t: -999, x: 0 };                  // (the last ACHOO! put up over a Dhanab: when, and where)
  var banner = null, hint = null, goT = 0, behindT = 0, zoneT = 0, zoneName = '';
  var spin = {}, gunAng = 2.2, duckT = 0;
  var opts = { boxes: false, calm: false };
  // other bosses draw themselves (render_<kind>.js): bosses[kind] = { draw(s, b, paused, K), events(e, s, K), hud(s, b, K) }
  var bosses = {}, K = null;
  // (at night in Taiz the men, Yazeed and the smoke are drawn from a copy of the sprites graded for the night, unless the
  // searchlight is on them: render_fly.js says which, through its tint(); SRC is the copy, or null for the sprites themselves)
  var SRC = null;

  function init(canvas, atlas, fonts, images) {
    cv = canvas; A = atlas; F = fonts; IMG = images;
    cx = cv.getContext('2d', { alpha: false });
    resize(W);
  }
  function resize(w, z) {
    z = z || 1;
    HW = w; zoom = z;
    W = Math.round(w * z); H = Math.round(HH * z);
    if (cv.width !== W) cv.width = W;
    if (cv.height !== H) cv.height = H;
    cx.imageSmoothingEnabled = false;
    if (z !== 1) {
      if (!hudCv) { hudCv = document.createElement('canvas'); hudCx = hudCv.getContext('2d'); }
      if (hudCv.width !== HW) hudCv.width = HW;
      if (hudCv.height !== HH) hudCv.height = HH;
      hudCx.imageSmoothingEnabled = false;
    }
    if (K) K.H = H;
  }
  function reset() {
    parts.length = 0; decals.length = 0; posts.length = 0; popups.length = 0; shake = 0; banner = null; hint = null; goT = 0; behindT = 0; zoneT = 0;
    spin = {}; gunAng = 2.2; duckT = 0; flashT = 0; achoo.t = -999; refillT = 0;
    for (var bk in bosses) if (bosses[bk].reset) bosses[bk].reset();
  }
  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }

  // ------------------------------------------------------------------ sprites and lettering
  // cut: leave off that many rows from the bottom (a man sunk behind something that is not tall enough to hide his feet)
  function spr(name, x, y, flip, alpha, cut) {
    var f = A.frames[name];
    if (!f) return;
    x = Math.round(x); y = Math.round(y);
    var h = f[3] - (cut || 0);
    if (h <= 0) return;
    if (alpha != null && alpha < 1) cx.globalAlpha = alpha;
    if (flip) {
      cx.save();
      cx.translate(x + 1, y);
      cx.scale(-1, 1);
      cx.drawImage(SRC || IMG.atlas, f[0], f[1], f[2], h, -f[4], -f[5], f[2], h);
      cx.restore();
    } else {
      cx.drawImage(SRC || IMG.atlas, f[0], f[1], f[2], h, x - f[4], y - f[5], f[2], h);
    }
    if (alpha != null && alpha < 1) cx.globalAlpha = 1;
  }
  // a sprite turned by any angle about its anchor, or about a point oy above it
  function sprRot(name, x, y, ang, flip, oy) {
    var f = A.frames[name];
    if (!f) return;
    cx.save();
    cx.translate(Math.round(x), Math.round(y));
    if (flip) cx.scale(-1, 1);
    cx.rotate(ang);
    cx.drawImage(SRC || IMG.atlas, f[0], f[1], f[2], f[3], -f[4], -f[5] + (oy || 0), f[2], f[3]);
    cx.restore();
  }
  // ---- Arabic lettering: the browser shapes the word in a Kufi face at pixel size, and the result is given
  // the pixel fonts' own look (a gradient down the letters, the dark edge, the shadow) and kept for the next frame.
  // Medium (500), not bold: bold reads chunky beside the pixel fonts (Khaled, 17 Oct). The sizes stay: one pixel
  // smaller and the dots sit level with the tops of the tall letters and read as strokes (tried, 17 Oct).
  var AR_PX = { s: 10, m: 12, b: 14, t: 14 }, AR_WT = { s: 500, m: 500, b: 500, t: 500 }, AR_FAM = "'Noto Kufi Arabic', 'DejaVu Sans', Arial, sans-serif", AR_THRESH = 110;
  var AR_GRAD = { lav: ['#ffffff', '#f4f4ff', '#dcdcf8', '#bcbcec', '#9c9cdc', '#8080c8'], org: ['#fff8c8', '#ffe66a', '#ffc22e', '#f8941c', '#e06410', '#b83c08'],
                  red: ['#fff0c0', '#ffc850', '#f88c28', '#e85018', '#c42810', '#8c1408'], blu: ['#ffffff', '#d8f0ff', '#a0d0f8', '#60a0e8', '#3070d0', '#1c48a8'] };
  var arCache = {}, arWork = null, arMask = null, arRGB = {}, AR_DOT = 48;
  function rgbOf(hex) { if (!arRGB[hex]) arRGB[hex] = [parseInt(hex.slice(1, 3), 16), parseInt(hex.slice(3, 5), 16), parseInt(hex.slice(5, 7), 16)]; return arRGB[hex]; }
  var arAsked = {};
  function arFont(wt) {           // ask for the Arabic part of the Kufi face (Google serves it as its own file) the first time a weight is needed
    if (arAsked[wt]) return;
    arAsked[wt] = true;
    try { if (document.fonts && document.fonts.load) document.fonts.load(wt + " 12px 'Noto Kufi Arabic'", '\u0628\u0627\u0628').then(function () { arCache = {}; }, function () {}); } catch (e) {}
  }
  // (for trying a look: Render.arTune({ wt: { m: 500 }, px: { s: 10 }, thresh: 130 }) and the next frame shows it)
  function arTune(o) {
    var k;
    if (o.wt) for (k in o.wt) AR_WT[k] = o.wt[k];
    if (o.px) for (k in o.px) AR_PX[k] = o.px[k];
    if (o.thresh) AR_THRESH = o.thresh;
    if (o.dot) AR_DOT = o.dot;
    arCache = {};
    return { wt: AR_WT, px: AR_PX, thresh: AR_THRESH, dot: AR_DOT };
  }
  // the marks of a word (8-connected), and the small ones grown to 2x2; returns whether anything grew
  var arLab = null;
  function arDots(d, M, WW, HH, x0, y0, x1, y1) {
    var N = WW * HH, i, j, k, x, y, n = 0, grew = false, stack = [], px = [];
    if (!arLab || arLab.length !== N) arLab = new Int32Array(N);
    var L = arLab;
    for (y = Math.max(0, y0 - 1); y <= Math.min(HH - 1, y1 + 1); y++) for (x = Math.max(0, x0 - 1); x <= Math.min(WW - 1, x1 + 1); x++) L[y * WW + x] = 0;
    function free(p, own) {         // a pixel that can be filled without touching a different mark
      var py = (p / WW) | 0, pxx = p - py * WW;
      if (py < 1 || pxx < 1 || py >= HH - 1 || pxx >= WW - 1 || M[p]) return false;
      for (var q = 0; q < 9; q++) { var r = p + (((q / 3) | 0) - 1) * WW + (q % 3) - 1; if (M[r] && L[r] !== own) return false; }
      return true;
    }
    for (y = y0; y <= y1; y++) for (x = x0; x <= x1; x++) {
      i = y * WW + x;
      if (!M[i] || L[i]) continue;
      n++; stack.length = 0; px.length = 0; stack.push(i); L[i] = n;
      while (stack.length) {
        j = stack.pop(); px.push(j);
        for (k = 0; k < 9; k++) {
          if (k === 4) continue;
          var r = j + (((k / 3) | 0) - 1) * WW + (k % 3) - 1;
          if (r >= 0 && r < N && M[r] && !L[r]) { L[r] = n; stack.push(r); }
        }
      }
      if (px.length > 3) continue;
      var bx0 = WW, bx1 = -1, by0 = HH, by1 = -1;
      for (k = 0; k < px.length; k++) { var yy = (px[k] / WW) | 0, xx = px[k] - yy * WW; if (xx < bx0) bx0 = xx; if (xx > bx1) bx1 = xx; if (yy < by0) by0 = yy; if (yy > by1) by1 = yy; }
      if (bx1 - bx0 > 1 || by1 - by0 > 1) continue;
      var fill = [], sides, s2, best, bs, c, add;
      if (bx1 === bx0) {              // one pixel wide: a column to the left or the right
        sides = [bx0 - 1, bx0 + 1]; best = null; bs = -1;
        for (s2 = 0; s2 < 2; s2++) {
          add = []; var sum = 0, ok = true;
          for (c = by0; c <= by1; c++) { var p2 = c * WW + sides[s2]; if (!free(p2, n)) { ok = false; break; } add.push(p2); sum += d[p2 * 4 + 3]; }
          if (ok && sum > bs) { bs = sum; best = add; }
        }
        if (best) fill = fill.concat(best);
      }
      if (by1 === by0) {              // one pixel tall: a row above or below
        sides = [by0 - 1, by0 + 1]; best = null; bs = -1;
        var cx0 = bx0, cx1 = bx1;
        if (fill.length) { var fx = fill[0] - ((fill[0] / WW) | 0) * WW; cx0 = Math.min(cx0, fx); cx1 = Math.max(cx1, fx); }
        for (s2 = 0; s2 < 2; s2++) {
          add = []; var sum2 = 0, ok2 = true;
          for (c = cx0; c <= cx1; c++) { var p3 = sides[s2] * WW + c; if (!free(p3, n)) { ok2 = false; break; } add.push(p3); sum2 += d[p3 * 4 + 3]; }
          if (ok2 && sum2 > bs) { bs = sum2; best = add; }
        }
        if (best) fill = fill.concat(best);
      }
      for (k = 0; k < fill.length; k++) { M[fill[k]] = 3; L[fill[k]] = n; grew = true; }
    }
    return grew;
  }
  function arBitmap(font, str) {
    var key = font + '|' + str, hit = arCache[key];
    if (hit) return hit;
    var kind = font === 'tall' ? 't' : font.charAt(0), pxs = AR_PX[kind] || 12, wt = AR_WT[kind] || 700, grad = AR_GRAD[font.split('_')[1]] || AR_GRAD.lav;
    arFont(wt);
    var WW = 640, HH = 48, BASE = 30, RIGHT = 630;
    if (!arWork) { arWork = document.createElement('canvas'); arWork.width = WW; arWork.height = HH; }
    var wc = arWork.getContext('2d', { willReadFrequently: true });
    wc.clearRect(0, 0, WW, HH);
    wc.font = wt + ' ' + pxs + 'px ' + AR_FAM; wc.direction = 'rtl'; wc.textAlign = 'right'; wc.textBaseline = 'alphabetic'; wc.fillStyle = '#ffffff';
    wc.fillText(str, RIGHT, BASE);
    var d = wc.getImageData(0, 0, WW, HH).data, N = WW * HH, x0 = WW, x1 = -1, y0 = HH, y1 = -1, x, y, i, j, k;
    if (!arMask) arMask = new Uint8Array(N);
    var M = arMask;
    for (i = 0; i < N; i++) M[i] = d[i * 4 + 3] >= AR_THRESH ? 1 : 0;
    // the dots that tell ب ت ث ن ق ي apart are faint blobs at these sizes and fall under the cut: a faint blob that
    // stands on its own (no kept stroke beside it) is kept at its brightest pixel
    for (y = 1; y < HH - 1; y++) for (x = 1; x < WW - 1; x++) {
      i = y * WW + x;
      var a = d[i * 4 + 3];
      if (M[i] || a < AR_DOT) continue;
      var lone = true, top = true;
      for (k = 0; k < 9 && lone; k++) {
        if (k === 4) continue;
        j = i + (((k / 3) | 0) - 1) * WW + (k % 3) - 1;
        if (M[j] === 1) lone = false; else if (d[j * 4 + 3] > a) top = false;
      }
      if (lone && top) M[i] = 2;
    }
    for (y = 0; y < HH; y++) for (x = 0; x < WW; x++) if (M[y * WW + x]) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
    if (x1 < 0) { hit = { w: 0, base: 0, cv: null }; arCache[key] = hit; return hit; }
    // ...and a dot one pixel wide reads as a stem: every mark of three pixels or fewer is grown to a 2x2 dot, towards
    // its brighter side, wherever that does not touch another mark
    if (arDots(d, M, WW, HH, x0, y0, x1, y1)) {
      x0 = WW; x1 = -1; y0 = HH; y1 = -1;
      for (y = 0; y < HH; y++) for (x = 0; x < WW; x++) if (M[y * WW + x]) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
    }
    var gw = x1 - x0 + 1, gh = y1 - y0 + 1, W2 = gw + 3, H2 = gh + 3;
    var cv = document.createElement('canvas'); cv.width = W2; cv.height = H2;
    var oc = cv.getContext('2d'), out = oc.createImageData(W2, H2), o = out.data;
    function on(x, y) { x -= 1; y -= 1; return x >= 0 && y >= 0 && x < gw && y < gh && M[(y + y0) * WW + (x + x0)] > 0; }
    function near(x, y) { for (var k = 0; k < 9; k++) if (on(x + (k % 3) - 1, y + ((k / 3) | 0) - 1)) return true; return false; }
    for (y = 0; y < H2; y++) for (x = 0; x < W2; x++) {
      var k = (y * W2 + x) * 4;
      if (on(x, y)) { var c = rgbOf(grad[Math.min(grad.length - 1, Math.floor((y - 1) * grad.length / gh))]); o[k] = c[0]; o[k + 1] = c[1]; o[k + 2] = c[2]; o[k + 3] = 255; }
      else if (near(x, y)) { o[k] = 16; o[k + 1] = 16; o[k + 2] = 28; o[k + 3] = 255; }
      else if (x > 0 && y > 0 && near(x - 1, y - 1)) { o[k] = 10; o[k + 1] = 8; o[k + 2] = 20; o[k + 3] = 120; }
    }
    oc.putImageData(out, 0, 0);
    hit = { w: gw, base: BASE - y0 + 1, cv: cv };
    arCache[key] = hit;
    return hit;
  }
  // the Kufi face arrives from the web after the first frames: whenever a face finishes loading, everything Arabic
  // drawn before then is drawn again (the lettering is kept per word, so this is cheap)
  try {
    if (document.fonts && document.fonts.addEventListener) document.fonts.addEventListener('loadingdone', function () { arCache = {}; });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { arCache = {}; }, function () {});
  } catch (e) {}
  function arText(font, str, x, y, align) {
    var b = arBitmap(font, str), fo = F[font] || F.m_lav, cap = font === 'tall' ? 22 : fo.cap;
    if (align === 'c') x -= Math.floor(b.w / 2);
    else if (align === 'r') x -= b.w;
    x = Math.round(x); y = Math.round(y);
    if (b.cv) cx.drawImage(b.cv, x - 1, y + cap - b.base);
    return x + b.w;
  }
  // how far apart lines stack: the pixel fonts' own pitch (the caller's number), or more for Arabic, whose letters
  // reach above and below where the capitals sit
  var AR_LH = { s: 12, m: 15, b: 17, t: 18 };
  function lineH(font, str, latin) {
    if (!Lang.isArabic(str)) return latin;
    var kind = font === 'tall' ? 't' : font.charAt(0);
    return AR_LH[kind] || latin;
  }
  function textW(font, str) {
    var fo = F[font], w = 0, adv = fo.adv != null ? fo.adv : 1;
    str = String(str);
    if (Lang.isArabic(str)) return arBitmap(font, str).w;
    if (fo.upper) str = str.toUpperCase();
    for (var i = 0; i < str.length; i++) { var g = fo.glyphs[str.charAt(i)] || fo.glyphs['?'] || fo.glyphs['0']; w += g[1] + adv; }
    return Math.max(0, w - adv);
  }
  function text(font, str, x, y, align) {
    var fo = F[font], tall = font === 'tall', adv = fo.adv != null ? fo.adv : 1;
    str = String(str);
    if (Lang.isArabic(str)) return arText(font, str, x, y, align);
    if (fo.upper) str = str.toUpperCase();
    if (align === 'c') x -= Math.floor(textW(font, str) / 2);
    else if (align === 'r') x -= textW(font, str);
    x = Math.round(x); y = Math.round(y);
    for (var i = 0; i < str.length; i++) {
      var ch = str.charAt(i), g = fo.glyphs[ch] || fo.glyphs['?'] || fo.glyphs['0'];
      if (ch !== ' ') {
        if (tall) cx.drawImage(IMG.font, g[0], fo.y, g[1] + 5, fo.cell, x - 2, y - 1, g[1] + 5, fo.cell);
        else cx.drawImage(IMG.font, g[0], fo.y, g[1] + 4, fo.cell, x - 1, y - 1, g[1] + 4, fo.cell);
      }
      x += g[1] + adv;
    }
    return x;
  }

  // ------------------------------------------------------------------ the painted stage
  // each mission has its own set of pictures (ATLAS.stages[L.art]: layers, world, fixed); the Strait's are also kept at
  // the top of the atlas, as before
  function stageOf(L) { return (A.stages && A.stages[(L && L.art) || 'strait']) || { layers: A.layers, world: A.world, fixed: A.fixed }; }
  // sky, far shore and sea go round and round; the ground is a run of strips, some of them repeated
  function wrapLayer(l, cam) {
    var im = IMG[l.img], x = Math.floor(cam * l.par) % l.w;
    if (x < 0) x += l.w;
    var w1 = Math.min(W, l.w - x);
    cx.drawImage(im, x, 0, w1, l.h, 0, l.y, w1, l.h);
    if (w1 < W) cx.drawImage(im, 0, 0, W - w1, l.h, w1, l.y, W - w1, l.h);
  }
  function stripLayer(l, cam, dy) {
    var x0 = Math.round(cam * l.par);
    for (var i = 0; i < l.strips.length; i++) {
      var st = l.strips[i], end = st.until != null ? st.until : st.x + st.w;
      if (end <= x0 || st.x >= x0 + W) continue;
      var k = st.until != null ? Math.max(0, Math.floor((x0 - st.x) / st.w)) : 0;
      for (var tx = st.x + k * st.w; tx < end && tx < x0 + W; tx += st.w) {
        var a = Math.max(0, x0 - tx), b = Math.min(st.w, end - tx, x0 + W - tx);
        if (b > a) cx.drawImage(IMG[st.img], a, 0, b - a, st.h, tx + a - x0, st.y + dy, b - a, st.h);
      }
    }
  }

  // ------------------------------------------------------------------ what the simulation's events look like
  function part(kind, x, y, o) {
    var p = { k: kind, x: x, y: y, vx: 0, vy: 0, t: 0, life: 8, g: 0, flip: false, name: null, ang: 0, spin: 0 };
    if (o) for (var k in o) p[k] = o[k];
    parts.push(p);
    return p;
  }
  function pop(x, y, str, f) { popups.push({ x: x, y: y, t: 0, s: str, f: f || 's_org' }); if (popups.length > 14) popups.shift(); }
  function embers(x, y, n, v) {
    for (var i = 0; i < n; i++) part('ember', x, y, { life: 14 + Math.random() * 14, vx: (Math.random() - 0.5) * (v || 220), vy: -60 - Math.random() * (v || 220) * 0.7, g: 520 });
  }
  // an explosion is a short film from the sheet (two ticks a frame), with grit thrown about it by hand
  function boom(e) {
    if (e.kind === 'chilli') {
      // (chillies: a puff of red where each comes down, no fire)
      for (var ci = 0; ci < 3; ci++) part('redpuff', e.x + (Math.random() - 0.5) * 12, e.y - Math.random() * 6, { life: 16 + Math.random() * 8, vx: (Math.random() - 0.5) * 50, vy: -20 - Math.random() * 30, k2: ci });
      for (var cj = 0; cj < 5; cj++) part('clod', e.x, e.y - 2, { life: 20 + Math.random() * 10, vx: (Math.random() - 0.5) * 140, vy: -80 - Math.random() * 90, g: 600, col: ['#c8301a', '#f87a4c', '#8a1c0c'][cj % 3] });
      shake = Math.max(shake, 2);
      return;
    }
    var big = e.kind === 'drum' || e.kind === 'mine' || e.kind === 'truck' || e.kind === 'heli' || e.kind === 'aa', set = e.air ? 'ex_a' : (big ? 'ex_m' : 'ex_s'), n = A.booms[set];
    var x = e.x, y = e.air ? e.y : e.floor, i;
    if (e.air && big) { set = 'ex_m'; n = A.booms[set]; y = e.y + 14; }           // a machine going up off the ground still goes up properly
    part('boom', x, y, { life: n * 2 - 1, set: set });
    for (i = 0; i < (big ? 9 : 5); i++) {
      part('ember', x, y - 6, { life: 18 + Math.random() * 16, vx: (Math.random() - 0.5) * 260, vy: -70 - Math.random() * 190, g: 520 });
    }
    if (!e.air) {
      for (i = 0; i < (big ? 9 : 5); i++) {
        part('clod', x + (Math.random() - 0.5) * 10, y - 2, { life: 30 + Math.random() * 22, vx: (Math.random() - 0.5) * (big ? 230 : 170), vy: -90 - Math.random() * (big ? 210 : 150), g: 640, dark: Math.random() < 0.5 });
      }
      decals.push({ x: x, y: y, t: 0 });
      if (decals.length > 14) decals.shift();
    }
    shake = Math.max(shake, big ? 12 : (e.kind === 'kdrone' ? 4 : 7));
    flashT = big ? 3 : flashT;
  }
  function onEvents(s, events) {
    for (var ri = 0; ri < events.length; ri++) if (events[ri].t === 'refill') refillT = 60;      // (a checkpoint refill: the HUD glints)
    for (var i = 0; i < events.length; i++) {
      var e = events[i], p = s.p, k, took = false;
      for (var pk in bosses) if (bosses[pk].pre && bosses[pk].pre(e, s, K)) { took = true; break; }      // (a mode of its own may take an event first: Taiz's Apache)
      if (took) continue;
      switch (e.t) {
        case 'shot':
          var ang = e.aim === 'up' ? -Math.PI / 2 : (e.aim === 'down' ? Math.PI / 2 : (e.aim === 'diag' ? -Math.PI / 4 : (e.aim === 'ddiag' ? Math.PI / 4 : 0)));
          part('muzzle', e.x, e.y, { life: 3, flip: e.face < 0, name: e.w === 'hmg' ? 'fx_muzzle' : 'fx_muzzle_s', ang: ang });
          if (e.w === 'hmg' || Math.random() < 0.6) part('casing', p.x - e.face * 2, p.y - (p.crouch ? 12 : 24), { life: 34, vx: -e.face * (40 + Math.random() * 40) + (s.mode === 'drive' ? s.car.vx * 0.5 : 0), vy: -110 - Math.random() * 50, g: 620 });
          break;
        case 'eshot':
          if (e.k === 'heavy' || e.k === 'boss') part('muzzle', e.x, e.y, { life: 4, flip: false, name: 'fx_muzzle', ang: e.k === 'boss' ? Math.atan2((p.y - 17) - e.y, p.x - e.x) : Math.PI });
          else part('muzzle', e.x, e.y, { life: 3, flip: e.face < 0, name: 'fx_muzzle_s', ang: 0 });
          break;
        case 'hit':
          if (e.kind === 'guard') { part('spark', e.x, e.y, { life: 4, name: 'fx_spark2' }); part('ember', e.x, e.y, { life: 8, vx: (Math.random() - 0.5) * 140, vy: -70 - Math.random() * 50, g: 500 }); break; }
          if (e.kind === 'bean') { part('ember', e.x, e.y - 1, { life: 9, vx: (Math.random() - 0.5) * 60, vy: -50, g: 400 }); break; }
          if (e.kind === 'sand' || e.kind === 'bags' || e.kind === 'cloth') part('puff', e.x, e.y - 2, { life: 9 });
          else part('spark', e.x, e.y, { life: 5, name: e.kind === 'body' ? 'fx_spark' : 'fx_spark2' });
          if (e.kind === 'door' || e.kind === 'metal') part('ember', e.x, e.y, { life: 10, vx: (Math.random() - 0.5) * 160, vy: -80 - Math.random() * 60, g: 500 });
          break;
        case 'slash':
          part('slash', e.x, e.y, { life: 7, flip: e.face < 0 });
          part('spark', e.x + e.face * 12, e.y, { life: 5, name: e.hit === 'door' ? 'fx_spark2' : 'fx_spark' });
          if (e.hit === 'door') embers(e.x + e.face * 12, e.y, 3, 150);
          shake = Math.max(shake, 3);
          break;
        case 'land':
          if (e.v > 150) { part('puff', e.x - 5, e.y - 2, { life: 9 }); part('puff', e.x + 5, e.y - 2, { life: 9, flip: true }); }
          break;
        case 'thud': part('puff', e.x, e.y - 2, { life: 9 }); break;
        case 'bounce': part('puff', e.x, e.y - 2, { life: 7 }); break;
        case 'explode': boom(e); break;
        case 'die':
          pop(e.x, e.y - 40, String(e.pts != null ? e.pts : Sim.KIND[e.k].score));
          if (e.door) part('piece', e.x + e.face * 10, e.y - 12, { life: 60, vx: e.face * 30, vy: -160, g: 700, spin: e.face * 0.2, name: 'piece_door' });
          if (e.how === 'ram') {
            spin[e.id] = 1;
            part('spark', e.x, e.y - 18, { life: 5, name: 'fx_spark' });
            part('puff', e.x, e.y - 4, { life: 9 });
            shake = Math.max(shake, 5);
          }
          break;
        case 'door_break':
          // the door comes apart in two and leaves him standing there
          part('piece', e.x + e.face * 12, e.y - 26, { life: 70, vx: e.dir * 70 + e.face * 20, vy: -210, g: 700, spin: e.dir * 0.31, name: 'piece_door_top' });
          part('piece', e.x + e.face * 12, e.y - 10, { life: 70, vx: e.dir * 120, vy: -130, g: 700, spin: -e.dir * 0.23, name: 'piece_door_bot' });
          embers(e.x + e.face * 12, e.y - 18, 6, 200);
          part('spark', e.x + e.face * 12, e.y - 18, { life: 5, name: 'fx_spark2' });
          pop(e.x, e.y - 44, T('DOOR {0}', [100]));
          shake = Math.max(shake, 4);
          break;
        case 'bash':
          part('puff', e.x, e.y + 14, { life: 9 });
          if (e.hit) { part('spark', e.x + e.face * 6, e.y, { life: 5, name: 'fx_spark2' }); shake = Math.max(shake, 7); }
          break;
        case 'capture': pop(e.x, e.y - 44, T('CAPTURED {0}', [e.pts != null ? e.pts : Sim.KIND.rifle.score * 2]), 's_lav'); break;
        case 'freed':
          pop(e.x, e.y - 50, T('FREED {0}', [500]), 's_lav');
          posts.push({ x: e.x, y: e.y });
          break;
        case 'pickup': pop(e.x, e.y - 26, e.k === 'hmg' ? T('HEAVY MG') : (e.k === 'bean' || e.k === 'chilli' ? '+' + e.pts : (e.k === 'rockets' ? T('ROCKETS +5') : T('GRENADES +5')))); break;
        // ---- Mocha
        case 'emerge': part('puff', e.x - 8, e.y - 2, { life: 9 }); part('puff', e.x + 8, e.y - 2, { life: 9, flip: true }); break;
        case 'fling': part('puff', e.x, e.y, { life: 7 }); break;
        case 'swing': part('puff', e.x, e.y + 18, { life: 8 }); if (e.hit) { part('spark', e.x, e.y, { life: 5, name: 'fx_spark2' }); shake = Math.max(shake, 6); } break;
        case 'vent_blast': shake = Math.max(shake, 2); break;
        // ---- the Souq
        case 'spice_burst':
          for (k = 0; k < 8; k++) part('clod', e.x + (Math.random() - 0.5) * 8, e.y - 4, { life: 18 + Math.random() * 14, vx: (Math.random() - 0.5) * 160, vy: -60 - Math.random() * 120, g: 500, col: SPICE_COL[e.col] || SPICE_COL.red });
          part('puff', e.x, e.y + 6, { life: 9 }); shake = Math.max(shake, 2);
          break;
        case 'sneeze':
          // (one ACHOO! for a knot of men going off together, not one on top of another)
          if (e.who === 'p') pop(e.x, e.y - 44, T('ACHOO!'), 's_lav');
          else if (tick - achoo.t > 40 || Math.abs(e.x - achoo.x) > 60) { pop(e.x, e.y - 46, T('ACHOO!'), 's_org'); achoo.t = tick; achoo.x = e.x; }
          part('spray', e.x + (e.who === 'p' ? p.face : -1) * 7, e.y - (e.who === 'p' ? 27 : 28), { life: 10, flip: (e.who === 'p' ? p.face : -1) < 0 });
          break;
        case 'achoo': part('spray', e.x + (e.face || -1) * 6, e.y + 1, { life: 9, flip: (e.face || -1) < 0 }); break;
        case 'fumble': part('puff', e.x, e.y + 20, { life: 8 }); break;
        case 'bar_hit':
          if (e.how === 'shot' && Math.random() < 0.5) part('clod', e.x - 8 + Math.random() * 16, e.y + Math.random() * 10, { life: 16, vx: -40 - Math.random() * 60, vy: -60 - Math.random() * 60, g: 600, col: '#8c552c' });
          break;
        case 'bar_break':
          for (k = 0; k < 4; k++) part('piece', e.x0 + 10 + k * 10, e.top + 8 + (k % 2) * 8, { life: 80, vx: e.dir * (60 + Math.random() * 120) + (Math.random() - 0.5) * 60, vy: -180 - Math.random() * 140, g: 640, spin: (Math.random() - 0.5) * 0.6, name: 'barr_p' + k, oy: 0, bounce: 1 });
          for (k = 0; k < 10; k++) part('clod', e.x0 + Math.random() * 46, e.top + 10 + Math.random() * 20, { life: 30 + Math.random() * 20, vx: e.dir * (40 + Math.random() * 160), vy: -90 - Math.random() * 150, g: 640, dark: Math.random() < 0.5 });
          for (k = 0; k < 4; k++) part('smoke', e.x0 + 8 + k * 10, e.top + 18, { life: 30, vx: (Math.random() - 0.5) * 30, vy: -30 });
          pop(e.x, e.top - 6, T('BARRICADE {0}', [e.pts]), 's_org');
          shake = Math.max(shake, 8); flashT = Math.max(flashT, 1);
          break;
        case 'plate_lost':
          shake = Math.max(shake, 6);
          if (s.mode === 'drive') embers(s.car.x + 20, s.car.y - 26, 6, 240);
          break;
        case 'life_lost': shake = Math.max(shake, 10); break;
        case 'go': if (!e.dir || e.dir === 'right') goT = 200; break;      // (Taiz's way up has an arrow of its own)
        case 'behind': behindT = 100; break;
        case 'checkpoint': zoneT = 150; zoneName = T(e.name); break;
        case 'drop_weapon': part('gunfall', e.x, e.y - 18, { life: 40, vx: -20, vy: -120, g: 700, spin: 0.25 }); break;

        // ---- the road
        case 'mount': part('puff', e.x - 30, e.y - 2, { life: 9 }); part('puff', e.x + 26, e.y - 2, { life: 9, flip: true }); break;
        case 'hop': part('puff', e.x - 29, e.y - 2, { life: 9 }); part('puff', e.x + 29, e.y - 2, { life: 9, flip: true }); break;
        case 'car_land':
          part('puff', e.x - 34, e.y - 2, { life: 10 }); part('puff', e.x + 34, e.y - 2, { life: 10, flip: true });
          part('puff', e.x - 22, e.y - 2, { life: 8, flip: true }); part('puff', e.x + 22, e.y - 2, { life: 8 });
          if (e.v > 180) shake = Math.max(shake, 5);
          break;
        case 'panic': part('alert', e.x, e.y - 48, { life: 22 }); break;
        case 'tell':
          if (e.k === 'swoop') duckT = 96;
          break;
        case 'gunner_down':
          part('piece', e.x, e.y - 2, { life: 70, vx: (s.car ? s.car.vx * 0.5 : 0) + 60 + Math.random() * 50, vy: -230, g: 700, spin: 0.3, name: 'rifle_angry_flung', oy: 18 });
          pop(e.x, e.y - 30, String(e.pts));
          break;
        case 'flip':
          pop(e.x, e.y - 58, T('FLIPPED {0}', [e.pts]));
          for (k = 0; k < 3; k++) part('spark', e.x - 40 + Math.random() * 14, e.y - 8 - Math.random() * 22, { life: 5, name: 'fx_spark2' });
          embers(e.x - 34, e.y - 18, 10, 300);
          shake = Math.max(shake, 10);
          break;
        case 'truck_dead':
          if (e.pts) pop(e.x, e.y - 58, e.how === 'crush' ? T('CRUSHED {0}', [e.pts]) : String(e.pts));
          for (k = -1; k <= 1; k += 2) part('piece', e.x + k * 29, e.y - 9, { life: 90, vx: k * (60 + Math.random() * 90) + 60, vy: -220 - Math.random() * 120, g: 640, spin: k * 0.3, name: 'wheel0', oy: 0, bounce: 1 });
          part('piece', e.x, e.y - 20, { life: 64, vx: 50 + Math.random() * 70, vy: -250, g: 640, spin: 0.21, name: 'truck_burnt', oy: 20, ang: e.how === 'flip' ? Math.PI : 0 });
          break;
        case 'strike': pop(e.x, e.y, T('STRIKE! {0}', [e.pts]), 'm_org'); shake = Math.max(shake, 8); break;
        case 'drone_down': if (e.pts) pop(e.x, e.y - 12, String(e.pts)); break;
        case 'smash':
          for (k = 0; k < (e.k === 'crate' ? 8 : 6); k++) {
            part('clod', e.x + (Math.random() - 0.5) * 16, e.y - 6 - Math.random() * 10, { life: 34 + Math.random() * 20, vx: 60 + Math.random() * 220, vy: -110 - Math.random() * 170, g: 640, dark: e.k === 'crate' || Math.random() < 0.4 });
          }
          part('puff', e.x, e.y - 4, { life: 10 }); part('puff', e.x + 10, e.y - 8, { life: 10, flip: true });
          if (e.k === 'bags') for (k = 0; k < 3; k++) part('piece', e.x - 8 + k * 8, e.y - 6, { life: 60, vx: 90 + k * 60, vy: -170 - Math.random() * 80, g: 700, spin: 0.2, name: 'sc_stone', oy: 6 });
          shake = Math.max(shake, 4);
          break;

        // ---- the battery (and whichever boss the mission has: its own file says what its moments look like)
        case 'boss_intro': case 'boss_start': case 'boss_phase': case 'boss_dying': case 'boss_dead':
          if (e.k && bosses[e.k] && bosses[e.k].events) { bosses[e.k].events(e, s, K); break; }
          if (e.t === 'boss_phase') {
            embers(e.x, e.y, 16, 320);
            pop(e.x, e.y - 30, e.n === 2 ? T('ONE ROTOR DOWN') : T('TWO ROTORS DOWN'), 's_lav');
            shake = Math.max(shake, 12);
            flashT = 2;
          } else if (e.t === 'boss_dying') { shake = Math.max(shake, 12); flashT = 3; }
          else if (e.t === 'boss_dead') {
            pop(e.x, e.y - 50, String(e.pts), 'm_org');
            embers(e.x, e.y, 26, 420);
            for (k = -1; k <= 1; k += 2) part('piece', e.x + k * 30, e.y - 20, { life: 110, vx: k * (90 + Math.random() * 60), vy: -300, g: 560, spin: k * 0.4, name: 'rotor0', oy: 0 });
            shake = 26; flashT = 5;
          }
          break;
        case 'launch': part('puff', e.x, e.y, { life: 8 }); break;
        case 'swoop': shake = Math.max(shake, 5); break;
        default:
          for (var bk in bosses) if (bosses[bk].misc && bosses[bk].misc(e, s, K)) break;
      }
    }
  }
  // a cloud of spice: a heap of billows about its middle, turning slowly, as thick as the cloud is
  var SPICE_COL = { red: '#c8301a', yel: '#e4aa20', org: '#d8701e' };
  function drawCloud(c) {
    var a = Math.max(0, Math.min(1, c.str || 0)) * 0.84;
    if (a <= 0.03) return;
    cx.globalAlpha = a;
    var ph = c.id * 1.7 + c.t * 0.012;
    for (var k = 0; k < 7; k++) {
      var px = c.x, py = c.y;
      if (k) { var an = ph + k * Math.PI * 2 / 6; px += Math.cos(an) * c.r * 0.58; py += Math.sin(an) * c.r * 0.44; }
      spr('cpuff_' + c.col + ((k + c.id) % 3), px, py);
    }
    cx.globalAlpha = 1;
  }
  function setBanner(top, bottom, life) { banner = { top: top, bottom: bottom || '', t: 0, life: life || 150 }; }
  function setHint(str, life) { hint = str ? { t: 0, s: str, life: life || 300 } : null; }

  // ------------------------------------------------------------------ hand-drawn animations, by the part they play
  // A.anims comes from tools/import_art.py through export_art.py: role -> { frames, ticks (by time) | px (by distance), loop }.
  // Where the art has a role it is used; where it does not, things are drawn as before. The roles asked for:
  //   yazeed.idle  yazeed.run.side  yazeed.run.hmg  yazeed.crouchwalk  yazeed.air (picked by how fast he is rising or falling)
  //   yazeed.throw  yazeed.knife  yazeed.death  yazeed.shoot.<side|hmg>.<fwd|up|diag>
  //   <rifle|bomber|door|door.bare|cmdr>[.<face>].<idle|walk|aim|fire|wind|throw|panic|startle|surrender|led|death[.<shot|blast|ram|knife>]>
  function roleLen(an) { if (an.px) return Infinity; var t = 0; for (var i = 0; i < an.ticks.length; i++) t += an.ticks[i]; return t; }
  function roleAt(role, t, dist) {
    var an = A.anims && A.anims[role];
    if (!an) return null;
    var n = an.frames.length, i;
    if (an.px) i = Math.floor((dist || 0) / an.px);
    else {
      var tot = roleLen(an), tt = an.loop ? ((t % tot) + tot) % tot : t;
      if (!an.loop && tt >= tot) return null;              // a film that has run its course hands back to the drawing underneath
      for (i = 0; i < n - 1; i++) { tt -= an.ticks[i]; if (tt < 0) break; }
    }
    return an.frames[((i % n) + n) % n];
  }
  function roleHold(role, t) {                                // the same, but it stays on its last frame
    var an = A.anims && A.anims[role];
    return an ? roleAt(role, an.px ? t : Math.min(t, roleLen(an) - 1)) : null;
  }
  function yazeedRole(p, gun, legs) {
    if (!A.anims) return null;
    var r = null, aim = p.aim === 'up' || p.aim === 'diag' ? p.aim : 'fwd';
    r = roleAt('yazeed.knife', p.knifeT) || roleAt('yazeed.throw', p.throwT);
    if (r) return r;
    if (p.air && A.anims['yazeed.air']) {
      var an = A.anims['yazeed.air'], u = (p.vy + Sim.T.JUMP_V) / (Sim.T.JUMP_V + Sim.T.MAX_FALL);
      return an.frames[Math.max(0, Math.min(an.frames.length - 1, Math.floor(u * an.frames.length)))];
    }
    if (legs === 'stand') return roleAt('yazeed.shoot.' + gun + '.' + aim, p.fireT) || (aim === 'fwd' && p.fireT > 20 ? roleAt('yazeed.idle', tick) : null);
    if (legs === 'run' || legs === 'pass') return aim === 'fwd' ? roleAt('yazeed.run.' + gun, 0, p.runD) : null;
    if (legs === 'crouch' && Math.abs(p.vx) > 1) return roleAt('yazeed.crouchwalk', 0, p.runD);
    return null;
  }
  function enemyRole(e) {
    if (!A.anims) return null;
    var k = e.k === 'door' && e.door <= 0 ? 'door.bare' : e.k, lk = e.look;
    function pick(suffix, t, dist) { return roleAt(k + '.' + lk + '.' + suffix, t, dist) || roleAt(k + '.' + suffix, t, dist); }
    function hold(suffix, t) { return roleHold(k + '.' + lk + '.' + suffix, t) || roleHold(k + '.' + suffix, t); }
    if (!e.alive) return hold('death.' + (e.how || 'shot'), e.deadT) || hold('death', e.deadT);
    if (e.st === 'panic') return pick('panic', 0, e.walkD);
    if (e.st === 'shock') return hold('startle', e.stT);
    if (e.st === 'surr') return e.captured && e.stT > 70 ? pick('led', 0, e.walkD) : pick('surrender', e.stT);
    if (e.st === 'wind') return pick('wind', e.stT);
    if (e.st === 'throw') return hold('throw', e.stT);
    if (e.st === 'aim') return hold('aim', e.stT);
    if (e.st === 'burst' || e.st === 'fire') return pick('fire', e.stT);
    if (e.moving) return pick('walk', 0, e.walkD);
    return pick('idle', tick + e.id * 7);
  }

  // ------------------------------------------------------------------ who is doing what
  function playerLegs(p) {
    if (p.air) return p.vy < 60 ? 'jump' : 'fall';
    if (p.crouch) return 'crouch';
    if (Math.abs(p.vx) > 1) return (Math.floor(p.runD / 11) % 2) ? 'pass' : 'run';
    return 'stand';
  }
  function playerFrame(p) {
    var gun = p.weapon === 'hmg' ? 'hmg' : 'side', legs = playerLegs(p), aim, hand = yazeedRole(p, gun, legs);
    if (hand) return hand;
    if (p.knifeT < 10) return 'yazeed_' + legs + '_knife' + (p.knifeT < 2 ? 1 : 2);       // the jambiya: up, and across
    if (p.throwT < 9) aim = 'throw';
    else if ((p.aim === 'up' || p.aim === 'diag') && legs !== 'crouch') aim = p.aim;
    else if ((p.aim === 'down' || p.aim === 'ddiag') && p.air) aim = p.aim;
    else aim = 'fwd';
    var name = 'yazeed_' + legs + '_' + gun + '_' + aim;
    if (!A.frames[name]) name = 'yazeed_' + legs + '_' + gun + '_fwd';
    return name;
  }
  function enemyFrame(e) {
    var walk = (Math.floor(e.walkD / 8) % 2) ? 'pass' : 'run', moving = !!e.moving, name;
    if (e.k === 'rifle') {
      var b = 'rifle_' + e.look + '_';
      if (!e.alive) name = b + 'flung';
      else if (e.st === 'panic') name = b + 'up_' + walk;                  // hands in the air, and away
      else if (e.st === 'surr' || e.st === 'shock') name = b + 'up_' + (e.captured && e.stT > 70 ? walk : 'stand');
      else if (e.st === 'aim' || e.st === 'burst' || e.st === 'cool') name = b + 'aim';
      else name = b + (moving ? walk : 'stand');
    } else if (e.k === 'bomber') {
      if (!e.alive) name = 'bomber_flung';
      else if (e.st === 'panic') name = 'bomber_up_' + walk;
      else if (e.st === 'surr' || e.st === 'shock') name = 'bomber_up_' + (e.captured && e.stT > 70 ? walk : 'stand');
      else if (e.st === 'wind') name = 'bomber_wind';
      else if (e.st === 'throw') name = 'bomber_throw';
      else name = 'bomber_' + (moving ? walk : 'stand');
    } else if (e.k === 'cmdr') {
      var cb = e.qm ? 'qm' : 'cmdr';                                  // (the Commander, or Mocha's quartermaster)
      if (e.st === 'watch') name = cb + '_stand';
      else name = e.captured && e.stT > 70 && (Math.floor(e.walkD / 8) % 2) ? cb + '_up_pass' : cb + '_up_stand';
    } else if (e.k === 'cook') {
      var cw = walk === 'pass' ? 'pass' : 'stand';
      if (!e.alive) name = 'cook_flung';
      else if (e.st === 'panic') name = 'cook_up_' + cw;
      else if (e.st === 'surr' || e.st === 'shock') name = 'cook_up_' + (e.captured && e.stT > 70 ? cw : 'stand');
      else if (e.st === 'scoop') name = 'cook_scoop';
      else if (e.st === 'fling') name = e.stT < 8 ? 'cook_fling' : 'cook_stand';
      else if (e.st === 'swingw') name = 'cook_raise';
      else if (e.st === 'swing') name = e.stT < 10 ? 'cook_swing' : 'cook_stand';
      else name = 'cook_' + (moving ? cw : 'stand');
    } else {
      if (!e.alive) name = 'door_flung';
      else if (e.st === 'surr' || e.st === 'shock') name = 'door_up_' + (e.captured && e.stT > 70 ? walk : 'stand');
      else if (e.st === 'stagger') name = 'door_up_stand';
      else if (e.door <= 0) name = (e.st === 'aim' || e.st === 'burst' || e.st === 'cool') ? 'door_aim' : 'door_bare_' + (moving ? walk : 'stand');
      else if (e.st === 'lean' || e.st === 'fire' || e.st === 'rec') name = 'door_lean';
      else if (e.st === 'bashw') name = 'door_back';
      else if (e.st === 'bash') name = e.stT < 10 ? 'door_shove' : 'door_stand';
      else name = 'door_' + (moving ? walk : 'stand');
    }
    return name;
  }

  // ------------------------------------------------------------------ machines
  function wheelName(dist, v) {
    if (Math.abs(v) > 150) return 'wheelf' + ((tick >> 1) & 1);
    return 'wheel' + (3 - (((Math.floor(dist / 2.4) % 4) + 4) % 4));
  }
  // Salem's car (the armoured truck since build 17): the body rides on its springs, the wheels stay on the road, and Yazeed stands up in the roof ring behind the cab
  function drawCar(s) {
    var c = s.car, p = s.p, D = Sim.D;
    if (!c || c.st === 'away') return;
    var riding = s.mode === 'drive', wreck = c.st === 'wreck', moving = Math.abs(c.vx) > 20, wr = A.rig.car.wheel;
    var bob = (!c.air && moving && !wreck) ? (Math.floor(c.wheel / 13) & 1) : 0;
    var dy = bob + (c.squash > 4 ? 2 : (c.squash > 0 ? 1 : 0)), droop = c.air && !wreck ? 2 : 0;
    // (the armoured car rides on the bigger wheels, their centres that much higher off the road)
    var big = A.rig.car.big || 0, wn = (big ? 'b' : '') + (wreck ? 'wheel0' : wheelName(c.wheel, c.vx)), lift = big ? big - A.rig.car.r : 0;
    cx.save();
    cx.translate(Math.round(c.x), Math.round(c.y) - 10);
    if (c.ang) cx.rotate(c.ang);
    if (riding && !p.dead && !(p.inv > 0 && (p.inv >> 1) % 2)) {
      var aim = p.throwT < 9 ? 'throw' : (p.aim === 'diag' ? 'diag' : 'fwd');
      spr('yazeed_stand_hmg_' + aim, D.BED - (p.fireT < 2 ? 1 : 0), 10 - D.STAND + dy, false);
    }
    spr(wreck ? 'shass_burnt' : (riding && p.hurtT < 3 ? 'shass!' : 'shass'), 0, 10 + dy);
    spr(wn, -wr, 1 - lift + droop); spr(wn, wr, 1 - lift + droop);
    cx.restore();
    if (c.st === 'wait' && (tick >> 4) % 2) { text('s_lav', T('GET IN'), c.x - 24, c.y - 66, 'c'); spr('hud_alert', c.x - 24, c.y - 52); }
  }
  function carSmoke(s, paused) {
    var c = s.car, p = s.p;
    if (!c || paused || c.st === 'away') return;
    if (c.st === 'wreck') { if (tick % 3 === 0) part('smoke', c.x + (Math.random() - 0.5) * 50, c.y - 20 - Math.random() * 16, { life: 30, vx: -10, vy: -46 }); return; }
    if (s.mode !== 'drive') return;
    if (p.plates <= 1 && tick % 5 === 0) part('smoke', c.x + 36, c.y - 30, { life: 26, vx: -c.vx * 0.2 - 10, vy: -34 });
    // on the beach the back wheels throw sand up behind it
    var Wd = stageOf(s.L).world, onSand = Wd.XR1 && c.x > Wd.XR1 + 420 && c.x < Wd.XR2 - 420;
    if (onSand && !c.air && c.vx > 60) {
      part('clod', c.x - 34 + Math.random() * 4, c.y - 2, { life: 16 + Math.random() * 14, vx: c.vx * 0.55 - 40 - Math.random() * 90, vy: -60 - Math.random() * 130, g: 600,
                                                          col: ['#6a4220', '#9c7038', '#f0d9a0'][Math.floor(Math.random() * 3)] });
      if (tick % 3 === 0) part('sand', c.x - 36 - Math.random() * 8, c.y, { life: 26 + Math.random() * 10, vx: c.vx * 0.74, vy: -8 - Math.random() * 6, flip: Math.random() < 0.5 });
    } else if (!c.air && c.vx > 90 && tick % 6 === 0) part('puff', c.x - 44, c.y - 3, { life: 8, vx: -30 });
  }
  function drawTruck(s, t, paused) {
    var gx = Sim.ext.drive.gunnerX(t), flip = t.face < 0, wr = A.rig.car.wheel, body = 'truck_' + t.paint;
    if (t.st === 'flip') {
      cx.save();
      cx.translate(Math.round(t.x), Math.round(t.y) - 20);
      cx.rotate(t.ang);
      spr(body, 0, 20, flip); spr('wheel0', -wr, 11); spr('wheel0', wr, 11);
      cx.restore();
      return;
    }
    if (t.st !== 'ok') return;
    var moving = t.seen && t.mode !== 'block', bob = moving ? (Math.floor(Math.abs(t.wheel) / 13) & 1) : 0;
    if (t.gun > 0) {
      var rec = t.gst === 'burst' && (t.gT % 7) < 3 ? 1 : 0;
      spr('rifle_angry_aim', gx + rec, t.y - 22 + bob, true);
      spr('truck_gun', gx - 6 + rec, t.y - 22 + bob);
      if (t.gst === 'tell' && (tick >> 2) % 2) spr('hud_alert', gx - 2, t.y - 66);
    }
    spr(body + (t.hurtT < 2 ? '!' : ''), t.x, t.y + bob, flip);
    var wn = wheelName(Math.abs(t.wheel), moving ? t.vx : 0);
    spr(wn, t.x - wr, t.y - 9); spr(wn, t.x + wr, t.y - 9);
    // still coming in: it flashes, and his shots glance off it
    if (!Sim.ext.drive.staged(s, t.x) && (tick >> 2) % 2) { cx.globalAlpha = 0.32; spr(body + '!', t.x, t.y + bob, flip); cx.globalAlpha = 1; }
    if (!paused && t.hp <= 3 && tick % 5 === 0) part('smoke', t.x + t.face * 34, t.y - 28, { life: 24, vx: -20, vy: -34 });
  }
  function dotted(x0, y0, x1, y1, gap, col) {
    var dx = x1 - x0, dy = y1 - y0, n = Math.floor(Math.sqrt(dx * dx + dy * dy) / gap), ph = (tick >> 1) % 2;
    cx.fillStyle = col;
    for (var i = 1 + ph; i < n; i += 2) cx.fillRect(Math.round(x0 + dx * i / n), Math.round(y0 + dy * i / n), 1, 1);
  }
  function drawDrone(s, d) {
    if (d.st === 'gone') return;
    var f = 'kdrone' + ((tick >> 1) & 1);
    if (d.st === 'tell') {
      // it shows where it means to come down
      var gy = Sim.groundY(s.L, clamp(d.tx, 0, s.L.width - 1));
      dotted(d.x, d.y + 5, d.tx, d.ty, 5, '#ff4030');
      cx.fillStyle = (tick >> 2) % 2 ? '#ff4030' : '#ffe06a';
      cx.fillRect(Math.round(d.tx) - 5, Math.round(gy) - 1, 11, 1); cx.fillRect(Math.round(d.tx), Math.round(gy) - 3, 1, 5);
      spr(f + ((tick >> 2) % 2 ? '!' : ''), d.x, d.y);
    } else if (d.st === 'dive') {
      sprRot(f, d.x, d.y, Math.atan2(-d.vx, d.vy) * 0.8, false);
      cx.fillStyle = 'rgba(255,240,200,0.5)';
      cx.fillRect(Math.round(d.x - d.vx * 0.03), Math.round(d.y - d.vy * 0.03), 1, 1); cx.fillRect(Math.round(d.x - d.vx * 0.05), Math.round(d.y - d.vy * 0.05), 1, 1);
    } else {
      spr(f, d.x, d.y);
      if (!Sim.ext.drive.staged(s, d.x) && (tick >> 2) % 2) { cx.globalAlpha = 0.42; spr(f + '!', d.x, d.y); cx.globalAlpha = 1; }       // (still coming in)
    }
  }
  // whichever boss the mission has
  function drawBoss(s, b, paused) {
    if (b.kind === 'boat') drawBoat(s, b, paused);
    else if (bosses[b.kind]) bosses[b.kind].draw(s, b, paused, K);
  }
  // the pride of the coast: hull, four rotors (fewer as the fight goes on), the gun under its bow
  function drawBoat(s, b, paused) {
    var R = A.rig.boat, p = s.p, face = b.face || -1, lost = b.phase - 1, i;
    var gxw = b.x + face * R.gun[0], gyw = b.y + R.gun[1];
    // the gun swings round after him rather than snapping
    var want = Math.atan2((p.y - 17) - gyw, (p.x - gxw) * face);
    if (want < 0.15) want = want < -Math.PI / 2 ? Math.PI - 0.15 : 0.15;
    if (want > Math.PI - 0.15) want = Math.PI - 0.15;
    if (b.st === 'gun' || b.st === 'guntell') gunAng += clamp(want - gunAng, -0.14, 0.14); else if (!paused) gunAng += clamp(1.9 - gunAng, -0.05, 0.05);
    cx.save();
    cx.translate(Math.round(b.x), Math.round(b.y));
    cx.rotate(clamp(b.tilt || 0, -1.3, 1.3) * 0.1);
    if (face < 0) cx.scale(-1, 1);
    var white = b.hurtT < 2 || (b.st === 'dying' && (tick >> 1) % 3 === 0);
    spr(white ? 'boat!' : 'boat', 0, 0);
    for (i = 0; i < R.rotors.length; i++) {
      if (i >= 4 - lost && i >= 2) continue;                    // the far ones go first
      spr('rotor' + ((tick + i) % 3), R.rotors[i][0], R.rotors[i][1]);
    }
    cx.save();
    cx.translate(R.gun[0], R.gun[1]);
    cx.rotate(gunAng);
    spr('boss_gun', 0, 0);
    cx.restore();
    if (b.st === 'bombtell' && (tick >> 2) % 2) spr('hud_alert', -6, 34);
    cx.restore();
    if (b.st === 'guntell') dotted(gxw, gyw, p.x, p.y - 17, 6, '#ff4030');
    if (paused) return;
    // what it trails
    for (i = 2; i < 4; i++) {
      if (i >= 4 - lost && tick % 4 === i - 2) part('smoke', b.x + face * R.rotors[i][0], b.y + R.rotors[i][1] + 2, { life: 30, vx: -b.vx * 0.2, vy: -40 });
    }
    if (b.st === 'dying' && tick % 2 === 0) part('smoke', b.x + (Math.random() - 0.5) * 70, b.y - 6 + (Math.random() - 0.5) * 20, { life: 34, vx: 0, vy: -50 });
    if (b.st === 'intro' && b.y < 112 && b.y > 66 && tick % 2 === 0) part('drip', b.x + (Math.random() - 0.5) * 70, b.y + 18, { life: 9, vy: 60, g: 500 });
    if (b.st === 'swoop' && tick % 2 === 0) part('puff', b.x - (b.vx > 0 ? 40 : -40), Sim.groundY(s.L, clamp(b.x, 0, s.L.width - 1)) - 3, { life: 9, flip: b.vx < 0 });
  }

  // ------------------------------------------------------------------ one frame
  function draw(s, ui) {
    tick++;
    var p = s.p, L = s.L, i, cam = Math.round(s.cam), camY = Math.round(s.camY || 0), sx = 0, sy = 0, paused = !!ui.paused;
    if (shake > 0) {
      if (!opts.calm) { sx = Math.round((Math.random() - 0.5) * Math.min(4, shake * 0.5)); sy = Math.round((Math.random() - 0.5) * Math.min(3, shake * 0.4)); }
      shake -= paused ? 0 : 1;
    }
    var SG = stageOf(L), ly = SG.layers, b = s.boss, own = L.fly && bosses.fly && bosses.fly.back;     // (Taiz draws its own sky and town: render_fly.js)
    // (Taiz's opening draws back from Yazeed on foot to the Apache's picture: while it does, the world is drawn larger than
    // the canvas would have it, by as much as the picture is narrower than the canvas)
    var ks = s.viewW && Math.abs(W / s.viewW - 1) > 0.002 ? W / s.viewW : 1;
    if (ks !== 1) { cx.save(); cx.scale(ks, ks); }
    if (own) bosses.fly.back(s, paused, K);
    else { wrapLayer(ly.sky, s.cam); if (ly.sea) wrapLayer(ly.sea, s.cam); wrapLayer(ly.far, s.cam); }
    cx.save();
    cx.translate(sx, 0);
    // it comes up out of the sea, behind the beach
    if (b && b.kind === 'boat' && b.st === 'intro') { cx.save(); cx.translate(-cam, sy); drawBoss(s, b, paused); cx.restore(); }
    if (!own) stripLayer(ly.play, s.cam, sy);
    cx.translate(-cam, sy - camY);

    // what stands beside the road
    if (L.scenery) {
      var base = (SG.world.ROAD_Y || 184) - 16;
      for (i = 0; i < L.scenery.length; i++) {
        var sc = L.scenery[i];
        if (sc.x > cam - 70 && sc.x < cam + W + 70) spr('sc_' + sc.k, sc.x, sc.y || base);
      }
    }
    // fires in the level (Mocha's roasters): now and then a spark out of the firebox door
    if (L.fires && !paused) for (i = 0; i < L.fires.length; i++) {
      var fire = L.fires[i];
      if (fire[0] > cam - 20 && fire[0] < cam + W + 20 && (tick + i * 5) % 9 === 0) part('ember', fire[0] + (Math.random() - 0.5) * 12, fire[1] - 4, { life: 16 + Math.random() * 14, vx: (Math.random() - 0.5) * 40, vy: -40 - Math.random() * 50, g: 120 });
    }
    for (i = 0; i < decals.length; i++) spr('scorch', decals[i].x, decals[i].y + 1, false, 0.9);
    for (i = 0; i < posts.length; i++) spr('post', posts[i].x, posts[i].y);
    // the launcher the battery is there for, or what is left of it
    if (L.boss && s.site) {
      var lx = L.boss.launcher[0], lyy = L.boss.launcher[1];
      if (lx < cam + W + 20) {
        if (s.site.launcher === 'wreck') {
          spr('launcher_wreck', lx, lyy);
          sprRot('boat_burnt', b ? b.x : lx + 40, (b ? b.y : lyy - 26) + 6, 0.3, (b ? b.face : -1) < 0);
          if (!paused && tick % 4 === 0) part('smoke', (b ? b.x : lx + 40) + (Math.random() - 0.5) * 80, lyy - 30 - Math.random() * 20, { life: 40, vx: 6, vy: -40 });
        } else spr('launcher', lx, lyy);
      }
    }
    // things standing in the level
    for (i = 0; i < s.props.length; i++) {
      var o = s.props[i];
      if (o.gone) continue;
      if (o.k === 'mine') {
        var fm = SG.fixed.mine;
        spr('mine', fm[0], fm[1]);
        if (s.mineSpotted && (tick >> 3) % 2) spr('hud_alert', o.x, fm[1] - 3);
      } else if (o.k === 'rmine') {
        spr('rmine_flag', o.x + 9, o.y);
        spr('rmine' + (Math.floor(tick / 6) & 1), o.x, o.y);
        if ((tick >> 3) % 2 && o.x < cam + W) spr('hud_alert', o.x + 10, o.y - 27);
      } else if (o.k === 'rbags') spr('rbags', o.x, o.y + 1);
      else if (o.k === 'vent') {
        // a grating over the steam: red hot while it hisses, a column of steam when it blows
        spr(o.st === 'hiss' && (tick >> 2) % 2 ? 'vent_hot' : 'vent', o.x, o.y + 1);
        if (!paused && o.st === 'hiss' && tick % 5 === 0) part('wisp', o.x + (Math.random() - 0.5) * 14, o.y - 4, { life: 18, vy: -50, vx: (Math.random() - 0.5) * 20 });
      }
      else if (o.k === 'drum') {
        spr('drum_' + o.paint + ((o.fuse >= 0 ? (tick >> 1) % 2 : (o.hp < 2 && (tick >> 3) % 2)) ? '!' : ''), o.x, o.y);
        if (o.fuse >= 0 && (tick >> 1) % 2) spr('fx_spark', o.x + 1, o.y - 22);
      }
      else if (o.k === 'crate') {
        var gr = o.gives === 'gren';
        spr(gr ? 'crate_g' : 'crate_h', o.x, o.y + 1);
        if ((tick >> 4) % 2) text('s_org', gr ? 'G' : 'H', o.x - 2, o.y - 27);
      }
      else if (o.k === 'detainee' && !L.fly) {          // (Taiz's, on the roofs with their lanterns and the rope: render_fly.js)
        var dn = o.look || 'det';                       // (the Souq's shopkeepers have their own clothes)
        if (o.st === 'tied') spr(dn + '_tied', o.x, o.y);
        else if (o.st === 'freed') spr(dn + '_freed', o.x + 5, o.y);
        else spr((Math.floor(o.t / 7) % 2) ? dn + '_walk1' : dn + '_walk2', o.x, o.y, true);
      }
      else if (o.k === 'spice') spr('spice_' + o.col, o.x, o.y);
    }
    // their pickups
    if (s.trucks) for (i = 0; i < s.trucks.length; i++) { if (L.fly && bosses.fly && bosses.fly.tint) SRC = bosses.fly.tint(s, s.trucks[i]); drawTruck(s, s.trucks[i], paused); }
    SRC = null;
    // what is left of a boss that stays on the floor, behind whoever stands about it; and a boss that is part of the
    // place (the Souq's Tailor and his dummies), drawn whether or not its fight has begun
    if (b && b.st === 'dead' && bosses[b.kind] && bosses[b.kind].wreck) bosses[b.kind].wreck(s, b, paused, K);
    for (var bsk in bosses) if (bosses[bsk].scene) bosses[bsk].scene(s, paused, K);
    // the Scorpion's men, far ones first
    var men = s.enemies.slice().sort(function (a, c2) { return a.y - c2.y; }), tint = L.fly && bosses.fly && bosses.fly.tint;
    for (i = 0; i < men.length; i++) {
      var e = men[i];
      if (e.st === 'gone') continue;
      if (tint) SRC = tint(s, e);
      if (e.ext && bosses[e.ext] && bosses[e.ext].man && bosses[e.ext].man(s, e, K)) continue;       // (a boss's own men draw themselves)
      var hand = enemyRole(e), name = hand || enemyFrame(e), flip = e.face < 0;
      if (e.k === 'cmdr') {
        var cbn = e.qm ? 'qm_up_stand' : 'cmdr_up_stand';
        if (e.st === 'fall') sprRot(cbn, e.x, e.y - 24, -e.stT * 0.22, false, 24);
        else if (e.st === 'daze') { sprRot(cbn, e.x, e.y - 5, -Math.PI / 2, false); if ((tick >> 3) % 2) spr('fx_spark2', e.x - 50 + ((tick >> 4) % 3) * 5, e.y - 22); }
        else spr(name, e.x, e.y - (e.st === 'watch' && (e.shoutT % 96) < 10 ? 1 : 0), flip);
        if (e.st === 'surr' && !e.captured && (tick >> 4) % 2) text('s_lav', T('WALK IN'), e.x, e.y - 62, 'c');
        continue;
      }
      if (!e.alive && hand) {
        if (e.deadT < 70 && (e.deadT < 40 || (e.deadT >> 1) % 2)) spr(name, e.x, e.y, flip);
        continue;
      }
      if (!e.alive) {
        if (e.air) { if (spin[e.id]) sprRot(name, e.x, e.y - 16, e.deadT * 0.4, false, 16); else spr(name, e.x, e.y, flip); }
        else if (e.deadT < 70 && (e.deadT < 40 || (e.deadT >> 1) % 2)) sprRot(name, e.x, e.y - 4, flip ? Math.PI / 2 : -Math.PI / 2, false);
        continue;
      }
      if (e.emerge > 0) {
        // out of the dark of a doorway: he comes into the light over a few frames
        spr(name, e.x, e.y, flip, Math.max(0.15, 1 - e.emerge / Sim.T.EMERGE));
        continue;
      }
      if (e.hurtT < 3 && A.frames[name + '!']) name += '!';
      var rx = (e.st === 'burst' && e.stT % 8 < 3) || (e.st === 'fire' && (e.stT < 5 || (e.stT > 15 && e.stT < 20))) ? -e.face : 0;
      // a man behind the bags keeps his head down, and comes up over a few frames to aim
      var down = e.covered && e.hostile ? (Sim.ducked(e) ? 9 : (e.st === 'aim' && e.stT < 4 ? 9 - e.stT * 3 : 0)) : 0;
      if (e.st === 'stagger') rx = (e.stT >> 1) % 2 ? 1 : -1;         // reeling
      spr(name, e.x + rx, e.y + down, flip, 1, down);
      // still coming in, out at the edge: he flashes, and nothing hurts him yet
      if (Sim.guarded(s, e) && (tick >> 2) % 2 && A.frames[name.replace('!', '') + '!']) {
        cx.globalAlpha = 0.42; spr(name.replace('!', '') + '!', e.x + rx, e.y + down, flip, 1, down); cx.globalAlpha = 1;
      }
      if (e.k === 'door' && e.door > 0 && e.door <= 9) {
        // the door shows what it has taken
        var dp = A.points[name.replace('!', '')];
        if (dp) spr(e.door <= 4 ? 'door_marks2' : 'door_marks1', e.x + rx + e.face * (dp[0] + 3), e.y - dp[1] + 9, flip);
      }
      if (e.k === 'bomber' && e.st === 'wind' && (tick >> 1) % 2) spr('fx_spark2', e.x - e.face * 4, e.y - 46);
      if (e.st === 'surr' && !e.captured && (tick >> 4) % 2) text('s_lav', T('WALK IN'), e.x, e.y - 50, 'c');
    }
    SRC = null;
    // the sandbags stand in front of whoever hides behind them
    for (i = 0; i < s.props.length; i++) {
      var cvp = s.props[i];
      if (cvp.k === 'detainee' && cvp.look && !cvp.gone) { spr('counter_' + cvp.look.slice(5), cvp.cx, cvp.cy + 1); continue; }     // (his counter, in front of him)
      if (cvp.k !== 'cover' || cvp.gone) continue;
      if (cvp.bar) {
        // a barricade: whole, knocked about, nearly gone; a flash where it is hit
        var bf = cvp.hp / cvp.hp0, bn = 'barr' + (bf > 0.6 ? 0 : (bf > 0.3 ? 1 : 2));
        spr(bn, cvp.x, cvp.y + 1);
        if (cvp.hurtT < 2) { cx.globalAlpha = 0.5; spr(bn + '!', cvp.x, cvp.y + 1); cx.globalAlpha = 1; }
        continue;
      }
      if (cvp.art) spr(cvp.art, cvp.x, cvp.y + 1);                                    // a sprite of its own, standing at the cover's x
      else if (SG.fixed.bags) spr('bags', SG.fixed.bags[0], SG.fixed.bags[1]);           // (the Strait's, drawn exactly where the painting had them)
    }
    if (tint) SRC = tint(s, null);
    for (i = 0; i < s.pickups.length; i++) {
      var q = s.pickups[i];
      if (!q.gone) spr(q.k === 'hmg' ? 'pick_hmg' : (q.k === 'bean' ? 'pick_bean' : (q.k === 'chilli' ? 'pick_chilli' : 'pick_gren')), q.x, q.y - (q.air ? 0 : ((tick >> 3) % 2)));
    }
    SRC = null;
    // a boss on the ground (the Big Roaster) stands behind Yazeed, not over him
    var under = b && bosses[b.kind] && bosses[b.kind].under;
    if (under) drawBoss(s, b, paused);
    // Salem's pickup, and Yazeed: in the back of it, or on his own feet
    drawCar(s);
    carSmoke(s, paused);
    if (s.mode !== 'drive' && s.mode !== 'fly') {
      if (tint) SRC = tint(s, { x: p.x, y: p.y, h: 34 });
      if (p.dead && A.anims && A.anims['yazeed.death']) {
        if ((p.dead >> 2) % 2 || p.dead < 44) spr(roleHold('yazeed.death', p.dead), p.x, p.y, p.face < 0);
      } else if (p.dead) {
        if (p.air || p.dead < 20) spr('yazeed_jump_side_fwd', p.x, p.y, p.face < 0);
        else if ((p.dead >> 2) % 2 || p.dead < 44) sprRot('yazeed_stand_side_fwd', p.x, p.y - 5, p.face < 0 ? Math.PI / 2 : -Math.PI / 2, false);
      } else if (!(p.inv > 0 && (p.inv >> 1) % 2)) {
        // (a crouching walk is a shuffle: the one frame, lifted a dot on every other step)
        var snz = p.sneezeT > Sim.T.P_SNEEZE - 6 ? 1 : 0;                              // (the Souq: doubled up with a sneeze)
        spr(playerFrame(p), p.x - (p.fireT < 2 ? p.face : 0) + snz * p.face, p.y - (p.crouch && Math.abs(p.vx) > 1 && Math.floor(p.runD / 5) % 2 ? 1 : 0) + snz, p.face < 0);
      }
      SRC = null;
    }
    // what flies
    if (s.drones) for (i = 0; i < s.drones.length; i++) drawDrone(s, s.drones[i]);
    if (b && !under && !(b.kind === 'boat' && b.st === 'intro') && b.st !== 'dead') drawBoss(s, b, paused);
    if (b && under && bosses[b.kind].over) bosses[b.kind].over(s, b, paused, K);
    if (b && b.st === 'swooptell' && (tick >> 2) % 2) {
      var ax = b.dir < 0 ? s.cam + W * s.laneL + 4 : s.cam + W * (1 - s.laneR) - 4;
      spr('hud_alert', ax, b.lowY + 4);
    }
    // a mode that lights its own picture does it here, over everything so far and under the shots, the flashes and the smoke (Taiz)
    for (var pbk in bosses) if (bosses[pbk].post) bosses[pbk].post(s, paused, K);
    // things in the air. (The boat's bombs throw a shadow where they will land, growing as they come down.)
    for (i = 0; i < s.bombs.length; i++) {
      var sb = s.bombs[i];
      if (sb.gone || sb.kind !== 'bbomb' || !sb.air) continue;
      var sgx = clamp(sb.x, 0, s.L.width - 1), sgy = Sim.groundY(s.L, sgx), fall = sgy - sb.y;
      if (fall <= 0) continue;
      var stt = (-sb.vy + Math.sqrt(sb.vy * sb.vy + 2 * (sb.g || 560) * fall)) / (sb.g || 560), lx = Math.round(sb.x + sb.vx * stt);
      var near = clamp(1 - fall / 110, 0, 1), sw = Math.round(6 + near * 18);
      cx.fillStyle = 'rgba(40,22,8,' + (0.32 + near * 0.36).toFixed(2) + ')';
      cx.fillRect(lx - (sw >> 1), Math.round(Sim.groundY(s.L, clamp(lx, 0, s.L.width - 1))) - 1, sw, 2);
      cx.fillRect(lx - (sw >> 1) + 2, Math.round(Sim.groundY(s.L, clamp(lx, 0, s.L.width - 1))) - 2, sw - 4, 1);
    }
    for (i = 0; i < s.bombs.length; i++) {
      var bm = s.bombs[i];
      if (bm.gone) continue;
      if (bm.kind === 'gren') spr('fx_gren' + ((bm.t >> 2) % 4), bm.x, bm.y - 2);
      else if (bm.kind === 'bbomb') sprRot(bm.art || 'bbomb', bm.x, bm.y - 4, bm.art ? bm.t * 0.3 : Math.atan2(bm.vx, -bm.vy), false);
      else {
        spr('fx_stick' + (bm.air ? (bm.t >> 2) % 4 : 0), bm.x, bm.y - 3);
        if ((tick >> 1) % 2) spr('fx_spark', bm.x + 2, bm.y - 7);
      }
    }
    for (i = 0; i < s.bullets.length; i++) {
      var bl = s.bullets[i];
      if (bl.gone || (bl.own && bl.age < (bl.hide || 2))) continue;       // a shot leaves from the middle of him: it shows once it is past the muzzle
      if (bl.heavy || bl.big) { sprRot('fx_heavy', bl.x, bl.y, Math.atan2(bl.vy, bl.vx), false); continue; }
      if (bl.bean) { spr(bl.hot ? 'fx_bean_hot' : 'fx_bean', bl.x, bl.y, bl.vx > 0); continue; }
      if (bl.art) { sprRot(bl.art, bl.x, bl.y, bl.spin ? bl.age * 0.45 * bl.spin : Math.atan2(bl.vy, bl.vx), false); continue; }      // (the Tailor's shears, turning over, and his pins)
      var nm = bl.own ? (bl.hmg ? 'fx_tracer_h' : 'fx_tracer') : 'fx_tracer_e';
      // (his shots fly on off the edge of the picture)
      if (Math.abs(bl.vy) < 2) spr(nm, bl.x, bl.y, bl.own ? bl.vx < 0 : bl.vx > 0);
      else sprRot(nm, bl.x, bl.y, Math.atan2(bl.vy, bl.vx) + (bl.own ? 0 : Math.PI), false);
    }
    // the Souq's clouds of spice, over whoever is in them
    for (i = 0; i < s.clouds.length; i++) drawCloud(s.clouds[i]);
    // the roasting house's vents, blowing: the steam goes up in front of whoever is standing in it
    for (i = 0; i < s.props.length; i++) {
      var vo = s.props[i];
      if (vo.k === 'vent' && !vo.gone && vo.st === 'blast') spr('steam' + ((tick >> 2) % 3), vo.x, vo.y + 1, (tick >> 3) % 2 === 1);
    }
    // sparks, smoke, brass
    var dt = paused ? 0 : 1 / 60;
    for (i = parts.length - 1; i >= 0; i--) {
      var pt = parts[i];
      if (pt.delay > 0) { pt.delay -= paused ? 0 : 1; continue; }
      pt.t += paused ? 0 : 1;
      if (pt.t > pt.life) { parts.splice(i, 1); continue; }
      pt.vy += pt.g * dt; pt.x += pt.vx * dt; pt.y += pt.vy * dt; pt.ang += paused ? 0 : pt.spin;
      var u = pt.t / pt.life;
      if (tint) SRC = (pt.k === 'smoke' || pt.k === 'puff' || pt.k === 'wisp' || pt.k === 'casing' || pt.k === 'piece' || pt.k === 'sand') ? tint(s, null) : null;
      if (pt.k === 'muzzle') { if (pt.ang) sprRot(pt.name, pt.x, pt.y, pt.ang, pt.flip); else spr(pt.name, pt.x, pt.y, pt.flip); }
      else if (pt.k === 'spark') spr(pt.name, pt.x, pt.y);
      else if (pt.k === 'puff') spr('fx_puff', pt.x, pt.y - u * 3, pt.flip, 1 - u * 0.7);
      else if (pt.k === 'smoke') spr('fx_bsmoke' + (u < 0.25 ? 0 : (u < 0.6 ? 1 : 2)), pt.x, pt.y, false, u < 0.5 ? 0.9 : 0.9 * (1 - (u - 0.5) * 1.7));
      else if (pt.k === 'wisp') spr('fx_smoke', pt.x, pt.y, false, 0.85 * (1 - u));
      else if (pt.k === 'casing') spr('fx_casing', pt.x, pt.y);
      else if (pt.k === 'ember') { cx.fillStyle = u < 0.5 ? '#fff0a0' : '#ff9a2a'; cx.fillRect(Math.round(pt.x), Math.round(pt.y), 1, 1); }
      else if (pt.k === 'drip') { cx.fillStyle = u < 0.5 ? '#e8fbff' : '#8fd4e8'; cx.fillRect(Math.round(pt.x), Math.round(pt.y), 1, 2); }
      else if (pt.k === 'boom') {
        var fi = Math.min(A.booms[pt.set] - 1, pt.t >> 1);
        spr(pt.set + (fi < 10 ? '0' : '') + fi, pt.x, pt.y);
      }
      else if (pt.k === 'clod') { cx.fillStyle = pt.col || (pt.dark ? '#7a4c24' : '#c69a54'); cx.fillRect(Math.round(pt.x), Math.round(pt.y), 2, 2); }
      else if (pt.k === 'sand') spr('fx_sand' + (u < 0.3 ? 0 : (u < 0.65 ? 1 : 2)), pt.x, pt.y - u * 5, pt.flip, 1 - u * 0.6);
      else if (pt.k === 'piece') {
        if (pt.bounce && pt.vy > 0) {
          var py = Sim.groundY(s.L, clamp(pt.x, 0, s.L.width - 1)) - 9;
          if (pt.y > py) { pt.y = py; if (pt.vy > 70) pt.vy = -pt.vy * 0.5; else { pt.vy = 0; pt.g = 0; } }
        }
        if (pt.t < pt.life - 20 || (pt.t >> 1) % 2) sprRot(pt.name, pt.x, pt.y, pt.ang, false, pt.oy);
      }
      else if (pt.k === 'slash') spr(pt.t < 4 ? 'fx_slash0' : 'fx_slash1', p.x + (pt.flip ? -1 : 1) * 15, p.y - (p.crouch ? 10 : 20), pt.flip);
      else if (pt.k === 'spray') spr('fx_sneeze', pt.x, pt.y, pt.flip, 1 - u * 0.6);
      else if (pt.k === 'redpuff') spr('fx_redpuff' + (pt.k2 || 0), pt.x, pt.y, false, 1 - u * 0.8);
      else if (pt.k === 'alert') { if ((pt.t >> 2) % 2 === 0) spr('hud_alert', pt.x, pt.y); }
      else if (pt.k === 'gunfall') { cx.fillStyle = '#2a261c'; cx.fillRect(Math.round(pt.x) - 6, Math.round(pt.y), 12, 2); cx.fillStyle = '#8a4c18'; cx.fillRect(Math.round(pt.x) - 7, Math.round(pt.y), 4, 2); }
    }
    SRC = null;
    for (i = popups.length - 1; i >= 0; i--) {
      var pu = popups[i];
      pu.t += paused ? 0 : 1;
      if (pu.t > 46) { popups.splice(i, 1); continue; }
      if (pu.t < 36 || (pu.t >> 1) % 2) text(pu.f, pu.s, pu.x, pu.y - pu.t * 0.35, 'c');
    }
    if (opts.boxes) boxes(s);
    cx.restore();
    // what passes close to the lens
    if (!own) { cx.save(); cx.translate(sx, 0); stripLayer(ly.fore, s.cam, sy); cx.restore(); }
    if (ks !== 1) cx.restore();
    if (flashT > 0) { if (!opts.calm) { cx.fillStyle = 'rgba(255,244,210,' + (0.16 * Math.min(4, flashT)) + ')'; cx.fillRect(0, 0, W, H); } flashT -= paused ? 0 : 1; }
    if (zoom !== 1) {
      // the HUD on its own canvas, at its own size (cleared even when there is none: the shell lays it over the world)
      var wcx = cx, wW = W, wH = H;
      cx = hudCx; W = HW; H = HH; K.H = H;
      cx.clearRect(0, 0, W, H);
      if (!ui.noHud) hud(s, ui);
      if (ui.dim) dimOver('rgba(8,10,24,' + ui.dim + ')', true);
      cx = wcx; W = wW; H = wH; K.H = H;
    } else if (!ui.noHud) hud(s, ui);
    if (ui.dim) { cx.fillStyle = 'rgba(8,10,24,' + ui.dim + ')'; cx.fillRect(0, 0, W, H); }
  }
  // a colour over the picture: over all of it, or (on the HUD's own canvas) over only what is drawn there, so that laid
  // over the world it darkens as much as the world does and no more
  function dimOver(c, onlyDrawn) {
    if (onlyDrawn) cx.globalCompositeOperation = 'source-atop';
    cx.fillStyle = c; cx.fillRect(0, 0, W, H);
    cx.globalCompositeOperation = 'source-over';
  }

  function boxes(s) {
    var L = s.L, i, p = s.p, b = Sim.playerBox(p);
    cx.strokeStyle = '#00ff88'; cx.lineWidth = 1;
    if (s.mode === 'drive') b = Sim.ext.drive.carBox(s.car);
    if (s.mode === 'fly') b = Sim.ext.fly.heliBox(s.heli);
    cx.strokeRect(b.x0 + 0.5, b.y0 + 0.5, b.x1 - b.x0, b.y1 - b.y0);
    cx.strokeStyle = '#ff4466';
    for (i = 0; i < s.enemies.length; i++) { var e = s.enemies[i], eh = e.alive && Sim.ducked(e) ? 18 : e.h; if (e.alive) cx.strokeRect(e.x - e.hw + 0.5, e.y - eh + 0.5, e.hw * 2, eh); }
    if (s.trucks) for (i = 0; i < s.trucks.length; i++) { var t = s.trucks[i], D = Sim.D; if (t.st === 'ok') { cx.strokeRect(t.x - D.TRUCK_HW + 0.5, t.y - D.TRUCK_H + 0.5, D.TRUCK_HW * 2, D.TRUCK_H); if (t.gun > 0) cx.strokeRect(Sim.ext.drive.gunnerX(t) - 8 + 0.5, t.y - 62 + 0.5, 16, 28); } }
    if (s.drones) for (i = 0; i < s.drones.length; i++) { var d = s.drones[i]; if (d.st !== 'gone') cx.strokeRect(d.x - 11 + 0.5, d.y - 8 + 0.5, 22, 16); }
    if (s.boss && s.boss.st !== 'dead') { var B = Sim.B; cx.strokeRect(s.boss.x - B.HW + 0.5, s.boss.y - B.HH + 0.5, B.HW * 2, B.HH * 2 + 4); }
    cx.strokeStyle = '#ffee44';
    for (i = 0; i < L.plats.length; i++) {
      var pts = L.plats[i].pts;
      cx.beginPath(); cx.moveTo(pts[0][0], pts[0][1] + 0.5);
      for (var j = 1; j < pts.length; j++) cx.lineTo(pts[j][0], pts[j][1] + 0.5);
      cx.stroke();
    }
    cx.beginPath();
    for (var x = Math.floor(s.cam); x < s.cam + W; x += 4) { var gy = Sim.groundY(L, Math.max(0, x)) + 0.5; if (x === Math.floor(s.cam)) cx.moveTo(x, gy); else cx.lineTo(x, gy); }
    cx.stroke();
    cx.strokeStyle = '#66aaff';
    for (i = 0; i < s.props.length; i++) { var o = s.props[i], ot = o.top + (o.openT > 0 ? 9 : 0); if (o.k === 'cover') cx.strokeRect(o.x0 + 0.5, ot + 0.5, o.x1 - o.x0, 180 - ot); }
  }

  // ------------------------------------------------------------------ the HUD, as on the look-and-feel canvas
  function tabW(label, min) { return Math.max(min, textW('s_lav', label) + 6); }
  function tab(x, y, w, label) {
    cx.fillStyle = '#10142c'; cx.fillRect(x, y, w, 9);
    cx.fillStyle = '#96a0dc'; cx.fillRect(x, y, w, 1); cx.fillRect(x, y, 1, 9);
    cx.fillStyle = '#3c4278'; cx.fillRect(x + w - 1, y, 1, 9); cx.fillRect(x, y + 8, w, 1);
    text('s_lav', label, x + Math.floor(w / 2) + 1, y + 2, 'c');
  }
  function clock(t) { t = Math.max(0, Math.floor(t)); var m = Math.floor(t / 60), s2 = t % 60; return m + ':' + (s2 < 10 ? '0' : '') + s2; }
  // on the road, what is coming is under the right thumb before it is anywhere else: say so at the edge of the clear picture
  function ahead(s) {
    var edge = s.cam + W * (1 - s.laneR), far = edge + 420, best = null, i, L = s.L;
    function see(x, label) { if (x > edge && x < far && (!best || x < best.x)) best = { x: x, label: label }; }
    for (i = 0; i < s.props.length; i++) if (!s.props[i].gone && s.props[i].k === 'rmine') see(s.props[i].x, 'MINE');
    for (i = 0; i < s.trucks.length; i++) if (s.trucks[i].st === 'ok' && s.trucks[i].mode !== 'run') see(s.trucks[i].x, s.trucks[i].mode === 'charge' ? 'TRUCK!' : 'TRUCK');
    for (i = s.roadI; i < L.road.length && L.road[i].x < far; i++) {
      if (L.road[i].k === 'rmine') see(L.road[i].x, 'MINE');
      else if (L.road[i].k === 'truck' && L.road[i].mode !== 'run') see(L.road[i].x, L.road[i].mode === 'charge' ? 'TRUCK!' : 'TRUCK');
    }
    return best;
  }
  // Yazeed's head for the lives row: the HUD portrait without its red card, cut to the head and its own outline
  var headCv = null;
  function lifeHead() {
    if (headCv) return headCv;
    var f = A && A.frames.hud_portrait; if (!f || !IMG.atlas) return null;
    try {
      var c = document.createElement('canvas'); c.width = f[2]; c.height = f[3];
      var g = c.getContext('2d'); g.drawImage(IMG.atlas, f[0], f[1], f[2], f[3], 0, 0, f[2], f[3]);
      var d = g.getImageData(0, 0, f[2], f[3]), px = d.data, x0 = 99, y0 = 99, x1 = -1, y1 = -1, x, y;
      for (y = 0; y < f[3]; y++) for (x = 0; x < f[2]; x++) {
        var k = (y * f[2] + x) * 4, r = px[k], gg = px[k + 1], b = px[k + 2];
        var card = x < 2 || y < 2 || x >= f[2] - 2 || y >= f[3] - 2 || (r === 184 && gg === 48 && b === 28) || (r === 90 && gg === 16 && b === 10);
        if (card) px[k + 3] = 0;
        else if (px[k + 3]) { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); }
      }
      g.putImageData(d, 0, 0);
      var h = document.createElement('canvas'); h.width = x1 - x0 + 1; h.height = y1 - y0 + 1;
      h.getContext('2d').drawImage(c, x0, y0, h.width, h.height, 0, 0, h.width, h.height);
      headCv = h;
    } catch (e) { headCv = null; return null; }
    return headCv;
  }
  function hud(s, ui) {
    var p = s.p, i, narrow = W < 430, mid = Math.floor(W / 2), paused = !!ui.paused;
    spr('hud_portrait', 5, 5);
    text('m_lav', T('YAZEED'), 30, 6);
    for (i = 0; i < 3; i++) spr(i < p.plates ? 'hud_plate_on' : 'hud_plate_off', 30 + i * 9, 17);
    var glint = refillT > 0 && ((refillT >> 2) & 1);        // a checkpoint refill: the plates and the heads glint gold for a second
    if (refillT > 0 && !paused) refillT--;
    if (glint) { cx.fillStyle = 'rgba(255,194,46,0.45)'; cx.fillRect(29, 16, 27, 9); }
    text('m_lav', ('0000000' + Math.min(9999999, s.score)).slice(-7), 60, 17);
    var fly = s.mode === 'fly', armsL = T(fly ? 'GUN' : 'ARMS'), bombL = T(fly ? 'ROCKETS' : 'BOMB');       // (the Apache: its chin gun and its rockets)
    var ax = narrow ? 108 : 118, aw = tabW(armsL, 28), bw2 = tabW(bombL, 28);
    var clockL = mid - Math.floor(textW('tall', '0:00') / 2);        // the two tabs stay clear of the clock
    if (ax + aw + 2 + bw2 + 2 > clockL) ax = Math.max(104, clockL - 2 - bw2 - 2 - aw);
    var bx0 = ax + aw + 2;
    tab(ax, 6, aw, armsL); tab(bx0, 6, bw2, bombL);
    if (p.weapon === 'hmg' && s.mode !== 'drive') text('m_org', String(p.ammo), ax + (aw >> 1), 17, 'c');
    else { text('m_org', 'o', ax + (aw >> 1) - 5, 17); text('m_org', 'o', ax + (aw >> 1), 17); }
    text('m_org', String(p.grenades), bx0 + (bw2 >> 1), 17, 'c');
    text('tall', clock(s.time), mid - Math.floor(textW('tall', clock(s.time)) / 2), 5);
    text('s_lav', T('PAR {0}', [clock(s.L.par)]), mid, 30, 'c');
    var fx0 = W - (narrow ? 164 : 168);
    if (!(s.L.fly && !s.stats.detainees)) {                       // (a flying mission with nobody to free has no count)
      tab(fx0, 6, tabW(T('FREED'), 30), T('FREED'));
      for (i = 0; i < Math.max(1, s.stats.detainees); i++) spr(i < s.stats.freed ? 'hud_pow_on' : 'hud_pow_off', fx0 + i * 8 - 1, 16);
    }
    var rx = W - (narrow ? 110 : 112);
    var rw = tabW(T('RADIO'), 34);
    if (RADIO_ON) { tab(rx, 6, rw, T('RADIO')); spr('hud_radio', rx + rw + 3, 5); }
    else {
      // lives, where the Radio was: one of Yazeed's heads for each; the one being lost blinks while he falls (Khaled, 19 Oct)
      var hd = lifeHead(), lv = Math.max(0, p.lives), hx = rx + 2, hy = 6;
      if (hd) {
        if (lv <= 4) {
          for (i = 0; i < lv; i++) {
            if (p.dead && i === lv - 1 && ((p.dead >> 3) % 2)) continue;
            cx.drawImage(hd, hx + i * (hd.width + 2), hy);
          }
        } else { cx.drawImage(hd, hx, hy); text('m_org', '=' + lv, hx + hd.width + 3, hy + 2); }
        if (glint && lv) { cx.fillStyle = 'rgba(255,194,46,0.45)'; cx.fillRect(hx - 1, hy - 1, Math.min(lv, 4) * (hd.width + 2) + 1, hd.height + 2); }
      }
    }
    for (i = 0; RADIO_ON && i < 3; i++) {
      var bx = rx + i * 16;
      cx.fillStyle = '#10101c'; cx.fillRect(bx, 17, 14, 7);
      cx.fillStyle = '#1e223c'; cx.fillRect(bx + 1, 18, 12, 5);
      if (s.radio > i) { cx.fillStyle = '#ffc22e'; cx.fillRect(bx + 1, 18, 12, 5); cx.fillStyle = '#fff8c8'; cx.fillRect(bx + 1, 18, 12, 2); }
    }
    // pause
    cx.fillStyle = 'rgba(16,20,44,0.78)'; cx.fillRect(W - 19, 6, 14, 14);
    cx.fillStyle = '#e8ecff'; cx.fillRect(W - 15, 9, 3, 8); cx.fillRect(W - 11, 9, 3, 8);
    if (ui.fps != null) text(ui.fps >= 57 ? 'm_lav' : 'm_org', ui.fps + ' FPS', W - 5, 23, 'r');
    // the trigger lock and AUTO: beside the tabs if there is room before the clock, else under the ARMS tab
    var mw = Math.max(ui.lock ? 8 : 0, ui.auto ? textW('s_org', T('AUTO')) : 0), mx = bx0 + bw2 + 2, my = 6;
    if (mw && mx + mw > clockL - 2) { mx = ax; my = Lang.isArabic(T('AUTO')) ? 29 : 26; }    // (Arabic letters rise higher)
    if (ui.lock) spr('hud_lock', mx, my);
    if (ui.auto) text('s_org', T('AUTO'), ui.lock && my !== 6 ? mx + 10 : mx, my + 2);

    // how much of the boat is left
    var b = s.boss;
    // (along the bottom, where it does not cover the boat)
    var barOn = !!(b && b.st !== 'dead' && b.st !== 'intro' && s.status === 'play');
    if (barOn) {
      var bw = 132, x0 = mid - bw / 2, full = b.full || Sim.B.HP, fill = Math.ceil((bw - 2) * b.hp / full), by = H - 9;
      cx.fillStyle = '#10142c'; cx.fillRect(x0, by, bw, 6);
      cx.fillStyle = '#96a0dc'; cx.fillRect(x0, by, bw, 1); cx.fillRect(x0, by, 1, 6);
      cx.fillStyle = '#3c4278'; cx.fillRect(x0 + bw - 1, by, 1, 6); cx.fillRect(x0, by + 5, bw, 1);
      cx.fillStyle = b.hurtT < 3 ? '#ffffff' : (b.phase === 3 ? '#ff5a3c' : '#ffc22e'); cx.fillRect(x0 + 1, by + 1, fill, 4);
      cx.fillStyle = b.hurtT < 3 ? '#ffffff' : (b.phase === 3 ? '#ffb09a' : '#fff8c8'); cx.fillRect(x0 + 1, by + 1, fill, 1);
      cx.fillStyle = '#10142c'; cx.fillRect(x0 + Math.round(bw / 3), by + 1, 1, 4); cx.fillRect(x0 + Math.round(bw * 2 / 3), by + 1, 1, 4);
      text('s_lav', T(b.label || 'BOSS'), x0 - 4, by, 'r');
    }
    if (b && bosses[b.kind] && bosses[b.kind].hud) bosses[b.kind].hud(s, b, K, paused);
    for (var hk in bosses) if (bosses[hk].hudAll) bosses[hk].hudAll(s, K, paused, { tabsX: ax, tabsEnd: bx0 + bw2, clockL: clockL });
    if (duckT > 0) { duckT -= paused ? 0 : 1; if (b && (b.st === 'swooptell' || b.st === 'swoop') && (duckT >> 2) % 2) text('b_org', T('GET DOWN!'), mid, 70, 'c'); }
    // on the road: what is about to come out from under the thumb
    if (s.mode === 'drive' && s.car && s.car.st === 'drive' && !p.dead) {
      var nxt = ahead(s);
      if (nxt && (tick >> 2) % 2) {
        var ex = Math.round(W * (1 - s.laneR)) - 6, ey = Math.round(Sim.groundY(s.L, clamp(nxt.x, 0, s.L.width - 1))) - 34;
        spr('hud_alert', ex - Math.floor(textW('m_org', T(nxt.label)) / 2), ey - 3);
        text('m_org', T(nxt.label), ex, ey + 2, 'r');
      }
    }

    if (goT > 0) { goT -= paused ? 0 : 1; if ((goT >> 3) % 2) spr('hud_go', W - 62, 54); }
    if (behindT > 0) { behindT -= paused ? 0 : 1; if ((behindT >> 2) % 2) { spr('hud_behind', 4, 108); text('s_org', T('BEHIND'), 13, 106); } }
    if (zoneT > 0) { zoneT -= paused ? 0 : 1; if (zoneT < 120 && !(b && b.st !== 'dead')) text('m_lav', zoneName, mid, 44, 'c'); }
    if (hint) { hint.t += paused ? 0 : 1; if (hint.t > hint.life) hint = null; else if (ui.caps !== false && (hint.t < hint.life - 50 || (hint.t >> 2) % 2)) text('m_org', hint.s, mid, 58, 'c'); }
    if (banner) {
      banner.t += paused ? 0 : 1;
      if (banner.t > banner.life) banner = null;
      else if (banner.t < banner.life - 24 || (banner.t >> 2) % 2) {
        text('b_red', banner.top, mid, 84, 'c');
        if (banner.bottom) text('b_org', banner.bottom, mid, 100, 'c');
      }
    }
    if (ui.sub && ui.caps !== false) {
      var who = ui.sub.who, line = ui.sub.text, rtl = Lang.rtl(), gap = textW('m_org', '  '), wWho = textW('m_org', who) + gap, fullw = wWho + textW('m_lav', line), maxw = W - (ui.overlay ? 190 : 16);
      function pair(l, y) {       // the speaker and a line of his, side by side: the name first in the reading direction
        var w = wWho + textW('m_lav', l), xa = mid - Math.floor(w / 2);
        if (rtl) { text('m_lav', l, xa, y); text('m_org', who, xa + w - wWho + gap, y); }
        else { text('m_org', who, xa, y); text('m_lav', l, xa + wWho, y); }
      }
      var sy = Lang.isArabic(line) ? (barOn ? 192 : 195) : 198;    // Arabic letters hang lower: the line sits higher, clear of the boss's bar
      if (fullw <= maxw) pair(line, sy);
      else {
        // two lines: break at the space nearest the middle
        var cut = line.lastIndexOf(' ', Math.floor(line.length / 2) + 3);
        if (cut < 0) cut = line.length;
        var lh = lineH('m_lav', line, 11);
        pair(line.slice(0, cut), sy + 1 - lh);
        text('m_lav', line.slice(cut + 1), mid, sy + 1, 'c');
      }
    }
  }

  K = {
    spr: spr, sprRot: sprRot, text: text, textW: textW, lineH: lineH, part: part, pop: pop, embers: embers, dotted: dotted, clamp: clamp,
    ctx: function () { return cx; }, tick: function () { return tick; }, W: function () { return W; }, H: H,
    shake: function (v) { shake = Math.max(shake, v); }, flash: function (v) { flashT = Math.max(flashT, v); },
    frame: function (n) { return A.frames[n]; }, rig: function (n) { return A.rig && A.rig[n]; },
    src: function (c) { SRC = c || null; }
  };
  return { init: init, resize: resize, reset: reset, draw: draw, onEvents: onEvents, setBanner: setBanner, setHint: setHint, text: text, textW: textW, lineH: lineH, arTune: arTune, arBitmap: arBitmap, spr: spr, opts: opts, bosses: bosses,
           width: function () { return W; }, height: function () { return H; }, zoom: function () { return zoom; },
           hudCanvas: function () { return zoom !== 1 ? hudCv : null; },
           clear: function (c) {
             cx.fillStyle = c; cx.fillRect(0, 0, W, H);
             if (zoom !== 1 && hudCx) { hudCx.globalCompositeOperation = 'source-atop'; hudCx.fillStyle = c; hudCx.fillRect(0, 0, HW, HH); hudCx.globalCompositeOperation = 'source-over'; }
           },
           ctx: function () { return cx; }, image: function (n) { return IMG[n]; } };
})();
