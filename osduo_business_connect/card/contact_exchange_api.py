# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Contact Exchange API.

Records the recipient of a shared card / business / product / service and
returns a pre-addressed share link for the chosen channel. Login-only: the
sender is always the authenticated owner/member, so the recipient contact is
voluntarily entered by them — never read from WhatsApp, SMS or email apps.

Share & Connect (v1.4.11) additions are deliberately backward-compatible:
``shared_content_type`` and ``request_id`` are optional trailing arguments and
historical callers keep the original positional order.
"""

import hashlib
import re
from urllib.parse import quote

import frappe
from frappe import _

from osduo_business_connect.card.my_card import get_user_card_slug
from osduo_business_connect.utils.roles import is_system_manager
from osduo_business_connect.utils.share import build_share_url
from osduo_business_connect.utils.urls import get_business_public_url, get_card_public_url

CHANNELS = ("WhatsApp", "SMS", "Email", "In-person")

# desk channel label -> utm_source value (Decision 12)
CHANNEL_UTM = {
    "WhatsApp": "whatsapp",
    "SMS": "sms",
    "Email": "email",
}

# Enquiry.source is a Select, so the exchanged contact has to map onto one of
# the sources the public enquiry form already uses.
ENQUIRY_SOURCES = {
    "card": "Digital Card",
    "product": "Product",
    "service": "Service",
}
DEFAULT_ENQUIRY_SOURCE = "Business Profile"

CONTENT_TYPES = ("Card", "Business", "Product", "Service")
CONTENT_TYPE_FIELDS = {
    "Card": "card",
    "Product": "product",
    "Service": "service",
}
CONTENT_TYPE_DOCTYPES = {
    "Card": "Digital Card",
    "Product": "Showcase Product",
    "Service": "Showcase Service",
}

# Fixed, neutral templates. No "As discussed" / "Nice connecting" phrasing.
MESSAGE_BODIES = {
    "Card": "Please find my digital business card below.",
    "Business": "Please find our business profile, products and services at the link below.",
    "Product": "Please find the details of {title} from {business_name}.\n\n"
               "Feel free to contact me for further information.",
    "Service": "Please find the details of our {title} offering.\n\n"
               "Feel free to contact me for further information.",
}

RESULT_FIELDS = (
    "name", "business", "card", "product", "service", "shared_content_type",
    "recipient_name", "recipient_phone", "recipient_email", "recipient_company",
    "channel", "event_name", "notes", "status", "user", "member",
    "linked_enquiry", "enquiry_requested", "enquiry_error",
)


def _require_login():
    if not frappe.session.user or frappe.session.user == "Guest":
        frappe.throw(_("Login required"), frappe.PermissionError)


def _clean(value, max_length=255):
    if value is None:
        return None
    value = str(value).strip()
    return value[:max_length] if value else None


def _has_field(doc, fieldname):
    meta = getattr(doc, "meta", None)
    return bool(meta and hasattr(meta, "has_field") and meta.has_field(fieldname))


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


def _normalize_content_type(value):
    value = _clean(value, 20)
    if not value:
        return None
    normalized = value[:1].upper() + value[1:].lower()
    if normalized not in CONTENT_TYPES:
        frappe.throw(_("Invalid shared content type"), frappe.ValidationError)
    return normalized


def _resolve_content_type(shared_content_type, card=None, product=None, service=None):
    """Return the explicit content type and enforce one matching typed link.

    New discriminator-aware requests must contain exactly one typed reference
    matching the selected content type (Business carries none). Legacy callers
    that omit the discriminator keep the original card > product > service
    precedence so existing integrations are not broken.
    """
    explicit = _normalize_content_type(shared_content_type)
    refs = {"Card": card, "Product": product, "Service": service}
    populated = [kind for kind, value in refs.items() if value]

    if explicit:
        selected = refs.get(explicit)
        if explicit == "Business":
            if populated:
                frappe.throw(
                    _("Business sharing cannot include a card, product or service reference"),
                    frappe.ValidationError,
                )
        elif not selected:
            frappe.throw(
                _("{0} was selected but no document was supplied").format(explicit),
                frappe.ValidationError,
            )
        elif len(populated) != 1 or populated[0] != explicit:
            frappe.throw(
                _("Selected content does not match the supplied document"),
                frappe.ValidationError,
            )
        return explicit

    # Legacy compatibility: infer from the single populated typed reference.
    if card and product and service:
        return "Card"
    if card and product:
        return "Card"
    if card and service:
        return "Card"
    if product and service:
        return "Product"
    if card:
        return "Card"
    if product:
        return "Product"
    if service:
        return "Service"
    return "Business"


def resolve_share_target(
    business,
    card=None,
    product=None,
    service=None,
    shared_content_type=None,
    user=None,
):
    """Resolve a shareable target to a single, server-derived public URL.

    Returns a plain dict so the manifest endpoint, QR endpoint and write API
    all derive URLs the same way. Client-built URLs are never trusted.
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

    kind = _resolve_content_type(shared_content_type, card, product, service)
    business_name = business_row.business_name or business_row.name

    # ?by= names the person who shared the link. Their own card wins; the page
    # slug is only the fallback for people without a card of their own.
    sharer = get_user_card_slug(business, user)

    if kind == "Card":
        row = frappe.db.get_value(
            "Digital Card",
            {"name": card, "business": business},
            ["name", "slug", "display_name", "member", "status", "public_profile_enabled"],
            as_dict=True,
        )
        if not row:
            frappe.throw(_("Digital Card not found for this business"), frappe.DoesNotExistError)
        _require_shareable(row, _("Digital Card"))
        url = get_card_public_url(row.slug)
        return {
            "content_type": kind,
            "title": row.display_name or row.name,
            "url": url,
            "public_url": url,
            "by_slug": sharer or row.slug,
            "member": row.member,
            "business_name": business_name,
        }

    if kind == "Product":
        row = frappe.db.get_value(
            "Showcase Product",
            {"name": product, "business": business},
            ["name", "slug", "product_name", "status"],
            as_dict=True,
        )
        if not row:
            frappe.throw(_("Product not found for this business"), frappe.DoesNotExistError)
        _require_shareable(row, _("Product"))
        url = f"{get_business_public_url(business_row.slug)}/products/{row.slug}"
        return {
            "content_type": kind,
            "title": row.product_name or row.name,
            "url": url,
            "public_url": url,
            "by_slug": sharer or business_row.slug,
            "member": None,
            "business_name": business_name,
        }

    if kind == "Service":
        row = frappe.db.get_value(
            "Showcase Service",
            {"name": service, "business": business},
            ["name", "slug", "service_name", "status"],
            as_dict=True,
        )
        if not row:
            frappe.throw(_("Service not found for this business"), frappe.DoesNotExistError)
        _require_shareable(row, _("Service"))
        url = f"{get_business_public_url(business_row.slug)}/services/{row.slug}"
        return {
            "content_type": kind,
            "title": row.service_name or row.name,
            "url": url,
            "public_url": url,
            "by_slug": sharer or business_row.slug,
            "member": None,
            "business_name": business_name,
        }

    url = get_business_public_url(business_row.slug)
    return {
        "content_type": "Business",
        "title": business_name,
        "url": url,
        "public_url": url,
        "by_slug": sharer or business_row.slug,
        "member": None,
        "business_name": business_name,
    }





