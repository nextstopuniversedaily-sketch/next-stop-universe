"""Render a native 16:9 long-form video (1920x1080) from longform/*.json.

Built for TV viewing: slower narration, large on-screen captions, chapter
markers, viewer-question cards and subscribe/like/share prompts.
Reuses the free image sources and helpers from render.py (Kokoro voice,
Wikipedia/Commons/NASA imagery, Pillow + ffmpeg).

Usage:
  python pipeline/render_long.py longform/moon-disappeared.json
  python pipeline/render_long.py --all          # every new/changed longform file
  python pipeline/render_long.py --all --list
  add --offline to skip image downloads (local tests)
writes videos/long/<slug>.mp4, .chapters.txt, .credits.txt, .meta.json and previews/long-<slug>.jpg
"""
import argparse, glob, hashlib, json, math, os, subprocess, sys, time

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R  # noqa: E402

W, H, FPS = 1920, 1080, 30
R.W, R.H = W, H  # paste_center / legibility read these module globals
SR = R.SR
PAD = 0.55          # calmer pause between segments
SPEED = float(os.environ.get("LONG_SPEED", "0.93"))
ROOT = R.ROOT
RED = (230, 33, 23)
QUESTION = (255, 200, 87)


def tts(text):
    R.tts("warm up") if R._kokoro is None else None
    samples, sr = R._kokoro.create(text, voice=R.VOICE, speed=SPEED, lang="en-us")
    return np.asarray(samples, dtype=np.float32)


def get_image(v, offline):
    if offline:
        return None
    os.makedirs(R.CACHE, exist_ok=True)
    for f in v.get("files", []):
        img = R._commons_file(f if f.startswith("File:") else "File:" + f, f)
        if img is not None:
            return img
    return R.pick_image(v, offline)


