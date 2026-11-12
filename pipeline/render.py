"""Render Next Stop: Universe episodes from episodes/*.json into vertical Shorts.

Free stack: Kokoro (local AI voice), NASA Image and Video Library (public domain
imagery), Pillow + ffmpeg for animation, captions and encoding.

Usage:
  python pipeline/render.py --all            # render every new/changed episode
  python pipeline/render.py episodes/x.json  # render one episode
  add --offline to skip NASA downloads (procedural backgrounds; for local tests)
"""
import argparse, glob, hashlib, io, json, math, os, random, re, subprocess, sys, time

import numpy as np
import requests
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 30
SR = 24000
PAD = 0.35            # silence after each segment (seconds)
ACCENT = (92, 225, 255)
WHITE = (255, 255, 255)
MODEL_DIR = os.environ.get("KOKORO_DIR", os.path.join(ROOT, "models"))
CACHE = os.environ.get("IMG_CACHE", "/tmp/nsu-cache")
VOICE = os.environ.get("VOICE", "am_michael")

FONT_BLACK = os.path.join(ROOT, "fonts", "InterDisplay-Black.otf")
FONT_BOLD = os.path.join(ROOT, "fonts", "Inter-Bold.otf")
FONT_SEMI = os.path.join(ROOT, "fonts", "Inter-SemiBold.otf")
_fonts = {}


def font(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


# ---------------------------------------------------------------- voice
_kokoro = None


def tts(text):
    global _kokoro
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        _kokoro = Kokoro(os.path.join(MODEL_DIR, "kokoro-v1.0.int8.onnx"),
                         os.path.join(MODEL_DIR, "voices-v1.0.bin"))
    samples, sr = _kokoro.create(text, voice=VOICE, speed=1.0, lang="en-us")
    assert sr == SR
    return np.asarray(samples, dtype=np.float32)


def ambient_pad(seconds, seed=7):
    """Very quiet procedural space drone so the video is never dead silent."""
    t = np.arange(int(seconds * SR)) / SR
    rng = np.random.default_rng(seed)
    out = np.zeros_like(t)
    for f in (55.0, 82.41, 110.0, 164.81):
        lfo = 0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(0.03, 0.08) * t + rng.uniform(0, 6))
        out += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * lfo
    out /= np.max(np.abs(out)) + 1e-9
    fade = np.minimum(1, np.minimum(t / 2.0, (seconds - t) / 2.0))
    return (out * fade * 0.035).astype(np.float32)


# ---------------------------------------------------------------- images
def nasa_image(visual, offline=False):
    """Return a PIL RGB image for a visual spec using the NASA Image Library."""
    if offline:
        return None
    os.makedirs(CACHE, exist_ok=True)
    nasa_id = visual.get("nasa_id")
    if not nasa_id:
        q = visual["query"]
        r = requests.get("https://images-api.nasa.gov/search",
                         params={"q": q, "media_type": "image"}, timeout=30)
        r.raise_for_status()
        items = r.json()["collection"]["items"]
        if not items:
            print(f"  ! no NASA result for {q!r}")
            return None
        pick = min(visual.get("pick", 0), len(items) - 1)
        nasa_id = items[pick]["data"][0]["nasa_id"]
        print(f"  NASA {q!r} -> {nasa_id}: {items[pick]['data'][0].get('title','')[:70]}")
    path = os.path.join(CACHE, re.sub(r"[^A-Za-z0-9_.-]", "_", nasa_id) + ".jpg")
    if not os.path.exists(path):
        r = requests.get(f"https://images-api.nasa.gov/asset/{nasa_id}", timeout=30)
        r.raise_for_status()
        hrefs = [i["href"].replace("http://", "https://") for i in r.json()["collection"]["items"]]
        jpgs = [h for h in hrefs if h.lower().endswith((".jpg", ".jpeg", ".png"))]
        order = ["~orig", "~large", "~medium"]
        jpgs.sort(key=lambda h: next((i for i, k in enumerate(order) if k in h), 9))
        for h in jpgs:
            try:
                resp = requests.get(h, timeout=60)
                if resp.status_code != 200 or len(resp.content) > 40_000_000:
                    continue
                img = Image.open(io.BytesIO(resp.content)).convert("RGB")
                img.thumbnail((3000, 3000))
                img.save(path, quality=92)
                break
            except Exception as e:  # noqa: BLE001
                print("  ! asset failed", h, e)
        else:
            return None
    return Image.open(path).convert("RGB")


