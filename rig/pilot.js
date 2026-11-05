function pilot(opt) {
  opt = opt || {};
  let flareWait = 0, rocketWait = 0;
  return function (s) {
    const h = s.heli, rt = X.route(s.L), c = X.ahead(rt, s.u), held = s.holdU != null && s.u >= s.holdU - 2;
    const lead = held ? 0 : Math.abs(c.dx) * s.viewW * F.LEAD + Math.abs(c.dy) * F.LEAD_UP + 40;
    // ahead along the route, and off to its left-hand side: above it going along (over the roofs), out from the rock going up
    // (going down, into the souq or under the bridge: along the route itself)
    const k = c.dy > 0.3 ? 0 : (opt.low ? -10 : 80) - 10 * Math.abs(c.dy);
    let tx = c.x + c.dx * lead + c.dy * k, ty = c.y + c.dy * lead - c.dx * k;
    if (held && Math.abs(c.dy) > Math.abs(c.dx)) ty -= 30;
    // in a fight: the gun reaches ahead and down, and down behind, but not up: keep them all ahead of it and under it
    // (left of the leftmost, over the highest)
    if (held) {
      let left = null, top = null;
      for (const e of s.enemies) if (e.alive && e.hostile && e.k !== 'drone' && e.st !== 'panic' && X.inView(s, e.x, e.y, 0)) { if (left === null || e.x < left) left = e.x; const t = e.y - e.h; if (top === null || t < top) top = t; }
      if (left !== null) tx = Math.max(s.cam + F.EDGE_X + 12, Math.min(tx, left - 90));
      if (top !== null) ty = Math.min(ty, top - 44);
      ty = Math.max(ty, s.camY + F.EDGE_T + 6);
    }
    // (something in the way ahead: go over it)
    for (let k = 1; k <= 4; k++) if (X.rockAt(s.L, h.x + Math.sign(tx - h.x || 1) * (F.HW + 12 * k), h.y + F.HB + 4)) { ty = Math.min(ty, h.y - 30); break; }
    let ax = Math.max(-1, Math.min(1, (tx - h.x) / 50)), ay = Math.max(-1, Math.min(1, (ty - h.y) / 40));
    // (stone overhead on the way up, a ledge over the nose or the tail: out from under it, to the side that is clear)
    if (ay < 0) {
      const over = dx => [-2, -8, -F.HT - 4, -F.HT - 12].some(dy => X.rockAt(s.L, h.x + dx, h.y + dy));
      const nose = over(F.HW + 2) || over(F.HW * 0.5), tail = over(-F.HW - 2) || over(-F.HW * 0.5);
      if (nose && !tail) ax = -1; else if (tail && !nose) ax = 1;
    }
    let jump = false, grenade = false;
    if (flareWait > 0) flareWait--; if (rocketWait > 0) rocketWait--;
    // flares in the last moments of a lock-on (they are still fresh when it fires), or at a missile on its way
    const threat = s.locking && s.lockT > (opt.lateFlares ? 90 : 30) || s.missiles.some(q => !q.decoy && Math.hypot(q.x - h.x, q.y - h.y) < 200);
    if (threat && flareWait <= 0 && !opt.noFlares) { jump = true; flareWait = 20; }
    // out of the way of a drone that has picked its moment, and of a missile with no flare to chase
    if (!opt.noDodge) {
      for (const e of s.enemies) if (e.alive && e.k === 'drone' && (e.st === 'tell' || e.st === 'dive')) { ay = e.y < h.y ? 1 : -1; if (h.y > s.camY + VH - 46) ay = -1; if (h.y < s.camY + 50) ay = 1; }
      for (const q of s.missiles) if (!q.decoy && Math.hypot(q.x - h.x, q.y - h.y) < 120 && (h.flareCd > 0 || q.kind === 'rpg')) ay = q.y < h.y ? 1 : -1;
      // out of the ring where a shell is coming down (a mortar's, the Castle Gun's flak)
      // (a shell marked near it: off to whichever side has least coming down on it; a shell right on it has no 'away')
      const shells = (s.shells || []).filter(q => q.t > -10);
      if (shells.some(q => Math.hypot(q.tx - h.x, q.ty - h.y) < (q.kind === 'flak' ? 30 : F.MORTAR_R) + 44)) {
        let best = null;
        for (const [dx, dy] of [[1, 0], [-1, 0], [0, -1], [0, 1], [0.7, -0.7], [-0.7, -0.7], [0.7, 0.7], [-0.7, 0.7]]) {
          const px = h.x + dx * 90, py = h.y + dy * 60;
          if (py < s.camY + F.EDGE_T + 4 || py > s.camY + VH - F.EDGE_B - 4 || px < s.cam + F.EDGE_X || px > s.cam + s.viewW - F.EDGE_X || X.rockAt(s.L, px, py)) continue;
          let danger = 0; for (const q of shells) danger += Math.max(0, 80 - Math.hypot(q.tx - px, q.ty - py));
          if (!best || danger < best.d) best = { dx, dy, d: danger };
        }
        if (best) { ax = best.dx; ay = best.dy; }
      }
    }
    if (!opt.noRockets && rocketWait <= 0 && s.enemies.some(e => e.alive && e.hostile && e.k === 'aa' && X.inView(s, e.x, e.y, -10) && Math.abs(e.y - 12 - h.y) < 40 && e.x > h.x)) { grenade = true; rocketWait = 30; }
    // on the aim stick: at the nearest thing the gun can reach (or nothing, and not firing); else FIRE held, and the gun finds its own
    if (opt.stick) {
      const m = X.muzzle(h);
      let best = null, bd = 1e9;
      for (const e of s.enemies) {
        if (!e.alive || !e.hostile || e.st === 'panic' || e.emerge > 0 || e.hidden || !X.inView(s, e.x, e.y - e.h / 2, -4)) continue;
        const low = e.k === 'sam' && e.covered;            // (his head over the parapet: last)
        const dx = e.x - m.x, dy = (low ? e.y - 10 : e.y - e.h * 0.55) - m.y, d = Math.hypot(dx, dy), a = Math.atan2(dy, dx);
        if (a < -F.GUN_UP || a > F.GUN_BACK || d > 520) continue;
        if (d * (low ? 2.5 : 1) < bd) { bd = d * (low ? 2.5 : 1); best = [dx / d, dy / d]; }
      }
      return { mx: 0, my: 0, ax: ax, ay: ay, fire: false, gun: !!best, gx: best ? best[0] : 0, gy: best ? best[1] : 0, jump: jump, grenade: grenade, auto: false };
    }
    return { mx: 0, my: 0, ax: ax, ay: ay, fire: true, jump: jump, grenade: grenade, auto: false };
  };
}
