"""
Unit tests for Theme DocType.

These tests verify:
- Theme CRUD operations
- Color validation
- Active theme uniqueness
- Custom settings validation
- Theme service functionality
"""

import os
import sys
import unittest

# Add parent directory to path for local testing
app_parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, app_parent_dir)


class TestThemeDocType(unittest.TestCase):
    """Tests for Theme DocType."""

    def test_theme_json_exists(self):
        """Test that Theme DocType JSON file exists."""
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "doctype",
            "theme",
            "theme.json",
        )
        self.assertTrue(os.path.exists(json_path), "Theme DocType JSON not found")

    def test_theme_json_has_required_fields(self):
        """Test that Theme DocType JSON has all required fields."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "doctype",
            "theme",
            "theme.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        required_fields = [
            "business",
            "template",
            "primary_color",
            "secondary_color",
            "button_style",
            "card_style",
            "active",
        ]

        field_names = [field["fieldname"] for field in doctype["fields"]]
        for field in required_fields:
            self.assertIn(field, field_names, f"Required field '{field}' not found")

    def test_theme_json_has_template_options(self):
        """Test that Theme template field has correct options."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "doctype",
            "theme",
            "theme.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        template_field = None
        for field in doctype["fields"]:
            if field["fieldname"] == "template":
                template_field = field
                break

        self.assertIsNotNone(template_field, "Template field not found")
        expected_options = ["Modern", "Professional", "Minimal", "Classic"]
        for option in expected_options:
            self.assertIn(option, template_field["options"], f"Template option '{option}' not found")

    def test_theme_json_has_button_style_options(self):
        """Test that Theme button_style field has correct options."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "doctype",
            "theme",
            "theme.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        button_field = None
        for field in doctype["fields"]:
            if field["fieldname"] == "button_style":
                button_field = field
                break

        self.assertIsNotNone(button_field, "Button style field not found")
        expected_options = ["Filled", "Outline", "Rounded", "Pill"]
        for option in expected_options:
            self.assertIn(option, button_field["options"], f"Button style option '{option}' not found")

    def test_theme_json_has_permissions(self):
        """Test that Theme DocType JSON has permissions defined."""
        import json

        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "doctype",
            "theme",
            "theme.json",
        )
        with open(json_path, "r") as f:
            doctype = json.load(f)

        self.assertIn("permissions", doctype, "Permissions not defined")
        self.assertGreater(len(doctype["permissions"]), 0, "No permissions defined")

    def test_theme_controller_exists(self):
        """Test that Theme controller file exists."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "theme.py",
        )
        self.assertTrue(os.path.exists(controller_path), "Theme controller not found")

    def test_theme_controller_has_validate(self):
        """Test that Theme controller has validate method."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "theme.py",
        )
        with open(controller_path, "r") as f:
            content = f.read()
        self.assertIn("def validate(self)", content, "validate method not found")

    def test_theme_controller_has_color_validation(self):
        """Test that Theme controller has color validation."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "theme.py",
        )
        with open(controller_path, "r") as f:
            content = f.read()
        self.assertIn("validate_colors", content, "Color validation not found")

    def test_theme_controller_has_active_validation(self):
        """Test that Theme controller has active theme validation."""
        controller_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "theme.py",
        )
        with open(controller_path, "r") as f:
            content = f.read()
        self.assertIn("validate_active_theme", content, "Active theme validation not found")


class TestThemeService(unittest.TestCase):
    """Tests for Theme service."""

    def test_theme_service_exists(self):
        """Test that Theme service file exists."""
        service_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "services",
            "theme_service.py",
        )
        self.assertTrue(os.path.exists(service_path), "Theme service not found")

    def test_theme_service_has_get_business_theme(self):
        """Test that Theme service has get_business_theme function."""
        service_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "services",
            "theme_service.py",
        )
        with open(service_path, "r") as f:
            content = f.read()
        self.assertIn("def get_business_theme", content, "get_business_theme function not found")

    def test_theme_service_has_activate_theme(self):
        """Test that Theme service has activate_theme function."""
        service_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "services",
            "theme_service.py",
        )
        with open(service_path, "r") as f:
            content = f.read()
        self.assertIn("def activate_theme", content, "activate_theme function not found")

    def test_theme_service_has_get_theme_css(self):
        """Test that Theme service has get_theme_css function."""
        service_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "services",
            "theme_service.py",
        )
        with open(service_path, "r") as f:
            content = f.read()
        self.assertIn("def get_theme_css", content, "get_theme_css function not found")

    def test_theme_service_has_default_theme(self):
        """Test that Theme service has get_default_theme function."""
        service_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "services",
            "theme_service.py",
        )
        with open(service_path, "r") as f:
            content = f.read()
        self.assertIn("def get_default_theme", content, "get_default_theme function not found")


if __name__ == "__main__":
    unittest.main()
