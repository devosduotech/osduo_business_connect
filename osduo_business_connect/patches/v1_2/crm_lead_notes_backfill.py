import frappe


def execute():
    """Backfill ``osduo_notes`` on existing CRM Leads from their Enquiry message.

    ``osduo_notes`` was added so the free-text captured on an Enquiry (website
    form message, or the channel/event context of a Share & Save Contact
    exchange) is visible on the CRM Lead. Leads already synced before this
    change never see the new mapping, so copy the message across in one pass.
    """
    # The custom field is created by after_migrate, which runs after patches —
    # create it here (idempotent) so the column exists before we update it.
    try:
        from osduo_business_connect.install import create_crm_custom_fields

        create_crm_custom_fields()
    except Exception:
        frappe.log_error(title="OSDuo notes backfill: custom field setup failed")
        return

    frappe.db.sql(
        """
        update `tabCRM Lead` lead
        join `tabEnquiry` enquiry on enquiry.name = lead.osduo_enquiry
        set lead.osduo_notes = enquiry.message
        where lead.osduo_enquiry is not null
          and (lead.osduo_notes is null or lead.osduo_notes = '')
          and enquiry.message is not null
          and enquiry.message != ''
        """,
    )
    frappe.db.commit()
