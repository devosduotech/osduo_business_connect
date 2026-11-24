# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
CRM Sync Module

Enqueues background jobs to sync Enquiries to CRM Leads.
"""

import frappe
from frappe import _


def _has_field(doctype, fieldname):
    """Return False when the site does not have this optional field."""
    try:
        meta = frappe.get_meta(doctype)
        return bool(meta and hasattr(meta, "has_field") and meta.has_field(fieldname))
    except Exception:
        return False


def _increment_sync_attempts(enquiry_name):
    if not _has_field("Enquiry", "crm_sync_attempts"):
        return
    try:
        current = frappe.db.get_value("Enquiry", enquiry_name, "crm_sync_attempts") or 0
        frappe.db.set_value(
            "Enquiry",
            enquiry_name,
            "crm_sync_attempts",
            int(current) + 1,
            update_modified=False,
        )
    except Exception as e:
        frappe.log_error(
            title="CRM sync attempt counter failed",
            message=f"Enquiry {enquiry_name}: {e}",
        )


def _set_last_sync_error(enquiry_name, error):
    if not _has_field("Enquiry", "last_sync_error"):
        return
    try:
        frappe.db.set_value(
            "Enquiry",
            enquiry_name,
            "last_sync_error",
            (str(error) if error else "")[:500],
            update_modified=False,
        )
    except Exception as e:
        frappe.log_error(
            title="CRM sync error recording failed",
            message=f"Enquiry {enquiry_name}: {e}",
        )


def enqueue_sync(enquiry_name):
    """
    Enqueue a background job to sync an Enquiry to a CRM Lead.

    Args:
        enquiry_name: Enquiry document name
    """
    frappe.enqueue(
        "osduo_business_connect.crm_integration.crm_sync.sync_enquiry_to_crm",
        queue="short",
        timeout=300,
        enqueue_after_commit=True,
        enquiry_name=enquiry_name,
    )


def sync_enquiry_to_crm(enquiry_name):
    """
    Sync an Enquiry to a CRM Lead. Called by background worker.

    Idempotent: checks for existing Lead before creating one.

    Args:
        enquiry_name: Enquiry document name

    Returns:
        dict: Result with status and lead name
    """
    try:
        enquiry_doc = frappe.get_doc("Enquiry", enquiry_name)
    except frappe.DoesNotExistError:
        return {"status": "error", "message": f"Enquiry {enquiry_name} not found"}

    _increment_sync_attempts(enquiry_name)

    try:
        # Idempotency check: does a CRM Lead already exist for this enquiry?
        existing_lead = getattr(enquiry_doc, "crm_lead", None)
        if not existing_lead:
            existing_lead = frappe.db.get_value(
                "CRM Lead", {"osduo_enquiry": enquiry_name}, "name"
            )

        if existing_lead:
            # Link existing lead to enquiry without creating a duplicate, then
            # let CRM remain authoritative for both statuses.
            if getattr(enquiry_doc, "crm_lead", None) != existing_lead:
                frappe.db.set_value(
                    "Enquiry", enquiry_name, "crm_lead", existing_lead,
                    update_modified=False,
                )
                frappe.db.commit()

            convergence_error = None
            try:
                from osduo_business_connect.crm_integration.status_reconciliation import (
                    sync_from_crm_lead,
                )
                outcome = sync_from_crm_lead(lead_name=existing_lead)
                if outcome and outcome.get("status") == "error":
                    convergence_error = outcome.get("message")
            except Exception as e:
                convergence_error = e
                frappe.log_error(
                    title="CRM Lead status convergence failed",
                    message=f"CRM Lead {existing_lead}: {e}",
                )

            _set_last_sync_error(enquiry_name, convergence_error)
            return {
                "status": "skipped",
                "message": f"Lead {existing_lead} already exists",
                "lead": existing_lead,
            }

        from osduo_business_connect.crm_integration.lead_mapper import create_lead_from_enquiry
        result = create_lead_from_enquiry(enquiry_doc)
        if result and result.get("status") == "success":
            _set_last_sync_error(enquiry_name, "")
        else:
            _set_last_sync_error(
                enquiry_name,
                (result or {}).get("message") or "CRM sync failed",
            )
        return result
    except Exception as e:
        _set_last_sync_error(enquiry_name, e)
        frappe.log_error(
            message=f"Failed to sync Enquiry {enquiry_name} to CRM: {e}",
            title="CRM Sync Failed",
        )
        return {"status": "error", "message": "Failed to sync Enquiry to CRM. Please try again later."}
