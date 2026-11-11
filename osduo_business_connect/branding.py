# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Default branding for OSDuo Business Connect.

Every brand asset (logo, mark, favicon, login panel) ships inside this app and
is served from ``/assets/osduo_business_connect/...``. This module applies
those bundled defaults to Frappe's per-site settings so no deployment ever has
to copy logo files into ``sites/<site>/public/files`` by hand. It also creates
the bundled Website Theme (``OSDuo Business Connect``) when missing and selects
it for sites that have not chosen a theme yet.

Called from ``after_install`` and ``after_migrate``; can also be run on demand:

    bench --site <site> execute osduo_business_connect.branding.apply_branding_settings
"""

from urllib.parse import unquote, urlparse

import frappe

from osduo_business_connect.hooks import OSDUO_BRANDING

APP_IMAGE_PREFIX = "/assets/osduo_business_connect/images/"
SITE_FILE_PREFIX = "/files/"

# Name of the Website Theme shipped with the app. Existing records with this
# name are never modified: a site that has customised the theme keeps its
# customisations and only gets it selected as the default.
WEBSITE_THEME_NAME = "OSDuo Business Connect"

# Website Theme colour fields are Links to the "Color" doctype. Each entry is
# (fieldname, Color record name, hex value). The record name is stable so
# repeated installs/migrations reuse the same Color rows.
_THEME_COLORS = (
    ("primary_color", "OSDuo Primary Blue", OSDUO_BRANDING["primary_color"]),
    ("text_color", "OSDuo Text", OSDUO_BRANDING["text_color"]),
    ("dark_color", "OSDuo Dark Blue", "#062653"),
    ("light_color", "OSDuo Light", OSDUO_BRANDING["background_color"]),
    ("background_color", "OSDuo Background", OSDUO_BRANDING["background_color"]),
)

# Extra rules compiled into the theme after Frappe's own website styles. Kept
# intentionally small: Bootstrap variables (primary/text/background colours)
# already come from the fields above. Avoid external font imports so sites
# stay fast and work offline.
_DEFAULT_THEME_SCSS = """
/* OSDuo Business Connect - bundled website theme */
:root {
    --osduo-primary: #0B3D91;
    --osduo-secondary: #1677FF;
    --osduo-accent: #00C49A;
    --osduo-ink: #333333;
    --osduo-surface: #F4F6F8;
}

body {
    color: var(--osduo-ink);
}

a {
    color: var(--osduo-primary);
}

a:hover,
a:focus {
    color: var(--osduo-secondary);
}

.btn-primary {
    --bs-btn-bg: var(--osduo-primary);
    --bs-btn-border-color: var(--osduo-primary);
    --bs-btn-hover-bg: var(--osduo-secondary);
    --bs-btn-hover-border-color: var(--osduo-secondary);
    --bs-btn-active-bg: var(--osduo-primary);
}

.web-footer {
    background-color: var(--osduo-primary);
    color: #ffffff;
}

.web-footer a {
    color: #ffffff;
}

