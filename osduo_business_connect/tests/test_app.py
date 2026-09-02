import os
import sys
import unittest

# NOTE: Tests check file structure only — no frappe import needed.
# The app __init__.py imports frappe (monkey-patch), so we avoid importing it.

APP_DIR = os.path.join(os.path.dirname(__file__), "..")


class TestAppStructure(unittest.TestCase):
    """Verify core app files exist and have correct content."""

    def _read(self, relative_path):
        path = os.path.join(APP_DIR, relative_path)
        with open(path) as f:
            return f.read()

    def test_init_file_exists(self):
        path = os.path.join(APP_DIR, "__init__.py")
        self.assertTrue(os.path.exists(path))

    def test_app_version_in_init(self):
        content = self._read("__init__.py")
        self.assertIn("__version__", content)
        self.assertIn("1.0.1", content)

    def test_app_name_in_init(self):
        content = self._read("__init__.py")
        self.assertIn('app_name', content)
        self.assertIn("osduo_business_connect", content)

    def test_hooks_file_exists(self):
        path = os.path.join(APP_DIR, "hooks.py")
        self.assertTrue(os.path.exists(path))

    def test_hooks_has_app_name(self):
        content = self._read("hooks.py")
        self.assertIn('app_name = "osduo_business_connect"', content)

    def test_hooks_has_app_title(self):
        content = self._read("hooks.py")
        self.assertIn("Business Connect", content)

    def test_hooks_requires_crm(self):
        content = self._read("hooks.py")
        self.assertIn('"crm"', content)

    def test_modules_txt_exists(self):
        path = os.path.join(APP_DIR, "modules.txt")
        self.assertTrue(os.path.exists(path))

    def test_modules_txt_content(self):
        content = self._read("modules.txt")
        for module in ["Business", "Card", "Showcase", "Analytics", "CRM Integration", "Enquiry"]:
            self.assertIn(module, content)

    def test_pyproject_toml_exists(self):
        parent = os.path.join(APP_DIR, "..")
        path = os.path.join(parent, "pyproject.toml")
        self.assertTrue(os.path.exists(path), f"pyproject.toml not found at {path}")

    def test_required_submodules_exist(self):
        submodules = ["business", "card", "showcase", "analytics", "crm_integration", "services", "utils"]
        for mod in submodules:
            path = os.path.join(APP_DIR, mod)
            self.assertTrue(os.path.isdir(path), f"Module directory missing: {mod}")

    def test_services_modules_exist(self):
        for mod in ["theme_service", "qr_service", "vcard_service", "scheduler"]:
            path = os.path.join(APP_DIR, "services", f"{mod}.py")
            self.assertTrue(os.path.exists(path), f"Missing: services/{mod}.py")


if __name__ == "__main__":
    unittest.main()
