import os, sys
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from playwright.sync_api import sync_playwright
from pages.login_page import LoginPage
from pages.contacts_page import ContactsPage, ContactData
import appsha_selectors as S

EMAIL = os.environ.get("APPSHA_EMAIL", "newton.appsha@gmail.com")
PASSWORD = os.environ.get("APPSHA_PASSWORD", "Newton@#26")

def run_final_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        
        # 1. LOGIN
        print("Starting Login...")
        login = LoginPage(page)
        login.login(EMAIL, PASSWORD)
        print("Login Success.")

        # 2. LINKS
        print("Navigating to Links...")
        page.click("text=Links")
        page.wait_for_url("**/links")
        print("Links page loaded.")

        # 3. APPEARANCE
        print("Navigating to Appearance...")
        page.click("text=Appearance")
        page.wait_for_url("**/appearance")
        print("Appearance page loaded.")

        # 4. CONTACTS & ADD DUMMY
        print("Navigating to Contacts...")
        cp = ContactsPage(page)
        cp.navigate()
        
        dummy_contact = ContactData(
            name="Zeta Automation",
            email="zeta@appsha.com",
            phone="+9779841234567",
            address="123 Appsha Way, Tech City",
            birthday="1995-01-01",
            anniversary="2024-06-23",
            note="High accuracy test run with all fields",
            tags=["Automation", "Priority"]
        )

        
        print(f"Creating Contact: {dummy_contact.name}")
        cp.create_contact(dummy_contact)
        
        print("Verifying Contact...")
        page.wait_for_timeout(2000)
        if cp.contact_exists(dummy_contact.name):
            print(f"SUCCESS: Contact '{dummy_contact.name}' created and visible.")
        else:
            print(f"FAILED: Contact '{dummy_contact.name}' not found in table.")
            page.screenshot(path="final_error.png")

        browser.close()

if __name__ == "__main__":
    run_final_flow()
