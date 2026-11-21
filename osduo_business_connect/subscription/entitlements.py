# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Single source of truth for plan entitlements.

Design rules (verified against Frappe v16):

* A Subscription Single document is created at provisioning. Its
  ``entitlement_snapshot`` is frozen so later edits to a SaaS Plan do not
  silently change an existing customer's entitlements.
* Missing/broken state fails closed to Professional for all authenticated
  operations. Public pages never call this module.
* ``frappe.permissions.has_permission`` short-circuits Administrator, so
  DocType hooks are NOT the enforcement boundary. Phase 2 installs a
  ``before_request`` gate that uses this service.

This module deliberately has no import-time database access.
"""

import json

import frappe
from frappe.utils import cint

from osduo_business_connect.subscription.constants import (
    DEFAULT_UPGRADE_URL,
    FEATURE_KEYS,
    LEGACY_UPGRADE_URLS,
    LIMIT_KEYS,
    PLAN_SEEDS,
    feature_defaults,
    limit_defaults,
    snapshot_defaults,
)


class PlanRestrictionError(frappe.ValidationError):
    """Raised when a plan does not include a requested feature or capacity."""


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

def clear_entitlement_cache():
    """Drop the request-local entitlement cache (used by tests/provisioning)."""
    if hasattr(frappe.local, "bc_entitlements"):
        delattr(frappe.local, "bc_entitlements")


# ---------------------------------------------------------------------------
# Plan / subscription loading
# ---------------------------------------------------------------------------

def get_plan_doc(plan_code):
    """Return a SaaS Plan document, or None when it is not available yet."""
    if not plan_code:
        return None
    try:
        if frappe.db.exists("SaaS Plan", plan_code):
            return frappe.get_doc("SaaS Plan", plan_code)
    except Exception:
        # During install/migrate the DocType may not be synced yet.
        return None
    return None


def get_subscription():
    """Return the site's Subscription Single document, or None."""
    try:
        if not frappe.db.exists("DocType", "Subscription"):
            return None
        # A Single DocType ALWAYS "exists" in Frappe v16 (database.exists short-circuits
        # when dt == dn), even before it has ever been saved. Check a real field instead.
        if not frappe.db.get_single_value("Subscription", "plan"):
            return None
        return frappe.get_doc("Subscription")
    except Exception:
        return None


def plan_to_snapshot(plan_doc):
    """Build a frozen snapshot payload from a SaaS Plan document."""
    features = {}
    for key in FEATURE_KEYS:
        features[key] = bool(plan_doc.get(key))

    limits = {}
    for key in LIMIT_KEYS:
        value = plan_doc.get(key)
        if key == "seat_cap":
            # The seat cap is derived at provisioning, not stored on the plan.
            value = limit_defaults(plan_doc.name).get("min_billed_seats")
        if value is None and key in limit_defaults(plan_doc.name):
            value = limit_defaults(plan_doc.name)[key]
        limits[key] = value

    return {
        "plan_code": plan_doc.name,
        "plan_name": plan_doc.get("plan_name") or plan_doc.name,
        "features": features,
        "limits": limits,
        "source": "plan_master",
    }


def _parse_snapshot(raw):
    """Parse the snapshot JSON, falling back to safe defaults on bad data."""
    if not raw:
        return None
    try:
        data = json.loads(raw) if isinstance(raw, str) else dict(raw)
    except (TypeError, ValueError):
        return None
    if not isinstance(data, dict) or not isinstance(data.get("features"), dict):
        return None
    return data


