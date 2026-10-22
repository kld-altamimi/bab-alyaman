# ms2.py - the cast, redrawn to the build measured from the arcade originals:
# about 40px tall and nearly as wide, a head a third of the height, barrel torso,
# thick arms, short wide-set legs. Three tones and a highlight per material, hard steps,
# black outlines on cloth and metal, dark brown outlines on skin.
from px import *

INK = '#120e0a'
INK2 = '#3c1c08'      # skin outline

# Tone letters (dark -> light):
#   top a b c d | lower garment f g h i | wrap k l m n | skin p q r s | hair u v w
#   metal x y z Z | wood W X Y | leather A B C | gold D E F | white H I J
#   red K L M | green N O P | blue R S T | black cloth U V G | straw 1 2 3 4 | canvas 5 6 7 8
#   '#' black line, '%' brown line, 'Q' eye white
SKIN = set('pqrs')

RAMPS = dict(
    khaki=('#3a3010', '#76683a', '#b8aa6c', '#e8dea8'),
    olive=('#232c0e', '#4c5c28', '#84944a', '#bcc884'),
    cream=('#5e5236', '#a09468', '#d8cea0', '#fbf6dc'),
    blue=('#1a2a48', '#365a88', '#6e9cc2', '#bcd8e8'),
    turban=('#6e6650', '#b0a88a', '#e4dec2', '#fffbef'),
    dark=('#1a1818', '#3a3632', '#645e52', '#958d78'),
    black=('#0c0c0e', '#24242a', '#43434c', '#6c6c76'),
    maroon=('#3c0c12', '#74202a', '#b04a44', '#e08c72'),
    redchk=('#5a1208', '#a4301c', '#dc6a3c', '#f8a870'),
    sage=('#1e3c22', '#3e7040', '#78aa68', '#b8d8a0'),
    rose=('#561c30', '#983e58', '#cc7484', '#f0b0b0'),
    navy=('#0e1420', '#1e2a40', '#38506c', '#6888a0'),
    white=('#6a6450', '#aca48a', '#e0dac0', '#fffbef'),
    teal=('#10302e', '#22585a', '#44888a', '#84bcb4'),
    sand=('#5a4c2c', '#9a8654', '#d0bc84', '#f2e6b8'),
    ochre=('#6a4a08', '#b8841c', '#e8b83c', '#ffe27a'),
    crimson=('#4a0c14', '#8c1c28', '#c8443c', '#f08c6c'),
    skin1=('#8a4c1c', '#cc8e52', '#f0c084', '#ffe6b6'),
    skin2=('#74400f', '#b87a40', '#e0a868', '#fad294'),
    skin3=('#552c0c', '#90592a', '#bc864c', '#e0b27a'),
)


def pal(top='khaki', lower='cream', wrap='blue', skin='skin2', **kw):
    p = {'#': INK, '%': INK2, 'Q': '#fffbef'}
    for letters, name in (('abcd', top), ('fghi', lower), ('klmn', wrap), ('pqrs', skin)):
        for ch, c in zip(letters, RAMPS[name]):
            p[ch] = c
    p.update({'u': '#241a14', 'v': '#4c3a2e', 'w': '#806a54',
              'x': '#1a1810', 'y': '#454032', 'z': '#807a60', 'Z': '#c4be98',
              'W': '#3e2008', 'X': '#8a4c18', 'Y': '#cc8640',
              'A': '#2c1808', 'B': '#6a3c18', 'C': '#a86c34',
              'D': '#7a5208', 'E': '#d49c1c', 'F': '#ffe264',
              'H': '#7c7660', 'I': '#c4bea2', 'J': '#fffbef',
              'K': '#6a0c08', 'L': '#b8301c', 'M': '#f0703c',
              'N': '#103c1c', 'O': '#2c7c3c', 'P': '#6cc068',
              '1': '#5e4a14', '2': '#a07c28', '3': '#d8b450', '4': '#f8e498',
              '5': '#2e3016', '6': '#5c6034', '7': '#929660', '8': '#c8cc98',
              'R': '#16264a', 'S': '#30588c', 'T': '#6c9cc8',
              'U': '#141216', 'V': '#2c2832', 'G': '#4e4a58'})
    p.update(kw)
    return p


def part(rows, p):
    """Fill-only rows -> outlined image. Skin edges get the brown line, the rest black."""
    w = max(len(r) for r in rows)
    g = ['.' * (w + 2)] + ['.' + r.ljust(w, '.') + '.' for r in rows] + ['.' * (w + 2)]
    out = []
    for y, row in enumerate(g):
        line = ''
        for x, ch in enumerate(row):
            if ch != '.':
                line += ch
                continue
            nb = []
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= yy < len(g) and 0 <= xx < len(row) and g[yy][xx] != '.':
                    nb.append(g[yy][xx])
            if not nb:
                line += '.'
            elif all(n in SKIN or n == '%' for n in nb):
                line += '%'
            else:
                line += '#'
        out.append(line)
    return sprite(out, p)


def compose(layers, flip=False, foot=None):
    """layers: (rows, x, y, palette), back to front. x, y are the fill's top-left."""
    minx = min(x for _, x, _, _ in layers) - 1
    miny = min(y for _, _, y, _ in layers) - 1
    maxx = max(x + max(len(r) for r in rows) for rows, x, _, _ in layers) + 1
    maxy = max(y + len(rows) for rows, _, y, _ in layers) + 1
    im = new(maxx - minx, maxy - miny)
    for rows, x, y, p in layers:
        blit(im, part(rows, p), x - 1 - minx, y - 1 - miny)
    fx, fy = foot or (0, maxy - 1)
    fx, fy = fx - minx, fy - miny
    bb = im.getbbox()
    im = im.crop(bb)
    fx, fy = fx - bb[0], fy - bb[1]
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
        fx = im.width - 1 - fx
    return im, fx, fy


# ---------------------------------------------------------------- heads (face right)
# A head is a face with a wrap, hat or scarf laid over it. The men's wrap is the Yemeni
# mashadda: a patterned shawl tied low and loose round the head, striped border showing,
# one tasselled end left hanging on the shoulder. Not a tall wound turban, no long tail.
# Faces are 13 wide: ear at the left, eye at column 8, nose tip at column 12.
FACES = {
    'yazeed': [            # moustache, stubble, grin
        '.pqqqq%%#qr..',
        'pqpqqrrqqrr..',
        'pppqqrrrqqrrs',
        '.pqqqqrqqqpp.',
        '.pqqqquuuuu..',
        '.ppvqqqJJq...',
        '..pvpqvqqq...',
        '...ppvpqq....',
    ],
    'salem': [           # broad nose, big moustache, wide grin; cropped hair behind the ear
        '.pqqqq%%#qr..',
        'uvpqqrrqqrr..',
        'uppqqrrrrqrrs',
        '.pqqqrrqqqqpp',
        '.pqquuuuuuuu.',
        '.ppqquJJJJq..',
        '..pqqquuuq...',
        '...ppqqqq....',
    ],
    'worried': [         # stubble, raised brow, wide eye, mouth open
        '.pqqqqu%%qq..',
        'pqpqqqQ#qrr..',
        'pppqqrrrqqrrs',
        '.pqqqqrqqqpp.',
        '.ppvqqqqqqq..',
        '.pvpvq###q...',
        '..pvpvqqq....',
        '...ppvpq.....',
    ],
    'qat': [             # moustache, squint, a cheek packed full
        '.pqqqq%%#qr..',
        'pqpqqrrqqrr..',
        'ppqrrsrqqqrrs',
        '.pqrssrrqqpp.',
        '.pqrrsruuuu..',
        '.ppqrrqq#q...',
        '..ppqqqqq....',
        '...pppqq.....',
    ],
    'youth': [           # clean shaven, nervous
        '.pqqqq%%#qr..',
        'pqpqqrrqqrr..',
        'pppqqrrrqqrrs',
        '.pqqqqrqqqpp.',
        '.pqqqqqqqqq..',
        '.ppqqqq##q...',
        '..ppqqqqq....',
        '...pppqq.....',
    ],
    'angry': [           # heavy brow, teeth bared
        '.pqqqqu%%#r..',
        'pqpqqrrqqrr..',
        'pppqqrrrqqrrs',
        '.pqqqqrqqqpp.',
        '.pqqquuuuuu..',
        '.ppqq#JJJJ#..',
        '..ppqqq###...',
        '...pppqq.....',
    ],
    'masked': [          # cloth over nose and mouth
        '.pqqqq%%#qr..',
        'pqpqqrrqqrr..',
        'UUVVGGGGGGGV.',
        '.UVVGGGGGGV..',
        '.UUVVGGGGV...',
        '.UUVVVGGV....',
        '..UUVVVV.....',
        '...UUVV......',
    ],
    'elder': [           # white brows, long white beard
        '.pqqqqII#qr..',
        'pqpqqrrqqrr..',
        'pppqqrrrqqrrs',
        '.pqqHIqrqqpp.',
        '.pHIIJJIIJJ..',
        '.HHIIJJJIJ...',
        '..HIIJJIJ....',
        '..HHIJJI.....',
        '...HIJI......',
        '...HIJ.......',
        '....HI.......',
    ],
    'veiled': [          # kohl-lined eye over a black veil hung with coins
        '.pqqqq##Q#r..',
        'pqqqqrrqqrr..',
        'UUVVVEVEVEVV.',
        '.UUVVVVGVVV..',
        '.UUVVVGVVV...',
        '.UUUVVVVV....',
        '..UUVVVV.....',
        '...UUVV......',
    ],
    'arwa': [            # round, cheerful
        '.pqqqq%%#qr..',
        '.pqqqrrrqqr..',
        '.pqqrrsrrqqr.',
        '.pqqrMrrqqp..',
        '.pqqqrrqLLq..',
        '..pqqqqqqq...',
        '...ppqqq.....',
    ],
}

