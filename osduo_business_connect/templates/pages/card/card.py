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
         "theme", "show_business"],
        as_dict=True,
    )
    if not doc:
        frappe.throw("Card not found", frappe.DoesNotExistError)

    context.doc = doc
    context.title = doc.get("display_name") or doc.get("name")

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

    context.meta_description = f"Contact {doc.get('display_name', '')}"
