# cast.py - the characters at arcade scale (about 43px tall), Metal Slug build:
# small head on a neck, wide shoulders, upright stance, weapon at the hip.
# One rig: head + torso + arm + futa/skirt + legs + gear. Palette and gear swaps.
from px import *

INK = '#1c1418'

# ------------------------------------------------------------------ heads (face right)
# Face sits in columns 3..10; the chin is on the second-to-last row.
HEADS = {
    'wrap': [                      # mashadda headwrap, short beard
        '...KKKKK....',
        '.KKLLKlKKk..',
        'KLLKKlKKKKk.',
        'KKKKlKKKlkk.',
        'KkklkkklkkR.',
        'Kk.rsSnnSnn.',
        'Kk.rSSoSSoS.',
        'kK.rsSSSSSSR',
        '.k.rNNNNNNs.',
        '...rNNNooNN.',
        '....NNNNNN..',
        '.....nNNn...',
    ],
    'wrap_clean': [
        '...KKKKK....',
        '.KKLLKlKKk..',
        'KLLKKlKKKKk.',
        'KKKKlKKKlkk.',
        'KkklkkklkkR.',
        'Kk.rsSnnSnn.',
        'Kk.rSSoSSoS.',
        'kK.rsSSSSSSR',
        '.k.rsSSSSSs.',
        '...rsSSooS..',
        '....rsSSSs..',
        '.....rss....',
    ],
    'wrap_tache': [
        '...KKKKK....',
        '.KKLLKlKKk..',
        'KLLKKlKKKKk.',
        'KKKKlKKKlkk.',
        'KkklkkklkkR.',
        'Kk.rsSnnSnn.',
        'Kk.rSSoSSoS.',
        'kK.rsSSSSSSR',
        '.k.rsSnnnnns',
        '...rsSSooS..',
        '....rsSSSs..',
        '.....rss....',
    ],
    'wrap_stubble': [
        '...KKKKK....',
        '.KKLLKlKKk..',
        'KLLKKlKKKKk.',
        'KKKKlKKKlkk.',
        'KkklkkklkkR.',
        'Kk.rsSnnSnn.',
        'Kk.rSSoSSoS.',
        'kK.rsSSSSSSR',
        '.k.rssSSSss.',
        '...rsssoos..',
        '....rssss...',
        '.....rss....',
    ],
    'wrap_panic': [
        '...KKKKK....',
        '.KKLLKlKKk..',
        'KLLKKlKKKKk.',
        'KKKKlKKKlkk.',
        'KkklkknnknnR',
        'Kk.rsSIoSIoS',
        'Kk.rSSSSSSSS',
        'kK.rsSSSSSSR',
        '.k.rsSIIIIs.',
        '...rsSooooS.',
        '....rsooooS.',
        '.....rssss..',
    ],
    'masked': [                    # the Guard: face scarf
        '...KKKKK....',
        '.KKLLKlKKk..',
        'KLLKKlKKKKk.',
        'KKKKlKKKlkk.',
        'KkklkkklkkS.',
        'Kk.krSnnSnn.',
        'Kk.kSSoSSoS.',
        'kK.KKKKKKKKK',
        '.k.kKKKKKKK.',
        '...kKKLKKK..',
        '....kKKKK...',
        '.....kkk....',
    ],
    'straw': [                     # Salem: tall Tihama straw hat, moustache
        '....22222....',
        '....21223....',
        '...2122223...',
        '...2122223...',
        '...2122223...',
        '..PPPPPPPPP..',
        '..212222223..',
        '.22122222223.',
        '3333333333333',
        '...rsSnnSnn..',
        '...rSSoSSoS..',
        '...rsSSSSSSR.',
        '...rsSnnnnns.',
        '...rsSSooS...',
        '....rsSSSs...',
        '.....rss.....',
    ],
    'veil': [                      # Bilqis: shawl hood, coin veil
        '...KKKKK....',
        '.KKLLKKKKk..',
        'KLLKKKKKKKk.',
        'KKKKKKKKKKk.',
        'KKKkSSSSSSk.',
        'KKkrSnnSnnk.',
        'KKkrSoSSoSS.',
        'KKkVVVVVVVV.',
        'KkkVYVYVYVV.',
        'kKkVVVVVVV..',
        'kKKkVVvVV...',
        '.kKKkVVV....',
    ],
    'scarf': [                     # Arwa: flowered scarf, sprig of basil
        '.6..KKKKK...',
        '676KKLKKKK..',
        '.7KLKKPKKKk.',
        '.KKKKKKKPKk.',
        '.KKPkSSSSSk.',
        '.KKkrSnSSnS.',
        '.KKkrSoSSoS.',
        '.KKkrsSSSSSR',
        '.KKkrsSSSSs.',
        '..KkrsSPPS..',
        '..kKkrSSs...',
        '..kkKKkk....',
    ],
    'pot': [                       # the cook wears his pot
        '...mmmmmmm...',
        '...MQQMMMm...',
        '...MQMMMMm...',
        '...MMMMMMm...',
        '.mmMMMMMMmmm.',
        '.m.MMMMMMm.m.',
        '..MMMMMMMMMm.',
        '...rSSoSSoS..',
        '...rsSSSSSSR.',
        '...rsNNNNNNs.',
        '...rsSSooS...',
        '....rsSSSs...',
        '.....rss.....',
    ],
    'marshal': [                   # towering wrap with a jewel and feather, shades
        '........W....',
        '.......WW....',
        '....KKKWKK...',
        '..KKLLKlWKKK.',
        '.KLLKKlKPPKKk',
        '.KLKKlKKPPKlk',
        'KLKKlKKKlKKlk',
        'KKKlKKKlKKlKk',
        'KKlKKKlKKlKkk',
        'KlKKKlKKlKkkk',
        '.KKKlKKlKkkk.',
        '.kkklkklkkkR.',
        '...rsSSSSSSS.',
        '...rsoooooooo',
        '...rSooQSooQS',
        '...rsSSSSSSSR',
        '...NNNNNNNNNN',
        '...rNNSooSNN.',
        '....rsSSSSs..',
        '.....rsss....',
    ],
    'elder': [                     # detainee: white cap, grey beard
        '............',
        '...WWWWW....',
        '..WWWWWWW...',
        '..WwWwWwW...',
        '..wwwwwwwS..',
        '..nrsSnnSnn.',
        '..nrSSoSSoS.',
        '...rsSSSSSSR',
        '...rnnnnnns.',
        '...nnnooonn.',
        '....nnnnnn..',
        '....nnnnnn..',
        '.....nnnn...',
    ],
}

