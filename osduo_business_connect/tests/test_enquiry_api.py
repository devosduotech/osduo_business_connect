import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

APP_DIR = os.path.join(os.path.dirname(__file__), "..")
ENQUIRY_DIR = os.path.join(APP_DIR, "enquiry")


class TestPublicEnquiryAPI(unittest.TestCase):
    """Verify the live guest enquiry API module (enquiry/, not crm_integration/)."""

    def test_exists(self):
        path = os.path.join(ENQUIRY_DIR, "public_enquiry_api.py")
        self.assertTrue(os.path.exists(path))

    def test_has_submit_enquiry(self):
        path = os.path.join(ENQUIRY_DIR, "public_enquiry_api.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def submit_enquiry", content)
        self.assertIn("@frappe.whitelist(allow_guest=True)", content)

    def test_dead_helpers_are_not_shipped(self):
        """The retired form-config/validation helpers must not be reintroduced."""
        path = os.path.join(ENQUIRY_DIR, "public_enquiry_api.py")
        with open(path) as f:
            content = f.read()
        self.assertNotIn("def get_enquiry_form_config", content)
        self.assertNotIn("def validate_enquiry_data", content)

    def test_dead_modules_are_not_shipped(self):
        """Unwired page/webhook duplicates of the guest API were removed."""
        for name in ("enquiry_webhook.py", "submit_enquiry_page.py"):
            self.assertFalse(os.path.exists(os.path.join(ENQUIRY_DIR, name)))


if __name__ == "__main__":
    unittest.main()
