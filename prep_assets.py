#!/usr/bin/env python3
"""Prep assets for PUNTA CANA CONTEST deck — WSOP Super Circuit Punta Cana (LATAM).
CLONE of the Bahamas contest deck (deck-bahamas-contest-2026-09-11). Same white / tan /
aqua + gold palette, same CLEARED no-face beach/resort/water imagery (works for Punta
Cana too), same real Jamie photos (NO AI faces). Only OUT path differs from Bahamas.
Produces base64 embeds:
  - AQUA-tinted, lightly-darkened backdrops (behind white text over imagery)
  - LIGHT aqua/tan wash backdrops for text-heavy slides (dark teal text reads on them)
  - resized REAL Jamie photos (NO AI faces)
  - full-color scenery cards
Palette: off-white #FBF7EF, sand/tan #D8C7A6, aqua #2BAEC0-#38C4D0, deep teal #0E3B44.
"""
import base64, io, json, os
from PIL import Image, ImageEnhance, ImageOps

OUT = "/home/aiciv/state/edge-output/deck-punta-cana-contest-2026-09-12"
IMG = "/home/aiciv/state/edge-output/deck-bahamas-2026-09-10/bahamas-imagery"
# Real Punta Cana imagery (sourced 2026-10-09) so this deck reads as Punta Cana, not Bahamas.
# 2 are Hard Rock Punta Cana official photos (resort pool, casino poker room); beach = Playa
# Bavaro (Wikimedia CC BY-SA); coastline = DR aerial (Pexels); walkway = tropical resort (Pexels).
PC  = "/home/aiciv/state/edge-output/deck-punta-cana-contest-2026-09-12/pc-imagery"
THUMB = "/home/aiciv/state/edge-output/thumbnail-rollout-photos-2026-09-10"
CREAM = "/home/aiciv/state/edge-output/sponsorship-deck"  # source of logo + headshot assets

assets = {}

def b64_jpg(im, q=86):
    im = im.convert("RGB")
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

