#!/usr/bin/env python3
"""Generate CEDAR-style icon pack PNGs with PIL.

Visual language:
  plate      #1A231D forest-dark, chamfered (45-deg-cut) corners
  primary    #7BA88A sage geometric glyphs
  secondary  #4E6B58 dim sage strokes

Rendered at 4x supersampling (768px) then downsampled to 192x192 LANCZOS.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res", "drawable-nodpi")
S = 4                 # supersample factor
W = 192               # final canvas
WS = W * S            # working canvas

PLATE = (26, 35, 29, 255)        # #1A231D
SAGE = (123, 168, 138, 255)      # #7BA88A
DIM = (78, 107, 88, 255)         # #4E6B58
HAIR = (78, 107, 88, 80)         # dim sage hairline

CHAMFER = 24                     # 45deg corner cut at 1x
C = CHAMFER * S


def octagon(m=0, c=None):
    """Points of a square with 45-degree cut corners (clockwise)."""
    c = C if c is None else c
    l, t, r, b = m * S, m * S, WS - m * S, WS - m * S
    return [(l + c, t), (r - c, t), (r, t + c), (r, b - c),
            (r - c, b), (l + c, b), (l, b - c), (l, t + c)]


def new_canvas():
    im = Image.new("RGBA", (WS, WS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon(octagon(), fill=PLATE)
    # subtle inner hairline following the chamfer
    d.line(octagon(m=8) + octagon(m=8)[:1], fill=HAIR, width=2 * S, joint="curve")
    return im, d


def sc(v):
    """scale a 1x coordinate/length"""
    return int(round(v * S))


def pts(*pairs):
    return [(sc(x), sc(y)) for x, y in pairs]


def line(d, pairs, fill=SAGE, w=10):
    d.line(pts(*pairs) + pts(*pairs)[-1:], fill=fill, width=sc(w), joint="curve")


def circle(d, cx, cy, r, fill=None, outline=None, w=9):
    b = [sc(cx - r), sc(cy - r), sc(cx + r), sc(cy + r)]
    if fill is not None:
        d.ellipse(b, fill=fill)
    if outline is not None:
        d.ellipse(b, outline=outline, width=sc(w))


def ring(d, cx, cy, r, w, fill=SAGE, start=0, end=360):
    d.arc([sc(cx - r), sc(cy - r), sc(cx + r), sc(cy + r)], start, end, fill=fill, width=sc(w))


def rrect(d, x0, y0, x1, y1, r=12, fill=None, outline=None, w=9):
    b = [sc(x0), sc(y0), sc(x1), sc(y1)]
    if fill is not None:
        d.rounded_rectangle(b, radius=sc(r), fill=fill)
    if outline is not None:
        d.rounded_rectangle(b, radius=sc(r), outline=outline, width=sc(w))


def poly(d, vertices, fill=None, outline=None, w=9):
    p = pts(*vertices)
    if fill is not None:
        d.polygon(p, fill=fill)
    if outline is not None:
        d.line(p + p[:1], fill=outline, width=sc(w), joint="curve")


def arc_cap(d, cx, cy, r, w, a0, a1, fill=SAGE):
    """Thick arc with round end caps."""
    ring(d, cx, cy, r, w, fill, a0, a1)
    for a in (a0, a1):
        rad = math.radians(a)
        circle(d, cx + r * math.cos(rad), cy + r * math.sin(rad), w / 2.0, fill=fill)


def rot(im, deg, cx=96, cy=96):
    """Rotate a 1x-coordinate overlay layer about the canvas centre."""
    return im.rotate(deg, resample=Image.BICUBIC, center=(sc(cx), sc(cy)))


# ---------------------------------------------------------------- glyphs

def phone(d, im):
    # classic handset: thick crescent band with round caps, rotated -45
    lay = Image.new("RGBA", (WS, WS), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    arc_cap(dl, 96, 96, 34, 22, 90, 270, SAGE)
    im.alpha_composite(rot(lay, -45))
    # signal ticks, dim sage
    line(d, [(118, 78), (130, 66)], DIM, 7)
    line(d, [(128, 92), (140, 80)], DIM, 7)


def messages(d, im):
    rrect(d, 54, 60, 138, 122, r=22, fill=SAGE)
    poly(d, [(70, 118), (70, 142), (94, 118)], fill=SAGE)
    for x in (76, 96, 116):
        circle(d, x, 91, 6, fill=DIM)


def chrome(d, im):
    ring(d, 96, 96, 42, 11)
    circle(d, 96, 96, 20, fill=SAGE)
    for a in (90, 210, 330):
        rad = math.radians(a)
        line(d, [(96 + 20 * math.cos(rad), 96 + 20 * math.sin(rad)),
                 (96 + 42 * math.cos(rad), 96 + 42 * math.sin(rad))], DIM, 7)


def camera(d, im):
    poly(d, [(78, 62), (114, 62), (122, 74), (134, 74), (134, 82), (58, 82), (58, 74), (70, 74)], fill=DIM)
    rrect(d, 54, 80, 138, 132, r=12, fill=SAGE)
    circle(d, 96, 106, 17, fill=PLATE)
    circle(d, 96, 106, 10, fill=SAGE)
    circle(d, 126, 92, 4, fill=DIM)


def clock(d, im):
    ring(d, 96, 96, 42, 10)
    line(d, [(96, 96), (96, 66)], SAGE, 8)
    line(d, [(96, 96), (118, 110)], DIM, 8)
    circle(d, 96, 96, 7, fill=SAGE)
    for a in (0, 90, 180, 270):
        rad = math.radians(a)
        circle(d, 96 + 42 * math.cos(rad), 96 + 42 * math.sin(rad), 2.5, fill=DIM)


def contacts(d, im):
    circle(d, 96, 82, 20, fill=SAGE)
    poly(d, [(62, 136), (66, 122), (78, 112), (96, 108), (114, 112), (126, 122), (130, 136)], fill=SAGE)
    line(d, [(134, 66), (134, 126)], DIM, 6)


def files(d, im):
    poly(d, [(56, 70), (92, 70), (100, 80), (136, 80), (136, 84), (56, 84)], fill=SAGE)
    rrect(d, 56, 84, 136, 130, r=6, fill=SAGE)
    line(d, [(56, 106), (136, 106)], DIM, 6)


def gmail(d, im):
    rrect(d, 52, 66, 140, 128, r=4, outline=SAGE, w=10)
    line(d, [(56, 70), (96, 102), (136, 70)], SAGE, 10)
    line(d, [(96, 102), (96, 124)], DIM, 7)


def google(d, im):
    ring(d, 96, 96, 40, 10, start=25, end=305)
    line(d, [(96, 92), (136, 92)], SAGE, 10)
    line(d, [(96, 100), (136, 100)], SAGE, 10)
    line(d, [(136, 92), (136, 100)], SAGE, 7)
    circle(d, 96, 96, 5, fill=SAGE)


def maps(d, im):
    line(d, [(50, 128), (86, 76)], DIM, 6)
    line(d, [(78, 136), (124, 72)], DIM, 6)
    line(d, [(122, 132), (146, 96)], DIM, 6)
    circle(d, 96, 88, 24, fill=SAGE)
    circle(d, 96, 88, 10, fill=PLATE)
    poly(d, [(78, 102), (114, 102), (96, 134)], fill=SAGE)


def photos(d, im):
    # 4-blade pinwheel
    for i, (a0, col) in enumerate([(270, SAGE), (0, DIM), (90, SAGE), (180, DIM)]):
        d.pieslice([sc(56), sc(56), sc(136), sc(136)], a0, a0 + 90, fill=col)
    circle(d, 96, 96, 18, fill=PLATE)
    circle(d, 96, 96, 9, fill=SAGE)


def settings(d, im):
    ring(d, 96, 96, 38, 13)
    for a in range(0, 360, 45):
        rad = math.radians(a)
        x, y = 96 + 44 * math.cos(rad), 96 + 44 * math.sin(rad)
        x2, y2 = 96 + 52 * math.cos(rad), 96 + 52 * math.sin(rad)
        line(d, [(x, y), (x2, y2)], SAGE, 12)
        circle(d, x2, y2, 6, fill=SAGE)
    circle(d, 96, 96, 14, fill=PLATE)
    ring(d, 96, 96, 20, 4, fill=DIM)


def youtube(d, im):
    rrect(d, 50, 66, 142, 126, r=20, fill=SAGE)
    poly(d, [(84, 82), (84, 110), (112, 96)], fill=PLATE)


def calendar(d, im):
    rrect(d, 56, 62, 136, 132, r=8, outline=SAGE, w=9)
    d.rectangle([sc(61), sc(67), sc(131), sc(85)], fill=SAGE)
    for row in (100, 116):
        for col in (76, 96, 116):
            circle(d, col, row, 5, fill=DIM)


def drive(d, im):
    poly(d, [(96, 56), (140, 130), (52, 130)], outline=SAGE, w=10)
    line(d, [(96, 56), (96, 130)], DIM, 6)
    line(d, [(74, 93), (118, 93)], DIM, 6)


def playstore(d, im):
    ring(d, 96, 96, 42, 8, fill=DIM)
    poly(d, [(80, 72), (80, 120), (122, 96)], fill=SAGE)


def calculator(d, im):
    rrect(d, 60, 54, 132, 138, r=10, outline=SAGE, w=9)
    rrect(d, 70, 64, 122, 86, r=6, fill=SAGE)
    for row in (102, 122):
        for col in (82, 110):
            rrect(d, col - 9, row - 7, col + 9, row + 7, r=4, fill=DIM)


def whatsapp(d, im):
    circle(d, 96, 94, 42, outline=SAGE, w=10)
    poly(d, [(64, 122), (58, 142), (84, 128)], fill=SAGE)
    lay = Image.new("RGBA", (WS, WS), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    arc_cap(dl, 96, 94, 20, 11, 100, 260, DIM)
    im.alpha_composite(lay)


def telegram(d, im):
    poly(d, [(58, 94), (136, 62), (120, 126), (96, 110), (86, 124), (84, 106)], fill=SAGE)
    line(d, [(96, 110), (136, 62)], DIM, 5)


def spotify(d, im):
    circle(d, 96, 96, 42, fill=SAGE)
    # three upward-bowing arcs peaking inside the disc (Spotify bars)
    for (y, half, R) in ((80, 35, 150), (96, 28, 120), (112, 20, 100)):
        lay = Image.new("RGBA", (WS, WS), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lay)
        dl.arc([sc(96 - R), sc(y), sc(96 + R), sc(y + 2 * R)], 270 - half, 270 + half,
               fill=PLATE, width=sc(10))
        im.alpha_composite(lay)


def gmail_alt(d, im):
    # open envelope
    poly(d, [(56, 78), (96, 50), (136, 78)], outline=SAGE, w=10)
    rrect(d, 54, 76, 138, 130, r=4, outline=SAGE, w=10)
    line(d, [(58, 80), (96, 110)], DIM, 6)
    line(d, [(134, 80), (96, 110)], DIM, 6)


def keep(d, im):
    circle(d, 96, 84, 26, fill=SAGE)
    d.rectangle([sc(84), sc(110), sc(108), sc(122)], fill=SAGE)
    line(d, [(84, 130), (108, 130)], DIM, 6)
    line(d, [(86, 140), (106, 140)], DIM, 5)


def translate(d, im):
    rrect(d, 48, 60, 112, 118, r=14, outline=SAGE, w=9)
    line(d, [(64, 78), (72, 96), (80, 78)], SAGE, 8)
    line(d, [(66, 90), (78, 90)], SAGE, 7)
    rrect(d, 100, 88, 148, 138, r=14, fill=DIM)
    line(d, [(112, 106), (120, 124), (128, 106)], SAGE, 7)
    line(d, [(126, 100), (126, 112)], DIM, 5)


def drive_alt(d, im):
    poly(d, [(96, 62), (138, 132), (54, 132)], outline=SAGE, w=10)
    line(d, [(72, 97), (120, 97)], SAGE, 9)
    circle(d, 96, 97, 6, fill=PLATE)


def wallet(d, im):
    rrect(d, 52, 64, 140, 128, r=14, outline=SAGE, w=10)
    rrect(d, 106, 84, 140, 108, r=8, fill=SAGE)
    circle(d, 124, 96, 5, fill=PLATE)
    line(d, [(62, 78), (100, 78)], DIM, 6)


def photos_alt(d, im):
    # aperture hexagon
    ring_pts = [(96 + 42 * math.cos(math.radians(a)), 96 + 42 * math.sin(math.radians(a)))
                for a in range(30, 390, 60)]
    poly(d, ring_pts, outline=SAGE, w=10)
    for (x, y) in ring_pts:
        line(d, [(96, 96), (x, y)], DIM, 6)
    circle(d, 96, 96, 12, fill=SAGE)


def ytmusic(d, im):
    ring(d, 96, 96, 42, 10)
    poly(d, [(82, 76), (82, 116), (118, 96)], fill=SAGE)


def podcasts(d, im):
    circle(d, 96, 116, 12, fill=SAGE)
    arc_cap(d, 96, 116, 30, 9, 180, 360, DIM)
    arc_cap(d, 96, 116, 50, 9, 180, 360, SAGE)


def home(d, im):
    poly(d, [(56, 96), (96, 58), (136, 96)], fill=SAGE)
    rrect(d, 66, 96, 126, 134, r=4, outline=SAGE, w=9)
    rrect(d, 88, 108, 104, 134, r=3, fill=DIM)


def recorder(d, im):
    rrect(d, 82, 56, 110, 116, r=14, fill=SAGE)
    arc_cap(d, 96, 104, 30, 8, 0, 180, SAGE)
    line(d, [(96, 134), (96, 146)], SAGE, 8)
    line(d, [(78, 148), (114, 148)], DIM, 7)


def pack_icon(d, im):
    # CEDAR mark: stylised evergreen over ground line
    poly(d, [(96, 52), (122, 88), (70, 88)], fill=SAGE)
    poly(d, [(96, 74), (130, 118), (62, 118)], fill=SAGE)
    d.rectangle([sc(90), sc(118), sc(102), sc(140)], fill=DIM)
    line(d, [(64, 142), (128, 142)], DIM, 8)


GLYPHS = {
    "ic_phone": phone,
    "ic_messages": messages,
    "ic_chrome": chrome,
    "ic_camera": camera,
    "ic_clock": clock,
    "ic_contacts": contacts,
    "ic_files": files,
    "ic_gmail": gmail,
    "ic_google": google,
    "ic_maps": maps,
    "ic_photos": photos,
    "ic_settings": settings,
    "ic_youtube": youtube,
    "ic_calendar": calendar,
    "ic_drive": drive,
    "ic_playstore": playstore,
    "ic_calculator": calculator,
    "ic_whatsapp": whatsapp,
    "ic_telegram": telegram,
    "ic_spotify": spotify,
    "ic_gmail_alt": gmail_alt,
    "ic_keep": keep,
    "ic_translate": translate,
    "ic_drive_alt": drive_alt,
    "ic_wallet": wallet,
    "ic_photos_alt": photos_alt,
    "ic_ytmusic": ytmusic,
    "ic_podcasts": podcasts,
    "ic_home": home,
    "ic_recorder": recorder,
    "ic_pack": pack_icon,
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in GLYPHS.items():
        im, d = new_canvas()
        fn(d, im)
        im = im.resize((W, W), Image.LANCZOS)
        im.save(os.path.join(OUT, name + ".png"))
        print("wrote", name + ".png")

    # contact sheet for visual review
    cols, cell, pad = 6, W + 8, 10
    rows = (len(GLYPHS) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell + 2 * pad, rows * cell + 2 * pad), (40, 44, 40, 255))
    for i, name in enumerate(GLYPHS):
        icon = Image.open(os.path.join(OUT, name + ".png"))
        x = pad + (i % cols) * cell
        y = pad + (i // cols) * cell
        sheet.alpha_composite(icon, (x + 4, y + 4))
    sheet.save(os.path.join(os.path.dirname(OUT), "..", "docs", "icon-contact-sheet.png"))
    print("contact sheet written")


if __name__ == "__main__":
    main()
