'use strict';
// record_v2.js - film VERSION 2: no caption strip, no progress bar, shorter holds (clip + 0.4 s lead + 0.3 s tail). Copy of record.js; v1 is untouched.
// The helper still records the {kind:'say'} events (they place the audio and write the .srt) but paints nothing.
// Raw takes go to tests/e2e/artifacts/film/raw_v2/<scene>/. Beats come from beats_v2.json.
// Toolkit flow: skills/record-demo-video.md (rules 1-13) + skills/demo-recording-polish.md; capture via tests/e2e/demo-polish.js.
// Raw takes: tests/e2e/artifacts/film/raw/<scene>/ (frames/, frames.json, events.json, scene.json). Post-processing is separate (post.js).
//
// Usage (the password is read from the environment only; it is never printed, logged or written):
//   TEST_PASS="$(awk '/^demo.user_password=/{sub(/^[^=]*=/,"");gsub(/\r/,"");print}' config/app.config)" \
//   node tests/e2e/film/record_v2.js <scene[,scene...]>
// Scenes in film order: A B C Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8 R1 R2 R3 P
//   R3 (graph down) needs the app started with GRAPH_BASE_URL=http://127.0.0.1:18080 and analysis/tools/stage6/tmp/n99/graph-proxy.js running.
// Slides are shown as an overlay inside the same page (real slide PNGs served through a route, never from the app).
// Sign-in is off camera (capture starts on the signed-in page). Every session ends with the XAS logout (never /logout).
// Dialogs: Cancel, never Save. A take with skipped steps exits non-zero (the raw frames are still written).
const fs = require('fs');
const path = require('path');
const http = require('http');
const { chromium } = require(path.resolve(__dirname, '..', '..', '..', 'node_modules', 'playwright'));
const polish = require('../demo-polish.js');
const L = require('./lib.js');

const ROOT = path.resolve(__dirname, '..', '..', '..');
const FILM = path.join(ROOT, 'tests', 'e2e', 'artifacts', 'film');
const RAW = path.join(FILM, 'raw_v2');
const BEATS = JSON.parse(fs.readFileSync(path.join(FILM, 'beats_v2.json'), 'utf8')).beats;
const BY = Object.fromEntries(BEATS.map(b => [b.id, b]));
const PW = process.env.TEST_PASS;
const BASE = L.BASE;
const VP = { width: 1600, height: 900 };
const STRIP_H = 0, LEAD = 400, TAIL = 300;   // no caption strip: the page uses the whole 1600x900 viewport
const REST = { x: VP.width - 24, y: 24 };
const nap = ms => new Promise(r => setTimeout(r, ms));
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const rnd = (a, b) => a + Math.random() * (b - a);
const log = (...a) => console.log(...a);

