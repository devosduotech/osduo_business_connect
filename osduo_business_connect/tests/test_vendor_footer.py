# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Phase E (P6) — sitewide OSDuo vendor attribution footer.

A single partial included in ``bc_base.html`` replaces the old per-page
"Powered by … connect.osduotech.com" footers. Checks the wiring, the gating,
and that the not-yet-live product URL is never emitted.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from osduo_business_connect.hooks import OSDUO_BRANDING
from osduo_business_connect.utils.website import get_branding_context

APP_DIR = os.path.join(os.path.dirname(__file__), "..")


def read(*parts):
    with open(os.path.join(APP_DIR, *parts)) as f:
        return f.read()


class TestVendorFooterPartial(unittest.TestCase):
    def setUp(self):
        self.partial = read("templates", "pages", "parts", "vendor_footer.html")

    def test_gated_by_show_vendor_credit(self):
        self.assertIn("bc_show_vendor_credit", self.partial)

    def test_links_credit_url_not_hardcoded(self):
        self.assertIn("{{ bc_credit_url }}", self.partial)
        self.assertNotIn("connect.osduotech.com", self.partial)

    def test_footer_landmark_with_label_no_nofollow(self):
        self.assertIn("<footer", self.partial)
        self.assertIn('aria-label="About this site"', self.partial)
        import re

        anchor = re.search(r"<a\b[^>]*>", self.partial).group(0)
        self.assertIn('rel="noopener"', anchor)
        self.assertNotIn("nofollow", anchor)  # the association is the point

    def test_uses_configurable_text(self):
        self.assertIn("{{ bc_vendor_credit_text }}", self.partial)

    def test_included_once_in_base(self):
        base = read("templates", "bc_base.html")
        self.assertEqual(base.count("vendor_footer.html"), 1)


class TestBrandingContext(unittest.TestCase):
    def _ctx(self):
        ctx = {"path": "/b/acme"}
        get_branding_context(ctx)
        return ctx

    def test_credit_url_is_vendor_site_while_product_offline(self):
        # product_url_live is False, so the footer must point at the vendor site.
        self.assertFalse(OSDUO_BRANDING["product_url_live"])
        ctx = self._ctx()
        self.assertEqual(ctx["bc_credit_url"], OSDUO_BRANDING["vendor_url"])
        self.assertNotIn(OSDUO_BRANDING["product_url"], str(ctx))

    def test_credit_url_follows_product_when_live(self):
        saved = OSDUO_BRANDING["product_url_live"]
        try:
            OSDUO_BRANDING["product_url_live"] = True
            ctx = self._ctx()
            self.assertEqual(ctx["bc_credit_url"], OSDUO_BRANDING["product_url"])
        finally:
            OSDUO_BRANDING["product_url_live"] = saved

    def test_all_vendor_keys_injected(self):
        ctx = self._ctx()
        for key in ("bc_credit_url", "bc_show_vendor_credit", "bc_vendor_credit_text", "bc_vendor_name", "bc_product_name"):
            self.assertIn(key, ctx, key)
        self.assertTrue(ctx["bc_show_vendor_credit"])


class TestOldFootersRemoved(unittest.TestCase):
    def test_no_inline_powered_by_in_page_templates(self):
        roots = ["business", "product", "service", "card"]
        for page in roots:
            for name in os.listdir(os.path.join(APP_DIR, "templates", "pages", page)):
                if name.endswith(".html"):
                    src = read("templates", "pages", page, name)
                    self.assertNotIn("Powered by", src, f"{page}/{name}")

    def test_no_connect_osduotech_links_left(self):
        import glob

        for path in glob.glob(os.path.join(APP_DIR, "templates", "**", "*.html"), recursive=True):
            src = open(path).read()
            self.assertNotIn("connect.osduotech.com", src, path)


if __name__ == "__main__":
    unittest.main()
