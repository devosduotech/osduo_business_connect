# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Published public digital cards — served at ``/sitemap-cards.xml``."""

from osduo_business_connect.seo.sitemap import get_cached_entries

no_cache = 1
base_template_path = "www/sitemap-cards.xml"


def get_context(context):
    context.urls = get_cached_entries("cards")
    return context
