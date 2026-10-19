#!/usr/bin/env python3
"""Stage the renders and the upper-floor plan from the Heights 777 brochure.

Sources come from SRC (a local folder of the brochure's assets) or, when that is
unset or missing, from the brochure's GitHub Pages site. JPEG renders keep their
full source resolution (the cover is a full-bleed photograph and the PDF is for
print) and are re-encoded at q84. The upper-floor plan is copied whole (plan-upper.png) and
cropped to the centre residence (plan-14.png, x 33-73 % of the sheet; ROOMS in
index.html uses the same crop).
Run:  [SRC=/path/to/brochure/assets] python3 tools/build_assets.py
"""
import io, os, urllib.request
from pathlib import Path
from PIL import Image

SRC = Path(os.environ["SRC"]) if os.environ.get("SRC") else None
PAGES = "https://mizanqist.github.io/heights-777/assets/"
DST = Path(__file__).resolve().parent.parent / "assets"
RENDERS = ["corner-dusk.jpg", "front-clear.jpg", "front-overcast.jpg", "entrance-day.jpg",
           "entrance-dusk.jpg", "balconies-aerial.jpg", "street-day.jpg"]
CROP = (0.33, 0.73)


def fetch(name: str) -> bytes:
    if SRC and (SRC / name).exists():
        return (SRC / name).read_bytes()
    with urllib.request.urlopen(PAGES + name, timeout=90) as r:
        return r.read()


def main():
    DST.mkdir(exist_ok=True)
    for name in RENDERS:
        im = Image.open(io.BytesIO(fetch(name)))
        im.load()
        im.convert("RGB").save(DST / name, "JPEG", quality=84, optimize=True, progressive=True)
        print(name, im.size, (DST / name).stat().st_size // 1024, "KB")
    raw = fetch("plan-upper.png")
    (DST / "plan-upper.png").write_bytes(raw)
    plan = Image.open(io.BytesIO(raw))
    crop = plan.crop((round(plan.width * CROP[0]), 0, round(plan.width * CROP[1]), plan.height))
    crop.save(DST / "plan-14.png", optimize=True)
    print("plan-upper.png", plan.size, "· plan-14.png", crop.size)


if __name__ == "__main__":
    main()