const SCENES = {
  A: { slides: true, ids: ['A01', 'A03', 'A04', 'A05'] },
  B: { slides: true, ids: ['B01', 'B03', 'B05'] },
  C: { user: 'manager', ids: ['C01', 'C02', 'C03'] },
  R1: { user: 'manager', ids: ['R01', 'R02', 'R03'] },
  R2: { user: 'viewer', ids: ['R04', 'R05'] },
  R3: { user: 'manager', down: true, ids: ['R06', 'R07'] },
  P: { slides: true, ids: ['P01', 'P02', 'P03', 'P05', 'P06'] },
};
for (const q of ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8']) SCENES[q] = { user: 'manager', ids: BEATS.filter(b => b.scene === q).map(b => b.id) };
const ORDER = ['A', 'B', 'C', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'R1', 'R2', 'R3', 'P'];

// ---------------------------------------------------------------- in-page caption strip + slide overlay
const STRIP = `(()=>{
 const build=()=>{ if(document.getElementById('__spot'))return; if(!document.body)return;
  const css=document.createElement('style'); css.id='__cap-css';
  css.textContent='#__slide{position:fixed;left:0;top:0;right:0;bottom:0;z-index:2147483000;background:#0b1224;display:none;align-items:center;justify-content:center}'
  +'#__slide.on{display:flex}#__slide img{max-width:100%;max-height:100%;object-fit:contain}'
  +'html.slide-on #__dp-cursor{display:none !important}'
  +'#__spot{position:fixed;z-index:2147483644;pointer-events:none;border:3px solid #f59e0b;border-radius:10px;box-shadow:0 0 0 5px rgba(245,158,11,.28);opacity:0;transition:opacity .25s}#__spot.on{opacity:1}';
  document.head.appendChild(css);
  const s=document.createElement('div'); s.id='__spot'; document.body.appendChild(s);
  const sl=document.createElement('div'); sl.id='__slide'; sl.innerHTML='<img alt="slide">'; document.body.appendChild(sl); };
 const set=()=>0;   // v2: the caption is never painted
 const spot=(x,y,w,h)=>{ build(); const s=document.getElementById('__spot'); s.style.cssText+=';left:'+x+'px;top:'+y+'px;width:'+w+'px;height:'+h+'px'; s.classList.add('on'); };
 const unspot=()=>{ const s=document.getElementById('__spot'); if(s)s.classList.remove('on'); };
 const slide=async(url)=>{ build(); const sl=document.getElementById('__slide'); if(!url){ sl.classList.remove('on'); document.documentElement.classList.remove('slide-on'); return true; }
  const i=new Image(); i.src=url; await i.decode(); sl.querySelector('img').src=url; sl.classList.add('on'); document.documentElement.classList.add('slide-on'); return true; };
 window.__cap={set,spot,unspot,build,slide};
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',build);else build();})()`;

// ---------------------------------------------------------------- state and helpers
const S = { step: 0, skips: 0, rec: null, sayEnd: 0, page: null, sceneLog: [], presetNext: false };
function skip(what) { S.skips += 1; log(`    (skipped -- ${what})`); S.sceneLog.push('SKIP ' + what); }
const vloc = (page, sel) => page.locator(sel + ' >> visible=true').first();
async function vis(page, sel, what, ms = 25000) {
  const ok = await vloc(page, sel).waitFor({ state: 'visible', timeout: ms }).then(() => true, () => false);
  if (!ok) skip(`${what || sel} did not appear within ${ms}ms`);
  return ok;
}
// A Mendix grid row is display:contents (no box of its own): its box is then the union of what is inside it
const boxOf = async loc => {
  const b = await loc.boundingBox().catch(() => null);
  if (b && b.width > 2 && b.height > 2) return { x: b.x, y: b.y, width: b.width, height: b.height };
  return loc.evaluate(el => {
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    el.querySelectorAll('*').forEach(c => { const r = c.getBoundingClientRect(); if (r.width > 2 && r.height > 2) { x0 = Math.min(x0, r.left); y0 = Math.min(y0, r.top); x1 = Math.max(x1, r.right); y1 = Math.max(y1, r.bottom); } });
    return x1 > x0 ? { x: x0, y: y0, width: x1 - x0, height: y1 - y0 } : null;
  }).catch(() => null);
};
const ensureStrip = page => page.evaluate(STRIP);
const roleOf = (b, sc) => (b.kind === 'slide' ? 'Deck' : (sc.user === 'viewer' ? 'Viewer' : 'Manager'));
const isIntent = b => b.intent_or_landing === 'intent';
const holdFor = b => b.audio_ms + LEAD + TAIL;   // v2: clip + 0.4 s lead-in + 0.3 s tail, no dwell

async function say(page, b, role) {
  const hold = holdFor(b);
  await ensureStrip(page);
  S.step += 1;
  const t = Date.now();
  let fsz = null;
  fsz = await page.evaluate(([text, n, h, r]) => window.__cap.set(text, n, h, r), [b.text, S.step, hold, role]);
  S.rec.events.push({ t, kind: 'say', beat: b.id, id: b.id, text: b.text, audio_ms: b.audio_ms, hold_ms: hold, step: S.step, font_px: fsz });
  polish.holdUntil(page, t + hold);
  S.sayEnd = t + hold;
  log(`  [${String(S.step).padStart(2, '0')}] ${b.id} (${(hold / 1000).toFixed(1)}s) ${b.text.slice(0, 80)}`);
  return { t, hold, end: t + hold, voiceStart: t + LEAD, voiceEnd: t + LEAD + b.audio_ms, wait: () => nap(Math.max(0, t + hold - Date.now())) };
}
const sleepUntil = t => nap(Math.max(0, t - Date.now()));

async function spotBox(page, loc, pad = 6, maxH = 0) {
  const b = await boxOf(loc); if (!b) return;
  if (maxH && b.height > maxH) b.height = maxH;
  const x = Math.max(2, b.x - pad), y = Math.max(2, b.y - pad);
  const r = Math.min(VP.width - 2, b.x + b.width + pad), btm = Math.min(VP.height - STRIP_H - 4, b.y + b.height + pad);
  await ensureStrip(page);
  await page.evaluate(([x, y, w, h]) => window.__cap.spot(x, y, w, h), [x, y, r - x, btm - y]);
}
const unspot = page => page.evaluate(() => window.__cap && window.__cap.unspot()).catch(() => {});

// human click: scroll only if the target is outside the safe area, glide, pause, ripple, real click, park afterwards
async function hclick(page, loc, o = {}) {
  if (page.__park) await page.__park.catch(() => {});
  await loc.waitFor({ state: 'visible', timeout: o.timeout || 25000 });
  let b = await boxOf(loc);
  if (b && (b.y < 70 || b.y + b.height > VP.height - STRIP_H - 16)) { await polish.scrollTo(page, loc, { block: o.block || 'center' }); b = await boxOf(loc); }
  if (!b) throw new Error('click target has no box');
  const x = b.x + b.width * clamp(o.fx ?? .5, .1, .9), y = b.y + b.height * clamp(o.fy ?? .5, .2, .8);
  const t0 = Date.now();
  await polish.moveTo(page, x, y);
  await nap(rnd(150, 250));
  const tClick = Date.now();
  await page.evaluate(([x, y]) => window.__dp.ripple(x, y), [x, y]);
  await page.mouse.click(x, y);
  if (S.rec) S.rec.events.push({ t: tClick, kind: 'click', bbox: b, x, y, t0 });
  if (o.park !== false) page.__park = (async () => { await nap(450); await polish.moveTo(page, REST.x, REST.y, { ms: 800 }); })().catch(() => {});
}
async function parkRest(page) { if (page.__park) await page.__park.catch(() => {}); await polish.moveTo(page, REST.x, REST.y, { ms: 800 }); }

// A wait in which nothing changes on screen is squeezed out of the film (rec.cut), keeping 2.5 s of it, but never inside a caption hold
function squeeze(a, b, keepHead = 2500, keepTail = 1000) {
  if (!S.rec || b - a < 5000) return;
  const from = Math.max(a + keepHead, S.sayEnd), to = b - keepTail;
  if (to - from > 800) { S.rec.cut(from, to); log(`    (squeezed a ${((to - from) / 1000).toFixed(1)}s wait out of the film)`); S.sceneLog.push(`CUT ${((to - from) / 1000).toFixed(1)}s`); }
}
const httpGet = u => new Promise(res => http.get(u, r => { let d = ''; r.on('data', c => d += c); r.on('end', () => res(d.trim())); }).on('error', e => res('ERR ' + e.message)));
const ctl = what => httpGet('http://127.0.0.1:18081/' + what);

// dropdown: mark the OPTION being chosen, hold, click, release (rule 10)
async function pickCombo(page, widget, want) {
  const box = vloc(page, `.mx-name-${widget}`);
  await box.waitFor({ state: 'visible', timeout: 15000 });
  await hclick(page, box.locator('[id^="downshift-"][id$="-toggle-button"]').first(), { park: false });
  const opts = page.locator('[role="option"]');
  await opts.first().waitFor({ state: 'visible', timeout: 8000 }).catch(() => {});
  await nap(500);
  const texts = await opts.evaluateAll(e => e.map(x => x.textContent.trim())).catch(() => []);
  const opt = opts.filter({ hasText: new RegExp('^\\s*' + want + '\\s*$') }).first();
  const useOpt = (await opt.count()) ? opt : page.locator('[role="option"]', { hasText: want }).first();
  if (!(await useOpt.isVisible().catch(() => false))) { skip(`${widget}: option "${want}" missing; options ${JSON.stringify(texts)}`); return false; }
  await spotBox(page, useOpt, 3);
  const bb = await useOpt.boundingBox();
  await polish.moveTo(page, bb.x + bb.width * 0.5, bb.y + bb.height * 0.5);
  await nap(650);
  await hclick(page, useOpt, { park: false });
  await nap(450);
  await unspot(page);
  const val = await box.locator('input[role="combobox"]').inputValue().catch(() => '');
  if (!val.includes(want)) { skip(`${widget}: value is "${val}", wanted "${want}"`); return false; }
  return true;
}
async function fillDate(page, widget, value) {
  const inp = vloc(page, `.mx-name-${widget} input`);
  await hclick(page, inp, { park: false });
  await nap(200);
  await page.keyboard.press('Control+A');
  await page.keyboard.type(value, { delay: 70 });
  await page.keyboard.press('Tab');
  await nap(500);
}

// ---------------------------------------------------------------- the step interpreter (steps come from beats.json)
async function runStep(page, st, b) {
  switch (st.do) {
    case 'click': {
      const loc = vloc(page, st.sel);
      if (st.block && !(await boxOf(loc))) { /* waits inside hclick */ }
      if (st.block) await polish.scrollTo(page, loc, { block: st.block }).catch(() => {});
      const before = st.sel.includes('btnNavPreset') ? (await page.locator('.mx-name-txtNavCounts').first().innerText().catch(() => '')) : null;
      await hclick(page, loc, { timeout: st.timeout_ms || 25000 });
      const tA = Date.now();
      if (st.ready) await vis(page, st.ready, `ready ${st.ready} after click`, st.timeout_ms || 45000);
      if (before !== null) {   // detector preset: the graph query runs; wait for the counts line to change
        const ok = await page.waitForFunction(b0 => { const e = document.querySelector('.mx-name-txtNavCounts'); return e && e.innerText.trim() !== b0.trim(); }, before, { timeout: 70000 }).then(() => true, () => false);
        if (!ok) skip('preset query: counts line did not change');
        squeeze(tA, Date.now());
        await nap(1500);
      } else {
        squeeze(tA, Date.now());
        const w = st.wait_ms || 0;
        await nap(st.ready ? Math.min(Math.max(w, 800), 4000) : 800);
      }
      break;
    }
    case 'wait_for': await vis(page, st.sel, st.sel, 40000); await nap(700); break;
    case 'scroll': {
      const loc = vloc(page, st.sel);
      if (!(await loc.waitFor({ state: 'visible', timeout: 30000 }).then(() => true, () => false))) { skip('scroll target not visible: ' + st.sel); break; }
      await polish.scrollTo(page, loc, { block: st.block || 'center' });
      await nap(700); break;
    }
    case 'spot': {
      const loc = vloc(page, st.sel);
      if (!(await loc.waitFor({ state: 'visible', timeout: 30000 }).then(() => true, () => false))) { skip('spot target not visible: ' + st.sel); break; }
      const b0 = await boxOf(loc);
      if (b0 && (b0.y < 60 || b0.y + Math.min(b0.height, 200) > VP.height - STRIP_H - 10)) { await polish.scrollTo(page, loc, { block: 'center' }); await nap(500); }
      await spotBox(page, loc, 6, /columnheader/.test(st.sel) ? 46 : 0); await nap(400); break;
    }
    case 'zoom': { const loc = vloc(page, st.sel); await polish.focus(page, loc); await nap(300); break; }
    case 'park': await parkRest(page); break;
    case 'session': break;   // the sign-in is the scene's own, off camera
    case 'proxy': { const r = await ctl(st.state); log('    proxy -> ' + st.state + ': ' + r); break; }
    default: skip('unknown step ' + st.do);
  }
}
async function runSteps(page, steps, b) {
  for (const st of steps) {
    try { await runStep(page, st, b); } catch (e) { skip(`${b.id} step ${st.do} ${st.sel || ''}: ${e.message.split('\n')[0].slice(0, 140)}`); }
  }
}

// wait until the first target of the beat is on screen with real content, before the caption goes up (caption after the screen paints)
async function prePaint(page, steps) {
  const st = steps.find(s => s.sel && ['spot', 'scroll', 'zoom'].includes(s.do));
  if (!st) { await nap(600); return; }
  const grid = (st.sel.match(/^\.mx-name-dg\w+/) || [])[0];
  if (grid) await vloc(page, grid + ' [role="gridcell"]').waitFor({ state: 'visible', timeout: 40000 }).catch(() => skip('grid content not visible: ' + grid));
  else await vloc(page, st.sel).waitFor({ state: 'attached', timeout: 30000 }).catch(() => skip('target not present: ' + st.sel));
  await nap(900);
}

// ---------------------------------------------------------------- beats with their own timing
const sentenceStarts = (text, from, len) => {   // wall-clock start of each sentence, proportional to characters
  const parts = text.split(/(?<=[.?!])\s+/); let c = 0; const out = [];
  for (const p of parts) { out.push(from + len * c / text.length); c += p.length + 1; }
  return out;
};
const CUSTOM = {
  // The popup beat: show the button, open the popup while the voice describes it, Cancel at the end. Never Save.
  async R03(page, b, sc) {
    const cap = await say(page, b, roleOf(b, sc));
    const ss = sentenceStarts(b.text, cap.voiceStart, b.audio_ms);
    const btn = vloc(page, '.mx-name-btnNavAddTask');
    await btn.waitFor({ state: 'visible', timeout: 20000 }).catch(() => skip('Add a task button not visible'));
    await nap(500);
    await polish.scrollTo(page, vloc(page, '.mx-name-dvNavSel'), { block: 'start' }).catch(() => skip('could not scroll the selection panel into view'));
    await nap(400); await spotBox(page, btn, 6);
    await sleepUntil(ss[1] - 600);
    await unspot(page);
    await hclick(page, btn, { park: false });
    if (!(await vis(page, '.mx-name-taDesc', 'task popup description', 20000))) return cap.wait();
    await nap(900);
    await spotBox(page, vloc(page, '.mx-name-taDesc'), 6);
    await snapEvidence(page, b, 'popup');
    const prefill = await page.locator('.mx-name-taDesc textarea').first().inputValue().catch(() => '');
    log('    popup prefill: ' + prefill.slice(0, 100));
    await sleepUntil(Math.max(cap.voiceEnd - 2600, Date.now() + 2500));
    await unspot(page);
    await hclick(page, vloc(page, '.mx-name-btnTaskCancel'), { park: false });
    await page.locator('.mx-name-taDesc').first().waitFor({ state: 'hidden', timeout: 8000 }).catch(() => skip('popup did not close after Cancel'));
    await parkRest(page);
    await cap.wait();
  },
  // The graph tour: zoom on the graph, cursor over the left hub while sentence 1 is spoken, over the right hub for sentence 2
  async Q1A10(page, b, sc) {
    await prePaint(page, b.action.steps);
    const g = vloc(page, '[class*="mx-name-ngNav"]');
    const gb0 = await boxOf(g);
    if (gb0 && (gb0.y < 60 || gb0.y + gb0.height > VP.height - STRIP_H - 10)) { await polish.scrollTo(page, g, { block: 'center' }); await nap(500); }
    const cap = await say(page, b, roleOf(b, sc));
    await polish.focus(page, g); await nap(1200);
    const gb = await boxOf(g);
    const ss = sentenceStarts(b.text, cap.voiceStart, b.audio_ms);
    const hubL = { x: gb.x + gb.width * .413, y: gb.y + gb.height * .445 }, hubR = { x: gb.x + gb.width * .672, y: gb.y + gb.height * .278 };
    await sleepUntil(ss[0]);
    await polish.moveTo(page, hubL.x, hubL.y, { ms: 1400 });
    await sleepUntil(ss[1]);
    await polish.moveTo(page, hubR.x, hubR.y, { ms: 1500 });
    await sleepUntil(cap.voiceEnd - 800);
    await parkRest(page);
    await cap.wait();
  },
  // The radiation filter: sentence one is already on the tab's lead line; the filter is applied while the rest is spoken
  async Q6A4(page, b, sc) {
    await prePaint(page, [{ do: 'spot', sel: '.mx-name-txtRadiationLead' }]);
    const cap = await say(page, b, roleOf(b, sc));
    const ss = sentenceStarts(b.text, cap.voiceStart, b.audio_ms);
    await runSteps(page, [{ do: 'spot', sel: '.mx-name-txtRadiationLead' }], b);
    await sleepUntil(ss[0] + b.audio_ms * 0.18);
    await unspot(page);
    try {
      await pickCombo(page, 'cmbSite', 'Narngulu');
      await nap(1200);
      await fillDate(page, 'dpFrom', '19 Aug 2026');
      await fillDate(page, 'dpTo', '19 Aug 2026');
      await hclick(page, vloc(page, '.mx-name-txtDateHint'), { park: false });
    } catch (e) { skip('Q6A4 filter: ' + e.message.split('\n')[0]); }
    await nap(3000);
    await runSteps(page, [{ do: 'spot', sel: '.mx-name-dgRadiation' }], b);
    const rows = await page.locator('.mx-name-dgRadiation [role="row"]').allInnerTexts().catch(() => []);
    log('    radiation rows after filter: ' + rows.map(r => r.replace(/\s+/g, ' ').slice(0, 60)).join(' || '));
    await parkRest(page);
    await cap.wait();
  },
  // Graph down: Details is chosen while the graph is unreachable; the error shows in the status banner
  async R07(page, b, sc) {
    const sel = '.mx-name-dgNavNodes [role="row"]:has-text("Contract ZR_CASTELLON") .mx-name-btnNavSelect';
    await hclick(page, vloc(page, sel), { timeout: 30000 });
    const ok = await page.waitForFunction(() => { const e = document.querySelector('.mx-name-txtNavStatus'); return e && /not|cannot|could/i.test(e.innerText); }, null, { timeout: 40000 }).then(() => true, () => false);
    if (!ok) skip('graph-down message did not appear in the status banner');
    await nap(900);
    await runSteps(page, [{ do: 'scroll', sel: '.mx-name-ctnNavStatus', block: 'center' }, { do: 'spot', sel: '.mx-name-ctnNavStatus' }], b);
    log('    status text: ' + (await page.locator('.mx-name-txtNavStatus').first().innerText().catch(() => '')).replace(/\s+/g, ' ').slice(0, 200));
    const cap = await say(page, b, roleOf(b, sc));
    await parkRest(page);
    await cap.wait();
    log('    proxy -> up: ' + await ctl('up'));
  },
};

// The step lists in beats.json are the plan; these overrides keep every number a caption states in the same frame as the caption.
function stepsFor(b) {
  const st = (b.action && b.action.steps) || [];
  if (b.id === 'Q1A3') return [{ do: 'scroll', sel: '.mx-name-dgS3Ctx', block: 'start' }];             // 15 Jun to 1 Jul all in view
  if (b.id === 'Q1A9') return [{ do: 'scroll', sel: '.mx-name-txtNavCounts', block: 'start' }];        // counts line, link types and graph in one view
  return st.map(s => (s.do === 'scroll' && /ngNav/.test(s.sel)) ? { ...s, sel: '.mx-name-txtNavCounts', block: 'start' } : s);
}
async function appBeat(page, b, sc) {
  await ensureStrip(page);
  await page.evaluate(() => window.__cap.slide(null));   // a slide from the previous beat comes down: the app behind it is unchanged
  if (CUSTOM[b.id]) return CUSTOM[b.id](page, b, sc);
  const steps = stepsFor(b);
  const role = roleOf(b, sc);
  if (isIntent(b)) {                    // caption first (before the click); the actions run while the line is spoken
    const cap = await say(page, b, role);
    await nap(1000);
    await runSteps(page, steps, b);
    const endAct = Date.now();
    await parkRest(page).catch(() => {});
    await sleepUntil(Math.max(cap.end, endAct + 800));
    return;
  }
  const needsAction = steps.some(s => ['click', 'wait_for'].includes(s.do));
  if (needsAction) {                    // action first: the caption goes up only after the new screen has painted
    await runSteps(page, steps, b);
    await parkRest(page).catch(() => {});
    await nap(600);
    const cap = await say(page, b, role);
    await cap.wait();
  } else {                              // caption first, then scroll / spot / zoom while the line is spoken
    await prePaint(page, steps);
    const cap = await say(page, b, role);
    await nap(900);
    await runSteps(page, steps, b);
    await cap.wait();
  }
  await unspot(page);
}

async function showSlide(page, n) { await ensureStrip(page); await page.evaluate(u => window.__cap.slide(u), `/__slide/slide-${String(n).padStart(2, '0')}.png`); }
async function slideBeat(page, b, sc) {
  await showSlide(page, b.source.slide);
  await unspot(page);
  const cap = await say(page, b, roleOf(b, sc));
  await cap.wait();
}

// What is actually visible on screen when a beat ends (text nodes inside the viewport above the caption strip): evidence for the claims check
async function snapEvidence(page, b, tag) {
  try {
    const txt = await page.evaluate(limit => {
      const out = [], w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      for (let n = w.nextNode(); n; n = w.nextNode()) {
        const t = n.nodeValue.replace(/\s+/g, ' ').trim(); if (!t) continue;
        const el = n.parentElement; if (!el || el.closest('#__cap,#__slide,#__spot,script,style')) continue;
        const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none') continue;
        const r = document.createRange(); r.selectNodeContents(n); const b = r.getBoundingClientRect();
        if (b.width < 1 || b.height < 1 || b.bottom <= 0 || b.top >= limit || b.right <= 0 || b.left >= innerWidth) continue;
        out.push(t);
      }
      return out.join(' | ').slice(0, 9000);
    }, VP.height - STRIP_H);
    S.rec.events.push({ t: Date.now(), kind: 'evidence', beat: b.id + (tag ? ':' + tag : ''), text: txt });
  } catch (e) { skip('evidence snapshot for ' + b.id + ': ' + e.message.split('\n')[0]); }
}

// ---------------------------------------------------------------- scene driver
let warmed = false;
async function warmUp() {
  if (warmed) return; warmed = true;
  const br = await chromium.launch(); const cx = await br.newContext({ viewport: VP });
  const pg = await cx.newPage();
  await pg.goto(BASE + '/login.html', { timeout: 60000 }).catch(() => {});
  await pg.waitForSelector('#passwordInput', { state: 'visible', timeout: 60000 }).catch(() => {});
  await cx.close(); await br.close();
  log('warm-up on a throwaway context done');
}

async function runScene(name) {
  const sc = SCENES[name];
  if (!sc) throw new Error('unknown scene ' + name);
  const dir = path.join(RAW, name);
  fs.mkdirSync(RAW, { recursive: true });
  S.skips = 0; S.step = 0; S.sceneLog = []; S.sayEnd = 0;
  log(`\n== scene ${name}: ${sc.ids.join(' ')}${sc.user ? ' (' + sc.user + ')' : ' (slides only, no sign-in)'}`);
  if (sc.down) { const st = await ctl('status'); log('graph proxy status: ' + st); if (st !== 'up') { console.error('graph proxy not up: ' + st); process.exit(2); } }
  if (sc.user) await warmUp();
  const browser = await chromium.launch({ args: polish.launchArgs(2) });
  const ctx = await browser.newContext({ viewport: VP, deviceScaleFactor: 2 });
  await polish.prepare(ctx);
  await ctx.addInitScript(STRIP);
  await ctx.route(/\/__slide\/slide-\d+\.png$/, r => r.fulfill({ path: path.join(FILM, 'slides', path.basename(new URL(r.request().url()).pathname)) }));
  await ctx.route(/\/__blank$/, r => r.fulfill({ status: 200, contentType: 'text/html', body: '<!doctype html><html><body style="margin:0;background:#0b1224"></body></html>' }));
  const page = await ctx.newPage();
  S.page = page;
  page.__dp = { x: REST.x, y: REST.y, rec: null };
  const errs = [];
  page.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  let rec = null, meta = null;
  const t0wall = Date.now();
  try {
    if (sc.user) {                                   // off-camera sign-in; capture starts on the signed-in page
      await page.goto(BASE + '/login.html', { timeout: 60000 });
      await page.fill('#usernameInput', sc.user);
      await page.fill('#passwordInput', PW);
      await page.click('#loginButton');
      await page.waitForSelector('.mx-page', { timeout: 60000 });
      log(`  signed in as ${sc.user}`);
      await nap(3500);
    } else {
      await page.goto(BASE + '/__blank', { timeout: 30000 });
    }
    // frame 0 carries the slide when the first beat is a slide
    const first = BY[sc.ids[0]];
    await ensureStrip(page);
    if (first.kind === 'slide') await showSlide(page, first.source.slide);
    await polish.bottomPad(page, STRIP_H);
    await nap(500);
    rec = await polish.startCapture(page, { dir, quality: 82 });
    S.rec = rec;
    for (let i = 0; i < sc.ids.length; i++) {
      const b = BY[sc.ids[i]];
      try {
        if (b.kind === 'slide') { await slideBeat(page, b, sc); S.rec.events.push({ t: Date.now(), kind: 'evidence', beat: b.id, slide: b.source.slide }); }
        else { await appBeat(page, b, sc); await snapEvidence(page, b); }
      } catch (e) { skip(`beat ${b.id} aborted: ${e.message.split('\n')[0].slice(0, 160)}`); }
    }
    await nap(400);
  } catch (e) {
    skip(`scene ${name} aborted: ${e.message.split('\n')[0]}`);
  } finally {
    if (rec) {
      meta = await rec.stop().catch(e => { log('stop failed ' + e.message); return null; });
      S.rec = null;
      const says = rec.events.filter(e => e.kind === 'say').map(e => ({ id: e.id, t: e.t, audio_ms: e.audio_ms, hold_ms: e.hold_ms, step: e.step }));
      fs.writeFileSync(path.join(dir, 'scene.json'), JSON.stringify({ scene: name, ids: sc.ids, user: sc.user || null, says, skips: S.skips, log: S.sceneLog, pageerrors: errs, wall_s: +((Date.now() - t0wall) / 1000).toFixed(1), meta }, null, 1));
      log(`  capture: ${meta && meta.frames} frames, frameSize ${meta && JSON.stringify(meta.frameSize)}, ${(meta && meta.captureFps || 0).toFixed(1)} fps source, cuts ${meta && meta.cuts.length}`);
    }
    for (const e of errs) log(`  pageerror: ${e}`);
    if (sc.user) log(`  xas logout: ${await L.logout(page)}`);
    await nap(500);
    await ctx.close().catch(() => {});
    await browser.close().catch(() => {});
  }
  log(`  scene ${name} done: skips ${S.skips}`);
  return S.skips;
}

(async () => {
  const arg = process.argv[2];
  if (!arg) { console.error('usage: record.js <scene[,scene...]>   scenes: ' + ORDER.join(' ')); process.exit(2); }
  if (!PW) { console.error('TEST_PASS not set'); process.exit(2); }
  if (!BASE || /undefined/.test(BASE)) { console.error('base url unset'); process.exit(2); }
  const want = arg === 'all' ? ORDER : arg.split(',');
  let skips = 0;
  for (const n of want) skips += await runScene(n);
  log(`\nDONE: scenes ${want.join(',')}; total skips ${skips}`);
  process.exit(skips ? 1 : 0);
})().catch(e => { console.error('FAILED', e); process.exit(1); });
