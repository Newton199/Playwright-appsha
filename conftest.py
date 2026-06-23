"""
conftest.py — shared pytest fixtures for the Appsha Playwright automation suite.

Provides:
  - playwright_instance: session-scoped SyncPlaywright context manager
  - browser_page: a session-scoped Playwright Page (Chromium, headless=False)
  - authenticated_page: a session-scoped page that has already logged in
  - unauthenticated_page: a function-scoped fresh page using the same browser

Credentials are loaded from environment variables APPSHA_EMAIL and
APPSHA_PASSWORD, with fallback support for a .env file via python-dotenv.
"""

from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from pages.login_page import LoginPage

# Load .env if present; environment variables already set take precedence.
load_dotenv()

_EMAIL = os.environ.get("APPSHA_EMAIL", "newton.appsha@gmail.com")
_PASSWORD = os.environ.get("APPSHA_PASSWORD", "Newton@#26")


# ---------------------------------------------------------------------------
# Session-scoped browser
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def session_browser():
    """Launch a headless Chromium browser for the entire test session."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture(scope="session")
def browser_page(session_browser: Browser) -> Page:  # type: ignore[misc]
    """Open a single Page in the session browser."""
    context: BrowserContext = session_browser.new_context(
        viewport={"width": 1280, "height": 900}
    )
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture(scope="session")
def authenticated_page(browser_page: Page) -> Page:
    """Return a Page that has already completed the login flow.

    Reuses the session-scoped browser_page so login runs only once
    per test session.
    """
    login = LoginPage(browser_page)
    login.login(_EMAIL, _PASSWORD)
    return browser_page


# ---------------------------------------------------------------------------
# Function-scoped unauthenticated page (for login-specific tests)
# Re-uses the session browser to avoid spawning a new sync_playwright context.
# ---------------------------------------------------------------------------


@pytest.fixture()
def unauthenticated_page(session_browser: Browser) -> Page:  # type: ignore[misc]
    """Open a fresh Chromium page for tests that need a clean, unauthenticated session."""
    context: BrowserContext = session_browser.new_context(
        viewport={"width": 1280, "height": 900}
    )
    page = context.new_page()
    yield page
    context.close()
