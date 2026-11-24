'use strict';
// probe-scroll.js - read-only: where does the OBL-007 row sit and which ancestors scroll? Logs out with the XAS call.
const L = require('./lib.js');
(async () => {
  const s = await L.openSession('manager', { width: 1600, height: 900 });
  const p = s.page;
  try {
    await L.nap(2000);
    await p.locator('a[title="Compliance"]:visible').first().click();
    await p.waitForSelector('.mx-name-dgLapses [role="gridcell"]', { timeout: 40000 }); await L.nap(1200);
    await p.locator('.mx-name-tcCompliance [role="tab"]:has-text("Obligations")').first().click();
    await p.waitForSelector('.mx-name-txtObligationsLead', { timeout: 20000 }); await L.nap(2000);
    const info = await p.locator('.mx-name-dgObligations [role="row"]:has-text("OBL-007") >> visible=true').first().evaluate(el => {
      const r = el.getBoundingClientRect(); const chain = [];
      for (let n = el.parentElement; n; n = n.parentElement) { const cs = getComputedStyle(n); if (/(auto|scroll)/.test(cs.overflowY)) chain.push({ cls: (n.className || '').toString().slice(0, 60), sh: n.scrollHeight, ch: n.clientHeight, st: n.scrollTop }); }
      return { top: Math.round(r.top), h: Math.round(r.height), inner: innerHeight, chain };
    });
    console.log(JSON.stringify(info));
  } finally { console.log('xas logout: ' + await L.closeSession(s)); }
})().catch(e => { console.error('FAILED', e.message.split('\n')[0]); process.exit(1); });
