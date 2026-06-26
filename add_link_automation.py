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

    def inspect_page_elements(self) -> None:
        """Debug function: inspect all form elements on the page."""
        print("\n" + "="*60)
        print("🔍 INSPECTING PAGE ELEMENTS")
        print("="*60 + "\n")
        
        # Get all input fields
        inputs = self.page.locator("input").all()
        print(f"📝 Found {len(inputs)} input fields:")
        for i, inp in enumerate(inputs):
            try:
                input_id = inp.get_attribute("id")
                input_name = inp.get_attribute("name")
                input_type = inp.get_attribute("type")
                input_placeholder = inp.get_attribute("placeholder")
                print(f"  [{i}] ID: {input_id} | Name: {input_name} | Type: {input_type} | Placeholder: {input_placeholder}")
            except:
                pass
        
        # Get all text fields specifically
        text_inputs = self.page.locator("input[type='text']").all()
        print(f"\n📄 Found {len(text_inputs)} text input fields:")
        for i, inp in enumerate(text_inputs):
            try:
                input_id = inp.get_attribute("id")
                input_name = inp.get_attribute("name")
                input_placeholder = inp.get_attribute("placeholder")
                print(f"  [{i}] ID: {input_id} | Name: {input_name} | Placeholder: {input_placeholder}")
            except:
                pass
        
        # Get all form elements
        forms = self.page.locator("form").all()
        print(f"\n📋 Found {len(forms)} form(s)")
        
        # Get all buttons
        buttons = self.page.locator("button").all()
        print(f"\n🔘 Found {len(buttons)} buttons:")
        for i, btn in enumerate(buttons):
            try:
                btn_text = btn.text_content()
                btn_id = btn.get_attribute("id")
                btn_type = btn.get_attribute("type")
                print(f"  [{i}] Text: {btn_text.strip() if btn_text else 'N/A'} | ID: {btn_id} | Type: {btn_type}")
            except:
                pass
        
        # Get all divs with specific classes
        divs = self.page.locator("div[class*='form']").all()
        print(f"\n📦 Found {len(divs)} divs with 'form' in class")
        
        print("\n" + "="*60 + "\n")

    # Automation methods for adding a link
    def click_add_link_button(self) -> None:
        """Click on the 'Add Link' button."""
        add_link_selector = "#links > div > div.flex.h-\\[60px\\].items-center.justify-between > div.flex.flex-shrink-0.items-center > a"
        self.page.click(add_link_selector)
        self.page.wait_for_load_state("networkidle")
        print("✓ Clicked 'Add Link' button")

    def click_form_button(self) -> None:
        """Click on the form button or proceed to add link."""
        # Try to find and click a button that opens the form
        try:
            form_button_xpath = "/html/body/div[2]/main/div/div[2]/div/div[1]/div[2]/button[1]"
            self.page.locator(f"xpath={form_button_xpath}").click()
            self.page.wait_for_load_state("networkidle")
            print("✓ Clicked form button")
        except:
            print("⚠ Form button not found, continuing...")
            self.page.wait_for_load_state("networkidle")

    def navigate_to_add_link_form(self) -> None:
        """Navigate to the add-link form page."""
        print("🔗 Navigating to add-link form...\n")
        self.page.goto("https://staging.appsha.com/u/profiles/zubdkqm/links/add-link/link")
        self.page.wait_for_load_state("networkidle")
        print(f"✓ Navigated to: {self.page.url}\n")
        
        # Inspect elements on this page
        self.inspect_page_elements()

    def fill_title_smart(self, title: str) -> None:
        """Fill in the title field - tries multiple approaches."""
        print(f"📝 Attempting to fill title: '{title}'\n")
        
        # Get all text inputs
        text_inputs = self.page.locator("input[type='text']").all()
        
        if len(text_inputs) > 0:
            # Try first text input
            try:
                text_inputs[0].fill(title)
                print(f"✓ Filled title using first text input")
                return
            except Exception as e:
                print(f"❌ First text input failed: {str(e)[:50]}")
        
        # Try by ID containing common patterns
        id_patterns = ["title", "name", "link-title", "subject"]
        for pattern in id_patterns:
            try:
                locator = self.page.locator(f"input[id*='{pattern}']").first
                if locator.count() > 0:
                    locator.fill(title)
                    print(f"✓ Filled title using ID pattern: '{pattern}'")
                    return
            except:
                pass
        
        raise Exception(f"Could not fill title field - found {len(text_inputs)} text inputs but all failed")

    def fill_url_smart(self, url: str) -> None:
        """Fill in the URL field - tries multiple approaches."""
        print(f"📝 Attempting to fill URL: '{url}'\n")
        
        # Get all text inputs
        text_inputs = self.page.locator("input[type='text']").all()
        
        if len(text_inputs) > 1:
            # Try second text input
            try:
                text_inputs[1].fill(url)
                print(f"✓ Filled URL using second text input")
                return
            except Exception as e:
                print(f"❌ Second text input failed: {str(e)[:50]}")
        
        # Try by ID containing common patterns
        id_patterns = ["url", "link", "href", "website"]
        for pattern in id_patterns:
            try:
                locator = self.page.locator(f"input[id*='{pattern}']").first
                if locator.count() > 0:
                    locator.fill(url)
                    print(f"✓ Filled URL using ID pattern: '{pattern}'")
                    return
            except:
                pass
        
        # Try URL input type
        try:
            self.page.locator("input[type='url']").first.fill(url)
            print(f"✓ Filled URL using input[type='url']")
            return
        except:
            pass
        
        raise Exception(f"Could not fill URL field - found {len(text_inputs)} text inputs but all failed")

    def select_icon(self) -> None:
        """Click on the icon selector."""
        icon_xpaths = [
            "//img[@role='img']",
            "//button[contains(@aria-label, 'icon')]",
            "img[alt*='icon']",
            "//img",
        ]
        
        clicked = False
        for xpath in icon_xpaths:
            try:
                locator = self.page.locator(f"xpath={xpath}" if xpath.startswith("/") else xpath)
                if locator.count() > 0:
                    locator.first.wait_for(state="visible", timeout=5000)
                    locator.first.click()
                    self.page.wait_for_load_state("networkidle")
                    print(f"✓ Selected icon (using selector: {xpath})")
                    clicked = True
                    break
            except Exception as e:
                print(f"  Icon selector '{xpath}' failed")
                continue
        
        if not clicked:
            print("⚠ Could not find icon selector (skipping)")

    def save_link(self) -> None:
        """Click on the save button."""
        save_selectors = [
            "button[type='submit']",
            "//button[contains(text(), 'Save')]",
            "//button[contains(text(), 'Create')]",
            "//button[contains(text(), 'Add')]",
            "//button",
        ]
        
        clicked = False
        for selector in save_selectors:
            try:
                locator = self.page.locator(f"xpath={selector}" if selector.startswith("/") else selector)
                if locator.count() > 0:
                    # Get button text to be sure
                    for btn in locator.all():
                        btn_text = btn.text_content()
                        if btn_text and any(word in btn_text.lower() for word in ['save', 'create', 'add', 'submit']):
                            btn.click()
                            self.page.wait_for_load_state("networkidle")
                            print(f"✓ Clicked save button: '{btn_text.strip()}'")
                            clicked = True
                            break
                    if clicked:
                        break
            except Exception as e:
                pass
        
        if not clicked:
            print("❌ Could not find save button!")
            self.page.screenshot(path="save_button_debug.png")
            raise Exception("Save button not found")

    def add_link(self, title: str, url: str) -> None:
        """Complete automation: add a link with the given title and URL."""
        print("\n🔄 Starting link automation...\n")
        self.fill_title_smart(title)
        self.fill_url_smart(url)
        self.select_icon()
        self.save_link()
        print("\n✅ Link added successfully!\n")


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

        except Exception as e:
            print(f"\n❌ Error occurred: {str(e)}\n")
            page.screenshot(path="error_screenshot.png")
            print("📸 Screenshot saved: error_screenshot.png")
            raise
        finally:
            browser.close()
            print("\n🔒 Browser closed")


if __name__ == "__main__":
    automate_add_link()
