# Bab al-Yaman — working rules for Claude

This repository is the **source of truth** for the game. The Claude artifact ("Strait Feel Prototype") is a preview
of these files, never the place where edits happen. If the artifact and the repo differ, the repo wins.

## Layout

- `index.html` — the entire game in one file: markup, CSS, all scripts, and the art (embedded as data URIs).
  Edit it in place; do not split it into modules or move the art out.
- `audio/` — ten MP3s the game fetches at runtime by relative path (`audio/<name>.mp3`). Keep the folder beside
  `index.html`; file names are referenced from the `AUDIO` manifest inside `index.html`.
- `analytics.js` — PostHog tracking. **Gameplay edits must not touch this file.** The game calls `window.HM` at a handful of
  points (`mission_start`, the simulation event tap in `react()`, `game_over`, `mission_complete`, `mission_leave`,
  and `quit` on tab-hide, plus `continue`, `skip_ahead` and `boot`). If a mission id, zone name or boss key is renamed, the event properties follow
  automatically — just keep those calls in place.

## Workflow for every change

1. Edit the repo files.
2. Republish the artifact from the repo files so Khaled can play it privately (for bosses or late zones he uses
   the mission's "start from" checkpoint dropdown; `window.__m1.begin(id, zone)` does the same from the console).
3. Iterate. **Do not push until Khaled says "push".**
4. On "push": commit to `main` with a one-line message describing the change. GitHub Pages deploys it to
   https://kld-altamimi.github.io/bab-alyaman/ within a couple of minutes. Bump `BUILD` near the top of the
   script in `index.html` so events carry the new build string.

## Checking a change

- `node --check` on the script block catches syntax errors; a headless Chromium run (`playwright`) with
  `window.__m1.begin('m1', 0)` confirms the game boots and starts a mission without page errors.
- The debug handle `window.__m1` exposes `state()`, `sim()`, `cur()`, `begin()`, `skipAhead()`, `report()`.

## Analytics events (see analytics.js)

The game calls `window.HM` at these points (one guarded line each; keep them when editing gameplay) and exposes a
read-only `window.HMgame` (`ctx()`: language, touch, fire mode, dev, muted; `now()`: state, mission, sim) that
analytics.js reads instead of the debug handle. `life_lost` in the simulation carries `why` (the cause of the hit).

| event | fired from | key properties |
|---|---|---|
| `boot` | `ready()` | load_ms (page start to title screen), since_script_ms |
| `audio_problem` | 20 s after boot, only if sound failed | audio_state, decoded |
| `mission_start` | `begin()` | mission, from_zone, from_checkpoint, run_number — starts a new run_id |
| `checkpoint` | sim event tap | mission, zone, zone_name, seconds, deaths |
| `life_lost` | sim event tap | + cause (e.g. "bullet", "heavy gun", "ladle", "roaster steam") |
| `boss_start`, `boss_dead` | sim event tap | + boss, fight_seconds |
| `game_over` | `gameOver()` | mission, zone, deaths, seconds |
| `continue` | `carryOn()` | same, run_continues goes up by one |
| `skip_ahead` | `skipAhead()` (pause menu) | where the player skipped from |
| `mission_complete` | `showResults()` | time, par, score, total, ace, liberator, practice, deaths |
| `mission_leave` | `stopGame()` | + status (play / over / clear) — ends the run |
| `quit` | tab hidden, on any screen | + state (home / map / play / pause / over …), run_seconds if mid-run |

Every event also carries: `build`, `run_id` and `run_continues` (while in a run), `lang`, `input` (touch / keyboard),
`fire_mode` (hold / auto), `orientation`, `dev` (filter `dev = true` out of real numbers) and `muted`.

Opening the game once with `?internal=1` marks that browser as internal (nothing sent; `?internal=0` undoes it) —
Khaled uses this on his own devices so test runs stay out of the numbers. Share links per channel as
`?utm_source=whatsapp` etc. so PostHog can tell channels apart (messaging apps strip the referrer).
