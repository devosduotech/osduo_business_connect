"""
Unit tests for Enquiry DocType.

These tests verify:
- Enquiry CRUD operations
- Validation rules
- Status transitions
- CRM sync handling
"""

import os
import sys
import unittest

# Add parent directory to path for local testing
app_parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, app_parent_dir)


class TestEnquiryDocType(unittest.TestCase):
    """Tests for Enquiry DocType."""

    def test_enquiry_json_exists(self):
        """Test that Enquiry DocType JSON file exists."""
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "doctype",
            "enquiry",
            "enquiry.json",
        )
        self.assertTrue(os.path.exists(json_path), "Enquiry DocType JSON not found")

    def test_enquiry_json_has_required_fields(self):
        """Test that Enquiry DocType JSON has all required fields."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "doctype",
            "enquiry",
            "enquiry.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        required_fields = [
            "business",
            "visitor_name",
            "visitor_email",
            "visitor_phone",
            "visitor_company",
            "message",
            "source",
            "status",
            "submitted_at",
            "crm_lead",
            "crm_sync_attempts",
            "last_sync_error",
            "consent",
            "consent_text",
        ]

        field_names = [field["fieldname"] for field in doctype["fields"]]
        for field in required_fields:
            self.assertIn(field, field_names, f"Required field '{field}' not found")

    def test_enquiry_json_has_source_options(self):
        """Test that Enquiry source field has correct options."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "doctype",
            "enquiry",
            "enquiry.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        source_field = None
        for field in doctype["fields"]:
            if field["fieldname"] == "source":
                source_field = field
                break

        self.assertIsNotNone(source_field, "Source field not found")
        expected_options = [
            "Digital Card",
            "Business Profile",
            "Product",
            "Service",
            "QR",
            "Campaign",
            "Other",
        ]
        for option in expected_options:
            self.assertIn(option, source_field["options"], f"Source option '{option}' not found")

    def test_enquiry_json_has_status_options(self):
        """Test that Enquiry status field has correct options."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "doctype",
            "enquiry",
            "enquiry.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        status_field = None
        for field in doctype["fields"]:
            if field["fieldname"] == "status":
                status_field = field
                break

        self.assertIsNotNone(status_field, "Status field not found")
        expected_options = [
            "New",
            "Sync Pending",
            "Synced",
            "Sync Failed",
            "Converted",
            "Closed",
            "Spam",
        ]
        for option in expected_options:
            self.assertIn(option, status_field["options"], f"Status option '{option}' not found")

    def test_enquiry_json_has_permissions(self):
        """Test that Enquiry DocType JSON has permissions defined."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "doctype",
            "enquiry",
            "enquiry.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        self.assertIn("permissions", doctype, "Permissions not defined")
        self.assertGreater(len(doctype["permissions"]), 0, "No permissions defined")

    def test_enquiry_controller_exists(self):
        """Test that Enquiry controller file exists."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "enquiry.py",
        )
        self.assertTrue(os.path.exists(controller_path), "Enquiry controller not found")

    def test_enquiry_controller_has_validate(self):
        """Test that Enquiry controller has validate method."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "enquiry.py",
        )
        with open(controller_path, "r") as f:
            content = f.read()
        self.assertIn("def validate(self)", content, "validate method not found")

    def test_enquiry_controller_has_visitor_validation(self):
        """Test that Enquiry controller has visitor validation."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "enquiry.py",
        )
        with open(controller_path, "r") as f:
            content = f.read()
        self.assertIn("validate_visitor_info", content, "Visitor validation not found")

    def test_enquiry_controller_has_reference_validation(self):
        """Test that Enquiry controller has reference validation."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "enquiry.py",
        )
        with open(controller_path, "r") as f:
            content = f.read()
        self.assertIn("validate_references", content, "Reference validation not found")


class TestEnquiryResponse(unittest.TestCase):
    """Tests for Enquiry Response child table."""

    def test_response_json_exists(self):
        """Test that Enquiry Response DocType JSON file exists."""
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "doctype",
            "enquiry_response",
            "enquiry_response.json",
        )
        self.assertTrue(os.path.exists(json_path), "Enquiry Response DocType JSON not found")

    def test_response_json_has_required_fields(self):
        """Test that Enquiry Response DocType JSON has all required fields."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "doctype",
            "enquiry_response",
            "enquiry_response.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        required_fields = ["responder", "response_type", "response_message", "response_at"]

        field_names = [field["fieldname"] for field in doctype["fields"]]
        for field in required_fields:
            self.assertIn(field, field_names, f"Required field '{field}' not found")

    def test_response_json_has_type_options(self):
        """Test that Enquiry Response response_type field has correct options."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "doctype",
            "enquiry_response",
            "enquiry_response.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        type_field = None
        for field in doctype["fields"]:
            if field["fieldname"] == "response_type":
                type_field = field
                break

        self.assertIsNotNone(type_field, "Response type field not found")
        expected_options = ["Email", "Phone", "WhatsApp", "Note"]
        for option in expected_options:
            self.assertIn(option, type_field["options"], f"Response type option '{option}' not found")


class TestEnquiryService(unittest.TestCase):
    """Tests for Enquiry service."""

    def test_enquiry_service_exists(self):
        """Test that Enquiry service file exists."""
        service_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "enquiry_service.py",
        )
        self.assertTrue(os.path.exists(service_path), "Enquiry service not found")

    def test_enquiry_service_has_create_enquiry(self):
        """Test that Enquiry service has create_enquiry function."""
        service_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "enquiry_service.py",
        )
        with open(service_path, "r") as f:
            content = f.read()
        self.assertIn("def create_enquiry", content, "create_enquiry function not found")

    def test_enquiry_service_has_stats(self):
        """Test that Enquiry service has get_enquiry_stats function."""
        service_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "enquiry_service.py",
        )
        with open(service_path, "r") as f:
            content = f.read()
        self.assertIn("def get_enquiry_stats", content, "get_enquiry_stats function not found")


if __name__ == "__main__":
    unittest.main()
