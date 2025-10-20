// tests/portrait_review.spec.js
const { test, expect } = require('@playwright/test');

test('creates a character and verifies portrait review', async ({ page }) => {
  // Assuming Storycraft is running at http://localhost:5173
  await page.goto('http://localhost:5173');

  // Navigate to the create character page
  await page.locator('text=Create Character').click();

  // Fill minimal required fields (adjust selectors as needed)
  await page.locator('input[name="characterName"]').fill('TestCharacter');
  await page.locator('select[name="classSelection"]').selectOption({ label: 'Fighter' }); // Or any other class
  await page.locator('button:has-text("Next")').click();

  // Navigate to the background section
  await page.locator('button:has-text("Next")').click();


  // Trigger portrait generation and mock backend response if needed
  await page.locator('button:has-text("Generate Portrait")').click();

  // Mock the portrait response (if necessary - remove if your backend is live)
  const mockedPortraitResponse = {
    data: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w+n9QkEBAgAEAwAIAoJcOqAAAAASUVORK5CYII=', // Replace with a valid base64 image
  };

  await page.waitForRequest(request => request.url().includes('generate-portrait'));
  const request = await page.waitForRequest(request => request.url().includes('generate-portrait'));
  request.respond({ status: 200, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(mockedPortraitResponse) });


  // Wait for the review step to load (adjust timeout as needed)
  await page.waitForSelector('text=Review Character', {timeout: 10000});

  // Assert that skin, eyes, and hair traits are displayed
  const traitsText = await page.locator('text=/Skin/').textContent();
  expect(traitsText).toContain('Skin');

  const eyesText = await page.locator('text=/Eyes/').textContent();
  expect(eyesText).toContain('Eyes');

  const hairText = await page.locator('text=/Hair/').textContent();
  expect(hairText).toContain('Hair');


  // Assert that the portrait image is displayed (check data-src or src)
  const portraitImage = await page.locator('img[data-src*="data:image"] || img[src*="data:image"]').first();

  const portraitSrc = await portraitImage.getAttribute('src'); //or data-src depending on implementation
  expect(portraitSrc).toContain('data:image');
});


// Test Setup (install dependencies)
// npm install @playwright/test
// npx playwright install