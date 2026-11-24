'use strict';
// explore3.js - read-only: Explore on a finding, dump the navigator list and counts, shoot the graph. Usage: node explore3.js <w> <h> <user> <findingText> <tag> [detailsRowText] [preset]
const L = require('./lib.js');
const path = require('path');
const OUT = path.resolve(__dirname, '..', 'artifacts', 'film', 'rehearsal');
(async () => {
  const [w, h, user, find, tag, rowText, preset] = process.argv.slice(2);
  const s = await L.openSession(user, { width: +w, height: +h });
  const p = s.page;
  try {
    await p.goto(L.BASE + '/p/findings');
    await p.waitForSelector('.mx-name-dgFindings [role="gridcell"]', { timeout: 30000 });
    await L.nap(1200);
    await p.locator(`.mx-name-dgFindings [role="gridcell"]:has-text("${find}")`).first().click();
    await p.waitForSelector('.mx-name-btnNavStart', { timeout: 40000 });
    await L.nap(2500);
    await p.locator('.mx-name-btnNavStart').first().click();
    await p.waitForSelector('.mx-name-btnNavRestart', { timeout: 40000 });
    await L.nap(5000);
    const nav = p.locator('.mx-name-ctnNavigator').first();
    await nav.scrollIntoViewIfNeeded();
    await L.nap(800);
    await p.screenshot({ path: path.join(OUT, `nav-${tag}-1-explored-${w}.png`) });
    await p.locator('[class*="mx-name-ngNav"]:visible').first().evaluate(e => e.scrollIntoView({ block: 'center' })).catch(() => {});
    await L.nap(800);
    await p.screenshot({ path: path.join(OUT, `nav-${tag}-1b-graph-${w}.png`) });
    const counts = (await p.locator('.mx-name-txtNavCounts').first().innerText().catch(() => '')).trim();
    const status = (await p.locator('.mx-name-txtNavStatus').first().innerText().catch(() => '')).trim();
    console.log('counts: ' + counts + '\nstatus: ' + status);
    const rows = await p.locator('.mx-name-dgNavNodes [role="row"]').evaluateAll(e => e.map(x => x.innerText.replace(/\s+/g, ' ').trim().slice(0, 130)));
    console.log('list rows (' + rows.length + '):'); rows.forEach(r => console.log('  ' + r));
    const gbox = await p.locator('[class*="mx-name-ngNav"]:visible').first().boundingBox().catch(() => null);
    console.log('graph box: ' + JSON.stringify(gbox));
    console.log('clipped(nav): ' + JSON.stringify(await L.clippedLabels(p, '.mx-name-ctnNavigator')));
    if (rowText) {
      const r = p.locator('.mx-name-dgNavNodes [role="row"]').filter({ hasText: rowText }).first();
      await r.locator('.mx-name-btnNavSelect').first().click();
      await p.waitForSelector('.mx-name-txtNavSelTitle', { timeout: 30000 });
      await L.nap(3500);
      await p.screenshot({ path: path.join(OUT, `nav-${tag}-2-details-${w}.png`) });
      console.log('panel: ' + (await p.locator('.mx-name-dvNavSel').first().innerText().catch(() => '')).replace(/\s+/g, ' ').slice(0, 500));
      console.log('buttons: ' + JSON.stringify(await p.locator('.mx-name-ctnNavigator [class*="mx-name-btnNav"]:visible').evaluateAll(e => e.map(x => (x.className.match(/mx-name-(btnNav\w+)/) || [])[1] + ':' + x.innerText.trim().slice(0, 50)))));
      if (preset) {
        await p.locator(`.mx-name-btnNavPreset${preset}`).first().click();
        await L.nap(12000);
        await p.screenshot({ path: path.join(OUT, `nav-${tag}-3-preset-${w}.png`) });
        console.log('after preset counts: ' + (await p.locator('.mx-name-txtNavCounts').first().innerText().catch(() => '')).trim());
        console.log('after preset status: ' + (await p.locator('.mx-name-txtNavStatus').first().innerText().catch(() => '')).trim());
      }
    }
  } finally {
    console.log('errors: ' + s.errs.length);
    console.log('xas logout: ' + await L.closeSession(s));
  }
})().catch(e => { console.error('FAILED', e.message.split('\n')[0]); process.exit(1); });
