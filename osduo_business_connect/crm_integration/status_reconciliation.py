# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
CRM Lead -> Enquiry -> Contact Exchange status reconciliation.

A CRM Lead is authoritative while it exists.  Enquiry is the fallback source
for linked Contact Exchanges when no CRM Lead was created (or CRM is not
installed).  All writes in this module use ``db.set_value`` and only happen
when the stored value actually changes, so the batch helper is safe to run
repeatedly (for example hourly).
"""

import frappe

__all__ = [
    "map_crm_status",
    "reconcile_statuses",
    "sync_contact_exchange_from_enquiry",
    "sync_from_crm_lead",
]

# CRM Lead status -> Enquiry status is deliberately 1:1 (P1).
_CRM_TO_ENQUIRY_STATUS = {
    "New": "New",
    "Contacted": "Contacted",
    "Nurture": "Nurture",
    "Qualified": "Qualified",
    "Converted": "Converted",
    "Unqualified": "Unqualified",
    "Junk": "Junk",
}

# CRM Lead status -> Contact Exchange status.  Contact Exchange has a smaller,
# follow-up oriented vocabulary (P2).
_CRM_TO_EXCHANGE_STATUS = {
    "New": "New",
    "Contacted": "Contacted",
    "Nurture": "Contacted",
    "Qualified": "Qualified",
    "Converted": "Converted",
    "Unqualified": "Archived",
    "Junk": "Archived",
}

# Enquiry-only statuses also map to Contact Exchange for unlinked-CRM sites.
# Unknown/unmapped values are ignored, never coerced.
_ENQUIRY_TO_EXCHANGE_STATUS = dict(_CRM_TO_EXCHANGE_STATUS)
_ENQUIRY_TO_EXCHANGE_STATUS.update({"Closed": "Archived", "Spam": "Archived"})


def map_crm_status(crm_status, converted=False):
    """Map a CRM Lead status to ``(enquiry_status, exchange_status)``.

    ``converted=1`` is authoritative: CRM conversion may be recorded without a
    status change (and sometimes without calling a document hook), so it forces
    both statuses to ``Converted`` even when the status text is stale.
    Unknown or empty statuses return ``(None, None)`` unless converted.
    """
    if converted:
        return "Converted", "Converted"

    if crm_status is None:
        return None, None
    if not isinstance(crm_status, str):
        crm_status = str(crm_status)

    crm_status = crm_status.strip()
    return (
        _CRM_TO_ENQUIRY_STATUS.get(crm_status),
        _CRM_TO_EXCHANGE_STATUS.get(crm_status),
    )


def _has_field(doctype, fieldname):
    """Return True only when the installed site has the field/column."""
    if not doctype or not fieldname:
        return False
    try:
        meta = frappe.get_meta(doctype)
        return bool(meta and hasattr(meta, "has_field") and meta.has_field(fieldname))
    except Exception:
        return False


def _db_value(doctype, name, fieldname, filters=None):
    """Small guarded wrapper around frappe.db.get_value."""
    try:
        if filters is not None:
            return frappe.db.get_value(doctype, filters, fieldname)
        return frappe.db.get_value(doctype, name, fieldname)
    except Exception:
        return None


def _as_name(row):
    if isinstance(row, dict):
        return row.get("name")
    return getattr(row, "name", None)


def _linked_exchange_names(enquiry_name, direct_name=None):
    """All Contact Exchanges linked to an Enquiry, de-duplicated.

    The Enquiry's reverse link is checked first by callers; the Exchange's
    ``linked_enquiry`` is the fallback and also handles multiple links (P4).
    """
    names = []

    def _add(name):
        if name and isinstance(name, str) and name not in names:
            names.append(name)

    _add(direct_name)
    if enquiry_name and _has_field("Contact Exchange", "linked_enquiry"):
        try:
            rows = frappe.get_all(
                "Contact Exchange",
                filters={"linked_enquiry": enquiry_name},
                fields=["name"],
                limit=0,
            )
            for row in rows or []:
                _add(_as_name(row))
        except Exception as e:
            frappe.log_error(
                title="Contact Exchange lookup failed",
                message=f"Enquiry {enquiry_name}: {e}",
            )
    return names


def _update_exchange_statuses(exchange_names, exchange_status):
    """Set status only on Exchanges whose stored value differs. Returns count."""
    updated = 0
    if not exchange_status:
        return updated

    for exchange_name in exchange_names or []:
        current = _db_value("Contact Exchange", exchange_name, "status")
        if current == exchange_status:
            continue
        try:
            frappe.db.set_value(
                "Contact Exchange",
                exchange_name,
                "status",
                exchange_status,
                update_modified=False,
            )
            updated += 1
        except Exception as e:
            frappe.log_error(
                title="Contact Exchange status sync failed",
                message=f"Contact Exchange {exchange_name}: {e}",
            )
    return updated


def _authoritative_lead(enquiry_name):
    """Return the CRM Lead name when one owns this Enquiry's status."""
    if _has_field("Enquiry", "crm_lead"):
        lead = _db_value("Enquiry", enquiry_name, "crm_lead")
        if lead:
            return lead
    if _has_field("CRM Lead", "osduo_enquiry") and enquiry_name:
        return _db_value("CRM Lead", None, "name", {"osduo_enquiry": enquiry_name})
    return None


