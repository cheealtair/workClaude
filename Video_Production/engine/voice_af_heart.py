"""af_heart offline narration synthesis (Kokoro), one WAV per beat. Film version 2.

Recipe: Video_Production.md section 4.5 H.1
  pipe = KPipeline(lang_code="a"); pipe(text, voice="af_heart", speed=1.0); concatenate the chunks; 24000 Hz WAV; NO post-processing.
Only the synthesis text is respelled (tests/e2e/film/pronunciations.json); the beat text is never changed.

Run (offline):
  C:/miniforge3/envs/py_claude/python.exe -I tests/e2e/film/voice_af_heart.py --beats tests/e2e/artifacts/film/beats.json --out tests/e2e/artifacts/film/voice_af_heart [--only ID,ID] [--pron path]
"""
import os

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import argparse
import json
import re
import socket
import subprocess
import sys
import time


def _blocked(*a, **k):
    raise RuntimeError("network access blocked by voice_af_heart.py (offline guard)")


socket.socket.connect = _blocked
socket.socket.connect_ex = _blocked
socket.create_connection = _blocked

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
FFPROBE = "C:/miniforge3/envs/rm_genai/Library/bin/ffprobe.exe"
VOICE = "af_heart"
SPEED = 1.0
CPS_MIN = 8.0
CPS_MAX = 24.0
MAX_TRIES = 3


def apply_pron(text, pron):
    for written, spoken in sorted(pron.items(), key=lambda kv: -len(kv[0])):
        text = re.sub(r"\b%s\b" % re.escape(written), spoken, text)
    return text


def probe_duration(path):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--beats", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--pron", default=os.path.join(HERE, "pronunciations.json"))
    args = ap.parse_args()
    beats = json.load(open(args.beats, encoding="utf-8"))["beats"]
    if args.only:
        wanted = set(args.only.split(","))
        beats = [b for b in beats if b["id"] in wanted]
    os.makedirs(args.out, exist_ok=True)
    pron = json.load(open(args.pron, encoding="utf-8")) if os.path.exists(args.pron) else {}

    from kokoro import KPipeline
    pipe = KPipeline(lang_code="a")

    log_path = os.path.join(args.out, "voice_log.json")
    log = {}
    if os.path.exists(log_path):
        log = {e["id"]: e for e in json.load(open(log_path, encoding="utf-8"))}
    total = 0.0
    for b in beats:
        bid, text = b["id"], b["text"]
        spoken = apply_pron(text, pron)
        out = os.path.join(args.out, bid + ".wav")
        entry = {"id": bid, "chars": len(text), "duration_s": 0.0, "cps": 0.0, "ok": False, "tries": 0, "voice": VOICE, "speed": SPEED}
        for attempt in range(1, MAX_TRIES + 1):
            entry["tries"] = attempt
            try:
                chunks = [np.asarray(a) for _, _, a in pipe(spoken, voice=VOICE, speed=SPEED)]
                wave = np.concatenate(chunks)
                sf.write(out, wave, 24000)
                dur = probe_duration(out)
            except Exception as e:
                print("  %s try %d error: %s" % (bid, attempt, e))
                time.sleep(1)
                continue
            cps = len(text) / dur if dur > 0 else 0.0
            entry["duration_s"] = round(dur, 3)
            entry["cps"] = round(cps, 2)
            if CPS_MIN <= cps <= CPS_MAX:
                entry["ok"] = True
                break
            print("  %s try %d implausible: %.1f s, %.1f chars/s" % (bid, attempt, dur, cps))
        total += entry["duration_s"]
        print("%s: %d chars, %.2f s, %.1f cps, ok=%s" % (bid, entry["chars"], entry["duration_s"], entry["cps"], entry["ok"]), flush=True)
        log[bid] = entry
        json.dump(list(log.values()), open(log_path, "w", encoding="utf-8"), indent=1)
    print("total this run: %.2f s" % total)
    return 0 if all(e["ok"] for e in log.values()) else 2


if __name__ == "__main__":
    sys.exit(main())
