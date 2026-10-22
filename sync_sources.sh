#!/bin/bash
# sync_sources.sh - copies the game's current sources from this workspace into the repo's `sources` branch (a worktree
# at $DEST), commits and pushes them (project-planning-R5, 22 Oct). Same layout as the workspace, so the scripts' paths
# work once link_workspace.sh has linked them. Working notes (STATE.md, *_PLAN.md, NOTES.md) stay out: the repo is public.
# Usage: sync_sources.sh "<one-line commit message>"
set -euo pipefail
SP=/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad
OUT=/home/claude/bab_out
DEST=${DEST:-/home/claude/bab-sources}
MSG=${1:-"Sync the game's sources"}
SNAP='_(build[0-9]+[a-z]?|before[a-z_]*|r[0-9]|0[0-9]{3}|pre_refill|kit1|v1)\.'
copy() {  # copy <src dir> <dest dir> <find -name patterns...>
  local from=$1 to=$2; shift 2
  mkdir -p "$to"
  local args=() first=1
  for p in "$@"; do if [ $first = 1 ]; then args+=(-name "$p"); first=0; else args+=(-o -name "$p"); fi; done
  find "$from" -maxdepth 1 -type f \( "${args[@]}" \) | grep -vE "$SNAP" | while read -r f; do cp -p "$f" "$to/"; done
}
rm -rf "$DEST/scratchpad" "$DEST/bab_out"
copy $SP/game/src            $DEST/scratchpad/game/src            '*.js' '*.json'
copy $SP/game/gen            $DEST/scratchpad/game/gen            '*.json'
copy $SP/game/art/out        $DEST/scratchpad/game/art/out        '*.png'
copy $SP/game/tools          $DEST/scratchpad/game/tools          '*.py' '*.js' '*.npy'
copy $SP/mock                $DEST/scratchpad/mock                '*.py'
copy $SP/snd                 $DEST/scratchpad/snd                 '*.py'
copy $SP/experiments         $DEST/scratchpad/experiments         '*.js'
copy $SP/refill              $DEST/scratchpad/refill              '*.py' '*.js'
copy $SP/bosses              $DEST/scratchpad/bosses              '*.js'
copy $SP/taizmap             $DEST/scratchpad/taizmap             'capture.js' 'dump_layout.js' 'map.tpl.html' 'test_map.js'
copy $SP/gamedev-page        $DEST/scratchpad/gamedev-page        'game-development.html' 'kit_v2.py' 'test_page.js'
copy $OUT/m1_src             $DEST/bab_out/m1_src                 '*.py' '*.js' '*.html' 'version.json'
cp -p $SP/sync_sources.sh "$DEST/sync_sources.sh"
cd "$DEST"
git add -A
if git diff --cached --quiet; then echo "nothing changed"; exit 0; fi
git commit -q -F - <<EOF
$MSG

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_019J6AwARVix7c5z6Cobd9WR
EOF
git push -q origin sources
git log --format='%h %s' -1 | cut -c1-120
