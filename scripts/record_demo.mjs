import { chromium } from "playwright";
import { mkdirSync, renameSync, readdirSync, rmSync, existsSync } from "node:fs";
import { join, resolve } from "node:path";

const LIVE_URL = process.env.LIVE_URL || "https://bd-edu-institutes-explorer-6565.netlify.app";
const outDir = resolve("docs/demo/raw");
mkdirSync(outDir, { recursive: true });

for (const file of readdirSync(outDir)) {
  if (file.endsWith(".webm")) rmSync(join(outDir, file), { force: true });
}

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  recordVideo: { dir: outDir, size: { width: 1920, height: 1080 } },
});
const page = await context.newPage();

async function pause(ms = 900) {
  await page.waitForTimeout(ms);
}

async function installCursor() {
  await page.addStyleTag({
    content: `
      .demo-cursor {
        position: fixed;
        z-index: 999999;
        left: 0;
        top: 0;
        width: 22px;
        height: 22px;
        border: 3px solid #cdf66e;
        border-radius: 999px;
        background: rgba(205, 246, 110, .16);
        pointer-events: none;
        transform: translate3d(40px, 40px, 0);
        transition: transform .45s ease, box-shadow .2s ease;
        box-shadow: 0 0 0 5px rgba(8,17,13,.45);
      }
      .demo-cursor.clicking { box-shadow: 0 0 0 12px rgba(205,246,110,.16); }
    `,
  });
  await page.evaluate(() => {
    const cursor = document.createElement("div");
    cursor.className = "demo-cursor";
    document.body.appendChild(cursor);
  });
}

async function moveCursor(x, y, click = false) {
  await page.evaluate(({ x, y, click }) => {
    const cursor = document.querySelector(".demo-cursor");
    if (!cursor) return;
    cursor.style.transform = `translate3d(${x}px, ${y}px, 0)`;
    cursor.classList.toggle("clicking", click);
  }, { x, y, click });
  await page.mouse.move(x + 8, y + 8, { steps: 14 });
  if (click) {
    await page.mouse.down();
    await page.waitForTimeout(120);
    await page.mouse.up();
    await page.evaluate(() => document.querySelector(".demo-cursor")?.classList.remove("clicking"));
  }
}

async function clickSelector(selector, options = {}) {
  const loc = page.locator(selector).first();
  await loc.scrollIntoViewIfNeeded();
  const box = await loc.boundingBox();
  if (box) await moveCursor(box.x + box.width / 2, box.y + box.height / 2, false);
  await loc.click(options);
  await page.evaluate(() => {
    const cursor = document.querySelector(".demo-cursor");
    cursor?.classList.add("clicking");
    setTimeout(() => cursor?.classList.remove("clicking"), 180);
  });
}

await page.goto(LIVE_URL, { waitUntil: "networkidle", timeout: 90000 });
await page.waitForSelector("#districtBubble .main-svg", { timeout: 90000 });
await installCursor();
await pause(1600);

// Homepage and KPI overview.
await moveCursor(920, 270);
await pause(1300);
await page.mouse.wheel(0, 460);
await pause(1200);

// District overview chart.
await moveCursor(1120, 520);
await pause(1200);
await clickSelector('a[href="#analytics"]');
await pause(900);

// Apply search and filter.
await clickSelector("#searchInput");
await page.keyboard.type("DHAKA", { delay: 45 });
await pause(1300);
await clickSelector("#districtFilterSearch");
await page.keyboard.type("Dhaka", { delay: 40 });
await pause(800);
const dhaka = page.locator("#districtFilter label").filter({ hasText: "Dhaka" }).first();
await dhaka.scrollIntoViewIfNeeded();
const dhakaBox = await dhaka.boundingBox();
if (dhakaBox) await moveCursor(dhakaBox.x + 18, dhakaBox.y + 18, false);
await dhaka.click();
await pause(1600);

// AI assistant local explanation.
await clickSelector('a[href="#ai-assistant"]');
await pause(800);
await clickSelector("#aiQuestion");
await page.keyboard.type("Which districts have the highest institute counts?", { delay: 28 });
await pause(500);
await clickSelector("#aiSendBtn");
await page.waitForFunction(() => document.querySelectorAll(".ai-message.assistant").length >= 2, null, { timeout: 20000 });
await pause(2500);

// Records table and detail selection.
await clickSelector('a[href="#records"]');
await pause(900);
await page.mouse.wheel(0, 900);
await page.waitForSelector("#tableBody tr", { timeout: 15000 });
await clickSelector("#tableBody tr");
await pause(1400);

// Clear filters and show validation/empty-state style via search.
await clickSelector("#topResetBtn");
await pause(1200);
await clickSelector("#searchInput");
await page.keyboard.type("zzzz-no-match-demo", { delay: 25 });
await pause(1200);
await clickSelector("#topResetBtn");
await pause(1200);

// Responsive layout demonstration.
await page.setViewportSize({ width: 390, height: 844 });
await pause(1200);
await moveCursor(315, 770, true);
await page.locator("#filterToggle").click();
await pause(1600);
await page.setViewportSize({ width: 1920, height: 1080 });
await pause(1300);

// Final summary view.
await page.evaluate(() => window.scrollTo({ top: 0, behavior: "smooth" }));
await pause(1800);

await context.close();
await browser.close();

const webm = readdirSync(outDir).find((file) => file.endsWith(".webm"));
if (!webm) throw new Error("No video was recorded.");
const finalWebm = resolve("docs/demo/web_app_demo_1080p.webm");
if (existsSync(finalWebm)) rmSync(finalWebm, { force: true });
renameSync(join(outDir, webm), finalWebm);
console.log(finalWebm);
