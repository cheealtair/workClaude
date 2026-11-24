"""wcheck.py - offline faster_whisper transcription check of rendered voice clips against the beat text.
Run: C:/miniforge3/envs/py_claude/python.exe -I tests/e2e/film/wcheck.py <beats.json> <voice_dir> [id,id,...]
Reports word-level agreement (case and punctuation ignored). Codes respelled in pronunciations.json are expected to differ.
"""
import json
import os
import re
import sys

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
from faster_whisper import WhisperModel  # noqa: E402

beats = json.load(open(sys.argv[1], encoding="utf-8"))["beats"]
vdir = sys.argv[2]
only = sys.argv[3].split(",") if len(sys.argv) > 3 else None
m = WhisperModel("medium", device="cpu", compute_type="int8")
norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower().replace("-", " ")).split()
for b in beats:
    if only and b["id"] not in only:
        continue
    f = os.path.join(vdir, b["id"] + ".wav")
    if not os.path.exists(f):
        continue
    segs, _ = m.transcribe(f, language="en")
    t = " ".join(s.text for s in segs)
    a, c = norm(t), norm(b["text"])
    same = sum(1 for x, y in zip(a, c) if x == y)
    print(b["id"], "exact=%s" % (a == c), "words heard %d, words written %d, aligned equal %d" % (len(a), len(c), same))
    print("  heard:   ", t.strip())
    print("  written: ", b["text"])
