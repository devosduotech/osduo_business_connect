/* OSDuo Business Connect — PWA bootstrap (runs on all website pages) */
(() => {
	"use strict";

	const SW_URL = "/sw.js";
	const MANIFEST_URL = "/manifest.json";

	function isSecureOrigin() {
		return (
			window.isSecureContext ||
			location.hostname === "localhost" ||
			location.hostname.endsWith(".localhost")
		);
	}

	function injectHeadTags() {
		if (!document.querySelector('link[rel="manifest"]')) {
			const link = document.createElement("link");
			link.rel = "manifest";
			link.href = MANIFEST_URL;
			document.head.appendChild(link);
		}

		// iOS reads apple-touch-icon (not the manifest) for the home-screen icon.
		if (!document.querySelector('link[rel="apple-touch-icon"]')) {
			const icon = document.createElement("link");
			icon.rel = "apple-touch-icon";
			icon.href =
				"/api/method/osduo_business_connect.pwa.get_app_icon?size=180";
			document.head.appendChild(icon);
		}
	}

	function registerServiceWorker() {
		if (!("serviceWorker" in navigator) || !isSecureOrigin()) return;
		window.addEventListener("load", () => {
			navigator.serviceWorker
				.register(SW_URL, { scope: "/" })
				.catch((err) => console.warn("BC SW registration failed:", err));
		});
	}

	function setupInstallPrompt() {
		let deferredPrompt = null;
		// The custom install UI only belongs on the login app entry point.
		// On public card/business pages we leave beforeinstallprompt alone so
		// Chrome shows its own mini-infobar and nothing covers the action bar.
		const showOwnUI = () => location.pathname.startsWith("/login");

		window.bcPwa = {
			canInstall: () => !!deferredPrompt,
			install: async () => {
				if (!deferredPrompt) return false;
				deferredPrompt.prompt();
				const { outcome } = await deferredPrompt.userChoice;
				if (outcome === "accepted") deferredPrompt = null;
				return outcome === "accepted";
			},
		};

		window.addEventListener("beforeinstallprompt", (event) => {
			if (!showOwnUI()) return; // allow default browser UI elsewhere
			event.preventDefault();
			deferredPrompt = event;
			window.dispatchEvent(new CustomEvent("bc-pwa-installable"));
			showInstallChip(event);
		});

		window.addEventListener("appinstalled", () => {
			deferredPrompt = null;
			hideInstallChip();
		});

		// iOS Safari never fires beforeinstallprompt — show guidance on login.
		if (showOwnUI() && isIOS()) {
			if (document.body) {
				showInstallChip(null);
			} else {
				document.addEventListener("DOMContentLoaded", () => showInstallChip(null), { once: true });
			}
		}
	}

	const DISMISS_KEY = "bc_pwa_install_dismissed";
	const isStandalone = () =>
		window.matchMedia("(display-mode: standalone)").matches ||
		window.navigator.standalone === true;
	const isIOS = () =>
		/iPhone|iPad|iPod/.test(navigator.userAgent) && !window.MSStream;

	function injectChipStyles() {
		if (document.getElementById("bc-pwa-chip-style")) return;
		const style = document.createElement("style");
		style.id = "bc-pwa-chip-style";
		style.textContent = `
			.bc-pwa-chip {
				position: fixed; left: 12px; bottom: 12px; z-index: 9999;
				display: flex; align-items: center; gap: 8px;
				background: #0f172a; color: #fff; border-radius: 10px;
				padding: 10px 12px; font-size: 13px; line-height: 1.4;
				box-shadow: 0 8px 28px rgba(15, 23, 42, 0.35);
				max-width: min(320px, calc(100vw - 24px));
				font-family: Inter, -apple-system, "Segoe UI", Roboto, sans-serif;
			}
			.bc-pwa-chip button {
				appearance: none; border: 0; cursor: pointer; border-radius: 6px;
				font-weight: 600; font-size: 13px; padding: 6px 10px;
			}
			.bc-pwa-chip .bc-pwa-install { background: #00C49A; color: #06281f; }
			.bc-pwa-chip .bc-pwa-close { background: transparent; color: #94a3b8; padding: 6px 4px; }
			.bc-pwa-hint { color: #cbd5e1; }
		`;
		document.head.appendChild(style);
	}

	function chipShell(onDismiss) {
		injectChipStyles();
		const chip = document.createElement("div");
		chip.className = "bc-pwa-chip";
		chip.setAttribute("role", "dialog");
		chip.setAttribute("aria-label", "Install app");

		const text = document.createElement("span");
		text.className = "bc-pwa-hint";
		chip.appendChild(text);

		return { chip, text };
	}

	function hideInstallChip() {
		const existing = document.querySelector(".bc-pwa-chip");
		if (existing) existing.remove();
	}

	function showInstallChip(deferredEvent) {
		if (isStandalone()) return;
		try {
			if (localStorage.getItem(DISMISS_KEY)) return;
		} catch (e) { /* private mode */ }
		hideInstallChip();

		const { chip, text } = chipShell();
		text.textContent = "Get the app for quick access";

		if (deferredEvent) {
			const installBtn = document.createElement("button");
			installBtn.className = "bc-pwa-install";
			installBtn.textContent = "Install";
			installBtn.addEventListener("click", async () => {
				const accepted = await window.bcPwa.install();
				if (accepted) hideInstallChip();
			});
			chip.appendChild(installBtn);
		} else if (isIOS()) {
			// iOS Safari has no prompt event — guide the user instead.
			text.textContent = "Install: tap Share, then “Add to Home Screen”.";
		} else {
			return; // desktop / unsupported: stay unobtrusive
		}

		const close = document.createElement("button");
		close.className = "bc-pwa-close";
		close.setAttribute("aria-label", "Dismiss");
		close.innerHTML = "&#10005;";
		close.addEventListener("click", () => {
			hideInstallChip();
			try {
				localStorage.setItem(DISMISS_KEY, String(Date.now()));
			} catch (e) { /* ignore */ }
		});
		chip.appendChild(close);
		document.body.appendChild(chip);
	}

	injectHeadTags();
	registerServiceWorker();
	setupInstallPrompt();
})();
