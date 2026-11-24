#!/usr/bin/env python
"""Compress media in a PPTX without renaming any media file.

Usage:
  python pptx_compress.py deck.pptx [--dpi 150] [--preset medium]
         [--keep "a,b"] [--skip-video] [--skip-audio] [--output out.pptx]

Requires: Python 3, Pillow, ffmpeg on PATH
"""
import argparse
import html
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import wave
import xml.etree.ElementTree as ET
import zipfile
from urllib.parse import unquote

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

EMU_PER_INCH = 914400.0
ZIP64_LIMIT = 2 ** 30

EXT_JPG = {".jpg", ".jpeg"}
EXT_PNG = {".png"}
EXT_VIDEO = {".mp4", ".mov"}
EXT_GIF = {".gif"}
EXT_AUDIO = {".mp3", ".wav", ".m4a"}

GIF_MAX_WIDTH = 960
GIF_MAX_FPS = 15
GIF_COLORS = 128
GIF_DURATION_TOLERANCE = 0.05

PRESETS = {
    "light": {"crf": 23, "sr": 44100},
    "medium": {"crf": 29, "sr": 44100},
    "aggressive": {"crf": 29, "sr": 22050},
}

# Video house rules: never wider than 960 px, never above 15 fps (sources already lower are left alone).
VIDEO_MAX_WIDTH = 960
VIDEO_MAX_FPS = 15

# Images: after the dpi cap, if either side is still above this many pixels, halve both sides.
HALVE_ABOVE_PX = 500

# Audio (mp3/m4a): sources above this bitrate are re-encoded to it; lower bitrates are left alone.
AUDIO_MAX_KBPS = 96
BITRATE_RE = re.compile(r"bitrate:\s*(\d+)\s*kb/s")

# Lossy re-encodes that do not resize must save at least 10% to be kept.
MIN_GAIN_LOSSY = 0.90

REL_RE = re.compile(r"<Relationship\b[^>]*?/>", re.S)
ATTR_RE = re.compile(r"([\w:]+)\s*=\s*([\"'])(.*?)\2", re.S)
SLDLAYOUTID_RE = re.compile(r"<(?:\w+:)?sldLayoutId\b[^>]*?/>", re.S)
SCANNED_PART_RE = re.compile(r"^ppt/(slides|slideLayouts|slideMasters)/[^/]+\.xml$")


def q(ns, tag):
    return "{%s}%s" % (ns, tag)


def kb(n):
    return "%s" % format(int(round(n / 1024.0)), ",")


def rels_owner(rels_name):
    d, f = posixpath.split(rels_name)
    base_dir = posixpath.dirname(d)
    return posixpath.join(base_dir, f[:-5]) if f.endswith(".rels") else rels_name


def rels_path_for(part):
    d, f = posixpath.split(part)
    return posixpath.join(d, "_rels", f + ".rels")


def resolve_target(owner, target):
    target = unquote(html.unescape(target))
    if target.startswith("/"):
        return posixpath.normpath(target.lstrip("/"))
    return posixpath.normpath(posixpath.join(posixpath.dirname(owner), target))


def build_rels(parts):
    rels = {}
    for name, data in parts.items():
        if not name.endswith(".rels"):
            continue
        owner = rels_owner(name)
        text = data.decode("utf-8", errors="replace")
        items = {}
        for m in REL_RE.finditer(text):
            attrs = {a: v for a, _, v in ATTR_RE.findall(m.group(0))}
            if attrs.get("TargetMode", "").lower() == "external":
                continue
            if "Id" not in attrs or "Target" not in attrs:
                continue
            items[attrs["Id"]] = (attrs.get("Type", ""), resolve_target(owner, attrs["Target"]))
        rels[owner] = items
    return rels


def build_parent_map(root):
    return {c: p for p in root.iter() for c in p}


def get_slide_size(parts):
    data = parts.get("ppt/presentation.xml")
    if data:
        try:
            root = ET.fromstring(data)
            sz = root.find(q(NS_P, "sldSz"))
            if sz is not None:
                return int(sz.get("cx")) / EMU_PER_INCH, int(sz.get("cy")) / EMU_PER_INCH
        except (ET.ParseError, TypeError, ValueError):
            pass
    return 12192000 / EMU_PER_INCH, 6858000 / EMU_PER_INCH


