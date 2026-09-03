# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Enquiry Service

This module handles enquiry-related operations for businesses.
"""

import frappe
from frappe import _


def create_enquiry(business_name, visitor_data, source="Other", references=None):
    """
    Create a new enquiry.

    Args:
        business_name: Business name
        visitor_data: Dict with visitor information
        source: Enquiry source
        references: Dict with optional card/product/service references

    Returns:
        dict: Created enquiry data
    """
    # Validate business
    business = frappe.get_doc("Business", business_name)
    if business.status != "Published":
        frappe.throw("Business is not published")

    # Create enquiry
    enquiry = frappe.get_doc({
        "doctype": "Enquiry",
        "business": business_name,
        "visitor_name": visitor_data.get("name"),
        "visitor_email": visitor_data.get("email"),
        "visitor_phone": visitor_data.get("phone"),
        "visitor_company": visitor_data.get("company"),
        "message": visitor_data.get("message"),
        "source": source,
        "status": "New",
        "campaign": references.get("campaign") if references else None,
        "landing_url": references.get("landing_url") if references else None,
        "card": references.get("card") if references else None,
        "product": references.get("product") if references else None,
        "service": references.get("service") if references else None,
        "consent": visitor_data.get("consent", 0),
        "consent_text": visitor_data.get("consent_text"),
        "submitted_at": frappe.utils.now_datetime(),
    })

    # Insert enquiry
    enquiry.insert(ignore_permissions=True)
    frappe.db.commit()

    # Track event with page references
    track_enquiry_event(
        business_name, enquiry.name, source,
        card=references.get("card") if references else None,
        product=references.get("product") if references else None,
        service=references.get("service") if references else None,
    )

    # CRM sync is triggered by Enquiry.on_update hook — do not enqueue here
    # to prevent duplicate Lead creation.

    return {
        "name": enquiry.name,
        "status": enquiry.status,
        "submitted_at": enquiry.submitted_at,
    }


def track_enquiry_event(business_name, enquiry_name, source, card=None, product=None, service=None):
    """
    Track enquiry submission event with page context.

    Args:
        business_name: Business name
        enquiry_name: Enquiry name
        source: Enquiry source
        card: Digital Card name (if enquiry came from a card page)
        product: Showcase Product name (if enquiry came from a product page)
        service: Showcase Service name (if enquiry came from a service page)
    """
    try:
        from osduo_business_connect.analytics.analytics_service import record_engagement
        record_engagement(
            business=business_name,
            event_type="enquiry_submitted",
            campaign=source,
            card=card,
            product=product,
            service=service,
        )
    except Exception:
        # Don't fail enquiry creation if event tracking fails
        pass


def get_enquiry_stats(business_name):
    """
    Get enquiry statistics for a business.
    Pipeline: New → Ongoing → Converted / Lost
    """
    total = frappe.db.count("Enquiry", filters={"business": business_name})

    new_count = frappe.db.count(
        "Enquiry", filters={"business": business_name, "status": "New"}
    )

    # Ongoing = Contacted, Nurture, Qualified
    ongoing_count = frappe.db.count(
        "Enquiry", filters={"business": business_name, "status": ["in", ["Contacted", "Nurture", "Qualified"]]}
    )

    # Converted
    converted_count = frappe.db.count(
        "Enquiry", filters={"business": business_name, "status": "Converted"}
    )

    # Lost = Unqualified, Junk
    lost_count = frappe.db.count(
        "Enquiry", filters={"business": business_name, "status": ["in", ["Unqualified", "Junk"]]}
    )

    source_counts = frappe.db.sql(
        """SELECT source, COUNT(name) as cnt
        FROM `tabEnquiry`
        WHERE business = %s
        GROUP BY source""",
        (business_name,),
        as_dict=True,
    )

    return {
        "total": total,
        "new": new_count,
        "ongoing": ongoing_count,
        "converted": converted_count,
        "lost": lost_count,
        "by_source": {row.source: row.cnt for row in source_counts},
    }
