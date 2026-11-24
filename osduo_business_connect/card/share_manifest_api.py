# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Cache-safe content manifest for Share & Connect.

Public page HTML is route-cached by Frappe, so this endpoint is the only place
that resolves the current user's permissions, card and sender identity. It
returns document IDs and canonical public URLs only — no recipient data, no
CSRF token and no client-supplied URLs.
"""

import frappe

from osduo_business_connect.utils.roles import is_system_manager

PAGE_TYPES = ("Card", "Business", "Product", "Service")
CONTENT_DOCTYPES = {
    "Card": "Digital Card",
    "Business": "Business",
    "Product": "Showcase Product",
    "Service": "Showcase Service",
}
BUSINESS_ROLES = ("Owner", "Manager", "Member")


def _set_private_headers():
    """Every response, including validation errors, is private and unstorable."""
    headers = getattr(frappe.local, "response_headers", None)
    if headers is None:
        return
    headers.set("Cache-Control", "private, no-store, max-age=0")
    headers.set("Pragma", "no-cache")
    headers.set("Expires", "0")


def _clean(value, limit=140):
    if value is None:
        return None
    value = str(value).strip()
    return value[:limit] if value else None


def _page_type(value):
    value = _clean(value, 20)
    if not value:
        return None
    normalized = value[:1].upper() + value[1:].lower()
    return normalized if normalized in PAGE_TYPES else None


def _business_key(value):
    """Accept a Business ID or slug from the cached shell.

    The shell carries a document ID, but older cached pages and hand-built
    requests may carry a slug with different casing. A failed lookup must never
    turn a public read into a 404.
    """
    if not value:
        return None
    try:
        name = frappe.db.get_value("Business", value, "name")
        if name:
            return name
        name = frappe.db.get_value("Business", {"slug": value.lower()}, "name")
        return name or None
    except Exception:
        return None


def _empty_manifest():
    """Safe response for guests and stale/unresolvable document IDs."""
    return {
        "can_record_exchange": False,
        "my_card_available": False,
        "sender": None,
        "items": [],
        "default_key": "",
    }


def _resolve():
    """Imported lazily: the shared contract lands with the API work package."""
    from osduo_business_connect.card.contact_exchange_api import resolve_share_target

    return resolve_share_target


def _item(kind, name, target, label=None, sender_name=None):
    """Build the minimal manifest item from a server-resolved target."""
    from osduo_business_connect.card.contact_exchange_api import build_share_message

    title = label or target.get("title") or name
    business_name = target.get("business_name") or ""
    subject, message = build_share_message(
        kind, title, business_name, target.get("url") or "",
        sender_name or business_name,
    )
    return {
        "key": f"{kind}:{name}",
        "doctype": CONTENT_DOCTYPES[kind],
        "name": name,
        "type": kind,
        "label": title,
        "url": target.get("url"),
        "subject": subject,
        "message": message,
    }


def _try_target(resolver, business, kind, document, user=None):
    """Resolve a target, skipping anything unpublished/sluggeless/foreign."""
    if not document:
        return None
    field = {"Card": "card", "Product": "product", "Service": "service"}.get(kind)
    kwargs = {field: document} if field else {}
    try:
        return resolver(
            business,
            shared_content_type=kind,
            user=user,
            **kwargs,
        )
    except Exception:
        # A stale manifest must never make the whole endpoint fail: only
        # published, public, slugged records are returned.
        return None


def _published_rows(doctype, business, name_field):
    return frappe.get_all(
        doctype,
        filters={
            "business": business,
            "status": "Published",
            "docstatus": ["<", 2],
        },
        fields=["name", name_field],
        order_by=f"{name_field} asc",
        limit=500,
    )


def _business_name(target, business):
    return target.get("business_name") or business


def _current_user_card(business, user, resolver):
    """Return (name, target) for this user's own published card, if any."""
    from osduo_business_connect.card.my_card import get_user_card_slug

    slug = get_user_card_slug(business, user)
    if not slug:
        return None, None
    name = frappe.db.get_value(
        "Digital Card",
        {
            "business": business,
            "slug": slug,
            "status": "Published",
            "public_profile_enabled": 1,
            "docstatus": ["<", 2],
        },
        "name",
    )
    if not name:
        return None, None
    return name, _try_target(resolver, business, "Card", name, user=user)


