"""Build the title menu's original 5 x 7 outline font; no raster UI assets."""
from pathlib import Path
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

# Each filled cell becomes a square outline in a normal, selectable text font.
ROWS = {
    'A': '01110/11011/11011/11111/11011/11011/11011',
    'B': '11110/11011/11011/11110/11011/11011/11110',
    'C': '01111/11000/11000/11000/11000/11000/01111',
    'D': '11110/11011/11011/11011/11011/11011/11110',
    'E': '11111/11000/11000/11110/11000/11000/11111',
    'F': '11111/11000/11000/11110/11000/11000/11000',
    'G': '01111/11000/11000/11011/11011/11011/01111',
    'H': '11011/11011/11011/11111/11011/11011/11011',
    'I': '11111/00100/00100/00100/00100/00100/11111',
    'J': '00111/00011/00011/00011/11011/11011/01110',
    'K': '11011/11011/11110/11100/11110/11011/11011',
    'L': '11000/11000/11000/11000/11000/11000/11111',
    'M': '10001/11011/11111/10101/10001/10001/10001',
    'N': '10011/11011/11011/11111/11011/11011/11001',
    'O': '01110/11011/11011/11011/11011/11011/01110',
    'P': '11110/11011/11011/11110/11000/11000/11000',
    'Q': '01110/11011/11011/11011/11111/01110/00011',
    'R': '11110/11011/11011/11110/11100/11010/11011',
    'S': '01111/11000/11000/01110/00011/00011/11110',
    'T': '11111/00100/00100/00100/00100/00100/00100',
    'U': '11011/11011/11011/11011/11011/11011/01110',
    'V': '11011/11011/11011/11011/11011/01010/00100',
    'W': '10001/10001/10001/10101/11111/11011/10001',
    'X': '11011/11011/01010/00100/01010/11011/11011',
    'Y': '11011/11011/11011/01110/00100/00100/00100',
    'Z': '11111/00011/00110/00100/01100/11000/11111',
    '0': '01110/11011/11011/11011/11011/11011/01110',
    '1': '00100/01100/00100/00100/00100/00100/01110',
    '2': '01110/11011/00011/00110/01100/11000/11111',
    '3': '11110/00011/00011/01110/00011/00011/11110',
    '4': '11011/11011/11011/11111/00011/00011/00011',
    '5': '11111/11000/11000/11110/00011/00011/11110',
    '6': '01110/11000/11000/11110/11011/11011/01110',
    '7': '11111/00011/00110/00100/01100/01100/01100',
    '8': '01110/11011/11011/01110/11011/11011/01110',
    '9': '01110/11011/11011/01111/00011/00011/01110',
    ':': '00000/00100/00100/00000/00100/00100/00000',
    '>': '10000/11000/11100/11110/11100/11000/10000',
    '.': '00000/00000/00000/00000/00000/00100/00100',
    '-': '00000/00000/00000/11111/00000/00000/00000',
    ' ': '00000/00000/00000/00000/00000/00000/00000',
}

def build():
    font = FontBuilder(800, isTTF=True)
    names = {char: f'uni{ord(char):04X}' for char in ROWS}
    font.setupGlyphOrder(['.notdef', *names.values()])
    font.setupCharacterMap({ord(char): name for char, name in names.items()})
    glyphs = {'.notdef': TTGlyphPen(None).glyph()}
    for char, pattern in ROWS.items():
        pen = TTGlyphPen(None)
        for y, row in enumerate(pattern.split('/')):
            for x, value in enumerate(row):
                if value == '1':
                    left, bottom = x * 100, (6 - y) * 100
                    pen.moveTo((left, bottom))
                    pen.lineTo((left, bottom + 100))
                    pen.lineTo((left + 100, bottom + 100))
                    pen.lineTo((left + 100, bottom))
                    pen.closePath()
        glyphs[names[char]] = pen.glyph()
    font.setupGlyf(glyphs)
    font.setupHorizontalMetrics({name: (600, 0) for name in glyphs})
    font.setupHorizontalHeader(ascent=700, descent=-100)
    font.setupNameTable({'familyName': 'Hell Menu Pixel', 'styleName': 'Regular',
                        'uniqueFontIdentifier': 'HellMenuPixel-Regular-1',
                        'fullName': 'Hell Menu Pixel', 'psName': 'HellMenuPixel-Regular',
                        'version': 'Version 1.0'})
    font.setupOS2(sTypoAscender=700, sTypoDescender=-100, usWinAscent=700, usWinDescent=100)
    font.setupPost()
    font.setupMaxp()
    output = Path(__file__).resolve().parents[1] / 'assets/title/fonts/hell-menu-pixel.ttf'
    output.parent.mkdir(parents=True, exist_ok=True)
    font.save(output)
    print(output)

if __name__ == '__main__':
    build()
