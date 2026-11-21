# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Manual provisioning helpers.

There is no checkout, invoice, payment or webhook processing in this app. An
operator provisions a site here after the sale has been agreed externally
(currently through Aasriva). This module only mirrors that state locally.
"""

import json
import os

import frappe
from frappe import _
from frappe.utils import add_days, getdate, now_datetime, today

from osduo_business_connect.subscription.constants import (
    PLAN_SEEDS,
    SUBSCRIPTION_STATUSES,
    snapshot_defaults,
)
from osduo_business_connect.subscription.entitlements import (
    clear_entitlement_cache,
    get_plan_doc,
    plan_to_snapshot,
)

ALLOWED_STATUS_TRANSITIONS = {
    "Trial": ("Active", "Past Due", "Suspended", "Cancelled"),
    "Active": ("Past Due", "Suspended", "Cancelled"),
    "Past Due": ("Active", "Suspended", "Cancelled"),
    "Suspended": ("Active", "Cancelled"),
    "Cancelled": (),
}


# ---------------------------------------------------------------------------
# site_config.json access (explicit, so no reliance on version-specific helpers)
# ---------------------------------------------------------------------------

def _site_config_path():
    return frappe.get_site_path("site_config.json")


def _read_site_config():
    path = _site_config_path()
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _write_site_config(updates, dry_run=False):
    """Merge ``updates`` into site_config.json, preserving existing keys."""
    if dry_run:
        return dict(updates)
    path = _site_config_path()
    conf = _read_site_config()
    conf.update(updates)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(conf, handle, indent=2, sort_keys=True)
        handle.write("\n")
    # Keep the in-memory conf used by entitlement lookups in this process.
    frappe.conf.update(updates)
    return conf


# ---------------------------------------------------------------------------
# Validation / snapshot helpers
# ---------------------------------------------------------------------------

def validate_provision_inputs(plan_code, seats=None, status="Active"):
    """Validate provisioning arguments before anything is written."""
    if plan_code not in PLAN_SEEDS:
        raise frappe.ValidationError(
            f"Unknown plan '{plan_code}'. Expected one of: {', '.join(PLAN_SEEDS)}"
        )
    if status not in SUBSCRIPTION_STATUSES:
        raise frappe.ValidationError(f"Unknown subscription status '{status}'")

    plan = get_plan_doc(plan_code)
    min_seats = int((plan.get("min_seats") if plan else PLAN_SEEDS[plan_code]["min_seats"]) or 0)
    seats = int(seats or min_seats)
    if seats < min_seats:
        raise frappe.ValidationError(
            f"{plan_code} requires at least {min_seats} billed seats; got {seats}."
        )
    return plan, min_seats, seats


def build_entitlement_snapshot(plan_code, plan=None):
    """Freeze a plan's features and limits into a JSON-serialisable dict."""
    plan = plan or get_plan_doc(plan_code)
    snapshot = plan_to_snapshot(plan) if plan else snapshot_defaults(plan_code)
    snapshot["captured_at"] = str(now_datetime())
    return snapshot


# ---------------------------------------------------------------------------
# Provisioning
# ---------------------------------------------------------------------------