def build_share_message(content_type, title, business_name, url, sender_name,
                        recipient_name=None):
    """Return (subject, body) for the fixed Share & Connect templates."""
    kind = _normalize_content_type(content_type) or "Business"
    body = MESSAGE_BODIES.get(kind, MESSAGE_BODIES["Business"]).format(
        title=title or "",
        business_name=business_name or "",
    )
    greeting = f"Hi {recipient_name},\n\n" if recipient_name else ""
    sender = sender_name or business_name or "OSDuo Business Connect"
    signature = f"Regards,\n{sender} | {business_name or sender}"
    text = f"{greeting}{body}\n\n{url}\n\n{signature}"
    subject = f"{title or 'Shared item'} — OSDuo Business Connect"
    return subject, text


def _attributed_url(url, channel, by_slug, campaign=None):
    """Append standard share UTM (Decision 12); In-person carries none.

    A recorded event/meeting is carried as ``utm_campaign`` so the recipient's
    card/product/service view is grouped under the same campaign. Canonical and
    printed QR/NFC URLs are never passed through this function.
    """
    utm_source = CHANNEL_UTM.get(channel)
    if not utm_source:
        return url
    return build_share_url(url, utm_source, by=by_slug, campaign=campaign)


def _build_share_link(channel, phone, email, subject, text, url, by_slug, campaign=None):
    linked_url = _attributed_url(url, channel, by_slug, campaign=campaign)
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





