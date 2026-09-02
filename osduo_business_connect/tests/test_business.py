import os
import sys
import json
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

APP_DIR = os.path.join(os.path.dirname(__file__), "..")
BUSINESS_DIR = os.path.join(APP_DIR, "business")


def load_json(path):
    with open(path) as f:
        return json.load(f)


class TestBusinessDocType(unittest.TestCase):
    """Verify Business DocType JSON structure and controller."""

    def setUp(self):
        self.json_path = os.path.join(BUSINESS_DIR, "doctype", "business", "business.json")
        self.data = load_json(self.json_path)

    def test_json_exists(self):
        self.assertTrue(os.path.exists(self.json_path))

    def test_required_fields(self):
        fieldnames = [f["fieldname"] for f in self.data["fields"]]
        for req in ["business_name", "slug", "status", "owner_user"]:
            self.assertIn(req, fieldnames, f"Missing required field: {req}")

    def test_has_permissions(self):
        roles = [p["role"] for p in self.data["permissions"]]
        self.assertTrue(len(roles) > 0, "No permissions defined")

    def test_controller_exists(self):
        path = os.path.join(BUSINESS_DIR, "doctype", "business", "business.py")
        self.assertTrue(os.path.exists(path))

    def test_controller_has_re_exports(self):
        path = os.path.join(BUSINESS_DIR, "doctype", "business", "business.py")
        with open(path) as f:
            content = f.read()
        # Controller is a re-export stub from core.py
        self.assertIn("from", content, "Controller should import from core.py")
        self.assertIn("Business", content)


class TestBusinessSocialLink(unittest.TestCase):
    """Verify Business Social Link child table."""

    def setUp(self):
        self.json_path = os.path.join(BUSINESS_DIR, "doctype", "business_social_link", "business_social_link.json")
        self.data = load_json(self.json_path)

    def test_json_exists(self):
        self.assertTrue(os.path.exists(self.json_path))

    def test_required_fields(self):
        fieldnames = [f["fieldname"] for f in self.data["fields"]]
        for req in ["platform", "url"]:
            self.assertIn(req, fieldnames)


class TestBusinessHour(unittest.TestCase):
    """Verify Business Hour child table."""

    def setUp(self):
        self.json_path = os.path.join(BUSINESS_DIR, "doctype", "business_hour", "business_hour.json")
        self.data = load_json(self.json_path)

    def test_json_exists(self):
        self.assertTrue(os.path.exists(self.json_path))

    def test_required_fields(self):
        fieldnames = [f["fieldname"] for f in self.data["fields"]]
        for req in ["day", "enabled"]:
            self.assertIn(req, fieldnames)


class TestBusinessMember(unittest.TestCase):
    """Verify Business Member DocType."""

    def setUp(self):
        self.json_path = os.path.join(BUSINESS_DIR, "doctype", "business_member", "business_member.json")
        self.data = load_json(self.json_path)

    def test_json_exists(self):
        self.assertTrue(os.path.exists(self.json_path))

    def test_required_fields(self):
        fieldnames = [f["fieldname"] for f in self.data["fields"]]
        for req in ["business", "user", "person_name", "role", "status"]:
            self.assertIn(req, fieldnames)

    def test_role_options(self):
        role_field = next(f for f in self.data["fields"] if f["fieldname"] == "role")
        options = role_field["options"]
        for role in ["Owner", "Manager", "Marketing"]:
            self.assertIn(role, options)

    def test_controller_exists(self):
        path = os.path.join(BUSINESS_DIR, "doctype", "business_member", "business_member.py")
        self.assertTrue(os.path.exists(path))


class TestBusinessCore(unittest.TestCase):
    """Verify business core module."""

    def test_core_exists(self):
        path = os.path.join(BUSINESS_DIR, "core.py")
        self.assertTrue(os.path.exists(path))

    def test_core_has_class(self):
        path = os.path.join(BUSINESS_DIR, "core.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("class Business", content)


class TestCRMIntegration(unittest.TestCase):
    """Verify CRM integration module."""

    def test_lead_mapper_exists(self):
        path = os.path.join(APP_DIR, "crm_integration", "lead_mapper.py")
        self.assertTrue(os.path.exists(path))

    def test_lead_mapper_has_create_function(self):
        path = os.path.join(APP_DIR, "crm_integration", "lead_mapper.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def create_lead_from_enquiry", content)

    def test_crm_permissions_exists(self):
        path = os.path.join(APP_DIR, "crm_integration", "crm_permissions.py")
        self.assertTrue(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()
