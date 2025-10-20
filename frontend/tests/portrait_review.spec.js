const { test, expect } = require("@playwright/test");
const fs = require("fs");
const path = require("path");

test("create -> review shows portrait and physical traits", async ({
  page,
}) => {
  // Adjust base URL if your frontend runs elsewhere
  await page.goto("http://localhost:5173");

  // Navigate to Create Character (selector may need adjustment)
  await page.getByText("Create Character").click();

  // Fill minimal fields (selectors may need to match your app)
  const nameInput = page.locator('input[name="characterName"]');
  if ((await nameInput.count()) > 0) {
    await nameInput.fill("PlaywrightTest");
  }

  // Click through steps (assumes Next button advances)
  await page.getByRole("button", { name: /Next/i }).first().click();
  await page.getByRole("button", { name: /Next/i }).first().click();

  // Intercept portrait generation endpoint and mock response
  const portraitPath = path.resolve(
    __dirname,
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
    // If no test image is present, provide a tiny placeholder
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

  // Trigger portrait generation in the UI
  await page.getByRole("button", { name: /Generate Portrait/i }).click();

  // Wait for the review step to appear
  await page.waitForSelector("text=Review Character", { timeout: 15000 });

  // Assert traits labels exist
  await expect(page.locator("text=Skin")).toBeVisible();
  await expect(page.locator("text=Eyes")).toBeVisible();
  await expect(page.locator("text=Hair")).toBeVisible();

  // Assert portrait image contains data URI
  const img = page.locator("img").first();
  await expect(img).toHaveAttribute("src", /data:image\//);
});
