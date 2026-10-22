// render_fly.js - Taiz by Apache, drawn as the teaser has it (Khaled, 21 Oct: "refer to the teaser as it was good ... drop
// dusk"): a night sky with its moon and stars, clouds, Jabal Sabir behind the city covered in lights, the castle on its
// hill floodlit gold, the old town far off with its lit windows, and in front the painted stage (tools/export_taiz.py):
// the tower houses, the gate, the souq, the terraces, the bridge, the village, the castle walls. The Zanabeel and their
// guns, the Apache with its searchlight, and what flies.
// How the night works: the stage's sheet, the men's sprites and the Zanabeel's guns are painted in daylight colours; on
// the first frame of the mission each is copied once, graded for the night (its brightness kept, its colour gone over to
// the blue of the moon, a little of its own left), the windows of the lit rooms lit in the stage's copy and the castle
// floodlit gold. The night copies are what is drawn; what the searchlight finds is drawn from the daylight ones, as in the
// teaser. Nothing is laid over the whole picture.
// (Seen from further back than on foot: W and H here are the world's picture, half as big again; the HUD is drawn at its
// own size on its own canvas, render.js.)
(function () {
  'use strict';
  if (typeof Render === 'undefined') return;
  var FS = null, IMT = null, SH = null, cx = null, K = null, W = 468, H = 216, tick = 0;
  var trail = [], goUpT = 0, beatT = 99, beatSolid = false, flashes = [], rlockBeat = 99, recountT = 0, recountAdd = 0, captions = {};
  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }
  function lerp(a, b, f) { return a + (b - a) * f; }
  function mix(c0, c1, f) { return [lerp(c0[0], c1[0], f), lerp(c0[1], c1[1], f), lerp(c0[2], c1[2], f)]; }
  function rgb(c) { return 'rgb(' + Math.round(c[0]) + ',' + Math.round(c[1]) + ',' + Math.round(c[2]) + ')'; }
  function rgba(c, a) { return 'rgba(' + Math.round(c[0]) + ',' + Math.round(c[1]) + ',' + Math.round(c[2]) + ',' + a.toFixed(3) + ')'; }
  function hash(a, b) { var t = (a * 374761393 + b * 668265263) | 0; t = Math.imul(t ^ (t >>> 13), 1274126177); return ((t ^ (t >>> 16)) >>> 0) / 4294967296; }
  function on(s) { return !!(s && s.L && s.L.fly); }
  function sheet() {
    if (!FS) FS = (typeof ATLAS !== 'undefined' && ATLAS.taiz) || null;
    if (!IMT) IMT = Render.image('taiz');
    return !!(FS && IMT);
  }
  // a frame from the Apache's own sheet (the guns' and the launcher's too): [x, y, w, h, ax, ay]
  function tspr(name, x, y, flip, alpha) {
    var f = FS.frames[name], im = SH || IMT;
    if (!f) return;
    x = Math.round(x); y = Math.round(y);
    if (alpha != null && alpha < 1) cx.globalAlpha = alpha;
    if (flip) { cx.save(); cx.translate(x + 1, y); cx.scale(-1, 1); cx.drawImage(im, f[0], f[1], f[2], f[3], -f[4], -f[5], f[2], f[3]); cx.restore(); }
    else cx.drawImage(im, f[0], f[1], f[2], f[3], x - f[4], y - f[5], f[2], f[3]);
    if (alpha != null && alpha < 1) cx.globalAlpha = 1;
  }
  function tsprRot(name, x, y, ang, sxScale) {
    var f = FS.frames[name];
    if (!f) return;
    cx.save(); cx.translate(Math.round(x), Math.round(y)); if (sxScale) cx.scale(sxScale, 1); cx.rotate(ang);
    cx.drawImage(SH || IMT, f[0], f[1], f[2], f[3], -f[4], -f[5], f[2], f[3]);
    cx.restore();
  }
  function canvas(w, h) { var c = document.createElement('canvas'); c.width = Math.max(1, w); c.height = Math.max(1, h); return c; }

  // ------------------------------------------------------------------ the hour (night, as in the teaser; dawn comes at the end)
  function hour(s) { var d = s.dark != null ? s.dark : Sim.ext.fly.dark(s.L, s.u); return { d: d, dawn: false }; }
  function night(s) { return hour(s).d >= 0.5; }

  // ------------------------------------------------------------------ the night copies
  // brightness to the night's blue: a little lifted in the middle (so a man in the dark still reads), the darkest parts
  // the colour of the sky at the top of the picture
  var LUT = null, KEEP = 0.16;
  function lut() {
    if (LUT) return LUT;
    LUT = { r: new Float32Array(256), g: new Float32Array(256), b: new Float32Array(256) };
    for (var l = 0; l < 256; l++) {
      var v = Math.pow(l / 255, 0.86) * 255;
      LUT.r[l] = v * 0.31 + 7; LUT.g[l] = v * 0.39 + 11; LUT.b[l] = v * 0.62 + 24;
    }
    return LUT;
  }
  function dawnRGB(c) { var d = [c[0], c[1], c[2], 255]; dawnPix(d, 0); return [d[0], d[1], d[2]]; }
  function nightRGB(c) { var T = lut(), l = (c[0] * 77 + c[1] * 150 + c[2] * 29) >> 8; return [T.r[l] + (c[0] - l) * KEEP, T.g[l] + (c[1] - l) * KEEP, T.b[l] + (c[2] - l) * KEEP]; }
  // a picture's night copy (extra: what else changes, given the graded pixels and the daylight ones)
  function graded(img, extra) {
    var w = img.width, h = img.height, c = canvas(w, h), g = c.getContext('2d');
    g.drawImage(img, 0, 0);
    var id = g.getImageData(0, 0, w, h), d = id.data, o = extra ? new Uint8ClampedArray(d) : null, T = lut();
    for (var i = 0; i < d.length; i += 4) {
      if (!d[i + 3]) continue;
      var r = d[i], gg = d[i + 1], b = d[i + 2], l = (r * 77 + gg * 150 + b * 29) >> 8;
      d[i] = T.r[l] + (r - l) * KEEP; d[i + 1] = T.g[l] + (gg - l) * KEEP; d[i + 2] = T.b[l] + (b - l) * KEEP;
    }
    if (extra) extra(d, o, w, h);
    g.putImageData(id, 0, 0);
    return c;
  }
  // the stage's night: the castle floodlit gold from below, and the rooms that are lit
  function stageNight(S, hz) {
    return function (d, o, w) {
      var P = S.pieces, k, places = {};
      S.place.forEach(function (q) { if (!places[q.p]) places[q.p] = q; });
      for (k in P) if (/^c_/.test(k)) flood(d, o, w, P[k], 1);
      S.windows.forEach(function (q) {
        var pl = places[q.house], pr = P[q.house];
        if (!pl || !pr) return;
        var odds = q.house === 'souq_back' ? 0.5 : (q.house.charAt(0) === 'c' ? 0.8 : 0.58);
        if (hash(q.x * 3 + 1, q.y * 7 + 2) >= odds) return;
        var ox = pr[0] - pl.x, oy = pr[1] - pl.y;
        lit(d, o, w, q.x + ox, q.y + oy, q.w, q.h, q.fan ? [q.fan[0] + ox, q.fan[1] + oy, q.fan[2], q.fan[3]] : null, hash(q.x, q.y + 5));
      });
      // the street lamps' heads
      if (P.lamp) { var lp = P.lamp; for (var y = 3; y < 9; y++) for (var x = 3; x < 11; x++) { var i = ((lp[1] + y) * w + lp[0] + x) * 4; if (o[i + 3] && (o[i] + o[i + 1] + o[i + 2]) > 240) { d[i] = 255; d[i + 1] = 236; d[i + 2] = 180; } } }
      // what can be flown into stands out from what cannot (Khaled, 21 Oct 15:01: "buildings and backgrounds blend together,
      // making me collide with buildings thinking they are in the background"): the moon catches the top edges of anything
      // solid, and its right-hand side, its left in shadow; the souq's back houses, the street's shopfronts and the water
      // tower, which are only scenery, are laid back in the night's haze
      var seen = {};
      S.place.forEach(function (q) {
        var r = P[q.p];
        if (!r || seen[q.p]) return;
        seen[q.p] = 1;
        if (hz[q.p] != null) haze(d, o, w, r, hz[q.p]);
        else if (q.layer === 'mid') rimPiece(d, o, w, r);
      });
    };
  }
  var SCENERY = { souq_back: 0.62, shops: 0.32, wtower: 0.45 };        // (how far back each is laid)
  // ...and the houses the level makes scenery (painted solid, but no stone: L.fly.scenery), as far back as the souq's
  function sceneryOf(sc) {
    var hz = {}, k;
    for (k in SCENERY) hz[k] = SCENERY[k];
    (sc || []).forEach(function (n) { if (hz[n] == null) hz[n] = 0.55; });
    return hz;
  }
  // the stage as the searchlight shows it: its own colours, but what is only scenery still laid back a little (paler,
  // bluer), so that in the light too what can be flown into stands out from what cannot (Khaled, 21 Oct: it was in the
  // light that the tall house on the souq's far side looked like the ones behind it)
  function dayCopy(img, S, hz) {
    var w = img.width, h = img.height, c = canvas(w, h), g = c.getContext('2d');
    g.drawImage(img, 0, 0);
    var id = g.getImageData(0, 0, w, h), d = id.data, P = S.pieces, seen = {};
    S.place.forEach(function (q) {
      var r = P[q.p];
      if (!r || seen[q.p] || hz[q.p] == null) return;
      seen[q.p] = 1;
      var a = hz[q.p] * 0.6;
      for (var y = 0; y < r[3]; y++) for (var x = 0; x < r[2]; x++) {
        var i = ((r[1] + y) * w + r[0] + x) * 4;
        if (!d[i + 3]) continue;
        d[i] += (92 - d[i]) * a; d[i + 1] += (104 - d[i + 1]) * a; d[i + 2] += (138 - d[i + 2]) * a;
      }
    });
    g.putImageData(id, 0, 0);
    return c;
  }
  function haze(d, o, w, r, a) {
    for (var y = 0; y < r[3]; y++) for (var x = 0; x < r[2]; x++) {
      var i = ((r[1] + y) * w + r[0] + x) * 4;
      if (!o[i + 3]) continue;
      d[i] += (24 - d[i]) * a; d[i + 1] += (32 - d[i + 1]) * a; d[i + 2] += (62 - d[i + 2]) * a;
    }
  }
  function rimPiece(d, o, w, r) {
    var x0 = r[0], y0 = r[1], ww = r[2], hh = r[3];
    function solid(x, y) { return x >= 0 && y >= 0 && x < ww && y < hh && o[((y0 + y) * w + x0 + x) * 4 + 3] >= 128; }
    for (var y = 0; y < hh; y++) for (var x = 0; x < ww; x++) {
      if (!solid(x, y)) continue;
      var i = ((y0 + y) * w + x0 + x) * 4;
      if (!solid(x, y - 1)) { d[i] = d[i] * 0.45 + 96; d[i + 1] = d[i + 1] * 0.45 + 110; d[i + 2] = d[i + 2] * 0.45 + 158; }
      else if (!solid(x, y - 2) || !solid(x + 1, y)) { d[i] = d[i] * 0.75 + 24; d[i + 1] = d[i + 1] * 0.75 + 28; d[i + 2] = d[i + 2] * 0.75 + 44; }
      else if (!solid(x - 1, y)) { d[i] *= 0.6; d[i + 1] *= 0.6; d[i + 2] *= 0.64; }
    }
  }
  // floodlights on the stone: its brightness in the floodlights' gold, strongest low down and fading up the wall (the
  // tops of the towers in the night's blue), as the teaser has the castle
  function flood(d, o, w, r, str) {
    for (var y = 0; y < r[3]; y++) {
      var u = y / r[3], f = (0.38 + 0.5 * Math.min(1, u * 1.4)) * str, yy = (r[1] + y) * w;
      for (var x = 0; x < r[2]; x++) {
        var i = (yy + r[0] + x) * 4;
        if (!o[i + 3]) continue;
        var l = (o[i] * 77 + o[i + 1] * 150 + o[i + 2] * 29) >> 8, R = Math.min(255, l * 1.08 + 26), G = l * 0.8 + 12, B = l * 0.42 + 6;
        d[i] += (R - d[i]) * f; d[i + 1] += (G - d[i + 1]) * f; d[i + 2] += (B - d[i + 2]) * f;
      }
    }
  }
  // the Apache by night: black, its top edges caught by the moon (so it reads against the dark of the mountain)
  function rimmed(img) {
    var w = img.width, h = img.height, c = canvas(w, h), g = c.getContext('2d');
    g.drawImage(img, 0, 0);
    var id = g.getImageData(0, 0, w, h), d = id.data, o = new Uint8ClampedArray(d);
    for (var y = 1; y < h; y++) for (var x = 0; x < w; x++) {
      var i = (y * w + x) * 4;
      if (o[i + 3] < 128) continue;
      var up = o[i - w * 4 + 3] < 128, up2 = y > 1 && o[i - w * 8 + 3] < 128;
      if (up) { d[i] = d[i] * 0.3 + 104; d[i + 1] = d[i + 1] * 0.3 + 118; d[i + 2] = d[i + 2] * 0.3 + 160; }
      else if (up2) { d[i] = d[i] * 0.6 + 40; d[i + 1] = d[i + 1] * 0.6 + 46; d[i + 2] = d[i + 2] * 0.6 + 66; }
    }
    g.putImageData(id, 0, 0);
    return c;
  }
  // a lit room: its glass warm (brighter at the top), the coloured glass of the fanlight over it glowing
  function lit(d, o, w, x0, y0, ww, hh, fan, v) {
    var x, y, i, warm = 0.8 + 0.2 * v;
    for (y = 0; y < hh; y++) for (x = 0; x < ww; x++) {
      i = ((y0 + y) * w + x0 + x) * 4;
      if (!o[i + 3]) continue;
      var l = (o[i] * 77 + o[i + 1] * 150 + o[i + 2] * 29) >> 8;
      if (l > 120) continue;                                        // (the frame stays as it is)
      var t = 1 - y / hh;
      d[i] = 255; d[i + 1] = (150 + 70 * t) * warm + 20; d[i + 2] = (64 + 70 * t) * warm;
      if (l < 30 && (x === (ww >> 1))) { d[i] = 150; d[i + 1] = 90; d[i + 2] = 40; }     // (its bar, against the light)
    }
    if (fan) for (y = 0; y < fan[3]; y++) for (x = 0; x < fan[2]; x++) {
      i = ((fan[1] + y) * w + fan[0] + x) * 4;
      if (!o[i + 3]) continue;
      var r = o[i], g = o[i + 1], b = o[i + 2], mx = Math.max(r, g, b), mn = Math.min(r, g, b);
      if (mx - mn < 30) continue;
      var k = 255 / Math.max(1, mx);
      d[i] = Math.min(255, r * k * 0.8 + 50); d[i + 1] = Math.min(255, g * k * 0.8 + 40); d[i + 2] = Math.min(255, b * k * 0.8 + 30);
    }
  }
  // dawn, at the end: everything warm and low-lit, the windows out, the castle's floodlights off
  function gradedFn(img, fn) {
    var w = img.width, h = img.height, c = canvas(w, h), g = c.getContext('2d');
    g.drawImage(img, 0, 0);
    var id = g.getImageData(0, 0, w, h), d = id.data;
    for (var i = 0; i < d.length; i += 4) if (d[i + 3]) fn(d, i);
    g.putImageData(id, 0, 0);
    return c;
  }
  function dawnPix(d, i) {
    var r = d[i], g = d[i + 1], b = d[i + 2], l = (r * 77 + g * 150 + b * 29) >> 8;
    d[i] = (l + (r - l) * 0.8) * 0.95 + 16; d[i + 1] = (l + (g - l) * 0.8) * 0.78 + 8; d[i + 2] = (l + (b - l) * 0.8) * 0.72 + 22;
  }
  function dawnCopies() {
    if (!NG) return null;
    if (!NG.dawn) NG.dawn = { stage: gradedFn(NG.day, dawnPix), atlas: gradedFn(Render.image('atlas'), dawnPix), earth: gradedFn(NG.earthDay, dawnPix), pats: [] };
    return NG.dawn;
  }
  var NG = null;                    // { stage, atlas, taiz, earth, earthDay } once made
  function nightCopies(S, sc) {
    if (NG && NG.S === S) return NG;
    var st = Render.image('taiz_stage'), at = Render.image('atlas');
    if (!st || !at || !sheet()) return null;
    var ed = earthPic(), hz = sceneryOf(sc);
    NG = { S: S, day: dayCopy(st, S, hz), stage: graded(st, stageNight(S, hz)), atlas: graded(at), taiz: graded(IMT), heli: rimmed(IMT), earthDay: ed, earth: graded(ed), pats: [] };
    return NG;
  }
  // the earth and rock under everything (a tile)
  function earthPic() {
    var c = canvas(64, 64), g = c.getContext('2d'), i;
    g.fillStyle = 'rgb(100,84,64)'; g.fillRect(0, 0, 64, 64);
    for (i = 0; i < 520; i++) {
      var x = Math.floor(hash(i, 61) * 64), y = Math.floor(hash(i, 62) * 64), d = hash(i, 63);
      g.fillStyle = d < 0.55 ? 'rgba(36,28,20,0.5)' : 'rgba(196,174,134,0.45)';
      g.fillRect(x, y, 1 + Math.floor(hash(i, 64) * 4), 1 + Math.floor(hash(i, 65) * 2));
    }
    for (i = 0; i < 7; i++) { g.fillStyle = 'rgba(36,26,18,0.45)'; g.fillRect(0, 4 + i * 9 + (i % 3), 64, 1); g.fillStyle = 'rgba(200,180,140,0.25)'; g.fillRect(0, 5 + i * 9 + (i % 3), 64, 1); }
    return c;
  }
  // (a pattern belongs with the canvas it is drawn on)
  function pat(g, day) {
    for (var i = 0; i < NG.pats.length; i++) if (NG.pats[i].g === g && NG.pats[i].day === day) return NG.pats[i].p;
    var p = g.createPattern(day === 'dawn' ? NG.dawn.earth : (day ? NG.earthDay : NG.earth), 'repeat');
    NG.pats.push({ g: g, day: day, p: p });
    return p;
  }
  // which sprites a thing is drawn from: the night copy, unless it is in the searchlight (render.js asks, for each man,
  // Yazeed, the pickups, smoke)
  function tint(s, e) {
    if (!on(s) || !NG || !night(s)) return null;
    if (e && lampA(s) > 0.5 && Sim.ext.fly.inBeam(s, e.x, e.y - (e.h || 30) * 0.5)) return null;
    if ((s.dawn || 0) >= 0.5 && NG.dawn) return NG.dawn.atlas;
    return NG.atlas;
  }
  function lampOn(s) { var h = s.heli; return !!(h && !s.p.dead && h.st !== 'off' && h.st !== 'wreck' && h.st !== 'down'); }
  // how much of it shows: all of it by night; as dawn comes up the pilot turns it down, and it is off before the sun is
  function lampA(s) { if (!lampOn(s)) return 0; var dw = s.dawn || 0; return dw <= 0.15 ? 1 : Math.max(0, 1 - (dw - 0.15) / 0.45); }
  // a hit shows as a white flash; under a stream of rounds (the chin gun puts in twenty a second) it flashes now and then
  // rather than staying white, so a pickup or a gun under fire still shows its colours
  var FLASH = {};
  function flash(e) {
    if (!(e.hurtT < 3)) return false;
    var t0 = FLASH[e.id];
    if (t0 == null || tick - t0 > 9 || tick < t0) FLASH[e.id] = t0 = tick;
    return tick - t0 < 3;
  }

  // ------------------------------------------------------------------ far away, as in the teaser
  // (the far layers are placed from the camera at the start of the lower town: Y0; they go down the picture a little as
  // the Apache climbs, the nearer ones more)
  var Y0 = 898, X0 = 649, FAR = null;
  function far() {
    if (FAR && FAR.W === W && FAR.H === H) return FAR;
    FAR = { W: W, H: H, sky: skyPic(W, H), dsky: null, mount: FAR ? FAR.mount : mountPic(), dmount: FAR ? FAR.dmount : null, dtown: FAR ? FAR.dtown : null, dclouds: FAR ? FAR.dclouds : null,
            town: FAR ? FAR.town : townPic(), clouds: FAR ? FAR.clouds : [cloudPic(1, 170, 40), cloudPic(2, 130, 32), cloudPic(3, 210, 46)] };
    return FAR;
  }
  function skyPic(w, h) {
    var c = canvas(w, h), g = c.getContext('2d'), gr = g.createLinearGradient(0, 0, 0, h), i;
    gr.addColorStop(0, '#090d1d'); gr.addColorStop(0.45, '#111933'); gr.addColorStop(0.8, '#1e2a52'); gr.addColorStop(1, '#283766');
    g.fillStyle = gr; g.fillRect(0, 0, w, h);
    for (i = 0; i < w * h / 520; i++) {
      var x = Math.floor(hash(i, 11) * w), y = Math.floor(Math.pow(hash(i, 12), 1.4) * h * 0.85), b = hash(i, 13);
      g.fillStyle = b < 0.82 ? 'rgba(196,208,255,' + (0.18 + b * 0.5).toFixed(2) + ')' : 'rgba(255,238,206,0.75)';
      g.fillRect(x, y, 1, 1);
    }
    // the moon: a thin crescent, high on the right, with a little light about it
    var mx = w - 66, my = 30, R = 10;
    var mg = g.createRadialGradient(mx, my, 4, mx, my, 34);
    mg.addColorStop(0, 'rgba(240,236,200,0.16)'); mg.addColorStop(1, 'rgba(240,236,200,0)');
    g.fillStyle = mg; g.fillRect(mx - 34, my - 34, 68, 68);
    for (var dy = -R; dy <= R; dy++) for (var dx = -R; dx <= R; dx++) {
      var inA = dx * dx + dy * dy <= R * R, inB = (dx - 5) * (dx - 5) + (dy + 3) * (dy + 3) <= (R - 1) * (R - 1);
      if (!inA || inB) continue;
      var edge = (dx - 5) * (dx - 5) + (dy + 3) * (dy + 3) <= (R + 0.6) * (R + 0.6);
      g.fillStyle = edge ? '#d8cfa4' : '#f6eec8'; g.fillRect(mx + dx, my + dy, 1, 1);
    }
    return c;
  }
  // a cloud: puffs together, lit along the top by the moon, darker underneath (dithered, in the teaser's blues)
  function cloudPic(seed, w, h, dawn) {
    var c = canvas(w, h), g = c.getContext('2d'), id = g.createImageData(w, h), d = id.data, P = [], i, x, y;
    // (many small puffs along a flat bottom, higher in the middle: never one round one, which would read as a moon)
    for (i = 0; i < 11; i++) { var u = (i + 0.5) / 11, r = h * (0.2 + 0.16 * hash(seed, i + 30)) * (0.75 + 0.5 * Math.sin(u * Math.PI)); P.push([w * (0.08 + 0.84 * u) + (hash(seed, i + 10) - 0.5) * 8, h - r - 4 - h * 0.3 * Math.sin(u * Math.PI) * hash(seed, i + 20), r]); }
    function inside(px, py) { for (var k = 0; k < P.length; k++) { var dx = px - P[k][0], dy = py - P[k][1]; if (dx * dx + dy * dy <= P[k][2] * P[k][2]) return true; } return py > h - 6 && py < h - 1 && px > w * 0.14 && px < w * 0.86; }
    for (y = 0; y < h; y++) for (x = 0; x < w; x++) {
      if (!inside(x, y)) continue;
      var top = !inside(x, y - 2) || !inside(x, y - 1), low = y > h * 0.72, dz = (x + y) % 2;
      var col = top ? [74, 90, 142] : (low ? (dz ? [30, 38, 74] : [36, 46, 86]) : (dz && y < h * 0.5 ? [54, 68, 116] : [44, 56, 102]));
      if (dawn) col = top ? [255, 204, 170] : (low ? (dz ? [138, 96, 124] : [150, 106, 132]) : (dz && y < h * 0.5 ? [214, 150, 152] : [190, 132, 144]));
      i = (y * w + x) * 4; d[i] = col[0]; d[i + 1] = col[1]; d[i + 2] = col[2]; d[i + 3] = 255;
    }
    g.putImageData(id, 0, 0);
    return c;
  }
  // Jabal Sabir: a great dark mountain over the city, rough along its top, the villages on its slopes lit (in clusters,
  // thicker towards its foot, none near the top), as the teaser has it
  function mountPic(dawn) {
    var w = 660, h = 200, c = canvas(w, h), g = c.getContext('2d'), id = g.createImageData(w, h), d = id.data, top = [], x, y, i, k;
    for (x = 0; x < w; x++) {
      var u = x / w, b = 168 * Math.exp(-Math.pow((u - 0.54) / 0.2, 2)) + 66 * Math.exp(-Math.pow((u - 0.2) / 0.13, 2)) + 50 * Math.exp(-Math.pow((u - 0.86) / 0.1, 2)) + 18;
      top[x] = Math.round(h - Math.min(h - 6, b) - 3 * Math.sin(x / 9) - 2 * Math.sin(x / 3.7 + 1) - 2 * hash(x >> 1, 7));
    }
    for (y = 0; y < h; y++) for (x = 0; x < w; x++) {
      if (y < top[x]) continue;
      i = (y * w + x) * 4;
      var sp = hash(x * 7 + 3, y * 13 + 1), edge = y - top[x] < 2;
      var col = edge ? [36, 44, 80] : (sp < 0.07 ? [28, 34, 62] : [17, 21, 42]);
      if (dawn) col = edge ? [170, 126, 140] : (sp < 0.07 ? [96, 78, 112] : [78, 64, 98]);
      d[i] = col[0]; d[i + 1] = col[1]; d[i + 2] = col[2]; d[i + 3] = 255;
    }
    if (dawn) { g.putImageData(id, 0, 0); return c; }
    function light(x, y, k) {
      if (x < 0 || x >= w || y >= h || y < top[x] + 10) return;
      var warm = hash(k, 93) < 0.85, br = 0.5 + 0.5 * hash(k, 94), j = (y * w + x) * 4;
      d[j] = warm ? 255 * br : 196 * br; d[j + 1] = warm ? 194 * br : 212 * br; d[j + 2] = warm ? 104 * br : 255 * br;
    }
    // the villages: clusters of lights
    for (k = 0; k < 70; k++) {
      var vx = Math.floor(hash(k, 81) * w), dep = Math.pow(hash(k, 82), 0.55), vy = Math.floor(top[vx] + 14 + dep * (h - top[vx] - 14)), n = 6 + Math.floor(hash(k, 83) * 22 * (0.4 + dep));
      for (i = 0; i < n; i++) light(vx + Math.floor((hash(k * 31 + i, 84) - 0.5) * 22), vy + Math.floor((hash(k * 31 + i, 85) - 0.5) * 9), k * 31 + i);
    }
    // and the town along its foot, thick
    for (i = 0; i < 700; i++) { x = Math.floor(hash(i, 86) * w); light(x, h - 1 - Math.floor(Math.pow(hash(i, 87), 1.8) * 34), i + 9000); }
    g.putImageData(id, 0, 0);
    return c;
  }
  // the old town far off: tower houses in silhouette, crenellated, a window lit here and there (it repeats along)
  function townPic(dawn) {
    var w = 1600, h = 120, c = canvas(w, h), g = c.getContext('2d'), x = 0, i = 0;
    while (x < w) {
      var bw = 14 + Math.floor(hash(i, 1) * 22), bh = 22 + Math.floor(hash(i, 2) * 58) + (hash(i, 3) < 0.15 ? 30 : 0);
      if (x + bw > w) bw = w - x;
      var col = dawn ? (hash(i, 4) < 0.5 ? [92, 76, 104] : [104, 86, 112]) : (hash(i, 4) < 0.5 ? [20, 25, 49] : [23, 29, 55]);
      g.fillStyle = rgb(col); g.fillRect(x, h - bh, bw, bh);
      g.fillStyle = rgb(mix(col, [70, 84, 130], 0.18)); g.fillRect(x, h - bh, bw, 1);
      for (var m = x + 1; m < x + bw - 1; m += 3) g.fillRect(m, h - bh - 2, 1, 2);
      for (var wy = h - bh + 5; wy < h - 4; wy += 7) for (var wx = x + 3; wx < x + bw - 3; wx += 5) {
        var q = hash(wx, wy);
        if (q < (dawn ? 0.03 : 0.12)) { g.fillStyle = q < 0.04 ? 'rgb(200,176,124)' : 'rgb(168,122,70)'; g.fillRect(wx, wy, q < 0.04 ? 2 : 1, q < 0.04 ? 2 : 1); }
      }
      x += bw + (hash(i, 5) < 0.3 ? Math.floor(hash(i, 6) * 6) : 0);
      i++;
    }
    return c;
  }
  // (the world's picture is s.viewW x s.viewH: the canvas's size, except while the opening draws back to it)
  function view(s) { W = s.viewW || K.W(); H = s.viewH || K.H; }
  function dskyPic(w, h) {
    var c = canvas(w, h), g = c.getContext('2d'), gr = g.createLinearGradient(0, 0, 0, h);
    gr.addColorStop(0, '#2c3566'); gr.addColorStop(0.45, '#7a6c9c'); gr.addColorStop(0.78, '#e2967f'); gr.addColorStop(1, '#ffcb9c');
    g.fillStyle = gr; g.fillRect(0, 0, w, h);
    var sg = g.createRadialGradient(w * 0.82, h * 0.92, 4, w * 0.82, h * 0.92, h * 0.7);
    sg.addColorStop(0, 'rgba(255,236,190,0.75)'); sg.addColorStop(0.3, 'rgba(255,190,140,0.3)'); sg.addColorStop(1, 'rgba(255,190,140,0)');
    g.fillStyle = sg; g.fillRect(0, 0, w, h);
    return c;
  }
  function back(s, paused, k) {
    K = k; cx = K.ctx(); tick = K.tick(); view(s);
    if (!on(s)) return;
    nightCopies(s.L.fly.stage, s.L.fly.scenery);
    var FW = s.fullW || W, FH = s.fullH || H;
    if (Math.abs(FW - W) > 1 || Math.abs(FH - H) > 1) {
      // (the opening, on foot, and the picture drawing back from it: the far things are laid out for the flight's whole
      // picture and shown at the size they will have in it, so the sky, the mountain and the far town are the same before
      // the Apache lifts off as after. Khaled, 21 Oct 15:01: "the intro background isn't the same as the game")
      if (!farCv || farCv.width !== FW || farCv.height !== FH) farCv = canvas(FW, FH);
      var real = cx, rw = W, rh = H;
      cx = farCv.getContext('2d'); W = FW; H = FH;
      farLayers(s, s.cam + (rw - FW) / 2, s.camY + (rh - FH) / 2);          // (as if the whole picture were about the same middle)
      cx = real; W = rw; H = rh;
      cx.save(); cx.imageSmoothingEnabled = true; cx.drawImage(farCv, 0, 0, FW, FH, 0, 0, W, H); cx.restore();
      return;
    }
    farLayers(s, s.cam, s.camY);
  }
  var farCv = null;
  function farLayers(s, cam, camY) {
    var Fq = far(), rise = Y0 - camY, i, dw = s.dawn || 0;
    if (dw > 0) {
      dawnCopies();
      if (!Fq.dsky) Fq.dsky = dskyPic(W, H);
      if (!Fq.dmount) { Fq.dmount = mountPic(true); Fq.dtown = townPic(true); Fq.dclouds = [cloudPic(1, 170, 40, true), cloudPic(2, 130, 32, true), cloudPic(3, 210, 46, true)]; }
    }
    cx.drawImage(Fq.sky, 0, 0);
    if (dw > 0) { cx.globalAlpha = dw; cx.drawImage(Fq.dsky, 0, 0); cx.globalAlpha = 1; }
    // a few stars twinkle
    for (i = 0; i < 24 && dw < 0.8; i++) {
      var sx = Math.floor(hash(i, 71) * W), sy = Math.floor(hash(i, 72) * H * 0.6), tw = 0.5 + 0.5 * Math.sin(tick * 0.06 + i * 2.1);
      cx.fillStyle = rgba([226, 232, 255], 0.9 * tw * (1 - dw)); cx.fillRect(sx, sy, 1, 1);
    }
    // the clouds, drifting
    var CL = Fq.clouds;
    for (i = 0; i < 5; i++) {
      var cp = CL[i % CL.length], span = W + 400, cxx = ((hash(i, 81) * span - cam * 0.025 - tick * 0.02 * (1 + i % 2)) % span + span) % span - 200;
      cx.drawImage(cp, Math.round(cxx), Math.round(70 + hash(i, 82) * 70 + rise * 0.03));
      if (dw > 0) { cx.globalAlpha = dw; cx.drawImage(Fq.dclouds[i % Fq.dclouds.length], Math.round(cxx), Math.round(70 + hash(i, 82) * 70 + rise * 0.03)); cx.globalAlpha = 1; }
    }
    // Jabal Sabir
    cx.drawImage(Fq.mount, Math.round(W * 0.66 - 356 - (cam - X0) * 0.03), Math.round(H - 40 - Fq.mount.height + rise * 0.04));
    if (dw > 0) { cx.globalAlpha = dw; cx.drawImage(Fq.dmount, Math.round(W * 0.66 - 356 - (cam - X0) * 0.03), Math.round(H - 40 - Fq.mount.height + rise * 0.04)); cx.globalAlpha = 1; }
    // the old town
    var tw2 = Fq.town.width, tx = -(((cam * 0.3) % tw2) + tw2) % tw2, ty = Math.round(H - 74 - Fq.town.height + 40 + rise * 0.3);
    if (ty < H) for (var xx = tx; xx < W; xx += tw2) { cx.drawImage(Fq.town, Math.round(xx), ty); if (dw > 0) { cx.globalAlpha = dw; cx.drawImage(Fq.dtown, Math.round(xx), ty); cx.globalAlpha = 1; } }
    // (a little haze over the far town, so the stage stands out from it)
    var hz = cx.createLinearGradient(0, ty + 40, 0, ty + Fq.town.height + 20);
    hz.addColorStop(0, 'rgba(30,40,80,0.1)'); hz.addColorStop(1, 'rgba(30,40,80,0.55)');
    cx.fillStyle = hz; cx.fillRect(0, ty + 40, W, Fq.town.height + 60);
  }

  // ------------------------------------------------------------------ near: the painted stage
  var PL = null;
  function placements(S) {
    if (PL && PL.S === S) return PL;
    var order = { back: 0, mid: 1, decor: 2 };
    PL = S.place.map(function (q) { var r = S.pieces[q.p]; return { r: r, x: q.x, y: q.y, x1: q.x + r[2], y1: q.y + r[3], o: order[q.layer] != null ? order[q.layer] : 1, p: q.p }; });
    PL.sort(function (a, b) { return a.o - b.o; });
    PL.S = S;
    return PL;
  }
  function pieces(g, img, S, x0, y0, x1, y1) {
    var P = placements(S);
    for (var i = 0; i < P.length; i++) {
      var q = P[i], r = q.r;
      if (q.x1 < x0 || q.x > x1 || q.y1 < y0 || q.y > y1) continue;
      g.drawImage(img, r[0], r[1], r[2], r[3], q.x, q.y, r[2], r[3]);
    }
  }
  var ROADC = [70, 70, 76], CURB = [150, 146, 138], PAVE = [92, 86, 80];
  function ground(g, s, x0, x1, y1, day) {
    var L = s.L, S = L.fly.stage, x;
    g.fillStyle = pat(g, day);
    g.beginPath(); g.moveTo(x0, y1);
    for (x = x0; x <= x1; x += 2) g.lineTo(x, Sim.groundY(L, clamp(x, 0, L.width)));
    g.lineTo(x1, y1); g.closePath(); g.fill();
    // the street (paved), the road (tarmac, its edge), the courtyard
    var pv = day ? PAVE : nightRGB(PAVE), rd = day ? ROADC : nightRGB(ROADC), cb = day ? CURB : nightRGB(CURB);
    if (day === 'dawn') { pv = dawnRGB(PAVE); rd = dawnRGB(ROADC); cb = dawnRGB(CURB); }
    var st0 = Math.max(x0, 0), st1 = Math.min(x1, S.world.SOUQ[1]);
    if (st1 > st0) {
      var sy = S.world.STREET;
      g.fillStyle = rgb(pv); g.fillRect(st0, sy, st1 - st0, 5);
      g.fillStyle = rgb(mix(pv, [0, 0, 0], 0.35)); for (x = Math.floor(st0 / 9) * 9; x < st1; x += 9) g.fillRect(x, sy + 1, 1, 4);
      g.fillStyle = rgb(mix(pv, [255, 255, 255], 0.18)); g.fillRect(st0, sy, st1 - st0, 1);
    }
    var R = S.road;
    if (R && R.length > 1 && x1 > R[0][0] && x0 < R[R.length - 1][0]) {
      g.strokeStyle = rgb(rd); g.lineWidth = 5;
      g.beginPath(); g.moveTo(R[0][0], R[0][1] + 2.5); for (var i = 1; i < R.length; i++) g.lineTo(R[i][0], R[i][1] + 2.5); g.stroke();
      g.strokeStyle = rgb(cb); g.lineWidth = 1;
      g.beginPath(); g.moveTo(R[0][0], R[0][1] + 0.5); for (i = 1; i < R.length; i++) g.lineTo(R[i][0], R[i][1] + 0.5); g.stroke();
    }
    var C = S.world.COURTYARD;
    if (C && x1 > C[0] && x0 < C[1]) { g.fillStyle = rgb(pv); g.fillRect(C[0], S.world.TOP, C[1] - C[0], 4); g.fillStyle = rgb(mix(pv, [255, 255, 255], 0.18)); g.fillRect(C[0], S.world.TOP, C[1] - C[0], 1); }
  }
  // the hillside road's side (drawn here, plainly): the terraced fields stepping down the hill under it, a low stone wall
  // along its edge, the poles carrying the wires up it, its lamps, bushes
  var TWALL = [132, 120, 102], TCROP = [64, 86, 46], POLE = [96, 76, 56], WIRE = [70, 70, 80], BUSH = [52, 74, 40], GUARD = [150, 140, 122];
  function roadY(R, x) {
    for (var i = 1; i < R.length; i++) if (x <= R[i][0]) { var f = (x - R[i - 1][0]) / (R[i][0] - R[i - 1][0] || 1); return R[i - 1][1] + (R[i][1] - R[i - 1][1]) * f; }
    return R[R.length - 1][1];
  }
  function onBridge(S, x) { var B = S.world.BRIDGE; return B && x > B.x - 4 && x < B.x + 324; }
  function dressing(g, s, x0, x1, y1, day) {
    var L = s.L, S = L.fly.stage, R = S.road, i, x, y;
    if (!R || x1 < R[0][0] || x0 > R[R.length - 1][0]) return;
    function col(c) { return rgb(day ? c : nightRGB(c)); }
    var xa = Math.max(x0, R[0][0]), xb = Math.min(x1, R[R.length - 1][0]);
    // the terraces: level walls of stone every 24 px down the hill, each from where the hill's face meets it, a strip of
    // crops along the top of each
    var tw = col(TWALL), tl = col(mix(TWALL, [255, 255, 255], 0.25)), td = col(mix(TWALL, [0, 0, 0], 0.4)), tc = col(TCROP);
    for (var Y = Math.floor(Sim.groundY(L, xb) / 24) * 24 + 24; Y < y1; Y += 24) {
      var xs = xa;
      while (xs < xb && Sim.groundY(L, xs) > Y - 4) xs += 4;
      if (xs >= xb) continue;
      for (x = xs; x < xb; x += 4) {
        if (onBridge(S, x) && Y > S.world.BRIDGE.deck) continue;
        g.fillStyle = tc; g.fillRect(x, Y - 2, 4, 2);
        g.fillStyle = ((x >> 2) + (Y >> 3)) % 3 ? tw : td; g.fillRect(x, Y, 4, 3);
        g.fillStyle = tl; g.fillRect(x, Y, 3, 1);
      }
    }
    // the low wall along the road's edge
    var gw = col(GUARD), gl = col(mix(GUARD, [255, 255, 255], 0.3));
    for (x = Math.floor(xa / 8) * 8; x < xb; x += 8) {
      if (onBridge(S, x)) continue;
      y = Math.round(roadY(R, x + 3));
      g.fillStyle = gw; g.fillRect(x, y - 4, 7, 4);
      g.fillStyle = gl; g.fillRect(x, y - 4, 7, 1);
    }
    // bushes on the slope below the road
    for (i = Math.floor(xa / 37); i * 37 < xb; i++) {
      if (hash(i, 501) < 0.45) continue;
      x = i * 37 + Math.floor(hash(i, 502) * 20); y = Math.round(Sim.groundY(L, clamp(x, 0, L.width))) + 6 + Math.floor(hash(i, 503) * 30);
      if (onBridge(S, x)) continue;
      var bw = 5 + Math.floor(hash(i, 504) * 6);
      g.fillStyle = col(BUSH); g.fillRect(x - (bw >> 1), y - 3, bw, 4); g.fillRect(x - (bw >> 1) + 1, y - 5, bw - 2, 2);
      g.fillStyle = col(mix(BUSH, [255, 255, 255], 0.2)); g.fillRect(x - (bw >> 1) + 1, y - 5, bw - 3, 1);
    }
    // the poles, and the wires between them
    var P = S.poles || (S.poles = (function () { var o = [], px; for (px = R[0][0] + 70; px < R[R.length - 1][0]; px += 170) if (!onBridge(S, px)) o.push([px, roadY(R, px)]); return o; })());
    g.strokeStyle = col(WIRE); g.lineWidth = 1;
    for (i = 0; i < P.length; i++) {
      var p0 = P[i];
      if (p0[0] < x0 - 200 || p0[0] > x1 + 200) continue;
      g.fillStyle = col(POLE); g.fillRect(p0[0], p0[1] - 50, 2, 50);
      g.fillStyle = col(mix(POLE, [0, 0, 0], 0.3)); g.fillRect(p0[0] - 5, p0[1] - 47, 12, 2);
      var p1 = P[i + 1];
      if (p1 && p1[0] - p0[0] < 400) {
        g.beginPath(); g.moveTo(p0[0] - 4, p0[1] - 46); g.quadraticCurveTo((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - 40, p1[0] - 4, p1[1] - 46); g.stroke();
        g.beginPath(); g.moveTo(p0[0] + 6, p0[1] - 46); g.quadraticCurveTo((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - 38, p1[0] + 6, p1[1] - 46); g.stroke();
      }
    }
  }
  function scene(s, paused, k) {
    if (!on(s)) return;
    K = k; cx = K.ctx(); tick = K.tick(); view(s);
    var N = nightCopies(s.L.fly.stage, s.L.fly.scenery);
    if (!N) return;
    var S = s.L.fly.stage, x0 = Math.floor(s.cam) - 2, x1 = x0 + W + 4, y0 = Math.floor(s.camY) - 2, y1 = y0 + H + 4, dk = night(s);
    ground(cx, s, x0, x1, y1, !dk);
    dressing(cx, s, x0, x1, y1, !dk);
    pieces(cx, dk ? N.stage : N.day, S, x0, y0, x1, y1);
    keepGate(s, dk);
    var dw = s.dawn || 0;
    if (dw > 0 && N.dawn) {
      cx.globalAlpha = dw;
      ground(cx, s, x0, x1, y1, 'dawn');
      pieces(cx, N.dawn.stage, S, x0, y0, x1, y1);
      keepGate(s, 'dawn');
      cx.globalAlpha = 1;
    }
    // in the searchlight: the stage in its own colours
    if (dk && lampA(s) > 0) coneDay(s, N, S, lampA(s));
  }
  // the searchlight's triangle (from the lamp on the nose, the way the beam points)
  function cone(s, len) {
    var h = s.heli, F = Sim.F, lp = Sim.ext.fly.lamp(h), lx = lp.x, ly = lp.y, a = h.face > 0 ? h.beam : Math.PI - h.beam, L2 = len || F.BEAM_LEN;
    return [[lx, ly], [lx + Math.cos(a - F.BEAM_HALF) * L2, ly + Math.sin(a - F.BEAM_HALF) * L2],
            [lx + Math.cos(a + F.BEAM_HALF) * L2, ly + Math.sin(a + F.BEAM_HALF) * L2], a];
  }
  var coneCv = null, maskCv = null;
  function coneDay(s, N, S, la) {
    var cn = cone(s), F = Sim.F, i;
    var bx0 = Math.floor(Math.min(cn[0][0], cn[1][0], cn[2][0])) - 2, by0 = Math.floor(Math.min(cn[0][1], cn[1][1], cn[2][1])) - 2;
    var bx1 = Math.ceil(Math.max(cn[0][0], cn[1][0], cn[2][0])) + 2, by1 = Math.ceil(Math.max(cn[0][1], cn[1][1], cn[2][1])) + 2;
    bx0 = Math.max(bx0, Math.floor(s.cam)); by0 = Math.max(by0, Math.floor(s.camY)); bx1 = Math.min(bx1, Math.ceil(s.cam + W)); by1 = Math.min(by1, Math.ceil(s.camY + H));
    var bw = bx1 - bx0, bh = by1 - by0;
    if (bw <= 0 || bh <= 0) return;
    if (!coneCv || coneCv.width < bw || coneCv.height < bh) { coneCv = canvas(Math.max(bw, 320), Math.max(bh, 320)); maskCv = canvas(coneCv.width, coneCv.height); }
    var g = coneCv.getContext('2d'), m = maskCv.getContext('2d');
    g.setTransform(1, 0, 0, 1, 0, 0); g.globalCompositeOperation = 'source-over'; g.clearRect(0, 0, bw, bh);
    g.translate(-bx0, -by0);
    ground(g, s, bx0, bx1, by1, true);
    dressing(g, s, bx0, bx1, by1, true);
    pieces(g, N.day, S, bx0, by0, bx1, by1);
    keepGate(s, false, g);
    g.setTransform(1, 0, 0, 1, 0, 0);
    // the light's shape: soft at its sides, fading along its length
    m.setTransform(1, 0, 0, 1, 0, 0); m.globalCompositeOperation = 'source-over'; m.clearRect(0, 0, bw, bh);
    m.translate(-bx0, -by0);
    var lx = cn[0][0], ly = cn[0][1], a = cn[3];
    for (i = 0; i < 3; i++) {
      var hw = F.BEAM_HALF * (1 - i * 0.28);
      m.fillStyle = 'rgba(0,0,0,0.45)';
      m.beginPath(); m.moveTo(lx, ly);
      m.lineTo(lx + Math.cos(a - hw) * F.BEAM_LEN, ly + Math.sin(a - hw) * F.BEAM_LEN);
      m.lineTo(lx + Math.cos(a + hw) * F.BEAM_LEN, ly + Math.sin(a + hw) * F.BEAM_LEN);
      m.closePath(); m.fill();
    }
    m.globalCompositeOperation = 'destination-in';
    var rg = m.createRadialGradient(lx, ly, 6, lx, ly, F.BEAM_LEN);
    rg.addColorStop(0, 'rgba(0,0,0,1)'); rg.addColorStop(0.55, 'rgba(0,0,0,0.9)'); rg.addColorStop(1, 'rgba(0,0,0,0)');
    m.fillStyle = rg; m.fillRect(bx0, by0, bw, bh);
    m.setTransform(1, 0, 0, 1, 0, 0);
    g.globalCompositeOperation = 'destination-in'; g.drawImage(maskCv, 0, 0);
    g.globalCompositeOperation = 'source-over';
    cx.globalAlpha = la;
    cx.drawImage(coneCv, 0, 0, bw, bh, bx0, by0, bw, bh);
    cx.globalAlpha = 1;
  }

  // ------------------------------------------------------------------ the Zanabeel's machines, the missile man, the crates
  // (K.spr draws each of them from the sprites render.js chose with tint(): the night's, or in the searchlight their own;
  // the guns and the launcher, from the Apache's sheet, the same way)
  function parapet(e, dk) {
    if (e.px == null) return;
    var c0 = dk ? nightRGB([150, 120, 86]) : [150, 120, 86], c1 = dk ? nightRGB([234, 226, 210]) : [234, 226, 210];
    cx.fillStyle = rgb(c0); cx.fillRect(Math.round(e.px) - 8, Math.round(e.py) - 9, 16, 9);
    cx.fillStyle = 'rgba(0,0,0,0.2)'; cx.fillRect(Math.round(e.px) + 5, Math.round(e.py) - 8, 3, 8);
    cx.fillStyle = rgb(c1); cx.fillRect(Math.round(e.px) - 8, Math.round(e.py) - 9, 16, 1);
  }
  var LOOKS = { worried: 1, angry: 1, youth: 1, qat: 1 };
  function man(s, e, k) {
    if (e.ext !== 'fly' || !on(s) || !sheet()) return false;
    K = k; cx = K.ctx(); tick = K.tick();
    var dk = !!tint(s, e);
    SH = dk ? NG.taiz : IMT;
    var done = drawMan(s, e, dk);
    SH = null;
    return done;
  }
  function drawMan(s, e, dk) {
    var h = s.heli, flip = e.face < 0, lk = LOOKS[e.look] ? e.look : 'angry', Fz = Sim.F;
    if (e.k === 'aa') {
      var bx = Math.round(e.x), by = Math.round(e.y);
      if (!e.alive) {
        tsprRot('aa_bar_burnt', bx + 1, by - 12, -0.3);
        tspr('aa_wreck', bx, by);
        if (tick % 6 === 0) K.part('smoke', bx + (Math.random() - 0.5) * 12, by - 14, { life: 34, vx: -6, vy: -30 });
        return true;
      }
      // the gunner on his seat behind the gun, the barrels over the sandbags
      var white = flash(e), rec = e.st === 'burst' && (e.stT % 5) < 2 ? -2 : 0;
      tspr(white ? 'aa_gunner!' : 'aa_gunner', bx - 10 + (e.st === 'burst' ? (tick >> 1) % 2 : 0), by - 8);
      tsprRot(white ? 'aa_bar!' : 'aa_bar', bx + 1 + Math.cos(e.bar) * rec, by - 14 + Math.sin(e.bar) * rec, e.bar);
      tspr(white ? 'aa_base!' : 'aa_base', bx, by);
      if (e.st === 'aim' && (tick >> 2) % 2) K.spr('hud_alert', bx, by - 26);
      return true;
    }
    if (e.k === 'drone') {
      if (e.st === 'gone' || !e.alive) return true;
      var f = 'kdrone' + ((tick >> 1) & 1), dy = e.y - 5;
      if (e.st === 'tell') {
        K.dotted(e.x, dy, e.tx, e.ty, 6, '#ff4030');                                  // (where it means to go)
        if ((tick >> 2) % 2) { cx.fillStyle = '#ff4030'; cx.fillRect(Math.round(e.tx) - 3, Math.round(e.ty), 7, 1); cx.fillRect(Math.round(e.tx), Math.round(e.ty) - 3, 1, 7); }
        K.spr(f + ((tick >> 2) % 2 ? '!' : ''), e.x, dy);
      } else if (e.st === 'dive') {
        K.sprRot(f, e.x, dy, Math.atan2(e.vy, e.vx) * 0.5, e.vx < 0);
      } else if (e.st === 'oops') {
        K.sprRot(f, e.x, dy, Math.PI + Math.sin(tick * 0.45) * 0.35, false);          // (the wrong way up, wobbling)
      } else K.spr(flash(e) ? f + '!' : f, e.x, dy);
      // (its light, blinking: how it is seen coming at night)
      if (dk && (tick + e.id * 7) % 40 < 6) { cx.fillStyle = '#ff3a26'; cx.fillRect(Math.round(e.x), Math.round(dy) - 4, 1, 1); }
      return true;
    }
    if (e.k === 'crate') { crate(s, e, dk); return true; }
    if (e.k === 'truck') { pickup(s, e, dk); return true; }
    if (e.k === 'cgun') { castleGun(s, e, dk); return true; }
    if (e.k === 'launcher') { launcherPic(s, e, dk); return true; }
    var base = 'rifle_' + lk + '_';
    // over the edge of his roof, arms up, tumbling (Khaled, 21 Oct: make them run and jump off buildings)
    if (e.alive && e.st === 'panic' && e.air) { K.sprRot(base + 'flung', e.x, e.y - 18, e.spin || 0, flip, 18); return true; }
    if (e.k === 'sniper') { sniper(s, e, base, flip, dk); return true; }
    if (e.k === 'mortar' && e.alive && !e.emerge) { mortar(s, e, base, flip, dk); return true; }
    if (e.k === 'light' && e.alive) { lamp2(s, e, base, flip, dk); return true; }
    if (e.k === 'rpg' && e.alive && !e.emerge) { rpgMan(s, e, base, flip, dk); return true; }
    // on his way to his post: out of a doorway (out of its dark), up through a hatch (from under the floor)
    if (e.alive && e.emerge > 0) {
      if (e.entry === 'hatch') { var rise = Math.round(32 * e.emerge / Fz.RISE_T); K.spr(base + 'stand', e.x, e.y + rise, flip, 1, rise); }
      else K.spr(base + 'stand', e.x, e.y, flip, Math.max(0.1, 1 - e.emerge / Fz.DOOR_T));
      if (e.k === 'sam' && e.entry !== 'hatch') tsprRot('sam_tube', e.x - e.face * 3, e.y - 24, flip ? Math.PI - 0.5 : 0.5);
      return true;
    }
    if (e.k === 'sam') {
      var alpha = e.emerge > 0 ? Math.max(0.15, 1 - e.emerge / 30) : 1;
      if (!e.alive) {
        if (e.air) K.spr(base + 'flung', e.x, e.y, flip);
        else if (e.deadT < 70 && (e.deadT < 40 || (e.deadT >> 1) % 2)) K.sprRot(base + 'flung', e.x, e.y - 4, flip ? Math.PI / 2 : -Math.PI / 2, false);
        parapet(e, dk);
        return true;
      }
      if (e.st === 'panic') { K.spr(base + 'up_' + ((Math.floor(e.walkD / 8) % 2) ? 'pass' : 'run'), e.x, e.y, flip); parapet(e, dk); return true; }
      if (e.st === 'out') {
        // the launcher over his shoulder on the way
        K.spr(base + ((Math.floor(e.walkD / 8) % 2) ? 'pass' : 'run'), e.x, e.y, flip);
        tsprRot('sam_tube', e.x - e.face * 3, e.y - 24, flip ? Math.PI - 0.5 : 0.5);
        parapet(e, dk);
        return true;
      }
      var hurt = flash(e) ? '!' : '';
      if (e.st !== 'aim' && e.st !== 'fired') {
        // down behind his parapet, the top of the launcher showing (locking on from there: its sight blinks with the beat)
        var tx0 = e.x - e.face * 3, ty0 = e.y - 14;
        var a0 = flip ? Math.PI : 0;
        if (h && e.st === 'lock') { var da0 = Math.atan2(h.y - ty0, h.x - tx0) - a0; while (da0 > Math.PI) da0 -= 2 * Math.PI; while (da0 < -Math.PI) da0 += 2 * Math.PI; a0 += da0 * 0.4; }
        tsprRot('sam_tube', tx0, ty0, a0);
        K.spr(base + 'stand' + hurt, e.x, e.y + 16, flip, alpha, 16);
        parapet(e, dk);
        if (e.st === 'lock' && beatT < 4) { cx.fillStyle = '#ff3020'; cx.fillRect(Math.round(tx0) - 1, Math.round(ty0) - 3, 3, 3); }
        return true;
      }
      // up, with it on his shoulder, pointed at the Apache (the sight lit for the long tone); after it goes, smoke at its back
      K.spr(base + 'stand' + hurt, e.x, e.y, flip);
      var ang = h ? Math.atan2(h.y - (e.y - 29), (h.x - e.x)) : 0, tx = e.x - e.face * 2, ty = e.y - 29;
      tsprRot('sam_tube', tx, ty, ang);
      parapet(e, dk);
      if (e.st === 'aim' && (tick >> 1) % 2) { cx.fillStyle = '#ff3020'; cx.fillRect(Math.round(tx + Math.cos(ang) * 3 - Math.sin(ang) * 3), Math.round(ty + Math.sin(ang) * 3 - 3), 2, 2); }
      if (e.st === 'fired' && e.stT < 30 && tick % 4 === 0) K.part('smoke', tx - Math.cos(ang) * 10, ty - Math.sin(ang) * 10, { life: 26, vx: -Math.cos(ang) * 20, vy: -24 });
      return true;
    }
    // giving up (Khaled's pick, 22 Oct): some wave a white vest over their heads, and now and then one holds up a sign
    if (e.k === 'rifle' && e.alive && e.st === 'panic') {
      K.spr(base + 'up_' + ((Math.floor(e.walkD / 8) % 2) ? 'pass' : 'run'), e.x, e.y, flip);
      giveUp(e, dk);
      return true;
    }
    return false;                      // (riflemen: drawn as everywhere else)
  }
  function giveUp(e, dk) {
    var x = Math.round(e.x), top = Math.round(e.y) - 37, kind = e.id % 5 === 2 ? 'sign' : (e.id % 2 ? 'vest' : '');
    if (kind === 'vest') {
      // a white vest held up in both hands, flapping
      var fl = (tick >> 2) & 1, wc = dk ? [200, 204, 216] : [248, 246, 238], ws = dk ? [140, 142, 160] : [196, 190, 176];
      cx.fillStyle = rgb(wc); cx.fillRect(x - 7, top - 9 - fl, 14, 9); cx.fillRect(x + (fl ? 7 : -11), top - 8 + fl, 4, 5);
      cx.fillStyle = rgb(ws); cx.fillRect(x - 7, top - 1 - fl, 14, 1); cx.fillRect(x - 4, top - 9 - fl, 2, 4); cx.fillRect(x + 2, top - 9 - fl, 2, 4);
    } else if (kind === 'sign') {
      // a bit of box held up on a stick: I'M ONLY THE COOK
      var label = T("I'M ONLY THE COOK"), w = K.textW('s_lav', label) + 6, x0 = x - Math.round(w / 2), bc = dk ? [92, 76, 56] : [150, 120, 82];
      cx.fillStyle = rgb(mix(bc, [0, 0, 0], 0.35)); cx.fillRect(x - 1, top - 6, 2, 8);
      cx.fillStyle = rgb(bc); cx.fillRect(x0, top - 17, w, 11);
      cx.fillStyle = rgb(mix(bc, [255, 255, 255], 0.2)); cx.fillRect(x0, top - 17, w, 1);
      K.text('s_lav', label, x, top - 15, 'c');
    }
  }
  // the colours of a thing drawn here: its own, or the night's
  function nc(c, dk) { return rgb(dk ? nightRGB(c) : c); }
  // a tube (a launcher, a mortar): from (x, y) along ang, len long, w thick, with a cone on its end (warhead) if any
  function tube(x, y, ang, len, w, col, head, dk) {
    cx.save(); cx.translate(Math.round(x), Math.round(y)); cx.rotate(ang);
    cx.fillStyle = nc(col, dk); cx.fillRect(-3, -Math.floor(w / 2), len, w);
    cx.fillStyle = nc(mix(col, [255, 255, 255], 0.25), dk); cx.fillRect(-3, -Math.floor(w / 2), len, 1);
    if (head) { cx.fillStyle = nc(head, dk); cx.fillRect(len - 3, -Math.floor(w / 2) - 1, 3, w + 2); cx.fillRect(len, -Math.floor(w / 2), 2, w); cx.fillRect(len + 2, -1, 1, 2); }
    cx.restore();
  }
  // the RPG: on his shoulder, pointing up and back as he waits; down on it at the Apache as he aims, its head glinting
  var RPGC = [74, 82, 54], RPGH = [110, 96, 66];
  function rpgMan(s, e, base, flip, dk) {
    var aim = e.st === 'aim', hurt = flash(e) ? '!' : '';
    K.spr(base + (aim ? 'aim' : (e.moving ? ((Math.floor(e.walkD / 8) % 2) ? 'pass' : 'run') : 'stand')) + hurt, e.x, e.y, flip);
    var a = aim && e.aimA != null ? e.aimA : (e.face > 0 ? -0.55 : Math.PI + 0.55);
    tube(e.x - e.face * 3, e.y - 27, a, 15, 3, RPGC, RPGH, dk);
    if (aim && (tick >> 1) % 2) { var hx = e.x - e.face * 3 + Math.cos(a) * 15, hy = e.y - 27 + Math.sin(a) * 15; cx.fillStyle = '#fff4c0'; cx.fillRect(Math.round(hx), Math.round(hy) - 1, 1, 1); }
    if (aim && (tick >> 2) % 2) K.spr('hud_alert', e.x, e.y - 40);
  }
  // a sniper: in the dark of his window (a glint now and then); at it, his head and shoulders over the sill and the laser
  // of his sight on the Apache
  function sniper(s, e, base, flip, dk) {
    if (!e.alive) { if (e.deadT < 40 && (e.deadT >> 1) % 2) K.spr(base + 'flung', e.x, e.y + 20, flip, 1, 20); return; }
    if (e.st === 'hide') { if ((tick + e.id * 37) % 170 < 3) { cx.fillStyle = '#e8f0ff'; cx.fillRect(Math.round(e.x), Math.round(e.y) - 8, 1, 1); } return; }
    K.spr(base + 'aim' + (flash(e) ? '!' : ''), e.x - e.face * 2, e.y + 20, flip, 1, 20);
  }
  function laser(e) {
    var mx = e.x + e.face * 10, my = e.y - 10, f = Math.min(1, e.stT / Sim.F.SNIPE_AIM);
    cx.save(); cx.globalCompositeOperation = 'lighter';
    cx.strokeStyle = 'rgba(255,40,30,' + (0.25 + 0.45 * f * (0.7 + 0.3 * Math.sin(tick * 0.6))).toFixed(3) + ')'; cx.lineWidth = 1;
    cx.beginPath(); cx.moveTo(mx + 0.5, my + 0.5); cx.lineTo(e.lx + 0.5, e.ly + 0.5); cx.stroke();
    cx.fillStyle = 'rgba(255,60,40,0.9)'; cx.fillRect(Math.round(e.lx) - 1, Math.round(e.ly) - 1, 2, 2);
    cx.restore();
  }
  // a mortar: its baseplate, the tube up at an angle, the man crouched at it
  var MORT = [70, 74, 60];
  function mortar(s, e, base, flip, dk) {
    var x = Math.round(e.x), y = Math.round(e.y), hurt = flash(e) ? '!' : '';
    K.spr(base + 'stand' + hurt, e.x - e.face * 9, e.y + 6, e.face < 0, 1, 6);
    cx.fillStyle = nc(MORT, dk); cx.fillRect(x - 6, y - 2, 12, 2);
    tube(x, y - 2, e.face > 0 ? -1.15 : Math.PI + 1.15, 15, 4, MORT, null, dk);
    if (e.st === 'load' && e.stT > 14 && (tick >> 1) % 2) { cx.fillStyle = '#ffd040'; cx.fillRect(x + e.face * 4, y - 15, 2, 2); }
  }
  // a searchlight on its stand, its operator beside it (its beam is drawn with the light: post)
  function lamp2(s, e, base, flip, dk) {
    var x = Math.round(e.x), y = Math.round(e.y), hurt = flash(e) ? '!' : '';
    K.spr(base + 'stand' + hurt, e.x - 11, e.y, false);
    cx.fillStyle = nc([60, 60, 66], dk); cx.fillRect(x - 1, y - 10, 2, 10); cx.fillRect(x - 5, y - 1, 10, 1);
    cx.save(); cx.translate(x, y - 13); cx.rotate(e.beam);
    cx.fillStyle = hurt ? '#fff8e8' : nc([84, 86, 92], dk); cx.fillRect(-6, -4, 10, 8);
    cx.fillStyle = '#fff6d8'; cx.fillRect(4, -4, 2, 8);
    cx.restore();
  }
  // a pickup with its gun in the back: tilted with the road, its wheels turning, the gunner turned round to fire back; a
  // wreck, burning
  function pickup(s, e, dk) {
    var wr = (K.rig('car') || { wheel: 29 }).wheel, body = 'truck_' + (e.paint || 'olive');
    cx.save(); cx.translate(Math.round(e.x), Math.round(e.y)); cx.rotate(e.ang || 0);
    if (!e.alive) {
      K.spr('truck_burnt', 0, 0, false); K.spr('wheel0', -wr, -9); K.spr('wheel0', wr, -9);
      cx.restore();
      if (tick % 4 === 0) K.part('smoke', e.x + (Math.random() - 0.5) * 40, e.y - 30, { life: 40, vx: -10, vy: -40 });
      if (tick % 7 === 0) K.part('ember', e.x + (Math.random() - 0.5) * 30, e.y - 20, { life: 16, vx: (Math.random() - 0.5) * 30, vy: -60 });
      return;
    }
    var bob = (Math.floor(e.wheel / 13) & 1), gx = -20;
    var rec = e.gst === 'burst' && (e.gT % 6) < 3 ? 1 : 0;
    K.spr('rifle_angry_aim' + (flash(e) ? '!' : ''), gx + rec, -22 + bob, true);
    K.spr('truck_gun', gx - 6 + rec, -22 + bob);
    K.spr(body + (flash(e) ? '!' : ''), 0, bob, false);
    var wn = e.vx > 150 ? 'wheelf' + ((tick >> 1) & 1) : 'wheel' + (3 - (((Math.floor(e.wheel / 2.4) % 4) + 4) % 4));
    K.spr(wn, -wr, -9); K.spr(wn, wr, -9);
    if (e.load) load(e.load, bob, dk, flash(e));
    cx.restore();
    if (e.gst === 'tell' && (tick >> 2) % 2) K.spr('hud_alert', e.x - 22, e.y - 64);
    if (e.hp <= 6 && tick % 5 === 0) K.part('smoke', e.x + 30, e.y - 28, { life: 24, vx: -30, vy: -30 });
    if (e.st === 'drive' && e.vx > 60 && tick % 4 === 0) K.part('puff', e.x - 46, e.y - 3, { life: 10, vx: -20, flip: true });
  }
  // what a pickup in the chase carries on its cab's roof, roped down (Khaled's pick, 22 Oct): a sofa, or a goat looking back
  // at the Apache. (A little of their own colour kept at night, so they read on the dark road.)
  var SOFA = [184, 54, 64], GOAT = [238, 234, 222], GOATP = [44, 38, 34];
  function load(kind, bob, dk, white) {
    var c = function (q) { return white ? '#fff8e8' : rgb(dk ? mix(nightRGB(q), q, 0.35) : q); }, y = -42 + bob;
    if (kind === 'sofa') {
      // from the front: its back across the top, the arms at its ends, three cushions, gold feet, two turns of rope
      cx.fillStyle = c(SOFA); cx.fillRect(-9, y - 11, 28, 5); cx.fillRect(-10, y - 7, 4, 6); cx.fillRect(16, y - 7, 4, 6); cx.fillRect(-6, y - 5, 22, 4);
      cx.fillStyle = c(mix(SOFA, [255, 255, 255], 0.35)); cx.fillRect(-9, y - 11, 28, 1); cx.fillRect(-6, y - 5, 22, 1); cx.fillRect(-10, y - 7, 4, 1); cx.fillRect(16, y - 7, 4, 1);
      cx.fillStyle = c(mix(SOFA, [0, 0, 0], 0.45)); cx.fillRect(1, y - 5, 1, 4); cx.fillRect(8, y - 5, 1, 4); cx.fillRect(-6, y - 6, 22, 1);
      cx.fillStyle = c([232, 190, 84]); cx.fillRect(-9, y - 1, 2, 1); cx.fillRect(17, y - 1, 2, 1);
      cx.fillStyle = c([70, 56, 40]); cx.fillRect(-3, y - 12, 1, 12); cx.fillRect(12, y - 12, 1, 12);
    } else if (kind === 'goat') {
      // side on, facing back up the road, its head up; now and then it looks round
      var nod = ((tick >> 5) & 1) && !white ? 1 : 0;
      cx.fillStyle = c(GOAT);
      cx.fillRect(-4, y - 9, 15, 6); cx.fillRect(-8, y - 12, 5, 5); cx.fillRect(-11, y - 15 + nod, 6, 5);
      cx.fillRect(-3, y - 3, 1, 3); cx.fillRect(0, y - 3, 1, 3); cx.fillRect(7, y - 3, 1, 3); cx.fillRect(10, y - 3, 1, 3); cx.fillRect(11, y - 10, 2, 2);
      cx.fillStyle = c(GOATP);
      cx.fillRect(2, y - 9, 5, 3); cx.fillRect(-8, y - 18 + nod, 1, 3); cx.fillRect(-7, y - 19 + nod, 2, 1); cx.fillRect(-5, y - 18 + nod, 1, 1);
      cx.fillRect(-10, y - 13 + nod, 1, 1); cx.fillRect(-11, y - 10 + nod, 1, 2);
      cx.fillStyle = c(mix(GOAT, [0, 0, 0], 0.3)); cx.fillRect(-5, y - 15 + nod, 1, 2); cx.fillRect(-4, y - 4, 15, 1);
    }
  }
  // THE CASTLE GUN: twin barrels on a turntable behind a shield, sandbags round it; under a tarp until it rises. (It
  // stands in the castle's floodlights, as the walls do: lit warm at night, so it reads against the sky.)
  var CG = [104, 108, 80], CGD = [62, 64, 46], BAGS = [150, 132, 96], TARP = [92, 96, 58];
  function fl(c, dk) { return rgb(dk ? flRGB(c) : c); }
  function flRGB(c) { var l = (c[0] * 77 + c[1] * 150 + c[2] * 29) >> 8; return mix(nightRGB(c), [Math.min(255, l * 1.08 + 26), l * 0.8 + 12, l * 0.42 + 6], 0.6); }
  function castleGun(s, e, dk) {
    var x = Math.round(e.x), y = Math.round(e.y), hurt = e.alive && flash(e), Fz = Sim.BG, W2 = '#fff8e8';
    // the sandbags round it
    for (var b = -36; b < 36; b += 9) { cx.fillStyle = fl(BAGS, dk); cx.fillRect(x + b, y - 9, 8, 9); cx.fillStyle = fl(mix(BAGS, [255, 255, 255], 0.25), dk); cx.fillRect(x + b + 1, y - 9, 6, 1); cx.fillStyle = fl(mix(BAGS, [0, 0, 0], 0.35), dk); cx.fillRect(x + b + 7, y - 8, 1, 8); }
    if (e.st === 'cover' || (e.st === 'rise' && e.stT < 12)) {
      // a tarp over a hump
      cx.fillStyle = fl(TARP, dk); cx.beginPath(); cx.moveTo(x - 38, y - 8); cx.quadraticCurveTo(x - 26, y - 52, x + 6, y - 50); cx.quadraticCurveTo(x + 36, y - 46, x + 38, y - 8); cx.closePath(); cx.fill();
      cx.fillStyle = fl(mix(TARP, [255, 255, 255], 0.25), dk); cx.fillRect(x - 18, y - 45, 24, 1); cx.fillRect(x - 30, y - 30, 8, 1);
      cx.fillStyle = fl(mix(TARP, [0, 0, 0], 0.3), dk); cx.fillRect(x + 10, y - 40, 1, 30);
      return;
    }
    var sink = e.st === 'rise' ? Math.round((1 - e.rise) * 24) : 0, py = y - 30 + sink, ang = e.alive ? e.bar : -0.3;
    // the turntable and the breech
    cx.fillStyle = hurt ? W2 : fl(CGD, dk); cx.fillRect(x - 20, y - 20 + sink, 40, 12);
    cx.fillStyle = hurt ? W2 : fl(mix(CGD, [255, 255, 255], 0.2), dk); cx.fillRect(x - 20, y - 20 + sink, 40, 1);
    cx.fillStyle = hurt ? W2 : fl(CG, dk); cx.fillRect(x - 15, py - 8, 30, 16);
    cx.fillStyle = hurt ? W2 : fl(mix(CG, [255, 255, 255], 0.25), dk); cx.fillRect(x - 15, py - 8, 30, 2);
    cx.fillStyle = fl(CGD, dk); cx.fillRect(x - 3, py - 3, 6, 6);
    // the barrels
    for (var t2 = -1; t2 <= 1; t2 += 2) {
      cx.save(); cx.translate(x - Math.sin(ang) * t2 * 4, py + Math.cos(ang) * t2 * 4); cx.rotate(ang);
      cx.fillStyle = hurt ? W2 : fl(CG, dk); cx.fillRect(0, -2, 52, 4);
      cx.fillStyle = hurt ? W2 : fl(mix(CG, [255, 255, 255], 0.3), dk); cx.fillRect(0, -2, 52, 1);
      cx.fillStyle = fl(CGD, dk); cx.fillRect(46, -3, 7, 6); cx.fillRect(12, -3, 3, 6);
      if (e.alive && e.phase === 3) { cx.fillStyle = 'rgba(255,90,40,' + (0.4 + 0.25 * Math.sin(tick * 0.4)).toFixed(2) + ')'; cx.fillRect(20, -2, 26, 4); }
      // (a sweep coming: the barrels warm up; too hot to fire after it: red, fading as they cool)
      if (e.alive && e.st === 'sweep' && e.stT <= Fz.CG_SWEEP_TELL) { cx.fillStyle = 'rgba(255,170,60,' + (0.3 + 0.35 * ((tick >> 2) & 1)).toFixed(2) + ')'; cx.fillRect(14, -2, 38, 4); }
      if (e.alive && e.st === 'cool') { cx.fillStyle = 'rgba(255,70,30,' + (0.85 * (1 - e.stT / Fz.CG_COOL)).toFixed(2) + ')'; cx.fillRect(8, -2, 45, 4); }
      cx.restore();
    }
    // the shield, until it comes off (phase 2)
    if (e.alive && e.phase === 1) {
      cx.fillStyle = hurt ? W2 : fl(mix(CG, [0, 0, 0], 0.1), dk);
      cx.beginPath(); cx.moveTo(x - 26, y - 9 + sink); cx.lineTo(x - 26, py - 16); cx.lineTo(x - 13, py - 22); cx.lineTo(x - 8, y - 9 + sink); cx.closePath(); cx.fill();
      cx.fillStyle = fl([200, 196, 170], dk); for (var rv = 0; rv < 4; rv++) cx.fillRect(x - 23, py - 12 + rv * 6, 1, 1);
      cx.fillStyle = fl(mix(CG, [255, 255, 255], 0.3), dk); cx.fillRect(x - 26, py - 16, 1, py > 0 ? (y - 9 + sink) - (py - 16) : 1);
    }
    if (!e.alive) { if (tick % 5 === 0) K.part('smoke', x + (Math.random() - 0.5) * 40, y - 24, { life: 46, vx: -8, vy: -36 }); if (tick % 9 === 0) K.part('ember', x + (Math.random() - 0.5) * 30, y - 20, { life: 16, vx: (Math.random() - 0.5) * 30, vy: -60 }); return; }
    if (e.phase >= 2 && tick % (e.phase === 3 ? 4 : 9) === 0) K.part('smoke', x + 10, py - 8, { life: 30, vx: -6, vy: -30 });
    if (e.st === 'sweep' && e.stT <= Fz.CG_SWEEP_TELL && (tick >> 2) % 2) K.spr('hud_alert', x, y - 60);
    // (cooling: steam off the barrels, white puffs drifting up)
    if (e.st === 'cool' && tick % 4 === 0) { var sa = e.bar, sl = 14 + Math.random() * 36; K.part('puff', x + Math.cos(sa) * sl + (Math.random() - 0.5) * 6, py + Math.sin(sa) * sl, { life: 18, vx: (Math.random() - 0.5) * 10, vy: -40, flip: Math.random() < 0.5 }); }
  }
  // THE LAUNCHER: eight wheels, a cab with a man and a machine gun on its roof, and its missile on a rail that a ram raises
  // (in the castle's floodlights, as the walls are, so it reads; in front of the keep, and through its gate as it comes out)
  var LN = { body: [100, 108, 64], dark: [62, 68, 40], lite: [146, 154, 98], cab: [150, 132, 88], cabD: [104, 90, 58], steel: [74, 76, 80], steelL: [138, 140, 142],
             tyre: [28, 28, 30], hub: [118, 118, 110], glass: [44, 66, 84], glassL: [150, 186, 204], mis: [190, 190, 172], misD: [122, 124, 110], nose: [86, 90, 76],
             tape: [226, 216, 176], fin: [106, 110, 98], smoke: [150, 150, 142] };
  var GATE = { x0: 7468, x1: 7556, top: 336, bot: 420 };
  // (a hit shows as a pale wash over it, not a white shape: it is big, and the gun puts a lot into it)
  function lnCol(c, dk, burnt, white) {
    var v = burnt ? mix(c, [22, 20, 18], 0.8) : (dk ? flRGB(c) : c);
    return rgb(white ? mix(v, [255, 248, 232], 0.55) : v);
  }
  // a missile from its tail (px, py) along a, len long: fins, a pale body with tape round it, a dark nose
  function missileBody(px, py, a, len, dk, white, burnt) {
    var c = function (q) { return lnCol(q, dk, burnt, white); }, b = len - 14;
    cx.save(); cx.translate(Math.round(px), Math.round(py)); cx.rotate(a);
    cx.fillStyle = c(LN.fin);
    cx.beginPath(); cx.moveTo(0, -5); cx.lineTo(-3, -11); cx.lineTo(13, -5); cx.closePath(); cx.fill();
    cx.beginPath(); cx.moveTo(0, 5); cx.lineTo(-3, 11); cx.lineTo(13, 5); cx.closePath(); cx.fill();
    cx.fillStyle = c(LN.mis); cx.fillRect(0, -5, b, 10);
    cx.fillStyle = c(mix(LN.mis, [255, 255, 255], 0.35)); cx.fillRect(0, -5, b, 2);
    cx.fillStyle = c(LN.misD); cx.fillRect(0, 3, b, 2);
    cx.fillStyle = c(LN.tape); cx.fillRect(Math.round(b * 0.3), -5, 3, 10); cx.fillRect(Math.round(b * 0.52), -5, 3, 10); cx.fillRect(Math.round(b * 0.7), -5, 2, 10);
    cx.fillStyle = c(LN.nose); cx.beginPath(); cx.moveTo(b, -5); cx.lineTo(len, 0); cx.lineTo(b, 5); cx.closePath(); cx.fill();
    cx.restore();
  }
  function launcherPic(s, e, dk) {
    var B = Sim.BG, x = Math.round(e.x), y = Math.round(e.y), dead = !e.alive, t0 = e.dieT || 0, white = !dead && flash(e), burnt = dead && t0 > 50, i;
    var bx = function (x0, y0, w, h, c) { cx.fillStyle = lnCol(c, dk, burnt, white); cx.fillRect(Math.round(x0), Math.round(y0), w, h); };
    if (dead && t0 > 150) { cx.fillStyle = 'rgba(10,8,8,0.42)'; cx.beginPath(); cx.ellipse(x, y - 1, 74, 4, 0, 0, Math.PI * 2); cx.fill(); }
    if (dead && t0 > 270) return;
    cx.save();
    if (dead && t0 > 150) cx.globalAlpha = Math.max(0, 1 - (t0 - 150) / 120);
    // (still in the keep: only what is already out, and what can be seen of it in the gateway, between the leaves)
    var inGate = !dead && x + 80 > GATE.x0;
    if (inGate) gateClip(e, x, y);
    var raise = dead ? (e.raise || 0) * Math.max(0, 1 - t0 / 40) : e.raise, a = Math.PI + raise * B.LN_MAX, px = x + B.LN_PIVOT[0], py = y + B.LN_PIVOT[1];
    // the bed, the rail and its pivot, the jacks down at the back once it has stopped
    bx(x - 74, y - 16, 148, 6, LN.steel);
    bx(x - 42, y - 24, 114, 10, LN.body); bx(x - 42, y - 24, 114, 1, LN.lite); bx(x - 42, y - 17, 114, 1, LN.dark);
    if (e.st !== 'roll' && e.st !== 'open' && e.st !== 'hide') { bx(x + 64, y - 14, 4, 13, LN.steel); bx(x + 61, y - 2, 10, 2, LN.steelL); }
    bx(px - 6, py - 4, 12, 10, LN.dark);
    // the cradle under the missile, and the missile (a new one coming out of the keep onto the rail while it loads)
    cx.save(); cx.translate(px, py); cx.rotate(a); cx.fillStyle = lnCol(LN.steel, dk, burnt, white); cx.fillRect(0, 6, 96, 4); cx.restore();
    if (e.missile && !dead) missileBody(px, py, a, B.LN_LEN, dk, white, false);
    if (e.missile && !dead && e.st === 'ignite') {
      // nought: the engine lit at its tail, on the rail, the truck shaking, and smoke billowing out along the courtyard
      var tx2 = px - Math.cos(a) * 4, ty2 = py - Math.sin(a) * 4;
      fire(tx2, ty2, 5 + (tick % 3)); fire(tx2 + 3, ty2 + 6, 3 + ((tick >> 1) % 2));
      glow(tx2, ty2 + 4, 34, [255, 170, 80], 0.45);
      if (tick % 2 === 0) for (var sm = 0; sm < 2; sm++) K.part('smoke', tx2 + (Math.random() - 0.5) * 20, y - 4, { life: 50, vx: (sm ? 1 : -1) * (40 + Math.random() * 70), vy: -6 - Math.random() * 16 });
    }
    else if (!dead && e.st === 'load') { var lf = Math.min(1, e.stT / B.LN_LOAD); missileBody(px + (1 - lf) * B.LN_LEN, py, Math.PI, B.LN_LEN, dk, false, false); }
    else if (dead && e.missile && t0 < 30) missileBody(px, py, a, B.LN_LEN, dk, false, false);
    // the ram that raises it
    var rx = px + Math.cos(a) * 46 + Math.cos(a + Math.PI / 2) * 9, ry = py + Math.sin(a) * 46 + Math.sin(a + Math.PI / 2) * 9;
    cx.strokeStyle = lnCol(LN.steelL, dk, burnt, white); cx.lineWidth = 2; cx.beginPath(); cx.moveTo(x + 10, y - 22); cx.lineTo(rx, ry); cx.stroke();
    cx.strokeStyle = lnCol(LN.steel, dk, burnt, white); cx.lineWidth = 4; cx.beginPath(); cx.moveTo(x + 10, y - 22); cx.lineTo(x + 10 + (rx - x - 10) * 0.45, y - 22 + (ry - y + 22) * 0.45); cx.stroke();
    // the cab
    cx.fillStyle = lnCol(LN.cab, dk, burnt, white);
    cx.beginPath(); cx.moveTo(x - 75, y - 13); cx.lineTo(x - 75, y - 30); cx.lineTo(x - 66, y - 40); cx.lineTo(x - 42, y - 40); cx.lineTo(x - 42, y - 13); cx.closePath(); cx.fill();
    bx(x - 66, y - 40, 24, 1, mix(LN.cab, [255, 255, 255], 0.35)); bx(x - 43, y - 40, 1, 27, LN.cabD);
    {
      cx.fillStyle = lnCol(LN.glass, dk, burnt, white); cx.beginPath(); cx.moveTo(x - 73, y - 30); cx.lineTo(x - 66, y - 38); cx.lineTo(x - 60, y - 38); cx.lineTo(x - 60, y - 30); cx.closePath(); cx.fill();
      bx(x - 56, y - 37, 10, 7, LN.glass); bx(x - 56, y - 37, 10, 1, LN.glassL); bx(x - 69, y - 33, 3, 1, LN.glassL);
      bx(x - 52, y - 29, 1, 15, LN.cabD); bx(x - 77, y - 26, 2, 10, LN.steel);
      cx.fillStyle = burnt ? '#2a2420' : (dk ? '#ffe9a0' : '#e0d8a8'); cx.fillRect(x - 77, y - 19, 2, 3);
    }
    // the wheels (eight, in pairs: four seen), turning as it rolls
    var spin = (e.wheel || 0) / 7;
    [-62, -46, 32, 48].forEach(function (o) {
      var wx = x + o, wy = y - 7;
      cx.fillStyle = burnt ? '#141210' : rgb(LN.tyre); cx.beginPath(); cx.arc(wx, wy, 7, 0, Math.PI * 2); cx.fill();
      cx.fillStyle = lnCol(LN.hub, dk, burnt, white); cx.beginPath(); cx.arc(wx, wy, 3, 0, Math.PI * 2); cx.fill();
      cx.fillStyle = burnt ? '#141210' : rgb(LN.tyre); cx.fillRect(Math.round(wx + Math.cos(spin) * 2), Math.round(wy + Math.sin(spin) * 2), 1, 1);
    });
    cx.restore();
    // the man on the cab with the machine gun (he swings round to it; a mark over him before a burst)
    if (!dead && e.st !== 'open' && !(inGate && (e.door || 0) < 1)) {
      if (inGate) { cx.save(); gateClip(e, x, y); }
      var rec = e.mgst === 'burst' && (e.mgT % 5) < 2 ? 1 : 0, gx = x + B.LN_MG_AT[0], gy = y - 40;
      K.spr('rifle_angry_aim' + (white ? '!' : ''), gx + rec, gy, true);
      K.spr('truck_gun', gx - 6 + rec, gy);
      if (e.mgst === 'tell' && (tick >> 2) % 2) K.spr('hud_alert', gx, gy - 42);
      if (inGate) cx.restore();
    }
    // its smoke, put up when the rocket pod has it
    if (!dead && e.smokeT > 0) {
      var sa = Math.min(1, e.smokeT / 30) * 0.88, up = (B.LN_SMOKE_T - e.smokeT) * 0.16;
      for (i = 0; i < 10; i++) {
        var sx2 = x - 84 + i * 18 + Math.sin(tick * 0.03 + i * 1.7) * 5, sy2 = y - 14 - (i % 3) * 13 - up, r2 = 13 + (i % 4) * 3;
        cx.fillStyle = rgba(dk ? nightRGB(LN.smoke) : LN.smoke, sa); cx.beginPath(); cx.arc(sx2, sy2, r2, 0, Math.PI * 2); cx.fill();
        cx.fillStyle = rgba(dk ? nightRGB(mix(LN.smoke, [255, 255, 255], 0.3)) : mix(LN.smoke, [255, 255, 255], 0.3), sa * 0.8); cx.beginPath(); cx.arc(sx2 - 2, sy2 - 3, r2 * 0.6, 0, Math.PI * 2); cx.fill();
      }
    }
    // hurt: smoke from the engine, and at the last fire on the bed; dead: burning
    if (!dead && e.phase >= 2 && tick % (e.phase === 3 ? 4 : 9) === 0) K.part('smoke', x - 58, y - 40, { life: 30, vx: -6, vy: -30 });
    if (!dead && e.phase === 3) fire(x + 20 + Math.sin(tick * 0.4) * 3, y - 26, 2);
    if (dead && t0 < 230) {
      if (tick % 3 === 0) K.part('smoke', x + (Math.random() - 0.5) * 120, y - 26, { life: 46, vx: -8, vy: -40 });
      if (tick % 5 === 0) K.part('ember', x + (Math.random() - 0.5) * 100, y - 20, { life: 16, vx: (Math.random() - 0.5) * 40, vy: -70 });
      if (t0 < 160) fire(x + Math.sin(tick * 0.3) * 30, y - 22, 3.2);
    }
  }
  // the keep's gate (the launcher is kept behind it): its leaves swing in, and inside, the lamps of the place it was kept
  // what can be seen of the launcher while it is still in the keep: the part already out in the courtyard, and in the
  // gateway what shows between the leaves (all of it once they are right open: they are swung in, behind it)
  function gateClip(e, x, y) {
    var g = GATE, r = (g.x1 - g.x0) / 2, mx = g.x0 + r, spring = g.top + r, op = e.door || 0, lw = op >= 1 ? 0 : r * (1 - op) + 4 * op;
    var a = g.x0 + lw, b = g.x1 - lw;
    cx.beginPath();
    cx.rect(x - 220, y - 240, g.x0 - (x - 220), 260);
    if (b - a > 0.5) {
      var ta = -Math.acos(Math.max(-1, Math.min(1, (a - mx) / r))), tb = -Math.acos(Math.max(-1, Math.min(1, (b - mx) / r)));
      cx.moveTo(a, g.bot); cx.lineTo(a, spring + Math.sin(ta) * r); cx.arc(mx, spring, r, ta, tb, false); cx.lineTo(b, g.bot); cx.closePath();
    }
    cx.clip();
  }
  // (mode: true by night, false in the searchlight's day colours, 'dawn' over the dawn copy; into another canvas if given)
  function keepGate(s, dk, g2) { var c0 = cx; if (g2) cx = g2; keepGateIn(s, dk); cx = c0; }
  function keepGateIn(s, dk) {
    var Lr = null, i;
    for (i = 0; i < s.enemies.length; i++) if (s.enemies[i].k === 'launcher') Lr = s.enemies[i];
    var g = GATE, r = (g.x1 - g.x0) / 2, mx = g.x0 + r, spring = g.top + r, open = !Lr ? 0 : Lr.alive ? (Lr.door || 0) : 1;
    if (g.x1 < s.cam - 10 || g.x0 > s.cam + W + 10) return;
    var gc = function (c) { return dk === 'dawn' ? rgb(dawnRGB(c)) : fl(c, dk); };
    function archPath(rr) { cx.beginPath(); cx.moveTo(mx - rr, g.bot); cx.lineTo(mx - rr, spring); cx.arc(mx, spring, rr, Math.PI, Math.PI * 2); cx.lineTo(mx + rr, g.bot); cx.closePath(); }
    cx.fillStyle = gc([206, 184, 140]); archPath(r + 5); cx.fill();
    cx.fillStyle = gc([150, 128, 96]); archPath(r + 2); cx.fill();
    cx.fillStyle = dk === 'dawn' ? rgb(dawnRGB([30, 26, 24])) : dk ? 'rgb(12,10,16)' : 'rgb(30,26,24)'; archPath(r); cx.fill();
    if (open > 0) {
      // (lamps inside)
      cx.save(); archPath(r); cx.clip();
      var lg = cx.createRadialGradient(mx, g.bot - 34, 4, mx, g.bot - 34, r * 1.3);
      lg.addColorStop(0, 'rgba(255,190,110,' + (0.32 * open).toFixed(3) + ')'); lg.addColorStop(1, 'rgba(255,190,110,0)');
      cx.fillStyle = lg; cx.fillRect(g.x0, g.top, g.x1 - g.x0, g.bot - g.top);
      cx.restore();
    }
    // the leaves: planks and studs, swung in (narrower) as it opens
    cx.save(); archPath(r); cx.clip();
    var lw = Math.round(r * (1 - open) + 4 * open);
    [[g.x0, 1], [g.x1 - lw, -1]].forEach(function (q) {
      cx.fillStyle = gc([110, 74, 44]); cx.fillRect(q[0], g.top, lw, g.bot - g.top);
      cx.fillStyle = gc([76, 50, 30]); for (var px2 = q[0] + 7; px2 < q[0] + lw; px2 += 8) cx.fillRect(px2, g.top, 1, g.bot - g.top);
      cx.fillStyle = gc([40, 38, 36]); for (var sy3 = spring + 6; sy3 < g.bot - 4; sy3 += 18) cx.fillRect(q[0] + 2, sy3, Math.max(1, lw - 4), 2);
    });
    cx.restore();
  }
  // a crate of drones: an olive box with its lid hinged at the back, open while it sends one up (the drone in it, rising)
  var CRATE = [92, 96, 60], CRATE_D = [58, 60, 38], CRATE_L = [140, 142, 96];
  function crate(s, e, dk) {
    var x = Math.round(e.x), y = Math.round(e.y), c0 = dk ? nightRGB(CRATE) : CRATE, c1 = dk ? nightRGB(CRATE_D) : CRATE_D, c2 = dk ? nightRGB(CRATE_L) : CRATE_L;
    if (!e.alive) {
      cx.fillStyle = 'rgb(24,22,22)'; cx.fillRect(x - 11, y - 6, 22, 6);
      cx.fillStyle = 'rgb(44,38,34)'; cx.fillRect(x - 9, y - 8, 6, 2); cx.fillRect(x + 3, y - 7, 7, 1);
      if (tick % 9 === 0) K.part('smoke', x + (Math.random() - 0.5) * 14, y - 8, { life: 30, vx: -4, vy: -26 });
      return;
    }
    var white = flash(e);
    // the drone in it, rising as the lid goes up
    if (e.st === 'open' && e.stT > 6) K.spr('kdrone' + ((tick >> 1) & 1), x, y - 6 - Math.min(10, (e.stT - 6) * 0.7));
    cx.fillStyle = white ? '#fff8e8' : rgb(c0); cx.fillRect(x - 11, y - 10, 22, 10);
    if (!white) {
      cx.fillStyle = rgb(c1); cx.fillRect(x - 11, y - 1, 22, 1); cx.fillRect(x - 4, y - 10, 1, 9); cx.fillRect(x + 3, y - 10, 1, 9); cx.fillRect(x + 10, y - 10, 1, 10);
      cx.fillStyle = rgb(c2); cx.fillRect(x - 11, y - 10, 22, 1);
      cx.fillStyle = dk ? 'rgb(150,150,120)' : 'rgb(236,226,170)'; cx.fillRect(x - 9, y - 7, 3, 2); cx.fillRect(x - 1, y - 7, 2, 2);
    }
    // the lid, hinged at the back left, up by e.lid
    var la = -e.lid * 1.9, lw = 22;
    cx.save(); cx.translate(x - 11, y - 10); cx.rotate(la);
    cx.fillStyle = white ? '#fff8e8' : rgb(c2); cx.fillRect(0, -2, lw, 2);
    cx.fillStyle = rgb(c1); cx.fillRect(0, -1, lw, 1);
    cx.restore();
    if (e.st === 'open' && (tick >> 2) % 2) K.spr('hud_alert', x, y - 22);
    // (what it says on the side, the first time it opens: Khaled's pick, 22 Oct)
    if (e.st === 'open' && captions[e.id] == null) captions[e.id] = tick;
    var ct = captions[e.id] != null ? tick - captions[e.id] : -1;
    if (ct >= 0 && ct < 150) { K.text('s_lav', T('MADE IN TEHRAN'), x, y - 40, 'c'); K.text('s_org', T('FRAGILE'), x, y - 32, 'c'); }
  }

  // ------------------------------------------------------------------ what gives light, then the Apache and what flies
  function post(s, paused, k) {
    if (!on(s) || !sheet()) return;
    K = k; cx = K.ctx(); tick = K.tick(); view(s);
    var h = s.heli, L = s.L, S = L.fly.stage, i, dk = night(s), x0 = s.cam - 40, x1 = s.cam + W + 40;
    // the street lamps: their light about them, and a pool of it on the street
    var dw = s.dawn || 0;
    if (dk && S.lamps && dw < 1) for (i = 0; i < S.lamps.length; i++) {
      var lp = S.lamps[i];
      if (lp[0] < x0 || lp[0] > x1) continue;
      glow(lp[0], lp[1], 26, [255, 206, 130], 0.32 * (1 - dw));
      pool(lp[0], S.world.STREET, 30, [255, 200, 120], 0.16 * (1 - dw));
    }
    // the searchlight: its beam in the air, and where it lands, a pool of light
    var la = lampA(s);
    if (h && dk && la > 0) {
      var cn = cone(s);
      cx.save();
      cx.globalCompositeOperation = 'lighter';
      cx.globalAlpha = la;
      var bg = cx.createLinearGradient(cn[0][0], cn[0][1], (cn[1][0] + cn[2][0]) / 2, (cn[1][1] + cn[2][1]) / 2);
      bg.addColorStop(0, 'rgba(255,248,224,0.2)'); bg.addColorStop(0.6, 'rgba(255,248,224,0.07)'); bg.addColorStop(1, 'rgba(255,248,224,0)');
      cx.fillStyle = bg;
      cx.beginPath(); cx.moveTo(cn[0][0], cn[0][1]); cx.lineTo(cn[1][0], cn[1][1]); cx.lineTo(cn[2][0], cn[2][1]); cx.closePath(); cx.fill();
      cx.restore();
      // (along the middle of the beam to the first stone)
      var ca = Math.cos(cn[3]), sa = Math.sin(cn[3]);
      for (var d = 20; d < Sim.F.BEAM_LEN; d += 6) {
        var px = cn[0][0] + ca * d, py = cn[0][1] + sa * d;
        if (Sim.ext.fly.rockAt(L, px, py)) { pool(px, py, 10 + d * 0.11, [255, 246, 220], (0.24 * (1 - d / Sim.F.BEAM_LEN) + 0.06) * la); break; }
      }
    }
    // the searchlights on the ground: their beams up into the sky (brighter on the Apache when one has it)
    for (i = 0; i < s.enemies.length; i++) {
      var le = s.enemies[i];
      if (le.k !== 'light' || !le.alive || le.beam == null || le.x < x0 - 300 || le.x > x1 + 300) continue;
      var lx0 = le.x + Math.cos(le.beam) * 6, ly0 = le.y - 13 + Math.sin(le.beam) * 6, LL = Sim.F.LIGHT_LEN, hw2 = Sim.F.LIGHT_HALF, trk = le.st === 'track';
      cx.save(); cx.globalCompositeOperation = 'lighter';
      var lg = cx.createLinearGradient(lx0, ly0, lx0 + Math.cos(le.beam) * LL, ly0 + Math.sin(le.beam) * LL);
      lg.addColorStop(0, 'rgba(255,250,226,' + (trk ? 0.32 : 0.2) + ')'); lg.addColorStop(0.7, 'rgba(255,250,226,' + (trk ? 0.1 : 0.06) + ')'); lg.addColorStop(1, 'rgba(255,250,226,0)');
      cx.fillStyle = lg;
      cx.beginPath(); cx.moveTo(lx0, ly0);
      cx.lineTo(lx0 + Math.cos(le.beam - hw2) * LL, ly0 + Math.sin(le.beam - hw2) * LL);
      cx.lineTo(lx0 + Math.cos(le.beam + hw2) * LL, ly0 + Math.sin(le.beam + hw2) * LL);
      cx.closePath(); cx.fill();
      cx.restore();
      glow(lx0, ly0, 10, [255, 246, 220], 0.5);
    }
    // a missile man locking on: the line from his launcher to the Apache, flashing with the beat
    if (s.locking && h) for (i = 0; i < s.enemies.length; i++) {
      var se = s.enemies[i];
      if (se.id === s.locking && se.alive) {
        var lx0 = se.x, ly0 = se.st === 'lock' ? se.y - 14 : se.y - 29;
        if (se.k === 'launcher') { var nz = Sim.lnNose(se); lx0 = nz.x; ly0 = nz.y; }
        if (beatSolid || beatT < 6) K.dotted(lx0, ly0, h.x, h.y, 5, beatSolid ? ((tick >> 1) % 2 ? '#ff4030' : '#ffd040') : '#ff4030');
        else if ((tick >> 2) % 2) K.dotted(lx0, ly0, h.x, h.y, 9, '#a03028');
      }
    }
    trails(s, paused);
    walker(s);
    drawHeli(s, paused);
    // the Apache in a searchlight's beam: lit up
    if (s.spotT > 0 && h && h.st === 'fly' && !s.p.dead) glow(h.x, h.y - 2, 40, [255, 248, 226], 0.18 + 0.04 * Math.sin(tick * 0.3));
    // the snipers' lasers
    for (i = 0; i < s.enemies.length; i++) { var sn = s.enemies[i]; if (sn.k === 'sniper' && sn.alive && sn.st === 'aim' && sn.lx != null) laser(sn); }
    // mortar shells going up, and where each will burst; the Castle Gun's flak on its way
    for (i = 0; i < s.shells.length; i++) {
      var sh = s.shells[i];
      if (sh.gone) continue;
      if (sh.kind === 'flak') {
        if (sh.t < 0) continue;
        var ff2 = sh.t / sh.fuse, rr3 = Sim.BG.CG_FLAK_R * (1.5 - 0.5 * ff2);
        if (sh.t < sh.fuse - 18) fire(sh.x, sh.y, 1.6);
        cx.save(); cx.globalCompositeOperation = 'lighter'; cx.fillStyle = 'rgba(255,70,40,' + (0.06 + 0.12 * ff2).toFixed(3) + ')'; cx.beginPath(); cx.arc(sh.tx, sh.ty, rr3, 0, Math.PI * 2); cx.fill(); cx.restore();
        if ((tick >> (ff2 > 0.6 ? 1 : 2)) % 2 === 0 || ff2 > 0.85) {
          cx.fillStyle = ff2 > 0.6 ? '#ff4030' : '#ffd040';
          for (var a2 = 0; a2 < 32; a2 += 2) { var aa2 = a2 / 32 * Math.PI * 2 - tick * 0.03; cx.fillRect(Math.round(sh.tx + Math.cos(aa2) * rr3) - 1, Math.round(sh.ty + Math.sin(aa2) * rr3) - 1, 2, 2); }
        }
        continue;
      }
      if (sh.t < 30) { var sy = sh.y - sh.t * sh.t * 0.6, sx = sh.x + (sh.tx - sh.x) * sh.t / 160; cx.fillStyle = '#2a2a24'; cx.fillRect(Math.round(sx) - 1, Math.round(sy) - 2, 2, 4); if (!paused) trail.push({ x: sx, y: sy + 4, t: 0, life: 12, c: 0 }); }
      var ft = sh.t / Sim.F.MORTAR_FUSE, rr2 = Sim.F.MORTAR_R * (1.7 - 0.7 * ft), per = ft > 0.7 ? 2 : (ft > 0.4 ? 3 : 4);
      // (a ring of dashes closing in, faster and redder as it comes; the middle marked)
      cx.save(); cx.globalCompositeOperation = 'lighter';
      cx.fillStyle = 'rgba(255,60,40,' + (0.05 + 0.1 * ft).toFixed(3) + ')'; cx.beginPath(); cx.arc(sh.tx, sh.ty, rr2, 0, Math.PI * 2); cx.fill();
      cx.restore();
      if ((tick >> per) % 2 === 0 || ft > 0.9) {
        cx.fillStyle = ft > 0.75 ? '#ff4030' : '#ffd040';
        for (var an = 0; an < 40; an++) { if (an % 2) continue; var aa = an / 40 * Math.PI * 2 + tick * 0.02; cx.fillRect(Math.round(sh.tx + Math.cos(aa) * rr2) - 1, Math.round(sh.ty + Math.sin(aa) * rr2) - 1, 2, 2); }
        cx.fillRect(Math.round(sh.tx) - 3, Math.round(sh.ty), 7, 1); cx.fillRect(Math.round(sh.tx), Math.round(sh.ty) - 3, 1, 7);
      }
    }
    if (s.intro && s.intro.st === 'wait' && h) {
      // GET IN, over the Apache, and a little arrow down at it
      if ((tick >> 4) % 2 === 0) K.text('b_org', T('GET IN'), h.x + 10, h.y - 46, 'c');
      var ab = Math.round(h.y - 30 + ((tick >> 3) % 2)), axx = Math.round(h.x + 10);
      cx.fillStyle = '#ffc22e'; for (var ar = 0; ar < 4; ar++) cx.fillRect(axx - 3 + ar, ab + ar, 7 - ar * 2, 1);
    }
    // rockets, missiles, flares
    for (i = 0; i < s.rockets.length; i++) {
      var r = s.rockets[i];
      if (r.gone) continue;
      tsprRot('rocket', r.x, r.y, Math.atan2(r.vy, r.vx));
      fire(r.x - r.dx * 5, r.y - r.dy * 5, 2);
      if (!paused) lay(r, r.x - r.dx * 6, r.y - r.dy * 6, 18, 0);
    }
    for (i = 0; i < s.missiles.length; i++) {
      var ms = s.missiles[i];
      if (ms.gone) continue;
      var mca = Math.cos(ms.ang), msa = Math.sin(ms.ang);
      if (ms.kind === 'big' || ms.kind === 'dud' || ms.kind === 'icbm') {
        // (the launcher's: as long as the Apache, the nose where it is; a long flame and a thick trail)
        var ml = Sim.BG.LN_LEN, tlx = ms.x - mca * ml, tly = ms.y - msa * ml;
        missileBody(tlx, tly, ms.ang, ml, night(s), false, false);
        fire(tlx - mca * 4, tly - msa * 4, ms.kind === 'dud' ? 2.2 + (tick % 3) : (ms.kind === 'icbm' ? 5.5 + (tick % 2) : 4.4));
        if (!paused) {
          lay(ms, tlx - mca * 8, tly - msa * 8, 70, 1);
          if (tick % 2 === 0) K.part('smoke', tlx - mca * 10, tly - msa * 10, { life: 44, vx: -mca * 26, vy: -msa * 26 - 8 });
          if (ms.kind === 'dud' && tick % 2 === 0) K.part('ember', tlx, tly, { life: 14, vx: (Math.random() - 0.5) * 90, vy: (Math.random() - 0.5) * 90 });
        }
        continue;
      }
      tsprRot(ms.kind === 'rpg' ? 'rocket' : 'missile', ms.x, ms.y, ms.ang);
      fire(ms.x - mca * 6, ms.y - msa * 6, 3);
      if (!paused) lay(ms, ms.x - mca * 7, ms.y - msa * 7, 34, 1);
    }
    for (i = 0; i < s.flares.length; i++) {
      var fl = s.flares[i];
      if (fl.gone) continue;
      var fa = 1 - fl.t / Sim.F.FLARE_LIFE;
      cx.save(); cx.globalCompositeOperation = 'lighter';
      var fg = cx.createRadialGradient(fl.x, fl.y, 0, fl.x, fl.y, 9);
      fg.addColorStop(0, 'rgba(255,240,200,' + (0.9 * fa).toFixed(3) + ')'); fg.addColorStop(0.4, 'rgba(255,150,60,' + (0.45 * fa).toFixed(3) + ')'); fg.addColorStop(1, 'rgba(255,120,40,0)');
      cx.fillStyle = fg; cx.fillRect(fl.x - 9, fl.y - 9, 18, 18);
      cx.restore();
      cx.fillStyle = '#fffbe8'; cx.fillRect(Math.round(fl.x) - 1, Math.round(fl.y) - 1, 2, 2);
      if (!paused) lay(fl, fl.x, fl.y, 26, 2);
    }
    // on the aim stick: the gun's line, out from the muzzle the way it points
    if (h && h.aiming && h.st === 'fly' && !s.p.dead) {
      var mz = Sim.ext.fly.muzzle(h), ca2 = Math.cos(h.gunA), sa2 = Math.sin(h.gunA);
      for (var gd = 16; gd < 70; gd += 6) { cx.fillStyle = gd < 40 ? 'rgba(255,214,110,0.75)' : 'rgba(255,214,110,0.4)'; cx.fillRect(Math.round(mz.x + ca2 * gd), Math.round(mz.y + sa2 * gd), 1, 1); }
      if (!h.target) {
        var rx2 = Math.round(mz.x + ca2 * 96), ry2 = Math.round(mz.y + sa2 * 96);
        cx.fillStyle = 'rgba(255,214,110,0.7)';
        cx.fillRect(rx2 - 4, ry2, 3, 1); cx.fillRect(rx2 + 2, ry2, 3, 1); cx.fillRect(rx2, ry2 - 4, 1, 3); cx.fillRect(rx2, ry2 + 2, 1, 3);
      }
    }
    // the rocket pod's lock: four corners closing in on what it has found (a beep each step), then held, red, with a
    // diamond: locked (the gun's own aim is its dotted line)
    if (h && h.rlock && h.st === 'fly' && !s.p.dead) {
      var lk = null;
      for (i = 0; i < s.enemies.length; i++) if (s.enemies[i].id === h.rlock) lk = s.enemies[i];
      if (lk && lk.alive) {
        var Fz = Sim.F, f = Math.min(1, h.rlockT / Fz.RLOCK_T), locked = h.rlockT > Fz.RLOCK_T;
        var lx = Math.round(lk.x), lyy = Math.round(lk.y - lk.h * 0.5), rr = Math.round(34 - 18 * f * f * (3 - 2 * f)), k2 = 7;
        var col = locked ? ((tick >> 3) % 4 ? '#ff3a2a' : '#ffb0a0') : (rlockBeat < 3 ? '#fff6c0' : '#ffd040');
        cx.fillStyle = 'rgba(8,10,24,0.55)';                    // (a dark edge under it, so it reads on anything)
        corners(lx + 1, lyy + 1, rr, k2);
        cx.fillStyle = col;
        corners(lx, lyy, rr, k2);
        if (locked) {
          for (var dq = 0; dq <= 5; dq++) { cx.fillRect(lx - 5 + dq, lyy - dq, 2, 1); cx.fillRect(lx + 4 - dq, lyy - dq, 2, 1); cx.fillRect(lx - 5 + dq, lyy + dq, 2, 1); cx.fillRect(lx + 4 - dq, lyy + dq, 2, 1); }
          if ((tick >> 3) % 2) K.text('s_org', T('LOCK'), lx, lyy - rr - 9, 'c');
        }
      }
    }
    if (!paused) rlockBeat++;
    // the end: where to put it down in the courtyard
    var E = s.ending, LQ = L.fly.landing;
    if (E && E.st === 'dawn' && LQ) {
      var pyy = LQ.y, pxx = LQ.pad;
      cx.fillStyle = (tick >> 3) % 2 ? '#ffd040' : '#fff6c0';
      for (var pa = 0; pa < 28; pa += 2) { var aa3 = pa / 28 * Math.PI * 2; cx.fillRect(Math.round(pxx + Math.cos(aa3) * 26), Math.round(pyy - 2 + Math.sin(aa3) * 6), 2, 1); }
      cx.fillRect(pxx - 5, pyy - 6, 2, 6); cx.fillRect(pxx + 3, pyy - 6, 2, 6); cx.fillRect(pxx - 3, pyy - 4, 6, 2);
      if ((tick >> 4) % 2 === 0) K.text('b_org', T('LAND'), pxx, pyy - 52, 'c');
      for (var ar2 = 0; ar2 < 4; ar2++) cx.fillRect(pxx - 3 + ar2, pyy - 38 + ar2 + ((tick >> 3) % 2), 7 - ar2 * 2, 1);
    }
    // the chin gun's rounds bursting
    for (i = flashes.length - 1; i >= 0; i--) {
      var fq = flashes[i];
      if (fq.t < 3) fire(fq.x, fq.y, 2.2 - fq.t * 0.5);
      if (!paused && ++fq.t > 3) flashes.splice(i, 1);
    }
  }
  // Yazeed on foot, in the opening: standing in the street, walking to the Apache, climbing in
  function walker(s) {
    var y = s.yaz;
    if (!y || y.st === 'gone') return;
    K.src(tint(s, { x: y.x, y: y.y, h: 34 }));
    var walk = (Math.floor(y.walkD / 8) % 2) ? 'yazeed_pass_side_fwd' : 'yazeed_run_side_fwd';
    if (y.st === 'board') K.spr('yazeed_jump_side_up', y.x, y.y, false, y.a);
    else K.spr(y.st === 'walk' ? walk : 'yazeed_stand_side_fwd', y.x, y.y, y.face < 0);
    K.src(null);
  }
  // light about a lamp (added to what is there), and a flattened pool of it on what it falls on
  function glow(x, y, r, c, a) {
    cx.save(); cx.globalCompositeOperation = 'lighter';
    var g = cx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, rgba(c, a)); g.addColorStop(0.35, rgba(c, a * 0.45)); g.addColorStop(1, rgba(c, 0));
    cx.fillStyle = g; cx.fillRect(x - r, y - r, r * 2, r * 2);
    cx.restore();
  }
  function pool(x, y, r, c, a) {
    cx.save(); cx.globalCompositeOperation = 'lighter';
    cx.translate(x, y); cx.scale(1, 0.32);
    var g = cx.createRadialGradient(0, 0, 0, 0, 0, r);
    g.addColorStop(0, rgba(c, a)); g.addColorStop(0.6, rgba(c, a * 0.5)); g.addColorStop(1, rgba(c, 0));
    cx.fillStyle = g; cx.fillRect(-r, -r, r * 2, r * 2);
    cx.restore();
  }

  // a target's four corners, two pixels thick (r: from the middle to the corner; k: each arm's length)
  function corners(x, y, r, k) {
    cx.fillRect(x - r, y - r, k, 2); cx.fillRect(x - r, y - r, 2, k); cx.fillRect(x + r - k + 1, y - r, k, 2); cx.fillRect(x + r - 1, y - r, 2, k);
    cx.fillRect(x - r, y + r - 1, k, 2); cx.fillRect(x - r, y + r - k + 1, 2, k); cx.fillRect(x + r - k + 1, y + r - 1, k, 2); cx.fillRect(x + r - 1, y + r - k + 1, 2, k);
  }
  function fire(x, y, r) {
    cx.save(); cx.globalCompositeOperation = 'lighter';
    var g = cx.createRadialGradient(x, y, 0, x, y, r * 2.5);
    g.addColorStop(0, 'rgba(255,240,180,0.95)'); g.addColorStop(0.5, 'rgba(255,140,40,0.5)'); g.addColorStop(1, 'rgba(255,100,20,0)');
    cx.fillStyle = g; cx.fillRect(x - r * 2.5, y - r * 2.5, r * 5, r * 5);
    cx.restore();
  }
  // smoke behind what flies: a puff every few pixels along its way since the last frame (o remembers where that was)
  var laid = typeof WeakMap !== 'undefined' ? new WeakMap() : null;       // (kept beside the game's things, not on them)
  function lay(o, x, y, life, c) {
    if (!laid) { trail.push({ x: x, y: y, t: 0, life: life, c: c }); return; }
    var q = laid.get(o);
    if (!q) { q = { x: x, y: y }; laid.set(o, q); }
    var dx = x - q.x, dy = y - q.y, d = Math.sqrt(dx * dx + dy * dy), n = Math.min(8, Math.floor(d / 3));
    for (var k = 1; k <= n; k++) trail.push({ x: q.x + dx * k / n, y: q.y + dy * k / n, t: k - n, life: life, c: c });
    if (n) { q.x = x; q.y = y; }
  }
  function trails(s, paused) {
    for (var i = trail.length - 1; i >= 0; i--) {
      var t = trail[i];
      if (!paused) { t.t++; t.y -= 0.15; }
      if (t.t > t.life) { trail.splice(i, 1); continue; }
      if (t.t < 0) continue;
      var u = t.t / t.life, col = t.c === 2 ? [255, 244, 230] : (t.c === 1 ? [226, 226, 222] : [196, 192, 186]);
      var a = (t.c === 3 ? 0.3 : 0.55) * (1 - u) * (u < 0.1 ? u * 10 : 1), sz = t.c === 3 ? 1 + (u > 0.5 ? 1 : 0) : 1 + Math.floor(u * (t.c === 0 ? 3 : 4));
      cx.fillStyle = rgba(col, a);
      cx.fillRect(Math.round(t.x - sz / 2), Math.round(t.y - sz / 2), sz, sz);
    }
    if (trail.length > 700) trail.splice(0, trail.length - 700);
  }
  // the Apache: its body tilted with the nose, the rotor over it, the tail rotor, the gun under its chin, its lamps
  function drawHeli(s, paused) {
    var h = s.heli, p = s.p, R = FS.rig, Fz = Sim.F;
    if (!h) return;
    if (h.st === 'wreck') {
      if (p.dead < 40 || (p.dead >> 1) % 2) tspr('apache_burnt', h.x, h.y + 4, h.face < 0);
      if (!paused && tick % 3 === 0) K.part('smoke', h.x + (Math.random() - 0.5) * 30, h.y - 4, { life: 40, vx: 6, vy: -40 });
      return;
    }
    if (h.st === 'down') {
      tsprRot('apache_burnt', h.x, h.y, h.ang, h.face < 0 ? -1 : 1);
      if (!paused && tick % 2 === 0) K.part('smoke', h.x - h.face * 10, h.y - 4, { life: 30, vx: -h.vx * 0.3, vy: -30 });
      return;
    }
    if (p.inv > 0 && (p.inv >> 1) % 2 && h.st === 'fly') return;          // (just come back in: it blinks)
    var HS = NG && night(s) ? NG.heli : IMT;
    SH = HS;
    var fi = clamp(Math.round((h.tilt + 0.24) / 0.08), 0, 6), turn = 1;          // (second cut: it never turns round)
    var sxs = h.face, c = Math.cos(h.tilt), sn = Math.sin(h.tilt);
    function at(o) { var lx = o[0] * c - o[1] * sn, ly = o[0] * sn + o[1] * c; return [h.x + lx * sxs, h.y + ly]; }
    // the gun, under the chin, behind the body's outline
    var gp = at(R.gun), ga = h.face > 0 ? h.gunA : Math.PI - h.gunA;
    if (turn > 0.6) tsprRot('apache_gun', gp[0], gp[1], ga);
    cx.save(); cx.translate(Math.round(h.x), Math.round(h.y)); cx.scale(sxs, 1);
    var f = FS.frames['apache_t' + fi + (p.hurtT < 3 ? '!' : '')];
    cx.drawImage(HS, f[0], f[1], f[2], f[3], -f[4], -f[5], f[2], f[3]);
    cx.restore();
    // the rotor, a blur over the hub, the tail rotor turning
    var hub = at(R.hub), tl = at(R.tail);
    tsprRot('apache_rotor' + (tick % 4), hub[0], hub[1], h.tilt * h.face, Math.max(0.6, turn));
    tspr('apache_tail' + ((tick >> 0) % 4), tl[0], tl[1]);
    // its lamps: red at the tail, green at the nose, the white beacon, and the searchlight's lamp at night
    var red = at(R.red), grn = at(R.green), bea = at(R.beacon);
    if ((tick % 50) < 25) { cx.fillStyle = '#ff2a1a'; cx.fillRect(Math.round(red[0]), Math.round(red[1]), 1, 1); }
    if ((tick % 50) >= 25) { cx.fillStyle = '#4aff6a'; cx.fillRect(Math.round(grn[0]), Math.round(grn[1]), 1, 1); }
    if (tick % 70 < 3) { cx.fillStyle = '#ffffff'; cx.fillRect(Math.round(bea[0]), Math.round(bea[1]), 2, 1); }
    var hr = hour(s);
    if (hr.d > 0.4 && turn > 0.6) { var li = at(R.light); fire(li[0], li[1], 1.3); }
    // (the exhaust's heat, faintly)
    if (!paused && tick % 4 === 0) { var ex = at(R.exhaust); trail.push({ x: ex[0] - h.face * 2, y: ex[1], t: 0, life: 14, c: 3 }); }
    SH = null;
  }

  // ------------------------------------------------------------------ what happens, as it looks
  function pre(e, s, k) {
    if (!on(s)) return false;
    K = k; tick = K.tick();
    var h = s.heli;
    switch (e.t) {
      case 'shot':
        if (e.w !== 'chin') return false;
        K.part('muzzle', e.x, e.y, { life: 3, flip: false, name: 'fx_muzzle', ang: Math.atan2(e.dy, e.dx) });
        if (Math.random() < 0.5) K.part('casing', e.x - e.face * 4, e.y, { life: 30, vx: -e.face * (20 + Math.random() * 30) + (h ? h.vx * 0.6 : 0), vy: -40 - Math.random() * 40, g: 620 });
        return true;
      case 'go':
        if (e.dir && e.dir !== 'right') goUpT = 200;
        return false;
      case 'rocket':
        K.part('puff', e.x - e.face * 6, e.y, { life: 9, flip: e.face < 0 });
        return true;
      case 'flare':
        for (var i2 = 0; i2 < 4; i2++) K.part('spark', e.x - (h ? h.face : 1) * 10, e.y + 4, { life: 5, name: 'fx_spark2' });
        return true;
      case 'sam_boom':
        if (e.shot) K.pop(e.x, e.y - 10, String(e.pts));
        return true;
      case 'scatter':
        K.pop(e.x, e.y - 44, String(e.pts));
        K.part('alert', e.x, e.y - 46, { life: 22 });
        return true;
      case 'qanya':
        K.part('alert', e.x, e.y - 12, { life: 30 });
        return true;
      case 'startle':
        K.part('alert', e.x, e.y - 44, { life: 60 });
        return true;
      case 'emerge':
        K.part('puff', e.x - 6, e.y - 2, { life: 9 }); K.part('puff', e.x + 6, e.y - 2, { life: 9, flip: true });
        return true;
      case 'scrape':
        for (var j = 0; j < 3; j++) K.part('spark', e.x, e.y, { life: 5, name: 'fx_spark2' });
        K.shake(3);
        return true;
      case 'plate_lost':
        if (h) { K.embers(h.x, h.y, 6, 240); K.part('spark', h.x, h.y, { life: 5, name: 'fx_spark2' }); }
        return false;
      case 'heli_down':
        K.shake(8);
        return true;
      case 'die':
        if (e.k === 'aa') K.part('piece', e.x - 10, e.y - 14, { life: 70, vx: -50 - Math.random() * 40, vy: -240, g: 700, spin: -0.28, name: 'rifle_angry_flung', oy: 18 });
        return false;
      case 'lock_on':
        beatT = 99; beatSolid = false;
        return true;
      case 'rlock':
        rlockBeat = 0;
        return true;
      case 'hedp':
        if (flashes.length < 24) flashes.push({ x: e.x, y: e.y, t: 0 });
        K.part('puff', e.x, e.y - 1, { life: 8 + (Math.random() * 4 | 0), flip: Math.random() < 0.5 });
        if (Math.random() < 0.5) K.part('spark', e.x, e.y, { life: 4, name: 'fx_spark2' });
        return true;
      case 'lock':
        beatT = 0; beatSolid = !!e.solid;
        return true;
      case 'lock_off': case 'sam_launch':
        beatSolid = false; beatT = 99;
        if (e.t === 'sam_launch') { K.part('puff', e.x, e.y, { life: 10 }); K.part('puff', e.x - 6, e.y + 2, { life: 12, flip: true }); }
        return true;
      case 'tell':
        if (e.k === 'aa') { K.part('alert', e.x, e.y - 4, { life: 26 }); return true; }
        if (e.k === 'rpg' || e.k === 'truck') return true;
        return false;
      case 'rpg_fire':
        K.part('puff', e.x, e.y, { life: 10 }); K.part('puff', e.x - e.face * 12, e.y + 1, { life: 14, flip: true }); K.part('smoke', e.x - e.face * 14, e.y, { life: 30, vx: -e.face * 30, vy: -20 });
        return true;
      case 'mortar_fire':
        K.part('puff', e.x, e.y - 2, { life: 12 }); K.part('smoke', e.x, e.y - 6, { life: 34, vx: 0, vy: -40 });
        return true;
      case 'spotted':
        K.part('alert', e.x, e.y - 20, { life: 40 });
        return true;
      case 'boss_intro': case 'boss_phase': case 'boss_dying': case 'boss_dead':
        if (e.k !== 'cgun' && e.k !== 'launcher') return false;
        if (e.t === 'boss_intro') {
          Render.setBanner(T(e.k === 'cgun' ? 'THE CASTLE GUN' : 'THE LAUNCHER'), e.k === 'launcher' ? T('WRECK IT BEFORE IT LAUNCHES') : '', 200);
          if (e.k === 'cgun') { for (var tq = 0; tq < 6; tq++) K.part('piece', e.x - 20 + tq * 8, e.y - 30, { life: 50, vx: -40 + tq * 16, vy: -200 - Math.random() * 60, g: 600, spin: 0.2, name: 'fx_puff', oy: 0 }); }
          if (e.k === 'launcher') dawnCopies();          // (the dawn's pictures made now, ready for the end)
        } else if (e.t === 'boss_phase') { K.embers(e.x, e.y, 14, 300); K.shake(10); K.flash(2); if (e.k === 'cgun' && e.n === 2) K.part('piece', e.x - 14, e.y - 10, { life: 70, vx: -90, vy: -220, g: 700, spin: -0.3, name: 'aa_bar_burnt', oy: 0 }); }
        else if (e.t === 'boss_dying') { K.shake(12); K.flash(3); }
        else if (e.t === 'boss_dead') { K.embers(e.x, e.y, 26, 420); K.shake(26); K.flash(5); }
        return true;
      case 'roll':
        for (var rq = 0; rq < 5; rq++) K.part('puff', GATE.x0 + 4, GATE.bot - 4 - rq * 6, { life: 16 + rq * 2, flip: true });
        return true;
      case 'smoke':
        for (var sq = 0; sq < 6; sq++) K.part('puff', e.x - 60 + sq * 24, e.y - 8, { life: 14, flip: sq % 2 === 0 });
        return true;
      case 'overheat':
        for (var oq = 0; oq < 5; oq++) K.part('smoke', e.x + (Math.random() - 0.5) * 20, e.y - 4, { life: 36, vx: (Math.random() - 0.5) * 30, vy: -40 });
        return true;
      case 'recount':
        recountT = 90; recountAdd = e.add || 0;
        return true;
      case 'ignite':
        K.flash(2); K.shake(6);
        return true;
      case 'got_away':
        Render.setBanner(T('THE MISSILE GOT AWAY'), '', 170);
        return true;
      case 'countdown':
        return true;
      case 'oops':
        K.part('alert', e.x, e.y - 14, { life: 30 });
        return false;
      case 'big_launch':
        K.flash(2); K.shake(10);
        for (var bq = 0; bq < 10; bq++) K.part('smoke', e.x + (Math.random() - 0.5) * 40, e.y + 40 + Math.random() * 30, { life: 50 + bq * 3, vx: (Math.random() - 0.5) * 60, vy: -20 - Math.random() * 30 });
        return true;
      case 'cookoff':
        K.embers(e.x, e.y, 12, 260);
        return true;
      case 'firework':
        K.embers(e.x, e.y, 34, 360); K.flash(1);
        return true;
      case 'land_man':
        K.part('puff', e.x, e.y, { life: 10 });
        return true;
      case 'flak':
        K.part('muzzle', e.x, e.y, { life: 4, flip: false, name: 'fx_muzzle', ang: Math.atan2(e.ty - e.y, e.tx - e.x) });
        return true;
      case 'touchdown':
        for (var dq = 0; dq < 6; dq++) K.part('puff', e.x - 30 + dq * 12, e.y + 18, { life: 14, flip: dq % 2 === 0 });
        return true;
    }
    return false;
  }

  // ------------------------------------------------------------------ the HUD: the flares, a lock-on, a missile on its way, the way up
  function hudAll(s, k, paused, at) {
    if (!on(s)) return;
    K = k; cx = K.ctx(); W = K.W(); tick = K.tick();
    var h = s.heli, mid = Math.floor(W / 2), F = Sim.F;
    if (!h) return;
    // the flares: ready, or coming back (a bar under the two tabs)
    // (under the armour and the score, where nothing else is)
    var label = T('FLARES'), fx = 30, fy = 27, bx = fx + K.textW('s_lav', label) + 3, bw = 24, ready = h.flareCd <= 0;
    K.text('s_lav', label, fx, fy);
    cx.fillStyle = '#10142c'; cx.fillRect(bx, fy, bw, 5);
    cx.fillStyle = ready ? ((tick >> 3) % 2 || paused ? '#ffc22e' : '#fff8c8') : '#6a7ab8';
    cx.fillRect(bx + 1, fy + 1, Math.max(0, Math.round((bw - 2) * (ready ? 1 : 1 - h.flareCd / F.FLARE_CD))), 3);
    // a missile man has it: FLARES!, flashed with each beat of his lock-on and held through the long tone (LOCK while the
    // flares are not ready); a missile on its way: MISSILE! (and FLARES! with it, if they are ready)
    var coming = false;
    for (var i = 0; i < s.missiles.length; i++) if (!s.missiles[i].gone && !s.missiles[i].decoy && s.missiles[i].kind !== 'rpg') coming = true;
    if (!paused) beatT++;
    if (s.status === 'play' && !s.p.dead) {
      if (s.locking) {
        var lit = beatSolid || beatT < 8;
        if (ready) { if (lit || (tick >> 3) % 2) K.text(lit ? 'b_red' : 'b_org', T('FLARES!'), mid, 76, 'c'); }
        else if (lit) K.text('b_org', T('LOCK'), mid, 76, 'c');
      } else if (coming) {
        if ((tick >> 2) % 2) K.text('b_red', T('MISSILE!'), mid, 76, 'c');
        else if (ready) K.text('b_org', T('FLARES!'), mid, 76, 'c');
      }
    }
    // the launcher's count (Khaled, 22 Oct: a timed boss): under the boss's name in the middle, red in its last ten
    // seconds; frozen and blinking while the crew argue over it, then what they put back on; IGNITION at nought
    var bs = s.boss;
    if (recountT > 0 && !paused) recountT--;
    if (bs && bs.kind === 'launcher' && bs.clock != null && bs.st !== 'dead' && s.status === 'play') {
      var secs = Math.ceil(bs.clock / 60), clk = Math.floor(secs / 60) + ':' + ('0' + secs % 60).slice(-2), cy0 = 40;
      if (bs.ign) { if ((tick >> 2) % 2) K.text('b_red', T('IGNITION!'), mid, cy0, 'c'); }
      else if (bs.argue) { if ((tick >> 3) % 2) K.text('b_org', T('LAUNCH IN {0}', [clk + ' ?']), mid, cy0, 'c'); }
      else if (secs > 10 || (tick >> 3) % 2 || paused) K.text(secs <= 10 ? 'b_red' : 'b_org', T('LAUNCH IN {0}', [clk]), mid, cy0, 'c');
      if (recountT > 0 && recountAdd) K.text('m_org', '+' + recountAdd, mid + Math.floor(K.textW('b_org', T('LAUNCH IN {0}', [clk])) / 2) + 10, cy0 + 2 - Math.floor((90 - recountT) / 9), 'c');
    }
    // the way on is up
    if (goUpT > 0) {
      goUpT -= paused ? 0 : 1;
      if ((goUpT >> 3) % 2) {
        var ax = W - 44, ay = 46;
        cx.fillStyle = '#10142c'; cx.fillRect(ax - 9, ay - 1, 19, 22);
        cx.fillStyle = '#ffc22e';
        for (var r = 0; r < 7; r++) cx.fillRect(ax - r, ay + 2 + r, 1 + r * 2, 1);
        cx.fillRect(ax - 2, ay + 9, 5, 9);
        K.text('s_org', T('GO'), ax + 1, ay + 22, 'c');
      }
    }
  }

  Render.bosses.fly = { back: back, scene: scene, man: man, post: post, pre: pre, hudAll: hudAll, tint: tint,
                        reset: function () { trail.length = 0; goUpT = 0; beatT = 99; beatSolid = false; flashes.length = 0; rlockBeat = 99; FLASH = {}; recountT = 0; captions = {}; } };
})();
