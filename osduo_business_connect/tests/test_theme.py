import importlib
import json
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

APP_DIR = os.path.join(os.path.dirname(__file__), "..")
SHOWCASE_DIR = os.path.join(APP_DIR, "showcase")


def load_json(path):
    with open(path) as f:
        return json.load(f)


def read(*parts):
    with open(os.path.join(APP_DIR, *parts)) as f:
        return f.read()


def load_theme_service():
    """Import theme_service with a minimal frappe stub for the pure helpers."""
    if "frappe" not in sys.modules:
        try:
            import frappe
        except Exception:
            sys.modules["frappe"] = types.ModuleType("frappe")
    # Another test may already have installed a bare stub without the translator.
    frappe = sys.modules["frappe"]
    if not hasattr(frappe, "_"):
        frappe._ = lambda value: value
    return importlib.import_module("osduo_business_connect.services.theme_service")


class TestThemeDocType(unittest.TestCase):
    """Verify BC Theme DocType JSON structure."""

    def setUp(self):
        self.json_path = os.path.join(SHOWCASE_DIR, "doctype", "bc_theme", "bc_theme.json")
        self.data = load_json(self.json_path)

    def test_json_exists(self):
        self.assertTrue(os.path.exists(self.json_path))

    def test_required_fields(self):
        fieldnames = [f["fieldname"] for f in self.data["fields"]]
        for req in ["theme_name", "template", "color_scheme", "primary_color", "secondary_color", "button_style", "layout_mode", "dark_mode"]:
            self.assertIn(req, fieldnames)

    def test_template_options(self):
        template_field = next(f for f in self.data["fields"] if f["fieldname"] == "template")
        options = template_field["options"]
        for tmpl in ["Modern", "Professional", "Minimal", "Classic", "Luxury", "Creative"]:
            self.assertIn(tmpl, options)

    def test_color_scheme_options(self):
        color_field = next(f for f in self.data["fields"] if f["fieldname"] == "color_scheme")
        options = color_field["options"]
        for scheme in ["Violet", "Indigo", "Blue", "Green", "Yellow", "Orange", "Red", "Gold", "Custom"]:
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

    def test_has_layout_map(self):
        path = os.path.join(APP_DIR, "services", "theme_service.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("LAYOUT_MAP", content)

    def test_has_dark_mode_map(self):
        path = os.path.join(APP_DIR, "services", "theme_service.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("DARK_MODE_MAP", content)


class TestThemeFontSize(unittest.TestCase):
    """Font-size presets must reach the root element, not just .bc-page."""

    @classmethod
    def setUpClass(cls):
        cls.service = load_theme_service()

    def test_presets_map_to_px(self):
        self.assertEqual(self.service.get_root_font_size({"font_size": "Small"}), "14px")
        self.assertEqual(self.service.get_root_font_size({"font_size": "Default"}), "16px")
        self.assertEqual(self.service.get_root_font_size({"font_size": "Large"}), "18px")

    def test_unknown_and_missing_presets_fall_back_to_default(self):
        self.assertEqual(self.service.get_root_font_size({"font_size": "Huge"}), "16px")
        self.assertEqual(self.service.get_root_font_size({}), "16px")

    def test_theme_variables_use_the_same_mapping(self):
        variables = self.service.get_theme_variables({"font_size": "Large"})
        self.assertIn("--bc-font-size: 18px;", variables)


class TestThemeFontSizeWiring(unittest.TestCase):
    """Every themed public page publishes the preset; the base template uses it."""

    PAGES = (
        ("templates", "pages", "business", "business.py"),
        ("templates", "pages", "product", "product.py"),
        ("templates", "pages", "service", "service.py"),
        ("templates", "pages", "card", "card.py"),
        ("templates", "pages", "card", "team_member.py"),
    )

    def test_all_themed_pages_publish_root_font_size(self):
        for path in self.PAGES:
            source = read(*path)
            self.assertIn("get_root_font_size", source, "/".join(path))
            self.assertIn(
                "context.theme_root_font_size = get_root_font_size(theme_data)",
                source,
                "/".join(path),
            )

    def test_base_template_applies_preset_to_html_root(self):
        base = read("templates", "bc_base.html")
        self.assertIn("theme_root_font_size", base)
        self.assertIn("html { font-size: {{ _root_font_size | e }}; }", base)
        self.assertIn("or '16px'", base)

    def test_base_css_still_exposes_the_wrapper_variable(self):
        css = read("public", "css", "business_connect.css")
        self.assertIn("--bc-font-size: 16px;", css)
        self.assertIn("font-size: var(--bc-font-size);", css)


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
