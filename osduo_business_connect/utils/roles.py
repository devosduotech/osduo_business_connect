# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Role helpers shared across OSDuo Business Connect."""

import frappe

BC_SYSTEM_MANAGER = "BC System Manager"
SYSTEM_MANAGER_ROLES = ("System Manager", BC_SYSTEM_MANAGER)


def is_system_manager(user=None):
    """Return True when the user has a full-access system role."""
    if not user:
        user = frappe.session.user
    if not user:
        return False
    return bool(set(SYSTEM_MANAGER_ROLES) & set(frappe.get_roles(user)))
