// Deterministic driver (from the trailer rig): virtual time for rAF/timers/now, a seeded Math.random, an offline audio
// context advanced in lockstep with the frames, and a log of what the game says and does, frame by frame.
(() => {
  const CFG = window.__CFG || {};
  const FPS = 60, DT = 1000 / FPS, SR = 48000, LENSEC = CFG.lensec || 150;
  let driving = false, vt = 0, vtBase = 0, dnBase = 0, frameIdx = 0, started = false;
  // seeded randomness, so the same inputs give the same pictures
  let seed = (CFG.seed || 12345) >>> 0;
  Math.random = function () { seed = (seed + 0x6D2B79F5) >>> 0; let t = seed; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  const pn = performance.now.bind(performance), dn = Date.now.bind(Date);
  performance.now = () => driving ? vt : pn();
  Date.now = () => driving ? Math.round(dnBase + (vt - vtBase)) : dn();
  const rRAF = window.requestAnimationFrame.bind(window);
  let rafQ = [], rafId = 1;
  window.requestAnimationFrame = (cb) => { if (!driving) return rRAF(cb); rafQ.push(cb); return rafId++; };
  const rST = window.setTimeout.bind(window), rCT = window.clearTimeout.bind(window), rSI = window.setInterval.bind(window), rCI = window.clearInterval.bind(window);
  const timers = new Map(); let tid = 1e7;
  window.setTimeout = (fn, ms, ...a) => { if (!driving || typeof fn !== 'function') return rST(fn, ms, ...a); const id = tid++; timers.set(id, { due: vt + (+ms || 0), fn, a, iv: 0 }); return id; };
  window.setInterval = (fn, ms, ...a) => { if (!driving || typeof fn !== 'function') return rSI(fn, ms, ...a); const id = tid++; timers.set(id, { due: vt + Math.max(1, +ms || 0), fn, a, iv: Math.max(1, +ms || 0) }); return id; };
  window.clearTimeout = (id) => { if (timers.has(id)) timers.delete(id); else rCT(id); };
  window.clearInterval = (id) => { if (timers.has(id)) timers.delete(id); else rCI(id); };
  function runTimers() {
    for (let guard = 0; guard < 1000; guard++) {
      let best = null, bid = null;
      for (const [id, t] of timers) if (t.due <= vt && (!best || t.due < best.due)) { best = t; bid = id; }
      if (!best) return;
      if (best.iv) best.due += best.iv; else timers.delete(bid);
      try { best.fn(...best.a); } catch (e) { console.error('timer', e); }
    }
  }
  if (!CFG.noAudio) {
    const OAC = window.OfflineAudioContext;
    window.AudioContext = function () {
      const c = new OAC(2, SR * LENSEC, SR);
      c.__suspend = c.suspend.bind(c); c.__resume = c.resume.bind(c);
      c.suspend = () => Promise.resolve(); c.resume = () => Promise.resolve();
      Object.defineProperty(c, 'state', { get: () => 'running' });
      Object.defineProperty(c, 'baseLatency', { get: () => 0 });
      window.__actx = c; return c;
    };
    window.webkitAudioContext = window.AudioContext;
  }
  const keyEv = (type, key) => window.dispatchEvent(new KeyboardEvent(type, { key, bubbles: true }));
  const held = new Set();
  const INTEREST = new Set(CFG.events || ['checkpoint', 'life_lost', 'boss_intro', 'boss_dead', 'boss_dying', 'chase', 'dawn', 'touchdown', 'clear', 'go', 'qanya', 'lost_count', 'recount', 'countdown', 'ignite', 'launch', 'big_launch', 'surrender', 'over', 'boss_phase', 'sam_launch', 'startle', 'heli_in', 'land', 'landed', 'board', 'liftoff', 'roll', 'truck_go', 'truck_dead', 'truck_away', 'crate_open', 'drone_up', 'drone_down', 'oops', 'firework', 'explode', 'panic', 'flak', 'respawn', 'road_end']);
  const D = window.__drv = {
    log: [], subs: [], hooks: [], frame: () => frameIdx, lastSub: null,
    down(k) { if (!held.has(k)) { held.add(k); keyEv('keydown', k); } },
    up(k) { if (held.has(k)) { held.delete(k); keyEv('keyup', k); } },
    tap(k) { keyEv('keydown', k); D.hooks.push({ at: frameIdx + 2, fn: () => keyEv('keyup', k), once: true }); },
    releaseAll() { for (const k of [...held]) D.up(k); },
    start() { vt = pn(); vtBase = vt; dnBase = dn(); driving = true; },
    driving: () => driving,
    note(kind, data) { D.log.push([kind, frameIdx, data]); },
    async step(n, capture, actions, until) {
      const out = [];
      const lo = document.getElementById('lo');
      for (let i = 0; i < n; i++) {
        const a = actions && actions[frameIdx];
        if (a) { try { (0, eval)(a); } catch (e) { console.error('action', frameIdx, e); D.log.push(['err', frameIdx, String(e)]); } }
        for (const h of D.hooks.slice()) { if (h.at == null || h.at <= frameIdx) { try { h.fn(); } catch (e) {} if (h.once) D.hooks.splice(D.hooks.indexOf(h), 1); } }
        vt += DT; runTimers();
        const q = rafQ; rafQ = [];
        for (const cb of q) { try { cb(vt); } catch (e) { console.error('raf', e); D.log.push(['raf', frameIdx, String(e)]); } }
        try {
          const s = window.__m1 && window.__m1.sim && window.__m1.sim();
          if (s && s.events) for (const e of s.events) { if (INTEREST.has(e.t)) D.log.push(['ev', frameIdx, [e.t, e.gate || e.k || e.name || e.why || '', e.n == null ? null : e.n]]); if (D.onEvent) try { D.onEvent(e, frameIdx); } catch (er) {} }
        } catch (e) {}
        if (capture) out.push(lo.toDataURL('image/png'));
        const c = window.__actx;
        frameIdx++;
        if (c && !CFG.noAudio) {
          const p = c.__suspend(frameIdx / FPS);
          if (!started) { started = true; c.__render = c.startRendering(); } else c.__resume();
          await p;
        }
        if (until) { let stop = false; try { stop = (0, eval)(until); } catch (e) {} if (stop) break; }
      }
      return out;
    },
    async finish() {
      const c = window.__actx; if (!c || CFG.noAudio) return null;
      c.__resume(); const buf = await c.__render;
      const n = Math.round(frameIdx * SR / FPS), L = buf.getChannelData(0), R = buf.getChannelData(1);
      const pcm = new Int16Array(n * 2);
      for (let i = 0; i < n; i++) { pcm[2 * i] = Math.max(-32768, Math.min(32767, Math.round(L[i] * 32767))); pcm[2 * i + 1] = Math.max(-32768, Math.min(32767, Math.round(R[i] * 32767))); }
      const u8 = new Uint8Array(pcm.buffer); let s = '';
      for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000));
      return { frames: frameIdx, samples: n, b64: btoa(s) };
    }
  };
})();
