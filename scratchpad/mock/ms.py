# ms.py - the cast in the arcade house style measured from Metal Slug sprites:
# about 44px tall and 28px wide, bulky forms, every form outlined in near-black,
# five-tone ramps lit from the front-top. Parts are fill-only; each gets its own outline.
from px import *

INK = '#14100c'

# Tone letters, dark -> light:
#   jacket a b c d e | lower garment f g h i j | wrap/accent k l m n o | skin p q r s t
#   hair u v w | metal x y z Z | wood W X Y | leather A B C | gold D E F
#   white H I J | red K L M | green N O P | straw 1 2 3 4 5 | veil 6 7 8 | '#' ink

# ---------------------------------------------------------------- heads (face right)
# The face starts at column 4; eye at column 7; nose at columns 10-11.
HEADS = {
    'wrap_beard': [
        '...lmnno....',
        '.klmnnoonm..',
        'kklmnonnnml.',
        'kkllmmlnnml.',
        'kkklmlmmlml.',
        'kkkllmlmmnl.',
        'kkl.pqrrrss.',
        'kkl.pquursst',
        '.kl.pqr#rsst',
        '.kk.pqrrrrs.',
        '..k.puuvuuq.',
        '....uuuvvuu.',
        '.....uuvvu..',
        '......uuu...',
    ],
    'wrap_tache': [
        '...lmnno....',
        '.klmnnoonm..',
        'kklmnonnnml.',
        'kkllmmlnnml.',
        'kkklmlmmlml.',
        'kkkllmlmmnl.',
        'kkl.pqrrrss.',
        'kkl.pquursst',
        '.kl.pqr#rsst',
        '.kk.pqrrrrs.',
        '..k.pquuuuuv',
        '....pqrr#rs.',
        '.....pqrrs..',
        '......pqq...',
    ],
    'wrap_stubble': [
        '...lmnno....',
        '.klmnnoonm..',
        'kklmnonnnml.',
        'kkllmmlnnml.',
        'kkklmlmmlml.',
        'kkkllmlmmnl.',
        'kkl.pqrrrss.',
        'kkl.pquursst',
        '.kl.pqr#rsst',
        '.kk.pqrrrrs.',
        '..k.pwqrrws.',
        '....pwqw#ws.',
        '.....wqwqw..',
        '......pwq...',
    ],
    'wrap_clean': [
        '...lmnno....',
        '.klmnnoonm..',
        'kklmnonnnml.',
        'kkllmmlnnml.',
        'kkklmlmmlml.',
        'kkkllmlmmnl.',
        'kkl.pqrrrss.',
        'kkl.pquursst',
        '.kl.pqr#rsst',
        '.kk.pqrrrrs.',
        '..k.pqrrrss.',
        '....pqrr#rs.',
        '.....pqrrs..',
        '......pqq...',
    ],
    'wrap_panic': [
        '...lmnno....',
        '.klmnnoonm..',
        'kklmnonnnml.',
        'kkllmmlnnml.',
        'kkklmlmmlml.',
        'kkkllmlmmnl.',
        'kkl.puurrss.',
        'kkl.pqQ#rsst',
        '.kl.pqQ#rsst',
        '.kk.pqrrrrs.',
        '..k.pq####s.',
        '....pq#LL#s.',
        '.....pq##s..',
        '......pqq...',
    ],
    'masked': [
        '...lmnno....',
        '.klmnnoonm..',
        'kklmnonnnml.',
        'kkllmmlnnml.',
        'kkklmlmmlml.',
        'kkkllmlmmnl.',
        'kkl.pqrrrss.',
        'kkl.pquursst',
        '.kl.pqr#rsst',
        '.kk.klmmnnml',
        '..k.kllmmnm.',
        '....kkllmml.',
        '.....kkllm..',
        '......kkl...',
    ],
    'straw': [
        '.....34453.....',
        '....2344553....',
        '....2344553....',
        '....2334553....',
        '...223445543...',
        '...223345543...',
        '...KLLMMMLLK...',
        '...223445543...',
        '.12234455554321',
        '....pqqrrrs....',
        '....pquursst...',
        '....pqr#rsst...',
        '....pqrrrrs....',
        '....pquuuuuv...',
        '....pqrr#rs....',
        '.....pqrrs.....',
        '......pqq......',
    ],
    'veil': [
        '...lmnno....',
        '.klmnnoonm..',
        'kklmnonnnml.',
        'kkllmnnnnml.',
        'kklmmnnnnnl.',
        'kkll.qrrsml.',
        'kkl.pquursm.',
        'kkl.pq#rr#st',
        'kkl.66777788',
        '.kl.6E7E7E78',
        '.kll66777787',
        '..kl6667778.',
        '..kkl66677..',
        '...kkl666...',
    ],
    'scarf': [
        '.P.lmnno....',
        'OPOmnn9onm..',
        '.Nlmnonnnml.',
        'kk9lmnn9nml.',
        'kklmmnnnnnl.',
        'kkll.qrssml.',
        'kkl.pqursst.',
        'kkl.pqr#rsst',
        '.kl.pqrrsss.',
        '.kl.pqr99s..',
        '.kll.pqrs...',
        '..kklllmm...',
        '...kkllm....',
    ],
    'pot': [
        '...xyyzzzzy...',
        '...yzzZZzzy...',
        '...yzZZzzzyx..',
        '...yzZzzzzyx..',
        '.xyyzzzzzzyyx.',
        '.x.yzzzzzzyx.x',
        '...xyyyyyyyxx.',
        '....pquursst..',
        '....pqQ#rsst..',
        '....pqrrrrs...',
        '....pquuuuuv..',
        '....pqrr#rs...',
        '.....pqrrs....',
        '......pqq.....',
    ],
    'marshal': [
        '.........J......',
        '........JJ......',
        '........IJ......',
        '.....lmnIno.....',
        '...klmnnLMonm...',
        '..kklmnoLMnnml..',
        '..kklmmnnnnnml..',
        '.kkllmlmnnmlml..',
        '.kklmlmmnmlmml..',
        '.kkllmlmmlmlml..',
        '.kkklmlmlmmlml..',
        '..kkllmlmmlml...',
        '..kkkllmlmml....',
        '....pqrrrss.....',
        '....pq######....',
        '....pq#zz#z#t...',
        '....pqrrrrs.....',
        '...uuuuuuuuuu...',
        '....puur#ruu....',
        '.....pqrrs......',
        '......pqq.......',
    ],
    'elder': [
        '............',
        '....HIIJJ...',
        '...HIIJJJI..',
        '...HIHIHIJI.',
        '...HHIIIIII.',
        '....pqrrrss.',
        '....pqzzrsst',
        '....pqr#rsst',
        '....pqrrrrs.',
        '....yzzZzzzy',
        '....yzzZZzz.',
        '.....yzzZz..',
        '.....yyzzz..',
        '......yyz...',
    ],
}

