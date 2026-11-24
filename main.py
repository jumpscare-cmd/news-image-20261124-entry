#!/usr/bin/env python3
"""Draw the front page of THE WORLD TODAY for Tuesday, 24 November 2026.

Standard library only. No network, no randomness, no timestamps.
Deterministic: running twice produces byte-identical output.
"""
import hashlib
import math
import os
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (163, 22, 33)
NAVY = (26, 58, 92)
GREY = (90, 86, 78)
LIGHT = (232, 226, 210)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 characters, '#' = ink.
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
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
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
    'j': ("00010", "00000", "00110", "00010", "00010", "00010", "01100"),
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
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '\u2014': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns list of lines."""
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for w in words:
            trial = w if not cur else cur + " " + w
            if text_width(trial, scale) <= max_width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


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
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

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
        steps = max(8, int(2 * math.pi * max(rx, ry)))
        for i in range(steps + 1):
            a = 2 * math.pi * i / steps
            self.set(int(cx + rx * math.cos(a)), int(cy + ry * math.sin(a)), color)

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def draw_char(self, x, y, ch, scale, color):
        glyph = FONT.get(ch)
        if glyph is None:
            glyph = FONT['?']
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    self.rect(x + col * scale, y + row * scale, scale, scale, color)

    def draw_text(self, x, y, text, scale, color):
        cx = x
        for ch in text:
            self.draw_char(cx, y, ch, scale, color)
            cx += 6 * scale
        return cx - x

    def draw_text_centered(self, cx, y, text, scale, color):
        w = text_width(text, scale)
        self.draw_text(cx - w // 2, y, text, scale, color)

    def draw_para(self, x, y, text, scale, color, max_width, leading=None):
        if leading is None:
            leading = 9 * scale
        for line in wrap_text(text, scale, max_width):
            self.draw_text(x, y, line, scale, color)
            y += leading
        return y


def png_bytes(canvas):
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# ---------------------------------------------------------------- layout
M = 30                      # page margin
CW = W - 2 * M              # content width


def draw_globe(cv, x, y, size, color):
    cx, cy, r = x + size // 2, y + size // 2, size // 2 - 4
    cv.circle(cx, cy, r, color)
    cv.ellipse(cx, cy, r, r // 3, color)          # equator
    cv.ellipse(cx, cy, r // 3, r, color)          # meridian
    cv.ellipse(cx, cy, int(r * 0.85), r, color)   # outer meridian
    for frac, rr in ((-0.55, None), (0.55, None)):
        yy = int(cy + frac * r)
        half = int(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
        cv.hline(cx - half, yy, 2 * half, color)
    # Benghazi marker on the Mediterranean
    bx, by = cx + int(r * 0.45), cy - int(r * 0.18)
    cv.disc(bx, by, 5, RED)
    cv.circle(bx, by, 9, RED)
    cv.draw_text(bx - 24, by + 13, "Benghazi", 1, RED)


def story(cv, x, y, width, kicker, head, body):
    cv.draw_text(x, y, kicker, 2, RED)
    y += 18
    y = cv.draw_para(x, y, head, 3, INK, width, leading=24)
    y += 5
    cv.hline(x, y, 46, RED, 3)
    y += 8
    y = cv.draw_para(x, y, body, 2, INK, width, leading=16)
    return y


def draw_page():
    cv = Canvas(W, H, PAPER)
    # frame
    cv.rect(0, 0, W, 4, INK)
    cv.rect(0, H - 4, W, 4, INK)

    # ---- masthead
    y = 26
    cv.draw_text_centered(W // 2, y, "THE WORLD TODAY", 6, INK)
    y += 48
    cv.hline(M, y, CW, INK, 3)
    y += 6
    cv.hline(M, y, CW, INK, 1)
    y += 10
    cv.draw_text_centered(W // 2, y, "TUESDAY, 24 NOVEMBER 2026", 3, NAVY)
    y += 22
    cv.draw_text(M, y, "ONE DAY. THE WHOLE WORLD.", 2, GREY)
    right = "WORLD EDITION"
    cv.draw_text(W - M - text_width(right, 2), y, right, 2, GREY)
    y += 18
    cv.hline(M, y, CW, INK, 2)
    y += 12

    # ---- lead story
    lead_top = y
    cv.draw_text(M, y, "WAR AT SEA  --  LIBYA", 2, RED)
    y += 22
    cv.draw_text(M, y, "UKRAINE SINKS", 6, INK)
    y += 46
    cv.draw_text(M, y, "RUSSIAN WARSHIP", 6, INK)
    y += 46
    cv.draw_text(M, y, "OFF LIBYA", 6, INK)
    y += 46
    sub = ("Kyiv said on Monday that seven sea drones sank the corvette "
           "Merkury in Benghazi port, destroying a Ka-27 helicopter on "
           "board. The cargo ship MV Angara was also hit. Libyan officials "
           "said at least 10 crew were killed.")
    y = cv.draw_para(M, y, sub, 2, INK, 620, leading=16)
    lead_bottom = max(y + 8, lead_top + 230)
    # globe box on the right of the lead
    gx, gy = W - M - 300, lead_top - 4
    box_h = lead_bottom - gy
    cv.rect(gx, gy, 300, box_h, LIGHT)
    cv.rect(gx, gy, 300, 2, NAVY)
    cv.rect(gx, gy + box_h - 2, 300, 2, NAVY)
    draw_globe(cv, gx + 62, gy + 10, 168, NAVY)
    cv.draw_text_centered(gx + 150, gy + box_h - 36, "THE WAR REACHES", 2, NAVY)
    cv.draw_text_centered(gx + 150, gy + box_h - 20, "THE MEDITERRANEAN", 2, NAVY)
    y = lead_bottom + 12
    cv.hline(M, y, CW, INK, 2)
    y += 14

    # ---- three columns of stories, two rows
    col_w = (CW - 2 * 20) // 3
    xs = [M, M + col_w + 20, M + 2 * (col_w + 20)]
    stories = [
        ("TECH  --  NVIDIA", "HUANG IS BACK AT NVIDIA",
         "Nvidia's board voted unanimously on Monday to reinstate Jensen "
         "Huang as chief executive. Shares soared 31% to $165.05, "
         "adding about $952bn in value."),
        ("TECH  --  AI SAFETY", "STATES SUE MUSK OVER GROK IMAGES",
         "Virginia and Oregon sued Musk companies on Monday, saying "
         "Grok's 'spicy mode' let users turn photos into sexualised "
         "images, including of children. The suits seek damages."),
        ("WAR  --  UKRAINE", "AT LEAST 15 KILLED AROUND KYIV",
         "Russian strikes on the Kyiv region killed at least 15 people, "
         "officials said. A drone hit a block of flats in Dymer, "
         "killing 11; a supermarket strike in Vyshneve killed three."),
        ("JUSTICE  --  LONDON", "GTA VI HACKER JAILED, THEN FREED",
         "Arion Kurtaj, 21, got seven years at Woolwich Crown Court on "
         "Monday for the 2022 Rockstar hack. Time already served meant "
         "he walked free on licence the same day."),
        ("AMERICA  --  WASHINGTON", "TRUMP ORDERS EXECUTIONS SPED UP",
         "President Trump signed a directive on Monday to expedite "
         "federal executions. It also seeks the death penalty for child "
         "murder and for rapists and traffickers who kill."),
        ("DIPLOMACY  --  BARBADOS", "UN CHIEF SEEKS AI SAFETY PACT",
         "UN chief Antonio Guterres called on Monday, at an AI safety "
         "summit in Barbados, for states to agree within a year on a "
         "global framework to manage AI risks, with independent "
         "oversight."),
    ]
    row_y = y
    row1_end = 0
    for i in range(3):
        end = story(cv, xs[i], row_y, col_w, *stories[i])
        row1_end = max(row1_end, end)
    row_y = row1_end + 12
    row2_end = 0
    for i in range(3, 6):
        end = story(cv, xs[i - 3], row_y, col_w, *stories[i])
        row2_end = max(row2_end, end)
    y = row2_end + 6
    for vx in (xs[1] - 10, xs[2] - 10):
        cv.vline(vx, lead_bottom + 26, y - lead_bottom - 34, GREY)
    cv.hline(M, y, CW, INK, 2)
    y += 12

    # ---- in brief
    cv.draw_text(M, y, "IN BRIEF", 2, RED)
    y += 18
    briefs = [
        "INDIA-EU: Trade pact likely signed 16 Dec in Brussels; in force by mid-2027.",
        "THANKSGIVING: Storms on both US coasts threaten holiday travel for millions.",
        "INDONESIA: Prabowo names Amran Sulaiman and Sugiono as VP candidates.",
        "MARKETS: Nvidia gave back about 5% on Tuesday after Monday's 31% surge.",
    ]
    for b in briefs:
        y = cv.draw_para(M + 14, y, b, 2, INK, CW - 14, leading=16)
        y += 2
    y += 4
    cv.hline(M, y, CW, INK, 1)
    y += 10
    cv.draw_text_centered(
        W // 2, y,
        "THE WORLD TODAY  --  TUESDAY, 24 NOVEMBER 2026  --  STORIES AS REPORTED ON 24 NOVEMBER 2026",
        1, GREY)
    return cv


def resolve_output():
    if len(sys.argv) > 1:
        return sys.argv[1]
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        return os.path.join(out_dir, "entry.png")
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "entry.png")


def main():
    out = resolve_output()
    data = png_bytes(draw_page())
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "wb") as f:
        f.write(data)
    os.chmod(out, 0o644)
    with open(out, "rb") as f:
        back = f.read()
    print("wrote %s" % out)
    print("size %d bytes" % len(back))
    print("sha256 %s" % hashlib.sha256(back).hexdigest())


if __name__ == "__main__":
    main()
