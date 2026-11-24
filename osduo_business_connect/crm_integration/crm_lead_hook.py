import frappe

from osduo_business_connect.crm_integration.status_reconciliation import (
    map_crm_status,
    sync_from_crm_lead,
)


def on_crm_lead_update(doc, method):
    """When CRM Lead status changes, update the linked Enquiry status.

    Only applies to leads created from our application (have osduo_enquiry).
    Contact Exchange status is reconciled by sync_from_crm_lead, which also
    re-reads ``converted`` so a stale status on the in-memory doc cannot win.
    """
    enquiry_name = getattr(doc, "osduo_enquiry", None)
    if not enquiry_name:
        try:
            enquiry_name = frappe.db.get_value("CRM Lead", doc.name, "osduo_enquiry")
        except Exception:
            return
    if not enquiry_name:
        return

    crm_status = getattr(doc, "status", None) or "New"
    enquiry_status, _ = map_crm_status(crm_status, converted=bool(getattr(doc, "converted", 0)))

    if enquiry_status and frappe.db.get_value("Enquiry", enquiry_name, "status") != enquiry_status:
        frappe.db.set_value("Enquiry", enquiry_name, "status", enquiry_status)

    try:
        sync_from_crm_lead(doc)
    except Exception as e:
        frappe.log_error(
            title="CRM Lead Contact Exchange status sync failed",
            message=f"CRM Lead {doc.name}: {e}",
        )
