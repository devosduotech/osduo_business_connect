import os
import sys
import unittest
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from osduo_business_connect.utils.publish import publish_on_submit


class TestPublishOnSubmit(unittest.TestCase):
    def test_draft_is_published_on_submit(self):
        doc = SimpleNamespace(_action="submit", status="Draft")
        self.assertEqual(publish_on_submit(doc), "Published")
        self.assertEqual(doc.status, "Published")

    def test_draft_is_not_published_on_plain_save(self):
        doc = SimpleNamespace(_action="save", status="Draft")
        self.assertEqual(publish_on_submit(doc), "Draft")

    def test_explicit_non_draft_status_is_preserved(self):
        for status in ("Published", "Suspended", "Archived", "Unpublished"):
            doc = SimpleNamespace(_action="submit", status=status)
            self.assertEqual(publish_on_submit(doc), status)

    def test_missing_action_is_safe(self):
        doc = SimpleNamespace(status="Draft")
        self.assertEqual(publish_on_submit(doc), "Draft")

    def test_custom_statuses_are_supported(self):
        doc = SimpleNamespace(_action="submit", status="New")
        self.assertEqual(
            publish_on_submit(doc, draft_status="New", published_status="Live"),
            "Live",
        )

    def test_public_doctypes_call_the_helper(self):
        app_dir = os.path.join(os.path.dirname(__file__), "..")
        controllers = (
            ("business", "core.py"),
            ("card", "doctype", "digital_card", "digital_card.py"),
            ("showcase", "doctype", "showcase_product", "showcase_product.py"),
            ("showcase", "doctype", "showcase_service", "showcase_service.py"),
        )
        for parts in controllers:
            with open(os.path.join(app_dir, *parts)) as f:
                self.assertIn("publish_on_submit(self)", f.read(), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