WRAPS = {
    'shawl': [           # cream shawl, blue and red woven border
        '....lmmml...',
        '..lmmnnmml..',
        '.lmkmmnmkml.',
        'klkmmnkmmnml',
        'kllkllklllkk',
        '.SKSSKSSKSS.',
    ],
    'shawl_end': [
        'lmm.',
        'SKSK',
        'lmml',
        'SSSS',
        'KKKK',
        'l.m.',
    ],
    'check': [           # the militia's: a checked shemagh tied the same way
        '....lm9ml...',
        '..l9mnm9ml..',
        '.lmm9mnm9ml.',
        'k9mmm9mmm9ml',
        'kl9lll9lll9k',
        '.kklkklkklk.',
    ],
    'check_end': [
        'lm9.',
        'l9ml',
        '9mm9',
        'lm9l',
        'l.ml',
    ],
    'hood': [            # the Guard's: black, one yellow bar
        '....lm9ml...',
        '..l9mnm9ml..',
        '.lmm9mnm9ml.',
        'k9mmm9mmm9ml',
        'EEFEEFEEFEEE',
        '.kklkklkklk.',
    ],
    'hood_end': [
        'lmm.',
        'klml',
        'lmml',
        'kl.l',
    ],
    'basil': [           # a bunch of basil tucked upright into the fold, Taiz fashion
        'P.',
        'OP',
        'NO',
        '.N',
    ],
    'kufiya': [          # Tihama men's kufiya: finely woven bamboo, flat-topped, shaped like a fez
        '..23343443..',
        '..23434344..',
        '.2233434344.',
        '.2234343434.',
        '.1223434343.',
        '.1121212121.',
        '.1223344332.',
    ],
    'straw': [           # Tihama women's sun hat (zulla): high tapered crown, flat brim. Not worn by the squad.
        '.....23443.....',
        '....2334443....',
        '....2343443....',
        '....2334343....',
        '...22343444....',
        '...22334344....',
        '...12343443....',
        '112233344433221',
    ],
    'scarf': [           # headscarf worked with gold, coin band across the brow
        '....lmmml...',
        '..lmEnnmml..',
        '.lmkmnEmkml.',
        'klkmmmkmmEml',
        'kllmFEFEFEFk',
        'kll.........',
    ],
    'drape': [           # the scarf falling behind the head
        'klm..',
        'kllm.',
        'kklm.',
        'kklmm',
        'kkllm',
        '.kllm',
        '.kklm',
        '..kll',
    ],
    'drape_long': [      # a longer fall, to the waist
        'klm...',
        'kllm..',
        'kklmm.',
        'kkllm.',
        'kkllmm',
        'kkllmm',
        '.kllmm',
        '.kkllm',
        '.kkllm',
        '..kklm',
        '..k.kl',
    ],
    'flowered': [        # flowered scarf
        '....lmmml...',
        '..lmMnnmml..',
        '.lmmmnJmmml.',
        'klMmmmmmMmml',
        'kllmmJmmmmlk',
        'kll.........',
    ],
    'knot': [
        'lm.',
        'klm',
        '.kl',
    ],
    'pot': [             # a cooking pot worn as a helmet, handles and all
        '..yzzZZZzzy...',
        '..yzZZzzzzyx..',
        '..yzZzzzzzyx..',
        '..yzzzzzzzyx..',
        'xxyyzzzzzyyxxx',
        'x.xyyyyyyyx.x.',
    ],
    'cap': [             # embroidered skullcap
        '...HIIJI....',
        '.HIIJJJJIH..',
        'HIKJKJKJKIH.',
        'HIIIIIIIIIH.',
    ],
}

