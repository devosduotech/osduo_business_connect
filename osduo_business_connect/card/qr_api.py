# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Allowlisted QR endpoint for Share & Connect.

Only published, public, slugged documents of the four supported doctypes may
be encoded. The URL is always re-derived server-side; arbitrary URLs and IDs
are rejected. PNG bytes are cached in Redis under a doctype-qualified,
URL-hashed key and returned as a data URI, so this public read endpoint creates
no File rows and writes nothing to disk. No Card fields are changed.
"""

import base64
import hashlib

import frappe
from frappe import _

ALLOWED = {
    "Digital Card": "Card",
    "Business": "Business",
    "Showcase Product": "Product",
    "Showcase Service": "Service",
}


def _set_private_headers():
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


def _resolver():
    from osduo_business_connect.card.contact_exchange_api import resolve_share_target

    return resolve_share_target


def _get_cache():
    """Return the Redis wrapper on Frappe v14–v16."""
    cache = getattr(frappe, "cache", None)
    try:
        # v14/v15 expose a callable cache; v16 exposes the wrapper directly.
        return cache() if callable(cache) else cache
    except Exception:
        return None


def _resolve_target(doctype, name):
    """Resolve the canonical URL through the shared target contract."""
    if doctype == "Business":
        business = name
    else:
        business = frappe.db.get_value(doctype, {"name": name}, "business")
    if not business:
        frappe.throw(_("Document not found"), frappe.DoesNotExistError)

    kind = ALLOWED[doctype]
    field = {"Card": "card", "Product": "product", "Service": "service"}.get(kind)
    kwargs = {field: name} if field else {}
    target = _resolver()(
        business,
        shared_content_type=kind,
        user=None,
        **kwargs,
    )
    if not target or not target.get("url"):
        frappe.throw(_("Document is not shareable"), frappe.ValidationError)
    return target


def _generate_qr(url):
    """Return a PNG data URI. No filesystem or database write is involved."""
    try:
        from io import BytesIO

        import qrcode
    except ImportError:
        frappe.throw(
            _("QR code generation requires 'qrcode'. Please install qrcode[pil]."),
            frappe.ValidationError,
        )

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    try:
        image.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    finally:
        buffer.close()
    return "data:image/png;base64," + encoded


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_share_qr(doctype=None, name=None):
    """Return a stable, lazy QR image for one allowlisted share target."""
    _set_private_headers()

    doctype = _clean(doctype, 40)
    name = _clean(name, 140)
    if doctype not in ALLOWED or not name:
        frappe.throw(_("Unsupported QR target"), frappe.ValidationError)

    target = _resolve_target(doctype, name)
    if doctype == "Digital Card":
        qr_enabled = frappe.db.get_value("Digital Card", name, "qr_enabled")
        if not qr_enabled:
            return {"qr_image": None, "reason": "disabled"}

    url = target["url"]

    # The cache key is doctype-qualified and includes the document ID plus the
    # URL digest, so a slug/domain change cannot serve a stale QR.
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()
    cache_key = "share_qr:" + hashlib.sha256(
        f"{doctype}|{name}|{url_hash}".encode()
    ).hexdigest()

    cache = _get_cache()
    qr_image = None
    try:
        if cache is not None:
            qr_image = cache.get_value(cache_key)
    except Exception:
        cache = None
        qr_image = None

    if not qr_image:
        qr_image = _generate_qr(url)
        if cache is not None:
            try:
                cache.set_value(cache_key, qr_image, expires_in_sec=86400)
            except Exception:
                pass

    return {
        "qr_image": qr_image,
        "key": f"{target['content_type']}:{name}",
        "url": url,
    }
