# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Customer-safe team invitations built on Frappe's User Invitation flow.

Customers never receive permissions on the core ``User`` DocType. The portal
collects the small set of fields Frappe needs, this module validates the
caller/business/plan/seat cap, and Frappe's invitation API creates the User
only after the invitee accepts the emailed link. An ``after_accept`` hook then
creates the Business Member row.

Direct calls to ``frappe.core.api.user_invitation.invite_by_email`` are blocked
at the request boundary by :mod:`subscription.plan_gates`, and the
``before_insert`` DocType hook below re-checks the context even if an bypass is
attempted through another route.
"""

import re

import frappe

APP_NAME = "osduo_business_connect"
INVITER_ROLE = "BC Business Owner"

# Invitee Frappe role -> Business Member role. Only these roles may be granted
# by a customer; Administrator, System Manager, BC System Manager, BC
# Subscription Manager and the per-business Owner role are deliberately absent.
ROLE_MAP = {
    "BC Business Member": "Member",
    "BC Business Manager": "Manager",
    "BC CRM User": "CRM User",
    "BC Marketing Manager": "Marketing",
}
MEMBER_ROLE_TO_INVITE_ROLE = {value: key for key, value in ROLE_MAP.items()}

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

PRIVILEGED_ROLES = frozenset({
    "Administrator",
    "System Manager",
    "BC System Manager",
    "BC Subscription Manager",
})


def allowed_invite_roles():
    """Options for the customer portal; never derived from the Role table."""
    return [
        {"invite_role": role, "member_role": member_role}
        for role, member_role in ROLE_MAP.items()
    ]


def _session_user():
    return getattr(frappe.session, "user", None) or "Guest"


def _roles(user=None):
    getter = getattr(frappe, "get_roles", None)
    if not callable(getter):
        return set()
    try:
        return set(getter(user or _session_user()) or [])
    except Exception:
        return set()


def _is_system_manager(user=None):
    return bool(_roles(user) & PRIVILEGED_ROLES)


def _deny(message):
    frappe.throw(message, exc=frappe.PermissionError)


def _current_user():
    user = _session_user()
    if user == "Guest":
        _deny("Please log in to invite team members")
    return user


def _assert_inviter(user):
    if not _is_system_manager(user) and INVITER_ROLE not in _roles(user):
        _deny("Only the Business Owner can invite team members")


def _assert_business_owner(user, business):
    if _is_system_manager(user):
        return
    from osduo_business_connect.business.core import get_user_role_in_business

    if get_user_role_in_business(user, business) != "Owner":
        _deny("You can only invite team members to a business you own")


def _validate_business(business):
    if not business or not frappe.db.exists("Business", business):
        frappe.throw("Please choose a valid Business", exc=frappe.ValidationError)


def _validate_payload(email, first_name, invite_role, last_name=None):
    if not email or not EMAIL_RE.match(str(email).strip().lower()):
        frappe.throw("Enter a valid email address", exc=frappe.ValidationError)
    if not first_name or not str(first_name).strip():
        frappe.throw("First Name is required", exc=frappe.ValidationError)
    if invite_role not in ROLE_MAP:
        frappe.throw("That role cannot be assigned from the portal", exc=frappe.PermissionError)
    return {
        "email": str(email).strip().lower(),
        "first_name": str(first_name).strip(),
        "last_name": str(last_name or "").strip(),
        "member_role": ROLE_MAP[invite_role],
    }


def _pending_invitation_count(email=None):
    """Count outstanding BC invitations, optionally excluding one email.

    Frappe's core invite API de-duplicates a pending invitation for the same
    email, so that email must not consume a second prospective seat.
    """
    filters = {"app_name": APP_NAME, "status": "Pending"}
    if email:
        filters["email"] = ["!=", email]
    return int(frappe.db.count("User Invitation", filters) or 0)


def _seat_preflight(email):
    """Reserve a prospective seat at invite time, including pending invites."""
    from osduo_business_connect.subscription.entitlements import enforce_limit, get_usage

    user_name = frappe.db.get_value("User", email, "name")
    existing_seat = bool(
        user_name
        and frappe.db.exists("Business Member", {"user": user_name, "status": "Active"})
    )
    # ``enforce_limit`` expects the count that already exists before the new
    # record is added: it blocks once that count has reached the cap. Pending
    # invitations are counted here so a seat cannot be sold twice; an invite
    # for the same email is excluded because Frappe de-duplicates it.
    current = int(get_usage().get("seats") or 0) + _pending_invitation_count(email)
    if existing_seat:
        return  # the invitee already holds a billable seat
    enforce_limit("seat_cap", current, "Seats")


@frappe.whitelist(methods=["POST"])
def invite_team_member(
    email,
    first_name,
    business,
    invite_role,
    last_name=None,
):
    """Validate a customer invite, then delegate to Frappe's invitation API."""
    user = _current_user()
    _assert_inviter(user)
    values = _validate_payload(email, first_name, invite_role, last_name)
    _validate_business(business)
    _assert_business_owner(user, business)

    from osduo_business_connect.subscription.entitlements import require_feature

    require_feature("team_management")
    _seat_preflight(values["email"])

    from frappe.core.api.user_invitation import invite_by_email

    return invite_by_email(
        emails=values["email"],
        roles=[invite_role],
        redirect_to_path="/portal/team",
        app_name=APP_NAME,
        bc_business=business,
        bc_member_role=values["member_role"],
        bc_first_name=values["first_name"],
        bc_last_name=values["last_name"],
    )