PARTS = {
    # ---- torsos, 14 wide
    'blazer': [
        '....bbcccb....',
        '..abbccddccb..',
        '.abbccdddJJb..',
        '.abbcccc#IJcb.',
        'aabbccc#cIJdcb',
        'aabbcc#ccIIdcb',
        'aabb#c#ccccdcb',
        'aabbccbcc#cccb',
        '.abb#cbcccccb.',
        '.aabbccc#cccb.',
        '..abbbccccbb..',
    ],
    'jacket': [   # field jacket, flap pocket
        '....bbcccb....',
        '..abbccddccb..',
        '.abbccdddccb..',
        '.abbcccccc#cb.',
        'aabbcccc###dcb',
        'aabbcccccccdcb',
        'aabb#ccccc#dcb',
        'aabbccbccccccb',
        '.abb#cbcccccb.',
        '.aabbccc#cccb.',
        '..abbbccccbb..',
    ],
    'undershirt': [      # white sleeveless vest, bare shoulders
        '....ppqqqp....',
        '..pqIJJqqrrq..',
        '.pIIJJJIqrrrq.',
        '.HIJJJJJIIqrq.',
        'HIIJJJJJJIIIq.',
        'HIIJJJJJJJIIH.',
        'HIIJJIJJJJIIH.',
        'HIIIJJIJJIIIH.',
        '.HIIJJJJJIIH..',
        '.HHIIJJJIIH...',
        '..HHIIIIHH....',
    ],
    'dress_top': [       # embroidered chest panel
        '....bbcccb....',
        '..abbccdcccb..',
        '.abbccdKEKcb..',
        '.abbcccEKEKcb.',
        'aabbcccKEKEccb',
        'aabbccccEKEdcb',
        'aabbccccKEKccb',
        'aabbccbcccccb.',
        '.abbccbcccccb.',
        '.aabbcccccccb.',
        '..abbbccccbb..',
    ],
    'medic_top': [       # bag strap across the chest
        '....bbcccb....',
        '..abbccdcccb..',
        '.abbccddcccb..',
        '.abbccAcccccb.',
        'aabbcccAccccb.',
        'aabbccccAcdccb',
        'aabbcccccAcccb',
        'aabbccbcccAccb',
        '.abbccbccccAb.',
        '.aabbcccccccA.',
        '..abbbccccbb..',
    ],
    'belt': [
        'DEEFEEFEEFEED',
        'DEFEDEFEDEFED',
    ],
    'belt_plain': [
        'ABBCBBCBBCBBA',
        'AABBABBABBABA',
    ],
    # ---- arms
    'sleeve': [
        '..bccdc..',
        '.bccdddcb',
        'bbccddccb',
        'abbccddcb',
        'aabb#ccb.',
        '.aabbcb..',
        '.aaaaa...',
    ],
    'short_sleeve': [    # undershirt sleeve, bare below
        '..IJJJI..',
        '.IIJJJJIH',
        'HIIJJJIIH',
        'HHIIIIIH.',
        'ppqqrrqp.',
        '.ppqqqp..',
        '.pqqqp...',
    ],
    'bicep': [           # bare upper arm
        '..pqqrq..',
        '.pqqrrrqp',
        'pqqrrsrqp',
        'pqqrrrrqp',
        'ppqqrrqp.',
        '.ppqqqp..',
        '.pqqqp...',
    ],
    'forearm': [         # bare, fist on the grip
        'pqqrq.......',
        'pqqrrqq.....',
        '.pqqrrrqqq..',
        '..pqqrrrrrrq',
        '...ppqqqrrsr',
        '......ppqqrq',
    ],
    'forearm_c': [       # sleeved to the wrist
        'abbcb.......',
        'abbcccb.....',
        '.abbccccbb..',
        '..abbccccpqq',
        '...aabbbqrsr',
        '......aapqrq',
    ],
    'forearm_e': [       # sleeved, gold-worked cuff
        'abbcb.......',
        'abbcccb.....',
        '.abbccccEb..',
        '..abbcccEpqq',
        '...aabbbErsr',
        '......aapqrq',
    ],
    'forearm_up': [      # reaching up to a shoulder weapon
        '........pqr',
        '.....bccqrs',
        '..abbcccbqr',
        'abbcccbb...',
        'aabbbb.....',
    ],
    'arm_raise': [       # thrown straight up, behind the head
        '.qrs..',
        'qrrr..',
        '.qrr..',
        '.bcc..',
        '.bccb.',
        '.abcc.',
        '..abcc',
        '..abcc',
        '..aabcc',
        '...abbc',
        '...aabb',
        '....aab',
    ],
    'arm_raise_f': [     # thrown up, in front of the face
        '..srq.',
        '..rrrq',
        '..rrq.',
        '..ccb.',
        '.bccb.',
        '.ccba.',
        'ccba..',
        'ccba..',
        'cbaa..',
        'bba...',
    ],
    'armband': [
        'EFFE',
        'E#FE',
        'DEED',
    ],
    'armband_s': [
        'EFE',
        'E#E',
    ],
    # ---- legs and lower garments
    'legs': [   # wide-set, shins splayed
        '....pqrrsq.....pqrrsq...',
        '...pqrrsq......pqrssrq..',
        '..ppqrrq.......ppqrsrq..',
        '..ppqrq.........pqrrrq..',
        '.ppqrq..........pqqrrq..',
        '.pqrq............pqrq...',
        '.pqArrq.........pqqArrq.',
        'pqAqArrs.......pqqAqArrs',
        'AAAAAAAA.......AAAAAAAAA',
    ],
    'pants': [           # trousers with worked cuffs, shoes
        '..ghhii.......ghhiii..',
        '..ghhii.......ghhiii..',
        '..ghhih.......ghhiih..',
        '..gghih.......gghih...',
        '..gghhi.......gghhi...',
        '..DEDED.......DEDED...',
        '.ABBCCCC.....ABBCCCC..',
        'ABBBCCCCC...ABBBCCCCC.',
        'AAAAAAAAA...AAAAAAAAA.',
    ],
    'futa': [   # cream, blue stripes, woven hem
        '...fghhhiiiihhhg....',
        '..fgghSiiiihghSgg...',
        '..fghhSh#iiihghSg...',
        '.ffghhShh#iiihhgSg..',
        '.fgghhShghiiiihgSg..',
        '.fghhhSggghhiiihgSg.',
        'SSKSSKSSKSSKSSKSSKSS',
    ],
    'futa_plain': [
        '...fghhhiiiihhhg....',
        '..fgghhiiiihghhgg...',
        '..fghhfh#iiihghhg...',
        '.ffghhfhh#iiihhghg..',
        '.fgghhfhghiiiihghg..',
        '.fghhhfggghhiiihghg.',
        'ffgghgffgghhhhhhggff',
    ],
    'futa_check': [      # red plaid
        '...KLLMLLKLLMLLK....',
        '..KKLLMLLKLLMLLKK...',
        '..KKKKKKKKKKKKKKK...',
        '.KKLLMLLKLLMLLKLLK..',
        '.KLLLMLLKLLMLLKLLKK.',
        '.KKKKKKKKKKKKKKKKKK.',
        'KKLLMLLKLLMLLKLLMLLK',
    ],
    'tunic': [           # knee-length dress skirt, green worked hem
        '...abbbccccbbba.....',
        '..aabbccccdcbbaa....',
        '..abbcbbcccdcbba....',
        '.aabbcbbbbccdcbba...',
        '.abbbcbbabbccdcbba..',
        '.abbbbbaaabbccdcbb..',
        'NOPONOPONOPONOPONOPO',
    ],
    'dress_long': [      # to the ankle, red and gold worked hem
        '....abbbccccbbba......',
        '...aabbccccdcbbaa.....',
        '...abbcbbcccdcbba.....',
        '..aabbcbbbbccdcbba....',
        '..abbbcbbabbccdcbba...',
        '..abbbcbaaabbccdcbb...',
        '.aabbbcbaaabbbccdcba..',
        '.abbbbcbaaabbbccdcbb..',
        '.abbbcbbaaaabbccddcba.',
        'aabbbcbbaaaabbbccdcbb.',
        'aabbbcbbaaaabbbccdcbba',
        'KEKEKEKEKEKEKEKEKEKEKE',
        'aabbbbbbaaaabbbbbcccba',
    ],
    'shoes': [
        '.ABBC........ABBBC....',
        'AAAAAA......AAAAAAA...',
    ],
    'thobe': [           # long white robe
        '....HIIIJJJJIIIH......',
        '...HHIIJJJJJJIIHH.....',
        '...HIIHIIJJJJJIIH.....',
        '..HHIIHIIIJJJJJIIH....',
        '..HIIIHIIHIJJJJIIH....',
        '..HIIIHIHHIIJJJJIIH...',
        '..HIIHIIHHIIIJJJIIH...',
        '.HHIIHIIHHHIIJJJJIIH..',
        '.HIIIHIIHHHIIIJJJIIH..',
        '.HIIIHIHHHHIIIJJJJIH..',
        '.HIIHIIHHHHIIIIJJJIIH.',
        '.HIIHIIHHHHHIIIJJJIIH.',
        '.HHIIIIIHHHHIIIIIIIHH.',
    ],
    'bare_feet': [
        '.pqqrrr......pqqrrr...',
        'pqqqqrrs....pqqqqrrs..',
    ],
    # ---- gear
    'jambiya': [
        '.DFD....',
        '.uvu....',
        '.DFD....',
        '.NOO...E',
        '.NOO..OE',
        '.NOPO.OO',
        '..NOPOON',
        '...NOON.',
    ],
    'jambiya_s': [       # the rank and file get a small one
        'DFD...',
        'uvu...',
        'NOO..E',
        'NOPOOO',
        '.NOON.',
    ],
    'pack': [            # strapped straw mat over a canvas satchel
        '12A34A2',
        '12A33A2',
        '.1A22A.',
        '.5667..',
        '566776.',
        '5667776',
        '566A676',
        '5566776',
        '5566676',
        '.55666.',
    ],
    'big_pack': [        # the medic's: mat, canvas, green crescent patch
        '...1223321..',
        '..122333221.',
        '.5667776....',
        '56677777665.',
        '566777777665',
        '5667HJJJH665',
        '566HJOOJJH65',
        '566HJOJJJH65',
        '566HJOOJJH65',
        '5667HJJJH765',
        '566777777665',
        '566677776665',
        '556677776655',
        '.5566666655.',
        '..55566555..',
    ],
    'jerrycan': [
        '.xx.KK.',
        'KLLLLLK',
        'KLMLMLK',
        'KLLMLLK',
        'KLMLMLK',
        'KLLLLLK',
        'KLLLLLK',
        'KKLLLKK',
        'KKKKKKK',
    ],
    'medic_bag': [       # green crescent
        '.HIIIIJ.',
        'HIJJJJJI',
        'HJJOOJJI',
        'HJOJJJJI',
        'HJOJJJJI',
        'HJJOOJJI',
        'HIJJJJII',
        '.HHIIII.',
    ],
    'umbrella': [
        '.WW',
        'W.W',
        '..W',
        '.KL',
        '.KL',
        '.LM',
        '.KL',
        '.LM',
        '.KL',
    ],
    'dallah': [          # brass coffee pot on the belt
        '..F..',
        '.DE..',
        '.DEF.',
        'DEEFE',
        'DEFFE',
        'DDEEE',
        '.DDE.',
    ],
    'bandolier': [
        'EF.......',
        'AEF......',
        '.AEF.....',
        '..AEF....',
        '...AEF...',
        '....AEF..',
        '.....AEF.',
        '......AEF',
    ],
    'sash': [
        'KL.......',
        'KLM......',
        '.KLM.....',
        '..KLM....',
        '...KLM...',
        '....KLM..',
        '.....KLM.',
        '......KLM',
    ],
    'cape': [
        '..UV.',
        '.UVVG',
        '.UVVG',
        'UUVVG',
        'UUVVG',
        'UUVGG',
        'UUVVG',
        'UVVGG',
        'UUVVG',
        'UUVG.',
        'UVV..',
        'U.V..',
    ],
    'apron': [
        '...IJJJ...',
        '...IJJJ...',
        '..IJJJJJ..',
        '..IJJLJJ..',
        '..IJJJJJ..',
        'BBBBCCBBBB',
        'IJJJJJJJJI',
        'IJJJJJXJJI',
        'IJJJJJJJJI',
        'IJLJJJJJJI',
        'IJJJJJJJJI',
        'IJJJJXJJJI',
        'HIJJJJJJII',
        'HIJJJJJJII',
        'HHIIIIIIIH',
    ],
    'rope': [
        'XYXYXYXYXYXYXYX',
        '...............',
        '...............',
        'YXYXYXYXYXYXYXY',
        '...............',
        '...............',
        'XYXYXYXYXYXYXYX',
    ],
    'post': ['.XY.', 'XYYX'] + ['.XY.', '.XX.', '.XY.', '.WX.'] * 11,
    'door': [            # a pickup door carried as a shield: mirror, stripe decal, scorpion tag
        '.....xxxxxxxxxx.',
        '....xTTTSTTTTTTx',
        '...xTTTSTTTTTTTx',
        'xx.xTTSTTTTTTSTx',
        'xyxxTSTTTTTTSTTx',
        'xx.xTTTTTTTSTTTx',
        '...xTTTTTTTTTTTx',
        '..HxxxxxxxxxxxxH',
        '..HIJJJJJJJJJJIH',
        '..HIJJJJJJJxxJIH',
        '..HIJJJJJJJJJJIH',
        '..HKKLLLMMMEEEFH',
        '..HKKLLLMMMEEEFH',
        '..HIJJJJJJJJJJIH',
        '..HIJJ#JJJ#JJJIH',
        '..HIJJJ###JJJJIH',
        '..HIJJ#####J#JIH',
        '..HIJJJ###JJ#JIH',
        '..HIJJ#JJJ##JXIH',
        '..HIJXJJJJJJJJIH',
        '..HIIJJJJJXXJIIH',
        '..HHIIIIIIIIIIHH',
        '...HHHHxxxxHHHH.',
    ],
}

