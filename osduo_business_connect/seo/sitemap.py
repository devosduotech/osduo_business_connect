# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Database-driven sitemaps for OSDuo Business Connect.

Public pages created by the app:

- Business profile  ``/b/<business_slug>``
- Product profile   ``/b/<business_slug>/products/<product_slug>``
- Service profile   ``/b/<business_slug>/services/<service_slug>``
- Digital card      ``/c/<card_slug>``

``/sitemap.xml`` is a **sitemap index** that points at four per-type
sitemaps. Each sitemap is generated from the live published records and
cached in Redis, so a newly published record appears on the next request
without any manual list to maintain.

Refresh strategy
----------------

1. **Event based** — :func:`invalidate_sitemap_cache` is wired to the
   Business / Showcase Product / Showcase Service / Digital Card
   ``on_update``, ``on_submit``, ``on_cancel`` and ``on_trash`` events in
   ``hooks.py``. Any publication change clears the cache so the next
   crawl sees the current state.
2. **Full regeneration** — :func:`generate_sitemaps` runs on the
   ``0 2 */3 * *`` cron entry in ``hooks.py``. It rebuilds and warms every
   cache and logs the URL counts (and any errors).

Nothing is ever written to disk, so there is no stale file to replace and
no "publish then wait three days" window. Search engines discover
``/sitemap.xml`` through ``robots.txt`` (see ``seo/robots.py`` and
``www/robots.py``) and recrawl it on their own schedule — the app never pushes
to Google.

The cache stores relative paths only; the absolute origin is added per request
by :func:`get_render_entries` using
:func:`osduo_business_connect.utils.urls.get_sitemap_base_url`. That keeps a
multi-tenant subdomain site correct even when its ``host_name`` is not yet
configured, and means the scheduled rebuild can never bake the wrong host.

Run manually with::

    bench --site <site> execute osduo_business_connect.seo.sitemap.generate_sitemaps