def blip_size(blip, parents, slide_size):
    bf = parents.get(blip)
    if bf is None or bf.tag not in (q(NS_A, "blipFill"), q(NS_P, "blipFill")):
        return None
    if bf.find(q(NS_A, "tile")) is not None:
        return None
    gp = parents.get(bf)
    if gp is None:
        return None
    if gp.tag == q(NS_P, "bgPr"):
        return slide_size
    if gp.tag == q(NS_P, "pic"):
        sppr = gp.find(q(NS_P, "spPr"))
    elif gp.tag == q(NS_P, "spPr"):
        sppr = gp
    else:
        return None
    if sppr is None:
        return None
    xfrm = sppr.find(q(NS_A, "xfrm"))
    ext = xfrm.find(q(NS_A, "ext")) if xfrm is not None else None
    if ext is None:
        return None
    try:
        w = int(ext.get("cx")) / EMU_PER_INCH
        h = int(ext.get("cy")) / EMU_PER_INCH
        node = parents.get(gp)
        while node is not None:
            if node.tag == q(NS_P, "grpSp"):
                gx = node.find(q(NS_P, "grpSpPr") + "/" + q(NS_A, "xfrm"))
                if gx is not None:
                    gext = gx.find(q(NS_A, "ext"))
                    gch = gx.find(q(NS_A, "chExt"))
                    if gext is not None and gch is not None:
                        chx, chy = int(gch.get("cx")), int(gch.get("cy"))
                        if chx > 0 and chy > 0:
                            w *= int(gext.get("cx")) / float(chx)
                            h *= int(gext.get("cy")) / float(chy)
            node = parents.get(node)
        fr = bf.find(q(NS_A, "stretch") + "/" + q(NS_A, "fillRect"))
        if fr is not None:
            fill_l = int(fr.get("l", "0")) / 100000.0
            fill_t = int(fr.get("t", "0")) / 100000.0
            fill_r = int(fr.get("r", "0")) / 100000.0
            fill_b = int(fr.get("b", "0")) / 100000.0
            w *= max(1.0 - fill_l - fill_r, 0.01)
            h *= max(1.0 - fill_t - fill_b, 0.01)
        left = top = right = bottom = 0.0
        sr = bf.find(q(NS_A, "srcRect"))
        if sr is not None:
            left = int(sr.get("l", "0")) / 100000.0
            top = int(sr.get("t", "0")) / 100000.0
            right = int(sr.get("r", "0")) / 100000.0
            bottom = int(sr.get("b", "0")) / 100000.0
        return w / max(1.0 - left - right, 0.01), h / max(1.0 - top - bottom, 0.01)
    except (TypeError, ValueError):
        return None


def scan_uses(parts, rels_by_part, slide_size):
    uses = {}
    for part, data in parts.items():
        if not SCANNED_PART_RE.match(part):
            continue
        rels = rels_by_part.get(part, {})
        try:
            root = ET.fromstring(data)
        except ET.ParseError:
            continue
        parents = build_parent_map(root)
        for blip in root.iter(q(NS_A, "blip")):
            rid = blip.get(q(NS_R, "embed"))
            if not rid or rid not in rels:
                continue
            target = rels[rid][1]
            if not target.startswith("ppt/media/"):
                continue
            size = blip_size(blip, parents, slide_size)
            rec = uses.setdefault(target, {}).setdefault((part, rid), {"w": 0.0, "h": 0.0, "unknown": False})
            if size is None:
                rec["unknown"] = True
            else:
                rec["w"] = max(rec["w"], size[0])
                rec["h"] = max(rec["h"], size[1])
    return uses


def build_refs(rels_by_part):
    refs = {}
    for owner, items in rels_by_part.items():
        for rid, (_typ, target) in items.items():
            if target.startswith("ppt/media/"):
                refs.setdefault(target, set()).add((owner, rid))
    return refs


def image_requirement(media, refs, uses):
    ref_set = refs.get(media, set())
    if not ref_set:
        return None, "not referenced by any part"
    use_map = uses.get(media, {})
    w = h = 0.0
    where = set()
    for key in ref_set:
        rec = use_map.get(key)
        if rec is None or rec["unknown"]:
            return None, "display size unknown (%s)" % posixpath.basename(key[0] or "package")
        w = max(w, rec["w"])
        h = max(h, rec["h"])
        if key[0].startswith("ppt/slides/"):
            where.add("S")
        elif key[0].startswith("ppt/slideLayouts/"):
            where.add("L")
        elif key[0].startswith("ppt/slideMasters/"):
            where.add("M")
    return (w, h, "".join(sorted(where))), ""


