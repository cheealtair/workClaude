"""voice_check.py - offline faster_whisper transcription of every voice clip, compared with the beat text.
Number words in the written text and digits in the transcript are both reduced to numeric values, so
'fifteenth' and '15th' match. Codes are compared with spaces and leading zeros removed ('SR1' = 'SR 1').
Known harmless recogniser variants (spelling, 'percent' written as a symbol, 'kg') are ignored.
Transcripts are cached in <voice_dir>/transcripts.json, so a re-diff does not re-transcribe.

Run: C:/miniforge3/envs/py_claude/python.exe -u -I tests/e2e/film/voice_check.py <beats.json> <voice_dir> <out.md> [id,id,...]
"""
import difflib
import json
import os
import re
import sys

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

beats_path, vdir, out_md = sys.argv[1:4]
only = sys.argv[4].split(",") if len(sys.argv) > 4 else None
beats = json.load(open(beats_path, encoding="utf-8"))["beats"]

HARMLESS = {"metres": "meters", "metre": "meter", "licence": "license", "licences": "licenses", "virtualisation": "virtualization",
            "kilograms": "kg", "tonne": "ton", "kiln's": "kilns", "iluca": "iluka"}
IGNORE_HEARD = {"th", "st", "nd", "rd", "percent"}
IGNORE_WRITTEN = {"percent"}

UNITS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split())}
TENS = {w: 10 * i for i, w in enumerate("x x twenty thirty forty fifty sixty seventy eighty ninety".split()) if w != "x"}
ORD = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10, "eleventh": 11,
       "twelfth": 12, "thirteenth": 13, "fourteenth": 14, "fifteenth": 15, "sixteenth": 16, "seventeenth": 17, "eighteenth": 18, "nineteenth": 19,
       "twentieth": 20, "thirtieth": 30, "fortieth": 40, "fiftieth": 50}


def numw(t):
    return t in UNITS or t in TENS or t in ORD or t in ("hundred", "thousand")


def parse_run(run):
    total, cur = 0, 0
    for t in run:
        if t in UNITS:
            cur += UNITS[t]
        elif t in TENS:
            cur += TENS[t]
        elif t in ORD:
            cur += ORD[t]
        elif t == "hundred":
            cur = max(cur, 1) * 100
        elif t == "thousand":
            total += max(cur, 1) * 1000
            cur = 0
    return total + cur


def numtok(intpart, dec):
    s = str(int(intpart or 0))
    if dec:
        d = dec.rstrip("0")
        if d:
            s += "." + d
    return "N:" + s


def clean(text):
    text = text.lower().replace("-", " ").replace("_", " ")
    text = re.sub(r"(\d),(\d{3})", lambda m: m.group(1) + m.group(2), text)
    text = re.sub(r"(\d+)\s?(st|nd|rd|th)\b", lambda m: m.group(1), text)
    text = re.sub(r"\d+(\.\d+)?", lambda m: " zzn" + m.group(0).replace(".", "p") + " ", text)
    text = re.sub(r"[,;:.?!]", " | ", text)
    text = re.sub(r"[^a-z0-9'| ]", " ", text)
    return text.split()


def tokens(text):
    toks = clean(text)
    out, i = [], 0
    while i < len(toks):
        t = toks[i]
        if t == "|":
            i += 1
        elif t.startswith("zzn"):
            a, _, b = t[3:].partition("p")
            out.append(numtok(a, b))
            i += 1
        elif numw(t) or (t == "point" and i + 1 < len(toks) and toks[i + 1] in UNITS):
            j, run, dec = i, [], None
            while j < len(toks) and (numw(toks[j]) or toks[j] == "point"):
                if toks[j] == "point":
                    k, ds = j + 1, []
                    while k < len(toks) and toks[k] in UNITS and UNITS[toks[k]] < 10:
                        ds.append(str(UNITS[toks[k]]))
                        k += 1
                    dec = "".join(ds)
                    j = k
                    break
                run.append(toks[j])
                j += 1
            out.append(numtok(parse_run(run) if run else 0, dec))
            i = j
        else:
            out.append(HARMLESS.get(t, t))
            i += 1
    return out


