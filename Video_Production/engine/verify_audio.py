"""verify_audio.py - proves every voice clip is audible and sits in its beat window of the final film.
Run: C:/miniforge3/envs/py_claude/python.exe -I tests/e2e/film/verify_audio.py <film.mp4> <timeline.json> <out.json>
Decodes the film's audio, then for each beat compares the RMS inside [voice_at, voice_at + clip] with the RMS in the 0.35 s before it
and with the RMS in the 0.5 s after the clip ends; a placed clip is louder than both. Prints the overall level too.
"""
import json, os, subprocess, sys, tempfile, wave
import numpy as np
FF = "C:/miniforge3/envs/rm_genai/Library/bin/ffmpeg.exe"
film, tl, out = sys.argv[1:4]
tmp = os.path.join(tempfile.gettempdir(), "film_audio_check.wav")
subprocess.run([FF, "-y", "-v", "error", "-i", film, "-vn", "-ac", "1", "-ar", "16000", tmp], check=True)
w = wave.open(tmp)
sr = w.getframerate()
x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
db = lambda a: 20 * np.log10(max(np.sqrt(np.mean(a * a)) if len(a) else 1e-9, 1e-9))
T = json.load(open(tl))["timeline"]
rows, bad = [], []
for b in T:
    a = int(b["voice_at_s"] * sr); z = int((b["voice_at_s"] + b["audio_ms"] / 1000) * sr)
    inside = db(x[a:z]); before = db(x[max(0, a - int(0.35 * sr)):a]); after = db(x[z:z + int(0.5 * sr)])
    ok = inside > -40 and inside > before + 10
    rows.append({"id": b["id"], "voice_at_s": b["voice_at_s"], "clip_s": b["audio_ms"] / 1000, "rms_inside_db": round(inside, 1), "rms_before_db": round(before, 1), "rms_after_db": round(after, 1), "ok": bool(ok)})
    if not ok:
        bad.append(b["id"])
res = {"duration_s": round(len(x) / sr, 2), "overall_rms_db": round(db(x), 1), "peak": round(float(np.max(np.abs(x))), 3), "beats": len(rows), "not_ok": bad, "rows": rows}
json.dump(res, open(out, "w"), indent=1)
print("audio %.1f s, overall RMS %.1f dBFS, peak %.3f, beats %d, placed and audible %d, NOT ok: %s" % (res["duration_s"], res["overall_rms_db"], res["peak"], len(rows), len(rows) - len(bad), bad))
