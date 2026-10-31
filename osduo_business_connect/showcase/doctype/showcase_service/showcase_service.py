# Copyright (c) 2026, OSDuo and contributors
import re

import frappe
from frappe.model.document import Document

from osduo_business_connect.utils.roles import is_system_manager
from osduo_business_connect.utils.sanitize import (
    normalize_url_fields,
    sanitize_rich_text,
    sanitize_text,
    sanitize_url,
)


class ShowcaseService(Document):
    def before_validate(self):
        if self.slug:
            self.slug = self.slug.lower().strip()
        if self.description:
            self.description = sanitize_rich_text(self.description)
        if self.short_description:
            self.short_description = sanitize_text(self.short_description)
        normalize_url_fields(self)
        for fieldname in ("location", "video_url", "brochure"):
            value = self.get(fieldname)
            if value:
                self.set(fieldname, sanitize_url(value))

    def validate(self):
        self.validate_slug_immutable()
        self.validate_slug()

    def validate_slug_immutable(self):
        """The service URL stays stable after submission; amendments may reuse it."""
        if self.is_new() or not self.name:
            return
        old_doc = self.get_doc_before_save()
        if old_doc and old_doc.docstatus >= 1 and old_doc.slug != self.slug:
            frappe.throw(
                "The Public Slug cannot be changed after submission. "
                "Cancel the service and amend it instead."
            )

    def validate_slug(self):
        if not self.slug:
            frappe.throw("Slug is required")
        if not re.match(r"^[a-z0-9-]+$", self.slug):
            frappe.throw("Slug can only contain lowercase letters, numbers, and hyphens")
        if self.slug.startswith("-") or self.slug.endswith("-"):
            frappe.throw("Slug cannot start or end with a hyphen")

        filters = {
            "slug": self.slug,
            "business": self.business,
            "docstatus": ["<", 2],
        }
        if not self.is_new():
            filters["name"] = ["!=", self.name]
        if frappe.db.exists("Showcase Service", filters):
            frappe.throw(f"Slug '{self.slug}' is already taken in this business")


def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user

    if user == "Guest":
        return (
            "`tabShowcase Service`.`status` = 'Published' "
            "and `tabShowcase Service`.docstatus < 2"
        )

    if is_system_manager(user):
        return ""

    from osduo_business_connect.business.core import get_user_businesses

    businesses = get_user_businesses(user)
    if not businesses:
        return "1=0"

    business_list = [frappe.db.escape(b["name"]) for b in businesses]
    return f"`tabShowcase Service`.business IN ({', '.join(business_list)})"


def has_permission(doc, user=None, ptype=None):
    if not user:
        user = frappe.session.user

    if user == "Guest":
        return ptype == "read" and doc.status == "Published" and doc.docstatus < 2

    if is_system_manager(user):
        return True

    from osduo_business_connect.business.core import get_user_role_in_business

    member_role = get_user_role_in_business(user, doc.business)
    if not member_role:
        return False

    if ptype == "read":
        return True
    if ptype in ("write", "create", "submit"):
        return member_role in ["Owner", "Manager", "Marketing"]
    if ptype in ("cancel", "amend", "delete"):
        return member_role == "Owner"

    return False
