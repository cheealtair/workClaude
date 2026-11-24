# Video_Production - reusable film pipeline (copied from MiningOpsApp, 2026-11-15)

START HERE: read Video_Production.md in this folder first (section 0 = best practice, Appendix C = the precedent).
It is the procedure; this folder also holds the code. Video_TerminalSession_Walkthrough.md is an OPTIONAL companion
(use case III: a narrated film of a session history file); read it only if the manual's question 10 gets a yes. Video_Production_A/B/C.md and README_A.md are backups: ignore them.

Source: C:\d_drive\workKW\WorkingMendixProjects\MiningOpsApp\tests\e2e\film\ (the working copy that made the two
MiningOpsApp walkthrough films). This folder is a TEMPLATE: copy ONLY engine/ (plus the example files you need)
into the TARGET project's tests/e2e/film/ and adapt there. Do not copy Video_Production.md or the backups into the
project; read the manual here. Never run film code from here against a project, and never edit it for one job;
improve it here only when a job teaches something general.

## What is generic (engine/) and what is not (example_MiningOpsApp/)

engine/ = reusable as it is (paths inside are relative to the project root, so copy into <project>/tests/e2e/film/):

| File | Job |
|---|---|
| voice_af_heart.py | one WAV per beat, Kokoro af_heart, speed 1.0, 24 kHz, offline, no processing (recipe H.1) |
| voice.py | same for Darth_MikGeorg (70% am_michael + 30% bm_george, speed 0.88, ffmpeg chain, recipe H.2) |
| voice_check_af_heart.py, voice_check.py | offline faster_whisper transcript of every clip compared with the beat text |
| prontest_af_heart.py, prontest.py, wcheck.py | try respellings of hard words quickly |
| voice_trim_v2.py | measure the speech window of each clip (the WAVs carry silence at both ends) |
| post_v2.js (post.js = the v1 captioned flow) | render and mix: places each clip at its beat time from the events, -16 LUFS, mux |
| verify_audio_v2.py, verify_frames_v2.py, slide_match_v2.py, gaps_v2.py | per-beat audio, no caption strip or bar or empty band, real-slide pixel match, gap measurement |
| export_pptx_slides.py (export_slides.py = PDF route) | slides to PNG; USE the PowerPoint COM one: the PDF export had 45 pages for a 48 slide deck |
| lib.js | sign in off camera, XAS logout, small helpers (password only from TEST_PASS, never printed) |
| smoke.js, rawframe.py | 10 second headless capture smoke test; raw frame grab |

example_MiningOpsApp/ = written around ONE app and ONE deck; use as worked examples, rewrite for a new app:
gen_beats.py (generates beats.json and the beat sheet: all the content), make_beats_v2.py (pause arithmetic),
update_beats.py, record.js / record_v2.js (the recorder: scene by scene, app click paths and selectors),
rehearse*.js, explore*.js, probe-scroll.js, check-graph.js (read-only rehearsal and graph checks),
verify_claims.js / verify_claims_v2.js (claims checks against this app's screen text),
pronunciations*.json (Mining place names and codes).
record_v2.js is the caption-free recorder (preferred); record.js is the older captioned one.

## Dependencies on this machine (verified 2026-11-15)

- Python with Kokoro and faster_whisper: C:\miniforge3\envs\py_claude\python.exe, always run with -I.
- ffmpeg and ffprobe: C:/miniforge3/envs/rm_genai/Library/bin/ffmpeg.exe (and ffprobe.exe). The scripts hold this path
  near the top; change it in one place per script if the machine changes.
- Node playwright 1.64.0 and axe-core 4.14.0 in the project's node_modules; the toolkit's demo-polish.js in the
  project's tests/e2e (capture; its default is 60 fps: call render/assemble with {fps:23}).
- PowerPoint for the COM slide export. ImageMagick on PATH is only the fallback.
- Offline: set the Hugging Face offline flags; no text may leave the machine for customer material.

## Starting a new job (short form; the long form is Video_Production.md section 0)

1. Copy engine/ to <project>/tests/e2e/film/. Read example_MiningOpsApp/gen_beats.py and record_v2.js as patterns.
2. Settle intake in ONE message: deck path, voice, length, output folder, captions or not, app and roles.
3. Slides to PNG (export_pptx_slides.py). Write beats (text, slide or app step, selectors, seconds) and the claims table.
4. Rehearse every app step read-only; pick the viewport (1600x900, device scale factor 2, render 1920x1080 at 23 fps).
5. Voice: all clips first, check them with voice_check, respell for synthesis only, measure the speech windows.
6. Record scene by scene (raw first), mix, verify, write the listening list for the author.
