# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Per-site PWA web app manifest — served at /manifest.json.

Uses the same raw-template mechanism as Frappe's own www/website_script
(controller + base template with a non-HTML extension). The response
content type is derived from the request path (application/json).
"""

from osduo_business_connect.pwa import get_manifest_context

no_cache = 1
base_template_path = "www/manifest.json"


def get_context(context):
    context.update(get_manifest_context())
    return context
