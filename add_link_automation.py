"""
Automation script to add a link in the Appsha application
This script performs the following actions:
1. Opens the links page
2. Clicks on "Add Link" button
3. Fills in the link details (title, URL)
4. Selects an icon
5. Saves the link
"""

from playwright.sync_api import sync_playwright
import time

def automate_add_link():
    """Main automation function"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to True for headless mode
        page = browser.new_page()
        
        try:
            # Step 1: Navigate to the links page
            print("Navigating to the staging application...")
            page.goto("https://staging.appsha.com/u/profiles/zubdkqm/links")
            page.wait_for_load_state("networkidle")
            
            # Step 2: Click on the "Add Link" button using the CSS selector
            print("Clicking on 'Add Link' button...")
            add_link_selector = "#links > div > div.flex.h-\\[60px\\].items-center.justify-between > div.flex.flex-shrink-0.items-center > a"
            page.click(add_link_selector)
            page.wait_for_load_state("networkidle")
            
            # Verify navigation to add-link page
            print(f"Current URL: {page.url}")
            assert "add-link" in page.url, "Failed to navigate to add-link page"
            
            # Step 3: Click on the form button (XPath)
            print("Clicking on form button...")
            form_button_xpath = "/html/body/div[2]/main/div/div[2]/div/div[1]/div[2]/button[1]"
            page.locator(f"xpath={form_button_xpath}").click()
            time.sleep(1)
            
            # Step 4: Fill in the title field
            print("Filling in the title...")
            title_xpath = "//*[@id=\"_r_h8_-form-item\"]"
            page.locator(f"xpath={title_xpath}").fill("hello")
            
            # Step 5: Fill in the URL field
            print("Filling in the URL...")
            url_xpath = "//*[@id=\"_r_h9_-form-item\"]"
            page.locator(f"xpath={url_xpath}").fill("www.appsha.com")
            
            # Step 6: Choose icon
            print("Clicking on icon selector...")
            icon_xpath = "//*[@id=\"radix-_r_h7_\"]/div/div/div/div/div[3]/div/div/div/div/div/div/div[2]/img"
            page.locator(f"xpath={icon_xpath}").click()
            time.sleep(1)
            
            # Step 7: Save the link
            print("Clicking on save button...")
            save_button_xpath = "/html/body/div[2]/main/div/div[2]/div/form/div[3]/button[2]"
            page.locator(f"xpath={save_button_xpath}").click()
            page.wait_for_load_state("networkidle")
            
            print("Link added successfully!")
            print(f"Final URL: {page.url}")
            
            # Wait a moment to see the result
            time.sleep(2)
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            # Take a screenshot for debugging
            page.screenshot(path="error_screenshot.png")
            raise
        finally:
            browser.close()

if __name__ == "__main__":
    automate_add_link()
