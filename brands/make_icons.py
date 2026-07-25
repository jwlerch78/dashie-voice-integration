"""Generate the Chickadee mark: flat geometric black-capped chickadee roundel.

Outputs:
  chickadee-addons/chickadee/icon.png        (256x256, badge)
  chickadee-addons/chickadee/logo.png        (500x200, mark + wordmark, transparent)
  chickadee/brands/custom_integrations/chickadee/icon.png     (256x256)
  chickadee/brands/custom_integrations/chickadee/icon@2x.png  (512x512)
  chickadee/brands/custom_integrations/chickadee/logo.png     (512 wide)
  chickadee/brands/custom_integrations/chickadee/logo@2x.png  (1024 wide)
"""
from PIL import Image, ImageDraw, ImageFont
import math, os

S = 1024  # master canvas

TEAL = (47, 107, 94, 255)       # badge
INK = (34, 34, 38, 255)         # cap/bib/beak near-black
CREAM = (250, 247, 240, 255)    # cheeks
BUFF = (232, 195, 158, 255)     # flank accent

def draw_bird(d, cx, cy, r, with_buff=True):
    """Chickadee head roundel: cream head, black cap (chord), small bib, beak."""
    bbox = (cx - r, cy - r, cx + r, cy + r)
    # head
    d.ellipse(bbox, fill=CREAM)
    # black cap: chord across the upper ~40% of the head, tilted down toward the beak
    d.chord(bbox, 197, 343, fill=INK)
    # bib: narrow wedge at bottom center
    d.pieslice(bbox, 68, 92, fill=INK)
    # beak: small triangle on the right at the cap/cheek boundary
    ang = math.radians(-14)
    bx = cx + r * math.cos(ang)
    by = cy + r * math.sin(ang)
    blen = r * 0.36
    d.polygon([
        (bx - r * 0.20, by - r * 0.14),
        (bx + blen, by + r * 0.05),
        (bx - r * 0.12, by + r * 0.18),
    ], fill=INK)
    # eye glint inside the cap
    ex, ey = cx + r * 0.36, cy - r * 0.40
    er = r * 0.075
    d.ellipse((ex - er, ey - er, ex + er, ey + er), fill=CREAM)

def make_badge():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = 40
    d.ellipse((m, m, S - m, S - m), fill=TEAL)
    draw_bird(d, S // 2 - 30, S // 2 + 20, 330)
    return img

def make_mark_transparent():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_bird(d, S // 2 - 20, S // 2, 430)
    return img

def load_font(size):
    for p in (
        "/System/Library/Fonts/Supplemental/Avenir Next.ttc",
        "/System/Library/Fonts/Supplemental/Futura.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
    ):
        if os.path.exists(p):
            try:
                # index 0 may be Regular; try to find a demi/medium face
                for idx in range(12):
                    try:
                        f = ImageFont.truetype(p, size, index=idx)
                        name = " ".join(f.getname())
                        if any(w in name for w in ("Demi", "Medium", "Bold")):
                            return f
                    except OSError:
                        break
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default()

def make_logo():
    W, H = 3400, 640
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = 250
    cx, cy = 300, H // 2
    d.ellipse((cx - r - 26, cy - r - 26, cx + r + 26, cy + r + 26), fill=TEAL)
    draw_bird(d, cx - 8, cy + 6, r * 0.78)
    font = load_font(340)
    text = "chickadee"
    tx = cx + r + 110
    bb = d.textbbox((0, 0), text, font=font)
    ty = cy - (bb[3] - bb[1]) / 2 - bb[1]
    d.text((tx, ty), text, font=font, fill=INK)
    # crop to content + padding
    bbox = img.getbbox()
    pad = 30
    img = img.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                    min(W, bbox[2] + pad), min(H, bbox[3] + pad)))
    return img

badge = make_badge()
logo = make_logo()

ADDON = "/Users/johnlerch/projects/chickadee-addons/chickadee"
BRANDS = "/Users/johnlerch/projects/chickadee/brands/custom_integrations/chickadee"
os.makedirs(BRANDS, exist_ok=True)

badge.resize((256, 256), Image.LANCZOS).save(f"{ADDON}/icon.png")
lw, lh = logo.size
logo.resize((500, int(lh * 500 / lw)), Image.LANCZOS).save(f"{ADDON}/logo.png")

badge.resize((256, 256), Image.LANCZOS).save(f"{BRANDS}/icon.png")
badge.resize((512, 512), Image.LANCZOS).save(f"{BRANDS}/icon@2x.png")
logo.resize((512, int(lh * 512 / lw)), Image.LANCZOS).save(f"{BRANDS}/logo.png")
logo.resize((1024, int(lh * 1024 / lw)), Image.LANCZOS).save(f"{BRANDS}/logo@2x.png")

# preview copies for the user
SCRATCH = os.path.dirname(os.path.abspath(__file__))
badge.resize((256, 256), Image.LANCZOS).save(f"{SCRATCH}/preview_icon.png")
logo.resize((800, int(lh * 800 / lw)), Image.LANCZOS).save(f"{SCRATCH}/preview_logo.png")
print("done", logo.size)
