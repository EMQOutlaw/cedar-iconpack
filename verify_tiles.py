#!/usr/bin/env python3
"""Final verification: tile-level before/after comparison + composite evidence images."""
from PIL import Image
import os

SAGE = (123, 168, 138)
def close(p, c, tol=32):
    return all(abs(p[i] - c[i]) <= tol for i in range(3))

before = Image.open("docs/drawer-before.png").convert("RGB")
after = Image.open("docs/drawer-after.png").convert("RGB")
cols = {1: 134, 2: 337, 3: 540, 4: 743, 5: 946}
tiles = {
    "Calendar": (1, 804), "Camera": (2, 804), "Chrome": (5, 804),
    "Clock": (1, 1038), "Contacts": (2, 1038), "Drive": (3, 1038),
    "Files": (4, 1038), "Gmail": (5, 1038),
    "Google": (1, 1272), "Maps": (2, 1272), "Messages": (3, 1272),
    "Phone": (4, 1272), "Photos": (5, 1272),
    "Settings": (2, 1506), "YouTube": (5, 1506), "YT Music": (1, 1740),
}

os.makedirs("docs/tiles", exist_ok=True)
themed = 0
rows = []
for app, (c, ly) in tiles.items():
    cx = cols[c]; cy = ly - 105; r = 85
    box = (cx - r, cy - r, cx + r, cy + r)
    b = before.crop(box); a = after.crop(box)
    bp, ap = b.load(), a.load()
    sa = 0; diff = 0; n = (2 * r) ** 2
    for y in range(2 * r):
        for x in range(2 * r):
            pb, pa = bp[x, y], ap[x, y]
            if close(pa, SAGE):
                sa += 1
            if sum(abs(pb[i] - pa[i]) for i in range(3)) > 60:
                diff += 1
    ok = sa > 300 and diff / n > 0.10
    if ok:
        themed += 1
    name = app.replace(" ", "_")
    b.save(f"docs/tiles/{name}-before.png")
    a.save(f"docs/tiles/{name}-after.png")
    rows.append((name, b, a, ok))
    print(f"{app:10s} sage={sa:5d} diff%={100*diff/n:5.1f} {'THEMED' if ok else 'CHECK'}")

print(f"\n{themed}/{len(tiles)} sampled apps themed")

# composite: two columns of before/after tile pairs
TH = 160
n = len(rows)
comp = Image.new("RGB", (4 * (TH + 8) + 24, ((n + 3) // 4) * (TH + 26) + 8), (52, 58, 52))
from PIL import ImageDraw
dr = ImageDraw.Draw(comp)
for i, (name, b, a, ok) in enumerate(rows):
    x = 8 + (i % 4) * (2 * TH + 16)
    y = 8 + (i // 4) * (TH + 26)
    comp.paste(b.resize((TH, TH)), (x, y))
    comp.paste(a.resize((TH, TH)), (x + TH + 8, y))
    dr.text((x + 2, y + TH + 4), f"{name} {'OK' if ok else '??'}", fill=(255, 255, 140))
comp.save("docs/verification-tiles-before-after.png")
print("composite saved: docs/verification-tiles-before-after.png")
