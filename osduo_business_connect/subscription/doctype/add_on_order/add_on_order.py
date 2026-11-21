# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from osduo_business_connect.subscription.entitlements import get_plan_code


class AddonOrder(Document):
    def before_insert(self):
        self.site = frappe.local.site
        self.plan_snapshot = get_plan_code()
        add_on = frappe.get_doc("Add-on Master", self.add_on) if self.add_on else None
        if add_on and add_on.billing_type == "Annual" and not self.amount:
            self.amount = add_on.price
