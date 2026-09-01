# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Centralized Permissions Module

This module provides permission functions for all OSDuo DocTypes.
It acts as a dispatcher to the appropriate DocType-specific permission logic.
"""

import frappe


def has_permission(doc, ptype):
    """
    Central permission check dispatcher.

    Routes to the appropriate DocType-specific permission function.
    """
    doctype = doc.doctype

    if doctype == "Business":
        from osduo_business_connect.business.business import (
            has_permission as business_has_permission,
        )
        return business_has_permission(doc, ptype)

    elif doctype == "Business Member":
        from osduo_business_connect.business.business_member import (
            has_permission as member_has_permission,
        )
        return member_has_permission(doc, ptype)

    elif doctype == "Digital Card":
        from osduo_business_connect.card.digital_card import (
            has_permission as card_has_permission,
        )
        return card_has_permission(doc, ptype)

    elif doctype == "Showcase Product":
        from osduo_business_connect.showcase.showcase_product import (
            has_permission as product_has_permission,
        )
        return product_has_permission(doc, ptype)

    elif doctype == "Showcase Service":
        from osduo_business_connect.showcase.showcase_service import (
            has_permission as service_has_permission,
        )
        return service_has_permission(doc, ptype)

    elif doctype == "Enquiry":
        from osduo_business_connect.enquiry.enquiry import (
            has_permission as enquiry_has_permission,
        )
        return enquiry_has_permission(doc, ptype)

    elif doctype == "Page Section":
        from osduo_business_connect.showcase.page_section import (
            has_permission as section_has_permission,
        )
        return section_has_permission(doc, ptype)

    elif doctype == "Engagement Event":
        from osduo_business_connect.analytics.engagement_event import (
            has_permission as event_has_permission,
        )
        return event_has_permission(doc, ptype)

    elif doctype == "Theme":
        from osduo_business_connect.showcase.theme import (
            has_permission as theme_has_permission,
        )
        return theme_has_permission(doc, ptype)

    return False


def get_permission_query_conditions(user):
    """
    Central permission query conditions dispatcher.

    Returns SQL WHERE conditions to filter list queries based on user permissions.
    """
    if not user:
        user = frappe.session.user

    # System Manager sees everything
    if "System Manager" in frappe.get_roles(user):
        return ""

    return ""