def compose(img, seed):
    bw, bh = int(W * 1.1), int(H * 1.1)
    if img is None:
        return R.starfield(seed, bw, bh)
    iw, ih = img.size
    if 1.45 <= iw / ih <= 2.4:  # wide photo: cover-crop
        s = max(bw / iw, bh / ih)
        im = img.resize((int(iw * s) + 1, int(ih * s) + 1), Image.LANCZOS)
        x, y = (im.width - bw) // 2, (im.height - bh) // 2
        return im.crop((x, y, x + bw, y + bh))
    # square, portrait or very wide panorama: whole image over a blurred, darkened fill
    s = max(bw / iw, bh / ih)
    bg = img.resize((int(iw * s) + 1, int(ih * s) + 1), Image.BILINEAR)
    x, y = (bg.width - bw) // 2, (bg.height - bh) // 2
    bg = bg.crop((x, y, x + bw, y + bh)).filter(ImageFilter.GaussianBlur(45))
    bg = Image.blend(Image.new("RGB", bg.size), bg, 0.4)
    th = int(bh * 0.96)
    fg = img.resize((max(1, int(iw * th / ih)), th), Image.LANCZOS)
    if fg.width > bw:
        fg = fg.resize((bw, int(fg.height * bw / fg.width)), Image.LANCZOS)
    bg.paste(fg, ((bw - fg.width) // 2, (bh - fg.height) // 2))
    return bg


def legibility(base):
    w, h = base.size
    y = np.linspace(0, 1, h)[:, None]
    a = np.clip(np.maximum((0.2 - y) / 0.2, (y - 0.62) / 0.38), 0, 1) ** 1.2 * 0.78
    arr = np.asarray(base, np.float32) * (1 - a[..., None])
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


def T(text, path, size, **kw):
    kw.setdefault("max_w", 1650)
    return R.text_layer(text, path, size, **kw)


def subscribe_button(scale=1.0):
    fnt = R.font(R.FONT_BLACK, int(52 * scale))
    tw = int(fnt.getlength("SUBSCRIBE"))
    w, h = tw + int(150 * scale), int(100 * scale)
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=RED + (255,))
    # bell-ish play triangle
    cx, cy, r = int(58 * scale), h // 2, int(20 * scale)
    d.polygon([(cx - r * 0.7, cy - r), (cx - r * 0.7, cy + r), (cx + r, cy)], fill=(255, 255, 255, 255))
    d.text((int(100 * scale), (h - fnt.size * 1.2) / 2), "SUBSCRIBE", font=fnt, fill=(255, 255, 255))
    return lay


def chunks(text):
    return R.chunks(text, max_words=7, max_chars=40)


def fmt(t):
    m, s = divmod(int(t), 60)
    return f"{m}:{s:02d}"


def render_long(path, offline=False):
    ep = json.load(open(path))
    slug = ep["slug"]
    out_dir = os.path.join(ROOT, "videos", "long")
    os.makedirs(out_dir, exist_ok=True)
    out_mp4 = os.path.join(out_dir, slug + ".mp4")
    print(f"== Long-form: {ep['title']}")
    segs = ep["segments"]

    seg_audio, seg_speech = [], []
    for s in segs:
        a = tts(s["text"])
        seg_speech.append(len(a) / SR)
        seg_audio.append(np.concatenate([a, np.zeros(int(PAD * SR), np.float32)]))
    voice = np.concatenate(seg_audio + [np.zeros(int(2.0 * SR), np.float32)])
    total = len(voice) / SR
    pad = R.ambient_pad(total + 0.1)[: len(voice)]
    pad = np.pad(pad, (0, len(voice) - len(pad))) * 1.4
    mix = voice + pad
    mix = mix / max(1.0, np.max(np.abs(mix)) / 0.95)
    wav = os.path.join("/tmp", slug + ".wav")
    sf.write(wav, mix, SR)
    print(f"  audio {total:.1f}s ({total / 60:.2f} min)")

    tmp = out_mp4.replace(".mp4", ".tmp.mp4")
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", wav, "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-maxrate", "2200k", "-bufsize", "4400k",
        "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-15:TP=-1.5:LRA=11",
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart", tmp,
    ], stdin=subprocess.PIPE)

    brand = T("NEXT STOP: UNIVERSE", R.FONT_BOLD, 30, stroke=3)
    sub_btn = subscribe_button(0.8)
    preview, chapters = [], []
    R.CREDITS.clear()
    last_img, t0 = None, 0.0
    n = len(segs)
    for si, s in enumerate(segs):
        v = s.get("visual", {"type": "image"})
        vt = v.get("type", "image")
        speech = seg_speech[si]
        dur = speech + PAD + (2.0 if si == n - 1 else 0)
        nframes = int(round(dur * FPS))
        if s.get("chapter"):
            chapters.append(f"{fmt(t0)} {s['chapter']}")
        if vt in ("card", "question"):
            base = R.starfield(seed=si * 31 + 5, w=int(W * 1.1), h=int(H * 1.1),
                               tint=(40, 30, 10) if vt == "question" else (10, 22, 52))
        else:
            img = get_image(v, offline)
            if img is None:
                img = last_img
            else:
                last_img = img
            base = legibility(compose(img, seed=si))
        bw, bh = base.size
        zoom_in = si % 2 == 0
        subs = chunks(s["text"])
        weights = [max(4, len(c)) for c in subs]
        bounds = np.cumsum([0] + [speech * w / sum(weights) for w in weights])
        chap_layer = T(s["chapter"].upper(), R.FONT_BOLD, 34, color=(10, 20, 40), stroke=0,
                       box=R.ACCENT + (240,)) if s.get("chapter") and vt not in ("title",) else None
        for fi in range(nframes):
            t = fi / FPS
            p = fi / max(1, nframes - 1)
            z = 1.0 + (0.045 if vt in ("card", "question") else 0.07) * (p if zoom_in else 1 - p)
            cw, ch = int(bw / z / 1.1), int(bh / z / 1.1)
            cx, cy = bw / 2 + (p - 0.5) * 40, bh / 2
            box = (int(cx - cw / 2), int(cy - ch / 2), int(cx - cw / 2) + cw, int(cy - ch / 2) + ch)
            frame = base.crop(box).resize((W, H), Image.BILINEAR).convert("RGBA")

            if vt == "title":
                R.paste_center(frame, T("NEXT STOP: UNIVERSE", R.FONT_BOLD, 40, color=(10, 20, 40), stroke=0,
                                        box=R.ACCENT + (255,)), 300, alpha=R.ease(t / 0.5))
                R.paste_center(frame, T(ep["screen_title"].upper(), R.FONT_BLACK,
                                        R.fit(ep["screen_title"].upper(), R.FONT_BLACK, 120, 1700, 80), max_w=1750),
                               470, alpha=R.ease((t - 0.3) / 0.5), scale=0.9 + 0.1 * R.ease((t - 0.3) / 0.6))
                if ep.get("subtitle"):
                    R.paste_center(frame, T(ep["subtitle"], R.FONT_SEMI, 56, color=R.ACCENT, stroke=4),
                                   620, alpha=R.ease((t - 0.9) / 0.5))
            elif vt == "card":
                k = R.ease((t - 0.15) / 0.5)
                R.paste_center(frame, T(v["big"], R.FONT_BLACK, R.fit(v["big"], R.FONT_BLACK, 220, 1700), color=R.ACCENT,
                                        stroke=0, max_w=1750), 400, alpha=k, scale=0.6 + 0.4 * k)
                R.paste_center(frame, T(v.get("label", ""), R.FONT_BLACK, 76, stroke=0), 600,
                               alpha=R.ease((t - 0.5) / 0.4))
                if v.get("sub"):
                    R.paste_center(frame, T(v["sub"], R.FONT_SEMI, 48, color=(185, 200, 225), stroke=0), 700,
                                   alpha=R.ease((t - 0.8) / 0.4))
            elif vt == "question":
                R.paste_center(frame, T(v.get("kicker", "TELL US IN THE COMMENTS"), R.FONT_BOLD, 40, color=(30, 20, 5),
                                        stroke=0, box=QUESTION + (255,)), 210, alpha=R.ease(t / 0.4))
                R.paste_center(frame, T(v["q"], R.FONT_BLACK, 84, stroke=0, max_w=1600), 470,
                               alpha=R.ease((t - 0.3) / 0.5), scale=0.92 + 0.08 * R.ease((t - 0.3) / 0.5))
                if v.get("sub"):
                    R.paste_center(frame, T(v["sub"], R.FONT_SEMI, 46, color=(235, 215, 170), stroke=0), 680,
                                   alpha=R.ease((t - 0.9) / 0.4))

            if s.get("headline") and vt not in ("title", "card", "question"):
                R.paste_center(frame, T(s["headline"], R.FONT_BLACK, 72, color=R.ACCENT), 120,
                               alpha=R.ease((t - 0.1) / 0.35))
            if chap_layer is not None and t < 4.0:
                a = R.ease(t / 0.4) * (1 - R.ease((t - 3.4) / 0.6))
                lay = chap_layer.copy()
                lay.putalpha(lay.getchannel("A").point(lambda q: int(q * a)))
                frame.alpha_composite(lay, (60, 60 if not s.get("headline") else 200))
            if vt == "end":
                R.paste_center(frame, T(v.get("big", "THANKS FOR WATCHING"), R.FONT_BLACK, 96, color=R.ACCENT), 150,
                               alpha=R.ease(t / 0.4))
                k = R.ease((t - 0.6) / 0.5)
                R.paste_center(frame, subscribe_button(1.3), 380, alpha=k, scale=0.8 + 0.2 * k)
                R.paste_center(frame, T("LIKE  •  COMMENT  •  SHARE", R.FONT_BLACK, 60, stroke=6), 540,
                               alpha=R.ease((t - 1.2) / 0.5))
            if s.get("subscribe") and 0.5 < t < dur - 0.3:
                k = R.ease((t - 0.5) / 0.4)
                lay = sub_btn.copy()
                lay.putalpha(lay.getchannel("A").point(lambda q: int(q * k)))
                frame.alpha_composite(lay, (W - lay.width - 60, 60))

            if vt != "title" and t < speech:
                idx = int(np.searchsorted(bounds, t, side="right") - 1)
                idx = min(max(idx, 0), len(subs) - 1)
                R.paste_center(frame, T(subs[idx], R.FONT_BLACK, 66, max_w=1700, stroke=7), 950)

            if vt not in ("title",):
                frame.alpha_composite(brand, (W - brand.width - 40, H - brand.height - 24))
            rgb = frame.convert("RGB")
            if fi < 6 and si > 0:
                rgb = Image.blend(Image.new("RGB", (W, H)), rgb, (fi + 1) / 7)
            if fi == nframes // 2:
                preview.append(rgb.resize((384, 216)))
            ff.stdin.write(rgb.tobytes())
        t0 += dur
        print(f"  segment {si + 1}/{n} [{vt}] {dur:.1f}s")
    ff.stdin.close()
    if ff.wait() != 0:
        raise SystemExit("ffmpeg failed")
    os.replace(tmp, out_mp4)

    cols = 5
    rows = math.ceil(len(preview) / cols)
    sheet = Image.new("RGB", (384 * cols, 216 * rows))
    for i, im in enumerate(preview):
        sheet.paste(im, ((i % cols) * 384, (i // cols) * 216))
    os.makedirs(os.path.join(ROOT, "previews"), exist_ok=True)
    sheet.save(os.path.join(ROOT, "previews", f"long-{slug}.jpg"), quality=85)
    open(os.path.join(out_dir, slug + ".chapters.txt"), "w").write("\n".join(chapters) + "\n")
    seen, lines = set(), []
    for artist, lic, url in R.CREDITS:
        if (artist, lic) in seen:
            continue
        seen.add((artist, lic))
        lines.append(f"{artist} ({lic})" + (f" {url}" if url and "nasa.gov" not in url else ""))
    open(os.path.join(out_dir, slug + ".credits.txt"), "w").write("\n".join(lines) + "\n")
    json.dump({"source": os.path.relpath(path, ROOT), "hash": file_hash(path), "seconds": round(total, 2),
               "rendered": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
              open(os.path.join(out_dir, slug + ".meta.json"), "w"), indent=2)
    print(f"  -> {out_mp4} ({os.path.getsize(out_mp4) / 1e6:.1f} MB, {total / 60:.2f} min)")


def file_hash(path):
    h = hashlib.sha256(open(path, "rb").read())
    h.update(open(os.path.abspath(__file__), "rb").read())
    return h.hexdigest()[:16]


def needs_render(path):
    slug = json.load(open(path))["slug"]
    meta = os.path.join(ROOT, "videos", "long", slug + ".meta.json")
    return not os.path.exists(meta) or json.load(open(meta)).get("hash") != file_hash(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    files = a.files or sorted(glob.glob(os.path.join(ROOT, "longform", "*.json")))
    if a.all:
        files = [f for f in files if needs_render(f)]
    if a.list:
        print("\n".join(files))
        return
    for f in files:
        render_long(f, offline=a.offline)


if __name__ == "__main__":
    main()
