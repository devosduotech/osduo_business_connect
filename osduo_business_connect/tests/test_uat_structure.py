# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
UAT Test Cases for OSDuo Business Connect.

This module contains test cases for User Acceptance Testing.
These tests require a running Frappe site with CRM installed.
"""

import os
import sys
import unittest

# Add parent directory to path for local testing
app_parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, app_parent_dir)


class TestUATStructure(unittest.TestCase):
    """Structural tests for UAT test cases."""

    def test_uat_test_file_exists(self):
        """Test that UAT test file exists."""
        uat_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "test_uat.py",
        )
        self.assertTrue(os.path.exists(uat_path), "UAT test file not found")

    def test_uat_has_test_functions(self):
        """Test that UAT test file has test functions."""
        uat_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "test_uat.py",
        )
        with open(uat_path, "r") as f:
            content = f.read()
        
        # Check for key test functions
        test_functions = [
            "test_business_creation",
            "test_business_member_creation",
            "test_digital_card_creation",
            "test_enquiry_submission",
            "test_crm_sync",
            "test_cross_business_isolation",
        ]
        
        for func in test_functions:
            self.assertIn(f"def {func}", content, f"Test function {func} not found")


if __name__ == "__main__":
    unittest.main()
