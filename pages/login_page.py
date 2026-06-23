"""
LoginPage page object for the Appsha staging site.

Encapsulates all interactions with the login page at
https://staging.appsha.com/login, including navigation, credential entry,
form submission, and post-login URL verification.

No time.sleep() calls are used — all waits are expressed via Playwright APIs.
"""

from playwright.sync_api import Page

from appsha_selectors import EMAIL_FIELD, PASSWORD_FIELD


class LoginPage:
    """Page object for the Appsha login page."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def navigate(self) -> None:
        """Navigate to the login page and wait for the DOM to be ready."""
        self.page.goto("https://staging.appsha.com/login")
        self.page.wait_for_load_state("domcontentloaded")

    def fill_email(self, email: str) -> None:
        """Wait for the email field to be visible, then fill it."""
        email_locator = self.page.locator(EMAIL_FIELD)
        email_locator.wait_for(state="visible")
        email_locator.fill(email)

    def fill_password(self, password: str) -> None:
        """Wait for the password field to be visible, then fill it."""
        password_locator = self.page.locator(PASSWORD_FIELD)
        password_locator.wait_for(state="visible")
        password_locator.fill(password)

    def submit(self) -> None:
        """Wait for the submit button to be visible, then click it."""
        submit_locator = self.page.locator("button[type='submit']")
        submit_locator.wait_for(state="visible")
        submit_locator.click()

    def expect_authenticated(self) -> None:
        """Wait for the post-login redirect to /u and assert the URL."""
        self.page.wait_for_url("**/u", timeout=15000)
        assert "/u" in self.page.url, (
            f"Expected URL to contain '/u' after login, got: {self.page.url}"
        )

    def login(self, email: str, password: str) -> None:
        """Perform a full login: navigate, fill credentials, submit, and verify."""
        self.navigate()
        self.fill_email(email)
        self.fill_password(password)
        self.submit()
        self.expect_authenticated()
