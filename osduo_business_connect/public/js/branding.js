/*
 * OSDuo Business Connect — Desk Branding JS
 *
 * Sets favicon and browser title dynamically.
 * Does NOT modify Frappe core files.
 */

(function () {
  "use strict";

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
})();
