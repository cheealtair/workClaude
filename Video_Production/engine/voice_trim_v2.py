"""voice_trim_v2.py - measure where the speech starts and ends inside each af_heart clip (non-destructive: the WAV files are never changed).
Kokoro clips carry about 0.3 s of silence before and 0.5 s after the speech. The mix (post_v2.js) places only the window [trim_start, trim_end] of each clip,
so that the planned 0.4 s lead-in and 0.3 s tail are the real silences. Window = first and last frame above -48 dBFS (10 ms frames), 30 ms margin before, 60 ms after.
Run: C:/miniforge3/envs/py_claude/python.exe -I tests/e2e/film/voice_trim_v2.py
"""
import glob, json, os
import numpy as np
import soundfile as sf
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "artifacts", "film", "voice_af_heart")
out = {}
for f in sorted(glob.glob(os.path.join(d, "*.wav"))):
    x, sr = sf.read(f); N = int(0.01 * sr); n = len(x) // N
    db = 20 * np.log10(np.maximum(np.sqrt((x[:n * N].reshape(n, N) ** 2).mean(axis=1)), 1e-9))
    idx = np.nonzero(db > -48)[0]
    s = max(0.0, idx[0] * 0.01 - 0.03); e = min(len(x) / sr, (idx[-1] + 1) * 0.01 + 0.06)
    out[os.path.basename(f)[:-4]] = {"clip_ms": int(round(len(x) / sr * 1000)), "trim_start_ms": int(round(s * 1000)), "trim_end_ms": int(round(e * 1000)), "speech_ms": int(round((e - s) * 1000))}
json.dump(out, open(os.path.join(d, "voice_trim.json"), "w"), indent=1)
sp = [v["speech_ms"] for v in out.values()]; cl = [v["clip_ms"] for v in out.values()]
print("clips", len(out), "full %.1f s, speech windows %.1f s" % (sum(cl) / 1000, sum(sp) / 1000))
