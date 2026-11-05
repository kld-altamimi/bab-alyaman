#!/usr/bin/env bash
# Prepare a fresh machine for the marketing tools: the live game from origin/main (unpacked into $MK_WORK/build),
# game-development's newest bot (from origin/sources), and a check that Playwright, PIL, numpy, scipy and ffmpeg are here.
# Usage: bash setup.sh [game-repo-dir]      (default /home/claude/bab-alyaman)
# Then: export MK_WORK=<printed path>; tools read their paths from mk.py.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO="${1:-/home/claude/bab-alyaman}"
export MK_WORK="${MK_WORK:-$ROOT/work}"
mkdir -p "$MK_WORK"
# a plain `git fetch` only moves FETCH_HEAD in these clones: name the refs
git -C "$REPO" fetch -q origin +main:refs/remotes/origin/main +sources:refs/remotes/origin/sources || { echo "fetch failed"; exit 1; }
rm -rf "$MK_WORK/build" && mkdir -p "$MK_WORK/build"
git -C "$REPO" archive origin/main | tar -x -C "$MK_WORK/build"
echo "live build: $(grep -oE "BUILD ?= ?['\"][0-9][^'\"]*" "$MK_WORK/build/index.html" | head -1 | grep -oE "[0-9][0-9.]*") ($(git -C "$REPO" log -1 --format='%h %ad' --date=short origin/main))"
# the bot: smartBot out of game-development's tools/bot.js (a CommonJS file), so it can run inside the page
git -C "$REPO" show origin/sources:scratchpad/game/tools/bot.js > "$MK_WORK/bot_sources.js" 2>/dev/null
python3 - "$MK_WORK" <<'EOF'
import sys, os
w = sys.argv[1]; p = os.path.join(w, 'bot_sources.js')
src = open(p).read() if os.path.exists(p) else ''
a = src.find('function smartBot(opts)'); b = src.find('\nfunction run(bot, opts)', a)
if a < 0 or b < 0:
    print('smartBot not found on the sources branch: using assets/smartbot.js')
else:
    open(os.path.join(w, 'smartbot.js'), 'w').write(src[a:b]); print('bot: smartBot from origin/sources (%d lines)' % src[a:b].count('\n'))
EOF
[ -f "$MK_WORK/smartbot.js" ] || cp "$ROOT/assets/smartbot.js" "$MK_WORK/smartbot.js"
python3 -c "import playwright, PIL, numpy, scipy" 2>/dev/null || pip install --break-system-packages -q pillow numpy scipy
which ffmpeg >/dev/null || echo "ffmpeg missing"
echo "ready: export MK_WORK=$MK_WORK"
