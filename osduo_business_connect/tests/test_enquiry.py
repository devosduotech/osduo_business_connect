import os
import sys
import json
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

APP_DIR = os.path.join(os.path.dirname(__file__), "..")
ENQUIRY_DIR = os.path.join(APP_DIR, "enquiry")


def load_json(path):
    with open(path) as f:
        return json.load(f)


class TestEnquiryDocType(unittest.TestCase):
    """Verify Enquiry DocType JSON structure."""

    def setUp(self):
        self.json_path = os.path.join(ENQUIRY_DIR, "doctype", "enquiry", "enquiry.json")
        self.data = load_json(self.json_path)

    def test_json_exists(self):
        self.assertTrue(os.path.exists(self.json_path))

    def test_required_fields(self):
        fieldnames = [f["fieldname"] for f in self.data["fields"]]
        for req in ["business", "source", "visitor_name", "status", "submitted_at"]:
            self.assertIn(req, fieldnames)

    def test_source_options(self):
        source_field = next(f for f in self.data["fields"] if f["fieldname"] == "source")
        options = source_field["options"]
        for src in ["Digital Card", "Business Profile", "QR"]:
            self.assertIn(src, options)

    def test_status_options(self):
        status_field = next(f for f in self.data["fields"] if f["fieldname"] == "status")
        options = status_field["options"]
        for st in ["New", "Contacted", "Nurture", "Qualified", "Converted", "Unqualified", "Junk"]:
            self.assertIn(st, options)

    def test_has_permissions(self):
        roles = [p["role"] for p in self.data["permissions"]]
        self.assertTrue(len(roles) > 0)

    def test_controller_has_re_exports(self):
        path = os.path.join(ENQUIRY_DIR, "doctype", "enquiry", "enquiry.py")
        with open(path) as f:
            content = f.read()
        # Controller is a re-export stub from core.py
        self.assertIn("from", content, "Controller should import from core.py")
        self.assertIn("Enquiry", content)


class TestEnquiryResponse(unittest.TestCase):
    """Verify Enquiry Response child table."""

    def setUp(self):
        self.json_path = os.path.join(ENQUIRY_DIR, "doctype", "enquiry_response", "enquiry_response.json")
        self.data = load_json(self.json_path)

    def test_json_exists(self):
        self.assertTrue(os.path.exists(self.json_path))

    def test_required_fields(self):
        fieldnames = [f["fieldname"] for f in self.data["fields"]]
        for req in ["responder", "response_type", "response_message"]:
            self.assertIn(req, fieldnames)


class TestEnquiryService(unittest.TestCase):
    """Verify enquiry service module."""

    def test_exists(self):
        path = os.path.join(ENQUIRY_DIR, "enquiry_service.py")
        self.assertTrue(os.path.exists(path))

    def test_has_create_enquiry(self):
        path = os.path.join(ENQUIRY_DIR, "enquiry_service.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def create_enquiry", content)

    def test_has_stats(self):
        path = os.path.join(ENQUIRY_DIR, "enquiry_service.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def get_enquiry_stats", content)


class TestEnquiryCore(unittest.TestCase):
    """Verify enquiry core module."""

    def test_core_exists(self):
        path = os.path.join(ENQUIRY_DIR, "core.py")
        self.assertTrue(os.path.exists(path))

    def test_core_has_class(self):
        path = os.path.join(ENQUIRY_DIR, "core.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("class Enquiry", content)


if __name__ == "__main__":
    unittest.main()
