# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Service worker — served at /sw.js (root scope).

Raw-template mechanism like Frappe's www/website_script; content type is
taken from the request path (text/javascript). The cache key combines the app
version with SW_CACHE_REVISION so asset-only changes (CSS/JS) can invalidate
old caches without bumping the public app version.
"""

import osduo_business_connect

no_cache = 1
base_template_path = "www/sw.js"

cache_headers = {"Cache-Control": "no-cache"}

# Bump this whenever bundled CSS/JS changes but the app version stays fixed.
# The worker's activate handler deletes every older bc-* cache, so existing
# clients pick up the new assets on their next navigation.
SW_CACHE_REVISION = "2026-11-24-touch-hover"


def get_context(context):
    context.cache_version = (
        f"{osduo_business_connect.__version__}-{SW_CACHE_REVISION}"
    )
    return context
