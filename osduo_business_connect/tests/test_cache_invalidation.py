# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Phase F — website page-cache invalidation on publication changes.

``utils/cache.py`` splits a pure route-mapping function from the Frappe wrapper.
The mapping is asserted directly; the wrapper is driven against a stubbed
``frappe`` that records which routes ``delete_page_cache`` is asked to drop.
"""

import importlib
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

APP_DIR = os.path.join(os.path.dirname(__file__), "..")

from osduo_business_connect.utils.cache import (  # noqa: E402
    business_route,
    card_route,
    product_route,
    routes_to_invalidate,
    service_route,
)


def read(*parts):
    with open(os.path.join(APP_DIR, *parts)) as f:
        return f.read()


class TestRouteMapping(unittest.TestCase):
    def test_business_page_clears_self_and_all_children(self):
        routes = routes_to_invalidate(
            doctype="Business",
            slug="osduo",
            product_slugs=("erp", "widget"),
            service_slugs=("consulting",),
            card_slugs=("karthic",),
        )
        self.assertEqual(
            routes,
            {
                "b/osduo",
                "b/osduo/products/erp",
                "b/osduo/products/widget",
                "b/osduo/services/consulting",
                "c/karthic",
            },
        )

    def test_product_clears_itself_and_parent_business(self):
        routes = routes_to_invalidate(
            doctype="Showcase Product", slug="erp", business_slug="osduo"
        )
        self.assertEqual(routes, {"b/osduo/products/erp", "b/osduo"})

    def test_service_clears_itself_and_parent_business(self):
        routes = routes_to_invalidate(
            doctype="Showcase Service", slug="consulting", business_slug="osduo"
        )
        self.assertEqual(routes, {"b/osduo/services/consulting", "b/osduo"})

    def test_card_clears_itself_and_parent_business(self):
        routes = routes_to_invalidate(doctype="Digital Card", slug="karthic", business_slug="osduo")
        self.assertEqual(routes, {"c/karthic", "b/osduo"})

    def test_card_without_business_only_clears_itself(self):
        routes = routes_to_invalidate(doctype="Digital Card", slug="solo", business_slug=None)
        self.assertEqual(routes, {"c/solo"})

    def test_missing_slug_or_business_is_noop(self):
        # A product with no business_slug, or a blank slug, must not emit a route.
        self.assertEqual(routes_to_invalidate(doctype="Showcase Product", slug="erp"), set())
        self.assertEqual(routes_to_invalidate(doctype="Business", slug=None), set())

    def test_business_children_only_when_present(self):
        routes = routes_to_invalidate(doctype="Business", slug="osduo")
        self.assertEqual(routes, {"b/osduo"})  # no children passed

    def test_helpers_match_expected_shape(self):
        self.assertEqual(business_route("osduo"), "b/osduo")
        self.assertEqual(product_route("osduo", "erp"), "b/osduo/products/erp")
        self.assertEqual(service_route("osduo", "consulting"), "b/osduo/services/consulting")
        self.assertEqual(card_route("karthic"), "c/karthic")


class FakeDoc:
    """Mimic a Frappe Document: ``get()`` works, but it is not subscriptable."""

    def __init__(self, **fields):
        self.__dict__.update(fields)

    def get(self, key, default=None):
        return getattr(self, key, default)


def _install_fake_frappe(deleted, get_all_rows, business_slugs):
    """Put a minimal stub frappe + frappe.website.utils in sys.modules.

    ``delete_page_cache`` records each route it is asked to drop; ``get_all`` /
    ``db.get_value`` supply the child slugs and parent-business slug the wrapper
    looks up. Returns the saved-module map for teardown.
    """
    frappe = types.ModuleType("frappe")

    def get_all(doctype, filters=None, fields=None, ignore_permissions=False):
        return get_all_rows.get(doctype, [])

    frappe.get_all = get_all
    frappe.db = types.SimpleNamespace(get_value=lambda doctype, name, field: business_slugs.get(name))

    website = types.ModuleType("frappe.website")
    website_utils = types.ModuleType("frappe.website.utils")
    website_utils.delete_page_cache = lambda path: deleted.append(path)
    website.utils = website_utils
    frappe.website = website

    modules = {"frappe": frappe, "frappe.website": website, "frappe.website.utils": website_utils}
    saved = {name: sys.modules.get(name) for name in modules}
    sys.modules.update(modules)
    return saved


class TestPublicationChangeHook(unittest.TestCase):
    def test_wrapper_calls_delete_page_cache_for_expected_routes(self):
        deleted = []
        saved = _install_fake_frappe(
            deleted,
            get_all_rows={
                "Showcase Product": [{"slug": "erp"}, {"slug": "widget"}],
                "Showcase Service": [{"slug": "consulting"}],
                "Digital Card": [{"slug": "karthic"}],
            },
            business_slugs={"BIZ-1": "osduo"},
        )
        try:
            import osduo_business_connect.utils.cache as cache_mod

            importlib.reload(cache_mod)
            business_doc = FakeDoc(doctype="Business", slug="osduo", name="BIZ-1")
            cache_mod.on_publication_change(business_doc, "on_update")
            self.assertEqual(
                sorted(deleted),
                sorted(
                    [
                        "b/osduo",
                        "b/osduo/products/erp",
                        "b/osduo/products/widget",
                        "b/osduo/services/consulting",
                        "c/karthic",
                    ]
                ),
            )

            deleted.clear()
            product_doc = FakeDoc(doctype="Showcase Product", slug="erp", business="BIZ-1")
            cache_mod.on_publication_change(product_doc, "on_submit")
            self.assertEqual(sorted(deleted), sorted(["b/osduo/products/erp", "b/osduo"]))

            deleted.clear()
            card_doc = FakeDoc(doctype="Digital Card", slug="karthic", business="BIZ-1")
            cache_mod.on_publication_change(card_doc, "on_update")
            self.assertEqual(sorted(deleted), sorted(["c/karthic", "b/osduo"]))
        finally:
            for name, value in saved.items():
                if value is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = value


class TestHookWiring(unittest.TestCase):
    def doc_events(self):
        return read("hooks.py")

    def test_page_cache_handler_registered_with_sitemap(self):
        hooks = self.doc_events()
        self.assertIn("_PAGE_CACHE_INVALIDATE = \"osduo_business_connect.utils.cache.on_publication_change\"", hooks)
        self.assertIn("_PUBLICATION_EVENTS = [_SITEMAP_INVALIDATE, _PAGE_CACHE_INVALIDATE]", hooks)
        for dt in ("Business", "Showcase Product", "Showcase Service", "Digital Card"):
            self.assertIn(f'"{dt}"', hooks)
        # every event for those doctypes maps to the combined list
        self.assertGreaterEqual(hooks.count('_PUBLICATION_EVENTS'), 16)

    def test_handler_never_subscripts_documents(self):
        source = read("utils", "cache.py")
        self.assertNotIn('doc["', source)
        self.assertNotIn("doc['", source)

    def test_product_url_live_flag_now_true(self):
        hooks = self.doc_events()
        self.assertIn('"product_url_live": True', hooks)
        self.assertNotIn('"product_url_live": False', hooks)


if __name__ == "__main__":
    unittest.main()
