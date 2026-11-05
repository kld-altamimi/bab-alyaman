"""Shared bits of the filming rig: serve the live build (mk.BUILD), boot it under the deterministic driver (drv.js:
virtual time, seeded randomness, an offline audio context in lockstep with the frames), and hook the game's logs.
Used by film.py and lettering/strips.py."""
import threading, http.server, functools, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import mk
D = os.path.dirname(os.path.abspath(__file__))
SRC = mk.BUILD
KUFI = open(mk.FONT, 'rb').read()
DRV = open(os.path.join(D, 'drv.js')).read()
PILOT = open(os.path.join(D, 'pilot.js')).read()

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
def serve(port):
    H = functools.partial(Q, directory=SRC)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv

HOOKS = r"""
(() => {
  const D = window.__drv;
  // what the game says, and what music it asks for
  const sv = Sound.voice.bind(Sound);
  Sound.voice = function (id, o) { D.note('voice', [id, o || {}]); return sv(id, o); };
  const sm = Sound.startMusic.bind(Sound);
  Sound.startMusic = function (intro, which, fadeIn) { D.note('music', [intro, which || null, !!fadeIn]); return sm(intro, which, fadeIn); };
  const sp = Sound.stopMusic.bind(Sound);
  Sound.stopMusic = function (f) { D.note('stopmusic', [f == null ? null : f]); return sp(f); };
  const sj = Sound.jingle.bind(Sound);
  Sound.jingle = function (k) { D.note('jingle', [k]); return sj.apply(Sound, arguments); };
  // the subtitle on screen each frame, kept for the reel's own subtitle band (the canvas keeps the world only)
  const rd = Render.draw.bind(Render);
  Render.draw = function (s, o) {
    const sub = o && o.sub ? (o.sub.who || '') + '|' + (o.sub.text || '') : '';
    if (sub !== D.lastSub) { D.lastSub = sub; D.subs.push([D.frame(), sub]); }
    if (o && window.__clean) {
      // the reel draws its own subtitles; on foot (no zoom) the HUD would sit in the world's canvas, so it goes
      o = Object.assign({}, o, { sub: null });
      if (Render.zoom() === 1 && window.__m1.state() === 'play') o.noHud = true;
    }
    return rd(s, o);
  };
  // Taiz: game-development's pilot flies the Apache through the game's own input, once it is up (window.__pilotOn)
  window.__pilot = eval('(' + __PILOT__ + ')')({ stick: true });
  const rs = Input.sample.bind(Input);
  Input.sample = function () {
    const base = rs();
    const s = window.__m1 && window.__m1.sim && window.__m1.sim();
    if (window.__pilotOn && s && s.heli && s.heli.st === 'fly' && s.status === 'play') {
      const p = window.__pilot(s);
      for (const k in p) base[k] = p[k];
      if (window.__holdFire) { base.fire = false; base.gun = false; base.grenade = false; }
    }
    return base;
  };
  // no game over while filming
  window.__keep = function () { const s = window.__m1.sim(); if (s && s.p) { s.p.lives = Math.max(s.p.lives, 3); } };
  // the tracks a mission plays (its theme, its boss's, its speech), from the game's own LEVEL globals
  window.__tracksFor = function (id) {
    const Ls = Object.keys(window).filter(k => /^LEVEL(_|$)/.test(k)).map(k => window[k]).filter(L => L && L.id);
    const L = Ls.find(l => l.id === id);
    return L ? [L.music || 'strait', L.bossMusic || 'battery'].concat(L.speech ? ['speech:' + id] : []) : [];
  };
})();
"""

def boot(p, port, cfg, w=1920, h=1080, dpr=1, want=None):
    """Boot the build under the driver. want: a mission id whose tracks are decoded before the clock starts (so the
    run's timing never waits on a decode), or a list of track names."""
    bw = p.chromium.launch(args=['--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--disable-backgrounding-occluded-windows', '--autoplay-policy=no-user-gesture-required'])
    ctx = bw.new_context(locale='ar-SA', viewport={'width': w, 'height': h}, device_scale_factor=dpr)
    ctx.add_init_script('window.__CFG = ' + json.dumps(cfg) + ';')
    ctx.add_init_script(DRV)
    css = "@font-face{font-family:'Noto Kufi Arabic';src:url(http://127.0.0.1:%d/__kufi.ttf) format('truetype');font-weight:100 900;}" % port
    ctx.route('**/*posthog*', lambda r: r.abort())
    ctx.route('**/fonts.googleapis.com/**', lambda r: r.fulfill(status=200, content_type='text/css', body=css))
    ctx.route('**/__kufi.ttf', lambda r: r.fulfill(status=200, content_type='font/ttf', body=KUFI))
    pg = ctx.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append('console: ' + m.text[:200]) if m.type == 'error' else None)
    pg.goto(f'http://127.0.0.1:{port}/index.html?internal=1')
    for _ in range(300):
        pg.wait_for_timeout(100)
        if pg.evaluate("!!(window.__m1 && window.__m1.state && window.__m1.state()==='home')"): break
    pg.evaluate("Sound.unlock(); Sound.setVolume('music', 0);")
    for _ in range(200):
        pg.wait_for_timeout(100)
        if pg.evaluate("Sound.isReady()"): break
    pg.evaluate(HOOKS.replace('__PILOT__', json.dumps(PILOT)))
    tracks = []
    if want:
        tracks = pg.evaluate("(w) => typeof w === 'string' ? window.__tracksFor(w) : w", want)
        pg.evaluate("(t) => Sound.want(t)", tracks)
        music = [t for t in tracks if not t.startswith('speech:')]
        for _ in range(300):
            pg.wait_for_timeout(100)
            if pg.evaluate("(t) => Sound.hasFailed() || t.every(k => Sound.hasTrack(k))", music): break
        pg.wait_for_timeout(2500)          # (the speech sprite decodes a little after)
    if cfg.get('muteVoices'): pg.evaluate("Sound.setVolume('voice', 0)")
    pg.evaluate("BUILD=''; window.__drv.start()")
    pg.wait_for_timeout(200)
    return bw, pg, errs, tracks
