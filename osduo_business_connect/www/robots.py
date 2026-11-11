# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""``/robots.txt`` — overrides Frappe core's static robots file.

Core serves ``Website Settings.robots_txt`` verbatim, which bakes in a fixed
``Sitemap:`` URL. This controller rebuilds the text on every request so the
sitemap line always matches the host the crawler reached (``seo/robots.py``).

``no_cache`` stops Frappe's page cache from holding one host's robots under
another host's request on a shared bench.
"""

from osduo_business_connect.seo.robots import build_robots_txt

no_cache = 1
base_template_path = "www/robots.txt"


def get_context(context):
    context.robots_txt = build_robots_txt()
    return context
