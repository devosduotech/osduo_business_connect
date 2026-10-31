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


class Business(Document):
    def before_validate(self):
        if self.slug:
            self.slug = self.slug.lower().strip()
        if self.description:
            self.description = sanitize_rich_text(self.description)
        if self.seo_description:
            self.seo_description = sanitize_text(self.seo_description)
        normalize_url_fields(self)
        if self.website:
            self.website = sanitize_url(self.website)

    def validate(self):
        self.validate_slug_immutable()
        self.validate_slug()
        self.validate_owner_user()
        self.validate_contact_methods()

    def after_insert(self):
        self.ensure_owner_membership()
        self.apply_default_theme()

    def validate_slug_immutable(self):
        """Keep the public URL stable once the record is submitted.

        Drafts remain editable, and an amendment (a fresh draft copied from a
        cancelled record) may keep the original slug so existing NFC cards
        continue to work.
        """
        if self.is_new() or not self.name:
            return
        old_doc = self.get_doc_before_save()
        if old_doc and old_doc.docstatus >= 1 and old_doc.slug != self.slug:
            frappe.throw(
                "The Public Slug cannot be changed after submission. "
                "Cancel the record and amend it instead."
            )

    def validate_slug(self):
        if not self.slug:
            frappe.throw("Public Slug is required")
        if not re.match(r"^[a-z0-9-]+$", self.slug):
            frappe.throw("Slug can only contain lowercase letters, numbers, and hyphens")
        if self.slug.startswith("-") or self.slug.endswith("-"):
            frappe.throw("Slug cannot start or end with a hyphen")

        # Cancelled records must not reserve a slug forever — amendments need
        # to reuse the original URL. Drafts and submitted records still clash.
        filters = {"slug": self.slug, "docstatus": ["<", 2]}
        if not self.is_new():
            filters["name"] = ["!=", self.name]
        if frappe.db.exists("Business", filters):
            frappe.throw(f"Slug '{self.slug}' is already taken")

    def validate_owner_user(self):
        if not self.owner_user:
            frappe.throw("Business Owner is required")

        owner = frappe.db.get_value(
            "User", self.owner_user, ["name", "enabled"], as_dict=True
        )
        if not owner:
            frappe.throw("Business Owner must be an existing User")
        if not owner.enabled:
            frappe.throw("Business Owner must be an enabled User")

    def validate_contact_methods(self):
        if self.status == "Published":
            if not any([self.email, self.phone, self.whatsapp, self.website]):
                frappe.throw(
                    "At least one contact method is required for published businesses"
                )

    def ensure_owner_membership(self):
        """Create the owner's Business Member row on first insert."""
        if not self.owner_user:
            return
        if frappe.db.exists(
            "Business Member",
            {"business": self.name, "user": self.owner_user, "status": "Active"},
        ):
            return

        member = frappe.get_doc(
            {
                "doctype": "Business Member",
                "business": self.name,
                "user": self.owner_user,
                "person_name": frappe.db.get_value(
                    "User", self.owner_user, "full_name"
                )
                or self.owner_user,
                "role": "Owner",
                "is_owner": 1,
                "status": "Active",
            }
        )
        # The membership is created on behalf of the new business; the owner
        # does not have an existing membership yet to authorize this insert.
        member.flags.bc_bootstrap_owner = True
        member.insert(ignore_permissions=True)

    def apply_default_theme(self):
        """Link the built-in blue theme when no theme was selected."""
        if self.default_theme:
            return
        theme = frappe.db.get_value("BC Theme", {"theme_name": "Default Blue"}, "name")
        if theme:
            self.default_theme = theme
            self.db_set("default_theme", theme, update_modified=False)


def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user

    if user == "Guest":
        return (
            "`tabBusiness`.`status` = 'Published' "
            "and `tabBusiness`.`public_profile_enabled` = 1 "
            "and `tabBusiness`.docstatus < 2"
        )

    if is_system_manager(user):
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
            return bool(
                doc.status == "Published"
                and doc.public_profile_enabled
                and doc.docstatus < 2
            )
        return False

    if is_system_manager(user):
        return True

    if ptype == "create":
        if "BC Business Owner" in frappe.get_roles(user):
            return True
        # Amendments are new drafts copied from a cancelled Business. Allow the
        # original business's Owner to create the replacement draft even if
        # they only hold the per-business Owner role.
        amended_from = doc.get("amended_from")
        if amended_from:
            return get_user_role_in_business(user, amended_from) == "Owner"
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
    if ptype == "write":
        return member_role in ["Owner", "Manager", "Marketing"]
    if ptype == "submit":
        return member_role in ["Owner", "Manager", "Marketing"]
    if ptype in ("cancel", "amend"):
        return member_role == "Owner"
    if ptype == "delete":
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
    if not slug:
        return None
    return frappe.db.get_value(
        "Business",
        {"slug": slug, "status": "Published", "docstatus": ["<", 2]},
        ["name", "slug", "business_name", "logo", "status"],
        as_dict=True,
    )


def get_public_business_by_slug(slug):
    if not slug:
        return None
    return frappe.db.get_value(
        "Business",
        {
            "slug": slug,
            "status": "Published",
            "public_profile_enabled": 1,
            "docstatus": ["<", 2],
        },
        [
            "name",
            "slug",
            "business_name",
            "logo",
            "industry",
            "status",
            "description",
            "website",
            "email",
            "phone",
            "whatsapp",
            "address",
            "city",
            "state",
            "show_about_in_product_page",
            "show_about_in_service_page",
        ],
        as_dict=True,
    )
