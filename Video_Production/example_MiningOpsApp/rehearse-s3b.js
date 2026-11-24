'use strict';
// rehearse-s3b.js - read-only: S3 question on SHP-ZR-024, then page 2 of the navigator list (the three other shipments). Usage: node rehearse-s3b.js <w> <h>
const L = require('./lib.js');
const path = require('path');
const OUT = path.resolve(__dirname, '..', 'artifacts', 'film', 'rehearsal');
(async () => {
  const [w, h] = process.argv.slice(2);
  const s = await L.openSession('manager', { width: +w, height: +h });
  const p = s.page;
  try {
    await p.goto(L.BASE + '/p/findings');
    await p.waitForSelector('.mx-name-dgFindings [role="gridcell"]', { timeout: 30000 });
    await L.nap(1000);
    await p.locator('.mx-name-dgFindings [role="gridcell"]:has-text("SHP-ZR-024")').first().click();
    await p.waitForSelector('.mx-name-btnNavStart', { timeout: 40000 });
    await L.nap(2000);
    await p.locator('.mx-name-btnNavStart').first().click();
    await p.waitForSelector('.mx-name-btnNavRestart', { timeout: 60000 });
    await L.nap(4000);
    const r = p.locator('.mx-name-dgNavNodes [role="row"]').filter({ hasText: 'SHP-ZR-024' }).first();
    await r.locator('.mx-name-btnNavSelect').first().click();
    await p.waitForSelector('.mx-name-btnNavPresetS3', { timeout: 30000 });
    await L.nap(2500);
    await p.locator('.mx-name-btnNavPresetS3').first().click();
    await L.nap(12000);
    await p.locator('[class*="mx-name-ngNav"]:visible').first().evaluate(e => e.scrollIntoView({ block: 'center' }));
    await L.nap(800);
    await p.screenshot({ path: path.join(OUT, `s3b-graph-${w}.png`) });
    console.log('counts: ' + (await p.locator('.mx-name-txtNavCounts').first().innerText()).trim());
    console.log('shipments in list page 1: ' + JSON.stringify(await p.locator('.mx-name-dgNavNodes [role="row"]').evaluateAll(e => e.map(x => x.innerText.replace(/\s+/g, ' ').trim()).filter(t => /Shipment/.test(t)).map(t => t.slice(0, 60)))));
    await p.locator('.mx-name-dgNavNodes [aria-label="Go to next page"]').first().click();
    await L.nap(2500);
    console.log('page 2 shipments: ' + JSON.stringify(await p.locator('.mx-name-dgNavNodes [role="row"]').evaluateAll(e => e.map(x => x.innerText.replace(/\s+/g, ' ').trim()).filter(t => /Shipment/.test(t)).map(t => t.slice(0, 80)))));
    await p.locator('.mx-name-dgNavNodes').first().evaluate(e => e.scrollIntoView({ block: 'start' }));
    await L.nap(500);
    await p.screenshot({ path: path.join(OUT, `s3b-page2-${w}.png`) });
  } finally {
    console.log('xas logout: ' + await L.closeSession(s));
  }
})().catch(e => { console.error('FAILED', e.message.split('\n')[0]); process.exit(1); });
