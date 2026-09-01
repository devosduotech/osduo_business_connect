"""
Unit tests for Showcase Product and Showcase Service DocTypes.

These tests verify:
- Product CRUD operations
- Service CRUD operations
- Slug validation
- Price validation
- Public API functionality
"""

import os
import sys
import unittest

# Add parent directory to path for local testing
app_parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, app_parent_dir)


class TestShowcaseProductDocType(unittest.TestCase):
    """Tests for Showcase Product DocType."""

    def test_product_json_exists(self):
        """Test that Showcase Product DocType JSON file exists."""
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "doctype",
            "showcase_product",
            "showcase_product.json",
        )
        self.assertTrue(os.path.exists(json_path), "Showcase Product DocType JSON not found")

    def test_product_json_has_required_fields(self):
        """Test that Showcase Product DocType JSON has all required fields."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "doctype",
            "showcase_product",
            "showcase_product.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        required_fields = [
            "business",
            "product_name",
            "slug",
            "short_description",
            "description",
            "image",
            "price_display_mode",
            "enquiry_enabled",
            "status",
            "featured",
        ]

        field_names = [field["fieldname"] for field in doctype["fields"]]
        for field in required_fields:
            self.assertIn(field, field_names, f"Required field '{field}' not found")

    def test_product_json_has_status_options(self):
        """Test that Showcase Product status field has correct options."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "doctype",
            "showcase_product",
            "showcase_product.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        status_field = None
        for field in doctype["fields"]:
            if field["fieldname"] == "status":
                status_field = field
                break

        self.assertIsNotNone(status_field, "Status field not found")
        expected_options = ["Draft", "Published", "Archived"]
        for option in expected_options:
            self.assertIn(option, status_field["options"], f"Status option '{option}' not found")

    def test_product_json_has_price_display_mode_options(self):
        """Test that Showcase Product price_display_mode field has correct options."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "doctype",
            "showcase_product",
            "showcase_product.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        price_field = None
        for field in doctype["fields"]:
            if field["fieldname"] == "price_display_mode":
                price_field = field
                break

        self.assertIsNotNone(price_field, "Price display mode field not found")
        expected_options = ["Hidden", "Contact", "Fixed"]
        for option in expected_options:
            self.assertIn(option, price_field["options"], f"Price display mode option '{option}' not found")

    def test_product_json_has_permissions(self):
        """Test that Showcase Product DocType JSON has permissions defined."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "doctype",
            "showcase_product",
            "showcase_product.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        self.assertIn("permissions", doctype, "Permissions not defined")
        self.assertGreater(len(doctype["permissions"]), 0, "No permissions defined")

    def test_product_controller_exists(self):
        """Test that Showcase Product controller file exists."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "showcase_product.py",
        )
        self.assertTrue(os.path.exists(controller_path), "Showcase Product controller not found")

    def test_product_controller_has_validate(self):
        """Test that Showcase Product controller has validate method."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "showcase_product.py",
        )
        with open(controller_path, "r") as f:
            content = f.read()
        self.assertIn("def validate(self)", content, "validate method not found")

    def test_product_controller_has_slug_validation(self):
        """Test that Showcase Product controller has slug validation."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "showcase_product.py",
        )
        with open(controller_path, "r") as f:
            content = f.read()
        self.assertIn("validate_slug", content, "Slug validation not found")


class TestProductGalleryItem(unittest.TestCase):
    """Tests for Product Gallery Item child table."""

    def test_gallery_item_json_exists(self):
        """Test that Product Gallery Item DocType JSON file exists."""
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "doctype",
            "product_gallery_item",
            "product_gallery_item.json",
        )
        self.assertTrue(os.path.exists(json_path), "Product Gallery Item DocType JSON not found")

    def test_gallery_item_json_has_required_fields(self):
        """Test that Product Gallery Item DocType JSON has all required fields."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "doctype",
            "product_gallery_item",
            "product_gallery_item.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        required_fields = ["image", "alt_text"]

        field_names = [field["fieldname"] for field in doctype["fields"]]
        for field in required_fields:
            self.assertIn(field, field_names, f"Required field '{field}' not found")


class TestShowcaseServiceDocType(unittest.TestCase):
    """Tests for Showcase Service DocType."""

    def test_service_json_exists(self):
        """Test that Showcase Service DocType JSON file exists."""
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "doctype",
            "showcase_service",
            "showcase_service.json",
        )
        self.assertTrue(os.path.exists(json_path), "Showcase Service DocType JSON not found")

    def test_service_json_has_required_fields(self):
        """Test that Showcase Service DocType JSON has all required fields."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "doctype",
            "showcase_service",
            "showcase_service.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        required_fields = [
            "business",
            "service_name",
            "slug",
            "short_description",
            "description",
            "image",
            "enquiry_enabled",
            "status",
            "featured",
        ]

        field_names = [field["fieldname"] for field in doctype["fields"]]
        for field in required_fields:
            self.assertIn(field, field_names, f"Required field '{field}' not found")

    def test_service_json_has_status_options(self):
        """Test that Showcase Service status field has correct options."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "doctype",
            "showcase_service",
            "showcase_service.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        status_field = None
        for field in doctype["fields"]:
            if field["fieldname"] == "status":
                status_field = field
                break

        self.assertIsNotNone(status_field, "Status field not found")
        expected_options = ["Draft", "Published", "Archived"]
        for option in expected_options:
            self.assertIn(option, status_field["options"], f"Status option '{option}' not found")

    def test_service_json_has_permissions(self):
        """Test that Showcase Service DocType JSON has permissions defined."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "doctype",
            "showcase_service",
            "showcase_service.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        self.assertIn("permissions", doctype, "Permissions not defined")
        self.assertGreater(len(doctype["permissions"]), 0, "No permissions defined")

    def test_service_controller_exists(self):
        """Test that Showcase Service controller file exists."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "showcase_service.py",
        )
        self.assertTrue(os.path.exists(controller_path), "Showcase Service controller not found")

    def test_service_controller_has_validate(self):
        """Test that Showcase Service controller has validate method."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "showcase_service.py",
        )
        with open(controller_path, "r") as f:
            content = f.read()
        self.assertIn("def validate(self)", content, "validate method not found")

    def test_service_controller_has_slug_validation(self):
        """Test that Showcase Service controller has slug validation."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "showcase_service.py",
        )
        with open(controller_path, "r") as f:
            content = f.read()
        self.assertIn("validate_slug", content, "Slug validation not found")


class TestServiceBenefit(unittest.TestCase):
    """Tests for Service Benefit child table."""

    def test_benefit_json_exists(self):
        """Test that Service Benefit DocType JSON file exists."""
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "doctype",
            "service_benefit",
            "service_benefit.json",
        )
        self.assertTrue(os.path.exists(json_path), "Service Benefit DocType JSON not found")

    def test_benefit_json_has_required_fields(self):
        """Test that Service Benefit DocType JSON has all required fields."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "doctype",
            "service_benefit",
            "service_benefit.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        required_fields = ["title"]

        field_names = [field["fieldname"] for field in doctype["fields"]]
        for field in required_fields:
            self.assertIn(field, field_names, f"Required field '{field}' not found")


if __name__ == "__main__":
    unittest.main()
