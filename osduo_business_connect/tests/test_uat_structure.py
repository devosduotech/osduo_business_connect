# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
UAT Test Structure Verification.

Checks that UAT test file exists (old integration tests, require live site).
"""

import os
import unittest

APP_DIR = os.path.join(os.path.dirname(__file__), "..")


class TestUATStructure(unittest.TestCase):
    """Structural tests for UAT test cases."""

    def test_uat_test_file_exists(self):
        """Test that UAT test file exists (may be renamed)."""
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        # Check both old and new names
        old_path = os.path.join(tests_dir, "test_uat.py")
        new_path = os.path.join(tests_dir, "_test_uat_old.py")
        exists = os.path.exists(old_path) or os.path.exists(new_path)
        self.assertTrue(exists, "UAT test file not found (test_uat.py or _test_uat_old.py)")

    def test_uat_has_test_functions(self):
        """Test that UAT test file has test functions."""
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        old_path = os.path.join(tests_dir, "test_uat.py")
        new_path = os.path.join(tests_dir, "_test_uat_old.py")
        uat_path = old_path if os.path.exists(old_path) else new_path

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
