import { chromium } from "playwright";

const LIVE_URL = process.env.LIVE_URL || "https://bd-edu-institutes-explorer-6565.netlify.app";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const errors = [];
const failedRequests = [];

page.on("console", (msg) => {
  if (msg.type() === "error") errors.push(msg.text());
});
page.on("requestfailed", (req) => failedRequests.push(`${req.method()} ${req.url()} ${req.failure()?.errorText || ""}`));

await page.goto(LIVE_URL, { waitUntil: "networkidle", timeout: 90000 });
await page.waitForSelector("#districtBubble .main-svg", { timeout: 90000 });

const initial = await page.evaluate(() => ({
  hasHero: document.body.innerText.includes("Bangladesh Educational Institutes Explorer"),
  hasAi: document.body.innerText.includes("AI Data Assistant"),
  hasRecords: document.body.innerText.includes("Filtered Institute Records"),
  resultCount: document.querySelector("#resultCount")?.textContent?.trim(),
  districtChart: Boolean(document.querySelector("#districtBubble .main-svg")),
}));

await page.fill("#searchInput", "DHAKA");
await page.waitForTimeout(1200);
const searchCount = await page.textContent("#resultCount");

await page.click('a[href="#ai-assistant"]');
await page.fill("#aiQuestion", "Which districts have the highest institute counts?");
await page.click("#aiSendBtn");
await page.waitForFunction(() => document.querySelectorAll(".ai-message.assistant").length >= 2, null, { timeout: 15000 });
const aiText = await page.locator(".ai-message.assistant").last().innerText();

await page.click('a[href="#records"]');
await page.waitForSelector("#tableBody tr", { timeout: 15000 });
const tableRows = await page.locator("#tableBody tr").count();

await page.setViewportSize({ width: 390, height: 844 });
await page.waitForTimeout(700);
const mobileButtonVisible = await page.locator("#filterToggle").isVisible();

const result = {
  liveUrl: LIVE_URL,
  initial,
  searchCount,
  tableRows,
  aiAnswered: aiText.includes("Main observation") || aiText.length > 60,
  mobileButtonVisible,
  consoleErrors: errors,
  failedRequests,
};

console.log(JSON.stringify(result, null, 2));
if (!initial.hasHero || !initial.hasAi || !initial.districtChart || tableRows === 0 || !result.aiAnswered || !mobileButtonVisible || errors.length) {
  await browser.close();
  process.exit(1);
}

await browser.close();
