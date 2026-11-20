#!/usr/bin/env python3
"""Print the YouTube post data (JSON) for one queue item.

usage: python tools/postdata.py ITEM_ID      e.g. ep041  or  long-solar-system
Fields: title, text (description), tags, publishAt, url (raw GitHub URL pinned to the commit of the video file).
"""
import glob, html, json, subprocess, sys

REPO = "https://raw.githubusercontent.com/nextstopuniversedaily-sketch/next-stop-universe"
SUB = "🔔 Subscribe for a new stop every day: https://www.youtube.com/@NextStopUniverse-v5v?sub_confirmation=1"
EXTRA_TAGS = ["nasa", "space documentary", "astronomy for beginners", "science for kids", "cosmos", "outer space"]

def sha(path):
    return subprocess.check_output(["git", "log", "-1", "--format=%H", "--", path], text=True).strip()

def credits(n):
    try:
        lines = [html.unescape(l.strip()) for l in open(f"videos/ep{n:03d}.credits.txt") if l.strip()]
    except FileNotFoundError:
        return ["NASA (public domain)"]
    return lines

def episode(n):
    d = json.load(open(glob.glob(f"episodes/ep{n:03d}-*.json")[0]))
    text = d["description"].replace("Images: NASA (public domain)",
                                    "Image credits:\n" + "\n".join("• " + c for c in credits(n)))
    text = text.replace("Follow so you don't miss a stop. A new episode every day.", SUB)
    tags = list(dict.fromkeys(d["tags"] + EXTRA_TAGS))
    path = f"videos/ep{n:03d}.mp4"
    return {"title": d["yt_title"], "text": text[:4900], "tags": tags[:30], "url": f"{REPO}/{sha(path)}/{path}"}

def original(name):
    """Original long-form video written in longform/<name>.json (not a compilation)."""
    d = json.load(open(f"longform/{name}.json"))
    chapters = open(f"videos/long/{name}.chapters.txt").read().strip()
    try:
        creds = [html.unescape(l.strip()) for l in open(f"videos/long/{name}.credits.txt") if l.strip()]
    except FileNotFoundError:
        creds = ["NASA (public domain)"]
    qs = "\n".join("• " + q for q in d.get("questions", []))
    text = (d["intro"] + "\n\n⏱️ Chapters\n" + chapters +
            ("\n\n💬 Tell us in the comments:\n" + qs if qs else "") +
            "\n\n" + SUB +
            "\n👍 If you enjoyed it, a like helps more people find the channel." +
            "\n📤 Share it with someone who loves the night sky: a grandchild, a friend, a whole family." +
            "\nShort daily episodes: start from Episode 1 \"Leaving Earth\" on the channel.\n\n" + d["hashtags"] +
            "\n\nNarration: AI voice\nImage credits:")
    for c in creds:
        if len(text) + len(c) + 3 > 4800:
            text += "\n• and other NASA, ESA and Wikimedia Commons contributors"
            break
        text += "\n• " + c
    path = f"videos/long/{name}.mp4"
    tags, total = [], 0
    for t in d["tags"]:
        if len(tags) < 30 and total + len(t) + 3 <= 480:
            tags.append(t)
            total += len(t) + 3
    return {"title": d["yt_title"], "text": text[:4900], "tags": tags, "url": f"{REPO}/{sha(path)}/{path}"}

def long(name):
    import os
    if os.path.exists(f"longform/{name}.json"):
        return original(name)
    q = {i["id"]: i for i in json.load(open("schedule/queue.json"))}[f"long-{name}"]
    chapters = open(f"videos/long/{name}.chapters.txt").read().strip()
    eps = [int(l.split("Ep. ")[1].split(":")[0]) for l in chapters.splitlines()]
    creds = []
    for n in eps:
        for c in credits(n):
            if c not in creds:
                creds.append(c)
    head = (q["intro"] + "\n\n⏱️ Chapters\n" + chapters + "\n\n" + SUB +
            "\nShort daily episodes: start from Episode 1 \"Leaving Earth\" on the channel.\n\n" + q["hashtags"] +
            "\n\nNarration: AI voice\nImage credits:")
    text = head
    for c in creds:
        if len(text) + len(c) + 3 > 4800:
            text += "\n• and other NASA, ESA and Wikimedia Commons contributors"
            break
        text += "\n• " + c
    path = f"videos/long/{name}.mp4"
    return {"title": q["title"], "text": text[:4900], "tags": q["tags"][:30], "url": f"{REPO}/{sha(path)}/{path}"}

item = sys.argv[1]
import datetime
for i in json.load(open("schedule/queue.json")):
    if i["id"] == item and i.get("notBefore", "") > datetime.date.today().isoformat():
        sys.exit(f"SKIP {item}: not before {i['notBefore']} (another task may upload it first); leave it pending and continue with the next item")
out = episode(int(item[2:])) if item.startswith("ep") else long(item[5:])
for i in json.load(open("schedule/queue.json")):
    if i["id"] == item:
        out["publishAt"] = i["publishAt"]
print(json.dumps(out, ensure_ascii=False, indent=1))
