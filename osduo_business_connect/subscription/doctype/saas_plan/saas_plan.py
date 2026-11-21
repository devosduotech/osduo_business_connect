# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SaaSPlan(Document):
    def validate(self):
        self.min_annual_commitment = (
            (self.price_per_seat_per_year or 0) * (self.min_seats or 0)
        )
        if int(self.min_seats or 0) < 1:
            frappe.throw("Minimum Billed Seats must be at least 1")
        if self.advanced_admin:
            # Keep the derived flags coherent with the master switch.
            self.crm_full_control = 1
            self.email_configuration = 1
            self.whatsapp_configuration = 1
