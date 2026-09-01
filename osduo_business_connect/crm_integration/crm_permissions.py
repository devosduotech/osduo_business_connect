# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
CRM Permissions Module

Handles CRM Lead isolation between businesses.
"""

import frappe


def get_lead_permission_query_conditions(user):
    """
    Return SQL conditions for filtering CRM Lead records based on business ownership.
    
    This ensures users can only see CRM Leads that belong to their businesses.
    
    Args:
        user: User email
        
    Returns:
        str: SQL WHERE condition fragment
    """
    if not user:
        user = frappe.session.user
    
    # System Manager can see all leads
    if "System Manager" in frappe.get_roles(user):
        return ""
    
    # Get businesses where user is a member
    from osduo_business_connect.business.business import get_user_businesses
    
    businesses = get_user_businesses(user)
    if not businesses:
        return "1=0"  # No access
    
    business_names = [b["name"] for b in businesses]
    
    # Use direct string construction for permission query conditions
    # This is the standard Frappe pattern for permission queries
    business_list = ", ".join(["%s"] * len(business_names))
    
    # Filter leads by osduo_business field
    # Note: This assumes CRM Lead has the osduo_business custom field
    return f"`tabCRM Lead`.osduo_business IN ({business_list})"


def has_lead_permission(doc, ptype):
    """
    Check if user has permission on CRM Lead document.
    
    This is called by Frappe's permission system when accessing CRM Lead.
    
    Args:
        doc: CRM Lead document
        ptype: Permission type (read, write, create, delete)
        
    Returns:
        bool: True if permitted, False otherwise
    """
    user = frappe.session.user
    
    # System Manager has full access
    if "System Manager" in frappe.get_roles(user):
        return True
    
    # If no osduo_business field, allow standard CRM permissions
    if not hasattr(doc, "osduo_business") or not doc.osduo_business:
        return True
    
    # Get businesses where user is a member
    from osduo_business_connect.business.business import get_user_businesses
    
    businesses = get_user_businesses(user)
    business_names = [b["name"] for b in businesses]
    
    # Check if lead belongs to user's business
    if doc.osduo_business not in business_names:
        return False
    
    # Get user's role in the business
    from osduo_business_connect.business.business import get_user_role_in_business
    
    member_role = get_user_role_in_business(user, doc.osduo_business)
    
    if not member_role:
        return False
    
    # Check permissions based on role
    if ptype == "read":
        return True
    elif ptype == "write":
        return member_role in ["Owner", "Manager", "CRM User"]
    elif ptype == "create":
        return member_role in ["Owner", "Manager", "CRM User"]
    elif ptype == "delete":
        return member_role == "Owner"
    
    return False
