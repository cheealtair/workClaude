"""update_beats.py - write measured clip durations into beats.json and recompute planned seconds.
planned_ms = max(audio + 400 lead + 1200 tail, stage-1 plan with its voice estimate replaced by the measured clip):
  slide and landing beats keep their dwell (and any action extras of the stage-1 model); intent beats keep max(voice + 1.6 s, action + 1.0 s).
Run: C:/miniforge3/envs/py_claude/python.exe -I tests/e2e/film/update_beats.py
"""
import json, os
film = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "artifacts", "film")
p = os.path.join(film, "beats.json")
d = json.load(open(p, encoding="utf-8"))
log = {e["id"]: e for e in json.load(open(os.path.join(film, "voice", "voice_log.json")))}
t = 0
voice_total = 0
for b in d["beats"]:
    e = log[b["id"]]
    assert e["ok"], b["id"]
    if "planned_ms_stage1" not in b:
        b["planned_ms_stage1"] = b["planned_ms"]
        b["est_audio_ms_stage1"] = b["est_audio_ms"]
    audio = int(round(e["duration_s"] * 1000))
    nonvoice = b["planned_ms_stage1"] - b["est_audio_ms_stage1"]
    b["audio_ms"] = audio
    b["chars"] = e["chars"]
    b["planned_ms"] = max(audio + 400 + 1200, audio + nonvoice)
    b["start_ms"] = t
    t += b["planned_ms"]
    voice_total += audio
d["total_planned_s"] = round(t / 1000, 1)
d["total_voice_s"] = round(voice_total / 1000, 1)
d["density_planned"] = round(voice_total / t, 3)
json.dump(d, open(p, "w", encoding="utf-8"), indent=1)
print("beats", len(d["beats"]), "voice %.1f s" % (voice_total / 1000), "planned %.1f s" % (t / 1000), "density %.1f%%" % (100 * voice_total / t))
