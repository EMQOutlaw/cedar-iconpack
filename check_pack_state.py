#!/usr/bin/env python3
"""Compare fresh System-pack drawer shot vs the themed CEDAR-pack shot."""
from PIL import Image

SAGE = (123, 168, 138)
def close(p, c, tol=32):
    return all(abs(p[i] - c[i]) <= tol for i in range(3))

fresh = Image.open("docs/drawer-before.png").convert("RGB")
themed = Image.open("docs/drawer-after.png").convert("RGB")
fp, tp = fresh.load(), themed.load()

for name, (cx, cy) in {"Clock": (134, 933), "Chrome": (946, 699), "Gmail": (946, 933)}.items():
    sb = sa = 0
    for y in range(cy - 85, cy + 85):
        for x in range(cx - 85, cx + 85):
            if close(fp[x, y], SAGE):
                sb += 1
            if close(tp[x, y], SAGE):
                sa += 1
    print(f"{name}: fresh-system-shot sage={sb}  themed-cedar-shot sage={sa}")
