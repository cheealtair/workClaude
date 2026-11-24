"""rawframe.py - pull still frames out of a raw take without rendering.
Run: C:/miniforge3/envs/py_claude/python.exe -I tests/e2e/film/rawframe.py <scene> <sec|beatId>[+offset] ...
A number is seconds since the take started; a beat id (e.g. Q1A5) is the moment its caption appeared, with an optional +seconds offset.
Writes tests/e2e/artifacts/film/chk/<scene>_<label>.png (1600 wide).
"""
import json, os, sys
from PIL import Image
film = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "artifacts", "film")
scene = sys.argv[1]
d = os.path.join(film, "raw", scene)
fr = json.load(open(os.path.join(d, "frames.json")))
ev = json.load(open(os.path.join(d, "events.json")))
t0 = fr["meta"]["t0"]
frames = fr["frames"]
os.makedirs(os.path.join(film, "chk"), exist_ok=True)
for a in sys.argv[2:]:
    off = 0.0
    if "+" in a:
        a, o = a.split("+"); off = float(o)
    if a.replace(".", "").isdigit():
        t = t0 + float(a) * 1000 + off * 1000
        label = a
    else:
        e = [x for x in ev if x.get("kind") == "say" and x["id"] == a][0]
        t = e["t"] + off * 1000
        label = a
    f = [x for x in frames if x["t"] <= t]
    f = f[-1] if f else frames[0]
    im = Image.open(os.path.join(d, "frames", f["file"]))
    im = im.resize((1600, round(im.height * 1600 / im.width)))
    out = os.path.join(film, "chk", "%s_%s%s.png" % (scene, label, ("+%g" % off) if off else ""))
    im.save(out)
    print(out)
