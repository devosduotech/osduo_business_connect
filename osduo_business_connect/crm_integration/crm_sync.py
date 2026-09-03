# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
CRM Sync Module

Enqueues background jobs to sync Enquiries to CRM Leads.
"""

import frappe
from frappe import _


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

    # Already synced — skip
    if enquiry_doc.crm_lead:
        return {"status": "skipped", "message": "Already synced"}

    # Idempotency check: does a CRM Lead already exist for this enquiry?
    existing_lead = frappe.db.get_value(
        "CRM Lead", {"osduo_enquiry": enquiry_name}, "name"
    )
    if existing_lead:
        # Link existing lead to enquiry and skip creation
        frappe.db.set_value("Enquiry", enquiry_name, "crm_lead", existing_lead)
        frappe.db.commit()
        return {"status": "skipped", "message": f"Lead {existing_lead} already exists"}

    from osduo_business_connect.crm_integration.lead_mapper import create_lead_from_enquiry
    return create_lead_from_enquiry(enquiry_doc)
