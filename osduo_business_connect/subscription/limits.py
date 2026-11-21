# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Creation-time plan quota checks.

``entitlements.enforce_limit`` is the single place that turns a quota into a
plan restriction error. It was deliberately kept out of the request gate: a
quota depends on the document being inserted, so it must run in the DocType
controller (which also covers REST, ``frappe.client.insert`` and imports).
"""

import frappe

from osduo_business_connect.subscription.entitlements import enforce_limit, get_usage


def enforce_member_card_limit(doc):
    """Allow exactly one Digital Card per Business Member.

    Drafts and submitted cards count; cancelled cards do not, so amendments
    may reuse the member. Because a site's members are already capped by
    ``seat_cap``, this also keeps active cards within the purchased seat cap —
    changing ``display_name`` cannot create an extra card for the same member.
    """
    if not doc.member:
        return  # the DocType's mandatory rule reports this field error
    filters = {"member": doc.member, "docstatus": ["<", 2]}
    if not doc.is_new() and doc.name:
        filters["name"] = ["!=", doc.name]
    if frappe.db.exists("Digital Card", filters):
        frappe.throw(
            "This Business Member already has a Digital Card. "
            "Cancel the existing card before creating another one.",
            exc=frappe.ValidationError,
        )


def enforce_business_limit():
    """Block a new Business profile beyond the plan's ``max_businesses``.

    Drafts count; cancelled documents do not. Call this from
    ``Business.validate()`` on insert only — editing an existing draft that
    was already over quota (a grandfathered site) must stay possible.
    """
    enforce_limit("max_businesses", get_usage()["businesses"], "Business profiles")


def enforce_seat_limit(doc):
    """Block a new billable seat beyond the plan's ``seat_cap``.

    A seat is a distinct active Business Member whose linked User is enabled.
    Saving an existing active member without changing their user does not add
    a seat; activating a member or assigning a different user does. A user who
    already holds an active seat (possibly in another business) is not billed
    twice.
    """
    if doc.status != "Active":
        return

    previous_status, previous_user = _previous_membership(doc)

    if not doc.is_new() and previous_status == "Active" and previous_user == doc.user:
        return  # unchanged seat — an ordinary edit is always allowed

    if _has_other_active_membership(doc.user, doc.name):
        return  # this user already occupies a seat

    current = get_usage()["seats"]

    # Reassigning an active member to a different user frees the old seat,
    # so it does not consume an additional one.
    if (
        not doc.is_new()
        and previous_status == "Active"
        and previous_user
        and previous_user != doc.user
        and not _has_other_active_membership(previous_user, doc.name)
    ):
        current -= 1

    enforce_limit("seat_cap", current, "Seats")


def _previous_membership(doc):
    if doc.is_new() or not doc.name:
        return None, None
    return (
        frappe.db.get_value("Business Member", doc.name, "status"),
        frappe.db.get_value("Business Member", doc.name, "user"),
    )


def _has_other_active_membership(user, exclude_name=None):
    if not user:
        return False
    filters = {"user": user, "status": "Active"}
    if exclude_name:
        filters["name"] = ["!=", exclude_name]
    return bool(frappe.db.exists("Business Member", filters))
