/* Bab al-Yaman — analytics (PostHog).
   The game calls into window.HM at a handful of moments; everything PostHog-specific lives here.
   Gameplay edits must not touch this file. If a mission id, zone name or boss key changes, the
   matching event properties change with it — nothing else. */
(function () {
  var KEY = 'phc_nGPyHPyJoK9oZbnAZQcMMCwhKTAJXVn8o5mQZ46JyWck';
  var HOST = 'https://eu.i.posthog.com';

  // PostHog loader (official snippet)
  !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty createPersonProfile opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing debug".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);

  // Internal-user kill switch: open the game once with ?internal=1 and this browser stops sending events
  // (?internal=0 turns it back on). Stored locally, per device.
  var internal = false;
  try {
    var q = /[?&]internal=([01])/.exec(window.location.search);
    if (q) localStorage.setItem('hm_internal', q[1]);
    internal = localStorage.getItem('hm_internal') === '1';
  } catch (e) {}
  if (internal) { window.HM = { track: function () {}, where: function () { return {}; }, sim: function () {}, internal: true }; return; }

  try {
    posthog.init(KEY, {
      api_host: HOST,
      person_profiles: 'identified_only', // players stay anonymous: cheaper events, no profiles
      autocapture: false,                 // a canvas game: clicks on it are noise
      capture_pageview: true,
      capture_pageleave: true
    });
  } catch (e) {}

  function track(name, props) {
    try {
      var p = props || {};
      if (window.BUILD) p.build = window.BUILD;
      if (window.posthog && posthog.capture) posthog.capture(name, p);
    } catch (e) {}
  }

  function zoneName(sim) {
    try { return sim.L.zones[sim.zone].name; } catch (e) { return undefined; }
  }
  function where(sim, cur) {
    return {
      mission: cur,
      zone: sim ? sim.zone : undefined,
      zone_name: sim ? zoneName(sim) : undefined,
      seconds: sim ? Math.round(sim.time) : undefined,
      deaths: sim && sim.stats ? sim.stats.deaths : undefined
    };
  }

  var bossT0 = 0;

  window.HM = {
    track: track,
    where: where,
    // one tap on the simulation's own event stream (called from react() in the game loop)
    sim: function (e, sim, cur) {
      switch (e.t) {
        case 'life_lost': track('life_lost', where(sim, cur)); break;
        case 'checkpoint': track('checkpoint', where(sim, cur)); break;
        case 'boss_intro':
          bossT0 = sim.time;
          var ps = where(sim, cur); ps.boss = e.k; track('boss_start', ps); break;
        case 'boss_dead':
          var pd = where(sim, cur); pd.boss = e.k; pd.fight_seconds = Math.round(sim.time - bossT0); track('boss_dead', pd); break;
      }
    }
  };

  // Abandonment: the tab hidden or closed mid-mission is the only reliable signal on mobile.
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState !== 'hidden') return;
    try {
      var m = window.__m1; if (!m) return;
      var st = m.state();
      if (st !== 'play' && st !== 'pause') return;
      var p = where(m.sim(), m.cur()); p.state = st;
      track('quit', p);
    } catch (e) {}
  });
})();
