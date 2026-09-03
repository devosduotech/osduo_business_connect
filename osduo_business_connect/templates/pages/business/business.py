import frappe
from frappe import _
from ....services.theme_service import get_business_theme, get_theme_variables


def get_context(context):
    """Business landing page — /b/<business_slug>"""
    slug = frappe.form_dict.get("business_slug")
    if not slug:
        frappe.throw("Business not found", frappe.DoesNotExistError)

    doc = frappe.db.get_value(
        "Business",
        {"slug": slug, "status": "Published", "public_profile_enabled": 1},
        ["name", "business_name", "legal_name", "slug", "status",
         "industry", "description", "logo", "cover_image",
         "website", "email", "phone", "whatsapp", "address",
         "city", "state", "country", "postal_code", "timezone",
         "public_profile_enabled", "seo_title", "seo_description"],
        as_dict=True,
    )

    if not doc:
        frappe.throw("Business not found", frappe.DoesNotExistError)

    context.doc = doc
    context.title = doc.get("business_name") or doc.get("name")

    # Theme
    theme_data = get_business_theme(doc.name)
    context.theme = theme_data
    context.theme_vars = get_theme_variables(theme_data)
    context.template_type = theme_data.get("template", "Modern")

    # Social links
    context.social_links = frappe.get_all(
        "Business Social Link",
        filters={"parent": doc.name, "parenttype": "Business"},
        fields=["platform", "url"],
        order_by="idx asc",
    )

    # Business hours
    context.business_hours = frappe.get_all(
        "Business Hour",
        filters={"parent": doc.name},
        fields=["day", "open_time", "close_time", "enabled", "is_24_hours"],
        order_by="idx asc",
    )

    # Members (optional)
    context.members = frappe.db.get_list(
        "Digital Card",
        filters={"business": doc.name, "status": "Published", "public_profile_enabled": 1},
        fields=["name", "display_name", "slug", "designation", "profile_image"],
        order_by="sort_order asc",
    )

    # Products
    context.products = frappe.db.get_list(
        "Showcase Product",
        filters={"business": doc.name, "status": "Published"},
        fields=["name", "product_name", "slug", "image", "short_description", "price", "currency"],
        order_by="sort_order asc",
    )

    # Services
    context.services = frappe.db.get_list(
        "Showcase Service",
        filters={"business": doc.name, "status": "Published"},
        fields=["name", "service_name", "slug", "image", "short_description"],
        order_by="sort_order asc",
    )

    # Gallery images (from products and services)
    context.gallery_images = _get_gallery_images(doc.name)

    # SEO
    if doc.get("seo_title"):
        context.title = doc["seo_title"]
    if doc.get("seo_description"):
        context.meta_description = doc["seo_description"]

    # Track profile view (non-blocking)
    analytics_ctx = _capture_analytics_context()
    _track_event(doc.name, "profile_view", **analytics_ctx)


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
        from osduo_business_connect.analytics.analytics_service import record_engagement
        frappe.enqueue(
            "osduo_business_connect.analytics.analytics_service.record_engagement",
            business=business,
            event_type=event_type,
            **kwargs,
        )
    except Exception:
        pass


def _get_gallery_images(business_name):
    """Collect gallery images from all published products and services."""
    images = []

    products = frappe.get_all(
        "Showcase Product",
        filters={"business": business_name, "status": "Published"},
        fields=["name"],
    )
    for p in products:
        doc = frappe.get_doc("Showcase Product", p.name)
        if doc.gallery:
            for item in doc.gallery:
                images.append({
                    "image": item.image,
                    "caption": item.caption,
                    "alt_text": item.alt_text,
                    "sort_order": item.sort_order or 0,
                    "source": doc.product_name,
                })

    services = frappe.get_all(
        "Showcase Service",
        filters={"business": business_name, "status": "Published"},
        fields=["name"],
    )
    for s in services:
        doc = frappe.get_doc("Showcase Service", s.name)
        if hasattr(doc, "gallery") and doc.gallery:
            for item in doc.gallery:
                images.append({
                    "image": item.image,
                    "caption": item.caption,
                    "alt_text": item.alt_text,
                    "sort_order": item.sort_order or 0,
                    "source": doc.service_name,
                })

    images.sort(key=lambda x: x["sort_order"])
    return images
