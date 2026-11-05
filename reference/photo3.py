"""A staged still: Taiz flown without the countdown farce, so the Apache attacks the launcher while its missile is still
low; from half its strength the Apache also fires guided rockets at it (ammunition topped up). The kill's score pop is
left out. Saves the world's canvas every 2nd frame from the rockets on, and every frame from the kill until just before
the missile would cook off. Usage: TAIZ_BUILD=build75 python3 photo3.py <outdir>"""
import json, os, sys, base64, time
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
OUT = os.path.join(common.D, '..', sys.argv[1] if len(sys.argv) > 1 else 'photo75c'); os.makedirs(OUT + '/f', exist_ok=True)
PORT = int(os.environ.get('RIG_PORT', '8776'))
HP_STAGE = float(os.environ.get('HP_STAGE', '240'))
STAGE = """(function(){
  const rs = Input.sample.bind(Input);
  window.__rkT = 0;
  Input.sample = function () { const b = rs(); if (window.__stage) { window.__rkT++; b.grenade = (window.__rkT % 18) < 2; } return b; };
  const oe = Render.onEvents.bind(Render);
  Render.onEvents = function (s, ev) { for (const e of ev) if (e.t === 'die' && e.k === 'launcher') e.t = 'die_quiet'; return oe(s, ev); };
})()"""
META = """(function(){
 var s=window.__m1.sim(); if(!s) return null;
 var h=s.heli, p=s.p, L=null;
 (s.enemies||[]).forEach(function(e){ if(e.k==='launcher') L=e; });
 var x0=s.cam, y0=s.camY||0, W=s.viewW, H=s.viewH, near=0, rkn=0;
 (s.bullets||[]).forEach(function(b){ if(b.own && L && Math.abs(b.x-L.x)<160 && b.x>x0 && b.x<x0+W && b.y>y0 && b.y<y0+H) near++; });
 (s.rockets||[]).forEach(function(r){ if(!r.gone && r.x>x0 && r.x<x0+W && r.y>y0 && r.y<y0+H) rkn++; });
 return {f: window.__drv.frame(), h: h?[Math.round(h.x-x0),Math.round(h.y-y0),h.face,h.st,Math.round(h.tilt*100)/100]:null, inv:p?p.inv:null, ammo:p?p.grenades:null,
   L: L?[Math.round(L.x-x0),Math.round(L.y-y0),Math.round(L.hp),L.raise!=null?Math.round(L.raise*100)/100:null,L.st,L.dieT==null?null:L.dieT]:null,
   near:near, rkn:rkn, lock: h?[h.rlock||0, h.rlockT||0]:null};
})()"""
srv = common.serve(PORT)
t0 = time.time()
with sync_playwright() as p:
    bw, pg, errs = common.boot(p, PORT, {'seed': 777, 'lensec': 260, 'noAudio': True, 'muteVoices': True})
    pg.evaluate("window.__clean = true; window.__farce = false;")
    pg.evaluate(STAGE)
    pg.evaluate("window.__m1.begin('taiz', 0)")
    def run(n, until, chunk):
        got = 0
        while got < n:
            k = min(chunk, n - got)
            pg.evaluate(f"window.__drv.step({k}, false, null, {json.dumps(until)})")
            got += k
            pg.evaluate("window.__keep && window.__keep()")
            if pg.evaluate(until): break
        return pg.evaluate("window.__drv.frame()")
    run(900, "(function(){var s=window.__m1.sim(); return s.intro && s.intro.st==='wait';})()", 10)
    pg.evaluate("window.__drv.down('ArrowRight')")
    run(1200, "(function(){var s=window.__m1.sim(); return s.heli && s.heli.st==='fly';})()", 10)
    pg.evaluate("window.__drv.up('ArrowRight'); window.__pilotOn = true;")
    f = run(14000, "(function(){var s=window.__m1.sim(); return !s || s.status!=='play' || !!(s.boss && s.boss.kind==='launcher');})()", 30)
    print('launcher fight from', f, round(time.time() - t0), 's', flush=True)
    f = run(6000, "(function(){var s=window.__m1.sim(); if(!s||s.status!=='play') return true; var L=null; s.enemies.forEach(function(e){ if(e.k==='launcher') L=e; }); return !!(L && L.hp <= %f);})()" % HP_STAGE, 3)
    print('staging rockets from', f, pg.evaluate(META), flush=True)
    pg.evaluate("window.__stage = true")
    rows, saved = [], 0
    while True:
        pg.evaluate("window.__drv.step(1, false, null, null)")
        pg.evaluate("(function(){var s=window.__m1.sim(); if (s && s.p) { s.p.grenades = 12; } window.__keep && window.__keep();})()")
        m = pg.evaluate(META)
        if not m: break
        rows.append(m)
        L = m['L']
        dying = L and L[5] is not None
        if dying or m['f'] % 2 == 0 or (L and L[2] <= 140):
            d = pg.evaluate("document.getElementById('lo').toDataURL('image/png')")
            open(f"{OUT}/f/{m['f']:06d}.png", 'wb').write(base64.b64decode(d.split(',', 1)[1])); saved += 1
        if (dying and L[5] >= 28) or len(rows) > 1500: break
    json.dump(rows, open(OUT + '/meta.json', 'w'))
    print('rows', len(rows), 'saved', saved, 'last', rows[-1], 'errors', errs[:3], round(time.time() - t0), 's')
    bw.close()
srv.shutdown()