# ------------------------------------------------------------------ body parts
PARTS = {
    'torso': [
        '.....abbb.....',
        '..aabbbbbbcc..',
        '.abbbbbbbWWbc.',
        'abbbbbbbbWwbbc',
        'abbbbbbbbWwbbc',
        'abbcbbbbbbWbbc',
        'abbcbbbbbbbbbc',
        '.bbcbbbbbbbbc.',
        '.cbbcbbbbbbbc.',
        '.cbbbbbbbbbbc.',
        '..cbbbbbbbbc..',
        '..dccccccccd..',
        '..TYTtYTtYTt..',
    ],
    'shawl': [
        '.KK..',
        'KLKk.',
        'KKKk.',
        'KKk..',
        'kKk..',
        'kKk..',
        '.kk..',
    ],
    'arm': [                       # near arm, weapon held at the hip
        '.abbbb..........',
        'abbbbbc.........',
        'abbbbbc.........',
        'abbbbbc.........',
        '.abbbbc.........',
        '.abbbbcd........',
        '.abbbbbcd.......',
        '..abbbbbbbbd....',
        '..cbbbbbbbbdRSs.',
        '...ccccccccdSSSs',
        '............sSs.',
    ],
    'arm_rolled': [                # sleeve to the elbow, bare forearm
        '.abbbb..........',
        'abbbbbc.........',
        'abbbbbc.........',
        'abbbbbc.........',
        '.abbbbc.........',
        '.dccccdd........',
        '.RSSSSSsr.......',
        '..RSSSSSSSSr....',
        '..sSSSSSSSSsRSs.',
        '...ssssssssrSSSs',
        '............sSs.',
    ],
    'armband': ['YYYYYY', 'YoYYoY'],
    'futa': [
        '.FFFFFFFFFFf...',
        '.EFFFFfFFFFFf..',
        'EFFFFFfFFFFFf..',
        'EFFFFFfFFFFFFf.',
        'EFFFFfFFFFFFFf.',
        'EFFFFfFFFFFFFf.',
        'EFFFFfFFFFFFFFf',
        'EFFFfFFFFFFFFFf',
        'HHHHHHHHHHHHHHh',
        'hYhYhYhYhYhYhYh',
        '.FFFFFFFFFFFFf.',
    ],
    'legs': [
        '..rSSs.....rSSs..',
        '..rSSs.....rSSs..',
        '..rSSs.....rSSs..',
        '...rSS......rSS..',
        '...rSS......rSS..',
        '...rSSs.....rSSs.',
        '..XrSSSSX..XrSSSSX',
        '..xxxxxxx..xxxxxxx',
    ],
    'futa_run': [
        '...FFFFFFFFFFf....',
        '..EFFFFfFFFFFFf...',
        '..EFFFFfFFFFFFFf..',
        '.EFFFFFfFFFFFFFf..',
        '.EFFFFfFFFFFFFFFf.',
        '.EFFFFfFFFFFFFFFf.',
        'EFFFFFfFFFFFFFFFFf',
        'EFFFFfFFFFFFFFFFFf',
        'HHHHHHHHHHHHHHHHHh',
        'hYhYhYhYhYhYhYhYhh',
        '.FFFFFFFFFFFFFFFf.',
    ],
    'legs_run': [
        '...rSSs........rSSs...',
        '..rSSs.........rSSs...',
        '.rSSs..........rSSs...',
        'rSSs............rSS...',
        'XSS.............rSS...',
        'xX..............rSSs..',
        'x..............XrSSSSX',
        '...............xxxxxxx',
    ],
    'futa_kneel': [
        '...FFFFFFFFFFf....',
        '..EFFFFfFFFFFFFf..',
        '.EFFFFFfFFFFFFFFf.',
        '.EFFFFFFfFFFHHHHh.',
        'EFFFFFFFf...rSSs..',
        'EFFFFFFFf...rSSs..',
        'HHHHHHHHh...rSSs..',
        '.rSSSSX....XrSSSSX',
        '.xxxxxx....xxxxxxx',
    ],
    'torso_front': [
        '.....abbb.....',
        '..aabbWWbbcc..',
        '.abbbbWWbbbbc.',
        'abbbbbWwbbbbbc',
        'abbbbbWwbbbbbc',
        '.bbbcbWWbcbbc.',
        '.bbbcbbbbcbbc.',
        '.cbbbbbbbbbbc.',
        '.cbbbbbbbbbbc.',
        '..cbbbbbbbbc..',
        '..cbbbbbbbbc..',
        '..dccccccccd..',
        '..TYTtYTtYTt..',
    ],
    'arm_up_l': [
        '.RSs..',
        'RSSs..',
        '.SSs..',
        '.abc..',
        '.abc..',
        '.abbc.',
        '.abbc.',
        '.abbc.',
        '..abc.',
        '..abbc',
        '..abbc',
        '...abb',
        '...abb',
    ],
    'arm_up_r': [
        '..sSR.',
        '..sSSR',
        '..sSS.',
        '..cba.',
        '..cba.',
        '.cbba.',
        '.cbba.',
        '.cbba.',
        '.cba..',
        'cbba..',
        'cbba..',
        'bba...',
        'bba...',
    ],
    'futa_front': [
        '.FFFFFFFFFFFFf.',
        '.EFFFFFfFFFFFf.',
        'EFFFFFFfFFFFFFf',
        'EFFFFFFfFFFFFFf',
        'EFFFFFFfFFFFFFf',
        'EFFFFFFfFFFFFFf',
        'EFFFFFFfFFFFFFf',
        'EFFFFFFfFFFFFFf',
        'HHHHHHHHHHHHHHh',
        'hYhYhYhYhYhYhYh',
        '.FFFFFFFFFFFFf.',
    ],
    'legs_front': [
        '..rSSs...rSSs..',
        '..rSSs...rSSs..',
        '..rSSs...rSSs..',
        '...rSS...rSS...',
        '...rSS...rSS...',
        '..rSSs...rSSs..',
        'XSSSSSX.XSSSSSX',
        'xxxxxxx.xxxxxxx',
    ],
    'rope': [
        'OOOOOOOOOOOOOO',
        '..............',
        '..............',
        'OOOOOOOOOOOOOO',
        '.....Oo.......',
        '..............',
        'OOOOOOOOOOOOOO',
    ],
    # Bilqis
    'torso_f': [
        '.....KKKK.....',
        '..KKKLKKKKkk..',
        '.KKLKKKbYbbKk.',
        'KKKKKbbbbYbbkk',
        'KKKkbbYbbbbbbc',
        'kKKkbbbbYbbbbc',
        'kkKcbbbbbbbbbc',
        '.kKcbbbbbbbbc.',
        '.kkcbbbbbbbbc.',
        '.kcbbbbbbbbbc.',
        '..cbbbbbbbbc..',
        '..dccccccccd..',
        '..TYTTYTTYTt..',
    ],
    'skirt_long': [
        '..bbbbbbbbbbc....',
        '..abbbbcbbbbc....',
        '.abbbbbcbbbbbc...',
        '.abbbbbcbbbbbc...',
        '.abbbbcbbbbbbc...',
        '.abbbbcbbbbbbbc..',
        'abbbbbcbbbbbbbc..',
        'abbbbbcbbbbbbbc..',
        'abbbbbcbbbbbbbbc.',
        'abbbbcbbbbbbbbbc.',
        'abbbbcbbbbbbbbbc.',
        'abbbbcbbbbbbbbbbc',
        'abbbbcbbbbbbbbbbc',
        'HHHHHHHHHHHHHHHHh',
        'YhYhYhYhYhYhYhYhh',
        'HHHHHHHHHHHHHHHHh',
        '..Xxxx.....Xxxxx.',
        '..xxxx.....xxxxx.',
    ],
    'skirt_long_run': [
        '....bbbbbbbbbbc.......',
        '...abbbbcbbbbbbc......',
        '...abbbbcbbbbbbbc.....',
        '..abbbbbcbbbbbbbc.....',
        '..abbbbcbbbbbbbbbc....',
        '.abbbbbcbbbbbbbbbc....',
        '.abbbbbcbbbbbbbbbbc...',
        '.abbbbcbbbbbbbbbbbc...',
        'abbbbbcbbbbbbbbbbbbc..',
        'abbbbbcbbbbbbbbbbbbc..',
        'abbbbcbbbbbbbbbbbbbbc.',
        'abbbbcbbbbbbbbbbbbbbc.',
        'abbbcbbbbbbbbbbbbbbbbc',
        'HHHHHHHHHHHHHHHHHHHHHh',
        'YhYhYhYhYhYhYhYhYhYhYh',
        '.HHHHHHHHHHHHHHHHHHHh.',
        '.Xxx.............Xxxxx',
        'xx................xxxx',
    ],
    # Arwa
    'torso_medic': [
        '.....abbb.....',
        '..aabbbbbbcc..',
        '.abbbbWWWWbbc.',
        'abbbbWW6WWWbbc',
        'abbbbW666WWbbc',
        'abbcbWW6WWWbbc',
        'abbcbbWWWWbbbc',
        '.bbcbbbbbbbbc.',
        '.cbbcbbbbbbbc.',
        '.cbbbbbbbbbbc.',
        '..cbbbbbbbbc..',
        '..dccccccccd..',
        '..TTTTTTTTTt..',
    ],
    'skirt_short': [
        '.bbbbbbbbbbc...',
        '.abbbbcbbbbbc..',
        'abbbbbcbbbbbc..',
        'abbbbbcbbbbbbc.',
        'abbbbcbbbbbbbc.',
        'abbbbcbbbbbbbbc',
        'HHHHHHHHHHHHHHh',
    ],
    'legs_trouser': [
        '..ZzZZ.....ZzZZ..',
        '..ZZzZ.....ZZzZ..',
        '..ZzZZ.....ZzZZ..',
        '..ZZzZ.....ZZzZ..',
        '..ZzZZ.....ZzZZ..',
        '..ZZzZ.....ZZzZ..',
        '..YYYY.....YYYY..',
        '..PYPY.....PYPY..',
        '..XXXX.....XXXX..',
        '.XXXXXX...XXXXXX.',
        '.xxxxxx...xxxxxx.',
    ],
    'medic_pack': [
        '..nn..',
        '.n..n.',
        '.n....',
        'PPPPP.',
        'WWWWWw',
        'WW6WWw',
        'W666Ww',
        'WW6WWw',
        'WWWWWw',
        'wwwwww',
    ],
    'umbrella': ['.N.', 'N.N', 'N..', 'P..', 'Pp.', 'Pp.', 'Pp.', 'Pp.', 'Pp.', 'Pp.', 'Pp.', 'Pp.', '.N.'],
    # officers: greatcoat to the knee, trousers, tall boots
    'coat_legs': [
        '..bbbbbbbbbbc....',
        '..abbbbcbbbbc....',
        '.abbbbbcbbbbbc...',
        '.abbbbbcbbbbbc...',
        '.abbbbcbbbbbbc...',
        '.abbbbcbbbbbbbc..',
        '.dccccdcccccccd..',
        '..ZZZz....ZZZz...',
        '..ZZZz....ZZZz...',
        '..ZZZz....ZZZz...',
        '..XXXx....XXXx...',
        '..XXXx....XXXx...',
        '..XQXx....XQXx...',
        '..XXXx....XXXx...',
        '..XXXx....XXXx...',
        '..XXXXx...XXXXx..',
        '.XXXXXXx.XXXXXXx.',
        '.xxxxxxx.xxxxxxx.',
    ],
    # gear. Rank is worn at the belt.
    'jambiya_s': ['N.', 'Gg', 'Gg', '.G'],
    'jambiya_m': ['NN....', 'NY....', 'NN....', 'GGg...', 'GYg...', 'GGg..G', 'GGGgGG', '.GGGG.', '..gg..'],
    'jambiya_l': [
        '.NNNN........',
        '.NYYN........',
        '.NNNN........',
        '.NYYN........',
        'GGGGGG.......',
        '.GYYGg.......',
        '.GGGGg.......',
        '.GGYGGg......',
        '.GGGYGg......',
        '..GGGYGg....G',
        '..GGGGYGg..GG',
        '...GGGGYGgGGG',
        '....GGGGYGGG.',
        '.....GGGGGG..',
        '......gggg...',
    ],
    'wrench': ['Q.Q..', 'QQQ..', '.M...', '.Mm..', '..M..', '..Mm.', '...M.', '..mMm', '..m.m'],
    'apron': [
        '..WWWW..',
        '..WWWW..',
        '.WWWWWW.',
        '.WWPWWW.',
        '.WWWWWW.',
        'TTTTTTTT',
        'WWWWWWWW',
        'WWWWWWWW',
        'WWoooWWW',
        'WWWWWWWW',
        'WWWWWWWw',
        'WWWWPWWw',
        'WWWWWWWw',
        'wwwwwwww',
    ],
    'medals': ['YPY6Y', 'PYPY6', '.Y.Y.'],
    'sash': ['P.......', 'PP......', '.PP.....', '..PP....', '...PP...', '....PP..', '.....PP.', '......PP', '.......P'],
    'epaulet': ['YYYYY', 'yYYYy', '.y.y.'],
    'bandolier': ['Y.......', 'oY......', '.oY.....', '..oY....', '...oY...', '....oY..', '.....oY.', '......oY'],
    'shield': [
        '..mMMMMMMQ..',
        '.mMMMMMMMMQ.',
        'mMMMMMMMMMMQ',
        'mMMoooooMMMQ',
        'mMMoIIIoMMMQ',
        'mMMoooooMMMQ',
        'mMMMMMMMMMMQ',
        'mMYMMMMMYMMQ',
        'mMYYMMMYYMMQ',
        'mMMYMYMYMMMQ',
        'mMMMYYYMMMMQ',
        'mMMMYYYMMMMQ',
        'mMMMMYMMYMMQ',
        'mMmMMYYYYmMQ',
        'mMMMMMMMMMMQ',
        'mMMMMMMMMMMQ',
        'mMMMMMMMMMMQ',
        'mMmMMMMMMmMQ',
        'mMMMMMMMMMMQ',
        'mMMMMMMMMMMQ',
        'mMMMMMMMMMMQ',
        'mMmMMMMMMmMQ',
        '.mMMMMMMMMQ.',
        '..mmmmmmmm..',
    ],
    'ladle': ['.MMMM.', 'MQMMMm', 'MMMMMm', '.mmmm.', '..Mm..', '..Mm..', '..Mm..', '..Mm..', '..Mm..', '..Mm..'],
    'post': ['.BB.', 'BBBb'] + ['.Bb.'] * 44,
}

