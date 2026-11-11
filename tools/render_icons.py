#!/usr/bin/env python3
"""Render CEDAR icon plates from SVG sources.

Sources are declared in icons.json:
  {"arcticons": "google_phone"}  -> glyph from the Arcticons checkout (GPL-3.0)
  {"custom": "cedar.svg"}        -> glyph hand-drawn in custom/

Each tile is built the same way the original CEDAR pack was:
  plate    #1A231D, 45-degree chamfered corners, dim-sage hairline inset 8px
  glyph    Arcticons 48x48 line art recoloured to sage #7BA88A, stroke 1.25,
           scaled into a 108/192 glyph box, rendered at 4x then LANCZOS-downsampled.

Usage:
  python3 tools/render_icons.py                 # render all + contact sheet
  python3 tools/render_icons.py --sheet-only    # rebuild the contact sheet
"""
import argparse
import json
import os
import re
import subprocess
import sys
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCTICONS = os.environ.get("ARCTICONS_SRC", os.path.expanduser("~/Projects/arcticons-source/icons/black"))
OUT = os.path.join(ROOT, "res", "drawable-nodpi")
DOCS = os.path.join(ROOT, "docs")

PLATE = (26, 35, 29, 255)      # #1A231D
SAGE = (123, 168, 138, 255)    # #7BA88A
HAIR = (78, 107, 88, 80)       # #4E6B58 @ 31%
SAGE_HEX = "#7BA88A"
CHAMFER = 24                   # at 1x


def plate(canvas=192, ss=4):
    """Chamfered forest plate with hairline, at supersampled size."""
    ws = canvas * ss
    c = CHAMFER * ss
    im = Image.new("RGBA", (ws, ws), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    m = 0
    l, t, r, b = m, m, ws, ws
    d.polygon([(l + c, t), (r - c, t), (r, t + c), (r, b - c),
               (r - c, b), (l + c, b), (l, b - c), (l, t + c)], fill=PLATE)
    hc, hm = c, 8 * ss                  # same 45-degree cut, inset 8px
    l2, t2, r2, b2 = hm, hm, ws - hm, ws - hm
    pts = [(l2 + hc, t2), (r2 - hc, t2), (r2, t2 + hc), (r2, b2 - hc),
           (r2 - hc, b2), (l2 + hc, b2), (l2, b2 - hc), (l2, t2 + hc)]
    d.line(pts + pts[:1], fill=HAIR, width=2 * ss, joint="curve")
    return im


def recolour(svg_text, stroke_width):
    """Swap Arcticons black for CEDAR sage and normalise the stroke weight.

    Arcticons ships <style>.x{fill:none;stroke:#000;...}</style> with default
    stroke-width 1. Injecting stroke-width in the class rule lets us thicken
    every stroke of the drawing at once (presentation attributes lose to CSS).
    """
    svg_text = svg_text.replace("#000", SAGE_HEX)

    def fix(rule):
        body = rule.group(0)
        if "stroke:" in body:
            body = re.sub(r"stroke-width:[0-9.]+;?", "", body)
            body = body.replace("}", "stroke-width:%s;}" % stroke_width)
        return body

    return re.sub(r"\.[A-Za-z0-9_-]+\{[^}]*\}", fix, svg_text)


def render_glyph(svg_text, box_px):
    tmp_svg = "/tmp/cedar-icon-glyph.svg"
    tmp_png = "/tmp/cedar-icon-glyph.png"
    with open(tmp_svg, "w", encoding="utf-8") as fh:
        fh.write(svg_text)
    subprocess.run(
        ["rsvg-convert", "-w", str(box_px), "-h", str(box_px), "-o", tmp_png, tmp_svg],
        check=True, capture_output=True,
    )
    return Image.open(tmp_png).convert("RGBA")


def build_tile(svg_text, cfg):
    canvas, ss, box = cfg["canvas"], cfg["supersample"], cfg["glyph_box"]
    tile = plate(canvas, ss)
    glyph = render_glyph(recolour(svg_text, cfg["stroke_width"]), box * ss)
    tile.alpha_composite(glyph, ((canvas - box) * ss // 2, (canvas - box) * ss // 2))
    return tile.resize((canvas, canvas), Image.Resampling.LANCZOS)


def font(size):
    for path in ("/usr/share/fonts/TTF/DejaVuSans.ttf",
                 "/usr/share/fonts/dejavu/DejaVuSans.ttf",
                 "/usr/share/fonts/liberation/LiberationSans-Regular.ttf"):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def contact_sheet(icons, size=144, cols=6):
    """Labeled sheet of every rendered icon, for visual review."""
    pad_x, pad_y, label_h = 18, 18, 22
    cw, ch = size + pad_x * 2, size + label_h + pad_y * 2
    rows = (len(icons) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cw, rows * ch), (10, 14, 12, 255))
    d = ImageDraw.Draw(sheet)
    f = font(13)
    for i, icon in enumerate(icons):
        path = os.path.join(OUT, icon["drawable"] + ".png")
        if not os.path.exists(path):
            continue
        im = Image.open(path).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
        x, y = (i % cols) * cw + pad_x, (i // cols) * ch + pad_y
        sheet.alpha_composite(im, (x, y))
        d.text((x, y + size + 4), icon["label"], fill=(175, 189, 178, 255), font=f)
    out = os.path.join(DOCS, "contact-sheet-v2.png")
    sheet.convert("RGB").save(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet-only", action="store_true")
    args = ap.parse_args()

    with open(os.path.join(ROOT, "icons.json"), encoding="utf-8") as fh:
        spec = json.load(fh)
    cfg = spec["render"]
    icons = spec["icons"]
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(DOCS, exist_ok=True)

    if args.sheet_only:
        print("contact sheet:", contact_sheet(icons))
        return

    missing = []
    for icon in icons:
        src = None
        if "arcticons" in icon:
            src = os.path.join(ARCTICONS, icon["arcticons"] + ".svg")
        elif "custom" in icon:
            src = os.path.join(ROOT, "custom", icon["custom"])
        if not src or not os.path.exists(src):
            missing.append("%s <- %s" % (icon["drawable"], src))
            continue
        with open(src, encoding="utf-8") as fh:
            text = fh.read()
        tile = build_tile(text, cfg)
        tile.save(os.path.join(OUT, icon["drawable"] + ".png"), optimize=True)
        if icon.get("pack_icon"):
            tile.save(os.path.join(OUT, "ic_pack.png"), optimize=True)

    if missing:
        print("ERROR: missing sources:\n  " + "\n  ".join(missing), file=sys.stderr)
        sys.exit(1)

    rendered = [i for i in icons if os.path.exists(os.path.join(OUT, i["drawable"] + ".png"))]
    total = sum(os.path.getsize(os.path.join(OUT, i["drawable"] + ".png")) for i in rendered)
    print("rendered %d icons, %.1f KB total" % (len(rendered), total / 1024))
    print("contact sheet:", contact_sheet(icons))


if __name__ == "__main__":
    main()