def _page_card(business, document, resolver):
    """Public card shown on a Card route for a guest (no user identity).

    Guests keep the normal card share outcome; this is the page's own published
    public card, not another user's private data.
    """
    if not document:
        return None, None
    name = frappe.db.get_value(
        "Digital Card",
        {
            "name": document,
            "business": business,
            "status": "Published",
            "public_profile_enabled": 1,
            "docstatus": ["<", 2],
        },
        "name",
    )
    if not name:
        return None, None
    return name, _try_target(resolver, business, "Card", name, user=None)


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_share_manifest(business=None, page_type=None, document=None):
    """Return the Share & Connect items available to the current requester."""
    _set_private_headers()

    business = _clean(business, 140)
    document = _clean(document, 140)
    kind = _page_type(page_type)

    resolver = _resolve()
    business_key = _business_key(business) or business
    business_target = _try_target(resolver, business_key, "Business", None)
    if not business_target:
        return _empty_manifest()

    business_name = _business_name(business_target, business_key)
    user = frappe.session.user if frappe.session else "Guest"
    logged_in = bool(user and user != "Guest")

    role = None
    if logged_in and not is_system_manager(user):
        from osduo_business_connect.business.core import get_user_role_in_business

        role = get_user_role_in_business(user, business)
    can_record_exchange = logged_in and (is_system_manager(user) or role in BUSINESS_ROLES)

    sender = None
    sender_name = business_name
    my_card_name = None
    page_card_name = None
    card_target = None
    if can_record_exchange:
        from osduo_business_connect.card.my_card import get_user_card_slug

        my_card_name, card_target = _current_user_card(business, user, resolver)
        full_name = frappe.db.get_value("User", user, "full_name") or user
        sender_name = full_name
        sender = {
            "name": full_name,
            "business": business_name,
            "by_slug": get_user_card_slug(business, user) or None,
        }
    elif kind == "Card":
        # Guests keep the normal public share bar, but a manifest response
        # still exposes only this page's public card and no sender identity.
        page_card_name, card_target = _page_card(business, document, resolver)

    items = [_item("Business", business, business_target,
                   label=business_name, sender_name=sender_name)]
    if my_card_name and card_target:
        items.append(_item("Card", my_card_name, card_target,
                           label="My Card", sender_name=sender_name))
    elif page_card_name and card_target:
        items.append(_item("Card", page_card_name, card_target,
                           label="Digital Card", sender_name=sender_name))

    for row in _published_rows("Showcase Product", business, "product_name"):
        target = _try_target(resolver, business, "Product", row.name)
        if target:
            items.append(_item("Product", row.name, target, sender_name=sender_name))

    for row in _published_rows("Showcase Service", business, "service_name"):
        target = _try_target(resolver, business, "Service", row.name)
        if target:
            items.append(_item("Service", row.name, target, sender_name=sender_name))

    default_key = ""
    if kind == "Business":
        default_key = f"Business:{business}"
    elif kind == "Card" and my_card_name:
        # A member's own card is the default, even when they are viewing
        # somebody else's card page.
        default_key = f"Card:{my_card_name}"
    elif kind and document:
        default_key = f"{kind}:{document}"
    if not any(item["key"] == default_key for item in items):
        default_key = items[0]["key"] if items else ""

    return {
        "can_record_exchange": bool(can_record_exchange),
        "my_card_available": bool(my_card_name),
        "sender": sender,
        "items": items,
        "default_key": default_key,
    }
