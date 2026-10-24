// ibb.js - Ibb (Mission 4, the Green Valleys): the Spokesman's loudspeakers on their poles, and his screens.
// It plugs into sim.js (Sim.ext.ibb) and does nothing in a level that has neither (L.speakers, L.screens).
//
// A speaker stands where a group stands (L.speakers: { x, g, zone, lines, hint }) and plays him. Three states, each one
// drawn on the men (render_ibb.js), never a hidden number:
//   live    the men of its group chant, fists up in step, a speech bubble over every head; they fight as hard as any,
//           but never give up while it plays (their last man does not surrender: G.noSurr)
//   hijack  Yazeed walks into the pole (as close as capturing a man): what comes out of it now is the announcer's
//           MISSION COMPLETE!, and every man of its group believes it, drops his gun and puts his hands up (the
//           surrender the game already has, set off by the speaker; nobody else of that group comes)
//   dead    shot in its horns (or blown up): silence, and its men fight like any others; the last of them may give up
//           again. (A shot at the men round it passes the pole: it goes when it is meant to, not to a stray round.)
// A screen (L.screens: { x, size: 'board' | 'tv', zone, lines }) shows him talking. Shot until it goes, it shows
// static, and the men near it flinch for a moment (an arm over the eyes: a moment to shoot). Screens and speakers that
// are playing say his lines, the nearest one on screen carrying the voice and the subtitle (render_ibb.js's talk(), by
// way of main.js), so walking past them puts a statement together.
var Sim = Sim || require('./sim.js');
(function () {
  'use strict';
  var _ = Sim._;
  var I = {
    SPK_HP: 6, BOARD_HP: 10, TV_HP: 2,
    POLE_H: 62,                         // the pole, ground to crossbar
    HORNS: [-22, 22, 71, 54],           // the horns on the crossbar, the target: x from, x to, height from, height to
    TOUCH: 12, TOUCH_Y: 30,             // walking into a pole (a man is captured at |dx| < 15: the pole is thinner)
    FLINCH_R: 84, FLINCH_T: 44,         // a screen going: the men this far from its edge flinch, for this long
    HINT_NEAR: 250,                     // the first speaker's hint: when Yazeed is this close to it
    PTS_HIJACK: 500, PTS_SPK: 200, PTS_BOARD: 300, PTS_TV: 100,
    CRATE_H: 14, TV_W: 46, TV_H: 30,    // a set on its crate: the crate's height, the set's body (feet included)
    BOARD_LIFT: 16                      // the billboard's picture: its bottom edge this far off the ground
  };

  function on(s) { return !!s.ibb; }

  function create(s, opts) {
    var L = s.L, zone = (opts && opts.zone) || 0;
    if (!L.speakers && !L.screens) { s.ibb = null; return; }
    s.ibb = { spk: [], scr: [], src: [], hinted: false, hijacks: 0 };
    (L.speakers || []).forEach(function (q) {
      if (q.zone < zone) return;
      var plat = q.plat ? _.platIndex(L, q.plat) : -1, y = Sim.surfaceY(L, plat, q.x);
      var o = { id: s.nextId++, kind: 'spk', x: q.x, y: y, g: q.g, hp: I.SPK_HP, st: 'live', t: 0, hurtT: 99, hint: !!q.hint,
                lines: q.lines || [], li: 0, on: true, mx: q.x, my: y - I.POLE_H - 4 };
      s.ibb.spk.push(o); s.ibb.src.push(o);
      var G = s.groups[q.g];
      if (G) G.noSurr = true;
    });
    (L.screens || []).forEach(function (q) {
      if (q.zone < zone) return;
      var plat = q.plat ? _.platIndex(L, q.plat) : -1, gy = Sim.surfaceY(L, plat, q.x), big = q.size === 'board';
      var o = { id: s.nextId++, kind: big ? 'board' : 'tv', big: big, x: q.x, y: gy, hp: big ? I.BOARD_HP : I.TV_HP, st: 'on', t: 0, hurtT: 99,
                lines: q.lines || [], li: 0, on: true };
      if (big) { o.x0 = q.x - 76; o.x1 = q.x + 76; o.y1 = gy - I.BOARD_LIFT + 4; o.y0 = o.y1 - 104; }
      else { o.x0 = q.x - I.TV_W / 2; o.x1 = q.x + I.TV_W / 2; o.y1 = gy - I.CRATE_H; o.y0 = o.y1 - I.TV_H; }
      o.mx = q.x; o.my = (o.y0 + o.y1) / 2;
      s.ibb.scr.push(o); s.ibb.src.push(o);
    });
  }

  function speakerOf(s, g) {
    for (var i = 0; i < s.ibb.spk.length; i++) if (s.ibb.spk[i].g === g) return s.ibb.spk[i];
    return null;
  }

  // ---------------------------------------------------------------- a speaker taken over
  function giveUp(e) {
    e.why = 'speaker'; e.lit = false; e.moving = 0;
    e.st = 'shock'; e.stT = 0;
  }
  function hijack(s, o) {
    o.st = 'hijack'; o.t = 0; o.on = false;
    s.score += I.PTS_HIJACK;
    s.ibb.hijacks++;
    var G = s.groups[o.g];
    if (G) {
      G.noSurr = false; G.hijacked = true; G.pending.length = 0;          // (nobody else of that group comes)
      if (!G.awake) { G.awake = true; G.awakeT = 0; }
    }
    for (var i = 0; i < s.enemies.length; i++) {
      var e = s.enemies[i];
      if (e.g === o.g && e.alive && e.hostile && e.st !== 'shock' && e.st !== 'surr') giveUp(e);
    }
    _.ev(s, { t: 'spk_hijack', x: o.x, y: o.y - I.POLE_H, src: o.id });
  }
  function hurtSpeaker(s, o, n, how) {
    if (o.st === 'dead') return;
    o.hp -= n; o.hurtT = 0;
    if (o.hp > 0) { _.ev(s, { t: 'spk_hit', x: o.x, y: o.y - I.POLE_H + 6, how: how }); return; }
    var was = o.st;
    o.st = 'dead'; o.t = 0; o.on = false;
    s.score += I.PTS_SPK;
    _.ev(s, { t: 'spk_dead', x: o.x, y: o.y - I.POLE_H, src: o.id, was: was });
    var G = s.groups[o.g];
    if (G && was === 'live') { G.noSurr = false; if (!G.done) _.lastMan(s, G); }       // (its last man may give up now)
  }

  // ---------------------------------------------------------------- a screen going
  function flinch(s, o) {
    for (var i = 0; i < s.enemies.length; i++) {
      var e = s.enemies[i];
      if (!e.alive || !e.hostile || e.ext || e.emerge > 0) continue;
      if (e.st === 'shock' || e.st === 'surr' || e.st === 'sneeze' || e.st === 'flinch' || e.st === 'stagger') continue;
      var dx = e.x < o.x0 ? o.x0 - e.x : (e.x > o.x1 ? e.x - o.x1 : 0);
      if (dx > I.FLINCH_R || Math.abs(e.y - o.y) > 90) continue;
      if (e.st === 'wind') e.lit = false;                 // (a bomber pinches out his fuse)
      e.st = 'flinch'; e.stT = 0; e.moving = 0; e.flinchT = I.FLINCH_T + Math.floor(s.rand() * 12);
      var G = s.groups[e.g];
      if (G && !G.awake) { G.awake = true; G.awakeT = 0; }
    }
  }
  function hurtScreen(s, o, n, how) {
    if (o.st !== 'on') return;
    o.hp -= n; o.hurtT = 0;
    if (o.hp > 0) { _.ev(s, { t: 'scr_hit', x: o.x, y: o.my, big: o.big, how: how }); return; }
    o.st = 'dead'; o.t = 0; o.on = false;
    s.score += o.big ? I.PTS_BOARD : I.PTS_TV;
    _.ev(s, { t: 'scr_dead', x: o.x, y: o.my, big: o.big, src: o.id });
    flinch(s, o);
  }

  // ---------------------------------------------------------------- hooks
  // his shots: a screen takes them anywhere on its face; a speaker in its horns (up, or up and along, from near it)
  function shot(s, b) {
    if (!on(s)) return false;
    var i, o;
    for (i = 0; i < s.ibb.scr.length; i++) {
      o = s.ibb.scr[i];
      if (o.st === 'on' && b.x >= o.x0 && b.x <= o.x1 && b.y >= o.y0 && b.y <= o.y1) { hurtScreen(s, o, 1, 'shot'); return true; }
    }
    for (i = 0; i < s.ibb.spk.length; i++) {
      o = s.ibb.spk[i];
      if (o.st === 'dead') continue;
      if (b.x >= o.x + I.HORNS[0] && b.x <= o.x + I.HORNS[1] && b.y >= o.y - I.HORNS[2] && b.y <= o.y - I.HORNS[3]) { hurtSpeaker(s, o, 1, 'shot'); return true; }
    }
    return false;
  }
  function blast(s, x, y, r) {
    if (!on(s)) return;
    var i, o;
    for (i = 0; i < s.ibb.scr.length; i++) {
      o = s.ibb.scr[i];
      if (o.st !== 'on') continue;
      var nx = Math.max(o.x0, Math.min(x, o.x1)), ny = Math.max(o.y0, Math.min(y, o.y1));
      if ((nx - x) * (nx - x) + (ny - y) * (ny - y) < (r + 4) * (r + 4)) hurtScreen(s, o, 3, 'blast');
    }
    for (i = 0; i < s.ibb.spk.length; i++) {
      o = s.ibb.spk[i];
      if (o.st === 'dead') continue;
      var py = Math.max(o.y - I.POLE_H, Math.min(y, o.y));
      if ((o.x - x) * (o.x - x) + (py - y) * (py - y) < (r + 4) * (r + 4)) hurtSpeaker(s, o, 3, 'blast');
    }
  }
  function step(s) {
    if (!on(s)) return;
    var p = s.p, i, j, o;
    for (i = 0; i < s.ibb.spk.length; i++) {
      o = s.ibb.spk[i];
      o.t++; o.hurtT++;
      if (o.st === 'live') {
        if (!p.dead && s.status === 'play' && s.mode === 'foot' && Math.abs(p.x - o.x) < I.TOUCH && Math.abs(p.y - o.y) < I.TOUCH_Y) hijack(s, o);
        else if (o.hint && !s.ibb.hinted && !p.dead && Math.abs(p.x - o.x) < I.HINT_NEAR && Sim.onScreen(s, o.x, -30)) { s.ibb.hinted = true; _.ev(s, { t: 'hint', k: 'speaker' }); }
      }
    }
    for (i = 0; i < s.ibb.scr.length; i++) { o = s.ibb.scr[i]; o.t++; o.hurtT++; }
    // who is under which speaker (for the drawing), and a group whose speaker was taken over stays taken over
    for (j = 0; j < s.enemies.length; j++) {
      var e = s.enemies[j];
      if (!e.alive) continue;
      if (!e.deco) { e.deco = 'ibb'; o = speakerOf(s, e.g); e.spk = o ? o.id : 0; }
      if (e.hostile && e.st !== 'shock' && e.st !== 'surr' && s.groups[e.g] && s.groups[e.g].hijacked) giveUp(e);
    }
  }
  // (for the drawing: the speaker a man chants for, if it is playing)
  function chanting(s, e) {
    if (!on(s) || !e.spk || !e.alive || !e.hostile) return null;
    for (var i = 0; i < s.ibb.spk.length; i++) if (s.ibb.spk[i].id === e.spk) return s.ibb.spk[i].st === 'live' ? s.ibb.spk[i] : null;
    return null;
  }

  Sim.ext.ibb = { create: create, step: step, shot: shot, blast: blast, chanting: chanting, I: I,
                  // (for tests)
                  hijack: hijack, hurtSpeaker: hurtSpeaker, hurtScreen: hurtScreen };
})();
if (typeof module !== 'undefined') module.exports = Sim;
