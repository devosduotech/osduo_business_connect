# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Add-on Order — the only new-creation UI in the subscription workflow.

Payments and invoices stay with Aasriva. This DocType records a request and
its provider-controlled status transitions; activation of a custom domain
creates the Subscription child row through :mod:`subscription.domains`.
"""

import frappe
from frappe.model.document import Document

from osduo_business_connect.subscription.constants import (
    CUSTOM_DOMAIN_ADDON,
    DOMAIN_REGISTRATION_ADDON,
)
from osduo_business_connect.subscription.domains import (
    activate_domain_mapping,
    get_period_end,
    next_mapping,
)
from osduo_business_connect.subscription.entitlements import get_plan_code

# Requested → Approved → Configured → Verified → Active, with Expired reserved
# for the scheduler and Cancelled available before activation.
ALLOWED_TRANSITIONS = {
    "Requested": {"Approved", "Cancelled"},
    "Approved": {"Configured", "Cancelled"},
    "Configured": {"Verified", "Cancelled"},
    "Verified": {"Active", "Cancelled"},
    "Active": {"Expired"},
    "Expired": set(),
    "Cancelled": set(),
}


class AddonOrder(Document):
    def before_insert(self):
        # A customer can create a request, never a pre-approved/active order.
        # The status default in the DocType JSON is UI-only and is not trusted.
        self.status = "Requested"
        self.approved_by = None
        self.external_ref = None

    def before_validate(self):
        if self.hostname:
            self.hostname = str(self.hostname).strip().lower()
        if self.customer_email:
            self.customer_email = str(self.customer_email).strip().lower()

    def validate(self):
        self.set_request_snapshot()
        self.validate_add_on()
        self.validate_hostname()
        self.validate_evidence()
        self.validate_status_transition()
        self.set_approved_by()
        self.set_expiry()

    def on_update(self):
        if self.status == "Active":
            activate_domain_mapping(self)

    def set_request_snapshot(self):
        if not self.site:
            self.site = frappe.local.site
        # Always server-derived: a client must not spoof a higher plan to pass
        # an add-on's applicability check.
        self.plan_snapshot = get_plan_code()

    def validate_add_on(self):
        if not self.add_on:
            frappe.throw("Add-on is required", exc=frappe.ValidationError)
        try:
            add_on = frappe.get_doc("Add-on Master", self.add_on)
        except Exception:
            add_on = None
        if not add_on:
            frappe.throw("Add-on does not exist", exc=frappe.ValidationError)
        if not add_on.is_active:
            frappe.throw("This add-on is not active", exc=frappe.ValidationError)

        self.billing_type = add_on.billing_type
        if not add_on.applies_to_all_plans:
            plans = {row.get("plan") for row in (add_on.applicable_plans or [])}
            if self.plan_snapshot not in plans:
                frappe.throw(
                    f"{add_on.add_on_name} is not available on the {self.plan_snapshot} plan",
                    exc=frappe.ValidationError,
                )

        if self.add_on == CUSTOM_DOMAIN_ADDON and self.billing_type == "Annual":
            # Price comes from the frozen plan entitlements, never the payload.
            mapping_type, price = next_mapping()
            self.mapping_type = mapping_type
            self.amount = price
        elif self.billing_type == "Annual":
            self.amount = add_on.price
        else:
            # Actual cost is settled by the provider; the site only records evidence.
            self.amount = 0

    def validate_hostname(self):
        # Only domain-related add-ons need a hostname. Generic add-ons (for
        # example priority support) are fulfilment/billing records and must not
        # be forced to carry a fake domain.
        if not self._is_domain_add_on():
            return
        if not self.hostname:
            frappe.throw("Hostname is required", exc=frappe.ValidationError)

    def validate_evidence(self):
        if self.billing_type == "Actual Cost" and not self.quote_attachment:
            frappe.throw(
                "A quote or vendor invoice is required for actual-cost add-ons",
                exc=frappe.ValidationError,
            )

    def validate_status_transition(self):
        previous = self._previous()
        if not previous:
            return
        old_status = previous.get("status")
        if old_status == self.status:
            return
        if self.status not in ("Requested", "Cancelled") and not self._is_provider():
            frappe.throw(
                "Only the subscription provider can advance an Add-on Order",
                exc=frappe.PermissionError,
            )
        allowed = ALLOWED_TRANSITIONS.get(old_status, set())
        if self.status not in allowed:
            frappe.throw(
                f"Cannot change Add-on Order status from {old_status} to {self.status}",
                exc=frappe.ValidationError,
            )

    def set_approved_by(self):
        if self.status == "Approved" and not self.approved_by:
            self.approved_by = frappe.session.user

    def set_expiry(self):
        if self._is_domain_add_on():
            self.expires_on = get_period_end()

    def _is_domain_add_on(self):
        return self.add_on in (CUSTOM_DOMAIN_ADDON, DOMAIN_REGISTRATION_ADDON)

    def _is_provider(self):
        roles = set(frappe.get_roles() if hasattr(frappe, "get_roles") else [])
        return bool(
            roles.intersection({"Administrator", "System Manager", "BC Subscription Manager"})
        )

    def _previous(self):
        getter = getattr(self, "get_doc_before_save", None)
        if not callable(getter):
            return None
        old = getter()
        as_dict = getattr(old, "as_dict", None) if old else None
        return as_dict() if callable(as_dict) else old
