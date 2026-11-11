# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Dynamic ``robots.txt`` for Business Connect.

Frappe core serves ``/robots.txt`` straight from ``Website Settings.robots_txt``,
so the ``Sitemap:`` line is frozen at whichever origin was set when the value
was last written — on a multi-tenant subdomain bench that can end up as the
bare site name (``http://customer.connect/sitemap.xml``).

This app overrides ``/robots.txt`` (see ``www/robots.py``) and rebuilds it on
every request: the crawl rules come from the administrator's ``robots_txt`` (or
the bundled defaults when unset), and the ``Sitemap:`` line is always
re-resolved for the host that served the request via
:func:`osduo_business_connect.utils.urls.get_sitemap_base_url`. A customer
therefore never has to hand-maintain a robots file per domain, and a stale
sitemap URL can never be served.
"""

from __future__ import annotations

# Bundled crawl rules. Public business / product / service / card routes are
# server-rendered HTML, so the private desk and API areas can be disallowed
# without affecting indexing.
DEFAULT_ROBOTS_RULES = (
    "User-agent: *",
    "Allow: /",
    "Disallow: /app/",
    "Disallow: /api/",
    "Disallow: /login",
    "Disallow: /printview",
    "Disallow: /dashboard/",
    "Disallow: /analytics",
)


def _drop_sitemap_lines(body):
    """Return ``body`` with any ``Sitemap:`` lines removed (case-insensitive)."""
    kept = [line for line in (body or "").splitlines() if not line.strip().lower().startswith("sitemap:")]
    return "\n".join(kept).strip("\n")


def compose_robots_txt(rules_body, base_url):
    """Build the final robots text from a rules body and a resolved origin.

    ``rules_body`` is the administrator's rules (may be empty, may contain an
    old ``Sitemap:`` line); it is normalised and the correct, current sitemap
    declaration is appended. Pure function — no Frappe access — so it is unit
    testable on its own.
    """
    rules = _drop_sitemap_lines(rules_body)
    if not rules:
        rules = "\n".join(DEFAULT_ROBOTS_RULES)
    return f"{rules}\n\nSitemap: {base_url}/sitemap.xml\n"


def _configured_rules():
    """Rules the administrator set, from Website Settings or a config file."""
    import frappe

    rules = frappe.db.get_single_value("Website Settings", "robots_txt") or ""
    if not rules.strip():
        conf_path = (frappe.local.conf or {}).get("robots_txt")
        if conf_path:
            rules = frappe.read_file(conf_path) or ""
    return rules


def build_robots_txt():
    """Full robots.txt served for the current request."""
    from osduo_business_connect.utils.urls import get_sitemap_base_url

    return compose_robots_txt(_configured_rules(), get_sitemap_base_url())