# ---------------------------------------------------------------- bodies
PARTS = {
    'torso': [
        '....bccdd.....',
        '..abccddeed...',
        '.abbccdddeIJc.',
        '.abbccddddIJdc',
        'aabbcccdddHIdc',
        'aabbbccddddcdc',
        'aabbbcccdddcdb',
        '.abbbbcccddcdb',
        '.aabbbccccdccb',
        '.aabbbbcccccbb',
        '..aabbbbccccb.',
        '..aaabbbbcccb.',
    ],
    'torso_dress': [
        '....lmmnn.....',
        '..klmmnnoon...',
        '.kllmmnnnoEdc.',
        '.kklmmnnddEddc',
        'kkklmmcdddEEdc',
        'kkllmccdddddcc',
        'akllbccdddddcb',
        '.aklbbcccdddcb',
        '.aabbbccccdccb',
        '.aabbbbcccccbb',
        '..aabbbbccccb.',
        '..aaabbbbcccb.',
    ],
    'torso_medic': [
        '....bccdd.....',
        '..abccddeed...',
        '.abbccIJJJJdc.',
        '.abbcIJJOJJJdc',
        'aabbcIJOOOJJdc',
        'aabbbIJJOJJIdc',
        'aabbbcIIJJIcdb',
        '.abbbbcccddcdb',
        '.aabbbccccdccb',
        '.aabbbbcccccbb',
        '..aabbbbccccb.',
        '..aaabbbbcccb.',
    ],
    'torso_coat': [
        '....bccdd.....',
        '..abccddeed...',
        '.abbccdddeEdc.',
        '.abbccdLEMEddc',
        'aabbccdELEEEdc',
        'aabbbccddddEdc',
        'aabbbcccddddcb',
        '.abbbbcccddEdb',
        '.aabbbccccdccb',
        '.aabbbbccccEbb',
        '..aabbbbccccb.',
        '..aaabbbbcccb.',
    ],
    'torso_front': [
        '.....bccd.....',
        '..abccddddcc..',
        '.abbccdIJdddc.',
        'abbbccdIJddddc',
        'abbbccdHIddddc',
        'abbbcccdIdddcc',
        '.abbbccddddcc.',
        '.aabbbccddccb.',
        '.aabbbbcccccb.',
        '..aabbbccccb..',
        '..aabbbbcccb..',
        '..aaabbbbccb..',
    ],
    'belt': [
        'ABBCBBCBBCBB',
        'AEBBEBBEBBEA',
    ],
    'belt_front': [
        'ABBCBBCBBCBA',
        'AEBBEBBEBBEA',
    ],
    'arm': [
        '.bcddd.........',
        'bccddedd.......',
        'bccdddec.......',
        'bbccddec.......',
        'bbccdddc.......',
        'abbccddc.......',
        'abbcccdcc......',
        '.abbccdddddd...',
        '.aabbcccccccsst',
        '..aabbbbbbbbrss',
        '...aaaaaaaa.qr.',
    ],
    'arm_rolled': [
        '.bcddd.........',
        'bccddedd.......',
        'bccdddec.......',
        'bbccddec.......',
        'bbccdddc.......',
        'aaaaaaaa.......',
        'pqqrrsss.......',
        '.pqqrrsssss....',
        '.ppqqrrrrrrsst.',
        '..ppqqqqqqqrss.',
        '...pppppppp.qr.',
    ],
    'far_hand': [
        'rst',
        'rss',
        'qrr',
    ],
    'arm_up_back': [
        '.r.s.s.',
        '.rsrsrs',
        '.qrrsss',
        '.qrrss.',
        '.abccd.',
        '.abccd.',
        '.abccdd',
        '.abbcdd',
        '..abccd',
        '..abbcdd',
        '..aabccd',
        '...abbcd',
        '...aabcc',
        '....abbc',
    ],
    'arm_up_front': [
        '.s.s.t..',
        'rsrsst..',
        'rrssst..',
        '.rsst...',
        '.bcdde..',
        '.bcdde..',
        'bbcdde..',
        'bbccde..',
        'bccdd...',
        'bbccdd..',
        'bccddc..',
        'bccdd...',
        'ccddc...',
        'cddc....',
    ],
    'futa': [
        '.ghhiiiijjih....',
        '.ghhiiiijjjih...',
        'gghhiihijjjjih..',
        'gghhiihiijjjih..',
        'gghhihhiijjjjih.',
        'fgghihhiiijjjih.',
        'kllmmmmnnnnmmmlk',
        'DEDEDEDEDEDEDEDE',
        'fgghhhhiiiijjjih',
    ],
    'futa_front': [
        '.ghhiiijjiih..',
        '.ghhiiijjjih..',
        'gghhiihjjjiih.',
        'gghhiihijjjih.',
        'gghhihhiijjjih',
        'fgghihhiijjjih',
        'kllmmmnnnnmmlk',
        'DEDEDEDEDEDEDE',
        'fgghhhiiijjjih',
    ],
    'futa_run': [
        '...ghhiiiijjih.....',
        '..gghhiiiijjjih....',
        '..gghiihijjjjjih...',
        '.gghhiihiijjjjih...',
        '.gghhihhiiijjjjih..',
        'fgghhihhiiijjjjjih.',
        'kllmmmmmnnnnnmmmmlk',
        'DEDEDEDEDEDEDEDEDED',
        '.fgghhhhiiiijjjih..',
    ],
    'futa_kneel': [
        '..ghhiiiijjjih....',
        '.gghhiihijjjjjih..',
        'gghhiihiijjjjjjih.',
        'gghhihhiijjjnnnml.',
        'fgghihhiih........',
        'fgghihhiih........',
        'kllmmmmnnl........',
    ],
    'leg': [
        '.pqrrs.....',
        '.pqrrss....',
        '.pqrrrs....',
        '.pqrrrs....',
        '.pqrrs.....',
        '..pqrs.....',
        '..pqrs.....',
        '..pqrr.....',
        '..pqrrs....',
        '.pqrBrrsss.',
        'pqrrBrrrsst',
        'AAAAAAAAAAA',
    ],
    'leg_back': [
        '....pqrrs.',
        '...pqrrss.',
        '..pqrrrs..',
        '.pqrrrs...',
        '.pqrrs....',
        'pqrrs.....',
        'pqrBs.....',
        'pqrrs.....',
        'Apqr......',
        'AA........',
    ],
    'leg_fwd': [
        '.pqrrs.......',
        '..pqrrs......',
        '..pqrrrs.....',
        '...pqrrrs....',
        '...pqrrs.....',
        '....pqrs.....',
        '....pqrs.....',
        '....pqrrs....',
        '...pqrBrrsss.',
        '..pqrrBrrrsst',
        '..AAAAAAAAAAA',
    ],
    'shin_kneel': [
        '.pqrrs.....',
        '.pqrrs.....',
        '.pqrrs.....',
        '.pqrrss....',
        'pqrBrrsss..',
        'pqrBrrrsst.',
        'AAAAAAAAAAA',
    ],
    'foot_back': [
        'pqrrrs....',
        'pqrBrrsss.',
        'AAAAAAAAA.',
    ],
    'leg_front_l': [
        '.pqrrs....',
        '.pqrrss...',
        '.pqrrrs...',
        '.pqrrrs...',
        '.pqrrs....',
        '..pqrs....',
        '..pqrs....',
        '..pqrr....',
        '.pqrrrs...',
        'pqrBrrss..',
        'pqrBrrrst.',
        'AAAAAAAAA.',
    ],
    'skirt_long': [
        '..bbcccdddddc.....',
        '..abbccdddddcc....',
        '.abbcccddddddc....',
        '.abbccdcdddddcc...',
        '.abbccdcddddddc...',
        'aabbccdcddddddc...',
        'aabbcddcdddddddc..',
        'aabbcdccddddddec..',
        'aabbcdcdddddddec..',
        'aabccdcddddddeedc.',
        'aabccdcdddddeeddc.',
        'aabcddcddddeedddc.',
        'abbcdccdddeeddddcc',
        'abbcdcddddeddddddc',
        'abbcdcdddddddddddc',
        'KLLLLLLMMMMMMLLLLK',
        'EDEDEDEDEDEDEDEDED',
        'KKLLLLLLLLLLLLLLKK',
    ],
    'shoe_pair': [
        'ABBC.....ABBBC',
        'AAAAA....AAAAAA',
    ],
    'tunic_skirt': [
        '.bbccdddddc....',
        '.abbccdddddc...',
        'abbcccddddddc..',
        'abbccdcdddddc..',
        'abbccdcddddddc.',
        'abbcddcddddddc.',
        'abbcdccdddddddc',
        'NOOOOOPPPPPOOON',
    ],
    'trouser_leg': [
        '.ghijih..',
        '.ghiijh..',
        '.ghijih..',
        '.ghiijh..',
        '.ghijih..',
        '.ghiijh..',
        '..ghijh..',
        '..ghiih..',
        '..DEEED..',
        '..ABBC...',
        '.ABBBCC..',
        'AAAAAAAA.',
    ],
    'coat_skirt': [
        '.bbcccddddddc...',
        '.abbccdddddEcc..',
        'abbcccddddddc...',
        'abbccdcddddEdc..',
        'abbccdcdddddddc.',
        'abbcddcdddddEdc.',
        'aabbccccccccccc.',
    ],
    'boot_leg': [
        '.fghhi...',
        '.fghhi...',
        '.fghhi...',
        '.ABBCC...',
        '.ABBCC...',
        '.ABCBC...',
        '.ABBCC...',
        '.ABBCC...',
        '.ABBC....',
        '.ABBCC...',
        '.ABBBCC..',
        'AABBBBCCC',
        'AAAAAAAAA',
    ],
    # gear. Rank is worn at the belt.
    'jambiya_s': ['uE.', 'OP.', 'NOP', '.NO'],
    'jambiya': [
        'uv....',
        'uE....',
        'uv....',
        'OPO...',
        'OEO...',
        'NOPO..',
        'NOEO.O',
        '.NOPOP',
        '..NOOO',
        '...NN.',
    ],
    'jambiya_l': [
        '.uvvu.........',
        '.uEEu.........',
        '.uvvu.........',
        '.uEEu.........',
        'NOPPON........',
        '.OEEPO........',
        '.OPPPO........',
        '.NOEPPO.......',
        '.NOPEPO.......',
        '..NOPEPO....O.',
        '..NOOPEPO..OP.',
        '...NOOPEPOOPP.',
        '....NOOPEPPO..',
        '.....NOOOOO...',
        '......NNNN....',
    ],
    'shawl': [
        '.lmn.',
        'klmno',
        'klmnn',
        'kllmn',
        'kklmm',
        '.klm.',
        '.kll.',
        '..kl.',
    ],
    'satchel': [
        '.ABBC.',
        'ABBCCC',
        'ABCBCC',
        'ABBBCC',
        'ABBBBC',
        'AABBBC',
        '.AAAA.',
    ],
    'armband': ['EEFFE', 'E#EE#', 'DEEED'],
    'wrench': ['Z.Z..', 'ZzZ..', '.zy..', '..zy.', '..zy.', '...zy', '..xzy', '..x.y'],
    'apron': [
        '..IJJJ..',
        '..IJJJ..',
        '.IJJJJJ.',
        '.IJLJJJ.',
        '.IJJJJJ.',
        'BBBCCBBB',
        'IJJJJJJJ',
        'IJJJJJJJ',
        'IJJ###JJ',
        'IJJJJJJI',
        'IJJJJJJI',
        'HJJJLJJI',
        'HIJJJJII',
        'HHIIIIIH',
    ],
    'sash': ['KL......', 'KLM.....', '.KLM....', '..KLM...', '...KLM..', '....KLM.', '.....KLM', '......KL'],
    'epaulet': ['DEFFE', 'DEEFE', '.D.D.'],
    'bandolier': ['EF......', 'AEF.....', '.AEF....', '..AEF...', '...AEF..', '....AEF.', '.....AEF', '......AE'],
    'shield': [
        '..xyyyyyyz..',
        '.xyyzzzzzzZ.',
        'xyyzzzzzzzzZ',
        'xyz######zzZ',
        'xyz#QQQQ#zzZ',
        'xyz######zzZ',
        'xyyzzzzzzzzZ',
        'xyEzzzzzEzzZ',
        'xyEEzzzEEzzZ',
        'xyzEzEzEzzzZ',
        'xyzzEEEzzzzZ',
        'xyzzEEEzzzzZ',
        'xyzzzEzzEzzZ',
        'xyyzzEEEEzzZ',
        'xyyzzzzzzzzZ',
        'xyxzzzzzzxzZ',
        'xyyzzzzzzzzZ',
        'xyyyzzzzzzzZ',
        'xyyyzzzzzzzZ',
        'xyxyzzzzzxzZ',
        'xyyyyzzzzzzZ',
        'xxyyyyzzzzzz',
        '.xxyyyyyyzz.',
        '..xxxxxxxx..',
    ],
    'ladle': ['.yzzy.', 'yzZZzy', 'yzzzzy', '.xyyx.', '..yz..', '..yz..', '..yz..', '..yz..', '..yz..', '..yz..', '..yz..'],
    'medic_pack': [
        '.KLLLK.',
        'HIJJJJI',
        'HJJOJJI',
        'HJOOOJI',
        'HJJOJJI',
        'HIJJJII',
        'HHIIIIH',
    ],
    'umbrella': ['.#.', '#.#', '#..', 'L..', 'LM.', 'LM.', 'KL.', 'LM.', 'KL.', 'LM.', 'KL.', 'LM.', '.#.'],
    'rope': ['XYYXYYXYYXYYXY', '..............', '..............', 'YXYYXYYXYYXYYX', '......XY......', '..............',
             'XYYXYYXYYXYYXY'],
    'post': ['.XY.', 'XYYX'] + ['.XY.', '.XX.'] * 23,
}

