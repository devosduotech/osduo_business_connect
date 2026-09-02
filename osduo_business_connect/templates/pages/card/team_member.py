import frappe
from ....services.theme_service import get_business_theme, get_theme_variables


def get_context(context):
    """Team member page — /b/<business_slug>/team/<member_slug>"""
    business_slug = frappe.form_dict.get("business_slug")
    member_slug = frappe.form_dict.get("member_slug")

    if not business_slug or not member_slug:
        frappe.throw("Member not found", frappe.DoesNotExistError)

    # Find business
    business = frappe.db.get_value(
        "Business",
        {"slug": business_slug, "status": "Published", "public_profile_enabled": 1},
        ["name", "business_name", "slug", "email", "phone", "whatsapp"],
        as_dict=True,
    )
    if not business:
        frappe.throw("Business not found", frappe.DoesNotExistError)

    # Find member
    doc = frappe.db.get_value(
        "Digital Card",
        {"slug": member_slug, "business": business.name, "status": "Published", "public_profile_enabled": 1},
        ["name", "business", "member", "display_name", "slug",
         "designation", "profile_image", "bio", "phone", "email",
         "whatsapp", "website", "qr_enabled", "qr_image",
         "show_business"],
        as_dict=True,
    )
    if not doc:
        frappe.throw("Member not found", frappe.DoesNotExistError)

    context.doc = doc
    context.title = doc.get("display_name") or doc.get("name")
    context.business = business
    context.business_name = business.business_name
    context.business_slug = business.slug
    context.business_phone = business.phone
    context.business_whatsapp = business.whatsapp

    # Theme
    theme_data = get_business_theme(business.name)
    context.theme = theme_data
    context.theme_vars = get_theme_variables(theme_data)

    # Social links (card-level)
    context.links = frappe.get_all(
        "Digital Card Link",
        filters={"parent": doc.name, "enabled": 1},
        fields=["link_type", "label", "value", "url"],
        order_by="sort_order asc",
    )
