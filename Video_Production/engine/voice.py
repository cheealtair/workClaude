"""Darth_MikGeorg offline narration synthesis (Kokoro), one WAV per beat.

Recipe copied from VoiceAI/kokoro_blend.py and Video_Production.md 4.5 H.2:
  KPipeline(lang_code="a"); blend = 0.7 * am_michael + 0.3 * bm_george; speed 0.88;
  raw 24 kHz WAV, then the ffmpeg chain below, output 24000 Hz mono.

Run (offline, no network):
  C:/miniforge3/envs/py_claude/python.exe voice.py --beats beats.json --out DIR [--first N] [--only ID,ID]

beats.json: {"beats": [{"id": "...", "text": "..."}, ...]}  (text = voice text = caption text)
Optional pronunciations.json beside this file: {"written": "spoken respelling"}; applied to the
synthesis text only, never to captions.
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

# Hard guard: any attempt to open a network connection raises. Loopback is not needed.
def _blocked(*a, **k):
    raise RuntimeError("network access blocked by voice.py (offline guard)")

socket.socket.connect = _blocked
socket.socket.connect_ex = _blocked
socket.create_connection = _blocked

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
FFMPEG = "C:/miniforge3/envs/rm_genai/Library/bin/ffmpeg.exe"
FFPROBE = "C:/miniforge3/envs/rm_genai/Library/bin/ffprobe.exe"

W_MICHAEL = 0.7
W_GEORGE = 0.3
SPEED = 0.88
SEMITONES = -1.5
EQ_GAIN_DB = 1.5
ECHO = "aecho=0.8:0.9:30:0.06"
PITCH_RATE = int(round(24000 * 2 ** (SEMITONES / 12.0)))
PITCH_TEMPO = 2 ** (-SEMITONES / 12.0)
FX_CHAIN = ",".join([
    "asetrate=%d" % PITCH_RATE,
    "aresample=24000",
    "atempo=%.5f" % PITCH_TEMPO,
    "equalizer=f=115:width_type=h:width=70:g=%.1f" % EQ_GAIN_DB,
    "acompressor=threshold=-18dB:ratio=2:attack=20:release=250:makeup=2",
    ECHO,
    "loudnorm=I=-16:TP=-1.5:LRA=11",
])

# Plausibility bounds, characters per second (4.4 uses 8-25 for edge-tts). This voice is slowed
# (speed 0.88), so the real rate is lower; the lower bound stays 8 to catch truncation and the
# upper bound drops to 20 to catch dropped text. Measured rate is logged either way.
CPS_MIN = 8.0
CPS_MAX = 20.0
MAX_TRIES = 3


def load_pron():
    path = os.path.join(HERE, "pronunciations.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def apply_pron(text, pron):
    for written, spoken in sorted(pron.items(), key=lambda kv: -len(kv[0])):
        text = re.sub(r"\b%s\b" % re.escape(written), spoken, text)
    return text


def probe_duration(path):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip())


def synth_raw(pipe, blend, text, raw_path):
    chunks = [np.asarray(a) for _, _, a in pipe(text, voice=blend, speed=SPEED)]
    wave = np.concatenate(chunks)
    sf.write(raw_path, wave, 24000)


def fx(raw_path, out_path):
    cmd = [FFMPEG, "-y", "-v", "error", "-i", raw_path, "-af", FX_CHAIN,
           "-ar", "24000", "-ac", "1", out_path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg failed: " + r.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--beats", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--first", type=int, default=0)
    ap.add_argument("--only", default="")
    args = ap.parse_args()

    with open(args.beats, "r", encoding="utf-8") as f:
        beats = json.load(f)["beats"]
    if args.only:
        wanted = set(args.only.split(","))
        beats = [b for b in beats if b["id"] in wanted]
    if args.first:
        beats = beats[:args.first]
    os.makedirs(args.out, exist_ok=True)
    pron = load_pron()

    from kokoro import KPipeline
    pipe = KPipeline(lang_code="a")
    michael = pipe.load_voice("am_michael")
    george = pipe.load_voice("bm_george")
    blend = W_MICHAEL * michael + W_GEORGE * george

    log_path = os.path.join(args.out, "voice_log.json")
    log = {}
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            log = {e["id"]: e for e in json.load(f)}

    total = 0.0
    for b in beats:
        bid, text = b["id"], b["text"]
        spoken = apply_pron(text, pron)
        out = os.path.join(args.out, bid + ".wav")
        raw = os.path.join(args.out, bid + "_raw.wav")
        entry = {"id": bid, "chars": len(text), "duration_s": 0.0, "cps": 0.0, "ok": False, "tries": 0}
        for attempt in range(1, MAX_TRIES + 1):
            entry["tries"] = attempt
            try:
                synth_raw(pipe, blend, spoken, raw)
                fx(raw, out)
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
        if os.path.exists(raw):
            os.remove(raw)
        total += entry["duration_s"]
        print("%s: %d chars, %.2f s, %.1f cps, ok=%s" % (bid, entry["chars"], entry["duration_s"], entry["cps"], entry["ok"]))
        log[bid] = entry
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(list(log.values()), f, indent=1)
    print("total this run: %.2f s" % total)
    return 0 if all(e["ok"] for e in log.values()) else 2


if __name__ == "__main__":
    sys.exit(main())
