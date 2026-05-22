import { test, expect } from '@playwright/test';

test('user can open home and submit a video URL', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { name: 'Video Transcription & Summarization' })).toBeVisible();

  const input = page.getByLabel('Video URL');
  await input.fill('https://www.youtube.com/watch?v=jNQXAC9IVRw');

  const submit = page.getByRole('button', { name: 'Start Transcription' });
  await expect(submit).toBeEnabled();

  await submit.click();
  await expect(submit).toBeDisabled();
});
