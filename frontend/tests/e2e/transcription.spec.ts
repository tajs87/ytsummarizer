import { test, expect } from '@playwright/test';

test('user can open home and submit a video URL', async ({ page }) => {
  // Mock the API call to simulate a pending state
  await page.route('**/api/v1/videos', async (route) => {
    // Delay response to keep button in pending state
    await new Promise((resolve) => setTimeout(resolve, 1000));
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 1,
        url: 'https://www.youtube.com/watch?v=jNQXAC9IVRw',
        title: 'Test Video',
        platform: 'youtube',
        status: 'pending',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }),
    });
  });

  await page.goto('/');

  await expect(page.getByRole('heading', { name: 'Video Transcription & Summarization' })).toBeVisible();

  const input = page.getByLabel('Video URL');
  await input.fill('https://www.youtube.com/watch?v=jNQXAC9IVRw');

  const submit = page.getByRole('button', { name: 'Start Transcription' });
  await expect(submit).toBeEnabled();

  await submit.click();
  await expect(submit).toBeDisabled();
});
