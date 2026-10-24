// audio.js - effects, the music and the voices. The effects, the voices, the menus' music and the jingles are fetched
// and decoded while the title is up; a mission's own music (its stage theme and its boss's) only when that mission is
// chosen (want()), and the music of the mission left behind is let go. Nothing sounds until the player has touched the
// page: a browser will not allow it sooner.
// Music: the stage theme and the battery's in play (startMusic), the home screen's theme and the map's march in the
// menus (menu), the mission jingles; one loop at a time, the menus' crossfading into each other.
// A mission's own spoken lines (Ibb's Spokesman, since 24 Oct) come the same way as its music: a file of their own,
// fetched with the mission (want()), laid out as the voices are and spoken through voice() like any other line.
var Sound = (function () {
  'use strict';
  var ctx = null, out = null, gMusic = null, gSfx = null, gVoice = null, man = null;
  var raw = {}, pre = {}, bufs = {}, shift = {}, last = {}, live = 0, loopSrc = null, seaSrc = null, jingleSrc = null, voiceNow = null;
  var muted = false, failed = false, flip = {}, names = [], all = [], wanted = {}, nDone = 0, how = '', off = null;
  var pendingMusic = null, pendingSea = false, endNode = null, counts = {}, loops = {}, track = 'strait';
  var said = {}, spoken = {};          // a mission's own lines by id (each knows its file), and those files
  var MIN_GAP = { shot_hmg: 0.04, shot_side: 0.045, eshot: 0.05, hit_body: 0.05, hit_sand: 0.07, clang: 0.05, step: 0.09, boom_s: 0.07, boom_m: 0.1, coin: 0.06, ricochet: 0.12, land: 0.08, tick: 0.05,
                 heavy_shot: 0.06, ram: 0.05, crash: 0.15, dive: 0.1, whistle: 0.08, lock: 0.1, smash_crate: 0.1, smash_bags: 0.1, car_land: 0.12, knife: 0.05, boom_big: 0.3,
                 gun30: 0.045, hedp: 0.09, beep: 0.04, rbeep: 0.03 };
  var TWIN = { shot_hmg: 'shot_hmg2', eshot: 'eshot2', step: 'step2', boom_s: 'boom_s2', heavy_shot: 'heavy_shot2', knife: 'knife2', ram: 'ram2', gun30: 'gun30b', hedp: 'hedp2' };
  // levels set by recording whole runs and measuring them: a spoken line has to sit clear of a heavy gun firing flat out
  var MUSIC = 0.62, MUSIC_UNDER = 0.38, SFX = 0.62, SFX_UNDER = 0.44, VOICE = 1.2, MASTER = 0.85;
  // the player's own levels, 0..1 each, on top of those (the meters in the options)
  var vol = { music: 1, sfx: 1, voice: 1 };
  var SILENCE = '/*SILENCE*/';

  // both the old callback form and the newer promise form, whichever this browser has
  function decodeWith(c, ab) {
    return new Promise(function (res, rej) {
      var done = false;
      function ok(b) { if (!done) { done = true; res(b); } }
      function no(e) { if (!done) { done = true; rej(e || new Error('could not decode')); } }
      try {
        var pr = c.decodeAudioData(ab, ok, no);
        if (pr && pr.then) pr.then(ok, no);
      } catch (e) { no(e); }
    });
  }
  // what is kept once decoded: everything fetched at the start, and the music of the mission chosen
  function keep(n) { return names.indexOf(n) >= 0 || !!wanted[n]; }
  function store(n, buf) {
    if (bufs[n] || !keep(n)) return;
    bufs[n] = buf;
    nDone++;
    if (n === 'sfx' || n === 'voices' || spoken[n]) {
      // a click near the start of the file says how far the decoder has shifted everything
      var d = buf.getChannelData(0), m = Math.min(d.length, Math.floor(buf.sampleRate * 0.3));
      shift[n] = 0;
      for (var i = 0; i < m; i++) { if (Math.abs(d[i]) > 0.15) { shift[n] = i / buf.sampleRate - man.mark; break; } }
    }
    if (ctx) flushPending();
  }
  function flushPending() {
    if (pendingMusic && bufs[man.music[pendingMusic.track].file] && (pendingMusic.menu || !pendingMusic.intro || bufs[man.music.start.file])) {
      var pm = pendingMusic; pendingMusic = null;
      // (a mission's music that arrives late comes in without the start call: that moment has gone)
      if (pm.menu) menu(pm.track); else startMusic(pm.intro && Date.now() - (pm.at || 0) < 1500, pm.track);
    }
    if (pendingSea && bufs.sfx) { pendingSea = false; sea(true); }
  }

  // what every screen needs comes first: the effects, the voices, the menus' music and the jingles. A mission's music
  // comes when the mission is chosen (want(); a mission whose music is still arriving starts it when it lands)
  function prefetch(manifest) {
    man = manifest;
    names = ['sfx', 'voices', man.music.start.file, man.music.complete.file];
    ['title', 'map'].forEach(function (k) { if (man.music[k]) names.push(man.music[k].file); });
    all = names.slice();
    for (var k in man.music) if (all.indexOf(man.music[k].file) < 0) all.push(man.music[k].file);
    for (var sk in man.speech || {}) {
      var sp = man.speech[sk];
      spoken[sp.file] = true;
      if (all.indexOf(sp.file) < 0) all.push(sp.file);
      for (var lid in sp.lines) { var ln = sp.lines[lid]; said[lid] = { at: ln.at, who: ln.who, text: ln.text, m: ln.m, f: sp.file }; }
    }
    var OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    try { if (OAC) off = new OAC(2, 2, 44100); } catch (e) { off = null; }
    how = off ? 'early' : 'on tap';
    names.forEach(fetchOne);
  }
  // the music a mission needs ('strait', 'battery', ...): fetched and decoded if it is not yet; the other missions'
  // music is let go (the menus', the jingles, the effects and the voices never are). 'speech:<mission>' asks for that
  // mission's own lines the same way.
  function want(tracks) {
    if (!man) return;
    var w = {};
    (tracks || []).forEach(function (k) {
      if (man.music[k]) w[man.music[k].file] = true;
      else if (k.indexOf('speech:') === 0 && man.speech && man.speech[k.slice(7)]) w[man.speech[k.slice(7)].file] = true;
    });
    for (var n in bufs) if (!w[n] && names.indexOf(n) < 0) { delete bufs[n]; nDone--; }
    for (var r in raw) if (!w[r] && names.indexOf(r) < 0) { delete raw[r]; delete pre[r]; }
    wanted = w;
    for (var f in w) if (!raw[f]) fetchOne(f);
  }
  function hasTrack(k) { return !!(man && man.music[k] && bufs[man.music[k].file]); }
  function fetchOne(n) {
    raw[n] = fetch('audio/' + n + '.mp3').then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.arrayBuffer(); });
    raw[n].catch(function () { failed = true; });
    // decode ahead of the first tap where the browser lets us; anything that fails here is tried again on the tap
    pre[n] = off ? raw[n].then(function (ab) { return decodeWith(off, ab.slice(0)); }).then(function (buf) { store(n, buf); }).catch(function () {}) : Promise.resolve();
    if (ctx) decodeLate(n);
  }
  function decodeLate(n) {
    pre[n].then(function () {
      if (bufs[n] || !keep(n) || !raw[n]) return null;
      return raw[n].then(function (ab) { return decodeWith(ctx, ab.slice(0)); }).then(function (buf) { store(n, buf); });
    }).catch(function () { failed = true; });
  }
  // call from inside a tap
  function unlock() {
    if (!man) return false;
    if (!ctx) {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) { failed = true; return false; }
      try { ctx = new AC(); } catch (e) { failed = true; return false; }
      out = ctx.createGain(); out.gain.value = muted ? 0 : MASTER;
      // a soft ceiling, so a long burst over the music does not crackle
      try {
        var lim = ctx.createDynamicsCompressor();
        lim.threshold.value = -8; lim.knee.value = 6; lim.ratio.value = 12; lim.attack.value = 0.002; lim.release.value = 0.12;
        out.connect(lim); lim.connect(ctx.destination); endNode = lim;
      } catch (e) { out.connect(ctx.destination); endNode = out; }
      gMusic = ctx.createGain(); gMusic.gain.value = MUSIC * vol.music; gMusic.connect(out);
      gSfx = ctx.createGain(); gSfx.gain.value = SFX * vol.sfx; gSfx.connect(out);
      gVoice = ctx.createGain(); gVoice.gain.value = VOICE * vol.voice; gVoice.connect(out);
      // on an iPhone, sound made this way obeys the ring switch unless the page says it is playback
      try { if (navigator.audioSession) navigator.audioSession.type = 'playback'; } catch (e) {}
      try {
        var ios = /iP(hone|ad|od)/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
        if (ios && !navigator.audioSession) {
          var a = document.createElement('audio');
          a.setAttribute('playsinline', ''); a.loop = true; a.src = SILENCE;
          var pr = a.play(); if (pr && pr.catch) pr.catch(function () {});
        }
      } catch (e) {}
      Object.keys(pre).forEach(function (n) { decodeLate(n); });
      flushPending();
    }
    resume();
    return true;
  }
  function resume() { if (ctx && ctx.state !== 'running' && ctx.resume) { try { var r = ctx.resume(); if (r && r.catch) r.catch(function () {}); } catch (e) {} } }

  function play(buf, at, dur, dest, o) {
    o = o || {};
    var s = ctx.createBufferSource(), g = ctx.createGain();
    s.buffer = buf;
    if (o.rate) s.playbackRate.value = o.rate;
    g.gain.value = o.gain == null ? 1 : o.gain;
    s.connect(g);
    if (o.pan && ctx.createStereoPanner) { var pn = ctx.createStereoPanner(); pn.pan.value = Math.max(-1, Math.min(1, o.pan)); g.connect(pn); pn.connect(dest); }
    else g.connect(dest);
    if (dur != null) s.start(o.when || 0, Math.max(0, at), dur);
    else s.start(o.when || 0, Math.max(0, at || 0));
    return { s: s, g: g };
  }
  function sfx(name, o) {
    if (!ctx || !bufs.sfx || ctx.state !== 'running') return;
    var now = ctx.currentTime, gap = MIN_GAP[name] || 0.02;
    if (last[name] != null && now - last[name] < gap) return;
    if (live > 26) return;
    last[name] = now;
    var id = name;
    if (TWIN[name]) { flip[name] = !flip[name]; if (flip[name]) id = TWIN[name]; }
    var a = man.sfx[id];
    if (!a) return;
    o = o || {};
    var opt = { gain: o.gain, pan: o.pan, rate: o.rate == null ? 0.97 + Math.random() * 0.06 : o.rate };
    var h = play(bufs.sfx, a[0] + shift.sfx, a[1] + 0.01, gSfx, opt);
    counts[name] = (counts[name] || 0) + 1;
    live++;
    h.s.onended = function () { live--; };
  }
  // one spoken line at a time; a new one cuts the old one off. Returns how long it runs, in seconds.
  function lineOf(id) { return man ? man.voices[id] || said[id] || null : null; }
  function voice(id, o) {
    var v = lineOf(id), f = v && v.f ? v.f : 'voices';
    if (!v) return 0;
    o = o || {};
    var len = v.at[1] / (o.rate || 1);
    if (!ctx || !bufs[f] || ctx.state !== 'running') return len;
    if (voiceNow && !o.over) {
      try { voiceNow.g.gain.setTargetAtTime(0, ctx.currentTime, 0.01); voiceNow.s.stop(ctx.currentTime + 0.06); } catch (e) {}
      voiceNow = null;
    }
    var h = play(bufs[f], v.at[0] + shift[f], v.at[1] + 0.01, gVoice, { gain: o.gain == null ? 1 : o.gain, rate: o.rate || 1, pan: o.pan });
    counts[id] = (counts[id] || 0) + 1;
    if (!o.over) {
      voiceNow = h;
      var t = ctx.currentTime;
      gMusic.gain.cancelScheduledValues(t);
      gMusic.gain.setTargetAtTime(MUSIC_UNDER * vol.music, t, 0.05);
      gMusic.gain.setTargetAtTime(MUSIC * vol.music, t + len, 0.18);
      gSfx.gain.cancelScheduledValues(t);
      gSfx.gain.setTargetAtTime(SFX_UNDER * vol.sfx, t, 0.04);
      gSfx.gain.setTargetAtTime(SFX * vol.sfx, t + len, 0.15);
    }
    return len;
  }

  function fadeOut(h, len) {
    try {
      var t = ctx.currentTime;
      h.g.gain.cancelScheduledValues(t);
      h.g.gain.setValueAtTime(h.g.gain.value, t);
      h.g.gain.linearRampToValueAtTime(0, t + len);
      h.s.stop(t + len + 0.03);
    } catch (e) {}
  }
  // keepMenu: leave the menus' music playing (the menu it is going to will take it from there)
  function stopMusic(fade, keepMenu) {
    if (!(keepMenu && pendingMusic && pendingMusic.menu)) pendingMusic = null;
    if (!ctx) return;
    if (loopSrc && !(keepMenu && loopSrc.menu)) { fadeOut(loopSrc, fade || 0.15); loopSrc = null; }
    if (jingleSrc) { fadeOut(jingleSrc, fade || 0.15); jingleSrc = null; }
  }
  // the home screen's theme ('title') or the map's march ('map'): whatever was playing fades as it comes in.
  // Asking for the one already playing changes nothing; before the first tap it is only remembered.
  function menu(which) {
    if (!man || !man.music[which]) return;
    track = which;
    if (!ctx) { pendingMusic = { menu: true, track: which }; return; }      // (it starts on the first tap)
    if (loopSrc && loopSrc.track === which) return;
    var b = bufs[man.music[which].file];
    if (!b) {
      // still arriving: quiet whatever is left of the game's music, and start this when it is ready
      if (loopSrc && !loopSrc.menu) { fadeOut(loopSrc, 0.3); loopSrc = null; }
      pendingMusic = { menu: true, track: which };
      return;
    }
    pendingMusic = null;
    var had = !!(loopSrc || jingleSrc);
    if (loopSrc) fadeOut(loopSrc, 0.8);
    if (jingleSrc) fadeOut(jingleSrc, 0.5);
    jingleSrc = null;
    var t = ctx.currentTime + 0.02, s = ctx.createBufferSource(), g = ctx.createGain();
    s.buffer = b; s.loop = true; s.loopStart = man.loopAt; s.loopEnd = man.loopAt + man.music[which].seconds;
    s.connect(g); g.connect(gMusic);
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(1, t + (had ? 0.9 : 0.4));
    s.start(t, man.lead);
    loopSrc = { s: s, g: g, track: which, menu: true };
  }
  // the mission-start call, then the stage theme coming in on its landing. which: 'strait' (default), 'battery', 'mocha',
  // 'roaster'
  function startMusic(intro, which, fadeIn) {
    which = which && man.music[which] ? which : 'strait';
    track = which;
    if (!ctx) return;
    var M = man.music, lb = bufs[M[which].file], jb = bufs[M.start.file];
    if (!lb && !wanted[M[which].file]) { wanted[M[which].file] = true; if (!raw[M[which].file]) fetchOne(M[which].file); }
    if (!lb || (intro && !jb)) { pendingMusic = { intro: intro, track: which, at: Date.now() }; return; }
    stopMusic(fadeIn ? 0.5 : 0.05);
    var t0 = ctx.currentTime + 0.06, when = t0;
    if (intro) { jingleSrc = play(jb, 0, null, gMusic, { when: t0, gain: 1.2 }); when = t0 + M.start.landing; }
    var s = ctx.createBufferSource(), g = ctx.createGain();
    s.buffer = lb; s.loop = true; s.loopStart = man.loopAt; s.loopEnd = man.loopAt + M[which].seconds;
    s.connect(g); g.connect(gMusic);
    if (fadeIn) { g.gain.setValueAtTime(0, when); g.gain.linearRampToValueAtTime(1, when + fadeIn); }
    s.start(when, man.lead);
    loopSrc = { s: s, g: g, track: which };
  }
  // engine, rotors: a stretch of the effects file that runs round until it is turned off. o: gain, rate.
  function loop(name, on, o) {
    if (!ctx) return;
    var Lp = loops[name];
    if (!on) {
      if (Lp) { try { Lp.g.gain.cancelScheduledValues(ctx.currentTime); Lp.g.gain.setTargetAtTime(0, ctx.currentTime, 0.06); Lp.s.stop(ctx.currentTime + 0.4); } catch (e) {} delete loops[name]; }
      return;
    }
    if (!bufs.sfx) return;
    o = o || {};
    if (!Lp) {
      var a = man.sfx[name];
      if (!a) return;
      var s = ctx.createBufferSource(), g = ctx.createGain(), st = a[0] + shift.sfx;
      s.buffer = bufs.sfx; s.loop = true; s.loopStart = st + 0.05; s.loopEnd = st + a[1] - 0.05;
      g.gain.value = 0; s.connect(g); g.connect(gSfx);
      if (o.rate) s.playbackRate.value = o.rate;
      s.start(0, st + 0.05);
      Lp = loops[name] = { s: s, g: g, gain: -1, rate: o.rate || 1 };
    }
    var t = ctx.currentTime;
    if (o.gain != null && Math.abs(o.gain - Lp.gain) > 0.01) { Lp.gain = o.gain; Lp.g.gain.setTargetAtTime(o.gain, t, 0.07); }
    if (o.rate != null && Math.abs(o.rate - Lp.rate) > 0.01) { Lp.rate = o.rate; Lp.s.playbackRate.setTargetAtTime(o.rate, t, 0.08); }
  }
  function loopsOff() { for (var k in loops) loop(k, false); }
  function jingle(which) {
    if (!ctx) return 0;
    var M = man.music[which], b = bufs[M.file];
    if (!b) return M.seconds;
    stopMusic(0.12);
    jingleSrc = play(b, 0, null, gMusic, { when: ctx.currentTime + 0.14, gain: 1.25 });
    return M.seconds;
  }
  function sea(on) {
    if (!ctx) return;
    if (seaSrc) { try { seaSrc.s.stop(); } catch (e) {} seaSrc = null; }
    if (!on) { pendingSea = false; return; }
    if (!bufs.sfx) { pendingSea = true; return; }
    var a = man.sfx.sea, s = ctx.createBufferSource(), g = ctx.createGain(), st = a[0] + shift.sfx;
    s.buffer = bufs.sfx; s.loop = true; s.loopStart = st + 0.05; s.loopEnd = st + a[1] - 0.05;
    g.gain.value = 0.45; s.connect(g); g.connect(gSfx);
    s.start(0, st + 0.05);
    seaSrc = { s: s, g: g };
  }
  function setMuted(b) { muted = b; if (out) out.gain.setTargetAtTime(b ? 0 : MASTER, ctx.currentTime, 0.02); }
  // the meters: kind is 'music', 'sfx' or 'voice', v 0..1. A voice that is ducking the rest finishes its ducking at the new level.
  function setVolume(kind, v) {
    if (!(kind in vol)) return;
    v = Math.max(0, Math.min(1, +v || 0));
    vol[kind] = v;
    if (!ctx) return;
    var g = kind === 'music' ? gMusic : (kind === 'sfx' ? gSfx : gVoice), base = kind === 'music' ? MUSIC : (kind === 'sfx' ? SFX : VOICE), t = ctx.currentTime;
    g.gain.cancelScheduledValues(t);
    g.gain.setTargetAtTime(base * v, t, 0.03);
  }
  function getVolume(kind) { return vol[kind]; }
  function pause(b) {
    if (!ctx) return;
    if (b) { try { if (ctx.suspend) { var r = ctx.suspend(); if (r && r.catch) r.catch(function () {}); } } catch (e) {} }
    else resume();
  }
  function isReady() { return names.length > 0 && names.every(function (n) { return !!bufs[n]; }); }
  function info() {
    return { state: ctx ? ctx.state : 'not started', rate: ctx ? ctx.sampleRate : 0, ready: isReady(), failed: failed, decoded: nDone + '/' + all.length, how: how,
             session: !!navigator.audioSession, latency: ctx && ctx.baseLatency != null ? Math.round(ctx.baseLatency * 1000) : null };
  }
  return { prefetch: prefetch, want: want, hasTrack: hasTrack, unlock: unlock, resume: resume, sfx: sfx, voice: voice, startMusic: startMusic, stopMusic: stopMusic, menu: menu, jingle: jingle, sea: sea, loop: loop, loopsOff: loopsOff,
           track: function () { return track; },
           // which loop is sounding now ('title', 'map', 'strait', 'battery', 'mocha', 'roaster'), or null
           playing: function () { return loopSrc ? loopSrc.track : null; },
           setMuted: setMuted, isMuted: function () { return muted; }, setVolume: setVolume, getVolume: getVolume, pause: pause, info: info, isReady: isReady, hasFailed: function () { return failed; },
           lineOf: lineOf,
           // for tests: the last node before the loudspeaker, and how often each sound has been asked for
           tap: function () { return { ctx: ctx, node: endNode, music: gMusic, sfx: gSfx, voice: gVoice }; }, counts: function () { return counts; } };
})();
