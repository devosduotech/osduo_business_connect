# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
My Card Web Page — /my-card

Login-gated entry point that lists the logged-in user's own digital cards.

Frappe resolves this module from the adjacent ``my-card.html`` template
(hyphens are converted to underscores for Python module names).
"""

import frappe

from osduo_business_connect.card.my_card import get_my_cards_for_user

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Login required", frappe.PermissionError)

    context.title = "My Card"
    context.no_cache = 1
    context.my_cards = get_my_cards_for_user(frappe.session.user)
    return context
