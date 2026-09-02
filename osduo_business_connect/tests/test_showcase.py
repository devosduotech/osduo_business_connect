import os
import sys
import json
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

APP_DIR = os.path.join(os.path.dirname(__file__), "..")
SHOWCASE_DIR = os.path.join(APP_DIR, "showcase")


def load_json(path):
    with open(path) as f:
        return json.load(f)


class TestShowcaseProductDocType(unittest.TestCase):
    """Verify Showcase Product DocType JSON structure."""

    def setUp(self):
        self.json_path = os.path.join(SHOWCASE_DIR, "doctype", "showcase_product", "showcase_product.json")
        self.data = load_json(self.json_path)

    def test_json_exists(self):
        self.assertTrue(os.path.exists(self.json_path))

    def test_required_fields(self):
        fieldnames = [f["fieldname"] for f in self.data["fields"]]
        for req in ["business", "product_name", "slug", "price_display_mode", "status"]:
            self.assertIn(req, fieldnames)

    def test_status_options(self):
        status_field = next(f for f in self.data["fields"] if f["fieldname"] == "status")
        options = status_field["options"]
        for st in ["Draft", "Published", "Archived"]:
            self.assertIn(st, options)

    def test_price_display_mode_options(self):
        price_field = next(f for f in self.data["fields"] if f["fieldname"] == "price_display_mode")
        options = price_field["options"]
        for mode in ["Hidden", "Contact", "Fixed"]:
            self.assertIn(mode, options)

    def test_has_permissions(self):
        roles = [p["role"] for p in self.data["permissions"]]
        self.assertTrue(len(roles) > 0)

    def test_controller_exists(self):
        path = os.path.join(SHOWCASE_DIR, "doctype", "showcase_product", "showcase_product.py")
        self.assertTrue(os.path.exists(path))


class TestProductGalleryItem(unittest.TestCase):
    """Verify Product Gallery Item child table."""

    def setUp(self):
        self.json_path = os.path.join(SHOWCASE_DIR, "doctype", "product_gallery_item", "product_gallery_item.json")
        self.data = load_json(self.json_path)

    def test_json_exists(self):
        self.assertTrue(os.path.exists(self.json_path))

    def test_required_fields(self):
        fieldnames = [f["fieldname"] for f in self.data["fields"]]
        self.assertIn("image", fieldnames)


class TestShowcaseServiceDocType(unittest.TestCase):
    """Verify Showcase Service DocType JSON structure."""

    def setUp(self):
        self.json_path = os.path.join(SHOWCASE_DIR, "doctype", "showcase_service", "showcase_service.json")
        self.data = load_json(self.json_path)

    def test_json_exists(self):
        self.assertTrue(os.path.exists(self.json_path))

    def test_required_fields(self):
        fieldnames = [f["fieldname"] for f in self.data["fields"]]
        for req in ["business", "service_name", "slug", "status"]:
            self.assertIn(req, fieldnames)

    def test_status_options(self):
        status_field = next(f for f in self.data["fields"] if f["fieldname"] == "status")
        options = status_field["options"]
        for st in ["Draft", "Published", "Archived"]:
            self.assertIn(st, options)

    def test_has_permissions(self):
        roles = [p["role"] for p in self.data["permissions"]]
        self.assertTrue(len(roles) > 0)

    def test_controller_exists(self):
        path = os.path.join(SHOWCASE_DIR, "doctype", "showcase_service", "showcase_service.py")
        self.assertTrue(os.path.exists(path))


class TestServiceBenefit(unittest.TestCase):
    """Verify Service Benefit child table."""

    def setUp(self):
        self.json_path = os.path.join(SHOWCASE_DIR, "doctype", "service_benefit", "service_benefit.json")
        self.data = load_json(self.json_path)

    def test_json_exists(self):
        self.assertTrue(os.path.exists(self.json_path))

    def test_required_fields(self):
        fieldnames = [f["fieldname"] for f in self.data["fields"]]
        self.assertIn("title", fieldnames)


if __name__ == "__main__":
    unittest.main()
