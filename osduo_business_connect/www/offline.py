# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Offline fallback page — served at /offline.

Rendered into the page by the service worker when a public page is requested
while the device has no network and no cached copy is available.
"""

from osduo_business_connect.hooks import OSDUO_BRANDING

no_cache = 1


def get_context(context):
    context.title = OSDUO_BRANDING["app_short_name"]
    context.theme_color = OSDUO_BRANDING["primary_color"]
    context.background_color = OSDUO_BRANDING["background_color"]
    context.heading = "You're offline"
    context.message = (
        "This page isn't cached on your device yet. "
        "Reconnect to the internet and try again."
    )
    context.retry_label = "Try again"
    return context
