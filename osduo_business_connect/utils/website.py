# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Website branding context injection.

Injects branding variables into all web templates so they can
use {{ bc_app_name }}, {{ bc_logo }}, etc. without hardcoding.
"""

import frappe

from osduo_business_connect.hooks import OSDUO_BRANDING


def get_branding_context(context):
    """
    Add branding variables to website context.

    Called via update_website_context hook in hooks.py.
    Available in all web templates as {{ bc_app_name }}, {{ bc_logo }}, etc.
    """
    context.update({
        "bc_app_name": OSDUO_BRANDING["app_name"],
        "bc_app_short_name": OSDUO_BRANDING["app_short_name"],
        "bc_tagline": OSDUO_BRANDING["tagline"],
        "bc_logo": OSDUO_BRANDING["logo"],
        "bc_logo_dark": OSDUO_BRANDING["logo_dark"],
        "bc_favicon": OSDUO_BRANDING["favicon"],
        "bc_logo_mark": OSDUO_BRANDING["logo_mark"],
        "bc_og_image": OSDUO_BRANDING["og_image"],
        "bc_primary_color": OSDUO_BRANDING["primary_color"],
        "bc_secondary_color": OSDUO_BRANDING["secondary_color"],
        "bc_accent_color": OSDUO_BRANDING["accent_color"],
        "bc_background_color": OSDUO_BRANDING["background_color"],
        "bc_text_color": OSDUO_BRANDING["text_color"],
    })


def safe_url(url):
    """Jinja filter: sanitize URL to prevent javascript: protocol injection.

    Returns empty string for dangerous protocols.
    """
    if not url:
        return ""
    url = str(url).strip()
    url_lower = url.lower()
    dangerous = ["javascript:", "data:", "vbscript:", "file:"]
    for proto in dangerous:
        if url_lower.startswith(proto):
            return ""
    return url


def safe_video_url(url):
    """Jinja filter: sanitize video iframe src to prevent XSS.

    Only allows https/http URLs from known video embed domains.
    Returns empty string for invalid or dangerous URLs.
    """
    if not url:
        return ""
    url = str(url).strip()
    url_lower = url.lower()

    # Block dangerous protocols
    dangerous = ["javascript:", "data:", "vbscript:", "file:"]
    for proto in dangerous:
        if url_lower.startswith(proto):
            return ""

    # Only allow https or http
    if not url_lower.startswith("http://") and not url_lower.startswith("https://"):
        return ""

    # Allow known video embed domains
    allowed_domains = [
        "youtube.com", "www.youtube.com", "youtu.be",
        "vimeo.com", "www.vimeo.com",
        "player.vimeo.com",
        "dailymotion.com", "www.dailymotion.com",
        "wistia.com", "www.wistia.com",
        "loom.com", "www.loom.com",
        "streamable.com", "www.streamable.com",
        "facebook.com", "www.facebook.com",
        "drive.google.com",
    ]

    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        if host and any(host == d or host.endswith("." + d) for d in allowed_domains):
            return url
    except Exception:
        pass

    return ""
