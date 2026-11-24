# Plan_Session_Walkthrough - narrated paged-viewer video of a session history file

Status: PLANNING DOCUMENT (high level), rev 2. Written 2026-11-24. Replaces rev 1, which described a
continuously scrolling film. That design was built once and rejected: 322 MiB for 14.8 min.
Audience: the Claude agent that does video jobs (and the user reviewing the plan).
Place this file beside Video_Production.md in the Video Production project.
Proposed as USE CASE III of Video_Production.md. Tags as in that file: [DOCUMENTED], [PRECEDENT],
[PROPOSED], [UNVERIFIED]. If this file conflicts with Video_Production.md on a rule, Video_Production.md wins,
EXCEPT for the three output settings in section 2 (720p, AAC 64 kbps, paged picture), which the user chose
for this use case.

## 1. Goal

Input: ONE text file that is a session history, normally `session_history.md` (written by the
KStudio_toolkit, see Plan_Session_History.md) but any file in the same style is accepted: speaker
blocks (USER:, CLAUDE:, TOOL:), phase headings, plain ASCII. Output: an independent narrated MP4 that looks
like a plain text viewer or pager (less / more): the file is shown one still PAGE at a time, the voice explains
the page, and a soft band marks the passage being discussed. The next page appears by an instant cut, as if
the presenter pressed PgDn. No scrolling, no typing, no waiting or processing time is shown. The job needs
nothing but the input file; it does not depend on any other project and never modifies the input.

[PRECEDENT] Run census2 (2026-11-24), two builds of the same 14.78 min narration:
- continuous scroll, 1080p: 337 MB (crf 20; moving text costs about 2.9 Mbit/s). Rejected by the user.
- paged, 1080p: 28.36 MB (video 17.6 MB, audio the rest; still pages cost about 155 kbit/s). Verified by
  ffprobe and by eye on a sample of frames; not yet listened to by the user.
- paged, downscaled to 720p, audio copied: 24.57 MiB (about 2.5 MiB saved; audio is now the larger part).
The size lesson: a still page is almost free, moving text is not. Never scroll.

## 2. Output settings for this use case [DECIDED BY: user]

| Item | Setting | Note |
|---|---|---|
| Picture | still pages, instant cut between pages | no scrolling, no easing |
| Resolution | 1280x720 | next step below the 1920x1080 default of Video_Production.md |
| Frame rate | 23 fps | as the other use cases |
| Video codec | H.264 yuv420p, preset medium, `-tune stillimage`, crf 22, GOP about 20 s | proven in census2 |
| Audio | AAC mono 48 kHz, 64 kbps | AAC is lossy but better than MP3 for speech at the same bitrate and plays everywhere |
| Loudness | set once over the whole track, -16 LUFS, true peak limit -1.5 dBFS | census2 paged film peaked at -1.0, 0.5 dB over; check this |
| Container | MP4, `+faststart` | |

[UNVERIFIED] 64 kbps AAC for this voice (Kokoro af_heart): census2 used 96 kbps; a 64 kbps build was never
made. The agent cannot hear, so the user must listen. Expected saving versus 96 kbps: about 3.3 MB for 15 min.
[UNVERIFIED] Native 720p rendering: census2 was rendered at 1080p and downscaled, and the 720p frame at 130 s
was sharp and legible. Rendering the pages natively at 1280x720 has not been tried. Keeping about 118
columns at 1280 px wide means a font of about 19-20 px (28 px was used at 1080p). Test legibility first on
the densest page (long wrapped lines, tables) before building everything.

## 3. Reuse everything that already exists (do not re-invent)

Apply, unchanged, the parts of Video_Production.md that are not specific to slides:
- Section 1 standing rules (offline voice default, no secrets, no git outside allowed folders, tool paths,
  ASCII only in code, backup of previous output to `_OLD`, task_state.json).
- Section 4 pipeline model: beats.json, voice-engine gate (ask before voicing whether narration text may
  leave the machine), voice-stage hardening, "making the voice sound human" (offline focus), respelling map
  applied to the SYNTHESIS text only.