def starfield(seed=1, w=W, h=H, tint=(10, 22, 52)):
    rng = np.random.default_rng(seed)
    y = np.linspace(0, 1, h)[:, None]
    base = np.zeros((h, w, 3), np.float32)
    for c in range(3):
        base[..., c] = 2 + tint[c] * (y ** 1.6)
    n = 1400
    xs, ys = rng.integers(0, w, n), rng.integers(0, h, n)
    br = rng.uniform(60, 255, n) * rng.uniform(0.3, 1, n)
    base[ys, xs] = np.maximum(base[ys, xs], br[:, None])
    big = rng.random(n) < 0.12  # a few larger stars
    for dx, dy in ((1, 0), (0, 1), (1, 1)):
        yy, xx = np.minimum(ys[big] + dy, h - 1), np.minimum(xs[big] + dx, w - 1)
        base[yy, xx] = np.maximum(base[yy, xx], br[big][:, None])
    img = Image.fromarray(base.clip(0, 255).astype(np.uint8))
    glow = Image.fromarray(base.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
    return Image.blend(img, glow, 0.35)


def compose_background(img, seed):
    """Build an oversized 9:16 canvas (for Ken Burns) from any image."""
    bw, bh = int(W * 1.12), int(H * 1.12)
    if img is None:
        return starfield(seed, bw, bh)
    iw, ih = img.size
    aspect = iw / ih
    if aspect <= 1.0:  # portrait/square: cover-crop
        s = max(bw / iw, bh / ih)
        im = img.resize((int(iw * s) + 1, int(ih * s) + 1), Image.LANCZOS)
        x, y = (im.width - bw) // 2, (im.height - bh) // 2
        return im.crop((x, y, x + bw, y + bh))
    # landscape: blurred fill + centered image, zoomed so it fills ~60% of height
    s = max(bw / iw, bh / ih)
    bg = img.resize((int(iw * s) + 1, int(ih * s) + 1), Image.BILINEAR)
    x, y = (bg.width - bw) // 2, (bg.height - bh) // 2
    bg = bg.crop((x, y, x + bw, y + bh)).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(Image.new("RGB", bg.size, (0, 0, 0)), bg, 0.45)
    target_h = int(bh * 0.62)
    fw = int(iw * target_h / ih)
    fg = img.resize((fw, target_h), Image.LANCZOS)
    if fw > bw * 1.6:  # very wide panoramas: crop the middle
        cx = fw // 2
        fg = fg.crop((cx - int(bw * 0.8), 0, cx + int(bw * 0.8), target_h))
    bg.paste(fg, ((bw - fg.width) // 2, (bh - fg.height) // 2))
    return bg


def legibility(base):
    """Darken top and bottom so captions read on any image."""
    w, h = base.size
    y = np.linspace(0, 1, h)[:, None]
    a = np.clip(np.maximum((0.28 - y) / 0.28, (y - 0.55) / 0.45), 0, 1) ** 1.3 * 0.75
    arr = np.asarray(base, np.float32) * (1 - a[..., None])
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


# ---------------------------------------------------------------- text
def wrap(text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if fnt.getlength(t) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


_text_cache = {}


def text_layer(text, path, size, color=WHITE, max_w=960, stroke=6, box=None, spacing=1.12):
    key = (text, path, size, color, max_w, stroke, box)
    if key in _text_cache:
        return _text_cache[key]
    fnt = font(path, size)
    lines = wrap(text, fnt, max_w)
    lh = int(size * spacing)
    tw = int(max(fnt.getlength(l) for l in lines)) + stroke * 2 + 4
    th = lh * len(lines) + stroke * 2 + int(size * 0.25)
    padx, pady = (44, 26) if box else (0, 0)
    layer = Image.new("RGBA", (tw + padx * 2, th + pady * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if box:
        d.rounded_rectangle((0, 0, layer.width - 1, layer.height - 1), radius=min(40, layer.height // 2), fill=box)
    for i, l in enumerate(lines):
        lw = fnt.getlength(l)
        d.text(((layer.width - lw) / 2, pady + stroke + i * lh), l, font=fnt, fill=color,
               stroke_width=stroke, stroke_fill=(0, 0, 0, 220) if stroke else None)
    _text_cache[key] = layer
    return layer


def paste_center(frame, layer, cy, alpha=1.0, scale=1.0):
    if scale != 1.0:
        layer = layer.resize((max(1, int(layer.width * scale)), max(1, int(layer.height * scale))), Image.BILINEAR)
    if alpha < 1.0:
        layer = layer.copy()
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    frame.alpha_composite(layer, (int((W - layer.width) / 2), int(cy - layer.height / 2)))


def chunks(text, max_words=4, max_chars=24):
    words, out, cur = text.split(), [], []
    for wd in words:
        if cur and (len(cur) >= max_words or len(" ".join(cur + [wd])) > max_chars):
            out.append(" ".join(cur))
            cur = []
        cur.append(wd)
        if re.search(r"[.!?]$", wd):
            out.append(" ".join(cur))
            cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


# ---------------------------------------------------------------- render
def render_episode(path, offline=False):
    ep = json.load(open(path))
    num = ep["number"]
    stem = f"ep{num:03d}"
    out_mp4 = os.path.join(ROOT, "videos", stem + ".mp4")
    print(f"== Episode {num}: {ep['title']}")

    # 1) voice per segment -> exact timing
    seg_audio, seg_speech = [], []
    for s in ep["segments"]:
        a = tts(s["text"])
        seg_speech.append(len(a) / SR)
        seg_audio.append(np.concatenate([a, np.zeros(int(PAD * SR), np.float32)]))
    voice = np.concatenate(seg_audio)
    total = len(voice) / SR + 0.6
    voice = np.concatenate([voice, np.zeros(int(0.6 * SR), np.float32)])
    mix = voice + ambient_pad(total)[: len(voice)]
    mix = mix / max(1.0, np.max(np.abs(mix)) / 0.95)
    wav = f"/tmp/{stem}.wav"
    sf.write(wav, mix, SR)
    print(f"  audio {total:.1f}s")

    # 2) frames
    tmp = out_mp4.replace(".mp4", ".tmp.mp4")
    os.makedirs(os.path.dirname(out_mp4), exist_ok=True)
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", wav, "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-af", "loudnorm=I=-15:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart", tmp,
    ], stdin=subprocess.PIPE)

    brand = text_layer("NEXT STOP: UNIVERSE", FONT_BOLD, 34, color=(255, 255, 255), stroke=3)
    preview_frames = []
    n_segs = len(ep["segments"])
    for si, s in enumerate(ep["segments"]):
        v = s.get("visual", {"type": "image"})
        vt = v.get("type", "image")
        speech = seg_speech[si]
        dur = speech + PAD + (0.6 if si == n_segs - 1 else 0)
        nframes = int(round(dur * FPS))
        if vt == "card":
            base = starfield(seed=num * 100 + si)
        else:
            base = legibility(compose_background(nasa_image(v, offline), seed=num * 100 + si))
        bw, bh = base.size
        zoom_in = (si % 2 == 0)
        subs = chunks(s["text"])
        weights = [max(4, len(c)) for c in subs]
        bounds = np.cumsum([0] + [speech * w / sum(weights) for w in weights])
        mid_frame = nframes // 2
        for fi in range(nframes):
            t = fi / FPS
            # Ken Burns
            if vt == "card":
                frame = base.copy().convert("RGBA")
            else:
                p = fi / max(1, nframes - 1)
                z = 1.0 + 0.08 * (p if zoom_in else 1 - p)
                cw, ch = int(bw / z / 1.12 * 1.0), int(bh / z / 1.12)
                cx, cy = bw / 2 + (p - 0.5) * 30, bh / 2
                box = (int(cx - cw / 2), int(cy - ch / 2), int(cx - cw / 2) + cw, int(cy - ch / 2) + ch)
                frame = base.crop(box).resize((W, H), Image.BILINEAR).convert("RGBA")

            if vt == "title":
                paste_center(frame, text_layer(f"EPISODE {num}", FONT_BOLD, 46, color=(10, 20, 40),
                                               stroke=0, box=ACCENT + (255,)), 720, alpha=ease(t / 0.4))
                paste_center(frame, text_layer(ep["title"].upper(), FONT_BLACK, 150, max_w=1000), 900,
                             alpha=ease((t - 0.2) / 0.4), scale=0.85 + 0.15 * ease((t - 0.2) / 0.5))
                if ep.get("subtitle"):
                    paste_center(frame, text_layer(ep["subtitle"], FONT_SEMI, 56, color=ACCENT, stroke=4),
                                 1060, alpha=ease((t - 0.7) / 0.4))
            elif vt == "card":
                k = ease((t - 0.15) / 0.45)
                paste_center(frame, text_layer(v["big"], FONT_BLACK, 230, color=ACCENT, stroke=0, max_w=1000),
                             780, alpha=k, scale=0.6 + 0.4 * k)
                paste_center(frame, text_layer(v.get("label", ""), FONT_BLACK, 74, max_w=960, stroke=0), 1000,
                             alpha=ease((t - 0.5) / 0.4))
                if v.get("sub"):
                    paste_center(frame, text_layer(v["sub"], FONT_SEMI, 46, color=(185, 200, 225), stroke=0),
                                 1120, alpha=ease((t - 0.8) / 0.4))

            if s.get("headline") and vt not in ("title", "card"):
                paste_center(frame, text_layer(s["headline"], FONT_BLACK, 76, color=ACCENT, max_w=980), 330,
                             alpha=ease((t - 0.1) / 0.35))
            if vt == "end":
                paste_center(frame, text_layer(f"NEXT STOP: {ep['next_stop'].upper()}", FONT_BLACK, 92,
                                               color=(255, 110, 70) if v.get("warm") else ACCENT, max_w=1000),
                             330, alpha=ease(t / 0.4))
                if t > max(0.0, dur - 4.0):
                    paste_center(frame, text_layer(f"FOLLOW FOR EPISODE {num + 1}", FONT_BLACK, 56,
                                                   color=(5, 15, 30), stroke=0, box=ACCENT + (245,)),
                                 1560, alpha=ease((t - (dur - 4.0)) / 0.3))

            # spoken captions (skip on title card for a clean opener)
            if vt != "title" and t < speech:
                idx = int(np.searchsorted(bounds, t, side="right") - 1)
                idx = min(max(idx, 0), len(subs) - 1)
                paste_center(frame, text_layer(subs[idx], FONT_BLACK, 78, max_w=940, stroke=8), 1380)

            frame.alpha_composite(brand, ((W - brand.width) // 2, 120))
            rgb = frame.convert("RGB")
            if fi < 5 and si > 0:  # dip from black between segments
                rgb = Image.blend(Image.new("RGB", (W, H)), rgb, (fi + 1) / 6)
            if fi == mid_frame:
                preview_frames.append(rgb.resize((270, 480)))
            ff.stdin.write(rgb.tobytes())
        print(f"  segment {si + 1}/{n_segs} [{vt}] {dur:.1f}s")
    ff.stdin.close()
    if ff.wait() != 0:
        raise SystemExit("ffmpeg failed")
    os.replace(tmp, out_mp4)

    # contact sheet for quick review
    cols = 5
    rows = math.ceil(len(preview_frames) / cols)
    sheet = Image.new("RGB", (270 * cols, 480 * rows))
    for i, im in enumerate(preview_frames):
        sheet.paste(im, ((i % cols) * 270, (i // cols) * 480))
    os.makedirs(os.path.join(ROOT, "previews"), exist_ok=True)
    sheet.save(os.path.join(ROOT, "previews", stem + ".jpg"), quality=85)
    meta = {"source": os.path.basename(path), "hash": file_hash(path), "seconds": round(total, 2),
            "rendered": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    json.dump(meta, open(os.path.join(ROOT, "videos", stem + ".meta.json"), "w"), indent=2)
    print(f"  -> {out_mp4} ({os.path.getsize(out_mp4) / 1e6:.1f} MB)")


def file_hash(path):
    h = hashlib.sha256(open(path, "rb").read())
    h.update(open(os.path.abspath(__file__), "rb").read())
    return h.hexdigest()[:16]


def needs_render(path):
    ep = json.load(open(path))
    meta = os.path.join(ROOT, "videos", f"ep{ep['number']:03d}.meta.json")
    if not os.path.exists(meta):
        return True
    return json.load(open(meta)).get("hash") != file_hash(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--offline", action="store_true")
    a = ap.parse_args()
    files = a.files or sorted(glob.glob(os.path.join(ROOT, "episodes", "*.json")))
    if a.all:
        files = [f for f in files if needs_render(f)]
    if not files:
        print("Nothing to render.")
    for f in files:
        render_episode(f, offline=a.offline)


if __name__ == "__main__":
    main()
