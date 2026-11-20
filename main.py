#!/usr/bin/env python3
"""Summarise Friday 20 November 2026's world news in a single image.

Draws a newspaper front page (1024x1024 PNG) covering the day's lead story,
six further stories and a ticker of briefs. The output is fully
deterministic: fixed fonts, fixed layout, no network, no clock, no random
input, so running the program twice produces byte-identical PNG files.

Usage:
    python3 main.py            # writes /output/entry.png
"""

import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants

WIDTH, HEIGHT = 1024, 1024
OUT_PATH = "/output/entry.png"

PAPER = (247, 243, 234)      # warm newsprint
INK = (18, 18, 18)           # near-black text
RED = (178, 34, 34)          # kicker / accent red
NAVY = (28, 58, 96)          # cyclone art + ticker band
GREY = (96, 92, 84)          # secondary text
RULE = (18, 18, 18)
CARD_BG = (255, 255, 255)

MARGIN = 36

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load_font(name, size):
    """Load a DejaVu font, falling back to Pillow's built-in bitmap font."""
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


MASTHEAD_FONT = load_font("DejaVuSerif-Bold.ttf", 80)
DATE_FONT = load_font("DejaVuSans-Bold.ttf", 21)
KICKER_FONT = load_font("DejaVuSans-Bold.ttf", 19)
HEADLINE_FONT = load_font("DejaVuSerif-Bold.ttf", 46)
DECK_FONT = load_font("DejaVuSerif.ttf", 23)
CARD_KICKER_FONT = load_font("DejaVuSans-Bold.ttf", 16)
CARD_HEAD_FONT = load_font("DejaVuSerif-Bold.ttf", 23)
TICKER_FONT = load_font("DejaVuSans-Bold.ttf", 18)
FOOTER_FONT = load_font("DejaVuSans.ttf", 16)
CAPTION_FONT = load_font("DejaVuSans.ttf", 15)


# ------------------------------------------------------------------- helpers

