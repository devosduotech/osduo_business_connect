# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
CRM Lead Mapper

Maps OSDuo Business Enquiry to Frappe CRM Lead.
Single source of truth for CRM Lead creation.
"""

import frappe
from frappe import _


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

        # Get card owner's user for lead_owner
        lead_owner = None
        if enquiry_doc.card:
            member_user = frappe.db.get_value(
                "Business Member",
                {"name": frappe.db.get_value("Digital Card", enquiry_doc.card, "member")},
                "user",
            )
            if member_user:
                lead_owner = member_user

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
        }

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


def ensure_crm_lead_source():
    """Ensure 'Business Connect' CRM Lead Source exists."""
    if not frappe.db.exists("CRM Lead Source", "Business Connect"):
        frappe.get_doc({
            "doctype": "CRM Lead Source",
            "source_name": "Business Connect",
        }).insert(ignore_permissions=True)
        frappe.db.commit()
