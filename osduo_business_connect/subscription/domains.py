# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Custom domain and add-on lifecycle helpers.

Rules locked by the plan matrix:

* The first Enterprise mapping is included (₹0). Every other mapping, and all
  Professional/Business mappings, cost the plan's ``domain_mapping_price``.
* A mapping expires with ``Subscription.current_period_end``. Nothing here
  changes ``host_name`` or the printed QR/NFC URLs, which stay stable.
* Domain Registration / Renewal is billed at actual cost by the provider; this
  module only records the request and its evidence, never takes payment.
"""

import frappe
from frappe.utils import cint, getdate, today

from osduo_business_connect.subscription.constants import CUSTOM_DOMAIN_ADDON
from osduo_business_connect.subscription.entitlements import (
    get_entitlements,
    get_subscription,
)

INCLUDED = "Included"
PAID_CUSTOM_DOMAIN = "Paid Custom Domain"
OPEN_STATUSES = ("Requested", "Approved", "Configured", "Verified", "Active")


def get_period_end(subscription=None):
    subscription = subscription or get_subscription()
    return getattr(subscription, "current_period_end", None) if subscription else None


def included_domains():
    return cint(get_entitlements()["limits"].get("included_domain_mappings") or 0)


def domain_price():
    return cint(get_entitlements()["limits"].get("domain_mapping_price") or 0)


def get_domain_rows(subscription=None):
    subscription = subscription or get_subscription()
    if not subscription:
        return []
    return list(subscription.get("domain_mappings") or [])


def open_domain_rows(subscription=None):
    return [row for row in get_domain_rows(subscription) if row.get("status") in OPEN_STATUSES]


def next_mapping(subscription=None):
    """Return ``(mapping_type, price)`` for the next domain on this plan."""
    rows = open_domain_rows(subscription)
    included_count = sum(1 for row in rows if row.get("mapping_type") == INCLUDED)
    if included_count < included_domains():
        return INCLUDED, 0
    return PAID_CUSTOM_DOMAIN, domain_price()


def add_domain_mapping(hostname, add_on_order=None, mapping_type=None, status="Requested"):
    """Add a mapping row to the site's Subscription and return it.

    ``mapping_type`` is derived from purchased entitlements when omitted; a
    caller may not override the price. The hostname must be unique among open
    mappings.
    """
    if not hostname:
        frappe.throw("Hostname is required", exc=frappe.ValidationError)
    hostname = str(hostname).strip().lower()
    if "://" in hostname or "/" in hostname:
        frappe.throw("Hostname must be a domain name, not a URL", exc=frappe.ValidationError)

    subscription = get_subscription()
    if not subscription:
        frappe.throw("The site has no Subscription to attach a domain to", exc=frappe.ValidationError)

    for row in open_domain_rows(subscription):
        if str(row.get("hostname") or "").strip().lower() == hostname:
            frappe.throw(f"{hostname} already has an open domain mapping", exc=frappe.ValidationError)
        if add_on_order and row.get("add_on_order") == add_on_order:
            frappe.throw("This Add-on Order already has a domain mapping", exc=frappe.ValidationError)

    # Entitlements decide the mapping type and price. A caller-supplied value
    # is only a hint for display; it can never turn a paid mapping into an
    # included one (Enterprise first mapping only).
    derived_type, derived_price = next_mapping(subscription)
    mapping_type = derived_type
    price = derived_price

    row = {
        "doctype": "Domain Mapping",
        "hostname": hostname,
        "mapping_type": mapping_type,
        "status": status,
        "price": price,
        "add_on": CUSTOM_DOMAIN_ADDON,
        "add_on_order": add_on_order,
        "expires_on": get_period_end(subscription),
    }
    subscription.append("domain_mappings", row)
    subscription.save(ignore_permissions=True)
    return row


def activate_domain_mapping(order):
    """Activate (or create) the mapping attached to a custom-domain order."""
    if not order or getattr(order, "add_on", None) != CUSTOM_DOMAIN_ADDON:
        return
    hostname = getattr(order, "hostname", None)
    if not hostname:
        return

    subscription = get_subscription()
    if not subscription:
        return
    for row in open_domain_rows(subscription):
        if row.get("add_on_order") == order.name:
            if row.get("status") == "Active" and row.get("configured_on"):
                return
            row.status = "Active"
            row.configured_on = today()
            row.expires_on = get_period_end(subscription)
            subscription.save(ignore_permissions=True)
            return

    add_domain_mapping(
        hostname,
        add_on_order=order.name,
        mapping_type=getattr(order, "mapping_type", None),
        status="Active",
    )


def expire_domains():
    """Expire mappings past the billing period. Returns the number changed.

    Only the mapping and its Add-on Order status are touched. ``host_name``,
    printed QR codes and NFC URLs are deliberately left alone.
    """
    subscription = get_subscription()
    if not subscription:
        return 0

    changed = 0
    for row in open_domain_rows(subscription):
        expires_on = row.get("expires_on")
        if expires_on and getdate(expires_on) < getdate(today()):
            row.status = "Expired"
            changed += 1
            if row.get("add_on_order"):
                frappe.db.set_value("Add-on Order", row.add_on_order, "status", "Expired")
    if changed:
        subscription.save(ignore_permissions=True)
    return changed
