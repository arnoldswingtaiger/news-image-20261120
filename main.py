#!/usr/bin/env python3
"""news-image-20261120: draw one image summing up the world news of
Friday 20 November 2026, and write it to /output/entry.png.

Pure Python 3 standard library (zlib, struct, os, math): the grader runs
with no network and nothing installed, so the PNG encoder and a 5x7 bitmap
font are built in here. Deterministic: no clock, no randomness, no input
files -- two runs write the same bytes.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# --- palette ---------------------------------------------------------------
PAPER = (250, 247, 239)   # warm newsprint
INK = (20, 24, 32)        # near-black text
NAVY = (14, 30, 58)       # masthead band
RED = (172, 32, 32)       # rules, lead tag
GOLD = (198, 160, 38)     # date line, accents
CARD = (255, 255, 255)    # story cards
GREY = (102, 108, 116)    # footer, captions
LINE = (203, 196, 182)    # hairlines
STORM = (96, 122, 148)    # cyclone sky
TEAL = (13, 112, 106)     # tag: justice / society
BLUE = (28, 88, 164)      # tag: diplomacy
PURPLE = (100, 62, 146)   # tag: markets / tech
GREEN = (44, 122, 48)     # tag: politics
ORANGE = (192, 92, 18)    # tag: weather
BROWN = (118, 80, 40)     # tag: climate
DARKRED = (140, 28, 28)   # tag: conflict

# --- canvas ----------------------------------------------------------------
px = bytearray(W * H * 3)


def fill(color):
    px[:] = bytes(color) * (W * H)


def rect(x, y, w, h, color):
    """Filled rectangle, clipped to the canvas."""
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(color) * (x1 - x0)
    for yy in range(y0, y1):
        o = (yy * W + x0) * 3
        px[o:o + len(row)] = row


def circle(cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = int(math.sqrt(max(0, r * r - dy * dy)))
        rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)


def ring(cx, cy, r, color, thick=3):
    """Circle outline of the given thickness."""
    for dy in range(-r - thick, r + thick + 1):
        for dx in range(-r - thick, r + thick + 1):
            d = math.sqrt(dx * dx + dy * dy)
            if r - thick / 2 <= d <= r + thick / 2:
                rect(cx + dx, cy + dy, 1, 1, color)


def tri(x1, y1, x2, y2, x3, y3, color):
    """Filled triangle, scanline fill."""
    pts = sorted(((x1, y1), (x2, y2), (x3, y3)), key=lambda p: p[1])
    (ax, ay), (bx, by), (cx, cy) = pts
    if ay == cy:
        return
    for y in range(max(0, ay), min(H, cy + 1)):
        xs = []
        for (px1, py1), (px2, py2) in (((ax, ay), (bx, by)),
                                       ((bx, by), (cx, cy)),
                                       ((ax, ay), (cx, cy))):
            if py2 != py1 and py1 <= y <= py2:
                xs.append(px1 + (px2 - px1) * (y - py1) / (py2 - py1))
            elif py2 != py1 and py2 <= y <= py1:
                xs.append(px2 + (px1 - px2) * (y - py2) / (py1 - py2))
        if len(xs) >= 2:
            xa, xb = int(min(xs)), int(max(xs))
            rect(xa, y, xb - xa + 1, 1, color)


def line(x1, y1, x2, y2, color, thick=1):
    n = max(abs(x2 - x1), abs(y2 - y1), 1)
    for i in range(n + 1):
        x = int(x1 + (x2 - x1) * i / n)
        y = int(y1 + (y2 - y1) * i / n)
        rect(x - thick // 2, y - thick // 2, thick, thick, color)


# --- PNG encoder (stdlib only) ---------------------------------------------
def _chunk(typ, data):
    return (struct.pack(">I", len(data)) + typ + data +
            struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))


def encode_png():
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += px[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
            _chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + _chunk(b"IEND", b""))


# --- 5x7 bitmap font -------------------------------------------------------
# Each glyph is 7 rows of 5 pixels ('#' on, '.' off).
FONT_UPPER = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
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
}
FONT_DIGITS = {
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#...#", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "#...#", ".###."),
}
FONT_LOWER = {
    'a': (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".###.", "#...#", "#....", "#...#", ".###."),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    'g': (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
    'j': (".....", "...#.", ".....", "..##.", "...#.", "...#.", "##.#."),
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
}
FONT_PUNCT = {
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '(': ("...#.", "..#..", "..#..", "..#..", "..#..", "..#..", "...#."),
    ')': (".#...", "..#..", "..#..", "..#..", "..#..", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '&': (".##..", "#..#.", "#..#.", ".#...", "#.##.", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.##.", "#....", ".###."),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '<': ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    '>': (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '[': (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    ']': (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    '·': (".....", ".....", ".....", ".##..", ".##..", ".....", "....."),
    '•': (".....", ".....", ".....", ".##..", ".##..", ".....", "....."),
    '–': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '—': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
}
FONT = {}
FONT.update(FONT_UPPER)
FONT.update(FONT_DIGITS)
FONT.update(FONT_LOWER)
FONT.update(FONT_PUNCT)
BLANK = FONT[' ']


# --- text ------------------------------------------------------------------
def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, fg, bg):
    """Draw string s at (x, y), top-left, on a solid bg colour."""
    fgc = bytes(fg)
    bgc = bytes(bg)
    cx = x
    for ch in s:
        g = FONT.get(ch, BLANK)
        for row in range(7):
            bits = g[row]
            seg = bytearray()
            for col in range(5):
                seg += fgc * scale if bits[col] == '#' else bgc * scale
            seg += bgc * scale  # one column of letter spacing
            for sy in range(scale):
                yy = y + row * scale + sy
                if 0 <= yy < H:
                    o = (yy * W + cx) * 3
                    px[o:o + len(seg)] = seg
        cx += 6 * scale


def wrap(s, scale, max_w):
    """Greedy word wrap; returns a list of lines."""
    words = s.split(' ')
    lines, cur = [], ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, s, scale, fg, bg, max_w, leading=None):
    """Draw a wrapped paragraph; returns the y just below it."""
    lh = leading if leading is not None else 7 * scale + 4
    for ln in wrap(s, scale, max_w):
        draw_text(x, y, ln, scale, fg, bg)
        y += lh
    return y


def center_text(y, s, scale, fg, bg, cx=W // 2):
    draw_text(cx - text_w(s, scale) // 2, y, s, scale, fg, bg)


# --- icons (each draws inside a 56x56 box at x, y) --------------------------
def icon_scales(x, y):
    """Justice: a pair of scales."""
    rect(x + 27, y + 6, 2, 34, INK)               # post
    rect(x + 10, y + 6, 36, 3, INK)               # beam
    tri(x + 10, y + 9, x + 24, y + 9, x + 17, y + 22, INK)   # left pan hanger
    tri(x + 32, y + 9, x + 46, y + 9, x + 39, y + 22, INK)   # right pan hanger
    rect(x + 8, y + 22, 18, 3, TEAL)              # left pan
    rect(x + 30, y + 22, 18, 3, TEAL)             # right pan
    rect(x + 22, y + 40, 12, 3, INK)              # base
    rect(x + 16, y + 43, 24, 4, INK)


def icon_chart(x, y):
    """Markets: rising bars and an arrow."""
    rect(x + 8, y + 34, 7, 16, PURPLE)
    rect(x + 19, y + 26, 7, 24, PURPLE)
    rect(x + 30, y + 18, 7, 32, PURPLE)
    rect(x + 41, y + 10, 7, 40, GREEN)
    line(x + 6, y + 8, x + 50, y + 2, GREEN, 2)
    tri(x + 50, y + 2, x + 42, y + 0, x + 44, y + 9, GREEN)


def icon_tower(x, y):
    """Conflict: a tower struck by a missile trail."""
    rect(x + 22, y + 8, 12, 40, (90, 96, 106))    # tower
    rect(x + 18, y + 14, 20, 4, (70, 76, 86))
    rect(x + 18, y + 24, 20, 4, (70, 76, 86))
    rect(x + 18, y + 34, 20, 4, (70, 76, 86))
    rect(x + 26, y + 2, 4, 6, (70, 76, 86))       # spire
    circle(x + 28, y + 6, 3, GOLD)                # impact flash
    line(x + 44, y + 4, x + 30, y + 8, DARKRED, 2)  # missile trail
    line(x + 48, y + 12, x + 34, y + 12, DARKRED, 2)
    rect(x + 6, y + 48, 44, 4, (70, 76, 86))      # ground


def icon_leaf(x, y):
    """Climate: a leaf over a globe."""
    circle(x + 28, y + 30, 18, (64, 120, 200))    # globe
    circle(x + 24, y + 26, 6, GREEN)              # land
    circle(x + 34, y + 34, 5, GREEN)
    rect(x + 20, y + 30, 16, 3, (64, 120, 200))
    # leaf
    tri(x + 28, y + 2, x + 44, y + 12, x + 28, y + 18, GREEN)
    tri(x + 28, y + 2, x + 12, y + 12, x + 28, y + 18, (60, 140, 60))
    line(x + 28, y + 4, x + 28, y + 18, (30, 90, 30), 1)


def icon_stars(x, y):
    """Diplomacy: a ring of stars on blue."""
    rect(x + 4, y + 4, 48, 48, (0, 51, 153))
    for k in range(12):
        a = math.radians(k * 30)
        dx = 28 + int(15 * math.cos(a))
        dy = 28 + int(15 * math.sin(a))
        rect(x + dx - 1, y + dy - 1, 3, 3, GOLD)


def icon_hourglass(x, y):
    """Politics: an hourglass — a decision put off."""
    tri(x + 10, y + 6, x + 46, y + 6, x + 28, y + 24, INK)
    tri(x + 10, y + 50, x + 46, y + 50, x + 28, y + 26, INK)
    rect(x + 8, y + 4, 40, 3, INK)
    rect(x + 8, y + 49, 40, 3, INK)
    circle(x + 28, y + 20, 4, GOLD)
    circle(x + 28, y + 34, 2, GOLD)


def draw_lead_art(x, y, w, h):
    """Cyclone Akvan over India's east coast: spiral bands, the eye,
    a coastline with waves below, rain streaks."""
    rect(x, y, w, h, STORM)
    # spiral cloud bands around the eye
    ex, ey = x + w // 2, y + 88
    for r, col in ((78, (226, 232, 238)), (62, (200, 210, 220)),
                   (46, (226, 232, 238)), (30, (200, 210, 220))):
        ring(ex, ey, r, col, 9)
    circle(ex, ey, 14, (240, 244, 248))           # the calm eye
    # spiral arms sweeping out
    for k in range(8):
        a = math.radians(k * 45 + 20)
        ax = ex + int(84 * math.cos(a))
        ay = ey + int(84 * math.sin(a))
        circle(ax, ay, 10, (226, 232, 238))
    # coastline: land bottom-right, sea bottom-left
    for dx in range(0, w):
        edge = y + h - 46 - int(26 * math.sin(dx / 34.0))
        rect(x + dx, edge, 1, y + h - edge, (46, 92, 58))
    # beach line
    for dx in range(0, w, 4):
        edge = y + h - 46 - int(26 * math.sin(dx / 34.0))
        rect(x + dx, edge - 3, 4, 3, (214, 196, 150))
    # waves in the sea
    for wy in (y + h - 34, y + h - 22, y + h - 12):
        for wx in range(0, 150, 24):
            line(x + wx, wy, x + wx + 12, wy - 4, CARD, 2)
    # rain streaks
    for rx in range(8, w, 26):
        line(x + rx, y + 8, x + rx - 6, y + 30, (180, 196, 210), 2)
    # town dots on the coast
    for tx, ty in ((210, y + h - 58), (238, y + h - 66), (262, y + h - 52)):
        rect(tx, ty, 4, 4, GOLD)


# --- the day's news (Friday 20 November 2026) -------------------------------
LEAD = {
    "tag": "INDIA · WEATHER",
    "color": ORANGE,
    "headline": "CYCLONE AKVAN SLAMS INTO INDIA",
    "body": ("More than 300,000 people evacuated as the severe storm crosses "
             "the Odisha-Andhra Pradesh coast near Gopalpur, with winds "
             "gusting to 110 km/h and 69 trains cancelled."),
}
CARDS = [
    {"tag": "UNITED STATES · IRAN", "color": GREEN, "icon": icon_hourglass,
     "headline": "TRUMP DEFERS IRAN DECISION",
     "body": ("The president says he is 'not rushing' new strikes and will "
              "decide after 1 January, as Iran widens attacks on Gulf shipping.")},
    {"tag": "JUSTICE · THE HAGUE", "color": TEAL, "icon": icon_scales,
     "headline": "MYANMAR GUILTY OF GENOCIDE",
     "body": ("The UN court rules Myanmar committed genocide against the "
              "Rohingya in 2017, its first such finding against a state.")},
    {"tag": "MARKETS · TECHNOLOGY", "color": PURPLE, "icon": icon_chart,
     "headline": "ANTHROPIC SOARS IN RECORD IPO",
     "body": ("The AI firm's shares jump 17% on their first day in the "
              "biggest listing on record, even as the S&P 500 falls 2%.")},
    {"tag": "MIDDLE EAST · CONFLICT", "color": DARKRED, "icon": icon_tower,
     "headline": "MISSILE HITS RIYADH TOWER",
     "body": ("A Houthi missile strikes Riyadh's tallest tower, and a tanker "
              "catches fire after hitting a mine east of the Strait of Hormuz.")},
    {"tag": "CLIMATE · ANTALYA", "color": BROWN, "icon": icon_leaf,
     "headline": "COP31 ENDS, NO FUEL PLEDGE",
     "body": ("The UN climate talks close with a 144-paragraph draft and the "
              "fossil-fuel reference dropped from the final text.")},
    {"tag": "EUROPE · UKRAINE", "color": BLUE, "icon": icon_stars,
     "headline": "EUROPE READY FOR RUSSIA TALKS",
     "body": ("Ukraine's European allies meet in Berlin and say they hold a "
              "united position for negotiations; Putin invites them to Moscow.")},
]
TICKER = ("ALSO TODAY: Ukraine hits the Crimean Bridge a third time in "
          "four days • Kyiv hit by four ballistic missiles • Migrant boat "
          "sinks off Senegal • Van Gogh sells for a record $190.4m • "
          "GTA VI rollout continues")
FOOTER = ("Compiled from public news reports · All events of Friday, "
          "20 November 2026")


def draw_card(x, y, w, h, card):
    rect(x, y, w, h, LINE)
    rect(x + 2, y + 2, w - 4, h - 4, CARD)
    draw_text(x + 14, y + 12, card["tag"], 2, card["color"], CARD)
    card["icon"](x + w - 68, y + 12)
    draw_para(x + 14, y + 32, card["headline"], 3, INK, CARD, w - 28 - 70)
    draw_para(x + 14, y + 96, card["body"], 2, INK, CARD, w - 28)


def draw_page():
    fill(PAPER)
    # masthead
    rect(0, 0, W, 126, NAVY)
    rect(0, 122, W, 4, GOLD)
    center_text(14, "WORLD NEWS", 7, (255, 255, 255), NAVY)
    center_text(72, "FRIDAY · 20 NOVEMBER 2026", 4, GOLD, NAVY)
    rect(0, 126, W, 6, RED)
    # lead story
    draw_text(28, 146, LEAD["tag"], 2, LEAD["color"], PAPER)
    draw_para(28, 168, LEAD["headline"], 4, INK, PAPER, 652)
    draw_para(28, 246, LEAD["body"], 3, INK, PAPER, 652)
    draw_lead_art(700, 142, 296, 230)
    # divider
    rect(28, 384, 968, 2, LINE)
    # story cards: 2 columns x 3 rows
    cw, ch, gx, gy = 472, 170, 16, 12
    for i, card in enumerate(CARDS):
        cx = 28 + (i % 2) * (cw + gx)
        cy = 398 + (i // 2) * (ch + gy)
        draw_card(cx, cy, cw, ch, card)
    # ticker + footer
    draw_para(28, 944, TICKER, 2, INK, PAPER, 968)
    center_text(1004, FOOTER, 2, GREY, PAPER)


def main():
    draw_page()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(encode_png())


if __name__ == "__main__":
    main()
