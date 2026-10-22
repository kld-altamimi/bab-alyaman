# game-features' sign-off: checks a build of Bab al-Yemen against game-features' "must still work" checklist
# (claude/topics/game-features-checklist.md in the Project, lines C1..C25) in headless Chromium (Python Playwright).
# Everything outside the local server is blocked; the game's HM.track calls are recorded, never sent.
# Usage: python3 tools/signoff.py <folder with index.html and audio/> <output folder> [--strict]
#   --strict: the lines marked [0.10.64] must be there too (every build made after 0.10.64 is live).
# Writes <output folder>/signoff.txt (one PASS / FAIL per line, with what was seen) and screenshots.
import asyncio, functools, http.server, json, re, sys, threading, urllib.parse
from playwright.async_api import async_playwright

SITE, OUT = sys.argv[1], sys.argv[2]
REQUIRE_064 = '--strict' in sys.argv
PORT = 8795
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), functools.partial(Q, directory=SITE))
threading.Thread(target=srv.serve_forever, daemon=True).start()
SRC = open(f'{SITE}/index.html', encoding='utf-8').read()
HAS_064 = "HM.track('menu_step'" in SRC
BUILD = (re.search(r'var BUILD = "([^"]+)"', SRC) or [None, '?'])[1]
LIVE = 'https://kld-altamimi.github.io/bab-alyaman/'

ANDROID = 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Mobile Safari/537.36'
IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1'
PHONE = {'width': 844, 'height': 390}
UPRIGHT = {'width': 390, 'height': 844}
DESK = {'width': 1280, 'height': 720}

SPY = """(() => { let h; Object.defineProperty(window, 'HM', { configurable: true, get() { return h; }, set(v) {
  h = v; if (v && v.track) { const t = v.track; v.track = function (n, p) { (window.__ev = window.__ev || []).push([n, JSON.parse(JSON.stringify(p || {}))]); return t.apply(this, arguments); }; } } }); })();"""
STUBS = """window.__opened = []; window.open = function (u) { window.__opened.push(String(u)); return null; };"""
SHEET = """window.__shared = []; Object.defineProperty(navigator, 'share', { configurable: true, value: function (d) { window.__shared.push(d); return Promise.resolve(); } });"""
NOSHEET = """Object.defineProperty(navigator, 'share', { configurable: true, value: undefined });"""
CLIP_OK = """window.__clip = []; Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: function (t) { window.__clip.push(t); return Promise.resolve(); } } });"""
CLIP_FAIL = """Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: function () { return Promise.reject(new Error('no')); } } }); document.execCommand = function () { return false; };"""
# frames delivered exactly 1/30 s apart once window.__fake30 is set (what a phone's power saving does)
FAKE30 = """(() => { const raf = window.requestAnimationFrame.bind(window); let last = 0, fake = null; window.__fake30 = false;
  window.requestAnimationFrame = function (cb) { return raf(function (t) {
    if (window.__fake30) { fake = (fake == null ? last : fake) + 1000 / 30; last = fake; cb(fake); } else { last = t; cb(t); } }); }; })();"""
OLD_SAVE = """if (!sessionStorage.getItem('seeded')) { sessionStorage.setItem('seeded', '1');
  localStorage.setItem('strait-m1', JSON.stringify({ scheme: 'auto', muted: true, lang: 'en', dev: false, prog: { m1: { runs: 3, reached: 2, cleared: true } }, last: 'm1' })); }"""
HOOKS = """(() => { if (window.__hooked) return; window.__hooked = 1; window.__hints = []; window.__sp = [];
  const sh = Render.setHint; Render.setHint = function (t) { window.__hints.push(String(t)); return sh.apply(this, arguments); };
  const sp = Sound.pause; Sound.pause = function (b) { window.__sp.push(b); return sp.apply(this, arguments); }; })()"""
VIS = "(id => { const e = typeof id === 'string' ? document.getElementById(id) : id; if (!e || e.getClientRects().length === 0) return false; const cs = getComputedStyle(e); return cs.visibility !== 'hidden' && cs.display !== 'none'; })"
RECT = "(id => { const b = document.getElementById(id).getBoundingClientRect(); return [b.left, b.top, b.width, b.height]; })"
SAVE = "(() => { try { return JSON.parse(localStorage.getItem('strait-m1')); } catch (e) { return null; } })()"

checks = {}       # C-id -> list of (ok, note)
errors = {}       # case -> page errors
events_seen = set()
def add(cid, ok, note):
    checks.setdefault(cid, []).append((bool(ok), note))

async def new_page(browser, vp, ua=ANDROID, touch=True, locale='en-US', init=()):
    kw = dict(viewport=vp, device_scale_factor=1, is_mobile=touch, has_touch=touch, locale=locale)
    if ua and touch: kw['user_agent'] = ua
    ctx = await browser.new_context(**kw)
    for s in (SPY, STUBS) + tuple(init): await ctx.add_init_script(s)
    async def block(route):
        if route.request.url.startswith(f'http://127.0.0.1:{PORT}/'): await route.continue_()
        else: await route.abort()
    await ctx.route('**/*', block)
    pg = await ctx.new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    return ctx, pg, errs

async def load(pg, query=''):
    await pg.goto(f'http://127.0.0.1:{PORT}/index.html{query}')
    await pg.wait_for_function("!!(window.__m1 && window.__m1.state && ['home','map'].indexOf(window.__m1.state()) >= 0)", timeout=30000)
    await pg.evaluate(HOOKS)
    await pg.wait_for_timeout(700)

async def wait_state(pg, s, t=8000):
    try:
        await pg.wait_for_function(f"__m1.state() === '{s}'", timeout=t, polling=50); return True
    except Exception:
        return False

async def click(pg, id_):
    await pg.evaluate(f"document.getElementById('{id_}').click()")

