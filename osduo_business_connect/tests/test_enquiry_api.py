import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

APP_DIR = os.path.join(os.path.dirname(__file__), "..")
ENQUIRY_DIR = os.path.join(APP_DIR, "enquiry")


class TestPublicEnquiryAPI(unittest.TestCase):
    """Verify public enquiry API module (located in enquiry/ not crm_integration/)."""

    def test_exists(self):
        path = os.path.join(ENQUIRY_DIR, "public_enquiry_api.py")
        self.assertTrue(os.path.exists(path))

    def test_has_submit_enquiry(self):
        path = os.path.join(ENQUIRY_DIR, "public_enquiry_api.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def submit_enquiry", content)

    def test_has_form_config(self):
        path = os.path.join(ENQUIRY_DIR, "public_enquiry_api.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def get_enquiry_form_config", content)

    def test_has_validate_data(self):
        path = os.path.join(ENQUIRY_DIR, "public_enquiry_api.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def validate_enquiry_data", content)


class TestEnquiryWebhook(unittest.TestCase):
    """Verify enquiry webhook module (located in enquiry/ not crm_integration/)."""

    def test_exists(self):
        path = os.path.join(ENQUIRY_DIR, "enquiry_webhook.py")
        self.assertTrue(os.path.exists(path))

    def test_has_handle_function(self):
        path = os.path.join(ENQUIRY_DIR, "enquiry_webhook.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def handle_enquiry_webhook", content)

    def test_has_rate_limit(self):
        path = os.path.join(ENQUIRY_DIR, "enquiry_webhook.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def rate_limit_check", content)

    def test_has_spam_check(self):
        path = os.path.join(ENQUIRY_DIR, "enquiry_webhook.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def spam_check", content)


if __name__ == "__main__":
    unittest.main()
