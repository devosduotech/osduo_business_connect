"""
Monkey-patch Frappe v16 CSRF validation to exempt guest enquiry submission.

Frappe v16 validates CSRF in HTTPRequest.__init__() BEFORE checking if
the endpoint is whitelisted. Guest users have no CSRF token, so all
POST API calls fail. This patch exempts specific paths from CSRF checks.
"""

import frappe
import frappe.auth


_original_init = frappe.auth.HTTPRequest.__init__

# Paths that should bypass CSRF validation (guest form submissions)
CSRF_EXEMPT_PATHS = [
    "/submit-enquiry",
]


def _patched_init(self):
    """Intercept CSRF check before the original __init__ runs."""
    import frappe

    # Check if this is a POST to an exempt path
    if hasattr(frappe, "request") and frappe.request:
        path = frappe.request.path or ""
        method = getattr(frappe.request, "method", "GET")
        if method == "POST" and any(path.startswith(p) for p in CSRF_EXEMPT_PATHS):
            # Temporarily store the original method, set to GET to bypass CSRF
            self.method = "GET"
            _original_init(self)
            # Restore actual method for later use
            self.method = method
            frappe.local.request.method = method
            return

    _original_init(self)


def apply_patch():
    """Apply the CSRF exemption monkey-patch."""
    frappe.auth.HTTPRequest.__init__ = _patched_init
