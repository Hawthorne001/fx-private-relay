import test, { expect } from "../fixtures/basePages";
import {
  ENV_URLS,
  fetchMaxNumFreeAliases,
  MAX_NUM_FREE_ALIASES,
} from "../e2eTestUtils/helpers";

let freeMaskLimit = MAX_NUM_FREE_ALIASES;

test.describe("Premium - General Functionalities, Desktop", () => {
  test.beforeAll(async () => {
    const env = process.env.E2E_TEST_ENV ?? "stage";
    const baseUrl = ENV_URLS[env] as string;
    freeMaskLimit = await fetchMaxNumFreeAliases(baseUrl);
  });

  test.beforeEach(async ({ landingPage, authPage, dashboardPage }) => {
    await landingPage.open();
    await landingPage.goToSignIn();
    await authPage.login(process.env.E2E_TEST_ACCOUNT_PREMIUM as string);
    const totalMasks = await dashboardPage.emailMasksUsedAmount.textContent();
    await dashboardPage.maybeDeleteMasks(true, parseInt(totalMasks as string));
  });

  test(`Verify that a premium user can make more than ${MAX_NUM_FREE_ALIASES} masks`, async ({
    dashboardPage,
  }) => {
    expect(await dashboardPage.emailMasksUsedAmount.textContent()).toBe("0");
    await dashboardPage.generateMask(freeMaskLimit + 1, true);

    await expect
      .poll(
        async () => {
          return await dashboardPage.emailMasksUsedAmount.textContent();
        },
        {
          intervals: [1_000],
        },
      )
      .toContain(String(freeMaskLimit + 1));
  });

  test("Verify that a user can click the mask blocking options", async ({
    dashboardPage,
  }) => {
    await dashboardPage.generateMask(1, true);
    await dashboardPage.blockPromotions.click();
    expect(await dashboardPage.blockLevelPromosLabel.textContent()).toContain(
      "Blocking promo emails",
    );
    await dashboardPage.blockAll.click();
    expect(await dashboardPage.blockLevelAllLabel.textContent()).toContain(
      "Blocking all emails",
    );
  });

  test("Verify that a premium user can generate a custom mask", async ({
    dashboardPage,
  }) => {
    // When there are zero masks, a random mask must be generated first
    await dashboardPage.generateMask();
    await dashboardPage.generatePremiumDomainMask();
  });
});
