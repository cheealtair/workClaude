'use strict';
// verify_claims_v2.js (version 2: raw_v2, beats_v2.json) - machine half of the claims check (rule 13). For every app beat, the strings its caption asserts must be in the text that was
// visible on screen when the beat ended (record.js snapshots the visible text nodes above the caption strip into events.json, kind 'evidence').
// The frame half is done by reading the extracted frames (docs/film/verification.md). Slide beats are checked against the slide number shown.
// Usage: node tests/e2e/film/verify_claims.js   -> prints a table and writes tests/e2e/artifacts/film/final/claims-check.json
const fs = require('fs');
const path = require('path');
const FILM = path.resolve(__dirname, '..', 'artifacts', 'film');
const BEATS = JSON.parse(fs.readFileSync(path.join(FILM, 'beats_v2.json'), 'utf8')).beats;
const SCENES = ['A', 'B', 'C', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'R1', 'R2', 'R3', 'P'];
const EXPECT = {
  C01: ['Findings', '30 Sep 2026'],
  C02: ['8 detectors', '30 Sep 2026', 'Critical', 'High', 'Medium', 'Low'],
  C03: ['Detector', 'S4', 'S6', 'S8', 'S3', 'S1', 'S5', 'S7', 'S2'],
  Q1A1: ['SHP-ZR-024', 'High'],
  Q1A2: ['7 zircon lots', 'MS-03', 'WO400340', '15 Jun 2026', '1 Jul 2026', 'High'],
  Q1A3: ['15 Jun 2026', '1.004', '30 Jun 2026', '0.717', '1 Jul 2026', '0.989'],
  Q1A4: ['Case SHP-ZR-024'],
  Q1A5: ['Open', 'High', 'hse', '31 Dec 2026', 'Done'],
  Q1A6: ['Back trace for SHP-ZR-024'],
  Q1A7: ['7 lots shipped', '14 ROM lots', '4 ore blocks', 'CAT-N-021', 'CAT-N-022', 'CAT-S-021', 'CAT-S-022', '21 Jun 2026', '27 Jun 2026', 'Cataby'],
  Q1A8: ['SHP-ZR-024'],
  Q1A9: ['24 records and 22 links'],
  Q1A10: ['Graph of 24 records and 22 links'],
  Q1A11: ['Selected: SHP-ZR-024', 'Which other shipments share its lots?'],
  Q1A12: ['27 records and 25 links'],
  Q2A1: ['Capel Kiln Line SR2 10 Jul 2026', 'Medium'],
  Q2A2: ['89.574', '89.29', '89.455', '1213.1', '1214.2', '1206.4', 'CAT-S-024'],
  Q2A3: ['89.43966667', '90.49775', 'Excursion > 1180 degC', 'Capel Kiln Line SR1', 'Capel Kiln Line SR2'],
  Q2A4: ['Selected: lot_SR_SR2_20260710'],
  Q2A5: ['89.44', '90.50', '3 days', '4 days', '1180 degC'],
  Q3A1: ['CAT-N-018', 'Low', 'Cataby'],
  Q3A2: ['9.6', '7.627', '-20.5', '8 Jun 2026', '11 Jun 2026'],
  Q4A1: ['BAL-RUM-03', 'Medium', 'Balranald'],
  Q4A2: ['Deviation event and corrective action', 'Steering correction applied from MD 510', '570'],
  Q4A3: ['BAL-RUM-03', '3.2', '480', '0.2'],
  Q4A4: ['Run date', 'Dilution pct'],
  Q5A1: ['TP_002', 'Low', 'Eneabba', 'Simulated'],
  Q5A2: ['Simulated', '5.85', '3.94'],
  Q6A1: ['MONAZITE_NAR_20260819', 'Critical', 'No case'],
  Q6A2: ['7.4', '312', 'Narngulu', 'Eneabba', 'Grace Dawson'],
  Q6A3: ['Compliance', 'Radiation'],
  Q6A4: ['RM00138', '7.40', '5.00', 'Over limit'],
  Q7A1: ['INC00027', 'High', 'Capel'],
  Q7A2: ['Amelia Sinclair', '31 May 2026', 'Kiln Operation', '60'],
  Q7A3: ['INC00027'],
  Q7A4: ['11 records and 11 links'],
  Q7A5: ['6 people hold an expired certificate', 'Amelia Sinclair'],
  Q8A1: ['OBL-007', 'High', 'Cataby'],
  Q8A2: ['45', '28', '17', 'Amelia Prescott'],
  Q8A3: ['Obligations'],
  Q8A4: ['19 obligations', '12 completed', '7 open', '1 overdue', 'OBL-007', 'Overdue'],
  Q8A5: ['Open cases at Cataby', 'OBL-007'],
  R02: ['Contract ZR_CASTELLON'],
  R03: ['Case SHP-ZR-024'],
  'R03:popup': ['Add task', 'What needs doing', 'Save task', 'Cancel'],
  R04: ['Contract ZR_CASTELLON'],
  R05: ['Selected: Contract ZR_CASTELLON'],
  R06: ['SHP-ZR-024'],
  R07: ['Could not load the details', 'cannot be reached'],
};
const ABSENT = { R05: ['Add a task about this'] };
const rows = []; let bad = 0, app = 0;
for (const sc of SCENES) {
  const evs = JSON.parse(fs.readFileSync(path.join(FILM, 'raw_v2', sc, 'events.json'), 'utf8')).filter(e => e.kind === 'evidence');
  for (const e of evs) {
    const b = BEATS.find(x => x.id === e.beat.split(':')[0]);
    if (b.kind === 'slide') {
      const ok = e.slide === b.source.slide;
      rows.push({ beat: e.beat, kind: 'slide', ok, note: `slide ${e.slide} shown, planned slide ${b.source.slide}` });
      if (!ok) bad++;
      continue;
    }
    app++;
    const want = EXPECT[e.beat] || [], not = ABSENT[e.beat] || [];
    const miss = want.filter(w => !e.text.includes(w)), present = not.filter(w => e.text.includes(w));
    const ok = miss.length === 0 && present.length === 0;
    rows.push({ beat: e.beat, kind: b.kind, ok, checked: want.length + not.length, missing: miss, wrongly_present: present });
    if (!ok) bad++;
  }
}
fs.mkdirSync(path.join(FILM, 'final_v2'), { recursive: true });
fs.writeFileSync(path.join(FILM, 'final_v2', 'claims-check.json'), JSON.stringify({ rows, bad, app_beats: app }, null, 1));
for (const r of rows) if (!r.ok) console.log('FAIL', r.beat, JSON.stringify(r));
console.log(`beats checked ${rows.length} (app ${app}), failures ${bad}`);
const noExpect = BEATS.filter(b => b.kind !== 'slide' && !EXPECT[b.id]).map(b => b.id);
if (noExpect.length) console.log('app beats without an expectation list: ' + noExpect.join(','));
