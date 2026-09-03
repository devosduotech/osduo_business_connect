"""
Monkey-patch Frappe v16 CSRF validation to exempt guest enquiry submission.

Frappe v16 validates CSRF in HTTPRequest.__init__() BEFORE checking if
the endpoint is whitelisted. Guest users have no CSRF token, so all
POST website route calls fail.

Solution: Override validate_csrf_token to check multiple sources for
the request path/method and skip CSRF for exempt paths.
"""

import frappe
import frappe.auth


_original_validate_csrf_token = frappe.auth.HTTPRequest.validate_csrf_token

# Paths that should bypass CSRF validation (guest form submissions)
CSRF_EXEMPT_PATHS = ["/submit-enquiry"]


def _get_request_info(self):
    """Try multiple sources to get request path and method."""
    # Source 1: WSGI environ on self
    environ = getattr(self, "environ", None)
    if environ:
        yield environ.get("PATH_INFO", ""), environ.get("REQUEST_METHOD", "GET")

    # Source 2: HTTPRequest instance attributes (Frappe stores these)
    path = getattr(self, "path", None)
    method = getattr(self, "method", None)
    if path and method:
        yield path, method

    # Source 3: werkzeug request proxy
    try:
        from werkzeug.local import LocalProxy
        from werkzeug.test import EnvironBuilder
        import flask
        req = flask.request
        yield req.path, req.method
    except Exception:
        pass

    # Source 4: frappe.local
    try:
        local_req = getattr(frappe.local, "request", None)
        if local_req:
            yield getattr(local_req, "path", ""), getattr(local_req, "method", "")
    except Exception:
        pass


def _patched_validate_csrf_token(self):
    """Skip CSRF for exempt paths, otherwise call original validation."""
    for path, method in _get_request_info(self):
        if method == "POST" and any(path.startswith(p) for p in CSRF_EXEMPT_PATHS):
            return  # Skip CSRF for exempt paths

    _original_validate_csrf_token(self)


def apply_patch():
    """Apply the CSRF exemption monkey-patch."""
    frappe.auth.HTTPRequest.validate_csrf_token = _patched_validate_csrf_token
