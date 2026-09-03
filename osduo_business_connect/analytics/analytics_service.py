import frappe
from frappe import _


def record_engagement(business, event_type, **kwargs):
    try:
        request = frappe.request if frappe.request else None

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

        if request:
            event_data["device_type"] = detect_device_type(request)
            event_data["browser"] = detect_browser(request)

        event = frappe.get_doc(event_data)
        event.insert(ignore_permissions=True)
        frappe.db.commit()

        return {"name": event.name, "event_type": event.event_type}

    except Exception as e:
        frappe.log_error(
            message=f"Failed to record engagement: {str(e)}",
            title="Analytics Error",
        )
        return None


def detect_device_type(request):
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
    from_date = frappe.utils.add_days(frappe.utils.nowdate(), -days)

    total_events = frappe.db.count(
        "Engagement Event",
        filters={"business": business_name, "event_time": [">=", from_date]},
    )

    events_by_type = frappe.db.sql(
        """SELECT event_type, COUNT(name) as cnt
        FROM `tabEngagement Event`
        WHERE business = %s AND event_time >= %s
        GROUP BY event_type""",
        (business_name, from_date),
        as_dict=True,
    )

    events_by_day = frappe.db.sql(
        """SELECT DATE(event_time) as date, COUNT(name) as cnt
        FROM `tabEngagement Event`
        WHERE business = %s AND event_time >= %s
        GROUP BY DATE(event_time)
        ORDER BY date ASC""",
        (business_name, from_date),
        as_dict=True,
    )

    top_products = frappe.db.sql(
        """SELECT product, COUNT(name) as views
        FROM `tabEngagement Event`
        WHERE business = %s AND event_type = 'product_view' AND event_time >= %s
        GROUP BY product
        ORDER BY views DESC
        LIMIT 5""",
        (business_name, from_date),
        as_dict=True,
    )

    top_services = frappe.db.sql(
        """SELECT service, COUNT(name) as views
        FROM `tabEngagement Event`
        WHERE business = %s AND event_type = 'service_view' AND event_time >= %s
        GROUP BY service
        ORDER BY views DESC
        LIMIT 5""",
        (business_name, from_date),
        as_dict=True,
    )

    return {
        "total_events": total_events,
        "events_by_type": {row.event_type: row.cnt for row in events_by_type},
        "events_by_day": [{"date": str(row.date), "count": row.cnt} for row in events_by_day],
        "top_products": [{"product": row.product, "views": row.views} for row in top_products],
        "top_services": [{"service": row.service, "views": row.views} for row in top_services],
    }


def get_top_cards(business_name, days=30, limit=5):
    from_date = frappe.utils.add_days(frappe.utils.nowdate(), -days)

    top_cards = frappe.db.sql(
        """SELECT ee.card, bm.person_name, COUNT(ee.name) as views
        FROM `tabEngagement Event` ee
        LEFT JOIN `tabDigital Card` dc ON ee.card = dc.name
        LEFT JOIN `tabBusiness Member` bm ON dc.member = bm.name
        WHERE ee.business = %s AND ee.event_type = 'card_view' AND ee.event_time >= %s
        GROUP BY ee.card
        ORDER BY views DESC
        LIMIT %s""",
        (business_name, from_date, limit),
        as_dict=True,
    )

    return [
        {"card": row.card, "member_name": row.person_name or row.card, "views": row.views}
        for row in top_cards
    ]


def get_recent_events(business_name, days=30, limit=15):
    from_date = frappe.utils.add_days(frappe.utils.nowdate(), -days)

    events = frappe.get_all(
        "Engagement Event",
        filters={
            "business": business_name,
            "event_time": [">=", from_date],
        },
        fields=[
            "event_type",
            "event_time",
            "card",
            "product",
            "service",
            "device_type",
            "browser",
        ],
        order_by="event_time DESC",
        limit_page_length=limit,
    )

    return events
