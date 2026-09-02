import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

APP_DIR = os.path.join(os.path.dirname(__file__), "..")
SHOWCASE_DIR = os.path.join(APP_DIR, "showcase")
CARD_DIR = os.path.join(APP_DIR, "card")


class TestShowcasePublicAPI(unittest.TestCase):
    """Verify showcase public API module."""

    def test_exists(self):
        path = os.path.join(SHOWCASE_DIR, "public_api.py")
        self.assertTrue(os.path.exists(path))

    def test_has_get_public_product(self):
        path = os.path.join(SHOWCASE_DIR, "public_api.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def get_public_product", content)

    def test_has_get_public_products(self):
        path = os.path.join(SHOWCASE_DIR, "public_api.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def get_public_products", content)

    def test_has_get_public_service(self):
        path = os.path.join(SHOWCASE_DIR, "public_api.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def get_public_service", content)

    def test_has_get_public_services(self):
        path = os.path.join(SHOWCASE_DIR, "public_api.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def get_public_services", content)

    def test_has_serialize_product(self):
        path = os.path.join(SHOWCASE_DIR, "public_api.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def serialize_product", content)

    def test_has_serialize_service(self):
        path = os.path.join(SHOWCASE_DIR, "public_api.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def serialize_service", content)


class TestProductRoute(unittest.TestCase):
    """Verify product route module."""

    def test_exists(self):
        path = os.path.join(SHOWCASE_DIR, "product_route.py")
        self.assertTrue(os.path.exists(path))

    def test_has_get_context(self):
        path = os.path.join(SHOWCASE_DIR, "product_route.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def get_context", content)


class TestServiceRoute(unittest.TestCase):
    """Verify service route module."""

    def test_exists(self):
        path = os.path.join(SHOWCASE_DIR, "service_route.py")
        self.assertTrue(os.path.exists(path))

    def test_has_get_context(self):
        path = os.path.join(SHOWCASE_DIR, "service_route.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def get_context", content)


if __name__ == "__main__":
    unittest.main()