.page-card {
    border-radius: 12px;
    box-shadow: 0 4px 24px rgba(11, 61, 145, 0.08);
}
""".strip()

# Normalised filenames that were historically copied into a site's
# public/files folder (or used as full-resolution app assets). These are safe
# to replace with the bundled, optimised asset paths. Normalisation strips
# spaces, underscores and hyphens, so "logo_mark_512x512" -> "logomark512x512".
_LEGACY_BRAND_STEMS = {
    "logo",
    "logomark",
    "logodark",
    "logowhite",
    "favicon",
}

# Optimised derivatives we ship ourselves — never treat these as "legacy".
_OPTIMIZED_ASSETS = {
    "logo512",
    "logodark512",
    "logomark128",
    "logomark512",
    "favicon256",
}


def _is_legacy_brand_copy(url):
    """True when ``url`` points at a hand-copied brand asset we should replace.

    Deliberately narrow: a customer's own upload such as
    ``/files/my-business-logo.png`` is left untouched. Only unambiguous OSDuo
    brand filenames (``logo.png``, ``logo_mark_512x512.png``, …) are replaced.
    """
    if not url:
        return False

    path = unquote(urlparse(str(url)).path)
    if not (path.startswith(SITE_FILE_PREFIX) or path.startswith(APP_IMAGE_PREFIX)):
        return False

    stem = path.rsplit("/", 1)[-1].lower().rsplit(".", 1)[0]
    compact = stem.replace(" ", "").replace("_", "").replace("-", "")

    if compact in _OPTIMIZED_ASSETS:
        return False
    if compact in _LEGACY_BRAND_STEMS:
        return True
    if compact.startswith(("logomark", "logodark", "logowhite")):
        return True

    # e.g. "OSDuo Business Connect Logo.png" / "osduo-business-connect-logo"
    return "logo" in compact and (
        "osduo" in compact or "businessconnect" in compact
    )


def _preferred(current, bundled):
    """Keep deliberate customisation; replace empty or hand-copied defaults."""
    current = (current or "").strip()
    if not current or _is_legacy_brand_copy(current):
        return bundled
    return current


def _is_generic_name(value):
    return (value or "").strip().lower() in ("", "frappe", "frappe technologies")


def _set_if_changed(doc, field, value):
    if getattr(doc, field, None) != value:
        setattr(doc, field, value)
        return True
    return False


def _is_default_theme_slot(value):
    """True when no deliberate theme has been chosen for the site."""
    return (value or "").strip() in ("", "Standard")


def _default_robots_txt():
    """Return the bundled ``robots.txt`` crawl rules.

    Applied only when ``Website Settings.robots_txt`` is empty, so an
    administrator's custom robots file is never overwritten. The ``Sitemap:``
    line is **not** stored here: ``/robots.txt`` is rendered dynamically by
    ``www/robots.py`` and appends the correct sitemap URL for whichever host
    served the request, so a frozen or wrong-host declaration can never leak.
    """
    from osduo_business_connect.seo.robots import DEFAULT_ROBOTS_RULES

    return "\n".join(DEFAULT_ROBOTS_RULES) + "\n"


def _get_or_create_color(name, value):
    """Return a ``Color`` record name, creating it once if needed.

    Existing records are left untouched: a different value with the same name
    may already be referenced elsewhere, so silently rewriting it would change
    other themes.
    """
    if frappe.db.exists("Color", name):
        return name

    frappe.get_doc(
        {
            "doctype": "Color",
            "__newname": name,
            "color": value,
        }
    ).insert(ignore_permissions=True)
    return name


def ensure_default_website_theme():
    """Create the bundled Website Theme if the site does not have it yet.

    Returns ``(theme_doc, created)``. An existing theme with
    :data:`WEBSITE_THEME_NAME` is returned as-is so per-site customisations
    survive migrations.
    """
    if frappe.db.exists("Website Theme", WEBSITE_THEME_NAME):
        return frappe.get_doc("Website Theme", WEBSITE_THEME_NAME), False

    theme = frappe.get_doc(
        {
            "doctype": "Website Theme",
            "theme": WEBSITE_THEME_NAME,
            "module": "Website",
            "custom": 1,
            "button_rounded_corners": 1,
            "button_shadows": 0,
            "button_gradients": 0,
            "custom_scss": _DEFAULT_THEME_SCSS,
        }
    )
    for fieldname, color_name, value in _THEME_COLORS:
        setattr(theme, fieldname, _get_or_create_color(color_name, value))

    # Creating a custom theme compiles SCSS with Node and shows a "Compiled
    # Successfully" message. That is noise during install/migrate.
    mute_messages = getattr(frappe.flags, "mute_messages", False)
    frappe.flags.mute_messages = True
    try:
        theme.insert(ignore_permissions=True)
    finally:
        frappe.flags.mute_messages = mute_messages

    return theme, True


def apply_branding_settings():
    """Apply bundled brand defaults to Website Settings and System Settings.

    Safe to call repeatedly (install, migrate, or manually):
    - fills empty or generic values,
    - replaces legacy ``/files/`` (or full-resolution asset) copies of the
      brand logo/favicon with the bundled asset paths,
    - creates the bundled Website Theme when it is missing and selects it when
      the site has not chosen a theme yet,
    - leaves genuine per-site custom logos/names/themes untouched.

    Returns a dict describing which settings were changed.
    """
    changed = {
        "website_settings": False,
        "system_settings": False,
        "website_theme": False,
    }

    website_settings = None
    try:
        website_settings = frappe.get_single("Website Settings")
        changed["website_settings"] |= _set_if_changed(
            website_settings,
            "favicon",
            _preferred(website_settings.favicon, OSDUO_BRANDING["favicon"]),
        )
        changed["website_settings"] |= _set_if_changed(
            website_settings,
            "app_logo",
            _preferred(website_settings.app_logo, OSDUO_BRANDING["logo_mark"]),
        )
        if _is_generic_name(website_settings.app_name):
            changed["website_settings"] |= _set_if_changed(
                website_settings, "app_name", OSDUO_BRANDING["app_name"]
            )
        # Non-destructive: only fill robots.txt when the site has not set one.
        # This seeds the crawl rules only — the Sitemap line itself is added per
        # request by www/robots.py (see seo/robots.py), so no host-specific URL
        # is ever stored here. We do not push to Google; crawlers discover the
        # sitemap through robots.txt and recrawl on their own.
        if not (website_settings.robots_txt or "").strip():
            changed["website_settings"] |= _set_if_changed(
                website_settings, "robots_txt", _default_robots_txt()
            )
    except Exception:
        frappe.log_error(
            frappe.get_traceback(), "OSDuo branding: Website Settings"
        )

    theme_available = False
    try:
        _, created = ensure_default_website_theme()
        changed["website_theme"] = created
        theme_available = True
    except Exception:
        frappe.log_error(frappe.get_traceback(), "OSDuo branding: Website Theme")

    if website_settings is not None:
        try:
            # Only adopt the bundled theme when the site has no deliberate
            # choice. A site using another theme (or a customised version of
            # ours) keeps it.
            if theme_available and _is_default_theme_slot(
                website_settings.website_theme
            ):
                changed["website_settings"] |= _set_if_changed(
                    website_settings, "website_theme", WEBSITE_THEME_NAME
                )

            if changed["website_settings"]:
                website_settings.save(ignore_permissions=True)
        except Exception:
            frappe.log_error(
                frappe.get_traceback(), "OSDuo branding: Website Settings save"
            )

    try:
        system_settings = frappe.get_single("System Settings")
        if _is_generic_name(system_settings.app_name):
            changed["system_settings"] |= _set_if_changed(
                system_settings, "app_name", OSDUO_BRANDING["app_name"]
            )

        if changed["system_settings"]:
            system_settings.save(ignore_permissions=True)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(), "OSDuo branding: System Settings"
        )

    return changed
