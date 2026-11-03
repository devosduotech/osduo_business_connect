# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
My Card helpers.

Resolves the card(s) that belong to the logged-in user, either through an
active Business Member row or through Business ownership. Used by the
``/my-card`` page and the whitelisted ``get_my_cards`` endpoint.
"""

import frappe

from osduo_business_connect.utils.urls import get_card_public_url


def get_my_cards_for_user(user=None):
    """Return the logged-in user's published cards as plain dicts.

    Guest/anonymous users always get an empty list. Only published cards whose
    business is public are returned, because the returned URL is shared.
    """
    if not user:
        user = frappe.session.user
    if not user or user == "Guest":
        return []

    member_names = frappe.get_all(
        "Business Member",
        filters={"user": user, "status": "Active"},
        pluck="name",
    )
    owned_businesses = frappe.get_all(
        "Business",
        filters={"owner_user": user},
        pluck="name",
    )

    if not member_names and not owned_businesses:
        return []

    or_filters = []
    if member_names:
        or_filters.append(["member", "in", member_names])
    if owned_businesses:
        or_filters.append(["business", "in", owned_businesses])

    cards = frappe.get_all(
        "Digital Card",
        filters={
            "status": "Published",
            "public_profile_enabled": 1,
            "docstatus": ["<", 2],
        },
        or_filters=or_filters,
        fields=["name", "slug", "display_name", "designation", "business", "member"],
        order_by="sort_order asc, modified desc",
    )

    business_names = {row.business for row in cards if row.business}
    business_map = {}
    if business_names:
        for row in frappe.get_all(
            "Business",
            filters={
                "name": ["in", list(business_names)],
                "status": "Published",
                "public_profile_enabled": 1,
                "docstatus": ["<", 2],
            },
            fields=["name", "business_name", "slug"],
        ):
            business_map[row.name] = row

    result = []
    for card in cards:
        # The card page also requires a public business, so skip cards whose
        # business is still Draft/private rather than returning a 404 link.
        business = business_map.get(card.business)
        if not card.slug or not business:
            continue
        result.append(
            {
                "name": card.name,
                "slug": card.slug,
                "display_name": card.display_name or card.name,
                "designation": card.designation or "",
                "business": card.business,
                "business_name": business.get("business_name", ""),
                "business_slug": business.get("slug", ""),
                "public_url": get_card_public_url(card.slug),
            }
        )
    return result


def user_can_manage_business(business, user=None):
    """True when the user may act on behalf of this business (owner/manager/member)."""
    if not business:
        return False
    if not user:
        user = frappe.session.user
    if not user or user == "Guest":
        return False

    from osduo_business_connect.business.core import get_user_role_in_business

    return bool(get_user_role_in_business(user, business))


@frappe.whitelist()
def get_my_cards():
    """Return the current user's cards (login required)."""
    if frappe.session.user == "Guest":
        return []
    return get_my_cards_for_user(frappe.session.user)
