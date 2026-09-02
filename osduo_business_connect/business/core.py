# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Business Core Module

Contains the Business class and all helper functions.
Separated from the doctype directory to avoid Python import conflicts
when module name == doctype name == file name (all 'business').
"""

import frappe
from frappe.model.document import Document


class Business(Document):
    """
    Business DocType - Root ownership record for all business-owned data.

    This is the fundamental ownership boundary for:
    - Team members (Business Member)
    - Digital cards
    - Products and services
    - Sections and theme
    - Analytics
    - Enquiries

    It is also the future tenancy boundary for v2 SaaS.
    """

    def before_validate(self):
        """Pre-process data before validation."""
        self.normalize_fields()
        self.normalize_urls()

    def validate(self):
        """Authoritative location for business validation."""
        self.validate_slug()
        self.validate_owner_user()
        self.validate_contact_methods()

    def before_save(self):
        """Pre-save operations."""
        self.set_defaults()

    def after_insert(self):
        """Post-insert operations - create owner membership."""
        self.create_owner_membership()

    def on_update(self):
        """Post-save operations."""
        pass

    def create_owner_membership(self):
        """
        Automatically create Business Member record for the owner.
        
        This ensures the owner can manage the business immediately after creation.
        """
        # Check if owner membership already exists
        existing = frappe.get_all(
            "Business Member",
            filters={
                "business": self.name,
                "user": self.owner_user,
                "role": "Owner",
            },
            fields=["name"],
            limit=1,
        )
        
        if not existing:
            user_doc = frappe.get_doc("User", self.owner_user)
            member = frappe.get_doc({
                "doctype": "Business Member",
                "business": self.name,
                "user": self.owner_user,
                "person_name": user_doc.full_name or self.owner_user,
                "email": self.owner_user,
                "role": "Owner",
                "is_owner": 1,
                "status": "Active",
            })
            member.insert(ignore_permissions=True)
            frappe.db.commit()

    def normalize_fields(self):
        """Normalize field values."""
        # Normalize slug to lowercase
        if self.slug:
            self.slug = self.slug.lower().strip()

    def normalize_urls(self):
        """Normalize URL fields to add https:// if missing."""
        from osduo_business_connect.utils.sanitize import normalize_url_fields
        normalize_url_fields(self)

        # Normalize email
        if self.email:
            self.email = self.email.lower().strip()

    def validate_slug(self):
        """Validate slug format and uniqueness."""
        if not self.slug:
            frappe.throw("Public Slug is required")

        # Check slug format: only lowercase letters, numbers, and hyphens
        import re
        if not re.match(r'^[a-z0-9-]+$', self.slug):
            frappe.throw("Slug can only contain lowercase letters, numbers, and hyphens")

        # Check for leading/trailing hyphen
        if self.slug.startswith('-') or self.slug.endswith('-'):
            frappe.throw("Slug cannot start or end with a hyphen")

        # Check reserved slugs
        reserved_slugs = [
            'admin', 'api', 'www', 'mail', 'ftp', 'localhost',
            'webmail', 'smtp', 'pop', 'ns1', 'ns2', 'ns3', 'ns4',
            'cdn', 'assets', 'static', 'media', 'files', 'images',
            'css', 'js', 'img', 'fonts', 'icons', 'favicon',
            'robots', 'sitemap', 'search', 'login', 'logout',
            'register', 'signup', 'signin', 'account', 'profile',
            'settings', 'dashboard', 'help', 'support', 'contact',
            'about', 'blog', 'news', 'careers', 'jobs', 'legal',
            'privacy', 'terms', 'security', 'status', 'demo',
        ]
        if self.slug in reserved_slugs:
            frappe.throw(f"Slug '{self.slug}' is reserved and cannot be used")

        # Check uniqueness
        if self.is_new():
            exists = frappe.db.exists("Business", {"slug": self.slug})
            if exists:
                frappe.throw(f"Slug '{self.slug}' is already taken")
        else:
            exists = frappe.db.exists(
                "Business", {"slug": self.slug, "name": ["!=", self.name]}
            )
            if exists:
                frappe.throw(f"Slug '{self.slug}' is already taken")

    def validate_owner_user(self):
        """Validate that owner_user is enabled."""
        if not self.owner_user:
            frappe.throw("Business Owner is required")

        # Check if user is enabled
        user = frappe.get_doc("User", self.owner_user)
        if user.enabled != 1:
            frappe.throw("Business Owner must be an enabled user")

    def validate_contact_methods(self):
        """
        Validate contact methods based on status.
        
        Draft: Contact info is optional
        Published: At least one contact method required
        """
        if self.status == "Published":
            has_contact = any([
                self.email,
                self.phone,
                self.whatsapp,
                self.website,
            ])
            if not has_contact:
                frappe.throw("At least one contact method (email, phone, WhatsApp, or website) is required for published businesses")

    def set_defaults(self):
        """Set default values."""
        pass


