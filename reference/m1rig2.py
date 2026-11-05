"""The Strait (Mission 1) flown by game-development's smartBot, from the live build, deterministic (the Taiz rig's
driver), with a director for the onboarding reel: after chosen events the bot holds its fire and its ground for a
while (it still ducks and jumps what comes at it, and nothing hurts Yazeed meanwhile), so the man speaking stays on
screen. Mode 'plan': the whole log and the game's sound. Mode 'shoot': the same run again, saving every frame of the
windows in a JSON file as PNG. Usage: m1rig2.py plan|shoot <outdir> <director.json> [windows.json]
director.json: [{"on": "alarm", "nth": 1, "len": 80, "fire": false}, {"on": "surrender", "nth": 2, "len": 100, "fire": true}]"""
import json, os, sys, base64, time
sys.path.insert(0, '/tmp/claude-0/-home-claude/df6305fd-b1bf-5dfd-a75a-44d8bb54fcc7/scratchpad/taiz/rig')
os.environ.setdefault('TAIZ_BUILD', '../gc/build77')
import common
from playwright.sync_api import sync_playwright
G = '/tmp/claude-0/-home-claude/df6305fd-b1bf-5dfd-a75a-44d8bb54fcc7/scratchpad/gc/'
MODE = sys.argv[1]; OUT = G + sys.argv[2]; os.makedirs(OUT + '/f', exist_ok=True)
DIRECTOR = json.load(open(G + sys.argv[3]))
WIN = json.load(open(G + sys.argv[4])) if MODE == 'shoot' else []
PORT = int(os.environ.get('PORT', 8783 if MODE == 'plan' else 8784))
BOT = open(G + 'smartbot_fn.js').read()
EVENTS = ['checkpoint', 'life_lost', 'go', 'surrender', 'explode', 'land', 'alarm', 'capture', 'drop_weapon', 'plate_lost', 'clear', 'over', 'throw', 'tell']
HOOK = """(function(){
  window.__bot = (function(){ var T = Sim.T; __BOT__; return smartBot({}); })();
  var D = window.__drv, RULES = __RULES__, count = {}, holdUntil = -1, holdFire = true;
  D.onEvent = function (e, f) {
    var s = window.__m1.sim();
    if (e.t === 'alarm' || e.t === 'surrender' || e.t === 'capture' || e.t === 'drop_weapon' || e.t === 'plate_lost')
      D.log.push(['evx', f, [e.t, Math.round((e.x || 0) - s.cam), Math.round(e.y || 0), e.id == null ? null : e.id]]);
    count[e.t] = (count[e.t] || 0) + 1;
    for (var i = 0; i < RULES.length; i++) {
      var r = RULES[i];
      if (r.on === e.t && (r.nth || 1) === count[e.t]) { holdUntil = f + r.len; holdFire = !!r.fire; D.log.push(['hold', f, [e.t, r.len, holdFire]]); }
    }
  };
  var rs = Input.sample.bind(Input);
  Input.sample = function () {
    var base = rs();
    var s = window.__m1 && window.__m1.sim && window.__m1.sim();
    if (window.__botOn && s && s.status === 'play') {
      var p = window.__bot(s); for (var k in p) base[k] = p[k];
      var f = D.frame();
      if (f <= holdUntil) {
        if (!holdFire) { base.fire = false; base.grenade = false; }
        if (base.mx > 0) base.mx = 0;
        s.p.inv = Math.max(s.p.inv, 2);
      }
      if (f % 10 === 0) D.log.push(['cam', f, [Math.round(s.cam), Math.round(s.p.x - s.cam), s.zone]]);
    }
    return base;
  };
})()""".replace('__BOT__', BOT).replace('__RULES__', json.dumps(DIRECTOR))
def wanted(f):
    for w in WIN:
        if w['a'] <= f < w['b']: return w
    return None
srv = common.serve(PORT)
t0 = time.time()
with sync_playwright() as p:
    bw, pg, errs = common.boot(p, PORT, {'seed': 41, 'lensec': 300, 'muteVoices': os.environ.get('MUTEV') == '1', 'events': EVENTS})
    pg.evaluate("Sound.want(['strait', 'battery'])")
    for _ in range(100):
        pg.wait_for_timeout(100)
        if pg.evaluate("Sound.hasTrack('strait') && Sound.hasTrack('battery')"): break
    pg.evaluate(HOOK)
    pg.evaluate("window.__clean = true;")
    pg.evaluate("window.__m1.begin('m1', 0); window.__botOn = true;")
    saved = 0
    STOP = int(os.environ.get('STOPAT', '16000'))
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
    st = pg.evaluate("(function(){var s=window.__m1.sim(); return {status:s.status, zone:s.zone, deaths:s.stats.deaths, state:window.__m1.state()};})()")
    print('end at', f, st, round(time.time() - t0), 's', flush=True)
    pg.evaluate("window.__drv.step(60, false, null, null)")
    log = pg.evaluate("window.__drv.log"); subs = pg.evaluate("window.__drv.subs")
    r = pg.evaluate("window.__drv.finish()")
    open(OUT + '/game.pcm', 'wb').write(base64.b64decode(r['b64']))
    json.dump({'log': log, 'subs': subs, 'errs': errs, 'frames': r['frames'], 'samples': r['samples']}, open(OUT + '/log.json', 'w'), ensure_ascii=False)
    print('frames', r['frames'], 'samples', r['samples'], 'saved', saved, 'errors', errs[:4], round(time.time() - t0), 's')
    bw.close()
srv.shutdown()
