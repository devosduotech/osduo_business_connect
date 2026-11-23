# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Add-on Order — the only new-creation UI in the subscription workflow.

Payments and invoices stay with Aasriva. This DocType records a request and
its provider-controlled status transitions; activation of a custom domain
creates the Subscription child row through :mod:`subscription.domains`.
"""

from html import escape

import frappe
from frappe.model.document import Document

from osduo_business_connect.subscription.constants import (
    ADDITIONAL_USER_ADDON,
    ADDON_ORDER_NOTIFICATION_CONFIG_KEY,
    ADDON_ORDER_NOTIFICATION_EMAIL,
    CUSTOM_DOMAIN_ADDON,
    DOMAIN_REGISTRATION_ADDON,
)
from osduo_business_connect.subscription.domains import (
    activate_domain_mapping,
    get_period_end,
    next_mapping,
)
from osduo_business_connect.subscription.entitlements import get_entitlements, get_plan_code

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


def _row_value(row, key, default=None):
    """Read a child row field from either a dict or a Frappe Document."""
    getter = getattr(row, "get", None)
    if callable(getter):
        return getter(key, default)
    try:
        return row[key]
    except (KeyError, TypeError):
        return default


def derive_addon_values(add_on_code, plan_code=None):
    """Validate an add-on for the active plan and derive server-owned values.

    Customer orders are locked to the site's frozen plan. Higher-plan add-ons
    stay hidden until the provider upgrades the site from Aasriva; a client
    cannot pass a target plan to bypass this check.
    """
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

    plan_row = next(
        (
            row for row in (add_on.applicable_plans or [])
            if _row_value(row, "plan") == plan_code
        ),
        None,
    )
    if not add_on.applies_to_all_plans and plan_row is None:
        upgrade_url = get_entitlements().get("upgrade_url") or ""
        upgrade_hint = f" Upgrade to unlock it: {upgrade_url}" if upgrade_url else ""
        frappe.throw(
            f"{add_on.add_on_name} is not available on the {plan_code} plan."
            + upgrade_hint,
            exc=frappe.ValidationError,
        )

    billing_type = add_on.billing_type
    mapping_type = None
    if add_on_code == CUSTOM_DOMAIN_ADDON and billing_type == "Annual":
        # Price comes from the frozen plan entitlements, never from the payload.
        mapping_type, amount = next_mapping()
    elif billing_type == "Annual":
        # Plan-specific prices live in the Applicable Plans table. The master
        # List Price remains the fallback for all-plan add-ons and legacy rows.
        plan_price = _row_value(plan_row, "price") if plan_row is not None else None
        amount = add_on.price if plan_price in (None, "") else plan_price
        try:
            amount = float(amount or 0)
        except (TypeError, ValueError):
            frappe.throw(
                f"Invalid price configured for {add_on.add_on_name} on the {plan_code} plan",
                exc=frappe.ValidationError,
            )
    else:
        # Actual cost is settled by the provider; the site only records evidence.
        amount = 0

    return add_on, {
        "plan_snapshot": plan_code,
        "billing_type": billing_type,
        "amount": amount,
        "mapping_type": mapping_type,
    }


def _user_is_provider(user=None):
    """Administrator and the provider-side subscription manager own the workflow."""
    user = user or getattr(frappe.session, "user", None)
    if user == "Administrator":
        return True
    get_roles = getattr(frappe, "get_roles", None)
    roles = get_roles(user) if callable(get_roles) else ()
    return "BC Subscription Manager" in (roles or ())


def _require_addon_order_access():
    """Reject anonymous/unauthorised callers of the whitelisted quote API.

    ``plan_gates`` only filters this method while the site is inaccessible, so
    the endpoint must enforce authentication itself. Quote data discloses the
    site's plan code, add-on pricing and domain expiry. Providers are allowed
    even though their role is intentionally absent from the customer DocPerms.
    """
    user = getattr(frappe.session, "user", None)
    if not user or user == "Guest":
        frappe.throw("Not permitted", exc=frappe.PermissionError)
    if _user_is_provider(user):
        return
    has_permission = getattr(frappe, "has_permission", None)
    if callable(has_permission) and not has_permission("Add-on Order", "read"):
        frappe.throw("Not permitted", exc=frappe.PermissionError)


@frappe.whitelist()
def get_addon_quote(add_on=None, **kwargs):
    """Server-derived preview for the customer-facing Add-on Order form.

    Returns only display metadata and values the controller will re-derive on
    save. It never accepts or returns a client-supplied price.
    """
    _require_addon_order_access()
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
    elif add_on == ADDITIONAL_USER_ADDON:
        amount_label = "Estimated annual price for one additional user"
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
        "requires_documents": add_on == DOMAIN_REGISTRATION_ADDON,
        "requires_attachment": requires_attachment,
    }


def get_notification_recipients():
    """Configured notification recipients, defaulting to the OSDuo inbox."""
    configured = frappe.conf.get(ADDON_ORDER_NOTIFICATION_CONFIG_KEY)
    if not configured:
        configured = ADDON_ORDER_NOTIFICATION_EMAIL
    return [
        address.strip()
        for address in str(configured).replace(";", ",").split(",")
        if address.strip()
    ]


def send_new_order_notification(doc):
    """Notify the provider when a new Add-on Order is created.

    The recipient is configurable per site. A mail failure must never roll back
    the customer's request, so errors are logged and swallowed.
    """
    recipients = get_notification_recipients()
    if not recipients:
        return
    message = (
        "<p>A new Add-on Order has been requested.</p>"
        "<ul>"
        f"<li><strong>Order:</strong> {escape(str(doc.name or ''))}</li>"
        f"<li><strong>Add-on:</strong> {escape(str(doc.add_on or ''))}</li>"
        f"<li><strong>Plan:</strong> {escape(str(doc.plan_snapshot or ''))}</li>"
        f"<li><strong>Estimated amount:</strong> {escape(str(doc.amount or 0))}</li>"
        f"<li><strong>Customer email:</strong> {escape(str(doc.customer_email or ''))}</li>"
        f"<li><strong>Hostname:</strong> {escape(str(doc.hostname or ''))}</li>"
        f"<li><strong>Requested by:</strong> {escape(str(frappe.session.user or ''))}</li>"
        "</ul>"
    )
    try:
        frappe.sendmail(
            recipients=recipients,
            subject=f"New Add-on Order {doc.name} — {doc.add_on}",
            message=message,
            reference_doctype=doc.doctype,
            reference_name=doc.name,
        )
    except Exception:
        log_error = getattr(frappe, "log_error", None)
        traceback = getattr(frappe, "get_traceback", lambda: "")
        if callable(log_error):
            log_error(
                title="BC Add-on Order notification failed",
                message=traceback(),
            )


class AddonOrder(Document):
    def before_insert(self):
        # Customers can only create Requested records. Provider users may
        # select any workflow status when creating an order.
        # The JSON default is UI-only and is never trusted for customers.
        if not self._is_provider():
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
        self.validate_customer_status()
        self.validate_add_on()
        self.validate_hostname()
        self.validate_evidence()
        self.validate_invoice_permission()
        self.validate_status_transition()
        self.set_approved_by()
        self.set_expiry()

    def after_insert(self):
        send_new_order_notification(self)

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

    def validate_customer_status(self):
        if not self.status:
            self.status = "Requested"
        if self._is_provider():
            return
        if self.status != "Requested":
            frappe.throw(
                "Customers can only request add-ons. Status changes are made by "
                "the subscription provider after the order is reviewed.",
                exc=frappe.PermissionError,
            )

    def validate_invoice_permission(self):
        if self._is_provider():
            return
        previous = self._previous() or {}
        previous_invoice = previous.get("invoice")
        if self.invoice and self.invoice != previous_invoice:
            frappe.throw(
                "Only the subscription provider can attach an Invoice",
                exc=frappe.PermissionError,
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
        # Standard System Manager is reserved for Frappe CRM and the remaining
        # BC roles are customer data-entry roles.
        return _user_is_provider()

    def _previous(self):
        getter = getattr(self, "get_doc_before_save", None)
        if not callable(getter):
            return None
        old = getter()
        as_dict = getattr(old, "as_dict", None) if old else None
        return as_dict() if callable(as_dict) else old