async def vis(pg, id_):
    return await pg.evaluate(f"{VIS}('{id_}')")

async def text(pg, id_):
    # (the words as written: the game sets some in capitals with CSS)
    return await pg.evaluate(f"((document.getElementById('{id_}') || {{}}).textContent || '').replace(/\\s+/g, ' ')")

async def evs(pg, name=None):
    ev = await pg.evaluate("window.__ev || []")
    for e in ev: events_seen.add(e[0])
    return [e for e in ev if name is None or e[0] == name]

async def tap_start(pg, vp, touch=True):
    if touch: await pg.touchscreen.tap(vp['width'] // 2, vp['height'] // 2)
    else: await pg.keyboard.press('Enter')
    ok = await wait_state(pg, 'play', 10000)
    await pg.wait_for_timeout(900)
    return ok

async def clear_mission(pg):
    await pg.wait_for_function("() => { const s = __m1.sim(); if (__m1.state() === 'play' && s) { s.status = 'clear'; s.clearT = 400; } return __m1.state() === 'results'; }", timeout=12000, polling=100)
    await pg.wait_for_timeout(1300)

async def game_over(pg):
    await pg.evaluate("__m1.sim().status = 'over'")
    ok = await wait_state(pg, 'over', 6000)
    await pg.wait_for_timeout(900)
    return ok

async def wake(pg, vp):
    await pg.touchscreen.tap(vp['width'] // 2, vp['height'] // 2)
    try:
        await pg.wait_for_function("!document.querySelector('#pHome .acts').hidden", timeout=4000); return True
    except Exception:
        return False

def done(name, errs):
    errors[name] = errs[:]

# ------------------------------------------------------------------------------------------------ the cases
async def case_play_new(browser):
    ctx, pg, errs = await new_page(browser, PHONE)
    await load(pg, '?play&utm_source=instagram&utm_medium=paid&utm_id=1&internal=1')
    look = await pg.evaluate(f"""({{ st: __m1.state(), quick: document.getElementById('app').classList.contains('is-quick'),
      stick: {VIS}('stick'), fire: {VIS}('bFire'), x: getComputedStyle(document.getElementById('aX')).display }})""")
    await pg.screenshot(path=f'{OUT}/C1_play_first_screen.png')
    started = await tap_start(pg, PHONE)
    cur, frm = await pg.evaluate("[__m1.cur(), __m1.run().from]")
    steps = [e[1] for e in await evs(pg, 'menu_step')]
    ok = look['st'] == 'home' and look['quick'] and look['stick'] and look['fire'] and started and cur == 'm1' and frm == 0
    add('C1', ok, f"phone: quick={look['quick']} controls={look['stick'] and look['fire']} one tap -> play={started} m1 from {frm}")
    add('C6', look['x'] == 'none', f"X credit hidden on the ?play screen (display {look['x']})")
    if HAS_064:
        add('C23', [s.get('step') for s in steps] == ['title'] and steps and steps[0].get('link') == 'play', f"?play tap: menu_step {steps}")
    await evs(pg); done('play_new', errs); await ctx.close()

async def case_play_desktop(browser):
    ctx, pg, errs = await new_page(browser, DESK, ua=None, touch=False)
    await load(pg, '?play&internal=1')
    quick = await pg.evaluate("document.getElementById('app').classList.contains('is-quick')")
    await pg.screenshot(path=f'{OUT}/C1_play_first_screen_desktop.png')
    started = await tap_start(pg, DESK, touch=False)
    add('C1', quick and started, f"computer: quick={quick}, a key -> play={started}")
    await evs(pg); done('play_desktop', errs); await ctx.close()

async def case_play_upright(browser, locale='en-US'):
    ctx, pg, errs = await new_page(browser, UPRIGHT, locale=locale)
    await load(pg, '?play&internal=1')
    info = await pg.evaluate(f"""(() => {{ const r = id => {{ const b = document.getElementById(id).getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; }};
      return {{ on: {VIS}('turn'), a: document.getElementById('turnA').textContent.trim(), b: document.getElementById('turnB').textContent.trim(),
               turn: r('turn'), others: ['stick', 'bFire', 'bJump', 'bBomb'].filter(id => {VIS}(id)).map(id => [id, r(id)]) }}; }})()""")
    t = info['turn']
    hits = [o[0] for o in info['others'] if not (t[2] <= o[1][0] or o[1][2] <= t[0] or t[3] <= o[1][1] or o[1][3] <= t[1])]
    await pg.screenshot(path=f'{OUT}/C3_turn_note_{locale}.png')
    if locale == 'en-US':
        add('C3', info['on'] and info['a'] == 'Turn your phone sideways' and not hits, f"turn note shown={info['on']} '{info['a']}' / '{info['b']}', overlaps={hits}")
    else:
        latin = re.findall(r'[A-Za-z]+', info['a'] + ' ' + info['b'])
        add('C20', info['on'] and not latin, f"Arabic turn note: '{info['a']}' / '{info['b']}'")
    await evs(pg); done(f'play_upright_{locale}', errs); await ctx.close()

async def case_play_returning(browser):
    ctx, pg, errs = await new_page(browser, PHONE)
    await load(pg, '?play&internal=1')
    await tap_start(pg, PHONE)
    await pg.evaluate("window.__ev = []")
    await load(pg, '?play&internal=1')
    st, quick = await pg.evaluate("[__m1.state(), document.getElementById('app').classList.contains('is-quick')]")
    add('C2', st == 'map' and not quick, f"?play with progress opens: {st}")
    if HAS_064:
        steps = [e[1] for e in await evs(pg, 'menu_step')]
        add('C23', len(steps) == 1 and steps[0].get('step') == 'map' and steps[0].get('link') == 'play', f"returning ?play: menu_step {steps}")
    await evs(pg); done('play_returning', errs); await ctx.close()

async def case_params(browser):
    for q, want in [('?utm_source=instagram&utm_medium=story&utm_campaign=1&internal=1&foo=bar', False),
                    ('?utm_source=instagram&utm_medium=paid&utm_id=1&play', True), ('?player=1&internal=1', False),
                    ('?internal=1&play=1', True), ('', False)]:
        ctx, pg, errs = await new_page(browser, PHONE)
        await load(pg, q)
        st, quick = await pg.evaluate("[__m1.state(), document.getElementById('app').classList.contains('is-quick')]")
        add('C5', st == 'home' and quick == want, f"'{q or '(no parameters)'}' -> {st}, one-tap screen={quick}")
        done(f'params {q}', errs); await ctx.close()

async def case_plain_flow(browser):
    ctx, pg, errs = await new_page(browser, PHONE)
    await load(pg, '?internal=1&utm_source=twitter')
    hidden_before = await pg.evaluate("document.querySelector('#pHome .acts').hidden")
    woke = await wake(pg, PHONE)
    acts = {b: await vis(pg, b) for b in ('bStart', 'bOpts', 'bShare')}
    add('C4', hidden_before and woke and all(acts.values()), f"title: buttons hidden before the tap={hidden_before}, after={acts}")
    await pg.screenshot(path=f'{OUT}/C4_home.png')
    x = await pg.evaluate(f"""(() => {{ const a = document.getElementById('aX'); a.addEventListener('click', e => e.preventDefault()); a.click();
      return {{ shown: {VIS}(a), href: a.href }}; }})()""")
    soc = [e[1] for e in await evs(pg, 'social_click')]
    add('C6', x['shown'] and x['href'] == 'https://x.com/babalyemengame', f"X credit shown, href {x['href']}")
    add('C22', soc == [{'to': 'x'}], f"social_click {soc}")
    # options from home
    await click(pg, 'bOpts')
    o1 = await wait_state(pg, 'opts', 3000)
    ctl = {b: await vis(pg, b) for b in ('segHold', 'segAuto', 'bSound3', 'vMusic', 'vSfx', 'vVoice', 'langEn', 'langAr', 'bDev', 'bErase', 'bBack')}
    full = await vis(pg, 'bFull')
    devtxt = await text(pg, 'bDev')
    await pg.screenshot(path=f'{OUT}/C9_options.png')
    await click(pg, 'bBack')
    back1 = await wait_state(pg, 'home', 3000)
    add('C9', o1 and all(ctl.values()) and devtxt.strip() == 'Developer: off' and back1,
        f"options from home={o1}, controls all shown={all(ctl.values())} {'' if all(ctl.values()) else ctl}, full screen button shown={full}, '{devtxt.strip()}', back={back1}")
    # Start -> map
    await click(pg, 'bStart')
    m = await wait_state(pg, 'map', 5000)
    add('C6', m, f"Start -> map={m}")
    await pg.wait_for_timeout(800)
    n = await pg.evaluate("CAMPAIGN.length")
    cardv = {b: await vis(pg, b) for b in ('mName', 'mBrief', 'mCps', 'mBoss', 'bPlay', 'bHome', 'bBriefs', 'bOpts2')}
    await pg.screenshot(path=f'{OUT}/C7_map_card.png')
    add('C7', all(cardv.values()), f"the card's parts shown: {all(cardv.values())} {'' if all(cardv.values()) else cardv}")
    # the From picker: developer only
    f0 = await vis(pg, 'mFromRow')
    await pg.evaluate("__m1.setDev(true)"); await pg.wait_for_timeout(200)
    f1 = await vis(pg, 'mFromRow')
    opts = await pg.evaluate("document.getElementById('mFrom').options.length")
    await pg.evaluate("__m1.setDev(false)"); await pg.wait_for_timeout(200)
    f2 = await vis(pg, 'mFromRow')
    add('C8', (not f0) and f1 and (not f2) and opts > 1, f"From picker: dev off={f0}, dev on={f1} ({opts} checkpoints), off again={f2}")
    # options from the map
    await click(pg, 'bOpts2')
    o2 = await wait_state(pg, 'opts', 3000)
    await click(pg, 'bBack')
    b2 = await wait_state(pg, 'map', 3000)
    add('C9', o2 and b2, f"options from the map={o2}, back to the map={b2}")
    # briefings: the list picks a mission
    await click(pg, 'bBriefs')
    br = await wait_state(pg, 'brief', 3000)
    items = await pg.evaluate("[...document.querySelectorAll('#bList .brief-item')].map(b => b.getAttribute('data-id'))")
    await pg.screenshot(path=f'{OUT}/C7_briefings.png')
    sel0 = await pg.evaluate("__m1.menu().sel")
    pick = next((i for i in items if i != sel0), None)
    await pg.evaluate(f"document.querySelector('#bList .brief-item[data-id=\"{pick}\"]').click()")
    bm = await wait_state(pg, 'map', 3000)
    sel1 = await pg.evaluate("__m1.menu().sel")
    add('C7', br and len(items) == n and bm and sel1 == pick, f"briefings list: {len(items)} of the campaign's {n} missions, picking '{pick}' -> map with it selected={sel1 == pick}")
    # a second visit to each step: no second event
    await click(pg, 'bBriefs'); await wait_state(pg, 'brief', 3000)
    other = next((i for i in items if i not in (sel0, pick)), None)
    await pg.evaluate(f"document.querySelector('#bList .brief-item[data-id=\"{other}\"]').click()"); await wait_state(pg, 'map', 3000)
    await click(pg, 'bHome'); await wait_state(pg, 'home', 4000)
    await click(pg, 'bStart'); await wait_state(pg, 'map', 5000)
    if HAS_064:
        steps = [e[1] for e in await evs(pg, 'menu_step')]
        names = [s.get('step') for s in steps]
        want = ['title', 'start', 'map', 'briefings', 'card']
        ok = names == want and all(s.get('link') == 'plain' for s in steps) and steps[2].get('mission') == 'm1' and steps[4].get('mission') == pick
        add('C23', ok, f"plain link, each step twice: {names} (link {set(s.get('link') for s in steps)}, map {steps[2].get('mission') if len(steps) > 2 else '-'}, card {steps[4].get('mission') if len(steps) > 4 else '-'})")
    keys = await pg.evaluate("['begin','skipAhead','state','sim','cur','report','toMap','setLang','setDev'].filter(k => typeof window.__m1[k] !== 'function')")
    add('C25', not keys, f"__m1 missing: {keys or 'none'}")
    await evs(pg); done('plain_flow', errs); await ctx.close()

async def case_settings(browser):
    ctx, pg, errs = await new_page(browser, PHONE)
    await load(pg, '?play&internal=1')
    await tap_start(pg, PHONE)
    await pg.evaluate("__m1.toMap()"); await wait_state(pg, 'map', 4000)
    await click(pg, 'bOpts2'); await wait_state(pg, 'opts', 3000)
    await click(pg, 'segAuto'); s1 = (await pg.evaluate(SAVE))['scheme']
    await click(pg, 'bSound3'); m1 = (await pg.evaluate(SAVE))['muted']
    await click(pg, 'bSound3'); m2 = (await pg.evaluate(SAVE))['muted']
    await pg.evaluate("(() => { const m = document.getElementById('vMusic'); m.value = 40; m.dispatchEvent(new Event('input')); m.dispatchEvent(new Event('change')); })()")
    v = (await pg.evaluate(SAVE))['vol']
    await click(pg, 'langAr'); la = [await pg.evaluate("__m1.lang()"), (await pg.evaluate(SAVE))['lang']]
    await click(pg, 'langEn'); le = await pg.evaluate("__m1.lang()")
    await click(pg, 'bDev'); d1 = [(await text(pg, 'bDev')).strip(), (await pg.evaluate(SAVE))['dev']]
    await click(pg, 'bDev'); d2 = (await pg.evaluate(SAVE))['dev']
    add('C9', s1 == 'auto' and m1 is True and m2 is False and la == ['ar', 'ar'] and le == 'en' and d1 == ['Developer: on', True] and d2 is False,
        f"fire mode saved {s1}; sound off/on saved {m1}/{m2}; music volume saved {v}; Arabic {la}, English {le}; Developer {d1} then {d2}")
    sv = await pg.evaluate(SAVE)
    want = ['scheme', 'muted', 'vol', 'lang', 'dev', 'best', 'prog', 'last', 'fpsTip']
    add('C18', all(k in sv for k in want) and sv['prog']['m1']['runs'] >= 1, f"save keys {sorted(sv.keys())}; m1 runs {sv['prog']['m1']['runs']}")
    await click(pg, 'bErase'); e1 = (await text(pg, 'bErase')).strip()
    await click(pg, 'bErase'); e2 = (await text(pg, 'bErase')).strip()
    runs = (await pg.evaluate(SAVE))['prog']['m1']['runs']
    add('C9', e1 == 'Tap again to erase' and e2 == 'Progress erased' and runs == 0, f"erase: '{e1}' then '{e2}', m1 runs after {runs}")
    await evs(pg); done('settings', errs); await ctx.close()

async def case_pause(browser):
    ctx, pg, errs = await new_page(browser, PHONE)
    await load(pg, '?play&internal=1')
    await tap_start(pg, PHONE)
    # the page out of sight
    await pg.evaluate("Object.defineProperty(document, 'hidden', { configurable: true, get: () => true }); document.dispatchEvent(new Event('visibilitychange'))")
    hid = await wait_state(pg, 'pause', 2000)
    await pg.evaluate("Object.defineProperty(document, 'hidden', { configurable: true, get: () => false }); document.dispatchEvent(new Event('visibilitychange'))")
    await pg.wait_for_timeout(400)
    still = await pg.evaluate("__m1.state()")
    add('C17', hid and still == 'pause', f"in a mission: hidden -> pause={hid}, back -> {still}")
    btns = {b: await vis(pg, b) for b in ('bResume', 'bRestart', 'bSkip', 'bQuit', 'segHold2', 'segAuto2', 'vMusic2', 'vSfx2', 'vVoice2', 'bSound')}
    devoff = [await vis(pg, 'bBoxes'), await pg.evaluate(f"{VIS}(document.querySelector('#pPause .rep.dev'))")]
    await pg.screenshot(path=f'{OUT}/C10_pause.png')
    await pg.evaluate("__m1.setDev(true)"); await pg.wait_for_timeout(150)
    devon = [await vis(pg, 'bBoxes'), await pg.evaluate(f"{VIS}(document.querySelector('#pPause .rep.dev'))")]
    await pg.evaluate("__m1.setDev(false)")
    await click(pg, 'bResume'); r = await wait_state(pg, 'play', 3000)
    z0 = await pg.evaluate("__m1.sim().zone")
    await pg.evaluate("__m1.pause()"); await wait_state(pg, 'pause', 2000)
    await click(pg, 'bSkip'); sk = await wait_state(pg, 'play', 4000)
    z1, skipped = await pg.evaluate("[__m1.sim().zone, __m1.run().skipped]")
    await pg.evaluate("__m1.pause()"); await wait_state(pg, 'pause', 2000)
    await click(pg, 'bRestart'); rs = await wait_state(pg, 'play', 4000)
    await pg.evaluate("__m1.pause()"); await wait_state(pg, 'pause', 2000)
    await click(pg, 'bQuit'); q = await wait_state(pg, 'map', 5000)
    add('C10', all(btns.values()) and devoff == [False, False] and devon == [True, True] and r and sk and z1 == z0 + 1 and skipped and rs and q,
        f"buttons shown={all(btns.values())} {'' if all(btns.values()) else btns}; dev-only hidden/shown {devoff}/{devon}; resume={r}; skip zone {z0}->{z1} practice={skipped}; restart={rs}; quit -> map={q}")
    # the menu music stops with the page out of sight
    await pg.wait_for_timeout(500)
    await pg.evaluate("window.__sp = []; Object.defineProperty(document, 'hidden', { configurable: true, get: () => true }); document.dispatchEvent(new Event('visibilitychange'))")
    sp = await pg.evaluate("window.__sp")
    add('C17', True in sp, f"on the map: hidden -> menu music paused={True in sp}")
    await evs(pg); done('pause', errs); await ctx.close()

async def case_over(browser):
    ctx, pg, errs = await new_page(browser, PHONE)
    await load(pg, '?play&internal=1')
    await tap_start(pg, PHONE)
    z0 = await pg.evaluate("__m1.sim().zone")
    ov = await game_over(pg)
    info = await pg.evaluate(f"""({{ h: document.getElementById('hOver').textContent.trim(), kept: document.getElementById('overKept').textContent.trim(),
      dial: !!document.getElementById('overDial') && {VIS}('overDial'), cont: {RECT}('bContinue'), acts: {RECT}('pOver'),
      cs: (() => {{ const a = getComputedStyle(document.getElementById('bContinue')), b = getComputedStyle(document.getElementById('bQuit2'));
        return {{ cH: parseFloat(a.minHeight), cF: a.fontSize, qT: document.getElementById('bQuit2').textContent.trim(), qU: b.textDecorationLine, qF: b.fontSize, qB: b.borderTopWidth }}; }})() }})""")
    await pg.screenshot(path=f'{OUT}/C11_continue.png')
    box = info['cont']
    await pg.touchscreen.tap(box[0] + box[2] / 2, box[1] + box[3] / 2)
    back = await wait_state(pg, 'play', 5000)
    z1 = await pg.evaluate("__m1.sim().zone")
    add('C11', ov and info['h'] == 'Continue?' and info['kept'].startswith('Score kept') and info['dial'] and back and z1 == z0,
        f"over={ov}, '{info['h']}', '{info['kept']}', dial={info['dial']}, Continue -> play={back} in zone {z0}->{z1}")
    cs = info['cs']
    if HAS_064:
        wide = box[2] >= 0.8 * min(info['acts'][2], 9999)
        add('C12', cs['cH'] >= 60 and cs['cF'] == '26px' and cs['qT'].lower() == 'mission map' and 'underline' in cs['qU'] and cs['qF'] == '14px',
            f"Continue {round(box[2])}x{round(box[3])}px font {cs['cF']}; way out '{cs['qT']}' {cs['qU']} {cs['qF']} border {cs['qB']}")
    # the countdown runs out: the map
    await game_over(pg)
    t = await wait_state(pg, 'map', 16000)
    add('C11', t, f"countdown ran out -> map={t}")
    await pg.evaluate("__m1.begin('m1', 0)"); await wait_state(pg, 'play', 5000); await pg.wait_for_timeout(500)
    await game_over(pg)
    await click(pg, 'bQuit2'); q = await wait_state(pg, 'map', 5000)
    add('C11', q, f"way out -> map={q}")
    await evs(pg); done('over', errs); await ctx.close()

async def case_results(browser):
    ctx, pg, errs = await new_page(browser, PHONE, init=(SHEET,))
    await load(pg, '?play&internal=1')
    await tap_start(pg, PHONE)
    await clear_mission(pg)
    r = {k: (await text(pg, k)).strip() for k in ('rTime', 'rPar', 'rTotal')}
    btn = {b: await vis(pg, b) for b in ('bToMap', 'bAgain', 'bShare2')}
    badges = await pg.evaluate("document.getElementById('rBadges') ? document.getElementById('rBadges').children.length : -1")
    sv = await pg.evaluate(SAVE)
    await pg.screenshot(path=f'{OUT}/C13_results.png')
    add('C13', all(r.values()) and all(btn.values()) and sv['prog']['m1']['cleared'] and sv['prog']['m1'].get('best') is not None,
        f"results {r}, buttons shown={all(btn.values())}, badges {badges}, cleared + best saved={bool(sv['prog']['m1'].get('best'))}")
    if HAS_064:
        q0 = [await vis(pg, 'fbQ'), (await text(pg, 'fbQ')).strip()]
        await click(pg, 'bLike')
        a = await pg.evaluate(f"[document.getElementById('bLike').classList.contains('picked'), {VIS}('fbQ'), {VIS}('fbThanks'), document.getElementById('fbThanks').textContent.trim()]")
        await click(pg, 'bDislike')
        dis = await pg.evaluate("document.getElementById('bDislike').classList.contains('picked')")
        await click(pg, 'bFbX')
        op = await pg.evaluate("window.__opened.slice(-1)[0] || ''")
        tw = urllib.parse.unquote(op.split('text=', 1)[1]) if 'text=' in op else ''
        fb = [e[1] for e in await evs(pg, 'feedback')]
        add('C14', q0 == [True, 'Like this mission?'] and a == [True, False, True, 'Thanks!'] and not dis and op.startswith('https://x.com/intent/tweet?text=') and tw.startswith('@BabAlYemenGame Feedback on '),
            f"'{q0[1]}' -> like picked, 'Thanks!' {a}; second vote ignored={not dis}; X post text '{tw}'")
        add('C24', fb == [{'mission': 'm1', 'choice': 'like'}, {'mission': 'm1', 'choice': 'x'}], f"feedback events {fb}")
    await click(pg, 'bShare2'); await pg.wait_for_timeout(300)
    shared = await pg.evaluate("window.__shared.slice(-1)[0] || {}")
    sc = [e[1] for e in await evs(pg, 'share_click')]
    add('C15', shared.get('url') == LIVE + '?play&utm_source=share&utm_medium=results&utm_content=m1', f"results share sheet link {shared.get('url')}")
    add('C22', sc and sc[-1] == {'from': 'results', 'mission': 'm1', 'how': 'sheet'}, f"share_click {sc[-1] if sc else None}")
    # play again, then a new results screen starts with a fresh vote
    await click(pg, 'bAgain'); ag = await wait_state(pg, 'play', 5000)
    await pg.wait_for_timeout(500)
    await clear_mission(pg)
    if HAS_064:
        fresh = await pg.evaluate(f"[{VIS}('fbQ'), document.getElementById('bLike').classList.contains('picked')]")
        add('C14', fresh == [True, False], f"next results screen: question back={fresh[0]}, nothing picked={not fresh[1]}")
    add('C13', ag, f"Play again -> play={ag}")
    # Advance: the map, and the new clear gets its stamp once
    await click(pg, 'bToMap'); mp = await wait_state(pg, 'map', 5000)
    try:
        await pg.wait_for_function("__m1.prog().m1.stamped === true", timeout=12000); stamped = True
    except Exception:
        stamped = False
    await pg.wait_for_timeout(600)
    await pg.screenshot(path=f'{OUT}/C7_map_after_clear.png')
    await pg.evaluate("__m1.toHome()"); await wait_state(pg, 'home', 3000)
    await pg.evaluate("__m1.toMap()"); await wait_state(pg, 'map', 3000)
    rv = await pg.evaluate("__m1.menu().rvId")
    add('C13', mp, f"Advance -> map={mp}")
    add('C7', stamped and rv is None, f"new clear stamped={stamped}, no second stamp on the next visit={rv is None}")
    await evs(pg); done('results', errs); await ctx.close()

async def case_practice(browser):
    ctx, pg, errs = await new_page(browser, PHONE)
    await load(pg, '?internal=1')
    await pg.evaluate("__m1.begin('m1', 1)"); await wait_state(pg, 'play', 5000); await pg.wait_for_timeout(600)
    await clear_mission(pg)
    p = (await pg.evaluate(SAVE))['prog']['m1']
    add('C13', p.get('cleared') and not p.get('best'), f"run from a checkpoint: cleared={p.get('cleared')}, best={p.get('best')}")
    await evs(pg); done('practice', errs); await ctx.close()

async def case_share_home(browser):
    # the share sheet
    ctx, pg, errs = await new_page(browser, PHONE, init=(SHEET,))
    await load(pg, '?internal=1'); await wake(pg, PHONE)
    await click(pg, 'bShare'); await pg.wait_for_timeout(300)
    sh = await pg.evaluate("window.__shared[0] || {}")
    sc = [e[1] for e in await evs(pg, 'share_click')]
    add('C15', sh.get('url') == LIVE + '?play&utm_source=share&utm_medium=home' and bool(sh.get('text')), f"home share sheet link {sh.get('url')}")
    add('C22', sc == [{'from': 'home', 'how': 'sheet'}], f"share_click {sc}")
    done('share_sheet', errs); await ctx.close()
    # no sheet: the link copied
    ctx, pg, errs = await new_page(browser, DESK, ua=None, touch=False, init=(NOSHEET, CLIP_OK))
    await load(pg, '?internal=1')
    await pg.mouse.click(DESK['width'] // 2, DESK['height'] // 2)
    await pg.wait_for_timeout(500)
    await click(pg, 'bShare'); await pg.wait_for_timeout(300)
    clip = await pg.evaluate("window.__clip[0] || ''")
    lab1 = (await text(pg, 'bShare')).strip()
    await pg.wait_for_timeout(2900)
    lab2 = (await text(pg, 'bShare')).strip()
    sc = [e[1] for e in await evs(pg, 'share_click')]
    add('C15', clip.endswith(LIVE + '?play&utm_source=share&utm_medium=home') and lab1 == 'Link copied' and lab2 == 'Share' and sc and sc[-1].get('how') == 'copy',
        f"no sheet: copied '...{clip[-60:]}', button '{lab1}' then '{lab2}', how={sc[-1].get('how') if sc else None}")
    done('share_copy', errs); await ctx.close()
    # no sheet and no clipboard: WhatsApp
    ctx, pg, errs = await new_page(browser, DESK, ua=None, touch=False, init=(NOSHEET, CLIP_FAIL))
    await load(pg, '?internal=1')
    await pg.mouse.click(DESK['width'] // 2, DESK['height'] // 2)
    await pg.wait_for_timeout(500)
    await click(pg, 'bShare'); await pg.wait_for_timeout(600)
    op = await pg.evaluate("window.__opened.slice(-1)[0] || ''")
    add('C15', op.startswith('https://wa.me/?text=') and urllib.parse.unquote(op).endswith(LIVE + '?play&utm_source=share&utm_medium=home'), f"no sheet, no clipboard: opens '{op[:40]}...'")
    await evs(pg); done('share_whatsapp', errs); await ctx.close()

async def fps_run(browser, ua, touch, label):
    vp = PHONE if touch else DESK
    ctx, pg, errs = await new_page(browser, vp, ua=ua, touch=touch, init=(FAKE30,))
    await load(pg, '?play&internal=1')
    await tap_start(pg, vp, touch)
    keep = "(() => { const s = __m1.sim(); if (s) for (const k in s) { const o = s[k]; if (o && typeof o === 'object' && 'inv' in o && 'lives' in o) o.inv = 999; } })()"
    await pg.evaluate("window.__fake30 = true")
    tips = []
    for _ in range(40):
        await pg.evaluate(keep)
        await pg.wait_for_timeout(250)
        tips = [h for h in await pg.evaluate("window.__hints") if 'smoother' in h]
        if tips: break
    saved = (await pg.evaluate(SAVE)).get('fpsTip')
    second = None
    if touch:
        await pg.evaluate("window.__fake30 = false")
        await load(pg, '?internal=1')
        await pg.evaluate("__m1.begin('m1', 0)"); await wait_state(pg, 'play', 5000)
        await pg.evaluate("window.__fake30 = true")
        for _ in range(24):
            await pg.evaluate(keep); await pg.wait_for_timeout(250)
        second = [h for h in await pg.evaluate("window.__hints") if 'smoother' in h]
    done(f'fps {label}', errs); await ctx.close()
    return tips, saved, second

async def case_fps(browser):
    t, s, again = await fps_run(browser, ANDROID, True, 'android')
    add('C16', t == ['Battery saver on? Turning it off makes the game smoother'] and s is True and again == [], f"Android: tip {t}, saved={s}, after a reload {again}")
    t, s, again = await fps_run(browser, IPHONE, True, 'iphone')
    add('C16', t == ['Low Power Mode on? Turning it off makes the game smoother'] and s is True and again == [], f"iPhone: tip {t}, saved={s}, after a reload {again}")
    t, s, _ = await fps_run(browser, None, False, 'desktop')
    add('C16', t == [] and not s, f"computer: tip {t}, saved={s}")

async def case_old_save(browser):
    ctx, pg, errs = await new_page(browser, PHONE, init=(OLD_SAVE,))
    await load(pg, '?internal=1')
    info = await pg.evaluate("""({ m1: __m1.prog().m1, scheme: document.getElementById('segAuto').getAttribute('aria-checked'), sound: document.getElementById('bSound3').innerText.trim() })""")
    await load(pg, '?play&internal=1')
    st = await pg.evaluate("__m1.state()")
    add('C18', info['m1'].get('cleared') and info['m1'].get('runs') == 3 and info['scheme'] == 'true' and info['sound'] == 'Sound is off' and st == 'map' and not errs,
        f"an older save: m1 cleared={info['m1'].get('cleared')} runs={info['m1'].get('runs')}, auto fire={info['scheme']}, '{info['sound']}', ?play -> {st}, errors {len(errs)}")
    await evs(pg); done('old_save', errs); await ctx.close()

async def case_lang(browser):
    for loc, want in (('ar-SA', 'ar'), ('en-US', 'en'), ('fr-FR', 'en')):
        ctx, pg, errs = await new_page(browser, PHONE, locale=loc)
        await load(pg, '?internal=1')
        got = await pg.evaluate("__m1.lang()")
        add('C19', got == want, f"browser {loc} -> {got}")
        if loc == 'ar-SA':
            await wake(pg, PHONE)
            await click(pg, 'bOpts'); await wait_state(pg, 'opts', 3000)
            await click(pg, 'langEn')
            await load(pg, '?internal=1')
            kept = await pg.evaluate("__m1.lang()")
            add('C19', kept == 'en', f"browser ar-SA, English picked, after a reload -> {kept}")
        done(f'lang {loc}', errs); await ctx.close()

SCAN = """(root => { const out = []; const r = typeof root === 'string' ? document.getElementById(root) : root; if (!r) return out;
  const w = document.createTreeWalker(r, NodeFilter.SHOW_TEXT); let n;
  while ((n = w.nextNode())) { const t = n.nodeValue.trim(); if (!t) continue; const e = n.parentElement;
    if (!e || e.closest('.vh,[data-fixed],script,style,svg')) continue; if (e.getClientRects().length === 0) continue;
    if (getComputedStyle(e).visibility === 'hidden') continue;
    const latin = t.match(/[A-Za-z][A-Za-z0-9'’-]*/g); if (latin) out.push([t.slice(0, 70), latin]); }
  return out; })"""
ALLOWED = {'X', '4x4'}

async def case_arabic(browser):
    ctx, pg, errs = await new_page(browser, PHONE, locale='ar-SA', init=(SHEET,))
    await load(pg, '?internal=1')
    found = {}
    async def scan(name, root):
        res = await pg.evaluate(f"{SCAN}('{root}')")
        bad = [r for r in res if any(w not in ALLOWED for w in r[1])]
        found[name] = bad
    await wake(pg, PHONE); await scan('home', 'pHome'); await pg.screenshot(path=f'{OUT}/C20_home_ar.png')
    await click(pg, 'bStart'); await wait_state(pg, 'map', 5000); await pg.wait_for_timeout(600); await scan('map + card', 'pMap')
    await pg.screenshot(path=f'{OUT}/C20_map_ar.png')
    await click(pg, 'bBriefs'); await wait_state(pg, 'brief', 3000); await scan('briefings', 'pBrief'); await click(pg, 'bBriefBack'); await wait_state(pg, 'map', 3000)
    await click(pg, 'bOpts2'); await wait_state(pg, 'opts', 3000); await scan('options', 'pOpts'); await pg.screenshot(path=f'{OUT}/C20_options_ar.png'); await click(pg, 'bBack'); await wait_state(pg, 'map', 3000)
    await pg.evaluate("__m1.begin('m1', 0)"); await wait_state(pg, 'play', 5000); await pg.wait_for_timeout(500)
    await pg.evaluate("__m1.pause()"); await wait_state(pg, 'pause', 2000); await scan('pause', 'pPause'); await pg.screenshot(path=f'{OUT}/C20_pause_ar.png')
    await click(pg, 'bResume'); await wait_state(pg, 'play', 3000)
    await game_over(pg); await scan('continue', 'pOver'); await pg.screenshot(path=f'{OUT}/C20_continue_ar.png')
    box = await pg.evaluate(f"{RECT}('bContinue')"); await pg.touchscreen.tap(box[0] + box[2] / 2, box[1] + box[3] / 2); await wait_state(pg, 'play', 5000)
    await clear_mission(pg); await scan('results', 'pDone'); await pg.screenshot(path=f'{OUT}/C20_results_ar.png')
    if HAS_064:
        await click(pg, 'bFbX')
        op = await pg.evaluate("window.__opened.slice(-1)[0] || ''")
        tw = urllib.parse.unquote(op.split('text=', 1)[1]) if 'text=' in op else ''
        found['X post text'] = [] if tw.startswith('@BabAlYemenGame ') and not re.search(r'[A-Za-z]', tw.replace('@BabAlYemenGame', '')) else [[tw, []]]
    await click(pg, 'bShare2'); await pg.wait_for_timeout(300)
    st = await pg.evaluate("(window.__shared.slice(-1)[0] || {}).text || ''")
    found['share text'] = [] if st and not re.search(r'[A-Za-z]', st) else [[st[:70], []]]
    bad = {k: v for k, v in found.items() if v}
    add('C20', not bad, f"Arabic screens with English left: {json.dumps(bad, ensure_ascii=False) if bad else 'none'}")
    await evs(pg); done('arabic', errs); await ctx.close()

def static_checks():
    # every literal key given to T() has its Arabic line
    line = next(l for l in SRC.split('\n') if l.startswith('var LANG_AR = '))
    ar = json.loads(line[len('var LANG_AR = '):].rstrip().rstrip(';'))
    keys, fallbacks = set(), set()
    for m in re.finditer(r'(?<![A-Za-z0-9_$.])T\(', SRC):
        j, depth = m.end(), 1
        while j < len(SRC) and depth > 0:
            c = SRC[j]
            if c in '\'"':
                k, s = j + 1, []
                while SRC[k] != c:
                    if SRC[k] == '\\': s.append(SRC[k + 1]); k += 2
                    else: s.append(SRC[k]); k += 1
                before = SRC[m.end():j].rstrip()
                lit = ''.join(s)
                if re.search(r'(===|!==|==|!=)$', before): pass          # a value compared with, not words shown
                elif before.endswith('||'): fallbacks.add(lit)          # shown only when a mission leaves its own words out
                else: keys.add(lit)
                j = k + 1; continue
            if c == '(' or c == '[': depth += 1
            elif c == ')' or c == ']': depth -= 1
            elif c == ',' and depth == 1: break
            j += 1
    missing = sorted(k for k in keys if k and k not in ar and re.search(r'[A-Za-z]', k))
    fb_missing = sorted(k for k in fallbacks if k not in ar)
    add('C20', not missing, f"T() keys without Arabic: {missing if missing else 'none'} (of {len(keys)})")
    # each built mission's own words on its results screen
    notes = re.findall(r"freedNote: '((?:[^'\\]|\\.)*)'", SRC)
    nm = [n for n in notes if n not in ar]
    add('C20', not nm, f"missions' freed-hostage lines without Arabic: {nm or 'none'} (of {len(notes)}); English-only fallback if a mission has none: {fb_missing or 'none'}")
    # the analytics calls: present, and each behind a guard
    want = ['mission_start', 'game_over', 'continue', 'skip_ahead', 'mission_complete', 'mission_leave', 'share_click', 'social_click'] + (['menu_step', 'feedback'] if HAS_064 else [])
    absent = [e for e in want if f"HM.track('{e}'" not in SRC]
    hooks = [h for h in ('HM.boot(', 'HM.sim(') if h not in SRC]
    unguarded = [l.strip()[:80] for l in SRC.split('\n') if re.search(r'(?<![A-Za-z0-9_$])HM\.(track|boot|sim)\(', l) and 'window.HM' not in l]
    hmgame = 'window.HMgame = { ctx:' in SRC and 'now: function' in SRC
    add('C21', not absent and not hooks and not unguarded and hmgame, f"calls missing {absent + hooks or 'none'}; unguarded {unguarded or 'none'}; HMgame={hmgame}")

async def main():
    static_checks()
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for c in (case_play_new, case_play_desktop, case_play_upright, case_play_returning, case_params, case_plain_flow, case_settings,
                  case_pause, case_over, case_results, case_practice, case_share_home, case_fps, case_old_save, case_lang, case_arabic):
            try:
                await c(browser)
            except Exception as e:
                errors.setdefault(c.__name__, []).append('TEST CRASH: ' + str(e)[:300])
        await case_play_upright(browser, 'ar-SA')
        await browser.close()
    # the events seen while running (everything in the game's own flows)
    flow = ['mission_start', 'mission_complete', 'mission_leave', 'game_over', 'continue', 'skip_ahead']
    add('C21', all(e in events_seen for e in flow), f"seen while playing: {sorted(e for e in events_seen)}")
    srv.shutdown()
    lines = []
    for n in range(1, 26):
        cid = f'C{n}'
        marked = cid in ('C12', 'C14', 'C23', 'C24')
        if marked and not HAS_064:
            status = 'FAIL (missing)' if REQUIRE_064 else 'n/a (0.10.64 lines not in this build)'
            lines.append(f"{cid}: {status}"); continue
        got = checks.get(cid, [])
        status = 'PASS' if got and all(ok for ok, _ in got) else ('NOT CHECKED' if not got else 'FAIL')
        lines.append(f"{cid}: {status}")
        for ok, note in got: lines.append(f"    {'ok ' if ok else 'BAD'} {note}")
    errs = {k: v for k, v in errors.items() if v}
    lines.append(f"page errors: {json.dumps(errs, ensure_ascii=False) if errs else 'none'}")
    head = f"build {BUILD} ({'with' if HAS_064 else 'without'} the 0.10.64 lines)"
    print(head); print('\n'.join(lines))
    with open(f'{OUT}/signoff.txt', 'w', encoding='utf-8') as f: f.write(head + '\n' + '\n'.join(lines) + '\n')

asyncio.run(main())