WEAPONS = {
    # rows, grip (the pixel under the near hand), fore (x offset of the support hand)
    'hmg': dict(grip=(5, 5), fore=14, rows=[
        '...........mmmm.................',
        '.....QQQQQQQQQQQQQQ.............',
        'xxxMMMMMMMMMMMMMMMMmQmQmQmQmQMM.',
        'xxBMMmmMMMMMMMMMMMMMMMMMMMMMMMMQ',
        'xBBMMMMMMMMMMMMMMMMmmmmmmmmmmm..',
        '.xx..MM.mYYYYYm.................',
        '.....Mm.mYyyyYm.................',
        '.....m..mYYYYYm.................',
        '.........mmmmm..................',
    ]),
    'rifle': dict(grip=(5, 3), fore=11, rows=[
        '....................Q.......',
        'xxxBMMMMMMMMMMMMMMMMMMmmmmmm',
        'xBBBMMMmMMMMBBBBBMm.........',
        'xB...MM.mMM.................',
        '.....Mm..mMM................',
        '..........mMM...............',
    ]),
    'marksman': dict(grip=(6, 4), fore=12, rows=[
        '.........QMMMMMMQ...................',
        '..........m....m....................',
        'xxxxBMMMMMMMMMMMMMMMMMMmmmmmmmmmmmmQ',
        'xxBBBMMMmMMMMBBBBBBM................',
        'xB....MM.mM.........................',
        '......Mm............................',
    ]),
    'rpg': dict(grip=(12, 3), fore=8, rows=[
        '...........................666......',
        'mmMMMMMMMMMMMMMMMMMMMMMMMM6666667...',
        'mMMMMMMMMMMMMMMMMMMMMMMMMM66666667..',
        'mm....BB....BB.............777......',
        '......xB....xB......................',
    ]),
    'shotgun': dict(grip=(5, 3), fore=11, rows=[
        '.....................Q....',
        'xxxBMMMMMMMMMMMMMMMMMMMmmm',
        'xBBBMMMmBBBBBBBmmmmmmmmm..',
        'xB...MM.m.................',
        '.....Mm...................',
    ]),
    'pistol': dict(grip=(0, 2), fore=None, rows=[
        'QQQQQQQQ.',
        'MMMMMMMMm',
        'MMMmmm...',
        'MMm......',
        'Mm.......',
    ]),
    'megaphone': dict(grip=(1, 4), fore=None, rows=[
        '.......WW',
        '.....PPPW',
        '...PPPPPW',
        '.PPPPPPPW',
        'MPPPPPPPW',
        '.pPPPPPPW',
        '...pPPPPW',
        '.....pPPW',
        '.......WW',
    ]),
    'detonator': dict(grip=(0, 0), fore=None, rows=[
        '...MM...',
        '.MMMMMM.',
        '...MM...',
        'PPPPPPPP',
        'PPYPPPPp',
        'PPPPPPPp',
        'pppppppp',
    ]),
}

