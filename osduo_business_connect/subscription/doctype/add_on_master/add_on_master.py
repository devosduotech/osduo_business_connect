# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AddOnMaster(Document):
    def validate(self):
        if self.billing_type == "Actual Cost":
            self.price = 0
