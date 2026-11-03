# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Share attribution helpers.

Share links carry ``?ref=share_<channel>&by=<slug>``. Only the whitelisted
values below are accepted; anything else is ignored so arbitrary query strings
cannot pollute analytics.
"""

import frappe

SHARE_REFS = {
    "share_whatsapp",
    "share_sms",
    "share_email",
    "share_copy",
    "mycard",
}


def get_share_ref():
    """Return the validated share reference from the current request, if any."""
    try:
        ref = frappe.form_dict.get("ref")
    except Exception:
        ref = None
    ref = (ref or "").strip().lower()
    return ref if ref in SHARE_REFS else None


def get_share_by():
    """Return the (sanitized, length-capped) sharer slug from the request."""
    try:
        by = frappe.form_dict.get("by")
    except Exception:
        by = None
    by = (by or "").strip()[:140]
    return by or None
