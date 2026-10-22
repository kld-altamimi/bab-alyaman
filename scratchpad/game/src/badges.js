// the two badges, Ace and Liberator, drawn here in pixels (Khaled, 19 Oct). Ace: a gold medal with a jambiya struck on
// it, on a ribbon in the flag's red, white and black. Liberator: a teal shield with a broken chain. A badge not won is
// its silhouette, so each is known by its outline alone: the round medal on two tails, and the pointed shield.
// size 'big' is 28x30 (results screen and mission card), 'mini' is 9x10 (the campaign map).
var Badges = (function () {
  var C = { o: '#2a1404', gd: '#b86a00', g: '#ffc22e', gh: '#ffe08a', e: '#6a3400', r: '#c8281c', w: '#f4f0e6', k: '#1a1a20',
            n: '#04050c', t: '#1f6f6b', th: '#3fb3a2', td: '#12443f', c: '#eef1ff', cd: '#8f99c4', sil: '#1e223c', sl: '#4a5290' };
  var cache = {};
  function G(w, h) {
    var a = new Array(w * h);
    return { w: w, h: h, a: a,
      set: function (x, y, c) { if (x >= 0 && y >= 0 && x < w && y < h) a[y * w + x] = c; },
      get: function (x, y) { return x >= 0 && y >= 0 && x < w && y < h ? a[y * w + x] : undefined; } };
  }
  function paint(g, pat, ox, oy, map) {
    pat.forEach(function (row, y) { for (var x = 0; x < row.length; x++) { var ch = row.charAt(x); if (map[ch]) g.set(ox + x, oy + y, map[ch]); } });
  }
  function aceBig() {
    var g = G(28, 30), x, y;
    for (y = 17; y <= 29; y++) {                       // the two ribbon tails, behind the medal
      var off = Math.floor((y - 17) / 3), cols = [C.o, C.r, C.r, C.w, C.k, C.k, C.o];
      for (var i = 0; i < 7; i++) {
        var lx = 5 - off + i, rx = 16 + off + i;
        if (y === 29 && (i === 0 || i === 3 || i === 6)) continue;      // the swallowtail notch
        g.set(lx, y, cols[i]); g.set(rx, y, cols[i]);
      }
    }
    for (y = 0; y < 26; y++) for (x = 0; x < 28; x++) {   // the medal
      var dx = x + 0.5 - 14, dy = y + 0.5 - 12.5, d = Math.sqrt(dx * dx + dy * dy);
      if (d > 12.2) continue;
      var c = d > 11.2 ? C.o : (d > 9.9 ? C.gd : C.g);
      if (d > 7 && d <= 9.9 && dx + dy < -6) c = C.gh;
      if (d > 7.5 && d <= 9.9 && dx + dy > 7) c = C.gd;
      if (d > 9.9 && d <= 11.2 && dx + dy < -8) c = C.g;
      g.set(x, y, c);
    }
    // the jambiya in its sheath, struck into the gold: the wide flat pommel, the grip, the belt collar, and the sheath
    // sweeping down and hooking up at its tip
    var jam = ['.eeeeeeee...', '..eeeeee....', '....ee......', '....ee......', '....ee......', '..eeeeee....', '...eeee.....', '...eeee.....', '...eeeee....', '....eeeee...', '.....eeeee.e', '......eeeeee', '.......eeee.'];
    paint(g, jam, 8, 5, { e: C.e });
    jam.forEach(function (row, yy) { for (var xx = 0; xx < row.length; xx++) if (row.charAt(xx) === 'e') { var q = g.get(9 + xx, 6 + yy); if (q === C.g || q === C.gh) g.set(9 + xx, 6 + yy, C.gd); } });
    [[9, 5], [10, 5], [10, 10], [11, 11], [11, 12], [11, 13], [12, 14], [13, 15]].forEach(function (p) { if (g.get(p[0], p[1]) === C.e) g.set(p[0], p[1], C.o); });
    return g;
  }
  function libBig() {
    var g = G(28, 30), x, y, m = [];
    for (y = 0; y < 30; y++) for (x = 0; x < 28; x++) {
      var hw = y <= 15 ? 12.5 : 12.5 - (y - 15) * 0.93, inside = y >= 1 && Math.abs(x + 0.5 - 14) <= hw && !(y === 1 && (x === 1 || x === 26));
      m[y * 28 + x] = inside;
    }
    function inM(x, y) { return x >= 0 && y >= 0 && x < 28 && y < 30 && m[y * 28 + x]; }
    function edge(x, y, r) { for (var a = -r; a <= r; a++) for (var b = -r; b <= r; b++) if (Math.abs(a) + Math.abs(b) <= r && !inM(x + a, y + b)) return true; return false; }
    for (y = 0; y < 30; y++) for (x = 0; x < 28; x++) if (inM(x, y)) {
      var c = edge(x, y, 1) ? C.n : (edge(x, y, 2) ? C.g : (edge(x, y, 3) ? C.gd : (x < 10 && y < 18 ? C.th : (x + y > 32 ? C.td : C.t))));
      g.set(x, y, c);
    }
    // a chain coming down from the top left, broken in the middle with a spark where it parted
    var ring = ['.cc.', 'c..c', 'c..c', '.cc.'];
    [[5, 5], [8, 8], [15, 15], [18, 18]].forEach(function (p, k) {
      paint(g, ring, p[0], p[1], { c: C.c });
      g.set(p[0] + 3, p[1] + 1, C.cd); g.set(p[0] + 3, p[1] + 2, C.cd); g.set(p[0] + 1, p[1] + 3, C.cd); g.set(p[0] + 2, p[1] + 3, C.cd);
    });
    g.set(11, 11, C.c); g.set(12, 12, C.cd);            // the end of the upper half, snapped
    g.set(15, 14, C.c);                                  // and the lower half's open link
    [[13, 12], [14, 11], [12, 14], [14, 13], [15, 12], [13, 14]].forEach(function (p, k) { g.set(p[0], p[1], k % 2 ? C.gh : C.g); });
    return g;
  }
  function aceMini() {
    var g = G(9, 10), x, y;
    paint(g, ['.........', '.........', '.........', '.........', '.........', '.........', '.........', '.rw..wk..', '.rw..wk..', '.........'], 0, 0, { r: C.r, w: C.w, k: C.k });
    for (y = 1; y < 8; y++) for (x = 1; x < 8; x++) { var dx = x + 0.5 - 4.5, dy = y + 0.5 - 4.2, d = Math.sqrt(dx * dx + dy * dy); if (d <= 3.4) g.set(x, y, d > 2.4 ? C.gd : C.g); }
    g.set(4, 3, C.e); g.set(4, 4, C.e); g.set(5, 5, C.e); g.set(3, 3, C.gh);
    return outline(g);
  }
  function libMini() {
    var g = G(9, 10);
    paint(g, ['.........', '.ggggggg.', '.gtttttg.', '.gtcttg..', '.gttcttg.', '.gtttttg.', '..gtttg..', '...gtg...', '....g....', '.........'], 0, 0, { g: C.g, t: C.t, c: C.c });
    g.set(6, 3, C.g); g.set(7, 3, C.g);
    return outline(g);
  }
  function outline(g) {     // a dark edge round the little ones, so they read on any part of the map
    var add = [];
    for (var y = 0; y < g.h; y++) for (var x = 0; x < g.w; x++) if (!g.get(x, y) && (g.get(x + 1, y) || g.get(x - 1, y) || g.get(x, y + 1) || g.get(x, y - 1))) add.push([x, y]);
    add.forEach(function (p) { g.set(p[0], p[1], C.n); });
    return g;
  }
  function draw(g, won) {
    var cv = document.createElement('canvas'); cv.width = g.w; cv.height = g.h;
    var cx = cv.getContext('2d'), x, y;
    for (y = 0; y < g.h; y++) for (x = 0; x < g.w; x++) {
      var c = g.get(x, y); if (!c) continue;
      if (!won) {
        var rim = !g.get(x + 1, y) || !g.get(x - 1, y) || !g.get(x, y + 1) || !g.get(x, y - 1);
        c = rim ? C.sl : C.sil;
      }
      cx.fillStyle = c; cx.fillRect(x, y, 1, 1);
    }
    return cv;
  }
  function get(kind, size, won) {
    var key = kind + size + (won ? 1 : 0);
    if (!cache[key]) cache[key] = draw(kind === 'ace' ? (size === 'mini' ? aceMini() : aceBig()) : (size === 'mini' ? libMini() : libBig()), won);
    return cache[key];
  }
  // a badge into a page: a canvas the page can scale up, crisp
  function into(node, kind, won) {
    var src = get(kind, 'big', won), cv = node.tagName === 'CANVAS' ? node : document.createElement('canvas');
    cv.width = src.width; cv.height = src.height;
    var c = cv.getContext('2d'); c.clearRect(0, 0, cv.width, cv.height); c.drawImage(src, 0, 0);
    return cv;
  }
  return { get: get, into: into };
})();
