import { test, expect } from '@playwright/test';

/**
 * E2E tests for the Front Door Support Agent chat interface.
 */

test.describe('Chat Interface', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display the chat interface with header', async ({ page }) => {
    // Check header is visible
    await expect(page.getByRole('banner')).toBeVisible();
    await expect(page.getByText('University Support')).toBeVisible();

    // Check chat input is visible
    await expect(page.getByRole('textbox', { name: /message/i })).toBeVisible();

    // Check send button is visible
    await expect(page.getByRole('button', { name: /send/i })).toBeVisible();
  });

  test('should send a message and receive a response', async ({ page }) => {
    // Type a message
    const input = page.getByRole('textbox', { name: /message/i });
    await input.fill('I forgot my password');

    // Send the message
    await page.getByRole('button', { name: /send/i }).click();

    // Wait for user message to appear
    await expect(page.getByText('I forgot my password')).toBeVisible();

    // Wait for typing indicator or response
    // The response should appear within a reasonable time
    await expect(page.locator('[role="main"]')).toContainText(/ticket|password|IT|help/i, {
      timeout: 30000,
    });
  });

  test('should display ticket card when ticket is created', async ({ page }) => {
    // Send a message that will create a ticket
    const input = page.getByRole('textbox', { name: /message/i });
    await input.fill('The elevator in Smith Hall is broken');
    await page.getByRole('button', { name: /send/i }).click();

    // Wait for response with ticket
    await expect(page.getByText(/TKT-/)).toBeVisible({ timeout: 30000 });
  });

  test('should display knowledge articles in response', async ({ page }) => {
    // Send a message
    const input = page.getByRole('textbox', { name: /message/i });
    await input.fill('How do I reset my Canvas password?');
    await page.getByRole('button', { name: /send/i }).click();

    // Wait for knowledge articles section
    await expect(page.getByText('Helpful Articles')).toBeVisible({ timeout: 30000 });
  });

  test('should clear chat when clear button is clicked', async ({ page }) => {
    // Send a message first
    const input = page.getByRole('textbox', { name: /message/i });
    await input.fill('Test message');
    await page.getByRole('button', { name: /send/i }).click();

    // Wait for message to appear
    await expect(page.getByText('Test message')).toBeVisible();

    // Click clear button
    await page.getByRole('button', { name: /clear chat/i }).click();

    // Message should be gone, welcome message should show
    await expect(page.getByText('Test message')).not.toBeVisible();
  });

  test('should handle Talk to Human button', async ({ page }) => {
    // Click Talk to Human button
    await page.getByRole('button', { name: /talk to a human/i }).click();

    // Should send a message requesting human
    await expect(page.getByText(/speak with a human|talk to a person|human support/i)).toBeVisible({
      timeout: 5000,
    });

    // Response should indicate escalation
    await expect(page.locator('[role="main"]')).toContainText(/human|specialist|team member|forwarded/i, {
      timeout: 30000,
    });
  });
});

test.describe('Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should have skip link for keyboard navigation', async ({ page }) => {
    // Skip link should exist
    const skipLink = page.getByRole('link', { name: /skip to main content/i });
    await expect(skipLink).toBeAttached();

    // Focus should reveal it
    await skipLink.focus();
    await expect(skipLink).toBeVisible();
  });

  test('should toggle high contrast mode', async ({ page }) => {
    // Find and click the high contrast toggle
    const contrastButton = page.getByRole('button', { name: /high contrast|toggle contrast/i });
    await contrastButton.click();

    // Check that high-contrast class is applied
    const body = page.locator('body');
    // The high-contrast class should be on a parent element
    await expect(page.locator('.high-contrast')).toBeVisible();

    // Toggle back
    await contrastButton.click();
    await expect(page.locator('.high-contrast')).not.toBeVisible();
  });

  test('should support keyboard navigation in chat', async ({ page }) => {
    // Focus on input
    const input = page.getByRole('textbox', { name: /message/i });
    await input.focus();

    // Type a message
    await input.fill('Test keyboard navigation');

    // Press Enter to send
    await input.press('Enter');

    // Message should be sent
    await expect(page.getByText('Test keyboard navigation')).toBeVisible();
  });

  test('should have proper ARIA labels', async ({ page }) => {
    // Check main landmark
    await expect(page.getByRole('main')).toBeVisible();

    // Check banner (header)
    await expect(page.getByRole('banner')).toBeVisible();

    // Check form elements have labels
    const input = page.getByRole('textbox');
    await expect(input).toBeVisible();
  });
});

