# PWA (Installable Mobile App) — OSDuo Business Connect

Every site on the bench (hosted subdomain like `karthic.connect.osduotech.com`
or a BYOD domain like `connect.ossolutions.in`) automatically becomes an
installable Progressive Web App. No per-customer build step, no app-store
release required; browsers treat each hostname as its own app (own icon,
cache, storage).

## What is included

| Piece | Served at | Source |
|---|---|---|
| Web app manifest (per-site name/icon/colors) | `/manifest.json` | `www/manifest.py` + `www/manifest.json` |
| Service worker (root scope) | `/sw.js` | `www/sw.py` + `www/sw.js` |
| Offline fallback page | `/offline` | `www/offline.py` + `www/offline.html` |
| App icons (192/512/maskable, PIL-generated) | `/api/method/osduo_business_connect.pwa.get_app_icon` | `pwa.py` |
| Install prompt + iOS guidance + SW registration | all website pages | `public/js/pwa.js` (via `web_include_js`) |

## Caching strategy (service worker)

- `/assets/**`, `/files/**` — cache-first (public images: logos, covers, QRs)
- `/login`, `/b/*`, `/c/*`, `/offline` — network-first, cached copy, then
  the offline page (public pages an NFC tap may need on flaky event Wi-Fi)
- `/api/**`, `/private/**`, `/app/**`, `/desk/**` — **never cached**
- Responses carrying `Set-Cookie` or opaque responses are never stored
- Cache names are stamped with the app `__version__`; the SW itself is
  served with `Cache-Control: no-cache`, so a version bump rolls every
  installed app forward on its next visit (skipWaiting + clients.claim).

## Canonical URLs (Phase 0 — matters for NFC!)

`public_url` on Business and Digital Card is derived from the **canonical**
site base (`utils/urls.py`) and auto-filled in the controllers — it is never
typed by hand and never derived from the request Host. `qr_service` encodes
that value into QR images (regenerated automatically on `on_update` when the
URL changes or QR was enabled).

Set the canonical origin per production site in `site_config.json`:

```json
{ "host_name": "https://karthic.connect.osduotech.com" }
```

The hosted subdomain is the permanent NFC/QR anchor even after a customer
attaches a custom (BYOD) domain — custom domains are additive; never
decommission the subdomain a card was printed with. `bench migrate`
re-syncs `public_url` across all records (see `install.backfill_public_urls`).

## Branding per customer

The manifest name/icon resolve in this order:

1. Website Settings → App Name / App Logo (set per site for white-label)
2. System Settings → App Name
3. `OSDUO_BRANDING` defaults in `hooks.py`

Theme/background colors come from `OSDUO_BRANDING`; adjust per-site by
editing those values in a fork or by extending `pwa.get_manifest_context`.

## Testing checklist

1. On the VM (no TLS): Chrome flag
   `chrome://flags/#unsafely-treat-insecure-origin-as-secure` → add
   `http://<vm-ip>:8000`, then open `/login` from a phone.
2. `curl -sI https://<site>/manifest.json` → 200 + `application/json`
3. `curl -sI https://<site>/sw.js` → 200 + `text/javascript`, `no-cache`
4. Android Chrome at `/login`: install chip appears → native install sheet
5. iOS Safari: chip shows "Share → Add to Home Screen" guidance
6. Airplane mode after one visit: open `/c/<slug>` → cached card page loads;
   unvisited page → `/offline` fallback
7. DevTools → Application → Manifest: no errors, icons 192/512/maskable green

## Per-customer domain provisioning

See **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** for the full SaaS runbook:
wildcard DNS/TLS for hosted subdomains (`customer.connect.yourdomain.com`) and the
Domain-doc + lets-encrypt flow for BYOD domains. Each customer = one bench site;
set its `host_name` **before** the first `bench migrate` so `public_url`/QR codes are
stamped with the right canonical origin from day one.

## Implementation gotchas (learned the hard way)

- `sw.js`/`manifest.json` are served via Frappe's raw-template mechanism
  (controller `.py` + extension template, like `website_script`/`sitemap`) —
  content type comes from the URL extension
- Binary API responses in Frappe v16 must set
  `frappe.local.response["type"] = "download"` (the `as_raw` handler); `"raw"` is not a
  registered key and returns HTTP 500
- A **custom Website Theme** replaces `website.bundle.css` site-wide — if a site uses
  one and it's stale after a Frappe upgrade, re-save the theme (migrate regenerates)
- PWA install requires **HTTPS**; localhost is exempt. On the HTTP test VM use Chrome's
  `unsafely-treat-insecure-origin-as-secure` flag

## Out of scope (roadmap)

- Full offline read/write in the desk (IndexedDB mirroring + sync)
- Web push (needs per-site Firebase VAPID config — Frappe supports it)
- Play Store listing via TWA (`/.well-known/assetlinks.json` served per site)
