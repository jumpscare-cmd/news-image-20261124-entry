#!/usr/bin/env python3
"""Draw the front page of THE WORLD TODAY for Tuesday, 24 November 2026.

Standard library only. Writes a deterministic 1024x1024 PNG to the path
given as argv[1], else $MAKEFUN_OUTPUT_DIR/entry.png, else entry.png next
to this file. No network, no randomness, no timestamps in the output.
"""

import hashlib
import os
import struct
import sys
import zlib

W, H = 1024, 1024
PAPER = (248, 243, 230)
INK = (17, 17, 17)
RED = (163, 22, 33)
BLUE = (31, 78, 121)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 characters, '#' = ink.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    'a': (".....", ".....", ".####", "....#", ".####", "#...#", ".####"),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    'g': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    'j': ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", ".##.."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '&': (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    '%': ("##..#", "##.#.", "..#..", ".#...", "#.#.#", "#..##", "#..##"),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '*': (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def char_advance(scale):
    return 6 * scale


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x0, x1, y, color, thick=1):
        for t in range(thick):
            for xx in range(x0, x1 + 1):
                self.set(xx, y + t, color)

    def vline(self, x, y0, y1, color, thick=1):
        for t in range(thick):
            for yy in range(y0, y1 + 1):
                self.set(x + t, yy, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.set(x, y, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, color, thick=2):
        for a in range(360):
            import math
            x = int(round(cx + r * math.cos(math.radians(a))))
            y = int(round(cy + r * math.sin(math.radians(a))))
            for t in range(thick):
                self.set(x + t, y, color)
                self.set(x, y + t, color)

    def ellipse(self, cx, cy, rx, ry, color, thick=1):
        import math
        for a in range(720):
            x = int(round(cx + rx * math.cos(math.radians(a / 2))))
            y = int(round(cy + ry * math.sin(math.radians(a / 2))))
            for t in range(thick):
                self.set(x, y + t, color)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                glyph = FONT[' ']
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '#':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, scale, color):
        x = cx - text_width(s, scale) // 2
        return self.text(x, y, s, scale, color)


def wrap(text, max_width, scale):
    """Greedy word wrap; returns list of lines fitting max_width px."""
    adv = 6 * scale
    words = text.split(' ')
    lines = []
    cur = ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if len(trial) * adv - scale <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(cv, x, y, w, kicker, headline, body, kcolor=RED):
    """One story block: kicker, headline, body. Returns y below block."""
    cv.text(x, y, kicker, 2, kcolor)
    y += 16
    for ln in wrap(headline, w, 3):
        cv.text(x, y, ln, 3, INK)
        y += 22
    y += 4
    for ln in wrap(body, w, 2):
        cv.text(x, y, ln, 2, INK)
        y += 14
    return y


def draw_bar_chart(cv, x, y, w):
    """Small horizontal bar chart: Nvidia share level around the return."""
    cv.text(x, y, "NVIDIA SHARES +31%", 2, BLUE)
    y += 18
    bars = [("12 NOV", 100), ("20 NOV", 67), ("23 NOV", 88)]
    for label, val in bars:
        cv.text(x, y, label, 2, INK)
        bw = val * 130 // 100
        cv.rect(x + 78, y + 1, bw, 10, BLUE if val == 88 else INK)
        y += 16
    return y


