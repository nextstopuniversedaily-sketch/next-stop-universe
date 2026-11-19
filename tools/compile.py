#!/usr/bin/env python3
"""Build a horizontal long-form compilation (1920x1080) from rendered vertical episodes.

usage: python tools/compile.py NAME EP [EP ...]
writes videos/long/NAME.mp4 and videos/long/NAME.chapters.txt (YouTube chapter lines)
"""
import json, glob, os, subprocess, sys, tempfile

name, eps = sys.argv[1], [int(x) for x in sys.argv[2:]]
os.makedirs("videos/long", exist_ok=True)
tmp = tempfile.mkdtemp()
parts, chapters, t = [], [], 0.0
for n in eps:
    src = f"videos/ep{n:03d}.mp4"
    meta = json.load(open(glob.glob(f"episodes/ep{n:03d}-*.json")[0]))
    out = os.path.join(tmp, f"{n:03d}.mp4")
    vf = ("[0:v]split[a][b];[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
          "boxblur=30:3,eq=brightness=-0.15[bg];[b]scale=-2:1080[fg];[bg][fg]overlay=(W-w)/2:0,fps=30,format=yuv420p[v]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", vf, "-map", "[v]", "-map", "0:a",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "27", "-maxrate", "1100k", "-bufsize", "2200k",
                    "-c:a", "aac", "-b:a", "96k", "-ar", "48000", "-ac", "1", out], check=True)
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]))
    m, s = divmod(int(t), 60)
    chapters.append(f"{m}:{s:02d} Ep. {n}: {meta['title']}")
    parts.append(out); t += d
lst = os.path.join(tmp, "list.txt")
open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                "-movflags", "+faststart", f"videos/long/{name}.mp4"], check=True)
open(f"videos/long/{name}.chapters.txt", "w").write("\n".join(chapters) + "\n")
print(name, f"{t/60:.1f} min", os.path.getsize(f"videos/long/{name}.mp4") // 1_000_000, "MB")
