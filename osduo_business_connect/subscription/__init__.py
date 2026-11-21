# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Subscription and plan-entitlement module for OSDuo Business Connect.

One Subscription Single document exists per Frappe site. It mirrors the plan
and seat state agreed externally (currently at Aasriva) and freezes the
entitlements that the plan gates must enforce. No payment, invoice or checkout
logic lives in this module.
"""
