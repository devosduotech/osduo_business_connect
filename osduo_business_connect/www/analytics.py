# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Analytics Web Page — /analytics

Self-contained analytics dashboard. Requires login.
"""

import frappe


def get_context(context):
    """Provide page context."""
    if frappe.session.user == "Guest":
        frappe.throw("Login required", frappe.PermissionError)

    context.title = "Analytics Dashboard"
    context.no_cache = 1
