# ms3.py - the cast, rebuilt on measurements re-taken from the arcade originals:
#   hero 38 rows tall: head 13 x 14 (hair or wrap 6 rows, face 8), trunk 14 wide, lower garment 18 wide
#   and 9 rows, feet 6 rows; the two legs stand close: 2 px between the soles, 4-5 at the ankle, and the
#   feet span 21 px, hardly wider than the hips.
#   faces: one black pixel for an eye in a shaded socket, a nose that sticks out one pixel with the
#   brightest tone on its tip, a small mouth (one or two white pixels of teeth over a short dark line),
#   a square chin with its own highlight; skin and hair carry a dark brown line, everything else black.
# Own drawings throughout: nothing here is copied from a reference sheet.
from px import *

INK = '#120e0a'
INK2 = '#3c1c08'      # the brown line: skin and hair

# Tone letters (dark -> light):
#   top a b c d | lower garment f g h i | wrap k l m n | skin p q r s (t: the speck on the nose) | hair u v w
#   metal x y z Z | wood W X Y | leather A B C | gold D E F | white H I J
#   red K L M | green N O P | blue R S T | black cloth U V G | straw 1 2 3 4 | canvas 5 6 7 8
#   '#' black line, '%' brown line, 'Q' eye white, '9' the wrap's pattern colour
SOFT = set('pqrstuvw%')

RAMPS = dict(
    khaki=('#3a3010', '#76683a', '#b8aa6c', '#e8dea8'),
    olive=('#28300e', '#566628', '#8ea04c', '#c6d488'),
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
    # skin: deep shadow, shadow, base, highlight. The base tone carries the face.
    skin1=('#6a3a14', '#a86a36', '#dca670', '#f8d8a4'),
    skin2=('#5a3010', '#94602c', '#cc9458', '#f0c48a'),
    skin3=('#44220a', '#744620', '#aa763e', '#d6a266'),
)


# the brightest point of a face (the tip of the nose): a warm near-white for each skin
SPECK = dict(skin1='#fff2d2', skin2='#fde6bc', skin3='#f0d0a0')


def pal(top='khaki', lower='cream', wrap='blue', skin='skin2', **kw):
    p = {'#': INK, '%': INK2, 'Q': '#fffbef'}
    for letters, name in (('abcd', top), ('fghi', lower), ('klmn', wrap), ('pqrs', skin)):
        for ch, c in zip(letters, RAMPS[name]):
            p[ch] = c
    p['t'] = SPECK[skin]
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


def part(rows, p, ink=None):
    """Fill-only rows -> outlined image. Skin and hair edges get the brown line, the rest black
    (or `ink`, when a part asks for its own line colour)."""
    w = max(len(r) for r in rows)
    g = ['.' * (w + 2)] + ['.' + r.ljust(w, '.') + '.' for r in rows] + ['.' * (w + 2)]
    pp = dict(p)
    pp['~'] = ink or INK
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
            elif all(n in SOFT for n in nb):
                line += '%'
            else:
                line += '~'
        out.append(line)
    return sprite(out, pp)


def compose(layers, flip=False, foot=None):
    """layers: (rows, x, y, palette[, ink]), back to front. x, y are the fill's top-left."""
    minx = min(l[1] for l in layers) - 1
    miny = min(l[2] for l in layers) - 1
    maxx = max(l[1] + max(len(r) for r in l[0]) for l in layers) + 1
    maxy = max(l[2] + len(l[0]) for l in layers) + 1
    im = new(maxx - minx, maxy - miny)
    for l in layers:
        rows, x, y, p = l[:4]
        blit(im, part(rows, p, l[4] if len(l) > 4 else None), x - 1 - minx, y - 1 - miny)
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
# A head is 13 x 14 with its line: four rows of wrap, the wrap's lower edge doing duty as the brow,
# then seven rows of face. Faces are 11 wide: nape at the left, eye at column 7, nose tip at column 10.
# Rows: eye, nose, cheek (ear at column 2), upper lip, mouth, lower lip, chin.
# The men's wrap is the Yemeni head shawl, tied low and loose, covering the back of the head, with one
# end left hanging. The rank and file get a head one pixel smaller each way, as the arcade's infantry do.
FACES = {
    'yazeed': [            # moustache, stubble along the jaw, mouth set
        '..rrrrq#rr.',
        '..qrrrrrrst',
        '..q%rrssrq.',
        '..qqrrrvuu.',
        '...pqrrrJ..',
        '...ppqr##r.',
        '....ppqrrs.',
    ],
    'salem': [           # round, cropped hair under the cap, big moustache, wide grin
        '.uvrrrq#rr.',
        '.uqrrrrrrst',
        '.qr%rsssrq.',
        '.qrrrruuuuu',
        '.qrrrrrJJJ.',
        '..qrrrr###.',
        '..qqrrrrrr.',
    ],
    'cook': [            # jowls, heavy brow, moustache, mouth turned down
        '.uvrrru#rr.',
        '.uqrrrrrrst',
        '..q%rssrrq.',
        '..qrrrvuuu.',
        '..qrrrrr#..',
        '...qrrr#rq.',
        '...qqrrrr..',
    ],
    'qat': [             # one cheek packed full, a leaf at the corner of the mouth
        '..rrrrq#rr.',
        '..qrrrrrrst',
        '..q%rsssrq.',
        '..qrsssruu.',
        '..qrrssrO#.',
        '...qrrrrr..',
        '....qqrrr..',
    ],
    'masked': [          # cloth over nose and mouth
        '..rrrru#rr.',
        '..UVVGGGGGV',
        '..UVVGGGGV.',
        '..UVVVGGGV.',
        '...UVVGGV..',
        '...UUVVV...',
        '....UUV....',
    ],
    'elder': [           # white hair and brow, a beard to the chest
        '.HIrrrI#rr.',
        '.HIrrrrrrst',
        '..q%rrsrqq.',
        '..HIIJIJJI.',
        '..HIIJJJI..',
        '...HIJJII..',
        '...HHIJI...',
        '....HIJI...',
        '....HIJ....',
        '.....HI....',
    ],
    'veiled': [          # kohl-lined eye over a black veil hung with coins
        '..rrrr#Q#r.',
        '..qrrrrrrr.',
        '..UVEVEVEVE',
        '..UVVVGVVV.',
        '...UVVGVVV.',
        '...UUVVVV..',
        '....UUVV...',
        '.....UV....',
    ],
    'arwa': [            # round and cheerful
        '..rrrrr#rr.',
        '..rrrrrrrs.',
        '..r%rMsrrr.',
        '...rrrrrr..',
        '...qrrrLL..',
        '....qrrr...',
        '.....qr....',
    ],
    # ---- the rank and file: 10 wide, six rows, eye at column 6, nose tip at column 9
    'worried': [         # brow up, eye wide, mouth open
        '..rrrQ#rr.',
        '..qrrrrrst',
        '..q%rsrrq.',
        '..pqrr##..',
        '...pqrJ#r.',
        '....pqrr..',
    ],
    'youth': [           # clean shaven, nervous
        '..rrrr#rr.',
        '..qrrrrrst',
        '..q%rssrq.',
        '..qrrrrr..',
        '...qrr##r.',
        '....qrrr..',
    ],
    'angry': [           # heavy brow, moustache, teeth bared
        '..rrru#qr.',
        '..qrrrrrst',
        '..q%rrrqq.',
        '..pqruuuu.',
        '...pq#JJ#.',
        '....ppqr..',
    ],
    'qat_l': [           # one cheek packed full, a leaf at the corner of the mouth
        '..rrrq#rr.',
        '..qrrrrrst',
        '..q%sssrq.',
        '..qrsssuu.',
        '...qrsrO#.',
        '....qqrr..',
    ],
}