def _enquiry_message(exchange):
    """Human-readable note for the Enquiry timeline."""
    lines = ["Contact exchanged via {0}.".format(exchange.channel or "In-person")]
    content_type = getattr(exchange, "shared_content_type", None)
    if content_type:
        lines.append(f"Shared: {content_type}")
    if exchange.event_name:
        lines.append(f"Event / meeting: {exchange.event_name}")
    if exchange.notes:
        lines.append(f"Notes: {exchange.notes}")
    return "\n".join(lines)


def create_enquiry_from_exchange(exchange, kind=None, landing_url=None, commit=False,
                                 shared_content_type=None, reraise=False):
    """Record the exchanged contact as an **Enquiry**.

    This goes through the same service the public "Send an Enquiry" form uses
    (``enquiry.enquiry_service.create_enquiry``), so an exhibition card
    exchange gets identical validation, the same ``enquiry_submitted``
    analytics event and the same automatic CRM Lead sync as a web form
    submission. Never blocks the exchange itself unless ``reraise=True`` is
    requested by the caller that owns the savepoint.
    """
    try:
        from osduo_business_connect.enquiry.enquiry_service import create_enquiry

        source_key = (kind or "").lower()
        if source_key not in ENQUIRY_SOURCES:
            source_key = (shared_content_type or "").lower()
        source = ENQUIRY_SOURCES.get(source_key, DEFAULT_ENQUIRY_SOURCE)

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
            source=source,
            references={
                "card": exchange.card,
                "product": exchange.product,
                "service": exchange.service,
                "campaign": exchange.event_name,
                "landing_url": landing_url,
                "enquiry_origin": "Contact Exchange",
                "contact_exchange": exchange.name,
                "shared_by": exchange.user,
            },
            commit=commit,
        )

        # Enquiry adds desk-oriented advisories (visitor consent, no email or
        # phone) when it validates. They are guidance for the person filling the
        # web form, not for an owner-entered exchange, so drop what this call
        # appended instead of letting it pop as a toast on the public page.
        del frappe.local.message_log[message_count:]

        enquiry_name = result.get("name") if isinstance(result, dict) else result
        if enquiry_name:
            if _has_field(exchange, "linked_enquiry"):
                frappe.db.set_value(
                    "Contact Exchange", exchange.name, "linked_enquiry",
                    enquiry_name, update_modified=False,
                )
            if _has_field(exchange, "enquiry_error"):
                frappe.db.set_value(
                    "Contact Exchange", exchange.name, "enquiry_error",
                    None, update_modified=False,
                )
        return enquiry_name
    except Exception as exc:
        frappe.log_error(
            title="Contact Exchange Enquiry Failed",
            message=f"Exchange {getattr(exchange, 'name', '?')}: {exc}",
        )
        if not reraise and _has_field(exchange, "enquiry_error"):
            frappe.db.set_value(
                "Contact Exchange", exchange.name, "enquiry_error",
                str(exc)[:500], update_modified=False,
            )
        if reraise:
            raise
        return None


def _idempotency_key(user, request_id):
    """Stable, user-scoped key for one client submit intent."""
    return hashlib.sha256(f"{user}:{request_id}".encode()).hexdigest()


def _existing_exchange_by_key(idempotency_key):
    if not idempotency_key:
        return None
    rows = frappe.get_all(
        "Contact Exchange",
        filters={"idempotency_key": idempotency_key},
        fields=list(RESULT_FIELDS),
        limit=1,
    )
    return rows[0] if rows else None


