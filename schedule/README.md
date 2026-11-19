# Upload queue

`queue.json` is processed by the daily uploader scheduled task (21:20 UTC, max 10 uploads/day,
YouTube's limit for this channel). Items run in list order; `notBefore` items are skipped until that date.

- Shorts air daily at 07:00 America/Mexico_City (Ep N = 2026-11-10 + N days).
- Long-form compilations (`videos/long/*.mp4`, built with `tools/compile.py`) air at 18:00.
- `python3 tools/postdata.py <id>` prints title, description, tags, publishAt and the pinned raw URL.