WEAPONS = {
    # grip = the pixel that sits under the near hand; fore = where the far hand holds on
    'rifle': dict(grip=(7, 4), fore=(19, 3), rows=[
        '..........................z.......',
        'WXXYYyyzzzzzzzzzzyyyyyyyyyzyyyyyyy',
        'WXXXYyyyyyyyyyyyXXYYYYYXxyyyyyyyyy',
        'WWXXXxyyyyxyyyxxWXXXXXXWxxxxxxx...',
        '.WWX..xyyx.xyyyx.WWWWW............',
        '.......yyx..xyyyx.................',
        '.......xx....xyyyx................',
        '..............xxxx................',
    ]),
    'hmg': dict(grip=(7, 6), fore=(22, 5), rows=[
        '.............xyyyyx.....................',
        '............x......x....................',
        '.....yyzzzzzzzzzzzzzzzzz................',
        'WXXyyzzZZZZzzzzzzzzzzzzzyxzxzxzxzxzxyyz.',
        'WXXYyyzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzZ',
        'WWXXyyyyyyyyyyyyyyyyyyyyyxxxxxxxxxxxxxx.',
        '.WWX..xyyx.xDEEEEEDx....................',
        '.......yyx.xDEFFFEDx....................',
        '.......xx..xDEEEEEDx....................',
        '...........xDDDDDDDx....................',
        '............xxxxxxx.....................',
    ]),
    'marksman': dict(grip=(8, 5), fore=(22, 4), rows=[
        '...........xyzzzzzzzyx....................',
        '...........yzZZzzzzzzy....................',
        '............x.......x.....................',
        'WXXXYYyyzzzzzzzzzzzzzyyyyyyyyyyyyyyyyyyyyz',
        'WWXXXYyyyyyyyyyyyXXYYYYYYXxxxxxxxxxxxxxxx.',
        '.WWXXXxyyyyxyyxxxWXXXXXXXW................',
        '..WWX..xyyx.xyyx..WWWWWW..................',
        '........yyx..xx...........................',
        '........xx................................',
    ]),
    'rpg': dict(grip=(14, 4), fore=(22, 4), rows=[
        '..............................NOOPPO......',
        'xx...........................NOOPPPPPO....',
        'xyyzzzzzzzzzzzzzzzzzzzzzzzzzyNOOPPPPPPPO..',
        'xyyyyyyyyyyyyyyyyyyyyyyyyyyyxNNOOOPPPPON..',
        'xx.....WXY......WXY..........NNOOOOON.....',
        '.......WXX......WXX...........NNNNN.......',
        '.......WW.......WW........................',
    ]),
    'shotgun': dict(grip=(7, 4), fore=(19, 3), rows=[
        '............................z...',
        'WXXYYyyzzzzzzzzzzzzzzzzzzzzzzyy.',
        'WXXXYyyyyyyyyyyXXYYYYYYXyyyyyyy.',
        'WWXXXxyyyyxxxxxWXXXXXXXWxxxxxx..',
        '.WWX..xyyx......................',
        '.......yyx......................',
        '.......xx.......................',
    ]),
    'pistol': dict(grip=(1, 3), fore=None, rows=[
        'yzzzzzzzzz',
        'yyyyyyyyyy',
        'xyyyxxxx..',
        'xyyx......',
        'xyyx......',
        '.xx.......',
    ]),
    'megaphone': dict(grip=(1, 5), fore=None, rows=[
        '.........IJ',
        '.......LMIJ',
        '.....LLMMIJ',
        '...KLLMMMIJ',
        'xyKLLLMMMIJ',
        'xyKLLLLMMIJ',
        '...KKLLLMIJ',
        '.....KKLLIJ',
        '.......KLIJ',
        '.........HI',
    ]),
    'detonator': dict(grip=(0, 1), fore=None, rows=[
        '....yz....',
        '..xyyyzz..',
        '....yz....',
        'KLLLLLLLMM',
        'KLLELLLLLM',
        'KLLLLLLLLL',
        'KKLLLLLLLK',
        'KKKKKKKKKK',
    ]),
}

