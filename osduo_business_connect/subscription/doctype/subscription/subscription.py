# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.model.document import Document

from osduo_business_connect.subscription.entitlements import clear_entitlement_cache


class Subscription(Document):
    def validate(self):
        self.validate_seats()
        self.validate_snapshot()
        self.sync_domain_expiry()

    def sync_domain_expiry(self):
        """Domain/add-on expiry always follows the subscription period end."""
        for row in self.get("domain_mappings") or []:
            if row.get("status") != "Cancelled":
                row.expires_on = self.current_period_end

    def on_update(self):
        clear_entitlement_cache()

    def validate_seats(self):
        minimum = int(self.min_billed_seats or 0)
        ordered = int(self.seats_ordered or 0)
        if minimum and ordered < minimum:
            frappe.throw(
                f"Seats Ordered ({ordered}) cannot be below the plan minimum ({minimum})."
            )
        self.seats_cap = max(minimum, ordered)

    def validate_snapshot(self):
        if not self.entitlement_snapshot:
            return
        try:
            json.loads(self.entitlement_snapshot)
        except (TypeError, ValueError):
            frappe.throw("Entitlement Snapshot must be valid JSON.")
