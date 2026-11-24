'use strict';
// explore1.js - read-only look: nav links, Findings grid rows, clipping, at a given viewport. Usage: node explore1.js <w> <h> <user>
const L = require('./lib.js');
const path = require('path');
const OUT = path.resolve(__dirname, '..', 'artifacts', 'film', 'rehearsal');
(async () => {
  const [w, h, user = 'manager'] = process.argv.slice(2);
  const s = await L.openSession(user, { width: +w, height: +h });
  const p = s.page;
  try {
    await L.nap(2500);
    await p.screenshot({ path: path.join(OUT, `ex1-${user}-landing-${w}.png`) });
    const links = await p.locator('a[title]:visible').evaluateAll(e => e.map(x => x.title + '|' + (x.getAttribute('href') || '')));
    console.log('nav links: ' + JSON.stringify(links));
    console.log('landing url: ' + p.url());
    console.log('clipped (landing): ' + JSON.stringify(await L.clippedLabels(p)));
    await p.goto(L.BASE + '/p/findings');
    await p.waitForSelector('.mx-name-dgFindings [role="gridcell"]', { timeout: 30000 });
    await L.nap(2500);
    await p.screenshot({ path: path.join(OUT, `ex1-${user}-findings-${w}.png`) });
    const rows = await p.locator('.mx-name-dgFindings [role="row"]').evaluateAll(e => e.map(x => x.innerText.replace(/\s+/g, ' ').trim()));
    console.log('findings rows (' + rows.length + '):'); rows.forEach(r => console.log('  ' + r));
    console.log('clipped (findings): ' + JSON.stringify(await L.clippedLabels(p)));
    const pager = await p.locator('.mx-name-dgFindings .paging-status').allInnerTexts().catch(() => []);
    console.log('pager: ' + JSON.stringify(pager));
  } finally {
    console.log('errors: ' + JSON.stringify(s.errs.slice(0, 4)));
    console.log('xas logout: ' + await L.closeSession(s));
  }
})().catch(e => { console.error('FAILED', e.message.split('\n')[0]); process.exit(1); });
