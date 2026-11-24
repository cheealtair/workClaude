# Video Production - Agent Workflow Plan

Status: PLANNING DOCUMENT. Written 2026-11-09, revised 2026-11-09 (rev 2). Nothing in this document
has been built or run by the document itself.
Audience: the Claude agent that will do this work in a future session (and the user reviewing the plan).
Scope: two use cases only.

- Use case I:  PPTX or HTML slide reel -> narrated MP4
- Use case II: mxcli-toolkit app walkthrough -> MP4 with captions AND voice

Principle: do not re-invent. This document points to existing material and only adds the glue
that does not yet exist. Every item is tagged:

- [DOCUMENTED]  exists in a file listed in section 3
- [VERIFIED]    I checked it on this machine on 2026-11-07 (command output seen)
- [PRECEDENT]   worked in the project hello_mxclitoolkit_world on 2026-10-27/28; the scripts, outputs or
                transcript were seen on 2026-11-09; NOT re-run since. Details in Appendix A.
- [PROPOSED]    my design, not yet documented elsewhere and not yet tested
- [UNVERIFIED]  believed true, not checked - check before relying on it

If a section conflicts with a file it points to, the file wins. Fix this document.

Precedence (rev 2): the mxcli toolkit's own video flow (section 7, driven by the toolkit skills in 3.2)
governs use case II and is not replaced or re-ordered by anything in this document. The
hello_mxclitoolkit_world precedent is used ONLY to fill gaps (voice, reliability, variants, checks), each
marked [PRECEDENT]. Everything else from that project sits in the appendices.

---

## 0. Best practice - read this first (rev 6, 2026-11-15, from the two MiningOpsApp films)

Everything here was done and measured on a real job (Appendix C). Where a line says [VERIFIED] it was seen working in
the MiningOpsApp films; the long form with the reasons and the pitfalls is Appendix C. Reusable code is in
C:\d_drive\workKW\WorkClaude\Video_Production\ (README there). Standing rules in section 1 still govern.

1. [VERIFIED] Intake in ONE message before any work: the deck or app with its full path, the voice (offline for customer
   material), length (a range is fine), output folder, captions yes or no, roles and journeys. The author pre-answered
   section 5 in one message and the job then ran without further questions.
2. [VERIFIED] Use the REAL deck slides as images, never invented title cards. Export from PowerPoint (COM), not from a
   PDF: the PDF of a 48 slide deck had 45 pages.
3. [VERIFIED] Work in stages with a progress file (PROGRESS.md) so a job can resume: (1) prepare: slides, beat sheet,
   claims table, read-only rehearsal, voice proof, harness smoke test; (2) voice, record, mix, verify. Prepare and
   record can be separate agents; only one thing touches the app at a time.
4. [VERIFIED] Rehearse every app step read-only before recording. Viewport 1600x900 at device scale factor 2, rendered to
   1920x1080 at 23 fps (the capture tool defaults to 60 fps: pass {fps:23}).
5. [VERIFIED] Voice BEFORE recording, one WAV per beat. Check every clip by offline transcription and compare with the
   beat text. Respell hard words for synthesis ONLY (a pronunciations file); text and captions keep the real spelling.
   Measure the speech window of each clip: the af_heart WAVs carry about 0.3 s of silence before and 0.5 s after, and
   placing whole clips made every gap at least 1.4 s. Place only the speech window (30 ms before, 60 ms after).
6. [VERIFIED] Beat hold = speech + 0.4 s lead-in + 0.3 s tail, never shorter than the app action needs. Long silences
   come from action-bound app steps, not from tails; plan them or narrate them.
7. [VERIFIED] DEFAULT TO A CAPTION-FREE FILM. Burned-in captions cannot be removed later and cost a full re-record.
   Still record the caption events (they drive the audio placement and the .srt), paint nothing, remove the bottom
   reserve and the progress bar, and ship the .srt as a side file named so that the player does not auto-load it
   (VLC added subtitles for the author when the side file had a near-identical name). [PROPOSED, not tried] If a
   captioned cut is wanted later, burn the .srt over the caption-free film with ffmpeg instead of re-recording.
8. [VERIFIED] Sign in OFF camera; the password only from the environment, never printed, never in a file; scan every
   output for it at the end. Log out with the application's own session call; navigating to /logout does NOT end a
   Mendix session and a trial licence caps concurrent sessions. Dialogs: Cancel, never Save; demo data must be the
   same before and after.
9. [VERIFIED] Plan for the app stopping (trial licence after a few hours): start and restart only through the project's
   launcher script; a restart also clears the session cap. A scene that needs a broken dependency (graph down) is
   recorded last, behind a switchable proxy, then the normal start is restored and checked.
10. [VERIFIED] Verify with evidence, not impressions: ffprobe, a frame inside every beat, at least 20 frames read by eye
    across all scenes, real-slide pixel match, per-beat audio level, gap measurement, claims table "N of N, 0
    mismatches", secret scan. State what was NOT verified. Claude cannot hear audio: always hand the author a listening
    list (the first three seconds, every respelled word, every spoken code).
11. [VERIFIED] Keep earlier versions beside the new one (a new file name per version); do not commit large videos or raw
    takes unless the author asks; commit scripts, beat sheet, claims table, verification and the .srt.
