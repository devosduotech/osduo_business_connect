# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Analytics Service

Handles engagement event recording and aggregation.
"""

import frappe
from frappe import _


def record_engagement(business, event_type, **kwargs):
    """
    Record an engagement event.
    
    Args:
        business: Business name
        event_type: Type of event
        **kwargs: Additional event data (card, product, service, etc.)
        
    Returns:
        dict: Created event data or None if failed
    """
    try:
        # Get request context
        request = frappe.request if frappe.request else None
        
        # Build event data
        event_data = {
            "doctype": "Engagement Event",
            "business": business,
            "event_type": event_type,
            "event_time": frappe.utils.now_datetime(),
            "session_id": kwargs.get("session_id"),
            "card": kwargs.get("card"),
            "product": kwargs.get("product"),
            "service": kwargs.get("service"),
            "campaign": kwargs.get("campaign"),
            "landing_url": kwargs.get("landing_url"),
            "referrer": kwargs.get("referrer"),
        }
        
        # Add device info from request
        if request:
            event_data["device_type"] = detect_device_type(request)
            event_data["browser"] = detect_browser(request)
        
        # Create event
        event = frappe.get_doc(event_data)
        event.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "name": event.name,
            "event_type": event.event_type,
        }
        
    except Exception as e:
        # Don't fail the main operation for analytics
        frappe.log_error(
            message=f"Failed to record engagement: {str(e)}",
            title="Analytics Error"
        )
        return None


def detect_device_type(request):
    """
    Detect device type from user agent.
    
    Args:
        request: Flask request object
        
    Returns:
        str: Device type (Desktop, Mobile, Tablet, Unknown)
    """
    if not request:
        return "Unknown"
    
    user_agent = request.headers.get("User-Agent", "").lower()
    
    if any(x in user_agent for x in ["mobile", "android", "iphone"]):
        return "Mobile"
    elif any(x in user_agent for x in ["tablet", "ipad"]):
        return "Tablet"
    elif any(x in user_agent for x in ["mozilla", "chrome", "safari", "firefox"]):
        return "Desktop"
    
    return "Unknown"


def detect_browser(request):
    """
    Detect browser from user agent.
    
    Args:
        request: Flask request object
        
    Returns:
        str: Browser name
    """
    if not request:
        return "Unknown"
    
    user_agent = request.headers.get("User-Agent", "").lower()
    
    if "chrome" in user_agent and "edg" not in user_agent:
        return "Chrome"
    elif "firefox" in user_agent:
        return "Firefox"
    elif "safari" in user_agent and "chrome" not in user_agent:
        return "Safari"
    elif "edg" in user_agent:
        return "Edge"
    
    return "Unknown"


def get_business_analytics(business_name, days=30):
    """
    Get analytics summary for a business.
    
    Args:
        business_name: Business name
        days: Number of days to look back
        
    Returns:
        dict: Analytics summary
    """
    from_date = frappe.utils.add_days(frappe.utils.nowdate(), -days)
    
    # Total events
    total_events = frappe.db.count(
        "Engagement Event",
        filters={"business": business_name, "event_time": [">=", from_date]}
    )
    
    # Events by type
    events_by_type = frappe.get_all(
        "Engagement Event",
        filters={"business": business_name, "event_time": [">=", from_date]},
        fields=["event_type", "count(name) as count"],
        group_by="event_type",
    )
    
    # Events by day
    events_by_day = frappe.get_all(
        "Engagement Event",
        filters={"business": business_name, "event_time": [">=", from_date]},
        fields=["DATE(event_time) as date", "count(name) as count"],
        group_by="DATE(event_time)",
        order_by="date ASC",
    )
    
    # Top viewed items
    top_products = frappe.get_all(
        "Engagement Event",
        filters={
            "business": business_name,
            "event_type": "product_view",
            "event_time": [">=", from_date],
        },
        fields=["product", "count(name) as views"],
        group_by="product",
        order_by="views DESC",
        limit_page_length=5,
    )
    
    top_services = frappe.get_all(
        "Engagement Event",
        filters={
            "business": business_name,
            "event_type": "service_view",
            "event_time": [">=", from_date],
        },
        fields=["service", "count(name) as views"],
        group_by="service",
        order_by="views DESC",
        limit_page_length=5,
    )
    
    return {
        "total_events": total_events,
        "events_by_type": {row.event_type: row.count for row in events_by_type},
        "events_by_day": [{"date": str(row.date), "count": row.count} for row in events_by_day],
        "top_products": [{"product": row.product, "views": row.views} for row in top_products],
        "top_services": [{"service": row.service, "views": row.views} for row in top_services],
    }


def get_top_cards(business_name, days=30, limit=5):
    """
    Get top viewed cards for a business.
    
    Args:
        business_name: Business name
        days: Number of days to look back
        limit: Number of results to return
        
    Returns:
        list: Top cards with view counts
    """
    from_date = frappe.utils.add_days(frappe.utils.nowdate(), -days)
    
    top_cards = frappe.get_all(
        "Engagement Event",
        filters={
            "business": business_name,
            "event_type": "card_view",
            "event_time": [">=", from_date],
        },
        fields=["card", "count(name) as views"],
        group_by="card",
        order_by="views DESC",
        limit_page_length=limit,
    )
    
    return [{"card": row.card, "views": row.views} for row in top_cards]
