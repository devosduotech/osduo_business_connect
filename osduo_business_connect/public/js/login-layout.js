
(() => {
    "use strict";

    const path = window.location.pathname.replace(/\/+$/, "");

/*    // Redirect the root URL to the branded login page.
    if (path === "") {
        window.location.replace("/login");
        return;
    } */

    if (window.location.pathname.replace(/\/+$/, "") !== "/login") {
       return;
    }

    // Apply the custom layout only to the login page.
    if (path !== "/login") {
        return;
    }

    function applyBusinessConnectLayout() {
        const section = document.querySelector("section.for-login");

        if (!section) {
            return;
        }

        const card = section.querySelector(".login-content.page-card");

        if (!card || section.querySelector(".bc-brand-panel")) {
            return;
        }

        const panel = document.createElement("div");
        panel.className = "bc-brand-panel";

        panel.innerHTML = `
            <div class="bc-brand-inner">
                <div class="bc-brand-heading">
                    <div class="bc-brand-identity">
                        <img
                            class="bc-brand-logo"
                            src="/files/logo_mark_512x512.png"
                            alt="OSDuo Business Connect logo"
                        >
                        <div>
                            <div class="bc-brand-name">OSDuo</div>
                            <div class="bc-brand-product">BUSINESS CONNECT</div>
                        </div>
                    </div>

                    <div class="bc-brand-accent" aria-hidden="true"></div>

                    <h1>
                        Your identity.<br>
                        One smart card.
                    </h1>

                    <p class="bc-brand-description">
                        Create, manage and share your professional identity
                        with a digital business card.
                    </p>
                </div>

                <div class="bc-brand-features">
                    <div class="bc-feature">
                        <div class="bc-feature-icon" aria-hidden="true">
                            <svg viewBox="0 0 24 24" fill="none" width="24" height="24">
                                <circle cx="12" cy="8" r="4"
                                    stroke="currentColor" stroke-width="1.8"/>
                                <path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"
                                    stroke="currentColor" stroke-width="1.8"
                                    stroke-linecap="round"/>
                            </svg>
                        </div>
                        <div>
                            <h3>For individuals</h3>
                            <p>Showcase your professional identity</p>
                        </div>
                    </div>

                    <div class="bc-feature">
                        <div class="bc-feature-icon" aria-hidden="true">
                            <svg viewBox="0 0 24 24" fill="none" width="24" height="24">
                                <rect x="3" y="7" width="18" height="14" rx="2"
                                    stroke="currentColor" stroke-width="1.8"/>
                                <path d="M8 7V4h8v3M3 12h18M10 12v2h4v-2"
                                    stroke="currentColor" stroke-width="1.8"
                                    stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </div>
                        <div>
                            <h3>For businesses</h3>
                            <p>Manage employee cards with consistent branding</p>
                        </div>
                    </div>

                    <div class="bc-feature">
                        <div class="bc-feature-icon" aria-hidden="true">
                            <svg viewBox="0 0 24 24" fill="none" width="24" height="24">
                                <circle cx="18" cy="5" r="3"
                                    stroke="currentColor" stroke-width="1.8"/>
                                <circle cx="6" cy="12" r="3"
                                    stroke="currentColor" stroke-width="1.8"/>
                                <circle cx="18" cy="19" r="3"
                                    stroke="currentColor" stroke-width="1.8"/>
                                <path d="m8.7 10.5 6.6-4M8.7 13.5l6.6 4"
                                    stroke="currentColor" stroke-width="1.8"
                                    stroke-linecap="round"/>
                            </svg>
                        </div>
                        <div>
                            <h3>Share anywhere</h3>
                            <p>Instantly via link or QR code</p>
                        </div>
                    </div>
                </div>

                <p class="bc-brand-footer">
                    Innovate. Integrate. Elevate.
                </p>
            </div>
        `;

        section.classList.add("bc-login-layout");
        section.insertBefore(panel, card);
    }

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            applyBusinessConnectLayout,
            { once: true }
        );
    } else {
        applyBusinessConnectLayout();
    }
})();
