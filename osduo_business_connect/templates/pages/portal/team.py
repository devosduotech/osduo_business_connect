# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Customer Team portal page — /portal/team.

Login-gated, Desk-free team management. Frappe resolves this controller from
the adjacent ``team.html`` through the ``website_route_rules`` entry in
``hooks.py``.
"""

import frappe

from osduo_business_connect.subscription.portal_nav import get_portal_nav
from osduo_business_connect.subscription.team_invite import get_team_page_data
from osduo_business_connect.utils.seo import NOINDEX, build_seo

no_cache = 1


def get_context(context):
    if getattr(frappe.session, "user", "Guest") == "Guest":
        frappe.throw("Login required", frappe.PermissionError)

    context.title = "Team"
    context.no_cache = 1
    context.team = get_team_page_data()
    context.portal_nav = get_portal_nav("team")
    context.seo = build_seo("Team", "", "/portal/team", robots=NOINDEX)
    return context
