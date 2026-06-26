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
        
        # Wait for form to load - look for any input field
        print("⏳ Waiting for form to load...")
        try:
            self.page.locator("input[type='text']").first.wait_for(state="attached", timeout=10000)
            print("✓ Form loaded successfully\n")
        except:
            print("⚠ Form elements not found immediately, continuing anyway...\n")

    def fill_title(self, title: str) -> None:
        """Fill in the title field - uses position-based detection."""
        print(f"📝 Filling title: '{title}'")
        
        try:
            # Get all text inputs
            text_inputs = self.page.locator("input[type='text']")
            count = text_inputs.count()
            
            if count == 0:
                print(f"❌ No text input fields found on page!")
                self.page.screenshot(path="form_debug.png")
                raise Exception("No text input fields found - screenshot saved as form_debug.png")
            
            print(f"   Found {count} text input field(s)")
            
            # Fill the first text input (title)
            first_input = text_inputs.nth(0)
            first_input.fill(title)
            print(f"✓ Title filled successfully (1st input field)\n")
            
        except Exception as e:
            print(f"❌ Failed to fill title: {str(e)}\n")
            self.page.screenshot(path="title_fill_error.png")
            raise

    def fill_url(self, url: str) -> None:
        """Fill in the URL field - uses position-based detection."""
        print(f"📝 Filling URL: '{url}'")
        
        try:
            # Get all text inputs
            text_inputs = self.page.locator("input[type='text']")
            count = text_inputs.count()
            
            if count < 2:
                print(f"❌ Expected at least 2 text input fields, but found {count}!")
                self.page.screenshot(path="form_debug.png")
                raise Exception(f"Not enough input fields - found {count}, expected 2+")
            
            print(f"   Found {count} text input field(s)")
            
            # Fill the second text input (URL)
            second_input = text_inputs.nth(1)
            second_input.fill(url)
            print(f"✓ URL filled successfully (2nd input field)\n")
            
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
            "//button[contains(@class, 'bg-white')]//img",
            "//img",
        ]
        
        clicked = False
        for selector in icon_selectors:
            try:
                locator = self.page.locator(f"xpath={selector}")
                count = locator.count()
                
                if count > 0:
                    # Try to click the first matching icon
                    locator.nth(0).click(timeout=5000)
                    print(f"✓ Icon selected\n")
                    clicked = True
                    break
            except:
                continue
        
        if not clicked:
            print("⚠ Icon selector not found (continuing anyway)\n")

    def save_link(self) -> None:
        """Click on the save button."""
        print("💾 Saving link...")
        
        try:
            # Try to find save button by text content
            save_button = self.page.locator("//button[contains(text(), 'Save') or contains(text(), 'Create') or contains(text(), 'Add')]").first
            
            if save_button.count() == 0:
                # Fallback: try the last button in the form
                form_buttons = self.page.locator("form button")
                if form_buttons.count() > 0:
                    save_button = form_buttons.nth(form_buttons.count() - 1)
                else:
                    raise Exception("No buttons found on form")
            
            save_button.click(timeout=5000)
            self.page.wait_for_load_state("networkidle")
            print(f"✓ Link saved successfully\n")
            
        except Exception as e:
            print(f"❌ Failed to save: {str(e)}\n")
            self.page.screenshot(path="save_button_error.png")
            raise

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
