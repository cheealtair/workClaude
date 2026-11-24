'use strict';
// lib.js - shared pieces for the film rehearsal and (later) recording scripts.
// Password comes ONLY from the environment (TEST_PASS); it is never printed or written.
// Every session ends with the XAS logout call (trial licence session cap); never /logout.
const path = require('path');
const { chromium } = require(path.resolve(__dirname, '..', '..', '..', 'node_modules', 'playwright'));

const BASE = process.env.APP_URL || 'http://127.0.0.1:8080';
const nap = ms => new Promise(r => setTimeout(r, ms));

async function openSession(user, vp, o = {}) {
  const pw = process.env.TEST_PASS;
  if (!pw) { console.error('TEST_PASS not set'); process.exit(2); }
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: o.dsf || 1 });
  const page = await ctx.newPage();
  const errs = [];
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text().slice(0, 160)); });
  page.on('pageerror', e => errs.push('pageerror: ' + String(e).slice(0, 160)));
  await page.goto(BASE + '/login.html');
  await page.fill('#usernameInput', user);
  await page.fill('#passwordInput', pw);
  await page.click('#loginButton');
  await page.waitForSelector('.mx-page', { timeout: 40000 });
  return { browser, ctx, page, errs };
}

async function logout(page) {
  try {
    await page.evaluate(async () => {
      const s = (window.mx && mx.session) || {};
      const t = (s.sessionData && s.sessionData.csrftoken) || '';
      if (t) await fetch('/xas/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Csrf-Token': t }, body: JSON.stringify({ action: 'logout', params: {} }) });
    });
    return true;
  } catch (e) { return false; }
}

async function closeSession(s) {
  const ok = await logout(s.page);
  await s.ctx.close().catch(() => {});
  await s.browser.close().catch(() => {});
  return ok;
}

// Elements whose text is cut by overflow (ellipsis or hidden), limited to the visible viewport area.
async function clippedLabels(page, scopeSel) {
  return page.evaluate((sel) => {
    const root = sel ? document.querySelector(sel) : document.body;
    if (!root) return ['(scope not found)'];
    const out = [];
    root.querySelectorAll('*').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width < 4 || r.height < 4 || r.bottom < 0 || r.top > innerHeight || r.right < 0) return;
      const cs = getComputedStyle(el);
      if (cs.visibility === 'hidden' || cs.display === 'none') return;
      const txt = (el.innerText || '').trim();
      if (!txt || el.children.length > 2) return;
      if (el.scrollWidth > el.clientWidth + 2 && (cs.overflowX === 'hidden' || cs.textOverflow === 'ellipsis' || cs.overflow === 'hidden'))
        out.push(txt.replace(/\s+/g, ' ').slice(0, 70) + ' [' + el.scrollWidth + '>' + el.clientWidth + ']');
    });
    return [...new Set(out)].slice(0, 25);
  }, scopeSel || null);
}

module.exports = { BASE, nap, openSession, closeSession, logout, clippedLabels };
