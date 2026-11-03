import frappe
from frappe import _
from datetime import datetime, timedelta
from ....services.theme_service import get_business_theme, get_theme_variables
from ....analytics.tracking import capture_analytics_context, track_event
from ....card.my_card import get_user_card_slug
from ....utils.urls import get_business_public_url
from ....utils.share import get_share_by, get_share_ref


def _format_hour_time(value):
    """Time fields come back as timedelta; render them as e.g. '9:00 AM'."""
    if not value:
        return ""
    if isinstance(value, timedelta):
        value = (datetime.min + value).time()
    if hasattr(value, "strftime"):
        return value.strftime("%I:%M %p").lstrip("0")
    return str(value)


def get_context(context):
    """Business landing page — /b/<business_slug>"""
    slug = frappe.form_dict.get("business_slug")
    if not slug:
        frappe.throw("Business not found", frappe.DoesNotExistError)

    doc = frappe.db.get_value(
        "Business",
        {"slug": slug, "status": "Published", "public_profile_enabled": 1, "docstatus": ["<", 2]},
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
        fields=["platform", "url", "icon_class"],
        order_by="idx asc",
    )

    # Business hours
    business_hours = frappe.get_all(
        "Business Hour",
        filters={"parent": doc.name, "parenttype": "Business", "enabled": 1},
        fields=["day", "open_time", "close_time", "is_24_hours"],
        order_by="idx asc",
    )
    for row in business_hours:
        row["open_time"] = _format_hour_time(row.get("open_time"))
        row["close_time"] = _format_hour_time(row.get("close_time"))
    context.business_hours = business_hours
    context.today = datetime.now().strftime("%A")

    # Products — public listing, so bypass per-document permissions (the page
    # itself only exposes records marked Published and not cancelled).
    context.products = frappe.get_all(
        "Showcase Product",
        filters={"business": doc.name, "status": "Published", "docstatus": ["<", 2]},
        fields=["name", "product_name", "slug", "image", "short_description",
                "price", "price_display_mode", "currency"],
        order_by="sort_order asc",
    )

    # Services
    context.services = frappe.get_all(
        "Showcase Service",
        filters={"business": doc.name, "status": "Published", "docstatus": ["<", 2]},
        fields=["name", "service_name", "slug", "image", "short_description"],
        order_by="sort_order asc",
    )

    # SEO
    if doc.get("seo_title"):
        context.title = doc["seo_title"]
    if doc.get("seo_description"):
        context.meta_description = doc["seo_description"]

    # Share — attributed to the card of whoever is sharing, when they have one.
    context.share_url = get_business_public_url(doc.get("slug"))
    context.share_by = get_user_card_slug(doc.name) or doc.get("slug")
    context.share_title = doc.get("business_name") or doc.get("name")
    context.share_text = f"Check out {context.share_title} — Business Profile"
    context.share_ref = True

    # My Card chip — only for people who belong to this business.
    from ....business.core import get_user_role_in_business
    context.show_my_card = bool(
        frappe.session.user != "Guest"
        and get_user_role_in_business(frappe.session.user, doc.name)
    )

    # Contact Exchange context
    context.ce_business = doc.name
    context.ce_card = ""

    # Track profile view (non-blocking)
    analytics_ctx = capture_analytics_context(doc.name)
    track_event(doc.name, "profile_view", **analytics_ctx)

    share_ref = get_share_ref()
    share_by = get_share_by()
    if share_ref:
        track_event(
            doc.name,
            "shared_link_open",
            campaign=share_ref,
            shared_by=share_by,
            **analytics_ctx,
        )