def _payload_matches(exchange, payload):
    """Detect a reused request ID with a different submit intent."""
    for field in (
        "business", "card", "product", "service", "shared_content_type",
        "recipient_name", "recipient_phone", "recipient_email", "recipient_company",
        "channel", "event_name", "notes",
    ):
        existing = getattr(exchange, field, None) or None
        incoming = payload.get(field) or None
        if existing != incoming:
            return False
    wants = bool(payload.get("enquiry_requested"))
    return bool(getattr(exchange, "enquiry_requested", 0)) == wants


def _conflict():
    frappe.local.response["http_status_code"] = 409
    frappe.throw(_("This request ID was already used for a different share"), frappe.ValidationError)


def _result_from_exchange(exchange, idempotent=False):
    """Rebuild a response from a saved Exchange without trusting client URLs."""
    business = exchange.business
    kind = getattr(exchange, "shared_content_type", None) or _resolve_content_type(
        None, exchange.card, exchange.product, exchange.service
    )
    fallback_slug = frappe.db.get_value("Business", business, "slug") or ""
    if kind == "Card" and exchange.card:
        row = frappe.db.get_value(
            "Digital Card", {"name": exchange.card, "business": business}, "slug"
        )
        public_url = get_card_public_url(row) if row else get_business_public_url(fallback_slug)
    elif kind == "Product" and exchange.product:
        row = frappe.db.get_value(
            "Showcase Product", {"name": exchange.product, "business": business}, "slug"
        )
        public_url = (
            f"{get_business_public_url(fallback_slug)}/products/{row}"
            if row else get_business_public_url(fallback_slug)
        )
    elif kind == "Service" and exchange.service:
        row = frappe.db.get_value(
            "Showcase Service", {"name": exchange.service, "business": business}, "slug"
        )
        public_url = (
            f"{get_business_public_url(fallback_slug)}/services/{row}"
            if row else get_business_public_url(fallback_slug)
        )
    else:
        public_url = get_business_public_url(fallback_slug)

    by_slug = get_user_card_slug(business, exchange.user) or fallback_slug
    business_name = frappe.db.get_value("Business", business, "business_name") or business
    label_field = {
        "Card": "display_name",
        "Product": "product_name",
        "Service": "service_name",
    }.get(kind)
    doc_name = {
        "Card": exchange.card,
        "Product": exchange.product,
        "Service": exchange.service,
    }.get(kind)
    title = business_name
    if label_field and doc_name:
        title = frappe.db.get_value(
            CONTENT_TYPE_DOCTYPES.get(kind), doc_name, label_field
        ) or business_name
    sender_name = frappe.db.get_value("User", exchange.user, "full_name") or exchange.user
    subject, text = build_share_message(
        kind, title, business_name, public_url, sender_name,
        recipient_name=getattr(exchange, "recipient_name", None),
    )
    share_link = _build_share_link(
        exchange.channel,
        exchange.recipient_phone,
        exchange.recipient_email,
        subject,
        text,
        public_url,
        by_slug,
        campaign=exchange.event_name,
    )
    return {
        "name": exchange.name,
        "channel": exchange.channel,
        "share_url": share_link,
        "public_url": public_url,
        "enquiry": getattr(exchange, "linked_enquiry", None),
        "content_type": kind,
        "idempotent": bool(idempotent),
        "request_id": getattr(exchange, "request_id", None),
    }


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
    shared_content_type=None,
    request_id=None,
):
    """Save a contact exchange and return the pre-addressed share link.

    The caller must be an active member of the business. An Enquiry (and CRM
    Lead) is created only when ``create_enquiry`` is selected; the Exchange is
    always saved and survives an Enquiry failure. ``request_id`` gives UI
    retries an idempotent key without changing the legacy positional API.
    """
    _require_login()

    business = _clean(business, 140)
    card = _clean(card, 140)
    product = _clean(product, 140)
    service = _clean(service, 140)
    shared_content_type = _normalize_content_type(shared_content_type)
    request_id = _clean(request_id, 64)
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

    wants_enquiry = str(create_enquiry).lower() not in ("0", "false", "no", "off", "")
    payload = {
        "business": business,
        "card": card,
        "product": product,
        "service": service,
        "shared_content_type": shared_content_type,
        "recipient_name": recipient_name,
        "recipient_phone": recipient_phone,
        "recipient_email": recipient_email,
        "recipient_company": recipient_company,
        "channel": channel,
        "event_name": event_name,
        "notes": notes,
        "enquiry_requested": 1 if wants_enquiry else 0,
    }

    key = _idempotency_key(frappe.session.user, request_id) if request_id else None
    if key:
        existing = _existing_exchange_by_key(key)
        if existing:
            if not _payload_matches(existing, payload):
                _conflict()
            return _result_from_exchange(existing, idempotent=True)

    target = resolve_share_target(
        business,
        card=card,
        product=product,
        service=service,
        shared_content_type=shared_content_type,
        user=frappe.session.user,
    )

    # Normalize refs to the resolved target type. The client may carry stale
    # hidden-field values; the server-resolved target is authoritative.
    resolved_kind = target.get("content_type")
    exchange = frappe.get_doc({
        "doctype": "Contact Exchange",
        "business": business,
        "card": card if resolved_kind == "Card" else None,
        "product": product if resolved_kind == "Product" else None,
        "service": service if resolved_kind == "Service" else None,
        "member": target["member"],
        "user": frappe.session.user,
        "recipient_name": recipient_name,
        "recipient_phone": recipient_phone,
        "recipient_email": recipient_email,
        "recipient_company": recipient_company,
        "channel": channel,
        "event_name": event_name,
        "notes": notes,
        "status": "New",
    })
    if _has_field(exchange, "shared_content_type"):
        exchange.shared_content_type = target["content_type"]
    if _has_field(exchange, "request_id"):
        exchange.request_id = request_id
    if _has_field(exchange, "idempotency_key"):
        exchange.idempotency_key = key
    if _has_field(exchange, "enquiry_requested"):
        exchange.enquiry_requested = 1 if wants_enquiry else 0

    try:
        exchange.insert(ignore_permissions=True)
    except Exception:
        # A concurrent request may have won the unique-key race. Recover the
        # original row instead of creating a second Exchange.
        if key:
            existing = _existing_exchange_by_key(key)
            if existing:
                if not _payload_matches(existing, payload):
                    _conflict()
                return _result_from_exchange(existing, idempotent=True)
        raise

    enquiry_name = None
    if wants_enquiry:
        savepoint = "ce_enquiry_" + re.sub(r"[^0-9a-zA-Z_]", "_", exchange.name)
        frappe.db.savepoint(savepoint)
        try:
            enquiry_name = create_enquiry_from_exchange(
                exchange,
                kind=target["content_type"],
                landing_url=target["url"],
                commit=False,
                shared_content_type=target["content_type"],
                reraise=True,
            )
            frappe.db.release_savepoint(savepoint)
        except Exception as exc:
            frappe.db.rollback(save_point=savepoint)
            enquiry_name = None
            if _has_field(exchange, "enquiry_error"):
                frappe.db.set_value(
                    "Contact Exchange", exchange.name, "enquiry_error",
                    str(exc)[:500], update_modified=False,
                )

    # One commit boundary for the Exchange and its Enquiry. The daily recovery
    # job retries Exchanges whose Enquiry creation failed.
    if _has_field(exchange, "linked_enquiry"):
        exchange.linked_enquiry = enquiry_name
    if _has_field(exchange, "enquiry_error") and enquiry_name:
        exchange.enquiry_error = None
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
            # The event/meeting is the campaign the owner is tracking; fall back
            # to the share channel when no event was entered.
            campaign=event_name or channel,
            **capture_analytics_context(business),
        )
    except Exception:
        frappe.log_error(title="Contact Exchange analytics failed")

    result = _result_from_exchange(exchange, idempotent=False)
    if enquiry_name:
        result["enquiry"] = enquiry_name
    return result


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
            "product",
            "service",
            "shared_content_type",
            "recipient_name",
            "recipient_phone",
            "recipient_email",
            "recipient_company",
            "channel",
            "event_name",
            "notes",
            "status",
            "exchanged_at",
            "user",
            "linked_enquiry",
            "enquiry_requested",
            "enquiry_error",
        ],
        order_by="exchanged_at desc",
        limit=int(limit or 20),
    )