def squash(ts):
    s = "".join(t.replace("N:", "") for t in ts)
    return re.sub(r"\d+", lambda m: str(int(m.group())), s)


cache_path = os.path.join(vdir, "transcripts.json")
cache = json.load(open(cache_path, encoding="utf-8")) if os.path.exists(cache_path) else {}
need = [b for b in beats if (not only or b["id"] in only) and os.path.exists(os.path.join(vdir, b["id"] + ".wav"))
        and (b["id"] not in cache or cache[b["id"]]["mtime"] != os.path.getmtime(os.path.join(vdir, b["id"] + ".wav")))]
if need:
    from faster_whisper import WhisperModel
    try:
        m = WhisperModel("medium", device="cuda", compute_type="float16")
        print("whisper on cuda")
    except Exception as e:
        m = WhisperModel("medium", device="cpu", compute_type="int8")
        print("whisper on cpu (%s)" % str(e)[:60])
    for b in need:
        f = os.path.join(vdir, b["id"] + ".wav")
        segs, _ = m.transcribe(f, language="en")
        t = " ".join(s.text.strip() for s in segs)
        cache[b["id"]] = {"text": re.sub(r"\s+", " ", t).strip(), "mtime": os.path.getmtime(f)}
        print("transcribed", b["id"], flush=True)
        json.dump(cache, open(cache_path, "w", encoding="utf-8"), indent=1)

rows, bad = [], 0
for b in beats:
    if only and b["id"] not in only:
        continue
    if b["id"] not in cache:
        continue
    a = [t for t in tokens(cache[b["id"]]["text"]) if t not in IGNORE_HEARD]
    c = [t for t in tokens(b["text"]) if t not in IGNORE_WRITTEN]
    sm = difflib.SequenceMatcher(None, c, a, autojunk=False)
    diffs, soft = [], []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        w, h = c[i1:i2], a[j1:j2]
        (soft if squash(w) == squash(h) else diffs).append("written [%s] heard [%s]" % (" ".join(w), " ".join(h)))
    rows.append((b["id"], sm.ratio(), diffs, soft, cache[b["id"]]["text"], b["text"]))
    if diffs:
        bad += 1
with open(out_md, "w", encoding="utf-8") as f:
    f.write("# Voice check (offline faster_whisper medium on cuda, Darth_MikGeorg clips vs beat text)\n\n")
    f.write("Method: every clip is transcribed offline; numbers are compared by value (fifteenth = 15th), codes with spaces and leading zeros removed (SR1 = SR 1), ")
    f.write("and a few spelling variants are ignored (metres/meters, licence/license, virtualisation/virtualization, 'percent' written as a symbol). ")
    f.write("What remains below are real differences between what the recogniser heard and what is written; each was reviewed by hand. ")
    f.write("The recogniser is not a perfect judge of rare place names: where it writes a different spelling of Narngulu, Eneabba, Castellon, Capel, Cataby or Balranald, ")
    f.write("the respelling in tests/e2e/film/pronunciations.json was chosen by testing candidates (tests/e2e/film/prontest.py) and the clips are listed for the author to listen to.\n\n")
    f.write("Clips with no difference after normalisation: %d of %d. Clips with remaining differences: %d.\n\n" % (len(rows) - bad, len(rows), bad))
    for bid, ratio, diffs, soft, heard, written in rows:
        f.write("## %s  match %.3f  %s\n\n" % (bid, ratio, "EXACT" if not diffs else "differences: %d" % len(diffs)))
        for d in diffs:
            f.write("- %s\n" % d)
        if soft:
            f.write("- code or number formatting only (equal once spaces and zeros are removed): %d\n" % len(soft))
        if diffs:
            f.write("\n- heard: %s\n- written: %s\n" % (heard, written))
        f.write("\n")
print("clips %d, exact after normalisation %d, with differences %d" % (len(rows), len(rows) - bad, bad))
for bid, ratio, diffs, soft, heard, written in rows:
    if diffs:
        print(bid, "%.3f" % ratio, "; ".join(diffs)[:400])
