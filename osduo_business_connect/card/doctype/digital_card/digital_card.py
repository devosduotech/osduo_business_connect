# Copyright (c) 2026, OSDuo and contributors
import re
import frappe
from frappe.model.document import Document

class DigitalCard(Document):
    def validate(self):
        if self.db_exists():
            old_doc = self.get_doc_before_save()
            if old_doc and old_doc.slug != self.slug:
                frappe.throw("The Public Slug cannot be changed once the record is saved to ensure NFC cards remain functional.")
        self.validate_slug()

    def validate_slug(self):
        if not self.slug:
            frappe.throw("Slug is required")
        if not re.match(r'^[a-z0-9-]+$', self.slug):
            frappe.throw("Slug can only contain lowercase letters, numbers, and hyphens")
        if frappe.db.exists("Digital Card", {"slug": self.slug, "name": ["!=", self.name]}):
            frappe.throw(f"Slug '{self.slug}' is already taken")

    def normalize_fields(self):
        if self.slug: self.slug = self.slug.lower().strip()

    def normalize_urls(self):
        if hasattr(self, 'email') and self.email: self.email = self.email.lower().strip()
