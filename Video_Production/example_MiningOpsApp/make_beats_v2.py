"""make_beats_v2.py - beats_v2.json: copy of beats.json with af_heart clip lengths and the v2 holds. Text fields are untouched.
Hold = speech window of the clip (silence at both ends of the WAV trimmed, WAV untouched) + 0.4 s lead-in + 0.3 s tail. An app beat is never planned below what its action needs:
  intent beat (caption first, actions run while the line is spoken): max(hold, 1.0 s + act + 0.8 s)
  landing beat with a click (action first, then the line): act + 0.6 s paint + hold
  landing beat without a click (scroll or spot after the caption): max(hold, 0.9 s + act + 0.6 s)
Run: C:/miniforge3/envs/py_claude/python.exe -I tests/e2e/film/make_beats_v2.py
"""
import json, os, copy
film = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "artifacts", "film")
d = json.load(open(os.path.join(film, "beats.json"), encoding="utf-8"))
log = {e["id"]: e for e in json.load(open(os.path.join(film, "voice_af_heart", "voice_log.json")))}
LEAD, TAIL = 400, 300
trim = json.load(open(os.path.join(film, "voice_af_heart", "voice_trim.json")))   # speech window of every clip (voice_trim_v2.py); the WAVs are untouched
t = 0; vt = 0
for b in d["beats"]:
    e = log[b["id"]]; assert e["ok"], b["id"]
    b["audio_ms_v1"] = b["audio_ms"]; b["planned_ms_v1"] = b["planned_ms"]
    tr = trim[b["id"]]
    a = tr["speech_ms"]; act = int(round(b.get("act_s", 0) * 1000))
    hold = a + LEAD + TAIL
    steps = (b.get("action") or {}).get("steps", [])
    click = any(s.get("do") in ("click", "wait_for") for s in steps)
    if b["kind"] == "slide": p = hold
    elif b["intent_or_landing"] == "intent": p = max(hold, 1000 + act + 800)
    elif click: p = act + 600 + hold
    else: p = max(hold, 900 + act + 600)
    b["clip_ms"] = tr["clip_ms"]; b["trim_start_ms"] = tr["trim_start_ms"]; b["trim_end_ms"] = tr["trim_end_ms"]
    b["audio_ms"] = a; b["hold_ms"] = hold; b["planned_ms"] = p; b["start_ms"] = t; b["voice"] = "af_heart"
    t += p; vt += a
d["voice"] = "af_heart (Kokoro, offline, H.1, speed 1.0, no post-processing)"
d["title"] = "MiningOpsApp full narrated walkthrough, version 2 (af_heart, no captions, shorter pauses)"
d["caption_strip_css_px"] = 0
d["total_planned_s"] = round(t / 1000, 1); d["total_voice_s"] = round(vt / 1000, 1); d["density_planned"] = round(vt / t, 3)
json.dump(d, open(os.path.join(film, "beats_v2.json"), "w", encoding="utf-8"), indent=1)
v1 = json.load(open(os.path.join(film, "beats.json"), encoding="utf-8"))["beats"]
assert [b["text"] for b in v1] == [b["text"] for b in d["beats"]] and [b["id"] for b in v1] == [b["id"] for b in d["beats"]]
print("beats", len(d["beats"]), "voice %.1f s planned %.1f s density %.1f%%" % (vt / 1000, t / 1000, 100 * vt / t), "text identical to beats.json: True")
