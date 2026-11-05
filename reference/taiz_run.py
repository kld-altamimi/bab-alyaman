"""One full, deterministic flight through Taiz with sound. Mode 'plan': a small picture every 10 frames, the HUD's canvas
during the launcher fight, the whole log and the game's sound. Mode 'shoot': the same flight again, saving every frame of
the windows given in windows.json as PNG (the world's canvas, plus the HUD's where asked)."""
import json, os, sys, base64, time
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
MODE = sys.argv[1] if len(sys.argv) > 1 else 'plan'
OUT = os.path.join(common.D, '..', sys.argv[2] if len(sys.argv) > 2 else MODE); os.makedirs(OUT + '/f', exist_ok=True)
WIN = json.load(open(os.path.join(common.D, sys.argv[3] if len(sys.argv) > 3 else 'windows.json'))) if MODE == 'shoot' else []
PORT = int(os.environ.get('RIG_PORT', '8772' if MODE == 'plan' else '8773'))
def wanted(f):
    for w in WIN:
        if w['a'] <= f < w['b']: return w
    return None
srv = common.serve(PORT)
t0 = time.time()
with sync_playwright() as p:
    bw, pg, errs = common.boot(p, PORT, {'seed': 777, 'lensec': 260, 'muteVoices': os.environ.get('MUTE_VOICES') == '1'})
    pg.evaluate("window.__clean = true; window.__farce = true;")
    pg.evaluate("window.__m1.begin('taiz', 0)")
    saved = 0
    def grab(f, hud):
        global saved
        d = pg.evaluate("document.getElementById('lo').toDataURL('image/png')")
        open(f"{OUT}/f/{f:06d}.png", 'wb').write(base64.b64decode(d.split(',', 1)[1])); saved += 1
        if hud:
            h = pg.evaluate("(function(){var c=Render.hudCanvas(); return c ? c.toDataURL('image/png') : null;})()")
            if h: open(f"{OUT}/f/{f:06d}_hud.png", 'wb').write(base64.b64decode(h.split(',', 1)[1]))
    def step(n, until=None):
        got = 0
        while got < n:
            f = pg.evaluate("window.__drv.frame()")
            if MODE == 'shoot':
                w = wanted(f)
                if w:
                    pg.evaluate("window.__drv.step(1, false, null, null)")
                    grab(f, w.get('hud'))
                    got += 1
                    if until and pg.evaluate(until): return pg.evaluate("window.__drv.frame()")
                    continue
                # (fast-forward to the next window)
                nxt = min([w['a'] for w in WIN if w['a'] > f] + [f + 60])
                k = max(1, min(n - got, nxt - f, 60))
            else:
                k = min(10, n - got)
            pg.evaluate(f"window.__drv.step({k}, false, null, {json.dumps(until) if until else 'null'})")
            got += k
            f2 = pg.evaluate("window.__drv.frame()")
            if MODE == 'plan':
                d = pg.evaluate("document.getElementById('lo').toDataURL('image/jpeg', 0.6)")
                open(f"{OUT}/f/{f2:06d}.jpg", 'wb').write(base64.b64decode(d.split(',', 1)[1]))
                if pg.evaluate("!!(window.__m1.sim() && window.__m1.sim().boss && window.__m1.sim().boss.k === 'launcher')"):
                    h = pg.evaluate("(function(){var c=Render.hudCanvas(); return c ? c.toDataURL('image/png') : null;})()")
                    if h: open(f"{OUT}/f/{f2:06d}_hud.png", 'wb').write(base64.b64decode(h.split(',', 1)[1]))
            if until and pg.evaluate(until): return f2
        return pg.evaluate("window.__drv.frame()")
    # the opening plays itself out (no button: the scare and the scream), then Yazeed walks right to the Apache
    f = step(900, "(function(){var s=window.__m1.sim(); return s.intro && s.intro.st==='wait';})()")
    print('opening waits at', f, flush=True)
    pg.evaluate("window.__drv.down('ArrowRight')")
    f = step(1200, "(function(){var s=window.__m1.sim(); return s.heli && s.heli.st==='fly';})()")
    pg.evaluate("window.__drv.up('ArrowRight'); window.__pilotOn = true;")
    print('flying at', f, flush=True)
    f = step(14000, "(function(){var s=window.__m1.sim(); return !s || s.status==='over' || (s.status==='clear' && window.__m1.state()!=='play');})()")
    print('end at', f, pg.evaluate("(function(){var s=window.__m1.sim(); return {status:s.status, zone:s.zone, deaths:s.stats.deaths, state:window.__m1.state()};})()"), round(time.time() - t0), 's', flush=True)
    step(120)
    log = pg.evaluate("window.__drv.log"); subs = pg.evaluate("window.__drv.subs")
    r = pg.evaluate("window.__drv.finish()")
    open(OUT + '/game.pcm', 'wb').write(base64.b64decode(r['b64']))
    json.dump({'log': log, 'subs': subs, 'errs': errs, 'frames': r['frames'], 'samples': r['samples']}, open(OUT + '/log.json', 'w'), ensure_ascii=False)
    print('frames', r['frames'], 'samples', r['samples'], 'saved', saved, 'errors', errs[:4], round(time.time() - t0), 's')
    bw.close()
srv.shutdown()