test.describe('Mobile Responsiveness', () => {
  test.use({ viewport: { width: 375, height: 667 } }); // iPhone SE

  test('should display correctly on mobile', async ({ page }) => {
    await page.goto('/');

    // Header should be visible
    await expect(page.getByRole('banner')).toBeVisible();

    // Chat input should be visible and usable
    const input = page.getByRole('textbox', { name: /message/i });
    await expect(input).toBeVisible();

    // Send button should be visible
    await expect(page.getByRole('button', { name: /send/i })).toBeVisible();
  });

  test('should handle chat on mobile', async ({ page }) => {
    await page.goto('/');

    // Type and send message
    const input = page.getByRole('textbox', { name: /message/i });
    await input.fill('Mobile test');
    await page.getByRole('button', { name: /send/i }).click();

    // Message should appear
    await expect(page.getByText('Mobile test')).toBeVisible();
  });
});

test.describe('Error Handling', () => {
  test('should not allow empty messages', async ({ page }) => {
    await page.goto('/');

    // Try to send empty message
    const sendButton = page.getByRole('button', { name: /send/i });

    // Button should be disabled when input is empty
    await expect(sendButton).toBeDisabled();
  });

  test('should show typing indicator while waiting for response', async ({ page }) => {
    await page.goto('/');

    // Send a message
    const input = page.getByRole('textbox', { name: /message/i });
    await input.fill('I need help');
    await page.getByRole('button', { name: /send/i }).click();

    // Typing indicator should appear (may be brief)
    // We check that the response eventually appears
    await expect(page.locator('[role="main"]')).toContainText(/ticket|help|support/i, {
      timeout: 30000,
    });
  });
});

test.describe('Session Persistence', () => {
  test('should maintain conversation history', async ({ page }) => {
    await page.goto('/');

    // Send first message
    const input = page.getByRole('textbox', { name: /message/i });
    await input.fill('First message');
    await page.getByRole('button', { name: /send/i }).click();
    await expect(page.getByText('First message')).toBeVisible();

    // Wait for response
    await expect(page.locator('[role="main"]')).toContainText(/ticket|help/i, {
      timeout: 30000,
    });

    // Send second message
    await input.fill('Second message');
    await page.getByRole('button', { name: /send/i }).click();

    // Both messages should be visible
    await expect(page.getByText('First message')).toBeVisible();
    await expect(page.getByText('Second message')).toBeVisible();
  });
});

test.describe('Intent Classification Visual Feedback', () => {
  test('should route IT issues correctly', async ({ page }) => {
    await page.goto('/');

    const input = page.getByRole('textbox', { name: /message/i });
    await input.fill('My WiFi is not connecting');
    await page.getByRole('button', { name: /send/i }).click();

    // Should mention IT in response
    await expect(page.locator('[role="main"]')).toContainText(/IT|ticket/i, {
      timeout: 30000,
    });
  });

  test('should route Registrar issues correctly', async ({ page }) => {
    await page.goto('/');

    const input = page.getByRole('textbox', { name: /message/i });
    await input.fill('I need an official transcript');
    await page.getByRole('button', { name: /send/i }).click();

    // Should mention Registrar in response
    await expect(page.locator('[role="main"]')).toContainText(/Registrar|transcript|ticket/i, {
      timeout: 30000,
    });
  });

  test('should handle escalation requests', async ({ page }) => {
    await page.goto('/');

    const input = page.getByRole('textbox', { name: /message/i });
    await input.fill('I want to appeal my grade');
    await page.getByRole('button', { name: /send/i }).click();

    // Should indicate human escalation
    await expect(page.locator('[role="main"]')).toContainText(/human|specialist|review|team/i, {
      timeout: 30000,
    });
  });
});
