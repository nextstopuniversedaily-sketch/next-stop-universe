# Next Stop: Universe

Daily space Shorts for the YouTube channel **Next Stop: Universe** (@NextStopUniverse-v5v).

## How it works

1. **Scripts** live in `episodes/epNNN-name.json`. Each has a title, YouTube metadata and a list of segments (narration + visual).
2. **Pushing** a new or changed episode file starts the GitHub Action `Render episodes`.
3. The Action renders each new episode for free:
   - voice: [Kokoro](https://github.com/thewh1teagle/kokoro-onnx) AI voice, run locally
   - images: [NASA Image and Video Library](https://images.nasa.gov) (public domain), slow pan/zoom
   - animated number cards, captions and branding drawn with Pillow, encoded with ffmpeg
4. Finished videos land in `videos/epNNN.mp4`, with a frame contact sheet in `previews/epNNN.jpg`.
5. Videos are then scheduled on YouTube through vidIQ, after approval.

## Segment visuals

| `visual.type` | What it shows |
|---|---|
| `title` | NASA image + "EPISODE N" + big title + `subtitle` |
| `image` | NASA image (from `query`, or an exact `nasa_id`; `pick` chooses another search result) + optional `headline` |
| `card` | Starfield with a big animated number: `big`, `label`, `sub` |
| `end` | NASA image + "NEXT STOP: X" + follow button |

## Run locally

```bash
pip install -r pipeline/requirements.txt
# put kokoro-v1.0.int8.onnx and voices-v1.0.bin in models/
python pipeline/render.py episodes/ep003-mars.json          # with NASA images
python pipeline/render.py --offline episodes/ep003-mars.json  # without internet
```

Fonts: Inter (SIL Open Font License).