RAMPS = dict(
    khaki=('#33290f', '#4d4020', '#786a3a', '#a08e54', '#cdb980'),
    olive=('#1e2a14', '#34442a', '#566a36', '#7e9048', '#b0bc74'),
    olive_d=('#181e10', '#2a3420', '#44522c', '#64743c', '#8c9858'),
    blue=('#1e2c40', '#2f4a66', '#4a6f92', '#7099b8', '#a8c8dc'),
    teal=('#16302e', '#265450', '#3e7c74', '#66a498', '#a0ccbc'),
    maroon=('#2e1016', '#501c24', '#7c2e34', '#a84c48', '#d08070'),
    sage=('#1c3422', '#2e5638', '#4c7c52', '#78a674', '#b0cca0'),
    rose=('#4a202c', '#743848', '#a05868', '#c88490', '#e8b8bc'),
    indigo=('#14121e', '#242236', '#383650', '#52506e', '#787696'),
    white=('#5e5a48', '#8c8870', '#bcb69a', '#e0dcc4', '#faf8ea'),
    cream=('#5a5038', '#8a7e5e', '#b4a882', '#d8ceaa', '#f2ecd2'),
    turban=('#6a6048', '#9c9274', '#c8c0a0', '#e8e2c8', '#fcfaec'),
    dark=('#1c1a18', '#34302a', '#504a40', '#706858', '#948a74'),
    black=('#0e0c0c', '#1e1c1c', '#302e2e', '#484644', '#6a6660'),
    redchk=('#3e1410', '#6a2418', '#983c28', '#c06040', '#e09068'),
    sky=('#34485a', '#56708a', '#7e9cb4', '#a8c4d6', '#d4e6f0'),
    stripe=('#6a5e44', '#9a8c68', '#c4b890', '#e2d8b4', '#f6f0d8'),
    skin1=('#5c3a26', '#946444', '#c08a60', '#e0b088', '#f6d4ac'),
    skin2=('#4a2c1c', '#7a4e30', '#a87448', '#cf9a68', '#ecc090'),
    skin3=('#3a2216', '#5e3c26', '#86583a', '#ac7a50', '#cc9c70'),
)


