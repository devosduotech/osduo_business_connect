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


def derive_addon_values(add_on_code, plan_code=None):
    """Validate an add-on for a plan and derive all server-owned order values."""
    if not add_on_code:
        frappe.throw("Add-on is required", exc=frappe.ValidationError)
    plan_code = plan_code or get_plan_code()
    try:
        add_on = frappe.get_doc("Add-on Master", add_on_code)
    except Exception:
        add_on = None
    if not add_on:
        frappe.throw("Add-on does not exist", exc=frappe.ValidationError)
    if not add_on.is_active:
        frappe.throw("This add-on is not active", exc=frappe.ValidationError)

    if not add_on.applies_to_all_plans:
        plans = {row.get("plan") for row in (add_on.applicable_plans or [])}
        if plan_code not in plans:
            frappe.throw(
                f"{add_on.add_on_name} is not available on the {plan_code} plan",
                exc=frappe.ValidationError,
            )

    billing_type = add_on.billing_type
    mapping_type = None
    if add_on_code == CUSTOM_DOMAIN_ADDON and billing_type == "Annual":
        # Price comes from the frozen plan entitlements, never from the payload.
        mapping_type, amount = next_mapping()
    elif billing_type == "Annual":
        amount = add_on.price
    else:
        # Actual cost is settled by the provider; the site only records evidence.
        amount = 0

    return add_on, {
        "plan_snapshot": plan_code,
        "billing_type": billing_type,
        "amount": amount,
        "mapping_type": mapping_type,
    }


@frappe.whitelist()
def get_addon_quote(add_on=None, **kwargs):
    """Server-derived preview for the customer-facing Add-on Order form.

    Returns only display metadata and values the controller will re-derive on
    save. It never accepts or returns a client-supplied price.
    """
    add_on_doc, values = derive_addon_values(add_on)
    is_domain_addon = add_on in (CUSTOM_DOMAIN_ADDON, DOMAIN_REGISTRATION_ADDON)
    requires_attachment = values["billing_type"] == "Actual Cost"

    if requires_attachment:
        amount_label = (
            "Actual vendor cost. Attach a quote; the final amount is confirmed "
            "by the provider."
        )
    elif values["amount"] == 0 and add_on == CUSTOM_DOMAIN_ADDON:
        amount_label = "Included in your plan"
    else:
        amount_label = "Estimated annual amount"

    return {
        "add_on": add_on,
        "add_on_name": add_on_doc.add_on_name,
        "plan_snapshot": values["plan_snapshot"],
        "billing_type": values["billing_type"],
        "amount": values["amount"],
        "amount_label": amount_label,
        "mapping_type": values["mapping_type"] or "",
        "expires_on": get_period_end() if is_domain_addon else None,
        "requires_hostname": is_domain_addon,
        "requires_mapping_type": add_on == CUSTOM_DOMAIN_ADDON,
        "requires_registration_details": add_on == DOMAIN_REGISTRATION_ADDON,
        "requires_attachment": requires_attachment,
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
        add_on, values = derive_addon_values(self.add_on, self.plan_snapshot)
        self.billing_type = values["billing_type"]
        self.amount = values["amount"]
        self.mapping_type = values["mapping_type"]

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
        # Only the site Administrator advances provider-controlled records.
        # Standard System Manager is reserved for Frappe CRM, and BC roles are
        # for Business Connect data entry only.
        return getattr(frappe.session, "user", None) == "Administrator"

    def _previous(self):
        getter = getattr(self, "get_doc_before_save", None)
        if not callable(getter):
            return None
        old = getter()
        as_dict = getattr(old, "as_dict", None) if old else None
        return as_dict() if callable(as_dict) else old
