# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Plan-aware navigation context for logged-in Business Connect portal pages.

The sidebar is deliberately data-driven: links are derived from the site's
entitlement snapshot and the caller's roles, never from the requested path.
Professional/Business customers therefore never see native Desk links, while
provider roles and Enterprise keep their advanced-administration entry point.
"""

import frappe

from osduo_business_connect.subscription.constants import PRIVILEGED_ROLES
from osduo_business_connect.subscription.entitlements import (
    get_entitlements,
    has_feature,
)

ACTIVE_KEYS = frozenset({
    "card",
    "team",
    "subscription",
    "analytics",
    "crm",
    "admin",
})


def get_portal_nav(active=None):
    """Return the shared sidebar context for the current request."""
    ent = get_entitlements()

    try:
        roles = set(frappe.get_roles() or ())
    except Exception:
        # A portal page should still render during install/migrate when role
        # helpers may be unavailable. Failing closed here only hides the
        # privileged admin link; the request gate remains authoritative.
        roles = set()

    return {
        "active": active if active in ACTIVE_KEYS else "",
        "plan_code": ent.get("plan_code") or "",
        "plan": ent.get("plan_name") or ent.get("plan_code") or "",
        "upgrade_url": ent.get("upgrade_url") or "",
        "can_team": has_feature("team_management"),
        "can_analytics": has_feature("analytics"),
        "can_crm": has_feature("crm_access"),
        "can_admin": bool(roles & PRIVILEGED_ROLES) or has_feature("advanced_admin"),
    }
