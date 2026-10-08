// Rasterize every .svg in this folder to a 2x .png with headless Chromium.
//   NODE_PATH=$(npm root -g) node render.cjs
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

(async () => {
  const dir = __dirname;
  const browser = await chromium.launch();
  for (const name of fs.readdirSync(dir).filter((f) => f.endsWith(".svg"))) {
    const svg = fs.readFileSync(path.join(dir, name), "utf8");
    const width = Number(svg.match(/width="(\d+)"/)[1]);
    const height = Number(svg.match(/height="(\d+)"/)[1]);
    const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 2 });
    await page.setContent(`<html><body style="margin:0;background:#fff">${svg}</body></html>`);
    await page.evaluate(() => document.fonts.ready);
    const out = path.join(dir, name.replace(/\.svg$/, ".png"));
    await page.locator("svg").screenshot({ path: out });
    await page.close();
    console.log(`${out} ${width * 2}x${height * 2}`);
  }
  await browser.close();
})();