def b64_png(im):
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def logo_on_dark(src_path, box_w=360, box_h=120, pad=0.14):
    """Fit a (possibly transparent/dark-ink) logo onto a transparent canvas, recoloring
    any dark ink to near-white so it reads on the deep-teal brand strips. Preserves alpha."""
    im = Image.open(src_path).convert("RGBA")
    maxw, maxh = int(box_w * (1 - pad)), int(box_h * (1 - pad))
    im.thumbnail((maxw, maxh), Image.LANCZOS)
    r, g, b, a = im.split()
    lum = Image.merge("RGB", (r, g, b)).convert("L")
    white = ImageOps.colorize(lum, black=(245, 246, 240), white=(255, 255, 255),
                              mid=(250, 250, 246))
    white = white.convert("RGBA")
    white.putalpha(a)
    canvas = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    canvas.alpha_composite(white, ((box_w - white.width) // 2, (box_h - white.height) // 2))
    return canvas

def logo_natural(src_path, box_w=360, box_h=120, pad=0.14):
    """Fit a full-color logo onto a transparent canvas without recoloring (for brand marks
    that carry their own color, placed on white chips)."""
    im = Image.open(src_path).convert("RGBA")
    maxw, maxh = int(box_w * (1 - pad)), int(box_h * (1 - pad))
    im.thumbnail((maxw, maxh), Image.LANCZOS)
    canvas = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    canvas.alpha_composite(im, ((box_w - im.width) // 2, (box_h - im.height) // 2))
    return canvas

def circle_headshot(src_path, size=180):
    """Crop a headshot to a circle with a thin aqua ring, transparent outside."""
    im = Image.open(src_path).convert("RGBA")
    im = ImageOps.fit(im, (size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    from PIL import ImageDraw
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, size, size), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out

def fit(im, w, h):
    return ImageOps.fit(im, (w, h), Image.LANCZOS)

def aqua_darkened(src_path, w=1920, h=1080, bright=0.62, sat=0.85):
    """Photo backdrop pushed toward aqua/teal and darkened so WHITE text reads over it.
    Used on slides where text sits over the imagery (cover, host, section heroes)."""
    im = Image.open(src_path).convert("RGB")
    im = fit(im, w, h)
    im = ImageEnhance.Color(im).enhance(sat)
    im = ImageEnhance.Brightness(im).enhance(bright)
    lum = im.convert("L")
    dark = (10, 46, 54)      # deep teal shadow
    light = (120, 205, 214)  # aqua highlight
    duo = ImageOps.colorize(lum, black=dark, white=light, mid=(43, 174, 192))
    out = Image.blend(im, duo, 0.55)
    out = ImageEnhance.Brightness(out).enhance(0.9)
    return out

def light_wash(src_path, w=1920, h=1080):
    """Very light aqua/off-white wash for TEXT-HEAVY slides — DARK TEAL text reads on it."""
    im = Image.open(src_path).convert("L")
    im = fit(im, w, h)
    duo = ImageOps.colorize(im, black=(196, 224, 226), white=(251, 247, 239),
                            mid=(224, 240, 238))
    duo = ImageEnhance.Brightness(duo).enhance(1.05)
    return duo

# --- Hero / over-image backdrops (WHITE text) --- (Punta Cana imagery)
assets["cover_bg"] = b64_jpg(aqua_darkened(os.path.join(PC, "punta-cana-beach.jpg"), bright=0.66), 82)
assets["host_bg"]  = b64_jpg(aqua_darkened(os.path.join(PC, "coastline-aerial.jpg"), bright=0.6), 82)
assets["next_bg"]  = b64_jpg(aqua_darkened(os.path.join(PC, "hardrock-resort.jpg"), bright=0.6), 82)

# --- Light wash backdrops (DARK TEAL text) --- (Punta Cana imagery)
assets["prize_bg"] = b64_jpg(light_wash(os.path.join(PC, "hardrock-resort.jpg")), 84)
assets["event_bg"] = b64_jpg(light_wash(os.path.join(PC, "palm-walkway.jpg")), 84)
assets["gen_bg"]   = b64_jpg(light_wash(os.path.join(PC, "coastline-aerial.jpg")), 84)
assets["wj_bg"]    = b64_jpg(light_wash(os.path.join(PC, "casino-pokerroom.jpg")), 84)

# --- Real Jamie photos (NO AI) ---
hero = Image.open(os.path.join(THUMB, "jamie-headshot-wsop-cap-topaz.png"))
assets["jamie_cover"] = b64_jpg(fit(hero, 820, 1080), 88)
assets["jamie_host"]  = b64_jpg(fit(hero, 700, 760), 88)

for key, fn, size in [
    ("jamie_stage1", "jamie-shuffleup-0303-topaz.png", (520, 360)),
    ("jamie_stage2", "jamie-onmic-0304-topaz.png", (520, 360)),
    ("jamie_smiling", "jamie-smiling-0207-topaz.png", (520, 360)),
    ("jamie_win2006", "jamie-wsop-win-2006-topaz.png", (520, 360)),
]:
    p = os.path.join(THUMB, fn)
    if os.path.exists(p):
        assets[key] = b64_jpg(fit(Image.open(p), *size), 84)

# --- Full-color scenery cards ---
for key, fn, size in [
    ("scene_beach", "punta-cana-beach.jpg", (440, 300)),
    ("scene_pool", "hardrock-resort.jpg", (440, 300)),   # GP banner = the actual Hard Rock PC resort
    ("scene_marina", "coastline-aerial.jpg", (440, 300)),
    ("scene_poker", "casino-pokerroom.jpg", (440, 300)),  # real Hard Rock PC poker room
]:
    assets[key] = b64_jpg(fit(Image.open(os.path.join(PC, fn)), *size), 84)

# --- PROOF assets grafted from the finalized cream deck (real logos + headshot, NOT fabricated) ---
# Ambassador / partner brand logos -> placed on white chips, keep their own color.
for key, rel in [
    ("logo_wsop", "logos/wsop.png"),
    ("logo_solana", "logos/solana.png"),
    ("logo_bbo", "logos/bbo.png"),
]:
    p = os.path.join(CREAM, rel)
    if os.path.exists(p):
        assets[key] = b64_png(logo_natural(p, box_w=300, box_h=150, pad=0.20))

# Press / "featured on" logos -> recolored warm-white to read on the deep-teal press strip.
for key, rel in [
    ("press_espn", "logos_mono/espn.png"),  # mono wordmark w/ real alpha (logos/espn.png is a solid red tile)
    ("press_nyt", "media-assets/featured-logos/nyt.png"),
    ("press_wsj", "media-assets/featured-logos/wsj.png"),
    ("press_usatoday", "media-assets/featured-logos/usa-today.png"),
    ("press_forbes", "media-assets/featured-logos/forbes.png"),
]:
    p = os.path.join(CREAM, rel)
    if os.path.exists(p):
        assets[key] = b64_png(logo_on_dark(p, box_w=340, box_h=110, pad=0.16))

# Kym Sleezer headshot -> circular, for the Commerce case-study testimonial card.
ks = os.path.join(CREAM, "assets", "kym-sleezer-headshot.png")
if os.path.exists(ks):
    assets["kym_headshot"] = b64_png(circle_headshot(ks, size=200))

with open(os.path.join(OUT, "assets_b64.json"), "w") as f:
    json.dump(assets, f)

sizes = {k: len(v) for k, v in assets.items()}
total = sum(sizes.values())
print("assets:", len(assets), "total b64 chars:", total, f"(~{total/1024/1024:.1f}MB)")
