// Gera um PNG 1080x1350 para cada <section class="slide"> de artes.html
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 1500 } });
  await page.goto('file://' + path.join(__dirname, 'artes.html'));
  await page.evaluate(() => document.fonts.ready);
  const ids = await page.$$eval('section.slide', els => els.map(e => e.id));
  for (const id of ids) {
    await page.locator('#' + id).screenshot({ path: path.join(__dirname, 'png', id + '.png') });
  }
  await browser.close();
  console.log(ids.length + ' artes geradas');
})();