PARTS.update({
    # ---- lean build (the rank and file): narrower trunk, thin arms, longer legs
    'jacket_l': [
        '...bbccb....',
        '.abbccddcb..',
        'abbccddcc#b.',
        'abbcccc###cb',
        'abb#ccccddcb',
        'abbcccccc#cb',
        'abbccbccccdb',
        '.ab#cbccccb.',
        '.abbccc#ccb.',
        '..abbccccb..',
    ],
    'sleeve_l': [
        '.bccdc.',
        'bccddcb',
        'bbcddcb',
        'abb#ccb',
        'aabbcb.',
        '.aabb..',
    ],
    'forearm_cl': [
        'abbcb......',
        'abbcccbb...',
        '.abbcccpqq.',
        '..aabbbqrsr',
        '.....aapqrq',
    ],
    'forearm_up_l': [
        '.......pqr',
        '....bccqrs',
        '.abbccbbqr',
        'abbccb....',
        'aabbb.....',
    ],
    'arm_raise_l': [
        '.qrs.',
        'qrrr.',
        '.qrr.',
        '.bcc.',
        '.bcc.',
        '.abc.',
        '..abc',
        '..abc',
        '..abcc',
        '...abc',
        '...aab',
    ],
    'arm_raise_fl': [
        '..srq',
        '..rrr',
        '..rrq',
        '..cb.',
        '.bcb.',
        '.cba.',
        'ccb..',
        'cba..',
        'ba...',
    ],
    'legs_l': [
        '....pqrsq.....pqrsq...',
        '...pqrsq......pqrssq..',
        '...pqrq.......pqrsrq..',
        '..ppqrq.......ppqrrq..',
        '..pqrq.........pqrrq..',
        '..pqrq.........pqrq...',
        '.pqrq...........pqrq..',
        '.pqArrq.........pqArrq',
        'pqAqArrs.......pqAqArrs',
        'AAAAAAAA.......AAAAAAAA',
    ],
    'futa_l': [
        '..fghhhiiihhg....',
        '.fgghhiiigihgg...',
        '.fghhfhhiigihhg..',
        'ffghhfhhhiigihg..',
        'fgghhfhgghiigihg.',
        'fgghhfhgghhiighg.',
        'fgghgffgghhhhggf.',
    ],
    'belt_l': [
        'ABBCBBCBBCA',
        'AABBABBABBA',
    ],
    # ---- heavy build: wide trunk, belly forward, thick arms
    'undershirt_h': [
        '.....ppqqqp......',
        '...IIIJJJqqII....',
        '..IIIJJJJIqIJI...',
        '.HIIJJJJJJIIJJI..',
        '.HIJJJJJJJJIJJI..',
        'HIIJJJJJJJJJIJJI.',
        'HIIJJJIJJJJJJIJI.',
        'HIIJJJJIJJJJJJII.',
        'HIIIJJJJJJJJJJIIH',
        '.HIIJJJJJJJJJJIIH',
        '.HHIIJJJJJJJJIIH.',
        '..HHIIIIIIIIIHH..',
    ],
    'jacket_h': [
        '.....bbcccb......',
        '...abbccdcccb....',
        '..abbccddccccb...',
        '.abbccccccc#ccb..',
        '.abbcccccc###ccb.',
        'aabbcccccccccdcb.',
        'aabbccccccccccccb',
        'aabbccbcccccccdcb',
        'aabbccbccccccccb.',
        '.abbccbccccc#ccb.',
        '.aabbcccccccccb..',
        '..aabbbcccccbb...',
    ],
    'short_sleeve_h': [
        '..IJJJJI..',
        '.IIJJJJJIH',
        'HIIJJJJIIH',
        'HIIJJJJIIH',
        'HHIIJJIIH.',
        'HHHIIIIH..',
        '.pqqrrqp..',
        '.ppqqqp...',
    ],
    'sleeve_h': [
        '..bccddc..',
        '.bccdddccb',
        'bbccdddccb',
        'bbcccddccb',
        'abbcccccb.',
        'abbbcccb..',
        '.aabbbb...',
        '.aaaaa....',
    ],
    'forearm_h': [
        'pqqrrq.......',
        'pqqrrrqq.....',
        'pqqrrsrrqqq..',
        '.pqqrrrrrrrrq',
        '..ppqqrrrrrsr',
        '....pppqqqrrq',
        '.......pppqq.',
    ],
    'forearm_ch': [
        'abbccb.......',
        'abbcccbb.....',
        'abbccccccbb..',
        '.abbcccccccpq',
        '..aabbbcccqrs',
        '....aaabbbqrr',
        '.......aaapq.',
    ],
    'legs_h': [
        '....pqqrrsq.......pqqrrsq...',
        '...pqqrrsq........pqqrssrq..',
        '..ppqqrrq.........ppqrrsrq..',
        '..ppqqrq...........pqqrrrq..',
        '.ppqqrq............pqqqrrq..',
        '.pqqrq..............pqqrq...',
        '.pqqArrq...........pqqqArrq.',
        'pqqAqArrs.........pqqqAqArrs',
        'AAAAAAAAA.........AAAAAAAAAA',
    ],
    'futa_check_h': [
        '....KLLMLLKLLMLLKLL....',
        '...KKLLMLLKLLMLLKLLK...',
        '..KKKKKKKKKKKKKKKKKKK..',
        '.KKLLMLLKLLMLLKLLMLLK..',
        '.KLLLMLLKLLMLLKLLMLLKK.',
        'KKKKKKKKKKKKKKKKKKKKKKK',
        'KKLLMLLKLLMLLKLLMLLKLLK',
    ],
    'futa_h': [
        '....fghhhhiiiiihhhg....',
        '...fgghhhiiiiigihhgg...',
        '..ffghhfhhiiiiigihhg...',
        '.ffghhhfhhhiiiiigihhg..',
        '.fgghhhfhgghhiiiigihg..',
        'ffghhhhfggghhhiiigihhg.',
        'ffgghhgfffgghhhhhhhggff',
    ],
    'belt_h': [
        'ABBCBBCBBCBBCBA',
        'AABBABBABBABBAA',
    ],
    'apron_h': [
        '....IJJJJ....',
        '....IJJJJ....',
        '...IJJJJJJ...',
        '...IJJLJJJ...',
        '..IJJJJJJJJ..',
        'BBBBBCCCBBBBB',
        'IJJJJJJJJJJJI',
        'IJJJJJJXJJJJI',
        'IJJLJJJJJJJJI',
        'IJJJJJJJJJJJI',
        'IJJJJJJJJXJJI',
        'IJJJJJJJJJJJI',
        'HIJJJJJJJJJII',
        'HIJJJJJJJJJII',
        'HHIIIIIIIIIIH',
    ],
    # ---- giant build (the Guard): a head taller, shoulders like a door
    'jacket_g': [
        '......bbcccccb.....',
        '....abbccdddcccb...',
        '..aabbccddddcccccb.',
        '.aabbcccddccccc#ccb',
        '.abbbccccccccc###cb',
        'aabbbcccccccccccdcb',
        'aabbbccccccccccc#cb',
        'aabbbcccbccccccccb.',
        'aabbbcccbcccccccdb.',
        '.abbbccbbccccccccb.',
        '.abbbbcbcccccc#ccb.',
        '.aabbbcbccccccccb..',
        '..abbbbccccccccb...',
        '..aabbbbcccccccb...',
        '...aabbbbcccccb....',
    ],
    'sleeve_g': [
        '...bccddc...',
        '..bccddddcb.',
        '.bbccdddccb.',
        'bbccddddccb.',
        'bbcccdddccb.',
        'abbcccdcccb.',
        'abbbcccccb..',
        '.abbbccccb..',
        '.aabbbbbb...',
        '..aaaaaa....',
    ],
    'forearm_cg': [
        'abbccb.........',
        'abbccccbb......',
        'abbcccccccbb...',
        '.abbccccccccpqq',
        '..aabbcccccqrrs',
        '....aabbbbbqrsr',
        '.......aaaapqrq',
    ],
    'legs_g': [
        '.....pqqrrsq.........pqqrrsq...',
        '....pqqrrsrq.........pqqrssrq..',
        '...ppqqrrsq..........pqqrrsrq..',
        '...ppqqrrq...........ppqrrsrq..',
        '..ppqqrrq.............pqqrrrq..',
        '..ppqqrq..............pqqqrrq..',
        '.ppqqrq................pqqrrq..',
        '.pqqArrq...............pqqArrq.',
        '.pqAqArrrq............pqqAqArrrq',
        'pqqAqAqrrs...........pqqqAqAqrrs',
        'AAAAAAAAAA...........AAAAAAAAAAA',
    ],
    'futa_g': [
        '....fghhhhiiiiiihhhhg....',
        '...fgghhhiiiiiigihhhgg...',
        '..ffghhfhhiiiiiigihhhg...',
        '..fgghhfhhhiiiiiigihhg...',
        '.ffghhhfhhghhiiiiigihhg..',
        '.fgghhhfhgghhhiiiiigihg..',
        'ffghhhhfggghhhhiiiigihhg.',
        'ffgghhgfffgghhhhhhhhhggff',
    ],
    'belt_g': [
        'DEEFEEFEEFEEFEEFD',
        'DEFEDEFEDEFEDEFED',
        'ADDDDDDDDDDDDDDDA',
    ],
    'cape_g': [
        '...UV..',
        '..UVVG.',
        '..UVVG.',
        '.UUVVG.',
        '.UUVVGG',
        '.UUVGGG',
        '.UUVVGG',
        'UUVVGGG',
        'UUVVVGG',
        'UUVVGG.',
        'UUVVVGG',
        'UUVVGGG',
        'UUVVVG.',
        'UUVVGG.',
        'UUVVVG.',
        'UVVVG..',
        'UUVG...',
        'UV.V...',
    ],
    'bandolier_g': [
        'EF..........',
        'AEF.........',
        '.AEF........',
        '..AEF.......',
        '...AEF......',
        '....AEF.....',
        '.....AEF....',
        '......AEF...',
        '.......AEF..',
        '........AEF.',
        '.........AEF',
    ],
    # ---- slim build: narrow shoulders, long line
    'dress_top_s': [
        '...bbccb....',
        '.abbccdccb..',
        'abbccdKEKb..',
        'abbcccEKEKb.',
        'abbcccKEKEcb',
        'abbccccEKEcb',
        'abbccccKEKcb',
        'abbccbccccb.',
        '.abbcbccccb.',
        '.abbccccccb.',
        '..abbccccb..',
        '..aabbccb...',
    ],
    'forearm_es': [
        'abbcb......',
        'abbcccbb...',
        '.abbccEpqq.',
        '..aabbEqrsr',
        '.....aEpqrq',
    ],
    'dress_long_s': [
        '...abbbccccbba......',
        '..aabbcccdcbbaa.....',
        '..abbcbbccdcbba.....',
        '.aabbcbbbccdcbba....',
        '.abbbcbabbccdcba....',
        '.abbbcbaabbccdcbb...',
        '.abbbcbaaabbccdcb...',
        'aabbbcbaaabbbcdcba..',
        'aabbcbbaaabbbccdcb..',
        'abbbcbbaaaabbccdcba.',
        'abbbcbbaaaabbbcdcbb.',
        'abbbcbbaaaabbbccdcba',
        'KEKEKEKEKEKEKEKEKEKE',
        'abbbbbbaaaabbbbbccba',
    ],
    'shoes_s': [
        '.ABBC.......ABBBC...',
        'AAAAAA.....AAAAAAA..',
    ],
    'thobe_top_s': [
        '...IIJJI....',
        '.HIIJJJJI...',
        'HIIJJJJJJI..',
        'HIIJJJIJJJI.',
        'HIIJJJIJJJJI',
        'HIIJJJIJJJJI',
        'HIIJJIIJJJJI',
        'HIIJJIJJJJI.',
        '.HIJJIJJJJI.',
        '.HIIJJJJJJI.',
        '..HIIJJJJI..',
        '..HHIIJJI...',
    ],
    'thobe_s': [
        '.HIIJJJJIH....',
        '.HIIJJJJJIH...',
        '.HIHIJJJJIH...',
        '.HIHIIJJJJIH..',
        'HIIHIIJJJJIH..',
        'HIIHIIHJJJJIH.',
        'HIIHIIHJJJJIH.',
        'HIIHIHHIJJJIH.',
        'HIHIIHHIJJJJIH',
        'HIHIIHHIIJJJIH',
        'HIHIIHHIIJJJIH',
        'HIHIHHHIIJJJIH',
        'HIHIHHHIIIJJIH',
        'HHIIIHHHIIIIHH',
    ],
    'bare_feet_s': [
        '.pqrr....pqrrr.',
        'pqqqrs..pqqqrrs',
    ],
    'rope_s': [
        'XYXYXYXYXYXYX',
        '.............',
        '.............',
        'YXYXYXYXYXYXY',
        '.............',
        '.............',
        'XYXYXYXYXYXYX',
    ],
    # ---- small build: short legs under a full-size trunk
    'pants_s': [
        '..ghhii.......ghhiii..',
        '..ghhih.......ghhiih..',
        '..DEDED.......DEDED...',
        '.ABBCCCC.....ABBCCCC..',
        'ABBBCCCCC...ABBBCCCCC.',
        'AAAAAAAAA...AAAAAAAAA.',
    ],
    'legs_s': [
        '..pqqrr.......pqqrrs..',
        '.ppqqrq......ppqqrrq..',
        '..pqqrq.......pqqrq...',
        '.pqqArrr.....pqqArrr..',
        'pqqAqArrs...pqqAqArrs.',
        'AAAAAAAAA...AAAAAAAAA.',
    ],
})

