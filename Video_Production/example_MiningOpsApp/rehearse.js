'use strict';
// rehearse.js - READ-ONLY rehearsal of every planned app step of the walkthrough film.
// Usage: TEST_PASS=... node rehearse.js <w> <h> <manager|viewer> [outTag]
// No saves: dialogs end with Cancel/dismiss. Ends every session with the XAS logout. Writes shots to artifacts/film/rehearsal/<tag>/.
const L = require('./lib.js');
const fs = require('fs');
const path = require('path');
const [W, H, ROLE = 'manager', TAG = 'r1'] = process.argv.slice(2);
const OUT = path.resolve(__dirname, '..', 'artifacts', 'film', 'rehearsal', `${TAG}-${W}-${ROLE}`);
fs.mkdirSync(OUT, { recursive: true });
const res = [];
let n = 0;
async function step(p, name, expects, fn) {
  n += 1;
  const id = String(n).padStart(2, '0');
  let ok = true, why = '';
  try {
    await fn();
    await L.nap(900);
    const txt = (await p.locator('.mx-page').first().innerText().catch(() => '')).replace(/\s+/g, ' ');
    const miss = (expects || []).filter(e => !txt.includes(e));
    if (miss.length) { ok = false; why = 'missing: ' + JSON.stringify(miss); }
  } catch (e) { ok = false; why = 'error: ' + e.message.split('\n')[0].slice(0, 160); }
  const shot = `${id}-${name.replace(/[^A-Za-z0-9]+/g, '-').slice(0, 40)}.png`;
  await p.screenshot({ path: path.join(OUT, shot) }).catch(() => {});
  const clip = await L.clippedLabels(p).catch(() => []);
  console.log(`${ok ? 'PASS' : 'FAIL'} ${id} ${name} ${why}\n     shot ${shot}${clip.length ? '\n     clipped: ' + JSON.stringify(clip.slice(0, 6)) : ''}`);
  res.push({ id, name, ok, why, shot });
}
const openFinding = async (p, key) => {
  await p.locator('a[title="Findings"]:visible').first().click();
  await p.waitForSelector('.mx-name-dgFindings [role="gridcell"]', { timeout: 30000 });
  await L.nap(1000);
  await p.locator(`.mx-name-dgFindings [role="gridcell"]:has-text("${key}")`).first().click();
  await p.waitForSelector('.mx-name-btnBack', { timeout: 30000 });
  await L.nap(2500);
};
const txtOf = async (p, sel) => (await p.locator(sel).first().innerText().catch(() => '')).replace(/\s+/g, ' ').trim();
const scrollTo = (p, sel, block = 'center') => p.locator(sel).first().evaluate((e, b) => e.scrollIntoView({ block: b }), block);
const explore = async (p) => {
  await p.locator('.mx-name-btnNavStart').first().click();
  await p.waitForSelector('.mx-name-btnNavRestart', { timeout: 60000 });
  await L.nap(5000);
};
const details = async (p, rowText) => {
  const r = p.locator('.mx-name-dgNavNodes [role="row"]').filter({ hasText: rowText }).first();
  await r.locator('.mx-name-btnNavSelect').first().click();
  await p.waitForSelector('.mx-name-txtNavSelTitle', { timeout: 30000 });
  await L.nap(3500);
};