def wrap(draw, text, font, max_width):
    """Greedy word-wrap of `text` so every line fits within `max_width`."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        current = ""
        for word in words:
            trial = (current + " " + word).strip()
            if draw.textlength(trial, font=font) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def draw_lines(draw, lines, font, x, y, fill, leading):
    """Draw wrapped lines top-down, returning the y below the last line."""
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def rule(draw, x0, y, x1, width=2, fill=RULE):
    """A horizontal rule from x0 to x1 at height y."""
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def cyclone(draw, cx, cy, radius, colour):
    """A simple spiral storm: a few spaced arcs that tighten to the eye."""
    steps = 14
    for i in range(steps):
        t = i / steps
        r = radius * (1.0 - t * 0.75)
        start = 90 + 260 * t
        end = start + 200
        box = [cx - r, cy - r, cx + r, cy + r]
        draw.arc(box, start=start, end=end, fill=colour, width=3)
    draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], outline=colour, width=3)


# --------------------------------------------------------------------- data

MASTHEAD = "WORLD NEWS"
DATELINE = "FRIDAY 20 NOVEMBER 2026"

LEAD_KICKER = "LEAD STORY  —  INDIA"
LEAD_HEADLINE = "Cyclone Akvan slams into\nIndia's east coast"
LEAD_DECK = (
    "More than 300,000 people were evacuated near Gopalpur as winds "
    "gusted to 110 km/h and the storm made landfall. 69 trains were "
    "cancelled across the region."
)
LEAD_CAPTION = "GOPALPUR, ODISHA"

CARDS = [
    ("WASHINGTON",
     "Trump defers the Iran decision to next year"),
    ("THE HAGUE",
     "ICJ rules Myanmar committed genocide against the Rohingya"),
    ("WALL STREET",
     "Anthropic soars 17% in record IPO as S&P 500 falls 2%"),
    ("ANTALYA",
     "COP31 ends with no fossil-fuel pledge"),
    ("EUROPE",
     "Europe ready for Russia talks"),
    ("MIDDLE EAST",
     "Houthi missile hits Riyadh's tallest tower; tanker mine fire off Hormuz"),
]

TICKER_ITEMS = [
    "Crimean Bridge hit a third time",
    "Kyiv hit by four ballistic missiles",
    "Migrant boat sinks off Senegal",
    "Van Gogh sells for a record $190.4m",
    "GTA VI rollout continues",
]

FOOTER = "WORLD NEWS  •  FRIDAY 20 NOVEMBER 2026  •  THE WHOLE DAY IN ONE IMAGE"


# -------------------------------------------------------------------- render

def render():
    img = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(img)
    right = WIDTH - MARGIN

    # --- masthead ------------------------------------------------------
    y = 24
    rule(draw, MARGIN, y, right, width=2)
    y += 10
    title_w = draw.textlength(MASTHEAD, font=MASTHEAD_FONT)
    draw.text(((WIDTH - title_w) / 2, y), MASTHEAD, font=MASTHEAD_FONT, fill=INK)
    y += 96
    date_w = draw.textlength(DATELINE, font=DATE_FONT)
    draw.text(((WIDTH - date_w) / 2, y), DATELINE, font=DATE_FONT, fill=RED)
    y += 30
    rule(draw, MARGIN, y, right, width=6)
    y += 8
    rule(draw, MARGIN, y, right, width=2)

    # --- lead story ----------------------------------------------------
    y += 14
    draw.text((MARGIN, y), LEAD_KICKER, font=KICKER_FONT, fill=RED)
    y += 26
    head_lines = wrap(draw, LEAD_HEADLINE, HEADLINE_FONT, WIDTH - 2 * MARGIN)
    y = draw_lines(draw, head_lines, HEADLINE_FONT, MARGIN, y, INK, 50)

    # Deck on the left, cyclone artwork on the right.
    y += 12
    art_w = 250
    art_x0 = right - art_w
    deck_w = art_x0 - MARGIN - 24
    deck_lines = wrap(draw, LEAD_DECK, DECK_FONT, deck_w)
    draw_lines(draw, deck_lines, DECK_FONT, MARGIN, y, INK, 30)

    art_y0 = y - 6
    art_y1 = art_y0 + 170
    draw.rectangle([art_x0, art_y0, right, art_y1], outline=NAVY, width=2)
    cyclone(draw, art_x0 + art_w // 2, art_y0 + 76, 66, NAVY)
    cap_w = draw.textlength(LEAD_CAPTION, font=CAPTION_FONT)
    draw.text((art_x0 + (art_w - cap_w) / 2, art_y1 - 26),
              LEAD_CAPTION, font=CAPTION_FONT, fill=NAVY)

    lead_bottom = max(y + len(deck_lines) * 30, art_y1) + 14
    rule(draw, MARGIN, lead_bottom, right, width=2)

    # --- six story cards, two columns x three rows ---------------------
    gap = 14
    card_w = (WIDTH - 2 * MARGIN - gap) // 2
    card_h = 116
    top = lead_bottom + 14
    for index, (kicker, headline) in enumerate(CARDS):
        col = index % 2
        row = index // 2
        x0 = MARGIN + col * (card_w + gap)
        y0 = top + row * (card_h + gap)
        draw.rectangle([x0, y0, x0 + card_w, y0 + card_h],
                       fill=CARD_BG, outline=(200, 194, 182), width=1)
        draw.text((x0 + 14, y0 + 10), kicker, font=CARD_KICKER_FONT, fill=RED)
        head = wrap(draw, headline, CARD_HEAD_FONT, card_w - 28)
        draw_lines(draw, head[:3], CARD_HEAD_FONT, x0 + 14, y0 + 32, INK, 28)

    cards_bottom = top + 3 * card_h + 2 * gap

    # --- ticker ---------------------------------------------------------
    # Two centred lines: the five briefs are too long for one line.
    tick_y0 = cards_bottom + 14
    tick_y1 = tick_y0 + 66
    draw.rectangle([MARGIN, tick_y0, right, tick_y1], fill=NAVY)
    tick_lines = ["  •  ".join(TICKER_ITEMS[:3]),
                  "  •  ".join(TICKER_ITEMS[3:])]
    tick_font = TICKER_FONT
    for size in range(17, 12, -1):
        tick_font = load_font("DejaVuSans-Bold.ttf", size)
        widths = [draw.textlength(t, font=tick_font) for t in tick_lines]
        if max(widths) <= right - MARGIN - 16:
            break
    line_y = tick_y0 + 10
    for line in tick_lines:
        line_w = draw.textlength(line, font=tick_font)
        draw.text(((WIDTH - line_w) / 2, line_y),
                  line, font=tick_font, fill=(255, 255, 255))
        line_y += 26

    # --- footer ---------------------------------------------------------
    foot_y = tick_y1 + 14
    rule(draw, MARGIN, foot_y, right, width=2)
    foot_w = draw.textlength(FOOTER, font=FOOTER_FONT)
    draw.text(((WIDTH - foot_w) / 2, foot_y + 10),
              FOOTER, font=FOOTER_FONT, fill=GREY)

    return img


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    image = render()
    image.save(OUT_PATH, format="PNG")
    print(f"Wrote {OUT_PATH} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
