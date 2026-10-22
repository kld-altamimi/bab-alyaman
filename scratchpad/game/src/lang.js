// lang.js - the game's words in more than one language. English is written straight into the code; T('...') looks
// each string up in the current language's table (LANG_AR, embedded by build.py from src/lang_ar.json) and hands
// back the English when there is no entry. Templates carry {0}, {1}: T('Next stop: {0}.', [name]).
// The table is keyed by the English exactly as it appears in the code; a key is also tried in upper case, so a zone
// name drawn in capitals on a banner finds the same entry as the name on the card.
var Lang = (function () {
  'use strict';
  var code = 'en', tables = { ar: typeof LANG_AR !== 'undefined' ? LANG_AR : {} }, listeners = [];
  var AR_RE = /[؀-ۿ]/;
  function fill(s, args) {
    if (!args) return s;
    return s.replace(/\{(\d)\}/g, function (m, i) { return args[+i] == null ? '' : String(args[+i]); });
  }
  function look(tb, key) {
    var v = tb[key];
    if (v == null) v = tb[key.toUpperCase()];
    if (v == null && /^the /i.test(key)) v = tb[key.replace(/^the /i, 'The ')];
    return v;
  }
  function t(key, args) {
    key = String(key);
    var tb = tables[code];
    if (tb) {
      var v = look(tb, key);
      if (v == null) {
        // a piece of a sentence in the page keeps the spaces around it (" starts again with..."): look it up without them
        var m = /^(\s*)([\s\S]*?)(\s*)$/.exec(key);
        if (m[2] !== key && m[2]) { v = look(tb, m[2]); if (v != null) v = m[1] + v + m[3]; }
      }
      if (v != null) return fill(v, args);
    }
    return fill(key, args);
  }
  function has(key) { var tb = tables[code]; return !!(tb && (tb[key] != null || tb[String(key).toUpperCase()] != null)); }
  function set(c) {
    c = tables[c] ? c : 'en';
    if (c === code) return;
    code = c;
    for (var i = 0; i < listeners.length; i++) listeners[i](code);
  }
  // 'auto' means the browser's language: Arabic if it says so, else English
  function resolve(pref) {
    if (pref && pref !== 'auto') return tables[pref] ? pref : 'en';
    var nav = (navigator.languages && navigator.languages[0]) || navigator.language || '';
    return /^ar\b/i.test(nav) ? 'ar' : 'en';
  }
  return {
    t: t, has: has, set: set, resolve: resolve,
    code: function () { return code; },
    rtl: function () { return code === 'ar'; },
    isArabic: function (s) { return AR_RE.test(String(s)); },
    onChange: function (fn) { listeners.push(fn); }
  };
})();
function T(key, args) { return Lang.t(key, args); }
