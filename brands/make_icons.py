"""Generate the Chickadee mark — "Tech Accent" style (John's pick, 2026-07-25):
white bird head + black cap + blue wing accent on a dark round badge, with a
rounded lowercase wordmark and the blue tagline "voice & ai, plug and play".

Outputs:
  chickadee-addons/chickadee/icon.png        (256x256, badge)
  chickadee-addons/chickadee/logo.png        (500 wide, mark + wordmark + tagline)
  chickadee/brands/custom_integrations/chickadee/icon.png     (256x256)
  chickadee/brands/custom_integrations/chickadee/icon@2x.png  (512x512)
  chickadee/brands/custom_integrations/chickadee/logo.png     (512 wide)
  chickadee/brands/custom_integrations/chickadee/logo@2x.png  (1024 wide)
"""
from PIL import Image, ImageDraw, ImageFont
import math, os

S = 1024  # master canvas

DARK = (22, 24, 29, 255)       # badge background
CAP = (14, 15, 18, 255)        # cap/beak black
WHITE = (255, 255, 255, 255)   # face
BLUE = (61, 125, 219, 255)     # wing accent + tagline
INKTEXT = (26, 28, 34, 255)    # wordmark

def draw_bird_e(d, cx, cy, r):
    """Column-E bird: white-outlined head, black cap chord, blue wing, bold beak."""
    # white outline ring so the cap reads against a dark badge
    o = r * 0.09
    d.ellipse((cx - r - o, cy - r - o, cx + r + o, cy + r + o), fill=WHITE)
    bbox = (cx - r, cy - r, cx + r, cy + r)
    # white head
    d.ellipse(bbox, fill=WHITE)
    # blue wing accent: curved crescent hugging the lower-left edge —
    # a chord lens cut by an offset white circle
    ib = (cx - r * 0.99, cy - r * 0.99, cx + r * 0.99, cy + r * 0.99)
    d.chord(ib, 88, 192, fill=BLUE)
    ccx, ccy, cr = cx + r * 0.22, cy - r * 0.16, r * 0.96
    d.ellipse((ccx - cr, ccy - cr, ccx + cr, ccy + cr), fill=WHITE)
    # black cap: chord across the top ~40%
    d.chord(bbox, 192, 348, fill=CAP)
    # eye: black dot on the white, tucked under the cap on the beak side
    ex, ey = cx + r * 0.33, cy - r * 0.02
    er = r * 0.105
    d.ellipse((ex - er, ey - er, ex + er, ey + er), fill=CAP)
    # beak: bold triangle at the right edge, at the cap junction
    d.polygon([
        (cx + r * 0.72, cy - r * 0.30),
        (cx + r * 1.34, cy - r * 0.02),
        (cx + r * 0.70, cy + r * 0.22),
    ], fill=CAP)

def make_badge():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = 24
    # thin white rim, then dark badge
    d.ellipse((m, m, S - m, S - m), fill=WHITE)
    rim = 14
    d.ellipse((m + rim, m + rim, S - m - rim, S - m - rim), fill=DARK)
    draw_bird_e(d, S // 2 - 45, S // 2 + 15, 320)
    return img

def load_font(size):
    return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf", size)

def make_logo():
    W, H = 3600, 800
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # mark
    r = 300
    cx, cy = 340, H // 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=WHITE)
    rim = 10
    d.ellipse((cx - r + rim, cy - r + rim, cx + r - rim, cy + r - rim), fill=DARK)
    draw_bird_e(d, cx - 24, cy + 4, r * 0.62)
    # wordmark
    f_word = load_font(360)
    f_tag = load_font(108)
    text = "chickadee"
    tag = "voice & ai, plug and play"
    tx = cx + r + 120
    wb = d.textbbox((0, 0), text, font=f_word)
    tb = d.textbbox((0, 0), tag, font=f_tag)
    gap = 40
    total_h = (wb[3] - wb[1]) + gap + (tb[3] - tb[1])
    top = cy - total_h / 2
    d.text((tx, top - wb[1]), text, font=f_word, fill=INKTEXT)
    d.text((tx + 14, top + (wb[3] - wb[1]) + gap - tb[1]), tag, font=f_tag, fill=BLUE)
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

SCRATCH = os.path.dirname(os.path.abspath(__file__))
badge.resize((256, 256), Image.LANCZOS).save(f"{SCRATCH}/preview_icon.png")
logo.resize((900, int(lh * 900 / lw)), Image.LANCZOS).save(f"{SCRATCH}/preview_logo.png")
print("done", logo.size)
