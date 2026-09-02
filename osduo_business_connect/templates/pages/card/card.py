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

    # Generate VCF content
    context.vcf_content = _generate_vcf(doc)

    context.meta_description = f"Contact {doc.get('display_name', '')}"


def _generate_vcf(doc):
    """Generate vCard 3.0 content for download."""
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
    ]

    name = doc.get("display_name") or ""
    parts = name.split(" ", 1)
    first_name = parts[0] if parts else ""
    last_name = parts[1] if len(parts) > 1 else ""
    lines.append(f"N:{last_name};{first_name};;;")
    lines.append(f"FN:{name}")

    if doc.get("designation"):
        lines.append(f"TITLE:{doc['designation']}")

    if doc.get("phone"):
        lines.append(f"TEL;TYPE=CELL:{doc['phone']}")

    if doc.get("email"):
        lines.append(f"EMAIL:{doc['email']}")

    if doc.get("website"):
        lines.append(f"URL:{doc['website']}")

    if doc.get("business_name"):
        lines.append(f"ORG:{doc['business_name']}")

    if doc.get("bio"):
        escaped = doc["bio"].replace("\n", "\\n")
        lines.append(f"NOTE:{escaped}")

    lines.append("END:VCARD")
    return "\r\n".join(lines)
