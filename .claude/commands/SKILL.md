---
name: pptx-compress
description: Compress media in a PPTX (jpg/png/mp4/mov/audio), cap images at 150 dpi, optionally prune unused slide layouts. Filenames and formats never change, so all links stay valid.
---

# PPTX Compress

Shrink a PowerPoint file by recompressing its embedded media and (optionally) removing unused slide layouts. A PPTX is a zip; media lives in `ppt/media/`.

## Python Environment

- Use the Python environment configured for this project (Python 3 with Pillow)
- Script: `.claude/skills/pptx_compress.py` (relative to the project root)
- Arguments passed by the user: $ARGUMENTS
- Required: Pillow (`import PIL`) and ffmpeg on PATH (`ffmpeg -version`)
- Before doing anything, run both checks. If either is missing, STOP and tell the user. Never assume they are installed.

## Hard Rules

- NEVER rename a media file or change its extension or folder. This keeps every `.rels` entry and `[Content_Types].xml` entry valid.
- NEVER upscale. Only replace a file if the result is smaller than the original. Lossy re-encodes that do not resize (JPG, video, audio) must save at least 10% to be kept.
- NEVER overwrite the input. Write to `<name>_compressed.pptx` next to the input.
- Re-zip with `[Content_Types].xml` as the first entry; preserve all other entries unchanged.
- Layout pruning is a DRY RUN by default. Only delete after the user confirms the list.
- Do not execute the script until the user asks for a run.

## Steps

1. **Unzip** the PPTX to a temp folder.

2. **Map media uses.** Scan slides, slide layouts and slide masters (`ppt/slides`, `ppt/slideLayouts`, `ppt/slideMasters`: both `.xml` and `_rels/*.rels`). For every media file record every place it is used, with the display size:
   - Display size in inches = `a:ext` `cx` / `cy` divided by 914400 (EMU per inch).
   - Correct for cropping: `a:srcRect` (l, t, r, b in 1/1000 of a percent). Full-image display width = frame width / (1 - l - r); same for height with t and b.
   - Backgrounds and full-slide fills use the slide size from `ppt/presentation.xml` (`p:sldSz`).
   - A media file used in several places (slides, layouts, masters) uses the LARGEST display size across all uses.
   - If the display size cannot be determined, leave the file untouched.

3. **Images (jpg, png).**
   - Max pixels = display inches x DPI (default 150). Resize only if the image is larger; keep aspect ratio; use Lanczos.
   - JPG: save as JPEG, quality 80, keep ICC profile, drop EXIF. Same path.
   - PNG: save as PNG with optimize on. Keep alpha. Same path. Do NOT convert PNG to JPG (would change format).
   - Applies equally to images used by slide masters and layouts (same 150 dpi cap).

4. **Video (mp4, mov).**
   - `ffmpeg -i in -c:v libx264 -crf <preset> -preset medium -c:a aac -b:a 128k -vf "scale='min(iw,1920)':-2" -movflags +faststart out`
   - Output keeps the SAME extension and container (`.mov` stays `.mov`, `.mp4` stays `.mp4`).
   - Presets: light = crf 23, medium = crf 26, aggressive = crf 29. Default: medium.
   - Warn the user that re-encoded `.mov` should be test-played in PowerPoint before the deck is trusted.

5. **Audio (mp3, wav, m4a).** Re-encode with ffmpeg to the same format at a lower bitrate (mp3/m4a 128k; wav stays wav at 22.05 or 44.1 kHz mono/stereo as source). Keep extension.

6. **Leave untouched:** svg, emf, wmf, gif, and any media type not listed above. (SVG is already small text; gains are negligible.)

7. **Prune unused layouts (only with `--prune-layouts`).**
   - A layout is USED if any slide's `.rels` targets it. Everything else is unused.
   - Dry run: print a table of each master, its layouts, and used/unused. Stop and ask the user to confirm.
   - `--keep "name1,name2"` forces named layouts to be retained even if unused.
   - On confirmation, for each unused layout remove:
     - the layout XML in `ppt/slideLayouts/` and its `_rels/` file
     - its `<p:sldLayoutId>` in the master's `p:sldLayoutIdLst`
     - the matching `Relationship` in the master's `.rels`
     - its `Override` in `[Content_Types].xml`
     - any media that is now referenced by nothing (check ALL rels before deleting)
   - If a master would end with zero layouts, keep one layout (the first) instead of deleting it. Never delete a master.
   - Warn the user: removed layouts are no longer available when adding new slides.

8. **Re-zip** to `<name>_compressed.pptx` and report.

## Report

Print a table: file, type, before (KB), after (KB), saved (%), action (resized / re-encoded / skipped / unchanged). Then totals: media before/after, whole-file before/after. If pruning ran, list removed layouts and orphaned media removed.

## Options

| Option | Default | Meaning |
|---|---|---|
| `--dpi N` | 150 | Max image resolution at display size |
| `--preset light/medium/aggressive` | medium | Video CRF (23 / 26 / 29) |
| `--prune-layouts` | off | Print the plan of unused layouts and exit without writing (dry run) |
| `--confirm-prune` | off | With `--prune-layouts`: apply the plan after the user has reviewed it |
| `--keep "a,b"` | none | Layout names to keep when pruning |
| `--quality N` | 80 | JPEG quality |
| `--output PATH` | `<name>_compressed.pptx` | Output file (a previous output is moved to `_OLD`) |
| `--skip-video` | off | Do not touch mp4/mov |
| `--skip-audio` | off | Do not touch audio |

## Verification (after a run)

- Open the output with python-pptx (`Presentation(path)`) to confirm it loads.
- Confirm every `Target` in every `.rels` resolves to an existing part.
- Confirm media filenames and extensions are identical to the original set (minus any orphans removed by pruning).
- Ask the user to open the deck in PowerPoint and check videos and slide layouts.
