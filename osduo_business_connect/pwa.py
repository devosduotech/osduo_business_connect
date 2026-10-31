# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
PWA support for OSDuo Business Connect.

Provides:
- A per-site web app manifest (rendered by www/manifest.py) so every
  customer site installs under its own name, icon and theme colors.
- A dynamically generated app icon endpoint (PIL) — no binaries needed in
  the repo, and each site can override the artwork via
  Website Settings → App Logo.
"""

import frappe
from frappe.utils import cint

from osduo_business_connect.hooks import OSDUO_BRANDING
from osduo_business_connect.utils.urls import get_canonical_base_url


def _hex_to_rgb(color):
    color = (color or "#0B3D91").lstrip("#")
    if len(color) != 6:
        color = "0B3D91"
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))


def _icon_source_path():
    """Resolve the source artwork: site logo first, app branding fallback."""
    logo_url = frappe.get_website_settings("app_logo") or ""
    if logo_url.startswith("/files/") and "?" not in logo_url:
        path = frappe.get_site_path("public", logo_url.lstrip("/"))
        import os

        if os.path.isfile(path):
            return path

    return frappe.get_app_path(
        "osduo_business_connect", "public", "images", "logo-mark.png"
    )


@frappe.whitelist(allow_guest=True)
def get_app_icon(size=512, maskable=0):
    """Render a PNG app icon for the PWA manifest.

    Args:
        size: pixel size (square)
        maskable: when truthy, composite on a solid theme-color background
                  with safe-zone padding (Android adaptive icons).
    """
    size = min(max(cint(size, 512), 48), 1024)
    maskable = cint(maskable, 0)

    from PIL import Image

    try:
        source = Image.open(_icon_source_path()).convert("RGBA")
    except Exception:
        frappe.throw("App icon source could not be loaded", frappe.DoesNotExistError)

    if maskable:
        canvas = Image.new("RGBA", (size, size), _hex_to_rgb(OSDUO_BRANDING["primary_color"]) + (255,))
        target = int(size * 0.62)
    else:
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        target = size

    source.thumbnail((target, target), Image.LANCZOS)
    canvas.paste(
        source,
        ((size - source.width) // 2, (size - source.height) // 2),
        source,
    )

    from io import BytesIO

    buffer = BytesIO()
    canvas.save(buffer, format="PNG", optimize=True)

    # Frappe v16: response type "download" (as_raw) honours content_type and
    # display_content_as — served inline as image/png so <img> and the
    # manifest can consume it. ("binary" would force an attachment.)
    frappe.local.response["type"] = "download"
    frappe.local.response["display_content_as"] = "inline"
    frappe.local.response["content_type"] = "image/png"
    frappe.local.response["filename"] = f"bc-icon-{size}{'-m' if maskable else ''}.png"
    frappe.local.response["filecontent"] = buffer.getvalue()
    buffer.close()


def get_manifest_context():
    """Build per-site manifest values for www/manifest.json."""
    name = frappe.get_website_settings("app_name") or ""
    if name.strip().lower() in ("", "frappe"):
        # Generic defaults are not white-label — prefer site-configured names.
        name = (
            frappe.db.get_single_value("System Settings", "app_name")
            or OSDUO_BRANDING["app_name"]
        )
    name = (name or OSDUO_BRANDING["app_name"]).strip()
    if name.strip().lower() == "frappe":
        name = OSDUO_BRANDING["app_name"]

    short_name = OSDUO_BRANDING["app_short_name"]
    if len(name) <= 30:
        short_name = name
    short_name = short_name[:30]

    return {
        "name": name,
        "short_name": short_name,
        "description": OSDUO_BRANDING["tagline"],
        "theme_color": OSDUO_BRANDING["primary_color"],
        "background_color": OSDUO_BRANDING["background_color"],
        "canonical_base_url": get_canonical_base_url(),
    }
