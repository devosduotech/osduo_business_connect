# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Website route fix for Frappe v16 bug.

Frappe's evaluate_dynamic_routes does urls.match("/" + path) but path
already has a leading slash, causing //b/osduo instead of /b/osduo.
This module monkey-patches the function to strip the extra slash.
"""

import frappe
from werkzeug.routing import Map, NotFound


def patched_evaluate_dynamic_routes(rules, path):
    """Fixed version that doesn't double the leading slash."""
    route_map = Map(rules)
    endpoint = None

    if hasattr(frappe.local, "request") and frappe.local.request.environ:
        urls = route_map.bind_to_environ(frappe.local.request.environ)
        try:
            # Fix: don't prepend "/" if path already starts with "/"
            match_path = path if path.startswith("/") else "/" + path
            endpoint, args = urls.match(match_path)
            if args:
                frappe.local.no_cache = 1
                frappe.local.form_dict.update(args)
        except NotFound:
            pass

    return endpoint


def apply_patch():
    """Apply the monkey-patch to frappe.website.path_resolver."""
    import frappe.website.path_resolver as pr
    pr.evaluate_dynamic_routes = patched_evaluate_dynamic_routes
