# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
CRM Lead Permission Module

Provides OSDuo Business Connect permission layer on top of Frappe CRM's
native permission model. CRM Lead is the bridge between Business Connect
acquisition context and CRM sales operations.

Rules:
- System Manager: full access
- CRM Manager/User: CRM's native rules apply (no OSDuo filtering)
- Business member: can only see CRM Leads where osduo_business
  belongs to one of their active Business memberships
- Guest: no access
"""

import frappe


def has_permission(doc, ptype):
    """
    Document-level permission for CRM Lead.

    Adds OSDuo business isolation on top of CRM's native permissions.
    """
    user = frappe.session.user

    # Guest: no access
    if user == "Guest":
        return False

    # System Manager: full access
    if "System Manager" in frappe.get_roles(user):
        return True

    # CRM Manager/User: defer to CRM's native permission system.
    # These roles manage CRM Leads through CRM's own ownership model.
    # Business Connect only adds filtering for business-scoped access.
    crm_roles = {"CRM Manager", "CRM User"}
    user_roles = set(frappe.get_roles(user))

    # If user has CRM roles AND the lead has no osduo_business,
    # let CRM handle it natively
    osduo_business = doc.osduo_business if hasattr(doc, "osduo_business") else None
    if not osduo_business:
        # No Business Connect context — CRM's native permissions apply
        return True

    # Lead has osduo_business: check if user is a member of that business
    from osduo_business_connect.business.core import get_user_businesses
    businesses = get_user_businesses(user)
    business_names = [b["name"] for b in businesses]

    if osduo_business in business_names:
        return True

    # User is not a member of the lead's business
    return False


def get_permission_query_conditions(user):
    """
    List-level permission filtering for CRM Lead.

    Adds OSDuo business isolation for list queries.
    """
    if not user:
        user = frappe.session.user

    # Guest: no access
    if user == "Guest":
        return "`tabCRM Lead`.name IN (SELECT name FROM `tabCRM Lead` WHERE 1=0)"

    # System Manager: see all
    if "System Manager" in frappe.get_roles(user):
        return ""

    # CRM Manager/User: see all CRM Leads (CRM's native model)
    # Business Connect filtering only applies to business-scoped views
    crm_roles = {"CRM Manager", "CRM User"}
    user_roles = set(frappe.get_roles(user))

    # If user has CRM roles, show all leads (CRM handles ownership)
    if user_roles & crm_roles:
        return ""

    # For non-CRM users (Business members):
    # Show leads where osduo_business matches their businesses
    # OR leads with no osduo_business (direct CRM leads)
    from osduo_business_connect.business.core import get_user_businesses
    businesses = get_user_businesses(user)

    if not businesses:
        # No business membership: show only leads with no osduo_business
        return "`tabCRM Lead`.osduo_business IS NULL OR `tabCRM Lead`.osduo_business = ''"

    business_names = [frappe.db.escape(b["name"]) for b in businesses]
    business_list = ", ".join(business_names)

    return (
        f"`tabCRM Lead`.osduo_business IN ({business_list}) "
        f"OR `tabCRM Lead`.osduo_business IS NULL "
        f"OR `tabCRM Lead`.osduo_business = ''"
    )