def pal(jacket='khaki', lower='cream', wrap='blue', skin='skin2', **kw):
    p = {'#': INK}
    for letters, name in (('abcde', jacket), ('fghij', lower), ('klmno', wrap), ('pqrst', skin)):
        for ch, c in zip(letters, RAMPS[name]):
            p[ch] = c
    p.update({'u': '#1c1612', 'v': '#3a2e26', 'w': '#5a4a3c',
              'x': '#22242c', 'y': '#454a56', 'z': '#7a8290', 'Z': '#b8c0c8',
              'W': '#3c2410', 'X': '#6e4420', 'Y': '#a06c34',
              'A': '#2a1a10', 'B': '#5a3a20', 'C': '#8a6038',
              'D': '#8a6414', 'E': '#d0a030', 'F': '#f4dc78',
              'H': '#8c866e', 'I': '#c8c2a8', 'J': '#f4f0e0',
              'K': '#5a1c18', 'L': '#a03828', 'M': '#d86a48',
              'N': '#1c4428', 'O': '#3c7c48', 'P': '#74b470', 'Q': '#f4f0e0',
              '1': '#5e4a1c', '2': '#8c7230', '3': '#b89a48', '4': '#dcc070', '5': '#f4e4a4',
              '6': '#121014', '7': '#24202a', '8': '#3c3644', '9': '#e89cb0'})
    p.update(kw)
    return p


