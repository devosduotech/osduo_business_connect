# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Contact Exchange API.

Records the recipient of a shared card / business / product / service and
returns a pre-addressed share link for the chosen channel. Login-only: the
sender is always the authenticated owner/member, so the recipient contact is
voluntarily entered by them — never read from WhatsApp, SMS or email apps.
"""

import re
from urllib.parse import quote

import frappe
from frappe import _

from osduo_business_connect.utils.roles import is_system_manager
from osduo_business_connect.utils.urls import get_business_public_url, get_card_public_url

CHANNELS = ("WhatsApp", "SMS", "Email", "In-person")

CHANNEL_REFS = {
    "WhatsApp": "share_whatsapp",
    "SMS": "share_sms",
    "Email": "share_email",
}


def _require_login():
    if not frappe.session.user or frappe.session.user == "Guest":
        frappe.throw(_("Login required"), frappe.PermissionError)


def _clean(value, max_length=255):
    if value is None:
        return None
    value = str(value).strip()
    return value[:max_length] if value else None


def _require_shareable(row, label):
    """Reject targets that have no working public URL yet.

    A share link built for a Draft/private record would 404 for the recipient,
    which is worse than refusing the exchange.
    """
    if not row.get("slug"):
        frappe.throw(_("{0} has no public link yet").format(label), frappe.ValidationError)
    if (row.get("status") or "Draft") != "Published":
        frappe.throw(_("{0} is not published yet").format(label), frappe.ValidationError)
    if "public_profile_enabled" in row and not row.get("public_profile_enabled"):
        frappe.throw(_("{0} is not publicly visible").format(label), frappe.ValidationError)


def _share_target(business, card=None, product=None, service=None):
    """Return (title, canonical_url, by_slug, member) for the shared item."""
    business_row = frappe.db.get_value(
        "Business",
        business,
        ["name", "slug", "business_name", "status", "public_profile_enabled"],
        as_dict=True,
    )
    if not business_row:
        frappe.throw(_("Business not found"), frappe.DoesNotExistError)
    _require_shareable(business_row, _("Business"))

    if card:
        row = frappe.db.get_value(
            "Digital Card",
            {"name": card, "business": business},
            ["name", "slug", "display_name", "member", "status", "public_profile_enabled"],
            as_dict=True,
        )
        if not row:
            frappe.throw(_("Digital Card not found for this business"), frappe.DoesNotExistError)
        _require_shareable(row, _("Digital Card"))
        return (
            row.display_name or row.name,
            get_card_public_url(row.slug),
            row.slug,
            row.member,
        )

    if product:
        row = frappe.db.get_value(
            "Showcase Product",
            {"name": product, "business": business},
            ["name", "slug", "product_name", "status"],
            as_dict=True,
        )
        if not row:
            frappe.throw(_("Product not found for this business"), frappe.DoesNotExistError)
        _require_shareable(row, _("Product"))
        return (
            row.product_name or row.name,
            f"{get_business_public_url(business_row.slug)}/products/{row.slug}",
            business_row.slug,
            None,
        )

    if service:
        row = frappe.db.get_value(
            "Showcase Service",
            {"name": service, "business": business},
            ["name", "slug", "service_name", "status"],
            as_dict=True,
        )
        if not row:
            frappe.throw(_("Service not found for this business"), frappe.DoesNotExistError)
        _require_shareable(row, _("Service"))
        return (
            row.service_name or row.name,
            f"{get_business_public_url(business_row.slug)}/services/{row.slug}",
            business_row.slug,
            None,
        )

    return (
        business_row.business_name or business_row.name,
        get_business_public_url(business_row.slug),
        business_row.slug,
        None,
    )


def _attributed_url(url, channel, by_slug):
    ref = CHANNEL_REFS.get(channel)
    if not ref:
        return url
    separator = "&" if "?" in url else "?"
    suffix = f"ref={ref}"
    if by_slug:
        suffix += f"&by={quote(str(by_slug))}"
    return f"{url}{separator}{suffix}"


def _build_share_link(channel, phone, email, subject, text, url, by_slug):
    linked_url = _attributed_url(url, channel, by_slug)
    message = f"{text} {linked_url}".strip()

    if channel == "WhatsApp":
        digits = re.sub(r"[^0-9]", "", phone or "")
        if not digits:
            return None
        return f"https://wa.me/{digits}?text={quote(message)}"

    if channel == "SMS":
        if not phone:
            return None
        return f"sms:{phone}?body={quote(message)}"

    if channel == "Email":
        if not email:
            return None
        return f"mailto:{email}?subject={quote(subject)}&body={quote(message)}"

    return None


def _maybe_create_lead(exchange):
    """Create a CRM Lead for the exchanged contact. Never blocks the exchange."""
    try:
        meta = frappe.get_meta("CRM Lead")
        full_name = exchange.recipient_name or "Unknown"
        name_parts = full_name.strip().split(" ", 1)

        lead_data = {
            "doctype": "CRM Lead",
            "first_name": name_parts[0],
            "last_name": name_parts[1] if len(name_parts) > 1 else "",
            "lead_name": full_name,
            "email": exchange.recipient_email,
            "mobile_no": exchange.recipient_phone,
            "organization": exchange.recipient_company or "",
            "source": "Business Connect",
            "status": "New",
        }

        custom_fields = {
            "osduo_business": exchange.business,
            "osduo_card": exchange.card,
            "osduo_product": exchange.product,
            "osduo_service": exchange.service,
            "osduo_source": "Contact Exchange",
            "osduo_campaign": exchange.event_name or "",
        }
        for fieldname, value in custom_fields.items():
            if meta.has_field(fieldname):
                lead_data[fieldname] = value

        if exchange.user:
            lead_data["lead_owner"] = exchange.user

        lead = frappe.get_doc(lead_data)
        lead.insert(ignore_permissions=True)
        exchange.db_set("crm_lead", lead.name, update_modified=False)
        return lead.name
    except Exception as exc:
        frappe.log_error(
            title="Contact Exchange CRM Lead Failed",
            message=f"Exchange {exchange.name}: {exc}",
        )
        return None


@frappe.whitelist()
def record_contact_exchange(
    business=None,
    card=None,
    product=None,
    service=None,
    recipient_name=None,
    recipient_phone=None,
    recipient_email=None,
    recipient_company=None,
    channel="WhatsApp",
    event_name=None,
    notes=None,
    create_lead=0,
):
    """Save a contact exchange and return the pre-addressed share link.

    The caller must be an active member of the business. ``create_lead`` is
    optional and defaults to off.
    """
    _require_login()

    business = _clean(business, 140)
    card = _clean(card, 140)
    product = _clean(product, 140)
    service = _clean(service, 140)
    recipient_name = _clean(recipient_name, 140)
    recipient_phone = _clean(recipient_phone, 40)
    recipient_email = _clean(recipient_email, 140)
    recipient_company = _clean(recipient_company, 140)
    event_name = _clean(event_name, 140)
    notes = _clean(notes, 2000)
    channel = _clean(channel, 20) or "In-person"

    if not recipient_name:
        frappe.throw(_("Recipient name is required"))
    if channel not in CHANNELS:
        frappe.throw(_("Invalid channel"))

    # Resolve the business from the shared reference when needed.
    if not business:
        if card:
            business = frappe.db.get_value("Digital Card", card, "business")
        elif product:
            business = frappe.db.get_value("Showcase Product", product, "business")
        elif service:
            business = frappe.db.get_value("Showcase Service", service, "business")
    if not business:
        frappe.throw(_("Business is required"))

    if not is_system_manager(frappe.session.user):
        from osduo_business_connect.business.core import get_user_role_in_business

        if not get_user_role_in_business(frappe.session.user, business):
            frappe.throw(_("You do not have access to this business"), frappe.PermissionError)

    title, public_url, by_slug, card_member = _share_target(
        business, card=card, product=product, service=service
    )
    subject = f"{title} — OSDuo Business Connect"
    text = f"Sharing {title}:"

    exchange = frappe.get_doc(
        {
            "doctype": "Contact Exchange",
            "business": business,
            "card": card,
            "product": product,
            "service": service,
            "member": card_member,
            "user": frappe.session.user,
            "recipient_name": recipient_name,
            "recipient_phone": recipient_phone,
            "recipient_email": recipient_email,
            "recipient_company": recipient_company,
            "channel": channel,
            "event_name": event_name,
            "notes": notes,
            "status": "New",
        }
    )
    exchange.insert(ignore_permissions=True)
    frappe.db.commit()

    # Funnel signal: this business recorded a contact exchange.
    try:
        from osduo_business_connect.analytics.tracking import (
            capture_analytics_context,
            track_event,
        )

        track_event(
            business,
            "contact_exchanged",
            card=card,
            product=product,
            service=service,
            campaign=channel,
            **capture_analytics_context(business),
        )
    except Exception:
        frappe.log_error(title="Contact Exchange analytics failed")

    lead = None
    if str(create_lead).lower() in ("1", "true", "yes", "on"):
        lead = _maybe_create_lead(exchange)

    share_link = _build_share_link(
        channel,
        exchange.recipient_phone,
        exchange.recipient_email,
        subject,
        text,
        public_url,
        by_slug,
    )

    return {
        "name": exchange.name,
        "channel": channel,
        "share_url": share_link,
        "public_url": public_url,
        "crm_lead": lead,
    }


@frappe.whitelist()
def get_contact_exchanges(business=None, limit=20):
    """List recent contact exchanges the current user may see."""
    _require_login()
    filters = {}
    if business:
        filters["business"] = business
    return frappe.get_all(
        "Contact Exchange",
        filters=filters,
        fields=[
            "name",
            "business",
            "card",
            "recipient_name",
            "recipient_phone",
            "recipient_email",
            "recipient_company",
            "channel",
            "event_name",
            "status",
            "exchanged_at",
            "crm_lead",
        ],
        order_by="exchanged_at desc",
        limit=int(limit or 20),
    )
