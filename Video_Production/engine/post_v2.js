'use strict';
// post_v2.js - film VERSION 2 (copy of post.js; v1 untouched): raw_v2 -> render_v2 -> final_v2, voice_af_heart clips, no caption strip, no progress bar.
// post.js - post-process the raw scene takes of the film (record and post are separate steps).
//   node tests/e2e/film/post.js render [A,B,...|all]   camera render of each raw scene to artifacts/film/render/<scene>.mp4 (23 fps, 1920x1080)
//   node tests/e2e/film/post.js mix                    join the scenes, place each voice clip at its caption time, loudness -16 LUFS, mux, SRT
// Env: FFMPEG / FFPROBE (full paths). Output: docs/film/MiningOpsApp_walkthrough_af_heart.mp4 and docs/film/MiningOpsApp_walkthrough_af_heart_captions.srt
// Mixing rule: each caption event time t is mapped to output time with demo-polish mapper().toOut(t) plus the scene's offset in the joined
// film; the voice clip starts 400 ms after the caption appears. A caption inside a cut maps to null: it is reported and the run stops.
const fs = require('fs');
const path = require('path');
const { execFileSync, spawnSync } = require('child_process');
const polish = require('../demo-polish.js');

const ROOT = path.resolve(__dirname, '..', '..', '..');
const FILM = path.join(ROOT, 'tests', 'e2e', 'artifacts', 'film');
const RAW = path.join(FILM, 'raw_v2'), REN = path.join(FILM, 'render_v2'), FIN = path.join(FILM, 'final_v2'), DOCS = path.join(ROOT, 'docs', 'film');
const FF = process.env.FFMPEG || 'C:/miniforge3/envs/rm_genai/Library/bin/ffmpeg.exe';
const FP = process.env.FFPROBE || 'C:/miniforge3/envs/rm_genai/Library/bin/ffprobe.exe';
const ORDER = ['A', 'B', 'C', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'R1', 'R2', 'R3', 'P'];
const FPS = 23, WIDTH = 1920, STRIP_H = 0, LEAD = 400;
const BEATS = Object.fromEntries(JSON.parse(fs.readFileSync(path.join(FILM, 'beats_v2.json'), 'utf8')).beats.map(b => [b.id, b]));
const dur = f => parseFloat(execFileSync(FP, ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString().trim());
fs.mkdirSync(REN, { recursive: true }); fs.mkdirSync(FIN, { recursive: true });

async function render(list) {
  for (const id of list) {
    const dir = path.join(RAW, id), out = path.join(REN, id + '.mp4');
    if (!fs.existsSync(path.join(dir, 'frames.json'))) { console.log(`scene ${id}: no raw take, skipped`); continue; }
    const fresh = fs.existsSync(out) && fs.statSync(out).mtimeMs > fs.statSync(path.join(dir, 'frames.json')).mtimeMs && process.env.REUSE === '1';
    let r = { shots: '-', skipped: [], renderSec: 0 };
    if (!fresh) r = await polish.render(dir, out, { fps: FPS, width: WIDTH, keepBottom: STRIP_H });
    console.log(`scene ${id}: ${dur(out).toFixed(2)}s, shots ${r.shots}, skipped ${JSON.stringify(r.skipped)}, render ${r.renderSec.toFixed(0)}s`);
  }
}

function mix() {
  const segs = ORDER.filter(id => fs.existsSync(path.join(REN, id + '.mp4')) && fs.existsSync(path.join(RAW, id, 'frames.json')));
  const missing = ORDER.filter(id => !segs.includes(id));
  if (missing.length) { console.error('missing rendered scenes: ' + missing.join(',')); process.exit(1); }
  const timeline = [], sceneRows = [], nulls = [];
  let offset = 0;
  for (const id of segs) {
    const dir = path.join(RAW, id), mp4 = path.join(REN, id + '.mp4');
    const meta = JSON.parse(fs.readFileSync(path.join(dir, 'frames.json'), 'utf8')).meta, events = JSON.parse(fs.readFileSync(path.join(dir, 'events.json'), 'utf8'));
    const mp = (function () { const cuts = [...meta.cuts].sort((a, b) => a[0] - b[0]); return t => { let o = t - meta.t0; for (const [a, b] of cuts) { if (t >= b) o -= b - a; else if (t > a) return null; } return o; }; })();
    const d = dur(mp4);
    sceneRows.push({ scene: id, start_s: +offset.toFixed(2), length_s: +d.toFixed(2) });
    for (const e of events.filter(x => x.kind === 'say')) {
      const o = mp(e.t);
      if (o == null) { nulls.push(`${e.id} in scene ${id}`); continue; }
      timeline.push({ scene: id, id: e.id, text: e.text, caption_at_s: +(offset + o / 1000).toFixed(3), voice_at_s: +(offset + o / 1000 + LEAD / 1000).toFixed(3), audio_ms: e.audio_ms, hold_ms: e.hold_ms, step: e.step });
    }
    offset += d;
  }
  // the voice of one beat must end before the voice of the next begins (the clips are never allowed to overlap)
  const overl = [];
  timeline.forEach((t, i) => { const n = timeline[i + 1]; if (n && t.voice_at_s + t.audio_ms / 1000 > n.voice_at_s - 0.05) overl.push(`${t.id} ends ${(t.voice_at_s + t.audio_ms / 1000).toFixed(2)} next ${n.id} starts ${n.voice_at_s}`); });
  if (overl.length) { console.error('VOICE OVERLAP: ' + overl.join('; ')); process.exit(1); }
  if (nulls.length) { console.error('CAPTION INSIDE A CUT (not placed): ' + nulls.join('; ')); process.exit(1); }
  const list = path.join(FIN, 'concat.txt');
  fs.writeFileSync(list, segs.map(id => `file '${path.join(REN, id + '.mp4').replace(/\\/g, '/')}'`).join('\n') + '\n');
  const video = path.join(FIN, 'video_silent.mp4');
  execFileSync(FF, ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', '-movflags', '+faststart', video]);
  const vdur = dur(video);
  console.log(`joined video ${vdur.toFixed(2)}s from ${segs.length} scenes`);
  // voice: one adelay per clip, then amix without normalisation
  const inputs = [], filt = [];
  timeline.forEach((t, i) => {
    inputs.push('-i', path.join(FILM, 'voice_af_heart', t.id + '.wav'));
    const ms = Math.round(t.voice_at_s * 1000);
    const bt = BEATS[t.id];   // the WAV is untouched; only its speech window is placed (silence before and after the speech is left out)
    filt.push(`[${i}:a]atrim=start=${(bt.trim_start_ms / 1000).toFixed(3)}:end=${(bt.trim_end_ms / 1000).toFixed(3)},asetpts=PTS-STARTPTS,aresample=48000,adelay=${ms}|${ms}[a${i}]`);
  });
  filt.push(timeline.map((_, i) => `[a${i}]`).join('') + `amix=inputs=${timeline.length}:normalize=0:dropout_transition=0,apad[mix]`);
  const fscript = path.join(FIN, 'mix_filter.txt');
  fs.writeFileSync(fscript, filt.join(';\n'));
  const raw = path.join(FIN, 'voice_raw.wav');
  let r = spawnSync(FF, ['-y', '-loglevel', 'error', ...inputs, '-/filter_complex', fscript, '-map', '[mix]', '-t', vdur.toFixed(3), '-ac', '1', raw], { encoding: 'utf8', maxBuffer: 1 << 26 });
  if (r.status !== 0) { console.error(r.stderr); process.exit(1); }
  // loudness: two-pass loudnorm to -16 LUFS, true peak -1.5
  const m = spawnSync(FF, ['-hide_banner', '-i', raw, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], { encoding: 'utf8', maxBuffer: 1 << 26 }).stderr;
  const js = JSON.parse(m.slice(m.lastIndexOf('{'), m.lastIndexOf('}') + 1));
  const norm = path.join(FIN, 'voice_norm.wav');
  r = spawnSync(FF, ['-y', '-loglevel', 'error', '-i', raw, '-af', `loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=${js.input_i}:measured_TP=${js.input_tp}:measured_LRA=${js.input_lra}:measured_thresh=${js.input_thresh}:offset=${js.target_offset}:linear=true`, '-ar', '48000', '-ac', '1', norm], { encoding: 'utf8', maxBuffer: 1 << 26 });
  if (r.status !== 0) { console.error(r.stderr); process.exit(1); }
  const out = path.join(DOCS, 'MiningOpsApp_walkthrough_af_heart.mp4');
  execFileSync(FF, ['-y', '-loglevel', 'error', '-i', video, '-i', norm, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-r', String(FPS), '-t', vdur.toFixed(3), '-movflags', '+faststart', out]);
  // SRT: each caption shown from its start until the next caption starts (never longer than its hold)
  const ts = s => { const ms = Math.round(s * 1000), h = Math.floor(ms / 3600000), mi = Math.floor(ms % 3600000 / 60000), se = Math.floor(ms % 60000 / 1000), x = ms % 1000; return `${String(h).padStart(2, '0')}:${String(mi).padStart(2, '0')}:${String(se).padStart(2, '0')},${String(x).padStart(3, '0')}`; };
  let srt = '';
  timeline.forEach((t, i) => {
    const end = Math.min(t.caption_at_s + t.hold_ms / 1000, i + 1 < timeline.length ? timeline[i + 1].caption_at_s : vdur);
    srt += `${i + 1}\n${ts(t.caption_at_s)} --> ${ts(end)}\n${t.text}\n\n`;
  });
  fs.writeFileSync(path.join(DOCS, 'MiningOpsApp_walkthrough_af_heart_captions.srt'), srt, 'ascii');
  const voiceSec = timeline.reduce((a, t) => a + t.audio_ms, 0) / 1000;
  const summary = { out, duration_s: +dur(out).toFixed(2), video_s: +vdur.toFixed(2), beats: timeline.length, voice_s: +voiceSec.toFixed(1), density_pct: +(100 * voiceSec / vdur).toFixed(1), loudnorm_measured: js, scenes: sceneRows };
  fs.writeFileSync(path.join(FIN, 'timeline.json'), JSON.stringify({ summary, timeline }, null, 1));
  console.log(JSON.stringify({ ...summary, scenes: undefined }));
}

(async () => {
  const [cmd, arg] = process.argv.slice(2);
  if (cmd === 'render') await render(!arg || arg === 'all' ? ORDER : arg.split(','));
  else if (cmd === 'mix') mix();
  else { console.error('usage: post.js render [scenes|all] | mix'); process.exit(2); }
})().catch(e => { console.error(e); process.exit(1); });
