"""Film a mission of the live build, played by game-development's smartBot (Taiz's Apache by its pilot), deterministic:
the same command gives the same run, frame for frame.
  plan  — the whole run's log (every event with positions, the camera every 10 frames, voices, subtitles) and the game's
          sound, no pictures: read it to choose moments.
  shoot — the same run again, saving every frame inside the windows as PNG (the world's canvas, 384x216, no HUD).
Usage: film.py plan|shoot <outdir> <mission> <zone> <stopframe> [windows.json]
  mission: m1 (the Strait), mocha (the Coffee Port), taiz, ibb …; zone: the checkpoint to start from (0 = the start)
  windows.json: [{"a": 120, "b": 400}, …] source frames [a, b)
Env (defaults in brackets):
  CLEANFIRE [1]  Yazeed fires only when there is something on screen to fire at (no shooting at an empty screen)
  NOHINTS   [1]  in-world hints for the player (the school's blinking «افتح») are not drawn, like the HUD
  SEED [41]  the run's randomness; another seed gives another run
  SHIELD=<event>  nothing hurts Yazeed after that event (staging: show it to Khaled as staging)
  HOLDFIRE=<event>:<n>:<frames>  he holds fire that long after the n-th such event (staging)
  PORT  the local server's port (one per parallel run)
  MUTEVOICES=1  the game's voices left out of game.pcm (effects only), for a reel that lays its lines itself (reel.py
                "lines"): each line then plays where its subject is on screen; the subtitles log still records them
Outputs: <outdir>/f/NNNNNN.png (shoot), <outdir>/game.pcm (48 kHz stereo s16, voices and effects, music muted: lay the
music in the edit), <outdir>/log.json {log, subs, errs, frames, samples}.
Note: a shoot can come out one frame early against its plan (or another shoot); compare the voice entries of the two
logs and shift frame numbers by the offset before mixing frames from two runs."""
import json, os, sys, base64, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common, mk
from playwright.sync_api import sync_playwright
MODE = sys.argv[1]; OUT = os.path.abspath(sys.argv[2]); MISSION = sys.argv[3]; ZONE = int(sys.argv[4]); STOP = int(sys.argv[5])
os.makedirs(OUT + '/f', exist_ok=True)
WIN = json.load(open(sys.argv[6])) if MODE == 'shoot' else []
PORT = int(os.environ.get('PORT', 8790 if MODE == 'plan' else 8791))
SEED = int(os.environ.get('SEED', '41'))
BOT = open(mk.BOT if os.path.exists(mk.BOT) else mk.BOT_FALLBACK).read()
SKIP = ['shot', 'hit', 'step', 'casing', 'spark', 'thud', 'land', 'tell', 'bounce', 'eshot', 'ricochet', 'muzzle', 'smoke', 'dust', 'splash', 'shell']
HOOK = """(function(){
  window.__bot = (function(){ var T = Sim.T; __BOT__; return smartBot({}); })();
  var D = window.__drv, SKIP = __SKIP__, count = {};
  window.__evcount = count;
  D.onEvent = function (e, f) {
    count[e.t] = (count[e.t] || 0) + 1;
    if (window.__shieldOn && e.t === window.__shieldOn) window.__shield = true;
    var hf = window.__holdFireOn;
    if (hf && e.t === hf[0] && (hf[1] == null || e.n === hf[1])) { window.__holdFireUntil = f + hf[2]; D.log.push(['hold', f, hf]); }
    if (SKIP.indexOf(e.t) >= 0) return;
    var s = window.__m1.sim(), o = {};
    for (var k in e) { var v = e[k]; if (typeof v === 'number') o[k] = Math.round(v * 10) / 10; else if (typeof v === 'string' || typeof v === 'boolean') o[k] = v; }
    o.cam = s ? Math.round(s.cam * 10) / 10 : null;
    D.log.push(['evx', f, o]);
  };
  var rs = Input.sample.bind(Input);
  Input.sample = function () {
    var base = rs();
    var s = window.__m1 && window.__m1.sim && window.__m1.sim();
    if (window.__botOn && s && s.status === 'play' && !(s.heli && s.heli.st === 'fly')) {
      var p = window.__bot(s); for (var k in p) base[k] = p[k];
    }
    if (s && s.status !== 'play' && D.frame() % 10 === 0) D.log.push(['cam', D.frame(), { status: s.status, state: window.__m1.state(), cam: Math.round(s.cam), px: Math.round(s.p.x - s.cam) }]);
    if (s && s.status === 'play') {
      var f = D.frame();
      if (window.__shield) s.p.inv = Math.max(s.p.inv, 2);       // nothing hurts Yazeed (inv 2 doesn't blink)
      if (window.__cleanFire && base.fire && !(s.heli && s.heli.st === 'fly')) {
        var any = !!(s.boss && s.boss.st !== 'dead' && Math.abs(s.boss.x - (s.cam + s.viewW / 2)) < s.viewW / 2 + 30), e2, q;   // a boss still off-screen is nothing to fire at
        for (q = 0; !any && q < (s.enemies || []).length; q++) { e2 = s.enemies[q]; if (e2.alive && e2.hostile && Sim.onScreen(s, e2.x, 0)) any = true; }
        for (q = 0; !any && q < (s.bars || []).length; q++) { e2 = s.bars[q]; if (!e2.gone && Sim.onScreen(s, e2.x0 || e2.x || 0, 0)) any = true; }
        for (q = 0; !any && q < (s.props || []).length; q++) { e2 = s.props[q]; if (!e2.gone && e2.hp > 0 && e2.k !== 'cover' && Math.abs(e2.x - s.p.x) < 170 && Sim.onScreen(s, e2.x, 0)) any = true; }
        if (!any) base.fire = false;
      }
      if (window.__holdFireUntil && f <= window.__holdFireUntil) { base.fire = false; base.grenade = false; }
      if (f % 10 === 0) {
        var b = s.boss, o = { cam: Math.round(s.cam), px: Math.round(s.p.x - s.cam), py: Math.round(s.p.y), zone: s.zone, plates: s.p.plates, lives: s.p.lives, fire: !!base.fire, mx: base.mx || 0, my: base.my || 0, face: s.p.face };
        if (b) { o.bk = b.kind; o.bst = b.st; o.bx = Math.round(b.x - s.cam); o.by = Math.round(b.y); o.hp = b.hp; }
        if (s.rally) { o.rst = s.rally.st; o.rx = Math.round(s.rally.x - s.cam); }
        if (s.heli) { o.hx = Math.round(s.heli.x - s.cam); o.hy = Math.round(s.heli.y); o.hst = s.heli.st; }
        D.log.push(['cam', f, o]);
      }
    }
    return base;
  };
})()""".replace('__BOT__', BOT).replace('__SKIP__', json.dumps(SKIP))
def wanted(f):
    for w in WIN:
        if w['a'] <= f < w['b']: return w
    return None
