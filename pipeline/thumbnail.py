"""Make a 1280x720 YouTube thumbnail for a longform/*.json video.

Style for the "Why You'd Never..." series: a dramatic monochrome, etched-looking
space image, a tiny astronaut for scale with an arrow pointing at it, and a
two-part hook ("IT CRUSHES" white + "YOU.." accent). Uses the same free image
sources as the videos (Wikipedia/Commons/NASA via render.py).

Spec in the JSON:
  "thumbnail": {"files": [...], "wiki": [...], "query": "...",
                "white": "IT CRUSHES", "accent": "YOU..",
                "astronaut": [x, y],        # where the tiny astronaut floats (0-1)
                "focus": [x, y],            # image point to keep in frame (0-1)
                "zoom": 1.0}
Usage: python pipeline/thumbnail.py longform/x.json [--offline]
writes previews/thumb-<slug>.jpg
"""
import json, math, os, sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R  # noqa: E402

TW, TH = 1280, 720
ACCENT = (255, 92, 51)
YELLOW = (255, 214, 0)


def get_image(spec, offline):
    if offline:
        return None
    os.makedirs(R.CACHE, exist_ok=True)
    for f in spec.get("files", []):
        img = R._commons_file(f if f.startswith("File:") else "File:" + f, f)
        if img is not None:
            return img
    return R.pick_image(spec, offline)


def cover(img, focus=(0.5, 0.5), zoom=1.0):
    iw, ih = img.size
    s = max(TW / iw, TH / ih) * zoom
    im = img.resize((int(iw * s) + 1, int(ih * s) + 1), Image.LANCZOS)
    x = int(min(max(focus[0] * im.width - TW / 2, 0), im.width - TW))
    y = int(min(max(focus[1] * im.height - TH / 2, 0), im.height - TH))
    return im.crop((x, y, x + TW, y + TH))


def etched(img):
    """High-contrast monochrome with fine engraving lines and grain."""
    g = ImageOps.grayscale(img)
    g = ImageOps.autocontrast(g, cutoff=1)
    g = g.filter(ImageFilter.UnsharpMask(radius=3, percent=180, threshold=2))
    a = np.asarray(g, np.float32) / 255.0
    a = np.clip((a - 0.5) * 1.35 + 0.5, 0, 1) ** 1.15
    yy, xx = np.mgrid[0:TH, 0:TW]
    lines = 0.5 + 0.5 * np.sin((xx * 0.35 + yy * 0.9) * 1.6)   # diagonal hatch
    shade = np.where(a < lines * 0.9, a * 0.55, a)                # hatch the mid/dark tones
    rng = np.random.default_rng(3)
    shade = np.clip(shade + rng.normal(0, 0.035, shade.shape), 0, 1)
    # vignette
    v = 1 - 0.55 * (((xx - TW / 2) / (TW / 2)) ** 2 + ((yy - TH / 2) / (TH / 2)) ** 2) / 2
    out = (shade * np.clip(v, 0.35, 1) * 255).astype(np.uint8)
    return Image.fromarray(out).convert("RGB")