def skin_arm(p):
    """The same arm shapes with bare skin instead of a sleeve."""
    q = dict(p)
    for a, b in zip('abcde', 'pqrst'):
        q[a] = p[b]
    return q


def compose(layers, flip=False, foot=None):
    """layers: (rows, x, y, palette). Each part is outlined on its own, then stacked in order."""
    minx = min(x for _, x, _, _ in layers) - 1
    miny = min(y for _, _, y, _ in layers) - 1
    maxx = max(x + max(len(r) for r in rows) for rows, x, _, _ in layers) + 1
    maxy = max(y + len(rows) for rows, _, y, _ in layers) + 1
    im = new(maxx - minx, maxy - miny)
    for rows, x, y, p in layers:
        part = outline(sprite(rows, p), INK)
        blit(im, part, x - 1 - minx, y - 1 - miny)
    fx, fy = foot or (0, maxy - 1)
    fx, fy = fx - minx, fy - miny
    bb = im.getbbox()
    im = im.crop(bb)
    fx, fy = fx - bb[0], fy - bb[1]
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
        fx = im.width - 1 - fx
    return im, fx, fy


TX, TY = 8, 16          # torso origin inside a figure's own space


def _head(L, name, p, dx=0):
    hd = HEADS[name]
    L.append((hd, TX + 2 + dx, TY + 2 - len(hd), p))


