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

    # Page Sections (ordered, enabled, public-only)
    section_names = frappe.get_all(
        "Page Section",
        filters={"business": doc.name, "enabled": 1, "visibility": "Public"},
        fields=["name"],
        order_by="sequence asc",
    )
    context.sections = []
    for sn in section_names:
        sec = frappe.get_doc("Page Section", sn.name)
        context.sections.append(sec.get_section_data())

    # SEO
    if doc.get("seo_title"):
        context.title = doc["seo_title"]
    if doc.get("seo_description"):
        context.meta_description = doc["seo_description"]
