# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
CRM Lead Mapper

This module handles the mapping between OSDuo Business Enquiry and Frappe CRM Lead.
It provides functions for creating CRM Leads from enquiries and filtering leads by business.
"""

import frappe
from frappe import _


def get_lead_permission_query_conditions(user):
    """
    Return SQL conditions for filtering CRM Lead records by OSDuo Business.

    This ensures users can only see leads belonging to businesses they have access to.

    Args:
        user: User email

    Returns:
        str: SQL WHERE condition
    """
    if not user:
        user = frappe.session.user

    # System Manager can see all leads
    if "System Manager" in frappe.get_roles(user):
        return ""

    # Get businesses where user is a member
    from osduo_business_connect.business.core import get_user_businesses
    businesses = get_user_businesses(user)

    if not businesses:
        return "1=0"  # No access

    business_names = [b["name"] for b in businesses]
    return f"`tabCRM Lead`.osduo_business IN ({', '.join(['%s'] * len(business_names))})"


def create_lead_from_enquiry(enquiry_doc):
    """
    Create a CRM Lead from a Business Enquiry.

    This function is called as a background job to ensure enquiries are never lost.

    Args:
        enquiry_doc: Business Enquiry document

    Returns:
        dict: Result with status and lead name if successful
    """
    try:
        # Validate enquiry
        if not enquiry_doc:
            return {"status": "error", "message": "Enquiry document is required"}

        if enquiry_doc.status != "Sync Pending":
            return {"status": "error", "message": f"Enquiry status is {enquiry_doc.status}, expected 'Sync Pending'"}

        # Create CRM Lead
        lead = frappe.get_doc({
            "doctype": "CRM Lead",
            "lead_name": enquiry_doc.visitor_name,
            "email_id": enquiry_doc.visitor_email,
            "mobile_no": enquiry_doc.visitor_phone,
            "organization": enquiry_doc.visitor_company,
            "lead_source": "OSDuo Business Enquiry",
            "osduo_business": enquiry_doc.business,
            "osduo_card": enquiry_doc.card,
            "osduo_product": enquiry_doc.product,
            "osduo_service": enquiry_doc.service,
            "osduo_enquiry": enquiry_doc.name,
            "osduo_campaign": enquiry_doc.campaign,
        })

        lead.insert(ignore_permissions=True)

        # Update enquiry status
        enquiry_doc.status = "Synced"
        enquiry_doc.crm_lead = lead.name
        enquiry_doc.save(ignore_permissions=True)

        frappe.db.commit()

        return {
            "status": "success",
            "lead": lead.name,
            "message": f"Lead {lead.name} created successfully"
        }

    except Exception as e:
        # Log error and update enquiry status
        frappe.log_error(
            message=f"Failed to create CRM Lead from Enquiry {enquiry_doc.name}: {str(e)}",
            title="CRM Lead Creation Failed"
        )

        # Update enquiry status to failed
        try:
            enquiry_doc.status = "Sync Failed"
            enquiry_doc.error_message = str(e)
            enquiry_doc.save(ignore_permissions=True)
            frappe.db.commit()
        except Exception:
            pass

        return {
            "status": "error",
            "message": str(e)
        }


def retry_failed_enquiries():
    """
    Retry creating CRM Leads for enquiries that failed to sync.

    This function is called by the scheduler (hourly).
    """
    # Get enquiries that failed to sync
    enquiries = frappe.get_all(
        "Business Enquiry",
        filters={
            "status": "Sync Failed",
        },
        fields=["name"],
        limit=100,  # Process in batches
    )

    if not enquiries:
        return

    frappe.logger().info(f"Retrying {len(enquiries)} failed enquiries")

    for enquiry in enquiries:
        try:
            enquiry_doc = frappe.get_doc("Business Enquiry", enquiry.name)
            create_lead_from_enquiry(enquiry_doc)
        except Exception as e:
            frappe.log_error(
                message=f"Failed to retry enquiry {enquiry.name}: {str(e)}",
                title="Enquiry Retry Failed"
            )
