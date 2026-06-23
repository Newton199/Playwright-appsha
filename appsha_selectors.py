# Centralized CSS selector constants for Appsha Playwright automation suite

# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
EMAIL_FIELD = "input[type='email'], input[id*='R_qan'], [id$='-form-item'] input[type='email'], #login-form input[type='email']"
PASSWORD_FIELD = "input[type='password'], input[id*='R_1aa'], [id$='-form-item'] input[type='password']"

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
SIDEBAR_LINKS = (
    "body > div.group\\/sidebar-wrapper.flex.min-h-svh.has-\\[\\[data-variant\\=inset\\]\\]\\:bg-sidebar.w-full"
    " > div"
    " > div.fixed.inset-y-0.z-10.hidden.h-svh.w-\\[--sidebar-width\\].\\!bg-background.md\\:flex"
    ".max-\\[1024px\\]\\:w-\\[--sidebar-width-sm\\].left-0"
    ".group-data-\\[collapsible\\=offcanvas\\]\\:left-\\[calc\\(var\\(--sidebar-width\\)\\*-1\\)\\]"
    ".group-data-\\[collapsible\\=icon\\]\\:w-\\[--sidebar-width-icon\\]"
    ".group-data-\\[side\\=left\\]\\:border-r.group-data-\\[side\\=right\\]\\:border-l"
    ".select-none.\\!border-r-\\[0\\.5px\\].border-\\[\\#C5C5C5\\].bg-\\[\\#F5F5F5\\]"
    ".px-5.py-4.lg\\:px-6.lg\\:py-6.transition-\\[width\\,padding\\].duration-300.ease-in-out.my-0"
    " > div"
    " > div.no-scrollbar.flex.min-h-0.flex-1.flex-col.gap-3.overflow-auto"
    ".group-data-\\[collapsible\\=icon\\]\\:overflow-hidden"
    " > div:nth-child(1) > div:nth-child(1) > a > div"
)

# ---------------------------------------------------------------------------
# Profile tab bar (Links / Appearance / Contacts)
# ---------------------------------------------------------------------------
# Use Radix UI tab role — the actual tab buttons have role="tab"
LINKS_TAB      = "[role='tab']:has-text('Links')"
APPEARANCE_TAB = "[role='tab']:has-text('Appearance'), a:has-text('Appearance'), button:has-text('Appearance')"
CONTACTS_TAB   = "[role='tab']:has-text('Contacts'), a:has-text('Contacts'), button:has-text('Contacts')"

# Add Link button
ADD_LINK_BTN = "#links a:has(img), #links [href*='add-link'] img, a[href*='add-link'] img"

# ---------------------------------------------------------------------------
# Add-link feature cards
# ---------------------------------------------------------------------------
FEATURE_SELECTORS: dict[str, str] = {
    "normal_link":   "div.flex.flex-col.gap-1:has-text('Link')",
    "embed_link":    "div.flex.flex-col.gap-1:has-text('HTML Embed')",
    "attachment":    "div.flex.flex-col.gap-1:has-text('Attachment')",
    "external_shop": "div.flex.flex-col.gap-1:has-text('External Shop')",
    "highlight":     "div.flex.flex-col.gap-1:has-text('Highlight')",
    "analytics":     "div.flex.flex-col.gap-1:has-text('Analytics')",
}

UPGRADE_PROMPT_SELECTORS: dict[str, str] = {
    "normal_link":   "div:has(> div.flex.flex-col.gap-1:has-text('Link')) span:has-text('Pro')",
    "embed_link":    "div:has(> div.flex.flex-col.gap-1:has-text('HTML Embed')) span:has-text('Pro')",
    "attachment":    "div:has(> div.flex.flex-col.gap-1:has-text('Attachment')) span:has-text('Pro')",
    "external_shop": "div:has(> div.flex.flex-col.gap-1:has-text('External Shop')) span:has-text('Pro')",
    "highlight":     "div:has(> div.flex.flex-col.gap-1:has-text('Highlight')) span:has-text('Pro')",
    "analytics":     "div:has(> div.flex.flex-col.gap-1:has-text('Analytics')) span:has-text('Pro')",
}

# ---------------------------------------------------------------------------
# Appearance page  (https://staging.appsha.com/u/profiles/{id}/appearance)
# ---------------------------------------------------------------------------

# Theme grid — each theme card has a radio input or clickable tile
APPEARANCE_THEME_CARDS   = "[data-testid='theme-card'], .theme-card, [aria-label*='theme'], label:has(input[name*='theme'])"
APPEARANCE_THEME_RADIO   = "input[name*='theme'], input[type='radio'][value*='theme']"

# Free themes — available to all plans (select-only, no customisation)
APPEARANCE_FREE_THEME    = "label:has-text('Default'), label:has-text('Classic'), [data-theme='default'], [data-theme='classic']"

