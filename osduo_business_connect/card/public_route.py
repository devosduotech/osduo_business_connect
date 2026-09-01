# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Public Card Route

This module handles the public route for Digital Cards.
"""

import frappe
from frappe import _


def get_context(context):
    """
    Get context for public card page.

    This function is called by Frappe's website route handler.
    """
    # Get slug from route
    slug = frappe.form_dict.get("card_slug")

    if not slug:
        frappe.throw(_("Card not found"), frappe.DoesNotExistError)

    # Get card by slug
    card = frappe.get_all(
        "Digital Card",
        filters={
            "slug": slug,
            "status": "Published",
            "public_profile_enabled": 1,
        },
        fields=["name"],
        limit=1,
    )

    if not card:
        frappe.throw(_("Card not found"), frappe.DoesNotExistError)

    # Get full card document
    card_doc = frappe.get_doc("Digital Card", card[0].name)

    # Get business data
    business = frappe.get_doc("Business", card_doc.business)

    # Set page context
    context.title = card_doc.display_name
    context.card = card_doc
    context.business = business
    context.meta_description = card_doc.bio or f"{card_doc.display_name} - {business.business_name}"

    # Record engagement event
    record_card_view(card_doc.name, business.name)

    return context


def record_card_view(card_name, business_name):
    """
    Record a card view engagement event.

    Args:
        card_name: Digital Card name
        business_name: Business name
    """
    try:
        # Create engagement event
        frappe.get_doc({
            "doctype": "Engagement Event",
            "business": business_name,
            "event_type": "Card View",
            "card": card_name,
            "visitor_ip": frappe.request.remote_addr if frappe.request else None,
            "visitor_user_agent": frappe.request.headers.get("User-Agent") if frappe.request else None,
        }).insert(ignore_permissions=True)

        frappe.db.commit()

    except Exception as e:
        # Log error but don't fail the page load
        frappe.log_error(
            message=f"Failed to record card view: {str(e)}",
            title="Engagement Event Failed"
        )
