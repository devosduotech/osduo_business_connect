# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Website page-cache invalidation for published records.

Frappe caches each rendered website page under ``website_page::<path>`` for ~30
minutes. When a Business / Showcase Product / Showcase Service / Digital Card is
created, edited, (un)published or deleted, any cached HTML for the pages that
show that record must be dropped so the change — including edited SEO text — is
served on the next request instead of up to half an hour later (SEO_PLAN
acceptance #7). The sitemap-cache half of this was handled in v1.2.9
(:func:`osduo_business_connect.seo.sitemap.invalidate_sitemap_cache`); this module
clears the page cache, in both directions:

- a product / service / card change clears its own page **and** its parent
  business page (which renders the item);
- a Business change clears its own page **and** every child product / service /
  card page (they inherit its logo and the Organization / LocalBusiness refs).

The route math is a pure function so the mapping is testable without a bench;
the hook wrapper is the only part that touches ``frappe``/the database.
"""

from __future__ import annotations


def product_route(business_slug: str, product_slug: str) -> str:
    return f"b/{business_slug}/products/{product_slug}"


def service_route(business_slug: str, service_slug: str) -> str:
    return f"b/{business_slug}/services/{service_slug}"


def business_route(business_slug: str) -> str:
    return f"b/{business_slug}"


def card_route(card_slug: str) -> str:
    return f"c/{card_slug}"


def routes_to_invalidate(
    *,
    doctype: str,
    slug: str | None = None,
    business_slug: str | None = None,
    product_slugs: tuple[str, ...] = (),
    service_slugs: tuple[str, ...] = (),
    card_slugs: tuple[str, ...] = (),
) -> set[str]:
    """Return the cached page routes that depend on the changed record.

    Pure — no ``frappe`` — so it can be unit-tested directly. ``slug`` is the
    changed record's own route slug; ``business_slug`` its parent; the plural
    sets are the children (only consulted for a Business change).
    """
    routes: set[str] = set()
    doctype = doctype or ""

    if doctype == "Business":
        if slug:
            routes.add(business_route(slug))
        for child in product_slugs:
            routes.add(product_route(slug, child))
        for child in service_slugs:
            routes.add(service_route(slug, child))
        for child in card_slugs:
            routes.add(card_route(child))
    elif doctype == "Showcase Product" and slug and business_slug:
        routes.add(product_route(business_slug, slug))
        routes.add(business_route(business_slug))
    elif doctype == "Showcase Service" and slug and business_slug:
        routes.add(service_route(business_slug, slug))
        routes.add(business_route(business_slug))
    elif doctype == "Digital Card" and slug:
        routes.add(card_route(slug))
        if business_slug:
            routes.add(business_route(business_slug))

    return routes


# --------------------------------------------------------------------------- #
# Frappe-backed wrapper. ``frappe`` is imported inside so the module stays
# import-safe for the structural test suite.
# --------------------------------------------------------------------------- #

def _child_slugs(business_name: str) -> dict:
    import frappe

    def slugs(doctype):
        return tuple(
            r["slug"]
            for r in frappe.get_all(
                doctype, filters={"business": business_name}, fields=["slug"], ignore_permissions=True
            )
            if r.get("slug")
        )

    return {
        "product_slugs": slugs("Showcase Product"),
        "service_slugs": slugs("Showcase Service"),
        "card_slugs": slugs("Digital Card"),
    }


def _business_slug(business_name: str) -> str | None:
    import frappe

    if not business_name:
        return None
    return frappe.db.get_value("Business", business_name, "slug")


def on_publication_change(doc, method=None):
    """``doc_events`` hook for the four public doctypes (create/update/submit/cancel/delete)."""
    from frappe.website.utils import delete_page_cache

    doctype = doc.get("doctype") or getattr(doc, "doctype", "")
    slug = doc.get("slug")

    if doctype == "Business":
        kwargs = {"doctype": doctype, "slug": slug}
        if doc.get("name"):
            # Frappe passes a Document, not a dict: it supports .get() but is
            # not subscriptable. Using .get() here also keeps dict-based tests
            # and direct calls working.
            kwargs.update(_child_slugs(doc.get("name")))
    else:
        kwargs = {
            "doctype": doctype,
            "slug": slug,
            "business_slug": _business_slug(doc.get("business")),
        }

    # delete_page_cache takes the stripped route, exactly as Frappe keys the
    # website page cache; it is a no-op for a page that was never cached.
    for route in routes_to_invalidate(**kwargs):
        delete_page_cache(route)
