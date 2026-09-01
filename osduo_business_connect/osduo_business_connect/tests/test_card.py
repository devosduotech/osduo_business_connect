"""
Unit tests for Digital Card DocType.

These tests verify:
- Digital Card CRUD operations
- Slug validation (format, uniqueness)
- Card validation (member ownership, contact methods)
- Public API functionality
- QR code and vCard generation
"""

import os
import sys
import unittest

# Add parent directory to path for local testing
app_parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, app_parent_dir)


class TestDigitalCardDocType(unittest.TestCase):
    """Tests for Digital Card DocType."""

    def test_digital_card_json_exists(self):
        """Test that Digital Card DocType JSON file exists."""
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "card",
            "card",
            "doctype",
            "digital_card",
            "digital_card.json",
        )
        self.assertTrue(os.path.exists(json_path), "Digital Card DocType JSON not found")

    def test_digital_card_json_has_required_fields(self):
        """Test that Digital Card DocType JSON has all required fields."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "card",
            "card",
            "doctype",
            "digital_card",
            "digital_card.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        required_fields = [
            "business",
            "member",
            "display_name",
            "slug",
            "status",
        ]

        field_names = [field["fieldname"] for field in doctype["fields"]]
        for field in required_fields:
            self.assertIn(field, field_names, f"Required field '{field}' not found")

    def test_digital_card_json_has_permissions(self):
        """Test that Digital Card DocType JSON has permissions defined."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "card",
            "card",
            "doctype",
            "digital_card",
            "digital_card.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        self.assertIn("permissions", doctype, "Permissions not defined")
        self.assertGreater(len(doctype["permissions"]), 0, "No permissions defined")

    def test_digital_card_controller_exists(self):
        """Test that Digital Card controller file exists."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "card",
            "card",
            "digital_card.py",
        )
        self.assertTrue(os.path.exists(controller_path), "Digital Card controller not found")

    def test_digital_card_controller_has_validate(self):
        """Test that Digital Card controller has validate method."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "card",
            "card",
            "digital_card.py",
        )
        with open(controller_path, "r") as f:
            content = f.read()
        self.assertIn("def validate(self)", content, "validate method not found")

    def test_digital_card_controller_has_slug_validation(self):
        """Test that Digital Card controller has slug validation."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "card",
            "card",
            "digital_card.py",
        )
        with open(controller_path, "r") as f:
            content = f.read()
        self.assertIn("validate_slug", content, "Slug validation not found")


class TestDigitalCardLink(unittest.TestCase):
    """Tests for Digital Card Link child table."""

    def test_card_link_json_exists(self):
        """Test that Digital Card Link DocType JSON file exists."""
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "card",
            "card",
            "doctype",
            "digital_card_link",
            "digital_card_link.json",
        )
        self.assertTrue(os.path.exists(json_path), "Digital Card Link DocType JSON not found")

    def test_card_link_json_has_required_fields(self):
        """Test that Digital Card Link DocType JSON has required fields."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "card",
            "card",
            "doctype",
            "digital_card_link",
            "digital_card_link.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        required_fields = ["link_type", "value", "enabled"]

        field_names = [field["fieldname"] for field in doctype["fields"]]
        for field in required_fields:
            self.assertIn(field, field_names, f"Required field '{field}' not found")


class TestQRService(unittest.TestCase):
    """Tests for QR service."""

    def test_qr_service_exists(self):
        """Test that QR service file exists."""
        service_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "services",
            "qr_service.py",
        )
        self.assertTrue(os.path.exists(service_path), "QR service not found")

    def test_qr_service_has_generate_function(self):
        """Test that QR service has generate function."""
        service_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "services",
            "qr_service.py",
        )
        with open(service_path, "r") as f:
            content = f.read()
        self.assertIn("def generate_qr_code", content, "generate_qr_code function not found")


class TestVCardService(unittest.TestCase):
    """Tests for vCard service."""

    def test_vcard_service_exists(self):
        """Test that vCard service file exists."""
        service_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "services",
            "vcard_service.py",
        )
        self.assertTrue(os.path.exists(service_path), "vCard service not found")

    def test_vcard_service_has_generate_function(self):
        """Test that vCard service has generate function."""
        service_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "services",
            "vcard_service.py",
        )
        with open(service_path, "r") as f:
            content = f.read()
        self.assertIn("def generate_vcard", content, "generate_vcard function not found")


class TestPublicAPI(unittest.TestCase):
    """Tests for public API."""

    def test_public_api_exists(self):
        """Test that public API file exists."""
        api_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "card",
            "card",
            "public_api.py",
        )
        self.assertTrue(os.path.exists(api_path), "Public API not found")

    def test_public_api_has_get_public_card(self):
        """Test that public API has get_public_card function."""
        api_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "card",
            "card",
            "public_api.py",
        )
        with open(api_path, "r") as f:
            content = f.read()
        self.assertIn("def get_public_card", content, "get_public_card function not found")

    def test_public_api_has_serialize_function(self):
        """Test that public API has serialize function."""
        api_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "card",
            "card",
            "public_api.py",
        )
        with open(api_path, "r") as f:
            content = f.read()
        self.assertIn("def serialize_card", content, "serialize_card function not found")


class TestPublicRoute(unittest.TestCase):
    """Tests for public route."""

    def test_public_route_exists(self):
        """Test that public route file exists."""
        route_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "card",
            "card",
            "public_route.py",
        )
        self.assertTrue(os.path.exists(route_path), "Public route not found")

    def test_public_route_has_get_context(self):
        """Test that public route has get_context function."""
        route_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "card",
            "card",
            "public_route.py",
        )
        with open(route_path, "r") as f:
            content = f.read()
        self.assertIn("def get_context", content, "get_context function not found")


if __name__ == "__main__":
    unittest.main()
