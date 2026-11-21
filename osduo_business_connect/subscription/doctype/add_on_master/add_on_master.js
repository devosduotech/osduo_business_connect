// Copyright (c) 2026, OSDuo and contributors
// For license information, please see license.txt

// Keep the Applicable Plans table consistent with the applicability switch.
// The DocType also clears rows server-side; this only makes the form behave
// immediately for the Administrator editing the master.
frappe.ui.form.on("Add-on Master", {
  applies_to_all_plans(frm) {
    if (frm.doc.applies_to_all_plans) {
      frm.doc.applicable_plans = [];
      frm.refresh_field("applicable_plans");
    }
  },
  before_save(frm) {
    if (frm.doc.applies_to_all_plans && (frm.doc.applicable_plans || []).length) {
      frm.doc.applicable_plans = [];
      frm.refresh_field("applicable_plans");
    }
  },
});
