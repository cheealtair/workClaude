"""prontest.py - render short phrases with candidate respellings (Darth_MikGeorg recipe) and transcribe them offline.
Run: C:/miniforge3/envs/py_claude/python.exe -u -I tests/e2e/film/prontest.py "phrase with {} " cand1 cand2 ...
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice as V
from kokoro import KPipeline
from faster_whisper import WhisperModel
frame = sys.argv[1]
cands = sys.argv[2:]
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "artifacts", "film", "prontest")
pipe = KPipeline(lang_code="a")
blend = V.W_MICHAEL * pipe.load_voice("am_michael") + V.W_GEORGE * pipe.load_voice("bm_george")
m = WhisperModel("medium", device="cuda", compute_type="float16")
for i, c in enumerate(cands):
    text = frame.replace("{}", c)
    raw, fin = os.path.join(out, "t_raw.wav"), os.path.join(out, "t%d.wav" % i)
    V.synth_raw(pipe, blend, text, raw); V.fx(raw, fin)
    segs, _ = m.transcribe(fin, language="en")
    print("%-22s -> %s" % (c, " ".join(s.text.strip() for s in segs)), flush=True)
