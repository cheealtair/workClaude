'use strict';
// Smoke capture: headless chromium, 1920x1080 viewport, dsf 1, 10 s capture of the login page. No login, no data.
const path = require('path');
const { chromium } = require('playwright');
const polish = require('../demo-polish');
const OUT = path.resolve(__dirname, '../artifacts/film/smoke');
const BASE = process.env.APP_URL || 'http://127.0.0.1:8080/';
(async () => {
  const browser = await chromium.launch({ headless: true, args: polish.launchArgs(1) });
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await polish.prepare(ctx);
  const page = await ctx.newPage();
  await page.goto(BASE, { waitUntil: 'load', timeout: 60000 });
  await page.waitForTimeout(3000);
  const rec = await polish.startCapture(page, { dir: path.join(OUT, 'take') });
  await polish.moveTo(page, 900, 500);
  await page.waitForTimeout(4000);
  await polish.moveTo(page, 1200, 300);
  await page.waitForTimeout(4000);
  const meta = await rec.stop();
  console.log(JSON.stringify(meta));
  polish.assemble(path.join(OUT, 'take'), path.join(OUT, 'smoke.mp4'), { fps: 23 });
  console.log(JSON.stringify(polish.sourceStats(path.join(OUT, 'take'))));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