def plan_resize(iw, ih, w_in, h_in, dpi):
    tw = w_in * dpi
    th = h_in * dpi
    scale = min(1.0, max(tw / float(iw), th / float(ih)))
    if iw * scale > HALVE_ABOVE_PX or ih * scale > HALVE_ABOVE_PX:
        scale *= 0.5
    if scale >= 1.0:
        return None
    return max(1, int(round(iw * scale))), max(1, int(round(ih * scale)))


def compress_jpg(Image, resample, src, dst, w_in, h_in, dpi, quality):
    with Image.open(src) as im:
        exif = im.getexif()
        if exif.get(0x0112, 1) not in (0, 1):
            return None, "skipped (EXIF rotation present)"
        icc = im.info.get("icc_profile")
        im.load()
        new_size = plan_resize(im.size[0], im.size[1], w_in, h_in, dpi)
        out = im.resize(new_size, resample) if new_size else im
        if out.mode not in ("RGB", "L", "CMYK"):
            out = out.convert("RGB")
        kw = {"format": "JPEG", "quality": quality, "optimize": True}
        if icc:
            kw["icc_profile"] = icc
        out.save(dst, **kw)
        note = "%dx%d -> %dx%d" % (im.size[0], im.size[1], new_size[0], new_size[1]) if new_size else "re-encoded"
        return bool(new_size), note


def compress_png(Image, resample, src, dst, w_in, h_in, dpi):
    with Image.open(src) as im:
        if getattr(im, "is_animated", False):
            return None, "skipped (animated PNG)"
        if im.mode not in ("RGB", "RGBA", "L", "LA", "P"):
            return None, "skipped (mode %s)" % im.mode
        icc = im.info.get("icc_profile")
        im.load()
        new_size = plan_resize(im.size[0], im.size[1], w_in, h_in, dpi)
        out = im
        if new_size:
            if im.mode == "P":
                out = im.convert("RGBA" if "transparency" in im.info else "RGB")
            out = out.resize(new_size, resample)
        kw = {"format": "PNG", "optimize": True}
        if icc:
            kw["icc_profile"] = icc
        out.save(dst, **kw)
        note = "%dx%d -> %dx%d" % (im.size[0], im.size[1], new_size[0], new_size[1]) if new_size else "optimized"
        return bool(new_size), note


