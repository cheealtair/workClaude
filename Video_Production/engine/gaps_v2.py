"""gaps_v2.py - measure the silence between the end of one narration line and the start of the next in the final v2 film.
Planned gap = next voice start - (voice start + clip length). Measured gap = from the last audible 20 ms frame of a beat to the first audible frame of the next beat
(audible = above -45 dBFS in the decoded mix). Run: C:/miniforge3/envs/py_claude/python.exe -I tests/e2e/film/gaps_v2.py
"""
import json, os, subprocess, tempfile, wave
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
FILM = os.path.join(ROOT, "tests", "e2e", "artifacts", "film")
FF = "C:/miniforge3/envs/rm_genai/Library/bin/ffmpeg.exe"
mp4 = os.path.join(ROOT, "docs", "film", "MiningOpsApp_walkthrough_af_heart.mp4")
tmp = os.path.join(tempfile.gettempdir(), "film_gaps.wav")
subprocess.run([FF, "-y", "-v", "error", "-i", mp4, "-vn", "-ac", "1", "-ar", "16000", tmp], check=True)
w = wave.open(tmp); sr = w.getframerate()
x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768
N = int(0.02 * sr); n = len(x) // N
db = 20 * np.log10(np.maximum(np.sqrt((x[:n * N].reshape(n, N) ** 2).mean(axis=1)), 1e-9))
aud = db > -45
T = json.load(open(os.path.join(FILM, "final_v2", "timeline.json")))["timeline"]
rows = []
for i, t in enumerate(T):
    a = int(t["voice_at_s"] / 0.02); z = int((t["voice_at_s"] + t["audio_ms"] / 1000) / 0.02) + 2
    nxt = T[i + 1] if i + 1 < len(T) else None
    b = int(nxt["voice_at_s"] / 0.02) if nxt else min(n, z + 100)
    seg = aud[a:min(b, n)]
    idx = np.nonzero(seg)[0]
    if not len(idx): rows.append({"id": t["id"], "error": "silent"}); continue
    first, last = a + idx[0], a + idx[-1]
    nseg = aud[b:min(b + 150, n)]; nidx = np.nonzero(nseg)[0]
    nfirst = b + nidx[0] if len(nidx) else None
    planned = (nxt["voice_at_s"] - (t["voice_at_s"] + t["audio_ms"] / 1000)) if nxt else None
    measured = ((nfirst - last - 1) * 0.02) if nfirst is not None and nxt else None
    rows.append({"id": t["id"], "scene": t["scene"], "planned_gap_s": None if planned is None else round(planned, 2), "measured_gap_s": None if measured is None else round(measured, 2)})
m = [r["measured_gap_s"] for r in rows if r.get("measured_gap_s") is not None]
p = [r["planned_gap_s"] for r in rows if r.get("planned_gap_s") is not None]
cross = [r["measured_gap_s"] for r in rows if r.get("measured_gap_s") is not None]
json.dump({"rows": rows}, open(os.path.join(FILM, "final_v2", "gaps.json"), "w"), indent=1)
q = lambda v, f: round(float(np.percentile(v, f)), 2)
print("planned gap (clip end to next clip start) s: min %.2f median %.2f p90 %.2f max %.2f mean %.2f" % (min(p), np.median(p), q(p, 90), max(p), np.mean(p)))
print("measured audible gap s: min %.2f median %.2f p90 %.2f max %.2f mean %.2f" % (min(m), np.median(m), q(m, 90), max(m), np.mean(m)))
big = sorted([(r["measured_gap_s"], r["id"]) for r in rows if r.get("measured_gap_s") is not None and r["measured_gap_s"] > 2.0], reverse=True)
print("gaps over 2.0 s:", big)
