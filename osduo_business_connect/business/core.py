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
