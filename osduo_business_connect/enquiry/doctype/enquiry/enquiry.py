# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Enquiry DocType Controller

This is a minimal stub. The full implementation lives in enquiry/core.py
to avoid Python import conflicts when module name == doctype name.
Frappe's load_doctype_module expects this file to exist.
"""

from osduo_business_connect.enquiry.core import (
    Enquiry,
    get_permission_query_conditions,
    has_permission,
)

__all__ = [
    "Enquiry",
    "get_permission_query_conditions",
    "has_permission",
]
