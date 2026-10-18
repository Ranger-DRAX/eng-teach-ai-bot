import { test, expect } from "@playwright/test";

test.describe("Child Learning Journey and Parent Dashboard", () => {
  test("complete end-to-end child journey without audio/voice dependencies", async ({ page }) => {
    // 1. Visit landing page
    await page.goto("/");
    await expect(page.getByRole("heading", { name: /English Learning Chatbot/i })).toBeVisible();

    // 2. Start Learning -> Navigate to Chat
    await page.getByRole("link", { name: /Start Learning/i }).click();
    await expect(page).toHaveURL(/.*chat/);

    // Verify chat UI primitives
    await expect(page.getByText(/English Buddy/i)).toBeVisible();
    await expect(page.getByText(/Level L1/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /Take a break/i })).toBeVisible();

    // Verify absence of any audio or voice input/output elements
    const audioElements = page.locator("audio, video, [aria-label*='voice'], [aria-label*='mic']");
    await expect(audioElements).toHaveCount(0);

    // 3. Child sends an L1 vocabulary message
    const messageInput = page.getByRole("textbox", { name: /Message input/i });
    await messageInput.fill("Blue");
    await page.getByRole("button", { name: /Send message/i }).click();

    // Verify child message appears in conversation log
    await expect(page.getByText("Blue")).toBeVisible();

    // 4. Test Child Autonomy: Take a break triggers support mode
    await page.getByRole("button", { name: /Take a break/i }).click();
    await expect(page.getByText(/take a break/i)).toBeVisible();

    // 5. Navigate to Parent Dashboard
    await page.goto("/dashboard");
    await expect(page.getByRole("heading", { name: /Learning Journey/i })).toBeVisible();

    // Verify level and skills distinction
    await expect(page.getByText(/Level L1/i)).toBeVisible();
    await expect(page.getByText(/Mastered 🏆/i)).toBeVisible();
    await expect(page.getByText(/Developing 🚀/i)).toBeVisible();
    await expect(page.getByText(/Unassessed ⚪/i)).toBeVisible();

    // 6. Test Privacy Controls
    await expect(page.getByRole("button", { name: /Export Learning History/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /Delete Profile/i })).toBeVisible();
  });
});