# Pro theme tile (locked for non-Pro+ users)
APPEARANCE_PRO_THEME     = "[data-theme='pro'], label:has-text('Pro'), [data-testid='theme-pro']"
APPEARANCE_PRO_LOCK      = "[data-testid='pro-lock'], .lock, svg[aria-label*='lock'], [aria-label*='Pro only'], text='Pro+'"

# Customize panel — only unlocked for Pro+
APPEARANCE_CUSTOMIZE_BTN = "button:has-text('Customize'), a:has-text('Customize'), [data-testid='customize-btn']"
APPEARANCE_CUSTOMIZE_PANEL = "[data-testid='customize-panel'], .customize-panel, [aria-label*='customize']"

# Background / button colour pickers inside the Customize panel
APPEARANCE_BG_COLOR      = "[data-testid='bg-color'], input[type='color'][name*='bg'], input[aria-label*='background']"
APPEARANCE_BTN_COLOR     = "[data-testid='btn-color'], input[type='color'][name*='button'], input[aria-label*='button color']"

# Font selector
APPEARANCE_FONT_SELECT   = "select[name*='font'], [data-testid='font-select'], [aria-label*='font']"

# Save / Apply button inside the appearance editor
APPEARANCE_SAVE_BTN      = "button:has-text('Save'), button:has-text('Apply'), button[type='submit']:visible"

# ---------------------------------------------------------------------------
# Contacts page  (https://staging.appsha.com/u/profiles/{id}/contacts)
# ---------------------------------------------------------------------------

# The contacts toolbar header area that holds both action buttons.
CONTACT_TOOLBAR = "div.flex.w-full.items-center.justify-end"

# "Add Contact" primary button — the blue "+" button on the far right.
CONTACT_ADD_BTN = "button.bg-primary:has(svg):not(:has-text('Sync'))"

# Filter button — white button with "Filter" text
CONTACT_FILTER_BTN = "button.border.border-input.bg-white:has-text('Filter')"

# Filter/customize panel opened by the filter button
CONTACT_FILTER_PANEL = "[data-state='open'][role='dialog']:has-text('Filter'), [data-state='open'][role='dialog']:has-text('Customize')"

# Tags filter dropdown inside the filter panel
CONTACT_FILTER_TAGS_TRIGGER = "button:has-text('Tag')"

# Column visibility checkboxes inside the filter panel
CONTACT_COLUMN_CHECKBOX = "button[role='checkbox']"

# Apply / Done button inside filter panel
CONTACT_FILTER_APPLY = "button:has-text('Apply'), button:has-text('Done')"

# Contact form fields
CONTACT_NAME_FIELD  = "input[placeholder='Name']"
CONTACT_EMAIL_FIELD = "input[placeholder='Email']"
CONTACT_PHONE_FIELD = "input[type='tel']"
CONTACT_ADDRESS_FIELD = "input[placeholder='Address']"
CONTACT_NOTE_FIELD  = "textarea[placeholder='Notes']"
CONTACT_TAG_FIELD   = "input[id^='react-select-']"
CONTACT_BIRTHDAY_FIELD = "#birthday"
CONTACT_ANNIVERSARY_FIELD = "#anniversary"

# Submit / Save inside contact form
CONTACT_SAVE_BTN = "form button[type='submit'], button:has-text('Save'), button:has-text('Add')"

# Contact table rows (tbody rows, skip header)
CONTACT_LIST_ROWS = "tbody tr, [role='row']:not([role='columnheader']):not(:has([role='columnheader']))"

# Edit / view button on a contact row (three-dot menu or explicit Edit btn)
CONTACT_EDIT_BTN   = "button[aria-label*='edit'], button:has-text('Edit'), [data-testid='edit-contact'], button[aria-label*='options']"

# Delete button on a contact row or in the row's action menu
CONTACT_DELETE_BTN = "button[aria-label*='delete'], button:has-text('Delete'), button:has-text('Remove'), [data-testid='delete-contact']"

# Confirm delete dialog
CONTACT_DELETE_CONFIRM = (
    "button:has-text('Confirm'), "
    "button:has-text('Yes'), "
    "[data-testid='confirm-delete'], "
    "[role='alertdialog'] button:has-text('Delete'), "
    "[role='dialog'] button:has-text('Delete')"
)

# Search input in the contacts toolbar — the input is hidden until revealed.
# Use state="attached" in waits; force=True if needed to interact with it.
CONTACT_SEARCH_FIELD = "input[placeholder*='Search by name'], input[placeholder*='Search'], input[type='search']"

# Empty-state (no contacts yet)
CONTACT_EMPTY_STATE = "[data-testid='empty-contacts'], .empty-state, td:has-text('No'), p:has-text('No contacts')"

# Pagination controls
CONTACT_PAGINATION_NEXT = "button[aria-label*='next'], button:has-text('Next'), [data-testid='pagination-next']"
CONTACT_PAGINATION_PREV = "button[aria-label*='previous'], button:has-text('Prev'), [data-testid='pagination-prev']"
CONTACT_PAGINATION_INFO = "[data-testid='pagination-info'], .pagination-info, span:has-text('of ')"
