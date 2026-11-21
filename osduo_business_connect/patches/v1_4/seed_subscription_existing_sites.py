# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Seed a Business subscription for sites that predate the plan module.

Fresh, empty sites are deliberately left unprovisioned so they fail closed to
Professional until an operator runs the provisioning script. Existing in-use
sites are defaulted to Business so current CRM/Analytics users are not locked
out by the new gates.
"""

import json

import frappe
from frappe.utils import add_days, now_datetime, today

from osduo_business_connect.subscription.constants import PLAN_SEEDS
from osduo_business_connect.subscription.entitlements import clear_entitlement_cache
from osduo_business_connect.subscription.provision import _write_site_config, build_entitlement_snapshot
from osduo_business_connect.subscription.seed import seed_plans_and_addons


def _count(doctype, filters=None):
    try:
        return int(frappe.db.count(doctype, filters) or 0)
    except Exception:
        return 0


def _active_seat_count():
    try:
        rows = frappe.db.sql(
            """SELECT COUNT(DISTINCT `bm`.`user`)
            FROM `tabBusiness Member` `bm`
            INNER JOIN `tabUser` `u` ON `u`.`name` = `bm`.`user`
            WHERE `bm`.`status` = 'Active' AND `u`.`enabled` = 1"""
        )
        return int(rows[0][0]) if rows else 0
    except Exception:
        return 0


def execute():
    try:
        # Single DocTypes always "exist" in Frappe v16; check a populated field.
        if frappe.db.get_single_value("Subscription", "plan"):
            return
    except Exception:
        return

    business_count = _count("Business")
    other_users = _count("User", {
        "enabled": 1,
        "name": ["not in", ["Administrator", "Guest"]],
    })
    if not business_count and not other_users:
        frappe.logger("osduo_business_connect").info(
            "Subscription migration skipped: site has no existing business or user data"
        )
        return

    seed_plans_and_addons()

    plan_code = "BUSINESS"
    seed = PLAN_SEEDS[plan_code]
    seats_ordered = max(seed["min_seats"], _active_seat_count())
    snapshot = build_entitlement_snapshot(plan_code)
    start = today()
    period_end = add_days(start, 365)

    subscription = frappe.get_doc({
        "doctype": "Subscription",
        "plan": plan_code,
        "status": "Active",
        "seats_ordered": seats_ordered,
        "min_billed_seats": seed["min_seats"],
        "seats_cap": max(seed["min_seats"], seats_ordered),
        "start_date": start,
        "current_period_end": period_end,
        "grace_until": None,
        "site_plan_source": "Manual Selection",
        "external_crm_enabled": 0,
        "provisioned_by": "Administrator",
        "provisioned_on": now_datetime(),
        "grandfathered": 1 if business_count > seed["max_businesses"] else 0,
        "migrated": 1,
        "entitlement_snapshot": json.dumps(snapshot, indent=2, sort_keys=True),
        "notes": "Seeded by migration; verify plan and seats with the provider.",
    })
    subscription.append("audit_log", {
        "timestamp": now_datetime(),
        "user": "Administrator",
        "action": "Migrated",
        "details": f"plan={plan_code}, seats={seats_ordered}, businesses={business_count}",
    })
    subscription.insert(ignore_permissions=True)

    _write_site_config({
        "bc_plan_code": plan_code,
        "bc_seats": seats_ordered,
        "bc_external_crm_enabled": 0,
    })

    # No explicit commit: bench migrate wraps each phase atomically.
    clear_entitlement_cache()
