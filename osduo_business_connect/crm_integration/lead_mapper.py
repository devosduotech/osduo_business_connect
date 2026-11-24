# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
CRM Lead Mapper

Maps OSDuo Business Enquiry to Frappe CRM Lead.
Single source of truth for CRM Lead creation.
"""

import frappe


def _has_field(doctype, fieldname):
    """Guard schema-dependent fields so older installs keep working."""
    try:
        meta = frappe.get_meta(doctype)
        return bool(meta and hasattr(meta, "has_field") and meta.has_field(fieldname))
    except Exception:
        return False


def _field_value(doc, fieldname):
    if doc is None:
        return None
    if isinstance(doc, dict):
        return doc.get(fieldname)
    return getattr(doc, fieldname, None)


def _linked_exchange(enquiry_doc):
    """Read the linked Contact Exchange: Enquiry link first, then reverse link."""
    if not enquiry_doc:
        return None

    exchange_name = _field_value(enquiry_doc, "contact_exchange")
    if exchange_name:
        try:
            return frappe.get_doc("Contact Exchange", exchange_name)
        except Exception:
            pass

    if _has_field("Contact Exchange", "linked_enquiry"):
        try:
            rows = frappe.get_all(
                "Contact Exchange",
                filters={"linked_enquiry": enquiry_doc.name},
                fields=["name"],
                limit=1,
            )
        except Exception:
            return None
        if rows:
            row = rows[0]
            exchange_name = (
                row.get("name") if isinstance(row, dict) else getattr(row, "name", None)
            )
            try:
                return frappe.get_doc("Contact Exchange", exchange_name)
            except Exception:
                return None
    return None


def _eligible_sender(*candidates):
    """First usable sender user; Guest is never an accountable lead owner."""
    for candidate in candidates:
        if not isinstance(candidate, str):
            continue
        user = candidate.strip()
        if user and user != "Guest":
            return user
    return None


def _card_owner_user(enquiry_doc):
    """Existing website-form ownership rule: card -> member -> user."""
    card = _field_value(enquiry_doc, "card")
    if not card:
        return None
    try:
        member_user = frappe.db.get_value(
            "Business Member",
            {"name": frappe.db.get_value("Digital Card", card, "member")},
            "user",
        )
    except Exception:
        return None
    return member_user


def _set_attribution(lead_data, meta, fieldname, value):
    """Only add a new custom field when this site actually has it."""
    if value and meta and hasattr(meta, "has_field") and meta.has_field(fieldname):
        lead_data[fieldname] = value


def create_lead_from_enquiry(enquiry_doc):
    """
    Create a CRM Lead from a Business Enquiry.

    Args:
        enquiry_doc: Enquiry document

    Returns:
        dict: Result with status and lead name
    """
    try:
        if not enquiry_doc:
            return {"status": "error", "message": "Enquiry document is required"}

        # Split name for CRM Lead (first_name is mandatory)
        full_name = enquiry_doc.visitor_name or "Unknown"
        name_parts = full_name.strip().split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        # Share & Connect enquiries belong to the sender, not to the owner of
        # the card/product/service that was shared.  Website enquiries keep the
        # existing card-owner derivation.
        exchange = _linked_exchange(enquiry_doc)
        enquiry_origin = _field_value(enquiry_doc, "enquiry_origin")
        is_exchange_origin = bool(exchange) or enquiry_origin == "Contact Exchange"
        if is_exchange_origin:
            lead_owner = _eligible_sender(
                _field_value(enquiry_doc, "shared_by"),
                _field_value(exchange, "user"),
            )
        else:
            lead_owner = _card_owner_user(enquiry_doc)

        # Build lead data with correct CRM field names
        lead_data = {
            "doctype": "CRM Lead",
            "first_name": first_name,
            "last_name": last_name,
            "lead_name": full_name,
            "email": enquiry_doc.visitor_email,
            "mobile_no": enquiry_doc.visitor_phone,
            "organization": enquiry_doc.visitor_company or "",
            "source": "Business Connect",
            "status": "New",
            # OSDuo custom fields
            "osduo_business": enquiry_doc.business,
            "osduo_card": enquiry_doc.card,
            "osduo_product": enquiry_doc.product,
            "osduo_service": enquiry_doc.service,
            "osduo_enquiry": enquiry_doc.name,
            "osduo_campaign": enquiry_doc.campaign or "",
            "osduo_source": enquiry_doc.source or "Business Profile",
            "osduo_landing_url": enquiry_doc.landing_url or "",
            # Free-text context: website form message, or the channel/event
            # notes of a contact exchange (Share & Save Contact).
            "osduo_notes": enquiry_doc.message or "",
        }

        # Share & Connect attribution is read at creation/retry time from the
        # persisted Enquiry and its linked Exchange, so an async retry keeps
        # the same context as the original submission.
        lead_meta = None
        try:
            lead_meta = frappe.get_meta("CRM Lead")
        except Exception:
            lead_meta = None
        enquiry_content_type = _field_value(enquiry_doc, "shared_content_type")
        _set_attribution(
            lead_data, lead_meta, "osduo_shared_content_type",
            _field_value(exchange, "shared_content_type") or enquiry_content_type,
        )
        _set_attribution(
            lead_data, lead_meta, "osduo_shared_by",
            _eligible_sender(
                _field_value(enquiry_doc, "shared_by"),
                _field_value(exchange, "user"),
            ),
        )
        _set_attribution(
            lead_data, lead_meta, "osduo_share_channel",
            _field_value(exchange, "channel"),
        )
        _set_attribution(
            lead_data, lead_meta, "osduo_share_event",
            _field_value(exchange, "event_name"),
        )
        _set_attribution(
            lead_data, lead_meta, "osduo_enquiry_origin",
            _field_value(enquiry_doc, "enquiry_origin"),
        )

        if lead_owner:
            lead_data["lead_owner"] = lead_owner

        lead = frappe.get_doc(lead_data)
        lead.insert(ignore_permissions=True)

        # Link CRM Lead to enquiry (status stays "New" — the CRM Lead hook
        # will update it when the lead status changes in CRM)
        enquiry_doc.crm_lead = lead.name
        enquiry_doc.save(ignore_permissions=True)

        frappe.db.commit()

        return {
            "status": "success",
            "lead": lead.name,
            "message": f"Lead {lead.name} created successfully",
        }

    except Exception as e:
        frappe.log_error(
            message=f"Failed to create CRM Lead from Enquiry {enquiry_doc.name}: {str(e)}",
            title="CRM Lead Creation Failed",
        )

        try:
            enquiry_doc.last_sync_error = str(e)[:500]
            enquiry_doc.save(ignore_permissions=True)
            frappe.db.commit()
        except Exception:
            pass

        return {"status": "error", "message": "Failed to create CRM Lead. Please try again later."}


def retry_failed_enquiries():
    """
    Retry creating CRM Leads for enquiries that failed to sync.
    Called by scheduler (daily). Uses sync_enquiry_to_crm for idempotency.

    Returns:
        int: Number of enquiries successfully synced
    """
    synced_count = 0

    enquiries = frappe.get_all(
        "Enquiry",
        filters={"status": "New", "crm_lead": ["is", "not set"]},
        fields=["name"],
        limit=100,
    )

    for enquiry in enquiries:
        try:
            from osduo_business_connect.crm_integration.crm_sync import sync_enquiry_to_crm
            result = sync_enquiry_to_crm(enquiry.name)
            if result and result.get("status") == "success":
                synced_count += 1
        except Exception as e:
            frappe.log_error(
                message=f"Failed to retry enquiry {enquiry.name}: {str(e)}",
                title="Enquiry Retry Failed",
            )

    return synced_count
