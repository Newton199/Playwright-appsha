"""
AddLinkPage page object for the Appsha staging site with Login.

Encapsulates all interactions and state inspection on the add-link page at
.../profiles/{id}/links/add-link, exposing per-feature visibility, enabled,
and upgrade-prompt checks, as well as a bulk feature-state collection method.

No time.sleep() calls are used — all waits are expressed via Playwright APIs.
"""

from playwright.sync_api import Page, sync_playwright
from pages.login_page import LoginPage
from appsha_selectors import FEATURE_SELECTORS, UPGRADE_PROMPT_SELECTORS
from models import FeatureState, FeatureStatus
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

FEATURES = [
    "normal_link",
    "embed_link",
    "attachment",
    "external_shop",
    "highlight",
    "analytics",
]

# Credentials
EMAIL = os.environ.get("APPSHA_EMAIL", "newton.appsha@gmail.com")
PASSWORD = os.environ.get("APPSHA_PASSWORD", "Newton@#26")


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
    def navigate_to_add_link_form(self) -> None:
        """Navigate to the add-link form page."""
        print("🔗 Navigating to add-link form...\n")
        self.page.goto("https://staging.appsha.com/u/profiles/zubdkqm/links/add-link/link")
        self.page.wait_for_load_state("networkidle")
        print(f"✓ Navigated to: {self.page.url}\n")

    def fill_title(self, title: str) -> None:
        """Fill in the title field using the exact selector."""
        print(f"📝 Filling title: '{title}'")
        
        try:
            # Use exact selector for title field
            title_selector = "#_r_24f_-form-item"
            locator = self.page.locator(title_selector)
            
            locator.scroll_into_view_if_needed()
            locator.wait_for(state="visible", timeout=5000)
            locator.fill(title)
            print(f"✓ Title filled successfully\n")
        except Exception as e:
            print(f"❌ Failed to fill title: {str(e)}\n")
            self.page.screenshot(path="title_fill_error.png")
            raise

    def fill_url(self, url: str) -> None:
        """Fill in the URL field using the exact selector."""
        print(f"📝 Filling URL: '{url}'")
        
        try:
            # Use exact selector for URL field
            url_selector = "#_r_24g_-form-item"
            locator = self.page.locator(url_selector)
            
            locator.scroll_into_view_if_needed()
            locator.wait_for(state="visible", timeout=5000)
            locator.fill(url)
            print(f"✓ URL filled successfully\n")
        except Exception as e:
            print(f"❌ Failed to fill URL: {str(e)}\n")
            self.page.screenshot(path="url_fill_error.png")
            raise

    def select_icon(self) -> None:
        """Click on the icon selector."""
        print("🎨 Selecting icon...")
        
        icon_selectors = [
            "//img[@role='img']",
            "//button[contains(@aria-label, 'icon')]",
            "img[alt*='icon']",
            "//img[contains(@class, 'cursor')]",
            "//img",
        ]
        
        clicked = False
        for selector in icon_selectors:
            try:
                locator = self.page.locator(f"xpath={selector}" if selector.startswith("/") else selector)
                if locator.count() > 0:
                    locator.first.wait_for(state="visible", timeout=3000)
                    locator.first.click()
                    self.page.wait_for_load_state("networkidle")
                    print(f"✓ Icon selected\n")
                    clicked = True
                    break
            except Exception as e:
                continue
        
        if not clicked:
            print("⚠ Icon selector not found (continuing anyway)\n")

    def save_link(self) -> None:
        """Click on the save button using the exact selector provided."""
        print("💾 Saving link...")
        
        try:
            # Use the exact selector provided for save button
            save_selector = "body > div.group\\/sidebar-wrapper.flex.min-h-svh.has-\\[\\[data-variant\\=inset\\]\\]\\:bg-sidebar.w-full > main > div > div.m-0.sm\\:m-6.xl\\:max-w-\\[600px\\].xl2\\:max-w-\\[690px\\].\\32 xl\\:max-w-\\[800px\\].min-\\[2000px\\]\\:max-w-\\[1000px\\] > div > form > div.flex.w-full.items-center.justify-end.gap-2 > button.inline-flex.items-center.hover\\:shadow-sm.justify-center.gap-2.whitespace-nowrap.ring-offset-background.transition-all.focus-visible\\:outline-none.focus-visible\\:ring-2.focus-visible\\:ring-ring.focus-visible\\:ring-offset-2.disabled\\:pointer-events-none.disabled\\:opacity-50.active\\:scale-95.\\[\\&_svg\\]\\:pointer-events-none.\\[\\&_svg\\]\\:size-4.\\[\\&_svg\\]\\:shrink-0.bg-primary.hover\\:bg-blue-800.h-10.px-6.py-3.w-fit.rounded-\\[4px\\].text-sm.font-semibold.text-white.md\\:text-base.md\\:font-bold"
            
            locator = self.page.locator(save_selector)
            locator.scroll_into_view_if_needed()
            locator.wait_for(state="visible", timeout=5000)
            locator.click()
            self.page.wait_for_load_state("networkidle")
            print(f"✓ Link saved successfully\n")
            
        except Exception as e:
            print(f"❌ Failed to save with exact selector: {str(e)[:80]}\n")
            
            # Try fallback selectors
            fallback_selectors = [
                "button[type='submit']",
                "//button[contains(text(), 'Save')]",
                "//button[contains(text(), 'Create')]",
                "form button:last-of-type",
                "//form//button[last()]",
            ]
            
            clicked = False
            for selector in fallback_selectors:
                try:
                    locator = self.page.locator(f"xpath={selector}" if selector.startswith("/") else selector)
                    if locator.count() > 0:
                        btn = locator.first
                        btn_text = btn.text_content()
                        btn.scroll_into_view_if_needed()
                        btn.wait_for(state="visible", timeout=5000)
                        btn.click()
                        self.page.wait_for_load_state("networkidle")
                        print(f"✓ Link saved with fallback selector\n")
                        clicked = True
                        break
                except:
                    continue
            
            if not clicked:
                print("❌ Could not find save button!")
                self.page.screenshot(path="save_button_debug.png")
                raise Exception("Save button not found")

    def add_link(self, title: str, url: str) -> None:
        """Complete automation: add a link with the given title and URL."""
        print("\n" + "="*60)
        print("🔄 STARTING LINK AUTOMATION")
        print("="*60 + "\n")
        
        self.fill_title(title)
        self.fill_url(url)
        self.select_icon()
        self.save_link()
        
        print("="*60)
        print("✅ LINK ADDED SUCCESSFULLY!")
        print("="*60 + "\n")


def automate_add_link():
    """Main automation function with login."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            print("🚀 Launching browser...\n")
            
            # Step 1: Login
            print("📝 Logging in...\n")
            login_page = LoginPage(page)
            login_page.login(EMAIL, PASSWORD)
            print(f"✓ Successfully logged in with email: {EMAIL}")
            print(f"✓ Current URL: {page.url}\n")
            
            # Create AddLinkPage instance
            add_link_page = AddLinkPage(page)

            # Step 2: Navigate to add-link form directly
            add_link_page.navigate_to_add_link_form()

            # Step 3: Add the link
            add_link_page.add_link(title="helllo", url="https://appsha.com/")

            # Step 4: Wait to see result
            page.wait_for_load_state("networkidle")
            print(f"✓ Final URL: {page.url}")
            print("\n🎉 Automation completed successfully!\n")

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
