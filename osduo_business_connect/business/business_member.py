# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BusinessMember(Document):
    """
    Business Member DocType - Links an authenticated Frappe User to a Business.

    This is the authorization bridge between Frappe User and OSDuo Business.
    It defines the user's role within the business and their access level.
    """

    def before_validate(self):
        """Pre-process data before validation."""
        self.normalize_fields()

    def validate(self):
        """Authoritative location for business member validation."""
        self.validate_user()
        self.validate_business()
        self.validate_role()
        self.validate_unique_membership()
        self.set_defaults()

    def before_save(self):
        """Pre-save operations."""
        self.set_email_from_user()

    def normalize_fields(self):
        """Normalize field values."""
        # Normalize email to lowercase
        if self.email:
            self.email = self.email.lower().strip()

    def validate_user(self):
        """Validate that user is valid and enabled."""
        if not self.user:
            frappe.throw("User is required")

        # Check if user exists and is enabled
        user = frappe.get_doc("User", self.user)
        if user.enabled != 1:
            frappe.throw("User must be an enabled user")

    def validate_business(self):
        """Validate that business exists."""
        if not self.business:
            frappe.throw("Business is required")

        # Check if business exists
        business = frappe.get_doc("Business", self.business)
        if not business:
            frappe.throw("Business does not exist")

    def validate_role(self):
        """Validate role assignments."""
        if not self.role:
            frappe.throw("Role is required")

        # Validate is_owner flag
        if self.is_owner and self.role != "Owner":
            frappe.throw("Is Owner flag requires role to be 'Owner'")

        # Validate only one active owner per business
        if self.role == "Owner" and self.status == "Active":
            existing_owner = frappe.get_all(
                "Business Member",
                filters={
                    "business": self.business,
                    "role": "Owner",
                    "status": "Active",
                    "name": ["!=", self.name],
                },
                fields=["name"],
            )
            if existing_owner:
                frappe.throw("A business can only have one active Owner. Please deactivate the existing owner first.")

        # Prevent Manager from creating Owner role
        if self.role == "Owner" and not self.is_new():
            user = frappe.session.user
            from osduo_business_connect.business.business import get_user_role_in_business
            current_role = get_user_role_in_business(user, self.business)
            if current_role == "Manager":
                frappe.throw("Managers cannot create or modify Owner role")

    def validate_unique_membership(self):
        """Validate that user doesn't have duplicate active membership."""
        if self.status == "Active":
            existing = frappe.get_all(
                "Business Member",
                filters={
                    "business": self.business,
                    "user": self.user,
                    "status": "Active",
                    "name": ["!=", self.name],
                },
                fields=["name"],
            )
            if existing:
                frappe.throw("This user already has an active membership in this business")

    def set_defaults(self):
        """Set default values."""
        if not self.joined_on:
            self.joined_on = frappe.utils.today()

    def set_email_from_user(self):
        """Set email from linked user."""
        if self.user and not self.email:
            user = frappe.get_doc("User", self.user)
            self.email = user.email


def get_permission_query_conditions(user):
    """
    Return SQL conditions for filtering Business Member records.

    Users can only see members of businesses they belong to.
    """
    if not user:
        user = frappe.session.user

    # System Manager can see all members
    if "System Manager" in frappe.get_roles(user):
        return ""

    # Get businesses where user is a member
    from osduo_business_connect.business.business import get_user_businesses
    businesses = get_user_businesses(user)
    if not businesses:
        return "1=0"  # No access

    business_names = [b["name"] for b in businesses]
    return f"`tabBusiness Member`.business IN ({', '.join(['%s'] * len(business_names))})"


def has_permission(doc, ptype):
    """
    Check if user has permission on Business Member document.

    Business Owner/Manager can manage members.
    Members can read their own membership.
    """
    user = frappe.session.user

    # System Manager has full access
    if "System Manager" in frappe.get_roles(user):
        return True

    # Check if user is a member of this business
    from osduo_business_connect.business.business import get_user_businesses
    businesses = get_user_businesses(user)
    business_names = [b["name"] for b in businesses]

    if doc.business not in business_names:
        return False

    # Get user's role in this business
    from osduo_business_connect.business.business import get_user_role_in_business
    member_role = get_user_role_in_business(user, doc.business)

    if not member_role:
        return False

    # Check permissions based on role
    if ptype == "read":
        # Members can read their own membership or if they are Owner/Manager
        if doc.user == user:
            return True
        return member_role in ["Owner", "Manager"]
    elif ptype == "write":
        return member_role in ["Owner", "Manager"]
    elif ptype == "create":
        return member_role in ["Owner", "Manager"]
    elif ptype == "delete":
        return member_role == "Owner"

    return False