def astronaut(h):
    """Tiny white astronaut silhouette (h px tall) drawn with simple shapes."""
    s = h / 100
    im = Image.new("RGBA", (int(80 * s), int(110 * s)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    W = (245, 245, 245, 255)
    D = (40, 40, 40, 255)
    d.rounded_rectangle((10 * s, 30 * s, 26 * s, 70 * s), radius=5 * s, fill=(200, 200, 200, 255))  # backpack
    d.rounded_rectangle((20 * s, 32 * s, 58 * s, 75 * s), radius=10 * s, fill=W)                    # torso
    d.ellipse((22 * s, 2 * s, 56 * s, 36 * s), fill=W)                                               # helmet
    d.ellipse((30 * s, 10 * s, 54 * s, 28 * s), fill=D)                                              # visor
    d.line((56 * s, 42 * s, 74 * s, 30 * s), fill=W, width=int(9 * s))                               # waving arm
    d.line((22 * s, 44 * s, 8 * s, 66 * s), fill=W, width=int(9 * s))                                # arm
    d.line((30 * s, 72 * s, 24 * s, 104 * s), fill=W, width=int(11 * s))                             # legs
    d.line((48 * s, 72 * s, 58 * s, 102 * s), fill=W, width=int(11 * s))
    im = im.rotate(-18, expand=True, resample=Image.BICUBIC)
    glow = im.filter(ImageFilter.GaussianBlur(6 * s))
    base = Image.new("RGBA", im.size, (0, 0, 0, 0))
    base.alpha_composite(glow)
    base.alpha_composite(im)
    return base


def arrow(d, start, end, color, width=9):
    """Curved hand-drawn style arrow from start to end."""
    (x0, y0), (x1, y1) = start, end
    mx, my = (x0 + x1) / 2 + (y1 - y0) * 0.35, (y0 + y1) / 2 - (x1 - x0) * 0.35
    pts = []
    for i in range(41):
        t = i / 40
        pts.append(((1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t * t * x1,
                    (1 - t) ** 2 * y0 + 2 * (1 - t) * t * my + t * t * y1))
    d.line(pts, fill=color, width=width, joint="curve")
    ang = math.atan2(y1 - pts[-4][1], x1 - pts[-4][0])
    L = 34
    for da in (2.6, -2.6):
        d.line((x1, y1, x1 + L * math.cos(ang + da), y1 + L * math.sin(ang + da)), fill=color, width=width)


def vivid(img):
    """Full-colour, punchy look: more saturation and contrast, a slight glow and a dark vignette."""
    im = img.convert("RGB")
    im = ImageOps.autocontrast(im, cutoff=1)
    im = ImageEnhance.Color(im).enhance(1.45)
    im = ImageEnhance.Contrast(im).enhance(1.18)
    im = im.filter(ImageFilter.UnsharpMask(radius=3, percent=140, threshold=2))
    glow = im.filter(ImageFilter.GaussianBlur(18))
    im = Image.blend(im, ImageChops.screen(im, glow), 0.35)
    a = np.asarray(im, np.float32) / 255.0
    yy, xx = np.mgrid[0:TH, 0:TW]
    v = 1 - 0.6 * (((xx - TW / 2) / (TW / 2)) ** 2 + ((yy - TH / 2) / (TH / 2)) ** 2) / 2
    top = np.clip(1 - 0.55 * np.clip(1 - yy / (TH * 0.42), 0, 1), 0, 1)   # darker top band so the text pops
    a = a * np.clip(v, 0.3, 1)[..., None] * top[..., None]
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def make(path, offline=False, source=None):
    ep = json.load(open(path))
    spec = ep["thumbnail"]
    img = source if source is not None else get_image(spec, offline)
    if img is None:
        img = R.starfield(5, TW * 2, TH * 2).resize((TW, TH))
    look = etched if spec.get("style") == "etched" else vivid
    canvas = look(cover(img, tuple(spec.get("focus", (0.5, 0.5))), spec.get("zoom", 1.0))).convert("RGBA")
    d = ImageDraw.Draw(canvas)

    # hook text, top-left, Inter Black with heavy outline
    white, accent = spec["white"], spec["accent"]
    size = 150
    fnt = R.font(R.FONT_BLACK, size)
    while max(fnt.getlength(white), fnt.getlength(accent)) > TW * 0.62 and size > 80:
        size -= 6
        fnt = R.font(R.FONT_BLACK, size)
    x, y = 50, 28
    for txt, col in ((white, (255, 255, 255)), (accent, YELLOW)):
        d.text((x, y), txt, font=fnt, fill=col, stroke_width=12, stroke_fill=(0, 0, 0))
        y += int(size * 1.02)

    # tiny astronaut + arrow pointing at it
    ax, ay = spec.get("astronaut", (0.3, 0.68))
    a = astronaut(spec.get("astronaut_size", 70))
    px, py = int(ax * TW - a.width / 2), int(ay * TH - a.height / 2)
    canvas.alpha_composite(a, (px, py))
    tx, ty = ax * TW, ay * TH
    start = (min(max(tx - 170, 60), TW - 60), max(ty - 230, 175))
    arrow(d, start, (tx - a.width * 0.45, ty - a.height * 0.45), ACCENT)

    out = os.path.join(R.ROOT, "previews", f"thumb-{ep['slug']}.jpg")
    canvas.convert("RGB").save(out, quality=90)
    print("thumbnail ->", out)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for p in args:
        make(p, offline="--offline" in sys.argv)
