import frappe
from ...services.theme_service import get_business_theme, get_theme_variables

def get_context(context):
    """Provide context for product profile page."""
    slug = frappe.form_dict.get("product_slug")
    business_slug = frappe.form_dict.get("business_slug")

    if not slug or not business_slug:
        frappe.throw("Product not found", frappe.DoesNotExistError)

    # Find business
    business = frappe.db.get_value(
        "Business",
        {"slug": business_slug, "status": "Published"},
        ["name", "business_name", "email", "phone", "whatsapp"],
        as_dict=True,
    )
    if not business:
        frappe.throw("Business not found", frappe.DoesNotExistError)

    # Find product - use frappe.get_doc to get child tables (gallery)
    product_name = frappe.db.get_value(
        "Showcase Product",
        {"slug": slug, "business": business.name, "status": "Published"},
        "name",
    )
    if not product_name:
        frappe.throw("Product not found", frappe.DoesNotExistError)

    doc = frappe.get_doc("Showcase Product", product_name)

    context.doc = doc
    context.title = doc.product_name or doc.name
    context.business_slug = business_slug
    context.business_name = business.business_name
    context.business_email = business.email
    context.business_phone = business.phone
    context.business_whatsapp = business.whatsapp
    context.no_breadcrumbs = 1
    context.no_header = 1

    # Fetch theme and generate CSS variables
    theme_data = get_business_theme(business.name)
    context.theme = theme_data
    context.theme_vars = get_theme_variables(theme_data)

    # SEO
    if getattr(doc, 'seo_title', None):
        context.title = doc.seo_title
    if getattr(doc, 'seo_description', None):
        context.meta_description = doc.seo_description
