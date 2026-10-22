// menu.js - the home screen and the campaign map, drawn into the game's own picture at the game's own size.
// It draws and it answers questions (where is this mission, what is under this point, what state is the campaign in);
// what happens next is main.js's business. The campaign is a graph of roads (campaign.js): missions are named by id.
var Menu = (function () {
  'use strict';
  var R = null, A = null, MAP = null, cx = null, W = 468, H = 216;
  var GOLD = '#ffc22e', INK = '#10101c', NAVY = '#10142c', LAV = '#96a0dc';
  var BY = {}, PREV = {};

  function init(render, atlas) {
    R = render; A = atlas; MAP = atlas.menu.map;
    CAMPAIGN.forEach(function (m) { BY[m.id] = m; PREV[m.id] = []; });
    CAMPAIGN.forEach(function (m) { m.next.forEach(function (n) { PREV[n].push(m.id); }); });
  }
  function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }
  function mission(id) { return BY[id]; }
  function before(id) { return PREV[id] || []; }

  // ------------------------------------------------------------------ where each mission stands
  // cleared | open (built, and a road to it is open) | soon (a road to it is open, it is not built yet) |
  // locked (no road to it open yet: you can see where it is and what it is called) | secret (the same, for the one
  // mission the map does not name)
  function statuses(prog) {
    var out = {};
    CAMPAIGN.forEach(function (m) {
      var p = prog[m.id] || {}, ins = PREV[m.id], open = ins.length === 0;
      for (var i = 0; i < ins.length; i++) if ((prog[ins[i]] || {}).cleared) open = true;
      if (!open) out[m.id] = m.secret ? 'secret' : 'locked';
      else if (!m.built) out[m.id] = 'soon';
      else out[m.id] = p.cleared ? 'cleared' : 'open';
    });
    return out;
  }
  // where Yazeed stands: the first mission he can play and has not cleared; failing that, the last one he cleared
  function here(st, last) {
    for (var i = 0; i < CAMPAIGN.length; i++) if (st[CAMPAIGN[i].id] === 'open') return CAMPAIGN[i].id;
    if (last && st[last] === 'cleared') return last;
    for (var j = CAMPAIGN.length - 1; j >= 0; j--) if (st[CAMPAIGN[j].id] === 'cleared') return CAMPAIGN[j].id;
    return CAMPAIGN[0].id;
  }
  function nodeAt(x, y, cam, camY) {
    var best = null, bd = 15 * 15;
    CAMPAIGN.forEach(function (m) {
      var n = MAP.nodes[m.id], dx = x + cam - n[0], dy = y + (camY || 0) - n[1], d = dx * dx + dy * dy;
      if (d < bd) { bd = d; best = m.id; }
    });
    return best;
  }
  // the camera that puts a mission in the middle of what can be seen (vis: how much of the picture's width is not under a panel)
  function camFor(id, vis) {
    var n = MAP.nodes[id];
    return { x: clamp(Math.round(n[0] - vis / 2), 0, MAP.w - W), y: clamp(Math.round(n[1] - H / 2 + 8), 0, MAP.h - H) };
  }
  // keys: along the campaign a stage at a time (keeping to the road you are on where there is a choice), or across a fork
  function stageOf(m) { return m.stage || 7; }
  function stageStep(id, dir) {
    var m = BY[id], s = stageOf(m) + dir, near = dir > 0 ? m.next : PREV[id], pick = null;
    for (var i = 0; i < near.length; i++) if (stageOf(BY[near[i]]) === s) { pick = near[i]; break; }
    if (!pick) for (var j = 0; j < CAMPAIGN.length; j++) if (stageOf(CAMPAIGN[j]) === s) { pick = CAMPAIGN[j].id; break; }
    return pick || id;
  }
  function laneStep(id, dir) {
    var s = stageOf(BY[id]), same = CAMPAIGN.filter(function (m) { return stageOf(m) === s; });
    if (same.length < 2) return id;
    var k = 0;
    for (var i = 0; i < same.length; i++) if (same[i].id === id) k = i;
    return same[(k + dir + same.length) % same.length].id;
  }

  // ------------------------------------------------------------------ small drawing helpers
  function fill(c, x, y, w, h) { cx.fillStyle = c; cx.fillRect(Math.round(x), Math.round(y), w, h); }
  function scaled(name, x, y, k, alpha) {
    var f = A.frames[name];
    if (!f) return;
    var w = Math.round(f[2] * k), h = Math.round(f[3] * k);
    if (alpha != null && alpha < 1) cx.globalAlpha = alpha;
    cx.drawImage(R.image('atlas'), f[0], f[1], f[2], f[3], Math.round(x - f[4] * k), Math.round(y - f[5] * k), w, h);
    cx.globalAlpha = 1;
  }
  function plate(x, y, w, h) {
    fill('rgba(16,20,44,0.86)', x, y, w, h);
    fill(LAV, x, y, w, 1); fill(LAV, x, y, 1, h);
    fill('#3c4278', x, y + h - 1, w, 1); fill('#3c4278', x + w - 1, y, 1, h);
  }
  // corner brackets round a point, as a gunsight does
  function brackets(x, y, r, c) {
    var L = 4;
    [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(function (s) {
      var bx = Math.round(x + s[0] * r), by = Math.round(y + s[1] * r);
      fill(INK, bx - (s[0] > 0 ? L : 0) - 1, by - 1, L + 2, 3);
      fill(INK, bx - 1, by - (s[1] > 0 ? L : 0) - 1, 3, L + 2);
      fill(c, bx - (s[0] > 0 ? L - 1 : 0), by, L, 1);
      fill(c, bx, by - (s[1] > 0 ? L - 1 : 0), 1, L);
    });
  }

  // ------------------------------------------------------------------ the home screen
  // o: { t (ticks on this screen), coarse, best (number or null), cleared, total, build }
  function home(o) {
    cx = R.ctx(); W = R.width();
    var mid = Math.floor(W / 2), t = o.t;
    // a band of shade behind the lettering, so it reads against the sky whatever the sky is doing
    // in Arabic the title is «باب اليمن», with BAB AL-YEMEN kept small under it (Khaled's pick, 17 Oct)
    var lname = Lang.rtl() && A.frames.menu_logo_ar ? 'menu_logo_ar' : 'menu_logo', lf = A.frames[lname], ar = lname === 'menu_logo_ar';
    var under = 18 + lf[3], tagY = ar ? under + 27 : 62, shade = ar ? 116 : 96;
    var g = cx.createLinearGradient(0, 0, 0, shade);
    g.addColorStop(0, 'rgba(10,12,28,0.55)'); g.addColorStop(0.75, 'rgba(10,12,28,0.25)'); g.addColorStop(1, 'rgba(10,12,28,0)');
    cx.fillStyle = g; cx.fillRect(0, 0, W, shade);
    // the logo drops in and settles; then, now and then, a glint runs along it
    var k = clamp(t / 24, 0, 1), back = 1 + 2.2 * Math.pow(k - 1, 3) + 1.2 * Math.pow(k - 1, 2), drop = o.calm ? 0 : Math.round((1 - back) * -70);
    R.spr(lname, mid, 18 + drop);
    if (ar) R.text('b_org', 'BAB AL-YEMEN', mid, under + 4 + drop, 'c');
    if (!o.calm && t > 40 && (t % 300) < 22) {
      var f = lf, gx = mid - f[4] + ((t % 300) / 22) * (f[2] + 30) - 15;
      cx.save(); cx.beginPath(); cx.rect(mid - f[4] + 3, 18 + 3, f[2] - 6, f[3] - 10); cx.clip();
      cx.globalAlpha = 0.55; cx.fillStyle = '#ffffff';
      cx.beginPath(); cx.moveTo(gx, 18); cx.lineTo(gx + 6, 18); cx.lineTo(gx - 6, 18 + f[3]); cx.lineTo(gx - 12, 18 + f[3]); cx.fill();
      cx.restore(); cx.globalAlpha = 1;
    }
    if (t > 16) R.text('m_lav', T('Yazeed and Salem against the Zanabeel'), mid, tagY, 'c');
    // the prompt, the way an arcade cabinet does it
    if (t > 30 && (t % 60) < 42) R.text('b_org', T(o.woke ? (o.coarse ? 'TAP TO START' : 'PRESS START') : (o.coarse ? 'TAP TO START' : 'PRESS ANY KEY')), mid, 140, 'c');
    // what has been done so far, and which build this is
    // what has been done so far (nothing until something has)
    var line = (o.cleared ? T('{0} OF {1} MISSIONS CLEARED', [o.cleared, o.total]) : '') + (o.best ? (o.cleared ? '    ' : '') + T('SCORE {0}', [o.best]) : '');
    if (line) R.text('s_lav', line, mid, 158, 'c');
    if (o.build) R.text('s_lav', 'V' + o.build, W - 5, 4, 'r');
    // the game's X account, as an arcade cabinet credits its maker: a quiet line in the corner (Khaled, 19 Oct)
    if (o.social && t > 30) {
      R.text('s_lav', T('FOLLOW US'), W - 6, H - 30, 'r');
      var hw = R.textW('m_org', 'x.com/babalyemengame');
      R.text('m_org', 'x.com/babalyemengame', W - 6, H - 21, 'r');
      if (o.hot) { cx.fillStyle = '#ffc22e'; cx.fillRect(W - 6 - hw, H - 11, hw, 1); }
    }
  }

  // ------------------------------------------------------------------ the campaign map
  // o: { t, cam, camY, sel, prog, last, reveal: { id, t } or null, calm }
  // The reveal is the minute after a first clear: CLEAR is stamped on the mission, the roads out of it are marked in gold,
  // and the places they lead to come out of the shade.
  function map(o) {
    cx = R.ctx(); W = R.width();
    var t = o.t, cam = Math.round(o.cam), camY = Math.round(o.camY || 0), st = statuses(o.prog), rv = o.reveal, rt = rv ? rv.t : -1, i, n, m;
    var shakeX = 0;
    if (rt >= 30 && rt < 38 && !o.calm) shakeX = (rt % 2 ? 1 : -1) * (38 - rt > 4 ? 2 : 1);
    // during the reveal the places beyond the new clear show as they were, until their moment comes
    var show = {}, fresh = {};
    CAMPAIGN.forEach(function (q) { show[q.id] = st[q.id]; });
    if (rv) BY[rv.id].next.forEach(function (nid) { fresh[nid] = true; if (rt < 112) show[nid] = BY[nid].secret ? 'secret' : 'locked'; });
    cam -= shakeX;
    cx.drawImage(R.image('map'), cam, camY, W, H, 0, 0, W, H);
    cx.save();
    cx.translate(-cam, -camY);
    // the sea catching the sun
    for (i = 0; i < MAP.sea.length; i++) {
      var sp = MAP.sea[i], ph = (t + i * 53) % 150;
      if (ph < 10 && sp[0] > cam - 4 && sp[0] < cam + W + 4 && sp[1] > camY - 4 && sp[1] < camY + H + 4) {
        cx.globalAlpha = ph < 5 ? 0.9 : 0.5;
        fill('#e8fbff', sp[0], sp[1], 1, 1);
        if (ph > 2 && ph < 8) { fill('#e8fbff', sp[0] - 1, sp[1], 3, 1); fill('#e8fbff', sp[0], sp[1] - 1, 1, 3); }
        cx.globalAlpha = 1;
      }
    }
    // a dhow working its way up the Red Sea, and another along the Gulf of Aden
    var dt = (t * 0.05) % 420, dxp = 104 - dt * 0.19, dyp = 452 - dt;
    if (dyp > 20) R.spr('menu_dhow', Math.round(dxp), Math.round(dyp));
    var dt2 = (t * 0.04 + 200) % 520;
    R.spr('menu_dhow', Math.round(200 + dt2), Math.round(452 - dt2 * 0.22), true);
    // the seas, the far shore, the sands and the one big city that is not on the road
    cx.globalAlpha = 0.6;
    R.text('s_lav', T('RED SEA'), 34, 236, 'c');
    R.text('s_lav', T('GULF OF ADEN'), 360, 452, 'c');
    R.text('s_lav', T('ERITREA'), 30, 396, 'c');
    R.text('s_lav', T('DJIBOUTI'), 96, 468, 'c');
    R.text('s_lav', T('RAMLAT AL-SABATAYN'), 452, 48, 'c');
    cx.globalAlpha = 0.85;
    R.text('s_lav', T('ADEN'), 330, 410, 'l');
    cx.globalAlpha = 1;
    R.spr('menu_coffee', 470, 300, false, 0.9);         // somebody put his cup down on the map
    R.spr('menu_compass', 24, 44);
    // the roads: gold out of every mission cleared, a faint dotted line where nobody has been yet
    CAMPAIGN.forEach(function (a, ai) {
      a.next.forEach(function (bid, k) {
        var b = BY[bid];
        if (b.secret && show[bid] === 'secret') return;          // (the map does not show the way there)
        var open = show[a.id] === 'cleared', upto = 1;
        if (rv && rv.id === a.id) { open = rt >= 50; upto = rt >= 50 ? clamp((rt - 50) / 60, 0, 1) : 1; }
        leg(MAP.nodes[a.id], MAP.nodes[bid], (a.bow && a.bow[k]) || 0.14, open, upto, t);
      });
    });
    // signposts where the road forks
    CAMPAIGN.forEach(function (q) {
      if (!q.sign) return;
      var nn = MAP.nodes[q.id], wob = rv && rv.id === q.id && rt >= 96 && rt < 130 ? Math.round(Math.sin((rt - 96) / 2.2) * 2 * (1 - (rt - 96) / 34)) : 0;
      R.spr('menu_sign', nn[0] + q.sign[0] + wob, nn[1] + q.sign[1]);
    });
    // the places themselves: in colour where the road is open, in the shade where it is not, and nothing where it is secret
    CAMPAIGN.forEach(function (q) {
      var s = show[q.id], nn = MAP.nodes[q.id];
      if (s === 'secret') return;
      var x = nn[0] + q.land[0], y = nn[1] + q.land[1];
      if (s === 'locked') { R.spr('menu_land_' + q.id + '_x', x, y); return; }
      if (fresh[q.id] && rt >= 112 && rt < 136) {
        R.spr('menu_land_' + q.id + '_x', x, y);
        R.spr('menu_land_' + q.id, x, y, false, (rt - 112) / 24);
      } else R.spr('menu_land_' + q.id, x, y);
    });
    CAMPAIGN.forEach(function (q) {
      if (!q.hq) return;
      var nn = MAP.nodes[q.id];
      R.spr('menu_scorpion', nn[0] + q.hq[0], nn[1] + q.hq[1]);
      if ((t >> 4) % 2 === 0) R.text('s_org', T('HQ'), nn[0] + q.hq[0] + 9, nn[1] + q.hq[1] - 3);
    });
    // the badges, with the stage number on them
    CAMPAIGN.forEach(function (q) {
      var s = show[q.id], nn = MAP.nodes[q.id], bad = s === 'cleared' ? 'clear' : (s === 'open' ? 'open' : 'lock');
      var bob = s === 'open' && !o.calm && (t >> 4) % 2 ? -1 : 0, num = q.stage ? String(q.stage) : 'q';
      var pop = fresh[q.id] && rt >= 112 && rt < 122 ? 1 + 0.6 * (1 - (rt - 112) / 10) : 1;
      if (s === 'secret') cx.globalAlpha = 0.7;
      if (pop > 1) scaled('menu_badge' + num + '_' + bad, nn[0], nn[1], pop);
      else R.spr('menu_badge' + num + '_' + bad, nn[0], nn[1] + bob);
      cx.globalAlpha = 1;
      if (s === 'secret' || s === 'soon' || s === 'locked') R.spr('menu_padlock', nn[0] + 7, nn[1] + 6);
      if (s === 'cleared') R.spr('menu_tick', nn[0] + 7, nn[1] + 6);
      label(q, s, t, fresh[q.id] ? rt : -1, o.prog && o.prog[q.id]);
    });
    // CLEAR, stamped on each mission done (and, the first time, stamped while you watch)
    CAMPAIGN.forEach(function (q) {
      if (st[q.id] !== 'cleared') return;
      var nn = MAP.nodes[q.id], sm = q.stamp, kk = 1, al = 1;
      if (rv && rv.id === q.id) {
        if (rt < 24) return;
        var u = clamp((rt - 24) / 8, 0, 1);
        kk = 2.4 - 1.4 * u; al = 0.35 + 0.65 * u;
      }
      scaled('menu_stamp', nn[0] + sm[0], nn[1] + sm[1], kk, al);
    });
    // the selected one: brackets that breathe
    if (o.sel && MAP.nodes[o.sel]) {
      n = MAP.nodes[o.sel];
      var ss = show[o.sel];
      brackets(n[0], n[1], 10 + ((t >> 4) % 2), ss === 'open' ? GOLD : (ss === 'cleared' ? '#a8f088' : '#e8ecff'));
    }
    // Yazeed, a little piece standing on the mission he is at, hopping now and then
    var h = MAP.nodes[here(st, o.last)], phs = t % 120, hb = o.calm || phs > 16 ? 0 : -Math.round(Math.sin(phs / 16 * Math.PI) * 4);
    cx.globalAlpha = 0.45; fill(INK, h[0] - 4, h[1] - 8, 9, 2); cx.globalAlpha = 1;
    R.spr('menu_yazeed', h[0], h[1] - 8 + hb);
    cx.restore();
    // the heading
    var head = T('CAMPAIGN MAP'), cl = 0, tot = 0;
    CAMPAIGN.forEach(function (q) { if (!q.secret) tot++; if (st[q.id] === 'cleared') cl++; });
    var tail = T('{0}/{1} CLEARED', [cl, tot]), hw = R.textW('s_lav', head) + R.textW('s_org', tail) + 22;
    plate(4, 4, hw, 13);
    if (Lang.rtl()) { var tx = R.text('s_org', tail, 9, 7); R.text('s_lav', head, tx + 8, 7); }    // read from the right: the heading first
    else { var hx = R.text('s_lav', head, 9, 7); R.text('s_org', tail, hx + 8, 7); }
  }

  // a road between two missions: a dotted curve, bowed to one side (bow > 0 bends it to the right of the way it runs)
  function leg(a, b, bowK, open, upto, t) {
    var mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, dx = b[0] - a[0], dy = b[1] - a[1], L = Math.sqrt(dx * dx + dy * dy);
    var bow = bowK * L, qx = mx - dy / L * bow, qy = my + dx / L * bow;
    var steps = Math.max(8, Math.floor(L / 5)), k, march = open ? (t >> 3) % 2 : 0;
    for (k = 2; k <= steps - 2; k++) {
      var u = k / steps;
      if (u > upto + 0.001) break;
      var x = (1 - u) * (1 - u) * a[0] + 2 * (1 - u) * u * qx + u * u * b[0];
      var y = (1 - u) * (1 - u) * a[1] + 2 * (1 - u) * u * qy + u * u * b[1];
      if (open) {
        fill(INK, x - 1, y - 1, 4, 4);
        fill((k + march) % 2 ? GOLD : '#fff0a0', x, y, 2, 2);
      } else if (k % 2 === 0) {
        cx.globalAlpha = 0.7; fill(NAVY, x - 1, y - 1, 3, 3); fill('#aab1d8', x, y, 1, 1); cx.globalAlpha = 1;
      }
    }
  }

  // a mission's name on the map, and under it, smaller in effect (fainter), the place it is at; SOON under both while
  // its road is open and it is not built yet. The secret one is only ???.
  function label(m, s, t, rt, pg) {
    var n = MAP.nodes[m.id], lb = m.label, x = n[0] + lb[0], y = n[1] + lb[1], secret = s === 'secret';
    var name = secret ? '???' : T(m.name).toUpperCase(), place = secret ? '' : T(m.place).toUpperCase();
    var font = s === 'open' ? 's_org' : 's_lav', faded = secret || s === 'locked';
    var w = R.textW(font, name), w2 = place ? R.textW('s_lav', place) : 0, lh = R.lineH('s_lav', name + place, 8);
    function at(ww) { return lb[2] === 'c' ? x - Math.floor(ww / 2) : (lb[2] === 'r' ? x - ww : x); }
    cx.globalAlpha = faded ? 0.72 : 1;
    R.text(font, name, at(w), y);
    if (place) { cx.globalAlpha = faded ? 0.5 : 0.78; R.text('s_lav', place, at(w2), y + lh); }
    cx.globalAlpha = 1;
    if (s === 'soon' && ((t >> 5) % 2 === 0 || rt >= 0)) R.text('s_org', T('SOON'), at(R.textW('s_org', T('SOON'))), y + (place ? 2 * lh : lh));
    // its two badges, won or only their outlines, once it is open to be played
    if (m.built && pg && (s === 'open' || s === 'cleared')) {
      var ba = Badges.get('ace', 'mini', !!pg.ace), bl = Badges.get('lib', 'mini', !!pg.lib), by = y + (place ? 2 * lh : lh) - 1;
      var bx = at(ba.width + bl.width + 1);
      cx.drawImage(ba, bx, by); cx.drawImage(bl, bx + ba.width + 1, by);
    }
  }

  // the ad's ?play link, for someone new: the first mission's own picture under one prompt, nothing else (no logo,
  // no menu, no story; Khaled, 21 Oct). The controls are on show too: on a touch screen the thumbs themselves (CSS),
  // with keys a line of them under the prompt.
  function gate(o) {
    cx = R.ctx(); W = R.width();
    var mid = Math.floor(W / 2), t = o.t;
    var g = cx.createLinearGradient(0, 100, 0, 172);
    g.addColorStop(0, 'rgba(10,12,28,0)'); g.addColorStop(0.5, 'rgba(10,12,28,0.5)'); g.addColorStop(1, 'rgba(10,12,28,0)');
    cx.fillStyle = g; cx.fillRect(0, 100, W, 72);
    if (o.wait) R.text('m_lav', T('Loading sound'), mid, 132, 'c');
    // (with keys the prompt goes up a little, so that it and the keys line both clear Yazeed's hat)
    else if (o.calm || (t % 60) < 44) R.text('b_org', T(o.coarse ? 'TAP TO PLAY' : 'PRESS ANY KEY TO PLAY'), mid, o.coarse ? 130 : 112, 'c');
    if (!o.coarse && !o.wait) R.text('m_lav', T('ARROWS MOVE    Z FIRE    X JUMP    C BOMB'), mid, 132, 'c');
  }
  return { init: init, home: home, gate: gate, map: map, statuses: statuses, here: here, nodeAt: nodeAt, camFor: camFor, mission: mission, before: before,
           stageStep: stageStep, laneStep: laneStep, mapW: function () { return MAP.w; }, mapH: function () { return MAP.h; } };
})();
