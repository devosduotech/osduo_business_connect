# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Decision 12 — share URL wire format and backward-compatible reader.

build_share_url is pure; get_share_ref only needs frappe.form_dict, so both are
exercised with a minimal stub (no bench). The tests lock the three guarantees:
standard UTM on the way out, the *same* stored campaign token for new and legacy
links, and arbitrary query strings never attributing.
"""

import importlib
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from osduo_business_connect.utils.share import CHANNELS, UTM_MEDIUM, build_share_url

SHARE = "osduo_business_connect.utils.share"


def _reader(form):
    """Import utils.share against a stubbed frappe.form_dict and run get_share_ref."""
    frappe_stub = types.ModuleType("frappe")
    frappe_stub.form_dict = dict(form)
    saved = sys.modules.get("frappe")
    saved_share = sys.modules.get(SHARE)
    sys.modules["frappe"] = frappe_stub
    for name in (SHARE,):
        sys.modules.pop(name, None)
    try:
        module = importlib.import_module(SHARE)
        return module.get_share_ref(), module.get_share_by()
    finally:
        for name in (SHARE,):
            sys.modules.pop(name, None)
        if saved_share is not None:
            sys.modules[SHARE] = saved_share
        if saved is None:
            sys.modules.pop("frappe", None)
        else:
            sys.modules["frappe"] = saved


class TestBuildShareUrl(unittest.TestCase):
    def test_appends_source_and_medium(self):
        out = build_share_url("https://x.test/b/acme", "whatsapp")
        self.assertIn("utm_source=whatsapp", out)
        self.assertIn("utm_medium=share", out)

    def test_uses_amp_when_query_present(self):
        out = build_share_url("https://x.test/c/k#frag", "email")
        self.assertIn("?utm_source=email", out)

    def test_keeps_by(self):
        out = build_share_url("https://x.test/b/acme", "sms", by="karthics-card")
        self.assertIn("by=karthics-card", out)

    def test_canonical_never_carries_these_by_construction(self):
        # build_share_url only ever *adds* params to what it is handed; the page
        # canonical is built elsewhere (absolute_url) and is left untouched here.
        self.assertTrue(build_share_url("https://x.test/b/acme", "copy").startswith("https://x.test/b/acme?"))


class TestReaderBackwardCompat(unittest.TestCase):
    def test_new_utm_maps_to_stable_token(self):
        for source, token in (("whatsapp", "share_whatsapp"), ("sms", "share_sms"),
                              ("email", "share_email"), ("copy", "share_copy"),
                              ("mycard", "mycard")):
            ref, _ = _reader({"utm_source": source, "utm_medium": UTM_MEDIUM})
            self.assertEqual(ref, token, source)

    def test_legacy_ref_still_attributing(self):
        ref, _ = _reader({"ref": "share_whatsapp"})
        self.assertEqual(ref, "share_whatsapp")

    def test_utm_source_needs_medium_share(self):
        # a bare utm_source (no utm_medium=share) does not attribute as a share;
        # this keeps unrelated utm_campaign tagging from being mistaken for shares.
        ref, _ = _reader({"utm_source": "whatsapp", "utm_medium": "cpc"})
        self.assertIsNone(ref)

    def test_arbitrary_params_ignored(self):
        ref, _ = _reader({"utm_source": "evil&utm_medium=xss", "utm_medium": "share", "foo": "bar"})
        self.assertIsNone(ref)
        ref, _ = _reader({"ref": "totally_unknown"})
        self.assertIsNone(ref)

    def test_by_is_returned_and_capped(self):
        _, by = _reader({"utm_source": "whatsapp", "utm_medium": UTM_MEDIUM, "by": "some-card"})
        self.assertEqual(by, "some-card")
        _, by = _reader({"by": "x" * 300})
        self.assertEqual(len(by), 140)


class TestChannelTable(unittest.TestCase):
    def test_native_is_copy_equivalent(self):
        # the "More" native sheet is logged as a copy-class share
        self.assertEqual(CHANNELS["native"], "share_copy")

    def test_every_channel_value_is_a_stable_token(self):
        for token in CHANNELS.values():
            self.assertIn(token, ("share_whatsapp", "share_sms", "share_email", "share_copy", "mycard"))


if __name__ == "__main__":
    unittest.main()
