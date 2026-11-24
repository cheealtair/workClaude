'use strict';
// explore2.js - read-only: open each finding's Finding_Detail, dump visible text + buttons + clipping, shoot top and bottom.
// Usage: node explore2.js <w> <h> <user> [codes comma separated]
const L = require('./lib.js');
const path = require('path');
const OUT = path.resolve(__dirname, '..', 'artifacts', 'film', 'rehearsal');
const CODES = { S3: 'SHP-ZR-024', S1: 'Capel Kiln Line SR2 10 Jul 2026', S2: 'CAT-N-018', S5: 'BAL-RUM-03', S7: 'TP_002', S4: 'MONAZITE_NAR_20260819', S6: 'INC00027', S8: 'OBL-007' };
(async () => {
  const [w, h, user = 'manager', only] = process.argv.slice(2);
  const want = only ? only.split(',') : Object.keys(CODES);
  const s = await L.openSession(user, { width: +w, height: +h });
  const p = s.page;
  try {
    for (const k of want) {
      await p.goto(L.BASE + '/p/findings');
      await p.waitForSelector('.mx-name-dgFindings [role="gridcell"]', { timeout: 30000 });
      await L.nap(1200);
      await p.locator(`.mx-name-dgFindings [role="gridcell"]:has-text("${CODES[k]}")`).first().click();
      await p.waitForSelector('.mx-name-btnBack', { timeout: 30000 });
      await L.nap(5000);
      await p.screenshot({ path: path.join(OUT, `fd-${k}-${w}-top.png`) });
      const txt = (await p.locator('.mx-page').first().innerText()).replace(/\s+/g, ' ').slice(+(process.env.TXT_FROM||0), +(process.env.TXT_TO||1400));
      const btns = await p.locator('[class*="mx-name-btn"]:visible').evaluateAll(e => e.map(x => (x.className.match(/mx-name-(btn\w+)/) || [])[1] + ':' + x.innerText.trim().slice(0, 30)));
      console.log(`\n=== ${k} ${CODES[k]}\ntext: ${txt}\nbuttons: ${JSON.stringify(btns)}`);
      console.log('clipped: ' + JSON.stringify((await L.clippedLabels(p)).slice(0, 8)));
      await p.evaluate(() => { const sc = document.querySelector('.mx-scrollcontainer-center') || document.scrollingElement; sc.scrollTop = 99999; window.scrollTo(0, 99999); });
      await L.nap(800);
      await p.screenshot({ path: path.join(OUT, `fd-${k}-${w}-bottom.png`) });
    }
  } finally {
    console.log('errors: ' + s.errs.length);
    console.log('xas logout: ' + await L.closeSession(s));
  }
})().catch(e => { console.error('FAILED', e.message.split('\n')[0]); process.exit(1); });
