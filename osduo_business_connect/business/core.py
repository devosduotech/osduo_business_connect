# Copyright (c) 2026, OSDuo and contributors
import re
import frappe
from frappe.model.document import Document

class Business(Document):
    def validate(self):
        if self.db_exists():
            old_doc = self.get_doc_before_save()
            if old_doc and old_doc.slug != self.slug:
                frappe.throw("The Public Slug cannot be changed once the record is saved to ensure NFC cards remain functional.")
        self.validate_slug()
        self.validate_owner_user()
        self.validate_contact_methods()

    def validate_slug(self):
        if not self.slug:
            frappe.throw("Public Slug is required")
        if not re.match(r'^[a-z0-9-]+$', self.slug):
            frappe.throw("Slug can only contain lowercase letters, numbers, and hyphens")
        if self.slug.startswith('-') or self.slug.endswith('-'):
            frappe.throw("Slug cannot start or end with a hyphen")
        if self.is_new():
            if frappe.db.exists("Business", {"slug": self.slug}):
                frappe.throw(f"Slug '{self.slug}' is already taken")
        else:
            if frappe.db.exists("Business", {"slug": self.slug, "name": ["!=", self.name]}):
                frappe.throw(f"Slug '{self.slug}' is already taken")

    def validate_owner_user(self):
        if not self.owner_user:
            frappe.throw("Business Owner is required")

    def validate_contact_methods(self):
        if self.status == "Published":
            if not any([self.email, self.phone, self.whatsapp, self.website]):
                frappe.throw("At least one contact method is required for published businesses")

    def before_validate(self):
        if self.slug:
            self.slug = self.slug.lower().strip()

    def normalize_fields(self):
        if self.slug: self.slug = self.slug.lower().strip()

    def normalize_urls(self):
        if hasattr(self, 'email') and self.email: self.email = self.email.lower().strip()


def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user

    if "System Manager" in frappe.get_roles(user):
        return ""

    businesses = get_user_businesses(user)
    if not businesses:
        return "1=0"

    business_names = [frappe.db.escape(b["name"]) for b in businesses]
    return f"`tabBusiness`.name IN ({', '.join(business_names)})"

def has_permission(doc, user=None, ptype=None):
    if not user:
        user = frappe.session.user

    if user == "Guest":
        if ptype == "read":
            return doc.status == "Published" and doc.public_profile_enabled
        return False

    if "System Manager" in frappe.get_roles(user):
        return True

    if ptype == "create":
        if "BC Business Owner" in frappe.get_roles(user):
            return True
        return False

    businesses = get_user_businesses(user)
    business_names = [b["name"] for b in businesses]

    if doc.name not in business_names:
        return False

    member_role = get_user_role_in_business(user, doc.name)
    if not member_role:
        return False

    if ptype == "read":
        return True
    elif ptype == "write":
        return member_role in ["Owner", "Manager", "Marketing"]
    elif ptype == "delete":
        return member_role == "Owner"

    return False

def get_user_businesses(user):
    if not user:
        user = frappe.session.user
    members = frappe.get_all(
        "Business Member",
        filters={"user": user, "status": "Active"},
        fields=["business", "role"],
    )
    return [{"name": m.business, "role": m.role} for m in members]

def get_user_role_in_business(user, business):
    member = frappe.get_all(
        "Business Member",
        filters={"user": user, "business": business, "status": "Active"},
        fields=["role"],
    )
    return member[0].role if member else None

def get_business_by_slug(slug):
    if not slug: return None
    return frappe.db.get_value(
        "Business", {"slug": slug, "status": "Published"},
        ["name", "slug", "business_name", "logo", "status"], as_dict=True
    )

def get_public_business_by_slug(slug):
    if not slug: return None
    return frappe.db.get_value(
        "Business", {"slug": slug, "status": "Published", "public_profile_enabled": 1},
        ["name", "slug", "business_name", "logo", "status", "description", "website", "email", "phone", "whatsapp", "address", "city", "state", "show_about_in_product_page", "show_about_in_service_page"],
        as_dict=True
    )