SKIN = {
    1: ('#f0c8a0', '#d8a47c', '#b07c5c', '#805844'),
    2: ('#e0b088', '#c48e66', '#9a6a4c', '#6e4a38'),
    3: ('#b88a66', '#9a6c4c', '#74503a', '#52382c'),
}


def pal(coat, futa=None, band=None, wrap=None, skin=2, **kw):
    """Build a palette. Each cloth is a 4-tone ramp (light, base, shade, dark)."""
    a, b, c, d = coat
    fu = futa or ('#f0e8d4', '#d8ceb4', '#aca084', '#84785e')
    bd = band or ('#c8a03c', '#96742c')
    wr = wrap or coat
    sk = SKIN[skin]
    p = {
        'a': a, 'b': b, 'c': c, 'd': d,
        'E': fu[0], 'F': fu[1], 'f': fu[2],
        'H': bd[0], 'h': bd[1],
        'L': wr[0], 'K': wr[1], 'k': wr[2], 'l': wr[3],
        'R': sk[0], 'S': sk[1], 's': sk[2], 'r': sk[3],
        'N': '#2a2022', 'n': '#463632', 'I': '#f0ece0', 'o': INK,
        'W': '#f0ece0', 'w': '#c4bca4', 'Y': '#d8b048', 'y': '#a07c2c',
        'T': '#6a4a34', 't': '#4a3428', 'G': '#4c8858', 'g': '#305c3c',
        'M': '#8c96a2', 'm': '#4a505c', 'Q': '#ccd2d8',
        'X': '#5a4030', 'x': '#2e201c', 'Z': '#56544c', 'z': '#3c3a36',
        'P': '#b84a40', 'p': '#863030', 'V': '#2a2428', 'v': '#4a4048',
        'B': '#9a6a3c', 'O': '#8c6240',
        '1': '#f0dc9c', '2': '#d8bc6c', '3': '#ac8a44',
        '6': '#5c9c5c', '7': '#386c40',
    }
    p.update(kw)
    return p


