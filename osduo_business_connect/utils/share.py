# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Share attribution helpers (Decision 12 — clean canonical + standard UTM).

Share buttons now emit standard Google-recognised UTM parameters instead of the
custom ``?ref=`` token::

    ?utm_source=<channel>&utm_medium=share&by=<sharer-slug>

Canonical / Open Graph / sitemap URLs and the printed QR/NFC payload stay
**parameter-free** (they never carried these params), so ``utm_*`` never pollutes
an indexable URL — Google Search Console ignores ``utm_*`` and the
``rel=canonical`` consolidates equity.

Two guarantees for live sites and already-distributed media:

1. **Backward compatible reader** — links in circulation still carry the legacy
   ``?ref=share_<channel>``. :func:`get_share_ref` accepts both the new
   ``utm_source`` and the old ``ref``, so old shared/printed links keep
   attributing.
2. **Stable stored campaign** — both forms map to the *same* campaign token
   (``share_whatsapp`` … ``mycard``), so engagement analytics stay comparable
   across the change; no report baselines shift.
"""

from urllib.parse import urlencode

# ``frappe`` is imported lazily (only the reader needs ``form_dict``), so this
# module stays import-safe without a bench — build_share_url and the channel
# table are pure and testable offline.

UTM_MEDIUM = "share"

# utm_source value -> stable campaign token stored in analytics.
# The token equals the historic ?ref= value so reports do not change.
CHANNELS = {
    "whatsapp": "share_whatsapp",
    "sms": "share_sms",
    "email": "share_email",
    "copy": "share_copy",
    "native": "share_copy",  # native share sheet is a copy-equivalent one-tap share
    "mycard": "mycard",
}

# Legacy ?ref= values still honoured (already on shared / printed links).
LEGACY_REFS = frozenset(CHANNELS.values())


def build_share_url(url, utm_source, by=None, campaign=None):
    """Return ``url`` with standard share UTM params appended.

    Emits ``utm_source=<channel>&utm_medium=share`` and, when given, ``by=<slug>``.
    An optional ``utm_campaign`` carries a named event/meeting from the logged-in
    Share & Save Contact flow so recipient views can be grouped under it.
    Never touches a canonical URL — this is only for outbound share buttons.
    """
    params = {"utm_source": utm_source, "utm_medium": UTM_MEDIUM}
    if by:
        params["by"] = by
    if campaign:
        params["utm_campaign"] = str(campaign).strip()[:140]
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}{urlencode(params)}"


def get_share_campaign():
    """Return the named campaign carried on an inbound share link, if any.

    ``utm_campaign`` is set by Share & Save Contact for a recorded event/meeting.
    The legacy ``campaign`` token is accepted for links already in circulation.
    """
    import frappe

    try:
        value = (
            frappe.form_dict.get("utm_campaign")
            or frappe.form_dict.get("campaign")
            or ""
        )
    except Exception:
        return None
    value = str(value).strip()[:140]
    return value or None


def _form(name):
    import frappe

    try:
        value = frappe.form_dict.get(name)
    except Exception:
        return ""
    return (value or "").strip().lower()


def get_share_ref():
    """Return the stable campaign token for the current request, if a share.

    Prefers the standard ``utm_source`` (accepted only with ``utm_medium=share``),
    then falls back to the legacy whitelisted ``?ref=`` so previously shared and
    already-printed links keep attributing. Anything else is ignored so arbitrary
    query strings cannot pollute analytics.
    """
    utm_source = _form("utm_source")
    if utm_source and _form("utm_medium") == UTM_MEDIUM:
        token = CHANNELS.get(utm_source)
        if token:
            return token
    ref = _form("ref")
    return ref if ref in LEGACY_REFS else None


def get_share_by():
    """Return the (sanitized, length-capped) sharer slug from the request."""
    import frappe

    try:
        by = frappe.form_dict.get("by")
    except Exception:
        by = None
    by = (by or "").strip()[:140]
    return by or None