def sync_from_crm_lead(lead_doc=None, lead_name=None):
    """Converge an Enquiry and all its Contact Exchanges from a CRM Lead.

    Args:
        lead_doc: CRM Lead document (optional).
        lead_name: CRM Lead name (optional, used when no document is passed).

    Returns:
        dict: Status, resolved statuses and the number of documents updated.
    """
    result = {
        "status": "skipped",
        "lead": lead_name or getattr(lead_doc, "name", None),
        "enquiry": None,
        "enquiry_status": None,
        "exchange_status": None,
        "converted": False,
        "enquiry_updated": 0,
        "exchanges_checked": 0,
        "exchanges_updated": 0,
        "message": "",
    }

    try:
        name = result["lead"]
        enquiry_name = getattr(lead_doc, "osduo_enquiry", None) if lead_doc is not None else None
        if not enquiry_name and name and _has_field("CRM Lead", "osduo_enquiry"):
            enquiry_name = _db_value("CRM Lead", name, "osduo_enquiry")
        if not enquiry_name:
            result["message"] = "CRM Lead has no linked Enquiry"
            return result

        crm_status = getattr(lead_doc, "status", None) if lead_doc is not None else None
        if not crm_status and name:
            crm_status = _db_value("CRM Lead", name, "status")

        converted = bool(getattr(lead_doc, "converted", 0)) if lead_doc is not None else False
        if name and _has_field("CRM Lead", "converted"):
            converted = converted or bool(_db_value("CRM Lead", name, "converted"))
        result["converted"] = converted

        enquiry_status, exchange_status = map_crm_status(crm_status, converted=converted)
        result["enquiry"] = enquiry_name
        result["enquiry_status"] = enquiry_status
        result["exchange_status"] = exchange_status
        result["status"] = "success"

        if not enquiry_status and not exchange_status:
            result["message"] = "Unknown CRM status; nothing to reconcile"
            return result

        if enquiry_status and _db_value("Enquiry", enquiry_name, "status") != enquiry_status:
            try:
                frappe.db.set_value(
                    "Enquiry",
                    enquiry_name,
                    "status",
                    enquiry_status,
                    update_modified=False,
                )
                result["enquiry_updated"] = 1
            except Exception as e:
                frappe.log_error(
                    title="Enquiry status sync from CRM failed",
                    message=f"Enquiry {enquiry_name}: {e}",
                )

        direct_name = None
        if _has_field("Enquiry", "contact_exchange"):
            direct_name = _db_value("Enquiry", enquiry_name, "contact_exchange")
        exchange_names = _linked_exchange_names(enquiry_name, direct_name)
        result["exchanges_checked"] = len(exchange_names)
        result["exchanges_updated"] = _update_exchange_statuses(exchange_names, exchange_status)
        return result

    except Exception as e:
        frappe.log_error(
            title="CRM Lead status reconciliation failed",
            message=f"CRM Lead {result['lead']}: {e}",
        )
        result["status"] = "error"
        result["message"] = str(e)
        return result


def sync_contact_exchange_from_enquiry(enquiry_name):
    """Map Enquiry status onto linked Exchanges when no CRM Lead is authoritative.

    Returns:
        int: Number of Contact Exchanges whose status changed.
    """
    if not enquiry_name:
        return 0

    try:
        if _authoritative_lead(enquiry_name):
            return 0

        enquiry_status = _db_value("Enquiry", enquiry_name, "status")
        exchange_status = _ENQUIRY_TO_EXCHANGE_STATUS.get((enquiry_status or "").strip())
        if not exchange_status:
            return 0

        direct_name = None
        if _has_field("Enquiry", "contact_exchange"):
            direct_name = _db_value("Enquiry", enquiry_name, "contact_exchange")
        exchange_names = _linked_exchange_names(enquiry_name, direct_name)
        return _update_exchange_statuses(exchange_names, exchange_status)
    except Exception as e:
        frappe.log_error(
            title="Contact Exchange status sync from Enquiry failed",
            message=f"Enquiry {enquiry_name}: {e}",
        )
        return 0


def reconcile_statuses(limit=200):
    """Reconcile a bounded batch of CRM Lead-linked records.

    Leads are processed newest-modified first.  ``converted=1`` overrides any
    stale status text.  Returns the number of leads for which at least one
    status write occurred.
    """
    try:
        if not _has_field("CRM Lead", "osduo_enquiry"):
            return 0

        try:
            limit = max(0, int(limit))
        except (TypeError, ValueError):
            limit = 200
        if not limit:
            return 0

        leads = frappe.get_all(
            "CRM Lead",
            filters={"osduo_enquiry": ["is", "set"]},
            fields=["name"],
            order_by="modified desc, creation desc",
            limit=limit,
        )

        changed = 0
        for lead in leads or []:
            lead_name = _as_name(lead)
            if not lead_name:
                continue
            try:
                outcome = sync_from_crm_lead(lead_name=lead_name)
            except Exception as e:
                # sync_from_crm_lead should not raise, but one bad lead must
                # never abort the hourly batch.
                frappe.log_error(
                    title="CRM status reconciliation failed for lead",
                    message=f"CRM Lead {lead_name}: {e}",
                )
                continue
            if (
                outcome.get("enquiry_updated")
                or outcome.get("exchanges_updated")
            ):
                changed += 1
        return changed
    except Exception as e:
        frappe.log_error(
            title="CRM status reconciliation batch failed",
            message=str(e),
        )
        return 0