def _normalise_snapshot(snapshot, plan_code=None):
    """Guarantee every feature and limit key exists in a snapshot."""
    code = plan_code or (snapshot or {}).get("plan_code") or "PROFESSIONAL"
    fallback = snapshot_defaults(code)
    source = dict(snapshot or {})
    features = dict(fallback["features"])
    features.update(source.get("features") or {})
    limits = dict(fallback["limits"])
    limits.update(source.get("limits") or {})

    # Belt-and-braces: never let a partial snapshot grant a base feature.
    base = feature_defaults(code)
    for key, value in base.items():
        if key not in (source.get("features") or {}):
            features[key] = value

    return {
        "plan_code": code,
        "plan_name": source.get("plan_name") or fallback["plan_name"],
        "features": {key: bool(features.get(key, False)) for key in FEATURE_KEYS},
        "limits": {key: limits.get(key) for key in LIMIT_KEYS},
        "source": source.get("source") or fallback["source"],
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_entitlements():
    """Return the effective entitlement dict for this request.

    Shape::

        {
          "plan_code": "BUSINESS",
          "features": {<key>: bool},
          "limits": {<key>: value},
          "status": "Active",
          "accessible": True,
          "external_crm_enabled": False,
          "upgrade_url": "https://...",
          "source": "subscription_snapshot",
        }
    """
    cached = getattr(frappe.local, "bc_entitlements", None)
    if cached is not None:
        return cached

    subscription = get_subscription()

    # Test-only override: lets the suite exercise a plan without provisioning.
    # Never honour it outside the test runner, so a client cannot escalate plan.
    override = getattr(frappe.flags, "bc_plan_override", None) if getattr(frappe.flags, "in_test", False) else None
    if override:
        plan = get_plan_doc(override)
        snapshot = plan_to_snapshot(plan) if plan else snapshot_defaults(override)
        result = _normalise_snapshot(snapshot, override)
        result.update({
            "status": "Active",
            "accessible": True,
            "source": "test_override",
        })
    elif subscription:
        snapshot = _parse_snapshot(getattr(subscription, "entitlement_snapshot", None))
        # The frozen snapshot decides the plan once provisioning has run. The
        # Subscription.plan field is only a legacy fallback for sites that have
        # no snapshot yet, so editing that field can never escalate entitlements.
        plan_code = (snapshot or {}).get("plan_code") or getattr(subscription, "plan", None)
        result = _normalise_snapshot(snapshot, plan_code)
        result["status"] = subscription.status or "Active"
        result["source"] = "subscription_snapshot" if snapshot else "subscription_defaults"
        # Seats actually purchased are live Subscription state, not plan-master data.
        # The frozen snapshot's seat_cap is only a fallback for test overrides.
        purchased_seats = cint(getattr(subscription, "seats_cap", 0))
        if purchased_seats > 0:
            result["limits"]["seat_cap"] = purchased_seats
    else:
        result = _normalise_snapshot(snapshot_defaults("PROFESSIONAL"), "PROFESSIONAL")
        result["status"] = "Active"
        result["source"] = "fail_closed_default"

    # Live site-level state always wins over anything frozen in the snapshot.
    result["external_crm_enabled"] = bool(cint(frappe.conf.get("bc_external_crm_enabled")))
    configured_url = frappe.conf.get("bc_upgrade_url")
    if not configured_url or configured_url in LEGACY_UPGRADE_URLS:
        # Existing sites configured before the pricing anchor was added must
        # still send customers straight to the plan/pricing section.
        configured_url = DEFAULT_UPGRADE_URL
    result["upgrade_url"] = configured_url
    result["accessible"] = _is_accessible(result["status"], subscription)

    frappe.local.bc_entitlements = result
    return result


def _is_accessible(status, subscription=None):
    """Trial/Active/Past Due (inside grace) are accessible; others are not."""
    if status in ("Trial", "Active"):
        return True
    if status == "Past Due":
        grace_until = getattr(subscription, "grace_until", None) if subscription else None
        if not grace_until:
            return False
        from frappe.utils import getdate, today
        return getdate(grace_until) >= getdate(today())
    return False


def get_plan_code():
    return get_entitlements()["plan_code"]


def get_features():
    return dict(get_entitlements()["features"])


def get_limits():
    return dict(get_entitlements()["limits"])


def has_feature(key):
    """True when the current plan includes ``key`` and the site is accessible."""
    ent = get_entitlements()
    return bool(ent["accessible"] and ent["features"].get(key, False))


def require_feature(key, label=None):
    """Raise PlanRestrictionError when the feature is not available."""
    if has_feature(key):
        return True
    ent = get_entitlements()
    plan_name = ent.get("plan_name") or ent["plan_code"]
    display = label or key.replace("_", " ")
    # frappe.throw (not a bare raise) publishes the text in __server_messages.
    # v16's API v2 error payload otherwise contains only the exception type.
    frappe.throw(
        f"{display.capitalize()} is not available on the {plan_name} plan. "
        f"Upgrade to unlock it: {ent['upgrade_url']}",
        exc=PlanRestrictionError,
    )


def get_limit(key):
    return get_entitlements()["limits"].get(key)


def enforce_limit(key, current, label=None):
    """Raise when ``current`` has reached/exceeded a hard limit."""
    limit = get_limit(key)
    if limit is None or int(limit) == -1:
        return
    if int(current or 0) >= int(limit):
        frappe.throw(
            f"{(label or key.replace('_', ' ')).capitalize()} limit reached "
            f"({int(current)} of {int(limit)}). Cancel an existing record or upgrade: "
            f"{get_entitlements()['upgrade_url']}",
            exc=PlanRestrictionError,
        )


def is_accessible():
    return bool(get_entitlements()["accessible"])


def get_usage():
    """Return current usage counters for the My Subscription page and quota checks."""
    usage = {"businesses": 0, "seats": 0, "active_domains": 0}
    try:
        usage["businesses"] = int(frappe.db.count("Business", {"docstatus": ["<", 2]}) or 0)
    except Exception:
        pass

    try:
        rows = frappe.db.sql(
            """SELECT COUNT(DISTINCT `bm`.`user`)
            FROM `tabBusiness Member` `bm`
            INNER JOIN `tabUser` `u` ON `u`.`name` = `bm`.`user`
            WHERE `bm`.`status` = 'Active' AND `u`.`enabled` = 1"""
        )
        usage["seats"] = int(rows[0][0]) if rows else 0
    except Exception:
        pass

    subscription = get_subscription()
    if subscription:
        try:
            usage["active_domains"] = sum(
                1 for row in (subscription.get("domain_mappings") or [])
                if row.get("status") == "Active"
            )
        except Exception:
            pass
    return usage
