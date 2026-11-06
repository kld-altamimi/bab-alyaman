# Bab al-Yemen — marketing tools

This branch (`marketing`) holds the tools the marketing work uses to make posts from the live game: film a mission,
letter it in the game's own hand, lay out pictures and cut reels. It shares nothing with `main`: the game is untouched
and nothing here deploys. The game's code stays game-development's; these tools only read the live build.

Owner: the "Game Marketing" chat in the Claude Project "Bab Al-yaman" (topic `marketing`). The daily run follows
[DAILY.md](DAILY.md).

## Set up a fresh machine

```bash
git -C /home/claude/bab-alyaman fetch origin marketing:refs/remotes/origin/marketing
git -C /home/claude/bab-alyaman worktree add --detach /home/claude/mk origin/marketing
bash /home/claude/mk/setup.sh /home/claude/bab-alyaman
export MK_WORK=/home/claude/mk/work
```

`setup.sh` unpacks the live game from `origin/main` into `$MK_WORK/build`, takes game-development's newest bot from
`origin/sources` (`scratchpad/game/tools/bot.js`, falling back to `assets/smartbot.js`), and checks Playwright, PIL,
numpy, scipy and ffmpeg (Chromium and Playwright come with the machine; don't reinstall them).

## Layout

| path | what |
|---|---|
| `mk.py` | paths every tool shares (`MK_WORK`, `MK_BUILD`, `MK_TEXT`), the logo, handle and font |
| `rig/drv.js` | the deterministic driver: virtual time, seeded randomness, offline audio in lockstep, the game's event log |
| `rig/common.py` | serve and boot the build under the driver; hooks the game's voices, music and subtitles |
| `rig/film.py` | film a mission with the bot: `plan` (log + sound) then `shoot` (frames of chosen windows) |
| `rig/pilot.js` | game-development's pilot for Taiz's Apache (used by film.py when the Apache flies) |
| `lettering/strips.py` | any string drawn by the game's text renderer, as a transparent strip (`strings/` holds past sets) |
| `layout/compose.py` | a picture post: logo, title row, a game frame, optional game subtitle or comic bubbles, call to play, handle |
| `edit/reel.py` | a reel from filmed runs, from a JSON spec: title row, the game's subtitles or laid lines, end card, one music track; refuses a shot whose picture stands still over 0.4 s |
| `edit/qc.py` | the quality gate a reel must pass: no still picture over 0.4 s, no strobe (3+ blinks a second, a boss's hit flash), what reads as "buggy" |
| `assets/` | the logo, the handle, Noto Kufi Arabic (OFL), a fallback copy of smartBot |
| `reference/` | the scripts behind past posts, kept as they were (paths point at an old scratchpad): read them for how a post was made |

## Recipes

**Choose moments.** `python3 rig/film.py plan $MK_WORK/runs/ibbP ibb 0 9000` films Ibb from its start for up to 9000
frames (150 s) and writes `log.json`: `evx` entries are game events with positions and the camera, `cam` entries the
camera, Yazeed and the boss every 10 frames, `voice` entries every line said, `subs` the subtitle shown from each frame.
Pick windows from it (a beat with text needs 3–4 s: 180–240 frames).

**Film them.** `python3 rig/film.py shoot $MK_WORK/runs/ibbP ibb 0 7000 windows.json` with
`[{"a": 2960, "b": 3160}, …]`. Same command, same run. If you film a second time with other windows, compare the voice
entries of the two logs: a shoot can come out one frame early; shift its frame numbers before mixing.
Defaults are natural play: Yazeed fires only when there is something on screen to fire at (`CLEANFIRE`), and in-world
hints are not drawn (`NOHINTS`). `SHIELD` and `HOLDFIRE` stage a run: Khaled has called staged play "buggy" (30 Oct), so
use them only when he asks.

**A picture.** Write a spec and run `python3 layout/compose.py spec.json`:
```json
{"frame": "work/runs/ibbP/f/005300.png", "crop": [12, 0, 3],
 "head": [["المهمة 4: إب", "b_org"], ["متاحة الآن", "b_red"]],
 "sub": ["العميد عاجل", "تعز ما زالت بأيدينا."], "out": "work/out/post.png"}
```
`sub` must be a line the game really says (check the build's `LANG_AR` or the run's `subs`). New words go in captions,
in `bubbles` drawn as a comic, or on cards, never in the subtitle band.

**A reel.** Write a spec (see the top of `edit/reel.py`) and run `python3 edit/reel.py spec.json --preview`, then without
`--preview` for the upright cut and with `--x` for the 4:5 cut for X. It letters every subtitle, name and title it needs
by itself (strips land in `$MK_WORK/text`) and runs `edit/qc.py` on the result. Check the sheet, then the video: frames at
each cut, loudness (about −15 LUFS, true peak under −1 dB), and the QC line (a still picture or a strobe fails it).
A line plays while what it's about is on screen: film with `MUTEVOICES=1` and lay the lines with the spec's `lines`
(`edit/specs/yazeed-v3.json` does). Then cut the dead time: the bot stands still while it waits (a boss's entrance with
the camera locked, a scripted pause), and with a still background that's a frozen picture. A cut inside a still stretch
is invisible; a laid line can run across it.

**Lettering only.** `python3 lettering/strips.py strings.json [outdir]` with `{"name": ["m_lav", "…"]}`. Fonts: `m_org`
(speaker names), `m_lav` (subtitle lines), `b_org` / `b_red` (titles), `s_lav` (small).

## Things that bite

- In the game repo clone, a plain `git fetch` moves only `FETCH_HEAD`: name the refs (setup.sh does).
- A new line cuts the one playing (`Sound.voice` stops it): at a cut, check the log so no clipped word is heard.
- AAC overshoots on bright tones: reel.py's encode keeps a low-pass and a limiter before it.
- A crop narrower than the game's screen can hide the man Yazeed is shooting at: use a wider shot (`sc: 3`) for fights.
- The world's canvas is 384x216 on these runs; scale by whole numbers only.
- A boss's hit flash strobes once the heavy MG is on it (the boat: full white; the Roaster: a half-white wash, 15 times a
  second): end a boss beat before its first hit (its `hp` in the `cam` log starts falling). The Roaster stays off-screen
  through its whole intro and rushes in at `boss_start`, so it has under half a second on screen before the hits.
- The rally (Ibb): after "Nice beret." the game holds 80 frames (1.3 s) before the Spokesman jumps: cut across it.
