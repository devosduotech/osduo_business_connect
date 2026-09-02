import frappe
from ....services.theme_service import get_business_theme, get_theme_variables


def get_context(context):
    """Product page — /b/<business_slug>/products/<product_slug>"""
    business_slug = frappe.form_dict.get("business_slug")
    product_slug = frappe.form_dict.get("product_slug")

    if not business_slug or not product_slug:
        frappe.throw("Product not found", frappe.DoesNotExistError)

    # Find business
    business = frappe.db.get_value(
        "Business",
        {"slug": business_slug, "status": "Published"},
        ["name", "business_name", "slug", "email", "phone", "whatsapp"],
        as_dict=True,
    )
    if not business:
        frappe.throw("Business not found", frappe.DoesNotExistError)

    # Find product
    product_name = frappe.db.get_value(
        "Showcase Product",
        {"slug": product_slug, "business": business.name, "status": "Published"},
        "name",
    )
    if not product_name:
        frappe.throw("Product not found", frappe.DoesNotExistError)

    doc = frappe.get_doc("Showcase Product", product_name)

    context.doc = doc
    context.title = doc.product_name or doc.name
    context.business = business
    context.business_name = business.business_name
    context.business_slug = business.slug
    context.business_email = business.email
    context.business_phone = business.phone
    context.business_whatsapp = business.whatsapp

    # Theme
    theme_data = get_business_theme(business.name)
    context.theme = theme_data
    context.theme_vars = get_theme_variables(theme_data)
    context.template_type = theme_data.get("template", "Modern")

    # SEO
    if getattr(doc, "seo_title", None):
        context.title = doc.seo_title
    if getattr(doc, "seo_description", None):
        context.meta_description = doc.seo_description

    # Track product view (non-blocking)
    _track_event(business.name, "product_view", product=doc.name)


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
