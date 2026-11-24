---
name: pptx-compress
description: Compress media in a PPTX (jpg/png/animated gif/mp4/mov/audio): images capped at 150 dpi then halved if still over 500 px, animated GIFs capped at 960 px wide / 15 fps / 128 colours, video capped at 960 px wide / 15 fps / crf 29, audio capped at 96 kb/s, and unused slide layouts pruned. Filenames and formats never change, so all links stay valid.
---

# PPTX Compress

Shrink a PowerPoint file by recompressing its embedded media and removing unused slide layouts. A PPTX is a zip; media lives in `ppt/media/`.

## Summary of house rules

| Area | Rule |
|---|---|
| Images (jpg, jpeg, png) | Cap at 150 dpi of display size, then halve both sides if either is still over 500 px. Never upscale. |
| Animated GIF | Max width 960 px or the 150 dpi display size (whichever is smaller), max 15 fps (never upsampled), 128-colour palette tuned to the clip, loop setting kept, play time must stay within 5%. Static GIFs left alone. |
| Video (mp4, mov) | H.264, max width 960 px, max 15 fps (never upsampled), crf 29. Same name and extension. |
| Audio mp3/m4a | Re-encode to 96 kb/s only if the source is higher; otherwise skip. |
| Audio wav | Stay wav, 16-bit PCM, sample rate capped at 44.1 kHz (22.05 kHz with `--preset aggressive`). |
| Layouts | Unused layouts are always pruned, with no dry run. `--keep` protects named ones. |
| Files | Never renamed, never converted to another format, never overwritten (output is `<name>_compressed.pptx`). |
| Replace only if smaller | Lossy re-encodes without a resize must save at least 10%. |

## Python Environment

- ALWAYS use the conda environment `py_claude` (`C:\miniforge3\envs\py_claude\python.exe`). Never use any other Python.
- Script: `.claude/skills/pptx_compress.py` (relative to the project root)
- Arguments passed by the user: $ARGUMENTS
- Required: Pillow (`import PIL`) and ffmpeg on PATH (ffmpeg is also used for animated GIFs) (`ffmpeg -version`)
- Prerequisite check (a read-only probe, allowed before the user asks for a run): confirm Pillow imports in `py_claude` and `ffmpeg -version` succeeds. If either is missing, STOP and tell the user. Never assume they are installed. Do not run the script itself until the user asks for a run.

## Hard Rules

- NEVER rename a media file or change its extension or folder. This keeps every `.rels` entry and `[Content_Types].xml` entry valid.
- NEVER upscale. Only replace a file if the result is smaller than the original. Lossy re-encodes that do not resize (JPG, video, audio) must save at least 10% to be kept.
- NEVER overwrite the input. Write to `<name>_compressed.pptx` next to the input.
- Re-zip with `[Content_Types].xml` as the first entry; preserve all other entries unchanged.
- Unused layouts are ALWAYS pruned on every run. There is no dry run and no opt-out. Use `--keep` to protect named layouts.
- Do not execute the script until the user asks for a run.

## Image Rules (all recognized image files: jpg, jpeg, png)

Applied in this order to every image whose display size is known:

1. **150 dpi cap.** If the image has more pixels than display inches x 150, reduce it to that size.
2. **Halve if still large.** If, after step 1, either side is still more than 500 pixels, reduce BOTH width and height to half (aspect ratio kept).

Both rules only ever shrink. An image already at or under both limits is not resized.

## GIF Rules (animated .gif, same name and extension)

Applied to every animated GIF whose display size is known (static GIFs, GIFs of unknown display size and GIFs referenced by no part are skipped and left unchanged):

1. **Width:** reduce to the smallest of the source width, 960 px, and display width x dpi (150 by default). Never upscale.
2. **Frame rate:** the average frame rate is frames / total play time (NOT the delay of the first frame, which can be misleading). Add `fps=15` only when the average is above 15; never upsample.
3. **Colours:** ffmpeg `palettegen=max_colors=128:stats_mode=diff` then `paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle`. Transparency is kept. This is lossy for photographic or gradient content; tell the user.
4. **Loop setting kept** (infinite stays infinite).
5. **Play time guard:** if the total play time of the result differs from the source by more than 5%, the original is kept ("play time would change").
6. **Replace only if smaller** (a resize must save something; a re-encode without a resize must save at least 10%).

