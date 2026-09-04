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


class TestThemeDocType(unittest.TestCase):
    """Verify BC Theme DocType JSON structure."""

    def setUp(self):
        self.json_path = os.path.join(SHOWCASE_DIR, "doctype", "bc_theme", "bc_theme.json")
        self.data = load_json(self.json_path)

    def test_json_exists(self):
        self.assertTrue(os.path.exists(self.json_path))

    def test_required_fields(self):
        fieldnames = [f["fieldname"] for f in self.data["fields"]]
        for req in ["theme_name", "template", "color_scheme", "primary_color", "secondary_color", "button_style"]:
            self.assertIn(req, fieldnames)

    def test_template_options(self):
        template_field = next(f for f in self.data["fields"] if f["fieldname"] == "template")
        options = template_field["options"]
        for tmpl in ["Modern", "Professional", "Minimal", "Classic"]:
            self.assertIn(tmpl, options)

    def test_color_scheme_options(self):
        color_field = next(f for f in self.data["fields"] if f["fieldname"] == "color_scheme")
        options = color_field["options"]
        for scheme in ["Violet", "Indigo", "Blue", "Green", "Yellow", "Orange", "Red", "Custom"]:
            self.assertIn(scheme, options)

    def test_button_style_options(self):
        btn_field = next(f for f in self.data["fields"] if f["fieldname"] == "button_style")
        options = btn_field["options"]
        for style in ["Filled", "Outline", "Rounded", "Pill"]:
            self.assertIn(style, options)

    def test_has_permissions(self):
        roles = [p["role"] for p in self.data["permissions"]]
        self.assertTrue(len(roles) > 0)

    def test_controller_exists(self):
        path = os.path.join(SHOWCASE_DIR, "doctype", "bc_theme", "bc_theme.py")
        self.assertTrue(os.path.exists(path))

    def test_controller_has_validate(self):
        path = os.path.join(SHOWCASE_DIR, "doctype", "bc_theme", "bc_theme.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("validate", content)


class TestThemeService(unittest.TestCase):
    """Verify theme service module."""

    def test_exists(self):
        path = os.path.join(APP_DIR, "services", "theme_service.py")
        self.assertTrue(os.path.exists(path))

    def test_has_get_business_theme(self):
        path = os.path.join(APP_DIR, "services", "theme_service.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def get_business_theme", content)

    def test_has_get_theme_data(self):
        path = os.path.join(APP_DIR, "services", "theme_service.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def get_theme_data", content)

    def test_has_get_default_theme(self):
        path = os.path.join(APP_DIR, "services", "theme_service.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def get_default_theme", content)

    def test_has_get_theme_variables(self):
        path = os.path.join(APP_DIR, "services", "theme_service.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def get_theme_variables", content)


class TestScheduler(unittest.TestCase):
    """Verify scheduler module."""

    def test_exists(self):
        path = os.path.join(APP_DIR, "services", "scheduler.py")
        self.assertTrue(os.path.exists(path))

    def test_has_daily_tasks(self):
        path = os.path.join(APP_DIR, "services", "scheduler.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def daily_tasks", content)


if __name__ == "__main__":
    unittest.main()
