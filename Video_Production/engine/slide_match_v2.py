"""slide_match_v2.py - every slide beat of the v2 film (frame at mid-voice) is correlated with all 48 real slide PNGs; the best match must be the planned slide.
The slide now fills the whole 1920x1080 frame (no caption strip). Run: C:/miniforge3/envs/py_claude/python.exe -I tests/e2e/film/slide_match_v2.py
"""
import json, os
import numpy as np
from PIL import Image
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
FILM = os.path.join(ROOT, "tests", "e2e", "artifacts", "film")
beats = {b["id"]: b for b in json.load(open(os.path.join(FILM, "beats_v2.json"), encoding="utf-8"))["beats"]}
T = json.load(open(os.path.join(FILM, "final_v2", "timeline.json")))["timeline"]
load = lambda p: np.asarray(Image.open(p).convert("L").resize((480, 270), Image.LANCZOS)).astype(float)
slides = {n: load(os.path.join(FILM, "slides", "slide-%02d.png" % n)) for n in range(1, 49)}
corr = lambda a, b: float(np.corrcoef(a.ravel(), b.ravel())[0, 1])
rows, bad = [], []
for i, t in enumerate(T):
    b = beats[t["id"]]
    if b["kind"] != "slide": continue
    f = load(os.path.join(FILM, "verify_v2", "f_%02d_%s.png" % (i, t["id"])))
    sc = sorted(((corr(f, s), n) for n, s in slides.items()), reverse=True)
    ok = sc[0][1] == b["source"]["slide"]
    rows.append({"beat": t["id"], "planned": b["source"]["slide"], "best": sc[0][1], "corr": round(sc[0][0], 4), "second": round(sc[1][0], 4), "ok": ok})
    if not ok: bad.append(t["id"])
json.dump({"rows": rows, "bad": bad}, open(os.path.join(FILM, "final_v2", "slide-check.json"), "w"), indent=1)
print("slide beats", len(rows), "matched", len(rows) - len(bad), "min corr", min(r["corr"] for r in rows), "bad", bad)
