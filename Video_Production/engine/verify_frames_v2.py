"""verify_frames_v2.py - extract a frame inside every beat of the v2 film (middle of the voice clip) and test for leftovers of v1:
a caption strip (dark band with a teal top border at the bottom), the progress bar, and an empty band at the bottom. Writes contact sheets.
Run: C:/miniforge3/envs/py_claude/python.exe -I tests/e2e/film/verify_frames_v2.py
"""
import json, os, subprocess
import numpy as np
from PIL import Image, ImageDraw
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
FILM = os.path.join(ROOT, "tests", "e2e", "artifacts", "film")
FF = "C:/miniforge3/envs/rm_genai/Library/bin/ffmpeg.exe"
mp4 = os.path.join(ROOT, "docs", "film", "MiningOpsApp_walkthrough_af_heart.mp4")
out = os.path.join(FILM, "verify_v2"); os.makedirs(out, exist_ok=True)
T = json.load(open(os.path.join(FILM, "final_v2", "timeline.json")))["timeline"]
rows = []
for i, b in enumerate(T):
    t = b["voice_at_s"] + b["audio_ms"] / 2000
    f = os.path.join(out, "f_%02d_%s.png" % (i, b["id"]))
    subprocess.run([FF, "-y", "-v", "error", "-ss", "%.3f" % t, "-i", mp4, "-frames:v", "1", f], check=True)
    a = np.asarray(Image.open(f).convert("RGB")).astype(int)
    H = a.shape[0]
    bottom = a[H - 140:]
    teal = ((abs(bottom[:, :, 0] - 20) < 25) & (abs(bottom[:, :, 1] - 184) < 25) & (abs(bottom[:, :, 2] - 166) < 25)).sum(axis=1)
    bar = ((abs(bottom[:, :, 0] - 94) < 12) & (abs(bottom[:, :, 1] - 234) < 12) & (abs(bottom[:, :, 2] - 212) < 12)).sum(axis=1)
    strip_line = int((teal > 0.9 * a.shape[1]).sum())          # a full-width teal rule = caption strip border
    bar_px = int(bar.max())
    last = a[H - 8:]                                             # the last 8 rows: a flat single colour all across = an empty band
    flat = bool(last.std(axis=(0, 1)).max() < 2.0)
    band = a[H - 125:]
    band_flat = bool(band.std() < 3.0)
    rows.append({"id": b["id"], "t": round(t, 2), "strip_line_rows": strip_line, "bar_px": bar_px, "bottom8_flat": flat, "bottom125_flat": band_flat})
json.dump(rows, open(os.path.join(out, "frame-checks.json"), "w"), indent=1)
bad = [r for r in rows if r["strip_line_rows"] or r["bar_px"] > 40]
print("frames", len(rows), "with strip line or progress bar:", [r["id"] for r in bad])
print("bottom 8 rows one flat colour:", [r["id"] for r in rows if r["bottom8_flat"]])
print("bottom 125 rows flat:", [r["id"] for r in rows if r["bottom125_flat"]])
# contact sheets: 6 frames each (2 x 3), each tile 960 x 540
files = sorted(f for f in os.listdir(out) if f.startswith("f_"))
for s in range(0, len(files), 6):
    sheet = Image.new("RGB", (1920, 1620), (40, 40, 40)); d = ImageDraw.Draw(sheet)
    for k, f in enumerate(files[s:s + 6]):
        im = Image.open(os.path.join(out, f)).convert("RGB").resize((960, 540))
        x, y = (k % 2) * 960, (k // 2) * 540
        sheet.paste(im, (x, y)); d.rectangle([x, y, x + 120, y + 18], fill=(0, 0, 0)); d.text((x + 3, y + 3), f[2:-4], fill=(255, 255, 0))
    sheet.save(os.path.join(out, "sheet_%02d.png" % (s // 6)))
print("sheets", (len(files) + 5) // 6)
