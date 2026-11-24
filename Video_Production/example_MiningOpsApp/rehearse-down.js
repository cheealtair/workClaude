'use strict';
// rehearse-down.js - READ-ONLY rehearsal of the graph-down beat. Needs the app started with
// GRAPH_BASE_URL=http://127.0.0.1:18080 and analysis/tools/stage6/tmp/n99/graph-proxy.js running (control port 18081).
// Usage: TEST_PASS=... node rehearse-down.js <w> <h>
const L = require('./lib.js');
const http = require('http');
const path = require('path');
const fs = require('fs');
const OUT = path.resolve(__dirname, '..', 'artifacts', 'film', 'rehearsal', 'down');
fs.mkdirSync(OUT, { recursive: true });
const ctl = (what) => new Promise((res) => http.get('http://127.0.0.1:18081/' + what, r => { let b = ''; r.on('data', d => b += d); r.on('end', () => res(b.trim())); }).on('error', e => res('ERR ' + e.message)));
(async () => {
  const [w, h] = process.argv.slice(2);
  console.log('proxy status: ' + await ctl('status'));
  const s = await L.openSession('manager', { width: +w, height: +h });
  const p = s.page;
  try {
    await L.nap(2000);
    await p.goto(L.BASE + '/p/findings');
    await p.waitForSelector('.mx-name-dgFindings [role="gridcell"]', { timeout: 30000 });
    await L.nap(1000);
    await p.locator('.mx-name-dgFindings [role="gridcell"]:has-text("SHP-ZR-024")').first().click();
    await p.waitForSelector('.mx-name-btnNavStart', { timeout: 40000 });
    await L.nap(2000);
    await p.locator('.mx-name-btnNavStart').first().click();
    await p.waitForSelector('.mx-name-btnNavRestart', { timeout: 60000 });
    await L.nap(5000);
    console.log('explored: ' + (await p.locator('.mx-name-txtNavCounts').first().innerText()).trim());
    console.log('proxy -> ' + await ctl('down'));
    const r = p.locator('.mx-name-dgNavNodes [role="row"]').filter({ hasText: 'Contract ZR_CASTELLON' }).first();
    await r.locator('.mx-name-btnNavSelect').first().click();
    await L.nap(9000);
    const st = (await p.locator('.mx-name-txtNavStatus').first().innerText().catch(() => '')).trim();
    console.log('status after Details with graph down: ' + st);
    console.log('counts: ' + (await p.locator('.mx-name-txtNavCounts').first().innerText().catch(() => '')).trim());
    await p.locator('.mx-name-ctnNavStatus').first().evaluate(e => e.scrollIntoView({ block: 'center' })).catch(() => {});
    await L.nap(700);
    await p.screenshot({ path: path.join(OUT, `down-details-${w}.png`) });
    console.log('error style: ' + (await p.locator('.mx-name-ctnNavStatus').first().getAttribute('class').catch(() => '')));
  } finally {
    console.log('proxy -> ' + await ctl('up'));
    console.log('errors: ' + s.errs.length);
    console.log('xas logout: ' + await L.closeSession(s));
  }
})().catch(e => { console.error('FAILED', e.message.split('\n')[0]); process.exit(1); });
