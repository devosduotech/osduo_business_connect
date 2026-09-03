import frappe


def on_crm_lead_update(doc, method):
    """When CRM Lead status changes, update the linked Enquiry status.
    If CRM Lead status is anything other than 'New', set Enquiry to 'Converted'.
    Only applies to leads created from our application (have osduo_enquiry)."""
    enquiry_name = doc.osduo_enquiry if hasattr(doc, "osduo_enquiry") else None
    if not enquiry_name:
        enquiry_name = frappe.db.get_value("CRM Lead", doc.name, "osduo_enquiry")
    if not enquiry_name:
        return

    # Any status other than New means the enquiry is being acted on
    new_status = "Converted" if doc.status != "New" else "New"

    current_status = frappe.db.get_value("Enquiry", enquiry_name, "status")
    if current_status != new_status:
        frappe.db.set_value("Enquiry", enquiry_name, "status", new_status)
        frappe.db.commit()