def provision_site(
    plan_code,
    seats=None,
    status="Active",
    external_crm=False,
    hostname=None,
    start_date=None,
    external_ref=None,
    notes=None,
    provisioned_by=None,
    dry_run=False,
    force=False,
):
    """Create or refresh this site's Subscription and write site_config keys.

    Returns a summary dict suitable for printing to the operator.
    """
    plan, min_seats, seats = validate_provision_inputs(
        plan_code, seats=seats, status=status
    )
    start = getdate(start_date) if start_date else getdate(today())
    period_end = add_days(start, 365)
    snapshot = build_entitlement_snapshot(plan_code, plan)
    seats_cap = max(min_seats, seats)

    conf_updates = {
        "bc_plan_code": plan_code,
        "bc_seats": seats,
        "bc_external_crm_enabled": 1 if external_crm else 0,
    }
    if external_ref:
        conf_updates["bc_external_ref"] = external_ref

    hostname_changed = False
    if hostname:
        existing = frappe.conf.get("host_name") or frappe.conf.get("hostname")
        if existing and existing.rstrip("/") != hostname.rstrip("/") and not force:
            raise frappe.ValidationError(
                "host_name is already set to a different value. Changing it re-derives "
                "printed QR/NFC URLs. Re-run with force=True only after confirming the "
                "printed-media policy."
            )
        hostname_changed = bool(existing and existing.rstrip("/") != hostname.rstrip("/"))
        conf_updates["host_name"] = hostname

    # Single DocTypes always "exist" in Frappe v16, so check a populated field.
    existing_subscription = None
    try:
        if frappe.db.get_single_value("Subscription", "plan"):
            existing_subscription = frappe.get_doc("Subscription")
    except Exception:
        existing_subscription = None

    if existing_subscription and not force:
        raise frappe.ValidationError(
            "This site already has a Subscription. Re-run with force=True to overwrite it."
        )

    doc_data = {
        "doctype": "Subscription",
        "plan": plan_code,
        "status": status,
        "seats_ordered": seats,
        "min_billed_seats": min_seats,
        "seats_cap": seats_cap,
        "start_date": start,
        "current_period_end": period_end,
        "grace_until": None,
        "site_plan_source": "Manual Selection",
        "external_ref": external_ref,
        "external_crm_enabled": 1 if external_crm else 0,
        "provisioned_by": provisioned_by or getattr(frappe.session, "user", None) or "Administrator",
        "provisioned_on": now_datetime(),
        "grandfathered": 0,
        "migrated": 0,
        "entitlement_snapshot": json.dumps(snapshot, indent=2, sort_keys=True),
        "notes": notes,
    }

    if dry_run:
        summary = dict(doc_data)
        summary["site_config_updates"] = conf_updates
        summary["dry_run"] = True
        return summary

    if existing_subscription:
        for key, value in doc_data.items():
            if key == "doctype":
                continue
            existing_subscription.set(key, value)
        subscription = existing_subscription
        action = "Reprovisioned"
    else:
        subscription = frappe.get_doc(doc_data)
        action = "Provisioned"

    subscription.append("audit_log", {
        "timestamp": now_datetime(),
        "user": doc_data["provisioned_by"],
        "action": action,
        "details": f"plan={plan_code}, seats={seats}, cap={seats_cap}, external_crm={bool(external_crm)}",
    })
    if subscription.is_new():
        subscription.insert(ignore_permissions=True)
    else:
        subscription.save(ignore_permissions=True)

    # Commit the Subscription first: a failed config write then fails closed
    # (external CRM off) instead of advertising a plan the site does not hold.
    frappe.db.commit()
    _write_site_config(conf_updates)
    clear_entitlement_cache()

    return {
        "site": frappe.local.site,
        "plan": plan_code,
        "billed_seats": seats_cap,
        "seats_ordered": seats,
        "max_businesses": snapshot["limits"]["max_businesses"],
        "included_domains": snapshot["limits"]["included_domain_mappings"],
        "domain_price": snapshot["limits"]["domain_mapping_price"],
        "status": status,
        "external_crm_enabled": bool(external_crm),
        "host_name_changed": hostname_changed,
        "period_end": period_end,
        "action": action,
    }


# ---------------------------------------------------------------------------
# Provider-controlled status changes
# ---------------------------------------------------------------------------

def set_status(status, grace_until=None, note=None, user=None):
    """Apply a provider-controlled Subscription status transition with audit."""
    if status not in SUBSCRIPTION_STATUSES:
        raise frappe.ValidationError(f"Unknown subscription status '{status}'")

    subscription = frappe.get_doc("Subscription")
    current = subscription.status
    if current == status:
        return {"site": frappe.local.site, "status": current, "changed": False}

    allowed = ALLOWED_STATUS_TRANSITIONS.get(current, ())
    if status not in allowed:
        raise frappe.ValidationError(
            f"Cannot change subscription status from {current} to {status}. "
            f"Allowed: {', '.join(allowed) or 'none'}"
        )

    subscription.status = status
    if grace_until is not None:
        subscription.grace_until = getdate(grace_until) if grace_until else None
    subscription.append("audit_log", {
        "timestamp": now_datetime(),
        "user": user or getattr(frappe.session, "user", None) or "Administrator",
        "action": f"Status: {current} -> {status}",
        "details": note or (f"grace_until={grace_until}" if grace_until else ""),
    })
    subscription.save(ignore_permissions=True)
    frappe.db.commit()
    clear_entitlement_cache()

    return {"site": frappe.local.site, "status": status, "changed": True}
