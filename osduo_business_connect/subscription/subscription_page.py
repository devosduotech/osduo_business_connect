# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Read-only data for the My Subscription Desk page.

The page deliberately exposes no payment, checkout, invoice or credential
data. Billing happens at Aasriva; this endpoint only reports plan, usage and
the configured upgrade link.
"""

import frappe

from osduo_business_connect.subscription.constants import FEATURE_KEYS, PLAN_SEEDS
from osduo_business_connect.subscription.domains import get_domain_rows
from osduo_business_connect.subscription.entitlements import (
    get_entitlements,
    get_subscription,
    get_usage,
)


@frappe.whitelist()
def get_my_subscription():
    """Return the current site's subscription summary for the signed-in user."""
    if not getattr(frappe.session, "user", "Guest") or frappe.session.user == "Guest":
        frappe.throw("Please log in to view your subscription", exc=frappe.PermissionError)

    ent = get_entitlements()
    usage = get_usage()
    limits = ent["limits"]
    subscription = get_subscription()
    plan_code = ent["plan_code"]

    return {
        "status": ent.get("status") or "Active",
        "accessible": bool(ent.get("accessible")),
        "plan": ent.get("plan_name") or plan_code,
        "plan_code": plan_code,
        "price_per_seat_per_year": PLAN_SEEDS.get(plan_code, {}).get(
            "price_per_seat_per_year", 0
        ),
        "period_end": getattr(subscription, "current_period_end", None) if subscription else None,
        "billing_source": "Aasriva",
        "external_crm_enabled": bool(ent.get("external_crm_enabled")),
        "seats": {
            "used": int(usage.get("seats") or 0),
            "billed": int(limits.get("seat_cap") or 0),
        },
        "businesses": {
            "used": int(usage.get("businesses") or 0),
            "cap": int(limits.get("max_businesses") or 0),
            "cancelled": _cancelled_businesses(),
        },
        "domains": {
            "included": int(limits.get("included_domain_mappings") or 0),
            "price": int(limits.get("domain_mapping_price") or 0),
            "rows": [_domain_row(row) for row in get_domain_rows(subscription)],
        },
        "features": [
            {"key": key, "label": key.replace("_", " ").title(), "enabled": bool(ent["features"].get(key))}
            for key in FEATURE_KEYS
        ],
        "upgrade_url": ent.get("upgrade_url") or "",
    }


def _cancelled_businesses():
    try:
        return int(frappe.db.count("Business", {"docstatus": 2}) or 0)
    except Exception:
        return 0


def _domain_row(row):
    return {
        "hostname": row.get("hostname"),
        "mapping_type": row.get("mapping_type"),
        "status": row.get("status"),
        "price": row.get("price"),
        "expires_on": row.get("expires_on"),
    }
