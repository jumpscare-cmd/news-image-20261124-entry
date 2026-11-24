#!/usr/bin/env python3
"""Draw a newspaper front page summing up Tuesday 24 November 2026.

Pure Python 3 standard library only: no network, no randomness, no
timestamps in the output. Writes entry.png deterministically.

Usage: python3 main.py [output_path]
  Output goes to argv[1], else $MAKEFUN_OUTPUT_DIR/entry.png,
  else <this script's directory>/entry.png.
"""

import hashlib
import os
import struct
import sys
import zlib

W, H = 1024, 1024
PAPER = (253, 252, 247)
INK = (12, 12, 12)
RED = (139, 0, 0)
GREY = (90, 90, 90)

# ---------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph is 7 rows of 5 bits, written as strings.
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
    'j': ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10001"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    'q': ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11100", "01000", "01000", "01001", "00110"),
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
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '^': ("00100", "01010", "10001", "00000", "00000", "00000", "00000"),
    '\\': ("10000", "01000", "01000", "00100", "00010", "00010", "00001"),
    '~': ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
}

BLANK = ("00000", "00000", "00000", "00000", "00000", "00000", "00000")


def text_width(text, scale):
    return len(text) * 6 * scale - scale


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

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:(yy * self.w + x1) * 3] = bytes(color) * (x1 - x0)

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def circle(self, cx, cy, r, color, thick=2):
        # midpoint circle outline
        x, y, d = 0, r, 3 - 2 * r
        while x <= y:
            for dx, dy in ((x, y), (y, x), (-x, y), (-y, x),
                           (x, -y), (y, -x), (-x, -y), (-y, -x)):
                self.fill_rect(cx + dx - thick // 2, cy + dy - thick // 2,
                               thick, thick, color)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    def ellipse(self, cx, cy, rx, ry, color, thick=1):
        # parametric ellipse outline
        import math
        steps = max(64, int(2 * math.pi * max(rx, ry)))
        for i in range(steps + 1):
            t = 2 * math.pi * i / steps
            x = int(round(cx + rx * math.cos(t)))
            y = int(round(cy + ry * math.sin(t)))
            self.fill_rect(x - thick // 2, y - thick // 2, thick, thick, color)

    def chord(self, cx, cy, r, dy, color, thick=1):
        """Horizontal chord of a circle at vertical offset dy."""
        if abs(dy) >= r:
            return
        import math
        half = int(math.sqrt(r * r - dy * dy))
        self.fill_rect(cx - half, cy + dy, 2 * half, thick, color)

    def draw_text(self, x, y, scale, text, color):
        cx = x
        for ch in text:
            glyph = FONT.get(ch, BLANK)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale
        return cx - x

    def text_centered(self, y, scale, text, color, cx=512):
        w = text_width(text, scale)
        self.draw_text(cx - w // 2, y, scale, text, color)

    def text_left(self, x, y, scale, text, color):
        self.draw_text(x, y, scale, text, color)


def wrap(text, max_chars):
    words = text.split(' ')
    lines, cur = [], ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- layout
M = 36                      # margin
CW = W - 2 * M              # content width = 952


def draw_poster(cv):
    # ---- top line
    cv.text_left(M, 18, 2, "VOL. I - NO. 328", GREY)
    right = "ONE DAY - ONE PAGE"
    cv.text_left(W - M - text_width(right, 2), 18, 2, right, GREY)
    cv.hline(M, 36, CW, INK, 2)

    # ---- masthead
    cv.text_centered(50, 8, "THE WORLD TODAY", INK)
    cv.hline(M, 116, CW, INK, 1)
    cv.hline(M, 120, CW, INK, 3)

    # ---- date line
    cv.text_centered(134, 4, "TUESDAY, 24 NOVEMBER 2026", RED)
    cv.hline(M, 172, CW, INK, 2)

    # ---- lead headline
    cv.text_centered(190, 5, "UKRAINE SINKS RUSSIAN", INK)
    cv.text_centered(233, 5, "WARSHIP OFF LIBYA", INK)

    # ---- lead subhead
    cv.text_centered(284, 3, "KYIV'S DRONES STRIKE FAR FROM THE FRONT", GREY)
    cv.hline(M, 314, CW, INK, 1)

    # ---- lead body (left) + globe (right)
    lead = ("Ukraine said its sea drones sank the Russian corvette "
            "Merkury at Benghazi, Libya, on Sunday. Seven drones hit "
            "the ship and destroyed a Ka-27 helicopter aboard. Kyiv "
            "also hit the cargo ship MV Angara.")
    y = 330
    for line in wrap(lead, 34):
        cv.text_left(M, y, 3, line, INK)
        y += 24

    # globe
    gx, gy, gr = 824, 405, 85
    cv.circle(gx, gy, gr, INK, 3)
    for dy in (-42, 0, 42):
        cv.chord(gx, gy, gr, dy, INK, 1)
    cv.ellipse(gx, gy, 42, gr, INK, 1)
    # abstract land blobs
    cv.fill_rect(gx - 56, gy - 50, 34, 22, INK)
    cv.fill_rect(gx - 12, gy - 28, 26, 18, INK)
    cv.fill_rect(gx + 8, gy + 18, 40, 20, INK)
    cv.fill_rect(gx - 50, gy + 30, 24, 16, INK)
    cv.text_centered(494, 2, "2,400 KM FROM THE FRONT LINE", GREY, cx=gx)

    # ---- section rule
    cv.hline(M, 522, CW, INK, 3)
    cv.hline(M, 527, CW, INK, 1)
    cv.text_centered(540, 3, "THE DAY'S OTHER NEWS", INK)

    # ---- secondary stories: 3 columns x 2 rows
    stories = [
        ("HUANG BACK AT NVIDIA",
         "Nvidia reinstated Jensen Huang as CEO, 11 days after he "
         "resigned. Trump pushed for his return. Shares jumped 31%."),
        ("NUCLEAR SPACE WEAPON FEAR",
         "Allies warned Russia may launch a nuclear-armed satellite "
         "next month. NATO vowed to defend space."),
        ("TRUMP SPEEDS EXECUTIONS",
         "President Trump ordered federal executions to be expedited, "
         "in a Justice Department speech on violent crime."),
        ("STATES SUE MUSK OVER GROK",
         "US states sued companies linked to Elon Musk, saying the "
         "Grok chatbot made sexualised images of people without "
         "consent."),
        ("KYIV STRIKES KILL AT LEAST 14",
         "Russian strikes on the Kyiv region killed at least 14 "
         "people, Ukraine said, as attacks on cities continued."),
        ("UN CHIEF SEEKS AI RISK RULES",
         "The UN chief called for a global AI risk framework within "
         "a year, warning the technology is outpacing its safeguards."),
    ]
    col_w, gap = 300, 26
    for idx, (head, body) in enumerate(stories):
        col = idx % 3
        row = idx // 3
        x = M + col * (col_w + gap)
        y0 = 576 + row * 150
        yy = y0
        for line in wrap(head, 16):
            cv.text_left(x, yy, 3, line, INK)
            yy += 24
        yy += 4
        for line in wrap(body, 25):
            cv.text_left(x, yy, 2, line, INK)
            yy += 17
        if col < 2:
            cv.vline(x + col_w + 13, y0, 130, GREY, 1)

    # ---- in brief
    cv.hline(M, 876, CW, INK, 2)
    cv.text_left(M, 888, 3, "IN BRIEF", RED)
    briefs = [
        "INDIA-EU TRADE PACT: signing set for 16 December in Brussels.",
        "GTA VI HACKER: Arion Kurtaj, 21, jailed for seven years in London.",
        "THANKSGIVING TRAVEL: storms and airline glitches threaten US trips.",
        "INDONESIA: Prabowo names a loyalist as vice-presidential pick.",
    ]
    y = 916
    for b in briefs:
        cv.text_left(M, y, 2, "- " + b, INK)
        y += 16

    # ---- footer
    cv.hline(M, 990, CW, INK, 1)
    cv.text_centered(998, 2, "ALL STORIES AS REPORTED ON 24 NOVEMBER 2026", GREY)


# ---------------------------------------------------------------- png
def chunk(ctype, data):
    out = ctype + data
    return struct.pack(">I", len(data)) + out + struct.pack(
        ">I", zlib.crc32(out) & 0xFFFFFFFF)


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    if len(sys.argv) > 1:
        out_path = sys.argv[1]
    elif os.environ.get("MAKEFUN_OUTPUT_DIR"):
        out_path = os.path.join(os.environ["MAKEFUN_OUTPUT_DIR"], "entry.png")
    else:
        out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "entry.png")
    cv = Canvas(W, H, PAPER)
    draw_poster(cv)
    data = encode_png(cv)
    with open(out_path, "wb") as f:
        f.write(data)
    os.chmod(out_path, 0o644)
    # verify by reading back
    with open(out_path, "rb") as f:
        back = f.read()
    assert back == data, "read-back mismatch"
    assert len(back) <= 1048576, "over 1 MiB"
    w, h = struct.unpack(">II", back[16:24])
    assert (w, h) == (W, H), "wrong dimensions"
    print("wrote %s" % out_path)
    print("size: %d bytes" % len(back))
    print("sha256: %s" % hashlib.sha256(back).hexdigest())
    print("dimensions: %dx%d" % (w, h))


if __name__ == "__main__":
    main()