`--skip-gif` leaves all GIFs untouched. A frame-by-frame look at one GIF before and after is advisable on the first run of a deck; the GIF files are the biggest part of many decks.

## Skip Behaviour (a skipped file is left byte-for-byte unchanged and reported as "skipped" with the reason)

- Image with unknown display size, or referenced by no part.
- JPG with an EXIF rotation tag (re-saving would drop the tag and turn the picture sideways).
- PNG that is animated, or in an unusual mode (anything other than RGB, RGBA, L, LA, P, for example 16-bit).
- Audio mp3/m4a already at or below 96 kb/s.
- Any file whose re-encode is not smaller (or, for lossy re-encodes without a resize, not at least 10% smaller): reported as "no worthwhile gain".
- Any file that raises an error or an ffmpeg failure.
- Static GIF (one frame), GIF with unknown display size or referenced by no part, GIF whose play time would change by more than 5%.
- svg, emf, wmf and other media types: counted as "left untouched" in the report.

## Steps

1. **Read** the PPTX (the script streams the zip and works from temporary files; the input is never modified).

2. **Map media uses.** Scan slides, slide layouts and slide masters (`ppt/slides`, `ppt/slideLayouts`, `ppt/slideMasters`: both `.xml` and `_rels/*.rels`). For every media file record every place it is used, with the display size:
   - Display size in inches = `a:ext` `cx` / `cy` divided by 914400 (EMU per inch).
   - Correct for cropping: `a:srcRect` (l, t, r, b in 1/1000 of a percent). Full-image display width = frame width / (1 - l - r); same for height with t and b.
   - Backgrounds and full-slide fills use the slide size from `ppt/presentation.xml` (`p:sldSz`).
   - A media file used in several places (slides, layouts, masters) uses the LARGEST display size across all uses.
   - If the display size cannot be determined, leave the file untouched.

3. **Images (jpg, png).** Follow the Image Rules above (150 dpi cap, then halve if a side is still over 500 px).
   - Resize only if the image is larger; keep aspect ratio; use Lanczos.
   - JPG: save as JPEG, quality 80, keep ICC profile, drop EXIF. Same path.
   - PNG: save as PNG with optimize on. Keep alpha. Same path. Do NOT convert PNG to JPG (would change format).
   - Applies equally to images used by slide masters and layouts (same 150 dpi cap).

4. **Video (mp4, mov).**
   - `ffmpeg -i in -map 0:v:0 -map 0:a? -c:v libx264 -pix_fmt yuv420p -crf <preset> -preset medium -vf "scale='trunc(min(iw,960)/2)*2':-2,fps=15" -c:a aac -b:a 128k -movflags +faststart out`
   - Output keeps the SAME extension and container (`.mov` stays `.mov`, `.mp4` stays `.mp4`).
   - Presets: light = crf 23, medium = crf 29, aggressive = crf 29. Default: medium (crf 29). Medium and aggressive are identical for video; `aggressive` differs only for WAV audio (22.05 kHz).
   - Audio inside a video: the main script re-encodes it to AAC 128 kb/s. The helper script copies it unchanged.
   - **Video house rules (permanent, apply to every preset):** max width 960 px (never upscale) and never above 15 fps. The `fps=15` filter is added only when the source is above 15 fps; a source already at or below 15 fps is never upsampled.
   - A video-only helper exists for re-running just the video rules on a deck without touching images or layouts. See "Companion tools" below.
   - **WARNING (always tell the user after a run):** video is always re-encoded to H.264 with `yuv420p` and capped at 960 px wide and 15 fps. This discards alpha channels, high-bit-depth or HDR colour, and extra audio/subtitle tracks (only the first video track and any audio are kept). The 10% gain rule does not protect against these quality losses. Re-encoded `.mov` files in particular must be test-played in PowerPoint before the deck is trusted.

5. **Audio (mp3, wav, m4a).** Keep extension and format.
   - mp3/m4a: if the source bitrate is higher than 96 kb/s, re-encode to 96k. If it is 96 kb/s or lower, skip it (see Skip Behaviour). The bitrate is the same for every preset.
   - wav: stays wav (16-bit PCM) at the source sample rate, capped at 44.1 kHz. Only `--preset aggressive` lowers this cap to 22.05 kHz.