PARTS.update({
    # ---- action poses for the house build
    'legs_run': [
        '........pqrrsq....pqrrsq...',
        '.......pqrrq......pqrssrq..',
        '.....ppqrrq........pqrrsrq.',
        '....ppqrq...........pqrrrq.',
        '..ppqrq..............pqrrq.',
        '.pqrrq...............pqrq..',
        'pqArq................pqArrq.',
        'qAqr................pqAqArrs',
        'AAr.................AAAAAAAA',
        '.A.........................',
    ],
    'futa_run': [
        '....fghhhiiiihhhg.....',
        '...fgghSiiiihghSgg....',
        '..ffghhSh#iiihghSgg...',
        '.ffghhhShh#iiihhgSgg..',
        'ffgghhhShghiiiihgSgg..',
        'fgghhhhSggghhiiihgSgg.',
        'SSKSSKSSKSSKSSKSSKSSKS',
    ],
    'futa_crouch': [
        '..fghhhiiiiiiihhhg..',
        '.fgghSiiiiiihghhSgg.',
        'ffghhShh#iiiihghhSgg',
        'SSKSSKSSKSSKSSKSSKSS',
    ],
    'legs_crouch': [
        '..pqrq.......pqqrrq.',
        '.pqArrq.....pqqArrq.',
        'pqAqArrs...pqqAqArrs',
        'AAAAAAAA...AAAAAAAAA',
    ],
})

