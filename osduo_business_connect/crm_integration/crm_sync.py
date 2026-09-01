# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
CRM Sync Service

Handles background synchronization of enquiries to Frappe CRM.
"""

import frappe
from frappe import _


def sync_enquiry_to_crm(enquiry_name):
    """
    Synchronize an enquiry to Frappe CRM.
    
    This is a controlled system operation that creates a CRM Lead
    from an OSDuo Business Enquiry.
    
    Args:
        enquiry_name: Enquiry name
        
    Returns:
        bool: True if successful
    """
    enquiry = frappe.get_doc("Enquiry", enquiry_name)
    
    # Check if already synced
    if enquiry.crm_lead:
        return True
    
    # Update status to Sync Pending
    frappe.db.set_value("Enquiry", enquiry_name, "status", "Sync Pending")
    frappe.db.commit()
    
    try:
        # Build CRM Lead data
        lead_data = build_lead_data(enquiry)
        
        # Create CRM Lead
        lead = frappe.get_doc(lead_data)
        lead.insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Update enquiry with lead reference
        frappe.db.set_value("Enquiry", enquiry_name, {
            "crm_lead": lead.name,
            "status": "Synced",
            "crm_sync_attempts": enquiry.crm_sync_attempts + 1,
            "last_sync_error": None,
        })
        frappe.db.commit()
        
        frappe.logger().info(f"Successfully synced enquiry {enquiry_name} to CRM Lead {lead.name}")
        return True
        
    except Exception as e:
        # Update enquiry with error
        error_msg = str(e)[:500]
        frappe.db.set_value("Enquiry", enquiry_name, {
            "status": "Sync Failed",
            "crm_sync_attempts": enquiry.crm_sync_attempts + 1,
            "last_sync_error": error_msg,
        })
        frappe.db.commit()
        
        frappe.log_error(
            message=f"CRM sync failed for {enquiry_name}: {error_msg}",
            title="CRM Sync Error"
        )
        return False


def build_lead_data(enquiry):
    """
    Build CRM Lead data from an enquiry.
    
    Args:
        enquiry: Enquiry document
        
    Returns:
        dict: Lead data for creation
    """
    # Get business name for organization
    business_name = None
    if enquiry.visitor_company:
        business_name = enquiry.visitor_company
    
    lead_data = {
        "doctype": "CRM Lead",
        "lead_name": enquiry.visitor_name,
        "email": enquiry.visitor_email,
        "mobile_no": enquiry.visitor_phone,
        "organization": business_name,
        "source": enquiry.source,
        "campaign_name": enquiry.campaign,
        "notes": enquiry.message,
        # OSDuo custom fields
        "osduo_business": enquiry.business,
        "osduo_card": enquiry.card,
        "osduo_product": enquiry.product,
        "osduo_service": enquiry.service,
        "osduo_enquiry": enquiry.name,
        "osduo_campaign": enquiry.campaign,
    }
    
    return lead_data


def retry_failed_sync():
    """
    Retry failed CRM sync for all pending enquiries.
    
    Returns:
        int: Number of successfully synced enquiries
    """
    # Get failed enquiries with less than 3 attempts
    enquiries = frappe.get_all(
        "Enquiry",
        filters={
            "status": "Sync Failed",
            "crm_sync_attempts": ["<", 3],
        },
        fields=["name"],
    )
    
    synced_count = 0
    for enquiry in enquiries:
        if sync_enquiry_to_crm(enquiry.name):
            synced_count += 1
    
    return synced_count


def enqueue_sync(enquiry_name):
    """
    Enqueue CRM sync as a background job.
    
    Args:
        enquiry_name: Enquiry name
    """
    frappe.enqueue(
        method="osduo_business_connect.crm_integration.crm_sync.sync_enquiry_to_crm",
        queue="default",
        timeout=300,
        enqueue_after_commit=True,
        enquiry_name=enquiry_name,
    )


def get_sync_stats(business_name=None):
    """
    Get CRM sync statistics.
    
    Args:
        business_name: Optional business name to filter by
        
    Returns:
        dict: Sync statistics
    """
    filters = {}
    if business_name:
        filters["business"] = business_name
    
    total = frappe.db.count("Enquiry", filters=filters)
    synced = frappe.db.count("Enquiry", filters={**filters, "status": "Synced"})
    failed = frappe.db.count("Enquiry", filters={**filters, "status": "Sync Failed"})
    pending = frappe.db.count("Enquiry", filters={**filters, "status": "Sync Pending"})
    new = frappe.db.count("Enquiry", filters={**filters, "status": "New"})
    
    return {
        "total": total,
        "synced": synced,
        "failed": failed,
        "pending": pending,
        "new": new,
    }
