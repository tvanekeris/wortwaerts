// Zweck:   Prüft, ob die Wortwärts-Seite (site/index.html) die Satzliste aufbaut –
//          in mehreren Varianten (Desktop, iPhone + Dunkelmodus, ohne Browser-Stimme,
//          ohne localStorage). Meldet Anzahl der Sätze, Sichtbarkeit und JS-Fehler.
//          Zusätzlich: ohne JavaScript muss der <noscript>-Hinweis erscheinen.
// Aufruf:  cd site && python3 -m http.server 8765 &
//          node scripts/test_seite.js [URL]        (Standard: http://localhost:8765/)
//          Gegen die Live-Seite: node scripts/test_seite.js https://tvanekeris.github.io/wortwaerts/
// Pakete:  Node.js, playwright (mit Chromium); Python 3 nur für den lokalen Webserver.
const { chromium, devices } = require('playwright');

const url = process.argv[2] || 'http://localhost:8765/';
const faelle = [
  ['desktop', {}, null],
  ['iphone-dunkel', { ...devices['iPhone 13'], colorScheme: 'dark' }, null],
  ['ohne-browser-stimme', {}, () => {
    Object.defineProperty(window, 'speechSynthesis', { value: undefined });
    window.SpeechSynthesisUtterance = undefined;
  }],
  ['ohne-localStorage', {}, () => {
    Object.defineProperty(window, 'localStorage', { get() { throw new Error('gesperrt'); } });
  }],
];

(async () => {
  const browser = await chromium.launch();
  let ok = true;
  for (const [name, optionen, vorher] of faelle) {
    const ctx = await browser.newContext(optionen);
    const page = await ctx.newPage();
    if (vorher) await page.addInitScript(vorher);
    const fehler = [];
    page.on('pageerror', e => fehler.push(e.message));
    await page.goto(url);
    await page.waitForTimeout(2500);
    const anzahl = await page.locator('#themen li').count();
    const sichtbar = anzahl > 0 && await page.locator('#themen li').first().isVisible();
    console.log(`${name}: ${anzahl} Sätze, sichtbar=${sichtbar}, Fehler=${JSON.stringify(fehler)}`);
    if (!anzahl || !sichtbar || fehler.length) ok = false;
    await ctx.close();
  }
  const ctx = await browser.newContext({ javaScriptEnabled: false });
  const page = await ctx.newPage();
  await page.goto(url);
  const hinweis = (await page.evaluate(() => document.body.innerText)).includes('braucht JavaScript');
  console.log(`ohne-javascript: Hinweis sichtbar=${hinweis}`);
  if (!hinweis) ok = false;
  await ctx.close();
  await browser.close();
  process.exit(ok ? 0 : 1);
})();
