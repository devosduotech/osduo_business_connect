# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Public API for Enquiries.

This module provides API functions for public enquiry submission.
"""

import frappe
from frappe import _

from osduo_business_connect.enquiry.enquiry_service import create_enquiry


@frappe.whitelist(allow_guest=True)
def submit_enquiry(business_slug, visitor_data, source="Other", references=None):
    """
    Submit a public enquiry.

    Args:
        business_slug: Business slug
        visitor_data: Dict or JSON string with visitor information
        source: Enquiry source
        references: Dict or JSON string with optional card/product/service references

    Returns:
        dict: Submission result
    """
    # Parse JSON strings if needed
    if isinstance(visitor_data, str):
        import json
        visitor_data = json.loads(visitor_data)
    if isinstance(references, str):
        import json
        references = json.loads(references)
    # Get business by slug
    business = frappe.get_all(
        "Business",
        filters={"slug": business_slug, "status": "Published"},
        fields=["name"],
        limit=1,
    )
    if not business:
        frappe.throw(_("Business not found"), frappe.DoesNotExistError)

    # Validate required fields
    if not visitor_data.get("name"):
        frappe.throw(_("Visitor name is required"))

    # Validate email format if provided
    if visitor_data.get("email"):
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, visitor_data["email"]):
            frappe.throw(_("Invalid email address"))

    # Validate phone format if provided
    if visitor_data.get("phone"):
        phone = visitor_data["phone"].replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not phone.isdigit() and not phone.startswith("+"):
            frappe.throw(_("Invalid phone number"))

    # Create enquiry
    result = create_enquiry(
        business_name=business[0].name,
        visitor_data=visitor_data,
        source=source,
        references=references,
    )

    return result


def get_enquiry_form_config(business_slug):
    """
    Get enquiry form configuration for a business.

    Args:
        business_slug: Business slug

    Returns:
        dict: Form configuration
    """
    # Get business by slug
    business = frappe.get_all(
        "Business",
        filters={"slug": business_slug, "status": "Published"},
        fields=["name", "business_name"],
        limit=1,
    )
    if not business:
        frappe.throw(_("Business not found"), frappe.DoesNotExistError)

    # Get business enquiry settings
    business_doc = frappe.get_doc("Business", business[0].name)

    return {
        "business_name": business_doc.business_name,
        "consent_text": "I agree to be contacted regarding my enquiry.",
        "required_fields": ["name", "email"],
        "optional_fields": ["phone", "company", "message"],
    }


def validate_enquiry_data(data):
    """
    Validate enquiry data.

    Args:
        data: Dict with enquiry data

    Returns:
        tuple: (is_valid, errors)
    """
    errors = []

    # Check required fields
    if not data.get("name"):
        errors.append("Visitor name is required")

    # Validate email if provided
    if data.get("email"):
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data["email"]):
            errors.append("Invalid email address")

    # Validate phone if provided
    if data.get("phone"):
        phone = data["phone"].replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not phone.isdigit() and not phone.startswith("+"):
            errors.append("Invalid phone number")

    # Check message length
    if data.get("message") and len(data["message"]) > 5000:
        errors.append("Message is too long (maximum 5000 characters)")

    return len(errors) == 0, errors
