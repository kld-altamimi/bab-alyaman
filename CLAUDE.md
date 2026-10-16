# Bab al-Yaman — working rules for Claude

This repository is the **source of truth** for the game. The Claude artifact ("Strait Feel Prototype") is a preview
of these files, never the place where edits happen. If the artifact and the repo differ, the repo wins.

## Layout

- `index.html` — the entire game in one file: markup, CSS, all scripts, and the art (embedded as data URIs).
  Edit it in place; do not split it into modules or move the art out.
- `audio/` — ten MP3s the game fetches at runtime by relative path (`audio/<name>.mp3`). Keep the folder beside
  `index.html`; file names are referenced from the `AUDIO` manifest inside `index.html`.
- `analytics.js` — PostHog tracking. **Gameplay edits must not touch this file.** The game calls `window.HM` at six
  points (`mission_start`, the simulation event tap in `react()`, `game_over`, `mission_complete`, `mission_leave`,
  and `quit` on tab-hide). If a mission id, zone name or boss key is renamed, the event properties follow
  automatically — just keep those six calls in place.

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

| event | fired from | key properties |
|---|---|---|
| `mission_start` | `begin()` | mission, from_zone, from_checkpoint, run_number |
| `checkpoint`, `life_lost` | sim event tap | mission, zone, zone_name, seconds, deaths |
| `boss_start`, `boss_dead` | sim event tap | + boss, fight_seconds |
| `game_over` | `gameOver()` | mission, zone, deaths, seconds |
| `mission_complete` | `showResults()` | time, par, score, total, ace, liberator, practice, deaths |
| `mission_leave` | `stopGame()` | + status (play / over / clear) |
| `quit` | tab hidden mid-mission | + state (play / pause) |

Every event also carries `build`. Share links per channel as `?utm_source=whatsapp` etc. so PostHog can tell
channels apart (messaging apps strip the referrer).