def _weapon(L, weapon, p, hand):
    wp = WEAPONS[weapon]
    gx, gy = wp['grip']
    wx, wy = hand[0] - gx, hand[1] - gy
    L.append((wp['rows'], wx, wy, p))
    if wp.get('fore'):
        fx, fy = wp['fore']
        L.append((PARTS['far_hand'], wx + fx, wy + fy, p))


def fighter(head, p, weapon='rifle', pose='ready', torso='torso', arm='arm', lower='futa',
            gear=(), band=False, bare=False, flip=False):
    """A standing or moving figure seen from the side, facing right."""
    L = []
    ap = skin_arm(p) if bare else p
    hand = (TX + 15, TY + 8)                    # the near hand
    if 'shawl' in gear:
        L.append((PARTS['shawl'], TX - 2, TY + 0, p))
    if 'satchel' in gear:
        L.append((PARTS['satchel'], TX - 5, TY + 6, p))
    if 'medic_pack' in gear:
        L.append((PARTS['umbrella'], TX + 0, TY - 9, p))
        L.append((PARTS['medic_pack'], TX - 6, TY + 5, p))
    # legs and lower garment
    if pose == 'ready':
        if lower == 'futa':
            L.append((PARTS['leg'], TX - 1, TY + 21, p))
            L.append((PARTS['leg'], TX + 6, TY + 21, p))
            L.append((PARTS['futa'], TX - 1, TY + 13, p))
            foot = (TX + 7, TY + 33)
        elif lower == 'skirt_long':
            L.append((PARTS['shoe_pair'], TX + 1, TY + 31, p))
            L.append((PARTS['skirt_long'], TX - 2, TY + 13, p))
            foot = (TX + 7, TY + 33)
        elif lower == 'tunic':
            L.append((PARTS['trouser_leg'], TX + 0, TY + 21, p))
            L.append((PARTS['trouser_leg'], TX + 7, TY + 21, p))
            L.append((PARTS['tunic_skirt'], TX - 1, TY + 13, p))
            foot = (TX + 7, TY + 33)
        elif lower == 'coat':
            L.append((PARTS['boot_leg'], TX + 0, TY + 20, p))
            L.append((PARTS['boot_leg'], TX + 7, TY + 20, p))
            L.append((PARTS['coat_skirt'], TX - 1, TY + 13, p))
            foot = (TX + 7, TY + 33)
    elif pose == 'run':
        L.append((PARTS['leg_back'], TX - 6, TY + 21, p))
        L.append((PARTS['leg_fwd'], TX + 6, TY + 22, p))
        L.append((PARTS['futa_run'], TX - 3, TY + 13, p))
        foot = (TX + 9, TY + 33)
    elif pose == 'kneel':
        L.append((PARTS['foot_back'], TX - 6, TY + 19, p))
        L.append((PARTS['shin_kneel'], TX + 9, TY + 15, p))
        L.append((PARTS['futa_kneel'], TX - 3, TY + 13, p))
        foot = (TX + 6, TY + 22)
    L.append((PARTS[torso], TX, TY, p))
    L.append((PARTS['belt'], TX + 1, TY + 12, p))
    for g in gear:
        if g == 'jambiya':
            L.append((PARTS[g], TX + 9, TY + 9, p))
        elif g == 'jambiya_s':
            L.append((PARTS[g], TX + 10, TY + 11, p))
        elif g == 'jambiya_l':
            L.append((PARTS[g], TX + 6, TY + 7, p))
        elif g == 'wrench':
            L.append((PARTS[g], TX + 9, TY + 9, p))
        elif g == 'sash':
            L.append((PARTS[g], TX + 3, TY + 2, p))
        elif g == 'bandolier':
            L.append((PARTS[g], TX + 4, TY + 2, p))
        elif g == 'apron':
            L.append((PARTS[g], TX + 6, TY + 4, p))
    if weapon:
        _weapon(L, weapon, p, hand)
    L.append((PARTS[arm], TX + 3, TY + 0, ap))
    if 'epaulet' in gear:
        L.append((PARTS['epaulet'], TX + 2, TY - 1, p))
    if band:
        L.append((PARTS['armband'], TX + 3, TY + 3, p))
    _head(L, head, p)
    if 'shield' in gear:
        L.append((PARTS['shield'], TX + 17, TY - 4, p))
    return compose(L, flip=flip, foot=foot)