6. **Leave untouched:** svg, emf, wmf, and any media type not listed above. (SVG is already small text; gains are negligible.)

7. **Prune unused layouts (ALWAYS, on every run).**
   - A layout is USED if any slide's `.rels` targets it. Everything else is unused.
   - Print a table of each master, its layouts, and used/unused, then prune immediately (no confirmation step).
   - `--keep "name1,name2"` forces named layouts to be retained even if unused.
   - For each unused layout remove:
     - the layout XML in `ppt/slideLayouts/` and its `_rels/` file
     - its `<p:sldLayoutId>` in the master's `p:sldLayoutIdLst`
     - the matching `Relationship` in the master's `.rels`
     - its `Override` in `[Content_Types].xml`
     - any media that is now referenced by nothing (check ALL rels before deleting)
   - If a master would end with zero layouts, keep one layout (the first) instead of deleting it. Never delete a master.
   - Warn the user: removed layouts are no longer available when adding new slides.

8. **Re-zip** to `<name>_compressed.pptx` and report.

## Report

Print a table: file, type, before (KB), after (KB), saved (%), action (resized / re-encoded / skipped / unchanged). GIF rows show the size, frame and colour change. Then totals: media before/after, whole-file before/after. List removed layouts and orphaned media removed (pruning runs every time). Repeat the video warning if any video was re-encoded. If any GIF was re-encoded, add: GIFs are reduced to 128 colours (banding is possible on gradients and photos), and the user should play them in PowerPoint.

## Options

| Option | Default | Meaning |
|---|---|---|
| `--dpi N` | 150 | Max image resolution at display size |
| `--preset light/medium/aggressive` | medium | Video CRF (23 / 29 / 29); aggressive also lowers the WAV sample-rate cap to 22.05 kHz |
| `--keep "a,b"` | none | Layout names to keep when pruning (pruning itself always runs) |
| `--quality N` | 80 | JPEG quality |
| `--output PATH` | `<name>_compressed.pptx` | Output file (a previous output is moved to `_OLD`) |
| `--skip-video` | off | Do not touch mp4/mov |
| `--skip-audio` | off | Do not touch audio |
| `--skip-gif` | off | Do not touch animated GIFs |

## Companion tools (all in `.claude/skills/`, run with the `py_claude` Python)

| Script | Purpose | Usage |
|---|---|---|
| `pptx_compress.py` | The full method described above (images, video, audio, layout pruning). | `python pptx_compress.py deck.pptx [options]` |
| `pptx_video_speed.py` | Video only: re-applies the video house rules (and optionally changes playback speed) without touching images, audio files or layouts. Writes `<name>_vid960w.pptx`. | `python pptx_video_speed.py deck.pptx [--speed N] [--fps N] [--max-width N] [--crf N] [--output PATH]` |
| `pptx_png_quantize.py` | Optional extra, NOT part of the standard run: reduces PNGs to a 256-colour palette (alpha kept) and lightly minifies SVG. (GIFs are now handled by the main script.) Lossy for photographic PNGs. | `python pptx_png_quantize.py in.pptx out.pptx [halve_over_px]` |

`pptx_video_speed.py` details:
- Enforces the same house rules. It refuses `--fps` above 15 and `--max-width` above 960, and defaults to crf 29.
- The `fps` and width filters are added only when the source exceeds the cap; nothing is upsampled.
- Audio inside a video is copied unchanged (re-encoded only when `--speed` is not 1).
- With `--speed` 1, a video is replaced only if the re-encode is smaller; otherwise the original is kept.
- `--speed` does NOT adjust PowerPoint trims, bookmarks, fades or animation timings, which stay as authored.
- The output is a new file; an existing output is moved to `_OLD`. The input is never modified.

`pptx_png_quantize.py` only replaces a PNG or SVG when the result is smaller, never renames anything, and keeps `[Content_Types].xml` first. It does not apply the dpi logic and does not prune layouts. Run it only when the user asks for it.

## Verification (after a run)

- Open the output with python-pptx (`Presentation(path)`) to confirm it loads.
- Confirm every `Target` in every `.rels` resolves to an existing part.
- Confirm media filenames and extensions are identical to the original set (minus any orphans removed by pruning).
- Ask the user to open the deck in PowerPoint and check videos and slide layouts.