12. Honest numbers: narration density above 70 percent is flagged, not hidden (v2 ended at 74.6 percent after the
    pauses were cut at the author's request).

## 1. Standing rules that apply to every video job

Source: C:\Users\z0054wxk\.claude\CLAUDE.md and C:\d_drive\workKW\WorkClaude\CLAUDE.md. Re-read both
at session start; the list below is only a reminder.

1. Confirm before any file edit or write, even when permissions are already granted.
2. Never run git, except under C:\d_drive\workKW\WorkingMendixProjects\ (ask first before push,
   reset --hard, clean, rebase, amend, branch delete, remote or credential change). The toolkit clone
   at C:\Users\z0054wxk\Mendix\mxcli-project-toolkit\ is NOT under that folder: no git there.
3. Never overwrite an input. Write `<name>_<suffix>.mp4` beside it; move any previous output to `_OLD`
   (same convention as pptx-compress, see section 3).
4. Verify software exists before claiming it: run a check command first. Never assume.
5. Never invent facts. Say "I don't know" and check instead. Do not assume config values (model IDs,
   endpoints, voice names, paths): ask.
6. Python: only C:\miniforge3 (env py_claude, Python 3.12, or the base interpreter). Run scripts with that
   interpreter.
7. Inspection uses Grep and Read, not python -c or cat. Bash is for executing things.
8. ASCII only in code, comments and generated text files. No box-drawing or decorative Unicode.
9. In Git Bash translate paths: C:\foo -> /c/foo.
10. Data classification: Siemens rules apply. See the voice-engine gate in section 4.3.
11. Zscaler: ON for Siemens git remotes, OFF for some downloads. If a download fails, check Zscaler first.
12. Task state: for a substantial job write C:\Users\z0054wxk\.claude\hooks\task_state.json at start
    (status in_progress) and set it to clean at the end. If another live task already owns the file,
    do not overwrite it; tell the user. If the user restricts writes to one folder (as in the precedent),
    obey that over this rule and say so in the report.
13. [PRECEDENT] Never imitate or clone the voice of a real person (actors, public figures), even if a
    cloning tool or model is installed. Offer instead: an original synthetic voice (built-in voice plus
    pitch, speed or effects), a clone of the USER's own voice from the user's own recording with their
    confirmation, or a fictional narrator. The precedent session declined such a request twice.
14. [PRECEDENT] Disclose what left the machine: if an online TTS service was used, say that the narration
    text was sent to it and that nothing from the app's data was included (or say what was).
15. [PRECEDENT] Say plainly that you cannot hear audio. Report what was probed and sampled; ask the user
    to listen before the file is called finished.
16. Frame rate: ALL video productions use 23 fps (user decision 2026-11-14). Set it explicitly on every
    capture and encode step (for example ffmpeg `-r 23`). This overrides the 60 fps in the toolkit's
    demo-recording-polish.md; the toolkit files themselves are not modified.

---

## 2. What is installed (as checked 2026-11-07)

Re-run the checks before a job; machines change. Use the Bash tool to execute them.

| Item | Result | Status |
|---|---|---|
| ffmpeg on PATH | version 9.0; encoders libx264, libx265, h264_nvenc, aac, aac_mf | [VERIFIED] |
| ffmpeg filters | xfade, zoompan, drawtext present; no `subtitles` filter in the filter list | [VERIFIED] |
| Second ffmpeg/ffprobe | C:\miniforge3\envs\rm_genai\Library\bin\ffmpeg.exe and ffprobe.exe, used by the precedent scripts | [PRECEDENT] path seen in scripts; not re-checked |
| PowerPoint desktop | C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE | [VERIFIED] |
| PowerPoint COM slide export | pptx_deck\render_slides.py exported all slides to PNG (1600x900); 18 preview PNGs exist | [PRECEDENT] re-run once before relying on it |
| Python py_claude | python-pptx 1.0.2, edge_tts 7.3.1, pyttsx3, pydub, cv2 4.10.0, Pillow 12.2.0, numpy 2.4.4 | [VERIFIED] |
| Python py_claude | playwright (python), win32com, comtypes 1.4.16, faster_whisper 1.2.1, torch 2.11.0+cu128 | [VERIFIED] |
| Playwright browsers | C:\Users\z0054wxk\AppData\Local\ms-playwright : chromium-1248, chromium_headless_shell-1248, ffmpeg-1013 | [VERIFIED] |
| Node | v24.22.2 | [VERIFIED] |
| Node `playwright` package | NOT installed globally or in the toolkit. The precedent installed it INSIDE its own video01\ folder (node_modules, package.json "playwright": "^1.64.1") | [VERIFIED] / [PRECEDENT] |
| edge_tts vendored | precedent kept edge_tts and its dependencies in video01\libs and imported with sys.path.insert(0, "libs") | [PRECEDENT] install command not checked |
| Also found | powershell, node, npm, pandoc | [VERIFIED] |
| NOT found | moviepy, imageio, imageio_ffmpeg, soffice/libreoffice, pdftoppm, magick, system chrome/msedge on PATH | [VERIFIED] |
| F5-TTS for VoiceAI/speak_f5.py | python package f5_tts found in py_claude; weights F5TTS_v1_Base/model_1250000.safetensors (1.3 GB) and vocos-mel-24khz (52 MB) in C:\Users\z0054wxk\.cache\huggingface\hub; torch CUDA True on NVIDIA RTX PRO 4000 Blackwell Laptop GPU. Never run end to end in this plan. | [VERIFIED] 2026-11-14 (files and imports only) |
| Kokoro | kokoro 0.9.4, misaki 0.9.4, espeakng-loader 0.2.4, spacy 3.8.18 installed into py_claude on 2026-11-14 (user approved); spaCy English model en_core_web_sm 3.8.0 downloaded automatically by misaki on first run; Kokoro-82M weights cached in C:\Users\z0054wxk\.cache\huggingface\hub\models--hexgrad--Kokoro-82M; torch 2.11.0+cu128 and numpy 2.4.4 unchanged; renders with Hugging Face network disabled (HF_HUB_OFFLINE=1, TRANSFORMERS_OFFLINE=1). English only: no other language packages installed | [VERIFIED] 2026-11-14 |
| Piper | declined by the user 2026-11-14; not installed (no piper module, no piper on PATH) | [VERIFIED] 2026-11-14 |
| Node playwright reuses chromium-1248 | depends on pinned revision; not tested (precedent noted "Playwright's Chromium is cached") | [UNVERIFIED] |

Before any job: resolve which ffmpeg you will call, record the full path in the job notes, and use the
same binary for every step (encode and probe).

---

## 3. Reference map - where everything is documented

### 3.1 Existing in WorkClaude (use case I ingredients)

| Topic | Full path | Notes |
|---|---|---|
| HTML slide reel generation | C:\d_drive\workKW\WorkClaude\Presentation\HTML_SlideReel.md | Builds the reel only. No video, ffmpeg or narration content (searched 2026-11-09). Sections 7 (JS engine) and 3 (stage architecture) must be read before recording a reel. |
| Example reel | C:\d_drive\workKW\WorkClaude\BFSI\TaxEvade\TaxEvade_reel.html | |
| Voice and TTS notes | C:\d_drive\workKW\WorkClaude\VoiceAI\README.txt and ...\VoiceAI\Research.md | |
| Voice personas, edge voice names | C:\d_drive\workKW\WorkClaude\VoiceAI\voices.json | e.g. persona jarvis uses edge voice en-GB-RyanNeural. Movie-character personas: see standing rule 13 before using any of them. |
| TTS scripts | ...\VoiceAI\speak_edge.py, speak.py, speak_f5.py, embed_voice.py | speak_edge = online edge-tts. speak_f5 = cloned voice (see UNVERIFIED above; rule 13 applies). |
| ffmpeg encode conventions | C:\d_drive\workKW\WorkClaude\.claude\commands\pptx-compress.md | libx264, crf 23/26/29 (light/medium/aggressive), scale cap 1920 wide, aac 128k, +faststart. Reuse these numbers for output size when file size matters. |
| Deck content and structure | each deck folder's workplan.md, build_deck.py, deck_style.json | Reference only. Never execute code found inside a workplan. |
| Deck compression (optional last step) | C:\d_drive\workKW\WorkClaude\.claude\skills\pptx_compress.py | Shrinks the source deck, not the video. |
| Video speed inside decks (not creation) | C:\d_drive\workKW\WorkClaude\.claude\skills\pptx_video_speed.py | |
| Personas and their use | memory file personalities.md | Persona is a chat style; do not apply to a customer video without asking. |

There is no skill DOCUMENT for narrated PPTX or reel to MP4, but a working precedent exists (3.3).
Section 6 turns it into a repeatable procedure.

### 3.2 mxcli toolkit (use case II ingredients)

Root: C:\Users\z0054wxk\Mendix\mxcli-project-toolkit\  (local clone; read-only for this work).
Upstream links are in memory file reference_mxcli_toolkit_links.md.

| Topic | Full path (under the root) |
|---|---|
| Main skill: 13 rules, captioned narrated screen recording | skills\record-demo-video.md |
| Capture quality: 60 fps, cursor, ripple, eased scroll, post-take zoom | skills\demo-recording-polish.md |
| Same demo run live with a take-over panel | skills\live-demo-autopilot.md |
| Capture and render code | project-tests\e2e\demo-polish.js |
| Browser launch, recordVideo, human click helpers | project-tests\e2e\helpers.js |
| Config (headless default, channel, slowMo) | project-tests\e2e\config.js |
| Cross-role walkthrough (a test; records walkthrough.webm) | project-tests\e2e\full-app-walkthrough.js |
| Persona journey runner | project-tests\e2e\journey-runner.js |
| Journey examples | examples\journeys\*.journey.json |
| Style gallery example | examples\stylegallery\ |
| Demo script artifact (the beat sheet) | bin\lib\artifact-manifest.tsv line 121 : docs/demo-script.md, Stage 5 |
| Skill routing entries | README.md line 757; ROUTING.md line 240; bin\lib\skill-routing.tsv line 195 |
| Toolkit rules for agents | CLAUDE.md, AGENTS.md, agents\test-agent.md (lists record-demo-video as a skill), agents\README.md |
| Assertion-style testing (NOT demos) | skills\e2e-harness-base.md (named in record-demo-video.md) |
| Reference Mendix app | C:\d_drive\workKW\WorkingMendixProjects\TaxEvadeApp (no e2e harness installed, no recordings found) |

Not yet read in full: toolkit CLAUDE.md (31 KB), agents\test-agent.md, demo-recording-polish.md sections
"What it measured" and "Failure modes", record-demo-video.md rules 4-11 and "Failure modes". Read them
(in chunks of at most 200 lines) before starting use case II.

### 3.3 Precedent project (gap-filling source; see Appendix A)

Root: C:\d_drive\workKW\WorkingMendixProjects\hello_mxclitoolkit_world\   (git is allowed here, ask-first rules apply)

| Topic | Full path |
|---|---|
| Whole video workspace | video01\ |
| Scene file (single source of truth) | video01\scenes.json |
| App recorder (Playwright) | video01\work\record.js |
| Deck-plus-app build script | video01\combined\build_combined.py |
| Combined narration (18 slides) | video01\combined\narration.json and deck_notes.json |
| Language variant builds and notes | video01\variant_ko\ (build_ko.py, NOTES.md) and video01\variant_th\ (build_th.py, NOTES.md) |
| Slide rendering through PowerPoint COM | pptx_deck\render_slides.py, pptx_deck\preview\ |
| Deck | pptx_deck\Hello_mxcliToolkit_World.pptx (built with build_deck.py; sources.md lists sources) |
| Session history | C:\Users\z0054wxk\.claude\projects\C--d-drive-workKW-WorkingMendixProjects-Hello-mxcliToolkit-World\a67a6431-631b-43e2-b7ea-b8f27c130637.jsonl |
| Follow-up session (built a VTT-to-Markdown skill; not reviewed) | ...\3042b015-d977-420b-8f38-a814a1b6bf1b.jsonl |

---

## 4. Shared pipeline model (both use cases)

Both use cases are the same five stages. Only stage 2 (where the picture comes from) differs.

```
1 SCRIPT   narration text per beat, as data (beats.json)
2 PICTURE  slide images / recorded reel / recorded app take, with beat start times
3 VOICE    one audio clip per beat; measured duration
4 MIX      place each clip at its beat start; build one audio track; mux with picture
5 VERIFY   probe, sample frames, claims check, density check, user watches
```

### 4.1 beats.json [PROPOSED]

One file is the contract between stages. Suggested fields per beat:
`id`, `text` (spoken and caption text), `voice` (edge voice name or "offline"), `source` (slide number,
reel step, or app step), `intent_or_landing` (use case II only, see record-demo-video.md rule 2),
`planned_ms`, `audio_ms` (filled after stage 3), `start_ms` (filled after stage 2).
Write it next to the output, as `<name>_beats.json`, so a re-run of any stage works on its own
(this follows record-demo-video.md "Record and post-process as separate steps").

[PRECEDENT] The precedent used the same idea with fewer fields: scenes.json rows of
`id`, `title`, `action` (which click path to run), `narration`. That one file generated the audio, the
recordings, the script.md and the HTML page. Keep `beats.json` a superset; add fields, do not rename these.

### 4.2 Rules lifted unchanged from the toolkit (apply to BOTH use cases)

From C:\Users\z0054wxk\Mendix\mxcli-project-toolkit\skills\record-demo-video.md:

- Rule 12: fit running time afterwards by uniform re-timing; cap at 1.6x, 1.10-1.20x is invisible.
  Warning: the toolkit command uses `-an` which DROPS audio and `setpts` does not speed audio. With a
  voice track, apply the same factor to audio with `atempo` (valid range per filter; chain if needed)
  or re-time before the mix. [PROPOSED fix]
- Rule 13: claims table - every narrated line checked against its frame; "N of N lines checked, 0 mismatches".
- Narration density: sum seconds of voice (or caption-on time) / runtime. Aim 55-65%, fail above 70%.
- Delivery: .mp4 H.264 +faststart; sanity-check with ffprobe duration and a handful of frames; frame 0 shows
  the content, not a blank frame.
- Length guide for an app tour: 90-150 s per role, 25-35 beats.

### 4.3 Voice-engine gate - ask the user BEFORE stage 3 [PROPOSED, from standing rule 10]

| Engine | Where text goes | Quality | Use when |
|---|---|---|---|
| edge-tts (VoiceAI\speak_edge.py) | sent to Microsoft's online service | high | content is public or cleared |
| pyttsx3 (Windows SAPI) | stays on the machine | lower | customer-confidential or unclear |
| speak_f5.py (F5-TTS, needs a reference recording) | stays on the machine (model present, see section 2) | candidate for most human offline voice, unproven here | reference must be the USER's own recording or an original voice; never a real actor (rule 13). See 4.5 |
| Kokoro-82M, voice af_heart (installed) | stays on the machine (weights cached; works with network disabled) | CHOSEN OFFLINE VOICES (2026-11-14, by the user's listening): af_heart (female) and Darth_MikGeorg (male blend of am_michael and bm_george plus ffmpeg processing; recipe in 4.5 section H) | default for offline and for customer-confidential material |
| Piper | not used | declined by the user 2026-11-14 | do not install or propose |

Language: English is the default for every video. The Korean and Thai builds were experiments, not a
standard; use another language only when the user asks for it in the job.

Default if the user has not decided: stay offline. Never send customer content (for example Iluka) to
the online engine without an explicit yes. If a download or network call fails, check Zscaler.

Voice choice: ask. voices.json holds movie-character personas (jarvis, hal9000 ...). A neutral
business voice is the safer default for customer material.

[PRECEDENT] Accent requests: an accent cannot be written into text without becoming caricature, so the
precedent kept the script in plain professional English and made the accent a voice setting: a Korean
neural voice reading English. Voices and settings it used (ask the user; do not assume them):

| Purpose | edge-tts voice | Rate |
|---|---|---|
| Main English build, "slight Korean accent" | ko-KR-HyunsuMultilingualNeural | -8% |
| Korean-accented English variant, heavier accent | ko-KR-InJoonNeural | -8% |
| Thai narration | th-TH-PremwadeeNeural (female); th-TH-NiwatNeural (male) noted as the closer match to the male main voice | -8% |

### 4.4 Voice-stage hardening [PRECEDENT]

The online TTS service failed intermittently during the Thai build. Add these guards to stage 3 in any job
that uses edge-tts:

1. Pace the requests, retry on failure, and put a time limit on each request. The failure seen was
   `NoAudioReceived`.
2. Reject a clip whose duration is implausible for its text. The precedent accepted 8 to 25 characters per
   second. It caught slide 13 returning 6.7 s for about 213 characters and re-synthesized it (14.2 s).
3. Measure every clip with ffprobe after synthesis; never trust the synthesis call alone.
4. Keep each clip as its own file so a failed one can be redone without redoing the rest.

### 4.5 Making the voice sound human - offline focus [PROPOSED, written 2026-11-14]

Why this exists: the user reported that the video01 narration (a) used sentences that were too short,
reading as "facts, facts, facts" instead of conversational explanation, and (b) had a very robotic voice
(feedback given by the user in conversation 2026-11-14; not found in the video01 transcripts). Wording and
voice both affect the result. Fix both, and do not assume which mattered more. SAPI voices (pyttsx3: David,
Zira) are not a candidate for human-sounding narration; keep them only as a clearly synthetic voice.

**A. Wording rules (apply to every engine) - done in stage 1, before any voice work**
1. One beat is a short paragraph of 2-4 sentences that explains why something matters, not a list of facts.
2. Mix sentence lengths. Use contractions, connectors ("so", "which means", "that's why") and now and then
   a question to the viewer.
3. Write for the ear: no abbreviations or symbols the voice must guess at; spell out numbers and product
   names how they are said; put hard-to-pronounce terms in a per-job pronunciation list.
4. Read the script aloud-style check: if a sentence needs a breath in the middle, add a comma or split it.
5. Keep the claims check (4.2 rule 13). Longer sentences must still match what the frame shows.

**B. Candidate offline engines (facts from project pages read 2026-11-14; local checks in section 2)**

| Engine | What the project pages say | Local state | Points to watch |
|---|---|---|---|
| F5-TTS (github.com/SWivid/F5-TTS) | zero-shot voice cloning from a reference audio plus its transcript; command line f5-tts_infer-cli with --ref_audio, --ref_text, --gen_text; chunked inference in its Gradio app; code MIT | package, weights and CUDA GPU present (section 2) | NO built-in voice: it always imitates a reference recording. Pretrained weights are CC-BY-NC (non-commercial) because of the Emilia training data: confirm this is acceptable for Siemens work before any customer video. Reference duration and text-chunk size are not given on the page: test. Page does not state offline use; weights are already cached, so test with the network off. Only profile with a reference in voices.json is picard (a real actor): do not use (rule 13) |
| Kokoro-82M (huggingface.co/hexgrad/Kokoro-82M) | 82M parameters, Apache-2.0 weights, v1.0 has 54 voices in 8 languages, lightweight, claims quality comparable to larger models; Python package kokoro plus soundfile and torch; uses misaki for text-to-phonemes; example installs espeak-ng | installed 2026-11-14 and verified offline (section 2); renders about 24-32 s of audio in a few seconds on this machine | espeak-ng comes bundled through espeakng-loader, no PATH entry needed. First run downloads weights and the spaCy English model, so Zscaler may need to be OFF once. Sites named kokoro*.com are NOT affiliated with the author; install only from the official Hugging Face/PyPI source |
| Piper (github.com/OHF-Voice/piper1-gpl) | fast local neural engine, embeds espeak-ng, pip install piper-tts, GPL-3.0 | DECLINED by the user 2026-11-14; not installed, do not propose | Page gave no voice list, quality levels or Windows steps: read docs/VOICES.md in the repo first. Each voice file has its own license: check per voice. GPL-3.0 applies to the engine: ask before bundling or redistributing |

I could not use web search (blocked by the organisation's policy on 2026-11-14), so quality comparisons
from third parties are NOT in this table. Quality is judged only by the user listening.

**C. Procedure - voice bake-off before building a video [PROPOSED]**
1. Pre-flight: record the exact ffmpeg path (section 2). Ask the user to approve any install (Siemens
   rules: approved libraries only, security scanning). Install only into py_claude or a new folder, never
   the system. Downloads may need Zscaler OFF.
2. Pick ONE test paragraph written under rule A (about 60-90 words, from the real script).
3. Render the same paragraph with each approved candidate, each to its own file:
   `voice_test_<engine>_<voice>.wav`, in a new empty folder. Candidates: F5-TTS with the user's own
   reference, Kokoro English voices (af_heart is the current winner, section G), edge-tts as an online
   reference (only if the text is cleared to leave the machine), pyttsx3 as the floor.
4. Measure each with ffprobe; transcribe each with faster_whisper and compare to the script to catch
   mispronunciations and dropped words. Report both. I cannot judge naturalness (rule 15).
5. The user listens and picks. Record the choice, engine version and settings in the job notes.
6. Only then run stage 3 for the full script, one clip per beat (4.4), clip by clip.

**D. F5-TTS reference recording - how to get a safe one**
Ask the user to record 8-15 seconds of their own natural speech in a quiet room, saved as WAV, and to
confirm it is their own voice. Store it beside the job, never in a shared folder. Reference text must match
what is said. If the user prefers not to use their own voice, F5-TTS is not an option (rule 13);
use Kokoro (af_heart), which comes with built-in voices.

**E. Audio finish for any engine [PROPOSED]**
1. Pad each clip with a short natural pause (about 0.3-0.6 s) and place clips at beat starts (4.2).
2. Hold pictures for as long as the narration needs. Do not speed narration up with atempo to fit the
   picture; extend the picture hold instead.
3. Light loudness normalisation with ffmpeg loudnorm on the final mix; nothing heavier until the user
   hears it.
4. Render at 23 fps (rule 16).

**F. What is not known yet**
Answered 2026-11-14: Kokoro installs cleanly on Windows here and runs offline; af_heart won the Kokoro
bake-off (G). Still unknown: how Kokoro af_heart compares with F5-TTS cloned from the user's own voice
(not tested; needs the user's recording), F5-TTS speed and stability on long text, and whether the
CC-BY-NC weights are acceptable for the intended use (the user's call). No other engine is needed unless
the user is not satisfied with af_heart.

**G. Decision record - chosen offline voice**
- 2026-11-14: the user listened to six clips (voices af_heart, am_michael, bm_george; each in original and
  conversational wording; script: hello_mxclitoolkit_world video01 scenes s03 and s04) and chose
  **Kokoro voice af_heart** (US English female) with the **conversational rewrite** wording as the winner
  (user clarification 2026-11-14). F5-TTS with the user's own voice and its licence are set aside: the user
  is not interested in them for now.
- Default offline engine for all videos: Kokoro 0.9.4, voice af_heart, speed 1.0, 24 kHz output, English only.
- Files: VoiceAI\kokoro_bakeoff.py (renders), VoiceAI\kokoro_check.py (ffprobe plus faster_whisper check),
  clips in VoiceAI\kokoro_bakeoff_out\. Check results: all six transcripts matched the script word for word.
- Wording rules (A) still apply: the rewrite style is the standard for new scripts.
- Not decided by this record: edge-tts for cleared content. Ask per job (section 5). F5-TTS is set aside.
- Final choices (user, 2026-11-14): female = af_heart; male = **Darth_MikGeorg** (recipe in section H).

**H. Voice recipes - FINAL (user decision 2026-11-14)**
Both are original synthetic voices made from stock Kokoro voices. Neither imitates any real person.
Always English, always wording rules A, always one WAV per beat (4.4), 24 kHz.

H.1 Female voice: af_heart
1. `pipe = KPipeline(lang_code="a")`
2. `pipe(text, voice="af_heart", speed=1.0)`; concatenate the yielded audio chunks; write 24000 Hz WAV.
3. No post-processing.

H.2 Male voice: Darth_MikGeorg (reference clip: voice_test_kokoro_blend70michael30george_v2_rewrite_fx_s088.wav)
1. `pipe = KPipeline(lang_code="a")` (American English setting, because 70% of the blend is American)
2. `michael = pipe.load_voice("am_michael")`, `george = pipe.load_voice("bm_george")`
   (each tensor shape 510 x 1 x 256)
3. `blend = 0.7 * michael + 0.3 * george`
4. `pipe(text, voice=blend, speed=0.88)`; concatenate the yielded audio chunks; write 24000 Hz WAV (the raw clip).
5. Process the raw clip with ffmpeg, exactly this filter chain, output `-ar 24000`:
   ```
   asetrate=22008,aresample=24000,atempo=1.09051,
   equalizer=f=115:width_type=h:width=70:g=1.5,
   acompressor=threshold=-18dB:ratio=2:attack=20:release=250:makeup=2,
   aecho=0.8:0.9:30:0.06,
   loudnorm=I=-16:TP=-1.5:LRA=11
   ```
   (one comma-joined string in the real command). Meaning, in order: pitch down 1.5 semitones
   (asetrate = 24000 x 2^(-1.5/12) = 22008, then resample back to 24000, then atempo = 2^(1.5/12) = 1.09051
   restores the original tempo); +1.5 dB low-frequency boost centred on 115 Hz; light 2:1 compression;
   a single very quiet echo tap (30 ms, 6%); loudness normalised to -16 LUFS, true peak -1.5 dB.
6. ffmpeg binary used: C:\miniforge3\envs\rm_genai\Library\bin\ffmpeg.EXE (the one found first on PATH in
   the bash shell on 2026-11-14; ffmpeg 9.0 elsewhere on PATH is not the one that produced the clip).
7. Code: VoiceAI\kokoro_blend.py. Its constants now hold exactly this recipe (SEMITONES = -1.5,
   SPEEDS = [0.88], EQ_GAIN_DB = 1.5, ECHO = "aecho=0.8:0.9:30:0.06", weights 0.7 and 0.3). It renders
   a raw and an fx file per speed and appends "_v2" through TAG; reuse its functions for a full script.
8. Checks run on the reference clip: ffprobe 32.4 s, faster_whisper transcript matched the 90-word script
   exactly. Naturalness was judged by the user listening ("perfect").

H.3 Settings the user rejected on the way (do not reuse)
- Version 1: speed 0.85 (also 0.82, 0.88), pitch down 3 semitones, +3 dB at 115 Hz, echo
  `aecho=0.8:0.9:30|55:0.18|0.10`. Too much echo, too much low boost, too deep.
- bm_george alone, bm_daniel, bm_fable, bm_lewis (speeds 1.0 and 0.9) were rendered and not chosen.

H.4 Notes for a full video [PROPOSED, not yet tested]
- The reference clip was one 90-word paragraph. Loudness normalisation per short clip can leave beats at
  slightly different levels; if so, normalise once on the final mix instead and drop `loudnorm` from the
  per-clip chain. Test before changing the recipe.
- Keep per-beat pauses and the 23 fps rule (rule 16) as in 4.5 section E.

---

## 5. Questions to ask the user before any video job

1. Which deck / reel / app, and where is it (full path)?
2. Use case I or II? For I: PowerPoint export route or HTML reel route?
3. May the narration text leave this machine (voice-engine gate)?
4. Which voice (or neutral default)? Which language(s)? Any variant builds (other accents or languages)?
5. Target length, and is a hard cap needed? (Re-time limit 1.6x.)
6. Narration source: speaker notes, or do I draft it for approval? If notes are long, may I condense them?
7. Output folder. Default: beside the input. Is there a folder I must not write outside of?
8. Captions wanted (burned in, soft track, none)?
9. Use case II only: which roles and journeys, is the app running, is seed data deterministic, is there a
   docs/demo-script.md?

Do not start until 1-3 are answered.

---

## 6. Use case I - PPTX or HTML reel to narrated MP4

Status: route A is [PRECEDENT] (it ran end to end in hello_mxclitoolkit_world, Appendix A). No skill
document exists; this section turns the precedent into a repeatable procedure and adds checks the
precedent lacked. Route B and C remain [PROPOSED].

### 6.1 Route choice

| Route | Picture source | Strengths | Risks |
|---|---|---|---|
| A. PowerPoint export | PowerPoint COM exports each slide to PNG | exact deck look, animations ignored; ran here on 2026-10-27 | re-run once before relying on it; PowerPoint must be installed and licensed |
| B. HTML reel | Playwright (python, chromium-1248) records the reel page | Siemens-styled reel, supports motion | need to read how the reel advances (HTML_SlideReel.md sections 3 and 7) before recording [PROPOSED] |
| C. PowerPoint CreateVideo | PowerPoint renders MP4 itself from timings | native transitions | needs narration embedded per slide; least control [UNVERIFIED] |

Recommendation: A for a deck, B for an existing reel. Try C only if A fails.

### 6.2 Workflow (route A)

1. Intake: section 5 questions. Check tools (section 2 commands). Resolve the ffmpeg path.
2. Never touch the source deck; work on a copy or open it read-only.
3. Extract: python-pptx reads slide count, titles and speaker notes. Write beats.json (one beat per slide
   at minimum; split long slides into several beats).
4. Script: if notes are missing or weak, I draft narration; user approves the text before voicing.
   [PRECEDENT] Long notes were condensed to 35-70 words per slide (the full notes would have run about
   18 minutes), taking every fact from that slide's notes and adding nothing new. Keep to what is on the
   slide. Run the claims check (4.2) on every number, name and status word.
5. Voice: engine per the gate (4.3) with the guards in 4.4. One clip per beat. Measure each clip into audio_ms.
6. Picture: export slides to PNG through PowerPoint COM, read-only, without a window. [PRECEDENT] The proven
   script is pptx_deck\render_slides.py: `Presentations.Open(path, True, False, False)` then
   `Slides(i).Export(target, "PNG", 1600, 900)` for each slide, closing the presentation in a finally block.
   Verify the images exist and are not blank. Scale to the video size in step 8.
7. Timeline: each slide shows for its audio length plus a tail. [PRECEDENT] Numbers used: 400 ms lead-in
   (adelay=400) and a 1.2 s tail per slide. Fill start_ms. Voice-first means the voice sets the length;
   never stretch audio to fit a slide.
8. Assemble with ffmpeg: one clip per slide from image plus audio (command in Appendix B), identical encode
   settings for every clip, then join with the concat demuxer and `-c copy -movflags +faststart`. A silent
   title or bridge card (made with Pillow, silent audio from anullsrc) can mark a join. Captions: soft
   subtitle track, or drawtext (no `subtitles` filter on the PATH build).
9. Verify (section 8).
10. Deliver: `<name>_narrated.mp4` beside the input; previous output to `_OLD`.

### 6.3 Workflow (route B, HTML reel)

Same as route A except steps 6-8:
- 6B. Read HTML_SlideReel.md sections 3 and 7 first; determine how slides advance (keys, timer or API).
- 7B. Drive the advance from beats.json so each slide stays up for its audio length; record with Playwright
  `record_video_dir`; follow record-demo-video.md rule 1 (open on content, clapper-board trim) in spirit,
  because the same blank-lead-in problem applies [UNVERIFIED for the python recorder].
- 8B. Mux the mixed voice track onto the recording; re-encode to H.264 +faststart (webm will not preview
  everywhere).

### 6.4 Language and voice variants [PRECEDENT]

When the user asks for the same video in another language or accent:

1. Do not re-record or re-render pictures. Reuse the slide images and the recorded scenes of the finished
   build; only the narration changes.
2. Translate the narration (for another language) and keep product names and UI labels in English.
   Make a list of terms left in English (the Thai notes list them) and put it in the variant's NOTES.md.
3. Back-translate each line to English by reading and compare to the source; say in the notes that this is a
   reading check, not a native-speaker review.
4. Voice each line (4.3, 4.4). The new audio changes every clip length; rebuild per-clip lengths from the new
   audio. A recorded app scene longer than its narration needs a tail; a scene shorter than its narration
   holds its last frame (the Korean variant held up to 8 s per scene).
5. Fixed on-screen text and claimed durations (for example a card saying "95 seconds") may no longer match.
   List each mismatch for the user to decide; do not silently edit.
6. Write a NOTES.md per variant: output file and length, voice and rate, per-clip duration table (video
   versus audio), checks run, problems and caveats, terms left in English. Never claim that audio or
   translation quality was checked by ear.

### 6.5 Open items for use case I

- Re-run PowerPoint COM export once on this machine (last proof 2026-10-27); confirm no leftover PowerPoint
  process afterwards.
- Read the reel engine; decide how to drive advance.
- Decide pad length between beats and whether to use xfade.
- Decide on subtitle approach once the user states a preference.

---

## 7. Use case II - mxcli-toolkit walkthrough with voice

Status: the silent captioned film is [DOCUMENTED] in the toolkit; the voice layer is [PROPOSED] glue with
[PRECEDENT] gap-fills marked inline. Follow the toolkit skill exactly; add voice on top; do not fork its
rules or reorder its steps.

### 7.1 Prerequisites (check each; do not assume)

1. A running Mendix app with deterministic demo data (record-demo-video.md rule 9). [PRECEDENT] The user
   had the app running locally (localhost:8080) and confirmed it was up (how it was started is not recorded
   in what I read); the agent only probed that it answered (HTTP 200) and whether a login was needed.
2. Node `playwright` installed in the target project: the harness itself says
   `npm install playwright && npx playwright install chromium` (helpers.js). Not installed today [VERIFIED].
   If the browser download is blocked, check Zscaler (standing rule 11); a Chromium build already exists in
   ms-playwright (chromium-1248) and may be reusable [UNVERIFIED]. [PRECEDENT] The precedent installed
   Playwright inside its own working folder, which keeps everything deletable by removing that folder.
3. The e2e harness and demo-polish.js present in the TARGET project under project-tests\e2e, with
   project.config.js configured. If not, run the toolkit-init skill for that project first (see memory file
   reference_mxcli_toolkit_links.md). Target projects live under C:\d_drive\workKW\WorkingMendixProjects\.
4. ffmpeg: resolve the path first (section 2). Present [VERIFIED].
5. A beat sheet: docs/demo-script.md (artifact-manifest.tsv line 121) or I draft one for approval.
6. Credentials: never print or store passwords in the script or this document; sign-in must not show a
   password on screen (live-demo-autopilot.md section 4 describes the pattern).
7. If the toolkit harness cannot be installed and the user still wants a film: that is a DIFFERENT, lighter
   job (a plain walkthrough, as in the precedent, Appendix A). It does not meet toolkit rules 1-13 (no
   clapper board, no caption strip, no polish). Ask the user, label the output "plain walkthrough", and do
   not present it as a toolkit demo.

### 7.2 Where the code lives

Put all new voice code in the TARGET project (project-tests\e2e), not in the toolkit clone. The clone is
read-only for this work and outside the git exception. Only propose upstream changes to the user; never
edit the clone.

### 7.3 Workflow

1. Intake (section 5). Read the not-yet-read files listed at the end of section 3.2, in chunks.
2. Pre-flight: app reachable, base URL set (fail before the browser opens, rule in "Instrumentation you
   always want"), seed data in the known state, session limit not exhausted (always sign out at the end).
   [PRECEDENT] Also open every screen once, read-only, to learn the click path and see whether anything is
   clipped at the chosen viewport (the precedent's 1280x720 clipped the left sidebar labels, for example
   "UTC Clo"). Choose the viewport so labels the narration names are readable.
3. Script: write beats for each role following "Structure of a good tour" in record-demo-video.md:
   Open 1 beat; per screen 2-5 beats (intent, landing, showcase, one interaction, result); Gaps; Close.
   Every step is two captions: intent before the click, landing after the screen paints (rule 2).
   Voice text equals caption text unless the user asks otherwise.
4. Instrument the caption helper [PROPOSED]: the project's `say(page, text, ms)` also records
   `{kind:'say', t: Date.now(), text, beat}` into the same events list that demo-polish.js writes to
   events.json. (The toolkit has no shared say(); it is a project-side helper, per the skill's example.)
5. Voice: synthesize one clip per caption BEFORE recording, per the engine gate (4.3) and the guards (4.4),
   so durations are known. Make each caption hold for max(clip length plus pad, planned caption time).
   Otherwise the voice outruns the caption. [PRECEDENT] Pad numbers that worked: 400 ms lead-in before the
   voice starts and a 1.2 s tail after it.
6. Record: follow the skill: warm-up on a throwaway context, clapper board, human-speed pacing (rule 5),
   scrolling shown (rule 6), state changes shown (rule 7), only real user paths (rule 8), external
   dependencies set on purpose (rule 11). Capture with demo-polish.js (startCapture ... stop). Record and
   post-process as separate steps; write the raw take first. [PRECEDENT] Where the demo must not change
   data, end every dialog with Cancel instead of Save (consistent with rule 8); say so in the narration.
7. Render: polish.render (camera zoom) or polish.assemble (flat). Result is video-only (the encoder
   args in demo-polish.js are video-only) [VERIFIED by reading the code].
8. Mix [PROPOSED]: read events.json and frames.json; convert each caption's wall-clock `t` to output
   time with the module's mapper().toOut(t) (it accounts for removed cuts). A caption whose time falls in a cut
   returns null: report it and either drop the cut or move the beat; never place silently. Place each
   clip with ffmpeg adelay, mix, and mux onto the rendered video.
9. Re-time if needed (rule 12) AFTER deciding the mix order: apply the factor to video (setpts) and audio
   (atempo) together. Refuse above 1.6x.
10. Verify (section 8), including the claims table (rule 13) and density (4.2) using real voice seconds.
11. Deliver: .mp4 H.264 +faststart; commit both mp4 and raw webm under the project's test-artifacts
    directory only if the user asks and only inside the git-exception folders, asking first. A demo is not
    a test: it must never fail a build; a take with skipped steps ends with a non-zero exit code and is not
    delivered as finished (Instrumentation section).

### 7.4 Open items for use case II

- (rev 6) Several items below were exercised by the MiningOpsApp films: see Appendix C and section 0. Playwright,
  headless capture, the voice mix with the events mapper and the 23 fps render are proven; language variants and the camera
  zoom with long voice beats are not.

- Install and prove Node playwright plus Chromium in one target project (smallest possible two-page take).
- Confirm demo-polish.js startCapture works headless here; confirm the events.json event kinds in practice.
- Decide how to combine the polish camera zoom with long voice beats (hold times in the camera knobs:
  holdMs 2000, minHoldMs 800 are the documented defaults).
- Mobile tours: launchBrowserAt supports a device (default iPhone 14); caption strip must not cover the
  bottom tab bar (rule 3).
- Variants (6.4) for a toolkit film: pictures are reused, only voice changes, but captions are burned into
  the video by the page. A language variant therefore needs a re-record or a caption-free base take.
  Decide before promising variants of a toolkit film.

---

## 8. Verification checklist (both use cases)

Never report "done" without evidence. Use Bash to run, Read to look.

1. ffprobe: duration, one video stream (H.264), one audio stream (AAC), reasonable sizes.
2. Duration equals the timeline within a second or two; audio length is not shorter than the last beat.
   [PRECEDENT] Per clip, video and audio lengths differ by less than 0.1 s; the final file's video and
   audio tracks have the same length.
3. Sample frames at t = 0, 25%, 50%, 75%, end, and at every join (ffmpeg -ss ... -frames:v 1); Read the
   images. Frame 0 shows content. Caption (if any) matches the screen. Nothing is covered.
4. Claims table (rule 13): every narrated number, name, role and status word against its frame.
5. Density between 55 and 65 percent; fail above 70 percent.
6. Silence and dead air: freezedetect (command in record-demo-video.md rule 1 notes) for stalls.
   [PRECEDENT] Also run silencedetect (noise -50 dB, minimum 4 s) and explain each hit; a planned silent
   bridge card plus clip tails was the only hit in the precedent. Exact command shape not seen: build it
   from the ffmpeg silencedetect filter documentation.
7. Voice clips: each passed the plausibility check in 4.4.
8. I cannot hear or judge pacing. The user must watch the whole file before it is called finished. Say so.
9. Report plainly what was checked, what was not, any beat that was dropped or moved, what text left the
   machine, and anything written outside the agreed folder.

---

## 9. Failure modes to expect

- Blank or magenta first frame (clapper not trimmed): record-demo-video.md rule 1 and its Failure modes table.
- Audio missing after re-time (`-an` used): see 4.2.
- Voice drifting out of sync after speed-up: apply atempo with the same factor.
- Caption inside a trimmed region (toOut returns null): see 7.3 step 8.
- Playwright cannot launch: helpers.js prints the fix; check Zscaler for downloads.
- Session limit on an unlicensed Mendix runtime: always sign out; a killed browser does not release a session.
- edge-tts unreachable: stop and ask; do not silently switch engines (data classification may differ).
- [PRECEDENT] edge-tts returns `NoAudioReceived` or a truncated clip: pace, retry, plausibility check (4.4).
- [PRECEDENT] Fixed on-screen text no longer matches a variant's timing (6.4 item 5).
- [PRECEDENT] A scene's narration states something the build does not support (the precedent's scene 6 said
  everything was created through mxcli; a later slide had to correct it). Run the claims check on the
  narration BEFORE recording, not after.
- [PRECEDENT] Left sidebar clipped at 1280x720 (7.3 step 2).
- Concat with `-c copy` joins clips with mismatched settings badly: encode every clip, including a recorded
  webm, with identical settings first (inferred from the precedent build script).

---

## 10. Definition of done

- Output MP4 exists beside the input (or the agreed folder), named per section 6.2 or 7.3.
- Verification checklist (section 8) run and reported, including what was NOT verified.
- No input overwritten; previous output moved to `_OLD`.
- No secrets in any file produced; no git outside the allowed folders.
- Online TTS use disclosed (rule 14); audio not heard by me, stated (rule 15).
- task_state.json set to clean if this job owned it.
- User told which open items (sections 6.5 and 7.4) were exercised and which remain.

---

## 11. Change log

- 2026-11-09 (rev 1): first version. Planning only; no code written, no video produced.
- 2026-11-09 (rev 2): added the hello_mxclitoolkit_world precedent. Used only to fill gaps: standing rules
  13-15, second ffmpeg path and COM proof (section 2), precedent map (3.3), voice settings and hardening
  (4.3, 4.4), question wording (5), route A procedure and variants (6), pre-flight and pad numbers (7),
  extra checks and failure modes (8, 9). Section 7 flow unchanged. Appendices A and B added. Backup of rev 1
  is Video_Production_A.md.
- 2026-11-14 (rev 3): standing rule 16 (23 fps for all videos); English is default language (4.3); section 2
  rows for F5-TTS (weights and GPU verified present) and Piper/Kokoro (verified not installed); engine table
  extended; new 4.5 "Making the voice sound human" (wording rules, candidate engines F5-TTS/Kokoro/Piper,
  bake-off procedure, F5 reference recording, audio finish). Backups: Video_Production_A.md (rev 2 plus rule
  16 and nothing else) and Video_Production_B.md (rev 2 as of 2026-11-14 before rule 16).
- 2026-11-14 (rev 4): Kokoro installed in py_claude and verified offline; Piper declined by the user; six-clip
  bake-off run and the user chose af_heart (4.5 section G); section 2 and 4.3 and 4.5 rows corrected.
  Backup of rev 3 is Video_Production_B.md (later rotated; see below).
- 2026-11-14 (rev 5): final voices recorded: af_heart (female) and Darth_MikGeorg (male, 70% am_michael +
  30% bm_george, speed 0.88, ffmpeg chain in 4.5 section H.2). Winning wording is the conversational rewrite.
  F5-TTS set aside. Backup of rev 4 is Video_Production_B.md.
- 2026-11-15 (rev 6): new section 0 "Best practice - read this first" and Appendix C (precedent 2: the two MiningOpsApp
  walkthrough films, v1 Darth_MikGeorg with captions 21:29, v2 af_heart caption-free 15:14; procedure, measured settings,
  pitfalls with fixes, what was and was not verified). Reusable code copied to C:/d_drive/workKW/WorkClaude/Video_Production/
  (engine/ generic, example_MiningOpsApp/ app specific, README.md). Findings from this job: caption-free by default,
  speech-window placement, respell for synthesis only, PowerPoint COM slide export, VLC auto-subtitles, XAS logout.
  Nothing above was changed. Backup of rev 5 is Video_Production_C.md.

---

## Appendix A - Precedent project: hello_mxclitoolkit_world (reference, not a procedure)

Read this for background. Nothing here overrides sections 1-11.

### A.1 What it was

A narrated video walkthrough of a small Mendix app (Hello_mxcliToolkit_World, running at
localhost:8080, no login) produced in one autonomous session on 2026-10-27, extended the same day with a
deck video, and on 2026-10-28 with two voice variants. History: transcript a67a6431... (path in 3.3).
The follow-up session 3042b015... (28-29 Oct) reviewed this work; I did not read it beyond the prompts.
Evidence that the outputs exist: ffprobe on 2026-11-09 showed H.264 1280x720 plus AAC 24 kHz audio in both
walkthrough.mp4 (95.3 s) and walkthrough_full.mp4 (535.0 s).

### A.2 Deliverables (all in video01\)

| File | Content |
|---|---|
| walkthrough.mp4 | 95 s, 6 scenes of the live app: Task Overview, New Task dialog (cancelled), UTC Clock, World Clock, iFrames, Summary |
| walkthrough.html | 141 KB self-contained slide-style page (base64 screenshots plus narration), opens by double-click |
| script.md, scenes.json | narration text; the single source of truth |
| walkthrough_full.mp4 | 8 min 55 s: deck slides 1-13, 2.5 s silent title card, the app walkthrough, slides 14-18 |
| walkthrough_full_korean.mp4 | 11 min 49 s, heavier Korean accent (voice ko-KR-InJoonNeural) |
| walkthrough_full_thai.mp4 | 7 min 46 s (465.8 s), Thai narration (th-TH-PremwadeeNeural) |

### A.3 How the user prompted it (patterns worth reusing)

- The named workflow, in the user's words: "Explore - Narrate - Screenshot - Stitch - Generate slide style
  walkthrough".
- The run rules: everything goes in a new subfolder video01/; include all screens; use TTS with an accented
  voice (not too heavy); loop through all phases automatically; make decisions provided they are reversible
  or changeable; never write or delete anything outside video01/; proceed autonomously.
- Follow-ups reused the build: "create a new video ... walk through the pptx ... incorporating the previous
  walkthrough" and "two additional videos ... based exactly on walkthrough_full.mp4 ... just synthesise the
  voices". Both said do not ask questions.
- Note: that autonomy was an explicit user instruction for that job. This document's default is to ask
  (section 5); follow the user's instruction when they give it, and still disclose what left the machine.

### A.4 The process as it ran (reconstructed from the transcript and scripts)

1. Probe tooling read-only: app answers, Playwright Chromium cached, ffmpeg found in the rm_genai env.
2. Workplan in six phases: Explore (read-only via mxcli: modules, entities, pages, navigation), Narrate
   (script per screen, 20-30 s each), Voice-over (check what TTS is approved), Screenshot and record
   (Playwright, read-only run), Stitch (ffmpeg), Slide-style HTML page. The agent put the accent in the voice
   setting, not in the text.
3. Install tooling inside video01 only; probe each screen (probe scripts and probe-*.png in work\).
4. Write scenes.json; generate one MP3 per scene; measure lengths with ffprobe.
5. Record each scene (work\record.js): a new browser context per scene at 1280x720 with video recording on;
   scene length = audio length + 1.2 s; clicks timed inside it; screenshot per scene; Cancel on the dialog.
6. Stitch each scene (webm plus MP3 to MP4, H.264, 25 fps, AAC 128k, shortest), concatenate with `-c copy`
   into walkthrough.mp4. Spot-check frames at 30 s and 60 s.
7. Generate script.md and walkthrough.html from scenes.json.
8. Combined video: render the deck slides to PNG (PowerPoint COM), condense speaker notes to 35-70 words
   per slide, voice them, make one clip per slide (image loop plus audio, 400 ms lead-in, 1.2 s tail), make a
   silent title card, normalise the demo recording to the same encode, concatenate. Checks: video and audio
   tracks equal length, only gap over 4 s is the planned card, frames sampled at joins.
9. Variants: new narration only (translate for Thai), per-variant build script with paced and retried TTS
   and the plausibility guard, per-variant NOTES.md, back-translation reading check.
10. Report: files, what was checked, what was NOT (never listened), text sent to Microsoft, one slip
    (task-state file rewritten outside the allowed folder during the combined build; content unchanged).

### A.5 Key scripts

| Script | Job |
|---|---|
| video01\work\record.js | Node, Playwright: scene loop, per-scene recordVideo, timed actions, screenshots, writes work\recordings.json |
| video01\combined\build_combined.py | Python (base interpreter, -I): edge-tts per slide, per-slide clips, title card, concat, prints per-clip and final durations; run from video01\ |
| video01\variant_ko\build_ko.py, check_voices.py | Korean-accent variant build; voice availability check with fallback to the earlier voice |
| video01\variant_th\build_th.py | Thai build with narration_th.json, scenes_th.json, build_log.txt |
| pptx_deck\render_slides.py | PowerPoint COM export of every slide to PNG (1600x900) |
| video01\work\probe.js, probe2.js | read-only visits to each screen |

### A.6 Issues the precedent recorded

- Left sidebar clipped at 1280x720 (app rendering, not a recording fault).
- iFrames scene showed only the empty state (no external URL loaded, by choice).
- The original scene 6 claimed everything was created through mxcli, which was not fully true; a later slide
  corrected it on screen. The embedded demo still carries the original sentence.
- Thai variant: the demo segment ran about 72 s while the fixed title card and one narration line say
  "95 seconds"; scene s06 cuts into slide 14 with no tail; "PROJECT dot md" and the step name "look" may be
  read oddly or ambiguously in Thai.
- Scene recordings are identical across variants; on-screen UI text stays English.

### A.7 What the precedent did NOT prove

- No audio was listened to by the agent; accent strength and Thai pronunciation were left for the user.
- It used a plain Playwright recorder, not the toolkit's demo-polish or record-demo-video flow. I did not
  check whether that session read the toolkit skills.
- Captions were not burned into the recorded app scenes; narration was voice only.
- The Korean, Thai and combined builds were produced by the same agent session that wrote them; no second
  review exists.

### A.8 A request the precedent declined

The user asked for voices like Terminator and Captain Picard through the VoiceAI tooling. The session declined
twice (real actors' voices, no consent), whichever tool was used, and offered an original robot voice, a
clone of the user's own voice from their recording, or a fictional narrator. This is now standing rule 13.

---

## Appendix B - Reference ffmpeg command shapes from the precedent [PRECEDENT]

Source: video01\combined\build_combined.py and the stitch commands in the session transcript. FF means the
resolved ffmpeg path (section 2). Settings: 1280x720, 25 fps, libx264 yuv420p crf 20 preset medium,
AAC 128k 24000 Hz mono. Adjust only with a reason; every clip that will be joined with `-c copy` must share
the same settings.

```
Duration of a file
  ffprobe -v error -show_entries format=duration -of csv=p=0 FILE

One clip per slide: image plus audio, lead-in 400 ms, tail 1.2 s (T = audio seconds + 1.2)
  FF -y -loop 1 -framerate 25 -i slide.png -i slide.mp3
     -vf "scale=1280:720:flags=lanczos,format=yuv420p"
     -af "adelay=400:all=1,apad" -t T
     -c:v libx264 -pix_fmt yuv420p -r 25 -preset medium -crf 20
     -c:a aac -b:a 128k -ar 24000 -ac 1  clip.mp4

Silent title card, 2.5 s (card.png made with Pillow)
  FF -y -loop 1 -framerate 25 -i card.png -f lavfi -i anullsrc=r=24000:cl=mono -t 2.5
     <same video and audio encode>  card.mp4

Normalise a recorded demo to the same encode before joining
  FF -y -i recording.mp4 -vf "scale=1280:720,format=yuv420p" <same encode>  recording_norm.mp4

Scene recording plus its audio (first video; webm from Playwright)
  FF -y -i rec.webm -i sNN.mp3 -map 0:v -map 1:a -c:v libx264 -pix_fmt yuv420p -r 25
     -c:a aac -b:a 128k -shortest sNN.mp4

Join (list.txt has one line per clip:  file 'name.mp4')
  FF -y -f concat -safe 0 -i list.txt -c copy -movflags +faststart final.mp4

Frame at a time T
  FF -y -ss T -i final.mp4 -frames:v 1 frame.png
```

Run the Python build scripts from the video folder as the precedent did, with the interpreter and -I flag
(isolated mode), for example `C:/miniforge3/python.exe -I combined/build_combined.py`.

---

## Appendix C - Precedent 2: the MiningOpsApp walkthrough films (reference, 2026-11-15)

Read this for the proven procedure and the pitfalls. Section 0 is the short form. Sections 1-11 still govern.
This precedent supersedes Appendix A where they differ (Appendix A was a lighter, plain walkthrough).

### C.1 What was built

- Project: C:\d_drive\workKW\WorkingMendixProjects\MiningOpsApp (a Mendix app on a Graph Studio knowledge graph, synthetic
  data). Deck: C:\d_drive\workKW\WorkClaude\Mining\Illuka\deck\Iluka_Presentation.pptx (48 slides; Part four holds eight
  live questions). Use case II with the deck as the script: each deck question = the real slide, then the live app.
- Version 1 (docs/film/MiningOpsApp_walkthrough.mp4): voice Darth_MikGeorg, burned-in captions with a progress bar,
  21 min 29 s, 70 beats (22 slide + 48 app), 15 raw scene takes, claims 71 of 71. Effort about 35 min preparation and
  2 h 20 min recording, mixing and checking.
- Version 2 (docs/film/MiningOpsApp_walkthrough_af_heart.mp4): voice af_heart, NO captions, no progress bar, pauses cut,
  15 min 14 s, same 70 beats, same text and slides, full re-record, claims 71 of 71. Effort about 1 h 30 min.
- Code: <project>/tests/e2e/film/ (now also templated in C:\d_drive\workKW\WorkClaude\Video_Production\).
  Records: docs/film/ beat-sheet.md, claims-table*.md, verification*.md, voice-check*.md, PROGRESS*.md, *_captions.srt.

### C.2 The procedure that worked

1. Intake in one message (section 0, item 1). Decide the voice gate: customer content = offline.
2. Prepare: slides to PNG by PowerPoint COM; beats.json (id, scene, source slide or app page, text, app action with exact
   selectors from the existing journeys, planned seconds) and docs/film/beat-sheet.md generated by one script
   (gen_beats.py: edit the generator, never the outputs); docs/film/claims-table.md (every spoken fact and its source).
3. Rehearse read-only as each role, at two viewports; report anything clipped; graph-down rehearsed through a proxy.
4. Voice: voice_af_heart.py (recipe H.1) or voice.py (H.2); voice_check offline; respell; voice_trim for the speech window.
5. Record with record_v2.js scene by scene, raw take first, post-process after; one scene can be redone alone.
6. Mix with post_v2.js: clip placed at its beat time from the events, -16 LUFS, H.264 + faststart, 1920x1080, 23 fps, AAC.
7. Verify (verify_frames_v2.py, slide_match_v2.py, verify_audio_v2.py, gaps_v2.py, verify_claims_v2.js) and write
   verification.md; the final report lists scene start times and the author's listening list.

### C.3 Measured settings

| Item | Value |
|---|---|
| Viewport and output | 1600x900, device scale factor 2, rendered to 1920x1080 at 23 fps; raw capture of static pages is about 11 fps and is resampled |
| Voice af_heart | Kokoro, lang_code a, speed 1.0, 24 kHz, no processing; clips about 12 to 16 characters per second |
| Voice Darth_MikGeorg | recipe 4.5 H.2; measured 12.4 characters per second at speed 0.88 |
| Beat hold | speech + 0.4 s lead-in + 0.3 s tail (v1 used a 1.2 s tail); not below the time the action needs |
| Speech window in the mix | 30 ms before, 60 ms after the measured speech |
| Loudness | -16 LUFS integrated, true peak about -1.4 dBFS |
| Density | v1 68.0 percent, v2 74.6 percent of the runtime is voice (guide: aim 55-65, flag above 70) |
| Frame-level check | a frame inside every beat tested, 24 to 30 read by eye per version; slide match correlation minimum 0.9984 |

### C.4 Pitfalls met, with the fix

| Symptom | Cause | Fix |
|---|---|---|
| Slide export had 45 pages for 48 slides | PDF export of the deck | export from PowerPoint by COM (export_pptx_slides.py) |
| Voice said "ILUCA" then "Aluka" for Iluka | default and first respelling | respell for synthesis only: "Ill-oo-kuh" |
| A code read without its letters (SHP-ZR-024) | respelling dropped SHP | spell codes letter by letter in the respelling file |
| Intent captions appeared after the click (v1) | the recorder read the beat kind from the wrong field | fixed in the recorder; check the order in the first read frames |
| Highlight did nothing on a data grid row | a Mendix grid row has no box of its own | highlight the union of the row's children |
| First click of an app beat failed | the slide overlay was not hidden before app beats | hide the overlay explicitly |
| Frame 0 showed a caption mid-fade (v1) | caption animated in | pre-set the caption and wait before the first frame |
| Start click missed after a cold app restart (graph-down scene) | navigator not ready | run a read-only graph check first as warm-up |
| Logins hang, "Maximum number of sessions" | trial licence cap; /logout does not end a Mendix session | XAS logout call at the end of every session; restart the app to clear |
| App stopped mid-job | trial licence time limit | restart only through the project launcher |
| Gaps between lines at least 1.4 s although the tail was set to 0.3 s | af_heart WAVs carry about 0.3 s silence in front and 0.5 s behind | place only the speech window |
| Captions could not be removed from a finished film | burned in by the page | caption-free by default; side .srt; this cost a full re-record |
| The author saw subtitles in the finished film | VLC auto-loaded a side subtitle file with a near-identical name | name the side file clearly different, or keep it in another folder, and say so in the hand-over |
| Capture tool made 60 fps | demo-polish default | pass {fps:23} to render or assemble |

### C.5 What was and was not verified

Verified: durations and streams (ffprobe), caption and bar absence on a frame inside all 70 beats, slides 22 of 22, claims
71 of 71, audio placed and audible 70 of 70, zero password hits across docs, scripts, raw takes and logs, demo data
unchanged, graph restored after the graph-down scene. NOT verified by Claude: how the voice sounds (offline speech
recognition matched 44 of 70 clips exactly, the rest being place-name spellings), clip edges (a clipped first or last
syllable), the pace across the film. The author listened and accepted version 2 ("perfect").

### C.6 Open items and ideas

- Captioned cut from a caption-free film by burning the .srt with ffmpeg: not tried [PROPOSED].
- Long silences in action-bound app steps (up to about 23 s) were accepted; a future job can narrate them or speed them up
  within the 1.6x re-time cap.
- Language and accent variants (section 6.4) are cheap for a caption-free film: only the voice changes, but every beat
  hold changes with the clip length, so the app scenes need a re-record.
- Consider promoting the engine/ scripts into the Mendix toolkit through the author (the clone is read-only for Claude).
