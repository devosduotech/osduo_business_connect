# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Analytics Web Page — /analytics

Self-contained analytics dashboard. Requires login.

Frappe resolves this controller from the adjacent ``analytics.html`` template
in ``templates/pages/`` — a bare ``www/analytics.py`` is only used when a
matching ``www/analytics.html`` exists, so the previous ``www`` copy was dead
code and the login gate never fired.
"""

import frappe

from osduo_business_connect.subscription.portal_nav import get_portal_nav
from osduo_business_connect.utils.seo import NOINDEX, build_seo

no_cache = 1


def get_context(context):
    """Provide page context."""
    if frappe.session.user == "Guest":
        frappe.throw("Login required", frappe.PermissionError)

    context.title = "Analytics Dashboard"
    context.no_cache = 1
    context.portal_nav = get_portal_nav("analytics")
    context.seo = build_seo("Analytics Dashboard", "", "/analytics", robots=NOINDEX)