srv = common.serve(PORT)
t0 = time.time()
with sync_playwright() as p:
    bw, pg, errs, tracks = common.boot(p, PORT, {'seed': SEED, 'lensec': max(60, STOP // 60 + 30), 'muteVoices': os.environ.get('MUTEVOICES') == '1'}, want=MISSION)
    print('tracks', tracks, flush=True)
    pg.evaluate(HOOK)
    pg.evaluate("window.__clean = true; window.__pilotOn = true;")
    if os.environ.get('CLEANFIRE', '1') == '1': pg.evaluate("window.__cleanFire = true;")
    if os.environ.get('NOHINTS', '1') == '1': pg.evaluate("(function(){ var T0 = window.T; window.T = function (k, a) { return k === 'OPEN' ? '' : T0(k, a); }; })()")
    if os.environ.get('SHIELD'): pg.evaluate("window.__shieldOn = %s;" % json.dumps(os.environ['SHIELD']))
    if os.environ.get('HOLDFIRE'):
        t_, n_, k_ = os.environ['HOLDFIRE'].split(':'); pg.evaluate("window.__holdFireOn = %s;" % json.dumps([t_, int(n_) if n_ else None, int(k_)]))
    pg.evaluate(f"window.__m1.begin({json.dumps(MISSION)}, {ZONE}); window.__botOn = true;")
    saved = 0
    END = "(function(){var s=window.__m1.sim(); return !s || s.status==='over' || (s.status==='clear' && window.__m1.state()!=='play') || window.__drv.frame() >= %d;})()" % STOP
    while True:
        f = pg.evaluate("window.__drv.frame()")
        if MODE == 'shoot':
            w = wanted(f)
            if w:
                pg.evaluate("window.__drv.step(1, false, null, null)")
                d = pg.evaluate("document.getElementById('lo').toDataURL('image/png')")
                open(f"{OUT}/f/{f:06d}.png", 'wb').write(base64.b64decode(d.split(',', 1)[1])); saved += 1
                pg.evaluate("window.__keep && window.__keep()")
                if pg.evaluate(END): break
                continue
            nxt = min([w['a'] for w in WIN if w['a'] > f] + [f + 60])
            if not [w for w in WIN if w['b'] > f]: break
            k = max(1, min(nxt - f, 60))
        else:
            k = 10
        pg.evaluate(f"window.__drv.step({k}, false, null, {json.dumps(END)})")
        pg.evaluate("window.__keep && window.__keep()")
        if pg.evaluate(END): break
    f = pg.evaluate("window.__drv.frame()")
    st = pg.evaluate("(function(){var s=window.__m1.sim(); return {status:s.status, zone:s.zone, deaths:s.stats.deaths, state:window.__m1.state(), lo:[document.getElementById('lo').width, document.getElementById('lo').height], zoom: Render.zoom()};})()")
    print('end at', f, st, round(time.time() - t0), 's', flush=True)
    print('event counts', pg.evaluate("JSON.stringify(window.__evcount)")[:1500], flush=True)
    pg.evaluate("window.__drv.step(60, false, null, null)")
    log = pg.evaluate("window.__drv.log"); subs = pg.evaluate("window.__drv.subs")
    r = pg.evaluate("window.__drv.finish()")
    open(OUT + '/game.pcm', 'wb').write(base64.b64decode(r['b64']))
    json.dump({'mission': MISSION, 'zone': ZONE, 'seed': SEED, 'log': log, 'subs': subs, 'errs': errs, 'frames': r['frames'], 'samples': r['samples']}, open(OUT + '/log.json', 'w'), ensure_ascii=False)
    print('frames', r['frames'], 'samples', r['samples'], 'saved', saved, 'errors', errs[:4], round(time.time() - t0), 's')
    bw.close()
srv.shutdown(); srv.server_close()
