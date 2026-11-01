# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Default branding for OSDuo Business Connect.

Every brand asset (logo, mark, favicon, login panel) ships inside this app and
is served from ``/assets/osduo_business_connect/...``. This module applies
those bundled defaults to Frappe's per-site settings so no deployment ever has
to copy logo files into ``sites/<site>/public/files`` by hand.

Called from ``after_install`` and ``after_migrate``; can also be run on demand:

    bench --site <site> execute osduo_business_connect.branding.apply_branding_settings
"""

from urllib.parse import unquote, urlparse

import frappe

from osduo_business_connect.hooks import OSDUO_BRANDING

APP_IMAGE_PREFIX = "/assets/osduo_business_connect/images/"
SITE_FILE_PREFIX = "/files/"

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


def apply_branding_settings():
    """Apply bundled brand defaults to Website Settings and System Settings.

    Safe to call repeatedly (install, migrate, or manually):
    - fills empty or generic values,
    - replaces legacy ``/files/`` (or full-resolution asset) copies of the
      brand logo/favicon with the bundled asset paths,
    - leaves genuine per-site custom logos/names untouched.

    Returns a dict describing which settings were changed.
    """
    changed = {"website_settings": False, "system_settings": False}

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

        if changed["website_settings"]:
            website_settings.save(ignore_permissions=True)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(), "OSDuo branding: Website Settings"
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