"""

from __future__ import annotations

import frappe
from frappe.utils import getdate

from osduo_business_connect.utils.urls import get_sitemap_base_url

# Cache keys and TTL. A short TTL is a safety net; event based invalidation
# is what keeps the sitemaps current between scheduled runs.
CACHE_PREFIX = "osduo_bc_sitemap::"
CACHE_TTL = 6 * 60 * 60  # seconds

# Logical sitemap names, in sitemap-index order.
KINDS = ("businesses", "products", "services", "cards")

# Public file served for each logical sitemap.
SITEMAP_FILES = {
    "businesses": "sitemap-businesses.xml",
    "products": "sitemap-products.xml",
    "services": "sitemap-services.xml",
    "cards": "sitemap-cards.xml",
}

# The sitemap index itself.
INDEX_FILE = "sitemap.xml"

# Google's hard limit is 50,000 URLs / 50 MB per sitemap. Warn well before
# that so chunking can be added before a sitemap is rejected.
MAX_URLS_PER_SITEMAP = 45000


def _cache_key(kind):
    return f"{CACHE_PREFIX}{kind}"


def _lastmod(value):
    """Return ``YYYY-MM-DD`` for a datetime, or ``None`` when unavailable."""
    if not value:
        return None
    return getdate(value).strftime("%Y-%m-%d")


def _path(*parts):
    """Relative URL path for an entry, without the origin.

    Cached entries stay origin-independent so a scheduled rebuild can never
    bake the wrong host; the origin is added at render time per request by
    :func:`get_render_entries`.
    """
    return "/".join(str(p).strip("/") for p in parts)


def _absolute(entries):
    """Return ``entries`` with an absolute ``loc`` for the current host."""
    base = get_sitemap_base_url()
    return [
        {"loc": f"{base}/{e['path']}", "lastmod": e.get("lastmod")}
        for e in entries
    ]


def get_business_entries():
    """Published, publicly visible business profiles."""
    rows = frappe.db.sql(
        """
        SELECT slug, modified
        FROM `tabBusiness`
        WHERE status = 'Published'
          AND public_profile_enabled = 1
          AND docstatus < 2
          AND slug IS NOT NULL AND slug != ''
        ORDER BY modified DESC
        """,
        as_dict=True,
    )
    return [{"path": _path("b", r.slug), "lastmod": _lastmod(r.modified)} for r in rows]


def _get_child_entries(doctype, segment):
    """Published products/services whose parent business is public."""
    rows = frappe.db.sql(
        f"""
        SELECT c.slug AS slug, b.slug AS business_slug, c.modified AS modified
        FROM `tab{doctype}` c
        INNER JOIN `tabBusiness` b ON b.name = c.business
        WHERE c.status = 'Published'
          AND c.docstatus < 2
          AND c.slug IS NOT NULL AND c.slug != ''
          AND b.status = 'Published'
          AND b.public_profile_enabled = 1
          AND b.docstatus < 2
          AND b.slug IS NOT NULL AND b.slug != ''
        ORDER BY c.modified DESC
        """,
        as_dict=True,
    )
    return [
        {
            "path": _path("b", r.business_slug, segment, r.slug),
            "lastmod": _lastmod(r.modified),
        }
        for r in rows
    ]


def get_product_entries():
    return _get_child_entries("Showcase Product", "products")


def get_service_entries():
    return _get_child_entries("Showcase Service", "services")


def get_card_entries():
    """Published public digital cards whose parent business is public."""
    rows = frappe.db.sql(
        """
        SELECT c.slug AS slug, c.modified AS modified
        FROM `tabDigital Card` c
        INNER JOIN `tabBusiness` b ON b.name = c.business
        WHERE c.status = 'Published'
          AND c.docstatus < 2
          AND c.public_profile_enabled = 1
          AND c.slug IS NOT NULL AND c.slug != ''
          AND b.status = 'Published'
          AND b.public_profile_enabled = 1
          AND b.docstatus < 2
        ORDER BY c.modified DESC
        """,
        as_dict=True,
    )
    return [{"path": _path("c", r.slug), "lastmod": _lastmod(r.modified)} for r in rows]


def get_index_entries():
    """One ``<sitemap>`` entry per child sitemap, with its newest ``lastmod``."""
    links = []
    for kind in KINDS:
        entries = get_cached_entries(kind)
        lastmod = max((e["lastmod"] for e in entries if e.get("lastmod")), default=None)
        links.append({"path": SITEMAP_FILES[kind], "lastmod": lastmod})
    return links


def get_entries(kind):
    """Return the raw (uncached) URL entries for ``kind``."""
    if kind == "businesses":
        return get_business_entries()
    if kind == "products":
        return get_product_entries()
    if kind == "services":
        return get_service_entries()
    if kind == "cards":
        return get_card_entries()
    if kind == "index":
        return get_index_entries()
    frappe.throw(f"Unknown sitemap kind: {kind}")


def get_cached_entries(kind):
    """Return the URL entries for ``kind``, served from Redis when warm."""
    cached = frappe.cache.get_value(_cache_key(kind))
    if cached is not None:
        return cached

    entries = get_entries(kind)
    frappe.cache.set_value(_cache_key(kind), entries, expires_in_sec=CACHE_TTL)
    return entries


def get_render_entries(kind):
    """Cached entries for ``kind`` with absolute URLs for the current host.

    Called by the ``www`` sitemap controllers. The cache stores relative paths
    (see :func:`_path`), so the origin is resolved per request from
    ``get_sitemap_base_url()`` — the configured ``host_name`` or, failing that,
    the host the sitemap was requested on.
    """
    return _absolute(get_cached_entries(kind))


def invalidate_sitemap_cache(doc=None, method=None):
    """``doc_events`` hook — drop every cached sitemap.

    Registered for Business / Showcase Product / Showcase Service /
    Digital Card create/update/submit/cancel/delete events so a publication
    change is reflected on the very next request.
    """
    for kind in (*KINDS, "index"):
        frappe.cache.delete_value(_cache_key(kind))


def generate_sitemaps():
    """Scheduled full regeneration (every 3 days).

    Clears the cache, rebuilds every sitemap and logs the URL counts so a
    silent failure (empty query, missing table) shows up in the Error Log
    instead of quietly serving an empty sitemap.
    """
    invalidate_sitemap_cache()

    counts = {}
    errors = []
    for kind in (*KINDS, "index"):
        try:
            count = len(get_cached_entries(kind))
            counts[kind] = count
            if kind != "index" and count > MAX_URLS_PER_SITEMAP:
                frappe.log_error(
                    title=f"Sitemap '{kind}' is getting large",
                    message=(
                        f"{count} URLs exceeds the {MAX_URLS_PER_SITEMAP} warning "
                        "threshold; add chunking before reaching 50,000."
                    ),
                )
        except Exception:
            errors.append(kind)
            frappe.log_error(
                title=f"Sitemap generation failed: {kind}",
                message=frappe.get_traceback(),
            )

    message = f"OSDuo Business Connect sitemaps regenerated: {counts}"
    if errors:
        message += f" — failed: {errors}"
    frappe.logger().info(message)
    return {"counts": counts, "errors": errors}
