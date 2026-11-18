"""Tuesday 17 November 2026: The World in One Page.

A procedural newspaper front page summing up 17 November 2026 in one
image: 36 verified stories, 12 pictured panels, a world map with 12
numbered pins, a by-the-numbers strip and a 24-item also-on list.

Python 3.13, standard library only, no network. Writes one
deterministic 1024x1024 PNG to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).
Every drawing is flat vector-style art drawn in code with an own PNG
encoder and an own 5x7 bitmap font, so no text ever garbles.

Repo: aikbani/news-image-20261117
Workdir: ~/workspace/makefun/work/news-image-20261117/
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
PAPER2 = (255, 252, 244)
INK = (26, 26, 26)
GREY = (110, 105, 92)
BORDER = (150, 138, 112)
NAVY = (20, 38, 77)
NAVY2 = (28, 52, 102)
RED = (176, 30, 36)
REDD = (140, 22, 28)
GOLD = (201, 162, 39)
GOLDL = (230, 200, 110)
SEA = (172, 204, 226)
SEA2 = (150, 188, 216)
LAND = (233, 225, 200)
LAND2 = (222, 212, 182)
TEAL = (18, 90, 90)
MAROON = (122, 32, 32)
GREEN = (46, 110, 46)
OCHRE = (188, 138, 20)
PURPLE = (88, 60, 120)
BROWN = (122, 84, 48)
CHARCOAL = (40, 40, 44)
SKY = (186, 216, 238)
SAND = (238, 226, 196)
WHITE = (255, 255, 255)
CREAM = (250, 246, 236)

# ------------------------------------------------------------------- PNG
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out

def write_png(path, px, w, h):
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += px[y * w * 3:(y + 1) * w * 3]
    comp = zlib.compress(bytes(raw), 9)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(_chunk(b"IHDR", ihdr))
        f.write(_chunk(b"IDAT", comp))
        f.write(_chunk(b"IEND", b""))

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.fill(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def rect(self, x, y, w, h, c, t=1):
        self.fill(x, y, w, t, c)
        self.fill(x, y + h - t, w, t, c)
        self.fill(x, y, t, h, c)
        self.fill(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.fill(x0, y0, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        if fill:
            for dy in range(-r, r + 1):
                dx = int((r * r - dy * dy) ** 0.5)
                self.fill(cx - dx, cy + dy, 2 * dx + 1, 1, c)
        else:
            for a in range(360):
                import math
                self.set(cx + int(r * math.cos(a * 3.14159 / 180)),
                         cy + int(r * math.sin(a * 3.14159 / 180)), c)

    def poly(self, pts, c):
        # scanline fill of a simple polygon
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.fill(int(xs[i]), y, int(xs[i + 1]) - int(xs[i]) + 1, 1, c)

# ------------------------------------------------------------ bitmap font
# 5x7 glyphs, each row a 5-char string of '1'/'0'.
FONT = {
'A': ("01110","10001","10001","11111","10001","10001","10001"),
'B': ("11110","10001","10001","11110","10001","10001","11110"),
'C': ("01110","10001","10000","10000","10000","10001","01110"),
'D': ("11110","10001","10001","10001","10001","10001","11110"),
'E': ("11111","10000","10000","11110","10000","10000","11111"),
'F': ("11111","10000","10000","11110","10000","10000","10000"),
'G': ("01110","10001","10000","10111","10001","10001","01111"),
'H': ("10001","10001","10001","11111","10001","10001","10001"),
'I': ("01110","00100","00100","00100","00100","00100","01110"),
'J': ("00111","00010","00010","00010","00010","10010","01100"),
'K': ("10001","10010","10100","11000","10100","10010","10001"),
'L': ("10000","10000","10000","10000","10000","10000","11111"),
'M': ("10001","11011","10101","10101","10001","10001","10001"),
'N': ("10001","11001","10101","10011","10001","10001","10001"),
'O': ("01110","10001","10001","10001","10001","10001","01110"),
'P': ("11110","10001","10001","11110","10000","10000","10000"),
'Q': ("01110","10001","10001","10001","10101","10010","01101"),
'R': ("11110","10001","10001","11110","10100","10010","10001"),
'S': ("01111","10000","10000","01110","00001","00001","11110"),
'T': ("11111","00100","00100","00100","00100","00100","00100"),
'U': ("10001","10001","10001","10001","10001","10001","01110"),
'V': ("10001","10001","10001","10001","10001","01010","00100"),
'W': ("10001","10001","10001","10101","10101","10101","01010"),
'X': ("10001","10001","01010","00100","01010","10001","10001"),
'Y': ("10001","10001","01010","00100","00100","00100","00100"),
'Z': ("11111","00001","00010","00100","01000","10000","11111"),
'0': ("01110","10001","10011","10101","11001","10001","01110"),
'1': ("00100","01100","00100","00100","00100","00100","01110"),
'2': ("01110","10001","00001","00110","01000","10000","11111"),
'3': ("11111","00010","00100","00010","00001","10001","01110"),
'4': ("00010","00110","01010","10010","11111","00010","00010"),
'5': ("11111","10000","11110","00001","00001","10001","01110"),
'6': ("01110","10000","10000","11110","10001","10001","01110"),
'7': ("11111","00001","00010","00100","01000","01000","01000"),
'8': ("01110","10001","10001","01110","10001","10001","01110"),
'9': ("01110","10001","10001","01111","00001","00001","01110"),
}

FONT.update({
'a': ("00000","00000","01110","00001","01111","10001","01111"),
'b': ("10000","10000","11110","10001","10001","10001","11110"),
'c': ("00000","00000","01110","10000","10000","10001","01110"),
'd': ("00001","00001","01111","10001","10001","10001","01111"),
'e': ("00000","00000","01110","10001","11111","10000","01110"),
'f': ("00110","01000","01000","11110","01000","01000","01000"),
'g': ("00000","01111","10001","10001","01111","00001","01110"),
'h': ("10000","10000","11110","10001","10001","10001","10001"),
'i': ("00100","00000","01100","00100","00100","00100","01110"),
'j': ("00010","00000","00110","00010","00010","10010","01100"),
'k': ("10000","10000","10010","10100","11000","10100","10010"),
'l': ("01100","00100","00100","00100","00100","00100","01110"),
'm': ("00000","00000","11010","10101","10101","10101","10101"),
'n': ("00000","00000","11110","10001","10001","10001","10001"),
'o': ("00000","00000","01110","10001","10001","10001","01110"),
'p': ("00000","11110","10001","10001","11110","10000","10000"),
'q': ("00000","01111","10001","10001","01111","00001","00001"),
'r': ("00000","00000","10110","11001","10000","10000","10000"),
's': ("00000","00000","01111","10000","01110","00001","11110"),
't': ("01000","01000","11100","01000","01000","01000","00110"),
'u': ("00000","00000","10001","10001","10001","10011","01101"),
'v': ("00000","00000","10001","10001","10001","01010","00100"),
'w': ("00000","00000","10001","10101","10101","10101","01010"),
'x': ("00000","00000","10001","01010","00100","01010","10001"),
'y': ("00000","00000","10001","10001","01111","00001","01110"),
'z': ("00000","00000","11111","00010","00100","01000","11111"),
' ': ("00000","00000","00000","00000","00000","00000","00000"),
'.': ("00000","00000","00000","00000","00000","01100","01100"),
',': ("00000","00000","00000","00000","01100","00100","01000"),
':': ("00000","01100","01100","00000","01100","01100","00000"),
';': ("00000","01100","01100","00000","01100","00100","01000"),
"'": ("00100","00100","01000","00000","00000","00000","00000"),
'"': ("01010","01010","00000","00000","00000","00000","00000"),
'-': ("00000","00000","00000","01110","00000","00000","00000"),
'—': ("00000","00000","00000","11111","00000","00000","00000"),
'•': ("00000","00000","01110","01110","01110","00000","00000"),
'$': ("00100","01111","10100","01110","00101","11110","00100"),
'%': ("11001","11010","00010","00100","01000","01011","10011"),
'/': ("00001","00010","00010","00100","01000","01000","10000"),
'(': ("00010","00100","01000","01000","01000","00100","00010"),
')': ("01000","00100","00010","00010","00010","00100","01000"),
'!': ("00100","00100","00100","00100","00100","00000","00100"),
'?': ("01110","10001","00001","00110","00100","00000","00100"),
'&': ("01100","10010","10100","01000","10101","10010","01101"),
'+': ("00000","00100","00100","11111","00100","00100","00000"),
'=': ("00000","00000","11111","00000","11111","00000","00000"),
'#': ("01010","01010","11111","01010","11111","01010","01010"),
'*': ("00000","10101","01110","11111","01110","10101","00000"),
'_': ("00000","00000","00000","00000","00000","00000","11111"),
'[': ("01110","01000","01000","01000","01000","01000","01110"),
']': ("01110","00010","00010","00010","00010","00010","01110"),
'<': ("00010","00100","01000","10000","01000","00100","00010"),
'>': ("01000","00100","00010","00001","00010","00100","01000"),
'|': ("00100","00100","00100","00100","00100","00100","00100"),
'’': ("00100","00100","01000","00000","00000","00000","00000"),
'“': ("01010","01010","00000","00000","00000","00000","00000"),
'”': ("01010","01010","00000","00000","00000","00000","00000"),
'?2': ("01110","10001","10001","10001","10001","10001","01110"),
})

def text_w(s, scale):
    return len(s) * 6 * scale - scale

def draw_text(cv, x, y, s, scale, color, bold=False):
    # Bold is a second pass shifted by less than one advance, so a bold
    # glyph never touches the next glyph (offset == scale merged letters).
    off = max(1, scale - 1) if bold else 0
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for r in range(7):
            row = g[r]
            for c in range(5):
                if row[c] == '1':
                    cv.fill(cx + c * scale, y + r * scale, scale, scale, color)
                    if bold:
                        cv.fill(cx + c * scale + off, y + r * scale, scale, scale, color)
        cx += 6 * scale
    return cx

def draw_text_c(cv, cx, y, s, scale, color, bold=False):
    draw_text(cv, cx - text_w(s, scale) // 2, y, s, scale, color, bold)

def wrap(s, max_chars):
    words = s.split(' ')
    lines, cur = [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if len(t) <= max_chars:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# ------------------------------------------------------------- world map
# Coarse continent outlines in (lon, lat). Equirectangular projection.
NORTH_AMERICA = [(-168, 66), (-155, 71), (-140, 70), (-128, 71), (-115, 73),
    (-100, 73), (-90, 74), (-82, 72), (-76, 72), (-70, 68), (-65, 62),
    (-60, 60), (-55, 52), (-60, 47), (-65, 44), (-70, 42), (-74, 39),
    (-76, 35), (-80, 32), (-81, 26), (-84, 30), (-90, 21), (-94, 19),
    (-97, 26), (-102, 25), (-105, 20), (-110, 23), (-114, 28), (-117, 33),
    (-122, 37), (-124, 42), (-125, 49), (-130, 55), (-135, 58), (-145, 60),
    (-155, 58), (-162, 55), (-168, 60)]
GREENLAND = [(-55, 60), (-45, 60), (-40, 64), (-32, 68), (-22, 70),
    (-25, 76), (-40, 78), (-58, 76), (-60, 74), (-55, 70)]
SOUTH_AMERICA = [(-79, 9), (-77, 7), (-72, 12), (-64, 10), (-60, 8),
    (-52, 5), (-50, 0), (-44, -3), (-35, -8), (-37, -13), (-40, -20),
    (-48, -27), (-55, -34), (-62, -39), (-66, -45), (-69, -52), (-73, -53),
    (-74, -48), (-73, -40), (-72, -30), (-70, -20), (-76, -14), (-80, -5),
    (-81, 0), (-80, 5)]
AFRICA = [(-17, 15), (-16, 20), (-10, 30), (-6, 33), (0, 36), (10, 37),
    (15, 32), (20, 32), (25, 31), (32, 31), (35, 28), (38, 22), (43, 12),
    (48, 11), (51, 12), (48, 5), (42, -2), (40, -10), (37, -16), (35, -22),
    (32, -26), (28, -33), (20, -35), (16, -29), (13, -20), (12, -15),
    (13, -10), (9, -1), (9, 4), (-8, 5), (-13, 8), (-17, 12)]
EUROPE = [(-9, 37), (-9, 43), (-4, 44), (-2, 47), (-1, 49), (2, 51),
    (5, 53), (8, 55), (8, 57), (10, 59), (13, 56), (18, 56), (21, 55),
    (23, 57), (25, 58), (27, 59), (30, 60), (30, 63), (28, 66), (25, 70),
    (20, 70), (15, 68), (12, 65), (10, 62), (5, 60), (5, 58), (2, 57),
    (-2, 55), (-4, 52), (-5, 50), (-8, 47), (-10, 43), (-10, 37)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
    (-2, 50)]
ASIA = [(30, 70), (35, 68), (40, 68), (45, 69), (50, 69), (55, 70),
    (60, 70), (65, 71), (70, 72), (75, 73), (80, 73), (85, 74), (90, 75),
    (95, 76), (100, 77), (105, 77), (110, 75), (115, 73), (120, 73),
    (125, 72), (130, 72), (135, 71), (140, 72), (145, 72), (150, 70),
    (155, 70), (160, 69), (165, 67), (170, 66), (178, 65), (175, 62),
    (170, 60), (165, 60), (160, 56), (158, 52), (155, 55), (150, 59),
    (145, 59), (142, 55), (141, 50), (140, 45), (138, 40), (135, 35),
    (132, 33), (129, 33), (127, 35), (125, 38), (122, 39), (120, 35),
    (118, 30), (115, 25), (112, 22), (110, 20), (108, 15), (106, 10),
    (104, 9), (101, 8), (99, 10), (97, 14), (94, 17), (92, 21), (89, 22),
    (87, 21), (85, 19), (82, 16), (80, 13), (78, 8), (76, 10), (74, 14),
    (72, 20), (70, 22), (67, 24), (64, 25), (61, 25), (58, 25), (56, 27),
    (54, 26), (52, 27), (50, 29), (49, 30), (47, 30), (44, 29), (42, 29),
    (40, 31), (38, 33), (36, 36), (34, 36), (32, 36), (30, 36), (28, 37),
    (27, 38), (26, 40), (24, 40), (23, 38), (22, 37), (24, 40), (26, 42),
    (28, 44), (28, 46), (29, 48), (30, 52), (32, 55), (34, 58), (34, 62),
    (32, 65), (30, 68), (30, 70)]
AUSTRALIA = [(113, -22), (114, -28), (115, -32), (116, -35), (120, -34),
    (124, -33), (129, -32), (132, -32), (135, -35), (137, -35), (140, -37),
    (145, -38), (150, -37), (153, -35), (153, -30), (152, -26), (150, -23),
    (147, -19), (144, -15), (142, -11), (140, -17), (138, -15), (136, -12),
    (135, -15), (132, -12), (130, -13), (128, -14), (126, -14), (124, -16),
    (122, -18), (120, -20), (117, -20), (114, -22)]
CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EUROPE,
              UK, ASIA, AUSTRALIA]

# (number, lon, lat, label, label dx, label dy)
PINS = [
    (1, 39.5, 45.3, "KERCH", 10, -3),
    (2, 121.0, 14.6, "MANILA", -42, -3),
    (3, 56.5, 26.6, "HORMUZ", 10, -3),
    (4, -74.0, 40.7, "", 0, 0),
    (5, -122.0, 37.4, "", 0, 0),
    (6, -80.5, 28.4, "", 0, 0),
    (7, -77.0, 38.9, "", 0, 0),
    (8, 30.1, -1.9, "RWANDA", 10, -3),
    (9, 45.0, 12.8, "ADEN", 10, -3),
    (10, 79.0, 30.1, "", 0, 0),
    (11, 28.0, -26.2, "S. AFRICA", -34, 10),
    (12, 139.7, 35.7, "", 0, 0),
]

def map_xy(mx, my, mw, mh, lon, lat):
    x = mx + (lon + 170) / 360.0 * mw
    y = my + (72 - lat) / 130.0 * mh
    return int(x), int(y)

def draw_map(cv, mx, my, mw, mh):
    cv.fill(mx, my, mw, mh, SEA)
    # graticule
    for lon in range(-150, 181, 30):
        x, _ = map_xy(mx, my, mw, mh, lon, 0)
        cv.fill(x, my, 1, mh, SEA2)
    for lat in range(-40, 61, 20):
        _, y = map_xy(mx, my, mw, mh, 0, lat)
        cv.fill(mx, y, mw, 1, SEA2)
    for poly in CONTINENTS:
        pts = [map_xy(mx, my, mw, mh, lon, lat) for lon, lat in poly]
        cv.poly(pts, LAND)
    cv.rect(mx, my, mw, mh, BORDER, 1)
    for num, lon, lat, label, dx, dy in PINS:
        px, py = map_xy(mx, my, mw, mh, lon, lat)
        r = 8 if num >= 10 else 7
        cv.circle(px, py, r + 1, WHITE)
        cv.circle(px, py, r, RED)
        s = str(num)
        draw_text(cv, px - text_w(s, 1) // 2, py - 3, s, 1, WHITE, bold=True)
        if label:
            draw_text(cv, px + dx, py + dy, label, 1, NAVY, bold=True)

# ------------------------------------------------------- panel drawings
# Each draws into (x, y, w=240, h=44) on its own coloured ground.

def d_kerch(cv, x, y, w, h):
    cv.fill(x, y, w, h, SKY)
    cv.fill(x, y + 30, w, h - 30, (46, 110, 160))
    cv.fill(x, y + 30, w, 2, WHITE)
    # bridge deck, two spans with a gap
    cv.fill(x + 8, y + 14, 92, 6, (90, 90, 96))
    cv.fill(x + 140, y + 14, 92, 6, (90, 90, 96))
    cv.line(x + 8, y + 14, x + 8, y + 30, (90, 90, 96), 3)
    cv.line(x + 232, y + 14, x + 232, y + 30, (90, 90, 96), 3)
    # fallen span, tilted into the water
    cv.line(x + 104, y + 20, x + 136, y + 34, (120, 120, 126), 4)
    # smoke
    cv.circle(x + 116, y + 12, 5, (220, 220, 220))
    cv.circle(x + 126, y + 8, 4, (200, 200, 200))
    cv.circle(x + 108, y + 6, 3, (235, 235, 235))
    # sun
    cv.circle(x + w - 18, y + 8, 5, GOLDL)

def d_manila(cv, x, y, w, h):
    cv.fill(x, y, w, h, CREAM)
    cv.fill(x, y + 34, w, h - 34, (214, 196, 150))
    # three flags on poles: USA, China, Russia
    for i, cols in enumerate([[(200, 40, 40), (255, 255, 255), (40, 60, 140)],
                              [(222, 40, 30), (255, 220, 60)],
                              [(255, 255, 255), (40, 80, 180), (200, 40, 40)]]):
        fx = x + 30 + i * 78
        cv.fill(fx, y + 6, 2, 28, INK)
        fh = 16
        for j, c in enumerate(cols):
            cv.fill(fx + 2, y + 6 + j * (fh // len(cols)), 26, fh // len(cols) + 1, c)
        if i == 1:
            cv.circle(fx + 8, y + 9, 2, (255, 220, 60))
    # podium line
    cv.fill(x + 20, y + 38, w - 40, 2, INK)

def d_hormuz(cv, x, y, w, h):
    cv.fill(x, y, w, h, (16, 70, 78))
    cv.fill(x, y + 28, w, h - 28, (10, 52, 62))
    # tanker hull
    cv.poly([(x + 20, y + 26), (x + 150, y + 26), (x + 165, y + 36),
             (x + 30, y + 36)], (150, 60, 40))
    cv.fill(x + 120, y + 14, 26, 12, WHITE)
    cv.fill(x + 128, y + 18, 10, 4, (150, 60, 40))
    # fire + smoke
    cv.poly([(x + 60, y + 26), (x + 68, y + 8), (x + 76, y + 26)], (240, 140, 20))
    cv.poly([(x + 66, y + 26), (x + 70, y + 14), (x + 74, y + 26)], (250, 200, 60))
    cv.circle(x + 70, y + 6, 4, (60, 60, 60))
    cv.circle(x + 78, y + 3, 3, (80, 80, 80))
    # mine with spikes
    cv.circle(x + 205, y + 18, 6, INK)
    for dx, dy in [(0, -9), (0, 9), (-9, 0), (9, 0), (-6, -6), (6, -6)]:
        cv.line(x + 205, y + 18, x + 205 + dx, y + 18 + dy, INK, 2)

def d_jpmorgan(cv, x, y, w, h):
    cv.fill(x, y, w, h, NAVY)
    # bank building
    cv.poly([(x + 70, y + 6), (x + 170, y + 6), (x + 120, y + 16)], CREAM)
    cv.fill(x + 76, y + 16, 88, 4, CREAM)
    for i in range(4):
        cv.fill(x + 80 + i * 22, y + 20, 8, 18, CREAM)
    cv.fill(x + 72, y + 38, 96, 4, CREAM)
    # red bug on the roof
    cv.circle(x + 196, y + 12, 7, RED)
    cv.circle(x + 193, y + 10, 2, INK)
    cv.circle(x + 199, y + 10, 2, INK)
    for dx in (-8, 8):
        cv.line(x + 196, y + 14, x + 196 + dx, y + 20, RED, 2)
    # cracked screen line
    cv.line(x + 20, y + 8, x + 44, y + 36, RED, 2)
    cv.line(x + 44, y + 36, x + 30, y + 42, RED, 2)

def d_nvidia(cv, x, y, w, h):
    cv.fill(x, y, w, h, CHARCOAL)
    # chip
    cv.fill(x + 30, y + 10, 40, 24, (40, 160, 70))
    cv.fill(x + 40, y + 18, 20, 8, (20, 100, 45))
    for i in range(4):
        cv.fill(x + 22, y + 13 + i * 6, 8, 3, GOLDL)
        cv.fill(x + 70, y + 13 + i * 6, 8, 3, GOLDL)
    # rising chart arrow
    cv.line(x + 110, y + 36, x + 140, y + 26, (90, 220, 120), 3)
    cv.line(x + 140, y + 26, x + 170, y + 18, (90, 220, 120), 3)
    cv.line(x + 170, y + 18, x + 200, y + 8, (90, 220, 120), 3)
    cv.poly([(x + 200, y + 8), (x + 190, y + 8), (x + 200, y + 18)], (90, 220, 120))
    draw_text(cv, x + 112, y + 6, "$109.1B", 1, GOLDL, bold=True)

def d_vulcan(cv, x, y, w, h):
    cv.fill(x, y, w, h, (12, 22, 48))
    # rocket, tilted
    cv.poly([(x + 100, y + 6), (x + 112, y + 6), (x + 112, y + 26),
             (x + 100, y + 26)], WHITE)
    cv.poly([(x + 100, y + 6), (x + 106, y - 2), (x + 112, y + 6)], RED)
    cv.poly([(x + 100, y + 26), (x + 106, y + 34), (x + 112, y + 26)],
            (250, 160, 40))
    cv.poly([(x + 104, y + 34), (x + 108, y + 34), (x + 106, y + 42)],
            (250, 200, 80))
    # explosion puffs
    cv.circle(x + 130, y + 12, 4, (200, 200, 200))
    cv.circle(x + 142, y + 20, 3, (170, 170, 170))
    # lost satellites as small squares
    for sx, sy in [(150, 30), (170, 12), (190, 28), (210, 14), (225, 34)]:
        cv.fill(x + sx, y + sy, 5, 5, (150, 150, 160))
    # stars
    for sx, sy in [(20, 8), (40, 20), (60, 8), (80, 26)]:
        cv.circle(x + sx, y + sy, 1, WHITE)
    draw_text(cv, x + 8, y + 34, "40 LOST", 1, (255, 120, 120), bold=True)

def d_house(cv, x, y, w, h):
    cv.fill(x, y, w, h, CREAM)
    # capitol dome, navy silhouette
    cv.fill(x + 96, y + 30, 48, 10, NAVY)
    cv.poly([(x + 100, y + 30), (x + 140, y + 30), (x + 120, y + 10)], NAVY)
    cv.fill(x + 118, y + 4, 4, 8, NAVY)
    cv.circle(x + 120, y + 4, 2, NAVY)
    for i in range(5):
        cv.fill(x + 100 + i * 9, y + 30, 4, 10, NAVY)
    cv.fill(x + 92, y + 40, 56, 3, NAVY)
    # blue banner
    cv.fill(x + 170, y + 8, 56, 12, (40, 80, 180))
    draw_text(cv, x + 174, y + 11, "NEW", 1, WHITE, bold=True)
    # flag
    cv.fill(x + 14, y + 8, 2, 30, INK)
    cv.fill(x + 16, y + 8, 22, 12, (200, 40, 40))
    cv.fill(x + 16, y + 12, 22, 3, WHITE)
    cv.fill(x + 16, y + 17, 22, 3, WHITE)

def d_rwanda(cv, x, y, w, h):
    cv.fill(x, y, w, h, SAND)
    # Europe blob -> arrow -> Africa blob with pin
    cv.poly([(x + 30, y + 8), (x + 70, y + 8), (x + 78, y + 18),
             (x + 60, y + 26), (x + 34, y + 24)], (190, 170, 120))
    cv.poly([(x + 150, y + 14), (x + 210, y + 14), (x + 200, y + 40),
             (x + 170, y + 40), (x + 156, y + 26)], (210, 150, 90))
    cv.line(x + 82, y + 18, x + 146, y + 24, RED, 3)
    cv.poly([(x + 146, y + 24), (x + 136, y + 19), (x + 136, y + 29)], RED)
    cv.circle(x + 182, y + 26, 6, RED)
    cv.circle(x + 182, y + 26, 2, WHITE)
    # small flags of the five states
    for i, c in enumerate([(0, 0, 0), (200, 40, 40), (255, 255, 255),
                           (40, 80, 180), (255, 200, 40)]):
        cv.fill(x + 36 + i * 12, y + 34, 10, 6, c)

def d_yemen(cv, x, y, w, h):
    cv.fill(x, y, w, h, (232, 214, 170))
    # mountains
    cv.poly([(x + 10, y + 40), (x + 60, y + 10), (x + 110, y + 40)], BROWN)
    cv.poly([(x + 80, y + 40), (x + 130, y + 16), (x + 180, y + 40)],
            (150, 110, 70))
    cv.poly([(x + 52, y + 16), (x + 60, y + 10), (x + 68, y + 16)], WHITE)
    # arrow to Aden
    cv.line(x + 150, y + 8, x + 200, y + 8, RED, 3)
    cv.poly([(x + 200, y + 8), (x + 190, y + 3), (x + 190, y + 13)], RED)
    cv.circle(x + 210, y + 8, 5, RED)
    draw_text(cv, x + 196, y + 16, "ADEN", 1, REDD, bold=True)
    # fortress
    cv.fill(x + 20, y + 28, 24, 12, (120, 90, 60))
    cv.fill(x + 24, y + 22, 6, 6, (120, 90, 60))
    cv.fill(x + 34, y + 22, 6, 6, (120, 90, 60))

def d_bus(cv, x, y, w, h):
    cv.fill(x, y, w, h, SKY)
    # cliff
    cv.poly([(x + 150, y + 44), (x + 240, y + 44), (x + 240, y + 14),
             (x + 190, y + 22)], (150, 110, 70))
    cv.fill(x, y + 40, w, 4, (90, 90, 96))
    # yellow bus, nose over the edge
    cv.fill(x + 60, y + 18, 100, 20, (240, 190, 40))
    cv.fill(x + 60, y + 18, 100, 5, (200, 150, 20))
    for i in range(4):
        cv.fill(x + 68 + i * 22, y + 23, 14, 8, (180, 220, 240))
    cv.circle(x + 80, y + 40, 5, INK)
    cv.circle(x + 140, y + 40, 5, INK)
    # warning triangle
    cv.poly([(x + 18, y + 34), (x + 28, y + 14), (x + 38, y + 34)], RED)
    draw_text(cv, x + 25, y + 24, "!", 1, WHITE, bold=True)

def d_safrica(cv, x, y, w, h):
    cv.fill(x, y, w, h, CHARCOAL)
    draw_text(cv, x + 14, y + 6, "17", 3, WHITE, bold=True)
    # two location pins
    for px in (x + 150, x + 190):
        cv.circle(px, y + 16, 7, RED)
        cv.poly([(px - 5, y + 20), (px + 5, y + 20), (px, y + 30)], RED)
        cv.circle(px, y + 16, 2, WHITE)
    draw_text(cv, x + 140, y + 34, "TWO CITIES", 1, (200, 200, 200), bold=True)

def d_japan(cv, x, y, w, h):
    cv.fill(x, y, w, h, SKY)
    # rising sun
    cv.circle(x + 200, y + 14, 9, RED)
    # two jets
    for jx, jy in [(60, 22), (110, 12)]:
        cv.poly([(x + jx, y + jy), (x + jx + 34, y + jy + 6),
                 (x + jx + 34, y + jy + 10), (x + jx, y + jy + 8)],
                (70, 70, 78))
        cv.poly([(x + jx + 8, y + jy - 6), (x + jx + 16, y + jy + 6),
                 (x + jx + 10, y + jy + 6)], (70, 70, 78))
    # speed lines
    for ly in (24, 16, 32):
        cv.fill(x + 20, y + ly, 26, 2, WHITE)
    # sea
    cv.fill(x, y + 38, w, 6, (46, 110, 160))

# ------------------------------------------------------------------ data
# 12 pictured stories. Headline lines are wrapped by hand to <=18 chars
# (scale-2 bold, 12 px advance, panel text width 226 px).
PANELS = [
    ("EUROPE • WAR", RED, d_kerch,
     ["Kerch Bridge span", "falls in Ukrainian", "strike"],
     "A road span drops into the strait in Kyiv's seven-stage operation."),
    ("ASIA • DIPLOMACY", TEAL, d_manila,
     ["Trump in Manila;", "Xi, Trump, Putin", "meet Thursday"],
     "Signs Thailand trade deal; China confirms three-way talks Thursday."),
    ("MIDDLE EAST • GULF", MAROON, d_hormuz,
     ["Two tankers hit", "mines off Hormuz;", "US carrier arrives"],
     "Iran says mines hit two tankers; a third US carrier reaches the Gulf."),
    ("USA • MONEY", NAVY, d_jpmorgan,
     ["JPMorgan blames", "software bug for", "bank outage"],
     "Monday's failure hit Zelle and branches; a bug, not a cyberattack."),
    ("MARKETS • TECH", GREEN, d_nvidia,
     ["Nvidia reports", "after the bell;", "first since Huang"],
     "Analysts expect $2.47 a share on $109.1bn. First since Huang resigned."),
    ("SCIENCE • SPACE", PURPLE, d_vulcan,
     ["Vulcan rocket", "fails; 40 Amazon", "satellites lost"],
     "ULA rocket fails 10 minutes after launch; its first outright failure."),
    ("USA • POLITICS", NAVY2, d_house,
     ["House Democrats", "set opening agenda"],
     "New majority targets Medicaid cuts, ACA credits, Iran war, tariffs."),
    ("EUROPE • MIGRATION", BROWN, d_rwanda,
     ["Five EU nations", "plan Rwanda return", "hub"],
     "Germany, Denmark, Austria, Greece and the Netherlands to send cases."),
    ("MIDDLE EAST • YEMEN", OCHRE, d_yemen,
     ["Houthis push army", "back to Aden"],
     "Government forces quit the Red Sea coast to defend the interim capital."),
    ("ASIA • INDIA", TEAL, d_bus,
     ["Bus plunges into", "ravine, 6 killed"],
     "At least six killed and 20 hurt in Tehri Garhwal, NDTV reports."),
    ("AFRICA • S. AFRICA", CHARCOAL, d_safrica,
     ["17 killed in two", "shootings, South", "Africa"],
     "Two separate shootings leave at least 17 people dead, police say."),
    ("ASIA • DIPLOMACY", REDD, d_japan,
     ["Japan scrambles", "jets after Russian", "intrusion"],
     "Tokyo protests to Moscow after two suspected Russian jets intrude."),
]

# 24 more stories, numbered 13-36. Each must fit one line at scale 1
# in a 490 px column (81 chars max).
ALSO_ON = [
    ("KYIV", "Russia hits two bridges over the Dnipro; heat, water, power cut"),
    ("RED SEA", "Saudi-backed forces pull back from the coast"),
    ("GULF", "Third US carrier, USS Theodore Roosevelt, reaches the Gulf"),
    ("IRAN", "Iran claims a US drone seized"),
    ("IRAN", "Iran claims more tankers hit"),
    ("CHINA", "Xi, Trump and Putin to meet Thursday in Shenzhen"),
    ("UKRAINE", "Russia says it downed 1,336 drones in one night"),
    ("USA", "Pentagon fails financial audit, 9th year in a row"),
    ("ESTONIA", "Russian border crossings to shut on 1 Dec"),
    ("SINGAPORE", "Seeks trusted access to AI chips"),
    ("USA", "New chip-sale licences for SE Asia data centres"),
    ("USA", "Vance: Iran war must not run for two years"),
    ("THAILAND", "To drop US tariffs; buy $2.6bn farm goods"),
    ("MANILA", "Protests over Pax Silica chip plan"),
    ("USA", "Washington state faces $4bn budget gap"),
    ("USA", "Seattle I-5 express lanes shut for repairs"),
    ("CANADA", "Carney returns to China a political star, a year on"),
    ("USA", "Colleges struggle as foreign students turn away"),
    ("SPORT", "Sri Lanka bowled out for 98 in Rawalpindi"),
    ("BAHRAIN", "64 jailed for life over alleged Iran links"),
    ("PERU", "Pope Leo XIV returns to port city he served"),
    ("TECH", "Microsoft explains last week's global outage"),
    ("USA", "13 babies born with congenital measles"),
    ("USA", "Petrol averages $3.78 a gallon"),
]

NUMBERS = [
    ("1,336", "Ukrainian drones Russia says it downed in a night"),
    ("40", "Amazon satellites lost in the Vulcan failure"),
    ("$109.1BN", "Nvidia revenue expected in Q3 results"),
    ("17", "killed in two shootings in South Africa"),
    ("$4.8TN", "Pentagon assets the audit cannot verify"),
    ("$3.78", "average US petrol price per gallon"),
]

# ---------------------------------------------------------------- layout
def draw_panel(cv, x, y, num, kicker, accent, draw_fn, headline, deck):
    w, h = 242, 150
    cv.fill(x, y, w, h, PAPER2)
    cv.fill(x, y, w, 3, accent)
    cv.rect(x, y, w, h, BORDER, 1)
    draw_fn(cv, x + 1, y + 4, w - 2, 44)
    # number badge
    cv.circle(x + 16, y + 18, 11, WHITE)
    cv.circle(x + 16, y + 18, 10, RED)
    s = str(num)
    draw_text(cv, x + 16 - text_w(s, 1) // 2, y + 15, s, 1, WHITE, bold=True)
    # kicker
    draw_text(cv, x + 10, y + 56, kicker, 1, accent, bold=True)
    # headline, scale 2 bold, 15 px leading so stacked lines breathe
    hy = y + 70
    for line in headline:
        draw_text(cv, x + 10, hy, line, 2, INK, bold=True)
        hy += 15
    # deck, scale 1, two lines max
    for i, line in enumerate(wrap(deck, 37)[:2]):
        draw_text(cv, x + 10, hy + 4 + i * 9, line, 1, (60, 58, 50))

def main():
    cv = Canvas(W, H, PAPER)

    # ---- masthead band
    cv.fill(0, 0, W, 102, NAVY)
    cv.fill(0, 102, W, 3, GOLD)
    draw_text(cv, 16, 14, "THE DAY IN WORLD NEWS", 2, GOLDL, bold=True)
    draw_text(cv, W - 16 - text_w("36 STORIES • 5 CONTINENTS • ONE PAGE", 2),
              14, "36 STORIES • 5 CONTINENTS • ONE PAGE", 2, GOLDL, bold=True)
    draw_text_c(cv, W // 2, 40, "TUESDAY 17 NOVEMBER 2026", 4, WHITE)
    draw_text_c(cv, W // 2, 76,
                "KERCH BRIDGE FALLS • TANKERS BURN OFF HORMUZ • "
                "TRUMP IN MANILA • VULCAN FAILS",
                1, GOLDL, bold=True)

    # ---- world map strip
    draw_map(cv, 16, 110, 992, 90)
    draw_text_c(cv, W // 2, 204,
                "WHERE IT HAPPENED — NUMBERED DOTS MARK THE 12 PICTURED STORIES",
                1, GREY)

    # ---- 12 pictured panels, 4 x 3
    gy = 220
    for i, (kicker, accent, fn, headline, deck) in enumerate(PANELS):
        px = 16 + (i % 4) * 250
        py = gy + (i // 4) * 158
        draw_panel(cv, px, py, i + 1, kicker, accent, fn, headline, deck)

    # ---- by the numbers
    ny = 694
    draw_text(cv, 16, ny, "BY THE NUMBERS", 1, NAVY, bold=True)
    cv.fill(16, ny + 11, 992, 2, NAVY)
    cell_w = (992 - 5 * 8) // 6
    for i, (num, cap) in enumerate(NUMBERS):
        cx = 16 + i * (cell_w + 8)
        draw_text(cv, cx, ny + 18, num, 3, NAVY, bold=True)
        for j, line in enumerate(wrap(cap, 25)[:2]):
            draw_text(cv, cx, ny + 42 + j * 9, line, 1, (60, 58, 50))
        if i < 5:
            cv.fill(cx + cell_w + 3, ny + 16, 1, 40, BORDER)

    # ---- also on Tuesday: 24 more stories, 2 columns
    ay = 766
    draw_text(cv, 16, ay, "ALSO ON TUESDAY — 24 MORE STORIES", 2, INK, bold=True)
    cv.fill(16, ay + 17, 992, 2, INK)
    ly = ay + 24
    for col in range(2):
        lx = 16 + col * 504
        for row in range(12):
            idx = col * 12 + row
            tag, text = ALSO_ON[idx]
            yy = ly + row * 16
            num = str(13 + idx)
            draw_text(cv, lx, yy, num, 1, RED, bold=True)
            tx = lx + text_w(num, 1) + 6
            draw_text(cv, tx, yy, tag, 1, NAVY, bold=True)
            tx += text_w(tag, 1) + 6
            draw_text(cv, tx, yy, "— " + text, 1, INK)

    # ---- footer
    cv.fill(16, 982, 992, 1, BORDER)
    draw_text_c(cv, W // 2, 990,
                "EVERY STORY HAPPENED OR WAS FIRST REPORTED ON TUESDAY "
                "17 NOVEMBER 2026. DISPUTED CLAIMS ARE ATTRIBUTED.",
                1, GREY)
    draw_text_c(cv, W // 2, 1000,
                "SOURCES: BBC • AP • REUTERS • AFP • AL JAZEERA • NDTV. "
                "ORIGINAL DRAWINGS.",
                1, GREY)

    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    write_png(os.path.join(out, "entry.png"), cv.px, W, H)

if __name__ == "__main__":
    main()
