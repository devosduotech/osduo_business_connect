import frappe
from ...services.theme_service import get_business_theme, get_theme_css

def get_context(context):
    """Provide context for service profile page."""
    slug = frappe.form_dict.get("service_slug")
    business_slug = frappe.form_dict.get("business_slug")

    if not slug or not business_slug:
        frappe.throw("Service not found", frappe.DoesNotExistError)

    # Find business
    business = frappe.db.get_value(
        "Business",
        {"slug": business_slug, "status": "Published"},
        ["name", "business_name", "email", "phone", "whatsapp"],
        as_dict=True,
    )
    if not business:
        frappe.throw("Business not found", frappe.DoesNotExistError)

    # Find service
    doc = frappe.db.get_value(
        "Showcase Service",
        {"slug": slug, "business": business.name, "status": "Published"},
        ["*"],
        as_dict=True,
    )
    if not doc:
        frappe.throw("Service not found", frappe.DoesNotExistError)

    context.doc = doc
    context.title = doc.get("service_name") or doc.get("name")
    context.business_slug = business_slug
    context.business_name = business.get("business_name")
    context.business_email = business.get("email")
    context.business_phone = business.get("phone")
    context.business_whatsapp = business.get("whatsapp")
    context.no_breadcrumbs = 1
    context.no_header = 1

    # Fetch theme and generate CSS
    theme_data = get_business_theme(business.name)
    context.theme = theme_data
    context.theme_css = get_theme_css(theme_data)

    # SEO
    if doc.get("seo_title"):
        context.title = doc["seo_title"]
    if doc.get("seo_description"):
        context.meta_description = doc["seo_description"]
