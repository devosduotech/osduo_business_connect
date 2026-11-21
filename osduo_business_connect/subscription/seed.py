# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Idempotent seeding of SaaS Plans and Add-on Masters.

Existing records are never overwritten: once a site is live its frozen
entitlement snapshot is authoritative, and provider-side plan edits must not be
silently reset by a migrate.
"""

import frappe

from osduo_business_connect.subscription.constants import (
    ADDON_SEEDS,
    FEATURE_KEYS,
    PLAN_SEEDS,
)


def seed_plans_and_addons():
    """Create the three plans and two add-ons when they are missing."""
    created = {"plans": [], "add_ons": []}

    for plan_code, seed in PLAN_SEEDS.items():
        if frappe.db.exists("SaaS Plan", plan_code):
            continue

        doc_data = {
            "doctype": "SaaS Plan",
            "plan_code": plan_code,
            "plan_name": seed["plan_name"],
            "price_per_seat_per_year": seed["price_per_seat_per_year"],
            "min_seats": seed["min_seats"],
            "min_annual_commitment": seed["price_per_seat_per_year"] * seed["min_seats"],
            "billing_cycle": "Annual",
            "max_businesses": seed["max_businesses"],
            "included_domain_mappings": seed["included_domain_mappings"],
            "domain_mapping_price": 5999,
            "domain_registration_billing": "Actual Cost",
            "is_active": 1,
            "sort_order": seed["sort_order"],
        }
        for key in FEATURE_KEYS:
            doc_data[key] = 1 if seed["features"].get(key) else 0

        frappe.get_doc(doc_data).insert(ignore_permissions=True)
        created["plans"].append(plan_code)

    for seed in ADDON_SEEDS:
        if frappe.db.exists("Add-on Master", seed["code"]):
            continue
        rows = seed.get("applicable_plans")
        if rows is None:
            rows = [
                {"doctype": "Add-on Applicable Plan", "plan": plan_code}
                for plan_code in PLAN_SEEDS
            ]
        else:
            rows = [
                {"doctype": "Add-on Applicable Plan", **row}
                for row in rows
            ]
        frappe.get_doc({
            "doctype": "Add-on Master",
            "code": seed["code"],
            "add_on_name": seed["add_on_name"],
            "billing_type": seed["billing_type"],
            "price": seed["price"],
            "description": seed["description"],
            "applies_to_all_plans": seed["applies_to_all_plans"],
            "applicable_plans": rows,
            "is_active": 1,
        }).insert(ignore_permissions=True)
        created["add_ons"].append(seed["code"])

    # Older restricted add-ons have plan rows but no plan price. Fill only the
    # blanks from the master List Price; never overwrite a provider's own price.
    created["plan_prices_backfilled"] = backfill_addon_plan_prices()

    # No explicit commit: install/migrate manage their own transaction boundaries.
    return created


def _row_get(row, key, default=None):
    getter = getattr(row, "get", None)
    if callable(getter):
        return getter(key, default)
    try:
        return row[key]
    except (KeyError, TypeError):
        return default


def _row_set(row, key, value):
    if isinstance(row, dict):
        row[key] = value
    else:
        setattr(row, key, value)


def backfill_addon_plan_prices():
    """Set missing Annual Prices on existing plan-specific add-on rows."""
    try:
        names = frappe.get_all(
            "Add-on Master",
            filters={"billing_type": "Annual", "applies_to_all_plans": 0},
            pluck="name",
        ) or []
    except Exception:
        return 0

    updated = 0
    for name in names:
        try:
            master = frappe.get_doc("Add-on Master", name)
        except Exception:
            continue
        changed = False
        for row in master.get("applicable_plans") or []:
            price = _row_get(row, "price")
            if price in (None, ""):
                _row_set(row, "price", master.price or 0)
                changed = True
        if changed:
            try:
                master.save(ignore_permissions=True)
            except Exception:
                continue
            updated += 1
    return updated
