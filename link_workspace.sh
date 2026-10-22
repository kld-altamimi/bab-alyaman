#!/bin/bash
# link_workspace.sh - points the workspace paths the scripts were written with at this checkout, so they run unchanged.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
SP=/tmp/claude-0/-home-claude/aa3bb6be-67d4-5082-8011-7c7396202436/scratchpad
mkdir -p "$(dirname "$SP")" /home/claude
if [ ! -e "$SP" ]; then ln -s "$ROOT/scratchpad" "$SP"; echo "linked $SP"; else echo "$SP already exists: left as it is"; fi
if [ ! -e /home/claude/bab_out ]; then mkdir -p /home/claude/bab_out; fi
if [ ! -e /home/claude/bab_out/m1_src ]; then ln -s "$ROOT/bab_out/m1_src" /home/claude/bab_out/m1_src; echo "linked bab_out/m1_src"; fi
mkdir -p /home/claude/bab_out/m1/audio
echo "Now put main's audio/*.mp3 into /home/claude/bab_out/m1/audio/ and run: python3 bab_out/m1_src/build.py --bump --local-fonts"
