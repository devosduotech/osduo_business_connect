# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Sitemap index — served at ``/sitemap.xml``.

Points at the four per-type sitemaps. Uses the raw-template mechanism
(controller + ``.xml`` template) like Frappe's own ``www/sitemap``; the
response content type is taken from the request path (``text/xml``).

``no_cache`` disables Frappe's 30-minute HTML page cache — the generator
manages its own Redis cache and invalidates it on publication changes.
"""

from osduo_business_connect.seo.sitemap import get_cached_entries

no_cache = 1
base_template_path = "www/sitemap.xml"


def get_context(context):
    context.links = get_cached_entries("index")
    return context