def run_ffmpeg(ffmpeg, args):
    p = subprocess.run(
        [ffmpeg, "-y", "-nostdin", "-v", "error"] + args,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return p.returncode == 0, p.stderr.strip().splitlines()[-1] if p.stderr.strip() else ""


def probe_fps(ffmpeg, src):
    p = subprocess.run([ffmpeg, "-nostdin", "-i", src], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    line = next((l for l in p.stderr.splitlines() if " Video:" in l), "")
    m = re.search(r"(\d+(?:\.\d+)?) fps", line)
    return float(m.group(1)) if m else None


def compress_video(ffmpeg, src, dst, preset):
    vf = "scale='trunc(min(iw,%d)/2)*2':-2" % VIDEO_MAX_WIDTH
    src_fps = probe_fps(ffmpeg, src)
    if src_fps is None or src_fps > VIDEO_MAX_FPS + 0.01:
        vf += ",fps=%d" % VIDEO_MAX_FPS
    args = [
        "-i", src, "-map", "0:v:0", "-map", "0:a?",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(preset["crf"]), "-preset", "medium",
        "-vf", vf,
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", dst,
    ]
    return run_ffmpeg(ffmpeg, args)


def probe_kbps(ffmpeg, src):
    p = subprocess.run([ffmpeg, "-nostdin", "-i", src], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    m = BITRATE_RE.search(p.stderr)
    return int(m.group(1)) if m else None


def compress_audio(ffmpeg, src, dst, ext, preset):
    if ext in (".mp3", ".m4a"):
        kbps = probe_kbps(ffmpeg, src)
        if kbps is not None and kbps <= AUDIO_MAX_KBPS:
            return None, "skipped (already %d kb/s, at or below %dk)" % (kbps, AUDIO_MAX_KBPS)
        codec = "libmp3lame" if ext == ".mp3" else "aac"
        args = ["-i", src, "-vn", "-c:a", codec, "-b:a", "%dk" % AUDIO_MAX_KBPS, dst]
    else:
        try:
            with wave.open(src, "rb") as w:
                src_sr = w.getframerate()
        except (wave.Error, EOFError):
            return False, "cannot read WAV sample rate"
        args = ["-i", src, "-vn", "-c:a", "pcm_s16le", "-ar", str(min(src_sr, preset["sr"])), dst]
    return run_ffmpeg(ffmpeg, args)


def gif_info(Image, path):
    """(width, height, frames, total_ms, loop) of a GIF; frames == 1 for a static one."""
    with Image.open(path) as im:
        n = getattr(im, "n_frames", 1)
        total = 0
        for i in range(n):
            im.seek(i)
            total += im.info.get("duration", 0) or 0
        return im.size[0], im.size[1], n, total, im.info.get("loop")


def compress_gif(ffmpeg, Image, src, dst, w_in, dpi):
    """Animated GIF: width capped at min(source, 960 px, display width at dpi); never above 15 fps (the fps filter is only
    added when the average frame rate is above 15, so nothing is upsampled); 128-colour palette tuned to the clip. The loop
    setting is kept and the total play time must stay within 5 percent, otherwise the file is left alone."""
    w, h, n, total_ms, loop = gif_info(Image, src)
    if n < 2:
        return None, "skipped (static GIF)"
    avg_fps = n * 1000.0 / total_ms if total_ms else 0.0
    target_w = int(min(w, GIF_MAX_WIDTH, max(1, w_in * dpi)))
    chain = []
    if avg_fps > GIF_MAX_FPS + 0.01:
        chain.append("fps=%d" % GIF_MAX_FPS)
    if target_w < w:
        chain.append("scale=%d:-2:flags=lanczos" % target_w)
    chain.append("split[a][b];[a]palettegen=max_colors=%d:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" % GIF_COLORS)
    vf = ",".join(chain[:-1] + [chain[-1]]) if len(chain) > 1 else chain[0]
    ok, note = run_ffmpeg(ffmpeg, ["-i", src, "-vf", vf, "-loop", "0" if loop == 0 else ("-1" if loop is None else str(loop)), dst])
    if not ok:
        return None, "ffmpeg failed: %s" % note
    try:
        _, _, n2, total2, _ = gif_info(Image, dst)
    except Exception as exc:
        return None, "skipped (cannot read result: %s)" % exc
    if total_ms and abs(total2 - total_ms) > GIF_DURATION_TOLERANCE * total_ms:
        return None, "skipped (play time would change: %.1fs -> %.1fs)" % (total_ms / 1000.0, total2 / 1000.0)
    ow, oh = Image.open(dst).size
    return (target_w < w), "%dx%d -> %dx%d, %d -> %d frames, %d colours" % (w, h, ow, oh, n, n2, GIF_COLORS)


def layout_name(data):
    m = re.search(r"<p:cSld\b[^>]*\bname=\"([^\"]*)\"", data.decode("utf-8", errors="replace"))
    return html.unescape(m.group(1)) if m else ""


def plan_prune(names, parts, rels_by_part, keep_names):
    used = set()
    for n in names:
        if re.match(r"^ppt/slides/[^/]+\.xml$", n):
            for _rid, (typ, target) in rels_by_part.get(n, {}).items():
                if typ.endswith("/slideLayout"):
                    used.add(target)
    plan = []
    for master in sorted(n for n in names if re.match(r"^ppt/slideMasters/[^/]+\.xml$", n)):
        mtext = parts[master].decode("utf-8")
        order = []
        for m in SLDLAYOUTID_RE.finditer(mtext):
            rm = re.search(r"\br:id=\"([^\"]+)\"", m.group(0))
            if rm:
                order.append(rm.group(1))
        mrels = rels_by_part.get(master, {})
        layouts = []
        for rid in order:
            if rid in mrels and mrels[rid][0].endswith("/slideLayout"):
                target = mrels[rid][1]
                nm = layout_name(parts.get(target, b""))
                if target in used:
                    status = "used"
                elif nm.lower() in keep_names:
                    status = "keep"
                else:
                    status = "remove"
                layouts.append({"rid": rid, "target": target, "name": nm, "status": status})
        if layouts and all(l["status"] == "remove" for l in layouts):
            layouts[0]["status"] = "keep"
        plan.append({"master": master, "layouts": layouts})
    return plan


def print_prune_plan(plan):
    print("Layout pruning plan (status: used / keep / remove)")
    print("-" * 78)
    total_remove = 0
    for entry in plan:
        print("Master: %s" % entry["master"])
        for l in entry["layouts"]:
            print("  %-7s %-26s %s" % (l["status"].upper(), l["name"][:26], posixpath.basename(l["target"])))
            if l["status"] == "remove":
                total_remove += 1
    print("-" * 78)
    print("Layouts to remove: %d" % total_remove)
    return total_remove


APP_PAIR_RE = re.compile(
    r"(<vt:lpstr>)(.*?)(</vt:lpstr></vt:variant>\s*<vt:variant>\s*<vt:i4>)(\d+)(</vt:i4>)", re.S)


def update_app_xml(parts, removed_names):
    name = "docProps/app.xml"
    if name not in parts or not removed_names:
        return False
    text = parts[name].decode("utf-8")
    hp = re.search(r"<HeadingPairs>(.*?)</HeadingPairs>", text, re.S)
    tp = re.search(r"<TitlesOfParts>(.*?)</TitlesOfParts>", text, re.S)
    if not hp or not tp:
        return False
    pairs = APP_PAIR_RE.findall(hp.group(1))
    titles = re.findall(r"<vt:lpstr>(.*?)</vt:lpstr>", tp.group(1), re.S)
    if not pairs or sum(int(p[3]) for p in pairs) != len(titles):
        return False
    start = 0
    idx = None
    for i, p in enumerate(pairs):
        if html.unescape(p[1]) == "Slide Layouts":
            idx = i
            break
        start += int(p[3])
    if idx is None:
        return False
    count = int(pairs[idx][3])
    block = titles[start:start + count]
    for nm in removed_names:
        pos = next((k for k, t in enumerate(block) if html.unescape(t) == nm), None)
        if pos is None:
            return False
        del block[pos]
    new_titles = titles[:start] + block + titles[start + count:]
    new_vector = '<vt:vector size="%d" baseType="lpstr">%s</vt:vector>' % (
        len(new_titles), "".join("<vt:lpstr>%s</vt:lpstr>" % t for t in new_titles))
    state = {"i": -1}

    def sub_pair(m):
        state["i"] += 1
        if state["i"] != idx:
            return m.group(0)
        return m.group(1) + m.group(2) + m.group(3) + str(len(block)) + m.group(5)

    new_hp = APP_PAIR_RE.sub(sub_pair, hp.group(1))
    text = text[:hp.start(1)] + new_hp + text[hp.end(1):tp.start(1)] + new_vector + text[tp.end(1):]
    parts[name] = text.encode("utf-8")
    return True


def apply_prune(parts, plan):
    removed = set()
    modified = set()
    ct_name = "[Content_Types].xml"
    ct = parts[ct_name].decode("utf-8")
    for entry in plan:
        drop = [l for l in entry["layouts"] if l["status"] == "remove"]
        if not drop:
            continue
        drop_rids = {l["rid"] for l in drop}
        master = entry["master"]

        mtext = parts[master].decode("utf-8")
        count = [0]

        def sub_layout_id(m):
            rm = re.search(r"\br:id=\"([^\"]+)\"", m.group(0))
            if rm and rm.group(1) in drop_rids:
                count[0] += 1
                return ""
            return m.group(0)

        mtext = SLDLAYOUTID_RE.sub(sub_layout_id, mtext)
        if count[0] != len(drop_rids):
            raise RuntimeError("could not remove all sldLayoutId entries in %s" % master)

        rpath = rels_path_for(master)
        rtext = parts[rpath].decode("utf-8")
        rcount = [0]

        def sub_rel(m):
            attrs = {a: v for a, _, v in ATTR_RE.findall(m.group(0))}
            if attrs.get("Id") in drop_rids:
                rcount[0] += 1
                return ""
            return m.group(0)

        rtext = REL_RE.sub(sub_rel, rtext)
        if rcount[0] != len(drop_rids):
            raise RuntimeError("could not remove all layout relationships in %s" % rpath)

        parts[master] = mtext.encode("utf-8")
        parts[rpath] = rtext.encode("utf-8")
        modified.update([master, rpath])

        for l in drop:
            removed.add(l["target"])
            removed.add(rels_path_for(l["target"]))
            pat = re.compile(r"<Override\b[^>]*\bPartName=\"/%s\"[^>]*/>" % re.escape(l["target"]), re.S)
            ct, n = pat.subn("", ct)
            if n == 0:
                print("  warning: no Content_Types override found for %s" % l["target"])
    parts[ct_name] = ct.encode("utf-8")
    modified.add(ct_name)
    dropped_names = [l["name"] for e in plan for l in e["layouts"] if l["status"] == "remove"]
    if update_app_xml(parts, dropped_names):
        modified.add("docProps/app.xml")
    for n in removed:
        parts.pop(n, None)
    return removed, modified


def clone_info(item):
    zi = zipfile.ZipInfo(item.filename, item.date_time)
    zi.compress_type = item.compress_type
    zi.external_attr = item.external_attr
    return zi


def verify(path, orig_media, removed_media):
    problems = []
    with zipfile.ZipFile(path) as z:
        bad = z.testzip()
        if bad:
            problems.append("corrupt zip entry: %s" % bad)
        names = set(z.namelist())
        parts = {n: z.read(n) for n in names if n.endswith((".xml", ".rels"))}
    rels = build_rels(parts)
    for owner, items in rels.items():
        if owner and owner not in names:
            problems.append("rels file for missing part: %s" % owner)
        for rid, (_typ, target) in items.items():
            if target not in names:
                problems.append("%s: %s -> missing %s" % (owner or "(package)", rid, target))
    ct = parts.get("[Content_Types].xml", b"").decode("utf-8", errors="replace")
    for m in re.finditer(r"<Override\b[^>]*\bPartName=\"([^\"]+)\"", ct):
        if m.group(1).lstrip("/") not in names:
            problems.append("Content_Types override for missing part: %s" % m.group(1))
    media_now = {n for n in names if n.startswith("ppt/media/") and not n.endswith("/")}
    expected = set(orig_media) - set(removed_media)
    if media_now != expected:
        problems.append("media set differs from expected (%d vs %d)" % (len(media_now), len(expected)))
    pptx_note = ""
    try:
        from pptx import Presentation
        prs = Presentation(path)
        pptx_note = "python-pptx loaded OK (%d slides)" % len(prs.slides)
    except ImportError:
        pptx_note = "python-pptx not installed; load test skipped"
    except Exception as exc:
        problems.append("python-pptx failed to load: %s" % exc)
    return problems, pptx_note


def main():
    ap = argparse.ArgumentParser(description="Compress media in a PPTX (names and formats unchanged).")
    ap.add_argument("input")
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--quality", type=int, default=80, help="JPEG quality")
    ap.add_argument("--preset", choices=sorted(PRESETS), default="medium")
    ap.add_argument("--prune-layouts", action="store_true", help="print the plan of unused layouts and exit without writing (dry run)")
    ap.add_argument("--confirm-prune", action="store_true", help="with --prune-layouts: apply the plan after the user has reviewed it")
    ap.add_argument("--keep", default="", help="comma-separated layout names to keep when pruning")
    ap.add_argument("--skip-video", action="store_true")
    ap.add_argument("--skip-audio", action="store_true")
    ap.add_argument("--skip-gif", action="store_true", help="do not touch animated GIFs")
    ap.add_argument("--output", default="")
    args = ap.parse_args()

    if args.confirm_prune and not args.prune_layouts:
        print("ERROR: --confirm-prune requires --prune-layouts")
        return 2

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    try:
        from PIL import Image
    except ImportError:
        print("ERROR: Pillow is not installed in this Python. Stop.")
        return 2
    Image.MAX_IMAGE_PIXELS = None
    resample = getattr(Image, "Resampling", Image).LANCZOS

    src = os.path.abspath(args.input)
    if not os.path.isfile(src) or not src.lower().endswith(".pptx"):
        print("ERROR: input must be an existing .pptx file")
        return 2
    out_path = os.path.abspath(args.output) if args.output else os.path.splitext(src)[0] + "_compressed.pptx"
    if os.path.normcase(out_path) == os.path.normcase(src):
        print("ERROR: output path equals input path")
        return 2

    preset = PRESETS[args.preset]
    keep_names = {k.strip().lower() for k in args.keep.split(",") if k.strip()}

    try:
        zin_cm = zipfile.ZipFile(src)
    except zipfile.BadZipFile:
        print("ERROR: file is not a valid ZIP/PPTX (corrupt or wrong format). Stop.")
        return 2
    with zin_cm as zin:
        infos = zin.infolist()
        names = [i.filename for i in infos]
        parts = {n: zin.read(n) for n in names if n.endswith((".xml", ".rels"))}
        media = sorted(n for n in names if n.startswith("ppt/media/") and not n.endswith("/"))

        need_ffmpeg = any(
            (posixpath.splitext(n)[1].lower() in EXT_VIDEO and not args.skip_video)
            or (posixpath.splitext(n)[1].lower() in EXT_AUDIO and not args.skip_audio)
            or (posixpath.splitext(n)[1].lower() in EXT_GIF and not args.skip_gif)
            for n in media
        )
        ffmpeg = shutil.which("ffmpeg")
        if need_ffmpeg and not ffmpeg:
            print("ERROR: ffmpeg not found on PATH but the deck has video/audio. Stop (or use --skip-video --skip-audio).")
            return 2

        rels_before = build_rels(parts)
        refs_before = build_refs(rels_before)

        removed = set()
        modified = set()
        removed_media = set()
        if args.prune_layouts:
            plan = plan_prune(names, parts, rels_before, keep_names)
            total_remove = print_prune_plan(plan)
            if not args.confirm_prune:
                print("Dry run only: nothing written. Re-run with --prune-layouts --confirm-prune to apply.")
                return 0
            if total_remove:
                removed, modified = apply_prune(parts, plan)
                refs_after_prune = build_refs(build_rels(parts))
                removed_media = {m for m in refs_before if m not in refs_after_prune and m in set(media)}

        rels_by_part = build_rels(parts)
        refs = build_refs(rels_by_part)
        uses = scan_uses(parts, rels_by_part, get_slide_size(parts))

        rows = []
        replaced = {}
        untouched_other = 0
        with tempfile.TemporaryDirectory() as tmp:
            for idx, name in enumerate(media):
                if name in removed_media:
                    continue
                ext = posixpath.splitext(name)[1].lower()
                is_img = ext in EXT_JPG or ext in EXT_PNG
                is_vid = ext in EXT_VIDEO
                is_aud = ext in EXT_AUDIO
                is_gif = ext in EXT_GIF
                if not (is_img or is_vid or is_aud or is_gif):
                    untouched_other += 1
                    continue
                before = zin.getinfo(name).file_size
                row = {"file": name[len("ppt/media/"):], "ext": ext, "before": before, "after": before,
                       "action": "unchanged", "note": "", "where": ""}
                rows.append(row)

                if (is_vid and args.skip_video) or (is_aud and args.skip_audio) or (is_gif and args.skip_gif):
                    row["action"] = "skipped"
                    row["note"] = "by option"
                    continue

                req = None
                if is_img or is_gif:
                    req, why = image_requirement(name, refs, uses)
                    if req is None:
                        row["action"] = "skipped"
                        row["note"] = why
                        continue
                    row["where"] = req[2]

                in_f = os.path.join(tmp, "in%d%s" % (idx, ext))
                out_f = os.path.join(tmp, "out%d%s" % (idx, ext))
                with zin.open(name) as s, open(in_f, "wb") as d:
                    shutil.copyfileobj(s, d)
                resized = False
                try:
                    if ext in EXT_JPG:
                        resized, note = compress_jpg(Image, resample, in_f, out_f, req[0], req[1], args.dpi, args.quality)
                        lossy = True
                    elif ext in EXT_PNG:
                        resized, note = compress_png(Image, resample, in_f, out_f, req[0], req[1], args.dpi)
                        lossy = False
                    elif is_gif:
                        resized, note = compress_gif(ffmpeg, Image, in_f, out_f, req[0], args.dpi)
                        lossy = True
                    elif is_vid:
                        ok, note = compress_video(ffmpeg, in_f, out_f, preset)
                        if not ok:
                            resized, note = None, "ffmpeg failed: %s" % note
                        else:
                            resized, note, lossy = False, "re-encoded crf %d" % preset["crf"], True
                    else:
                        ok, note = compress_audio(ffmpeg, in_f, out_f, ext, preset)
                        if ok is None:
                            resized = None
                        elif not ok:
                            resized, note = None, "ffmpeg failed: %s" % note
                        else:
                            resized, note, lossy = False, "re-encoded", True
                except Exception as exc:
                    resized, note = None, "error: %s" % exc

                if resized is None:
                    row["action"] = "skipped"
                    row["note"] = note
                else:
                    after = os.path.getsize(out_f)
                    threshold = before if (resized or not lossy) else before * MIN_GAIN_LOSSY
                    keep_new = after < threshold if (resized or not lossy) else after <= threshold
                    if keep_new:
                        row["after"] = after
                        row["action"] = "resized" if resized else ("re-encoded" if lossy else "optimized")
                        row["note"] = note
                        replaced[name] = out_f
                        out_f = None
                    else:
                        row["note"] = "no worthwhile gain"
                for f in (in_f, out_f):
                    if f and os.path.exists(f):
                        os.remove(f)

            order = sorted(infos, key=lambda i: 0 if i.filename == "[Content_Types].xml" else 1)
            tmp_out = out_path + ".tmp"
            with zipfile.ZipFile(tmp_out, "w", allowZip64=True) as zout:
                for item in order:
                    n = item.filename
                    if n in removed or n in removed_media:
                        continue
                    zi = clone_info(item)
                    if n.endswith("/"):
                        zout.writestr(zi, b"")
                    elif n in replaced:
                        size = os.path.getsize(replaced[n])
                        zi.file_size = size
                        with open(replaced[n], "rb") as s, zout.open(zi, "w", force_zip64=size > ZIP64_LIMIT) as d:
                            shutil.copyfileobj(s, d)
                    elif n in modified:
                        zout.writestr(zi, parts[n])
                    else:
                        zi.file_size = item.file_size
                        with zin.open(item) as s, zout.open(zi, "w", force_zip64=item.file_size > ZIP64_LIMIT) as d:
                            shutil.copyfileobj(s, d)

    if os.path.exists(out_path):
        old = os.path.splitext(out_path)[0] + "_OLD.pptx"
        os.replace(out_path, old)
        print("Previous output moved to %s" % old)
    os.replace(tmp_out, out_path)

    print()
    print("%-36s %-5s %-4s %9s %9s %6s  %s" % ("file", "type", "used", "before KB", "after KB", "saved", "action / note"))
    print("-" * 110)
    for r in rows:
        saved = (1.0 - r["after"] / float(r["before"])) * 100.0 if r["before"] else 0.0
        print("%-36s %-5s %-4s %9s %9s %5.0f%%  %s %s" % (
            r["file"][:36], r["ext"], r["where"], kb(r["before"]), kb(r["after"]), saved, r["action"], r["note"]))
    print("-" * 110)
    mb = sum(r["before"] for r in rows)
    ma = sum(r["after"] for r in rows)
    print("Media handled: %s KB -> %s KB" % (kb(mb), kb(ma)))
    print("Other media types left untouched: %d file(s)" % untouched_other)
    if removed:
        print("Removed layouts: %d part(s) incl. rels; orphaned media removed: %d" % (len(removed), len(removed_media)))
        for m in sorted(removed_media):
            print("  orphan removed: %s" % m)
        if "docProps/app.xml" in modified:
            print("docProps/app.xml layout titles and count updated.")
        else:
            print("Warning: docProps/app.xml left unchanged (unexpected structure); check the deck opens cleanly.")
    print("Whole file: %s KB -> %s KB" % (kb(os.path.getsize(src)), kb(os.path.getsize(out_path))))
    print("Output: %s" % out_path)

    problems, pptx_note = verify(out_path, media, removed_media)
    print()
    print("Verification: %s" % ("PASS" if not problems else "FAIL"))
    print("  %s" % pptx_note)
    for p in problems:
        print("  - %s" % p)
    print("Please open the output in PowerPoint and check videos and layouts.")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