WPAL = {'M': '#565a66', 'm': '#32343e', 'Q': '#8a909c', 'B': '#9a6a3c', 'x': '#664028',
        'Y': '#c8a03c', 'y': '#96742c', '6': '#7c8c50', '7': '#525e36',
        'P': '#b84a40', 'p': '#863030', 'W': '#f0ece0'}

# cloth ramps: light, base, shade, dark. Dusty and sun-bleached, nothing neon.
BLUE = ('#a0c0d8', '#6890b4', '#466a90', '#2c4868')
TEAL = ('#8cbcb0', '#5c9088', '#3e6a68', '#284a4c')
MAROON = ('#b86c64', '#903e42', '#662a32', '#421c24')
SAGE = ('#a8c898', '#74a070', '#4e7850', '#345438')
ROSE = ('#dca4ac', '#b87480', '#8c5060', '#603844')
COAT = ('#b0a080', '#8a7a5c', '#625642', '#40382c')
OLIVE = ('#9aa070', '#767c50', '#545a3a', '#383c28')
KHAKI = ('#c8b890', '#a4946c', '#7a6c4e', '#504634')
EARTH = ('#a08468', '#7a604a', '#564234', '#382a22')
SAND = ('#dcc8a0', '#b8a47c', '#8c7a5a', '#5e523c')
SLATE = ('#8a8c90', '#64666c', '#44464c', '#2a2c30')
CHARC = ('#62605e', '#444244', '#2e2c30', '#1c1a1e')
WHITE = ('#f8f4e8', '#e0dac8', '#b4ac94', '#88806a')
INDIGO = ('#5e5c7c', '#403e5a', '#2c2a42', '#1c1a2c')
SKYB = ('#c8dce8', '#a0bcd0', '#7898b0', '#56748c')
DKFUTA = ('#7c7468', '#5c564c', '#403c36', '#2a2622')
REDFUTA = ('#d08468', '#b05c4c', '#803c3c', '#56282c')