HAND = [
    'qrrs',
    'qrrr',
    'pqqr',
    '.pq.',
]

WEAPONS = {
    # a battered old rifle: cloth wound round the stock and handguard, magazine bound with tape
    'rifle': dict(grip=(8, 5), hand=(20, 2), rows=[
        '............................zy....',
        '.....xyyzzZzzzzzy.WXYYYXW..yzy..x.',
        'WXYYYyyzyyyyyyzyyyXXYYJKYXyyzzzzzyy',
        'WXXKJYyyy##yyyyyyxWXXJKXXWyyyyyyyyx',
        'WXXKJXxyyyyyzyyyyx.WWWWWWxxyyyyx.x.',
        'WWXXXX.xyyx.xyyzzyx...............',
        '.WWWW..xyyx.HIIIIIIx..............',
        '.......xyx...xyyzzyx..............',
        '..............xyyzzyx.............',
        '...............xyyyyx.............',
    ]),
    'shotgun': dict(grip=(8, 5), hand=(13, 3), rows=[
        '..........................z.',
        '.....xyyzzzzzzzzzzzzzzzzzzzz',
        'WXYYYyyyyyyyyyyyyyyyyyyyyyyy',
        'WXXKJYxyyzzzzzzzzzzzzzzzzzzy',
        'WXXKJXxyyyWXYYYYYXWyyyyyyyy.',
        'WWXXXX.xyyxWXXXXXXW.........',
        '.WWWW..xyyx.WWWWWW..........',
        '.......xyx..................',
    ]),
    'marksman': dict(grip=(8, 5), hand=(24, 2), rows=[
        '..............xyyzzzzzyx...................',
        '..............xyzZZzzzyx...................',
        '.....xyyzzzzzzyyxyyyyxyyy..................',
        'WXYYYYXXYYYYXXXXYYYJKYYYXXYYJKYYXyyyyyyyzzy',
        'WXXKJXXXXXXXXXXXXXXJKXXXXXXXJKXXWyyyyyyyyy.',
        'WXXKJXXxyyxWWWWWWWWWWWWWWWWWWWWW...........',
        'WWXXXX.xyyx................................',
        '.WWWW..xyx.................................',
    ]),
    'mg': dict(grip=(8, 5), hand=(22, 2), rows=[
        '...........................zy........',
        '.....xyyzzZzzzzzzy.xyyyyyyyzy.....x..',
        'WXYYYyyzyyyyyyyzyyyyzzzzzzzzzzzzzzyyy',
        'WXXXYYyyy##yyyyyyyxyyyyyyyyyyyyyyyyyx',
        'WXXXXXxyyyyyzyyyyx.xy..xy.........x..',
        'WWXXXX.xyyx.DEFEDEx..................',
        '.WWWW..xyyx.DEEFEDFE.................',
        '.......xyx..EFEDEEDEF................',
        '............DEDEFD.EDE...............',
        '....................FE...............',
    ]),
    'rpg': dict(grip=(15, 5), rows=[
        '............................NOOPO.....',
        'xx.........................NOOPPPO....',
        'xyyzzzzzzzzzzXYYYYYXzzzzzzyNOPPPPPPO..',
        'xyyyyyyyyyyyyXXXXXXXyyyyyyyxNOOPPPOON.',
        'xx....WXY.....WXY...........NNOOOON...',
        '......WXX.....WXX............NNNN.....',
        '......WW......WW......................',
    ]),
    'pistol': dict(grip=(1, 3), rows=[
        'xyzzzzzzzy',
        'xyyyyyyyyy',
        'xyyyxxxx..',
        'WXYx......',
        'WXYx......',
        '.WX.......',
    ]),
    'ladle': dict(grip=(1, 9), rows=[
        '.......yzzzy.',
        '......yzZZzzy',
        '......yzzzzzy',
        '.......yyyyy.',
        '......zy.....',
        '.....zy......',
        '....zy.......',
        '...zy........',
        '..zy.........',
        '.zy..........',
    ]),
    'dynamite': dict(grip=(3, 8), rows=[
        '....F..',
        '...F.E.',
        '....v..',
        '.KLMKLM',
        '.KLMKLM',
        '.JJJJJJ',
        '.KLMKLM',
        '.KLMKLM',
    ]),
}

# Where things sit, per build (fill coordinates; the sole of the foot is always the row above FOOT's y).
class Build:
    def __init__(self, **k):
        self.__dict__.update(k)


STD = Build(pack=(0, 12), legs=(1, 28), futa=(3, 22), torso=(6, 11), belt=(7, 20), jamb=(13, 19),
            grip=(20, 19), forearm=(10, 15), sleeve=(7, 11), face=(10, 6), wrap=(10, 0), foot=(13, 37))
LEAN = Build(pack=(1, 12), legs=(2, 27), futa=(4, 21), torso=(7, 11), belt=(8, 19), jamb=(14, 19),
             grip=(19, 18), forearm=(10, 15), sleeve=(8, 11), face=(9, 6), wrap=(9, 0), foot=(13, 37))
HEAVY = Build(pack=(-2, 13), legs=(-1, 28), futa=(1, 22), torso=(5, 10), belt=(6, 20), jamb=(15, 19),
              grip=(21, 20), forearm=(10, 16), sleeve=(6, 11), face=(11, 6), wrap=(11, 0), foot=(13, 37))
GIANT = Build(pack=(-3, 12), legs=(-2, 33), futa=(1, 26), torso=(4, 11), belt=(5, 24), jamb=(15, 23),
              grip=(23, 23), forearm=(10, 19), sleeve=(5, 11), face=(12, 6), wrap=(12, 0), foot=(14, 44))
SLIM = Build(pack=(1, 10), legs=(3, 21), futa=(3, 21), torso=(7, 9), belt=(8, 19), jamb=(13, 18),
             grip=(19, 16), forearm=(10, 13), sleeve=(8, 9), face=(9, 4), wrap=(9, -2), foot=(13, 37))
SMALL = Build(pack=(0, 15), legs=(2, 31), futa=(3, 25), torso=(6, 14), belt=(7, 23), jamb=(13, 22),
              grip=(20, 22), forearm=(10, 18), sleeve=(7, 14), face=(10, 9), wrap=(10, 3), foot=(13, 37))
PACK, LEGS, FUTA, TORSO, BELT, JAMB = STD.pack, STD.legs, STD.futa, STD.torso, STD.belt, STD.jamb
GRIP, FOREARM, SLEEVE, FACE, WRAP, FOOT = STD.grip, STD.forearm, STD.sleeve, STD.face, STD.wrap, STD.foot


def at(part, pos, p, dx=0, dy=0):
    rows = PARTS[part] if isinstance(part, str) else part
    return (rows, pos[0] + dx, pos[1] + dy, p)


def weapon(L, name, p, grip=GRIP, hand=True):
    w = WEAPONS[name]
    ox, oy = grip[0] - w['grip'][0], grip[1] - w['grip'][1]
    L.append((w['rows'], ox, oy, p))
    if hand and w.get('hand'):
        L.append((HAND, ox + w['hand'][0], oy + w['hand'][1], p))


def done(L, flip=False, foot=FOOT):
    return compose(L, flip=flip, foot=foot)