# ---------------------------------------------------------------- page
def build():
    cv = Canvas(W, H, PAPER)
    # double border
    cv.rect(14, 14, W - 28, 3, INK)
    cv.rect(14, H - 17, W - 28, 3, INK)
    cv.rect(14, 14, 3, H - 28, INK)
    cv.rect(W - 17, 14, 3, H - 28, INK)
    cv.rect(24, 24, W - 48, 1, INK)
    cv.rect(24, H - 25, W - 48, 1, INK)
    cv.rect(24, 24, 1, H - 48, INK)
    cv.rect(W - 25, 24, 1, H - 48, INK)

    # masthead
    cv.text_center(W // 2, 44, "THE WORLD TODAY", 6, INK)
    cv.hline(40, W - 40, 100, RED, 3)
    cv.hline(40, W - 40, 106, INK, 1)
    cv.text(40, 118, "EST. 2026", 2, INK)
    cv.text_center(W // 2, 116, "Tuesday, 24 November 2026", 3, INK)
    cv.text(W - 40 - text_width("PRICE $1", 2), 118, "PRICE $1", 2, INK)
    cv.hline(40, W - 40, 148, INK, 2)

    # kicker + lead headline
    cv.text(40, 166, "WAR IN UKRAINE REACHES THE MEDITERRANEAN", 2, RED)
    cv.text(40, 192, "UKRAINE SINKS RUSSIAN", 5, INK)
    cv.text(40, 232, "WARSHIP OFF LIBYA", 5, INK)
    lead = ("Seven Ukrainian sea drones sank the Russian corvette Merkury "
            "as she lay at Benghazi, President Zelenskyy said on Monday. "
            "A Ka-27 helicopter aboard was destroyed, and the cargo ship "
            "MV Angara, said to be carrying arms, was also hit.")
    y = 288
    for ln in wrap(lead, 600, 2):
        cv.text(40, y, ln, 2, INK)
        y += 15
    cv.text(40, y + 6, "Satellite pictures show the 2023-built warship", 2, INK)
    cv.text(40, y + 21, "capsized, only her bow above the water.", 2, INK)

    # globe illustration, right of the lead
    gx, gy, gr = 845, 275, 88
    cv.circle(gx, gy, gr, INK, 3)
    cv.ellipse(gx, gy, gr, gr // 3, INK)
    cv.ellipse(gx, gy, gr // 3, gr, INK)
    cv.hline(gx - gr, gx + gr, gy - gr // 2, INK, 1)
    cv.hline(gx - gr, gx + gr, gy + gr // 2, INK, 1)
    cv.vline(gx, gy - gr, gy + gr, INK, 1)
    # marker dot for Benghazi on the globe
    cv.rect(gx + 18, gy - 6, 8, 8, RED)
    cv.text_center(gx, gy + gr + 12, "BENGHAZI, LIBYA", 2, RED)
    cv.text_center(gx, gy + gr + 30, "Seven sea drones,", 2, INK)

    cv.hline(40, W - 40, 412, INK, 2)

    # three columns of stories
    colw = 300
    xs = [40, 362, 684]
    y0 = 428
    y1 = 640
    draw_block(cv, xs[0], y0, colw, "BUSINESS",
               "HUANG IS BACK AT NVIDIA",
               "The board reinstated Jensen Huang as chief executive and "
               "president on Monday, 11 days after he resigned.")
    draw_bar_chart(cv, xs[0], 566, colw)
    draw_block(cv, xs[0], y1, colw, "TECH",
               "GTA VI HACKER WALKS FREE",
               "Arion Kurtaj, 21, was jailed for seven years at Woolwich "
               "Crown Court for the 2022 Rockstar hack and other Lapsus$ "
               "attacks. He walked free the same day, time served.")
    draw_block(cv, xs[1], y0, colw, "WASHINGTON",
               "TRUMP SPEEDS UP EXECUTIONS",
               "President Trump signed a memo ordering the Justice "
               "Department to seek the death penalty more widely and to "
               "carry out federal death sentences as fast as possible.")
    draw_block(cv, xs[1], y1, colw, "COURTS",
               "STATES SUE MUSK OVER GROK IMAGES",
               "Virginia and Oregon sued Musk companies, saying Grok's "
               "spicy mode made sexualised images of real people, "
               "including children, without safeguards.")
    draw_block(cv, xs[2], y0, colw, "UKRAINE",
               "14 KILLED IN KYIV STRIKES",
               "Russian strikes killed at least 14 people across the Kyiv "
               "region. Ten died in Dymer, where a five-storey block "
               "partly collapsed; three more died at a supermarket.")
    draw_block(cv, xs[2], y1, colw, "UNITED NATIONS",
               "UN CHIEF SEEKS AI RISK RULES",
               "Secretary-General Antonio Guterres called on states to "
               "agree a global framework for AI risk management within a "
               "year, with independent oversight, in Barbados.")

    cv.hline(40, W - 40, 816, INK, 2)

    # briefs
    cv.text(40, 830, "IN BRIEF", 3, RED)
    briefs = [
        "INDIA-EU: India and the EU may sign their trade pact on 16 December.",
        "THANKSGIVING: Storms on both US coasts threaten holiday travel.",
        "JAKARTA: Prabowo named Sugiono and Amran Sulaiman as his VP candidates.",
    ]
    y = 864
    for ln in briefs:
        cv.text(40, y, ln, 2, INK)
        y += 15

    cv.hline(40, W - 40, 930, INK, 1)
    cv.text_center(W // 2, 944, "THE WORLD TODAY - TUESDAY, 24 NOVEMBER 2026",
                   2, INK)
    return cv


# ---------------------------------------------------------------- PNG out
def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += cv.px[yy * W * 3:(yy + 1) * W * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    os.chmod(path, 0o644)
    return png


def main():
    if len(sys.argv) > 1:
        dest = sys.argv[1]
    elif os.environ.get("MAKEFUN_OUTPUT_DIR"):
        dest = os.environ["MAKEFUN_OUTPUT_DIR"]
    else:
        dest = os.path.dirname(os.path.abspath(__file__))
    if dest.endswith(".png"):
        path = dest
    else:
        path = os.path.join(dest, "entry.png")
    cv = build()
    png = write_png(cv, path)
    # verify by reading back
    with open(path, "rb") as f:
        back = f.read()
    assert back == png, "read-back mismatch"
    sha = hashlib.sha256(back).hexdigest()
    print("wrote %s (%d bytes) sha256=%s" % (path, len(back), sha))
    return 0


if __name__ == "__main__":
    sys.exit(main())