PAL = {
    'yazeed': pal(COAT, band=('#6890b4', '#466a90'), wrap=BLUE, skin=2),
    'salem': pal(WHITE, futa=REDFUTA, band=('#d8bc6c', '#5c8c5c'), wrap=TEAL, skin=3),
    'bilqis': pal(INDIGO, band=('#903e42', '#662a32'), wrap=MAROON, skin=2, T='#662a32', t='#421c24'),
    'arwa': pal(ROSE, band=('#74a070', '#4e7850'), wrap=SAGE, skin=1, P='#e8b0c0',
                Z='#e4dcc4', z='#b8ac8c', T='#4e7850', t='#345438'),
    'elder': pal(SKYB, band=('#5c9088', '#3e6a68'), wrap=SKYB, skin=3, n='#c4c0b8', N='#94908a'),
}

TURBAN = ('#f6f2e4', '#dcd4bc', '#aca48a', '#7c745c')
TURBAN2 = ('#ece0c4', '#ccbc98', '#9c8c6c', '#6e6048')
WRAPS = [TURBAN, TURBAN2, TURBAN, TURBAN2]


def grunt_pal(skin=2, wrap=0, coat=OLIVE):
    return pal(coat, futa=DKFUTA, band=('#c8a03c', '#96742c'), wrap=WRAPS[wrap % len(WRAPS)], skin=skin,
               W='#c8c0a4', w='#9c9478')


def guard_pal(skin=2):
    return pal(CHARC, futa=CHARC, band=('#c8a03c', '#96742c'), wrap=CHARC, skin=skin,
               W='#64666c', w='#44464c')


def marshal_pal(skin=1):
    return pal(('#7c8458', '#5a623e', '#3e442c', '#282c1e'), futa=DKFUTA, band=('#c8a03c', '#96742c'),
               wrap=CHARC, skin=skin, Z='#3e442c', z='#282c1e', X='#2a2428', x='#161214',
               T='#c8a03c', t='#96742c', P='#b84a40')


def _arm_pal(p, bare):
    if not bare:
        return p
    q = dict(p)
    q.update(a=p['R'], b=p['S'], c=p['s'], d=p['r'])
    return q


