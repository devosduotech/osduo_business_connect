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
    favicon.href = "/assets/osduo_business_connect/images/favicon-256.png";
    favicon.type = "image/png";
  } else {
    var link = document.createElement("link");
    link.rel = "icon";
    link.type = "image/png";
    link.href = "/assets/osduo_business_connect/images/favicon-256.png";
    document.head.appendChild(link);
  }

  // Set browser title
  if (document.title === "Frappe" || document.title === "") {
    document.title = "OSDuo Business Connect";
  }

  // ── Social Links ──────────────────────────────────────────

  var PLATFORM_CONFIG = {
    Facebook: { icon: "fa-brands fa-facebook" },
    Instagram: { icon: "fa-brands fa-instagram" },
    LinkedIn: { icon: "fa-brands fa-linkedin" },
    X: { icon: "fa-brands fa-x-twitter" },
    YouTube: { icon: "fa-brands fa-youtube" },
    Telegram: { icon: "fa-brands fa-telegram" },
    Website: { icon: "fa-solid fa-globe" },
    Portfolio: { icon: "fa-solid fa-briefcase" },
    Other: { icon: "fa-solid fa-link" },
  };

  function set_icon(frm, cdt, cdn, platform_field) {
    // Use setTimeout to let Frappe sync the model first
    // Without this, locals[cdt][cdn] still has the OLD value
    setTimeout(function () {
      var child = locals[cdt][cdn];
      if (!child) return;
      var platform = child[platform_field];
      if (!platform) return;
      var config = PLATFORM_CONFIG[platform];
      if (!config) return;
      frappe.model.set_value(cdt, cdn, "icon_class", config.icon);
    }, 100);
  }

  // ── Business Social Links ─────────────────────────────────

  frappe.ui.form.on("Business Social Link", {
    platform: function (frm, cdt, cdn) {
      set_icon(frm, cdt, cdn, "platform");
    },
  });

  // ── Digital Card Links ────────────────────────────────────

  frappe.ui.form.on("Digital Card Link", {
    link_type: function (frm, cdt, cdn) {
      set_icon(frm, cdt, cdn, "link_type");
    },
  });

var BC_MY_CARD_SVG =
    '<svg class="bc-my-card-icon" viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="8" cy="11.5" r="2.2"/><path d="M13 10h5.5M13 13h4"/><path d="M5.4 16.5c.9-1.5 4.3-1.5 5.2 0"/></svg>';

// ── My Card navbar link ───────────────────────────────────

function add_my_card_link() {
    if (typeof frappe === "undefined" || !frappe.session) return;
    if (!frappe.session.user || frappe.session.user === "Guest") return;
    if (document.querySelector(".bc-my-card-nav")) return;

    // Desktop navbar first; second pass covers the collapsed mobile menu,
    // which usually keeps its own list after the breakpoint.
    var navbar =
      document.querySelector(".navbar .navbar-right") ||
      document.querySelector(".navbar .navbar-nav") ||
      document.querySelector(".navbar-nav") ||
      document.querySelector("nav .nav");
    if (!navbar) return;

    var link = document.createElement("a");
    link.href = "/my-card";
    link.className = "nav-link bc-my-card-nav";
    link.innerHTML = BC_MY_CARD_SVG + '<span>My Card</span>';
    link.style.cssText =
      "display:inline-flex;align-items:center;gap:6px;padding:6px 10px;font-size:13px;color:inherit;text-decoration:none;white-space:nowrap;";
    link.addEventListener("click", function (event) {
      event.preventDefault();
      window.location.href = "/my-card";
    });

    if (navbar.tagName === "UL") {
      var item = document.createElement("li");
      item.className = "nav-item bc-my-card-nav";
      item.appendChild(link);
      navbar.appendChild(item);
    } else {
      link.classList.add("bc-my-card-nav");
      navbar.appendChild(link);
    }
  }

  if (typeof frappe !== "undefined") {
    if (window.jQuery) {
      $(document).on("page-change", function () {
        setTimeout(add_my_card_link, 300);
      });
    }
    setTimeout(add_my_card_link, 1200);
    // Mobile site menus are often built asynchronously by the theme; retry
    // once more when no target has been reached yet.
    setTimeout(function () {
      if (frappe.session.user && frappe.session.user !== "Guest" && !document.querySelector(".bc-my-card-nav")) {
        add_my_card_link();
      }
    }, 3000);
  }
})();
