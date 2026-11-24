"""prontest_af_heart.py - render short phrases with candidate respellings (af_heart, H.1 recipe) and transcribe them offline.
Run: C:/miniforge3/envs/py_claude/python.exe -u -I tests/e2e/film/prontest_af_heart.py "phrase with {} " cand1 cand2 ...
"""
import os, sys
os.environ["HF_HUB_OFFLINE"] = "1"
import numpy as np, soundfile as sf
from kokoro import KPipeline
from faster_whisper import WhisperModel
frame = sys.argv[1]; cands = sys.argv[2:]
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "artifacts", "film", "prontest_af_heart")
pipe = KPipeline(lang_code="a")
m = WhisperModel("medium", device="cuda", compute_type="float16")
for i, c in enumerate(cands):
    text = frame.replace("{}", c)
    f = os.path.join(out, "t%d.wav" % i)
    sf.write(f, np.concatenate([np.asarray(a) for _, _, a in pipe(text, voice="af_heart", speed=1.0)]), 24000)
    segs, _ = m.transcribe(f, language="en")
    print("%-22s -> %s" % (c, " ".join(s.text.strip() for s in segs)), flush=True)
