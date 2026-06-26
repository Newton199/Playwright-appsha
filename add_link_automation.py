"""
AddLinkPage page object for the Appsha staging site.

Encapsulates all interactions and state inspection on the add-link page at
.../profiles/{id}/links/add-link, exposing per-feature visibility, enabled,
and upgrade-prompt checks, as well as a bulk feature-state collection method.

No time.sleep() calls are used — all waits are expressed via Playwright APIs.
"""

from playwright.sync_api import Page, sync_playwright
from appsha_selectors import FEATURE_SELECTORS, UPGRADE_PROMPT_SELECTORS
from models import FeatureState, FeatureStatus

FEATURES = [
    "normal_link",
    "embed_link",
    "attachment",
    "external_shop",
    "highlight",
    "analytics",
]


class AddLinkPage:
    """Page object for the Appsha add-link page."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def is_feature_visible(self, feature: str) -> bool:
        """Return True if the feature element is visible on the page."""
        loc = self.page.locator(FEATURE_SELECTORS[feature]).first
        try:
            loc.wait_for(state="visible", timeout=3000)
            return True
        except:
            return False

    def is_feature_enabled(self, feature: str) -> bool:
        """Return True if the feature element is enabled (interactable).
        """
        if not self.is_feature_visible(feature):
            return False
        return self.page.locator(FEATURE_SELECTORS[feature]).first.is_enabled()

    def has_upgrade_prompt(self, feature: str) -> bool:
        """Return True if an upgrade/upsell prompt is visible for the feature."""
        return self.page.locator(UPGRADE_PROMPT_SELECTORS[feature]).first.is_visible()

    def get_feature_states(self) -> dict[str, FeatureState]:
        """Collect and return the observable state for all 6 features."""
        states: dict[str, FeatureState] = {}

        for feature in FEATURES:
            visible = self.is_feature_visible(feature)
            enabled = self.is_feature_enabled(feature)
            has_upgrade = self.has_upgrade_prompt(feature)

            if not visible:
                status = FeatureStatus.HIDDEN
            elif has_upgrade:
                status = FeatureStatus.UPGRADE_PROMPT
            elif not enabled:
                status = FeatureStatus.DISABLED
            else:
                status = FeatureStatus.ENABLED

            states[feature] = FeatureState(
                status=status,
                visible=visible,
                enabled=enabled,
                has_upgrade_prompt=has_upgrade,
            )

        assert len(states) == 6, f"Expected 6 feature states, got {len(states)}"
        return states

    # Automation methods for adding a link
    def click_add_link_button(self) -> None:
        """Click on the 'Add Link' button."""
        add_link_selector = "#links > div > div.flex.h-\\[60px\\].items-center.justify-between > div.flex.flex-shrink-0.items-center > a"
        self.page.click(add_link_selector)
        self.page.wait_for_load_state("networkidle")
        print("✓ Clicked 'Add Link' button")

    def click_form_button(self) -> None:
        """Click on the form button."""
        form_button_xpath = "/html/body/div[2]/main/div/div[2]/div/div[1]/div[2]/button[1]"
        self.page.locator(f"xpath={form_button_xpath}").click()
        self.page.wait_for_load_state("networkidle")
        print("✓ Clicked form button")

    def fill_title(self, title: str) -> None:
        """Fill in the title field."""
        title_xpath = "//*[@id=\"_r_h8_-form-item\"]"
        self.page.locator(f"xpath={title_xpath}").fill(title)
        print(f"✓ Filled title: {title}")

    def fill_url(self, url: str) -> None:
        """Fill in the URL field."""
        url_xpath = "//*[@id=\"_r_h9_-form-item\"]"
        self.page.locator(f"xpath={url_xpath}").fill(url)
        print(f"✓ Filled URL: {url}")

    def select_icon(self) -> None:
        """Click on the icon selector."""
        icon_xpath = "//*[@id=\"radix-_r_h7_\"]/div/div/div/div/div[3]/div/div/div/div/div/div/div[2]/img"
        self.page.locator(f"xpath={icon_xpath}").click()
        self.page.wait_for_load_state("networkidle")
        print("✓ Selected icon")

    def save_link(self) -> None:
        """Click on the save button."""
        save_button_xpath = "/html/body/div[2]/main/div/div[2]/div/form/div[3]/button[2]"
        self.page.locator(f"xpath={save_button_xpath}").click()
        self.page.wait_for_load_state("networkidle")
        print("✓ Clicked save button")

    def add_link(self, title: str, url: str) -> None:
        """Complete automation: add a link with the given title and URL."""
        print("\n🔄 Starting link automation...\n")
        self.click_form_button()
        self.fill_title(title)
        self.fill_url(url)
        self.select_icon()
        self.save_link()
        print("\n✅ Link added successfully!\n")


def automate_add_link():
    """Main automation function."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            print("🚀 Launching browser...\n")
            page.goto("https://staging.appsha.com/u/profiles/zubdkqm/links")
            page.wait_for_load_state("networkidle")

            # Create AddLinkPage instance
            add_link_page = AddLinkPage(page)

            # Click add link button
            add_link_page.click_add_link_button()

            # Verify navigation
            page.wait_for_url("**/add-link")
            print(f"✓ Navigated to: {page.url}\n")

            # Add the link
            add_link_page.add_link(title="hello", url="www.appsha.com")

            # Wait to see result
            page.wait_for_load_state("networkidle")

        except Exception as e:
            print(f"\n❌ Error occurred: {str(e)}\n")
            page.screenshot(path="error_screenshot.png")
            print("📸 Screenshot saved: error_screenshot.png")
            raise
        finally:
            browser.close()
            print("🔒 Browser closed")


if __name__ == "__main__":
    automate_add_link()
