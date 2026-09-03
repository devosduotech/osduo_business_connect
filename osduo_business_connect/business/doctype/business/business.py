# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Business DocType Controller

This is a minimal stub. The full implementation lives in business/core.py
to avoid Python import conflicts when module name == doctype name.
Frappe's load_doctype_module expects this file to exist.
"""

from osduo_business_connect.business.core import (
    Business,
    get_permission_query_conditions,
    has_permission,
    get_user_businesses,
    get_user_role_in_business,
    get_business_by_slug,
)

__all__ = [
    "Business",
    "get_permission_query_conditions",
    "has_permission",
    "get_user_businesses",
    "get_user_role_in_business",
    "get_business_by_slug",
]
