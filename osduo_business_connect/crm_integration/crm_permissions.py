# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
CRM Permissions Module

Provides additional business-level filtering for CRM Lead.
DOES NOT override CRM's native permission system.
"""

import frappe


def get_lead_permission_query_conditions(user):
    """
    Return SQL conditions for filtering CRM Lead records by OSDuo Business.

    This adds business-level isolation on top of CRM's native permissions.

    Args:
        user: User email

    Returns:
        str: SQL WHERE condition fragment
    """
    if not user:
        user = frappe.session.user

    # System Manager sees all
    if "System Manager" in frappe.get_roles(user):
        return ""

    # CRM Manager/User sees all (CRM's own permissions handle the rest)
    if any(r in frappe.get_roles(user) for r in ["CRM Manager", "CRM User"]):
        return ""

    # Get businesses where user is a member
    from osduo_business_connect.business.core import get_user_businesses
    businesses = get_user_businesses(user)

    if not businesses:
        return "1=0"

    # Use frappe.db.escape for safe SQL construction
    business_names = [frappe.db.escape(b["name"]) for b in businesses]
    business_list = ", ".join(business_names)

    return f"`tabCRM Lead`.osduo_business IN ({business_list})"
