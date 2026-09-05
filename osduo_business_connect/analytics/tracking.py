# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Shared analytics tracking for public page controllers.

Extracts request metadata and enqueues engagement events.
Used by business, card, product, and service page controllers.
"""

import frappe


def capture_analytics_context():
    """Extract request metadata for analytics before background job.

    Returns:
        dict: Context with landing_url, referrer, device_type, browser
    """
    ctx = {}
    request = frappe.request if frappe.request else None
    if request:
        ctx["landing_url"] = request.url
        ctx["referrer"] = request.headers.get("Referer")
        user_agent = request.headers.get("User-Agent", "").lower()
        if any(x in user_agent for x in ["mobile", "android", "iphone"]):
            ctx["device_type"] = "Mobile"
        elif any(x in user_agent for x in ["tablet", "ipad"]):
            ctx["device_type"] = "Tablet"
        elif any(x in user_agent for x in ["mozilla", "chrome", "safari", "firefox"]):
            ctx["device_type"] = "Desktop"
        else:
            ctx["device_type"] = "Unknown"
        if "chrome" in user_agent and "edg" not in user_agent:
            ctx["browser"] = "Chrome"
        elif "firefox" in user_agent:
            ctx["browser"] = "Firefox"
        elif "safari" in user_agent and "chrome" not in user_agent:
            ctx["browser"] = "Safari"
        elif "edg" in user_agent:
            ctx["browser"] = "Edge"
        else:
            ctx["browser"] = "Unknown"
    return ctx


def track_event(business, event_type, **kwargs):
    """Record engagement event in background. Never blocks page load.

    Args:
        business: Business name
        event_type: Event type (profile_view, card_view, product_view, etc.)
        **kwargs: Additional event parameters
    """
    try:
        frappe.enqueue(
            "osduo_business_connect.analytics.analytics_service.record_engagement",
            business=business,
            event_type=event_type,
            **kwargs,
        )
    except Exception as e:
        frappe.log_error(
            title="Analytics Track Event Failed",
            message=f"Failed to enqueue {event_type} for {business}: {str(e)}",
        )
