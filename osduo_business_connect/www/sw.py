# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Service worker — served at /sw.js (root scope).

Raw-template mechanism like Frappe's www/website_script; content type is
taken from the request path (text/javascript). The cache version is stamped
with the app version so a bench deploy automatically invalidates old caches.
"""

import osduo_business_connect

no_cache = 1
base_template_path = "www/sw.js"

cache_headers = {"Cache-Control": "no-cache"}


def get_context(context):
    context.cache_version = osduo_business_connect.__version__
    return context
