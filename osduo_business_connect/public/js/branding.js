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

  var SOCIAL_PLATFORM_CONFIG = {
    Facebook: { icon: "fa-brands fa-facebook", url_hint: "https://facebook.com/your-page" },
    Instagram: { icon: "fa-brands fa-instagram", url_hint: "https://instagram.com/your-handle" },
    LinkedIn: { icon: "fa-brands fa-linkedin", url_hint: "https://linkedin.com/in/your-profile" },
    X: { icon: "fa-brands fa-x-twitter", url_hint: "https://x.com/your-handle" },
    YouTube: { icon: "fa-brands fa-youtube", url_hint: "https://youtube.com/@your-channel" },
    Telegram: { icon: "fa-brands fa-telegram", url_hint: "https://t.me/your-handle" },
    Website: { icon: "fa-solid fa-globe", url_hint: "https://your-website.com" },
    Portfolio: { icon: "fa-solid fa-briefcase", url_hint: "https://your-portfolio.com" },
    Other: { icon: "fa-solid fa-link", url_hint: "Enter the full URL" },
  };

  function set_icon_and_hint(row, platform_field) {
    var platform = row[platform_field];
    if (!platform) return;
    var config = SOCIAL_PLATFORM_CONFIG[platform];
    if (!config) return;

    frappe.model.set_value(row.doctype, row.name, "icon_class", config.icon);

    // Update URL field description with format hint
    var url_df = frappe.meta.get_docfield(row.doctype, "url", row.parenttype);
    if (url_df) {
      url_df.description = "Expected format: " + config.url_hint;
    }
  }

  // Attach to form refresh for Business and Digital Card
  $(document).on("form-refresh", function (e, frm) {
    var doctype = frm.doc.doctype || frm.doc.__doctype;

    if (doctype === "Business") {
      var grid = frm.fields_dict.social_links && frm.fields_dict.social_links.grid;
      if (grid && grid.wrapper) {
        grid.wrapper.off("change.social_links").on("change.social_links", "[data-fieldname='platform']", function () {
          var row = $(this).closest(".grid-row").data("doc");
          if (row) {
            set_icon_and_hint(row, "platform");
            frm.refresh_field("social_links");
          }
        });
      }
    }

    if (doctype === "Digital Card") {
      var grid = frm.fields_dict.links && frm.fields_dict.links.grid;
      if (grid && grid.wrapper) {
        grid.wrapper.off("change.card_links").on("change.card_links", "[data-fieldname='link_type']", function () {
          var row = $(this).closest(".grid-row").data("doc");
          if (row) {
            set_icon_and_hint(row, "link_type");
            frm.refresh_field("links");
          }
        });
      }
    }
  });
})();
