# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Published business profiles — served at ``/sitemap-businesses.xml``."""

from osduo_business_connect.seo.sitemap import get_render_entries

no_cache = 1
base_template_path = "www/sitemap-businesses.xml"


def get_context(context):
    context.urls = get_render_entries("businesses")
    return context
