# Copyright (c) 2026, OSDuo and contributors
import re
import frappe
from frappe.model.document import Document

class ShowcaseProduct(Document):
    def validate(self):
        if self.name and frappe.db.exists(self.doctype, self.name):
            old_doc = self.get_doc_before_save()
            if old_doc and old_doc.slug != self.slug:
                frappe.throw("The Public Slug cannot be changed once the record is saved to ensure NFC cards remain functional.")
        self.validate_slug()

    def validate_slug(self):
        if not self.slug:
            frappe.throw("Slug is required")
        if frappe.db.exists("Showcase Product", {"slug": self.slug, "business": self.business, "name": ["!=", self.name]}):
            frappe.throw(f"Slug '{self.slug}' is already taken in this business")

    def normalize_fields(self):
        if self.slug: self.slug = self.slug.lower().strip()

    def normalize_urls(self):
        pass


def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user

    if user == "Guest":
        return "`tabShowcase Product`.`status` = 'Published' and `tabShowcase Product`.docstatus < 2"

    if "System Manager" in frappe.get_roles(user):
        return ""

    from osduo_business_connect.business.core import get_user_businesses
    businesses = get_user_businesses(user)
    if not businesses:
        return "1=0"

    business_list = [frappe.db.escape(b["name"]) for b in businesses]
    return f"`tabShowcase Product`.business IN ({', '.join(business_list)})"

def has_permission(doc, user=None, ptype=None):
    if not user:
        user = frappe.session.user

    if user == "Guest":
        return ptype == "read" and doc.status == "Published" and doc.docstatus < 2

    if "System Manager" in frappe.get_roles(user):
        return True

    from osduo_business_connect.business.core import get_user_role_in_business
    member_role = get_user_role_in_business(user, doc.business)
    if not member_role:
        return False

    if ptype == "read":
        return True
    elif ptype == "write":
        return member_role in ["Owner", "Manager", "Marketing"]
    elif ptype == "delete":
        return member_role == "Owner"

    return False
