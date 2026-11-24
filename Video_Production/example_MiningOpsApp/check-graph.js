'use strict';
// check-graph.js - read-only: proves the app talks to the real graph (Explore on SHP-ZR-024 must show 24 records and 22 links). Logs out with the XAS call.
const L = require('./lib.js');
(async () => {
  const s = await L.openSession('manager', { width: 1600, height: 900 });
  const p = s.page;
  try {
    await L.nap(2000);
    await p.goto(L.BASE + '/p/findings');
    await p.waitForSelector('.mx-name-dgFindings [role="gridcell"]', { timeout: 30000 });
    await p.locator('.mx-name-dgFindings [role="gridcell"]:has-text("SHP-ZR-024")').first().click();
    await p.waitForSelector('.mx-name-btnNavStart', { timeout: 40000 });
    await L.nap(1500);
    await p.locator('.mx-name-btnNavStart').first().click();
    await p.waitForSelector('.mx-name-btnNavRestart', { timeout: 60000 });
    await L.nap(2500);
    console.log('counts: ' + (await p.locator('.mx-name-txtNavCounts').first().innerText()).replace(/\s+/g, ' ').trim());
  } finally { console.log('xas logout: ' + await L.closeSession(s)); }
})().catch(e => { console.error('FAILED', e.message.split('\n')[0]); process.exit(1); });
