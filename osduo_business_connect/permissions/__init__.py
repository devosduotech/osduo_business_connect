# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Centralized Permissions Module

This module provides permission functions for all OSDuo DocTypes.
It acts as a dispatcher to the appropriate DocType-specific permission logic.

Frappe's has_permission hook receives: doc, user, ptype
- True → do not deny
- False → deny
- None → fall back to normal permission behaviour
"""

import frappe


def has_permission(doc, user=None, ptype=None):
    """
    Central permission check dispatcher.

    Routes to the appropriate DocType-specific permission function.
    """
    if not user:
        user = frappe.session.user

    doctype = doc.doctype

    if doctype == "Business":
        from osduo_business_connect.business.core import (
            has_permission as business_has_permission,
        )
        return business_has_permission(doc, user=user, ptype=ptype)

    elif doctype == "Business Member":
        from osduo_business_connect.business.doctype.business_member.business_member import (
            has_permission as member_has_permission,
        )
        return member_has_permission(doc, user=user, ptype=ptype)

    elif doctype == "Digital Card":
        from osduo_business_connect.card.doctype.digital_card.digital_card import (
            has_permission as card_has_permission,
        )
        return card_has_permission(doc, user=user, ptype=ptype)

    elif doctype == "Showcase Product":
        from osduo_business_connect.showcase.doctype.showcase_product.showcase_product import (
            has_permission as product_has_permission,
        )
        return product_has_permission(doc, user=user, ptype=ptype)

    elif doctype == "Showcase Service":
        from osduo_business_connect.showcase.doctype.showcase_service.showcase_service import (
            has_permission as service_has_permission,
        )
        return service_has_permission(doc, user=user, ptype=ptype)

    elif doctype == "Enquiry":
        from osduo_business_connect.enquiry.core import (
            has_permission as enquiry_has_permission,
        )
        return enquiry_has_permission(doc, user=user, ptype=ptype)

    elif doctype == "Engagement Event":
        from osduo_business_connect.analytics.doctype.engagement_event.engagement_event import (
            has_permission as event_has_permission,
        )
        return event_has_permission(doc, user=user, ptype=ptype)

    elif doctype == "BC Theme":
        from osduo_business_connect.showcase.doctype.bc_theme.bc_theme import (
            has_permission as theme_has_permission,
        )
        return theme_has_permission(doc, user=user, ptype=ptype)

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
