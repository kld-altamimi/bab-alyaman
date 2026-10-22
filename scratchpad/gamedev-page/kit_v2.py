#!/usr/bin/env python3
"""Moves the Game Development page from page kit v1 to v2: the kit's v2 styles copied unchanged, the v2 skeleton (Needs
your decision with a count and a More (n) group, Done collapsed), and rows ranked with level chips."""
import re
import sys

P = sys.argv[1]
t = open(P, encoding='utf-8').read()

KIT_V2 = r''':root{--ink:#04050c;--bg:#10142c;--panel:#1e223c;--edge:#3c4278;--lav:#96a0dc;--text:#e8ecff;
--gold:#ffc22e;--red:#ff4030;--blue:#8fc0ff;--green:#5cc85c;--orange:#ff9a3c;--sand:#f0d9a0;
--f-pix:"Pixelify Sans","Courier New",monospace;--f-body:"Public Sans",system-ui,-apple-system,"Segoe UI",sans-serif;color-scheme:dark}
html,body{background:var(--ink)}
body{color:var(--text);font-family:var(--f-body);font-size:15px;line-height:1.45;padding-left:max(12px,env(safe-area-inset-left,0px));padding-right:max(12px,env(safe-area-inset-right,0px));padding-block:16px 40px}
.frame{max-width:64rem;margin:0 auto;background:var(--bg);border:3px solid var(--ink);box-shadow:inset 0 0 0 2px var(--edge);padding-bottom:20px}
.banner{padding:18px;background:#0b3a6e;border-bottom:3px solid var(--ink);display:grid;gap:4px}
.eyebrow{font-family:var(--f-pix);font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--orange)}
h1{font-family:var(--f-pix);font-weight:700;font-size:clamp(28px,5vw,40px);line-height:1;margin:0;color:var(--gold);text-shadow:3px 3px 0 var(--ink)}
.syncline,.lead{font-size:12px;color:var(--lav)} .lead{font-size:13px;margin:0 0 10px}
.body{padding:0 18px;display:grid;gap:24px;margin-top:18px}
h2{font-family:var(--f-pix);font-weight:600;font-size:22px;margin:0 0 4px} h2 small{font-family:var(--f-body);font-size:12px;color:var(--lav);font-weight:500;margin-left:8px}
.panel{background:var(--panel);border:2px solid var(--ink);box-shadow:inset 0 0 0 2px var(--edge);padding:12px 14px;min-width:0}
.rows{display:grid;gap:6px}
.rowbtn{width:100%;display:grid;grid-template-columns:auto auto auto 1fr auto auto;gap:10px;align-items:center;text-align:left;font:inherit;color:var(--text);background:var(--panel);border:2px solid var(--ink);box-shadow:inset 0 0 0 2px var(--edge);padding:9px 12px;cursor:pointer}
.rowbtn:hover{box-shadow:inset 0 0 0 2px var(--lav)}
.rank{font-family:var(--f-pix);font-size:16px;color:var(--lav);min-width:1.4em;text-align:right}
.lv{font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:1px 6px;white-space:nowrap;color:var(--ink)}
.lv.critical{background:var(--red)} .lv.high{background:var(--orange)} .lv.medium{background:var(--gold)} .lv.low{background:var(--lav)}
.st{font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:1px 6px;border:1px solid currentColor;white-space:nowrap}
.st.you{color:var(--gold)} .st.warn{color:var(--orange)} .st.moving{color:var(--blue)} .st.done{color:var(--green)} .st.no{color:var(--red)} .st.muted{color:var(--lav)}
.ctx{font-size:12px;color:var(--lav);white-space:nowrap} .tx{min-width:0;overflow-wrap:anywhere;font-weight:500} .car{color:var(--lav)}
@media (max-width:600px){.rowbtn{grid-template-columns:auto auto 1fr auto}.ctx,.rank{display:none}}
.box{background:var(--bg);border:2px solid var(--ink);border-top:0;box-shadow:inset 0 0 0 1px var(--edge);padding:10px 12px;display:grid;gap:6px;font-size:13px}
.box p{margin:0;overflow-wrap:anywhere} .box b{color:var(--lav);font-weight:600}
.acts{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.ib{font:inherit;font-size:14px;font-weight:700;line-height:1;min-width:30px;height:30px;padding:0 9px;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;border:2px solid var(--ink);color:var(--ink);background:var(--gold);box-shadow:inset -2px -2px 0 #b86a00}
.ib.no{background:var(--red);box-shadow:inset -2px -2px 0 #c8301a}
.ib.ghost{background:var(--panel);color:var(--lav);box-shadow:inset 0 0 0 1px var(--edge)}
.ib.opt{background:var(--panel);color:var(--text);box-shadow:inset 0 0 0 1px var(--edge);font-size:13px}
.ib:focus-visible,.rowbtn:focus-visible,textarea:focus-visible,.tog:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
textarea{font:inherit;font-size:14px;width:100%;box-sizing:border-box;min-height:52px;border:2px solid var(--ink);box-shadow:inset 0 0 0 1px var(--edge);background:var(--panel);color:var(--text);padding:7px 9px}
.done-line{font-weight:600;color:var(--green)} .done-line.no{color:var(--red)} .done-line span{color:var(--lav);font-weight:500}
.pending{background:#3c2a08;border:2px solid var(--ink);box-shadow:inset 0 0 0 2px var(--gold);color:var(--sand);padding:9px 12px;font-size:14px} .pending b{color:var(--gold)}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,9.5rem),1fr));gap:10px}
.tile span{font-size:12px;color:var(--lav)} .tile b{display:block;font-family:var(--f-pix);font-size:32px;font-weight:700;color:var(--gold);font-variant-numeric:tabular-nums}
.group-h,.tog{font-family:var(--f-pix);font-size:13px;color:var(--lav);text-transform:uppercase;letter-spacing:.06em;margin:12px 0 2px;background:none;border:0;padding:0;cursor:pointer;text-align:left}
.isdone .rowbtn{opacity:.6} .isdone .lv{background:var(--edge);color:var(--lav)}
.empty{border:2px dashed var(--edge);padding:12px;color:var(--lav);font-size:14px}
'''