def figure(layers, flip=False, ink=INK, foot=None):
    """layers: list of (rows, x, y, palette). Returns (image, foot_x, foot_y)."""
    minx = min(x for _, x, _, _ in layers)
    miny = min(y for _, _, y, _ in layers)
    maxx = max(x + max(len(r) for r in rows) for rows, x, _, _ in layers)
    maxy = max(y + len(rows) for rows, _, y, _ in layers)
    im = new(maxx - minx, maxy - miny)
    for rows, x, y, p in layers:
        blit(im, sprite(rows, p), x - minx, y - miny)
    fx, fy = (foot or (8, maxy))
    fx, fy = fx - minx, fy - miny
    bb = im.getbbox()
    im = im.crop(bb)
    fx, fy = fx - bb[0], fy - bb[1]
    im = outline(im, ink)
    fx, fy = fx + 1, fy + 1
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
        fx = im.width - 1 - fx
    return im, fx, fy


def _weapon_layers(weapon, hand, p):
    """Weapon under the near hand at `hand` (x, y of the hand's top-left)."""
    if not weapon:
        return [], []
    wp = WEAPONS[weapon]
    gx, gy = wp['grip']
    hx, hy = hand
    under = [(wp['rows'], hx + 1 - gx, hy + 1 - gy, WPAL)]
    over = []
    if wp.get('fore'):
        fx = hx + wp['fore']
        under.insert(0, (['dccc', 'dccc', '.dd.'], fx - 4, hy, p))       # far forearm
        over.append((['Rs.', 'SSs', '.s.'], fx, hy + 1, p))
    return under, over


GEAR_AT = {            # offsets from the torso's top-left
    'jambiya_s': (9, 10), 'jambiya_m': (8, 8), 'jambiya_l': (4, 5), 'wrench': (7, 8),
    'medals': (7, 3), 'sash': (3, 2), 'epaulet': (1, 0), 'bandolier': (4, 3), 'apron': (4, 4),
}


def man(head, p, pose='aim', weapon='rifle', gear=(), bare_arms=False, shawl=True, flip=False,
        torso='torso', legs='futa', band=False, arm='arm'):
    """A man in jacket and futa. pose: aim | run | kneel | handsup | tied."""
    L = []
    hd = HEADS[head]
    ap = _arm_pal(p, bare_arms)
    if pose in ('aim', 'run', 'kneel'):
        tx, ty = (3 if pose == 'run' else 2), 0
        hand = (tx + 13, ty + 10)                 # top-left of the near hand
        under, over = _weapon_layers(weapon, hand, p)
        if pose == 'aim':
            if legs == 'coat':
                L.append((PARTS['coat_legs'], tx - 1, 13, p))
            else:
                L.append((PARTS['legs'], tx - 2, 24, p))
                L.append((PARTS['futa'], tx - 1, 13, p))
            foot = (tx + 6, 32)
        elif pose == 'run':
            L.append((PARTS['legs_run'], tx - 4, 24, p))
            L.append((PARTS['futa_run'], tx - 2, 13, p))
            foot = (tx + 7, 32)
        else:
            L.append((PARTS['futa_kneel'], tx - 3, 13, p))
            foot = (tx + 6, 22)
        L.append((PARTS[torso], tx, ty, p))
        if shawl:
            L.append((PARTS['shawl'], tx, ty + 1, p))
        for g in gear:
            if g in GEAR_AT:
                gx, gy = GEAR_AT[g]
                L.append((PARTS[g], tx + gx, ty + gy, p))
        L += under
        L.append((PARTS[arm], tx + 1, ty + 2, ap))
        if band:
            L.append((PARTS['armband'], tx + 1, ty + 4, p))
        L += over
        if 'shield' in gear:
            L.append((PARTS['shield'], tx + 14, ty - 3, p))
        L.append((hd, tx + (0 if len(hd[0]) <= 12 else -1), ty + 1 - len(hd), p))
        return figure(L, flip=flip, foot=foot)
    # front-facing poses
    tx, ty = 2, 0
    if pose == 'tied':
        L.append((PARTS['post'], tx + 5, ty - 15, p))
    L.append((PARTS['legs_front'], tx - 1, 24, p))
    L.append((PARTS['futa_front'], tx - 1, 13, p))
    if pose == 'handsup':
        L.append((PARTS['arm_up_l'], tx - 4, ty - 10, ap))
        L.append((PARTS['arm_up_r'], tx + 12, ty - 10, ap))
    L.append((PARTS['torso_front'], tx, ty, p))
    if pose == 'tied':
        L.append((PARTS['rope'], tx, ty + 3, p))
    for g in gear:
        if g == 'jambiya_s':
            L.append((PARTS[g], tx + 6, ty + 10, p))
        elif g == 'jambiya_m':
            L.append((PARTS[g], tx + 5, ty + 8, p))
        elif g == 'apron':
            L.append((PARTS[g], tx + 3, ty + 4, p))
        elif g == 'ladle':
            L.append((PARTS[g], tx + 13, ty - 19, p))
    if band and pose == 'handsup':
        L.append((['YYY', 'YoY'], tx - 3, ty - 5, p))
    L.append((hd, tx + (1 if len(hd[0]) <= 12 else 0), ty + 1 - len(hd), p))
    return figure(L, flip=flip, foot=(tx + 7, 32))