# ---------------------------------------------------------------- the squad
# Honey-coloured bamboo for Salem's kufiya (the good ones lean reddish).
KUFIYA = {'1': '#5a3610', '2': '#a66c2c', '3': '#d8a456', '4': '#f6dca0'}


def yazeed(flip=False, pose='ready'):
    """Stocky, the house build. Blue checked wrap, blazer, striped futa, jambiya."""
    p = pal('blue', 'cream', 'blue', 'skin2')
    p['9'] = '#e4dec2'
    B = STD
    dx, dy = 0, 0
    if pose == 'run':
        dx = 2
        L = [at('pack', B.pack, p, dx), at('legs_run', (-1, 27), p), at('futa_run', (2, 22), p)]
    elif pose == 'crouch':
        dy = 8
        L = [at('pack', B.pack, p, 0, dy), at('legs_crouch', (2, 33), p), at('futa_crouch', (2, 30), p)]
    else:
        L = [at('pack', B.pack, p), at('legs', B.legs, p), at('futa', B.futa, p)]
    L += [at('blazer', B.torso, p, dx, dy), at('belt', B.belt, p, dx, dy), at('jambiya', B.jamb, p, dx, dy)]
    weapon(L, 'rifle', p, (B.grip[0] + dx, B.grip[1] + dy))
    L += [at('forearm', B.forearm, p, dx, dy), at('sleeve', B.sleeve, p, dx, dy),
          at(FACES['yazeed'], B.face, p, dx, dy),
          at(WRAPS['check_end'], B.wrap, p, dx - 1, dy + 6), at(WRAPS['check'], B.wrap, p, dx, dy),
          at(WRAPS['basil'], B.wrap, p, dx + 1, dy)]
    return done(L, flip, B.foot)


def yazeed_run(flip=False):
    return yazeed(flip, 'run')


def yazeed_crouch(flip=False):
    return yazeed(flip, 'crouch')


def salem(flip=False):
    """Heavy. The Tihama man's woven bamboo kufiya, white shirt over the belly, plaid futa, fuel can."""
    p = pal('white', 'cream', 'cream', 'skin3', **KUFIYA)
    B = HEAVY
    L = [at('jerrycan', B.pack, p), at('legs_h', B.legs, p), at('futa_check_h', B.futa, p),
         at('undershirt_h', B.torso, p), at('belt_h', B.belt, p)]
    weapon(L, 'shotgun', p, B.grip)
    L += [at('forearm_ch', B.forearm, p), at('sleeve_h', B.sleeve, p),
          at(FACES['salem'], B.face, p), at(WRAPS['kufiya'], B.wrap, p, 0, -1)]
    return done(L, flip, B.foot)


def bilqis(flip=False):
    """Slim and a head-wrap taller. Veil hung with coins, worked dress, the long rifle."""
    p = pal('navy', 'navy', 'crimson', 'skin2')
    B = SLIM
    L = [at(WRAPS['drape_long'], B.wrap, p, -4, 5), at('shoes_s', B.legs, p, 0, 14),
         at('dress_long_s', B.legs, p), at('dress_top_s', B.torso, p), at('belt_l', B.belt, p),
         at('dallah', B.jamb, p, -1, 2)]
    weapon(L, 'marksman', p, B.grip)
    L += [at('forearm_es', B.forearm, p), at('sleeve_l', B.sleeve, p),
          at(FACES['veiled'], B.face, p), at(WRAPS['scarf'], B.wrap, p)]
    return done(L, flip, B.foot)


def arwa(flip=False):
    """Small, under a pack bigger than she is. Flowered scarf, umbrella."""
    p = pal('rose', 'cream', 'sage', 'skin1')
    B = SMALL
    L = [at('umbrella', B.pack, p, -1, -9), at('big_pack', B.pack, p, -7, -3),
         at(WRAPS['drape'], B.wrap, p, -3, 5),
         at('pants_s', B.legs, p), at('tunic', B.futa, p), at('medic_top', B.torso, p),
         at('belt_plain', B.belt, p)]
    weapon(L, 'rifle', p, B.grip)
    L += [at('forearm_c', B.forearm, p), at('sleeve', B.sleeve, p),
          at(FACES['arwa'], B.face, p), at(WRAPS['knot'], B.face, p, 5, 6), at(WRAPS['flowered'], B.wrap, p)]
    return done(L, flip, B.foot)


# ---------------------------------------------------------------- the Scorpion's men
MILITIA_WRAP = ('white', '#b8301c')


def militia_pal(skin='skin2'):
    p = pal('olive', 'dark', MILITIA_WRAP[0], skin)
    p['9'] = MILITIA_WRAP[1]
    return p


def _lean_base(p, B=LEAN):
    return [at('legs_l', B.legs, p), at('futa_l', B.futa, p), at('jacket_l', B.torso, p),
            at('belt_l', B.belt, p), at('jambiya_s', B.jamb, p)]


def _militia_head(L, face, p, B=LEAN):
    L += [at(FACES[face], B.face, p), at(WRAPS['check_end'], B.wrap, p, -1, 6), at(WRAPS['check'], B.wrap, p)]


def grunt(face='worried', skin='skin2', flip=False):
    """Lean, like the arcade's infantry."""
    p = militia_pal(skin)
    B = LEAN
    L = _lean_base(p)
    weapon(L, 'rifle', p, B.grip)
    L += [at('forearm_cl', B.forearm, p), at('sleeve_l', B.sleeve, p), at('armband_s', B.sleeve, p, 2, 2)]
    _militia_head(L, face, p)
    return done(L, flip, B.foot)


def rocketeer(skin='skin3', flip=False):
    p = militia_pal(skin)
    B = LEAN
    L = _lean_base(p)
    L += [at('sleeve_l', B.sleeve, p), at('armband_s', B.sleeve, p, 2, 2)]
    _militia_head(L, 'worried', p)
    weapon(L, 'rpg', p, grip=(19, 15))
    L += [at('forearm_up_l', (11, 14), p)]
    return done(L, flip, B.foot)


def doorman(skin='skin2', flip=False):
    """Stocky, behind a pickup door."""
    p = militia_pal(skin)
    B = STD
    L = [at('legs', B.legs, p), at('futa_plain', B.futa, p), at('jacket', B.torso, p),
         at('belt_plain', B.belt, p), at('jambiya_s', B.jamb, p, 1, 1),
         at('sleeve', B.sleeve, p), at('armband', B.sleeve, p, 2, 2)]
    _militia_head(L, 'qat', p, B)
    L += [at('door', (21, 10), p)]
    weapon(L, 'pistol', p, grip=(21, 12))
    L += [at('forearm_up', (11, 11), p)]
    return done(L, flip, B.foot)


def bomber(skin='skin1', flip=False):
    p = militia_pal(skin)
    B = LEAN
    L = [at('arm_raise_l', (4, 0), p)]
    weapon(L, 'dynamite', p, grip=(6, 0))
    L += _lean_base(p)
    L += [at('forearm_cl', B.forearm, p), at('sleeve_l', B.sleeve, p), at('armband_s', B.sleeve, p, 2, 2)]
    _militia_head(L, 'angry', p)
    return done(L, flip, B.foot)


def cook(skin='skin2', flip=False):
    """Heavy. Pot for a helmet, ladle for a club."""
    p = militia_pal(skin)
    B = HEAVY
    L = [at('legs_h', B.legs, p), at('futa_h', B.futa, p), at('jacket_h', B.torso, p),
         at('apron_h', (10, 13), p)]
    weapon(L, 'ladle', p, B.grip)
    L += [at('forearm_ch', B.forearm, p), at('sleeve_h', B.sleeve, p),
          at(FACES['salem'], B.face, p), at(WRAPS['pot'], B.wrap, p, -1, 0)]
    return done(L, flip, B.foot)


def surrender(skin='skin1', flip=False):
    p = militia_pal(skin)
    B = LEAN
    L = [at('arm_raise_l', (4, 0), p)] + _lean_base(p)
    _militia_head(L, 'worried', p)
    L += [at('arm_raise_fl', (20, 2), p), at('armband_s', (5, 5), p)]
    return done(L, flip, B.foot)


