# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Analytics Desk Page

Provides a whitelisted API for the analytics dashboard.
"""

import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_analytics(business, days=30):
    """
    Get analytics data for a business.

    Args:
        business: Business name
        days: Number of days to look back (default 30)

    Returns:
        dict: Combined analytics and enquiry data
    """
    if not business:
        frappe.throw(_("Business is required"))

    # Verify user has access to this business
    from osduo_business_connect.business.core import get_user_businesses
    user_businesses = get_user_businesses(frappe.session.user)
    business_names = [b["name"] for b in user_businesses]

    if frappe.session.user != "Administrator" and business not in business_names:
        frappe.throw(_("You do not have access to this business"))

    days = int(days)

    # Engagement analytics
    from osduo_business_connect.analytics.analytics_service import (
        get_business_analytics,
        get_top_cards,
        get_recent_events,
    )
    engagement = get_business_analytics(business, days=days)
    engagement["qr_scans"] = get_qr_scans(business, days=days)
    engagement["recent_events"] = get_recent_events(business, days=days, limit=15)
    top_cards = get_top_cards(business, days=days, limit=5)

    # Enquiry stats
    from osduo_business_connect.enquiry.enquiry_service import get_enquiry_stats
    enquiry_stats = get_enquiry_stats(business)

    # Summary card counts
    total_cards = frappe.db.count(
        "Digital Card",
        filters={"business": business, "status": "Published"},
    )
    total_products = frappe.db.count(
        "Showcase Product",
        filters={"business": business, "status": "Published"},
    )
    total_services = frappe.db.count(
        "Showcase Service",
        filters={"business": business, "status": "Published"},
    )

    return {
        "engagement": engagement,
        "top_cards": top_cards,
        "enquiry_stats": enquiry_stats,
        "summary": {
            "total_cards": total_cards,
            "total_products": total_products,
            "total_services": total_services,
        },
        "days": days,
    }


@frappe.whitelist(allow_guest=True)
def get_business_list():
    """Get list of businesses the current user has access to."""
    from osduo_business_connect.business.core import get_user_businesses

    user = frappe.session.user
    if "System Manager" in frappe.get_roles(user):
        return frappe.get_all(
            "Business",
            filters={"status": "Published"},
            fields=["name", "business_name", "slug"],
            order_by="business_name asc",
        )

    businesses = get_user_businesses(user)
    if not businesses:
        return []

    names = [b["name"] for b in businesses]
    return frappe.get_all(
        "Business",
        filters={"name": ["in", names], "status": "Published"},
        fields=["name", "business_name", "slug"],
        order_by="business_name asc",
    )


def get_qr_scans(business, days=30):
    """Count QR code scans (qr_landing events) for a business."""
    from_date = frappe.utils.add_days(frappe.utils.nowdate(), -days)
    return frappe.db.count(
        "Engagement Event",
        filters={
            "business": business,
            "event_type": "qr_landing",
            "event_time": [">=", from_date],
        },
    )
