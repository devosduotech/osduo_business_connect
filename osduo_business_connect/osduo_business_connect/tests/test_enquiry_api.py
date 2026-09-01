"""
Unit tests for Enquiry Public API.

These tests verify:
- Public enquiry API functionality
- Webhook handling
- Validation functions
"""

import os
import sys
import unittest

# Add parent directory to path for local testing
app_parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, app_parent_dir)


class TestPublicEnquiryAPI(unittest.TestCase):
    """Tests for Public Enquiry API."""

    def test_public_enquiry_api_exists(self):
        """Test that public enquiry API file exists."""
        api_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "public_enquiry_api.py",
        )
        self.assertTrue(os.path.exists(api_path), "Public enquiry API not found")

    def test_public_enquiry_api_has_submit_enquiry(self):
        """Test that public enquiry API has submit_enquiry function."""
        api_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "public_enquiry_api.py",
        )
        with open(api_path, "r") as f:
            content = f.read()
        self.assertIn("def submit_enquiry", content, "submit_enquiry function not found")

    def test_public_enquiry_api_has_form_config(self):
        """Test that public enquiry API has get_enquiry_form_config function."""
        api_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "public_enquiry_api.py",
        )
        with open(api_path, "r") as f:
            content = f.read()
        self.assertIn(
            "def get_enquiry_form_config", content, "get_enquiry_form_config function not found"
        )

    def test_public_enquiry_api_has_validate_data(self):
        """Test that public enquiry API has validate_enquiry_data function."""
        api_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "public_enquiry_api.py",
        )
        with open(api_path, "r") as f:
            content = f.read()
        self.assertIn(
            "def validate_enquiry_data", content, "validate_enquiry_data function not found"
        )


class TestEnquiryWebhook(unittest.TestCase):
    """Tests for Enquiry Webhook."""

    def test_enquiry_webhook_exists(self):
        """Test that Enquiry webhook file exists."""
        webhook_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "enquiry_webhook.py",
        )
        self.assertTrue(os.path.exists(webhook_path), "Enquiry webhook not found")

    def test_enquiry_webhook_has_handle_function(self):
        """Test that Enquiry webhook has handle_enquiry_webhook function."""
        webhook_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "enquiry_webhook.py",
        )
        with open(webhook_path, "r") as f:
            content = f.read()
        self.assertIn(
            "def handle_enquiry_webhook", content, "handle_enquiry_webhook function not found"
        )

    def test_enquiry_webhook_has_rate_limit(self):
        """Test that Enquiry webhook has rate_limit_check function."""
        webhook_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "enquiry_webhook.py",
        )
        with open(webhook_path, "r") as f:
            content = f.read()
        self.assertIn("def rate_limit_check", content, "rate_limit_check function not found")

    def test_enquiry_webhook_has_spam_check(self):
        """Test that Enquiry webhook has spam_check function."""
        webhook_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "enquiry",
            "enquiry",
            "enquiry_webhook.py",
        )
        with open(webhook_path, "r") as f:
            content = f.read()
        self.assertIn("def spam_check", content, "spam_check function not found")


if __name__ == "__main__":
    unittest.main()
