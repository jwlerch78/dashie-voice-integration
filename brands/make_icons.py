#!/usr/bin/env python3
"""Derive the home-assistant/brands images for `dashie_voice` from the add-on art.

The brands images are NOT independently drawn. They are the same Dashie mark and
wordmark the add-on ships, resized to the sizes brands wants — that is the whole
point: HA renders this icon next to an add-on the user just installed, and the two
must not be two different pictures.

Until 2026-07-30 this script drew a bird and the wordmark "chickadee" from scratch,
because that was a separate brand with its own art. The brand is retired (one
product, two editions), so the drawing code is gone and the add-on PNGs
(`dashie-ha/icon.png`, `dashie-ha/logo.png`) are now the single source.

Usage (from the repo root):

    python3 brands/make_icons.py [path/to/dashie-ha-console]

Writes brands/custom_integrations/dashie_voice/{icon,icon@2x,logo,logo@2x}.png.
"""

import sys
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "brands" / "custom_integrations" / "dashie_voice"

# The add-on repo (jwlerch78/dashie-ha), cloned as dashie-ha-console by convention.
DEFAULT_ADDON_REPO = Path.home() / "projects" / "dashie-ha-console"


def fit(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    w, h = img.size
    scale = min(max_w / w, max_h / h)
    return img.resize((round(w * scale), round(h * scale)), Image.LANCZOS)


def main() -> int:
    addon = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_ADDON_REPO
    src = addon / "dashie-ha"
    icon_src, logo_src = src / "icon.png", src / "logo.png"
    for p in (icon_src, logo_src):
        if not p.is_file():
            print(f"missing source art: {p}", file=sys.stderr)
            print("pass the add-on repo path as argv[1]", file=sys.stderr)
            return 1

    OUT.mkdir(parents=True, exist_ok=True)

    icon = Image.open(icon_src).convert("RGBA")
    if icon.size[0] != icon.size[1]:
        print(f"icon source is not square: {icon.size}", file=sys.stderr)
        return 1
    icon.resize((256, 256), Image.LANCZOS).save(OUT / "icon.png")
    icon.resize((512, 512), Image.LANCZOS).save(OUT / "icon@2x.png")

    # brands wants the logo trimmed to its content, no baked-in padding.
    logo = Image.open(logo_src).convert("RGBA")
    logo = logo.crop(logo.getbbox())
    fit(logo, 512, 256).save(OUT / "logo.png")
    fit(logo, 1024, 512).save(OUT / "logo@2x.png")

    for name in ("icon.png", "icon@2x.png", "logo.png", "logo@2x.png"):
        print(f"{name}: {Image.open(OUT / name).size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