def guard(skin='skin2', flip=False):
    """Giant. Black from wrap to hem, one yellow bar, belt-fed gun."""
    p = pal('black', 'black', 'black', skin)
    p['9'] = '#6c6c76'
    B = GIANT
    L = [at('cape_g', (-2, 12), p), at('legs_g', B.legs, p), at('futa_g', B.futa, p),
         at('jacket_g', B.torso, p), at('bandolier_g', (8, 13), p), at('belt_g', B.belt, p),
         at('jambiya', B.jamb, p)]
    weapon(L, 'mg', p, B.grip)
    L += [at('forearm_cg', B.forearm, p), at('sleeve_g', B.sleeve, p), at('armband', B.sleeve, p, 4, 3),
          at(FACES['masked'], B.face, p), at(WRAPS['hood_end'], B.wrap, p, -1, 6), at(WRAPS['hood'], B.wrap, p)]
    return done(L, flip, B.foot)


def detainee(flip=False, freed=False):
    """Slim elder roped to a post, the arcade's prisoner in a thobe. Freed, he salutes."""
    p = pal('white', 'white', 'white', 'skin3')
    B = SLIM
    L = []
    if not freed:
        L.append(at('post', (3, -8), p))
    L += [at('bare_feet_s', (6, 35), p), at('thobe_s', (6, 21), p), at('thobe_top_s', B.torso, p)]
    if freed:
        L += [at('arm_raise_fl', (17, 2), p), at(FACES['elder'], B.face, p), at(WRAPS['cap'], B.wrap, p, 0, 2)]
    else:
        L += [at('rope_s', (6, 11), p), at(FACES['elder'], B.face, p), at(WRAPS['cap'], B.wrap, p, 0, 2)]
    return done(L, flip, B.foot)


def detainee_freed(flip=False):
    return detainee(flip, True)


MARSHAL = {
    'boots': [
        '...UVVGG..........UVVGGV....',
        '...UVVGG..........UVVGGV....',
        '...UVGVG..........UVVGVG....',
        '...UVVGG..........UVVGGV....',
        '...UVVGG..........UVVGG.....',
        '...UVVG...........UVVG......',
        '..UVVGGG.........UVVGGGG....',
        '.UVVVGGGGG......UVVVGGGGGG..',
        'UUVVVVVGGGG....UUVVVVVGGGGG.',
        'UUUUUUUUUUU....UUUUUUUUUUUU.',
    ],
    'skirt': [
        '....abbbcccccccccccccbE......',
        '...aabbcccccccdcccccccbE.....',
        '...abbbccbcccccdccccccbE.....',
        '..aabbccbbccccccdcccccbbE....',
        '..abbbccbccccccccdccccccE....',
        '.aabbbcbbcccbcccccdcccccbE...',
        '.abbbccbbccbbccccccdccccbE...',
        '.abbbccbcccbccccccccdccccbE..',
        'aabbbcbbcccbcccccccccccccbE..',
        'aabbbcbbccbbcccccccccccccbbE.',
        'EEEEEEEEEEEEEEEEEEEEEEEEEEEE.',
    ],
    'torso': [
        '......bbccccccb.........',
        '....abbcccddccccb.......',
        '...abbccccdddcccccb.....',
        '..abbccccccccccccccb....',
        '..abbcccccccccccEccb....',
        '.aabbccccccccccccccccb..',
        '.aabbcccccccccccEccccb..',
        '.aabbccccccccccccccccb..',
        'aaabbcccccccccccEcccdccb',
        'aaabbccccccccccccccddccb',
        'aaabbcccccccccccEccdcccb',
        'aaabbbccccccccccccccccb.',
        '.aabbbccccccccccEccccb..',
        '.aabbbbcccccccccccccbb..',
        '..aabbbbcccccccccccbb...',
        '..aaabbbbcccccccccbb....',
    ],
    'medals': [
        'LMSTOP',
        'LMSTOP',
        'E.E.E.',
        'F.F.F.',
    ],
    'sash': [
        'KLM.............',
        '.KLM............',
        '..KLLM..........',
        '...KLLM.........',
        '....KLLM........',
        '.....KLLM.......',
        '......KLLM......',
        '.......KLLM.....',
        '........KLLM....',
        '.........KLLM...',
        '..........KLLM..',
        '...........KLLM.',
        '............KLLM',
    ],
    'belt': [
        'DEEFEEFEEFEEFEEFEEFEEFED',
        'DEFEDEFEDEFEDEFEDEFEDEFE',
        'ADDDDDDDDDDDDDDDDDDDDDDA',
    ],
    'jambiya': [         # rank is worn at the belt
        '..DFFD.......',
        '..uvvu.......',
        '..uEEu.......',
        '..uvvu.......',
        '..DFFD.......',
        '.NOOPPO......',
        '.NOEPPO.....E',
        '.NOOPPO....EF',
        '.NOEPPPO..OOE',
        '..NOOPPO.OPPO',
        '..NOEPPPOPPO.',
        '...NOOPPPPO..',
        '....NOOOOO...',
        '.....NNNN....',
    ],
    'sleeve': [
        '..bccddc....',
        '.bccddddcb..',
        'bbccdddccb..',
        'bbcccddccb..',
        'abbccccccb..',
        'abbbccccb...',
        '.abbbcccb...',
        '.aabbbbb....',
    ],
    'far_arm': [         # the megaphone arm, coming from behind the chest
        '......pqr',
        '....EFqrs',
        '..bcEFrrq',
        'bbccEFq..',
        'bcccb....',
        'bccb.....',
    ],
    'forearm': [         # near arm, hand on the hilt
        'abbccb.......',
        'abbccccbb....',
        '.abbcccccEF..',
        '..aabbcccEFqq',
        '....aabbbEFrs',
        '.......aaEFqr',
    ],
    'megaphone': [
        '..........IJ.',
        '........LMIJ.',
        '......LLMMIJ.',
        '....KLLMMMIJJ',
        'xyyKLLLMMMIJJ',
        'xyyKLLLLMMIJJ',
        '.x..KKLLLMIJJ',
        '.xy...KKLLIJ.',
        '.xy.....KLIJ.',
        '..........HI.',
    ],
    'face': [            # aviators, a moustache with its own postcode
        '..pqqqqqqqqqqq...',
        '.pqqq#########q..',
        'pqpqqqqq#xxZx#rr.',
        'pppqqqqq#xxxx#rrs',
        '.pqqqrrqq####qrrs',
        '.pqqrrsrqqqqqqpp.',
        '.pqquuuuuuuuuuuuu',
        '.ppquvuuuuuuvuuu.',
        '..pqqqu#JJJ#qq...',
        '..ppqqqq###qqp...',
        '...pppqqqqqpp....',
    ],
    'wrap': [            # the biggest shemagh in the country, fanned crest, gold brooch
        '.J9J..............',
        'J9J9J....mmmm.....',
        '9J9J9J.mm9mnm9mm..',
        '.9J9Jmm9mmnmm9mmm.',
        '..kJm9mmm9mmm9mmmm',
        '..km9mmm9mmm9mmEFm',
        '..k9mml9mml9mmlFEk',
        '..kkl9lll9lll9llkk',
        '...kklkklkklkklkk.',
    ],
    'epaulette': [
        'DEFFFED',
        'EFEFEFE',
        'E.E.E.E',
    ],
}


def marshal(flip=False):
    """Fat and tall. The biggest shemagh, the most medals, the largest jambiya in the country."""
    p = pal('olive', 'black', 'white', 'skin1')
    p['9'] = '#b8301c'
    M = MARSHAL
    L = [(M['boots'], 4, 43, p), (M['skirt'], 3, 33, p), (M['far_arm'], 25, 13, p), (M['torso'], 5, 16, p),
         (M['sash'], 12, 17, p), (M['medals'], 20, 20, p), (M['belt'], 6, 31, p), (M['jambiya'], 17, 26, p),
         (M['megaphone'], 31, 7, p), (M['forearm'], 9, 24, p), (M['sleeve'], 5, 17, p),
         (M['epaulette'], 5, 15, p), (M['face'], 13, 6, p), (M['wrap'], 11, -2, p)]
    return compose(L, flip=flip, foot=(16, 52))


CAST = [('yazeed', yazeed), ('salem', salem), ('bilqis', bilqis), ('arwa', arwa),
        ('grunt', grunt), ('rocketeer', rocketeer), ('doorman', doorman), ('bomber', bomber),
        ('cook', cook), ('surrender', surrender), ('guard', guard), ('detainee', detainee),
        ('marshal', marshal), ('yazeed_run', yazeed_run), ('yazeed_crouch', yazeed_crouch),
        ('detainee_freed', detainee_freed)]