def woman(who, pose='aim', weapon=None, flip=False):
    L = []
    if who == 'bilqis':
        p = PAL['bilqis']
        hd = HEADS['veil']
        tx, ty = (3 if pose == 'run' else 2), 0
        hand = (tx + 13, ty + 10)
        under, over = _weapon_layers(weapon or 'marksman', hand, p)
        if pose == 'run':
            L.append((PARTS['skirt_long_run'], tx - 3, 13, p))
            foot = (tx + 7, 31)
        else:
            L.append((PARTS['skirt_long'], tx - 1, 13, p))
            foot = (tx + 6, 31)
        L.append((PARTS['torso_f'], tx, ty, p))
        L.append((PARTS['bandolier'], tx + 4, ty + 3, p))
        L += under
        L.append((PARTS['arm'], tx + 1, ty + 2, p))
        L += over
        L.append((hd, tx, ty + 1 - len(hd), p))
        return figure(L, flip=flip, foot=foot)
    if who == 'arwa':
        p = PAL['arwa']
        hd = HEADS['scarf']
        tx, ty = 2, 0
        hand = (tx + 13, ty + 10)
        under, over = _weapon_layers(weapon or 'rifle', hand, p)
        L.append((PARTS['umbrella'], tx - 1, ty - 7, p))
        L.append((PARTS['medic_pack'], tx - 5, ty + 3, p))
        L.append((PARTS['legs_trouser'], tx - 2, 20, p))
        L.append((PARTS['skirt_short'], tx - 1, 13, p))
        L.append((PARTS['torso_medic'], tx, ty, p))
        L += under
        L.append((PARTS['arm'], tx + 1, ty + 2, p))
        L += over
        L.append((hd, tx - 1, ty + 1 - len(hd), p))
        return figure(L, flip=flip, foot=(tx + 6, 31))


# ------------------------------------------------------------------ the cast
def hero(name, pose='aim', weapon=None, flip=False):
    if name == 'yazeed':
        return man('wrap', PAL['yazeed'], pose, weapon or 'pistol', gear=('jambiya_m',), flip=flip)
    if name == 'salem':
        return man('straw', PAL['salem'], pose, weapon or 'shotgun', gear=('wrench',),
                   arm='arm_rolled', flip=flip)
    return woman(name, pose, weapon, flip)


def grunt(kind='rifle', skin=2, flip=True, face=None, wrap=0):
    g = grunt_pal(skin, wrap)
    if kind == 'rifle':
        return man(face or 'wrap_stubble', g, 'aim', 'rifle', gear=('jambiya_s',), flip=flip, band=True)
    if kind == 'rpg':
        return man(face or 'wrap_tache', g, 'kneel', 'rpg', gear=('jambiya_s',), flip=flip, band=True)
    if kind == 'surrender':
        return man('wrap_panic', g, 'handsup', None, gear=('jambiya_s',), flip=flip, band=True)
    if kind == 'cook':
        g = dict(g, W='#f0ece0', w='#c4bca4')
        return man('pot', g, 'handsup', None, gear=('apron', 'ladle'), flip=flip)
    if kind == 'shield':
        return man(face or 'wrap_tache', g, 'aim', 'pistol', gear=('jambiya_s', 'shield'), flip=flip, band=True)
    if kind == 'demo':
        return man(face or 'wrap_clean', g, 'kneel', 'detonator', gear=('jambiya_s',), flip=flip, band=True)
    if kind == 'guard':
        return man('masked', guard_pal(skin), 'aim', 'shotgun', gear=('jambiya_m', 'bandolier'), flip=flip, band=True)
    if kind == 'marshal':
        return man('marshal', marshal_pal(skin), 'aim', 'megaphone', legs='coat', shawl=False,
                   gear=('sash', 'medals', 'epaulet', 'jambiya_l'), flip=flip)


def detainee(flip=False, freed=False):
    if freed:
        return man('elder', PAL['elder'], 'handsup', None, shawl=False, flip=flip)
    return man('elder', PAL['elder'], 'tied', None, shawl=False, flip=flip)


if __name__ == '__main__':
    sheet = new(700, 84, hexc('#b8b0a0'))
    x = 6
    items = [hero('yazeed', 'run', 'hmg'), hero('yazeed'), hero('salem'), hero('bilqis'), hero('bilqis', 'run'),
             hero('arwa'), grunt('rifle', flip=False), grunt('rpg', 3, flip=False, wrap=1),
             grunt('surrender', 1, flip=False, wrap=2), grunt('cook', flip=False), grunt('shield', 3, flip=False, wrap=3),
             grunt('demo', flip=False, wrap=1), grunt('guard', 1, flip=False), grunt('marshal', flip=False),
             detainee()]
    for im, fx, fy in items:
        blit(sheet, im, x, 78 - fy)
        x += im.width + 4
    rect(sheet, 0, 78, 699, 78, '#7c7468')
    print('used width', x)
    save(sheet, 't_cast1.png', 1)
