# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from osduo_business_connect.subscription.entitlements import get_plan_code

try:
    from frappe import validate_and_sanitize_search_inputs
except ImportError:  # isolated local test stub
    def validate_and_sanitize_search_inputs(fn):
        return fn


def _row_value(row, key, default=None):
    """Read a child row field from either a dict or a Frappe Document."""
    getter = getattr(row, "get", None)
    if callable(getter):
        return getter(key, default)
    try:
        return row[key]
    except (KeyError, TypeError):
        return default


def _set_row_value(row, key, value):
    """Write a child row field without assuming dict vs Document."""
    if isinstance(row, dict):
        row[key] = value
    else:
        setattr(row, key, value)


class AddonMaster(Document):
    def validate(self):
        rows = self.applicable_plans or []
        if self.billing_type == "Actual Cost":
            self.price = 0
            for row in rows:
                _set_row_value(row, "price", 0)
        if self.applies_to_all_plans:
            # A master that applies to every plan must not keep stale per-plan
            # rows. The table is also read-only in the form for this state.
            self.applicable_plans = []
            return
        if not rows:
            frappe.throw(
                "Select at least one Applicable Plan when 'Applies to All Plans' "
                "is unchecked",
                exc=frappe.ValidationError,
            )

        seen = set()
        for row in rows:
            plan = _row_value(row, "plan")
            if plan in seen:
                frappe.throw(
                    f"Plan {plan} is listed more than once in Applicable Plans",
                    exc=frappe.ValidationError,
                )
            seen.add(plan)
            if self.billing_type != "Annual":
                continue
            price = _row_value(row, "price")
            if price in (None, ""):
                frappe.throw(
                    f"Set an Annual Price for {plan} in the Applicable Plans table",
                    exc=frappe.ValidationError,
                )
            try:
                price = float(price)
            except (TypeError, ValueError):
                frappe.throw(
                    f"Invalid Annual Price for {plan} in the Applicable Plans table",
                    exc=frappe.ValidationError,
                )
            if price < 0:
                frappe.throw(
                    f"Annual Price for {plan} cannot be negative",
                    exc=frappe.ValidationError,
                )
            _set_row_value(row, "price", price)


@frappe.whitelist()
@validate_and_sanitize_search_inputs
def get_orderable_addons(
    doctype=None,
    txt=None,
    searchfield=None,
    start=0,
    page_len=20,
    filters=None,
    **kwargs,
):
    """Link-query rows for Add-on Orders, without exposing the master list.

    ``frappe.get_all`` bypasses DocPerms by design. This method returns only the
    active add-ons the current site's frozen plan is allowed to order, so customer
    roles need no read/list permission on Add-on Master.
    """
    plan_code = get_plan_code()
    masters = frappe.get_all(
        "Add-on Master",
        filters={"is_active": 1},
        fields=["name", "add_on_name", "applies_to_all_plans"],
        order_by="add_on_name asc",
        limit_page_length=0,
    ) or []

    names = [row.get("name") for row in masters if row.get("name")]
    allowed_plans = {}
    if names:
        for child in frappe.get_all(
            "Add-on Applicable Plan",
            filters={"parent": ["in", names], "parenttype": "Add-on Master"},
            fields=["parent", "plan"],
            limit_page_length=0,
        ) or []:
            allowed_plans.setdefault(child.get("parent"), set()).add(child.get("plan"))

    needle = str(txt or "").strip().lower()
    options = []
    for row in masters:
        name = row.get("name")
        if not name:
            continue
        eligible = bool(row.get("applies_to_all_plans")) or (
            plan_code in allowed_plans.get(name, set())
        )
        if not eligible:
            continue
        label = row.get("add_on_name") or name
        if needle and needle not in str(name).lower() and needle not in str(label).lower():
            continue
        options.append((name, label))

    start = int(start or 0)
    page_len = int(page_len or 20)
    return options[start:start + page_len]
