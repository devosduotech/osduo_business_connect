# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Test helpers for exercising plan entitlements without provisioning a site."""

from contextlib import contextmanager

import frappe

from osduo_business_connect.subscription.entitlements import clear_entitlement_cache


@contextmanager
def plan_override(plan_code):
    """Temporarily resolve entitlements as ``plan_code``."""
    previous = getattr(frappe.flags, "bc_plan_override", None)
    frappe.flags.bc_plan_override = plan_code
    clear_entitlement_cache()
    try:
        yield
    finally:
        if previous is None:
            try:
                delattr(frappe.flags, "bc_plan_override")
            except AttributeError:
                pass
        else:
            frappe.flags.bc_plan_override = previous
        clear_entitlement_cache()
