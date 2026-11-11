# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Money formatting helpers for public pages.

Exposed to Jinja as the ``format_money`` filter (see the ``jinja`` hook in
``hooks.py``) so product, service and card templates render amounts with the
site's configured number format and the currency *code* prefix, e.g.
``INR 12,000`` rather than ``INR 12000``.
"""


def format_money(amount, currency=None, precision=None):
    """Format ``amount`` with thousands separators and an optional currency code.

    Uses Frappe's ``fmt_money`` when available so the site's configured number
    format is respected, and falls back to plain Python formatting otherwise
    (for example in the structural unit tests). Whole amounts are shown without
    trailing decimals::

        format_money(12000, "INR")      -> "INR 12,000"
        format_money(140000, "INR")     -> "INR 140,000"
        format_money(12000.5, "INR")    -> "INR 12,000.50"
        format_money(12000, "INR", 2)   -> "INR 12,000.00"

    Returns an empty string for a missing amount so templates can print the
    result directly.
    """
    if amount is None or amount == "":
        return ""

    try:
        value = float(amount)
    except (TypeError, ValueError):
        return str(amount)

    if precision is None:
        rounded = round(value, 2)
        try:
            precision = 0 if rounded == int(rounded) else 2
        except (ValueError, OverflowError):
            # NaN / infinity — keep a safe default rather than crashing a page.
            precision = 2

    text = _format_number(value, precision)

    if currency:
        return f"{currency} {text}"
    return text


def _format_number(value, precision):
    """Format a number using Frappe's formatter, with a stdlib fallback."""
    try:
        from frappe.utils import fmt_money as frappe_fmt_money
    except Exception:
        return f"{value:,.{precision}f}"
    return frappe_fmt_money(value, precision=precision)
