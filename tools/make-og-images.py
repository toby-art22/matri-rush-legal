#!/usr/bin/env python3
"""Build the 1200x630 social preview image for each per-app page.

Every app page carries its own og:image so a link to /bottle-rush-shooting-3d/
previews as that game rather than as the Matri Rush home page. The cards are
drawn here rather than by hand so a new app is one dict entry away.

    python tools/make-og-images.py          # writes assets/og-<slug>.png

The card is the site's own "Toy Stage": a saturated wall, a hard horizon over a
darker floor, and the app icon standing on a pedestal disc. Requires Pillow.
"""

import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 630
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")

FONT_BLACK = r"C:\Windows\Fonts\seguibl.ttf"
FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"

# wall, floor, deep, accent — the same six colour worlds as app.css
APPS = [
    {
        "slug": "rush-delivery-3d",
        "name": "Rush Delivery 3D",
        "tag": "Clear the jam. Make the drop.",
        "status": "FREE ON THE APP STORE",
        "icon": "rush-icon.png",
        "colors": ("#ff6a16", "#e04d05", "#ae3a02", "#ffe07a"),
    },
    {
        "slug": "bottle-rush-shooting-3d",
        "name": "Bottle Rush Shooting 3D",
        "tag": "Line up the shot. Keep the chain alive.",
        "status": "FREE ON THE APP STORE",
        "icon": "bottle-icon.png",
        "colors": ("#5aa628", "#43871a", "#2f6410", "#ffd94a"),
    },
    {
        "slug": "animalculator",
        "name": "Animalculator",
        "tag": "Do a sum, get an animal.",
        "status": "FREE ON THE APP STORE",
        "icon": "animalculator-icon.png",
        "colors": ("#3b2415", "#2a1810", "#1b0f09", "#ffb44a"),
    },
    {
        "slug": "tictactalk",
        "name": "TicTacTalk",
        "tag": "Get it right, get the square.",
        "status": "IN DEVELOPMENT",
        "icon": "talk-icon.png",
        "colors": ("#12a5c8", "#0a7fa1", "#05627f", "#ffc53d"),
    },
    {
        "slug": "bawa",
        "name": "BAWA",
        "tag": "Find a hand, close by.",
        "status": "IN DEVELOPMENT",
        "icon": "bawa-icon.png",
        "colors": ("#12263f", "#0a1728", "#050e19", "#ecb000"),
        "tall_icon": True,   # the chilli is a cutout, not a rounded app tile
    },
]


def rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i + 2], 16) for i in (0, 2, 4))


def tracked_text(draw, xy, text, font, fill, tracking=4):
    """PIL has no letter-spacing, so the eyebrow is drawn a glyph at a time."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x


def wrap(draw, text, font, max_width):
    words, lines, line = text.split(), [], ""
    for word in words:
        probe = (line + " " + word).strip()
        if draw.textlength(probe, font=font) <= max_width or not line:
            line = probe
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def rounded_icon(path, size, radius_ratio=0.225, tall=False):
    img = Image.open(path).convert("RGBA")
    if tall:
        # keep the aspect ratio and leave the alpha alone: no tile, no mask
        ratio = size / img.height
        return img.resize((max(1, int(img.width * ratio)), size), Image.LANCZOS)
    img = img.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size * 4 - 1, size * 4 - 1), radius=int(size * 4 * radius_ratio), fill=255
    )
    mask = mask.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def build(app):
    wall, floor, deep, accent = (rgb(c) for c in app["colors"])
    card = Image.new("RGB", (W, H), wall)
    draw = ImageDraw.Draw(card)

    # the floor, and the hard horizon that defines the whole look
    floor_top = int(H * 0.70)
    draw.rectangle((0, floor_top, W, H), fill=floor)

    # a wide pool of light down the wall, so flat never reads flat
    glow = Image.new("L", (W // 6, H // 6), 0)
    ImageDraw.Draw(glow).ellipse(
        (-W // 12, -H // 8, W // 6 + W // 12, H // 8), fill=70
    )
    glow = glow.filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.BICUBIC)
    card.paste(Image.new("RGB", (W, H), (255, 255, 255)), (0, 0), glow)

    # ── the icon, standing on a pedestal disc ────────────────────────────
    tall = app.get("tall_icon", False)
    icon_size = 300 if not tall else 280
    icon = rounded_icon(os.path.join(ASSETS, app["icon"]), icon_size, tall=tall)
    ix = 830 - icon.width // 2
    iy = floor_top - icon.height + 40

    ped_w, ped_h = int(icon.width * 1.30), 74
    ped = Image.new("RGBA", (ped_w, ped_h + 16), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(ped)
    pdraw.ellipse((0, 16, ped_w - 1, ped_h + 15), fill=deep + (255,))
    pdraw.ellipse((0, 0, ped_w - 1, ped_h - 1), fill=wall + (255,))
    pdraw.ellipse((int(ped_w * .10), 6, int(ped_w * .90), int(ped_h * .45)),
                  fill=(255, 255, 255, 40))
    card.paste(ped, (830 - ped_w // 2, floor_top - 6), ped)

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 120), (ix + 10, iy + 26, ix + icon.width + 10, iy + icon.height + 26),
                 icon.split()[3])
    card.paste(Image.new("RGB", (W, H), (0, 0, 0)), (0, 0),
               shadow.filter(ImageFilter.GaussianBlur(22)).split()[3])
    card.paste(icon, (ix, iy), icon)

    # ── the type block ───────────────────────────────────────────────────
    f_eyebrow = ImageFont.truetype(FONT_BOLD, 24)
    f_tag = ImageFont.truetype(FONT_BOLD, 32)
    f_status = ImageFont.truetype(FONT_BOLD, 22)

    x = 78
    tracked_text(draw, (x, 92), "MATRIRUSH.COM", f_eyebrow, accent, tracking=5)

    # the title has to clear the icon, so it shrinks until it fits the column
    # both ways: at most two lines, and no line wider than the column itself
    col = 570
    size = 86
    while size > 44:
        f_title = ImageFont.truetype(FONT_BLACK, size)
        lines = wrap(draw, app["name"], f_title, col)
        widest = max(draw.textlength(ln, font=f_title) for ln in lines)
        if len(lines) <= 2 and widest <= col:
            break
        size -= 4
    y = 150
    for line in lines:
        draw.text((x, y), line, font=f_title, fill=(255, 255, 255))
        y += int(size * 1.06)

    y += 12
    for line in wrap(draw, app["tag"], f_tag, col):
        draw.text((x, y), line, font=f_tag, fill=(255, 255, 255, 235))
        y += 44

    # the status pill: never claim a store listing an app does not have
    pill_w = int(draw.textlength(app["status"], font=f_status) + 5 * len(app["status"]) + 52)
    pill_y = 470
    draw.rounded_rectangle((x, pill_y, x + pill_w, pill_y + 58), radius=29,
                           fill=accent if "FREE" in app["status"] else None,
                           outline=None if "FREE" in app["status"] else (255, 255, 255, 140),
                           width=3)
    ink = (40, 26, 2) if "FREE" in app["status"] else (255, 255, 255)
    tracked_text(draw, (x + 26, pill_y + 16), app["status"], f_status, ink, tracking=5)

    out = os.path.join(ASSETS, "og-%s.png" % app["slug"])
    card.save(out, "PNG", optimize=True)
    print("wrote %s (%d x %d)" % (out, W, H))


if __name__ == "__main__":
    for app in APPS:
        build(app)