def sub_once(old, new):
    global t
    if t.count(old) != 1:
        sys.exit('anchor found %d times: %r' % (t.count(old), old[:70]))
    t = t.replace(old, new)


sub_once('<meta name="bay-kit" content="v1">', '<meta name="bay-kit" content="v2">')
m = re.search(r'<style>\n(:root\{--ink:.*?)</style>', t, re.S)
if not m:
    sys.exit('kit style block not found')
t = t[:m.start(1)] + KIT_V2 + t[m.end(1):]
sub_once('.stack{display:grid;gap:10px;min-width:0}', '.stack{display:grid;gap:10px;min-width:0}\n.chips{display:inline-flex;gap:4px;flex-wrap:wrap}')
sub_once('''      <h2>Needs your decision</h2>
      <p class="lead">One line each; tap for details. Your answers reach the Game Development chat at your next message there.</p>
      <div class="rows" id="needs"><div class="empty">Loading…</div></div>''',
         '''      <h2>Needs your decision <small id="needs-n"></small></h2>
      <p class="lead">Most important first; tap for details. Your answers reach the Game Development chat at your next message there.</p>
      <div class="rows" id="needs"><div class="empty">Loading…</div></div>
      <button class="tog" type="button" id="more-tog" aria-expanded="false" hidden></button>
      <div class="rows" id="more" hidden></div>''')
sub_once('''      <div class="group-h" id="doneH">Done</div>
      <div class="rows isdone" id="done"><div class="empty">Loading…</div></div>''',
         '''      <button class="tog" type="button" id="done-tog" aria-expanded="false">▸ Done</button>
      <div class="rows isdone" id="done" hidden><div class="empty">Loading…</div></div>''')

# --- script: rows with rank and level; ranked Needs with More (n); Done collapsed; "Action on you"
sub_once("decide: ['you', 'Your call'], idea: ['you', 'Your call'], waiting: ['you', 'Your call'],",
         "decide: ['you', 'Your call'], idea: ['you', 'Your call'], waiting: ['you', 'Action on you'],")
