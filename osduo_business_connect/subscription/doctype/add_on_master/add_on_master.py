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


class AddonMaster(Document):
    def validate(self):
        if self.billing_type == "Actual Cost":
            self.price = 0
        if self.applies_to_all_plans:
            # A master that applies to every plan must not keep stale per-plan
            # rows. The table is also read-only in the form for this state.
            self.applicable_plans = []
        elif not (self.applicable_plans or []):
            frappe.throw(
                "Select at least one Applicable Plan when 'Applies to All Plans' "
                "is unchecked",
                exc=frappe.ValidationError,
            )


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
