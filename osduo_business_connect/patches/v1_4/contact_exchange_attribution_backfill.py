# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Backfill attribution for legacy Contact Exchanges and Enquiries.

Registered as a post-model-sync patch, so the new DocType fields already exist.
Only empty values are filled: a curator/caller's explicit choice is never
overwritten, and CRM Leads are deliberately left alone. All writes use
``db.set_value(..., update_modified=False)`` to avoid controller recursion and
spurious modification stamps. Re-running the patch is a no-op.
"""

import frappe

CONTENT_TYPE_FIELDS = ("card", "product", "service")
CONTENT_TYPE_LABELS = {"card": "Card", "product": "Product", "service": "Service"}


def _has_column(doctype, fieldname):
    """Tolerate running the patch before model sync on an un-migrated site."""
    has_column = getattr(frappe.db, "has_column", None)
    return bool(has_column(doctype, fieldname)) if has_column else True


def _is_set(value):
    return bool((value or "").strip())


def _classify_exchanges():
    """Set shared_content_type only where the typed links are unambiguous."""
    if not _has_column("Contact Exchange", "shared_content_type"):
        return

    exchanges = frappe.get_all(
        "Contact Exchange",
        filters={"shared_content_type": ("is", "not set")},
        fields=["name", "card", "product", "service"],
    )
    for exchange in exchanges:
        typed = [field for field in CONTENT_TYPE_FIELDS if _is_set(exchange.get(field))]
        if len(typed) > 1:
            # Card + product, product + service, etc. cannot be classified
            # safely; leave the legacy row unclassified.
            continue
        content_type = CONTENT_TYPE_LABELS.get(typed[0]) if typed else "Business"
        frappe.db.set_value(
            "Contact Exchange",
            exchange.name,
            "shared_content_type",
            content_type,
            update_modified=False,
        )


def _reliable_exchanges():
    """Map an Enquiry to its Exchange only for a strict one-to-one link."""
    if not _has_column("Contact Exchange", "linked_enquiry"):
        return {}

    exchanges = frappe.get_all(
        "Contact Exchange",
        filters={"linked_enquiry": ("is", "set")},
        fields=["name", "linked_enquiry", "user"],
    )
    counts = {}
    for exchange in exchanges:
        enquiry = exchange.linked_enquiry
        counts[enquiry] = counts.get(enquiry, 0) + 1
    return {
        exchange.linked_enquiry: exchange
        for exchange in exchanges
        if counts[exchange.linked_enquiry] == 1
    }


def _backfill_enquiries():
    if not _has_column("Enquiry", "enquiry_origin"):
        return

    reliable = _reliable_exchanges()
    if reliable:
        enquiries = frappe.get_all(
            "Enquiry",
            filters={"name": ["in", list(reliable)]},
            fields=["name", "contact_exchange", "shared_by", "enquiry_origin"],
        )
        for enquiry in enquiries:
            exchange = reliable.get(enquiry.name)
            if not exchange:
                continue
            updates = {}
            if not enquiry.contact_exchange and _has_column("Enquiry", "contact_exchange"):
                updates["contact_exchange"] = exchange.name
            if not enquiry.shared_by and _has_column("Enquiry", "shared_by"):
                if _is_set(exchange.get("user")):
                    updates["shared_by"] = exchange.user
            if not enquiry.enquiry_origin:
                updates["enquiry_origin"] = "Contact Exchange"
            if updates:
                frappe.db.set_value(
                    "Enquiry", enquiry.name, updates, update_modified=False
                )

    # Historical enquiries without a trustworthy Exchange link keep their
    # existing origin (if any); empty ones are marked Unknown, never guessed
    # as Website Form.
    unclassified = frappe.get_all(
        "Enquiry",
        filters={"enquiry_origin": ("is", "not set")},
        pluck="name",
    )
    for name in unclassified:
        if name in reliable:
            continue
        frappe.db.set_value(
            "Enquiry", name, "enquiry_origin", "Unknown", update_modified=False
        )


def execute():
    _classify_exchanges()
    _backfill_enquiries()
    # No explicit commit: bench migrate wraps each patch phase atomically.
