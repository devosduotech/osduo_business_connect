import frappe
from ....services.theme_service import get_business_theme, get_theme_variables
from ....analytics.tracking import capture_analytics_context, track_event
from ....card.my_card import get_user_card_slug
from ....utils.urls import get_business_public_url
from ....utils.share import get_share_by, get_share_ref


def get_context(context):
    """Service page — /b/<business_slug>/services/<service_slug>"""
    business_slug = frappe.form_dict.get("business_slug")
    service_slug = frappe.form_dict.get("service_slug")

    if not business_slug or not service_slug:
        frappe.throw("Service not found", frappe.DoesNotExistError)

    # Find business (requires Published + public_profile_enabled)
    from ....business.core import get_public_business_by_slug
    business = get_public_business_by_slug(business_slug)
    if not business:
        frappe.throw("Business not found", frappe.DoesNotExistError)

    # Find service
    service_name = frappe.db.get_value(
        "Showcase Service",
        {"slug": service_slug, "business": business.name, "status": "Published", "docstatus": ["<", 2]},
        "name",
    )
    if not service_name:
        frappe.throw("Service not found", frappe.DoesNotExistError)

    doc = frappe.get_doc("Showcase Service", service_name)

    context.doc = doc
    context.title = doc.service_name or doc.name
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

    # Share — attributed to the card of whoever is sharing, when they have one.
    context.share_url = f"{get_business_public_url(business.slug)}/services/{doc.slug}"
    context.share_by = get_user_card_slug(business.name) or business.slug
    context.share_title = doc.service_name or doc.name
    context.share_text = f"Check out {context.share_title} from {business.business_name or business.name}"
    context.share_ref = True

    # My Card chip — only for people who belong to this business.
    from ....business.core import get_user_role_in_business
    context.show_my_card = bool(
        frappe.session.user != "Guest"
        and get_user_role_in_business(frappe.session.user, business.name)
    )

    # Contact Exchange context
    context.ce_business = business.name
    context.ce_card = ""
    context.ce_service = doc.name

    # Capture analytics context BEFORE enqueueing
    analytics_ctx = capture_analytics_context(business.name)
    track_event(business.name, "service_view", service=doc.name, **analytics_ctx)

    share_ref = get_share_ref()
    share_by = get_share_by()
    if share_ref:
        track_event(
            business.name,
            "shared_link_open",
            service=doc.name,
            campaign=share_ref,
            shared_by=share_by,
            **analytics_ctx,
        )
