import { test, expect } from "@playwright/test";
import fs from "fs";
import path from "path";

test("create -> review shows portrait and physical traits", async ({
  page,
}) => {
  const base = process.env.FRONTEND_URL || "http://localhost:3000";

  // Mock initial GET endpoints so the page loads without hitting a real backend
  await page.route("**/api/generate/options/**", (route) => {
    const body = JSON.stringify({
      themes: ["adventure"],
      character_archetypes: ["Hero", "Villain"],
      personality_traits: ["Brave", "Curious"],
      physical_traits: ["Tall", "Short"],
      emotional_traits: ["Stoic", "Cheerful"],
    });
    route.fulfill({ status: 200, contentType: "application/json", body });
  });
  await page.route("**/api/generate/variations/**", (route) => {
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({}),
    });
  });
  await page.route("**/api/generate/cultural-origins/**", (route) => {
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([]),
    });
  });

  // Mock backend health and characters list that the Characters page requests
  await page.route("**/health", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ status: "ok" }),
    })
  );

  await page.route("**/api/characters/**", (route) => {
    // Return empty character list for fast load (matches ?exclude_portrait=true)
    const url = route.request().url();
    if (
      url.includes("?exclude_portrait=true") ||
      url.endsWith("/api/characters/")
    ) {
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      });
    } else {
      // Default empty response for other characters routes
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({}),
      });
    }
  });

  // Navigate directly to the Create Character page to avoid navigation flakiness
  // Include e2e_mocks=1 so the dev-only hook pre-populates generatedContent
  // and characterName for deterministic testing (only active in development).
  await page.goto(`${base}/create/character?e2e_mocks=1`);

  // Diagnostic: capture console logs and failed requests
  const requestsLog = [];
  // Diagnostic: log all network requests to help debug which endpoints are used
  const requests = [];
  page.on("console", (msg) =>
    requestsLog.push({ type: "console", text: msg.text() })
  );
  page.on("requestfailed", (req) =>
    requestsLog.push({
      type: "requestfailed",
      url: req.url(),
      errorText: req.failure()?.errorText,
    })
  );
  page.on("response", (resp) =>
    requestsLog.push({
      type: "response",
      url: resp.url(),
      status: resp.status(),
    })
  );

  page.on("request", (req) => {
    const url = req.url();
    if (url.includes("/api/")) requests.push(url);
  });

  // We're already on the create page; wait for header/stepper to render
  await page.waitForSelector("text=Create a Character", { timeout: 10000 });

  // Wait for route to update to creation page
  // Allow query params (e.g. ?e2e_mocks=1) and give extra time for SPA routing
  await page.waitForURL("**/create/character*", { timeout: 20000 });

  // Diagnostic: capture the initial DOM once the create page is loaded
  try {
    const earlyDom = await page.content();
    const outDir = path.resolve(process.cwd(), "scripts");
    try {
      fs.mkdirSync(outDir, { recursive: true });
    } catch (e) {}
    fs.writeFileSync(path.join(outDir, "playwright_create_dom.html"), earlyDom);
  } catch (e) {
    // ignore
  }

  // If the dev E2E hook pre-populated generated content, the page may already
  // be on the Review step and the Generate Portrait button will be present.
  // In that case, skip the stepper clicks.
  const portraitBtnEarly = page
    .getByRole("button", { name: /Generate Portrait/i })
    .first();
  const portraitBtnEarlyCount = await portraitBtnEarly.count();
  if (portraitBtnEarlyCount > 0 && (await portraitBtnEarly.isEnabled())) {
    // We are already in the Review step with portrait button enabled; proceed.
    console.log("E2E hook detected: skipping generation stepper");
  } else {
    // Mock generation endpoints so the UI advances quickly
    await page.route("**/api/generate/character/structured/**", (route) => {
      const gen = {
        physical_description: "A young adventurer with a friendly face.",
        hair: "brown",
        eyes: "green",
        skin: "fair",
        height: "5'8\"",
        build: "slim",
        name: "PlaywrightTest",
        personality: "Brave and curious",
      };
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(gen),
      });
    });

    await page.route("**/api/generate/character/**", (route) => {
      const gen = { content: "Narrative content", name: "PlaywrightTest" };
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(gen),
      });
    });

    // Diagnostic: log all network requests to help debug which endpoints are used
    const requests = [];
    page.on("request", (req) => {
      const url = req.url();
      if (url.includes("/api/")) requests.push(url);
    });

    // Wait for the page to render and click through the stepper to generate
    await page.waitForSelector("text=Create a Character", { timeout: 10000 });
    const nextBtn = page
      .getByRole("button", { name: /Next|Generate with AI/i })
      .first();
    await expect(nextBtn).toBeVisible();
    // Click once to advance to the generation step
    await nextBtn.click();

    // Click the Generate button and wait for the generation request to be sent.
    // Re-resolve the button locator because its label may change.
    const genBtn = page
      .getByRole("button", { name: /Generate with AI|Next/i })
      .first();
    await expect(genBtn).toBeVisible({ timeout: 10000 });
    await Promise.all([
      // Don't force method === POST: some flows use GET or different verbs for
      // structured generation. Match any request that targets the character
      // generation path so the mock is applied.
      page.waitForRequest(
        (req) => req.url().includes("/api/generate/character"),
        { timeout: 30000 }
      ),
      genBtn.click(),
    ]);
  }

  // Wait for name options to appear (generatedContent -> NamePicker)
  await page.waitForSelector("text=Choose a Generated Name", {
    timeout: 10000,
  });

  // Fill the Character Name so portrait generation becomes enabled. If the
  // NamePicker rendered suggestions, prefer selecting one so the UI enables
  // the portrait button deterministically.
  const nameField = page.getByLabel("Character Name");
  if ((await nameField.count()) > 0) {
    // Wait briefly for NamePicker options to render
    await page.waitForTimeout(500);

    // If generated name suggestions exist, click the first one
    const firstNameChip = page
      .locator('div:has-text("Choose a Generated Name")')
      .locator("button")
      .first();
    if ((await firstNameChip.count()) > 0) {
      try {
        // Give the chip a little more time to become interactive
        await firstNameChip.click({ timeout: 3000 });
      } catch (e) {
        // fallback to filling the field
        await nameField.fill("PlaywrightTest");
      }
    } else {
      await nameField.fill("PlaywrightTest");
    }
  }

  // Wait for the generated structured content to render (physical traits)
  // before attempting portrait generation. This ensures `generatedContent`
  // in the React state is truthy and the portrait button can enable.
  try {
    await page.waitForSelector("text=brown", { timeout: 10000 });
    await page.waitForSelector("text=green", { timeout: 10000 });
    await page.waitForSelector(
      "text=A young adventurer with a friendly face.",
      { timeout: 10000 }
    );
  } catch (e) {
    console.log(
      "Generated trait texts not found yet - requests:",
      requests.slice(-20)
    );
  }

  // Prepare portrait image (test fixture or tiny placeholder)
  const testDir = path.dirname(new URL(import.meta.url).pathname);
  const portraitPath = path.resolve(
    testDir,
    "..",
    "..",
    "scripts",
    "last_portrait.png"
  );
  let b64 = null;
  try {
    const buf = fs.readFileSync(portraitPath);
    b64 = buf.toString("base64");
  } catch (e) {
    b64 =
      "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAn8B9W5v3QAAAABJRU5ErkJggg==";
  }

  await page.route(
    "**/api/generate/character/generate-portrait/**",
    (route) => {
      const body = JSON.stringify({
        image_base64: b64,
        prompt: "mocked portrait",
      });
      route.fulfill({ status: 200, contentType: "application/json", body });
    }
  );

  // Click Generate Portrait and wait for the portrait image data URI to appear.
  // The button can be initially disabled; wait until it becomes enabled.
  const portraitBtn = page
    .getByRole("button", { name: /Generate Portrait/i })
    .first();
  // Portrait generation may take some UI updates; wait longer for the button
  // to become enabled and re-resolve the locator just before clicking.
  await expect(portraitBtn).toBeEnabled({ timeout: 15000 });
  await portraitBtn.click();
  await page.waitForSelector('img[src^="data:image/"]', { timeout: 15000 });

  // Diagnostic: write captured API requests and page DOM to disk for debugging
  try {
    const outDir = path.resolve(process.cwd(), "scripts");
    try {
      fs.mkdirSync(outDir, { recursive: true });
    } catch (e) {}
    fs.writeFileSync(
      path.join(outDir, "playwright_last_requests.json"),
      JSON.stringify(requests, null, 2)
    );
    const dom = await page.content();
    fs.writeFileSync(path.join(outDir, "playwright_last_dom.html"), dom);
  } catch (e) {
    // ignore
  }

  // Assert mocked physical fields are visible in the StructuredCharacterDisplay
  await expect(page.locator("text=brown")).toBeVisible();
  await expect(page.locator("text=green")).toBeVisible();
  await expect(
    page.locator("text=A young adventurer with a friendly face.")
  ).toBeVisible();

  // Assert portrait image contains data URI
  const img = page.locator("img").first();
  await expect(img).toHaveAttribute("src", /data:image\//);
});
