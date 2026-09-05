/*
 * OSDuo Business Connect — Desk Branding JS
 *
 * Sets favicon and browser title dynamically.
 * Handles social link icon auto-population and URL hints.
 * Does NOT modify Frappe core files.
 */

(function () {
  "use strict";

  // ── Branding ──────────────────────────────────────────────

  // Set favicon
  var favicon = document.querySelector('link[rel="icon"]');
  if (favicon) {
    favicon.href = "/assets/osduo_business_connect/images/favicon.png";
    favicon.type = "image/png";
  } else {
    var link = document.createElement("link");
    link.rel = "icon";
    link.type = "image/png";
    link.href = "/assets/osduo_business_connect/images/favicon.png";
    document.head.appendChild(link);
  }

  // Set browser title
  if (document.title === "Frappe" || document.title === "") {
    document.title = "OSDuo Business Connect";
  }

  // ── Social Links ──────────────────────────────────────────

  var PLATFORM_CONFIG = {
    Facebook: { icon: "fa-brands fa-facebook", hint: "https://facebook.com/your-page" },
    Instagram: { icon: "fa-brands fa-instagram", hint: "https://instagram.com/your-handle" },
    LinkedIn: { icon: "fa-brands fa-linkedin", hint: "https://linkedin.com/in/your-profile" },
    X: { icon: "fa-brands fa-x-twitter", hint: "https://x.com/your-handle" },
    YouTube: { icon: "fa-brands fa-youtube", hint: "https://youtube.com/@your-channel" },
    Telegram: { icon: "fa-brands fa-telegram", hint: "https://t.me/your-handle" },
    Website: { icon: "fa-solid fa-globe", hint: "https://your-website.com" },
    Portfolio: { icon: "fa-brands fa-solid fa-briefcase", hint: "https://your-portfolio.com" },
    Other: { icon: "fa-solid fa-link", hint: "Enter the full URL" },
  };

  function apply_platform_config(parent_doc, child_doc, platform_field, url_field) {
    var platform = child_doc[platform_field];
    if (!platform) return;
    var config = PLATFORM_CONFIG[platform];
    if (!config) return;

    // Set icon_class on the child row
    frappe.model.set_value(child_doc.doctype, child_doc.name, "icon_class", config.icon);

    // Update URL field description with format hint
    var url_df = frappe.meta.get_docfield(child_doc.doctype, url_field, parent_doc.doctype);
    if (url_df) {
      url_df.description = "Example: " + config.hint;
    }
  }

  // ── Business Social Links ─────────────────────────────────
  // Child table: Business Social Link | parent field: social_links
  // Platform select field: platform | URL field: url

  frappe.ui.form.on("Business Social Link", {
    platform: function (frm, cdt, cdn) {
      var child = locals[cdt][cdn];
      apply_platform_config(frm.doc, child, "platform", "url");
      frm.refresh_field("social_links");
    },
  });

  // ── Digital Card Links ────────────────────────────────────
  // Child table: Digital Card Link | parent field: links
  // Link type select field: link_type | URL field: url

  frappe.ui.form.on("Digital Card Link", {
    link_type: function (frm, cdt, cdn) {
      var child = locals[cdt][cdn];
      apply_platform_config(frm.doc, child, "link_type", "url");
      frm.refresh_field("links");
    },
  });
})();