WRAPS = {
    'check': [           # checked shemagh, wound low; it covers the back of the head to the nape
        '...lmnnnl..',
        '.klm9nnn9m.',
        'kl9mmn9nnnl',
        'k9lmm9mmn9l',
        'kl.........',
        'k9.........',
        '.k.........',
    ],
    'check_end': [       # the loose end, hanging behind the shoulder
        'l9',
        'km',
        'l9',
        'k.',
    ],
    'check_l': [         # the same, a size down
        '...lmnnl..',
        '.kl9nnn9m.',
        'k9lmn9nnml',
        'kl9m9lm9nl',
        'k9........',
        'kl........',
        '.k........',
    ],
    'hood': [            # the Guard's: black, one yellow bar across the brow
        '...lmnnnl..',
        '.klmmnnnmm.',
        'klmmmnnnnnl',
        'EEFEEFEEFEE',
        'kl.........',
        'kl.........',
        '.k.........',
    ],
    'hood_end': [
        'lm',
        'kl',
        'lm',
        'k.',
    ],
    'basil': [           # a sprig tucked upright into the fold, as Taiz men wear it on Fridays
        '.P',
        'OP',
        'NO',
    ],
    'kufiya': [          # the Tihama man's cap: finely woven bamboo, shaped like a fez
        '..2334443..',
        '..2343434..',
        '.223434344.',
        '.122121212.',
        '.123344332.',
    ],
    'pot': [             # a cooking pot worn as a helmet, handles and all
        '..yzzZZzzy..',
        '.yzzZZzzzzyx',
        '.yzZzzzzzzyx',
        'xyyzzzzzzyyx',
    ],
    'scarf': [           # headscarf worked with gold, a band of coins across the brow
        '...lmnnml..',
        '.klmEnnnml.',
        'klmmmnEnmml',
        'FEFEFEFEFEF',
        'kl.........',
        'kl.........',
        'kl.........',
    ],
    'drape_long': [      # the scarf falling behind the shoulder to the waist
        'klm.',
        'kllm',
        'kklm',
        'kklm',
        'kkll',
        'kkll',
        '.kll',
        '.kkl',
        '.kkl',
        '..kl',
        '..k.',
    ],
    'flowered': [        # flowered scarf
        '...lmnnml..',
        '.klmMnnnml.',
        'klmmmnJnmml',
        'klMmmmmmMml',
        'kl.........',
        'kl.........',
        'kll........',
    ],
    'drape': [
        'klm',
        'kll',
        'kkl',
        'kkl',
        '.kl',
        '.k.',
    ],
    'knot': [
        'lm',
        'kl',
    ],
    'cap': [             # embroidered skullcap
        '..HIJJJI...',
        '.HIKJKJKIH.',
        '.HIIIIIIIH.',
    ],
}

