import frappe


def patched_evaluate_dynamic_routes(rules, path):
    """Fixed version that doesn't double the leading slash."""
    from werkzeug.routing import Map

    route_map = Map(rules)
    endpoint = None

    if hasattr(frappe.local, "request") and frappe.local.request.environ:
        urls = route_map.bind_to_environ(frappe.local.request.environ)
        try:
            match_path = path if path.startswith("/") else "/" + path
            endpoint, args = urls.match(match_path)
            if args:
                frappe.local.no_cache = 1
                frappe.local.form_dict.update(args)
        except Exception:
            pass

    return endpoint


def apply_patch():
    """Apply the monkey-patch to frappe.website.path_resolver."""
    import frappe.website.path_resolver as pr
    pr.evaluate_dynamic_routes = patched_evaluate_dynamic_routes
