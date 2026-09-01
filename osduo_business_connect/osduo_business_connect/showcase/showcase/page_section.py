# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PageSection(Document):
    """
    Page Section DocType - Defines configurable sections for public business profiles.
    
    Controls which sections appear and in what order on the public profile page.
    """

    def before_validate(self):
        """Pre-process data before validation."""
        pass

    def validate(self):
        """Authoritative location for section validation."""
        self.validate_business()
        self.validate_sequence()
        self.validate_section_config()

    def before_save(self):
        """Pre-save operations."""
        pass

    def on_update(self):
        """Post-save operations."""
        pass

    def validate_business(self):
        """Validate that business exists and is published."""
        if not self.business:
            frappe.throw("Business is required")

        business = frappe.get_doc("Business", self.business)
        if not business:
            frappe.throw("Business does not exist")

    def validate_sequence(self):
        """Validate sequence uniqueness within business."""
        if self.sequence is None:
            return

        existing = frappe.get_all(
            "Page Section",
            filters={
                "business": self.business,
                "sequence": self.sequence,
                "name": ["!=", self.name],
            },
            fields=["name"],
        )
        if existing:
            frappe.throw(
                f"A section with sequence {self.sequence} already exists in this business"
            )

    def validate_section_config(self):
        """Validate section-specific configuration."""
        if self.section_type == "Hero":
            if not self.config_hero_title:
                frappe.throw("Hero Title is required for Hero section")

    def get_section_data(self):
        """
        Get section data for rendering.
        
        Returns:
            dict: Section configuration data
        """
        data = {
            "section_type": self.section_type,
            "title": self.title,
            "enabled": self.enabled,
            "sequence": self.sequence,
            "visibility": self.visibility,
        }

        # Add section-specific configuration
        if self.section_type == "Hero":
            data["hero"] = {
                "title": self.config_hero_title,
                "subtitle": self.config_hero_subtitle,
                "image": self.config_hero_image,
                "cta_text": self.config_hero_cta_text,
                "cta_url": self.config_hero_cta_url,
            }
        elif self.section_type == "About":
            data["about"] = {
                "text": self.config_about_text,
                "image": self.config_about_image,
            }
        elif self.section_type == "Products":
            data["products"] = {
                "show_products": self.config_show_products,
            }
        elif self.section_type == "Services":
            data["services"] = {
                "show_services": self.config_show_services,
            }
        elif self.section_type == "Contact":
            data["contact"] = {
                "email": self.config_contact_email,
                "phone": self.config_contact_phone,
                "address": self.config_contact_address,
            }
        elif self.section_type == "Custom":
            data["custom"] = {
                "html": self.config_custom_html,
            }

        return data


def get_permission_query_conditions(user):
    """
    Return SQL conditions for filtering Page Section records.
    
    Users can only see sections of businesses they belong to.
    """
    if not user:
        user = frappe.session.user

    # System Manager can see all sections
    if "System Manager" in frappe.get_roles(user):
        return ""

    # Get businesses where user is a member
    from osduo_business_connect.business.business.business import get_user_businesses
    businesses = get_user_businesses(user)

    if not businesses:
        return "1=0"

    business_names = [b["name"] for b in businesses]
    return f"`tabPage Section`.business IN ({', '.join(['%s'] * len(business_names))})"


def has_permission(doc, ptype):
    """
    Check if user has permission on Page Section document.
    
    Business Owner/Manager/Marketing can manage sections.
    """
    user = frappe.session.user

    # System Manager has full access
    if "System Manager" in frappe.get_roles(user):
        return True

    # Check if user is a member of this business
    from osduo_business_connect.business.business.business import get_user_businesses
    businesses = get_user_businesses(user)
    business_names = [b["name"] for b in businesses]

    if doc.business not in business_names:
        return False

    # Get user's role in this business
    from osduo_business_connect.business.business.business import get_user_role_in_business
    member_role = get_user_role_in_business(user, doc.business)

    if not member_role:
        return False

    # Check permissions based on role
    if ptype == "read":
        return True
    elif ptype == "write":
        return member_role in ["Owner", "Manager", "Marketing"]
    elif ptype == "create":
        return member_role in ["Owner", "Manager", "Marketing"]
    elif ptype == "delete":
        return member_role == "Owner"

    return False
