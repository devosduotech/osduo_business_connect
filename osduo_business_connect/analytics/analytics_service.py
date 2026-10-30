import frappe
from frappe import _


def record_engagement(business, event_type, **kwargs):
    try:
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
            "device_type": kwargs.get("device_type"),
            "browser": kwargs.get("browser"),
        }

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


def _get_session_id(request):
    """Generate a session ID from request context."""
    if not request:
        return None
    user = frappe.session.user if frappe.session and frappe.session.user else "Guest"
    ip = request.remote_addr or request.headers.get("X-Forwarded-For", "unknown")
    import hashlib
    return hashlib.md5(f"{user}:{ip}".encode()).hexdigest()


def _get_landing_url(request):
    """Get the current page URL from the request."""
    if not request:
        return None
    return request.url


def _get_referrer(request):
    """Get the HTTP Referer header from the request."""
    if not request:
        return None
    return request.headers.get("Referer")


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

    events = frappe.db.sql(
        """SELECT ee.event_type, ee.event_time, ee.card, ee.device_type, ee.browser,
        bm.person_name,
        CASE WHEN sp.name IS NOT NULL THEN sp.product_name ELSE ee.product END as product_name,
        CASE WHEN ss.name IS NOT NULL THEN ss.service_name ELSE ee.service END as service_name
        FROM `tabEngagement Event` ee
        LEFT JOIN `tabDigital Card` dc ON ee.card = dc.name
        LEFT JOIN `tabBusiness Member` bm ON dc.member = bm.name
        LEFT JOIN `tabShowcase Product` sp ON ee.product = sp.name
        LEFT JOIN `tabShowcase Service` ss ON ee.service = ss.name
        WHERE ee.business = %s AND ee.event_time >= %s
        ORDER BY ee.event_time DESC
        LIMIT %s""",
        (business_name, from_date, limit),
        as_dict=True,
    )

    return events


# Event types the public card page may send via navigator.sendBeacon().
CLIENT_EVENT_TYPES = {
    "card_view",
    "product_view",
    "service_view",
    "phone_click",
    "email_click",
    "whatsapp_click",
    "website_click",
    "brochure_download",
    "qr_landing",
    "enquiry_submitted",
}

# Light abuse guard: at most 60 client events per IP per minute.
CLIENT_EVENT_RATE_LIMIT = 60
CLIENT_EVENT_RATE_WINDOW = 60


def _clean_str(value, max_length=255):
    if value is None:
        return None
    value = str(value).strip()
    return value[:max_length] if value else None


def _client_rate_allowed():
    try:
        ip = frappe.local.request_ip or "127.0.0.1"
    except Exception:
        ip = "127.0.0.1"
    cache_key = f"bc_evt_rl:{ip}"
    try:
        count = frappe.cache.get_value(cache_key) or 0
        if count >= CLIENT_EVENT_RATE_LIMIT:
            return False
        frappe.cache.set_value(cache_key, count + 1, expires_in_sec=CLIENT_EVENT_RATE_WINDOW)
    except Exception:
        pass
    return True


@frappe.whitelist(allow_guest=True)
def log_event(business=None, event_type=None, card=None, product=None, service=None,
              campaign=None, landing_url=None, referrer=None, session_id=None):
    """Record a lightweight client-side engagement event.

    Called from public pages with navigator.sendBeacon(). Guest-safe and
    rate limited; never raises to the browser.
    """
    try:
        business = _clean_str(business)
        event_type = _clean_str(event_type, 40)

        if not business or not event_type:
            return {"ok": False, "error": "missing_fields"}
        if event_type not in CLIENT_EVENT_TYPES:
            return {"ok": False, "error": "invalid_event_type"}
        if not _client_rate_allowed():
            return {"ok": False, "error": "rate_limited"}
        if not frappe.db.exists("Business", business):
            return {"ok": False, "error": "invalid_business"}

        request = frappe.request
        ctx = {}
        try:
            from osduo_business_connect.analytics.tracking import capture_analytics_context
            ctx = capture_analytics_context()
        except Exception:
            ctx = {}

        result = record_engagement(
            business,
            event_type,
            card=_clean_str(card, 140),
            product=_clean_str(product, 140),
            service=_clean_str(service, 140),
            campaign=_clean_str(campaign, 140),
            landing_url=_clean_str(landing_url or ctx.get("landing_url"), 500),
            referrer=_clean_str(referrer or ctx.get("referrer"), 500),
            device_type=ctx.get("device_type") or detect_device_type(request),
            browser=ctx.get("browser") or detect_browser(request),
            session_id=_clean_str(session_id) or _get_session_id(request),
        )
        return {"ok": bool(result)}
    except Exception as e:
        frappe.log_error(
            message=f"Client analytics event failed: {str(e)}",
            title="Analytics Client Event Error",
        )
        return {"ok": False, "error": "server_error"}
