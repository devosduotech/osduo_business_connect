# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Canonical URL helpers.

Public URLs (card and business) are frozen into printed QR codes and NFC
taps, so they must be derived from the site's canonical base URL — never from
the host of the current request. Otherwise saving a card through a custom
domain would silently change the URL encoded on already-printed material.

The canonical base is controlled, in order of precedence:

1. ``host_name`` in ``site_config.json`` (recommended for production/BYOD)
2. SSL/wildcard configuration + the site name (bench default)
3. ``Website Settings → Subdomain`` as a last resort

See docs/PWA.md for setup notes.
"""

import frappe


def get_canonical_base_url():
    """Return the site's canonical base URL without a trailing slash."""
    url = frappe.utils.get_url(allow_header_override=False) or ""
    return url.rstrip("/")


def get_business_public_url(slug):
    if not slug:
        return None
    return f"{get_canonical_base_url()}/b/{slug}"


def get_card_public_url(slug):
    if not slug:
        return None
    return f"{get_canonical_base_url()}/c/{slug}"
