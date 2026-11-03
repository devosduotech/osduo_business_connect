// Copyright (c) 2026, OSDuo and contributors
// For license information, please see license.txt

frappe.ui.form.on("Showcase Service", {
    refresh(frm) {
        add_open_public_url_button(frm);
    },
});

function add_open_public_url_button(frm) {
    const url = frm.doc.public_url;
    const wrapper = frm.fields_dict.public_url && frm.fields_dict.public_url.$wrapper;
    if (!url || !wrapper) {
        return;
    }

    wrapper.find(".bc-open-public-url").remove();
    const btn = window.$('<a>', {
        class: "btn btn-sm btn-secondary bc-open-public-url",
        href: url,
        target: "_blank",
        rel: "noopener",
        title: url,
        text: __("Open"),
    });
    btn.css("margin-left", "8px");
    wrapper.append(btn);
}
