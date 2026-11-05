"""Ibb (Mission 4) on the live build 0.17.95, flown by game-development's newest smartBot (sources 29cea47: spokesmanBot,
the school, the rally), deterministic (the Taiz rig's driver). Starts from a zone (0 Wadi al-Sahul, 1 Jibla, 2 the terraces,
3 Sumara pass). Mode 'plan': the whole log and the game's sound. Mode 'shoot': the same run again, saving every frame of
the windows in a JSON file as PNG. Music muted (laid in the edit); voices and his speech on, in the game's own mix.
Usage: ibbrig.py plan|shoot <outdir> <zone> <stopframe> [windows.json]"""
import json, os, sys, base64, time
sys.path.insert(0, '/tmp/claude-0/-home-claude/df6305fd-b1bf-5dfd-a75a-44d8bb54fcc7/scratchpad/taiz/rig')
os.environ.setdefault('TAIZ_BUILD', '../ibb95')
import common
from playwright.sync_api import sync_playwright
G = '/tmp/claude-0/-home-claude/df6305fd-b1bf-5dfd-a75a-44d8bb54fcc7/scratchpad/ibbr/'
MODE = sys.argv[1]; OUT = G + sys.argv[2]; ZONE = int(sys.argv[3]); STOP = int(sys.argv[4])
os.makedirs(OUT + '/f', exist_ok=True)
WIN = json.load(open(G + sys.argv[5])) if MODE == 'shoot' else []
PORT = int(os.environ.get('PORT', 8790 if MODE == 'plan' else 8791))
BOT = open(G + 'smartbot_fn.js').read()
SKIP = ['shot', 'hit', 'step', 'casing', 'spark', 'thud', 'land', 'tell', 'bounce', 'eshot', 'ricochet', 'muzzle', 'smoke', 'dust', 'splash', 'shell']
HOOK = """(function(){
  window.__bot = (function(){ var T = Sim.T; __BOT__; return smartBot({}); })();
  var D = window.__drv, SKIP = __SKIP__, count = {};
  window.__evcount = count;
  D.onEvent = function (e, f) {
    count[e.t] = (count[e.t] || 0) + 1;
    if (window.__shieldOn && e.t === window.__shieldOn) window.__shield = true;
    var hf = window.__holdFireOn;           // [type, n, frames]: after that event, Yazeed holds his fire a while
    if (hf && e.t === hf[0] && (hf[1] == null || e.n === hf[1])) { window.__holdFireUntil = f + hf[2]; D.log.push(['hold', f, hf]); }
    if (SKIP.indexOf(e.t) >= 0) return;
    var s = window.__m1.sim(), o = {};
    for (var k in e) { var v = e[k]; if (typeof v === 'number') o[k] = Math.round(v * 10) / 10; else if (typeof v === 'string' || typeof v === 'boolean') o[k] = v; }
    o.cam = s ? Math.round(s.cam * 10) / 10 : null;
    D.log.push(['evx', f, o]);
  };
  // the director (env RALLYHOLD): Yazeed keeps back from the rally's chairs until the statement has got past «وانتهت.»
  var sv = Sound.voice.bind(Sound);
  Sound.voice = function (id, o) { if (id === 'sp_D7' && !window.__d7) window.__d7 = D.frame(); return sv(id, o); };
  var rs = Input.sample.bind(Input);
  Input.sample = function () {
    var base = rs();
    var s = window.__m1 && window.__m1.sim && window.__m1.sim();
    if (window.__botOn && s && s.status === 'play') {
      var p = window.__bot(s); for (var k in p) base[k] = p[k];
      var f = D.frame();
      if (window.__shield) s.p.inv = Math.max(s.p.inv, 2);       // nothing hurts Yazeed (inv 2 doesn't blink)
      if (window.__cleanFire && base.fire) {
        // as a player would: no shooting at an empty screen (a man of theirs, a barricade, a crate or drum, or the boss to shoot at)
        var any = !!(s.boss && s.boss.st !== 'dead'), e2, q;
        for (q = 0; !any && q < s.enemies.length; q++) { e2 = s.enemies[q]; if (e2.alive && e2.hostile && Sim.onScreen(s, e2.x, 0)) any = true; }
        for (q = 0; !any && q < s.bars.length; q++) { e2 = s.bars[q]; if (!e2.gone && Sim.onScreen(s, e2.x0 || e2.x || 0, 0)) any = true; }
        for (q = 0; !any && q < s.props.length; q++) { e2 = s.props[q]; if (!e2.gone && e2.hp > 0 && e2.k !== 'cover' && Math.abs(e2.x - s.p.x) < 170 && Sim.onScreen(s, e2.x, 0)) any = true; }
        if (!any) base.fire = false;
      }
      if (window.__holdFireUntil && f <= window.__holdFireUntil) { base.fire = false; base.grenade = false; }
      if (window.__rallyHold && s.rally && s.rally.st === 'speech' && !(window.__d7 && f > window.__d7 + 40)) {
        var lim = s.L.stage.x0 - 80;
        if (s.p.x > lim && base.mx > 0) base.mx = 0;
      }
      if (f % 10 === 0) {
        var b = s.boss, o = { cam: Math.round(s.cam), px: Math.round(s.p.x - s.cam), py: Math.round(s.p.y), zone: s.zone, plates: s.p.plates, lives: s.p.lives };
        if (b) { o.bk = b.kind; o.bst = b.st; o.bx = Math.round(b.x - s.cam); o.by = Math.round(b.y); o.hp = b.hp; }
        if (s.rally) { o.rst = s.rally.st; o.rx = Math.round(s.rally.x - s.cam); }
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
    bw, pg, errs = common.boot(p, PORT, {'seed': 41, 'lensec': 300, 'muteVoices': False})
    pg.evaluate("Sound.want(['ibb', 'spokesman', 'speech:ibb'])")
    for _ in range(150):
        pg.wait_for_timeout(100)
        if pg.evaluate("Sound.hasTrack('ibb') && Sound.hasTrack('spokesman')"): break
    pg.wait_for_timeout(2500)
    print('sound', pg.evaluate("JSON.stringify(Sound.info ? Sound.info() : null)")[:300], flush=True)
    pg.evaluate(HOOK)
    pg.evaluate("window.__clean = true;")
    if os.environ.get('RALLYHOLD') == '1': pg.evaluate("window.__rallyHold = true;")
    if os.environ.get('CLEANFIRE') == '1': pg.evaluate("window.__cleanFire = true;")
    # (env NOHINTS: the school's blinking «افتح» over its doors is a hint to the player, like the HUD: not drawn)
    if os.environ.get('NOHINTS') == '1': pg.evaluate("(function(){ var T0 = window.T; window.T = function (k, a) { return k === 'OPEN' ? '' : T0(k, a); }; })()")
    if os.environ.get('SHIELD'): pg.evaluate("window.__shieldOn = %s;" % json.dumps(os.environ['SHIELD']))
    if os.environ.get('HOLDFIRE'):
        t_, n_, k_ = os.environ['HOLDFIRE'].split(':'); pg.evaluate("window.__holdFireOn = %s;" % json.dumps([t_, int(n_) if n_ else None, int(k_)]))
    pg.evaluate(f"window.__m1.begin('ibb', {ZONE}); window.__botOn = true;")
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
    json.dump({'log': log, 'subs': subs, 'errs': errs, 'frames': r['frames'], 'samples': r['samples']}, open(OUT + '/log.json', 'w'), ensure_ascii=False)
    print('frames', r['frames'], 'samples', r['samples'], 'saved', saved, 'errors', errs[:4], round(time.time() - t0), 's')
    bw.close()
srv.shutdown()
