"""Paths shared by the marketing tools.
ROOT: this checkout of the `marketing` branch. WORK: scratch space for the game build, runs and outputs (env MK_WORK,
default ROOT/work, which git ignores). BUILD: the live game unpacked from origin/main by setup.sh (env MK_BUILD).
TEXT: lettering strips made by lettering/strips.py (env MK_TEXT)."""
import os
ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.environ.get('MK_WORK', os.path.join(ROOT, 'work'))
BUILD = os.environ.get('MK_BUILD', os.path.join(WORK, 'build'))
TEXT = os.environ.get('MK_TEXT', os.path.join(WORK, 'text'))
ASSETS = os.path.join(ROOT, 'assets')
FONT = os.path.join(ASSETS, 'NotoKufiArabic[wght].ttf')
LOGO = os.path.join(ASSETS, 'logo.png')          # the game's logo, on its own box colour BG
HANDLE = os.path.join(ASSETS, 'handle.png')      # @babalyemengame in the game's lettering (1x)
BOT = os.path.join(WORK, 'smartbot.js')          # setup.sh takes it from game-development's newest bot
BOT_FALLBACK = os.path.join(ASSETS, 'smartbot.js')
BG = (3, 4, 9)                                   # the logo's box colour: pages and cards use it so the logo has no edge
for _d in (WORK, TEXT):
    os.makedirs(_d, exist_ok=True)
