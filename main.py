#!/usr/bin/env python3
"""Draw a newspaper front page summing up Wednesday, 25 November 2026.

Pure Python 3 standard library. No network, no randomness, no timestamps.
Deterministic: running it twice produces byte-identical output.

Usage: python3 main.py [output-path]
  Output goes to the first argument, else $MAKEFUN_OUTPUT_DIR/entry.png,
  else entry.png next to this file.
"""

import hashlib
import os
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (248, 243, 230)
INK = (20, 20, 20)
RED = (163, 22, 33)
BLUE = (29, 53, 87)
GREY = (90, 86, 78)
LIGHT = (226, 219, 203)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 strings of 5 chars, '#' = ink, '.' = blank.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "00010", "00110"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    'q': ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.set(x, y, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, color):
        x, y, d = 0, r, 3 - 2 * r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y),
                           (cx - x, cy - y), (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self.set(px, py, color)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    def ellipse(self, cx, cy, rx, ry, color):
        # Sampled outline: deterministic, no floats in output path beyond this.
        import math
        for deg in range(360):
            a = math.radians(deg)
            self.set(int(cx + rx * math.cos(a)), int(cy + ry * math.sin(a)), color)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == '1':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def center(self, y, s, scale, color, x0=0, x1=None):
        x1 = self.w if x1 is None else x1
        x = x0 + (x1 - x0 - self.text_w(s, scale)) // 2
        return self.text(x, y, s, scale, color)


def wrap(canvas, text, max_w, scale):
    """Greedy word wrap; returns list of lines that fit max_w px."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if canvas.text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_globe(cv, cx, cy, r):
    cv.circle(cx, cy, r, BLUE)
    cv.circle(cx, cy, r - 1, BLUE)
    # Equator and tropics.
    cv.ellipse(cx, cy, r, int(r * 0.28), BLUE)
    cv.ellipse(cx, cy, r, int(r * 0.62), BLUE)
    # Meridians.
    cv.ellipse(cx, cy, int(r * 0.28), r, BLUE)
    cv.ellipse(cx, cy, int(r * 0.62), r, BLUE)
    cv.vline(cx, cy - r, 2 * r, BLUE)
    cv.hline(cx - r, cy, 2 * r, BLUE)
    # Land dots: a few small blocks suggesting continents.
    for dx, dy in ((-38, -42), (-30, -30), (18, -48), (34, -28), (-52, 22),
                   (8, 34), (44, 8), (-8, -58)):
        cv.rect(cx + dx, cy + dy, 9, 6, RED)


def story(cv, x, y, w, kicker, headline, body):
    cv.text(x, y, kicker, 2, RED)
    y += 20
    for line in wrap(cv, headline, w, 3):
        cv.text(x, y, line, 3, INK)
        y += 26
    y += 4
    for line in wrap(cv, body, w, 2):
        cv.text(x, y, line, 2, INK)
        y += 16
    return y


def build():
    cv = Canvas(W, H, PAPER)
    # Double border.
    cv.rect(0, 0, W, 3, INK)
    cv.rect(0, H - 3, W, 3, INK)
    cv.rect(0, 0, 3, H, INK)
    cv.rect(W - 3, 0, 3, H, INK)
    cv.rect(10, 10, W - 20, 2, INK)
    cv.rect(10, H - 12, W - 20, 2, INK)

    # Masthead.
    cv.center(26, "THE WORLD TODAY", 7, INK)
    cv.hline(36, 108, W - 72, INK, 3)
    cv.center(120, "WEDNESDAY, 25 NOVEMBER 2026", 3, RED)
    cv.center(148, "One day's news from every corner of the globe", 2, GREY)
    cv.hline(36, 172, W - 72, INK, 2)

    # Lead headline.
    cv.text(40, 190, "KYIV SINKS RUSSIAN WARSHIP", 4, INK)
    cv.text(40, 224, "OFF LIBYA; MOSCOW HITS BACK", 4, INK)
    cv.hline(40, 262, 640, RED, 2)

    # Lead body (left) + globe (right).
    lead = (
        "Ukraine said its sea drones sank the Russian corvette Merkury at "
        "Benghazi, Libya, on 22 November, and hit the arms cargo ship Angara. "
        "Russia answered overnight with one of the war's biggest air attacks: "
        "about 100 missiles and 400 drones. Three bridges in Kyiv were hit "
        "and three people killed; two died in Odesa."
    )
    y = 276
    for line in wrap(cv, lead, 640, 2):
        cv.text(40, y, line, 2, INK)
        y += 17
    draw_globe(cv, 848, 320, 88)

    # Section header.
    cv.hline(36, 420, W - 72, INK, 2)
    cv.center(432, "THE DAY IN BRIEF", 3, INK)
    cv.hline(36, 462, W - 72, INK, 1)

    cols = [(36, 301), (361, 301), (686, 301)]
    row1 = [
        ("MARKETS", "HUANG'S COMEBACK COOLS",
         "Nvidia shares soared 31% on Monday as Jensen Huang returned as "
         "chief executive, adding $952bn in value. On Tuesday the rally "
         "faded, with shares down over 5%."),
        ("CLIMATE", "CLIMATE TALKS END WITH NO DEAL",
         "COP31 closed in Antalya, Turkiye, on 22 November with no final "
         "pact. Fossil-fuel phase-out language and a $120bn adaptation "
         "target were dropped. Talks move to COP32 in 2027."),
        ("MIDDLE EAST", "HOUTHIS STRIKE RIYADH AGAIN",
         "Yemen's Houthis hit Riyadh's tallest skyscraper for a second "
         "time in under a week, injuring 11 people. A Saudi-led coalition "
         "answered with strikes on Yemen's Hodeidah port."),
    ]
    row2 = [
        ("SPACE", "FIRST PAKISTANI IN SPACE",
         "China launched Shenzhou-24 on 25 November carrying the first "
         "Pakistani astronaut, Zeeshan Ali, to its space station. Pakistan "
         "hailed the flight as a milestone."),
        ("GAZA", "HAMAS SECURITY CHIEF KILLED",
         "Israeli air strikes on Gaza City killed seven people, including "
         "Hamas internal security director Naim Abu Nahal, Palestinian "
         "officials said, despite a ceasefire."),
        ("WASHINGTON", "TRUMP HONOURS GIULIANI",
         "President Donald Trump awarded Rudy Giuliani the Medal of "
         "Freedom, the highest US civilian honour, praising the former New "
         "York mayor as a staunch ally since 9/11."),
    ]
    for (x, w), (kick, head, body) in zip(cols, row1):
        story(cv, x, 478, w, kick, head, body)
    cv.hline(36, 690, W - 72, LIGHT, 1)
    for (x, w), (kick, head, body) in zip(cols, row2):
        story(cv, x, 704, w, kick, head, body)
    # Thin vertical rules between columns.
    for vx in (349, 674):
        cv.vline(vx, 478, 420, LIGHT, 1)

    # Bottom strip: weather and disasters.
    cv.hline(36, 916, W - 72, INK, 2)
    cv.text(40, 928, "WEATHER & DISASTERS", 2, RED)
    weather = (
        "Orange flood alerts in south-east France, up to 150 mm of rain. "
        "Hanoi gas blast kills six; Turkish helicopter crash kills five; "
        "UAE bus crash kills 13."
    )
    y = 950
    for line in wrap(cv, weather, 944, 2):
        cv.text(40, y, line, 2, INK)
        y += 17

    # Footer.
    cv.text(40, 994, "All stories as reported on Wednesday, 25 November 2026.",
            1, GREY)
    return cv


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    os.chmod(path, 0o644)
    with open(path, "rb") as f:
        data = f.read()
    print("wrote %s: %d bytes sha256=%s" % (path, len(data),
                                            hashlib.sha256(data).hexdigest()))
    return data


def main():
    if len(sys.argv) > 1:
        out = sys.argv[1]
    elif os.environ.get("MAKEFUN_OUTPUT_DIR"):
        out = os.path.join(os.environ["MAKEFUN_OUTPUT_DIR"], "entry.png")
    else:
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "entry.png")
    cv = build()
    write_png(cv, out)


if __name__ == "__main__":
    main()