- Section 5 questions (see 4 below). Section 8 verification checklist and section 10 definition of done.
- Proven in census2 and the earlier films: voice sets the timing (about 0.5 s lead-in plus speech plus 1.5 s
  tail), concat of segments, faster-whisper check of every voice clip against its text.
All current options stay available: voice and language variants, target length with the re-time limit,
captions (none, soft track or burned in), output folder, backup to `_OLD`.

## 4. Questions to ask before starting (extends Video_Production.md section 5)

1. Full path of the session history file. Is it a re-enactment condensed from records, or a live capture?
   (If it is a reconstruction the film MUST say so on screen and in the first narration.)
2. Voice-engine gate (may the narration text leave this machine?). Default: offline voice.
3. Voice and language; variant builds?
4. Target length (default 12-15 min for a ~700-line file) and whether there is a hard cap.
5. Narration: drafted by me from the file, then approved by you BEFORE voicing (recommended), or voiced
   straight away? Narrator person: first person ("I") as the agent, or third person.
   [PRECEDENT] census2 narration was voiced before approval; the plan makes approval the default.
6. Output folder (default: a new folder beside the input) and any folder I must not write to.
7. Captions: none, soft side file, or burned in. Look: default dark pager theme, or another.
8. Which sections to skim (long tool outputs) and which must be shown in full (decision points, gates,
   corrections). Chapter cards at human gates: yes or no.
9. Keep the settings in section 2 (720p, AAC 64 kbps), or override (for example 1080p, 96 kbps)?
Do not start until 1, 2 and 5 are answered.

## 5. Workflow [PROPOSED, mostly PRECEDENT from census2]

Stage 0 Intake. Check the input exists, is ASCII, and what style it is. Check the tools: Pillow, ffmpeg,
Kokoro (offline), faster-whisper, a monospace font (Consolas on Windows). If something is missing, say so
and stop; do not install from the network. Scan the text for user names or personal paths and report them.

Stage 1 Parse. Split the file into blocks and chapters (PHASE headings, gates, Corrections, Open items).
Write a map: chapter -> line range.

Stage 2 Narration draft (`narration.md`). One beat per meaningful passage, 20-60 s each, about 165 words
per minute, first person, explaining the WHY of each decision and who decided it (agent or human). Each beat
records the input line range it covers, and the highlight ranges inside it. Rules:
- every number and name in the narration must appear in the input file (Grep to confirm);
- items marked [unconfirmed] or (paraphrase) are narrated as unconfirmed or paraphrased, never as fact;
- numbers written as words for the voice; respellings only at synthesis;
- the opening beat states the re-enactment disclosure when applicable.
GATE: show the narration to the user for approval before voicing (unless the user waived it).

Stage 3 Voice. beats.json, one clip per beat, trim windows, offline recogniser check of every clip against its
text, re-voice any that differ, list any recogniser-only artefacts (for example text invented at the end of a
clip).

Stage 4 Pagination and picture.
- Layout: dark window, slim title bar ("session_history.md - viewer (re-enactment)"), status line in the
  style of less: file name, "lines A-B / total", current phase, right side "PgDn = next page".
- Page size at 1080p was 28 px Consolas, about 118 columns, 22-28 rows [PRECEDENT]; the 720p equivalent is
  to be fixed by the legibility test in section 2 [UNVERIFIED].
- Colour: coloured speaker tags USER / CLAUDE / TOOL, phase bands, accent for decision tags and for
  Corrections / UNVERIFIED headings. Cards (opening disclosure, human gates, Corrections, closing open items)
  use the same pager frame.
- Pagination: greedy fill; each page starts at a block boundary (blank line or PHASE header) and never inside
  a highlight range. If no clean boundary fits, allow one mid-block start and list it in NOTES.md
  [PRECEDENT: census2 page 27 started mid-block].
