# Bab al-Yemen — game sources

This branch holds the game's sources and build scripts. `main` holds what players get: the built `index.html`, the
`audio/` folder and `analytics.js`. The Game Development chat owns this branch and syncs it after each build
(`sync_sources.sh`). Repo rules: `CLAUDE.md` on `main`.

## Layout
The folders mirror the workspace they were written in, so the scripts' paths keep working:
- `scratchpad/game/src/` — the game, one file per module: `sim.js` (the deterministic simulation, 60 steps a second),
  `drive.js` (the 4x4), `fly.js` (the Apache), `boss.js`, `roaster.js`, `tailor.js`, the levels (`level*.js`),
  `campaign.js`, the renderers (`render*.js`), `audio.js`, `input.js`, `menu.js`, `main.js`, `lang.js` and
  `lang_ar.json` (the Arabic lines; keys are the exact English strings), `badges.js`.
- `scratchpad/game/gen/` — data the build reads: the atlas, fonts, audio manifest, ground and stage layouts.
- `scratchpad/game/art/out/` — the art sheets the build embeds (drawn by the Python scripts in `game/tools/` and `mock/`).
- `scratchpad/game/tools/` — art exporters (`export_*.py`, `*_sprites.py`) and tests: `unit*.js` (mechanics),
  `unit_taiz.js`, `bot.js` (a playing bot; `run()`, `smartBot()`, `fuzzBot()`), `sweep.js`, `fuzz.js`.
- `scratchpad/mock/` — stage painters and character sheets (Python, Pillow).
- `scratchpad/snd/` — the synthesiser: instruments, `voice.py` (the babble with subtitles), music and effects exports.
- `scratchpad/experiments/` — `baseline.js`, `baseline_mocha.js`: seeded bot runs whose end states guard against
  unintended changes.
- `scratchpad/refill/`, `scratchpad/taizmap/`, `scratchpad/gamedev-page/` — the checkpoint refill patch and its
  measurements, the Taiz Level Map tools, and the topic page.
- `bab_out/m1_src/` — `build.py` (writes the single-file `index.html`, art as lossless WebP data URIs; `version.json`
  holds the release and build numbers), `page.tpl.html`, `build_standalone.py`, browser tests `test_*.js` (Playwright)
  and picture scripts `snap_*.js`.

## Building
1. Run `./link_workspace.sh` once: it links the original workspace paths to this checkout.
2. Put the MP3s from `main`'s `audio/` into `/home/claude/bab_out/m1/audio/` (or rebuild them with `snd/`).
3. `python3 bab_out/m1_src/build.py --bump --local-fonts` (add `--no-souq` while the Souq stays off the live game).
4. Test: `node scratchpad/game/tools/unit.js` (and the other `unit*.js`), then the browser tests in `bab_out/m1_src/`.
5. Copy the built `index.html` to a test branch, never straight to `main`; `main` changes only when Khaled says push.

## Notes
- Before every build, check game-features' list of things that must keep working
  (`claude/topics/game-features-checklist.md` in the project; `tools/signoff.py` on `main` once 0.10.64 is live).
- Build numbers are shared across branches: use the highest number seen plus one.
- Other chats edit `index.html` on `main` directly. Port their changes into these sources before building, or the
  build wipes them.
