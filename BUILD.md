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
3. `python3 bab_out/m1_src/build.py --bump --local-fonts` (add `--no-souq` while the Souq stays off the live game; add
   `--ibb` only for Ibb's test builds: its level, code and sheet, its lines, and the map's road from Taiz to it).
4. Test: `node scratchpad/game/tools/unit.js` (and the other `unit*.js`), then the browser tests in `bab_out/m1_src/`.
5. Copy the built `index.html` to a test branch, never straight to `main`; `main` changes only when Khaled says push.

## Notes
- Before every build, read the must-still-work checklist (`claude/topics/game-development-checklist.md` in the
  project); `python3 tools/signoff.py <site folder> <out> --strict` on `main` checks it on the built site folder.
- Build numbers are shared across branches: use the highest number seen plus one.
- Since 23 Oct only the Game Development chat changes the game, here in the sources. A change made straight in
  `index.html` must be ported into these sources before the next build, or the build wipes it.
- Art: `scratchpad/game/tools/export_art.py` redraws every sheet (`art/out/`, `gen/atlas.json`) from the scripts; it
  is deterministic, so after an art change compare the sheets with the last ones and check only the frames you meant
  moved (24 Oct: the Roaster's edits changed its 33 `rst_*` frames and nothing else).
- Ibb (Mission 4, being built in stages, 24 Oct): `tools/ibb_sprites.py --sheet` writes its sheet (`art/out/ibb.png`,
  `gen/ibb_sprites.json`); `snd/add_speech.py` writes the Spokesman's lines to `audio/speech_ibb.mp3` (a file the game
  fetches only with Ibb, as it does a mission's music) and lists them in `gen/audio.json` (`speech.ibb`, each line with
  its mouth shapes); `tools/unit_ibb.js` checks the level (platforms against the painting, bots through the zones
  painted so far); `snap_ibb_z1.js`, `snap_ibb_z2.js` and `rt_ibb_z1.js` picture zones 1 and 2 and play zone 1. Its stage
  is painted zone by zone (Khaled plays each one): `mock/stage_ibb.py` (sky, mountains, the nearer hills as a `mid` layer)
  and a painter per zone (`mock/stage_ibb_z1.py`, `mock/stage_ibb_z2.py`; zone 2 also paints Jibla's town and its mosque
  as a `back` layer at 0.7, drawn before the play strips); `tools/export_ibb.py` writes the pictures (`art/out/i_*.png`)
  and `gen/stage_ibb.json`, which `build.py --ibb` packs; `mock/z1_look.py` and `mock/z2_look.py` picture a zone with its
  screens and people before it goes in, and `mock/mock_school.py` is the storyboard of zone 2's classrooms (a mock only).