- Page change: instant cut. For the first 0.6 s of a new page the status line shows an orange "[PgDn]" tag
  (a separate still) so the viewer sees that a key was pressed.
- Highlight: a soft band over the lines being explained. Within a beat, the highlight ranges share the speech
  time evenly (not word-aligned; say so in NOTES.md). Assert programmatically that every highlight range lies
  wholly on the page shown while it is highlighted.
- Dwell: a page stays at least about 8 s [PRECEDENT: census2 min 8.7 s, mean 28.6 s, max 52.0 s]. Report any
  page shown longer than about 50 s and ask whether to split the narration.
- Encode each distinct still once as a short segment (stillimage tuning) and repeat it by concat; census2 had
  102 distinct stills for 29 pages. Intermediates are large (52 MB in census2): delete after the build or
  keep only if asked.

Stage 5 Build. Timeline from the voice lengths, audio mix, loudness once, concat, soft captions file if
wanted, `timeline.json` (pages, segments, stills).

Stage 6 Verify (section 8 plus):
- ffprobe: one video stream, one audio stream, size, fps, resolution 1280x720, audio 64 kbps, durations agree;
- LOOK at one frame inside every beat and at every page change, not just a sample; census2 looked at only 9
  of 80. At least: opening card, a USER block, a TOOL block, each gate card, the corrections view, the closing
  card. Text legible, nothing cut off at the right or bottom edge, status line numbers match the page;
- loudness and true peak against the targets; per-beat level and spread; silence and freeze reports
  explained (freezes are expected on still pages: say so);
- the audio after the 64 kbps encode compared with the source track (correlation, as census2 did for 96 kbps);
- no user name or personal path visible on any frame.

Stage 7 Report. Output path, length, size, beats and words, pages and page changes, verification numbers, a
listening list (numbers and abbreviations as spoken, any clip with a recogniser difference, the disclosure,
the ending, whether 64 kbps sounds rough), what was NOT verified (audio quality, accent, naturalness: the
agent cannot hear), and any narration claim that could not be traced to a line of the input. Ask the user:
do 20-50 s still pages feel too static, and do page changes land at sensible moments?

## 6. Outputs (all in the new folder; the input is untouched)

`<name>_walkthrough.mp4`, `narration.md`, `<name>_captions_for_reference.srt` (named so a player does not
auto-load it), `timeline.json`, `NOTES.md` (settings, honest numbers, verified / not verified, listening
list, disclosures, files), `verify\` (frames and report), `film\` (beats.json, voice clips, scripts), and a
progress log so the job can resume after a context reset. Expected size for 15 min at the section 2 settings:
roughly 20-25 MB.

## 7. Reusable code [PROPOSED]

Keep as scripts in the Video Production project: parse (input -> blocks and chapters), paginate and render
pages (Pillow), build_paged and verify_paged (census2 versions exist in
`TEST_Kstudio\video_census2_session\scripts\` and take `--crf` and `--abr`; they need parameters for
resolution and audio rate, currently 1080p and 96k), plus the existing voice, trim and check scripts from
use case I. Paths to ffmpeg, Python and fonts live in one config, not in the scripts.

## 8. Open items

- [UNVERIFIED] Pillow is available in the Python environment used for video jobs (check at Stage 0).
- [UNVERIFIED] 64 kbps AAC quality and native 720p legibility (section 2).
- [UNVERIFIED] The user has not yet watched or listened to the census2 paged film.
- The highlight band moves by even time shares, not by spoken words; word-aligned highlighting would need
  word timestamps from the recogniser.
- Known census2 defects to avoid: first build showed a sliver of the next line at the bottom of pages (crop
  at the exact end of the last line); a 1-pixel green tick at the far left bottom of some pages; true peak
  0.5 dB over target.
- Fonts are Windows-specific.
- Very long inputs (well over 700 lines): split into parts or set a skim policy.
- Languages other than English: voice and respelling map per language (see Video_Production.md 6.4).
- Optional add-on, out of scope here: real screen recordings of the application to cut in.
