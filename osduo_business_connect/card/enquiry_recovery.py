# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Recovery for Contact Exchanges whose Enquiry creation failed.

This is deliberately separate from the daily CRM Lead retry: that job can only
retry Enquiries which already exist. Here we retry the *Enquiry creation* step
for Exchanges where the user explicitly requested an Enquiry.

Safety rules:
- Only ``enquiry_requested = 1`` rows are eligible. An unchecked checkbox is
  never turned into an Enquiry by a background job.
- Legacy rows have ``enquiry_requested = 0`` and are never picked up.
- Each row is re-checked before insert, so concurrent retries cannot create a
  second Enquiry.
"""

import frappe


def _select_pending(limit):
    """Lock a small batch of eligible Exchanges, with a portable fallback."""
    sql = """
        SELECT name
        FROM `tabContact Exchange`
        WHERE enquiry_requested = 1
          AND (linked_enquiry IS NULL OR linked_enquiry = '')
          AND docstatus < 2
        ORDER BY creation ASC
        LIMIT %s
        FOR UPDATE
    """
    try:
        return frappe.db.sql(sql, (int(limit or 100),), as_dict=True)
    except Exception:
        # Some test/SQLite setups do not accept FOR UPDATE. The re-check below
        # still prevents duplicate Enquiries.
        return frappe.db.sql(
            sql.replace("FOR UPDATE", ""), (int(limit or 100),), as_dict=True
        )


def _existing_enquiry_for_exchange(exchange_name):
    """Return an Enquiry already pointing at this Exchange, if any."""
    try:
        return frappe.db.get_value(
            "Enquiry", {"contact_exchange": exchange_name}, "name"
        )
    except Exception:
        return None


def retry_failed_enquiry_creation(limit=100):
    """Create missing Enquiries for requested-but-failed Exchange saves.

    Returns the number of Enquiries recovered. Safe to run repeatedly.
    """
    try:
        rows = _select_pending(limit)
    except Exception as exc:
        frappe.log_error(
            title="Enquiry Recovery Select Failed",
            message=str(exc),
        )
        return 0

    recovered = 0
    for row in rows:
        name = row.get("name") if isinstance(row, dict) else row[0]
        try:
            current = frappe.db.get_value(
                "Contact Exchange", name,
                ["linked_enquiry", "enquiry_error", "shared_content_type", "card",
                 "product", "service"],
                as_dict=True,
            )
            if not current or current.linked_enquiry:
                continue

            existing = _existing_enquiry_for_exchange(name)
            if existing:
                frappe.db.set_value(
                    "Contact Exchange", name, "linked_enquiry", existing,
                    update_modified=False,
                )
                frappe.db.set_value(
                    "Contact Exchange", name, "enquiry_error", None,
                    update_modified=False,
                )
                frappe.db.commit()
                continue

            exchange = frappe.get_doc("Contact Exchange", name)
            from osduo_business_connect.card.contact_exchange_api import (
                create_enquiry_from_exchange,
            )

            kind = current.shared_content_type or None
            if not kind:
                if current.card:
                    kind = "Card"
                elif current.product:
                    kind = "Product"
                elif current.service:
                    kind = "Service"
                else:
                    kind = "Business"

            enquiry_name = create_enquiry_from_exchange(
                exchange,
                kind=kind,
                landing_url=None,
                commit=False,
                shared_content_type=kind,
                reraise=False,
            )
            if enquiry_name:
                recovered += 1
            frappe.db.commit()
        except Exception as exc:
            frappe.log_error(
                title="Enquiry Recovery Failed",
                message=f"Contact Exchange {name}: {exc}",
            )
            try:
                frappe.db.rollback()
            except Exception:
                pass

    return recovered
