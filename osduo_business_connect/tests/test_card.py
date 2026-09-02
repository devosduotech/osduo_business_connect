import os
import sys
import json
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

APP_DIR = os.path.join(os.path.dirname(__file__), "..")
CARD_DIR = os.path.join(APP_DIR, "card")


def load_json(path):
    with open(path) as f:
        return json.load(f)


class TestDigitalCardDocType(unittest.TestCase):
    """Verify Digital Card DocType JSON structure."""

    def setUp(self):
        self.json_path = os.path.join(CARD_DIR, "doctype", "digital_card", "digital_card.json")
        self.data = load_json(self.json_path)

    def test_json_exists(self):
        self.assertTrue(os.path.exists(self.json_path))

    def test_required_fields(self):
        fieldnames = [f["fieldname"] for f in self.data["fields"]]
        for req in ["business", "member", "display_name", "slug", "status"]:
            self.assertIn(req, fieldnames)

    def test_has_permissions(self):
        roles = [p["role"] for p in self.data["permissions"]]
        self.assertTrue(len(roles) > 0)

    def test_controller_exists(self):
        path = os.path.join(CARD_DIR, "doctype", "digital_card", "digital_card.py")
        self.assertTrue(os.path.exists(path))


class TestDigitalCardLink(unittest.TestCase):
    """Verify Digital Card Link child table."""

    def setUp(self):
        self.json_path = os.path.join(CARD_DIR, "doctype", "digital_card_link", "digital_card_link.json")
        self.data = load_json(self.json_path)

    def test_json_exists(self):
        self.assertTrue(os.path.exists(self.json_path))

    def test_required_fields(self):
        fieldnames = [f["fieldname"] for f in self.data["fields"]]
        for req in ["link_type", "value"]:
            self.assertIn(req, fieldnames)


class TestQRService(unittest.TestCase):
    """Verify QR service module."""

    def test_exists(self):
        path = os.path.join(APP_DIR, "services", "qr_service.py")
        self.assertTrue(os.path.exists(path))

    def test_has_generate_function(self):
        path = os.path.join(APP_DIR, "services", "qr_service.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def generate_qr_code", content)


class TestVCardService(unittest.TestCase):
    """Verify vCard service module."""

    def test_exists(self):
        path = os.path.join(APP_DIR, "services", "vcard_service.py")
        self.assertTrue(os.path.exists(path))

    def test_has_generate_function(self):
        path = os.path.join(APP_DIR, "services", "vcard_service.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def generate_vcard", content)


class TestPublicAPI(unittest.TestCase):
    """Verify card public API module."""

    def test_exists(self):
        path = os.path.join(CARD_DIR, "public_api.py")
        self.assertTrue(os.path.exists(path))

    def test_has_get_public_card(self):
        path = os.path.join(CARD_DIR, "public_api.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def get_public_card", content)

    def test_has_serialize_function(self):
        path = os.path.join(CARD_DIR, "public_api.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def serialize_card", content)


class TestPublicRoute(unittest.TestCase):
    """Verify card public route module."""

    def test_exists(self):
        path = os.path.join(CARD_DIR, "public_route.py")
        self.assertTrue(os.path.exists(path))

    def test_has_get_context(self):
        path = os.path.join(CARD_DIR, "public_route.py")
        with open(path) as f:
            content = f.read()
        self.assertIn("def get_context", content)


if __name__ == "__main__":
    unittest.main()