def front(head, p, pose='handsup', gear=(), band=False, bare=False, flip=False):
    """Front-facing figure: surrendering, or tied to a post."""
    L = []
    ap = skin_arm(p) if bare else p
    if pose == 'tied':
        L.append((PARTS['post'], TX + 5, TY - 16, p))
    L.append((PARTS['leg_front_l'], TX - 1, TY + 21, p))
    L.append((PARTS['leg_front_l'], TX + 6, TY + 21, p))
    L.append((PARTS['futa_front'], TX + 0, TY + 13, p))
    if pose == 'handsup':
        L.append((PARTS['arm_up_back'], TX - 5, TY - 11, ap))
    L.append((PARTS['torso_front'], TX, TY, p))
    L.append((PARTS['belt_front'], TX + 1, TY + 12, p))
    if pose == 'tied':
        L.append((PARTS['rope'], TX, TY + 3, p))
    for g in gear:
        if g == 'jambiya_s':
            L.append((PARTS[g], TX + 7, TY + 11, p))
        elif g == 'apron':
            L.append((PARTS[g], TX + 3, TY + 3, p))
    if pose == 'handsup':
        if 'ladle' in gear:
            L.append((PARTS['ladle'], TX + 13, TY - 21, p))
        L.append((PARTS['arm_up_front'], TX + 10, TY - 11, ap))
        if band:
            L.append((PARTS['armband'], TX + 10, TY - 5, p))
    hd = HEADS[head]
    L.append((hd, TX + 0, TY + 2 - len(hd), p))
    return compose(L, flip=flip, foot=(TX + 7, TY + 33))


# ---------------------------------------------------------------- palettes and cast
P_YAZEED = pal('khaki', 'cream', 'blue', 'skin2')
P_SALEM = pal('white', 'redchk', 'teal', 'skin3', k='#5a4a10', l='#8c7230', m='#3c7c48', n='#d0a030', o='#f4dc78')
P_BILQIS = pal('indigo', 'indigo', 'maroon', 'skin2')
P_ARWA = pal('rose', 'stripe', 'sage', 'skin1')
P_ELDER = pal('sky', 'cream', 'teal', 'skin3')


def p_grunt(skin='skin2', coat='olive'):
    return pal(coat, 'dark', 'turban', skin, k=RAMPS['turban'][0], l=RAMPS['turban'][1], m=RAMPS['turban'][2],
               n=RAMPS['turban'][3], o=RAMPS['turban'][4])


def p_guard(skin='skin2'):
    return pal('black', 'black', 'black', skin)


def p_marshal(skin='skin1'):
    return pal('olive_d', 'black', 'black', skin)


def hero(name, pose='ready', weapon=None, flip=False):
    if name == 'yazeed':
        return fighter('wrap_beard', P_YAZEED, weapon or 'rifle', pose, gear=('shawl', 'jambiya'), flip=flip)
    if name == 'salem':
        return fighter('straw', P_SALEM, weapon or 'shotgun', pose, arm='arm_rolled',
                       gear=('wrench',), flip=flip)
    if name == 'bilqis':
        return fighter('veil', P_BILQIS, weapon or 'marksman', pose, torso='torso_dress',
                       lower='skirt_long', gear=('bandolier',), flip=flip)
    if name == 'arwa':
        return fighter('scarf', P_ARWA, weapon or 'rifle', pose, torso='torso_medic',
                       lower='tunic', gear=('medic_pack',), flip=flip)


def grunt(kind='rifle', skin='skin2', flip=False, face=None):
    g = p_grunt(skin)
    if kind == 'rifle':
        return fighter(face or 'wrap_stubble', g, 'rifle', gear=('jambiya_s',), band=True, flip=flip)
    if kind == 'rpg':
        return fighter(face or 'wrap_tache', g, 'rpg', pose='kneel', gear=('jambiya_s',), band=True, flip=flip)
    if kind == 'shield':
        return fighter(face or 'wrap_tache', g, 'pistol', gear=('jambiya_s', 'shield'), band=True, flip=flip)
    if kind == 'demo':
        return fighter(face or 'wrap_clean', g, 'detonator', pose='kneel', gear=('jambiya_s',), band=True, flip=flip)
    if kind == 'surrender':
        return front('wrap_panic', g, 'handsup', gear=('jambiya_s',), band=True, flip=flip)
    if kind == 'cook':
        return front('pot', g, 'handsup', gear=('apron', 'ladle'), flip=flip)
    if kind == 'guard':
        return fighter('masked', p_guard(skin), 'shotgun', gear=('jambiya', 'bandolier'), band=True, flip=flip)
    if kind == 'marshal':
        return fighter('marshal', p_marshal(skin), 'megaphone', torso='torso_coat', lower='coat',
                       gear=('sash', 'epaulet', 'jambiya_l'), flip=flip)


def detainee(freed=False, flip=False):
    return front('elder', P_ELDER, 'handsup' if freed else 'tied', flip=flip)


if __name__ == '__main__':
    sheet = new(760, 76, hexc('#8a8478'))
    x = 6
    items = [hero('yazeed'), hero('yazeed', 'run', 'hmg'), hero('salem'), hero('bilqis'), hero('arwa'),
             grunt('rifle'), grunt('rpg', 'skin3'), grunt('shield', 'skin3'), grunt('demo', 'skin1'),
             grunt('surrender', 'skin1'), grunt('cook'), grunt('guard'), grunt('marshal'), detainee()]
    for im, fx, fy in items:
        blit(sheet, im, x, 70 - fy)
        x += im.width + 5
    rect(sheet, 0, 70, 759, 70, '#5a544a')
    print('used width', x)
    save(sheet, 't_ms1.png', 1)
