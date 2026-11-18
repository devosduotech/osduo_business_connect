import frappe

from ....analytics.tracking import capture_analytics_context, track_event
from ....seo import jsonld
from ....services.theme_service import (
    get_business_theme,
    get_default_theme,
    get_root_font_size,
    get_theme_data,
    get_theme_variables,
)
from ....utils.seo import build_seo
from ....utils.share import get_share_by, get_share_ref
from ....utils.urls import get_card_public_url


def get_context(context):
    """Digital Card — /c/<card_slug>"""
    slug = frappe.form_dict.get("card_slug")
    if not slug:
        frappe.throw("Card not found", frappe.DoesNotExistError)

    doc = frappe.db.get_value(
        "Digital Card",
        {"slug": slug, "status": "Published", "public_profile_enabled": 1, "docstatus": ["<", 2]},
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
        biz = frappe.db.get_value(
            "Business",
            {"name": doc["business"], "status": "Published", "public_profile_enabled": 1, "docstatus": ["<", 2]},
            ["name"],
        )
        if not biz:
            frappe.throw("Business not available", frappe.DoesNotExistError)

    context.doc = doc
    context.title = doc.get("display_name") or doc.get("name")

    # Card URL for sharing — always the canonical URL (printed QR/NFC safety).
    context.card_url = get_card_public_url(slug)
    context.landing_url = context.card_url
    context.share_url = context.card_url
    context.share_by = slug
    context.share_title = doc.get("display_name") or doc.get("name") or "Digital Card"
    context.share_text = f"{context.share_title} — Digital Business Card"
    context.share_ref = True
    if doc.get("qr_enabled") and doc.get("qr_image"):
        context.share_qr = doc.qr_image
        context.share_qr_alt = f"QR code for {context.share_title}"

    # My Card chip — only for people who belong to this business.
    from ....business.core import get_user_role_in_business
    context.show_my_card = bool(
        frappe.session.user != "Guest"
        and doc.get("business")
        and get_user_role_in_business(frappe.session.user, doc.business)
    )

    # Contact Exchange context
    context.ce_business = doc.get("business")
    context.ce_card = doc.name

    # Theme — card's own, or fall back to business default
    if doc.get("theme"):
        theme_data = get_theme_data(doc.theme)
    elif doc.get("business"):
        theme_data = get_business_theme(doc.business)
    else:
        theme_data = get_default_theme()

    context.theme = theme_data
    context.theme_vars = get_theme_variables(theme_data)
    context.theme_root_font_size = get_root_font_size(theme_data)
    context.template_type = theme_data.get("template", "Modern")

    # Social links
    context.links = frappe.get_all(
        "Digital Card Link",
        filters={"parent": doc.name, "enabled": 1},
        fields=["link_type", "label", "value", "url", "icon_class"],
        order_by="sort_order asc",
    )

    # Business info — also feeds the SEO description/image fallbacks below.
    business = None
    if doc.get("business"):
        business = frappe.db.get_value(
            "Business",
            doc["business"],
            ["business_name", "slug", "description", "seo_description", "logo"],
            as_dict=True,
        )
        if business:
            doc["business_name"] = business.get("business_name")
            doc["business_slug"] = business.get("slug")

    # SEO — canonical / Open Graph metadata. Precedence per SEO_PLAN §C.
    card_title = doc.get("display_name") or doc.get("name")
    if doc.get("designation"):
        card_title = f"{card_title} — {doc.designation}"
    if doc.get("business_name"):
        card_title = f"{card_title} — {doc.business_name}"
    seo_description = (
        (business.get("seo_description") if business else None)
        or (business.get("description") if business else None)
        or doc.get("bio")
    )
    card_blocks = [*jsonld.vendor_blocks(), jsonld.profile_page_node(doc, business, context.links)]
    if business and business.get("slug"):
        card_blocks.append(
            jsonld.breadcrumb_node(
                [
                    (business.get("business_name") or business.get("name"), f"/b/{business['slug']}"),
                    (card_title, f"/c/{slug}"),
                ]
            )
        )

    context.seo = build_seo(
        card_title,
        seo_description,
        f"/c/{slug}",
        image=doc.get("profile_image") or (business.get("logo") if business else None),
        page_type="profile",
        business=business,
        blocks=card_blocks,
    )

    # Products (if enabled)
    context.products = []
    if doc.get("show_products") and doc.get("business"):
        context.products = frappe.get_all(
            "Showcase Product",
            filters={"business": doc["business"], "status": "Published", "docstatus": ["<", 2]},
            fields=["name", "product_name", "slug", "short_description", "price", "price_display_mode", "currency", "image", "featured"],
            order_by="featured desc, sort_order asc",
            limit=10,
        )

    # Services (if enabled)
    context.services = []
    if doc.get("show_services") and doc.get("business"):
        context.services = frappe.get_all(
            "Showcase Service",
            filters={"business": doc["business"], "status": "Published", "docstatus": ["<", 2]},
            fields=["name", "service_name", "slug", "short_description",
                    "price", "price_display_mode", "currency", "image", "featured"],
            order_by="featured desc, sort_order asc",
            limit=10,
        )

    # Generate VCF content
    from osduo_business_connect.services.vcard_service import generate_vcard
    context.vcf_content = generate_vcard(frappe.get_doc("Digital Card", doc.name))

    context.meta_description = f"Contact {doc.get('display_name', '')}"

    # Track card view (non-blocking)
    analytics_ctx = capture_analytics_context(doc.business)
    track_event(doc.business, "card_view", card=doc.name, **analytics_ctx)

    # Attribution: a share link was opened (utm_source=<channel> / legacy ?ref=)
    share_ref = get_share_ref()
    share_by = get_share_by()
    if share_ref:
        track_event(
            doc.business,
            "shared_link_open",
            card=doc.name,
            campaign=share_ref,
            shared_by=share_by,
            **analytics_ctx,
        )
