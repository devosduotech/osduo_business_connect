# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.model.document import Document

from osduo_business_connect.subscription.entitlements import clear_entitlement_cache

# Only the provider CLI may change these fields after the Site is provisioned.
# DocType JSON ``read_only`` flags are UI-only and are not a security boundary.
PROVIDER_MANAGED_FIELDS = (
    "plan",
    "status",
    "seats_ordered",
    "min_billed_seats",
    "seats_cap",
    "current_period_end",
    "grace_until",
    "external_crm_enabled",
    "external_ref",
    "site_plan_source",
    "provisioned_by",
    "provisioned_on",
    "grandfathered",
    "migrated",
    "entitlement_snapshot",
)


class Subscription(Document):
    def validate(self):
        self.validate_provider_managed_fields()
        self.validate_seats()
        self.validate_snapshot()
        self.sync_domain_expiry()

    def validate_provider_managed_fields(self):
        """Keep the frozen snapshot and provider-set status non-escalatable.

        The provisioning CLI and status CLI set ``frappe.flags.bc_provisioning``
        around their writes. Everyone else may only add audit/domain rows and
        edit notes — never the plan, seats, snapshot or status.
        """
        if getattr(frappe.flags, "bc_provisioning", False) or self.is_new():
            return
        old = self.get_doc_before_save() if hasattr(self, "get_doc_before_save") else None
        if not old:
            return
        for field in PROVIDER_MANAGED_FIELDS:
            if old.get(field) != self.get(field):
                frappe.throw(
                    f"{field.replace('_', ' ').title()} is managed by the subscription provider. "
                    "Use the provisioning/status CLI to change it.",
                    exc=frappe.ValidationError,
                )

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