PARTS = {
    # ---- house build: trunk 12 wide
    'blazer': [
        '....bccb....',
        '..abccdcb...',
        '.abbcddccb..',
        '.abbcddcIJb.',
        'aabbccdcIJcb',
        'aabbcccc#Icb',
        'aabbccc#ccdb',
        'aabbcc#cccdb',
        'aabbcc#ccccb',
        'aabbbcc#cccb',
        '.abbbccc#ccb',
        '.aabbccccccb',
        '.aabbbcccbb.',
        '..aabbbbbb..',
    ],
    'jacket': [          # field jacket, flap pocket
        '....bccb....',
        '..abcddcb...',
        '.abccdddcb..',
        '.abccddcc#c.',
        'aabcccdc###c',
        'abbcccccccdc',
        'abbc#cccc#dc',
        'abbcccbccccc',
        'abbc#cbccccb',
        'aabbcccc#ccb',
        '.abbcccccbb.',
        '.aabbccccbb.',
        '.aabbbcccb..',
        '..aabbbbb...',
    ],
    'medic_top': [       # bag strap across the chest
        '....bccb....',
        '..abccdcb...',
        '.abbcddccb..',
        '.abbcAdcccb.',
        'aabbccAcccb.',
        'aabbcccAcdcb',
        'aabbccccAccb',
        'aabbccbccAcb',
        '.abbccbcccA.',
        '.aabbcccccb.',
        '..abbbcccb..',
    ],
    'belt': [
        'DEFEEFEEFEED',
        'DEDEFEDEFEDD',
    ],
    'belt_plain': [
        'ABBCBBCBBCBA',
        'AABBABBABBAA',
    ],
    'sleeve': [          # upper arm in the jacket
        '..bcddc.',
        '.bccdddc',
        'abccdddc',
        'abbccddc',
        'aabbcccb',
        '.aabbcb.',
        '..aabb..',
    ],
    'forearm': [         # sleeved to the wrist, fist on the grip
        'abcb........',
        'abbcccb.....',
        'aabbccccbb..',
        '.aabbcccqrrs',
        '..aaabbbqrsr',
        '.....aaapqrq',
    ],
    'forearm_up': [      # reaching up to a weapon held high
        '.........qrs',
        '......bccrrr',
        '...abcccbqr.',
        'abbccccb....',
        'aabbbbb.....',
    ],
    'armband': [
        'EFE',
        'E#E',
    ],
    'futa': [            # cream, blue stripes, woven hem; to mid-shin
        '..fghhiiihhg....',
        '.fgghSiiihgSg...',
        '.fghhSh#iihgSg..',
        '.fghhShh#iihSgg.',
        'ffghhShgh#iihSg.',
        'fgghhSgghhiihSgg',
        'fghhhSggghhiihSg',
        'SSKSSKSSKSSKSSKS',
    ],
    'futa_plain': [
        '..fghhiiihhg....',
        '.fgghhiiihghg...',
        '.fghhfh#iihghg..',
        '.fghhfhh#iihhgg.',
        'ffghhfhgh#iihhg.',
        'fgghhfgghhiihhgg',
        'fghhhfggghhiihhg',
        'ffgghffgghhhhggf',
    ],
    'legs': [            # bare shins and sandals; the feet stand close
        '..pqrrq.......pqrrs.',
        '..pqrrq.......pqrrs.',
        '..pqrrq.......pqrrq.',
        '.pqqArrq.....pqqArrq',
        'pqqAqArs....pqqAqArs',
        'AAAAAAAA....AAAAAAAA',
    ],
    'jambiya': [
        '.DFD..',
        '.uvu..',
        '.NOO.E',
        '.NOPOO',
        '..NOON',
    ],
    'jambiya_s': [       # the rank and file get a small one
        'DFD..',
        'NOO.E',
        'NOPOO',
        '.NON.',
    ],
    'pack': [            # rolled straw mat strapped over a canvas satchel
        '12A32',
        '12A32',
        '.1A2.',
        '5667.',
        '56776',
        '56776',
        '56A76',
        '55676',
        '55666',
        '.556.',
    ],
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
    # ---- lean build (the rank and file): trunk 10 wide, a row more leg
    'jacket_l': [
        '...bccb...',
        '.abccddcb.',
        'abccdddccb',
        'abcccdc##c',
        'abccccccdc',
        'abc#ccccdc',
        'abccbccccc',
        'abbcbccccb',
        '.ab#bccccb',
        '.abbccc#cb',
        '.aabbcccbb',
        '..abbbbbb.',
    ],
    'sleeve_l': [
        '.bcddc',
        'bccddc',
        'bccddc',
        'abccdb',
        'abbcb.',
        '.aab..',
    ],
    'forearm_l': [
        'abcb.......',
        'abbccb.....',
        '.abbcccqrr.',
        '..aabbbqrsr',
        '.....aapqrq',
    ],
    'forearm_up_l': [
        '........qrs',
        '.....bccrrr',
        '..abccbbqr.',
        'abbccb.....',
        'aabbb......',
    ],
    'arm_raise_l': [     # thrown straight up, behind the head
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
    'arm_raise_fl': [    # thrown up, in front of the face
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
        '..pqrr.......pqrs.',
        '..pqrr.......pqrs.',
        '..pqrq.......pqrr.',
        '..pqrq.......pqrq.',
        '.pqArrq.....pqArrq',
        'pqAqArs....pqAqArs',
        'AAAAAAA....AAAAAAA',
    ],
    'futa_l': [
        '..fghhiihg....',
        '.fgghhiihgg...',
        '.fghhfhiihg...',
        '.fghhfhhiihg..',
        'ffghhfhghiihg.',
        'fgghhfgghhiihg',
        'fgghhfgghhhihg',
        'fgghgffgghhhgf',
    ],
    'belt_l': [
        'ABBCBBCBBA',
        'AABBABBABA',
    ],
    # ---- heavy build: a belly 17 wide, feet a little further apart
    'shirt_h': [         # white shirt stretched over the belly, and nowhere near covering it
        '.....IJJJI...........',
        '...HIJJJJJII.........',
        '..HIJJJJJJJJII.......',
        '.HIIJJJJJJJJJJII.....',
        '.HIJJJJJJJJJJJJJII...',
        'HIIJJJJJIJJJJJJJJJI..',
        'HIIJJJJJJIJJJJJJJJJI.',
        'HIIJJJJJJJIJJJJJJJJJI',
        'HIIIJJJJJJJJJJJJJJJII',
        'HHIIIJJJJJJJJJJJJJIIH',
        '.HHIIIIIJJJJJJJIIIIH.',
        '..pqrrrrrrrssrrrrrrq.',
        '..pqrrrrrrrsssrrrrrrq',
        '..pqqrrrrrrr#rrrrrrrq',
        '...pqqrrrrrrrrrrrrrq.',
        '....ppqqqqqqqqqqqqq..',
        '......ppppqqqqqpp....',
    ],
    'jacket_h': [
        '.....bccccb......',
        '...abccdddccb....',
        '..abccdddddccb...',
        '.abcccdddcc#ccb..',
        '.abccccccc###ccb.',
        'abbcccccccccddcb.',
        'abbccccccccccdccb',
        'abbcccbccccccddcb',
        'abbcccbccccccccb.',
        '.abbccbccccc#ccb.',
        '.abbccccccccccb..',
        '.aabbcccccccbb...',
        '..aabbbccccbb....',
        '..aaabbbbbbb.....',
    ],
    'sleeve_h': [
        '..bccddc.',
        '.bccdddcb',
        'bbccdddcb',
        'bbcccddcb',
        'abbccccb.',
        'abbbccb..',
        '.aabbb...',
    ],
    'forearm_h': [
        'abbcb.......',
        'abbcccbb....',
        'abbccccccb..',
        '.abbcccccqrs',
        '..aabbbccrsr',
        '....aaabbqrq',
    ],
    'legs_h': [
        '..pqqrr.........pqqrs.',
        '..pqqrr.........pqqrs.',
        '..pqqrq.........pqqrr.',
        '.pqqArrq.......pqqArrq',
        'pqqAqArs......pqqAqArs',
        'AAAAAAAA......AAAAAAAA',
    ],
    'futa_check_h': [    # red plaid
        '..KLLMLLKLLMLL...',
        '.KKLLMLLKLLMLLK..',
        '.KKKKKKKKKKKKKKK.',
        'KKLLMLLKLLMLLKLLK',
        'KLLLMLLKLLMLLKLLK',
        'KKKKKKKKKKKKKKKKK',
        'KLLMLLKLLMLLKLLMK',
    ],
    'futa_h': [
        '..fghhhiiihhg....',
        '.fgghhhiiighhg...',
        '.fghhfhhiiighhg..',
        'ffghhfhhhiiighg..',
        'fgghhfhgghhiighg.',
        'fgghhfggghhhiighg',
        'ffghgfffgghhhhggf',
    ],
    'apron_h': [
        '...IJJJJ....',
        '...IJJJJ....',
        '..IJJJJJJ...',
        '..IJJLJJJ...',
        'BBBBBCCCBBBB',
        'IJJJJJJJJJJI',
        'IJJJJJJXJJJI',
        'IJJLJJJJJJJI',
        'IJJJJJJJJJJI',
        'IJJJJJJJXJJI',
        'HIJJJJJJJJII',
        'HIJJJJJJJJII',
        'HHIIIIIIIIIH',
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
        'aabbbccbbccccccccb.',
        '.abbbccbbccccccccb.',
        '.abbbbcbcccccc#ccb.',
        '.aabbbcbccccccccb..',
        '.aabbbbccccccccb...',
        '..abbbbccccccccb...',
        '..aabbbbcccccccb...',
        '...aabbbbcccccb....',
        '...aaabbbbbbbb.....',
    ],
    'sleeve_g': [
        '...bccddc..',
        '..bccddddcb',
        '.bbccdddccb',
        'bbccddddccb',
        'bbcccdddccb',
        'abbcccdcccb',
        'abbbcccccb.',
        '.abbbccccb.',
        '.aabbbbbb..',
        '..aaaaaa...',
    ],
    'forearm_g': [
        'abbccb.........',
        'abbccccbb......',
        'abbcccccccbb...',
        '.abbccccccccqrr',
        '..aabbcccccqrrs',
        '....aabbbbbqrsr',
        '.......aaaapqrq',
    ],
    'legs_g': [
        '..pqqrrs........pqqrrs..',
        '..pqqrrs........pqqrrs..',
        '..pqqrrq........pqqrrs..',
        '..pqqrrq........pqqrrq..',
        '..pqqrq.........pqqrrq..',
        '.pqqArrq.......pqqArrrq.',
        'pqqAqArrs.....pqqAqArrrs',
        'AAAAAAAAA.....AAAAAAAAAA',
    ],
    'futa_g': [
        '...fghhhhiiiiihhhg...',
        '..fgghhhiiiiiighhhg..',
        '.ffghhfhhiiiiiighhg..',
        '.fgghhfhhhiiiiiighhg.',
        '.fghhhfhhghhiiiiighg.',
        'ffghhhfhgghhhiiiighg.',
        'fgghhhfhgghhhhiiiighg',
        'fgghhhfggghhhhhiiighg',
        'fghhhhfggghhhhhhiihhg',
        'ffgghgfffgghhhhhhhggf',
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
    # ---- slim build: narrow shoulders, a long line, feet together
    'dress_top_s': [     # embroidered chest panel
        '...bccb...',
        '.abccdcb..',
        'abbcdKEKb.',
        'abbccEKEKb',
        'abbccKEKEb',
        'abbcccEKEb',
        'abbcccKEKb',
        'abbcbccccb',
        '.abcbccccb',
        '.abbcccccb',
        '.abbccccb.',
        '..abbccb..',
        '..aabbcb..',
    ],
    'sleeve_s': [
        '.bcdc.',
        'bccddb',
        'bccddb',
        'abccdb',
        'abbcb.',
        '.aab..',
    ],
    'forearm_s': [       # sleeved, gold-worked cuff
        'abcb.......',
        'abbccb.....',
        '.abbccEqrr.',
        '..aabbEqrsr',
        '.....aEpqrq',
    ],
    'dress_long_s': [    # to the ankle, red and gold worked hem
        '..abbcccbba..',
        '..abbccdcbba.',
        '.aabbccdcbba.',
        '.abbcbccdcba.',
        '.abbcbbccdcb.',
        '.abbcbabcdcb.',
        '.abbcbabbcdcb',
        'aabbcbabbcdcb',
        'aabbcbaabccdb',
        'abbbcbaabbcdb',
        'abbbcbaabbcdb',
        'abbcbbaabbcdc',
        'abbcbbaabbccd',
        'KEKEKEKEKEKEK',
        'abbbbbaabbbcc',
    ],
    'shoes_s': [
        '.ABBC..ABBC.',
        'AAAAAA.AAAAA',
    ],
    'thobe_top_s': [
        '...IJJI...',
        '.HIJJJJI..',
        'HIIJJJJJI.',
        'HIIJJIJJJI',
        'HIIJJIJJJI',
        'HIIJJIJJJI',
        'HIIJIIJJJI',
        'HIIJIJJJJI',
        '.HIJIJJJJI',
        '.HIIJJJJJI',
        '.HIIJJJJI.',
        '..HIIJJI..',
        '..HHIIJI..',
    ],
    'thobe_s': [
        '..HIIJJJIH..',
        '..HIIJJJJIH.',
        '.HIHIJJJJIH.',
        '.HIHIIJJJIH.',
        '.HIHIIJJJJH.',
        '.HIHIIHJJJIH',
        'HIIHIIHJJJIH',
        'HIIHIHHIJJIH',
        'HIHIIHHIJJJH',
        'HIHIIHHIJJJH',
        'HIHIIHHIIJJH',
        'HIHIHHHIIJJH',
        'HIHIHHHIIJJH',
        'HIHIHHHIIIJH',
        'HHIIIHHHIIHH',
    ],
    'arm_salute_s': [
        '....qrs',
        '...Iqrr',
        '..IJJ..',
        '.HIJ...',
        'HIJJ...',
        'HIJ....',
        '.HI....',
    ],
    'bare_feet_s': [
        '.pqrr..pqrr.',
        'pqqqrs.pqqrs',
    ],
    'rope_s': [
        'XYXYXYXYXYXY',
        '............',
        '............',
        'YXYXYXYXYXYX',
        '............',
        '............',
        'XYXYXYXYXYXY',
    ],
    'post': ['.XY.', 'XYYX'] + ['.XY.', '.XX.', '.XY.', '.WX.'] * 11,
    'dallah': [          # brass coffee pot on the belt
        '..F..',
        '.DE..',
        '.DEF.',
        'DEEFE',
        'DEFFE',
        '.DDE.',
    ],
    # ---- small build: a full-size head on a short trunk and shorter legs
    'tunic_s': [         # knee-length skirt of the dress, green worked hem
        '..abbcccbba...',
        '.aabbccdcbba..',
        '.abbcbccdcbba.',
        'aabbcbbccdcba.',
        'abbbcbabccdcbb',
        'NOPONOPONOPONO',
    ],
    'pants_s': [         # trousers with worked cuffs, shoes
        '..ghhi......ghhii',
        '..ghhi......ghhih',
        '..DEDE......DEDED',
        '.ABBCCC....ABBCCC',
        'AAAAAAA....AAAAAA',
    ],
    'big_pack': [        # the medic's: mat, canvas, green crescent patch; bigger than she is
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
    # ---- action poses for the house build
    'legs_run': [
        '.........pqrr.....pqrs..',
        '.......pqqrrq.....pqrr..',
        '....ppqqrrq........pqrr.',
        '..pqqrrrq..........pqrq.',
        'pqArrq............pqArrq',
        'qAqArq...........pqAqArs',
        'AAAq.............AAAAAAA',
    ],
    'futa_run': [
        '....fghhiiihhg.....',
        '...fgghSiiihgSg....',
        '..ffghhSh#iihgSg...',
        '.ffghhhShh#iihSgg..',
        'ffgghhhShgh#iihSgg.',
        'fgghhhhSgghhiiihSgg',
        'fghhhhhSggghhiiihSg',
        'SSKSSKSSKSSKSSKSSKS',
    ],
    'futa_crouch': [
        '..fghhiiiiihhhg...',
        '.fgghSiiiiihghSgg.',
        'ffghhShh#iiihghSgg',
        'SSKSSKSSKSSKSSKSSK',
    ],
    'legs_crouch': [
        '..pqrq.......pqrrq..',
        '.pqArrq.....pqqArrq.',
        'pqAqArrs...pqqAqArrs',
        'AAAAAAAA...AAAAAAAAA',
    ],
}

HAND = [
    'qrrs',
    'qrrr',
    'pqqr',
    '.pq.',
]

WEAPONS = {
    # a battered old rifle: cloth wound round the stock and handguard, magazine bound with tape
    'rifle': dict(grip=(7, 5), hand=(16, 2), rows=[
        '.......................zy....',
        '....xyyzzZzzzzy.WXYYXW.yzy.x.',
        'WXYYyyzyyyyyzyyyXXYJKYXyzzzzy',
        'WXKJyyy##yyyyyxWXJKXXWyyyyyyx',
        'WXKJXxyyyyzyyx.WWWWWWx.....x.',
        'WWXXX.xyyx.xyzzyx............',
        '.WWW..xyyx.HIIIIx............',
        '......xyx...xyzzyx...........',
        '.............xyyyx...........',
    ]),
    'shotgun': dict(grip=(7, 4), hand=(13, 2), rows=[
        '....xyyzzzzzzzzzzzzzzzzz',
        'WXYYyyyyyyyyyyyyyyyyyyyy',
        'WXKJYxyyzzzzzzzzzzzzzzzy',
        'WXKJXxyyyWXYYYYXWyyyyyy.',
        'WWXXX.xyyxWXXXXXW.......',
        '.WWW..xyyx.WWWWW........',
        '......xyx...............',
    ]),
    'marksman': dict(grip=(7, 5), hand=(20, 2), rows=[
        '............xyyzzzzyx...............',
        '............xyzZZzzyx...............',
        '....xyyzzzzzyyxyyyxyy...............',
        'WXYYYXXYYYXXXXYYJKYYXXYJKYXyyyyyyzzy',
        'WXKJXXXXXXXXXXXXJKXXXXXJKXWyyyyyyyy.',
        'WXKJXxyyxWWWWWWWWWWWWWWWWWW.........',
        'WWXXX.xyyx..........................',
        '.WWW..xyx...........................',
    ]),
    'mg': dict(grip=(7, 5), hand=(19, 2), rows=[
        '........................zy.......',
        '....xyyzzZzzzzzy.xyyyyyyzy....x..',
        'WXYYyyzyyyyyyzyyyyzzzzzzzzzzzzyyy',
        'WXXYYyyy##yyyyyyxyyyyyyyyyyyyyyyx',
        'WXXXXxyyyyzyyyyx.xy..xy.......x..',
        'WWXXX.xyyx.DEFEDx................',
        '.WWW..xyyx.DEEFEDFE..............',
        '......xyx..EFEDEEDEF.............',
        '...........DEDEFD.EDE............',
        '..................FE.............',
    ]),
    'rpg': dict(grip=(17, 4), rows=[
        '.............................NOOPO....',
        'xx..........................NOOPPPO...',
        'xyyzzzzzzzzzzzzzXYYYYXzzzzzyNOPPPPPO..',
        'xyyyyyyyyyyyyyyyXXXXXXyyyyyyxNOOPPOON.',
        'xx........WXY....WXY.........NNOOON...',
        '..........WXX....WXX..........NNN.....',
        '..........WW.....WW...................',
    ]),
    'pistol': dict(grip=(1, 3), rows=[
        'xyzzzzzzy',
        'xyyyyyyyy',
        'xyyyxxx..',
        'WXYx.....',
        'WXYx.....',
        '.WX......',
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


class Build:
    def __init__(self, **k):
        self.__dict__.update(k)


# Where things sit, per build (fill coordinates). The sole's line is the row at foot[1].
STD = Build(pack=(1, 9), legs=(2, 30), futa=(4, 22), torso=(6, 8), belt=(6, 20), jamb=(13, 19),
            grip=(17, 19), forearm=(8, 15), sleeve=(7, 11), face=(10, 5), wrap=(10, 0), foot=(11, 36))
LEAN = Build(pack=(1, 9), legs=(2, 28), futa=(4, 20), torso=(6, 8), belt=(6, 18), jamb=(12, 17),
             grip=(15, 18), forearm=(8, 14), sleeve=(6, 11), face=(9, 5), wrap=(9, 0), foot=(10, 35))
HEAVY = Build(pack=(0, 10), legs=(3, 30), futa=(5, 23), torso=(5, 8), belt=(6, 22), jamb=(15, 21),
              grip=(20, 17), forearm=(9, 13), sleeve=(6, 10), face=(12, 5), wrap=(12, 0), foot=(13, 36))
GIANT = Build(pack=(0, 12), legs=(3, 36), futa=(4, 26), torso=(5, 8), belt=(6, 24), jamb=(16, 23),
              grip=(21, 22), forearm=(9, 18), sleeve=(5, 11), face=(14, 5), wrap=(14, 0), foot=(15, 44))
SLIM = Build(pack=(1, 8), legs=(5, 34), futa=(4, 19), torso=(5, 6), belt=(5, 17), jamb=(11, 17),
             grip=(14, 16), forearm=(7, 12), sleeve=(5, 9), face=(8, 3), wrap=(8, -2), foot=(10, 36))
SMALL = Build(pack=(0, 14), legs=(3, 31), futa=(4, 26), torso=(5, 15), belt=(5, 24), jamb=(12, 23),
              grip=(16, 24), forearm=(7, 20), sleeve=(6, 17), face=(9, 11), wrap=(9, 6), foot=(11, 36))


def at(part_, pos, p, dx=0, dy=0, ink=None):
    rows = PARTS[part_] if isinstance(part_, str) else part_
    return (rows, pos[0] + dx, pos[1] + dy, p, ink)


def weapon(L, name, p, grip, hand=True):
    w = WEAPONS[name]
    ox, oy = grip[0] - w['grip'][0], grip[1] - w['grip'][1]
    L.append((w['rows'], ox, oy, p))
    if hand and w.get('hand'):
        L.append((HAND, ox + w['hand'][0], oy + w['hand'][1], p))


def done(L, flip=False, foot=None):
    return compose(L, flip=flip, foot=foot)


def head(L, B, p, face, wrap, end=None, dx=0, dy=0):
    """Hanging end, face, then the wrap over it. Head parts take the brown line, as hair does."""
    if end:
        L.append(at(WRAPS[end], B.wrap, p, dx - 1, dy + 6, ink=INK2))
    L.append(at(FACES[face], B.face, p, dx, dy))
    L.append(at(WRAPS[wrap], B.wrap, p, dx, dy, ink=INK2))


# ---------------------------------------------------------------- the squad
def yazeed(flip=False, pose='ready'):
    """Stocky, the house build. Blue checked wrap, blazer, striped futa, jambiya."""
    p = pal('blue', 'cream', 'blue', 'skin2')
    p['9'] = '#e4dec2'
    B = STD
    dx, dy = 0, 0
    if pose == 'run':
        dx = 1
        L = [at('pack', B.pack, p, dx), at('legs_run', (0, 29), p), at('futa_run', (3, 22), p)]
    elif pose == 'crouch':
        dy = 8
        L = [at('pack', B.pack, p, 0, dy), at('legs_crouch', (2, 32), p), at('futa_crouch', (3, 29), p)]
    else:
        L = [at('pack', B.pack, p), at('legs', B.legs, p), at('futa', B.futa, p)]
    L += [at('blazer', B.torso, p, dx, dy), at('belt', B.belt, p, dx, dy), at('jambiya', B.jamb, p, dx, dy)]
    weapon(L, 'rifle', p, (B.grip[0] + dx, B.grip[1] + dy))
    L += [at('forearm', B.forearm, p, dx, dy), at('sleeve', B.sleeve, p, dx, dy)]
    head(L, B, p, 'yazeed', 'check', 'check_end', dx, dy)
    L.append(at(WRAPS['basil'], B.wrap, p, dx, dy + 1, ink=INK2))
    return done(L, flip, B.foot)


def yazeed_run(flip=False):
    return yazeed(flip, 'run')


def yazeed_crouch(flip=False):
    return yazeed(flip, 'crouch')


# Honey-coloured bamboo for Salem's kufiya (the good ones lean reddish).
KUFIYA = {'1': '#5a3610', '2': '#a66c2c', '3': '#d8a456', '4': '#f6dca0'}


def salem(flip=False):
    """Heavy. The Tihama man's woven kufiya, a white shirt that stops short of the belly, plaid futa."""
    p = pal('white', 'cream', 'cream', 'skin3', **KUFIYA)
    B = HEAVY
    L = [at('jerrycan', B.pack, p), at('legs_h', B.legs, p), at('futa_check_h', B.futa, p),
         at('shirt_h', B.torso, p)]
    weapon(L, 'shotgun', p, B.grip)
    L += [at('forearm_h', B.forearm, p), at('sleeve_h', B.sleeve, p),
          at(FACES['salem'], B.face, p), at(WRAPS['kufiya'], B.wrap, p, 0, -1, ink=INK2)]
    return done(L, flip, B.foot)


def bilqis(flip=False):
    """Slim and two pixels taller. Veil hung with coins, worked dress to the ankle, the long rifle."""
    p = pal('navy', 'navy', 'crimson', 'skin2')
    B = SLIM
    L = [at(WRAPS['drape_long'], B.wrap, p, -3, 5, ink=INK2), at('shoes_s', B.legs, p),
         at('dress_long_s', B.futa, p), at('dress_top_s', B.torso, p), at('belt_l', B.belt, p),
         at('dallah', B.jamb, p, -2, 1)]
    weapon(L, 'marksman', p, B.grip)
    L += [at('forearm_s', B.forearm, p), at('sleeve_s', B.sleeve, p)]
    head(L, B, p, 'veiled', 'scarf')
    return done(L, flip, B.foot)


def arwa(flip=False):
    """Small, under a pack bigger than she is. Flowered scarf, umbrella."""
    p = pal('rose', 'cream', 'sage', 'skin1')
    B = SMALL
    L = [at('umbrella', B.pack, p, 0, -11), at('big_pack', B.pack, p, -6, -6),
         at(WRAPS['drape'], B.wrap, p, -2, 5, ink=INK2),
         at('pants_s', B.legs, p), at('tunic_s', B.futa, p), at('medic_top', B.torso, p),
         at('belt_plain', B.belt, p)]
    weapon(L, 'rifle', p, B.grip)
    L += [at('forearm', B.forearm, p), at('sleeve', B.sleeve, p)]
    head(L, B, p, 'arwa', 'flowered')
    L.append(at(WRAPS['knot'], B.face, p, 5, 6, ink=INK2))
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
    if B is LEAN:
        L.append(at(WRAPS['check_end'], B.wrap, p, -1, 6, ink=INK2))
        L.append(at(FACES[face], B.face, p))
        L.append(at(WRAPS['check_l'], B.wrap, p, ink=INK2))
    else:
        head(L, B, p, face, 'check', 'check_end')


def grunt(face='worried', skin='skin2', flip=False):
    """Lean, like the arcade's infantry."""
    p = militia_pal(skin)
    B = LEAN
    face = {'qat': 'qat_l'}.get(face, face)
    L = _lean_base(p)
    weapon(L, 'rifle', p, B.grip)
    L += [at('forearm_l', B.forearm, p), at('sleeve_l', B.sleeve, p), at('armband', B.sleeve, p, 2, 2)]
    _militia_head(L, face, p)
    return done(L, flip, B.foot)


def rocketeer(skin='skin3', flip=False):
    p = militia_pal(skin)
    B = LEAN
    L = _lean_base(p)
    weapon(L, 'rpg', p, grip=(20, 11))
    L += [at('sleeve_l', B.sleeve, p), at('armband', B.sleeve, p, 2, 2)]
    _militia_head(L, 'youth', p)
    L += [at('forearm_up_l', (11, 11), p)]
    return done(L, flip, B.foot)


def doorman(skin='skin2', flip=False):
    """Stocky, behind a pickup door."""
    p = militia_pal(skin)
    B = STD
    L = [at('legs', B.legs, p), at('futa_plain', B.futa, p), at('jacket', B.torso, p),
         at('belt_plain', B.belt, p), at('jambiya_s', B.jamb, p, 0, 1),
         at('sleeve', B.sleeve, p), at('armband', B.sleeve, p, 3, 2)]
    _militia_head(L, 'qat', p, B)
    L += [at('door', (19, 11), p)]
    weapon(L, 'pistol', p, grip=(21, 9))
    L += [at('forearm_up', (9, 8), p)]
    return done(L, flip, B.foot)


def bomber(skin='skin1', flip=False):
    p = militia_pal(skin)
    B = LEAN
    L = [at('arm_raise_l', (3, 0), p)]
    weapon(L, 'dynamite', p, grip=(5, 0))
    L += _lean_base(p)
    L += [at('forearm_l', B.forearm, p), at('sleeve_l', B.sleeve, p), at('armband', B.sleeve, p, 2, 2)]
    _militia_head(L, 'angry', p)
    return done(L, flip, B.foot)


def cook(skin='skin2', flip=False):
    """Heavy. Pot for a helmet, ladle for a club."""
    p = militia_pal(skin)
    B = HEAVY
    L = [at('legs_h', B.legs, p), at('futa_h', B.futa, p), at('jacket_h', B.torso, p),
         at('apron_h', (10, 12), p)]
    weapon(L, 'ladle', p, B.grip)
    L += [at('forearm_h', B.forearm, p), at('sleeve_h', B.sleeve, p),
          at(FACES['cook'], B.face, p), at(WRAPS['pot'], B.wrap, p, -1, 0)]
    return done(L, flip, B.foot)


def surrender(skin='skin1', flip=False):
    p = militia_pal(skin)
    B = LEAN
    L = [at('arm_raise_l', (3, 0), p)] + _lean_base(p)
    _militia_head(L, 'worried', p)
    L += [at('arm_raise_fl', (17, 2), p)]
    return done(L, flip, B.foot)


def guard(skin='skin2', flip=False):
    """Giant. Black from wrap to hem, one yellow bar, belt-fed gun."""
    p = pal('black', 'black', 'black', skin)
    B = GIANT
    L = [at('cape_g', (-1, 11), p), at('legs_g', B.legs, p), at('futa_g', B.futa, p),
         at('jacket_g', B.torso, p), at('bandolier_g', (9, 12), p), at('belt_g', B.belt, p),
         at('jambiya', B.jamb, p)]
    weapon(L, 'mg', p, B.grip)
    L += [at('forearm_g', B.forearm, p), at('sleeve_g', B.sleeve, p), at('armband', B.sleeve, p, 4, 3)]
    head(L, B, p, 'masked', 'hood', 'hood_end')
    return done(L, flip, B.foot)


def detainee(flip=False, freed=False):
    """Slim elder roped to a post, the arcade's prisoner in a thobe. Freed, he salutes."""
    p = pal('white', 'white', 'white', 'skin3')
    B = SLIM
    L = []
    if not freed:
        L.append(at('post', (2, -10), p))
    L += [at('bare_feet_s', B.legs, p), at('thobe_s', B.futa, p), at('thobe_top_s', B.torso, p)]
    if freed:
        pass
    else:
        L += [at('rope_s', (4, 10), p)]
    L += [at(FACES['elder'], B.face, p), at(WRAPS['cap'], B.wrap, p, 0, 1, ink=INK2)]
    if freed:
        L += [at('arm_salute_s', (12, 2), p)]
    return done(L, flip, B.foot)


def detainee_freed(flip=False):
    return detainee(flip, True)



# ---------------------------------------------------------------- the Marshal
MARSHAL = {
    'boots': [
        '..UVVGG...........UVVGGV..',
        '..UVVGG...........UVVGGV..',
        '..UVGVG...........UVVGVG..',
        '..UVVGG...........UVVGG...',
        '..UVVG............UVVG....',
        '.UVVGGG..........UVVGGGG..',
        'UVVVGGGGG.......UVVVGGGGG.',
        'UUUUUUUUU.......UUUUUUUUUU',
    ],
    'skirt': [           # the greatcoat below the belt, gold piping at the edge
        '...abbbccccccccccccccbE.....',
        '..aabbcccccccdccccccccbE....',
        '..abbbccbcccccdcccccccbE....',
        '.aabbccbbcccccdccccccccbE...',
        '.abbbccbcccccccdcccccccbE...',
        '.abbbcbbcccbcccdccccccccbE..',
        'aabbbcbbccbbccccdcccccccbE..',
        'aabbbcbcccbcccccdccccccccbE.',
        'aabbbcbcccbccccccdcccccccbE.',
        'aabbcbbccbbccccccdcccccccbbE',
        'EEEEEEEEEEEEEEEEEEEEEEEEEEEE',
    ],
    'torso': [           # greatcoat, a button line, a belly that leads
        '......bbcccccb...........',
        '....abbccdddcccb.........',
        '...abbcccdddccccb........',
        '..abbccccccccccccb.......',
        '..abbccccccccccEcccb.....',
        '.aabbccccccccccccccccb...',
        '.aabbccccccccccEccccccb..',
        '.aabbccccccccccccccdcccb.',
        'aaabbccccccccccEcccddcccb',
        'aaabbccccccccccccccdddccb',
        'aaabbccccccccccEccccddccb',
        'aaabbbcccccccccccccccdccb',
        'aaabbbccccccccccEcccccccb',
        '.aabbbcccccccccccccccccb.',
        '.aabbbbcccccccccEcccccb..',
        '.aabbbbcccccccccccccbb...',
        '..aabbbbccccccccccccb....',
        '..aaabbbbccccccccccb.....',
    ],
    'medals': [
        'LMSTOP',
        'LMSTOP',
        'E.E.E.',
        'F.F.F.',
    ],
    'sash': [
        'KLM..........',
        '.KLM.........',
        '..KLLM.......',
        '...KLLM......',
        '....KLLM.....',
        '.....KLLM....',
        '......KLLM...',
        '.......KLLM..',
        '........KLLM.',
        '.........KLLM',
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
        '..DFFD.......',
        '.NOOPPO......',
        '.NOEPPO.....E',
        '.NOOPPO....EF',
        '.NOEPPPO..OOE',
        '..NOOPPO.OPPO',
        '..NOEPPPOPPO.',
        '...NOOPPPPO..',
        '....NOOOOO...',
    ],
    'sleeve': [
        '..bccddc...',
        '.bccddddcb.',
        'bbccdddccb.',
        'bbcccddccb.',
        'abbccccccb.',
        'abbbccccb..',
        '.abbbcccb..',
        '.aabbbbb...',
    ],
    'far_arm': [         # the megaphone arm, coming from behind the chest
        '......qrs',
        '....EFrrr',
        '..bcEFrrq',
        'bbccEFq..',
        'bcccb....',
        'bccb.....',
    ],
    'forearm': [         # near arm, hand on the hilt
        'abbccb.......',
        'abbccccbb....',
        '.abbcccccEF..',
        '..aabbcccEFqr',
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
    'face': [            # aviators, and a moustache wider than the face it sits on
        '..rr#xxZxx#.',
        '..qr#xxxxx#.',
        '..q%rr###rst',
        '..qrrrrrrrq.',
        '.uuuuuuuuuuu',
        '..uvuuuuuvu.',
        '..qrrr#JJ#r.',
        '...qqrrrrrr.',
    ],
    'wrap': [            # the biggest shemagh in the country: fanned crest, gold brooch
        '.J9J..........',
        'J9J9J.........',
        '9J9J9J.lmnml..',
        '.9J9Jlm9nnn9m.',
        '..kJm9mmn9nnnl',
        '..k9lmm9mmnEFl',
        '..kl9lm9lmmFEk',
        '..kklk9lkl9lkk',
        '..kl..........',
        '..k9..........',
        '...k..........',
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
    L = [(M['boots'], 4, 40, p), (M['skirt'], 3, 30, p), (M['far_arm'], 24, 12, p), (M['torso'], 4, 13, p),
         (M['sash'], 10, 14, p), (M['medals'], 18, 17, p), (M['belt'], 4, 28, p), (M['jambiya'], 18, 24, p),
         (M['megaphone'], 30, 6, p), (M['forearm'], 10, 22, p), (M['sleeve'], 4, 15, p),
         (M['epaulette'], 4, 13, p), (M['face'], 14, 5, p), (M['wrap'], 11, -4, p, INK2)]
    return compose(L, flip=flip, foot=(17, 48))


CAST = [('yazeed', yazeed), ('salem', salem), ('bilqis', bilqis), ('arwa', arwa),
        ('grunt', grunt), ('rocketeer', rocketeer), ('doorman', doorman), ('bomber', bomber),
        ('cook', cook), ('surrender', surrender), ('guard', guard), ('detainee', detainee),
        ('marshal', marshal), ('yazeed_run', yazeed_run), ('yazeed_crouch', yazeed_crouch),
        ('detainee_freed', detainee_freed)]


def check():
    """Report parts whose rows differ in width (a typo guard)."""
    bad = []
    for group, d in (('FACES', FACES), ('WRAPS', WRAPS), ('PARTS', PARTS), ('MARSHAL', MARSHAL)):
        for k, rows in d.items():
            ws = {len(r) for r in rows}
            if len(ws) > 1 and k not in ('post', 'arm_raise_l'):
                bad.append((group, k, sorted(ws)))
    for k, w in WEAPONS.items():
        ws = {len(r) for r in w['rows']}
        if len(ws) > 1:
            bad.append(('WEAPONS', k, sorted(ws)))
    return bad
