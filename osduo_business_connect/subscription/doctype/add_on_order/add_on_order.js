// Copyright (c) 2026, OSDuo and contributors
// For license information, please see license.txt

const BC_CUSTOM_DOMAIN_ADDON = "CUSTOM_DOMAIN_SERVICE";
const BC_DOMAIN_REGISTRATION_ADDON = "DOMAIN_REGISTRATION_RENEWAL";
const BC_ADMIN_USER = "Administrator";
const BC_ADDON_QUOTE_METHOD =
  "osduo_business_connect.subscription.doctype.add_on_order.add_on_order.get_addon_quote";

// Add-on Masters are Administrator-only. The custom query returns only the
// active add-ons allowed by this site's frozen plan, so the link field works
// without granting customer roles read access to the master list.

function bc_doc_info(frm) {
  const add_on = frm.doc.add_on;
  const is_domain_addon =
    add_on === BC_CUSTOM_DOMAIN_ADDON || add_on === BC_DOMAIN_REGISTRATION_ADDON;
  return {
    requires_hostname: is_domain_addon,
    requires_mapping_type: add_on === BC_CUSTOM_DOMAIN_ADDON,
    requires_registration_details: add_on === BC_DOMAIN_REGISTRATION_ADDON,
    requires_documents: add_on === BC_DOMAIN_REGISTRATION_ADDON,
    requires_attachment: frm.doc.billing_type === "Actual Cost",
    amount_label: "",
  };
}

function bc_apply_layout(frm, info) {
  frm.set_df_property("hostname", "hidden", info.requires_hostname ? 0 : 1);
  frm.set_df_property("hostname", "reqd", info.requires_hostname ? 1 : 0);

  frm.set_df_property("mapping_type", "hidden", info.requires_mapping_type ? 0 : 1);
  frm.set_df_property(
    "registration_details",
    "hidden",
    info.requires_registration_details ? 0 : 1,
  );

  const requires_documents =
    info.requires_documents || info.requires_registration_details;
  frm.set_df_property("documents", "hidden", requires_documents ? 0 : 1);
  frm.set_df_property("quote_attachment", "hidden", info.requires_attachment ? 0 : 1);
  frm.set_df_property("quote_attachment", "reqd", info.requires_attachment ? 1 : 0);

  const is_admin = frappe.session.user === BC_ADMIN_USER;
  // Invoice is a first-class, Administrator-only attachment on every order.
  frm.set_df_property("invoice", "hidden", is_admin ? 0 : 1);
  frm.set_df_property(
    "section_attachments",
    "hidden",
    requires_documents || info.requires_attachment || is_admin ? 0 : 1,
  );

  if (info.amount_label) {
    frm.set_df_property("amount", "description", info.amount_label);
  }
}

function bc_apply_status(frm) {
  if (frappe.session.user === BC_ADMIN_USER) return;
  frm.set_df_property("status", "read_only", 1);
  if (frm.is_new()) {
    frm.set_df_property("status", "options", "Requested");
    frm.set_value("status", "Requested");
  }
}

function bc_clear_irrelevant_values(frm, info) {
  if (!info.requires_hostname) frm.set_value("hostname", null);
  if (!info.requires_mapping_type) frm.set_value("mapping_type", null);
  if (!info.requires_registration_details) frm.set_value("registration_details", null);
  if (!info.requires_documents) frm.set_value("documents", null);
}

function bc_load_quote(frm) {
  frm.__bc_addon_quote = null;
  if (!frm.doc.add_on) {
    bc_apply_layout(frm, bc_doc_info(frm));
    return;
  }

  frappe.xcall(BC_ADDON_QUOTE_METHOD, { add_on: frm.doc.add_on }).then((quote) => {
    if (!quote || frm.doc.add_on !== quote.add_on) return;
    frm.__bc_addon_quote = quote;
    ["billing_type", "amount", "mapping_type", "expires_on"].forEach((field) => {
      frm.set_value(field, quote[field] || null);
    });
    bc_apply_layout(frm, quote);
  });
}

frappe.ui.form.on("Add-on Order", {
  setup(frm) {
    frm.set_query("add_on", () => ({
      query:
        "osduo_business_connect.subscription.doctype.add_on_master.add_on_master.get_orderable_addons",
    }));
  },

  onload_post_render(frm) {
    bc_apply_status(frm);
    bc_apply_layout(frm, frm.__bc_addon_quote || bc_doc_info(frm));
  },

  refresh(frm) {
    bc_apply_status(frm);
    bc_apply_layout(frm, frm.__bc_addon_quote || bc_doc_info(frm));
  },

  add_on(frm) {
    const info = bc_doc_info(frm);
    bc_clear_irrelevant_values(frm, info);
    bc_apply_layout(frm, info);
    bc_load_quote(frm);
  },
});