def get_permission_query_conditions(user):
    """
    Return SQL conditions for filtering Business records based on user permissions.

    This ensures users can only see businesses they have access to.
    """
    if not user:
        user = frappe.session.user

    # System Manager can see all businesses
    if "System Manager" in frappe.get_roles(user):
        return ""

    # Get businesses where user is a member
    businesses = get_user_businesses(user)
    if not businesses:
        return "1=0"  # No access

    business_names = [b["name"] for b in businesses]
    return f"`tabBusiness`.name IN ({', '.join(['%s'] * len(business_names))})"


def has_permission(doc, ptype):
    """
    Check if user has permission on Business document.

    This is called by Frappe's permission system.
    """
    user = frappe.session.user

    # Guest can only read published businesses with public profile enabled
    if user == "Guest":
        if ptype == "read":
            return doc.status == "Published" and doc.public_profile_enabled
        return False

    # System Manager has full access
    if "System Manager" in frappe.get_roles(user):
        return True

    # Check if user is a member of this business
    businesses = get_user_businesses(user)
    business_names = [b["name"] for b in businesses]

    if doc.name not in business_names:
        return False

    # Get user's role in this business
    member_role = get_user_role_in_business(user, doc.name)

    if not member_role:
        return False

    # Check permissions based on role
    if ptype == "read":
        return True
    elif ptype == "write":
        return member_role in ["Owner", "Manager", "Marketing"]
    elif ptype == "create":
        return member_role == "Owner"
    elif ptype == "delete":
        return member_role == "Owner"

    return False


def get_user_businesses(user):
    """
    Get list of businesses where user is an active member.

    Returns:
        list: List of dictionaries with business name and role
    """
    if not user:
        user = frappe.session.user

    # Query Business Member table
    members = frappe.get_all(
        "Business Member",
        filters={
            "user": user,
            "status": "Active",
        },
        fields=["business", "role"],
    )

    return [
        {"name": m.business, "role": m.role}
        for m in members
    ]


def get_user_role_in_business(user, business):
    """
    Get user's role in a specific business.

    Args:
        user: User email
        business: Business name

    Returns:
        str: Role name (Owner, Manager, Member, Marketing, CRM User) or None
    """
    member = frappe.get_all(
        "Business Member",
        filters={
            "user": user,
            "business": business,
            "status": "Active",
        },
        fields=["role"],
    )

    if member:
        return member[0].role
    return None


def get_business_by_slug(slug):
    """
    Get a published business by its public slug.

    Args:
        slug: Business public slug

    Returns:
        dict: Business document data or None
    """
    if not slug:
        return None

    business = frappe.get_all(
        "Business",
        filters={
            "slug": slug,
            "status": "Published",
        },
        fields=["name", "slug", "business_name", "tagline", "logo", "status"],
        limit=1,
    )

    if business:
        return business[0]
    return None
