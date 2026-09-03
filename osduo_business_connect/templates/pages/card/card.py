import frappe
from ....services.theme_service import get_business_theme, get_theme_data, get_default_theme, get_theme_variables


def get_context(context):
    """Digital Card — /c/<card_slug>"""
    slug = frappe.form_dict.get("card_slug")
    if not slug:
        frappe.throw("Card not found", frappe.DoesNotExistError)

    doc = frappe.db.get_value(
        "Digital Card",
        {"slug": slug, "status": "Published", "public_profile_enabled": 1},
        ["name", "business", "member", "display_name", "slug",
         "designation", "profile_image", "bio", "phone", "email",
         "whatsapp", "website", "qr_enabled", "qr_image",
         "theme", "show_business", "show_products", "show_services"],
        as_dict=True,
    )
    if not doc:
        frappe.throw("Card not found", frappe.DoesNotExistError)

    # Verify associated Business is also Published + public_profile_enabled
    if doc.get("business"):
        from ....business.core import get_public_business_by_slug
        biz = frappe.db.get_value(
            "Business",
            {"name": doc["business"], "status": "Published", "public_profile_enabled": 1},
            ["name"],
        )
        if not biz:
            frappe.throw("Business not available", frappe.DoesNotExistError)

    context.doc = doc
    context.title = doc.get("display_name") or doc.get("name")

    # Card URL for sharing
    host = frappe.request.host if frappe.request else "business.local"
    protocol = "https" if frappe.request and frappe.request.scheme == "https" else "http"
    context.card_url = f"{protocol}://{host}/c/{slug}"

    # Theme — card's own, or fall back to business default
    if doc.get("theme"):
        theme_data = get_theme_data(doc.theme)
    elif doc.get("business"):
        theme_data = get_business_theme(doc.business)
    else:
        theme_data = get_default_theme()

    context.theme = theme_data
    context.theme_vars = get_theme_variables(theme_data)
    context.template_type = theme_data.get("template", "Modern")

    # Social links
    context.links = frappe.get_all(
        "Digital Card Link",
        filters={"parent": doc.name, "enabled": 1},
        fields=["link_type", "label", "value", "url"],
        order_by="sort_order asc",
    )

    # Business info
    if doc.get("business"):
        business = frappe.db.get_value(
            "Business",
            doc["business"],
            ["business_name", "slug"],
            as_dict=True,
        )
        if business:
            doc["business_name"] = business.get("business_name")
            doc["business_slug"] = business.get("slug")

    # Products (if enabled)
    context.products = []
    if doc.get("show_products") and doc.get("business"):
        context.products = frappe.get_all(
            "Showcase Product",
            filters={"business": doc["business"], "status": "Published"},
            fields=["name", "product_name", "slug", "short_description", "price", "currency", "image"],
            order_by="sort_order asc",
            limit=10,
        )

    # Services (if enabled)
    context.services = []
    if doc.get("show_services") and doc.get("business"):
        context.services = frappe.get_all(
            "Showcase Service",
            filters={"business": doc["business"], "status": "Published"},
            fields=["name", "service_name", "slug", "short_description", "image"],
            order_by="sort_order asc",
            limit=10,
        )

    # Generate VCF content
    from osduo_business_connect.services.vcard_service import generate_vcard
    context.vcf_content = generate_vcard(frappe.get_doc("Digital Card", doc.name))

    context.meta_description = f"Contact {doc.get('display_name', '')}"

    # Capture analytics context BEFORE enqueueing
    analytics_ctx = _capture_analytics_context()
    _track_event(doc.business, "card_view", card=doc.name, **analytics_ctx)


def _capture_analytics_context():
    """Extract request metadata for analytics before background job."""
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


def _track_event(business, event_type, **kwargs):
    """Record engagement event in background. Never blocks page load."""
    try:
        frappe.enqueue(
            "osduo_business_connect.analytics.analytics_service.record_engagement",
            business=business,
            event_type=event_type,
            **kwargs,
        )
    except Exception:
        pass
