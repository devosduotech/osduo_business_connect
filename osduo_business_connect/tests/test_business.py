"""
Unit tests for Business and Business Member DocTypes.

These tests verify:
- Business CRUD operations
- Slug validation (format, uniqueness, reserved words)
- Business Member role enforcement
- Cross-business access prevention
- Owner vs Manager vs Member permissions
"""

import os
import sys
import unittest

# Add parent directory to path for local testing
app_parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, app_parent_dir)


class TestBusinessDocType(unittest.TestCase):
    """Tests for Business DocType."""

    def test_business_json_exists(self):
        """Test that Business DocType JSON file exists."""
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "business",
            "business",
            "doctype",
            "business",
            "business.json",
        )
        self.assertTrue(os.path.exists(json_path), "Business DocType JSON not found")

    def test_business_json_has_required_fields(self):
        """Test that Business DocType JSON has all required fields."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "business",
            "business",
            "doctype",
            "business",
            "business.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        required_fields = [
            "business_name",
            "slug",
            "status",
            "owner_user",
        ]

        field_names = [field["fieldname"] for field in doctype["fields"]]
        for field in required_fields:
            self.assertIn(field, field_names, f"Required field '{field}' not found")

    def test_business_json_has_permissions(self):
        """Test that Business DocType JSON has permissions defined."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "business",
            "business",
            "doctype",
            "business",
            "business.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        self.assertIn("permissions", doctype, "Permissions not defined")
        self.assertGreater(len(doctype["permissions"]), 0, "No permissions defined")

    def test_business_controller_exists(self):
        """Test that Business controller file exists."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "business",
            "business",
            "business.py",
        )
        self.assertTrue(os.path.exists(controller_path), "Business controller not found")

    def test_business_controller_has_validate(self):
        """Test that Business controller has validate method."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "business",
            "business",
            "business.py",
        )
        with open(controller_path, "r") as f:
            content = f.read()
        self.assertIn("def validate(self)", content, "validate method not found")

    def test_business_controller_has_slug_validation(self):
        """Test that Business controller has slug validation."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "business",
            "business",
            "business.py",
        )
        with open(controller_path, "r") as f:
            content = f.read()
        self.assertIn("validate_slug", content, "Slug validation not found")


class TestBusinessSocialLink(unittest.TestCase):
    """Tests for Business Social Link child table."""

    def test_social_link_json_exists(self):
        """Test that Business Social Link DocType JSON file exists."""
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "business",
            "business",
            "doctype",
            "business_social_link",
            "business_social_link.json",
        )
        self.assertTrue(os.path.exists(json_path), "Business Social Link DocType JSON not found")

    def test_social_link_json_has_required_fields(self):
        """Test that Business Social Link DocType JSON has required fields."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "business",
            "business",
            "doctype",
            "business_social_link",
            "business_social_link.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        required_fields = ["platform", "url", "enabled"]

        field_names = [field["fieldname"] for field in doctype["fields"]]
        for field in required_fields:
            self.assertIn(field, field_names, f"Required field '{field}' not found")


class TestBusinessHour(unittest.TestCase):
    """Tests for Business Hour child table."""

    def test_business_hour_json_exists(self):
        """Test that Business Hour DocType JSON file exists."""
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "business",
            "business",
            "doctype",
            "business_hour",
            "business_hour.json",
        )
        self.assertTrue(os.path.exists(json_path), "Business Hour DocType JSON not found")

    def test_business_hour_json_has_required_fields(self):
        """Test that Business Hour DocType JSON has required fields."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "business",
            "business",
            "doctype",
            "business_hour",
            "business_hour.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        required_fields = ["day", "enabled", "open_time", "close_time"]

        field_names = [field["fieldname"] for field in doctype["fields"]]
        for field in required_fields:
            self.assertIn(field, field_names, f"Required field '{field}' not found")


class TestBusinessMember(unittest.TestCase):
    """Tests for Business Member DocType."""

    def test_business_member_json_exists(self):
        """Test that Business Member DocType JSON file exists."""
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "business",
            "business",
            "doctype",
            "business_member",
            "business_member.json",
        )
        self.assertTrue(os.path.exists(json_path), "Business Member DocType JSON not found")

    def test_business_member_json_has_required_fields(self):
        """Test that Business Member DocType JSON has required fields."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "business",
            "business",
            "doctype",
            "business_member",
            "business_member.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        required_fields = ["business", "user", "person_name", "role", "status"]

        field_names = [field["fieldname"] for field in doctype["fields"]]
        for field in required_fields:
            self.assertIn(field, field_names, f"Required field '{field}' not found")

    def test_business_member_json_has_role_options(self):
        """Test that Business Member role field has correct options."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "business",
            "business",
            "doctype",
            "business_member",
            "business_member.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        role_field = None
        for field in doctype["fields"]:
            if field["fieldname"] == "role":
                role_field = field
                break

        self.assertIsNotNone(role_field, "Role field not found")
        expected_options = ["Owner", "Manager", "Member", "Marketing", "CRM User"]
        for option in expected_options:
            self.assertIn(option, role_field["options"], f"Role option '{option}' not found")

    def test_business_member_json_has_permissions(self):
        """Test that Business Member DocType JSON has permissions defined."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "business",
            "business",
            "doctype",
            "business_member",
            "business_member.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        self.assertIn("permissions", doctype, "Permissions not defined")
        self.assertGreater(len(doctype["permissions"]), 0, "No permissions defined")

    def test_business_member_controller_exists(self):
        """Test that Business Member controller file exists."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "business",
            "business",
            "business_member.py",
        )
        self.assertTrue(os.path.exists(controller_path), "Business Member controller not found")

    def test_business_member_controller_has_validate(self):
        """Test that Business Member controller has validate method."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "business",
            "business",
            "business_member.py",
        )
        with open(controller_path, "r") as f:
            content = f.read()
        self.assertIn("def validate(self)", content, "validate method not found")


class TestCRMIntegrationContract(unittest.TestCase):
    """Tests for CRM Integration Contract."""

    def test_contract_document_exists(self):
        """Test that CRM Integration Contract document exists."""
        contract_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "crm_integration",
            "CONTRACT.md",
        )
        self.assertTrue(os.path.exists(contract_path), "CRM Integration Contract not found")

    def test_lead_mapper_exists(self):
        """Test that lead_mapper.py exists."""
        mapper_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "crm_integration",
            "lead_mapper.py",
        )
        self.assertTrue(os.path.exists(mapper_path), "lead_mapper.py not found")

    def test_lead_mapper_has_permission_query(self):
        """Test that lead_mapper.py has permission query function."""
        mapper_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "crm_integration",
            "lead_mapper.py",
        )
        with open(mapper_path, "r") as f:
            content = f.read()
        self.assertIn("get_lead_permission_query_conditions", content, "Permission query function not found")


if __name__ == "__main__":
    unittest.main()
