# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Enquiry Webhook Handler

This module handles webhook requests for enquiry submission.
"""

import frappe
from frappe import _

from osduo_business_connect.enquiry.enquiry_service import create_enquiry


def handle_enquiry_webhook():
    """
    Handle incoming enquiry webhook request.

    Returns:
        dict: Response
    """
    try:
        # Get request data
        data = frappe.request.json
        if not data:
            return {
                "success": False,
                "error": "No data provided",
            }

        # Validate required fields
        if not data.get("business"):
            return {
                "success": False,
                "error": "Business slug is required",
            }

        if not data.get("visitor"):
            return {
                "success": False,
                "error": "Visitor information is required",
            }

        visitor = data["visitor"]
        if not visitor.get("name"):
            return {
                "success": False,
                "error": "Visitor name is required",
            }

        # Create enquiry
        result = create_enquiry(
            business_name=data["business"],
            visitor_data=visitor,
            source=data.get("source", "Other"),
            references=data.get("references"),
        )

        return {
            "success": True,
            "data": result,
        }

    except Exception as e:
        frappe.log_error(f"Enquiry webhook error: {str(e)}")
        return {
            "success": False,
            "error": "An error occurred while processing your enquiry. Please try again later.",
        }


def handle_enquiry_webhook_with_auth():
    """
    Handle incoming enquiry webhook request with API key authentication.

    Returns:
        dict: Response
    """
    # Verify API key
    api_key = frappe.request.headers.get("X-API-Key")
    if not api_key:
        return {
            "success": False,
            "error": "API key required",
        }

    # Validate API key
    # In production, this should validate against stored API keys
    # For now, we'll just check if it exists
    if not api_key:
        return {
            "success": False,
            "error": "Invalid API key",
        }

    return handle_enquiry_webhook()


def rate_limit_check(ip_address):
    """
    Check rate limiting for enquiries from same IP.

    Args:
        ip_address: IP address

    Returns:
        bool: True if allowed, False if rate limited
    """
    # Get recent enquiries from this IP
    # In production, this should use Redis or similar
    # For now, we'll just return True
    return True


def spam_check(visitor_data):
    """
    Check for spam in enquiry data.

    Args:
        visitor_data: Visitor data

    Returns:
        tuple: (is_spam, reason)
    """
    # Check for suspicious patterns
    suspicious_patterns = [
        "test",
        "spam",
        "fake",
        "xxx",
    ]

    message = (visitor_data.get("message") or "").lower()
    name = (visitor_data.get("name") or "").lower()

    for pattern in suspicious_patterns:
        if pattern in message or pattern in name:
            return True, f"Suspicious content detected: {pattern}"

    # Check for excessive links
    if message.count("http") > 3:
        return True, "Excessive links detected"

    return False, None
