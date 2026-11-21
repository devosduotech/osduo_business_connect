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

  // ── Desk support menu (avatar) ────────────────────────────
  //
  // Frappe v16 builds the avatar "user menu" in JS
  // (frappe.ui.Sidebar.user_menu_options) and it carries no OSDuo links.
  // Append the support rows the server publishes as frappe.boot.osduo_support,
  // so both the sidebar avatar and the dock rail avatar get them. External rows
  // carry target="_blank"; Frappe's menu component then adds
  // rel="noopener noreferrer".

  function support_menu_rows() {
    var support = (frappe.boot && frappe.boot.osduo_support) || null;
    var items = (support && support.items) || [];
    var rows = [];
    for (var i = 0; i < items.length; i++) {
      var item = items[i];
      if (!item || !item.url) continue;
      var row = { label: item.label, icon: item.icon, href: item.url };
      if (item.target) row.target = item.target;
      rows.push(row);
    }
    return rows;
  }

  function patch_user_menu() {
    if (typeof frappe === "undefined" || !frappe.ui || !frappe.ui.Sidebar) return false;
    var proto = frappe.ui.Sidebar.prototype;
    if (proto.__osduoSupportPatched) return true;
    if (typeof proto.user_menu_options !== "function") return false;
    if (!support_menu_rows().length) return false;

    var original = proto.user_menu_options;
    proto.user_menu_options = function () {
      var groups = original.apply(this, arguments) || [];
      // Sit above the last group (Logout) when the menu has more than one.
      var at = groups.length > 1 ? groups.length - 1 : groups.length;
      groups.splice(at, 0, { group: "", options: support_menu_rows() });
      return groups;
    };
    proto.__osduoSupportPatched = true;
    return true;
  }

  // The Desktop/Workspace page has a second avatar menu built directly in
  // frappe/desk/page/desktop/desktop.js. Its About and Frappe Support rows are
  // hard-coded, so hiding the Navbar Settings help rows cannot remove them.
  // Patch only dropdowns triggered by .desktop-avatar; every other Frappe
  // dropdown must keep its original options.
  var DESKTOP_AVATAR_SELECTOR = ".desktop-avatar";
  var FRAPPE_DESKTOP_HELP_LABELS = ["About", "System Health", "Frappe Support"];

  function translated(label) {
    return typeof __ === "function" ? __(label) : label;
  }

  function is_desktop_avatar_dropdown(dropdown) {
    if (!dropdown) return false;
    var trigger = dropdown.opts && dropdown.opts.trigger;
    if (trigger && trigger.jquery && typeof trigger.is === "function") {
      if (trigger.is(DESKTOP_AVATAR_SELECTOR)) return true;
    }
    var element = dropdown.trigger_el || (trigger && trigger[0]) || trigger;
    return !!(element && typeof element.matches === "function" && element.matches(DESKTOP_AVATAR_SELECTOR));
  }

  function is_frappe_desktop_help_row(row) {
    if (!row || !row.label) return false;
    var label = String(row.label);
    for (var i = 0; i < FRAPPE_DESKTOP_HELP_LABELS.length; i++) {
      if (label === translated(FRAPPE_DESKTOP_HELP_LABELS[i])) return true;
    }
    return false;
  }

  function rewrite_desktop_avatar_options(dropdown) {
    var source = dropdown.opts && dropdown.opts.options;
    if (!Array.isArray(source)) return;

    // Rebuild from the original array on every open so the patch is
    // idempotent and never accumulates duplicate support rows.
    var rows = [];
    for (var i = 0; i < source.length; i++) {
      if (!is_frappe_desktop_help_row(source[i])) rows.push(source[i]);
    }

    var logout = translated("Logout");
    var at = rows.length;
    for (var j = 0; j < rows.length; j++) {
      if (rows[j] && String(rows[j].label) === logout) {
        at = j;
        break;
      }
    }

    var support = support_menu_rows();
    for (var k = 0; k < support.length; k++) {
      rows.splice(at + k, 0, support[k]);
    }
    dropdown.options = rows;
  }

  function patch_desktop_avatar_menu() {
    if (typeof frappe === "undefined" || !frappe.ui || !frappe.ui.Dropdown) return false;
    var proto = frappe.ui.Dropdown.prototype;
    if (proto.__osduoDesktopAvatarPatched) return true;
    if (typeof proto.open !== "function") return false;

    var original = proto.open;
    proto.open = function () {
      if (is_desktop_avatar_dropdown(this)) rewrite_desktop_avatar_options(this);
      return original.apply(this, arguments);
    };
    proto.__osduoDesktopAvatarPatched = true;
    return true;
  }

  function apply_patch_with_polling(patch) {
    // The sidebar computes its avatar options once, at construction time
    // (frappe.Application.startup -> make_sidebar -> create_user_menu), which
    // happens on DOMContentLoaded — after this script. app_include_js also
    // loads after Frappe's desk bundle, so the classes are normally already
    // defined; the poll is only a safety net for a different load order.
    if (patch()) return;
    var tries = 0;
    var timer = setInterval(function () {
      if (patch() || ++tries > 400) clearInterval(timer);
    }, 10);
  }

  // ── Business customer workspace theme ───────────────────
  // Business-plan customer roles may open only the BC workspace. Mirroring the
  // /portal/team palette here keeps that single Desk surface visually
  // consistent. The workspace's links and sidebar content are NOT touched.
  var BC_WORKSPACE_ROLES = [
    "BC Business Owner",
    "BC Business Manager",
    "BC Business Member",
    "BC CRM User",
    "BC Marketing Manager",
  ];
  var BC_PRIVILEGED_ROLES = [
    "Administrator",
    "System Manager",
    "BC System Manager",
    "BC Subscription Manager",
  ];

  function has_any_role(roles) {
    if (typeof frappe === "undefined" || !frappe.user || typeof frappe.user.has_role !== "function") {
      return false;
    }
    for (var i = 0; i < roles.length; i++) {
      if (frappe.user.has_role(roles[i])) return true;
    }
    return false;
  }

  function apply_bc_workspace_theme() {
    if (typeof document === "undefined" || !document.body) return false;
    if (has_any_role(BC_PRIVILEGED_ROLES) || !has_any_role(BC_WORKSPACE_ROLES)) {
      document.body.classList.remove("bc-customer-workspace");
      return true;
    }
    var path = (window.location.pathname || "").replace(/\/+$/, "");
    if (path === "/app/business-connect" || path === "/desk/business-connect") {
      document.body.classList.add("bc-customer-workspace");
    } else {
      document.body.classList.remove("bc-customer-workspace");
    }
    return true;
  }

  function install_support_patch() {
    apply_patch_with_polling(patch_user_menu);
    apply_patch_with_polling(patch_desktop_avatar_menu);
  }

  if (typeof frappe !== "undefined") {
    install_support_patch();
    apply_patch_with_polling(apply_bc_workspace_theme);
    if (window.jQuery) {
      $(document).on("page-change", function () {
        setTimeout(apply_bc_workspace_theme, 50);
      });
    }
  }
})();
