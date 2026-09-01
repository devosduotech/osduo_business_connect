import os
import sys
import unittest

# Add parent directory to path for local testing
# The app structure is: osduo_business_connect/osduo_business_connect/
# So we need to go up two levels to import the app
app_parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, app_parent_dir)


class TestOSDuoBusinessConnect(unittest.TestCase):
    """Basic tests for OSDuo Business Connect app structure."""

    def test_app_version(self):
        """Test that app version is defined."""
        from osduo_business_connect import __version__

        self.assertEqual(__version__, "1.0.1")

    def test_app_name(self):
        """Test that app name is correctly set."""
        import osduo_business_connect

        self.assertEqual(osduo_business_connect.app_name, "osduo_business_connect")

    def test_modules_exist(self):
        """Test that all required modules exist."""
        import osduo_business_connect.business
        import osduo_business_connect.card
        import osduo_business_connect.showcase
        import osduo_business_connect.analytics
        import osduo_business_connect.crm_integration
        import osduo_business_connect.services
        import osduo_business_connect.utils

        self.assertTrue(osduo_business_connect.business)
        self.assertTrue(osduo_business_connect.card)
        self.assertTrue(osduo_business_connect.showcase)
        self.assertTrue(osduo_business_connect.analytics)
        self.assertTrue(osduo_business_connect.crm_integration)
        self.assertTrue(osduo_business_connect.services)
        self.assertTrue(osduo_business_connect.utils)

    def test_hooks_has_app_name(self):
        """Test that hooks.py has app_name defined."""
        hooks_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "hooks.py",
        )
        with open(hooks_path, "r") as f:
            content = f.read()
        self.assertIn('app_name = "osduo_business_connect"', content)
        self.assertIn('app_title = "OSDuo Business Connect"', content)

    def test_modules_txt_exists(self):
        """Test that modules.txt exists and has correct content."""
        modules_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "modules.txt",
        )
        with open(modules_path, "r") as f:
            content = f.read()
        self.assertIn("Business", content)
        self.assertIn("Card", content)
        self.assertIn("Showcase", content)
        self.assertIn("Analytics", content)
        self.assertIn("CRM Integration", content)

    def test_pyproject_toml_exists(self):
        """Test that pyproject.toml exists and has correct content."""
        pyproject_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "pyproject.toml",
        )
        with open(pyproject_path, "r") as f:
            content = f.read()
        self.assertIn('name = "osduo_business_connect"', content)
        self.assertIn("frappe = ", content)

    def test_no_erpnext_in_app_code(self):
        """Test that no ERPNext references exist in app code (excluding tests)."""
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for root, dirs, files in os.walk(app_dir):
            # Skip tests directory
            if "tests" in root:
                continue
            for file in files:
                if file.endswith(".py") or file.endswith(".toml"):
                    filepath = os.path.join(root, file)
                    with open(filepath, "r") as f:
                        content = f.read().lower()
                    self.assertNotIn(
                        "erpnext",
                        content,
                        f"ERPNext reference found in {filepath}",
                    )


if __name__ == "__main__":
    unittest.main()
