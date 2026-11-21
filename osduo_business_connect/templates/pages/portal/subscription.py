# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Subscription portal page — /portal/subscription.

Desk-free replacement for the legacy My Subscription Desk page. It reads the
same whitelisted, read-only summary and exposes no billing credentials.
"""

import frappe

from osduo_business_connect.subscription.portal_nav import get_portal_nav
from osduo_business_connect.subscription.subscription_page import get_my_subscription
from osduo_business_connect.utils.seo import NOINDEX, build_seo

no_cache = 1


def get_context(context):
    if getattr(frappe.session, "user", "Guest") == "Guest":
        frappe.throw("Login required", frappe.PermissionError)

    context.title = "My Subscription"
    context.no_cache = 1
    context.subscription = get_my_subscription()
    context.portal_nav = get_portal_nav("subscription")
    context.seo = build_seo("My Subscription", "", "/portal/subscription", robots=NOINDEX)
    return context
