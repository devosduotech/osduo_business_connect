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

from osduo_business_connect.card.my_card import get_user_card_slug
from osduo_business_connect.utils.roles import is_system_manager
from osduo_business_connect.utils.urls import get_business_public_url, get_card_public_url

CHANNELS = ("WhatsApp", "SMS", "Email", "In-person")

CHANNEL_REFS = {
    "WhatsApp": "share_whatsapp",
    "SMS": "share_sms",
    "Email": "share_email",
}

# Enquiry.source is a Select, so the exchanged contact has to map onto one of
# the sources the public enquiry form already uses.
ENQUIRY_SOURCES = {
    "card": "Digital Card",
    "product": "Product",
    "service": "Service",
}
DEFAULT_ENQUIRY_SOURCE = "Business Profile"


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


def _share_target(business, card=None, product=None, service=None, user=None):
    """Return (title, canonical_url, by_slug, member) for the shared item.

    ``by_slug`` names who shared it, so it prefers the acting user's own card
    and only falls back to the page's slug when they have no card.
    """
    business_row = frappe.db.get_value(
        "Business",
        business,
        ["name", "slug", "business_name", "status", "public_profile_enabled"],
        as_dict=True,
    )
    if not business_row:
        frappe.throw(_("Business not found"), frappe.DoesNotExistError)
    _require_shareable(business_row, _("Business"))

    # ?by= is meant to name the person who shared the link, so their own card
    # wins; the page slug below is only the fallback for people without a card.
    sharer = get_user_card_slug(business, user)

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
            sharer or row.slug,
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
            sharer or business_row.slug,
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
            sharer or business_row.slug,
            None,
        )

    return (
        business_row.business_name or business_row.name,
        get_business_public_url(business_row.slug),
        sharer or business_row.slug,
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


def _target_kind(card=None, product=None, service=None):
    """Which public page this exchange came from — also picks Enquiry.source."""
    if card:
        return "card"
    if product:
        return "product"
    if service:
        return "service"
    return "business"


def _enquiry_message(exchange):
    """Human-readable note for the Enquiry timeline."""
    lines = [f"Contact exchanged via {exchange.channel}."]
    if exchange.event_name:
        lines.append(f"Event / meeting: {exchange.event_name}")
    if exchange.notes:
        lines.append(f"Notes: {exchange.notes}")
    return "\n".join(lines)


def create_enquiry_from_exchange(exchange, kind, landing_url=None):
    """Record the exchanged contact as an **Enquiry**.

    This goes through the same service the public "Send an Enquiry" form uses
    (``enquiry.enquiry_service.create_enquiry``), so an exhibition card
    exchange gets identical validation, the same ``enquiry_submitted``
    analytics event and the same automatic CRM Lead sync as a web form
    submission. Never blocks the exchange itself.
    """
    try:
        from osduo_business_connect.enquiry.enquiry_service import create_enquiry

        # A web request always has this list; keep it safe outside one.
        frappe.local.message_log = getattr(frappe.local, "message_log", None) or []
        message_count = len(frappe.local.message_log)
        result = create_enquiry(
            business_name=exchange.business,
            visitor_data={
                "name": exchange.recipient_name,
                "email": exchange.recipient_email,
                "phone": exchange.recipient_phone,
                "company": exchange.recipient_company,
                "message": _enquiry_message(exchange),
                "consent": 0,
                "consent_text": "Contact given to the business directly; not a web form submission.",
            },
            source=ENQUIRY_SOURCES.get(kind, DEFAULT_ENQUIRY_SOURCE),
            references={
                "card": exchange.card,
                "product": exchange.product,
                "service": exchange.service,
                "campaign": exchange.event_name,
                "landing_url": landing_url,
            },
        )

        # Enquiry adds desk-oriented advisories (visitor consent, no email or
        # phone) when it validates. They are guidance for the person filling the
        # web form, not for an owner-entered exchange, so drop what this call
        # appended instead of letting it pop as a toast on the public page.
        del frappe.local.message_log[message_count:]

        enquiry_name = result.get("name") if isinstance(result, dict) else result
        if enquiry_name:
            exchange.db_set("linked_enquiry", enquiry_name, update_modified=False)
        return enquiry_name
    except Exception as exc:
        frappe.log_error(
            title="Contact Exchange Enquiry Failed",
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
    create_enquiry=1,
):
    """Save a contact exchange and return the pre-addressed share link.

    The caller must be an active member of the business. Every exchange is also
    recorded as an **Enquiry** (``create_enquiry=0`` opts out), so card contacts
    captured at an event follow the same pipeline as the public enquiry form and
    reach CRM through it.
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

    kind = _target_kind(card, product, service)
    enquiry_name = None
    if str(create_enquiry).lower() not in ("0", "false", "no", "off", ""):
        enquiry_name = create_enquiry_from_exchange(exchange, kind, landing_url=public_url)

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
        "enquiry": enquiry_name,
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
            "user",
            "linked_enquiry",
        ],
        order_by="exchanged_at desc",
        limit=int(limit or 20),
    )
