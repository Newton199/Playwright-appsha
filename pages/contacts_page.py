"""
ContactsPage — page object for the Appsha profile contacts section.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from playwright.sync_api import Locator, Page

import appsha_selectors as S

_PROFILE_ID = os.environ.get("APPSHA_PROFILE_ID", "vfchxswq")
CONTACTS_URL = f"https://staging.appsha.com/u/profiles/{_PROFILE_ID}/contacts"


@dataclass
class ContactData:
    """Field values for a single contact record."""
    name: str
    email: str = ""
    phone: str = ""
    address: str = ""
    birthday: str = ""
    anniversary: str = ""
    note: str = ""
    tags: list[str] = field(default_factory=list)


class ContactsPage:
    """All interactions on the Appsha profile contacts page."""

    def __init__(self, page: Page) -> None:
        self.page = page

    # ------------------------------------------------------------------ #
    # Navigation                                                           #
    # ------------------------------------------------------------------ #

    def navigate(self) -> None:
        """Go directly to the contacts URL if not already there."""
        if CONTACTS_URL not in self.page.url:
            self.page.goto(CONTACTS_URL, wait_until="networkidle")
            self.page.wait_for_url("**/contacts", timeout=15_000)
        
        # Ensure toolbar is present and visible
        toolbar = self.page.locator(S.CONTACT_TOOLBAR).first
        toolbar.wait_for(state="visible", timeout=15_000)

    def navigate_via_tab(self) -> None:
        """Click the Contacts tab inside the profile tab bar."""
        tab = self.page.locator(S.CONTACTS_TAB).first
        tab.wait_for(state="visible", timeout=10_000)
        tab.click()
        self.page.wait_for_url("**/contacts", timeout=15_000)
        self.page.wait_for_load_state("networkidle")

    # ------------------------------------------------------------------ #
    # Low-level locators                                                   #
    # ------------------------------------------------------------------ #

    def _add_btn(self) -> Locator:
        """Primary 'Add Contact' button (blue bg-primary button)."""
        return self.page.locator(S.CONTACT_ADD_BTN).first

    def _filter_btn(self) -> Locator:
        """Filter button (bordered white button next to Add Contact)."""
        return self.page.locator(S.CONTACT_FILTER_BTN).first

    def _table_rows(self) -> Locator:
        """All data rows in the contacts table (excludes header)."""
        return self.page.locator(S.CONTACT_LIST_ROWS)

    def _wait_for_loading_dismiss(self) -> None:
        """Wait for the '#Loading...' text/shimmer to disappear if present."""
        try:
            loading = self.page.locator("text=Loading", has_text="Loading").first
            if loading.is_visible(timeout=1_000):
                loading.wait_for(state="hidden", timeout=10_000)
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    # CREATE                                                               #
    # ------------------------------------------------------------------ #

    def open_add_form(self) -> None:
        """
        Click the Add Contact button.
        """
        btn = self._add_btn()
        btn.scroll_into_view_if_needed()
        btn.wait_for(state="visible", timeout=10_000)
        btn.click(force=True)
        # The name field is inside a Radix Sheet
        name_loc = self.page.locator(S.CONTACT_NAME_FIELD).first
        name_loc.wait_for(state="visible", timeout=15_000)

    def fill_contact_form(self, data: ContactData) -> None:
        """Fill ALL form fields."""
        self._wait_for_loading_dismiss()

        # Name
        self.page.locator(S.CONTACT_NAME_FIELD).first.fill(data.name)

        # Email
        if data.email:
            self.page.locator(S.CONTACT_EMAIL_FIELD).first.fill(data.email)

        # Phone
        if data.phone:
            # Clicking the input first to ensure focus
            phone_input = self.page.locator(S.CONTACT_PHONE_FIELD).first
            phone_input.click()
            phone_input.fill(data.phone)

        # Address
        if data.address:
            self.page.locator(S.CONTACT_ADDRESS_FIELD).first.fill(data.address)

        # Birthday & Anniversary
        if data.birthday:
            self.page.locator(S.CONTACT_BIRTHDAY_FIELD).first.fill(data.birthday)

        # Anniversary
        if data.anniversary:
            self.page.locator(S.CONTACT_ANNIVERSARY_FIELD).first.fill(data.anniversary)

        # Note / Notes
        if data.note:
            self.page.locator(S.CONTACT_NOTE_FIELD).first.fill(data.note)

        # Tags - handle react-select
        if data.tags:
            tag_field = self.page.locator(S.CONTACT_TAG_FIELD).first
            for tag in data.tags:
                tag_field.fill(tag)
                self.page.keyboard.press("Enter")

    def submit_form(self) -> None:
        """Click the Save / Create button and wait for form to close."""
        btn = self.page.locator(S.CONTACT_SAVE_BTN).first
        btn.wait_for(state="visible", timeout=8_000)
        
        # Click the Save button using Javascript to ensure it triggers
        btn.evaluate("el => el.click()")
        
        try:
            # Wait for the dialog to disappear
            self.page.locator("div[role='dialog']").wait_for(state="hidden", timeout=15_000)
        except Exception:
            # Final attempt: press Enter
            self.page.keyboard.press("Enter")
            try:
                self.page.locator("div[role='dialog']").wait_for(state="hidden", timeout=10_000)
            except:
                pass
        self.page.wait_for_load_state("networkidle")

    def create_contact(self, data: ContactData) -> None:
        """Full create flow: open form → fill fields → submit."""
        self.open_add_form()
        self.fill_contact_form(data)
        self.submit_form()

    # ------------------------------------------------------------------ #
    # READ                                                                 #
    # ------------------------------------------------------------------ #

    def row_count(self) -> int:
        """Number of visible data rows in the contacts table."""
        rows = self._table_rows()
        try:
            rows.first.wait_for(state="visible", timeout=8_000)
        except Exception:
            return 0
        return rows.count()

    def contact_row_count(self) -> int:
        """Alias for row_count() — used by test_full_flow.py."""
        return self.row_count()

    def is_empty(self) -> bool:
        """Return True when the contacts list shows an empty-state or zero rows."""
        empty = self.page.locator(S.CONTACT_EMPTY_STATE).first
        if empty.is_visible():
            return True
        return self.row_count() == 0

    def find_row(self, name: str) -> Locator:
        """Return the first table row containing *name*."""
        return self._table_rows().filter(has_text=name).first

    def contact_exists(self, name: str) -> bool:
        """Return True if a row containing *name* is visible."""
        return self.find_row(name).is_visible()

    def search(self, query: str) -> None:
        """
        Type into the search box.
        """
        field = self.page.locator(S.CONTACT_SEARCH_FIELD).first
        field.wait_for(state="attached", timeout=8_000)
        field.fill(query, force=True)
        self.page.wait_for_load_state("networkidle")

    def clear_search(self) -> None:
        """Clear the search box."""
        field = self.page.locator(S.CONTACT_SEARCH_FIELD).first
        if field.count() > 0:
            field.fill("", force=True)
            self.page.wait_for_load_state("networkidle")

    # ------------------------------------------------------------------ #
    # UPDATE                                                               #
    # ------------------------------------------------------------------ #

    def open_edit_form(self, name: str) -> None:
        """
        Open the edit sheet for the contact named *name*.
        """
        # Find the row containing the name
        row = self.page.locator("tr", has_text=name).first
        row.scroll_into_view_if_needed()
        row.wait_for(state="visible", timeout=10_000)
        
        # Click the arrow navigation at the end of the row
        row.locator(S.CONTACT_ROW_NAV).first.click()

        # Click the Edit option (first item in the resulting Radix menu)
        self.page.locator("div[role='menuitem']:has-text('Edit'), button:has-text('Edit')").first.click()

        # Ensure the dialog/sheet is open by waiting for the name field
        self.page.locator(S.CONTACT_NAME_FIELD).first.wait_for(
            state="visible", timeout=15_000
        )

    def update_contact(self, original_name: str, new_data: ContactData) -> None:
        """Full update flow: open edit sheet → fill → submit."""
        self.open_edit_form(original_name)
        self.fill_contact_form(new_data)
        self.submit_form()

    # ------------------------------------------------------------------ #
    # DELETE                                                               #
    # ------------------------------------------------------------------ #

    def delete_contact(self, name: str) -> None:
        """
        Delete the contact row matching *name*.
        """
        row = self.page.locator("tr", has_text=name).first
        row.scroll_into_view_if_needed()
        row.wait_for(state="visible", timeout=10_000)
        
        # Click the arrow navigation
        row.locator(S.CONTACT_ROW_NAV).first.click()

        # Click the red Delete option
        del_btn = self.page.locator(S.CONTACT_DELETE_BTN).first
        del_btn.click()

        confirm = self.page.locator(S.CONTACT_DELETE_CONFIRM).first
        if confirm.is_visible(timeout=5_000):
            confirm.click()

        self.page.wait_for_load_state("networkidle")

    # ------------------------------------------------------------------ #
    # FILTER PANEL                                                         #
    # ------------------------------------------------------------------ #

    def open_filter_panel(self) -> None:
        """
        Click the filter button.
        """
        btn = self._filter_btn()
        btn.wait_for(state="visible", timeout=10_000)
        btn.click()
        self.page.locator(S.CONTACT_FILTER_PANEL).first.wait_for(
            state="visible", timeout=8_000
        )

    def filter_by_tag(self, tag: str) -> None:
        """
        Open the tag dropdown inside the filter panel and select *tag*.
        """
        trigger = self.page.locator(S.CONTACT_FILTER_TAGS_TRIGGER).first
        trigger.wait_for(state="visible", timeout=8_000)
        trigger.click()

        tag_option = self.page.locator(
            f"[role='option']:has-text('{tag}'), "
            f"[role='listitem']:has-text('{tag}'), "
            f"li:has-text('{tag}')"
        ).first
        tag_option.wait_for(state="visible", timeout=6_000)
        tag_option.click()
        self.page.keyboard.press("Escape")

    def deselect_tag(self, tag: str) -> None:
        """Deselect a previously selected tag filter option."""
        trigger = self.page.locator(S.CONTACT_FILTER_TAGS_TRIGGER).first
        if trigger.is_visible():
            trigger.click()
            tag_option = self.page.locator(
                f"[role='option'][aria-selected='true']:has-text('{tag}'), "
                f"[role='option'].selected:has-text('{tag}')"
            ).first
            if tag_option.is_visible():
                tag_option.click()
            self.page.keyboard.press("Escape")

    def get_column_checkboxes(self) -> list[Locator]:
        """Return a list of all column-visibility checkboxes in the filter panel."""
        return self.page.locator(S.CONTACT_COLUMN_CHECKBOX).all()

    def toggle_column(self, index: int = 0) -> None:
        """Toggle the checkbox at *index* in the column-visibility list."""
        checkboxes = self.get_column_checkboxes()
        if index < len(checkboxes):
            checkboxes[index].click()

    def apply_filters(self) -> None:
        """Click Apply / Done inside the filter panel."""
        apply_btn = self.page.locator(S.CONTACT_FILTER_APPLY).first
        if apply_btn.is_visible():
            apply_btn.click()
        else:
            self.page.keyboard.press("Escape")
        self.page.wait_for_load_state("networkidle")

    def close_filter_panel(self) -> None:
        """Dismiss the filter panel by pressing Escape."""
        self.page.keyboard.press("Escape")
        self.page.wait_for_load_state("networkidle")

    # ------------------------------------------------------------------ #
    # PAGINATION                                                           #
    # ------------------------------------------------------------------ #

    def has_next_page(self) -> bool:
        """Return True if the Next page button is visible and enabled."""
        btn = self.page.locator(S.CONTACT_PAGINATION_NEXT).first
        return btn.is_visible() and btn.is_enabled()

    def has_prev_page(self) -> bool:
        """Return True if the Previous page button is visible and enabled."""
        btn = self.page.locator(S.CONTACT_PAGINATION_PREV).first
        return btn.is_visible() and btn.is_enabled()

    def go_next_page(self) -> None:
        """Click Next page and wait for the table to update."""
        btn = self.page.locator(S.CONTACT_PAGINATION_NEXT).first
        btn.wait_for(state="visible", timeout=6_000)
        btn.click()
        self.page.wait_for_load_state("networkidle")

    def go_prev_page(self) -> None:
        """Click Previous page and wait for the table to update."""
        btn = self.page.locator(S.CONTACT_PAGINATION_PREV).first
        btn.wait_for(state="visible", timeout=6_000)
        btn.click()
        self.page.wait_for_load_state("networkidle")

    def pagination_info_text(self) -> str:
        """Return the pagination info text if present."""
        info = self.page.locator(S.CONTACT_PAGINATION_INFO).first
        return info.inner_text() if info.is_visible() else ""

    # ------------------------------------------------------------------ #
    # Assertion helpers                                                    #
    # ------------------------------------------------------------------ #

    def assert_on_contacts_page(self) -> None:
        assert "contacts" in self.page.url, (
            f"Expected URL to contain 'contacts', got: {self.page.url}"
        )

    def assert_contact_visible(self, name: str) -> None:
        assert self.contact_exists(name), (
            f"Contact '{name}' should be visible in the contacts table"
        )

    def assert_contact_not_visible(self, name: str) -> None:
        assert not self.contact_exists(name), (
            f"Contact '{name}' should NOT be visible after deletion"
        )

    def assert_row_count_gte(self, minimum: int) -> None:
        count = self.row_count()
        assert count >= minimum, (
            f"Expected at least {minimum} contact row(s), found {count}"
        )