sub_once("""  function row(id, chipHtml, ctx, tx, boxFn) {
    const isOpen = open.has(id);
    return '<div><button class="rowbtn" type="button" data-act="toggle" data-id="' + esc(id) + '" aria-expanded="' + isOpen + '">' +
      chipHtml + '<span class="ctx">' + esc(ctx || '') + '</span><span class="tx">' + esc(tx || '') + '</span><span class="car" aria-hidden="true">' + (isOpen ? '▾' : '▸') + '</span>' +
      '</button>' + (isOpen ? '<div class="box">' + boxFn() + '</div>' : '') + '</div>';
  }""",
         """  // (kit v2 order: rank · level · status · title · context · caret; rows without a rank or level keep empty cells)
  function row(id, chipHtml, ctx, tx, boxFn, rank, lv) {
    const isOpen = open.has(id);
    return '<div><button class="rowbtn" type="button" data-act="toggle" data-id="' + esc(id) + '" aria-expanded="' + isOpen + '">' +
      '<span class="rank">' + (rank != null ? esc(rank) : '') + '</span>' + (lv ? '<span class="lv ' + esc(lv) + '">' + esc(lv) + '</span>' : '<span></span>') +
      '<span class="chips">' + chipHtml + '</span><span class="tx">' + esc(tx || '') + '</span><span class="ctx">' + esc(ctx || '') + '</span><span class="car" aria-hidden="true">' + (isOpen ? '▾' : '▸') + '</span>' +
      '</button>' + (isOpen ? '<div class="box">' + boxFn() + '</div>' : '') + '</div>';
  }
  const stale = (it) => !!it.since && (Date.now() - Date.parse(it.since)) > 7 * 864e5;""")
sub_once("""  function itemRow(it, readonly) {
    const ans = answerFor(it.id), waiting = ans && !ans.picked_up;
    return row(it.id, waiting ? st('sent') : st(it.status), it.ctx, it.title, () => {
      let h = lines('What', it.details) + line('Why', it.why);""",
         """  function itemRow(it, readonly, ranked) {
    const ans = answerFor(it.id), waiting = ans && !ans.picked_up;
    const chip = (waiting ? st('sent') : st(it.status)) + (ranked && !waiting && stale(it) ? '<span class="st warn">Stale</span>' : '');
    return row(it.id, chip, it.ctx, it.title, () => {
      let h = lines('What it is', it.details) + line('Why', it.why) + line('Recommendation', it.rec) + line('Drawbacks', it.drawbacks) +
        line('Who does it', it.who) + line("How we'll know", it.how);""")
sub_once("""      if (errs[it.id]) h += '<p class="err" role="alert">' + esc(errs[it.id]) + '</p>';
      return h;
    });
  }""", """      if (errs[it.id]) h += '<p class="err" role="alert">' + esc(errs[it.id]) + '</p>';
      return h;
    }, ranked ? it.rank : null, ranked ? it.level : null);
  }""")
sub_once("""  function renderNeeds() {
    if (!S.items) { $('#needs').innerHTML = loading(); return; }
    const list = items('decide');
    $('#needs').innerHTML = list.length ? list.map((it) => itemRow(it)).join('') : empty('Nothing is waiting on you.');
  }""", """  let moreOpen = false, doneOpen = false;
  function renderNeeds() {
    if (!S.items) { $('#needs').innerHTML = loading(); return; }
    const list = items('decide').sort((a, b) => (a.rank == null ? 99 : a.rank) - (b.rank == null ? 99 : b.rank));
    const top = list.slice(0, 7), rest = list.slice(7);
    $('#needs-n').textContent = list.length ? String(list.length) : '';
    $('#needs').innerHTML = top.length ? top.map((it) => itemRow(it, false, true)).join('') : empty('Nothing is waiting on you.');
    const mt = $('#more-tog'), mr = $('#more');
    mt.hidden = !rest.length; mt.textContent = (moreOpen ? '▾' : '▸') + ' More (' + rest.length + ')'; mt.setAttribute('aria-expanded', String(moreOpen));
    mr.hidden = !rest.length || !moreOpen; mr.innerHTML = moreOpen ? rest.map((it) => itemRow(it, false, true)).join('') : '';
  }""")
sub_once("""  function renderDone() {
    if (!S.items) { $('#done').innerHTML = loading(); return; }
    const list = items('done');
    $('#doneH').textContent = 'Done (' + list.length + ')';
    $('#done').innerHTML = list.length ? list.map((it) => itemRow(it, true)).join('') : empty('Nothing finished yet.');
  }""", """  function renderDone() {
    const list = S.items ? items('done') : [], t = $('#done-tog'), d = $('#done');
    t.textContent = (doneOpen ? '▾' : '▸') + ' Done (' + list.length + ')'; t.setAttribute('aria-expanded', String(doneOpen));
    d.hidden = !doneOpen;
    if (doneOpen) d.innerHTML = !S.items ? loading() : (list.length ? list.map((it) => itemRow(it, true, false)).join('') : empty('Nothing finished yet.'));
  }
  $('#more-tog').addEventListener('click', () => { moreOpen = !moreOpen; render(); });
  $('#done-tog').addEventListener('click', () => { doneOpen = !doneOpen; render(); });""")
open(P, 'w', encoding='utf-8').write(t)
print('kit v2 applied')
