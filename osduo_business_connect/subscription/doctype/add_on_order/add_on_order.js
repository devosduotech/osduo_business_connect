// Copyright (c) 2026, OSDuo and contributors
// For license information, please see license.txt

// Add-on Masters are Administrator-only. The custom query returns only the
// active add-ons allowed by this site's frozen plan, so the link field works
// without granting customer roles read access to the master list.
frappe.ui.form.on("Add-on Order", {
  setup(frm) {
    frm.set_query("add_on", () => ({
      query:
        "osduo_business_connect.subscription.doctype.add_on_master.add_on_master.get_orderable_addons",
    }));
  },
});