def validate_invitation_context(doc, method=None):
    """DocType hook: direct core API calls cannot skip BC validation."""
    if getattr(doc, "app_name", None) != APP_NAME:
        return
    status = getattr(doc, "status", None)
    if status and status != "Pending":
        return

    user = _current_user()
    _assert_inviter(user)

    roles = []
    for row in getattr(doc, "roles", None) or []:
        value = row.get("role") if hasattr(row, "get") else getattr(row, "role", None)
        if value:
            roles.append(value)
    if len(roles) != 1 or roles[0] not in ROLE_MAP:
        frappe.throw("Choose one allowed BC role", exc=frappe.PermissionError)

    business = getattr(doc, "bc_business", None)
    member_role = getattr(doc, "bc_member_role", None)
    if member_role != ROLE_MAP[roles[0]]:
        frappe.throw("Invite role and member role do not match", exc=frappe.ValidationError)

    values = _validate_payload(
        getattr(doc, "email", None),
        getattr(doc, "bc_first_name", None),
        roles[0],
        getattr(doc, "bc_last_name", None),
    )
    _validate_business(business)
    _assert_business_owner(user, business)

    from osduo_business_connect.subscription.entitlements import require_feature

    require_feature("team_management")
    _seat_preflight(values["email"])


def after_accept_create_member(invitation, user, user_inserted=False):
    """Create the Business Member row after the invitee sets their password."""
    if getattr(invitation, "app_name", None) != APP_NAME:
        return

    from osduo_business_connect.subscription.entitlements import (
        enforce_limit,
        get_usage,
        require_feature,
    )

    # Re-check the plan and seat cap at acceptance. A downgrade or seat sale
    # between invite and acceptance must still be honoured.
    require_feature("team_management")

    business = getattr(invitation, "bc_business", None)
    member_role = getattr(invitation, "bc_member_role", None)
    if member_role not in MEMBER_ROLE_TO_INVITE_ROLE:
        frappe.throw("The invitation is missing a valid member role", exc=frappe.ValidationError)
    _validate_business(business)

    user_name = getattr(user, "name", None)
    existing_here = bool(
        user_name
        and frappe.db.exists(
            "Business Member",
            {"business": business, "user": user_name, "status": "Active"},
        )
    )
    existing_seat = bool(
        user_name
        and frappe.db.exists("Business Member", {"user": user_name, "status": "Active"})
    )
    if not existing_seat:
        # The Business Member insert runs its own seat check, but rejecting here
        # gives a clearer error while the invitee is still on the accept page.
        enforce_limit("seat_cap", int(get_usage().get("seats") or 0), "Seats")

    first_name = getattr(invitation, "bc_first_name", None) or getattr(user, "first_name", None)
    last_name = getattr(invitation, "bc_last_name", None) or getattr(user, "last_name", None)
    if first_name and (
        getattr(user, "first_name", None) != first_name
        or getattr(user, "last_name", None) != last_name
    ):
        user.first_name = first_name
        user.last_name = last_name
        user.save(ignore_permissions=True)

    if existing_here:
        return

    member = frappe.get_doc(
        {
            "doctype": "Business Member",
            "business": business,
            "user": user_name,
            "person_name": " ".join(part for part in (first_name, last_name) if part),
            "email": getattr(user, "email", None) or getattr(invitation, "email", None),
            "role": member_role,
            "status": "Active",
        }
    )
    member.insert(ignore_permissions=True)


@frappe.whitelist()
def get_team_page_data():
    """Read-only portal payload: own businesses, members, seats and role options."""
    user = _current_user()

    from osduo_business_connect.business.core import get_user_businesses
    from osduo_business_connect.subscription.entitlements import (
        get_entitlements,
        get_usage,
        has_feature,
    )

    if _is_system_manager(user):
        businesses = [
            {"name": row.name, "business_name": row.business_name, "role": "System Manager"}
            for row in frappe.get_all(
                "Business",
                filters={"status": ["!=", "Cancelled"], "docstatus": ["<", 2]},
                fields=["name", "business_name"],
            )
        ]
    else:
        businesses = get_user_businesses(user)

    names = [row["name"] for row in businesses]
    members = []
    if names:
        members = [
            {
                "name": row.name,
                "business": row.business,
                "person_name": row.person_name,
                "email": row.email,
                "role": row.role,
                "status": row.status,
            }
            for row in frappe.get_all(
                "Business Member",
                filters={"business": ["in", names]},
                fields=["name", "business", "person_name", "email", "role", "status"],
                order_by="creation desc",
                limit=200,
            )
        ]

    ent = get_entitlements()
    usage = get_usage()
    is_owner = any(row.get("role") == "Owner" for row in businesses)
    can_manage = bool(
        has_feature("team_management")
        and (_is_system_manager(user) or (INVITER_ROLE in _roles(user) and is_owner))
    )

    return {
        "can_manage": can_manage,
        "is_owner": is_owner,
        "plan": ent.get("plan_name") or ent.get("plan_code"),
        "plan_code": ent.get("plan_code"),
        "upgrade_url": ent.get("upgrade_url") or "",
        "seats": {
            "used": usage.get("seats") or 0,
            "billed": (ent.get("limits") or {}).get("seat_cap") or 0,
        },
        "businesses": businesses,
        "members": members,
        "roles": allowed_invite_roles(),
    }
