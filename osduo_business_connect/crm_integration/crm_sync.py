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

    Args:
        enquiry_name: Enquiry document name

    Returns:
        dict: Result with status and lead name
    """
    try:
        enquiry_doc = frappe.get_doc("Enquiry", enquiry_name)
    except frappe.DoesNotExistError:
        return {"status": "error", "message": f"Enquiry {enquiry_name} not found"}

    if enquiry_doc.status == "Synced":
        return {"status": "skipped", "message": "Already synced"}

    from osduo_business_connect.crm_integration.lead_mapper import create_lead_from_enquiry
    return create_lead_from_enquiry(enquiry_doc)