(async () => {
  const user = ROLE === 'viewer' ? 'viewer' : 'manager';
  const s = await L.openSession(user, { width: +W, height: +H });
  const p = s.page;
  try {
    await L.nap(2500);
    if (ROLE === 'manager') {
      await step(p, 'landing', ['Cases'], async () => { console.log('     url ' + p.url()); });
      await step(p, 'findings-list', ['MONAZITE_NAR_20260819', 'INC00027', 'OBL-007', 'SHP-ZR-024', 'Capel Kiln Line SR2 10 Jul 2026', 'BAL-RUM-03', 'TP_002', 'CAT-N-018', 'No case'], async () => {
        await p.locator('a[title="Findings"]:visible').first().click();
        await p.waitForSelector('.mx-name-dgFindings [role="gridcell"]', { timeout: 30000 }); await L.nap(1500);
      });
      // Q1 / S3
      await step(p, 'S3-finding', ['WO400340', '15 Jun 2026', '1 Jul 2026', 'MS-03', 'Evidence', 'Trace this shipment', 'Go to case'], async () => { await openFinding(p, 'SHP-ZR-024'); });
      await step(p, 'S3-finding-scroll-case-card', ['Case state', 'Explore connections'], async () => { await scrollTo(p, '.mx-name-btnNavStart'); });
      await step(p, 'S3-case-view', ['SHP-ZR-024', 'Open', 'Tasks', 'Comments', 'Audit trail'], async () => {
        await p.evaluate(() => window.scrollTo(0, 0)); await p.locator('.mx-name-btnGoToCase').first().click();
        await p.waitForSelector('.mx-name-txtTitle', { timeout: 30000 }); await L.nap(2500);
        console.log('     case title: ' + await txtOf(p, '.mx-name-txtTitle') + ' | badge: ' + await txtOf(p, '.mx-name-txtStatusBadge'));
      });
      await step(p, 'S3-trace', ['Back trace for SHP-ZR-024', 'CAT-N-021', 'CAT-N-022', 'CAT-S-021', 'CAT-S-022', '4 ore blocks, 14 ROM lots'], async () => {
        await openFinding(p, 'SHP-ZR-024');
        await p.locator('.mx-name-btnTraceShipment').first().click();
        await p.waitForSelector('.mx-name-dgBack [role="gridcell"]', { timeout: 90000 }); await L.nap(3500);
      });
      await step(p, 'S3-explore', ['24 records and 22 links shown', 'wo_00340', 'eq_nar_ms03', 'Contract ZR_CASTELLON'], async () => {
        await openFinding(p, 'SHP-ZR-024'); await explore(p); await scrollTo(p, '[class*="mx-name-ngNav"]:not([style*="display: none"])');
      });
      await step(p, 'S3-details-workorder', ['Selected: wo_00340'], async () => { await details(p, 'wo_00340'); await scrollTo(p, '.mx-name-txtNavSelTitle', 'start'); });
      await step(p, 'S3-details-equipment', ['Selected: eq_nar_ms03'], async () => { await details(p, 'eq_nar_ms03'); await scrollTo(p, '.mx-name-txtNavSelTitle', 'start'); });
      // add task popup on the contract (manager), cancel
      await step(p, 'S3-case-explore-contract-add-task', ['Add a task about this', 'Selected: Contract ZR_CASTELLON'], async () => {
        await openFinding(p, 'SHP-ZR-024'); await p.locator('.mx-name-btnGoToCase').first().click();
        await p.waitForSelector('.mx-name-txtTitle', { timeout: 30000 }); await L.nap(2000);
        await explore(p); await details(p, 'Contract ZR_CASTELLON'); await scrollTo(p, '.mx-name-txtNavSelTitle', 'start');
      });
      await step(p, 'S3-add-task-popup-cancel', ['Look into'], async () => {
        await p.locator('.mx-name-btnNavAddTask').first().click();
        await p.waitForSelector('.mx-name-taDesc', { timeout: 15000 }); await L.nap(1200);
        console.log('     prefill: ' + await p.locator('.mx-name-taDesc textarea').first().inputValue().catch(() => '?'));
        console.log('     cancel button present: ' + (await p.locator('.mx-name-btnTaskCancel:visible').count()));
        await p.screenshot({ path: path.join(OUT, 'popup-open.png') });
        await p.locator('.mx-name-btnTaskCancel:visible').first().click(); await L.nap(900);
      });
      // Q2 / S1
      await step(p, 'S1-finding', ['89.574', '1213.1', 'CAT-S-024', 'Excursion > 1180 degC'], async () => { await openFinding(p, 'Capel Kiln Line SR2 10 Jul 2026'); });
      await step(p, 'S1-explore-preset', ['Question S1', '89.44', '90.50'], async () => {
        await explore(p); await details(p, 'lot_SR_SR2_20260710');
        await p.locator('.mx-name-btnNavPresetS1').first().click(); await L.nap(14000);
        await scrollTo(p, '.mx-name-txtNavStatus', 'start');
        console.log('     status: ' + await txtOf(p, '.mx-name-txtNavStatus'));
        console.log('     counts: ' + await txtOf(p, '.mx-name-txtNavCounts'));
      });
      await step(p, 'S1-graph', [], async () => { await scrollTo(p, '[class*="mx-name-ngNav"]:not([style*="display: none"])'); });
      // Q3 / S2
      await step(p, 'S2-finding', ['9.6', '7.627', '-20.55', 'CAT-N-018'], async () => { await openFinding(p, 'CAT-N-018'); });
      // Q4 / S5
      await step(p, 'S5-finding', ['DEV-BAL-RUM-03-01', 'Steering correction applied from MD 510', '3.2', '1.5'], async () => { await openFinding(p, 'BAL-RUM-03'); });
      await step(p, 'S5-finding-runs', ['Runs above the dilution threshold'], async () => { await scrollTo(p, 'text=Runs above the dilution threshold', 'start').catch(async () => { await p.evaluate(() => window.scrollTo(0, 99999)); }); });
      // Q5 / S7
      await step(p, 'S7-finding', ['Simulated', '5.85', '3.94', 'Refinery records are simulated'], async () => { await openFinding(p, 'TP_002'); });
      // Q6 / S4
      await step(p, 'S4-finding', ['7.4', '312', 'Grace Dawson', 'No case', 'Narngulu', 'Eneabba'], async () => { await openFinding(p, 'MONAZITE_NAR_20260819'); });
      await step(p, 'S4-compliance-radiation', ['183 radiation readings, 1 over their limit', 'Over limit'], async () => {
        await p.locator('a[title="Compliance"]:visible').first().click();
        await p.waitForSelector('.mx-name-dgLapses [role="gridcell"]', { timeout: 40000 }); await L.nap(1500);
        await p.locator('.mx-name-tcCompliance [role="tab"]:has-text("Radiation")').first().click();
        await p.waitForSelector('.mx-name-txtRadiationLead', { timeout: 20000 }); await L.nap(2500);
      });
      await step(p, 'S4-compliance-radiation-filter', ['RM00138', '7.40', '5.00', 'Over limit'], async () => {
        const box = p.locator('.mx-name-cmbSite:visible').first();
        await box.locator('[id^="downshift-"][id$="-toggle-button"]').first().click(); await L.nap(600);
        await p.locator('[role="option"]').filter({ hasText: /^\s*Narngulu\s*$/ }).first().click(); await L.nap(1500);
        await p.locator('.mx-name-dpFrom input:visible').first().fill('19 Aug 2026'); await p.keyboard.press('Tab');
        await p.locator('.mx-name-dpTo input:visible').first().fill('19 Aug 2026'); await p.keyboard.press('Tab'); await L.nap(500);
        await p.locator('.mx-name-txtDateHint:visible').first().click().catch(() => {}); await L.nap(3000);
      });
      // Q7 / S6
      await step(p, 'S6-finding', ['Amelia Sinclair', '31 May 2026', 'Kiln Operation', '60'], async () => { await openFinding(p, 'INC00027'); });
      await step(p, 'S6-explore-preset', ['Question S6'], async () => {
        await explore(p); await details(p, 'INC00027');
        await p.locator('.mx-name-btnNavPresetS6').first().click(); await L.nap(12000);
        await scrollTo(p, '[class*="mx-name-ngNav"]:not([style*="display: none"])');
        console.log('     status: ' + await txtOf(p, '.mx-name-txtNavStatus'));
        console.log('     counts: ' + await txtOf(p, '.mx-name-txtNavCounts'));
        const rows = await p.locator('.mx-name-dgNavNodes [role="row"]').evaluateAll(e => e.map(x => x.innerText.replace(/\s+/g, ' ').trim().slice(0, 90)));
        console.log('     rows: ' + JSON.stringify(rows));
      });
      await step(p, 'S6-compliance-lapsed', ['6 people hold an expired certificate', 'Amelia Sinclair'], async () => {
        await p.locator('a[title="Compliance"]:visible').first().click();
        await p.waitForSelector('.mx-name-dgLapses [role="gridcell"]', { timeout: 40000 }); await L.nap(2000);
      });
      // Q8 / S8
      await step(p, 'S8-finding', ['45', '28', '17', 'Amelia Prescott', '30 Jun 2026', 'RA-CAT-07'], async () => { await openFinding(p, 'OBL-007'); });
      await step(p, 'S8-compliance-obligations', ['19 obligations, any due date: 12 completed, 7 open of which 1 overdue at 30 Sep 2026', 'OBL-007', 'Overdue'], async () => {
        await p.locator('a[title="Compliance"]:visible').first().click();
        await p.waitForSelector('.mx-name-dgLapses [role="gridcell"]', { timeout: 40000 }); await L.nap(1200);
        await p.locator('.mx-name-tcCompliance [role="tab"]:has-text("Obligations")').first().click();
        await p.waitForSelector('.mx-name-txtObligationsLead', { timeout: 20000 }); await L.nap(2500);
      });
      await step(p, 'sites-cataby', ['Open cases at Cataby', 'OBL-007'], async () => {
        await p.locator('a[title="Sites"]:visible').first().click();
        await p.waitForSelector('.mx-name-galSites .mx-name-ctnSiteCard', { timeout: 30000 }); await L.nap(1500);
        await p.locator('.mx-name-galSites .mx-name-ctnSiteCard:has-text("Cataby")').first().click();
        await p.waitForSelector('.mx-name-dgUnits [role="gridcell"]', { timeout: 40000 }); await L.nap(2500);
      });
    } else {
      await step(p, 'viewer-landing', ['Home'], async () => { console.log('     url ' + p.url()); });
      await step(p, 'viewer-S3-case-view', ['Case SHP-ZR-024'], async () => {
        await openFinding(p, 'SHP-ZR-024');
        await p.locator('.mx-name-btnGoToCase').first().click();
        await p.waitForSelector('.mx-name-txtTitle', { timeout: 30000 }); await L.nap(2500);
        const btns = await p.locator('[class*="mx-name-btn"]:visible').evaluateAll(e => e.map(x => (x.className.match(/mx-name-(btn\w+)/) || [])[1]));
        console.log('     case-page buttons for viewer: ' + JSON.stringify(btns));
      });
      await step(p, 'viewer-explore-contract', ['Selected: Contract ZR_CASTELLON'], async () => {
        await explore(p); await details(p, 'Contract ZR_CASTELLON'); await scrollTo(p, '.mx-name-txtNavSelTitle', 'start');
        console.log('     Add a task button count: ' + (await p.locator('.mx-name-btnNavAddTask').count()));
        console.log('     panel: ' + (await txtOf(p, '.mx-name-dvNavSel')).slice(0, 300));
      });
    }
  } finally {
    fs.writeFileSync(path.join(OUT, 'results.json'), JSON.stringify(res, null, 1));
    const bad = res.filter(r => !r.ok).length;
    console.log(`\nSUMMARY ${ROLE} ${W}x${H}: ${res.length - bad} pass, ${bad} fail; console errors ${s.errs.length}: ${JSON.stringify([...new Set(s.errs.map(e => e.slice(0, 70)))])}`);
    console.log('xas logout: ' + await L.closeSession(s));
  }
})().catch(e => { console.error('FAILED', e.message.split('\n')[0]); process.exit(1); });
