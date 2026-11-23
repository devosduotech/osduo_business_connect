import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

APP_DIR = os.path.join(os.path.dirname(__file__), "..")
SHOWCASE_DIR = os.path.join(APP_DIR, "showcase")
CARD_DIR = os.path.join(APP_DIR, "card")
PAGES_DIR = os.path.join(APP_DIR, "templates", "pages")


class TestShowcasePublicAPI(unittest.TestCase):
    """Public product/service listing data comes from the live page controllers.

    The old showcase/public_api.py helpers were never whitelisted or routed and
    duplicated the queries in templates/pages, so they were removed.
    """

    def test_dead_module_is_not_shipped(self):
        self.assertFalse(os.path.exists(os.path.join(SHOWCASE_DIR, "public_api.py")))

    def test_live_listing_controllers_exist(self):
        for path in (
            os.path.join(PAGES_DIR, "business", "business.py"),
            os.path.join(PAGES_DIR, "card", "card.py"),
            os.path.join(PAGES_DIR, "product", "product.py"),
            os.path.join(PAGES_DIR, "service", "service.py"),
        ):
            self.assertTrue(os.path.exists(path), path)

    def test_listings_only_expose_published_rows(self):
        for page in ("business", "card"):
            path = os.path.join(PAGES_DIR, page, f"{page}.py")
            with open(path) as f:
                source = f.read()
            self.assertIn('"status": "Published"', source)
            self.assertIn("docstatus", source)
        for page in ("product", "service"):
            path = os.path.join(PAGES_DIR, page, f"{page}.py")
            with open(path) as f:
                source = f.read()
            self.assertIn("get_public_business_by_slug", source)


if __name__ == "__main__":
    unittest.main()
